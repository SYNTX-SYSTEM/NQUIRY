"""Fresh persisted facts for the SYSTEM_OPERATION right (F04 HD-17).

Structurally satisfies `boundaries.system_operation.SystemOperationReader`
(persistence does not import boundaries). Every method is one live query;
nothing is cached, and nothing reads "current" state where the architecture
requires a persisted reference (the precondition artifact X is always read by
the id the authorization row persisted).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import OperationAuthorization
from ai_contracts.derived_artifact import AIDerivedArtifact
from ai_contracts.generation import AIGeneration
from command.envelope import CommandOutcome
from domain.session import SessionState
from semantic_types.ids import CommandId, GenerationId, SessionId, WorkspaceId

from persistence.ai_authorization_repository import SqlAlchemyOperationAuthorizationRepository
from persistence.ai_record_repository import SqlAlchemyAIRecordRepository
from persistence.tables import (
    ai_operation_authorizations_table,
    command_attempts_table,
    commands_table,
    sessions_table,
)


@dataclass(frozen=True, slots=True)
class CommittedCommandFact:
    """Structurally a `boundaries.system_operation.CommittedCommand`."""

    command_id: CommandId
    workspace_id: WorkspaceId
    command_type: str
    target_refs: tuple[str, ...]


class SqlAlchemySystemOperationReader:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection
        self._authorizations = SqlAlchemyOperationAuthorizationRepository(connection)
        self._records = SqlAlchemyAIRecordRepository(connection)

    def authorization(self, authorization_id: uuid.UUID) -> OperationAuthorization | None:
        return self._authorizations.get(authorization_id)

    def latest_sequence(self, session_id: SessionId, ai_operation_id: AIOperationId) -> int | None:
        t = ai_operation_authorizations_table
        return self._connection.execute(
            sa.select(sa.func.max(t.c.sequence_no)).where(
                t.c.session_id == session_id.value, t.c.ai_operation_id == ai_operation_id.value
            )
        ).scalar_one_or_none()

    def committed_command(self, command_id: CommandId) -> CommittedCommandFact | None:
        c, a = commands_table, command_attempts_table
        committed = sa.exists().where(
            a.c.command_id == c.c.id,
            a.c.workspace_id == c.c.workspace_id,
            a.c.outcome == CommandOutcome.COMMITTED.value,
        )
        row = (
            self._connection.execute(
                sa.select(c.c.id, c.c.workspace_id, c.c.command_type, c.c.target_refs).where(
                    c.c.id == command_id.value, committed
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return CommittedCommandFact(
            CommandId(row["id"]),
            WorkspaceId(row["workspace_id"]),
            row["command_type"],
            tuple(row["target_refs"] or ()),
        )

    def session_state(self, session_id: SessionId) -> tuple[WorkspaceId, SessionState] | None:
        row = self._connection.execute(
            sa.select(sessions_table.c.workspace_id, sessions_table.c.state).where(
                sessions_table.c.id == session_id.value
            )
        ).one_or_none()
        return None if row is None else (WorkspaceId(row[0]), SessionState(row[1]))

    def generation_for_authorization(self, authorization_id: uuid.UUID) -> AIGeneration | None:
        return self._records.get_generation_for_authorization(authorization_id)

    def generation(self, ai_generation_id: GenerationId) -> AIGeneration | None:
        return self._records.get_generation(ai_generation_id)

    def artifact(self, artifact_id: uuid.UUID) -> AIDerivedArtifact | None:
        return self._records.get_derived_artifact(artifact_id)

    def accepted_artifact(
        self, session_id: SessionId, ai_operation_id: AIOperationId
    ) -> AIDerivedArtifact | None:
        return self._records.get_accepted_artifact(session_id, ai_operation_id)


__all__ = ["SqlAlchemySystemOperationReader"]
