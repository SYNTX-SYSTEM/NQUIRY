"""IdGenerator port.

Source: 14_IMPLEMENTATION_SEQUENCE.md §5, §42 ("`IdGenerator` port
supports deterministic tests. IDs are non-semantic.").

Non-collapse rule: the values produced here are opaque identity
material only. Production code must depend on the `IdGenerator`
Protocol, never call `uuid.uuid4()`/a raw UUIDv7 generator directly,
so that tests can supply a deterministic sequence (see
`packages/test_support/id_generator.py`) instead of relying on
randomness for reproducible proof.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Protocol, runtime_checkable


@runtime_checkable
class IdGenerator(Protocol):
    """Port: a source of fresh, non-semantic identity values."""

    def new_uuid(self) -> uuid.UUID:
        """Return a fresh UUID suitable for wrapping in a strong identity type."""
        ...


def _generate_uuid7() -> uuid.UUID:
    """Construct a UUIDv7-compatible value (RFC 9562) from stdlib primitives only.

    Layout (128 bits): 48-bit millisecond Unix timestamp, 4-bit version
    (0b0111), 12-bit random, 2-bit variant (0b10), 62-bit random. Time
    ordering is a storage/index convenience only; it carries no
    authority or sequencing semantics for domain purposes.
    """
    unix_ts_ms = time.time_ns() // 1_000_000
    ts_bytes = unix_ts_ms.to_bytes(6, byteorder="big")
    rand = os.urandom(10)

    out = bytearray(16)
    out[0:6] = ts_bytes
    out[6] = 0x70 | (rand[0] & 0x0F)  # version nibble (7) + 4 random bits
    out[7] = rand[1]
    out[8] = 0x80 | (rand[2] & 0x3F)  # variant bits (10) + 6 random bits
    out[9:16] = rand[3:10]
    return uuid.UUID(bytes=bytes(out))


class SystemIdGenerator:
    """Default production `IdGenerator` adapter, producing UUIDv7-compatible values."""

    def new_uuid(self) -> uuid.UUID:
        return _generate_uuid7()


__all__ = ["IdGenerator", "SystemIdGenerator"]
