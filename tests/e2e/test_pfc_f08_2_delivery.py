"""WU-PFC-F08-2 (F08 Consequence Integrity): exact EventEnvelope → Worker →
Projection → Replay/Rebuild.

Architecture: 19 §28 (TARGET "exact EventEnvelope → Worker → Projection →
Replay/Rebuild"; TESTS FIRST: duplicate delivery, worker restart, poison event,
projection failure, projection deletion, projection rebuild, "replay does not
execute Command"); 09 §15 (at-least-once, statuses PENDING / DELIVERED /
FAILED_DELIVERY), §18 (replay may rebuild projections, may not advance
canonical state or submit Commands), §73.1 (a projection consumer never updates
canonical state), §74 (consumers track processed events; redelivery must not
duplicate projection rows); 10 §17 (F-OUT: retry delivery, never repeat the
domain Command), §56 (SYSTEM_SERVICE may retry delivery and advance delivery
status); 12 §17 (COMMAND → COMMIT → DURABLE OUTBOX → EventEnvelope → DELIVERY
→ PROJECTION UPDATE, plus a replay test).

FIRST BROKEN RELATION (after WU-PFC-F08-1): the exact envelope exists, but
nothing delivers it. `nquiry_worker.__main__` is a Phase-0 no-op, `OutboxWorker`
and `ProjectionWorker` are unwired, and the projection consumer's dedupe
(`last_event_id` equality) lets an older retried event overwrite a newer
projected state.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from datetime import timedelta
from typing import Any

import f02_support as f02
import f04_support as f04
import pytest
import sqlalchemy as sa
from persistence.tables import (
    audit_events_table,
    command_attempts_table,
    commands_table,
    commit_units_table,
    inquiry_read_model_table,
    outbox_events_table,
    projection_checkpoints_table,
    session_read_model_table,
    sessions_table,
)
from test_support.clock import FixedClock


def _ports(db: sa.Connection) -> Any:
    from projection.delivery import DeliveryPorts

    return DeliveryPorts(db)


def _pass(db: sa.Connection, *, clock: Any = None, ports: Any = None) -> Any:
    from nquiry_worker.delivery import run_delivery_pass

    return run_delivery_pass(ports or _ports(db), clock=clock or FixedClock(f02.NOW))


def _outbox(db: sa.Connection, ws: Any) -> list[Any]:
    stmt = sa.select(outbox_events_table).where(outbox_events_table.c.workspace_id == ws.value)
    return list(db.execute(stmt).mappings())


def _session_model(db: sa.Connection, session: Any) -> Any:
    return (
        db.execute(
            sa.select(session_read_model_table).where(
                session_read_model_table.c.session_id == session.value
            )
        )
        .mappings()
        .one_or_none()
    )


def _inquiry_models(db: sa.Connection, ws: Any) -> list[dict[str, Any]]:
    rows = db.execute(
        sa.select(inquiry_read_model_table)
        .where(inquiry_read_model_table.c.workspace_id == ws.value)
        .order_by(inquiry_read_model_table.c.aggregate_ref)
    ).mappings()
    return [{k: v for k, v in r.items() if k != "id"} for r in rows]


def _count(db: sa.Connection, table: sa.Table) -> int:
    return db.execute(sa.select(sa.func.count()).select_from(table)).scalar_one()


def _analysed(db: sa.Connection) -> dict[str, Any]:
    ctx = f04.analysis_context(db)
    assert f04.run(db, ctx, ctx["oa1"]).status == "ACCEPTED"
    return ctx


# ------------------------------------------------------------ MUST BECOME TRUE


def test_delivery_projects_the_committed_session_state(db_connection: sa.Connection) -> None:
    ctx = _analysed(db_connection)
    result = _pass(db_connection)
    outbox = _outbox(db_connection, ctx["ws"])
    assert {r["delivery_status"] for r in outbox} == {"DELIVERED"}
    assert {r["id"] for r in outbox} <= set(result.delivered)
    model = _session_model(db_connection, ctx["session"])
    assert model is not None and model["current_state"] == "ANALYSIS"
    session_version = db_connection.execute(
        sa.select(sessions_table.c.record_version).where(
            sessions_table.c.id == ctx["session"].value
        )
    ).scalar_one()
    assert model["last_aggregate_version"] == session_version
    # delivered in per-aggregate commit order: every Session event applied, none skipped
    assert model["projection_version"] == session_version
    checkpoints = db_connection.execute(
        sa.select(projection_checkpoints_table).where(
            projection_checkpoints_table.c.workspace_id == ctx["ws"].value
        )
    ).mappings()
    assert {c["projection_name"] for c in checkpoints} == {
        "session_read_model",
        "inquiry_read_model",
    }


def test_every_non_session_aggregate_gets_its_committed_snapshot(
    db_connection: sa.Connection,
) -> None:
    ctx = _analysed(db_connection)
    _pass(db_connection)
    models = {m["aggregate_ref"]: m for m in _inquiry_models(db_connection, ctx["ws"])}
    q = f"question:{ctx['question_ids'][0].value}"
    assert models[q]["snapshot"]["origin"] == "HUMAN"
    assert models[q]["last_aggregate_version"] == 1
    assert not any(ref.startswith("session:") for ref in models)


# ------------------------------------------------------------ at-least-once safety


def test_redelivery_of_the_same_events_changes_nothing(db_connection: sa.Connection) -> None:
    from persistence.committed_event_repository import SqlAlchemyCommittedEventRepository

    ctx = _analysed(db_connection)
    ports = _ports(db_connection)
    _pass(db_connection, ports=ports)
    before = (
        dict(_session_model(db_connection, ctx["session"])),
        _inquiry_models(db_connection, ctx["ws"]),
    )
    envelopes = SqlAlchemyCommittedEventRepository(db_connection).list_for_workspace(ctx["ws"])
    from nquiry_worker.delivery import projection_publisher

    publisher = projection_publisher(ports)
    for envelope in envelopes:  # an at-least-once redelivery of every event
        publisher.publish(envelope)
    after = (
        dict(_session_model(db_connection, ctx["session"])),
        _inquiry_models(db_connection, ctx["ws"]),
    )
    assert after == before


def test_worker_restart_delivers_nothing_twice(db_connection: sa.Connection) -> None:
    ctx = _analysed(db_connection)
    first = _pass(db_connection)
    second = _pass(db_connection)  # a restarted worker's first pass
    assert first.delivered and not second.delivered and not second.failed
    # exactly one successful attempt each: nothing was delivered twice
    assert {r["delivery_attempt_count"] for r in _outbox(db_connection, ctx["ws"])} == {1}


def test_stale_retry_never_regresses_a_newer_projected_state(db_connection: sa.Connection) -> None:
    from persistence.committed_event_repository import SqlAlchemyCommittedEventRepository

    ctx = _analysed(db_connection)
    ports = _ports(db_connection)
    from nquiry_worker.delivery import projection_publisher

    publisher = projection_publisher(ports)
    ref = f"session:{ctx['session'].value}"
    session_events = sorted(
        (
            e
            for e in SqlAlchemyCommittedEventRepository(db_connection).list_for_workspace(ctx["ws"])
            if e.aggregate_ref == ref
        ),
        key=lambda e: e.aggregate_version_after_commit.value,
    )
    publisher.publish(session_events[-1])  # the newest state arrives first
    for older in session_events[:-1]:  # older events delivered late (retries)
        publisher.publish(older)
    model = _session_model(db_connection, ctx["session"])
    assert model["current_state"] == "ANALYSIS"
    assert (
        model["last_aggregate_version"] == session_events[-1].aggregate_version_after_commit.value
    )


def test_stale_retry_never_regresses_a_non_session_snapshot(db_connection: sa.Connection) -> None:
    """A binding granted then revoked: the late GRANT event never overwrites
    the projected REVOKED snapshot."""
    from application.authority_binding_handler import revoke_human_authority_binding
    from nquiry_worker.delivery import projection_publisher
    from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingVersionReader
    from persistence.committed_event_repository import SqlAlchemyCommittedEventRepository
    from semantic_types.ids import (
        AttemptId,
        AuthorityBindingId,
        CommandId,
        CommitId,
        CorrelationId,
    )

    ctx = f02.inquiry_context(db_connection)
    history = SqlAlchemyCommittedEventRepository(db_connection).list_for_workspace(ctx["ws"])
    grant = next(
        e for e in history if e.event_type == "CMD_GRANT_HUMAN_AUTHORITY_BINDING_COMMITTED"
    )
    binding = AuthorityBindingId(uuid.UUID(grant.payload["binding_id"]))  # type: ignore[index]
    p = f02.ports(db_connection)
    revoke_human_authority_binding(
        db_connection,
        actor=f02.human(ctx["owner"]),
        workspace_id=ctx["ws"],
        binding_id=binding,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=f02.NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        authority_binding_repository=p.bindings,
        authority_resolver=p.resolver,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        current_version_reader=SqlAlchemyAuthorityBindingVersionReader(db_connection),
    )
    revoke = next(
        e
        for e in SqlAlchemyCommittedEventRepository(db_connection).list_for_workspace(ctx["ws"])
        if e.event_type == "CMD_REVOKE_HUMAN_AUTHORITY_BINDING_COMMITTED"
    )
    publisher = projection_publisher(_ports(db_connection))
    publisher.publish(revoke)
    publisher.publish(grant)  # the older event arrives late
    (model,) = [
        m
        for m in _inquiry_models(db_connection, ctx["ws"])
        if m["aggregate_ref"] == grant.aggregate_ref
    ]
    assert model["snapshot"]["state"] == "REVOKED"
    assert model["last_aggregate_version"] == revoke.aggregate_version_after_commit.value


def test_rebuild_repairs_a_corrupted_projection_from_committed_history(
    db_connection: sa.Connection,
) -> None:
    from nquiry_worker.delivery import rebuild_projections

    ctx = _analysed(db_connection)
    _pass(db_connection)
    truth = dict(_session_model(db_connection, ctx["session"]))
    db_connection.execute(
        sa.update(session_read_model_table)
        .where(session_read_model_table.c.session_id == ctx["session"].value)
        .values(current_state="CLOSED")
    )
    rebuild_projections(_ports(db_connection), workspace_id=ctx["ws"])
    assert dict(_session_model(db_connection, ctx["session"])) == truth


# ------------------------------------------------------------ failure handling


def test_poison_event_fails_closed_and_blocks_nothing_else(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    rows = _outbox(db_connection, ctx["ws"])
    poison = next(r for r in rows if r["event_type"] == "CHALLENGE_CREATED")
    db_connection.execute(sa.text("ALTER TABLE committed_events DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("DELETE FROM committed_events WHERE event_id = :e"), {"e": poison["event_id"]}
    )
    db_connection.execute(sa.text("ALTER TABLE committed_events ENABLE TRIGGER USER"))
    result = _pass(db_connection)
    assert result.failed == (poison["id"],)
    after = {r["id"]: r for r in _outbox(db_connection, ctx["ws"])}
    assert after[poison["id"]]["delivery_status"] == "FAILED_DELIVERY"
    assert after[poison["id"]]["delivery_attempt_count"] == 1
    assert after[poison["id"]]["next_attempt_at"] > f02.NOW
    assert all(r["delivery_status"] == "DELIVERED" for i, r in after.items() if i != poison["id"])
    challenge = f"challenge:{ctx['challenge'].challenge_id.value}"
    assert challenge not in {m["aggregate_ref"] for m in _inquiry_models(db_connection, ctx["ws"])}


def test_projection_failure_rolls_back_the_projection_and_is_retried(
    db_connection: sa.Connection,
) -> None:
    from projection.delivery import ProjectionStoreFailure

    ctx = f02.inquiry_context(db_connection)
    ports = _ports(db_connection)
    real_upsert = ports.projection.upsert_inquiry_read_model
    calls = {"n": 0}

    def failing_upsert(model: Any) -> None:
        calls["n"] += 1
        real_upsert(model)  # the write happens, then the store fails
        raise ProjectionStoreFailure("injected projection store failure")

    ports.projection.upsert_inquiry_read_model = failing_upsert
    result = _pass(db_connection, ports=ports)
    assert result.failed and calls["n"] >= 1
    assert _inquiry_models(db_connection, ctx["ws"]) == []  # nothing partial survives
    ports.projection.upsert_inquiry_read_model = real_upsert
    retried = _pass(db_connection, ports=ports, clock=FixedClock(f02.NOW + timedelta(hours=1)))
    assert set(result.failed) <= set(retried.delivered)
    assert {r["delivery_status"] for r in _outbox(db_connection, ctx["ws"])} == {"DELIVERED"}


# ------------------------------------------------------------ replay / rebuild


def test_projection_deletion_and_rebuild_reproduce_the_identical_read_model(
    db_connection: sa.Connection,
) -> None:
    from nquiry_worker.delivery import rebuild_projections

    ctx = _analysed(db_connection)
    _pass(db_connection)
    session_before = dict(_session_model(db_connection, ctx["session"]))
    inquiry_before = _inquiry_models(db_connection, ctx["ws"])
    db_connection.execute(
        sa.delete(session_read_model_table).where(
            session_read_model_table.c.workspace_id == ctx["ws"].value
        )
    )
    db_connection.execute(
        sa.delete(inquiry_read_model_table).where(
            inquiry_read_model_table.c.workspace_id == ctx["ws"].value
        )
    )
    assert _session_model(db_connection, ctx["session"]) is None
    rebuild_projections(_ports(db_connection), workspace_id=ctx["ws"])
    assert dict(_session_model(db_connection, ctx["session"])) == session_before
    assert _inquiry_models(db_connection, ctx["ws"]) == inquiry_before


def test_delivery_and_replay_execute_no_command_and_change_no_canonical_state(
    db_connection: sa.Connection,
) -> None:
    from nquiry_worker.delivery import rebuild_projections

    ctx = _analysed(db_connection)
    tables = (
        commands_table,
        command_attempts_table,
        commit_units_table,
        audit_events_table,
        outbox_events_table,
    )
    counts = {t.name: _count(db_connection, t) for t in tables}
    committed = _count(db_connection, sa.table("committed_events"))
    session = dict(
        db_connection.execute(
            sa.select(sessions_table).where(sessions_table.c.id == ctx["session"].value)
        )
        .mappings()
        .one()
    )
    _pass(db_connection)
    rebuild_projections(_ports(db_connection), workspace_id=ctx["ws"])
    assert {t.name: _count(db_connection, t) for t in tables} == counts
    assert _count(db_connection, sa.table("committed_events")) == committed
    assert (
        dict(
            db_connection.execute(
                sa.select(sessions_table).where(sessions_table.c.id == ctx["session"].value)
            )
            .mappings()
            .one()
        )
        == session
    )


def test_delivery_files_import_no_command_path() -> None:
    """14 §41: an event consumer cannot import a consequential handler."""
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for rel in ("apps/worker/src/nquiry_worker/delivery.py", "packages/projection/delivery.py"):
        tree = ast.parse((root / rel).read_text())
        modules = {
            (n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
        } | {
            a.name.split(".")[0]
            for n in ast.walk(tree)
            if isinstance(n, ast.Import)
            for a in n.names
        }
        assert not modules & {"command", "commit", "application", "boundaries", "domain"}, rel


# ------------------------------------------------------------ the running worker


def _worker_env() -> dict[str, str]:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(root / p) for p in ("packages", "apps/worker/src"))
    return env


def test_worker_entrypoint_runs_one_real_pass_and_exits_cleanly() -> None:
    env = _worker_env()
    if not env.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; this test runs the worker against a live PostgreSQL")
    completed = subprocess.run(
        [sys.executable, "-m", "nquiry_worker", "--once"],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "delivery pass" in completed.stderr


def test_worker_entrypoint_refuses_to_run_without_a_database() -> None:
    env = {k: v for k, v in _worker_env().items() if k != "DATABASE_URL"}
    completed = subprocess.run(
        [sys.executable, "-m", "nquiry_worker", "--once"],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 2
    assert "DATABASE_URL" in completed.stderr
