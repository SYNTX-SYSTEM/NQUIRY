"""T9: the OIDC Auth Transaction Field (24 WU-AUTH-05; §11.3–11.11, §13.4–13.7,
§22.2–22.3, §22.6–22.7, §33.2–33.3, §33.6, §33.10, §39.2, §39.11;
FBR-AUTH-008, -010, -013, -014).

MUST BECOME TRUE: an OIDC login start creates an authoritative, expiring,
purpose-bound transaction with a protected state binding, an expected-nonce
binding, an initiating user-agent binding and a confidentially retrievable
PKCE verifier; only PENDING can be claimed; the claim is atomic and exactly
one callback wins; only the winner receives the verifier; PROCESSING never
returns to PENDING; every terminal state makes the verifier unavailable and
the user-agent binding invalid; provider cancel/error terminalizes without
any verifier use; an ACCOUNT_LINK transaction binds its initiating user.

MUST REMAIN IMPOSSIBLE: a callback without a transaction; replay of a claimed
or terminal transaction; a LOGIN transaction becoming a LINK; a callback
transplanted into another user-agent; an expired or terminal transaction
reaching the claim; a verifier stored only as a hash, retrieved before the
claim, retrieved by a loser, reused after a terminal state or satisfying
another transaction; raw state, nonce or binding token in the database.
"""

from __future__ import annotations

import base64
import hashlib
import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from application.oidc_transactions import (
    TransactionRejected,
    cancel_transaction,
    claim_transaction,
    complete_transaction,
    fail_transaction,
    start_transaction,
)
from persistence.oidc_transaction_repository import SqlAlchemyOidcTransactionRepository
from persistence.tables import users_table
from security.oidc_transaction import (
    TERMINAL_STATES,
    OidcTransactionPurpose,
    OidcTransactionState,
    derive_code_challenge,
    generate_code_verifier,
    generate_protocol_token,
    hash_protocol_value,
    is_legal_transition,
)
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_LIFETIME = timedelta(minutes=10)
_PROVIDER = "TEST_PROVIDER"
_TARGET = "/workspaces"


def _repo(db: sa.Connection) -> SqlAlchemyOidcTransactionRepository:
    return SqlAlchemyOidcTransactionRepository(db)


def _user(db: sa.Connection) -> UserId:
    user_id = UserId(uuid.uuid4())
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=f"{user_id.value}@example.test",
            name="OIDC",
            record_version=1,
            created_at=_NOW,
            established_at=_NOW,  # WU-AUTH-22: established
            updated_at=_NOW,
        )
    )
    return user_id


def _start(db: sa.Connection, **overrides: object):  # type: ignore[no-untyped-def]
    values: dict[str, object] = {
        "provider": _PROVIDER,
        "purpose": OidcTransactionPurpose.LOGIN,
        "initiating_user_id": None,
        "redirect_target": _TARGET,
        "now": _NOW,
        "lifetime": _LIFETIME,
    }
    values.update(overrides)
    return start_transaction(_repo(db), **values)  # type: ignore[arg-type]


def _row(db: sa.Connection, transaction_id: uuid.UUID) -> sa.RowMapping:
    return (
        db.execute(
            sa.text("SELECT * FROM oidc_auth_transactions WHERE id = :id"), {"id": transaction_id}
        )
        .mappings()
        .one()
    )


def _claim(db: sa.Connection, started, **overrides: object):  # type: ignore[no-untyped-def]
    values: dict[str, object] = {
        "state": started.state,
        "binding_token": started.binding_token,
        "purpose": OidcTransactionPurpose.LOGIN,
        "initiating_user_id": None,
        "now": _NOW + timedelta(minutes=1),
    }
    values.update(overrides)
    return claim_transaction(_repo(db), **values)  # type: ignore[arg-type]


def _refused(db: sa.Connection, statement: str, **params: object) -> str:
    with pytest.raises(sa.exc.DBAPIError) as refused, db.begin_nested():
        db.execute(sa.text(statement), params)
    return str(refused.value)


# ------------------------------------------------------------ pure (no database)


def test_pkce_challenge_derivation_matches_rfc_7636() -> None:
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    assert derive_code_challenge(verifier) == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


def test_generated_verifiers_are_rfc_7636_shaped_high_entropy_and_distinct() -> None:
    verifiers = {generate_code_verifier() for _ in range(64)}
    assert len(verifiers) == 64
    for verifier in verifiers:
        assert 43 <= len(verifier) <= 128
        assert re.fullmatch(r"[A-Za-z0-9\-._~]+", verifier)


def test_protocol_tokens_are_distinct_and_hashes_do_not_reveal_them() -> None:
    tokens = {generate_protocol_token() for _ in range(64)}
    assert len(tokens) == 64 and all(len(token) >= 43 for token in tokens)
    token = next(iter(tokens))
    digest = hash_protocol_value(token)
    assert digest == hashlib.sha256(token.encode()).hexdigest()
    assert token not in digest


def test_the_state_machine_is_exactly_24_section_11_4() -> None:
    legal = {
        (OidcTransactionState.PENDING, OidcTransactionState.PROCESSING),
        (OidcTransactionState.PENDING, OidcTransactionState.EXPIRED),
        (OidcTransactionState.PENDING, OidcTransactionState.CANCELLED_TERMINAL),
        (OidcTransactionState.PENDING, OidcTransactionState.FAILED_TERMINAL),
        (OidcTransactionState.PROCESSING, OidcTransactionState.COMPLETED),
        (OidcTransactionState.PROCESSING, OidcTransactionState.FAILED_TERMINAL),
    }
    for origin in OidcTransactionState:
        for target in OidcTransactionState:
            assert is_legal_transition(origin, target) is ((origin, target) in legal), (
                origin,
                target,
            )
    terminal = {
        OidcTransactionState.COMPLETED,
        OidcTransactionState.FAILED_TERMINAL,
        OidcTransactionState.EXPIRED,
        OidcTransactionState.CANCELLED_TERMINAL,
    }
    assert set(TERMINAL_STATES) == terminal
    assert not is_legal_transition(OidcTransactionState.PROCESSING, OidcTransactionState.PENDING)


# ------------------------------------------------------------------- start


def test_start_creates_a_pending_transaction_bound_by_hashes_only(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    row = _row(db_connection, started.transaction_id)

    assert row["state"] == "PENDING" and row["purpose"] == "LOGIN"
    assert row["provider"] == _PROVIDER and row["initiating_user_id"] is None
    assert row["state_hash"] == hash_protocol_value(started.state)
    assert row["nonce_hash"] == hash_protocol_value(started.nonce)
    assert row["user_agent_binding_hash"] == hash_protocol_value(started.binding_token)
    assert row["created_at"] == _NOW and row["expires_at"] == _NOW + _LIFETIME
    assert row["post_auth_redirect_target"] == _TARGET
    assert row["claimed_at"] is None and row["verifier_unavailable_at"] is None
    rendered = " ".join(str(value) for value in row.values())
    for raw in (started.state, started.nonce, started.binding_token):
        assert raw not in rendered


def test_the_verifier_is_stored_confidentially_and_never_returned_at_start(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    row = _row(db_connection, started.transaction_id)
    stored = row["pkce_code_verifier"]
    assert stored is not None and stored != hash_protocol_value(stored)
    assert derive_code_challenge(stored) == started.code_challenge == row["pkce_code_challenge"]
    assert not hasattr(started, "code_verifier")
    assert stored not in (started.state, started.nonce, started.binding_token)


def test_an_account_link_transaction_binds_its_initiating_user(
    db_connection: sa.Connection,
) -> None:
    user_id = _user(db_connection)
    started = _start(
        db_connection, purpose=OidcTransactionPurpose.ACCOUNT_LINK, initiating_user_id=user_id
    )
    row = _row(db_connection, started.transaction_id)
    assert row["purpose"] == "ACCOUNT_LINK" and row["initiating_user_id"] == user_id.value
    with pytest.raises(ValueError):
        _start(db_connection, purpose=OidcTransactionPurpose.ACCOUNT_LINK, initiating_user_id=None)
    with pytest.raises(ValueError):
        _start(db_connection, purpose=OidcTransactionPurpose.LOGIN, initiating_user_id=user_id)


# ------------------------------------------------------------------- claim


def test_the_first_valid_callback_claims_the_transaction_and_receives_the_verifier(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    claimed = _claim(db_connection, started)

    assert claimed.transaction_id == started.transaction_id
    assert derive_code_challenge(claimed.code_verifier) == started.code_challenge
    assert claimed.nonce_hash == hash_protocol_value(started.nonce)
    assert claimed.redirect_target == _TARGET
    assert claimed.purpose is OidcTransactionPurpose.LOGIN
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "PROCESSING"
    assert row["claimed_at"] == _NOW + timedelta(minutes=1)
    assert row["pkce_code_verifier"] is None
    assert row["verifier_unavailable_at"] == _NOW + timedelta(minutes=1)


def test_a_second_callback_for_a_claimed_transaction_fails_closed_without_a_verifier(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    _claim(db_connection, started)
    with pytest.raises(TransactionRejected) as rejected:
        _claim(db_connection, started)
    assert rejected.value.reason == "ALREADY_PROCESSING"
    assert not hasattr(rejected.value, "code_verifier")
    assert _row(db_connection, started.transaction_id)["state"] == "PROCESSING"


def test_a_callback_without_a_transaction_fails_closed(db_connection: sa.Connection) -> None:
    started = _start(db_connection)
    with pytest.raises(TransactionRejected) as rejected:
        _claim(db_connection, started, state="not-a-known-state")
    assert rejected.value.reason == "MISSING_TRANSACTION"
    assert _row(db_connection, started.transaction_id)["state"] == "PENDING"


@pytest.mark.parametrize(
    ("binding", "reason"),
    [(None, "USER_AGENT_BINDING_MISSING"), ("another-browser", "USER_AGENT_BINDING_MISMATCH")],
)
def test_a_transplanted_callback_is_rejected_before_the_claim_and_terminalizes(
    db_connection: sa.Connection, binding: str | None, reason: str
) -> None:
    """24 §11.6: valid state, foreign user-agent. No claim, no verifier, and
    the transaction is unusable afterwards even for the original browser."""
    started = _start(db_connection)
    with pytest.raises(TransactionRejected) as rejected:
        _claim(db_connection, started, binding_token=binding)
    assert rejected.value.reason == reason
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "FAILED_TERMINAL" and row["failure_reason"] == reason
    assert row["pkce_code_verifier"] is None and row["verifier_unavailable_at"] is not None
    with pytest.raises(TransactionRejected) as again:
        _claim(db_connection, started)
    assert again.value.reason == "FAILED_TERMINAL"


def test_an_expired_transaction_cannot_be_claimed_and_becomes_expired(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    with pytest.raises(TransactionRejected) as rejected:
        _claim(db_connection, started, now=_NOW + _LIFETIME)
    assert rejected.value.reason == "EXPIRED_TRANSACTION"
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "EXPIRED" and row["expired_at"] == _NOW + _LIFETIME
    assert row["pkce_code_verifier"] is None
    with pytest.raises(TransactionRejected) as again:
        _claim(db_connection, started, now=_NOW + timedelta(seconds=1))
    assert again.value.reason == "EXPIRED"


def test_a_login_transaction_cannot_be_claimed_as_an_account_link(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    with pytest.raises(TransactionRejected) as rejected:
        _claim(
            db_connection,
            started,
            purpose=OidcTransactionPurpose.ACCOUNT_LINK,
            initiating_user_id=_user(db_connection),
        )
    assert rejected.value.reason == "PURPOSE_MISMATCH"
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "FAILED_TERMINAL" and row["pkce_code_verifier"] is None


def test_an_account_link_callback_must_come_from_the_initiating_user(
    db_connection: sa.Connection,
) -> None:
    owner, stranger = _user(db_connection), _user(db_connection)
    started = _start(
        db_connection, purpose=OidcTransactionPurpose.ACCOUNT_LINK, initiating_user_id=owner
    )
    for wrong in (stranger, None):
        fresh = _start(
            db_connection, purpose=OidcTransactionPurpose.ACCOUNT_LINK, initiating_user_id=owner
        )
        with pytest.raises(TransactionRejected) as rejected:
            _claim(
                db_connection,
                fresh,
                purpose=OidcTransactionPurpose.ACCOUNT_LINK,
                initiating_user_id=wrong,
            )
        assert rejected.value.reason == "INITIATING_USER_MISMATCH"
        assert _row(db_connection, fresh.transaction_id)["state"] == "FAILED_TERMINAL"
    claimed = _claim(
        db_connection,
        started,
        purpose=OidcTransactionPurpose.ACCOUNT_LINK,
        initiating_user_id=owner,
    )
    assert claimed.initiating_user_id == owner


def test_a_verifier_from_one_transaction_cannot_satisfy_another(
    db_connection: sa.Connection,
) -> None:
    first, second = _start(db_connection), _start(db_connection)
    claimed_first = _claim(db_connection, first)
    claimed_second = _claim(db_connection, second)
    assert derive_code_challenge(claimed_first.code_verifier) == first.code_challenge
    assert derive_code_challenge(claimed_first.code_verifier) != second.code_challenge
    assert claimed_first.code_verifier != claimed_second.code_verifier


# -------------------------------------------------------- terminal states


def test_completion_and_failure_are_terminal_and_unclaimable(
    db_connection: sa.Connection,
) -> None:
    done, broken = _start(db_connection), _start(db_connection)
    _claim(db_connection, done)
    _claim(db_connection, broken)
    later = _NOW + timedelta(minutes=2)

    complete_transaction(_repo(db_connection), done.transaction_id, now=later)
    fail_transaction(
        _repo(db_connection), broken.transaction_id, reason="TOKEN_EXCHANGE_REJECTED", now=later
    )

    assert _row(db_connection, done.transaction_id)["completed_at"] == later
    failed = _row(db_connection, broken.transaction_id)
    assert failed["failed_terminal_at"] == later
    assert failed["failure_reason"] == "TOKEN_EXCHANGE_REJECTED"
    for started, reason in ((done, "ALREADY_COMPLETED"), (broken, "FAILED_TERMINAL")):
        with pytest.raises(TransactionRejected) as rejected:
            _claim(db_connection, started, now=later)
        assert rejected.value.reason == reason
    with pytest.raises(TransactionRejected):
        complete_transaction(_repo(db_connection), broken.transaction_id, now=later)
    with pytest.raises(TransactionRejected):
        complete_transaction(_repo(db_connection), uuid.uuid4(), now=later)


def test_an_uncertain_exchange_outcome_is_terminal_not_retryable(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    _claim(db_connection, started)
    fail_transaction(
        _repo(db_connection),
        started.transaction_id,
        reason="TOKEN_EXCHANGE_OUTCOME_UNCERTAIN",
        now=_NOW + timedelta(minutes=2),
    )
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "FAILED_TERMINAL" and row["pkce_code_verifier"] is None
    with pytest.raises(TransactionRejected):
        _claim(db_connection, started, now=_NOW + timedelta(minutes=3))


def test_a_pending_transaction_cannot_be_completed_without_a_claim(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    with pytest.raises(TransactionRejected):
        complete_transaction(_repo(db_connection), started.transaction_id, now=_NOW)
    assert _row(db_connection, started.transaction_id)["state"] == "PENDING"


def test_provider_cancel_terminalizes_without_touching_the_verifier(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    outcome = cancel_transaction(
        _repo(db_connection),
        state=started.state,
        binding_token=started.binding_token,
        reason="USER_CANCEL",
        now=_NOW + timedelta(minutes=1),
    )
    assert outcome.transaction_id == started.transaction_id
    assert outcome.redirect_target == _TARGET
    row = _row(db_connection, started.transaction_id)
    assert row["state"] == "CANCELLED_TERMINAL" and row["failure_reason"] == "USER_CANCEL"
    assert row["cancelled_at"] == _NOW + timedelta(minutes=1)
    assert row["pkce_code_verifier"] is None and row["claimed_at"] is None
    with pytest.raises(TransactionRejected) as rejected:
        _claim(db_connection, started)
    assert rejected.value.reason == "CANCELLED_TERMINAL"


@pytest.mark.parametrize(
    ("binding", "reason"),
    [(None, "USER_AGENT_BINDING_MISSING"), ("another-browser", "USER_AGENT_BINDING_MISMATCH")],
)
def test_a_transplanted_cancel_callback_cannot_cancel_another_browsers_transaction(
    db_connection: sa.Connection, binding: str | None, reason: str
) -> None:
    started = _start(db_connection)
    with pytest.raises(TransactionRejected) as rejected:
        cancel_transaction(
            _repo(db_connection),
            state=started.state,
            binding_token=binding,
            reason="USER_CANCEL",
            now=_NOW,
        )
    assert rejected.value.reason == reason
    assert _row(db_connection, started.transaction_id)["state"] == "FAILED_TERMINAL"


def test_cancel_after_the_claim_or_without_a_transaction_is_rejected(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    _claim(db_connection, started)
    with pytest.raises(TransactionRejected) as rejected:
        cancel_transaction(
            _repo(db_connection),
            state=started.state,
            binding_token=started.binding_token,
            reason="USER_CANCEL",
            now=_NOW,
        )
    assert rejected.value.reason == "ALREADY_PROCESSING"
    with pytest.raises(TransactionRejected) as missing:
        cancel_transaction(
            _repo(db_connection), state="unknown", binding_token="x", reason="USER_CANCEL", now=_NOW
        )
    assert missing.value.reason == "MISSING_TRANSACTION"


# -------------------------------------------------------- database rules


def test_the_database_refuses_illegal_transitions_for_every_writer(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    transaction_id = started.transaction_id
    _claim(db_connection, started)
    for assignment in (
        "state = 'PENDING', claimed_at = NULL",
        "state = 'EXPIRED', expired_at = now()",
        "state = 'CANCELLED_TERMINAL', cancelled_at = now()",
        "pkce_code_verifier = 'resurrected'",
    ):
        refusal = _refused(
            db_connection,
            f"UPDATE oidc_auth_transactions SET {assignment} WHERE id = :id",
            id=transaction_id,
        )
        assert "transition" in refusal or "verifier" in refusal, refusal
    complete_transaction(_repo(db_connection), transaction_id, now=_NOW + timedelta(minutes=2))
    for assignment in (
        "state = 'PENDING'",
        "state = 'PROCESSING'",
        "state = 'FAILED_TERMINAL', failed_terminal_at = now()",
        "completed_at = now()",
        "post_auth_redirect_target = '/elsewhere'",
    ):
        refusal = _refused(
            db_connection,
            f"UPDATE oidc_auth_transactions SET {assignment} WHERE id = :id",
            id=transaction_id,
        )
        assert "terminal" in refusal or "immutable" in refusal, refusal


def test_the_database_refuses_a_pending_transaction_without_a_verifier_and_vice_versa(
    db_connection: sa.Connection,
) -> None:
    started = _start(db_connection)
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.text("UPDATE oidc_auth_transactions SET pkce_code_verifier = NULL WHERE id = :id"),
            {"id": started.transaction_id},
        )
    statement = (
        "INSERT INTO oidc_auth_transactions (id, provider, purpose, state, state_hash, nonce_hash,"
        " user_agent_binding_hash, pkce_code_verifier, pkce_code_challenge,"
        " post_auth_redirect_target, created_at, expires_at, provenance_ref) VALUES"
        " (:id, 'TEST_PROVIDER', :purpose, :state, :sh, :nh, :bh, :verifier, 'c', :target,"
        " :at, :until, 'test')"
    )
    base = {"nh": uuid.uuid4().hex, "bh": uuid.uuid4().hex, "at": _NOW, "until": _NOW + _LIFETIME}
    refusals = [
        {"purpose": "LOGIN", "state": "PROCESSING", "verifier": "v", "target": _TARGET},
        {"purpose": "LOGIN", "state": "PENDING", "verifier": None, "target": _TARGET},
        {"purpose": "LOGIN", "state": "COMPLETED", "verifier": None, "target": _TARGET},
        {"purpose": "ACCOUNT_LINK", "state": "PENDING", "verifier": "v", "target": _TARGET},
        {"purpose": "LOGIN", "state": "PENDING", "verifier": "v", "target": "https://evil.test/"},
        {"purpose": "LOGIN", "state": "PENDING", "verifier": "v", "target": "//evil.test/x"},
        {"purpose": "RECOVERY", "state": "PENDING", "verifier": "v", "target": _TARGET},
    ]
    for params in refusals:
        with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
            db_connection.execute(
                sa.text(statement), {**base, **params, "id": uuid.uuid4(), "sh": uuid.uuid4().hex}
            )


def test_the_identity_of_a_transaction_is_immutable(db_connection: sa.Connection) -> None:
    started = _start(db_connection)
    for assignment in (
        "purpose = 'ACCOUNT_LINK', initiating_user_id = :user",
        "state_hash = 'other'",
        "nonce_hash = 'other'",
        "user_agent_binding_hash = 'other'",
        "pkce_code_challenge = 'other'",
        "expires_at = expires_at + interval '1 hour'",
        "provider = 'OTHER'",
    ):
        refusal = _refused(
            db_connection,
            f"UPDATE oidc_auth_transactions SET {assignment} WHERE id = :id",
            id=started.transaction_id,
            user=_user(db_connection).value,
        )
        assert "immutable" in refusal, refusal


def test_the_relation_is_not_workspace_scoped_and_has_no_identity_columns(
    db_connection: sa.Connection,
) -> None:
    columns = set(
        db_connection.execute(
            sa.text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'oidc_auth_transactions'"
            )
        ).scalars()
    )
    assert "workspace_id" not in columns
    assert not {"email", "provider_subject", "role", "user_id"} & columns
    assert (
        db_connection.execute(
            sa.text("SELECT relrowsecurity FROM pg_class WHERE relname = 'oidc_auth_transactions'")
        ).scalar_one()
        is False
    )


def test_two_parallel_callbacks_produce_exactly_one_winner(db_connection: sa.Connection) -> None:
    """24 §33.6 / §11.7: the claim is decided by authoritative state under
    concurrency, not by process-local memory or provider code reuse."""
    engine = db_connection.engine
    with engine.begin() as setup:
        started = _start(setup)
    first, second = engine.connect(), engine.connect()
    try:
        first_tx = first.begin()
        winner = _claim(first, started)  # uncommitted claim holds the row lock
        second_tx = second.begin()
        second.execute(sa.text("SET LOCAL lock_timeout = '300ms'"))
        with pytest.raises(sa.exc.OperationalError):
            _claim(second, started)
        second_tx.rollback()
        first_tx.commit()
        second_tx = second.begin()
        with pytest.raises(TransactionRejected) as rejected:
            _claim(second, started)
        second_tx.rollback()
        assert rejected.value.reason == "ALREADY_PROCESSING"
        assert derive_code_challenge(winner.code_verifier) == started.code_challenge
        with engine.connect() as check:
            row = (
                check.execute(
                    sa.text(
                        "SELECT state, pkce_code_verifier FROM oidc_auth_transactions "
                        "WHERE id = :id"
                    ),
                    {"id": started.transaction_id},
                )
                .mappings()
                .one()
            )
        assert row["state"] == "PROCESSING" and row["pkce_code_verifier"] is None
    finally:
        first.close()
        second.close()
        with engine.begin() as cleanup:
            cleanup.execute(
                sa.text("DELETE FROM oidc_auth_transactions WHERE id = :id"),
                {"id": started.transaction_id},
            )


def test_pkce_challenge_is_plain_s256_of_the_stored_verifier(db_connection: sa.Connection) -> None:
    started = _start(db_connection)
    stored = _row(db_connection, started.transaction_id)["pkce_code_verifier"]
    expected = base64.urlsafe_b64encode(hashlib.sha256(stored.encode("ascii")).digest())
    assert started.code_challenge == expected.rstrip(b"=").decode("ascii")
