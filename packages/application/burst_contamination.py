"""BND-008 facts: the AI-exclusion testable invariant, prepared as data.

Source: 06_BOUNDARY_ARCHITECTURE.md §14 (BND-008 QUESTION BURST
CONTAMINATION BOUNDARY).

WHAT THIS MODULE IS
--------------------
14 PKG-07's own coding prompt is explicit: "BOUNDARIES: Prepare BND-008
facts" -- not "implement BND-008". The full boundary is a 06 §14
evaluator with IDENTITY/SCOPE/AUTHORITY/EVIDENCE requirements, ALLOW/
DENY/REQUIRE/ESCALATE outcomes, a `BoundaryEvaluationRecord` (14 §7.1),
and convergence with BND-009/BND-010/BND-014/BND-018 -- none of which
exists yet (the boundary engine is PKG-08's "Boundary engine core").
`packages/boundaries` itself is not in this package's
`FILES_ALLOWED_TO_CREATE` list at all -- only `packages/domain burst`
and `packages/application burst operations` are authorized production
directories, which is also why this module lives here rather than
under `packages/domain`: it needs `authority.actor.ActorClass`, and
`domain`'s only permitted dependency is `semantic_types` (14 §3.1) --
`application` is the lowest layer in this package's authorized scope
that may depend on both `domain` and `authority`.

What this module materializes is exactly one thing 06 §14 states
plainly enough to test without inventing anything: the "TESTABLE
INVARIANT" itself --

    "No AI analysis/evaluation/reframe/generation can affect the
    protected raw Human-only Burst before valid completion and freeze."

`evaluate_burst_contamination_guard` is a pure function computing that
one fact from real domain state (`BurstState`, `ActorClass`, an
operation category drawn from 06 §14's own named list). It returns
only `ALLOW`/`DENY` -- 06 §14's fuller `REQUIRE`/`ESCALATE` outcomes
are not modeled, because nothing in this package's scope has a
resolved condition that would produce them (`REQUIRE` fires only when
"BURST_INPUT_VALID cannot be established by a source-compatible
mechanism", which is `GAP-03-003`, `[UNDERDEFINED]`; `ESCALATE` needs
"authorized methodology governance" this package does not implement).
A future BND-008 evaluator (PKG-08) is expected to call this function
as one input among several, not to be replaced by it.

WHY POST-COMPLETED AI OPERATIONS RETURN `ALLOW` HERE
------------------------------------------------------
06 §14 ALLOW: "After COMPLETED/frozen: post-Burst AI analysis may
become eligible ... subject to BND-009/BND-010." This function only
answers the contamination question (was the raw set protected at the
time); it does not and cannot answer whether BND-009 (AI Invocation)
or BND-010 (AI Output/Canonical State) would also allow the same
request -- those boundaries do not exist yet either. `ALLOW` from this
function is therefore explicitly a *necessary, not sufficient*
verdict, exactly like `session_transitions.SessionTransitionVerdict.STATE_ELIGIBLE`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from authority.actor import ActorClass
from domain.burst import PROTECTED_BURST_STATES, BurstState


class BurstOperationCategory(Enum):
    """06 §14's own "REQUESTED OPERATION" examples, restricted to the
    categories this function's single testable invariant actually
    distinguishes: capture (human-submitted, always legitimate for a
    `HUMAN_USER` actor while ACTIVE) versus the four AI operation
    categories 06 §14 names as denied during protected states
    (`REFRAME`/`CLASSIFY`/`CLUSTER`/`GENERATE_QUESTION`, plus
    `AI_ANALYSIS` for the analysis/evaluation case), plus the Burst
    lifecycle operations themselves (start/pause/resume/complete),
    which this function always allows for a `HUMAN_USER` or
    `SYSTEM_SERVICE` actor and always denies for `AI_PROCESSOR` (04
    §35-39's "AI PROHIBITED ROLE" throughout: "may not start/pause/
    resume/complete Burst").
    """

    CAPTURE_BURST_QUESTION = "CAPTURE_BURST_QUESTION"
    AI_ANALYSIS = "AI_ANALYSIS"
    AI_REFRAME = "AI_REFRAME"
    AI_CLASSIFY = "AI_CLASSIFY"
    AI_CLUSTER = "AI_CLUSTER"
    AI_QUESTION_GENERATION = "AI_QUESTION_GENERATION"
    PREPARE_BURST = "PREPARE_BURST"
    START_BURST = "START_BURST"
    PAUSE_BURST = "PAUSE_BURST"
    RESUME_BURST = "RESUME_BURST"
    COMPLETE_BURST = "COMPLETE_BURST"


_AI_ONLY_OPERATIONS = frozenset(
    {
        BurstOperationCategory.AI_ANALYSIS,
        BurstOperationCategory.AI_REFRAME,
        BurstOperationCategory.AI_CLASSIFY,
        BurstOperationCategory.AI_CLUSTER,
        BurstOperationCategory.AI_QUESTION_GENERATION,
    }
)
"""06 §14 DENY, "During ACTIVE protected Human-only Burst": answer
generation, explanation generation, question evaluation,
classification, clustering, reframing, AI question generation -- the
subset of that list expressible as one of this module's operation
categories (answer/explanation generation are not Burst operation
categories at all in this vocabulary; they are rejected upstream by
`GAP-03-003`'s still-unresolved `BURST_INPUT_VALID` predicate, not by
this function).
"""

_LIFECYCLE_OPERATIONS = frozenset(
    {
        BurstOperationCategory.PREPARE_BURST,
        BurstOperationCategory.START_BURST,
        BurstOperationCategory.PAUSE_BURST,
        BurstOperationCategory.RESUME_BURST,
        BurstOperationCategory.COMPLETE_BURST,
    }
)


class BurstContaminationVerdict(Enum):
    """06 §14's ALLOW/DENY outcomes only -- see module docstring for
    why REQUIRE/ESCALATE are not modeled here.
    """

    ALLOW = "ALLOW"
    DENY = "DENY"


class ContaminationDenyReason(Enum):
    """Closed reason vocabulary, each tied to a specific 06 §14 DENY
    line or 04 §35-39 AI-PROHIBITED-ROLE statement."""

    AI_OPERATION_DURING_PROTECTED_BURST = "AI_OPERATION_DURING_PROTECTED_BURST"
    AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE = "AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE"


@dataclass(frozen=True, slots=True)
class BurstContaminationResult:
    verdict: BurstContaminationVerdict
    reason: ContaminationDenyReason | None
    burst_state: BurstState
    operation: BurstOperationCategory
    actor_class: ActorClass


def evaluate_burst_contamination_guard(
    *, burst_state: BurstState, operation: BurstOperationCategory, actor_class: ActorClass
) -> BurstContaminationResult:
    """06 §14's testable invariant, computed from real domain state.

    Not authority, not a boundary evaluation, not a commit: a
    necessary fact a future BND-008 (and, for AI operations, BND-009)
    must additionally pass before any consequence occurs.
    """

    def result(
        verdict: BurstContaminationVerdict, reason: ContaminationDenyReason | None
    ) -> BurstContaminationResult:
        return BurstContaminationResult(
            verdict=verdict,
            reason=reason,
            burst_state=burst_state,
            operation=operation,
            actor_class=actor_class,
        )

    if actor_class is ActorClass.AI_PROCESSOR:
        if operation in _AI_ONLY_OPERATIONS and burst_state in PROTECTED_BURST_STATES:
            # Mandatory adversarial attack: AI invocation ACTIVE (and,
            # per 03 section 19.4, PAUSED -- protection does not lapse
            # merely because input is suspended).
            return result(
                BurstContaminationVerdict.DENY,
                ContaminationDenyReason.AI_OPERATION_DURING_PROTECTED_BURST,
            )
        if operation in _LIFECYCLE_OPERATIONS:
            # 04 section 35-39: "AI PROHIBITED ROLE: May not
            # start/pause/resume/complete Burst" -- unconditional, not
            # state-dependent.
            return result(
                BurstContaminationVerdict.DENY,
                ContaminationDenyReason.AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE,
            )

    return result(BurstContaminationVerdict.ALLOW, None)


__all__ = [
    "BurstOperationCategory",
    "BurstContaminationVerdict",
    "ContaminationDenyReason",
    "BurstContaminationResult",
    "evaluate_burst_contamination_guard",
]
