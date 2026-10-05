"""Credential rotation contact (WU-AUTH-19; 24 §9.2, §23.2):
`POST /auth/password/change`. Thin adapter (24 §23.10)."""

from __future__ import annotations

from application.http_credential import dispatch_password_change
from application.http_dispatch import SESSION_COOKIE_NAME
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class PasswordChangeBody(BaseModel):
    currentPassword: str  # noqa: N815 -- wire name
    newPassword: str  # noqa: N815 -- wire name


@router.post("/auth/password/change")
def password_change(request: Request, body: PasswordChangeBody) -> JSONResponse:
    status, payload = dispatch_password_change(
        session_token=request.cookies.get(SESSION_COOKIE_NAME),
        current_password=body.currentPassword,
        new_password=body.newPassword,
    )
    return JSONResponse(status_code=status, content=payload)


__all__ = ["router"]
