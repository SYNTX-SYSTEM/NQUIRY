"""T6 AI TEST: `ai_gateway.context` -- AIContextManifest allowlist
builder, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_gateway.context import (
    AIContextManifest,
    CoachMode,
    InputArtifactRef,
    build_context_manifest,
    compute_context_fingerprint,
)
from persistence.ai_record_repository import SqlAlchemyAIRecordRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id


def test_fingerprint_is_deterministic_and_order_independent() -> None:
    ref_a = InputArtifactRef(artifact_ref="question:1", version=RecordVersion(1))
    ref_b = InputArtifactRef(artifact_ref="question:2", version=RecordVersion(3))

    forward = compute_context_fingerprint(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        input_artifact_refs_with_versions=(ref_a, ref_b),
    )
    backward = compute_context_fingerprint(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        input_artifact_refs_with_versions=(ref_b, ref_a),
    )

    assert forward == backward
    assert len(forward) == 64


def test_fingerprint_changes_when_a_member_version_changes() -> None:
    before = compute_context_fingerprint(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        input_artifact_refs_with_versions=(
            InputArtifactRef(artifact_ref="question:1", version=RecordVersion(1)),
        ),
    )
    after = compute_context_fingerprint(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        input_artifact_refs_with_versions=(
            InputArtifactRef(artifact_ref="question:1", version=RecordVersion(2)),
        ),
    )

    assert before != after


def test_denies_an_empty_artifact_ref() -> None:
    with pytest.raises(ValueError, match="artifact_ref"):
        InputArtifactRef(artifact_ref="", version=RecordVersion(1))


def test_build_context_manifest_never_accepts_an_unresolved_query() -> None:
    """Structural proof (14 section 48's own forbidden pattern: "whole
    Workspace dump"): `build_context_manifest`'s own signature has no
    parameter through which a caller could hand it "everything in the
    Workspace" -- every input artifact is an explicit, individually
    named `InputArtifactRef`."""
    import inspect

    signature = inspect.signature(build_context_manifest)
    assert "input_artifact_refs_with_versions" in signature.parameters
    forbidden_names = {"workspace_dump", "all_artifacts", "query", "filter"}
    assert not forbidden_names & set(signature.parameters)


def test_build_context_manifest_produces_a_reconstructable_manifest() -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    refs = (
        InputArtifactRef(artifact_ref="question:1", version=RecordVersion(1)),
        InputArtifactRef(artifact_ref="question:2", version=RecordVersion(1)),
    )

    manifest = build_context_manifest(
        ai_context_manifest_id=uuid.uuid4(),
        workspace_id=workspace_id,
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        requesting_actor_ref="user-ref-1",
        input_artifact_refs_with_versions=refs,
        source_classifications=("human_question",),
        assembled_at=_NOW,
        coach_mode=CoachMode.REFLECTIVE,
        burst_mode="HUMAN_ONLY",
    )

    assert manifest.workspace_id == workspace_id
    assert manifest.input_artifact_refs_with_versions == refs
    assert manifest.context_fingerprint == compute_context_fingerprint(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        input_artifact_refs_with_versions=refs,
    )


def test_denies_a_non_coach_mode_value() -> None:
    with pytest.raises(TypeError):
        AIContextManifest(
            ai_context_manifest_id=uuid.uuid4(),
            workspace_id=WorkspaceId(uuid.uuid4()),
            ai_operation_id=AIOperationId.AIOP_001,
            ai_operation_contract_version=ContractVersion("1.0"),
            requesting_actor_ref="user-ref-1",
            input_artifact_refs_with_versions=(),
            source_classifications=(),
            assembled_at=_NOW,
            context_fingerprint="fp",
            coach_mode="REFLECTIVE",  # type: ignore[arg-type]
        )


def test_full_round_trip_create_and_get(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-context-roundtrip@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    manifest = build_context_manifest(
        ai_context_manifest_id=uuid.uuid4(),
        workspace_id=workspace_id,
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        requesting_actor_ref="user-ref-1",
        input_artifact_refs_with_versions=(
            InputArtifactRef(artifact_ref="question:1", version=RecordVersion(1)),
        ),
        source_classifications=("human_question",),
        assembled_at=_NOW,
        coach_mode=CoachMode.REFLECTIVE,
        burst_mode="HUMAN_ONLY",
        method_ref="QUESTION_BURST",
        excluded_context_classes=("ai_question",),
    )

    repo.create_context_manifest(manifest)
    fetched = repo.get_context_manifest(manifest.ai_context_manifest_id)

    assert fetched == manifest


def test_cross_workspace_context_manifest_is_not_representable(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: wrong Workspace artifact, applied
    to the context manifest itself."""
    _bootstrap(db_connection, email="ai-context-cross@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    manifest = build_context_manifest(
        ai_context_manifest_id=uuid.uuid4(),
        workspace_id=WorkspaceId(uuid.uuid4()),  # never bootstrapped
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=ContractVersion("1.0"),
        requesting_actor_ref="user-ref-1",
        input_artifact_refs_with_versions=(),
        source_classifications=(),
        assembled_at=_NOW,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_context_manifest(manifest)
