"""T7 IDEMPOTENCY TEST: the pure decision engine and the durable
SqlAlchemyIdempotencyRepository adapter, against real PostgreSQL.

14 section 50's own test implementation map assigns this exact file to
P-19 ("duplicate COMMITTED -> one consequence").

WHY EVERY DB-BACKED TEST CALLS `CommandRepository.record_attempt` FIRST
--------------------------------------------------------------------
`idempotency_records.command_id` carries a composite FK to
`commands(id, workspace_id)` (`b5b33834b7ea`) -- an `IdempotencyPort.begin()`
call for a `command_id` that was never recorded via PKG-10's
`CommandRepository` is not a legitimate scenario in production (a real
caller always records the command attempt before or alongside tracking
its idempotency), and `begin()` correctly refuses it (a real
`ForeignKeyViolation`, surfaced as `sa.exc.IntegrityError` --
`test_begin_propagates_a_genuine_integrity_error_that_is_not_a_race`
proves this is not swallowed as a false "race"). Every other test
therefore records the command first, exactly mirroring the real
two-step flow: `CommandRepository.record_attempt` then
`IdempotencyPort.begin`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope, compute_payload_fingerprint
from commit.idempotency import (
    IdempotencyAlreadyCommitted,
    IdempotencyDecision,
    IdempotencyIndeterminateBlocked,
    IdempotencyInProgress,
    IdempotencyOutcome,
    IdempotencyPayloadCollision,
    IdempotencyRecord,
    SqlAlchemyIdempotencyRepository,
    decide_idempotency_action,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.tables import idempotency_records_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _record(
    *,
    idempotency_key: str = "idem-1",
    workspace_id: WorkspaceId,
    command_id: CommandId,
    payload_fingerprint: str = "fp-1",
    outcome: IdempotencyOutcome = IdempotencyOutcome.IN_PROGRESS,
    commit_id: CommitId | None = None,
    result_ref: str | None = None,
) -> IdempotencyRecord:
    return IdempotencyRecord(
        idempotency_key=idempotency_key,
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        command_id=command_id,
        payload_fingerprint=payload_fingerprint,
        first_seen_at=_NOW,
        latest_attempt_id=AttemptId(uuid.uuid4()),
        outcome=outcome,
        commit_id=commit_id,
        result_ref=result_ref,
    )


# ---------------------------------------------------------------------------
# Pure decision engine (no database)
# ---------------------------------------------------------------------------


def test_new_request_proceeds() -> None:
    """Mandatory attack category: new."""
    decision = decide_idempotency_action(
        existing=None,
        requested_command_id=CommandId(uuid.uuid4()),
        requested_payload_fingerprint="fp",
    )
    assert decision is IdempotencyDecision.PROCEED_NEW


def test_in_progress_duplicate_returns_no_second_execution() -> None:
    """Mandatory attack: in-progress duplicate."""
    command_id = CommandId(uuid.uuid4())
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(
        workspace_id=workspace_id, command_id=command_id, outcome=IdempotencyOutcome.IN_PROGRESS
    )

    decision = decide_idempotency_action(
        existing=existing, requested_command_id=command_id, requested_payload_fingerprint="fp-1"
    )

    assert decision is IdempotencyDecision.RETURN_IN_PROGRESS_NO_EXECUTION


def test_committed_duplicate_returns_prior_result() -> None:
    """Mandatory attack: committed duplicate."""
    command_id = CommandId(uuid.uuid4())
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(
        workspace_id=workspace_id,
        command_id=command_id,
        outcome=IdempotencyOutcome.COMMITTED,
        commit_id=CommitId(uuid.uuid4()),
        result_ref="result-1",
    )

    decision = decide_idempotency_action(
        existing=existing, requested_command_id=command_id, requested_payload_fingerprint="fp-1"
    )

    assert decision is IdempotencyDecision.RETURN_COMMITTED_RESULT


def test_same_key_different_payload_is_rejected() -> None:
    """Mandatory attack: same key different payload."""
    command_id = CommandId(uuid.uuid4())
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(workspace_id=workspace_id, command_id=command_id, payload_fingerprint="fp-1")

    decision = decide_idempotency_action(
        existing=existing,
        requested_command_id=command_id,
        requested_payload_fingerprint="fp-DIFFERENT",
    )

    assert decision is IdempotencyDecision.REJECT_PAYLOAD_COLLISION


def test_different_command_id_under_same_key_is_also_a_collision() -> None:
    """Novel/adapted attack: command_id substitution under a reused
    idempotency_key, even with a matching payload fingerprint by
    coincidence (see module docstring).
    """
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(
        workspace_id=workspace_id, command_id=CommandId(uuid.uuid4()), payload_fingerprint="fp-1"
    )

    decision = decide_idempotency_action(
        existing=existing,
        requested_command_id=CommandId(uuid.uuid4()),
        requested_payload_fingerprint="fp-1",
    )

    assert decision is IdempotencyDecision.REJECT_PAYLOAD_COLLISION


def test_failed_precommit_retry_proceeds_with_fresh_attempt() -> None:
    """Mandatory attack: FAILED_PRECOMMIT retry."""
    command_id = CommandId(uuid.uuid4())
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(
        workspace_id=workspace_id,
        command_id=command_id,
        outcome=IdempotencyOutcome.FAILED_PRECOMMIT,
    )

    decision = decide_idempotency_action(
        existing=existing, requested_command_id=command_id, requested_payload_fingerprint="fp-1"
    )

    assert decision is IdempotencyDecision.PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT


def test_indeterminate_retry_is_blocked() -> None:
    """Mandatory attack: INDETERMINATE retry."""
    command_id = CommandId(uuid.uuid4())
    workspace_id = WorkspaceId(uuid.uuid4())
    existing = _record(
        workspace_id=workspace_id, command_id=command_id, outcome=IdempotencyOutcome.INDETERMINATE
    )

    decision = decide_idempotency_action(
        existing=existing, requested_command_id=command_id, requested_payload_fingerprint="fp-1"
    )

    assert decision is IdempotencyDecision.BLOCK_INDETERMINATE_NO_BLIND_RETRY


def test_idempotency_record_requires_commit_id_iff_committed() -> None:
    with pytest.raises(ValueError, match="commit_id must be set if and only if"):
        _record(
            workspace_id=WorkspaceId(uuid.uuid4()),
            command_id=CommandId(uuid.uuid4()),
            outcome=IdempotencyOutcome.COMMITTED,
            commit_id=None,
        )
    with pytest.raises(ValueError, match="commit_id must be set if and only if"):
        _record(
            workspace_id=WorkspaceId(uuid.uuid4()),
            command_id=CommandId(uuid.uuid4()),
            outcome=IdempotencyOutcome.IN_PROGRESS,
            commit_id=CommitId(uuid.uuid4()),
        )


def test_idempotency_record_rejects_result_ref_unless_committed() -> None:
    with pytest.raises(ValueError, match="result_ref may only be set"):
        _record(
            workspace_id=WorkspaceId(uuid.uuid4()),
            command_id=CommandId(uuid.uuid4()),
            outcome=IdempotencyOutcome.IN_PROGRESS,
            result_ref="result-1",
        )


# ---------------------------------------------------------------------------
# SqlAlchemyIdempotencyRepository, against real PostgreSQL
# ---------------------------------------------------------------------------


def _envelope(
    *,
    command_id: CommandId,
    attempt_id: AttemptId,
    workspace_id: WorkspaceId,
    idempotency_key: str = "idem-1",
    payload: object = _Payload("hello"),
) -> CommandEnvelope:
    return CommandEnvelope(
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
        payload=payload,
        idempotency_key=idempotency_key,
    )


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def _begin(
    db_connection: sa.Connection,
    idempotency_repo: SqlAlchemyIdempotencyRepository,
    envelope: CommandEnvelope,
    *,
    seen_at: datetime,
) -> IdempotencyRecord:
    """The real two-step flow: record the command attempt (PKG-10),
    then track its idempotency (this package). See module docstring.
    """
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=seen_at)
    return idempotency_repo.begin(envelope, seen_at=seen_at)


def test_begin_creates_a_new_in_progress_record(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-new@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
    )

    record = _begin(db_connection, repo, envelope, seen_at=_NOW)

    assert record.outcome is IdempotencyOutcome.IN_PROGRESS
    assert record.commit_id is None


def test_begin_requires_an_idempotency_key(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-no-key@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        idempotency_key=None,  # type: ignore[arg-type]
    )
    SqlAlchemyCommandRepository(db_connection).record_attempt(envelope, received_at=_NOW)

    with pytest.raises(ValueError, match="requires envelope.idempotency_key"):
        repo.begin(envelope, seen_at=_NOW)


def test_begin_propagates_a_genuine_integrity_error_that_is_not_a_race(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: `begin()` called for a `command_id` that
    was never recorded via `CommandRepository` -- the composite FK
    violation this produces must propagate as-is, not be misreported
    as a resolved in-progress race (see module docstring and
    `SqlAlchemyIdempotencyRepository._resolve_after_race`'s own
    docstring).
    """
    workspace_id = _workspace(db_connection, email="idem-orphan-command@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
    )

    with pytest.raises(sa.exc.IntegrityError, match="fk_idempotency_records_command_workspace"):
        repo.begin(envelope, seen_at=_NOW)


def test_begin_denies_in_progress_duplicate(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-in-progress@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    payload = _Payload("same")
    first = _envelope(
        command_id=command_id,
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        payload=payload,
    )
    _begin(db_connection, repo, first, seen_at=_NOW)

    second = _envelope(
        command_id=command_id,
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        payload=payload,
    )
    with pytest.raises(IdempotencyInProgress) as excinfo:
        _begin(db_connection, repo, second, seen_at=_LATER)
    assert excinfo.value.existing.outcome is IdempotencyOutcome.IN_PROGRESS


def test_begin_denies_committed_duplicate_and_returns_prior_result(
    db_connection: sa.Connection,
) -> None:
    """Mandatory attack: committed duplicate. P-19's own precondition."""
    workspace_id = _workspace(db_connection, email="idem-committed@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    payload = _Payload("same")
    envelope = _envelope(
        command_id=command_id,
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        payload=payload,
    )
    _begin(db_connection, repo, envelope, seen_at=_NOW)
    repo.mark_committed(
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        idempotency_key="idem-1",
        commit_id=CommitId(uuid.uuid4()),
        result_ref="result-ref-1",
    )

    retry = _envelope(
        command_id=command_id,
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        payload=payload,
    )
    SqlAlchemyCommandRepository(db_connection).record_attempt(retry, received_at=_LATER)
    with pytest.raises(IdempotencyAlreadyCommitted) as excinfo:
        repo.begin(retry, seen_at=_LATER)
    assert excinfo.value.existing.result_ref == "result-ref-1"
    assert excinfo.value.existing.outcome is IdempotencyOutcome.COMMITTED


def test_begin_denies_same_key_different_payload(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-payload-conflict@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    _begin(
        db_connection,
        repo,
        _envelope(
            command_id=command_id,
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            payload=_Payload("original"),
        ),
        seen_at=_NOW,
    )

    # A changed payload under the same command_id is itself a
    # PKG-10-layer conflict (CommandPayloadConflict) before idempotency
    # is ever consulted -- so this attack is exercised with a *new*
    # command_id sharing the same idempotency_key instead, which is
    # exactly 09/14's own scenario ("same key different payload").
    changed_command_id = CommandId(uuid.uuid4())
    with pytest.raises(IdempotencyPayloadCollision):
        _begin(
            db_connection,
            repo,
            _envelope(
                command_id=changed_command_id,
                attempt_id=AttemptId(uuid.uuid4()),
                workspace_id=workspace_id,
                payload=_Payload("changed"),
            ),
            seen_at=_LATER,
        )


def test_begin_allows_a_fresh_attempt_after_failed_precommit(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-failed-retry@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    payload = _Payload("same")
    first_attempt = AttemptId(uuid.uuid4())
    _begin(
        db_connection,
        repo,
        _envelope(
            command_id=command_id,
            attempt_id=first_attempt,
            workspace_id=workspace_id,
            payload=payload,
        ),
        seen_at=_NOW,
    )
    repo.mark_failed_precommit(
        workspace_id=workspace_id, command_type="CMD_TEST_OPERATION", idempotency_key="idem-1"
    )

    second_attempt = AttemptId(uuid.uuid4())
    record = _begin(
        db_connection,
        repo,
        _envelope(
            command_id=command_id,
            attempt_id=second_attempt,
            workspace_id=workspace_id,
            payload=payload,
        ),
        seen_at=_LATER,
    )

    assert record.outcome is IdempotencyOutcome.IN_PROGRESS
    assert record.latest_attempt_id == second_attempt


def test_begin_blocks_indeterminate_retry(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-indeterminate@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    payload = _Payload("same")
    _begin(
        db_connection,
        repo,
        _envelope(
            command_id=command_id,
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_id,
            payload=payload,
        ),
        seen_at=_NOW,
    )
    repo.mark_indeterminate(
        workspace_id=workspace_id, command_type="CMD_TEST_OPERATION", idempotency_key="idem-1"
    )

    retry = _envelope(
        command_id=command_id,
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
        payload=payload,
    )
    SqlAlchemyCommandRepository(db_connection).record_attempt(retry, received_at=_LATER)
    with pytest.raises(IdempotencyIndeterminateBlocked):
        repo.begin(retry, seen_at=_LATER)


def test_begin_denies_cross_workspace_key_collision(db_connection: sa.Connection) -> None:
    """Mandatory attack: cross-Workspace key collision. `idempotency_records`'
    own PRIMARY KEY includes `workspace_id`, so a colliding key at a
    *different* Workspace is not even the same row -- it is structurally
    a brand-new, independent identity, proving cross-Workspace isolation
    at the strongest possible level (there is no shared row to collide
    over at all).
    """
    workspace_a = _workspace(db_connection, email="idem-ws-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="idem-ws-b@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)

    record_a = _begin(
        db_connection,
        repo,
        _envelope(
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_a,
            idempotency_key="shared-key",
        ),
        seen_at=_NOW,
    )
    record_b = _begin(
        db_connection,
        repo,
        _envelope(
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            workspace_id=workspace_b,
            idempotency_key="shared-key",
        ),
        seen_at=_NOW,
    )

    assert record_a.workspace_id == workspace_a
    assert record_b.workspace_id == workspace_b
    assert record_a.command_id != record_b.command_id


def test_begin_denies_an_idempotency_record_referencing_a_cross_workspace_command(
    db_connection: sa.Connection,
) -> None:
    """Mandatory attack: cross-Workspace key collision, structural half
    -- the composite FK (command_id, workspace_id) -> commands(id,
    workspace_id) makes it impossible to even insert a row claiming a
    Workspace different from its referenced Command's own Workspace.
    """
    workspace_a = _workspace(db_connection, email="idem-fk-a@nonproof.test")
    workspace_b = _workspace(db_connection, email="idem-fk-b@nonproof.test")
    command_repo = SqlAlchemyCommandRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    command_repo.record_attempt(
        CommandEnvelope(
            command_id=command_id,
            command_type="CMD_TEST_OPERATION",
            command_contract_version=ContractVersion("1.0"),
            attempt_id=AttemptId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            requested_at=_NOW,
            requesting_actor_type="HUMAN_USER",
            requesting_actor_id="user-ref-1",
            workspace_scope_ref=workspace_a,
            target_refs=(),
            expected_versions={},
            payload=_Payload("hello"),
        ),
        received_at=_NOW,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(idempotency_records_table).values(
                idempotency_key="forged-key",
                workspace_id=workspace_b.value,  # different Workspace than the Command's own
                command_type="CMD_TEST_OPERATION",
                command_id=command_id.value,
                payload_fingerprint="fp-1",
                first_seen_at=_NOW,
                latest_attempt_id=uuid.uuid4(),
                outcome="IN_PROGRESS",
            )
        )


def test_begin_survives_a_concurrent_insert_race(db_connection: sa.Connection) -> None:
    """Deterministic proof (no sleep, no thread) of the exact race
    `begin()`'s own SAVEPOINT/IntegrityError handling defends against:
    seed the row exactly as a concurrent winner would have just
    committed it, then call `begin()` -- it must resolve via the same
    decision path as if it had read that row from the start, not raise
    a raw `sa.exc.IntegrityError`.
    """
    workspace_id = _workspace(db_connection, email="idem-race@nonproof.test")
    command_id = CommandId(uuid.uuid4())
    winning_attempt = AttemptId(uuid.uuid4())
    SqlAlchemyCommandRepository(db_connection).record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=winning_attempt,
            workspace_id=workspace_id,
            idempotency_key="race-key",
        ),
        received_at=_NOW,
    )
    db_connection.execute(
        sa.insert(idempotency_records_table).values(
            idempotency_key="race-key",
            workspace_id=workspace_id.value,
            command_type="CMD_TEST_OPERATION",
            command_id=command_id.value,
            # Must match the real fingerprint of the default `_Payload("hello")`
            # both envelopes below carry -- a mismatched placeholder here
            # would make `decide_idempotency_action` see a payload
            # collision instead of the in-progress race this test exists
            # to prove.
            payload_fingerprint=compute_payload_fingerprint(_Payload("hello")),
            first_seen_at=_NOW,
            latest_attempt_id=winning_attempt.value,
            outcome="IN_PROGRESS",
        )
    )

    repo = SqlAlchemyIdempotencyRepository(db_connection)
    losing_attempt = AttemptId(uuid.uuid4())
    SqlAlchemyCommandRepository(db_connection).record_attempt(
        _envelope(
            command_id=command_id,
            attempt_id=losing_attempt,
            workspace_id=workspace_id,
            idempotency_key="race-key",
        ),
        received_at=_LATER,
    )
    losing_envelope = _envelope(
        command_id=command_id,
        attempt_id=losing_attempt,
        workspace_id=workspace_id,
        idempotency_key="race-key",
    )
    # Force the PROCEED_NEW path so the INSERT actually executes and
    # collides with the row already there, exercising the IntegrityError
    # handler rather than the ordinary get()-sees-existing branch.
    monkey_get_calls = {"count": 0}
    original_get = repo.get

    def _get_none_once_then_real(
        *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> IdempotencyRecord | None:
        monkey_get_calls["count"] += 1
        if monkey_get_calls["count"] == 1:
            return None
        return original_get(
            workspace_id=workspace_id, command_type=command_type, idempotency_key=idempotency_key
        )

    repo.get = _get_none_once_then_real  # type: ignore[method-assign]

    with pytest.raises(IdempotencyInProgress) as excinfo:
        repo.begin(losing_envelope, seen_at=_LATER)
    assert excinfo.value.existing.latest_attempt_id == winning_attempt


def test_idempotency_records_row_identity_is_immutable_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="idem-db-immutable@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
    )
    _begin(db_connection, repo, envelope, seen_at=_NOW)

    with pytest.raises(sa.exc.DBAPIError, match="immutable"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.idempotency_key == "idem-1",
            )
            .values(payload_fingerprint="tampered")
        )


def test_committed_outcome_is_terminal_at_the_database_layer(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="idem-db-terminal@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
    )
    _begin(db_connection, repo, envelope, seen_at=_NOW)
    repo.mark_committed(
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        idempotency_key="idem-1",
        commit_id=CommitId(uuid.uuid4()),
        result_ref="result-1",
    )

    with pytest.raises(sa.exc.DBAPIError, match="terminal"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.idempotency_key == "idem-1",
            )
            .values(outcome="INDETERMINATE")
        )


def test_illegal_outcome_transition_is_rejected_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: skip straight from FAILED_PRECOMMIT to
    COMMITTED directly (skipping the required intermediate
    re-IN_PROGRESS retry step) -- proves the trigger's allow-list, not
    merely its terminal-state checks.
    """
    workspace_id = _workspace(db_connection, email="idem-db-illegal-transition@nonproof.test")
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    envelope = _envelope(
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        workspace_id=workspace_id,
    )
    _begin(db_connection, repo, envelope, seen_at=_NOW)
    repo.mark_failed_precommit(
        workspace_id=workspace_id, command_type="CMD_TEST_OPERATION", idempotency_key="idem-1"
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal idempotency outcome transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.idempotency_key == "idem-1",
            )
            .values(outcome="COMMITTED", commit_id=uuid.uuid4())
        )
