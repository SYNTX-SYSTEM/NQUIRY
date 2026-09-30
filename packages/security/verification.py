"""Email verification relations: challenges and verified emails
(24 §13.9, §16.1, §19.4, §22.2–22.3; WU-AUTH-11).

State machine (24 §16.1): UNVERIFIED → CHALLENGE_ISSUED → VERIFIED →
SUPERSEDED / REVOKED / EXPIRED. A challenge is temporary proof material
(24 §13.2 "Excluded": never an authentication method); a verified email is a
persisted relation created only after the challenge proof (24 §19.4).

Only the SHA-256 of a challenge token is stored; the raw token exists in the
delivered mail and nowhere else.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from semantic_types.ids import UserId


class ChallengeType(Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"


class VerificationMethod(Enum):
    EMAIL_CHALLENGE = "EMAIL_CHALLENGE"


def generate_challenge_token() -> str:
    return secrets.token_urlsafe(32)


def hash_challenge_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ChallengeRecord:
    challenge_id: uuid.UUID
    challenge_type: ChallengeType
    user_id: UserId
    email: str
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None
    revoked_at: datetime | None
    failed_attempts: int


@dataclass(frozen=True, slots=True)
class VerifiedEmail:
    relation_id: uuid.UUID
    user_id: UserId
    email: str
    verified_at: datetime
    verification_method: VerificationMethod
    superseded_at: datetime | None
    revoked_at: datetime | None


class ChallengeRepository(Protocol):
    def create(
        self,
        *,
        challenge_type: ChallengeType,
        user_id: UserId,
        email: str,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> ChallengeRecord: ...

    def latest_open(
        self, *, challenge_type: ChallengeType, user_id: UserId, email: str
    ) -> ChallengeRecord | None: ...

    def revoke_open(
        self, *, challenge_type: ChallengeType, user_id: UserId, email: str, revoked_at: datetime
    ) -> int: ...

    def get_for_update(self, challenge_id: uuid.UUID) -> ChallengeRecord | None: ...

    def consume(
        self,
        challenge_id: uuid.UUID,
        *,
        token_hash: str,
        now: datetime,
        max_failed_attempts: int,
    ) -> ChallengeRecord | None:
        """One conditional write: consumes the challenge only if it is open,
        unexpired, under the attempt limit and the token hash matches."""
        ...

    def count_failed_attempt(self, challenge_id: uuid.UUID) -> int: ...


class VerifiedEmailRepository(Protocol):
    def active_for_email(self, email: str) -> VerifiedEmail | None: ...

    def list_for_user(self, user_id: UserId) -> tuple[VerifiedEmail, ...]: ...

    def supersede_active(self, *, user_id: UserId, email: str, superseded_at: datetime) -> int: ...

    def create(
        self,
        *,
        user_id: UserId,
        email: str,
        verified_at: datetime,
        verification_method: VerificationMethod,
        provenance_ref: str,
    ) -> VerifiedEmail: ...


__all__ = [
    "ChallengeRecord",
    "ChallengeRepository",
    "ChallengeType",
    "VerificationMethod",
    "VerifiedEmail",
    "VerifiedEmailRepository",
    "generate_challenge_token",
    "hash_challenge_token",
]
