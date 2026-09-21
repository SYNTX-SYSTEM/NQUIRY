"""Command dispatch: `POST /decisions/{decisionId}/decide`.

Architecture 17 materialization of the extension point this file's own
`__init__.py` reserved since PKG-00 ("`commands.py` ... land in Phase
4+"), updated by the local-login field
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): identity now
comes from the real, `HttpOnly` `nquiry_session` cookie -- see
`queries.py`'s own updated header docstring for the full rationale.
Same thin-adapter discipline -- all real work happens in
`application.http_dispatch.dispatch_record_human_decision`.
"""

from __future__ import annotations

from application.http_dispatch import (
    SESSION_COOKIE_NAME,
    NoValidSessionError,
    dispatch_record_human_decision,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class RecordHumanDecisionBody(BaseModel):
    selectedOption: str  # noqa: N815 -- wire contract is camelCase (apps/web/lib/api/decisionClient.ts)
    rationale: str | None = None
    confidence: str | None = None


@router.post("/decisions/{decision_id}/decide")
def record_human_decision(
    decision_id: str, body: RecordHumanDecisionBody, request: Request
) -> JSONResponse:
    try:
        result = dispatch_record_human_decision(
            session_token=request.cookies.get(SESSION_COOKIE_NAME),
            decision_id_str=decision_id,
            selected_option=body.selectedOption,
            rationale=body.rationale,
            confidence=body.confidence,
        )
    except NoValidSessionError as exc:
        return JSONResponse(
            status_code=401, content={"kind": "denied", "result": "DENY", "reasonCode": str(exc)}
        )
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"kind": "rejected", "reasonCode": str(exc)})
    return JSONResponse(content=result)


__all__ = ["router"]
