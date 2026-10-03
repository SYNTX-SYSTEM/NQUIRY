"""Canonical human identity rows (`users`) for the host-operator account
creation path (WU-PFC-AC1, HD-28).

Two operations only: an existence check by normalized email and the insert of
one `users` row. The credential lives in `local_auth_credentials`
(`persistence.local_auth_repository`); identity and credential stay separate
(18; 24 §4.2). Nothing here touches memberships, roles, bindings or
participations.
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from semantic_types.ids import UserId

from persistence.tables import users_table


class SqlAlchemyIdentityRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def email_exists(self, normalized_email: str) -> bool:
        return (
            self._connection.execute(
                sa.select(users_table.c.id).where(
                    sa.func.lower(users_table.c.email) == normalized_email
                )
            ).first()
            is not None
        )

    def create(self, *, user_id: UserId, email: str, name: str, now: datetime) -> None:
        self._connection.execute(
            sa.insert(users_table).values(
                id=user_id.value,
                email=email,
                name=name,
                record_version=1,
                created_at=now,
                updated_at=now,
            )
        )

    # --- PURPLE_IDENTITY_PRESENTATION_01 ------------------------------------

    def presentation(self, user_id: UserId) -> tuple[str, str] | None:
        """(name, email) of the canonical identity row — the two human-facing
        attributes the identity creation authority wrote (HD-28). None when no
        such identity exists. Reads nothing of any authentication relation."""
        row = self._connection.execute(
            sa.select(users_table.c.name, users_table.c.email).where(
                users_table.c.id == user_id.value
            )
        ).first()
        return None if row is None else (row.name, row.email)

    # --- WU-AUTH-13 (24 §18.2 account disable) ------------------------------

    def find_by_email(self, normalized_email: str) -> tuple[UserId, bool] | None:
        """(user id, disabled) for the identity holding `normalized_email`."""
        row = self._connection.execute(
            sa.select(users_table.c.id, users_table.c.disabled_at).where(
                sa.func.lower(users_table.c.email) == normalized_email
            )
        ).first()
        return None if row is None else (UserId(row.id), row.disabled_at is not None)

    def is_disabled(self, user_id: UserId) -> bool:
        """True when the identity exists and is disabled."""
        return (
            self._connection.execute(
                sa.select(users_table.c.id).where(
                    users_table.c.id == user_id.value, users_table.c.disabled_at.isnot(None)
                )
            ).first()
            is not None
        )

    def disable(self, user_id: UserId, *, now: datetime, provenance: str) -> bool:
        """One conditional write: disables the identity only while it is not
        disabled. False when it does not exist or is already disabled."""
        result = self._connection.execute(
            sa.update(users_table)
            .where(users_table.c.id == user_id.value, users_table.c.disabled_at.is_(None))
            .values(
                disabled_at=now,
                disabled_provenance=provenance,
                updated_at=now,
                record_version=users_table.c.record_version + 1,
            )
        )
        return result.rowcount == 1


__all__ = ["SqlAlchemyIdentityRepository"]
