"""Method unlink dispatch (24 §23.2 "unlink authentication method"; WU-AUTH-13).
Composition root for `POST /auth/methods/{method_id}/unlink`.

Requires the caller's own live session. Answers: `ok` with the propagation
facts (and the session cookie cleared when the presenting session was one of
the unlinked method's), `NO_SESSION`, `MALFORMED_METHOD_ID`, `UNLINK_DENIED`
(unknown / foreign / already revoked, one class) and `LAST_METHOD` (24 §14.6).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from persistence.engine import connect_auth as connect  # WU-AUTH-17: scoped auth persistence

from application.http_dispatch import SessionDispatchResult
from application.http_oidc import current_auth_runtime
from application.revocation import (
    LastMethodRefused,
    SessionRequired,
    UnlinkDenied,
    unlink_method,
)

_NO_SESSION: dict[str, object] = {"kind": "denied", "reasonCode": "NO_SESSION"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def dispatch_unlink_method(
    *, session_token: str | None, method_id: object
) -> SessionDispatchResult:
    try:
        parsed = uuid.UUID(str(method_id))
    except ValueError:
        return SessionDispatchResult(400, {"kind": "rejected", "reasonCode": "MALFORMED_METHOD_ID"})
    environment = current_auth_runtime().environment
    with connect() as connection:
        try:
            outcome = unlink_method(
                connection, session_token, parsed, now=_now(), environment=environment
            )
        except SessionRequired:
            return SessionDispatchResult(401, _NO_SESSION)
        except UnlinkDenied:
            return SessionDispatchResult(403, {"kind": "denied", "reasonCode": "UNLINK_DENIED"})
        except LastMethodRefused:
            return SessionDispatchResult(409, {"kind": "denied", "reasonCode": "LAST_METHOD"})
    return SessionDispatchResult(
        200,
        {
            "kind": "ok",
            "methodId": str(outcome.method_id.value),
            "sessionsRevoked": outcome.sessions_revoked,
            "currentSessionEnded": outcome.current_session_ended,
        },
        clear_cookie=outcome.current_session_ended,
    )


__all__ = ["dispatch_unlink_method"]
