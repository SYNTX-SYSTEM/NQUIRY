"""QuestionSelectionRepository: the PUBLIC_INTERFACES port 14 section 10
assigns for QuestionSelection.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`QuestionSelectionRepository`: authority-bearing relation read/write
only through governed selection Command."

WHY `create` DOES NOT CATCH OR TRANSLATE DATABASE ERRORS
------------------------------------------------------------
Unlike `BurstRepository`'s transition methods (an application-computed
optimistic-concurrency guard the database itself cannot express, so a
lost race is silently 0 affected rows -- an exception has to be
manufactured to surface it at all), every failure mode this method can
hit is already a real, informative database exception: the composite
Session/Question foreign keys (`sa.exc.IntegrityError`), the
`UNIQUE(session_id, question_id, selection_type)` constraint
(`sa.exc.IntegrityError`), the partial-unique "at most one PRIMARY"
index (`sa.exc.IntegrityError`), or the cardinality-cap trigger
(`sa.exc.DBAPIError`, a raised PL/pgSQL exception -- same class the
existing `audit_events` immutability triggers surface as, per
`tests/command_commit_event/test_audit.py`). This method lets each
propagate directly, the same choice `persistence.audit_repository.
SqlAlchemyAuditRepository.append` already made -- inventing a wrapper
exception here would manufacture a translation this codebase's own
precedent does not require for a genuine DB-raised error. Any exception
raised here, reached through a `commit.coordinator.MutationExecutor`
wrapper, is caught by `CommitCoordinator._commit_inner`'s own generic
rollback handling and surfaces as `CommitFailedPrecommit` -- 09 section
121's own "Before commit: FAILED_PRECOMMIT", exactly the disposition
04's own AUTHORITY PRECONDITIONS name for a cardinality/conflict
violation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.question_selection import QuestionSelection, SelectionType
from semantic_types.ids import (
    AuthorityBindingId,
    QuestionId,
    QuestionSelectionId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from persistence.tables import question_selections_table


@runtime_checkable
class QuestionSelectionRepository(Protocol):
    """Port: QuestionSelection create/read only (14 section 10). No
    update method exists -- 09 section 33.1: "That stored binding
    reference does not authorize future changes"; there is no
    legitimate mutation of an existing selection row.
    """

    def create(self, selection: QuestionSelection) -> None:
        """Persist a new QuestionSelection row. Raises a real database
        exception (never silently ignored) on any constraint violation
        -- see module docstring for exactly which."""
        ...

    def get(self, question_selection_id: QuestionSelectionId) -> QuestionSelection | None:
        """The QuestionSelection row for this id, or `None` if it does
        not exist."""
        ...

    def list_for_session(self, session_id: SessionId) -> tuple[QuestionSelection, ...]:
        """Every QuestionSelection currently recorded for this Session,
        oldest first."""
        ...


class SqlAlchemyQuestionSelectionRepository:
    """`QuestionSelectionRepository` backed by `question_selections` via
    a SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(self, selection: QuestionSelection) -> None:
        self._connection.execute(sa.insert(question_selections_table).values(**_to_row(selection)))

    def get(self, question_selection_id: QuestionSelectionId) -> QuestionSelection | None:
        stmt = sa.select(question_selections_table).where(
            question_selections_table.c.id == question_selection_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _from_row(row)

    def list_for_session(self, session_id: SessionId) -> tuple[QuestionSelection, ...]:
        stmt = (
            sa.select(question_selections_table)
            .where(question_selections_table.c.session_id == session_id.value)
            .order_by(question_selections_table.c.selected_at)
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_from_row(row) for row in rows)


def _to_row(selection: QuestionSelection) -> dict[str, object]:
    return {
        "id": selection.question_selection_id.value,
        "workspace_id": selection.workspace_id.value,
        "session_id": selection.session_id.value,
        "question_id": selection.question_id.value,
        "selection_type": selection.selection_type.value,
        "selected_by_user_id": selection.selected_by_user_id.value,
        "human_authority_binding_id": selection.human_authority_binding_id.value,
        "selected_at": selection.selected_at,
        "record_version": selection.record_version.value,
    }


def _from_row(row: sa.RowMapping) -> QuestionSelection:
    return QuestionSelection(
        question_selection_id=QuestionSelectionId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        session_id=SessionId(row["session_id"]),
        question_id=QuestionId(row["question_id"]),
        selection_type=SelectionType(row["selection_type"]),
        selected_by_user_id=UserId(row["selected_by_user_id"]),
        human_authority_binding_id=AuthorityBindingId(row["human_authority_binding_id"]),
        selected_at=row["selected_at"],
        record_version=RecordVersion(row["record_version"]),
    )


__all__ = ["QuestionSelectionRepository", "SqlAlchemyQuestionSelectionRepository"]
