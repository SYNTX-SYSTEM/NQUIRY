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

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.identity import AuthenticatedPrincipal
from security.local_auth import (
    LocalCredentialRepository,
    LocalSessionRecord,
    LocalSessionRepository,
    SessionRevocationReason,
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from semantic_types.ids import AuthenticationMethodId, UserId

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
    # WU-AUTH-13 (24 §16.3 "no account disable"): after the password, same
    # cost and same answer. The session row itself is refused by the database
    # for a disabled identity, so a disable that commits between this read and
    # `issue_session` still ends without a session (24 §33.7).
    if record.account_disabled:
        raise InvalidCredentials("unknown email or wrong password")
    # WU-AUTH-03 (24 §16.3 "method active"): the credential's method must be
    # ACTIVE. Checked after the password so a revoked method costs the same
    # and answers the same as a wrong password. `mark_authenticated` changes
    # the method row only while it is ACTIVE, so a revocation committed after
    # the credential was read still denies this login.
    if not credential_repository.mark_authenticated(record.method_id, at=now):
        raise InvalidCredentials("unknown email or wrong password")

    return issue_session(
        session_repository, user_id=record.user_id, method_id=record.method_id, now=now
    )


def issue_session(
    session_repository: LocalSessionRepository,
    *,
    user_id: UserId,
    method_id: AuthenticationMethodId,
    now: datetime,
) -> LoginSuccess:
    """The one session producer (24 §19.3): a fresh row with a fresh token,
    attributed to the method whose proof just succeeded. Used by the local
    password login and by the provider callback (WU-AUTH-08). Never reads
    or reuses a token the browser presented (24 §15.4, §21.5)."""
    raw_token = generate_session_token()
    expires_at = now + SESSION_LIFETIME
    session_repository.create(
        user_id=user_id,
        session_token_hash=hash_session_token(raw_token),
        issued_at=now,
        expires_at=expires_at,
        method_id=method_id,
    )
    return LoginSuccess(user_id=user_id, session_token=raw_token, expires_at=expires_at)


def _live_session(
    raw_token: str | None, *, session_repository: LocalSessionRepository, now: datetime
) -> LocalSessionRecord | None:
    """The one definition of "this token names a session that authenticates
    now" (24 §15.3, §15.7; 11 AC-11-002 item 4): the row exists, is not
    revoked, is not expired, the method that produced it, if any, is still
    ACTIVE, and the identity is not disabled. The last two conditions make a
    session die with its method or its identity even before any propagation
    writes `revoked_at` on it (24 falsifier 76; §18.2)."""
    if not raw_token:
        return None
    record = session_repository.get_by_token_hash(hash_session_token(raw_token))
    if record is None:
        return None
    if record.revoked_at is not None:
        return None
    if record.expires_at <= now:
        return None
    if (
        record.method_id is not None
        and record.method_status is not AuthenticationMethodStatus.ACTIVE
    ):
        return None
    if record.account_disabled:  # WU-AUTH-13 (24 §18.2 "If account disabled")
        return None
    return record


def resolve_session(
    raw_token: str | None,
    *,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> AuthenticatedPrincipal | None:
    """Verifies `raw_token` (the `nquiry_session` cookie value) against
    a real, persisted `local_auth_sessions` row. Returns `None` — never
    raises — for: no token, an unknown/garbage/tampered token, a
    revoked session, an expired session, or a session whose authentication
    method has been revoked. Every one of these is a distinct,
    independently-tested failure mode (see `tests/e2e/test_auth_handler.py`,
    `tests/e2e/test_auth_wu04_session_evolution.py`); all collapse to the same
    `None` here so a caller cannot distinguish them (same non-enumeration
    principle as `login`'s own `InvalidCredentials`)."""
    record = _live_session(raw_token, session_repository=session_repository, now=now)
    if record is None:
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
    session at all, is not an error, and a second logout does not rewrite
    the first revocation."""
    if not raw_token:
        return
    session_repository.revoke(
        hash_session_token(raw_token), revoked_at=now, reason=SessionRevocationReason.LOGOUT
    )


class SessionRequired(Exception):
    """The operation acts on the caller's own sessions and the caller
    presented no session that authenticates now. One exception for every
    cause (no token, unknown, revoked, expired, method revoked)."""


@dataclass(frozen=True, slots=True)
class SessionSummary:
    """What the owner of a session may see of it. No token, no token hash."""

    session_id: uuid.UUID
    issued_at: datetime
    expires_at: datetime
    current: bool
    method_type: AuthenticationMethodType | None


def _require_live(
    raw_token: str | None, *, session_repository: LocalSessionRepository, now: datetime
) -> LocalSessionRecord:
    record = _live_session(raw_token, session_repository=session_repository, now=now)
    if record is None:
        raise SessionRequired("no valid session")
    return record


def list_sessions(
    raw_token: str | None, *, session_repository: LocalSessionRepository, now: datetime
) -> tuple[SessionSummary, ...]:
    """The caller's own live sessions, oldest first (24 §21.2 session management)."""
    current = _require_live(raw_token, session_repository=session_repository, now=now)
    return tuple(
        SessionSummary(
            session_id=record.session_id,
            issued_at=record.issued_at,
            expires_at=record.expires_at,
            current=record.session_id == current.session_id,
            method_type=record.method_type,
        )
        for record in session_repository.list_live_for_user(current.user_id, now=now)
    )


def logout_all_sessions(
    raw_token: str | None, *, session_repository: LocalSessionRepository, now: datetime
) -> int:
    """All-session scope (24 §15.7): revokes every unrevoked session of the
    caller's identity, including the presenting one. Returns how many."""
    current = _require_live(raw_token, session_repository=session_repository, now=now)
    return session_repository.revoke_all_for_user(
        current.user_id, revoked_at=now, reason=SessionRevocationReason.ALL_SESSIONS_LOGOUT
    )


def revoke_own_session(
    raw_token: str | None,
    session_id: uuid.UUID,
    *,
    session_repository: LocalSessionRepository,
    now: datetime,
) -> bool:
    """Single-session scope by id: the caller revokes one of their OWN
    sessions. False when `session_id` is unknown, already revoked or belongs
    to another identity; the three are not told apart."""
    current = _require_live(raw_token, session_repository=session_repository, now=now)
    return session_repository.revoke_own(
        session_id,
        user_id=current.user_id,
        revoked_at=now,
        reason=SessionRevocationReason.SESSION_REVOKED,
    )


def rotate_session(
    raw_token: str | None, *, session_repository: LocalSessionRepository, now: datetime
) -> LoginSuccess:
    """Rotation (24 §15.6): the presented session is revoked (ROTATED) and a
    new one with a fresh token takes its place, in the caller's transaction.

    Rotation is not an authentication. The new session keeps the user, the
    method or proof provenance, the original `issued_at` (so
    `authentication_time` stays the time of the real authentication) and the
    original `expires_at` (rotation never extends a session). Only the winner
    of the conditional revocation creates the successor, so a token rotates at
    most once."""
    current = _require_live(raw_token, session_repository=session_repository, now=now)
    if not session_repository.revoke(
        current.session_token_hash, revoked_at=now, reason=SessionRevocationReason.ROTATED
    ):
        raise SessionRequired("no valid session")
    new_token = generate_session_token()
    session_repository.create(
        user_id=current.user_id,
        session_token_hash=hash_session_token(new_token),
        issued_at=current.issued_at,
        expires_at=current.expires_at,
        method_id=current.method_id,
        proof_provenance=current.proof_provenance,
    )
    return LoginSuccess(
        user_id=current.user_id, session_token=new_token, expires_at=current.expires_at
    )


__all__ = [
    "SESSION_LIFETIME",
    "InvalidCredentials",
    "LoginSuccess",
    "SessionRequired",
    "SessionSummary",
    "issue_session",
    "list_sessions",
    "login",
    "logout",
    "logout_all_sessions",
    "resolve_session",
    "revoke_own_session",
    "rotate_session",
]
