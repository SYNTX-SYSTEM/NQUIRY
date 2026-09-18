"""T4 BOUNDARY TEST: BND-002 Workspace Evaluator, against real PostgreSQL.

Uses `NonProofWorkspaceBootstrap` for the Workspace/owner (13 §5's
permitted downstream use); the invariant under test (Workspace
resolution/isolation) does not depend on how the Workspace came to
exist.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
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


def test_allows_a_single_effective_workspace(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd002-allow@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
    boundary_input = Bnd002Input(
        boundary_id=BoundaryId.BND_002,
        context=context,
        resolved_object_workspace_ids=(result.workspace_id,),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW


def test_denies_cross_workspace_object_set(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: Workspace mismatch."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_a = bootstrap.seed(owner_email="bnd002-a@nonproof.test")
    workspace_b = bootstrap.seed(owner_email="bnd002-b@nonproof.test")
    context = _context(
        workspace_id=workspace_a.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
    )
    evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
    boundary_input = Bnd002Input(
        boundary_id=BoundaryId.BND_002,
        context=context,
        resolved_object_workspace_ids=(workspace_a.workspace_id, workspace_b.workspace_id),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CROSS_WORKSPACE_OBJECT_SET"


def test_denies_unresolvable_workspace_with_no_objects(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd002-empty@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
    boundary_input = Bnd002Input(
        boundary_id=BoundaryId.BND_002, context=context, resolved_object_workspace_ids=()
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "UNRESOLVED_WORKSPACE_NO_OBJECTS"


def test_denies_claimed_workspace_differing_from_resolved_scope(
    db_connection: sa.Connection,
) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_a = bootstrap.seed(owner_email="bnd002-claim-a@nonproof.test")
    workspace_b = bootstrap.seed(owner_email="bnd002-claim-b@nonproof.test")
    # Actor claims workspace_b's context, but the object actually
    # resolves to workspace_a.
    context = _context(
        workspace_id=workspace_b.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
    )
    evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
    boundary_input = Bnd002Input(
        boundary_id=BoundaryId.BND_002,
        context=context,
        resolved_object_workspace_ids=(workspace_a.workspace_id,),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CLAIMED_WORKSPACE_MISMATCH"


def test_denies_a_workspace_id_that_does_not_exist(db_connection: sa.Connection) -> None:
    nonexistent = WorkspaceId(uuid.uuid4())
    context = _context(
        workspace_id=nonexistent,
        actor=ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4())),
    )
    evaluator = Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection))
    boundary_input = Bnd002Input(
        boundary_id=BoundaryId.BND_002,
        context=context,
        resolved_object_workspace_ids=(nonexistent,),
    )

    proof = evaluator.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "UNRESOLVED_WORKSPACE_NOT_FOUND"
