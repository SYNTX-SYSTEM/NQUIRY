"""Evidence and SourceReference: the two root constructs of Evidence
core.

Source: 07_EVIDENCE_AND_PROVENANCE.md section 2 (Evidence Classes --
"The approved evidence classes remain: SYSTEM_PROOF, DOMAIN_EVIDENCE,
AI_VALIDATION_PROOF... not interchangeable"), section 6 (Evidence
Validation State Semantics -- exact 4-value vocabulary, also
14_IMPLEMENTATION_SEQUENCE.md section 6's own "Evidence validation"
closed-vocabulary entry), section 7 (Evidence Validation Transitions),
section 8 (AC-07-001 Evidence Content Used Consequentially Is
Version-Stable), section 9 (Source Reference Architecture), section 24
(Provenance Origin Classes -- "LEVEL 1 requires distinction among:
human, ai, imported, inferred... 07 additionally uses: system-derived");
09_DATA_EVENT_API_CONTRACTS.md section 40 (DATA CONTRACT:
SourceReference -- exact field list), section 41 (DATA CONTRACT:
Evidence -- exact field list).

WHY `EvidenceType` IS A CLOSED ENUM DESPITE NOT APPEARING IN 14 SECTION
6's OWN CLOSED-VOCABULARIES TABLE
------------------------------------------------------------------------
14 section 6 lists "Evidence validation" and "EvidenceRelation
assessment" explicitly, but not "Evidence type"/"Evidence class". 07
section 2's own language is nonetheless unambiguously closed ("The
approved evidence classes REMAIN..."), unlike the softer "examples"/
"may include" language 07 uses for `source_type` (section 9) and
`SourceReference.validation_status` (09 section 40.1: "Example
technical states"). This module therefore materializes exactly two
closed enums grounded in 14 section 6's own table
(`EvidenceValidationState`) and in 07 section 2's equally definitive
language (`EvidenceType`), while leaving `source_type` and
`validation_status` as plain, unconstrained strings -- disclosed
explicitly per field below, not silently narrowed to a guessed set 14
never approved.

WHY `ProvenanceOrigin` HAS 5 VALUES, NOT `domain.question.QuestionOrigin`'s
4
------------------------------------------------------------------------
07 section 24 states LEVEL 1's own 4 categories (human, ai, imported,
inferred) -- exactly `domain.question.QuestionOrigin`'s own closed set,
confirming that enum already materializes this same LEVEL-1 list for
Question capture specifically. 07 section 24 then adds a 5th value,
`system-derived`, "for operational/proof artifacts where origin is
deterministic System computation rather than domain content" --
explicitly required for `SYSTEM_PROOF`/`AI_VALIDATION_PROOF` typed
Evidence and for `SourceReference`/`EvidenceRelation`'s own `origin`
fields (09 sections 40/44). Extending or importing `QuestionOrigin`
here would either invent a 5th value onto a predecessor's own closed
type (not this package's file to widen) or under-represent Evidence's
own origin space. A new, separate `ProvenanceOrigin` enum is the
literal, non-inventive materialization of 07 section 24's own text.

WHY `Evidence` HAS NO `origin` COLUMN OF ITS OWN
------------------------------------------------------------------------
07 section 5.4 describes "Evidence origin" conceptually, but 09 section
41's own field list -- the actual schema authority -- does not include
an `origin` column on `Evidence` at all. `human_source_user_id`
(non-null implies human origin), `source_reference_id` (non-null
implies an external/imported source), and `provenance_ref` (the
eventual structured origin record, PKG-16's own opaque forward
reference here) already carry this information without a redundant,
separately-drifting closed-vocabulary column 09 itself never names.

WHY `content_version` IS SET ONCE AND NEVER CHANGES, DISTINCT FROM
`record_version`
------------------------------------------------------------------------
AC-07-001: "Once Evidence content has been consumed... the exact
consumed Evidence representation must remain reconstructable... Change
is represented through: new version / new Evidence identity." Evidence
CONTENT therefore never changes in place -- a content change is always
a new `Evidence` row linked via `supersedes_evidence_id`.
`content_version` exists purely so `EvidenceRelation.evidence_content_version`
(09 section 44) has something concrete to pin against, the same "exact
version consumed" pattern `ClaimAnchor.target_content_version` already
uses for its own target. `record_version` remains the generic
optimistic-concurrency counter, which DOES legitimately advance on
`validation_state` transitions (07 section 7) -- a real, in-place
metadata mutation distinct from content change.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from semantic_types.ids import EvidenceId, SourceReferenceId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion


class EvidenceType(Enum):
    """07 section 2's exact 3-value closed vocabulary. Closed -- "They
    are not interchangeable."
    """

    SYSTEM_PROOF = "SYSTEM_PROOF"
    DOMAIN_EVIDENCE = "DOMAIN_EVIDENCE"
    AI_VALIDATION_PROOF = "AI_VALIDATION_PROOF"


class EvidenceValidationState(Enum):
    """14 section 6's exact 4-value closed vocabulary ("Evidence
    validation"), matching 07 section 6/09 section 41 verbatim.
    """

    UNVALIDATED = "UNVALIDATED"
    STRUCTURALLY_VALID = "STRUCTURALLY_VALID"
    INVALIDATED = "INVALIDATED"
    UNAVAILABLE = "UNAVAILABLE"


_LEGAL_VALIDATION_TRANSITIONS: frozenset[
    tuple[EvidenceValidationState, EvidenceValidationState]
] = frozenset(
    {
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.STRUCTURALLY_VALID),
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.INVALIDATED),
        (EvidenceValidationState.UNVALIDATED, EvidenceValidationState.UNAVAILABLE),
        (EvidenceValidationState.STRUCTURALLY_VALID, EvidenceValidationState.INVALIDATED),
        (EvidenceValidationState.STRUCTURALLY_VALID, EvidenceValidationState.UNAVAILABLE),
        (EvidenceValidationState.UNAVAILABLE, EvidenceValidationState.STRUCTURALLY_VALID),
        (EvidenceValidationState.UNAVAILABLE, EvidenceValidationState.INVALIDATED),
    }
)
"""07 section 7's exact transition table, transcribed. `INVALIDATED` is
terminal -- "not silently returned to STRUCTURALLY_VALID"; correction
requires a new Evidence/version or an explicit 10-owned recovery, both
out of this package's scope.
"""


def is_legal_validation_transition(
    current: EvidenceValidationState, target: EvidenceValidationState
) -> bool:
    """Pure topology check, mirroring `domain.burst_transitions`'s own
    "no state skip" discipline -- used by the persistence layer's own
    DB trigger design and by this package's own tests, not by any
    boundary (BND-013 itself is PKG-17's own scope; this package only
    "prepares BND-013 facts", 14 PKG-16 BOUNDARIES).
    """
    return (current, target) in _LEGAL_VALIDATION_TRANSITIONS


class ProvenanceOrigin(Enum):
    """07 section 24's exact 5-value closed vocabulary: LEVEL 1's own
    4 categories (matching `domain.question.QuestionOrigin` exactly)
    plus `SYSTEM_DERIVED` for operational/proof artifacts. See module
    docstring for why this is a new, separate enum rather than
    extending or importing `QuestionOrigin`.
    """

    HUMAN = "HUMAN"
    AI = "AI"
    IMPORTED = "IMPORTED"
    INFERRED = "INFERRED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"


@dataclass(frozen=True, slots=True)
class SourceReference:
    """09 section 40's exact field list. `source_type` and
    `validation_status` are deliberately plain strings, not closed
    enums -- see module docstring for why 07/09's own "example"/"may
    include" language for these two fields does not rise to the same
    closure 14 section 6 or 07 section 2 give the enums this package
    does materialize.
    """

    source_reference_id: SourceReferenceId
    workspace_id: WorkspaceId
    source_type: str
    locator: str
    external_id: str | None
    title: str | None
    retrieved_at: datetime | None
    source_published_at: datetime | None
    content_fingerprint: str | None
    snapshot_ref: str | None
    created_by_ref: str
    origin: ProvenanceOrigin
    validation_status: str
    created_at: datetime
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.source_reference_id, SourceReferenceId):
            raise TypeError(
                "source_reference_id must be a SourceReferenceId, "
                f"got {type(self.source_reference_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.source_type:
            raise ValueError("SourceReference.source_type must be non-empty")
        if not self.locator:
            raise ValueError("SourceReference.locator must be non-empty")
        if not self.created_by_ref:
            raise ValueError("SourceReference.created_by_ref must be non-empty")
        if not isinstance(self.origin, ProvenanceOrigin):
            raise TypeError(f"origin must be a ProvenanceOrigin, got {type(self.origin)!r}")
        if not self.validation_status:
            raise ValueError("SourceReference.validation_status must be non-empty")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )


@dataclass(frozen=True, slots=True)
class Evidence:
    """09 section 41's exact field list. Frozen: 14 section 3.1 gives
    `evidence` no canonical write capability of its own ("canonical
    write: only through CommitUnit") -- a validation-state transition
    or supersession is a new value produced by a governed write, never
    an in-place Python mutation.
    """

    evidence_id: EvidenceId
    workspace_id: WorkspaceId
    type: EvidenceType
    content: str
    source_reference_id: SourceReferenceId | None
    human_source_user_id: UserId | None
    reliability: str | None
    captured_at: datetime
    validation_state: EvidenceValidationState
    content_version: RecordVersion
    record_version: RecordVersion
    supersedes_evidence_id: EvidenceId | None
    provenance_ref: UUID | None

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, EvidenceId):
            raise TypeError(f"evidence_id must be an EvidenceId, got {type(self.evidence_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.type, EvidenceType):
            raise TypeError(f"type must be an EvidenceType, got {type(self.type)!r}")
        if not self.content:
            raise ValueError("Evidence.content must be non-empty")
        if self.source_reference_id is not None and not isinstance(
            self.source_reference_id, SourceReferenceId
        ):
            raise TypeError("source_reference_id must be a SourceReferenceId or None")
        if self.human_source_user_id is not None and not isinstance(
            self.human_source_user_id, UserId
        ):
            raise TypeError("human_source_user_id must be a UserId or None")
        if not isinstance(self.validation_state, EvidenceValidationState):
            raise TypeError(
                "validation_state must be an EvidenceValidationState, "
                f"got {type(self.validation_state)!r}"
            )
        if not isinstance(self.content_version, RecordVersion):
            raise TypeError(
                f"content_version must be a RecordVersion, got {type(self.content_version)!r}"
            )
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if self.supersedes_evidence_id is not None and not isinstance(
            self.supersedes_evidence_id, EvidenceId
        ):
            raise TypeError("supersedes_evidence_id must be an EvidenceId or None")
        # Mandatory-category adversarial attack: self-supersession.
        if (
            self.supersedes_evidence_id is not None
            and self.supersedes_evidence_id == self.evidence_id
        ):
            raise ValueError("Evidence cannot supersede itself")


__all__ = [
    "EvidenceType",
    "EvidenceValidationState",
    "is_legal_validation_transition",
    "ProvenanceOrigin",
    "SourceReference",
    "Evidence",
]
