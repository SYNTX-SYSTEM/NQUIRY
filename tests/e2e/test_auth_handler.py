"""T10 test: `application.auth_handler.{login,resolve_session,logout}`
against the REAL `local_auth_credentials`/`local_auth_sessions` tables
(migration `05794035ef3c`), through the real
`persistence.local_auth_repository` adapters.

Closes the disclosed GAP-14-001 weakness
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`
recorded: identity used to be a bare, unverified request header. Every
negative/adversarial case here is written BEFORE (TDD RED) the HTTP
layer wiring in `test_http_session_view.py`/`test_http_record_decision.py`
consumes this same handler — those files trust that the mechanism
proven here is sound and only need to prove the wiring.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from application.auth_handler import (
    InvalidCredentials,
    LoginSuccess,
    login,
    logout,
    resolve_session,
)
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.tables import users_table
from security.local_auth import hash_password
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _seed_user_with_password(db_connection: sa.Connection, *, email: str, password: str) -> UserId:
    user_id = UserId(uuid.uuid4())
    db_connection.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Local Auth Test User",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db_connection).create(
        user_id=user_id, password_hash=hash_password(password), now=_NOW
    )
    return user_id


def test_login_with_correct_credentials_issues_a_real_session(
    db_connection: sa.Connection,
) -> None:
    user_id = _seed_user_with_password(
        db_connection, email="login-happy@nonproof.test", password="correct horse battery staple"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    result = login(
        "login-happy@nonproof.test",
        "correct horse battery staple",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )

    assert isinstance(result, LoginSuccess)
    assert result.user_id == user_id
    assert result.expires_at == _NOW + timedelta(hours=12)
    assert len(result.session_token) >= 32

    # The proof is the real row, independent of the returned object.
    principal = resolve_session(
        result.session_token, session_repository=session_repository, now=_NOW
    )
    assert principal is not None
    assert principal.user_id == user_id


def test_login_normalizes_email_case_and_surrounding_whitespace(
    db_connection: sa.Connection,
) -> None:
    user_id = _seed_user_with_password(
        db_connection, email="case-sensitive@nonproof.test", password="pw12345678"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    result = login(
        "  Case-Sensitive@NonProof.Test  ",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )

    assert result.user_id == user_id


def test_login_strips_surrounding_whitespace_from_the_password(
    db_connection: sa.Connection,
) -> None:
    """Real-world failure mode found via human browser verification:
    copying a password out of a chat message/terminal easily picks up
    a trailing newline/space -- login must still succeed with the
    visible password, byte-exact comparison must not silently reject
    it."""
    user_id = _seed_user_with_password(
        db_connection, email="whitespace-pw@nonproof.test", password="correct horse battery staple"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    result = login(
        "whitespace-pw@nonproof.test",
        "  correct horse battery staple\n",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )

    assert result.user_id == user_id


def test_login_rejects_a_wrong_password(db_connection: sa.Connection) -> None:
    _seed_user_with_password(db_connection, email="wrong-pw@nonproof.test", password="the-real-one")
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    with pytest.raises(InvalidCredentials):
        login(
            "wrong-pw@nonproof.test",
            "not-the-real-one",
            credential_repository=credential_repository,
            session_repository=session_repository,
            now=_NOW,
        )


def test_login_rejects_an_unknown_email_with_the_identical_exception_as_a_wrong_password(
    db_connection: sa.Connection,
) -> None:
    """Adversarial: no user-enumeration -- an unregistered email and a
    wrong password for a real account must be indistinguishable to the
    caller (same exception type, same message shape)."""
    _seed_user_with_password(
        db_connection, email="real-account@nonproof.test", password="pw12345678"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    with pytest.raises(InvalidCredentials) as unknown_exc:
        login(
            "never-registered@nonproof.test",
            "anything",
            credential_repository=credential_repository,
            session_repository=session_repository,
            now=_NOW,
        )
    with pytest.raises(InvalidCredentials) as wrong_pw_exc:
        login(
            "real-account@nonproof.test",
            "anything",
            credential_repository=credential_repository,
            session_repository=session_repository,
            now=_NOW,
        )
    assert str(unknown_exc.value) == str(wrong_pw_exc.value)


def test_login_rejects_an_empty_password(db_connection: sa.Connection) -> None:
    _seed_user_with_password(db_connection, email="empty-pw@nonproof.test", password="pw12345678")
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    with pytest.raises(InvalidCredentials):
        login(
            "empty-pw@nonproof.test",
            "",
            credential_repository=credential_repository,
            session_repository=session_repository,
            now=_NOW,
        )


def test_login_does_not_create_a_session_row_on_failure(db_connection: sa.Connection) -> None:
    from persistence.tables import local_auth_sessions_table

    user_id = _seed_user_with_password(
        db_connection, email="no-leak@nonproof.test", password="pw12345678"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)

    with pytest.raises(InvalidCredentials):
        login(
            "no-leak@nonproof.test",
            "wrong",
            credential_repository=credential_repository,
            session_repository=session_repository,
            now=_NOW,
        )

    # Scoped to THIS test's own user, not an unscoped table-wide count --
    # an unscoped count is fragile against real, disclosed residue from
    # other tests/manual runs in a shared live DB (the exact,
    # already-documented anti-pattern
    # `tests/security/test_habb_grant_constraints.py::
    # test_grant_without_active_membership_is_rejected` has; not
    # repeated here).
    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(local_auth_sessions_table)
        .where(local_auth_sessions_table.c.user_id == user_id.value)
    ).scalar()
    assert count == 0


def test_resolve_session_returns_none_for_a_missing_token(db_connection: sa.Connection) -> None:
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    assert resolve_session(None, session_repository=session_repository, now=_NOW) is None


def test_resolve_session_returns_none_for_an_unknown_garbage_token(
    db_connection: sa.Connection,
) -> None:
    """Adversarial: a forged/never-issued token must not resolve."""
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    assert (
        resolve_session("totally-made-up-token", session_repository=session_repository, now=_NOW)
        is None
    )


def test_resolve_session_returns_none_for_a_tampered_token(db_connection: sa.Connection) -> None:
    """Adversarial: a real, previously-issued token with ONE character
    flipped must not resolve -- proves the hash comparison is exact,
    not a prefix/fuzzy match."""
    _seed_user_with_password(db_connection, email="tamper@nonproof.test", password="pw12345678")
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    result = login(
        "tamper@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )
    flipped_char = "a" if result.session_token[0] != "a" else "b"
    tampered_token = flipped_char + result.session_token[1:]

    assert resolve_session(tampered_token, session_repository=session_repository, now=_NOW) is None


def test_resolve_session_returns_none_for_an_expired_session(db_connection: sa.Connection) -> None:
    """Adversarial: a session past its own `expires_at` must not
    resolve, even though it was never explicitly revoked."""
    _seed_user_with_password(db_connection, email="expired@nonproof.test", password="pw12345678")
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    result = login(
        "expired@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )
    one_second_after_expiry = result.expires_at + timedelta(seconds=1)

    principal = resolve_session(
        result.session_token, session_repository=session_repository, now=one_second_after_expiry
    )
    assert principal is None


def test_resolve_session_still_resolves_one_second_before_expiry(
    db_connection: sa.Connection,
) -> None:
    """Boundary proof for the expiry test above -- proves the failure is
    genuinely about crossing `expires_at`, not an off-by-a-mile bug."""
    _seed_user_with_password(
        db_connection, email="not-yet-expired@nonproof.test", password="pw12345678"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    result = login(
        "not-yet-expired@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )
    one_second_before_expiry = result.expires_at - timedelta(seconds=1)

    principal = resolve_session(
        result.session_token, session_repository=session_repository, now=one_second_before_expiry
    )
    assert principal is not None
    assert principal.user_id == result.user_id


def test_logout_revokes_the_session_and_it_no_longer_resolves(
    db_connection: sa.Connection,
) -> None:
    _seed_user_with_password(db_connection, email="logout@nonproof.test", password="pw12345678")
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    result = login(
        "logout@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )
    assert (
        resolve_session(result.session_token, session_repository=session_repository, now=_NOW)
        is not None
    )

    logout(result.session_token, session_repository=session_repository, now=_NOW)

    assert (
        resolve_session(result.session_token, session_repository=session_repository, now=_NOW)
        is None
    )


def test_logout_with_an_unknown_token_is_a_silent_no_op(db_connection: sa.Connection) -> None:
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    logout("never-issued-token", session_repository=session_repository, now=_NOW)  # must not raise
    logout(None, session_repository=session_repository, now=_NOW)  # must not raise


def test_revoking_one_session_does_not_affect_a_second_independent_session(
    db_connection: sa.Connection,
) -> None:
    """Adversarial: multi-session isolation -- logging out of one device
    (one issued token) must not silently invalidate a second, separately
    issued session for the same user."""
    _seed_user_with_password(
        db_connection, email="multi-session@nonproof.test", password="pw12345678"
    )
    credential_repository = SqlAlchemyLocalCredentialRepository(db_connection)
    session_repository = SqlAlchemyLocalSessionRepository(db_connection)
    first = login(
        "multi-session@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW,
    )
    second = login(
        "multi-session@nonproof.test",
        "pw12345678",
        credential_repository=credential_repository,
        session_repository=session_repository,
        now=_NOW + timedelta(seconds=1),
    )
    assert first.session_token != second.session_token

    logout(first.session_token, session_repository=session_repository, now=_NOW)

    assert (
        resolve_session(first.session_token, session_repository=session_repository, now=_NOW)
        is None
    )
    still_valid = resolve_session(
        second.session_token, session_repository=session_repository, now=_NOW
    )
    assert still_valid is not None
    assert still_valid.user_id == first.user_id
