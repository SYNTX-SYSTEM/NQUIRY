"""BND-007 SESSION / STATE TRANSITION BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §13. "Enforce the 03 state
topology, current-state requirements, legal transition path and
transition preconditions... AUTHORITY REQUIREMENT: 04 authority
requirement already satisfied or deferred to BND-005/BND-006. BND-007
does not invent authority."

WHY THIS EVALUATOR CONSUMES A RESOLUTION RATHER THAN COMPUTING ONE
------------------------------------------------------------------------
14 §18 (STATE TRANSITION ENGINE): "Transition rules are centralized
registry entries, not controller conditionals." Those registries
already exist and are already the authoritative source of truth --
`domain.session_transitions.resolve_session_transition_to_state` (PKG-05)
and `domain.burst_transitions.resolve_burst_transition_to_state` (PKG-07).
06 §13's own VALIDATION list ("current state exact, requested transition
legal, no state skip, ...") is *exactly* what those two functions
already compute. Re-implementing that logic a third time here -- or
worse, approximating it -- would be exactly "DO NOT SUBSTITUTE FRAMEWORK
CONVENTION FOR SOURCE SEMANTICS" (14 PKG-09 FORBIDDEN_SHORTCUTS) applied
to this package's own predecessor. This evaluator's only job is the one
06 §13 actually assigns a *boundary* (as opposed to the domain
registry): translate an already-computed domain verdict into the
boundary algebra, and make it reconstructable as a `BoundaryProof`.

This evaluator handles Session (PKG-05), QuestionBurst (PKG-07) and
QuestionSelection (PKG-14) transitions through one small tagged union
(`Bnd007Input.resolution`), rather than being split into separate
evaluators -- 06 §13's own title, "SESSION / STATE TRANSITION", and its
generic "BOUNDARY SUBJECT: State-owning object/process" wording, treat
state-topology enforcement as one boundary regardless of which
03-defined state machine is involved; `BoundaryId` has no separate ID
for "Burst state transition" or "Selection state-preserving mutation"
distinct from BND-008's own, narrower contamination concern.

PKG-14 EXTENSION: `SelectionTransitionResolution`
------------------------------------------------------------
06 §13's own REQUESTED OPERATION line reads "One specific 03 transition
or state-preserving consequential mutation" (transcribed verbatim) --
`domain.question_selection.resolve_selection_transition` materializes
exactly the second half of that disjunction (03 §39: "QuestionSelection
is a relation, not a state... Creating it is consequential"). Adding it
as a third tagged-union member is not a new boundary and not new
authority; it is the same translation this evaluator already performs
for the other two state machines, extended to a third one this
boundary's own purpose statement already covers.

PKG-15 EXTENSION: `DecisionTransitionResolution`
------------------------------------------------------------
Unlike PKG-14's Decision is a genuine `CANONICAL_DOMAIN_OBJECT` (02
§26.1), not a relation, with real `from_state != to_state` pairs (03
§36 TRN-DEC-001/002: absent -> UNDER_CONSIDERATION -> DECIDED) --
squarely the *first* half of 06 §13's own disjunction, the same shape
`SessionTransitionResolution`/`BurstTransitionResolution` already use.
Adding it as a fourth tagged-union member is, again, not a new
boundary: 06 §13's own generic "BOUNDARY SUBJECT: State-owning
object/process" wording already covers Decision as one more
03-defined state machine.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.burst_transitions import BurstTransitionResolution, BurstTransitionVerdict
from domain.decision import DecisionTransitionResolution, DecisionTransitionVerdict
from domain.question_selection import SelectionTransitionResolution, SelectionTransitionVerdict
from domain.session_transitions import SessionTransitionResolution, SessionTransitionVerdict
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult

_RESOLUTION_TYPES = (
    SessionTransitionResolution,
    BurstTransitionResolution,
    SelectionTransitionResolution,
    DecisionTransitionResolution,
)

_AnyResolution = (
    SessionTransitionResolution
    | BurstTransitionResolution
    | SelectionTransitionResolution
    | DecisionTransitionResolution
)

_AnyVerdict = (
    SessionTransitionVerdict
    | BurstTransitionVerdict
    | SelectionTransitionVerdict
    | DecisionTransitionVerdict
)


@dataclass(frozen=True, slots=True)
class Bnd007Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    resolution: _AnyResolution

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_007:
            raise ValueError(f"Bnd007Input.boundary_id must be BND_007, got {self.boundary_id}")
        if not isinstance(self.resolution, _RESOLUTION_TYPES):
            raise TypeError(
                "Bnd007Input.resolution must be a SessionTransitionResolution, "
                "BurstTransitionResolution, SelectionTransitionResolution or "
                f"DecisionTransitionResolution, got {type(self.resolution)!r}"
            )


class Bnd007StateTransitionEvaluator:
    boundary_id = BoundaryId.BND_007
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: Bnd007Input, context: BoundaryContext) -> BoundaryProof:
        resolution = boundary_input.resolution
        verdict: _AnyVerdict = resolution.verdict
        result = BoundaryResult.ALLOW if resolution.is_state_eligible else BoundaryResult.DENY
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=result,
            reason_code=verdict.value,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(resolution.requested,),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd007Input", "Bnd007StateTransitionEvaluator"]
