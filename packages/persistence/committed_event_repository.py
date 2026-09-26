"""The durable committed Event basis (WU-PFC-F08-1, F08).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 28
(HISTORICAL EVENT BASIS: "Must reconstruct required historical fields without
mutable-current lookups"); 09_DATA_EVENT_API_CONTRACTS.md section 16
(EventEnvelope), section 72 (immutability); 10_FAILURE_RECOVERY_ROLLBACK.md
section 17 ("No authoritative Event may be regenerated from guesswork").

Three pieces:
- `SqlAlchemyCommittedEventRepository`: `append` (called only by
  CommitCoordinator inside the CommitUnit transaction) and `get`.
- `CommittedEventEnvelopeSource`: the concrete `EventEnvelopeSource` that
  `nquiry_worker.outbox_worker` left as SUCCESSOR_NOT_BUILT. It resolves an
  outbox record to its EventEnvelope from the committed row alone, and raises
  `EventBasisMissing` when no row exists. It never reconstructs a missing
  Event from current state.
- `committed_aggregate_version`: read by CommitCoordinator inside the
  committing transaction, right after the mutation, so the recorded
  `aggregate_version_after_commit` is the version the canonical row reached
  in that commit, not a value the mutation asserts.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from events.contracts import EventBasisMissing, EventContract, aggregate_kind_and_id
from events.envelope import EventEnvelope
from events.outbox import DeliveryStatus, OutboxRecord
from semantic_types.ids import CausationId, CommandId, CommitId, CorrelationId, EventId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion

from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import committed_events_table, outbox_events_table

# Aggregate kind -> the canonical table whose `record_version` it names, and
# the column holding the owning Workspace (the Workspace row is its own owner).
_AGGREGATE_TABLES: dict[str, tuple[str, str]] = {
    "workspace": ("workspaces", "id"),
    "workspace_membership": ("workspace_memberships", "workspace_id"),
    "authority_binding": ("human_authority_bindings", "workspace_id"),
    "challenge": ("challenges", "workspace_id"),
    "session": ("sessions", "workspace_id"),
    "burst": ("question_bursts", "workspace_id"),
    "session_participation": ("session_participations", "workspace_id"),
    "question": ("questions", "workspace_id"),
    "ai_operation_authorization": ("ai_operation_authorizations", "workspace_id"),
    "ai_generation": ("ai_generations", "workspace_id"),
    "ai_derived_artifact": ("ai_derived_artifacts", "workspace_id"),
    "decision": ("decisions", "workspace_id"),
    "question_selection": ("question_selections", "workspace_id"),
}


class AggregateNotCommitted(LookupError):
    """The aggregate an Event names does not exist in the committing
    transaction, or belongs to another Workspace. The commit is refused."""


def committed_aggregate_version(
    connection: sa.Connection,
    *,
    aggregate_ref: str,
    workspace_id: WorkspaceId,
    contract: EventContract,
) -> RecordVersion:
    kind, raw_id = aggregate_kind_and_id(aggregate_ref)
    table, workspace_column = _AGGREGATE_TABLES[kind]
    version = "record_version" if contract.versioned else "1"
    row = connection.execute(
        sa.text(f"SELECT {version} AS v, {workspace_column} AS ws FROM {table} WHERE id = :id"),  # noqa: S608 -- closed table map
        {"id": uuid.UUID(raw_id)},
    ).one_or_none()
    if row is None or row.ws != workspace_id.value:
        raise AggregateNotCommitted(f"{aggregate_ref} is not a committed record of {workspace_id}")
    return RecordVersion(int(row.v))


class SqlAlchemyCommittedEventRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def append(self, envelope: EventEnvelope) -> None:
        self._connection.execute(
            sa.insert(committed_events_table).values(
                event_id=envelope.event_id.value,
                event_type=envelope.event_type,
                event_schema_version=envelope.event_schema_version.value,
                occurred_at=envelope.occurred_at,
                workspace_id=envelope.workspace_scope_ref.value,
                aggregate_ref=envelope.aggregate_ref,
                aggregate_version_after_commit=envelope.aggregate_version_after_commit.value,
                command_id=envelope.command_id.value,
                commit_id=envelope.commit_id.value,
                correlation_id=envelope.correlation_id.value,
                causation_id=None if envelope.causation_id is None else envelope.causation_id.value,
                actor_ref=envelope.actor_ref,
                authority_source_ref=envelope.authority_source_ref,
                payload=envelope.payload,
            )
        )

    def get(self, event_id: EventId) -> EventEnvelope | None:
        row = (
            self._connection.execute(
                sa.select(committed_events_table).where(
                    committed_events_table.c.event_id == event_id.value
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _envelope_from_row(row)

    def list_for_workspace(self, workspace_id: WorkspaceId) -> tuple[EventEnvelope, ...]:
        """WU-PFC-F08-2: the complete committed history of one Workspace, in
        per-aggregate commit order (aggregate, then version). Replay and rebuild
        read only this (09 section 18), never current canonical state."""
        t = committed_events_table
        rows = (
            self._connection.execute(
                sa.select(t)
                .where(t.c.workspace_id == workspace_id.value)
                .order_by(t.c.aggregate_ref, t.c.aggregate_version_after_commit, t.c.occurred_at)
            )
            .mappings()
            .all()
        )
        return tuple(_envelope_from_row(row) for row in rows)


class SqlAlchemyAggregateOrderedOutbox:
    """WU-PFC-F08-2: the `OutboxRepository` the delivery pass uses. It is the
    real `SqlAlchemyOutboxRepository` except for due-selection order: records
    are selected by commit time, then aggregate, then the committed aggregate
    version. Two commits of one aggregate at the same timestamp are therefore
    delivered in version order. Records without a basis sort last (they fail
    closed in the envelope source)."""

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection
        self._outbox = SqlAlchemyOutboxRepository(connection)

    def append(self, record: OutboxRecord) -> None:
        self._outbox.append(record)

    def get(self, outbox_id: uuid.UUID) -> OutboxRecord | None:
        return self._outbox.get(outbox_id)

    def mark_delivered(self, outbox_id: uuid.UUID, *, delivered_at: datetime) -> None:
        self._outbox.mark_delivered(outbox_id, delivered_at=delivered_at)

    def mark_failed_delivery(self, outbox_id: uuid.UUID, *, next_attempt_at: datetime) -> None:
        self._outbox.mark_failed_delivery(outbox_id, next_attempt_at=next_attempt_at)

    def list_due_for_delivery(self, *, now: datetime, limit: int = 100) -> tuple[OutboxRecord, ...]:
        o, e = outbox_events_table, committed_events_table
        stmt = (
            sa.select(o.c.id)
            .select_from(o.outerjoin(e, e.c.event_id == o.c.event_id))
            .where(
                sa.or_(
                    o.c.delivery_status == DeliveryStatus.PENDING.value,
                    sa.and_(
                        o.c.delivery_status == DeliveryStatus.FAILED_DELIVERY.value,
                        o.c.next_attempt_at <= now,
                    ),
                )
            )
            .order_by(
                o.c.created_at,
                e.c.aggregate_ref.nulls_last(),
                e.c.aggregate_version_after_commit.nulls_last(),
                o.c.id,
            )
            .limit(limit)
        )
        records = []
        for outbox_id in self._connection.execute(stmt).scalars():
            record = self._outbox.get(outbox_id)
            assert record is not None  # noqa: S101 -- selected in this transaction
            records.append(record)
        return tuple(records)


class CommittedEventEnvelopeSource:
    """`nquiry_worker.outbox_worker.EventEnvelopeSource`, structurally."""

    def __init__(self, connection: sa.Connection) -> None:
        self._repository = SqlAlchemyCommittedEventRepository(connection)

    def resolve(self, record: OutboxRecord) -> EventEnvelope:
        envelope = self._repository.get(record.event_id)
        if envelope is None:
            raise EventBasisMissing(f"no committed Event for outbox event {record.event_id}")
        if (
            envelope.commit_id != record.commit_id
            or envelope.workspace_scope_ref != record.workspace_id
            or envelope.event_type != record.event_type
        ):
            raise EventBasisMissing(
                f"committed Event {record.event_id} does not match its outbox record"
            )
        return envelope


def _envelope_from_row(row: Any) -> EventEnvelope:
    return EventEnvelope(
        event_id=EventId(row["event_id"]),
        event_type=row["event_type"],
        event_schema_version=ContractVersion(row["event_schema_version"]),
        occurred_at=row["occurred_at"],
        workspace_scope_ref=WorkspaceId(row["workspace_id"]),
        aggregate_ref=row["aggregate_ref"],
        aggregate_version_after_commit=RecordVersion(row["aggregate_version_after_commit"]),
        command_id=CommandId(row["command_id"]),
        commit_id=CommitId(row["commit_id"]),
        correlation_id=CorrelationId(row["correlation_id"]),
        actor_ref=row["actor_ref"],
        authority_source_ref=row["authority_source_ref"],
        payload=row["payload"],
        causation_id=None if row["causation_id"] is None else CausationId(row["causation_id"]),
    )


__all__ = [
    "AggregateNotCommitted",
    "CommittedEventEnvelopeSource",
    "SqlAlchemyAggregateOrderedOutbox",
    "SqlAlchemyCommittedEventRepository",
    "committed_aggregate_version",
]
