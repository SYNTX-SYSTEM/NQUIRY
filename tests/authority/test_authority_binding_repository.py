"""T3 authority tests: AuthorityBindingRepository, against real PostgreSQL.

Covers three of PKG-02's mandatory adversarial attacks: "revoked HABB",
"wrong Workspace binding", and "Owner assumed superuser" — plus the
conservative non-collapse boundary this repository deliberately does
not cross ("absent membership": a stale ACTIVE binding is still
returned raw, proving this layer does not silently resolve
effectiveness).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.tables import (
    human_authority_bindings_table,
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
) -> None:
    connection.execute(
        sa.insert(role_assignments_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            membership_id=membership_id,
            role=role.value,
            granted_by_user_id=granted_by.value,
            granted_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )


def _insert_binding(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    granted_by: UserId,
    authority_class: AuthorityClass = AuthorityClass.DECISION_RIGHT,
    scope_id: uuid.UUID | None = None,
    state: AuthorityBindingState = AuthorityBindingState.ACTIVE,
    revoked_by: UserId | None = None,
    revoked_at: datetime | None = None,
) -> uuid.UUID:
    binding_id = uuid.uuid4()
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=human_user_id.value,
            authority_class=authority_class.value,
            scope_type="DECISION",
            scope_id=scope_id or uuid.uuid4(),
            authority_source="WORKSPACE_GOVERNANCE_ROOT",
            granted_by_user_id=granted_by.value,
            granted_at=datetime.now(timezone.utc),
            revoked_by_user_id=revoked_by.value if revoked_by else None,
            revoked_at=revoked_at,
            state=state.value,
            record_version=1,
        )
    )
    return binding_id


def test_list_current_bindings_excludes_revoked(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: revoked HABB."""
    owner = _insert_user(db_connection, email="owner@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        state=AuthorityBindingState.REVOKED,
        revoked_by=owner,
        revoked_at=datetime.now(timezone.utc),
    )

    repository = SqlAlchemyAuthorityBindingRepository(db_connection)

    assert repository.list_current_bindings(workspace_id, member) == ()
    history = repository.list_binding_history(workspace_id, member)
    assert len(history) == 1
    assert history[0].state == AuthorityBindingState.REVOKED


def test_list_current_bindings_returns_active(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner2@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member2@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    _insert_binding(
        db_connection, workspace_id=workspace_id, human_user_id=member, granted_by=owner
    )

    repository = SqlAlchemyAuthorityBindingRepository(db_connection)
    current = repository.list_current_bindings(workspace_id, member)

    assert len(current) == 1
    assert current[0].state == AuthorityBindingState.ACTIVE
    assert current[0].authority_class == AuthorityClass.DECISION_RIGHT


def test_wrong_workspace_binding_is_not_returned(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong Workspace binding."""
    owner = _insert_user(db_connection, email="owner3@test.local")
    workspace_a = _insert_workspace(db_connection, owner_id=owner)
    workspace_b = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member3@test.local")
    _insert_membership(db_connection, workspace_id=workspace_a, user_id=member)
    _insert_membership(db_connection, workspace_id=workspace_b, user_id=member)
    _insert_binding(db_connection, workspace_id=workspace_a, human_user_id=member, granted_by=owner)

    repository = SqlAlchemyAuthorityBindingRepository(db_connection)

    assert len(repository.list_current_bindings(workspace_a, member)) == 1
    assert repository.list_current_bindings(workspace_b, member) == ()


def test_stale_active_binding_is_not_silently_resolved_against_membership(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: absent membership — from the
    conservative-boundary direction. This repository must NOT
    cross-check membership effectiveness (that is AuthorityResolver's
    job, PKG-03). Proving this repository stays conservative: a binding
    whose target's membership has since been revoked is *still*
    returned by `list_current_bindings`, because its own `state`
    column is still ACTIVE. A caller must separately check membership
    -- this repository does not do it for them, and must not pretend
    to.
    """
    owner = _insert_user(db_connection, email="owner4@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member4@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    _insert_binding(
        db_connection, workspace_id=workspace_id, human_user_id=member, granted_by=owner
    )

    # Membership is revoked directly (simulating a future governance
    # Command's effect) without touching the HABB row at all -- there is
    # no cascade-write in this package (no CommitUnit exists to run one).
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(
            workspace_memberships_table.c.workspace_id == workspace_id.value,
            workspace_memberships_table.c.user_id == member.value,
        )
        .values(status=MembershipStatus.REVOKED.value, revoked_at=datetime.now(timezone.utc))
    )

    repository = SqlAlchemyAuthorityBindingRepository(db_connection)
    current = repository.list_current_bindings(workspace_id, member)

    assert len(current) == 1, (
        "this repository is documented to return the raw stored fact, not an "
        "effectiveness-resolved result -- if this assertion ever needs to become "
        "`== ()`, that is AuthorityResolver behavior creeping into PKG-02's scope"
    )
    assert current[0].state == AuthorityBindingState.ACTIVE


def test_owner_role_alone_yields_no_bindings(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: Owner assumed superuser.

    AC-04-001: "This closure does NOT mean: Workspace Owner = automatic
    executor of every operation." A membership with role=Owner and no
    explicit HumanAuthorityBinding must yield zero results here.
    """
    owner = _insert_user(db_connection, email="owner5@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=owner)
    _insert_role(
        db_connection,
        workspace_id=workspace_id,
        membership_id=membership_id,
        role=WorkspaceRole.OWNER,
        granted_by=owner,
    )

    repository = SqlAlchemyAuthorityBindingRepository(db_connection)

    assert repository.list_current_bindings(workspace_id, owner) == ()
