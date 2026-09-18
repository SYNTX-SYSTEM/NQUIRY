"""BND-005 HUMAN AUTHORITY BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §11. "Validate the exact human
operation authority required by 04 for the requested consequential
operation."

WHY THIS EVALUATOR HOLDS AN ALREADY-BUILT `AuthorityResolver`
------------------------------------------------------------------
14 PKG-09's own coding prompt: "AUTHORITY: Use AuthorityResolver
current proof only." This evaluator does not construct its own
`MembershipRepository`/`AuthorityBindingRepository` -- it receives a
fully-constructed `authority.resolver.AuthorityResolver` via the
constructor (dependency injection), so this module's own import
surface stays exactly `authority` + `semantic_types` (no `persistence`
needed here at all, unlike BND-002/003/004). `AuthorityResolver.resolve()`
already re-reads live on every call (PKG-03's own "never caches"
discipline) -- this evaluator adds nothing on top except translating
`AuthorityVerdict` into `BoundaryResult`.

`AuthorityVerdict.UNRESOLVED` maps to `BoundaryResult.DENY`, not to a
`BoundaryResult.ESCALATE` or any partial-success value: 14 §16 states
"`UNRESOLVED` is fail-closed for consequential operation", and
AC-06-013 (06 §47) requires the least-permissive interpretation under
uncertainty -- `DENY` is 06 §2.2's own "terminal" result, which is the
correct translation of "fail-closed", not `ESCALATE` (06 §2.4:
"routed to an explicitly authorized human or governance process" --
this evaluator has no such routing target to name).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from governance.authority_binding import AuthorityClass
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd005Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    required_authority_class: AuthorityClass
    scope_type: str
    scope_id: uuid.UUID

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_005:
            raise ValueError(f"Bnd005Input.boundary_id must be BND_005, got {self.boundary_id}")
        if not self.scope_type:
            raise ValueError("Bnd005Input.scope_type must be non-empty")


class Bnd005HumanAuthorityEvaluator:
    boundary_id = BoundaryId.BND_005
    boundary_version = ContractVersion("1")

    def __init__(self, resolver: AuthorityResolver) -> None:
        self._resolver = resolver

    def evaluate(self, boundary_input: Bnd005Input, context: BoundaryContext) -> BoundaryProof:
        resolution = self._resolver.resolve(
            AuthorityRequest(
                actor=context.actor,
                workspace_id=context.workspace_id,
                operation=context.operation,
                required_authority_class=boundary_input.required_authority_class,
                scope_type=boundary_input.scope_type,
                scope_id=boundary_input.scope_id,
            )
        )
        result = (
            BoundaryResult.ALLOW
            if resolution.verdict is AuthorityVerdict.GRANTED
            else BoundaryResult.DENY
        )
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=result,
            reason_code=resolution.proof.reason.value,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(boundary_input.scope_type, str(boundary_input.scope_id)),
            authoritative_version_refs=(),
            authority_proof=resolution.proof,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd005Input", "Bnd005HumanAuthorityEvaluator"]
