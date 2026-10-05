"""The authentication audit vocabulary (24 §31.1; WU-AUTH-18).

The closed set of SecurityEvent types the authentication relations emit for
the human-facing effects of 24 §31.1 that had no event yet: local login
(success / failure), logout, session revocation (one / all), the provider
protocol (start, terminal outcomes) and the provider login's own outcome.
The relations that already emitted their event keep it unchanged
(`AUTH_METHOD_LINKED`, `AUTH_METHOD_UNLINKED`, `IDENTITY_CREATED`,
`ACCOUNT_DISABLED`, `EMAIL_VERIFICATION_*`, `RECOVERY_*`, `PASSWORD_RESET`).

PRIVACY (24 §31.3): an event names ids and classes, never a value — no
password, session token, state, nonce, code, verifier, provider token or
e-mail address, and for a failed login no account at all ("aggregated
safely": the failure class only, actor = the unauthenticated client).
"""

from __future__ import annotations

from enum import Enum


class AuthAuditEvent(Enum):
    LOGIN_SUCCEEDED = "LOGIN_SUCCEEDED"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    SESSION_REVOKED = "SESSION_REVOKED"
    ALL_SESSIONS_REVOKED = "ALL_SESSIONS_REVOKED"
    PROVIDER_LOGIN_STARTED = "PROVIDER_LOGIN_STARTED"
    PROVIDER_LINK_STARTED = "PROVIDER_LINK_STARTED"
    PROVIDER_LOGIN_SUCCEEDED = "PROVIDER_LOGIN_SUCCEEDED"
    PROVIDER_LOGIN_UNAVAILABLE = "PROVIDER_LOGIN_UNAVAILABLE"
    OIDC_TRANSACTION_FAILED = "OIDC_TRANSACTION_FAILED"
    OIDC_TRANSACTION_CANCELLED = "OIDC_TRANSACTION_CANCELLED"
    # WU-AUTH-19 credential rotation (24 §9.2)
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_CHANGE_FAILED = "PASSWORD_CHANGE_FAILED"


ACTOR_UNAUTHENTICATED = "UNAUTHENTICATED_CLIENT"
"""The actor of an event before or without an identity (a failed login, a
protocol start, a failed callback): never an account, never an address."""

FORBIDDEN_FACT_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "token",
        "sessionToken",
        "state",
        "nonce",
        "code",
        "verifier",
        "codeVerifier",
        "accessToken",
        "refreshToken",
        "idToken",
        "clientSecret",
        "email",
        "subject",
        "providerSubject",
    }
)
"""Fact keys an authentication audit event may never carry (24 §31.3)."""


__all__ = ["ACTOR_UNAUTHENTICATED", "FORBIDDEN_FACT_KEYS", "AuthAuditEvent"]
