"""`auth_rate_limits` adapter (WU-AUTH-20): read a window for update, write it
back, clear it. Keys are digests (security.login_throttle.throttle_key)."""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from security.login_throttle import ThrottleKeyKind, ThrottleWindow

from persistence.tables import auth_rate_limits_table


class SqlAlchemyAuthRateLimitRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(
        self, kind: ThrottleKeyKind, key_hash: str, *, for_update: bool = False
    ) -> ThrottleWindow | None:
        stmt = sa.select(auth_rate_limits_table).where(
            auth_rate_limits_table.c.key_kind == kind.value,
            auth_rate_limits_table.c.key_hash == key_hash,
        )
        if for_update:
            stmt = stmt.with_for_update()
        row = self._connection.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return ThrottleWindow(
            kind=kind,
            key_hash=key_hash,
            window_started_at=row["window_started_at"],
            failures=row["failures"],
            locked_until=row["locked_until"],
        )

    def put(self, window: ThrottleWindow, *, now: datetime) -> None:
        values = {
            "window_started_at": window.window_started_at,
            "failures": window.failures,
            "locked_until": window.locked_until,
            "updated_at": now,
        }
        updated = self._connection.execute(
            sa.update(auth_rate_limits_table)
            .where(
                auth_rate_limits_table.c.key_kind == window.kind.value,
                auth_rate_limits_table.c.key_hash == window.key_hash,
            )
            .values(**values)
        )
        if updated.rowcount == 0:
            self._connection.execute(
                sa.insert(auth_rate_limits_table).values(
                    key_kind=window.kind.value, key_hash=window.key_hash, **values
                )
            )

    def clear(self, kind: ThrottleKeyKind, key_hash: str, *, now: datetime) -> None:
        """A success closes the window: failures 0, no lock (the row stays as evidence)."""
        self._connection.execute(
            sa.update(auth_rate_limits_table)
            .where(
                auth_rate_limits_table.c.key_kind == kind.value,
                auth_rate_limits_table.c.key_hash == key_hash,
            )
            .values(failures=0, locked_until=None, window_started_at=now, updated_at=now)
        )


__all__ = ["SqlAlchemyAuthRateLimitRepository"]
