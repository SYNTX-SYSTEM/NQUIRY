"""T10: provider identity binding (24 WU-AUTH-08; §11.13–11.14, §13.3, §13.10,
§14.7, §19.1, §19.3, §22.3, §33.9; falsifiers 1, 42, 43, 47–50).

MUST BECOME TRUE: `provider_issuer + provider_subject` maps to a canonical
`UserId` through a provider identity binding of an ACTIVE method; a provider
login through an existing binding creates a fresh session traceable to that
method and updates the provider attributes only.

MUST REMAIN IMPOSSIBLE: linking or logging in by email equality; a provider
subject trusted before ID Token validation (proven in WU-AUTH-07); an
unknown subject creating a user without policy; two identities bound to the
same issuer + subject; a binding on a non-provider method or on another
user's method; a revoked method still producing sessions; any Workspace
authority from a provider login.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import AuthRuntime, auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.tables import (
    external_provider_identities_table,
    local_auth_sessions_table,
    users_table,
)
from security.auth_methods import AuthenticationMethodType
from security.local_auth import hash_password, hash_session_token
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.oidc_transaction import hash_protocol_value
from security.provider_identity import ProviderIdentityConflict
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_TEST_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
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
def runtime(issuer: LocalTestIssuer) -> AuthRuntime:
    return auth_runtime_from_environment(_TEST_ENV, test_issuer=issuer)


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, runtime: AuthRuntime
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(runtime)
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _user(db: sa.Connection, *, email: str | None = None) -> UserId:
    user_id = UserId(uuid.uuid4())
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email or f"{user_id.value}@example.test",
            name="Provider User",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return user_id


def _bind(
    db: sa.Connection,
    user_id: UserId,
    *,
    subject: str,
    issuer: str = TEST_ISSUER,
    method_type: AuthenticationMethodType = AuthenticationMethodType.TEST_PROVIDER,
    email: str | None = None,
):  # type: ignore[no-untyped-def]
    method = SqlAlchemyAuthenticationMethodRepository(db).create(
        user_id=user_id, method_type=method_type, provenance_ref="test:wu-auth-08", now=_NOW
    )
    binding = SqlAlchemyProviderIdentityRepository(db).create(
        method_id=method.method_id,
        user_id=user_id,
        provider_issuer=issuer,
        provider_subject=subject,
        provider_email=email,
        provider_email_verified=email is not None,
        provider_display_name=None,
        now=_NOW,
        provenance_ref="test:wu-auth-08",
    )
    return method, binding


def _login_via_provider(
    client: TestClient, issuer: LocalTestIssuer, *, subject: str, **claims: str
):  # type: ignore[no-untyped-def]
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject=subject, **claims)
    response = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    )
    return response, params


def _transaction_state(db: sa.Connection, state: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.text(
                "SELECT state, failure_reason FROM oidc_auth_transactions WHERE state_hash = :h"
            ),
            {"h": hash_protocol_value(state)},
        )
        .mappings()
        .one()
    )


def _session_row(db: sa.Connection, token: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.session_token_hash == hash_session_token(token)
            )
        )
        .mappings()
        .one()
    )


# ----------------------------------------------------------- the relation


def test_a_binding_maps_issuer_and_subject_to_a_user_never_an_email(
    db_connection: sa.Connection,
) -> None:
    user_id = _user(db_connection)
    method, binding = _bind(db_connection, user_id, subject="s-1", email="one@example.test")
    repository = SqlAlchemyProviderIdentityRepository(db_connection)
    found = repository.find(TEST_ISSUER, "s-1")
    assert found is not None and found.user_id == user_id and found.method_id == method.method_id
    assert repository.find(TEST_ISSUER, "s-2") is None
    assert repository.find("https://another-issuer.nquiry.local", "s-1") is None
    public = {name for name in dir(repository) if not name.startswith("_")}
    assert public == {
        "create",
        "find",
        "list_for_user",
        "authenticate",
    }  # by id or user, never by email
    assert "email" not in " ".join(public)


def test_the_same_issuer_and_subject_cannot_be_bound_to_two_identities(
    db_connection: sa.Connection,
) -> None:
    first, second = _user(db_connection), _user(db_connection)
    _bind(db_connection, first, subject="shared-subject")
    # The database's uniqueness, translated by the adapter into the typed
    # conflict the account creation / linking effects consume (WU-AUTH-09).
    with pytest.raises(ProviderIdentityConflict), db_connection.begin_nested():
        _bind(db_connection, second, subject="shared-subject")


def test_the_same_subject_at_another_issuer_is_another_binding(
    db_connection: sa.Connection,
) -> None:
    first, second = _user(db_connection), _user(db_connection)
    _bind(db_connection, first, subject="subject-x")
    _bind(db_connection, second, subject="subject-x", issuer="https://another-issuer.nquiry.local")
    repository = SqlAlchemyProviderIdentityRepository(db_connection)
    assert repository.find(TEST_ISSUER, "subject-x").user_id == first  # type: ignore[union-attr]
    assert repository.find("https://another-issuer.nquiry.local", "subject-x").user_id == second  # type: ignore[union-attr]


def test_two_identities_may_carry_the_same_provider_email(db_connection: sa.Connection) -> None:
    """Email is an attribute, not identity (24 §10.4): two subjects with the
    same provider email are two bindings of two identities."""
    first, second = _user(db_connection), _user(db_connection)
    _bind(db_connection, first, subject="s-a", email="same@example.test")
    _bind(db_connection, second, subject="s-b", email="same@example.test")
    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(external_provider_identities_table)
        .where(external_provider_identities_table.c.provider_email == "same@example.test")
    ).scalar_one()
    assert count == 2


def test_a_binding_needs_a_provider_method_of_the_same_user(db_connection: sa.Connection) -> None:
    owner, other = _user(db_connection), _user(db_connection)
    repository = SqlAlchemyProviderIdentityRepository(db_connection)
    methods = SqlAlchemyAuthenticationMethodRepository(db_connection)
    local = methods.create(
        user_id=owner,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref="test",
        now=_NOW,
    )
    with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
        repository.create(
            method_id=local.method_id,
            user_id=owner,
            provider_issuer=TEST_ISSUER,
            provider_subject="s-local",
            provider_email=None,
            provider_email_verified=False,
            provider_display_name=None,
            now=_NOW,
            provenance_ref="test",
        )
    assert "LOCAL_PASSWORD" in str(refused.value) or "provider" in str(refused.value)
    foreign = methods.create(
        user_id=other,
        method_type=AuthenticationMethodType.TEST_PROVIDER,
        provenance_ref="test",
        now=_NOW,
    )
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        repository.create(
            method_id=foreign.method_id,
            user_id=owner,
            provider_issuer=TEST_ISSUER,
            provider_subject="s-foreign",
            provider_email=None,
            provider_email_verified=False,
            provider_display_name=None,
            now=_NOW,
            provenance_ref="test",
        )


def test_one_method_carries_at_most_one_binding_and_the_link_is_immutable(
    db_connection: sa.Connection,
) -> None:
    user_id = _user(db_connection)
    method, binding = _bind(db_connection, user_id, subject="s-1")
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        SqlAlchemyProviderIdentityRepository(db_connection).create(
            method_id=method.method_id,
            user_id=user_id,
            provider_issuer=TEST_ISSUER,
            provider_subject="s-other",
            provider_email=None,
            provider_email_verified=False,
            provider_display_name=None,
            now=_NOW,
            provenance_ref="test",
        )
    successor = SqlAlchemyAuthenticationMethodRepository(db_connection).create(
        user_id=user_id,
        method_type=AuthenticationMethodType.TEST_PROVIDER,
        provenance_ref="test",
        now=_NOW,
    )
    for assignment in (
        "provider_subject = 'moved'",
        "provider_issuer = 'https://elsewhere.nquiry.local'",
        "authentication_method_id = :successor",
        "user_id = :other",
    ):
        with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"UPDATE external_provider_identities SET {assignment} WHERE id = :id"),
                {
                    "id": binding.binding_id,
                    "successor": successor.method_id.value,
                    "other": _user(db_connection).value,
                },
            )
        assert "immutable" in str(refused.value), assignment


# ------------------------------------------------------ provider login path


def test_an_existing_binding_logs_in_with_a_fresh_session_traceable_to_the_method(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id = _user(db_connection)
    method, _ = _bind(db_connection, user_id, subject="bound-1", email="old@example.test")

    response, params = _login_via_provider(
        client, issuer, subject="bound-1", email="new@example.test"
    )

    assert response.status_code == 303 and response.headers["location"] == "/workspaces"
    token = response.cookies[SESSION_COOKIE_NAME]
    assert "httponly" in response.headers["set-cookie"].lower()
    row = _session_row(db_connection, token)
    assert row["user_id"] == user_id.value
    assert row["authentication_method_id"] == method.method_id.value
    assert _transaction_state(db_connection, params["state"])["state"] == "COMPLETED"
    assert client.get("/auth/me").json() == {"kind": "ok", "userId": str(user_id.value)}

    after = SqlAlchemyAuthenticationMethodRepository(db_connection).get(method.method_id)
    assert after is not None and after.last_authenticated_at is not None
    binding = SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "bound-1")
    assert binding is not None and binding.user_id == user_id  # the link did not move
    assert binding.provider_email == "new@example.test"  # the attribute did (24 §14.7)
    user_email = db_connection.execute(
        sa.select(users_table.c.email).where(users_table.c.id == user_id.value)
    ).scalar_one()
    assert user_email != "new@example.test"  # canonical identity unchanged


def test_a_provider_login_replaces_any_planted_session_cookie(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id = _user(db_connection)
    _bind(db_connection, user_id, subject="bound-2")
    client.cookies.set(SESSION_COOKIE_NAME, "planted-by-someone-else")
    response, _ = _login_via_provider(client, issuer, subject="bound-2")
    issued = response.cookies[SESSION_COOKIE_NAME]
    assert issued != "planted-by-someone-else"
    assert client.get("/auth/me").json()["userId"] == str(user_id.value)


def test_an_unknown_subject_creates_neither_user_nor_binding_nor_session(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    users_before = db_connection.execute(
        sa.select(sa.func.count()).select_from(users_table)
    ).scalar_one()
    response, params = _login_via_provider(
        client, issuer, subject="nobody-knows-me", email="new@example.test"
    )
    assert response.headers["location"] == "/login?auth=unavailable"
    assert SESSION_COOKIE_NAME not in response.cookies
    state = _transaction_state(db_connection, params["state"])
    assert state["state"] == "FAILED_TERMINAL"
    assert state["failure_reason"] == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    assert (
        db_connection.execute(sa.select(sa.func.count()).select_from(users_table)).scalar_one()
        == users_before
    )
    assert (
        SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "nobody-knows-me")
        is None
    )


def test_a_matching_email_without_a_binding_does_not_log_in(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """Falsifiers 43, 49: an identity with a local password and the same email
    as the provider's claim is not linked and not logged in."""
    user_id = _user(db_connection, email="collide@example.test")
    SqlAlchemyLocalCredentialRepository(db_connection).create(
        user_id=user_id, password_hash=hash_password("correct horse battery staple"), now=_NOW
    )
    response, params = _login_via_provider(
        client, issuer, subject="new-subject", email="collide@example.test"
    )
    assert response.headers["location"] == "/login?auth=unavailable"
    assert SESSION_COOKIE_NAME not in response.cookies
    assert _transaction_state(db_connection, params["state"])["state"] == "FAILED_TERMINAL"
    assert (
        SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "new-subject") is None
    )
    sessions = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(local_auth_sessions_table)
        .where(local_auth_sessions_table.c.user_id == user_id.value)
    ).scalar_one()
    assert sessions == 0


def test_a_revoked_provider_method_cannot_log_in(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id = _user(db_connection)
    method, _ = _bind(db_connection, user_id, subject="revoked-1")
    SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
        method.method_id, revoked_at=_NOW + timedelta(minutes=1)
    )
    response, params = _login_via_provider(client, issuer, subject="revoked-1")
    assert response.headers["location"] == "/login?auth=failed"
    assert SESSION_COOKIE_NAME not in response.cookies
    state = _transaction_state(db_connection, params["state"])
    assert state["state"] == "FAILED_TERMINAL"
    assert state["failure_reason"] == "AUTHENTICATION_METHOD_REVOKED"


def test_a_provider_login_creates_no_authority(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    user_id = _user(db_connection)
    _bind(db_connection, user_id, subject="bound-3")
    before = counts()
    response, _ = _login_via_provider(client, issuer, subject="bound-3")
    assert response.status_code == 303 and SESSION_COOKIE_NAME in response.cookies
    assert counts() == before
    denied = client.get("/workspaces")
    assert denied.status_code == 200 and denied.json()["workspaces"] == []


def test_the_provider_login_session_is_a_normal_session(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """Logout, all-session logout and the session list treat a provider
    session like any other; its method type is reported."""
    user_id = _user(db_connection)
    _bind(db_connection, user_id, subject="bound-4")
    _login_via_provider(client, issuer, subject="bound-4")
    listing = client.get("/auth/sessions").json()
    assert [item["methodType"] for item in listing["sessions"]] == ["TEST_PROVIDER"]
    assert client.post("/auth/logout").status_code == 200
    assert client.get("/auth/me").status_code == 401
