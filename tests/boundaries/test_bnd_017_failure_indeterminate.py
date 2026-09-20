"""T4 BOUNDARY TEST: BND-017 Failure / Indeterminate Boundary, against
real PostgreSQL, wrapping the real
`persistence.recovery_repository.SqlAlchemyRecoveryRepository` (PKG-23/
PKG-24) -- the same "real repository, not a fake" discipline
`test_bnd_002_workspace.py`/`test_bnd_013_evidence.py` already
establish, since this evaluator's own DENY branch depends on a fresh
`is_target_blocked` read (06 section 24's own DENY: "dependent
consequential operation after INDETERMINATE").
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_017_failure_indeterminate import (
    Bnd017FailureIndeterminateEvaluator,
    Bnd017Input,
)
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.recovery_repository import SqlAlchemyRecoveryRepository
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
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _bootstrap(db_connection: sa.Connection, *, email: str) -> tuple[WorkspaceId, ActorIdentity]:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id)


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_TEST_DEPENDENT_OPERATION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


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


def _seed_blocking_recovery_record(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, target_ref: str
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
        blocked_target_refs=(target_ref,),
    )
    repo.create(record)
    return record.recovery_id


def _input(
    *,
    context: BoundaryContext,
    requested_operation: str,
    known_consequence_certainty: ConsequenceCertainty,
    target_ref: str,
    exclude_recovery_id: RecoveryId | None = None,
) -> Bnd017Input:
    return Bnd017Input(
        boundary_id=BoundaryId.BND_017,
        context=context,
        requested_operation=requested_operation,
        known_consequence_certainty=known_consequence_certainty,
        target_ref=target_ref,
        exclude_recovery_id=exclude_recovery_id,
    )


def test_denies_dependent_operation_while_target_is_blocked(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (06 section 24's own DENY line):
    a dependent consequential operation is denied unconditionally
    while ANY unresolved RecoveryRecord names its target as blocked --
    regardless of what certainty or operation the caller claims."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-blocked@nonproof.test")
    _seed_blocking_recovery_record(db_connection, workspace_id=workspace_id, target_ref="session:1")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="acknowledge_committed",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_COMMITTED,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DEPENDENT_OPERATION_BLOCKED_BY_INDETERMINATE"


def test_unblocked_target_is_not_affected_by_an_unrelated_blocked_record(
    db_connection: sa.Connection,
) -> None:
    """Positive control: blocking is per-target, not workspace-wide."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-unrelated@nonproof.test")
    _seed_blocking_recovery_record(db_connection, workspace_id=workspace_id, target_ref="session:1")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="retry",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
        target_ref="session:999",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "SAFE_RETRY_AFTER_PROVEN_NON_COMMIT"


def test_a_recovery_record_excludes_itself_from_its_own_blocking_check(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: the recovery currently being resolved must
    not be blocked by its own row -- proves `exclude_recovery_id`
    actually reaches the repository read, not just documented intent."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-self-exclude@nonproof.test")
    recovery_id = _seed_blocking_recovery_record(
        db_connection, workspace_id=workspace_id, target_ref="session:1"
    )
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="reconcile",
        known_consequence_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        target_ref="session:1",
        exclude_recovery_id=recovery_id,
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "RECONCILIATION_PERMITTED_FOR_UNCERTAIN_CONSEQUENCE"


def test_proven_committed_allows_only_acknowledge(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-committed-ack@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="acknowledge_committed",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_COMMITTED,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "COMMITTED_CONSEQUENCE_ACKNOWLEDGED"


def test_proven_committed_denies_a_repeat_attempt(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (06 section 24 ALLOW line's own
    negative space): "known COMMITTED -> do not repeat consequence."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-committed-repeat@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="retry",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_COMMITTED,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "COMMITTED_CONSEQUENCE_MUST_NOT_REPEAT"


def test_proven_not_committed_allows_retry_and_reconcile(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-notcommit-retry@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))

    for op in ("retry", "continue_dependent_workflow", "reconcile"):
        boundary_input = _input(
            context=context,
            requested_operation=op,
            known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
            target_ref="session:1",
        )
        proof = evaluator.evaluate(boundary_input, context)
        assert proof.result is BoundaryResult.ALLOW, op
        assert proof.reason_code == "SAFE_RETRY_AFTER_PROVEN_NON_COMMIT", op


def test_proven_not_committed_requires_a_fresh_chain_for_anything_else(
    db_connection: sa.Connection,
) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-notcommit-other@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="assume_commit",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.REQUIRE
    assert proof.reason_code == "FRESH_BOUNDARY_CHAIN_REQUIRED"


def test_uncertain_consequence_denies_assumption_operations(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (06 section 24 DENY): "assume
    rollback without proof; assume commit without proof."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-uncertain-assume@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))

    for op, certainty in (
        ("assume_commit", ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN),
        ("assume_rollback", ConsequenceCertainty.CANONICAL_STATE_UNKNOWN),
    ):
        boundary_input = _input(
            context=context,
            requested_operation=op,
            known_consequence_certainty=certainty,
            target_ref="session:1",
        )
        proof = evaluator.evaluate(boundary_input, context)
        assert proof.result is BoundaryResult.DENY, op
        assert proof.reason_code == f"CANNOT_ASSUME_OUTCOME_WITHOUT_PROOF:{op}"


def test_uncertain_consequence_denies_blind_retry(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack (06 section 24 DENY): "blind retry
    when duplicate consequence is possible."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-uncertain-retry@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="retry",
        known_consequence_certainty=ConsequenceCertainty.GOVERNANCE_STATE_UNKNOWN,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "BLIND_RETRY_ON_UNCERTAIN_CONSEQUENCE"


def test_uncertain_consequence_allows_reconciliation(db_connection: sa.Connection) -> None:
    """06 section 24 REQUIRE: "Recovery/reconciliation for
    INDETERMINATE" -- requesting reconciliation is itself the fresh
    re-evaluation that satisfies the REQUIRE."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-uncert-reconcile@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="reconcile",
        known_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "RECONCILIATION_PERMITTED_FOR_UNCERTAIN_CONSEQUENCE"


def test_uncertain_consequence_requires_reconciliation_for_unrecognized_operations(
    db_connection: sa.Connection,
) -> None:
    """Fail-closed default: an unrecognized `requested_operation` is
    never guessed into an ALLOW -- 06 section 24's own "Examples:"
    (not "defines") language for this field."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-uncertain-unknown@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="emit_compensating_mutation",
        known_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.REQUIRE
    assert proof.reason_code == "RECONCILIATION_REQUIRED_FOR_INDETERMINATE"


def test_denies_construction_with_the_wrong_boundary_id(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-wrong-id@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)

    try:
        Bnd017Input(
            boundary_id=BoundaryId.BND_018,  # wrong boundary
            context=context,
            requested_operation="retry",
            known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
            target_ref="session:1",
        )
    except ValueError as exc:
        assert "BND_017" in str(exc)
    else:
        raise AssertionError("expected ValueError for a mismatched boundary_id")


def test_denies_an_empty_requested_operation(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-empty-op@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)

    try:
        Bnd017Input(
            boundary_id=BoundaryId.BND_017,
            context=context,
            requested_operation="",
            known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
            target_ref="session:1",
        )
    except ValueError as exc:
        assert "requested_operation" in str(exc)
    else:
        raise AssertionError("expected ValueError for an empty requested_operation")


def test_denies_an_empty_target_ref(db_connection: sa.Connection) -> None:
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-empty-target@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)

    try:
        Bnd017Input(
            boundary_id=BoundaryId.BND_017,
            context=context,
            requested_operation="retry",
            known_consequence_certainty=ConsequenceCertainty.PROVEN_NOT_COMMITTED,
            target_ref="",
        )
    except ValueError as exc:
        assert "target_ref" in str(exc)
    else:
        raise AssertionError("expected ValueError for an empty target_ref")


def test_registers_cleanly_in_the_boundary_registry(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: prove BND-017 composes with the generic
    chain evaluator exactly like every other boundary -- no special-
    casing required."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-chain@nonproof.test")
    context = _context(workspace_id=workspace_id, actor=actor)
    evaluator = Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository(db_connection))
    boundary_input = _input(
        context=context,
        requested_operation="reconcile",
        known_consequence_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        target_ref="session:1",
    )
    registry = BoundaryRegistry()
    registry.register(evaluator)

    chain_result = evaluate_chain(
        registry, [BoundaryId.BND_017], {BoundaryId.BND_017: boundary_input}, context
    )

    assert chain_result.is_allowed
    assert (
        chain_result.proofs[0].reason_code == "RECONCILIATION_PERMITTED_FOR_UNCERTAIN_CONSEQUENCE"
    )


# ---------------------------------------------------------------------------
# MUT-PKG24-01: mutation proof for the blocking check (test-only mutant --
# never edits the shipped `boundaries.bnd_017_failure_indeterminate` module;
# same "duplicate-and-mutate" discipline as PKG-21's own
# tests/command_commit_event/mutation/test_projection_mutations.py, adapted
# here as a fact-source mutant rather than a source-edit mutant since the
# real invariant under test depends entirely on the repository's own
# `is_target_blocked` answer, not on any other internal evaluator state).
# ---------------------------------------------------------------------------


class _AlwaysUnblockedRecoveryRepository:
    """MUTANT (test-only): wraps a REAL `SqlAlchemyRecoveryRepository`
    but always reports `is_target_blocked` as `False`, simulating the
    one scenario where BND-017's own blocking guard would have no
    effect. If `test_denies_dependent_operation_while_target_is_blocked`
    were vacuous (passing only because of how the test happens to seed
    data, not because the evaluator's own check is load-bearing), this
    mutant would still DENY. It does not: see
    `test_mut_pkg24_01_a_broken_blocking_guard_would_wrongly_allow`.
    """

    def __init__(self, real: SqlAlchemyRecoveryRepository) -> None:
        self._real = real

    def create(self, record: RecoveryRecord) -> None:
        self._real.create(record)

    def get(self, recovery_id: RecoveryId, workspace_id: WorkspaceId) -> RecoveryRecord | None:
        return self._real.get(recovery_id, workspace_id)

    def record_attempt(self, *args: object, **kwargs: object) -> None:
        self._real.record_attempt(*args, **kwargs)  # type: ignore[arg-type]

    def mark_resolved(self, *args: object, **kwargs: object) -> None:
        self._real.mark_resolved(*args, **kwargs)  # type: ignore[arg-type]

    def is_target_blocked(self, *args: object, **kwargs: object) -> bool:
        return False


def test_mut_pkg24_01_a_broken_blocking_guard_would_wrongly_allow(
    db_connection: sa.Connection,
) -> None:
    """MUT-PKG24-01: with the blocking guard neutered (mutant repository
    always answers `is_target_blocked=False`), the SAME scenario that
    `test_denies_dependent_operation_while_target_is_blocked` proves
    DENY for now wrongly ALLOWS -- proving that scenario's DENY comes
    genuinely from `Bnd017FailureIndeterminateEvaluator`'s own check,
    not from an unrelated cause."""
    workspace_id, actor = _bootstrap(db_connection, email="bnd017-mut01@nonproof.test")
    _seed_blocking_recovery_record(db_connection, workspace_id=workspace_id, target_ref="session:1")
    context = _context(workspace_id=workspace_id, actor=actor)
    mutant_repository = _AlwaysUnblockedRecoveryRepository(
        SqlAlchemyRecoveryRepository(db_connection)
    )
    evaluator = Bnd017FailureIndeterminateEvaluator(mutant_repository)  # type: ignore[arg-type]
    boundary_input = _input(
        context=context,
        requested_operation="acknowledge_committed",
        known_consequence_certainty=ConsequenceCertainty.PROVEN_COMMITTED,
        target_ref="session:1",
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "COMMITTED_CONSEQUENCE_ACKNOWLEDGED"
