"""Challenge: the canonical inquiry frame.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §9 (Challenge —
`CANONICAL_DOMAIN_OBJECT`, scoped by exactly one Workspace);
09_DATA_EVENT_API_CONTRACTS.md §25 (DATA CONTRACT: Challenge);
03_STATE_AND_TRANSITION_ARCHITECTURE.md §12 (Challenge State
Treatment) and §12.3 / TRN-CH-001 (creation is existential
ABSENT -> PRESENT, not a status transition).

WHY THERE IS NO `status` FIELD
------------------------------
LEVEL 1 names `Challenge.status` but defines no values. 03 §12.1
refuses to invent one ("03 does not invent: OPEN, ACTIVE, CLOSED,
ARCHIVED or any other Challenge status vocabulary"), GAP-02-012 /
GAP-03-013 remain OPEN in 16_DECISION_GAP_REGISTER.md (NQ-GAP-018),
and 03 §12.2 forbids using it as::

    transition guard
    authority predicate
    boundary predicate
    prototype acceptance condition

which is every use this prototype would have for it. 09 §25.2 leaves
materialization open ("If no such enum is required by prototype, it
remains nullable/configuration-bound according to implementation") --
so not materializing it is a permitted implementation choice, and it
is the fail-closed one: a nullable free-text `status` column is
exactly the `STATE != STATUS STRING` collapse this package is
required to prevent. Adding the column later, once GAP-03-013 closes
with a real vocabulary, is a purely additive migration.

WHY THERE IS NO `emotional_temperature` FIELD
---------------------------------------------
02 §10.5 states its technical role -- initial reading, latest-reading
projection, compatibility field, or denormalized value -- "remains for
09", and 09 §25 restates it only as "emotional_temperature
representation" without resolving it. Choosing one of those four
meanings here would be semantic invention. 02 §10 models the real
thing as a separate `EmotionalTemperatureReading` VALUE_RECORD, and 14
§9 assigns no such table to migration 003. Deferred, not stubbed.

Neither omission closes a gap: no 03 transition contract depends on
either field.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from semantic_types.ids import ChallengeId, WorkspaceId
from semantic_types.versions import RecordVersion


@dataclass(frozen=True, slots=True)
class Challenge:
    """One Challenge, as canonically stored.

    Frozen: this is a canonical-state snapshot, not a mutable entity.
    14 §3.1 gives `domain` no canonical write capability at all
    ("Canonical write: no"), so there is deliberately no mutator on
    this type -- a changed Challenge is a new `Challenge` value
    produced by a governed CommitUnit (Phase 4), never an in-place
    edit of this object.

    `workspace_id` is the single authoritative scope (02 §9.3,
    `[ARCHITECTURAL CLOSURE]`: "Challenge is scoped by exactly one
    Workspace"), materialized as a direct FK exactly as 09 §25.1
    permits.
    """

    challenge_id: ChallengeId
    workspace_id: WorkspaceId
    title: str
    description: str | None
    context: str | None
    desired_outcome: str | None
    constraints: str | None
    stakeholders: str | None
    created_at: datetime
    updated_at: datetime
    record_version: RecordVersion

    def __post_init__(self) -> None:
        # Dataclasses do not enforce annotations at runtime; the two
        # identity fields are the ones a caller could most plausibly
        # pass as a bare UUID, collapsing the strong-ID distinction
        # PKG-00 established.
        if not isinstance(self.challenge_id, ChallengeId):
            raise TypeError(f"challenge_id must be a ChallengeId, got {type(self.challenge_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if not self.title:
            raise ValueError("Challenge.title must be non-empty")


__all__ = ["Challenge"]
