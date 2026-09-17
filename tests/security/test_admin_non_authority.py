"""P-24 (14 §50, 13 §6 T13-P24-ADMIN-NONAUTH): "admin/root decides ->
no legitimate transition".

Exercised now that `packages/authority` (PKG-03) exists — deferred
from PKG-00 exactly as that package's own skip reason anticipated:
"Exercise once packages/authority and packages/governance are
implemented."

There is no `ADMIN` `ActorClass` (04 §3 defines exactly `HUMAN_USER`,
`SYSTEM_SERVICE`, `AI_PROCESSOR`, `EXTERNAL_SYSTEM` — "ADMIN API !=
GOVERNANCE AUTHORITY" per 14 non-collapse). An "admin" is,
architecturally, nothing more than a `HUMAN_USER` who happens to also
hold elevated technical/infrastructure access (e.g. a `migration_owner`
DB principal, PKG-25 scope) — that technical privilege carries no
`AuthorityRequest` field at all, so the only way this test can express
"admin" is: a real, authenticated human, Workspace member, with no
`DECISION_RIGHT` `HumanAuthorityBinding`. 13's table's own ATTACK/
LEGITIMATE CONTROL columns are both reproduced here.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import (
    AuthorityRequest,
    AuthorityResolver,
    AuthorityVerdict,
    ResolutionReason,
)
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import (
    human_authority_bindings_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from semantic_types.ids import UserId, WorkspaceId
from test_support.clock import FixedClock


def _resolver(connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(connection),
        SqlAlchemyAuthorityBindingRepository(connection),
        FixedClock(datetime(2030, 1, 1, tzinfo=timezone.utc)),
    )


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Test User",
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return UserId(user_id)


def _insert_workspace(connection: sa.Connection, *, owner_id: UserId) -> WorkspaceId:
    workspace_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name="W",
            owner_id=owner_id.value,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return WorkspaceId(workspace_id)


def _insert_membership(
    connection: sa.Connection, *, workspace_id: WorkspaceId, user_id: UserId
) -> None:
    connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            user_id=user_id.value,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )


def test_admin_cannot_create_a_legitimate_decision(db_connection: sa.Connection) -> None:
    """ATTACK column: "admin finalizes Decision" with no human right."""
    owner = _insert_user(db_connection, email="owner@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    admin = _insert_user(db_connection, email="admin@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=admin)
    # Deliberately no human_authority_bindings row for `admin` at all --
    # elevated technical access grants nothing here because there is
    # nothing for it to grant through.

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, admin),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=uuid.uuid4(),
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_human_right_positive_control_grants_the_decision(db_connection: sa.Connection) -> None:
    """LEGITIMATE CONTROL column: the same operation, for a human who
    actually holds `DECISION_RIGHT`, is `GRANTED` -- proving the attack
    above fails because of the missing binding specifically, not
    because resolution is broken outright.
    """
    owner = _insert_user(db_connection, email="owner2@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    decision_maker = _insert_user(db_connection, email="decider@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=decision_maker)
    scope_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            human_user_id=decision_maker.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="DECISION",
            scope_id=scope_id,
            authority_source="WORKSPACE_GOVERNANCE_ROOT",
            granted_by_user_id=owner.value,
            granted_at=datetime.now(timezone.utc),
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, decision_maker),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.GRANTED
