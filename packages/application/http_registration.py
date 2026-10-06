"""`POST /auth/register` (WU-AUTH-22; HD-AUTH-13): the HTTP projection of local
self-registration.

Availability = the open account-creation policy (SELF_REGISTRATION_ALLOWED,
24 §11.14) AND a mail sink (the identity must be able to receive its
verification) AND a declared environment (the provenance must name it) —
otherwise 503 `REGISTRATION_NOT_AVAILABLE`; `GET /auth/contacts` says the same
word in advance so a consumer offers the contact only where it exists.

Answers: 200 `{kind: ok}` — THE ONE ANSWER for a new address and for an address
that already belongs to an identity (nothing is enumerable); 400 `rejected`
for a malformed request (EMAIL_INVALID / NAME_REQUIRED / PASSWORD_INVALID);
429 `RATE_LIMITED` for a paused client (every attempt counts); 503
`EMAIL_DELIVERY_FAILED` when the deployment's sink refused the message — the
registration rolled back with it, nothing exists. No session is created:
the person logs in with the password they chose; the identity stays
PENDING_EMAIL_VERIFICATION until the message's link is opened while logged in.
"""

from __future__ import annotations

from datetime import datetime, timezone

from persistence.engine import connect_auth as connect  # WU-AUTH-17: scoped auth persistence
from security.account_creation import AccountCreationPolicy
from security.auth_audit import AuthAuditEvent
from security.mail import MailDeliveryFailed

from application.auth_audit import record_auth_event
from application.http_oidc import current_auth_runtime
from application.local_registration import RegistrationRejected, register_local_identity
from application.login_throttle import RegistrationThrottle

_UNAVAILABLE: tuple[int, dict[str, object]] = (
    503,
    {"kind": "unavailable", "reasonCode": "REGISTRATION_NOT_AVAILABLE"},
)
_RATE_LIMITED: tuple[int, dict[str, object]] = (
    429,
    {"kind": "denied", "reasonCode": "RATE_LIMITED"},
)
_OK: tuple[int, dict[str, object]] = (200, {"kind": "ok"})


def registration_available() -> bool:
    runtime = current_auth_runtime()
    return (
        runtime.account_creation_policy is AccountCreationPolicy.SELF_REGISTRATION_ALLOWED
        and runtime.mail_sink is not None
        and runtime.environment is not None
    )


def dispatch_register(
    *, email: object, name: object, password: object, client: str | None
) -> tuple[int, dict[str, object]]:
    if not registration_available():
        return _UNAVAILABLE
    runtime = current_auth_runtime()
    assert runtime.mail_sink is not None and runtime.environment is not None
    now = datetime.now(timezone.utc)
    with connect() as connection:
        throttle = RegistrationThrottle(connection, policy=runtime.login_throttle)
        if throttle.locked(client, now=now):
            return _RATE_LIMITED
        throttle.attempted(client, now=now)
    try:
        with connect() as connection:
            register_local_identity(
                connection,
                email=email,
                name=name,
                password=password,
                now=now,
                environment=runtime.environment,
                mail_sink=runtime.mail_sink,
            )
    except RegistrationRejected as rejected:
        return 400, {"kind": "rejected", "reasonCode": rejected.reason_code}
    except MailDeliveryFailed as failed:
        # the identity, credential, provenance and challenge rolled back with the
        # transaction; the refusal is operator evidence (class only)
        with connect() as connection:
            record_auth_event(
                connection,
                AuthAuditEvent.MAIL_DELIVERY_FAILED,
                environment=runtime.environment,
                now=now,
                actor=None,
                facts={"kind": "REGISTRATION", "reason": str(failed)},
            )
        return 503, {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_FAILED"}
    return _OK


__all__ = ["dispatch_register", "registration_available"]
