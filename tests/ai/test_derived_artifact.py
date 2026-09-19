"""T6 AI TEST: `ai_contracts.derived_artifact`/
`persistence.ai_record_repository` -- AIDerivedArtifact, against real
PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.derived_artifact import AIDerivedArtifact
from ai_contracts.generation import AIGeneration, AIGenerationStatus
from persistence.ai_record_repository import SqlAlchemyAIRecordRepository
from persistence.tables import ai_derived_artifacts_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, GenerationId, WorkspaceId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id


def _seed_generation(
    repo: SqlAlchemyAIRecordRepository, *, workspace_id: WorkspaceId
) -> AIGeneration:
    generation = AIGeneration(
        ai_generation_id=GenerationId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        prompt_version=PromptVersion("1.0"),
        model="mock-model",
        provider="mock-provider",
        status=AIGenerationStatus.REQUESTED,
        requested_at=_NOW,
        correlation_id=CorrelationId(uuid.uuid4()),
        record_version=RecordVersion.initial(),
    )
    repo.create_generation(generation)
    return generation


def _make_artifact(
    *, workspace_id: WorkspaceId, ai_generation_id: GenerationId, **overrides: object
) -> AIDerivedArtifact:
    fields: dict[str, object] = dict(
        ai_derived_artifact_id=uuid.uuid4(),
        workspace_id=workspace_id,
        ai_generation_id=ai_generation_id,
        ai_operation_id=AIOperationId.AIOP_001,
        content="classification proposal: unusual question flagged",
        content_fingerprint="fp-1",
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    fields.update(overrides)
    return AIDerivedArtifact(**fields)  # type: ignore[arg-type]


def test_denies_an_empty_content() -> None:
    with pytest.raises(ValueError, match="content"):
        _make_artifact(
            workspace_id=WorkspaceId(uuid.uuid4()),
            ai_generation_id=GenerationId(uuid.uuid4()),
            content="",
        )


def test_denies_a_non_uuid_artifact_id() -> None:
    with pytest.raises(TypeError):
        _make_artifact(
            workspace_id=WorkspaceId(uuid.uuid4()),
            ai_generation_id=GenerationId(uuid.uuid4()),
            ai_derived_artifact_id="not-a-uuid",
        )


def test_has_no_field_that_could_represent_ai_confidence_or_domain_truth() -> None:
    """Novel/adapted attack, mirroring PKG-16's own mandatory "AI
    confidence cast as Evidence": `AIDerivedArtifact` has no
    `confidence`/`score`/`truth`-shaped field of any kind -- 08 section
    16: "AIGeneration VALIDATED != ... Evidence"; a derived artifact is
    never mistakable for a confidence-scored or truth-bearing record."""
    field_names = set(AIDerivedArtifact.__dataclass_fields__)
    assert "confidence" not in field_names
    assert "score" not in field_names
    assert "truth" not in field_names
    assert "validation_state" not in field_names


def test_full_round_trip_create_and_get(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-artifact-roundtrip@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _seed_generation(repo, workspace_id=workspace_id)
    artifact = _make_artifact(
        workspace_id=workspace_id,
        ai_generation_id=generation.ai_generation_id,
        provenance_ref="ai-gateway-pipeline-v1",
    )

    repo.create_derived_artifact(artifact)
    fetched = repo.get_derived_artifact(artifact.ai_derived_artifact_id)

    assert fetched == artifact


def test_denies_a_derived_artifact_referencing_a_nonexistent_generation(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: missing provenance. An
    artifact cannot exist without a real, resolvable AIGeneration --
    08 section 23 OUTPUT PROVENANCE: "Must reference: AIGeneration...".
    """
    workspace_id = _bootstrap(db_connection, email="ai-artifact-phantom-gen@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    phantom_generation_id = GenerationId(uuid.uuid4())
    artifact = _make_artifact(workspace_id=workspace_id, ai_generation_id=phantom_generation_id)

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_derived_artifact(artifact)


def test_cross_workspace_derived_artifact_is_not_representable(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: cross-Workspace derived artifact."""
    workspace_a = _bootstrap(db_connection, email="ai-artifact-cross-a@nonproof.test")
    workspace_b = _bootstrap(db_connection, email="ai-artifact-cross-b@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _seed_generation(repo, workspace_id=workspace_a)
    artifact = _make_artifact(
        workspace_id=workspace_b,  # mismatched Workspace
        ai_generation_id=generation.ai_generation_id,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_derived_artifact(artifact)


def test_an_ai_operation_id_outside_the_closed_vocabulary_is_rejected_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-artifact-bad-op@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _seed_generation(repo, workspace_id=workspace_id)

    with (
        pytest.raises(sa.exc.DBAPIError, match="ck_ai_derived_artifacts_ai_operation_id"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(ai_derived_artifacts_table).values(
                id=uuid.uuid4(),
                workspace_id=workspace_id.value,
                ai_generation_id=generation.ai_generation_id.value,
                ai_operation_id="AIOP-999",
                content="bogus",
                content_fingerprint="fp",
                created_at=_NOW,
                record_version=1,
                provenance_ref=None,
            )
        )
