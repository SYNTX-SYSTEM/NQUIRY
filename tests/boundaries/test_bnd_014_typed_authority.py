"""F02 WU-02.6 (HD-6): BND-014 evaluates typed authority sources.

MUST BECOME TRUE: every ALLOW carries an `AuthoritySourceProof` whose
`source_ref` is a real, resolvable record (binding id / role assignment
id / founding Command id) and whose `scope_ref` names the exact scope.
MUST REMAIN IMPOSSIBLE: an ALLOW with no authority source; a ROLE ALLOW
for a non-member, a revoked member or a wrong role; a FOUNDING ALLOW for a
non-human actor; a BINDING ALLOW at the wrong scope.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.authority_source import (
    AuthoritySourceType,
    BindingAuthority,
    FoundingAuthority,
    RoleAuthority,
)
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import (
    human_authority_bindings_table,
    role_assignments_table,
    users_table,
    workspace_memberships_table,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _evaluator(db: sa.Connection) -> Bnd014CommitEvaluator:
    membership = SqlAlchemyMembershipRepository(db)
    resolver = AuthorityResolver(
        membership, SqlAlchemyAuthorityBindingRepository(db), FixedClock(_NOW)
    )
    return Bnd014CommitEvaluator(resolver, membership_repository=membership)


def _context(workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_TEST",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _input(context: BoundaryContext, authority: object, **extra: object) -> Bnd014Input:
    return Bnd014Input(
        boundary_id=BoundaryId.BND_014,
        context=context,
        authority=authority,  # type: ignore[arg-type]
        expected_versions={"t": RecordVersion(1)},
        current_versions={"t": RecordVersion(1)},
        upstream_chain_result=BoundaryResult.ALLOW,
        **extra,  # type: ignore[arg-type]
    )


def _seed(db: sa.Connection, tag: str):  # noqa: ANN202
    return NonProofWorkspaceBootstrap(db, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=f"{tag}-{uuid.uuid4().hex[:6]}@t.test"
    )


def _member(
    db: sa.Connection, workspace_id: WorkspaceId, role: WorkspaceRole
) -> tuple[UserId, uuid.UUID]:
    user_id = uuid.uuid4()
    db.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=f"m-{user_id.hex[:8]}@t.test",
            name="M",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    membership_id = uuid.uuid4()
    db.execute(
        sa.insert(workspace_memberships_table).values(
            id=membership_id,
            workspace_id=workspace_id.value,
            user_id=user_id,
            status="ACTIVE",
            created_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )
    role_id = uuid.uuid4()
    db.execute(
        sa.insert(role_assignments_table).values(
            id=role_id,
            workspace_id=workspace_id.value,
            membership_id=membership_id,
            role=role.value,
            granted_by_user_id=user_id,
            granted_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )
    return UserId(user_id), role_id


def test_binding_allow_carries_the_real_binding_id_and_exact_scope(
    db_connection: sa.Connection,
) -> None:
    seeded = _seed(db_connection, "bind")
    session_scope = uuid.uuid4()
    binding_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=seeded.workspace_id.value,
            human_user_id=seeded.owner_user_id.value,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
            scope_type="SESSION",
            scope_id=session_scope,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=seeded.owner_user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, seeded.owner_user_id))
    proof = _evaluator(db_connection).evaluate(
        _input(
            ctx, BindingAuthority(AuthorityClass.SESSION_CONTROL_RIGHT, "SESSION", session_scope)
        ),
        ctx,
    )
    assert proof.result is BoundaryResult.ALLOW
    assert proof.authority_source is not None
    assert proof.authority_source.source_type is AuthoritySourceType.BINDING
    assert proof.authority_source.source_ref == binding_id
    assert proof.authority_source.scope_ref == f"SESSION:{session_scope}"

    # Same binding, different Session scope: denied (HD-1 exact scope).
    other = _evaluator(db_connection).evaluate(
        _input(
            ctx, BindingAuthority(AuthorityClass.SESSION_CONTROL_RIGHT, "SESSION", uuid.uuid4())
        ),
        ctx,
    )
    assert other.result is BoundaryResult.DENY
    assert other.authority_source is None


def test_role_allow_carries_the_current_role_assignment_id(db_connection: sa.Connection) -> None:
    seeded = _seed(db_connection, "role")
    user, role_id = _member(db_connection, seeded.workspace_id, WorkspaceRole.FACILITATOR)
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, user))
    proof = _evaluator(db_connection).evaluate(
        _input(ctx, RoleAuthority(frozenset({WorkspaceRole.FACILITATOR}), "AUTH-DEP-CH-001")), ctx
    )
    assert proof.result is BoundaryResult.ALLOW
    assert proof.authority_source is not None
    assert proof.authority_source.source_type is AuthoritySourceType.ROLE
    assert proof.authority_source.source_ref == role_id
    assert proof.authority_source.scope_ref == f"WORKSPACE:{seeded.workspace_id.value}"
    assert "Facilitator" in proof.authority_source.detail


def test_role_denies_wrong_role(db_connection: sa.Connection) -> None:
    seeded = _seed(db_connection, "wrongrole")
    user, _ = _member(db_connection, seeded.workspace_id, WorkspaceRole.CONTRIBUTOR)
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, user))
    proof = _evaluator(db_connection).evaluate(
        _input(ctx, RoleAuthority(frozenset({WorkspaceRole.FACILITATOR}), "AUTH-DEP-CH-001")), ctx
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("ROLE_NOT_ACCEPTED")


def test_role_denies_non_member_and_revoked_member(db_connection: sa.Connection) -> None:
    seeded = _seed(db_connection, "nonmember")
    stranger = UserId(uuid.uuid4())
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, stranger))
    proof = _evaluator(db_connection).evaluate(
        _input(ctx, RoleAuthority(frozenset({WorkspaceRole.FACILITATOR}), "AUTH-DEP-CH-001")), ctx
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "ROLE_NO_ACTIVE_MEMBERSHIP"

    user, _ = _member(db_connection, seeded.workspace_id, WorkspaceRole.FACILITATOR)
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.user_id == user.value)
        .values(status="REVOKED", revoked_at=_NOW, record_version=2)
    )
    ctx2 = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, user))
    proof2 = _evaluator(db_connection).evaluate(
        _input(ctx2, RoleAuthority(frozenset({WorkspaceRole.FACILITATOR}), "AUTH-DEP-CH-001")), ctx2
    )
    assert proof2.result is BoundaryResult.DENY


def test_role_fails_closed_without_membership_reader(db_connection: sa.Connection) -> None:
    seeded = _seed(db_connection, "noreader")
    user, _ = _member(db_connection, seeded.workspace_id, WorkspaceRole.FACILITATOR)
    membership = SqlAlchemyMembershipRepository(db_connection)
    evaluator = Bnd014CommitEvaluator(
        AuthorityResolver(
            membership, SqlAlchemyAuthorityBindingRepository(db_connection), FixedClock(_NOW)
        )
    )
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, user))
    proof = evaluator.evaluate(
        _input(ctx, RoleAuthority(frozenset({WorkspaceRole.FACILITATOR}), "AUTH-DEP-CH-001")), ctx
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "ROLE_READER_NOT_CONFIGURED"


def test_founding_allow_references_the_founding_command(db_connection: sa.Connection) -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    command_ref = uuid.uuid4()
    ctx = _context(workspace_id, ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4())))
    proof = _evaluator(db_connection).evaluate(
        Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=ctx,
            authority=FoundingAuthority(eligibility_reason_code="UNGATED_SELF_SERVICE"),
            expected_versions={},
            current_versions={},
            upstream_chain_result=BoundaryResult.ALLOW,
            command_ref=command_ref,
        ),
        ctx,
    )
    assert proof.result is BoundaryResult.ALLOW
    assert proof.authority_source is not None
    assert proof.authority_source.source_type is AuthoritySourceType.FOUNDING
    assert proof.authority_source.source_ref == command_ref
    assert proof.authority_source.scope_ref == f"WORKSPACE:{workspace_id.value}"
    assert "UNGATED_SELF_SERVICE" in proof.authority_source.detail


def test_founding_denies_non_human_actor(db_connection: sa.Connection) -> None:
    workspace_id = WorkspaceId(uuid.uuid4())
    ctx = _context(workspace_id, ActorIdentity(ActorClass.AI_PROCESSOR, UserId(uuid.uuid4())))
    proof = _evaluator(db_connection).evaluate(
        Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=ctx,
            authority=FoundingAuthority(eligibility_reason_code="UNGATED_SELF_SERVICE"),
            expected_versions={},
            current_versions={},
            upstream_chain_result=BoundaryResult.ALLOW,
            command_ref=uuid.uuid4(),
        ),
        ctx,
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.authority_source is None


def test_founding_requires_a_command_ref() -> None:
    ctx = _context(
        WorkspaceId(uuid.uuid4()), ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    )
    with pytest.raises(ValueError, match="command_ref"):
        Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=ctx,
            authority=FoundingAuthority(eligibility_reason_code="X"),
            expected_versions={},
            current_versions={},
            upstream_chain_result=BoundaryResult.ALLOW,
        )


def test_legacy_binding_fields_still_produce_a_typed_proof(db_connection: sa.Connection) -> None:
    seeded = _seed(db_connection, "legacy")
    binding_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=seeded.workspace_id.value,
            human_user_id=seeded.owner_user_id.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=seeded.workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=seeded.owner_user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )
    ctx = _context(seeded.workspace_id, ActorIdentity(ActorClass.HUMAN_USER, seeded.owner_user_id))
    proof = _evaluator(db_connection).evaluate(
        Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=ctx,
            required_authority_class=AuthorityClass.DECISION_RIGHT,
            authority_scope_type="WORKSPACE",
            authority_scope_id=seeded.workspace_id.value,
            expected_versions={},
            current_versions={},
            upstream_chain_result=BoundaryResult.ALLOW,
        ),
        ctx,
    )
    assert proof.result is BoundaryResult.ALLOW
    assert proof.authority_source is not None
    assert proof.authority_source.source_ref == binding_id
