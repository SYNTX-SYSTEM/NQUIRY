"""Recovery dispatch (24 §23.2 "start / complete password reset"; WU-AUTH-12).
Composition root for `POST /auth/recovery/start` and `POST /auth/recovery/complete`.

Both contacts are unauthenticated (the caller has lost the credential). Under
`RecoveryPolicy.DENIED` (the default; 24 §36 #11 undecided) both answer
`unavailable` and write nothing. The start contact never discloses whether
an identity exists (24 §45.2); a denied completion that counted an attempt
is handled inside the request transaction so the count commits.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from persistence.engine import connect
from security.recovery import RecoveryPolicy

from application.http_oidc import current_auth_runtime
from application.recovery import (
    PasswordInvalid,
    RecoveryDenied,
    complete_recovery,
    request_recovery,
)

_UNAVAILABLE: tuple[int, dict[str, object]] = (
    503,
    {"kind": "unavailable", "reasonCode": "RECOVERY_NOT_AVAILABLE"},
)
_DENIED: tuple[int, dict[str, object]] = (403, {"kind": "denied", "reasonCode": "RECOVERY_DENIED"})


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _available() -> bool:
    runtime = current_auth_runtime()
    return (
        runtime.recovery_policy is RecoveryPolicy.VERIFIED_EMAIL_SELF_SERVICE
        and runtime.mail_sink is not None
        and runtime.environment is not None
    )


def dispatch_recovery_start(*, email: object) -> tuple[int, dict[str, object]]:
    if not _available():
        return _UNAVAILABLE
    runtime = current_auth_runtime()
    assert runtime.mail_sink is not None and runtime.environment is not None
    with connect() as connection:
        request_recovery(
            connection,
            email=email,
            now=_now(),
            environment=runtime.environment,
            mail_sink=runtime.mail_sink,
        )
    return 200, {"kind": "ok"}


def dispatch_recovery_complete(
    *, recovery_id: object, token: object, new_password: object
) -> tuple[int, dict[str, object]]:
    if not _available():
        return _UNAVAILABLE
    runtime = current_auth_runtime()
    assert runtime.environment is not None
    try:
        parsed = uuid.UUID(str(recovery_id))
    except ValueError:
        return 400, {"kind": "rejected", "reasonCode": "MALFORMED_RECOVERY_ID"}
    if not isinstance(token, str) or not token:
        return 400, {"kind": "rejected", "reasonCode": "MALFORMED_TOKEN"}
    with connect() as connection:
        try:
            complete_recovery(
                connection,
                recovery_id=parsed,
                token=token,
                new_password=new_password,
                now=_now(),
                environment=runtime.environment,
            )
        except PasswordInvalid:
            return 400, {"kind": "rejected", "reasonCode": "PASSWORD_INVALID"}
        except RecoveryDenied:
            return _DENIED  # inside the transaction: a counted attempt commits
    return 200, {"kind": "ok"}


__all__ = ["dispatch_recovery_complete", "dispatch_recovery_start"]
