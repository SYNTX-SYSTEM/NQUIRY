"""WU-PFC-AC1: production account creation by the host operator (HD-28 / NQ-DEC-056).

Architecture: 24 §1 / §11.14 (ACCOUNT CREATION POLICY is HUMAN_AUTHORITY_REQUIRED;
no Workspace authority is created with an identity); 04 §17 (default deny, no
fallback to a system administrator unless explicitly permitted); 11 §47
("Privileged infrastructure operations affecting production trust, credentials
… require attributable administrative identity and SecurityEvent/audit
treatment"), TB-17 Administrative Tooling ("privileged-operation security
event", "no canonical bypass"), AC-11-017 (environments); 18 (local credential
adapter: PBKDF2 hash, identity separate from credential); F02 HD-3 (dev-only
provisioning; IDENTITY != MEMBERSHIP != ROLE != AUTHORITY).

Human Authority HD-28: Option A. Account creation on PRODUCTION is an explicit
host/operator authority exercised through a server-operator command, operator
recorded as otti@condyn.eu; credential set only at
creation; no reset; no in-app admin role, Workspace-owner creation, public or
self-service registration; no automatic membership, role, governance or
Session authority; audited provenance.

FIRST BROKEN RELATION (before this Work Unit): no production-safe relation lets
a new identity come into existence (only /auth/login, /auth/logout, /auth/me;
the only provisioning path is dev-only), and the dev-only guard does not refuse
a PRODUCTION environment whose database host is named `postgres`.
"""

from __future__ import annotations

import io
import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import f02_support as f02
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import (
    human_authority_bindings_table,
    local_auth_credentials_table,
    role_assignments_table,
    security_events_table,
    session_participations_table,
    users_table,
    workspace_memberships_table,
)

db_app = http_f02.db_app
OPERATOR = "otti@condyn.eu"
PASSWORD = "Review-Pass-7f3K9q2LmX"
PROD = {"NQUIRY_ENVIRONMENT": "PRODUCTION"}


def _run(
    db: sa.Connection,
    *args: str,
    password: str = PASSWORD,
    environ: dict[str, str] | None = None,
    stdout: io.StringIO | None = None,
    stderr: io.StringIO | None = None,
) -> int:
    from nquiry_api.operator import create_identity

    @contextmanager
    def _connect() -> Iterator[sa.Connection]:
        with db.begin_nested():
            yield db

    return create_identity.main(
        list(args),
        stdin=io.StringIO(password + "\n"),
        environ=PROD if environ is None else environ,
        connect=_connect,
        stdout=stdout or io.StringIO(),
        stderr=stderr or io.StringIO(),
    )


def _create(db: sa.Connection, email: str = "livereview-ravi@condyn.eu", **kw: Any) -> int:
    return _run(db, "--email", email, "--name", "LIVE REVIEW Ravi", "--operator", OPERATOR, **kw)


def _user(db: sa.Connection, email: str) -> Any:
    return (
        db.execute(sa.select(users_table).where(users_table.c.email == email))
        .mappings()
        .one_or_none()
    )


def _count(db: sa.Connection, table: sa.Table, **where: Any) -> int:
    stmt = sa.select(sa.func.count()).select_from(table)
    for column, value in where.items():
        stmt = stmt.where(table.c[column] == value)
    return int(db.execute(stmt).scalar_one())


# ------------------------------------------------------------ MUST BECOME TRUE


def test_the_host_operator_creates_an_identity_under_production(db_app: sa.Connection) -> None:
    out = io.StringIO()
    assert _create(db_app, stdout=out) == 0
    user = _user(db_app, "livereview-ravi@condyn.eu")
    assert user is not None and user["name"] == "LIVE REVIEW Ravi"
    result = json.loads(out.getvalue())
    assert result["userId"] == str(user["id"]) and result["email"] == "livereview-ravi@condyn.eu"
    assert result["createdBy"] == OPERATOR and result["environment"] == "PRODUCTION"


def test_the_credential_is_hashed_and_the_password_appears_nowhere(
    db_app: sa.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    out, err = io.StringIO(), io.StringIO()
    assert _create(db_app, stdout=out, stderr=err) == 0
    user = _user(db_app, "livereview-ravi@condyn.eu")
    stored = db_app.execute(
        sa.select(local_auth_credentials_table.c.password_hash).where(
            local_auth_credentials_table.c.user_id == user["id"]
        )
    ).scalar_one()
    assert stored.startswith("pbkdf2_sha256$") and PASSWORD not in stored
    event = (
        db_app.execute(
            sa.select(security_events_table).where(
                security_events_table.c.target_ref == f"user:{user['id']}"
            )
        )
        .mappings()
        .one()
    )
    for text in (out.getvalue(), err.getvalue(), caplog.text, json.dumps(dict(event), default=str)):
        assert PASSWORD not in text


def test_the_creation_is_attributed_to_the_host_operator(db_app: sa.Connection) -> None:
    assert _create(db_app) == 0
    user = _user(db_app, "livereview-ravi@condyn.eu")
    (event,) = db_app.execute(
        sa.select(security_events_table).where(
            security_events_table.c.target_ref == f"user:{user['id']}"
        )
    ).mappings()
    assert event["event_type"] == "IDENTITY_CREATED"
    assert event["actor_type"] == "HOST_OPERATOR" and event["actor_id"] == OPERATOR
    assert event["trust_boundary"] == "TB-17" and event["environment"] == "PRODUCTION"
    assert event["workspace_id"] is None
    facts = json.loads(event["observed_facts"])
    assert facts["authority"] == "HD-28 HOST_OPERATOR"
    assert facts["workspaceAuthority"] == "NONE"


def test_the_created_identity_logs_in_normally(db_app: sa.Connection) -> None:
    assert _create(db_app) == 0
    client = TestClient(app)
    r = client.post(
        "/auth/login", json={"email": "livereview-ravi@condyn.eu", "password": PASSWORD}
    )
    assert r.status_code == 200, r.text
    me = client.get("/auth/me")
    user_id = str(_user(db_app, "livereview-ravi@condyn.eu")["id"])
    assert me.status_code == 200 and me.json()["userId"] == user_id
    assert client.post("/auth/logout").status_code in (200, 204)
    assert client.get("/auth/me").status_code == 401


def test_the_created_identity_carries_no_authority_of_any_kind(db_app: sa.Connection) -> None:
    f02.inquiry_context(db_app)  # a real Workspace, Challenge and Session exist
    assert _create(db_app) == 0
    user_id = _user(db_app, "livereview-ravi@condyn.eu")["id"]
    assert _count(db_app, workspace_memberships_table, user_id=user_id) == 0
    roles = db_app.execute(
        sa.select(sa.func.count())
        .select_from(role_assignments_table)
        .join(
            workspace_memberships_table,
            workspace_memberships_table.c.id == role_assignments_table.c.membership_id,
        )
        .where(workspace_memberships_table.c.user_id == user_id)
    ).scalar_one()
    assert roles == 0
    assert _count(db_app, human_authority_bindings_table, human_user_id=user_id) == 0
    assert _count(db_app, session_participations_table, user_id=user_id) == 0
    client = TestClient(app)
    client.post("/auth/login", json={"email": "livereview-ravi@condyn.eu", "password": PASSWORD})
    assert client.get("/workspaces").json() == {"kind": "ok", "workspaces": []}


def test_existing_identities_are_unchanged(db_app: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_app)
    before = db_app.execute(sa.select(users_table).order_by(users_table.c.id)).all()
    creds = db_app.execute(
        sa.select(local_auth_credentials_table).order_by(local_auth_credentials_table.c.id)
    ).all()
    assert _create(db_app) == 0
    after = db_app.execute(
        sa.select(users_table)
        .where(users_table.c.email != "livereview-ravi@condyn.eu")
        .order_by(users_table.c.id)
    ).all()
    assert after == before
    assert (
        db_app.execute(
            sa.select(local_auth_credentials_table)
            .where(
                local_auth_credentials_table.c.user_id
                != _user(db_app, "livereview-ravi@condyn.eu")["id"]
            )
            .order_by(local_auth_credentials_table.c.id)
        ).all()
        == creds
    )
    assert _count(db_app, workspace_memberships_table, workspace_id=ctx["ws"].value) == 2


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


@pytest.mark.parametrize("email", ["livereview-ravi@condyn.eu", "  LiveReview-Ravi@CONDYN.eu  "])
def test_a_duplicate_identity_is_refused_and_nothing_is_written(
    db_app: sa.Connection, email: str
) -> None:
    assert _create(db_app) == 0
    users, events = _count(db_app, users_table), _count(db_app, security_events_table)
    err = io.StringIO()
    assert _create(db_app, email, stderr=err) != 0
    assert "IDENTITY_ALREADY_EXISTS" in err.getvalue()
    assert _count(db_app, users_table) == users and _count(db_app, security_events_table) == events


@pytest.mark.parametrize(
    ("environ", "code"),
    [
        ({}, "ENVIRONMENT_NOT_DECLARED"),
        ({"NQUIRY_ENVIRONMENT": "production"}, "ENVIRONMENT_UNKNOWN"),
        ({"NQUIRY_ENVIRONMENT": "PROD"}, "ENVIRONMENT_UNKNOWN"),
    ],
)
def test_an_undeclared_or_spoofed_environment_is_refused(
    db_app: sa.Connection, environ: dict[str, str], code: str
) -> None:
    err = io.StringIO()
    assert _create(db_app, environ=environ, stderr=err) != 0
    assert code in err.getvalue() and _user(db_app, "livereview-ravi@condyn.eu") is None


@pytest.mark.parametrize(
    ("args", "password", "code"),
    [
        (("--email", "a@condyn.eu", "--name", "A"), PASSWORD, "OPERATOR_REQUIRED"),
        (
            ("--email", "a@condyn.eu", "--name", "A", "--operator", " "),
            PASSWORD,
            "OPERATOR_REQUIRED",
        ),
        (
            ("--email", "not-an-email", "--name", "A", "--operator", OPERATOR),
            PASSWORD,
            "EMAIL_INVALID",
        ),
        (
            ("--email", "a@condyn.eu", "--name", " ", "--operator", OPERATOR),
            PASSWORD,
            "NAME_REQUIRED",
        ),
        (
            ("--email", "a@condyn.eu", "--name", "A", "--operator", OPERATOR),
            "",
            "PASSWORD_REQUIRED",
        ),
        (
            ("--email", "a@condyn.eu", "--name", "A", "--operator", OPERATOR),
            "short",
            "PASSWORD_TOO_SHORT",
        ),
        (
            ("--email", "a@condyn.eu", "--name", "A", "--operator", OPERATOR),
            " " + PASSWORD,
            "PASSWORD_SURROUNDING_WHITESPACE",
        ),
    ],
)
def test_malformed_operator_input_is_refused(
    db_app: sa.Connection, args: tuple[str, ...], password: str, code: str
) -> None:
    err = io.StringIO()
    assert _run(db_app, *args, password=password, stderr=err) != 0
    assert code in err.getvalue() and _user(db_app, "a@condyn.eu") is None


def test_the_password_cannot_be_passed_on_the_command_line(db_app: sa.Connection) -> None:
    """argv is visible in process listings and shell history."""
    with pytest.raises(SystemExit):
        _run(
            db_app,
            "--email", "a@condyn.eu", "--name", "A", "--operator", OPERATOR,
            "--password", PASSWORD,
        )  # fmt: skip
    assert _user(db_app, "a@condyn.eu") is None


def test_a_failed_provenance_write_leaves_no_identity(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    from persistence.security_event_repository import SqlAlchemySecurityEventRepository

    def boom(self: Any, event: Any) -> None:
        raise RuntimeError("security event store unavailable")

    monkeypatch.setattr(SqlAlchemySecurityEventRepository, "record", boom)
    with pytest.raises(RuntimeError):
        _create(db_app)
    assert _user(db_app, "livereview-ravi@condyn.eu") is None


@pytest.mark.parametrize("environment", ["PRODUCTION", "STAGING"])
def test_dev_provisioning_stays_refused_outside_development(environment: str) -> None:
    """The dev-only path (HD-3) must refuse a production-like environment even
    with the opt-in and a database host named like the live one (`postgres`)."""
    from test_support.dev_identity import (
        DEV_IDENTITY_OPT_IN_VALUE,
        DevIdentityProvisioningRefused,
        check_dev_provisioning_allowed,
    )

    with pytest.raises(DevIdentityProvisioningRefused):
        check_dev_provisioning_allowed(
            opt_in_value=DEV_IDENTITY_OPT_IN_VALUE,
            database_host="postgres",
            environment=environment,
        )


def test_dev_provisioning_still_works_for_local_development() -> None:
    from test_support.dev_identity import DEV_IDENTITY_OPT_IN_VALUE, check_dev_provisioning_allowed

    for environment in (None, "DEVELOPMENT", "TEST"):
        check_dev_provisioning_allowed(
            opt_in_value=DEV_IDENTITY_OPT_IN_VALUE,
            database_host="localhost",
            environment=environment,
        )


def test_no_http_route_creates_identities(db_app: sa.Connection) -> None:
    """Option A: no in-app admin, Workspace-owner or invitation creation route. HD-AUTH-13
    (2026-10-07) superseded Option A's "no self-service registration" clause: exactly ONE
    self-service contact exists, `POST /auth/register` (WU-AUTH-22), and without the open
    creation policy it creates nothing (503 REGISTRATION_NOT_AVAILABLE)."""
    paths = {getattr(r, "path", "") for r in app.routes}
    forbidden = ("signup", "sign-up", "invit", "/users", "/identities", "/accounts")
    assert not [p for p in paths if any(f in p.lower() for f in forbidden)]
    assert [p for p in paths if "register" in p.lower()] == ["/auth/register"]
    client = TestClient(app)
    for path in ("/auth/signup", "/users", "/identities"):
        r = client.post(path, json={"email": "x@condyn.eu", "password": PASSWORD, "name": "X"})
        assert r.status_code in (404, 405)
    r = client.post(
        "/auth/register",
        json={"email": "x@condyn.eu", "password": PASSWORD, "name": "X"},
        headers={"Origin": "http://testserver"},
    )
    assert r.status_code == 503 and r.json()["reasonCode"] == "REGISTRATION_NOT_AVAILABLE"
    assert _user(db_app, "x@condyn.eu") is None
