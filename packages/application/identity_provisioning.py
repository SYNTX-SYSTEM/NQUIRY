"""Production account creation by the host operator (WU-PFC-AC1; HD-28 / NQ-DEC-056).

AUTHORITY (HD-28 Option A): account creation on PRODUCTION is an explicit
host/operator authority. It is exercised only through the server-operator
command (`nquiry_api.operator.create_identity`) by someone with shell access to
the deployment; no HTTP route reaches this module. The operator is named
explicitly on every call and recorded (HD-28: `otti@condyn.eu`).

WHAT IS CREATED, in ONE transaction:
- one canonical identity (`users` row; email normalized to lower case, unique
  case-insensitively);
- one local credential hashed with the existing mechanism
  (`security.local_auth.hash_password`, PBKDF2-HMAC-SHA256, random salt);
- one SecurityEvent (11 §47 privileged infrastructure operation affecting
  credentials; TB-17 Administrative Tooling "privileged-operation security
  event"): IDENTITY_CREATED, actor HOST_OPERATOR / the operator, the declared
  environment, target `user:<id>`, and non-secret facts only.
If any part fails, nothing persists: the three writes share the command's one
transaction (`persistence.engine.connect`, rolled back on any exception).

WHAT IS NEVER CREATED: Workspace membership, role, authority binding,
governance authority, Session participation or Session control (HD-28; 24
§11.14; HD-3: IDENTITY != MEMBERSHIP != ROLE != AUTHORITY). Those relations
exist only through the governed product.

WHAT IS NEVER DONE: persisting, returning or logging the password; accepting a
password from argv (the command reads it from stdin); password reset or any
change to an existing identity (HD-28 §2); guessing the environment (the
declared `NQUIRY_ENVIRONMENT` must be one of AC-11-017's exact values).
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.security_event_repository import SqlAlchemySecurityEventRepository
from security.events import Environment, SecurityEvent, TrustBoundary
from security.local_auth import hash_password
from semantic_types.ids import CorrelationId, SecurityEventId, UserId

ACTOR_TYPE = "HOST_OPERATOR"
EVENT_TYPE = "IDENTITY_CREATED"
AUTHORITY = "HD-28 HOST_OPERATOR"
IDENTITY_CLASS = "LOCAL_PASSWORD_IDENTITY"
PASSWORD_MIN_CHARS = 12
PASSWORD_MAX_CHARS = 1024
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ConnectionFactory = Callable[[], AbstractContextManager[Any]]


class IdentityCreationRefused(Exception):
    """Nothing was written. `reason_code` is safe to print (never a secret)."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class HostOperator:
    """The explicitly named host operator and the host facts of the call."""

    operator_id: str
    os_user: str
    host: str


@dataclass(frozen=True, slots=True)
class CreatedIdentity:
    user_id: UserId
    email: str
    security_event_id: SecurityEventId
    environment: Environment
    created_by: str


def declared_environment(raw: str | None) -> Environment:
    """AC-11-017: the environment is declared, never inferred or normalized."""
    if raw is None or raw == "":
        raise IdentityCreationRefused("ENVIRONMENT_NOT_DECLARED")
    try:
        return Environment(raw)
    except ValueError as exc:
        raise IdentityCreationRefused("ENVIRONMENT_UNKNOWN") from exc


def _validated(email: str, name: str, password: str, operator: HostOperator) -> tuple[str, str]:
    if not operator.operator_id.strip():
        raise IdentityCreationRefused("OPERATOR_REQUIRED")
    normalized = email.strip().lower()
    if not _EMAIL.match(normalized):
        raise IdentityCreationRefused("EMAIL_INVALID")
    if not name.strip():
        raise IdentityCreationRefused("NAME_REQUIRED")
    if password == "":
        raise IdentityCreationRefused("PASSWORD_REQUIRED")
    if password != password.strip():
        # Login strips surrounding whitespace (auth_handler), so such a
        # credential could never be used as typed.
        raise IdentityCreationRefused("PASSWORD_SURROUNDING_WHITESPACE")
    if len(password) < PASSWORD_MIN_CHARS:
        raise IdentityCreationRefused("PASSWORD_TOO_SHORT")
    if len(password) > PASSWORD_MAX_CHARS:
        raise IdentityCreationRefused("PASSWORD_TOO_LONG")
    return normalized, name.strip()


def create_identity_by_host_operator(
    connection: Any,
    *,
    email: str,
    name: str,
    password: str,
    operator: HostOperator,
    environment: Environment,
    now: datetime,
) -> CreatedIdentity:
    """Creates one identity + credential + SecurityEvent on `connection`, in
    the caller's transaction (no own savepoint: HD-6 keeps commit boundaries
    out of application modules). The command's `connect()` commits all three
    together or rolls all three back on any exception."""
    normalized, clean_name = _validated(email, name, password, operator)
    identities = SqlAlchemyIdentityRepository(connection)
    if identities.email_exists(normalized):
        raise IdentityCreationRefused("IDENTITY_ALREADY_EXISTS")
    user_id = UserId(uuid.uuid4())
    event_id = SecurityEventId(uuid.uuid4())
    identities.create(user_id=user_id, email=normalized, name=clean_name, now=now)
    SqlAlchemyLocalCredentialRepository(connection).create(
        user_id=user_id, password_hash=hash_password(password), now=now
    )
    SqlAlchemySecurityEventRepository(connection).record(
        SecurityEvent(
            security_event_id=event_id,
            occurred_at=now,
            environment=environment,
            actor_type=ACTOR_TYPE,
            actor_id=operator.operator_id.strip(),
            trust_boundary=TrustBoundary.TB_17_ADMINISTRATIVE_TOOLING,
            event_type=EVENT_TYPE,
            correlation_id=CorrelationId(uuid.uuid4()),
            target_ref=f"user:{user_id.value}",
            observed_facts=json.dumps(
                {
                    "authority": AUTHORITY,
                    "identityClass": IDENTITY_CLASS,
                    "credential": "LOCAL_PASSWORD_PBKDF2_SHA256",
                    "workspaceAuthority": "NONE",
                    "osUser": operator.os_user,
                    "host": operator.host,
                },
                sort_keys=True,
            ),
            audit_linkage=f"user:{user_id.value}",
        )
    )
    return CreatedIdentity(
        user_id=user_id,
        email=normalized,
        security_event_id=event_id,
        environment=environment,
        created_by=operator.operator_id.strip(),
    )


def run_host_operator_creation(
    *,
    email: str,
    name: str,
    password: str,
    operator: HostOperator,
    environment_raw: str | None,
    now: datetime,
    connect: ConnectionFactory | None = None,
) -> CreatedIdentity:
    """The command's single entry: declared environment, then one committed
    transaction (the application's own request-scoped `persistence.engine.connect`
    unless a factory is supplied)."""
    environment = declared_environment(environment_raw)
    if connect is None:
        from persistence.engine import connect as default_connect

        connect = default_connect
    with connect() as connection:
        return create_identity_by_host_operator(
            connection,
            email=email,
            name=name,
            password=password,
            operator=operator,
            environment=environment,
            now=now,
        )


__all__ = [
    "ACTOR_TYPE",
    "AUTHORITY",
    "EVENT_TYPE",
    "IDENTITY_CLASS",
    "ConnectionFactory",
    "CreatedIdentity",
    "HostOperator",
    "IdentityCreationRefused",
    "create_identity_by_host_operator",
    "declared_environment",
    "run_host_operator_creation",
]
