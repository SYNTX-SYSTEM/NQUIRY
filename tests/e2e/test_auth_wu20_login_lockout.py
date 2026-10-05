"""WU-AUTH-20: the login lockout boundary (24 §21.16 "IP/user/email-keyed rate
limits, lockout policy, audit"; §22.3 "credential validity requires … no
active lockout/rate-limit boundary"; §9.2 "rate limiting" for an official
password method).

MUST BECOME TRUE: after the CREDENTIAL threshold of failures inside the
window the typed address is locked for the lock duration — the right password
is refused too (429 RATE_LIMITED, no session), the refusal is audited (class
only) and does not extend the lock; the window expires and the lock ends;
a success clears the address's window; the CLIENT key locks a client after
ten times the failures across any addresses; an address that names no account
behaves exactly like one that does (no enumeration); the table carries
digests only; the policy is configurable and refuses nonsense.

MUST REMAIN IMPOSSIBLE: a locked address logging in with the right password;
a lock extended by hammering; an address or identity in `auth_rate_limits`;
a lockout event naming an account.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import application.http_dispatch as http_dispatch
import application.http_oidc as http_oidc
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.login_throttle import LoginThrottle
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import auth_rate_limits_table, security_events_table
from security.login_throttle import (
    ThrottleKeyKind,
    ThrottlePolicy,
    ThrottleWindow,
    next_window,
    throttle_key,
)
from test_auth_wu10_account_linking import _PASSWORD, _local_user

_ENV = {"NQUIRY_ENVIRONMENT": "TEST"}
_T0 = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def client(db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV))
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _attempt(client: TestClient, email: str, password: str, forwarded: str | None = None):  # type: ignore[no-untyped-def]
    headers = {"X-Forwarded-For": forwarded} if forwarded else {}
    return client.post("/auth/login", json={"email": email, "password": password}, headers=headers)


def _window(db: sa.Connection, kind: ThrottleKeyKind, value: str) -> sa.RowMapping | None:
    return (
        db.execute(
            sa.select(auth_rate_limits_table).where(
                auth_rate_limits_table.c.key_kind == kind.value,
                auth_rate_limits_table.c.key_hash == throttle_key(kind, value),
            )
        )
        .mappings()
        .one_or_none()
    )


# --- the pure policy ---------------------------------------------------------------------


def test_the_window_arithmetic_locks_at_the_threshold_and_never_extends_a_lock() -> None:
    policy = ThrottlePolicy(
        credential_failures=3, window=timedelta(minutes=10), lock=timedelta(minutes=10)
    )
    kind, key = ThrottleKeyKind.CREDENTIAL, throttle_key(ThrottleKeyKind.CREDENTIAL, " A@B.test ")
    assert key == throttle_key(kind, "a@b.test")  # normalized: one key however typed
    w = None
    for i in range(1, 3):
        w = next_window(w, kind=kind, key_hash=key, now=_T0 + timedelta(seconds=i), policy=policy)
        assert w.failures == i and w.locked_until is None
    w = next_window(w, kind=kind, key_hash=key, now=_T0 + timedelta(seconds=3), policy=policy)
    assert w.failures == 3 and w.locked_until == _T0 + timedelta(seconds=3, minutes=10)
    # hammering while locked counts but does not move the lock
    later = next_window(w, kind=kind, key_hash=key, now=_T0 + timedelta(minutes=5), policy=policy)
    assert later.failures == 4 and later.locked_until == w.locked_until
    # a failure after the window elapsed starts a fresh window of one
    fresh = next_window(w, kind=kind, key_hash=key, now=_T0 + timedelta(minutes=11), policy=policy)
    assert fresh.failures == 1 and fresh.window_started_at == _T0 + timedelta(minutes=11)
    assert policy.threshold(ThrottleKeyKind.CLIENT) == 30
    assert not ThrottleWindow(kind, key, _T0, 9, _T0 + timedelta(minutes=1)).locked(
        _T0 + timedelta(minutes=2)
    )


def test_the_policy_is_configurable_and_refuses_nonsense() -> None:
    runtime = auth_runtime_from_environment(
        {"NQUIRY_LOGIN_LOCKOUT_FAILURES": "3", "NQUIRY_LOGIN_LOCKOUT_MINUTES": "2"}
    )
    assert runtime.login_throttle.credential_failures == 3
    assert runtime.login_throttle.window == timedelta(minutes=2) == runtime.login_throttle.lock
    assert auth_runtime_from_environment({}).login_throttle == ThrottlePolicy()
    for bad in (
        {"NQUIRY_LOGIN_LOCKOUT_FAILURES": "0"},
        {"NQUIRY_LOGIN_LOCKOUT_MINUTES": "x"},
        {"NQUIRY_LOGIN_LOCKOUT_FAILURES": "-1"},
    ):
        with pytest.raises(ValueError):
            auth_runtime_from_environment(bad)


# --- the boundary at the contact ---------------------------------------------------------


def test_five_failures_lock_the_address_the_right_password_is_refused_and_the_lock_is_audited(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, email = _local_user(db_connection)
    for _ in range(4):
        assert _attempt(client, email, "wrong").status_code == 401
    fifth = _attempt(client, email, "wrong")
    assert fifth.status_code == 401  # the fifth failure locks; it is itself still a plain failure
    locked = _attempt(client, email, _PASSWORD)
    assert locked.status_code == 429
    assert locked.json() == {"kind": "denied", "reasonCode": "RATE_LIMITED"}
    assert SESSION_COOKIE_NAME not in locked.cookies
    row = _window(db_connection, ThrottleKeyKind.CREDENTIAL, email)
    assert row is not None and row["failures"] == 5 and row["locked_until"] is not None
    locked_until = row["locked_until"]
    # a refused attempt neither counts nor extends the lock
    assert _attempt(client, email, "wrong").status_code == 429
    row = _window(db_connection, ThrottleKeyKind.CREDENTIAL, email)
    assert row["failures"] == 5 and row["locked_until"] == locked_until  # type: ignore[index]
    events = (
        db_connection.execute(
            sa.select(security_events_table).where(
                security_events_table.c.event_type == "LOGIN_RATE_LIMITED"
            )
        )
        .mappings()
        .all()
    )
    assert len(events) >= 2
    for event in events:
        assert event["actor_type"] == "UNAUTHENTICATED_CLIENT" and event["target_ref"] is None
        assert json.loads(event["observed_facts"]) == {
            "method": "LOCAL_PASSWORD",
            "boundary": "LOCKOUT",
        }
    # the table and the events carry no address and no identity
    blob = " ".join(
        str(v)
        for r in db_connection.execute(sa.select(auth_rate_limits_table)).mappings()
        for v in r.values()
    )
    assert email not in blob and "@" not in blob
    assert email not in " ".join(str(e["observed_facts"]) for e in events)


def test_the_lock_ends_with_the_window_and_a_success_clears_the_address(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, email = _local_user(db_connection)
    throttle = LoginThrottle(db_connection, policy=ThrottlePolicy())
    for i in range(5):
        throttle.failed(email, "10.0.0.9", now=_T0 + timedelta(seconds=i))
    assert throttle.locked(email, "10.0.0.9", now=_T0 + timedelta(minutes=14))
    assert not throttle.locked(email, "10.0.0.9", now=_T0 + timedelta(minutes=16))
    throttle.succeeded(email, now=_T0 + timedelta(minutes=16))
    row = _window(db_connection, ThrottleKeyKind.CREDENTIAL, email)
    assert row is not None and row["failures"] == 0 and row["locked_until"] is None
    # live: four failures then the right password → success, and the window is clear again
    for _ in range(4):
        _attempt(client, email, "wrong")
    assert _attempt(client, email, _PASSWORD).status_code == 200
    row = _window(db_connection, ThrottleKeyKind.CREDENTIAL, email)
    assert row is not None and row["failures"] == 0


def test_an_unknown_address_is_locked_exactly_like_a_known_one(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, known = _local_user(db_connection)
    unknown = "nobody-here@example.test"
    for _ in range(5):
        assert _attempt(client, known, "wrong").status_code == 401
        assert _attempt(client, unknown, "wrong").status_code == 401
    known_locked, unknown_locked = (
        _attempt(client, known, "wrong"),
        _attempt(client, unknown, "wrong"),
    )
    assert known_locked.status_code == unknown_locked.status_code == 429
    assert known_locked.json() == unknown_locked.json()
    assert _window(db_connection, ThrottleKeyKind.CREDENTIAL, unknown) is not None


def test_a_client_is_locked_after_ten_times_the_failures_across_addresses(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, email = _local_user(db_connection)
    attacker = "203.0.113.7"
    for i in range(50):
        assert (
            _attempt(client, f"guess-{i}@example.test", "wrong", forwarded=attacker).status_code
            == 401
        )
    # the 51st attempt from that client is refused whatever the address — even the right password
    assert _attempt(client, email, _PASSWORD, forwarded=attacker).status_code == 429
    # another client with the right password still logs in: the lock is the client's
    assert _attempt(client, email, _PASSWORD, forwarded="198.51.100.4").status_code == 200
    row = _window(db_connection, ThrottleKeyKind.CLIENT, attacker)
    assert row is not None and row["failures"] == 50 and row["locked_until"] is not None
    assert attacker not in " ".join(str(v) for v in row.values())
