"""BND-001 IDENTITY BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md §7. "Establish the actor class and
provable identity before any consequential authority evaluation.
Identity is necessary. Identity is not authority."

WHAT THIS EVALUATOR CAN HONESTLY CHECK RIGHT NOW
--------------------------------------------------
06 §7's IDENTITY REQUIREMENT differs by actor class: human consequential
mutation needs "authenticated User identity", a system operation needs
"identified trusted service identity", and AI operation identity "must
remain distinguishable from HUMAN_USER and SYSTEM_SERVICE". No real
authentication adapter exists yet (`security.identity.IdentityPort` is a
port with no production adapter, PKG-01, `GAP-14-001` still open) -- so
this evaluator cannot itself verify a credential. What it *can* verify,
honestly and completely, is the one thing `authority.actor.ActorIdentity`
already structurally guarantees end-to-end: the actor's *class* is
exactly one of the four 04 §3 values, and it matches whichever classes
the requested operation actually accepts. This is not a weaker version
of BND-001 -- it is the mandatory adversarial attack "forged identity"
made concrete: `ActorClass` is a closed enum a caller cannot coerce an
arbitrary string into (see `tests/boundaries/test_bnd_001_identity.py`),
so "AI presented as human" (06 §7 DENY) is refused at the type layer
before this evaluator even runs, and this evaluator refuses the
remaining case: a genuinely-typed actor whose class the operation does
not accept at all.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorClass
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd001Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    required_actor_classes: frozenset[ActorClass]

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_001:
            raise ValueError(f"Bnd001Input.boundary_id must be BND_001, got {self.boundary_id}")
        if not self.required_actor_classes:
            raise ValueError("Bnd001Input.required_actor_classes must be non-empty")


class Bnd001IdentityEvaluator:
    boundary_id = BoundaryId.BND_001
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: Bnd001Input, context: BoundaryContext) -> BoundaryProof:
        actor_class = context.actor.actor_class
        if actor_class in boundary_input.required_actor_classes:
            result = BoundaryResult.ALLOW
            reason_code = "IDENTITY_VALID_FOR_OPERATION"
        else:
            result = BoundaryResult.DENY
            reason_code = f"IDENTITY_CLASS_NOT_ACCEPTED:{actor_class.value}"

        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=result,
            reason_code=reason_code,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(actor_class.value,),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd001Input", "Bnd001IdentityEvaluator"]
