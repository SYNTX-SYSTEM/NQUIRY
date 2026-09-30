"""Concrete `security.auth_methods.AuthenticationMethodRepository`, backed by
`authentication_methods` (migration `f1a7c3d9b2e4`; WU-AUTH-02).

Same port/adapter split as `local_auth_repository.py`. Lookups are by method
id or by user id only: there is no lookup by email, so nothing here can relate
two identities through an email value (24 §10.4).

`revoke` is one conditional UPDATE (`WHERE status = 'ACTIVE'`): of two
concurrent revocations exactly one changes the row, decided by the database.
The database itself refuses every other change to a method (triggers in the
migration), so these rules hold for any writer, not only for this class.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from security.auth_methods import (
    AuthenticationMethod,
    AuthenticationMethodStatus,
    AuthenticationMethodType,
)
from semantic_types.ids import AuthenticationMethodId, UserId

from persistence.tables import authentication_methods_table


def _to_method(row: Any) -> AuthenticationMethod:
    return AuthenticationMethod(
        method_id=AuthenticationMethodId(row["id"]),
        user_id=UserId(row["user_id"]),
        method_type=AuthenticationMethodType(row["method_type"]),
        status=AuthenticationMethodStatus(row["status"]),
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
        last_authenticated_at=row["last_authenticated_at"],
        provenance_ref=row["provenance_ref"],
    )


class SqlAlchemyAuthenticationMethodRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        user_id: UserId,
        method_type: AuthenticationMethodType,
        provenance_ref: str,
        now: datetime,
    ) -> AuthenticationMethod:
        method = AuthenticationMethod(
            method_id=AuthenticationMethodId(uuid.uuid4()),
            user_id=user_id,
            method_type=method_type,
            status=AuthenticationMethodStatus.ACTIVE,
            created_at=now,
            revoked_at=None,
            last_authenticated_at=None,
            provenance_ref=provenance_ref,
        )
        self._connection.execute(
            sa.insert(authentication_methods_table).values(
                id=method.method_id.value,
                user_id=user_id.value,
                method_type=method_type.value,
                status=method.status.value,
                created_at=now,
                revoked_at=None,
                last_authenticated_at=None,
                provenance_ref=provenance_ref,
            )
        )
        return method

    def get(self, method_id: AuthenticationMethodId) -> AuthenticationMethod | None:
        row = (
            self._connection.execute(
                sa.select(authentication_methods_table).where(
                    authentication_methods_table.c.id == method_id.value
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_method(row)

    def list_for_user(self, user_id: UserId) -> tuple[AuthenticationMethod, ...]:
        rows = (
            self._connection.execute(
                sa.select(authentication_methods_table)
                .where(authentication_methods_table.c.user_id == user_id.value)
                .order_by(
                    authentication_methods_table.c.created_at,
                    authentication_methods_table.c.id,
                )
            )
            .mappings()
            .all()
        )
        return tuple(_to_method(row) for row in rows)

    def revoke(self, method_id: AuthenticationMethodId, *, revoked_at: datetime) -> bool:
        """True when this call revoked the method; False when it does not
        exist or was already revoked (nothing changes)."""
        result = self._connection.execute(
            sa.update(authentication_methods_table)
            .where(
                authentication_methods_table.c.id == method_id.value,
                authentication_methods_table.c.status == AuthenticationMethodStatus.ACTIVE.value,
            )
            .values(status=AuthenticationMethodStatus.REVOKED.value, revoked_at=revoked_at)
        )
        return result.rowcount == 1


__all__ = ["SqlAlchemyAuthenticationMethodRepository"]
