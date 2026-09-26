"""WU-PFC-F08-3 (F08): delivery diagnostics and projection freshness.

Architecture: 19 §28 (INTERNAL WORK UNITS "projection freshness",
"diagnostics"; HUMAN PRODUCT EFFECT "A user-visible consequence remains
explainable after process crash, worker restart, projection rebuild");
09 §122 (AC-09-010: "broker delivery failure ... does require outbox
retry/observability"); 09 §177 (consistency classes for queries);
12 §25 (operational telemetry aids diagnosis and never replaces authoritative
audit).

FIRST BROKEN RELATION (after WU-PFC-F08-2): delivery runs, but nothing states
how far a Workspace's projections trail its committed history, or how many
records are pending, failing or without a basis. A stale projection is
indistinguishable from a fresh one, and a poison backlog is invisible except
by raw SQL.

MUST REMAIN IMPOSSIBLE: diagnostics writing anything; one Workspace's backlog
leaking into another's freshness.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import f02_support as f02
import pytest
import sqlalchemy as sa
from persistence.tables import outbox_events_table
from test_support.clock import FixedClock


def _ports(db: sa.Connection) -> Any:
    from projection.delivery import DeliveryPorts

    return DeliveryPorts(db)


def _deliver(db: sa.Connection) -> Any:
    from nquiry_worker.delivery import run_delivery_pass

    return run_delivery_pass(_ports(db), clock=FixedClock(f02.NOW))


def _outbox_state(db: sa.Connection) -> list[tuple[Any, ...]]:
    rows = db.execute(
        sa.select(
            outbox_events_table.c.id,
            outbox_events_table.c.delivery_status,
            outbox_events_table.c.delivery_attempt_count,
        ).order_by(outbox_events_table.c.id)
    )
    return [tuple(r) for r in rows]


def test_freshness_reports_the_undelivered_backlog_then_fresh(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    outbox = (
        db_connection.execute(
            sa.select(outbox_events_table).where(
                outbox_events_table.c.workspace_id == ctx["ws"].value
            )
        )
        .mappings()
        .all()
    )
    stale = _ports(db_connection).freshness(ctx["ws"])
    assert not stale.fresh
    assert stale.undelivered_events == len(outbox) > 0
    assert stale.oldest_undelivered_at == min(r["created_at"] for r in outbox)
    assert stale.last_delivered_at is None
    _deliver(db_connection)
    fresh = _ports(db_connection).freshness(ctx["ws"])
    assert fresh.fresh and fresh.undelivered_events == 0
    assert fresh.oldest_undelivered_at is None
    assert fresh.last_delivered_at == f02.NOW


def test_freshness_is_workspace_scoped(db_connection: sa.Connection) -> None:
    one = f02.inquiry_context(db_connection)
    _deliver(db_connection)
    f02.inquiry_context(db_connection)  # another Workspace's backlog, undelivered
    assert _ports(db_connection).freshness(one["ws"]).fresh


def test_diagnostics_count_every_delivery_state_including_poison(
    db_connection: sa.Connection,
) -> None:
    ctx = f02.inquiry_context(db_connection)
    rows = (
        db_connection.execute(
            sa.select(outbox_events_table).where(
                outbox_events_table.c.workspace_id == ctx["ws"].value
            )
        )
        .mappings()
        .all()
    )
    poison = rows[0]
    db_connection.execute(sa.text("ALTER TABLE committed_events DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("DELETE FROM committed_events WHERE event_id = :e"), {"e": poison["event_id"]}
    )
    db_connection.execute(sa.text("ALTER TABLE committed_events ENABLE TRIGGER USER"))
    before = _ports(db_connection).diagnostics(ctx["ws"])
    assert (before.pending, before.failed, before.delivered) == (len(rows), 0, 0)
    assert before.without_basis == 1
    _deliver(db_connection)
    after = _ports(db_connection).diagnostics(ctx["ws"])
    assert (after.pending, after.failed, after.delivered) == (0, 1, len(rows) - 1)
    assert after.without_basis == 1 and after.max_failed_attempts == 1
    assert after.oldest_undelivered_at == poison["created_at"]


def test_diagnostics_and_freshness_write_nothing(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    before = _outbox_state(db_connection)
    ports = _ports(db_connection)
    ports.diagnostics(ctx["ws"])
    ports.diagnostics(None)
    ports.freshness(ctx["ws"])
    assert _outbox_state(db_connection) == before


def _worker(*args: str, db: bool = True) -> subprocess.CompletedProcess[str]:
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(root / p) for p in ("packages", "apps/worker/src"))
    if not db:
        env.pop("DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, "-m", "nquiry_worker", *args],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_worker_diagnose_prints_machine_readable_state() -> None:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; this test runs the worker against a live PostgreSQL")
    completed = _worker("--diagnose")
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert set(report) == {
        "pending",
        "failed",
        "delivered",
        "without_basis",
        "max_failed_attempts",
        "oldest_undelivered_at",
    }


def test_worker_diagnose_refuses_without_a_database() -> None:
    completed = _worker("--diagnose", db=False)
    assert completed.returncode == 2
    assert "DATABASE_URL" in completed.stderr
