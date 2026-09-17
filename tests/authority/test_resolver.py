"""T3/T4 authority tests: AuthorityResolver, against real PostgreSQL.

PKG-03 is flagged a "critical package" requiring >=10 total
novel/adapted attacks; this file covers the 10 package-mandatory
attacks (role-only, Owner-only, author-only, AI, service, revoked
binding, wrong scope, wrong Workspace, stale binding, missing
membership) plus 3 novel ones (ambiguous active bindings -> UNRESOLVED,
no admin/role field exists to smuggle a bypass through, and
cross-authority-class confusion), for 13 total.
"""

from __future__ import annotations

import dataclasses
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
from governance.membership import WorkspaceRole
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import (
    human_authority_bindings_table,
    role_assignments_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from semantic_types.ids import UserId, WorkspaceId
from test_support.clock import FixedClock


def _resolver(connection: sa.Connection, *, now: datetime | None = None) -> AuthorityResolver:
    clock = FixedClock(now or datetime(2030, 1, 1, tzinfo=timezone.utc))
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(connection),
        SqlAlchemyAuthorityBindingRepository(connection),
        clock,
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
) -> uuid.UUID:
    membership_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=membership_id,
            workspace_id=workspace_id.value,
            user_id=user_id.value,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )
    return membership_id


def _insert_role(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    membership_id: uuid.UUID,
    role: WorkspaceRole,
    granted_by: UserId,
) -> None:
    connection.execute(
        sa.insert(role_assignments_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            membership_id=membership_id,
            role=role.value,
            granted_by_user_id=granted_by.value,
            granted_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )


def _insert_binding(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    granted_by: UserId,
    authority_class: AuthorityClass = AuthorityClass.DECISION_RIGHT,
    scope_type: str = "DECISION",
    scope_id: uuid.UUID | None = None,
) -> uuid.UUID:
    binding_id = uuid.uuid4()
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=human_user_id.value,
            authority_class=authority_class.value,
            scope_type=scope_type,
            scope_id=scope_id if scope_id is not None else uuid.uuid4(),
            authority_source="WORKSPACE_GOVERNANCE_ROOT",
            granted_by_user_id=granted_by.value,
            granted_at=datetime.now(timezone.utc),
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )
    return binding_id


def test_granted_when_effective_binding_exists(db_connection: sa.Connection) -> None:
    """Positive control: everything the mandatory attacks below try to
    fake or bypass, present for real.
    """
    owner = _insert_user(db_connection, email="owner@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    binding_id = _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.GRANTED
    assert resolution.proof.reason == ResolutionReason.GRANTED_EFFECTIVE_BINDING
    assert str(resolution.proof.binding_id) == str(binding_id)
    assert resolution.proof.operation == "RECORD_DECISION"


def test_role_only_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: role-only. A Facilitator role
    assignment with no explicit HABB grants nothing (05 AC-05-005)."""
    owner = _insert_user(db_connection, email="owner2@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member2@test.local")
    membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    _insert_role(
        db_connection,
        workspace_id=workspace_id,
        membership_id=membership_id,
        role=WorkspaceRole.FACILITATOR,
        granted_by=owner,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="START_BURST",
        required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="SESSION",
        scope_id=uuid.uuid4(),
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_owner_only_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: Owner-only (AC-04-001: Owner is not
    an automatic executor of every operation; ATK-005)."""
    owner = _insert_user(db_connection, email="owner3@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=owner)
    _insert_role(
        db_connection,
        workspace_id=workspace_id,
        membership_id=membership_id,
        role=WorkspaceRole.OWNER,
        granted_by=owner,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, owner),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=uuid.uuid4(),
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_author_only_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: author-only. No domain object with
    an "author" field exists yet (Question is PKG-06); the closest
    faithful stand-in is the human who *granted* someone else's binding
    -- granting authority to another does not itself confer that
    authority on the grantor (06 §11 PROHIBITED PATH: "human authorship
    -> authority")."""
    owner = _insert_user(db_connection, email="owner4@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    grantor = _insert_user(db_connection, email="grantor4@test.local")
    beneficiary = _insert_user(db_connection, email="beneficiary4@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=grantor)
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=beneficiary)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=beneficiary,
        granted_by=grantor,
        scope_id=scope_id,
    )

    # The grantor ("author" of the binding record) tries to use the
    # very authority they granted someone else.
    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, grantor),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_ai_processor_actor_is_denied_even_with_a_real_human_binding(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: AI (04 §3.3: AI_PROCESSOR may not
    receive human decision rights -- ATK-003). Uses the UserId of a
    human who genuinely holds the binding, to prove the actor_class
    check is authoritative independent of what the UserId itself would
    otherwise qualify for.
    """
    owner = _insert_user(db_connection, email="owner5@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member5@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.AI_PROCESSOR, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_ACTOR_NOT_HUMAN


def test_system_service_actor_is_denied_even_with_a_real_human_binding(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: service (04 §8: SYSTEM_DERIVED
    authority is a different mechanism entirely -- ATK-009)."""
    owner = _insert_user(db_connection, email="owner6@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member6@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_ACTOR_NOT_HUMAN


def test_external_system_actor_is_denied(db_connection: sa.Connection) -> None:
    """Bonus (not package-mandatory, closes out all 4 actor classes):
    EXTERNAL_SYSTEM has no consequential authority merely by being
    integrated (04 §3.4)."""
    owner = _insert_user(db_connection, email="owner7@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.EXTERNAL_SYSTEM, owner),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=uuid.uuid4(),
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_ACTOR_NOT_HUMAN


def test_revoked_binding_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: revoked binding."""
    owner = _insert_user(db_connection, email="owner8@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member8@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    binding_id = _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.id == binding_id)
        .values(
            state="REVOKED", revoked_at=datetime.now(timezone.utc), revoked_by_user_id=owner.value
        )
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_wrong_scope_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong scope."""
    owner = _insert_user(db_connection, email="owner9@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member9@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    granted_scope = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=granted_scope,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=uuid.uuid4(),  # different Decision
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_WRONG_SCOPE


def test_wrong_workspace_is_denied(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong Workspace (ATK-015)."""
    owner = _insert_user(db_connection, email="owner10@test.local")
    workspace_a = _insert_workspace(db_connection, owner_id=owner)
    workspace_b = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member10@test.local")
    _insert_membership(db_connection, workspace_id=workspace_a, user_id=member)
    _insert_membership(db_connection, workspace_id=workspace_b, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_b,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    # Binding is in Workspace B; request claims Workspace A.
    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_a,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_stale_binding_denied_after_revoke_between_two_resolutions(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: stale binding (P-11 / ATK-011:
    "revoke before commit" -- 14 §16: "Commit-time resolver reloads
    current authoritative state"). Proves there is no caching: the
    exact same resolver instance flips from GRANTED to DENIED.
    """
    owner = _insert_user(db_connection, email="owner11@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member11@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    binding_id = _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolver = _resolver(db_connection)

    first = resolver.resolve(request)
    assert first.verdict == AuthorityVerdict.GRANTED

    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.id == binding_id)
        .values(
            state="REVOKED", revoked_at=datetime.now(timezone.utc), revoked_by_user_id=owner.value
        )
    )

    second = resolver.resolve(request)
    assert second.verdict == AuthorityVerdict.DENIED
    assert second.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_missing_membership_is_denied_even_with_a_real_binding_row(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: missing membership (05 AC-05-004).
    A HABB row can exist (e.g. created before membership was revoked)
    while membership is currently absent/revoked -- membership is
    checked, and fails, before the binding is even read.
    """
    owner = _insert_user(db_connection, email="owner12@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member12@test.local")
    membership_id = _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.id == membership_id)
        .values(status="REVOKED", revoked_at=datetime.now(timezone.utc))
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_ACTIVE_MEMBERSHIP


def test_ambiguous_active_bindings_are_unresolved(db_connection: sa.Connection) -> None:
    """Novel attack 1: migration 002's schema does not prevent two
    simultaneously ACTIVE bindings for the identical (workspace, human,
    class, scope) tuple. Picking either arbitrarily would be exactly
    the "inferred authority" this architecture forbids -- the resolver
    must instead fail closed as UNRESOLVED.
    """
    owner = _insert_user(db_connection, email="owner13@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member13@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.UNRESOLVED
    assert resolution.proof.reason == ResolutionReason.UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS


def test_binding_for_different_authority_class_does_not_satisfy_request(
    db_connection: sa.Connection,
) -> None:
    """Novel attack 2: an ACTIVE binding in the exact right scope but
    for a *different* authority class must not satisfy the request --
    authority classes are closed and exact (04 §9), never "close
    enough".
    """
    owner = _insert_user(db_connection, email="owner14@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member14@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=member,
        granted_by=owner,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )

    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    resolution = _resolver(db_connection).resolve(request)

    assert resolution.verdict == AuthorityVerdict.DENIED
    assert resolution.proof.reason == ResolutionReason.DENIED_NO_MATCHING_BINDING


def test_no_admin_or_role_field_exists_to_bypass_resolution() -> None:
    """Novel attack 3 (also P-24/ATK-007's structural half: "admin
    decides" has no field to even attempt through). `AuthorityRequest`
    and `ActorIdentity` cannot express a role, an "is_admin" flag, or
    any privilege shortcut -- there is no such parameter to pass.
    """
    request_fields = {f.name for f in dataclasses.fields(AuthorityRequest)}
    actor_fields = {f.name for f in dataclasses.fields(ActorIdentity)}

    assert request_fields == {
        "actor",
        "workspace_id",
        "operation",
        "required_authority_class",
        "scope_type",
        "scope_id",
    }
    assert actor_fields == {"actor_class", "user_id"}


def test_two_resolutions_never_share_mutable_state(db_connection: sa.Connection) -> None:
    """Adapted attack: one resolver instance handling two different
    actors' requests must not leak state between them (a classic
    "cached from the last call" bug class)."""
    owner = _insert_user(db_connection, email="owner15@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    granted_member = _insert_user(db_connection, email="granted15@test.local")
    ungranted_member = _insert_user(db_connection, email="ungranted15@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=granted_member)
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=ungranted_member)
    scope_id = uuid.uuid4()
    _insert_binding(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=granted_member,
        granted_by=owner,
        scope_id=scope_id,
    )

    resolver = _resolver(db_connection)
    granted_request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, granted_member),
        workspace_id=workspace_id,
        operation="RECORD_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type="DECISION",
        scope_id=scope_id,
    )
    ungranted_request = dataclasses.replace(
        granted_request, actor=ActorIdentity(ActorClass.HUMAN_USER, ungranted_member)
    )

    assert resolver.resolve(granted_request).verdict == AuthorityVerdict.GRANTED
    assert resolver.resolve(ungranted_request).verdict == AuthorityVerdict.DENIED
    # Order independence: re-running the granted request afterward must
    # still be GRANTED, proving the DENIED result above did not corrupt
    # any shared state.
    assert resolver.resolve(granted_request).verdict == AuthorityVerdict.GRANTED
