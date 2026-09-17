"""T1 domain tests: WorkspaceRepository (read-only), against real PostgreSQL.

Covers PKG-01's mandatory adversarial attack "cross-Workspace ID":
reading Workspace A must never return Workspace B's row, proven
against two genuinely persisted rows, not mocks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from persistence.tables import users_table, workspaces_table
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
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


def _insert_workspace(connection: sa.Connection, *, name: str, owner_id: UserId) -> WorkspaceId:
    workspace_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name=name,
            owner_id=owner_id.value,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return WorkspaceId(workspace_id)


def test_get_returns_none_for_unknown_workspace(db_connection: sa.Connection) -> None:
    repository = SqlAlchemyWorkspaceRepository(db_connection)
    assert repository.get(WorkspaceId(uuid.uuid4())) is None


def test_get_returns_the_correct_record(db_connection: sa.Connection) -> None:
    owner_id = _insert_user(db_connection, email="owner@example.test")
    workspace_id = _insert_workspace(db_connection, name="Acme", owner_id=owner_id)

    repository = SqlAlchemyWorkspaceRepository(db_connection)
    record = repository.get(workspace_id)

    assert record is not None
    assert record.id == workspace_id
    assert record.name == "Acme"
    assert record.owner_id == owner_id
    assert record.record_version.value == 1


def test_get_never_returns_a_different_workspaces_row(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace ID."""
    owner_id = _insert_user(db_connection, email="owner2@example.test")
    workspace_a = _insert_workspace(db_connection, name="Workspace A", owner_id=owner_id)
    workspace_b = _insert_workspace(db_connection, name="Workspace B", owner_id=owner_id)

    repository = SqlAlchemyWorkspaceRepository(db_connection)

    record_a = repository.get(workspace_a)
    record_b = repository.get(workspace_b)

    assert record_a is not None and record_b is not None
    assert record_a.id == workspace_a
    assert record_b.id == workspace_b
    assert record_a.id != record_b.id
    assert record_a.name != record_b.name
