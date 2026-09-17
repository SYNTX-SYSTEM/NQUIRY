"""MembershipRepository and its RoleAssignment reads.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`MembershipRepository`: current and historical membership reads,
governed mutation plan only." PKG-02's `PUBLIC_INTERFACES` authorizes
only the read half.

RoleAssignment reads are exposed from this same repository rather than
a separate `RoleAssignmentRepository`: 09 §23.1 treats RoleAssignment
as a governance-relation *sub-concept* of membership ("Role Is
Separate [table], Use RoleAssignment"), and PKG-02's own
`PUBLIC_INTERFACES` never names a third repository.

Non-collapse rule (14 §10): "No repository returns an authority
conclusion." These reads return raw stored facts (a membership row, a
role-assignment row) — never a computed "is this user authorized"
verdict.

`membership_id`/`role_assignment_id` are plain `uuid.UUID`, not a
wrapped strong-ID type: 14 §5's closed identity list has no
`MembershipId`/`RoleAssignmentId` entry, and 02 §7.6 explains why —
"A persistence join record may receive a technical primary key later.
That does not convert the semantic concept into a standalone domain
thing." (`HumanAuthorityBinding` is different — see
`authority_binding_repository.py`, which does use the closed-list
`AuthorityBindingId`.)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from governance.membership import MembershipStatus, WorkspaceRole
from semantic_types.ids import UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import role_assignments_table, workspace_memberships_table


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    """A `workspace_memberships` row as actually read from storage."""

    id: uuid.UUID
    workspace_id: WorkspaceId
    user_id: UserId
    status: MembershipStatus
    created_at: datetime
    revoked_at: datetime | None
    record_version: RecordVersion


@dataclass(frozen=True, slots=True)
class RoleAssignmentRecord:
    """A `role_assignments` row as actually read from storage."""

    id: uuid.UUID
    workspace_id: WorkspaceId
    membership_id: uuid.UUID
    role: WorkspaceRole
    granted_by_user_id: UserId
    granted_at: datetime
    revoked_at: datetime | None
    record_version: RecordVersion


@runtime_checkable
class MembershipRepository(Protocol):
    """Port: membership and role-assignment reads only (14 §10)."""

    def get_current_membership(
        self, workspace_id: WorkspaceId, user_id: UserId
    ) -> MembershipRecord | None:
        """The ACTIVE membership row for (workspace_id, user_id), or
        `None` if there isn't one — including if the user was never a
        member, or was a member and was revoked."""
        ...

    def list_membership_history(
        self, workspace_id: WorkspaceId, user_id: UserId
    ) -> tuple[MembershipRecord, ...]:
        """Every membership row (ACTIVE and REVOKED) for the pair,
        oldest first — the full historical reconstruction (14 §10)."""
        ...

    def get_current_role(self, membership_id: uuid.UUID) -> RoleAssignmentRecord | None:
        """The role assignment with `revoked_at IS NULL` for this
        membership, or `None`. At most one can exist (enforced by
        `uq_role_assignments_active_per_membership`, 05 GOV-004)."""
        ...

    def list_role_history(self, membership_id: uuid.UUID) -> tuple[RoleAssignmentRecord, ...]:
        """Every role assignment (current and revoked) for this
        membership, oldest first (05 GOV-004: "Role history must be
        reconstructable")."""
        ...


class SqlAlchemyMembershipRepository:
    """`MembershipRepository` backed by `workspace_memberships`/
    `role_assignments` via a SQLAlchemy Core connection. Read-only by
    construction — no `grant`/`revoke`/`assign_role` method exists.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get_current_membership(
        self, workspace_id: WorkspaceId, user_id: UserId
    ) -> MembershipRecord | None:
        stmt = sa.select(workspace_memberships_table).where(
            workspace_memberships_table.c.workspace_id == workspace_id.value,
            workspace_memberships_table.c.user_id == user_id.value,
            workspace_memberships_table.c.status == MembershipStatus.ACTIVE.value,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _membership_record_from_row(row)

    def list_membership_history(
        self, workspace_id: WorkspaceId, user_id: UserId
    ) -> tuple[MembershipRecord, ...]:
        stmt = (
            sa.select(workspace_memberships_table)
            .where(
                workspace_memberships_table.c.workspace_id == workspace_id.value,
                workspace_memberships_table.c.user_id == user_id.value,
            )
            .order_by(workspace_memberships_table.c.created_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_membership_record_from_row(row) for row in rows)

    def get_current_role(self, membership_id: uuid.UUID) -> RoleAssignmentRecord | None:
        stmt = sa.select(role_assignments_table).where(
            role_assignments_table.c.membership_id == membership_id,
            role_assignments_table.c.revoked_at.is_(None),
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _role_assignment_record_from_row(row)

    def list_role_history(self, membership_id: uuid.UUID) -> tuple[RoleAssignmentRecord, ...]:
        stmt = (
            sa.select(role_assignments_table)
            .where(role_assignments_table.c.membership_id == membership_id)
            .order_by(role_assignments_table.c.granted_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_role_assignment_record_from_row(row) for row in rows)


def _membership_record_from_row(row: sa.RowMapping) -> MembershipRecord:
    return MembershipRecord(
        id=row["id"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        user_id=UserId(row["user_id"]),
        status=MembershipStatus(row["status"]),
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
        record_version=RecordVersion(row["record_version"]),
    )


def _role_assignment_record_from_row(row: sa.RowMapping) -> RoleAssignmentRecord:
    return RoleAssignmentRecord(
        id=row["id"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        membership_id=row["membership_id"],
        role=WorkspaceRole(row["role"]),
        granted_by_user_id=UserId(row["granted_by_user_id"]),
        granted_at=row["granted_at"],
        revoked_at=row["revoked_at"],
        record_version=RecordVersion(row["record_version"]),
    )


__all__ = [
    "MembershipRecord",
    "RoleAssignmentRecord",
    "MembershipRepository",
    "SqlAlchemyMembershipRepository",
]
