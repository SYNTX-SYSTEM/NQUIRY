"""T8 RECOVERY TEST: INDETERMINATE blocks blind retry (P-20's own
territory, 14 section 27: "INDETERMINATE -> no blind retry, route
BND-017/BND-018").

WHY THIS TEST LIVES IN `tests/recovery/`, NOT `tests/command_commit_event/`
--------------------------------------------------------------------------
Every other PKG-11 mandatory attack is a fact purely internal to the
idempotency lifecycle itself (in-progress/committed/payload-collision/
FAILED_PRECOMMIT retry all resolve entirely within `commit.idempotency`).
INDETERMINATE is different: 14 section 27 does not define a legal next
state for it *at all* within this package -- it explicitly routes the
concern to BND-017/BND-018, which are 10_FAILURE_RECOVERY_ROLLBACK.md's
own territory (T8 -> `tests/recovery/`, 14 section 39). This test proves
the half of that routing PKG-11 can actually prove: that no method this
package exposes, and no direct database write, can move an
INDETERMINATE `idempotency_records` row anywhere except by whatever
future governed recovery path PKG-18+ eventually builds
(SUCCESSOR_NOT_BUILT) -- exercised here, in the recovery-shaped test
directory, rather than folded into the general idempotency test file, to
keep the "this needs a future recovery package" framing visible at the
file-location level too.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope
from commit.idempotency import (
    IdempotencyIndeterminateBlocked,
    IdempotencyOutcome,
    SqlAlchemyIdempotencyRepository,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.tables import idempotency_records_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import AttemptId, CommandId, CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _envelope(
    *, command_id: CommandId, attempt_id: AttemptId, workspace_id: WorkspaceId
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
        payload=_Payload("hello"),
        idempotency_key="idem-indeterminate",
    )


def test_no_blind_retry_is_possible_through_the_port_once_indeterminate(
    db_connection: sa.Connection,
) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_id = bootstrap.seed(owner_email="recovery-indeterminate@nonproof.test").workspace_id
    command_repo = SqlAlchemyCommandRepository(db_connection)
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    first_attempt = _envelope(
        command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_id
    )
    command_repo.record_attempt(first_attempt, received_at=_NOW)
    repo.begin(first_attempt, seen_at=_NOW)
    repo.mark_indeterminate(
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        idempotency_key="idem-indeterminate",
    )

    retry = _envelope(
        command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_id
    )
    command_repo.record_attempt(retry, received_at=_LATER)
    with pytest.raises(IdempotencyIndeterminateBlocked):
        repo.begin(retry, seen_at=_LATER)

    record = repo.get(
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        idempotency_key="idem-indeterminate",
    )
    assert record is not None
    assert record.outcome is IdempotencyOutcome.INDETERMINATE


def test_no_direct_database_write_can_move_an_indeterminate_row_either(
    db_connection: sa.Connection,
) -> None:
    """`IdempotencyPort` refuses INDETERMINATE retries at the Python
    layer (proven above); this proves the identical refusal holds even
    for a direct SQL UPDATE bypassing the repository entirely -- the
    outcome-transition trigger, not application discipline alone, is
    what makes "no legal next state for INDETERMINATE in this package"
    a real guarantee.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_id = bootstrap.seed(
        owner_email="recovery-indeterminate-db@nonproof.test"
    ).workspace_id
    command_repo = SqlAlchemyCommandRepository(db_connection)
    repo = SqlAlchemyIdempotencyRepository(db_connection)
    command_id = CommandId(uuid.uuid4())
    envelope = _envelope(
        command_id=command_id, attempt_id=AttemptId(uuid.uuid4()), workspace_id=workspace_id
    )
    command_repo.record_attempt(envelope, received_at=_NOW)
    repo.begin(envelope, seen_at=_NOW)
    repo.mark_indeterminate(
        workspace_id=workspace_id,
        command_type="CMD_TEST_OPERATION",
        idempotency_key="idem-indeterminate",
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="INDETERMINATE has no legal next state"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.idempotency_key == "idem-indeterminate",
            )
            .values(outcome="IN_PROGRESS")
        )
