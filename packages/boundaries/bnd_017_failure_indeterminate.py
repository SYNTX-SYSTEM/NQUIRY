"""BND-017 FAILURE / INDETERMINATE BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 24 (full spec: PURPOSE
"Contain uncertain or failed consequential operations so uncertainty
cannot create permission, duplicate consequence or downstream state";
ALLOW "known FAILED_PRECOMMIT -> safe re-request may be possible after
full boundary reevaluation; known COMMITTED -> do not repeat
consequence"; DENY "dependent consequential operation after
INDETERMINATE; blind retry when duplicate consequence is possible;
assume rollback without proof; assume commit without proof"; REQUIRE
"Recovery/reconciliation for INDETERMINATE"; TESTABLE INVARIANT "An
INDETERMINATE consequential operation blocks every dependent
consequence until reconciliation establishes the last valid state.").

WHY THIS EVALUATOR HOLDS A REAL `RecoveryRepository`
--------------------------------------------------------------------
06 section 24's own DENY line ("dependent consequential operation
after INDETERMINATE") cannot be honestly checked from a caller-supplied
boolean alone -- 06 section 8's own precedent for `Bnd002WorkspaceEvaluator`
already established that a claim ("this target is/isn't blocked") is
not SYSTEM_PROOF by itself. This evaluator therefore re-reads
`RecoveryRepository.is_target_blocked` fresh on every call, the same
"always current, never cached" discipline `Bnd002WorkspaceEvaluator`/
`Bnd003MembershipEvaluator` already established -- see
`scripts/check_architecture_dependencies.py`'s own `INTERNAL_ALLOWED["boundaries"]`
entry for the disclosed `boundaries -> recovery` extension this
requires.

WHY `requested_operation` STAYS A PLAIN STRING
--------------------------------------------------------------------
06 section 24's own REQUESTED OPERATION list is "Examples:" language
(retry / continue dependent workflow / assume commit / assume rollback
/ emit compensating mutation), never "defines"/"exact" closure --
formalizing it into a closed enum here would be inventing a vocabulary
06 itself never closes. This module recognizes a small, disclosed set
of literal values it can honestly reason about
(`"retry"`/`"reconcile"`/`"assume_commit"`/`"assume_rollback"`/
`"acknowledge_committed"`); any other string falls through to the same
fail-closed REQUIRE this module gives an unrecognized-but-uncertain
operation, never a guessed ALLOW.
"""

from __future__ import annotations

from dataclasses import dataclass

from recovery.certainty import ConsequenceCertainty
from recovery.models import RecoveryRepository
from semantic_types.ids import RecoveryId
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult

_RETRY_LIKE_OPERATIONS = frozenset({"retry", "continue_dependent_workflow"})
_ASSUMPTION_OPERATIONS = frozenset({"assume_commit", "assume_rollback"})


@dataclass(frozen=True, slots=True)
class Bnd017Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    requested_operation: str
    known_consequence_certainty: ConsequenceCertainty
    target_ref: str
    exclude_recovery_id: RecoveryId | None = None

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_017:
            raise ValueError(f"Bnd017Input.boundary_id must be BND_017, got {self.boundary_id}")
        if not self.requested_operation:
            raise ValueError("Bnd017Input.requested_operation must be non-empty")
        if not isinstance(self.known_consequence_certainty, ConsequenceCertainty):
            raise TypeError(
                "known_consequence_certainty must be a ConsequenceCertainty, got "
                f"{type(self.known_consequence_certainty)!r}"
            )
        if not self.target_ref:
            raise ValueError("Bnd017Input.target_ref must be non-empty")


class Bnd017FailureIndeterminateEvaluator:
    boundary_id = BoundaryId.BND_017
    boundary_version = ContractVersion("1.0")

    def __init__(self, recovery_repository: RecoveryRepository) -> None:
        self._recovery_repository = recovery_repository

    def evaluate(self, boundary_input: Bnd017Input, context: BoundaryContext) -> BoundaryProof:
        def result_proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(boundary_input.target_ref,),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # Mandatory adversarial attack: dependent operation after
        # INDETERMINATE. Checked first, unconditionally -- a blocked
        # target is denied regardless of what operation or certainty is
        # claimed.
        if self._recovery_repository.is_target_blocked(
            context.workspace_id,
            target_ref=boundary_input.target_ref,
            exclude_recovery_id=boundary_input.exclude_recovery_id,
        ):
            return result_proof(BoundaryResult.DENY, "DEPENDENT_OPERATION_BLOCKED_BY_INDETERMINATE")

        certainty = boundary_input.known_consequence_certainty
        op = boundary_input.requested_operation

        if certainty is ConsequenceCertainty.PROVEN_COMMITTED:
            if op == "acknowledge_committed":
                return result_proof(BoundaryResult.ALLOW, "COMMITTED_CONSEQUENCE_ACKNOWLEDGED")
            # 06 §24 ALLOW: "known COMMITTED -> do not repeat
            # consequence" -- any operation that would repeat it
            # (retry/reconcile/assume-anything) is denied.
            return result_proof(BoundaryResult.DENY, "COMMITTED_CONSEQUENCE_MUST_NOT_REPEAT")

        if certainty is ConsequenceCertainty.PROVEN_NOT_COMMITTED:
            if op in _RETRY_LIKE_OPERATIONS or op == "reconcile":
                return result_proof(BoundaryResult.ALLOW, "SAFE_RETRY_AFTER_PROVEN_NON_COMMIT")
            return result_proof(BoundaryResult.REQUIRE, "FRESH_BOUNDARY_CHAIN_REQUIRED")

        # Every remaining certainty value (`*_UNKNOWN`,
        # `GOVERNANCE_STATE_UNKNOWN`) is genuinely uncertain.
        if op in _ASSUMPTION_OPERATIONS:
            return result_proof(BoundaryResult.DENY, f"CANNOT_ASSUME_OUTCOME_WITHOUT_PROOF:{op}")
        if op in _RETRY_LIKE_OPERATIONS:
            return result_proof(BoundaryResult.DENY, "BLIND_RETRY_ON_UNCERTAIN_CONSEQUENCE")
        if op == "reconcile":
            # 06 §24 REQUIRE ("Recovery/reconciliation for
            # INDETERMINATE") is satisfied precisely by requesting
            # reconciliation itself -- AC-06-004's own "REQUIRE is
            # named and re-evaluated" pattern: this is the fresh
            # re-evaluation for the one operation that answers it.
            return result_proof(
                BoundaryResult.ALLOW, "RECONCILIATION_PERMITTED_FOR_UNCERTAIN_CONSEQUENCE"
            )
        return result_proof(BoundaryResult.REQUIRE, "RECONCILIATION_REQUIRED_FOR_INDETERMINATE")


__all__ = ["Bnd017Input", "Bnd017FailureIndeterminateEvaluator"]
