"""SqlAlchemyAuditRepository: the durable, append-only `AuditRepository` adapter.

THIS REPOSITORY HAS NO UPDATE OR DELETE METHOD, NOT EVEN A PRIVATE ONE
-----------------------------------------------------------------------
`AuditRepository`'s own Protocol shape (`packages/audit/models.py`) is
already the primary defense against the mandatory adversarial attacks
"audit update"/"audit delete" -- there is no method here that could be
called to mutate or remove an existing row, so a caller cannot even
attempt it through this class. `audit_events`' own migration triggers
(`<revision>_audit_outbox.py`) are the independent, defense-in-depth
proof that even a caller bypassing this repository entirely (raw SQL)
cannot succeed either -- the same "checked at two independent layers"
discipline every prior append-only/immutable table in this codebase has
used.
"""

from __future__ import annotations

import sqlalchemy as sa
from audit.models import AuditEvent
from semantic_types.ids import (
    AuditEventId,
    CausationId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    EvidenceSetId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion

from persistence.tables import audit_events_table


class SqlAlchemyAuditRepository:
    """`AuditRepository` backed by `audit_events` via a SQLAlchemy Core
    connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def append(self, event: AuditEvent) -> None:
        self._connection.execute(
            sa.insert(audit_events_table).values(
                id=event.audit_event_id.value,
                workspace_id=event.workspace_id.value,
                event_type=event.event_type,
                event_schema_version=event.event_schema_version.value,
                occurred_at=event.occurred_at,
                actor_type=event.actor_type,
                actor_id=event.actor_id,
                command_type=event.command_type,
                command_id=event.command_id.value,
                commit_id=event.commit_id.value,
                correlation_id=event.correlation_id.value,
                causation_id=None if event.causation_id is None else event.causation_id.value,
                target_refs=list(event.target_refs),
                authority_source_ref=event.authority_source_ref,
                result=event.result,
                human_decision_ref=(
                    None if event.human_decision_ref is None else event.human_decision_ref.value
                ),
                evidence_set_ref=(
                    None if event.evidence_set_ref is None else event.evidence_set_ref.value
                ),
                state_before_ref=event.state_before_ref,
                state_after_ref=event.state_after_ref,
                failure_code=event.failure_code,
                metadata_ref=event.metadata_ref,
            )
        )

    def get(self, audit_event_id: AuditEventId) -> AuditEvent | None:
        stmt = sa.select(audit_events_table).where(audit_events_table.c.id == audit_event_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _event_from_row(row)

    def list_for_correlation(self, correlation_id: CorrelationId) -> tuple[AuditEvent, ...]:
        stmt = (
            sa.select(audit_events_table)
            .where(audit_events_table.c.correlation_id == correlation_id.value)
            .order_by(audit_events_table.c.occurred_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_event_from_row(row) for row in rows)


def _event_from_row(row: sa.RowMapping) -> AuditEvent:
    return AuditEvent(
        audit_event_id=AuditEventId(row["id"]),
        event_type=row["event_type"],
        event_schema_version=ContractVersion(row["event_schema_version"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        occurred_at=row["occurred_at"],
        actor_type=row["actor_type"],
        actor_id=row["actor_id"],
        command_type=row["command_type"],
        command_id=CommandId(row["command_id"]),
        commit_id=CommitId(row["commit_id"]),
        correlation_id=CorrelationId(row["correlation_id"]),
        causation_id=None if row["causation_id"] is None else CausationId(row["causation_id"]),
        target_refs=tuple(row["target_refs"] or ()),
        authority_source_ref=row["authority_source_ref"],
        result=row["result"],
        human_decision_ref=(
            None if row["human_decision_ref"] is None else DecisionId(row["human_decision_ref"])
        ),
        evidence_set_ref=(
            None if row["evidence_set_ref"] is None else EvidenceSetId(row["evidence_set_ref"])
        ),
        state_before_ref=row["state_before_ref"],
        state_after_ref=row["state_after_ref"],
        failure_code=row["failure_code"],
        metadata_ref=row["metadata_ref"],
    )


__all__ = ["SqlAlchemyAuditRepository"]
