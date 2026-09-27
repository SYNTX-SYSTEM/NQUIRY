"""CMD_BEGIN_REFLECTION (WU-PFC-B1): TRN-SESS-007, ANALYSIS -> REFLECTION; and
CMD_BEGIN_QUESTION_SELECTION (WU-PFC-B2): TRN-SESS-008, REFLECTION -> QUESTION_SELECTION.

AUTHORITY (HD-24 rules 10, 11): a human controller Command, the holder of
`SESSION_CONTROL_RIGHT` at exactly `SESSION:<id>` (04 AUTH-DEP-SESS-007 human
path), BINDING at the effect gate. The System path of AUTH-DEP-SESS-007
(SYSTEM_DERIVED, method-derived) is not materialized and stays REQUIRE/DENY
(REC-018): BND-001 accepts HUMAN_USER only.

PRECONDITIONS, under the Session row lock (`application.reflection_proof`, the
one definition shared with the projection):
- the Session is in ANALYSIS;
- no AI operation of the Session is unresolved (BND-017);
- the required AIOP-001 analysis is accepted and its VALIDATED proof
  reconstructs from write-once records to this Session's human BEGIN_ANALYSIS;
- the frozen human set still verifies (the SYSTEM_PROOF that derived analysis
  did not alter raw Questions);
- a proof source admits the proof: `FIXTURE_MOCK` for a Fixture Session
  (HD-24 Option 03), or an eligible real provider (Option 01, empty until
  HARD-DEP-002). A mock proof never admits a non-Fixture Session (HD-20).
Any unmet condition is `blocked`, and the Session stays in ANALYSIS ("AI
failure does not advance state").

EFFECT (one commit): the Session becomes REFLECTION. The committed event
SESSION_REFLECTION records the proof reference (artifact, VALIDATED proof,
provider), its class and source, and the Fixture status, so a NON_PROOF
REFLECTION can never be read as a real provider proof (HD-24 rule 7).

This handler contains no proof-source rule. Moving to Option 01 changes only
`reflection_proof.ELIGIBLE_PROOF_SOURCES` (HD-24 rule 12).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from authority.actor import ActorIdentity
from commit.coordinator import CommitUnit, FailureInjectionPort, MutationOutcome
from domain.question_selection import session_target_ref
from domain.session import Session, SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from events.contracts import EventFacts
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.reflection_proof import ReflectionProof, reflection_readiness
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _run,
    deny_unless_member,
    replay_guard,
)

COMMAND_TYPE = "CMD_BEGIN_REFLECTION"


@dataclass(frozen=True, slots=True)
class BeginReflectionPayload:
    session_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class BeginReflectionResult:
    commit_unit: CommitUnit
    proof: ReflectionProof


def begin_reflection(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> BeginReflectionResult:
    payload = BeginReflectionPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    replay_guard(ports, workspace_id, COMMAND_TYPE, ident, payload)

    session = ports.sessions.get(session_id)
    deny_unless_member(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        operation=COMMAND_TYPE,
        ident=ident,
    )
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )

    session_ref = session_target_ref(session_id)
    resolution = (
        resolve_session_transition(
            current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_007
        )
        if session.state is SessionState.ANALYSIS
        else None
    )
    ready: dict[str, Any] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        readiness = reflection_readiness(ports, fresh)
        if readiness.blocker is not None:
            raise SessionPreconditionUnmet(readiness.blocker)
        assert readiness.proof is not None  # noqa: S101 -- no blocker means a proof
        ready["proof"] = readiness.proof
        ready["session"] = fresh

    def mutate() -> MutationOutcome:
        fresh = ready["session"]
        proof: ReflectionProof = ready["proof"]
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.ANALYSIS,
            to_state=SessionState.REFLECTION,
            expected_record_version=fresh.record_version,
            updated_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref="session:ANALYSIS",
            state_after_ref="session:REFLECTION",
            relation_refs=(
                f"ai_derived_artifact:{proof.analysis_artifact_id}",
                f"ai_validation_proof:{proof.validation_proof_id}",
            ),
            event_type="SESSION_REFLECTION",
            result_ref=proof.validation_proof_id,
            event=EventFacts(
                aggregate_ref=session_ref,
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.ANALYSIS.value,
                    "state": SessionState.REFLECTION.value,
                    "fixture": fresh.fixture,
                    "analysis_artifact_id": proof.analysis_artifact_id,
                    "validation_proof_id": proof.validation_proof_id,
                    "provider": proof.provider,
                    "proof_class": proof.proof_class,
                    "proof_source": proof.proof_source,
                    "is_real_provider_proof": proof.is_real_provider_proof,
                },
            ),
        )

    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=COMMAND_TYPE,
        payload=payload,
        ident=ident,
        resolution=resolution,
        target_refs=(session_ref,),
        expected_versions={session_ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return BeginReflectionResult(commit_unit=unit, proof=ready["proof"])


# ---------------------------------------------------------------- TRN-SESS-008

BEGIN_QUESTION_SELECTION = "CMD_BEGIN_QUESTION_SELECTION"
HUMAN_PROCEDURAL_CONFIRMATION = "HUMAN_PROCEDURAL_CONFIRMATION"
"""HD-25 / NQ-DEC-053: the audited Reflection-completion proof basis."""


@dataclass(frozen=True, slots=True)
class BeginQuestionSelectionPayload:
    session_id: str
    expected_session_version: int
    reflection_completion_confirmed: bool


@dataclass(frozen=True, slots=True)
class BeginQuestionSelectionResult:
    commit_unit: CommitUnit
    reflection_completion_basis: str


def question_selection_blocker(session: Session, *, confirmed: bool) -> str | None:
    """TRN-SESS-008 preconditions (03; HD-25): the Session is in REFLECTION and
    the SESSION_CONTROL_RIGHT holder explicitly confirms Reflection completion.
    Zero Reflection responses are permitted; persisted responses are not a
    precondition (HA-05 stays decoupled)."""
    if session.state is not SessionState.REFLECTION:
        return "SESSION_NOT_IN_REFLECTION"
    if confirmed is not True:
        return "REFLECTION_COMPLETION_NOT_CONFIRMED"
    return None


def begin_question_selection(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    reflection_completion_confirmed: bool,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> BeginQuestionSelectionResult:
    """CMD_BEGIN_QUESTION_SELECTION (WU-PFC-B2): TRN-SESS-008, REFLECTION ->
    QUESTION_SELECTION, carrying the explicit human procedural confirmation of
    Reflection completion (HD-25). No separate Reflection-complete state or
    transition exists: the confirmation is a mandatory field of this Command.
    Without it the Session remains in REFLECTION (03 FAILURE CONSEQUENCE).
    Authority as TRN-SESS-007: BND-001 HUMAN_USER only, BINDING
    SESSION_CONTROL_RIGHT at `SESSION:<id>`; UI navigation, AI output and
    SYSTEM_DERIVED completion never reach this effect (04 AUTH-DEP-SESS-008)."""
    payload = BeginQuestionSelectionPayload(
        session_id=str(session_id.value),
        expected_session_version=expected_session_version,
        reflection_completion_confirmed=reflection_completion_confirmed is True,
    )
    replay_guard(ports, workspace_id, BEGIN_QUESTION_SELECTION, ident, payload)

    session = ports.sessions.get(session_id)
    deny_unless_member(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        operation=BEGIN_QUESTION_SELECTION,
        ident=ident,
    )
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )

    session_ref = session_target_ref(session_id)
    resolution = (
        resolve_session_transition(
            current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_008
        )
        if session.state is SessionState.REFLECTION
        else None
    )
    ready: dict[str, Any] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        blocker = question_selection_blocker(
            fresh, confirmed=payload.reflection_completion_confirmed
        )
        if blocker is not None:
            raise SessionPreconditionUnmet(blocker)
        ready["session"] = fresh

    def mutate() -> MutationOutcome:
        fresh = ready["session"]
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.REFLECTION,
            to_state=SessionState.QUESTION_SELECTION,
            expected_record_version=fresh.record_version,
            updated_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref="session:REFLECTION",
            state_after_ref=(
                f"session:QUESTION_SELECTION|reflection_completion:{HUMAN_PROCEDURAL_CONFIRMATION}"
            ),
            relation_refs=(),
            event_type="SESSION_QUESTION_SELECTION",
            result_ref=None,
            event=EventFacts(
                aggregate_ref=session_ref,
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.REFLECTION.value,
                    "state": SessionState.QUESTION_SELECTION.value,
                    "fixture": fresh.fixture,
                    "reflection_completion_basis": HUMAN_PROCEDURAL_CONFIRMATION,
                },
            ),
        )

    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=BEGIN_QUESTION_SELECTION,
        payload=payload,
        ident=ident,
        resolution=resolution,
        target_refs=(session_ref,),
        expected_versions={session_ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return BeginQuestionSelectionResult(
        commit_unit=unit, reflection_completion_basis=HUMAN_PROCEDURAL_CONFIRMATION
    )


__all__ = [
    "BEGIN_QUESTION_SELECTION",
    "COMMAND_TYPE",
    "HUMAN_PROCEDURAL_CONFIRMATION",
    "BeginQuestionSelectionPayload",
    "BeginQuestionSelectionResult",
    "BeginReflectionPayload",
    "BeginReflectionResult",
    "begin_question_selection",
    "begin_reflection",
    "question_selection_blocker",
]
