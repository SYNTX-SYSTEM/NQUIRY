"""Version and contract-version value objects.

Source: 14_IMPLEMENTATION_SEQUENCE.md §5, §26 (OPTIMISTIC CONCURRENCY),
§42 (CONTRACT VERSIONING, CLOCK, IDS AND FINGERPRINTS), §49 (DATABASE
IMPLEMENTATION MAP: `record_version bigint >= 1`).

Non-collapse rule: a version number proves ordering/expectation only.
It is not authority, not Evidence, and not a legitimacy proof by
itself. `RecordVersion` exists to support optimistic concurrency
(expected-version compare-and-swap); it never selects a "latest wins"
domain winner (14 §26: "No last-write-wins domain winner selection").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CONTRACT_VERSION_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)*$")


class InvalidVersionValue(ValueError):
    """Raised when a value cannot legitimately construct a version type."""


@dataclass(frozen=True, slots=True)
class RecordVersion:
    """Monotonic optimistic-concurrency counter for a canonical/governance row.

    Must be `>= 1` (14 §49). A Command carries the *expected* version;
    the persistence layer compares it against the *current* stored
    version at commit time (14 §26). This type only carries the
    integer and its increment operation — it does not decide whether
    an increment is authorized.
    """

    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise InvalidVersionValue(f"RecordVersion requires an int, got {type(self.value)!r}")
        if self.value < 1:
            raise InvalidVersionValue(f"RecordVersion must be >= 1, got {self.value}")

    @classmethod
    def initial(cls) -> RecordVersion:
        """The version of a record at its first legitimate commit."""
        return cls(1)

    def next(self) -> RecordVersion:
        """The version this record moves to on its *next* successful commit.

        Producing this value does not perform or authorize a mutation;
        it only describes what the next legitimate version number is.
        """
        return RecordVersion(self.value + 1)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class _DottedVersion:
    """Shared shape for dotted-integer contract versions, e.g. "1.0" or "1.2.3".

    Not exported directly; concrete subclasses below keep contract
    kinds (Command/Event/AIOP/prompt/method) from being interchangeable
    types, matching 14 §42 ("No silent semantic contract change").
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _CONTRACT_VERSION_PATTERN.match(self.value):
            raise InvalidVersionValue(
                f"{type(self).__name__} requires a dotted-integer version string "
                f"(e.g. '1.0'), got {self.value!r}"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContractVersion(_DottedVersion):
    """Version of a Command/Event/API contract payload shape."""


@dataclass(frozen=True, slots=True)
class PromptVersion(_DottedVersion):
    """Version of an AI Gateway prompt template (14 §24, §42)."""


@dataclass(frozen=True, slots=True)
class MethodVersion(_DottedVersion):
    """Version of an approved methodology definition (14 §43: Method Approval)."""


__all__ = [
    "InvalidVersionValue",
    "RecordVersion",
    "ContractVersion",
    "PromptVersion",
    "MethodVersion",
]
