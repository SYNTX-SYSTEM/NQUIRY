"""The fixed F04 SYSTEM_SERVICE identity (pre-implementation binding PI-3).

`ActorIdentity` requires a `user_id` for every actor class (11 §8: some
identifier for audit and correlation). The F04 analysis service has one fixed,
well-known id. It is not a `users` row, holds no membership, no role and no
binding, and `AuthorityResolver` never consults it (SYSTEM_SERVICE is never a
binding holder). Its only authority is SYSTEM_OPERATION: a committed human
Command that authorized exactly the operation it runs (HD-17).

Only the F04 system-operation handlers (`application.analysis_system`) may
construct an actor with this identity; a static gate
(`tests/regression/test_f04_static_gates.py`) enforces that. The effect gate
refuses SYSTEM_OPERATION for any other SYSTEM_SERVICE id.
"""

from __future__ import annotations

import uuid

from semantic_types.ids import UserId

F04_ANALYSIS_SERVICE_ID = UserId(uuid.UUID("5f040000-0000-4000-8000-000000000001"))

__all__ = ["F04_ANALYSIS_SERVICE_ID"]
