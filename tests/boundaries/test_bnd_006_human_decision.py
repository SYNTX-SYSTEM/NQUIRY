"""T4 BOUNDARY TEST: BND-006 Human Decision Authority Evaluator. Pure Python."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_006_human_decision import Bnd006HumanDecisionEvaluator, Bnd006Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _context(actor_class: ActorClass) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="RECORD_DECISION",
        actor=ActorIdentity(actor_class, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def test_allows_a_human_requester_with_human_authored_content() -> None:
    context = _context(ActorClass.HUMAN_USER)
    evaluator = Bnd006HumanDecisionEvaluator()
    boundary_input = Bnd006Input(
        boundary_id=BoundaryId.BND_006, context=context, decision_origin=ActorClass.HUMAN_USER
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_ai_authored_decision_content() -> None:
    """Mandatory-category adversarial attack: missing human Decision --
    06 section 12 TESTABLE INVARIANT: "No AI output can cross BND-006
    as an authority-bearing human decision."
    """
    context = _context(ActorClass.HUMAN_USER)
    evaluator = Bnd006HumanDecisionEvaluator()
    boundary_input = Bnd006Input(
        boundary_id=BoundaryId.BND_006, context=context, decision_origin=ActorClass.AI_PROCESSOR
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert "AI_PROCESSOR" in proof.reason_code


def test_denies_a_non_human_requester_regardless_of_decision_origin() -> None:
    """Novel attack: AI actor attempting Decision creation -- distinct
    from "AI-authored content": here the *requester itself* is not
    human, even if it claims human-authored content.
    """
    context = _context(ActorClass.AI_PROCESSOR)
    evaluator = Bnd006HumanDecisionEvaluator()
    boundary_input = Bnd006Input(
        boundary_id=BoundaryId.BND_006, context=context, decision_origin=ActorClass.HUMAN_USER
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DECISION_CREATION_REQUIRES_HUMAN_REQUESTER"


def test_denies_system_service_attempting_decision_creation() -> None:
    context = _context(ActorClass.SYSTEM_SERVICE)
    evaluator = Bnd006HumanDecisionEvaluator()
    boundary_input = Bnd006Input(
        boundary_id=BoundaryId.BND_006, context=context, decision_origin=ActorClass.HUMAN_USER
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
