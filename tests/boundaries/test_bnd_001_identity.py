"""T4 BOUNDARY TEST: BND-001 Identity Evaluator. Pure Python."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _context(actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="TEST_OPERATION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def test_allows_a_required_actor_class() -> None:
    actor = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    context = _context(actor)
    evaluator = Bnd001IdentityEvaluator()
    boundary_input = Bnd001Input(
        boundary_id=BoundaryId.BND_001,
        context=context,
        required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_an_actor_class_the_operation_does_not_accept() -> None:
    """Mandatory adversarial attack: forged identity -- an AI_PROCESSOR
    actor requesting a HUMAN_USER-only operation.
    """
    actor = ActorIdentity(ActorClass.AI_PROCESSOR, UserId(uuid.uuid4()))
    context = _context(actor)
    evaluator = Bnd001IdentityEvaluator()
    boundary_input = Bnd001Input(
        boundary_id=BoundaryId.BND_001,
        context=context,
        required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert "AI_PROCESSOR" in proof.reason_code


def test_ai_processor_can_never_pass_as_human_user() -> None:
    """06 section 7 TESTABLE INVARIANT: "AI_PROCESSOR can never pass as
    HUMAN_USER or SYSTEM_SERVICE." Exhaustive over all 4 actor classes
    when only HUMAN_USER is required.
    """
    evaluator = Bnd001IdentityEvaluator()
    for actor_class in ActorClass:
        actor = ActorIdentity(actor_class, UserId(uuid.uuid4()))
        context = _context(actor)
        boundary_input = Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        )

        proof = evaluator.evaluate(boundary_input, context)

        if actor_class is ActorClass.HUMAN_USER:
            assert proof.result is BoundaryResult.ALLOW
        else:
            assert proof.result is BoundaryResult.DENY


def test_system_service_allowed_when_operation_accepts_it() -> None:
    """Positive control: SYSTEM_SERVICE is not universally denied, only
    when the operation does not accept it.
    """
    actor = ActorIdentity(ActorClass.SYSTEM_SERVICE, UserId(uuid.uuid4()))
    context = _context(actor)
    evaluator = Bnd001IdentityEvaluator()
    boundary_input = Bnd001Input(
        boundary_id=BoundaryId.BND_001,
        context=context,
        required_actor_classes=frozenset({ActorClass.HUMAN_USER, ActorClass.SYSTEM_SERVICE}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
