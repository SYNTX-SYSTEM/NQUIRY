"""T9 SECURITY: the runtime DB principal of authentication persistence
(24 §21.18; WU-AUTH-17; FBR-AUTH-006).

Proven against a live PostgreSQL with `infra/local/db_roles.sql` run and the
migrations applied, over REAL connections authenticated AS `auth_runtime`
(never the bootstrap owner asking on its behalf):

- the capability map is explicit (`security.db_capabilities`) and the
  principal holds exactly it — every table of the database, every privilege;
- unauthorized operations fail for real (business tables, DELETE anywhere,
  reading the audit it may only append to);
- the live HTTP authentication paths all work when their persistence runs as
  that principal: login, session management, provider first login (account
  creation), link, email verification, recovery, unlink, account disable;
- the business principals can resolve a session (the one auth read every
  governed request makes) and nothing more of the auth relations;
- bootstrap / test authority is never represented as runtime authority: the
  runtime declares SCOPED only when a scoped auth connector is configured.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
from application.account_disable import disable_identity_by_host_operator
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import configure_auth_runtime
from application.identity_provisioning import HostOperator
from application.request_security import (
    configure_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence import engine as engine_module
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import users_table
from security.db_capabilities import (
    AUTH_PERSISTENCE_CAPABILITIES,
    AUTH_RUNTIME_PRINCIPAL,
    SESSION_RESOLUTION_READ_TABLES,
    SESSION_RESOLVING_PRINCIPALS,
)
from security.events import Environment
from security.identity import ServicePrincipal
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.oidc_test_issuer import LocalTestIssuer
from security.request_security import RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE")
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
    "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
}


def _principal_engine(db_connection: sa.Connection, principal: str) -> sa.Engine:
    url = db_connection.engine.url.set(username=principal, password=f"{principal}_local_dev_only")
    return sa.create_engine(url)


def _all_tables(db: sa.Connection) -> list[str]:
    return [
        row[0]
        for row in db.execute(
            sa.text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                "AND tablename <> 'alembic_version' ORDER BY tablename"
            )
        )
    ]


def _privileges(engine: sa.Engine, table: str) -> frozenset[str]:
    with engine.connect() as conn:
        return frozenset(
            privilege
            for privilege in _PRIVILEGES
            if conn.execute(
                sa.text("SELECT has_table_privilege(current_user, :table, :privilege)"),
                {"table": table, "privilege": privilege},
            ).scalar_one()
        )


# --------------------------------------------------------- the capability map


def test_the_auth_runtime_principal_exists_is_declared_and_is_no_superuser(
    db_connection: sa.Connection,
) -> None:
    assert AUTH_RUNTIME_PRINCIPAL == "auth_runtime"
    assert ServicePrincipal.AUTH_RUNTIME.value == AUTH_RUNTIME_PRINCIPAL
    row = (
        db_connection.execute(
            sa.text(
                "SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls, rolcanlogin "
                "FROM pg_roles WHERE rolname = :n"
            ),
            {"n": AUTH_RUNTIME_PRINCIPAL},
        )
        .mappings()
        .one()
    )
    assert row["rolcanlogin"] is True
    assert not (
        row["rolsuper"] or row["rolcreatedb"] or row["rolcreaterole"] or row["rolbypassrls"]
    )


def test_the_capability_map_names_only_authentication_relations_and_never_delete() -> None:
    assert set(AUTH_PERSISTENCE_CAPABILITIES) == {
        "users",
        "local_auth_credentials",
        "local_auth_sessions",
        "authentication_methods",
        "external_provider_identities",
        "oidc_auth_transactions",
        "auth_challenges",
        "verified_emails",
        "recovery_challenges",
        "security_events",
    }
    for table, privileges in AUTH_PERSISTENCE_CAPABILITIES.items():
        assert "DELETE" not in privileges, table  # revocation preserves evidence (24 §18.3)
    assert AUTH_PERSISTENCE_CAPABILITIES["security_events"] == frozenset({"INSERT"})
    assert set(SESSION_RESOLUTION_READ_TABLES) == {
        "local_auth_sessions",
        "authentication_methods",
        "users",
    }
    assert set(SESSION_RESOLVING_PRINCIPALS) == {"api_reader", "governed_commit_writer"}


def test_the_principal_holds_exactly_the_declared_capabilities_over_every_table(
    db_connection: sa.Connection,
) -> None:
    engine = _principal_engine(db_connection, AUTH_RUNTIME_PRINCIPAL)
    actual = {table: _privileges(engine, table) for table in _all_tables(db_connection)}
    expected = {table: AUTH_PERSISTENCE_CAPABILITIES.get(table, frozenset()) for table in actual}
    assert actual == expected, {
        t: (sorted(actual[t]), sorted(expected[t])) for t in actual if actual[t] != expected[t]
    }


def test_business_principals_may_resolve_a_session_and_touch_no_other_auth_relation(
    db_connection: sa.Connection,
) -> None:
    auth_tables = set(AUTH_PERSISTENCE_CAPABILITIES) - {"users", "security_events"}
    for principal in SESSION_RESOLVING_PRINCIPALS:
        engine = _principal_engine(db_connection, principal)
        for table in SESSION_RESOLUTION_READ_TABLES:
            assert "SELECT" in _privileges(engine, table), (principal, table)
        for table in auth_tables - SESSION_RESOLUTION_READ_TABLES:
            assert _privileges(engine, table) == frozenset(), (principal, table)
        for table in auth_tables:
            assert not _privileges(engine, table) & {"INSERT", "UPDATE", "DELETE"}, (
                principal,
                table,
            )


# ---------------------------------------------------------- negative capability


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO workspaces DEFAULT VALUES",
        "SELECT 1 FROM workspaces LIMIT 1",
        "SELECT 1 FROM questions LIMIT 1",
        "SELECT 1 FROM decisions LIMIT 1",
        "SELECT 1 FROM audit_events LIMIT 1",
        "SELECT 1 FROM security_events LIMIT 1",
        "DELETE FROM local_auth_sessions",
        "DELETE FROM users",
        "DELETE FROM authentication_methods",
        "DELETE FROM external_provider_identities",
        "DELETE FROM recovery_challenges",
        "UPDATE security_events SET event_type = 'x'",
        "INSERT INTO workspace_memberships DEFAULT VALUES",
        "INSERT INTO human_authority_bindings DEFAULT VALUES",
    ],
)
def test_operations_outside_the_capability_set_fail_for_real(
    db_connection: sa.Connection, statement: str
) -> None:
    engine = _principal_engine(db_connection, AUTH_RUNTIME_PRINCIPAL)
    with engine.connect() as conn, pytest.raises(sa.exc.DBAPIError, match="permission denied"):
        conn.execute(sa.text(statement))
        conn.rollback()


# ------------------------------------------------- the live path, scoped


@pytest.fixture
def scoped(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[TestClient, sa.Connection, LocalTestIssuer, LocalMailCapture]]:
    """The real HTTP app with every authentication persistence path running
    as `auth_runtime` (a real connection of that principal, rolled back at
    the end), and the scoped auth connector declared."""
    engine = _principal_engine(db_connection, AUTH_RUNTIME_PRINCIPAL)
    connection = engine.connect()
    outer = connection.begin()

    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with connection.begin_nested():
            yield connection

    monkeypatch.setenv("NQUIRY_AUTH_DATABASE_URL", str(engine.url))
    monkeypatch.setattr(engine_module, "_auth_engine", None)
    monkeypatch.setattr(http_dispatch, "connect_auth", _reuse)
    for module in (http_oidc, http_email, http_recovery, http_revocation):
        monkeypatch.setattr(module, "connect", _reuse)
    issuer = LocalTestIssuer.create()
    mail = LocalMailCapture()
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=mail))
    configure_request_security(RequestSecurityPolicy(allowed_origins=("http://localhost:3000",)))
    try:
        yield TestClient(app, follow_redirects=False), connection, issuer, mail
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))
        outer.rollback()
        connection.close()
        engine.dispose()


def _local_user(db: sa.Connection) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Scoped",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def test_every_live_authentication_path_works_under_the_scoped_principal(
    scoped: tuple[TestClient, sa.Connection, LocalTestIssuer, LocalMailCapture],
) -> None:
    client, db, issuer, mail = scoped
    assert engine_module.auth_persistence_scope() == "SCOPED"
    with db.begin_nested():
        _, email = _local_user(db)

    # local login, session management
    assert (
        client.post("/auth/login", json={"email": email, "password": _PASSWORD}).status_code == 200
    )
    assert client.get("/auth/me").json()["kind"] == "ok"
    assert client.get("/auth/sessions").json()["kind"] == "ok"
    # email verification + recovery
    challenge = client.post("/auth/email/verification/start", json={"email": email}).json()
    assert challenge["kind"] == "ok"
    assert (
        client.post(
            "/auth/email/verification/complete",
            json={"challengeId": challenge["challengeId"], "token": mail.outbox[-1].token},
        ).status_code
        == 200
    )
    # provider link + unlink
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    linked = client.get(
        "/auth/oidc/test/link/callback",
        params={"code": issuer.authorize(params, subject="scoped-link"), "state": params["state"]},
    )
    assert linked.headers["location"] == "/account/security?link=ok"
    methods = client.get("/auth/methods").json()["methods"]
    (provider_method,) = [m for m in methods if m["methodType"] == "TEST_PROVIDER"]
    assert client.post(f"/auth/methods/{provider_method['methodId']}/unlink").status_code == 200
    assert client.post("/auth/logout-all").status_code == 200
    assert client.get("/auth/me").status_code == 401
    assert client.post("/auth/recovery/start", json={"email": email}).json() == {"kind": "ok"}
    delivered = mail.outbox[-1]
    assert (
        client.post(
            "/auth/recovery/complete",
            json={
                "recoveryId": delivered.challenge_id,
                "token": delivered.token,
                "newPassword": "a brand new passphrase 2030",
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/auth/login", json={"email": email, "password": "a brand new passphrase 2030"}
        ).status_code
        == 200
    )
    # provider first login creates an identity (TEST policy)
    other = TestClient(app, follow_redirects=False)
    start = other.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    created = other.get(
        "/auth/oidc/test/callback",
        params={
            "code": issuer.authorize(params, subject="scoped-new", email="scoped-new@example.test"),
            "state": params["state"],
        },
    )
    assert created.headers["location"] == "/workspaces"
    # account disable through the same principal
    with db.begin_nested():
        outcome = disable_identity_by_host_operator(
            db,
            email=email,
            operator=HostOperator(operator_id="otti@condyn.eu", os_user="codi", host="h"),
            reason="scoped proof",
            environment=Environment.TEST,
            now=datetime.now(timezone.utc),
        )
    assert outcome.sessions_revoked >= 1
    assert client.get("/auth/me").status_code == 401


def test_the_scoped_principal_cannot_build_or_read_business_state(
    scoped: tuple[TestClient, sa.Connection, LocalTestIssuer, LocalMailCapture],
) -> None:
    _, db, _, _ = scoped
    with pytest.raises(sa.exc.DBAPIError, match="permission denied"), db.begin_nested():
        db.execute(sa.text("SELECT count(*) FROM workspaces"))


# ------------------------------------------------ bootstrap != runtime authority


def test_the_runtime_declares_scoped_only_when_a_scoped_connector_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NQUIRY_AUTH_DATABASE_URL", raising=False)
    monkeypatch.setattr(engine_module, "_auth_engine", None)
    assert engine_module.auth_persistence_scope() == "UNSCOPED_BOOTSTRAP"
    monkeypatch.setenv(
        "NQUIRY_AUTH_DATABASE_URL", "postgresql+psycopg://auth_runtime:x@localhost/db"
    )
    assert engine_module.auth_persistence_scope() == "SCOPED"
    monkeypatch.setenv("NQUIRY_AUTH_DATABASE_URL", "   ")
    assert engine_module.auth_persistence_scope() == "UNSCOPED_BOOTSTRAP"


def test_the_auth_connector_falls_back_to_the_request_connector_only_when_unscoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NQUIRY_AUTH_DATABASE_URL", raising=False)
    monkeypatch.setattr(engine_module, "_auth_engine", None)
    assert engine_module.auth_scope_configured() is False
    monkeypatch.setenv(
        "NQUIRY_AUTH_DATABASE_URL", "postgresql+psycopg://auth_runtime:x@localhost/db"
    )
    assert engine_module.auth_scope_configured() is True
