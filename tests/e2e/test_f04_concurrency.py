"""F04 concurrency: separate PostgreSQL connections, real row locks, real commits.

The race runs in a throwaway database cloned from the test database (the F03
pattern), so committed history never leaks into the shared test database.
Skipped unless `DATABASE_URL` names a `*_test` database.

MUST BECOME TRUE: every F04 command on one Session is serialized by the Session
row lock (FOR NO KEY UPDATE); after any interleaving there is exactly one
BEGIN_ANALYSIS, at most one generation per OA, at most one non-terminal
generation per (Session, operation), exactly one new OA per contested request,
and a superseded OA never executes. The multi-transaction run (PI-2) commits
T1, T2a and T2b+T3 as separate, durable transactions.

MUST REMAIN IMPOSSIBLE: two BEGIN_ANALYSIS commits; two generations for one
OA; two OA rows with the same sequence; a request and an execution both
succeeding against the same unconsumed OA.
"""

from __future__ import annotations

import os
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import f02_support as f02
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application.analysis_runtime import mock_runtime
from application.analysis_system import run_authorized_operation
from application.composition import GovernedPorts
from application.session_control_handler import SessionPreconditionUnmet, SessionVersionStale
from commit.coordinator import CommitDenied, CommitFailedPrecommit
from sqlalchemy.engine import make_url

A1 = AIOperationId.AIOP_001


@pytest.fixture
def race() -> Iterator[dict[str, Any]]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set")
    parsed = make_url(url)
    if not (parsed.database or "").endswith("_test"):
        pytest.skip("concurrency proof clones the database; requires a *_test DATABASE_URL")
    clone = f"race_{uuid.uuid4().hex[:10]}"
    admin = sa.create_engine(parsed.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(sa.text(f'CREATE DATABASE "{clone}" TEMPLATE "{parsed.database}"'))
    engine = sa.create_engine(parsed.set(database=clone), pool_size=8, max_overflow=8)
    try:
        with engine.connect() as setup:
            ctx = f04.capture_context(setup)
            setup.commit()
        yield {"engine": engine, "ctx": ctx}
    finally:
        engine.dispose()
        with admin.connect() as c:
            c.execute(sa.text(f'DROP DATABASE IF EXISTS "{clone}" WITH (FORCE)'))
        admin.dispose()


def _engine_uow(engine: sa.Engine) -> Any:
    """Production-shaped UnitOfWork: one real, committed transaction per call."""

    @contextmanager
    def unit() -> Iterator[GovernedPorts]:
        with engine.connect() as connection, connection.begin():
            yield GovernedPorts(connection)

    return unit


def _lock_timeout(conn: sa.Connection, ms: int = 400) -> None:
    conn.execute(sa.text(f"SET lock_timeout = '{ms}ms'"))


def _count(engine: sa.Engine, sql: str, **params: Any) -> int:
    with engine.connect() as c:
        return int(c.execute(sa.text(sql), params).scalar_one())


def _begun(engine: sa.Engine, ctx: dict[str, Any]) -> dict[str, Any]:
    with engine.connect() as c:
        result = f04.begin(c, ctx)
        c.commit()
    ctx = dict(ctx, oa1=result.authorization_id, begin_command=result.commit_unit.command_id)
    return ctx


def test_open_begin_excludes_a_second_begin(race: dict[str, Any]) -> None:
    engine, ctx = race["engine"], race["ctx"]
    with engine.connect() as first, engine.connect() as second:
        version = f04.f03.session_of(first, ctx["session"]).record_version.value
        f04.begin(first, ctx, expected_session_version=version)  # not committed: holds the lock
        _lock_timeout(second)
        with pytest.raises(sa.exc.OperationalError, match="lock timeout|could not obtain lock"):
            f04.begin(second, ctx, expected_session_version=version)
        second.rollback()
        first.commit()
        with pytest.raises((SessionVersionStale, SessionPreconditionUnmet)):
            f04.begin(second, ctx, expected_session_version=version)
        second.rollback()
    assert (
        _count(
            engine,
            "SELECT count(*) FROM audit_events WHERE state_after_ref = 'session:ANALYSIS'",
        )
        == 1
    )
    assert _count(engine, "SELECT count(*) FROM ai_operation_authorizations") == 1


def test_thread_race_of_begins(race: dict[str, Any]) -> None:
    engine, ctx = race["engine"], race["ctx"]
    with engine.connect() as c:
        version = f04.f03.session_of(c, ctx["session"]).record_version.value
    results: list[str] = []
    lock = threading.Lock()
    start = threading.Barrier(4)

    def begin() -> None:
        with engine.connect() as conn:
            start.wait(timeout=10)
            try:
                f04.begin(conn, ctx, expected_session_version=version)
                conn.commit()
                outcome = "committed"
            except (
                SessionPreconditionUnmet,
                SessionVersionStale,
                CommitDenied,
                CommitFailedPrecommit,
            ) as exc:
                conn.rollback()
                outcome = type(exc).__name__
            with lock:
                results.append(outcome)

    threads = [threading.Thread(target=begin) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert results.count("committed") == 1, results
    assert _count(engine, "SELECT count(*) FROM ai_operation_authorizations") == 1


def test_pi2_multi_transaction_run_commits_each_step_durably(race: dict[str, Any]) -> None:
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    outcome = run_authorized_operation(
        _engine_uow(engine),
        session_id=ctx["session"],
        authorization_id=ctx["oa1"],
        runtime=mock_runtime(),
        now=lambda: f02.NOW,
    )
    assert outcome.status == "ACCEPTED" and outcome.next.status == "ACCEPTED"  # type: ignore[union-attr]
    # Every step is durable and visible to a brand-new connection.
    assert _count(engine, "SELECT count(*) FROM ai_generations WHERE status = 'VALIDATED'") == 2
    assert _count(engine, "SELECT count(*) FROM ai_validation_proofs") == 2
    assert (
        _count(engine, "SELECT count(*) FROM ai_derived_artifacts WHERE session_id IS NOT NULL")
        == 2
    )
    assert (
        _count(
            engine,
            "SELECT count(*) FROM audit_events WHERE authority_source_type = 'SYSTEM_OPERATION'",
        )
        == 4
    )


def test_thread_race_of_executions_of_one_oa(race: dict[str, Any]) -> None:
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    statuses: list[str] = []
    lock = threading.Lock()
    start = threading.Barrier(4)

    def execute() -> None:
        start.wait(timeout=10)
        outcome = run_authorized_operation(
            _engine_uow(engine),
            session_id=ctx["session"],
            authorization_id=ctx["oa1"],
            runtime=mock_runtime({AIOperationId.AIOP_002: MockProviderOutcome.TIMEOUT}),
            now=lambda: f02.NOW,
        )
        with lock:
            statuses.append(outcome.status)

    threads = [threading.Thread(target=execute) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert statuses.count("ACCEPTED") == 1, statuses
    assert (
        _count(engine, "SELECT count(*) FROM ai_generations WHERE ai_operation_id = 'AIOP-001'")
        == 1
    )


def test_request_racing_an_execution_of_the_same_unconsumed_oa(race: dict[str, Any]) -> None:
    """RECOVERY vs EXECUTE on OA-1: the Session lock orders them; never both."""
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    results: dict[str, Any] = {}
    start = threading.Barrier(2)

    def recover() -> None:
        with engine.connect() as conn:
            start.wait(timeout=10)
            try:
                f04.request(conn, ctx, A1, RequestCase.RECOVERY)
                conn.commit()
                results["request"] = "committed"
            except SessionPreconditionUnmet as exc:
                conn.rollback()
                results["request"] = exc.reason_code

    def execute() -> None:
        start.wait(timeout=10)
        outcome = run_authorized_operation(
            _engine_uow(engine),
            session_id=ctx["session"],
            authorization_id=ctx["oa1"],
            runtime=mock_runtime(),
            now=lambda: f02.NOW,
            stop_after_execute=True,
        )
        results["execute"] = outcome.reason_code

    threads = [threading.Thread(target=recover), threading.Thread(target=execute)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    executed = results["execute"] == "PROCESS_STOPPED"
    requested = results["request"] == "committed"
    assert executed != requested, results  # exactly one side won
    if requested:
        assert results["execute"] == "SYSTEM_OPERATION_SUPERSEDED"
    else:
        assert results["request"] in {"GENERATION_IN_PROGRESS", "REQUEST_CASE_MISMATCH:RETRY"}
    assert _count(engine, "SELECT count(*) FROM ai_generations") == (1 if executed else 0)


def test_thread_race_of_retry_requests(race: dict[str, Any]) -> None:
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    run_authorized_operation(
        _engine_uow(engine),
        session_id=ctx["session"],
        authorization_id=ctx["oa1"],
        runtime=mock_runtime({A1: MockProviderOutcome.TIMEOUT}),
        now=lambda: f02.NOW,
    )
    outcomes: list[str] = []
    lock = threading.Lock()
    start = threading.Barrier(4)

    def retry() -> None:
        with engine.connect() as conn:
            start.wait(timeout=10)
            try:
                f04.request(conn, ctx, A1, RequestCase.RETRY)
                conn.commit()
                outcome = "committed"
            except SessionPreconditionUnmet as exc:
                conn.rollback()
                outcome = exc.reason_code
            with lock:
                outcomes.append(outcome)

    threads = [threading.Thread(target=retry) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert outcomes.count("committed") == 1, outcomes
    # the losers saw the new, unconsumed OA-2: their RETRY no longer matches
    assert set(outcomes) - {"committed"} <= {"REQUEST_CASE_MISMATCH:RECOVERY"}
    assert _count(engine, "SELECT count(*) FROM ai_operation_authorizations") == 2


# ---- independent review R1 / R2 at REAL COMMIT (deferred PI-1 triggers fire here)


def test_r2_real_commit_denied_acceptance_leaves_no_validated_proof(race: dict[str, Any]) -> None:
    from commit.coordinator import CommitInjectionPoint
    from test_support.failure_injector import ScriptedFailureInjector

    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    outcome = run_authorized_operation(
        _engine_uow(engine),
        session_id=ctx["session"],
        authorization_id=ctx["oa1"],
        runtime=mock_runtime(),
        now=lambda: f02.NOW,
        accept_failure_injector=ScriptedFailureInjector(
            fire_at=CommitInjectionPoint.BEFORE_AUDIT, exception=RuntimeError("boom")
        ),
    )
    assert outcome.status == "ACCEPTANCE_DENIED"
    assert _count(engine, "SELECT count(*) FROM ai_validation_proofs") == 0
    assert (
        _count(engine, "SELECT count(*) FROM ai_derived_artifacts WHERE session_id IS NOT NULL")
        == 0
    )
    assert (
        _count(
            engine,
            "SELECT count(*) FROM ai_generations WHERE status = 'FAILED' "
            "AND failure_detail_ref LIKE 'validated_output_fingerprint:%'",
        )
        == 1
    )


def test_r2_real_commit_refuses_an_orphan_validated_proof(race: dict[str, Any]) -> None:
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    run_authorized_operation(
        _engine_uow(engine),
        session_id=ctx["session"],
        authorization_id=ctx["oa1"],
        runtime=mock_runtime(),
        now=lambda: f02.NOW,
        stop_after_execute=True,
    )
    with engine.connect() as c:
        generation_id = c.execute(sa.text("SELECT id FROM ai_generations")).scalar_one()
        c.execute(
            sa.text(
                "INSERT INTO ai_validation_proofs (id, workspace_id, ai_generation_id, "
                "ai_operation_id, contract_version, validator_version, validation_result, "
                "validated_at, output_fingerprint) VALUES (:i, :w, :g, 'AIOP-001', '1.0', '4.1', "
                "'VALIDATED', now(), :f)"
            ),
            {"i": uuid.uuid4(), "w": ctx["ws"].value, "g": generation_id, "f": "f" * 64},
        )
        with pytest.raises(sa.exc.DBAPIError, match="PI-1"):
            c.commit()  # the deferred trigger refuses AT COMMIT
    assert _count(engine, "SELECT count(*) FROM ai_validation_proofs") == 0


def test_r1_r2_real_commit_happy_path_binds_every_accepted_artifact(race: dict[str, Any]) -> None:
    engine = race["engine"]
    ctx = _begun(engine, race["ctx"])
    outcome = run_authorized_operation(
        _engine_uow(engine),
        session_id=ctx["session"],
        authorization_id=ctx["oa1"],
        runtime=mock_runtime(),
        now=lambda: f02.NOW,
    )
    assert outcome.status == "ACCEPTED" and outcome.next.status == "ACCEPTED"  # type: ignore[union-attr]
    assert (
        _count(
            engine,
            "SELECT count(*) FROM ai_derived_artifacts a JOIN ai_validation_proofs p "
            "ON p.ai_generation_id = a.ai_generation_id WHERE a.session_id IS NOT NULL "
            "AND p.validation_result = 'VALIDATED' "
            "AND p.output_fingerprint = a.content_fingerprint "
            "AND a.content_fingerprint = encode(sha256(convert_to(a.content, 'UTF8')), 'hex')",
        )
        == 2
    )
    # iff: every VALIDATED proof has its VALIDATED generation and accepted artifact
    assert (
        _count(
            engine,
            "SELECT count(*) FROM ai_validation_proofs p WHERE p.validation_result = 'VALIDATED' "
            "AND NOT EXISTS (SELECT 1 FROM ai_generations g JOIN ai_derived_artifacts a "
            "ON a.ai_generation_id = g.id AND a.session_id IS NOT NULL "
            "WHERE g.id = p.ai_generation_id AND g.status = 'VALIDATED')",
        )
        == 0
    )
