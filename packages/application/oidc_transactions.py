"""OIDC transaction effect gate (24 §19.9; WU-AUTH-05).

Start, claim, complete, fail and cancel an OIDC auth transaction. This module
owns the protocol-state relations of 24 §11.3–11.9 and nothing else: no
provider call, no ID Token, no identity, no session. Those consume what this
module returns (WU-AUTH-07 onward).

CLAIM ORDER (24 §16.2 steps 1–10, §11.18): lookup by state → state PENDING →
initiating user-agent binding → expiry → purpose → initiating user when
ACCOUNT_LINK → atomic claim → the verifier, to the winner only. A security
failure before the claim (foreign user-agent, wrong purpose, wrong initiating
user) terminalizes the transaction as FAILED_TERMINAL: callback material that
reached the wrong context is not left usable (24 §11.4 "security validation
failed in a way that makes reuse unsafe"). An expired transaction becomes
EXPIRED at the moment it is met.

Provider cancel/error (24 §11.16) validates the same relations up to the
expiry and then terminalizes as CANCELLED_TERMINAL: no claim, no verifier, no
token exchange, no local effect.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from security.oidc_transaction import (
    OidcFailureReason,
    OidcTransactionPurpose,
    OidcTransactionRecord,
    OidcTransactionRepository,
    OidcTransactionState,
    derive_code_challenge,
    generate_code_verifier,
    generate_protocol_token,
    hash_protocol_value,
)
from security.redirect_target import resolve_redirect_target
from semantic_types.ids import UserId

DEFAULT_TRANSACTION_LIFETIME = timedelta(minutes=10)
_PROVENANCE = "application.oidc_transactions.start_transaction"


class TransactionRejected(Exception):
    """The callback (or cancel) does not continue. `reason` is one
    `OidcFailureReason` value; it is internal evidence, not a public message."""

    def __init__(self, reason: OidcFailureReason) -> None:
        self.reason = reason.value
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class StartedTransaction:
    """What a login start hands to the provider redirect and the browser:
    the raw state and nonce (they travel through the protocol), the code
    challenge (never the verifier) and the user-agent binding token (for the
    browser's pre-auth cookie). The verifier stays on the server."""

    transaction_id: uuid.UUID
    provider: str
    purpose: OidcTransactionPurpose
    state: str
    nonce: str
    code_challenge: str
    binding_token: str
    redirect_target: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ClaimedTransaction:
    """What the winning callback processor holds: the verifier for the token
    exchange and the expected-nonce binding for validation after the ID
    Token has been validated (24 §11.12)."""

    transaction_id: uuid.UUID
    provider: str
    purpose: OidcTransactionPurpose
    initiating_user_id: UserId | None
    nonce_hash: str
    code_verifier: str
    redirect_target: str


@dataclass(frozen=True, slots=True)
class CancelledTransaction:
    transaction_id: uuid.UUID
    redirect_target: str


def start_transaction(
    repository: OidcTransactionRepository,
    *,
    provider: str,
    purpose: OidcTransactionPurpose,
    initiating_user_id: UserId | None,
    redirect_target: object,
    now: datetime,
    lifetime: timedelta = DEFAULT_TRANSACTION_LIFETIME,
) -> StartedTransaction:
    """24 §11.2 / §23.4. `redirect_target` is a CANDIDATE (24 §22.8): it is
    validated here (WU-AUTH-06) and only a legitimate local destination, or
    the safe default, is bound. The database refuses anything else as well."""
    if (purpose is OidcTransactionPurpose.ACCOUNT_LINK) != (initiating_user_id is not None):
        raise ValueError("ACCOUNT_LINK binds an initiating user; LOGIN binds none")
    state, nonce, binding = (
        generate_protocol_token(),
        generate_protocol_token(),
        generate_protocol_token(),
    )
    verifier = generate_code_verifier()
    challenge = derive_code_challenge(verifier)
    destination = resolve_redirect_target(redirect_target)
    transaction_id = uuid.uuid4()
    repository.create(
        transaction_id=transaction_id,
        provider=provider,
        purpose=purpose,
        initiating_user_id=initiating_user_id,
        state_hash=hash_protocol_value(state),
        nonce_hash=hash_protocol_value(nonce),
        user_agent_binding_hash=hash_protocol_value(binding),
        code_verifier=verifier,
        code_challenge=challenge,
        redirect_target=destination,
        created_at=now,
        expires_at=now + lifetime,
        provenance_ref=_PROVENANCE,
    )
    return StartedTransaction(
        transaction_id=transaction_id,
        provider=provider,
        purpose=purpose,
        state=state,
        nonce=nonce,
        code_challenge=challenge,
        binding_token=binding,
        redirect_target=destination,
        expires_at=now + lifetime,
    )


_STATE_REASON = {
    OidcTransactionState.PROCESSING: OidcFailureReason.ALREADY_PROCESSING,
    OidcTransactionState.COMPLETED: OidcFailureReason.ALREADY_COMPLETED,
    OidcTransactionState.FAILED_TERMINAL: OidcFailureReason.FAILED_TERMINAL,
    OidcTransactionState.EXPIRED: OidcFailureReason.EXPIRED,
    OidcTransactionState.CANCELLED_TERMINAL: OidcFailureReason.CANCELLED_TERMINAL,
}


def _fail_pending(
    repository: OidcTransactionRepository,
    record: OidcTransactionRecord,
    reason: OidcFailureReason,
    *,
    now: datetime,
) -> TransactionRejected:
    repository.terminalize(
        record.transaction_id,
        from_state=OidcTransactionState.PENDING,
        to_state=OidcTransactionState.FAILED_TERMINAL,
        reason=reason,
        now=now,
    )
    return TransactionRejected(reason)


def _validate_pending(
    repository: OidcTransactionRepository,
    *,
    state: str | None,
    binding_token: str | None,
    now: datetime,
) -> OidcTransactionRecord:
    """Steps 1–6 of 24 §16.2, shared by the success and the cancel path."""
    if not state:
        raise TransactionRejected(OidcFailureReason.MISSING_TRANSACTION)
    record = repository.get_by_state_hash(hash_protocol_value(state))
    if record is None:
        raise TransactionRejected(OidcFailureReason.MISSING_TRANSACTION)
    if record.state is not OidcTransactionState.PENDING:
        raise TransactionRejected(_STATE_REASON[record.state])
    if not binding_token:
        raise _fail_pending(
            repository, record, OidcFailureReason.USER_AGENT_BINDING_MISSING, now=now
        )
    if hash_protocol_value(binding_token) != record.user_agent_binding_hash:
        raise _fail_pending(
            repository, record, OidcFailureReason.USER_AGENT_BINDING_MISMATCH, now=now
        )
    if record.expires_at <= now:
        repository.terminalize(
            record.transaction_id,
            from_state=OidcTransactionState.PENDING,
            to_state=OidcTransactionState.EXPIRED,
            reason=None,
            now=now,
        )
        raise TransactionRejected(OidcFailureReason.EXPIRED_TRANSACTION)
    return record


def claim_transaction(
    repository: OidcTransactionRepository,
    *,
    state: str | None,
    binding_token: str | None,
    purpose: OidcTransactionPurpose,
    initiating_user_id: UserId | None,
    now: datetime,
) -> ClaimedTransaction:
    """Steps 1–10 of 24 §16.2. `purpose` is the purpose of the route the
    callback arrived on; `initiating_user_id` is the currently authenticated
    identity, required to match for ACCOUNT_LINK."""
    record = _validate_pending(repository, state=state, binding_token=binding_token, now=now)
    if record.purpose is not purpose:
        raise _fail_pending(repository, record, OidcFailureReason.PURPOSE_MISMATCH, now=now)
    if record.purpose is OidcTransactionPurpose.ACCOUNT_LINK and (
        initiating_user_id is None or initiating_user_id != record.initiating_user_id
    ):
        raise _fail_pending(repository, record, OidcFailureReason.INITIATING_USER_MISMATCH, now=now)
    verifier = repository.claim(record.transaction_id, now=now)
    if verifier is None:
        current = repository.get(record.transaction_id)
        if current is None or current.state is OidcTransactionState.PENDING:
            raise TransactionRejected(OidcFailureReason.MISSING_PKCE_VERIFIER)
        raise TransactionRejected(_STATE_REASON[current.state])
    return ClaimedTransaction(
        transaction_id=record.transaction_id,
        provider=record.provider,
        purpose=record.purpose,
        initiating_user_id=record.initiating_user_id,
        nonce_hash=record.nonce_hash,
        code_verifier=verifier,
        redirect_target=record.redirect_target,
    )


def complete_transaction(
    repository: OidcTransactionRepository, transaction_id: uuid.UUID, *, now: datetime
) -> None:
    """PROCESSING → COMPLETED after the local effect gate committed."""
    if not repository.terminalize(
        transaction_id,
        from_state=OidcTransactionState.PROCESSING,
        to_state=OidcTransactionState.COMPLETED,
        reason=None,
        now=now,
    ):
        raise TransactionRejected(OidcFailureReason.INVALID_STATE)


def fail_transaction(
    repository: OidcTransactionRepository,
    transaction_id: uuid.UUID,
    *,
    reason: str,
    now: datetime,
) -> None:
    """PROCESSING → FAILED_TERMINAL (24 §11.9, §11.15, §19.11): a rejected or
    uncertain exchange, a failed validation or a failed local effect. The
    transaction is never retried; a new login flow is the user's recovery."""
    if not repository.terminalize(
        transaction_id,
        from_state=OidcTransactionState.PROCESSING,
        to_state=OidcTransactionState.FAILED_TERMINAL,
        reason=OidcFailureReason(reason),
        now=now,
    ):
        raise TransactionRejected(OidcFailureReason.INVALID_STATE)


def cancel_transaction(
    repository: OidcTransactionRepository,
    *,
    state: str | None,
    binding_token: str | None,
    reason: str,
    now: datetime,
) -> CancelledTransaction:
    """24 §11.16 provider error / user cancel: validated like a callback up
    to the expiry, then PENDING → CANCELLED_TERMINAL. No claim, no verifier."""
    record = _validate_pending(repository, state=state, binding_token=binding_token, now=now)
    if not repository.terminalize(
        record.transaction_id,
        from_state=OidcTransactionState.PENDING,
        to_state=OidcTransactionState.CANCELLED_TERMINAL,
        reason=OidcFailureReason(reason),
        now=now,
    ):
        current = repository.get(record.transaction_id)
        raise TransactionRejected(
            _STATE_REASON.get(
                current.state if current else OidcTransactionState.FAILED_TERMINAL,
                OidcFailureReason.INVALID_STATE,
            )
        )
    return CancelledTransaction(
        transaction_id=record.transaction_id, redirect_target=record.redirect_target
    )


__all__ = [
    "DEFAULT_TRANSACTION_LIFETIME",
    "CancelledTransaction",
    "ClaimedTransaction",
    "StartedTransaction",
    "TransactionRejected",
    "cancel_transaction",
    "claim_transaction",
    "complete_transaction",
    "fail_transaction",
    "start_transaction",
]
