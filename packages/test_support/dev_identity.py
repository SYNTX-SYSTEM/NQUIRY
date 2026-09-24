"""DEV-ONLY local identity provisioning (F02 HD-3, 16 §41 REC-003).

Creates exactly two rows: one `users` row and one
`local_auth_credentials` row, so that a second (third, ...) real human can
log in to a LOCAL development stack for real-stack browser proof.

What this module must never do, by the operator's own decision:
create Workspace membership, assign a role, grant a
`HumanAuthorityBinding`, grant Facilitator status or grant Session
authority. Those relations exist only through the governed product
(`CMD_ADD_MEMBER`, `CMD_GRANT_HUMAN_AUTHORITY_BINDING`, ...).

    DEV IDENTITY != MEMBERSHIP     IDENTITY != ROLE     ROLE != AUTHORITY

Why it cannot be mistaken for a registration feature:
- it lives in `test_support`, which production code may never import
  (`scripts/check_test_only_imports.py`);
- no HTTP route reaches it;
- its only caller, `scripts/dev_provision_local_identity.py`, refuses to
  run without an explicit opt-in environment variable and refuses any
  database host that is not local;
- the identity it creates is structurally identical to one a future
  production identity adapter would create. It carries NO authority, so
  there is nothing to launder. GAP-14-001 (production identity provider)
  stays open.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import users_table
from security.local_auth import hash_password
from semantic_types.ids import UserId

DEV_IDENTITY_OPT_IN_ENV = "NQUIRY_DEV_IDENTITY_PROVISIONING"
DEV_IDENTITY_OPT_IN_VALUE = "I_UNDERSTAND_THIS_IS_DEV_ONLY"
LOCAL_DATABASE_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "postgres"})


class DevIdentityProvisioningRefused(Exception):
    """Raised when a guard refuses provisioning. Nothing was written."""


@dataclass(frozen=True, slots=True)
class ProvisionedDevIdentity:
    user_id: UserId
    email: str
    identity_class: str = "DEV_LOCAL_IDENTITY"


def check_dev_provisioning_allowed(*, opt_in_value: str | None, database_host: str | None) -> None:
    if opt_in_value != DEV_IDENTITY_OPT_IN_VALUE:
        raise DevIdentityProvisioningRefused(
            f"{DEV_IDENTITY_OPT_IN_ENV} must be set to {DEV_IDENTITY_OPT_IN_VALUE!r}"
        )
    if database_host not in LOCAL_DATABASE_HOSTS:
        raise DevIdentityProvisioningRefused(
            f"database host {database_host!r} is not a local development host"
        )


def provision_dev_identity(
    connection: sa.Connection,
    *,
    email: str,
    name: str,
    password: str,
    now: datetime,
) -> ProvisionedDevIdentity:
    """Create one local identity. Raises `DevIdentityProvisioningRefused`
    for malformed input or an email that already exists."""
    normalized = email.strip().lower()
    if "@" not in normalized or not name.strip() or len(password) < 12:
        raise DevIdentityProvisioningRefused(
            "email must contain '@', name must be non-empty, password >= 12 characters"
        )
    existing = connection.execute(
        sa.select(users_table.c.id).where(users_table.c.email == normalized)
    ).first()
    if existing is not None:
        raise DevIdentityProvisioningRefused(f"identity {normalized!r} already exists")

    user_id = UserId(uuid.uuid4())
    with connection.begin_nested():
        connection.execute(
            sa.insert(users_table).values(
                id=user_id.value,
                email=normalized,
                name=name.strip(),
                record_version=1,
                created_at=now,
                updated_at=now,
            )
        )
        SqlAlchemyLocalCredentialRepository(connection).create(
            user_id=user_id, password_hash=hash_password(password), now=now
        )
    return ProvisionedDevIdentity(user_id=user_id, email=normalized)


__all__ = [
    "DEV_IDENTITY_OPT_IN_ENV",
    "DEV_IDENTITY_OPT_IN_VALUE",
    "DevIdentityProvisioningRefused",
    "ProvisionedDevIdentity",
    "check_dev_provisioning_allowed",
    "provision_dev_identity",
]
