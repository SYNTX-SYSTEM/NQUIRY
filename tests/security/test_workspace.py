"""T9 SECURITY / ISOLATION TEST: PostgreSQL RLS defense-in-depth,
against real PostgreSQL with `047bdf9bc528_rls_and_security_events.py`
applied.

14 section 46's own repository-topology row assigns
`tests/security/test_workspace.py` to `packages/security/workspace.py`.
This file proves the DB-POLICY layer specifically -- repository/
Command/Evidence/AI-context/projection-layer Workspace isolation is
already proven by every prior package's own tests (PKG-01/09/10/16/17/
19/21) and re-exercised, unmodified, by this package's own
RECURSIVE_REGRESSION full-suite run.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.recovery_repository import SqlAlchemyRecoveryRepository
from persistence.workspace_rls_context import SqlAlchemyWorkspaceContext
from recovery.certainty import ConsequenceCertainty
from recovery.failure_classifier import FailureClass
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord
from security.workspace import WorkspaceContextPort
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    RecoveryId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def _record_real_command_and_commit(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> tuple[CommandId, AttemptId, CommitId]:
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    SqlAlchemyCommandRepository(db_connection).record_attempt(
        CommandEnvelope(
            command_id=command_id,
            command_type="CMD_TEST_OPERATION",
            command_contract_version=ContractVersion("1.0"),
            attempt_id=attempt_id,
            correlation_id=CorrelationId(uuid.uuid4()),
            requested_at=_NOW,
            requesting_actor_type="HUMAN_USER",
            requesting_actor_id="user-ref-1",
            workspace_scope_ref=workspace_id,
            target_refs=(),
            expected_versions={},
            payload=_Payload("hello"),
        ),
        received_at=_NOW,
    )
    commit_id = CommitId(uuid.uuid4())
    SqlAlchemyCommitRepository(db_connection).append(
        CommitUnit(
            commit_id=commit_id,
            command_id=command_id,
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            target_refs=(),
            relation_refs=(),
            governance_refs=(),
            audit_event_ids=(),
            outbox_ids=(),
            committed_at=_NOW,
            outcome=CommitOutcome.COMMITTED,
        )
    )
    return command_id, attempt_id, commit_id


def _seed_recovery_record(db_connection: sa.Connection, *, workspace_id: WorkspaceId) -> RecoveryId:
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_id
    )
    record = RecoveryRecord(
        recovery_id=RecoveryId(uuid.uuid4()),
        workspace_scope_ref=workspace_id,
        failure_correlation_ref=CorrelationId(uuid.uuid4()),
        original_command_id=command_id,
        original_attempt_id=attempt_id,
        original_commit_id=commit_id,
        failure_classifications=(FailureClass.F_PERS,),
        canonical_state_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        external_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        recovery_actor_type="SYSTEM_SERVICE",
        recovery_actor_id="recovery-worker-1",
        result=RecoveryOutcome.UNRESOLVED,
        created_at=_NOW,
        updated_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    SqlAlchemyRecoveryRepository(db_connection).create(record)
    return record.recovery_id


def _principal_engine(db_connection: sa.Connection, principal: str) -> sa.Engine:
    url = db_connection.engine.url.set(username=principal, password=f"{principal}_local_dev_only")
    return sa.create_engine(url)


@contextmanager
def _as_principal(db_connection: sa.Connection, principal: str) -> Iterator[sa.Connection]:
    """Exercises RLS/grants AS `principal` on the SAME session/transaction
    as `db_connection` itself, via `SET ROLE` (the superuser bootstrap
    role may always do this) -- unlike a genuinely separate connection
    (`_principal_engine`), this lets a test observe rows this SAME test
    just seeded via `db_connection`, which a truly separate connection
    could never see until the seeding transaction commits (it never
    does -- `db_connection`'s own fixture rolls back at teardown).
    `current_user` changes for real, so RLS/grants apply exactly as they
    would for a genuine `recovery_reader`/`api_reader`/etc. connection.
    """
    db_connection.execute(sa.text(f"SET ROLE {principal}"))
    try:
        yield db_connection
    finally:
        db_connection.execute(sa.text("RESET ROLE"))


def test_workspace_context_port_structural_shape() -> None:
    method_names = {name for name in dir(WorkspaceContextPort) if not name.startswith("_")}
    assert method_names == {"set_workspace_context", "clear_workspace_context"}


def test_no_context_set_yields_zero_rows_even_though_real_rows_exist(
    db_connection: sa.Connection,
) -> None:
    """TESTABLE INVARIANT: RLS defaults to fail-closed, not
    fail-open. A connection that never calls the trusted server
    adapter sees NOTHING, not everything."""
    workspace_id = _workspace(db_connection, email="rls-no-context@nonproof.test")
    _seed_recovery_record(db_connection, workspace_id=workspace_id)

    with _as_principal(db_connection, "recovery_reader") as conn:
        count = conn.execute(sa.text("SELECT count(*) FROM recovery_records")).scalar_one()

    assert count == 0


def test_correct_context_reveals_only_its_own_workspace_row(db_connection: sa.Connection) -> None:
    workspace_a = _workspace(db_connection, email="rls-correct-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="rls-correct-b@nonproof.test")
    recovery_id_a = _seed_recovery_record(db_connection, workspace_id=workspace_a)
    _seed_recovery_record(db_connection, workspace_id=workspace_b)

    with _as_principal(db_connection, "recovery_reader") as conn:
        SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_a)
        rows = conn.execute(sa.text("SELECT id FROM recovery_records")).scalars().all()

    assert rows == [recovery_id_a.value]


def test_mut_pkg26_01_rls_bypass_assumption_arbitrary_context_grants_access(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "RLS bypass assumption" --
    disclosed, not hidden. `set_workspace_context` performs NO
    membership verification of its own (see `security.workspace`'s
    own module docstring) -- a connection that calls it with an
    arbitrary, unverified `WorkspaceId` (one it does not genuinely
    belong to) DOES gain visibility into that Workspace's own rows.
    This is RLS's own real, honestly-proven limit: it defends against
    ACCIDENTAL leakage (a forgotten WHERE clause, an unset context),
    never against a caller already trusted enough to call this port
    who chooses to lie to it -- that verification remains BND-002's
    own job, performed BEFORE this adapter is ever called, which this
    test deliberately skips to prove the boundary is real."""
    workspace_a = _workspace(db_connection, email="rls-bypass-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="rls-bypass-b@nonproof.test")
    _seed_recovery_record(db_connection, workspace_id=workspace_a)
    recovery_id_b = _seed_recovery_record(db_connection, workspace_id=workspace_b)

    with _as_principal(db_connection, "recovery_reader") as conn:
        # This connection never proved membership in workspace_b -- it
        # simply claims it.
        SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_b)
        rows = conn.execute(sa.text("SELECT id FROM recovery_records")).scalars().all()

    assert rows == [recovery_id_b.value]


def test_clearing_context_returns_to_the_fail_closed_default(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="rls-clear@nonproof.test")
    _seed_recovery_record(db_connection, workspace_id=workspace_id)

    with _as_principal(db_connection, "recovery_reader") as conn:
        context = SqlAlchemyWorkspaceContext(conn)
        context.set_workspace_context(workspace_id)
        assert conn.execute(sa.text("SELECT count(*) FROM recovery_records")).scalar_one() == 1
        context.clear_workspace_context()
        assert conn.execute(sa.text("SELECT count(*) FROM recovery_records")).scalar_one() == 0


def test_with_check_rejects_an_insert_claiming_the_wrong_workspace(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "direct canonical write" --
    RLS's own `WITH CHECK` clause defends the WRITE side too, not just
    reads: `recovery_reader` genuinely HAS an INSERT grant on
    `recovery_records` (PKG-25), but if the row's own `workspace_id`
    does not match the connection's CURRENT context, the insert is
    rejected -- even though the table-level GRANT alone would have
    allowed it."""
    workspace_a = _workspace(db_connection, email="rls-check-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="rls-check-b@nonproof.test")
    command_id, attempt_id, commit_id = _record_real_command_and_commit(
        db_connection, workspace_id=workspace_b
    )

    with _as_principal(db_connection, "recovery_reader") as conn:
        SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_a)  # claims workspace_a...
        with (
            pytest.raises(sa.exc.DBAPIError, match="row-level security policy"),
            conn.begin_nested(),
        ):
            conn.execute(
                sa.text(
                    "INSERT INTO recovery_records "
                    "(id, workspace_id, failure_correlation_ref, original_command_id, "
                    "original_attempt_id, original_commit_id, canonical_state_certainty, "
                    "external_consequence_certainty, recovery_class, recovery_actor_type, "
                    "recovery_actor_id, result, created_at, updated_at, record_version) "
                    "VALUES (:id, :workspace_id, :correlation, :command_id, :attempt_id, "
                    ":commit_id, 'CANONICAL_STATE_UNKNOWN', 'EXTERNAL_CONSEQUENCE_UNKNOWN', "
                    "'RC-02', 'SYSTEM_SERVICE', 'recovery-worker-1', 'UNRESOLVED', "
                    ":now, :now, 1)"
                ),
                {
                    "id": uuid.uuid4(),
                    "workspace_id": workspace_b.value,  # ...but writes into workspace_b
                    "correlation": uuid.uuid4(),
                    "command_id": command_id.value,
                    "attempt_id": attempt_id.value,
                    "commit_id": commit_id.value,
                    "now": _NOW,
                },
            )


def test_api_reader_is_subject_to_the_same_rls_policy_as_recovery_reader(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "wrong DB principal" -- RLS
    applies uniformly across every non-owner principal, not only the
    one this package's other tests happen to use most."""
    workspace_a = _workspace(db_connection, email="rls-api-reader-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="rls-api-reader-b@nonproof.test")
    recovery_id_a = _seed_recovery_record(db_connection, workspace_id=workspace_a)
    _seed_recovery_record(db_connection, workspace_id=workspace_b)

    with _as_principal(db_connection, "api_reader") as conn:
        SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_a)
        rows = conn.execute(sa.text("SELECT id FROM recovery_records")).scalars().all()

    assert rows == [recovery_id_a.value]


def test_migration_owner_remains_denied_all_dml_regardless_of_rls_context(
    db_connection: sa.Connection,
) -> None:
    """Regression proof: adding RLS must not accidentally WIDEN
    `migration_owner`'s own privilege (PKG-25's own P-24 proof) --
    RLS is defense-in-depth on TOP of the grant system, never a
    replacement that could loosen it."""
    workspace_id = _workspace(db_connection, email="rls-migration-owner@nonproof.test")

    engine = _principal_engine(db_connection, "migration_owner")
    try:
        with engine.connect() as conn:
            SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_id)
            with pytest.raises(sa.exc.DBAPIError, match="permission denied"):
                conn.execute(sa.text("SELECT 1 FROM recovery_records LIMIT 1"))
    finally:
        engine.dispose()


def test_rls_is_enabled_on_every_workspace_scoped_table(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: a future migration could add a new
    Workspace-keyed table and forget to enable RLS on it -- this test
    would catch that regression for every table this migration
    actually touched."""
    rows = (
        db_connection.execute(
            sa.text(
                "SELECT relname FROM pg_class "
                "WHERE relrowsecurity = true AND relnamespace = 'public'::regnamespace"
            )
        )
        .scalars()
        .all()
    )

    assert set(rows) == {
        "workspace_memberships",
        "role_assignments",
        "human_authority_bindings",
        "challenges",
        "sessions",
        "questions",
        "question_lineage",
        "question_bursts",
        "burst_question_memberships",
        "commands",
        "command_attempts",
        "idempotency_records",
        "audit_events",
        "outbox_events",
        "commit_units",
        "question_selections",
        "decisions",
        "source_references",
        "evidence",
        "claim_anchors",
        "evidence_relations",
        "evidence_set_references",
        "ai_generations",
        "ai_derived_artifacts",
        "ai_context_manifests",
        "projection_checkpoints",
        "session_read_model",
        "inquiry_read_model",
        "recovery_records",
        # F02 WU-02.8 (migration b3d8e5f0a2c7): same workspace_isolation policy.
        "session_participations",
    }


def test_mut_pkg26_02_rls_is_the_actual_mechanism_not_an_empty_table_coincidence(
    db_connection: sa.Connection,
) -> None:
    """Guard-necessity/counterfactual proof, not a code mutation (this
    session's own tool classifier denies temporarily disabling a real
    security control, even reverted -- the same disclosed adaptation
    PKG-24/25 each already used). PostgreSQL RLS is structurally
    bypassed for a table's own OWNER and for superusers (`nquiry`,
    this fixture's own connection, is both, unchanged since before
    this package) -- this is inherent Postgres behavior, not something
    this package configures. Querying the IDENTICAL table with the
    IDENTICAL two seeded rows through BOTH `db_connection` (bypasses
    RLS) and `recovery_reader` (subject to RLS) in the same test proves
    the difference in visible row count is caused BY the RLS policy
    itself, not by the rows failing to exist or by some other
    unrelated cause."""
    workspace_a = _workspace(db_connection, email="rls-mut02-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="rls-mut02-b@nonproof.test")
    _seed_recovery_record(db_connection, workspace_id=workspace_a)
    _seed_recovery_record(db_connection, workspace_id=workspace_b)

    superuser_count = db_connection.execute(
        sa.text("SELECT count(*) FROM recovery_records")
    ).scalar_one()

    with _as_principal(db_connection, "recovery_reader") as conn:
        SqlAlchemyWorkspaceContext(conn).set_workspace_context(workspace_a)
        restricted_count = conn.execute(
            sa.text("SELECT count(*) FROM recovery_records")
        ).scalar_one()

    assert superuser_count == 2
    assert restricted_count == 1
