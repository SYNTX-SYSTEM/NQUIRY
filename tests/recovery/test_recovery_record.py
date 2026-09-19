"""T8 RECOVERY RECORD TEST: RecoveryRecord/RecoveryOutcome/RecoveryClass
and SqlAlchemyRecoveryRepository, against real PostgreSQL where noted.

14 section 48's own PKG-23 scope: `packages/recovery/models.py`,
`packages/persistence/recovery_repository.py`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.recovery_repository import RecoveryRecordNotFound, SqlAlchemyRecoveryRepository
from persistence.tables import recovery_records_table
from recovery.certainty import ConsequenceCertainty
from recovery.failure_classifier import FailureClass
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    RecoveryId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def _record_real_command_and_commit(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> tuple[CommandId, AttemptId, CommitId]:
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    SqlAlchemyCommandRepository(db_connection).record_attempt(
        CommandEnvelope(
            command_id=command_id,
            command_type="CMD_TEST_OPERATION",
            command_contract_version=ContractVersion("1.0"),
            attempt_id=attempt_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            requested_at=_NOW,
            requesting_actor_type="HUMAN_USER",
            requesting_actor_id="user-ref-1",
            workspace_scope_ref=workspace_id,
            target_refs=(),
            expected_versions={},
            payload=_Payload("hello"),
        ),
        received_at=_NOW,
    )
    commit_id = CommitId(uuid.uuid4())
    SqlAlchemyCommitRepository(db_connection).append(
        CommitUnit(
            commit_id=commit_id,
            command_id=command_id,
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            target_refs=(),
            relation_refs=(),
            governance_refs=(),
            audit_event_ids=(),
            outbox_ids=(),
            committed_at=_NOW,
            outcome=CommitOutcome.COMMITTED,
        )
    )
    return command_id, attempt_id, commit_id


def _record(
    *,
    workspace_id: WorkspaceId,
    command_id: CommandId,
    attempt_id: AttemptId,
    commit_id: CommitId | None = None,
    result: RecoveryOutcome = RecoveryOutcome.UNRESOLVED,
    resolved_at: datetime | None = None,
) -> RecoveryRecord:
    return RecoveryRecord(
        recovery_id=RecoveryId(uuid.uuid4()),
        workspace_scope_ref=workspace_id,
        failure_correlation_ref=CorrelationId(uuid.uuid4()),
        original_command_id=command_id,
        original_attempt_id=attempt_id,
        original_commit_id=commit_id,
        failure_classifications=(FailureClass.F_PERS,),
        canonical_state_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        external_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        recovery_actor_type="SYSTEM_SERVICE",
        recovery_actor_id="recovery-worker-1",
        result=result,
        created_at=_NOW,
        updated_at=_NOW,
        resolved_at=resolved_at,
    )


# ---------------------------------------------------------------------------
# RecoveryRecord construction (no database)
# ---------------------------------------------------------------------------


def test_denies_a_non_failure_class_in_failure_classifications() -> None:
    with pytest.raises(TypeError, match="failure_classifications"):
        RecoveryRecord(
            recovery_id=RecoveryId(uuid.uuid4()),
            workspace_scope_ref=WorkspaceId(uuid.uuid4()),
            failure_correlation_ref=CorrelationId(uuid.uuid4()),
            original_command_id=CommandId(uuid.uuid4()),
            original_attempt_id=AttemptId(uuid.uuid4()),
            failure_classifications=("F-PERS",),  # type: ignore[arg-type]
            canonical_state_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
            external_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
            recovery_class=RecoveryClass.RC_02_RECONCILIATION,
            recovery_actor_type="SYSTEM_SERVICE",
            recovery_actor_id="recovery-worker-1",
            result=RecoveryOutcome.UNRESOLVED,
            created_at=_NOW,
            updated_at=_NOW,
        )


def test_denies_resolved_at_set_while_unresolved() -> None:
    with pytest.raises(ValueError, match="resolved_at"):
        _record(
            workspace_id=WorkspaceId(uuid.uuid4()),
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            result=RecoveryOutcome.UNRESOLVED,
            resolved_at=_NOW,
        )


def test_denies_a_terminal_outcome_without_resolved_at() -> None:
    with pytest.raises(ValueError, match="resolved_at"):
        _record(
            workspace_id=WorkspaceId(uuid.uuid4()),
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            result=RecoveryOutcome.RECOVERED,
            resolved_at=None,
        )


# ---------------------------------------------------------------------------
# SqlAlchemyRecoveryRepository (real PostgreSQL)
# ---------------------------------------------------------------------------


def test_create_then_get_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="recovery-record-crud@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id, command_id=command_id, attempt_id=attempt_id, commit_id=commit_id
    )

    repo.create(record)

    assert repo.get(record.recovery_id, workspace_id) == record


def test_record_attempt_appends_without_losing_history(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="recovery-record-attempts@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id, command_id=command_id, attempt_id=attempt_id, commit_id=commit_id
    )
    repo.create(record)

    repo.record_attempt(
        record.recovery_id, workspace_id, attempt_ref="attempt-1", updated_at=_LATER
    )
    repo.record_attempt(
        record.recovery_id, workspace_id, attempt_ref="attempt-2", updated_at=_LATER
    )

    stored = repo.get(record.recovery_id, workspace_id)
    assert stored is not None
    assert stored.recovery_attempt_refs == ("attempt-1", "attempt-2")


def test_record_attempt_against_a_nonexistent_record_raises(db_connection: sa.Connection) -> None:
    with pytest.raises(RecoveryRecordNotFound):
        SqlAlchemyRecoveryRepository(db_connection).record_attempt(
            RecoveryId(uuid.uuid4()),
            WorkspaceId(uuid.uuid4()),
            attempt_ref="attempt-1",
            updated_at=_NOW,
        )


def test_mark_resolved_transitions_from_unresolved_to_terminal(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="recovery-record-resolve@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id, command_id=command_id, attempt_id=attempt_id, commit_id=commit_id
    )
    repo.create(record)

    repo.mark_resolved(
        record.recovery_id,
        workspace_id,
        result=RecoveryOutcome.RECONCILED,
        resolved_at=_LATER,
        last_proven_valid_state_ref="session:1@v2",
    )

    stored = repo.get(record.recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.RECONCILED
    assert stored.resolved_at == _LATER
    assert stored.last_proven_valid_state_ref == "session:1@v2"


def test_db_trigger_rejects_insert_with_non_unresolved_result(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (structural, DB-layer): a
    RecoveryRecord cannot be created already "resolved" -- every
    record starts UNRESOLVED (10 section 64), enforced by the real
    trigger, not merely by this repository's own Python discipline.
    """
    workspace_id = _workspace(db_connection, email="recovery-record-bad-insert@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="must be created with result"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(recovery_records_table).values(
                id=uuid.uuid4(),
                workspace_id=workspace_id.value,
                failure_correlation_ref=uuid.uuid4(),
                original_command_id=command_id.value,
                original_attempt_id=attempt_id.value,
                original_commit_id=commit_id.value,
                failure_classifications=["F-PERS"],
                canonical_state_certainty="CANONICAL_STATE_UNKNOWN",
                external_consequence_certainty="EXTERNAL_CONSEQUENCE_UNKNOWN",
                recovery_class="RC-02",
                recovery_actor_type="SYSTEM_SERVICE",
                recovery_actor_id="recovery-worker-1",
                evidence_proof_refs=[],
                recovery_command_ids=[],
                recovery_attempt_refs=[],
                result="RECOVERED",
                created_at=_NOW,
                updated_at=_NOW,
                resolved_at=_NOW,
            )
        )


def test_db_trigger_rejects_reopening_a_terminal_result(db_connection: sa.Connection) -> None:
    """Once RESOLVED, a RecoveryRecord's own `result` is terminal (10
    section 64) -- a second, direct attempt to move it to a DIFFERENT
    terminal outcome is rejected by the real trigger.
    """
    workspace_id = _workspace(db_connection, email="recovery-record-reopen@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id, command_id=command_id, attempt_id=attempt_id, commit_id=commit_id
    )
    repo.create(record)
    repo.mark_resolved(
        record.recovery_id,
        workspace_id,
        result=RecoveryOutcome.NO_ACTION_REQUIRED,
        resolved_at=_LATER,
        last_proven_valid_state_ref=None,
    )

    with pytest.raises(sa.exc.DBAPIError, match="is terminal"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(recovery_records_table)
            .where(recovery_records_table.c.id == record.recovery_id.value)
            .values(result="RECOVERED")
        )


def test_db_trigger_rejects_mutating_identity_fields(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="recovery-record-identity@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id, command_id=command_id, attempt_id=attempt_id, commit_id=commit_id
    )
    repo.create(record)

    with pytest.raises(sa.exc.DBAPIError, match="immutable"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(recovery_records_table)
            .where(recovery_records_table.c.id == record.recovery_id.value)
            .values(recovery_actor_id="someone-else")
        )


def test_forged_original_command_without_a_real_command_is_rejected(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: forged original reference. A
    RecoveryRecord cannot claim an `original_command_id` that was never
    actually committed to `commands` -- rejected by the real composite
    foreign key.
    """
    workspace_id = _workspace(db_connection, email="recovery-record-forged@nonproof.test")
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=workspace_id,
        command_id=CommandId(uuid.uuid4()),  # never recorded
        attempt_id=AttemptId(uuid.uuid4()),
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create(record)


def test_cross_workspace_original_command_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory Workspace attack: the real command exists, but under a
    DIFFERENT Workspace than the one this RecoveryRecord claims --
    rejected by the composite (id, workspace_id) foreign key.
    """
    real_workspace_id = _workspace(db_connection, email="recovery-record-xws-real@nonproof.test")
    other_workspace_id = _workspace(db_connection, email="recovery-record-xws-other@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=real_workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = _record(
        workspace_id=other_workspace_id,  # does not match the real command's Workspace
        command_id=command_id,
        attempt_id=attempt_id,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create(record)
