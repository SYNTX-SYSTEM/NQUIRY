"""Real local login: verifies a password credential, issues a genuine,
server-verified HTTP session, and resolves that session back to a real
`security.identity.AuthenticatedPrincipal`.

Closes the disclosed GAP-14-001 weakness
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`
recorded: `application.http_dispatch.resolve_actor` trusted a bare
request header at face value, "no cryptographic verification ...
anywhere in this path". GAP-14-001 itself (real OIDC provider
selection) remains open — this module never talks to an external
identity provider. HARD-DEP-001 (legitimate first Workspace
governance-root bootstrap) is untouched: this module resolves WHO a
user is, never WHICH Workspace/governance root they may legitimately
act as — that remains `authority.resolver.AuthorityResolver`'s own,
separate job.

A session resolved here is ALWAYS `authority.actor.ActorClass.HUMAN_USER`
— a real password login has no mechanism to authenticate as
`SYSTEM_SERVICE`/`AI_PROCESSOR`/`EXTERNAL_SYSTEM`, so this module
structurally cannot produce one (see `http_dispatch.py`'s own updated
docstring for what this means for the two production HTTP routes: the
`x-nquiry-actor-class` header these routes previously trusted is now
fully inert dead input, proven by the mandatory adversarial test).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from security.identity import AuthenticatedPrincipal
from security.local_auth import (
    LocalCredentialRepository,
    LocalSessionRepository,
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from semantic_types.ids import UserId

SESSION_LIFETIME = timedelta(hours=12)
_ISSUER_REF = "nquiry-local-credential-adapter"

# A precomputed, fixed dummy hash -- `login` always runs one
# `verify_password` call, win or lose, so that the wall-clock time of a
# response does not disclose whether `email` is a registered account
# (a classic user-enumeration timing side channel). Computed once at
# import time (one real PBKDF2 pass, ~tens of milliseconds), not per
# call, using the real `hash_password` so its shape (iterations/salt/
# digest length) can never silently drift from what `verify_password`
# actually expects.
_DUMMY_HASH = hash_password("not-a-real-password-used-only-for-timing-parity")


class InvalidCredentials(Exception):
    """Wrong email, wrong password, or an email with no registered
    credential at all -- deliberately ONE exception for all three, so a
    caller (and an attacker) cannot distinguish "unknown email" from
    "wrong password" (mandatory adversarial property: no user
    enumeration via the error message)."""


@dataclass(frozen=True, slots=True)
class LoginSuccess:
    user_id: UserId
    session_token: str
    expires_at: datetime


def login(
    email: str,
    password: str,
    *,
    credential_repository: LocalCredentialRepository,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> LoginSuccess:
    """Verifies `email`/`password` against a real, persisted
    `local_auth_credentials` row and, only on success, issues a real
    `local_auth_sessions` row. Raises `InvalidCredentials` (fails
    closed) for an unknown email, a wrong password, or an empty
    password — never silently succeeds.

    `password` has its surrounding whitespace stripped before
    comparison (same treatment `email` already gets) -- a real-world
    failure mode found during this field's own human verification pass:
    copying a password out of a chat message/terminal easily picks up
    a trailing newline/space, which a byte-exact comparison would
    reject even though the visible password is correct. `hash_password`/
    `verify_password` themselves (`security.local_auth`) stay
    deliberately byte-exact -- normalizing "what counts as the same
    password" is a login-boundary policy decision, not something the
    underlying crypto primitive should silently decide. This stays
    consistent because every current credential-creation call site
    (`scripts/seed_local_demo.py`, every test's own `hash_password(...)`
    call) passes a literal Python string with no accidental whitespace
    -- never a human-typed/pasted value -- so there is no call site
    where a credential could legitimately be CREATED with meaningful
    leading/trailing whitespace in the first place; only LOGIN input
    (typed or pasted by a human) needs this normalization."""
    normalized_email = email.strip().lower()
    normalized_password = password.strip()
    record = credential_repository.get_by_email(normalized_email)
    if record is None:
        verify_password(
            normalized_password, _DUMMY_HASH
        )  # constant-effort decoy, see module docstring
        raise InvalidCredentials("unknown email or wrong password")
    if not normalized_password or not verify_password(normalized_password, record.password_hash):
        raise InvalidCredentials("unknown email or wrong password")

    raw_token = generate_session_token()
    expires_at = now + SESSION_LIFETIME
    session_repository.create(
        user_id=record.user_id,
        session_token_hash=hash_session_token(raw_token),
        issued_at=now,
        expires_at=expires_at,
    )
    return LoginSuccess(user_id=record.user_id, session_token=raw_token, expires_at=expires_at)


def resolve_session(
    raw_token: str | None,
    *,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> AuthenticatedPrincipal | None:
    """Verifies `raw_token` (the `nquiry_session` cookie value) against
    a real, persisted `local_auth_sessions` row. Returns `None` — never
    raises — for: no token, an unknown/garbage/tampered token, a
    revoked session, or an expired session. Every one of these is a
    distinct, independently-tested failure mode (see
    `tests/e2e/test_auth_handler.py`); all collapse to the same `None`
    here so a caller cannot distinguish them (same non-enumeration
    principle as `login`'s own `InvalidCredentials`)."""
    if not raw_token:
        return None
    record = session_repository.get_by_token_hash(hash_session_token(raw_token))
    if record is None:
        return None
    if record.revoked_at is not None:
        return None
    if record.expires_at <= now:
        return None
    return AuthenticatedPrincipal(
        user_id=record.user_id,
        authentication_session_ref=f"local-session:{record.session_id}",
        authentication_time=record.issued_at,
        issuer_ref=_ISSUER_REF,
    )


def logout(
    raw_token: str | None,
    *,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> None:
    """Revokes the session `raw_token` names, if any. A missing/unknown
    token is a silent no-op — logging out twice, or logging out with no
    session at all, is not an error."""
    if not raw_token:
        return
    session_repository.revoke(hash_session_token(raw_token), revoked_at=now)


__all__ = [
    "SESSION_LIFETIME",
    "InvalidCredentials",
    "LoginSuccess",
    "login",
    "resolve_session",
    "logout",
]
