"""T4 BOUNDARY TEST: BND-014 Commit Evaluator, against real PostgreSQL,
wrapping the real `AuthorityResolver` (PKG-03).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_TEST_OPERATION",
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


def _evaluator(db_connection: sa.Connection) -> Bnd014CommitEvaluator:
    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )
    return Bnd014CommitEvaluator(resolver)


def _base_input(
    *, workspace_id: WorkspaceId, context: BoundaryContext, **overrides: object
) -> Bnd014Input:
    kwargs: dict[str, object] = {
        "boundary_id": BoundaryId.BND_014,
        "context": context,
        "required_authority_class": AuthorityClass.SESSION_CONTROL_RIGHT,
        "authority_scope_type": "WORKSPACE",
        "authority_scope_id": workspace_id.value,
        "expected_versions": {"burst-1": RecordVersion(1)},
        "current_versions": {"burst-1": RecordVersion(1)},
        "upstream_chain_result": BoundaryResult.ALLOW,
    }
    kwargs.update(overrides)
    return Bnd014Input(**kwargs)  # type: ignore[arg-type]


def test_allows_when_every_commit_sensitive_predicate_is_current(
    db_connection: sa.Connection,
) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-allow@nonproof.test")
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
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "COMMIT_SENSITIVE_PREDICATES_CURRENT"
    assert proof.authority_proof is not None
    assert proof.authority_proof.reason.value == "GRANTED_EFFECTIVE_BINDING"


def test_denies_when_upstream_chain_did_not_allow(db_connection: sa.Connection) -> None:
    """06 section 20 PRECONDITIONS: "Every applicable upstream boundary
    currently allows."
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-upstream-deny@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, upstream_chain_result=BoundaryResult.DENY
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("UPSTREAM_CHAIN_NOT_ALLOW")


def test_denies_a_stale_expected_version(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: state version changed."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-stale-version@nonproof.test")
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
    boundary_input = _base_input(
        workspace_id=result.workspace_id,
        context=context,
        expected_versions={"burst-1": RecordVersion(1)},
        current_versions={"burst-1": RecordVersion(2)},  # competing operation advanced it
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "STALE_VERSION:burst-1"


def test_denies_a_target_that_no_longer_exists(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: the target ref vanished entirely (current
    version unresolvable) between preparation and commit.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-vanished-target@nonproof.test")
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
    boundary_input = _base_input(
        workspace_id=result.workspace_id,
        context=context,
        expected_versions={"burst-1": RecordVersion(1)},
        current_versions={"burst-1": None},
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "STALE_VERSION:burst-1"


def test_denies_authority_revoked_after_preparation(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: authority revoked after
    preparation."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-revoked@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.human_user_id == result.owner_user_id.value)
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
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("AUTHORITY_NOT_CURRENT")


def test_denies_a_never_granted_authority(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-never-granted@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AUTHORITY_NOT_CURRENT:DENIED_NO_MATCHING_BINDING"


def test_allows_an_operation_with_no_targets_at_all(db_connection: sa.Connection) -> None:
    """Positive control: a creation-style operation with no pre-existing
    target has nothing to check versions for -- not vacuously denied.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-no-targets@nonproof.test")
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
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, expected_versions={}, current_versions={}
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
