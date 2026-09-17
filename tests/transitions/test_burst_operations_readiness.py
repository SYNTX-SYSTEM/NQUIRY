"""T2 TRANSITION TEST: `application.burst_operations.check_burst_operation_readiness`.

13 §6 T2 scope: "State fixtures, Commands" -- this compositor's whole
purpose is combining a state fixture (current Burst state) with a real
authority resolution, so its proof belongs here rather than inventing
a new test directory outside this package's `FILES_ALLOWED_TO_CREATE`
(`tests/transitions, boundaries and ai guards` -- no `tests/application`
is authorized).

Uses `NonProofWorkspaceBootstrap` for the Workspace/owner/membership
(13 §5's permitted downstream use), then grants `SESSION_CONTROL_RIGHT`
directly (mirroring `test_cross_layer_authority_resolver_grants_against_the_seeded_root`'s
style in `tests/regression/test_nonproof_bootstrap.py`) -- the fixture
only proves the invariant under test here (readiness composition), not
bootstrap legitimacy.
"""

from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from application.burst_operations import BurstOperationOutcome, check_burst_operation_readiness
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityVerdict
from domain.burst import BurstState
from domain.burst_transitions import BurstOperation, BurstTransitionVerdict
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import UserId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_workspace_with_owner(connection: sa.Connection, *, owner_email: str):
    bootstrap = NonProofWorkspaceBootstrap(connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=owner_email)


def _grant_session_control_right(
    connection: sa.Connection, *, workspace_id: WorkspaceId, user_id: UserId
) -> None:
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def _repos(connection: sa.Connection):
    return (
        SqlAlchemyMembershipRepository(connection),
        SqlAlchemyAuthorityBindingRepository(connection),
    )


def test_ready_when_authority_granted_and_transition_eligible(db_connection: sa.Connection) -> None:
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="ready@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.PREPARE_BURST,
        current_state=None,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.READY
    assert outcome.is_ready
    assert outcome.transition_verdict is BurstTransitionVerdict.STATE_ELIGIBLE
    assert outcome.authority_verdict is AuthorityVerdict.GRANTED


def test_denied_authority_when_no_binding_exists(db_connection: sa.Connection) -> None:
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="no-binding@nonproof.test")
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.PREPARE_BURST,
        current_state=None,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_AUTHORITY
    assert outcome.transition_verdict is BurstTransitionVerdict.STATE_ELIGIBLE
    assert outcome.authority_verdict is AuthorityVerdict.DENIED


def test_denied_transition_when_authority_granted_but_state_illegal(
    db_connection: sa.Connection,
) -> None:
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="bad-state@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.START_BURST,
        current_state=BurstState.COMPLETED,  # START_BURST only legal from PREPARED
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_TRANSITION
    assert outcome.transition_verdict is BurstTransitionVerdict.DENIED_TERMINAL_STATE
    assert outcome.authority_verdict is AuthorityVerdict.GRANTED


def test_denied_both_when_neither_authority_nor_transition_hold(
    db_connection: sa.Connection,
) -> None:
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="denied-both@nonproof.test")
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.START_BURST,
        current_state=BurstState.COMPLETED,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_BOTH


def test_system_service_actor_cannot_complete_a_burst_via_this_compositor(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: timer auto-completes without
    authority. `AuthorityResolver` structurally denies any non-`HUMAN_USER`
    actor before ever reading a binding (04 §3.3/05 AC-05-007) -- a
    `SYSTEM_SERVICE` "timer" actor is refused here independent of
    whatever binding exists, proving no automatic/system completion
    path exists through this compositor.
    """
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="timer@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.COMPLETE_BURST,
        current_state=BurstState.ACTIVE,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_AUTHORITY
    assert outcome.authority_verdict is AuthorityVerdict.DENIED


def test_ai_processor_actor_is_denied_authority_for_any_burst_operation(
    db_connection: sa.Connection,
) -> None:
    """Second, independent layer proving AI cannot control the Burst
    lifecycle: even without the contamination guard, `AuthorityResolver`
    itself refuses an `AI_PROCESSOR` actor (04 §3.3: "AI_PROCESSOR may
    not receive human decision rights").
    """
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="ai-actor@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.START_BURST,
        current_state=BurstState.PREPARED,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_AUTHORITY
    assert outcome.authority_verdict is AuthorityVerdict.DENIED


def test_unresolved_ambiguous_bindings_is_never_treated_as_success(
    db_connection: sa.Connection,
) -> None:
    """14 §16: `UNRESOLVED` is fail-closed -- two active
    `SESSION_CONTROL_RIGHT` bindings for the same actor/scope must never
    resolve to `READY`.
    """
    result = _bootstrap_workspace_with_owner(db_connection, owner_email="ambiguous@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation=BurstOperation.PREPARE_BURST,
        current_state=None,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.UNRESOLVED_AUTHORITY
    assert outcome.authority_verdict is AuthorityVerdict.UNRESOLVED
    assert not outcome.is_ready


def test_cross_workspace_actor_has_no_authority(db_connection: sa.Connection) -> None:
    """Mandatory-category Workspace attack: an actor's
    `SESSION_CONTROL_RIGHT` in Workspace A grants nothing in Workspace B.
    """
    workspace_a = _bootstrap_workspace_with_owner(db_connection, owner_email="ws-a@nonproof.test")
    workspace_b = _bootstrap_workspace_with_owner(db_connection, owner_email="ws-b@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=workspace_a.workspace_id, user_id=workspace_a.owner_user_id
    )
    membership_repo, binding_repo = _repos(db_connection)

    outcome = check_burst_operation_readiness(
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
        workspace_id=workspace_b.workspace_id,
        operation=BurstOperation.PREPARE_BURST,
        current_state=None,
        membership_repository=membership_repo,
        authority_binding_repository=binding_repo,
        clock=FixedClock(_NOW),
    )

    assert outcome.outcome is BurstOperationOutcome.DENIED_AUTHORITY
