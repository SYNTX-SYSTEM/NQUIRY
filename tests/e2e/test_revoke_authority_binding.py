"""T-RevokeAuthorityBinding END-TO-END TEST:
`application.authority_binding_handler` (F01 WU-01.6) -- the real,
governed "Workspace governance root revokes a HumanAuthorityBinding"
Command, against real PostgreSQL.

Every Workspace here is founded through the real
`application.workspace_creation_handler.create_workspace` Command (F01
WU-01.4b); every authority check runs through the real
`authority.resolver.AuthorityResolver` and the real BND-001..005
evaluators (PKG-09), then the real `commit.coordinator.CommitCoordinator`
-- no mocks anywhere in the precommit or commit path. Written FIRST,
before `application.authority_binding_handler`/the `revoke()` half of
`persistence.authority_binding_repository` exist -- this file is
expected to fail on import until both are implemented (TDD RED).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.authority_binding_handler import (
    AuthorityBindingNotFound,
    GovernanceRootOrphaningRefused,
    RevokeAuthorityBindingDenied,
    revoke_human_authority_binding,
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
from persistence.authority_binding_repository import (
    SqlAlchemyAuthorityBindingRepository,
    SqlAlchemyAuthorityBindingVersionReader,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import commands_table, human_authority_bindings_table, users_table
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import (
    AttemptId,
    AuthorityBindingId,
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 21, tzinfo=timezone.utc)


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


def _governance_binding_id(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> AuthorityBindingId:
    """The real founder self-grant `create_workspace` already wrote --
    never inserted directly, always read back."""
    row = (
        db_connection.execute(
            sa.select(human_authority_bindings_table.c.id).where(
                human_authority_bindings_table.c.workspace_id == workspace_id.value,
                human_authority_bindings_table.c.authority_class
                == AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT.value,
            )
        )
        .mappings()
        .one()
    )
    return AuthorityBindingId(row["id"])


def _add_member(
    db_connection: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole = WorkspaceRole.CONTRIBUTOR,
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


def _grant_directly(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    human_user_id: UserId,
    granted_by_user_id: UserId,
    authority_class: AuthorityClass = AuthorityClass.DECISION_RIGHT,
    state: AuthorityBindingState = AuthorityBindingState.ACTIVE,
) -> AuthorityBindingId:
    """No real Command grants a non-`WORKSPACE_GOVERNANCE_RIGHT` binding
    yet (WU-01.6's own scope is revoke only, mirroring how WU-01.5 used
    direct inserts for prerequisite state no Command yet produces) --
    disclosed, not hidden; matches this repository's own established
    `NonProofWorkspaceBootstrap`-adjacent convention of direct fixture
    inserts where no legitimate Command exists yet to call instead.

    The real `trg_habb_check_grant_preconditions` trigger (05 GOV-005)
    requires `human_user_id` to already hold an ACTIVE
    `workspace_membership` in `workspace_id` -- this helper makes that
    real via the real `AddMember` Command first (never a direct insert
    into `workspace_memberships`), then inserts the binding directly
    (the one row no real Command yet grants).
    """
    _add_member(
        db_connection,
        owner=granted_by_user_id,
        workspace_id=workspace_id,
        new_member_user_id=human_user_id,
    )
    binding_id = uuid.uuid4()
    already_revoked = state is AuthorityBindingState.REVOKED
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=human_user_id.value,
            authority_class=authority_class.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=granted_by_user_id.value,
            granted_at=_NOW,
            # `ck_habb_revoked_consistency` requires both set together
            # with `state=REVOKED`, and both NULL otherwise.
            revoked_by_user_id=granted_by_user_id.value if already_revoked else None,
            revoked_at=_NOW if already_revoked else None,
            state=state.value,
            record_version=1,
        )
    )
    return AuthorityBindingId(binding_id)


def _revoke(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    binding_id: AuthorityBindingId,
    idempotency_key: str | None = None,
):
    return revoke_human_authority_binding(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        binding_id=binding_id,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=idempotency_key,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyAuthorityBindingVersionReader(db_connection),
    )


def _binding_row(db_connection: sa.Connection, binding_id: AuthorityBindingId) -> sa.RowMapping:
    return (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == binding_id.value
            )
        )
        .mappings()
        .one()
    )


def _commands_count(db_connection: sa.Connection, *, workspace_id: WorkspaceId) -> int:
    return db_connection.execute(
        sa.select(sa.func.count())
        .select_from(commands_table)
        .where(commands_table.c.workspace_id == workspace_id.value)
    ).scalar_one()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_owner_revokes_a_real_granted_binding(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-revoke-happy@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Revoke Happy Path")
    holder = _insert_user(db_connection, email="holder-revoke-happy@real-human.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )

    commit_unit = _revoke(
        db_connection, actor=_human_actor(owner), workspace_id=workspace_id, binding_id=binding_id
    )

    assert commit_unit.outcome.value == "COMMITTED"
    row = _binding_row(db_connection, binding_id)
    assert row["state"] == AuthorityBindingState.REVOKED.value
    assert row["revoked_by_user_id"] == owner.value
    assert row["revoked_at"] == _NOW
    assert row["record_version"] == 2


def test_revoking_a_binding_removes_it_from_the_holders_effective_authority(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-revoke-effective@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Revoke Effective")
    holder = _insert_user(db_connection, email="holder-revoke-effective@real-human.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )

    _revoke(
        db_connection, actor=_human_actor(owner), workspace_id=workspace_id, binding_id=binding_id
    )

    current = SqlAlchemyAuthorityBindingRepository(db_connection).list_current_bindings(
        workspace_id, holder
    )
    assert current == ()


# ---------------------------------------------------------------------------
# Adversarial: governance-root orphaning refused (GAP-05-001, [UNDERDEFINED])
# ---------------------------------------------------------------------------


def test_revoking_the_workspaces_own_governance_right_binding_is_refused(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-orphan-self@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="No Self-Orphaning")
    binding_id = _governance_binding_id(db_connection, workspace_id=workspace_id)

    with pytest.raises(GovernanceRootOrphaningRefused):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )

    row = _binding_row(db_connection, binding_id)
    assert row["state"] == AuthorityBindingState.ACTIVE.value
    assert (
        _commands_count(db_connection, workspace_id=workspace_id) == 1
    )  # only CreateWorkspace's own


# ---------------------------------------------------------------------------
# Adversarial: authority
# ---------------------------------------------------------------------------


def test_non_owner_member_cannot_revoke_another_members_binding(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-contributor-revoke-attack@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Contributor Revoke Attack")
    contributor = _insert_user(db_connection, email="mere-contributor-revoke@real-human.test")
    _add_member(
        db_connection, owner=owner, workspace_id=workspace_id, new_member_user_id=contributor
    )
    holder = _insert_user(db_connection, email="holder-contributor-attack@real-human.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )

    with pytest.raises(RevokeAuthorityBindingDenied):
        _revoke(
            db_connection,
            actor=_human_actor(contributor),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )

    row = _binding_row(db_connection, binding_id)
    assert row["state"] == AuthorityBindingState.ACTIVE.value


def test_non_member_actor_cannot_revoke_in_a_workspace_they_do_not_belong_to(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-stranger-revoke@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Not Yours To Revoke")
    holder = _insert_user(db_connection, email="holder-stranger-revoke@real-human.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )
    stranger = _insert_user(db_connection, email="stranger-revoke@real-human.test")

    with pytest.raises(RevokeAuthorityBindingDenied):
        _revoke(
            db_connection,
            actor=_human_actor(stranger),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )

    row = _binding_row(db_connection, binding_id)
    assert row["state"] == AuthorityBindingState.ACTIVE.value


def test_non_existent_workspace_denies(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-revoke-nonexistent-ws@real-human.test")

    with pytest.raises(RevokeAuthorityBindingDenied):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=WorkspaceId(uuid.uuid4()),
            binding_id=AuthorityBindingId(uuid.uuid4()),
        )


@pytest.mark.parametrize(
    "actor_class", [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM]
)
def test_non_human_actor_is_denied(db_connection: sa.Connection, actor_class: ActorClass) -> None:
    owner = _insert_user(
        db_connection, email=f"owner-revoke-non-human-{actor_class.value}@real.test"
    )
    workspace_id = _found_workspace(db_connection, owner=owner, name="Non-Human Revoke Attack")
    holder = _insert_user(db_connection, email=f"holder-non-human-{actor_class.value}@real.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )

    with pytest.raises(RevokeAuthorityBindingDenied):
        _revoke(
            db_connection,
            actor=ActorIdentity(actor_class=actor_class, user_id=owner),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )

    row = _binding_row(db_connection, binding_id)
    assert row["state"] == AuthorityBindingState.ACTIVE.value


# ---------------------------------------------------------------------------
# Adversarial: the binding itself does not (legitimately) exist
# ---------------------------------------------------------------------------


def test_non_existent_binding_id_is_denied(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email="owner-revoke-nonexistent-binding@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Nonexistent Binding Target")

    with pytest.raises(AuthorityBindingNotFound):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            binding_id=AuthorityBindingId(uuid.uuid4()),
        )


def test_binding_from_a_different_workspace_is_denied_not_revoked(
    db_connection: sa.Connection,
) -> None:
    owner_a = _insert_user(db_connection, email="owner-a-cross-ws@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=owner_a, name="Workspace A")
    holder_a = _insert_user(db_connection, email="holder-a-cross-ws@real-human.test")
    binding_a = _grant_directly(
        db_connection, workspace_id=workspace_a, human_user_id=holder_a, granted_by_user_id=owner_a
    )

    owner_b = _insert_user(db_connection, email="owner-b-cross-ws@real-human.test")
    workspace_b = _found_workspace(db_connection, owner=owner_b, name="Workspace B")

    with pytest.raises(AuthorityBindingNotFound):
        _revoke(
            db_connection,
            actor=_human_actor(owner_b),
            workspace_id=workspace_b,
            binding_id=binding_a,
        )

    row = _binding_row(db_connection, binding_a)
    assert row["state"] == AuthorityBindingState.ACTIVE.value


# ---------------------------------------------------------------------------
# Adversarial: real database/version conflict
# ---------------------------------------------------------------------------


def test_revoking_an_already_revoked_binding_fails_as_a_stale_conflict(
    db_connection: sa.Connection,
) -> None:
    owner = _insert_user(db_connection, email="owner-double-revoke@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Double Revoke Target")
    holder = _insert_user(db_connection, email="holder-double-revoke@real-human.test")
    binding_id = _grant_directly(
        db_connection, workspace_id=workspace_id, human_user_id=holder, granted_by_user_id=owner
    )
    _revoke(
        db_connection, actor=_human_actor(owner), workspace_id=workspace_id, binding_id=binding_id
    )

    with pytest.raises(CommitFailedPrecommit):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )


def test_revoking_an_already_revoked_fixture_binding_fails_the_same_way(
    db_connection: sa.Connection,
) -> None:
    """Same conflict, reached without ever calling `revoke()` twice --
    proves the guard is the real stored `state`, not merely "did this
    process already revoke it once"."""
    owner = _insert_user(db_connection, email="owner-pre-revoked@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=owner, name="Pre-Revoked Target")
    holder = _insert_user(db_connection, email="holder-pre-revoked@real-human.test")
    binding_id = _grant_directly(
        db_connection,
        workspace_id=workspace_id,
        human_user_id=holder,
        granted_by_user_id=owner,
        state=AuthorityBindingState.REVOKED,
    )

    with pytest.raises(CommitFailedPrecommit):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=workspace_id,
            binding_id=binding_id,
        )
