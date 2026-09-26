"""SqlAlchemyProjectionRepository: the durable `ProjectionRepository`
adapter.

14 section 10: "ProjectionRepository: projection-only read/write." No
method here reads or writes any canonical table for a write -- the
composite foreign key `session_read_model` carries into `sessions` is
read-only from this repository's own perspective (enforced by the
database, not by this class's own discipline alone).

WHY EVERY UPSERT IS IDEMPOTENT ON `last_event_id`, NOT AN UNCONDITIONAL
OVERWRITE
--------------------------------------------------------------------
Mirrors `SqlAlchemyOutboxRepository.mark_delivered`'s own precedent
(PKG-12/20): a caller re-applying the identical, already-projected
Event (at-least-once redelivery, 09 section 15.2) must be a safe
no-op, not a duplicate-effect or an error. `projection.consumer.
ProjectionConsumer` already checks this before calling either upsert
method; this repository checks it again independently (defense in
depth, this codebase's dominant pattern) rather than trusting the one
caller that exists today.
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from projection.models import InquiryReadModel, ProjectionCheckpoint, SessionReadModel
from semantic_types.ids import EventId, SessionId, WorkspaceId

from persistence.tables import (
    inquiry_read_model_table,
    projection_checkpoints_table,
    session_read_model_table,
)


class SqlAlchemyProjectionRepository:
    """`ProjectionRepository` backed by `session_read_model`/
    `inquiry_read_model`/`projection_checkpoints` via a SQLAlchemy Core
    connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get_session_read_model(
        self, session_id: SessionId, workspace_id: WorkspaceId
    ) -> SessionReadModel | None:
        stmt = sa.select(session_read_model_table).where(
            session_read_model_table.c.session_id == session_id.value,
            session_read_model_table.c.workspace_id == workspace_id.value,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _session_read_model_from_row(row)

    def upsert_session_read_model(self, model: SessionReadModel) -> None:
        current = self.get_session_read_model(model.session_id, model.workspace_id)
        if current is not None and current.last_event_id.value == model.last_event_id.value:
            return
        if current is None:
            self._connection.execute(
                sa.insert(session_read_model_table).values(
                    session_id=model.session_id.value,
                    workspace_id=model.workspace_id.value,
                    current_state=model.current_state,
                    projection_version=model.projection_version,
                    last_event_id=model.last_event_id.value,
                    updated_at=model.updated_at,
                    last_aggregate_version=model.last_aggregate_version,
                )
            )
        else:
            self._connection.execute(
                sa.update(session_read_model_table)
                .where(session_read_model_table.c.session_id == model.session_id.value)
                .values(
                    current_state=model.current_state,
                    projection_version=model.projection_version,
                    last_event_id=model.last_event_id.value,
                    updated_at=model.updated_at,
                    last_aggregate_version=model.last_aggregate_version,
                )
            )

    def get_inquiry_read_model(
        self, aggregate_ref: str, workspace_id: WorkspaceId
    ) -> InquiryReadModel | None:
        stmt = sa.select(inquiry_read_model_table).where(
            inquiry_read_model_table.c.aggregate_ref == aggregate_ref,
            inquiry_read_model_table.c.workspace_id == workspace_id.value,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _inquiry_read_model_from_row(row)

    def upsert_inquiry_read_model(self, model: InquiryReadModel) -> None:
        current = self.get_inquiry_read_model(model.aggregate_ref, model.workspace_id)
        if current is not None and current.last_event_id.value == model.last_event_id.value:
            return
        if current is None:
            self._connection.execute(
                sa.insert(inquiry_read_model_table).values(
                    id=model.id,
                    aggregate_ref=model.aggregate_ref,
                    workspace_id=model.workspace_id.value,
                    projection_version=model.projection_version,
                    snapshot=dict(model.snapshot),
                    last_event_id=model.last_event_id.value,
                    updated_at=model.updated_at,
                    last_aggregate_version=model.last_aggregate_version,
                )
            )
        else:
            self._connection.execute(
                sa.update(inquiry_read_model_table)
                .where(inquiry_read_model_table.c.id == current.id)
                .values(
                    projection_version=model.projection_version,
                    snapshot=dict(model.snapshot),
                    last_event_id=model.last_event_id.value,
                    updated_at=model.updated_at,
                    last_aggregate_version=model.last_aggregate_version,
                )
            )

    def get_checkpoint(
        self, projection_name: str, workspace_id: WorkspaceId
    ) -> ProjectionCheckpoint | None:
        stmt = sa.select(projection_checkpoints_table).where(
            projection_checkpoints_table.c.projection_name == projection_name,
            projection_checkpoints_table.c.workspace_id == workspace_id.value,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _checkpoint_from_row(row)

    def advance_checkpoint(
        self, projection_name: str, workspace_id: WorkspaceId, *, last_processed_event_id: EventId
    ) -> None:
        current = self.get_checkpoint(projection_name, workspace_id)
        if current is None:
            self._connection.execute(
                sa.insert(projection_checkpoints_table).values(
                    projection_name=projection_name,
                    workspace_id=workspace_id.value,
                    last_processed_event_id=last_processed_event_id.value,
                    checkpoint_version=1,
                    updated_at=_utcnow(),
                )
            )
        else:
            self._connection.execute(
                sa.update(projection_checkpoints_table)
                .where(
                    projection_checkpoints_table.c.projection_name == projection_name,
                    projection_checkpoints_table.c.workspace_id == workspace_id.value,
                )
                .values(
                    last_processed_event_id=last_processed_event_id.value,
                    checkpoint_version=current.checkpoint_version + 1,
                    updated_at=_utcnow(),
                )
            )

    def reset_projection(self, projection_name: str, workspace_id: WorkspaceId) -> None:
        if projection_name == "session_read_model":
            self._connection.execute(
                sa.delete(session_read_model_table).where(
                    session_read_model_table.c.workspace_id == workspace_id.value
                )
            )
        elif projection_name == "inquiry_read_model":
            self._connection.execute(
                sa.delete(inquiry_read_model_table).where(
                    inquiry_read_model_table.c.workspace_id == workspace_id.value
                )
            )
        self._connection.execute(
            sa.delete(projection_checkpoints_table).where(
                projection_checkpoints_table.c.projection_name == projection_name,
                projection_checkpoints_table.c.workspace_id == workspace_id.value,
            )
        )


def _utcnow() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)


def _session_read_model_from_row(row: sa.RowMapping) -> SessionReadModel:
    return SessionReadModel(
        session_id=SessionId(row["session_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        current_state=row["current_state"],
        projection_version=row["projection_version"],
        last_event_id=EventId(row["last_event_id"]),
        updated_at=row["updated_at"],
        last_aggregate_version=row["last_aggregate_version"],
    )


def _inquiry_read_model_from_row(row: sa.RowMapping) -> InquiryReadModel:
    return InquiryReadModel(
        id=row["id"],
        aggregate_ref=row["aggregate_ref"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        projection_version=row["projection_version"],
        snapshot=dict(row["snapshot"]),
        last_event_id=EventId(row["last_event_id"]),
        updated_at=row["updated_at"],
        last_aggregate_version=row["last_aggregate_version"],
    )


def _checkpoint_from_row(row: sa.RowMapping) -> ProjectionCheckpoint:
    return ProjectionCheckpoint(
        projection_name=row["projection_name"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        checkpoint_version=row["checkpoint_version"],
        updated_at=row["updated_at"],
        last_processed_event_id=(
            EventId(row["last_processed_event_id"])
            if row["last_processed_event_id"] is not None
            else None
        ),
    )


__all__ = ["SqlAlchemyProjectionRepository"]
