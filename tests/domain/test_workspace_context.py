"""T1 domain tests: request Workspace context.

Covers PKG-01's mandatory adversarial attacks "missing Workspace" and
"forged Workspace context", plus F01 WU-01.3's own completion of 11
§7's full formula (membership-consistency check) and its mandatory
adversarial attack "cross-Workspace isolation" (19 §21 TESTS FIRST).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.workspace_context import (
    NotAWorkspaceMemberError,
    WorkspaceContext,
    WorkspaceNotFoundError,
    resolve_workspace_context,
)
from governance.membership import MembershipStatus
from persistence.membership_repository import (
    MembershipRecord,
    SqlAlchemyMembershipRepository,
)
from persistence.tables import users_table, workspace_memberships_table, workspaces_table
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


def _insert_user(connection: sa.Connection, *, email: str) -> uuid.UUID:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Owner",
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return user_id


def _insert_workspace(connection: sa.Connection, *, owner_id: uuid.UUID) -> uuid.UUID:
    workspace_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name="Real Workspace",
            owner_id=owner_id,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return workspace_id


def _insert_active_membership(
    connection: sa.Connection, *, workspace_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            record_version=1,
        )
    )


def test_resolve_workspace_context_succeeds_for_a_member_of_an_existing_workspace(
    db_connection: sa.Connection,
) -> None:
    owner_id = _insert_user(db_connection, email="owner3@example.test")
    workspace_id = _insert_workspace(db_connection, owner_id=owner_id)
    _insert_active_membership(db_connection, workspace_id=workspace_id, user_id=owner_id)

    workspace_repository = SqlAlchemyWorkspaceRepository(db_connection)
    membership_repository = SqlAlchemyMembershipRepository(db_connection)
    principal = _principal(UserId(owner_id))

    context = resolve_workspace_context(
        principal, WorkspaceId(workspace_id), workspace_repository, membership_repository
    )

    assert context.principal == principal
    assert context.workspace.id == WorkspaceId(workspace_id)
    assert context.membership.user_id == UserId(owner_id)
    assert context.membership.workspace_id == WorkspaceId(workspace_id)


def test_resolve_workspace_context_fails_closed_for_missing_workspace(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: missing Workspace."""
    workspace_repository = SqlAlchemyWorkspaceRepository(db_connection)
    membership_repository = SqlAlchemyMembershipRepository(db_connection)
    principal = _principal(UserId(uuid.uuid4()))
    unknown_workspace_id = WorkspaceId(uuid.uuid4())

    with pytest.raises(WorkspaceNotFoundError) as exc_info:
        resolve_workspace_context(
            principal, unknown_workspace_id, workspace_repository, membership_repository
        )

    assert exc_info.value.workspace_id == unknown_workspace_id


def test_resolve_workspace_context_fails_closed_for_a_non_member(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: cross-Workspace isolation. The
    Workspace is real, but the requesting principal has never been
    granted membership in it -- a real Workspace existing must never
    be sufficient on its own."""
    owner_id = _insert_user(db_connection, email="owner-only@example.test")
    workspace_id = _insert_workspace(db_connection, owner_id=owner_id)
    outsider_id = _insert_user(db_connection, email="outsider@example.test")

    workspace_repository = SqlAlchemyWorkspaceRepository(db_connection)
    membership_repository = SqlAlchemyMembershipRepository(db_connection)
    principal = _principal(UserId(outsider_id))

    with pytest.raises(NotAWorkspaceMemberError) as exc_info:
        resolve_workspace_context(
            principal, WorkspaceId(workspace_id), workspace_repository, membership_repository
        )

    assert exc_info.value.workspace_id == WorkspaceId(workspace_id)


def test_resolve_workspace_context_fails_closed_for_a_revoked_member(
    db_connection: sa.Connection,
) -> None:
    """A membership that once existed but was revoked must be treated
    identically to never having been a member -- no stale-context
    fallback."""
    owner_id = _insert_user(db_connection, email="revoked-owner@example.test")
    workspace_id = _insert_workspace(db_connection, owner_id=owner_id)
    former_member_id = _insert_user(db_connection, email="former-member@example.test")
    db_connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=former_member_id,
            status="REVOKED",
            created_at=datetime.now(timezone.utc),
            revoked_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )

    workspace_repository = SqlAlchemyWorkspaceRepository(db_connection)
    membership_repository = SqlAlchemyMembershipRepository(db_connection)
    principal = _principal(UserId(former_member_id))

    with pytest.raises(NotAWorkspaceMemberError):
        resolve_workspace_context(
            principal, WorkspaceId(workspace_id), workspace_repository, membership_repository
        )


def test_workspace_context_cannot_be_forged_from_bare_ids() -> None:
    """Mandatory adversarial attack: forged Workspace context.

    `WorkspaceContext.workspace`/`.membership` require genuine
    `WorkspaceRecord`/`MembershipRecord`, not bare IDs -- constructing
    one with bare values is a type error a static checker (mypy)
    rejects, and even a caller ignoring types cannot supply a genuine
    record without first obtaining one from the repository.
    """
    principal = _principal(UserId(uuid.uuid4()))
    forged_workspace_id = WorkspaceId(uuid.uuid4())
    genuine_membership = MembershipRecord(
        id=uuid.uuid4(),
        workspace_id=forged_workspace_id,
        user_id=principal.user_id,
        status=MembershipStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        revoked_at=None,
        record_version=RecordVersion(1),
    )

    with pytest.raises(TypeError):
        WorkspaceContext(
            principal=principal,
            workspace=forged_workspace_id,  # type: ignore[arg-type]
            membership=genuine_membership,
        )


def test_workspace_context_accepts_only_genuine_records() -> None:
    principal = _principal(UserId(uuid.uuid4()))
    genuine_workspace = WorkspaceRecord(
        id=WorkspaceId(uuid.uuid4()),
        name="Genuine",
        owner_id=UserId(uuid.uuid4()),
        record_version=RecordVersion(1),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    genuine_membership = MembershipRecord(
        id=uuid.uuid4(),
        workspace_id=genuine_workspace.id,
        user_id=principal.user_id,
        status=MembershipStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        revoked_at=None,
        record_version=RecordVersion(1),
    )

    context = WorkspaceContext(
        principal=principal, workspace=genuine_workspace, membership=genuine_membership
    )

    assert context.workspace == genuine_workspace
    assert context.membership == genuine_membership
