"""BND-005 (Human Authority) for the source-explicit participation right.

F03 HD-15. BND-005's binding evaluator resolves `HumanAuthorityBinding`
classes; Question capture's authority is the participation right
(04 AUTH-DEP-Q-001), which is not a binding. This evaluator fills the same
BND-005 slot in the precommit chain for that operation. It evaluates the same
definition (`boundaries.participation_right`) that BND-014 re-evaluates at
commit, so the precommit result and the effect-gate result cannot diverge.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from persistence.membership_repository import MembershipRepository
from persistence.session_participation_repository import SessionParticipationRepository
from semantic_types.versions import ContractVersion

from boundaries.participation_right import resolve_participation_right
from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd005ParticipationInput:
    boundary_id: BoundaryId
    context: BoundaryContext
    session_id: uuid.UUID

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_005:
            raise ValueError(
                f"Bnd005ParticipationInput.boundary_id must be BND_005, got {self.boundary_id}"
            )


class Bnd005ParticipationEvaluator:
    boundary_id = BoundaryId.BND_005
    boundary_version = ContractVersion("1")

    def __init__(
        self,
        participation_repository: SessionParticipationRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self._participations = participation_repository
        self._memberships = membership_repository

    def evaluate(
        self, boundary_input: Bnd005ParticipationInput, context: BoundaryContext
    ) -> BoundaryProof:
        resolution = resolve_participation_right(
            participation_repository=self._participations,
            membership_repository=self._memberships,
            actor=context.actor,
            workspace_id=context.workspace_id,
            session_id=boundary_input.session_id,
        )
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=BoundaryResult.ALLOW if resolution.granted else BoundaryResult.DENY,
            reason_code=resolution.reason_code,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=("SESSION", str(boundary_input.session_id)),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd005ParticipationEvaluator", "Bnd005ParticipationInput"]
