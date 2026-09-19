"""T4 BOUNDARY TEST: BND-009 AI Invocation Boundary. Pure Python (no
persistence involved in this evaluator's own logic), mirroring
`test_bnd_008_question_burst.py`'s own no-DB shape.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ai_contracts.aiop import AIOperationId
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_009_ai_invocation import Bnd009AiInvocationEvaluator, Bnd009Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_EVALUATOR = Bnd009AiInvocationEvaluator()


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="AIOP-001",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _base_input(
    *, workspace_id: WorkspaceId, context: BoundaryContext, **overrides: object
) -> Bnd009Input:
    kwargs: dict[str, object] = {
        "boundary_id": BoundaryId.BND_009,
        "context": context,
        "ai_operation_id": AIOperationId.AIOP_001,
        "ai_operation_contract_version": ContractVersion("1.0"),
        "aiop_contract_approved": True,
        "context_manifest_workspace_id": workspace_id,
    }
    kwargs.update(overrides)
    return Bnd009Input(**kwargs)  # type: ignore[arg-type]


def test_allows_a_well_formed_human_requested_invocation() -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "AI_INVOCATION_PERMITTED"


def test_allows_a_system_service_requested_invocation() -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.SYSTEM_SERVICE, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_ai_self_invocation() -> None:
    """Mandatory package-specific attack: AI self-invocation. 06
    section 15: "AI_PROCESSOR may not self-authorize a new invocation" --
    unconditional, unlike BND-008's own Burst-state-dependent check."""
    workspace_id = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.AI_PROCESSOR, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_SELF_INVOCATION_NOT_PERMITTED"


def test_ai_self_invocation_denial_precedes_every_other_check() -> None:
    """Novel/adapted attack: proves ordering -- AI self-invocation is
    denied first, even when the request is ALSO cross-Workspace and
    missing an approved contract (06 section 15's own unconditional
    "AI_PROCESSOR may not self-authorize" is not merely one input among
    several this evaluator weighs)."""
    workspace_a = WorkspaceId(uuid.uuid4())
    workspace_b = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.AI_PROCESSOR, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_a, actor=actor)
    boundary_input = _base_input(
        workspace_id=workspace_a,
        context=context,
        context_manifest_workspace_id=workspace_b,
        aiop_contract_approved=False,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_SELF_INVOCATION_NOT_PERMITTED"


def test_denies_cross_workspace_context() -> None:
    """Mandatory adversarial attack: cross-Workspace context."""
    workspace_a = WorkspaceId(uuid.uuid4())
    workspace_b = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_a, actor=actor)
    boundary_input = _base_input(
        workspace_id=workspace_a, context=context, context_manifest_workspace_id=workspace_b
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CROSS_WORKSPACE_CONTEXT"


def test_requires_an_approved_operation_contract() -> None:
    """Mandatory package-specific attack: invalid contract. 06 section
    15 REQUIRE list: "operation contract" -- REQUIRE, not DENY, since
    this is a missing prerequisite rather than a known-bad request."""
    workspace_id = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = _base_input(
        workspace_id=workspace_id, context=context, aiop_contract_approved=False
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.REQUIRE
    assert proof.reason_code == "APPROVED_OPERATION_CONTRACT_REQUIRED"


def test_cross_workspace_denial_precedes_the_contract_require() -> None:
    """Novel/adapted attack: proves DENY ordering -- a request that is
    BOTH cross-Workspace AND missing an approved contract must DENY,
    never REQUIRE (06 section 3: DENY is terminal and takes precedence
    -- a REQUIRE must never mask a genuine DENY condition)."""
    workspace_a = WorkspaceId(uuid.uuid4())
    workspace_b = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_a, actor=actor)
    boundary_input = _base_input(
        workspace_id=workspace_a,
        context=context,
        context_manifest_workspace_id=workspace_b,
        aiop_contract_approved=False,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CROSS_WORKSPACE_CONTEXT"


def test_registers_cleanly_in_the_boundary_registry() -> None:
    """Novel/adapted attack: prove BND-009 composes with the generic
    chain evaluator exactly like every other boundary."""
    workspace_id = WorkspaceId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(workspace_id=workspace_id, actor=actor)
    boundary_input = _base_input(workspace_id=workspace_id, context=context)
    registry = BoundaryRegistry()
    registry.register(_EVALUATOR)

    chain_result = evaluate_chain(
        registry, [BoundaryId.BND_009], {BoundaryId.BND_009: boundary_input}, context
    )

    assert chain_result.is_allowed
    assert chain_result.proofs[0].reason_code == "AI_INVOCATION_PERMITTED"
