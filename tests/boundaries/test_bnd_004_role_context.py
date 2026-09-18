"""T4 BOUNDARY TEST: BND-004 Role/Governance Context Evaluator, against
real PostgreSQL.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_004_role_context import Bnd004Input, Bnd004RoleContextEvaluator
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from governance.membership import WorkspaceRole
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import role_assignments_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="TEST_OPERATION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _grant_role(
    connection: sa.Connection,
    *,
    membership_id: uuid.UUID,
    workspace_id: WorkspaceId,
    role: WorkspaceRole,
    granted_by_user_id: uuid.UUID,
) -> None:
    connection.execute(
        sa.insert(role_assignments_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            membership_id=membership_id,
            role=role.value,
            granted_by_user_id=granted_by_user_id,
            granted_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )


def test_allows_an_accepted_current_role(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd004-allow@nonproof.test")
    _grant_role(
        db_connection,
        membership_id=result.membership_id,
        workspace_id=result.workspace_id,
        role=WorkspaceRole.FACILITATOR,
        granted_by_user_id=result.owner_user_id.value,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd004RoleContextEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd004Input(
        boundary_id=BoundaryId.BND_004,
        context=context,
        membership_id=result.membership_id,
        accepted_roles=frozenset({WorkspaceRole.FACILITATOR}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_a_role_not_in_the_accepted_set(db_connection: sa.Connection) -> None:
    """Mandatory-category attack: role-only authority -- 06 section 10
    DENY example: "Observer/Viewer mutation".
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd004-wrong-role@nonproof.test")
    _grant_role(
        db_connection,
        membership_id=result.membership_id,
        workspace_id=result.workspace_id,
        role=WorkspaceRole.VIEWER,
        granted_by_user_id=result.owner_user_id.value,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd004RoleContextEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd004Input(
        boundary_id=BoundaryId.BND_004,
        context=context,
        membership_id=result.membership_id,
        accepted_roles=frozenset({WorkspaceRole.FACILITATOR}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert "VIEWER" in proof.reason_code.upper() or "Viewer" in proof.reason_code


def test_denies_no_current_role(db_connection: sa.Connection) -> None:
    """Novel attack: stale role after removal -- here in its "no role
    row at all" shape.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd004-no-role@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd004RoleContextEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd004Input(
        boundary_id=BoundaryId.BND_004,
        context=context,
        membership_id=result.membership_id,
        accepted_roles=frozenset({WorkspaceRole.FACILITATOR}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "NO_CURRENT_ROLE"


def test_denies_a_revoked_role(db_connection: sa.Connection) -> None:
    """Novel attack: stale role after removal -- here in its "role was
    revoked" shape.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd004-revoked-role@nonproof.test")
    _grant_role(
        db_connection,
        membership_id=result.membership_id,
        workspace_id=result.workspace_id,
        role=WorkspaceRole.FACILITATOR,
        granted_by_user_id=result.owner_user_id.value,
    )
    db_connection.execute(
        sa.update(role_assignments_table)
        .where(role_assignments_table.c.membership_id == result.membership_id)
        .values(revoked_at=_NOW, record_version=2)
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd004RoleContextEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd004Input(
        boundary_id=BoundaryId.BND_004,
        context=context,
        membership_id=result.membership_id,
        accepted_roles=frozenset({WorkspaceRole.FACILITATOR}),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "NO_CURRENT_ROLE"
