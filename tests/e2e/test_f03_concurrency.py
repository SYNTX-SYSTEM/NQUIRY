"""F03 WU-03.7 (FBR-F03-2, FBR-F03-6): capture and completion under REAL
concurrency: separate PostgreSQL connections, real row locks, real commits.

The race runs in a throwaway database cloned from the test database
(`CREATE DATABASE ... TEMPLATE`), so committed history never leaks into the
shared `nquiry_test` (several PKG-era tests assert properties of the whole
outbox). Skipped unless `DATABASE_URL` names a `*_test` database.

MUST BECOME TRUE: a capture and a completion are mutually exclusive; after any
interleaving the stored fingerprint equals the fingerprint recomputed from the
final membership, every capture that reported `committed` is in the frozen set,
and `captured_order` is unique and contiguous.

MUST REMAIN IMPOSSIBLE: a capture committing into a Burst after the completion
computed its fingerprint (a frozen set that disagrees with its fingerprint); a
capture committing while the Burst is COMPLETED; two captures with the same
order; a completion that misses a capture that committed first.

FALSIFIER: a capture transaction held open across a completion attempt: exactly
one of the two wins, and the frozen set is consistent.
"""

from __future__ import annotations

import os
import threading
import uuid
from collections.abc import Iterator
from typing import Any

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from application.frozen_set import verify_frozen_set
from application.session_control_handler import SessionPreconditionUnmet
from sqlalchemy.engine import make_url


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
            ctx = f03.generating_context(setup, participants=3)
            setup.commit()
        yield {"engine": engine, "ctx": ctx}
    finally:
        engine.dispose()
        with admin.connect() as c:
            c.execute(sa.text(f'DROP DATABASE IF EXISTS "{clone}" WITH (FORCE)'))
        admin.dispose()


def _capture(conn: sa.Connection, ctx: dict, actor, text: str):  # type: ignore[no-untyped-def,type-arg]
    return f03.capture(conn, ctx, actor, text)


def _lock_timeout(conn: sa.Connection, ms: int = 400) -> None:
    conn.execute(sa.text(f"SET lock_timeout = '{ms}ms'"))


def _final_state(engine: sa.Engine, ctx: dict) -> dict[str, Any]:  # type: ignore[type-arg]
    with engine.connect() as c:
        burst = f03.burst_of(c, ctx)
        verification = verify_frozen_set(f02.ports(c), burst)
        orders = [m["captured_order"] for m in f03.membership_rows(c, ctx)]
        texts = {r["original_text"] for r in f03.question_rows(c, ctx)}
        return {
            "state": burst.state.value,
            "verification": verification,
            "orders": orders,
            "texts": texts,
        }


def test_an_open_capture_excludes_a_completion_and_is_then_frozen(race: dict[str, Any]) -> None:
    engine, ctx = race["engine"], race["ctx"]
    a = ctx["participants"][0]
    with engine.connect() as cap, engine.connect() as comp:
        _capture(cap, ctx, a, "In flight?")  # not committed: holds the Burst row lock
        _lock_timeout(comp)
        with pytest.raises(sa.exc.OperationalError, match="lock timeout|could not obtain lock"):
            f03.complete(comp, ctx, ctx["fac"])
        comp.rollback()
        cap.commit()
        result = f03.complete(comp, ctx, ctx["fac"])
        comp.commit()
    assert result.member_count == 1
    final = _final_state(engine, ctx)
    assert final["state"] == "COMPLETED" and final["verification"].matches
    assert final["texts"] == {"In flight?"}


def test_an_open_completion_excludes_a_capture_which_then_finds_the_burst_completed(
    race: dict[str, Any],
) -> None:
    engine, ctx = race["engine"], race["ctx"]
    a, b = ctx["participants"][:2]
    with engine.connect() as setup:
        f03.capture(setup, ctx, a, "Before?")
        setup.commit()
    with engine.connect() as comp, engine.connect() as late:
        f03.complete(comp, ctx, ctx["fac"])  # not committed: holds the Burst row lock
        _lock_timeout(late)
        with pytest.raises(sa.exc.OperationalError, match="lock timeout|could not obtain lock"):
            _capture(late, ctx, b, "Late?")
        late.rollback()
        comp.commit()
        # the capture retried after the freeze: blocked, nothing written
        with pytest.raises(SessionPreconditionUnmet):
            _capture(late, ctx, b, "Late?")
        late.rollback()
    final = _final_state(engine, ctx)
    assert final["state"] == "COMPLETED" and final["verification"].matches
    assert final["texts"] == {"Before?"} and final["orders"] == [0]


def test_concurrent_captures_are_serialized_without_order_collisions(race: dict[str, Any]) -> None:
    engine, ctx = race["engine"], race["ctx"]
    a, b, _ = ctx["participants"]
    with engine.connect() as first, engine.connect() as second:
        _capture(first, ctx, a, "One?")  # holds the lock
        _lock_timeout(second)
        with pytest.raises(sa.exc.OperationalError, match="lock timeout|could not obtain lock"):
            _capture(second, ctx, b, "Two?")
        second.rollback()
        first.commit()
        _capture(second, ctx, b, "Two?")
        second.commit()
    final = _final_state(engine, ctx)
    assert final["orders"] == [0, 1]


def test_real_thread_race_between_captures_and_completion(race: dict[str, Any]) -> None:
    """Many interleavings, real connections: whatever the schedule, the frozen
    set equals what was acknowledged and verifies against its fingerprint."""
    engine, ctx = race["engine"], race["ctx"]
    a, b, c3 = ctx["participants"]
    with engine.connect() as seed:
        f03.capture(seed, ctx, a, "Seed?")
        seed.commit()

    acknowledged: list[str] = []
    refused: list[str] = []
    errors: list[BaseException] = []
    lock = threading.Lock()
    start = threading.Barrier(5)

    def capturer(actor, label: str) -> None:  # type: ignore[no-untyped-def]
        try:
            with engine.connect() as conn:
                start.wait(timeout=10)
                for i in range(4):
                    text = f"{label}-{i}?"
                    try:
                        _capture(conn, ctx, actor, text)
                        conn.commit()
                        with lock:
                            acknowledged.append(text)
                    except SessionPreconditionUnmet:
                        conn.rollback()
                        with lock:
                            refused.append(text)
        except BaseException as exc:  # noqa: BLE001
            with lock:
                errors.append(exc)

    def completer() -> None:
        try:
            with engine.connect() as conn:
                start.wait(timeout=10)
                f03.complete(conn, ctx, ctx["fac"])
                conn.commit()
        except BaseException as exc:  # noqa: BLE001
            with lock:
                errors.append(exc)

    threads = [
        threading.Thread(target=capturer, args=(a, "a")),
        threading.Thread(target=capturer, args=(b, "b")),
        threading.Thread(target=capturer, args=(c3, "c")),
        threading.Thread(target=completer),
        threading.Thread(target=capturer, args=(a, "a2")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert not errors, errors

    final = _final_state(engine, ctx)
    assert final["state"] == "COMPLETED"
    assert final["verification"].matches, (
        final["verification"].stored,
        final["verification"].recomputed,
    )
    # exactly what was acknowledged is frozen; nothing refused is in the set
    assert final["texts"] == {"Seed?", *acknowledged}
    assert not (set(refused) & final["texts"])
    assert final["orders"] == list(range(len(final["orders"])))
