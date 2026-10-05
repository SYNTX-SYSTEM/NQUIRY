"""Authentication audit writer (24 §31.1–31.3; WU-AUTH-18).

One function, `record_auth_event`, appends a SecurityEvent on the connection
of the effect it describes — the same transaction, so an event never exists
without its effect and an effect never commits without its event (F02 HD-6:
no commit boundary here; the connector owns it). The same gate as every
authentication event before it: nothing is written without a declared
environment (AC-11-017: an event names the environment it happened in).

Facts are a small JSON object of ids and classes. `FORBIDDEN_FACT_KEYS` is
enforced structurally: a caller cannot record a value under a key the
privacy law names (24 §31.3), and no fact value may equal a secret the caller
knows (the raw session token, the OIDC state) — the caller passes those as
`never` and the writer refuses to persist an event whose facts contain them.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.auth_audit import ACTOR_UNAUTHENTICATED, FORBIDDEN_FACT_KEYS, AuthAuditEvent
from security.events import Environment, SecurityEvent, TrustBoundary
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

Facts = Mapping[str, object]


class ForbiddenAuditFact(ValueError):
    """The event would have carried a value 24 §31.3 forbids."""


def _check_facts(facts: Facts, never: Iterable[str | None]) -> None:
    forbidden = FORBIDDEN_FACT_KEYS.intersection(facts.keys())
    if forbidden:
        raise ForbiddenAuditFact(f"forbidden fact keys: {sorted(forbidden)}")
    secrets = {value for value in never if value}
    if not secrets:
        return
    for key, value in facts.items():
        if isinstance(value, str) and (value in secrets or any(s in value for s in secrets)):
            raise ForbiddenAuditFact(f"fact {key!r} carries a secret value")


def record_auth_event(
    connection: Any,  # the effect's own connection (application never names the driver, 14 §3.1)
    event: AuthAuditEvent,
    *,
    environment: Environment | None,
    now: datetime,
    actor: UserId | None,
    facts: Facts,
    target_ref: str | None = None,
    never: Iterable[str | None] = (),
) -> bool:
    """Append the event on `connection`. Returns False when no environment is
    declared (nothing written). `actor` None = the unauthenticated client."""
    if environment is None:
        return False
    _check_facts(facts, never)
    actor_id = ACTOR_UNAUTHENTICATED.lower() if actor is None else str(actor.value)
    SqlAlchemySecurityEventRepository(connection).record(
        SecurityEvent(
            security_event_id=SecurityEventId(uuid.uuid4()),
            occurred_at=now,
            environment=environment,
            actor_type=ACTOR_UNAUTHENTICATED if actor is None else "HUMAN_USER",
            actor_id=actor_id,
            trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,
            event_type=event.value,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=(
                target_ref
                if target_ref is not None
                else (None if actor is None else f"user:{actor.value}")
            ),
            observed_facts=json.dumps(dict(facts), sort_keys=True),
            audit_linkage=None if actor is None else f"user:{actor.value}",
        )
    )
    return True


__all__ = ["ForbiddenAuditFact", "record_auth_event"]
