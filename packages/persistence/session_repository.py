"""SessionRepository: the read-only half of the 14 section 10 port.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`SessionRepository`: canonical current version, state mutation only
through transition plan."

WHY THIS PACKAGE ONCE BUILT ONLY THE "CURRENT VERSION" HALF, AND WHY
`create()` IS NOW ADDED (F02 WU-02.3)
------------------------------------------------------------
PKG-05 deliberately deferred the whole port ("a repository written now
could only offer a write path with neither [CommitUnit nor the
boundary pipeline]" -- `persistence/challenge_session_mapping.py`'s own
docstring). Both now exist (PKG-08/09 boundaries, PKG-13 CommitCoordinator),
but 14 assigned PKG-14 no Session *mutation* -- 03 section 39's own
TRN-SEL-001/002 keep the Session in `QUESTION_SELECTION`
("state-preserving consequential mutation"), so PKG-14 itself never
wrote a `sessions` row. What PKG-14 genuinely needed, for the first
time, was a live, fresh, single-query read of a Session's current state
and `record_version` -- BND-007's own state-topology precondition and
BND-014's own AC-09-001 freshness check both require it. `create()`
below is the real "canonical write" half 14's own port description
always named ("`SessionRepository`: canonical current version, state
mutation only through transition plan") -- added now because
`application.session_creation_handler.create_session` (F02 WU-02.3,
TRN-SESS-001, "Session absent -> DRAFT") is the first real, governed
caller, mirroring `persistence.decision_repository.DecisionRepository.create`'s
own identical shape (`create(decision: Decision) -> None`, a plain
fact-recording insert of an already-fully-constructed domain object,
not itself an authority decision -- 14 section 10 non-collapse: "No
repository returns an authority conclusion") rather than
`ChallengeRepository.create()`'s own individual-kwargs shape, since
`create_session` (like `open_decision_consideration`) builds the whole
`Session` value itself before handing it to
`commit.coordinator.CommitCoordinator` via a `MutationExecutor`, the
same mechanism `OpenDecisionConsideration` already established for
this exact "authority-binding-gated child-object creation" shape
(unlike `CreateChallenge`, which has no `HumanAuthorityBinding` to
check at all and therefore hand-rolls its own write path instead of
using `CommitCoordinator` -- see that module's own docstring).

`get` returns the real `domain.session.Session` via
`persistence.challenge_session_mapping.session_from_row` (PKG-05's own
row-to-domain mapper) rather than re-deriving that mapping a second
time.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.question_selection import session_target_ref
from domain.session import Session, SessionState
from semantic_types.ids import SessionId
from semantic_types.versions import RecordVersion

from persistence.challenge_session_mapping import session_from_row
from persistence.tables import sessions_table


class SessionTransitionConflict(Exception):
    """A guarded transition matched no row: the Session is not at the
    expected state/version (stale view or concurrent writer)."""


@runtime_checkable
class SessionRepository(Protocol):
    """Port: Session canonical current-version read plus the one
    governed creation write (14 section 10).
    """

    def get(self, session_id: SessionId) -> Session | None:
        """The current `sessions` row for `session_id`, or `None` if it
        does not exist. Always a fresh read -- no caching, matching
        every other "current state" reader in this codebase
        (`AuthorityResolver.resolve`, `MembershipRepository.get_current_membership`).
        """
        ...

    def create(self, session: Session) -> None:
        """Insert a new `sessions` row from an already-fully-constructed
        `Session` value (mirrors `persistence.decision_repository.DecisionRepository.create`).
        Raises a real database exception on any constraint violation
        (notably `fk_sessions_challenge_workspace`, migration 003's
        own enforcement that `session.workspace_id` equals the
        Challenge's own real Workspace -- a caller-forged mismatch is
        rejected by the database itself, not merely trusted).
        `application.session_creation_handler.create_session` is this
        method's one legitimate caller."""
        ...

    def transition(
        self,
        *,
        session_id: SessionId,
        from_state: SessionState,
        to_state: SessionState,
        expected_record_version: RecordVersion,
        updated_at: datetime,
    ) -> None:
        """One governed Session state transition (F02 WU-02.7). Guarded by
        `expected_record_version` AND `from_state`; raises
        `SessionTransitionConflict` if no row matched (the caller's
        mutation maps it to `StaleVersionConflict`). Legality of
        `(from_state, to_state)` is additionally enforced by the DB trigger
        `trg_sessions_enforce_transition` (migration 003). Caller:
        `application.session_control_handler` only.
        No generic state setter exists (09 §27.2)."""
        ...


class SqlAlchemySessionRepository:
    """`SessionRepository` backed by `sessions` via a SQLAlchemy Core
    connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(self, session_id: SessionId) -> Session | None:
        stmt = sa.select(sessions_table).where(sessions_table.c.id == session_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else session_from_row(dict(row))

    def create(self, session: Session) -> None:
        self._connection.execute(
            sa.insert(sessions_table).values(
                id=session.session_id.value,
                challenge_id=session.challenge_id.value,
                workspace_id=session.workspace_id.value,
                applied_method_key=session.applied_method_key,
                applied_method_version=session.applied_method_version.value,
                state=session.state.value,
                created_at=session.created_at,
                updated_at=session.updated_at,
                closed_at=session.closed_at,
                record_version=session.record_version.value,
            )
        )

    def transition(
        self,
        *,
        session_id: SessionId,
        from_state: SessionState,
        to_state: SessionState,
        expected_record_version: RecordVersion,
        updated_at: datetime,
    ) -> None:
        result = self._connection.execute(
            sa.update(sessions_table)
            .where(
                sessions_table.c.id == session_id.value,
                sessions_table.c.state == from_state.value,
                sessions_table.c.record_version == expected_record_version.value,
            )
            .values(
                state=to_state.value,
                updated_at=updated_at,
                record_version=expected_record_version.next().value,
            )
        )
        if result.rowcount == 0:
            raise SessionTransitionConflict(
                f"session {session_id.value} not at {from_state.value} "
                f"record_version {expected_record_version.value}"
            )


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
