"""Mail delivery port (24 §16.1, §25.3, §36 #16; WU-AUTH-11, WU-AUTH-21).

EMAIL DELIVERY != VERIFICATION. This port carries a verification or recovery
challenge to an address; it proves nothing. Two sinks exist:
`LocalMailCapture`, a deterministic in-process outbox for DEVELOPMENT and TEST
(24 §25.3 "local email sink"), and `SmtpMailSink` (WU-AUTH-21, HD-AUTH-10:
self-service recovery through verified e-mail is part of the product), which
renders the one message per challenge kind and hands it to an SMTP submission
service — the deployment's own mail provider, named by configuration (24 §36
#16: which provider is the operator's choice; this module makes the handover
possible, never picks one).

The raw token is part of the message by necessity (the recipient must present
it). It is never stored, logged or put into a SecurityEvent; the sink is the
only place it exists outside the recipient's hands. A rendered message carries
one absolute link to the frontend's own contact (a frontend-owned path under
the public web origin) and nothing about the account beyond the address it is
sent to.
"""

from __future__ import annotations

import smtplib
import ssl
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from typing import Protocol
from urllib.parse import urlencode


@dataclass(frozen=True, slots=True)
class CapturedMail:
    kind: str
    to: str
    challenge_id: str
    token: str
    expires_at: datetime


class MailSink(Protocol):
    def deliver(self, mail: CapturedMail) -> None: ...


@dataclass
class LocalMailCapture:
    """DEVELOPMENT / TEST only: keeps delivered mail in memory."""

    outbox: list[CapturedMail] = field(default_factory=list)

    def deliver(self, mail: CapturedMail) -> None:
        self.outbox.append(mail)


class MailDeliveryFailed(RuntimeError):
    """The submission service did not accept the message (connection, TLS,
    authentication or recipient refusal). Carries no address and no token."""


@dataclass(frozen=True, slots=True)
class MailLinks:
    """Where a rendered message sends the recipient: the public web origin and
    the frontend's own paths (frontend-owned facts, configured per deployment)."""

    web_base_url: str
    verify_path: str = "/account/verify-email"
    recovery_path: str = "/recover/reset"


_SUBJECTS = {
    "EMAIL_VERIFICATION": "nquiry: verify your e-mail address",
    "PASSWORD_RECOVERY": "nquiry: reset your password",
}


def render_mail(mail: CapturedMail, links: MailLinks) -> tuple[str, str]:
    """Subject and plain-text body for one challenge. The link carries the
    challenge id and the token as the frontend contact expects them."""
    expires = mail.expires_at.strftime("%Y-%m-%d %H:%M UTC")
    if mail.kind == "EMAIL_VERIFICATION":
        query = urlencode({"challengeId": mail.challenge_id, "token": mail.token})
        link = f"{links.web_base_url}{links.verify_path}?{query}"
        body = (
            "Someone - most likely you - asked nquiry to verify this e-mail address.\n\n"
            f"Open this link while logged in to nquiry:\n{link}\n\n"
            f"It works once and expires at {expires}. If you did not ask for this, ignore this "
            "message; nothing changes."
        )
    elif mail.kind == "PASSWORD_RECOVERY":
        query = urlencode({"recovery": mail.challenge_id, "token": mail.token})
        link = f"{links.web_base_url}{links.recovery_path}?{query}"
        body = (
            "Someone - most likely you - asked nquiry to reset the password of the account "
            "that uses this e-mail address.\n\n"
            f"Choose a new password here:\n{link}\n\n"
            f"The link works once and expires at {expires}. If you did not ask for this, ignore "
            "this message; your password stays as it is."
        )
    else:
        raise ValueError(f"no message for challenge kind {mail.kind!r}")
    return _SUBJECTS[mail.kind], body


Transport = Callable[[EmailMessage], None]
"""Hands one message to the submission service; raises on refusal."""


@dataclass(frozen=True, slots=True)
class SmtpSettings:
    host: str
    port: int
    sender: str
    security: str  # "starttls" (submission, 587) | "tls" (implicit, 465)
    username: str | None = None
    password: str | None = None
    timeout_seconds: float = 10.0
    ca_file: str | None = None
    """A CA bundle to verify the submission service against (a private CA);
    None = the platform's trust store. Verification is never disabled."""

    def __post_init__(self) -> None:
        if not self.host or not self.sender:
            raise ValueError("SMTP host and sender are required")
        if self.security not in ("starttls", "tls"):
            raise ValueError(
                "SMTP security must be 'starttls' or 'tls' (plaintext submission is refused)"
            )
        if (self.username is None) != (self.password is None):
            raise ValueError("SMTP username and password come together")
        if not 0 < self.port < 65536:
            raise ValueError("SMTP port out of range")


def smtp_transport(settings: SmtpSettings) -> Transport:
    """The real submission: TLS always (STARTTLS or implicit), SASL when
    credentials are configured. Nothing about the message is logged."""

    def send(message: EmailMessage) -> None:
        context = ssl.create_default_context(cafile=settings.ca_file)
        try:
            if settings.security == "tls":
                client: smtplib.SMTP = smtplib.SMTP_SSL(
                    settings.host, settings.port, timeout=settings.timeout_seconds, context=context
                )
            else:
                client = smtplib.SMTP(
                    settings.host, settings.port, timeout=settings.timeout_seconds
                )
            with client:
                client.ehlo()
                if settings.security == "starttls":
                    client.starttls(context=context)
                    client.ehlo()
                if settings.username is not None and settings.password is not None:
                    client.login(settings.username, settings.password)
                client.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            raise MailDeliveryFailed(type(exc).__name__) from exc

    return send


@dataclass(frozen=True, slots=True)
class SmtpMailSink:
    """Production delivery (WU-AUTH-21): renders the message and submits it.
    The transport is injectable so the rendering and the error contract are
    provable without a mail server; `smtp_transport` is the real one."""

    sender: str
    links: MailLinks
    transport: Transport

    def deliver(self, mail: CapturedMail) -> None:
        subject, body = render_mail(mail, self.links)
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = mail.to
        message["Subject"] = subject
        message["Auto-Submitted"] = "auto-generated"
        # ASCII text, 7bit: the link stays one unbroken line in the raw message (no quoted-printable
        # soft breaks for a recipient's plain-text viewer to trip over)
        message.set_content(body, cte="7bit")
        self.transport(message)


__all__ = [
    "CapturedMail",
    "LocalMailCapture",
    "MailDeliveryFailed",
    "MailLinks",
    "MailSink",
    "SmtpMailSink",
    "SmtpSettings",
    "render_mail",
    "smtp_transport",
]
