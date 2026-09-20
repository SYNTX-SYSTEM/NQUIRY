"""Query dispatch: `GET /workspaces/{workspaceId}/sessions/{sessionId}`.

Architecture 17 materialization of the extension point this file's own
`__init__.py` reserved since PKG-00 ("`queries.py` ... land in Phase 4+").
A genuine thin adapter (14 §3.1): every line below either extracts a
plain string from the HTTP request or serializes a plain dict already
shaped as `SessionReadResult` (`apps/web/lib/api/types.ts`) into a JSON
response. All real work -- identity resolution, boundary evaluation,
repository construction, the database connection itself -- happens in
`application.http_dispatch.dispatch_get_session_view`, the one
function this module calls (`nquiry_api`'s own 14 §3.1 "May depend on"
list: `application`, `observability`, `semantic_types` only -- this
file imports nothing else).
"""

from __future__ import annotations

from application.http_dispatch import (
    ACTOR_CLASS_HEADER,
    ACTOR_USER_ID_HEADER,
    MalformedActorClaimError,
    MissingActorClaimError,
    dispatch_get_session_view,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/workspaces/{workspace_id}/sessions/{session_id}")
def get_session_view(workspace_id: str, session_id: str, request: Request) -> JSONResponse:
    try:
        body = dispatch_get_session_view(
            actor_user_id_claim=request.headers.get(ACTOR_USER_ID_HEADER),
            actor_class_claim=request.headers.get(ACTOR_CLASS_HEADER),
            workspace_id_str=workspace_id,
            session_id_str=session_id,
        )
    except (MissingActorClaimError, MalformedActorClaimError) as exc:
        return JSONResponse(
            status_code=401, content={"kind": "denied", "result": "DENY", "reasonCode": str(exc)}
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400, content={"kind": "denied", "result": "DENY", "reasonCode": str(exc)}
        )
    return JSONResponse(content=body)


__all__ = ["router"]
