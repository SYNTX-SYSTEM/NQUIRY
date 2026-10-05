"""The login lockout boundary at the login contact (WU-AUTH-20; 24 §21.16,
§22.3). Decides BEFORE any credential work and records AFTER the outcome,
in the login's own transaction.

    locked(email, client)      → any key locked now → LOGIN_RATE_LIMITED (audited, class only)
    failed(email, client)      → both windows advance; a key reaching its threshold locks
    succeeded(email)           → the CREDENTIAL window is cleared

The keys are digests of the typed address and of the client address; an
address that names no account has a window like any other (no enumeration).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from persistence.auth_rate_limit_repository import SqlAlchemyAuthRateLimitRepository
from security.login_throttle import ThrottleKeyKind, ThrottlePolicy, next_window, throttle_key


class LoginThrottle:
    def __init__(self, connection: Any, *, policy: ThrottlePolicy) -> None:
        self._repo = SqlAlchemyAuthRateLimitRepository(connection)
        self._policy = policy

    @staticmethod
    def _keys(email: str, client: str | None) -> tuple[tuple[ThrottleKeyKind, str], ...]:
        keys: list[tuple[ThrottleKeyKind, str]] = [
            (ThrottleKeyKind.CREDENTIAL, throttle_key(ThrottleKeyKind.CREDENTIAL, email))
        ]
        if client:
            keys.append((ThrottleKeyKind.CLIENT, throttle_key(ThrottleKeyKind.CLIENT, client)))
        return tuple(keys)

    def locked(self, email: str, client: str | None, *, now: datetime) -> bool:
        for kind, key_hash in self._keys(email, client):
            window = self._repo.get(kind, key_hash)
            if window is not None and window.locked(now):
                return True
        return False

    def failed(self, email: str, client: str | None, *, now: datetime) -> bool:
        """Records the failure on every key; True when a key is now locked."""
        locked_now = False
        for kind, key_hash in self._keys(email, client):
            current = self._repo.get(kind, key_hash, for_update=True)
            window = next_window(
                current, kind=kind, key_hash=key_hash, now=now, policy=self._policy
            )
            self._repo.put(window, now=now)
            locked_now = locked_now or window.locked(now)
        return locked_now

    def succeeded(self, email: str, *, now: datetime) -> None:
        self._repo.clear(
            ThrottleKeyKind.CREDENTIAL, throttle_key(ThrottleKeyKind.CREDENTIAL, email), now=now
        )


__all__ = ["LoginThrottle"]
