"""Local self-registration (WU-AUTH-22; HD-AUTH-13, 2026-10-07; 24 §11.14
SELF_REGISTRATION_ALLOWED for a local e-mail address and password).

THE TRANSITION: a non-actor becomes an identity that EXISTS — a `users` row, a
LOCAL_PASSWORD credential, the IDENTITY_CREATED provenance — and, in the same
effect, the verification challenge for the address it asserted (WU-AUTH-11,
one message through the deployment's sink). The identity is NOT ESTABLISHED:
`users.established_at` stays NULL until the verification of its own address
completes (`email_verification.complete_challenge`), and until then every
business relation refuses it (`http_f02._with_actor` → IDENTITY_NOT_ESTABLISHED)
while the authentication surface — login, the chamber, verification — stays
open so it can finish.

REGISTRATION ESTABLISHES IDENTITY ONLY. No Workspace, membership, role, grant,
governance, Session or other authority is created here or anywhere down the
line (HARD-DEP-001 Option A; 24 §20.3); the created identity may later found a
workspace through the ordinary act like every identity.

ONE ANSWER (24 §45.2 pattern, as recovery): an address that already belongs to
an identity creates nothing, sends nothing, records REGISTRATION_REFUSED
(class only, no address) and the caller answers exactly as for a new address —
the login answer afterwards is the same for a wrong password and for an
address that was never registered by this person, so nothing is enumerable.

ONE EFFECT: identity + credential + provenance + challenge + message commit
together or not at all. A delivery refusal (`MailDeliveryFailed`) rolls the
whole registration back — an identity that cannot receive its verification
is not created.

Validation is the host operator's (HD-28) rules for the same credential family
(`identity_provisioning`): address shape, a name, 12..1024 characters without
surrounding whitespace.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.account_creation import (
    EMAIL_SOURCE_SELF_ASSERTED_UNVERIFIED,
    ESTABLISHMENT_PENDING,
    IDENTITY_CLASS_SELF_REGISTERED,
    NAME_SOURCE_SELF_ASSERTED,
)
from security.auth_audit import ACTOR_UNAUTHENTICATED
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import hash_password
from security.mail import MailSink
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

from application.email_verification import IssuedChallenge, issue_challenge
from application.identity_provisioning import (
    _EMAIL,
    PASSWORD_MAX_CHARS,
    PASSWORD_MIN_CHARS,
)

EVENT_CREATED = "IDENTITY_CREATED"
EVENT_REFUSED = "REGISTRATION_REFUSED"
AUTHORITY = "SELF_REGISTRATION (HD-AUTH-13)"


class RegistrationRejected(Exception):
    """The request itself is malformed: EMAIL_INVALID, NAME_REQUIRED,
    PASSWORD_INVALID. Public classes (nothing about existing identities)."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


@dataclass(frozen=True, slots=True)
class RegisteredIdentity:
    user_id: UserId
    email: str
    challenge: IssuedChallenge


def validate_registration(email: object, name: object, password: object) -> tuple[str, str, str]:
    if not isinstance(email, str):
        raise RegistrationRejected("EMAIL_INVALID")
    normalized = email.strip().lower()
    if not _EMAIL.match(normalized):
        raise RegistrationRejected("EMAIL_INVALID")
    if not isinstance(name, str) or not name.strip():
        raise RegistrationRejected("NAME_REQUIRED")
    if (
        not isinstance(password, str)
        or not password
        or password != password.strip()
        or not PASSWORD_MIN_CHARS <= len(password) <= PASSWORD_MAX_CHARS
    ):
        raise RegistrationRejected("PASSWORD_INVALID")
    return normalized, name.strip(), password


def register_local_identity(
    connection: Any,
    *,
    email: object,
    name: object,
    password: object,
    now: datetime,
    environment: Environment,
    mail_sink: MailSink,
) -> RegisteredIdentity | None:
    """On the caller's connection / transaction (HD-6). None = the address
    already belongs to an identity: nothing created, REGISTRATION_REFUSED
    recorded; the caller gives the one answer."""
    normalized, clean_name, clean_password = validate_registration(email, name, password)
    identities = SqlAlchemyIdentityRepository(connection)
    events = SqlAlchemySecurityEventRepository(connection)
    if identities.email_exists(normalized):
        events.record(
            SecurityEvent(
                security_event_id=SecurityEventId(uuid.uuid4()),
                occurred_at=now,
                environment=environment,
                actor_type=ACTOR_UNAUTHENTICATED,
                actor_id=ACTOR_UNAUTHENTICATED.lower(),
                trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
                event_type=EVENT_REFUSED,
                correlation_id=CorrelationId(uuid.uuid4()),
                target_ref=None,
                observed_facts=json.dumps({"reason": "ADDRESS_TAKEN"}, sort_keys=True),
                audit_linkage=None,
            )
        )
        return None
    user_id = UserId(uuid.uuid4())
    identities.create(
        user_id=user_id, email=normalized, name=clean_name, now=now, established_at=None
    )
    SqlAlchemyLocalCredentialRepository(connection).create(
        user_id=user_id, password_hash=hash_password(clean_password), now=now
    )
    events.record(
        SecurityEvent(
            security_event_id=SecurityEventId(uuid.uuid4()),
            occurred_at=now,
            environment=environment,
            actor_type="HUMAN_USER",
            actor_id=str(user_id.value),
            trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
            event_type=EVENT_CREATED,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=f"user:{user_id.value}",
            observed_facts=json.dumps(
                {
                    "authority": AUTHORITY,
                    "identityClass": IDENTITY_CLASS_SELF_REGISTERED,
                    "credential": "LOCAL_PASSWORD_PBKDF2_SHA256",
                    "nameSource": NAME_SOURCE_SELF_ASSERTED,
                    "emailSource": EMAIL_SOURCE_SELF_ASSERTED_UNVERIFIED,
                    "establishment": ESTABLISHMENT_PENDING,
                    "workspaceAuthority": "NONE",
                },
                sort_keys=True,
            ),
            audit_linkage=f"user:{user_id.value}",
        )
    )
    challenge = issue_challenge(
        connection,
        user_id=user_id,
        email=normalized,
        now=now,
        environment=environment,
        mail_sink=mail_sink,
    )
    return RegisteredIdentity(user_id=user_id, email=normalized, challenge=challenge)


__all__ = [
    "AUTHORITY",
    "EVENT_CREATED",
    "EVENT_REFUSED",
    "RegisteredIdentity",
    "RegistrationRejected",
    "register_local_identity",
    "validate_registration",
]
