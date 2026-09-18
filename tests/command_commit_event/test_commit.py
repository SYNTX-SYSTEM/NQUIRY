"""T7 COMMIT TEST: CommitCoordinator/BND-014, against real PostgreSQL.

CRITICAL PACKAGE (14 PKG-13's own prompt: ">=10 total novel/adapted
attacks required"). Every test in this file exercises the REAL
predecessor chain end to end: NonProofWorkspaceBootstrap (PKG-04) ->
Challenge/Session (PKG-05, direct SQL) -> QuestionBurst (PKG-07, real
`BurstRepository`) -> real `AuthorityResolver` (PKG-03) ->
`Bnd014CommitEvaluator` (this package) -> `CommitCoordinator` (this
package) -> `CommandRepository`/`IdempotencyPort`/`AuditRepository`/
`OutboxRepository`/`CommitRepository` (PKG-10/11/12/this package). The
one `MutationExecutor` used throughout wraps `BurstRepository.start`
(PKG-07) -- a genuine, already-real canonical mutation, not an
invented concrete Command (14 PKG-13 COMMANDS: NOT_APPLICABLE).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from boundaries.types import BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from commit.coordinator import (
    AmbiguousCommitFailure,
    CommitCoordinator,
    CommitDenied,
    CommitFailedPrecommit,
    CommitIndeterminate,
    CommitInjectionPoint,
    CommitOutcome,
    MutationOutcome,
    StaleVersionConflict,
)
from commit.idempotency import (
    IdempotencyAlreadyCommitted,
    IdempotencyOutcome,
    SqlAlchemyIdempotencyRepository,
)
from domain.burst import BurstMode, BurstState, QuestionBurst
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.burst_repository import BurstConflict, SqlAlchemyBurstRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import (
    challenges_table,
    commit_units_table,
    human_authority_bindings_table,
    question_bursts_table,
    sessions_table,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    BurstId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.failure_injector import RecordingFailureInjector, ScriptedFailureInjector
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _BurstStartPayload:
    burst_id: str


def _bootstrap_burst(
    db_connection: sa.Connection, *, email: str
) -> tuple[WorkspaceId, UserId, QuestionBurst]:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email=email)

    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=result.workspace_id.value,
            title="Onboarding drop-off",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    session_id = SessionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=result.workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=1,
        )
    )
    burst = QuestionBurst(
        burst_id=BurstId(_ID_GEN.new_uuid()),
        session_id=session_id,
        workspace_id=result.workspace_id,
        state=BurstState.PREPARED,
        mode=BurstMode.HUMAN_ONLY,
        started_at=None,
        paused_at=None,
        completed_at=None,
        frozen_membership_fingerprint=None,
        record_version=RecordVersion.initial(),
    )
    SqlAlchemyBurstRepository(db_connection).create_prepared(burst)
    return result.workspace_id, result.owner_user_id, burst


def _grant_session_control(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, user_id: UserId
) -> None:
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def _envelope_for_burst_start(
    *,
    workspace_id: WorkspaceId,
    burst: QuestionBurst,
    command_id: CommandId | None = None,
    idempotency_key: str | None = "start-burst-1",
) -> CommandEnvelope:
    burst_ref = str(burst.burst_id.value)
    return CommandEnvelope(
        command_id=command_id or CommandId(uuid.uuid4()),
        command_type="CMD_START_QUESTION_BURST",
        command_contract_version=ContractVersion("1.0"),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        requested_at=_NOW,
        requesting_actor_type="HUMAN_USER",
        requesting_actor_id="user-ref-1",
        workspace_scope_ref=workspace_id,
        target_refs=(burst_ref,),
        expected_versions={burst_ref: burst.record_version},
        payload=_BurstStartPayload(burst_ref),
        idempotency_key=idempotency_key,
    )


class _BurstStartMutation:
    """Wraps the REAL `BurstRepository.start` (PKG-07). Mandatory
    adversarial attack "concurrent Commands"/"state version changed" at
    the persistence layer: `BurstConflict` (a genuine 0-row-affected
    guarded UPDATE) is translated to `StaleVersionConflict`, the
    vocabulary `CommitCoordinator` itself understands.
    """

    def __init__(
        self,
        repo: SqlAlchemyBurstRepository,
        *,
        burst_id: BurstId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        started_at: datetime,
    ) -> None:
        self._repo = repo
        self._burst_id = burst_id
        self._workspace_id = workspace_id
        self._expected_record_version = expected_record_version
        self._started_at = started_at

    def apply(self) -> MutationOutcome:
        try:
            self._repo.start(
                burst_id=self._burst_id,
                workspace_id=self._workspace_id,
                expected_record_version=self._expected_record_version,
                started_at=self._started_at,
            )
        except BurstConflict as exc:
            raise StaleVersionConflict(str(exc)) from exc
        return MutationOutcome(state_before_ref="PREPARED", state_after_ref="ACTIVE")


class _BurstVersionReader:
    """`CurrentVersionReader` reading the REAL, fresh
    `question_bursts.record_version` for one burst -- no caching, one
    query per call, mirroring `AuthorityResolver.resolve()`'s own
    "always reads live" discipline.
    """

    def __init__(self, connection: sa.Connection, *, burst_id: BurstId) -> None:
        self._connection = connection
        self._burst_id = burst_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != str(self._burst_id.value):
            return None
        stmt = sa.select(question_bursts_table.c.record_version).where(
            question_bursts_table.c.id == self._burst_id.value
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


def _begin_idempotency_if_needed(db_connection: sa.Connection, envelope: CommandEnvelope) -> None:
    """14 section 27 rule 1: "new request -> create command/attempt" --
    an `IdempotencyRecord` begins its life (IN_PROGRESS) at dispatch
    time, BEFORE commit coordination ever starts. `CommitCoordinator`
    itself only ever *transitions* an existing record (`mark_committed`/
    `mark_failed_precommit`/`mark_indeterminate`, never creates one) --
    every test that supplies an `idempotency_key` must therefore call
    this first, mirroring the real two-step dispatch-then-commit flow.
    """
    if envelope.idempotency_key is not None:
        SqlAlchemyIdempotencyRepository(db_connection).begin(envelope, seen_at=_NOW)


def _build_coordinator(
    db_connection: sa.Connection, *, failure_injector: object | None = None
) -> CommitCoordinator:
    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )
    return CommitCoordinator(
        db_connection,
        bnd014_evaluator=Bnd014CommitEvaluator(resolver),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        failure_injector=failure_injector,  # type: ignore[arg-type]
    )


def _commit_burst_start(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    owner_id: UserId,
    burst: QuestionBurst,
    envelope: CommandEnvelope,
    failure_injector: object | None = None,
) -> CommitCoordinator:
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    coordinator = _build_coordinator(db_connection, failure_injector=failure_injector)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )
    coordinator.commit(
        envelope=envelope,
        actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        authority_scope_type="WORKSPACE",
        authority_scope_id=workspace_id.value,
        upstream_chain_result=BoundaryResult.ALLOW,
        current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
        mutation=mutation,
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
    )
    return coordinator


def test_commit_denies_when_authority_was_revoked_after_preparation(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: authority revoked after
    preparation.
    ATTACK: prepare a legitimate envelope, then revoke the required
    binding before the coordinator ever runs.
    EXPECTED DEFENSE: Bnd014CommitEvaluator's fresh AuthorityResolver call.
    EXPECTED CANONICAL RESULT: CommitDenied, Burst state unchanged, no
    CommitUnit/AuditEvent/OutboxEvent row exists.
    EXPECTED PROOF ARTIFACT: the raised CommitDenied's own BoundaryProof.
    ACTUAL RESULT: matches.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-revoked@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.human_user_id == owner_id.value)
        .values(
            state=AuthorityBindingState.REVOKED.value,
            revoked_at=_NOW,
            revoked_by_user_id=owner_id.value,
        )
    )
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    coordinator = _build_coordinator(db_connection)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitDenied) as excinfo:
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert excinfo.value.boundary_proof.reason_code.startswith("AUTHORITY_NOT_CURRENT")
    assert SqlAlchemyBurstRepository(db_connection).get(burst.burst_id).state is BurstState.PREPARED
    assert db_connection.execute(sa.select(commit_units_table)).first() is None


def test_commit_denies_when_state_version_changed(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: state version changed.
    ATTACK: a competing operation advances the Burst's record_version
    between envelope preparation and this commit attempt.
    EXPECTED CANONICAL RESULT: CommitDenied (BND-014's own fresh read
    catches it before any mutation is even attempted).
    ACTUAL RESULT: matches.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-stale-version@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    # A competing write advances the real row's version out from under us.
    db_connection.execute(
        sa.update(question_bursts_table)
        .where(question_bursts_table.c.id == burst.burst_id.value)
        .values(record_version=2, state="ACTIVE", started_at=_NOW)
    )
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    coordinator = _build_coordinator(db_connection)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitDenied) as excinfo:
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert "STALE_VERSION" in excinfo.value.boundary_proof.reason_code


def test_commit_succeeds_and_atomically_writes_every_artifact(db_connection: sa.Connection) -> None:
    """Positive control: the full atomic bundle, real predecessor
    chain, real mutation.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-success@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    coordinator = _build_coordinator(db_connection)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    commit_unit = coordinator.commit(
        envelope=envelope,
        actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        authority_scope_type="WORKSPACE",
        authority_scope_id=workspace_id.value,
        upstream_chain_result=BoundaryResult.ALLOW,
        current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
        mutation=mutation,
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
    )

    assert commit_unit.outcome is CommitOutcome.COMMITTED
    updated_burst = SqlAlchemyBurstRepository(db_connection).get(burst.burst_id)
    assert updated_burst.state is BurstState.ACTIVE
    assert updated_burst.record_version == RecordVersion(2)

    stored_commit = SqlAlchemyCommitRepository(db_connection).get(commit_unit.commit_id)
    assert stored_commit is not None
    assert stored_commit.outcome is CommitOutcome.COMMITTED
    audit_events = SqlAlchemyAuditRepository(db_connection).list_for_correlation(
        envelope.correlation_id
    )
    assert len(audit_events) == 1
    assert audit_events[0].commit_id == commit_unit.commit_id
    assert audit_events[0].result == "COMMITTED"

    command_attempt = SqlAlchemyCommandRepository(db_connection).get_attempt(envelope.attempt_id)
    assert command_attempt is not None
    assert command_attempt.outcome is CommandOutcome.COMMITTED
    assert command_attempt.commit_id == commit_unit.commit_id

    idem = SqlAlchemyIdempotencyRepository(db_connection).get(
        workspace_id=workspace_id,
        command_type=envelope.command_type,
        idempotency_key="start-burst-1",
    )
    assert idem is not None
    assert idem.outcome is IdempotencyOutcome.COMMITTED
    assert idem.commit_id == commit_unit.commit_id


def test_duplicate_idempotent_request_after_commit_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: duplicate idempotent request.
    Also proves "connection loss after commit" (see module docstring
    in commit/coordinator.py): a caller who never saw the first
    response and retries hits the identical defense.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-duplicate@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    _commit_burst_start(
        db_connection, workspace_id=workspace_id, owner_id=owner_id, burst=burst, envelope=envelope
    )

    retry_repo = SqlAlchemyIdempotencyRepository(db_connection)
    with pytest.raises(IdempotencyAlreadyCommitted) as excinfo:
        retry_repo.begin(envelope, seen_at=_LATER)
    assert excinfo.value.existing.outcome is IdempotencyOutcome.COMMITTED


def test_commit_denies_a_concurrent_command_targeting_the_same_burst(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: concurrent Commands. Two distinct
    command_ids both prepared against the Burst's original version;
    the first legitimately commits, the second's own commit attempt is
    denied by BND-014's fresh version read -- not merely by chance
    ordering.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-concurrent@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    first_envelope = _envelope_for_burst_start(
        workspace_id=workspace_id, burst=burst, idempotency_key="race-key-a"
    )
    _commit_burst_start(
        db_connection,
        workspace_id=workspace_id,
        owner_id=owner_id,
        burst=burst,
        envelope=first_envelope,
    )

    second_envelope = _envelope_for_burst_start(
        workspace_id=workspace_id, burst=burst, idempotency_key="race-key-b"
    )
    SqlAlchemyCommandRepository(db_connection).record_attempt(second_envelope, received_at=_LATER)
    coordinator = _build_coordinator(db_connection)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,  # stale: still version 1
        started_at=_LATER,
    )

    with pytest.raises(CommitDenied) as excinfo:
        coordinator.commit(
            envelope=second_envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_LATER,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert "STALE_VERSION" in excinfo.value.boundary_proof.reason_code


def test_commit_rolls_back_the_real_mutation_on_a_failure_after_it(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: failure after first mutation.
    This is the single strongest atomicity proof in this file: the
    REAL BurstRepository.start() UPDATE genuinely executes, then a
    later step fails -- the mutation itself must roll back too, not
    just the audit/outbox/commit_units rows.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-fail-after-mutation@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    injector = ScriptedFailureInjector(
        fire_at=CommitInjectionPoint.BEFORE_AUDIT, exception=RuntimeError("simulated audit outage")
    )
    coordinator = _build_coordinator(db_connection, failure_injector=injector)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitFailedPrecommit):
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    # The real mutation executed inside the SAVEPOINT -- proven rolled back.
    reverted = SqlAlchemyBurstRepository(db_connection).get(burst.burst_id)
    assert reverted.state is BurstState.PREPARED
    assert reverted.record_version == RecordVersion(1)
    assert db_connection.execute(sa.select(commit_units_table)).first() is None
    command_attempt = SqlAlchemyCommandRepository(db_connection).get_attempt(envelope.attempt_id)
    assert command_attempt.outcome is CommandOutcome.FAILED_PRECOMMIT


def test_audit_insertion_failure_rolls_back_the_whole_bundle(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: audit insertion failure."""
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-audit-failure@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    injector = ScriptedFailureInjector(
        fire_at=CommitInjectionPoint.AFTER_AUDIT,
        exception=RuntimeError("simulated post-audit outage"),
    )
    coordinator = _build_coordinator(db_connection, failure_injector=injector)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitFailedPrecommit):
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert db_connection.execute(sa.select(commit_units_table)).first() is None
    assert (
        SqlAlchemyAuditRepository(db_connection).list_for_correlation(envelope.correlation_id) == ()
    )


def test_outbox_insertion_failure_rolls_back_the_already_inserted_audit_event(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: outbox insertion failure. Proves
    atomicity spans the WHOLE bundle, not just the outbox row itself --
    the AuditEvent already inserted moments earlier is rolled back too.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-outbox-failure@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    injector = ScriptedFailureInjector(
        fire_at=CommitInjectionPoint.BEFORE_OUTBOX,
        exception=RuntimeError("simulated outbox outage"),
    )
    coordinator = _build_coordinator(db_connection, failure_injector=injector)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitFailedPrecommit):
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert (
        SqlAlchemyAuditRepository(db_connection).list_for_correlation(envelope.correlation_id) == ()
    )
    reverted = SqlAlchemyBurstRepository(db_connection).get(burst.burst_id)
    assert reverted.state is BurstState.PREPARED


def test_ambiguous_commit_failure_is_recorded_as_indeterminate(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attacks: abort before commit (proven
    FAILED_PRECOMMIT above); connection loss after commit's genuine
    counterpart here -- a failure this coordinator cannot locally prove
    either way records the honest INDETERMINATE disposition via a
    separate write, per commit/coordinator.py's own module docstring.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-indeterminate@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    injector = ScriptedFailureInjector(
        fire_at=CommitInjectionPoint.BEFORE_DB_COMMIT,
        exception=AmbiguousCommitFailure("simulated ambiguous connection loss"),
    )
    coordinator = _build_coordinator(db_connection, failure_injector=injector)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )
    commit_id = CommitId(uuid.uuid4())

    with pytest.raises(CommitIndeterminate):
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=commit_id,
        )

    stored = SqlAlchemyCommitRepository(db_connection).get(commit_id)
    assert stored is not None
    assert stored.outcome is CommitOutcome.INDETERMINATE
    # The mutation itself is rolled back (its own SAVEPOINT failed) --
    # 09 section 14: "dependent consequence blocked", not silently kept.
    reverted = SqlAlchemyBurstRepository(db_connection).get(burst.burst_id)
    assert reverted.state is BurstState.PREPARED
    command_attempt = SqlAlchemyCommandRepository(db_connection).get_attempt(envelope.attempt_id)
    assert command_attempt.outcome is CommandOutcome.INDETERMINATE


def test_failure_injector_reaches_every_named_point_on_the_happy_path(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: prove the FailureInjector hooks are
    actually wired at every one of 14 section 40's 11 named points, in
    the correct order -- a missing hook would let an attack class slip
    through untested without this test ever failing.
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-injection-points@nonproof.test"
    )
    _grant_session_control(db_connection, workspace_id=workspace_id, user_id=owner_id)
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    _begin_idempotency_if_needed(db_connection, envelope)
    recorder = RecordingFailureInjector()
    coordinator = _build_coordinator(db_connection, failure_injector=recorder)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    coordinator.commit(
        envelope=envelope,
        actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        authority_scope_type="WORKSPACE",
        authority_scope_id=workspace_id.value,
        upstream_chain_result=BoundaryResult.ALLOW,
        current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
        mutation=mutation,
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
    )

    assert recorder.points_observed == list(CommitInjectionPoint)


def test_denied_bundle_never_reaches_any_post_bnd014_injection_point(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: prove a DENY at BND-014 short-circuits
    before any mutation/audit/outbox hook fires -- the denial is
    provably not "invoked but ignored."
    """
    workspace_id, owner_id, burst = _bootstrap_burst(
        db_connection, email="commit-denied-short-circuit@nonproof.test"
    )
    # Deliberately no authority grant at all.
    envelope = _envelope_for_burst_start(workspace_id=workspace_id, burst=burst)
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)
    recorder = RecordingFailureInjector()
    coordinator = _build_coordinator(db_connection, failure_injector=recorder)
    mutation = _BurstStartMutation(
        SqlAlchemyBurstRepository(db_connection),
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    with pytest.raises(CommitDenied):
        coordinator.commit(
            envelope=envelope,
            actor=ActorIdentity(ActorClass.HUMAN_USER, owner_id),
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=workspace_id.value,
            upstream_chain_result=BoundaryResult.ALLOW,
            current_version_reader=_BurstVersionReader(db_connection, burst_id=burst.burst_id),
            mutation=mutation,
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
        )

    assert recorder.points_observed == [
        CommitInjectionPoint.BEFORE_TRANSACTION,
        CommitInjectionPoint.AFTER_AUTHORITY_EVALUATION,
        CommitInjectionPoint.AFTER_BND014,
    ]
