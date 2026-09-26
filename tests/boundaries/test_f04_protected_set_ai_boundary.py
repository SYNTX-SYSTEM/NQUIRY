"""F04 WU-04.2 (FBR-F04-3): the protected set against AI, for ANY requester.

MUST BECOME TRUE: every AI operation category is denied while the Burst is
ACTIVE or PAUSED, whoever requests it (HUMAN_USER, SYSTEM_SERVICE,
AI_PROCESSOR, EXTERNAL_SYSTEM). BND-009 permits an invocation only over a
COMPLETED Burst whose frozen-set fingerprint is verified.

MUST REMAIN IMPOSSIBLE: a human- or system-requested AI operation during the
Burst; an invocation over an unfrozen or unverified set.

FALSIFIERS: B1 (RED before the repair for HUMAN_USER / SYSTEM_SERVICE), B2, B3.
B4 is the unchanged F03 capture suite.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from ai_contracts.aiop import AIOperationId
from application.burst_contamination import (
    BurstContaminationVerdict,
    BurstOperationCategory,
    evaluate_burst_contamination_guard,
)
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.bnd_009_ai_invocation import Bnd009AiInvocationEvaluator, Bnd009Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from domain.burst import BurstState
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_AI = [
    Bnd008OperationCategory.AI_ANALYSIS,
    Bnd008OperationCategory.AI_REFRAME,
    Bnd008OperationCategory.AI_CLASSIFY,
    Bnd008OperationCategory.AI_CLUSTER,
    Bnd008OperationCategory.AI_QUESTION_GENERATION,
]


def _context(actor_class: ActorClass, ws: WorkspaceId | None = None) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=ws or WorkspaceId(uuid.uuid4()),
        operation="F04",
        actor=ActorIdentity(actor_class, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


@pytest.mark.parametrize("actor_class", list(ActorClass))
@pytest.mark.parametrize("state", [BurstState.ACTIVE, BurstState.PAUSED])
@pytest.mark.parametrize("operation", _AI)
def test_b1_ai_category_denied_during_protected_burst_for_any_requester(
    actor_class: ActorClass, state: BurstState, operation: Bnd008OperationCategory
) -> None:
    context = _context(actor_class)
    proof = Bnd008QuestionBurstEvaluator().evaluate(
        Bnd008Input(
            boundary_id=BoundaryId.BND_008,
            context=context,
            burst_state=state,
            operation_category=operation,
        ),
        context,
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_OPERATION_DURING_PROTECTED_BURST"
    guard = evaluate_burst_contamination_guard(
        burst_state=state,
        operation=BurstOperationCategory[operation.name],
        actor_class=actor_class,
    )
    assert guard.verdict is BurstContaminationVerdict.DENY


@pytest.mark.parametrize("actor_class", [ActorClass.HUMAN_USER, ActorClass.SYSTEM_SERVICE])
def test_b1_control_ai_analysis_after_completion_is_not_denied_by_bnd_008(
    actor_class: ActorClass,
) -> None:
    context = _context(actor_class)
    proof = Bnd008QuestionBurstEvaluator().evaluate(
        Bnd008Input(
            boundary_id=BoundaryId.BND_008,
            context=context,
            burst_state=BurstState.COMPLETED,
            operation_category=Bnd008OperationCategory.AI_ANALYSIS,
        ),
        context,
    )
    assert proof.result is BoundaryResult.ALLOW


def _bnd009(context: BoundaryContext, *, burst_state: BurstState, verified: bool) -> BoundaryResult:
    proof = Bnd009AiInvocationEvaluator().evaluate(
        Bnd009Input(
            boundary_id=BoundaryId.BND_009,
            context=context,
            ai_operation_id=AIOperationId.AIOP_001,
            ai_operation_contract_version=ContractVersion("1.0"),
            aiop_contract_approved=True,
            context_manifest_workspace_id=context.workspace_id,
            burst_state=burst_state,
            frozen_set_verified=verified,
        ),
        context,
    )
    return proof.result


@pytest.mark.parametrize("state", [BurstState.PREPARED, BurstState.ACTIVE, BurstState.PAUSED])
def test_b2_bnd_009_denies_when_burst_not_completed(state: BurstState) -> None:
    assert (
        _bnd009(_context(ActorClass.SYSTEM_SERVICE), burst_state=state, verified=True)
        is BoundaryResult.DENY
    )


def test_b3_bnd_009_denies_an_unverified_frozen_set() -> None:
    assert (
        _bnd009(
            _context(ActorClass.SYSTEM_SERVICE), burst_state=BurstState.COMPLETED, verified=False
        )
        is BoundaryResult.DENY
    )


def test_b2_b3_control_completed_and_verified_is_allowed() -> None:
    assert (
        _bnd009(
            _context(ActorClass.SYSTEM_SERVICE), burst_state=BurstState.COMPLETED, verified=True
        )
        is BoundaryResult.ALLOW
    )


def test_bnd_009_denies_an_external_system_requester() -> None:
    """06 §15 REQUESTING ACTOR: HUMAN_USER or SYSTEM_SERVICE only."""
    assert (
        _bnd009(
            _context(ActorClass.EXTERNAL_SYSTEM), burst_state=BurstState.COMPLETED, verified=True
        )
        is BoundaryResult.DENY
    )
