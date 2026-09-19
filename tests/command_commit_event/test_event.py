"""T7 EVENT TEST: EventEnvelope construction, versioning and
serialization -- pure, no database.

14 section 48's own file-level implementation map assigns
`tests/command_commit_event/test_event.py` to `packages/events/envelope.py`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from events.envelope import (
    EventConsumer,
    EventEnvelope,
    EventEnvelopeSerializationError,
    EventPublisher,
    build_event_envelope,
    event_envelope_from_json,
    event_envelope_to_json,
)
from semantic_types.ids import (
    CausationId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_SCHEMA_VERSION = ContractVersion("1.0")


def _envelope(**overrides: object) -> EventEnvelope:
    fields: dict[str, object] = {
        "event_id": EventId(uuid.uuid4()),
        "event_type": "SESSION_TRANSITIONED",
        "event_schema_version": _SCHEMA_VERSION,
        "occurred_at": _NOW,
        "workspace_scope_ref": WorkspaceId(uuid.uuid4()),
        "aggregate_ref": "session:1",
        "aggregate_version_after_commit": RecordVersion(2),
        "command_id": CommandId(uuid.uuid4()),
        "commit_id": CommitId(uuid.uuid4()),
        "correlation_id": CorrelationId(uuid.uuid4()),
        "actor_ref": "HUMAN_USER:user-ref-1",
        "authority_source_ref": uuid.uuid4(),
        "payload": {"note": "hello"},
    }
    fields.update(overrides)
    return build_event_envelope(**fields)  # type: ignore[arg-type]


def test_constructs_a_well_formed_event_envelope() -> None:
    envelope = _envelope()
    assert envelope.causation_id is None
    assert envelope.event_type == "SESSION_TRANSITIONED"


def test_denies_empty_event_type() -> None:
    with pytest.raises(ValueError, match="event_type"):
        _envelope(event_type="")


def test_denies_empty_aggregate_ref() -> None:
    with pytest.raises(ValueError, match="aggregate_ref"):
        _envelope(aggregate_ref="")


def test_denies_empty_actor_ref() -> None:
    with pytest.raises(ValueError, match="actor_ref"):
        _envelope(actor_ref="")


def test_command_id_cannot_masquerade_as_event_id() -> None:
    """Mandatory adversarial attack (P-16): Command != Event. A
    structurally different strong identity cannot substitute for
    `event_id`, mirroring `CommandEnvelope.__post_init__`'s identical
    defense (PKG-10).
    """
    with pytest.raises(TypeError, match="event_id"):
        _envelope(event_id=CommandId(uuid.uuid4()))


def test_causation_id_rejects_wrong_type() -> None:
    with pytest.raises(TypeError, match="causation_id"):
        _envelope(causation_id=CorrelationId(uuid.uuid4()))


def test_causation_id_is_optional_and_accepted_when_present() -> None:
    envelope = _envelope(causation_id=CausationId(uuid.uuid4()))
    assert isinstance(envelope.causation_id, CausationId)


def test_event_envelope_has_no_execution_or_authority_capability() -> None:
    """09 section 16.2: "Event Does Not Mean: execute again / authorize
    another command / grant authority / prove domain truth." Structural
    proof: the type's own method surface has no such capability at all.
    """
    forbidden_names = {"execute", "authorize", "grant_authority", "apply", "commit", "run"}
    public_methods = {
        name
        for name in dir(EventEnvelope)
        if not name.startswith("_") and callable(getattr(EventEnvelope, name, None))
    }
    assert not forbidden_names & public_methods


def test_serialization_round_trip_produces_an_equal_envelope() -> None:
    envelope = _envelope(causation_id=CausationId(uuid.uuid4()))
    raw = event_envelope_to_json(envelope)
    restored = event_envelope_from_json(raw, supported_schema_version=_SCHEMA_VERSION)
    assert restored == envelope


def test_deserialization_rejects_malformed_json() -> None:
    with pytest.raises(EventEnvelopeSerializationError, match="malformed"):
        event_envelope_from_json("not json", supported_schema_version=_SCHEMA_VERSION)


def test_deserialization_rejects_mismatched_schema_version() -> None:
    envelope = _envelope(event_schema_version=ContractVersion("2.0"))
    raw = event_envelope_to_json(envelope)
    with pytest.raises(EventEnvelopeSerializationError, match="unsupported"):
        event_envelope_from_json(raw, supported_schema_version=_SCHEMA_VERSION)


def test_deserialization_rejects_a_missing_required_field() -> None:
    envelope = _envelope()
    raw = event_envelope_to_json(envelope)
    import json

    data = json.loads(raw)
    del data["aggregate_ref"]
    with pytest.raises(EventEnvelopeSerializationError, match="malformed"):
        event_envelope_from_json(json.dumps(data), supported_schema_version=_SCHEMA_VERSION)


def test_event_publisher_and_consumer_are_structural_protocols() -> None:
    class _Publisher:
        def publish(self, envelope: EventEnvelope) -> None: ...

    class _Consumer:
        def handle(self, envelope: EventEnvelope) -> None: ...

    assert isinstance(_Publisher(), EventPublisher)
    assert isinstance(_Consumer(), EventConsumer)
