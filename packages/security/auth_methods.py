"""Authentication methods: the typed relation between a canonical `UserId`
and a persistent way it authenticates (24 §9.1, §13.2; WU-AUTH-02, FBR-AUTH-002).

A method says WHICH persistent mechanism a canonical identity may authenticate
through and whether that mechanism is currently usable. It is not the
credential (the password hash stays in `local_auth_credentials`; a provider
subject will live in its own relation), not the identity (`users`), and not
authority: it has no role, membership, Workspace or capability field, by
construction.

THE VOCABULARY IS CLOSED (24 §9.1). `FUTURE_OIDC_PROVIDER` there is a class of
later, human-approved providers, not a value: a new provider extends this enum
and the database CHECK in its own Work Unit. Proof and protocol relations are
never methods (24 §9.1, §13.2 "Excluded"): a recovery challenge, an OIDC
transaction, an initiating user-agent binding, a PKCE verifier, a CSRF or
login-CSRF proof. They have no member here, so they cannot be represented.

STATUS (24 §13.2): ACTIVE or REVOKED. REVOKED is terminal and keeps the row
(24 §18.3: "Revocation preserves evidence"). A replacement is a new method.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from semantic_types.ids import AuthenticationMethodId, UserId


class AuthenticationMethodType(Enum):
    LOCAL_PASSWORD = "LOCAL_PASSWORD"
    GOOGLE_OIDC = "GOOGLE_OIDC"
    TEST_PROVIDER = "TEST_PROVIDER"


class AuthenticationMethodStatus(Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _require_aware(name: str, value: datetime | None) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"AuthenticationMethod.{name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class AuthenticationMethod:
    method_id: AuthenticationMethodId
    user_id: UserId
    method_type: AuthenticationMethodType
    status: AuthenticationMethodStatus
    created_at: datetime
    revoked_at: datetime | None
    last_authenticated_at: datetime | None
    provenance_ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.method_type, AuthenticationMethodType):
            raise TypeError("method_type must be an AuthenticationMethodType")
        if not isinstance(self.status, AuthenticationMethodStatus):
            raise TypeError("status must be an AuthenticationMethodStatus")
        if not self.provenance_ref:
            raise ValueError("AuthenticationMethod requires a non-empty provenance_ref")
        _require_aware("created_at", self.created_at)
        _require_aware("revoked_at", self.revoked_at)
        _require_aware("last_authenticated_at", self.last_authenticated_at)
        revoked = self.status is AuthenticationMethodStatus.REVOKED
        if revoked != (self.revoked_at is not None):
            raise ValueError("a method is REVOKED exactly when it carries revoked_at")


class AuthenticationMethodRepository(Protocol):
    """Port. Concrete adapter:
    `persistence.authentication_method_repository.SqlAlchemyAuthenticationMethodRepository`.
    Lookups are by method or by user, never by email."""

    def create(
        self,
        *,
        user_id: UserId,
        method_type: AuthenticationMethodType,
        provenance_ref: str,
        now: datetime,
    ) -> AuthenticationMethod: ...

    def get(self, method_id: AuthenticationMethodId) -> AuthenticationMethod | None: ...

    def list_for_user(self, user_id: UserId) -> tuple[AuthenticationMethod, ...]: ...

    def revoke(self, method_id: AuthenticationMethodId, *, revoked_at: datetime) -> bool: ...


__all__ = [
    "AuthenticationMethod",
    "AuthenticationMethodRepository",
    "AuthenticationMethodStatus",
    "AuthenticationMethodType",
]
