"""The OIDC Auth Transaction Field: types, protocol helpers and port
(24 §11.3–11.11, §13.4–13.7, §22.6–22.7; WU-AUTH-05).

An OIDC transaction is the temporary authoritative relation between a provider
login start and its callback. It is not a provider identity, not an
authentication method and not a session (24 §13.4). It binds, for one
start: the purpose (LOGIN or ACCOUNT_LINK, with the initiating user for a
link), the protected expected state, the expected nonce, the initiating
user-agent, the confidential PKCE verifier, the validated post-auth redirect
target and an expiry.

STATE MACHINE (24 §11.4). PENDING → PROCESSING (the one atomic claim) →
COMPLETED | FAILED_TERMINAL; PENDING → EXPIRED | CANCELLED_TERMINAL |
FAILED_TERMINAL. PROCESSING never returns to PENDING; a terminal state never
changes. `is_legal_transition` is the single table; the database trigger
mirrors it for every writer.

PROTOCOL MATERIAL. `state`, `nonce` and the user-agent binding token are
random 256-bit values; only their SHA-256 hashes are stored (they are
compared, never recovered). The PKCE `code_verifier` is different (24 §11.10,
§22.6): it must be presented to the token endpoint, so it is stored in a
recoverable server-side form while PENDING, handed out exactly once, in the
same statement that claims the transaction, and absent from the row from
that moment on. Hash-only storage is forbidden (falsifier 78).

`derive_code_challenge` is RFC 7636 S256: BASE64URL(SHA256(ASCII(verifier)))
without padding.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from semantic_types.ids import UserId


class OidcTransactionPurpose(Enum):
    LOGIN = "LOGIN"
    ACCOUNT_LINK = "ACCOUNT_LINK"


class OidcTransactionState(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    EXPIRED = "EXPIRED"
    CANCELLED_TERMINAL = "CANCELLED_TERMINAL"


TERMINAL_STATES: frozenset[OidcTransactionState] = frozenset(
    {
        OidcTransactionState.COMPLETED,
        OidcTransactionState.FAILED_TERMINAL,
        OidcTransactionState.EXPIRED,
        OidcTransactionState.CANCELLED_TERMINAL,
    }
)

_LEGAL_TRANSITIONS: frozenset[tuple[OidcTransactionState, OidcTransactionState]] = frozenset(
    {
        (OidcTransactionState.PENDING, OidcTransactionState.PROCESSING),
        (OidcTransactionState.PENDING, OidcTransactionState.EXPIRED),
        (OidcTransactionState.PENDING, OidcTransactionState.CANCELLED_TERMINAL),
        (OidcTransactionState.PENDING, OidcTransactionState.FAILED_TERMINAL),
        (OidcTransactionState.PROCESSING, OidcTransactionState.COMPLETED),
        (OidcTransactionState.PROCESSING, OidcTransactionState.FAILED_TERMINAL),
    }
)


def is_legal_transition(origin: OidcTransactionState, target: OidcTransactionState) -> bool:
    return (origin, target) in _LEGAL_TRANSITIONS


class OidcFailureReason(Enum):
    """24 §32.2: the internal failure classes. Public responses may collapse
    them; the transaction keeps the exact one."""

    MISSING_TRANSACTION = "MISSING_TRANSACTION"
    EXPIRED_TRANSACTION = "EXPIRED_TRANSACTION"
    INVALID_STATE = "INVALID_STATE"
    USER_AGENT_BINDING_MISSING = "USER_AGENT_BINDING_MISSING"
    USER_AGENT_BINDING_MISMATCH = "USER_AGENT_BINDING_MISMATCH"
    PURPOSE_MISMATCH = "PURPOSE_MISMATCH"
    INITIATING_USER_MISMATCH = "INITIATING_USER_MISMATCH"
    ALREADY_PROCESSING = "ALREADY_PROCESSING"
    ALREADY_COMPLETED = "ALREADY_COMPLETED"
    CANCELLED_TERMINAL = "CANCELLED_TERMINAL"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    EXPIRED = "EXPIRED"
    MISSING_PKCE_VERIFIER = "MISSING_PKCE_VERIFIER"
    TOKEN_EXCHANGE_REJECTED = "TOKEN_EXCHANGE_REJECTED"
    TOKEN_EXCHANGE_OUTCOME_UNCERTAIN = "TOKEN_EXCHANGE_OUTCOME_UNCERTAIN"
    INVALID_ID_TOKEN_SIGNATURE = "INVALID_ID_TOKEN_SIGNATURE"
    INVALID_ISSUER = "INVALID_ISSUER"
    INVALID_AUDIENCE = "INVALID_AUDIENCE"
    EXPIRED_ID_TOKEN = "EXPIRED_ID_TOKEN"
    INVALID_NONCE = "INVALID_NONCE"
    PROVIDER_SUBJECT_MISSING = "PROVIDER_SUBJECT_MISSING"
    PROVIDER_SUBJECT_COLLISION = "PROVIDER_SUBJECT_COLLISION"
    PROVIDER_ACCESS_DENIED = "PROVIDER_ACCESS_DENIED"
    USER_CANCEL = "USER_CANCEL"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    MALFORMED_CALLBACK = "MALFORMED_CALLBACK"
    REDIRECT_TARGET_REJECTED = "REDIRECT_TARGET_REJECTED"
    ACCOUNT_CREATION_POLICY_UNRESOLVED = "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    ACCOUNT_LINK_AUTHORITY_FAILURE = "ACCOUNT_LINK_AUTHORITY_FAILURE"
    LOCAL_EFFECT_FAILURE = "LOCAL_EFFECT_FAILURE"
    AUTHENTICATION_METHOD_REVOKED = "AUTHENTICATION_METHOD_REVOKED"  # WU-AUTH-08


_TOKEN_BYTES = 32  # 256 bits; `token_urlsafe` renders 43 characters
_VERIFIER_BYTES = 64  # 86 characters, inside RFC 7636's 43..128


def generate_protocol_token() -> str:
    """A fresh state, nonce or user-agent binding token."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def generate_code_verifier() -> str:
    """RFC 7636 §4.1: unreserved characters only, 43..128 long.
    `token_urlsafe` is base64url, a subset of the unreserved set."""
    return secrets.token_urlsafe(_VERIFIER_BYTES)


def derive_code_challenge(code_verifier: str) -> str:
    """RFC 7636 §4.2, S256."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def hash_protocol_value(value: str) -> str:
    """The stored binding of a state, nonce or binding token. Compared with
    a freshly hashed candidate; the raw value is never recovered."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class OidcTransactionRecord:
    """One row, as read. `code_verifier` is never part of a read: it leaves
    the row only through `claim`."""

    transaction_id: uuid.UUID
    provider: str
    purpose: OidcTransactionPurpose
    initiating_user_id: UserId | None
    state: OidcTransactionState
    state_hash: str
    nonce_hash: str
    user_agent_binding_hash: str
    code_challenge: str
    redirect_target: str
    created_at: datetime
    expires_at: datetime
    claimed_at: datetime | None
    failure_reason: OidcFailureReason | None


class OidcTransactionRepository(Protocol):
    """Port. Adapter:
    `persistence.oidc_transaction_repository.SqlAlchemyOidcTransactionRepository`."""

    def create(
        self,
        *,
        transaction_id: uuid.UUID,
        provider: str,
        purpose: OidcTransactionPurpose,
        initiating_user_id: UserId | None,
        state_hash: str,
        nonce_hash: str,
        user_agent_binding_hash: str,
        code_verifier: str,
        code_challenge: str,
        redirect_target: str,
        created_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> None: ...

    def get_by_state_hash(self, state_hash: str) -> OidcTransactionRecord | None: ...

    def get(self, transaction_id: uuid.UUID) -> OidcTransactionRecord | None: ...

    def claim(self, transaction_id: uuid.UUID, *, now: datetime) -> str | None:
        """The atomic PENDING → PROCESSING claim (24 §11.7, §22.7). Returns
        the original code verifier to the one caller whose statement made the
        transition; None for everyone else. After it the row holds no
        verifier."""
        ...

    def terminalize(
        self,
        transaction_id: uuid.UUID,
        *,
        from_state: OidcTransactionState,
        to_state: OidcTransactionState,
        reason: OidcFailureReason | None,
        now: datetime,
    ) -> bool:
        """Conditional transition into a terminal state; False when the
        transaction is no longer in `from_state`."""
        ...


__all__ = [
    "TERMINAL_STATES",
    "OidcFailureReason",
    "OidcTransactionPurpose",
    "OidcTransactionRecord",
    "OidcTransactionRepository",
    "OidcTransactionState",
    "derive_code_challenge",
    "generate_code_verifier",
    "generate_protocol_token",
    "hash_protocol_value",
    "is_legal_transition",
]
