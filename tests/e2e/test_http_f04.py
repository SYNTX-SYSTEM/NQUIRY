"""F04 over HTTP: begin analysis, the derived field, RETRY / RECOVERY (real
FastAPI routes, real cookies, real PostgreSQL through the F02 HTTP harness).

MUST BECOME TRUE: the controller begins analysis over HTTP; the response carries
the committed transition and the run outcome as SEPARATE facts; every member of
the frozen-set audience is served the same derived field (HD-22), marked
AI · DERIVED / PROPOSAL · MOCK / NON_PROOF, with the human Questions separate and
verbatim; the RETRY / RECOVERY capability is the controller's only, with the
server's reason and case; clusters appear only after the analysis is accepted.

MUST REMAIN IMPOSSIBLE: a non-controller begin or request; an outsider reading
the derived field; a mock shown without its marker; a failed run making the
committed transition look failed; a case mismatch accepted.

FALSIFIERS: G1-G5, F2, F3, and the backend halves of H1-H6 (the browser halves
are WU-04.8, blocked on H-8).
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f04_support as f04
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from ai_contracts.aiop import AIOperationId
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application import http_f04
from application.analysis_runtime import UNAVAILABLE, mock_runtime
from fastapi.testclient import TestClient
from test_http_f02 import _client, _idem

A1, A2 = AIOperationId.AIOP_001, AIOperationId.AIOP_002


db_app = http_f02.db_app  # the F02 request-connection fixture


@pytest.fixture
def f04_app(db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch) -> sa.Connection:
    """The F02 harness plus: the system run's transactions are SAVEPOINTs on the
    same test connection, and the runtime is the (scriptable) MockProvider."""
    from contextlib import contextmanager

    @contextmanager
    def _reuse() -> Any:
        yield db_app

    monkeypatch.setattr(http_f04, "connect", _reuse)
    monkeypatch.setattr(http_f04, "transaction_uow", f04.savepoint_uow(db_app))
    monkeypatch.setattr(http_f04, "_runtime", mock_runtime())
    return db_app


def _world(db: sa.Connection) -> dict[str, Any]:
    ctx = f04.capture_context(db)
    ws, sid = str(ctx["ws"].value), str(ctx["session"].value)
    stranger = f02.insert_user(db, "stranger")
    return {
        "ctx": ctx,
        "base": f"/workspaces/{ws}/sessions/{sid}",
        "fac": _client(db, ctx["fac"]),
        "a": _client(db, ctx["participants"][0]),
        "owner": _client(db, ctx["owner"]),
        "outsider": _client(db, ctx["outsider"]),
        "stranger": _client(db, stranger),
    }


def _pos(client: TestClient, w: dict[str, Any]) -> dict[str, Any]:
    return client.get(f"{w['base']}/position").json()


def _begin(client: TestClient, w: dict[str, Any], version: int | None = None) -> Any:
    if version is None:
        version = _pos(w["fac"], w)["session"]["version"]
    return client.post(
        f"{w['base']}/transitions/begin-analysis",
        headers=_idem(),
        json={"expectedVersion": version},
    )


def _request(client: TestClient, w: dict[str, Any], path: str, case: str) -> Any:
    version = _pos(w["fac"], w)["session"]["version"]
    return client.post(
        f"{w['base']}/{path}", headers=_idem(), json={"expectedVersion": version, "case": case}
    )


def test_h1_h2_h3_g1_g3_g4_begin_and_derived_field(f04_app: sa.Connection) -> None:
    w = _world(f04_app)
    before = _pos(w["a"], w)
    assert before["actions"]["BEGIN_ANALYSIS"]["available"] is False  # participant
    assert _pos(w["fac"], w)["actions"]["BEGIN_ANALYSIS"]["available"] is True
    human = before["questionSet"]["frozen"]["questions"]

    r = _begin(w["fac"], w)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "committed" and body["commandType"] == "CMD_BEGIN_ANALYSIS"
    assert body["analysis"]["status"] == "ACCEPTED"
    assert body["analysis"]["next"]["status"] == "ACCEPTED"
    pos = body["position"]
    assert pos["session"]["state"] == "ANALYSIS"
    assert pos["establishedBy"]["commandType"] == "CMD_BEGIN_ANALYSIS"

    # G1 / H3: every member of the frozen-set audience sees the same derived field
    views = [_pos(w[n], w)["analysis"] for n in ("fac", "a", "owner", "outsider")]
    assert all(v == views[0] for v in views)
    analysis = views[0]
    assert analysis["visible"] is True
    # G3 / F2: AI origin, generation refs and the MOCK marker
    assert (
        analysis["marker"]["origin"] == "AI" and analysis["marker"]["proof"] == "MOCK / NON_PROOF"
    )
    artifact = analysis["analysis"]["artifact"]
    assert artifact["isMockNonProof"] is True and artifact["marker"]["isMock"] is True
    assert artifact["generationId"] in {g["generationId"] for g in analysis["generations"]}
    assert all(g["provider"] == "mock" for g in analysis["generations"])
    assert "additional_questions" not in artifact["content"]
    ids = {q["questionId"] for q in human}
    assert {p["question_id"] for p in artifact["content"]["classification_proposals"]} <= ids
    # clusters after acceptance (H6), only frozen Questions
    clusters = analysis["clustering"]["clusters"]
    assert clusters and {q for c in clusters for q in c["questionIds"]} <= ids
    # G4: the human Questions are unchanged and separate
    after = _pos(w["a"], w)["questionSet"]["frozen"]["questions"]
    assert after == human
    # no controls for a participant (H3 / H5)
    actions = _pos(w["a"], w)["actions"]
    for name in ("BEGIN_ANALYSIS", "REQUEST_QUESTION_ANALYSIS", "REQUEST_QUESTION_CLUSTERING"):
        assert actions[name]["available"] is False


def test_g2_an_outsider_is_denied(f04_app: sa.Connection) -> None:
    w = _world(f04_app)
    _begin(w["fac"], w)
    r = w["stranger"].get(f"{w['base']}/position")
    assert r.status_code == 403 and r.json()["kind"] == "denied"


def test_h5_non_controllers_cannot_begin(f04_app: sa.Connection) -> None:
    w = _world(f04_app)
    for name in ("a", "owner", "outsider"):
        r = _begin(w[name], w)
        assert r.status_code == 403 and r.json()["kind"] == "denied", name
    assert _pos(w["fac"], w)["session"]["state"] == "QUESTION_CAPTURE"


def test_h4_g5_failed_run_is_honest_then_controller_retry(
    f04_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    w = _world(f04_app)
    monkeypatch.setattr(http_f04, "_runtime", mock_runtime({A1: MockProviderOutcome.TIMEOUT}))
    r = _begin(w["fac"], w)
    assert r.status_code == 200 and r.json()["kind"] == "committed"  # the transition stands
    assert r.json()["analysis"]["status"] == "FAILED"
    pos = _pos(w["a"], w)
    assert pos["session"]["state"] == "ANALYSIS"
    assert pos["analysis"]["analysis"]["status"] == "UNAVAILABLE"
    assert pos["analysis"]["clustering"]["status"] == "NOT_RUN"  # H6 / K7
    assert pos["analysis"]["clustering"]["clusters"] == []
    assert pos["questionSet"]["visibility"] == "FULL_FROZEN_SET"  # F3: still readable
    # G5: the RETRY capability is the controller's only, with its case
    assert pos["actions"]["REQUEST_QUESTION_ANALYSIS"]["available"] is False
    cap = _pos(w["fac"], w)["actions"]["REQUEST_QUESTION_ANALYSIS"]
    assert cap["available"] is True and cap["case"] == "RETRY"
    for name in ("a", "owner"):
        assert _request(w[name], w, "analysis/request", "RETRY").status_code == 403
    # E18 over HTTP: the wrong case is rejected, not corrected
    wrong = _request(w["fac"], w, "analysis/request", "RECOVERY")
    assert wrong.status_code == 400 and wrong.json()["reasonCode"] == "REQUEST_CASE_MISMATCH:RETRY"

    monkeypatch.setattr(http_f04, "_runtime", mock_runtime())
    ok = _request(w["fac"], w, "analysis/request", "RETRY")
    assert ok.status_code == 200, ok.text
    assert ok.json()["case"] == "RETRY" and ok.json()["analysis"]["status"] == "ACCEPTED"
    final = _pos(w["fac"], w)
    assert final["analysis"]["analysis"]["status"] == "ACCEPTED"
    assert final["actions"]["REQUEST_QUESTION_ANALYSIS"]["available"] is False
    assert final["actions"]["REQUEST_QUESTION_ANALYSIS"]["reasonCode"] == "RESULT_ALREADY_ACCEPTED"


def test_unavailable_provider_then_recovery_over_http(
    f04_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    w = _world(f04_app)
    monkeypatch.setattr(http_f04, "_runtime", UNAVAILABLE)
    r = _begin(w["fac"], w)
    assert r.status_code == 200
    assert r.json()["analysis"]["reasonCode"] == "AI_PROVIDER_UNAVAILABLE"
    pos = _pos(w["fac"], w)
    assert pos["analysis"]["analysis"]["status"] == "PENDING"
    assert pos["actions"]["REQUEST_QUESTION_ANALYSIS"]["case"] == "RECOVERY"
    monkeypatch.setattr(http_f04, "_runtime", mock_runtime())
    ok = _request(w["fac"], w, "analysis/request", "RECOVERY")
    assert ok.status_code == 200 and ok.json()["analysis"]["status"] == "ACCEPTED"


def test_clustering_retry_over_http(
    f04_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    w = _world(f04_app)
    monkeypatch.setattr(
        http_f04, "_runtime", mock_runtime({A2: MockProviderOutcome.PROVIDER_ERROR})
    )
    _begin(w["fac"], w)
    pos = _pos(w["fac"], w)
    assert pos["analysis"]["clustering"]["status"] == "UNAVAILABLE"
    assert pos["actions"]["REQUEST_QUESTION_CLUSTERING"]["case"] == "RETRY"
    monkeypatch.setattr(http_f04, "_runtime", mock_runtime())
    ok = _request(w["fac"], w, "analysis/clustering/request", "RETRY")
    assert ok.status_code == 200 and ok.json()["analysis"]["status"] == "ACCEPTED"
    assert _pos(w["a"], w)["analysis"]["clustering"]["status"] == "ACCEPTED"


def test_begin_is_idempotent_over_http_and_replay_runs_nothing(f04_app: sa.Connection) -> None:
    w = _world(f04_app)
    version = _pos(w["fac"], w)["session"]["version"]
    key = {"Idempotency-Key": str(uuid.uuid4())}
    first = w["fac"].post(
        f"{w['base']}/transitions/begin-analysis", headers=key, json={"expectedVersion": version}
    )
    again = w["fac"].post(
        f"{w['base']}/transitions/begin-analysis", headers=key, json={"expectedVersion": version}
    )
    assert first.json()["replayed"] is False and again.json()["replayed"] is True
    assert again.json()["analysis"] is None  # rule 5: nothing executes on a replay
    assert len(f04.generations(f04_app, w["ctx"], "AIOP-001")) == 1


def test_malformed_inputs_are_rejected(f04_app: sa.Connection) -> None:
    w = _world(f04_app)
    r = w["fac"].post(f"{w['base']}/transitions/begin-analysis", headers=_idem(), json={})
    assert r.status_code == 400 and r.json()["reasonCode"] == "EXPECTED_VERSION_REQUIRED"
    _begin(w["fac"], w)
    r = _request(w["fac"], w, "analysis/request", "PLEASE")
    assert r.status_code == 400 and r.json()["reasonCode"] == "REQUEST_CASE_REQUIRED"
    r = w["fac"].post(f"{w['base']}/transitions/begin-analysis", json={"expectedVersion": 1})
    assert r.status_code == 400 and r.json()["reasonCode"] == "IDEMPOTENCY_KEY_REQUIRED"
