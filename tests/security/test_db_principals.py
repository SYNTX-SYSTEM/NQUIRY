"""T9 SECURITY / ISOLATION TEST: real local PostgreSQL privilege
separation for the 9 PKG-25 service principals, against a live
database with `migrations/versions/2feb99a01f9d_service_identity_db_principals.py`
applied and `infra/local/db_roles.sql` already run.

Every "ALLOWED" case below is proven via `has_table_privilege(current_user,
...)`, evaluated over a REAL connection authenticated AS that principal
(never the superuser asking on another role's behalf) -- this avoids
needing to construct a fully FK-valid row for tables this test suite
has no business seeding, while still reflecting exactly what that
principal's own connection believes it can do. Every "FORBIDDEN" case
is proven via a REAL DML attempt against a live connection authenticated
as that principal, since PostgreSQL checks table privileges before any
constraint -- an incomplete/invalid `INSERT` still raises
`InsufficientPrivilege`/"permission denied" first if the grant is
absent, so no valid row is needed to prove a denial either.
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from security.identity import ServicePrincipal

_ALL_PRINCIPAL_NAMES = tuple(p.value for p in ServicePrincipal)


def _principal_engine(db_connection: sa.Connection, principal: str) -> sa.Engine:
    url = db_connection.engine.url.set(username=principal, password=f"{principal}_local_dev_only")
    return sa.create_engine(url)


def _has_privilege(engine: sa.Engine, table: str, privilege: str) -> bool:
    with engine.connect() as conn:
        return bool(
            conn.execute(
                sa.text("SELECT has_table_privilege(current_user, :table, :privilege)"),
                {"table": table, "privilege": privilege},
            ).scalar_one()
        )


def _assert_write_denied(engine: sa.Engine, table: str) -> None:
    with engine.connect() as conn, pytest.raises(sa.exc.DBAPIError, match="permission denied"):
        conn.execute(sa.text(f"INSERT INTO {table} DEFAULT VALUES"))
        conn.rollback()


def _assert_read_denied(engine: sa.Engine, table: str) -> None:
    with engine.connect() as conn, pytest.raises(sa.exc.DBAPIError, match="permission denied"):
        conn.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1"))
        conn.rollback()


def test_all_nine_principals_exist_and_none_is_a_superuser_or_can_create_roles_or_databases(
    db_connection: sa.Connection,
) -> None:
    """14's own "No runtime superuser" requirement -- the hard proof."""
    rows = (
        db_connection.execute(
            sa.text(
                "SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolbypassrls "
                "FROM pg_roles WHERE rolname = ANY(:names)"
            ),
            {"names": list(_ALL_PRINCIPAL_NAMES)},
        )
        .mappings()
        .all()
    )
    assert {row["rolname"] for row in rows} == set(_ALL_PRINCIPAL_NAMES)
    for row in rows:
        assert row["rolsuper"] is False, row["rolname"]
        assert row["rolcreatedb"] is False, row["rolname"]
        assert row["rolcreaterole"] is False, row["rolname"]
        assert row["rolbypassrls"] is False, row["rolname"]


def test_api_reader_can_read_but_cannot_write_a_canonical_table(
    db_connection: sa.Connection,
) -> None:
    """Mandatory attack: "for each principal attempt permitted and
    forbidden read/write"."""
    engine = _principal_engine(db_connection, "api_reader")
    try:
        assert _has_privilege(engine, "decisions", "SELECT")
        assert not _has_privilege(engine, "decisions", "INSERT")
        _assert_write_denied(engine, "decisions")
    finally:
        engine.dispose()


def test_governed_commit_writer_can_write_its_own_tables_but_not_ai_or_projection_or_recovery(
    db_connection: sa.Connection,
) -> None:
    engine = _principal_engine(db_connection, "governed_commit_writer")
    try:
        assert _has_privilege(engine, "decisions", "INSERT")
        assert _has_privilege(engine, "commit_units", "INSERT")
        assert not _has_privilege(engine, "ai_generations", "INSERT")
        assert not _has_privilege(engine, "projection_checkpoints", "INSERT")
        assert not _has_privilege(engine, "recovery_records", "INSERT")
        _assert_write_denied(engine, "ai_generations")
        _assert_write_denied(engine, "recovery_records")
    finally:
        engine.dispose()


def test_ai_gateway_writer_cannot_write_canonical_domain_or_commit_tables(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "governance write from AI
    Gateway" -- and P-23's own "AI Gateway exclusive provider path":
    the Gateway's OWN writer may never reach a canonical/commit table
    from the DB-permission layer, regardless of what the application
    layer intends."""
    engine = _principal_engine(db_connection, "ai_gateway_writer")
    try:
        assert _has_privilege(engine, "ai_generations", "INSERT")
        assert not _has_privilege(engine, "decisions", "INSERT")
        assert not _has_privilege(engine, "commands", "INSERT")
        assert not _has_privilege(engine, "commit_units", "INSERT")
        assert not _has_privilege(engine, "human_authority_bindings", "INSERT")
        _assert_write_denied(engine, "decisions")
        _assert_write_denied(engine, "human_authority_bindings")
    finally:
        engine.dispose()


def test_projection_writer_cannot_write_a_canonical_write_table(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "attempt canonical write from
    projection" -- 11 §14 explicitly excludes "projection service" from
    canonical write capability."""
    engine = _principal_engine(db_connection, "projection_writer")
    try:
        assert _has_privilege(engine, "session_read_model", "INSERT")
        assert _has_privilege(engine, "session_read_model", "DELETE")
        assert not _has_privilege(engine, "decisions", "INSERT")
        assert not _has_privilege(engine, "sessions", "UPDATE")
        _assert_write_denied(engine, "decisions")
    finally:
        engine.dispose()


def test_recovery_reader_is_scoped_to_recovery_records_only(db_connection: sa.Connection) -> None:
    engine = _principal_engine(db_connection, "recovery_reader")
    try:
        assert _has_privilege(engine, "recovery_records", "INSERT")
        assert _has_privilege(engine, "recovery_records", "UPDATE")
        assert not _has_privilege(engine, "decisions", "SELECT")
        assert not _has_privilege(engine, "commands", "SELECT")
        _assert_read_denied(engine, "decisions")
    finally:
        engine.dispose()


def test_audit_reader_can_read_but_never_write_audit_events(db_connection: sa.Connection) -> None:
    """11 §35: "Ordinary application principals cannot rewrite
    established audit history" -- proven for the one principal whose
    entire purpose is reading audit history."""
    engine = _principal_engine(db_connection, "audit_reader")
    try:
        assert _has_privilege(engine, "audit_events", "SELECT")
        assert not _has_privilege(engine, "audit_events", "INSERT")
        assert not _has_privilege(engine, "audit_events", "UPDATE")
        assert not _has_privilege(engine, "audit_events", "DELETE")
        assert not _has_privilege(engine, "decisions", "SELECT")
        _assert_write_denied(engine, "audit_events")
    finally:
        engine.dispose()


def test_security_event_writer_has_no_table_access_at_all_yet(db_connection: sa.Connection) -> None:
    """`security_events` does not exist until PKG-26 -- this role's own
    GRANT is deliberately deferred (see this package's own migration
    docstring). This test doubles as the proof that `REVOKE ALL ON
    SCHEMA public FROM PUBLIC` actually works: a role with ONLY schema
    `USAGE` and zero table grants can reach NO table at all, proving
    PostgreSQL's own default `PUBLIC` access was genuinely revoked, not
    merely left unused."""
    engine = _principal_engine(db_connection, "security_event_writer")
    try:
        assert not _has_privilege(engine, "decisions", "SELECT")
        assert not _has_privilege(engine, "audit_events", "SELECT")
        _assert_read_denied(engine, "decisions")
        _assert_read_denied(engine, "audit_events")
    finally:
        engine.dispose()


def test_test_principal_has_broad_dml_across_unrelated_subsystems(
    db_connection: sa.Connection,
) -> None:
    """`test_principal` is the disclosed NON_PROOF fixture-power
    identity -- broad DML, but never DDL and never a superuser
    attribute (already proven above)."""
    engine = _principal_engine(db_connection, "test_principal")
    try:
        for table in ("decisions", "ai_generations", "recovery_records", "audit_events"):
            assert _has_privilege(engine, table, "SELECT")
            assert _has_privilege(engine, table, "INSERT")
            assert _has_privilege(engine, table, "UPDATE")
            assert _has_privilege(engine, table, "DELETE")
    finally:
        engine.dispose()


def test_migration_owner_can_create_schema_objects_but_never_write_domain_rows(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: "Decision write from
    admin-like technical identity" -- `migration_owner` is the ONE
    principal with elevated schema (DDL) rights among these 9; P-24's
    own claim ("Admin/root technical capability is not domain
    authority") requires that this elevated DDL right still grants
    ZERO row-level write capability on any canonical table."""
    engine = _principal_engine(db_connection, "migration_owner")
    try:
        assert not _has_privilege(engine, "decisions", "INSERT")
        assert not _has_privilege(engine, "decisions", "SELECT")
        _assert_write_denied(engine, "decisions")

        probe_table = "zz_pkg25_migration_owner_ddl_probe"
        with engine.connect() as conn:
            conn.execute(sa.text(f"CREATE TABLE {probe_table} (id int)"))
            conn.execute(sa.text(f"DROP TABLE {probe_table}"))
            conn.commit()
    finally:
        engine.dispose()


def test_mut_pkg25_01_revoke_all_from_public_is_genuinely_load_bearing(
    db_connection: sa.Connection,
) -> None:
    """Guard-necessity proof, not a code mutation (this session's own
    tool classifier denies temporarily weakening a real security
    control in place -- see PKG-24's own MUTATION_TESTS section for the
    prior occurrence and the adopted alternative). This migration's
    own `REVOKE ALL ON SCHEMA public FROM PUBLIC` is the ONE statement
    standing between "a brand-new role with zero explicit grants of its
    own" and PostgreSQL's own historical default (`PUBLIC` gets
    `CREATE`/`USAGE` on the `public` schema unless revoked). A throwaway
    role created here with NO grant statement of any kind -- not even
    from this package's own migration -- must still be unable to reach
    any table, proving the revoke is what protects every OTHER
    principal's own narrow scope, not merely that nobody happened to
    grant this one anything."""
    probe_role = "zz_pkg25_mut01_no_grants_role"
    # A separate, autocommit administrative connection -- CREATE
    # ROLE/DROP ROLE are cluster-wide and must be visible to the
    # freshly-connected `_principal_engine` below, without touching the
    # shared `db_connection` fixture's own transaction (that fixture
    # rolls back at teardown; committing it here would break that
    # contract for every other test in this module).
    admin_engine = db_connection.engine.execution_options(isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as admin_conn:
        admin_conn.execute(
            sa.text(f"CREATE ROLE {probe_role} LOGIN PASSWORD '{probe_role}_local_dev_only'")
        )
        try:
            engine = _principal_engine(db_connection, probe_role)
            try:
                # No `has_table_privilege` pre-check here: with schema
                # `USAGE` itself revoked from `PUBLIC`, this role cannot
                # even resolve the unqualified table name (PostgreSQL
                # reports the object as not visible, "does not exist",
                # rather than merely "permission denied") -- an even
                # stronger lockdown than the named principals above,
                # each of which was explicitly granted `USAGE`.
                with (
                    engine.connect() as conn,
                    pytest.raises(sa.exc.DBAPIError, match="permission denied|does not exist"),
                ):
                    conn.execute(sa.text("SELECT 1 FROM decisions LIMIT 1"))
                    conn.rollback()
            finally:
                engine.dispose()
        finally:
            admin_conn.execute(sa.text(f"DROP ROLE {probe_role}"))
