"""Concrete `security.provider_identity.ProviderIdentityRepository`, backed by
`external_provider_identities` (migration `d5f7b9c1e3a7`; WU-AUTH-08).

`authenticate` is the provider counterpart of the local credential's
`mark_authenticated`: one UPDATE on `authentication_methods`, joined through
the binding, conditional on the binding being unrevoked and the method
ACTIVE. The row it changes is the method row (last authentication); the
binding's provider attributes are refreshed in a second statement only after
that first one changed a row. Nothing here reads or writes by email.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from security.auth_methods import AuthenticationMethodStatus
from security.provider_identity import (
    ProviderAuthentication,
    ProviderIdentityBinding,
    ProviderIdentityConflict,
)
from semantic_types.ids import AuthenticationMethodId, UserId

from persistence.tables import external_provider_identities_table


def _to_binding(row: Any) -> ProviderIdentityBinding:
    return ProviderIdentityBinding(
        binding_id=row["id"],
        method_id=AuthenticationMethodId(row["authentication_method_id"]),
        user_id=UserId(row["user_id"]),
        provider_issuer=row["provider_issuer"],
        provider_subject=row["provider_subject"],
        provider_email=row["provider_email"],
        provider_email_verified=bool(row["provider_email_verified"]),
        provider_display_name=row["provider_display_name"],
        linked_at=row["linked_at"],
        revoked_at=row["revoked_at"],
        provenance_ref=row["provenance_ref"],
    )


class SqlAlchemyProviderIdentityRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

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
    ) -> ProviderIdentityBinding:
        binding_id = uuid.uuid4()
        try:
            self._insert(
                binding_id=binding_id,
                method_id=method_id,
                user_id=user_id,
                provider_issuer=provider_issuer,
                provider_subject=provider_subject,
                provider_email=provider_email,
                provider_email_verified=provider_email_verified,
                provider_display_name=provider_display_name,
                now=now,
                provenance_ref=provenance_ref,
            )
        except sa.exc.IntegrityError as exc:
            if "uq_external_provider_identities" in str(exc.orig):
                raise ProviderIdentityConflict(str(exc.orig).splitlines()[0]) from exc
            raise
        return ProviderIdentityBinding(
            binding_id=binding_id,
            method_id=method_id,
            user_id=user_id,
            provider_issuer=provider_issuer,
            provider_subject=provider_subject,
            provider_email=provider_email,
            provider_email_verified=provider_email_verified,
            provider_display_name=provider_display_name,
            linked_at=now,
            revoked_at=None,
            provenance_ref=provenance_ref,
        )

    def _insert(
        self,
        *,
        binding_id: uuid.UUID,
        method_id: AuthenticationMethodId,
        user_id: UserId,
        provider_issuer: str,
        provider_subject: str,
        provider_email: str | None,
        provider_email_verified: bool,
        provider_display_name: str | None,
        now: datetime,
        provenance_ref: str,
    ) -> None:
        self._connection.execute(
            sa.insert(external_provider_identities_table).values(
                id=binding_id,
                authentication_method_id=method_id.value,
                user_id=user_id.value,
                provider_issuer=provider_issuer,
                provider_subject=provider_subject,
                provider_email=provider_email,
                provider_email_verified=provider_email_verified,
                provider_display_name=provider_display_name,
                linked_at=now,
                revoked_at=None,
                provenance_ref=provenance_ref,
            )
        )

    def find(self, provider_issuer: str, provider_subject: str) -> ProviderIdentityBinding | None:
        row = (
            self._connection.execute(
                sa.select(external_provider_identities_table).where(
                    external_provider_identities_table.c.provider_issuer == provider_issuer,
                    external_provider_identities_table.c.provider_subject == provider_subject,
                    external_provider_identities_table.c.revoked_at.is_(None),
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_binding(row)

    def was_bound(self, provider_issuer: str, provider_subject: str) -> bool:
        return (
            self._connection.execute(
                sa.select(external_provider_identities_table.c.id).where(
                    external_provider_identities_table.c.provider_issuer == provider_issuer,
                    external_provider_identities_table.c.provider_subject == provider_subject,
                )
            ).first()
            is not None
        )

    def find_by_method(self, method_id: AuthenticationMethodId) -> ProviderIdentityBinding | None:
        row = (
            self._connection.execute(
                sa.select(external_provider_identities_table).where(
                    external_provider_identities_table.c.authentication_method_id == method_id.value
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_binding(row)

    def revoke_for_method(self, method_id: AuthenticationMethodId, *, revoked_at: datetime) -> bool:
        result = self._connection.execute(
            sa.update(external_provider_identities_table)
            .where(
                external_provider_identities_table.c.authentication_method_id == method_id.value,
                external_provider_identities_table.c.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        return result.rowcount == 1

    def list_for_user(self, user_id: UserId) -> tuple[ProviderIdentityBinding, ...]:
        rows = (
            self._connection.execute(
                sa.select(external_provider_identities_table)
                .where(external_provider_identities_table.c.user_id == user_id.value)
                .order_by(external_provider_identities_table.c.linked_at)
            )
            .mappings()
            .all()
        )
        return tuple(_to_binding(row) for row in rows)

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
        row = self._connection.execute(
            sa.text(
                "UPDATE authentication_methods AS m SET last_authenticated_at = :now "
                "FROM external_provider_identities AS e "
                "WHERE e.authentication_method_id = m.id "
                "  AND e.provider_issuer = :issuer AND e.provider_subject = :subject "
                "  AND e.revoked_at IS NULL AND m.status = :active "
                "  AND EXISTS (SELECT 1 FROM users u WHERE u.id = m.user_id "
                "              AND u.disabled_at IS NULL) "
                "RETURNING m.id, m.user_id, e.id AS binding_id"
            ),
            {
                "now": now,
                "issuer": provider_issuer,
                "subject": provider_subject,
                "active": AuthenticationMethodStatus.ACTIVE.value,
            },
        ).first()
        if row is None:
            return None
        self._connection.execute(
            sa.update(external_provider_identities_table)
            .where(external_provider_identities_table.c.id == row.binding_id)
            .values(
                provider_email=provider_email,
                provider_email_verified=provider_email_verified,
                provider_display_name=provider_display_name,
            )
        )
        return ProviderAuthentication(
            user_id=UserId(row.user_id), method_id=AuthenticationMethodId(row.id)
        )


__all__ = ["SqlAlchemyProviderIdentityRepository"]
