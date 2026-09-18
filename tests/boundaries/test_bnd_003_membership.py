"""T4 BOUNDARY TEST: BND-003 Membership Evaluator, against real PostgreSQL."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import workspace_memberships_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
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


def test_allows_an_active_member(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd003-active@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd003Input(boundary_id=BoundaryId.BND_003, context=context)

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_a_non_member(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: missing membership."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd003-nonmember@nonproof.test")
    stranger_user_id = UserId(uuid.uuid4())
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, stranger_user_id),
    )
    evaluator = Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd003Input(boundary_id=BoundaryId.BND_003, context=context)

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "NO_ACTIVE_MEMBERSHIP"


def test_denies_a_revoked_member(db_connection: sa.Connection) -> None:
    """Novel attack: revoked membership treated as active -- 06 section
    9 TESTABLE INVARIANT: "A removed Workspace member cannot commit ...
    even if an older authority binding still exists in storage."
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd003-revoked@nonproof.test")
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.id == result.membership_id)
        .values(status="REVOKED", revoked_at=_NOW, record_version=2)
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd003Input(boundary_id=BoundaryId.BND_003, context=context)

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "NO_ACTIVE_MEMBERSHIP"


def test_denies_membership_in_a_different_workspace(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_a = bootstrap.seed(owner_email="bnd003-cross-a@nonproof.test")
    workspace_b = bootstrap.seed(owner_email="bnd003-cross-b@nonproof.test")
    context = _context(
        workspace_id=workspace_b.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
    )
    evaluator = Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd003Input(boundary_id=BoundaryId.BND_003, context=context)

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY


def test_denies_a_non_human_actor(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd003-nonhuman@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, result.owner_user_id),
    )
    evaluator = Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection))
    boundary_input = Bnd003Input(boundary_id=BoundaryId.BND_003, context=context)

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "MEMBERSHIP_REQUIRES_HUMAN_ACTOR"
