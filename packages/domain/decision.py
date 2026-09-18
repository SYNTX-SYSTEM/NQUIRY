"""Decision canonical object and its transition topology.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §26 (Decision -- CANONICAL_DOMAIN_OBJECT,
identity via `Decision.id`, belongs to a Challenge, relates to Question/
Evidence; §26.6 GAP-02-006 explicitly defers lifecycle/authority
interaction to 03/04); 03_STATE_AND_TRANSITION_ARCHITECTURE.md §35
(Decision State Architecture -- exact 2-value vocabulary
UNDER_CONSIDERATION/DECIDED, `[ARCHITECTURAL CLOSURE]`), §36 (TRN-DEC-001
OPEN_DECISION_CONSIDERATION, TRN-DEC-002 RECORD_HUMAN_DECISION -- exact
CURRENT STATE/PRECONDITIONS/DENY CONDITION/NEXT STATE text), §37
(Decision Does Not Equal Authorized Execution); 09_DATA_EVENT_API_CONTRACTS.md
§47 (DATA CONTRACT: Decision -- exact field list).

WHY BOTH TRN-DEC-001 AND TRN-DEC-002 ARE THIS PACKAGE'S SCOPE
------------------------------------------------------------------------
14_IMPLEMENTATION_SEQUENCE.md §46's own PKG-15 manifest entry reads
"PUBLIC INTERFACES: Decision commands" (plural, unlike a single-command
package's own singular wording) and 14's own Command Registry (§12)
never assigns `CMD_OPEN_DECISION_CONSIDERATION`/TRN-DEC-001 to any
other package at all -- there is no other legitimate owner in the
32-package DAG. Without OPEN, `RecordHumanDecision` would have no
governed path to ever reach a real `UNDER_CONSIDERATION` row in
production, only a direct-SQL test fixture -- exactly the "direct
persistence" forbidden shortcut this package's own coding prompt
names. Both transitions are therefore materialized here, mirroring
`domain.session_transitions`/`domain.burst_transitions`'s own pattern
of one module owning a complete, closed transition topology.

WHY THIS IS A REAL STATE TRANSITION (UNLIKE PKG-14's QuestionSelection)
------------------------------------------------------------------------
02 §26.1 classifies Decision's own representation as
`CANONICAL_DOMAIN_OBJECT`, not `RELATION` (contrast
`domain.question_selection.QuestionSelection`, explicitly `RELATION`,
03 §39's own "state-preserving consequential mutation"). TRN-DEC-001/002
have genuine `from_state != to_state` pairs (absent -> UNDER_CONSIDERATION
-> DECIDED) -- this module therefore mirrors
`domain.burst_transitions`'s shape exactly (a closed `_BY_STATE_PAIR`
topology, default-DENY), not `domain.question_selection`'s
state-preserving-mutation shape.

WHY `decision_ref` STILL GOES IN `relation_refs`, NOT `target_refs`,
FOR THE OPEN COMMAND -- DESPITE DECISION BEING A CANONICAL OBJECT
------------------------------------------------------------------------
AC-09-001 requires an "expected current version" for every
`target_ref`, and `CommandEnvelope.__post_init__` enforces
`target_refs == expected_versions.keys()` exactly. A Decision that
does not exist yet at OPEN time has no real prior version to name as
"expected" -- the identical technical constraint
`application.question_selection_handler` already resolved for a newly
created row, regardless of that row's own domain representation label.
`application.human_decision_handler` (this package's own application
module) therefore places the Challenge (the pre-existing, read-checked
object) in `target_refs`/`expected_versions`, and the newly created
Decision's own ref in `relation_refs` via `MutationOutcome.relation_refs`
-- purely a commit-unit provenance record of what this specific
mutation created, not a claim that Decision is architecturally a
relation. For RECORD_HUMAN_DECISION, by contrast, the Decision already
exists and IS a genuine `target_ref` (its own current `record_version`
is read fresh and re-validated by BND-014, exactly like every other
existing-row mutation in this codebase).

WHY `options`/`criteria` ARE PLAIN STRING TUPLES
------------------------------------------------------------------------
02 §26.4 names `options`/`criteria` as LEVEL 1 relations without
further structure, and 09 §47's own field list gives them no
sub-schema either. Inventing a structured `Option`/`Criterion` domain
object neither source defines would be semantic invention beyond what
either architecture layer specifies; a plain `tuple[str, ...]` is the
literal, non-inventive materialization of "options" and "criteria" as
named.

WHY `decision_question_ref`/`decision_question_text` ARE TWO SEPARATE
OPTIONAL FIELDS
------------------------------------------------------------------------
09 §47's own field name is written "decision_question_ref/text" --
read literally as two possible representations of the same concept
(an existing, already-captured Question, or freeform decision-question
text not tied to any captured Question object), not a single
polymorphic field. `[IMPLEMENTATION CHOICE]`, disclosed: both are
optional and independent; nothing in 02/03/09 states one is mandatory
whenever the other is absent.

WHY `provenance_ref` STAYS A BARE OPAQUE `uuid.UUID | None`
------------------------------------------------------------------------
14 §22's own `ProvenanceEnvelope` ("hybrid typed JSONB provenance
envelope plus normalized lineage link table") is explicitly an
`[IMPLEMENTATION CHOICE]` assigned to `packages/evidence/provenance.py`
-- PKG-16, Phase 6, not yet built. "AI recommendation refs if consumed"
(14 §21) has no dedicated Decision column in 09 §47's own field list
either -- both are honestly deferred into this one opaque forward
reference, the identical disclosed treatment
`commit.coordinator.CommitUnit.commit_time_proof_ref` and
`command.envelope.CommandEnvelope.authority_context_ref` already
established for a comparable forward-reference gap. "Evidence refs if
consumed" does NOT need a Decision-level field at all: it already has
a real, existing carrier -- `CommandEnvelope.evidence_set_ref`
(PKG-10), which `commit.coordinator._commit_inner` already writes onto
the resulting `AuditEvent.evidence_set_ref` unconditionally. This
package only has to pass a caller-supplied `EvidenceSetId` through,
not build new plumbing.

WHY `confidence` IS AN OPAQUE STRING, NOT A NUMERIC SCORE
------------------------------------------------------------------------
02 §26.4 names it without a defined range or vocabulary. Inventing a
numeric scale here would be exactly the "confidence into Evidence"
collapse this package's own NON_COLLAPSE_RULES forbid materializing --
kept as an optional human-authored qualitative string, carrying no
implied sufficiency semantics of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from semantic_types.ids import (
    AuthorityBindingId,
    ChallengeId,
    DecisionId,
    QuestionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion


class DecisionState(Enum):
    """03 §35.2's exact 2-value closed vocabulary. `[ARCHITECTURAL
    CLOSURE]`. Closed -- there is no third Decision state; 03 §38
    (GAP-03-005) explicitly forbids `DECIDED -> UNDER_CONSIDERATION`
    as a silent rewrite, so this vocabulary is not extended for
    revision/supersession either.
    """

    UNDER_CONSIDERATION = "UNDER_CONSIDERATION"
    DECIDED = "DECIDED"


@dataclass(frozen=True, slots=True)
class Decision:
    """09 §47's exact field list (plus the disclosed `workspace_id`
    technical necessity every other protected object in this codebase
    already carries). Frozen: 14 §3.1 gives `domain` no canonical
    write capability -- a changed Decision is a new `Decision` value
    produced by a governed CommitUnit, never an in-place edit.
    """

    decision_id: DecisionId
    workspace_id: WorkspaceId
    challenge_id: ChallengeId
    decision_question_ref: QuestionId | None
    decision_question_text: str | None
    options: tuple[str, ...]
    criteria: tuple[str, ...]
    selected_option: str | None
    rationale: str | None
    confidence: str | None
    state: DecisionState
    opened_by_user_id: UserId
    decision_authority_binding_id: AuthorityBindingId
    decided_by_user_id: UserId | None
    created_at: datetime
    decided_at: datetime | None
    record_version: RecordVersion
    provenance_ref: UUID | None

    def __post_init__(self) -> None:
        if not isinstance(self.decision_id, DecisionId):
            raise TypeError(f"decision_id must be a DecisionId, got {type(self.decision_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.challenge_id, ChallengeId):
            raise TypeError(f"challenge_id must be a ChallengeId, got {type(self.challenge_id)!r}")
        if self.decision_question_ref is not None and not isinstance(
            self.decision_question_ref, QuestionId
        ):
            raise TypeError("decision_question_ref must be a QuestionId or None")
        if not isinstance(self.state, DecisionState):
            raise TypeError(f"state must be a DecisionState, got {type(self.state)!r}")
        if not isinstance(self.opened_by_user_id, UserId):
            raise TypeError(
                f"opened_by_user_id must be a UserId, got {type(self.opened_by_user_id)!r}"
            )
        if not isinstance(self.decision_authority_binding_id, AuthorityBindingId):
            raise TypeError(
                "decision_authority_binding_id must be an AuthorityBindingId, "
                f"got {type(self.decision_authority_binding_id)!r}"
            )
        if self.decided_by_user_id is not None and not isinstance(self.decided_by_user_id, UserId):
            raise TypeError("decided_by_user_id must be a UserId or None")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        # Mandatory-category adversarial attack: unattributed Decision.
        # A DECIDED Decision with no attributed decider is exactly the
        # "apparently DECIDED record without provable human authority"
        # 03 TRN-DEC-002's own RECOVERY/ROLLBACK REQUIREMENT forbids.
        if self.state is DecisionState.DECIDED and self.decided_by_user_id is None:
            raise ValueError("a DECIDED Decision must carry decided_by_user_id")
        if self.state is DecisionState.DECIDED and self.decided_at is None:
            raise ValueError("a DECIDED Decision must carry decided_at")
        if self.state is DecisionState.DECIDED and self.selected_option is None:
            raise ValueError("a DECIDED Decision must carry selected_option")
        if self.state is DecisionState.UNDER_CONSIDERATION and self.decided_by_user_id is not None:
            raise ValueError("an UNDER_CONSIDERATION Decision must not carry decided_by_user_id")


class DecisionTransitionId(Enum):
    """03 §36's two named transition identifiers. Closed."""

    TRN_DEC_001 = "TRN-DEC-001"
    TRN_DEC_002 = "TRN-DEC-002"


class DecisionOperation(Enum):
    """The `REQUESTED TRANSITION` name each 03 §36 contract carries."""

    OPEN_DECISION_CONSIDERATION = "OPEN_DECISION_CONSIDERATION"
    RECORD_HUMAN_DECISION = "RECORD_HUMAN_DECISION"


class DecisionTransitionVerdict(Enum):
    """Outcome of the topology evaluation. Default-DENY, identical
    vocabulary shape to `SessionTransitionVerdict`/`BurstTransitionVerdict`.
    """

    STATE_ELIGIBLE = "STATE_ELIGIBLE"
    DENIED_UNKNOWN_TRANSITION = "DENIED_UNKNOWN_TRANSITION"
    DENIED_ILLEGAL_TRANSITION = "DENIED_ILLEGAL_TRANSITION"
    DENIED_TERMINAL_STATE = "DENIED_TERMINAL_STATE"
    DENIED_DECISION_ALREADY_EXISTS = "DENIED_DECISION_ALREADY_EXISTS"


@dataclass(frozen=True, slots=True)
class DecisionTransitionResolution:
    verdict: DecisionTransitionVerdict
    current_state: DecisionState | None
    requested: str

    @property
    def is_state_eligible(self) -> bool:
        return self.verdict is DecisionTransitionVerdict.STATE_ELIGIBLE


_TERMINAL_DECISION_STATES: frozenset[DecisionState] = frozenset()
"""03 §38 (GAP-03-005) forbids `DECIDED -> UNDER_CONSIDERATION` as a
silent rewrite, but does not declare `DECIDED` terminal in the sense
`BurstState`'s own `TERMINAL_BURST_STATES` uses (no further Decision
transition of any kind is defined at all past `DECIDED` -- there is
simply no third state or contract to transition to). Kept as an empty,
explicit set rather than omitted, so a future amendment introducing a
real post-DECIDED transition finds an intentional, documented starting
point rather than an implicit gap.
"""


def resolve_decision_transition_to_state(
    *, current_state: DecisionState | None, target_state: DecisionState
) -> DecisionTransitionResolution:
    """Evaluate a request expressed as a desired target state --
    mirrors `domain.burst_transitions.resolve_burst_transition_to_state`
    exactly, including why an unmatched pair means illegal, never
    "unknown" (a target *state* is always a real `DecisionState`).
    """
    requested = target_state.value
    if current_state is not None and current_state in _TERMINAL_DECISION_STATES:
        return DecisionTransitionResolution(
            verdict=DecisionTransitionVerdict.DENIED_TERMINAL_STATE,
            current_state=current_state,
            requested=requested,
        )
    if current_state is None and target_state is DecisionState.UNDER_CONSIDERATION:
        return DecisionTransitionResolution(
            verdict=DecisionTransitionVerdict.STATE_ELIGIBLE,
            current_state=current_state,
            requested=requested,
        )
    if current_state is DecisionState.UNDER_CONSIDERATION and target_state is DecisionState.DECIDED:
        return DecisionTransitionResolution(
            verdict=DecisionTransitionVerdict.STATE_ELIGIBLE,
            current_state=current_state,
            requested=requested,
        )
    if current_state is None:
        # Mandatory-category adversarial attack: state skip -- attempting
        # RECORD_HUMAN_DECISION with no prior OPEN_DECISION_CONSIDERATION.
        return DecisionTransitionResolution(
            verdict=DecisionTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    if current_state is DecisionState.UNDER_CONSIDERATION and target_state is (
        DecisionState.UNDER_CONSIDERATION
    ):
        # Mandatory-category adversarial attack: a second
        # OPEN_DECISION_CONSIDERATION against an already-open Decision.
        return DecisionTransitionResolution(
            verdict=DecisionTransitionVerdict.DENIED_DECISION_ALREADY_EXISTS,
            current_state=current_state,
            requested=requested,
        )
    return DecisionTransitionResolution(
        verdict=DecisionTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
        current_state=current_state,
        requested=requested,
    )


def challenge_target_ref(challenge_id: ChallengeId) -> str:
    """The `CommandEnvelope.target_refs`/`CurrentVersionReader` ref
    string naming a Challenge as a commit-sensitive (read-only, never
    written by this package) target for `OpenDecisionConsideration` --
    shared by `application.human_decision_handler` (builds the
    envelope) and `persistence.challenge_repository` (reads the live
    version for it), mirroring `domain.question_selection.session_target_ref`'s
    own precedent (PKG-14) exactly: the helper lives with the package
    whose command consumes the ref, not with the referenced object's
    own owning package.
    """
    return f"challenge:{challenge_id.value}"


def decision_target_ref(decision_id: DecisionId) -> str:
    """The ref string naming a Decision as a commit-sensitive target
    for `RecordHumanDecision` (the Decision already exists at that
    point and its own `record_version` is genuinely re-validated by
    BND-014 -- unlike `OpenDecisionConsideration`, where the
    newly-created Decision's ref goes in `relation_refs` instead, see
    module docstring).
    """
    return f"decision:{decision_id.value}"


__all__ = [
    "DecisionState",
    "Decision",
    "DecisionTransitionId",
    "DecisionOperation",
    "DecisionTransitionVerdict",
    "DecisionTransitionResolution",
    "resolve_decision_transition_to_state",
    "challenge_target_ref",
    "decision_target_ref",
]
