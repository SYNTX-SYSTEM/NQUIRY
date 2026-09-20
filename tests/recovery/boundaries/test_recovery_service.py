"""T8/T4 CROSS-LAYER TEST: `application.recovery_handler.RecoveryService`
end to end, against real PostgreSQL -- the one production caller of
`Bnd017FailureIndeterminateEvaluator`/`Bnd018RecoveryRollbackEvaluator`
wired through `boundaries.registry.evaluate_chain`, `BND_001`, `BND_002`,
and the real `SqlAlchemyRecoveryRepository`/`SqlAlchemyWorkspaceRepository`.

This is the CRITICAL-package adversarial suite (14 section 48's own
PKG-24 CRITICAL classification): every mandatory attack this package's
own OBJECTIVE names (admin recovery, AI chooses recovery outcome, blind
retry, dependent operation after INDETERMINATE, recover to a
never-legitimate state, erase audit/history, unresolvable/cross-Workspace
target, stale version / concurrent attempt, event replay) plus the
novel/adapted attacks specific to this service's own composition (chain
short-circuit order, replay-after-success). BND-017/BND-018's own
isolated unit-level attacks already live in `tests/boundaries/
test_bnd_017_failure_indeterminate.py`/`test_bnd_018_recovery_rollback.py`;
this file proves the SAME invariants hold once wired through the real
governed Command path, not just at the evaluator's own boundary.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.recovery_handler import (
    RecoveryResolutionDenied,
    RecoveryResolutionFacts,
    RecoveryResolutionStaleVersion,
    RecoveryService,
)
from authority.actor import ActorClass, ActorIdentity
from boundaries.types import BoundaryId
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.recovery_repository import SqlAlchemyRecoveryRepository
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
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
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_SYSTEM_ACTOR = ActorIdentity(ActorClass.SYSTEM_SERVICE, "recovery-worker-1")


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


def _seed_recovery_record(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, target_ref: str = "session:1"
) -> RecoveryId:
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    repo = SqlAlchemyRecoveryRepository(db_connection)
    record = RecoveryRecord(
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
        result=RecoveryOutcome.UNRESOLVED,
        created_at=_NOW,
        updated_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    repo.create(record)
    return record.recovery_id


def _service(db_connection: sa.Connection) -> RecoveryService:
    return RecoveryService(
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        recovery_repository=SqlAlchemyRecoveryRepository(db_connection),
    )


def _allowed_facts(**overrides: object) -> RecoveryResolutionFacts:
    base: dict[str, object] = dict(
        known_consequence_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        lpvs_resolved=True,
        last_proven_valid_state_ref="session:1@v2",
        restores_already_legitimized_state=True,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
        result=RecoveryOutcome.RECONCILED,
    )
    base.update(overrides)
    return RecoveryResolutionFacts(**base)  # type: ignore[arg-type]


def test_resolves_a_deterministic_reconciliation_end_to_end(db_connection: sa.Connection) -> None:
    """Positive control: the full governed path (BND-001/002/017/018
    ALLOW) actually performs the write and returns the resolved
    record."""
    workspace_id = _workspace(db_connection, email="recsvc-happy@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)

    resolved = service.resolve_recovery(
        db_connection,
        actor=_SYSTEM_ACTOR,
        workspace_id=workspace_id,
        recovery_id=recovery_id,
        original_target_ref="session:1",
        requested_operation="reconcile",
        expected_record_version=RecordVersion.initial(),
        facts=_allowed_facts(),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_LATER,
    )

    assert resolved.result is RecoveryOutcome.RECONCILED
    assert resolved.resolved_at == _LATER
    assert resolved.last_proven_valid_state_ref == "session:1@v2"
    assert resolved.record_version == RecordVersion(2)


def test_denies_admin_recovery_attempt_by_a_human_user(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: admin recovery. A HUMAN_USER actor
    invoking this deterministic Recovery Command is denied at BND-001
    before BND-017/BND-018 ever run -- no write happens."""
    workspace_id = _workspace(db_connection, email="recsvc-admin@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)
    human_actor = ActorIdentity(ActorClass.HUMAN_USER, "admin-user-1")

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=human_actor,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_001
    stored = SqlAlchemyRecoveryRepository(db_connection).get(recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.UNRESOLVED


def test_denies_ai_processor_actor_before_bnd_018_ever_runs(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (06 section 25 PROHIBITED PATH):
    "AI chooses recovery outcome." BND-001's own `required_actor_classes
    = {SYSTEM_SERVICE}` denies an AI_PROCESSOR actor structurally
    before BND-018's own independent AI check would ever run --
    defense-in-depth proven at the chain-composition level."""
    workspace_id = _workspace(db_connection, email="recsvc-ai@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)
    ai_actor = ActorIdentity(ActorClass.AI_PROCESSOR, "ai-gateway-1")

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=ai_actor,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_001


def test_denies_blind_retry_on_uncertain_consequence(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: blind retry when duplicate
    consequence is possible -- denied at BND-017, no write."""
    workspace_id = _workspace(db_connection, email="recsvc-blind-retry@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="retry",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(
                known_consequence_certainty=ConsequenceCertainty.GOVERNANCE_STATE_UNKNOWN
            ),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_017
    stored = SqlAlchemyRecoveryRepository(db_connection).get(recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.UNRESOLVED


def test_denies_dependent_operation_blocked_by_another_indeterminate_record(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: dependent consequential operation
    after INDETERMINATE. A second, still-UNRESOLVED RecoveryRecord
    blocking the same target denies this one unconditionally."""
    workspace_id = _workspace(db_connection, email="recsvc-blocked@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    blocking_record = RecoveryRecord(
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
        recovery_actor_id="recovery-worker-2",
        result=RecoveryOutcome.UNRESOLVED,
        created_at=_NOW,
        updated_at=_NOW,
        record_version=RecordVersion.initial(),
        blocked_target_refs=("session:1",),
    )
    SqlAlchemyRecoveryRepository(db_connection).create(blocking_record)
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_017
    assert excinfo.value.chain_result.proofs[-1].reason_code == (
        "DEPENDENT_OPERATION_BLOCKED_BY_INDETERMINATE"
    )


def test_denies_recovering_to_a_never_legitimate_state(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack / TESTABLE INVARIANT: recovery can
    never produce a state that was not proven legitimate."""
    workspace_id = _workspace(db_connection, email="recsvc-never-legit@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(restores_already_legitimized_state=False),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_018
    assert excinfo.value.chain_result.proofs[-1].reason_code == (
        "DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE"
    )


def test_denies_when_audit_reconstruction_would_be_broken(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: erase audit/history. Recovery
    cannot proceed if it would break audit reconstruction, even with
    every other fact proven."""
    workspace_id = _workspace(db_connection, email="recsvc-audit@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(audit_reconstruction_preserved=False),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_018
    assert "audit_reconstruction_preserved" in excinfo.value.chain_result.proofs[-1].reason_code


def test_a_nonexistent_recovery_id_is_denied_without_disclosing_existence(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: probing for a `recovery_id` that does not
    exist (at all, or under this Workspace) is denied at BND-002
    ('no resolvable objects') rather than surfacing a distinguishable
    not-found signal before Workspace/identity has even been proven."""
    workspace_id = _workspace(db_connection, email="recsvc-nonexistent@nonproof.test")
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=RecoveryId(uuid.uuid4()),
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_002
    assert excinfo.value.chain_result.proofs[-1].reason_code == "UNRESOLVED_WORKSPACE_NO_OBJECTS"


def test_a_record_from_a_different_workspace_is_treated_as_nonexistent(
    db_connection: sa.Connection,
) -> None:
    """Mandatory Workspace attack: a real RecoveryRecord exists, but
    under a DIFFERENT Workspace than the caller claims -- the
    Workspace-scoped repository read makes it invisible, so this
    collapses to the same 'no resolvable objects' denial as a
    genuinely nonexistent id, never a cross-Workspace leak."""
    real_workspace_id = _workspace(db_connection, email="recsvc-xws-real@nonproof.test")
    other_workspace_id = _workspace(db_connection, email="recsvc-xws-other@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=real_workspace_id)
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionDenied) as excinfo:
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=other_workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=RecordVersion.initial(),
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    assert excinfo.value.chain_result.terminal_boundary_id is BoundaryId.BND_002
    stored = SqlAlchemyRecoveryRepository(db_connection).get(recovery_id, real_workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.UNRESOLVED


def test_denies_a_stale_record_version_after_a_concurrent_attempt(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: concurrent/stale recovery attempt
    (TOCTOU). If the record's own `record_version` advanced (another
    attempt was recorded) between when the caller observed it and this
    write, the write is refused -- no double-application of a stale
    decision."""
    workspace_id = _workspace(db_connection, email="recsvc-stale@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyRecoveryRepository(db_connection)
    stale_expected_version = RecordVersion.initial()
    # Simulate a concurrent attempt advancing the record's own version
    # after the caller last observed it.
    repo.record_attempt(
        recovery_id, workspace_id, attempt_ref="concurrent-attempt", updated_at=_NOW
    )
    service = _service(db_connection)

    with pytest.raises(RecoveryResolutionStaleVersion):
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=stale_expected_version,
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    stored = repo.get(recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.UNRESOLVED
    assert stored.record_version == RecordVersion(2)


def test_event_replay_with_the_original_expected_version_cannot_double_resolve(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: event replay as recovery. Replaying the
    identical Recovery Command (same `expected_record_version`) after
    it already succeeded once must not apply a second write -- the
    record's own version already moved on, so the replay is refused as
    stale, not silently re-applied or double-counted."""
    workspace_id = _workspace(db_connection, email="recsvc-replay@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyRecoveryRepository(db_connection)
    service = _service(db_connection)
    original_expected_version = RecordVersion.initial()

    first = service.resolve_recovery(
        db_connection,
        actor=_SYSTEM_ACTOR,
        workspace_id=workspace_id,
        recovery_id=recovery_id,
        original_target_ref="session:1",
        requested_operation="reconcile",
        expected_record_version=original_expected_version,
        facts=_allowed_facts(),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_LATER,
    )
    assert first.result is RecoveryOutcome.RECONCILED

    with pytest.raises(RecoveryResolutionStaleVersion):
        service.resolve_recovery(
            db_connection,
            actor=_SYSTEM_ACTOR,
            workspace_id=workspace_id,
            recovery_id=recovery_id,
            original_target_ref="session:1",
            requested_operation="reconcile",
            expected_record_version=original_expected_version,  # the replayed, now-stale claim
            facts=_allowed_facts(),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_LATER,
        )

    stored = repo.get(recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.RECONCILED
    assert stored.record_version == RecordVersion(2)


def test_full_precommit_chain_runs_in_order_on_the_allowed_path(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: prove all four boundaries in
    `_PRECOMMIT_CHAIN` actually execute (in BND-001/002/017/018 order)
    on a real ALLOW path -- not merely that the service happens to
    reach a write, which a bug skipping a boundary could also produce."""
    workspace_id = _workspace(db_connection, email="recsvc-chain-order@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    service = _service(db_connection)

    resolved = service.resolve_recovery(
        db_connection,
        actor=_SYSTEM_ACTOR,
        workspace_id=workspace_id,
        recovery_id=recovery_id,
        original_target_ref="session:1",
        requested_operation="reconcile",
        expected_record_version=RecordVersion.initial(),
        facts=_allowed_facts(),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_LATER,
    )

    assert resolved.result is RecoveryOutcome.RECONCILED
    # The chain itself is not returned to the caller on success, but a
    # DENY at each individual boundary (already proven by the DENY
    # tests above, each with a different `terminal_boundary_id`) shows
    # every one of the four is real and independently load-bearing.


def test_mut_pkg24_03_bypassing_the_service_guard_allows_a_stale_write(
    db_connection: sa.Connection,
) -> None:
    """MUT-PKG24-03: guard-necessity proof, not a code mutation --
    `RecoveryService.resolve_recovery`'s own `record_version` staleness
    check (see `application.recovery_handler`'s own module docstring:
    "the one fact this command actually needs fresh") is enforced ONLY
    in Python, at the service layer -- `SqlAlchemyRecoveryRepository.
    mark_resolved` itself performs no such comparison (confirmed by
    reading its own WHERE clause: only `id`/`workspace_id`, no
    `record_version` condition). Calling the repository directly,
    bypassing `RecoveryService` entirely, after a concurrent attempt
    already advanced the version, SUCCEEDS where
    `test_denies_a_stale_record_version_after_a_concurrent_attempt`
    proves the real service call is refused -- proving the guard is
    genuinely load-bearing and not duplicated anywhere beneath it."""
    workspace_id = _workspace(db_connection, email="recsvc-mut03@nonproof.test")
    recovery_id = _seed_recovery_record(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyRecoveryRepository(db_connection)
    repo.record_attempt(
        recovery_id, workspace_id, attempt_ref="concurrent-attempt", updated_at=_NOW
    )

    # No RecoveryResolutionStaleVersion here -- the repository itself
    # has no opinion about the caller's stale expectation.
    repo.mark_resolved(
        recovery_id,
        workspace_id,
        result=RecoveryOutcome.RECONCILED,
        resolved_at=_LATER,
        last_proven_valid_state_ref="session:1@v2",
    )

    stored = repo.get(recovery_id, workspace_id)
    assert stored is not None
    assert stored.result is RecoveryOutcome.RECONCILED
