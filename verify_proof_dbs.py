"""ORANGE proof-database precondition verifier (read-only).

For each allowlisted proof database proves: exact migration head, schema
fingerprint (catalog-derived, OID-free), clean-data precondition, allowlist
membership, and no foreign connections. Also proves the fingerprint is
SENSITIVE (a DDL change inside a rolled-back transaction must change it).

Usage: python verify_proof_dbs.py [--sensitivity]
Exit 0 only if every check holds for all five databases.
"""

from __future__ import annotations

import hashlib
import json
import sys

import sqlalchemy as sa

EXPECTED_HEAD = "e8c2a5f1b7d4"
ALLOW = (
    "nquiry_proof_serial_test",
    "nquiry_proof_gw0_test",
    "nquiry_proof_gw1_test",
    "nquiry_proof_gw2_test",
    "nquiry_proof_gw3_test",
)
BASE = "postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/"

CATALOG = {
    "columns": """
        select c.relname, a.attnum, a.attname, format_type(a.atttypid, a.atttypmod),
               a.attnotnull, coalesce(pg_get_expr(d.adbin, d.adrelid), ''), a.attidentity, a.attgenerated
        from pg_attribute a join pg_class c on c.oid = a.attrelid
        join pg_namespace n on n.oid = c.relnamespace
        left join pg_attrdef d on d.adrelid = a.attrelid and d.adnum = a.attnum
        where n.nspname = 'public' and a.attnum > 0 and not a.attisdropped
        order by 1, 2""",
    "relations": """
        select c.relname, c.relkind, c.relrowsecurity, c.relforcerowsecurity, coalesce(c.relacl::text, '')
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = 'public' order by 1""",
    "constraints": """
        select conrelid::regclass::text, conname, contype, pg_get_constraintdef(oid), condeferrable, condeferred
        from pg_constraint where connamespace = 'public'::regnamespace order by 1, 2""",
    "indexes": """
        select tablename, indexname, indexdef from pg_indexes where schemaname = 'public' order by 1, 2""",
    "triggers": """
        select tgrelid::regclass::text, tgname, pg_get_triggerdef(oid), tgenabled, tgdeferrable, tginitdeferred
        from pg_trigger where not tgisinternal
          and tgrelid in (select oid from pg_class where relnamespace = 'public'::regnamespace)
        order by 1, 2""",
    "functions": """
        select p.proname, pg_get_function_identity_arguments(p.oid), pg_get_functiondef(p.oid),
               coalesce(p.proacl::text, '')
        from pg_proc p where p.pronamespace = 'public'::regnamespace order by 1, 2""",
    "policies": """
        select tablename, policyname, permissive, roles::text, cmd, coalesce(qual, ''), coalesce(with_check, '')
        from pg_policies where schemaname = 'public' order by 1, 2""",
    "views": """
        select viewname, definition from pg_views where schemaname = 'public' order by 1""",
    "types": """
        select t.typname, t.typtype, coalesce(string_agg(e.enumlabel, ',' order by e.enumsortorder), '')
        from pg_type t left join pg_enum e on e.enumtypid = t.oid
        where t.typnamespace = 'public'::regnamespace and t.typtype in ('e', 'd', 'c')
        group by 1, 2 order by 1""",
    "sequences": """
        select sequencename, data_type::text, start_value, increment_by, cycle
        from pg_sequences where schemaname = 'public' order by 1""",
    "schema_acl": """
        select nspname, coalesce(nspacl::text, '') from pg_namespace where nspname = 'public'""",
    "default_acl": """
        select defaclrole::regrole::text, defaclnamespace::regnamespace::text, defaclobjtype,
               defaclacl::text from pg_default_acl order by 1, 2, 3""",
    "extensions": "select extname, extversion from pg_extension order by 1",
}


def fingerprint(conn: sa.Connection) -> tuple[str, dict[str, str]]:
    parts: dict[str, str] = {}
    for name, sql in CATALOG.items():
        rows = [tuple(map(str, r)) for r in conn.execute(sa.text(sql))]
        parts[name] = hashlib.sha256(json.dumps(rows).encode()).hexdigest()
    overall = hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()
    return overall, parts


def check(db: str) -> dict[str, object]:
    engine = sa.create_engine(BASE + db, poolclass=sa.pool.NullPool)
    with engine.connect() as conn:
        conn.execute(sa.text("SET TRANSACTION READ ONLY"))
        head = conn.execute(sa.text("select version_num from alembic_version")).scalars().all()
        overall, parts = fingerprint(conn)
        tables = conn.execute(
            sa.text(
                "select tablename from pg_tables where schemaname = 'public' "
                "and tablename <> 'alembic_version' order by 1"
            )
        ).scalars().all()
        nonempty = {}
        for t in tables:
            n = conn.execute(sa.text(f'select count(*) from public."{t}"')).scalar_one()
            if n:
                nonempty[t] = n
        foreign = conn.execute(
            sa.text(
                "select count(*) from pg_stat_activity where datname = current_database() "
                "and pid <> pg_backend_pid()"
            )
        ).scalar_one()
        dbmeta = conn.execute(
            sa.text(
                "select pg_encoding_to_char(encoding), datcollate, datctype, datdba::regrole::text "
                "from pg_database where datname = current_database()"
            )
        ).one()
        conn.rollback()
    engine.dispose()
    return {
        "db": db,
        "allowlisted": db in ALLOW and db.endswith("_test"),
        "head": head,
        "head_ok": head == [EXPECTED_HEAD],
        "fingerprint": overall,
        "parts": parts,
        "tables": len(tables),
        "nonempty_tables": nonempty,
        "clean": not nonempty,
        "foreign_connections": foreign,
        "no_foreign_connections": foreign == 0,
        "dbmeta": list(map(str, dbmeta)),
    }


def sensitivity(db: str) -> tuple[bool, str, str, str]:
    """The fingerprint must change under a DDL delta (rolled back, never committed)."""
    engine = sa.create_engine(BASE + db, poolclass=sa.pool.NullPool)
    with engine.connect() as conn:
        before, _ = fingerprint(conn)
        conn.execute(sa.text("ALTER TABLE public.workspaces ADD COLUMN zz_px_sensitivity_probe int"))
        during, _ = fingerprint(conn)
        conn.rollback()
        after, _ = fingerprint(conn)
        conn.rollback()
    engine.dispose()
    return (before != during and before == after), before, during, after


def main() -> int:
    # shared cluster catalogs read through a PROOF database only (never a non-proof db);
    catalog_db = __import__("os").environ.get("ORANGE_CATALOG_DB", "nquiry_proof_gw0_test")
    assert catalog_db in ALLOW, "catalog db must be a proof database"
    cluster = sa.create_engine(BASE + catalog_db, poolclass=sa.pool.NullPool)
    with cluster.connect() as conn:
        present = conn.execute(
            sa.text("select datname from pg_database where datname like 'nquiry_proof%' order by 1")
        ).scalars().all()
    cluster.dispose()
    ok = True
    print(f"proof databases on cluster: {present}")
    if sorted(present) != sorted(ALLOW):
        print("ALLOWLIST_SET::FAIL (cluster proof DBs != allowlist)")
        ok = False
    else:
        print("ALLOWLIST_SET::PASS (cluster proof DBs == allowlist, exactly 5)")
    results = [check(db) for db in ALLOW]
    fps = {r["fingerprint"] for r in results}
    for r in results:
        flags = [k for k in ("allowlisted", "head_ok", "clean", "no_foreign_connections") if not r[k]]
        print(
            f"{r['db']:26} head={r['head']} tables={r['tables']} nonempty={r['nonempty_tables']} "
            f"foreign_conns={r['foreign_connections']} fp={r['fingerprint'][:16]} "
            f"meta={r['dbmeta']} -> {'PASS' if not flags else 'FAIL ' + str(flags)}"
        )
        ok = ok and not flags
    metas = {tuple(r["dbmeta"]) for r in results}
    print(
        "SCHEMA_FINGERPRINT_EQUIVALENCE::"
        + ("PASS" if len(fps) == 1 else f"FAIL ({len(fps)} distinct)")
        + f" ({results[0]['fingerprint']})"
    )
    print("DB_METADATA_EQUIVALENCE::" + ("PASS" if len(metas) == 1 else "FAIL"))
    ok = ok and len(fps) == 1 and len(metas) == 1
    if "--sensitivity" in sys.argv:
        sens, before, during, after = sensitivity(ALLOW[0])
        print(
            f"FINGERPRINT_SENSITIVITY::{'PASS' if sens else 'FAIL'} "
            f"(before={before[:16]} with-DDL={during[:16]} after-rollback={after[:16]})"
        )
        ok = ok and sens
        again = check(ALLOW[0])
        print(
            "POST_SENSITIVITY_RESTORED::"
            + ("PASS" if again["fingerprint"] == results[0]["fingerprint"] and again["clean"] else "FAIL")
        )
        ok = ok and again["fingerprint"] == results[0]["fingerprint"] and again["clean"]
    out = __import__("os").environ.get("ORANGE_PROOF_DBS_JSON")
    if out:  # written only where the caller says (committed evidence is never overwritten)
        with open(out, "w") as fh:
            json.dump(results, fh, indent=1)
    print("PROOF_DB_PRECONDITIONS::" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
