"""WU-AUTH-21: production e-mail delivery and the self-service recovery
admission (HD-AUTH-10; 24 §16.1, §17, §25.2, §36 #11 / #16).

MUST BECOME TRUE: `NQUIRY_EMAIL_DELIVERY_MODE=smtp` composes a sink from a
complete configuration and refuses an incomplete one at startup; a rendered
message carries exactly one absolute link to the frontend's own path with the
challenge id and token, the sender, the recipient, no account fact; the
transport's refusal is `MailDeliveryFailed`; a verification start under a
failing provider answers `unavailable EMAIL_DELIVERY_FAILED`, writes no
challenge, audits the refusal; a recovery start under a failing provider
answers the one answer (`ok`), writes no challenge, audits the refusal;
`VERIFIED_EMAIL_SELF_SERVICE` is admitted in PRODUCTION; `GET /auth/contacts`
tells a frontend which contacts lead somewhere.

MUST REMAIN IMPOSSIBLE: plaintext submission; a token outside the message;
an incomplete smtp configuration coming up; recovery availability without
delivery; disclosure of account existence through a delivery outage.
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import ssl
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import application.http_dispatch as http_dispatch
import application.http_email as http_email
import application.http_oidc as http_oidc
import application.http_recovery as http_recovery
import pytest
import sqlalchemy as sa
from application.auth_runtime import auth_runtime_from_environment
from application.http_oidc import configure_auth_runtime
from fastapi.testclient import TestClient
from nquiry_api.main import app
from persistence.tables import (
    auth_challenges_table,
    recovery_challenges_table,
    security_events_table,
    verified_emails_table,
)
from security.mail import (
    CapturedMail,
    MailDeliveryFailed,
    MailLinks,
    SmtpMailSink,
    SmtpSettings,
    render_mail,
)
from security.recovery import RecoveryPolicy
from test_auth_wu10_account_linking import _local_user, _login

_T = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc)
_LINKS = MailLinks(web_base_url="https://app.example.test")
_SMTP_ENV = {
    "NQUIRY_ENVIRONMENT": "PRODUCTION",
    "NQUIRY_EMAIL_DELIVERY_MODE": "smtp",
    "NQUIRY_SMTP_HOST": "mail.example.test",
    "NQUIRY_SMTP_FROM": "nquiry@example.test",
    "NQUIRY_PUBLIC_WEB_BASE_URL": "https://app.example.test",
    "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
}


class _FailingTransport:
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    def __call__(self, message: EmailMessage) -> None:
        self.messages.append(message)
        raise MailDeliveryFailed("SMTPRecipientsRefused")


class _Transport:
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    def __call__(self, message: EmailMessage) -> None:
        self.messages.append(message)


# --- rendering and the sink contract -------------------------------------------------------------


def test_a_rendered_message_carries_one_absolute_link_with_the_challenge_and_nothing_else() -> None:
    verify = CapturedMail(
        "EMAIL_VERIFICATION", "person@example.test", "c-1", "tok-v", _T + timedelta(hours=1)
    )
    subject, body = render_mail(verify, _LINKS)
    assert subject.startswith("nquiry") and "verify" in subject
    assert body.count("https://") == 1
    assert "https://app.example.test/account/verify-email?challengeId=c-1&token=tok-v" in body
    recover = CapturedMail(
        "PASSWORD_RECOVERY", "person@example.test", "r-1", "tok-r", _T + timedelta(hours=1)
    )
    subject, body = render_mail(recover, _LINKS)
    assert "https://app.example.test/recover/reset?recovery=r-1&token=tok-r" in body
    assert "2030-01-01 13:00 UTC" in body
    assert "person@example.test" not in body  # the address is the envelope, not the text
    with pytest.raises(ValueError):
        render_mail(CapturedMail("OTHER", "x@example.test", "i", "t", _T), _LINKS)


def test_the_smtp_sink_submits_from_the_sender_to_the_recipient_and_maps_a_refusal() -> None:
    transport = _Transport()
    sink = SmtpMailSink(sender="nquiry@example.test", links=_LINKS, transport=transport)
    sink.deliver(CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-2", "tok", _T))
    (message,) = transport.messages
    assert message["From"] == "nquiry@example.test" and message["To"] == "person@example.test"
    assert message["Auto-Submitted"] == "auto-generated"
    assert "recovery=r-2&token=tok" in message.get_content()
    failing = SmtpMailSink(
        sender="nquiry@example.test", links=_LINKS, transport=_FailingTransport()
    )
    with pytest.raises(MailDeliveryFailed):
        failing.deliver(CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-3", "tok", _T))


def test_smtp_settings_refuse_plaintext_half_credentials_and_an_empty_sender() -> None:
    SmtpSettings(host="h", port=587, sender="a@b.test", security="starttls")
    SmtpSettings(host="h", port=465, sender="a@b.test", security="tls", username="u", password="p")
    for bad in (
        {"host": "h", "port": 25, "sender": "a@b.test", "security": "none"},
        {"host": "h", "port": 587, "sender": "", "security": "starttls"},
        {"host": "h", "port": 587, "sender": "a@b.test", "security": "starttls", "username": "u"},
        {"host": "h", "port": 70000, "sender": "a@b.test", "security": "starttls"},
    ):
        with pytest.raises(ValueError):
            SmtpSettings(**bad)  # type: ignore[arg-type]


# --- the runtime --------------------------------------------------------------------------------


def test_the_runtime_composes_the_smtp_sink_only_from_a_complete_configuration() -> None:
    runtime = auth_runtime_from_environment(_SMTP_ENV)
    assert isinstance(runtime.mail_sink, SmtpMailSink)
    assert runtime.mail_sink.links.web_base_url == "https://app.example.test"
    assert runtime.mail_sink.links.verify_path == "/account/verify-email"
    assert runtime.recovery_policy is RecoveryPolicy.VERIFIED_EMAIL_SELF_SERVICE
    for missing in ("NQUIRY_SMTP_HOST", "NQUIRY_SMTP_FROM", "NQUIRY_PUBLIC_WEB_BASE_URL"):
        env = {k: v for k, v in _SMTP_ENV.items() if k != missing}
        with pytest.raises(ValueError):
            auth_runtime_from_environment(env)
    with pytest.raises(ValueError):
        auth_runtime_from_environment({**_SMTP_ENV, "NQUIRY_SMTP_SECURITY": "none"})
    with pytest.raises(ValueError):
        auth_runtime_from_environment(
            {**_SMTP_ENV, "NQUIRY_RECOVERY_COMPLETE_PATH": "https://evil.example/"}
        )
    paths = auth_runtime_from_environment(
        {**_SMTP_ENV, "NQUIRY_EMAIL_VERIFY_PATH": "/verify-email"}
    )
    assert (
        isinstance(paths.mail_sink, SmtpMailSink)
        and paths.mail_sink.links.verify_path == "/verify-email"
    )


def test_self_service_recovery_is_admitted_in_declared_environments_only() -> None:
    for env in ("DEVELOPMENT", "TEST", "STAGING", "PRODUCTION"):
        runtime = auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": env, "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE"}
        )
        assert runtime.recovery_policy is RecoveryPolicy.VERIFIED_EMAIL_SELF_SERVICE
    with pytest.raises(Exception):  # noqa: B017 -- RecoveryPolicyForbidden, the module's own class
        auth_runtime_from_environment({"NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE"})


# --- the contacts under a failing provider -------------------------------------------------------


@pytest.fixture
def failing_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse() -> Iterator[sa.Connection]:
        with db_connection.begin_nested():
            yield db_connection

    for module in (http_dispatch, http_oidc, http_email, http_recovery):
        monkeypatch.setattr(module, "connect", _reuse)
    sink = SmtpMailSink(sender="nquiry@example.test", links=_LINKS, transport=_FailingTransport())
    configure_auth_runtime(
        auth_runtime_from_environment(
            {
                "NQUIRY_ENVIRONMENT": "TEST",
                "NQUIRY_EMAIL_DELIVERY_MODE": "capture",  # the injected sink takes the slot
                "NQUIRY_RECOVERY_POLICY": "VERIFIED_EMAIL_SELF_SERVICE",
            },
            mail_sink=sink,
        )
    )
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        configure_auth_runtime(auth_runtime_from_environment({}))


def _events(db: sa.Connection, event_type: str) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(security_events_table).where(security_events_table.c.event_type == event_type)
        ).mappings()
    )


def test_a_failing_provider_makes_verification_unavailable_without_a_challenge_and_is_audited(
    db_connection: sa.Connection, failing_client: TestClient
) -> None:
    user_id, email = _local_user(db_connection)
    _login(failing_client, email)
    before = len(_events(db_connection, "MAIL_DELIVERY_FAILED"))
    response = failing_client.post("/auth/email/verification/start", json={"email": email})
    assert response.status_code == 503
    assert response.json() == {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_FAILED"}
    challenges = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(auth_challenges_table)
        .where(auth_challenges_table.c.user_id == user_id.value)
    ).scalar_one()
    assert challenges == 0
    events = _events(db_connection, "MAIL_DELIVERY_FAILED")
    assert len(events) == before + 1
    facts = json.loads(events[-1]["observed_facts"])
    assert facts == {"kind": "EMAIL_VERIFICATION", "reason": "SMTPRecipientsRefused"}
    assert email not in str(events[-1]["observed_facts"])


def test_a_failing_provider_keeps_recovery_start_at_the_one_answer_without_a_challenge(
    db_connection: sa.Connection, failing_client: TestClient
) -> None:
    # an address with an ACTIVE verified relation and a local password: eligible, delivery fails
    user_id, email = _local_user(db_connection)
    db_connection.execute(
        sa.insert(verified_emails_table).values(
            id=uuid.uuid4(),
            user_id=user_id.value,
            email=email,
            verified_at=datetime.now(timezone.utc),
            verification_method="EMAIL_CHALLENGE",
            superseded_at=None,
            revoked_at=None,
            provenance_ref="test:wu21",
        )
    )
    before_events = len(_events(db_connection, "MAIL_DELIVERY_FAILED"))
    eligible = failing_client.post("/auth/recovery/start", json={"email": email})
    unknown = failing_client.post("/auth/recovery/start", json={"email": "nobody@example.test"})
    assert eligible.status_code == unknown.status_code == 200
    assert eligible.json() == unknown.json() == {"kind": "ok"}
    issued = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(recovery_challenges_table)
        .where(recovery_challenges_table.c.user_id == user_id.value)
    ).scalar_one()
    assert issued == 0  # the challenge rolled back with the failed delivery
    assert len(_events(db_connection, "MAIL_DELIVERY_FAILED")) == before_events + 1
    assert _events(db_connection, "RECOVERY_ISSUED") == [] or all(
        str(user_id.value) not in (e["target_ref"] or "")
        for e in _events(db_connection, "RECOVERY_ISSUED")
    )


def test_the_public_contacts_name_what_this_deployment_serves(
    db_connection: sa.Connection, failing_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # WU-AUTH-22: `registration` follows the OPEN creation policy (absent here) × delivery
    assert failing_client.get("/auth/contacts").json() == {
        "kind": "ok",
        "recovery": "AVAILABLE",
        "emailVerification": "AVAILABLE",
        "registration": "UNAVAILABLE",
    }
    configure_auth_runtime(auth_runtime_from_environment({"NQUIRY_ENVIRONMENT": "TEST"}))
    assert failing_client.get("/auth/contacts").json() == {
        "kind": "ok",
        "recovery": "UNAVAILABLE",
        "emailVerification": "UNAVAILABLE",
        "registration": "UNAVAILABLE",
    }
    configure_auth_runtime(
        auth_runtime_from_environment(
            {"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_EMAIL_DELIVERY_MODE": "capture"}
        )
    )
    assert failing_client.get("/auth/contacts").json()["recovery"] == "UNAVAILABLE"
    assert failing_client.get("/auth/contacts").json()["emailVerification"] == "AVAILABLE"


# --- the real transport against a real STARTTLS submission service ------------------------------


def _self_signed_localhost_cert(tmp_path) -> tuple[str, str]:  # type: ignore[no-untyped-def]
    from datetime import timedelta as _td

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - _td(minutes=1))
        .not_valid_after(now + _td(hours=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    cert_path, key_path = tmp_path / "smtp.crt", tmp_path / "smtp.key"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    return str(cert_path), str(key_path)


class _SubmissionService:
    """A minimal STARTTLS + AUTH PLAIN submission service (the shape of a real
    MTA's port 587) that records what it accepted."""

    def __init__(self, cert: str, key: str, *, username: str, password: str) -> None:
        import socket
        import threading

        self.accepted: list[tuple[str, list[str], str]] = []
        self.plaintext_mail_attempted = False
        self._ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self._ctx.load_cert_chain(cert, key)
        self._creds = (username, password)
        self._sock = socket.socket()
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(4)
        self.port = self._sock.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        import base64

        while True:
            try:
                conn, _ = self._sock.accept()
            except OSError:
                return
            try:
                f = conn.makefile("rwb", buffering=0)
                f.write(b"220 localhost ESMTP test\r\n")
                tls = False
                authed = False
                sender, rcpts = "", []
                while True:
                    line = f.readline()
                    if not line:
                        break
                    cmd = line.decode("utf-8", "replace").strip()
                    upper = cmd.upper()
                    if upper.startswith("EHLO") or upper.startswith("HELO"):
                        f.write(b"250-localhost\r\n250-STARTTLS\r\n250 AUTH PLAIN\r\n")
                    elif upper == "STARTTLS":
                        f.write(b"220 go ahead\r\n")
                        conn = self._ctx.wrap_socket(conn, server_side=True)
                        f = conn.makefile("rwb", buffering=0)
                        tls = True
                    elif upper.startswith("AUTH PLAIN"):
                        blob = cmd.split(" ", 2)[2] if cmd.count(" ") >= 2 else ""
                        parts = base64.b64decode(blob).split(b"\0")
                        ok = (
                            len(parts) == 3
                            and (parts[1].decode(), parts[2].decode()) == self._creds
                        )
                        authed = ok
                        f.write(b"235 ok\r\n" if ok else b"535 bad credentials\r\n")
                    elif upper.startswith("MAIL FROM:"):
                        if not tls:
                            self.plaintext_mail_attempted = True
                            f.write(b"530 Must issue a STARTTLS command first\r\n")
                        elif not authed:
                            f.write(b"530 Authentication required\r\n")
                        else:
                            sender = cmd[10:].strip()
                            f.write(b"250 ok\r\n")
                    elif upper.startswith("RCPT TO:"):
                        rcpts.append(cmd[8:].strip())
                        f.write(b"250 ok\r\n")
                    elif upper == "DATA":
                        f.write(b"354 end with .\r\n")
                        body = b""
                        while True:
                            chunk = f.readline()
                            if chunk in (b".\r\n", b""):
                                break
                            body += chunk
                        self.accepted.append((sender, list(rcpts), body.decode("utf-8", "replace")))
                        f.write(b"250 queued\r\n")
                    elif upper == "QUIT":
                        f.write(b"221 bye\r\n")
                        break
                    else:
                        f.write(b"250 ok\r\n")
            except (OSError, ssl.SSLError):
                pass
            finally:
                with contextlib.suppress(OSError):
                    conn.close()

    def close(self) -> None:
        self._sock.close()


def test_the_real_transport_negotiates_starttls_authenticates_and_submits(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from security.mail import smtp_transport

    cert, key = _self_signed_localhost_cert(tmp_path)
    service = _SubmissionService(cert, key, username="nquiry", password="s3cret")
    try:
        settings = SmtpSettings(
            host="localhost",
            port=service.port,
            sender="nquiry@example.test",
            security="starttls",
            username="nquiry",
            password="s3cret",
            ca_file=cert,
            timeout_seconds=5,
        )
        sink = SmtpMailSink(
            sender=settings.sender, links=_LINKS, transport=smtp_transport(settings)
        )
        sink.deliver(CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-9", "tok-9", _T))
        assert len(service.accepted) == 1
        sender, rcpts, body = service.accepted[0]
        assert "nquiry@example.test" in sender and any("person@example.test" in r for r in rcpts)
        assert "recovery=r-9&token=tok-9" in body and "Subject: nquiry: reset your password" in body
        assert service.plaintext_mail_attempted is False  # MAIL FROM only after STARTTLS
        # wrong credentials → one refusal class; nothing accepted
        bad = dataclasses.replace(settings, password="wrong")
        with pytest.raises(MailDeliveryFailed):
            SmtpMailSink(sender=bad.sender, links=_LINKS, transport=smtp_transport(bad)).deliver(
                CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-10", "tok", _T)
            )
        assert len(service.accepted) == 1
        # an untrusted certificate (no ca_file) → refused, never delivered in the clear
        untrusted = dataclasses.replace(settings, ca_file=None)
        with pytest.raises(MailDeliveryFailed):
            SmtpMailSink(
                sender=untrusted.sender, links=_LINKS, transport=smtp_transport(untrusted)
            ).deliver(CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-11", "tok", _T))
        assert len(service.accepted) == 1 and service.plaintext_mail_attempted is False
    finally:
        service.close()
    # nothing listening → refused as a delivery failure, not a crash
    closed = SmtpSettings(
        host="localhost",
        port=service.port,
        sender="a@b.test",
        security="starttls",
        timeout_seconds=2,
    )
    with pytest.raises(MailDeliveryFailed):
        SmtpMailSink(sender="a@b.test", links=_LINKS, transport=smtp_transport(closed)).deliver(
            CapturedMail("PASSWORD_RECOVERY", "person@example.test", "r-12", "tok", _T)
        )
