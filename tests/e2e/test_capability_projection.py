"""T-CapabilityProjection END-TO-END TEST:
`application.capability_projection` (F01 WU-01.7) -- "authenticate ->
... -> see actual available capabilities", 19 §21's own HUMAN PRODUCT
EFFECT closure, against real PostgreSQL.

Every Workspace here is founded through the real
`application.workspace_creation_handler.create_workspace` Command (F01
WU-01.4b); every membership through the real
`application.membership_operations_handler.add_member` Command (F01
WU-01.5); every non-governance-right binding revoked through the real
`application.authority_binding_handler.revoke_human_authority_binding`
Command (F01 WU-01.6) -- no mocks anywhere. Written FIRST, before
`application.capability_projection` exists -- this file is expected to
fail on import until it is implemented (TDD RED).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from application.authority_binding_handler import revoke_human_authority_binding
from application.capability_projection import CapabilityProjection, project_capabilities
from application.membership_operations_handler import add_member
from application.workspace_context import resolve_workspace_context
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
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 21, tzinfo=timezone.utc)


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
    role: WorkspaceRole = WorkspaceRole.CONTRIBUTOR,
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


def _grant_directly(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    granted_by_user_id: UserId,
    authority_class: AuthorityClass,
) -> AuthorityBindingId:
    """No real Command grants a non-`WORKSPACE_GOVERNANCE_RIGHT` binding
    yet (F01 WU-01.6's own disclosed scope boundary) -- same direct-
    insert convention that Work Unit's own test file already
    established, never a direct insert into `workspace_memberships`
    (the real `AddMember` Command is used for that first)."""
    binding_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=human_user_id.value,
            authority_class=authority_class.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=granted_by_user_id.value,
            granted_at=_NOW,
            revoked_by_user_id=None,
            revoked_at=None,
            state="ACTIVE",
            record_version=1,
        )
    )
    return AuthorityBindingId(binding_id)


def _revoke(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    binding_id: AuthorityBindingId,
) -> None:
    revoke_human_authority_binding(
        db_connection,
        actor=actor,
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


def _project(
    db_connection: sa.Connection, *, user_id: UserId, workspace_id: WorkspaceId
) -> CapabilityProjection:
    context = resolve_workspace_context(
        _principal(user_id),
        workspace_id,
        SqlAlchemyWorkspaceRepository(db_connection),
        SqlAlchemyMembershipRepository(db_connection),
    )
    return project_capabilities(
        context,
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_the_founder_is_governance_capable_and_authorized(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-capability-founder@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Founder Capability")

    projection = _project(db_connection, user_id=owner, workspace_id=workspace_id)

    assert projection.role is WorkspaceRole.OWNER
    assert projection.governance_capable is True
    assert projection.authorized is True
    assert projection.held_authority_classes == frozenset(
        {AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT}
    )


def test_a_plain_member_with_no_bindings_is_neither_authorized_nor_governance_capable(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-capability-plain@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Plain Member Capability")
    member = _insert_user(db_connection, email="member-capability-plain@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=member)

    projection = _project(db_connection, user_id=member, workspace_id=workspace_id)

    assert projection.role is WorkspaceRole.CONTRIBUTOR
    assert projection.governance_capable is False
    assert projection.authorized is False
    assert projection.held_authority_classes == frozenset()


def test_a_member_holding_a_non_governance_binding_is_authorized_but_not_governance_capable(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-capability-decision@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Decision Right Capability")
    member = _insert_user(db_connection, email="member-capability-decision@real-human.test")
    _add_member(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        new_member_user_id=member,
        role=WorkspaceRole.FACILITATOR,
    )
    _grant_directly(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by_user_id=owner,
        authority_class=AuthorityClass.DECISION_RIGHT,
    )

    projection = _project(db_connection, user_id=member, workspace_id=workspace_id)

    assert projection.role is WorkspaceRole.FACILITATOR
    assert projection.governance_capable is False
    assert projection.authorized is True
    assert projection.held_authority_classes == frozenset({AuthorityClass.DECISION_RIGHT})


def test_multiple_held_authority_classes_are_all_projected(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-capability-multi@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Multi Binding Capability")
    member = _insert_user(db_connection, email="member-capability-multi@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=member)
    _grant_directly(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by_user_id=owner,
        authority_class=AuthorityClass.DECISION_RIGHT,
    )
    _grant_directly(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by_user_id=owner,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )

    projection = _project(db_connection, user_id=member, workspace_id=workspace_id)

    assert projection.held_authority_classes == frozenset(
        {AuthorityClass.DECISION_RIGHT, AuthorityClass.SESSION_CONTROL_RIGHT}
    )
    assert projection.governance_capable is False
    assert projection.authorized is True


# ---------------------------------------------------------------------------
# Cross-Work-Unit proof: revoking a binding (WU-01.6) changes the projection
# ---------------------------------------------------------------------------


def test_revoking_the_only_binding_flips_authorized_back_to_false(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-capability-revoke@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Revoke Flips Capability")
    member = _insert_user(db_connection, email="member-capability-revoke@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=member)
    binding_id = _grant_directly(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by_user_id=owner,
        authority_class=AuthorityClass.DECISION_RIGHT,
    )
    before = _project(db_connection, user_id=member, workspace_id=workspace_id)
    assert before.authorized is True

    _revoke(
        db_connection, actor=_human_actor(owner), workspace_id=workspace_id, binding_id=binding_id
    )

    after = _project(db_connection, user_id=member, workspace_id=workspace_id)
    assert after.authorized is False
    assert after.held_authority_classes == frozenset()
    # the member's own role is untouched by revoking an authority binding
    # (role != right, 19 §21 BACKEND REQUIREMENTS)
    assert after.role is WorkspaceRole.CONTRIBUTOR
