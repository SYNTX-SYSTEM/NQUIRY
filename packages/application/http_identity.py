"""`GET /auth/identity` dispatch (PURPLE_IDENTITY_PRESENTATION_01): the
authenticated self's human-facing identity presentation.

Kept apart from `GET /auth/me` on purpose: `/auth/me` is the authentication
VERDICT (`{kind, userId}`, 24 §20.1 AuthenticatedPrincipal) and stays so; this
contact answers the identity PRESENTATION question, which is method-independent
identity truth. Answers: `ok` with exactly `userId`, `displayName`,
`canonicalEmail`; `NO_SESSION` (401) otherwise — the same one class for a
missing, unknown, expired or revoked session and for a principal without an
identity row.
"""

from __future__ import annotations

from datetime import datetime, timezone

from persistence.engine import connect_auth as connect

from application.identity_presentation import SessionRequired, own_identity_presentation

_NO_SESSION: tuple[int, dict[str, object]] = (401, {"kind": "denied", "reasonCode": "NO_SESSION"})


def dispatch_identity_presentation(*, session_token: str | None) -> tuple[int, dict[str, object]]:
    with connect() as connection:
        try:
            presentation = own_identity_presentation(
                connection, session_token, now=datetime.now(timezone.utc)
            )
        except SessionRequired:
            return _NO_SESSION
    return 200, {
        "kind": "ok",
        "userId": str(presentation.user_id.value),
        "displayName": presentation.display_name,
        "canonicalEmail": presentation.canonical_email,
    }


__all__ = ["dispatch_identity_presentation"]
