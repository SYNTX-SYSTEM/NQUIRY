"""F03 WU-03.6: CMD_CAPTURE_BURST_QUESTION (TRN-Q-001 / AUTH-DEP-Q-001),
against real PostgreSQL, through the real governed handler.

MUST BECOME TRUE: an authorized participant captures a human Question into the
ACTIVE HUMAN_ONLY Burst. The Question exists (HUMAN, author = actor,
`original_text` byte-exact, `normalized_text` NULL) with its membership (order,
time, actor, HUMAN) in ONE commit. Provenance is real: PARTICIPATION source,
the participation id, scope `SESSION:<id>`. An identical retry is idempotent.

MUST REMAIN IMPOSSIBLE (falsifiers below): capture before ACTIVE; capture by a
non-participant (member, controller, Owner, outsider, other Workspace, foreign
Session); an unauthorized or malformed capture leaving rows; text that is
altered, trimmed or normalized; a non-question form stored; client-supplied
origin/author; an AI/system actor capturing; a changed payload or another
Command type reusing a key; a stale capture committing; a partial capture after
a failure before commit; a capture writing a `session:*` state_after_ref (EC-2).
"""

from __future__ import annotations

import inspect

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from application.burst_capture_handler import (
    CaptureInputRejected,
    capture_burst_question,
)
from application.session_control_handler import (
    IdempotentReplay,
    SessionCommandDenied,
    SessionPreconditionUnmet,
    SessionVersionStale,
    admit_participant,
)
from authority.actor import ActorClass, ActorIdentity
from command.envelope import CommandOutcome
from commit.coordinator import (
    AmbiguousCommitFailure,
    CommitFailedPrecommit,
    CommitIndeterminate,
    CommitInjectionPoint,
)
from commit.idempotency import IdempotencyOutcome, IdempotencyPayloadCollision
from persistence import inquiry_directory as directory
from persistence.burst_repository import burst_target_ref
from persistence.command_repository import CommandTypeMismatch
from persistence.tables import (
    audit_events_table,
    commit_units_table,
    outbox_events_table,
    questions_table,
)
from test_support.failure_injector import ScriptedFailureInjector


def _burst_version(db: sa.Connection, ctx: dict) -> int:  # type: ignore[type-arg]
    return f03.burst_of(db, ctx).record_version.value


def _no_rows(db: sa.Connection, ctx: dict) -> None:  # type: ignore[type-arg]
    assert f03.question_rows(db, ctx) == []
    assert f03.membership_rows(db, ctx) == []
    assert f03.audit_rows(db, ctx, "CMD_CAPTURE_BURST_QUESTION") == []


# ----------------------------------------------------------------------- lawful


def test_participant_captures_a_human_question_with_real_provenance(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a = ctx["participants"][0]
    before = _burst_version(db_connection, ctx)

    result = f03.capture(db_connection, ctx, a, "Why did onboarding drop after step 2?")

    (q,) = f03.question_rows(db_connection, ctx)
    assert q["original_text"] == "Why did onboarding drop after step 2?"
    assert q["normalized_text"] is None
    assert q["origin"] == "HUMAN" and q["author_user_id"] == a.value
    assert q["challenge_id"] == ctx["challenge"].challenge_id.value
    assert q["id"] == result.question_id.value

    (m,) = f03.membership_rows(db_connection, ctx)
    assert m["question_id"] == q["id"] and m["captured_order"] == 0
    assert m["capture_actor_user_id"] == a.value and m["capture_origin"] == "HUMAN"
    assert m["captured_at"] == f02.NOW

    # Burst and Session are untouched by a capture (TRN-Q-001).
    assert _burst_version(db_connection, ctx) == before
    assert f03.session_of(db_connection, ctx["session"]).state.value == "QUESTION_GENERATION"

    # Provenance: PARTICIPATION at the exact Session, ref = the participation.
    (audit,) = f03.audit_rows(db_connection, ctx, "CMD_CAPTURE_BURST_QUESTION")
    participation = f02.ports(db_connection).participations.get_current(ctx["session"], a)
    assert participation is not None
    assert audit["authority_source_type"] == "PARTICIPATION"
    assert audit["authority_source_ref"] == participation.participation_id
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    assert audit["actor_id"] == str(a.value)
    assert burst_target_ref(ctx["burst"]) in audit["target_refs"]
    assert f"question:{q['id']}" in audit["target_refs"]
    # EC-2: a capture must not write a `session:*` establishing after-state.
    assert not (audit["state_after_ref"] or "").startswith("session:")
    outbox = db_connection.execute(
        sa.select(outbox_events_table.c.event_type).where(
            outbox_events_table.c.commit_id == audit["commit_id"]
        )
    ).scalar_one()
    assert outbox == "BURST_QUESTION_CAPTURED"


def test_capture_order_is_sequential_and_states_are_established_once(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a, b = ctx["participants"]
    f03.capture(db_connection, ctx, a, "Question A?")
    f03.capture(db_connection, ctx, b, "Question B?")
    f03.capture(db_connection, ctx, a, "Question C?")
    orders = [m["captured_order"] for m in f03.membership_rows(db_connection, ctx)]
    assert orders == [0, 1, 2]
    # EC-2: `session_state_established_by` is one_or_none per (Session, state);
    # captures must not create a second establishing row.
    row = directory.session_state_established_by(
        db_connection, ctx["ws"].value, ctx["session"].value, "QUESTION_GENERATION"
    )
    assert row is not None and row.command_type == "CMD_OPEN_QUESTION_GENERATION"


@pytest.mark.parametrize(
    "text",
    [
        "  Was ist über “Drop-off” hinaus zu sagen?  ",
        "\U0001f680 你好 — مرحبا שלום?",
        "café vs café?",
        "Line one\n  line two\t?\n\n",
        "  leading spaces and  double  spaces ?",
        "ﬁ vs fi (ligature) ² ?",
        "UPPER lower MiXeD?",
    ],
)
def test_original_text_is_stored_byte_exact(db_connection: sa.Connection, text: str) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    result = f03.capture(db_connection, ctx, a, text)
    stored = db_connection.execute(
        sa.select(questions_table.c.original_text).where(
            questions_table.c.id == result.question_id.value
        )
    ).scalar_one()
    assert stored == text
    assert stored.encode("utf-8") == text.encode("utf-8")


def test_controller_self_admitted_may_capture_hd14(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1, controller_participates=True)
    fac = ctx["fac"]
    f03.capture(db_connection, ctx, fac, "A controller question?")
    (audit,) = f03.audit_rows(db_connection, ctx, "CMD_CAPTURE_BURST_QUESTION")
    assert audit["authority_source_type"] == "PARTICIPATION"  # not BINDING: role is not authority
    admissions = f03.audit_rows(db_connection, ctx, "CMD_ADMIT_SESSION_PARTICIPANT")
    self_admission = [r for r in admissions if r["actor_id"] == str(fac.value)]
    assert self_admission and self_admission[0]["authority_source_type"] == "BINDING"


# ----------------------------------------------------------------- impossibility


def test_capture_before_the_burst_is_active_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f03.prepared_context(db_connection)
    a = f03.add_workspace_member(db_connection, ctx, "early")
    f03._step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=a)
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f03.capture(db_connection, ctx, a, "Too early?")
    assert exc.value.reason_code.startswith("SESSION_NOT_QUESTION_GENERATION")
    _no_rows(db_connection, ctx)


@pytest.mark.parametrize("who", ["outsider", "controller", "owner"])
def test_non_participants_are_denied(db_connection: sa.Connection, who: str) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    actor = {"outsider": ctx["outsider"], "controller": ctx["fac"], "owner": ctx["owner"]}[who]
    with pytest.raises(SessionCommandDenied) as exc:
        f03.capture(db_connection, ctx, actor, "Sneaky?")
    assert exc.value.reason_code == "PARTICIPATION_NOT_CURRENT"
    _no_rows(db_connection, ctx)
    # The DENIED attempt is recorded, and not left unresolved (FBR-F03-3).
    unresolved = f02.ports(db_connection).commands.list_unresolved_for_target(
        workspace_id=ctx["ws"],
        command_type="CMD_CAPTURE_BURST_QUESTION",
        target_ref=burst_target_ref(ctx["burst"]),
    )
    assert unresolved == ()


def test_actor_from_another_workspace_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, foreign = f03.new_workspace_with_member(db_connection, "foreign")
    with pytest.raises(SessionCommandDenied):
        f03.capture(db_connection, ctx, foreign, "From outside?")
    _no_rows(db_connection, ctx)


def test_participant_of_another_session_cannot_capture_here(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    # A second Session in the SAME Workspace/Challenge; `a` participates in
    # neither its Burst nor the Session.
    other_session = f02.create_session(
        db_connection,
        actor=ctx["fac"],
        workspace_id=ctx["ws"],
        challenge_id=ctx["challenge"].challenge_id,
    )
    with pytest.raises(SessionCommandDenied) as exc:
        f03.capture(db_connection, ctx, a, "Wrong session?", session_id=other_session)
    assert exc.value.reason_code == "PARTICIPATION_NOT_CURRENT"
    _no_rows(db_connection, ctx)


def test_non_human_actors_cannot_capture(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    for actor_class in (ActorClass.AI_PROCESSOR, ActorClass.SYSTEM_SERVICE):
        with pytest.raises(SessionCommandDenied):
            capture_burst_question(
                f02.ports(db_connection),
                actor=ActorIdentity(actor_class, a),
                workspace_id=ctx["ws"],
                session_id=ctx["session"],
                original_text="Generated?",
                expected_burst_version=_burst_version(db_connection, ctx),
                ident=f03.keyed_ident(),
            )
    _no_rows(db_connection, ctx)


def test_the_handler_has_no_way_to_carry_origin_or_author() -> None:
    params = set(inspect.signature(capture_burst_question).parameters)
    assert params.isdisjoint({"origin", "author", "author_user_id", "capture_origin", "mode"})


@pytest.mark.parametrize("text", ["It dropped because of onboarding.", "", "   ", "Why?!"])
def test_non_question_form_is_rejected_and_stores_nothing(
    db_connection: sa.Connection, text: str
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    with pytest.raises(CaptureInputRejected):
        f03.capture(db_connection, ctx, ctx["participants"][0], text)
    _no_rows(db_connection, ctx)


def test_unauthorized_actor_learns_nothing_from_input_validation(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    with pytest.raises(SessionCommandDenied):  # denied, NOT rejected
        f03.capture(db_connection, ctx, ctx["outsider"], "not a question")


def test_stale_burst_version_cannot_commit(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    real = _burst_version(db_connection, ctx)
    with pytest.raises(SessionVersionStale) as exc:
        f03.capture(
            db_connection, ctx, ctx["participants"][0], "Stale?", expected_burst_version=real + 7
        )
    assert exc.value.current == real and exc.value.expected == real + 7
    _no_rows(db_connection, ctx)


# ------------------------------------------------------------------ idempotency


def test_identical_retry_is_idempotent(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    first = f03.capture(db_connection, ctx, a, "Once only?", ident_=ident)
    with pytest.raises(IdempotentReplay) as replay:
        f03.capture(db_connection, ctx, a, "Once only?", ident_=f03.retry(ident))
    assert replay.value.result_ref == str(first.question_id.value)
    assert len(f03.question_rows(db_connection, ctx)) == 1
    assert len(f03.membership_rows(db_connection, ctx)) == 1
    assert len(f03.audit_rows(db_connection, ctx, "CMD_CAPTURE_BURST_QUESTION")) == 1


def test_changed_payload_under_the_same_key_is_rejected(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    f03.capture(db_connection, ctx, a, "Original text?", ident_=ident)
    with pytest.raises(IdempotencyPayloadCollision):
        f03.capture(db_connection, ctx, a, "Changed text?", ident_=f03.retry(ident))
    (q,) = f03.question_rows(db_connection, ctx)
    assert q["original_text"] == "Original text?"


def test_two_different_keys_with_identical_text_are_two_legitimate_captures(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    f03.capture(db_connection, ctx, a, "Same words?")
    f03.capture(db_connection, ctx, a, "Same words?")
    assert (
        len(f03.question_rows(db_connection, ctx)) == 2
    )  # no content dedup: not in the architecture


def test_a_key_of_another_command_type_cannot_be_reused_for_capture(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    newcomer = f03.add_workspace_member(db_connection, ctx, "newcomer")
    session = f03.session_of(db_connection, ctx["session"])
    admit_participant(
        f02.ports(db_connection),
        actor=f02.human(ctx["fac"]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        participant_user_id=newcomer,
        expected_session_version=session.record_version.value,
        ident=ident,
    )
    with pytest.raises(CommandTypeMismatch):
        f03.capture(db_connection, ctx, a, "Cross-command reuse?", ident_=f03.retry(ident))
    _no_rows(db_connection, ctx)


def test_a_capture_key_cannot_be_reused_for_another_command_type(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    f03.capture(db_connection, ctx, a, "First?", ident_=ident)
    newcomer = f03.add_workspace_member(db_connection, ctx, "newcomer")
    session = f03.session_of(db_connection, ctx["session"])
    with pytest.raises(CommandTypeMismatch):
        admit_participant(
            f02.ports(db_connection),
            actor=f02.human(ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            participant_user_id=newcomer,
            expected_session_version=session.record_version.value,
            ident=f03.retry(ident),
        )


# ----------------------------------------------------- immutability and atomicity


def test_original_text_cannot_be_mutated_once_captured(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    result = f03.capture(db_connection, ctx, ctx["participants"][0], "Fixed forever?")
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.update(questions_table)
            .where(questions_table.c.id == result.question_id.value)
            .values(original_text="rewritten?")
        )
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.update(questions_table)
            .where(questions_table.c.id == result.question_id.value)
            .values(origin="AI", author_user_id=None)
        )


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
def test_failure_before_commit_leaves_no_partial_capture(
    db_connection: sa.Connection, point: CommitInjectionPoint
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    units_before = db_connection.execute(
        sa.select(sa.func.count()).select_from(commit_units_table)
    ).scalar_one()
    with pytest.raises(CommitFailedPrecommit):
        f03.capture(
            db_connection,
            ctx,
            a,
            "Will fail?",
            ident_=ident,
            failure_injector=ScriptedFailureInjector(
                fire_at=point, exception=RuntimeError("injected")
            ),
        )
    _no_rows(db_connection, ctx)
    assert (
        db_connection.execute(
            sa.select(sa.func.count()).select_from(commit_units_table)
        ).scalar_one()
        == units_before
    )
    p = f02.ports(db_connection)
    attempt = p.commands.list_attempts(ident.command_id)[-1]
    assert attempt.outcome is CommandOutcome.FAILED_PRECOMMIT
    record = p.idempotency.get(
        workspace_id=ctx["ws"],
        command_type="CMD_CAPTURE_BURST_QUESTION",
        idempotency_key=ident.idempotency_key,
    )
    assert record is not None and record.outcome is IdempotencyOutcome.FAILED_PRECOMMIT
    # A fresh attempt of the SAME intent may now succeed exactly once.
    f03.capture(db_connection, ctx, a, "Will fail?", ident_=f03.retry(ident))
    assert len(f03.question_rows(db_connection, ctx)) == 1


def test_indeterminate_capture_is_recorded_as_unresolved_for_its_burst(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    a = ctx["participants"][0]
    ident = f03.keyed_ident()
    with pytest.raises(CommitIndeterminate):
        f03.capture(
            db_connection,
            ctx,
            a,
            "Unknown fate?",
            ident_=ident,
            failure_injector=ScriptedFailureInjector(
                fire_at=CommitInjectionPoint.BEFORE_DB_COMMIT,
                exception=AmbiguousCommitFailure("uncertain"),
            ),
        )
    unresolved = f02.ports(db_connection).commands.list_unresolved_for_target(
        workspace_id=ctx["ws"],
        command_type="CMD_CAPTURE_BURST_QUESTION",
        target_ref=burst_target_ref(ctx["burst"]),
    )
    assert unresolved == (ident.command_id,)
    # No blind retry (10 §4.4): the same key stays blocked.
    from commit.idempotency import IdempotencyIndeterminateBlocked

    with pytest.raises(IdempotencyIndeterminateBlocked):
        f03.capture(db_connection, ctx, a, "Unknown fate?", ident_=f03.retry(ident))


def test_audit_rows_of_a_capture_are_immutable(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    f03.capture(db_connection, ctx, ctx["participants"][0], "Auditable?")
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.update(audit_events_table)
            .where(audit_events_table.c.command_type == "CMD_CAPTURE_BURST_QUESTION")
            .values(authority_source_type="BINDING")
        )
