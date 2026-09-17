"""Deterministic `IdGenerator` test double.

TEST ONLY. Must never be imported by production code — see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`.
"""

from __future__ import annotations

import uuid

from semantic_types.id_generator import (
    IdGenerator,  # noqa: F401  (Protocol, for type-checking callers)
)


class SequentialIdGenerator:
    """An `IdGenerator` producing a deterministic, reproducible UUID sequence.

    Each call returns `uuid.UUID(int=N)` for an incrementing `N`
    starting at 1, so a test that asserts on specific identity values
    gets the same sequence on every run.
    """

    def __init__(self, start: int = 1) -> None:
        if start < 1:
            raise ValueError("SequentialIdGenerator start must be >= 1")
        self._next = start

    def new_uuid(self) -> uuid.UUID:
        value = uuid.UUID(int=self._next)
        self._next += 1
        return value

    def reset(self, start: int = 1) -> None:
        if start < 1:
            raise ValueError("SequentialIdGenerator start must be >= 1")
        self._next = start


__all__ = ["SequentialIdGenerator"]
