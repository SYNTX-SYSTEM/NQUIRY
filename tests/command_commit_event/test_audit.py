"""T7 AUDIT TEST: AuditEvent and SqlAlchemyAuditRepository, against real
PostgreSQL.

14 section 50's own test implementation map assigns
`tests/command_commit_event/test_audit.py` to this package.

WHY EVERY DB-BACKED TEST NOW RECORDS A REAL `commit_units` ROW TOO
--------------------------------------------------------------------
PKG-13's own migration (`b06f9a5b3d1b`) retrofits a composite FK from
`audit_events.commit_id` to `commit_units(id, workspace_id)` -- exactly
the forward reference this package's own migration docstring disclosed
as pending. A bare, never-persisted `CommitId` placeholder (this
file's own original PKG-12-era design, honest at the time since
`commit_units` did not exist yet) now violates that FK. Every fixture
therefore records a real `CommitUnit` via `SqlAlchemyCommitRepository`
(PKG-13) first, exactly the same "keep predecessor tests green across
a later package's retrofit" obligation PKG-11 already honored for its
own idempotency tests when PKG-10's `command_attempts` table gained
its own composite FKs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from audit.models import AuditEvent
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.tables import audit_events_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    AuditEventId,
    CommandId,
    CommitId,
    CorrelationId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion
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


def _record_command(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, command_id: CommandId
) -> AttemptId:
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
    return attempt_id


def _record_commit_unit(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    command_id: CommandId,
    attempt_id: AttemptId,
    commit_id: CommitId,
) -> None:
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


def _record_command_and_commit(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId, command_id: CommandId
) -> CommitId:
    attempt_id = _record_command(db_connection, workspace_id=workspace_id, command_id=command_id)
    commit_id = CommitId(uuid.uuid4())
    _record_commit_unit(
        db_connection,
        workspace_id=workspace_id,
        command_id=command_id,
        attempt_id=attempt_id,
        commit_id=commit_id,
    )
    return commit_id


def _event(
    *,
    workspace_id: WorkspaceId,
    command_id: CommandId,
    commit_id: CommitId,
    correlation_id: CorrelationId | None = None,
    result: str = "COMMITTED",
) -> AuditEvent:
    return AuditEvent(
        audit_event_id=AuditEventId(uuid.uuid4()),
        event_type="SESSION_TRANSITIONED",
        event_schema_version=ContractVersion("1.0"),
        workspace_id=workspace_id,
        occurred_at=_NOW,
        actor_type="HUMAN_USER",
        actor_id="user-ref-1",
        command_type="CMD_TEST_OPERATION",
        command_id=command_id,
        commit_id=commit_id,
        correlation_id=correlation_id or CorrelationId(uuid.uuid4()),
        target_refs=("thing-a",),
        authority_source_ref=uuid.uuid4(),
        result=result,
    )


# ---------------------------------------------------------------------------
# AuditEvent construction (no database)
# ---------------------------------------------------------------------------


def test_constructs_a_well_formed_audit_event() -> None:
    event = _event(
        workspace_id=WorkspaceId(uuid.uuid4()),
        command_id=CommandId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
    )
    assert event.result == "COMMITTED"


def test_denies_empty_event_type() -> None:
    with pytest.raises(ValueError, match="event_type must be non-empty"):
        AuditEvent(
            audit_event_id=AuditEventId(uuid.uuid4()),
            event_type="",
            event_schema_version=ContractVersion("1.0"),
            workspace_id=WorkspaceId(uuid.uuid4()),
            occurred_at=_NOW,
            actor_type="HUMAN_USER",
            actor_id="user-ref-1",
            command_type="CMD_TEST_OPERATION",
            command_id=CommandId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            target_refs=(),
            authority_source_ref=uuid.uuid4(),
            result="COMMITTED",
        )


def test_denies_a_non_audit_event_id() -> None:
    """Novel/adapted attack: a foreign strong identity (here, a bare
    UUID pretending to be an AuditEventId) cannot construct an
    AuditEvent -- the same type-distinctness defense PKG-10 established
    for CommandEnvelope.command_id.
    """
    with pytest.raises(TypeError, match="audit_event_id must be an AuditEventId"):
        AuditEvent(
            audit_event_id=uuid.uuid4(),  # type: ignore[arg-type]
            event_type="SESSION_TRANSITIONED",
            event_schema_version=ContractVersion("1.0"),
            workspace_id=WorkspaceId(uuid.uuid4()),
            occurred_at=_NOW,
            actor_type="HUMAN_USER",
            actor_id="user-ref-1",
            command_type="CMD_TEST_OPERATION",
            command_id=CommandId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            target_refs=(),
            authority_source_ref=uuid.uuid4(),
            result="COMMITTED",
        )


# ---------------------------------------------------------------------------
# SqlAlchemyAuditRepository, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_append_and_get_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="audit-roundtrip@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_id, command_id=command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    event = _event(workspace_id=workspace_id, command_id=command_id, commit_id=commit_id)

    repo.append(event)

    fetched = repo.get(event.audit_event_id)
    assert fetched is not None
    assert fetched.audit_event_id == event.audit_event_id
    assert fetched.target_refs == ("thing-a",)


def test_list_for_correlation_returns_only_matching_events(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="audit-correlation@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_id, command_id=command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    shared_correlation = CorrelationId(uuid.uuid4())
    matching = _event(
        workspace_id=workspace_id,
        command_id=command_id,
        commit_id=commit_id,
        correlation_id=shared_correlation,
    )
    other = _event(workspace_id=workspace_id, command_id=command_id, commit_id=commit_id)
    repo.append(matching)
    repo.append(other)

    results = repo.list_for_correlation(shared_correlation)

    assert [e.audit_event_id for e in results] == [matching.audit_event_id]


def test_repository_exposes_no_update_or_delete_method(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attacks: audit update; audit delete
    (structural half). `AuditRepository`'s own Protocol shape is the
    primary defense -- there is no method to even attempt either.
    """
    repo = SqlAlchemyAuditRepository(db_connection)
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")
    assert not hasattr(repo, "correct")


def test_direct_sql_update_of_an_audit_event_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: audit update (database half)."""
    workspace_id = _workspace(db_connection, email="audit-db-update@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_id, command_id=command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    event = _event(workspace_id=workspace_id, command_id=command_id, commit_id=commit_id)
    repo.append(event)

    with (
        pytest.raises(sa.exc.DBAPIError, match="append-only"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(audit_events_table)
            .where(audit_events_table.c.id == event.audit_event_id.value)
            .values(result="DENIED")
        )


def test_direct_sql_delete_of_an_audit_event_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: audit delete (database half)."""
    workspace_id = _workspace(db_connection, email="audit-db-delete@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_id, command_id=command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    event = _event(workspace_id=workspace_id, command_id=command_id, commit_id=commit_id)
    repo.append(event)

    with (
        pytest.raises(sa.exc.DBAPIError, match="cannot be deleted"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.delete(audit_events_table).where(
                audit_events_table.c.id == event.audit_event_id.value
            )
        )


def test_denies_an_audit_event_referencing_an_unrecorded_command(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: an AuditEvent claiming a command_id that
    was never recorded via CommandRepository -- the composite FK makes
    this structurally impossible, mirroring PKG-11's own
    `test_begin_propagates_a_genuine_integrity_error_that_is_not_a_race`.
    A real, valid `commit_units` row is used so this test isolates
    exactly the command_id FK, not the commit_id one.
    """
    workspace_id = _workspace(db_connection, email="audit-orphan-command@nonproof.test")
    unrelated_command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_id, command_id=unrelated_command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    event = _event(
        workspace_id=workspace_id, command_id=CommandId(uuid.uuid4()), commit_id=commit_id
    )

    with pytest.raises(sa.exc.IntegrityError, match="fk_audit_events_command_workspace"):
        repo.append(event)


def test_denies_an_audit_event_referencing_a_cross_workspace_command(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: cross-Workspace command_id reference --
    the same composite-FK defense PKG-11 established for
    `idempotency_records`, applied here to `audit_events`.
    """
    workspace_a = _workspace(db_connection, email="audit-fk-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="audit-fk-b@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    _record_command(db_connection, workspace_id=workspace_a, command_id=command_id)
    unrelated_command_id = CommandId(uuid.uuid4())
    commit_id = _record_command_and_commit(
        db_connection, workspace_id=workspace_b, command_id=unrelated_command_id
    )
    repo = SqlAlchemyAuditRepository(db_connection)
    event = _event(workspace_id=workspace_b, command_id=command_id, commit_id=commit_id)

    with pytest.raises(sa.exc.IntegrityError, match="fk_audit_events_command_workspace"):
        repo.append(event)
