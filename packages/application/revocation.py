"""Authentication method unlink (24 §18 revocation; §14.6; §18.2 "If a
provider method is unlinked" / "If a credential is revoked"; WU-AUTH-13).

The identity presenting a live session revokes one of its OWN authentication
methods. One effect, in the caller's transaction (HD-6: no own commit
boundary):

1. the method becomes REVOKED (conditional write, terminal at the database);
2. a provider binding of the method becomes revoked evidence (24 §18.3), so a
   provider login through that subject is denied and the subject may be linked
   again later as a new method;
3. every session the method produced is revoked with METHOD_REVOKED
   (dependent sessions, 24 §18.2), the presenting session included when it
   was one of them;
4. a SecurityEvent AUTH_METHOD_UNLINKED (24 §31.1 "provider unlink",
   "auth method disabled").

A local password method is unlinked the same way: the credential row stays
as evidence, the login is denied by the method state (`mark_authenticated`),
and recovery of that password is no longer possible (an ACTIVE local method is
part of the recovery eligibility, WU-AUTH-12).

MUST REMAIN IMPOSSIBLE: unlinking the identity's last ACTIVE method (24 §14.6
"must remain impossible unless recovery authority is established or account
disable is intended"; §36 #12 is HUMAN_AUTHORITY_REQUIRED and undecided, so
the default stands: HA-AUTH-03). Unknown, foreign and already-revoked methods
are one refusal class (no enumeration of another identity's methods).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from persistence.provider_identity_repository import SqlAlchemyProviderIdentityRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.auth_methods import AuthenticationMethodStatus
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import SessionRevocationReason
from semantic_types.ids import AuthenticationMethodId, CorrelationId, SecurityEventId, UserId

from application.auth_handler import SessionRequired, _require_live


class UnlinkDenied(Exception):
    """The method is not one of the caller's ACTIVE methods (unknown, another
    identity's, or already revoked): one class for all three."""


class LastMethodRefused(Exception):
    """24 §14.6 / §36 #12 default: the last ACTIVE method stays."""


@dataclass(frozen=True, slots=True)
class UnlinkOutcome:
    user_id: UserId
    method_id: AuthenticationMethodId
    sessions_revoked: int
    current_session_ended: bool


def unlink_method(
    connection: Any,
    raw_token: str | None,
    method_id: uuid.UUID,
    *,
    now: datetime,
    environment: Environment | None,
) -> UnlinkOutcome:
    sessions = SqlAlchemyLocalSessionRepository(connection)
    current = _require_live(raw_token, session_repository=sessions, now=now)
    methods = SqlAlchemyAuthenticationMethodRepository(connection)
    target_id = AuthenticationMethodId(method_id)
    own = {m.method_id: m for m in methods.list_for_user(current.user_id)}
    target = own.get(target_id)
    if target is None or target.status is not AuthenticationMethodStatus.ACTIVE:
        raise UnlinkDenied("not an active method of this identity")
    active = [m for m in own.values() if m.status is AuthenticationMethodStatus.ACTIVE]
    if len(active) <= 1:
        raise LastMethodRefused("the last active authentication method stays")
    if not methods.revoke(target_id, revoked_at=now):
        # Lost a race with a concurrent unlink of the same method: it is
        # already revoked, which is the one public class above.
        raise UnlinkDenied("not an active method of this identity")
    binding_revoked = SqlAlchemyProviderIdentityRepository(connection).revoke_for_method(
        target_id, revoked_at=now
    )
    revoked = sessions.revoke_for_method(
        target_id, revoked_at=now, reason=SessionRevocationReason.METHOD_REVOKED
    )
    current_ended = current.method_id == target_id
    if environment is not None:
        SqlAlchemySecurityEventRepository(connection).record(
            SecurityEvent(
                security_event_id=SecurityEventId(uuid.uuid4()),
                occurred_at=now,
                environment=environment,
                actor_type="HUMAN_USER",
                actor_id=str(current.user_id.value),
                trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
                event_type="AUTH_METHOD_UNLINKED",
                correlation_id=CorrelationId(uuid.uuid4()),
                target_ref=f"user:{current.user_id.value}",
                observed_facts=json.dumps(
                    {
                        "authority": "24 section 18 identity revokes own method",
                        "methodId": str(target_id.value),
                        "method": target.method_type.value,
                        "providerBindingRevoked": binding_revoked,
                        "sessionsRevoked": revoked,
                        "currentSessionEnded": current_ended,
                        "remainingActiveMethods": len(active) - 1,
                    },
                    sort_keys=True,
                ),
                audit_linkage=f"user:{current.user_id.value}",
            )
        )
    return UnlinkOutcome(
        user_id=current.user_id,
        method_id=target_id,
        sessions_revoked=revoked,
        current_session_ended=current_ended,
    )


__all__ = ["LastMethodRefused", "SessionRequired", "UnlinkDenied", "UnlinkOutcome", "unlink_method"]
