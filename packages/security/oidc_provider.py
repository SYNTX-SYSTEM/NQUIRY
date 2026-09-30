"""The external provider port (24 §26.1; WU-AUTH-07).

A provider adapter owns protocol mechanics only (24 §12.3, §26.2): the
authorization URL, the token exchange with the original PKCE verifier, ID
Token validation and error normalization. It does not own the transaction,
the claim, the user-agent binding, the redirect target, canonical identity,
account creation, linking, membership, role or authority. Its one product is
a `VerifiedProviderCredential`: issuer and subject (the canonical external
key, 24 §11.13) plus email attributes, produced only after the ID Token has
passed signature, issuer, audience and expiry validation and the nonce claim
matched the transaction's expected nonce (24 §11.12).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from security.oidc_transaction import OidcFailureReason


class ProviderExchangeRejected(Exception):
    """The token endpoint answered and refused the exchange."""


class ProviderExchangeUncertain(Exception):
    """The exchange's outcome cannot be reconstructed (transport failure,
    timeout, malformed answer). 24 §11.9: never retried."""


class IdTokenInvalid(Exception):
    def __init__(self, reason: OidcFailureReason) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class VerifiedProviderCredential:
    """Trusted only because validation succeeded. Not an identity (24 §13.8):
    the identity resolver maps it to a `UserId` or refuses."""

    provider_id: str
    issuer: str
    subject: str
    email: str | None
    email_verified: bool
    display_name: str | None


class OidcProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    @property
    def label(self) -> str: ...

    @property
    def proof_class(self) -> str:
        """`PRODUCTION_PROVIDER` or `TEST_PROVIDER` (24 §27)."""
        ...

    @property
    def issuer(self) -> str: ...

    @property
    def client_id(self) -> str: ...

    @property
    def redirect_uri(self) -> str:
        """The registered provider redirect URI of the LOGIN callback. Never
        an application redirect target (24 §11.17)."""
        ...

    @property
    def link_redirect_uri(self) -> str:
        """The registered redirect URI of the ACCOUNT_LINK callback (24 §11.21:
        a separate contact, so a LOGIN transaction cannot be consumed by the
        link callback or the reverse)."""
        ...

    def authorization_url(
        self, *, state: str, nonce: str, code_challenge: str, redirect_uri: str
    ) -> str: ...

    def exchange_code(self, *, code: str, code_verifier: str, redirect_uri: str) -> str:
        """Returns the raw ID Token from the token response, or raises
        `ProviderExchangeRejected` / `ProviderExchangeUncertain`."""
        ...

    def validate_id_token(
        self, raw_id_token: str, *, expected_nonce_hash: str
    ) -> VerifiedProviderCredential: ...

    def normalize_error(self, error: str) -> OidcFailureReason: ...


__all__ = [
    "IdTokenInvalid",
    "OidcProvider",
    "ProviderExchangeRejected",
    "ProviderExchangeUncertain",
    "VerifiedProviderCredential",
]
