"""EvidenceRelation: the assessment relation between Evidence and a
ClaimAnchor.

Source: 07_EVIDENCE_AND_PROVENANCE.md section 11 (EvidenceRelation --
"Representation: RELATION, not a standalone domain thing"; endpoints
Evidence <-> ClaimAnchor; section 11.4 Relation Authority: "AI may
propose a relation. AI proposal remains derived. For consequential
use, the relation must be adopted/accepted under the authority already
governing the target interpretation/decision context. No new
EvidenceRelation authority class is introduced."; section 11.5 Relation
Versioning: "Relation must reference: specific Evidence version,
specific ClaimAnchor version"), section 12 (Contradictory Evidence --
"The system must preserve both [supporting and contradicting Evidence].
It must not silently calculate... and discard the contradiction.");
09_DATA_EVENT_API_CONTRACTS.md section 44 (DATA CONTRACT:
EvidenceRelation -- exact field list, section 44.1: "AI-proposed
relation is not authority-bearing acceptance... 09 therefore stores
`origin` and `human_adoption_ref` without inventing a universal
acceptance state machine", `GAP-07-010` remains open).

WHY `evidence_content_version` IS A PLAIN COPIED `RecordVersion`, NOT A
LIVE FOREIGN KEY
------------------------------------------------------------------------
07 section 11.5 requires the relation to reference a *specific*
Evidence version, and 07 section 8 (AC-07-001) makes Evidence content
immutable per identity -- a relation's own claim is "this exact
content-version supported/contradicted this exact claim-version",
which must remain reconstructable even after a later Evidence
supersession. Storing the version value directly (rather than trusting
"current Evidence.content_version") is what makes "A later Evidence or
claim change invalidates the current applicability of the relation
until re-evaluated" (07 section 11.5) a checkable fact rather than an
assumed one -- a future BND-013 (PKG-17) compares this stored value
against the live `Evidence.content_version` to detect staleness itself;
this package only stores the fact honestly.

WHY `human_adoption_ref` IS A BARE `uuid.UUID | None`
------------------------------------------------------------------------
09 section 44.1 explicitly declines to invent "a universal acceptance
state machine" (`GAP-07-010` remains open). No structured "adoption
record" type exists anywhere in this codebase. A bare opaque reference
is the same disclosed forward-reference treatment
`command.envelope.CommandEnvelope.authority_context_ref` and
`commit.coordinator.CommitUnit.commit_time_proof_ref` already
established.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from semantic_types.ids import (
    ClaimAnchorId,
    EvidenceId,
    EvidenceRelationId,
    GenerationId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from evidence.models import ProvenanceOrigin


class EvidenceRelationType(Enum):
    """14 section 6's exact 5-value closed vocabulary ("EvidenceRelation
    assessment"), matching 07 section 11.3/09 section 44 verbatim.
    """

    UNASSESSED = "UNASSESSED"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXTUAL = "CONTEXTUAL"
    DOES_NOT_SUPPORT = "DOES_NOT_SUPPORT"


@dataclass(frozen=True, slots=True)
class EvidenceRelation:
    """09 section 44's exact field list (plus the disclosed
    `workspace_id` technical necessity every other protected record in
    this codebase already carries)."""

    evidence_relation_id: EvidenceRelationId
    workspace_id: WorkspaceId
    evidence_id: EvidenceId
    evidence_content_version: RecordVersion
    claim_anchor_id: ClaimAnchorId
    relation_type: EvidenceRelationType
    origin: ProvenanceOrigin
    producer_ref: str
    ai_generation_id: GenerationId | None
    human_adoption_ref: UUID | None
    created_at: datetime
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_relation_id, EvidenceRelationId):
            raise TypeError(
                "evidence_relation_id must be an EvidenceRelationId, "
                f"got {type(self.evidence_relation_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.evidence_id, EvidenceId):
            raise TypeError(f"evidence_id must be an EvidenceId, got {type(self.evidence_id)!r}")
        if not isinstance(self.evidence_content_version, RecordVersion):
            raise TypeError(
                "evidence_content_version must be a RecordVersion, "
                f"got {type(self.evidence_content_version)!r}"
            )
        if not isinstance(self.claim_anchor_id, ClaimAnchorId):
            raise TypeError(
                f"claim_anchor_id must be a ClaimAnchorId, got {type(self.claim_anchor_id)!r}"
            )
        if not isinstance(self.relation_type, EvidenceRelationType):
            raise TypeError(
                f"relation_type must be an EvidenceRelationType, got {type(self.relation_type)!r}"
            )
        if not isinstance(self.origin, ProvenanceOrigin):
            raise TypeError(f"origin must be a ProvenanceOrigin, got {type(self.origin)!r}")
        if not self.producer_ref:
            raise ValueError("EvidenceRelation.producer_ref must be non-empty")
        if self.ai_generation_id is not None and not isinstance(
            self.ai_generation_id, GenerationId
        ):
            raise TypeError("ai_generation_id must be a GenerationId or None")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )


__all__ = ["EvidenceRelationType", "EvidenceRelation"]
