"""Recovery relations (24 §17; §19.6–19.7; §22.5; WU-AUTH-12).

RECOVERY REQUEST → RECOVERY CHALLENGE → VERIFIED RECOVERY PROOF → RECOVERY
AUTHORITY → RESTORATION / REPLACEMENT EFFECT.

A recovery challenge is temporary, proof-bearing material (24 §17.3). It is
NOT an authentication method (24 §17.2, falsifier 39): it lives in its own
relation, appears in no method list and authenticates nothing; it can only
authorize one restoration effect after verification.

`RecoveryPolicy` is the product boundary of 24 §36 #11 (recovery policy and
proof requirements). It is HUMAN_AUTHORITY_REQUIRED; until decided the
default is DENIED (24 §17.6 "Default unresolved behavior: fail closed"). The
one materialized proof class, VERIFIED_EMAIL_SELF_SERVICE (a challenge
delivered to an ACTIVE verified address of an identity that has an ACTIVE
local password method), is admitted by the runtime in DEVELOPMENT / TEST
only, so the mechanism can be proven without deciding the policy.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from semantic_types.ids import UserId


class RecoveryPolicy(Enum):
    DENIED = "DENIED"
    VERIFIED_EMAIL_SELF_SERVICE = "VERIFIED_EMAIL_SELF_SERVICE"


class RecoveryType(Enum):
    PASSWORD_RESET = "PASSWORD_RESET"


@dataclass(frozen=True, slots=True)
class RecoveryChallengeRecord:
    recovery_id: uuid.UUID
    user_id: UserId
    recovery_type: RecoveryType
    issued_at: datetime
    expires_at: datetime
    verified_at: datetime | None
    consumed_at: datetime | None
    revoked_at: datetime | None
    failed_attempts: int


class RecoveryChallengeRepository(Protocol):
    def create(
        self,
        *,
        user_id: UserId,
        recovery_type: RecoveryType,
        challenge_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> RecoveryChallengeRecord: ...

    def latest_open(
        self, *, user_id: UserId, recovery_type: RecoveryType
    ) -> RecoveryChallengeRecord | None: ...

    def revoke_open(
        self, *, user_id: UserId, recovery_type: RecoveryType, revoked_at: datetime
    ) -> int: ...

    def get_for_update(self, recovery_id: uuid.UUID) -> RecoveryChallengeRecord | None: ...

    def verify_and_consume(
        self,
        recovery_id: uuid.UUID,
        *,
        challenge_hash: str,
        now: datetime,
        max_failed_attempts: int,
    ) -> RecoveryChallengeRecord | None:
        """One conditional write: sets verified_at and consumed_at only if the
        challenge is open, unexpired, under the attempt limit and the hash matches."""
        ...

    def count_failed_attempt(self, recovery_id: uuid.UUID) -> int: ...


__all__ = [
    "RecoveryChallengeRecord",
    "RecoveryChallengeRepository",
    "RecoveryPolicy",
    "RecoveryType",
]
