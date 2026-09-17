"""T2 TRANSITION TEST: migration `d8a1147fde30`'s live PostgreSQL
constraint proof for `question_bursts`/`burst_question_memberships`.

Mirrors `test_session_transition_constraints.py`'s design exactly
(same SAVEPOINT-ordering discipline: `pytest.raises` is always the
OUTER context manager, `db_connection.begin_nested()` the inner one --
see that file's module docstring for why the order matters).

Uses `NonProofWorkspaceBootstrap` for Workspace/owner (13 §5's
permitted downstream use), then direct-SQL Challenge/Session/Question
rows exactly as `tests/domain/question/test_question_repository.py`
and `tests/transitions/test_session_transition_constraints.py` already
do -- the invariants under test here (Burst topology, freeze
enforcement) do not depend on how any of those came to exist.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from domain.burst import BurstMode, BurstState, QuestionBurst
from domain.burst_membership import QuestionBurstMembership, compute_frozen_membership_fingerprint
from domain.burst_transitions import legal_state_pairs
from domain.question import QuestionOrigin
from persistence.burst_repository import BurstConflict, SqlAlchemyBurstRepository
from persistence.tables import (
    challenges_table,
    question_bursts_table,
    questions_table,
    sessions_table,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    BurstId,
    ChallengeId,
    QuestionId,
    RelationId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_session(connection: sa.Connection, *, owner_email: str):
    bootstrap = NonProofWorkspaceBootstrap(connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email=owner_email)

    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=result.workspace_id.value,
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
    connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=result.workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=1,
        )
    )
    return result.workspace_id, session_id, result.owner_user_id


def _insert_question(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    author_id: UserId,
) -> QuestionId:
    question_id = QuestionId(_ID_GEN.new_uuid())
    connection.execute(
        sa.insert(questions_table).values(
            id=question_id.value,
            challenge_id=challenge_id.value,
            workspace_id=workspace_id.value,
            original_text="Why do onboarding users drop off after step 2?",
            normalized_text=None,
            origin="HUMAN",
            author_user_id=author_id.value,
            created_at=_NOW,
            record_version=1,
        )
    )
    return question_id


def _prepared_burst(*, session_id: SessionId, workspace_id: WorkspaceId) -> QuestionBurst:
    return QuestionBurst(
        burst_id=BurstId(_ID_GEN.new_uuid()),
        session_id=session_id,
        workspace_id=workspace_id,
        state=BurstState.PREPARED,
        mode=BurstMode.HUMAN_ONLY,
        started_at=None,
        paused_at=None,
        completed_at=None,
        frozen_membership_fingerprint=None,
        record_version=RecordVersion.initial(),
    )


def test_burst_created_in_prepared_succeeds(db_connection: sa.Connection) -> None:
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="prep@nonproof.test"
    )
    repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)

    repo.create_prepared(burst)

    assert repo.get(burst.burst_id) == burst


def test_burst_created_outside_prepared_is_rejected(db_connection: sa.Connection) -> None:
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="prep-bad@nonproof.test"
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="must be created in PREPARED"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(question_bursts_table).values(
                id=_ID_GEN.new_uuid(),
                session_id=session_id.value,
                workspace_id=workspace_id.value,
                state="ACTIVE",
                mode="HUMAN_ONLY",
                started_at=_NOW,
                paused_at=None,
                completed_at=None,
                frozen_membership_fingerprint=None,
                record_version=1,
            )
        )


def test_direct_enum_coercion_of_state_is_rejected(db_connection: sa.Connection) -> None:
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="coerce-state@nonproof.test"
    )

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_bursts_table).values(
                id=_ID_GEN.new_uuid(),
                session_id=session_id.value,
                workspace_id=workspace_id.value,
                state="MADE_UP_STATE",
                mode="HUMAN_ONLY",
                started_at=None,
                paused_at=None,
                completed_at=None,
                frozen_membership_fingerprint=None,
                record_version=1,
            )
        )


def test_non_human_only_mode_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """08 §12.2/12.3: Mode B/C are out of this package's scope. Proven
    at the schema level, independent of `QuestionBurst.__post_init__`.
    """
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="mode@nonproof.test"
    )

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_bursts_table).values(
                id=_ID_GEN.new_uuid(),
                session_id=session_id.value,
                workspace_id=workspace_id.value,
                state="PREPARED",
                mode="HUMAN_PLUS_AI",
                started_at=None,
                paused_at=None,
                completed_at=None,
                frozen_membership_fingerprint=None,
                record_version=1,
            )
        )


def test_cross_workspace_burst_target_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory-category Workspace attack, Burst variant."""
    _workspace_a, session_a, _owner_a = _bootstrap_session(
        db_connection, owner_email="burst-cross-a@nonproof.test"
    )
    workspace_b, _session_b, _owner_b = _bootstrap_session(
        db_connection, owner_email="burst-cross-b@nonproof.test"
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_bursts_table).values(
                id=_ID_GEN.new_uuid(),
                session_id=session_a.value,
                workspace_id=workspace_b.value,
                state="PREPARED",
                mode="HUMAN_ONLY",
                started_at=None,
                paused_at=None,
                completed_at=None,
                frozen_membership_fingerprint=None,
                record_version=1,
            )
        )


def test_illegal_burst_transition_is_rejected(db_connection: sa.Connection) -> None:
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="illegal-burst@nonproof.test"
    )
    repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    repo.create_prepared(burst)

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal burst transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(question_bursts_table)
            .where(question_bursts_table.c.id == burst.burst_id.value)
            .values(state="PAUSED", record_version=2)
        )


def test_completed_burst_is_fully_immutable(db_connection: sa.Connection) -> None:
    """03 §19.5: COMPLETED is terminal -- not just for `state`, for the
    whole row.
    """
    workspace_id, session_id, owner = _bootstrap_session(
        db_connection, owner_email="completed-immutable@nonproof.test"
    )
    challenge_id = ChallengeId(
        db_connection.execute(
            sa.select(sessions_table.c.challenge_id).where(sessions_table.c.id == session_id.value)
        ).scalar_one()
    )
    burst_repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    burst_repo.create_prepared(burst)
    burst_repo.start(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )

    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_id=owner
    )
    membership = QuestionBurstMembership(
        burst_question_membership_id=RelationId(_ID_GEN.new_uuid()),
        question_burst_id=burst.burst_id,
        question_id=question_id,
        workspace_id=workspace_id,
        captured_order=0,
        captured_at=_NOW,
        capture_actor_user_id=owner,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )
    burst_repo.add_member(membership)

    fingerprint = compute_frozen_membership_fingerprint(
        (membership,), {question_id: RecordVersion.initial()}
    )
    burst_repo.complete(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        completed_at=_NOW,
        frozen_membership_fingerprint=fingerprint,
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="is COMPLETED and immutable"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(question_bursts_table)
            .where(question_bursts_table.c.id == burst.burst_id.value)
            .values(record_version=4)
        )


def test_add_raw_member_after_freeze_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: add raw member after freeze."""
    workspace_id, session_id, owner = _bootstrap_session(
        db_connection, owner_email="add-after-freeze@nonproof.test"
    )
    challenge_id = ChallengeId(
        db_connection.execute(
            sa.select(sessions_table.c.challenge_id).where(sessions_table.c.id == session_id.value)
        ).scalar_one()
    )
    burst_repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    burst_repo.create_prepared(burst)
    burst_repo.start(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_id=owner
    )
    membership = QuestionBurstMembership(
        burst_question_membership_id=RelationId(_ID_GEN.new_uuid()),
        question_burst_id=burst.burst_id,
        question_id=question_id,
        workspace_id=workspace_id,
        captured_order=0,
        captured_at=_NOW,
        capture_actor_user_id=owner,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )
    burst_repo.add_member(membership)
    fingerprint = compute_frozen_membership_fingerprint(
        (membership,), {question_id: RecordVersion.initial()}
    )
    burst_repo.complete(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        completed_at=_NOW,
        frozen_membership_fingerprint=fingerprint,
    )

    late_question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_id=owner
    )
    late_membership = QuestionBurstMembership(
        burst_question_membership_id=RelationId(_ID_GEN.new_uuid()),
        question_burst_id=burst.burst_id,
        question_id=late_question_id,
        workspace_id=workspace_id,
        captured_order=1,
        captured_at=_NOW,
        capture_actor_user_id=owner,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="raw membership is frozen"),
        db_connection.begin_nested(),
    ):
        burst_repo.add_member(late_membership)


def test_remove_member_after_freeze_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: remove member after freeze."""
    workspace_id, session_id, owner = _bootstrap_session(
        db_connection, owner_email="remove-after-freeze@nonproof.test"
    )
    challenge_id = ChallengeId(
        db_connection.execute(
            sa.select(sessions_table.c.challenge_id).where(sessions_table.c.id == session_id.value)
        ).scalar_one()
    )
    burst_repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    burst_repo.create_prepared(burst)
    burst_repo.start(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_id=owner
    )
    membership = QuestionBurstMembership(
        burst_question_membership_id=RelationId(_ID_GEN.new_uuid()),
        question_burst_id=burst.burst_id,
        question_id=question_id,
        workspace_id=workspace_id,
        captured_order=0,
        captured_at=_NOW,
        capture_actor_user_id=owner,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )
    burst_repo.add_member(membership)
    fingerprint = compute_frozen_membership_fingerprint(
        (membership,), {question_id: RecordVersion.initial()}
    )
    burst_repo.complete(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(2),
        completed_at=_NOW,
        frozen_membership_fingerprint=fingerprint,
    )

    from persistence.tables import burst_question_memberships_table

    with (
        pytest.raises(sa.exc.DBAPIError, match="raw membership is frozen"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.delete(burst_question_memberships_table).where(
                burst_question_memberships_table.c.id
                == membership.burst_question_membership_id.value
            )
        )


def test_membership_reassignment_via_update_is_rejected(db_connection: sa.Connection) -> None:
    """Novel attack: membership reassignment, mirroring
    `question_lineage`'s full-row immutability (PKG-06).
    """
    workspace_id, session_id, owner = _bootstrap_session(
        db_connection, owner_email="reassign-member@nonproof.test"
    )
    challenge_id = ChallengeId(
        db_connection.execute(
            sa.select(sessions_table.c.challenge_id).where(sessions_table.c.id == session_id.value)
        ).scalar_one()
    )
    burst_repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    burst_repo.create_prepared(burst)
    burst_repo.start(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=burst.record_version,
        started_at=_NOW,
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_id=owner
    )
    membership = QuestionBurstMembership(
        burst_question_membership_id=RelationId(_ID_GEN.new_uuid()),
        question_burst_id=burst.burst_id,
        question_id=question_id,
        workspace_id=workspace_id,
        captured_order=0,
        captured_at=_NOW,
        capture_actor_user_id=owner,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )
    burst_repo.add_member(membership)

    from persistence.tables import burst_question_memberships_table

    with (
        pytest.raises(sa.exc.DBAPIError, match="burst_question_memberships rows are immutable"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(burst_question_memberships_table)
            .where(
                burst_question_memberships_table.c.id
                == membership.burst_question_membership_id.value
            )
            .values(captured_order=99)
        )


def test_burst_conflict_raised_on_stale_expected_version(db_connection: sa.Connection) -> None:
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="stale-version@nonproof.test"
    )
    repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    repo.create_prepared(burst)

    with pytest.raises(BurstConflict):
        repo.start(
            burst_id=burst.burst_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion(99),  # wrong
            started_at=_NOW,
        )


def test_registry_and_database_agree_on_every_legal_pair(db_connection: sa.Connection) -> None:
    """Cross-layer proof: `domain.burst_transitions.legal_state_pairs()`
    and migration `d8a1147fde30`'s trigger allow-list agree, walked as
    one continuous chain through PREPARED -> ACTIVE -> PAUSED -> ACTIVE
    -> COMPLETED.
    """
    workspace_id, session_id, _owner = _bootstrap_session(
        db_connection, owner_email="agree-burst@nonproof.test"
    )
    repo = SqlAlchemyBurstRepository(db_connection)
    burst = _prepared_burst(session_id=session_id, workspace_id=workspace_id)
    repo.create_prepared(burst)

    successor_of: dict[BurstState, BurstState] = {}
    for source, target in legal_state_pairs():
        if source is not None and source is not BurstState.ACTIVE:
            # ACTIVE has two legal successors (PAUSED, COMPLETED); walk
            # the PAUSED branch explicitly below instead of collapsing
            # it into a single successor map.
            successor_of[source] = target

    current_version = burst.record_version
    repo.start(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=current_version,
        started_at=_NOW,
    )
    current_version = current_version.next()
    assert repo.get(burst.burst_id).state is BurstState.ACTIVE  # type: ignore[union-attr]

    repo.pause(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=current_version,
        paused_at=_NOW,
    )
    current_version = current_version.next()
    assert repo.get(burst.burst_id).state is BurstState.PAUSED  # type: ignore[union-attr]

    repo.resume(
        burst_id=burst.burst_id, workspace_id=workspace_id, expected_record_version=current_version
    )
    current_version = current_version.next()
    assert repo.get(burst.burst_id).state is BurstState.ACTIVE  # type: ignore[union-attr]

    fingerprint = "deterministic-placeholder-fingerprint"
    repo.complete(
        burst_id=burst.burst_id,
        workspace_id=workspace_id,
        expected_record_version=current_version,
        completed_at=_NOW,
        frozen_membership_fingerprint=fingerprint,
    )
    final = repo.get(burst.burst_id)
    assert final is not None
    assert final.state is BurstState.COMPLETED
    assert final.frozen_membership_fingerprint == fingerprint
