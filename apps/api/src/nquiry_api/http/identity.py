"""Identity presentation contact (PURPLE_IDENTITY_PRESENTATION_01):
`GET /auth/identity` — the authenticated self only. Thin adapter (24 §23.10)."""

from __future__ import annotations

from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_identity import dispatch_identity_presentation
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/auth/identity")
def identity(request: Request) -> JSONResponse:
    status, body = dispatch_identity_presentation(
        session_token=request.cookies.get(SESSION_COOKIE_NAME)
    )
    return JSONResponse(status_code=status, content=body)


__all__ = ["router"]
