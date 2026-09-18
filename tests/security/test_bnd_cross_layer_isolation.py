"""T9 SECURITY / ISOLATION TEST: chained BND-001..005 evaluation against
real PostgreSQL -- P-13 (Boundary DENY prevents consequence, no
downstream override) and P-22 (Workspace isolation) exercised with the
*real* concrete evaluators this package builds, registered into
PKG-08's real `BoundaryRegistry`/`evaluate_chain` -- not test-only
fixtures this time, the actual production evaluators.

13 §6 T9 scope: "Workspace isolation, identity, direct-write and
gateway controls... Two Workspaces, service principals... Technical
bypass blocked/detected."
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_003_membership import Bnd003Input, Bnd003MembershipEvaluator
from boundaries.bnd_005_human_authority import Bnd005HumanAuthorityEvaluator, Bnd005Input
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()

_FULL_CHAIN = [BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003, BoundaryId.BND_005]


def _build_registry(db_connection: sa.Connection) -> BoundaryRegistry:
    registry = BoundaryRegistry()
    registry.register(Bnd001IdentityEvaluator())
    registry.register(Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository(db_connection)))
    registry.register(Bnd003MembershipEvaluator(SqlAlchemyMembershipRepository(db_connection)))
    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )
    registry.register(Bnd005HumanAuthorityEvaluator(resolver))
    return registry


def _grant_session_control_right(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, user_id: uuid.UUID
) -> None:
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def _inputs(*, context: BoundaryContext, workspace_id: WorkspaceId) -> dict:
    return {
        BoundaryId.BND_001: Bnd001Input(
            boundary_id=BoundaryId.BND_001,
            context=context,
            required_actor_classes=frozenset({ActorClass.HUMAN_USER}),
        ),
        BoundaryId.BND_002: Bnd002Input(
            boundary_id=BoundaryId.BND_002,
            context=context,
            resolved_object_workspace_ids=(workspace_id,),
        ),
        BoundaryId.BND_003: Bnd003Input(boundary_id=BoundaryId.BND_003, context=context),
        BoundaryId.BND_005: Bnd005Input(
            boundary_id=BoundaryId.BND_005,
            context=context,
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
        ),
    }


def test_full_chain_allows_a_legitimate_authorized_member(db_connection: sa.Connection) -> None:
    """The complete, real chained proof: a genuine human identity, in
    its own real Workspace, as a real active member, holding a real
    SESSION_CONTROL_RIGHT binding -- reaches ALLOW through all four
    boundaries.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-full-allow@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id.value
    )
    registry = _build_registry(db_connection)
    context = BoundaryContext(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    inputs = _inputs(context=context, workspace_id=result.workspace_id)

    chain_result = evaluate_chain(registry, _FULL_CHAIN, inputs, context)

    assert chain_result.result is BoundaryResult.ALLOW
    assert len(chain_result.proofs) == 4


def test_missing_authority_denies_at_bnd005_after_bnd001_002_003_allow(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: downstream ALLOW after earlier
    DENY -- here proven the other direction, showing the chain's own
    natural stopping point: identity/Workspace/membership are all
    genuinely fine (each ALLOWs for real), and only the final,
    authority-specific boundary denies -- proving BND-001/002/003 are
    not silently substituting for BND-005's own distinct check.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-no-authority@nonproof.test")
    # Deliberately no SESSION_CONTROL_RIGHT granted.
    registry = _build_registry(db_connection)
    context = BoundaryContext(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    inputs = _inputs(context=context, workspace_id=result.workspace_id)

    chain_result = evaluate_chain(registry, _FULL_CHAIN, inputs, context)

    assert chain_result.result is BoundaryResult.DENY
    assert chain_result.terminal_boundary_id is BoundaryId.BND_005
    assert len(chain_result.proofs) == 4  # all four ran; only the last denied
    assert chain_result.proofs[0].result is BoundaryResult.ALLOW  # BND-001
    assert chain_result.proofs[1].result is BoundaryResult.ALLOW  # BND-002
    assert chain_result.proofs[2].result is BoundaryResult.ALLOW  # BND-003
    assert chain_result.proofs[3].result is BoundaryResult.DENY  # BND-005


def test_non_member_is_denied_at_bnd003_before_bnd005_ever_runs(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: downstream ALLOW after earlier
    DENY -- a stranger with no membership is denied at BND-003, and the
    real (injected) BND-005 evaluator, which *would* deny anyway, is
    proven never invoked at all.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-non-member@nonproof.test")
    stranger = ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))
    registry = _build_registry(db_connection)
    context = BoundaryContext(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=stranger,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    inputs = _inputs(context=context, workspace_id=result.workspace_id)

    chain_result = evaluate_chain(registry, _FULL_CHAIN, inputs, context)

    assert chain_result.result is BoundaryResult.DENY
    assert chain_result.terminal_boundary_id is BoundaryId.BND_003
    assert len(chain_result.proofs) == 3  # BND-005 never reached


def test_cross_workspace_actor_denied_at_bnd002_before_membership_or_authority_checked(
    db_connection: sa.Connection,
) -> None:
    """P-22 (Cross-Workspace isolation): an actor belonging to
    Workspace A, attempting an operation whose object resolves to
    Workspace B, is denied at BND-002 -- before BND-003/BND-005 ever
    read anything about Workspace B at all.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_a = bootstrap.seed(owner_email="chain-cross-a@nonproof.test")
    workspace_b = bootstrap.seed(owner_email="chain-cross-b@nonproof.test")
    _grant_session_control_right(
        db_connection,
        workspace_id=workspace_a.workspace_id,
        user_id=workspace_a.owner_user_id.value,
    )
    registry = _build_registry(db_connection)
    # Actor and requested context both claim Workspace A, but the
    # object under operation actually resolves to Workspace B.
    context = BoundaryContext(
        workspace_id=workspace_a.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    inputs = _inputs(context=context, workspace_id=workspace_a.workspace_id)
    inputs[BoundaryId.BND_002] = Bnd002Input(
        boundary_id=BoundaryId.BND_002,
        context=context,
        resolved_object_workspace_ids=(workspace_b.workspace_id,),
    )

    chain_result = evaluate_chain(registry, _FULL_CHAIN, inputs, context)

    assert chain_result.result is BoundaryResult.DENY
    assert chain_result.terminal_boundary_id is BoundaryId.BND_002
    # BND-001 (identity) genuinely ALLOWs first -- the actor's identity
    # itself is fine; BND-002 (Workspace) is where the cross-Workspace
    # object resolution is caught. BND-003/BND-005 never run.
    assert len(chain_result.proofs) == 2
    assert chain_result.proofs[0].result is BoundaryResult.ALLOW  # BND-001
    assert chain_result.proofs[1].result is BoundaryResult.DENY  # BND-002


def test_ai_processor_denied_at_bnd001_before_any_later_boundary_runs(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: forged identity, chained -- an
    AI_PROCESSOR actor is refused at the very first boundary, before
    Workspace/membership/authority are ever consulted.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-ai-actor@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id.value
    )
    registry = _build_registry(db_connection)
    context = BoundaryContext(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, result.owner_user_id),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    inputs = _inputs(context=context, workspace_id=result.workspace_id)

    chain_result = evaluate_chain(registry, _FULL_CHAIN, inputs, context)

    assert chain_result.result is BoundaryResult.DENY
    assert chain_result.terminal_boundary_id is BoundaryId.BND_001
    assert len(chain_result.proofs) == 1
