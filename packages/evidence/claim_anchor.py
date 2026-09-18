"""ClaimAnchor: a semantic reference to the exact claim-bearing content
being evaluated.

Source: 07_EVIDENCE_AND_PROVENANCE.md section 10 (Claim Architecture --
"A ClaimAnchor is a semantic reference to the exact claim-bearing
content being evaluated. It is not a top-level domain object... Without
versioned claim targeting, the system could not prove whether Evidence
supported: the current claim, a prior version, another claim in the
same object... A ClaimAnchor only identifies what is being evaluated",
section 10.3: "ClaimAnchor Does Not Grant Truth");
09_DATA_EVENT_API_CONTRACTS.md section 43 (DATA CONTRACT: ClaimAnchor --
exact field list, "Representation: SEMANTIC REFERENCE MATERIALIZATION,
not a canonical domain object").

WHY `target_type`/`target_id` ARE PLAIN, UNCONSTRAINED FIELDS
------------------------------------------------------------------------
07 section 10.1's own examples ("Assumption.statement,
Experiment.hypothesis, Decision.rationale, Insight.text, specific
Question-related research claim") span several object classes that do
not exist yet in this codebase (Assumption, Experiment, Insight are all
future packages). A closed enum here would either omit those future
classes (silent gap) or invent their existence prematurely (semantic
invention this package's own coding prompt forbids). This mirrors the
identical "polymorphic reference, closed vocabulary enforced nowhere
yet" precedent `human_authority_bindings.scope_type`/`scope_id`
already established (PKG-02) -- `target_type` names the target's
class as an inert string, `target_id` is a bare `uuid.UUID`, and no
foreign key is possible or claimed.

WHY THERE IS NO UPDATE METHOD ANYWHERE FOR ClaimAnchor
------------------------------------------------------------------------
07 section 43.1: "If target content changes, create a new ClaimAnchor."
A ClaimAnchor row is append-only for the exact same reason
`question_lineage` rows are (PKG-06): it is a permanent record of what
was evaluated at one exact target version, never a live pointer that
tracks the target's current state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from semantic_types.ids import ClaimAnchorId, WorkspaceId
from semantic_types.versions import RecordVersion


@dataclass(frozen=True, slots=True)
class ClaimAnchor:
    """09 section 43's exact field list."""

    claim_anchor_id: ClaimAnchorId
    workspace_id: WorkspaceId
    target_type: str
    target_id: UUID
    claim_field_or_fragment: str
    target_content_version: RecordVersion
    content_fingerprint: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.claim_anchor_id, ClaimAnchorId):
            raise TypeError(
                f"claim_anchor_id must be a ClaimAnchorId, got {type(self.claim_anchor_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.target_type:
            raise ValueError("ClaimAnchor.target_type must be non-empty")
        if not isinstance(self.target_id, UUID):
            raise TypeError(f"target_id must be a uuid.UUID, got {type(self.target_id)!r}")
        if not self.claim_field_or_fragment:
            raise ValueError("ClaimAnchor.claim_field_or_fragment must be non-empty")
        if not isinstance(self.target_content_version, RecordVersion):
            raise TypeError(
                "target_content_version must be a RecordVersion, "
                f"got {type(self.target_content_version)!r}"
            )


__all__ = ["ClaimAnchor"]
