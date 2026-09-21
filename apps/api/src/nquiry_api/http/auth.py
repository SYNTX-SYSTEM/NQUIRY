"""Auth dispatch: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.

Local-login field materialization
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`). Same thin-
adapter discipline as `queries.py`/`commands.py`'s own header docstrings
-- all real work (password verification, session issuance/lookup/
revocation) happens in `application.http_dispatch.dispatch_login`/
`dispatch_logout`/`dispatch_current_session`. This file's only extra
job beyond a plain JSON passthrough is the `Set-Cookie`/cookie-clearing
mechanics, because an `HttpOnly` cookie is a response HEADER, not
something `application.http_dispatch` (which returns plain
JSON-serializable dicts everywhere else) can express -- see
`http_dispatch.LoginDispatchResult`'s own docstring.

Cookie flags: `HttpOnly` (client-side JavaScript can never read the
session token -- the entire point of moving off the old
`x-nquiry-actor-user-id` header, which any page script COULD read/spoof
via `document.cookie` if it had been a JS-visible cookie instead) and
`SameSite=Lax` (sent on the real cross-port `localhost:3000` ->
`localhost:8000` fetch calls this prototype makes -- SameSite restricts
cross-SITE requests, not cross-ORIGIN/cross-PORT ones; both ports share
the same site, `localhost`). `Secure` defaults to `False` because this
prototype's own real, running frontend is plain `http://localhost:3000`
(`docs/RUNTIME_OPERATION.md`) -- a `Secure` cookie is never sent over
plain HTTP at all, which would break the one real environment this
repository runs in. Disclosed `[IMPLEMENTATION CHOICE]`, the same class
of honestly-scoped local-only limitation as GAP-14-002 (production
egress) -- a real deployment behind HTTPS must set
`NQUIRY_COOKIE_SECURE=1`.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from application.http_dispatch import (
    SESSION_COOKIE_NAME,
    dispatch_current_session,
    dispatch_login,
    dispatch_logout,
)
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

_COOKIE_SECURE = os.environ.get("NQUIRY_COOKIE_SECURE") == "1"


class LoginRequestBody(BaseModel):
    email: str
    password: str


@router.post("/auth/login")
def login(body: LoginRequestBody, response: Response) -> JSONResponse:
    result = dispatch_login(email=body.email, password=body.password)
    if result.session_token is None or result.expires_at is None:
        return JSONResponse(status_code=401, content=result.body)

    json_response = JSONResponse(content=result.body)
    max_age = max(0, int((result.expires_at - datetime.now(timezone.utc)).total_seconds()))
    json_response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=result.session_token,
        max_age=max_age,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_COOKIE_SECURE,
    )
    return json_response


@router.post("/auth/logout")
def logout(request: Request) -> JSONResponse:
    body = dispatch_logout(session_token=request.cookies.get(SESSION_COOKIE_NAME))
    json_response = JSONResponse(content=body)
    json_response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return json_response


@router.get("/auth/me")
def me(request: Request) -> JSONResponse:
    body = dispatch_current_session(session_token=request.cookies.get(SESSION_COOKIE_NAME))
    status_code = 200 if body.get("kind") == "ok" else 401
    return JSONResponse(status_code=status_code, content=body)


__all__ = ["router"]
