"""F03 WU-03.4 (FBR-F03-3): a capture attempt is linked to its Burst, so an
unresolved capture can block completion.

TRN-BURST-005: "No capture write acknowledged to the user remains
unresolved." BND-008: "Capture uncertainty blocks Burst completion."

MUST BECOME TRUE: every Command persists the refs of the records it targets
(`commands.target_refs`, 09 §9); a capture Command for a Burst whose latest
attempt is IN_PROGRESS (no outcome) or INDETERMINATE is discoverable as an
unresolved capture for exactly that Burst.

MUST REMAIN IMPOSSIBLE: an unresolved capture that is invisible to the Burst it
targets (no persisted link); a COMMITTED / FAILED_PRECOMMIT / DENIED capture
counted as unresolved; an unresolved capture of ANOTHER Burst or another
Command type counted; an INDETERMINATE capture whose recovery record was
resolved counted (recovery is the architecture's own resolution path, 10 §64).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope, CommandOutcome
from persistence.burst_repository import burst_target_ref
from persistence.recovery_repository import SqlAlchemyRecoveryRepository
from recovery.certainty import ConsequenceCertainty
from recovery.failure_classifier import FailureClass
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord
from semantic_types.ids import (
    AttemptId,
    BurstId,
    CommandId,
    CorrelationId,
    RecoveryId,
    UserId,
)
from semantic_types.versions import ContractVersion, RecordVersion

CAPTURE = "CMD_CAPTURE_BURST_QUESTION"


def _record_capture_attempt(
    db: sa.Connection,
    ctx: dict,  # type: ignore[type-arg]
    actor: UserId,
    *,
    burst: BurstId | None = None,
    command_type: str = CAPTURE,
    outcome: CommandOutcome | None = None,
    command_id: CommandId | None = None,
) -> tuple[CommandId, AttemptId]:
    p = f02.ports(db)
    target = burst or ctx["burst"]
    command_id = command_id or CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    ref = burst_target_ref(target)
    p.commands.record_attempt(
        CommandEnvelope(
            command_id=command_id,
            command_type=command_type,
            command_contract_version=ContractVersion("1.0"),
            attempt_id=attempt_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            requested_at=f02.NOW,
            requesting_actor_type="HUMAN_USER",
            requesting_actor_id=str(actor.value),
            workspace_scope_ref=ctx["ws"],
            target_refs=(ref,),
            expected_versions={ref: RecordVersion(2)},
            created_refs=(f"question:{uuid.uuid4()}",),
            payload=_Payload(str(command_id.value)),
        ),
        received_at=f02.NOW,
    )
    if outcome is not None:
        p.commands.record_outcome(
            attempt_id=attempt_id,
            workspace_id=ctx["ws"],
            outcome=outcome,
            completed_at=f02.NOW,
        )
    return command_id, attempt_id


@dataclass(frozen=True, slots=True)
class _Payload:
    value: str


def _unresolved(db: sa.Connection, ctx: dict, burst: BurstId | None = None):  # type: ignore[no-untyped-def,type-arg]
    return f02.ports(db).commands.list_unresolved_for_target(
        workspace_id=ctx["ws"],
        command_type=CAPTURE,
        target_ref=burst_target_ref(burst or ctx["burst"]),
    )


def test_command_persists_its_target_refs(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    actor = ctx["participants"][0]
    command_id, _ = _record_capture_attempt(db_connection, ctx, actor)
    record = f02.ports(db_connection).commands.get_command(command_id)
    assert record is not None
    assert record.target_refs == (burst_target_ref(ctx["burst"]),)


def test_in_progress_capture_is_unresolved_for_its_burst(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    command_id, _ = _record_capture_attempt(db_connection, ctx, ctx["participants"][0])
    assert _unresolved(db_connection, ctx) == (command_id,)


def test_indeterminate_capture_is_unresolved_for_its_burst(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    command_id, _ = _record_capture_attempt(
        db_connection, ctx, ctx["participants"][0], outcome=CommandOutcome.INDETERMINATE
    )
    assert _unresolved(db_connection, ctx) == (command_id,)


def test_terminal_captures_are_not_unresolved(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    actor = ctx["participants"][0]
    for outcome in (CommandOutcome.DENIED, CommandOutcome.FAILED_PRECOMMIT):
        _record_capture_attempt(db_connection, ctx, actor, outcome=outcome)
    assert _unresolved(db_connection, ctx) == ()


def test_other_burst_and_other_command_type_are_not_counted(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    actor = ctx["participants"][0]
    other_burst = BurstId(uuid.uuid4())
    _record_capture_attempt(
        db_connection, ctx, actor, command_type="CMD_SOMETHING_ELSE", outcome=None
    )
    assert _unresolved(db_connection, ctx) == ()
    assert _unresolved(db_connection, ctx, burst=other_burst) == ()


def test_recovery_resolved_indeterminate_capture_is_not_unresolved(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    command_id, attempt_id = _record_capture_attempt(
        db_connection, ctx, ctx["participants"][0], outcome=CommandOutcome.INDETERMINATE
    )
    recovery = SqlAlchemyRecoveryRepository(db_connection)
    record = RecoveryRecord(
        recovery_id=RecoveryId(uuid.uuid4()),
        workspace_scope_ref=ctx["ws"],
        failure_correlation_ref=CorrelationId(uuid.uuid4()),
        original_command_id=command_id,
        original_attempt_id=attempt_id,
        failure_classifications=(FailureClass.F_PERS,),
        canonical_state_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        external_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        recovery_actor_type="SYSTEM_SERVICE",
        recovery_actor_id="recovery-worker-1",
        result=RecoveryOutcome.UNRESOLVED,
        created_at=f02.NOW,
        updated_at=f02.NOW,
        record_version=RecordVersion.initial(),
    )
    recovery.create(record)
    assert _unresolved(db_connection, ctx) == (command_id,)  # UNRESOLVED recovery still blocks
    recovery.mark_resolved(
        record.recovery_id,
        ctx["ws"],
        result=RecoveryOutcome.RECONCILED,
        resolved_at=f02.NOW,
        last_proven_valid_state_ref=None,
    )
    assert _unresolved(db_connection, ctx) == ()


# --------------------------------------------------------------------------- FBR-F03-7
# Discovered while repairing FBR-F03-3: a BND-014 DENY at the effect gate left
# the attempt with no outcome (IN_PROGRESS forever). Once attempts are linked to
# their Burst, that would make a merely STALE or de-authorized capture block the
# Burst's completion forever.


def test_bnd014_denial_resolves_the_attempt_and_the_idempotency_record(
    db_connection: sa.Connection,
) -> None:
    from authority.actor import ActorClass, ActorIdentity
    from boundaries.authority_source import BindingAuthority
    from boundaries.types import BoundaryResult
    from commit.coordinator import CommitCoordinator, CommitDenied, MutationOutcome
    from commit.idempotency import IdempotencyOutcome
    from governance.authority_binding import AuthorityClass
    from semantic_types.ids import CommitId

    ctx = f03.generating_context(db_connection, participants=1)
    actor: UserId = ctx["participants"][0]  # holds no SESSION_CONTROL_RIGHT
    p = f02.ports(db_connection)
    command_id = CommandId(uuid.uuid4())
    key = str(command_id.value)
    ref = burst_target_ref(ctx["burst"])
    envelope = CommandEnvelope(
        command_id=command_id,
        command_type="CMD_TEST_DENIED_AT_GATE",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        requested_at=f02.NOW,
        requesting_actor_type="HUMAN_USER",
        requesting_actor_id=str(actor.value),
        workspace_scope_ref=ctx["ws"],
        target_refs=(ref,),
        expected_versions={ref: f03.burst_of(db_connection, ctx).record_version},
        payload=_Payload("x"),
        idempotency_key=key,
    )
    p.commands.record_attempt(envelope, received_at=f02.NOW)
    p.idempotency.begin(envelope, seen_at=f02.NOW)

    class _NeverApplied:
        def apply(self) -> MutationOutcome:  # pragma: no cover -- must not run
            raise AssertionError("a denied commit must not mutate")

    class _Reader:
        def read(self, target_ref: str):  # noqa: ANN202
            return f03.burst_of(db_connection, ctx).record_version

    with pytest.raises(CommitDenied):
        CommitCoordinator(
            db_connection,
            bnd014_evaluator=p.bnd014(),
            command_repository=p.commands,
            audit_repository=p.audit,
            outbox_repository=p.outbox,
            commit_repository=p.commits,
            idempotency_port=p.idempotency,
        ).commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, actor),
            authority=BindingAuthority(
                authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
                scope_type="SESSION",
                scope_id=ctx["session"].value,
            ),
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_Reader(),
            mutation=_NeverApplied(),
            occurred_at=f02.NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    attempt = p.commands.get_attempt(envelope.attempt_id)
    assert attempt is not None and attempt.outcome is CommandOutcome.DENIED
    record = p.idempotency.get(
        workspace_id=ctx["ws"], command_type="CMD_TEST_DENIED_AT_GATE", idempotency_key=key
    )
    assert record is not None and record.outcome is IdempotencyOutcome.FAILED_PRECOMMIT
    assert (
        p.commands.list_unresolved_for_target(
            workspace_id=ctx["ws"], command_type="CMD_TEST_DENIED_AT_GATE", target_ref=ref
        )
        == ()
    )
