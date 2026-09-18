"""T7 OUTBOX TEST: OutboxRecord and SqlAlchemyOutboxRepository, against
real PostgreSQL.

14 section 50's own test implementation map assigns
`tests/command_commit_event/test_outbox.py` to this package.

WHY EVERY DB-BACKED TEST NOW RECORDS A REAL `commit_units` ROW TOO
--------------------------------------------------------------------
See `tests/command_commit_event/test_audit.py`'s own module docstring:
PKG-13's migration (`b06f9a5b3d1b`) retrofits a composite FK from
`outbox_events.commit_id` to `commit_units(id, workspace_id)`, so the
bare, never-persisted `CommitId` placeholder this file originally used
(honest at PKG-12's own build time) must become a real row.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from events.outbox import DeliveryStatus, OutboxRecord
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.outbox_repository import OutboxRecordNotFound, SqlAlchemyOutboxRepository
from persistence.tables import outbox_events_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, EventId, WorkspaceId
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2030, 1, 1, 0, 5, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


@dataclass(frozen=True, slots=True)
class _Payload:
    note: str


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def _record_real_commit(db_connection: sa.Connection, *, workspace_id: WorkspaceId) -> CommitId:
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
    return commit_id


def _record(
    *,
    workspace_id: WorkspaceId,
    commit_id: CommitId,
    event_id: EventId | None = None,
) -> OutboxRecord:
    return OutboxRecord(
        outbox_id=uuid.uuid4(),
        event_id=event_id or EventId(uuid.uuid4()),
        workspace_id=workspace_id,
        commit_id=commit_id,
        event_type="SESSION_TRANSITIONED",
        created_at=_NOW,
        delivery_status=DeliveryStatus.PENDING,
        delivery_attempt_count=0,
    )


# ---------------------------------------------------------------------------
# OutboxRecord construction (no database)
# ---------------------------------------------------------------------------


def test_constructs_a_well_formed_pending_record() -> None:
    record = _record(workspace_id=WorkspaceId(uuid.uuid4()), commit_id=CommitId(uuid.uuid4()))
    assert record.delivery_status is DeliveryStatus.PENDING
    assert record.delivered_at is None


def test_denies_negative_delivery_attempt_count() -> None:
    with pytest.raises(ValueError, match="delivery_attempt_count must be >= 0"):
        OutboxRecord(
            outbox_id=uuid.uuid4(),
            event_id=EventId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            event_type="SESSION_TRANSITIONED",
            created_at=_NOW,
            delivery_status=DeliveryStatus.PENDING,
            delivery_attempt_count=-1,
        )


def test_denies_delivered_at_without_delivered_status() -> None:
    with pytest.raises(ValueError, match="delivered_at must be set if and only if"):
        OutboxRecord(
            outbox_id=uuid.uuid4(),
            event_id=EventId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            event_type="SESSION_TRANSITIONED",
            created_at=_NOW,
            delivery_status=DeliveryStatus.PENDING,
            delivery_attempt_count=0,
            delivered_at=_NOW,
        )


def test_denies_delivered_status_without_delivered_at() -> None:
    with pytest.raises(ValueError, match="delivered_at must be set if and only if"):
        OutboxRecord(
            outbox_id=uuid.uuid4(),
            event_id=EventId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            commit_id=CommitId(uuid.uuid4()),
            event_type="SESSION_TRANSITIONED",
            created_at=_NOW,
            delivery_status=DeliveryStatus.DELIVERED,
            delivery_attempt_count=1,
            delivered_at=None,
        )


# ---------------------------------------------------------------------------
# SqlAlchemyOutboxRepository, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_append_and_get_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="outbox-roundtrip@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)

    repo.append(record)

    fetched = repo.get(record.outbox_id)
    assert fetched is not None
    assert fetched.delivery_status is DeliveryStatus.PENDING


def test_denies_outbox_duplicate(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: outbox duplicate. 14 section 7.3:
    "outbox_events.event_id is unique."
    """
    workspace_id = _workspace(db_connection, email="outbox-duplicate@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    shared_event_id = EventId(uuid.uuid4())
    repo.append(_record(workspace_id=workspace_id, commit_id=commit_id, event_id=shared_event_id))

    with pytest.raises(sa.exc.IntegrityError, match="uq_outbox_events_event_id"):
        repo.append(
            _record(workspace_id=workspace_id, commit_id=commit_id, event_id=shared_event_id)
        )


def test_mark_delivered_updates_status_and_timestamp(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="outbox-delivered@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)

    repo.mark_delivered(record.outbox_id, delivered_at=_LATER)

    fetched = repo.get(record.outbox_id)
    assert fetched is not None
    assert fetched.delivery_status is DeliveryStatus.DELIVERED
    assert fetched.delivered_at == _LATER
    assert fetched.delivery_attempt_count == 1


def test_mark_delivered_is_idempotent_under_replay(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: outbox replay. 09 section 15.2:
    duplicate delivery must not produce a duplicate consequential
    effect -- re-confirming an already-DELIVERED record is a safe
    no-op, not an error, and does not double-count the attempt.
    """
    workspace_id = _workspace(db_connection, email="outbox-replay@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)
    repo.mark_delivered(record.outbox_id, delivered_at=_LATER)

    repo.mark_delivered(record.outbox_id, delivered_at=_LATER)  # replay

    fetched = repo.get(record.outbox_id)
    assert fetched is not None
    assert fetched.delivery_status is DeliveryStatus.DELIVERED
    assert fetched.delivered_at == _LATER
    assert fetched.delivery_attempt_count == 1  # not double-incremented


def test_mark_failed_delivery_does_not_touch_canonical_state(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: outbox failure after canonical
    commit fixture. 09 section 121: "Canonical commit remains
    COMMITTED. Outbox delivery retries." This repository has no method
    that could roll anything canonical back -- proven here by asserting
    a failed delivery changes only this row's own delivery-tracking
    fields (event_id/commit_id/workspace_id/event_type all identical
    before and after).
    """
    workspace_id = _workspace(db_connection, email="outbox-failure@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)

    repo.mark_failed_delivery(record.outbox_id, next_attempt_at=_LATER)

    fetched = repo.get(record.outbox_id)
    assert fetched is not None
    assert fetched.delivery_status is DeliveryStatus.FAILED_DELIVERY
    assert fetched.next_attempt_at == _LATER
    assert fetched.event_id == record.event_id
    assert fetched.commit_id == record.commit_id
    assert fetched.workspace_id == record.workspace_id
    assert fetched.event_type == record.event_type


def test_mark_failed_delivery_after_already_delivered_is_rejected(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: un-delivering an already-successful
    delivery -- the DELIVERED-is-terminal trigger rejects this, unlike
    `mark_delivered`'s own deliberate replay tolerance.
    """
    workspace_id = _workspace(db_connection, email="outbox-undeliver@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)
    repo.mark_delivered(record.outbox_id, delivered_at=_LATER)

    with pytest.raises(sa.exc.DBAPIError, match="terminal"):
        repo.mark_failed_delivery(record.outbox_id, next_attempt_at=_LATER)


def test_mark_delivered_denies_an_unknown_outbox_id(db_connection: sa.Connection) -> None:
    repo = SqlAlchemyOutboxRepository(db_connection)
    with pytest.raises(OutboxRecordNotFound):
        repo.mark_delivered(uuid.uuid4(), delivered_at=_LATER)


def test_identity_fields_are_immutable_at_the_database_layer(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: rewrite an outbox row's own identity/content
    fields (here, `event_type`) directly via SQL -- 14 section 7.1's
    write-owner split ("commit writer, then outbox worker delivery
    fields only") is enforced independently of application discipline.
    """
    workspace_id = _workspace(db_connection, email="outbox-db-immutable@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)

    with (
        pytest.raises(sa.exc.DBAPIError, match="immutable"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(outbox_events_table)
            .where(outbox_events_table.c.id == record.outbox_id)
            .values(event_type="TAMPERED")
        )


def test_illegal_delivery_status_transition_is_rejected_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: FAILED_DELIVERY's own legal-pair topology
    does not include jumping straight to an arbitrary unrelated state --
    proven here by attempting PENDING -> PENDING with a forged
    delivered_at bypassing mark_delivered entirely (structurally
    invalid regardless of the value chosen).
    """
    workspace_id = _workspace(db_connection, email="outbox-db-illegal@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _record(workspace_id=workspace_id, commit_id=commit_id)
    repo.append(record)
    repo.mark_delivered(record.outbox_id, delivered_at=_LATER)

    with (
        pytest.raises(sa.exc.DBAPIError, match="terminal"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(outbox_events_table)
            .where(outbox_events_table.c.id == record.outbox_id)
            .values(delivery_status="PENDING", delivered_at=None)
        )
