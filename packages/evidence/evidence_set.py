"""EvidenceSetReference: an immutable, exact consumed-Evidence-context
snapshot.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 45 (DATA CONTRACT:
EvidenceSetReference -- "Representation: OPERATIONAL REFERENCE.
Required when a consequential operation depends on an exact Evidence
context... Supports AC-07-004 and BND-014 freshness... EvidenceSetReference
does not itself become Evidence"); 14_IMPLEMENTATION_SEQUENCE.md section
22 ("EvidenceSetReference is an immutable consumed version set...
Commit freshness rechecks every Evidence version consumed by a
consequential operation").

WHY `member_evidence_id_and_version_list` IS `tuple[EvidenceSetMember, ...]`
------------------------------------------------------------------------
09's own field name is a compound "id AND version" list -- a plain
`tuple[EvidenceId, ...]` would silently drop the version each member
was pinned at, defeating the whole purpose of the set (09 section 45.1:
"Supports... BND-014 freshness"). `EvidenceSetMember` is the smallest
typed pair that preserves both facts, mirroring
`commit.coordinator.CommitUnit`'s own array-of-typed-refs precedent
rather than an untyped dict/tuple-of-tuples.

WHY `fingerprint` IS COMPUTED THE SAME WAY
`compute_frozen_membership_fingerprint` (PKG-07) WAS
------------------------------------------------------------------------
14 section 19's own `[IMPLEMENTATION CHOICE]` for `QuestionBurstMembership`'s
fingerprint (canonical sorted join, SHA-256) is the only concrete
precedent this codebase has for "a durable fingerprint over an ordered
set of typed members" -- reused here rather than inventing a second
algorithm for the same shape of problem. `[IMPLEMENTATION CHOICE]`,
disclosed: canonical sort by `(evidence_id, content_version)`, then
SHA-256 over the deterministic joined string.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from semantic_types.ids import ClaimAnchorId, EvidenceId, EvidenceSetId, WorkspaceId
from semantic_types.versions import RecordVersion


@dataclass(frozen=True, slots=True)
class EvidenceSetMember:
    evidence_id: EvidenceId
    content_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, EvidenceId):
            raise TypeError(f"evidence_id must be an EvidenceId, got {type(self.evidence_id)!r}")
        if not isinstance(self.content_version, RecordVersion):
            raise TypeError(
                f"content_version must be a RecordVersion, got {type(self.content_version)!r}"
            )


@dataclass(frozen=True, slots=True)
class EvidenceSetReference:
    """09 section 45's exact field list."""

    evidence_set_ref_id: EvidenceSetId
    workspace_id: WorkspaceId
    consumer_type: str
    consumer_id: str | None
    member_evidence_id_and_version_list: tuple[EvidenceSetMember, ...]
    claim_anchor_refs: tuple[ClaimAnchorId, ...]
    created_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_set_ref_id, EvidenceSetId):
            raise TypeError(
                "evidence_set_ref_id must be an EvidenceSetId, "
                f"got {type(self.evidence_set_ref_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.consumer_type:
            raise ValueError("EvidenceSetReference.consumer_type must be non-empty")
        if not self.member_evidence_id_and_version_list:
            # Mandatory-category adversarial attack: an "exact Evidence
            # context" that names no Evidence at all is not a legitimate
            # consumed set (09 section 45: "Required when a consequential
            # operation depends on an exact Evidence context").
            raise ValueError(
                "EvidenceSetReference.member_evidence_id_and_version_list must be non-empty"
            )
        if not self.fingerprint:
            raise ValueError("EvidenceSetReference.fingerprint must be non-empty")


def compute_evidence_set_fingerprint(members: tuple[EvidenceSetMember, ...]) -> str:
    """`[IMPLEMENTATION CHOICE]`, disclosed in module docstring: SHA-256
    over the canonically sorted `evidence_id:content_version` join --
    the identical algorithmic shape
    `domain.burst_membership.compute_frozen_membership_fingerprint`
    (PKG-07) already established for a comparable "durable fingerprint
    over an ordered set of typed members" problem.
    """
    canonical = ",".join(
        f"{member.evidence_id.value}:{member.content_version.value}"
        for member in sorted(
            members, key=lambda m: (str(m.evidence_id.value), m.content_version.value)
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["EvidenceSetMember", "EvidenceSetReference", "compute_evidence_set_fingerprint"]
