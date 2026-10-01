"""T15: protocol callback semantics (24 WU-AUTH-15; §11.19; §21.14; §11.2;
§38 falsifiers 67–70; §44.8).

MUST BECOME TRUE: the OIDC callback GET is a protocol response contact whose
effects are exactly the protocol-defined security / identity effects, reached
only through the dedicated proof gates; the login start GET is a protocol
initiation contact whose only effect is the transaction; every other GET
route of the API mutates nothing; the set of protocol contacts is declared
and checked, not implied.

MUST REMAIN IMPOSSIBLE: a callback that writes outside the protocol /
identity relations (a business command, Workspace authority, membership,
role, participation, a Decision); a callback that bypasses the user-agent
binding, the claim, PKCE, ID Token validation or the creation / linking
authority and still produces a session or an identity; an ordinary GET that
mutates.

Measured by EFFECT (the full table write set), not by the projection: every
case diffs the row counts of every user table in the database.
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
import application.http_f02 as http_f02
import application.http_f04 as http_f04
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
import test_pfc_f09_2_isolation_sweep as sweep
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import (
    PROTOCOL_CALLBACK_WRITE_SET,
    PROTOCOL_CONTACTS,
    PROTOCOL_START_WRITE_SET,
    configure_auth_runtime,
)
from application.request_security import (
    configure_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import users_table
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.oidc_test_issuer import LocalTestIssuer
from security.oidc_transaction import hash_protocol_value
from security.request_security import RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
}
_IDENTITY_TABLES = {"users", "authentication_methods", "external_provider_identities"}


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

    for module in (
        http_dispatch,
        http_f02,
        http_f04,
        http_oidc,
        http_email,
        http_recovery,
        http_revocation,
    ):
        monkeypatch.setattr(module, "connect", _reuse)
    configure_auth_runtime(
        auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=LocalMailCapture())
    )
    configure_request_security(RequestSecurityPolicy(allowed_origins=("http://localhost:3000",)))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


def _all_counts(db: sa.Connection) -> dict[str, int]:
    """Row counts of EVERY user table: the write set is measured, not assumed."""
    names = [
        row[0]
        for row in db.execute(
            sa.text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                "AND tablename <> 'alembic_version' ORDER BY tablename"
            )
        )
    ]
    return {
        name: int(db.execute(sa.text(f'SELECT count(*) FROM "{name}"')).scalar_one())
        for name in names
    }


def _changed(before: dict[str, int], after: dict[str, int]) -> set[str]:
    return {name for name in after if after[name] != before.get(name)}


def _start(client: TestClient, **query: str) -> dict[str, str]:
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces", **query})
    assert start.status_code == 303
    return {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}


def _callback(client: TestClient, **query: str):  # type: ignore[no-untyped-def]
    return client.get("/auth/oidc/test/callback", params=query)


def _transaction(db: sa.Connection, state: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.text(
                "SELECT state, failure_reason FROM oidc_auth_transactions WHERE state_hash = :h"
            ),
            {"h": hash_protocol_value(state)},
        )
        .mappings()
        .one()
    )


def _local_user(db: sa.Connection) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Caller",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


# ------------------------------------------------ the declared protocol contacts


def test_the_protocol_contacts_are_declared_and_are_exactly_the_mutating_get_routes() -> None:
    """24 §11.19: the callback GET is a protocol response contact, the start
    GET a protocol initiation contact. They are declared in one place; the
    sweep below proves every other GET route writes nothing."""
    served_get = {
        r.path  # type: ignore[attr-defined]
        for r in app.routes
        if "GET" in getattr(r, "methods", set())
    }
    assert set(PROTOCOL_CONTACTS) == {
        "/auth/oidc/{provider}/start",
        "/auth/oidc/{provider}/callback",
        "/auth/oidc/{provider}/link/callback",
    }
    assert set(PROTOCOL_CONTACTS) <= served_get
    assert set(PROTOCOL_START_WRITE_SET) == {"oidc_auth_transactions"}
    assert set(PROTOCOL_CALLBACK_WRITE_SET) == {
        "oidc_auth_transactions",
        "local_auth_sessions",
        "users",
        "authentication_methods",
        "external_provider_identities",
        "security_events",
    }
    # nothing of the business / authority field is in the callback's write set
    assert not PROTOCOL_CALLBACK_WRITE_SET & set(t.name for t in sweep._PROTECTED)
    assert not PROTOCOL_CALLBACK_WRITE_SET & {
        "workspaces",
        "workspace_memberships",
        "role_assignments",
        "human_authority_bindings",
        "session_participations",
    }


def test_the_start_contact_writes_the_transaction_and_nothing_else(
    db_connection: sa.Connection, client: TestClient
) -> None:
    before = _all_counts(db_connection)
    _start(client)
    assert _changed(before, _all_counts(db_connection)) == set(PROTOCOL_START_WRITE_SET)


# ----------------------------------------- the callback's effect set, measured


def test_a_first_login_callback_writes_exactly_the_protocol_and_identity_relations(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    params = _start(client)
    code = issuer.authorize(params, subject="effect-subject", email="effect@example.test")
    before = _all_counts(db_connection)

    response = _callback(client, code=code, state=params["state"])

    assert response.status_code == 303 and response.headers["location"] == "/workspaces"
    after = _all_counts(db_connection)
    changed = _changed(before, after)
    assert changed <= set(PROTOCOL_CALLBACK_WRITE_SET), changed - set(PROTOCOL_CALLBACK_WRITE_SET)
    assert _IDENTITY_TABLES | {"local_auth_sessions", "security_events"} <= changed
    # and the created identity holds nothing: no Workspace, no membership, no role
    assert client.get("/workspaces").json()["workspaces"] == []


def test_a_returning_login_callback_writes_session_and_audit_only(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    params = _start(client)
    _callback(
        client,
        code=issuer.authorize(params, subject="return-subject", email="r@example.test"),
        state=params["state"],
    )
    client.cookies.clear()
    params = _start(client)
    code = issuer.authorize(params, subject="return-subject", email="r@example.test")
    before = _all_counts(db_connection)

    assert _callback(client, code=code, state=params["state"]).status_code == 303

    changed = _changed(before, _all_counts(db_connection))
    assert changed <= {"local_auth_sessions", "oidc_auth_transactions", "security_events"}
    assert "local_auth_sessions" in changed
    assert not changed & _IDENTITY_TABLES


def test_a_link_callback_writes_method_binding_session_rotation_and_audit_only(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    assert (
        client.post("/auth/login", json={"email": email, "password": _PASSWORD}).status_code == 200
    )
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject="link-effect")
    before = _all_counts(db_connection)

    response = client.get(
        "/auth/oidc/test/link/callback", params={"code": code, "state": params["state"]}
    )

    assert response.headers["location"] == "/account/security?link=ok"
    changed = _changed(before, _all_counts(db_connection))
    assert changed <= set(PROTOCOL_CALLBACK_WRITE_SET) - {"users"}
    assert {
        "authentication_methods",
        "external_provider_identities",
        "local_auth_sessions",
    } <= changed


# -------------------------------------------- every bypass ends without effect


def _bypass_cases() -> list[tuple[str, Any]]:
    return [
        ("no transaction", lambda c, i, p: _callback(c, code="x", state="no-such-state")),
        ("no state", lambda c, i, p: _callback(c, code=i.authorize(p, subject="s"))),
        ("no code", lambda c, i, p: _callback(c, state=p["state"])),
        (
            "no user-agent binding",
            lambda c, i, p: (
                c.cookies.clear(),
                _callback(c, code=i.authorize(p, subject="s"), state=p["state"]),
            )[1],
        ),
        (
            "foreign browser (transplanted)",
            lambda c, i, p: TestClient(app, follow_redirects=False).get(
                "/auth/oidc/test/callback",
                params={"code": i.authorize(p, subject="s"), "state": p["state"]},
            ),
        ),
        ("wrong code", lambda c, i, p: _callback(c, code="not-a-code", state=p["state"])),
        (
            "nonce tampered",
            lambda c, i, p: _callback(
                c, code=i.authorize(p, subject="s", defect="wrong_nonce"), state=p["state"]
            ),
        ),
        (
            "signature invalid",
            lambda c, i, p: _callback(
                c, code=i.authorize(p, subject="s", defect="wrong_signature"), state=p["state"]
            ),
        ),
        (
            "audience foreign",
            lambda c, i, p: _callback(
                c, code=i.authorize(p, subject="s", defect="wrong_audience"), state=p["state"]
            ),
        ),
        (
            "issuer foreign",
            lambda c, i, p: _callback(
                c, code=i.authorize(p, subject="s", defect="wrong_issuer"), state=p["state"]
            ),
        ),
        (
            "subject missing",
            lambda c, i, p: _callback(
                c, code=i.authorize(p, subject="s", defect="no_subject"), state=p["state"]
            ),
        ),
        (
            "provider error",
            lambda c, i, p: _callback(c, error="access_denied", state=p["state"]),
        ),
        (
            "link callback for a login transaction",
            lambda c, i, p: c.get(
                "/auth/oidc/test/link/callback",
                params={"code": i.authorize(p, subject="s"), "state": p["state"]},
            ),
        ),
    ]


@pytest.mark.parametrize(
    ("name", "attempt"), _bypass_cases(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_no_proof_gate_can_be_bypassed_into_a_session_or_an_identity(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    name: str,
    attempt: Any,
) -> None:
    params = _start(client)
    before = _all_counts(db_connection)
    exchanges = len(issuer.exchanges)

    response = attempt(client, issuer, params)

    assert response.status_code == 303, name
    assert response.headers["location"].startswith("/login?auth="), name
    assert "nquiry_session" not in response.cookies, name
    changed = _changed(before, _all_counts(db_connection))
    # a failed callback may write its terminal state and an audit fact,
    # never a session or an identity
    assert changed <= {"oidc_auth_transactions", "security_events"}, (name, changed)
    assert client.get("/auth/me").status_code == 401, name
    assert TestClient(app).get("/auth/me").status_code == 401
    # the transaction never returns to PENDING after a failed proof, and a
    # second attempt with the same state cannot reach the token endpoint
    row = _transaction(db_connection, params["state"])
    if row["state"] != "PENDING":
        exchanges_after = len(issuer.exchanges)
        _callback(client, code=issuer.authorize(params, subject="s"), state=params["state"])
        assert len(issuer.exchanges) == exchanges_after, name
    assert len(issuer.exchanges) <= exchanges + 1, name


# ---------------------------------------- ordinary GET routes mutate nothing


def _get_routes() -> list[str]:
    return sorted(
        r.path  # type: ignore[attr-defined]
        for r in app.routes
        if "GET" in getattr(r, "methods", set())
        and not r.path.startswith(("/docs", "/openapi", "/redoc"))  # type: ignore[attr-defined]
        and r.path not in PROTOCOL_CONTACTS  # type: ignore[attr-defined]
    )


@pytest.mark.parametrize("path", _get_routes())
def test_every_ordinary_get_route_mutates_nothing(
    db_connection: sa.Connection, client: TestClient, path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """24 §11.19 "GET / ordinary application resource != mutation command",
    as the caller with the most authority the world has (Workspace A's
    owner), measured over every table."""
    monkeypatch.setattr(http_f02, "connect", http_oidc.connect)  # the sweep's world uses it
    w = sweep._world(db_connection)
    owner = sweep._client(db_connection, w["owner"])
    world = {**w, "provider": "test", "method_id": str(uuid.uuid4())}
    url = path
    for key, value in world.items():
        url = url.replace("{" + key + "}", str(value))
    url = (
        url.replace("{workspace_id}", str(w["ws"]))
        .replace("{challenge_id}", str(w["challenge"]))
        .replace("{session_id}", str(w["session"]))
        .replace("{binding_id}", str(w["binding"]))
        .replace("{decision_id}", str(w["decision"]))
    )
    assert "{" not in url, url
    before = _all_counts(db_connection)

    response = owner.get(url)

    assert response.status_code < 500, (path, response.text)
    assert _changed(before, _all_counts(db_connection)) == set(), path
