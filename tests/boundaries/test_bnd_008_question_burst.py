"""T4 BOUNDARY TEST: BND-008 Question Burst Contamination Evaluator.
Pure Python.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from domain.burst import BurstState
from domain.burst_input import check_burst_input
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _context(actor_class: ActorClass) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="TEST_OPERATION",
        actor=ActorIdentity(actor_class, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _evaluate(
    *, actor_class: ActorClass, burst_state: BurstState, operation: Bnd008OperationCategory
):  # F03 WU-03.5: a CAPTURE also needs an established BURST_INPUT_VALID (06 §14).
    context = _context(actor_class)
    evaluator = Bnd008QuestionBurstEvaluator()
    boundary_input = Bnd008Input(
        boundary_id=BoundaryId.BND_008,
        context=context,
        burst_state=burst_state,
        operation_category=operation,
        input_check=(
            check_burst_input("Why did it drop?")
            if operation is Bnd008OperationCategory.CAPTURE_BURST_QUESTION
            else None
        ),
    )
    return evaluator.evaluate(boundary_input, context)


def test_denies_ai_analysis_during_active_burst() -> None:
    """Mandatory adversarial attack: ACTIVE Burst AI contamination."""
    proof = _evaluate(
        actor_class=ActorClass.AI_PROCESSOR,
        burst_state=BurstState.ACTIVE,
        operation=Bnd008OperationCategory.AI_ANALYSIS,
    )

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_OPERATION_DURING_PROTECTED_BURST"


def test_denies_ai_analysis_during_paused_burst() -> None:
    proof = _evaluate(
        actor_class=ActorClass.AI_PROCESSOR,
        burst_state=BurstState.PAUSED,
        operation=Bnd008OperationCategory.AI_ANALYSIS,
    )

    assert proof.result is BoundaryResult.DENY


def test_allows_ai_analysis_after_completed() -> None:
    proof = _evaluate(
        actor_class=ActorClass.AI_PROCESSOR,
        burst_state=BurstState.COMPLETED,
        operation=Bnd008OperationCategory.AI_ANALYSIS,
    )

    assert proof.result is BoundaryResult.ALLOW


def test_denies_ai_controlling_burst_lifecycle() -> None:
    proof = _evaluate(
        actor_class=ActorClass.AI_PROCESSOR,
        burst_state=BurstState.PREPARED,
        operation=Bnd008OperationCategory.START_BURST,
    )

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE"


def test_allows_human_capture_during_active() -> None:
    proof = _evaluate(
        actor_class=ActorClass.HUMAN_USER,
        burst_state=BurstState.ACTIVE,
        operation=Bnd008OperationCategory.CAPTURE_BURST_QUESTION,
    )

    assert proof.result is BoundaryResult.ALLOW
