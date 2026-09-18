"""BND-004 ROLE / GOVERNANCE CONTEXT BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §10. "Resolve source-explicit role
rights and governance context without converting role labels into
generic authority."

WHY `accepted_roles` IS CALLER-SUPPLIED, NOT HARDCODED HERE
------------------------------------------------------------
06 §10's own examples ("Facilitator in Workspace: may create Challenge";
"Session Participant: may submit own Question during active Burst")
are each a *specific*, source-cited operation-to-role mapping (04
AUTH-DEP-CH-001, 04 §40 AUTH-DEP-Q-001) -- this evaluator does not own
those mappings and must not invent new ones. `accepted_roles` is the
caller's declaration of which roles *this specific, already-identified*
operation accepts; this evaluator's own job is narrower and mechanical:
prove the actor's *current* role (not a stale or claimed one) is one of
them. This is exactly what keeps BND-004 from collapsing into "the
generic authority function" the package prompt forbids (14 PKG-09
FAILURE_RECOVERY-adjacent "Do not compress to one authorization
function") -- the *mapping* of role to right lives with whichever
future Command construction supplies `accepted_roles`, never here.

TESTABLE INVARIANT (06 §10, transcribed): "A Facilitator cannot control
a QuestionBurst in a Session lacking an ACTIVE FacilitatorScopeBinding."
`FacilitatorScopeBinding` does not exist yet (deferred since PKG-02);
this evaluator does not fabricate that check -- a caller requiring it
must `REQUIRE` (06 §10) rather than this evaluator silently treating
role alone as sufficient for Burst control specifically. This
evaluator only proves the *role* half of that invariant; it never
claims to prove the FacilitatorScopeBinding half.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authority.actor import ActorClass
from governance.membership import WorkspaceRole
from persistence.membership_repository import MembershipRepository
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd004Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    membership_id: uuid.UUID
    accepted_roles: frozenset[WorkspaceRole]

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_004:
            raise ValueError(f"Bnd004Input.boundary_id must be BND_004, got {self.boundary_id}")
        if not self.accepted_roles:
            raise ValueError("Bnd004Input.accepted_roles must be non-empty")


class Bnd004RoleContextEvaluator:
    boundary_id = BoundaryId.BND_004
    boundary_version = ContractVersion("1")

    def __init__(self, membership_repository: MembershipRepository) -> None:
        self._membership_repository = membership_repository

    def evaluate(self, boundary_input: Bnd004Input, context: BoundaryContext) -> BoundaryProof:
        def result_proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(str(boundary_input.membership_id),),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        if context.actor.actor_class is not ActorClass.HUMAN_USER:
            return result_proof(BoundaryResult.DENY, "ROLE_CONTEXT_REQUIRES_HUMAN_ACTOR")

        role_assignment = self._membership_repository.get_current_role(boundary_input.membership_id)
        if role_assignment is None:
            # Mandatory-category attack: role-only authority -- here in
            # its "no current role at all" shape (e.g. removed but a
            # stale scope binding elsewhere still references the
            # membership).
            return result_proof(BoundaryResult.DENY, "NO_CURRENT_ROLE")

        if role_assignment.role not in boundary_input.accepted_roles:
            # Mandatory-category attack: role-only authority -- a real
            # current role that simply is not the one this operation
            # accepts (e.g. Observer/Viewer attempting a Facilitator-only
            # operation, 06 §10 DENY: "Observer/Viewer mutation").
            return result_proof(
                BoundaryResult.DENY, f"ROLE_NOT_ACCEPTED:{role_assignment.role.value}"
            )

        return result_proof(BoundaryResult.ALLOW, f"ROLE_ACCEPTED:{role_assignment.role.value}")


__all__ = ["Bnd004Input", "Bnd004RoleContextEvaluator"]
