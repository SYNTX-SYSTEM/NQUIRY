"""T7 PROJECTION TEST: SessionReadModel/InquiryReadModel/ProjectionCheckpoint,
SqlAlchemyProjectionRepository and ProjectionConsumer, against real
PostgreSQL where noted.

14 section 48's own file-level implementation map assigns
`tests/command_commit_event/test_projection.py` to
`packages/projection/consumer.py`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from events.envelope import build_event_envelope
from persistence.projection_repository import SqlAlchemyProjectionRepository
from persistence.tables import challenges_table, sessions_table
from projection.consumer import (
    INQUIRY_PROJECTION_NAME,
    SESSION_PROJECTION_NAME,
    ProjectionConsumer,
    projection_name_for,
    session_aggregate_ref,
)
from projection.models import InquiryReadModel, ProjectionCheckpoint, SessionReadModel
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    SessionId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_SCHEMA_VERSION = ContractVersion("1.0")


def _workspace(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    return bootstrap.seed(owner_email=email).workspace_id


def _seed_session(db_connection: sa.Connection, *, workspace_id: WorkspaceId) -> SessionId:
    """A real Session, left in its legal initial state (`DRAFT`) --
    projection purposes need only a real, FK-satisfiable row, not any
    particular downstream state.
    """
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=workspace_id.value,
            title="Onboarding drop-off",
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
    session_id = SessionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=1,
        )
    )
    return session_id


def _envelope(
    *,
    aggregate_ref: str,
    workspace_id: WorkspaceId,
    payload: object,
    event_id: EventId | None = None,
    occurred_at: datetime = _NOW,
):
    return build_event_envelope(
        event_id=event_id or EventId(uuid.uuid4()),
        event_type="CMD_TEST_OPERATION_COMMITTED",
        event_schema_version=_SCHEMA_VERSION,
        occurred_at=occurred_at,
        workspace_scope_ref=workspace_id,
        aggregate_ref=aggregate_ref,
        aggregate_version_after_commit=RecordVersion(1),
        command_id=CommandId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        actor_ref="HUMAN_USER:user-ref-1",
        authority_source_ref=uuid.uuid4(),
        payload=payload,
    )


# ---------------------------------------------------------------------------
# Models (no database)
# ---------------------------------------------------------------------------


def test_session_read_model_denies_empty_current_state() -> None:
    with pytest.raises(ValueError, match="current_state"):
        SessionReadModel(
            session_id=SessionId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            current_state="",
            projection_version=1,
            last_event_id=EventId(uuid.uuid4()),
            updated_at=_NOW,
        )


def test_session_read_model_denies_projection_version_below_one() -> None:
    with pytest.raises(ValueError, match="projection_version"):
        SessionReadModel(
            session_id=SessionId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            current_state="DRAFT",
            projection_version=0,
            last_event_id=EventId(uuid.uuid4()),
            updated_at=_NOW,
        )


def test_inquiry_read_model_denies_empty_aggregate_ref() -> None:
    with pytest.raises(ValueError, match="aggregate_ref"):
        InquiryReadModel(
            id=uuid.uuid4(),
            aggregate_ref="",
            workspace_id=WorkspaceId(uuid.uuid4()),
            projection_version=1,
            snapshot={},
            last_event_id=EventId(uuid.uuid4()),
            updated_at=_NOW,
        )


def test_projection_checkpoint_denies_negative_version() -> None:
    with pytest.raises(ValueError, match="checkpoint_version"):
        ProjectionCheckpoint(
            projection_name="session_read_model",
            workspace_id=WorkspaceId(uuid.uuid4()),
            checkpoint_version=-1,
            updated_at=_NOW,
        )


def test_session_aggregate_ref_format() -> None:
    session_id = SessionId(uuid.uuid4())
    assert session_aggregate_ref(session_id) == f"session:{session_id.value}"


def test_projection_name_for_dispatches_session_shaped_refs() -> None:
    session_envelope = _envelope(
        aggregate_ref=session_aggregate_ref(SessionId(uuid.uuid4())),
        workspace_id=WorkspaceId(uuid.uuid4()),
        payload={"state": "DRAFT"},
    )
    generic_envelope = _envelope(
        aggregate_ref="question:1", workspace_id=WorkspaceId(uuid.uuid4()), payload={}
    )

    assert projection_name_for(session_envelope) == SESSION_PROJECTION_NAME
    assert projection_name_for(generic_envelope) == INQUIRY_PROJECTION_NAME


# ---------------------------------------------------------------------------
# SqlAlchemyProjectionRepository (real PostgreSQL)
# ---------------------------------------------------------------------------


def test_upsert_session_read_model_creates_then_updates(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="projection-session-crud@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)

    first = SessionReadModel(
        session_id=session_id,
        workspace_id=workspace_id,
        current_state="DRAFT",
        projection_version=1,
        last_event_id=EventId(uuid.uuid4()),
        updated_at=_NOW,
    )
    repo.upsert_session_read_model(first)
    assert repo.get_session_read_model(session_id, workspace_id) == first

    second = SessionReadModel(
        session_id=session_id,
        workspace_id=workspace_id,
        current_state="SETUP",
        projection_version=2,
        last_event_id=EventId(uuid.uuid4()),
        updated_at=_NOW,
    )
    repo.upsert_session_read_model(second)
    assert repo.get_session_read_model(session_id, workspace_id) == second


def test_upsert_session_read_model_is_idempotent_on_same_event_id(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="projection-session-idempotent@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)
    event_id = EventId(uuid.uuid4())
    model = SessionReadModel(
        session_id=session_id,
        workspace_id=workspace_id,
        current_state="DRAFT",
        projection_version=1,
        last_event_id=event_id,
        updated_at=_NOW,
    )
    repo.upsert_session_read_model(model)

    # Redelivery of the SAME event, claiming a different state -- must
    # be a safe no-op, not a second effect (09 section 15.2).
    replay_attempt = SessionReadModel(
        session_id=session_id,
        workspace_id=workspace_id,
        current_state="CORRUPTED",
        projection_version=2,
        last_event_id=event_id,
        updated_at=_NOW,
    )
    repo.upsert_session_read_model(replay_attempt)

    assert repo.get_session_read_model(session_id, workspace_id) == model


def test_session_read_model_rejects_cross_workspace_corruption(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: corrupt projection. A
    `SessionReadModel` claiming a Workspace that does not match the
    real Session's own Workspace is rejected by the real composite
    foreign key, not merely by application convention.
    """
    real_workspace_id = _workspace(db_connection, email="projection-corrupt-real@nonproof.test")
    other_workspace_id = _workspace(db_connection, email="projection-corrupt-other@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=real_workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)

    forged = SessionReadModel(
        session_id=session_id,
        workspace_id=other_workspace_id,  # does not match the real Session's Workspace
        current_state="DRAFT",
        projection_version=1,
        last_event_id=EventId(uuid.uuid4()),
        updated_at=_NOW,
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repo.upsert_session_read_model(forged)


def test_upsert_inquiry_read_model_creates_then_updates(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="projection-inquiry-crud@nonproof.test")
    repo = SqlAlchemyProjectionRepository(db_connection)
    aggregate_ref = "question:1"

    first = InquiryReadModel(
        id=uuid.uuid4(),
        aggregate_ref=aggregate_ref,
        workspace_id=workspace_id,
        projection_version=1,
        snapshot={"text": "hello"},
        last_event_id=EventId(uuid.uuid4()),
        updated_at=_NOW,
    )
    repo.upsert_inquiry_read_model(first)
    assert repo.get_inquiry_read_model(aggregate_ref, workspace_id) == first

    second = InquiryReadModel(
        id=first.id,
        aggregate_ref=aggregate_ref,
        workspace_id=workspace_id,
        projection_version=2,
        snapshot={"text": "updated"},
        last_event_id=EventId(uuid.uuid4()),
        updated_at=_NOW,
    )
    repo.upsert_inquiry_read_model(second)
    assert repo.get_inquiry_read_model(aggregate_ref, workspace_id) == second


def test_checkpoint_advances_monotonically(db_connection: sa.Connection) -> None:
    workspace_id = _workspace(db_connection, email="projection-checkpoint@nonproof.test")
    repo = SqlAlchemyProjectionRepository(db_connection)

    assert repo.get_checkpoint("session_read_model", workspace_id) is None

    first_event_id = EventId(uuid.uuid4())
    repo.advance_checkpoint(
        "session_read_model", workspace_id, last_processed_event_id=first_event_id
    )
    checkpoint = repo.get_checkpoint("session_read_model", workspace_id)
    assert checkpoint is not None
    assert checkpoint.checkpoint_version == 1
    assert checkpoint.last_processed_event_id == first_event_id

    second_event_id = EventId(uuid.uuid4())
    repo.advance_checkpoint(
        "session_read_model", workspace_id, last_processed_event_id=second_event_id
    )
    checkpoint = repo.get_checkpoint("session_read_model", workspace_id)
    assert checkpoint is not None
    assert checkpoint.checkpoint_version == 2
    assert checkpoint.last_processed_event_id == second_event_id


# ---------------------------------------------------------------------------
# ProjectionConsumer (real PostgreSQL)
# ---------------------------------------------------------------------------


def test_consumer_dispatches_session_shaped_envelope_to_session_read_model(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="projection-consumer-session@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)
    consumer = ProjectionConsumer(repository=repo)

    envelope = _envelope(
        aggregate_ref=session_aggregate_ref(session_id),
        workspace_id=workspace_id,
        payload={"state": "SETUP"},
    )
    consumer.handle(envelope)

    model = repo.get_session_read_model(session_id, workspace_id)
    assert model is not None
    assert model.current_state == "SETUP"
    assert model.last_event_id == envelope.event_id
    assert repo.get_inquiry_read_model(envelope.aggregate_ref, workspace_id) is None


def test_consumer_dispatches_generic_envelope_to_inquiry_read_model(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="projection-consumer-inquiry@nonproof.test")
    repo = SqlAlchemyProjectionRepository(db_connection)
    consumer = ProjectionConsumer(repository=repo)

    envelope = _envelope(
        aggregate_ref="question:1", workspace_id=workspace_id, payload={"text": "hello"}
    )
    consumer.handle(envelope)

    model = repo.get_inquiry_read_model("question:1", workspace_id)
    assert model is not None
    assert model.snapshot == {"text": "hello"}
    assert model.last_event_id == envelope.event_id


def test_consumer_is_idempotent_on_duplicate_event_id(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: replay twice."""
    workspace_id = _workspace(db_connection, email="projection-consumer-replay@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)
    consumer = ProjectionConsumer(repository=repo)

    envelope = _envelope(
        aggregate_ref=session_aggregate_ref(session_id),
        workspace_id=workspace_id,
        payload={"state": "SETUP"},
    )
    consumer.handle(envelope)
    consumer.handle(envelope)
    consumer.handle(envelope)

    model = repo.get_session_read_model(session_id, workspace_id)
    assert model is not None
    assert model.projection_version == 1


def test_consumer_preserves_state_when_payload_has_no_state_key(
    db_connection: sa.Connection,
) -> None:
    """A payload carrying no recognizable state information never
    invents one -- the read model keeps whatever it already projected.
    """
    workspace_id = _workspace(db_connection, email="projection-consumer-partial@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)
    consumer = ProjectionConsumer(repository=repo)

    consumer.handle(
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"state": "SETUP"},
        )
    )
    consumer.handle(
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"unrelated": "field"},
        )
    )

    model = repo.get_session_read_model(session_id, workspace_id)
    assert model is not None
    assert model.current_state == "SETUP"
    assert model.projection_version == 2
