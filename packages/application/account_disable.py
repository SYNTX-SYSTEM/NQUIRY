"""Account disable (24 §18.1 "account disable"; §18.2 "If account disabled";
§19.2–19.3 "no account disable"; WU-AUTH-13).

THE EFFECT, in ONE transaction (HD-6: the caller's `connect()` commits or
rolls back everything):
- `users.disabled_at` + `disabled_provenance` set once (conditional write;
  one-way at the database);
- every unrevoked session of the identity revoked with ACCOUNT_DISABLED;
- every open recovery challenge of the identity revoked (24 §18.2 "challenge
  cannot restore method or session");
- one SecurityEvent ACCOUNT_DISABLED (TB-17 administrative tooling, actor
  HOST_OPERATOR, non-secret facts).
Authentication methods are NOT rewritten: they stay as they are and are
blocked by the identity's state (login, provider login, session resolution,
recovery and the session INSERT itself all check it). The identity row is not
deleted (24 §18.3 "Deletion is not revocation").

WHO MAY DISABLE: not decided. 24 §36 names administrative recovery (#13) and
HD-28 / NQ-DEC-056 made the host operator the production identity *creator*
only ("any change to an existing identity" is outside that command). The
mechanism therefore exists with the HD-28 shape (an explicitly named host
operator through a server-side command, never an HTTP route) and is admitted
in DEVELOPMENT / TEST only; PRODUCTION / STAGING refuse with
ACCOUNT_DISABLE_EXPOSURE_UNDECIDED until HA-AUTH-04 is decided (24 §17.6
"Default unresolved behavior: fail closed").

Re-enabling a disabled identity is administrative recovery (24 §36 #13) and
is not materialized.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from persistence.recovery_challenge_repository import SqlAlchemyRecoveryChallengeRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import SessionRevocationReason
from security.recovery import RecoveryType
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

from application.identity_provisioning import (
    ACTOR_TYPE,
    ConnectionFactory,
    HostOperator,
    IdentityCreationRefused,
    declared_environment,
)

EVENT_TYPE = "ACCOUNT_DISABLED"
AUTHORITY = "HA-AUTH-04 undecided; DEVELOPMENT / TEST host-operator mechanism"
_ADMITTED = frozenset({Environment.DEVELOPMENT, Environment.TEST})


class AccountDisableRefused(Exception):
    """Nothing was written. `reason_code` is safe to print (never a secret)."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class DisabledIdentity:
    user_id: UserId
    email: str
    sessions_revoked: int
    recovery_challenges_revoked: int
    security_event_id: SecurityEventId
    environment: Environment
    disabled_by: str


def disable_identity_by_host_operator(
    connection: Any,
    *,
    email: str,
    operator: HostOperator,
    reason: str,
    environment: Environment,
    now: datetime,
) -> DisabledIdentity:
    if environment not in _ADMITTED:
        raise AccountDisableRefused("ACCOUNT_DISABLE_EXPOSURE_UNDECIDED")
    operator_id = operator.operator_id.strip()
    if not operator_id:
        raise AccountDisableRefused("OPERATOR_REQUIRED")
    clean_reason = reason.strip()
    if not clean_reason:
        raise AccountDisableRefused("REASON_REQUIRED")
    normalized = email.strip().lower()
    identities = SqlAlchemyIdentityRepository(connection)
    found = identities.find_by_email(normalized)
    if found is None:
        raise AccountDisableRefused("IDENTITY_UNKNOWN")
    user_id, already = found
    if already:
        raise AccountDisableRefused("ALREADY_DISABLED")
    provenance = f"host-operator:{operator_id}:{now.isoformat()}"
    if not identities.disable(user_id, now=now, provenance=provenance):
        raise AccountDisableRefused("ALREADY_DISABLED")  # lost the race: same class
    sessions_revoked = SqlAlchemyLocalSessionRepository(connection).revoke_all_for_user(
        user_id, revoked_at=now, reason=SessionRevocationReason.ACCOUNT_DISABLED
    )
    challenges_revoked = SqlAlchemyRecoveryChallengeRepository(connection).revoke_open(
        user_id=user_id, recovery_type=RecoveryType.PASSWORD_RESET, revoked_at=now
    )
    event_id = SecurityEventId(uuid.uuid4())
    SqlAlchemySecurityEventRepository(connection).record(
        SecurityEvent(
            security_event_id=event_id,
            occurred_at=now,
            environment=environment,
            actor_type=ACTOR_TYPE,
            actor_id=operator_id,
            trust_boundary=TrustBoundary.TB_17_ADMINISTRATIVE_TOOLING,
            event_type=EVENT_TYPE,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=f"user:{user_id.value}",
            observed_facts=json.dumps(
                {
                    "authority": AUTHORITY,
                    "reason": clean_reason,
                    "sessionsRevoked": sessions_revoked,
                    "recoveryChallengesRevoked": challenges_revoked,
                    "methods": "BLOCKED_NOT_REWRITTEN",
                    "osUser": operator.os_user,
                    "host": operator.host,
                },
                sort_keys=True,
            ),
            audit_linkage=f"user:{user_id.value}",
        )
    )
    return DisabledIdentity(
        user_id=user_id,
        email=normalized,
        sessions_revoked=sessions_revoked,
        recovery_challenges_revoked=challenges_revoked,
        security_event_id=event_id,
        environment=environment,
        disabled_by=operator_id,
    )


def run_host_operator_disable(
    *,
    email: str,
    reason: str,
    operator: HostOperator,
    environment_raw: str | None,
    now: datetime,
    connect: ConnectionFactory | None = None,
) -> DisabledIdentity:
    """The command's single entry: declared environment (AC-11-017), then one
    committed transaction."""
    try:
        environment = declared_environment(environment_raw)
    except IdentityCreationRefused as exc:
        raise AccountDisableRefused(exc.reason_code) from exc
    if connect is None:
        from persistence.engine import connect as default_connect

        connect = default_connect
    with connect() as connection:
        return disable_identity_by_host_operator(
            connection,
            email=email,
            operator=operator,
            reason=reason,
            environment=environment,
            now=now,
        )


__all__ = [
    "AUTHORITY",
    "EVENT_TYPE",
    "AccountDisableRefused",
    "DisabledIdentity",
    "disable_identity_by_host_operator",
    "run_host_operator_disable",
]
