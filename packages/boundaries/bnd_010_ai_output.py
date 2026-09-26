"""BND-010 AI OUTPUT / CANONICAL STATE BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 16 (full spec: PURPOSE
"Prevent AI output from becoming human-authoritative, evidentiary or
canonical consequence merely because it was generated, validated or
persisted"; EVIDENCE REQUIREMENT "AI_VALIDATION_PROOF for schema/
contract validity. AI confidence is not DOMAIN_EVIDENCE"; ALLOW "Only
the bounded derived artifact accepted by the AI contract"; DENY list
"AI output -> Decision DECIDED, ... QuestionSelection, ... Session
state advance, ..."; TESTABLE INVARIANT "Persisting a valid AI output
can never, by itself, create an authority-bearing human decision or a
03 state transition.").

WHY THIS EVALUATOR'S OWN DENY LIST (06's FULL LIST: DECISION/
EXPERIMENT/SELECTION/ASSUMPTION/SESSION/GOVERNANCE) HAS NO
CORRESPONDING INPUT FIELD
--------------------------------------------------------------------
14 PKG-19's own scope is exactly "derived artifact persistence" (the
one canonical effect 08 section 23 ALLOWED CANONICAL EFFECT authorizes
for AIOP-001) -- `persistence.ai_record_repository.AIRecordRepository`
has no method that could touch Decision/Selection/HABB/Session/
Assumption at all (proven directly by
`tests/ai/test_generation.py::test_ai_record_repository_has_no_domain_mutation_capability`,
PKG-18). Accepting a field like `requested_effect: str` and comparing
it against 06's own denial list would be exactly the kind of
decorative check 14's DIFF_AUDIT discipline forbids: this evaluator's
own REQUESTED OPERATION is always, structurally, "persist one
AIDerivedArtifact" -- there is nothing else this package's own write
path could ever ask BND-010 to permit.

WHY `evidence_proof_refs` CARRIES THE AI_VALIDATION_PROOF REFERENCE
--------------------------------------------------------------------
`boundaries.types.BoundaryProof.evidence_proof_refs` was first
populated by BND-013 (PKG-17) for a real DOMAIN_EVIDENCE proof. This
evaluator populates the same field for AI_VALIDATION_PROOF instead --
06 section 16's own EVIDENCE REQUIREMENT explicitly names
AI_VALIDATION_PROOF as the proof class this boundary consults, and no
separate `BoundaryProof` field exists for a non-Evidence proof
reference. This does NOT imply AI_VALIDATION_PROOF became
DOMAIN_EVIDENCE (06 section 16: "AI confidence is not DOMAIN_EVIDENCE"
remains unchanged) -- it is the same generic "opaque proof reference"
slot, reused for the one applicable proof class this boundary actually
has.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_contracts.generation import AIGenerationStatus, AIValidationResult
from semantic_types.ids import WorkspaceId
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd010Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    ai_generation_status: AIGenerationStatus
    validation_result: AIValidationResult
    source_workspace_id: WorkspaceId
    ai_validation_proof_ref: str
    output_fields: frozenset[str] = frozenset()
    """F04 WU-04.5 (06 BND-010 DENY list; E14): the top-level fields of the
    output the caller asks to accept. Empty for pre-F04 callers."""
    permitted_output_fields: frozenset[str] | None = None
    """The registered contract's closed field set (HD-18 / 09 §34-35). When
    given, any other field (a Decision, selection, Evidence, Assumption, Session
    or new-Question claim) is DENIED."""

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_010:
            raise ValueError(f"Bnd010Input.boundary_id must be BND_010, got {self.boundary_id}")
        if not isinstance(self.ai_generation_status, AIGenerationStatus):
            raise TypeError(
                "ai_generation_status must be an AIGenerationStatus, got "
                f"{type(self.ai_generation_status)!r}"
            )
        if not isinstance(self.validation_result, AIValidationResult):
            raise TypeError(
                f"validation_result must be an AIValidationResult, got "
                f"{type(self.validation_result)!r}"
            )
        if not self.ai_validation_proof_ref:
            raise ValueError("Bnd010Input.ai_validation_proof_ref must be non-empty")


class Bnd010AiOutputEvaluator:
    """Mandatory adversarial attacks this evaluator alone defends
    against: persisting a derived artifact from a generation that is
    not VALIDATED, from a validation proof that is not itself
    VALIDATED, or across a Workspace boundary."""

    boundary_id = BoundaryId.BND_010
    boundary_version = ContractVersion("1.0")

    def evaluate(self, boundary_input: Bnd010Input, context: BoundaryContext) -> BoundaryProof:
        def proof(
            result: BoundaryResult, reason_code: str, *, evidence_proof_refs: tuple[str, ...] = ()
        ) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=result,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=(boundary_input.ai_validation_proof_ref,),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=evidence_proof_refs,
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        if boundary_input.ai_generation_status is not AIGenerationStatus.VALIDATED:
            return proof(BoundaryResult.DENY, "GENERATION_NOT_VALIDATED")

        if boundary_input.validation_result is not AIValidationResult.VALIDATED:
            return proof(BoundaryResult.DENY, "AI_VALIDATION_PROOF_NOT_VALIDATED")

        if boundary_input.source_workspace_id != context.workspace_id:
            return proof(BoundaryResult.DENY, "CROSS_WORKSPACE_DERIVED_ARTIFACT")

        if boundary_input.permitted_output_fields is not None:
            outside = boundary_input.output_fields - boundary_input.permitted_output_fields
            if outside:
                return proof(BoundaryResult.DENY, f"OUTPUT_OUTSIDE_CONTRACT:{sorted(outside)[0]}")

        return proof(
            BoundaryResult.ALLOW,
            "DERIVED_ARTIFACT_ACCEPTABLE",
            evidence_proof_refs=(boundary_input.ai_validation_proof_ref,),
        )


__all__ = ["Bnd010Input", "Bnd010AiOutputEvaluator"]
