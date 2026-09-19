"""AIRecordRepository: the PUBLIC_INTERFACES port 14 section 10 assigns
for AI operational writes.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`AIRecordRepository`: AIGeneration, manifest and derived artifact
operational writes only."

WHY MANIFEST METHODS WERE ADDED AT PKG-19, NOT PKG-18
------------------------------------------------------------------------
`ai_context_manifests` (14 section 9's own migration plan) was PKG-18's
own disclosed forward-reference gap -- PKG-18's own migration subset
created only `ai_generations`/`ai_derived_artifacts`. PKG-19's OBJECTIVE
("AIContextManifest allowlist builder") is what actually creates the
`ai_context_manifests` table and closes that gap; `create_context_manifest`/
`get_context_manifest` are added here, alongside the retrofitted
`ai_generations.ai_context_manifest_id` foreign key (see the PKG-19
migration's own docstring).

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
from ai_gateway.context import AIContextManifest, CoachMode, InputArtifactRef
from semantic_types.ids import CommandId, CorrelationId, GenerationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion

from persistence.tables import (
    ai_context_manifests_table,
    ai_derived_artifacts_table,
    ai_generations_table,
)


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

    def create_context_manifest(self, manifest: AIContextManifest) -> None: ...
    def get_context_manifest(
        self, ai_context_manifest_id: uuid.UUID
    ) -> AIContextManifest | None: ...


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

    def create_context_manifest(self, manifest: AIContextManifest) -> None:
        self._connection.execute(
            sa.insert(ai_context_manifests_table).values(**_context_manifest_to_row(manifest))
        )

    def get_context_manifest(self, ai_context_manifest_id: uuid.UUID) -> AIContextManifest | None:
        stmt = sa.select(ai_context_manifests_table).where(
            ai_context_manifests_table.c.id == ai_context_manifest_id
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _context_manifest_from_row(row)


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


def _context_manifest_to_row(manifest: AIContextManifest) -> dict[str, object]:
    return {
        "id": manifest.ai_context_manifest_id,
        "workspace_id": manifest.workspace_id.value,
        "ai_operation_id": manifest.ai_operation_id.value,
        "ai_operation_contract_version": str(manifest.ai_operation_contract_version),
        "requesting_actor_ref": manifest.requesting_actor_ref,
        "input_artifact_refs_with_versions": [
            {"artifact_ref": ref.artifact_ref, "version": ref.version.value}
            for ref in manifest.input_artifact_refs_with_versions
        ],
        "source_classifications": list(manifest.source_classifications),
        "method_ref": manifest.method_ref,
        "coach_mode": None if manifest.coach_mode is None else manifest.coach_mode.value,
        "burst_mode": manifest.burst_mode,
        "excluded_context_classes": list(manifest.excluded_context_classes),
        "assembled_at": manifest.assembled_at,
        "context_fingerprint": manifest.context_fingerprint,
    }


def _context_manifest_from_row(row: sa.RowMapping) -> AIContextManifest:
    return AIContextManifest(
        ai_context_manifest_id=_as_uuid(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        ai_operation_id=AIOperationId(row["ai_operation_id"]),
        ai_operation_contract_version=ContractVersion(row["ai_operation_contract_version"]),
        requesting_actor_ref=row["requesting_actor_ref"],
        input_artifact_refs_with_versions=tuple(
            InputArtifactRef(
                artifact_ref=item["artifact_ref"], version=RecordVersion(item["version"])
            )
            for item in row["input_artifact_refs_with_versions"]
        ),
        source_classifications=tuple(row["source_classifications"] or ()),
        method_ref=row["method_ref"],
        coach_mode=None if row["coach_mode"] is None else CoachMode(row["coach_mode"]),
        burst_mode=row["burst_mode"],
        excluded_context_classes=tuple(row["excluded_context_classes"] or ()),
        assembled_at=row["assembled_at"],
        context_fingerprint=row["context_fingerprint"],
    )


__all__ = ["AIRecordConflict", "AIRecordRepository", "SqlAlchemyAIRecordRepository"]
