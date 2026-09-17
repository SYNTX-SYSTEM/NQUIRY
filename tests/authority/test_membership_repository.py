"""T3 authority tests: MembershipRepository, against real PostgreSQL."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import (
    role_assignments_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from semantic_types.ids import UserId, WorkspaceId


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Test User",
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return UserId(user_id)


def _insert_workspace(connection: sa.Connection, *, owner_id: UserId) -> WorkspaceId:
    workspace_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name="W",
            owner_id=owner_id.value,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return WorkspaceId(workspace_id)


def _insert_membership(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    user_id: UserId,
    status: MembershipStatus = MembershipStatus.ACTIVE,
    revoked_at: datetime | None = None,
) -> uuid.UUID:
    membership_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=membership_id,
            workspace_id=workspace_id.value,
            user_id=user_id.value,
            status=status.value,
            created_at=datetime.now(timezone.utc),
            revoked_at=revoked_at,
            record_version=1,
        )
    )
    return membership_id


def _insert_role(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    membership_id: uuid.UUID,
    role: WorkspaceRole,
    granted_by: UserId,
    revoked_at: datetime | None = None,
) -> uuid.UUID:
    role_id = uuid.uuid4()
    connection.execute(
        sa.insert(role_assignments_table).values(
            id=role_id,
            workspace_id=workspace_id.value,
            membership_id=membership_id,
            role=role.value,
            granted_by_user_id=granted_by.value,
            granted_at=datetime.now(timezone.utc),
            revoked_at=revoked_at,
            record_version=1,
        )
    )
    return role_id


def test_get_current_membership_returns_none_when_absent(db_connection: sa.Connection) -> None:
    repository = SqlAlchemyMembershipRepository(db_connection)
    assert (
        repository.get_current_membership(WorkspaceId(uuid.uuid4()), UserId(uuid.uuid4())) is None
    )


def test_get_current_membership_returns_active_row(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=owner)

    repository = SqlAlchemyMembershipRepository(db_connection)
    record = repository.get_current_membership(workspace_id, owner)

    assert record is not None
    assert record.status == MembershipStatus.ACTIVE
    assert record.user_id == owner


def test_get_current_membership_excludes_revoked(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner2@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member@test.local")
    _insert_membership(
        db_connection,
        workspace_id=workspace_id,
        user_id=member,
        status=MembershipStatus.REVOKED,
        revoked_at=datetime.now(timezone.utc),
    )

    repository = SqlAlchemyMembershipRepository(db_connection)
    assert repository.get_current_membership(workspace_id, member) is None


def test_list_membership_history_includes_revoked_and_active(db_connection: sa.Connection) -> None:
    """A user who left and rejoined the same Workspace has two
    membership rows for the same (workspace, user) pair: one REVOKED,
    one ACTIVE. The partial unique index only forbids two simultaneous
    ACTIVE rows, so this is a legitimate history, and both rows must
    surface here even though `get_current_membership` only ever
    returns the ACTIVE one.
    """
    owner = _insert_user(db_connection, email="owner3@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member3@test.local")
    _insert_membership(
        db_connection,
        workspace_id=workspace_id,
        user_id=member,
        status=MembershipStatus.REVOKED,
        revoked_at=datetime.now(timezone.utc),
    )
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)

    repository = SqlAlchemyMembershipRepository(db_connection)
    history = repository.list_membership_history(workspace_id, member)

    assert len(history) == 2
    assert history[0].status == MembershipStatus.REVOKED
    assert history[1].status == MembershipStatus.ACTIVE


def test_role_current_and_history(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner4@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=owner)
    _insert_role(
        db_connection,
        workspace_id=workspace_id,
        membership_id=membership_id,
        role=WorkspaceRole.OWNER,
        granted_by=owner,
        revoked_at=datetime.now(timezone.utc),
    )
    _insert_role(
        db_connection,
        workspace_id=workspace_id,
        membership_id=membership_id,
        role=WorkspaceRole.FACILITATOR,
        granted_by=owner,
    )

    repository = SqlAlchemyMembershipRepository(db_connection)

    current = repository.get_current_role(membership_id)
    assert current is not None
    assert current.role == WorkspaceRole.FACILITATOR

    history = repository.list_role_history(membership_id)
    assert len(history) == 2
    assert history[0].role == WorkspaceRole.OWNER
    assert history[1].role == WorkspaceRole.FACILITATOR
