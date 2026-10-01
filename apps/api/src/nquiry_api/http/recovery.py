"""Recovery contacts (WU-AUTH-12; 24 §23.2): `POST /auth/recovery/start`,
`POST /auth/recovery/complete`. Thin adapter (24 §23.10)."""

from __future__ import annotations

from application.http_recovery import dispatch_recovery_complete, dispatch_recovery_start
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class RecoveryStartBody(BaseModel):
    email: str


class RecoveryCompleteBody(BaseModel):
    recoveryId: str  # noqa: N815 -- wire name
    token: str
    newPassword: str  # noqa: N815 -- wire name


@router.post("/auth/recovery/start")
def recovery_start(body: RecoveryStartBody) -> JSONResponse:
    status, payload = dispatch_recovery_start(email=body.email)
    return JSONResponse(status_code=status, content=payload)


@router.post("/auth/recovery/complete")
def recovery_complete(body: RecoveryCompleteBody) -> JSONResponse:
    status, payload = dispatch_recovery_complete(
        recovery_id=body.recoveryId, token=body.token, new_password=body.newPassword
    )
    return JSONResponse(status_code=status, content=payload)


__all__ = ["router"]
