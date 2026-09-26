"""Operation authorizations (F04 WU-04.3, PI-4; reconstruction §0.1).

Write-once: there is a create method and read methods, and nothing else. The
table rejects UPDATE / DELETE by trigger; supersession, the chain root, the
RETRY / RECOVERY case and the precondition artifact are checked by the insert
trigger of migration a8d3f1c6e902 against persisted state.
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization, RequestCase
from semantic_types.ids import CommandId, GenerationId, SessionId, WorkspaceId

from persistence.tables import ai_operation_authorizations_table as t


class SqlAlchemyOperationAuthorizationRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(self, authorization: OperationAuthorization) -> None:
        a = authorization
        self._connection.execute(
            sa.insert(t).values(
                id=a.authorization_id,
                workspace_id=a.workspace_id.value,
                session_id=a.session_id.value,
                ai_operation_id=a.ai_operation_id.value,
                shape=a.shape.value,
                authorizing_command_id=a.authorizing_command_id.value,
                sequence_no=a.sequence_no,
                chain_root_command_id=a.chain_root_command_id.value,
                request_case=None if a.request_case is None else a.request_case.value,
                supersedes_authorization_id=a.supersedes_authorization_id,
                retry_of_generation_id=(
                    None if a.retry_of_generation_id is None else a.retry_of_generation_id.value
                ),
                precondition_artifact_ref=a.precondition_artifact_ref,
                created_at=a.created_at,
            )
        )

    def get(self, authorization_id: uuid.UUID) -> OperationAuthorization | None:
        row = (
            self._connection.execute(sa.select(t).where(t.c.id == authorization_id))
            .mappings()
            .one_or_none()
        )
        return None if row is None else _from_row(row)

    def latest(
        self, session_id: SessionId, ai_operation_id: AIOperationId
    ) -> OperationAuthorization | None:
        """The only executable authorization of (Session, operation) (§0.1 rule 5)."""
        row = (
            self._connection.execute(
                sa.select(t)
                .where(
                    t.c.session_id == session_id.value,
                    t.c.ai_operation_id == ai_operation_id.value,
                )
                .order_by(t.c.sequence_no.desc())
                .limit(1)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _from_row(row)

    def list_for_session(self, session_id: SessionId) -> tuple[OperationAuthorization, ...]:
        rows = self._connection.execute(
            sa.select(t)
            .where(t.c.session_id == session_id.value)
            .order_by(t.c.ai_operation_id, t.c.sequence_no)
        ).mappings()
        return tuple(_from_row(r) for r in rows)


def _from_row(row: sa.RowMapping) -> OperationAuthorization:
    return OperationAuthorization(
        authorization_id=row["id"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        session_id=SessionId(row["session_id"]),
        ai_operation_id=AIOperationId(row["ai_operation_id"]),
        shape=AuthorizationShape(row["shape"]),
        authorizing_command_id=CommandId(row["authorizing_command_id"]),
        sequence_no=row["sequence_no"],
        chain_root_command_id=CommandId(row["chain_root_command_id"]),
        created_at=row["created_at"],
        request_case=None if row["request_case"] is None else RequestCase(row["request_case"]),
        supersedes_authorization_id=row["supersedes_authorization_id"],
        retry_of_generation_id=(
            None
            if row["retry_of_generation_id"] is None
            else GenerationId(row["retry_of_generation_id"])
        ),
        precondition_artifact_ref=row["precondition_artifact_ref"],
    )


__all__ = ["SqlAlchemyOperationAuthorizationRepository"]
