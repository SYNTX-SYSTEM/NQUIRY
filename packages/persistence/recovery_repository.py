"""SqlAlchemyRecoveryRepository: the durable `RecoveryRepository`
adapter.

14 section 10: "RecoveryRepository: RecoveryRecord reads and bounded
operational updates." `record_attempt`/`mark_resolved` are the ONLY
two write methods -- no generic setter exists, matching this package's
own FORBIDDEN_SHORTCUTS ("generic status setters ... forbidden where
they erase semantics"). `is_target_blocked` is read-only.

WHY `is_target_blocked` NEEDS NO SEPARATE JOIN TABLE
--------------------------------------------------------------------
See `recovery.models`'s own module docstring: "is target X blocked" is
answered directly against `recovery_records` itself --
`result = 'UNRESOLVED' AND :target_ref = ANY (blocked_target_refs)` --
so resolving a record (leaving `UNRESOLVED`) automatically excludes its
own formerly-blocked refs from every future query, with no separate
"unblock" write.

WHY `record_attempt`/`mark_resolved` NOW ALSO ADVANCE `record_version`
--------------------------------------------------------------------
PKG-24's own retrofit (`recovery.models`'s own docstring) gives
`recovery_records` a real optimistic-concurrency column for the first
time -- every governed mutation this repository performs advances it
by one, the same convention every other versioned table in this
codebase already follows.
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from recovery.certainty import ConsequenceCertainty
from recovery.failure_classifier import FailureClass
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    RecoveryId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from persistence.tables import recovery_records_table


class RecoveryRecordNotFound(Exception):
    """Raised by `record_attempt`/`mark_resolved` when no record exists
    for the given `recovery_id`.
    """


class SqlAlchemyRecoveryRepository:
    """`RecoveryRepository` backed by `recovery_records` via a
    SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(self, record: RecoveryRecord) -> None:
        self._connection.execute(
            sa.insert(recovery_records_table).values(
                id=record.recovery_id.value,
                workspace_id=record.workspace_scope_ref.value,
                failure_correlation_ref=record.failure_correlation_ref.value,
                original_command_id=record.original_command_id.value,
                original_attempt_id=record.original_attempt_id.value,
                original_commit_id=(
                    record.original_commit_id.value
                    if record.original_commit_id is not None
                    else None
                ),
                failure_classifications=[fc.value for fc in record.failure_classifications],
                known_canonical_state_ref=record.known_canonical_state_ref,
                canonical_state_certainty=record.canonical_state_certainty.value,
                known_external_consequence_ref=record.known_external_consequence_ref,
                external_consequence_certainty=record.external_consequence_certainty.value,
                unknown_consequence_description=record.unknown_consequence_description,
                last_proven_valid_state_ref=record.last_proven_valid_state_ref,
                recovery_class=record.recovery_class.value,
                recovery_actor_type=record.recovery_actor_type,
                recovery_actor_id=record.recovery_actor_id,
                required_authority_ref=record.required_authority_ref,
                current_authority_binding_ref=record.current_authority_binding_ref,
                human_decision_ref=(
                    record.human_decision_ref.value
                    if record.human_decision_ref is not None
                    else None
                ),
                evidence_proof_refs=list(record.evidence_proof_refs),
                recovery_command_ids=[cid.value for cid in record.recovery_command_ids],
                recovery_attempt_refs=list(record.recovery_attempt_refs),
                blocked_target_refs=list(record.blocked_target_refs),
                result=record.result.value,
                created_at=record.created_at,
                updated_at=record.updated_at,
                resolved_at=record.resolved_at,
                audit_linkage=record.audit_linkage,
                record_version=record.record_version.value,
            )
        )

    def get(self, recovery_id: RecoveryId, workspace_id: WorkspaceId) -> RecoveryRecord | None:
        stmt = sa.select(recovery_records_table).where(
            recovery_records_table.c.id == recovery_id.value,
            recovery_records_table.c.workspace_id == workspace_id.value,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _record_from_row(row)

    def record_attempt(
        self,
        recovery_id: RecoveryId,
        workspace_id: WorkspaceId,
        *,
        attempt_ref: str,
        updated_at: datetime,
    ) -> None:
        current = self.get(recovery_id, workspace_id)
        if current is None:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")
        result = self._connection.execute(
            sa.update(recovery_records_table)
            .where(
                recovery_records_table.c.id == recovery_id.value,
                recovery_records_table.c.workspace_id == workspace_id.value,
            )
            .values(
                recovery_attempt_refs=[*current.recovery_attempt_refs, attempt_ref],
                updated_at=updated_at,
                record_version=current.record_version.next().value,
            )
        )
        if result.rowcount == 0:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")

    def mark_resolved(
        self,
        recovery_id: RecoveryId,
        workspace_id: WorkspaceId,
        *,
        result: RecoveryOutcome,
        resolved_at: datetime,
        last_proven_valid_state_ref: str | None,
    ) -> None:
        current = self.get(recovery_id, workspace_id)
        if current is None:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")
        outcome = self._connection.execute(
            sa.update(recovery_records_table)
            .where(
                recovery_records_table.c.id == recovery_id.value,
                recovery_records_table.c.workspace_id == workspace_id.value,
            )
            .values(
                result=result.value,
                resolved_at=resolved_at,
                last_proven_valid_state_ref=last_proven_valid_state_ref,
                updated_at=resolved_at,
                record_version=current.record_version.next().value,
            )
        )
        if outcome.rowcount == 0:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")

    def is_target_blocked(
        self,
        workspace_id: WorkspaceId,
        *,
        target_ref: str,
        exclude_recovery_id: RecoveryId | None = None,
    ) -> bool:
        conditions = [
            recovery_records_table.c.workspace_id == workspace_id.value,
            recovery_records_table.c.result == RecoveryOutcome.UNRESOLVED.value,
            recovery_records_table.c.blocked_target_refs.any(target_ref),
        ]
        if exclude_recovery_id is not None:
            conditions.append(recovery_records_table.c.id != exclude_recovery_id.value)
        stmt = sa.select(sa.literal(1)).where(*conditions).limit(1)
        return self._connection.execute(stmt).first() is not None


def _record_from_row(row: sa.RowMapping) -> RecoveryRecord:
    return RecoveryRecord(
        recovery_id=RecoveryId(row["id"]),
        workspace_scope_ref=WorkspaceId(row["workspace_id"]),
        failure_correlation_ref=CorrelationId(row["failure_correlation_ref"]),
        original_command_id=CommandId(row["original_command_id"]),
        original_attempt_id=AttemptId(row["original_attempt_id"]),
        original_commit_id=(
            CommitId(row["original_commit_id"]) if row["original_commit_id"] is not None else None
        ),
        failure_classifications=tuple(FailureClass(v) for v in row["failure_classifications"]),
        known_canonical_state_ref=row["known_canonical_state_ref"],
        canonical_state_certainty=ConsequenceCertainty(row["canonical_state_certainty"]),
        known_external_consequence_ref=row["known_external_consequence_ref"],
        external_consequence_certainty=ConsequenceCertainty(row["external_consequence_certainty"]),
        unknown_consequence_description=row["unknown_consequence_description"],
        last_proven_valid_state_ref=row["last_proven_valid_state_ref"],
        recovery_class=RecoveryClass(row["recovery_class"]),
        recovery_actor_type=row["recovery_actor_type"],
        recovery_actor_id=row["recovery_actor_id"],
        required_authority_ref=row["required_authority_ref"],
        current_authority_binding_ref=row["current_authority_binding_ref"],
        human_decision_ref=(
            DecisionId(row["human_decision_ref"]) if row["human_decision_ref"] is not None else None
        ),
        evidence_proof_refs=tuple(row["evidence_proof_refs"]),
        recovery_command_ids=tuple(CommandId(v) for v in row["recovery_command_ids"]),
        recovery_attempt_refs=tuple(row["recovery_attempt_refs"]),
        blocked_target_refs=tuple(row["blocked_target_refs"]),
        result=RecoveryOutcome(row["result"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        resolved_at=row["resolved_at"],
        audit_linkage=row["audit_linkage"],
        record_version=RecordVersion(row["record_version"]),
    )


__all__ = ["RecoveryRecordNotFound", "SqlAlchemyRecoveryRepository"]
