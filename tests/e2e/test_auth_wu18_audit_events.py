"""WU-AUTH-18: authentication audit events (24 §31.1–31.3; §47 item 24).

MUST BECOME TRUE: every human-facing authentication effect that had no
SecurityEvent yet records one in the transaction of its effect — local login
success and failure, logout, one-session and all-session revocation, the
provider protocol's start, cancel, rejection and failure, the provider
login's success and its account-creation refusal.

MUST REMAIN IMPOSSIBLE: a value in an event (password, session token, state,
nonce, code, e-mail, subject); an account named by a failed login; an event
for a no-op (logout without a session, revoke of an unknown id); an event
without a declared environment; an event type outside the closed vocabulary.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_audit import ForbiddenAuditFact, record_auth_event
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import local_auth_sessions_table, security_events_table
from security.auth_audit import ACTOR_UNAUTHENTICATED, AuthAuditEvent
from security.events import Environment
from security.oidc_test_issuer import LocalTestIssuer
from semantic_types.ids import UserId
from test_auth_wu10_account_linking import _PASSWORD, _local_user, _login

_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
_BOOTSTRAP_ENV = {**_ENV, "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED"}
_VOCABULARY = {e.value for e in AuthAuditEvent}


@pytest.fixture
def issuer() -> LocalTestIssuer:
    return LocalTestIssuer.create()


def _client_for(
    env: dict[str, str],
    db_connection: sa.Connection,
    monkeypatch: pytest.MonkeyPatch,
    issuer: LocalTestIssuer,
) -> TestClient:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(env, test_issuer=issuer))
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    try:
        yield _client_for(_ENV, db_connection, monkeypatch, issuer)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


@pytest.fixture
def bootstrap_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    try:
        yield _client_for(_BOOTSTRAP_ENV, db_connection, monkeypatch, issuer)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


# the proof database carries rows of earlier fixtures (some dated in the future): every read is
# scoped to the
# events this test itself produced, by excluding the ids present when it started
_BASELINE: set[uuid.UUID] = set()


@pytest.fixture(autouse=True)
def _baseline(db_connection: sa.Connection) -> None:
    _BASELINE.clear()
    _BASELINE.update(db_connection.execute(sa.select(security_events_table.c.id)).scalars())


def _own_rows(db: sa.Connection) -> list[sa.RowMapping]:
    rows = db.execute(
        sa.select(security_events_table).order_by(security_events_table.c.occurred_at)
    ).mappings()
    return [row for row in rows if row["id"] not in _BASELINE]


def _events(db: sa.Connection, event_type: str) -> list[sa.RowMapping]:
    return [row for row in _own_rows(db) if row["event_type"] == event_type]


def _facts(row: sa.RowMapping) -> dict[str, object]:
    return dict(json.loads(row["observed_facts"]))


def _assert_no_value(db: sa.Connection, *values: str | None) -> None:
    """24 §31.3: none of the given secret / identifying values appears in any event column."""
    for row in _own_rows(db):
        blob = " ".join(str(v) for v in row.values() if v is not None)
        for value in values:
            if value:
                assert value not in blob, (row["event_type"], value[:4])


def _start_login(client: TestClient) -> dict[str, str]:
    response = client.get("/auth/oidc/test/start")
    assert response.status_code == 303
    return {k: v[0] for k, v in parse_qs(urlparse(response.headers["location"]).query).items()}


def _callback(client: TestClient, **query: str):  # type: ignore[no-untyped-def]
    return client.get("/auth/oidc/test/callback", params=query)


# --- local login --------------------


def test_local_login_success_records_the_identity_the_session_id_and_no_value(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    token = _login(client, email)
    rows = _events(db_connection, "LOGIN_SUCCEEDED")
    assert len(rows) == 1
    row = rows[0]
    assert row["actor_type"] == "HUMAN_USER" and row["actor_id"] == str(user_id.value)
    assert row["target_ref"] == f"user:{user_id.value}" and row["environment"] == "TEST"
    facts = _facts(row)
    assert (
        set(facts) == {"method", "sessionId", "expiresAt"} and facts["method"] == "LOCAL_PASSWORD"
    )
    session_row = db_connection.execute(
        sa.select(local_auth_sessions_table.c.id).where(
            local_auth_sessions_table.c.user_id == user_id.value
        )
    ).scalar_one()
    assert facts["sessionId"] == str(session_row)
    _assert_no_value(db_connection, token, _PASSWORD, email)


def test_local_login_failure_is_aggregated_safely_no_account_no_address(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    wrong = client.post("/auth/login", json={"email": email, "password": "not it"})
    unknown = client.post(
        "/auth/login", json={"email": "nobody@example.test", "password": "not it"}
    )
    assert wrong.status_code == 401 and unknown.status_code == 401
    rows = _events(db_connection, "LOGIN_FAILED")
    assert len(rows) == 2
    for row in rows:
        assert row["actor_type"] == ACTOR_UNAUTHENTICATED
        assert row["actor_id"] == ACTOR_UNAUTHENTICATED.lower()
        assert row["target_ref"] is None and row["audit_linkage"] is None
        assert _facts(row) == {"method": "LOCAL_PASSWORD", "reason": "INVALID_CREDENTIALS"}
    # the two failures are indistinguishable (non-enumeration), and name no account
    assert _facts(rows[0]) == _facts(rows[1])
    _assert_no_value(db_connection, email, "nobody@example.test", "not it", str(user_id.value))
    assert _events(db_connection, "LOGIN_SUCCEEDED") == []


# --- logout and revocation --------------------


def test_logout_records_once_and_a_no_op_logout_records_nothing(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    token = _login(client, email)
    assert client.post("/auth/logout").status_code == 200
    assert client.post("/auth/logout").status_code == 200  # no live session: no event
    client.cookies.delete(SESSION_COOKIE_NAME)
    assert client.post("/auth/logout").status_code == 200
    rows = _events(db_connection, "LOGOUT")
    assert len(rows) == 1
    assert rows[0]["actor_id"] == str(user_id.value)
    assert _facts(rows[0]) == {"session": f"local-session:{_session_id(db_connection, user_id)}"}
    _assert_no_value(db_connection, token)


def test_revoking_one_session_and_all_sessions_record_their_scope(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    first = _login(client, email)
    other = TestClient(app, follow_redirects=False)
    other_token = _login(other, email)
    client.cookies.set(SESSION_COOKIE_NAME, first)
    sessions = client.get("/auth/sessions").json()["sessions"]
    foreign = [s for s in sessions if not s["current"]][0]["sessionId"]
    assert client.post(f"/auth/sessions/{foreign}/revoke").status_code == 200
    assert client.post(f"/auth/sessions/{uuid.uuid4()}/revoke").status_code == 404  # no event
    revoked = _events(db_connection, "SESSION_REVOKED")
    assert len(revoked) == 1
    assert _facts(revoked[0]) == {"revokedSessionId": foreign, "currentSessionEnded": False}
    assert client.post("/auth/logout-all").status_code == 200
    everything = _events(db_connection, "ALL_SESSIONS_REVOKED")
    assert len(everything) == 1 and everything[0]["actor_id"] == str(user_id.value)
    assert _facts(everything[0])["revokedSessions"] == 1
    assert client.post("/auth/logout-all").status_code == 401  # no session: no event
    assert len(_events(db_connection, "ALL_SESSIONS_REVOKED")) == 1
    _assert_no_value(db_connection, first, other_token)


# --- provider protocol --------------------


def test_provider_login_start_success_and_cancel_record_ids_and_classes_only(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    # bind the subject by a link so the LOGIN resolves to the identity (LINKED case)
    _login(client, email)
    link = client.post("/auth/oidc/test/link/start", params={"next": "/workspaces"})
    link_params = {k: v[0] for k, v in parse_qs(urlparse(link.headers["location"]).query).items()}
    code = issuer.authorize(link_params, subject="audited-subject")
    assert (
        client.get(
            "/auth/oidc/test/link/callback", params={"code": code, "state": link_params["state"]}
        ).status_code
        == 303
    )
    started_link = _events(db_connection, "PROVIDER_LINK_STARTED")
    assert len(started_link) == 1 and started_link[0]["actor_id"] == str(user_id.value)
    assert set(_facts(started_link[0])) == {"provider", "transactionId"}
    client.post("/auth/logout")
    client.cookies.clear()

    params = _start_login(client)
    started = _events(db_connection, "PROVIDER_LOGIN_STARTED")
    assert len(started) == 1 and started[0]["actor_type"] == ACTOR_UNAUTHENTICATED
    assert started[0]["target_ref"] == f"oidc-transaction:{_facts(started[0])['transactionId']}"
    code = issuer.authorize(params, subject="audited-subject")
    done = _callback(client, code=code, state=params["state"])
    assert done.status_code == 303 and SESSION_COOKIE_NAME in done.cookies
    succeeded = _events(db_connection, "PROVIDER_LOGIN_SUCCEEDED")
    assert len(succeeded) == 1 and succeeded[0]["actor_id"] == str(user_id.value)
    facts = _facts(succeeded[0])
    assert set(facts) == {"provider", "transactionId", "methodId"}
    assert facts["transactionId"] == _facts(started[0])["transactionId"]

    cancelled_params = _start_login(client)
    assert (
        _callback(client, error="access_denied", state=cancelled_params["state"]).headers[
            "location"
        ]
        == "/login?auth=cancelled"
    )
    cancelled = _events(db_connection, "OIDC_TRANSACTION_CANCELLED")
    assert len(cancelled) == 1
    assert _facts(cancelled[0]) == {"provider": "test", "purpose": "LOGIN", "reason": "USER_CANCEL"}
    _assert_no_value(
        db_connection,
        params["state"],
        params.get("nonce"),
        code,
        cancelled_params["state"],
        done.cookies.get(SESSION_COOKIE_NAME),
        "audited-subject",
        email,
    )


def test_a_replayed_callback_and_an_unknown_state_record_their_rejection_class(
    db_connection: sa.Connection, bootstrap_client: TestClient, issuer: LocalTestIssuer
) -> None:
    params = _start_login(bootstrap_client)
    code = issuer.authorize(params, subject="replayed", email="replayed@provider.test")
    first = _callback(bootstrap_client, code=code, state=params["state"])
    assert first.status_code == 303 and SESSION_COOKIE_NAME in first.cookies
    assert _events(db_connection, "OIDC_TRANSACTION_FAILED") == []
    replay = _callback(bootstrap_client, code=code, state=params["state"])
    assert replay.headers["location"] == "/login?auth=failed"
    failed = _events(db_connection, "OIDC_TRANSACTION_FAILED")
    assert len(failed) == 1
    facts = _facts(failed[0])
    assert facts == {"provider": "test", "purpose": "LOGIN", "reason": "ALREADY_COMPLETED"}
    # an unknown state is a rejection too (never silent)
    assert (
        _callback(bootstrap_client, code="x", state="unknown-state").headers["location"]
        == "/login?auth=failed"
    )
    rejected = _events(db_connection, "OIDC_TRANSACTION_FAILED")
    assert len(rejected) == 2 and _facts(rejected[1])["reason"] == "MISSING_TRANSACTION"
    _assert_no_value(
        db_connection, params["state"], code, "unknown-state", "replayed@provider.test"
    )


def test_an_unbound_subject_under_denied_policy_records_the_unavailable_class(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    params = _start_login(client)
    code = issuer.authorize(params, subject="stranger", email="stranger@provider.test")
    response = _callback(client, code=code, state=params["state"])
    assert response.headers["location"] == "/login?auth=unavailable"
    unavailable = _events(db_connection, "PROVIDER_LOGIN_UNAVAILABLE")
    assert len(unavailable) == 1 and unavailable[0]["actor_type"] == ACTOR_UNAUTHENTICATED
    assert _facts(unavailable[0])["reason"] == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    failed = _events(db_connection, "OIDC_TRANSACTION_FAILED")
    assert len(failed) == 1 and _facts(failed[0])["reason"] == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    assert _events(db_connection, "PROVIDER_LOGIN_SUCCEEDED") == []
    _assert_no_value(db_connection, "stranger", "stranger@provider.test", params["state"], code)


def test_a_bootstrapped_login_records_success_next_to_identity_created(
    db_connection: sa.Connection, bootstrap_client: TestClient, issuer: LocalTestIssuer
) -> None:
    params = _start_login(bootstrap_client)
    code = issuer.authorize(params, subject="newcomer", email="newcomer@provider.test")
    response = _callback(bootstrap_client, code=code, state=params["state"])
    assert response.status_code == 303 and SESSION_COOKIE_NAME in response.cookies
    created = _events(db_connection, "IDENTITY_CREATED")
    succeeded = _events(db_connection, "PROVIDER_LOGIN_SUCCEEDED")
    assert len(created) == 1 and len(succeeded) == 1
    assert succeeded[0]["actor_id"] == created[0]["target_ref"].removeprefix("user:")
    _assert_no_value(db_connection, "newcomer@provider.test", params["state"], code)


# --- the writer's own laws --------------------


def test_every_recorded_event_type_is_in_the_closed_vocabulary(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    client.post("/auth/logout")
    params = _start_login(client)
    _callback(client, error="access_denied", state=params["state"])
    types = {row["event_type"] for row in _own_rows(db_connection)}
    assert types <= _VOCABULARY | {"AUTH_METHOD_LINKED", "AUTH_METHOD_UNLINKED", "IDENTITY_CREATED"}
    assert {
        "LOGIN_SUCCEEDED",
        "LOGOUT",
        "PROVIDER_LOGIN_STARTED",
        "OIDC_TRANSACTION_CANCELLED",
    } <= types


def test_the_writer_refuses_forbidden_keys_and_secret_values_and_needs_an_environment(
    db_connection: sa.Connection,
) -> None:
    now = datetime.now(timezone.utc)
    actor = UserId(uuid.uuid4())
    with pytest.raises(ForbiddenAuditFact):
        record_auth_event(
            db_connection,
            AuthAuditEvent.LOGOUT,
            environment=Environment.TEST,
            now=now,
            actor=actor,
            facts={"email": "x@example.test"},
        )
    with pytest.raises(ForbiddenAuditFact):
        record_auth_event(
            db_connection,
            AuthAuditEvent.LOGOUT,
            environment=Environment.TEST,
            now=now,
            actor=actor,
            facts={"session": "local-session:tok-123"},
            never=("tok-123",),
        )
    assert (
        record_auth_event(
            db_connection,
            AuthAuditEvent.LOGOUT,
            environment=None,
            now=now,
            actor=actor,
            facts={"session": "s"},
        )
        is False
    )
    assert _events(db_connection, "LOGOUT") == []
    assert record_auth_event(
        db_connection,
        AuthAuditEvent.LOGOUT,
        environment=Environment.TEST,
        now=now,
        actor=actor,
        facts={"session": "s"},
    )
    assert len(_events(db_connection, "LOGOUT")) == 1


def _session_id(db: sa.Connection, user_id: UserId) -> uuid.UUID:
    return db.execute(
        sa.select(local_auth_sessions_table.c.id).where(
            local_auth_sessions_table.c.user_id == user_id.value
        )
    ).scalar_one()
