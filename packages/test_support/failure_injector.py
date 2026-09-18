"""Deterministic `FailureInjectionPort` test double.

TEST ONLY. Must never be imported by production code — see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`.

Mirrors `test_support.clock.FixedClock`'s own relationship to
`semantic_types.clock.Clock`: the Protocol (`commit.coordinator.
FailureInjectionPort`) is production-importable; this concrete,
fully-deterministic double is not. 14 section 40: "Test-only
`FailureInjector` hooks... Production import test forbids
FailureInjector" -- honored by this module living here, never in
`packages/commit/`.
"""

from __future__ import annotations

from commit.coordinator import CommitInjectionPoint  # noqa: F401  (re-exported for test callers)


class ScriptedFailureInjector:
    """Raises a caller-chosen exception the first time `before()` is
    called with a caller-chosen `CommitInjectionPoint`, and is a no-op
    for every other point and every subsequent call -- deterministic,
    no sleep, no timing dependency, matching 14 section 40's own
    requirement ("deterministic barriers/hooks, never sleep-based
    proof").
    """

    def __init__(self, *, fire_at: CommitInjectionPoint, exception: Exception) -> None:
        self._fire_at = fire_at
        self._exception = exception
        self._fired = False

    def before(self, point: CommitInjectionPoint) -> None:
        if not self._fired and point is self._fire_at:
            self._fired = True
            raise self._exception

    @property
    def fired(self) -> bool:
        return self._fired


class RecordingFailureInjector:
    """Never raises; records every point it was called with, in order
    -- lets a test assert exactly which hooks a given code path
    actually reaches (and, just as importantly, which ones it does
    NOT reach once an earlier point already failed/denied).
    """

    def __init__(self) -> None:
        self.points_observed: list[CommitInjectionPoint] = []

    def before(self, point: CommitInjectionPoint) -> None:
        self.points_observed.append(point)


__all__ = ["ScriptedFailureInjector", "RecordingFailureInjector"]
