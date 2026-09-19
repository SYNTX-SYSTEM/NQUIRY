"""BND-009 AI INVOCATION BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 15 (full spec: PURPOSE
"Ensure every LLM/model invocation occurs through the approved AI
Gateway context and only when current state, scope, mode and authority
permit the operation"; REQUESTING ACTOR "HUMAN_USER or SYSTEM_SERVICE.
AI_PROCESSOR may not self-authorize a new invocation"; DENY list
"direct application-to-provider call, AI self-invocation without
authority, analysis during protected ACTIVE Human-only Burst,
cross-Workspace context, forbidden tool access, operation not allowed
in current state/mode"; REQUIRE list "approved context, operation
contract, provider route, method/mode prerequisite"; NEXT PERMITTED
PATH "AI provider execution then BND-010 for returned output").

WHY "ANALYSIS DURING PROTECTED ACTIVE BURST" IS NOT RE-CHECKED HERE
--------------------------------------------------------------------
`boundaries.bnd_008_question_burst.Bnd008QuestionBurstEvaluator`
(PKG-09) already proves this exact DENY condition. 06 section 4's own
canonical request path places BND-008 and BND-009 as sequential steps
of the SAME chain (`boundaries.registry.evaluate_chain`); AC-06-003
("downstream ALLOW cannot override upstream DENY") means a caller that
runs BND-008 before BND-009 in one ordered sequence never even reaches
this evaluator for a Burst-blocked request -- re-deriving the same
check here would be the identical "recompute instead of consume"
anti-pattern PKG-09 already rejected for BND-006 trusting BND-005.

WHY "DIRECT APPLICATION-TO-PROVIDER CALL" AND "FORBIDDEN TOOL ACCESS"
ARE NOT FIELDS ON `Bnd009Input`
--------------------------------------------------------------------
Both are structural, not per-request facts this evaluator could
meaningfully accept as input and still provide real protection: "direct
application-to-provider call" is enforced by
`scripts/check_provider_sdk_imports.py`'s own static allowlist (14
section 41 -- only `packages/ai_gateway/adapters/providers/` may import
a provider SDK at all), and tool access is `NOT_APPLICABLE` at this
build phase (14 PKG-19's own OBJECTIVE names no tool declaration; 08
section 21 Tool Access Architecture is unused here). A boolean field a
caller could simply always set to "compliant" would be exactly the
kind of decorative check 14's own DIFF_AUDIT discipline forbids.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_contracts.aiop import AIOperationId
from authority.actor import ActorClass
from semantic_types.ids import WorkspaceId
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd009Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    ai_operation_id: AIOperationId
    ai_operation_contract_version: ContractVersion
    aiop_contract_approved: bool
    context_manifest_workspace_id: WorkspaceId

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_009:
            raise ValueError(f"Bnd009Input.boundary_id must be BND_009, got {self.boundary_id}")
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )


class Bnd009AiInvocationEvaluator:
    """Mandatory adversarial attacks this evaluator alone defends
    against: AI self-invocation, cross-Workspace context at invocation
    time, unapproved/mismatched AIOP contract."""

    boundary_id = BoundaryId.BND_009
    boundary_version = ContractVersion("1.0")

    def evaluate(self, boundary_input: Bnd009Input, context: BoundaryContext) -> BoundaryProof:
        def proof(result: BoundaryResult, reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(boundary_input.ai_operation_id.value,),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # 06 section 15 REQUESTING ACTOR: "AI_PROCESSOR may not
        # self-authorize a new invocation" -- unconditional, unlike
        # BND-008's own narrower Burst-state-dependent AI exclusion.
        if context.actor.actor_class is ActorClass.AI_PROCESSOR:
            return proof(BoundaryResult.DENY, "AI_SELF_INVOCATION_NOT_PERMITTED")

        # DENY: cross-Workspace context.
        if boundary_input.context_manifest_workspace_id != context.workspace_id:
            return proof(BoundaryResult.DENY, "CROSS_WORKSPACE_CONTEXT")

        # REQUIRE: "operation contract" -- the AIOP reference itself is
        # not yet an approved, current contract.
        if not boundary_input.aiop_contract_approved:
            return proof(BoundaryResult.REQUIRE, "APPROVED_OPERATION_CONTRACT_REQUIRED")

        return proof(BoundaryResult.ALLOW, "AI_INVOCATION_PERMITTED")


__all__ = ["Bnd009Input", "Bnd009AiInvocationEvaluator"]
