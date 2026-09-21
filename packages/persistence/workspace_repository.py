"""WorkspaceRepository: authoritative Workspace reads and creation.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`WorkspaceRepository`: authoritative Workspace reads, governed
mutation plan only." PKG-01's `PUBLIC_INTERFACES` authorized only the
*read* half at that time, pending the governed mutation plan --
Workspace creation was additionally blocked upstream by `HARD-DEP-001`
(legitimate first Workspace governance-root bootstrap).

[F01 WU-01.4, human-confirmed 2026-09-21] HARD-DEP-001 is now resolved
(Option A: self-service founder) -- `create()` below is exactly the
"governed mutation plan" this module's own docstring was forward
-referencing, added by `application.workspace_creation_handler.create_workspace`,
the real `CreateWorkspace` Command it did not yet have a caller for.
It is a plain insert, not itself authority-bearing -- the caller is
solely responsible for having already evaluated BND-001 and the
eligibility check before calling it (14 §10's non-collapse rule below
still holds: this repository does not decide whether the write is
allowed, only performs it).

Non-collapse rule (14 §10): "No repository returns an authority
conclusion." `get()` returns a plain `WorkspaceRecord` or `None` — it
never returns ALLOW/DENY, membership, or any authority-shaped result.
`create()` is the same kind of raw fact-recording operation on the
write side.

[F01 WU-01.5] `workspace_target_ref`/`SqlAlchemyWorkspaceVersionReader`
mirror `domain.decision.challenge_target_ref`/
`persistence.challenge_repository.SqlAlchemyChallengeVersionReader`'s
own precedent exactly: a Workspace becomes a commit-sensitive
(`CommandEnvelope.target_refs`/`commit.coordinator.CurrentVersionReader`)
target for the first time once a governed Command mutates something
*under* an already-existing Workspace (`AddMember`,
`application.membership_operations_handler`) rather than the Workspace
row itself (only `CreateWorkspace` writes that row, via `create()`
above, outside `CommitCoordinator` entirely — see
`workspace_creation_handler`'s own docstring for why).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from semantic_types.ids import UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import workspaces_table


def workspace_target_ref(workspace_id: WorkspaceId) -> str:
    """The `CommandEnvelope.target_refs`/`CurrentVersionReader` ref
    string naming a Workspace as a commit-sensitive target."""
    return f"workspace:{workspace_id.value}"


@dataclass(frozen=True, slots=True)
class WorkspaceRecord:
    """A canonical Workspace row as actually read from storage.

    Possessing a `WorkspaceRecord` is exactly the proof 14 §11's
    `CanonicalReadPort` requires before a consequential decision may
    treat a Workspace as real — a bare `WorkspaceId` is not sufficient
    (14 §3 non-collapse: `Object identifiers are never sufficient proof
    of access`, 06 §8 BND-002: "Claimed Workspace IDs are not
    authoritative by themselves.").
    """

    id: WorkspaceId
    name: str
    owner_id: UserId
    record_version: RecordVersion
    created_at: datetime
    updated_at: datetime


@runtime_checkable
class WorkspaceRepository(Protocol):
    """Port: authoritative Workspace reads plus the one governed
    creation write (14 §10)."""

    def get(self, workspace_id: WorkspaceId) -> WorkspaceRecord | None:
        """Return the canonical `WorkspaceRecord` for `workspace_id`, or
        `None` if no such Workspace exists. Never raises for "not
        found" — the caller (14 §11 BND-002 preparation) decides what
        "not found" means for its own consequential path.
        """
        ...

    def create(
        self,
        workspace_id: WorkspaceId,
        *,
        name: str,
        owner_id: UserId,
        created_at: datetime,
    ) -> WorkspaceRecord:
        """Insert a new `workspaces` row at `RecordVersion.initial()`.

        A raw fact-recording write, not an authority decision (module
        docstring) -- the caller must have already evaluated BND-001
        and the eligibility check (`application.workspace_creation_handler`
        is this method's one legitimate caller).
        """
        ...


class SqlAlchemyWorkspaceRepository:
    """`WorkspaceRepository` backed by the `workspaces`/`users` tables
    via a SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get(self, workspace_id: WorkspaceId) -> WorkspaceRecord | None:
        stmt = sa.select(workspaces_table).where(workspaces_table.c.id == workspace_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return WorkspaceRecord(
            id=WorkspaceId(row["id"]),
            name=row["name"],
            owner_id=UserId(row["owner_id"]),
            record_version=RecordVersion(row["record_version"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(
        self,
        workspace_id: WorkspaceId,
        *,
        name: str,
        owner_id: UserId,
        created_at: datetime,
    ) -> WorkspaceRecord:
        record_version = RecordVersion.initial()
        self._connection.execute(
            sa.insert(workspaces_table).values(
                id=workspace_id.value,
                name=name,
                owner_id=owner_id.value,
                record_version=record_version.value,
                created_at=created_at,
                updated_at=created_at,
            )
        )
        return WorkspaceRecord(
            id=workspace_id,
            name=name,
            owner_id=owner_id,
            record_version=record_version,
            created_at=created_at,
            updated_at=created_at,
        )


class SqlAlchemyWorkspaceVersionReader:
    """`commit.coordinator.CurrentVersionReader` reading the REAL,
    fresh `workspaces.record_version` for one Workspace -- no caching,
    mirrors `persistence.challenge_repository.SqlAlchemyChallengeVersionReader`
    exactly. Lives here, not in `application.membership_operations_handler`,
    for the identical reason: `application` may not import `sqlalchemy`
    directly (14 §3.1/§4).
    """

    def __init__(self, connection: sa.Connection, *, workspace_id: WorkspaceId) -> None:
        self._connection = connection
        self._workspace_id = workspace_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != workspace_target_ref(self._workspace_id):
            return None
        stmt = sa.select(workspaces_table.c.record_version).where(
            workspaces_table.c.id == self._workspace_id.value
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


__all__ = [
    "WorkspaceRecord",
    "WorkspaceRepository",
    "SqlAlchemyWorkspaceRepository",
    "workspace_target_ref",
    "SqlAlchemyWorkspaceVersionReader",
]
