"""QuestionLineage: the derivation relation between two Questions.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §16 (Question-to-Question
Lineage — `RELATION`, AC-02-003: "A reframe that constitutes a new
question must create a new Question identity linked to its source
Question. It must not overwrite the source Question."); 03
§25.4 (Question reframe is not a status transition: "source Question
remains unchanged + new Question created + QuestionLineage relation
created"); 09_DATA_EVENT_API_CONTRACTS.md §32 (DATA CONTRACT:
QuestionLineage).

WHY `question_lineage_id` IS A `RelationId`, NOT A NEW STRONG ID TYPE
----------------------------------------------------------------------
14_IMPLEMENTATION_SEQUENCE.md §5 defines exactly 28 strong ID types
(PKG-00's `semantic_types.ids` — deliberately explicit, not
dynamically generated) and no `QuestionLineageId` is among them.
`RelationId` is: a generic strong identity for RELATION-classed
objects that have no *dedicated* named ID in that closed list (unlike,
say, `EvidenceRelationId`, which 14 §5 does name specifically for
`EvidenceRelation`). `QuestionLineage` is 02 §16.2's own classification
as exactly `RELATION`, so `RelationId` is the correct, already-existing
type -- not a 29th type this package would have to invent.

WHY `QuestionLineage` HAS NO REPRESENTATION OF `producer_origin` AS A
SEPARATE VOCABULARY FROM `QuestionOrigin`
----------------------------------------------------------------------
09 §32 lists `producer_origin` on the lineage row itself (who/what
performed *this specific derivation act*), independent of the child
Question's own `origin` field. Both describe the same ORIGIN dimension
AC-02-002 establishes -- reusing `domain.question.QuestionOrigin`
avoids inventing a second vocabulary for one concept (14 PKG-06
NON_COLLAPSE_RULES: "Do not turn ... role into authority" and the
general non-collapse posture against duplicate semantics). This
package does not enforce `producer_origin == child.origin` as a DB
constraint: 09 does not require that cross-table equality, and adding
an unrequested trigger for it would be scope beyond "the smallest
complete coherent change" -- by construction the two values describe
the same real-world event and are expected to agree, but nothing here
manufactures a false guarantee if a caller ever legitimately needed
them to differ.

WHY `ai_generation_id` HAS NO FOREIGN KEY
-------------------------------------------
09 §32 lists `ai_generation_id nullable` on the lineage row, but the
`ai_generations` table (14 §9's migration `007_ai_operational`) does
not exist yet -- many packages away. This is the same situation PKG-02
disclosed for `human_authority_bindings.scope_id` (a polymorphic
reference to not-yet-existing target tables): a plain nullable UUID
column, no FK, and no claim that storing a value there proves a real
AIGeneration exists. `packages/persistence/tables.py`'s docstring
repeats this disclosure at the schema level.

WHY LINEAGE IS FULLY IMMUTABLE (NOT JUST "PARENT CANNOT CHANGE")
-------------------------------------------------------------------
09 §32.1: "Once established for a derived Question, lineage may not be
silently reassigned to a different parent. Correction requires
explicit new relation/history according to later policy." This package
reads that as covering the whole row, not only `parent_question_id`:
every field here is a birth fact of one specific derivation event
(who derived it, from what, when, by what transformation) — there is
no legitimate reason for *any* of them to change after creation, and
allowing some fields to be mutable while only `parent_question_id` is
protected would leave a narrower guarantee than 09 actually states.
Migration enforcement (a full `BEFORE UPDATE` rejection trigger) is
therefore stricter than a single-column check, matching the "may not
be silently reassigned" language literally rather than minimally.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import GenerationId, QuestionId, RelationId, WorkspaceId

from domain.question import QuestionOrigin


class LineageTransformationType(Enum):
    """09 §32's own named transformation semantics: "Allowed
    transformation semantics may include: REFRAME, FOLLOW_UP." Closed
    to exactly these two -- the only transformations 02 §16 and 09 §32
    actually name for this prototype. 02 §16.6 is explicit that
    normalization is a third, *excluded* case: "Normalization is not
    lineage" -- a `normalized_text` update never creates a
    `QuestionLineage` row at all, so no corresponding member exists
    here.
    """

    REFRAME = "REFRAME"
    FOLLOW_UP = "FOLLOW_UP"


@dataclass(frozen=True, slots=True)
class QuestionLineage:
    """One derivation relation: `child_question_id` was derived from
    `parent_question_id` by `transformation_type`.

    Frozen for the same reason `Question` is, reinforced here by 09
    §32.1's explicit no-reassignment rule: unlike `Question` (which is
    immutable because nothing in *this* package's scope legitimately
    changes it yet), a `QuestionLineage` row is immutable by
    architectural closure -- no future Command in this system is ever
    meant to edit an established lineage relation, only to create a
    new one recording a correction (09 §32.1: "Correction requires
    explicit new relation/history").
    """

    question_lineage_id: RelationId
    parent_question_id: QuestionId
    child_question_id: QuestionId
    workspace_id: WorkspaceId
    transformation_type: LineageTransformationType
    producer_origin: QuestionOrigin
    ai_generation_id: GenerationId | None
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.question_lineage_id, RelationId):
            raise TypeError(
                f"question_lineage_id must be a RelationId, got {type(self.question_lineage_id)!r}"
            )
        if not isinstance(self.parent_question_id, QuestionId):
            raise TypeError(
                f"parent_question_id must be a QuestionId, got {type(self.parent_question_id)!r}"
            )
        if not isinstance(self.child_question_id, QuestionId):
            raise TypeError(
                f"child_question_id must be a QuestionId, got {type(self.child_question_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.transformation_type, LineageTransformationType):
            raise TypeError(
                f"transformation_type must be a LineageTransformationType, "
                f"got {type(self.transformation_type)!r}"
            )
        if not isinstance(self.producer_origin, QuestionOrigin):
            raise TypeError(
                f"producer_origin must be a QuestionOrigin, got {type(self.producer_origin)!r}"
            )
        if self.ai_generation_id is not None and not isinstance(
            self.ai_generation_id, GenerationId
        ):
            raise TypeError(
                f"ai_generation_id must be a GenerationId or None, "
                f"got {type(self.ai_generation_id)!r}"
            )
        if self.parent_question_id == self.child_question_id:
            # Mandatory adversarial attack: invalid self-lineage. A
            # Question cannot be derived from itself.
            raise ValueError(
                f"QuestionLineage.parent_question_id and child_question_id must differ, "
                f"both were {self.parent_question_id!r}"
            )


__all__ = ["LineageTransformationType", "QuestionLineage"]
