"""Deterministic `EventPublisher`/`EventEnvelopeSource`/`EventConsumer`
test doubles.

TEST ONLY. Must never be imported by production code -- see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`.

Mirrors `test_support.failure_injector`'s own relationship to
`commit.coordinator`: the Protocols (`events.envelope.EventPublisher`/
`EventConsumer`, `apps/worker/src/nquiry_worker/outbox_worker.
EventEnvelopeSource`) are production-importable; these concrete,
fully-deterministic doubles are not.
"""

from __future__ import annotations

import uuid

from events.envelope import EventEnvelope
from events.outbox import OutboxRecord
from nquiry_worker.outbox_worker import EventDeliveryFailure


class StaticEventEnvelopeSource:
    """Resolves a due `OutboxRecord` to a pre-built `EventEnvelope` via
    an explicit `outbox_id -> EventEnvelope` mapping the test controls.
    Real production envelope assembly from a bare `commit_id` remains
    `SUCCESSOR_NOT_BUILT` (see `events.envelope`'s own module
    docstring) -- this double never fabricates that join, it only
    hands back exactly what the test already built with
    `events.envelope.build_event_envelope`.
    """

    def __init__(self, envelopes_by_outbox_id: dict[uuid.UUID, EventEnvelope]) -> None:
        self._envelopes_by_outbox_id = dict(envelopes_by_outbox_id)

    def resolve(self, record: OutboxRecord) -> EventEnvelope:
        return self._envelopes_by_outbox_id[record.outbox_id]


class ScriptedEventPublisher:
    """Raises `EventDeliveryFailure` for every `event_id` in
    `fail_for_event_ids` (checked once, then removed -- a second
    delivery attempt for the same id succeeds, modeling a transient
    failure a retry legitimately recovers from); records every
    envelope it was actually asked to publish, in order, so a test can
    assert exactly what -- and how many times -- was delivered.
    """

    def __init__(self, *, fail_for_event_ids: frozenset[uuid.UUID] = frozenset()) -> None:
        self._fail_for_event_ids = set(fail_for_event_ids)
        self.published: list[EventEnvelope] = []

    def publish(self, envelope: EventEnvelope) -> None:
        event_id_value = envelope.event_id.value
        if event_id_value in self._fail_for_event_ids:
            self._fail_for_event_ids.discard(event_id_value)
            raise EventDeliveryFailure(f"scripted delivery failure for event {event_id_value}")
        self.published.append(envelope)


class RecordingIdempotentConsumer:
    """Reference `EventConsumer` satisfying 09 section 15.2's own
    obligation ("must not produce duplicate consequential effects
    solely because delivery repeats"): deduplicates by `event_id`, the
    envelope's own durable identity, not by object identity or call
    count. `effects_applied` only ever grows once per distinct
    `event_id`, however many times `handle()` is actually called for
    it.
    """

    def __init__(self) -> None:
        self.effects_applied: list[EventEnvelope] = []
        self.duplicate_deliveries_ignored = 0
        self._seen_event_ids: set[uuid.UUID] = set()

    def handle(self, envelope: EventEnvelope) -> None:
        event_id_value = envelope.event_id.value
        if event_id_value in self._seen_event_ids:
            self.duplicate_deliveries_ignored += 1
            return
        self._seen_event_ids.add(event_id_value)
        self.effects_applied.append(envelope)


__all__ = [
    "StaticEventEnvelopeSource",
    "ScriptedEventPublisher",
    "RecordingIdempotentConsumer",
]
