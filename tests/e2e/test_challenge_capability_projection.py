"""T-ChallengeCapabilityProjection END-TO-END TEST:
`application.challenge_capability_projection` (F02 WU-02.2, "Challenge
semantic projection") -- against real PostgreSQL, no mocks.

Every Workspace here is founded through the real `create_workspace`
(F01 WU-01.4b); every membership through the real `add_member` (F01
WU-01.5); every Challenge through the real `create_challenge` (F02
WU-02.1); every `SESSION_CONTROL_RIGHT` binding through the real
`grant_human_authority_binding` (F02 WU-02.0) -- no raw table inserts
anywhere in this file. Written FIRST, before
`application.challenge_capability_projection` exists -- this file is
expected to fail on import until it is implemented (TDD RED).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.authority_binding_handler import (
    grant_human_authority_binding,
    revoke_human_authority_binding,
)
from application.challenge_capability_projection import (
    ChallengeCapabilityProjection,
    ChallengeOutsideWorkspaceContext,
    project_challenge_capabilities,
)
from application.challenge_creation_handler import create_challenge
from application.membership_operations_handler import add_member
from application.workspace_context import WorkspaceContext, resolve_workspace_context
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
from persistence.authority_binding_repository import (
    SqlAlchemyAuthorityBindingRepository,
    SqlAlchemyAuthorityBindingVersionReader,
)
from persistence.challenge_repository import SqlAlchemyChallengeRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import human_authority_bindings_table, users_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import (
    AttemptId,
    AuthorityBindingId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def _principal(user_id: UserId) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        authentication_session_ref="session-1",
        authentication_time=_NOW,
        issuer_ref="https://issuer.example.test",
    )


def _human_actor(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


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
    authority_class: AuthorityClass,
    scope_type: str,
    scope_id: uuid.UUID,
):
    return grant_human_authority_binding(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=human_user_id,
        authority_class=authority_class,
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


def _revoke(db_connection: sa.Connection, *, owner: UserId, workspace_id: WorkspaceId, binding_id):
    revoke_human_authority_binding(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        binding_id=binding_id,
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
        current_version_reader=SqlAlchemyAuthorityBindingVersionReader(db_connection),
    )


def _context(
    db_connection: sa.Connection, *, user_id: UserId, workspace_id: WorkspaceId
) -> WorkspaceContext:
    return resolve_workspace_context(
        _principal(user_id),
        workspace_id,
        SqlAlchemyWorkspaceRepository(db_connection),
        SqlAlchemyMembershipRepository(db_connection),
    )


def _project(
    db_connection: sa.Connection, *, context: WorkspaceContext, challenge_id: ChallengeId
) -> ChallengeCapabilityProjection:
    challenge = SqlAlchemyChallengeRepository(db_connection).get(challenge_id)
    assert challenge is not None
    return project_challenge_capabilities(
        context, challenge, authority_resolver=_resolver(db_connection)
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_a_real_challenge_scoped_binding_grants_can_create_session(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-proj-happy@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Projection Happy")
    facilitator = _insert_user(db_connection, email="facilitator-proj-happy@real-human.test")
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
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )

    context = _context(db_connection, user_id=facilitator, workspace_id=workspace_id)
    projection = _project(db_connection, context=context, challenge_id=challenge_id)

    assert projection.challenge_id == challenge_id
    assert projection.can_create_session is True


# ---------------------------------------------------------------------------
# Adversarial
# ---------------------------------------------------------------------------


def test_no_binding_at_all_cannot_create_session(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-proj-none@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Projection No Binding")
    facilitator = _insert_user(db_connection, email="facilitator-proj-none@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=facilitator
    )
    challenge_id = _create_challenge(
        db_connection, workspace_id=workspace_id, facilitator=facilitator
    )

    context = _context(db_connection, user_id=facilitator, workspace_id=workspace_id)
    projection = _project(db_connection, context=context, challenge_id=challenge_id)

    assert projection.can_create_session is False


def test_a_binding_scoped_to_a_different_challenge_does_not_grant_capability_here(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-proj-wrong-challenge@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Projection Wrong Challenge")
    facilitator = _insert_user(
        db_connection, email="facilitator-proj-wrong-challenge@real-human.test"
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
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="CHALLENGE",
        scope_id=other_challenge_id.value,
    )

    context = _context(db_connection, user_id=facilitator, workspace_id=workspace_id)
    projection = _project(db_connection, context=context, challenge_id=challenge_id)

    assert projection.can_create_session is False


def test_a_workspace_scoped_binding_does_not_grant_challenge_scoped_capability(
    db_connection: sa.Connection,
) -> None:
    """AUTH-DEP-SESS-001's own SCOPE is "Target Challenge within one
    Workspace" -- a `SESSION_CONTROL_RIGHT` binding scoped to the
    Workspace at large (the shape `burst_operations.py`'s own AUTH-DEP-
    BURST-001 legitimately uses for a DIFFERENT Command) must not be
    mistaken for a Challenge-scoped one here (06 §11 BND-005: exact
    scope match, never a broader-scope fallback)."""
    owner = _insert_user(db_connection, email="owner-proj-workspace-scope@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Projection Workspace Scope")
    facilitator = _insert_user(
        db_connection, email="facilitator-proj-workspace-scope@real-human.test"
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
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=workspace_id.value,
    )

    context = _context(db_connection, user_id=facilitator, workspace_id=workspace_id)
    projection = _project(db_connection, context=context, challenge_id=challenge_id)

    assert projection.can_create_session is False


def test_a_challenge_from_a_different_workspace_raises(db_connection: sa.Connection) -> None:
    owner_a = _insert_user(db_connection, email="owner-a-proj-forged@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=owner_a, name="Workspace A Proj Forged")
    facilitator_a = _insert_user(db_connection, email="facilitator-a-proj-forged@real-human.test")
    _add_member(
        db_connection, owner=owner_a, workspace_id=workspace_a, new_member_user_id=facilitator_a
    )
    challenge_a = _create_challenge(
        db_connection, workspace_id=workspace_a, facilitator=facilitator_a
    )

    owner_b = _insert_user(db_connection, email="owner-b-proj-forged@real-human.test")
    workspace_b = _found_workspace(db_connection, owner=owner_b, name="Workspace B Proj Forged")

    context_b = _context(db_connection, user_id=owner_b, workspace_id=workspace_b)

    with pytest.raises(ChallengeOutsideWorkspaceContext):
        _project(db_connection, context=context_b, challenge_id=challenge_a)


# ---------------------------------------------------------------------------
# Cross-Work-Unit proof: revoking the binding (WU-01.6/WU-02.0) flips the
# projection
# ---------------------------------------------------------------------------


def test_revoking_the_binding_flips_can_create_session_back_to_false(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-proj-revoke@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Projection Revoke")
    facilitator = _insert_user(db_connection, email="facilitator-proj-revoke@real-human.test")
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
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    binding_row = db_connection.execute(
        sa.select(human_authority_bindings_table.c.id).where(
            human_authority_bindings_table.c.human_user_id == facilitator.value,
            human_authority_bindings_table.c.authority_class
            == AuthorityClass.SESSION_CONTROL_RIGHT.value,
            human_authority_bindings_table.c.scope_type == "CHALLENGE",
            human_authority_bindings_table.c.scope_id == challenge_id.value,
        )
    ).one()
    binding_id = AuthorityBindingId(binding_row[0])

    context = _context(db_connection, user_id=facilitator, workspace_id=workspace_id)
    before = _project(db_connection, context=context, challenge_id=challenge_id)
    assert before.can_create_session is True

    _revoke(db_connection, owner=owner, workspace_id=workspace_id, binding_id=binding_id)

    after = _project(db_connection, context=context, challenge_id=challenge_id)
    assert after.can_create_session is False
