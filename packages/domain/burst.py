"""QuestionBurst: the protected raw-capture process object.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §13 (QuestionBurst — canonical
process object, protected capture lifecycle); 03_STATE_AND_TRANSITION_
ARCHITECTURE.md §19 (QuestionBurst State Machine — `[ARCHITECTURAL
CLOSURE]`) and §20 (TRN-BURST-001..005); 09_DATA_EVENT_API_CONTRACTS.md
§29 (DATA CONTRACT: QuestionBurst).

WHY THERE IS NO `configured_duration_ref`/`value` OR `timer_basis_ref`
------------------------------------------------------------------------
03 §21 (CONFLICT-007) leaves the Burst duration model an `[OPEN SOURCE
TENSION]` ("fixed four minutes" vs. "four-minute default with
configuration" vs. "method-defined approximate duration") and 03 §22
(GAP-03-002) leaves pause/timer interaction `[UNDERDEFINED]`
("whether timer stops while PAUSED", "whether resume continues
remaining time", etc.), with the explicit rule: "No timer
implementation may invent these semantics before closure." 09 §29.2
adds: "`timer_basis_ref` cannot be treated as authority until timer
gaps close." This package's own coding prompt is unambiguous: "Manual
authorized completion only. No automatic timer." Materializing a
duration/timer field that nothing in this package populates,
interprets, or enforces would be exactly the kind of invented timer
semantics 03 §22 forbids -- omitted, the same fail-closed pattern as
`Challenge.status`/`Question.status`.

WHY `mode` IS RESTRICTED TO `HUMAN_ONLY` HERE
------------------------------------------------
09 §29.1 resolves 3 approved `burst_mode` values (`HUMAN_ONLY`,
`HUMAN_PLUS_AI`, `AI_CHALLENGE_AFTER_HUMANS`) -- the vocabulary itself
is not underdefined, so `BurstMode` carries all 3. But 08 §12.2 states
Mode B ("Prototype inclusion remains unresolved") and 08 §12.3
describes Mode C as a distinct post-freeze capability. This package's
own objective is exactly "Human-only Burst states" -- implementing
Mode B/C transition or capture behavior here would be "successor
behavior" the package boundary forbids. `QuestionBurst.__post_init__`
therefore requires `mode is BurstMode.HUMAN_ONLY`; a future package
implementing Mode B/C will extend or supersede this constructor, not
this one.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import BurstId, SessionId, WorkspaceId
from semantic_types.versions import RecordVersion


class BurstState(Enum):
    """03 §19.1's 4-state vocabulary, `[ARCHITECTURAL CLOSURE]`.

    "No `CANCELLED` or `RECOVERING` domain state is introduced" (03
    §19.1) -- failure/recovery are transition outcomes and 10
    architecture, not additional Burst states.
    """

    PREPARED = "PREPARED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class BurstMode(Enum):
    """09 §29.1's 3 approved values. See module docstring for why only
    `HUMAN_ONLY` is constructible by this package.
    """

    HUMAN_ONLY = "HUMAN_ONLY"
    HUMAN_PLUS_AI = "HUMAN_PLUS_AI"
    AI_CHALLENGE_AFTER_HUMANS = "AI_CHALLENGE_AFTER_HUMANS"


INITIAL_BURST_STATE = BurstState.PREPARED
"""03 TRN-BURST-001 PREPARE_BURST, NEXT STATE: `PREPARED`."""

TERMINAL_BURST_STATES = frozenset({BurstState.COMPLETED})
"""03 §19.5: "`COMPLETED` is terminal for the same QuestionBurst." """

PROTECTED_BURST_STATES = frozenset({BurstState.ACTIVE, BurstState.PAUSED})
"""06 §14's contamination DENY list applies "During ACTIVE protected
Human-only Burst", and 03 §19.4 describes PAUSED as "the same process"
as ACTIVE with input merely suspended -- protection does not lapse
because input is paused. Used by `domain.burst_contamination`.
"""


@dataclass(frozen=True, slots=True)
class QuestionBurst:
    """One QuestionBurst, as canonically stored.

    Frozen for the same reason `Session` is (PKG-05): 14 §3.1 gives
    `domain` no canonical write capability, and a changed Burst is a
    new value a governed write produces, never an in-place edit here.

    `workspace_id` is the same constrained denormalization pattern as
    `Session`/`Question`: 09 does not name it explicitly for
    QuestionBurst, but 02 §13.4's "Ownership" ties a Burst to its
    Session, which itself resolves to Workspace through Challenge --
    migration enforcement is a composite FK through `session_id`,
    identical in kind to `sessions`' own FK into `challenges`.

    `frozen_membership_fingerprint` materializes 14 §19's
    `[IMPLEMENTATION CHOICE]`: "canonical sorted serialization of
    membership IDs plus Question content versions. Hash establishes
    identity/integrity relation only" -- not a security signature, a
    change-detection value (identical role to AC-09-009's Evidence-set
    fingerprint). It is `None` until COMPLETED and required once
    COMPLETED (03 §19.5: "Raw captured Question membership is
    frozen").
    """

    burst_id: BurstId
    session_id: SessionId
    workspace_id: WorkspaceId
    state: BurstState
    mode: BurstMode
    started_at: datetime | None
    paused_at: datetime | None
    completed_at: datetime | None
    frozen_membership_fingerprint: str | None
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.burst_id, BurstId):
            raise TypeError(f"burst_id must be a BurstId, got {type(self.burst_id)!r}")
        if not isinstance(self.session_id, SessionId):
            raise TypeError(f"session_id must be a SessionId, got {type(self.session_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.state, BurstState):
            raise TypeError(f"state must be a BurstState, got {type(self.state)!r}")
        if not isinstance(self.mode, BurstMode):
            raise TypeError(f"mode must be a BurstMode, got {type(self.mode)!r}")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if self.mode is not BurstMode.HUMAN_ONLY:
            # PACKAGE_BOUNDARY: Mode B/C behavior is successor scope.
            raise ValueError(
                f"this package only constructs HUMAN_ONLY Bursts (08 section 12.2/12.3), "
                f"got {self.mode}"
            )
        is_completed = self.state is BurstState.COMPLETED
        has_fingerprint = self.frozen_membership_fingerprint is not None
        if is_completed != has_fingerprint:
            raise ValueError(
                f"frozen_membership_fingerprint must be set if and only if state is "
                f"COMPLETED (03 section 19.5), state={self.state}, "
                f"fingerprint={self.frozen_membership_fingerprint!r}"
            )
        if self.completed_at is not None and not is_completed:
            raise ValueError(
                f"completed_at may only be set when state is COMPLETED, got {self.state}"
            )
        if self.state is BurstState.PREPARED and self.started_at is not None:
            raise ValueError("started_at must be unset while state is PREPARED")

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_BURST_STATES

    @property
    def is_protected(self) -> bool:
        """Whether raw-capture contamination protection currently
        applies (06 §14) -- true for ACTIVE and PAUSED alike.
        """
        return self.state in PROTECTED_BURST_STATES


__all__ = [
    "BurstState",
    "BurstMode",
    "QuestionBurst",
    "INITIAL_BURST_STATE",
    "TERMINAL_BURST_STATES",
    "PROTECTED_BURST_STATES",
]
