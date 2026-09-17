"""T0 semantic tests: Clock port and its production/test implementations.

14 §40 requires deterministic barriers/hooks, never sleep-based
timing, for concurrency/expiry proof. `FixedClock.advance()` is
exercised here as the mechanism later packages must use instead of
`time.sleep`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from semantic_types.clock import Clock, SystemClock
from test_support.clock import FixedClock


def test_system_clock_returns_timezone_aware_utc_now() -> None:
    clock: Clock = SystemClock()
    now = clock.now()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


def test_fixed_clock_is_deterministic_until_advanced() -> None:
    start = datetime(2030, 1, 1, tzinfo=timezone.utc)
    clock: Clock = FixedClock(start)
    assert clock.now() == start
    assert clock.now() == start  # calling twice does not itself advance time


def test_fixed_clock_advance_moves_time_forward_deterministically() -> None:
    start = datetime(2030, 1, 1, tzinfo=timezone.utc)
    clock = FixedClock(start)
    clock.advance(timedelta(hours=1))
    assert clock.now() == start + timedelta(hours=1)


def test_fixed_clock_set_requires_timezone_aware_datetime() -> None:
    clock = FixedClock()
    with pytest.raises(ValueError):
        clock.set(datetime(2030, 1, 1))  # naive datetime rejected
