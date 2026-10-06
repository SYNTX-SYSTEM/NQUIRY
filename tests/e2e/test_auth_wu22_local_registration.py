"""WU-AUTH-22: local self-registration (HD-AUTH-13, 2026-10-07; 24 §11.14
SELF_REGISTRATION_ALLOWED for a local address and password; §20.3; 06 §7).

MUST BECOME TRUE: an unauthenticated person registers with an address, a name
and a password and gets THE ONE ANSWER; an identity, a LOCAL_PASSWORD
credential, the IDENTITY_CREATED provenance (SELF_REGISTERED, self-asserted
sources, PENDING) and the verification challenge with its message exist
together; the identity can log in and use the authentication surface but no
business relation (403 IDENTITY_NOT_ESTABLISHED) until the verification of
ITS OWN address completes — then it is established (IDENTITY_ESTABLISHED) and
`/auth/me` says so; `/auth/contacts` offers registration only where it exists;
the login-CSRF class applies; attempts per client are paused.

MUST REMAIN IMPOSSIBLE: a second identity for a taken address or any
observable difference from a fresh one; an identity without its verification
message (delivery refusal rolls everything back); establishment by verifying a
different address; any Workspace, membership, role or Session authority from
registration; registration without the open policy, a sink or an environment;
a pre-existing (operator / provider) identity becoming pending.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_f02 as http_f02
import application.http_identity as http_identity
import application.http_oidc as http_oidc
import application.http_registration as http_registration
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_dispatch import SESSION_COOKIE_NAME
from application.http_oidc import configure_auth_runtime
from application.identity_provisioning import HostOperator, create_identity_by_host_operator
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import (
    auth_challenges_table,
    local_auth_credentials_table,
    security_events_table,
    users_table,
    workspace_memberships_table,
)
from security.events import Environment
from security.mail import CapturedMail, LocalMailCapture, MailDeliveryFailed

_PASSWORD = "a passphrase long enough"
_ENV = {
    "NQUIRY_ENVIRONMENT": "TEST",
    "NQUIRY_EMAIL_DELIVERY_MODE": "capture",
    "NQUIRY_ACCOUNT_CREATION_POLICY": "SELF_REGISTRATION_ALLOWED",
}
_ORIGIN = {"Origin": "http://testserver"}


class _RefusingSink:
    def deliver(self, mail: CapturedMail) -> None:
        raise MailDeliveryFailed("SMTPRecipientsRefused")


@pytest.fixture
def mail() -> LocalMailCapture:
    return LocalMailCapture()


def _client_with(
    db_connection: sa.Connection,
    monkeypatch: pytest.MonkeyPatch,
    env: dict[str, str],
    sink: object,
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (
        http_dispatch,
        http_email,
        http_oidc,
        http_registration,
        http_f02,
        http_identity,
    ):
        monkeypatch.setattr(module, "connect", _reuse)
    configure_auth_runtime(auth_runtime_from_environment(env, mail_sink=sink))  # type: ignore[arg-type]
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


@pytest.fixture
def client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, mail: LocalMailCapture
) -> Iterator[TestClient]:
    yield from _client_with(db_connection, monkeypatch, _ENV, mail)


def _address() -> str:
    return f"{uuid.uuid4()}@example.test"


def _register(client: TestClient, email: str, name: str = "Someone", password: str = _PASSWORD):  # type: ignore[no-untyped-def]
    return client.post(
        "/auth/register", json={"email": email, "name": name, "password": password}, headers=_ORIGIN
    )


def _login(client: TestClient, email: str, password: str = _PASSWORD):  # type: ignore[no-untyped-def]
    return client.post("/auth/login", json={"email": email, "password": password}, headers=_ORIGIN)


def _user(db: sa.Connection, email: str) -> sa.RowMapping | None:
    row = db.execute(sa.select(users_table).where(users_table.c.email == email)).mappings().first()
    return row


def _events(db: sa.Connection, user_id: uuid.UUID) -> list[str]:
    return list(
        db.execute(
            sa.select(security_events_table.c.event_type)
            .where(security_events_table.c.target_ref == f"user:{user_id}")
            .order_by(security_events_table.c.occurred_at)
        ).scalars()
    )


def _facts(db: sa.Connection, user_id: uuid.UUID, event_type: str) -> dict[str, object]:
    import json

    raw = db.execute(
        sa.select(security_events_table.c.observed_facts).where(
            security_events_table.c.target_ref == f"user:{user_id}",
            security_events_table.c.event_type == event_type,
        )
    ).scalar_one()
    return dict(json.loads(raw))


def _complete(client: TestClient, delivered: CapturedMail):  # type: ignore[no-untyped-def]
    return client.post(
        "/auth/email/verification/complete",
        json={"challengeId": delivered.challenge_id, "token": delivered.token},
        headers=_ORIGIN,
    )


# --- availability ---------------------------------------------------------------------------------


def test_registration_is_offered_only_with_the_open_policy_a_sink_and_an_environment(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch, mail: LocalMailCapture
) -> None:
    for env, offered in (
        (_ENV, True),
        ({k: v for k, v in _ENV.items() if k != "NQUIRY_ACCOUNT_CREATION_POLICY"}, False),
        ({k: v for k, v in _ENV.items() if k != "NQUIRY_EMAIL_DELIVERY_MODE"}, False),
    ):
        sink = mail if "NQUIRY_EMAIL_DELIVERY_MODE" in env else None
        for client in _client_with(db_connection, monkeypatch, env, sink):
            word = client.get("/auth/contacts").json()["registration"]
            assert word == ("AVAILABLE" if offered else "UNAVAILABLE"), env
            response = _register(client, _address())
            if offered:
                assert response.status_code == 200
            else:
                assert response.status_code == 503
                assert response.json() == {
                    "kind": "unavailable",
                    "reasonCode": "REGISTRATION_NOT_AVAILABLE",
                }


# --- the transition -------------------------------------------------------------------------------


def test_registration_creates_a_pending_identity_with_its_credential_provenance_and_message(
    client: TestClient, db_connection: sa.Connection, mail: LocalMailCapture
) -> None:
    email = _address()
    response = _register(client, f"  {email.upper()} ", name="  Ada  ")
    assert response.status_code == 200 and response.json() == {"kind": "ok"}
    assert SESSION_COOKIE_NAME not in response.cookies  # identity only, no session
    user = _user(db_connection, email)
    assert user is not None and user["name"] == "Ada" and user["established_at"] is None
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(local_auth_credentials_table)
            .where(local_auth_credentials_table.c.user_id == user["id"])
        ).scalar_one()
        == 1
    )
    assert _events(db_connection, user["id"]) == ["IDENTITY_CREATED", "EMAIL_VERIFICATION_ISSUED"]
    facts = _facts(db_connection, user["id"], "IDENTITY_CREATED")
    assert facts["identityClass"] == "SELF_REGISTERED_IDENTITY"
    assert facts["nameSource"] == "SELF_ASSERTED"
    assert facts["emailSource"] == "SELF_ASSERTED_UNVERIFIED"
    assert facts["establishment"] == "PENDING_EMAIL_VERIFICATION"
    assert facts["workspaceAuthority"] == "NONE"
    assert _PASSWORD not in str(facts) and "hash" not in str(facts).lower()
    (delivered,) = mail.outbox
    assert delivered.kind == "EMAIL_VERIFICATION" and delivered.to == email
    challenge = db_connection.execute(
        sa.select(auth_challenges_table).where(
            auth_challenges_table.c.id == uuid.UUID(delivered.challenge_id)
        )
    ).first()
    assert challenge is not None and challenge.user_id == user["id"]
    # no authority of any kind
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(workspace_memberships_table)
            .where(workspace_memberships_table.c.user_id == user["id"])
        ).scalar_one()
        == 0
    )


def test_a_taken_address_gets_the_one_answer_and_nothing_else(
    client: TestClient, db_connection: sa.Connection, mail: LocalMailCapture
) -> None:
    email = _address()
    first = _register(client, email)
    users_before = db_connection.execute(
        sa.select(sa.func.count()).select_from(users_table)
    ).scalar_one()
    second = _register(client, email, name="Impostor", password="another passphrase 7")
    assert second.status_code == first.status_code == 200
    assert second.json() == first.json() == {"kind": "ok"}
    assert (
        db_connection.execute(sa.select(sa.func.count()).select_from(users_table)).scalar_one()
        == users_before
    )
    assert len(mail.outbox) == 1  # no second message
    refused = (
        db_connection.execute(
            sa.select(security_events_table.c.observed_facts).where(
                security_events_table.c.event_type == "REGISTRATION_REFUSED"
            )
        )
        .scalars()
        .all()
    )
    assert len(refused) == 1 and email not in refused[0] and "ADDRESS_TAKEN" in refused[0]
    # the impostor's password opens nothing; the owner's does — identical login classes otherwise
    assert _login(client, email, "another passphrase 7").status_code == 401
    assert _login(client, email).status_code == 200


def test_a_pending_identity_authenticates_but_holds_no_business_relation_until_verified(
    client: TestClient, db_connection: sa.Connection, mail: LocalMailCapture
) -> None:
    email = _address()
    assert _register(client, email).status_code == 200
    assert _login(client, email).status_code == 200
    me = client.get("/auth/me").json()
    assert me["kind"] == "ok" and me["establishment"] == "PENDING_EMAIL_VERIFICATION"
    # the authentication surface is open
    assert client.get("/auth/identity").json()["canonicalEmail"] == email
    assert client.get("/auth/methods").json()["methods"][0]["methodType"] == "LOCAL_PASSWORD"
    assert client.get("/auth/emails").json() == {"kind": "ok", "emails": []}
    # business relations are not
    for method, path, body in (
        ("GET", "/workspaces", None),
        ("POST", "/workspaces", {"name": "Mine"}),
        ("GET", f"/workspaces/{uuid.uuid4()}", None),  # orientation (principal resolver)
        ("GET", f"/workspaces/{uuid.uuid4()}/challenges/{uuid.uuid4()}", None),  # f02 _with_actor
    ):
        response = client.request(
            method, path, json=body, headers={**_ORIGIN, "Idempotency-Key": str(uuid.uuid4())}
        )
        assert response.status_code == 403, (method, path, response.text)
        assert response.json()["reasonCode"] == "IDENTITY_NOT_ESTABLISHED"
    # verifying ANOTHER address does not establish it
    other = _address()
    assert (
        client.post(
            "/auth/email/verification/start", json={"email": other}, headers=_ORIGIN
        ).status_code
        == 200
    )
    assert _complete(client, mail.outbox[-1]).status_code == 200
    assert client.get("/auth/me").json()["establishment"] == "PENDING_EMAIL_VERIFICATION"
    assert client.get("/workspaces").status_code == 403
    # verifying its OWN address (the registration's message) establishes it
    assert _complete(client, mail.outbox[0]).status_code == 200
    assert client.get("/auth/me").json()["establishment"] == "ESTABLISHED"
    user = _user(db_connection, email)
    assert user is not None and user["established_at"] is not None
    events = _events(db_connection, user["id"])
    assert events.count("IDENTITY_ESTABLISHED") == 1
    assert events.index("IDENTITY_ESTABLISHED") > events.index("EMAIL_VERIFICATION_COMPLETED")
    assert client.get("/workspaces").status_code == 200
    # still no authority was granted by any of this
    assert client.get("/workspaces").json()["workspaces"] == []
    # a second verification of the same identity does not re-establish or re-record
    assert client.post(
        "/auth/email/verification/start", json={"email": email}, headers=_ORIGIN
    ).status_code in (200, 429)
    assert _events(db_connection, user["id"]).count("IDENTITY_ESTABLISHED") == 1


def test_a_delivery_refusal_rolls_the_whole_registration_back(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    email = _address()
    for client in _client_with(db_connection, monkeypatch, _ENV, _RefusingSink()):
        response = _register(client, email)
        assert response.status_code == 503
        assert response.json() == {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_FAILED"}
        assert _user(db_connection, email) is None
        assert (
            db_connection.execute(
                sa.select(sa.func.count())
                .select_from(security_events_table)
                .where(security_events_table.c.event_type == "IDENTITY_CREATED")
                .where(security_events_table.c.observed_facts.contains("SELF_REGISTERED"))
            ).scalar_one()
            == 0
        )
        failed = (
            db_connection.execute(
                sa.select(security_events_table.c.observed_facts).where(
                    security_events_table.c.event_type == "MAIL_DELIVERY_FAILED"
                )
            )
            .scalars()
            .all()
        )
        assert any("REGISTRATION" in f for f in failed)
        assert _login(client, email).status_code == 401


# --- request contract and boundaries --------------------------------------------------------------


def test_malformed_requests_are_rejected_with_public_classes(client: TestClient) -> None:
    cases = (
        ({"email": "not-an-address", "name": "A", "password": _PASSWORD}, "EMAIL_INVALID"),
        ({"email": _address(), "name": "   ", "password": _PASSWORD}, "NAME_REQUIRED"),
        ({"email": _address(), "name": "A", "password": "short"}, "PASSWORD_INVALID"),
        (
            {"email": _address(), "name": "A", "password": " padded passphrase 1 "},
            "PASSWORD_INVALID",
        ),
    )
    for body, reason in cases:
        response = client.post("/auth/register", json=body, headers=_ORIGIN)
        assert response.status_code == 400, body
        assert response.json() == {"kind": "rejected", "reasonCode": reason}


def test_registration_shares_the_login_csrf_class(
    client: TestClient, mail: LocalMailCapture
) -> None:
    # a cross-site origin
    hostile = client.post(
        "/auth/register",
        json={"email": _address(), "name": "A", "password": _PASSWORD},
        headers={"Origin": "https://evil.example"},
    )
    assert hostile.status_code == 403 and hostile.json()["reasonCode"] == "LOGIN_CSRF_REJECTED"
    # a form body (not the JSON contract)
    form = client.post(
        "/auth/register",
        data={"email": _address(), "name": "A", "password": _PASSWORD},
        headers=_ORIGIN,
    )
    assert form.status_code == 403 and form.json()["reasonCode"] == "LOGIN_CSRF_REJECTED"
    assert mail.outbox == []


def test_attempts_per_client_are_paused(client: TestClient, db_connection: sa.Connection) -> None:
    for _ in range(5):
        assert _register(client, _address()).status_code == 200
    sixth = _register(client, _address())
    assert sixth.status_code == 429 and sixth.json() == {
        "kind": "denied",
        "reasonCode": "RATE_LIMITED",
    }
    # a different client keeps its own window
    other = client.post(
        "/auth/register",
        json={"email": _address(), "name": "B", "password": _PASSWORD},
        headers={**_ORIGIN, "X-Forwarded-For": "203.0.113.9"},
    )
    assert other.status_code == 200


# --- the other creation paths stay established ---------------------------------------------


def test_operator_created_identities_are_established_at_creation(
    db_connection: sa.Connection,
) -> None:
    now = datetime.now(timezone.utc)
    created = create_identity_by_host_operator(
        db_connection,
        email=_address(),
        name="Created by the operator",
        password=_PASSWORD,
        operator=HostOperator(operator_id="operator@example.test", os_user="root", host="h"),
        environment=Environment.TEST,
        now=now,
    )
    user = _user(db_connection, created.email)
    assert user is not None and user["established_at"] == now


def test_the_backfill_rule_every_identity_before_wu22_is_established(
    db_connection: sa.Connection,
) -> None:
    """The migration sets established_at = created_at for every pre-existing row;
    the same statement holds for the proof database after it ran."""
    pending = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(users_table)
        .where(users_table.c.established_at.is_(None))
        .where(
            users_table.c.created_at
            < datetime(2026, 10, 7, tzinfo=timezone.utc) - timedelta(days=1)
        )
    ).scalar_one()
    assert pending == 0
