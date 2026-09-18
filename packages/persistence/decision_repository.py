"""DecisionRepository: the PUBLIC_INTERFACES port 14 section 10 names
for Decision.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`DecisionRepository`: read and governed human Decision mutation."

WHY `record_decision` TAKES AN `expected_record_version` GUARD, LIKE
`BurstRepository`'s OWN TRANSITION METHODS
------------------------------------------------------------------------
`RECORD_HUMAN_DECISION` (03 section 36 TRN-DEC-002) mutates an EXISTING
Decision row (UNDER_CONSIDERATION -> DECIDED) -- a real optimistic-
concurrency race is possible (two DECISION_RIGHT holders racing to
record the same Decision). Mirrors `persistence.burst_repository.
BurstRepository`'s own guarded-UPDATE-returns-0-rows -> `DecisionConflict`
pattern exactly, the second, narrower line of defense behind BND-014's
own application-layer version check (mandatory adversarial attack:
"concurrent Commands" / persistence/concurrency category).

WHY `create` HAS NO SUCH GUARD
------------------------------------------------------------------------
`OPEN_DECISION_CONSIDERATION` (TRN-DEC-001) creates a brand-new row --
there is no prior version to race against. Any race here manifests as
a primary-key collision, a real database exception this method lets
propagate directly (same choice `persistence.question_selection_repository.
SqlAlchemyQuestionSelectionRepository.create` already made for its own
create-only method).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

import sqlalchemy as sa
from domain.decision import Decision, DecisionState, decision_target_ref
from semantic_types.ids import (
    AuthorityBindingId,
    ChallengeId,
    DecisionId,
    QuestionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion

from persistence.tables import decisions_table


class DecisionConflict(Exception):
    """Raised by `record_decision` when its own expected-version-guarded
    UPDATE affects zero rows -- a race between BND-014's fresh read and
    this attempt's actual write, or a Decision that does not exist at
    all.
    """


@runtime_checkable
class DecisionRepository(Protocol):
    """Port: Decision create/read/governed-record-decision only (14
    section 10). No generic update method exists -- the only mutation
    this port exposes is the one 03 section 36 TRN-DEC-002 names.
    """

    def create(self, decision: Decision) -> None:
        """Persist a new Decision row in `UNDER_CONSIDERATION`. Raises
        a real database exception on any constraint violation."""
        ...

    def get(self, decision_id: DecisionId) -> Decision | None:
        """The Decision row for this id, or `None` if it does not
        exist."""
        ...

    def record_decision(
        self,
        *,
        decision_id: DecisionId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        decided_by_user_id: UserId,
        selected_option: str,
        rationale: str | None,
        confidence: str | None,
        decided_at: datetime,
        provenance_ref: UUID | None = None,
    ) -> None:
        """03 TRN-DEC-002: UNDER_CONSIDERATION -> DECIDED. Raises
        `DecisionConflict` if `expected_record_version` no longer
        matches the stored row (including "no such row")."""
        ...


class SqlAlchemyDecisionRepository:
    """`DecisionRepository` backed by `decisions` via a SQLAlchemy Core
    connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(self, decision: Decision) -> None:
        self._connection.execute(sa.insert(decisions_table).values(**_to_row(decision)))

    def get(self, decision_id: DecisionId) -> Decision | None:
        stmt = sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _from_row(row)

    def record_decision(
        self,
        *,
        decision_id: DecisionId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        decided_by_user_id: UserId,
        selected_option: str,
        rationale: str | None,
        confidence: str | None,
        decided_at: datetime,
        provenance_ref: UUID | None = None,
    ) -> None:
        result = self._connection.execute(
            sa.update(decisions_table)
            .where(
                decisions_table.c.id == decision_id.value,
                decisions_table.c.workspace_id == workspace_id.value,
                decisions_table.c.record_version == expected_record_version.value,
            )
            .values(
                state=DecisionState.DECIDED.value,
                decided_by_user_id=decided_by_user_id.value,
                selected_option=selected_option,
                rationale=rationale,
                confidence=confidence,
                decided_at=decided_at,
                provenance_ref=provenance_ref,
                record_version=expected_record_version.next().value,
            )
        )
        if result.rowcount == 0:
            raise DecisionConflict(
                f"decision {decision_id!r} not found at workspace {workspace_id!r} with "
                f"expected record_version {expected_record_version.value}"
            )


class SqlAlchemyDecisionVersionReader:
    """`commit.coordinator.CurrentVersionReader` reading the REAL, fresh
    `decisions.record_version` for one Decision -- no caching. Used
    only by `RecordHumanDecision` (the Decision already exists by then);
    `OpenDecisionConsideration` uses
    `persistence.challenge_repository.SqlAlchemyChallengeVersionReader`
    instead (see `domain.decision`'s own module docstring for why the
    newly-created Decision itself is never a `target_ref`).
    """

    def __init__(self, connection: sa.Connection, *, decision_id: DecisionId) -> None:
        self._connection = connection
        self._decision_id = decision_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != decision_target_ref(self._decision_id):
            return None
        stmt = sa.select(decisions_table.c.record_version).where(
            decisions_table.c.id == self._decision_id.value
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


def _to_row(decision: Decision) -> dict[str, object]:
    return {
        "id": decision.decision_id.value,
        "workspace_id": decision.workspace_id.value,
        "challenge_id": decision.challenge_id.value,
        "decision_question_ref": (
            None if decision.decision_question_ref is None else decision.decision_question_ref.value
        ),
        "decision_question_text": decision.decision_question_text,
        "options": list(decision.options),
        "criteria": list(decision.criteria),
        "selected_option": decision.selected_option,
        "rationale": decision.rationale,
        "confidence": decision.confidence,
        "state": decision.state.value,
        "opened_by_user_id": decision.opened_by_user_id.value,
        "decision_authority_binding_id": decision.decision_authority_binding_id.value,
        "decided_by_user_id": (
            None if decision.decided_by_user_id is None else decision.decided_by_user_id.value
        ),
        "created_at": decision.created_at,
        "decided_at": decision.decided_at,
        "record_version": decision.record_version.value,
        "provenance_ref": decision.provenance_ref,
    }


def _from_row(row: sa.RowMapping) -> Decision:
    return Decision(
        decision_id=DecisionId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        challenge_id=ChallengeId(row["challenge_id"]),
        decision_question_ref=(
            None
            if row["decision_question_ref"] is None
            else QuestionId(row["decision_question_ref"])
        ),
        decision_question_text=row["decision_question_text"],
        options=tuple(row["options"] or ()),
        criteria=tuple(row["criteria"] or ()),
        selected_option=row["selected_option"],
        rationale=row["rationale"],
        confidence=row["confidence"],
        state=DecisionState(row["state"]),
        opened_by_user_id=UserId(row["opened_by_user_id"]),
        decision_authority_binding_id=AuthorityBindingId(row["decision_authority_binding_id"]),
        decided_by_user_id=(
            None if row["decided_by_user_id"] is None else UserId(row["decided_by_user_id"])
        ),
        created_at=row["created_at"],
        decided_at=row["decided_at"],
        record_version=RecordVersion(row["record_version"]),
        provenance_ref=row["provenance_ref"],
    )


__all__ = [
    "DecisionConflict",
    "DecisionRepository",
    "SqlAlchemyDecisionRepository",
    "SqlAlchemyDecisionVersionReader",
]
