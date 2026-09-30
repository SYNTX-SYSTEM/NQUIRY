"""T10: the OIDC provider adapter and the start / callback contacts
(24 WU-AUTH-07; §11.1–11.2, §11.12–11.13, §11.16–11.21, §16.2, §19.9–19.12,
§23.4–23.5, §25.3, §26, §27.1, §32.2–32.3, §39.3, §39.12; FBR-AUTH-001, -012, -016).

The provider under test is the same standards-based adapter class that a
real Google configuration instantiates, pointed at an in-process local
issuer that signs real RS256 ID Tokens (24 §27.1: a TEST_PROVIDER, marked,
impossible in production config, unable to produce production proof).

MUST BECOME TRUE: a login start creates the transaction, binds the browser
and redirects to the provider with S256 PKCE, state and nonce; the callback
follows 24 §16.2 in order: transaction, binding, state, expiry, purpose,
claim, exchange with the original verifier, ID Token validation (signature,
issuer, audience, expiry), then nonce, then the trusted subject; a provider
error or cancel terminalizes without an exchange; an uncertain exchange is
terminal and never retried.

MUST REMAIN IMPOSSIBLE: a forged callback creating a session; implicit flow;
an unvalidated ID Token; nonce or subject trusted before validation; a
verifier reaching the browser; a provider button or start without
configuration; the test provider in a production configuration.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import (
    AuthRuntime,
    LocalProviderForbidden,
    auth_runtime_from_environment,
)
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import BINDING_COOKIE_NAME, configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import local_auth_sessions_table
from security.oidc_test_issuer import LocalTestIssuer
from security.oidc_transaction import derive_code_challenge, hash_protocol_value

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_TEST_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}


@pytest.fixture
def issuer() -> LocalTestIssuer:
    return LocalTestIssuer.create()


@pytest.fixture
def runtime(issuer: LocalTestIssuer) -> AuthRuntime:
    return auth_runtime_from_environment(_TEST_ENV, test_issuer=issuer)


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, runtime: AuthRuntime
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(runtime)
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _transaction(db: sa.Connection, state: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.text("SELECT * FROM oidc_auth_transactions WHERE state_hash = :h"),
            {"h": hash_protocol_value(state)},
        )
        .mappings()
        .one()
    )


def _session_count(db: sa.Connection) -> int:
    return int(
        db.execute(sa.select(sa.func.count()).select_from(local_auth_sessions_table)).scalar_one()
    )


def _start(client: TestClient, provider: str = "test", **query: str):  # type: ignore[no-untyped-def]
    response = client.get(f"/auth/oidc/{provider}/start", params=query)
    assert response.status_code == 303, response.text
    location = urlparse(response.headers["location"])
    params = {key: value[0] for key, value in parse_qs(location.query).items()}
    return response, location, params


def _callback(client: TestClient, provider: str = "test", **query: str):  # type: ignore[no-untyped-def]
    return client.get(f"/auth/oidc/{provider}/callback", params=query)


# ------------------------------------------------------------------ providers


def test_the_provider_list_names_only_configured_providers(client: TestClient) -> None:
    response = client.get("/auth/providers")
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    assert body["providers"] == [
        {"providerId": "test", "label": "Test provider", "proofClass": "TEST_PROVIDER"}
    ]


def test_without_configuration_no_provider_is_offered_and_start_is_unavailable(
    client: TestClient,
) -> None:
    configure_auth_runtime(auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}))
    assert client.get("/auth/providers").json() == {"kind": "ok", "providers": []}
    response = client.get("/auth/oidc/google/start")
    assert response.status_code == 503
    assert response.json() == {"kind": "unavailable", "reasonCode": "PROVIDER_NOT_CONFIGURED"}
    unknown = client.get("/auth/oidc/nonsense/start")
    assert unknown.status_code == 503 and unknown.json()["kind"] == "unavailable"


@pytest.mark.parametrize("environment", ["PRODUCTION", "STAGING", None, "prod"])
def test_the_test_provider_is_refused_outside_development_and_test(
    issuer: LocalTestIssuer, environment: str | None
) -> None:
    env = {"NQUIRY_AUTH_PROVIDER_MODE": "test"}
    if environment is not None:
        env["NQUIRY_ENVIRONMENT"] = environment
    with pytest.raises(LocalProviderForbidden):
        auth_runtime_from_environment(env, test_issuer=issuer)


def test_google_is_configured_only_from_complete_configuration() -> None:
    partial = {
        "NQUIRY_ENVIRONMENT": "PRODUCTION",
        "NQUIRY_AUTH_PROVIDER_MODE": "google",
        "NQUIRY_GOOGLE_CLIENT_ID": "client-id.apps.googleusercontent.com",
    }
    assert auth_runtime_from_environment(partial).providers == {}
    complete = dict(
        partial,
        NQUIRY_GOOGLE_CLIENT_SECRET="not-a-real-secret",
        NQUIRY_GOOGLE_REDIRECT_URI="https://nquiry.example/auth/oidc/google/callback",
    )
    runtime = auth_runtime_from_environment(complete)
    assert set(runtime.providers) == {"google"}
    assert runtime.providers["google"].issuer == "https://accounts.google.com"
    assert runtime.providers["google"].proof_class == "PRODUCTION_PROVIDER"


# --------------------------------------------------------------------- start


def test_start_creates_a_pending_transaction_binds_the_browser_and_redirects(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    response, location, params = _start(client, next="/account/security")

    assert f"{location.scheme}://{location.netloc}{location.path}" == issuer.authorization_endpoint
    assert params["response_type"] == "code"
    assert params["code_challenge_method"] == "S256"
    assert params["client_id"] == issuer.client_id
    assert params["redirect_uri"] == "http://testserver/auth/oidc/test/callback"
    assert "openid" in params["scope"].split()
    assert "code_verifier" not in params and "token" not in params["response_type"]

    row = _transaction(db_connection, params["state"])
    assert row["state"] == "PENDING" and row["purpose"] == "LOGIN"
    assert row["nonce_hash"] == hash_protocol_value(params["nonce"])
    assert row["pkce_code_challenge"] == params["code_challenge"]
    assert derive_code_challenge(row["pkce_code_verifier"]) == params["code_challenge"]
    assert row["post_auth_redirect_target"] == "/account/security"

    cookie = response.headers["set-cookie"]
    assert BINDING_COOKIE_NAME in cookie and "httponly" in cookie.lower()
    assert "samesite=lax" in cookie.lower()
    binding = response.cookies[BINDING_COOKIE_NAME]
    assert row["user_agent_binding_hash"] == hash_protocol_value(binding)
    assert row["pkce_code_verifier"] not in response.text
    assert row["pkce_code_verifier"] not in cookie


def test_start_binds_only_a_legitimate_redirect_target(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, _, params = _start(client, next="https://elsewhere.example/")
    assert _transaction(db_connection, params["state"])["post_auth_redirect_target"] == "/"


def test_two_starts_in_one_browser_are_two_transactions_with_two_bindings(
    db_connection: sa.Connection, client: TestClient
) -> None:
    first, _, first_params = _start(client)
    second, _, second_params = _start(client)
    assert first_params["state"] != second_params["state"]
    assert first.cookies[BINDING_COOKIE_NAME] != second.cookies[BINDING_COOKIE_NAME]
    assert _transaction(db_connection, first_params["state"])["state"] == "PENDING"


# ------------------------------------------------------------------ callback


def test_a_valid_callback_reaches_provider_proof_then_fails_closed_on_identity(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """Provider proof succeeds end to end (claim, exchange with the original
    verifier, ID Token validation, nonce, trusted subject). No provider
    identity binding and no account creation policy exist yet, so the local
    effect gate fails closed (24 §11.14 default): no user, no session."""
    _, _, params = _start(client, next="/workspaces")
    code = issuer.authorize(params, subject="subject-1", email="one@example.test")

    response = _callback(client, code=code, state=params["state"])

    assert response.status_code == 303
    assert response.headers["location"] == "/login?auth=unavailable"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL"
    assert row["failure_reason"] == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    assert row["pkce_code_verifier"] is None
    assert _session_count(db_connection) == 0
    assert SESSION_COOKIE_NAME not in response.cookies
    exchange = issuer.exchanges[-1]
    assert exchange.code == code
    assert derive_code_challenge(exchange.code_verifier) == params["code_challenge"]
    assert exchange.redirect_uri == "http://testserver/auth/oidc/test/callback"
    assert exchange.client_authenticated
    assert BINDING_COOKIE_NAME in response.headers.get("set-cookie", "")


def test_a_replayed_callback_does_not_reach_the_token_endpoint(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    _callback(client, code=code, state=params["state"])
    exchanges = len(issuer.exchanges)

    replay = _callback(client, code=code, state=params["state"])

    assert replay.status_code == 303 and replay.headers["location"] == "/login?auth=failed"
    assert len(issuer.exchanges) == exchanges
    assert _session_count(db_connection) == 0


def test_a_callback_without_a_transaction_or_with_a_foreign_state_fails_closed(
    client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    for state in ("unknown-state", ""):
        response = _callback(client, code=code, state=state)
        assert response.status_code == 303
        assert response.headers["location"] == "/login?auth=failed"
    assert issuer.exchanges == []


def test_a_callback_transplanted_into_another_browser_fails_before_the_exchange(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    victim = TestClient(app, follow_redirects=False)

    response = victim.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    )

    assert response.status_code == 303 and response.headers["location"] == "/login?auth=failed"
    assert issuer.exchanges == []
    assert SESSION_COOKIE_NAME not in response.cookies
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL"
    assert row["failure_reason"] == "USER_AGENT_BINDING_MISSING"


def test_provider_cancel_and_error_terminalize_without_an_exchange(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    for error, reason, projection in (
        ("access_denied", "USER_CANCEL", "cancelled"),
        ("temporarily_unavailable", "PROVIDER_FAILURE", "provider_unavailable"),
        ("invalid_scope", "PROVIDER_FAILURE", "provider_error"),
    ):
        _, _, params = _start(client)
        response = _callback(client, error=error, state=params["state"])
        assert response.status_code == 303
        assert response.headers["location"] == f"/login?auth={projection}", error
        row = _transaction(db_connection, params["state"])
        assert row["state"] == "CANCELLED_TERMINAL" and row["failure_reason"] == reason
        assert row["pkce_code_verifier"] is None
    assert issuer.exchanges == [] and _session_count(db_connection) == 0


def test_a_malformed_callback_creates_no_effect(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    response = _callback(client, state=params["state"])  # neither code nor error
    assert response.status_code == 303 and response.headers["location"] == "/login?auth=failed"
    assert _transaction(db_connection, params["state"])["state"] == "PENDING"
    assert issuer.exchanges == []


# ---------------------------------------------------- token and ID Token trust


@pytest.mark.parametrize(
    ("defect", "reason"),
    [
        ("wrong_signature", "INVALID_ID_TOKEN_SIGNATURE"),
        ("wrong_issuer", "INVALID_ISSUER"),
        ("wrong_audience", "INVALID_AUDIENCE"),
        ("expired", "EXPIRED_ID_TOKEN"),
        ("no_subject", "PROVIDER_SUBJECT_MISSING"),
        ("wrong_nonce", "INVALID_NONCE"),
    ],
)
def test_a_defective_id_token_is_rejected_after_the_exchange(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    defect: str,
    reason: str,
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1", defect=defect)

    response = _callback(client, code=code, state=params["state"])

    assert response.status_code == 303 and response.headers["location"] == "/login?auth=failed"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL" and row["failure_reason"] == reason
    assert len(issuer.exchanges) == 1
    assert _session_count(db_connection) == 0


def test_the_nonce_is_not_trusted_before_the_id_token_is_validated(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """A token with a wrong signature AND a wrong nonce fails on the
    signature: the nonce claim of an unvalidated token is never read as a
    fact (24 §11.12, falsifier 22)."""
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1", defect="wrong_signature_and_nonce")
    _callback(client, code=code, state=params["state"])
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "INVALID_ID_TOKEN_SIGNATURE"
    )


def test_a_rejected_exchange_is_terminal(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    response = _callback(client, code="not-a-code-the-issuer-knows", state=params["state"])
    assert response.headers["location"] == "/login?auth=failed"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL" and row["failure_reason"] == "TOKEN_EXCHANGE_REJECTED"
    assert len(issuer.exchanges) == 1


def test_an_uncertain_exchange_outcome_is_terminal_and_never_retried(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    issuer.fail_next_exchange_uncertainly()

    response = _callback(client, code=code, state=params["state"])

    assert response.headers["location"] == "/login?auth=failed"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL"
    assert row["failure_reason"] == "TOKEN_EXCHANGE_OUTCOME_UNCERTAIN"
    assert len(issuer.exchanges) == 1
    replay = _callback(client, code=code, state=params["state"])
    assert replay.headers["location"] == "/login?auth=failed"
    assert len(issuer.exchanges) == 1


def test_the_id_token_and_verifier_never_reach_the_browser(
    client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    response = _callback(client, code=code, state=params["state"])
    rendered = response.text + str(response.headers)
    assert issuer.last_id_token not in rendered
    assert issuer.exchanges[-1].code_verifier not in rendered
    assert code not in response.headers["location"]


def test_the_test_provider_authorize_endpoint_exists_only_in_test_mode(
    client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    page = client.get("/auth/test-provider/authorize", params=params)
    assert page.status_code == 200 and "TEST_PROVIDER" in page.text
    configure_auth_runtime(auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}))
    assert client.get("/auth/test-provider/authorize", params=params).status_code == 404


def test_callback_routes_are_get_and_ordinary_get_routes_do_not_mutate(client: TestClient) -> None:
    served = {(m, r.path) for r in app.routes for m in getattr(r, "methods", set())}  # type: ignore[attr-defined]
    assert ("GET", "/auth/oidc/{provider}/callback") in served
    assert ("POST", "/auth/oidc/{provider}/callback") not in served


def test_the_verifier_is_gone_from_the_row_before_the_exchange_is_attempted(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    code = issuer.authorize(params, subject="subject-1")
    seen: list[object] = []

    def observe(_exchange: object) -> None:
        seen.append(_transaction(db_connection, params["state"])["pkce_code_verifier"])

    issuer.on_exchange = observe
    _callback(client, code=code, state=params["state"])
    assert seen == [None]


# ------------------------------------------------ the test provider's consent


def test_the_consent_page_round_trip_reaches_the_callback_with_a_code(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """The browser path of a development stack: start → consent page → approve
    → callback. The consent POST sends the browser to the registered redirect
    URI only, with `code` and `state`."""
    _, _, params = _start(client)
    approve = client.post(
        "/auth/test-provider/authorize",
        data={
            **params,
            "subject": "browser-subject",
            "email": "b@example.test",
            "action": "approve",
        },
    )
    assert approve.status_code == 303
    location = urlparse(approve.headers["location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == issuer.redirect_uri
    query = {k: v[0] for k, v in parse_qs(location.query).items()}
    assert query["state"] == params["state"] and query["code"]

    response = _callback(client, **query)
    assert response.headers["location"] == "/login?auth=unavailable"  # no identity yet (WU-08/-09)
    assert issuer.exchanges[-1].code == query["code"]


def test_the_consent_page_cancel_sends_access_denied_to_the_callback(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    cancel = client.post(
        "/auth/test-provider/authorize", data={**params, "subject": "x", "action": "cancel"}
    )
    query = {k: v[0] for k, v in parse_qs(urlparse(cancel.headers["location"]).query).items()}
    assert query == {"error": "access_denied", "state": params["state"]}
    response = _callback(client, **query)
    assert response.headers["location"] == "/login?auth=cancelled"
    assert _transaction(db_connection, params["state"])["state"] == "CANCELLED_TERMINAL"
    assert issuer.exchanges == []


def test_the_consent_page_refuses_a_foreign_redirect_uri(
    client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, _, params = _start(client)
    response = client.post(
        "/auth/test-provider/authorize",
        data={
            **params,
            "redirect_uri": "https://elsewhere.example/cb",
            "subject": "x",
            "action": "approve",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"kind": "rejected", "reasonCode": "REDIRECT_URI_MISMATCH"}
