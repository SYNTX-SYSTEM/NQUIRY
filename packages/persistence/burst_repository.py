"""BurstRepository: the "canonical Burst state and frozen membership" port.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`BurstRepository`: canonical Burst state and frozen membership."
Carries no CommitUnit qualifier -- same reading PKG-06 applied to
`QuestionRepository` ("create/read"): the transition machinery this
port exposes performs genuine SQL state changes now, backed
independently by the migration's own triggers, rather than being
deferred behind not-yet-built CommitUnit/Command infrastructure.

THIS REPOSITORY IS NOT ITSELF A GOVERNED TRANSITION PATH
-----------------------------------------------------------
Every mutating method here is a single, real UPDATE/INSERT -- not
wrapped in BND-014, not producing an AuditEvent, not idempotent against
retry. It is exactly the kind of typed persistence adapter 14 §3.1
assigns to `persistence`, meant to be called *through* by a future
governed Command (Phase 3/4), not a claim that calling it now
constitutes a legitimate transition. `packages/application/burst_operations.py`
deliberately does **not** call any mutating method here -- 14 §3.1
gives `application` "Canonical write: no direct write", and PKG-01's
own established precedent is explicit that `application` "can read via
persistence but never write through it (writes stay commit-only)".
This package's mutating methods are therefore exercised only by tests,
the same disclosed-unwired pattern PKG-06 established for
`QuestionRepository.create_root`/`create_derived`.

WHY EACH TRANSITION METHOD TAKES AN `expected_record_version`
------------------------------------------------------------------
No CommitUnit/expected-version Command envelope exists yet (14 §26's
full mechanism is Phase 4), but a lost-update race between two
concurrent transition attempts is a real, present correctness hazard
this adapter can and should guard against on its own: every mutating
method issues its `UPDATE` with `WHERE id = ... AND workspace_id = ...
AND record_version = :expected`, and raises `BurstConflict` (not a
silent no-op) if zero rows changed -- either the Burst does not exist
at that Workspace, or another writer already advanced it past the
version this caller expected. This is a narrower guarantee than 14
§26's full optimistic-concurrency Command contract (there is still no
`expected_versions` list spanning multiple aggregates, no idempotency
key), but it is a real one, not a placeholder.

NO GENERIC `update_state` METHOD
-------------------------------------
14 PKG-07 PUBLIC_INTERFACES: "Generic ... generic status setters ...
are forbidden where they erase semantics." Each Burst transition (start/
pause/resume/complete) is its own named method with its own
transition-specific side effects (`started_at`/`paused_at`/`completed_at`/
the freeze fingerprint) -- there is no single method through which a
caller could request an arbitrary target state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.burst import BurstMode, BurstState, QuestionBurst
from domain.burst_membership import QuestionBurstMembership
from domain.question import QuestionOrigin
from semantic_types.ids import BurstId, QuestionId, RelationId, SessionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import burst_question_memberships_table, question_bursts_table


@runtime_checkable
class BurstRepository(Protocol):
    """Port: canonical Burst state and frozen membership create/read/
    transition (14 §10). No repository method returns an authority
    conclusion, and no method accepts an arbitrary target state --
    every transition is its own named method.
    """

    def create_prepared(self, burst: QuestionBurst) -> None: ...

    def get(self, burst_id: BurstId) -> QuestionBurst | None: ...

    def get_by_session(self, session_id: SessionId) -> QuestionBurst | None: ...

    def start(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        started_at: datetime,
    ) -> None: ...

    def pause(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        paused_at: datetime,
    ) -> None: ...

    def resume(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
    ) -> None: ...

    def complete(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        completed_at: datetime,
        frozen_membership_fingerprint: str,
    ) -> None: ...

    def add_member(self, membership: QuestionBurstMembership) -> None: ...

    def list_members(self, burst_id: BurstId) -> tuple[QuestionBurstMembership, ...]: ...


class BurstConflict(Exception):
    """Raised when a mutating method's expected-version guard fails:
    either the targeted Burst does not exist at the given Workspace, or
    it has already been advanced past the caller's expected version.
    Never raised for a legitimate, current-version match.
    """


class SqlAlchemyBurstRepository:
    """`BurstRepository` backed by `question_bursts`/
    `burst_question_memberships` via a SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create_prepared(self, burst: QuestionBurst) -> None:
        """03 TRN-BURST-001: create a Burst in PREPARED. `burst.state`
        must already be `PREPARED` (enforced by `QuestionBurst` itself
        having no constructor path to any other initial value the
        caller would reasonably pass here, and independently by the
        migration's `trg_question_bursts_enforce_initial_state`).
        """
        self._connection.execute(sa.insert(question_bursts_table).values(**_burst_to_row(burst)))

    def get(self, burst_id: BurstId) -> QuestionBurst | None:
        stmt = sa.select(question_bursts_table).where(question_bursts_table.c.id == burst_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _burst_from_row(row)

    def get_by_session(self, session_id: SessionId) -> QuestionBurst | None:
        """Architecture 17 materialization: the Session-read Query
        (14 §13 `GetSession`) needs its Session's own Burst without
        already knowing a `BurstId`. Uses `.one_or_none()` (raises on
        more than one row) rather than an ORDER BY/LIMIT heuristic --
        03 §19's own topology names no multi-Burst-per-Session concept
        anywhere in 02/03, and `question_bursts` carries no
        `created_at` column to order by even if one existed, so a
        second row for the same `session_id` would be a genuine schema/
        domain-invariant violation this method deliberately surfaces
        (`sqlalchemy.exc.MultipleResultsFound`) rather than silently
        picking one. Fresh read, no caching, same discipline every
        other "current state" reader in this codebase already uses.
        """
        stmt = sa.select(question_bursts_table).where(
            question_bursts_table.c.session_id == session_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _burst_from_row(row)

    def start(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        started_at: datetime,
    ) -> None:
        """03 TRN-BURST-002: PREPARED -> ACTIVE."""
        self._transition(
            burst_id=burst_id,
            workspace_id=workspace_id,
            expected_record_version=expected_record_version,
            values={"state": BurstState.ACTIVE.value, "started_at": started_at},
        )

    def pause(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        paused_at: datetime,
    ) -> None:
        """03 TRN-BURST-003: ACTIVE -> PAUSED."""
        self._transition(
            burst_id=burst_id,
            workspace_id=workspace_id,
            expected_record_version=expected_record_version,
            values={"state": BurstState.PAUSED.value, "paused_at": paused_at},
        )

    def resume(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
    ) -> None:
        """03 TRN-BURST-004: PAUSED -> ACTIVE."""
        self._transition(
            burst_id=burst_id,
            workspace_id=workspace_id,
            expected_record_version=expected_record_version,
            values={"state": BurstState.ACTIVE.value},
        )

    def complete(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        completed_at: datetime,
        frozen_membership_fingerprint: str,
    ) -> None:
        """03 TRN-BURST-005: ACTIVE or PAUSED -> COMPLETED.

        `frozen_membership_fingerprint` must already be computed (by
        `domain.burst_membership.compute_frozen_membership_fingerprint`,
        over the durable membership rows as they stand at this moment)
        -- this method stores it, it does not compute it, keeping the
        canonical-serialization algorithm in `domain` where it can be
        tested without a database.
        """
        if not frozen_membership_fingerprint:
            raise ValueError("frozen_membership_fingerprint must be non-empty")
        self._transition(
            burst_id=burst_id,
            workspace_id=workspace_id,
            expected_record_version=expected_record_version,
            values={
                "state": BurstState.COMPLETED.value,
                "completed_at": completed_at,
                "frozen_membership_fingerprint": frozen_membership_fingerprint,
            },
        )

    def _transition(
        self,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        values: dict[str, object],
    ) -> None:
        result = self._connection.execute(
            sa.update(question_bursts_table)
            .where(
                question_bursts_table.c.id == burst_id.value,
                question_bursts_table.c.workspace_id == workspace_id.value,
                question_bursts_table.c.record_version == expected_record_version.value,
            )
            .values(record_version=expected_record_version.next().value, **values)
        )
        if result.rowcount == 0:
            raise BurstConflict(
                f"burst {burst_id!r} not found at workspace {workspace_id!r} with "
                f"expected record_version {expected_record_version.value}"
            )

    def add_member(self, membership: QuestionBurstMembership) -> None:
        """03 TRN-Q-001's "Create Burst-capture membership relation."
        Rejected by `trg_burst_memberships_enforce_freeze` if the
        parent Burst is already COMPLETED -- this method performs no
        pre-check of its own, trusting the trigger as the single source
        of truth for that rule (checking twice would risk the two
        checks silently drifting apart, exactly what PKG-05's
        cross-layer agreement tests exist to catch when duplication is
        unavoidable; here it is avoidable).
        """
        self._connection.execute(
            sa.insert(burst_question_memberships_table).values(**_membership_to_row(membership))
        )

    def list_members(self, burst_id: BurstId) -> tuple[QuestionBurstMembership, ...]:
        stmt = (
            sa.select(burst_question_memberships_table)
            .where(burst_question_memberships_table.c.question_burst_id == burst_id.value)
            .order_by(burst_question_memberships_table.c.captured_order.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_membership_from_row(row) for row in rows)


def _burst_to_row(burst: QuestionBurst) -> dict[str, object]:
    return {
        "id": burst.burst_id.value,
        "session_id": burst.session_id.value,
        "workspace_id": burst.workspace_id.value,
        "state": burst.state.value,
        "mode": burst.mode.value,
        "started_at": burst.started_at,
        "paused_at": burst.paused_at,
        "completed_at": burst.completed_at,
        "frozen_membership_fingerprint": burst.frozen_membership_fingerprint,
        "record_version": burst.record_version.value,
    }


def _burst_from_row(row: sa.RowMapping) -> QuestionBurst:
    return QuestionBurst(
        burst_id=BurstId(row["id"]),
        session_id=SessionId(row["session_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        state=BurstState(row["state"]),
        mode=BurstMode(row["mode"]),
        started_at=row["started_at"],
        paused_at=row["paused_at"],
        completed_at=row["completed_at"],
        frozen_membership_fingerprint=row["frozen_membership_fingerprint"],
        record_version=RecordVersion(row["record_version"]),
    )


def _membership_to_row(membership: QuestionBurstMembership) -> dict[str, object]:
    return {
        "id": membership.burst_question_membership_id.value,
        "question_burst_id": membership.question_burst_id.value,
        "question_id": membership.question_id.value,
        "workspace_id": membership.workspace_id.value,
        "captured_order": membership.captured_order,
        "captured_at": membership.captured_at,
        "capture_actor_user_id": (
            None
            if membership.capture_actor_user_id is None
            else membership.capture_actor_user_id.value
        ),
        "capture_origin": membership.capture_origin.value,
        "record_version": membership.record_version.value,
    }


def _membership_from_row(row: sa.RowMapping) -> QuestionBurstMembership:
    return QuestionBurstMembership(
        burst_question_membership_id=RelationId(row["id"]),
        question_burst_id=BurstId(row["question_burst_id"]),
        question_id=QuestionId(row["question_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        captured_order=row["captured_order"],
        captured_at=row["captured_at"],
        capture_actor_user_id=(
            None if row["capture_actor_user_id"] is None else UserId(row["capture_actor_user_id"])
        ),
        capture_origin=QuestionOrigin(row["capture_origin"]),
        record_version=RecordVersion(row["record_version"]),
    )


__all__ = ["BurstRepository", "BurstConflict", "SqlAlchemyBurstRepository"]
