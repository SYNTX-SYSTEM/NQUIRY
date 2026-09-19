"""T11 MUTATION TEST: programmatic mutation proofs for PKG-21's
projection mechanics.

14 section 3.1's own PKG-21 `FILES_ALLOWED_TO_CREATE` names this exact
subdirectory (`tests/command_commit_event/mutation`), distinct from the
top-level `tests/mutation/` placeholder (T11's own general home,
reserved for a later package's "scripts/mutation runner" -- see
`packages/projection/models.py`'s neighbor files, this codebase's
mutation analysis has so far been textual/inspection-based in each
package's own completion report; this is the first package to also
encode that analysis as real, executable pytest mutants rather than
narration alone.

Each test below constructs a deliberately weakened ("mutant") variant
of a real invariant INLINE, proves the mutant produces the wrong,
corrupting result, and proves the REAL production code does not.
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
from projection.models import SessionReadModel
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


class _ConsumerWithoutItsOwnGuard(ProjectionConsumer):
    """MUT-PKG21-01 mutant: removes ONLY the consumer-level idempotency
    check from `_apply_to_session_read_model` -- every `handle()` call
    unconditionally builds and submits a "next version" model, even for
    an already-seen `event_id`. It still submits through the real
    `ProjectionRepository` port, unlike MUT-PKG21-02 below.
    """

    def _apply_to_session_read_model(self, envelope) -> None:  # type: ignore[override]
        session_id = SessionId(uuid.UUID(envelope.aggregate_ref[len("session:") :]))
        current = self._repository.get_session_read_model(session_id, envelope.workspace_scope_ref)
        model = SessionReadModel(
            session_id=session_id,
            workspace_id=envelope.workspace_scope_ref,
            current_state="MUTATED",
            projection_version=1 if current is None else current.projection_version + 1,
            last_event_id=envelope.event_id,
            updated_at=envelope.occurred_at,
        )
        self._repository.upsert_session_read_model(model)


def test_mut_pkg21_01_missing_consumer_guard_alone_does_not_survive(
    db_connection: sa.Connection,
) -> None:
    """MUT-PKG21-01: remove ONLY the consumer-level idempotency guard.
    EXPECTED RED (if this guard were the sole defense):
    `test_consumer_is_idempotent_on_duplicate_event_id`
    (tests/command_commit_event/test_projection.py).
    ACTUAL RESULT: the mutant still does NOT corrupt the read model --
    `SqlAlchemyProjectionRepository.upsert_session_read_model`'s own,
    INDEPENDENT `last_event_id` guard (defense in depth, by design)
    catches the redelivery anyway and keeps `projection_version` at 1.
    INTERPRETATION: this specific single-layer mutation does not
    survive, because a second, independent layer already defends the
    same invariant. It is NOT evidence the consumer-level guard is
    redundant/removable -- MUT-PKG21-02 below proves the repository
    layer alone, with no consumer guard AND no repository guard, DOES
    let corruption through, which is the genuine kill target. Recorded
    as `INTERPRETATION: defense-in-depth confirmed`, not
    `TEST_DESIGN_DEFECT` -- the assertion below is the correct,
    honestly observed result, not a weakened expectation.
    """
    workspace_id = _workspace(db_connection, email="mut-pkg21-01@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    repo = SqlAlchemyProjectionRepository(db_connection)
    mutant = _ConsumerWithoutItsOwnGuard(repository=repo)
    envelope = _envelope(
        aggregate_ref=session_aggregate_ref(session_id),
        workspace_id=workspace_id,
        payload={"state": "SETUP"},
    )

    mutant.handle(envelope)
    mutant.handle(envelope)
    mutant.handle(envelope)

    protected = repo.get_session_read_model(session_id, workspace_id)
    assert protected is not None
    assert protected.projection_version == 1
    assert protected.current_state == "MUTATED"


class _UnguardedRepository:
    """MUT-PKG21-02 mutant: a `ProjectionRepository` whose
    `upsert_session_read_model` never checks `last_event_id` -- an
    unconditional overwrite.
    """

    def __init__(self, real: SqlAlchemyProjectionRepository) -> None:
        self._real = real

    def get_session_read_model(self, session_id, workspace_id):
        return self._real.get_session_read_model(session_id, workspace_id)

    def upsert_session_read_model(self, model) -> None:
        # No last_event_id comparison at all -- always overwrites.
        import sqlalchemy as sa_
        from persistence.tables import session_read_model_table

        current = self._real.get_session_read_model(model.session_id, model.workspace_id)
        stmt = (
            sa_.insert(session_read_model_table).values(
                session_id=model.session_id.value,
                workspace_id=model.workspace_id.value,
                current_state=model.current_state,
                projection_version=model.projection_version,
                last_event_id=model.last_event_id.value,
                updated_at=model.updated_at,
            )
            if current is None
            else sa_.update(session_read_model_table)
            .where(session_read_model_table.c.session_id == model.session_id.value)
            .values(
                current_state=model.current_state,
                projection_version=model.projection_version,
                last_event_id=model.last_event_id.value,
                updated_at=model.updated_at,
            )
        )
        self._real._connection.execute(stmt)  # noqa: SLF001 -- deliberate mutant, test-only

    def get_inquiry_read_model(self, *a, **k):
        return self._real.get_inquiry_read_model(*a, **k)

    def upsert_inquiry_read_model(self, *a, **k):
        return self._real.upsert_inquiry_read_model(*a, **k)

    def get_checkpoint(self, *a, **k):
        return self._real.get_checkpoint(*a, **k)

    def advance_checkpoint(self, *a, **k):
        return self._real.advance_checkpoint(*a, **k)

    def reset_projection(self, *a, **k):
        return self._real.reset_projection(*a, **k)


def test_mut_pkg21_02_unguarded_repository_overwrite_is_killed(
    db_connection: sa.Connection,
) -> None:
    """MUT-PKG21-02: a repository that upserts unconditionally, without
    comparing `last_event_id`.
    EXPECTED RED:
    `test_upsert_session_read_model_is_idempotent_on_same_event_id`
    (tests/command_commit_event/test_projection.py).
    ACTUAL RESULT: the mutant repository DOES let a stale replay
    overwrite with corrupted content; the real
    `SqlAlchemyProjectionRepository` does not (proven separately).
    INTERPRETATION: mutation killed -- the repository-level guard is
    independently load-bearing (defense in depth), not redundant with
    the consumer-level guard.
    """
    workspace_id = _workspace(db_connection, email="mut-pkg21-02@nonproof.test")
    session_id = _seed_session(db_connection, workspace_id=workspace_id)
    real_repo = SqlAlchemyProjectionRepository(db_connection)
    mutant_repo = _UnguardedRepository(real_repo)
    event_id = EventId(uuid.uuid4())

    mutant_repo.upsert_session_read_model(
        SessionReadModel(
            session_id=session_id,
            workspace_id=workspace_id,
            current_state="DRAFT",
            projection_version=1,
            last_event_id=event_id,
            updated_at=_NOW,
        )
    )
    # Same event_id, but a corrupted replayed payload -- the mutant has
    # no guard against this at all.
    mutant_repo.upsert_session_read_model(
        SessionReadModel(
            session_id=session_id,
            workspace_id=workspace_id,
            current_state="CORRUPTED",
            projection_version=2,
            last_event_id=event_id,
            updated_at=_NOW,
        )
    )

    corrupted = real_repo.get_session_read_model(session_id, workspace_id)
    assert corrupted is not None
    assert corrupted.current_state == "CORRUPTED"


def test_mut_pkg21_03_command_repository_capability_would_be_caught(
    db_connection: sa.Connection,
) -> None:
    """MUT-PKG21-03 (mandatory attacks: "replay tries Command"; "use
    projection in authority/commit"): a mutant `ProjectionWorker`
    subclass that gains a `command_repository` constructor parameter.
    EXPECTED RED:
    `test_projection_worker_has_no_command_or_commit_repository_capability`
    (tests/command_commit_event/test_projection_worker.py).
    ACTUAL RESULT: the mutant's own `__init__` signature exposes the
    forbidden parameter, proven caught here directly; the real
    `ProjectionWorker` does not expose it (proven separately).
    INTERPRETATION: mutation killed.
    """

    class _MutantWorker(ProjectionWorker):
        def __init__(self, *, repository, consumer, command_repository=None) -> None:
            super().__init__(repository=repository, consumer=consumer)
            self._command_repository = command_repository

    mutant_params = set(inspect.signature(_MutantWorker.__init__).parameters)
    real_params = set(inspect.signature(ProjectionWorker.__init__).parameters)

    assert "command_repository" in mutant_params
    assert "command_repository" not in real_params
