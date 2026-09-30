"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) route: the observation ingress
(Architecture 26, FBR-PCPG-1; R-01/R-02 only).

Thin adapter (14 §3.1): extracts strings from the request, calls exactly one
`application.http_pcpg` function, serializes `(status, body)`. Identity comes
only from the HttpOnly `nquiry_session` cookie, same as every other route.

This is a QUERY (side-effect-free, `01_INVARIANTS.md` I-18): no
Idempotency-Key, no canonical write. `POST`, not `GET`, only because the raw
intent needs a request body the `GET` verb does not carry cleanly — see
`02_RELATIONS.md` R-01: "not a Command and carries no Idempotency semantics
of a Command".
"""

from __future__ import annotations

from typing import Any

from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_pcpg import dispatch_submit_observation
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


def _json(result: tuple[int, dict[str, object]]) -> JSONResponse:
    status, body = result
    return JSONResponse(status_code=status, content=body)


def _token(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE_NAME)


class ObservationBody(BaseModel):
    """Wire contract: ONLY `rawIntent`, optionally `sessionId` and
    `declaredPurpose`. Nothing else is read from the body by this Field
    (unknown fields are ignored, Pydantic's default) -- there is no governance
    evaluation yet for them to leak into (FBR-PCPG-2..5 pending)."""

    rawIntent: Any = None  # noqa: N815 -- camelCase wire contract; validated in dispatch
    sessionId: str | None = None  # noqa: N815
    declaredPurpose: Any = None  # noqa: N815


@router.post("/workspaces/{workspace_id}/prompt-observations")
def submit_observation(workspace_id: str, body: ObservationBody, request: Request) -> JSONResponse:
    return _json(
        dispatch_submit_observation(
            session_token=_token(request),
            workspace_id=workspace_id,
            raw_intent=body.rawIntent,
            session_id=body.sessionId,
            declared_purpose=body.declaredPurpose,
        )
    )


__all__ = ["router"]
