"""T16: authorization regression (24 WU-AUTH-16; §20.1–20.3; §11.14; §38
falsifiers 71–73; §44.9).

MUST BECOME TRUE: nothing this Field added alters membership, role or
authority. Every kind of authenticated identity the Field can now produce —
local password, provider-created, provider-linked (logged in through the
provider), recovered (logged in with the reset password), unlinked (logged
in through the remaining method), rotated session (after a link) — reaches
the existing authority resolver with exactly the same `AuthenticatedPrincipal`
shape, is denied on every protected route of Workspace A without disclosure
or mutation, holds no authority relation, and gains access only through the
governed membership command, not through its login kind.

MUST REMAIN IMPOSSIBLE: a provider login granting Workspace authority; an
identity creation creating a governance root; a login kind that the
authority resolver treats differently from another.

Reuses the F09-2 isolation sweep's world and route table (`ROUTES`), so the
regression covers every protected route the repository serves.
"""

from __future__ import annotations

import dataclasses
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_f02 as http_f02
import application.http_f04 as http_f04
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
import test_pfc_f09_2_isolation_sweep as sweep
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import configure_auth_runtime
from application.request_security import (
    configure_request_security,
    request_security_from_environment,
)
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import users_table
from security.identity import AuthenticatedPrincipal
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.oidc_test_issuer import LocalTestIssuer
from security.request_security import RequestSecurityPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_NEW_PASSWORD = "a brand new passphrase 2030"
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
    "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
}
_INSERT_VERIFIED_EMAIL = sa.text(
    "INSERT INTO verified_emails"
    " (id, user_id, email, verified_at, verification_method, provenance_ref)"
    " VALUES (:id, :u, :e, :at, 'EMAIL_CHALLENGE', 'test')"
)


@pytest.fixture
def issuer() -> LocalTestIssuer:
    return LocalTestIssuer.create()


@pytest.fixture
def mail() -> LocalMailCapture:
    return LocalMailCapture()


@pytest.fixture
def db(
    db_connection: sa.Connection,
    monkeypatch: pytest.MonkeyPatch,
    issuer: LocalTestIssuer,
    mail: LocalMailCapture,
) -> Iterator[sa.Connection]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (
        http_dispatch,
        http_f02,
        http_f04,
        http_oidc,
        http_email,
        http_recovery,
        http_revocation,
    ):
        monkeypatch.setattr(module, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=mail))
    configure_request_security(RequestSecurityPolicy(allowed_origins=("http://localhost:3000",)))
    try:
        yield db_connection
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))
        configure_request_security(request_security_from_environment({}))


# ------------------------------------------------------------ identity kinds


def _local_user(db: sa.Connection, *, verified: bool = False) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Kind",
            record_version=1,
            created_at=_NOW,
            established_at=_NOW,  # WU-AUTH-22: established
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    if verified:
        db.execute(
            _INSERT_VERIFIED_EMAIL,
            {"id": uuid.uuid4(), "u": user_id.value, "e": email, "at": _NOW},
        )
    return user_id, email


def _password_login(client: TestClient, email: str, password: str = _PASSWORD) -> None:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text


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
    assert response.headers["location"] == "/workspaces", response.headers.get("location")


def _link(client: TestClient, issuer: LocalTestIssuer, subject: str) -> None:
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    response = client.get(
        "/auth/oidc/test/link/callback",
        params={"code": issuer.authorize(params, subject=subject), "state": params["state"]},
    )
    assert response.headers["location"] == "/account/security?link=ok"


def _me(client: TestClient) -> str:
    body = client.get("/auth/me").json()
    assert body["kind"] == "ok", body
    return str(body["userId"])


Kind = Callable[[sa.Connection, LocalTestIssuer, LocalMailCapture], tuple[TestClient, str]]


def _kind_local(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    user_id, email = _local_user(db)
    client = TestClient(app, follow_redirects=False)
    _password_login(client, email)
    return client, str(user_id.value)


def _kind_provider_created(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    client = TestClient(app, follow_redirects=False)
    stamp = uuid.uuid4().hex[:8]
    _provider_login(client, issuer, f"created-{stamp}", f"created-{stamp}@example.test")
    return client, _me(client)


def _kind_linked_provider_login(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    user_id, email = _local_user(db)
    client = TestClient(app, follow_redirects=False)
    _password_login(client, email)
    subject = f"linked-{uuid.uuid4().hex[:8]}"
    _link(client, issuer, subject)
    client.cookies.clear()
    _provider_login(client, issuer, subject, email)
    return client, str(user_id.value)


def _kind_rotated_after_link(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    user_id, email = _local_user(db)
    client = TestClient(app, follow_redirects=False)
    _password_login(client, email)
    _link(client, issuer, f"rotated-{uuid.uuid4().hex[:8]}")  # the session is rotated here
    return client, str(user_id.value)


def _kind_recovered(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    user_id, email = _local_user(db, verified=True)
    client = TestClient(app, follow_redirects=False)
    assert client.post("/auth/recovery/start", json={"email": email}).json() == {"kind": "ok"}
    delivered = mail.outbox[-1]
    assert (
        client.post(
            "/auth/recovery/complete",
            json={
                "recoveryId": delivered.challenge_id,
                "token": delivered.token,
                "newPassword": _NEW_PASSWORD,
            },
        ).status_code
        == 200
    )
    _password_login(client, email, _NEW_PASSWORD)
    return client, str(user_id.value)


def _kind_unlinked(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> tuple[TestClient, str]:
    user_id, email = _local_user(db)
    client = TestClient(app, follow_redirects=False)
    _password_login(client, email)
    _link(client, issuer, f"unlinked-{uuid.uuid4().hex[:8]}")
    methods = client.get("/auth/methods").json()["methods"]
    (provider_method,) = [m for m in methods if m["methodType"] == "TEST_PROVIDER"]
    assert client.post(f"/auth/methods/{provider_method['methodId']}/unlink").status_code == 200
    return client, str(user_id.value)


KINDS: dict[str, Kind] = {
    "local_password": _kind_local,
    "provider_created": _kind_provider_created,
    "linked_then_provider_login": _kind_linked_provider_login,
    "rotated_after_link": _kind_rotated_after_link,
    "recovered": _kind_recovered,
    "unlinked_remaining_method": _kind_unlinked,
}


def _authority_rows(db: sa.Connection, user_id: str) -> dict[str, int]:
    """Every relation that could carry authority for this identity."""
    uid = uuid.UUID(user_id)
    queries = {
        "workspaces_owned": "SELECT count(*) FROM workspaces WHERE owner_id = :u",
        "memberships": "SELECT count(*) FROM workspace_memberships WHERE user_id = :u",
        "role_assignments": (
            "SELECT count(*) FROM role_assignments r JOIN workspace_memberships m "
            "ON m.id = r.membership_id WHERE m.user_id = :u"
        ),
        "bindings": "SELECT count(*) FROM human_authority_bindings WHERE human_user_id = :u",
        "participations": "SELECT count(*) FROM session_participations WHERE user_id = :u",
    }
    return {
        name: int(db.execute(sa.text(q), {"u": uid}).scalar_one()) for name, q in queries.items()
    }


# ---------------------------------------------------------------- the proofs


def test_the_principal_shape_is_24_section_20_1_and_nothing_more() -> None:
    assert {f.name for f in dataclasses.fields(AuthenticatedPrincipal)} == {
        "user_id",
        "authentication_session_ref",
        "authentication_time",
        "issuer_ref",
    }


@pytest.mark.parametrize("kind", list(KINDS))
def test_every_identity_kind_holds_no_authority_and_is_denied_on_every_protected_route(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture, kind: str
) -> None:
    """The F09-2 isolation sweep, re-run for each identity kind this Field
    can produce, as the outsider of Workspace A."""
    w = sweep._world(db)
    client, user_id = KINDS[kind](db, issuer, mail)
    assert _me(client) == user_id
    assert _authority_rows(db, user_id) == dict.fromkeys(_authority_rows(db, user_id), 0), kind
    assert client.get("/workspaces").json() == {"kind": "ok", "workspaces": []}
    world = {**w, "outsider": user_id, "outsider_id": UserId(uuid.UUID(user_id))}
    before = sweep._counts(db)
    for method, path, body in sweep.ROUTES:
        if (method, path) in sweep._CROSS_WORKSPACE_EXEMPT:
            continue
        response = sweep._call(client, method, path, body, world)
        payload = response.json()
        assert response.status_code in (200, 403), (kind, path, response.status_code, response.text)
        assert payload["kind"] == "denied", (kind, path, payload)
        assert set(payload) <= {"kind", "reasonCode", "result"}, (kind, path, payload)
        for value in (w["challenge"], w["session"], w["binding"], w["decision"]):
            assert value not in response.text, (kind, path, "Workspace A id disclosed")
    assert sweep._counts(db) == before, kind
    assert _authority_rows(db, user_id) == dict.fromkeys(_authority_rows(db, user_id), 0), kind


@pytest.mark.parametrize("kind", list(KINDS))
def test_access_comes_from_membership_not_from_the_login_kind(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture, kind: str
) -> None:
    """The one lawful path to Workspace A is the owner's governed membership
    command; afterwards the identity reads the Workspace like any member and
    still holds no role, binding or participation it was not given."""
    w = sweep._world(db)
    client, user_id = KINDS[kind](db, issuer, mail)
    assert client.get(f"/workspaces/{w['ws']}").json()["kind"] == "denied"
    owner = sweep._client(db, w["owner"])
    added = owner.post(
        f"/workspaces/{w['ws']}/members",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={"userId": user_id, "role": "Contributor"},
    )
    assert added.json()["kind"] in ("ok", "committed"), (kind, added.text)

    assert client.get(f"/workspaces/{w['ws']}").json()["kind"] == "ok", kind
    rows = _authority_rows(db, user_id)
    assert rows["memberships"] == 1 and rows["bindings"] == 0 and rows["participations"] == 0, (
        kind,
        rows,
    )
    assert rows["workspaces_owned"] == 0

    # membership is not Session control: the governed transitions still deny
    def _begin(version: int) -> dict[str, Any]:
        return client.post(  # type: ignore[no-any-return]
            f"/workspaces/{w['ws']}/sessions/{w['session']}/transitions/begin-investigation",
            headers={"Idempotency-Key": str(uuid.uuid4())},
            json={"expectedVersion": version},
        ).json()

    begin = _begin(1)
    if begin["kind"] == "stale":  # F02's precedence for a member: version, then authority
        begin = _begin(int(begin["currentVersion"]))
    assert begin["kind"] == "denied", (kind, begin)


def test_founding_a_workspace_is_the_same_explicit_act_for_every_kind(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> None:
    """24 §20.3: identity creation is not governance bootstrap. Founding a
    Workspace (HARD-DEP-001 REC-001, F01) stays an explicit command of the
    identity, identical for a provider-created identity and a local one —
    never a side effect of the login."""
    outcomes: dict[str, Any] = {}
    for kind in ("local_password", "provider_created"):
        client, user_id = KINDS[kind](db, issuer, mail)
        assert _authority_rows(db, user_id)["workspaces_owned"] == 0, (
            kind
        )  # the login founded nothing
        founded = client.post(
            "/workspaces",
            headers={"Idempotency-Key": str(uuid.uuid4())},
            json={"name": f"W-{kind}"},
        )
        outcomes[kind] = (founded.status_code, founded.json()["kind"])
        assert _authority_rows(db, user_id)["workspaces_owned"] == (
            1 if founded.json()["kind"] in ("ok", "committed") else 0
        ), kind
    assert outcomes["provider_created"] == outcomes["local_password"], outcomes


def test_a_disabled_identity_has_no_principal_at_all(
    db: sa.Connection, issuer: LocalTestIssuer, mail: LocalMailCapture
) -> None:
    from application.account_disable import disable_identity_by_host_operator
    from application.identity_provisioning import HostOperator
    from security.events import Environment

    w = sweep._world(db)
    client, user_id = KINDS["local_password"](db, issuer, mail)
    owner = sweep._client(db, w["owner"])
    owner.post(
        f"/workspaces/{w['ws']}/members",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={"userId": user_id, "role": "Contributor"},
    )
    assert client.get(f"/workspaces/{w['ws']}").json()["kind"] == "ok"
    email = db.execute(
        sa.select(users_table.c.email).where(users_table.c.id == uuid.UUID(user_id))
    ).scalar_one()

    disable_identity_by_host_operator(
        db,
        email=email,
        operator=HostOperator(operator_id="otti@condyn.eu", os_user="codi", host="h"),
        reason="regression",
        environment=Environment.TEST,
        now=datetime.now(timezone.utc),
    )

    # authorization fails before business capability (24 §18.2): no principal, membership irrelevant
    assert client.get(f"/workspaces/{w['ws']}").status_code == 401
    assert client.get("/auth/me").status_code == 401
    assert (
        _authority_rows(db, user_id)["memberships"] == 1
    )  # the relation is preserved, not consulted
