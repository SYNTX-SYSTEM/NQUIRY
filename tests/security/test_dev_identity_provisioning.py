"""F02 HD-3: DEV-ONLY local identity provisioning creates identity only.

Falsifiers: the provisioned identity must hold no membership, no role,
no authority binding, and must be able to log in through the real local
auth handler; the guards must refuse without opt-in or on a non-local host.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.auth_handler import login
from persistence.local_auth_repository import (
    SqlAlchemyLocalCredentialRepository,
    SqlAlchemyLocalSessionRepository,
)
from persistence.tables import (
    human_authority_bindings_table,
    role_assignments_table,
    workspace_memberships_table,
)
from test_support.dev_identity import (
    DEV_IDENTITY_OPT_IN_VALUE,
    DevIdentityProvisioningRefused,
    check_dev_provisioning_allowed,
    provision_dev_identity,
)

NOW = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


def _email() -> str:
    return f"dev-{uuid.uuid4().hex[:10]}@dev.local.test"


def test_provisioned_identity_has_no_membership_role_or_binding(
    db_connection: sa.Connection,
) -> None:
    identity = provision_dev_identity(
        db_connection, email=_email(), name="Dev B", password="dev-password-123", now=NOW
    )
    uid = identity.user_id.value
    for table, column in (
        (workspace_memberships_table, workspace_memberships_table.c.user_id),
        (human_authority_bindings_table, human_authority_bindings_table.c.human_user_id),
    ):
        count = db_connection.execute(
            sa.select(sa.func.count()).select_from(table).where(column == uid)
        ).scalar()
        assert count == 0
    role_count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(role_assignments_table)
        .join(
            workspace_memberships_table,
            role_assignments_table.c.membership_id == workspace_memberships_table.c.id,
        )
        .where(workspace_memberships_table.c.user_id == uid)
    ).scalar()
    assert role_count == 0
    assert identity.identity_class == "DEV_LOCAL_IDENTITY"


def test_provisioned_identity_can_log_in_through_real_local_auth(
    db_connection: sa.Connection,
) -> None:
    email = _email()
    identity = provision_dev_identity(
        db_connection, email=email, name="Dev B", password="dev-password-123", now=NOW
    )
    result = login(
        email=email.upper(),
        password="dev-password-123",
        credential_repository=SqlAlchemyLocalCredentialRepository(db_connection),
        session_repository=SqlAlchemyLocalSessionRepository(db_connection),
        now=NOW,
    )
    assert result.user_id == identity.user_id


def test_duplicate_email_is_refused(db_connection: sa.Connection) -> None:
    email = _email()
    provision_dev_identity(
        db_connection, email=email, name="A", password="dev-password-123", now=NOW
    )
    with pytest.raises(DevIdentityProvisioningRefused, match="already exists"):
        provision_dev_identity(
            db_connection, email=email, name="A", password="dev-password-123", now=NOW
        )


@pytest.mark.parametrize(
    ("email", "name", "password"),
    [
        ("no-at-sign", "A", "dev-password-123"),
        (_email(), " ", "dev-password-123"),
        (_email(), "A", "short"),
    ],
)
def test_malformed_input_is_refused(
    db_connection: sa.Connection, email: str, name: str, password: str
) -> None:
    with pytest.raises(DevIdentityProvisioningRefused):
        provision_dev_identity(db_connection, email=email, name=name, password=password, now=NOW)


def test_guard_refuses_without_explicit_opt_in() -> None:
    with pytest.raises(DevIdentityProvisioningRefused, match="must be set"):
        check_dev_provisioning_allowed(opt_in_value=None, database_host="localhost")
    with pytest.raises(DevIdentityProvisioningRefused, match="must be set"):
        check_dev_provisioning_allowed(opt_in_value="yes", database_host="localhost")


def test_guard_refuses_non_local_database_host() -> None:
    with pytest.raises(DevIdentityProvisioningRefused, match="not a local"):
        check_dev_provisioning_allowed(
            opt_in_value=DEV_IDENTITY_OPT_IN_VALUE, database_host="db.prod.example.com"
        )


def test_guard_allows_local_host_with_opt_in() -> None:
    check_dev_provisioning_allowed(
        opt_in_value=DEV_IDENTITY_OPT_IN_VALUE, database_host="localhost"
    )
