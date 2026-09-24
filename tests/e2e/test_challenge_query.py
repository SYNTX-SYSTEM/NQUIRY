"""T-GetChallenge END-TO-END TEST: `application.challenge_query.get_challenge`
(F02 WU-02.1, the "read" half), against real PostgreSQL, no mocks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.challenge_creation_handler import create_challenge
from application.challenge_query import (
    ChallengeViewData,
    ChallengeViewDenied,
    ChallengeViewNotFound,
    get_challenge,
)
from application.membership_operations_handler import add_member
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.challenge_repository import SqlAlchemyChallengeRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import users_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


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


def _add_member(
    db_connection: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole = WorkspaceRole.FACILITATOR,
) -> None:
    add_member(
        db_connection,
        actor=_human_actor(owner),
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


def _real_challenge(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, facilitator: UserId
) -> ChallengeId:
    result = create_challenge(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        title="Signup conversion dropped 18%",
        description=None,
        context=None,
        desired_outcome=None,
        constraints=None,
        stakeholders=None,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
    )
    return result.challenge_id


def _get(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
):
    return get_challenge(
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        correlation_id=CorrelationId(uuid.uuid4()),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_any_real_member_reads_a_real_challenge(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-get-challenge@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Get Challenge Happy")
    facilitator = _insert_user(db_connection, email="facilitator-get-challenge@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _real_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )

    # The OWNER (not the Facilitator who created it) reads it -- proves
    # this Query's own read-side scope is "any real member", not
    # "Facilitator only" (unlike creation itself).
    result = _get(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
    )

    assert isinstance(result, ChallengeViewData)
    assert result.challenge.challenge_id == challenge_id
    assert result.challenge.title == "Signup conversion dropped 18%"


# ---------------------------------------------------------------------------
# Adversarial
# ---------------------------------------------------------------------------


def test_non_existent_challenge_is_not_found_not_denied(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-get-nonexistent@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Get Nonexistent")

    result = _get(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        challenge_id=ChallengeId(uuid.uuid4()),
    )

    assert isinstance(result, ChallengeViewNotFound)


def test_cross_workspace_stranger_is_denied(db_connection: sa.Connection) -> None:
    owner_a = _insert_user(db_connection, email="owner-a-get-cross@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=owner_a, name="Workspace A Get Cross")
    facilitator_a = _insert_user(db_connection, email="facilitator-a-get-cross@real-human.test")
    _add_member(
        db_connection, owner=owner_a, workspace_id=workspace_a, new_member_user_id=facilitator_a
    )
    challenge_id = _real_challenge(
        db_connection, workspace_id=workspace_a, facilitator=facilitator_a
    )

    stranger = _insert_user(db_connection, email="stranger-get-cross@real-human.test")

    result = _get(
        db_connection,
        actor=_human_actor(stranger),
        workspace_id=workspace_a,
        challenge_id=challenge_id,
    )

    assert isinstance(result, ChallengeViewDenied)


def test_forged_workspace_in_request_is_ignored_the_real_challenge_workspace_governs(
    db_connection: sa.Connection,
) -> None:
    """Mandatory attack (mirrors `session-view.spec.ts`'s own "forged
    Workspace in client" case): the caller's own claimed `workspace_id`
    is never authoritative by itself (06 §8 BND-002 non-collapse) --
    only the Challenge's REAL, stored `workspace_id` (read fresh from
    `challenge_repository.get`) is ever used to resolve BND-002."""
    owner_a = _insert_user(db_connection, email="owner-a-forged-ws@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=owner_a, name="Workspace A Forged")
    facilitator_a = _insert_user(db_connection, email="facilitator-a-forged-ws@real-human.test")
    _add_member(
        db_connection, owner=owner_a, workspace_id=workspace_a, new_member_user_id=facilitator_a
    )
    challenge_id = _real_challenge(
        db_connection, workspace_id=workspace_a, facilitator=facilitator_a
    )

    owner_b = _insert_user(db_connection, email="owner-b-forged-ws@real-human.test")
    workspace_b = _found_workspace(db_connection, owner=owner_b, name="Workspace B Forged")

    # facilitator_a claims workspace_b (a real Workspace, just not the
    # Challenge's own real one, and not one they belong to either) --
    # must still be denied, not accidentally granted via the forged
    # workspace_id.
    result = _get(
        db_connection,
        actor=_human_actor(facilitator_a),
        workspace_id=workspace_b,
        challenge_id=challenge_id,
    )

    assert isinstance(result, ChallengeViewDenied)


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(db_connection, email=f"owner-get-non-human-{actor_class.value}@real.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Get Attack")
    facilitator = _insert_user(
        db_connection, email=f"facilitator-get-non-human-{actor_class.value}@real.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _real_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )

    result = _get(
        db_connection,
        actor=ActorIdentity(actor_class=actor_class, user_id=owner),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
    )

    assert isinstance(result, ChallengeViewDenied)
