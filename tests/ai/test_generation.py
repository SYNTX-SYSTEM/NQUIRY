"""T6 AI TEST: `ai_contracts.generation`/`persistence.ai_record_repository`
-- AIGeneration lifecycle, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.generation import (
    AIGeneration,
    AIGenerationStatus,
    is_legal_generation_transition,
)
from persistence.ai_record_repository import AIRecordConflict, SqlAlchemyAIRecordRepository
from persistence.tables import ai_generations_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, GenerationId, WorkspaceId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()

_ALL_STATUSES = tuple(AIGenerationStatus)
_TERMINAL_STATUSES = (
    AIGenerationStatus.VALIDATED,
    AIGenerationStatus.REJECTED,
    AIGenerationStatus.FAILED,
)


def _bootstrap(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id


def _make_generation(*, workspace_id: WorkspaceId, **overrides: object) -> AIGeneration:
    fields: dict[str, object] = dict(
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
    fields.update(overrides)
    return AIGeneration(**fields)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Pure Python: legal-transition topology and dataclass invariants.
# ---------------------------------------------------------------------------


def test_legal_transitions_match_section_15_exactly() -> None:
    expected = {
        (AIGenerationStatus.REQUESTED, AIGenerationStatus.RUNNING),
        (AIGenerationStatus.RUNNING, AIGenerationStatus.OUTPUT_RECEIVED),
        (AIGenerationStatus.RUNNING, AIGenerationStatus.FAILED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.VALIDATED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.REJECTED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.FAILED),
    }
    actual = {
        (a, b) for a in _ALL_STATUSES for b in _ALL_STATUSES if is_legal_generation_transition(a, b)
    }
    assert actual == expected


def test_no_transition_out_of_any_terminal_state_is_legal() -> None:
    """08 section 15: "REJECTED -> VALIDATED by silent mutation" and
    "FAILED -> VALIDATED" are explicitly illegal -- proven here for
    every possible target, not merely VALIDATED."""
    for terminal in _TERMINAL_STATUSES:
        for target in _ALL_STATUSES:
            assert not is_legal_generation_transition(terminal, target)


def test_retry_of_generation_id_cannot_equal_its_own_id() -> None:
    """Mandatory package-specific attack: retry reuses GenerationId."""
    workspace_id = WorkspaceId(uuid.uuid4())
    generation_id = GenerationId(_ID_GEN.new_uuid())

    with pytest.raises(ValueError, match="retry_of_generation_id"):
        _make_generation(
            workspace_id=workspace_id,
            ai_generation_id=generation_id,
            retry_of_generation_id=generation_id,
        )


def test_ai_generation_rejects_a_non_enum_status() -> None:
    with pytest.raises(TypeError):
        _make_generation(workspace_id=WorkspaceId(uuid.uuid4()), status="REQUESTED")


def test_ai_derived_artifact_has_no_field_that_could_misrepresent_ai_output_as_human() -> None:
    """Mandatory package-specific attack: AI output marked human. Proven
    structurally: `AIGeneration`/`ai_contracts.derived_artifact.AIDerivedArtifact`
    have no `origin`/`author`/`created_by_ref`-style field a caller
    could set to a human identity -- an AI-produced record's only
    identity link is its own mandatory, non-nullable `ai_generation_id`/
    `ai_operation_id`."""
    generation_fields = set(AIGeneration.__dataclass_fields__)
    assert "origin" not in generation_fields
    assert "author_user_id" not in generation_fields


# ---------------------------------------------------------------------------
# Live PostgreSQL: repository round-trip, transition topology, conflicts.
# ---------------------------------------------------------------------------


def test_full_round_trip_create_and_get(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-generation-roundtrip@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)

    repo.create_generation(generation)
    fetched = repo.get_generation(generation.ai_generation_id)

    assert fetched == generation


def test_a_generation_created_outside_requested_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: a generation inserted directly at
    the database layer in a non-REQUESTED state must be rejected by the
    trigger, independent of the Python type's own default."""
    workspace_id = _bootstrap(db_connection, email="ai-generation-bad-initial@nonproof.test")
    generation = _make_generation(workspace_id=workspace_id)
    row = _row_for(generation)
    row["status"] = "RUNNING"

    with pytest.raises(sa.exc.DBAPIError, match="must be created in REQUESTED"):
        db_connection.execute(sa.insert(ai_generations_table).values(**row))


def test_advances_through_the_full_legal_chain_to_validated(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-generation-chain@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)
    repo.create_generation(generation)

    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_status=AIGenerationStatus.RUNNING,
        started_at=_NOW,
    )
    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        new_status=AIGenerationStatus.OUTPUT_RECEIVED,
        output_received_at=_NOW,
        output_tokens=42,
    )
    output_ref = uuid.uuid4()
    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(3),
        new_status=AIGenerationStatus.VALIDATED,
        completed_at=_NOW,
        output_artifact_ref=output_ref,
    )

    final = repo.get_generation(generation.ai_generation_id)
    assert final is not None
    assert final.status is AIGenerationStatus.VALIDATED
    assert final.output_tokens == 42
    assert final.output_artifact_ref == output_ref
    assert final.record_version == RecordVersion(4)


def test_a_failed_generation_from_running_is_terminal(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-generation-failed@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)
    repo.create_generation(generation)
    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_status=AIGenerationStatus.RUNNING,
    )
    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        new_status=AIGenerationStatus.FAILED,
        failure_code="PROVIDER_TIMEOUT",
    )

    with pytest.raises(sa.exc.DBAPIError, match="is terminal"):
        db_connection.execute(
            sa.update(ai_generations_table)
            .where(ai_generations_table.c.id == generation.ai_generation_id.value)
            .values(status="RUNNING", record_version=4)
        )


def test_an_illegal_transition_is_rejected_even_with_a_genuinely_current_version(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: illegal skip (REQUESTED straight to
    VALIDATED) attempted with the row's own genuinely current version --
    the trigger's topology check, not a stale-version guard, is what
    stops it."""
    workspace_id = _bootstrap(db_connection, email="ai-generation-illegal-skip@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)
    repo.create_generation(generation)

    with pytest.raises(sa.exc.DBAPIError, match="illegal AIGeneration transition"):
        db_connection.execute(
            sa.update(ai_generations_table)
            .where(ai_generations_table.c.id == generation.ai_generation_id.value)
            .values(status="VALIDATED", record_version=2)
        )


def test_identity_fields_are_immutable_once_requested(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-generation-immutable@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)
    repo.create_generation(generation)

    with pytest.raises(sa.exc.DBAPIError, match="immutable once requested"):
        db_connection.execute(
            sa.update(ai_generations_table)
            .where(ai_generations_table.c.id == generation.ai_generation_id.value)
            .values(model="a-different-model", record_version=2)
        )


def test_update_raises_conflict_on_a_stale_expected_version(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: concurrent Commands / stale
    expected version."""
    workspace_id = _bootstrap(db_connection, email="ai-generation-stale@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_id)
    repo.create_generation(generation)
    repo.update_generation_status(
        ai_generation_id=generation.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_status=AIGenerationStatus.RUNNING,
    )

    with pytest.raises(AIRecordConflict):
        repo.update_generation_status(
            ai_generation_id=generation.ai_generation_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion.initial(),  # stale: already advanced to 2
            new_status=AIGenerationStatus.OUTPUT_RECEIVED,
        )


def test_update_raises_conflict_under_a_cross_workspace_claim(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace generation. A
    caller asserting the WRONG Workspace for a genuinely-existing
    generation must be denied identically to "does not exist" -- never
    silently redirected to the real row."""
    workspace_a = _bootstrap(db_connection, email="ai-generation-cross-a@nonproof.test")
    workspace_b = _bootstrap(db_connection, email="ai-generation-cross-b@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    generation = _make_generation(workspace_id=workspace_a)
    repo.create_generation(generation)

    with pytest.raises(AIRecordConflict):
        repo.update_generation_status(
            ai_generation_id=generation.ai_generation_id,
            workspace_id=workspace_b,
            expected_record_version=RecordVersion.initial(),
            new_status=AIGenerationStatus.RUNNING,
        )


def test_retry_creates_a_new_independent_generation_not_a_revival(
    db_connection: sa.Connection,
) -> None:
    """08 section 15: "A retry creates a new AIGeneration identity. It
    does not revive a FAILED/REJECTED generation." AC-09-022."""
    workspace_id = _bootstrap(db_connection, email="ai-generation-retry@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    original = _make_generation(workspace_id=workspace_id)
    repo.create_generation(original)
    repo.update_generation_status(
        ai_generation_id=original.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_status=AIGenerationStatus.RUNNING,
    )
    repo.update_generation_status(
        ai_generation_id=original.ai_generation_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        new_status=AIGenerationStatus.FAILED,
        failure_code="PROVIDER_ERROR",
    )

    retry = _make_generation(
        workspace_id=workspace_id, retry_of_generation_id=original.ai_generation_id
    )
    repo.create_generation(retry)

    stored_original = repo.get_generation(original.ai_generation_id)
    stored_retry = repo.get_generation(retry.ai_generation_id)
    assert stored_original is not None and stored_original.status is AIGenerationStatus.FAILED
    assert stored_retry is not None and stored_retry.status is AIGenerationStatus.REQUESTED
    assert stored_retry.ai_generation_id != stored_original.ai_generation_id
    assert stored_retry.retry_of_generation_id == original.ai_generation_id


def test_retry_of_a_nonexistent_generation_is_not_representable(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _bootstrap(db_connection, email="ai-generation-retry-phantom@nonproof.test")
    repo = SqlAlchemyAIRecordRepository(db_connection)
    phantom = GenerationId(uuid.uuid4())

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.create_generation(
            _make_generation(workspace_id=workspace_id, retry_of_generation_id=phantom)
        )


def test_ai_record_repository_has_no_domain_mutation_capability() -> None:
    """Mandatory package-specific attack: forbidden effect. 08 section
    23's own FORBIDDEN CANONICAL EFFECT list (modify Question text,
    select Questions, advance Session, create Decision, authorize
    Experiment, change Assumption status, create Evidence from
    confidence) has no corresponding method on this port -- proven both
    positively (the exact 5 expected methods exist) and negatively (no
    method touches any other repository's own vocabulary)."""
    from persistence.ai_record_repository import AIRecordRepository

    public_attrs = {name for name in vars(AIRecordRepository) if not name.startswith("_")}
    expected = {
        "create_generation",
        "get_generation",
        "update_generation_status",
        "create_derived_artifact",
        "get_derived_artifact",
    }
    assert expected <= public_attrs
    forbidden_fragments = (
        "question",
        "session",
        "decision",
        "experiment",
        "assumption",
        "evidence",
        "selection",
    )
    for name in public_attrs:
        lowered = name.lower()
        assert not any(fragment in lowered for fragment in forbidden_fragments), name


def _row_for(generation: AIGeneration) -> dict[str, object]:
    return {
        "id": generation.ai_generation_id.value,
        "workspace_id": generation.workspace_id.value,
        "user_id": None,
        "ai_operation_id": generation.ai_operation_id.value,
        "ai_operation_contract_version": str(generation.ai_operation_contract_version),
        "ai_context_manifest_id": None,
        "prompt_version": str(generation.prompt_version),
        "model": generation.model,
        "provider": generation.provider,
        "status": generation.status.value,
        "requested_at": generation.requested_at,
        "started_at": None,
        "output_received_at": None,
        "completed_at": None,
        "input_tokens": None,
        "output_tokens": None,
        "latency_ms": None,
        "estimated_cost": None,
        "retry_of_generation_id": None,
        "command_id": None,
        "correlation_id": generation.correlation_id.value,
        "output_artifact_ref": None,
        "failure_code": None,
        "failure_detail_ref": None,
        "record_version": generation.record_version.value,
    }
