"""T1 domain tests: request Workspace context.

Covers PKG-01's mandatory adversarial attacks "missing Workspace" and
"forged Workspace context".
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.workspace_context import (
    WorkspaceContext,
    WorkspaceNotFoundError,
    resolve_workspace_context,
)
from persistence.tables import users_table, workspaces_table
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository, WorkspaceRecord
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import UserId, WorkspaceId
from semantic_types.versions import RecordVersion


def _principal(user_id: UserId) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        authentication_session_ref="session-1",
        authentication_time=datetime(2030, 1, 1, tzinfo=timezone.utc),
        issuer_ref="https://issuer.example.test",
    )


def test_resolve_workspace_context_succeeds_for_an_existing_workspace(
    db_connection: sa.Connection,
) -> None:
    owner_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(users_table).values(
            id=owner_id,
            email="owner3@example.test",
            name="Owner",
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    workspace_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name="Real Workspace",
            owner_id=owner_id,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )

    repository = SqlAlchemyWorkspaceRepository(db_connection)
    principal = _principal(UserId(uuid.uuid4()))

    context = resolve_workspace_context(principal, WorkspaceId(workspace_id), repository)

    assert context.principal == principal
    assert context.workspace.id == WorkspaceId(workspace_id)


def test_resolve_workspace_context_fails_closed_for_missing_workspace(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: missing Workspace."""
    repository = SqlAlchemyWorkspaceRepository(db_connection)
    principal = _principal(UserId(uuid.uuid4()))
    unknown_workspace_id = WorkspaceId(uuid.uuid4())

    with pytest.raises(WorkspaceNotFoundError) as exc_info:
        resolve_workspace_context(principal, unknown_workspace_id, repository)

    assert exc_info.value.workspace_id == unknown_workspace_id


def test_workspace_context_cannot_be_forged_from_a_bare_workspace_id() -> None:
    """Mandatory adversarial attack: forged Workspace context.

    `WorkspaceContext.workspace` requires a `WorkspaceRecord`, not a
    `WorkspaceId` -- constructing one with a bare ID is a type error a
    static checker (mypy) rejects, and even a caller ignoring types
    cannot supply a `WorkspaceRecord` without first obtaining one from
    the repository (there is no public constructor for `WorkspaceRecord`
    other than reading it off a real row -- see
    `SqlAlchemyWorkspaceRepository.get`).
    """
    principal = _principal(UserId(uuid.uuid4()))
    forged_workspace_id = WorkspaceId(uuid.uuid4())

    with pytest.raises(TypeError):
        WorkspaceContext(principal=principal, workspace=forged_workspace_id)  # type: ignore[arg-type]


def test_workspace_context_accepts_only_a_genuine_workspace_record() -> None:
    principal = _principal(UserId(uuid.uuid4()))
    genuine_record = WorkspaceRecord(
        id=WorkspaceId(uuid.uuid4()),
        name="Genuine",
        owner_id=UserId(uuid.uuid4()),
        record_version=RecordVersion(1),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    context = WorkspaceContext(principal=principal, workspace=genuine_record)

    assert context.workspace == genuine_record
