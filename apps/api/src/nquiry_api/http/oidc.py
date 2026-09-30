"""OIDC provider contacts (WU-AUTH-07; 24 §11.21, §23.4–23.5):
`GET /auth/providers`, `GET /auth/oidc/{provider}/start`,
`GET /auth/oidc/{provider}/callback`, and, in DEVELOPMENT / TEST only, the
test provider's consent page `/auth/test-provider/authorize`.

Thin adapter (24 §23.10): parse, call one dispatch function, translate to a
redirect or JSON, set or clear the two cookies. The callback is a GET because
it is a protocol response contact (24 §11.19); it gains no effect from being
reached: every effect is behind the transaction pipeline in
`application.http_oidc`.

The pre-auth binding cookie (24 §21.3): `HttpOnly`, `SameSite=Lax` (sent on
the provider's top-level redirect back to the callback), `Secure` per
`NQUIRY_COOKIE_SECURE`, path `/auth`, lifetime of the transaction. It is not a
session and never becomes one.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from html import escape
from urllib.parse import parse_qs, urlencode

from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import (
    BINDING_COOKIE_NAME,
    BINDING_COOKIE_PATH,
    OidcDispatchResult,
    current_auth_runtime,
    dispatch_list_providers,
    dispatch_oidc_callback,
    dispatch_oidc_start,
)
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

router = APIRouter()

_COOKIE_SECURE = os.environ.get("NQUIRY_COOKIE_SECURE") == "1"


def _response(result: OidcDispatchResult) -> Response:
    response: Response
    if result.location is not None:
        response = RedirectResponse(url=result.location, status_code=result.status_code)
    else:
        response = JSONResponse(status_code=result.status_code, content=result.body)
    if result.binding_token is not None:
        response.set_cookie(
            key=BINDING_COOKIE_NAME,
            value=result.binding_token,
            max_age=result.binding_max_age,
            path=BINDING_COOKIE_PATH,
            httponly=True,
            samesite="lax",
            secure=_COOKIE_SECURE,
        )
    if result.clear_binding:
        response.delete_cookie(key=BINDING_COOKIE_NAME, path=BINDING_COOKIE_PATH)
    if result.session_token is not None and result.session_expires_at is not None:
        max_age = max(
            0, int((result.session_expires_at - datetime.now(timezone.utc)).total_seconds())
        )
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=result.session_token,
            max_age=max_age,
            path="/",
            httponly=True,
            samesite="lax",
            secure=_COOKIE_SECURE,
        )
    return response


@router.get("/auth/providers")
def providers() -> JSONResponse:
    return JSONResponse(content=dispatch_list_providers())


@router.get("/auth/oidc/{provider}/start")
def oidc_start(provider: str, request: Request) -> Response:
    return _response(
        dispatch_oidc_start(
            provider_id=provider, redirect_candidate=request.query_params.get("next")
        )
    )


@router.get("/auth/oidc/{provider}/callback")
def oidc_callback(provider: str, request: Request) -> Response:
    return _response(
        dispatch_oidc_callback(
            provider_id=provider,
            params=dict(request.query_params),
            binding_token=request.cookies.get(BINDING_COOKIE_NAME),
        )
    )


# --- the test provider's consent page (DEVELOPMENT / TEST only) ------------

_AUTHORIZE_FIELDS = (
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "nonce",
    "code_challenge",
    "code_challenge_method",
)


@router.get("/auth/test-provider/authorize")
def test_provider_authorize_page(request: Request) -> Response:
    issuer = current_auth_runtime().test_issuer
    if issuer is None:
        return JSONResponse(status_code=404, content={"kind": "denied", "reasonCode": "NOT_FOUND"})
    hidden = "".join(
        f'<input type="hidden" name="{name}" value="{escape(request.query_params.get(name, ""))}">'
        for name in _AUTHORIZE_FIELDS
    )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>TEST_PROVIDER consent</title></head><body>
<main><h1>TEST_PROVIDER</h1>
<p>This is the local test identity provider (24 §27.1).
It is not a real provider and proves nothing about production.</p>
<form method="post" action="/auth/test-provider/authorize" data-testid="test-provider-form">
{hidden}
<label for="subject">Provider subject</label>
<input id="subject" name="subject" data-testid="test-provider-subject" required
 value="test-subject-1">
<label for="email">Email (provider attribute)</label>
<input id="email" name="email" data-testid="test-provider-email" value="">
<button type="submit" name="action" value="approve"
 data-testid="test-provider-approve">Continue</button>
<button type="submit" name="action" value="cancel"
 data-testid="test-provider-cancel">Cancel</button>
</form></main></body></html>"""
    return HTMLResponse(content=page)


@router.post("/auth/test-provider/authorize")
async def test_provider_authorize(request: Request) -> Response:
    """The consent decision of the test provider. `approve` issues a code for
    the entered subject and sends the browser to the registered redirect URI
    with `code` and `state`; `cancel` sends it there with `error=access_denied`
    (24 §11.16). The body is parsed here to avoid a form-parsing dependency."""
    issuer = current_auth_runtime().test_issuer
    if issuer is None:
        return JSONResponse(status_code=404, content={"kind": "denied", "reasonCode": "NOT_FOUND"})
    form = {k: v[0] for k, v in parse_qs((await request.body()).decode("utf-8")).items()}
    params = {name: form.get(name, "") for name in _AUTHORIZE_FIELDS}
    if params["redirect_uri"] != issuer.redirect_uri:
        return JSONResponse(
            status_code=400, content={"kind": "rejected", "reasonCode": "REDIRECT_URI_MISMATCH"}
        )
    if form.get("action") != "approve":
        query = urlencode({"error": "access_denied", "state": params["state"]})
        return RedirectResponse(url=f"{issuer.redirect_uri}?{query}", status_code=303)
    subject = form.get("subject", "").strip()
    if not subject:
        return JSONResponse(
            status_code=400, content={"kind": "rejected", "reasonCode": "SUBJECT_REQUIRED"}
        )
    try:
        code = issuer.authorize(
            params, subject=subject, email=form.get("email", "").strip() or None
        )
    except (ValueError, KeyError):
        return JSONResponse(
            status_code=400, content={"kind": "rejected", "reasonCode": "MALFORMED_REQUEST"}
        )
    query = urlencode({"code": code, "state": params["state"]})
    return RedirectResponse(url=f"{issuer.redirect_uri}?{query}", status_code=303)


__all__ = ["router"]
