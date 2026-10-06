"""The login lockout boundary (24 §21.16 "IP/user/email-keyed rate limits,
lockout policy"; §22.3 "credential validity requires … no active
lockout/rate-limit boundary"; WU-AUTH-20).

Pure vocabulary and arithmetic; persistence lives in
`persistence.auth_rate_limit_repository`, the decision in
`application.login_throttle`.

    key = SHA-256(kind || normalized value)      never the address, never the identity
    window: failures counted since `window_started_at`; a failure after the
            window elapsed starts a new window
    lock:   when `failures` reaches the kind's threshold inside its window,
            `locked_until = now + lock duration`; while locked, every attempt is
            refused BEFORE any credential work (constant for known and unknown
            addresses: enumeration resistance), and the lock is not extended
            by refused attempts (a locked attacker cannot keep a victim locked
            out indefinitely by hammering)
    reset:  a successful login clears the CREDENTIAL key; the CLIENT key keeps
            its window (a client that succeeds once is not thereby trusted)

Thresholds (24 §36 #17: adjustable by product / security policy; these are
the fail-closed defaults, overridable per deployment through
`NQUIRY_LOGIN_LOCKOUT_FAILURES` / `NQUIRY_LOGIN_LOCKOUT_MINUTES` for the
CREDENTIAL key, and ten times the failures for the CLIENT key):
CREDENTIAL 5 failures / 15 min → locked 15 min; CLIENT 50 failures / 15 min →
locked 15 min.

WU-AUTH-22 (HD-AUTH-13): REGISTRATION — a CLIENT-address key counting every
self-registration attempt (each one costs a message): 5 attempts / 15 min →
locked 15 min (`NQUIRY_REGISTRATION_ATTEMPTS` overrides the count).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

DEFAULT_CREDENTIAL_FAILURES = 5
DEFAULT_WINDOW = timedelta(minutes=15)
DEFAULT_LOCK = timedelta(minutes=15)
CLIENT_FAILURE_MULTIPLIER = 10
DEFAULT_REGISTRATION_ATTEMPTS = 5


class ThrottleKeyKind(Enum):
    CREDENTIAL = "CREDENTIAL"
    CLIENT = "CLIENT"
    REGISTRATION = "REGISTRATION"  # WU-AUTH-22: self-registration attempts per client


@dataclass(frozen=True, slots=True)
class ThrottlePolicy:
    credential_failures: int = DEFAULT_CREDENTIAL_FAILURES
    window: timedelta = DEFAULT_WINDOW
    lock: timedelta = DEFAULT_LOCK
    registration_attempts: int = DEFAULT_REGISTRATION_ATTEMPTS

    def __post_init__(self) -> None:
        if self.credential_failures < 1 or self.registration_attempts < 1:
            raise ValueError("credential_failures and registration_attempts must be >= 1")
        if self.window <= timedelta(0) or self.lock <= timedelta(0):
            raise ValueError("window and lock must be positive")

    def threshold(self, kind: ThrottleKeyKind) -> int:
        if kind is ThrottleKeyKind.CREDENTIAL:
            return self.credential_failures
        if kind is ThrottleKeyKind.REGISTRATION:
            return self.registration_attempts
        return self.credential_failures * CLIENT_FAILURE_MULTIPLIER


@dataclass(frozen=True, slots=True)
class ThrottleWindow:
    """One `auth_rate_limits` row as read."""

    kind: ThrottleKeyKind
    key_hash: str
    window_started_at: datetime
    failures: int
    locked_until: datetime | None

    def locked(self, now: datetime) -> bool:
        return self.locked_until is not None and self.locked_until > now


def throttle_key(kind: ThrottleKeyKind, value: str) -> str:
    """The stored key: a digest of the kind and the normalized value. Lower-cased
    and stripped so the same address is one key however it was typed."""
    normalized = value.strip().lower()
    return hashlib.sha256(f"{kind.value}:{normalized}".encode()).hexdigest()


def next_window(
    current: ThrottleWindow | None,
    *,
    kind: ThrottleKeyKind,
    key_hash: str,
    now: datetime,
    policy: ThrottlePolicy,
) -> ThrottleWindow:
    """The window after one more failure at `now` (pure)."""
    if current is None or now - current.window_started_at >= policy.window:
        failures, started = 1, now
    else:
        failures, started = current.failures + 1, current.window_started_at
    locked_until = current.locked_until if current is not None else None
    if failures >= policy.threshold(kind) and (locked_until is None or locked_until <= now):
        locked_until = now + policy.lock
    return ThrottleWindow(
        kind=kind,
        key_hash=key_hash,
        window_started_at=started,
        failures=failures,
        locked_until=locked_until,
    )


__all__ = [
    "CLIENT_FAILURE_MULTIPLIER",
    "DEFAULT_CREDENTIAL_FAILURES",
    "DEFAULT_LOCK",
    "DEFAULT_REGISTRATION_ATTEMPTS",
    "DEFAULT_WINDOW",
    "ThrottleKeyKind",
    "ThrottlePolicy",
    "ThrottleWindow",
    "next_window",
    "throttle_key",
]
