"""ChallengeRepository: canonical Challenge reads plus the one governed
creation write (14 section 10 port).

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`ChallengeRepository`: canonical read and mutation-plan application
inside CommitUnit."

WHY THIS MODULE WAS READ-ONLY UNTIL F02 WU-02.1
------------------------------------------------------------
Mirrors `persistence.session_repository`'s own precedent exactly (PKG-14):
PKG-05 deferred the whole port because neither CommitUnit nor the
boundary pipeline existed yet. Both now existed by PKG-15, but 14
assigned PKG-15 no Challenge *mutation* -- `OpenDecisionConsideration`
only reads the Challenge to prove it exists and to cross-check
Workspace/version freshness (AC-09-001), it never writes to
`challenges`. `create()` below is the real "mutation-plan application
inside CommitUnit" half this module's own docstring always deferred,
now added by `application.challenge_creation_handler.create_challenge`
(F02 WU-02.1) -- the same "read half first, write half once a real
governed caller exists" sequencing `WorkspaceRepository.create()`
(F01 WU-01.4b) already established for the identical reason.

`get` returns the real `domain.challenge.Challenge` via
`persistence.challenge_session_mapping.challenge_from_row` (PKG-05's
own row-to-domain mapper) rather than re-deriving that mapping a
second time. `create()` is a plain fact-recording insert, not itself
authority-bearing (14 section 10 non-collapse: "No repository returns
an authority conclusion") -- the caller must have already evaluated
BND-001..004 before calling it.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.challenge import Challenge
from domain.decision import challenge_target_ref
from semantic_types.ids import ChallengeId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.challenge_session_mapping import challenge_from_row
from persistence.tables import challenges_table


@runtime_checkable
class ChallengeRepository(Protocol):
    """Port: Challenge canonical reads plus the one governed creation
    write (14 section 10).
    """

    def get(self, challenge_id: ChallengeId) -> Challenge | None:
        """The current `challenges` row for `challenge_id`, or `None`
        if it does not exist. Always a fresh read -- no caching."""
        ...

    def create(
        self,
        challenge_id: ChallengeId,
        *,
        workspace_id: WorkspaceId,
        title: str,
        description: str | None,
        context: str | None,
        desired_outcome: str | None,
        constraints: str | None,
        stakeholders: str | None,
        created_at: datetime,
    ) -> Challenge:
        """Insert a new `challenges` row at `RecordVersion.initial()`.
        A raw fact-recording write, not an authority decision (module
        docstring) -- `application.challenge_creation_handler.create_challenge`
        is this method's one legitimate caller."""
        ...


class SqlAlchemyChallengeRepository:
    """`ChallengeRepository` backed by `challenges` via a SQLAlchemy
    Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(self, challenge_id: ChallengeId) -> Challenge | None:
        stmt = sa.select(challenges_table).where(challenges_table.c.id == challenge_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else challenge_from_row(dict(row))

    def create(
        self,
        challenge_id: ChallengeId,
        *,
        workspace_id: WorkspaceId,
        title: str,
        description: str | None,
        context: str | None,
        desired_outcome: str | None,
        constraints: str | None,
        stakeholders: str | None,
        created_at: datetime,
    ) -> Challenge:
        record_version = RecordVersion.initial()
        self._connection.execute(
            sa.insert(challenges_table).values(
                id=challenge_id.value,
                workspace_id=workspace_id.value,
                title=title,
                description=description,
                context=context,
                desired_outcome=desired_outcome,
                constraints=constraints,
                stakeholders=stakeholders,
                created_at=created_at,
                updated_at=created_at,
                record_version=record_version.value,
            )
        )
        return Challenge(
            challenge_id=challenge_id,
            workspace_id=workspace_id,
            title=title,
            description=description,
            context=context,
            desired_outcome=desired_outcome,
            constraints=constraints,
            stakeholders=stakeholders,
            created_at=created_at,
            updated_at=created_at,
            record_version=record_version,
        )


class SqlAlchemyChallengeVersionReader:
    """`commit.coordinator.CurrentVersionReader` reading the REAL,
    fresh `challenges.record_version` for one Challenge -- no caching,
    mirrors `persistence.session_repository.SqlAlchemySessionVersionReader`
    exactly. Lives here, not in `application.human_decision_handler`,
    for the identical reason: `application` may not import `sqlalchemy`
    directly (14 section 4's forbidden-dependency matrix).
    """

    def __init__(self, connection: sa.Connection, *, challenge_id: ChallengeId) -> None:
        self._connection = connection
        self._challenge_id = challenge_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != challenge_target_ref(self._challenge_id):
            return None
        stmt = sa.select(challenges_table.c.record_version).where(
            challenges_table.c.id == self._challenge_id.value
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


__all__ = [
    "ChallengeRepository",
    "SqlAlchemyChallengeRepository",
    "SqlAlchemyChallengeVersionReader",
]
