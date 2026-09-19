"""AIRecordRepository: the PUBLIC_INTERFACES port 14 section 10 assigns
for AI operational writes.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`AIRecordRepository`: AIGeneration, manifest and derived artifact
operational writes only."

WHY THIS REPOSITORY HAS NO MANIFEST METHODS
------------------------------------------------------------------------
`ai_context_manifests` (14 section 9's own migration plan) is PKG-19's
own table to create -- this package's migration subset creates only
`ai_generations`/`ai_derived_artifacts` (see the migration's own
docstring). The port name 14 gives is a single umbrella covering all
of PKG-18's and PKG-19's eventual AI-operational writes; this module
implements exactly the two-thirds this package is authorized to build,
honestly disclosed rather than stubbing manifest methods that would
have no real table to write to yet.

WHY `update_generation_status` TAKES AN `expected_record_version` GUARD
------------------------------------------------------------------------
08 section 15 (AIGeneration Legal Transitions) mutates an EXISTING
generation's own lifecycle state -- a real optimistic-concurrency race
is possible (two callers attempting to advance the same generation
concurrently, e.g. after a provider response races a timeout). Mirrors
`persistence.evidence_repository.SqlAlchemyEvidenceRepository.update_validation_state`'s
own guarded-UPDATE-returns-0-rows -> conflict-exception pattern
exactly; the database's own transition-topology trigger is the second,
independent line of defense behind this application-level guard,
matching that same predecessor's own layering.

WHY `create_generation`/`create_derived_artifact` HAVE NO SUCH GUARD
------------------------------------------------------------------------
Each persists a brand-new row -- there is no prior version to race
against. Any race manifests as a primary-key violation, the same
choice every other create-only method in this codebase already makes.
"""

from __future__ import annotations

import uuid
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.derived_artifact import AIDerivedArtifact
from ai_contracts.generation import AIGeneration, AIGenerationStatus
from semantic_types.ids import CommandId, CorrelationId, GenerationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion

from persistence.tables import ai_derived_artifacts_table, ai_generations_table


class AIRecordConflict(Exception):
    """Raised by `update_generation_status` when its own
    expected-version-guarded UPDATE affects zero rows -- a race between
    a caller's fresh read and this attempt's actual write, or a
    generation row that does not exist at all."""


@runtime_checkable
class AIRecordRepository(Protocol):
    """Port: AIGeneration create/read plus the one governed lifecycle
    mutation 08 section 15 names, and AIDerivedArtifact create/read
    (14 section 10)."""

    def create_generation(self, generation: AIGeneration) -> None: ...
    def get_generation(self, ai_generation_id: GenerationId) -> AIGeneration | None: ...

    def update_generation_status(
        self,
        *,
        ai_generation_id: GenerationId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        new_status: AIGenerationStatus,
        started_at: object | None = None,
        output_received_at: object | None = None,
        completed_at: object | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        estimated_cost: float | None = None,
        output_artifact_ref: uuid.UUID | None = None,
        failure_code: str | None = None,
        failure_detail_ref: str | None = None,
    ) -> None:
        """08 section 15's own legal-transition table. Raises
        `AIRecordConflict` if `expected_record_version` no longer
        matches the stored row (including "no such row")."""
        ...

    def create_derived_artifact(self, artifact: AIDerivedArtifact) -> None: ...
    def get_derived_artifact(
        self, ai_derived_artifact_id: uuid.UUID
    ) -> AIDerivedArtifact | None: ...


class SqlAlchemyAIRecordRepository:
    """`AIRecordRepository` backed by `ai_generations`/
    `ai_derived_artifacts` via a SQLAlchemy Core connection."""

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create_generation(self, generation: AIGeneration) -> None:
        self._connection.execute(
            sa.insert(ai_generations_table).values(**_generation_to_row(generation))
        )

    def get_generation(self, ai_generation_id: GenerationId) -> AIGeneration | None:
        stmt = sa.select(ai_generations_table).where(
            ai_generations_table.c.id == ai_generation_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _generation_from_row(row)

    def update_generation_status(
        self,
        *,
        ai_generation_id: GenerationId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        new_status: AIGenerationStatus,
        started_at: object | None = None,
        output_received_at: object | None = None,
        completed_at: object | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        estimated_cost: float | None = None,
        output_artifact_ref: uuid.UUID | None = None,
        failure_code: str | None = None,
        failure_detail_ref: str | None = None,
    ) -> None:
        values: dict[str, object] = {
            "status": new_status.value,
            "record_version": expected_record_version.next().value,
        }
        optional_fields = {
            "started_at": started_at,
            "output_received_at": output_received_at,
            "completed_at": completed_at,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "estimated_cost": estimated_cost,
            "output_artifact_ref": output_artifact_ref,
            "failure_code": failure_code,
            "failure_detail_ref": failure_detail_ref,
        }
        for column, value in optional_fields.items():
            if value is not None:
                values[column] = value
        result = self._connection.execute(
            sa.update(ai_generations_table)
            .where(
                ai_generations_table.c.id == ai_generation_id.value,
                ai_generations_table.c.workspace_id == workspace_id.value,
                ai_generations_table.c.record_version == expected_record_version.value,
            )
            .values(**values)
        )
        if result.rowcount == 0:
            raise AIRecordConflict(
                f"ai_generation {ai_generation_id!r} not found at workspace {workspace_id!r} "
                f"with expected record_version {expected_record_version.value}"
            )

    def create_derived_artifact(self, artifact: AIDerivedArtifact) -> None:
        self._connection.execute(
            sa.insert(ai_derived_artifacts_table).values(**_derived_artifact_to_row(artifact))
        )

    def get_derived_artifact(self, ai_derived_artifact_id: uuid.UUID) -> AIDerivedArtifact | None:
        stmt = sa.select(ai_derived_artifacts_table).where(
            ai_derived_artifacts_table.c.id == ai_derived_artifact_id
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _derived_artifact_from_row(row)


def _generation_to_row(generation: AIGeneration) -> dict[str, object]:
    return {
        "id": generation.ai_generation_id.value,
        "workspace_id": generation.workspace_id.value,
        "user_id": None if generation.user_id is None else generation.user_id.value,
        "ai_operation_id": generation.ai_operation_id.value,
        "ai_operation_contract_version": str(generation.ai_operation_contract_version),
        "ai_context_manifest_id": generation.ai_context_manifest_id,
        "prompt_version": str(generation.prompt_version),
        "model": generation.model,
        "provider": generation.provider,
        "status": generation.status.value,
        "requested_at": generation.requested_at,
        "started_at": generation.started_at,
        "output_received_at": generation.output_received_at,
        "completed_at": generation.completed_at,
        "input_tokens": generation.input_tokens,
        "output_tokens": generation.output_tokens,
        "latency_ms": generation.latency_ms,
        "estimated_cost": generation.estimated_cost,
        "retry_of_generation_id": (
            None
            if generation.retry_of_generation_id is None
            else generation.retry_of_generation_id.value
        ),
        "command_id": None if generation.command_id is None else generation.command_id.value,
        "correlation_id": generation.correlation_id.value,
        "output_artifact_ref": generation.output_artifact_ref,
        "failure_code": generation.failure_code,
        "failure_detail_ref": generation.failure_detail_ref,
        "record_version": generation.record_version.value,
    }


def _generation_from_row(row: sa.RowMapping) -> AIGeneration:
    return AIGeneration(
        ai_generation_id=GenerationId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        user_id=None if row["user_id"] is None else UserId(row["user_id"]),
        ai_operation_id=AIOperationId(row["ai_operation_id"]),
        ai_operation_contract_version=ContractVersion(row["ai_operation_contract_version"]),
        ai_context_manifest_id=row["ai_context_manifest_id"],
        prompt_version=PromptVersion(row["prompt_version"]),
        model=row["model"],
        provider=row["provider"],
        status=AIGenerationStatus(row["status"]),
        requested_at=row["requested_at"],
        started_at=row["started_at"],
        output_received_at=row["output_received_at"],
        completed_at=row["completed_at"],
        input_tokens=row["input_tokens"],
        output_tokens=row["output_tokens"],
        latency_ms=row["latency_ms"],
        estimated_cost=row["estimated_cost"],
        retry_of_generation_id=(
            None
            if row["retry_of_generation_id"] is None
            else GenerationId(row["retry_of_generation_id"])
        ),
        command_id=None if row["command_id"] is None else CommandId(row["command_id"]),
        correlation_id=CorrelationId(row["correlation_id"]),
        output_artifact_ref=row["output_artifact_ref"],
        failure_code=row["failure_code"],
        failure_detail_ref=row["failure_detail_ref"],
        record_version=RecordVersion(row["record_version"]),
    )


def _derived_artifact_to_row(artifact: AIDerivedArtifact) -> dict[str, object]:
    return {
        "id": artifact.ai_derived_artifact_id,
        "workspace_id": artifact.workspace_id.value,
        "ai_generation_id": artifact.ai_generation_id.value,
        "ai_operation_id": artifact.ai_operation_id.value,
        "content": artifact.content,
        "content_fingerprint": artifact.content_fingerprint,
        "created_at": artifact.created_at,
        "record_version": artifact.record_version.value,
        "provenance_ref": artifact.provenance_ref,
    }


def _derived_artifact_from_row(row: sa.RowMapping) -> AIDerivedArtifact:
    return AIDerivedArtifact(
        ai_derived_artifact_id=_as_uuid(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        ai_generation_id=GenerationId(row["ai_generation_id"]),
        ai_operation_id=AIOperationId(row["ai_operation_id"]),
        content=row["content"],
        content_fingerprint=row["content_fingerprint"],
        created_at=row["created_at"],
        record_version=RecordVersion(row["record_version"]),
        provenance_ref=row["provenance_ref"],
    )


def _as_uuid(value: object) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


__all__ = ["AIRecordConflict", "AIRecordRepository", "SqlAlchemyAIRecordRepository"]
