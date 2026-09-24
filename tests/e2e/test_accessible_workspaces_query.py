"""T-ListAccessibleWorkspaces END-TO-END TEST:
`application.accessible_workspaces_query` (F01 WU-01.2) -- the
read-only "which Workspaces can I see" Query, against real PostgreSQL.

Every Workspace here is created through the real
`application.workspace_creation_handler.create_workspace` Command
(F01 WU-01.4b), never `NonProofWorkspaceBootstrap` -- this Query's own
job is reading real membership facts, so its tests build real
memberships to read.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from application.accessible_workspaces_query import (
    AccessibleWorkspacesDenied,
    list_accessible_workspaces,
)
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from governance.membership import MembershipStatus
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import users_table, workspace_memberships_table
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId

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


def _make_workspace(
    db_connection: sa.Connection, *, owner: UserId, name: str, occurred_at: datetime = _NOW
) -> uuid.UUID:
    result = create_workspace(
        db_connection,
        actor=_human_actor(owner),
        workspace_name=name,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=occurred_at,
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
    return result.workspace_id.value


def _list_for(db_connection: sa.Connection, actor: ActorIdentity) -> tuple:
    return list_accessible_workspaces(
        actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
    )


class _RaisingMembershipRepository:
    def list_active_memberships_for_user(self, user_id: object) -> tuple:
        raise AssertionError("must never be queried when BND-001 denies")


def test_founder_sees_the_workspace_they_created(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="sees-own@real-human.test")
    workspace_id = _make_workspace(db_connection, owner=founder, name="Founder Workspace")

    accessible = _list_for(db_connection, _human_actor(founder))

    assert [w.id.value for w in accessible] == [workspace_id]


def test_founder_with_two_workspaces_sees_both_oldest_first(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="sees-two@real-human.test")
    # F02 WU-02.11: distinct creation times. With identical timestamps
    # "oldest first" is undefined, and the assertion was an intermittent flake.
    first_id = _make_workspace(db_connection, owner=founder, name="First Workspace")
    second_id = _make_workspace(
        db_connection,
        owner=founder,
        name="Second Workspace",
        occurred_at=_NOW + timedelta(minutes=1),
    )

    accessible = _list_for(db_connection, _human_actor(founder))

    assert [w.id.value for w in accessible] == [first_id, second_id]


def test_human_with_no_memberships_sees_an_empty_list_not_a_denial(
    db_connection: sa.Connection,
) -> None:
    lonely = _insert_user(db_connection, email="no-workspaces@real-human.test")

    accessible = _list_for(db_connection, _human_actor(lonely))

    assert accessible == ()


def test_cross_user_isolation_one_founder_never_sees_anothers_workspace(
    db_connection: sa.Connection,
) -> None:
    founder_a = _insert_user(db_connection, email="isolation-a@real-human.test")
    founder_b = _insert_user(db_connection, email="isolation-b@real-human.test")
    _make_workspace(db_connection, owner=founder_a, name="A's Workspace")
    workspace_b_id = _make_workspace(db_connection, owner=founder_b, name="B's Workspace")

    accessible_to_b = _list_for(db_connection, _human_actor(founder_b))

    assert [w.id.value for w in accessible_to_b] == [workspace_b_id]


def test_revoked_membership_is_excluded(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="revoked-excluded@real-human.test")
    workspace_id = _make_workspace(db_connection, owner=founder, name="Soon Revoked")

    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.workspace_id == workspace_id)
        .values(status=MembershipStatus.REVOKED.value, revoked_at=_NOW)
    )

    accessible = _list_for(db_connection, _human_actor(founder))

    assert accessible == ()


@pytest.mark.parametrize(
    "actor_class",
    [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM],
)
def test_non_human_actor_is_denied_and_repository_is_never_queried(
    db_connection: sa.Connection, actor_class: ActorClass
) -> None:
    non_human_id = _insert_user(db_connection, email=f"non-human-{actor_class.value}@real.test")

    with pytest.raises(AccessibleWorkspacesDenied) as exc_info:
        list_accessible_workspaces(
            ActorIdentity(actor_class=actor_class, user_id=non_human_id),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_NOW,
            membership_repository=_RaisingMembershipRepository(),  # type: ignore[arg-type]
            workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        )

    assert exc_info.value.reason_code.startswith("IDENTITY_CLASS_NOT_ACCEPTED")
