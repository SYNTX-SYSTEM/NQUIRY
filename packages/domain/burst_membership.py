"""QuestionBurstMembership: the frozen raw-capture relation.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §17 (QuestionBurstQuestion
Membership); 09_DATA_EVENT_API_CONTRACTS.md §30 (DATA CONTRACT:
QuestionBurstQuestion Membership, §30.1 Frozen Membership).

WHY `capture_origin` REUSES `domain.question.QuestionOrigin`
----------------------------------------------------------------
09 §30 lists `capture_origin` as its own field, independent of the
captured Question's own `origin` (PKG-06). Both describe the same
ORIGIN dimension AC-02-002 establishes (02 §15.2) -- reusing the
existing closed vocabulary avoids a second enum for one concept, the
same reasoning `domain.question_lineage.QuestionLineage.producer_origin`
already applied.

WHY `capture_origin` IS FURTHER RESTRICTED TO `HUMAN` HERE
--------------------------------------------------------------
09 §30's own field list allows `capture_actor_user_id nullable for
AI-origin mode contribution` -- meaning a non-HUMAN `capture_origin`
is a real, named possibility in the full architecture, for Mode B/C
Bursts (08 §12.2/12.3). Since `domain.burst.QuestionBurst` only
constructs `HUMAN_ONLY` Bursts in this package (see that module's
docstring), every membership captured into one is, by construction, a
human capture -- allowing this type to accept an AI-origin membership
row would silently open a door this package's own Burst type refuses
to open. `capture_actor_user_id`/`capture_origin` are paired with the
identical biconditional PKG-06 established for `Question.author_user_id`/
`origin`.

WHY `workspace_id` IS PRESENT (NOT A NAMED 09 §30 FIELD)
--------------------------------------------------------------
09 §30's field list does not name `workspace_id`, but this package's
own migration requires it on the underlying table for the same
constrained-denormalization reason `sessions`/`questions`/
`question_lineage` all carry one: two composite foreign keys --
`(question_burst_id, workspace_id)` and `(question_id, workspace_id)`,
both against a parent's own `(id, workspace_id)` anchor -- force the
Burst and its captured Question to resolve to the same Workspace,
making cross-Workspace capture structurally unrepresentable (the exact
pattern PKG-06 established for `QuestionLineage`). The domain type
carries it so a caller cannot construct a membership without stating
which Workspace it is even meant to belong to.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from semantic_types.ids import BurstId, QuestionId, RelationId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from domain.question import QuestionOrigin


@dataclass(frozen=True, slots=True)
class QuestionBurstMembership:
    """One captured-Question-in-Burst relation.

    Frozen: 09 §30.1 says outright that "membership
    additions/removals [are] prohibited" once the parent Burst is
    COMPLETED, but this package goes further and treats every
    membership row as immutable from the moment it is captured --
    `captured_order` in particular has no legitimate reason to change
    once assigned (it is the ordinal position of a specific capture
    event, not a re-orderable priority field). A correction, if ever
    needed, is a new relation/history entry per the same "explicit
    new relation" policy PKG-06 established for `QuestionLineage`
    (09 §32.1), not an in-place edit of this one.
    """

    burst_question_membership_id: RelationId
    question_burst_id: BurstId
    question_id: QuestionId
    workspace_id: WorkspaceId
    captured_order: int
    captured_at: datetime
    capture_actor_user_id: UserId | None
    capture_origin: QuestionOrigin
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.burst_question_membership_id, RelationId):
            raise TypeError(
                f"burst_question_membership_id must be a RelationId, "
                f"got {type(self.burst_question_membership_id)!r}"
            )
        if not isinstance(self.question_burst_id, BurstId):
            raise TypeError(
                f"question_burst_id must be a BurstId, got {type(self.question_burst_id)!r}"
            )
        if not isinstance(self.question_id, QuestionId):
            raise TypeError(f"question_id must be a QuestionId, got {type(self.question_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.capture_origin, QuestionOrigin):
            raise TypeError(
                f"capture_origin must be a QuestionOrigin, got {type(self.capture_origin)!r}"
            )
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if self.capture_actor_user_id is not None and not isinstance(
            self.capture_actor_user_id, UserId
        ):
            raise TypeError(
                f"capture_actor_user_id must be a UserId or None, "
                f"got {type(self.capture_actor_user_id)!r}"
            )
        if self.capture_origin is not QuestionOrigin.HUMAN:
            # PACKAGE_BOUNDARY: only HUMAN_ONLY Bursts are constructed
            # here (domain.burst), so only HUMAN captures are legitimate.
            raise ValueError(
                f"this package only constructs HUMAN-origin burst memberships, "
                f"got {self.capture_origin}"
            )
        if self.capture_actor_user_id is None:
            raise ValueError("HUMAN-origin capture requires a capture_actor_user_id")
        if self.captured_order < 0:
            raise ValueError(f"captured_order must be >= 0, got {self.captured_order}")


FROZEN_SET_FINGERPRINT_SCHEME = "NQ-FROZEN-SET-V2"
"""The canonical-serialization scheme tag. V1 (PKG-07) hashed
`question_id:record_version`."""


def compute_frozen_membership_fingerprint(
    memberships: Sequence[QuestionBurstMembership],
    question_original_texts: Mapping[QuestionId, str],
) -> str:
    """The frozen raw set's identity/integrity relation (not a security
    signature; the same disclosed role as AC-09-009's Evidence-set fingerprint).

    F03 WU-03.3 (FBR-F03-4), a DISCLOSED DEVIATION from 14 §19's historical
    `[IMPLEMENTATION CHOICE]` ("membership IDs plus Question content versions",
    PKG-07: `question_id:record_version`). `questions.record_version` and
    `normalized_text` stay updatable after the Burst (03 §25.5: normalization
    is legitimate derived work, F04), so a fingerprint over them would stop
    matching an UNTOUCHED raw set after a later normalization bump, and
    03 TRN-SESS-005 requires "frozen-set identity must be reconstructable".
    The fingerprint is therefore computed over immutable BIRTH FACTS only. Per
    member: the membership id, the question id, the SHA-256 digest of the exact
    `original_text` (UTF-8, no normalization), `captured_order`, the capture
    actor and `captured_at` (UTC). Members are ordered by
    `(captured_order, membership id)`. Every membership row and every
    `original_text` is immutable at the database (DB triggers), so the value
    is recomputable at any time from canonical persistence.

    `question_original_texts` must contain an entry for every membership's
    `question_id`; a missing entry raises rather than silently omitting a
    member (an incomplete fingerprint would look valid while proving less than
    it claims).
    """
    if not memberships:
        raise ValueError("cannot compute a frozen membership fingerprint over zero memberships")

    lines: list[str] = [FROZEN_SET_FINGERPRINT_SCHEME]
    for membership in sorted(
        memberships,
        key=lambda m: (m.captured_order, str(m.burst_question_membership_id.value)),
    ):
        try:
            original_text = question_original_texts[membership.question_id]
        except KeyError as exc:
            raise ValueError(
                f"no original_text supplied for question_id={membership.question_id!r}"
            ) from exc
        digest = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
        actor_id = membership.capture_actor_user_id
        actor = "" if actor_id is None else str(actor_id.value)
        lines.append(
            "|".join(
                (
                    str(membership.burst_question_membership_id.value),
                    str(membership.question_id.value),
                    digest,
                    str(membership.captured_order),
                    actor,
                    membership.captured_at.astimezone(timezone.utc).isoformat(),
                )
            )
        )
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


__all__ = [
    "FROZEN_SET_FINGERPRINT_SCHEME",
    "QuestionBurstMembership",
    "compute_frozen_membership_fingerprint",
]
