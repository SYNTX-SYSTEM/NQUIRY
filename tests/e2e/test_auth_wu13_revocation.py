"""T13: revocation expansion (24 WU-AUTH-13; §14.6; §15.7; §18; §19.2–19.3;
§33.7; §36 #12; falsifiers 53, 76; §44.4).

MUST BECOME TRUE: an identity can unlink (revoke) one of its own
authentication methods; the method's sessions end with it, a provider login
through it is denied, the binding is kept as revoked evidence; account disable
exists as an explicit, audited effect that ends every session and blocks every
method; a terminal OIDC transaction never re-enters callback processing.

MUST REMAIN IMPOSSIBLE: unlinking the last ACTIVE method (24 §14.6, §36 #12
default); a revoked method continuing to log in; a disabled identity
authenticating, recovering or holding a session; a terminal transaction
reaching the token endpoint or returning to PENDING; account disable exposed
in a production-like runtime before its authority is decided (HA-AUTH-04).
"""

from __future__ import annotations

import io
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import application.http_revocation as http_revocation
import pytest
import sqlalchemy as sa
from application.account_disable import (
    AccountDisableRefused,
    disable_identity_by_host_operator,
    run_host_operator_disable,
)
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.identity_provisioning import HostOperator
from application.oidc_transactions import TransactionRejected, claim_transaction
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.oidc_transaction_repository import SqlAlchemyOidcTransactionRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.tables import (
    authentication_methods_table,
    external_provider_identities_table,
    local_auth_credentials_table,
    local_auth_sessions_table,
    recovery_challenges_table,
    security_events_table,
    users_table,
)
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.events import Environment
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.oidc_test_issuer import TEST_ISSUER, LocalTestIssuer
from security.oidc_transaction import (
    OidcFailureReason,
    OidcTransactionPurpose,
    OidcTransactionState,
    hash_protocol_value,
)
from security.provider_identity import ProviderIdentityConflict
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_OPERATOR = HostOperator(operator_id="otti@condyn.eu", os_user="codi", host="test-host")
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
}
_AUTHORITY_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "session_participations",
    "workspaces",
)
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
def client(
    db_connection: sa.Connection,
    monkeypatch: pytest.MonkeyPatch,
    issuer: LocalTestIssuer,
    mail: LocalMailCapture,
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (http_dispatch, http_oidc, http_email, http_recovery, http_revocation):
        monkeypatch.setattr(module, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer, mail_sink=mail))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


# ---------------------------------------------------------------- helpers


def _local_user(db: sa.Connection, *, verified: bool = False) -> tuple[UserId, str]:
    user_id = UserId(uuid.uuid4())
    email = f"{user_id.value}@example.test"
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="Revoker",
            record_version=1,
            created_at=_NOW,
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


def _bind_provider(db: sa.Connection, user_id: UserId, subject: str) -> uuid.UUID:
    method = SqlAlchemyAuthenticationMethodRepository(db).create(
        user_id=user_id,
        method_type=AuthenticationMethodType.TEST_PROVIDER,
        provenance_ref="test:wu-auth-13",
        now=_NOW,
    )
    SqlAlchemyProviderIdentityRepository(db).create(
        method_id=method.method_id,
        user_id=user_id,
        provider_issuer=TEST_ISSUER,
        provider_subject=subject,
        provider_email=None,
        provider_email_verified=False,
        provider_display_name=None,
        now=_NOW,
        provenance_ref="test:wu-auth-13",
    )
    return method.method_id.value


def _login(client: TestClient, email: str, password: str = _PASSWORD) -> int:
    return client.post("/auth/login", json={"email": email, "password": password}).status_code


def _provider_login(client: TestClient, issuer: LocalTestIssuer, subject: str):  # type: ignore[no-untyped-def]
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject=subject)
    response = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    )
    return response, params


def _link(client: TestClient, issuer: LocalTestIssuer, subject: str):  # type: ignore[no-untyped-def]
    start = client.post("/auth/oidc/test/link/start", params={"next": "/account/security"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject=subject)
    return client.get(
        "/auth/oidc/test/link/callback", params={"code": code, "state": params["state"]}
    )


def _unlink(client: TestClient, method_id: object):  # type: ignore[no-untyped-def]
    return client.post(f"/auth/methods/{method_id}/unlink")


def _methods(db: sa.Connection, user_id: UserId) -> dict[str, Any]:
    rows = db.execute(
        sa.select(authentication_methods_table).where(
            authentication_methods_table.c.user_id == user_id.value
        )
    ).mappings()
    return {str(row["id"]): dict(row) for row in rows}


def _sessions(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.user_id == user_id.value
            )
        ).mappings()
    )


def _events(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(security_events_table)
            .where(security_events_table.c.target_ref == f"user:{user_id.value}")
            .order_by(security_events_table.c.occurred_at)
        ).mappings()
    )


def _transaction(db: sa.Connection, state: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.text(
                "SELECT id, state, failure_reason, pkce_code_verifier "
                "FROM oidc_auth_transactions WHERE state_hash = :h"
            ),
            {"h": hash_protocol_value(state)},
        )
        .mappings()
        .one()
    )


def _authority_counts(db: sa.Connection) -> dict[str, int]:
    return {
        table: int(db.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one())
        for table in _AUTHORITY_TABLES
    }


def _user_row(db: sa.Connection, user_id: UserId) -> sa.RowMapping:
    return (
        db.execute(sa.select(users_table).where(users_table.c.id == user_id.value)).mappings().one()
    )


# ------------------------------------------------------------- unlink


def test_unlink_requires_a_session(client: TestClient) -> None:
    response = _unlink(client, uuid.uuid4())
    assert response.status_code == 401
    assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}


def test_unlinking_a_provider_method_revokes_it_its_sessions_and_its_login(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    method_id = _bind_provider(db_connection, user_id, "unlink-1")
    other = TestClient(app, follow_redirects=False)
    assert _provider_login(other, issuer, "unlink-1")[0].status_code == 303
    assert other.get("/auth/me").status_code == 200
    assert _login(client, email) == 200

    response = _unlink(client, method_id)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok" and body["methodId"] == str(method_id)
    assert body["sessionsRevoked"] == 1 and body["currentSessionEnded"] is False
    method = _methods(db_connection, user_id)[str(method_id)]
    assert method["status"] == "REVOKED" and method["revoked_at"] is not None
    binding = SqlAlchemyProviderIdentityRepository(db_connection).find(TEST_ISSUER, "unlink-1")
    assert binding is None  # no ACTIVE binding any more ...
    kept = db_connection.execute(
        sa.select(external_provider_identities_table.c.revoked_at).where(
            external_provider_identities_table.c.authentication_method_id == method_id
        )
    ).scalar_one()
    assert kept is not None  # ... the row stays as revoked evidence (24 §18.3)
    (provider_session,) = [s for s in _sessions(db_connection, user_id) if s["revoked_at"]]
    assert provider_session["revoked_reason"] == "METHOD_REVOKED"
    assert other.get("/auth/me").status_code == 401
    assert client.get("/auth/me").status_code == 200  # the local session survives
    listed = {m["methodId"]: m for m in client.get("/auth/methods").json()["methods"]}
    assert listed[str(method_id)]["status"] == "REVOKED"
    # provider login through the unlinked subject is denied, not re-created
    denied, params = _provider_login(other, issuer, "unlink-1")
    assert denied.headers["location"] == "/login?auth=failed"
    row = _transaction(db_connection, params["state"])
    assert row["state"] == "FAILED_TERMINAL"
    assert row["failure_reason"] == "AUTHENTICATION_METHOD_REVOKED"
    assert other.get("/auth/me").status_code == 401
    assert _user_row(db_connection, user_id)["disabled_at"] is None  # identity remains
    events = [
        e for e in _events(db_connection, user_id) if e["event_type"] == "AUTH_METHOD_UNLINKED"
    ]
    assert len(events) == 1 and '"sessionsRevoked": 1' in events[0]["observed_facts"]


def test_unlinking_the_method_of_the_current_session_ends_that_session(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, _ = _local_user(db_connection)
    method_id = _bind_provider(db_connection, user_id, "unlink-current")
    assert _provider_login(client, issuer, "unlink-current")[0].status_code == 303

    response = _unlink(client, method_id)

    assert response.status_code == 200
    assert response.json()["currentSessionEnded"] is True
    assert response.headers.get("set-cookie", "").startswith(f"{SESSION_COOKIE_NAME}=")
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert client.get("/auth/me").status_code == 401


def test_unlinking_the_local_password_method_denies_password_login_and_recovery(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    mail: LocalMailCapture,
) -> None:
    user_id, email = _local_user(db_connection, verified=True)
    _bind_provider(db_connection, user_id, "keep-provider")
    assert _login(client, email) == 200
    (local_method_id,) = [
        mid
        for mid, m in _methods(db_connection, user_id).items()
        if m["method_type"] == "LOCAL_PASSWORD"
    ]

    response = _unlink(client, local_method_id)

    assert response.status_code == 200 and response.json()["currentSessionEnded"] is True
    assert _login(client, email) == 401
    # the credential row is evidence, not a live method
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(local_auth_credentials_table)
            .where(local_auth_credentials_table.c.user_id == user_id.value)
        ).scalar_one()
        == 1
    )
    sent = len(mail.outbox)
    assert client.post("/auth/recovery/start", json={"email": email}).json() == {"kind": "ok"}
    assert len(mail.outbox) == sent  # no ACTIVE local method: nothing to recover
    assert _provider_login(client, issuer, "keep-provider")[0].status_code == 303
    assert client.get("/auth/me").status_code == 200


def test_the_last_active_method_cannot_be_unlinked(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """24 §14.6 / §36 #12: the default (impossible) is in force (HA-AUTH-03)."""
    user_id, email = _local_user(db_connection)
    second = _bind_provider(db_connection, user_id, "second")
    assert _login(client, email) == 200
    (local_method_id,) = [
        mid
        for mid, m in _methods(db_connection, user_id).items()
        if m["method_type"] == "LOCAL_PASSWORD"
    ]
    assert _unlink(client, second).status_code == 200

    response = _unlink(client, local_method_id)

    assert response.status_code == 409
    assert response.json() == {"kind": "denied", "reasonCode": "LAST_METHOD"}
    method = _methods(db_connection, user_id)[local_method_id]
    assert method["status"] == "ACTIVE" and method["revoked_at"] is None
    assert client.get("/auth/me").status_code == 200
    assert all(s["revoked_at"] is None for s in _sessions(db_connection, user_id))
    assert not [
        e
        for e in _events(db_connection, user_id)
        if e["event_type"] == "AUTH_METHOD_UNLINKED" and local_method_id in e["observed_facts"]
    ]


def test_foreign_unknown_and_revoked_methods_are_one_refusal(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    stranger, _ = _local_user(db_connection)
    foreign = _bind_provider(db_connection, stranger, "foreign")
    mine = _bind_provider(db_connection, user_id, "mine")
    assert _login(client, email) == 200
    assert _unlink(client, mine).status_code == 200

    answers = {
        name: _unlink(client, target)
        for name, target in (("foreign", foreign), ("unknown", uuid.uuid4()), ("revoked", mine))
    }

    for name, response in answers.items():
        assert response.status_code == 403, name
        assert response.json() == {"kind": "denied", "reasonCode": "UNLINK_DENIED"}, name
    assert _methods(db_connection, stranger)[str(foreign)]["status"] == "ACTIVE"
    assert _unlink(client, "not-a-uuid").status_code == 400
    assert _unlink(client, "not-a-uuid").json()["reasonCode"] == "MALFORMED_METHOD_ID"


def test_an_unlinked_subject_can_be_linked_again_as_a_new_method(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    user_id, email = _local_user(db_connection)
    first = _bind_provider(db_connection, user_id, "again")
    assert _login(client, email) == 200
    assert _unlink(client, first).status_code == 200

    response = _link(client, issuer, "again")

    assert response.headers["location"] == "/account/security?link=ok"
    methods = _methods(db_connection, user_id)
    provider_methods = [m for m in methods.values() if m["method_type"] == "TEST_PROVIDER"]
    assert sorted(m["status"] for m in provider_methods) == ["ACTIVE", "REVOKED"]
    bindings = (
        db_connection.execute(
            sa.select(external_provider_identities_table.c.revoked_at)
            .where(external_provider_identities_table.c.provider_subject == "again")
            .order_by(external_provider_identities_table.c.linked_at)
        )
        .scalars()
        .all()
    )
    assert sorted(b is None for b in bindings) == [False, True]  # one revoked, one active
    assert (
        _provider_login(TestClient(app, follow_redirects=False), issuer, "again")[0].headers[
            "location"
        ]
        == "/workspaces"
    )


def test_the_database_allows_one_active_binding_per_subject_only(
    db_connection: sa.Connection,
) -> None:
    user_id, _ = _local_user(db_connection)
    other, _ = _local_user(db_connection)
    _bind_provider(db_connection, user_id, "dup")
    with pytest.raises(ProviderIdentityConflict), db_connection.begin_nested():
        _bind_provider(db_connection, other, "dup")  # the adapter's typed refusal (WU-AUTH-08)


# ----------------------------------------------------------- account disable


def _disable(db: sa.Connection, email: str, **kw: Any):  # type: ignore[no-untyped-def]
    return disable_identity_by_host_operator(
        db,
        email=email,
        operator=kw.pop("operator", _OPERATOR),
        reason=kw.pop("reason", "compromised credential response"),
        environment=kw.pop("environment", Environment.TEST),
        now=kw.pop("now", datetime.now(timezone.utc)),
    )


def test_account_disable_ends_every_session_and_blocks_every_method(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    mail: LocalMailCapture,
) -> None:
    user_id, email = _local_user(db_connection, verified=True)
    _bind_provider(db_connection, user_id, "disabled-subject")
    other = TestClient(app, follow_redirects=False)
    assert _login(client, email) == 200
    assert _provider_login(other, issuer, "disabled-subject")[0].status_code == 303
    assert client.post("/auth/recovery/start", json={"email": email}).json() == {"kind": "ok"}
    open_recovery = mail.outbox[-1]
    authority_before = _authority_counts(db_connection)

    outcome = _disable(db_connection, email)

    assert outcome.user_id == user_id and outcome.sessions_revoked == 2
    row = _user_row(db_connection, user_id)
    assert row["disabled_at"] is not None and "otti@condyn.eu" in row["disabled_provenance"]
    assert all(
        s["revoked_at"] is not None and s["revoked_reason"] == "ACCOUNT_DISABLED"
        for s in _sessions(db_connection, user_id)
    )
    assert client.get("/auth/me").status_code == 401
    assert other.get("/auth/me").status_code == 401
    assert _login(client, email) == 401
    denied, params = _provider_login(other, issuer, "disabled-subject")
    assert denied.headers["location"] == "/login?auth=failed"
    assert _transaction(db_connection, params["state"])["failure_reason"] == "ACCOUNT_DISABLED"
    # methods are blocked, not rewritten (re-enable is 24 §36 #13 territory)
    assert all(m["status"] == "ACTIVE" for m in _methods(db_connection, user_id).values())
    # recovery: the open challenge is revoked, nothing new is issued
    assert (
        db_connection.execute(
            sa.select(recovery_challenges_table.c.revoked_at).where(
                recovery_challenges_table.c.id == uuid.UUID(open_recovery.challenge_id)
            )
        ).scalar_one()
        is not None
    )
    completion = client.post(
        "/auth/recovery/complete",
        json={
            "recoveryId": open_recovery.challenge_id,
            "token": open_recovery.token,
            "newPassword": "a brand new passphrase 2030",
        },
    )
    assert completion.status_code == 403
    sent = len(mail.outbox)
    assert client.post("/auth/recovery/start", json={"email": email}).json() == {"kind": "ok"}
    assert len(mail.outbox) == sent
    assert _login(client, email, "a brand new passphrase 2030") == 401
    event = [e for e in _events(db_connection, user_id) if e["event_type"] == "ACCOUNT_DISABLED"]
    assert len(event) == 1
    assert event[0]["actor_type"] == "HOST_OPERATOR" and event[0]["actor_id"] == "otti@condyn.eu"
    assert '"sessionsRevoked": 2' in event[0]["observed_facts"]
    assert _authority_counts(db_connection) == authority_before
    assert row["email"] == email  # the identity is not deleted (24 §18.3)


def test_no_session_can_be_issued_for_a_disabled_identity(
    db_connection: sa.Connection, client: TestClient
) -> None:
    """24 §33.7 "account disable during login": the database refuses the
    session row itself, so a login that verified its password before the
    disable committed still ends without a session."""
    user_id, email = _local_user(db_connection)
    _disable(db_connection, email)
    with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
        db_connection.execute(
            sa.insert(local_auth_sessions_table).values(
                id=uuid.uuid4(),
                user_id=user_id.value,
                session_token_hash="x" * 64,
                issued_at=_NOW,
                expires_at=_NOW + timedelta(hours=1),
                proof_provenance="test:wu-auth-13",
            )
        )
    assert "disabled" in str(refused.value)
    assert _sessions(db_connection, user_id) == []


def test_account_disable_is_one_way_at_the_database(
    db_connection: sa.Connection,
) -> None:
    user_id, email = _local_user(db_connection)
    _disable(db_connection, email)
    for assignment in ("disabled_at = NULL, disabled_provenance = NULL", "disabled_at = now()"):
        with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"UPDATE users SET {assignment} WHERE id = :id"), {"id": user_id.value}
            )
        assert "one-way" in str(refused.value), assignment
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.text("UPDATE users SET disabled_at = now() WHERE id = :id"),
            {"id": _local_user(db_connection)[0].value},
        )  # a disable without provenance is not a disable


def test_disable_refusals_write_nothing(db_connection: sa.Connection) -> None:
    user_id, email = _local_user(db_connection)
    before = len(_events(db_connection, user_id))
    cases: list[tuple[dict[str, Any], str]] = [
        ({"email": "nobody@example.test"}, "IDENTITY_UNKNOWN"),
        ({"email": email, "reason": "  "}, "REASON_REQUIRED"),
        (
            {"email": email, "operator": HostOperator(operator_id=" ", os_user="x", host="h")},
            "OPERATOR_REQUIRED",
        ),
        (
            {"email": email, "environment": Environment.PRODUCTION},
            "ACCOUNT_DISABLE_EXPOSURE_UNDECIDED",
        ),
        (
            {"email": email, "environment": Environment.STAGING},
            "ACCOUNT_DISABLE_EXPOSURE_UNDECIDED",
        ),
    ]
    for kwargs, code in cases:
        with pytest.raises(AccountDisableRefused) as refused, db_connection.begin_nested():
            _disable(db_connection, **kwargs)
        assert refused.value.reason_code == code, kwargs
    assert _user_row(db_connection, user_id)["disabled_at"] is None
    assert len(_events(db_connection, user_id)) == before
    _disable(db_connection, email)
    with pytest.raises(AccountDisableRefused) as again, db_connection.begin_nested():
        _disable(db_connection, email)
    assert again.value.reason_code == "ALREADY_DISABLED"


def test_the_operator_command_disables_under_a_declared_environment_only(
    db_connection: sa.Connection,
) -> None:
    from nquiry_api.operator import disable_identity

    user_id, email = _local_user(db_connection)

    @contextmanager
    def _connect() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    def run(environ: dict[str, str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        code = disable_identity.main(
            ["--email", email, "--operator", "otti@condyn.eu", "--reason", "device lost"],
            environ=environ,
            connect=_connect,
            stdout=out,
            stderr=err,
        )
        return code, out.getvalue(), err.getvalue()

    code, out, err = run({})
    assert code == 3 and "ENVIRONMENT_NOT_DECLARED" in err and out == ""
    code, out, err = run({"NQUIRY_ENVIRONMENT": "PRODUCTION"})
    assert code == 3 and "ACCOUNT_DISABLE_EXPOSURE_UNDECIDED" in err
    assert _user_row(db_connection, user_id)["disabled_at"] is None
    code, out, err = run({"NQUIRY_ENVIRONMENT": "TEST"})
    assert code == 0 and err == ""
    assert f'"userId": "{user_id.value}"' in out and '"environment": "TEST"' in out
    assert _user_row(db_connection, user_id)["disabled_at"] is not None
    assert run_host_operator_disable  # the module-level entry exists for the command


def test_no_http_route_disables_identities() -> None:
    assert not [
        r
        for r in app.routes
        if "disable" in getattr(r, "path", "")  # type: ignore[attr-defined]
    ]


# -------------------------------------------------- terminal transactions


@pytest.mark.parametrize(
    "terminal",
    [
        OidcTransactionState.PROCESSING,
        OidcTransactionState.COMPLETED,
        OidcTransactionState.FAILED_TERMINAL,
        OidcTransactionState.CANCELLED_TERMINAL,
        OidcTransactionState.EXPIRED,
    ],
)
def test_a_terminal_transaction_never_re_enters_callback_processing(
    db_connection: sa.Connection,
    client: TestClient,
    issuer: LocalTestIssuer,
    terminal: OidcTransactionState,
) -> None:
    """24 §18.2: no second entry into the token exchange, no return to
    PENDING, verifier unavailable, from every non-PENDING state."""
    start = client.get("/auth/oidc/test/start", params={"next": "/workspaces"})
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    row = _transaction(db_connection, params["state"])
    repository = SqlAlchemyOidcTransactionRepository(db_connection)
    now = datetime.now(timezone.utc)
    if terminal in (OidcTransactionState.PROCESSING, OidcTransactionState.COMPLETED):
        assert repository.claim(row["id"], now=now) is not None
        if terminal is OidcTransactionState.COMPLETED:
            assert repository.terminalize(
                row["id"],
                from_state=OidcTransactionState.PROCESSING,
                to_state=terminal,
                reason=None,
                now=now,
            )
    else:
        assert repository.terminalize(
            row["id"],
            from_state=OidcTransactionState.PENDING,
            to_state=terminal,
            reason=(
                None
                if terminal is OidcTransactionState.EXPIRED
                else OidcFailureReason.USER_CANCEL
                if terminal is OidcTransactionState.CANCELLED_TERMINAL
                else OidcFailureReason.PROVIDER_FAILURE
            ),
            now=now,
        )
    exchanges = len(issuer.exchanges)
    code = issuer.authorize(params, subject="terminal-subject")

    response = client.get(
        "/auth/oidc/test/callback", params={"code": code, "state": params["state"]}
    )

    assert response.status_code == 303 and response.headers["location"].startswith("/login?auth=")
    assert len(issuer.exchanges) == exchanges  # never reached the token endpoint
    after = _transaction(db_connection, params["state"])
    assert after["state"] == terminal.value
    assert after["pkce_code_verifier"] is None
    with pytest.raises(TransactionRejected):
        claim_transaction(
            repository,
            state=params["state"],
            binding_token=client.cookies.get("nquiry_oidc_binding"),
            purpose=OidcTransactionPurpose.LOGIN,
            initiating_user_id=None,
            now=now,
        )
    assert client.get("/auth/me").status_code == 401


# --------------------------------------------------------------- vocabulary


def test_revocation_reasons_and_method_states_are_closed() -> None:
    assert {s.value for s in AuthenticationMethodStatus} == {"ACTIVE", "REVOKED"}
    assert "ACCOUNT_DISABLED" in {r.value for r in OidcFailureReason}
