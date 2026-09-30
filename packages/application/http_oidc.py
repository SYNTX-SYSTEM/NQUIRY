"""OIDC start / callback dispatch for LOGIN and ACCOUNT_LINK (24 §11.16,
§11.18, §14.2, §16.2, §19.5, §19.9–19.12, §23.4–23.6; WU-AUTH-07, -08, -09, -10).
The composition root for the provider contacts.

TRANSACTION BOUNDARIES. A callback runs in three request transactions on
purpose: (1) validation and the atomic claim are committed BEFORE the token
exchange, so PROCESSING is authoritative state even if the process dies
during the exchange (24 §11.7–11.8); (2) the exchange and the ID Token
validation touch no database; (3) the local effect gate (identity resolution
or link), the session effect and the terminal transaction state commit
together. A refusal or failure in (2) or (3) is written as FAILED_TERMINAL in
its own transaction: the transaction never returns to PENDING and a partial
local effect never persists (24 §11.9, §11.15, §19.11).

PURPOSES. The LOGIN contacts (`/auth/oidc/{p}/start`, `/callback`) and the
ACCOUNT_LINK contacts (`/auth/oidc/{p}/link/start`, `/link/callback`) are
separate routes with separate registered redirect URIs, so a transaction of
one purpose cannot be consumed by the other's callback (PURPOSE_MISMATCH). A
link additionally binds the initiating identity, checked against the current
session before the claim (24 §14.2).

PROJECTIONS (24 §11.16, §24.6, §32.3): a login non-success ends at
`/login?auth=<projection>`; a link outcome at the bound local target with
`?link=<projection>` (`ok`, `already_linked`, `collision`, `cancelled`,
`failed`). The browser sees a class, never a code, token, verifier or state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from persistence.engine import connect
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from persistence.oidc_transaction_repository import SqlAlchemyOidcTransactionRepository
from security.oidc_provider import (
    IdTokenInvalid,
    OidcProvider,
    ProviderExchangeRejected,
    ProviderExchangeUncertain,
    VerifiedProviderCredential,
)
from security.oidc_transaction import OidcFailureReason, OidcTransactionPurpose
from semantic_types.ids import UserId

from application.auth_handler import (
    SessionRequired,
    issue_session,
    resolve_session,
    rotate_session,
)
from application.auth_runtime import AuthRuntime, auth_runtime_from_environment
from application.oidc_identity import (
    ProviderIdentityUnresolved,
    link_provider_identity,
    list_methods,
    resolve_provider_identity,
)
from application.oidc_transactions import (
    DEFAULT_TRANSACTION_LIFETIME,
    ClaimedTransaction,
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
ACCOUNT_SECURITY_DESTINATION = "/account/security"
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
_NO_SESSION_BODY: dict[str, object] = {"kind": "denied", "reasonCode": "NO_SESSION"}

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


def _login_projection(name: str) -> OidcDispatchResult:
    return OidcDispatchResult(303, location=f"{LOGIN_PROJECTION_BASE}{name}", clear_binding=True)


def _link_location(name: str, target: str = ACCOUNT_SECURITY_DESTINATION) -> str:
    joiner = "&" if "?" in target else "?"
    return f"{target}{joiner}link={name}"


def _link_projection(name: str, target: str = ACCOUNT_SECURITY_DESTINATION) -> OidcDispatchResult:
    return OidcDispatchResult(303, location=_link_location(name, target), clear_binding=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _current_user(session_token: str | None, *, now: datetime) -> UserId | None:
    with connect() as connection:
        principal = resolve_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection), now=now
        )
    return None if principal is None else principal.user_id


# --------------------------------------------------------------- providers


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


def dispatch_list_methods(*, session_token: str | None) -> tuple[int, dict[str, object]]:
    """`GET /auth/methods` (24 §23.2, §24.5): the caller's own authentication
    methods with their provider attribute, never a secret or a subject."""
    runtime = current_auth_runtime()
    issuers = {provider.issuer: provider.provider_id for provider in runtime.providers.values()}
    with connect() as connection:
        try:
            methods = list_methods(
                connection,
                session_token,
                session_repository=SqlAlchemyLocalSessionRepository(connection),
                now=_now(),
            )
        except SessionRequired:
            return 401, _NO_SESSION_BODY
    return 200, {
        "kind": "ok",
        "methods": [
            {
                "methodId": str(item.method_id.value),
                "methodType": item.method_type.value,
                "status": item.status.value,
                "createdAt": item.created_at.isoformat(),
                "lastAuthenticatedAt": (
                    None
                    if item.last_authenticated_at is None
                    else item.last_authenticated_at.isoformat()
                ),
                "provider": (
                    None
                    if item.provider_issuer is None
                    else {
                        "providerId": issuers.get(item.provider_issuer, item.provider_issuer),
                        "email": item.provider_email,
                    }
                ),
            }
            for item in methods
        ],
    }


# -------------------------------------------------------------------- start


def _redirect_uri_for(provider: OidcProvider, purpose: OidcTransactionPurpose) -> str:
    if purpose is OidcTransactionPurpose.ACCOUNT_LINK:
        return provider.link_redirect_uri
    return provider.redirect_uri


def _start(
    provider: OidcProvider,
    *,
    purpose: OidcTransactionPurpose,
    initiating_user_id: UserId | None,
    redirect_candidate: object,
    now: datetime,
) -> OidcDispatchResult:
    with connect() as connection:
        started = start_transaction(
            SqlAlchemyOidcTransactionRepository(connection),
            provider=provider.provider_id,
            purpose=purpose,
            initiating_user_id=initiating_user_id,
            redirect_target=redirect_candidate,
            now=now,
        )
    return OidcDispatchResult(
        303,
        location=provider.authorization_url(
            state=started.state,
            nonce=started.nonce,
            code_challenge=started.code_challenge,
            redirect_uri=_redirect_uri_for(provider, purpose),
        ),
        binding_token=started.binding_token,
        binding_max_age=int(DEFAULT_TRANSACTION_LIFETIME.total_seconds()),
    )


def _unconfigured() -> OidcDispatchResult:
    return OidcDispatchResult(
        503, body={"kind": "unavailable", "reasonCode": "PROVIDER_NOT_CONFIGURED"}
    )


def dispatch_oidc_start(*, provider_id: str, redirect_candidate: str | None) -> OidcDispatchResult:
    """`GET /auth/oidc/{provider}/start` (24 §23.4)."""
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return _unconfigured()
    return _start(
        provider,
        purpose=OidcTransactionPurpose.LOGIN,
        initiating_user_id=None,
        redirect_candidate=redirect_candidate,
        now=_now(),
    )


def dispatch_oidc_link_start(
    *, provider_id: str, session_token: str | None, redirect_candidate: str | None
) -> OidcDispatchResult:
    """`POST /auth/oidc/{provider}/link/start` (24 §14.2): only for an
    authenticated identity; the transaction binds it."""
    now = _now()
    user_id = _current_user(session_token, now=now)
    if user_id is None:
        return OidcDispatchResult(401, body=_NO_SESSION_BODY)
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return _unconfigured()
    return _start(
        provider,
        purpose=OidcTransactionPurpose.ACCOUNT_LINK,
        initiating_user_id=user_id,
        redirect_candidate=redirect_candidate or ACCOUNT_SECURITY_DESTINATION,
        now=now,
    )


# ----------------------------------------------------------------- callback


def _fail(transaction_id: object, reason: OidcFailureReason, *, now: datetime) -> None:
    with connect() as connection:
        fail_transaction(
            SqlAlchemyOidcTransactionRepository(connection),
            transaction_id,  # type: ignore[arg-type]
            reason=reason.value,
            now=now,
        )


@dataclass(frozen=True, slots=True)
class _Proof:
    claimed: ClaimedTransaction
    credential: VerifiedProviderCredential


def _protocol_steps(
    provider: OidcProvider,
    *,
    purpose: OidcTransactionPurpose,
    params: dict[str, str],
    binding_token: str | None,
    initiating_user_id: UserId | None,
    now: datetime,
) -> _Proof | str:
    """24 §16.2 steps 1–20 for either purpose. Returns the proof, or the name
    of the projection to answer with (the transaction is by then terminal or
    untouched, as the rules require)."""
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
                return "failed"
        if reason is OidcFailureReason.USER_CANCEL:
            return "cancelled"
        if error in _PROVIDER_UNAVAILABLE_ERRORS:
            return "provider_unavailable"
        return "provider_error"

    code = params.get("code")
    if not code or not state:
        return "failed"  # 24 §11.16 malformed callback: no effect

    # (1) local validation and the atomic claim, committed before any exchange.
    with connect() as connection:
        try:
            claimed = claim_transaction(
                SqlAlchemyOidcTransactionRepository(connection),
                state=state,
                binding_token=binding_token,
                purpose=purpose,
                initiating_user_id=initiating_user_id,
                now=now,
            )
        except TransactionRejected:
            return "failed"

    # (2) provider proof: exchange with the original verifier, then validation.
    try:
        raw_id_token = provider.exchange_code(
            code=code,
            code_verifier=claimed.code_verifier,
            redirect_uri=_redirect_uri_for(provider, purpose),
        )
    except ProviderExchangeRejected:
        _fail(claimed.transaction_id, OidcFailureReason.TOKEN_EXCHANGE_REJECTED, now=now)
        return "failed"
    except ProviderExchangeUncertain:
        _fail(claimed.transaction_id, OidcFailureReason.TOKEN_EXCHANGE_OUTCOME_UNCERTAIN, now=now)
        return "failed"
    try:
        credential = provider.validate_id_token(
            raw_id_token, expected_nonce_hash=claimed.nonce_hash
        )
    except IdTokenInvalid as invalid:
        _fail(claimed.transaction_id, invalid.reason, now=now)
        return "failed"
    return _Proof(claimed=claimed, credential=credential)


def dispatch_oidc_callback(
    *, provider_id: str, params: dict[str, str], binding_token: str | None
) -> OidcDispatchResult:
    """`GET /auth/oidc/{provider}/callback`: 24 §16.2 steps 1–24 for LOGIN."""
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return _login_projection("unavailable")
    now = _now()
    proof = _protocol_steps(
        provider,
        purpose=OidcTransactionPurpose.LOGIN,
        params=params,
        binding_token=binding_token,
        initiating_user_id=None,
        now=now,
    )
    if isinstance(proof, str):
        return _login_projection(proof)
    claimed, credential = proof.claimed, proof.credential

    # (3) the local effect gate, the fresh session and the terminal state:
    # one transaction; a refusal or failure rolls it back and is then
    # recorded as FAILED_TERMINAL in its own transaction.
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
            return _login_projection("unavailable")
        return _login_projection("failed")
    except Exception:  # noqa: BLE001 -- any local failure after provider proof is terminal
        _fail(claimed.transaction_id, OidcFailureReason.LOCAL_EFFECT_FAILURE, now=now)
        return _login_projection("failed")
    return OidcDispatchResult(
        303,
        location=claimed.redirect_target,
        clear_binding=True,
        session_token=session.session_token,
        session_expires_at=session.expires_at,
    )


def dispatch_oidc_link_callback(
    *,
    provider_id: str,
    params: dict[str, str],
    binding_token: str | None,
    session_token: str | None,
) -> OidcDispatchResult:
    """`GET /auth/oidc/{provider}/link/callback` (24 §14.2, §19.5): the same
    protocol steps with purpose ACCOUNT_LINK and the current identity as the
    initiating user; then the link effect and a session rotation (24 §15.6)."""
    provider = current_auth_runtime().provider(provider_id)
    if provider is None:
        return _link_projection("failed")
    now = _now()
    user_id = _current_user(session_token, now=now)
    proof = _protocol_steps(
        provider,
        purpose=OidcTransactionPurpose.ACCOUNT_LINK,
        params=params,
        binding_token=binding_token,
        initiating_user_id=user_id,
        now=now,
    )
    if isinstance(proof, str):
        if user_id is None:
            return _login_projection("failed")
        return _link_projection(proof if proof == "cancelled" else "failed")
    claimed, credential = proof.claimed, proof.credential
    if user_id is None:  # cannot happen: the claim verified the initiating user
        _fail(claimed.transaction_id, OidcFailureReason.INITIATING_USER_MISMATCH, now=now)
        return _login_projection("failed")
    runtime = current_auth_runtime()
    try:
        with connect() as connection:
            outcome = link_provider_identity(
                connection, credential, user_id=user_id, now=now, environment=runtime.environment
            )
            rotated = rotate_session(
                session_token,
                session_repository=SqlAlchemyLocalSessionRepository(connection),
                now=now,
            )
            complete_transaction(
                SqlAlchemyOidcTransactionRepository(connection), claimed.transaction_id, now=now
            )
    except ProviderIdentityUnresolved as unresolved:
        _fail(claimed.transaction_id, unresolved.reason, now=now)
        if unresolved.reason is OidcFailureReason.PROVIDER_SUBJECT_COLLISION:
            return _link_projection("collision", claimed.redirect_target)
        return _link_projection("failed", claimed.redirect_target)
    except Exception:  # noqa: BLE001 -- any local failure after provider proof is terminal
        _fail(claimed.transaction_id, OidcFailureReason.LOCAL_EFFECT_FAILURE, now=now)
        return _link_projection("failed", claimed.redirect_target)
    return OidcDispatchResult(
        303,
        location=_link_location(
            "already_linked" if outcome.already_linked else "ok", claimed.redirect_target
        ),
        clear_binding=True,
        session_token=rotated.session_token,
        session_expires_at=rotated.expires_at,
    )


__all__ = [
    "ACCOUNT_SECURITY_DESTINATION",
    "BINDING_COOKIE_NAME",
    "BINDING_COOKIE_PATH",
    "LOGIN_PROJECTION_BASE",
    "OidcDispatchResult",
    "configure_auth_runtime",
    "current_auth_runtime",
    "dispatch_list_methods",
    "dispatch_list_providers",
    "dispatch_oidc_callback",
    "dispatch_oidc_link_callback",
    "dispatch_oidc_link_start",
    "dispatch_oidc_start",
]
