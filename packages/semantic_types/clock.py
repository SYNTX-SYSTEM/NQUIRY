"""Clock port.

Source: 14_IMPLEMENTATION_SEQUENCE.md §42 ("`Clock` port centralizes
time for deterministic expiry, binding validity where modeled, audit,
event and recovery tests.").

Non-collapse rule: the Clock only reports time. It does not decide
expiry, validity, or any other domain consequence — a later package
that needs "is this expired" logic must ask that question explicitly
using a value obtained from this port, not embed `datetime.now()`
calls of its own. Production code must depend on the `Clock`
Protocol, never on `datetime.now()`/`time.time()` directly, so that
tests can supply a deterministic implementation (see
`packages/test_support/clock.py`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Port: a source of the current, timezone-aware instant."""

    def now(self) -> datetime:
        """Return the current instant as a timezone-aware UTC `datetime`."""
        ...


class SystemClock:
    """Default production `Clock` adapter backed by the system wall clock."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


__all__ = ["Clock", "SystemClock"]
