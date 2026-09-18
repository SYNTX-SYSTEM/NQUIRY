"""BND-002 WORKSPACE BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §8. "Ensure every protected
consequential operation resolves to one effective Workspace and cannot
cross Workspace scope... Claimed Workspace IDs are not authoritative by
themselves."; 11_SECURITY_PRIVACY_OBSERVABILITY.md §11 (AC-11-004,
Workspace Isolation Law) and §12 (Cross-Workspace Reference
Enforcement).

WHY THIS EVALUATOR CALLS `WorkspaceRepository.get` ITSELF
------------------------------------------------------------
06 §8's EVIDENCE REQUIREMENT is "SYSTEM_PROOF of object-to-Workspace
resolution" -- a claim alone is explicitly insufficient ("Claimed
Workspace IDs are not authoritative by themselves"). A caller-supplied
boolean "workspace_exists" would be exactly that insufficient claim.
This evaluator therefore holds a real `WorkspaceRepository` (PKG-01)
and re-reads it on every call, the same "always current, never cached"
discipline `AuthorityResolver` established (PKG-03) -- see
`scripts/check_architecture_dependencies.py`'s `INTERNAL_ALLOWED["boundaries"]`
entry for why this package may hold one at all.

`resolved_object_workspace_ids` is supplied by the caller because this
evaluator has no way to independently know which protected objects
(Session, Challenge, Question, Burst, ...) are involved in a given
operation -- 06 §8 itself frames the VALIDATION as "all objects belong
to same permitted Workspace where operation requires one scope", which
presupposes the caller already resolved each object's own
`workspace_id` (every canonical object PKG-05/06/07 built carries one).
This evaluator's job is the cross-check and the existence proof, not
discovering which objects matter.
"""

from __future__ import annotations

from dataclasses import dataclass

from persistence.workspace_repository import WorkspaceRepository
from semantic_types.ids import WorkspaceId
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd002Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    resolved_object_workspace_ids: tuple[WorkspaceId, ...]

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_002:
            raise ValueError(f"Bnd002Input.boundary_id must be BND_002, got {self.boundary_id}")


class Bnd002WorkspaceEvaluator:
    boundary_id = BoundaryId.BND_002
    boundary_version = ContractVersion("1")

    def __init__(self, workspace_repository: WorkspaceRepository) -> None:
        self._workspace_repository = workspace_repository

    def evaluate(self, boundary_input: Bnd002Input, context: BoundaryContext) -> BoundaryProof:
        def deny(reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=BoundaryResult.DENY,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=tuple(
                    str(w.value) for w in boundary_input.resolved_object_workspace_ids
                ),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        resolved = boundary_input.resolved_object_workspace_ids
        if not resolved:
            # Mandatory-category attack: unresolvable Workspace.
            return deny("UNRESOLVED_WORKSPACE_NO_OBJECTS")

        distinct = set(resolved)
        if len(distinct) > 1:
            # Mandatory adversarial attack: Workspace mismatch
            # (cross-Workspace object set).
            return deny("CROSS_WORKSPACE_OBJECT_SET")

        effective_workspace_id = next(iter(distinct))
        if effective_workspace_id != context.workspace_id:
            # "claimed Workspace differs from authoritative scope".
            return deny("CLAIMED_WORKSPACE_MISMATCH")

        if self._workspace_repository.get(effective_workspace_id) is None:
            return deny("UNRESOLVED_WORKSPACE_NOT_FOUND")

        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=BoundaryResult.ALLOW,
            reason_code="SINGLE_EFFECTIVE_WORKSPACE_PROVEN",
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(str(effective_workspace_id.value),),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd002Input", "Bnd002WorkspaceEvaluator"]
