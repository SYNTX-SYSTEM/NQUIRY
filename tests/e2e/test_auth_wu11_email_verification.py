"""T10: email verification (24 WU-AUTH-11; §13.9; §16.1; §19.4; §22.2–22.3;
§25.3; §33.11; §36 #16; §42; FBR-AUTH-003; falsifiers 37, 43).

MUST BECOME TRUE: email verification has a challenge state and a commit; a
verified email is a persisted relation created only after correct challenge
proof; delivery goes through a port whose local implementation captures
mail deterministically (no production mail provider in proof).

MUST REMAIN IMPOSSIBLE: email delivery counting as verification; a verified
relation before proof; a wrong, expired, consumed or foreign-identity token
verifying; a raw token stored, logged into a SecurityEvent or returned by
the API; verification changing identity, membership, role or session
authority; production delivery being chosen by the implementation.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import application.email_verification as email_verification
import application.http_dispatch as http_dispatch
import application.http_email as http_email
import pytest
import sqlalchemy as sa
from application.auth_runtime import (
    MailDeliveryForbidden,
    auth_runtime_from_environment,
)
from application.email_verification import (
    CHALLENGE_LIFETIME,
    MAX_FAILED_ATTEMPTS,
    RESEND_INTERVAL,
)
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    auth_challenges_table,
    security_events_table,
    users_table,
    verified_emails_table,
)
from security.auth_audit import AuthAuditEvent
from security.local_auth import hash_password
from security.mail import CapturedMail, LocalMailCapture
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PASSWORD = "correct horse battery staple"
_ENV = {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_EMAIL_DELIVERY_MODE": "capture"}
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
            name="Verifier",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db).create(
        user_id=user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return user_id, email


def _login(client: TestClient, email: str) -> None:
    assert (
        client.post("/auth/login", json={"email": email, "password": _PASSWORD}).status_code == 200
    )


def _start(client: TestClient, email: str):  # type: ignore[no-untyped-def]
    return client.post("/auth/email/verification/start", json={"email": email})


def _complete(client: TestClient, challenge_id: str, token: str):  # type: ignore[no-untyped-def]
    return client.post(
        "/auth/email/verification/complete", json={"challengeId": challenge_id, "token": token}
    )


def _challenge(db: sa.Connection, challenge_id: str) -> sa.RowMapping:
    return (
        db.execute(
            sa.select(auth_challenges_table).where(
                auth_challenges_table.c.id == uuid.UUID(challenge_id)
            )
        )
        .mappings()
        .one()
    )


def _verified(db: sa.Connection, user_id: UserId) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(verified_emails_table)
            .where(verified_emails_table.c.user_id == user_id.value)
            .order_by(verified_emails_table.c.verified_at)
        ).mappings()
    )


def _events(db: sa.Connection, user_id: UserId) -> list[str]:
    """The verification relation's own events; the session events of WU-AUTH-18
    (LOGIN_SUCCEEDED, LOGOUT, …) belong to another relation and are left out."""
    return [
        event_type
        for event_type in db.execute(
            sa.select(security_events_table.c.event_type)
            .where(security_events_table.c.target_ref == f"user:{user_id.value}")
            .order_by(security_events_table.c.occurred_at)
        ).scalars()
        if event_type not in {e.value for e in AuthAuditEvent}
    ]


# ------------------------------------------------------------- delivery port


def test_delivery_is_a_port_and_only_capture_is_materialized() -> None:
    assert auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}).mail_sink is None
    runtime = auth_runtime_from_environment(_ENV)
    assert isinstance(runtime.mail_sink, LocalMailCapture)
    with pytest.raises(ValueError):
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_EMAIL_DELIVERY_MODE": "smtp"}
        )


@pytest.mark.parametrize("environment", ["PRODUCTION", "STAGING", None])
def test_capture_delivery_is_refused_outside_development_and_test(environment: str | None) -> None:
    env = {"NQUIRY_EMAIL_DELIVERY_MODE": "capture"}
    if environment is not None:
        env["NQUIRY_ENVIRONMENT"] = environment
    with pytest.raises(MailDeliveryForbidden):
        auth_runtime_from_environment(env)


def test_without_delivery_verification_is_unavailable(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    configure_auth_runtime(auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}))
    response = _start(client, email)
    assert response.status_code == 503
    assert response.json() == {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_NOT_CONFIGURED"}
    assert (
        db_connection.execute(
            sa.select(sa.func.count()).select_from(auth_challenges_table)
        ).scalar_one()
        == 0
    )


# ---------------------------------------------------------- issue and commit


def test_start_issues_a_challenge_delivers_it_and_stores_only_the_hash(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)

    response = _start(client, email)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok" and set(body) == {"kind", "challengeId", "expiresAt"}
    (delivered,) = mail.outbox
    assert isinstance(delivered, CapturedMail)
    assert delivered.to == email and delivered.challenge_id == body["challengeId"]
    assert len(delivered.token) >= 43
    row = _challenge(db_connection, body["challengeId"])
    assert row["challenge_type"] == "EMAIL_VERIFICATION"
    assert row["user_id"] == user_id.value and row["email"] == email
    assert row["consumed_at"] is None and row["failed_attempts"] == 0
    assert row["expires_at"] == row["issued_at"] + CHALLENGE_LIFETIME
    assert delivered.token not in " ".join(str(v) for v in row.values())
    assert delivered.token not in response.text
    assert _verified(db_connection, user_id) == []  # delivery is not verification
    assert _events(db_connection, user_id) == ["EMAIL_VERIFICATION_ISSUED"]
    facts = db_connection.execute(
        sa.select(security_events_table.c.observed_facts).where(
            security_events_table.c.target_ref == f"user:{user_id.value}",
            security_events_table.c.event_type == "EMAIL_VERIFICATION_ISSUED",
        )
    ).scalar_one()
    assert delivered.token not in (facts or "") and email not in (facts or "")


def test_the_correct_token_verifies_once_and_creates_the_relation(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    challenge_id = _start(client, email).json()["challengeId"]
    token = mail.outbox[-1].token

    response = _complete(client, challenge_id, token)

    assert response.status_code == 200
    assert response.json() == {"kind": "ok", "email": email}
    (relation,) = _verified(db_connection, user_id)
    assert relation["email"] == email and relation["verification_method"] == "EMAIL_CHALLENGE"
    assert relation["superseded_at"] is None and relation["revoked_at"] is None
    assert _challenge(db_connection, challenge_id)["consumed_at"] is not None
    assert _events(db_connection, user_id)[-1] == "EMAIL_VERIFICATION_COMPLETED"

    replay = _complete(client, challenge_id, token)
    assert replay.status_code == 403
    assert replay.json() == {"kind": "denied", "reasonCode": "VERIFICATION_DENIED"}
    assert len(_verified(db_connection, user_id)) == 1


def test_a_wrong_token_is_denied_counted_and_eventually_locks_the_challenge(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    challenge_id = _start(client, email).json()["challengeId"]
    token = mail.outbox[-1].token

    for attempt in range(1, MAX_FAILED_ATTEMPTS + 1):
        response = _complete(client, challenge_id, "not-the-token")
        assert response.status_code == 403
        assert response.json() == {"kind": "denied", "reasonCode": "VERIFICATION_DENIED"}
        assert _challenge(db_connection, challenge_id)["failed_attempts"] == attempt
    # the attempt boundary is spent: even the correct token no longer verifies
    correct = _complete(client, challenge_id, token)
    assert correct.status_code == 403
    assert _verified(db_connection, user_id) == []
    assert "EMAIL_VERIFICATION_FAILED" in _events(db_connection, user_id)


def test_an_expired_challenge_does_not_verify(
    db_connection: sa.Connection,
    client: TestClient,
    mail: LocalMailCapture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    challenge_id = _start(client, email).json()["challengeId"]
    token = mail.outbox[-1].token
    later = datetime.now(timezone.utc) + CHALLENGE_LIFETIME + timedelta(seconds=1)
    monkeypatch.setattr(http_email, "_now", lambda: later)

    response = _complete(client, challenge_id, token)

    assert response.status_code == 403
    assert _verified(db_connection, user_id) == []


def test_a_challenge_of_another_identity_cannot_be_completed(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    owner_id, owner_email = _local_user(db_connection)
    _login(client, owner_email)
    challenge_id = _start(client, owner_email).json()["challengeId"]
    token = mail.outbox[-1].token
    client.cookies.clear()
    other_id, other_email = _local_user(db_connection)
    _login(client, other_email)

    response = _complete(client, challenge_id, token)

    assert response.status_code == 403
    assert response.json() == {"kind": "denied", "reasonCode": "VERIFICATION_DENIED"}
    assert _verified(db_connection, owner_id) == [] and _verified(db_connection, other_id) == []
    assert _challenge(db_connection, challenge_id)["consumed_at"] is None


def test_completion_and_start_require_a_session(client: TestClient) -> None:
    for response in (
        _start(client, "nobody@example.test"),
        _complete(client, str(uuid.uuid4()), "x"),
    ):
        assert response.status_code == 401
        assert response.json() == {"kind": "denied", "reasonCode": "NO_SESSION"}


def test_a_malformed_start_or_completion_is_rejected(
    db_connection: sa.Connection, client: TestClient
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    assert _start(client, "not-an-email").json() == {
        "kind": "rejected",
        "reasonCode": "EMAIL_INVALID",
    }
    assert _complete(client, "not-a-uuid", "t").json() == {
        "kind": "rejected",
        "reasonCode": "MALFORMED_CHALLENGE_ID",
    }
    unknown = _complete(client, str(uuid.uuid4()), "t")
    assert unknown.status_code == 403 and unknown.json()["reasonCode"] == "VERIFICATION_DENIED"


def test_a_new_start_supersedes_the_open_challenge_and_is_throttled(
    db_connection: sa.Connection,
    client: TestClient,
    mail: LocalMailCapture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    first = _start(client, email).json()["challengeId"]
    first_token = mail.outbox[-1].token

    throttled = _start(client, email)
    assert throttled.status_code == 429
    assert throttled.json() == {"kind": "denied", "reasonCode": "VERIFICATION_RESEND_THROTTLED"}
    assert len(mail.outbox) == 1

    later = datetime.now(timezone.utc) + RESEND_INTERVAL + timedelta(seconds=1)
    monkeypatch.setattr(http_email, "_now", lambda: later)
    second = _start(client, email).json()["challengeId"]
    assert second != first and len(mail.outbox) == 2
    assert _complete(client, first, first_token).status_code == 403  # superseded
    assert _complete(client, second, mail.outbox[-1].token).status_code == 200
    assert len(_verified(db_connection, user_id)) == 1


def test_an_email_verified_by_another_identity_cannot_be_verified_again(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    """24 §14.5 / falsifier 43: the same address does not become a verified
    relation of two identities."""
    owner_id, owner_email = _local_user(db_connection)
    _login(client, owner_email)
    challenge_id = _start(client, owner_email).json()["challengeId"]
    assert _complete(client, challenge_id, mail.outbox[-1].token).status_code == 200
    client.cookies.clear()
    other_id, other_email = _local_user(db_connection)
    _login(client, other_email)

    response = _start(client, owner_email)

    assert response.status_code == 403
    assert response.json() == {"kind": "denied", "reasonCode": "VERIFICATION_DENIED"}
    assert len(mail.outbox) == 1
    assert _verified(db_connection, other_id) == []
    assert len(_verified(db_connection, owner_id)) == 1


def test_a_second_verification_of_the_same_email_supersedes_the_first_relation(
    db_connection: sa.Connection,
    client: TestClient,
    mail: LocalMailCapture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id, email = _local_user(db_connection)
    _login(client, email)
    first = _start(client, email).json()["challengeId"]
    assert _complete(client, first, mail.outbox[-1].token).status_code == 200
    later = datetime.now(timezone.utc) + RESEND_INTERVAL + timedelta(seconds=1)
    monkeypatch.setattr(http_email, "_now", lambda: later)
    second = _start(client, email).json()["challengeId"]
    assert _complete(client, second, mail.outbox[-1].token).status_code == 200
    relations = _verified(db_connection, user_id)
    assert len(relations) == 2
    assert relations[0]["superseded_at"] is not None and relations[1]["superseded_at"] is None


def test_the_database_refuses_a_second_active_relation_for_one_address(
    db_connection: sa.Connection,
) -> None:
    first, _ = _local_user(db_connection)
    second, _ = _local_user(db_connection)
    statement = sa.text(
        "INSERT INTO verified_emails (id, user_id, email, verified_at, verification_method, "
        "provenance_ref) VALUES "
        "(:id, :user_id, 'shared@example.test', :at, 'EMAIL_CHALLENGE', 'test')"
    )
    db_connection.execute(statement, {"id": uuid.uuid4(), "user_id": first.value, "at": _NOW})
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(statement, {"id": uuid.uuid4(), "user_id": second.value, "at": _NOW})


def test_the_database_refuses_a_consumed_challenge_being_reopened_or_rewritten(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    challenge_id = _start(client, email).json()["challengeId"]
    assert _complete(client, challenge_id, mail.outbox[-1].token).status_code == 200
    for assignment in (
        "consumed_at = NULL",
        "token_hash = 'other'",
        "user_id = :other",
        "email = 'x@y.test'",
    ):
        with pytest.raises(sa.exc.DBAPIError) as refused, db_connection.begin_nested():
            db_connection.execute(
                sa.text(f"UPDATE auth_challenges SET {assignment} WHERE id = :id"),
                {"id": uuid.UUID(challenge_id), "other": _local_user(db_connection)[0].value},
            )
        assert "consumed" in str(refused.value) or "immutable" in str(refused.value), assignment


def test_verification_creates_no_authority_and_changes_no_session_or_identity(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    user_id, email = _local_user(db_connection)
    _login(client, email)
    token_before = client.cookies[SESSION_COOKIE_NAME]
    before = counts()
    challenge_id = _start(client, email).json()["challengeId"]
    assert _complete(client, challenge_id, mail.outbox[-1].token).status_code == 200
    assert counts() == before
    assert client.cookies[SESSION_COOKIE_NAME] == token_before
    user = (
        db_connection.execute(sa.select(users_table).where(users_table.c.id == user_id.value))
        .mappings()
        .one()
    )
    assert user["email"] == email and user["record_version"] == 1


def test_two_concurrent_completions_verify_once(
    db_connection: sa.Connection, mail: LocalMailCapture
) -> None:
    """24 §33.11: consumption is one conditional write; parallel completions
    yield one success at most."""
    engine = db_connection.engine
    created: UserId | None = None
    with engine.begin() as setup:
        user_id, email = _local_user(setup)
        created = user_id
        issued = email_verification.issue_challenge(
            setup, user_id=user_id, email=email, now=_NOW, environment="TEST", mail_sink=mail
        )
    first, second = engine.connect(), engine.connect()
    try:
        first_tx = first.begin()
        winner = email_verification.complete_challenge(
            first,
            user_id=user_id,
            challenge_id=issued.challenge_id,
            token=mail.outbox[-1].token,
            now=_NOW + timedelta(minutes=1),
            environment="TEST",
        )
        second_tx = second.begin()
        second.execute(sa.text("SET LOCAL lock_timeout = '300ms'"))
        with pytest.raises((sa.exc.OperationalError, email_verification.VerificationDenied)):
            email_verification.complete_challenge(
                second,
                user_id=user_id,
                challenge_id=issued.challenge_id,
                token=mail.outbox[-1].token,
                now=_NOW + timedelta(minutes=1),
                environment="TEST",
            )
        second_tx.rollback()
        first_tx.commit()
        second_tx = second.begin()
        with pytest.raises(email_verification.VerificationDenied):
            email_verification.complete_challenge(
                second,
                user_id=user_id,
                challenge_id=issued.challenge_id,
                token=mail.outbox[-1].token,
                now=_NOW + timedelta(minutes=2),
                environment="TEST",
            )
        second_tx.rollback()
        assert winner.email == email
        with engine.connect() as check:
            count = check.execute(
                sa.text("SELECT count(*) FROM verified_emails WHERE user_id = :u"),
                {"u": user_id.value},
            ).scalar_one()
        assert count == 1
    finally:
        first.close()
        second.close()
        if created is not None:
            with engine.begin() as cleanup:
                for statement in (
                    "DELETE FROM verified_emails WHERE user_id = :u",
                    "DELETE FROM auth_challenges WHERE user_id = :u",
                    "DELETE FROM local_auth_credentials WHERE user_id = :u",
                    "DELETE FROM authentication_methods WHERE user_id = :u",
                    "DELETE FROM users WHERE id = :u",
                ):
                    cleanup.execute(sa.text(statement), {"u": created.value})


def test_the_local_outbox_exists_only_with_the_capture_sink(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    challenge_id = _start(client, email).json()["challengeId"]
    outbox = client.get("/auth/test-mail/outbox")
    assert outbox.status_code == 200
    body = outbox.json()
    assert body["proofClass"] == "TEST_MAIL_SINK"
    assert [m["challengeId"] for m in body["mail"]] == [challenge_id]
    assert body["mail"][0]["token"] == mail.outbox[-1].token
    configure_auth_runtime(auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}))
    assert client.get("/auth/test-mail/outbox").status_code == 404


def test_verified_emails_are_listed_for_the_caller_only(
    db_connection: sa.Connection, client: TestClient, mail: LocalMailCapture
) -> None:
    _, email = _local_user(db_connection)
    _login(client, email)
    assert client.get("/auth/emails").json() == {"kind": "ok", "emails": []}
    challenge_id = _start(client, email).json()["challengeId"]
    _complete(client, challenge_id, mail.outbox[-1].token)
    listing = client.get("/auth/emails").json()
    assert [e["email"] for e in listing["emails"]] == [email]
    assert listing["emails"][0]["active"] is True
    client.cookies.clear()
    assert client.get("/auth/emails").status_code == 401
