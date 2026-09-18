"""T4 BOUNDARY TEST: BND-005 Human Authority Evaluator, against real
PostgreSQL, wrapping the real `AuthorityResolver` (PKG-03).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_005_human_authority import Bnd005HumanAuthorityEvaluator, Bnd005Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="BEGIN_SETUP",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _grant(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    user_id: uuid.UUID,
    authority_class: AuthorityClass,
) -> None:
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id,
            authority_class=authority_class.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def _evaluator(db_connection: sa.Connection) -> Bnd005HumanAuthorityEvaluator:
    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )
    return Bnd005HumanAuthorityEvaluator(resolver)


def test_allows_a_granted_authority_class(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-allow@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.authority_proof is not None
    assert proof.authority_proof.reason.value == "GRANTED_EFFECTIVE_BINDING"


def test_denies_missing_binding(db_connection: sa.Connection) -> None:
    """Mandatory-category attack: role-only authority -- no binding at
    all, only membership.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-missing@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_NO_MATCHING_BINDING"


def test_denies_wrong_scope(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-wrongscope@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="SESSION",  # binding is scoped WORKSPACE, not SESSION
        scope_id=uuid.uuid4(),
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_WRONG_SCOPE"


def test_denies_a_revoked_binding(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-revoked@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.human_user_id == result.owner_user_id.value)
        .where(human_authority_bindings_table.c.authority_class == "SESSION_CONTROL_RIGHT")
        .values(
            state=AuthorityBindingState.REVOKED.value,
            revoked_at=_NOW,
            revoked_by_user_id=result.owner_user_id.value,
        )
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY


def test_denies_an_ai_processor_actor(db_connection: sa.Connection) -> None:
    """04 section 3.3: AI_PROCESSOR may never receive a human decision
    right, regardless of any binding row.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-ai@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DENIED_ACTOR_NOT_HUMAN"


def test_ambiguous_bindings_are_never_allow(db_connection: sa.Connection) -> None:
    """14 section 16: UNRESOLVED is fail-closed -- never treated as
    ALLOW at the boundary layer either.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd005-ambiguous@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = Bnd005Input(
        boundary_id=BoundaryId.BND_005,
        context=context,
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS"
