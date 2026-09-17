"""Human identity: authenticated principal shape and the identity port.

Source: 14_IMPLEMENTATION_SEQUENCE.md §32 (AUTHENTICATION AND SERVICE
IDENTITY) — the `AuthenticatedPrincipal` shape is taken verbatim from
there. 11_SECURITY_PRIVACY_OBSERVABILITY.md §5–§7 (Human Identity,
Authentication Session Contract, Identity to Workspace Resolution) and
06_BOUNDARY_ARCHITECTURE.md §7 (BND-001 IDENTITY BOUNDARY) ground the
non-collapse rule below.

PKG-01 SCOPE NOTE: this module defines the identity *port* only — the
shape authentication resolves to, and the Protocol a caller uses to
resolve it. It does not implement a production OIDC adapter.
`GAP-14-001` (Reference Authentication Provider Selection, 15 §0)
remains open; a concrete production adapter is future work, gated by
that gap being resolved. The deterministic test adapter lives in
`packages/test_support/identity.py` (14 §32: "Test adapter is
deterministic").

Non-collapse rule (11 §1 AC-11-001, 06 §7 BND-001): IDENTITY != AUTHORITY.
`AuthenticatedPrincipal` proves WHO IS CALLING only — it structurally
cannot carry a role, permission, or any other authority-shaped field.
A claims payload containing e.g. `role: "admin"` must have no effect on
and no representation in the resolved principal (11 §6 AC-11-002 item 7:
"session material is never accepted as a client-supplied
HumanAuthorityBinding").
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from semantic_types.ids import UserId


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Exactly the shape from 14 §32: `AuthenticatedPrincipal(UserId,
    authentication_session_ref, authentication_time, issuer_ref)`.

    No role, permission, or authority-shaped field exists here by
    construction — that is the non-collapse proof, not a runtime check.
    """

    user_id: UserId
    authentication_session_ref: str
    authentication_time: datetime
    issuer_ref: str

    def __post_init__(self) -> None:
        if not self.authentication_session_ref:
            raise ValueError(
                "AuthenticatedPrincipal requires a non-empty authentication_session_ref"
            )
        if self.authentication_time.tzinfo is None:
            raise ValueError("AuthenticatedPrincipal.authentication_time must be timezone-aware")
        if not self.issuer_ref:
            raise ValueError("AuthenticatedPrincipal requires a non-empty issuer_ref")


@dataclass(frozen=True, slots=True)
class ExternalCredential:
    """Already-verified external identity claims, presented to the
    identity port for mapping to a canonical `UserId`.

    Cryptographic verification of the underlying credential (signature,
    audience, expiry, revocation — 11 §6 AC-11-002 item 1: "credential
    verification occurs at an authenticated boundary") happens upstream
    of this port, in the concrete production adapter `GAP-14-001` will
    introduce. This type carries only what identity *resolution* needs
    once that verification has already occurred; it is not a JWT/OIDC
    token parser.

    `extra_claims` exists so a concrete adapter can pass through
    provider-specific claims for logging/observability, but
    `IdentityPort.resolve` must never read an authority-shaped key out
    of it (e.g. "role", "is_admin") — see the mandatory adversarial
    test in `tests/security/test_identity.py`.
    """

    subject: str
    issuer_ref: str
    session_ref: str
    authentication_time: datetime
    extra_claims: tuple[tuple[str, str], ...] = ()


@runtime_checkable
class IdentityPort(Protocol):
    """Port: map an already-authenticated external credential to a
    canonical `AuthenticatedPrincipal`.

    How a concrete adapter performs that mapping (a users-table lookup,
    just-in-time provisioning, ...) is an implementation detail of the
    adapter, not of this port.
    """

    def resolve(self, credential: ExternalCredential) -> AuthenticatedPrincipal: ...


__all__ = ["AuthenticatedPrincipal", "ExternalCredential", "IdentityPort"]
