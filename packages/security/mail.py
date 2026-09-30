"""Mail delivery port (24 §16.1, §25.3, §36 #16; WU-AUTH-11).

EMAIL DELIVERY != VERIFICATION. This port carries a verification (later:
recovery) challenge to an address; it proves nothing. The only materialized
sink is `LocalMailCapture`, a deterministic in-process outbox for DEVELOPMENT
and TEST (24 §25.3 "local email sink"); a production provider is a Human
Authority decision (24 §36 #16) and is not chosen here.

The raw token is part of the message by necessity (the recipient must present
it). It is never stored, logged or put into a SecurityEvent; the sink is the
only place it exists outside the recipient's hands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


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


__all__ = ["CapturedMail", "LocalMailCapture", "MailSink"]
