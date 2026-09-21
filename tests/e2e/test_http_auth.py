"""T10 END-TO-END TEST: `POST /auth/login`, `POST /auth/logout`,
`GET /auth/me`, and the full adversarial session-verification matrix
for the two Architecture-17 routes, through the REAL FastAPI app,
against real PostgreSQL.

This is the closure proof for the local-login field
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): every
negative/adversarial case that motivated replacing the old
header-trust `resolve_actor` is proven here, through the REAL cookie
mechanism a real browser actually uses (`fastapi.testclient.TestClient`
is httpx-based and persists cookies across calls on the same client
instance exactly like a browser does -- `_login` below relies on this).

Same `http_client` connection-reuse fixture technique as
`test_http_session_view.py` -- see that file's own module docstring for
why `application.http_dispatch.connect` is the correct monkeypatch
target.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import application.http_dispatch as http_dispatch
import pytest
import sqlalchemy as sa
from application.http_dispatch import SESSION_COOKIE_NAME
from fastapi.testclient import TestClient
from governance.membership import WorkspaceRole
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    challenges_table,
    local_auth_sessions_table,
    role_assignments_table,
    sessions_table,
)
from security.local_auth import hash_password
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ChallengeId, SessionId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import (
    NonProofWorkspaceBootstrap,
    NonProofWorkspaceBootstrapResult,
)

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_PASSWORD = "correct horse battery staple"


@pytest.fixture
def http_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse_test_connection() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse_test_connection)
    yield TestClient(app)


def _bootstrap_with_password(
    db_connection: sa.Connection, *, email: str, password: str = _PASSWORD
) -> NonProofWorkspaceBootstrapResult:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    db_connection.execute(
        sa.insert(role_assignments_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=result.workspace_id.value,
            membership_id=result.membership_id,
            role=WorkspaceRole.OWNER.value,
            granted_by_user_id=result.owner_user_id.value,
            granted_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )
    SqlAlchemyLocalCredentialRepository(db_connection).create(
        user_id=result.owner_user_id, password_hash=hash_password(password), now=_NOW
    )
    return result


def _seed_challenge_and_session(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> tuple[ChallengeId, SessionId]:
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=workspace_id.value,
            title="Local-login HTTP proof Challenge",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    session_id = SessionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=1,
        )
    )
    return challenge_id, session_id


def _login(http_client: TestClient, *, email: str, password: str = _PASSWORD):
    return http_client.post("/auth/login", json={"email": email, "password": password})


# --- POST /auth/login --------------------------------------------------


def test_login_happy_path_sets_an_httponly_session_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap_with_password(db_connection, email="auth-login-happy@nonproof.test")

    response = _login(http_client, email="auth-login-happy@nonproof.test")

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    assert body["userId"] == str(result.owner_user_id.value)
    assert SESSION_COOKIE_NAME not in body  # raw token must never appear in the JSON body
    set_cookie = response.headers.get("set-cookie", "")
    assert f"{SESSION_COOKIE_NAME}=" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert result.owner_user_id.value.hex not in set_cookie  # cookie is an opaque token, not the id


def test_login_rejects_a_wrong_password_and_sets_no_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _bootstrap_with_password(db_connection, email="auth-login-wrongpw@nonproof.test")

    response = _login(http_client, email="auth-login-wrongpw@nonproof.test", password="nope")

    assert response.status_code == 401
    assert response.json()["kind"] == "denied"
    assert "set-cookie" not in {k.lower() for k in response.headers}


def test_login_rejects_an_unknown_email(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    response = _login(http_client, email="never-registered@nonproof.test", password="anything")
    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


# --- GET /auth/me / POST /auth/logout -----------------------------------


def test_me_reports_no_session_before_login(http_client: TestClient) -> None:
    response = http_client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


def test_me_reports_the_real_logged_in_user_after_login(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap_with_password(db_connection, email="auth-me-happy@nonproof.test")
    _login(http_client, email="auth-me-happy@nonproof.test")

    response = http_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["userId"] == str(result.owner_user_id.value)


def test_logout_revokes_the_session_and_me_reports_no_session_afterward(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _bootstrap_with_password(db_connection, email="auth-logout@nonproof.test")
    _login(http_client, email="auth-logout@nonproof.test")
    assert http_client.get("/auth/me").status_code == 200

    logout_response = http_client.post("/auth/logout")
    assert logout_response.status_code == 200

    assert http_client.get("/auth/me").status_code == 401


def test_logout_with_no_session_is_a_silent_no_op(http_client: TestClient) -> None:
    response = http_client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["kind"] == "ok"


# --- Adversarial session-verification matrix, exercised against the
# real GET /workspaces/{w}/sessions/{s} route ---------------------------


def test_session_view_denies_a_request_with_no_cookie_at_all(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap_with_password(db_connection, email="matrix-no-cookie@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


def test_session_view_denies_a_forged_garbage_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: a cookie value that was never issued by a real
    `/auth/login` call must not resolve to anyone."""
    result = _bootstrap_with_password(db_connection, email="matrix-garbage@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )

    http_client.cookies.set(SESSION_COOKIE_NAME, "totally-forged-never-issued-token")
    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 401


def test_session_view_denies_a_tampered_real_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: a real, previously-issued cookie with one character
    flipped must not resolve -- proves the lookup is an exact hash
    match, not fuzzy/prefix."""
    result = _bootstrap_with_password(db_connection, email="matrix-tamper@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    login_response = _login(http_client, email="matrix-tamper@nonproof.test")
    real_cookie = login_response.cookies[SESSION_COOKIE_NAME]
    flipped = ("a" if real_cookie[0] != "a" else "b") + real_cookie[1:]

    # A fresh, separate client -- avoids httpx TestClient's own ambiguous
    # per-request-cookie-vs-persistent-jar merge behavior (the
    # `http_client` instance above already carries the REAL cookie in
    # its jar from `_login`; a second client has an empty jar, so
    # setting the tampered value is unambiguous). The `connect`
    # monkeypatch is on the `http_dispatch` module itself, not scoped to
    # any one client instance, so a second `TestClient(app)` still uses
    # the same patched, test-transaction-reusing connection.
    tampered_client = TestClient(app)
    tampered_client.cookies.set(SESSION_COOKIE_NAME, flipped)

    response = tampered_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 401


def test_session_view_denies_an_expired_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: a session past its own `expires_at`, never
    explicitly revoked, must not resolve."""
    result = _bootstrap_with_password(db_connection, email="matrix-expired@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="matrix-expired@nonproof.test")
    # `resolve_session` compares against the REAL wall-clock
    # (`datetime.now(timezone.utc)`), not this file's fixed `_NOW`
    # (2030-01-01, used only for seeding unrelated domain rows) -- the
    # expiry must be backdated relative to actual real time for this
    # test to mean anything.
    db_connection.execute(
        sa.update(local_auth_sessions_table)
        .where(local_auth_sessions_table.c.user_id == result.owner_user_id.value)
        .values(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    )

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 401


def test_session_view_denies_a_revoked_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: a session explicitly revoked via `/auth/logout`
    must not resolve, even though its own `expires_at` has not passed
    yet."""
    result = _bootstrap_with_password(db_connection, email="matrix-revoked@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="matrix-revoked@nonproof.test")
    assert (
        http_client.get(
            f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
        ).status_code
        == 200
    )

    http_client.post("/auth/logout")

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )
    assert response.status_code == 401


def test_session_view_denies_a_foreign_user_id_header_when_no_session_is_present(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial, direct proof of GAP-14-001 closure: the OLD
    `x-nquiry-actor-user-id` header, naming a completely real, valid
    owner, gains NOTHING at all now -- no session cookie means 401
    regardless of what any header claims."""
    result = _bootstrap_with_password(db_connection, email="matrix-header-only@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}",
        headers={
            "x-nquiry-actor-user-id": str(result.owner_user_id.value),
            "x-nquiry-actor-class": "AI_PROCESSOR",
        },
    )

    assert response.status_code == 401


def test_session_view_ignores_a_forged_actor_class_header_when_a_real_session_is_present(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: WITH a real, valid session present, smuggling the
    old `x-nquiry-actor-class: AI_PROCESSOR` header alongside it has
    ZERO effect -- the request still succeeds as the real logged-in
    HUMAN_USER, proving the header is fully inert dead input, not
    silently trusted as an override. (BND-001's own AI-actor DENY logic
    itself is unchanged and still covered directly by
    `tests/e2e/test_proof_bundle_paths.py::
    test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched`
    -- there is simply no HTTP path left that can ever present as
    AI_PROCESSOR at all, which is the point.)"""
    result = _bootstrap_with_password(db_connection, email="matrix-header-ignored@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="matrix-header-ignored@nonproof.test")

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}",
        headers={
            "x-nquiry-actor-user-id": str(uuid.uuid4()),  # a completely different, real stranger
            "x-nquiry-actor-class": "AI_PROCESSOR",
        },
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "ok"


def test_session_view_denies_a_real_logged_in_stranger_with_no_workspace_membership(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Replaces the old header-forged 'stranger' test: now a REAL,
    independently-registered-and-logged-in user, who genuinely has no
    membership in the target Workspace -- BND-002/003 still deny, same
    as before, now proven through a real second login rather than a
    forged header naming an id that belongs to no one."""
    owner = _bootstrap_with_password(db_connection, email="matrix-stranger-owner@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=owner.workspace_id
    )
    _bootstrap_with_password(db_connection, email="matrix-stranger-self@nonproof.test")
    _login(http_client, email="matrix-stranger-self@nonproof.test")

    response = http_client.get(
        f"/workspaces/{owner.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "denied"
    assert body["result"] == "DENY"
