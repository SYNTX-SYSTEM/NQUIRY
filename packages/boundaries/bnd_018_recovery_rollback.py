"""BND-018 RECOVERY / ROLLBACK BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 25 (full spec: PURPOSE
"Ensure recovery restores or reconciles only architecture-valid state
and cannot bypass normal authority, scope, immutability or audit
semantics"; REQUESTING ACTOR "SYSTEM_SERVICE for deterministic
reconciliation. HUMAN_USER only where 10 later defines a discretionary
recovery decision with valid authority"; AUTHORITY REQUIREMENT
"Recovery cannot invent a new domain decision. Deterministic
reconciliation may use bounded SYSTEM_DERIVED recovery authority only
if 10 can prove it is restoring a state already legitimized by the
original operation. Any discretionary new decision requires the normal
04 authority path"; VALIDATION list -- the exact 8 invariants; DENY
list; TESTABLE INVARIANT "Recovery can never produce a state that
could not have been validly reached or legitimately restored under
00-06.").

WHY THE SYSTEM_SERVICE BRANCH CHECKS `restores_already_legitimized_state`
INSTEAD OF CALLING `AuthorityResolver`
--------------------------------------------------------------------
`governance.authority_binding.AuthorityClass`'s own 7 values are all
HUMAN Decision Rights (04 §9) -- none represents 04 §563's own
"SYSTEM_DERIVED" authority category a deterministic recovery actor
would need, and no BND-011 (SYSTEM_DERIVED AUTHORITY BOUNDARY)
evaluator exists in this codebase to resolve one. Calling
`AuthorityResolver.resolve()` with any of the 7 human-shaped classes
for a SYSTEM_SERVICE actor would itself BE "recovery inherits human
authority" -- exactly the P-21 violation this boundary exists to
prevent. `restores_already_legitimized_state` is this evaluator's own
honest materialization of AC-10-005 ("if 10 can prove it is restoring
a state already legitimized by the original operation"): a caller-
supplied, already-verified fact (typically: LPVS resolved to a state
that WAS the target's own last legitimate canonical state), never a
fresh authority grant.

WHY THE HUMAN_USER BRANCH IS DISCLOSED, NOT WIRED TO A REAL
`AuthorityResolver` CALL EITHER
--------------------------------------------------------------------
06 §25 itself hedges this branch ("HUMAN_USER only where 10 LATER
defines a discretionary recovery decision") -- 10 itself defines RC-07
(Manual/Discretionary Recovery) only as a set of EXAMPLES requiring
"domain judgment", with no concrete AuthorityClass/right named for it
anywhere in 04. `current_human_authority_confirmed` is therefore the
same caller-supplied-fact pattern, disclosed as `SUCCESSOR_NOT_BUILT`
in this package's own completion report -- this prototype's own
MINIMUM scope (12_MINIMUM_PROTOTYPE_ARCHITECTURE.md) never exercises
this branch.

WHY AI_PROCESSOR IS DENIED FIRST, UNCONDITIONALLY
--------------------------------------------------------------------
06 §25's own PROHIBITED PATH names "AI chooses recovery outcome"
explicitly. Mirrors `Bnd009AiInvocationEvaluator`'s own "AI self-
invocation" unconditional-first-check precedent (PKG-19).
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass
from recovery.models import RecoveryClass
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult

_VALIDATION_INVARIANTS = (
    "workspace_scope_preserved",
    "question_immutability_preserved",
    "raw_burst_integrity_preserved",
    "human_ai_distinction_preserved",
    "authority_history_preserved",
    "audit_reconstruction_preserved",
    "no_duplicate_consequence",
)


@dataclass(frozen=True, slots=True)
class Bnd018Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    recovery_class: RecoveryClass
    lpvs_resolved: bool
    restores_already_legitimized_state: bool
    current_human_authority_confirmed: bool
    workspace_scope_preserved: bool
    question_immutability_preserved: bool
    raw_burst_integrity_preserved: bool
    human_ai_distinction_preserved: bool
    authority_history_preserved: bool
    audit_reconstruction_preserved: bool
    no_duplicate_consequence: bool

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_018:
            raise ValueError(f"Bnd018Input.boundary_id must be BND_018, got {self.boundary_id}")
        if not isinstance(self.recovery_class, RecoveryClass):
            raise TypeError(
                f"recovery_class must be a RecoveryClass, got {type(self.recovery_class)!r}"
            )


class Bnd018RecoveryRollbackEvaluator:
    boundary_id = BoundaryId.BND_018
    boundary_version = ContractVersion("1.0")

    def evaluate(self, boundary_input: Bnd018Input, context: BoundaryContext) -> BoundaryProof:
        def result_proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # TESTABLE INVARIANT: recovery can never produce a state that
        # was not proven legitimate. Checked first -- nothing else
        # matters if there is no proven state to recover to at all.
        if not boundary_input.lpvs_resolved:
            return result_proof(BoundaryResult.DENY, "NO_PROVEN_LEGITIMATE_STATE_TO_RECOVER_TO")

        # 06 §25 PROHIBITED PATH: "AI chooses recovery outcome."
        if context.actor.actor_class is ActorClass.AI_PROCESSOR:
            return result_proof(BoundaryResult.DENY, "AI_CANNOT_CHOOSE_RECOVERY_OUTCOME")

        if context.actor.actor_class is ActorClass.HUMAN_USER:
            if not boundary_input.current_human_authority_confirmed:
                return result_proof(
                    BoundaryResult.DENY,
                    "DISCRETIONARY_RECOVERY_REQUIRES_CURRENT_HUMAN_AUTHORITY",
                )
        else:
            # SYSTEM_SERVICE / EXTERNAL_SYSTEM: the deterministic path.
            if not boundary_input.restores_already_legitimized_state:
                return result_proof(
                    BoundaryResult.DENY,
                    "DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE",
                )

        violated = tuple(
            name for name in _VALIDATION_INVARIANTS if not getattr(boundary_input, name)
        )
        if violated:
            return result_proof(
                BoundaryResult.DENY, f"RECOVERY_VALIDATION_INVARIANT_VIOLATED:{','.join(violated)}"
            )

        return result_proof(BoundaryResult.ALLOW, "RECOVERY_PERMITTED")


__all__ = ["Bnd018Input", "Bnd018RecoveryRollbackEvaluator"]
