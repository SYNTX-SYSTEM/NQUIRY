"""WU-AUTH-19: credential rotation by the authenticated identity (24 §9.2
"credential rotation", §17.1 "replace password credential after proof").

MUST BECOME TRUE: a live local session proves the current password and
replaces it; the old password stops working and the new one works; every
OTHER session of the identity ends with CREDENTIAL_RESET while the proving
session continues; the LOCAL_PASSWORD method is unchanged; PASSWORD_CHANGED
is audited with ids only.

MUST REMAIN IMPOSSIBLE: rotation without a session; with a wrong current
password (audited, session kept, hash kept); an invalid or unchanged new
password; rotation for an identity without a local credential (a bootstrapped
provider identity); any password, token or address in an event.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import parse_qs, urlparse

import application.http_credential as http_credential
import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import (
    authentication_methods_table,
    local_auth_credentials_table,
    local_auth_sessions_table,
    security_events_table,
)
from security.oidc_test_issuer import LocalTestIssuer
from test_auth_wu10_account_linking import _PASSWORD, _local_user, _login

_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_AUTH_PROVIDER_MODE": "test",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
}
_NEW = "a brand new passphrase 42"
_BASELINE: set[object] = set()


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

    for module in (http_dispatch, http_oidc, http_credential):
        monkeypatch.setattr(module, "connect", _reuse)
    _BASELINE.clear()
    _BASELINE.update(db_connection.execute(sa.select(security_events_table.c.id)).scalars())
    configure_auth_runtime(auth_runtime_from_environment(_ENV, test_issuer=issuer))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _change(client: TestClient, current: str, new: str):  # type: ignore[no-untyped-def]
    return client.post(
        "/auth/password/change", json={"currentPassword": current, "newPassword": new}
    )


def _events(db: sa.Connection, event_type: str) -> list[sa.RowMapping]:
    rows = db.execute(
        sa.select(security_events_table).where(security_events_table.c.event_type == event_type)
    ).mappings()
    return [r for r in rows if r["id"] not in _BASELINE]


def _hash(db: sa.Connection, user_id: object) -> str:
    return str(
        db.execute(
            sa.select(local_auth_credentials_table.c.password_hash).where(
                local_auth_credentials_table.c.user_id == user_id
            )
        ).scalar_one()
    )


def test_rotation_replaces_the_credential_keeps_the_proving_session_and_ends_the_others(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    other = TestClient(app, follow_redirects=False)
    other_token = _login(other, email)
    token = _login(client, email)
    before = _hash(db_connection, user_id.value)
    method_before = (
        db_connection.execute(
            sa.select(authentication_methods_table).where(
                authentication_methods_table.c.user_id == user_id.value
            )
        )
        .mappings()
        .one()
    )

    response = _change(client, _PASSWORD, _NEW)
    assert response.status_code == 200
    assert response.json() == {"kind": "ok", "sessionsRevoked": 1}
    assert SESSION_COOKIE_NAME not in response.headers.get("set-cookie", "")
    # the proving session continues; the other one ended with the credential
    assert client.get("/auth/me").json() == {"kind": "ok", "userId": str(user_id.value)}
    other.cookies.set(SESSION_COOKIE_NAME, other_token)
    assert other.get("/auth/me").status_code == 401
    reasons = (
        db_connection.execute(
            sa.select(local_auth_sessions_table.c.revoked_reason).where(
                local_auth_sessions_table.c.user_id == user_id.value,
                local_auth_sessions_table.c.revoked_at.is_not(None),
            )
        )
        .scalars()
        .all()
    )
    assert reasons == ["CREDENTIAL_RESET"]
    # the hash moved, the method did not
    assert _hash(db_connection, user_id.value) != before
    method_after = (
        db_connection.execute(
            sa.select(authentication_methods_table).where(
                authentication_methods_table.c.user_id == user_id.value
            )
        )
        .mappings()
        .one()
    )
    assert dict(method_after) == dict(method_before)
    # old password refused, new one works
    fresh = TestClient(app, follow_redirects=False)
    assert (
        fresh.post("/auth/login", json={"email": email, "password": _PASSWORD}).status_code == 401
    )
    assert fresh.post("/auth/login", json={"email": email, "password": _NEW}).status_code == 200
    # audit: ids and classes only
    changed = _events(db_connection, "PASSWORD_CHANGED")
    assert len(changed) == 1 and changed[0]["actor_id"] == str(user_id.value)
    facts = json.loads(changed[0]["observed_facts"])
    assert set(facts) == {"method", "methodId", "sessionsRevoked", "session"}
    assert facts["methodId"] == str(method_before["id"]) and facts["sessionsRevoked"] == 1
    blob = " ".join(str(v) for r in _events(db_connection, "PASSWORD_CHANGED") for v in r.values())
    for secret in (_PASSWORD, _NEW, token, other_token, email):
        assert secret not in blob


def test_a_wrong_current_password_is_refused_audited_and_changes_nothing(
    db_connection: sa.Connection, client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    before = _hash(db_connection, user_id.value)
    response = _change(client, "not the password", _NEW)
    assert response.status_code == 403
    assert response.json() == {"kind": "denied", "reasonCode": "CURRENT_PASSWORD_INVALID"}
    assert _hash(db_connection, user_id.value) == before
    assert client.get("/auth/me").status_code == 200  # the session is kept
    failed = _events(db_connection, "PASSWORD_CHANGE_FAILED")
    assert len(failed) == 1 and json.loads(failed[0]["observed_facts"]) == {
        "reason": "CURRENT_PASSWORD_INVALID"
    }
    assert "not the password" not in str(failed[0]["observed_facts"])
    assert _events(db_connection, "PASSWORD_CHANGED") == []
    # an empty current password is the same refusal
    assert _change(client, "   ", _NEW).status_code == 403


@pytest.mark.parametrize("new", ["short", " padded passphrase ", "", _PASSWORD, "x" * 1025])
def test_an_invalid_or_unchanged_new_password_is_rejected_before_any_effect(
    db_connection: sa.Connection, client: TestClient, new: str
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    before = _hash(db_connection, user_id.value)
    response = _change(client, _PASSWORD, new)
    assert response.status_code == 400
    assert response.json() == {"kind": "rejected", "reasonCode": "PASSWORD_INVALID"}
    assert _hash(db_connection, user_id.value) == before
    assert _events(db_connection, "PASSWORD_CHANGED") == []


def test_no_session_means_no_rotation_and_no_event(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _local_user(db_connection)
    response = _change(client, _PASSWORD, _NEW)
    assert response.status_code == 401 and response.json()["reasonCode"] == "NO_SESSION"
    assert _events(db_connection, "PASSWORD_CHANGED") == []
    assert _events(db_connection, "PASSWORD_CHANGE_FAILED") == []


def test_a_provider_bootstrapped_identity_has_no_local_credential_to_rotate(
    db_connection: sa.Connection, client: TestClient, issuer: LocalTestIssuer
) -> None:
    start = client.get("/auth/oidc/test/start")
    params = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    code = issuer.authorize(params, subject="rotation-newcomer", email="newcomer@provider.test")
    done = client.get("/auth/oidc/test/callback", params={"code": code, "state": params["state"]})
    assert done.status_code == 303 and SESSION_COOKIE_NAME in done.cookies
    response = _change(client, "anything", _NEW)
    assert response.status_code == 403
    assert response.json() == {"kind": "denied", "reasonCode": "NO_LOCAL_CREDENTIAL"}
    assert client.get("/auth/me").status_code == 200
