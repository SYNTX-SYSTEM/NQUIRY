"""T-AddMember END-TO-END TEST: `application.membership_operations_handler`
(F01 WU-01.5) -- the real, governed "Workspace governance root adds a
member" Command, against real PostgreSQL.

Every Workspace here is founded through the real
`application.workspace_creation_handler.create_workspace` Command
(F01 WU-01.4b); every authority check runs through the real
`authority.resolver.AuthorityResolver` and the real BND-001..005
evaluators (PKG-09), then the real `commit.coordinator.CommitCoordinator`
-- no mocks anywhere in the precommit or commit path.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.membership_operations_handler import (
    AddMemberDenied,
    OwnerRoleNotAssignable,
    add_member,
)
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.coordinator import CommitFailedPrecommit
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import role_assignments_table, users_table, workspace_memberships_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId, WorkspaceId
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 21, tzinfo=timezone.utc)


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Real Human",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return UserId(user_id)


def _human_actor(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


def _resolver(db_connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )


def _found_workspace(db_connection: sa.Connection, *, owner: UserId, name: str) -> WorkspaceId:
    result = create_workspace(
        db_connection,
        actor=_human_actor(owner),
        workspace_name=name,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
    )
    return result.workspace_id


def _add(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole = WorkspaceRole.CONTRIBUTOR,
):
    return add_member(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        new_member_user_id=new_member_user_id,
        role=role,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyWorkspaceVersionReader(
            db_connection, workspace_id=workspace_id
        ),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("role", [WorkspaceRole.FACILITATOR, WorkspaceRole.CONTRIBUTOR])
def test_owner_adds_a_real_registered_user_with_an_assignable_role(
    db_connection: sa.Connection, role: WorkspaceRole
) -> None:
    owner = _insert_user(db_connection, email=f"owner-{role.value}@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Team Workspace")
    new_member = _insert_user(db_connection, email=f"new-member-{role.value}@real-human.test")

    commit_unit = _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        new_member_user_id=new_member,
        role=role,
    )

    assert commit_unit.outcome.value == "COMMITTED"

    membership_row = (
        db_connection.execute(
            sa.select(workspace_memberships_table).where(
                workspace_memberships_table.c.workspace_id == workspace_id.value,
                workspace_memberships_table.c.user_id == new_member.value,
            )
        )
        .mappings()
        .one()
    )
    assert membership_row["status"] == MembershipStatus.ACTIVE.value

    role_row = (
        db_connection.execute(
            sa.select(role_assignments_table).where(
                role_assignments_table.c.membership_id == membership_row["id"]
            )
        )
        .mappings()
        .one()
    )
    assert role_row["role"] == role.value
    assert role_row["granted_by_user_id"] == owner.value


def test_new_members_workspace_becomes_accessible_to_them(db_connection: sa.Connection) -> None:
    from application.accessible_workspaces_query import list_accessible_workspaces

    owner = _insert_user(db_connection, email="owner-accessible@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Now Accessible")
    new_member = _insert_user(db_connection, email="new-member-accessible@real-human.test")

    _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        new_member_user_id=new_member,
    )

    accessible = list_accessible_workspaces(
        _human_actor(new_member),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
    )
    assert [w.id for w in accessible] == [workspace_id]


# ---------------------------------------------------------------------------
# Adversarial: role scope
# ---------------------------------------------------------------------------


def test_owner_role_is_refused_before_any_boundary_or_write(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-refuse-owner-role@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="No Co-Owners")
    new_member = _insert_user(db_connection, email="wants-co-owner@real-human.test")

    with pytest.raises(OwnerRoleNotAssignable):
        _add(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            new_member_user_id=new_member,
            role=WorkspaceRole.OWNER,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(workspace_memberships_table)
        .where(workspace_memberships_table.c.user_id == new_member.value)
    ).scalar_one()
    assert count == 0


# ---------------------------------------------------------------------------
# Adversarial: authority
# ---------------------------------------------------------------------------


def test_non_owner_member_cannot_add_another_member(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-for-contributor-attack@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Contributor Attack Target")
    contributor = _insert_user(db_connection, email="mere-contributor@real-human.test")
    _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        new_member_user_id=contributor,
        role=WorkspaceRole.CONTRIBUTOR,
    )
    outsider = _insert_user(db_connection, email="attempted-victim@real-human.test")

    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=_human_actor(contributor),
            workspace_id=workspace_id,
            new_member_user_id=outsider,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(workspace_memberships_table)
        .where(workspace_memberships_table.c.user_id == outsider.value)
    ).scalar_one()
    assert count == 0


def test_non_member_actor_cannot_add_to_a_workspace_they_do_not_belong_to(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-cross-workspace@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Not Yours")
    stranger = _insert_user(db_connection, email="stranger@real-human.test")
    target = _insert_user(db_connection, email="target-of-stranger@real-human.test")

    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=_human_actor(stranger),
            workspace_id=workspace_id,
            new_member_user_id=target,
        )


def test_non_existent_workspace_denies(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-nonexistent-ws@real-human.test")
    target = _insert_user(db_connection, email="target-nonexistent-ws@real-human.test")

    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=WorkspaceId(uuid.uuid4()),
            new_member_user_id=target,
        )


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(db_connection, email=f"owner-non-human-{actor_class.value}@real.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Attack")
    target = _insert_user(db_connection, email=f"target-non-human-{actor_class.value}@real.test")

    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=ActorIdentity(actor_class=actor_class, user_id=owner),
            workspace_id=workspace_id,
            new_member_user_id=target,
        )


# ---------------------------------------------------------------------------
# Adversarial: real database constraints surfaced as CommitFailedPrecommit
# ---------------------------------------------------------------------------


def test_adding_an_already_active_member_fails_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-duplicate-member@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Duplicate Member Target")
    member = _insert_user(db_connection, email="already-member@real-human.test")
    _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        new_member_user_id=member,
    )

    with pytest.raises(CommitFailedPrecommit):
        _add(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            new_member_user_id=member,
        )


def test_adding_a_non_existent_user_fails_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-nonexistent-user@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Nonexistent User Target")

    with pytest.raises(CommitFailedPrecommit):
        _add(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            new_member_user_id=UserId(uuid.uuid4()),
        )
