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
from domain.session import SessionState
from domain.session_transitions import resolve_session_transition_to_state
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

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


def test_rejects_a_resolution_of_the_wrong_type() -> None:
    """Structural proof: a caller cannot smuggle an arbitrary object in
    as a "resolution".
    """
    context = _context()
    with pytest.raises(TypeError, match="must be a SessionTransitionResolution"):
        Bnd007Input(boundary_id=BoundaryId.BND_007, context=context, resolution="ALLOW")  # type: ignore[arg-type]
