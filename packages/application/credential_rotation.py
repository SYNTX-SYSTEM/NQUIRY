"""Credential rotation by the authenticated identity (24 §9.2 "credential
rotation", §17.1 "credential reset: replace password credential after proof";
WU-AUTH-19).

    LIVE SESSION (the caller) → the identity's OWN local credential → proof =
    the CURRENT password → new password validated (the recovery rules) →
    hash replaced → every OTHER session of the identity revoked
    (CREDENTIAL_RESET) → SecurityEvent PASSWORD_CHANGED — one transaction.

ROTATION != RECOVERY: recovery regains access without the credential (24 §17,
HA-AUTH-02); rotation needs the credential and a live session and is
therefore no Human Authority question. ROTATION != METHOD: the LOCAL_PASSWORD
method, its id and its provenance are unchanged; only the hash moves.
A wrong current password is refused and audited (PASSWORD_CHANGE_FAILED,
class only) but never ends the session: the caller is still who the session
says; the attempt is evidence, not a verdict. No e-mail, password or token
appears in any event (24 §31.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from security.auth_audit import AuthAuditEvent
from security.events import Environment
from security.local_auth import SessionRevocationReason, hash_password, verify_password
from semantic_types.ids import UserId

from application.auth_audit import record_auth_event
from application.auth_handler import SessionRequired, _require_live
from application.recovery import PasswordInvalid, validate_new_password


class RotationDenied(Exception):
    """`reason`: CURRENT_PASSWORD_INVALID | NO_LOCAL_CREDENTIAL (one class each)."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True, slots=True)
class RotationOutcome:
    user_id: UserId
    sessions_revoked: int


def rotate_password(
    connection: Any,
    *,
    session_token: str | None,
    current_password: object,
    new_password: object,
    now: datetime,
    environment: Environment | None,
) -> RotationOutcome:
    """Raises `SessionRequired` (no live session), `RotationDenied`,
    `PasswordInvalid` (the new password fails the rules or equals the old)."""
    sessions = SqlAlchemyLocalSessionRepository(connection)
    current = _require_live(session_token, session_repository=sessions, now=now)
    credentials = SqlAlchemyLocalCredentialRepository(connection)
    credential = credentials.get_by_user_id(current.user_id)
    if credential is None:
        raise RotationDenied("NO_LOCAL_CREDENTIAL")
    presented = current_password.strip() if isinstance(current_password, str) else ""
    if not presented or not verify_password(presented, credential.password_hash):
        record_auth_event(
            connection,
            AuthAuditEvent.PASSWORD_CHANGE_FAILED,
            environment=environment,
            now=now,
            actor=current.user_id,
            facts={"reason": "CURRENT_PASSWORD_INVALID"},
            never=(session_token, presented),
        )
        raise RotationDenied("CURRENT_PASSWORD_INVALID")
    password = validate_new_password(new_password)
    if password == presented:
        raise PasswordInvalid()
    if not credentials.replace_password(
        user_id=current.user_id, password_hash=hash_password(password), now=now
    ):
        raise RotationDenied("NO_LOCAL_CREDENTIAL")
    revoked = sessions.revoke_all_for_user_except(
        current.user_id,
        keep_session_id=current.session_id,
        revoked_at=now,
        reason=SessionRevocationReason.CREDENTIAL_RESET,
    )
    record_auth_event(
        connection,
        AuthAuditEvent.PASSWORD_CHANGED,
        environment=environment,
        now=now,
        actor=current.user_id,
        facts={
            "method": "LOCAL_PASSWORD",
            "methodId": str(credential.method_id.value),
            "sessionsRevoked": revoked,
            "session": f"local-session:{current.session_id}",
        },
        never=(session_token, presented, password),
    )
    return RotationOutcome(user_id=current.user_id, sessions_revoked=revoked)


__all__ = ["RotationDenied", "RotationOutcome", "SessionRequired", "rotate_password"]
