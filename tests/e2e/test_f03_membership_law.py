"""F03 WU-03.2 (FBR-F03-2, FBR-F03-6, EC-1): the persistence home of the
Burst-membership law, against real PostgreSQL.

MUST BECOME TRUE: a burst membership exists only for an ACTIVE Burst, for an
author who holds a CURRENT SessionParticipation in that Burst's Session, whose
Question is HUMAN-origin, authored by that same actor, and belongs to the
Session's own Challenge. `captured_order` is unique per Burst. A Session owns
at most ONE Burst row, ever.

MUST REMAIN IMPOSSIBLE (falsifiers, each a test below): membership in a
PREPARED / COMPLETED Burst; membership for a non-participant (member, owner,
controller, left participant); a Question authored by someone else than the
capture actor; a Question of another Challenge; two memberships with the same
`captured_order`; a second Burst row for a Session after the first COMPLETED.
"""

from __future__ import annotations

import uuid

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from domain.burst_membership import QuestionBurstMembership
from domain.question import Question, QuestionOrigin
from persistence.session_participation_repository import SqlAlchemySessionParticipationRepository
from persistence.tables import question_bursts_table, session_participations_table
from semantic_types.ids import QuestionId, RelationId, UserId
from semantic_types.versions import RecordVersion


def _question(db: sa.Connection, ctx: dict, *, author: UserId, challenge_id=None) -> QuestionId:  # type: ignore[no-untyped-def,type-arg]
    p = f02.ports(db)
    qid = QuestionId(uuid.uuid4())
    p.questions.create_root(
        Question(
            question_id=qid,
            challenge_id=challenge_id or ctx["challenge"].challenge_id,
            workspace_id=ctx["ws"],
            original_text="Why did it drop?",
            normalized_text=None,
            origin=QuestionOrigin.HUMAN,
            author_user_id=author,
            created_at=f02.NOW,
            record_version=RecordVersion.initial(),
        )
    )
    return qid


def _membership(ctx: dict, qid: QuestionId, actor: UserId, order: int = 0):  # type: ignore[no-untyped-def,type-arg]
    return QuestionBurstMembership(
        burst_question_membership_id=RelationId(uuid.uuid4()),
        question_burst_id=ctx["burst"],
        question_id=qid,
        workspace_id=ctx["ws"],
        captured_order=order,
        captured_at=f02.NOW,
        capture_actor_user_id=actor,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )


def _add(db: sa.Connection, ctx: dict, m: QuestionBurstMembership) -> None:  # type: ignore[type-arg]
    f02.ports(db).bursts.add_member(m)


def test_lawful_membership_in_active_burst_for_participant(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    qid = _question(db_connection, ctx, author=author)
    _add(db_connection, ctx, _membership(ctx, qid, author))
    assert len(f02.ports(db_connection).bursts.list_members(ctx["burst"])) == 1


def test_membership_in_prepared_burst_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.prepared_context(db_connection)
    author = f02.insert_user(db_connection, "late")
    # admit the author as a participant so ONLY the Burst state can refuse
    f02.add_member(db_connection, owner=ctx["owner"], workspace_id=ctx["ws"], member=author)
    SqlAlchemySessionParticipationRepository(db_connection).admit(
        participation_id=uuid.uuid4(),
        session_id=ctx["session"],
        workspace_id=ctx["ws"],
        user_id=author,
        admitted_by_user_id=ctx["fac"],
        joined_at=f02.NOW,
    )
    qid = _question(db_connection, ctx, author=author)
    with (
        pytest.raises(sa.exc.DBAPIError, match="not ACTIVE"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, qid, author))


def test_membership_in_completed_burst_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    q1 = _question(db_connection, ctx, author=author)
    m1 = _membership(ctx, q1, author)
    _add(db_connection, ctx, m1)
    burst = f03.burst_of(db_connection, ctx)
    f02.ports(db_connection).bursts.complete(
        burst_id=burst.burst_id,
        workspace_id=ctx["ws"],
        expected_record_version=burst.record_version,
        completed_at=f02.NOW,
        frozen_membership_fingerprint="fp",
    )
    q2 = _question(db_connection, ctx, author=author)
    with (
        pytest.raises(sa.exc.DBAPIError, match="not ACTIVE|COMPLETED"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, q2, author, order=1))


@pytest.mark.parametrize("who", ["outsider", "controller", "owner"])
def test_membership_for_non_participant_is_refused(db_connection: sa.Connection, who: str) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    actor: UserId = {"outsider": ctx["outsider"], "controller": ctx["fac"], "owner": ctx["owner"]}[
        who
    ]
    qid = _question(db_connection, ctx, author=actor)
    with (
        pytest.raises(sa.exc.DBAPIError, match="SessionParticipation"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, qid, actor))


def test_membership_for_left_participant_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    db_connection.execute(
        sa.update(session_participations_table)
        .where(session_participations_table.c.user_id == author.value)
        .values(left_at=f02.NOW)
    )
    qid = _question(db_connection, ctx, author=author)
    with (
        pytest.raises(sa.exc.DBAPIError, match="SessionParticipation"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, qid, author))


def test_question_authored_by_someone_else_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a, b = ctx["participants"]
    qid = _question(db_connection, ctx, author=b)  # b wrote it
    with (
        pytest.raises(sa.exc.DBAPIError, match="author"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, qid, a))  # a claims the capture


def test_question_of_another_challenge_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    other = f02.create_challenge(
        db_connection, actor=ctx["fac"], workspace_id=ctx["ws"], title="Another challenge"
    )
    qid = _question(db_connection, ctx, author=author, challenge_id=other.challenge_id)
    with (
        pytest.raises(sa.exc.DBAPIError, match="Challenge"),
        db_connection.begin_nested(),
    ):
        _add(db_connection, ctx, _membership(ctx, qid, author))


def test_duplicate_captured_order_is_refused(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    _add(db_connection, ctx, _membership(ctx, _question(db_connection, ctx, author=author), author))
    with (
        pytest.raises(sa.exc.IntegrityError, match="captured_order"),
        db_connection.begin_nested(),
    ):
        _add(
            db_connection,
            ctx,
            _membership(ctx, _question(db_connection, ctx, author=author), author, order=0),
        )


def test_second_burst_row_for_a_session_is_refused_even_after_completion(
    db_connection: sa.Connection,
) -> None:
    """EC-1: `get_by_session`'s one-Burst-per-Session assumption lives at the DB."""
    ctx = f03.generating_context(db_connection, participants=1)
    author = ctx["participants"][0]
    _add(db_connection, ctx, _membership(ctx, _question(db_connection, ctx, author=author), author))
    burst = f03.burst_of(db_connection, ctx)
    f02.ports(db_connection).bursts.complete(
        burst_id=burst.burst_id,
        workspace_id=ctx["ws"],
        expected_record_version=burst.record_version,
        completed_at=f02.NOW,
        frozen_membership_fingerprint="fp",
    )
    with (
        pytest.raises(sa.exc.IntegrityError, match="uq_question_bursts_session"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(question_bursts_table).values(
                id=uuid.uuid4(),
                session_id=ctx["session"].value,
                workspace_id=ctx["ws"].value,
                state="PREPARED",
                mode="HUMAN_ONLY",
                record_version=1,
            )
        )
