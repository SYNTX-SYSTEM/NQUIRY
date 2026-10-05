"""The runtime DB-principal capability map of authentication persistence
(24 §21.18; WU-AUTH-17; FBR-AUTH-006).

`auth_runtime` is the database principal under which the live authentication
persistence paths may run (login and sessions, provider transactions and
identities, verification, recovery, revocation, the host-operator identity
commands). It receives exactly the capabilities below — SELECT / INSERT /
UPDATE on the authentication relations, INSERT only on the audit it appends
to — and nothing else: no business or authority relation, no DELETE anywhere
(revocation preserves evidence, 24 §18.3), no read of the audit.

The map is the single source for the migration that grants it and for the
proof that measures it (`tests/security/test_auth_db_principal.py`: every
table of the database, every privilege, over a real connection as that
principal). Business principals that serve HTTP requests need the one auth
read every governed request makes — resolving the session cookie — and get
SELECT on exactly those tables.

Who runs the live deployment under this principal is a deployment action
(PFC HA-10): the runtime declares its scope, it never claims one.
"""

from __future__ import annotations

from collections.abc import Mapping

AUTH_RUNTIME_PRINCIPAL = "auth_runtime"

_RW: frozenset[str] = frozenset({"SELECT", "INSERT", "UPDATE"})

AUTH_PERSISTENCE_CAPABILITIES: Mapping[str, frozenset[str]] = {
    "users": _RW,  # identity rows: created by policy / operator, disabled, never deleted
    "local_auth_credentials": _RW,
    "local_auth_sessions": _RW,
    "authentication_methods": _RW,
    "external_provider_identities": _RW,
    "oidc_auth_transactions": _RW,
    "auth_challenges": _RW,
    "verified_emails": _RW,
    "recovery_challenges": _RW,
    "auth_rate_limits": _RW,  # WU-AUTH-20: the login lockout boundary's windows
    "security_events": frozenset({"INSERT"}),  # append-only audit (11 §47)
}

SESSION_RESOLUTION_READ_TABLES: frozenset[str] = frozenset(
    {"local_auth_sessions", "authentication_methods", "users"}
)
SESSION_RESOLVING_PRINCIPALS: tuple[str, ...] = ("api_reader", "governed_commit_writer")

__all__ = [
    "AUTH_PERSISTENCE_CAPABILITIES",
    "AUTH_RUNTIME_PRINCIPAL",
    "SESSION_RESOLUTION_READ_TABLES",
    "SESSION_RESOLVING_PRINCIPALS",
]
