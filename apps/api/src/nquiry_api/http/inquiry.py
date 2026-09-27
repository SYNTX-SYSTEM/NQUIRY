"""F02 routes: Workspace overview, Challenges, Sessions, Session control,
participation, authority grants (WU-02.9).

Thin adapter (14 §3.1): extracts strings from the request, calls exactly
one `application.http_f02` function, serializes `(status, body)`. Identity
comes only from the HttpOnly `nquiry_session` cookie. Every Command route
requires an `Idempotency-Key` header (see `application.http_f02`).

No generic state route exists. Each Session movement is its own path
segment, mapped to one semantic Command (12 §23, 19 §22).
"""

from __future__ import annotations

from typing import Any

from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_f02 import (
    dispatch_capture_question,
    dispatch_challenge_detail,
    dispatch_complete_burst,
    dispatch_create_challenge,
    dispatch_create_session,
    dispatch_grant_authority,
    dispatch_session_command,
    dispatch_session_position,
    dispatch_workspace_overview,
)
from application.http_f04 import (
    dispatch_begin_analysis,
    dispatch_begin_question_selection,
    dispatch_begin_reflection,
    dispatch_request_analysis,
    dispatch_request_clustering,
)
from application.http_f05 import (
    dispatch_append_impact_chain_node,
    dispatch_create_impact_chain,
    dispatch_impact_chain,
    dispatch_question_selections,
    dispatch_select_question,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictBool

router = APIRouter()


def _json(result: tuple[int, dict[str, object]]) -> JSONResponse:
    status, body = result
    return JSONResponse(status_code=status, content=body)


def _token(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE_NAME)


def _idem(request: Request) -> str | None:
    return request.headers.get("Idempotency-Key")


class CreateChallengeBody(BaseModel):
    title: str
    description: str | None = None
    context: str | None = None
    desiredOutcome: str | None = None  # noqa: N815 -- camelCase wire contract
    constraints: str | None = None
    stakeholders: str | None = None


class CreateSessionBody(BaseModel):
    """HD-24: `fixture` declares a Fixture (NON_PROOF) Session. Strictly boolean;
    absent means a normal Session."""

    fixture: StrictBool = False


class GrantBody(BaseModel):
    humanUserId: str  # noqa: N815 -- camelCase wire contract
    authorityClass: str  # noqa: N815
    scopeType: str  # noqa: N815
    scopeId: str  # noqa: N815


class SessionCommandBody(BaseModel):
    expectedVersion: int | None = None  # noqa: N815
    participantUserId: str | None = None  # noqa: N815


class CaptureQuestionBody(BaseModel):
    """Wire contract of a capture: ONLY `originalText` and `expectedBurstVersion`.
    Extra fields are captured (not dropped) so the dispatch can REJECT them."""

    model_config = ConfigDict(extra="allow")
    originalText: Any = None  # noqa: N815 -- camelCase wire contract; validated in dispatch
    expectedBurstVersion: Any = None  # noqa: N815


class CompleteBurstBody(BaseModel):
    expectedVersion: int | None = None  # noqa: N815
    expectedBurstVersion: int | None = None  # noqa: N815


@router.get("/workspaces/{workspace_id}/overview")
def workspace_overview(workspace_id: str, request: Request) -> JSONResponse:
    return _json(
        dispatch_workspace_overview(session_token=_token(request), workspace_id=workspace_id)
    )


@router.post("/workspaces/{workspace_id}/challenges")
def create_challenge(
    workspace_id: str, body: CreateChallengeBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_create_challenge(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            title=body.title,
            description=body.description,
            context=body.context,
            desired_outcome=body.desiredOutcome,
            constraints=body.constraints,
            stakeholders=body.stakeholders,
        )
    )


@router.get("/workspaces/{workspace_id}/challenges/{challenge_id}")
def challenge_detail(workspace_id: str, challenge_id: str, request: Request) -> JSONResponse:
    return _json(
        dispatch_challenge_detail(
            session_token=_token(request), workspace_id=workspace_id, challenge_id=challenge_id
        )
    )


@router.post("/workspaces/{workspace_id}/challenges/{challenge_id}/sessions")
def create_session(
    workspace_id: str,
    challenge_id: str,
    request: Request,
    body: CreateSessionBody | None = None,
) -> JSONResponse:
    return _json(
        dispatch_create_session(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            challenge_id=challenge_id,
            fixture=body.fixture if body is not None else False,
        )
    )


@router.post("/workspaces/{workspace_id}/authority-bindings")
def grant_authority(workspace_id: str, body: GrantBody, request: Request) -> JSONResponse:
    return _json(
        dispatch_grant_authority(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            human_user_id=body.humanUserId,
            authority_class=body.authorityClass,
            scope_type=body.scopeType,
            scope_id=body.scopeId,
        )
    )


@router.get("/workspaces/{workspace_id}/sessions/{session_id}/position")
def session_position(workspace_id: str, session_id: str, request: Request) -> JSONResponse:
    return _json(
        dispatch_session_position(
            session_token=_token(request), workspace_id=workspace_id, session_id=session_id
        )
    )


def _session_command(
    workspace_id: str, session_id: str, command: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_session_command(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            command=command,
            expected_version=body.expectedVersion,
            participant_user_id=body.participantUserId,
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/transitions/begin-setup")
def begin_setup(
    workspace_id: str, session_id: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _session_command(workspace_id, session_id, "begin-setup", body, request)


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/transitions/begin-challenge-capture")
def begin_challenge_capture(
    workspace_id: str, session_id: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _session_command(workspace_id, session_id, "begin-challenge-capture", body, request)


@router.post(
    "/workspaces/{workspace_id}/sessions/{session_id}/transitions/open-question-generation"
)
def open_question_generation(
    workspace_id: str, session_id: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _session_command(workspace_id, session_id, "open-question-generation", body, request)


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/burst")
def prepare_burst(
    workspace_id: str, session_id: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _session_command(workspace_id, session_id, "prepare-burst", body, request)


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/participants")
def admit_participant(
    workspace_id: str, session_id: str, body: SessionCommandBody, request: Request
) -> JSONResponse:
    return _session_command(workspace_id, session_id, "admit-participant", body, request)


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/burst/questions")
def capture_question(
    workspace_id: str, session_id: str, body: CaptureQuestionBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_capture_question(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            original_text=body.originalText,
            expected_burst_version=body.expectedBurstVersion,
            extra_fields=tuple((body.model_extra or {}).keys()),
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/transitions/complete-burst")
def complete_burst(
    workspace_id: str, session_id: str, body: CompleteBurstBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_complete_burst(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_session_version=body.expectedVersion,
            expected_burst_version=body.expectedBurstVersion,
        )
    )


# ------------------------------------------------------------------ F04


class BeginAnalysisBody(BaseModel):
    expectedVersion: int | None = None  # noqa: N815


class BeginQuestionSelectionBody(BaseModel):
    expectedVersion: int | None = None  # noqa: N815
    reflectionCompletionConfirmed: StrictBool | None = None  # noqa: N815 -- HD-25


class SelectQuestionBody(BaseModel):
    questionId: object = None  # noqa: N815 -- validated as a UUID string by the dispatcher
    expectedVersion: int | None = None  # noqa: N815


class AppendImpactNodeBody(BaseModel):
    expectedChainVersion: object = None  # noqa: N815 -- validated by the dispatcher
    level: object = None
    answer: object = None


class OperationRequestBody(BaseModel):
    expectedVersion: int | None = None  # noqa: N815
    case: str | None = None


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/transitions/begin-analysis")
def begin_analysis(
    workspace_id: str, session_id: str, body: BeginAnalysisBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_begin_analysis(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/transitions/begin-reflection")
def begin_reflection(
    workspace_id: str, session_id: str, body: BeginAnalysisBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_begin_reflection(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
        )
    )


@router.post(
    "/workspaces/{workspace_id}/sessions/{session_id}/transitions/begin-question-selection"
)
def begin_question_selection(
    workspace_id: str, session_id: str, body: BeginQuestionSelectionBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_begin_question_selection(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
            reflection_completion_confirmed=body.reflectionCompletionConfirmed,
        )
    )


def _select(
    workspace_id: str,
    session_id: str,
    body: SelectQuestionBody,
    request: Request,
    selection_type: str,
) -> JSONResponse:
    return _json(
        dispatch_select_question(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=body.questionId,
            expected_version=body.expectedVersion,
            selection_type=selection_type,
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/question-selections")
def select_compelling_question(
    workspace_id: str, session_id: str, body: SelectQuestionBody, request: Request
) -> JSONResponse:
    return _select(workspace_id, session_id, body, request, "COMPELLING")


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/primary-question")
def select_primary_question(
    workspace_id: str, session_id: str, body: SelectQuestionBody, request: Request
) -> JSONResponse:
    return _select(workspace_id, session_id, body, request, "PRIMARY")


@router.get("/workspaces/{workspace_id}/sessions/{session_id}/question-selections")
def question_selections(workspace_id: str, session_id: str, request: Request) -> JSONResponse:
    return _json(
        dispatch_question_selections(
            session_token=_token(request), workspace_id=workspace_id, session_id=session_id
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/impact-chain")
def create_impact_chain(
    workspace_id: str, session_id: str, body: BeginAnalysisBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_create_impact_chain(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/impact-chain/nodes")
def append_impact_chain_node(
    workspace_id: str, session_id: str, body: AppendImpactNodeBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_append_impact_chain_node(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_chain_version=body.expectedChainVersion,
            level=body.level,
            answer=body.answer,
        )
    )


@router.get("/workspaces/{workspace_id}/sessions/{session_id}/impact-chain")
def impact_chain(workspace_id: str, session_id: str, request: Request) -> JSONResponse:
    return _json(
        dispatch_impact_chain(
            session_token=_token(request), workspace_id=workspace_id, session_id=session_id
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/analysis/request")
def request_analysis(
    workspace_id: str, session_id: str, body: OperationRequestBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_request_analysis(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
            case=body.case,
        )
    )


@router.post("/workspaces/{workspace_id}/sessions/{session_id}/analysis/clustering/request")
def request_clustering(
    workspace_id: str, session_id: str, body: OperationRequestBody, request: Request
) -> JSONResponse:
    return _json(
        dispatch_request_clustering(
            session_token=_token(request),
            idempotency_key=_idem(request),
            workspace_id=workspace_id,
            session_id=session_id,
            expected_version=body.expectedVersion,
            case=body.case,
        )
    )


__all__ = ["router"]
