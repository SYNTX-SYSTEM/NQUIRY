"""SessionParticipation persistence (F02 WU-02.8, 09 §28, 02 §12).

A RELATION (User <-> Session), not a canonical domain object and not
authority. Written only by `application.session_participation_handler`
through `CommitCoordinator`. The DB enforces the cross-Workspace FK, the
ACTIVE-membership precondition and one current participation per
(session, user) (migration b3d8e5f0a2c7).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from semantic_types.ids import SessionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import session_participations_table, users_table


@dataclass(frozen=True, slots=True)
class SessionParticipationRecord:
    participation_id: uuid.UUID
    session_id: SessionId
    workspace_id: WorkspaceId
    user_id: UserId
    joined_at: datetime
    left_at: datetime | None
    admitted_by_user_id: UserId
    record_version: RecordVersion
    user_name: str | None = None
    user_email: str | None = None


@runtime_checkable
class SessionParticipationRepository(Protocol):
    def admit(
        self,
        *,
        participation_id: uuid.UUID,
        session_id: SessionId,
        workspace_id: WorkspaceId,
        user_id: UserId,
        admitted_by_user_id: UserId,
        joined_at: datetime,
    ) -> None: ...

    def list_current(self, session_id: SessionId) -> tuple[SessionParticipationRecord, ...]: ...

    def get_current(
        self, session_id: SessionId, user_id: UserId
    ) -> SessionParticipationRecord | None: ...


class SqlAlchemySessionParticipationRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def admit(
        self,
        *,
        participation_id: uuid.UUID,
        session_id: SessionId,
        workspace_id: WorkspaceId,
        user_id: UserId,
        admitted_by_user_id: UserId,
        joined_at: datetime,
    ) -> None:
        self._connection.execute(
            sa.insert(session_participations_table).values(
                id=participation_id,
                session_id=session_id.value,
                workspace_id=workspace_id.value,
                user_id=user_id.value,
                joined_at=joined_at,
                left_at=None,
                admitted_by_user_id=admitted_by_user_id.value,
                record_version=1,
            )
        )

    def _select(self) -> sa.Select:
        t = session_participations_table
        return sa.select(
            t, users_table.c.name.label("user_name"), users_table.c.email.label("user_email")
        ).join(users_table, users_table.c.id == t.c.user_id)

    def list_current(self, session_id: SessionId) -> tuple[SessionParticipationRecord, ...]:
        t = session_participations_table
        rows = self._connection.execute(
            self._select()
            .where(t.c.session_id == session_id.value, t.c.left_at.is_(None))
            .order_by(t.c.joined_at.asc(), t.c.id.asc())
        ).mappings()
        return tuple(_from_row(row) for row in rows)

    def get_current(
        self, session_id: SessionId, user_id: UserId
    ) -> SessionParticipationRecord | None:
        t = session_participations_table
        row = (
            self._connection.execute(
                self._select().where(
                    t.c.session_id == session_id.value,
                    t.c.user_id == user_id.value,
                    t.c.left_at.is_(None),
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _from_row(row)


def _from_row(row: sa.RowMapping) -> SessionParticipationRecord:
    return SessionParticipationRecord(
        participation_id=row["id"],
        session_id=SessionId(row["session_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        user_id=UserId(row["user_id"]),
        joined_at=row["joined_at"],
        left_at=row["left_at"],
        admitted_by_user_id=UserId(row["admitted_by_user_id"]),
        record_version=RecordVersion(row["record_version"]),
        user_name=row["user_name"],
        user_email=row["user_email"],
    )


__all__ = [
    "SessionParticipationRecord",
    "SessionParticipationRepository",
    "SqlAlchemySessionParticipationRepository",
]
