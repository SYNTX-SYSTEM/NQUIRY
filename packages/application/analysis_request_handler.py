"""Controller RETRY / RECOVERY requests (F04 WU-04.5 / WU-04.9; §0.1 rule 9).

- CMD_REQUEST_QUESTION_ANALYSIS → OA-2 = (this Command, AIOP-001).
- CMD_REQUEST_QUESTION_CLUSTERING → OA-4 = (this Command, AIOP-002).

AUTHORITY: the human holder of `SESSION_CONTROL_RIGHT` at `SESSION:<id>`
(BINDING; HD-16 / HD-23 "an explicit controller request").

LEGAL IN EXACTLY TWO CASES (derived, fail-closed), both requiring Session
ANALYSIS, no accepted result for the operation (R2 / R8) and no non-terminal
generation for it (E10 / K20):
- RETRY: the latest OA was consumed by a FAILED / REJECTED generation; the new
  generation carries `retry_of` → that generation (08 §45: the failed one is
  not revived);
- RECOVERY: the latest OA was never consumed (the process stopped after its
  commit, or the provider was unavailable); the new OA supersedes it and its
  generation carries no `retry_of`.
The client names the case it intends. A case that disagrees with the persisted
state is REJECTED (`RequestCaseMismatch`, E18 / K20), never silently corrected.
Clustering additionally requires an accepted AIOP-001 artifact X (K12) and
records X write-once (rule 8).

EFFECT (one commit): one immutable OA row recording the chain root
(BEGIN_ANALYSIS), the case, the superseded OA and, for RETRY, `retry_of`; for
clustering, X. No Session state or version changes (EC-2). The system executes
the new OA immediately after this commit (`analysis_system`); this module calls
no AI.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization, RequestCase
from ai_contracts.generation import AIGenerationStatus
from authority.actor import ActorIdentity
from commit.coordinator import CommitUnit, FailureInjectionPort, MutationOutcome
from domain.question_selection import session_target_ref
from domain.session import SessionState
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _run,
    replay_guard,
)

REQUEST_COMMAND = {
    AIOperationId.AIOP_001: "CMD_REQUEST_QUESTION_ANALYSIS",
    AIOperationId.AIOP_002: "CMD_REQUEST_QUESTION_CLUSTERING",
}
_SHAPE = {
    AIOperationId.AIOP_001: AuthorizationShape.OA_2,
    AIOperationId.AIOP_002: AuthorizationShape.OA_4,
}
_NON_TERMINAL = frozenset(
    {AIGenerationStatus.REQUESTED, AIGenerationStatus.RUNNING, AIGenerationStatus.OUTPUT_RECEIVED}
)
_FAILED = frozenset({AIGenerationStatus.FAILED, AIGenerationStatus.REJECTED})


class RequestCaseMismatch(SessionPreconditionUnmet):
    """E18 / K20: the named case disagrees with the persisted state. Input, not
    authority: surfaced as `rejected`."""


@dataclass(frozen=True, slots=True)
class OperationRequestPayload:
    session_id: str
    expected_session_version: int
    operation: str
    case: str


@dataclass(frozen=True, slots=True)
class RequestResult:
    commit_unit: CommitUnit
    authorization_id: uuid.UUID
    case: RequestCase


@dataclass(frozen=True, slots=True)
class RequestAvailability:
    """For the capability projection: which case is legal now, or why none."""

    case: RequestCase | None
    blocker: str | None


def request_availability(
    ports: GovernedPorts, session_id: SessionId, op: AIOperationId, state: SessionState
) -> RequestAvailability:
    """The request preconditions in one place (Command and projection)."""
    if state is not SessionState.ANALYSIS:
        return RequestAvailability(None, f"SESSION_NOT_ANALYSIS:{state.value}")
    records = ports.ai_records
    if records.get_accepted_artifact(session_id, op) is not None:
        return RequestAvailability(None, "RESULT_ALREADY_ACCEPTED")
    if (
        op is AIOperationId.AIOP_002
        and records.get_accepted_artifact(session_id, AIOperationId.AIOP_001) is None
    ):
        return RequestAvailability(None, "NO_ACCEPTED_ANALYSIS")
    if any(g.status in _NON_TERMINAL for g in records.list_session_generations(session_id, op)):
        return RequestAvailability(None, "GENERATION_IN_PROGRESS")
    latest = ports.ai_authorizations.latest(session_id, op)
    if latest is None:
        return RequestAvailability(None, "NO_AUTHORIZATION_TO_SUPERSEDE")
    carrier = records.get_generation_for_authorization(latest.authorization_id)
    if carrier is None:
        return RequestAvailability(RequestCase.RECOVERY, None)
    if carrier.status in _FAILED:
        return RequestAvailability(RequestCase.RETRY, None)
    return RequestAvailability(None, f"LATEST_GENERATION_{carrier.status.value}")


def request_operation(
    ports: GovernedPorts,
    *,
    ai_operation_id: AIOperationId,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    case: RequestCase,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> RequestResult:
    op = ai_operation_id
    command_type = REQUEST_COMMAND[op]
    payload = OperationRequestPayload(
        session_id=str(session_id.value),
        expected_session_version=expected_session_version,
        operation=op.value,
        case=case.value,
    )
    replay_guard(ports, workspace_id, command_type, ident, payload)
    session = ports.sessions.get(session_id)
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )
    authorization_id = uuid.uuid4()
    plan: dict[str, OperationAuthorization] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        availability = request_availability(ports, session_id, op, fresh.state)
        if availability.blocker is not None:
            raise SessionPreconditionUnmet(availability.blocker)
        if availability.case is not case:
            raise RequestCaseMismatch(
                f"REQUEST_CASE_MISMATCH:{availability.case.value if availability.case else None}"
            )
        latest = ports.ai_authorizations.latest(session_id, op)
        assert latest is not None  # noqa: S101 -- availability guarantees it
        carrier = ports.ai_records.get_generation_for_authorization(latest.authorization_id)
        x = (
            ports.ai_records.get_accepted_artifact(session_id, AIOperationId.AIOP_001)
            if op is AIOperationId.AIOP_002
            else None
        )
        plan["latest"] = latest
        plan["new"] = OperationAuthorization(
            authorization_id=authorization_id,
            workspace_id=workspace_id,
            session_id=session_id,
            ai_operation_id=op,
            shape=_SHAPE[op],
            authorizing_command_id=ident.command_id,
            sequence_no=latest.sequence_no + 1,
            chain_root_command_id=latest.chain_root_command_id,
            created_at=ident.occurred_at,
            request_case=case,
            supersedes_authorization_id=latest.authorization_id,
            retry_of_generation_id=(
                carrier.ai_generation_id if case is RequestCase.RETRY and carrier else None
            ),
            precondition_artifact_ref=None if x is None else x.ai_derived_artifact_id,
        )

    def mutate() -> MutationOutcome:
        new = plan["new"]
        ports.ai_authorizations.create(new)
        return MutationOutcome(
            state_before_ref=f"ai_operation_authorization:{plan['latest'].authorization_id}:LATEST",
            state_after_ref=f"ai_operation_authorization:{new.authorization_id}:{new.shape.value}:{case.value}",
            relation_refs=(f"ai_operation_authorization:{new.authorization_id}",),
            event_type="AI_OPERATION_REQUESTED",
            result_ref=str(new.authorization_id),
        )

    ref = session_target_ref(session_id)
    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=command_type,
        payload=payload,
        ident=ident,
        resolution=None,
        target_refs=(ref,),
        expected_versions={ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return RequestResult(commit_unit=unit, authorization_id=authorization_id, case=case)


__all__ = [
    "OperationRequestPayload",
    "REQUEST_COMMAND",
    "RequestAvailability",
    "RequestCaseMismatch",
    "RequestResult",
    "request_availability",
    "request_operation",
]
