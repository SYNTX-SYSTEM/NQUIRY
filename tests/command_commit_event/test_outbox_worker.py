"""T7 OUTBOX WORKER TEST: OutboxWorker delivery loop, against real
PostgreSQL and the real `SqlAlchemyOutboxRepository`.

14 section 48/50's own PKG-20 scope: `apps/worker/src/nquiry_worker/
outbox_worker.py`. Every DB-backed test here records a real
`commit_units` row first, the same pattern `test_outbox.py`/
`test_audit.py` already established (the composite FK from
`outbox_events.commit_id` to `commit_units` requires it).
"""

from __future__ import annotations

import inspect
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from events.envelope import build_event_envelope
from events.outbox import DeliveryStatus, OutboxRecord
from nquiry_worker.outbox_worker import OutboxWorker
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import commit_units_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.event_doubles import (
    RecordingIdempotentConsumer,
    ScriptedEventPublisher,
    StaticEventEnvelopeSource,
)
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
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


def _seed_outbox_record(
    repo: SqlAlchemyOutboxRepository,
    *,
    workspace_id: WorkspaceId,
    commit_id: CommitId,
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING,
    next_attempt_at: datetime | None = None,
) -> OutboxRecord:
    record = OutboxRecord(
        outbox_id=uuid.uuid4(),
        event_id=EventId(uuid.uuid4()),
        workspace_id=workspace_id,
        commit_id=commit_id,
        event_type="CMD_TEST_OPERATION_COMMITTED",
        created_at=_NOW,
        delivery_status=DeliveryStatus.PENDING,
        delivery_attempt_count=0,
    )
    repo.append(record)
    if delivery_status is not DeliveryStatus.PENDING:
        # Move the freshly-appended row into the desired starting state
        # via the same repository methods a real worker would use, not
        # a raw UPDATE -- proves the fixture itself only reaches
        # reachable states.
        repo.mark_failed_delivery(
            record.outbox_id, next_attempt_at=next_attempt_at or _NOW - timedelta(minutes=1)
        )
    return repo.get(record.outbox_id)  # type: ignore[return-value]


def _envelope_for(record: OutboxRecord, *, workspace_id: WorkspaceId):
    return build_event_envelope(
        event_id=record.event_id,
        event_type=record.event_type,
        event_schema_version=ContractVersion("1.0"),
        occurred_at=_NOW,
        workspace_scope_ref=workspace_id,
        aggregate_ref="session:1",
        aggregate_version_after_commit=RecordVersion(1),
        command_id=CommandId(uuid.uuid4()),
        commit_id=record.commit_id,
        correlation_id=CorrelationId(uuid.uuid4()),
        actor_ref="HUMAN_USER:user-ref-1",
        authority_source_ref=uuid.uuid4(),
        payload={"note": "hello"},
    )


def test_delivers_a_pending_record_and_marks_it_delivered(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="outbox-worker-success@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _seed_outbox_record(repo, workspace_id=workspace_id, commit_id=commit_id)
    envelope = _envelope_for(record, workspace_id=workspace_id)

    publisher = ScriptedEventPublisher()
    worker = OutboxWorker(
        outbox_repository=repo,
        envelope_source=StaticEventEnvelopeSource({record.outbox_id: envelope}),
        publisher=publisher,
        clock=FixedClock(_NOW),
    )

    result = worker.deliver_due()

    assert result.delivered == (record.outbox_id,)
    assert result.failed == ()
    assert publisher.published == [envelope]
    stored = repo.get(record.outbox_id)
    assert stored is not None
    assert stored.delivery_status is DeliveryStatus.DELIVERED
    assert stored.delivered_at is not None


def test_delivery_failure_marks_failed_delivery_without_touching_canonical_state(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="outbox-worker-failure@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _seed_outbox_record(repo, workspace_id=workspace_id, commit_id=commit_id)
    envelope = _envelope_for(record, workspace_id=workspace_id)

    publisher = ScriptedEventPublisher(fail_for_event_ids=frozenset({envelope.event_id.value}))
    clock = FixedClock(_NOW)
    worker = OutboxWorker(
        outbox_repository=repo,
        envelope_source=StaticEventEnvelopeSource({record.outbox_id: envelope}),
        publisher=publisher,
        clock=clock,
    )

    result = worker.deliver_due(retry_backoff_seconds=120)

    assert result.failed == (record.outbox_id,)
    assert result.delivered == ()
    stored = repo.get(record.outbox_id)
    assert stored is not None
    assert stored.delivery_status is DeliveryStatus.FAILED_DELIVERY
    assert stored.next_attempt_at == _NOW + timedelta(seconds=120)

    # AC-09-010: broker/delivery failure never rolls back already
    # COMMITTED canonical state.
    row = db_connection.execute(
        sa.select(commit_units_table.c.outcome).where(commit_units_table.c.id == commit_id.value)
    ).scalar_one()
    assert row == CommitOutcome.COMMITTED.value


def test_worker_restart_resumes_and_completes_a_previously_failed_delivery(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: worker restart. A record left
    FAILED_DELIVERY (with a now-past `next_attempt_at`) by a crashed
    prior worker instance is picked up and completed by a brand-new
    `OutboxWorker` object that never saw the earlier attempt --
    resumable state lives entirely in the durable row, never in worker
    memory. Deterministic RC-01 recovery, no new domain choice.
    """
    workspace_id = _workspace(db_connection, email="outbox-worker-restart@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _seed_outbox_record(
        repo,
        workspace_id=workspace_id,
        commit_id=commit_id,
        delivery_status=DeliveryStatus.FAILED_DELIVERY,
        next_attempt_at=_NOW - timedelta(minutes=1),
    )
    assert record.delivery_attempt_count == 1
    envelope = _envelope_for(record, workspace_id=workspace_id)

    # A brand-new `OutboxWorker` instance -- it never saw the crashed
    # prior attempt, only the durable row.
    fresh_worker = OutboxWorker(
        outbox_repository=repo,
        envelope_source=StaticEventEnvelopeSource({record.outbox_id: envelope}),
        publisher=ScriptedEventPublisher(),
        clock=FixedClock(_NOW),
    )

    result = fresh_worker.deliver_due()

    assert result.delivered == (record.outbox_id,)
    stored = repo.get(record.outbox_id)
    assert stored is not None
    assert stored.delivery_status is DeliveryStatus.DELIVERED
    assert stored.delivery_attempt_count == 2


def test_an_already_delivered_record_is_never_redelivered(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="outbox-worker-no-redeliver@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _seed_outbox_record(repo, workspace_id=workspace_id, commit_id=commit_id)
    envelope = _envelope_for(record, workspace_id=workspace_id)
    publisher = ScriptedEventPublisher()
    worker = OutboxWorker(
        outbox_repository=repo,
        envelope_source=StaticEventEnvelopeSource({record.outbox_id: envelope}),
        publisher=publisher,
        clock=FixedClock(_NOW),
    )

    worker.deliver_due()
    second_result = worker.deliver_due()

    assert second_result.delivered == ()
    assert second_result.failed == ()
    assert publisher.published == [envelope]


def test_list_due_for_delivery_excludes_a_future_retry(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="outbox-worker-future-retry@nonproof.test")
    commit_id = _record_real_commit(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyOutboxRepository(db_connection)
    record = _seed_outbox_record(
        repo,
        workspace_id=workspace_id,
        commit_id=commit_id,
        delivery_status=DeliveryStatus.FAILED_DELIVERY,
        next_attempt_at=_NOW + timedelta(hours=1),
    )

    due = repo.list_due_for_delivery(now=_NOW)

    assert record.outbox_id not in {r.outbox_id for r in due}


def test_forged_outbox_record_without_a_real_commit_is_rejected(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: forged Event without CommitUnit.
    `outbox_events.commit_id` carries a real composite FK to
    `commit_units` (PKG-13) -- a bare, never-committed `CommitId` is
    rejected at the database layer, not merely by convention.
    """
    workspace_id = _workspace(db_connection, email="outbox-worker-forged@nonproof.test")
    repo = SqlAlchemyOutboxRepository(db_connection)
    forged_record = OutboxRecord(
        outbox_id=uuid.uuid4(),
        event_id=EventId(uuid.uuid4()),
        workspace_id=workspace_id,
        commit_id=CommitId(uuid.uuid4()),  # never committed
        event_type="FORGED_EVENT",
        created_at=_NOW,
        delivery_status=DeliveryStatus.PENDING,
        delivery_attempt_count=0,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.append(forged_record)


def test_duplicate_delivery_to_an_idempotent_consumer_applies_the_effect_once() -> None:
    """09 section 15.2: "consumers must assume duplicate event delivery
    is possible ... must not produce duplicate consequential effects
    solely because delivery repeats." Proven directly against the
    reference idempotent consumer, keyed by the envelope's own durable
    `event_id`, not by call count.
    """
    envelope = build_event_envelope(
        event_id=EventId(uuid.uuid4()),
        event_type="SESSION_TRANSITIONED",
        event_schema_version=ContractVersion("1.0"),
        occurred_at=_NOW,
        workspace_scope_ref=WorkspaceId(uuid.uuid4()),
        aggregate_ref="session:1",
        aggregate_version_after_commit=RecordVersion(1),
        command_id=CommandId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        actor_ref="HUMAN_USER:user-ref-1",
        authority_source_ref=uuid.uuid4(),
        payload={"note": "hello"},
    )
    consumer = RecordingIdempotentConsumer()

    consumer.handle(envelope)
    consumer.handle(envelope)
    consumer.handle(envelope)

    assert consumer.effects_applied == [envelope]
    assert consumer.duplicate_deliveries_ignored == 2


def test_outbox_worker_has_no_command_or_commit_repository_capability() -> None:
    """Mandatory adversarial attack: outbox retry interpreted as
    command retry. Structural proof mirroring `AIGateway`'s own "no
    domain mutation capability" check (PKG-19): `OutboxWorker`'s entire
    constructor surface has no parameter through which a command/commit
    repository -- or any other canonical writer -- could be supplied at
    all.
    """
    params = set(inspect.signature(OutboxWorker.__init__).parameters)
    forbidden = {"command_repository", "commit_repository", "commit_coordinator", "coordinator"}
    assert not forbidden & params
