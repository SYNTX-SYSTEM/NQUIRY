"""Session control Commands (F02 WU-02.7 / WU-02.8).

One semantic Command per architecture-defined transition. There is no
generic setter and no "advance" (09 §27.2, 12 §23, 19 §22):

- CMD_BEGIN_SETUP: TRN-SESS-002 / AUTH-DEP-SESS-002, Session DRAFT -> SETUP.
- CMD_BEGIN_CHALLENGE_CAPTURE: TRN-SESS-003 / AUTH-DEP-SESS-003,
  SETUP -> CHALLENGE_CAPTURE.
- CMD_PREPARE_BURST: TRN-BURST-001 / AUTH-DEP-BURST-001, QuestionBurst
  absent -> PREPARED (HUMAN_ONLY).
- CMD_ADMIT_SESSION_PARTICIPANT: 09 §28 / GAP-09-007 / HD-7,
  SessionParticipation created.
- CMD_OPEN_QUESTION_GENERATION: TRN-SESS-004 (+ coupled TRN-BURST-002) /
  AUTH-DEP-SESS-004, CHALLENGE_CAPTURE -> QUESTION_GENERATION AND Burst
  PREPARED -> ACTIVE as one bundle.

AUTHORITY (HD-1, 16 §41 REC-002): every Command here requires a current
`SESSION_CONTROL_RIGHT` binding at EXACTLY `SESSION:<session_id>`. It is
checked twice: in the precommit chain (BND-005) and again at commit (BND-014,
BINDING source). A Challenge-scoped or Workspace-scoped binding does not
satisfy it; there is no scope inheritance. No Workspace role is consulted.

BURST CONTROL (HD-9, 16 §41 REC-009 / NQ-DEC-037): Burst start (coupled into
TRN-SESS-004 here) and manual Burst completion are closed, for the current
prototype, by the same Session-scoped `SESSION_CONTROL_RIGHT`. This is an
explicit human PROTOTYPE NARROWING of 04 §36-39 / 05 §20 (Facilitator role +
ACTIVE Session FacilitatorScopeBinding), which remain the architecture's
broader model and stay OPEN for production (NQ-GAP-080). WU-02.7 had
classified this reading as derivable (Case 1). WU-02.12 corrects that: it
was a Case-3 authority relation, now closed by HD-9.

EXPECTED VERSION: every Command carries the caller's `expected_session_version`.
A mismatch with the fresh Session is STALE (`SessionVersionStale`) before any
boundary runs, because a stale view is not an authority denial. BND-014
re-checks the same version at commit to catch a race.

PRECONDITIONS that are neither authority nor version surface as
`SessionPreconditionUnmet` (BLOCKED):
- TRN-SESS-003 "method-required setup structurally present": the pinned
  `applied_method_key`/`applied_method_version` exist (12: one pinned method).
- TRN-BURST-001 "pre-generation state compatible with later start": Session in
  DRAFT/SETUP/CHALLENGE_CAPTURE, and no Burst yet for the Session.
- TRN-SESS-004: Burst PREPARED; Challenge context present (non-empty title);
  HD-8: at least one current SessionParticipation.
- HD-7 admission: target is an ACTIVE member (also DB-enforced) and not already
  a current participant.

COUPLED BUNDLE (TRN-SESS-004): "The Session and Burst state changes form one
logical transition bundle." Both version-checked targets are in one envelope.
Both writes run in ONE mutation inside the coordinator's SAVEPOINT, so neither
can commit without the other.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from authority.actor import ActorClass, ActorIdentity
from boundaries.authority_source import BindingAuthority
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.bnd_005_human_authority import Bnd005HumanAuthorityEvaluator, Bnd005Input
from boundaries.bnd_007_state_transition import Bnd007Input, Bnd007StateTransitionEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome, compute_payload_fingerprint
from commit.coordinator import (
    CommitCoordinator,
    CommitUnit,
    CurrentVersionReader,
    FailureInjectionPort,
    MutationOutcome,
    StaleVersionConflict,
)
from commit.idempotency import (
    IdempotencyDecision,
    decide_idempotency_action,
    raise_for_decision,
)
from domain.burst import BurstMode, BurstState, QuestionBurst
from domain.burst_transitions import BurstTransitionId, resolve_burst_transition
from domain.question_selection import session_target_ref
from domain.session import Session, SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from events.contracts import EventFacts
from governance.authority_binding import AuthorityClass
from persistence.burst_repository import (
    BurstConflict,
    SqlAlchemyBurstVersionReader,
    burst_target_ref,
)
from persistence.session_participation_repository import (
    SqlAlchemySessionParticipationRepository,
)
from persistence.session_repository import (
    SessionTransitionConflict,
    SqlAlchemySessionVersionReader,
)
from semantic_types.ids import (
    AttemptId,
    BurstId,
    CommandId,
    CommitId,
    CorrelationId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

from application.composition import GovernedPorts

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_003,
    BoundaryId.BND_005,
    BoundaryId.BND_007,
)
_PRE_GENERATION_STATES = frozenset(
    {SessionState.DRAFT, SessionState.SETUP, SessionState.CHALLENGE_CAPTURE}
)


class SessionNotFound(LookupError):
    pass


class SessionVersionStale(Exception):
    def __init__(self, *, expected: int, current: int, current_state: str) -> None:
        self.expected = expected
        self.current = current
        self.current_state = current_state
        super().__init__(f"STALE_VERSION: expected {expected}, current {current}")


class SessionCommandDenied(Exception):
    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        terminal = chain_result.proofs[-1] if chain_result.proofs else None
        self.reason_code = terminal.reason_code if terminal is not None else "DENIED"
        super().__init__(self.reason_code)


class IdempotentReplay(Exception):
    """The same logical Command (same idempotency key + command id) already
    COMMITTED. The caller returns the committed result (a fresh reread), never
    re-executes (14 §27 RETURN_COMMITTED_RESULT)."""

    def __init__(self, result_ref: str | None) -> None:
        self.result_ref = result_ref
        super().__init__("ALREADY_COMMITTED")


def _replay_guard(
    ports: GovernedPorts,
    workspace_id: WorkspaceId,
    command_type: str,
    ident: CommandIdentity,
    payload: object,
) -> None:
    """Applies the authoritative idempotency disposition (14 §27,
    `commit.idempotency.decide_idempotency_action`) BEFORE the
    expected-version comparison, because a replay of a committed transition
    would otherwise be misreported as STALE (the same reason
    `human_decision_handler._raise_if_already_committed` exists).

    F02 WU-02.12 (FBR-B): the disposition is the shared one, with the real
    payload fingerprint. A key already COMMITTED for a different payload
    (another expected version, participant or Session) is a collision and
    is rejected (`IdempotencyPayloadCollision`); it is never reported as a
    replay. IN_PROGRESS / INDETERMINATE records block without executing.
    """
    if ident.idempotency_key is None:
        return
    existing = ports.idempotency.get(
        workspace_id=workspace_id, command_type=command_type, idempotency_key=ident.idempotency_key
    )
    if existing is None:
        return
    decision = decide_idempotency_action(
        existing=existing,
        requested_command_id=ident.command_id,
        requested_payload_fingerprint=compute_payload_fingerprint(payload),
    )
    if decision is IdempotencyDecision.RETURN_COMMITTED_RESULT:
        raise IdempotentReplay(existing.result_ref)
    if decision is IdempotencyDecision.PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT:
        return
    raise_for_decision(decision, existing)


replay_guard = _replay_guard
"""Public name for the shared idempotency disposition (F03 reuses it)."""


class SessionPreconditionUnmet(Exception):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class SessionTransitionPayload:
    session_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class AdmitParticipantPayload:
    session_id: str
    participant_user_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class CommandIdentity:
    command_id: CommandId
    attempt_id: AttemptId
    correlation_id: CorrelationId
    commit_id: CommitId
    occurred_at: datetime
    idempotency_key: str | None = None

    @staticmethod
    def fresh(occurred_at: datetime, idempotency_key: str | None = None) -> CommandIdentity:
        return CommandIdentity(
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            occurred_at=occurred_at,
            idempotency_key=idempotency_key,
        )


class _FirstReader:
    """Combines per-target version readers (each answers only its own ref)."""

    def __init__(self, *readers: CurrentVersionReader) -> None:
        self._readers = readers

    def read(self, target_ref: str) -> RecordVersion | None:
        for reader in self._readers:
            value = reader.read(target_ref)
            if value is not None:
                return value
        return None


class _Mutation:
    def __init__(self, fn: Callable[[], MutationOutcome]) -> None:
        self._fn = fn

    def apply(self) -> MutationOutcome:
        try:
            return self._fn()
        except (SessionTransitionConflict, BurstConflict) as exc:
            raise StaleVersionConflict(str(exc)) from exc


# --- Pure precondition checks, shared with capability projections -----------
# (`application.inquiry_queries`). One definition, so the UI affordance can
# never disagree with what the Command enforces.


def prepare_burst_blocker(session: Session, existing_burst: QuestionBurst | None) -> str | None:
    if session.state not in _PRE_GENERATION_STATES:
        return f"SESSION_NOT_PRE_GENERATION:{session.state.value}"
    if existing_burst is not None:
        return f"BURST_ALREADY_EXISTS:{existing_burst.state.value}"
    return None


def open_question_generation_blocker(
    session: Session,
    burst: QuestionBurst | None,
    challenge_title: str | None,
    participant_count: int,
) -> str | None:
    if session.state is not SessionState.CHALLENGE_CAPTURE:
        return f"STATE_NOT_ELIGIBLE:{session.state.value}"
    if burst is None:
        return "BURST_ABSENT"
    if burst.state is not BurstState.PREPARED:
        return f"BURST_NOT_PREPARED:{burst.state.value}"
    if not resolve_burst_transition(
        current_state=burst.state, transition_id=BurstTransitionId.TRN_BURST_002
    ).is_state_eligible:
        return "BURST_START_NOT_ELIGIBLE"
    if not challenge_title or not challenge_title.strip():
        return "CHALLENGE_CONTEXT_INCOMPLETE"
    if participant_count < 1:
        return "NO_SESSION_PARTICIPANT"
    return None


def method_setup_blocker(session: Session) -> str | None:
    if not session.applied_method_key or not session.applied_method_version.value:
        return "METHOD_SETUP_MISSING"
    return None


def _raise_if(blocker: str | None) -> None:
    if blocker is not None:
        raise SessionPreconditionUnmet(blocker)


def _load_fresh(ports: GovernedPorts, session_id: SessionId, expected: int) -> Session:
    session = ports.sessions.get(session_id)
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected:
        raise SessionVersionStale(
            expected=expected,
            current=session.record_version.value,
            current_state=session.state.value,
        )
    return session


def _run(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session: Session | None,
    session_id: SessionId,
    command_type: str,
    payload: object,
    ident: CommandIdentity,
    resolution: object | None,
    target_refs: tuple[str, ...],
    expected_versions: dict[str, RecordVersion],
    created_refs: tuple[str, ...],
    reader: CurrentVersionReader,
    precondition: Callable[[], None] | None,
    mutation: Callable[[], MutationOutcome],
    failure_injector: FailureInjectionPort | None = None,
) -> CommitUnit:
    context = BoundaryContext(
        workspace_id=workspace_id,
        operation=command_type,
        actor=actor,
        correlation_id=ident.correlation_id,
        evaluated_at=ident.occurred_at,
    )
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
    registry.register(Bnd002WorkspaceEvaluator(ports.workspaces))  # type: ignore[arg-type]
    registry.register(Bnd003MembershipEvaluator(ports.memberships))  # type: ignore[arg-type]
    registry.register(Bnd005HumanAuthorityEvaluator(ports.resolver))  # type: ignore[arg-type]
    registry.register(Bnd007StateTransitionEvaluator())  # type: ignore[arg-type]

    inputs: dict[BoundaryId, object] = {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(session.workspace_id,) if session is not None else (),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
        BoundaryId.BND_005: Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="SESSION",
            scope_id=session_id.value,
        ),
    }
    chain: tuple[BoundaryId, ...] = _PRECOMMIT_CHAIN
    if resolution is not None:
        inputs[BoundaryId.BND_007] = Bnd007Input(
            boundary_id=BoundaryId.BND_007,
            context=context,
            resolution=resolution,  # type: ignore[arg-type]
        )
    else:
        chain = tuple(b for b in _PRECOMMIT_CHAIN if b is not BoundaryId.BND_007)

    # The workspace named by the caller must exist before a `commands` row can
    # reference it (fk_commands_workspace). An unknown/foreign Workspace is
    # denied by BND-002 without recording an attempt.
    workspace = ports.workspaces.get(workspace_id)
    if workspace is None or session is None:
        precheck = evaluate_chain(
            registry,
            (BoundaryId.BND_001, BoundaryId.BND_002),
            inputs,  # type: ignore[arg-type]
            context,
        )
        raise SessionCommandDenied(precheck)

    envelope = CommandEnvelope(
        command_id=ident.command_id,
        command_type=command_type,
        command_contract_version=ContractVersion("1.0"),
        attempt_id=ident.attempt_id,
        correlation_id=ident.correlation_id,
        requested_at=ident.occurred_at,
        requesting_actor_type=actor.actor_class.value,
        requesting_actor_id=str(actor.user_id.value),
        workspace_scope_ref=workspace_id,
        target_refs=target_refs,
        expected_versions=expected_versions,
        created_refs=created_refs,
        payload=payload,
        idempotency_key=ident.idempotency_key,
    )
    ports.commands.record_attempt(envelope, received_at=ident.occurred_at)

    chain_result = evaluate_chain(registry, chain, inputs, context)  # type: ignore[arg-type]
    if chain_result.result is not BoundaryResult.ALLOW:
        ports.commands.record_outcome(
            attempt_id=ident.attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=ident.occurred_at,
        )
        raise SessionCommandDenied(chain_result)

    if precondition is not None:
        try:
            precondition()
        except SessionPreconditionUnmet:
            ports.commands.record_outcome(
                attempt_id=ident.attempt_id,
                workspace_id=workspace_id,
                outcome=CommandOutcome.DENIED,
                completed_at=ident.occurred_at,
                failure_code="PRECONDITION_UNMET",
            )
            raise

    if ident.idempotency_key is not None:
        ports.idempotency.begin(envelope, seen_at=ident.occurred_at)

    coordinator = CommitCoordinator(
        ports.connection,
        bnd014_evaluator=ports.bnd014(),
        command_repository=ports.commands,
        audit_repository=ports.audit,
        outbox_repository=ports.outbox,
        commit_repository=ports.commits,
        idempotency_port=ports.idempotency,
        failure_injector=failure_injector,
    )
    return coordinator.commit(
        envelope=envelope,
        actor=actor,
        authority=BindingAuthority(
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="SESSION",
            scope_id=session_id.value,
        ),
        upstream_chain_result=chain_result.result,
        current_version_reader=reader,
        mutation=_Mutation(mutation),
        occurred_at=ident.occurred_at,
        commit_id=ident.commit_id,
    )


def _session_transition(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    transition_id: SessionTransitionId,
    command_type: str,
    ident: CommandIdentity,
    precondition: Callable[[Session], None] | None = None,
) -> CommitUnit:
    payload = SessionTransitionPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    _replay_guard(ports, workspace_id, command_type, ident, payload)
    session = _load_fresh(ports, session_id, expected_session_version)
    resolution = resolve_session_transition(
        current_state=session.state, transition_id=transition_id
    )
    ref = session_target_ref(session_id)
    to_state = resolution.spec.to_state if resolution.spec is not None else session.state

    def mutate() -> MutationOutcome:
        ports.sessions.transition(
            session_id=session_id,
            from_state=session.state,
            to_state=to_state,
            expected_record_version=session.record_version,
            updated_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref=f"session:{session.state.value}",
            state_after_ref=f"session:{to_state.value}",
            event_type=f"SESSION_{to_state.value}",
            event=EventFacts(
                aggregate_ref=ref,
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": session.state.value,
                    "state": to_state.value,
                },
            ),
        )

    return _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=command_type,
        payload=payload,
        ident=ident,
        resolution=resolution,
        target_refs=(ref,),
        expected_versions={ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=(lambda: precondition(session)) if precondition is not None else None,
        mutation=mutate,
    )


def begin_setup(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
) -> CommitUnit:
    """TRN-SESS-002 DRAFT → SETUP (AUTH-DEP-SESS-002, scope: Specific Session)."""
    return _session_transition(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        expected_session_version=expected_session_version,
        transition_id=SessionTransitionId.TRN_SESS_002,
        command_type="CMD_BEGIN_SETUP",
        ident=ident,
    )


def _method_setup_present(session: Session) -> None:
    _raise_if(method_setup_blocker(session))


def begin_challenge_capture(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
) -> CommitUnit:
    """TRN-SESS-003 SETUP → CHALLENGE_CAPTURE; method setup structurally present."""
    return _session_transition(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        expected_session_version=expected_session_version,
        transition_id=SessionTransitionId.TRN_SESS_003,
        command_type="CMD_BEGIN_CHALLENGE_CAPTURE",
        ident=ident,
        precondition=_method_setup_present,
    )


def prepare_burst(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
) -> tuple[CommitUnit, BurstId]:
    """TRN-BURST-001: QuestionBurst absent → PREPARED, HUMAN_ONLY (NQ-DEC-016).
    Version-checks the Session (the Burst belongs to it); the Burst is a created ref."""
    payload = SessionTransitionPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    _replay_guard(ports, workspace_id, "CMD_PREPARE_BURST", ident, payload)
    session = _load_fresh(ports, session_id, expected_session_version)
    burst_id = BurstId(uuid.uuid4())
    ref = session_target_ref(session_id)
    existing = ports.bursts.get_by_session(session_id)
    resolution = resolve_burst_transition(
        current_state=None if existing is None else existing.state,
        transition_id=BurstTransitionId.TRN_BURST_001,
    )

    def precondition() -> None:
        # One Burst per Session (03 §19 topology; get_by_session reads one).
        _raise_if(prepare_burst_blocker(session, existing))

    def mutate() -> MutationOutcome:
        ports.bursts.create_prepared(
            QuestionBurst(
                burst_id=burst_id,
                session_id=session_id,
                workspace_id=session.workspace_id,
                state=BurstState.PREPARED,
                mode=BurstMode.HUMAN_ONLY,
                started_at=None,
                paused_at=None,
                completed_at=None,
                frozen_membership_fingerprint=None,
                record_version=RecordVersion.initial(),
            )
        )
        return MutationOutcome(
            state_before_ref=None,
            state_after_ref=f"burst:{BurstState.PREPARED.value}",
            event_type="QUESTION_BURST_PREPARED",
            result_ref=str(burst_id.value),
            event=EventFacts(
                aggregate_ref=burst_target_ref(burst_id),
                payload={
                    "burst_id": str(burst_id.value),
                    "session_id": str(session_id.value),
                    "state": BurstState.PREPARED.value,
                    "mode": BurstMode.HUMAN_ONLY.value,
                },
            ),
        )

    commit_unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type="CMD_PREPARE_BURST",
        payload=payload,
        ident=ident,
        # A second open Burst is a PRECONDITION (BLOCKED), not a topology
        # denial; BND-007 is only consulted when the topology itself allows.
        resolution=resolution if existing is None else None,
        target_refs=(ref,),
        expected_versions={ref: RecordVersion(expected_session_version)},
        created_refs=(burst_target_ref(burst_id),),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
    )
    return commit_unit, burst_id


def admit_participant(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    participant_user_id: UserId,
    expected_session_version: int,
    ident: CommandIdentity,
) -> CommitUnit:
    """HD-7 (16 §41 REC-006): the Session controller admits an ACTIVE member."""
    payload = AdmitParticipantPayload(
        session_id=str(session_id.value),
        participant_user_id=str(participant_user_id.value),
        expected_session_version=expected_session_version,
    )
    _replay_guard(ports, workspace_id, "CMD_ADMIT_SESSION_PARTICIPANT", ident, payload)
    session = _load_fresh(ports, session_id, expected_session_version)
    participations = SqlAlchemySessionParticipationRepository(ports.connection)
    participation_id = uuid.uuid4()
    ref = session_target_ref(session_id)

    def precondition() -> None:
        if session.state is SessionState.CLOSED:
            raise SessionPreconditionUnmet("SESSION_CLOSED")
        membership = ports.memberships.get_current_membership(
            session.workspace_id, participant_user_id
        )
        if membership is None:
            raise SessionPreconditionUnmet("PARTICIPANT_NOT_ACTIVE_MEMBER")
        if participations.get_current(session_id, participant_user_id) is not None:
            raise SessionPreconditionUnmet("ALREADY_PARTICIPANT")

    def mutate() -> MutationOutcome:
        participations.admit(
            participation_id=participation_id,
            session_id=session_id,
            workspace_id=session.workspace_id,
            user_id=participant_user_id,
            admitted_by_user_id=actor.user_id,
            joined_at=ident.occurred_at,
        )
        return MutationOutcome(
            relation_refs=(f"session_participation:{participation_id}",),
            event_type="SESSION_PARTICIPANT_ADMITTED",
            result_ref=str(participation_id),
            event=EventFacts(
                aggregate_ref=f"session_participation:{participation_id}",
                payload={
                    "participation_id": str(participation_id),
                    "session_id": str(session_id.value),
                    "participant_user_id": str(participant_user_id.value),
                },
            ),
        )

    return _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type="CMD_ADMIT_SESSION_PARTICIPANT",
        payload=payload,
        ident=ident,
        resolution=None,
        target_refs=(ref,),
        expected_versions={ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
    )


def open_question_generation(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
) -> CommitUnit:
    """TRN-SESS-004 bundle: Session CHALLENGE_CAPTURE → QUESTION_GENERATION
    and Burst PREPARED → ACTIVE, atomically."""
    payload = SessionTransitionPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    _replay_guard(ports, workspace_id, "CMD_OPEN_QUESTION_GENERATION", ident, payload)
    session = _load_fresh(ports, session_id, expected_session_version)
    burst = ports.bursts.get_by_session(session_id)
    participations = SqlAlchemySessionParticipationRepository(ports.connection)
    resolution = resolve_session_transition(
        current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_004
    )
    session_ref = session_target_ref(session_id)

    def precondition() -> None:
        challenge = ports.challenges.get(session.challenge_id)
        _raise_if(
            open_question_generation_blocker(
                session,
                burst,
                challenge.title if challenge is not None else None,
                len(participations.list_current(session_id)),
            )
        )

    target_refs: tuple[str, ...] = (session_ref,)
    expected: dict[str, RecordVersion] = {session_ref: RecordVersion(expected_session_version)}
    readers: list[CurrentVersionReader] = [
        SqlAlchemySessionVersionReader(ports.connection, session_id=session_id)
    ]
    if burst is not None:
        bref = burst_target_ref(burst.burst_id)
        target_refs = (session_ref, bref)
        expected[bref] = burst.record_version
        readers.append(SqlAlchemyBurstVersionReader(ports.connection, burst_id=burst.burst_id))

    def mutate() -> MutationOutcome:
        assert burst is not None  # noqa: S101 -- precondition guarantees it
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.CHALLENGE_CAPTURE,
            to_state=SessionState.QUESTION_GENERATION,
            expected_record_version=session.record_version,
            updated_at=ident.occurred_at,
        )
        ports.bursts.start(
            burst_id=burst.burst_id,
            workspace_id=burst.workspace_id,
            expected_record_version=burst.record_version,
            started_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref="session:CHALLENGE_CAPTURE|burst:PREPARED",
            state_after_ref="session:QUESTION_GENERATION|burst:ACTIVE",
            event_type="QUESTION_GENERATION_OPENED",
            event=EventFacts(
                aggregate_ref=session_ref,
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.CHALLENGE_CAPTURE.value,
                    "state": SessionState.QUESTION_GENERATION.value,
                    "burst_id": str(burst.burst_id.value),
                    "burst_state": BurstState.ACTIVE.value,
                },
            ),
        )

    return _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type="CMD_OPEN_QUESTION_GENERATION",
        payload=payload,
        ident=ident,
        resolution=resolution,
        target_refs=target_refs,
        expected_versions=expected,
        created_refs=(),
        reader=_FirstReader(*readers),
        precondition=precondition,
        mutation=mutate,
    )


__all__ = [
    "AdmitParticipantPayload",
    "CommandIdentity",
    "IdempotentReplay",
    "SessionCommandDenied",
    "SessionNotFound",
    "SessionPreconditionUnmet",
    "SessionTransitionPayload",
    "SessionVersionStale",
    "admit_participant",
    "replay_guard",
    "method_setup_blocker",
    "open_question_generation_blocker",
    "prepare_burst_blocker",
    "begin_challenge_capture",
    "begin_setup",
    "open_question_generation",
    "prepare_burst",
]
