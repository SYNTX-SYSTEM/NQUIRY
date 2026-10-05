"""T10: the account creation boundary (24 WU-AUTH-09; §11.14, §11.15, §20.3,
§25.3, §33.9, §39.10; FBR-AUTH-007; falsifiers 46–50, 107, 109).

MUST BECOME TRUE: an unknown provider subject evaluates an explicit,
configured account creation policy; an unresolved policy fails closed; an
approved policy creates a canonical `UserId` with its provider method and
binding as one local effect, audited, with no Workspace authority.

MUST REMAIN IMPOSSIBLE: a user created by implementation convenience; a
binding by email; a self-registration policy in a production-like runtime
(HD-28: no self-service registration; 24 §36 #3–#5 undecided); membership,
role, governance root or capability by an authentication side effect; a
partial creation shown as success; duplicate users from a first-login race.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import persistence.security_event_repository as security_event_repository
import pytest
import sqlalchemy as sa
from application.auth_runtime import (
    AccountCreationPolicyForbidden,
    AccountCreationPolicyNotMaterialized,
    AuthRuntime,
    auth_runtime_from_environment,
)
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.oidc_identity import ProviderIdentityUnresolved, resolve_provider_identity
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.tables import security_events_table, users_table
from security.account_creation import AccountCreationPolicy
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.events import Environment
from security.oidc_provider import VerifiedProviderCredential
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.oidc_transaction import hash_protocol_value
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_DENIED_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
_OPEN_ENV = {**_DENIED_ENV, "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED"}
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


def _client_for(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, runtime: AuthRuntime
) -> TestClient:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        # Mirrors `persistence.engine.connect`: one request transaction, rolled
        # back on any exception, so a partial local effect never persists.
        with db_connection.begin_nested():
            yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(runtime)
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def open_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    yield _client_for(
        db_connection, monkeypatch, auth_runtime_from_environment(_OPEN_ENV, test_issuer=issuer)
    )
    configure_auth_runtime(auth_runtime_from_environment({}))


@pytest.fixture
def denied_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    yield _client_for(
        db_connection, monkeypatch, auth_runtime_from_environment(_DENIED_ENV, test_issuer=issuer)
    )
    configure_auth_runtime(auth_runtime_from_environment({}))


def _login(client: TestClient, issuer: LocalTestIssuer, *, subject: str, **claims):  # type: ignore[no-untyped-def]
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject=subject, **claims)
    return client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    ), params


def _transaction(db: sa.Connection, state: str) -> sa.RowMapping:
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


def _users(db: sa.Connection) -> int:
    return int(db.execute(sa.select(sa.func.count()).select_from(users_table)).scalar_one())


def _credential(subject: str, email: str | None = "new@example.test", verified: bool = True):  # type: ignore[no-untyped-def]
    return VerifiedProviderCredential(
        provider_id="test",
        issuer=TEST_ISSUER,
        subject=subject,
        email=email,
        email_verified=verified,
        display_name="New Person",
    )


# ------------------------------------------------------------- the policy


def test_the_policy_vocabulary_is_24_section_11_14() -> None:
    assert {member.value for member in AccountCreationPolicy} == {
        "DENIED",
        "SELF_REGISTRATION_ALLOWED",
        "INVITATION_REQUIRED",
        "PRE_PROVISIONED_IDENTITY_REQUIRED",
        "GOVERNANCE_MEDIATED_CREATION",
    }


def test_the_default_policy_is_denied(issuer: LocalTestIssuer) -> None:
    runtime = auth_runtime_from_environment(_DENIED_ENV, test_issuer=issuer)
    assert runtime.account_creation_policy is AccountCreationPolicy.DENIED
    assert auth_runtime_from_environment({}).account_creation_policy is AccountCreationPolicy.DENIED


@pytest.mark.parametrize("environment", [None, "development"])
def test_self_registration_needs_a_declared_environment(environment: str | None) -> None:
    """HD-AUTH-08 (2026-10-04, resolving HA-AUTH-01): the generic provider
    bootstrap is admitted in every DECLARED environment; an undeclared or
    unknown one is refused because the creation provenance must name it."""
    env = {"NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED"}
    if environment is not None:
        env["NQUIRY_ENVIRONMENT"] = environment
    with pytest.raises((AccountCreationPolicyForbidden, ValueError)):
        auth_runtime_from_environment(env)


@pytest.mark.parametrize("environment", ["PRODUCTION", "STAGING", "DEVELOPMENT", "TEST"])
def test_self_registration_is_admitted_in_every_declared_environment(environment: str) -> None:
    runtime = auth_runtime_from_environment(
        {
            "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
            "NQUIRY_ENVIRONMENT": environment,
        }
    )
    assert runtime.account_creation_policy is AccountCreationPolicy.SELF_REGISTRATION_ALLOWED


@pytest.mark.parametrize(
    "policy",
    ["INVITATION_REQUIRED", "PRE_PROVISIONED_IDENTITY_REQUIRED", "GOVERNANCE_MEDIATED_CREATION"],
)
def test_policies_without_a_materialized_relation_are_refused_at_startup(policy: str) -> None:
    with pytest.raises(AccountCreationPolicyNotMaterialized):
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_ACCOUNT_CREATION_POLICY": policy}
        )


def test_an_unknown_policy_value_is_refused_not_guessed() -> None:
    with pytest.raises(ValueError):
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_ACCOUNT_CREATION_POLICY": "open"}
        )


# --------------------------------------------------------------- DENIED


def test_under_denied_an_unknown_subject_creates_nothing(
    db_connection: sa.Connection, denied_client: TestClient, issuer: LocalTestIssuer
) -> None:
    before = _users(db_connection)
    response, params = _login(denied_client, issuer, subject="unknown-1", email="u1@example.test")
    assert response.headers["location"] == "/login?auth=unavailable"
    assert SESSION_COOKIE_NAME not in response.cookies
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    )
    assert _users(db_connection) == before


# ----------------------------------------------- SELF_REGISTRATION_ALLOWED


def test_under_self_registration_an_unknown_verified_subject_becomes_an_identity(
    db_connection: sa.Connection, open_client: TestClient, issuer: LocalTestIssuer
) -> None:
    before = _users(db_connection)
    response, params = _login(
        open_client, issuer, subject="first-login-1", email="First.Login@Example.test"
    )

    assert response.status_code == 303 and response.headers["location"] == "/workspaces"
    assert SESSION_COOKIE_NAME in response.cookies
    assert _transaction(db_connection, params["state"])["state"] == "COMPLETED"
    assert _users(db_connection) == before + 1
    user = (
        db_connection.execute(
            sa.select(users_table).where(users_table.c.email == "first.login@example.test")
        )
        .mappings()
        .one()
    )
    binding = SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "first-login-1")
    assert binding is not None and binding.user_id == UserId(user["id"])
    assert binding.provider_email == "First.Login@Example.test" and binding.provider_email_verified
    (method,) = SqlAlchemyAuthenticationMethodRepository(db_connection).list_for_user(
        UserId(user["id"])
    )
    assert method.method_type is AuthenticationMethodType.TEST_PROVIDER
    assert method.status is AuthenticationMethodStatus.ACTIVE
    assert method.method_id == binding.method_id
    assert open_client.get("/auth/me").json() == {"kind": "ok", "userId": str(user["id"])}

    # WU-AUTH-18: the login's own event (PROVIDER_LOGIN_SUCCEEDED) stands next to the creation event
    events = {
        row["event_type"]: row
        for row in db_connection.execute(
            sa.select(security_events_table).where(
                security_events_table.c.target_ref == f"user:{user['id']}"
            )
        ).mappings()
    }
    assert set(events) == {"IDENTITY_CREATED", "PROVIDER_LOGIN_SUCCEEDED"}
    assert events["PROVIDER_LOGIN_SUCCEEDED"]["actor_id"] == str(user["id"])
    event = events["IDENTITY_CREATED"]
    assert event["event_type"] == "IDENTITY_CREATED"
    assert event["actor_type"] == "ACCOUNT_CREATION_POLICY"
    assert event["actor_id"] == "SELF_REGISTRATION_ALLOWED"
    assert event["environment"] == "TEST"
    assert "first-login-1" not in (event["observed_facts"] or "")
    assert "example.test" not in (event["observed_facts"] or "")
    assert '"workspaceAuthority": "NONE"' in (event["observed_facts"] or "")


def test_a_second_login_of_the_created_subject_resolves_the_same_identity(
    db_connection: sa.Connection, open_client: TestClient, issuer: LocalTestIssuer
) -> None:
    first, _ = _login(open_client, issuer, subject="first-login-2", email="two@example.test")
    user_id = open_client.get("/auth/me").json()["userId"]
    before = _users(db_connection)
    open_client.cookies.clear()
    second, params = _login(open_client, issuer, subject="first-login-2", email="two@example.test")
    assert second.status_code == 303 and _users(db_connection) == before
    assert open_client.get("/auth/me").json()["userId"] == user_id
    assert first.cookies[SESSION_COOKIE_NAME] != second.cookies[SESSION_COOKIE_NAME]


def test_a_created_identity_holds_no_authority_of_any_kind(
    db_connection: sa.Connection, open_client: TestClient, issuer: LocalTestIssuer
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    before = counts()
    response, _ = _login(open_client, issuer, subject="first-login-3", email="three@example.test")
    assert response.status_code == 303
    assert counts() == before
    assert open_client.get("/workspaces").json()["workspaces"] == []


@pytest.mark.parametrize(
    ("claims", "reason"),
    [
        ({}, "PROVIDER_EMAIL_MISSING"),
    ],
)
def test_a_subject_without_a_usable_email_attribute_is_not_created(
    db_connection: sa.Connection,
    open_client: TestClient,
    issuer: LocalTestIssuer,
    claims: dict[str, str],
    reason: str,
) -> None:
    before = _users(db_connection)
    response, params = _login(open_client, issuer, subject="no-email-1", **claims)
    assert response.headers["location"] == "/login?auth=unavailable"
    assert _transaction(db_connection, params["state"])["failure_reason"] == reason
    assert _users(db_connection) == before


def test_an_unverified_provider_email_does_not_create_an_identity(
    db_connection: sa.Connection,
) -> None:
    before = _users(db_connection)
    with pytest.raises(ProviderIdentityUnresolved) as refused:
        resolve_provider_identity(
            db_connection,
            _credential("unverified-1", email="u@example.test", verified=False),
            now=_NOW,
            policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
            environment=Environment.TEST,
        )
    assert refused.value.reason.value == "PROVIDER_EMAIL_UNVERIFIED"
    assert _users(db_connection) == before


def test_a_provider_email_matching_an_existing_identity_is_a_collision_not_a_link(
    db_connection: sa.Connection, open_client: TestClient, issuer: LocalTestIssuer
) -> None:
    """Falsifiers 43, 49: an existing identity with that email is neither
    linked nor logged in, and no second identity is created."""
    existing = UserId(uuid.uuid4())
    db_connection.execute(
        sa.insert(users_table).values(
            id=existing.value,
            email="taken@example.test",
            name="Existing",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    before = _users(db_connection)
    response, params = _login(open_client, issuer, subject="collider-1", email="Taken@example.test")
    assert response.headers["location"] == "/login?auth=unavailable"
    assert SESSION_COOKIE_NAME not in response.cookies
    assert _transaction(db_connection, params["state"])["failure_reason"] == "EMAIL_COLLISION"
    assert _users(db_connection) == before
    assert (
        SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "collider-1") is None
    )
    assert SqlAlchemyAuthenticationMethodRepository(db_connection).list_for_user(existing) == ()


def test_a_failed_provenance_write_leaves_no_identity(
    db_connection: sa.Connection,
    open_client: TestClient,
    issuer: LocalTestIssuer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """24 §11.15 / §19.11: account creation, method, binding and audit are one
    local effect; if any part fails, none persists and the transaction is
    terminal, not replayable."""

    original = security_event_repository.SqlAlchemySecurityEventRepository.record

    def _boom(self: object, event: object) -> None:
        # WU-AUTH-18: the protocol's own audit events (start, failure) keep writing; the
        # creation's provenance write is the one that fails
        if getattr(event, "event_type", None) == "IDENTITY_CREATED":
            raise RuntimeError("provenance store unavailable")
        original(self, event)  # type: ignore[arg-type]

    monkeypatch.setattr(
        security_event_repository.SqlAlchemySecurityEventRepository, "record", _boom
    )
    before = _users(db_connection)
    response, params = _login(
        open_client, issuer, subject="partial-1", email="partial@example.test"
    )
    assert response.headers["location"] == "/login?auth=failed"
    assert SESSION_COOKIE_NAME not in response.cookies
    state = _transaction(db_connection, params["state"])
    assert state["state"] == "FAILED_TERMINAL" and state["failure_reason"] == "LOCAL_EFFECT_FAILURE"
    assert _users(db_connection) == before
    assert (
        SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "partial-1") is None
    )


def test_two_first_logins_of_one_subject_create_one_identity(db_connection: sa.Connection) -> None:
    """24 §33.9: the second creation waits on the first and is refused by the
    subject's uniqueness, not by process-local state."""
    engine = db_connection.engine
    first, second = engine.connect(), engine.connect()
    created_user: UserId | None = None
    try:
        first_tx = first.begin()
        winner = resolve_provider_identity(
            first,
            _credential("race-1", email="race@example.test"),
            now=_NOW,
            policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
            environment=Environment.TEST,
        )
        created_user = winner.user_id
        second_tx = second.begin()
        second.execute(sa.text("SET LOCAL lock_timeout = '300ms'"))
        with pytest.raises((sa.exc.OperationalError, ProviderIdentityUnresolved)):
            resolve_provider_identity(
                second,
                _credential("race-1", email="race@example.test"),
                now=_NOW,
                policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
                environment=Environment.TEST,
            )
        second_tx.rollback()
        first_tx.commit()
        second_tx = second.begin()
        loser = resolve_provider_identity(
            second,
            _credential("race-1", email="race@example.test"),
            now=_NOW,
            policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
            environment=Environment.TEST,
        )
        second_tx.rollback()
        assert loser.user_id == winner.user_id  # the binding now exists: no second user
        with engine.connect() as check:
            count = check.execute(
                sa.text("SELECT count(*) FROM users WHERE email = 'race@example.test'")
            ).scalar_one()
        assert count == 1
    finally:
        first.close()
        second.close()
        if created_user is not None:
            with engine.begin() as cleanup:
                # The IDENTITY_CREATED SecurityEvent is append-only evidence and stays.
                for statement in (
                    "DELETE FROM external_provider_identities WHERE user_id = :u",
                    "DELETE FROM authentication_methods WHERE user_id = :u",
                    "DELETE FROM users WHERE id = :u",
                ):
                    cleanup.execute(sa.text(statement), {"u": created_user.value})
