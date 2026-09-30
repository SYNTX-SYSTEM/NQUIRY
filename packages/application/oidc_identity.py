"""Provider credential → canonical identity (24 §11.14–11.15, §26.3; the local
effect gate of the OIDC callback; WU-AUTH-08, WU-AUTH-09).

VALID PROVIDER PROOF → LOOKUP provider_issuer + provider_subject
→ existing, unrevoked binding of an ACTIVE method → canonical `UserId`
→ (else) ACCOUNT CREATION POLICY:
   DENIED → fail closed (the default; 24 §36 #3–#5 undecided)
   SELF_REGISTRATION_ALLOWED → create identity + method + binding + audit as
   ONE local effect (24 §11.15), no Workspace authority (24 §20.3).

Creation preconditions under SELF_REGISTRATION_ALLOWED: the provider supplied
an email and marked it verified (a canonical `users.email` is a lookup key of
the local login; an unverified provider claim must not become one), and no
identity already carries that email (24 §14.5: same email is a collision
boundary, never a link). The new identity's canonical email is the provider
email, lower-cased; that is an attribute of the identity, not a `verified_emails`
relation (24 §36 #9 undecided).

Atomicity: everything runs in the caller's transaction (HD-6: no own commit
boundary); if any write fails, the caller rolls back and no partial identity
exists (24 §19.11). A concurrent first login of the same subject is decided by
the subject's uniqueness: the loser sees the winner's binding on retry.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.account_creation import AccountCreationPolicy
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import LocalSessionRepository
from security.oidc_provider import VerifiedProviderCredential
from security.oidc_transaction import OidcFailureReason
from security.provider_identity import ProviderIdentityConflict
from semantic_types.ids import AuthenticationMethodId, CorrelationId, SecurityEventId, UserId

from application.auth_handler import SessionRequired, resolve_session

_METHOD_TYPES = {
    "google": AuthenticationMethodType.GOOGLE_OIDC,
    "test": AuthenticationMethodType.TEST_PROVIDER,
}
_EVENT_TYPE = "IDENTITY_CREATED"
_ACTOR_TYPE = "ACCOUNT_CREATION_POLICY"


class ProviderIdentityUnresolved(Exception):
    def __init__(self, reason: OidcFailureReason) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class ResolvedProviderIdentity:
    user_id: UserId
    method_id: AuthenticationMethodId
    created: bool = False


def resolve_provider_identity(
    connection: Any,
    credential: VerifiedProviderCredential,
    *,
    now: datetime,
    policy: AccountCreationPolicy = AccountCreationPolicy.DENIED,
    environment: Environment | None = None,
) -> ResolvedProviderIdentity:
    """Maps a verified provider credential to a canonical `UserId` through an
    existing binding, or through the account creation policy, or refuses.
    Never by email."""
    repository = SqlAlchemyProviderIdentityRepository(connection)
    binding = repository.find(credential.issuer, credential.subject)
    if binding is None:
        if policy is not AccountCreationPolicy.SELF_REGISTRATION_ALLOWED:
            raise ProviderIdentityUnresolved(OidcFailureReason.ACCOUNT_CREATION_POLICY_UNRESOLVED)
        return _create_identity(connection, credential, now=now, environment=environment)
    authenticated = repository.authenticate(
        credential.issuer,
        credential.subject,
        provider_email=credential.email,
        provider_email_verified=credential.email_verified,
        provider_display_name=credential.display_name,
        now=now,
    )
    if authenticated is None:
        raise ProviderIdentityUnresolved(OidcFailureReason.AUTHENTICATION_METHOD_REVOKED)
    return ResolvedProviderIdentity(
        user_id=authenticated.user_id, method_id=authenticated.method_id
    )


def _create_identity(
    connection: Any,
    credential: VerifiedProviderCredential,
    *,
    now: datetime,
    environment: Environment | None,
) -> ResolvedProviderIdentity:
    if environment is None:
        # AC-11-017: the audit record declares its environment; none declared,
        # no creation (the runtime only admits this policy in DEVELOPMENT / TEST).
        raise ProviderIdentityUnresolved(OidcFailureReason.LOCAL_EFFECT_FAILURE)
    method_type = _METHOD_TYPES.get(credential.provider_id)
    if method_type is None:
        raise ProviderIdentityUnresolved(OidcFailureReason.LOCAL_EFFECT_FAILURE)
    if not credential.email:
        raise ProviderIdentityUnresolved(OidcFailureReason.PROVIDER_EMAIL_MISSING)
    if not credential.email_verified:
        raise ProviderIdentityUnresolved(OidcFailureReason.PROVIDER_EMAIL_UNVERIFIED)
    email = credential.email.strip().lower()
    identities = SqlAlchemyIdentityRepository(connection)
    if identities.email_exists(email):
        raise ProviderIdentityUnresolved(OidcFailureReason.EMAIL_COLLISION)

    user_id = UserId(uuid.uuid4())
    name = credential.display_name or email.split("@", 1)[0]
    try:
        identities.create(user_id=user_id, email=email, name=name, now=now)
        method = SqlAlchemyAuthenticationMethodRepository(connection).create(
            user_id=user_id,
            method_type=method_type,
            provenance_ref=f"account-creation:{AccountCreationPolicy.SELF_REGISTRATION_ALLOWED.value}",
            now=now,
        )
        SqlAlchemyProviderIdentityRepository(connection).create(
            method_id=method.method_id,
            user_id=user_id,
            provider_issuer=credential.issuer,
            provider_subject=credential.subject,
            provider_email=credential.email,
            provider_email_verified=True,
            provider_display_name=credential.display_name,
            now=now,
            provenance_ref=f"account-creation:{AccountCreationPolicy.SELF_REGISTRATION_ALLOWED.value}",
        )
        SqlAlchemySecurityEventRepository(connection).record(
            SecurityEvent(
                security_event_id=SecurityEventId(uuid.uuid4()),
                occurred_at=now,
                environment=environment,
                actor_type=_ACTOR_TYPE,
                actor_id=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED.value,
                trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
                event_type=_EVENT_TYPE,
                correlation_id=CorrelationId(uuid.uuid4()),
                target_ref=f"user:{user_id.value}",
                observed_facts=json.dumps(
                    {
                        "authority": "24 section 11.14 SELF_REGISTRATION_ALLOWED",
                        "identityClass": "PROVIDER_IDENTITY",
                        "providerIssuer": credential.issuer,
                        "providerSubjectHash": hashlib.sha256(
                            credential.subject.encode("utf-8")
                        ).hexdigest()[:16],
                        "method": method_type.value,
                        "workspaceAuthority": "NONE",
                    },
                    sort_keys=True,
                ),
                audit_linkage=f"user:{user_id.value}",
            )
        )
    except ProviderIdentityConflict as exc:
        # A concurrent first login won the subject first.
        raise ProviderIdentityUnresolved(OidcFailureReason.LOCAL_EFFECT_FAILURE) from exc
    return ResolvedProviderIdentity(user_id=user_id, method_id=method.method_id, created=True)


@dataclass(frozen=True, slots=True)
class LinkOutcome:
    method_id: AuthenticationMethodId
    already_linked: bool


def link_provider_identity(
    connection: Any,
    credential: VerifiedProviderCredential,
    *,
    user_id: UserId,
    now: datetime,
    environment: Environment | None,
) -> LinkOutcome:
    """24 §14.2 / §19.5 link effect for the AUTHENTICATED identity `user_id`:
    a verified provider credential becomes a provider method + binding of that
    identity, audited, in the caller's transaction. A subject already bound to
    another identity is a collision (24 §14.4): nothing moves. A subject
    already bound to this identity is not a second method."""
    method_type = _METHOD_TYPES.get(credential.provider_id)
    if method_type is None or environment is None:
        raise ProviderIdentityUnresolved(OidcFailureReason.LOCAL_EFFECT_FAILURE)
    repository = SqlAlchemyProviderIdentityRepository(connection)
    existing = repository.find(credential.issuer, credential.subject)
    if existing is not None:
        if existing.user_id != user_id or existing.revoked_at is not None:
            raise ProviderIdentityUnresolved(OidcFailureReason.PROVIDER_SUBJECT_COLLISION)
        return LinkOutcome(method_id=existing.method_id, already_linked=True)
    provenance = f"account-link:user:{user_id.value}"
    try:
        method = SqlAlchemyAuthenticationMethodRepository(connection).create(
            user_id=user_id, method_type=method_type, provenance_ref=provenance, now=now
        )
        repository.create(
            method_id=method.method_id,
            user_id=user_id,
            provider_issuer=credential.issuer,
            provider_subject=credential.subject,
            provider_email=credential.email,
            provider_email_verified=credential.email_verified,
            provider_display_name=credential.display_name,
            now=now,
            provenance_ref=provenance,
        )
        SqlAlchemySecurityEventRepository(connection).record(
            SecurityEvent(
                security_event_id=SecurityEventId(uuid.uuid4()),
                occurred_at=now,
                environment=environment,
                actor_type="HUMAN_USER",
                actor_id=str(user_id.value),
                trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
                event_type="AUTH_METHOD_LINKED",
                correlation_id=CorrelationId(uuid.uuid4()),
                target_ref=f"user:{user_id.value}",
                observed_facts=json.dumps(
                    {
                        "authority": "24 section 14.2 authenticated identity links own method",
                        "method": method_type.value,
                        "methodId": str(method.method_id.value),
                        "providerIssuer": credential.issuer,
                        "providerSubjectHash": hashlib.sha256(
                            credential.subject.encode("utf-8")
                        ).hexdigest()[:16],
                        "workspaceAuthority": "NONE",
                    },
                    sort_keys=True,
                ),
                audit_linkage=f"user:{user_id.value}",
            )
        )
    except ProviderIdentityConflict as exc:
        # A concurrent link of the same subject won.
        raise ProviderIdentityUnresolved(OidcFailureReason.PROVIDER_SUBJECT_COLLISION) from exc
    return LinkOutcome(method_id=method.method_id, already_linked=False)


@dataclass(frozen=True, slots=True)
class MethodListing:
    method_id: AuthenticationMethodId
    method_type: AuthenticationMethodType
    status: AuthenticationMethodStatus
    created_at: datetime
    last_authenticated_at: datetime | None
    provider_issuer: str | None
    provider_email: str | None


def list_methods(
    connection: Any,
    session_token: str | None,
    *,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> tuple[MethodListing, ...]:
    """24 §23.2 "list authentication methods": the caller's own, with the
    provider attribute of a provider method. No secret, no subject."""
    principal = resolve_session(session_token, session_repository=session_repository, now=now)
    if principal is None:
        raise SessionRequired("no valid session")
    bindings = {
        binding.method_id: binding
        for binding in SqlAlchemyProviderIdentityRepository(connection).list_for_user(
            principal.user_id
        )
    }
    return tuple(
        MethodListing(
            method_id=method.method_id,
            method_type=method.method_type,
            status=method.status,
            created_at=method.created_at,
            last_authenticated_at=method.last_authenticated_at,
            provider_issuer=(
                None
                if method.method_id not in bindings
                else bindings[method.method_id].provider_issuer
            ),
            provider_email=(
                None
                if method.method_id not in bindings
                else bindings[method.method_id].provider_email
            ),
        )
        for method in SqlAlchemyAuthenticationMethodRepository(connection).list_for_user(
            principal.user_id
        )
    )


__all__ = [
    "LinkOutcome",
    "MethodListing",
    "ProviderIdentityUnresolved",
    "ResolvedProviderIdentity",
    "link_provider_identity",
    "list_methods",
    "resolve_provider_identity",
]
