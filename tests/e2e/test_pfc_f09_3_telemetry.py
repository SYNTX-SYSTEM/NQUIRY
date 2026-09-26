"""WU-PFC-F09-3 (F09): telemetry never interferes; governed Commands are correlated.

Architecture: 19 §29 (internal Work Unit "observability correlation"; TESTS
FIRST "telemetry sink failure"); 11 §36 (AC-11-013: "OBSERVABILITY RECONSTRUCTS
TECHNICAL BEHAVIOR. OBSERVABILITY DOES NOT DEFINE DOMAIN TRUTH OR AUTHORITY"),
§37 (correlation model: correlation_id, command_id, attempt_id, commit_id ...
"traceable across API edge, Command processing ... CommitUnit"), §38 (trace
context never carries authority or content); 12 §20 ("Operational log
unavailable -> Audit record remains separately reconstructable"), §25 (minimum
causal chain request -> correlation -> command -> attempt -> commit).

FIRST BROKEN RELATION (before this Work Unit): `LocalOtelObservationSink.emit`
lets any tracer failure escape. The worker's delivery loop and `/healthz` call
it unguarded, so a telemetry outage stops delivery or fails liveness. Governed
Commands emit no observation at all: the 12 §25 chain has no operational trace
at the API edge.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from persistence.tables import challenges_table
from test_http_f02 import _client

db_app = http_f02.db_app


class _BrokenTracer:
    def start_as_current_span(self, *_a: Any, **_k: Any) -> Any:
        raise RuntimeError("telemetry exporter unavailable")


class _Recording:
    def __init__(self) -> None:
        self.contexts: list[Any] = []

    def emit(self, context: Any) -> None:
        self.contexts.append(context)


def _broken_sink() -> Any:
    from observability.context import LocalOtelObservationSink

    sink = LocalOtelObservationSink(tracer_name="test.broken")
    sink._tracer = _BrokenTracer()  # type: ignore[assignment]
    return sink


def test_a_failing_tracer_never_escapes_the_sink(capsys: pytest.CaptureFixture[str]) -> None:
    from observability.context import ObservationContext
    from semantic_types.ids import CorrelationId

    _broken_sink().emit(
        ObservationContext(correlation_id=CorrelationId(uuid.uuid4()), operation="x")
    )
    assert "observability" in capsys.readouterr().err


def test_liveness_survives_a_telemetry_outage(monkeypatch: pytest.MonkeyPatch) -> None:
    import nquiry_api.main as main
    from fastapi.testclient import TestClient

    monkeypatch.setattr(main, "_observation_sink", _broken_sink())
    r = TestClient(main.app).get("/healthz")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_a_governed_command_commits_despite_a_telemetry_outage(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    import application.http_f02 as dispatch

    monkeypatch.setattr(dispatch, "_observation_sink", _broken_sink())
    ctx = f02.inquiry_context(db_app)
    r = _client(db_app, ctx["fac"]).post(
        f"/workspaces/{ctx['ws'].value}/challenges",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={"title": "Committed while telemetry is down"},
    )
    assert r.status_code == 200 and r.json()["kind"] == "committed", r.text
    cid = uuid.UUID(r.json()["challengeId"])
    assert (
        db_app.execute(
            sa.select(sa.func.count())
            .select_from(challenges_table)
            .where(challenges_table.c.id == cid)
        ).scalar_one()
        == 1
    )


def test_the_worker_pass_survives_a_telemetry_outage(monkeypatch: pytest.MonkeyPatch) -> None:
    import os

    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; this test runs a real delivery pass")
    import nquiry_worker.__main__ as worker

    monkeypatch.setattr(worker, "_observation_sink", _broken_sink())
    assert worker.main(["--once"]) == 0


def test_every_governed_command_is_correlated_with_its_identities(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    import application.http_f02 as dispatch

    recording = _Recording()
    monkeypatch.setattr(dispatch, "_observation_sink", recording)
    ctx = f02.inquiry_context(db_app)
    key = str(uuid.uuid4())
    r = _client(db_app, ctx["fac"]).post(
        f"/workspaces/{ctx['ws'].value}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "Correlated"},
    )
    assert r.json()["kind"] == "committed"
    (observed,) = recording.contexts
    assert observed.operation == "http.command.committed"
    assert str(observed.command_id.value) == key
    assert observed.attempt_id is not None and observed.commit_id is not None
    audit_commit = db_app.execute(
        sa.text("SELECT commit_id, correlation_id FROM audit_events WHERE command_id = :c"),
        {"c": uuid.UUID(key)},
    ).one()
    assert observed.commit_id.value == audit_commit.commit_id
    assert observed.correlation_id.value == audit_commit.correlation_id


def test_a_denied_command_is_correlated_without_a_commit(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    import application.http_f02 as dispatch

    recording = _Recording()
    monkeypatch.setattr(dispatch, "_observation_sink", recording)
    ctx = f02.inquiry_context(db_app)
    key = str(uuid.uuid4())
    r = _client(db_app, ctx["owner"]).post(  # Owner may not create a Challenge (F02)
        f"/workspaces/{ctx['ws'].value}/challenges",
        headers={"Idempotency-Key": key},
        json={"title": "Denied"},
    )
    assert r.json()["kind"] == "denied"
    (observed,) = recording.contexts
    assert observed.operation == "http.command.denied"
    assert str(observed.command_id.value) == key and observed.commit_id is None


def test_the_trace_carries_no_authority_and_no_content(
    db_app: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    """11 §38: only identities and the outcome; never the title, the actor or a binding."""
    import application.http_f02 as dispatch

    recording = _Recording()
    monkeypatch.setattr(dispatch, "_observation_sink", recording)
    ctx = f02.inquiry_context(db_app)
    _client(db_app, ctx["fac"]).post(
        f"/workspaces/{ctx['ws'].value}/challenges",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={"title": "SECRET-TITLE-TEXT"},
    )
    rendered = repr(recording.contexts)
    assert "SECRET-TITLE-TEXT" not in rendered
    assert str(ctx["fac"].value) not in rendered
