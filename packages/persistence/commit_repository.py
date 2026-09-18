"""SqlAlchemyCommitRepository: the durable `CommitRepository` adapter.

Deliberately separate from `commit/coordinator.py` (unlike PKG-11's
`commit/idempotency.py`, which holds its own concrete adapter directly)
-- 14 PKG-13's own `FILES_ALLOWED_TO_CREATE` names "packages/commit
coordinator" and "persistence commit repository" as two distinct
creation targets. See `scripts/check_architecture_dependencies.py`'s
own `INTERNAL_ALLOWED["persistence"]` citation for why the resulting
`persistence -> commit` edge does not create an actual circular
import even though `commit -> persistence` already exists too.
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from commit.coordinator import CommitOutcome, CommitUnit
from semantic_types.ids import AttemptId, AuditEventId, CommandId, CommitId, WorkspaceId

from persistence.tables import commit_units_table


class SqlAlchemyCommitRepository:
    """`CommitRepository` backed by `commit_units` via a SQLAlchemy
    Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def append(self, commit_unit: CommitUnit) -> None:
        self._connection.execute(
            sa.insert(commit_units_table).values(
                id=commit_unit.commit_id.value,
                workspace_id=commit_unit.workspace_id.value,
                command_id=commit_unit.command_id.value,
                attempt_id=commit_unit.attempt_id.value,
                target_refs=list(commit_unit.target_refs),
                relation_refs=list(commit_unit.relation_refs),
                governance_refs=list(commit_unit.governance_refs),
                audit_event_ids=[i.value for i in commit_unit.audit_event_ids],
                outbox_ids=list(commit_unit.outbox_ids),
                commit_time_proof_ref=commit_unit.commit_time_proof_ref,
                committed_at=commit_unit.committed_at,
                outcome=commit_unit.outcome.value,
            )
        )

    def get(self, commit_id: CommitId) -> CommitUnit | None:
        stmt = sa.select(commit_units_table).where(commit_units_table.c.id == commit_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _commit_unit_from_row(row)


def _commit_unit_from_row(row: sa.RowMapping) -> CommitUnit:
    return CommitUnit(
        commit_id=CommitId(row["id"]),
        command_id=CommandId(row["command_id"]),
        attempt_id=AttemptId(row["attempt_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        target_refs=tuple(row["target_refs"] or ()),
        relation_refs=tuple(row["relation_refs"] or ()),
        governance_refs=tuple(row["governance_refs"] or ()),
        audit_event_ids=tuple(AuditEventId(i) for i in (row["audit_event_ids"] or ())),
        outbox_ids=tuple(uuid.UUID(str(i)) for i in (row["outbox_ids"] or ())),
        commit_time_proof_ref=row["commit_time_proof_ref"],
        committed_at=row["committed_at"],
        outcome=CommitOutcome(row["outcome"]),
    )


__all__ = ["SqlAlchemyCommitRepository"]
