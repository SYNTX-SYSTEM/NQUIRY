"""T7/T11 PROJECTION WORKER TEST: ProjectionWorker rebuild/replay, against
real PostgreSQL and the real `SqlAlchemyProjectionRepository`.

14 section 48/50's own PKG-21 scope: `apps/worker/src/nquiry_worker/
projection_worker.py`. Every DB-backed test here seeds a real `sessions`
row first, the same pattern `test_projection.py` already established
(the composite FK from `session_read_model.session_id` requires it).
"""

from __future__ import annotations

import inspect
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from events.envelope import build_event_envelope
from nquiry_worker.projection_worker import ProjectionWorker
from persistence.projection_repository import SqlAlchemyProjectionRepository
from persistence.tables import challenges_table, sessions_table
from projection.consumer import ProjectionConsumer, session_aggregate_ref
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


def _envelope(*, aggregate_ref: str, workspace_id: WorkspaceId, payload: object):
    return build_event_envelope(
        event_id=EventId(uuid.uuid4()),
        event_type="CMD_TEST_OPERATION_COMMITTED",
        event_schema_version=_SCHEMA_VERSION,
        occurred_at=_NOW,
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


def _worker(
    db_connection: sa.Connection,
) -> tuple[ProjectionWorker, SqlAlchemyProjectionRepository]:
    repo = SqlAlchemyProjectionRepository(db_connection)
    consumer = ProjectionConsumer(repository=repo)
    return ProjectionWorker(repository=repo, consumer=consumer), repo


def test_apply_batch_applies_in_order_and_advances_checkpoints_per_projection(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _workspace(db_connection, email="projection-worker-batch@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    worker, repo = _worker(db_connection)

    envelopes = [
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"state": "SETUP"},
        ),
        _envelope(aggregate_ref="question:1", workspace_id=workspace_id, payload={"text": "a"}),
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"state": "CHALLENGE_CAPTURE"},
        ),
    ]

    result = worker.apply_batch(envelopes, workspace_id=workspace_id)

    assert result.applied_event_ids == tuple(e.event_id.value for e in envelopes)
    session_checkpoint = repo.get_checkpoint("session_read_model", workspace_id)
    inquiry_checkpoint = repo.get_checkpoint("inquiry_read_model", workspace_id)
    assert session_checkpoint is not None and session_checkpoint.checkpoint_version == 2
    assert inquiry_checkpoint is not None and inquiry_checkpoint.checkpoint_version == 1
    model = repo.get_session_read_model(session_id, workspace_id)
    assert model is not None
    assert model.current_state == "CHALLENGE_CAPTURE"


def test_rebuild_wipes_and_replays_to_identical_state(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: delete projection then rebuild."""
    workspace_id = _workspace(db_connection, email="projection-worker-rebuild@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    worker, repo = _worker(db_connection)

    envelopes = [
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"state": "SETUP"},
        ),
        _envelope(
            aggregate_ref=session_aggregate_ref(session_id),
            workspace_id=workspace_id,
            payload={"state": "CHALLENGE_CAPTURE"},
        ),
    ]
    worker.apply_batch(envelopes, workspace_id=workspace_id)
    original = repo.get_session_read_model(session_id, workspace_id)
    assert original is not None

    result = worker.rebuild(
        envelopes, projection_name="session_read_model", workspace_id=workspace_id
    )

    rebuilt = repo.get_session_read_model(session_id, workspace_id)
    assert rebuilt == original
    assert result.applied_event_ids == tuple(e.event_id.value for e in envelopes)


def test_replay_of_the_full_history_twice_does_not_duplicate(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: replay twice."""
    workspace_id = _workspace(db_connection, email="projection-worker-replay-twice@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    worker, repo = _worker(db_connection)

    envelope = _envelope(
        aggregate_ref=session_aggregate_ref(session_id),
        workspace_id=workspace_id,
        payload={"state": "SETUP"},
    )

    worker.apply_batch([envelope], workspace_id=workspace_id)
    worker.apply_batch([envelope], workspace_id=workspace_id)

    model = repo.get_session_read_model(session_id, workspace_id)
    assert model is not None
    assert model.projection_version == 1
    assert model.current_state == "SETUP"


def test_projection_worker_has_no_command_or_commit_repository_capability() -> None:
    """Mandatory adversarial attacks: replay tries Command; use
    projection in authority/commit. Structural proof mirroring
    `OutboxWorker`'s own "no domain mutation capability" check
    (PKG-20): neither `ProjectionWorker.__init__` nor `apply_batch`/
    `rebuild` has any parameter through which a Command/Commit
    repository, coordinator, or AuthorityResolver could be supplied at
    all.
    """
    forbidden = {
        "command_repository",
        "commit_repository",
        "commit_coordinator",
        "coordinator",
        "authority_resolver",
    }
    init_params = set(inspect.signature(ProjectionWorker.__init__).parameters)
    apply_params = set(inspect.signature(ProjectionWorker.apply_batch).parameters)
    rebuild_params = set(inspect.signature(ProjectionWorker.rebuild).parameters)
    assert not forbidden & init_params
    assert not forbidden & apply_params
    assert not forbidden & rebuild_params
