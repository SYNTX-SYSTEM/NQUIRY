"""F04 WU-04.1: CMD_BEGIN_ANALYSIS, TRN-SESS-006 QUESTION_CAPTURE → ANALYSIS.

MUST BECOME TRUE: the Session controller begins analysis; the Session is
ANALYSIS at version +1; one audit row, BINDING at `SESSION:<id>`, with after
state `session:ANALYSIS` (EC-2, `establishedBy`); exactly one unconsumed
OA-1 = (this Command, AIOP-001) exists.

MUST REMAIN IMPOSSIBLE: a non-controller begin; a begin from any state other
than QUESTION_CAPTURE; a begin over an unverified frozen set or with an
unresolved capture; a stale begin; a double begin; any AI call in this commit.

FALSIFIERS: A1-A10 (F04 reconstruction §15).
"""

from __future__ import annotations

import ast
import uuid
from pathlib import Path

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from application.session_control_handler import (
    IdempotentReplay,
    SessionCommandDenied,
    SessionPreconditionUnmet,
    SessionVersionStale,
)
from commit.coordinator import CommitFailedPrecommit, CommitInjectionPoint
from commit.idempotency import IdempotencyPayloadCollision
from domain.session import SessionState
from persistence.tables import (
    ai_generations_table,
    ai_operation_authorizations_table,
    audit_events_table,
)
from test_support.failure_injector import ScriptedFailureInjector

ROOT = Path(__file__).resolve().parents[2]


def _oas(db: sa.Connection, ctx: dict) -> list:  # type: ignore[type-arg]
    return f04.rows(db, ai_operation_authorizations_table, session_id=ctx["session"].value)


def test_a1_controller_begins_analysis(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    before = f03.session_of(db_connection, ctx["session"])
    result = f04.begin(db_connection, ctx)

    after = f03.session_of(db_connection, ctx["session"])
    assert after.state is SessionState.ANALYSIS
    assert after.record_version.value == before.record_version.value + 1

    audits = f03.audit_rows(db_connection, ctx, "CMD_BEGIN_ANALYSIS")
    assert len(audits) == 1
    audit = audits[0]
    assert audit["authority_source_type"] == "BINDING"
    assert audit["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    assert audit["state_after_ref"] == "session:ANALYSIS"
    assert audit["actor_type"] == "HUMAN_USER"

    oas = _oas(db_connection, ctx)
    assert len(oas) == 1
    oa = oas[0]
    assert oa["id"] == result.authorization_id
    assert (oa["shape"], oa["ai_operation_id"], oa["sequence_no"]) == ("OA-1", "AIOP-001", 1)
    assert oa["authorizing_command_id"] == result.commit_unit.command_id.value
    assert oa["chain_root_command_id"] == result.commit_unit.command_id.value
    # unconsumed: no generation carries it
    assert f04.rows(db_connection, ai_generations_table, operation_authorization_id=oa["id"]) == []

    position = f03.position(db_connection, ctx, ctx["fac"])
    assert position["session"]["state"] == "ANALYSIS"
    assert position["establishedBy"]["commandType"] == "CMD_BEGIN_ANALYSIS"
    assert position["establishedBy"]["authoritySourceType"] == "BINDING"


def test_a2_wrong_authority_is_denied(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    for actor in (ctx["participants"][0], ctx["owner"], ctx["outsider"]):
        with pytest.raises(SessionCommandDenied):
            f04.begin(db_connection, ctx, actor)
    # a Challenge-scoped control binding is not Session control
    other = ctx["participants"][1]
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
        f04.begin(db_connection, ctx, other)
    # a non-member of the Workspace
    stranger = f02.insert_user(db_connection, "stranger")
    with pytest.raises(SessionCommandDenied):
        f04.begin(db_connection, ctx, stranger)
    assert f03.session_of(db_connection, ctx["session"]).state is SessionState.QUESTION_CAPTURE
    assert _oas(db_connection, ctx) == []


def test_a3_wrong_state_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f04.begin(db_connection, ctx)
    assert exc.value.reason_code.startswith("SESSION_NOT_QUESTION_CAPTURE:QUESTION_GENERATION")

    ctx2 = f04.analysis_context(db_connection)
    with pytest.raises(SessionPreconditionUnmet) as exc2:
        f04.begin(db_connection, ctx2)
    assert exc2.value.reason_code == "SESSION_NOT_QUESTION_CAPTURE:ANALYSIS"


def test_a4_unverified_frozen_set_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    # Test-superuser tamper: the stored fingerprint no longer matches the set.
    db_connection.execute(sa.text("ALTER TABLE question_bursts DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text(
            "UPDATE question_bursts SET frozen_membership_fingerprint = 'tampered' WHERE id = :b"
        ),
        {"b": ctx["burst"].value},
    )
    db_connection.execute(sa.text("ALTER TABLE question_bursts ENABLE TRIGGER USER"))
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f04.begin(db_connection, ctx)
    assert exc.value.reason_code == "FROZEN_SET_UNVERIFIED"
    assert f03.session_of(db_connection, ctx["session"]).state is SessionState.QUESTION_CAPTURE
    assert _oas(db_connection, ctx) == []


def test_a5_unresolved_capture_is_blocked(db_connection: sa.Connection) -> None:
    from persistence.tables import command_attempts_table, commands_table

    ctx = f04.capture_context(db_connection)
    # An IN_PROGRESS capture attempt targeting this Burst (10 §4.4: never
    # assumed either way).
    command_id, attempt_id = uuid.uuid4(), uuid.uuid4()
    db_connection.execute(
        sa.insert(commands_table).values(
            id=command_id,
            workspace_id=ctx["ws"].value,
            command_type="CMD_CAPTURE_BURST_QUESTION",
            contract_version="1.0",
            payload_fingerprint="x",
            created_at=f02.NOW,
            target_refs=[f"burst:{ctx['burst'].value}"],
        )
    )
    db_connection.execute(
        sa.insert(command_attempts_table).values(
            id=attempt_id,
            command_id=command_id,
            workspace_id=ctx["ws"].value,
            actor_ref="x",
            received_at=f02.NOW,
        )
    )
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f04.begin(db_connection, ctx)
    assert exc.value.reason_code == "UNRESOLVED_CAPTURE"


def test_a6_stale_expected_version(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    session = f03.session_of(db_connection, ctx["session"])
    with pytest.raises(SessionVersionStale):
        f04.begin(db_connection, ctx, expected_session_version=session.record_version.value - 1)
    assert _oas(db_connection, ctx) == []


def test_a7_idempotent_replay_and_key_collision(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    ident = f03.keyed_ident()
    session = f03.session_of(db_connection, ctx["session"])
    version = session.record_version.value
    f04.begin(db_connection, ctx, ident=ident, expected_session_version=version)
    with pytest.raises(IdempotentReplay):
        f04.begin(db_connection, ctx, ident=f03.retry(ident), expected_session_version=version)
    with pytest.raises(IdempotencyPayloadCollision):
        f04.begin(db_connection, ctx, ident=f03.retry(ident), expected_session_version=version + 7)
    assert len(_oas(db_connection, ctx)) == 1


def test_a8_no_ai_in_the_transition_commit(db_connection: sa.Connection) -> None:
    source = (ROOT / "packages/application/analysis_begin_handler.py").read_text()
    imported = {
        (node.module or "").split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "ai_gateway" not in imported
    ctx = f04.capture_context(db_connection)
    f04.begin(db_connection, ctx)
    assert f04.rows(db_connection, ai_generations_table, session_id=ctx["session"].value) == []


def test_a9_exactly_one_session_analysis_row(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(audit_events_table)
        .where(
            audit_events_table.c.workspace_id == ctx["ws"].value,
            audit_events_table.c.state_after_ref == "session:ANALYSIS",
        )
    ).scalar_one()
    assert count == 1


@pytest.mark.parametrize(
    "point",
    [
        CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION,
        CommitInjectionPoint.BEFORE_AUDIT,
        CommitInjectionPoint.BEFORE_OUTBOX,
    ],
)
def test_a10_failed_precommit_leaves_nothing(
    db_connection: sa.Connection, point: CommitInjectionPoint
) -> None:
    ctx = f04.capture_context(db_connection)
    with pytest.raises(CommitFailedPrecommit):
        f04.begin(
            db_connection,
            ctx,
            failure_injector=ScriptedFailureInjector(fire_at=point, exception=RuntimeError("x")),
        )
    assert f03.session_of(db_connection, ctx["session"]).state is SessionState.QUESTION_CAPTURE
    assert _oas(db_connection, ctx) == []
    assert f03.audit_rows(db_connection, ctx, "CMD_BEGIN_ANALYSIS") == []
