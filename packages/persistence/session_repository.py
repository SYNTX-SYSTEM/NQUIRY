"""SessionRepository: the read-only half of the 14 section 10 port.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`SessionRepository`: canonical current version, state mutation only
through transition plan."

WHY THIS PACKAGE BUILDS ONLY THE "CURRENT VERSION" HALF
------------------------------------------------------------
PKG-05 deliberately deferred the whole port ("a repository written now
could only offer a write path with neither [CommitUnit nor the
boundary pipeline]" -- `persistence/challenge_session_mapping.py`'s own
docstring). Both now exist (PKG-08/09 boundaries, PKG-13 CommitCoordinator),
but 14 assigns PKG-14 no Session *mutation* -- 03 section 39's own
TRN-SEL-001/002 keep the Session in `QUESTION_SELECTION`
("state-preserving consequential mutation"), so this package never
writes a `sessions` row. What PKG-14 genuinely needs, for the first
time, is a live, fresh, single-query read of a Session's current state
and `record_version` -- BND-007's own state-topology precondition and
BND-014's own AC-09-001 freshness check both require it. This module
therefore materializes exactly the "canonical current version" half of
14's own port description, honestly leaving "state mutation only
through transition plan" to whichever future package first needs to
mutate a Session (14's own port name, `SessionRepository`, is not
claimed as fully implemented -- only this reading is).

`get` returns the real `domain.session.Session` via
`persistence.challenge_session_mapping.session_from_row` (PKG-05's own
row-to-domain mapper) rather than re-deriving that mapping a second
time.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.question_selection import session_target_ref
from domain.session import Session
from semantic_types.ids import SessionId
from semantic_types.versions import RecordVersion

from persistence.challenge_session_mapping import session_from_row
from persistence.tables import sessions_table


@runtime_checkable
class SessionRepository(Protocol):
    """Port: Session canonical current-version read only (14 section 10,
    partial -- see module docstring).
    """

    def get(self, session_id: SessionId) -> Session | None:
        """The current `sessions` row for `session_id`, or `None` if it
        does not exist. Always a fresh read -- no caching, matching
        every other "current state" reader in this codebase
        (`AuthorityResolver.resolve`, `MembershipRepository.get_current_membership`).
        """
        ...


class SqlAlchemySessionRepository:
    """`SessionRepository` backed by `sessions` via a SQLAlchemy Core
    connection. Read-only by construction -- no `create`/`update`
    method exists.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(self, session_id: SessionId) -> Session | None:
        stmt = sa.select(sessions_table).where(sessions_table.c.id == session_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else session_from_row(dict(row))


class SqlAlchemySessionVersionReader:
    """`commit.coordinator.CurrentVersionReader` reading the REAL, fresh
    `sessions.record_version` for one Session -- no caching, one query
    per call (AC-09-001: "authoritative commit-time version"). Lives
    here, not in `application.question_selection_handler`, because
    `application` may not import `sqlalchemy` directly (14 §4's
    forbidden-dependency matrix; 14 §3.1's own "Must not depend on:
    ORM mutation, provider SDK" for this layer) -- the same "direct
    persistence" forbidden shortcut PKG-14's own coding prompt names.
    Structurally satisfies `commit.coordinator.CurrentVersionReader`
    (a `Protocol`) without inheriting from it.
    """

    def __init__(self, connection: sa.Connection, *, session_id: SessionId) -> None:
        self._connection = connection
        self._session_id = session_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != session_target_ref(self._session_id):
            return None
        stmt = sa.select(sessions_table.c.record_version).where(
            sessions_table.c.id == self._session_id.value
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


__all__ = ["SessionRepository", "SqlAlchemySessionRepository", "SqlAlchemySessionVersionReader"]
