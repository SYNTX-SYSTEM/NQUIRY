"""AIDerivedArtifact: the generic derived-analysis container.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 7.1 (core tables list --
`ai_derived_artifacts | derived | yes | record_version |
ai_gateway_writer through bounded derived port`), section 9 (migration
plan -- `007_ai_operational`: "generations, manifests, derived
artifacts"); 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 23 (AIOP-001
OUTPUT CONTRACT -- "Structured derived analysis such as: classification
proposals, pattern descriptions, unusual-question flags, contradiction
proposals, Question-family proposals, additional Question
suggestions"; ALLOWED CANONICAL EFFECT -- "Persist permitted derived
analysis artifacts/annotations according to 09 representation.");
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md GAP-12-008 (Derived AI artifact
physical type -- "Prototype must map AIOP-001 output to an approved
08/09 derived representation without inventing a new domain Thing.",
home 08/09, status carried, NOT resolved by this package).

WHY THIS TYPE HAS NO PER-OPERATION STRUCTURED SCHEMA, AND WHY
GAP-12-008 REMAINS OPEN AFTER THIS PACKAGE
--------------------------------------------------------------------
09's own DATA CONTRACT catalogue gives several AIOPs a real, named
domain Thing to create (AIOP-004 ASSUMPTION_INFERENCE creates
`Assumption` at `status=UNKNOWN`, 09 section 36.1; AIOP-005
INSIGHT_SYNTHESIS creates AI-origin `Insight`, 09 section 37.1) -- but
AIOP-001 QUESTION_ANALYSIS, the one AIOP 12 section 12.1 actually
requires for the minimum prototype, has NO corresponding named domain
Thing anywhere in 07/09. Inventing one (e.g. a bespoke
"QuestionAnalysisResult" CANONICAL_DOMAIN_OBJECT) would be exactly the
semantic invention 14's own DIFF_AUDIT discipline forbids. 14 section
7.1 already commits to a generic `ai_derived_artifacts` table as the
implementation vehicle for whichever AIOP produced output with no
dedicated domain Thing -- that IS the "approved 08/09 derived
representation" GAP-12-008 asks for, but the gap register still
correctly marks it open because 08/09 themselves never gave this
generic container its own field-by-field DATA CONTRACT (unlike every
other artifact class, sections 21-60). This module materializes
exactly what 14 already authorized (the physical container), while
disclosing, not silently closing, the remaining gap: WHICH AIOP output
maps to a real named domain Thing versus this generic container is
still an open, per-operation decision 08/09 have not made.

WHY `ai_derived_artifact_id` IS A BARE `uuid.UUID`, NOT A NEW STRONG ID
TYPE
--------------------------------------------------------------------
14 section 5's closed identity/version list (`semantic_types.ids`) was
materialized in full at PKG-00 and does not name a
`DerivedArtifactId` -- the same reasoning `ClaimAnchor.target_id`
(PKG-16) and `AuthorityContextReference`'s own `authority_context_ref`
(PKG-10) already apply to a concept 14 does not enumerate as its own
first-class identity: giving GAP-12-008's own still-open container a
bespoke strong type would overstate its architectural standing.

WHY `content` IS AN OPAQUE `str`, NOT A STRUCTURED PAYLOAD
--------------------------------------------------------------------
08 section 23's own OUTPUT CONTRACT lists six illustrative shapes
("classification proposals", "pattern descriptions", ...) with no
single common schema; `evidence.models.Evidence.content` (PKG-16)
already established the identical "opaque str, no premature schema"
choice for a comparably underspecified content field.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from semantic_types.ids import GenerationId, WorkspaceId
from semantic_types.versions import RecordVersion

from ai_contracts.aiop import AIOperationId


@dataclass(frozen=True, slots=True)
class AIDerivedArtifact:
    ai_derived_artifact_id: uuid.UUID
    workspace_id: WorkspaceId
    ai_generation_id: GenerationId
    ai_operation_id: AIOperationId
    content: str
    content_fingerprint: str
    created_at: datetime
    record_version: RecordVersion
    provenance_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ai_derived_artifact_id, uuid.UUID):
            raise TypeError(
                "ai_derived_artifact_id must be a uuid.UUID, got "
                f"{type(self.ai_derived_artifact_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.ai_generation_id, GenerationId):
            raise TypeError(
                f"ai_generation_id must be a GenerationId, got {type(self.ai_generation_id)!r}"
            )
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )
        if not self.content:
            raise ValueError("AIDerivedArtifact.content must be non-empty")
        if not self.content_fingerprint:
            raise ValueError("AIDerivedArtifact.content_fingerprint must be non-empty")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )


__all__ = ["AIDerivedArtifact"]
