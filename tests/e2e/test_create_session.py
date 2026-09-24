"""T-CreateSession END-TO-END TEST:
`application.session_creation_handler.create_session` (F02 WU-02.3,
"Session create/read" -- the "create" half; `GetSession`/
`application.session_view_query.get_session_view`, Architecture 17,
already exists and already passes its own suite) -- against real
PostgreSQL, no mocks.

`AUTH-DEP-SESS-001` (04 §22): Session creation is gated on a real,
currently-effective `SESSION_CONTROL_RIGHT` `HumanAuthorityBinding`
scoped to the target Challenge -- "AUTHORITY SCOPE: Target Challenge
within one Workspace." Every Workspace here is founded through the
real `create_workspace` (F01 WU-01.4b); every membership through the
real `add_member` (F01 WU-01.5); every Challenge through the real
`create_challenge` (F02 WU-02.1); every `SESSION_CONTROL_RIGHT`
binding through the real `grant_human_authority_binding` (F02
WU-02.0) -- no raw table inserts anywhere in this file.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.authority_binding_handler import grant_human_authority_binding
from application.challenge_creation_handler import create_challenge
from application.membership_operations_handler import add_member
from application.session_creation_handler import CreateSessionDenied, create_session
from application.session_view_query import SessionViewData, get_session_view
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.burst_repository import SqlAlchemyBurstRepository
from persistence.challenge_repository import (
    SqlAlchemyChallengeRepository,
    SqlAlchemyChallengeVersionReader,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.decision_repository import SqlAlchemyDecisionRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.session_repository import SqlAlchemySessionRepository
from persistence.tables import sessions_table, users_table
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
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import MethodVersion
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)
_METHOD_KEY = "STANDARD_INQUIRY"
_METHOD_VERSION = MethodVersion("1.0")


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


def _create_challenge(
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


def _grant(
    db_connection: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    scope_type: str,
    scope_id: uuid.UUID,
) -> None:
    grant_human_authority_binding(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=human_user_id,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type=scope_type,
        scope_id=scope_id,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
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


def _create_session(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    session_id: SessionId | None = None,
):
    return create_session(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        session_id=session_id if session_id is not None else SessionId(uuid.uuid4()),
        applied_method_key=_METHOD_KEY,
        applied_method_version=_METHOD_VERSION,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        session_repository=SqlAlchemySessionRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyChallengeVersionReader(
            db_connection, challenge_id=challenge_id
        ),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_the_binding_holder_creates_a_real_session(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-session@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Create Session Happy")
    facilitator = _insert_user(db_connection, email="facilitator-create-session@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    session_id = SessionId(uuid.uuid4())

    commit_unit = _create_session(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        session_id=session_id,
    )

    assert commit_unit.outcome.value == "COMMITTED"
    row = (
        db_connection.execute(
            sa.select(sessions_table).where(sessions_table.c.id == session_id.value)
        )
        .mappings()
        .one()
    )
    assert row["challenge_id"] == challenge_id.value
    assert row["workspace_id"] == workspace_id.value
    assert row["state"] == "DRAFT"
    assert row["applied_method_key"] == _METHOD_KEY
    assert row["applied_method_version"] == _METHOD_VERSION.value
    assert row["closed_at"] is None
    assert row["record_version"] == 1


def test_a_second_session_under_the_same_challenge_is_a_legitimate_new_inquiry_cycle(
    db_connection: sa.Connection,
) -> None:
    """`domain.session.py`'s own docstring: "A new inquiry cycle creates
    a new Session under the same Challenge." -- no uniqueness
    constraint on (challenge_id) is expected."""
    owner = _insert_user(db_connection, email="owner-create-session-two@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Second Inquiry Cycle")
    facilitator = _insert_user(
        db_connection, email="facilitator-create-session-two@real-human.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )

    _create_session(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
    )
    _create_session(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
    )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(sessions_table)
        .where(sessions_table.c.challenge_id == challenge_id.value)
    ).scalar_one()
    assert count == 2


# ---------------------------------------------------------------------------
# Adversarial
# ---------------------------------------------------------------------------


def test_no_binding_at_all_is_denied(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-session-none@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="No Binding Create Session")
    facilitator = _insert_user(
        db_connection, email="facilitator-create-session-none@real-human.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=_human_actor(facilitator),
            workspace_id=workspace_id,
            challenge_id=challenge_id,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(sessions_table)
        .where(sessions_table.c.challenge_id == challenge_id.value)
    ).scalar_one()
    assert count == 0


def test_a_binding_scoped_to_a_different_challenge_is_denied(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-session-wrong-challenge@real.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Wrong Challenge Scope")
    facilitator = _insert_user(
        db_connection, email="facilitator-create-session-wrong-challenge@real.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    other_challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="CHALLENGE",
        scope_id=other_challenge_id.value,
    )

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=_human_actor(facilitator),
            workspace_id=workspace_id,
            challenge_id=challenge_id,
        )


def test_a_workspace_scoped_binding_is_denied(db_connection: sa.Connection) -> None:
    """AUTH-DEP-SESS-001's own SCOPE is "Target Challenge within one
    Workspace" -- a binding scoped to the Workspace at large is not a
    substitute (exact scope match, 06 §11 BND-005)."""
    owner = _insert_user(db_connection, email="owner-create-session-ws-scope@real.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Workspace Scope Denied")
    facilitator = _insert_user(db_connection, email="facilitator-create-session-ws-scope@real.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="WORKSPACE",
        scope_id=workspace_id.value,
    )

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=_human_actor(facilitator),
            workspace_id=workspace_id,
            challenge_id=challenge_id,
        )


def test_non_existent_challenge_is_denied(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-create-session-nonexistent@real.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Nonexistent Challenge")

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            challenge_id=ChallengeId(uuid.uuid4()),
        )


def test_workspace_mismatch_is_denied(db_connection: sa.Connection) -> None:
    """AUTH-DEP-SESS-001's own DENY CONDITION: "Workspace mismatch." A
    caller claiming a real, different Workspace than the Challenge's
    own real Workspace must be denied, not silently resolved against
    whichever Workspace the Challenge actually belongs to."""
    owner_a = _insert_user(db_connection, email="owner-a-create-session-mismatch@real.test")
    workspace_a = _found_workspace(
        db_connection, owner=owner_a, name="Workspace A Session Mismatch"
    )
    facilitator_a = _insert_user(
        db_connection, email="facilitator-a-create-session-mismatch@real.test"
    )
    _add_member(
        db_connection, owner=owner_a, workspace_id=workspace_a, new_member_user_id=facilitator_a
    )
    challenge_a = _create_challenge(
        db_connection, workspace_id=workspace_a, facilitator=facilitator_a
    )
    _grant(
        db_connection,
        owner=owner_a,
        workspace_id=workspace_a,
        human_user_id=facilitator_a,
        scope_type="CHALLENGE",
        scope_id=challenge_a.value,
    )

    owner_b = _insert_user(db_connection, email="owner-b-create-session-mismatch@real.test")
    workspace_b = _found_workspace(
        db_connection, owner=owner_b, name="Workspace B Session Mismatch"
    )

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=_human_actor(facilitator_a),
            workspace_id=workspace_b,
            challenge_id=challenge_a,
        )


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(
        db_connection, email=f"owner-create-session-non-human-{actor_class.value}@real.test"
    )
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Create Session")
    facilitator = _insert_user(
        db_connection, email=f"facilitator-create-session-non-human-{actor_class.value}@real.test"
    )
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )

    with pytest.raises(CreateSessionDenied):
        _create_session(
            db_connection,
            actor=ActorIdentity(actor_class=actor_class, user_id=facilitator),
            workspace_id=workspace_id,
            challenge_id=challenge_id,
        )


# ---------------------------------------------------------------------------
# Cross-Work-Unit proof: a created Session is real through the "read" half
# too -- `get_session_view` (Architecture 17, already committed) -- proving
# this Work Unit's own combined "Session create/read" mission end-to-end.
# ---------------------------------------------------------------------------


def test_a_created_session_is_readable_through_get_session_view(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-create-then-read@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Create Then Read")
    facilitator = _insert_user(db_connection, email="facilitator-create-then-read@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )
    _grant(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        human_user_id=facilitator,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    session_id = SessionId(uuid.uuid4())
    _create_session(
        db_connection,
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        session_id=session_id,
    )

    result = get_session_view(
        actor=_human_actor(facilitator),
        workspace_id=workspace_id,
        session_id=session_id,
        correlation_id=CorrelationId(uuid.uuid4()),
        session_repository=SqlAlchemySessionRepository(db_connection),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        burst_repository=SqlAlchemyBurstRepository(db_connection),
        question_repository=SqlAlchemyQuestionRepository(db_connection),
        decision_repository=SqlAlchemyDecisionRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
    )

    assert isinstance(result, SessionViewData)
    assert result.session.session_id == session_id
    assert result.session.state.value == "DRAFT"
    assert result.challenge.challenge_id == challenge_id
    assert result.burst is None
    assert result.decision is None
