"""SqlAlchemySecurityEventRepository: the durable, append-only
`SecurityEventRepository` adapter.

THIS REPOSITORY HAS NO UPDATE OR DELETE METHOD, NOT EVEN A PRIVATE ONE
-----------------------------------------------------------------------
Same discipline as `persistence.audit_repository.SqlAlchemyAuditRepository`:
`SecurityEventRepository`'s own Protocol shape (`packages/security/events.py`)
is already the primary defense against "SecurityEvent tamper/rewrite" --
there is no method here that could mutate or remove an existing row.
`security_events`' own migration triggers are the independent,
defense-in-depth proof that even a caller bypassing this repository
entirely (raw SQL) cannot succeed either.

WHY THIS FILE EXISTS AT ALL, RATHER THAN LIVING INSIDE
`packages/security/events.py` ITSELF
--------------------------------------------------------------------
`security`'s own allow-list (14 section 3.1) is `semantic_types` only
-- it cannot import `sqlalchemy` or `persistence`. This is the
identical "concrete adapters live in persistence" split PKG-12 already
established for `AuditRepository`/`OutboxRepository`, requiring the
same kind of new, disclosed, one-directional `persistence -> security`
extension (see `scripts/check_architecture_dependencies.py`).
"""

from __future__ import annotations

import sqlalchemy as sa
from security.events import Environment, SecurityEvent, TrustBoundary
from semantic_types.ids import (
    CommandId,
    CorrelationId,
    GenerationId,
    RecoveryId,
    SecurityEventId,
    WorkspaceId,
)

from persistence.tables import security_events_table


class SqlAlchemySecurityEventRepository:
    """`SecurityEventRepository` backed by `security_events` via a
    SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def record(self, event: SecurityEvent) -> None:
        self._connection.execute(
            sa.insert(security_events_table).values(
                id=event.security_event_id.value,
                workspace_id=None if event.workspace_id is None else event.workspace_id.value,
                occurred_at=event.occurred_at,
                environment=event.environment.value,
                actor_type=event.actor_type,
                actor_id=event.actor_id,
                trust_boundary=event.trust_boundary.value,
                event_type=event.event_type,
                correlation_id=event.correlation_id.value,
                target_ref=event.target_ref,
                command_id=None if event.command_id is None else event.command_id.value,
                generation_id=None if event.generation_id is None else event.generation_id.value,
                recovery_id=None if event.recovery_id is None else event.recovery_id.value,
                observed_facts=event.observed_facts,
                uncertain=event.uncertain,
                containment_action=event.containment_action,
                audit_linkage=event.audit_linkage,
            )
        )

    def get(self, security_event_id: SecurityEventId) -> SecurityEvent | None:
        stmt = sa.select(security_events_table).where(
            security_events_table.c.id == security_event_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _event_from_row(row)

    def list_for_correlation(self, correlation_id: CorrelationId) -> tuple[SecurityEvent, ...]:
        stmt = (
            sa.select(security_events_table)
            .where(security_events_table.c.correlation_id == correlation_id.value)
            .order_by(security_events_table.c.occurred_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_event_from_row(row) for row in rows)


def _event_from_row(row: sa.RowMapping) -> SecurityEvent:
    return SecurityEvent(
        security_event_id=SecurityEventId(row["id"]),
        occurred_at=row["occurred_at"],
        environment=Environment(row["environment"]),
        actor_type=row["actor_type"],
        actor_id=row["actor_id"],
        trust_boundary=TrustBoundary(row["trust_boundary"]),
        event_type=row["event_type"],
        correlation_id=CorrelationId(row["correlation_id"]),
        workspace_id=None if row["workspace_id"] is None else WorkspaceId(row["workspace_id"]),
        target_ref=row["target_ref"],
        command_id=None if row["command_id"] is None else CommandId(row["command_id"]),
        generation_id=None if row["generation_id"] is None else GenerationId(row["generation_id"]),
        recovery_id=None if row["recovery_id"] is None else RecoveryId(row["recovery_id"]),
        observed_facts=row["observed_facts"],
        uncertain=row["uncertain"],
        containment_action=row["containment_action"],
        audit_linkage=row["audit_linkage"],
    )


__all__ = ["SqlAlchemySecurityEventRepository"]
