"""QuestionRepository: the PUBLIC_INTERFACES port 14 assigns to PKG-06.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`QuestionRepository`: create/read, no original-text update." Unlike
`ChallengeRepository`/`SessionRepository` (14 §10: "mutation-plan
application inside CommitUnit" / "state mutation only through
transition plan" -- both requiring machinery PKG-05 correctly deferred
to Phase 4), 14's own wording for `QuestionRepository` is "create/read"
without a CommitUnit qualifier. This package reads that literally:
Question creation (03 TRN-Q-001) is an append-only, no-transition-machine
operation -- there is no illegal-state-transition risk a create-only
port could enable, unlike a state *mutator* would. What 14 explicitly
forbids instead is narrower and structural: "no original-text update"
-- honored here in its strongest form, matching PKG-05's `Session`
precedent: no update method of any kind exists on this repository, for
either `questions` or `question_lineage`.

THIS REPOSITORY IS NOT ITSELF A GOVERNED CREATION PATH
--------------------------------------------------------
`create_root`/`create_derived` perform real INSERTs -- they are the
first write-capable production repository in this codebase (every
prior package's repository was read-only, deferring writes to
CommitUnit). That is a deliberate, disclosed choice matching 14 §10's
literal text, not a "direct persistence" forbidden-shortcut violation:
the forbidden shortcut is code *outside* `persistence` bypassing a
governed Command/Boundary/CommitUnit path and writing directly to the
database while claiming legitimacy. This module IS the typed
persistence adapter 14 §3.1 assigns to `persistence`
("PostgreSQL adapters implementing typed ports") -- exactly what a
future governed Command (Phase 3/4, boundary engine + CommitUnit) is
meant to call *through*, the same relationship
`SqlAlchemyMembershipRepository`'s reads already have to the
not-yet-built `AuthorityResolver` callers that will eventually consume
them. PKG-06 wires this repository into no Command, no HTTP endpoint,
and no production caller of any kind (14 assigns neither a Command nor
a Query to PKG-06) -- it is a port, defined and proven correct in
isolation, not yet invoked.

Both `questions` and `question_lineage` are owned by this one
repository, not split into `QuestionRepository`/
`QuestionLineageRepository`: 14 §10's repository-port list has no
separate entry for QuestionLineage (unlike, say, `AuthorityBindingRepository`
being split out from `MembershipRepository` for a different 02
object), and PKG-06's own objective groups "Question stable identity,
immutable original, lineage" as one coherent capability.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.question import Question, QuestionOrigin
from domain.question_lineage import LineageTransformationType, QuestionLineage
from semantic_types.ids import (
    ChallengeId,
    GenerationId,
    QuestionId,
    RelationId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from persistence.tables import question_lineage_table, questions_table


@runtime_checkable
class QuestionRepository(Protocol):
    """Port: Question and QuestionLineage create/read (14 §10).

    No repository returns an authority conclusion (14 §10) -- these
    methods return raw canonical state, never a computed "may this
    caller do X" verdict. No repository method updates `original_text`,
    any other Question field, or any `QuestionLineage` field -- the
    absence is structural, not merely undocumented.
    """

    def create_root(self, question: Question) -> None:
        """Persist a Question with no parent (a root capture -- 03
        §25.3's existential ABSENT -> PRESENT). Raises on constraint
        violation (duplicate id, cross-Workspace Challenge mismatch,
        origin/author pairing violation) -- this method does not catch
        or reinterpret those as anything softer than a real failure.
        """
        ...

    def create_derived(self, question: Question, lineage: QuestionLineage) -> None:
        """Persist a derived Question together with the
        `QuestionLineage` relation proving its derivation, in one call
        so a caller cannot create one without the other through this
        port's own surface (AC-02-003: reframe/follow-up "must not
        overwrite the source Question" -- the source Question is never
        touched by this method at all, only referenced by
        `lineage.parent_question_id`).

        `lineage.child_question_id` must equal `question.question_id`
        and `lineage.workspace_id` must equal `question.workspace_id`
        -- raises `ValueError` immediately (no DB round-trip) if a
        caller passes a mismatched pair, since that mismatch is a
        precondition of this method's own contract, not something the
        database schema alone would necessarily catch.
        """
        ...

    def get(self, question_id: QuestionId) -> Question | None:
        """The Question row for this id, or `None` if it does not
        exist."""
        ...

    def get_lineage_for_child(self, child_question_id: QuestionId) -> QuestionLineage | None:
        """The `QuestionLineage` relation for which this Question is
        the child, or `None` if this Question is a root capture (no
        parent)."""
        ...


class SqlAlchemyQuestionRepository:
    """`QuestionRepository` backed by `questions`/`question_lineage`
    via a SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create_root(self, question: Question) -> None:
        self._connection.execute(sa.insert(questions_table).values(**_question_to_row(question)))

    def create_derived(self, question: Question, lineage: QuestionLineage) -> None:
        if lineage.child_question_id != question.question_id:
            raise ValueError(
                f"lineage.child_question_id ({lineage.child_question_id!r}) must equal "
                f"question.question_id ({question.question_id!r})"
            )
        if lineage.workspace_id != question.workspace_id:
            raise ValueError(
                f"lineage.workspace_id ({lineage.workspace_id!r}) must equal "
                f"question.workspace_id ({question.workspace_id!r})"
            )
        self._connection.execute(sa.insert(questions_table).values(**_question_to_row(question)))
        self._connection.execute(
            sa.insert(question_lineage_table).values(**_lineage_to_row(lineage))
        )

    def get(self, question_id: QuestionId) -> Question | None:
        stmt = sa.select(questions_table).where(questions_table.c.id == question_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _question_from_row(row)

    def get_lineage_for_child(self, child_question_id: QuestionId) -> QuestionLineage | None:
        stmt = sa.select(question_lineage_table).where(
            question_lineage_table.c.child_question_id == child_question_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _lineage_from_row(row)


def _question_to_row(question: Question) -> dict[str, object]:
    return {
        "id": question.question_id.value,
        "challenge_id": question.challenge_id.value,
        "workspace_id": question.workspace_id.value,
        "original_text": question.original_text,
        "normalized_text": question.normalized_text,
        "origin": question.origin.value,
        "author_user_id": None
        if question.author_user_id is None
        else question.author_user_id.value,
        "created_at": question.created_at,
        "record_version": question.record_version.value,
    }


def _question_from_row(row: sa.RowMapping) -> Question:
    return Question(
        question_id=QuestionId(row["id"]),
        challenge_id=ChallengeId(row["challenge_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        original_text=row["original_text"],
        normalized_text=row["normalized_text"],
        origin=QuestionOrigin(row["origin"]),
        author_user_id=None if row["author_user_id"] is None else UserId(row["author_user_id"]),
        created_at=row["created_at"],
        record_version=RecordVersion(row["record_version"]),
    )


def _lineage_to_row(lineage: QuestionLineage) -> dict[str, object]:
    return {
        "id": lineage.question_lineage_id.value,
        "parent_question_id": lineage.parent_question_id.value,
        "child_question_id": lineage.child_question_id.value,
        "workspace_id": lineage.workspace_id.value,
        "transformation_type": lineage.transformation_type.value,
        "producer_origin": lineage.producer_origin.value,
        "ai_generation_id": (
            None if lineage.ai_generation_id is None else lineage.ai_generation_id.value
        ),
        "created_at": lineage.created_at,
    }


def _lineage_from_row(row: sa.RowMapping) -> QuestionLineage:
    return QuestionLineage(
        question_lineage_id=RelationId(row["id"]),
        parent_question_id=QuestionId(row["parent_question_id"]),
        child_question_id=QuestionId(row["child_question_id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        transformation_type=LineageTransformationType(row["transformation_type"]),
        producer_origin=QuestionOrigin(row["producer_origin"]),
        ai_generation_id=(
            None if row["ai_generation_id"] is None else GenerationId(row["ai_generation_id"])
        ),
        created_at=row["created_at"],
    )


__all__ = ["QuestionRepository", "SqlAlchemyQuestionRepository"]
