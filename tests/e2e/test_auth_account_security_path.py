"""CYAN_PRODUCTION_ROOT_CUTOVER propagation (2026-10-04): the deployed frontend's
account-security location is a frontend-owned fact, so the fallback target of
an ACCOUNT_LINK projection (24 §14.4–14.5; §11.17) is runtime-configured
(`NQUIRY_ACCOUNT_SECURITY_PATH`), default `/account/security` (the AUTH-line
web). The product frontend presents links on `/workspaces`.

MUST BECOME TRUE: with the setting, a link started without `next` returns to
the configured location; a link callback whose transaction cannot be bound
(purpose mismatch, no binding) projects its failure there; a bound `next`
still wins. MUST REMAIN IMPOSSIBLE: a non-local value at startup; a changed
default; any effect of the setting on LOGIN projections.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import ACCOUNT_SECURITY_DESTINATION, configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from security.oidc_test_issuer import LocalTestIssuer
from test_auth_wu10_account_linking import _link_callback, _link_start, _local_user, _login

_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_ACCOUNT_SECURITY_PATH": "/workspaces",
}


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

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def test_the_default_is_the_auth_line_location_and_a_non_local_value_is_refused() -> None:
    assert auth_runtime_from_environment({}).account_security_path == ACCOUNT_SECURITY_DESTINATION
    assert ACCOUNT_SECURITY_DESTINATION == "/account/security"
    assert auth_runtime_from_environment(
        {"NQUIRY_ACCOUNT_SECURITY_PATH": "  "}
    ).account_security_path == ("/account/security")
    for bad in ("https://evil.example/", "//evil.example", "workspaces", "/x\\y", "/%00"):
        with pytest.raises(ValueError):
            auth_runtime_from_environment({"NQUIRY_ACCOUNT_SECURITY_PATH": bad})


def test_a_link_started_without_next_returns_to_the_configured_location(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    code = issuer.authorize(params, subject="configured-fallback")
    response = _link_callback(client, code=code, state=params["state"])
    assert response.status_code == 303
    assert response.headers["location"] == "/workspaces?link=ok"


def test_a_bound_next_still_wins_over_the_configured_location(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client, next="/workspaces/abc?tab=access")
    assert params is not None
    code = issuer.authorize(params, subject="bound-next")
    response = _link_callback(client, code=code, state=params["state"])
    assert response.headers["location"] == "/workspaces/abc?tab=access&link=ok"


def test_an_unbindable_link_callback_projects_its_failure_to_the_configured_location(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    login_start = client.get("/auth/oidc/test/start")
    login_params = {
        k: v[0] for k, v in parse_qs(urlparse(login_start.headers["location"]).query).items()
    }
    code = issuer.authorize(login_params, subject="purpose-crossed")
    crossed = _link_callback(client, code=code, state=login_params["state"])
    assert crossed.headers["location"] == "/workspaces?link=failed"
    # the LOGIN projection base is untouched by the setting
    assert http_oidc.LOGIN_PROJECTION_BASE == "/login?auth="
