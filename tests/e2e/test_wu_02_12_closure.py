"""F02 WU-02.12: Field-closure repairs, over real HTTP against real PostgreSQL.

FBR-B (idempotency / command identity)
MUST BECOME TRUE: a reused `Idempotency-Key` is either the SAME logical
Command (same Workspace, command type and payload fingerprint; returns the
committed result without a second effect) or it is `rejected`. That holds
for every F02 Command route, including the Session Commands.
MUST REMAIN IMPOSSIBLE: (a) a key reused with a different payload reported
as `committed`/`replayed`; (b) a key from one Session carrying an effect on
another Session; (c) a `command_id` that already names one Command type
carrying the effect of another Command type (provenance corruption: the
audit/commit rows would name a Command that never asked for that effect);
(d) cross-Workspace key reuse surfacing as a server error.

FBR-C (outcome vocabulary on the wire)
MUST BECOME TRUE: framework-level input validation is `rejected` (400) in the
envelope shape, never FastAPI's bare `{detail}` 422 (which collides with
`blocked`=422); a proven rollback on the F01/PKG routes is
`failed_precommit`, never folded into `rejected`.

FALSIFIER: any assertion below failing on the current tree.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

import f02_support as f02
import pytest
import sqlalchemy as sa
from application import http_dispatch, http_f02
from commit.coordinator import CommitFailedPrecommit
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    commands_table,
    commit_units_table,
    sessions_table,
    users_table,
)
from security.local_auth import hash_password
from semantic_types.ids import UserId

PASSWORD = "wu-02-12-password"


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


def _grant(client: TestClient, ws: str, holder: UserId, scope_type: str, scope_id: str) -> None:
    body = client.post(
        f"/workspaces/{ws}/authority-bindings",
        headers=_idem(),
        json={
            "humanUserId": str(holder.value),
            "authorityClass": "SESSION_CONTROL_RIGHT",
            "scopeType": scope_type,
            "scopeId": scope_id,
        },
    ).json()
    assert body["kind"] == "committed", body


def _context(db: sa.Connection, sessions: int = 1) -> dict:  # type: ignore[type-arg]
    owner = f02.insert_user(db, "owner")
    fac = f02.insert_user(db, "fac")
    ws = str(f02.found_workspace(db, owner=owner, name="WU-02.12").workspace_id.value)
    f02.add_member(db, owner=owner, workspace_id=f02.WorkspaceId(uuid.UUID(ws)), member=fac)
    a, b = _client(db, owner), _client(db, fac)
    cid = b.post(f"/workspaces/{ws}/challenges", headers=_idem(), json={"title": "T"}).json()[
        "challengeId"
    ]
    _grant(a, ws, fac, "CHALLENGE", cid)
    sids = []
    for _ in range(sessions):
        sid = b.post(f"/workspaces/{ws}/challenges/{cid}/sessions", headers=_idem()).json()[
            "sessionId"
        ]
        _grant(a, ws, fac, "SESSION", sid)
        sids.append(sid)
    return {"owner": owner, "fac": fac, "ws": ws, "a": a, "b": b, "cid": cid, "sids": sids}


def _session_row(db: sa.Connection, sid: str) -> tuple[str, int]:
    row = db.execute(
        sa.select(sessions_table.c.state, sessions_table.c.record_version).where(
            sessions_table.c.id == uuid.UUID(sid)
        )
    ).one()
    return row.state, row.record_version


def _commit_count(db: sa.Connection, ws: str) -> int:
    return db.execute(
        sa.select(sa.func.count())
        .select_from(commit_units_table)
        .where(commit_units_table.c.workspace_id == uuid.UUID(ws))
    ).scalar_one()


# ----------------------------------------------------------------------------- FBR-B


def test_identical_session_command_retry_is_replayed_without_second_effect(
    db_app: sa.Connection,
) -> None:
    """Positive control: the legitimate retry must survive the repair."""
    ctx = _context(db_app)
    b, ws, sid = ctx["b"], ctx["ws"], ctx["sids"][0]
    key = _idem()
    url = f"/workspaces/{ws}/sessions/{sid}/transitions/begin-setup"
    first = b.post(url, headers=key, json={"expectedVersion": 1}).json()
    commits = _commit_count(db_app, ws)
    again = b.post(url, headers=key, json={"expectedVersion": 1}).json()
    assert (first["kind"], first["replayed"]) == ("committed", False)
    assert (again["kind"], again["replayed"]) == ("committed", True)
    assert _commit_count(db_app, ws) == commits
    assert _session_row(db_app, sid) == ("SETUP", 2)


def test_same_key_different_payload_on_session_command_is_rejected(
    db_app: sa.Connection,
) -> None:
    ctx = _context(db_app)
    b, ws, sid = ctx["b"], ctx["ws"], ctx["sids"][0]
    key = _idem()
    url = f"/workspaces/{ws}/sessions/{sid}/transitions/begin-setup"
    assert b.post(url, headers=key, json={"expectedVersion": 1}).json()["kind"] == "committed"
    commits = _commit_count(db_app, ws)

    reused = b.post(url, headers=key, json={"expectedVersion": 2})
    assert reused.status_code == 400
    assert reused.json() == {
        "kind": "rejected",
        "reasonCode": "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND",
    }
    assert _commit_count(db_app, ws) == commits
    assert _session_row(db_app, sid) == ("SETUP", 2)


def test_same_key_on_another_session_is_rejected_and_has_no_effect(
    db_app: sa.Connection,
) -> None:
    ctx = _context(db_app, sessions=2)
    b, ws = ctx["b"], ctx["ws"]
    s1, s2 = ctx["sids"]
    key = _idem()
    first = b.post(
        f"/workspaces/{ws}/sessions/{s1}/transitions/begin-setup",
        headers=key,
        json={"expectedVersion": 1},
    ).json()
    assert first["kind"] == "committed"

    reused = b.post(
        f"/workspaces/{ws}/sessions/{s2}/transitions/begin-setup",
        headers=key,
        json={"expectedVersion": 1},
    )
    assert reused.json()["kind"] == "rejected", reused.json()
    assert reused.json()["reasonCode"] == "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND"
    assert _session_row(db_app, s2) == ("DRAFT", 1)


def test_command_id_cannot_carry_the_effect_of_another_command_type(
    db_app: sa.Connection,
) -> None:
    """prepare-burst and open-question-generation share the payload shape
    (session id + expected version), so their fingerprints are equal. The
    key is the `command_id`: reusing it for a different Command type would
    make one `commands` row (CMD_PREPARE_BURST) the provenance of a
    QUESTION_GENERATION effect."""
    ctx = _context(db_app)
    b, ws, sid, owner = ctx["b"], ctx["ws"], ctx["sids"][0], ctx["owner"]
    base = f"/workspaces/{ws}/sessions/{sid}"
    b.post(f"{base}/transitions/begin-setup", headers=_idem(), json={"expectedVersion": 1})
    b.post(
        f"{base}/transitions/begin-challenge-capture", headers=_idem(), json={"expectedVersion": 2}
    )
    b.post(
        f"{base}/participants",
        headers=_idem(),
        json={"expectedVersion": 3, "participantUserId": str(owner.value)},
    )
    key = _idem()
    prepared = b.post(f"{base}/burst", headers=key, json={"expectedVersion": 3}).json()
    assert prepared["kind"] == "committed"
    assert prepared["position"]["session"]["version"] == 3

    reused = b.post(
        f"{base}/transitions/open-question-generation", headers=key, json={"expectedVersion": 3}
    )
    assert reused.json() == {
        "kind": "rejected",
        "reasonCode": "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND",
    }
    assert _session_row(db_app, sid) == ("CHALLENGE_CAPTURE", 3)
    command_types = (
        db_app.execute(
            sa.select(commands_table.c.command_type).where(
                commands_table.c.id == uuid.UUID(key["Idempotency-Key"])
            )
        )
        .scalars()
        .all()
    )
    assert command_types == ["CMD_PREPARE_BURST"]


def test_cross_workspace_key_reuse_is_rejected_not_a_server_error(
    db_app: sa.Connection,
) -> None:
    ctx = _context(db_app)
    b, ws = ctx["b"], ctx["ws"]
    key = _idem()
    assert (
        b.post(f"/workspaces/{ws}/challenges", headers=key, json={"title": "One"}).json()["kind"]
        == "committed"
    )
    other_owner = f02.insert_user(db_app, "other")
    other_ws = str(f02.found_workspace(db_app, owner=other_owner, name="Other").workspace_id.value)
    other_fac = f02.insert_user(db_app, "otherfac")
    f02.add_member(
        db_app,
        owner=other_owner,
        workspace_id=f02.WorkspaceId(uuid.UUID(other_ws)),
        member=other_fac,
    )
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies = _client(db_app, other_fac).cookies
    reused = c.post(f"/workspaces/{other_ws}/challenges", headers=key, json={"title": "One"})
    assert reused.status_code == 400, reused.text
    assert reused.json() == {
        "kind": "rejected",
        "reasonCode": "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND",
    }


# ----------------------------------------------------------------------------- FBR-C


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/workspaces/{ws}/challenges", {"description": "no title"}),
        ("/workspaces/{ws}/sessions/{sid}/transitions/begin-setup", {"expectedVersion": "x"}),
        ("/workspaces/{ws}/authority-bindings", {"humanUserId": "only"}),
        ("/workspaces", {}),
        ("/workspaces/{ws}/members", {}),
    ],
)
def test_framework_validation_failure_is_rejected_in_envelope_shape(
    db_app: sa.Connection,
    path: str,
    body: dict,  # type: ignore[type-arg]
) -> None:
    ctx = _context(db_app)
    url = path.format(ws=ctx["ws"], sid=ctx["sids"][0])
    r = ctx["b"].post(url, headers=_idem(), json=body)
    assert r.status_code == 400, r.text
    assert r.json() == {"kind": "rejected", "reasonCode": "MALFORMED_REQUEST_BODY"}


def test_login_validation_failure_is_rejected_in_envelope_shape() -> None:
    r = TestClient(app).post("/auth/login", json={"email": "x@y.z"})
    assert r.status_code == 400
    assert r.json() == {"kind": "rejected", "reasonCode": "MALFORMED_REQUEST_BODY"}


def test_failed_precommit_on_f01_route_is_not_folded_into_rejected(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx = _context(db_app)
    newcomer = f02.insert_user(db_app, "newcomer")

    def _rolled_back(*_args: object, **_kwargs: object) -> None:
        raise CommitFailedPrecommit("INJECTED_SAVEPOINT_ROLLBACK")

    monkeypatch.setattr(http_dispatch, "add_member", _rolled_back)
    r = ctx["a"].post(
        f"/workspaces/{ctx['ws']}/members",
        json={"userId": str(newcomer.value), "role": "Contributor"},
    )
    assert r.json() == {"kind": "failed_precommit", "reasonCode": "INJECTED_SAVEPOINT_ROLLBACK"}
