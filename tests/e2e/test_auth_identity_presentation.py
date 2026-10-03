"""PURPLE_IDENTITY_PRESENTATION_01: the authenticated self's human-facing
identity presentation (24 §13.1 canonical identity; §20.1 AUTHENTICATION !=
AUTHORIZATION; HD-28 identity creation).

Reconstructed source (STATE A): `users.name` and `users.email` are NOT NULL
attributes of the canonical identity row, produced only by the identity
creation authority (HD-28 host operator; DEV / TEST policy creation), never
mutated by any authentication relation, and already projected to other humans
(member rosters, participants). They are therefore authoritative for the
identity's own presentation, independent of how the current session was made.

MUST BECOME TRUE: `GET /auth/identity` returns, for the live session's own
identity only, `{kind: ok, userId, displayName, canonicalEmail}` — the same
values whether the session came from LOCAL_PASSWORD or GOOGLE_OIDC, before and
after a link, after a rotation, after an unlink.

MUST REMAIN IMPOSSIBLE: provider email or provider display name entering the
presentation; a name derived from an email; any role / membership / authority
key; reading another identity's presentation; a presentation without a live
session; `/auth/me` changing shape (it stays the authentication verdict).
"""

from __future__ import annotations

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
from application.request_security import (
    configure_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.tables import users_table
from security.auth_methods import AuthenticationMethodType
from security.local_auth import hash_password
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.request_security import RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AUTH_PROVIDER_MODE": "test"}
_PRESENTATION_KEYS = {"kind", "userId", "displayName", "canonicalEmail"}


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

    for module in (http_dispatch, http_identity, http_oidc, http_revocation):
        monkeypatch.setattr(module, "connect", _reuse)
    monkeypatch.setattr(http_dispatch, "connect_auth", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer))
    configure_request_security(RequestSecurityPolicy(allowed_origins=("http://localhost:3000",)))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


def _identity(
    db: sa.Connection, *, name: str = "Tobias Example", email: str | None = None
) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    address = email or f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=address,
            name=name,
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, address


def _bind(db: sa.Connection, user_id: UserId, subject: str, provider_email: str) -> None:
    method = SqlAlchemyAuthenticationMethodRepository(db).create(
        user_id=user_id,
        method_type=AuthenticationMethodType.TEST_PROVIDER,
        provenance_ref="test:identity-presentation",
        now=_NOW,
    )
    SqlAlchemyProviderIdentityRepository(db).create(
        method_id=method.method_id,
        user_id=user_id,
        provider_issuer=TEST_ISSUER,
        provider_subject=subject,
        provider_email=provider_email,
        provider_email_verified=True,
        provider_display_name="Provider Profile Name",
        now=_NOW,
        provenance_ref="test:identity-presentation",
    )


def _login(client: TestClient, email: str) -> None:
    assert (
        client.post("/auth/login", json={"email": email, "password": _PASSWORD}).status_code == 200
    )


def _provider_login(client: TestClient, issuer: LocalTestIssuer, subject: str, email: str) -> None:
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    response = client.get(
        "/auth/oidc/test/callback",
        params={
            "code": issuer.authorize(params, subject=subject, email=email),
            "state": params["state"],
        },
    )
    assert response.headers["location"] == "/workspaces"


def _link(client: TestClient, issuer: LocalTestIssuer, subject: str, email: str) -> None:
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    response = client.get(
        "/auth/oidc/test/link/callback",
        params={
            "code": issuer.authorize(params, subject=subject, email=email),
            "state": params["state"],
        },
    )
    assert response.headers["location"] == "/account/security?link=ok"


def _presentation(client: TestClient) -> dict[str, object]:
    response = client.get("/auth/identity")
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def _current_method(client: TestClient) -> str:
    (current,) = [s for s in client.get("/auth/sessions").json()["sessions"] if s["current"]]
    return str(current["methodType"])


def _users_row(db: sa.Connection, user_id: UserId) -> sa.RowMapping:
    return (
        db.execute(sa.select(users_table).where(users_table.c.id == user_id.value)).mappings().one()
    )


# ------------------------------------------------------------ the contract


def test_a_local_password_session_reads_its_own_identity_presentation(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """FALSIFIER_02: no provider needed; the presentation is identity truth."""
    user_id, email = _identity(db_connection, name="Tobias Example")
    _login(client, email)

    body = _presentation(client)

    assert body == {
        "kind": "ok",
        "userId": str(user_id.value),
        "displayName": "Tobias Example",
        "canonicalEmail": email,
    }
    assert set(body) == _PRESENTATION_KEYS  # FALSIFIER_13: nothing else


def test_auth_me_keeps_its_verdict_shape(db_connection: sa.Connection, client: TestClient) -> None:
    _, email = _identity(db_connection)
    _login(client, email)
    assert set(client.get("/auth/me").json()) == {"kind", "userId"}


def test_unauthenticated_requests_leak_no_presentation(client: TestClient) -> None:
    """FALSIFIER_11."""
    response = client.get("/auth/identity")
    assert response.status_code == 401
    assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}
    client.cookies.set("nquiry_session", "not-a-session")
    assert client.get("/auth/identity").status_code == 401


def test_the_relation_is_self_only(db_connection: sa.Connection, client: TestClient) -> None:
    """FALSIFIER_12: there is no parameter by which A could name B."""
    a_id, a_email = _identity(db_connection, name="A Person")
    b_id, _ = _identity(db_connection, name="B Person")
    _login(client, a_email)
    body = _presentation(client)
    assert body["userId"] == str(a_id.value) and body["displayName"] == "A Person"
    for probe in (f"/auth/identity/{b_id.value}", f"/auth/identity?userId={b_id.value}"):
        response = client.get(probe)
        assert response.status_code == 404 or response.json()["userId"] == str(a_id.value), probe


# -------------------------------------------------- method invariance laws


def test_local_and_provider_sessions_of_one_identity_present_the_same_human(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """FALSIFIER_01 / _03 / _15 / _16: the presentation is invariant across the
    authentication method; the provider email stays in the method inventory."""
    user_id, email = _identity(db_connection, name="Tobias Example")
    _bind(db_connection, user_id, "same-human", "external-provider@example.test")
    _login(client, email)
    via_local = _presentation(client)
    local_session = _current_method(client)
    client.cookies.clear()
    _provider_login(client, issuer, "same-human", "external-provider@example.test")
    via_provider = _presentation(client)
    provider_session = _current_method(client)
    client.cookies.clear()
    _login(client, email)
    via_local_again = _presentation(client)

    assert via_local == via_provider == via_local_again
    assert via_local["canonicalEmail"] == email != "external-provider@example.test"
    assert via_local["displayName"] == "Tobias Example" != "Provider Profile Name"
    assert (local_session, provider_session) == ("LOCAL_PASSWORD", "TEST_PROVIDER")
    methods = client.get("/auth/methods").json()["methods"]
    (provider_method,) = [m for m in methods if m["provider"]]
    assert provider_method["provider"]["email"] == "external-provider@example.test"


def test_linking_a_provider_does_not_touch_the_presentation(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """FALSIFIER_04 / _14: link transaction completes, session rotates,
    `users` row and presentation unchanged; provider email only in methods."""
    user_id, email = _identity(db_connection, name="Tobias Example")
    _login(client, email)
    before = _presentation(client)
    row_before = dict(_users_row(db_connection, user_id))

    _link(client, issuer, "linked-later", "external-provider@example.test")

    assert _presentation(client) == before
    assert dict(_users_row(db_connection, user_id)) == row_before  # no identity mutation
    assert _current_method(client) == "LOCAL_PASSWORD"


def test_unlinking_the_provider_leaves_the_presentation(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    """FALSIFIER_05 (fixture proof; no production unlink)."""
    user_id, email = _identity(db_connection, name="Tobias Example")
    _bind(db_connection, user_id, "to-unlink", "external-provider@example.test")
    _login(client, email)
    before = _presentation(client)
    methods = client.get("/auth/methods").json()["methods"]
    (provider_method,) = [m for m in methods if m["provider"]]
    assert client.post(f"/auth/methods/{provider_method['methodId']}/unlink").status_code == 200
    assert _presentation(client) == before


# ----------------------------------------------- no promotion, no invention


def test_equal_strings_stay_separate_relations(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """FALSIFIER_09: provider email == canonical email by value; the
    presentation still reads the identity row, the method keeps its own."""
    user_id, email = _identity(db_connection, name="Tobias Example")
    _bind(db_connection, user_id, "same-address", email)
    _login(client, email)
    body = _presentation(client)
    assert body["canonicalEmail"] == email
    methods = client.get("/auth/methods").json()["methods"]
    (provider_method,) = [m for m in methods if m["provider"]]
    assert provider_method["provider"]["email"] == email
    assert "provider" not in body and "providerEmail" not in body


def test_names_are_never_derived_or_invented(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """FALSIFIER_06 / _08: the display name is the identity row verbatim,
    never the email local-part, never the provider profile name."""
    user_id, email = _identity(
        db_connection, name="Ravi Ó. Live-Review", email="ravi.review@example.test"
    )
    _bind(db_connection, user_id, "other-mailbox", "ravi.private@provider.example")
    _login(client, email)
    body = _presentation(client)
    assert body["displayName"] == "Ravi Ó. Live-Review"
    assert body["displayName"] not in ("ravi.review", "Ravi", "Provider Profile Name")
    assert body["canonicalEmail"] == "ravi.review@example.test"


def test_a_session_whose_identity_row_is_gone_fails_closed(
    db_connection: sa.Connection, client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FALSIFIER_10: a malformed source (no identity row behind the principal)
    is a denial, never a partial or synthesized presentation."""
    from application import identity_presentation

    _, email = _identity(db_connection)
    _login(client, email)
    monkeypatch.setattr(
        identity_presentation.SqlAlchemyIdentityRepository,
        "presentation",
        lambda self, user_id: None,
    )
    response = client.get("/auth/identity")
    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


def test_the_contract_carries_no_authority_shape(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """FALSIFIER_13 as a structural statement about the dataclass."""
    import dataclasses

    from application.identity_presentation import IdentityPresentation

    assert {f.name for f in dataclasses.fields(IdentityPresentation)} == {
        "user_id",
        "display_name",
        "canonical_email",
    }
