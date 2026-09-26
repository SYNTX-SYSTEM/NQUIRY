"""BND-008 QUESTION BURST CONTAMINATION BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §14. Testable invariant, quoted
verbatim: "No AI analysis/evaluation/reframe/generation can affect the
protected raw Human-only Burst before valid completion and freeze. No
Question accepted into the raw set can have original_text silently
rewritten."

WHY THIS DUPLICATES `application.burst_contamination`'S LOGIC INSTEAD
OF IMPORTING IT
------------------------------------------------------------------------
PKG-07 already built `application.burst_contamination.evaluate_burst_contamination_guard`,
explicitly as a "prepare BND-008 facts" placeholder anticipating this
real evaluator. It cannot be imported here: `application` depends on
`boundaries` (14 §3.1), not the reverse, and `boundaries` importing
`application` at all would both invert that arrow and create a literal
import cycle. `packages/boundaries` is also not the file PKG-07 could
have put this in either -- it needs `authority.actor.ActorClass`, and
at the time PKG-07 ran, `packages/boundaries` had no evaluator files at
all yet (PKG-08, the generic engine, came after).

This module is therefore a second, independent implementation of 06
§14's *same* one testable invariant -- not a second, competing
interpretation of it (the two implementations are cross-checked
against each other, exhaustively, by
`tests/boundaries/test_bnd_008_agrees_with_application_guard.py`, which
fails immediately if they ever diverge on any input combination). This
is the disclosed resolution recorded in this package's own
`PRE_IMPLEMENTATION_TRACE`; consolidating the two into one shared
location is left to whichever future package restructures the
`application`/`boundaries` dependency direction, since doing so here
would exceed this package's own scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from authority.actor import ActorClass
from domain.burst import PROTECTED_BURST_STATES, BurstState
from domain.burst_input import BurstInputCheck
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


class Bnd008OperationCategory(Enum):
    """06 §14's own named operation categories, restricted to the ones
    this boundary's testable invariant actually distinguishes -- see
    `application.burst_contamination.BurstOperationCategory`'s
    identical docstring reasoning (independently re-derived from the
    same 06 §14 text, not copied from that module).
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
        Bnd008OperationCategory.AI_ANALYSIS,
        Bnd008OperationCategory.AI_REFRAME,
        Bnd008OperationCategory.AI_CLASSIFY,
        Bnd008OperationCategory.AI_CLUSTER,
        Bnd008OperationCategory.AI_QUESTION_GENERATION,
    }
)

_LIFECYCLE_OPERATIONS = frozenset(
    {
        Bnd008OperationCategory.PREPARE_BURST,
        Bnd008OperationCategory.START_BURST,
        Bnd008OperationCategory.PAUSE_BURST,
        Bnd008OperationCategory.RESUME_BURST,
        Bnd008OperationCategory.COMPLETE_BURST,
    }
)


@dataclass(frozen=True, slots=True)
class Bnd008Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    burst_state: BurstState
    operation_category: Bnd008OperationCategory
    input_check: BurstInputCheck | None = None
    """F03 HD-12 (NQ-DEC-040): the BURST_INPUT_VALID fact for a capture,
    computed by `domain.burst_input.check_burst_input` over the exact submitted
    text. `None` means it has not been established."""

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_008:
            raise ValueError(f"Bnd008Input.boundary_id must be BND_008, got {self.boundary_id}")


class Bnd008QuestionBurstEvaluator:
    boundary_id = BoundaryId.BND_008
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: Bnd008Input, context: BoundaryContext) -> BoundaryProof:
        def result_proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(
                    boundary_input.burst_state.value,
                    boundary_input.operation_category.value,
                ),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        actor_class = context.actor.actor_class
        operation = boundary_input.operation_category
        burst_state = boundary_input.burst_state

        if operation is Bnd008OperationCategory.CAPTURE_BURST_QUESTION:
            # 06 §14 IDENTITY: "Human submission requires authenticated Session
            # Participant ... AI must remain AI_PROCESSOR." ALLOW lists only
            # "valid human Question capture".
            if actor_class is not ActorClass.HUMAN_USER:
                return result_proof(BoundaryResult.DENY, "CAPTURE_REQUIRES_HUMAN_ACTOR")
            check = boundary_input.input_check
            if check is None:
                # 06 §14 REQUIRE: BURST_INPUT_VALID cannot be established.
                return result_proof(BoundaryResult.REQUIRE, "BURST_INPUT_VALID_NOT_ESTABLISHED")
            if not check.valid:
                return result_proof(BoundaryResult.DENY, f"BURST_INPUT_INVALID:{check.reason_code}")
            return result_proof(BoundaryResult.ALLOW, "BURST_INPUT_VALID")

        if operation in _AI_ONLY_OPERATIONS and burst_state in PROTECTED_BURST_STATES:
            # Mandatory adversarial attack: ACTIVE Burst AI contamination (and
            # PAUSED, 03 section 19.4). F04 WU-04.2 (FBR-F04-3): 06 §14 denies
            # the AI OPERATION during the protected Burst, whoever requests it;
            # a human or system requester does not make it legal.
            return result_proof(BoundaryResult.DENY, "AI_OPERATION_DURING_PROTECTED_BURST")
        if actor_class is ActorClass.AI_PROCESSOR and operation in _LIFECYCLE_OPERATIONS:
            return result_proof(BoundaryResult.DENY, "AI_ACTOR_CANNOT_CONTROL_BURST_LIFECYCLE")

        return result_proof(BoundaryResult.ALLOW, "NO_CONTAMINATION_DETECTED")


__all__ = ["Bnd008OperationCategory", "Bnd008Input", "Bnd008QuestionBurstEvaluator"]
