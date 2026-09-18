"""ChallengeRepository: the read-only half of the 14 section 10 port.

Source: 14_IMPLEMENTATION_SEQUENCE.md section 10 (REPOSITORY PORTS):
"`ChallengeRepository`: canonical read and mutation-plan application
inside CommitUnit."

WHY THIS PACKAGE BUILDS ONLY THE "CANONICAL READ" HALF
------------------------------------------------------------
Mirrors `persistence.session_repository`'s own precedent exactly (PKG-14):
PKG-05 deferred the whole port because neither CommitUnit nor the
boundary pipeline existed yet. Both now exist, but 14 assigns PKG-15 no
Challenge *mutation* -- `OpenDecisionConsideration` only reads the
Challenge to prove it exists and to cross-check Workspace/version
freshness (AC-09-001), it never writes to `challenges`. This module
therefore materializes exactly the "canonical read" half of 14's own
port description, honestly leaving "mutation-plan application inside
CommitUnit" to whichever future package first needs to mutate a
Challenge.

`get` returns the real `domain.challenge.Challenge` via
`persistence.challenge_session_mapping.challenge_from_row` (PKG-05's
own row-to-domain mapper) rather than re-deriving that mapping a
second time.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from domain.challenge import Challenge
from domain.decision import challenge_target_ref
from semantic_types.ids import ChallengeId
from semantic_types.versions import RecordVersion

from persistence.challenge_session_mapping import challenge_from_row
from persistence.tables import challenges_table


@runtime_checkable
class ChallengeRepository(Protocol):
    """Port: Challenge canonical current-version read only (14 section
    10, partial -- see module docstring).
    """

    def get(self, challenge_id: ChallengeId) -> Challenge | None:
        """The current `challenges` row for `challenge_id`, or `None`
        if it does not exist. Always a fresh read -- no caching."""
        ...


class SqlAlchemyChallengeRepository:
    """`ChallengeRepository` backed by `challenges` via a SQLAlchemy
    Core connection. Read-only by construction -- no `create`/`update`
    method exists.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(self, challenge_id: ChallengeId) -> Challenge | None:
        stmt = sa.select(challenges_table).where(challenges_table.c.id == challenge_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else challenge_from_row(dict(row))


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
