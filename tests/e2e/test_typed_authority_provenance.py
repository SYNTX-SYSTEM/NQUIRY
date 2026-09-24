"""F02 WU-02.6 (HD-6): every governed write goes through the effect gate
and records real, typed authority provenance.

MUST BECOME TRUE:
- CMD_CREATE_WORKSPACE audit row: FOUNDING, ref = its own `commands` row.
- CMD_CREATE_CHALLENGE audit row: ROLE, ref = the creator's current
  `role_assignments` row; the new Challenge is a recorded created ref.
- BINDING Commands (CMD_ADD_MEMBER): ref = a real
  `human_authority_bindings` row.
MUST REMAIN IMPOSSIBLE:
- an audit row written by these Commands whose ref resolves to nothing;
- a canonical write in `packages/application` that opens its own
  SAVEPOINT beside CommitCoordinator.
"""

from __future__ import annotations

import ast
import pathlib
import uuid

import f02_support as f02
import pytest
import sqlalchemy as sa
from persistence.tables import (
    audit_events_table,
    commands_table,
    commit_units_table,
    human_authority_bindings_table,
    role_assignments_table,
    workspace_memberships_table,
)


def _audit_rows(
    db: sa.Connection, workspace_id: uuid.UUID, command_type: str
) -> list[sa.RowMapping]:
    return list(
        db.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.workspace_id == workspace_id,
                audit_events_table.c.command_type == command_type,
            )
        ).mappings()
    )


def test_founding_is_admitted_by_the_effect_gate_with_founding_provenance(
    db_connection: sa.Connection,
) -> None:
    owner = f02.insert_user(db_connection, "founder")
    result = f02.found_workspace(db_connection, owner=owner, name="Founded")
    ws = result.workspace_id.value

    rows = _audit_rows(db_connection, ws, "CMD_CREATE_WORKSPACE")
    assert len(rows) == 1
    row = rows[0]
    assert row["authority_source_type"] == "FOUNDING"
    assert row["authority_scope_ref"] == f"WORKSPACE:{ws}"
    command = (
        db_connection.execute(
            sa.select(commands_table).where(commands_table.c.id == row["authority_source_ref"])
        )
        .mappings()
        .one()
    )
    assert command["command_type"] == "CMD_CREATE_WORKSPACE"
    assert f"workspace:{ws}" in row["target_refs"]

    commit_unit = (
        db_connection.execute(
            sa.select(commit_units_table).where(commit_units_table.c.id == row["commit_id"])
        )
        .mappings()
        .one()
    )
    assert (
        f"authority_binding:{result.governance_binding_id.value}" in commit_unit["governance_refs"]
    )


def test_challenge_creation_records_role_provenance(db_connection: sa.Connection) -> None:
    owner = f02.insert_user(db_connection, "owner")
    facilitator = f02.insert_user(db_connection, "fac")
    ws = f02.found_workspace(db_connection, owner=owner, name="Roles").workspace_id
    f02.add_member(db_connection, owner=owner, workspace_id=ws, member=facilitator)

    challenge = f02.create_challenge(
        db_connection, actor=facilitator, workspace_id=ws, title="Why?"
    )

    row = _audit_rows(db_connection, ws.value, "CMD_CREATE_CHALLENGE")[0]
    assert row["authority_source_type"] == "ROLE"
    assert row["authority_scope_ref"] == f"WORKSPACE:{ws.value}"
    role = (
        db_connection.execute(
            sa.select(role_assignments_table.c.role, workspace_memberships_table.c.user_id)
            .join(
                workspace_memberships_table,
                role_assignments_table.c.membership_id == workspace_memberships_table.c.id,
            )
            .where(role_assignments_table.c.id == row["authority_source_ref"])
        )
        .mappings()
        .one()
    )
    assert role["role"] == "Facilitator"
    assert role["user_id"] == facilitator.value
    assert f"challenge:{challenge.challenge_id.value}" in row["target_refs"]


def test_binding_commands_reference_a_real_binding(db_connection: sa.Connection) -> None:
    owner = f02.insert_user(db_connection, "owner2")
    member = f02.insert_user(db_connection, "member2")
    founded = f02.found_workspace(db_connection, owner=owner, name="Bind")
    f02.add_member(db_connection, owner=owner, workspace_id=founded.workspace_id, member=member)

    row = _audit_rows(db_connection, founded.workspace_id.value, "CMD_ADD_MEMBER")[0]
    assert row["authority_source_type"] == "BINDING"
    assert row["authority_source_ref"] == founded.governance_binding_id.value
    assert (
        db_connection.execute(
            sa.select(sa.func.count())
            .select_from(human_authority_bindings_table)
            .where(human_authority_bindings_table.c.id == row["authority_source_ref"])
        ).scalar()
        == 1
    )


def _opens_savepoint(source: str) -> bool:
    """F02 WU-02.12: AST detection of any `<receiver>.begin_nested(...)` call.

    The WU-02.6 version matched only the literal text
    `with connection.begin_nested(`, so `self._connection.begin_nested()`,
    `conn.begin_nested()` or a savepoint opened outside a `with` passed
    unseen. Docstrings and comments that merely mention the method are not
    calls and are ignored.
    """
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "begin_nested"
        for node in ast.walk(ast.parse(source))
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("with connection.begin_nested():\n    pass", True),
        ("with self._connection.begin_nested():\n    pass", True),
        ("sp = conn.begin_nested()\nsp.commit()", True),
        ('"""uses connection.begin_nested() via the coordinator"""', False),
        ("# connection.begin_nested() is forbidden here\nx = 1", False),
    ],
)
def test_savepoint_detector_is_falsifiable(source: str, expected: bool) -> None:
    assert _opens_savepoint(source) is expected


def test_no_application_handler_opens_its_own_write_savepoint() -> None:
    """HD-6: CommitCoordinator is the single governed commit boundary."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    # The one documented exception: RecoveryRecord is an OPERATIONAL_RECORD
    # that 10 §63 models without a CommitUnit (PKG-24, F09 scope).
    allowed = {"recovery_handler.py"}
    offenders = [
        p.name
        for p in root.glob("*.py")
        if p.name not in allowed and _opens_savepoint(p.read_text())
    ]
    assert offenders == []
    # The exception must stay real: if recovery ever stops opening its own
    # savepoint, the allow-list entry is stale and must be removed.
    assert _opens_savepoint((root / "recovery_handler.py").read_text())
