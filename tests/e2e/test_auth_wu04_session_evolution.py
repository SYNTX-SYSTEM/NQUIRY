"""T10: authenticated session evolution (24 WU-AUTH-04; §15; §18; §21.5;
FBR-AUTH-005, FBR-AUTH-017; falsifiers 32-35, 51, 62, 74-76, 105).

MUST BECOME TRUE: a session is traceable to its canonical user and to the
authentication method (or proof provenance) that produced it; it records its
revocation and why; a successful login creates a fresh session and sets the
cookie; revocation works at single-session, all-session, method and account
scope; a session can be rotated.

MUST REMAIN IMPOSSIBLE: a raw token in the database or in JSON; a revoked or
expired session resolving; a session surviving the revocation of its method;
a session being un-revoked, extended or moved to another user or method; a
login adopting or preserving a session identity the browser already carried;
one user's revocation touching another user's sessions; a session carrying or
granting authority.
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
from application.auth_handler import (
    SESSION_LIFETIME,
    SessionRequired,
    list_sessions,
    login,
    logout,
    logout_all_sessions,
    resolve_session,
    revoke_own_session,
    rotate_session,
)
from application.http_dispatch import SESSION_COOKIE_NAME
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.tables import local_auth_sessions_table, users_table
from security.local_auth import SessionRevocationReason, hash_password, hash_session_token
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_AUTHORITY_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "session_participations",
    "workspaces",
)


def _email() -> str:
    return f"wu04-{uuid.uuid4().hex}@example.test"


def _seed(db: sa.Connection, *, email: str) -> UserId:
    user_id = UserId(uuid.uuid4())
    db.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email,
            name="WU-AUTH-04",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id


def _sessions(db: sa.Connection) -> SqlAlchemyLocalSessionRepository:
    return SqlAlchemyLocalSessionRepository(db)


def _login(db: sa.Connection, email: str, *, now: datetime = _NOW) -> str:
    return login(
        email,
        _PASSWORD,
        credential_repository=SqlAlchemyLocalCredentialRepository(db),
        session_repository=_sessions(db),
        now=now,
    ).session_token


def _resolves(db: sa.Connection, token: str, *, now: datetime = _NOW) -> bool:
    return resolve_session(token, session_repository=_sessions(db), now=now) is not None


def _row(db: sa.Connection, token: str) -> Any:
    return (
        db.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.session_token_hash == hash_session_token(token)
            )
        )
        .mappings()
        .one()
    )


def _method_id(db: sa.Connection, user_id: UserId) -> Any:
    (method,) = SqlAlchemyAuthenticationMethodRepository(db).list_for_user(user_id)
    return method.method_id


def _refused(db: sa.Connection, statement: str, **params: object) -> str:
    with pytest.raises(sa.exc.DBAPIError) as refused, db.begin_nested():
        db.execute(sa.text(statement), params)
    return str(refused.value)


# ------------------------------------------------------------- traceability


def test_a_session_is_traceable_to_its_user_and_its_authentication_method(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    token = _login(db_connection, email)

    row = _row(db_connection, token)
    assert row["user_id"] == user_id.value
    assert row["authentication_method_id"] == _method_id(db_connection, user_id).value
    assert row["issued_at"] == _NOW and row["expires_at"] == _NOW + SESSION_LIFETIME
    assert row["revoked_at"] is None and row["revoked_reason"] is None
    record = _sessions(db_connection).get_by_token_hash(hash_session_token(token))
    assert record is not None and record.method_id == _method_id(db_connection, user_id)


def test_the_raw_token_is_not_stored_and_the_session_carries_no_authority_column(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    token = _login(db_connection, email)
    row = _row(db_connection, token)
    assert token not in " ".join(str(value) for value in row.values())
    assert set(row.keys()) == {
        "id",
        "user_id",
        "session_token_hash",
        "issued_at",
        "expires_at",
        "revoked_at",
        "authentication_method_id",
        "proof_provenance",
        "revoked_reason",
    }


def test_a_session_needs_a_method_or_an_explicit_proof_provenance(
    db_connection: sa.Connection,
) -> None:
    user_id = _seed(db_connection, email=_email())
    statement = (
        "INSERT INTO local_auth_sessions (id, user_id, session_token_hash, issued_at, "
        "expires_at, authentication_method_id, proof_provenance) "
        "VALUES (:id, :user_id, :hash, :at, :until, :method, :provenance)"
    )
    base = {"user_id": user_id.value, "at": _NOW, "until": _NOW + SESSION_LIFETIME}
    for provenance in (None, ""):
        _refused(
            db_connection,
            statement,
            **base,
            id=uuid.uuid4(),
            hash=uuid.uuid4().hex,
            method=None,
            provenance=provenance,
        )
    other = _seed(db_connection, email=_email())
    _refused(
        db_connection,
        statement,
        **base,
        id=uuid.uuid4(),
        hash=uuid.uuid4().hex,
        method=_method_id(db_connection, other).value,
        provenance=None,
    )
    db_connection.execute(
        sa.text(statement),
        {
            **base,
            "id": uuid.uuid4(),
            "hash": uuid.uuid4().hex,
            "method": None,
            "provenance": "test:explicit-proof",
        },
    )


# ------------------------------------------------------ database invariants


def test_a_session_cannot_be_unrevoked_extended_or_moved(db_connection: sa.Connection) -> None:
    email = _email()
    _seed(db_connection, email=email)
    other = _seed(db_connection, email=_email())
    token = _login(db_connection, email)
    session_id = _row(db_connection, token)["id"]

    for assignment in (
        "user_id = :other",
        "session_token_hash = 'rewritten'",
        "issued_at = issued_at + interval '1 hour'",
        "authentication_method_id = NULL, proof_provenance = 'rewritten'",
        "expires_at = expires_at + interval '1 second'",
    ):
        refusal = _refused(
            db_connection,
            f"UPDATE local_auth_sessions SET {assignment} WHERE id = :id",
            id=session_id,
            other=other.value,
        )
        assert "immutable" in refusal or "extended" in refusal, refusal

    logout(token, session_repository=_sessions(db_connection), now=_NOW + timedelta(minutes=5))
    for assignment in (
        "revoked_at = NULL, revoked_reason = NULL",
        "revoked_at = revoked_at + interval '1 hour'",
        "revoked_reason = 'ROTATED'",
    ):
        refusal = _refused(
            db_connection,
            f"UPDATE local_auth_sessions SET {assignment} WHERE id = :id",
            id=session_id,
        )
        assert "revoked" in refusal, refusal
    assert not _resolves(db_connection, token, now=_NOW + timedelta(minutes=6))


def test_revocation_always_carries_a_known_reason(db_connection: sa.Connection) -> None:
    email = _email()
    _seed(db_connection, email=email)
    token = _login(db_connection, email)
    session_id = _row(db_connection, token)["id"]
    for assignment in (
        "revoked_at = now()",
        "revoked_reason = 'LOGOUT'",
        "revoked_at = now(), revoked_reason = 'BECAUSE'",
    ):
        with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"UPDATE local_auth_sessions SET {assignment} WHERE id = :id"),
                {"id": session_id},
            )
    assert {reason.value for reason in SessionRevocationReason} == {
        "LOGOUT",
        "ALL_SESSIONS_LOGOUT",
        "SESSION_REVOKED",
        "METHOD_REVOKED",
        "ACCOUNT_DISABLED",
        "ROTATED",
    }


# ------------------------------------------------------- revocation scopes


def test_single_session_logout_records_its_reason_and_leaves_other_sessions(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    first, second = _login(db_connection, email), _login(db_connection, email)
    later = _NOW + timedelta(minutes=1)

    logout(first, session_repository=_sessions(db_connection), now=later)

    row = _row(db_connection, first)
    assert row["revoked_at"] == later and row["revoked_reason"] == "LOGOUT"
    assert not _resolves(db_connection, first, now=later)
    assert _resolves(db_connection, second, now=later)
    logout(first, session_repository=_sessions(db_connection), now=later + timedelta(hours=1))
    assert _row(db_connection, first)["revoked_at"] == later


def test_all_session_logout_revokes_every_session_of_the_user_and_no_one_elses(
    db_connection: sa.Connection,
) -> None:
    email, other_email = _email(), _email()
    _seed(db_connection, email=email)
    _seed(db_connection, email=other_email)
    tokens = [_login(db_connection, email) for _ in range(3)]
    other = _login(db_connection, other_email)
    later = _NOW + timedelta(minutes=1)

    revoked = logout_all_sessions(tokens[0], session_repository=_sessions(db_connection), now=later)

    assert revoked == 3
    assert not any(_resolves(db_connection, token, now=later) for token in tokens)
    assert {_row(db_connection, token)["revoked_reason"] for token in tokens} == {
        "ALL_SESSIONS_LOGOUT"
    }
    assert _resolves(db_connection, other, now=later)


def test_all_session_logout_requires_a_valid_session(db_connection: sa.Connection) -> None:
    email = _email()
    _seed(db_connection, email=email)
    live = _login(db_connection, email)
    dead = _login(db_connection, email)
    logout(dead, session_repository=_sessions(db_connection), now=_NOW)
    for token in (None, "garbage", dead):
        with pytest.raises(SessionRequired):
            logout_all_sessions(token, session_repository=_sessions(db_connection), now=_NOW)
    assert _resolves(db_connection, live)


def test_a_user_can_revoke_one_of_their_own_sessions_by_id(db_connection: sa.Connection) -> None:
    email = _email()
    _seed(db_connection, email=email)
    current, target = _login(db_connection, email), _login(db_connection, email)
    target_id = _row(db_connection, target)["id"]

    assert revoke_own_session(
        current, target_id, session_repository=_sessions(db_connection), now=_NOW
    )
    assert not _resolves(db_connection, target)
    assert _resolves(db_connection, current)
    assert _row(db_connection, target)["revoked_reason"] == "SESSION_REVOKED"
    assert not revoke_own_session(
        current, target_id, session_repository=_sessions(db_connection), now=_NOW
    )


def test_a_user_cannot_revoke_another_users_session(db_connection: sa.Connection) -> None:
    email, victim_email = _email(), _email()
    _seed(db_connection, email=email)
    _seed(db_connection, email=victim_email)
    attacker = _login(db_connection, email)
    victim = _login(db_connection, victim_email)
    victim_id = _row(db_connection, victim)["id"]

    assert not revoke_own_session(
        attacker, victim_id, session_repository=_sessions(db_connection), now=_NOW
    )
    assert _resolves(db_connection, victim)
    with pytest.raises(SessionRequired):
        revoke_own_session(None, victim_id, session_repository=_sessions(db_connection), now=_NOW)


def test_method_scope_revocation_revokes_only_that_methods_sessions(
    db_connection: sa.Connection,
) -> None:
    email, other_email = _email(), _email()
    user_id = _seed(db_connection, email=email)
    _seed(db_connection, email=other_email)
    tokens = [_login(db_connection, email) for _ in range(2)]
    other = _login(db_connection, other_email)
    later = _NOW + timedelta(minutes=1)

    revoked = _sessions(db_connection).revoke_for_method(
        _method_id(db_connection, user_id),
        revoked_at=later,
        reason=SessionRevocationReason.METHOD_REVOKED,
    )

    assert revoked == 2
    assert {_row(db_connection, token)["revoked_reason"] for token in tokens} == {"METHOD_REVOKED"}
    assert _resolves(db_connection, other, now=later)


def test_account_scope_revocation_revokes_every_session_of_the_user(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    tokens = [_login(db_connection, email) for _ in range(2)]
    revoked = _sessions(db_connection).revoke_all_for_user(
        user_id, revoked_at=_NOW, reason=SessionRevocationReason.ACCOUNT_DISABLED
    )
    assert revoked == 2
    assert {_row(db_connection, token)["revoked_reason"] for token in tokens} == {
        "ACCOUNT_DISABLED"
    }
    assert not any(_resolves(db_connection, token) for token in tokens)


def test_a_session_does_not_survive_the_revocation_of_its_method(
    db_connection: sa.Connection,
) -> None:
    """Even before any propagation writes `revoked_at` on the session rows, a
    session whose method is REVOKED resolves to no identity (falsifier 76)."""
    email = _email()
    user_id = _seed(db_connection, email=email)
    token = _login(db_connection, email)
    assert _resolves(db_connection, token)

    SqlAlchemyAuthenticationMethodRepository(db_connection).revoke(
        _method_id(db_connection, user_id), revoked_at=_NOW + timedelta(minutes=1)
    )

    assert _row(db_connection, token)["revoked_at"] is None
    assert not _resolves(db_connection, token, now=_NOW + timedelta(minutes=2))


def test_an_expired_session_does_not_resolve_and_is_not_listed(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    old = _login(db_connection, email)
    fresh = _login(db_connection, email, now=_NOW + timedelta(hours=6))
    after_expiry = _NOW + SESSION_LIFETIME
    assert not _resolves(db_connection, old, now=after_expiry)
    listed = list_sessions(fresh, session_repository=_sessions(db_connection), now=after_expiry)
    assert [item.session_id for item in listed] == [_row(db_connection, fresh)["id"]]


def test_listing_shows_only_the_users_own_live_sessions_and_marks_the_current_one(
    db_connection: sa.Connection,
) -> None:
    email, other_email = _email(), _email()
    _seed(db_connection, email=email)
    _seed(db_connection, email=other_email)
    current = _login(db_connection, email)
    second = _login(db_connection, email, now=_NOW + timedelta(minutes=1))
    gone = _login(db_connection, email)
    logout(gone, session_repository=_sessions(db_connection), now=_NOW)
    _login(db_connection, other_email)

    listed = list_sessions(
        current, session_repository=_sessions(db_connection), now=_NOW + timedelta(minutes=2)
    )

    assert {item.session_id for item in listed} == {
        _row(db_connection, current)["id"],
        _row(db_connection, second)["id"],
    }
    assert [item.current for item in listed] == [True, False]
    with pytest.raises(SessionRequired):
        list_sessions("garbage", session_repository=_sessions(db_connection), now=_NOW)


# ------------------------------------------------------------------ rotation


def test_rotation_replaces_the_token_and_the_old_token_stops_working(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    old = _login(db_connection, email)
    later = _NOW + timedelta(hours=1)

    rotated = rotate_session(old, session_repository=_sessions(db_connection), now=later)

    assert rotated.session_token != old and rotated.user_id == user_id
    assert not _resolves(db_connection, old, now=later)
    assert _resolves(db_connection, rotated.session_token, now=later)
    old_row, new_row = _row(db_connection, old), _row(db_connection, rotated.session_token)
    assert old_row["revoked_reason"] == "ROTATED" and old_row["revoked_at"] == later
    assert new_row["authentication_method_id"] == old_row["authentication_method_id"]
    assert new_row["issued_at"] == old_row["issued_at"]
    assert new_row["expires_at"] == old_row["expires_at"] == rotated.expires_at
    assert new_row["id"] != old_row["id"]


def test_a_dead_session_cannot_be_rotated_and_a_token_rotates_only_once(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    user_id = _seed(db_connection, email=email)
    token = _login(db_connection, email)
    rotate_session(token, session_repository=_sessions(db_connection), now=_NOW)
    for dead in (token, None, "garbage"):
        with pytest.raises(SessionRequired):
            rotate_session(dead, session_repository=_sessions(db_connection), now=_NOW)
    live = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(local_auth_sessions_table)
        .where(
            local_auth_sessions_table.c.user_id == user_id.value,
            local_auth_sessions_table.c.revoked_at.is_(None),
        )
    ).scalar_one()
    assert live == 1


def test_session_operations_create_no_authority(db_connection: sa.Connection) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    email = _email()
    _seed(db_connection, email=email)
    before = counts()
    token = _login(db_connection, email)
    rotated = rotate_session(token, session_repository=_sessions(db_connection), now=_NOW)
    logout_all_sessions(
        rotated.session_token, session_repository=_sessions(db_connection), now=_NOW
    )
    assert counts() == before


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


def _http_login(client: TestClient, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": _PASSWORD})
    assert response.status_code == 200
    return response.cookies[SESSION_COOKIE_NAME]


def test_login_replaces_a_planted_cookie_with_a_fresh_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Session fixation (24 §21.5, falsifier 105): whatever session cookie the
    browser carried before the login does not decide the identity after it."""
    victim_email, attacker_email = _email(), _email()
    victim = _seed(db_connection, email=victim_email)
    _seed(db_connection, email=attacker_email)
    attacker_token = _http_login(http_client, attacker_email)

    for planted in ("planted-by-an-attacker", attacker_token):
        http_client.cookies.clear()
        http_client.cookies.set(SESSION_COOKIE_NAME, planted)
        response = http_client.post(
            "/auth/login", json={"email": victim_email, "password": _PASSWORD}
        )
        issued = response.cookies[SESSION_COOKIE_NAME]
        assert issued != planted
        assert "httponly" in response.headers["set-cookie"].lower()
        me = http_client.get("/auth/me")
        assert me.json() == {"kind": "ok", "userId": str(victim.value)}
        assert issued not in response.text and planted not in response.text


def test_a_failed_login_leaves_the_browsers_cookie_untouched(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    response = http_client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert response.status_code == 401
    assert "set-cookie" not in {name.lower() for name in response.headers}


def test_two_logins_are_two_independent_sessions(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    first = _http_login(http_client, email)
    second = _http_login(http_client, email)
    assert first != second
    assert _row(db_connection, first)["id"] != _row(db_connection, second)["id"]


def test_http_logout_all_revokes_every_session_and_clears_the_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    first = _http_login(http_client, email)
    second = _http_login(http_client, email)

    response = http_client.post("/auth/logout-all")

    assert response.status_code == 200
    assert response.json() == {"kind": "ok", "revokedSessions": 2}
    assert SESSION_COOKIE_NAME in response.headers["set-cookie"]
    for token in (first, second):
        assert _row(db_connection, token)["revoked_reason"] == "ALL_SESSIONS_LOGOUT"
    http_client.cookies.set(SESSION_COOKIE_NAME, first)
    assert http_client.get("/auth/me").status_code == 401


def test_http_logout_all_without_a_session_is_denied_and_changes_nothing(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    token = _http_login(http_client, email)
    http_client.cookies.clear()
    response = http_client.post("/auth/logout-all")
    assert response.status_code == 401
    assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}
    assert _row(db_connection, token)["revoked_at"] is None


def test_http_session_list_and_revoke(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    other = _http_login(http_client, email)
    current = _http_login(http_client, email)
    other_id = str(_row(db_connection, other)["id"])

    listing = http_client.get("/auth/sessions")
    assert listing.status_code == 200
    body = listing.json()
    assert body["kind"] == "ok" and len(body["sessions"]) == 2
    assert {item["sessionId"] for item in body["sessions"]} >= {other_id}
    assert [item["current"] for item in body["sessions"]].count(True) == 1
    assert set(body["sessions"][0]) == {
        "sessionId",
        "issuedAt",
        "expiresAt",
        "current",
        "methodType",
    }
    assert {item["methodType"] for item in body["sessions"]} == {"LOCAL_PASSWORD"}
    assert other not in listing.text and current not in listing.text
    assert hash_session_token(current) not in listing.text

    revoked = http_client.post(f"/auth/sessions/{other_id}/revoke")
    assert revoked.status_code == 200 and revoked.json() == {"kind": "ok"}
    assert _row(db_connection, other)["revoked_reason"] == "SESSION_REVOKED"
    assert http_client.get("/auth/me").status_code == 200

    again = http_client.post(f"/auth/sessions/{other_id}/revoke")
    assert again.status_code == 404
    assert again.json() == {"kind": "denied", "reasonCode": "SESSION_NOT_FOUND"}
    malformed = http_client.post("/auth/sessions/not-a-uuid/revoke")
    assert malformed.status_code == 400
    assert malformed.json() == {"kind": "rejected", "reasonCode": "MALFORMED_SESSION_ID"}


def test_http_revoking_another_users_session_is_indistinguishable_from_unknown(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email, victim_email = _email(), _email()
    _seed(db_connection, email=email)
    _seed(db_connection, email=victim_email)
    victim = _http_login(http_client, victim_email)
    victim_id = str(_row(db_connection, victim)["id"])
    http_client.cookies.clear()
    _http_login(http_client, email)

    foreign = http_client.post(f"/auth/sessions/{victim_id}/revoke")
    unknown = http_client.post(f"/auth/sessions/{uuid.uuid4()}/revoke")

    assert foreign.status_code == unknown.status_code == 404
    assert foreign.json() == unknown.json()
    assert _row(db_connection, victim)["revoked_at"] is None


def test_http_session_routes_require_a_session(http_client: TestClient) -> None:
    for response in (
        http_client.get("/auth/sessions"),
        http_client.post(f"/auth/sessions/{uuid.uuid4()}/revoke"),
    ):
        assert response.status_code == 401
        assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}


def test_http_revoking_the_current_session_clears_the_cookie(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    email = _email()
    _seed(db_connection, email=email)
    current = _http_login(http_client, email)
    response = http_client.post(f"/auth/sessions/{_row(db_connection, current)['id']}/revoke")
    assert response.status_code == 200
    assert SESSION_COOKIE_NAME in response.headers["set-cookie"]
    http_client.cookies.set(SESSION_COOKIE_NAME, current)
    assert http_client.get("/auth/me").status_code == 401
