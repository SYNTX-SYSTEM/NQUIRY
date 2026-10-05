"""Credential rotation dispatch (24 §9.2, §23.2; WU-AUTH-19): composition root
for `POST /auth/password/change`. Authenticated (the session cookie), unsafe
(the anti-CSRF boundary of WU-AUTH-14 applies), JSON body
`{currentPassword, newPassword}`. Answers: `200 {kind: ok, sessionsRevoked}`
(the current session continues), `401 denied NO_SESSION`, `403 denied
CURRENT_PASSWORD_INVALID | NO_LOCAL_CREDENTIAL`, `400 rejected
PASSWORD_INVALID` (the new password fails the rules or equals the current).
"""

from __future__ import annotations

from datetime import datetime, timezone

from persistence.engine import connect_auth as connect  # WU-AUTH-17: scoped auth persistence

from application.credential_rotation import RotationDenied, SessionRequired, rotate_password
from application.http_oidc import current_auth_runtime
from application.recovery import PasswordInvalid

_NO_SESSION: tuple[int, dict[str, object]] = (
    401,
    {"kind": "denied", "reasonCode": "NO_SESSION"},
)


def dispatch_password_change(
    *, session_token: str | None, current_password: object, new_password: object
) -> tuple[int, dict[str, object]]:
    with connect() as connection:
        try:
            outcome = rotate_password(
                connection,
                session_token=session_token,
                current_password=current_password,
                new_password=new_password,
                now=datetime.now(timezone.utc),
                environment=current_auth_runtime().environment,
            )
        except SessionRequired:
            return _NO_SESSION
        except RotationDenied as denied:
            return 403, {"kind": "denied", "reasonCode": denied.reason}
        except PasswordInvalid:
            return 400, {"kind": "rejected", "reasonCode": "PASSWORD_INVALID"}
    return 200, {"kind": "ok", "sessionsRevoked": outcome.sessions_revoked}


__all__ = ["dispatch_password_change"]
