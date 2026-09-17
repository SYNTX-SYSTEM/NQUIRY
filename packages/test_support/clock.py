"""Deterministic `Clock` test double.

TEST ONLY. Must never be imported by production code — see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from semantic_types.clock import Clock  # noqa: F401  (Protocol, for type-checking callers)


class FixedClock:
    """A `Clock` that returns a fixed, test-controlled instant.

    `advance()` lets a test move time forward explicitly and
    deterministically instead of sleeping, matching 14 §40's
    requirement that concurrency/expiry tests use deterministic
    barriers/hooks, never sleep-based timing.
    """

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or datetime(2000, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now = self._now + delta

    def set(self, when: datetime) -> None:
        if when.tzinfo is None:
            raise ValueError("FixedClock requires a timezone-aware datetime")
        self._now = when


__all__ = ["FixedClock"]
