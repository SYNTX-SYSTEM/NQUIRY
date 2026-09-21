"""T10 END-TO-END TEST: `GET /workspaces/{w}/sessions/{s}` (Architecture
17), through the REAL FastAPI app, against real PostgreSQL.

LOCAL-LOGIN FIELD UPDATE
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): identity now
comes from a real, verified `nquiry_session` cookie issued by a real
`POST /auth/login` call, not from the old `x-nquiry-actor-user-id`/
`x-nquiry-actor-class` request headers -- see
`application.http_dispatch`'s own updated module docstring. The full
adversarial session-verification matrix (forged/tampered/expired/
revoked cookies, forged headers now proven inert) lives in
`tests/e2e/test_http_auth.py`, written once and shared across both
Architecture-17 routes since both call the identical
`_resolve_actor_from_session` internally -- this file keeps the
route-specific happy paths and denial cases (missing session, no
membership, nonexistent session) that were always specific to THIS
route's own response shape.

WHY `persistence.engine.connect` IS MONKEYPATCHED TO THE TEST'S OWN
`db_connection`, NOT LEFT TO OPEN A SECOND REAL CONNECTION
--------------------------------------------------------------------
`db_connection` (this file's own fixture dependency, `tests/e2e/
conftest.py`) wraps the whole test body in one open, never-committed
transaction, rolled back at teardown -- this repository's own
established isolation discipline for every T10 file. `persistence.
engine.connect()`'s OWN real behavior opens a genuinely SEPARATE
PostgreSQL connection; a second, independent connection cannot see
the first one's uncommitted rows (PostgreSQL's own READ COMMITTED
default), so a real end-to-end HTTP call would see none of this test's
own seeded data unless the seed were force-committed -- which would
leak real rows into the database past this test's own teardown,
exactly what the rollback-based fixture exists to prevent. Patching
`persistence.engine.connect` to yield THIS test's own already-open
`db_connection` instead keeps the full real call path (FastAPI ->
`application.http_dispatch` -> `application.session_view_query` ->
real `persistence.SqlAlchemy*Repository` classes -> real boundary
evaluators) genuinely exercised, while the physical connection stays
the one object whose transaction the fixture already owns and rolls
back -- the same "swap only the outermost connection-acquisition, not
any application-layer object" technique, applied to a real ASGI
request instead of a direct Python call.

Each test constructs its own local helpers (this repository's own
established per-T10-file convention, see `tests/e2e/test_proof_bundle_paths.py`'s
own module docstring) and drives the REAL ASGI app via
`fastapi.testclient.TestClient` -- a genuine HTTP request/response
cycle (request line, headers, JSON body, and now real cookies), not a
direct Python call into `application.session_view_query`.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

import application.http_dispatch as http_dispatch
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from governance.membership import WorkspaceRole
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    challenges_table,
    question_bursts_table,
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


def _bootstrap(db_connection: sa.Connection, *, email: str) -> NonProofWorkspaceBootstrapResult:
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
        user_id=result.owner_user_id, password_hash=hash_password(_PASSWORD), now=_NOW
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
            title="Architecture 17 HTTP proof Challenge",
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


def _login(http_client: TestClient, *, email: str) -> None:
    response = http_client.post("/auth/login", json={"email": email, "password": _PASSWORD})
    assert response.status_code == 200, response.text


def test_http_session_view_happy_path_returns_real_committed_state(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-session-happy@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="http-session-happy@nonproof.test")

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    assert body["data"]["session"]["sessionId"] == str(session_id.value)
    assert body["data"]["session"]["state"] == "DRAFT"
    assert body["data"]["burst"] is None
    assert body["data"]["decision"] is None
    assert body["data"]["aiRecommendation"] is None


def test_http_session_view_includes_real_burst(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-session-burst@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    burst_id = _ID_GEN.new_uuid()
    db_connection.execute(
        sa.insert(question_bursts_table).values(
            id=burst_id,
            session_id=session_id.value,
            workspace_id=result.workspace_id.value,
            state="PREPARED",
            mode="HUMAN_ONLY",
            started_at=None,
            paused_at=None,
            completed_at=None,
            frozen_membership_fingerprint=None,
            record_version=1,
        )
    )
    _login(http_client, email="http-session-burst@nonproof.test")

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["burst"]["burstId"] == str(burst_id)
    assert body["data"]["burst"]["state"] == "PREPARED"
    assert body["data"]["burst"]["mode"] == "HUMAN_ONLY"
    assert body["data"]["burst"]["questions"] == []


def test_http_session_view_denies_a_request_with_no_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-session-noheader@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{session_id.value}"
    )

    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


def test_http_session_view_denies_a_nonexistent_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-session-missing@nonproof.test")
    fake_session_id = uuid.uuid4()
    _login(http_client, email="http-session-missing@nonproof.test")

    response = http_client.get(
        f"/workspaces/{result.workspace_id.value}/sessions/{fake_session_id}"
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "denied"


def test_http_session_view_denies_a_nonexistent_workspace(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """A malformed-but-well-formed-UUID workspace id that genuinely does
    not exist -- same DENY shape as a missing Session, proven separately
    since a stray "always matches the seeded Workspace" bug could hide
    behind the happy-path test alone."""
    result = _bootstrap(db_connection, email="http-session-badworkspace@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="http-session-badworkspace@nonproof.test")

    response = http_client.get(f"/workspaces/{uuid.uuid4()}/sessions/{session_id.value}")

    assert response.status_code == 200
    assert response.json()["kind"] == "denied"


def test_malformed_workspace_id_is_rejected(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-session-malformed@nonproof.test")
    _challenge_id, session_id = _seed_challenge_and_session(
        db_connection, workspace_id=result.workspace_id
    )
    _login(http_client, email="http-session-malformed@nonproof.test")

    response = http_client.get(f"/workspaces/not-a-uuid/sessions/{session_id.value}")

    assert response.status_code == 400
