"""SqlAlchemyOutboxRepository: the durable `OutboxRepository` adapter.

THIS REPOSITORY DOES NOT DELIVER ANYTHING
------------------------------------------
`mark_delivered`/`mark_failed_delivery` only record that a delivery
attempt happened and its outcome -- neither method performs an actual
broker publish or has any code path back into canonical/domain state.

UPDATED AT PKG-20: `list_due_for_delivery` (below) closes the "delivery
worker does not exist yet" half of this disclosure -- `apps/worker/
src/nquiry_worker/outbox_worker.py`'s own `OutboxWorker` now calls
`list_due_for_delivery`/`mark_delivered`/`mark_failed_delivery` for
real, against this real adapter. This repository still never publishes
anything itself and still has no code path into canonical/domain
state; only the read side (which records are due) and the two
write-outcome methods moved from "built but unwired" to "built and
wired," the same transition `AIRecordRepository`'s manifest methods
made at PKG-19.

WHY `mark_delivered` IS IDEMPOTENT ONCE ALREADY DELIVERED
------------------------------------------------------------
09 section 15.2: "consumers must assume duplicate event delivery is
possible... must not produce duplicate consequential effects solely
because delivery repeats." A worker re-confirming a delivery already
recorded is exactly this scenario -- `mark_delivered` treats it as a
safe no-op rather than letting it hit the migration's own
terminal-state trigger as an error. `mark_failed_delivery` is
deliberately NOT given the same treatment: transitioning an
already-DELIVERED record to FAILED_DELIVERY is never legitimate (it
would mean un-delivering a real success), so that case is left to
surface the trigger's own rejection.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from events.outbox import DeliveryStatus, OutboxRecord
from semantic_types.ids import CommitId, EventId, WorkspaceId

from persistence.tables import outbox_events_table


class OutboxRecordNotFound(Exception):
    """Raised by `mark_delivered`/`mark_failed_delivery` when no record
    exists for the given `outbox_id`.
    """


class SqlAlchemyOutboxRepository:
    """`OutboxRepository` backed by `outbox_events` via a SQLAlchemy
    Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def append(self, record: OutboxRecord) -> None:
        self._connection.execute(
            sa.insert(outbox_events_table).values(
                id=record.outbox_id,
                event_id=record.event_id.value,
                workspace_id=record.workspace_id.value,
                commit_id=record.commit_id.value,
                event_type=record.event_type,
                event_payload_ref=record.event_payload_ref,
                delivery_status=record.delivery_status.value,
                delivery_attempt_count=record.delivery_attempt_count,
                next_attempt_at=record.next_attempt_at,
                created_at=record.created_at,
                delivered_at=record.delivered_at,
            )
        )

    def get(self, outbox_id: uuid.UUID) -> OutboxRecord | None:
        stmt = sa.select(outbox_events_table).where(outbox_events_table.c.id == outbox_id)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _record_from_row(row)

    def mark_delivered(self, outbox_id: uuid.UUID, *, delivered_at: datetime) -> None:
        current = self.get(outbox_id)
        if current is None:
            raise OutboxRecordNotFound(f"outbox_id {outbox_id!r} not found")
        if current.delivery_status is DeliveryStatus.DELIVERED:
            # Mandatory adversarial attack: outbox replay. 09 section
            # 15.2: "consumers must assume duplicate event delivery is
            # possible" -- a worker re-confirming a delivery it (or a
            # duplicate at-least-once redelivery) already recorded must
            # not hit the terminal-state trigger below as an error; it
            # is a safe no-op, not a new fact.
            return
        result = self._connection.execute(
            sa.update(outbox_events_table)
            .where(outbox_events_table.c.id == outbox_id)
            .values(
                delivery_status=DeliveryStatus.DELIVERED.value,
                delivered_at=delivered_at,
                delivery_attempt_count=current.delivery_attempt_count + 1,
            )
        )
        if result.rowcount == 0:
            raise OutboxRecordNotFound(f"outbox_id {outbox_id!r} not found")

    def mark_failed_delivery(self, outbox_id: uuid.UUID, *, next_attempt_at: datetime) -> None:
        current = self.get(outbox_id)
        if current is None:
            raise OutboxRecordNotFound(f"outbox_id {outbox_id!r} not found")
        result = self._connection.execute(
            sa.update(outbox_events_table)
            .where(outbox_events_table.c.id == outbox_id)
            .values(
                delivery_status=DeliveryStatus.FAILED_DELIVERY.value,
                next_attempt_at=next_attempt_at,
                delivery_attempt_count=current.delivery_attempt_count + 1,
            )
        )
        if result.rowcount == 0:
            raise OutboxRecordNotFound(f"outbox_id {outbox_id!r} not found")

    def list_due_for_delivery(self, *, now: datetime, limit: int = 100) -> tuple[OutboxRecord, ...]:
        stmt = (
            sa.select(outbox_events_table)
            .where(
                sa.or_(
                    outbox_events_table.c.delivery_status == DeliveryStatus.PENDING.value,
                    sa.and_(
                        outbox_events_table.c.delivery_status
                        == DeliveryStatus.FAILED_DELIVERY.value,
                        outbox_events_table.c.next_attempt_at <= now,
                    ),
                )
            )
            .order_by(outbox_events_table.c.created_at)
            .limit(limit)
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_record_from_row(row) for row in rows)


def _record_from_row(row: sa.RowMapping) -> OutboxRecord:
    return OutboxRecord(
        outbox_id=row["id"],
        event_id=EventId(row["event_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        commit_id=CommitId(row["commit_id"]),
        event_type=row["event_type"],
        event_payload_ref=row["event_payload_ref"],
        delivery_status=DeliveryStatus(row["delivery_status"]),
        delivery_attempt_count=row["delivery_attempt_count"],
        next_attempt_at=row["next_attempt_at"],
        created_at=row["created_at"],
        delivered_at=row["delivered_at"],
    )


__all__ = ["OutboxRecordNotFound", "SqlAlchemyOutboxRepository"]
