"""T9 security tests: the PKG-25 `ServicePrincipal`/`SECURITY_CAPABILITY_MAP`
structural shape -- pure Python, no database. Real live-Postgres
privilege enforcement is proven separately in
`tests/security/test_db_principals.py`.
"""

from __future__ import annotations

from security.identity import (
    ALL_PROTECTED_TABLES,
    SECURITY_CAPABILITY_MAP,
    ServicePrincipal,
    TableOperation,
    capability_operations,
    capability_tables,
)

_WRITE_OPS = frozenset({TableOperation.INSERT, TableOperation.UPDATE, TableOperation.DELETE})

_GOVERNED_COMMIT_WRITER_TABLES = capability_tables(ServicePrincipal.GOVERNED_COMMIT_WRITER)
_AI_GATEWAY_WRITER_TABLES = capability_tables(ServicePrincipal.AI_GATEWAY_WRITER)
_PROJECTION_WRITER_TABLES = capability_tables(ServicePrincipal.PROJECTION_WRITER)
_RECOVERY_READER_TABLES = capability_tables(ServicePrincipal.RECOVERY_READER)
_AUDIT_READER_TABLES = capability_tables(ServicePrincipal.AUDIT_READER)

# 14's own PKG-25 OBJECTIVE names exactly these 9 principals, verbatim.
_EXPECTED_PRINCIPAL_NAMES = {
    "migration_owner",
    "api_reader",
    "governed_commit_writer",
    "ai_gateway_writer",
    "projection_writer",
    "recovery_reader",
    "security_event_writer",
    "audit_reader",
    "test_principal",
}

# 11 §14's own explicit list of components that do NOT receive canonical
# write capability, materialized here as the 5 tables that (as of
# PKG-25) have no real production writer anywhere in this codebase.
_NO_GOVERNED_WRITER_YET_TABLES = frozenset(
    {
        "users",
        "workspaces",
        "workspace_memberships",
        "role_assignments",
        "human_authority_bindings",
        "challenges",
        "sessions",
    }
)


def test_exactly_the_nine_named_principals_exist() -> None:
    names = {p.value for p in ServicePrincipal}
    assert names == _EXPECTED_PRINCIPAL_NAMES


def test_api_reader_is_select_only_on_every_protected_table() -> None:
    """Mandatory attack: "for each principal attempt permitted and
    forbidden read/write" -- api_reader's own forbidden case is ANY
    write, anywhere."""
    for table in ALL_PROTECTED_TABLES:
        ops = capability_operations(ServicePrincipal.API_READER, table)
        assert ops == frozenset({TableOperation.SELECT}), table
    assert capability_tables(ServicePrincipal.API_READER) == frozenset(ALL_PROTECTED_TABLES)


def test_migration_owner_has_no_row_level_dml_capability_at_all() -> None:
    """migration_owner is DDL-only (11 §15: "schema migration
    capability, not domain mutation authority") -- it has no row-level
    capability of any kind in this table-keyed map."""
    assert SECURITY_CAPABILITY_MAP[ServicePrincipal.MIGRATION_OWNER] == ()


def test_security_event_writer_has_no_grant_yet() -> None:
    """`security_events` does not exist until PKG-26 -- the role is
    named (14's own literal list) but carries no capability here yet,
    the same disclosed forward-reference pattern `recovery_reader`
    itself followed one package earlier for `recovery_records`."""
    assert SECURITY_CAPABILITY_MAP[ServicePrincipal.SECURITY_EVENT_WRITER] == ()


def test_ai_gateway_writer_cannot_touch_any_governed_commit_writer_table() -> None:
    """Mandatory package-specific attack: "governance write from AI
    Gateway" -- structurally, ai_gateway_writer's own table set shares
    NOTHING with governed_commit_writer's own table set (which includes
    `decisions`, the canonical Decision table)."""
    assert _AI_GATEWAY_WRITER_TABLES.isdisjoint(_GOVERNED_COMMIT_WRITER_TABLES)
    assert "decisions" not in _AI_GATEWAY_WRITER_TABLES
    governance_tables = ("human_authority_bindings", "role_assignments", "workspace_memberships")
    for governance_table in governance_tables:
        assert governance_table not in _AI_GATEWAY_WRITER_TABLES


def test_projection_writer_cannot_touch_any_canonical_write_table() -> None:
    """Mandatory package-specific attack: "attempt canonical write from
    projection" -- structurally, projection_writer's own table set
    (the 3 read-model/checkpoint tables) shares NOTHING with
    governed_commit_writer's own canonical set."""
    assert _PROJECTION_WRITER_TABLES.isdisjoint(_GOVERNED_COMMIT_WRITER_TABLES)
    assert _PROJECTION_WRITER_TABLES.isdisjoint(_AI_GATEWAY_WRITER_TABLES)
    assert "decisions" not in _PROJECTION_WRITER_TABLES


def test_recovery_reader_is_scoped_to_recovery_records_only() -> None:
    assert frozenset({"recovery_records"}) == _RECOVERY_READER_TABLES
    assert _RECOVERY_READER_TABLES.isdisjoint(_GOVERNED_COMMIT_WRITER_TABLES)


def test_audit_reader_is_read_only_and_cannot_write_audit_events() -> None:
    """11 §35: "Ordinary application principals cannot rewrite
    established audit history" -- audit_reader itself proves the read
    side of that separation: it can SELECT audit_events but has no
    write operation on it at all, even though governed_commit_writer
    (a DIFFERENT principal) does."""
    assert frozenset({"audit_events"}) == _AUDIT_READER_TABLES
    assert capability_operations(ServicePrincipal.AUDIT_READER, "audit_events") == frozenset(
        {TableOperation.SELECT}
    )


def test_no_governed_writer_yet_tables_receive_no_write_grant_from_any_principal() -> None:
    """Every table with no real production writer in this codebase (see
    `security.identity`'s own "code-grounded" docstring section) must
    not be silently granted write capability to any principal except
    `test_principal` (the disclosed NON_PROOF fixture power)."""
    for principal, capabilities in SECURITY_CAPABILITY_MAP.items():
        if principal is ServicePrincipal.TEST_PRINCIPAL:
            continue
        for capability in capabilities:
            if capability.table in _NO_GOVERNED_WRITER_YET_TABLES:
                assert not (capability.operations & _WRITE_OPS), (principal, capability.table)


def test_test_principal_has_broad_dml_but_capability_map_names_no_ddl_verb() -> None:
    """`test_principal` gets full DML on every table (NON_PROOF fixture
    power) but `TableOperation` itself has no DDL member at all --
    structurally, this map can never grant CREATE/ALTER/DROP to
    anything."""
    assert capability_tables(ServicePrincipal.TEST_PRINCIPAL) == frozenset(ALL_PROTECTED_TABLES)
    for table in ALL_PROTECTED_TABLES:
        ops = capability_operations(ServicePrincipal.TEST_PRINCIPAL, table)
        expected = {
            TableOperation.SELECT,
            TableOperation.INSERT,
            TableOperation.UPDATE,
            TableOperation.DELETE,
        }
        assert ops == frozenset(expected)
    assert {op.value for op in TableOperation} == {"SELECT", "INSERT", "UPDATE", "DELETE"}


def test_capability_operations_returns_empty_for_an_unrelated_table() -> None:
    """Fail-closed default: a principal with no declared row for a
    table has NO capability on it, never an inferred/default one."""
    assert capability_operations(ServicePrincipal.AUDIT_READER, "decisions") == frozenset()
    assert capability_operations(ServicePrincipal.RECOVERY_READER, "commit_units") == frozenset()


def test_all_protected_tables_is_exhaustive_against_the_capability_map() -> None:
    """Every table named anywhere in `SECURITY_CAPABILITY_MAP` must
    appear in `ALL_PROTECTED_TABLES` -- prevents a future edit from
    silently introducing an ungoverned table name."""
    named_tables = {
        capability.table
        for capabilities in SECURITY_CAPABILITY_MAP.values()
        for capability in capabilities
    }
    assert named_tables <= set(ALL_PROTECTED_TABLES)
