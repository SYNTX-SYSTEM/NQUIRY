"""T10: local credentials work through the method model (24 WU-AUTH-03; §9.2,
§16.3, §22.3, §22.4, §28.2).

MUST BECOME TRUE: every local password credential belongs to exactly one
LOCAL_PASSWORD authentication method of the same user; every creator of a
credential (host operator HD-28, dev provisioning HD-3, seed, fixtures)
produces that method through the one canonical producer; login requires the
method to be ACTIVE ("method status controls login") and records the
authentication on it; existing logins keep working.

MUST REMAIN IMPOSSIBLE: a credential without a method, with another user's
method, with a non-password method, or sharing a method; a revoked method
still logging in; a revoked method being told apart from a wrong password; a
plaintext password anywhere in the new relation.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

import application.http_dispatch as http_dispatch
import pytest
import sqlalchemy as sa
from application.auth_handler import InvalidCredentials, login
from application.http_dispatch import SESSION_COOKIE_NAME
from application.identity_provisioning import HostOperator, create_identity_by_host_operator
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.tables import (
    authentication_methods_table,
    local_auth_credentials_table,
    local_auth_sessions_table,
    users_table,
)
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.events import Environment
from security.local_auth import LocalCredentialRecord, hash_password
from semantic_types.ids import UserId
from test_support.dev_identity import provision_dev_identity

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"


def _email() -> str:
    return f"wu03-{uuid.uuid4().hex}@example.test"


def _insert_user(db: sa.Connection, *, email: str) -> UserId:
    user_id = UserId(uuid.uuid4())
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="WU-AUTH-03",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return user_id


def _seed(db: sa.Connection, *, email: str, password: str = _PASSWORD) -> UserId:
    user_id = _insert_user(db, email=email)
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(password), now=_NOW
    )
    return user_id


def _methods(db: sa.Connection, user_id: UserId) -> tuple[Any, ...]:
    return SqlAlchemyAuthenticationMethodRepository(db).list_for_user(user_id)


def _credential_row(db: sa.Connection, user_id: UserId) -> Any:
    return (
        db.execute(
            sa.select(local_auth_credentials_table).where(
                local_auth_credentials_table.c.user_id == user_id.value
            )
        )
        .mappings()
        .one()
    )


def _session_count(db: sa.Connection, user_id: UserId) -> int:
    return int(
        db.execute(
            sa.select(sa.func.count())
            .select_from(local_auth_sessions_table)
            .where(local_auth_sessions_table.c.user_id == user_id.value)
        ).scalar_one()
    )


def _login(db: sa.Connection, email: str, password: str = _PASSWORD, *, now: datetime = _NOW):
    return login(
        email,
        password,
        credential_repository=SqlAlchemyLocalCredentialRepository(db),
        session_repository=SqlAlchemyLocalSessionRepository(db),
        now=now,
    )


# ------------------------------------------------------------ MUST BECOME TRUE


def test_creating_a_credential_creates_its_local_password_method(
    db_connection: sa.Connection,
) -> None:
    user_id = _seed(db_connection, email=_email())

    (method,) = _methods(db_connection, user_id)
    credential = _credential_row(db_connection, user_id)
    assert method.method_type is AuthenticationMethodType.LOCAL_PASSWORD
    assert method.status is AuthenticationMethodStatus.ACTIVE
    assert method.user_id == user_id
    assert credential["authentication_method_id"] == method.method_id.value
    assert method.provenance_ref == f"local-credential:{credential['id']}"


def test_the_credential_record_names_its_method(db_connection: sa.Connection) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    record = SqlAlchemyLocalCredentialRepository(db_connection).get_by_email(email)
    assert record is not None
    (method,) = _methods(db_connection, user_id)
    assert record.method_id == method.method_id


def test_login_through_an_active_method_succeeds_and_is_recorded_on_the_method(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    later = _NOW + timedelta(hours=3)

    result = _login(db_connection, email, now=later)

    assert result.user_id == user_id
    (method,) = _methods(db_connection, user_id)
    assert method.last_authenticated_at == later
    assert method.status is AuthenticationMethodStatus.ACTIVE


def test_the_host_operator_identity_gets_a_method_and_logs_in(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    created = create_identity_by_host_operator(
        db_connection,
        email=email,
        name="Operator Created",
        password=_PASSWORD,
        operator=HostOperator(operator_id="otti@condyn.eu", os_user="root", host="test"),
        environment=Environment.PRODUCTION,
        now=_NOW,
    )
    (method,) = _methods(db_connection, created.user_id)
    assert method.method_type is AuthenticationMethodType.LOCAL_PASSWORD
    assert _login(db_connection, email).user_id == created.user_id


def test_the_dev_provisioned_identity_gets_a_method_and_logs_in(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    provisioned = provision_dev_identity(
        db_connection, email=email, name="Dev", password=_PASSWORD, now=_NOW
    )
    (method,) = _methods(db_connection, provisioned.user_id)
    assert method.status is AuthenticationMethodStatus.ACTIVE
    assert _login(db_connection, email).user_id == provisioned.user_id


# ----------------------------------------------------- MUST REMAIN IMPOSSIBLE


def test_a_revoked_method_cannot_log_in_and_creates_no_session(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    (method,) = _methods(db_connection, user_id)
    SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
        method.method_id, revoked_at=_NOW + timedelta(minutes=1)
    )

    with pytest.raises(InvalidCredentials) as revoked:
        _login(db_connection, email, now=_NOW + timedelta(minutes=2))
    with pytest.raises(InvalidCredentials) as wrong:
        _login(db_connection, email, "not the password", now=_NOW + timedelta(minutes=2))

    assert str(revoked.value) == str(wrong.value)
    assert _session_count(db_connection, user_id) == 0
    (after,) = _methods(db_connection, user_id)
    assert after.last_authenticated_at is None


def test_a_method_revoked_while_the_login_is_in_flight_does_not_log_in(
    db_connection: sa.Connection,
) -> None:
    """The credential was read while its method was ACTIVE; the method is
    revoked before the login commits. The authoritative check is the
    conditional write on the method, not the earlier read (24 §39.13 "method
    revocation during login")."""
    email = _email()
    user_id = _seed(db_connection, email=email)

    class _RevokedAfterRead(SqlAlchemyLocalCredentialRepository):
        def get_by_email(self, email: str) -> LocalCredentialRecord | None:
            record = super().get_by_email(email)
            assert record is not None
            SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
                record.method_id, revoked_at=_NOW + timedelta(seconds=1)
            )
            return record

    with pytest.raises(InvalidCredentials):
        login(
            email,
            _PASSWORD,
            credential_repository=_RevokedAfterRead(db_connection),
            session_repository=SqlAlchemyLocalSessionRepository(db_connection),
            now=_NOW + timedelta(seconds=2),
        )
    assert _session_count(db_connection, user_id) == 0


def test_a_failed_login_is_not_recorded_as_an_authentication(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    with pytest.raises(InvalidCredentials):
        _login(db_connection, email, "wrong", now=_NOW + timedelta(hours=1))
    (method,) = _methods(db_connection, user_id)
    assert method.last_authenticated_at is None


def _raw_credential(db: sa.Connection, *, user_id: UserId, method_id: uuid.UUID | None) -> None:
    db.execute(
        sa.insert(local_auth_credentials_table).values(
            id=uuid.uuid4(),
            user_id=user_id.value,
            authentication_method_id=method_id,
            password_hash=hash_password(_PASSWORD),
            created_at=_NOW,
            updated_at=_NOW,
        )
    )


def _raw_method(db: sa.Connection, *, user_id: UserId, method_type: str) -> uuid.UUID:
    method_id = uuid.uuid4()
    db.execute(
        sa.insert(authentication_methods_table).values(
            id=method_id,
            user_id=user_id.value,
            method_type=method_type,
            status="ACTIVE",
            created_at=_NOW,
            revoked_at=None,
            last_authenticated_at=None,
            provenance_ref="test:wu-auth-03",
        )
    )
    return method_id


def test_a_credential_cannot_exist_without_a_method(db_connection: sa.Connection) -> None:
    user_id = _insert_user(db_connection, email=_email())
    # Refused by the trigger (no such method) before NOT NULL / the FK are reached.
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        _raw_credential(db_connection, user_id=user_id, method_id=None)
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        _raw_credential(db_connection, user_id=user_id, method_id=uuid.uuid4())
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(local_auth_credentials_table)
            .where(local_auth_credentials_table.c.user_id == user_id.value)
        ).scalar_one()
        == 0
    )


def test_a_credential_cannot_use_another_users_method(db_connection: sa.Connection) -> None:
    owner = _insert_user(db_connection, email=_email())
    other = _insert_user(db_connection, email=_email())
    method_id = _raw_method(db_connection, user_id=other, method_type="LOCAL_PASSWORD")
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_credential(db_connection, user_id=owner, method_id=method_id)


def test_a_credential_cannot_use_a_method_that_is_not_a_local_password(
    db_connection: sa.Connection,
) -> None:
    user_id = _insert_user(db_connection, email=_email())
    method_id = _raw_method(db_connection, user_id=user_id, method_type="GOOGLE_OIDC")
    with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
        _raw_credential(db_connection, user_id=user_id, method_id=method_id)
    assert "LOCAL_PASSWORD" in str(refused.value)


def test_a_credential_cannot_be_moved_to_another_method(db_connection: sa.Connection) -> None:
    user_id = _seed(db_connection, email=_email())
    (method,) = _methods(db_connection, user_id)
    SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
        method.method_id, revoked_at=_NOW + timedelta(minutes=1)
    )
    successor = _raw_method(db_connection, user_id=user_id, method_type="LOCAL_PASSWORD")
    with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
        db_connection.execute(
            sa.update(local_auth_credentials_table)
            .where(local_auth_credentials_table.c.user_id == user_id.value)
            .values(authentication_method_id=successor)
        )
    assert "immutable" in str(refused.value)


def test_the_password_appears_nowhere_in_the_method(db_connection: sa.Connection) -> None:
    user_id = _seed(db_connection, email=_email())
    row = (
        db_connection.execute(
            sa.select(authentication_methods_table).where(
                authentication_methods_table.c.user_id == user_id.value
            )
        )
        .mappings()
        .one()
    )
    credential = _credential_row(db_connection, user_id)
    rendered = " ".join(str(value) for value in row.values())
    assert _PASSWORD not in rendered
    assert credential["password_hash"] not in rendered


# ------------------------------------------------------------------ over HTTP


@pytest.fixture
def http_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse_test_connection() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse_test_connection)
    yield TestClient(app)


def test_http_login_with_a_revoked_method_is_indistinguishable_from_a_wrong_password(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    wrong = http_client.post("/auth/login", json={"email": email, "password": "wrong"})
    ok = http_client.post("/auth/login", json={"email": email, "password": _PASSWORD})
    assert ok.status_code == 200 and SESSION_COOKIE_NAME in ok.cookies

    (method,) = _methods(db_connection, user_id)
    SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
        method.method_id, revoked_at=datetime.now(timezone.utc)
    )
    http_client.cookies.clear()
    revoked = http_client.post("/auth/login", json={"email": email, "password": _PASSWORD})

    assert revoked.status_code == wrong.status_code == 401
    assert revoked.json() == wrong.json() == {"kind": "denied", "reasonCode": "INVALID_CREDENTIALS"}
    assert SESSION_COOKIE_NAME not in revoked.cookies
    assert "set-cookie" not in {name.lower() for name in revoked.headers}
