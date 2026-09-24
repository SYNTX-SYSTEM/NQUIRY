"""F02 WU-02.9: real FastAPI routes -> application.http_f02 -> real governed
Commands, against real PostgreSQL (the request connection is the test's own
rolled-back `db_connection`, same harness as `test_http_session_view.py`).

MUST BECOME TRUE: the full F02 flow is drivable over HTTP with real cookies;
every outcome kind is distinct (committed / denied / rejected / stale /
blocked / not_found); Command routes require `Idempotency-Key`; a replay of
a committed intent returns `committed` (replayed) and never double-writes.
MUST REMAIN IMPOSSIBLE: malformed input reported as `denied`; a transition
without an exact Session-scoped binding; cross-Workspace read or write.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

import f02_support as f02
import pytest
import sqlalchemy as sa
from application import http_dispatch, http_f02
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import sessions_table, users_table
from security.local_auth import hash_password
from semantic_types.ids import UserId

PASSWORD = "f02-http-password"


@pytest.fixture
def db_app(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[sa.Connection]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_f02, "connect", _reuse)
    yield db_connection


def _client(db: sa.Connection, user: UserId) -> TestClient:
    email = db.execute(
        sa.select(users_table.c.email).where(users_table.c.id == user.value)
    ).scalar_one()
    if SqlAlchemyLocalCredentialRepository(db).get_by_email(email) is None:
        SqlAlchemyLocalCredentialRepository(db).create(
            user_id=user, password_hash=hash_password(PASSWORD), now=f02.NOW
        )
    client = TestClient(app)
    assert (
        client.post("/auth/login", json={"email": email, "password": PASSWORD}).status_code == 200
    )
    return client


def _idem() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


def _grant(client: TestClient, ws: str, holder: UserId, scope_type: str, scope_id: str) -> dict:  # type: ignore[type-arg]
    return client.post(
        f"/workspaces/{ws}/authority-bindings",
        headers=_idem(),
        json={
            "humanUserId": str(holder.value),
            "authorityClass": "SESSION_CONTROL_RIGHT",
            "scopeType": scope_type,
            "scopeId": scope_id,
        },
    ).json()


def _setup(db: sa.Connection) -> dict:  # type: ignore[type-arg]
    owner = f02.insert_user(db, "owner")
    fac = f02.insert_user(db, "fac")
    ws = f02.found_workspace(db, owner=owner, name="HTTP F02").workspace_id
    f02.add_member(db, owner=owner, workspace_id=ws, member=fac)
    return {
        "owner": owner,
        "fac": fac,
        "ws": str(ws.value),
        "a": _client(db, owner),
        "b": _client(db, fac),
    }


def test_full_f02_flow_over_http(db_app: sa.Connection) -> None:
    ctx = _setup(db_app)
    a, b, ws = ctx["a"], ctx["b"], ctx["ws"]

    overview_a = a.get(f"/workspaces/{ws}/overview").json()
    assert overview_a["capabilities"]["createChallenge"]["available"] is False
    assert "Facilitator" in overview_a["capabilities"]["createChallenge"]["reason"]
    assert (
        b.get(f"/workspaces/{ws}/overview").json()["capabilities"]["createChallenge"]["available"]
        is True
    )

    created = b.post(
        f"/workspaces/{ws}/challenges", headers=_idem(), json={"title": "Why?", "description": "d"}
    ).json()
    assert created["kind"] == "committed"
    cid = created["challengeId"]

    detail = b.get(f"/workspaces/{ws}/challenges/{cid}").json()
    assert detail["capabilities"]["openSession"]["available"] is False
    assert "SESSION_CONTROL_RIGHT" in detail["capabilities"]["openSession"]["reason"]
    assert _grant(a, ws, ctx["fac"], "CHALLENGE", cid)["kind"] == "committed"
    assert (
        b.get(f"/workspaces/{ws}/challenges/{cid}").json()["capabilities"]["openSession"][
            "available"
        ]
        is True
    )

    session = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=_idem()).json()
    assert session["kind"] == "committed"
    sid = session["sessionId"]
    base = f"/workspaces/{ws}/sessions/{sid}"

    pos = b.get(f"{base}/position").json()
    assert pos["session"]["state"] == "DRAFT"
    assert pos["actions"]["BEGIN_SETUP"]["available"] is False
    assert pos["actions"]["BEGIN_SETUP"]["reasonCode"] == "NO_SESSION_CONTROL"
    assert pos["establishedBy"]["commandType"] == "CMD_CREATE_SESSION"

    assert _grant(a, ws, ctx["fac"], "SESSION", sid)["kind"] == "committed"
    r = b.post(f"{base}/transitions/begin-setup", headers=_idem(), json={"expectedVersion": 1})
    assert r.status_code == 200 and r.json()["position"]["session"]["state"] == "SETUP"
    r = b.post(
        f"{base}/transitions/begin-challenge-capture", headers=_idem(), json={"expectedVersion": 2}
    )
    assert r.json()["position"]["session"]["state"] == "CHALLENGE_CAPTURE"
    r = b.post(f"{base}/burst", headers=_idem(), json={"expectedVersion": 3})
    assert r.json()["position"]["burst"]["state"] == "PREPARED"

    blocked = b.post(
        f"{base}/transitions/open-question-generation", headers=_idem(), json={"expectedVersion": 3}
    )
    assert blocked.status_code == 422
    assert blocked.json() == {"kind": "blocked", "reasonCode": "NO_SESSION_PARTICIPANT"}

    r = b.post(
        f"{base}/participants",
        headers=_idem(),
        json={"expectedVersion": 3, "participantUserId": str(ctx["owner"].value)},
    )
    assert r.json()["kind"] == "committed"
    r = b.post(
        f"{base}/transitions/open-question-generation", headers=_idem(), json={"expectedVersion": 3}
    )
    body = r.json()
    assert body["kind"] == "committed"
    assert body["position"]["session"]["state"] == "QUESTION_GENERATION"
    assert body["position"]["burst"]["state"] == "ACTIVE"
    assert body["position"]["establishedBy"]["authoritySourceType"] == "BINDING"
    assert body["position"]["establishedBy"]["authorityScopeRef"] == f"SESSION:{sid}"

    # The Owner sees canonical state but has no control affordance.
    owner_view = a.get(f"{base}/position").json()
    assert owner_view["session"]["state"] == "QUESTION_GENERATION"
    assert owner_view["viewer"]["isSessionController"] is False


def test_outcome_kinds_are_distinct(db_app: sa.Connection) -> None:
    ctx = _setup(db_app)
    a, b, ws = ctx["a"], ctx["b"], ctx["ws"]
    cid = b.post(f"/workspaces/{ws}/challenges", headers=_idem(), json={"title": "T"}).json()[
        "challengeId"
    ]
    _grant(a, ws, ctx["fac"], "CHALLENGE", cid)
    sid = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=_idem()).json()["sessionId"]
    _grant(a, ws, ctx["fac"], "SESSION", sid)
    base = f"/workspaces/{ws}/sessions/{sid}"

    # denied (authority): the Owner holds no Session control.
    r = a.post(f"{base}/transitions/begin-setup", headers=_idem(), json={"expectedVersion": 1})
    assert (r.status_code, r.json()["kind"]) == (403, "denied")
    # rejected (input): malformed id, missing idempotency key, missing version.
    r = b.post(
        f"/workspaces/{ws}/sessions/not-a-uuid/transitions/begin-setup",
        headers=_idem(),
        json={"expectedVersion": 1},
    )
    assert (r.status_code, r.json()["kind"]) == (400, "rejected")
    r = b.post(f"{base}/transitions/begin-setup", json={"expectedVersion": 1})
    assert r.json() == {"kind": "rejected", "reasonCode": "IDEMPOTENCY_KEY_REQUIRED"}
    r = b.post(f"{base}/transitions/begin-setup", headers=_idem(), json={})
    assert r.json() == {"kind": "rejected", "reasonCode": "EXPECTED_VERSION_REQUIRED"}
    # stale: expected version behind.
    b.post(f"{base}/transitions/begin-setup", headers=_idem(), json={"expectedVersion": 1})
    r = b.post(f"{base}/transitions/begin-setup", headers=_idem(), json={"expectedVersion": 1})
    assert (r.status_code, r.json()["kind"], r.json()["currentState"]) == (409, "stale", "SETUP")
    # not_found.
    r = b.get(f"/workspaces/{ws}/sessions/{uuid.uuid4()}/position")
    assert (r.status_code, r.json()["kind"]) == (404, "not_found")
    # no session cookie.
    r = TestClient(app).get(f"{base}/position")
    assert (r.status_code, r.json()["kind"]) == (401, "denied")
    # F01 route E9 repair: malformed Workspace id is rejected, not denied.
    r = b.get("/workspaces/not-a-uuid")
    assert r.json()["kind"] == "rejected"


def test_cross_workspace_read_and_write_are_denied(db_app: sa.Connection) -> None:
    ctx = _setup(db_app)
    a, b, ws = ctx["a"], ctx["b"], ctx["ws"]
    cid = b.post(f"/workspaces/{ws}/challenges", headers=_idem(), json={"title": "T"}).json()[
        "challengeId"
    ]
    _grant(a, ws, ctx["fac"], "CHALLENGE", cid)
    sid = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=_idem()).json()["sessionId"]

    outsider = f02.insert_user(db_app, "outsider")
    f02.found_workspace(db_app, owner=outsider, name="Other")
    c = _client(db_app, outsider)
    assert c.get(f"/workspaces/{ws}/sessions/{sid}/position").json()["kind"] == "denied"
    assert c.get(f"/workspaces/{ws}/challenges/{cid}").json()["kind"] == "denied"
    assert c.get(f"/workspaces/{ws}/overview").json()["kind"] == "denied"
    w = c.post(
        f"/workspaces/{ws}/sessions/{sid}/transitions/begin-setup",
        headers=_idem(),
        json={"expectedVersion": 1},
    )
    assert w.json()["kind"] == "denied"
    state = db_app.execute(
        sa.select(sessions_table.c.state).where(sessions_table.c.id == uuid.UUID(sid))
    ).scalar_one()
    assert state == "DRAFT"


def test_idempotent_replay_returns_committed_without_double_write(db_app: sa.Connection) -> None:
    ctx = _setup(db_app)
    a, b, ws = ctx["a"], ctx["b"], ctx["ws"]
    key = {"Idempotency-Key": str(uuid.uuid4())}
    first = b.post(f"/workspaces/{ws}/challenges", headers=key, json={"title": "Once"}).json()
    again = b.post(f"/workspaces/{ws}/challenges", headers=key, json={"title": "Once"}).json()
    assert first["challengeId"] == again["challengeId"]
    assert len(b.get(f"/workspaces/{ws}/overview").json()["challenges"]) == 1
    collision = b.post(
        f"/workspaces/{ws}/challenges", headers=key, json={"title": "Different"}
    ).json()
    assert collision["kind"] == "rejected"

    cid = first["challengeId"]
    _grant(a, ws, ctx["fac"], "CHALLENGE", cid)
    skey = {"Idempotency-Key": str(uuid.uuid4())}
    s1 = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=skey).json()
    s2 = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=skey).json()
    assert s1["sessionId"] == s2["sessionId"]
    assert len(b.get(f"/workspaces/{ws}/challenges/{cid}").json()["sessions"]) == 1

    sid = s1["sessionId"]
    _grant(a, ws, ctx["fac"], "SESSION", sid)
    tkey = {"Idempotency-Key": str(uuid.uuid4())}
    t1 = b.post(
        f"/workspaces/{ws}/sessions/{sid}/transitions/begin-setup",
        headers=tkey,
        json={"expectedVersion": 1},
    )
    t2 = b.post(
        f"/workspaces/{ws}/sessions/{sid}/transitions/begin-setup",
        headers=tkey,
        json={"expectedVersion": 1},
    )
    assert t1.json()["replayed"] is False
    assert t2.json()["kind"] == "committed" and t2.json()["replayed"] is True
    assert t2.json()["position"]["session"]["version"] == 2
