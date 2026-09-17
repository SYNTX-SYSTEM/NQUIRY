"""T0 semantic tests: RecordVersion and dotted contract versions."""

from __future__ import annotations

import pytest
from semantic_types.versions import (
    ContractVersion,
    InvalidVersionValue,
    MethodVersion,
    PromptVersion,
    RecordVersion,
)


def test_record_version_initial_is_one() -> None:
    assert RecordVersion.initial() == RecordVersion(1)


def test_record_version_next_increments_by_one() -> None:
    v = RecordVersion.initial()
    assert v.next() == RecordVersion(2)
    assert v.next().next() == RecordVersion(3)
    # `.next()` does not mutate `v` — RecordVersion is a frozen value, not a counter.
    assert v == RecordVersion(1)


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_record_version_rejects_non_positive(bad: int) -> None:
    with pytest.raises(InvalidVersionValue):
        RecordVersion(bad)


def test_record_version_rejects_non_int() -> None:
    with pytest.raises(InvalidVersionValue):
        RecordVersion("1")  # type: ignore[arg-type]
    with pytest.raises(InvalidVersionValue):
        RecordVersion(True)  # bool is an int subclass; must still be rejected


@pytest.mark.parametrize("cls", [ContractVersion, PromptVersion, MethodVersion])
def test_dotted_version_accepts_valid_forms(cls: type) -> None:
    assert str(cls("1")) == "1"
    assert str(cls("1.0")) == "1.0"
    assert str(cls("1.2.3")) == "1.2.3"


@pytest.mark.parametrize("cls", [ContractVersion, PromptVersion, MethodVersion])
@pytest.mark.parametrize("bad", ["", "v1", "1.", ".1", "1.0.0-beta", "one.two"])
def test_dotted_version_rejects_invalid_forms(cls: type, bad: str) -> None:
    with pytest.raises(InvalidVersionValue):
        cls(bad)


def test_dotted_version_kinds_are_distinct_types() -> None:
    assert ContractVersion("1.0") != PromptVersion("1.0")
    assert type(ContractVersion("1.0")) is not type(PromptVersion("1.0"))
