"""WorkspaceRepository: authoritative Workspace reads.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`WorkspaceRepository`: authoritative Workspace reads, governed
mutation plan only." PKG-01's `PUBLIC_INTERFACES` authorizes only the
*read* half — "WorkspaceRepository read contracts". The governed
mutation plan (Workspace creation/update through a Command inside a
CommitUnit) is not implemented here; Workspace creation is additionally
blocked upstream by `HARD-DEP-001` (legitimate first Workspace
governance-root bootstrap) until that is resolved.

Non-collapse rule (14 §10): "No repository returns an authority
conclusion." `get()` returns a plain `WorkspaceRecord` or `None` — it
never returns ALLOW/DENY, membership, or any authority-shaped result.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from semantic_types.ids import UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import workspaces_table


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
    """Port: authoritative Workspace reads only (14 §10)."""

    def get(self, workspace_id: WorkspaceId) -> WorkspaceRecord | None:
        """Return the canonical `WorkspaceRecord` for `workspace_id`, or
        `None` if no such Workspace exists. Never raises for "not
        found" — the caller (14 §11 BND-002 preparation) decides what
        "not found" means for its own consequential path.
        """
        ...


class SqlAlchemyWorkspaceRepository:
    """`WorkspaceRepository` backed by the `workspaces`/`users` tables
    via a SQLAlchemy Core connection.

    Read-only by construction: this class has no `create`/`update`
    method. A future package materializing the governed mutation plan
    adds that through `packages/commit`, not by extending this class
    with a write method.
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


__all__ = ["WorkspaceRecord", "WorkspaceRepository", "SqlAlchemyWorkspaceRepository"]
