"""Delivery diagnostics and projection freshness (WU-PFC-F08-3, F08).

Source: 19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md section 28 (internal
Work Units "projection freshness", "diagnostics"); 09_DATA_EVENT_API_CONTRACTS.md
section 122 (AC-09-010: delivery failure "does require outbox
retry/observability"); 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 25
(operational telemetry aids diagnosis and is never authoritative audit).

Both reads are read-only: plain SELECTs, no locks, no writes.

- Freshness answers, per Workspace, whether every committed consequence has
  reached the projections. A Workspace is fresh when none of its outbox
  records is undelivered. Records that fail without a basis count as
  undelivered, so a poison backlog is never reported as fresh.
- Diagnostics count the delivery states (09 section 15.1 vocabulary only),
  the records without an exact Event basis, the highest attempt count among
  failed records, and the oldest undelivered commit time. It covers one
  Workspace or, with `None`, the whole database (the worker's operator view).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from events.outbox import DeliveryStatus
from semantic_types.ids import WorkspaceId

from persistence.tables import committed_events_table, outbox_events_table


@dataclass(frozen=True, slots=True)
class ProjectionFreshness:
    workspace_id: WorkspaceId
    undelivered_events: int
    oldest_undelivered_at: datetime | None
    last_delivered_at: datetime | None

    @property
    def fresh(self) -> bool:
        return self.undelivered_events == 0


@dataclass(frozen=True, slots=True)
class DeliveryDiagnostics:
    pending: int
    failed: int
    delivered: int
    without_basis: int
    max_failed_attempts: int
    oldest_undelivered_at: datetime | None


def _scoped(stmt: sa.Select, workspace_id: WorkspaceId | None) -> sa.Select:
    if workspace_id is None:
        return stmt
    return stmt.where(outbox_events_table.c.workspace_id == workspace_id.value)


def projection_freshness(
    connection: sa.Connection, workspace_id: WorkspaceId
) -> ProjectionFreshness:
    o = outbox_events_table
    undelivered = o.c.delivery_status != DeliveryStatus.DELIVERED.value
    row = connection.execute(
        _scoped(
            sa.select(
                sa.func.count().filter(undelivered),
                sa.func.min(o.c.created_at).filter(undelivered),
                sa.func.max(o.c.delivered_at),
            ),
            workspace_id,
        )
    ).one()
    return ProjectionFreshness(
        workspace_id=workspace_id,
        undelivered_events=int(row[0]),
        oldest_undelivered_at=row[1],
        last_delivered_at=row[2],
    )


def delivery_diagnostics(
    connection: sa.Connection, workspace_id: WorkspaceId | None
) -> DeliveryDiagnostics:
    o, e = outbox_events_table, committed_events_table
    status = o.c.delivery_status
    row = connection.execute(
        _scoped(
            sa.select(
                sa.func.count().filter(status == DeliveryStatus.PENDING.value),
                sa.func.count().filter(status == DeliveryStatus.FAILED_DELIVERY.value),
                sa.func.count().filter(status == DeliveryStatus.DELIVERED.value),
                sa.func.count().filter(e.c.event_id.is_(None)),
                sa.func.coalesce(
                    sa.func.max(o.c.delivery_attempt_count).filter(
                        status == DeliveryStatus.FAILED_DELIVERY.value
                    ),
                    0,
                ),
                sa.func.min(o.c.created_at).filter(status != DeliveryStatus.DELIVERED.value),
            ).select_from(o.outerjoin(e, e.c.event_id == o.c.event_id)),
            workspace_id,
        )
    ).one()
    return DeliveryDiagnostics(
        pending=int(row[0]),
        failed=int(row[1]),
        delivered=int(row[2]),
        without_basis=int(row[3]),
        max_failed_attempts=int(row[4]),
        oldest_undelivered_at=row[5],
    )


__all__ = [
    "DeliveryDiagnostics",
    "ProjectionFreshness",
    "delivery_diagnostics",
    "projection_freshness",
]
