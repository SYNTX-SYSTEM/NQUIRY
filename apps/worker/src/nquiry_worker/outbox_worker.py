"""OutboxWorker: transactional-outbox delivery loop.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 15.2 (At-Least-Once
Delivery), section 122 (AC-09-010: "broker delivery failure does not
roll back already COMMITTED canonical state ... does require outbox
retry/observability"); 10_FAILURE_RECOVERY_ROLLBACK.md section 17
(F-OUT: "retry outbox delivery / deduplicate consumer delivery /
rebuild event-delivery projection" are legitimate recovery; "repeat
domain Command / repeat external consequence merely because Event
delivery failed" are not), section 31 (RC-01 deterministic technical
recovery: "resume transactional-outbox delivery" / "deduplicate known
repeated delivery" are named SYSTEM_SERVICE-eligible examples -- this
worker IS that recovery operation, run continuously rather than
on-demand); 14_IMPLEMENTATION_SEQUENCE.md section 28 ("Outbox retry is
delivery retry, not domain retry"), section 41 ("event consumer cannot
import direct consequential handler").

WHY THIS FILE IMPORTS ONLY `events`/`semantic_types`, NEVER
`command`/`commit`/`persistence`
--------------------------------------------------------------------
`nquiry_worker`'s own 14 section 3.1 package-level ceiling is
`{events, projection, recovery, command, commit, semantic_types}` --
wide enough for a *future* `recovery_worker.py` sibling that genuinely
needs governed recovery Commands. That package-level ceiling does NOT
mean every file under `apps/worker/src/nquiry_worker/` may use all of
it: 14 section 41's own dedicated rule ("event consumer cannot import
direct consequential handler") is a FILE-level constraint the generic
`check_architecture_dependencies.py` package-level checker cannot see.
`tests/security/test_outbox_worker_exclusivity.py` proves, by scanning this file's
own real AST, that it imports none of `command`, `commit`,
`persistence` -- the same P-23-style dynamic proof PKG-19 already
established for `MockProviderAdapter` exclusivity.

WHY `EventEnvelopeSource` IS A CALLER-SUPPLIED PORT, NOT AN INTERNAL LOOKUP
--------------------------------------------------------------------
See `events.envelope`'s own module docstring: no durable path from a
bare `OutboxRecord.commit_id` to a fully historically faithful
`EventEnvelope` exists yet in this codebase (`aggregate_ref`,
`aggregate_version_after_commit`, `correlation_id`, `causation_id`,
`actor_ref`, `authority_source_ref` and `payload` are not all jointly
recoverable from any table `events`/`nquiry_worker` may import). This
worker proves the DELIVERY LOOP's own mechanics (due-selection,
publish, mark-delivered/failed, retry-is-not-domain-retry,
idempotent-redelivery-safety) against a real `OutboxRepository`, using
a caller-supplied resolver for the one part of the pipeline
(`OutboxRecord -> EventEnvelope`) that remains `SUCCESSOR_NOT_BUILT`.

SUCCESSOR TRUTH (WU-PFC-F08-1/F08-2): the resolver now exists as
`persistence.committed_event_repository.CommittedEventEnvelopeSource`,
backed by the immutable `committed_events` basis written in every
CommitUnit. It is wired into the running worker by
`nquiry_worker.delivery.run_delivery_pass`. This file's own mechanics and
import exclusivity are unchanged.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol, runtime_checkable

from events.envelope import EventEnvelope, EventPublisher
from events.outbox import OutboxRecord, OutboxRepository
from semantic_types.clock import Clock


class EventDeliveryFailure(Exception):
    """Raised by an `EventPublisher` when one delivery attempt did not
    succeed. The ONLY exception `OutboxWorker` catches per-record -- no
    catch-all, per 14's own "no catch-all retry" prohibition.
    """


@runtime_checkable
class EventEnvelopeSource(Protocol):
    """Resolves the `EventEnvelope` a due `OutboxRecord` describes.
    See this module's own docstring for why this is a caller-supplied
    port rather than an internal lookup.
    """

    def resolve(self, record: OutboxRecord) -> EventEnvelope: ...


@dataclass(frozen=True, slots=True)
class OutboxDeliveryBatchResult:
    """Outcome of one `OutboxWorker.deliver_due()` pass. Never a bare
    boolean/count -- each outbox_id is individually reconstructable,
    matching this codebase's "no unversioned consequential dict
    payloads" discipline.
    """

    delivered: tuple[uuid.UUID, ...]
    failed: tuple[uuid.UUID, ...]


class OutboxWorker:
    """SYSTEM_SERVICE-class deterministic recovery (10 section 31,
    RC-01): resumes transactional-outbox delivery and deduplicates
    already-delivered facts. Creates no new domain choice, invents no
    authority, and never re-enters the governed Command/CommitUnit
    write path -- see this module's own docstring and
    `tests/security/test_outbox_worker_exclusivity.py` for the structural proof.
    """

    def __init__(
        self,
        *,
        outbox_repository: OutboxRepository,
        envelope_source: EventEnvelopeSource,
        publisher: EventPublisher,
        clock: Clock,
    ) -> None:
        self._outbox_repository = outbox_repository
        self._envelope_source = envelope_source
        self._publisher = publisher
        self._clock = clock

    def deliver_due(self, *, retry_backoff_seconds: int = 300) -> OutboxDeliveryBatchResult:
        """One deterministic delivery pass. Idempotent to call
        repeatedly (worker-restart safe): a record already DELIVERED is
        never selected by `list_due_for_delivery` in the first place,
        and a record delivered successfully here is marked DELIVERED
        before this method returns, so a re-run never re-publishes it.
        """

        now = self._clock.now()
        due_records = self._outbox_repository.list_due_for_delivery(now=now)

        delivered: list[uuid.UUID] = []
        failed: list[uuid.UUID] = []
        for record in due_records:
            try:
                envelope = self._envelope_source.resolve(record)
                self._publisher.publish(envelope)
            except EventDeliveryFailure:
                self._outbox_repository.mark_failed_delivery(
                    record.outbox_id,
                    next_attempt_at=self._clock.now() + timedelta(seconds=retry_backoff_seconds),
                )
                failed.append(record.outbox_id)
                continue
            self._outbox_repository.mark_delivered(record.outbox_id, delivered_at=self._clock.now())
            delivered.append(record.outbox_id)

        return OutboxDeliveryBatchResult(delivered=tuple(delivered), failed=tuple(failed))


__all__ = [
    "EventDeliveryFailure",
    "EventEnvelopeSource",
    "OutboxDeliveryBatchResult",
    "OutboxWorker",
]
