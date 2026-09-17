"""T0 semantic tests: IdGenerator port and its production/test implementations."""

from __future__ import annotations

import uuid

from semantic_types.id_generator import IdGenerator, SystemIdGenerator
from test_support.id_generator import SequentialIdGenerator


def test_system_id_generator_produces_uuidv7_version_and_variant_bits() -> None:
    generator: IdGenerator = SystemIdGenerator()
    value = generator.new_uuid()
    assert isinstance(value, uuid.UUID)
    assert value.version == 7
    # RFC 9562 variant: the two most significant bits of byte 8 are '10'.
    assert (value.bytes[8] & 0xC0) == 0x80


def test_system_id_generator_produces_distinct_values() -> None:
    generator = SystemIdGenerator()
    values = {generator.new_uuid() for _ in range(1000)}
    assert len(values) == 1000


def test_system_id_generator_is_roughly_time_ordered() -> None:
    """UUIDv7 orders by creation time as a storage convenience (14 §42);
    this is not a domain sequencing guarantee, only a monotonic-ish
    prefix proof.
    """
    generator = SystemIdGenerator()
    first = generator.new_uuid()
    second = generator.new_uuid()
    assert first.bytes[:6] <= second.bytes[:6]


def test_sequential_id_generator_is_deterministic_and_reproducible() -> None:
    generator: IdGenerator = SequentialIdGenerator()
    assert generator.new_uuid() == uuid.UUID(int=1)
    assert generator.new_uuid() == uuid.UUID(int=2)

    replay = SequentialIdGenerator()
    assert replay.new_uuid() == uuid.UUID(int=1)
    assert replay.new_uuid() == uuid.UUID(int=2)


def test_sequential_id_generator_reset() -> None:
    generator = SequentialIdGenerator(start=5)
    assert generator.new_uuid() == uuid.UUID(int=5)
    generator.reset(1)
    assert generator.new_uuid() == uuid.UUID(int=1)
