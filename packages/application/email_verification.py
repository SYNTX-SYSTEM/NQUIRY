"""Email verification effect gate (24 §16.1, §19.4, §33.11, §42; WU-AUTH-11).

VERIFICATION START → CHALLENGE ISSUED (hash stored, token delivered)
VERIFICATION COMPLETE → CHALLENGE PROOF (one conditional consume)
→ VERIFIED EMAIL RELATION → audit.

- Delivery is not verification; issuing a challenge writes no verified relation.
- Completion requires the session of the identity the challenge was issued to
  (a wrong identity is denied without touching the challenge), the challenge
  id AND the token; a wrong token counts one failed attempt, and after
  `MAX_FAILED_ATTEMPTS` the challenge is spent (24 §16.1 "attempt limit").
- Resend is throttled (`RESEND_INTERVAL`); a new challenge supersedes the
  open one (24 §16.1 "resend throttling").
- An address actively verified by another identity is refused at start and at
  completion (24 §14.5: a collision boundary, never a link); a re-verification
  by the same identity supersedes the earlier relation.
- Every issue / completion / failure is a SecurityEvent (24 §16.1, §31.1)
  with the challenge id and an address hash; never the token or the address.

Everything runs in the caller's transaction (HD-6). Failures that must
persist (a counted attempt) are returned to the dispatcher as denials, which
it handles inside the request transaction so that the count commits.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from persistence.verification_repository import (
    SqlAlchemyChallengeRepository,
    SqlAlchemyVerifiedEmailRepository,
)
from security.events import Environment, SecurityEvent, TrustBoundary
from security.mail import CapturedMail, MailSink
from security.verification import (
    ChallengeType,
    VerificationMethod,
    VerifiedEmail,
    generate_challenge_token,
    hash_challenge_token,
)
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

CHALLENGE_LIFETIME = timedelta(minutes=30)
RESEND_INTERVAL = timedelta(seconds=60)
MAX_FAILED_ATTEMPTS = 5
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PROVENANCE = "application.email_verification"


class EmailInvalid(ValueError):
    """The candidate is not an email address; nothing is written."""


class VerificationThrottled(Exception):
    """An open challenge for this address was issued within `RESEND_INTERVAL`."""


class VerificationDenied(Exception):
    """Refused. `reason` is internal evidence (never a public message):
    ADDRESS_VERIFIED_ELSEWHERE, UNKNOWN_CHALLENGE, FOREIGN_CHALLENGE,
    CHALLENGE_CLOSED, CHALLENGE_EXPIRED, ATTEMPTS_EXHAUSTED, TOKEN_MISMATCH."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True, slots=True)
class IssuedChallenge:
    challenge_id: uuid.UUID
    email: str
    expires_at: datetime


def normalize_email(candidate: object) -> str:
    if not isinstance(candidate, str):
        raise EmailInvalid()
    normalized = candidate.strip().lower()
    if not _EMAIL.match(normalized) or len(normalized) > 320:
        raise EmailInvalid()
    return normalized


def _environment(value: Environment | str) -> Environment:
    return value if isinstance(value, Environment) else Environment(value)


def _event(
    connection: Any,
    *,
    event_type: str,
    user_id: UserId,
    environment: Environment,
    now: datetime,
    facts: dict[str, object],
) -> None:
    SqlAlchemySecurityEventRepository(connection).record(
        SecurityEvent(
            security_event_id=SecurityEventId(uuid.uuid4()),
            occurred_at=now,
            environment=environment,
            actor_type="HUMAN_USER",
            actor_id=str(user_id.value),
            trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
            event_type=event_type,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=f"user:{user_id.value}",
            observed_facts=json.dumps(facts, sort_keys=True),
            audit_linkage=f"user:{user_id.value}",
        )
    )


def _email_hash(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]


def issue_challenge(
    connection: Any,
    *,
    user_id: UserId,
    email: object,
    now: datetime,
    environment: Environment | str,
    mail_sink: MailSink,
) -> IssuedChallenge:
    address = normalize_email(email)
    env = _environment(environment)
    verified = SqlAlchemyVerifiedEmailRepository(connection)
    active = verified.active_for_email(address)
    if active is not None and active.user_id != user_id:
        raise VerificationDenied("ADDRESS_VERIFIED_ELSEWHERE")
    challenges = SqlAlchemyChallengeRepository(connection)
    latest = challenges.latest_open(
        challenge_type=ChallengeType.EMAIL_VERIFICATION, user_id=user_id, email=address
    )
    if latest is not None and now - latest.issued_at < RESEND_INTERVAL:
        raise VerificationThrottled()
    challenges.revoke_open(
        challenge_type=ChallengeType.EMAIL_VERIFICATION,
        user_id=user_id,
        email=address,
        revoked_at=now,
    )
    token = generate_challenge_token()
    record = challenges.create(
        challenge_type=ChallengeType.EMAIL_VERIFICATION,
        user_id=user_id,
        email=address,
        token_hash=hash_challenge_token(token),
        issued_at=now,
        expires_at=now + CHALLENGE_LIFETIME,
        provenance_ref=_PROVENANCE,
    )
    _event(
        connection,
        event_type="EMAIL_VERIFICATION_ISSUED",
        user_id=user_id,
        environment=env,
        now=now,
        facts={"challengeId": str(record.challenge_id), "emailHash": _email_hash(address)},
    )
    mail_sink.deliver(
        CapturedMail(
            kind="EMAIL_VERIFICATION",
            to=address,
            challenge_id=str(record.challenge_id),
            token=token,
            expires_at=record.expires_at,
        )
    )
    return IssuedChallenge(
        challenge_id=record.challenge_id, email=address, expires_at=record.expires_at
    )


def complete_challenge(
    connection: Any,
    *,
    user_id: UserId,
    challenge_id: uuid.UUID,
    token: str,
    now: datetime,
    environment: Environment | str,
) -> VerifiedEmail:
    env = _environment(environment)
    challenges = SqlAlchemyChallengeRepository(connection)
    record = challenges.get_for_update(challenge_id)
    if record is None or record.challenge_type is not ChallengeType.EMAIL_VERIFICATION:
        raise VerificationDenied("UNKNOWN_CHALLENGE")
    if record.user_id != user_id:
        raise VerificationDenied("FOREIGN_CHALLENGE")
    if record.consumed_at is not None or record.revoked_at is not None:
        raise VerificationDenied("CHALLENGE_CLOSED")
    if record.expires_at <= now:
        raise VerificationDenied("CHALLENGE_EXPIRED")
    if record.failed_attempts >= MAX_FAILED_ATTEMPTS:
        raise VerificationDenied("ATTEMPTS_EXHAUSTED")
    consumed = challenges.consume(
        challenge_id,
        token_hash=hash_challenge_token(token),
        now=now,
        max_failed_attempts=MAX_FAILED_ATTEMPTS,
    )
    if consumed is None:
        attempts = challenges.count_failed_attempt(challenge_id)
        _event(
            connection,
            event_type="EMAIL_VERIFICATION_FAILED",
            user_id=user_id,
            environment=env,
            now=now,
            facts={"challengeId": str(challenge_id), "failedAttempts": attempts},
        )
        raise VerificationDenied("TOKEN_MISMATCH")
    verified = SqlAlchemyVerifiedEmailRepository(connection)
    active = verified.active_for_email(consumed.email)
    if active is not None and active.user_id != user_id:
        raise VerificationDenied("ADDRESS_VERIFIED_ELSEWHERE")
    verified.supersede_active(user_id=user_id, email=consumed.email, superseded_at=now)
    relation = verified.create(
        user_id=user_id,
        email=consumed.email,
        verified_at=now,
        verification_method=VerificationMethod.EMAIL_CHALLENGE,
        provenance_ref=f"challenge:{challenge_id}",
    )
    _event(
        connection,
        event_type="EMAIL_VERIFICATION_COMPLETED",
        user_id=user_id,
        environment=env,
        now=now,
        facts={"challengeId": str(challenge_id), "emailHash": _email_hash(consumed.email)},
    )
    return relation


__all__ = [
    "CHALLENGE_LIFETIME",
    "MAX_FAILED_ATTEMPTS",
    "RESEND_INTERVAL",
    "EmailInvalid",
    "IssuedChallenge",
    "VerificationDenied",
    "VerificationThrottled",
    "complete_challenge",
    "issue_challenge",
    "normalize_email",
]
