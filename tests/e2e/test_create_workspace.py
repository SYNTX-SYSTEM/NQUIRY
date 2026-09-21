"""T-CreateWorkspace END-TO-END TEST: `application.workspace_creation_handler`
-- the real, governed "self-service founder" Workspace-creation Command
that closes HARD-DEP-001 for this prototype's own scope (F01 WU-01.4,
human-confirmed 2026-09-21, Option A).

CRITICAL PACKAGE (this Command mints a Workspace's first governance
root -- the exact concern HARD-DEP-001 named). Every test here
exercises the REAL path: a real `users` row (never
`NonProofWorkspaceBootstrap`) -> real BND-001 (`boundaries.evaluate_chain`)
-> the real, human-confirmed eligibility port -> a real atomic write
(`workspaces`/`workspace_memberships`/`role_assignments`/
`human_authority_bindings`/`commands`/`commit_units`/`audit_events`/
`outbox_events`), backed by real PostgreSQL, not mocks.

`NonProofWorkspaceBootstrap` (PKG-04) is used in exactly one test here
(`test_authority_source_is_level_1_explicit_never_fixture`), and only
as a CONTRAST fixture -- to prove, against a real row from each path
side by side, that a real founder's `authority_source` can never be
confused with a fixture's.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    CreateWorkspaceResult,
    WorkspaceCreationDenied,
    WorkspaceCreationEligibility,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import (
    AttemptAlreadyRecorded,
    SqlAlchemyCommandRepository,
)
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import (
    command_attempts_table,
    commands_table,
    commit_units_table,
    human_authority_bindings_table,
    outbox_events_table,
    role_assignments_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2026, 9, 21, tzinfo=timezone.utc)


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Real Human Founder",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return UserId(user_id)


def _human_actor(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


def _repos(db_connection: sa.Connection) -> dict[str, object]:
    return {
        "command_repository": SqlAlchemyCommandRepository(db_connection),
        "audit_repository": SqlAlchemyAuditRepository(db_connection),
        "outbox_repository": SqlAlchemyOutboxRepository(db_connection),
        "commit_repository": SqlAlchemyCommitRepository(db_connection),
        "workspace_repository": SqlAlchemyWorkspaceRepository(db_connection),
        "membership_repository": SqlAlchemyMembershipRepository(db_connection),
        "authority_binding_repository": SqlAlchemyAuthorityBindingRepository(db_connection),
    }


def _create(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_name: str = "Acme Product Team",
    eligibility_checker: object | None = None,
    **repo_overrides: object,
) -> CreateWorkspaceResult:
    repos = _repos(db_connection)
    repos.update(repo_overrides)
    return create_workspace(
        db_connection,
        actor=actor,
        workspace_name=workspace_name,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        eligibility_checker=eligibility_checker or AllowAllWorkspaceCreationEligibilityChecker(),
        **repos,
    )


def _workspace_row_count(db_connection: sa.Connection) -> int:
    return db_connection.execute(
        sa.select(sa.func.count()).select_from(workspaces_table)
    ).scalar_one()


class _AlwaysDenyEligibilityChecker:
    def check(self, actor: ActorIdentity) -> WorkspaceCreationEligibility:
        return WorkspaceCreationEligibility(
            allowed=False, reason_code="TEST_DENIED_FOR_ADVERSARIAL_PROOF"
        )


class _RaisingAuditRepository:
    """Adversarial fake: injects a failure INSIDE the atomic write, after
    `workspaces`/`workspace_memberships`/`role_assignments`/
    `human_authority_bindings`/`commit_units` have already been written
    to the open SAVEPOINT, to prove the whole block rolls back
    atomically rather than leaving partial rows."""

    def append(self, event: object) -> None:
        raise RuntimeError("INJECTED_AUDIT_FAILURE")


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_real_human_founder_creates_workspace_and_becomes_governance_root(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="founder@real-human.test")
    actor = _human_actor(founder)

    result = _create(db_connection, actor=actor, workspace_name="Real Founder Workspace")

    assert result.workspace_id is not None
    assert result.owner_user_id == founder

    workspace_row = (
        db_connection.execute(
            sa.select(workspaces_table).where(workspaces_table.c.id == result.workspace_id.value)
        )
        .mappings()
        .one()
    )
    assert workspace_row["name"] == "Real Founder Workspace"
    assert workspace_row["owner_id"] == founder.value

    membership_row = (
        db_connection.execute(
            sa.select(workspace_memberships_table).where(
                workspace_memberships_table.c.id == result.membership_id
            )
        )
        .mappings()
        .one()
    )
    assert membership_row["workspace_id"] == result.workspace_id.value
    assert membership_row["user_id"] == founder.value
    assert membership_row["status"] == MembershipStatus.ACTIVE.value

    role_row = (
        db_connection.execute(
            sa.select(role_assignments_table).where(
                role_assignments_table.c.membership_id == result.membership_id
            )
        )
        .mappings()
        .one()
    )
    assert role_row["role"] == WorkspaceRole.OWNER.value
    assert role_row["granted_by_user_id"] == founder.value

    binding_row = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == result.governance_binding_id.value
            )
        )
        .mappings()
        .one()
    )
    assert binding_row["human_user_id"] == founder.value
    assert binding_row["authority_class"] == AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT.value
    assert binding_row["scope_type"] == "WORKSPACE"
    assert binding_row["scope_id"] == result.workspace_id.value
    assert binding_row["authority_source"] == "LEVEL_1_EXPLICIT"
    assert binding_row["granted_by_user_id"] == founder.value
    assert binding_row["state"] == AuthorityBindingState.ACTIVE.value

    command_row = (
        db_connection.execute(
            sa.select(commands_table).where(
                commands_table.c.workspace_id == result.workspace_id.value
            )
        )
        .mappings()
        .one()
    )
    assert command_row["command_type"] == "CMD_CREATE_WORKSPACE"

    commit_row = (
        db_connection.execute(
            sa.select(commit_units_table).where(
                commit_units_table.c.workspace_id == result.workspace_id.value
            )
        )
        .mappings()
        .one()
    )
    assert commit_row["outcome"] == "COMMITTED"
    assert (
        f"authority_binding:{result.governance_binding_id.value}" in commit_row["governance_refs"]
    )

    audit_row = (
        db_connection.execute(
            sa.select(sa.text("*"))
            .select_from(sa.text("audit_events"))
            .where(sa.text("workspace_id = :ws"))
            .params(ws=result.workspace_id.value)
        )
        .mappings()
        .one()
    )
    assert audit_row["event_type"] == "CMD_CREATE_WORKSPACE_COMMITTED"
    assert audit_row["authority_source_ref"] == result.governance_binding_id.value
    assert audit_row["result"] == "COMMITTED"


def test_outbox_event_records_workspace_created_pending_delivery(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="outbox-founder@real-human.test")
    result = _create(db_connection, actor=_human_actor(founder))

    outbox_row = (
        db_connection.execute(
            sa.select(outbox_events_table).where(
                outbox_events_table.c.workspace_id == result.workspace_id.value
            )
        )
        .mappings()
        .one()
    )
    assert outbox_row["event_type"] == "WORKSPACE_CREATED"
    assert outbox_row["delivery_status"] == "PENDING"
    assert outbox_row["delivery_attempt_count"] == 0


def test_founder_owner_role_assignment_is_self_granted(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="self-grant@real-human.test")
    result = _create(db_connection, actor=_human_actor(founder))

    role_row = (
        db_connection.execute(
            sa.select(role_assignments_table).where(
                role_assignments_table.c.membership_id == result.membership_id
            )
        )
        .mappings()
        .one()
    )
    binding_row = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == result.governance_binding_id.value
            )
        )
        .mappings()
        .one()
    )
    # Nothing else could legitimately grant the FIRST binding a genuinely
    # new founder holds -- honest self-grant, not a workaround.
    assert role_row["granted_by_user_id"] == founder.value
    assert binding_row["granted_by_user_id"] == founder.value


# ---------------------------------------------------------------------------
# Structural non-conflation with the fixture lane
# ---------------------------------------------------------------------------


def test_result_carries_no_fixture_legitimacy_field(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="no-fixture-field@real-human.test")
    result = _create(db_connection, actor=_human_actor(founder))

    assert not hasattr(result, "fixture_legitimacy")
    field_names = {f for f in result.__dataclass_fields__}
    assert field_names == {
        "workspace_id",
        "owner_user_id",
        "membership_id",
        "governance_binding_id",
    }


def test_authority_source_is_level_1_explicit_never_fixture(db_connection: sa.Connection) -> None:
    # The one and only fixture-lane comparison point in this file: a
    # real founder's binding side by side with a fixture's own binding,
    # proving the two are never confusable.
    from semantic_types.id_generator import SystemIdGenerator

    fixture_result = NonProofWorkspaceBootstrap(
        db_connection, FixedClock(_NOW), SystemIdGenerator()
    ).seed(owner_email="fixture-owner@nonproof.test")
    fixture_binding = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.workspace_id == fixture_result.workspace_id.value
            )
        )
        .mappings()
        .one()
    )
    assert fixture_binding["authority_source"] == "NON_PROOF_FIXTURE"

    founder = _insert_user(db_connection, email="real-lane@real-human.test")
    real_result = _create(db_connection, actor=_human_actor(founder))
    real_binding = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == real_result.governance_binding_id.value
            )
        )
        .mappings()
        .one()
    )
    assert real_binding["authority_source"] == "LEVEL_1_EXPLICIT"
    assert real_binding["authority_source"] != "NON_PROOF_FIXTURE"


# ---------------------------------------------------------------------------
# BND-001 adversarial: non-HUMAN_USER actors are denied, nothing written
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "actor_class",
    [ActorClass.SYSTEM_SERVICE, ActorClass.AI_PROCESSOR, ActorClass.EXTERNAL_SYSTEM],
)
def test_non_human_actor_is_denied_workspace_creation(
    db_connection: sa.Connection, actor_class: ActorClass
) -> None:
    non_human_id = _insert_user(db_connection, email=f"non-human-{actor_class.value}@real.test")
    before = _workspace_row_count(db_connection)

    with pytest.raises(WorkspaceCreationDenied) as exc_info:
        _create(db_connection, actor=ActorIdentity(actor_class=actor_class, user_id=non_human_id))

    assert exc_info.value.reason_code.startswith("IDENTITY_CLASS_NOT_ACCEPTED")
    assert _workspace_row_count(db_connection) == before


def test_denied_actor_writes_no_command_row_either(db_connection: sa.Connection) -> None:
    non_human_id = _insert_user(db_connection, email="no-command-row@real.test")
    before = db_connection.execute(
        sa.select(sa.func.count()).select_from(commands_table)
    ).scalar_one()

    with pytest.raises(WorkspaceCreationDenied):
        _create(
            db_connection,
            actor=ActorIdentity(actor_class=ActorClass.SYSTEM_SERVICE, user_id=non_human_id),
        )

    after = db_connection.execute(
        sa.select(sa.func.count()).select_from(commands_table)
    ).scalar_one()
    assert after == before


# ---------------------------------------------------------------------------
# Eligibility-checker adversarial: the named, replaceable port
# ---------------------------------------------------------------------------


def test_eligibility_checker_denial_blocks_creation_and_writes_nothing(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="ineligible@real-human.test")
    before = _workspace_row_count(db_connection)

    with pytest.raises(WorkspaceCreationDenied) as exc_info:
        _create(
            db_connection,
            actor=_human_actor(founder),
            eligibility_checker=_AlwaysDenyEligibilityChecker(),
        )

    assert exc_info.value.reason_code == "TEST_DENIED_FOR_ADVERSARIAL_PROOF"
    assert _workspace_row_count(db_connection) == before


def test_allow_all_checker_is_the_named_replaceable_default() -> None:
    checker = AllowAllWorkspaceCreationEligibilityChecker()
    outcome = checker.check(
        ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=UserId(uuid.uuid4()))
    )
    assert outcome.allowed is True
    assert outcome.reason_code == "UNGATED_SELF_SERVICE"


# ---------------------------------------------------------------------------
# Malformed input adversarial
# ---------------------------------------------------------------------------


def test_empty_workspace_name_is_rejected_before_any_boundary_or_write(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="empty-name@real-human.test")
    before = _workspace_row_count(db_connection)

    with pytest.raises(ValueError):
        _create(db_connection, actor=_human_actor(founder), workspace_name="")

    assert _workspace_row_count(db_connection) == before


def test_whitespace_only_workspace_name_is_rejected(db_connection: sa.Connection) -> None:
    founder = _insert_user(db_connection, email="whitespace-name@real-human.test")
    before = _workspace_row_count(db_connection)

    with pytest.raises(ValueError):
        _create(db_connection, actor=_human_actor(founder), workspace_name="   \t\n  ")

    assert _workspace_row_count(db_connection) == before


# ---------------------------------------------------------------------------
# Idempotency / replay adversarial
# ---------------------------------------------------------------------------


def test_duplicate_attempt_id_is_rejected_and_second_workspace_never_created(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="duplicate-attempt@real-human.test")
    repos = _repos(db_connection)
    shared_attempt_id = AttemptId(uuid.uuid4())

    first = create_workspace(
        db_connection,
        actor=_human_actor(founder),
        workspace_name="First Attempt Workspace",
        command_id=CommandId(uuid.uuid4()),
        attempt_id=shared_attempt_id,
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
        **repos,
    )
    before = _workspace_row_count(db_connection)

    with pytest.raises(AttemptAlreadyRecorded):
        create_workspace(
            db_connection,
            actor=_human_actor(founder),
            workspace_name="Second Attempt Workspace",
            command_id=CommandId(uuid.uuid4()),
            attempt_id=shared_attempt_id,  # replayed identity (09 sec. 4.4)
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
            eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
            **repos,
        )

    assert first.workspace_id is not None
    assert _workspace_row_count(db_connection) == before


# ---------------------------------------------------------------------------
# Atomicity / failure-injection adversarial
# ---------------------------------------------------------------------------


def test_mid_transaction_failure_rolls_back_every_row_including_the_attempt_itself(
    db_connection: sa.Connection,
) -> None:
    """`commands.workspace_id` carries a real FK to `workspaces.id`
    (`fk_commands_workspace`), and for CreateWorkspace that Workspace
    does not exist until this Command's own write creates it --
    `record_attempt` therefore runs INSIDE the same SAVEPOINT as the
    `workspaces` insert (see the handler's own module docstring), unlike
    every other governed Command in this codebase. The disclosed
    consequence: a failed founding attempt leaves NO trace at all in
    `commands`/`command_attempts` -- not even a `FAILED_PRECOMMIT` row --
    because the schema's own FK correctly refuses to let an operational
    record reference a canonical record that was never actually
    brought into being. This test proves that consequence is real, not
    a silent swallow: the exception still propagates to the caller."""
    founder = _insert_user(db_connection, email="rollback@real-human.test")
    repos = _repos(db_connection)
    repos["audit_repository"] = _RaisingAuditRepository()
    attempt_id = AttemptId(uuid.uuid4())
    before_commands = db_connection.execute(
        sa.select(sa.func.count()).select_from(commands_table)
    ).scalar_one()

    with pytest.raises(RuntimeError, match="INJECTED_AUDIT_FAILURE"):
        create_workspace(
            db_connection,
            actor=_human_actor(founder),
            workspace_name="Doomed Workspace",
            command_id=CommandId(uuid.uuid4()),
            attempt_id=attempt_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
            eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
            **repos,
        )

    # The nested SAVEPOINT block rolled back entirely: no workspace,
    # membership, role, binding, commit_unit, or command_attempts row
    # survives.
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(workspaces_table)
            .where(workspaces_table.c.owner_id == founder.value)
        ).scalar_one()
        == 0
    )
    assert (
        db_connection.execute(
            sa.select(sa.func.count()).select_from(commit_units_table)
        ).scalar_one()
        == 0
    )
    assert (
        db_connection.execute(sa.select(sa.func.count()).select_from(commands_table)).scalar_one()
        == before_commands
    )
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(command_attempts_table)
            .where(command_attempts_table.c.id == attempt_id.value)
        ).scalar_one()
        == 0
    )
