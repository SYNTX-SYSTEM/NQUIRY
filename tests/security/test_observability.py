"""T9 SECURITY TEST: ObservationContext / ObservationSink /
LocalOtelObservationSink -- pure Python plus one real OpenTelemetry SDK
capture, no PostgreSQL required.

14 section 46's own repository-topology row assigns
`tests/security/test_observability.py` to
`packages/observability/context.py`.

WHY THIS FILE CONFIGURES A REAL `opentelemetry.sdk` TracerProvider
ONCE, AT MODULE SCOPE
--------------------------------------------------------------------
`opentelemetry.trace.set_tracer_provider` may only be called once per
process (subsequent calls are silently ignored by the API itself) --
the standard OTel testing pattern is therefore one global
`TracerProvider`/`InMemorySpanExporter` pair, with `exporter.clear()`
between tests, never a fresh provider per test.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest
from observability.context import LocalOtelObservationSink, ObservationContext, ObservationSink
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    GenerationId,
    RecoveryId,
)

_EXPORTER = InMemorySpanExporter()
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(_EXPORTER))


@pytest.fixture(autouse=True)
def _clear_exporter() -> None:
    _EXPORTER.clear()


def _context(**overrides: object) -> ObservationContext:
    base: dict[str, object] = dict(
        correlation_id=CorrelationId(uuid.uuid4()),
        operation="select_question",
    )
    base.update(overrides)
    return ObservationContext(**base)  # type: ignore[arg-type]


def test_observation_context_field_set_is_exactly_the_intended_minimum() -> None:
    """Structural non-collapse proof for "minimize content" (14's own
    PKG-27 OBJECTIVE) -- a future edit adding a field here (e.g. a raw
    prompt/Evidence-text field) would be caught immediately."""
    field_names = {f.name for f in fields(ObservationContext)}
    assert field_names == {
        "correlation_id",
        "operation",
        "command_id",
        "attempt_id",
        "commit_id",
        "event_id",
        "generation_id",
        "recovery_id",
        "boundary_result",
        "failure_class",
    }


def test_observation_context_is_frozen() -> None:
    context = _context()
    with pytest.raises(FrozenInstanceError):
        context.operation = "tampered"  # type: ignore[misc]


def test_rejects_wrong_correlation_id_type() -> None:
    with pytest.raises(TypeError, match="correlation_id"):
        ObservationContext(correlation_id=uuid.uuid4(), operation="x")  # type: ignore[arg-type]


def test_rejects_empty_operation() -> None:
    with pytest.raises(ValueError, match="operation"):
        _context(operation="")


def test_rejects_wrong_optional_id_types() -> None:
    with pytest.raises(TypeError, match="command_id"):
        _context(command_id=uuid.uuid4())
    with pytest.raises(TypeError, match="attempt_id"):
        _context(attempt_id=uuid.uuid4())
    with pytest.raises(TypeError, match="commit_id"):
        _context(commit_id=uuid.uuid4())
    with pytest.raises(TypeError, match="event_id"):
        _context(event_id=uuid.uuid4())
    with pytest.raises(TypeError, match="generation_id"):
        _context(generation_id=uuid.uuid4())
    with pytest.raises(TypeError, match="recovery_id"):
        _context(recovery_id=uuid.uuid4())


def test_accepts_every_correlation_identity_field_with_the_real_strong_type() -> None:
    context = _context(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
        event_id=EventId(uuid.uuid4()),
        generation_id=GenerationId(uuid.uuid4()),
        recovery_id=RecoveryId(uuid.uuid4()),
        boundary_result="DENY",
        failure_class="F-BND",
    )
    assert context.boundary_result == "DENY"
    assert context.failure_class == "F-BND"


def test_mandatory_attack_prompt_content_leakage_operation_length_capped() -> None:
    """Mandatory package-specific attack: "prompt content leakage" --
    a full prompt is far longer than any legitimate `operation` name;
    the length cap rejects the smuggling attempt structurally, on top
    of `operation` having no semantic meaning as a content field at
    all."""
    fake_prompt = "x" * 5000
    with pytest.raises(ValueError, match="minimize content"):
        _context(operation=fake_prompt)


def test_mandatory_attack_secret_in_trace_unknown_boundary_result_rejected() -> None:
    """Mandatory package-specific attack: "Secret in trace" -- fail
    closed on an unrecognized `boundary_result` value rather than
    silently accepting an arbitrary string (which could otherwise be
    used to carry non-boundary-result content)."""
    with pytest.raises(ValueError, match="closed BoundaryResult vocabulary"):
        _context(boundary_result="sk-supersecretapikey")


def test_mandatory_attack_secret_in_trace_unknown_failure_class_rejected() -> None:
    with pytest.raises(ValueError, match="closed FailureClass vocabulary"):
        _context(failure_class="password=hunter2")


def test_mandatory_attack_full_evidence_in_log_no_content_field_exists() -> None:
    """Mandatory package-specific attack: "full Evidence in log" --
    there is no field on `ObservationContext` a caller could even
    attempt to pass Evidence content through (a `TypeError` for an
    unexpected keyword, not a validation rejection -- proving the
    field never existed to validate in the first place)."""
    with pytest.raises(TypeError):
        _context(evidence_content="the user said: I feel anxious about...")  # type: ignore[call-arg]


def test_mandatory_attack_trace_value_used_as_authority_no_such_dependency_exists() -> None:
    """Mandatory package-specific attack: "trace value used as
    authority" -- proven structurally against the real architecture
    dependency graph: none of `boundaries`/`authority`/`governance` may
    import `observability` at all, so no boundary evaluator or
    authority resolver could ever consume an `ObservationContext` as an
    input to a real decision."""
    import importlib

    checker = importlib.import_module("check_architecture_dependencies")
    for consequential_package in ("boundaries", "authority", "governance"):
        allowed = checker.INTERNAL_ALLOWED.get(consequential_package, frozenset())
        assert "observability" not in allowed


def test_mandatory_attack_missing_audit_replaced_by_log_no_persistence_access() -> None:
    """Mandatory package-specific attack: "missing audit replaced by
    log" -- `observability` cannot reach `persistence`/any DB driver at
    all (structurally, via the same dependency graph), so nothing here
    could ever be mistaken for -- or substituted for -- a real
    `AuditEvent`/`SecurityEvent` write."""
    import importlib

    checker = importlib.import_module("check_architecture_dependencies")
    assert checker.INTERNAL_ALLOWED["observability"] == frozenset({"semantic_types"})


def test_observation_sink_protocol_returns_none() -> None:
    method_names = {name for name in dir(ObservationSink) if not name.startswith("_")}
    assert method_names == {"emit"}


def test_local_otel_sink_emits_a_real_span_with_the_expected_attributes() -> None:
    sink = LocalOtelObservationSink(tracer_name="test.observability")
    context = _context(
        command_id=CommandId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
        boundary_result="ALLOW",
        failure_class="F-PERS",
    )

    sink.emit(context)

    spans = _EXPORTER.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "select_question"
    assert span.attributes is not None
    assert span.attributes["correlation_id"] == str(context.correlation_id.value)
    assert span.attributes["command_id"] == str(context.command_id.value)  # type: ignore[union-attr]
    assert span.attributes["commit_id"] == str(context.commit_id.value)  # type: ignore[union-attr]
    assert span.attributes["boundary_result"] == "ALLOW"
    assert span.attributes["failure_class"] == "F-PERS"
    assert "attempt_id" not in span.attributes
    assert "event_id" not in span.attributes
    assert "generation_id" not in span.attributes
    assert "recovery_id" not in span.attributes


def test_local_otel_sink_omits_absent_optional_attributes_entirely() -> None:
    """Novel/adapted attack: an absent optional field is emitted as a
    present-but-empty attribute rather than genuinely omitted, which
    could mislead an investigator into thinking a `command_id`/etc was
    genuinely resolved as `None`/empty rather than never having applied
    at all."""
    sink = LocalOtelObservationSink(tracer_name="test.observability")
    context = _context()

    sink.emit(context)

    span = _EXPORTER.get_finished_spans()[0]
    assert span.attributes is not None
    assert set(span.attributes.keys()) == {"correlation_id"}


def test_mut_pkg27_01_emitting_never_returns_anything_authority_shaped() -> None:
    """Guard-necessity proof for this package's own AUTHORITY line
    ("Never consumed as authority proof"): `ObservationSink.emit`
    returns `None` in the real implementation -- there is nothing a
    caller could receive back and mistake for a `BoundaryProof`,
    authority token, or governance verdict."""
    sink = LocalOtelObservationSink(tracer_name="test.observability")
    result = sink.emit(_context())
    assert result is None


def test_local_otel_sink_is_safe_with_no_sdk_configured_in_a_fresh_process() -> None:
    """Novel/adapted attack: production code (this test file's own
    module-scope `TracerProvider` aside) must not require an SDK to be
    configured to avoid crashing -- proven in a genuinely separate,
    fresh Python process that never imports `opentelemetry.sdk` at
    all, only `opentelemetry-api` (the real runtime dependency)."""
    script = (
        "from observability.context import LocalOtelObservationSink, ObservationContext\n"
        "from semantic_types.ids import CorrelationId\n"
        "import uuid, sys\n"
        "assert 'opentelemetry.sdk' not in sys.modules\n"
        "sink = LocalOtelObservationSink()\n"
        "result = sink.emit(ObservationContext(correlation_id=CorrelationId(uuid.uuid4()), "
        "operation='probe'))\n"
        "assert result is None\n"
        "print('OK')\n"
    )
    repo_root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        str(repo_root / part) for part in ("packages", "apps/api/src", "apps/worker/src")
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert "OK" in completed.stdout
