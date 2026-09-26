"""The running delivery pipeline: outbox -> exact EventEnvelope -> projection,
plus replay/rebuild (WU-PFC-F08-2, F08).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 28;
09_DATA_EVENT_API_CONTRACTS.md section 15 (at-least-once; PENDING /
DELIVERED / FAILED_DELIVERY), section 18 (replay may rebuild projections only),
section 74 (consumers dedupe); 10_FAILURE_RECOVERY_ROLLBACK.md section 17
(F-OUT: "retry outbox delivery / deduplicate consumer delivery / rebuild
event-delivery projection"; never "repeat domain Command"), section 56
(SYSTEM_SERVICE may deterministically retry delivery and advance delivery
status); 14_IMPLEMENTATION_SEQUENCE.md section 41 (an event consumer cannot
import a consequential handler).

The pipeline composes the two proven workers. `OutboxWorker` provides
due-selection, marking and retry-is-not-domain-retry. `ProjectionWorker`
provides idempotent apply, checkpoint and rebuild. `projection.delivery`
supplies the ports. No file here imports `command`, `commit`, `application`,
`boundaries` or `domain`, so no Command can be reached from delivery or replay.

POISON EVENTS (within 09 section 15.1's existing vocabulary): an outbox record
whose exact Event basis is missing (pre-F08 commits, or a corrupted basis)
fails closed. It is marked FAILED_DELIVERY with a retry time, it never blocks
other records, and it is never reconstructed from guesswork (10 section 17).
A terminal dead-letter status would extend 09's delivery vocabulary; that is
recorded as a Human Authority question, not invented here.
"""

from __future__ import annotations

from events.contracts import EventBasisMissing
from events.envelope import EventEnvelope
from events.outbox import OutboxRecord
from projection.delivery import DeliveryPorts, ProjectionStoreFailure
from semantic_types.clock import Clock
from semantic_types.ids import WorkspaceId

from nquiry_worker.outbox_worker import (
    EventDeliveryFailure,
    EventEnvelopeSource,
    OutboxDeliveryBatchResult,
    OutboxWorker,
)
from nquiry_worker.projection_worker import ProjectionApplyResult, ProjectionWorker

DEFAULT_RETRY_BACKOFF_SECONDS = 300


class BasisRequiredEnvelopeSource:
    """An `EventEnvelopeSource` that reports a missing exact basis as a
    delivery failure (the one exception `OutboxWorker` handles per record),
    so a poison record fails closed without stopping the pass."""

    def __init__(self, source: EventEnvelopeSource) -> None:
        self._source = source

    def resolve(self, record: OutboxRecord) -> EventEnvelope:
        try:
            return self._source.resolve(record)
        except EventBasisMissing as exc:
            raise EventDeliveryFailure(f"EVENT_BASIS_MISSING: {exc}") from exc


class ProjectionEventPublisher:
    """`events.envelope.EventPublisher`: in-process delivery to the projection
    consumer (12 section 17), one SAVEPOINT per event."""

    def __init__(self, *, ports: DeliveryPorts, worker: ProjectionWorker) -> None:
        self._ports = ports
        self._worker = worker

    def publish(self, envelope: EventEnvelope) -> None:
        try:
            with self._ports.isolated():
                self._worker.apply_batch([envelope], workspace_id=envelope.workspace_scope_ref)
        except ProjectionStoreFailure as exc:
            raise EventDeliveryFailure(f"PROJECTION_STORE_FAILURE: {exc}") from exc


def _projection_worker(ports: DeliveryPorts) -> ProjectionWorker:
    return ProjectionWorker(repository=ports.projection, consumer=ports.consumer)


def projection_publisher(ports: DeliveryPorts) -> ProjectionEventPublisher:
    return ProjectionEventPublisher(ports=ports, worker=_projection_worker(ports))


def run_delivery_pass(
    ports: DeliveryPorts,
    *,
    clock: Clock,
    retry_backoff_seconds: int = DEFAULT_RETRY_BACKOFF_SECONDS,
) -> OutboxDeliveryBatchResult:
    """One deterministic pass over every due outbox record."""
    return OutboxWorker(
        outbox_repository=ports.outbox,
        envelope_source=BasisRequiredEnvelopeSource(ports.envelope_source),
        publisher=projection_publisher(ports),
        clock=clock,
    ).deliver_due(retry_backoff_seconds=retry_backoff_seconds)


def rebuild_projections(
    ports: DeliveryPorts, *, workspace_id: WorkspaceId
) -> ProjectionApplyResult:
    """Replay (09 section 18): wipe both read models of one Workspace and
    rebuild them from the committed Event history alone. It reads no current
    canonical state and submits no Command."""
    history = ports.history.list_for_workspace(workspace_id)
    worker = _projection_worker(ports)
    applied: list = []
    for name in ("session_read_model", "inquiry_read_model"):
        ports.projection.reset_projection(name, workspace_id)
    for envelope in history:
        applied.extend(worker.apply_batch([envelope], workspace_id=workspace_id).applied_event_ids)
    return ProjectionApplyResult(applied_event_ids=tuple(applied))


__all__ = [
    "DEFAULT_RETRY_BACKOFF_SECONDS",
    "BasisRequiredEnvelopeSource",
    "ProjectionEventPublisher",
    "projection_publisher",
    "rebuild_projections",
    "run_delivery_pass",
]
