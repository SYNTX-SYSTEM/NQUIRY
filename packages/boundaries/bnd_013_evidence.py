"""BND-013 EVIDENCE BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 19 (full spec: PURPOSE
"Prevent non-evidence signals from satisfying a transition or human
decision that requires DOMAIN_EVIDENCE"; VALIDATION "At minimum reject
substitution of: AI confidence / AI classification / AI inference /
raw user assertion / imported source with no required source metadata
-- for validated DOMAIN_EVIDENCE where validation is required"; ALLOW
"Required Evidence condition is valid under 07 rules"; DENY "Known
invalid/out-of-scope Evidence or prohibited substitution"; REQUIRE "If
evidence policy/validation required by the operation is not yet
closed"; FAILURE BEHAVIOR "Fail closed when Evidence is required and
validity cannot be proven.").

WHY "REJECT AI CONFIDENCE/RAW ASSERTION SUBSTITUTION" IS NOT A RUNTIME
CHECK IN THIS EVALUATOR
--------------------------------------------------------------------
06's own VALIDATION list is already closed structurally one layer
down: `evidence.models.Evidence` (PKG-16) has no `confidence`/`score`
field of any kind to substitute into, and `EvidenceSetReference`
carries only `(EvidenceId, content_version)` pairs -- there is no
representable input shape by which "AI confidence" or "a raw user
assertion" could ever reach this evaluator disguised as a member
(PKG-16's own mandatory adversarial attack #1,
`test_evidence_has_no_confidence_field`, already proves the absence).
What THIS evaluator adds, that PKG-16 could not build (07/09's own
"Evidence existence != sufficiency" plus "no global Evidence score" --
PKG-16 had no BND-013 yet), is CURRENTNESS: a resolvable, real Evidence
row is not, by itself, a legitimate consequential prerequisite unless
it is still fresh (06 CURRENT STATE: "Current Evidence relations and
later 07 validation status"). That is exactly what
`evidence.freshness.resolve_evidence_set_freshness` proves.

WHY BND-013 AND THE BND-014 COMMIT-FRESHNESS LINKAGE SHARE ONE
RESOLUTION FUNCTION, EVALUATED TWICE
--------------------------------------------------------------------
06 section 19 NEXT PERMITTED PATH: "BND-014 after all other boundaries
pass" -- and 09 section 114 assigns the actual member/version
comparison to BND-014 itself ("BND-014 compares member versions/
current states"). This evaluator is therefore the PREPARE-TIME
legitimacy gate (is a fresh, in-scope Evidence set proven now?); the
`boundaries.bnd_014_commit` extension (this package) is the
COMMIT-TIME revalidation (is it STILL fresh, immediately before
persistence?) -- the identical duplication-on-purpose precedent
`Bnd014CommitEvaluator` already documents for authority (BND-005 vs
BND-014's own independent re-check).
"""

from __future__ import annotations

from dataclasses import dataclass

from evidence.freshness import EvidenceSetFreshnessResult
from semantic_types.ids import EvidenceSetId
from semantic_types.versions import ContractVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd013Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    evidence_required: bool
    evidence_set_ref_id: EvidenceSetId | None
    freshness: EvidenceSetFreshnessResult | None

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_013:
            raise ValueError(f"Bnd013Input.boundary_id must be BND_013, got {self.boundary_id}")
        if (self.evidence_set_ref_id is None) != (self.freshness is None):
            raise ValueError(
                "Bnd013Input.freshness must be provided if and only if "
                "evidence_set_ref_id is provided"
            )
        if (
            self.freshness is not None
            and self.evidence_set_ref_id is not None
            and self.freshness.evidence_set_ref_id != self.evidence_set_ref_id
        ):
            raise ValueError(
                "Bnd013Input.freshness.evidence_set_ref_id must match evidence_set_ref_id"
            )


class Bnd013EvidenceEvaluator:
    """06 section 19's Evidence prerequisite boundary. Mandatory
    adversarial attacks this evaluator alone defends against: Evidence
    invalidated after prepare, Evidence unavailable after prepare,
    cross-Workspace Evidence, set membership no longer resolvable.
    """

    boundary_id = BoundaryId.BND_013
    boundary_version = ContractVersion("1.0")

    def evaluate(self, boundary_input: Bnd013Input, context: BoundaryContext) -> BoundaryProof:
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
                input_refs=(
                    ()
                    if boundary_input.evidence_set_ref_id is None
                    else (str(boundary_input.evidence_set_ref_id.value),)
                ),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=evidence_proof_refs,
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # BOUNDARY PURPOSE: an operation not requiring DOMAIN_EVIDENCE
        # has nothing for this boundary to prove -- not vacuously
        # denied (mirrors BND-014's own "no targets at all" ALLOW).
        if not boundary_input.evidence_required:
            return proof(BoundaryResult.ALLOW, "EVIDENCE_NOT_REQUIRED")

        # REQUIRE: "If evidence policy/validation required by the
        # operation is not yet closed" -- here, concretely, no
        # EvidenceSetReference was ever supplied for an operation that
        # requires one.
        if boundary_input.evidence_set_ref_id is None:
            return proof(BoundaryResult.REQUIRE, "EVIDENCE_SET_REQUIRED_BUT_ABSENT")

        freshness = boundary_input.freshness
        assert freshness is not None  # enforced by __post_init__

        # FAILURE BEHAVIOR: "Fail closed when Evidence is required and
        # validity cannot be proven" -- a forged/vanished set ref.
        if not freshness.evidence_set_found:
            return proof(BoundaryResult.DENY, "EVIDENCE_SET_NOT_FOUND")

        if not freshness.is_fresh:
            return proof(BoundaryResult.DENY, f"STALE_EVIDENCE:{','.join(freshness.stale_refs)}")

        return proof(
            BoundaryResult.ALLOW,
            "EVIDENCE_SET_CURRENT",
            evidence_proof_refs=(str(boundary_input.evidence_set_ref_id.value),),
        )


__all__ = ["Bnd013Input", "Bnd013EvidenceEvaluator"]
