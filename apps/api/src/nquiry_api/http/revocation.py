"""Method unlink contact (WU-AUTH-13; 24 §11.9 recommended shape
`POST /auth/methods/{methodId}/unlink`). Thin adapter (24 §23.10)."""

from __future__ import annotations

from application.http_dispatch import SESSION_COOKIE_NAME, SessionDispatchResult
from application.http_revocation import dispatch_unlink_method
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


def _session_response(result: SessionDispatchResult) -> JSONResponse:
    json_response = JSONResponse(status_code=result.status_code, content=result.body)
    if result.clear_cookie:
        json_response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return json_response


@router.post("/auth/methods/{method_id}/unlink")
def unlink_method(method_id: str, request: Request) -> JSONResponse:
    return _session_response(
        dispatch_unlink_method(
            session_token=request.cookies.get(SESSION_COOKIE_NAME), method_id=method_id
        )
    )


__all__ = ["router"]
