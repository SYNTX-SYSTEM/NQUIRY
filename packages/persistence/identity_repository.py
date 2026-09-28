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


__all__ = ["SqlAlchemyIdentityRepository"]
