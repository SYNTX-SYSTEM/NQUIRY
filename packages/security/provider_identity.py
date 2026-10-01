"""External provider identity: the binding of `provider_issuer +
provider_subject` to a canonical `UserId` through an authentication method
(24 §11.13, §13.3, §14.7; WU-AUTH-08).

The canonical external key is issuer + subject, never email (24 §11.13).
A binding belongs to exactly one provider-type authentication method of the
same user; the method's status is what controls login (24 §13.2). Provider
email and display name are attributes recorded "at last authentication" and
updated after each provider proof; they never change the link (24 §14.7) and
they are never a lookup key (24 §10.4).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from semantic_types.ids import AuthenticationMethodId, UserId


class ProviderIdentityConflict(Exception):
    """The binding could not be created because the issuer + subject (or the
    method) is already bound: a concurrent first login or link won."""


@dataclass(frozen=True, slots=True)
class ProviderIdentityBinding:
    binding_id: uuid.UUID
    method_id: AuthenticationMethodId
    user_id: UserId
    provider_issuer: str
    provider_subject: str
    provider_email: str | None
    provider_email_verified: bool
    provider_display_name: str | None
    linked_at: datetime
    revoked_at: datetime | None
    provenance_ref: str


@dataclass(frozen=True, slots=True)
class ProviderAuthentication:
    """The result of one successful provider login through an existing,
    active binding: the canonical identity and the method that produced it."""

    user_id: UserId
    method_id: AuthenticationMethodId


class ProviderIdentityRepository(Protocol):
    """Port. Adapter:
    `persistence.provider_identity_repository.SqlAlchemyProviderIdentityRepository`.
    Lookups are by issuer + subject only."""

    def create(
        self,
        *,
        method_id: AuthenticationMethodId,
        user_id: UserId,
        provider_issuer: str,
        provider_subject: str,
        provider_email: str | None,
        provider_email_verified: bool,
        provider_display_name: str | None,
        now: datetime,
        provenance_ref: str,
    ) -> ProviderIdentityBinding: ...

    def find(
        self, provider_issuer: str, provider_subject: str
    ) -> ProviderIdentityBinding | None: ...

    def list_for_user(self, user_id: UserId) -> tuple[ProviderIdentityBinding, ...]: ...

    def was_bound(self, provider_issuer: str, provider_subject: str) -> bool:
        """WU-AUTH-13: whether this subject was ever bound (an unlinked
        subject's login is denied, never re-created; 24 §18.2)."""
        ...

    def find_by_method(
        self, method_id: AuthenticationMethodId
    ) -> ProviderIdentityBinding | None: ...

    def revoke_for_method(self, method_id: AuthenticationMethodId, *, revoked_at: datetime) -> bool:
        """WU-AUTH-13 unlink: the binding becomes revoked evidence (24 §18.3)."""
        ...

    def authenticate(
        self,
        provider_issuer: str,
        provider_subject: str,
        *,
        provider_email: str | None,
        provider_email_verified: bool,
        provider_display_name: str | None,
        now: datetime,
    ) -> ProviderAuthentication | None:
        """One conditional write: records the authentication on the binding's
        method only while the binding is unrevoked, the method ACTIVE and the
        identity not disabled, and refreshes the provider attributes. None when
        no such active binding exists (unknown, revoked, method inactive or
        identity disabled)."""
        ...


__all__ = [
    "ProviderAuthentication",
    "ProviderIdentityBinding",
    "ProviderIdentityConflict",
    "ProviderIdentityRepository",
]
