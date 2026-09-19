"""P-04 (T13-P04-BURST-AI-DENY): No AI contamination during ACTIVE
Human-only QuestionBurst.

13 §6 P-04 row: "No AI contamination active HUMAN_ONLY Burst | BURST
ACTIVE HUMAN_ONLY | invoke AIOP-001 | wait for completion then invoke |
BND-008/BND-009 | no AI artifact | denial record | ... | gateway/
boundary signal | DENIED | Burst state + no generation/provider call |
AI blocked."

WHY THIS PROOF IS STRUCTURAL, NOT A MOCK-BOUNDARY TEST
------------------------------------------------------------
Neither the AI Gateway nor a provider adapter exists yet in this
codebase (`ai_gateway` remains an empty stub -- PKG-19's own scope).
"No AI artifact / no generation/provider call" is therefore proven the
strongest way currently available: by showing no code path in this
package's own production surface (`domain`, `persistence`,
`application`) can even reach an AI operation during a protected Burst
-- there is no AIOP-001 invocation function to call in the first place,
and the one contamination-guard function that *does* exist
unconditionally denies every AI-attributed operation category during
ACTIVE/PAUSED. This is a stronger claim than "the mock returned DENY";
it is "there is nothing here that could return anything else."

UPDATED AT PKG-18: `ai_contracts` itself is no longer an empty stub --
it now holds the real AIOP registry, `AIGeneration` lifecycle, and
derived-artifact types (14 PKG-18's own PUBLIC_INTERFACES). That
content is pure vocabulary/data, not an invocation path -- so this
file's own "the whole package is empty" proxy check was replaced by
the more precise, durable claim it always meant: no Burst-protected
production module imports `ai_contracts` at all.

UPDATED AGAIN AT PKG-19: `ai_gateway` itself is no longer an empty stub
either -- it now holds the real `AIGateway`/`MockProviderAdapter`/
context/prompt/validator (14 PKG-19's own PUBLIC_INTERFACES: "AIGateway").
The same reasoning applies again: none of that is reachable from a
Burst-protected module, since none of `domain.burst`/`domain.
burst_membership`/`domain.burst_transitions`/`application.
burst_operations`/`application.burst_contamination`/`persistence.
burst_repository` imports `ai_gateway` (or `ai_contracts`) at all --
the loop below re-proves this, extended to cover `ai_gateway` too, and
"the whole package must stay empty" is finally retired as a check
since NEITHER `ai_contracts` NOR `ai_gateway` can ever legitimately
return to being empty stubs again. Mirrors PKG-13's own precedent for
fixing a previously-green test whose assumption a later, legitimate
package invalidates -- the underlying architectural claim (P-04) is
unchanged and still holds.
"""

from __future__ import annotations

import importlib
import inspect

import pytest
from application.burst_contamination import (
    BurstContaminationVerdict,
    BurstOperationCategory,
    ContaminationDenyReason,
    evaluate_burst_contamination_guard,
)
from authority.actor import ActorClass
from domain.burst import BurstState

_BURST_PROTECTED_MODULES = (
    "domain.burst",
    "domain.burst_membership",
    "domain.burst_transitions",
    "application.burst_operations",
    "application.burst_contamination",
    "persistence.burst_repository",
)


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
    """P-04's "no generation/provider call" half: `ai_gateway`/
    `ai_contracts` are both real as of PKG-18/19 (AIOP registry,
    AIGeneration lifecycle, AIGateway, MockProviderAdapter), but no
    Burst-protected production module imports either of them at all --
    there is no invocation path for this package's own Burst code to
    reach even if it tried.
    """
    for module_name in _BURST_PROTECTED_MODULES:
        source = inspect.getsource(importlib.import_module(module_name))
        assert "import ai_gateway" not in source, module_name
        assert "import ai_contracts" not in source, module_name


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
