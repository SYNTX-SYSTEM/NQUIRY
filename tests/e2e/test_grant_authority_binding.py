"""T-GrantAuthorityBinding END-TO-END TEST:
`application.authority_binding_handler.grant_human_authority_binding`
(F02 WU-02.0 -- a prerequisite F02 discovered, not a domain concept F02
itself owns: `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md`'s own
COMMAND REGISTRY names `GrantHumanAuthorityBinding` as a real Command
(`WORKSPACE_GOVERNANCE_RIGHT`-gated, "new HABB"), and F01's own WU-01.6
only ever built the REVOKE half of GAP-04-014 (`AuthorityBindingRepository.grant()`'s
own docstring: "F01 WU-01.4, human-confirmed... `create_workspace` is
this Command's own scope... revocation remains a later Field's scope
(F01 WU-01.6)" -- silent about a GENERIC grant path for any OTHER
authority class). `AUTH-DEP-SESS-001` (04) requires a real, granted
`SESSION_CONTROL_RIGHT` HumanAuthorityBinding before `CreateSession`
(F02's own next Work Unit) is reachable by any real actor -- this file
proves the missing grant mechanism first, human-confirmed necessary
before proceeding, 2026-09-22), against real PostgreSQL, no mocks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.authority_binding_handler import (
    GovernanceRightNotGrantableViaGenericGrant,
    GrantAuthorityBindingDenied,
    grant_human_authority_binding,
)
from application.membership_operations_handler import add_member
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.coordinator import CommitFailedPrecommit
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import challenges_table, human_authority_bindings_table, users_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Real Human",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return UserId(user_id)


def _human_actor(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


def _resolver(db_connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )


def _found_workspace(db_connection: sa.Connection, *, owner: UserId, name: str) -> WorkspaceId:
    result = create_workspace(
        db_connection,
        actor=_human_actor(owner),
        workspace_name=name,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
    )
    return result.workspace_id


def _add_member(
    db_connection: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole = WorkspaceRole.FACILITATOR,
) -> None:
    add_member(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        new_member_user_id=new_member_user_id,
        role=role,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyWorkspaceVersionReader(
            db_connection, workspace_id=workspace_id
        ),
    )


def _real_challenge(db_connection: sa.Connection, workspace_id: WorkspaceId) -> uuid.UUID:
    """F02 WU-02.7: a grant's scope must name a real record of the same
    Workspace. Test precondition only (this suite tests grants, not
    Challenge creation, which has its own governed Command and tests).
    For a nonexistent Workspace no row can exist; the grant is denied
    before its scope is examined, so a bare id is returned."""
    challenge_id = uuid.uuid4()
    if SqlAlchemyWorkspaceRepository(db_connection).get(workspace_id) is None:
        return challenge_id
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id,
            workspace_id=workspace_id.value,
            title="Grant scope challenge",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    return challenge_id


def _grant(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    authority_class: AuthorityClass = AuthorityClass.SESSION_CONTROL_RIGHT,
    scope_type: str = "CHALLENGE",
    scope_id: uuid.UUID | None = None,
):
    return grant_human_authority_binding(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        human_user_id=human_user_id,
        authority_class=authority_class,
        scope_type=scope_type,
        scope_id=scope_id if scope_id is not None else _real_challenge(db_connection, workspace_id),
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyWorkspaceVersionReader(
            db_connection, workspace_id=workspace_id
        ),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_owner_grants_session_control_right_to_a_real_member(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-happy@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Grant Happy Path")
    holder = _insert_user(db_connection, email="holder-grant-happy@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=holder)
    challenge_id = _real_challenge(db_connection, workspace_id)

    commit_unit = _grant(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=holder,
        scope_id=challenge_id,
    )

    assert commit_unit.outcome.value == "COMMITTED"
    row = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.human_user_id == holder.value,
                human_authority_bindings_table.c.authority_class
                == AuthorityClass.SESSION_CONTROL_RIGHT.value,
            )
        )
        .mappings()
        .one()
    )
    assert row["state"] == AuthorityBindingState.ACTIVE.value
    assert row["scope_type"] == "CHALLENGE"
    assert row["scope_id"] == challenge_id
    assert row["granted_by_user_id"] == owner.value
    assert row["authority_source"] == "LEVEL_1_EXPLICIT"


def test_granted_binding_is_immediately_effective_via_the_real_resolver(
    db_connection: sa.Connection,
) -> None:
    from authority.resolver import AuthorityRequest, AuthorityVerdict

    owner = _insert_user(db_connection, email="owner-grant-effective@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Grant Effective")
    holder = _insert_user(db_connection, email="holder-grant-effective@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=holder)
    challenge_id = _real_challenge(db_connection, workspace_id)
    _grant(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=holder,
        scope_id=challenge_id,
    )

    resolution = _resolver(db_connection).resolve(
        AuthorityRequest(
            actor=_human_actor(holder),
            workspace_id=workspace_id,
            operation="CreateSession",
            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
            scope_type="CHALLENGE",
            scope_id=challenge_id,
        )
    )
    assert resolution.verdict is AuthorityVerdict.GRANTED


# ---------------------------------------------------------------------------
# Adversarial: WORKSPACE_GOVERNANCE_RIGHT refused via this generic path
# ---------------------------------------------------------------------------


def test_granting_workspace_governance_right_is_refused(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-governance-refused@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="No Second Governance Grant")
    holder = _insert_user(db_connection, email="holder-grant-governance-refused@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=holder)

    with pytest.raises(GovernanceRightNotGrantableViaGenericGrant):
        _grant(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            human_user_id=holder,
            authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(human_authority_bindings_table)
        .where(
            human_authority_bindings_table.c.human_user_id == holder.value,
            human_authority_bindings_table.c.authority_class
            == AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT.value,
        )
    ).scalar_one()
    assert count == 0


# ---------------------------------------------------------------------------
# Adversarial: authority
# ---------------------------------------------------------------------------


def test_non_owner_member_cannot_grant(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-nonowner@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Owner Grant Attack")
    contributor = _insert_user(db_connection, email="contributor-grant-nonowner@real-human.test")
    _add_member(
        db_connection,
        owner=owner,
        workspace_id=workspace_id,
        new_member_user_id=contributor,
        role=WorkspaceRole.CONTRIBUTOR,
    )
    victim = _insert_user(db_connection, email="victim-grant-nonowner@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=victim)

    with pytest.raises(GrantAuthorityBindingDenied):
        _grant(
            db_connection,
            actor=_human_actor(contributor),
            workspace_id=workspace_id,
            human_user_id=victim,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(human_authority_bindings_table)
        .where(
            human_authority_bindings_table.c.human_user_id == victim.value,
            human_authority_bindings_table.c.authority_class
            == AuthorityClass.SESSION_CONTROL_RIGHT.value,
        )
    ).scalar_one()
    assert count == 0


def test_non_member_actor_cannot_grant(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-stranger@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Stranger Grant Attack")
    stranger = _insert_user(db_connection, email="stranger-grant@real-human.test")
    target = _insert_user(db_connection, email="target-stranger-grant@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=target)

    with pytest.raises(GrantAuthorityBindingDenied):
        _grant(
            db_connection,
            actor=_human_actor(stranger),
            workspace_id=workspace_id,
            human_user_id=target,
        )


def test_non_existent_workspace_denies(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-nonexistent-ws@real-human.test")
    target = _insert_user(db_connection, email="target-grant-nonexistent-ws@real-human.test")

    with pytest.raises(GrantAuthorityBindingDenied):
        _grant(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=WorkspaceId(uuid.uuid4()),
            human_user_id=target,
        )


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(
        db_connection, email=f"owner-grant-non-human-{actor_class.value}@real.test"
    )
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Grant Attack")
    target = _insert_user(db_connection, email=f"target-non-human-{actor_class.value}@real.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=target)

    with pytest.raises(GrantAuthorityBindingDenied):
        _grant(
            db_connection,
            actor=ActorIdentity(actor_class=actor_class, user_id=owner),
            workspace_id=workspace_id,
            human_user_id=target,
        )


# ---------------------------------------------------------------------------
# Adversarial: real DB constraints (GOV-005 grant precondition)
# ---------------------------------------------------------------------------


def test_granting_to_a_non_member_fails_at_the_database_layer(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-grant-nonmember-target@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Nonmember Target Grant")
    non_member = _insert_user(db_connection, email="nonmember-grant-target@real-human.test")

    with pytest.raises(CommitFailedPrecommit):
        _grant(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            human_user_id=non_member,
        )


def test_granting_the_same_class_and_scope_twice_creates_two_independent_bindings(
    db_connection: sa.Connection,
) -> None:
    """No uniqueness constraint spans (authority_class, scope) -- a
    real, disclosed data-integrity property `authority.resolver`'s own
    module docstring already names (`UNRESOLVED_AMBIGUOUS_ACTIVE_BINDINGS`).
    This Command does not invent a new uniqueness rule; both real rows
    are written, exactly as `grant()` itself does."""
    owner = _insert_user(db_connection, email="owner-grant-twice@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Grant Twice")
    holder = _insert_user(db_connection, email="holder-grant-twice@real-human.test")
    _add_member(db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=holder)
    challenge_id = _real_challenge(db_connection, workspace_id)

    _grant(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=holder,
        scope_id=challenge_id,
    )
    _grant(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=workspace_id,
        human_user_id=holder,
        scope_id=challenge_id,
    )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(human_authority_bindings_table)
        .where(
            human_authority_bindings_table.c.human_user_id == holder.value,
            human_authority_bindings_table.c.authority_class
            == AuthorityClass.SESSION_CONTROL_RIGHT.value,
        )
    ).scalar_one()
    assert count == 2


# --- F02 WU-02.7: grant scope must name a record of the same Workspace ---


def test_grant_for_a_foreign_or_missing_session_scope_is_rejected(
    db_connection: sa.Connection,
) -> None:
    import f02_support as f02
    from application.authority_binding_handler import GrantScopeInvalid

    ctx = f02.inquiry_context(db_connection)
    other_owner = f02.insert_user(db_connection, "other")
    other_ws = f02.found_workspace(db_connection, owner=other_owner, name="Other").workspace_id
    for scope_type, scope_id, workspace, owner in (
        ("SESSION", uuid.uuid4(), ctx["ws"], ctx["owner"]),
        ("SESSION", ctx["session"].value, other_ws, other_owner),
        ("CHALLENGE", ctx["challenge"].challenge_id.value, other_ws, other_owner),
        ("WORKSPACE", ctx["ws"].value, other_ws, other_owner),
        ("NOT_A_SCOPE", uuid.uuid4(), ctx["ws"], ctx["owner"]),
    ):
        with pytest.raises(GrantScopeInvalid):
            f02.grant(
                db_connection,
                owner=owner,
                workspace_id=workspace,
                member=owner,
                authority_class="SESSION_CONTROL_RIGHT",
                scope_type=scope_type,
                scope_id=scope_id,
            )
