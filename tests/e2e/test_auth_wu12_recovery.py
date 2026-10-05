"""T10: recovery (24 WU-AUTH-12; §17; §19.6–19.7; §22.5; §33.7, §33.11;
§36 #11; §45.2, §45.13; FBR-AUTH-004; falsifiers 36, 38–40, 52, 54, 57).

MUST BECOME TRUE: password recovery uses an explicit, proof-bearing recovery
challenge delivered to a VERIFIED address of an identity that has a local
password method; a verified recovery proof authorizes exactly one credential
replacement, which revokes the identity's sessions; the recovery challenge is
never an authentication method.

MUST REMAIN IMPOSSIBLE: a reset by email string alone; a recovery request
committing any effect; replay of a recovery token; recovery through an
unverified address or for an identity without a local password; a recovery
creating a session; account existence disclosed by the request contact; a
recovery policy in force in a production-like runtime while 24 §36 #11 is
undecided.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import application.recovery as recovery
import pytest
import sqlalchemy as sa
from application.auth_runtime import (
    RecoveryPolicyForbidden,
    auth_runtime_from_environment,
)
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.recovery import MAX_FAILED_ATTEMPTS, RECOVERY_LIFETIME, RESEND_INTERVAL
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    local_auth_credentials_table,
    local_auth_sessions_table,
    recovery_challenges_table,
    security_events_table,
    users_table,
)
from security.local_auth import hash_password
from security.mail import LocalMailCapture
from security.recovery import RecoveryPolicy
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_NEW_PASSWORD = "a brand new passphrase 2030"
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
}
_INSERT_VERIFIED_EMAIL = sa.text(
    "INSERT INTO verified_emails"
    " (id, user_id, email, verified_at, verification_method, provenance_ref)"
    " VALUES (:id, :u, :e, :at, 'EMAIL_CHALLENGE', 'test')"
)
_AUTHORITY_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "session_participations",
    "workspaces",
)


@pytest.fixture
def mail() -> LocalMailCapture:
    return LocalMailCapture()


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, mail: LocalMailCapture
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse)
    monkeypatch.setattr(http_email, "connect", _reuse)
    monkeypatch.setattr(http_oidc, "connect", _reuse)
    monkeypatch.setattr(http_recovery, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(_ENV, mail_sink=mail))
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
            name="Recoverer",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def _login(client: TestClient, email: str, password: str = _PASSWORD) -> int:
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.status_code


def _verify(client: TestClient, mail: LocalMailCapture, email: str) -> None:
    challenge_id = client.post("/auth/email/verification/start", json={"email": email}).json()[
        "challengeId"
    ]
    assert (
        client.post(
            "/auth/email/verification/complete",
            json={"challengeId": challenge_id, "token": mail.outbox[-1].token},
        ).status_code
        == 200
    )


def _verified_local_user(
    db: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> tuple[UserId, str]:
    user_id, email = _local_user(db)
    assert _login(client, email) == 200
    _verify(client, mail, email)
    client.cookies.clear()
    return user_id, email


def _start(client: TestClient, email: str):  # type: ignore[no-untyped-def]
    return client.post("/auth/recovery/start", json={"email": email})


def _complete(client: TestClient, recovery_id: str, token: str, password: str = _NEW_PASSWORD):  # type: ignore[no-untyped-def]
    return client.post(
        "/auth/recovery/complete",
        json={"recoveryId": recovery_id, "token": token, "newPassword": password},
    )


def _challenges(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(recovery_challenges_table)
            .where(recovery_challenges_table.c.user_id == user_id.value)
            .order_by(recovery_challenges_table.c.issued_at)
        ).mappings()
    )


def _sessions(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(local_auth_sessions_table).where(
                local_auth_sessions_table.c.user_id == user_id.value
            )
        ).mappings()
    )


def _events(db: sa.Connection, user_id: UserId) -> list[str]:
    return list(
        db.execute(
            sa.select(security_events_table.c.event_type)
            .where(security_events_table.c.target_ref == f"user:{user_id.value}")
            .order_by(security_events_table.c.occurred_at)
        ).scalars()
    )


# ---------------------------------------------------------------- policy


def test_the_recovery_policy_defaults_to_denied_and_is_a_closed_vocabulary() -> None:
    assert {member.value for member in RecoveryPolicy} == {"DENIED", "VERIFIED_EMAIL_SELF_SERVICE"}
    assert (
        auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}).recovery_policy
        is RecoveryPolicy.DENIED
    )
    with pytest.raises(ValueError):
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_RECOVERY_POLICY": "anything"}
        )


def test_self_service_recovery_needs_a_declared_environment() -> None:
    """HD-AUTH-10 (2026-10-06): VERIFIED_EMAIL_SELF_SERVICE is part of the product in every
    declared environment (WU-AUTH-21 proves PRODUCTION / STAGING); undeclared is refused."""
    with pytest.raises(RecoveryPolicyForbidden):
        auth_runtime_from_environment({"NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE"})
    for environment in ("PRODUCTION", "STAGING"):
        runtime = auth_runtime_from_environment(
            {
                "NQUIRY_ENVIRONMENT": environment,
                "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
            }
        )
        assert runtime.recovery_policy.value == "VERIFIED_EMAIL_SELF_SERVICE"
        assert runtime.mail_sink is None  # policy without delivery: the contacts stay unavailable


def test_under_denied_the_contacts_are_unavailable_and_write_nothing(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    configure_auth_runtime(
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_EMAIL_DELIVERY_MODE": "capture"}, mail_sink=mail
        )
    )
    sent = len(mail.outbox)
    response = _start(client, email)
    assert response.status_code == 503
    assert response.json() == {"kind": "unavailable", "reasonCode": "RECOVERY_NOT_AVAILABLE"}
    assert _challenges(db_connection, user_id) == [] and len(mail.outbox) == sent
    assert _complete(client, str(uuid.uuid4()), "t").status_code == 503


# ------------------------------------------------------------- request path


def test_a_request_for_a_verified_local_identity_issues_a_challenge_and_commits_nothing_else(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    hash_before = db_connection.execute(
        sa.select(local_auth_credentials_table.c.password_hash).where(
            local_auth_credentials_table.c.user_id == user_id.value
        )
    ).scalar_one()

    response = _start(client, email.upper())

    assert response.status_code == 200 and response.json() == {"kind": "ok"}
    (challenge,) = _challenges(db_connection, user_id)
    assert challenge["recovery_type"] == "PASSWORD_RESET"
    assert challenge["verified_at"] is None and challenge["consumed_at"] is None
    assert challenge["expires_at"] == challenge["issued_at"] + RECOVERY_LIFETIME
    delivered = mail.outbox[-1]
    assert delivered.kind == "PASSWORD_RECOVERY" and delivered.to == email
    assert delivered.challenge_id == str(challenge["id"])
    assert delivered.token not in " ".join(str(v) for v in challenge.values())
    assert delivered.token not in response.text
    assert _events(db_connection, user_id)[-1] == "RECOVERY_ISSUED"
    # the request is not an effect (24 §17.5): credential and sessions unchanged
    hash_after = db_connection.execute(
        sa.select(local_auth_credentials_table.c.password_hash).where(
            local_auth_credentials_table.c.user_id == user_id.value
        )
    ).scalar_one()
    assert hash_after == hash_before
    assert _login(client, email) == 200


@pytest.mark.parametrize("case", ["unknown", "unverified", "provider_only", "malformed"])
def test_requests_that_cannot_recover_answer_identically_and_send_nothing(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture, case: str
) -> None:
    """24 §45.2 / falsifier 57: the request contact does not disclose whether
    an account exists, is verified or has a password."""
    if case == "unknown":
        email = f"{uuid.uuid4().hex}@example.test"
    elif case == "unverified":
        _, email = _local_user(db_connection)  # local password, address never verified
    elif case == "provider_only":
        user_id = UserId(uuid.uuid4())
        email = f"{user_id.value}@example.test"
        db_connection.execute(
            sa.insert(users_table).values(
                id=user_id.value,
                email=email,
                name="P",
                record_version=1,
                created_at=_NOW,
                updated_at=_NOW,
            )
        )
        db_connection.execute(
            _INSERT_VERIFIED_EMAIL,
            {"id": uuid.uuid4(), "u": user_id.value, "e": email, "at": _NOW},
        )
    else:
        email = "not an address"
    sent = len(mail.outbox)
    ok_user, ok_email = _verified_local_user(db_connection, client, mail)
    sent = len(mail.outbox)
    reference = _start(client, ok_email)
    response = _start(client, email)

    assert response.status_code == reference.status_code == 200
    assert response.json() == reference.json() == {"kind": "ok"}
    assert len(mail.outbox) == sent + 1  # only the reference request delivered
    assert (
        db_connection.execute(
            sa.select(sa.func.count()).select_from(recovery_challenges_table)
        ).scalar_one()
        == 1
    )
    assert ok_user


def test_repeated_requests_are_throttled_silently_and_supersede(
    db_connection: sa.Connection,
    client: TestClient,
    mail: LocalMailCapture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    assert _start(client, email).json() == {"kind": "ok"}
    first_token = mail.outbox[-1].token
    sent = len(mail.outbox)
    assert _start(client, email).json() == {
        "kind": "ok"
    }  # within the interval: same answer, no mail
    assert len(mail.outbox) == sent
    later = datetime.now(timezone.utc) + RESEND_INTERVAL + timedelta(seconds=1)
    monkeypatch.setattr(http_recovery, "_now", lambda: later)
    assert _start(client, email).json() == {"kind": "ok"}
    assert len(mail.outbox) == sent + 1
    first, second = _challenges(db_connection, user_id)
    assert first["revoked_at"] is not None and second["revoked_at"] is None
    assert _complete(client, str(first["id"]), first_token).status_code == 403


# ------------------------------------------------------------ completion


def test_the_correct_proof_replaces_the_credential_once_and_revokes_sessions(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    assert _login(client, email) == 200
    other = TestClient(app, follow_redirects=False)
    assert _login(other, email) == 200
    client.cookies.clear()
    # setup login (verification) + the two logins above: three live sessions
    live_before = [s for s in _sessions(db_connection, user_id) if s["revoked_at"] is None]
    assert len(live_before) == 3
    _start(client, email)
    delivered = mail.outbox[-1]

    response = _complete(client, delivered.challenge_id, delivered.token)

    assert response.status_code == 200 and response.json() == {"kind": "ok"}
    assert SESSION_COOKIE_NAME not in response.cookies  # recovery creates no session
    (challenge,) = _challenges(db_connection, user_id)
    assert challenge["verified_at"] is not None and challenge["consumed_at"] is not None
    assert all(
        s["revoked_at"] is not None and s["revoked_reason"] == "CREDENTIAL_RESET"
        for s in _sessions(db_connection, user_id)
    )  # every pre-reset session, none survives
    assert other.get("/auth/me").status_code == 401
    assert _login(client, email, _PASSWORD) == 401
    assert _login(client, email, _NEW_PASSWORD) == 200
    revoked = [
        s for s in _sessions(db_connection, user_id) if s["revoked_reason"] == "CREDENTIAL_RESET"
    ]
    assert len(revoked) == len(live_before)
    events = _events(db_connection, user_id)
    assert "RECOVERY_COMPLETED" in events and "PASSWORD_RESET" in events
    replay = _complete(client, delivered.challenge_id, delivered.token, "another passphrase 2031")
    assert replay.status_code == 403
    assert replay.json() == {"kind": "denied", "reasonCode": "RECOVERY_DENIED"}
    assert _login(client, email, _NEW_PASSWORD) == 200  # the replay changed nothing


def test_a_wrong_token_is_counted_and_the_challenge_is_spent_after_the_limit(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    _start(client, email)
    delivered = mail.outbox[-1]
    for attempt in range(1, MAX_FAILED_ATTEMPTS + 1):
        response = _complete(client, delivered.challenge_id, "not-the-token")
        assert response.status_code == 403 and response.json()["reasonCode"] == "RECOVERY_DENIED"
        assert _challenges(db_connection, user_id)[0]["failed_attempts"] == attempt
    assert _complete(client, delivered.challenge_id, delivered.token).status_code == 403
    assert _login(client, email, _PASSWORD) == 200
    assert "RECOVERY_FAILED" in _events(db_connection, user_id)


def test_an_expired_or_unknown_recovery_does_not_reset(
    db_connection: sa.Connection,
    client: TestClient,
    mail: LocalMailCapture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    _start(client, email)
    delivered = mail.outbox[-1]
    assert _complete(client, str(uuid.uuid4()), delivered.token).status_code == 403
    assert _complete(client, "not-a-uuid", delivered.token).json() == {
        "kind": "rejected",
        "reasonCode": "MALFORMED_RECOVERY_ID",
    }
    later = datetime.now(timezone.utc) + RECOVERY_LIFETIME + timedelta(seconds=1)
    monkeypatch.setattr(http_recovery, "_now", lambda: later)
    assert _complete(client, delivered.challenge_id, delivered.token).status_code == 403
    assert _login(client, email, _PASSWORD) == 200
    assert _login(client, email, _NEW_PASSWORD) == 401
    assert user_id


def test_a_weak_or_malformed_new_password_is_rejected_and_the_proof_is_kept(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    _start(client, email)
    delivered = mail.outbox[-1]
    for weak in ("short", " padded passphrase 2030 ", ""):
        response = _complete(client, delivered.challenge_id, delivered.token, weak)
        assert response.status_code == 400
        assert response.json() == {"kind": "rejected", "reasonCode": "PASSWORD_INVALID"}
    assert (
        _challenges(db_connection, user_id)[0]["consumed_at"] is None
    )  # not spent by a bad password
    assert _complete(client, delivered.challenge_id, delivered.token).status_code == 200


def test_recovery_challenges_are_not_authentication_methods(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    _start(client, email)
    assert _login(client, email) == 200
    methods = client.get("/auth/methods").json()["methods"]
    assert [m["methodType"] for m in methods] == ["LOCAL_PASSWORD"]
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.text(
                "INSERT INTO authentication_methods (id, user_id, method_type, status, created_at, "
                "provenance_ref) VALUES (:id, :u, 'RECOVERY_CHALLENGE', 'ACTIVE', :at, 'x')"
            ),
            {"id": uuid.uuid4(), "u": user_id.value, "at": _NOW},
        )


def test_recovery_creates_no_authority_and_no_session(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    user_id, email = _verified_local_user(db_connection, client, mail)
    before = counts()
    sessions_before = len(_sessions(db_connection, user_id))
    _start(client, email)
    delivered = mail.outbox[-1]
    assert _complete(client, delivered.challenge_id, delivered.token).status_code == 200
    assert counts() == before
    assert len(_sessions(db_connection, user_id)) == sessions_before
    assert client.get("/auth/me").status_code == 401


def test_the_database_refuses_reopening_or_rewriting_a_consumed_recovery(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _verified_local_user(db_connection, client, mail)
    _start(client, email)
    delivered = mail.outbox[-1]
    assert _complete(client, delivered.challenge_id, "not-the-token").status_code == 403
    # live challenge: the attempt count never decreases
    with pytest.raises(sa.exc.DBAPIError) as decreased, db_connection.begin_nested():
        db_connection.execute(
            sa.text("UPDATE recovery_challenges SET failed_attempts = 0 WHERE id = :id"),
            {"id": uuid.UUID(delivered.challenge_id)},
        )
    assert "never decreases" in str(decreased.value)
    assert _complete(client, delivered.challenge_id, delivered.token).status_code == 200
    for assignment in (
        "consumed_at = NULL",
        "verified_at = NULL",
        "challenge_hash = 'x'",
        "user_id = :other",
    ):
        with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"UPDATE recovery_challenges SET {assignment} WHERE id = :id"),
                {
                    "id": uuid.UUID(delivered.challenge_id),
                    "other": _local_user(db_connection)[0].value,
                },
            )
        assert "terminal" in str(refused.value) or "immutable" in str(refused.value), assignment
    assert user_id


def test_two_concurrent_completions_reset_once(
    db_connection: sa.Connection, mail: LocalMailCapture
) -> None:
    """24 §33.7: consumption is atomic; a consumed recovery token cannot be replayed."""
    engine = db_connection.engine
    created: UserId | None = None
    with engine.begin() as setup:
        user_id, email = _local_user(setup)
        created = user_id
        setup.execute(
            _INSERT_VERIFIED_EMAIL,
            {"id": uuid.uuid4(), "u": user_id.value, "e": email, "at": _NOW},
        )
        issued = recovery.request_recovery(
            setup, email=email, now=_NOW, environment="TEST", mail_sink=mail
        )
        assert issued is not None
    token = mail.outbox[-1].token
    first, second = engine.connect(), engine.connect()
    try:
        first_tx = first.begin()
        recovery.complete_recovery(
            first,
            recovery_id=issued.recovery_id,
            token=token,
            new_password=_NEW_PASSWORD,
            now=_NOW + timedelta(minutes=1),
            environment="TEST",
        )
        second_tx = second.begin()
        second.execute(sa.text("SET LOCAL lock_timeout = '300ms'"))
        with pytest.raises((sa.exc.OperationalError, recovery.RecoveryDenied)):
            recovery.complete_recovery(
                second,
                recovery_id=issued.recovery_id,
                token=token,
                new_password="another passphrase 2031",
                now=_NOW + timedelta(minutes=1),
                environment="TEST",
            )
        second_tx.rollback()
        first_tx.commit()
        second_tx = second.begin()
        with pytest.raises(recovery.RecoveryDenied):
            recovery.complete_recovery(
                second,
                recovery_id=issued.recovery_id,
                token=token,
                new_password="another passphrase 2031",
                now=_NOW + timedelta(minutes=2),
                environment="TEST",
            )
        second_tx.rollback()
        with engine.connect() as check:
            stored = check.execute(
                sa.text("SELECT password_hash FROM local_auth_credentials WHERE user_id = :u"),
                {"u": user_id.value},
            ).scalar_one()
        from security.local_auth import verify_password

        assert verify_password(_NEW_PASSWORD, stored)
    finally:
        first.close()
        second.close()
        if created is not None:
            with engine.begin() as cleanup:
                for statement in (
                    "DELETE FROM recovery_challenges WHERE user_id = :u",
                    "DELETE FROM verified_emails WHERE user_id = :u",
                    "DELETE FROM local_auth_sessions WHERE user_id = :u",
                    "DELETE FROM local_auth_credentials WHERE user_id = :u",
                    "DELETE FROM authentication_methods WHERE user_id = :u",
                    "DELETE FROM users WHERE id = :u",
                ):
                    cleanup.execute(sa.text(statement), {"u": created.value})
