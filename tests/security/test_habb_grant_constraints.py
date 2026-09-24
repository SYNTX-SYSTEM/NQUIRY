"""T9 security tests: live database enforcement of `human_authority_bindings`
grant preconditions and immutability, against real PostgreSQL.

Covers PKG-02's mandatory adversarial attacks "absent membership" (DB-
enforced at grant time, not merely documented as a read-side caveat —
see `tests/authority/test_authority_binding_repository.py` for the
complementary read-side proof), "wrong Workspace binding" (the
`WORKSPACE_GOVERNANCE_RIGHT` scope-equals-workspace case specifically),
"AI actor binding", and "SYSTEM_SERVICE given human right".

Each "must fail" statement runs inside a `SAVEPOINT`
(`connection.begin_nested()`): PostgreSQL aborts the whole enclosing
transaction after a raised error, so without a savepoint the *next*
statement in the same test (or the fixture's own rollback) would itself
fail with "current transaction is aborted". The savepoint is what lets
one test assert several independent failures.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from persistence.tables import (
    human_authority_bindings_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from sqlalchemy.exc import DBAPIError


def _insert_user(connection: sa.Connection, *, email: str) -> uuid.UUID:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Test User",
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return user_id


def _insert_workspace(connection: sa.Connection, *, owner_id: uuid.UUID) -> uuid.UUID:
    workspace_id = uuid.uuid4()
    connection.execute(
        sa.insert(workspaces_table).values(
            id=workspace_id,
            name="W",
            owner_id=owner_id,
            record_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    return workspace_id


def _insert_membership(
    connection: sa.Connection, *, workspace_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    connection.execute(
        sa.insert(workspace_memberships_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            record_version=1,
        )
    )


def _binding_values(
    *, workspace_id: uuid.UUID, human_user_id: uuid.UUID, granted_by: uuid.UUID, **overrides: object
) -> dict:
    values: dict = {
        "id": uuid.uuid4(),
        "workspace_id": workspace_id,
        "human_user_id": human_user_id,
        "authority_class": "DECISION_RIGHT",
        "scope_type": "DECISION",
        "scope_id": uuid.uuid4(),
        "authority_source": "WORKSPACE_GOVERNANCE_ROOT",
        "granted_by_user_id": granted_by,
        "granted_at": datetime.now(timezone.utc),
        "state": "ACTIVE",
        "record_version": 1,
    }
    values.update(overrides)
    return values


def test_grant_without_active_membership_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: absent membership (05 GOV-005 precondition)."""
    owner = _insert_user(db_connection, email="owner@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    non_member = _insert_user(db_connection, email="nonmember@test.local")

    with (
        pytest.raises(DBAPIError, match="no ACTIVE workspace_membership"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(human_authority_bindings_table).values(
                **_binding_values(
                    workspace_id=workspace_id, human_user_id=non_member, granted_by=owner
                )
            )
        )

    # Connection remains usable after the savepoint rollback. Scoped to
    # this test's own Workspace: an unscoped COUNT(*) also counted rows
    # a live, demo-seeded database legitimately holds (F02 WU-02.5 fix).
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(human_authority_bindings_table)
            .where(human_authority_bindings_table.c.workspace_id == workspace_id)
        ).scalar()
        == 0
    )


def test_workspace_governance_right_scope_must_equal_workspace(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: wrong Workspace binding
    (WORKSPACE_GOVERNANCE_RIGHT-specific case, 05 GOV-002 TARGET SCOPE)."""
    owner = _insert_user(db_connection, email="owner2@test.local")
    workspace_a = _insert_workspace(db_connection, owner_id=owner)
    workspace_b = _insert_workspace(db_connection, owner_id=owner)
    _insert_membership(db_connection, workspace_id=workspace_a, user_id=owner)

    with (
        pytest.raises(
            DBAPIError, match="WORKSPACE_GOVERNANCE_RIGHT scope_id must equal workspace_id"
        ),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(human_authority_bindings_table).values(
                **_binding_values(
                    workspace_id=workspace_a,
                    human_user_id=owner,
                    granted_by=owner,
                    authority_class="WORKSPACE_GOVERNANCE_RIGHT",
                    scope_id=workspace_b,  # wrong Workspace
                )
            )
        )


def test_binding_cannot_target_a_nonexistent_identity(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attacks: AI actor binding, SYSTEM_SERVICE
    given human right. Neither has a row in `users` at all -- there is
    no service/AI identity table to reference (that lands PKG-25), so
    the only possible outcome of trying to bind one is rejection, here
    surfaced through the same "no ACTIVE workspace_membership" path a
    nonexistent identity necessarily takes (05 AC-05-007: "HABB subject
    must be a human User").
    """
    owner = _insert_user(db_connection, email="owner3@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    fictitious_ai_processor_id = uuid.uuid4()

    with pytest.raises(DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(human_authority_bindings_table).values(
                **_binding_values(
                    workspace_id=workspace_id,
                    human_user_id=fictitious_ai_processor_id,
                    granted_by=owner,
                )
            )
        )


def test_immutable_fields_cannot_be_updated_after_grant(db_connection: sa.Connection) -> None:
    """09 §50.1: subject/class/scope/source/grantor/grant time are immutable after grant."""
    owner = _insert_user(db_connection, email="owner4@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member4@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    binding_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            **_binding_values(
                workspace_id=workspace_id, human_user_id=member, granted_by=owner, id=binding_id
            )
        )
    )

    with pytest.raises(DBAPIError, match="immutable after grant"), db_connection.begin_nested():
        db_connection.execute(
            sa.update(human_authority_bindings_table)
            .where(human_authority_bindings_table.c.id == binding_id)
            .values(authority_class="ACTION_DECISION_RIGHT")
        )


def test_revoked_binding_is_terminal(db_connection: sa.Connection) -> None:
    """05 §8.1: "REVOKED is terminal for that binding record." No
    silent reactivation (05 GOV-007 FAILURE_BEHAVIOR).
    """
    owner = _insert_user(db_connection, email="owner5@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member5@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
    binding_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            **_binding_values(
                workspace_id=workspace_id, human_user_id=member, granted_by=owner, id=binding_id
            )
        )
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.id == binding_id)
        .values(state="REVOKED", revoked_at=datetime.now(timezone.utc), revoked_by_user_id=owner)
    )

    with (
        pytest.raises(DBAPIError, match="is REVOKED, which is terminal"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(human_authority_bindings_table)
            .where(human_authority_bindings_table.c.id == binding_id)
            .values(state="ACTIVE")
        )


def test_duplicate_active_membership_rejected(db_connection: sa.Connection) -> None:
    """05 GOV-002 precondition: "target User is not already an active
    member under conflicting membership."""
    owner = _insert_user(db_connection, email="owner6@test.local")
    workspace_id = _insert_workspace(db_connection, owner_id=owner)
    member = _insert_user(db_connection, email="member6@test.local")
    _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)

    with (
        pytest.raises(DBAPIError, match="uq_workspace_memberships_active_pair"),
        db_connection.begin_nested(),
    ):
        _insert_membership(db_connection, workspace_id=workspace_id, user_id=member)
