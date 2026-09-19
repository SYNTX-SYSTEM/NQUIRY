"""T4 BOUNDARY TEST: BND-010 AI Output / Canonical State Boundary. Pure
Python, mirroring `test_bnd_009_ai_invocation.py`'s own no-DB shape.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ai_contracts.generation import AIGenerationStatus, AIValidationResult
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_010_ai_output import Bnd010AiOutputEvaluator, Bnd010Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_EVALUATOR = Bnd010AiOutputEvaluator()


def _context(*, workspace_id: WorkspaceId) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="PERSIST_DERIVED_ARTIFACT",
        actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _base_input(
    *, workspace_id: WorkspaceId, context: BoundaryContext, **overrides: object
) -> Bnd010Input:
    kwargs: dict[str, object] = {
        "boundary_id": BoundaryId.BND_010,
        "context": context,
        "ai_generation_status": AIGenerationStatus.VALIDATED,
        "validation_result": AIValidationResult.VALIDATED,
        "source_workspace_id": workspace_id,
        "ai_validation_proof_ref": str(uuid.uuid4()),
    }
    kwargs.update(overrides)
    return Bnd010Input(**kwargs)  # type: ignore[arg-type]


def test_allows_persisting_a_validated_derived_artifact() -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_id)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "DERIVED_ARTIFACT_ACCEPTABLE"
    assert proof.evidence_proof_refs == (boundary_input.ai_validation_proof_ref,)


def test_denies_persistence_when_generation_is_not_validated() -> None:
    """Mandatory adversarial attack: forbidden canonical effect --
    persisting from a REJECTED/FAILED/in-flight generation."""
    workspace_id = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_id)
    boundary_input = _base_input(
        workspace_id=workspace_id,
        context=context,
        ai_generation_status=AIGenerationStatus.REJECTED,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "GENERATION_NOT_VALIDATED"
    assert proof.evidence_proof_refs == ()


def test_denies_persistence_when_validation_result_is_not_validated() -> None:
    """Novel/adapted attack: a generation whose own status somehow
    claims VALIDATED but whose actual AI_VALIDATION_PROOF disagrees --
    the two facts are checked independently, neither alone is
    sufficient."""
    workspace_id = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_id)
    boundary_input = _base_input(
        workspace_id=workspace_id,
        context=context,
        validation_result=AIValidationResult.INDETERMINATE,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_VALIDATION_PROOF_NOT_VALIDATED"


def test_denies_cross_workspace_derived_artifact() -> None:
    """Mandatory adversarial attack: wrong Workspace artifact."""
    workspace_a = WorkspaceId(uuid.uuid4())
    workspace_b = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_a)
    boundary_input = _base_input(
        workspace_id=workspace_a, context=context, source_workspace_id=workspace_b
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CROSS_WORKSPACE_DERIVED_ARTIFACT"


def test_generation_status_denial_precedes_workspace_check() -> None:
    """Novel/adapted attack: ordering -- a not-VALIDATED generation is
    denied before the (also failing) Workspace check ever matters."""
    workspace_a = WorkspaceId(uuid.uuid4())
    workspace_b = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_a)
    boundary_input = _base_input(
        workspace_id=workspace_a,
        context=context,
        ai_generation_status=AIGenerationStatus.FAILED,
        source_workspace_id=workspace_b,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "GENERATION_NOT_VALIDATED"


def test_rejects_a_non_enum_generation_status() -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_id)

    try:
        Bnd010Input(
            boundary_id=BoundaryId.BND_010,
            context=context,
            ai_generation_status="VALIDATED",  # type: ignore[arg-type]
            validation_result=AIValidationResult.VALIDATED,
            source_workspace_id=workspace_id,
            ai_validation_proof_ref=str(uuid.uuid4()),
        )
    except TypeError as exc:
        assert "ai_generation_status" in str(exc)
    else:
        raise AssertionError("expected TypeError for a non-enum ai_generation_status")


def test_registers_cleanly_in_the_boundary_registry() -> None:
    """Novel/adapted attack: prove BND-010 composes with the generic
    chain evaluator exactly like every other boundary."""
    workspace_id = WorkspaceId(uuid.uuid4())
    context = _context(workspace_id=workspace_id)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)
    registry = BoundaryRegistry()
    registry.register(_EVALUATOR)

    chain_result = evaluate_chain(
        registry, [BoundaryId.BND_010], {BoundaryId.BND_010: boundary_input}, context
    )

    assert chain_result.is_allowed
    assert chain_result.proofs[0].reason_code == "DERIVED_ARTIFACT_ACCEPTABLE"
