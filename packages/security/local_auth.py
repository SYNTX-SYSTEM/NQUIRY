"""Local, deterministic credential + session identity adapter.

Source: 14_IMPLEMENTATION_SEQUENCE.md §32 ("pluggable OIDC adapter plus
deterministic test adapter `[IMPLEMENTATION CHOICE]`") — this is the
"deterministic test adapter" half of that authorized pair, hardened
into a REAL local login usable in an actual browser (not merely a
pytest fixture). It closes the specific, disclosed GAP-14-001 weakness
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`
recorded: `application.http_dispatch.resolve_actor` trusted a bare
`x-nquiry-actor-user-id` request header at face value, with "no
cryptographic verification ... anywhere in this path". GAP-14-001
itself (real OIDC provider selection) remains open — this module never
talks to an external identity provider, and does not claim to.

HARD-DEP-001 (legitimate first Workspace governance-root bootstrap) is
untouched by this module: it authenticates WHO a user is, never WHICH
Workspace/governance root they may legitimately act as — that question
is `authority.resolver.AuthorityResolver`'s job, orthogonal and
unchanged.

Two independent secrets, two independent hashes, by design:

- A password is verified against `local_auth_credentials.password_hash`
  (PBKDF2-HMAC-SHA256, random per-credential salt, `hash_password`/
  `verify_password` below).
- A session is verified against `local_auth_sessions.session_token_hash`
  (plain SHA-256 of a high-entropy random token, `generate_session_token`/
  `hash_session_token` below) — SHA-256, not PBKDF2, is correct here:
  the session token itself is already 256 bits of real randomness (not
  a human-guessable secret the way a password is), so the hash only
  needs to prevent "read the DB, replay the raw token" (a fast hash is
  fine and desirable — a session is looked up on every single request).
  Storing only the hash means a DB read alone (without the cookie a
  browser holds) can never reconstruct a usable session.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from semantic_types.ids import UserId

_PBKDF2_ALGORITHM = "sha256"
_PBKDF2_ITERATIONS = 600_000  # OWASP 2023 minimum for PBKDF2-HMAC-SHA256
_SALT_BYTES = 16
_SESSION_TOKEN_BYTES = 32
_ENCODED_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """Returns `'pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>'`. A
    fresh random salt is drawn every call, so hashing the same password
    twice never produces the same output (see the mandatory adversarial
    test: an attacker with DB read access cannot spot two users sharing
    a password by comparing stored hashes)."""
    if not password:
        raise ValueError("password must not be empty")
    salt = os.urandom(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return f"{_ENCODED_PREFIX}${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Fails closed on ANY malformed/foreign/tampered `encoded` value —
    never raises past this boundary (a raised exception here would
    crash the login request instead of simply failing the login)."""
    parts = encoded.split("$")
    if len(parts) != 4:
        return False
    algorithm, iterations_str, salt_hex, digest_hex = parts
    if algorithm != _ENCODED_PREFIX:
        return False
    try:
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except ValueError:
        return False
    if iterations <= 0:
        return False
    candidate = hashlib.pbkdf2_hmac(_PBKDF2_ALGORITHM, password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def generate_session_token() -> str:
    """A fresh, high-entropy (256-bit), URL-safe raw session token. This
    is the value set in the browser's `nquiry_session` cookie — never
    persisted anywhere raw, only as `hash_session_token`'s own output
    (see this module's own docstring)."""
    return secrets.token_urlsafe(_SESSION_TOKEN_BYTES)


def hash_session_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LocalCredentialRecord:
    user_id: UserId
    email: str
    password_hash: str


@dataclass(frozen=True, slots=True)
class LocalSessionRecord:
    session_id: uuid.UUID
    user_id: UserId
    session_token_hash: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None


class LocalCredentialRepository(Protocol):
    """Port: look up a local password credential by email. Concrete
    adapter: `persistence.local_auth_repository.SqlAlchemyLocalCredentialRepository`."""

    def get_by_email(self, email: str) -> LocalCredentialRecord | None: ...


class LocalSessionRepository(Protocol):
    """Port: create/read/revoke a real, server-verified HTTP session.
    Concrete adapter: `persistence.local_auth_repository.SqlAlchemyLocalSessionRepository`."""

    def create(
        self,
        *,
        user_id: UserId,
        session_token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> LocalSessionRecord: ...

    def get_by_token_hash(self, session_token_hash: str) -> LocalSessionRecord | None: ...

    def revoke(self, session_token_hash: str, *, revoked_at: datetime) -> None: ...


__all__ = [
    "hash_password",
    "verify_password",
    "generate_session_token",
    "hash_session_token",
    "LocalCredentialRecord",
    "LocalSessionRecord",
    "LocalCredentialRepository",
    "LocalSessionRepository",
]
