"""T7 COMMAND TEST: SqlAlchemyCommandRepository, against real PostgreSQL.

Uses `NonProofWorkspaceBootstrap` for the Workspace (13 section 5's
permitted downstream use); the invariant under test (Command/attempt
identity, retry, and conflict semantics) does not depend on how the
Workspace came to exist.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope, CommandOutcome
from persistence.command_repository import (
    AttemptAlreadyRecorded,
    AttemptNotFound,
    AttemptOutcomeAlreadyFinal,
    CommandPayloadConflict,
    CommandTypeMismatch,
    CommandWorkspaceMismatch,
    SqlAlchemyCommandRepository,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import AttemptId, CommandId, CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _envelope(
    *,
    command_id: CommandId,
    attempt_id: AttemptId,
    workspace_id: WorkspaceId,
    payload: object = _Payload("hello"),
    target_refs: tuple[str, ...] = (),
    expected_versions: dict[str, RecordVersion] | None = None,
    command_type: str = "CMD_TEST_OPERATION",
) -> CommandEnvelope:
    return CommandEnvelope(
        command_id=command_id,
        command_type=command_type,
        command_contract_version=ContractVersion("1.0"),
        attempt_id=attempt_id,
        correlation_id=CorrelationId(uuid.uuid4()),
        requested_at=_NOW,
        requesting_actor_type="HUMAN_USER",
        requesting_actor_id="user-ref-1",
        workspace_scope_ref=workspace_id,
        target_refs=target_refs,
        expected_versions=expected_versions or {},
        payload=payload,
    )


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def test_records_a_new_command_and_its_first_attempt(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="cmd-new@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    envelope = _envelope(command_id=command_id, attempt_id=attempt_id, workspace_id=workspace_id)

    attempt = repo.record_attempt(envelope, received_at=_NOW)

    assert attempt.command_id == command_id
    assert attempt.attempt_id == attempt_id
    assert attempt.outcome is None
    command = repo.get_command(command_id)
    assert command is not None
    assert command.workspace_id == workspace_id


def test_legitimate_retry_reuses_command_id_with_a_new_attempt_id(
    db_connection: sa.Connection,
) -> None:
    """09 section 12.1: same command_id, new attempt_id, unchanged payload."""
    workspace_id = _workspace(db_connection, email="cmd-retry@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    first_attempt = AttemptId(uuid.uuid4())
    second_attempt = AttemptId(uuid.uuid4())
    payload = _Payload("unchanged")

    repo.record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=first_attempt,
            workspace_id=workspace_id,
            payload=payload,
        ),
        received_at=_NOW,
    )
    repo.record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=second_attempt,
            workspace_id=workspace_id,
            payload=payload,
        ),
        received_at=_LATER,
    )

    attempts = repo.list_attempts(command_id)
    assert len(attempts) == 2
    assert {a.attempt_id for a in attempts} == {first_attempt, second_attempt}


def test_denies_changed_payload_under_the_same_command_identity(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: changed payload under same command
    identity (09 section 12.4/139).
    """
    workspace_id = _workspace(db_connection, email="cmd-payload-conflict@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())

    repo.record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            payload=_Payload("original"),
        ),
        received_at=_NOW,
    )

    with pytest.raises(CommandPayloadConflict):
        repo.record_attempt(
            _envelope(
                command_id=command_id,
                attempt_id=AttemptId(uuid.uuid4()),
                workspace_id=workspace_id,
                payload=_Payload("changed"),
            ),
            received_at=_LATER,
        )


def test_denies_reusing_a_command_id_under_a_different_workspace(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: wrong Workspace."""
    workspace_a = _workspace(db_connection, email="cmd-ws-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="cmd-ws-b@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())

    repo.record_attempt(
        _envelope(
            command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_a
        ),
        received_at=_NOW,
    )

    with pytest.raises(CommandWorkspaceMismatch):
        repo.record_attempt(
            _envelope(
                command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_b
            ),
            received_at=_LATER,
        )


def test_denies_reusing_a_command_id_for_a_different_command_type(
    db_connection: sa.Connection,
) -> None:
    """F02 WU-02.12 (FBR-B): 09 §4.3 defines `command_id` as "the stable
    identity of one logical requested consequential operation". A second
    Command type under the same id is a different operation even when the
    payload fingerprint is equal (two Commands can share a payload shape).
    Accepting it would make the `commands` row of one Command the
    provenance of another Command's effect.
    """
    workspace_id = _workspace(db_connection, email="cmd-type-reuse@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())

    repo.record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            command_type="CMD_FIRST_OPERATION",
        ),
        received_at=_NOW,
    )

    with pytest.raises(CommandTypeMismatch):
        repo.record_attempt(
            _envelope(
                command_id=command_id,
                attempt_id=AttemptId(uuid.uuid4()),
                workspace_id=workspace_id,
                command_type="CMD_SECOND_OPERATION",
            ),
            received_at=_LATER,
        )
    assert len(repo.list_attempts(command_id)) == 1


def test_denies_replaying_an_already_recorded_attempt_id(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: attempt_id reused across two different
    command_ids (identity confusion) -- and, in its simplest form, the
    same attempt_id replayed at all.
    """
    workspace_id = _workspace(db_connection, email="cmd-attempt-reuse@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    shared_attempt_id = AttemptId(uuid.uuid4())
    first_command = CommandId(uuid.uuid4())
    second_command = CommandId(uuid.uuid4())

    repo.record_attempt(
        _envelope(
            command_id=first_command, attempt_id=shared_attempt_id, workspace_id=workspace_id
        ),
        received_at=_NOW,
    )

    with pytest.raises(AttemptAlreadyRecorded):
        repo.record_attempt(
            _envelope(
                command_id=second_command, attempt_id=shared_attempt_id, workspace_id=workspace_id
            ),
            received_at=_LATER,
        )


def test_commands_row_is_immutable_at_the_database_layer(db_connection: sa.Connection) -> None:
    """Defense-in-depth proof: even bypassing the repository's own
    Python-level checks, the database trigger independently rejects any
    UPDATE to `commands`.
    """
    from persistence.tables import commands_table

    workspace_id = _workspace(db_connection, email="cmd-db-immutable@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    repo.record_attempt(
        _envelope(
            command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_id
        ),
        received_at=_NOW,
    )

    with pytest.raises(sa.exc.DBAPIError, match="immutable"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(commands_table)
            .where(commands_table.c.id == command_id.value)
            .values(command_type="CMD_TAMPERED")
        )


def test_records_a_determined_outcome(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="cmd-outcome@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    repo.record_attempt(
        _envelope(command_id=command_id, attempt_id=attempt_id, workspace_id=workspace_id),
        received_at=_NOW,
    )

    repo.record_outcome(
        attempt_id=attempt_id,
        workspace_id=workspace_id,
        outcome=CommandOutcome.COMMITTED,
        completed_at=_LATER,
    )

    attempt = repo.get_attempt(attempt_id)
    assert attempt is not None
    assert attempt.outcome is CommandOutcome.COMMITTED
    assert attempt.completed_at == _LATER


def test_denies_redetermining_an_already_final_outcome(db_connection: sa.Connection) -> None:
    """09 section 18: an outcome is terminal once set; none of the 4
    values is reinterpreted as another.
    """
    workspace_id = _workspace(db_connection, email="cmd-outcome-final@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    attempt_id = AttemptId(uuid.uuid4())
    repo.record_attempt(
        _envelope(command_id=command_id, attempt_id=attempt_id, workspace_id=workspace_id),
        received_at=_NOW,
    )
    repo.record_outcome(
        attempt_id=attempt_id,
        workspace_id=workspace_id,
        outcome=CommandOutcome.INDETERMINATE,
        completed_at=_LATER,
    )

    with pytest.raises(AttemptOutcomeAlreadyFinal):
        repo.record_outcome(
            attempt_id=attempt_id,
            workspace_id=workspace_id,
            outcome=CommandOutcome.COMMITTED,
            completed_at=_LATER,
        )


def test_record_outcome_denies_an_unknown_attempt(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="cmd-outcome-unknown@nonproof.test")
    repo = SqlAlchemyCommandRepository(db_connection)

    with pytest.raises(AttemptNotFound):
        repo.record_outcome(
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            outcome=CommandOutcome.DENIED,
            completed_at=_LATER,
        )


def test_missing_expected_version_is_rejected_before_any_persistence_is_touched(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: missing required expected version,
    exercised at the full repository boundary (envelope construction
    itself fails, so record_attempt is never reached with a malformed
    envelope) -- proves the persistence layer never has to defend
    against this shape because CommandEnvelope already fails closed.
    """
    workspace_id = _workspace(db_connection, email="cmd-missing-version@nonproof.test")
    with pytest.raises(ValueError, match="expected_versions must cover exactly target_refs"):
        _envelope(
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            target_refs=("thing-a",),
            expected_versions={},
        )
