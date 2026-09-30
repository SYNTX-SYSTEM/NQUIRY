"""Provider credential → canonical identity (24 §11.14, §26.3; the local
effect gate of the OIDC callback; WU-AUTH-08).

VALID PROVIDER PROOF → LOOKUP provider_issuer + provider_subject
→ existing, unrevoked binding of an ACTIVE method → canonical `UserId`
→ (else) ACCOUNT CREATION POLICY.

WU-AUTH-08 state: the lookup and the active-method check exist and are one
conditional write. No account creation policy is established (24 §36 #3–#5;
WU-AUTH-09), so an unknown subject fails closed: no user is created, nothing
is matched by email. A known subject whose method is revoked is refused with
its own class.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from security.oidc_provider import VerifiedProviderCredential
from security.oidc_transaction import OidcFailureReason
from semantic_types.ids import AuthenticationMethodId, UserId


class ProviderIdentityUnresolved(Exception):
    def __init__(self, reason: OidcFailureReason) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class ResolvedProviderIdentity:
    user_id: UserId
    method_id: AuthenticationMethodId


def resolve_provider_identity(
    connection: Any, credential: VerifiedProviderCredential, *, now: datetime
) -> ResolvedProviderIdentity:
    """Maps a verified provider credential to a canonical `UserId` through
    an existing provider identity binding, or refuses. Never by email."""
    repository = SqlAlchemyProviderIdentityRepository(connection)
    binding = repository.find(credential.issuer, credential.subject)
    if binding is None:
        # 24 §11.14 "IF NO EXISTING BINDING: evaluate ACCOUNT CREATION POLICY";
        # no policy is established: DENIED / UNAVAILABLE (WU-AUTH-09).
        raise ProviderIdentityUnresolved(OidcFailureReason.ACCOUNT_CREATION_POLICY_UNRESOLVED)
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


__all__ = ["ProviderIdentityUnresolved", "ResolvedProviderIdentity", "resolve_provider_identity"]
