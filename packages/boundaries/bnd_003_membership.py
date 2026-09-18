"""BND-003 MEMBERSHIP BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §9. "Ensure human Workspace-scoped
authority is exercised only by an active Workspace member where
membership is required. Membership is an authority precondition.
Membership is not authority."

TESTABLE INVARIANT (06 §9, transcribed): "A removed Workspace member
cannot commit a Workspace-scoped consequential operation even if an
older authority binding still exists in storage." This evaluator
re-reads `MembershipRepository.get_current_membership` fresh on every
call (PKG-02's own repository already filters to `status = 'ACTIVE'`
only -- a revoked membership row existing in storage never counts),
which is exactly what makes the "revoked membership treated as active"
attack structurally impossible here, independent of whatever an older
`HumanAuthorityBinding` row might still say.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass
from persistence.membership_repository import MembershipRepository
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd003Input:
    boundary_id: BoundaryId
    context: BoundaryContext

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_003:
            raise ValueError(f"Bnd003Input.boundary_id must be BND_003, got {self.boundary_id}")


class Bnd003MembershipEvaluator:
    boundary_id = BoundaryId.BND_003
    boundary_version = ContractVersion("1")

    def __init__(self, membership_repository: MembershipRepository) -> None:
        self._membership_repository = membership_repository

    def evaluate(self, boundary_input: Bnd003Input, context: BoundaryContext) -> BoundaryProof:
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

        # 06 §9 REQUESTING ACTOR: HUMAN_USER. Membership is a human
        # concept -- a SYSTEM_SERVICE/AI_PROCESSOR actor cannot be a
        # Workspace member at all, so it is denied here rather than
        # this evaluator asking the repository a question that can
        # never legitimately answer yes for it.
        if context.actor.actor_class is not ActorClass.HUMAN_USER:
            return result_proof(BoundaryResult.DENY, "MEMBERSHIP_REQUIRES_HUMAN_ACTOR")

        membership = self._membership_repository.get_current_membership(
            context.workspace_id, context.actor.user_id
        )
        if membership is None:
            # Mandatory adversarial attack: missing membership.
            # Covers both "never a member" and "removed member" --
            # `get_current_membership` filters to ACTIVE only, so a
            # revoked row is indistinguishable from no row at all here,
            # which is exactly the 06 §9 TESTABLE INVARIANT.
            return result_proof(BoundaryResult.DENY, "NO_ACTIVE_MEMBERSHIP")

        return result_proof(BoundaryResult.ALLOW, "ACTIVE_MEMBERSHIP_PROVEN")


__all__ = ["Bnd003Input", "Bnd003MembershipEvaluator"]
