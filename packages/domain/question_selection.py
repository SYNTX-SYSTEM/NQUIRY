"""QuestionSelection relation and its state-preserving transition topology.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §18 (Classification: RELATION,
not a standalone object; endpoints Session -> selects -> Question;
selection semantics distinguish "compelling" from "primary"), §47.3
(representation: relation); 09_DATA_EVENT_API_CONTRACTS.md §33 (DATA
CONTRACT: QuestionSelection -- exact field list, minimum selection
types COMPELLING/PRIMARY); 03_STATE_AND_TRANSITION_ARCHITECTURE.md §39
(TRN-SEL-001 SELECT_COMPELLING_QUESTION, TRN-SEL-002
SELECT_PRIMARY_QUESTION -- "QuestionSelection is a relation, not a
state. Creating it is consequential."); 04_AUTHORITY_AND_DECISION_RIGHTS.md
§41-42 (AUTH-DEP-SEL-001/002 -- AUTHORITY PRECONDITIONS: "Session
QUESTION_SELECTION", "Question belongs to Session Challenge").

WHY THIS IS "STATE-PRESERVING", NOT A TRANSITION LIKE SESSION/BURST
--------------------------------------------------------------------
03 §39's own title is "Question Selection as State-Preserving
Consequential Mutation": both TRN-SEL-001 and TRN-SEL-002 keep the
Session in `QUESTION_SELECTION` (`NEXT STATE: Session remains
QUESTION_SELECTION`) -- there is no `from_state != to_state` pair the
way `session_transitions`/`burst_transitions` model. 06 §13's own
BND-007 REQUESTED OPERATION line reads "One specific 03 transition OR
state-preserving consequential mutation" (transcribed verbatim) --
this module materializes the second half of that disjunction, not a
weaker version of the first. `SelectionTransitionResolution` mirrors
`SessionTransitionResolution`/`BurstTransitionResolution`'s public
shape (`.verdict`, `.is_state_eligible`, `.requested`) precisely so it
can be added as a third member of `boundaries.bnd_007_state_transition.
Bnd007Input.resolution`'s tagged union without changing that
evaluator's own algebra.

WHAT THIS RESOLUTION CHECKS, AND WHAT IT DELIBERATELY DOES NOT
------------------------------------------------------------------
06 §13's own VALIDATION list includes "current state exact" and
"cross-object state invariant valid" -- this module checks exactly
those two facts: the Session is currently `QUESTION_SELECTION`, and the
candidate Question's `challenge_id` matches the Session's own
`challenge_id` (04 §41 AUTHORITY PRECONDITIONS: "Question belongs to
Session Challenge"; TRN-SEL-001 DENY CONDITION: "Question belongs to
another Workspace/Challenge" -- the Workspace half is BND-002's own
job, not duplicated here).

What this module does NOT check: selection-cardinality rules (1-3
compelling, at most one primary without governed replacement). Those
depend on how many `QuestionSelection` rows already exist for the
Session -- repository state, not Session/Question state *topology* --
and are enforced transactionally at the persistence layer
(`persistence.question_selection_repository`), the same "repository
raises a named conflict exception, caught by CommitCoordinator's
generic rollback" pattern `BurstRepository.start`/`BurstConflict`
already established (PKG-07/PKG-13).

WHY `SelectionType` LIVES HERE, NOT AS A THIRD FILE
------------------------------------------------------------
09 §33's "Minimum selection types" (COMPELLING, PRIMARY) are exactly
two closed values attached to exactly one relation -- there is no
independent semantic role for the vocabulary the way `BurstMode`
justified its own concern inside `domain.burst`. It stays with the
`QuestionSelection` dataclass it types, the same locality
`domain.burst`'s own `BurstState`/`BurstMode` pair already uses.

WHY `QuestionSelection` CARRIES `workspace_id`
------------------------------------------------------------
Same disclosed technical necessity as `QuestionBurstMembership`
(PKG-07) and `Question`/`Session` themselves: 14 §49's "workspace_id on
protected records: S" pattern, needed for the composite-FK
Workspace-confinement the migration applies. 09 §33's own field list
does not name it explicitly; it is added for the same reason those
other packages added it, not as a departure from the contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import (
    AuthorityBindingId,
    ChallengeId,
    QuestionId,
    QuestionSelectionId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from domain.session import SessionState


class SelectionType(Enum):
    """09 §33's exact 2-value closed vocabulary. Closed -- there is no
    third selection type, and 09 §33.2's own "Collaborative Gap"
    (`GAP-04-001`) is explicitly a conflict-*policy* gap, never license
    to invent a third value here.
    """

    COMPELLING = "COMPELLING"
    PRIMARY = "PRIMARY"


@dataclass(frozen=True, slots=True)
class QuestionSelection:
    """09 §33's exact field list (plus the disclosed `workspace_id`
    technical necessity -- see module docstring). Frozen: 14 §3.1 gives
    `domain` no canonical write capability, and 09 §33.1 states the
    relation's own binding reference "does not authorize future
    changes" -- there is no legitimate mutation of an existing
    selection row, only creation of a new one.
    """

    question_selection_id: QuestionSelectionId
    workspace_id: WorkspaceId
    session_id: SessionId
    question_id: QuestionId
    selection_type: SelectionType
    selected_by_user_id: UserId
    human_authority_binding_id: AuthorityBindingId
    selected_at: datetime
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.question_selection_id, QuestionSelectionId):
            raise TypeError(
                "question_selection_id must be a QuestionSelectionId, "
                f"got {type(self.question_selection_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.session_id, SessionId):
            raise TypeError(f"session_id must be a SessionId, got {type(self.session_id)!r}")
        if not isinstance(self.question_id, QuestionId):
            raise TypeError(f"question_id must be a QuestionId, got {type(self.question_id)!r}")
        if not isinstance(self.selection_type, SelectionType):
            raise TypeError(
                f"selection_type must be a SelectionType, got {type(self.selection_type)!r}"
            )
        if not isinstance(self.selected_by_user_id, UserId):
            raise TypeError(
                f"selected_by_user_id must be a UserId, got {type(self.selected_by_user_id)!r}"
            )
        if not isinstance(self.human_authority_binding_id, AuthorityBindingId):
            raise TypeError(
                "human_authority_binding_id must be an AuthorityBindingId, "
                f"got {type(self.human_authority_binding_id)!r}"
            )
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )


class SelectionTransitionId(Enum):
    """03 §39's two named transition identifiers. Closed."""

    TRN_SEL_001 = "TRN-SEL-001"
    TRN_SEL_002 = "TRN-SEL-002"


class SelectionOperation(Enum):
    """The `REQUESTED TRANSITION` name each 03 §39 contract carries."""

    SELECT_COMPELLING_QUESTION = "SELECT_COMPELLING_QUESTION"
    SELECT_PRIMARY_QUESTION = "SELECT_PRIMARY_QUESTION"


_TRANSITION_OPERATIONS = {
    SelectionTransitionId.TRN_SEL_001: SelectionOperation.SELECT_COMPELLING_QUESTION,
    SelectionTransitionId.TRN_SEL_002: SelectionOperation.SELECT_PRIMARY_QUESTION,
}


class SelectionTransitionVerdict(Enum):
    """Outcome of the state-preserving-mutation topology evaluation.
    Default-DENY, same vocabulary shape as `SessionTransitionVerdict`/
    `BurstTransitionVerdict`.
    """

    STATE_ELIGIBLE = "STATE_ELIGIBLE"
    DENIED_WRONG_SESSION_STATE = "DENIED_WRONG_SESSION_STATE"
    DENIED_QUESTION_WRONG_CHALLENGE = "DENIED_QUESTION_WRONG_CHALLENGE"


@dataclass(frozen=True, slots=True)
class SelectionTransitionResolution:
    verdict: SelectionTransitionVerdict
    current_session_state: SessionState
    requested: str

    @property
    def is_state_eligible(self) -> bool:
        return self.verdict is SelectionTransitionVerdict.STATE_ELIGIBLE


def resolve_selection_transition(
    *,
    transition_id: SelectionTransitionId,
    current_session_state: SessionState,
    session_challenge_id: ChallengeId,
    question_challenge_id: ChallengeId,
) -> SelectionTransitionResolution:
    """Evaluate the two 03 §39 cross-object/state-topology facts a
    state-preserving QuestionSelection mutation requires. Cardinality
    (1-3 compelling, at most one primary) is deliberately NOT checked
    here -- see module docstring.
    """
    requested = _TRANSITION_OPERATIONS[transition_id].value

    if current_session_state is not SessionState.QUESTION_SELECTION:
        return SelectionTransitionResolution(
            verdict=SelectionTransitionVerdict.DENIED_WRONG_SESSION_STATE,
            current_session_state=current_session_state,
            requested=requested,
        )
    if question_challenge_id != session_challenge_id:
        # Mandatory-category adversarial attack: wrong Workspace/Challenge
        # -- here in its "same Workspace, different Challenge" shape
        # (TRN-SEL-001 DENY CONDITION: "Question belongs to another
        # Workspace/Challenge"). The Workspace half is BND-002's own job.
        return SelectionTransitionResolution(
            verdict=SelectionTransitionVerdict.DENIED_QUESTION_WRONG_CHALLENGE,
            current_session_state=current_session_state,
            requested=requested,
        )
    return SelectionTransitionResolution(
        verdict=SelectionTransitionVerdict.STATE_ELIGIBLE,
        current_session_state=current_session_state,
        requested=requested,
    )


def session_target_ref(session_id: SessionId) -> str:
    """The `CommandEnvelope.target_refs`/`CurrentVersionReader` ref
    string naming a Session as a commit-sensitive (read-only, never
    written) target -- shared by `application.question_selection_handler`
    (builds the envelope) and `persistence.session_repository` (reads
    the live version for it), so the two sides cannot silently drift.
    """
    return f"session:{session_id.value}"


__all__ = [
    "SelectionType",
    "QuestionSelection",
    "SelectionTransitionId",
    "SelectionOperation",
    "SelectionTransitionVerdict",
    "SelectionTransitionResolution",
    "resolve_selection_transition",
    "session_target_ref",
]
