"""BND-006 HUMAN DECISION AUTHORITY BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §12. "Ensure a required human
decision is actually created by the correct authorized human, rather
than inferred from AI output, approval UI, persistence or workflow
progression."

WHY THIS EVALUATOR DOES NOT RE-CHECK AUTHORITY ITSELF
----------------------------------------------------------
06 §12's own AUTHORITY REQUIREMENT is "BND-005 ALLOW for the relevant
human decision right", and its own NEXT PERMITTED PATH places BND-006
*after* BND-005 in the canonical chain (06 §4). `evaluate_chain`
(PKG-08) only reaches BND-006 at all if BND-005 already returned
`ALLOW` for the same request -- re-deriving that same authority check
here would duplicate BND-005's own proof rather than adding the
*distinct* fact 06 §12 actually assigns this boundary: whether the
decision's content itself was genuinely authored or adopted by an
authenticated human, as opposed to being AI output nodded through.
Those are different questions (an actor can hold `DECISION_RIGHT`
perfectly validly while a *specific* decision payload was nonetheless
synthesized from a model) -- collapsing them into one check would be
exactly the "compress to one authorization function" 14 PKG-09 forbids.

TESTABLE INVARIANT (06 §12, transcribed): "No AI output can cross
BND-006 as an authority-bearing human decision." No `Decision` domain
object or persistence exists yet (PKG-14+); this evaluator proves the
one fact honestly available now -- the *origin* asserted for the
decision content -- and refuses unconditionally whenever that origin is
not `HUMAN_USER`, regardless of what authority the requesting actor
otherwise holds.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd006Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    decision_origin: ActorClass
    """Which actor class actually produced the decision's content --
    supplied by the caller from whatever recorded the decision (a
    future `Decision`/`QuestionSelection` construction). Distinct from
    `context.actor`, which is who is *requesting* this operation --
    06 §12 REQUESTING ACTOR ("HUMAN_USER for decision creation") is
    checked against `context.actor` here; `decision_origin` is checked
    against the content-authorship rule separately, because a human
    actor could still be attempting to submit AI-authored content as
    their own decision (06 PROHIBITED PATH: "AI decides -> human
    approves as generic token").
    """

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_006:
            raise ValueError(f"Bnd006Input.boundary_id must be BND_006, got {self.boundary_id}")


class Bnd006HumanDecisionEvaluator:
    boundary_id = BoundaryId.BND_006
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: Bnd006Input, context: BoundaryContext) -> BoundaryProof:
        def result_proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(boundary_input.decision_origin.value,),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # 06 §12 REQUESTING ACTOR: "HUMAN_USER for decision creation."
        if context.actor.actor_class is not ActorClass.HUMAN_USER:
            return result_proof(BoundaryResult.DENY, "DECISION_CREATION_REQUIRES_HUMAN_REQUESTER")

        # Mandatory-category adversarial attack: missing human Decision
        # -- here in its "content is AI-authored" shape, 06's own
        # named DENY examples ("AI selected the option", "AI generated
        # the selection and system auto-accepted it").
        if boundary_input.decision_origin is not ActorClass.HUMAN_USER:
            return result_proof(
                BoundaryResult.DENY,
                f"DECISION_CONTENT_NOT_HUMAN_ORIGIN:{boundary_input.decision_origin.value}",
            )

        return result_proof(BoundaryResult.ALLOW, "HUMAN_AUTHORED_DECISION_PROVEN")


__all__ = ["Bnd006Input", "Bnd006HumanDecisionEvaluator"]
