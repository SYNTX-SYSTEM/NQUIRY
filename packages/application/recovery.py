"""Recovery effect gate (24 §17, §19.6–19.7, §33.7; WU-AUTH-12).

RECOVERY REQUEST (an address) → eligibility (an identity with that address
as an ACTIVE verified relation AND an ACTIVE local password method) →
RECOVERY CHALLENGE (hash stored, token delivered) → COMPLETE (id + token +
new password) → VERIFIED RECOVERY PROOF (one conditional consume) → RECOVERY
AUTHORITY → credential replaced, every session of the identity revoked
(24 §15.7, §19.6), audit. No session is created (24 §17.5: only after
"explicit session commit", which no policy grants).

The request contact answers identically whether or not anything was issued
(24 §45.2): an unknown, unverified, provider-only or throttled address sends
nothing and says the same. A bad new password is rejected BEFORE the proof is
consumed, so a typo does not spend the challenge.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.recovery_challenge_repository import SqlAlchemyRecoveryChallengeRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from persistence.verification_repository import SqlAlchemyVerifiedEmailRepository
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import SessionRevocationReason, hash_password
from security.mail import CapturedMail, MailSink
from security.recovery import RecoveryType
from security.verification import generate_challenge_token, hash_challenge_token
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

from application.email_verification import EmailInvalid, normalize_email
from application.identity_provisioning import PASSWORD_MAX_CHARS, PASSWORD_MIN_CHARS

RECOVERY_LIFETIME = timedelta(minutes=30)
RESEND_INTERVAL = timedelta(seconds=60)
MAX_FAILED_ATTEMPTS = 5
_PROVENANCE = "application.recovery"


class RecoveryDenied(Exception):
    """Refused; `reason` is internal evidence, never a public message."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class PasswordInvalid(ValueError):
    """The new password does not meet the credential rules; nothing consumed."""


@dataclass(frozen=True, slots=True)
class IssuedRecovery:
    recovery_id: uuid.UUID
    user_id: UserId
    expires_at: datetime


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
            actor_type="RECOVERY_CHALLENGE",
            actor_id=str(user_id.value),
            trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
            event_type=event_type,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=f"user:{user_id.value}",
            observed_facts=json.dumps(facts, sort_keys=True),
            audit_linkage=f"user:{user_id.value}",
        )
    )


def _eligible_identity(connection: Any, address: str) -> UserId | None:
    """The identity that may recover through `address`: its ACTIVE verified
    relation, and an ACTIVE LOCAL_PASSWORD method (24 §17.4 verified email as
    the recovery authority; §17.6 provider loss is not recoverable here)."""
    relation = SqlAlchemyVerifiedEmailRepository(connection).active_for_email(address)
    if relation is None:
        return None
    if SqlAlchemyIdentityRepository(connection).is_disabled(relation.user_id):
        return None  # WU-AUTH-13 (24 §18.2): a disabled identity recovers nothing
    methods = SqlAlchemyAuthenticationMethodRepository(connection).list_for_user(relation.user_id)
    if not any(
        m.method_type is AuthenticationMethodType.LOCAL_PASSWORD
        and m.status is AuthenticationMethodStatus.ACTIVE
        for m in methods
    ):
        return None
    return relation.user_id


def request_recovery(
    connection: Any,
    *,
    email: object,
    now: datetime,
    environment: Environment | str,
    mail_sink: MailSink,
) -> IssuedRecovery | None:
    """Returns the issued challenge, or None when nothing was issued (unknown,
    unverified, provider-only, malformed or throttled). The caller answers the
    same in both cases."""
    try:
        address = normalize_email(email)
    except EmailInvalid:
        return None
    user_id = _eligible_identity(connection, address)
    if user_id is None:
        return None
    env = _environment(environment)
    challenges = SqlAlchemyRecoveryChallengeRepository(connection)
    latest = challenges.latest_open(user_id=user_id, recovery_type=RecoveryType.PASSWORD_RESET)
    if latest is not None and now - latest.issued_at < RESEND_INTERVAL:
        return None
    challenges.revoke_open(
        user_id=user_id, recovery_type=RecoveryType.PASSWORD_RESET, revoked_at=now
    )
    token = generate_challenge_token()
    record = challenges.create(
        user_id=user_id,
        recovery_type=RecoveryType.PASSWORD_RESET,
        challenge_hash=hash_challenge_token(token),
        issued_at=now,
        expires_at=now + RECOVERY_LIFETIME,
        provenance_ref=_PROVENANCE,
    )
    _event(
        connection,
        event_type="RECOVERY_ISSUED",
        user_id=user_id,
        environment=env,
        now=now,
        facts={
            "recoveryId": str(record.recovery_id),
            "recoveryType": RecoveryType.PASSWORD_RESET.value,
        },
    )
    mail_sink.deliver(
        CapturedMail(
            kind="PASSWORD_RECOVERY",
            to=address,
            challenge_id=str(record.recovery_id),
            token=token,
            expires_at=record.expires_at,
        )
    )
    return IssuedRecovery(
        recovery_id=record.recovery_id, user_id=user_id, expires_at=record.expires_at
    )


def validate_new_password(candidate: object) -> str:
    if not isinstance(candidate, str) or not candidate:
        raise PasswordInvalid()
    if candidate != candidate.strip():
        raise PasswordInvalid()
    if not PASSWORD_MIN_CHARS <= len(candidate) <= PASSWORD_MAX_CHARS:
        raise PasswordInvalid()
    return candidate


def complete_recovery(
    connection: Any,
    *,
    recovery_id: uuid.UUID,
    token: str,
    new_password: object,
    now: datetime,
    environment: Environment | str,
) -> UserId:
    """24 §19.6 reset commit: verified recovery proof → new credential hash
    persisted → dependent sessions revoked → audit."""
    password = validate_new_password(new_password)
    env = _environment(environment)
    challenges = SqlAlchemyRecoveryChallengeRepository(connection)
    record = challenges.get_for_update(recovery_id)
    if record is None or record.recovery_type is not RecoveryType.PASSWORD_RESET:
        raise RecoveryDenied("UNKNOWN_RECOVERY")
    if record.consumed_at is not None or record.revoked_at is not None:
        raise RecoveryDenied("RECOVERY_CLOSED")
    if record.expires_at <= now:
        raise RecoveryDenied("RECOVERY_EXPIRED")
    if record.failed_attempts >= MAX_FAILED_ATTEMPTS:
        raise RecoveryDenied("ATTEMPTS_EXHAUSTED")
    consumed = challenges.verify_and_consume(
        recovery_id,
        challenge_hash=hash_challenge_token(token),
        now=now,
        max_failed_attempts=MAX_FAILED_ATTEMPTS,
    )
    if consumed is None:
        attempts = challenges.count_failed_attempt(recovery_id)
        _event(
            connection,
            event_type="RECOVERY_FAILED",
            user_id=record.user_id,
            environment=env,
            now=now,
            facts={"recoveryId": str(recovery_id), "failedAttempts": attempts},
        )
        raise RecoveryDenied("TOKEN_MISMATCH")
    user_id = consumed.user_id
    if SqlAlchemyIdentityRepository(connection).is_disabled(user_id):
        raise RecoveryDenied("ACCOUNT_DISABLED")  # the proof is consumed, the effect refused
    if not SqlAlchemyLocalCredentialRepository(connection).replace_password(
        user_id=user_id, password_hash=hash_password(password), now=now
    ):
        raise RecoveryDenied("NO_LOCAL_CREDENTIAL")
    revoked = SqlAlchemyLocalSessionRepository(connection).revoke_all_for_user(
        user_id, revoked_at=now, reason=SessionRevocationReason.CREDENTIAL_RESET
    )
    _event(
        connection,
        event_type="PASSWORD_RESET",
        user_id=user_id,
        environment=env,
        now=now,
        facts={"recoveryId": str(recovery_id), "sessionsRevoked": revoked},
    )
    _event(
        connection,
        event_type="RECOVERY_COMPLETED",
        user_id=user_id,
        environment=env,
        now=now,
        facts={"recoveryId": str(recovery_id), "effect": "PASSWORD_RESET"},
    )
    return user_id


__all__ = [
    "MAX_FAILED_ATTEMPTS",
    "RECOVERY_LIFETIME",
    "RESEND_INTERVAL",
    "IssuedRecovery",
    "PasswordInvalid",
    "RecoveryDenied",
    "complete_recovery",
    "request_recovery",
    "validate_new_password",
]
