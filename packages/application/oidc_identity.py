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
from security.auth_methods import AuthenticationMethodType
from security.events import Environment, SecurityEvent, TrustBoundary
from security.oidc_provider import VerifiedProviderCredential
from security.oidc_transaction import OidcFailureReason
from security.provider_identity import ProviderIdentityConflict
from semantic_types.ids import AuthenticationMethodId, CorrelationId, SecurityEventId, UserId

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


__all__ = ["ProviderIdentityUnresolved", "ResolvedProviderIdentity", "resolve_provider_identity"]
