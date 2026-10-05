"""Email verification dispatch (24 §23.2 "start / complete email verification";
WU-AUTH-11). Composition root for `POST /auth/email/verification/start`,
`POST /auth/email/verification/complete` and `GET /auth/emails`.

Both writes require the caller's own live session (a challenge is issued to,
and completed by, one identity). A denial that must persist (a counted failed
attempt) is handled inside the request transaction so that it commits;
refusals with nothing to persist answer the same public class,
`VERIFICATION_DENIED` (24 §45.2: no enumeration of challenge state).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from persistence.engine import connect_auth as connect  # WU-AUTH-17: scoped auth persistence
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from persistence.verification_repository import SqlAlchemyVerifiedEmailRepository
from security.auth_audit import AuthAuditEvent
from security.mail import LocalMailCapture, MailDeliveryFailed
from security.recovery import RecoveryPolicy
from semantic_types.ids import UserId

from application.auth_audit import record_auth_event
from application.auth_handler import resolve_session
from application.email_verification import (
    EmailInvalid,
    VerificationDenied,
    VerificationThrottled,
    complete_challenge,
    issue_challenge,
)
from application.http_oidc import current_auth_runtime

_NO_SESSION: tuple[int, dict[str, object]] = (401, {"kind": "denied", "reasonCode": "NO_SESSION"})
_DENIED: tuple[int, dict[str, object]] = (
    403,
    {"kind": "denied", "reasonCode": "VERIFICATION_DENIED"},
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _current_user(session_token: str | None, *, now: datetime) -> UserId | None:
    with connect() as connection:
        principal = resolve_session(
            session_token, session_repository=SqlAlchemyLocalSessionRepository(connection), now=now
        )
    return None if principal is None else principal.user_id


def dispatch_verification_start(
    *, session_token: str | None, email: object
) -> tuple[int, dict[str, object]]:
    now = _now()
    user_id = _current_user(session_token, now=now)
    if user_id is None:
        return _NO_SESSION
    runtime = current_auth_runtime()
    if runtime.mail_sink is None:
        return 503, {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_NOT_CONFIGURED"}
    if runtime.environment is None:
        return 503, {"kind": "unavailable", "reasonCode": "ENVIRONMENT_NOT_DECLARED"}
    try:
        with connect() as connection:
            issued = issue_challenge(
                connection,
                user_id=user_id,
                email=email,
                now=now,
                environment=runtime.environment,
                mail_sink=runtime.mail_sink,
            )
    except EmailInvalid:
        return 400, {"kind": "rejected", "reasonCode": "EMAIL_INVALID"}
    except VerificationThrottled:
        return 429, {"kind": "denied", "reasonCode": "VERIFICATION_RESEND_THROTTLED"}
    except VerificationDenied:
        return _DENIED
    except MailDeliveryFailed as failed:
        # WU-AUTH-21: the challenge rolled back with the transaction; the identity itself asked,
        # so the outage may be named (no enumeration surface here)
        with connect() as connection:
            record_auth_event(
                connection,
                AuthAuditEvent.MAIL_DELIVERY_FAILED,
                environment=runtime.environment,
                now=now,
                actor=user_id,
                facts={"kind": "EMAIL_VERIFICATION", "reason": str(failed)},
            )
        return 503, {"kind": "unavailable", "reasonCode": "EMAIL_DELIVERY_FAILED"}
    return 200, {
        "kind": "ok",
        "challengeId": str(issued.challenge_id),
        "expiresAt": issued.expires_at.isoformat(),
    }


def dispatch_verification_complete(
    *, session_token: str | None, challenge_id: object, token: object
) -> tuple[int, dict[str, object]]:
    now = _now()
    user_id = _current_user(session_token, now=now)
    if user_id is None:
        return _NO_SESSION
    runtime = current_auth_runtime()
    if runtime.environment is None:
        return 503, {"kind": "unavailable", "reasonCode": "ENVIRONMENT_NOT_DECLARED"}
    try:
        parsed = uuid.UUID(str(challenge_id))
    except ValueError:
        return 400, {"kind": "rejected", "reasonCode": "MALFORMED_CHALLENGE_ID"}
    if not isinstance(token, str) or not token:
        return 400, {"kind": "rejected", "reasonCode": "MALFORMED_TOKEN"}
    with connect() as connection:
        try:
            relation = complete_challenge(
                connection,
                user_id=user_id,
                challenge_id=parsed,
                token=token,
                now=now,
                environment=runtime.environment,
            )
        except VerificationDenied:
            # Inside the transaction on purpose: a counted attempt commits.
            return _DENIED
    return 200, {"kind": "ok", "email": relation.email}


def dispatch_list_verified_emails(*, session_token: str | None) -> tuple[int, dict[str, object]]:
    """`GET /auth/emails`: the caller's own verified addresses (24 §24.5)."""
    now = _now()
    user_id = _current_user(session_token, now=now)
    if user_id is None:
        return _NO_SESSION
    with connect() as connection:
        relations = SqlAlchemyVerifiedEmailRepository(connection).list_for_user(user_id)
    return 200, {
        "kind": "ok",
        "emails": [
            {
                "email": relation.email,
                "verifiedAt": relation.verified_at.isoformat(),
                "active": relation.superseded_at is None and relation.revoked_at is None,
            }
            for relation in relations
        ],
    }


def dispatch_auth_contacts() -> tuple[int, dict[str, object]]:
    """`GET /auth/contacts` (WU-AUTH-21; 24 §24.2 "recovery links if recovery
    architecture exists"): which optional, policy-gated contacts this
    deployment serves — so a frontend offers a link only when it leads
    somewhere. Public, no secret, no account fact."""
    runtime = current_auth_runtime()
    delivery = runtime.mail_sink is not None and runtime.environment is not None
    recovery = delivery and runtime.recovery_policy is RecoveryPolicy.VERIFIED_EMAIL_SELF_SERVICE
    word = {True: "AVAILABLE", False: "UNAVAILABLE"}
    return 200, {"kind": "ok", "recovery": word[recovery], "emailVerification": word[delivery]}


def dispatch_test_mail_outbox() -> tuple[int, dict[str, object]]:
    """`GET /auth/test-mail/outbox`, DEVELOPMENT / TEST only (24 §25.3 local
    email sink): the captured mail, so a browser proof can pick up a challenge.
    404 unless the runtime holds the capture sink (production refuses it)."""
    sink = current_auth_runtime().mail_sink
    if not isinstance(sink, LocalMailCapture):
        return 404, {"kind": "denied", "reasonCode": "NOT_FOUND"}
    return 200, {
        "kind": "ok",
        "proofClass": "TEST_MAIL_SINK",
        "mail": [
            {
                "kind": mail.kind,
                "to": mail.to,
                "challengeId": mail.challenge_id,
                "token": mail.token,
                "expiresAt": mail.expires_at.isoformat(),
            }
            for mail in sink.outbox
        ],
    }


__all__ = [
    "dispatch_auth_contacts",
    "dispatch_list_verified_emails",
    "dispatch_test_mail_outbox",
    "dispatch_verification_complete",
    "dispatch_verification_start",
]
