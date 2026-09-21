"""Architecture 17 defect, found during the full-stack local runtime
acceptance field: a real browser loading the real Next.js frontend
(`http://localhost:3000`) and issuing the real `fetch()` calls
`lib/api/client.ts`/`decisionClient.ts` already make against the real
API (`http://localhost:8000`) is blocked by the browser's own
same-origin policy -- the API sent no `Access-Control-Allow-Origin`
header at all. Every prior HTTP proof for Architecture 17 (curl,
`requests`, `TestClient`, and the existing Playwright E2E suite, which
uses `page.route()` network-level mocking and therefore never issues a
REAL cross-origin request) structurally could not have caught this --
CORS is enforced by the browser itself, not by any of those callers.

FastAPI's `CORSMiddleware` is boilerplate HTTP-transport wiring, not a
new domain capability -- it decides which BROWSER ORIGIN may attempt a
request at all, never who is authorized once a request arrives (that
remains real session verification and the real boundary chain, both
unchanged by this fix). `FRONTEND != AUTHORITY` holds exactly as
before: a permitted origin gets nothing but the opportunity to ask,
same as any other caller.

LOCAL-LOGIN FIELD UPDATE
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): identity now
travels as an `HttpOnly` cookie (`nquiry_session`), not as the old
`x-nquiry-actor-user-id`/`x-nquiry-actor-class` request headers -- a
cookie is not a CORS "header" in the preflight sense at all (the
browser attaches it automatically once `credentials: 'include'` is set
and the server sends `Access-Control-Allow-Credentials: true`), so
`allow_headers` now lists only `Content-Type` (still needed for the
JSON bodies `/auth/login` and `/decisions/{id}/decide` both send). This
file's own preflight test is updated to the new, real contract; the new
`allow_credentials=True` assertion is this field's own addition.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from nquiry_api.main import app

_FRONTEND_ORIGIN = "http://localhost:3000"


def test_a_request_from_the_real_frontend_origin_receives_a_cors_allow_header() -> None:
    client = TestClient(app)
    response = client.get("/healthz", headers={"Origin": _FRONTEND_ORIGIN})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == _FRONTEND_ORIGIN


def test_cors_allows_credentials_so_the_session_cookie_can_be_sent_cross_origin() -> None:
    """Without `Access-Control-Allow-Credentials: true`, the browser
    silently drops the `nquiry_session` cookie on every real cross-origin
    (`localhost:3000` -> `localhost:8000`) request -- a real login would
    appear to succeed but every subsequent call would be treated as
    unauthenticated. This is the field's own new regression proof for
    exactly that failure mode."""
    client = TestClient(app)
    response = client.get("/healthz", headers={"Origin": _FRONTEND_ORIGIN})
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_a_preflight_request_for_the_real_decide_route_is_permitted() -> None:
    client = TestClient(app)
    response = client.options(
        "/decisions/00000000-0000-0000-0000-000000000000/decide",
        headers={
            "Origin": _FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == _FRONTEND_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed_headers


def test_a_preflight_request_for_the_real_login_route_is_permitted() -> None:
    client = TestClient(app)
    response = client.options(
        "/auth/login",
        headers={
            "Origin": _FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == _FRONTEND_ORIGIN


def test_an_unrecognized_origin_receives_no_cors_allow_header() -> None:
    """CORS is not authority, but it is also not "allow everyone" --
    only the real, configured local frontend origin is permitted."""
    client = TestClient(app)
    response = client.get("/healthz", headers={"Origin": "http://evil.example"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in {k.lower() for k in response.headers}
