"""Session: the canonical process object that owns the inquiry state machine.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §11 (Session —
`CANONICAL_PROCESS_OBJECT`, belongs to exactly one Challenge, resolves
to Workspace *through* Challenge); 03_STATE_AND_TRANSITION_ARCHITECTURE.md
§13 (Session State Machine, the 13 source-defined states and their
`[ARCHITECTURAL CLOSURE]` semantics) and §14 (AC-03-001: iteration does
not reopen a CLOSED Session); 09_DATA_EVENT_API_CONTRACTS.md §27 (DATA
CONTRACT: Session).

`SessionState` is the approved state vocabulary. It is a *state*, not a
status string (14 PKG-05 ARCHITECTURAL_INVARIANTS: "STATE != STATUS
STRING"). Three independent properties make that true rather than
merely asserted:

1. The vocabulary is closed -- `SessionState("anything_else")` raises.
2. `Session` is frozen and exposes no state mutator, so there is no
   generic setter an illegal transition could travel through
   ("ILLEGAL TRANSITION MUST NOT BE ENABLED BY GENERIC SETTER").
3. Which pairs of states may follow one another is not a property of
   this module at all -- it lives in `domain.session_transitions`,
   derived from 03 §15/§16, and is enforced a second time by the
   database in migration 003.

09 §27.2 is the rule those three properties serve: "`state` may change
only through mapped 03 Commands and governed CommitUnit. Direct state
field update is invalid."
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import ChallengeId, SessionId, WorkspaceId
from semantic_types.versions import MethodVersion, RecordVersion


class SessionState(Enum):
    """The 13 Session states 03 §13.1 defines, in 03 §13.2's order.

    Closed vocabulary: `[SPECIFIED]` by LEVEL 1 and restated
    identically by 02 §11.5 and 09 §27. A state not listed here does
    not exist architecturally. In particular 03 §18 (GAP-03-001)
    records that LEVEL 1 defines no CANCELLED / ABANDONED / EXPIRED /
    VOID state and that "03 does not invent one" -- so neither does
    this enum. A user abandoning a Session before REVIEW currently has
    no source-defined terminal transition, and that is deliberately
    left visible rather than papered over with a hidden skip to
    CLOSED.
    """

    DRAFT = "DRAFT"
    SETUP = "SETUP"
    CHALLENGE_CAPTURE = "CHALLENGE_CAPTURE"
    QUESTION_GENERATION = "QUESTION_GENERATION"
    QUESTION_CAPTURE = "QUESTION_CAPTURE"
    ANALYSIS = "ANALYSIS"
    REFLECTION = "REFLECTION"
    QUESTION_SELECTION = "QUESTION_SELECTION"
    INVESTIGATION = "INVESTIGATION"
    EXPERIMENT = "EXPERIMENT"
    ACTION = "ACTION"
    REVIEW = "REVIEW"
    CLOSED = "CLOSED"


INITIAL_SESSION_STATE = SessionState.DRAFT
"""The one state a newly created Session may hold.

03 TRN-SESS-001 CREATE_SESSION, NEXT STATE: `DRAFT`. There is no other
entry point into the state machine, which is why migration 003's
`BEFORE INSERT` trigger rejects any other value outright -- a
caller-supplied target state cannot be smuggled in at creation time.
"""

TERMINAL_SESSION_STATES = frozenset({SessionState.CLOSED})
"""03 §13.3 CLOSED: "The Session is terminal. No further transition
inside the same Session is legal." Reinforced by AC-03-001 (03 §14):
a CLOSED Session does not transition back to DRAFT, SETUP or
CHALLENGE_CAPTURE -- "A new inquiry cycle creates a new Session under
the same Challenge."
"""


@dataclass(frozen=True, slots=True)
class Session:
    """One Session, as canonically stored.

    Frozen for the same reason `Challenge` is: 14 §3.1 gives `domain`
    no canonical write capability. A Session that has transitioned is
    a *new* `Session` value produced by a governed CommitUnit (Phase
    4) after the boundary pipeline (Phase 3) has allowed it -- never an
    in-place edit of this object. PKG-05 provides neither of those
    layers, and deliberately provides no substitute for them.

    `workspace_id` is a denormalized convenience, permitted by 09 §27.1
    *only* under the constraint that it equals the Challenge's
    Workspace: "It cannot become an alternate ownership source."
    Authoritative ownership stays 02 §11.4's derivation through
    `challenge_id`. Migration 003 enforces the equality with a
    composite foreign key, so a Session whose Workspace disagrees with
    its Challenge's is not representable in the database at all.

    `applied_method_key` / `applied_method_version` materialize 09
    §27's pinned InquiryMethod reference (12 §9: "InquiryMethod version
    reference | CONFIGURATION | Pinned Session configuration only").
    They are configuration, not authority: pinning a method never
    grants a right.
    """

    session_id: SessionId
    challenge_id: ChallengeId
    workspace_id: WorkspaceId
    applied_method_key: str
    applied_method_version: MethodVersion
    state: SessionState
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, SessionId):
            raise TypeError(f"session_id must be a SessionId, got {type(self.session_id)!r}")
        if not isinstance(self.challenge_id, ChallengeId):
            raise TypeError(f"challenge_id must be a ChallengeId, got {type(self.challenge_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.state, SessionState):
            # The direct-enum-coercion attack: a caller passing the raw
            # string "CLOSED" (or "TOTALLY_DONE") must not produce a
            # Session that merely *looks* like it holds a state.
            raise TypeError(f"state must be a SessionState, got {type(self.state)!r}")
        if not isinstance(self.applied_method_version, MethodVersion):
            raise TypeError(
                f"applied_method_version must be a MethodVersion, "
                f"got {type(self.applied_method_version)!r}"
            )
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if not self.applied_method_key:
            raise ValueError("Session.applied_method_key must be non-empty")
        if self.closed_at is not None and self.state is not SessionState.CLOSED:
            # `closed_at` is 09 §27's nullable closure timestamp. It may
            # only be populated once the Session actually reached its
            # terminal state -- otherwise a record could claim closure
            # while still sitting mid-chain, which 03 TRN-SESS-013
            # explicitly refuses ("CLOSED must not be used to hide
            # unresolved failure"). Migration 003 carries the same rule
            # as a CHECK constraint.
            raise ValueError(
                f"Session.closed_at may only be set when state is CLOSED, got {self.state}"
            )

    @property
    def is_terminal(self) -> bool:
        """Whether 03 permits any further transition inside this Session.

        This reports a fact about the current state. It is not an
        authority conclusion and not a boundary result.
        """
        return self.state in TERMINAL_SESSION_STATES


__all__ = [
    "SessionState",
    "Session",
    "INITIAL_SESSION_STATE",
    "TERMINAL_SESSION_STATES",
]
