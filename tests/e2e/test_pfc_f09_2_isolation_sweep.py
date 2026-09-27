"""WU-PFC-F09-2 (F09): Workspace isolation and session sweep over EVERY route.

Architecture: 19 §29 (internal Work Units "Workspace isolation sweep",
"session/security sweep"; TESTS FIRST "cross-Workspace access", "session
expiry"); 13 P-22 (T13-P22-CROSS-WORKSPACE: WS-A actor against WS-B objects ->
"no disclosure/mutation", DENIED); 12 AC-12-024 ("PASS if Workspace mismatch is
denied before protected data disclosure"); 06 BND-001 (identity: an expired
session is no identity), BND-002/BND-003 (Workspace, membership).

The sweep is generated from the application's own route table, so a route added
later without an entry here fails `test_the_sweep_covers_every_route`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from persistence.tables import (
    audit_events_table,
    challenges_table,
    command_attempts_table,
    commit_units_table,
    decisions_table,
    human_authority_bindings_table,
    local_auth_sessions_table,
    outbox_events_table,
    question_bursts_table,
    questions_table,
    session_participations_table,
    sessions_table,
    workspace_memberships_table,
)
from test_http_f02 import _client

db_app = http_f02.db_app

# Canonical and governance state. `commands` / `command_attempts` are the command
# log: a denied attempt is legitimately recorded there (10 §4.1), and is checked
# separately to be DENIED only.
_PROTECTED = (
    audit_events_table,
    challenges_table,
    commit_units_table,
    decisions_table,
    human_authority_bindings_table,
    outbox_events_table,
    question_bursts_table,
    questions_table,
    session_participations_table,
    sessions_table,
    workspace_memberships_table,
)

# Every route except the unauthenticated entry points. `{...}` are filled with
# Workspace A's real ids.
ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("GET", "/auth/me", None),
    ("GET", "/workspaces", None),
    ("POST", "/workspaces", {"name": "W"}),
    ("GET", "/workspaces/{ws}", None),
    ("POST", "/workspaces/{ws}/members", {"userId": "{outsider}", "role": "Contributor"}),
    ("POST", "/workspaces/{ws}/authority-bindings/{binding}/revoke", {}),
    ("GET", "/workspaces/{ws}/overview", None),
    ("POST", "/workspaces/{ws}/challenges", {"title": "intruder"}),
    ("GET", "/workspaces/{ws}/challenges/{challenge}", None),
    ("POST", "/workspaces/{ws}/challenges/{challenge}/sessions", {}),
    (
        "POST",
        "/workspaces/{ws}/authority-bindings",
        {
            "humanUserId": "{outsider}",
            "authorityClass": "SESSION_CONTROL_RIGHT",
            "scopeType": "SESSION",
            "scopeId": "{session}",
        },
    ),
    ("GET", "/workspaces/{ws}/sessions/{session}", None),
    ("GET", "/workspaces/{ws}/sessions/{session}/position", None),
    ("POST", "/workspaces/{ws}/sessions/{session}/transitions/begin-setup", {"expectedVersion": 1}),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/begin-challenge-capture",
        {"expectedVersion": 1},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/open-question-generation",
        {"expectedVersion": 1},
    ),
    ("POST", "/workspaces/{ws}/sessions/{session}/burst", {"expectedVersion": 1}),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/participants",
        {"expectedVersion": 1, "participantUserId": "{outsider}"},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/burst/questions",
        {"originalText": "Why would an outsider write here?", "expectedBurstVersion": 2},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/complete-burst",
        {"expectedVersion": 1, "expectedBurstVersion": 2},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/begin-analysis",
        {"expectedVersion": 1},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/begin-reflection",
        {"expectedVersion": 1},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/transitions/begin-question-selection",
        {"expectedVersion": 1, "reflectionCompletionConfirmed": True},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/question-selections",
        {"expectedVersion": 1, "questionId": "00000000-0000-4000-8000-000000000001"},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/primary-question",
        {"expectedVersion": 1, "questionId": "00000000-0000-4000-8000-000000000001"},
    ),
    ("GET", "/workspaces/{ws}/sessions/{session}/question-selections", None),
    ("POST", "/workspaces/{ws}/sessions/{session}/impact-chain", {"expectedVersion": 1}),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/impact-chain/nodes",
        {"expectedChainVersion": 1, "level": 1, "answer": "Because it matters."},
    ),
    ("GET", "/workspaces/{ws}/sessions/{session}/impact-chain", None),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/analysis/request",
        {"expectedVersion": 1, "case": "RETRY"},
    ),
    (
        "POST",
        "/workspaces/{ws}/sessions/{session}/analysis/clustering/request",
        {"expectedVersion": 1, "case": "RETRY"},
    ),
    ("POST", "/decisions/{decision}/decide", {"selectedOption": "fix_a"}),
]
_UNAUTHENTICATED = {("POST", "/auth/login"), ("POST", "/auth/logout")}
_CROSS_WORKSPACE_EXEMPT = {
    ("GET", "/auth/me"),  # the caller's own identity
    ("GET", "/workspaces"),  # the caller's own Workspace list (checked separately)
    ("POST", "/workspaces"),  # founding one's own Workspace (F01 bootstrap)
}


def _world(db: sa.Connection) -> dict[str, Any]:
    """Workspace A: a Session in QUESTION_GENERATION with an ACTIVE Burst, a
    Facilitator SESSION binding and a Decision under consideration. Workspace B:
    its own owner, the outsider."""
    ctx = f03.generating_context(db, participants=1)
    binding = (
        db.execute(
            sa.select(human_authority_bindings_table.c.id).where(
                human_authority_bindings_table.c.workspace_id == ctx["ws"].value,
                human_authority_bindings_table.c.scope_type == "SESSION",
            )
        )
        .scalars()
        .first()
    )
    decision = uuid.uuid4()
    db.execute(
        sa.insert(decisions_table).values(
            id=decision,
            workspace_id=ctx["ws"].value,
            challenge_id=ctx["challenge"].challenge_id.value,
            decision_question_ref=None,
            decision_question_text="Which fix ships first?",
            options=["fix_a", "fix_b"],
            criteria=["impact"],
            selected_option=None,
            rationale=None,
            confidence=None,
            state="UNDER_CONSIDERATION",
            opened_by_user_id=ctx["fac"].value,
            decision_authority_binding_id=binding,
            decided_by_user_id=None,
            created_at=f02.NOW,
            decided_at=None,
            record_version=1,
            provenance_ref=None,
        )
    )
    ws_b, outsider = f03.new_workspace_with_member(db, "outsider")
    return {
        "ws": str(ctx["ws"].value),
        "challenge": str(ctx["challenge"].challenge_id.value),
        "session": str(ctx["session"].value),
        "binding": str(binding),
        "decision": str(decision),
        "outsider": str(outsider.value),
        "outsider_id": outsider,
        "ws_b": str(ws_b.value),
        "owner": ctx["owner"],
    }


def _fill(value: Any, w: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return value.format(**{k: v for k, v in w.items() if isinstance(v, str)})
    if isinstance(value, dict):
        return {k: _fill(v, w) for k, v in value.items()}
    return value


def _call(
    client: Any, method: str, path: str, body: dict[str, Any] | None, w: dict[str, Any]
) -> Any:
    url = _fill(path, w)
    if method == "GET":
        return client.get(url)
    return client.post(url, headers={"Idempotency-Key": str(uuid.uuid4())}, json=_fill(body, w))


def _counts(db: sa.Connection) -> dict[str, int]:
    return {
        t.name: db.execute(sa.select(sa.func.count()).select_from(t)).scalar_one()
        for t in _PROTECTED
    }


def test_the_sweep_covers_every_route() -> None:
    from nquiry_api.main import app

    served = {
        (m, r.path)  # type: ignore[attr-defined]
        for r in app.routes
        for m in getattr(r, "methods", set())
        if m in ("GET", "POST")
        and not r.path.startswith(("/docs", "/openapi", "/redoc", "/healthz"))  # type: ignore[attr-defined]
    }
    swept = {(m, p.replace("{ws}", "{workspace_id}")) for m, p, _ in ROUTES}
    swept = {
        (
            m,
            p.replace("{challenge}", "{challenge_id}")
            .replace("{session}", "{session_id}")
            .replace("{binding}", "{binding_id}")
            .replace("{decision}", "{decision_id}"),
        )
        for m, p in swept
    }
    assert served - _UNAUTHENTICATED == swept


@pytest.mark.parametrize(
    ("method", "path", "body"), [r for r in ROUTES if (r[0], r[1]) not in _CROSS_WORKSPACE_EXEMPT]
)
def test_an_outsider_is_denied_on_every_route_without_disclosure_or_mutation(
    db_app: sa.Connection, method: str, path: str, body: dict[str, Any] | None
) -> None:
    w = _world(db_app)
    outsider = _client(db_app, w["outsider_id"])
    before = _counts(db_app)
    r = _call(outsider, method, path, body, w)
    payload = r.json()
    # The older route family answers every outcome with HTTP 200 and states it
    # in `kind` (09 §77: "HTTP status may map to these outcomes but does not
    # define them"); the F02+ family uses 403.
    assert r.status_code in (200, 403), (path, r.status_code, r.text)
    assert payload["kind"] == "denied", (path, payload)
    assert set(payload) <= {"kind", "reasonCode", "result"}, (path, payload)  # no protected data
    for value in (w["challenge"], w["session"], w["binding"], w["decision"]):
        assert value not in r.text, (path, "Workspace A id disclosed")
    assert _counts(db_app) == before, path
    outcomes = (
        db_app.execute(
            sa.select(command_attempts_table.c.outcome).where(
                command_attempts_table.c.actor_ref.contains(w["outsider"]),
                command_attempts_table.c.workspace_id == uuid.UUID(w["ws"]),
            )
        )
        .scalars()
        .all()
    )
    assert set(outcomes) <= {"DENIED"}, (path, outcomes)


def test_an_outsiders_workspace_list_never_contains_workspace_a(db_app: sa.Connection) -> None:
    w = _world(db_app)
    r = _client(db_app, w["outsider_id"]).get("/workspaces")
    assert r.status_code == 200
    assert w["ws"] not in r.text and w["ws_b"] in r.text


@pytest.mark.parametrize(("method", "path", "body"), ROUTES)
def test_an_expired_session_is_no_identity_on_every_route(
    db_app: sa.Connection, method: str, path: str, body: dict[str, Any] | None
) -> None:
    w = _world(db_app)
    owner = _client(db_app, w["owner"])
    db_app.execute(
        sa.update(local_auth_sessions_table)
        .where(local_auth_sessions_table.c.user_id == w["owner"].value)
        .values(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    )
    before = _counts(db_app)
    r = _call(owner, method, path, body, w)
    assert r.status_code == 401, (path, r.status_code, r.text)
    assert r.json()["kind"] == "denied", (path, r.json())
    assert _counts(db_app) == before, path


_SESSION_ROUTES = [r for r in ROUTES if "{session}" in r[1] and r[0] == "POST"]


@pytest.mark.parametrize(("method", "path", "body"), _SESSION_ROUTES)
def test_a_member_of_b_cannot_reach_a_session_of_a_through_bs_own_url(
    db_app: sa.Connection, method: str, path: str, body: dict[str, Any] | None
) -> None:
    """BND-002: the Session must belong to the Workspace the caller names. The
    outsider IS a member of B, so membership alone would pass."""
    w = _world(db_app)
    outsider = _client(db_app, w["outsider_id"])
    before = _counts(db_app)
    crossed = dict(w, ws=w["ws_b"])
    r = _call(outsider, method, path, body, crossed)
    payload = r.json()
    assert r.status_code in (200, 403), (path, r.status_code, r.text)
    assert payload["kind"] == "denied", (path, payload)
    assert "currentVersion" not in payload and "currentState" not in payload
    assert _counts(db_app) == before, path
