"""OIDC start / callback dispatch (24 §11.18, §11.16, §16.2, §19.9–19.12,
§23.4–23.6; WU-AUTH-07). The composition root for the provider login contacts.

TRANSACTION BOUNDARIES. The callback runs in three request transactions on
purpose: (1) validation and the atomic claim are committed BEFORE the token
exchange, so PROCESSING is authoritative state even if the process dies
during the exchange (24 §11.7–11.8); (2) the exchange and the ID Token
validation touch no database; (3) the local effect gate and the terminal
transaction state commit together. A failure in (2) or (3) is written as
FAILED_TERMINAL in its own transaction: the transaction never returns to
PENDING (24 §11.9, §19.11).

PROJECTIONS (24 §11.16, §24.6, §32.3): every non-success ends at
`/login?auth=<projection>` with one of `cancelled`, `provider_unavailable`,
`provider_error`, `failed`, `unavailable`. Security-sensitive distinctions
stay in the transaction's `failure_reason`; the browser sees a class, never a
code, a token, a verifier or a state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from persistence.engine import connect
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from persistence.oidc_transaction_repository import SqlAlchemyOidcTransactionRepository
from security.oidc_provider import (
    IdTokenInvalid,
    ProviderExchangeRejected,
    ProviderExchangeUncertain,
    VerifiedProviderCredential,
)
from security.oidc_transaction import OidcFailureReason, OidcTransactionPurpose

from application.auth_handler import issue_session
from application.auth_runtime import AuthRuntime, auth_runtime_from_environment
from application.oidc_identity import ProviderIdentityUnresolved, resolve_provider_identity
from application.oidc_transactions import (
    DEFAULT_TRANSACTION_LIFETIME,
    TransactionRejected,
    cancel_transaction,
    claim_transaction,
    complete_transaction,
    fail_transaction,
    start_transaction,
)

BINDING_COOKIE_NAME = "nquiry_oidc_binding"
BINDING_COOKIE_PATH = "/auth"
LOGIN_PROJECTION_BASE = "/login?auth="
_PROVIDER_UNAVAILABLE_ERRORS = frozenset({"temporarily_unavailable", "server_error"})
# Refusals of the account creation boundary: "signing in with this provider is
# not available for this account" (24 §24.6), as opposed to a failed proof.
_UNAVAILABLE_REASONS = frozenset(
    {
        OidcFailureReason.ACCOUNT_CREATION_POLICY_UNRESOLVED,
        OidcFailureReason.PROVIDER_EMAIL_MISSING,
        OidcFailureReason.PROVIDER_EMAIL_UNVERIFIED,
        OidcFailureReason.EMAIL_COLLISION,
    }
)

_runtime: AuthRuntime | None = None


def configure_auth_runtime(runtime: AuthRuntime) -> None:
    global _runtime
    _runtime = runtime


def current_auth_runtime() -> AuthRuntime:
    global _runtime
    if _runtime is None:
        _runtime = auth_runtime_from_environment()
    return _runtime


@dataclass(frozen=True, slots=True)
class OidcDispatchResult:
    """A redirect (`location`) or a JSON answer (`status_code` + `body`), plus
    cookie effects for the thin HTTP adapter."""

    status_code: int
    body: dict[str, object] | None = None
    location: str | None = None
    binding_token: str | None = None
    binding_max_age: int | None = None
    clear_binding: bool = False
    session_token: str | None = None
    session_expires_at: datetime | None = None


def _projection(name: str) -> OidcDispatchResult:
    return OidcDispatchResult(303, location=f"{LOGIN_PROJECTION_BASE}{name}", clear_binding=True)


def dispatch_list_providers() -> dict[str, object]:
    """`GET /auth/providers`: which provider contacts exist for this runtime
    (24 §24.2: a button only for a configured backend)."""
    runtime = current_auth_runtime()
    return {
        "kind": "ok",
        "providers": [
            {
                "providerId": provider.provider_id,
                "label": provider.label,
                "proofClass": provider.proof_class,
            }
            for provider in runtime.providers.values()
        ],
    }


def dispatch_oidc_start(*, provider_id: str, redirect_candidate: str | None) -> OidcDispatchResult:
    """`GET /auth/oidc/{provider}/start` (24 §23.4)."""
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return OidcDispatchResult(
            503, body={"kind": "unavailable", "reasonCode": "PROVIDER_NOT_CONFIGURED"}
        )
    now = datetime.now(timezone.utc)
    with connect() as connection:
        started = start_transaction(
            SqlAlchemyOidcTransactionRepository(connection),
            provider=provider.provider_id,
            purpose=OidcTransactionPurpose.LOGIN,
            initiating_user_id=None,
            redirect_target=redirect_candidate,
            now=now,
        )
    return OidcDispatchResult(
        303,
        location=provider.authorization_url(
            state=started.state, nonce=started.nonce, code_challenge=started.code_challenge
        ),
        binding_token=started.binding_token,
        binding_max_age=int(DEFAULT_TRANSACTION_LIFETIME.total_seconds()),
    )


def _fail(transaction_id: object, reason: OidcFailureReason, *, now: datetime) -> None:
    with connect() as connection:
        fail_transaction(
            SqlAlchemyOidcTransactionRepository(connection),
            transaction_id,  # type: ignore[arg-type]
            reason=reason.value,
            now=now,
        )


def dispatch_oidc_callback(
    *, provider_id: str, params: dict[str, str], binding_token: str | None
) -> OidcDispatchResult:
    """`GET /auth/oidc/{provider}/callback`: 24 §16.2 steps 1–24."""
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return _projection("unavailable")
    now = datetime.now(timezone.utc)
    state = params.get("state")

    error = params.get("error")
    if error:
        reason = provider.normalize_error(error)
        with connect() as connection:
            try:
                cancel_transaction(
                    SqlAlchemyOidcTransactionRepository(connection),
                    state=state,
                    binding_token=binding_token,
                    reason=reason.value,
                    now=now,
                )
            except TransactionRejected:
                return _projection("failed")
        if reason is OidcFailureReason.USER_CANCEL:
            return _projection("cancelled")
        if error in _PROVIDER_UNAVAILABLE_ERRORS:
            return _projection("provider_unavailable")
        return _projection("provider_error")

    code = params.get("code")
    if not code or not state:
        return _projection("failed")  # 24 §11.16 malformed callback: no effect

    # (1) local validation and the atomic claim, committed before any exchange.
    with connect() as connection:
        try:
            claimed = claim_transaction(
                SqlAlchemyOidcTransactionRepository(connection),
                state=state,
                binding_token=binding_token,
                purpose=OidcTransactionPurpose.LOGIN,
                initiating_user_id=None,
                now=now,
            )
        except TransactionRejected:
            return _projection("failed")

    # (2) provider proof: exchange with the original verifier, then validation.
    try:
        raw_id_token = provider.exchange_code(code=code, code_verifier=claimed.code_verifier)
    except ProviderExchangeRejected:
        _fail(claimed.transaction_id, OidcFailureReason.TOKEN_EXCHANGE_REJECTED, now=now)
        return _projection("failed")
    except ProviderExchangeUncertain:
        _fail(claimed.transaction_id, OidcFailureReason.TOKEN_EXCHANGE_OUTCOME_UNCERTAIN, now=now)
        return _projection("failed")
    try:
        credential: VerifiedProviderCredential = provider.validate_id_token(
            raw_id_token, expected_nonce_hash=claimed.nonce_hash
        )
    except IdTokenInvalid as invalid:
        _fail(claimed.transaction_id, invalid.reason, now=now)
        return _projection("failed")

    # (3) the local effect gate, the fresh session and the terminal state:
    # one transaction. A refusal or a failure inside it rolls that transaction
    # back (no partial identity, 24 §19.11) and the refusal is then written as
    # FAILED_TERMINAL in its own transaction (24 §11.15).
    runtime = current_auth_runtime()
    try:
        with connect() as connection:
            resolved = resolve_provider_identity(
                connection,
                credential,
                now=now,
                policy=runtime.account_creation_policy,
                environment=runtime.environment,
            )
            session = issue_session(
                SqlAlchemyLocalSessionRepository(connection),
                user_id=resolved.user_id,
                method_id=resolved.method_id,
                now=now,
            )
            complete_transaction(
                SqlAlchemyOidcTransactionRepository(connection), claimed.transaction_id, now=now
            )
    except ProviderIdentityUnresolved as unresolved:
        _fail(claimed.transaction_id, unresolved.reason, now=now)
        if unresolved.reason in _UNAVAILABLE_REASONS:
            return _projection("unavailable")
        return _projection("failed")
    except Exception:  # noqa: BLE001 -- any local failure after provider proof is terminal
        _fail(claimed.transaction_id, OidcFailureReason.LOCAL_EFFECT_FAILURE, now=now)
        return _projection("failed")
    return OidcDispatchResult(
        303,
        location=claimed.redirect_target,
        clear_binding=True,
        session_token=session.session_token,
        session_expires_at=session.expires_at,
    )


__all__ = [
    "BINDING_COOKIE_NAME",
    "BINDING_COOKIE_PATH",
    "LOGIN_PROJECTION_BASE",
    "OidcDispatchResult",
    "configure_auth_runtime",
    "current_auth_runtime",
    "dispatch_list_providers",
    "dispatch_oidc_callback",
    "dispatch_oidc_start",
]
