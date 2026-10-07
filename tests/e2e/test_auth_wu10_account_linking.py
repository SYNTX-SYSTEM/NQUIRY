"""T10: account linking (24 WU-AUTH-10; §14; §15.6; §19.5; §23.2; §33.5;
falsifiers 59–61, 91; §44.5).

MUST BECOME TRUE: an authenticated identity can add a provider method through
an ACCOUNT_LINK transaction bound to that identity and to the initiating
browser; provider proof, collision check, method + binding + audit as one
effect; the session is rotated after the link; the account security surface
lists the identity's methods.

MUST REMAIN IMPOSSIBLE: an unauthenticated link; a link callback for another
identity's transaction; a LOGIN transaction consumed by the link callback (or
the reverse); a provider subject that is already bound to another identity
moving accounts; a link by email; any authority from a link.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import BINDING_COOKIE_NAME, configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.tables import local_auth_sessions_table, security_events_table, users_table
from security.auth_methods import AuthenticationMethodType
from security.local_auth import hash_password, hash_session_token
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.oidc_transaction import hash_protocol_value
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
_AUTHORITY_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "session_participations",
    "workspaces",
)


@pytest.fixture
def issuer() -> LocalTestIssuer:
    return LocalTestIssuer.create()


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _local_user(db: sa.Connection) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Linker",
            record_version=1,
            created_at=_NOW,
            established_at=_NOW,  # WU-AUTH-22: established
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def _login(client: TestClient, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": _PASSWORD})
    assert response.status_code == 200
    return response.cookies[SESSION_COOKIE_NAME]


def _link_start(client: TestClient, **query: str):  # type: ignore[no-untyped-def]
    response = client.post("/auth/oidc/test/link/start", params=query)
    if response.status_code != 303:
        return response, None
    params = {k: v[0] for k, v in parse_qs(urlparse(response.headers["location"]).query).items()}
    return response, params


def _link_callback(client: TestClient, **query: str):  # type: ignore[no-untyped-def]
    return client.get("/auth/oidc/test/link/callback", params=query)


def _transaction(db: sa.Connection, state: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.text(
                "SELECT state, purpose, initiating_user_id, failure_reason "
                "FROM oidc_auth_transactions WHERE state_hash = :h"
            ),
            {"h": hash_protocol_value(state)},
        )
        .mappings()
        .one()
    )


def _methods(db: sa.Connection, user_id: UserId):  # type: ignore[no-untyped-def]
    return SqlAlchemyAuthenticationMethodRepository(db).list_for_user(user_id)


# ------------------------------------------------------------------ start


def test_link_start_requires_a_session(client: TestClient) -> None:
    response, _ = _link_start(client)
    assert response.status_code == 401
    assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}
    assert BINDING_COOKIE_NAME not in response.cookies


def test_link_start_creates_an_account_link_transaction_bound_to_the_caller(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)

    response, params = _link_start(client, next="/account/security")

    assert params is not None
    location = urlparse(response.headers["location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == issuer.authorization_endpoint
    assert params["redirect_uri"] == "http://testserver/auth/oidc/test/link/callback"
    assert params["code_challenge_method"] == "S256"
    row = _transaction(db_connection, params["state"])
    assert row["purpose"] == "ACCOUNT_LINK" and row["initiating_user_id"] == user_id.value
    assert BINDING_COOKIE_NAME in response.cookies


def test_link_start_for_an_unconfigured_provider_is_unavailable(
    client: TestClient, db_connection: sa.Connection
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    response = client.post("/auth/oidc/google/link/start")
    assert response.status_code == 503
    assert response.json() == {"kind": "unavailable", "reasonCode": "PROVIDER_NOT_CONFIGURED"}


# --------------------------------------------------------------- callback


def test_an_authenticated_user_links_a_provider_method_and_the_session_rotates(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    old_token = _login(client, email)
    _, params = _link_start(client, next="/account/security")
    assert params is not None
    code = issuer.authorize(params, subject="linked-subject-1", email="linked@example.test")

    response = _link_callback(client, code=code, state=params["state"])

    assert response.status_code == 303
    assert response.headers["location"] == "/account/security?link=ok"
    assert _transaction(db_connection, params["state"])["state"] == "COMPLETED"
    # (the fixture dates the local method in 2030; the link is dated now, so
    # the created_at order puts the provider method first)
    methods = {m.method_type: m for m in _methods(db_connection, user_id)}
    assert set(methods) == {
        AuthenticationMethodType.LOCAL_PASSWORD,
        AuthenticationMethodType.TEST_PROVIDER,
    }
    binding = SqlAlchemyProviderIdentityRepository(db_connection).find(
        TEST_ISSUER, "linked-subject-1"
    )
    assert binding is not None and binding.user_id == user_id
    assert binding.method_id == methods[AuthenticationMethodType.TEST_PROVIDER].method_id
    assert binding.provider_email == "linked@example.test"

    # 24 §15.6: rotation after linking; the old token is dead, the new one is the same identity.
    new_token = response.cookies[SESSION_COOKIE_NAME]
    assert new_token != old_token
    old_row = (
        db_connection.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.session_token_hash == hash_session_token(old_token)
            )
        )
        .mappings()
        .one()
    )
    assert old_row["revoked_reason"] == "ROTATED"
    assert client.get("/auth/me").json() == {
        "kind": "ok",
        "userId": str(user_id.value),
        "establishment": "ESTABLISHED",  # WU-AUTH-22
    }

    event = (
        db_connection.execute(
            sa.select(security_events_table).where(
                security_events_table.c.event_type == "AUTH_METHOD_LINKED",
                security_events_table.c.target_ref == f"user:{user_id.value}",
            )
        )
        .mappings()
        .one()
    )
    assert event["actor_id"] == str(user_id.value)
    assert "linked-subject-1" not in (event["observed_facts"] or "")


def test_the_linked_method_logs_in_as_the_same_identity(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    code = issuer.authorize(params, subject="linked-subject-2")
    _link_callback(client, code=code, state=params["state"])
    client.cookies.clear()

    start = client.get("/auth/oidc/test/start")
    login_params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(login_params, subject="linked-subject-2")
    response = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": login_params["state"]}
    )
    assert response.status_code == 303 and SESSION_COOKIE_NAME in response.cookies
    assert client.get("/auth/me").json()["userId"] == str(user_id.value)


def test_a_subject_bound_to_another_identity_cannot_be_linked(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """24 §14.4 / falsifier 61: a provider subject never moves accounts."""
    owner_id, owner_email = _local_user(db_connection)
    _login(client, owner_email)
    _, params = _link_start(client)
    assert params is not None
    _link_callback(
        client, code=issuer.authorize(params, subject="taken-subject"), state=params["state"]
    )
    client.cookies.clear()

    intruder_id, intruder_email = _local_user(db_connection)
    _login(client, intruder_email)
    _, params = _link_start(client)
    assert params is not None
    response = _link_callback(
        client, code=issuer.authorize(params, subject="taken-subject"), state=params["state"]
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/account/security?link=collision"
    row = _transaction(db_connection, params["state"])
    assert (
        row["state"] == "FAILED_TERMINAL" and row["failure_reason"] == "PROVIDER_SUBJECT_COLLISION"
    )
    binding = SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "taken-subject")
    assert binding is not None and binding.user_id == owner_id
    assert [m.method_type for m in _methods(db_connection, intruder_id)] == [
        AuthenticationMethodType.LOCAL_PASSWORD
    ]
    assert client.get("/auth/me").json()["userId"] == str(intruder_id.value)  # session untouched


def test_linking_a_subject_already_linked_to_oneself_is_not_a_second_method(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    for _ in range(2):
        _, params = _link_start(client)
        assert params is not None
        response = _link_callback(
            client, code=issuer.authorize(params, subject="mine-subject"), state=params["state"]
        )
    assert response.headers["location"] == "/account/security?link=already_linked"
    assert len(_methods(db_connection, user_id)) == 2


def test_a_link_callback_needs_the_session_of_the_initiating_user(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    code = issuer.authorize(params, subject="stranger-callback")

    # Same browser binding, but the session now belongs to someone else.
    other_id, other_email = _local_user(db_connection)
    client.cookies.delete(SESSION_COOKIE_NAME)
    _login(client, other_email)
    response = _link_callback(client, code=code, state=params["state"])

    assert response.headers["location"] == "/account/security?link=failed"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL" and row["failure_reason"] == "INITIATING_USER_MISMATCH"
    assert issuer.exchanges == []
    for identity in (user_id, other_id):
        assert [m.method_type for m in _methods(db_connection, identity)] == [
            AuthenticationMethodType.LOCAL_PASSWORD
        ]


def test_a_link_callback_without_a_session_fails_before_the_exchange(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    code = issuer.authorize(params, subject="no-session-callback")
    client.cookies.delete(SESSION_COOKIE_NAME)
    response = _link_callback(client, code=code, state=params["state"])
    assert response.headers["location"] == "/login?auth=failed"
    assert issuer.exchanges == []
    assert (
        _transaction(db_connection, params["state"])["failure_reason"] == "INITIATING_USER_MISMATCH"
    )


def test_a_login_transaction_cannot_be_consumed_by_the_link_callback_and_vice_versa(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    login_start = client.get("/auth/oidc/test/start")
    login_params = {
        k: v[0] for k, v in parse_qs(urlparse(login_start.headers["location"]).query).items()
    }
    code = issuer.authorize(login_params, subject="purpose-1")
    crossed = _link_callback(client, code=code, state=login_params["state"])
    assert crossed.headers["location"] == "/account/security?link=failed"
    assert (
        _transaction(db_connection, login_params["state"])["failure_reason"] == "PURPOSE_MISMATCH"
    )

    _, link_params = _link_start(client)
    assert link_params is not None
    code = issuer.authorize(link_params, subject="purpose-2")
    crossed = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": link_params["state"]}
    )
    assert crossed.headers["location"] == "/login?auth=failed"
    assert _transaction(db_connection, link_params["state"])["failure_reason"] == "PURPOSE_MISMATCH"
    assert issuer.exchanges == []


def test_a_transplanted_link_callback_fails_before_the_exchange(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    code = issuer.authorize(params, subject="transplant")
    client.cookies.delete(BINDING_COOKIE_NAME, path="/auth")
    response = _link_callback(client, code=code, state=params["state"])
    assert response.headers["location"] == "/account/security?link=failed"
    assert issuer.exchanges == []
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "USER_AGENT_BINDING_MISSING"
    )


def test_provider_cancel_during_a_link_terminalizes_without_effect(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    response = _link_callback(client, error="access_denied", state=params["state"])
    assert response.headers["location"] == "/account/security?link=cancelled"
    assert _transaction(db_connection, params["state"])["state"] == "CANCELLED_TERMINAL"
    assert len(_methods(db_connection, user_id)) == 1


def test_a_link_creates_no_authority(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    _, email = _local_user(db_connection)
    _login(client, email)
    before = counts()
    _, params = _link_start(client)
    assert params is not None
    _link_callback(
        client, code=issuer.authorize(params, subject="no-authority"), state=params["state"]
    )
    assert counts() == before


# ------------------------------------------------------- methods surface


def test_the_methods_list_shows_the_callers_own_methods_without_secrets(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    _, params = _link_start(client)
    assert params is not None
    _link_callback(
        client,
        code=issuer.authorize(params, subject="listed-subject", email="listed@example.test"),
        state=params["state"],
    )

    listing = client.get("/auth/methods")

    assert listing.status_code == 200
    body = listing.json()
    assert body["kind"] == "ok"
    by_type = {m["methodType"]: m for m in body["methods"]}
    assert set(by_type) == {"LOCAL_PASSWORD", "TEST_PROVIDER"}
    assert all(m["status"] == "ACTIVE" for m in body["methods"])
    provider = by_type["TEST_PROVIDER"]
    assert set(provider) == {
        "methodId",
        "methodType",
        "status",
        "createdAt",
        "lastAuthenticatedAt",
        "provider",
    }
    assert provider["provider"] == {"providerId": "test", "email": "listed@example.test"}
    assert by_type["LOCAL_PASSWORD"]["provider"] is None
    assert "listed-subject" not in listing.text
    assert "password_hash" not in listing.text and "pbkdf2" not in listing.text
    assert client.get("/auth/methods").json()["methods"][0]["methodId"]
    client.cookies.clear()
    assert client.get("/auth/methods").status_code == 401
