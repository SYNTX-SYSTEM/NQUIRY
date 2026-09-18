"""T4 BOUNDARY TEST: BND-007 State Transition Evaluator. Pure Python,
using real `domain.session_transitions`/`domain.burst_transitions`
resolutions -- not stubs.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_007_state_transition import Bnd007Input, Bnd007StateTransitionEvaluator
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from domain.burst import BurstState
from domain.burst_transitions import resolve_burst_transition_to_state
from domain.decision import DecisionState, resolve_decision_transition_to_state
from domain.question_selection import SelectionTransitionId, resolve_selection_transition
from domain.session import SessionState
from domain.session_transitions import resolve_session_transition_to_state
from semantic_types.ids import ChallengeId, CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _context() -> BoundaryContext:
    return BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def test_allows_a_legal_session_transition() -> None:
    context = _context()
    resolution = resolve_session_transition_to_state(
        current_state=SessionState.DRAFT, target_state=SessionState.SETUP
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_an_illegal_session_transition() -> None:
    """Mandatory adversarial attack: illegal state transition."""
    context = _context()
    resolution = resolve_session_transition_to_state(
        current_state=SessionState.DRAFT, target_state=SessionState.CHALLENGE_CAPTURE
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_ILLEGAL_TRANSITION"


def test_denies_reopening_a_closed_session() -> None:
    """06 section 13 DENY example: "CLOSED Session reopening"."""
    context = _context()
    resolution = resolve_session_transition_to_state(
        current_state=SessionState.CLOSED, target_state=SessionState.DRAFT
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_TERMINAL_STATE"


def test_allows_a_legal_burst_transition() -> None:
    context = _context()
    resolution = resolve_burst_transition_to_state(
        current_state=BurstState.PREPARED, target_state=BurstState.ACTIVE
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_an_illegal_burst_transition() -> None:
    context = _context()
    resolution = resolve_burst_transition_to_state(
        current_state=BurstState.PREPARED, target_state=BurstState.COMPLETED
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY


def test_allows_a_state_preserving_selection_mutation() -> None:
    """PKG-14: 06 section 13's own REQUESTED OPERATION line ("one
    specific 03 transition or state-preserving consequential
    mutation") -- proven with a real `SelectionTransitionResolution`,
    not a stub.
    """
    context = _context()
    challenge_id = ChallengeId(uuid.uuid4())
    resolution = resolve_selection_transition(
        transition_id=SelectionTransitionId.TRN_SEL_001,
        current_session_state=SessionState.QUESTION_SELECTION,
        session_challenge_id=challenge_id,
        question_challenge_id=challenge_id,
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "STATE_ELIGIBLE"


def test_denies_selection_when_session_is_not_in_question_selection_state() -> None:
    context = _context()
    challenge_id = ChallengeId(uuid.uuid4())
    resolution = resolve_selection_transition(
        transition_id=SelectionTransitionId.TRN_SEL_001,
        current_session_state=SessionState.ANALYSIS,
        session_challenge_id=challenge_id,
        question_challenge_id=challenge_id,
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_WRONG_SESSION_STATE"


def test_denies_a_question_from_a_different_challenge() -> None:
    """Mandatory-category adversarial attack: wrong Workspace/Challenge
    -- here in its "different Challenge" shape (TRN-SEL-001 DENY
    CONDITION: "Question belongs to another Workspace/Challenge").
    """
    context = _context()
    resolution = resolve_selection_transition(
        transition_id=SelectionTransitionId.TRN_SEL_002,
        current_session_state=SessionState.QUESTION_SELECTION,
        session_challenge_id=ChallengeId(uuid.uuid4()),
        question_challenge_id=ChallengeId(uuid.uuid4()),
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_QUESTION_WRONG_CHALLENGE"


def test_allows_a_legal_decision_transition() -> None:
    """PKG-15: unlike PKG-14's QuestionSelection, Decision has genuine
    `from_state != to_state` pairs -- proven with a real
    `DecisionTransitionResolution`, not a stub.
    """
    context = _context()
    resolution = resolve_decision_transition_to_state(
        current_state=None, target_state=DecisionState.UNDER_CONSIDERATION
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_an_illegal_decision_transition() -> None:
    context = _context()
    resolution = resolve_decision_transition_to_state(
        current_state=DecisionState.DECIDED, target_state=DecisionState.UNDER_CONSIDERATION
    )
    evaluator = Bnd007StateTransitionEvaluator()
    boundary_input = Bnd007Input(
        boundary_id=BoundaryId.BND_007, context=context, resolution=resolution
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY


def test_rejects_a_resolution_of_the_wrong_type() -> None:
    """Structural proof: a caller cannot smuggle an arbitrary object in
    as a "resolution".
    """
    context = _context()
    with pytest.raises(TypeError, match="must be a SessionTransitionResolution"):
        Bnd007Input(boundary_id=BoundaryId.BND_007, context=context, resolution="ALLOW")  # type: ignore[arg-type]
