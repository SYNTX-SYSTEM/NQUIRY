"""PROVIDER_BOOTSTRAP (generic provider-driven identity; 24 §11.14
SELF_REGISTRATION_ALLOWED, §13.3, §13.10, §14.5, §14.7, §20.3; HA-AUTH-01).

The generic relation, independent of the concrete provider (the local test
provider stands in for any OIDC provider; Google shares the same code path):

  VERIFIED PROVIDER CREDENTIAL (issuer, subject, verified email, display name)
  → no ACTIVE binding for (issuer, subject)
  → account creation policy admits provider bootstrap
  → NQUIRY identity created with displayName := provider display-name claim,
    canonicalEmail := provider verified email (lower-cased), both COPIED at
    creation and owned by NQUIRY afterwards (never synchronized)
  → authentication method + provider binding + IDENTITY_CREATED provenance
  → fresh session; no authority of any kind.

MUST REMAIN IMPOSSIBLE: resolution by previous session / browser identity,
by email or display-name equality; a merge on email collision; a name made up
from an email; an unverified or absent email becoming a canonical email;
bootstrap without provenance; LINK or LOGIN collapsing into bootstrap;
provider attribute drift rewriting the NQUIRY identity; any role /
membership / authority from a provider login; bootstrap on PRODUCTION
while HA-AUTH-01 is DENIED.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_identity as http_identity
import application.http_oidc as http_oidc
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import configure_auth_runtime
from application.oidc_identity import ProviderIdentityUnresolved, resolve_provider_identity
from application.request_security import (
    configure_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    external_provider_identities_table,
    security_events_table,
    users_table,
)
from security.account_creation import (
    EMAIL_SOURCE_PROVIDER_VERIFIED_CLAIM,
    IDENTITY_CLASS_PROVIDER_BOOTSTRAP,
    NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM,
    AccountCreationPolicy,
)
from security.events import Environment
from security.local_auth import hash_password
from security.oidc_provider import VerifiedProviderCredential
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.oidc_transaction import OidcFailureReason, hash_protocol_value
from security.request_security import RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_BOOTSTRAP_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
}
_DENIED_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
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
    db_connection: sa.Connection,
    monkeypatch: pytest.MonkeyPatch,
    issuer: LocalTestIssuer,
    env: dict[str, str],
) -> TestClient:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (http_dispatch, http_identity, http_oidc, http_revocation):
        monkeypatch.setattr(module, "connect", _reuse)
    monkeypatch.setattr(http_dispatch, "connect_auth", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(env, test_issuer=issuer))
    configure_request_security(RequestSecurityPolicy(allowed_origins=("http://localhost:3000",)))
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    try:
        yield _client_for(db_connection, monkeypatch, issuer, _BOOTSTRAP_ENV)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


@pytest.fixture
def denied_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, issuer: LocalTestIssuer
) -> Iterator[TestClient]:
    try:
        yield _client_for(db_connection, monkeypatch, issuer, _DENIED_ENV)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


# ---------------------------------------------------------------- helpers


def _local_identity(db: sa.Connection, *, name: str = "Local Person") -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@local.example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name=name,
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def _provider_login(
    client: TestClient,
    issuer: LocalTestIssuer,
    subject: str,
    *,
    email: str | None,
    display_name: str | None = "Provider Person",
):  # type: ignore[no-untyped-def]
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject=subject, email=email, display_name=display_name)
    response = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    )
    return response, params


def _link(client: TestClient, issuer: LocalTestIssuer, subject: str, email: str) -> str:
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    response = client.get(
        "/auth/oidc/test/link/callback",
        params={
            "code": issuer.authorize(params, subject=subject, email=email),
            "state": params["state"],
        },
    )
    return str(response.headers["location"])


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


def _users(db: sa.Connection) -> list[sa.RowMapping]:
    return list(db.execute(sa.select(users_table).order_by(users_table.c.created_at)).mappings())


def _identity_of(client: TestClient) -> dict[str, object]:
    body = client.get("/auth/identity").json()
    assert body["kind"] == "ok", body
    return body  # type: ignore[no-any-return]


def _creation_event(db: sa.Connection, user_id: str) -> dict[str, object]:
    row = (
        db.execute(
            sa.select(security_events_table).where(
                security_events_table.c.target_ref == f"user:{user_id}",
                security_events_table.c.event_type == "IDENTITY_CREATED",
            )
        )
        .mappings()
        .one()
    )
    facts = json.loads(row["observed_facts"])
    facts["_actor_type"] = row["actor_type"]
    return facts  # type: ignore[no-any-return]


def _authority_counts(db: sa.Connection) -> dict[str, int]:
    return {
        t: int(db.execute(sa.text(f"SELECT count(*) FROM {t}")).scalar_one())
        for t in _AUTHORITY_TABLES
    }


def _credential(
    subject: str,
    *,
    email: str | None,
    verified: bool = True,
    display_name: str | None = "Provider Person",
) -> VerifiedProviderCredential:
    return VerifiedProviderCredential(
        provider_id="test",
        issuer=TEST_ISSUER,
        subject=subject,
        email=email,
        email_verified=verified,
        display_name=display_name,
    )


# ----------------------------------------------------- NEW PROVIDER SUBJECT


def test_a_new_verified_provider_identity_bootstraps_its_own_nquiry_identity_with_provenance(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    users_before = len(_users(db_connection))
    authority_before = _authority_counts(db_connection)

    response, params = _provider_login(
        client,
        issuer,
        "new-subject",
        email="New.Person@Provider.Example",
        display_name="New Person",
    )

    assert response.headers["location"] == "/workspaces"
    assert _transaction(db_connection, params["state"])["state"] == "COMPLETED"
    assert len(_users(db_connection)) == users_before + 1
    me = client.get("/auth/me").json()
    presentation = _identity_of(client)
    assert presentation == {
        "kind": "ok",
        "userId": me["userId"],
        "displayName": "New Person",  # the provider display-name claim, verbatim
        "canonicalEmail": "new.person@provider.example",  # the verified claim, lower-cased
    }
    methods = client.get("/auth/methods").json()["methods"]
    assert [m["methodType"] for m in methods] == ["TEST_PROVIDER"]
    assert methods[0]["provider"] == {"providerId": "test", "email": "New.Person@Provider.Example"}
    facts = _creation_event(db_connection, me["userId"])
    assert (
        facts["identityClass"] == IDENTITY_CLASS_PROVIDER_BOOTSTRAP == "PROVIDER_BOOTSTRAP_IDENTITY"
    )
    assert facts["nameSource"] == NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM
    assert facts["emailSource"] == EMAIL_SOURCE_PROVIDER_VERIFIED_CLAIM
    assert facts["providerIssuer"] == TEST_ISSUER
    assert facts["providerSubjectHash"] == hashlib.sha256(b"new-subject").hexdigest()[:16]
    assert facts["previouslyBound"] is False
    assert (
        facts["workspaceAuthority"] == "NONE" and facts["_actor_type"] == "ACCOUNT_CREATION_POLICY"
    )
    assert "subject" not in json.dumps(facts).lower().replace("providersubjecthash", "")
    assert _authority_counts(db_connection) == authority_before  # IDENTITY != AUTHORITY
    assert client.get("/workspaces").json()["workspaces"] == []
    (session,) = [s for s in client.get("/auth/sessions").json()["sessions"] if s["current"]]
    assert session["methodType"] == "TEST_PROVIDER"


def test_a_known_provider_subject_resolves_to_its_existing_identity_and_nothing_is_created(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    _provider_login(client, issuer, "known", email="known@provider.example")
    first = _identity_of(client)
    client.cookies.clear()
    users_before = len(_users(db_connection))

    _provider_login(client, issuer, "known", email="known@provider.example")

    assert _identity_of(client) == first
    assert len(_users(db_connection)) == users_before


# ---------------------------------------------------- no invention, no promotion


def test_a_provider_identity_without_a_display_name_is_refused_not_named(
    db_connection: sa.Connection,
) -> None:
    before = _users(db_connection)
    for display_name in (None, "", "   "):
        with pytest.raises(ProviderIdentityUnresolved) as refused:
            resolve_provider_identity(
                db_connection,
                _credential(
                    "nameless", email="nameless@provider.example", display_name=display_name
                ),
                now=_NOW,
                policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
                environment=Environment.TEST,
            )
        assert refused.value.reason is OidcFailureReason.PROVIDER_PROFILE_INCOMPLETE, display_name
    assert _users(db_connection) == before
    assert not any(u["name"] in ("nameless", "Nameless") for u in _users(db_connection))


def test_a_nameless_provider_login_projects_unavailable_and_commits_nothing(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    before = len(_users(db_connection))
    response, params = _provider_login(
        client, issuer, "nameless-http", email="n@provider.example", display_name=None
    )
    assert response.headers["location"] == "/login?auth=unavailable"
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "PROVIDER_PROFILE_INCOMPLETE"
    )
    assert len(_users(db_connection)) == before and client.get("/auth/me").status_code == 401


@pytest.mark.parametrize(
    ("email", "verified", "reason"),
    [
        (None, True, OidcFailureReason.PROVIDER_EMAIL_MISSING),
        ("", True, OidcFailureReason.PROVIDER_EMAIL_MISSING),
        ("u@provider.example", False, OidcFailureReason.PROVIDER_EMAIL_UNVERIFIED),
    ],
)
def test_an_absent_or_unverified_provider_email_cannot_become_a_canonical_email(
    db_connection: sa.Connection, email: str | None, verified: bool, reason: OidcFailureReason
) -> None:
    before = _users(db_connection)
    with pytest.raises(ProviderIdentityUnresolved) as refused:
        resolve_provider_identity(
            db_connection,
            _credential("unverified", email=email, verified=verified),
            now=_NOW,
            policy=AccountCreationPolicy.SELF_REGISTRATION_ALLOWED,
            environment=Environment.TEST,
        )
    assert refused.value.reason is reason
    assert _users(db_connection) == before


# ------------------------------------------------------------- COLLISION


def test_an_email_collision_is_refused_and_the_legitimate_path_is_the_identitys_own_link(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """24 §14.5: same email is never a merge. The existing identity, once
    authenticated, may LINK the provider subject; from then on the login
    resolves through that binding (CASE B), not through the email."""
    user_id, local_email = _local_identity(db_connection, name="Existing Person")
    before = len(_users(db_connection))

    response, params = _provider_login(
        client, issuer, "colliding", email=local_email.upper(), display_name="Someone Else"
    )

    assert response.headers["location"] == "/login?auth=unavailable"
    assert _transaction(db_connection, params["state"])["failure_reason"] == "EMAIL_COLLISION"
    assert len(_users(db_connection)) == before and client.get("/auth/me").status_code == 401
    # the legitimate transition: the owner authenticates and links explicitly
    assert (
        client.post("/auth/login", json={"email": local_email, "password": _PASSWORD}).status_code
        == 200
    )
    assert _link(client, issuer, "colliding", local_email) == "/account/security?link=ok"
    client.cookies.clear()
    response, _ = _provider_login(
        client, issuer, "colliding", email=local_email, display_name="Someone Else"
    )
    assert response.headers["location"] == "/workspaces"
    assert _identity_of(client)["userId"] == str(user_id.value)
    assert (
        _identity_of(client)["displayName"] == "Existing Person"
    )  # the link changed no identity attribute
    assert len(_users(db_connection)) == before


# ------------------------------------------- NO RESIDUE / NO LEAKAGE / LOCAL SAFE


def test_an_unbound_provider_never_inherits_the_identity_active_in_the_browser(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """CASE C / G: a local session A exists in the browser (not even logged
    out); an unbound provider subject logs in → a NEW identity B, never A."""
    a_id, a_email = _local_identity(db_connection, name="A Person")
    assert (
        client.post("/auth/login", json={"email": a_email, "password": _PASSWORD}).status_code
        == 200
    )
    assert _identity_of(client)["userId"] == str(a_id.value)
    a_methods_before = client.get("/auth/methods").json()["methods"]

    response, _ = _provider_login(
        client, issuer, "stranger", email="stranger@provider.example", display_name="Stranger"
    )

    assert response.headers["location"] == "/workspaces"
    b = _identity_of(client)
    assert b["userId"] != str(a_id.value) and b["displayName"] == "Stranger"
    # A is untouched: same methods, no binding, its session still its own
    a_row = (
        db_connection.execute(sa.select(users_table).where(users_table.c.id == a_id.value))
        .mappings()
        .one()
    )
    assert a_row["name"] == "A Person"
    a_bindings = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(external_provider_identities_table)
        .where(external_provider_identities_table.c.user_id == a_id.value)
    ).scalar_one()
    assert a_bindings == 0
    assert [m["methodType"] for m in a_methods_before] == ["LOCAL_PASSWORD"]
    assert (
        client.post("/auth/login", json={"email": a_email, "password": _PASSWORD}).status_code
        == 200
    )
    assert _identity_of(client)["userId"] == str(a_id.value)


# ------------------------------------------ UNLINKED SUBJECT: RE-BOOTSTRAP


def test_an_unlinked_subject_bootstraps_a_new_identity_under_the_policy(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """The subject's former owner keeps its identity and the revoked binding
    as evidence; the subject itself is simply unbound again."""
    owner_id, owner_email = _local_identity(db_connection, name="Former Owner")
    assert (
        client.post("/auth/login", json={"email": owner_email, "password": _PASSWORD}).status_code
        == 200
    )
    assert (
        _link(client, issuer, "wanderer", "wanderer@provider.example")
        == "/account/security?link=ok"
    )
    (provider_method,) = [m for m in client.get("/auth/methods").json()["methods"] if m["provider"]]
    assert client.post(f"/auth/methods/{provider_method['methodId']}/unlink").status_code == 200
    client.cookies.clear()
    users_before = len(_users(db_connection))

    response, params = _provider_login(
        client, issuer, "wanderer", email="wanderer@provider.example", display_name="Wanderer"
    )

    assert response.headers["location"] == "/workspaces"
    new = _identity_of(client)
    assert new["userId"] != str(owner_id.value) and new["displayName"] == "Wanderer"
    assert len(_users(db_connection)) == users_before + 1
    assert _creation_event(db_connection, str(new["userId"]))["previouslyBound"] is True
    owner_row = (
        db_connection.execute(sa.select(users_table).where(users_table.c.id == owner_id.value))
        .mappings()
        .one()
    )
    assert owner_row["name"] == "Former Owner"
    bindings = list(
        db_connection.execute(
            sa.select(
                external_provider_identities_table.c.user_id,
                external_provider_identities_table.c.revoked_at,
            ).where(external_provider_identities_table.c.provider_subject == "wanderer")
        ).mappings()
    )
    assert sorted(
        (str(b["user_id"]) == str(owner_id.value), b["revoked_at"] is None) for b in bindings
    ) == [
        (False, True),
        (True, False),
    ]


def test_under_denied_an_unlinked_subject_is_denied_and_an_unknown_subject_unavailable(
    db_connection: sa.Connection, denied_client: TestClient, issuer: LocalTestIssuer
) -> None:
    owner_id, owner_email = _local_identity(db_connection)
    assert (
        denied_client.post(
            "/auth/login", json={"email": owner_email, "password": _PASSWORD}
        ).status_code
        == 200
    )
    assert (
        _link(denied_client, issuer, "left", "left@provider.example") == "/account/security?link=ok"
    )
    (provider_method,) = [
        m for m in denied_client.get("/auth/methods").json()["methods"] if m["provider"]
    ]
    assert (
        denied_client.post(f"/auth/methods/{provider_method['methodId']}/unlink").status_code == 200
    )
    denied_client.cookies.clear()
    before = len(_users(db_connection))

    response, params = _provider_login(denied_client, issuer, "left", email="left@provider.example")
    assert response.headers["location"] == "/login?auth=failed"
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "AUTHENTICATION_METHOD_REVOKED"
    )
    response, params = _provider_login(
        denied_client, issuer, "never-seen", email="never@provider.example"
    )
    assert response.headers["location"] == "/login?auth=unavailable"
    assert (
        _transaction(db_connection, params["state"])["failure_reason"]
        == "ACCOUNT_CREATION_POLICY_UNRESOLVED"
    )
    assert len(_users(db_connection)) == before and denied_client.get("/auth/me").status_code == 401


# --------------------------------------------- PROVIDER ATTRIBUTE DRIFT


def test_provider_attribute_drift_refreshes_the_binding_and_never_the_nquiry_identity(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """Copied at creation, owned by NQUIRY afterwards (24 §14.7): a later
    login with a changed provider name / email changes the binding's
    attributes only; the presentation and the users row are stable; the
    provenance still answers why the identity is named as it is."""
    _provider_login(
        client, issuer, "drifter", email="old@provider.example", display_name="Old Name"
    )
    first = _identity_of(client)
    row_before = dict(
        db_connection.execute(
            sa.select(users_table).where(users_table.c.id == uuid.UUID(str(first["userId"])))
        )
        .mappings()
        .one()
    )
    client.cookies.clear()

    response, _ = _provider_login(
        client, issuer, "drifter", email="new@provider.example", display_name="New Name"
    )

    assert response.headers["location"] == "/workspaces"
    assert _identity_of(client) == first  # displayName "Old Name", canonicalEmail old@…
    row_after = dict(
        db_connection.execute(
            sa.select(users_table).where(users_table.c.id == uuid.UUID(str(first["userId"])))
        )
        .mappings()
        .one()
    )
    assert row_after == row_before
    (method,) = client.get("/auth/methods").json()["methods"]
    assert method["provider"]["email"] == "new@provider.example"  # provider truth, visible as such
    binding = (
        db_connection.execute(
            sa.select(external_provider_identities_table).where(
                external_provider_identities_table.c.provider_subject == "drifter"
            )
        )
        .mappings()
        .one()
    )
    assert (
        binding["provider_display_name"] == "New Name"
        and binding["provider_email"] == "new@provider.example"
    )
    facts = _creation_event(db_connection, str(first["userId"]))
    assert (
        facts["nameSource"] == NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM
    )  # WHY is this person called this


# --------------------------------------------------------- DISTINCTIONS


def test_bootstrap_login_and_link_remain_three_relations(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """LINK never bootstraps (a link callback for an unbound subject binds it
    to the authenticated identity; it creates no identity); LOGIN of a bound
    subject never links anything new; BOOTSTRAP happens only in LOGIN of an
    unbound subject under the policy."""
    owner_id, owner_email = _local_identity(db_connection, name="Owner")
    users_before = len(_users(db_connection))
    assert (
        client.post("/auth/login", json={"email": owner_email, "password": _PASSWORD}).status_code
        == 200
    )
    assert (
        _link(client, issuer, "attached", "attached@provider.example")
        == "/account/security?link=ok"
    )
    assert len(_users(db_connection)) == users_before  # LINK != BOOTSTRAP
    client.cookies.clear()
    response, _ = _provider_login(
        client, issuer, "attached", email="attached@provider.example", display_name="Attached"
    )
    assert _identity_of(client)["userId"] == str(owner_id.value)  # LOGIN of a bound subject → owner
    assert len(_users(db_connection)) == users_before
    assert len(client.get("/auth/methods").json()["methods"]) == 2  # no third method appeared


def test_the_bootstrap_policy_is_admitted_in_production_and_refused_without_an_environment() -> (
    None
):
    """HD-AUTH-08: generic provider bootstrap is a production capability; the
    default stays DENIED and an undeclared environment is refused."""
    from application.auth_runtime import AccountCreationPolicyForbidden

    for environment in ("PRODUCTION", "STAGING"):
        runtime = auth_runtime_from_environment(
            {
                "NQUIRY_ENVIRONMENT": environment,
                "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
            }
        )
        assert runtime.account_creation_policy is AccountCreationPolicy.SELF_REGISTRATION_ALLOWED
    assert (
        auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "PRODUCTION"}).account_creation_policy
        is AccountCreationPolicy.DENIED
    )
    with pytest.raises(AccountCreationPolicyForbidden):
        auth_runtime_from_environment(
            {"NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED"}
        )
