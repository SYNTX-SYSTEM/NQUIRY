"""T-CreateChallenge END-TO-END TEST: `application.challenge_creation_handler.create_challenge`
(F02 WU-02.1), against real PostgreSQL, no mocks.

`AUTH-DEP-CH-001` (04 §21): Challenge creation is gated on **role
alone** ("Facilitator role valid in target Workspace") -- no
`HumanAuthorityBinding`/BND-005 check, deliberately (04 §84: "CLOSED.
Facilitator has source authority." -- human-confirmed, 2026-09-22, to
build exactly as specified rather than inventing an Owner exception
"No implicit Owner/Facilitator substitution" repeatedly forbids). This
is the first governance-shaped Command in this codebase whose
precommit chain is BND-001/002/003/004 WITHOUT BND-005 -- every prior
one (`AddMember`, `RevokeHumanAuthorityBinding`,
`GrantHumanAuthorityBinding`) required both together.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.challenge_creation_handler import (
    ChallengeCreationDenied,
    create_challenge,
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
from persistence.tables import challenges_table, users_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import (
    AttemptId,
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


def _create(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    title: str = "Signup conversion dropped 18%",
    description: str | None = None,
    command_id: CommandId | None = None,
    idempotency_key: str | None = None,
):
    return create_challenge(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        title=title,
        description=description,
        context=None,
        desired_outcome=None,
        constraints=None,
        stakeholders=None,
        command_id=command_id if command_id is not None else CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=idempotency_key,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_facilitator_creates_a_real_challenge(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-challenge@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Create Challenge Happy")
    facilitator = _insert_user(db_connection, email="facilitator-create-challenge@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )

    result = _create(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        title="Signup conversion dropped 18% after the redesign",
        description="Users abandon the new flow at the payment step.",
    )

    assert result.workspace_id == workspace_id
    row = (
        db_connection.execute(
            sa.select(challenges_table).where(challenges_table.c.workspace_id == workspace_id.value)
        )
        .mappings()
        .one()
    )
    assert row["id"] == result.challenge_id.value
    assert row["title"] == "Signup conversion dropped 18% after the redesign"
    assert row["description"] == "Users abandon the new flow at the payment step."
    assert row["record_version"] == 1


# ---------------------------------------------------------------------------
# Adversarial: the founder-cannot-create-in-their-own-Workspace property
# (human-confirmed intentional, AUTH-DEP-CH-001/04 §84)
# ---------------------------------------------------------------------------


def test_the_workspace_owner_alone_cannot_create_a_challenge(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-cannot-create-challenge@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Owner Alone")

    with pytest.raises(ChallengeCreationDenied):
        _create(db_connection, actor=_human_actor(owner), workspace_id=workspace_id)

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(challenges_table)
        .where(challenges_table.c.workspace_id == workspace_id.value)
    ).scalar_one()
    assert count == 0


def test_a_contributor_cannot_create_a_challenge(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-contributor-cant-create@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Contributor Cannot Create")
    contributor = _insert_user(db_connection, email="contributor-cant-create@real-human.test")
    _add_member(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        new_member_user_id=contributor,
        role=WorkspaceRole.CONTRIBUTOR,
    )

    with pytest.raises(ChallengeCreationDenied):
        _create(db_connection, actor=_human_actor(contributor), workspace_id=workspace_id)


def test_non_member_actor_cannot_create(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-stranger-create@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Stranger Create Attack")
    stranger = _insert_user(db_connection, email="stranger-create-challenge@real-human.test")

    with pytest.raises(ChallengeCreationDenied):
        _create(db_connection, actor=_human_actor(stranger), workspace_id=workspace_id)


def test_non_existent_workspace_denies(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-nonexistent-ws@real-human.test")

    with pytest.raises(ChallengeCreationDenied):
        _create(db_connection, actor=_human_actor(owner), workspace_id=WorkspaceId(uuid.uuid4()))


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(
        db_connection, email=f"owner-create-non-human-{actor_class.value}@real.test"
    )
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Create Attack")
    facilitator = _insert_user(
        db_connection, email=f"facilitator-non-human-{actor_class.value}@real.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )

    with pytest.raises(ChallengeCreationDenied):
        _create(
            db_connection,
            actor=ActorIdentity(actor_class=actor_class, user_id=facilitator),
            workspace_id=workspace_id,
        )


def test_empty_title_is_rejected_before_any_boundary_or_write(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-empty-title@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Empty Title Target")
    facilitator = _insert_user(db_connection, email="facilitator-empty-title@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )

    with pytest.raises(ValueError):
        _create(
            db_connection, actor=_human_actor(facilitator), workspace_id=workspace_id, title="   "
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(challenges_table)
        .where(challenges_table.c.workspace_id == workspace_id.value)
    ).scalar_one()
    assert count == 0


def test_cross_workspace_facilitator_cannot_create_in_a_workspace_they_do_not_belong_to(
    db_connection: sa.Connection,
) -> None:
    owner_a = _insert_user(db_connection, email="owner-a-cross-create@real-human.test")
    _found_workspace(db_connection, owner=owner_a, name="Workspace A Cross Create")
    owner_b = _insert_user(db_connection, email="owner-b-cross-create@real-human.test")
    workspace_b = _found_workspace(db_connection, owner=owner_b, name="Workspace B Cross Create")
    facilitator_a = _insert_user(db_connection, email="facilitator-a-cross-create@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=owner_a, name="Workspace A2 Cross Create")
    _add_member(
        db_connection, owner=owner_a, workspace_id=workspace_a, new_member_user_id=facilitator_a
    )

    with pytest.raises(ChallengeCreationDenied):
        _create(db_connection, actor=_human_actor(facilitator_a), workspace_id=workspace_b)


# ---------------------------------------------------------------------------
# Idempotent retry (F02 WU-02.1 follow-up: "return the existing Challenge,
# do not create a second one" -- human-requested, 2026-09-22)
# ---------------------------------------------------------------------------


def test_a_retried_call_with_the_same_idempotency_key_returns_the_same_challenge(
    db_connection: sa.Connection,
) -> None:
    """14 section 27: "same identity COMMITTED -> return prior committed
    result." A genuine retry reuses BOTH the same `command_id` (09
    section 4.3: a different `command_id` is a different logical
    operation, never a retry of this one) AND the same
    `idempotency_key` -- exactly what an HTTP client resubmitting an
    identical request after a lost response would send, with a fresh
    `attempt_id` per physical send (this Command's own
    `command_repository.record_attempt` already treats a repeated
    `command_id` with an unchanged payload fingerprint as "record a
    new attempt row only", never a second `commands` row)."""
    owner = _insert_user(db_connection, email="owner-idempotent-create@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Idempotent Create")
    facilitator = _insert_user(db_connection, email="facilitator-idempotent-create@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )

    shared_command_id = CommandId(uuid.uuid4())
    shared_idempotency_key = "retry-key-signup-conversion-challenge"

    first = _create(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        title="Signup conversion dropped 18% after the redesign",
        description="Users abandon the new flow at the payment step.",
        command_id=shared_command_id,
        idempotency_key=shared_idempotency_key,
    )
    second = _create(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        title="Signup conversion dropped 18% after the redesign",
        description="Users abandon the new flow at the payment step.",
        command_id=shared_command_id,
        idempotency_key=shared_idempotency_key,
    )

    assert second.challenge_id == first.challenge_id
    assert second.workspace_id == first.workspace_id

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(challenges_table)
        .where(challenges_table.c.workspace_id == workspace_id.value)
    ).scalar_one()
    assert count == 1
