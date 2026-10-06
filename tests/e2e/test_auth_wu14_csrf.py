"""T14: anti-CSRF boundary (24 WU-AUTH-14; §21.3, §21.5–21.9; §38
falsifiers 62–66; §44.7).

MUST BECOME TRUE: every unsafe cookie-authenticated application request
passes the explicit anti-CSRF boundary before application execution; local
password login has its own login-CSRF boundary (origin + JSON request
contract) that runs before credential validation; legitimate same-origin and
allowed-origin requests still work and a successful login still creates a
fresh session; the allowed origins are explicit, pinned and configurable.

MUST REMAIN IMPOSSIBLE: a hostile-origin unsafe request committing an effect;
a hostile origin logging a victim browser into an attacker-selected local
account; a CSRF failure becoming an application effect; OIDC state standing
in for application CSRF; a safe request mutating; a wildcard origin.

The real-browser proof of the same boundary (a hostile page served from a
third origin against the real API) is `apps/web/tests/real-stack/
auth-csrf.real.spec.ts` on the AUTH real lane (`scripts/auth_real_stack.sh`).
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_oidc as http_oidc
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.request_security import (
    configure_request_security,
    current_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    authentication_methods_table,
    local_auth_sessions_table,
    users_table,
    workspaces_table,
)
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.oidc_test_issuer import LocalTestIssuer
from security.request_security import AllowedOriginsInvalid, RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_APP_ORIGIN = "http://localhost:3000"
_EVIL = "https://evil.example"
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
}
_WATCHED = (local_auth_sessions_table, authentication_methods_table, workspaces_table, users_table)


@pytest.fixture
def issuer() -> LocalTestIssuer:
    return LocalTestIssuer.create()


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (http_dispatch, http_oidc, http_email, http_revocation):
        monkeypatch.setattr(module, "connect", _reuse)
    configure_auth_runtime(
        auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=LocalMailCapture())
    )
    configure_request_security(RequestSecurityPolicy(allowed_origins=(_APP_ORIGIN,)))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


def _local_user(db: sa.Connection) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Victim",
            record_version=1,
            created_at=_NOW,
            established_at=_NOW,  # WU-AUTH-22: established
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def _login(client: TestClient, email: str, **headers: str):  # type: ignore[no-untyped-def]
    return client.post("/auth/login", json={"email": email, "password": _PASSWORD}, headers=headers)


def _counts(db: sa.Connection) -> dict[str, int]:
    return {
        t.name: int(db.execute(sa.select(sa.func.count()).select_from(t)).scalar_one())
        for t in _WATCHED
    }


def _sessions(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.user_id == user_id.value
            )
        ).mappings()
    )


_UNSAFE_CONTACTS: list[tuple[str, dict[str, Any] | None]] = [
    ("/auth/logout-all", None),
    ("/auth/logout", None),
    ("/auth/sessions/{session}/revoke", None),
    ("/auth/methods/{method}/unlink", None),
    ("/auth/email/verification/start", {"email": "v@example.test"}),
    ("/auth/oidc/test/link/start", None),
    ("/workspaces", {"name": "W"}),
]


def _fill(path: str, world: dict[str, str]) -> str:
    for key, value in world.items():
        path = path.replace("{" + key + "}", value)
    return path


# ---------------------------------------------- unsafe application requests


@pytest.mark.parametrize(("path", "body"), _UNSAFE_CONTACTS)
@pytest.mark.parametrize(
    "hostile",
    [
        {"Origin": _EVIL},
        {"Origin": "null"},
        {"Origin": "http://localhost:3001"},
        {"Origin": "https://localhost:3000"},
        {"Sec-Fetch-Site": "cross-site"},
        {"Sec-Fetch-Site": "same-site"},
        {"Origin": _EVIL, "Sec-Fetch-Site": "same-origin"},  # Origin decides
    ],
)
def test_a_hostile_unsafe_cookie_authenticated_request_is_refused_before_any_effect(
    db_connection: sa.Connection,
    client: TestClient,
    path: str,
    body: dict[str, Any] | None,
    hostile: dict[str, str],
) -> None:
    user_id, email = _local_user(db_connection)
    assert _login(client, email).status_code == 200
    session_id = client.get("/auth/sessions").json()["sessions"][0]["sessionId"]
    method_id = client.get("/auth/methods").json()["methods"][0]["methodId"]
    world = {"session": session_id, "method": method_id}
    before = _counts(db_connection)
    sessions_before = _sessions(db_connection, user_id)

    response = client.post(
        _fill(path, world),
        json=body,
        headers={**hostile, "Idempotency-Key": str(uuid.uuid4())},
    )

    assert response.status_code == 403, (path, hostile, response.text)
    assert response.json() == {"kind": "denied", "reasonCode": "CSRF_REJECTED"}
    assert SESSION_COOKIE_NAME not in response.headers.get("set-cookie", "")
    assert _counts(db_connection) == before
    assert _sessions(db_connection, user_id) == sessions_before
    assert client.get("/auth/me").status_code == 200  # the victim's session survives


@pytest.mark.parametrize(
    "legitimate",
    [
        {"Origin": _APP_ORIGIN},
        {"Origin": _APP_ORIGIN, "Sec-Fetch-Site": "same-site"},
        {"Origin": "http://testserver"},  # the API's own origin (its own pages' forms)
        {"Sec-Fetch-Site": "same-origin"},
        {"Sec-Fetch-Site": "none"},
        {},  # no browser metadata: not a browser
    ],
)
def test_a_legitimate_unsafe_request_passes_and_commits(
    db_connection: sa.Connection, client: TestClient, legitimate: dict[str, str]
) -> None:
    user_id, email = _local_user(db_connection)
    assert _login(client, email).status_code == 200

    response = client.post("/auth/logout-all", headers=legitimate)

    assert response.status_code == 200 and response.json()["revokedSessions"] == 1
    assert all(s["revoked_at"] is not None for s in _sessions(db_connection, user_id))


def test_the_boundary_runs_before_the_application_even_with_no_session(
    client: TestClient,
) -> None:
    """A hostile request that would be a 401 anyway is still answered as the
    boundary failure it is (24 §21.7 "boundary failure, not application
    effect"); the application is never entered."""
    response = client.post("/auth/logout-all", headers={"Origin": _EVIL})
    assert response.status_code == 403
    assert response.json()["reasonCode"] == "CSRF_REJECTED"


def test_safe_requests_commit_nothing(db_connection: sa.Connection, client: TestClient) -> None:
    _, email = _local_user(db_connection)
    assert _login(client, email).status_code == 200
    before = _counts(db_connection)
    rows_before = db_connection.execute(
        sa.select(local_auth_sessions_table).order_by(local_auth_sessions_table.c.id)
    ).all()
    for path in ("/auth/me", "/auth/sessions", "/auth/methods", "/auth/emails", "/auth/providers"):
        assert client.get(path, headers={"Origin": _EVIL}).status_code in (200, 401), path
    assert _counts(db_connection) == before
    assert (
        db_connection.execute(
            sa.select(local_auth_sessions_table).order_by(local_auth_sessions_table.c.id)
        ).all()
        == rows_before
    )


# ------------------------------------------------------ local login-CSRF


def test_a_hostile_origin_cannot_log_the_victim_browser_into_an_attacker_account(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """24 §21.6 falsifier. The attacker's own credentials are valid; the
    submission comes from a foreign origin; no session may come of it."""
    attacker_id, attacker_email = _local_user(db_connection)
    before = _counts(db_connection)

    for hostile in ({"Origin": _EVIL}, {"Origin": "null"}, {"Sec-Fetch-Site": "cross-site"}):
        response = _login(client, attacker_email, **hostile)
        assert response.status_code == 403, hostile
        assert response.json() == {"kind": "denied", "reasonCode": "LOGIN_CSRF_REJECTED"}
        assert SESSION_COOKIE_NAME not in response.cookies
    assert _sessions(db_connection, attacker_id) == []
    assert _counts(db_connection) == before
    assert client.get("/auth/me").status_code == 401


@pytest.mark.parametrize(
    "content_type",
    ["application/x-www-form-urlencoded", "multipart/form-data; boundary=x", "text/plain", None],
)
def test_a_form_shaped_login_is_refused_by_the_request_contract_before_credentials(
    db_connection: sa.Connection, client: TestClient, content_type: str | None
) -> None:
    """A cross-site HTML form can only produce these shapes; the login
    contract is JSON (24 §21.6 "request media-type contract"). Refused even
    from the allowed origin and even with no browser metadata."""
    attacker_id, attacker_email = _local_user(db_connection)
    body = f'{{"email": "{attacker_email}", "password": "{_PASSWORD}"}}'.encode()
    for origin in ({"Origin": _APP_ORIGIN}, {}):
        headers = {**origin}
        if content_type is not None:
            headers["Content-Type"] = content_type
        response = client.post("/auth/login", content=body, headers=headers)
        assert response.status_code == 403, (content_type, origin)
        assert response.json() == {"kind": "denied", "reasonCode": "LOGIN_CSRF_REJECTED"}
        assert SESSION_COOKIE_NAME not in response.cookies
    assert _sessions(db_connection, attacker_id) == []


def test_a_legitimate_login_still_creates_a_fresh_session(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    first = _login(client, email, Origin=_APP_ORIGIN)
    assert first.status_code == 200 and SESSION_COOKIE_NAME in first.cookies
    first_token = first.cookies[SESSION_COOKIE_NAME]
    # a second login from a browser that already holds a session: a fresh
    # session, never the presented one (24 §21.5)
    second = _login(client, email, Origin=_APP_ORIGIN, **{"Sec-Fetch-Site": "same-site"})
    assert second.status_code == 200
    assert second.cookies[SESSION_COOKIE_NAME] != first_token
    assert len(_sessions(db_connection, user_id)) == 2
    # wrong password under the same legitimate contract is still a credential denial
    wrong = client.post(
        "/auth/login", json={"email": email, "password": "nope"}, headers={"Origin": _APP_ORIGIN}
    )
    assert wrong.status_code == 401 and wrong.json()["reasonCode"] == "INVALID_CREDENTIALS"


# -------------------------------------------- protocol callback stays itself


def test_the_provider_callback_is_governed_by_its_own_proof_not_by_the_csrf_boundary(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """The provider redirect IS cross-site (24 §21.4, §21.8). The callback
    GET carries `Sec-Fetch-Site: cross-site` and no allowed Origin, and must
    still be processed by the transaction / binding / state / nonce proof."""
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject="csrf-callback-subject")

    response = client.get(
        "/auth/oidc/test/callback",
        params={"code": code, "state": params["state"]},
        headers={"Sec-Fetch-Site": "cross-site", "Referer": "https://accounts.example/"},
    )

    # the subject is unknown and creation is DENIED by default: the protocol
    # proof ran to its own answer, which is the point
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login?auth=")
    assert "CSRF" not in response.headers["location"]


def test_the_test_provider_consent_form_posts_from_the_api_s_own_origin(
    client: TestClient, issuer: LocalTestIssuer
) -> None:
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    response = client.post(
        "/auth/test-provider/authorize",
        content="&".join(
            f"{k}={v}" for k, v in {**params, "subject": "s", "decision": "deny"}.items()
        ),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://testserver",
        },
    )
    assert response.status_code in (302, 303)
    hostile = client.post(
        "/auth/test-provider/authorize",
        content="a=b",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Origin": _EVIL},
    )
    assert hostile.status_code == 403 and hostile.json()["reasonCode"] == "CSRF_REJECTED"


# -------------------------------------------------------- configuration


def test_allowed_origins_are_configured_explicitly_and_refuse_a_wildcard() -> None:
    assert request_security_from_environment({}).allowed_origins == ("http://localhost:3000",)
    assert request_security_from_environment(
        {"NQUIRY_ALLOWED_ORIGINS": "https://nquiry.condyn.eu,http://localhost:13460"}
    ).allowed_origins == ("https://nquiry.condyn.eu", "http://localhost:13460")
    for raw in ("*", "https://nquiry.condyn.eu,*", "nquiry.condyn.eu"):
        with pytest.raises(AllowedOriginsInvalid):
            request_security_from_environment({"NQUIRY_ALLOWED_ORIGINS": raw})


def test_cors_is_pinned_to_the_same_origins_and_is_not_the_boundary(client: TestClient) -> None:
    """CORS != CSRF (24 §21.9): the CORS layer answers preflights for the
    configured origins only; the boundary above refuses hostile origins
    whether or not a preflight ever happened (simple requests have none)."""
    cors = [m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"]
    assert len(cors) == 1
    assert tuple(cors[0].kwargs["allow_origins"]) == current_request_security().allowed_origins
    assert cors[0].kwargs["allow_credentials"] is True
    assert "*" not in cors[0].kwargs["allow_origins"]
    preflight = client.options(
        "/auth/logout-all",
        headers={"Origin": _EVIL, "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in preflight.headers
    allowed = client.options(
        "/auth/logout-all",
        headers={"Origin": _APP_ORIGIN, "Access-Control-Request-Method": "POST"},
    )
    assert allowed.headers.get("access-control-allow-origin") == _APP_ORIGIN


# ----------------------------------- split origins: destinations reach the app


def test_local_destinations_are_prefixed_with_the_app_origin_when_configured(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Found by the real lane: with the app on another origin than the API, a
    relative `Location` landed the browser on the API. Provider URLs are
    never prefixed; local destinations are (login projection, post-login
    target, link projection)."""
    configure_auth_runtime(
        auth_runtime_from_environment(
            {**_ENV, "NQUIRY_PUBLIC_WEB_BASE_URL": "http://localhost:13470"},
            test_issuer=issuer,
            mail_sink=LocalMailCapture(),
        )
    )
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    assert start.headers["location"].startswith(issuer.authorization_endpoint)
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    denied = client.get(
        "/auth/oidc/test/callback",
        params={"code": issuer.authorize(params, subject="split-origin"), "state": params["state"]},
    )
    assert denied.headers["location"] == "http://localhost:13470/login?auth=unavailable"

    _, email = _local_user(db_connection)
    assert _login(client, email).status_code == 200
    link = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    link_params = {k: v[0] for k, v in parse_qs(urlparse(link.headers["location"]).query).items()}
    linked = client.get(
        "/auth/oidc/test/link/callback",
        params={
            "code": issuer.authorize(link_params, subject="split-origin"),
            "state": link_params["state"],
        },
    )
    assert linked.headers["location"] == "http://localhost:13470/account/security?link=ok"
    # the app's own default (same origin) stays relative
    configure_auth_runtime(
        auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=LocalMailCapture())
    )
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    relative = client.get(
        "/auth/oidc/test/callback",
        params={
            "code": issuer.authorize(params, subject="split-origin-2"),
            "state": params["state"],
        },
    )
    assert relative.headers["location"] == "/login?auth=unavailable"


def test_the_web_base_must_be_an_explicit_origin() -> None:
    for raw in ("localhost:13470", "http://localhost:13470/", "*", "http://localhost:13470/app"):
        with pytest.raises(ValueError):
            auth_runtime_from_environment(
                {**_ENV, "NQUIRY_PUBLIC_WEB_BASE_URL": raw}, test_issuer=LocalTestIssuer.create()
            )
