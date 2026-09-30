"""Provider credential → canonical identity (24 §11.14, §26.3; the local
effect gate of the OIDC callback).

WU-AUTH-07 state: NO provider identity relation exists yet (WU-AUTH-08) and
NO account creation policy is established (24 §36 #3–#5; WU-AUTH-09). By
24 §11.14 the boundary therefore fails closed for every verified credential:
no user is created, no user is looked up, no session is created. WU-AUTH-08
gives this function its lookup; WU-AUTH-09 its policy branch.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
    del connection, credential, now
    raise ProviderIdentityUnresolved(OidcFailureReason.ACCOUNT_CREATION_POLICY_UNRESOLVED)


__all__ = ["ProviderIdentityUnresolved", "ResolvedProviderIdentity", "resolve_provider_identity"]
