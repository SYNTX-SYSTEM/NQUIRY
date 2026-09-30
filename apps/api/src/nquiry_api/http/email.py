"""Email verification contacts (WU-AUTH-11; 24 §23.2): `POST
/auth/email/verification/start`, `POST /auth/email/verification/complete`,
`GET /auth/emails`, and, in DEVELOPMENT / TEST only, the local mail sink's
outbox `GET /auth/test-mail/outbox` (24 §25.3) so a browser proof can pick up
a challenge without a mail provider.

Thin adapter (24 §23.10): parse, one dispatch call, status + JSON.
"""

from __future__ import annotations

from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_email import (
    dispatch_list_verified_emails,
    dispatch_test_mail_outbox,
    dispatch_verification_complete,
    dispatch_verification_start,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class VerificationStartBody(BaseModel):
    email: str


class VerificationCompleteBody(BaseModel):
    challengeId: str  # noqa: N815 -- wire name (camelCase JSON contract)
    token: str


@router.post("/auth/email/verification/start")
def verification_start(body: VerificationStartBody, request: Request) -> JSONResponse:
    status, payload = dispatch_verification_start(
        session_token=request.cookies.get(SESSION_COOKIE_NAME), email=body.email
    )
    return JSONResponse(status_code=status, content=payload)


@router.post("/auth/email/verification/complete")
def verification_complete(body: VerificationCompleteBody, request: Request) -> JSONResponse:
    status, payload = dispatch_verification_complete(
        session_token=request.cookies.get(SESSION_COOKIE_NAME),
        challenge_id=body.challengeId,
        token=body.token,
    )
    return JSONResponse(status_code=status, content=payload)


@router.get("/auth/emails")
def verified_emails(request: Request) -> JSONResponse:
    status, payload = dispatch_list_verified_emails(
        session_token=request.cookies.get(SESSION_COOKIE_NAME)
    )
    return JSONResponse(status_code=status, content=payload)


@router.get("/auth/test-mail/outbox")
def test_mail_outbox() -> JSONResponse:
    status, payload = dispatch_test_mail_outbox()
    return JSONResponse(status_code=status, content=payload)


__all__ = ["router"]
