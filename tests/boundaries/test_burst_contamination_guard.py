"""T4 BOUNDARY TEST: `application.burst_contamination`'s BND-008 facts.

13 §6 T4 scope: "Boundary convergence and monotonic restriction ...
DENY/REQUIRE/ESCALATE/ALLOW as approved." Pure Python: this module
computes 06 §14's one testable invariant as a pure function -- no
database, no boundary engine (PKG-08).
"""

from __future__ import annotations

from application.burst_contamination import (
    BurstContaminationVerdict,
    BurstOperationCategory,
    ContaminationDenyReason,
    evaluate_burst_contamination_guard,
)
from authority.actor import ActorClass
from domain.burst import BurstState

_AI_OPERATIONS = (
    BurstOperationCategory.AI_ANALYSIS,
    BurstOperationCategory.AI_REFRAME,
    BurstOperationCategory.AI_CLASSIFY,
    BurstOperationCategory.AI_CLUSTER,
    BurstOperationCategory.AI_QUESTION_GENERATION,
)

_LIFECYCLE_OPERATIONS = (
    BurstOperationCategory.PREPARE_BURST,
    BurstOperationCategory.START_BURST,
    BurstOperationCategory.PAUSE_BURST,
    BurstOperationCategory.RESUME_BURST,
    BurstOperationCategory.COMPLETE_BURST,
)


def test_ai_operation_during_active_is_denied() -> None:
    """Mandatory adversarial attack: AI invocation ACTIVE."""
    for operation in _AI_OPERATIONS:
        result = evaluate_burst_contamination_guard(
            burst_state=BurstState.ACTIVE, operation=operation, actor_class=ActorClass.AI_PROCESSOR
        )
        assert result.verdict is BurstContaminationVerdict.DENY, f"{operation} must be denied"
        assert result.reason is ContaminationDenyReason.AI_OPERATION_DURING_PROTECTED_BURST


def test_ai_operation_during_paused_is_also_denied() -> None:
    """Novel attack: PAUSED-state AI invocation. 03 §19.4 describes
    PAUSED as "the same process" as ACTIVE with input merely
    suspended -- contamination protection does not lapse.
    """
    for operation in _AI_OPERATIONS:
        result = evaluate_burst_contamination_guard(
            burst_state=BurstState.PAUSED, operation=operation, actor_class=ActorClass.AI_PROCESSOR
        )
        assert result.verdict is BurstContaminationVerdict.DENY, f"{operation} must be denied"
        assert result.reason is ContaminationDenyReason.AI_OPERATION_DURING_PROTECTED_BURST


def test_ai_operation_before_active_or_after_completed_is_allowed_by_this_guard() -> None:
    """06 §14 ALLOW: "After COMPLETED/frozen: post-Burst AI analysis
    may become eligible... subject to BND-009/BND-010" -- this guard
    only answers the contamination question, disclosed explicitly as
    necessary-not-sufficient (BND-009/010 do not exist to gate the
    actual call).
    """
    for state in (BurstState.PREPARED, BurstState.COMPLETED):
        for operation in _AI_OPERATIONS:
            result = evaluate_burst_contamination_guard(
                burst_state=state, operation=operation, actor_class=ActorClass.AI_PROCESSOR
            )
            assert result.verdict is BurstContaminationVerdict.ALLOW, (
                f"{operation} at {state} should not be denied by the contamination guard"
            )
            assert result.reason is None


def test_ai_actor_cannot_control_burst_lifecycle_in_any_state() -> None:
    """04 §35-39: "AI PROHIBITED ROLE: May not start/pause/resume/
    complete Burst" -- unconditional, not state-dependent.
    """
    for state in BurstState:
        for operation in _LIFECYCLE_OPERATIONS:
            result = evaluate_burst_contamination_guard(
                burst_state=state, operation=operation, actor_class=ActorClass.AI_PROCESSOR
            )
            assert result.verdict is BurstContaminationVerdict.DENY, (
                f"AI must not control {operation} at {state}"
            )
            assert result.reason is ContaminationDenyReason.AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE


def test_human_capture_during_active_is_allowed() -> None:
    """Positive control: the guard must not be vacuously strict --
    legitimate human capture during ACTIVE is allowed.
    """
    result = evaluate_burst_contamination_guard(
        burst_state=BurstState.ACTIVE,
        operation=BurstOperationCategory.CAPTURE_BURST_QUESTION,
        actor_class=ActorClass.HUMAN_USER,
    )
    assert result.verdict is BurstContaminationVerdict.ALLOW
    assert result.reason is None


def test_human_actor_can_control_burst_lifecycle() -> None:
    """Positive control: a human actor is not blocked by the AI-only
    lifecycle rule.
    """
    for operation in _LIFECYCLE_OPERATIONS:
        result = evaluate_burst_contamination_guard(
            burst_state=BurstState.PREPARED, operation=operation, actor_class=ActorClass.HUMAN_USER
        )
        assert result.verdict is BurstContaminationVerdict.ALLOW


def test_system_service_can_control_burst_lifecycle() -> None:
    """Negative control on the AI-specific rule: `SYSTEM_SERVICE` is a
    distinct actor class from `AI_PROCESSOR` (04 §3) and is not
    rejected by this AI-specific guard -- authority evaluation (a
    separate concern) still applies elsewhere.
    """
    for operation in _LIFECYCLE_OPERATIONS:
        result = evaluate_burst_contamination_guard(
            burst_state=BurstState.PREPARED,
            operation=operation,
            actor_class=ActorClass.SYSTEM_SERVICE,
        )
        assert result.verdict is BurstContaminationVerdict.ALLOW


def test_result_records_the_inputs_it_was_evaluated_against() -> None:
    """Proof-artifact shape: the result carries enough to reconstruct
    what was checked, not just the verdict.
    """
    result = evaluate_burst_contamination_guard(
        burst_state=BurstState.ACTIVE,
        operation=BurstOperationCategory.AI_ANALYSIS,
        actor_class=ActorClass.AI_PROCESSOR,
    )
    assert result.burst_state is BurstState.ACTIVE
    assert result.operation is BurstOperationCategory.AI_ANALYSIS
    assert result.actor_class is ActorClass.AI_PROCESSOR
