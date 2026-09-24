"""F03 WU-03.7: CMD_COMPLETE_BURST = TRN-SESS-005 + TRN-BURST-005 as ONE bundle
(manual, authorized), against real PostgreSQL, through the real handler.

MUST BECOME TRUE: the holder of SESSION_CONTROL_RIGHT at exactly `SESSION:<id>`
(HD-9) completes the ACTIVE Burst. In ONE commit the Burst becomes COMPLETED
with a frozen-set fingerprint, and the Session becomes QUESTION_CAPTURE. The
frozen set contains exactly the committed human Questions, and its fingerprint
is recomputable from canonical persistence. Provenance: BINDING at
`SESSION:<id>`; `establishedBy` resolves QUESTION_CAPTURE.

MUST REMAIN IMPOSSIBLE: completion by a participant, the Workspace Owner, a
Challenge-scoped controller or a non-human actor; a stale completion; a second
completion; completion with a capture still unresolved (FBR-F03-3) or with zero
Questions (O-6); a capture after the freeze; a partial freeze after a failure
before commit; a fingerprint that disagrees with the frozen membership, also
after later normalization work; time alone completing the Burst (HD-11).
"""

from __future__ import annotations

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from application.burst_completion_handler import complete_burst
from application.frozen_set import recompute_frozen_fingerprint, verify_frozen_set
from application.session_control_handler import (
    IdempotentReplay,
    SessionCommandDenied,
    SessionPreconditionUnmet,
    SessionVersionStale,
)
from authority.actor import ActorClass, ActorIdentity
from command.envelope import CommandOutcome
from commit.coordinator import (
    AmbiguousCommitFailure,
    CommitFailedPrecommit,
    CommitIndeterminate,
    CommitInjectionPoint,
)
from domain.burst import BurstState
from domain.session import SessionState
from persistence import inquiry_directory as directory
from persistence.tables import questions_table
from test_support.failure_injector import ScriptedFailureInjector


def _captured(db: sa.Connection, ctx: dict, n: int = 3) -> list[str]:  # type: ignore[type-arg]
    a, b = ctx["participants"][:2]
    texts = [f"Question {i}?" for i in range(n)]
    for i, text in enumerate(texts):
        f03.capture(db, ctx, (a, b)[i % 2], text)
    return texts


def _states(db: sa.Connection, ctx: dict):  # type: ignore[no-untyped-def,type-arg]
    return f03.session_of(db, ctx["session"]).state, f03.burst_of(db, ctx).state


def _untouched(db: sa.Connection, ctx: dict) -> None:  # type: ignore[type-arg]
    assert _states(db, ctx) == (SessionState.QUESTION_GENERATION, BurstState.ACTIVE)
    assert f03.burst_of(db, ctx).frozen_membership_fingerprint is None
    assert f03.audit_rows(db, ctx, "CMD_COMPLETE_BURST") == []


# ----------------------------------------------------------------------- lawful


def test_controller_completes_the_burst_and_freezes_exactly_the_captured_set(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    texts = _captured(db_connection, ctx, 3)
    ctx_burst_version = f03.burst_of(db_connection, ctx).record_version.value

    result = f03.complete(db_connection, ctx, ctx["fac"])

    session_state, burst_state = _states(db_connection, ctx)
    assert (session_state, burst_state) == (SessionState.QUESTION_CAPTURE, BurstState.COMPLETED)
    burst = f03.burst_of(db_connection, ctx)
    assert burst.completed_at == f02.NOW and burst.record_version.value == ctx_burst_version + 1
    assert burst.frozen_membership_fingerprint == result.fingerprint
    assert result.member_count == 3

    # exactly the committed human questions, in capture order, verbatim
    members = f03.membership_rows(db_connection, ctx)
    assert [m["captured_order"] for m in members] == [0, 1, 2]
    stored = [
        db_connection.execute(
            sa.select(questions_table.c.original_text, questions_table.c.origin).where(
                questions_table.c.id == m["question_id"]
            )
        ).one()
        for m in members
    ]
    assert [s[0] for s in stored] == texts and {s[1] for s in stored} == {"HUMAN"}

    # reconstructable from canonical persistence
    verification = verify_frozen_set(f02.ports(db_connection), burst)
    assert verification.matches and verification.member_count == 3
    assert (
        recompute_frozen_fingerprint(f02.ports(db_connection), burst.burst_id) == result.fingerprint
    )

    # provenance: BINDING at SESSION:<id>, the completion Command, one bundle commit
    (audit,) = f03.audit_rows(db_connection, ctx, "CMD_COMPLETE_BURST")
    assert audit["authority_source_type"] == "BINDING"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    assert audit["state_before_ref"] == "session:QUESTION_GENERATION|burst:ACTIVE"
    assert audit["state_after_ref"] == "session:QUESTION_CAPTURE|burst:COMPLETED"
    established = directory.session_state_established_by(
        db_connection, ctx["ws"].value, ctx["session"].value, "QUESTION_CAPTURE"
    )
    assert established is not None
    assert established.command_type == "CMD_COMPLETE_BURST"
    assert established.authority_source_type == "BINDING"
    # QUESTION_GENERATION is no longer current, and still resolves uniquely (EC-2)
    opened = directory.session_state_established_by(
        db_connection, ctx["ws"].value, ctx["session"].value, "QUESTION_GENERATION"
    )
    assert opened is not None and opened.command_type == "CMD_OPEN_QUESTION_GENERATION"


def test_time_passing_alone_never_completes_the_burst(db_connection: sa.Connection) -> None:
    """HD-11: the timer is presentation only; there is no scheduler, and a
    capture years after the start is still lawful while the Burst is ACTIVE."""
    from datetime import timedelta

    ctx = f03.generating_context(db_connection, participants=1)
    late = f03.keyed_ident()
    late = type(late)(
        command_id=late.command_id,
        attempt_id=late.attempt_id,
        correlation_id=late.correlation_id,
        commit_id=late.commit_id,
        occurred_at=f02.NOW + timedelta(days=3650),
        idempotency_key=late.idempotency_key,
    )
    f03.capture(db_connection, ctx, ctx["participants"][0], "Still open?", ident_=late)
    assert _states(db_connection, ctx) == (SessionState.QUESTION_GENERATION, BurstState.ACTIVE)


# ------------------------------------------------------------------ authority


def test_participants_and_the_owner_cannot_complete(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    for actor in (ctx["participants"][0], ctx["owner"], ctx["outsider"]):
        with pytest.raises(SessionCommandDenied):
            f03.complete(db_connection, ctx, actor)
    _untouched(db_connection, ctx)
    assert len(f03.membership_rows(db_connection, ctx)) == 2


def test_challenge_scoped_control_does_not_complete(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    other = f03.add_workspace_member(db_connection, ctx, "challenge-controller")
    f02.grant(
        db_connection,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=other,
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="CHALLENGE",
        scope_id=ctx["challenge"].challenge_id.value,
    )
    with pytest.raises(SessionCommandDenied):
        f03.complete(db_connection, ctx, other)
    _untouched(db_connection, ctx)


@pytest.mark.parametrize("actor_class", [ActorClass.AI_PROCESSOR, ActorClass.SYSTEM_SERVICE])
def test_non_human_actors_cannot_complete(
    db_connection: sa.Connection, actor_class: ActorClass
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    session = f03.session_of(db_connection, ctx["session"])
    burst = f03.burst_of(db_connection, ctx)
    with pytest.raises(SessionCommandDenied):
        complete_burst(
            f02.ports(db_connection),
            actor=ActorIdentity(actor_class, ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=session.record_version.value,
            expected_burst_version=burst.record_version.value,
            ident=f03.keyed_ident(),
        )
    _untouched(db_connection, ctx)


def test_controller_from_another_workspace_cannot_complete(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    _, foreign_owner = f03.new_workspace_with_member(db_connection, "foreign")
    with pytest.raises(SessionCommandDenied):
        f03.complete(db_connection, ctx, foreign_owner)
    _untouched(db_connection, ctx)


# ---------------------------------------------------------- preconditions / state


def test_stale_versions_cannot_complete(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    session = f03.session_of(db_connection, ctx["session"])
    with pytest.raises(SessionVersionStale):
        f03.complete(
            db_connection,
            ctx,
            ctx["fac"],
            expected_session_version=session.record_version.value + 3,
        )
    burst = f03.burst_of(db_connection, ctx)
    with pytest.raises(SessionVersionStale):
        f03.complete(
            db_connection, ctx, ctx["fac"], expected_burst_version=burst.record_version.value + 3
        )
    _untouched(db_connection, ctx)


def test_zero_questions_blocks_completion(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f03.complete(db_connection, ctx, ctx["fac"])
    assert exc.value.reason_code == "NO_CAPTURED_QUESTIONS"
    _untouched(db_connection, ctx)


def test_second_completion_is_blocked_or_replayed(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    ident = f03.keyed_ident()
    sv = f03.session_of(db_connection, ctx["session"]).record_version.value
    bv = f03.burst_of(db_connection, ctx).record_version.value
    first = f03.complete(db_connection, ctx, ctx["fac"], ident_=ident)
    fingerprint = f03.burst_of(db_connection, ctx).frozen_membership_fingerprint

    # the same intent again (a retry re-sends the SAME body): idempotent replay
    with pytest.raises(IdempotentReplay):
        f03.complete(
            db_connection,
            ctx,
            ctx["fac"],
            ident_=f03.retry(ident),
            expected_session_version=sv,
            expected_burst_version=bv,
        )
    # a NEW intent against the completed Burst: blocked (not a topology denial)
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f03.complete(db_connection, ctx, ctx["fac"])
    assert exc.value.reason_code.startswith("SESSION_NOT_QUESTION_GENERATION")

    assert f03.burst_of(db_connection, ctx).frozen_membership_fingerprint == fingerprint
    assert first.fingerprint == fingerprint
    assert len(f03.audit_rows(db_connection, ctx, "CMD_COMPLETE_BURST")) == 1


def test_late_capture_after_the_freeze_is_impossible(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    f03.complete(db_connection, ctx, ctx["fac"])
    frozen = f03.burst_of(db_connection, ctx).frozen_membership_fingerprint
    # the application refuses ...
    with pytest.raises(SessionPreconditionUnmet):
        f03.capture(db_connection, ctx, ctx["participants"][0], "Too late?")
    # ... and so does the database, even for a caller that bypasses the handler
    import uuid

    from domain.burst_membership import QuestionBurstMembership
    from domain.question import Question, QuestionOrigin
    from semantic_types.ids import QuestionId, RelationId
    from semantic_types.versions import RecordVersion

    qid = QuestionId(uuid.uuid4())
    f02.ports(db_connection).questions.create_root(
        Question(
            question_id=qid,
            challenge_id=ctx["challenge"].challenge_id,
            workspace_id=ctx["ws"],
            original_text="Bypass?",
            normalized_text=None,
            origin=QuestionOrigin.HUMAN,
            author_user_id=ctx["participants"][0],
            created_at=f02.NOW,
            record_version=RecordVersion.initial(),
        )
    )
    with pytest.raises(sa.exc.DBAPIError, match="frozen"), db_connection.begin_nested():
        f02.ports(db_connection).bursts.add_member(
            QuestionBurstMembership(
                burst_question_membership_id=RelationId(uuid.uuid4()),
                question_burst_id=ctx["burst"],
                question_id=qid,
                workspace_id=ctx["ws"],
                captured_order=99,
                captured_at=f02.NOW,
                capture_actor_user_id=ctx["participants"][0],
                capture_origin=QuestionOrigin.HUMAN,
                record_version=RecordVersion.initial(),
            )
        )
    assert f03.burst_of(db_connection, ctx).frozen_membership_fingerprint == frozen
    assert len(f03.membership_rows(db_connection, ctx)) == 2


# ------------------------------------------------------- unresolved capture


def test_unresolved_capture_blocks_completion_until_recovery_resolves_it(
    db_connection: sa.Connection,
) -> None:
    import uuid

    from persistence.recovery_repository import SqlAlchemyRecoveryRepository
    from recovery.certainty import ConsequenceCertainty
    from recovery.failure_classifier import FailureClass
    from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord
    from semantic_types.ids import CorrelationId, RecoveryId
    from semantic_types.versions import RecordVersion

    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    ident = f03.keyed_ident()
    with pytest.raises(CommitIndeterminate):
        f03.capture(
            db_connection,
            ctx,
            ctx["participants"][0],
            "Unknown fate?",
            ident_=ident,
            failure_injector=ScriptedFailureInjector(
                fire_at=CommitInjectionPoint.BEFORE_DB_COMMIT,
                exception=AmbiguousCommitFailure("uncertain"),
            ),
        )
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f03.complete(db_connection, ctx, ctx["fac"])
    assert exc.value.reason_code == "UNRESOLVED_CAPTURE"
    _untouched(db_connection, ctx)

    attempt = f02.ports(db_connection).commands.list_attempts(ident.command_id)[-1]
    recovery = SqlAlchemyRecoveryRepository(db_connection)
    record = RecoveryRecord(
        recovery_id=RecoveryId(uuid.uuid4()),
        workspace_scope_ref=ctx["ws"],
        failure_correlation_ref=CorrelationId(uuid.uuid4()),
        original_command_id=ident.command_id,
        original_attempt_id=attempt.attempt_id,
        failure_classifications=(FailureClass.F_PERS,),
        canonical_state_certainty=ConsequenceCertainty.CANONICAL_STATE_UNKNOWN,
        external_consequence_certainty=ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        recovery_actor_type="SYSTEM_SERVICE",
        recovery_actor_id="recovery-worker-1",
        result=RecoveryOutcome.UNRESOLVED,
        created_at=f02.NOW,
        updated_at=f02.NOW,
        record_version=RecordVersion.initial(),
    )
    recovery.create(record)
    recovery.mark_resolved(
        record.recovery_id,
        ctx["ws"],
        result=RecoveryOutcome.RECONCILED,
        resolved_at=f02.NOW,
        last_proven_valid_state_ref=None,
    )
    result = f03.complete(db_connection, ctx, ctx["fac"])
    # Only what was actually committed is frozen: the uncertain capture is not in the set.
    assert result.member_count == 2
    assert _states(db_connection, ctx) == (SessionState.QUESTION_CAPTURE, BurstState.COMPLETED)


def test_denied_and_failed_captures_are_not_in_the_frozen_set(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    f03.capture(db_connection, ctx, a, "Kept?")
    with pytest.raises(SessionCommandDenied):
        f03.capture(db_connection, ctx, ctx["outsider"], "Denied?")
    with pytest.raises(CommitFailedPrecommit):
        f03.capture(
            db_connection,
            ctx,
            a,
            "Failed?",
            failure_injector=ScriptedFailureInjector(
                fire_at=CommitInjectionPoint.AFTER_AUDIT, exception=RuntimeError("x")
            ),
        )
    result = f03.complete(db_connection, ctx, ctx["fac"])
    assert result.member_count == 1
    texts = [
        db_connection.execute(
            sa.select(questions_table.c.original_text).where(
                questions_table.c.id == m["question_id"]
            )
        ).scalar_one()
        for m in f03.membership_rows(db_connection, ctx)
    ]
    assert texts == ["Kept?"]


# ------------------------------------------------------------ reconstruction


def test_fingerprint_survives_later_normalization_work(db_connection: sa.Connection) -> None:
    """FBR-F03-4: post-Burst derived work (F04) bumps `questions.record_version`
    and sets `normalized_text`. The frozen set must still verify."""
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 3)
    f03.complete(db_connection, ctx, ctx["fac"])
    burst = f03.burst_of(db_connection, ctx)
    db_connection.execute(
        sa.update(questions_table)
        .where(questions_table.c.workspace_id == ctx["ws"].value)
        .values(normalized_text="normalized", record_version=questions_table.c.record_version + 5)
    )
    verification = verify_frozen_set(f02.ports(db_connection), burst)
    assert verification.matches, (verification.stored, verification.recomputed)


def test_a_tampered_frozen_set_no_longer_verifies(db_connection: sa.Connection) -> None:
    """The check is real: a stored fingerprint that does not match the
    membership is reported as a mismatch."""
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    f03.complete(db_connection, ctx, ctx["fac"])
    burst = f03.burst_of(db_connection, ctx)
    from dataclasses import replace

    forged = replace(burst, frozen_membership_fingerprint="0" * 64)
    assert verify_frozen_set(f02.ports(db_connection), forged).matches is False


# --------------------------------------------------------------- atomicity


@pytest.mark.parametrize(
    "point",
    [
        CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION,
        CommitInjectionPoint.AFTER_RELATION_MUTATION,
        CommitInjectionPoint.BEFORE_AUDIT,
        CommitInjectionPoint.AFTER_AUDIT,
        CommitInjectionPoint.BEFORE_OUTBOX,
        CommitInjectionPoint.AFTER_OUTBOX,
        CommitInjectionPoint.BEFORE_DB_COMMIT,
    ],
)
def test_failure_before_commit_creates_no_partial_freeze(
    db_connection: sa.Connection, point: CommitInjectionPoint
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    ident = f03.keyed_ident()
    with pytest.raises(CommitFailedPrecommit):
        f03.complete(
            db_connection,
            ctx,
            ctx["fac"],
            ident_=ident,
            failure_injector=ScriptedFailureInjector(
                fire_at=point, exception=RuntimeError("injected")
            ),
        )
    # neither half of the bundle exists
    _untouched(db_connection, ctx)
    attempt = f02.ports(db_connection).commands.list_attempts(ident.command_id)[-1]
    assert attempt.outcome is CommandOutcome.FAILED_PRECOMMIT
    # the same intent can be retried, and then freezes exactly once
    f03.complete(db_connection, ctx, ctx["fac"], ident_=f03.retry(ident))
    assert _states(db_connection, ctx) == (SessionState.QUESTION_CAPTURE, BurstState.COMPLETED)


def test_indeterminate_completion_blocks_blind_retry(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    _captured(db_connection, ctx, 2)
    ident = f03.keyed_ident()
    with pytest.raises(CommitIndeterminate):
        f03.complete(
            db_connection,
            ctx,
            ctx["fac"],
            ident_=ident,
            failure_injector=ScriptedFailureInjector(
                fire_at=CommitInjectionPoint.BEFORE_DB_COMMIT,
                exception=AmbiguousCommitFailure("uncertain"),
            ),
        )
    from commit.idempotency import IdempotencyIndeterminateBlocked

    with pytest.raises(IdempotencyIndeterminateBlocked):
        f03.complete(db_connection, ctx, ctx["fac"], ident_=f03.retry(ident))
