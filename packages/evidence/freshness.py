"""Evidence proof resolver: the "commit Evidence proof" file 14's own
file-level map (section 48) assigns to this package
(`packages/evidence/freshness.py`).

Source: 09_DATA_EVENT_API_CONTRACTS.md section 114 (Evidence Commit
Materialization -- "Command/Decision context stores evidence_set_ref.
BND-014 compares member versions/current states. If any member:
invalidated / superseded where current use requires newer version /
unavailable where current verification required / wrong Workspace /
changed content version -- then stale ALLOW fails."), section 115
(AC-09-009 Evidence Set Fingerprint), section 116 (Evidence Relation
Versioning -- "An EvidenceRelation references exact Evidence content
version, ClaimAnchor version. If either changes: relation remains
historical, new current relation assessment required.");
07_EVIDENCE_AND_PROVENANCE.md section 8 (AC-07-001 Evidence Content
Used Consequentially Is Version-Stable); 06_BOUNDARY_ARCHITECTURE.md
section 19 (BND-013 -- "The boundary itself evaluates whether the
named DOMAIN_EVIDENCE prerequisite can be proven.").

WHY THIS MODULE PERFORMS NO I/O OF ITS OWN
--------------------------------------------------------------------
Mirrors `commit.coordinator.CurrentVersionReader`'s own split: a
generic engine has no way to know how a caller's repository is wired
(real SQLAlchemy connection in production, an in-memory double in a
unit test). `resolve_evidence_set_freshness` consumes an
`EvidenceFreshnessPort` the caller supplies (in production, a thin
wrapper around `persistence.evidence_repository.
SqlAlchemyEvidenceRepository`) and performs no database access itself.

WHY "SUPERSEDED" IS A DEDICATED PORT METHOD, NOT A NEW TABLE/INDEX
--------------------------------------------------------------------
`Evidence.supersedes_evidence_id` already exists (PKG-16) and already
implies its own inverse ("is this evidence_id superseded BY some other
row") is answerable with a plain `SELECT ... WHERE supersedes_evidence_id
= :id LIMIT 1` against the existing `evidence` table -- no new column,
index, or migration is required (14 PKG-17 DATABASE_CHANGES: "none").
`EvidenceFreshnessPort.find_superseding_evidence_id` names this read
explicitly rather than overloading `get_evidence` to hide a second
query inside it.

WHY CLAIM-ANCHOR TARGET-VERSION DRIFT IS CALLER-SUPPLIED, NOT
RESOLVED HERE
--------------------------------------------------------------------
A `ClaimAnchor.target_type`/`target_id` pair is deliberately
polymorphic (PKG-16: "no FK") -- this module has no generic way to
dispatch "read the current version of an arbitrary target type" any
more than `commit.coordinator.CurrentVersionReader` does for
`target_refs` (that dispatch is the CALLER's job, per opaque
`target_ref` strings, one layer up). `current_target_versions` is an
optional caller-supplied `{ClaimAnchorId: RecordVersion | None}`
mapping for exactly the targets a real caller has already resolved by
other means; a `ClaimAnchorId` absent from that mapping is honestly
treated as "drift not checked" (the anchor's own continued existence
is still verified), not silently assumed current. No concrete Command
supplies this mapping yet (14 PKG-17 COMMANDS: NOT_APPLICABLE) --
disclosed as a `KNOWN_LIMITATION`, matching PKG-16's own
`test_stale_claim_anchor_target_version_is_detectable_by_comparison`
disclosure that the comparison is "structurally possible for a future
consumer", not yet wired to a concrete target type.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from semantic_types.ids import ClaimAnchorId, EvidenceId, EvidenceSetId, WorkspaceId
from semantic_types.versions import RecordVersion

from evidence.claim_anchor import ClaimAnchor
from evidence.evidence_set import EvidenceSetReference
from evidence.models import Evidence, EvidenceValidationState


class EvidenceMemberFreshness(Enum):
    """09 section 114's own 5 stale conditions, plus one defense-in-depth
    outcome (`MEMBER_NOT_FOUND`) 114 does not name but 06 section 19's
    own FAILURE BEHAVIOR ("fail closed when Evidence is required and
    validity cannot be proven") requires for a forged/vanished ref.
    """

    FRESH = "FRESH"
    MEMBER_NOT_FOUND = "MEMBER_NOT_FOUND"
    WRONG_WORKSPACE = "WRONG_WORKSPACE"
    INVALIDATED = "INVALIDATED"
    UNAVAILABLE = "UNAVAILABLE"
    CONTENT_VERSION_CHANGED = "CONTENT_VERSION_CHANGED"
    SUPERSEDED = "SUPERSEDED"


class ClaimAnchorFreshness(Enum):
    """09 section 116's own ClaimAnchor-version-drift concern, resolved
    to the extent a caller-supplied current target version is
    available (see module docstring).
    """

    CURRENT = "CURRENT"
    CLAIM_ANCHOR_NOT_FOUND = "CLAIM_ANCHOR_NOT_FOUND"
    TARGET_VERSION_DRIFTED = "TARGET_VERSION_DRIFTED"


@dataclass(frozen=True, slots=True)
class EvidenceMemberFreshnessResult:
    evidence_id: EvidenceId
    expected_content_version: RecordVersion
    outcome: EvidenceMemberFreshness


@dataclass(frozen=True, slots=True)
class ClaimAnchorFreshnessResult:
    claim_anchor_id: ClaimAnchorId
    outcome: ClaimAnchorFreshness


@dataclass(frozen=True, slots=True)
class EvidenceSetFreshnessResult:
    """The one structured verdict both BND-013 (prepare-time) and the
    BND-014 commit-freshness linkage (commit-time) consume -- the same
    resolution function, invoked twice at two different moments, is
    what proves "stale Evidence fails" whether the staleness appears
    before or after the initial evaluation (06 section 19's own
    ESCALATE/DENY split does not apply here: this is a pure fact
    resolution, not itself a boundary decision).
    """

    evidence_set_ref_id: EvidenceSetId
    evidence_set_found: bool
    members: tuple[EvidenceMemberFreshnessResult, ...]
    claim_anchors: tuple[ClaimAnchorFreshnessResult, ...]

    @property
    def is_fresh(self) -> bool:
        return (
            self.evidence_set_found
            and all(m.outcome is EvidenceMemberFreshness.FRESH for m in self.members)
            and all(c.outcome is ClaimAnchorFreshness.CURRENT for c in self.claim_anchors)
        )

    @property
    def stale_refs(self) -> tuple[str, ...]:
        refs = [
            f"evidence:{m.evidence_id.value}:{m.outcome.value}"
            for m in self.members
            if m.outcome is not EvidenceMemberFreshness.FRESH
        ]
        refs += [
            f"claim_anchor:{c.claim_anchor_id.value}:{c.outcome.value}"
            for c in self.claim_anchors
            if c.outcome is not ClaimAnchorFreshness.CURRENT
        ]
        return tuple(sorted(refs))


@runtime_checkable
class EvidenceFreshnessPort(Protocol):
    """Caller-supplied fresh reads. `persistence.evidence_repository.
    SqlAlchemyEvidenceRepository` already satisfies the first four
    methods structurally; `find_superseding_evidence_id` is this
    package's own addition to that repository (see module docstring).
    """

    def get_evidence_set_reference(
        self, evidence_set_ref_id: EvidenceSetId
    ) -> EvidenceSetReference | None: ...
    def get_evidence(self, evidence_id: EvidenceId) -> Evidence | None: ...
    def find_superseding_evidence_id(self, evidence_id: EvidenceId) -> EvidenceId | None: ...
    def get_claim_anchor(self, claim_anchor_id: ClaimAnchorId) -> ClaimAnchor | None: ...


def resolve_evidence_set_freshness(
    evidence_set_ref_id: EvidenceSetId,
    *,
    workspace_id: WorkspaceId,
    reader: EvidenceFreshnessPort,
    current_target_versions: Mapping[ClaimAnchorId, RecordVersion | None] | None = None,
) -> EvidenceSetFreshnessResult:
    """Re-resolve, from current authoritative state, whether every
    member of the named EvidenceSetReference (and every ClaimAnchor it
    references) is still exactly what it was when the set was
    captured. Called once by BND-013 at prepare-time and again,
    independently, by the BND-014 commit-freshness linkage --
    duplicating the read is deliberate (see `boundaries.bnd_014_commit`'s
    own module docstring for the identical precedent with authority).
    """
    evidence_set = reader.get_evidence_set_reference(evidence_set_ref_id)
    if evidence_set is None:
        return EvidenceSetFreshnessResult(
            evidence_set_ref_id=evidence_set_ref_id,
            evidence_set_found=False,
            members=(),
            claim_anchors=(),
        )

    member_results = tuple(
        EvidenceMemberFreshnessResult(
            evidence_id=member.evidence_id,
            expected_content_version=member.content_version,
            outcome=_resolve_member(
                member.evidence_id, member.content_version, workspace_id, reader
            ),
        )
        for member in evidence_set.member_evidence_id_and_version_list
    )

    versions = current_target_versions or {}
    anchor_results = tuple(
        _resolve_claim_anchor(claim_anchor_id, reader, versions)
        for claim_anchor_id in evidence_set.claim_anchor_refs
    )

    return EvidenceSetFreshnessResult(
        evidence_set_ref_id=evidence_set_ref_id,
        evidence_set_found=True,
        members=member_results,
        claim_anchors=anchor_results,
    )


def resolve_evidence_relation_freshness(
    *,
    evidence_id: EvidenceId,
    evidence_content_version: RecordVersion,
    workspace_id: WorkspaceId,
    reader: EvidenceFreshnessPort,
) -> EvidenceMemberFreshness:
    """09 section 116: "An EvidenceRelation references exact Evidence
    content version... If either changes: relation remains historical,
    new current relation assessment required." Mandatory adversarial
    attack "EvidenceRelation changed": exposed independently of
    `resolve_evidence_set_freshness` because an `EvidenceRelation`
    (07 section 11) is not itself a member of any
    `EvidenceSetReference` -- 09 section 45's own EvidenceSetReference
    field list carries `member_evidence_id_and_version_list` (Evidence)
    plus `claim_anchor_refs`, never a relation identity.
    """
    return _resolve_member(evidence_id, evidence_content_version, workspace_id, reader)


def _resolve_member(
    evidence_id: EvidenceId,
    expected_content_version: RecordVersion,
    workspace_id: WorkspaceId,
    reader: EvidenceFreshnessPort,
) -> EvidenceMemberFreshness:
    current = reader.get_evidence(evidence_id)
    if current is None:
        return EvidenceMemberFreshness.MEMBER_NOT_FOUND
    if current.workspace_id != workspace_id:
        return EvidenceMemberFreshness.WRONG_WORKSPACE
    if current.validation_state is EvidenceValidationState.INVALIDATED:
        return EvidenceMemberFreshness.INVALIDATED
    if current.validation_state is EvidenceValidationState.UNAVAILABLE:
        return EvidenceMemberFreshness.UNAVAILABLE
    if current.content_version != expected_content_version:
        return EvidenceMemberFreshness.CONTENT_VERSION_CHANGED
    if reader.find_superseding_evidence_id(evidence_id) is not None:
        return EvidenceMemberFreshness.SUPERSEDED
    return EvidenceMemberFreshness.FRESH


def _resolve_claim_anchor(
    claim_anchor_id: ClaimAnchorId,
    reader: EvidenceFreshnessPort,
    current_target_versions: Mapping[ClaimAnchorId, RecordVersion | None],
) -> ClaimAnchorFreshnessResult:
    anchor = reader.get_claim_anchor(claim_anchor_id)
    if anchor is None:
        return ClaimAnchorFreshnessResult(
            claim_anchor_id, ClaimAnchorFreshness.CLAIM_ANCHOR_NOT_FOUND
        )
    if claim_anchor_id in current_target_versions:
        current_version = current_target_versions[claim_anchor_id]
        if current_version != anchor.target_content_version:
            return ClaimAnchorFreshnessResult(
                claim_anchor_id, ClaimAnchorFreshness.TARGET_VERSION_DRIFTED
            )
    return ClaimAnchorFreshnessResult(claim_anchor_id, ClaimAnchorFreshness.CURRENT)


__all__ = [
    "EvidenceMemberFreshness",
    "ClaimAnchorFreshness",
    "EvidenceMemberFreshnessResult",
    "ClaimAnchorFreshnessResult",
    "EvidenceSetFreshnessResult",
    "EvidenceFreshnessPort",
    "resolve_evidence_set_freshness",
    "resolve_evidence_relation_freshness",
]
