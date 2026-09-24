"""F03 WU-03.9: capture and completion over HTTP (real FastAPI routes, real
cookies, real PostgreSQL through the harness of `test_http_f02.py`).

MUST BECOME TRUE: the protected-Burst path is drivable over HTTP; each outcome
kind stays distinct (committed / denied / rejected / stale / blocked); a
capture response carries the canonical reread (the Question exactly as typed,
HUMAN); an identical retry replays; the frozen set is served to every member.

MUST REMAIN IMPOSSIBLE: a client-supplied `origin` / author / mode being honoured
(it is REJECTED, not ignored); a statement stored; an unauthorized actor learning
anything from validation; a route that updates, deletes or rewrites a Question or
a membership; AI reachable from the capture / completion path.
"""

from __future__ import annotations

import ast
import pathlib
import uuid

import f03_support as f03
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from fastapi.testclient import TestClient
from nquiry_api.main import app
from test_http_f02 import _client, _idem

db_app = http_f02.db_app  # the same request-connection fixture as the F02 HTTP proof


def _world(db: sa.Connection) -> dict:  # type: ignore[type-arg]
    ctx = f03.generating_context(db, participants=2)
    ws, sid = str(ctx["ws"].value), str(ctx["session"].value)
    return {
        "ctx": ctx,
        "ws": ws,
        "sid": sid,
        "base": f"/workspaces/{ws}/sessions/{sid}",
        "fac": _client(db, ctx["fac"]),
        "a": _client(db, ctx["participants"][0]),
        "b": _client(db, ctx["participants"][1]),
        "owner": _client(db, ctx["owner"]),
        "outsider": _client(db, ctx["outsider"]),
    }


def _capture(client: TestClient, w: dict, text: object, version: int | None = None, **extra):  # type: ignore[no-untyped-def,type-arg]
    if version is None:
        version = client.get(f"{w['base']}/position").json()["burst"]["version"]
    return client.post(
        f"{w['base']}/burst/questions",
        headers=_idem(),
        json={"originalText": text, "expectedBurstVersion": version, **extra},
    )


def test_capture_and_completion_flow_over_http(db_app: sa.Connection) -> None:
    w = _world(db_app)
    a, b, fac = w["a"], w["b"], w["fac"]

    pos = a.get(f"{w['base']}/position").json()
    assert pos["actions"]["CAPTURE_QUESTION"]["available"] is True
    assert pos["burst"]["state"] == "ACTIVE" and pos["burst"]["mode"] == "HUMAN_ONLY"

    r = _capture(a, w, "Question A — exactly as typed?")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "committed" and body["replayed"] is False
    mine = body["position"]["questionSet"]["mine"]
    assert [q["originalText"] for q in mine] == ["Question A — exactly as typed?"]
    assert mine[0]["origin"] == "HUMAN"
    assert _capture(a, w, "Question B?").status_code == 200

    # participant B sees only their own (none yet); the controller sees a count
    assert b.get(f"{w['base']}/position").json()["questionSet"]["mine"] == []
    ctl = fac.get(f"{w['base']}/position").json()["questionSet"]
    assert ctl["capturedCount"] == 2 and ctl["mine"] == []

    # unauthorized: outsider (member, not participant) and Owner
    for name in ("outsider", "owner", "fac"):
        r = _capture(w[name], w, "Sneaky?", version=pos["burst"]["version"])
        assert r.status_code == 403 and r.json()["kind"] == "denied", name
        assert r.json()["reasonCode"] == "PARTICIPATION_NOT_CURRENT"

    # participants cannot complete
    sv = pos["session"]["version"]
    r = a.post(
        f"{w['base']}/transitions/complete-burst",
        headers=_idem(),
        json={"expectedVersion": sv, "expectedBurstVersion": pos["burst"]["version"]},
    )
    assert r.status_code == 403 and r.json()["kind"] == "denied"

    # the controller completes
    r = fac.post(
        f"{w['base']}/transitions/complete-burst",
        headers=_idem(),
        json={"expectedVersion": sv, "expectedBurstVersion": pos["burst"]["version"]},
    )
    assert r.status_code == 200, r.text
    done = r.json()["position"]
    assert done["session"]["state"] == "QUESTION_CAPTURE" and done["burst"]["state"] == "COMPLETED"
    assert done["questionSet"]["frozen"]["verified"] is True
    assert done["establishedBy"]["commandType"] == "CMD_COMPLETE_BURST"

    # late capture: blocked, and the frozen set is unchanged for everyone
    r = _capture(a, w, "Too late?", version=done["burst"]["version"])
    assert r.status_code == 422 and r.json()["kind"] == "blocked"
    for name in ("a", "b", "fac", "owner", "outsider"):
        view = w[name].get(f"{w['base']}/position").json()["questionSet"]["frozen"]
        assert view["memberCount"] == 2
        assert [q["originalText"] for q in view["questions"]] == [
            "Question A — exactly as typed?",
            "Question B?",
        ]


def test_input_and_envelope_outcomes_are_distinct(db_app: sa.Connection) -> None:
    w = _world(db_app)
    a = w["a"]
    version = a.get(f"{w['base']}/position").json()["burst"]["version"]

    r = _capture(a, w, "It dropped.", version)
    assert r.status_code == 400 and r.json() == {
        "kind": "rejected",
        "reasonCode": "INPUT_NOT_A_QUESTION",
    }
    assert _capture(a, w, "   ", version).json()["reasonCode"] == "INPUT_EMPTY"
    assert _capture(a, w, 42, version).json()["reasonCode"] == "ORIGINAL_TEXT_REQUIRED"
    assert _capture(a, w, None, version).json()["reasonCode"] == "ORIGINAL_TEXT_REQUIRED"

    r = a.post(
        f"{w['base']}/burst/questions",
        json={"originalText": "No key?", "expectedBurstVersion": version},
    )
    assert r.status_code == 400 and r.json()["reasonCode"] == "IDEMPOTENCY_KEY_REQUIRED"
    r = a.post(
        f"{w['base']}/burst/questions", headers=_idem(), json={"originalText": "No version?"}
    )
    assert r.status_code == 400 and r.json()["reasonCode"] == "EXPECTED_VERSION_REQUIRED"

    r = _capture(a, w, "Stale view?", version + 5)
    assert r.status_code == 409 and r.json()["kind"] == "stale"
    assert r.json()["currentVersion"] == version

    # unauthenticated
    anon = TestClient(app)
    r = anon.post(
        f"{w['base']}/burst/questions",
        headers=_idem(),
        json={"originalText": "Anon?", "expectedBurstVersion": version},
    )
    assert r.status_code == 401
    assert f03.question_rows(db_app, w["ctx"]) == []


@pytest.mark.parametrize(
    "extra",
    [
        {"origin": "AI"},
        {"authorUserId": str(uuid.uuid4())},
        {"mode": "HUMAN_PLUS_AI"},
        {"captureOrigin": "AI"},
        {"normalizedText": "rewritten"},
    ],
)
def test_client_supplied_origin_author_or_mode_is_rejected_not_honoured(
    db_app: sa.Connection,
    extra: dict,
) -> None:
    w = _world(db_app)
    version = w["a"].get(f"{w['base']}/position").json()["burst"]["version"]
    r = _capture(w["a"], w, "Injected?", version, **extra)
    assert r.status_code == 400 and r.json()["kind"] == "rejected"
    assert r.json()["reasonCode"].startswith("UNSUPPORTED_FIELD:")
    assert f03.question_rows(db_app, w["ctx"]) == []


def test_unauthorized_actor_gets_denied_not_a_validation_hint(db_app: sa.Connection) -> None:
    w = _world(db_app)
    version = w["a"].get(f"{w['base']}/position").json()["burst"]["version"]
    r = _capture(w["outsider"], w, "not a question", version)
    assert r.status_code == 403 and r.json()["kind"] == "denied"


def test_identical_retry_replays_and_changed_payload_is_rejected(db_app: sa.Connection) -> None:
    w = _world(db_app)
    a = w["a"]
    version = a.get(f"{w['base']}/position").json()["burst"]["version"]
    headers = _idem()
    body = {"originalText": "Once?", "expectedBurstVersion": version}
    first = a.post(f"{w['base']}/burst/questions", headers=headers, json=body)
    again = a.post(f"{w['base']}/burst/questions", headers=headers, json=body)
    assert first.status_code == again.status_code == 200
    assert first.json()["replayed"] is False and again.json()["replayed"] is True
    assert len(f03.question_rows(db_app, w["ctx"])) == 1

    changed = a.post(
        f"{w['base']}/burst/questions",
        headers=headers,
        json={"originalText": "Changed?", "expectedBurstVersion": version},
    )
    assert changed.status_code == 400
    assert changed.json()["reasonCode"] == "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND"

    # the same key used for ANOTHER command type (completion) is rejected too
    pos = w["fac"].get(f"{w['base']}/position").json()
    cross = w["fac"].post(
        f"{w['base']}/transitions/complete-burst",
        headers=headers,
        json={
            "expectedVersion": pos["session"]["version"],
            "expectedBurstVersion": pos["burst"]["version"],
        },
    )
    assert cross.status_code == 400
    assert cross.json()["reasonCode"] == "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND"
    assert len(f03.question_rows(db_app, w["ctx"])) == 1


def test_blocked_and_stale_completion(db_app: sa.Connection) -> None:
    w = _world(db_app)
    fac = w["fac"]
    pos = fac.get(f"{w['base']}/position").json()
    zero = fac.post(
        f"{w['base']}/transitions/complete-burst",
        headers=_idem(),
        json={
            "expectedVersion": pos["session"]["version"],
            "expectedBurstVersion": pos["burst"]["version"],
        },
    )
    assert zero.status_code == 422 and zero.json() == {
        "kind": "blocked",
        "reasonCode": "NO_CAPTURED_QUESTIONS",
    }
    _capture(w["a"], w, "One?")
    stale = fac.post(
        f"{w['base']}/transitions/complete-burst",
        headers=_idem(),
        json={
            "expectedVersion": pos["session"]["version"] + 4,
            "expectedBurstVersion": pos["burst"]["version"],
        },
    )
    assert stale.status_code == 409 and stale.json()["kind"] == "stale"
    missing = fac.post(f"{w['base']}/transitions/complete-burst", headers=_idem(), json={})
    assert (
        missing.status_code == 400 and missing.json()["reasonCode"] == "EXPECTED_VERSION_REQUIRED"
    )


def test_no_route_can_update_delete_or_rewrite_a_question() -> None:
    """Static route inventory: capture is the only writer; there is no
    Question / membership / freeze mutation route (PUT/PATCH/DELETE)."""
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = set(getattr(route, "methods", set()) or set())
        if "/questions" in path.lower() or "burst" in path.lower():
            assert not (methods & {"PUT", "PATCH", "DELETE"}), (path, methods)
    writers = [
        (getattr(r, "path", ""), sorted(getattr(r, "methods", set()) or set()))
        for r in app.routes
        if "/questions" in getattr(r, "path", "").lower()
    ]
    assert writers == [
        ("/workspaces/{workspace_id}/sessions/{session_id}/burst/questions", ["POST"])
    ]


def test_ai_is_not_reachable_from_the_capture_and_completion_path() -> None:
    """Static: the F03 handlers import no AI gateway/contract/provider module
    (BND-009: no AI operation is reachable during the protected Burst)."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    forbidden = ("ai_gateway", "ai_contracts", "anthropic", "openai", "google", "provider")
    for name in ("burst_capture_handler.py", "burst_completion_handler.py", "frozen_set.py"):
        tree = ast.parse((root / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            else:
                continue
            for mod in mods:
                assert not any(mod.split(".")[0].startswith(f) for f in forbidden), (name, mod)
