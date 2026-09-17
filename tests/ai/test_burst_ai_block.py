"""P-04 (T13-P04-BURST-AI-DENY): No AI contamination during ACTIVE
Human-only QuestionBurst.

13 §6 P-04 row: "No AI contamination active HUMAN_ONLY Burst | BURST
ACTIVE HUMAN_ONLY | invoke AIOP-001 | wait for completion then invoke |
BND-008/BND-009 | no AI artifact | denial record | ... | gateway/
boundary signal | DENIED | Burst state + no generation/provider call |
AI blocked."

WHY THIS PROOF IS STRUCTURAL, NOT A MOCK-BOUNDARY TEST
------------------------------------------------------------
Neither the AI Gateway, `AIGeneration` persistence, nor a provider
adapter exists yet in this codebase (all Phase 3+/PKG-08+ scope). "No
AI artifact / no generation/provider call" is therefore proven the
strongest way currently available: by showing no code path in this
package's own production surface (`domain`, `persistence`,
`application`) can even reach an AI operation during a protected Burst
-- there is no AIOP-001 invocation function to call in the first place,
and the one contamination-guard function that *does* exist
unconditionally denies every AI-attributed operation category during
ACTIVE/PAUSED. This is a stronger claim than "the mock returned DENY";
it is "there is nothing here that could return anything else."
"""

from __future__ import annotations

import pytest
from application.burst_contamination import (
    BurstContaminationVerdict,
    BurstOperationCategory,
    ContaminationDenyReason,
    evaluate_burst_contamination_guard,
)
from authority.actor import ActorClass
from domain.burst import BurstState


def test_ai_analysis_during_active_human_only_burst_is_denied() -> None:
    """Mandatory adversarial attack: AI invocation ACTIVE. Direct
    proof for P-04's own named scenario (AIOP-001 QUESTION_ANALYSIS).
    """
    result = evaluate_burst_contamination_guard(
        burst_state=BurstState.ACTIVE,
        operation=BurstOperationCategory.AI_ANALYSIS,
        actor_class=ActorClass.AI_PROCESSOR,
    )

    assert result.verdict is BurstContaminationVerdict.DENY
    assert result.reason is ContaminationDenyReason.AI_OPERATION_DURING_PROTECTED_BURST


def test_no_ai_gateway_or_provider_module_is_reachable_from_this_package() -> None:
    """P-04's "no generation/provider call" half: there is no AI
    Gateway, provider adapter, or `AIGeneration` persistence module
    that this package's Burst code could call even if it tried --
    those packages remain empty stubs (Phase 3+/PKG-08+).
    """
    import ai_contracts
    import ai_gateway

    assert not [name for name in vars(ai_contracts) if not name.startswith("_")]
    assert not [name for name in vars(ai_gateway) if not name.startswith("_")]


def test_burst_repository_has_no_ai_generation_method() -> None:
    """Structural proof: `BurstRepository`'s public surface has no
    method that could invoke, record, or reference an AI generation --
    the mandatory attack "AI invocation ACTIVE" has no method to call
    even before the contamination guard would deny it.
    """
    from persistence.burst_repository import SqlAlchemyBurstRepository

    ai_shaped = [
        name
        for name in dir(SqlAlchemyBurstRepository)
        if not name.startswith("_") and ("ai" in name.lower() or "generat" in name.lower())
    ]
    assert ai_shaped == []


def test_application_burst_operations_never_imports_a_provider_sdk() -> None:
    """`packages/application/burst_operations.py` and
    `packages/application/burst_contamination.py` must not import any
    AI provider SDK -- proven by re-running the real
    `check_provider_sdk_imports` checker, not a re-implementation.
    """
    from check_provider_sdk_imports import check

    violations = check()
    assert violations == [], "\n".join(str(v) for v in violations)


@pytest.mark.parametrize(
    "operation",
    [
        BurstOperationCategory.AI_REFRAME,
        BurstOperationCategory.AI_CLASSIFY,
        BurstOperationCategory.AI_CLUSTER,
        BurstOperationCategory.AI_QUESTION_GENERATION,
    ],
)
def test_every_ai_operation_category_is_denied_during_active(
    operation: BurstOperationCategory,
) -> None:
    """06 §14 DENY, "During ACTIVE protected Human-only Burst":
    reframing, classification, clustering, AI question generation --
    proven individually, not merely as one aggregate case.
    """
    result = evaluate_burst_contamination_guard(
        burst_state=BurstState.ACTIVE, operation=operation, actor_class=ActorClass.AI_PROCESSOR
    )

    assert result.verdict is BurstContaminationVerdict.DENY
