"""Question: the first-class canonical inquiry object.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §14 (Question —
`CANONICAL_DOMAIN_OBJECT`; LEVEL 1 calls it "the most important object
in the system") and §15 (Question Origin and Derivation Semantics);
03_STATE_AND_TRANSITION_ARCHITECTURE.md §23 (Consequential Question
Capture, TRN-Q-001) and §25 (Question State Treatment,
GAP-02-013/GAP-02-002); 07_EVIDENCE_AND_PROVENANCE.md §45 (Provenance
and Question Integrity) and §54.1/§54.2 (Provenance Minimums);
09_DATA_EVENT_API_CONTRACTS.md §31 (DATA CONTRACT: Question).

WHY THERE IS NO `text` FIELD (ONLY `original_text`)
----------------------------------------------------
LEVEL 1 defines both `text` and `original_text` but 02 §14.7
(GAP-02-002) leaves `text`'s exact semantics `[UNDERDEFINED]`, stating
only the negative constraint: "text must not become a mechanism for
silently replacing original_text." 09 §31.2 restates this as a
materialization rule: "09 stores both only if their semantics are
explicitly distinguished by application contract. No field alias may
allow `text` update to mutate `original_text`." This package has no
Command, no update path, and no application contract that would give
`text` a distinct, safe meaning -- so a `text` column here would be an
unused field with undefined write semantics, which is exactly the kind
of ambiguity 09 warns against. Omitted, the same way PKG-05 omitted
`Challenge.status` for an analogous reason (see `domain.challenge`).
Re-adding it once a real application contract resolves GAP-02-002 is
additive.

WHY THERE IS NO `status` FIELD
-------------------------------
03 §25.1 (GAP-02-013, carried from GAP-02-012's pattern): "Question
status vocabulary remains [UNDERDEFINED]." 03 §25.2 forbids using it as
transition guard, authority predicate, selection authority, evidence
status, or AI validation status -- every use this prototype would have.
Omitted for the same fail-closed reason as `Challenge.status`.

WHY THERE IS NO question_type / priority / emotional_signal /
novelty_score / catalytic_score
----------------------------------------------------------------------
02 §14.9-§14.11 classifies all of these as classification metadata or
derived assessments that "do not define Question identity or truth."
None are required by this package's proof claims (P-01, P-02) or its
stated objective ("Question stable identity, immutable original,
origin/derivation representation, QuestionLineage relation"). Adding
unused columns with no consumer or test in this package would be scope
creep, not the smallest complete coherent change 14 requires.

THE ORIGIN VOCABULARY (`QuestionOrigin`)
-----------------------------------------
09 §31 lists an unnamed "origin/source semantics" field on Question.
02 §15.1 (GAP-02-003) explicitly *refuses* LEVEL 2's mixed enum
(`source: human | ai | imported | inferred | reframed`) because it
conflates two independent dimensions -- 02 §15.2 (AC-02-002) requires
ORIGIN and DERIVATION/LINEAGE to be represented separately. 02 §15's
own "general source categories" list -- `human, ai, imported,
inferred` -- is exactly the ORIGIN axis once `reframed` (which 02
itself assigns to the derivation axis) is excluded. `QuestionOrigin`
below adopts that list verbatim; derivation is represented separately
by `domain.question_lineage.LineageTransformationType`.

`author_user_id` pairs with `origin`: 09 §31 says it is "nullable where
non-human" -- read here as the direct biconditional that
`__post_init__` enforces: `origin is HUMAN` if and only if
`author_user_id` is set. AI is never converted into User identity (02
§14.12: "AI is not converted into User identity"), and this pairing is
exactly what prevents an AI-origin Question from claiming human
authorship (a mandatory adversarial attack for this package).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import ChallengeId, QuestionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion


class QuestionOrigin(Enum):
    """The ORIGIN axis of 02 §15.2's AC-02-002 split. Closed to 02
    §15's own "general source categories" list, excluding `reframed`
    (which 02 assigns to the derivation axis, not origin -- see
    `domain.question_lineage.LineageTransformationType`).
    """

    HUMAN = "HUMAN"
    AI = "AI"
    IMPORTED = "IMPORTED"
    INFERRED = "INFERRED"


@dataclass(frozen=True, slots=True)
class Question:
    """One Question, as canonically stored.

    Frozen: 14 §3.1 gives `domain` no canonical write capability, and
    this package additionally makes immutability the *point* --
    `original_text` is a birth fact (AC-02-001) that must never change
    for the life of this identity. There is deliberately no
    `updated_at` field: 09 §31's field list does not include one, and
    nothing this package materializes ever legitimately changes after
    creation (P-01/P-02's entire proof is that it doesn't).

    `challenge_id` establishes ownership (02 §14.3: "Question belongs
    to a Challenge through `challenge_id`... does not require Session
    ownership to exist" -- a Question may be captured during a Burst,
    during general inquiry, as a follow-up, or as a reframe, none of
    which require a live Session reference on the Question itself).
    `workspace_id` is the same kind of constrained denormalization 09
    §27.1 sanctioned for `Session` (02 §14.4: "Question resolves to
    Workspace through Challenge") -- migration enforcement is a
    composite FK, not a trigger.
    """

    question_id: QuestionId
    challenge_id: ChallengeId
    workspace_id: WorkspaceId
    original_text: str
    normalized_text: str | None
    origin: QuestionOrigin
    author_user_id: UserId | None
    created_at: datetime
    record_version: RecordVersion

    def __post_init__(self) -> None:
        if not isinstance(self.question_id, QuestionId):
            raise TypeError(f"question_id must be a QuestionId, got {type(self.question_id)!r}")
        if not isinstance(self.challenge_id, ChallengeId):
            raise TypeError(f"challenge_id must be a ChallengeId, got {type(self.challenge_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.origin, QuestionOrigin):
            # The direct-enum-coercion attack: a caller passing the raw
            # string "HUMAN" must not produce a Question that merely
            # *looks* like it holds an origin.
            raise TypeError(f"origin must be a QuestionOrigin, got {type(self.origin)!r}")
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        if self.author_user_id is not None and not isinstance(self.author_user_id, UserId):
            raise TypeError(
                f"author_user_id must be a UserId or None, got {type(self.author_user_id)!r}"
            )
        if not self.original_text:
            raise ValueError("Question.original_text must be non-empty")
        # 09 §31: "author_user_id nullable where non-human" -- read as
        # the direct biconditional. This is the structural half of the
        # "AI reframe/import claims human authorship" attack: there is
        # no constructor path that produces a HUMAN-origin Question
        # without an author, or a non-HUMAN-origin Question with one.
        is_human = self.origin is QuestionOrigin.HUMAN
        has_author = self.author_user_id is not None
        if is_human != has_author:
            raise ValueError(
                f"Question.author_user_id must be set if and only if origin is HUMAN "
                f"(origin={self.origin}, author_user_id={self.author_user_id!r})"
            )


__all__ = ["QuestionOrigin", "Question"]
