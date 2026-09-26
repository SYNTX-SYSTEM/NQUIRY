"""CMD_BEGIN_ANALYSIS (F04 WU-04.1): TRN-SESS-006, QUESTION_CAPTURE → ANALYSIS.

AUTHORITY: the human holder of `SESSION_CONTROL_RIGHT` at exactly
`SESSION:<id>` (04 AUTH-DEP-SESS-006 human path; HD-1 / HD-9), BINDING at the
effect gate. The System path of AUTH-DEP-SESS-006 (SYSTEM_DERIVED,
method-derived) is not materialized and stays REQUIRE/DENY under D8.

PRECONDITIONS (03 TRN-SESS-006), under the Session row lock and then the Burst
row lock: Session QUESTION_CAPTURE; Burst COMPLETED; the frozen set re-verifies
(`verify_frozen_set`, FBR-F03-4); no capture of this Burst is unresolved.
A failed transition leaves the Session in QUESTION_CAPTURE.

EFFECT (one commit): the Session becomes ANALYSIS and exactly one operation
authorization OA-1 = (this Command, AIOP-001) is created (HD-16; §0.1). No AI is
called in this commit (A8): the authorized run is a separate, later
SYSTEM_OPERATION (`application.analysis_system`), after this commit is durable
(pre-implementation binding PI-2). This module imports no AI Gateway.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization
from authority.actor import ActorIdentity
from commit.coordinator import (
    CommitUnit,
    CurrentVersionReader,
    FailureInjectionPort,
    MutationOutcome,
)
from domain.burst import BurstState
from domain.question_selection import session_target_ref
from domain.session import Session, SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from events.contracts import EventFacts
from persistence.burst_repository import SqlAlchemyBurstVersionReader, burst_target_ref
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.frozen_set import verify_frozen_set
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _FirstReader,
    _run,
    replay_guard,
)

COMMAND_TYPE = "CMD_BEGIN_ANALYSIS"


@dataclass(frozen=True, slots=True)
class BeginAnalysisPayload:
    session_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class BeginAnalysisResult:
    commit_unit: CommitUnit
    authorization_id: uuid.UUID


def begin_analysis_blocker(
    session_state: SessionState,
    burst_state: BurstState | None,
    *,
    frozen_verified: bool | None = None,
    unresolved_capture: bool = False,
) -> str | None:
    """The non-authority, non-version preconditions in one place, shared with the
    capability projection. Facts not loaded are passed as neutral defaults."""
    if session_state is not SessionState.QUESTION_CAPTURE:
        return f"SESSION_NOT_QUESTION_CAPTURE:{session_state.value}"
    if burst_state is None:
        return "BURST_ABSENT"
    if burst_state is not BurstState.COMPLETED:
        return f"BURST_NOT_COMPLETED:{burst_state.value}"
    if unresolved_capture:
        return "UNRESOLVED_CAPTURE"
    if frozen_verified is False:
        return "FROZEN_SET_UNVERIFIED"
    return None


def begin_analysis(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> BeginAnalysisResult:
    payload = BeginAnalysisPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    replay_guard(ports, workspace_id, COMMAND_TYPE, ident, payload)

    session = ports.sessions.get(session_id)
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )
    burst = ports.bursts.get_by_session(session_id)

    session_ref = session_target_ref(session_id)
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

    # BND-007 only when the 03 topology itself allows the transition; any other
    # state is a PRECONDITION (blocked), the reading F02/F03 apply.
    resolution = (
        resolve_session_transition(
            current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_006
        )
        if session.state is SessionState.QUESTION_CAPTURE
        else None
    )
    authorization_id = uuid.uuid4()
    locked: dict[str, Session] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        fresh_burst = ports.bursts.get_by_session_for_update(session_id)
        state_blocker = begin_analysis_blocker(
            fresh.state, None if fresh_burst is None else fresh_burst.state
        )
        if state_blocker is not None:
            raise SessionPreconditionUnmet(state_blocker)
        assert fresh_burst is not None  # noqa: S101 -- the blocker guarantees it
        unresolved = bool(
            ports.commands.list_unresolved_for_target(
                workspace_id=workspace_id,
                command_type="CMD_CAPTURE_BURST_QUESTION",
                target_ref=burst_target_ref(fresh_burst.burst_id),
            )
        )
        blocker = begin_analysis_blocker(
            fresh.state,
            fresh_burst.state,
            frozen_verified=verify_frozen_set(ports, fresh_burst).matches,
            unresolved_capture=unresolved,
        )
        if blocker is not None:
            raise SessionPreconditionUnmet(blocker)
        locked["session"] = fresh

    def mutate() -> MutationOutcome:
        fresh = locked["session"]
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.QUESTION_CAPTURE,
            to_state=SessionState.ANALYSIS,
            expected_record_version=fresh.record_version,
            updated_at=ident.occurred_at,
        )
        # HD-16: exactly one operation authorization, OA-1. Written once, in the
        # same commit that establishes ANALYSIS (§0.1 rule 8).
        ports.ai_authorizations.create(
            OperationAuthorization(
                authorization_id=authorization_id,
                workspace_id=workspace_id,
                session_id=session_id,
                ai_operation_id=AIOperationId.AIOP_001,
                shape=AuthorizationShape.OA_1,
                authorizing_command_id=ident.command_id,
                sequence_no=1,
                chain_root_command_id=ident.command_id,
                created_at=ident.occurred_at,
            )
        )
        return MutationOutcome(
            state_before_ref="session:QUESTION_CAPTURE",
            state_after_ref="session:ANALYSIS",
            relation_refs=(f"ai_operation_authorization:{authorization_id}",),
            event_type="SESSION_ANALYSIS_BEGUN",
            result_ref=str(authorization_id),
            event=EventFacts(
                aggregate_ref=session_target_ref(session_id),
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.QUESTION_CAPTURE.value,
                    "state": SessionState.ANALYSIS.value,
                    "operation_authorization_id": str(authorization_id),
                    "ai_operation_id": AIOperationId.AIOP_001.value,
                    "authorization_shape": AuthorizationShape.OA_1.value,
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
        target_refs=target_refs,
        expected_versions=expected,
        created_refs=(),
        reader=_FirstReader(*readers),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return BeginAnalysisResult(commit_unit=unit, authorization_id=authorization_id)


__all__ = [
    "COMMAND_TYPE",
    "BeginAnalysisPayload",
    "BeginAnalysisResult",
    "begin_analysis",
    "begin_analysis_blocker",
]
