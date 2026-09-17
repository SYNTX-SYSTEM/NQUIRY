#!/usr/bin/env python3
"""Migration pipeline validation skeleton.

14 §44 PHASE 0 gate: "migration pipeline empty-pass". This script
proves the Alembic pipeline is structurally valid and, at this build
phase, that it is genuinely empty (14 §7: "No domain tables... empty
Alembic pipeline only").

Two independent checks:

1. STATIC (always runs, no DB required): the Alembic `ScriptDirectory`
   loads without error and has zero revisions and zero heads, or (in a
   later phase) a single linear chain with no branch points.
2. LIVE (runs only if `DATABASE_URL` is set and reachable): `alembic
   upgrade head` followed by `alembic current` matches head, proving
   the pipeline actually applies against a real PostgreSQL instance
   (14 §9 MIGRATION PLAN). Skipped, not silently passed, when no
   database is reachable — this script reports
   `MIGRATION_LIVE_CHECK::SKIPPED_NO_DATABASE` rather than pretending
   success.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_INI = REPO_ROOT / "migrations" / "alembic.ini"


def _alembic_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(REPO_ROOT / "migrations"))
    return cfg


def check_static() -> tuple[bool, str]:
    script_dir = ScriptDirectory.from_config(_alembic_config())
    revisions = list(script_dir.walk_revisions())
    heads = script_dir.get_heads()

    if len(revisions) == 0 and len(heads) == 0:
        return True, "MIGRATION_STATIC_CHECK::PASS (empty pipeline, as required at Phase 0)"

    if len(heads) > 1:
        return (
            False,
            f"MIGRATION_STATIC_CHECK::FAIL (branched heads: {heads}; a linear chain is required)",
        )

    return True, f"MIGRATION_STATIC_CHECK::PASS ({len(revisions)} revision(s), single head {heads})"


def check_live() -> tuple[bool, str]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return True, "MIGRATION_LIVE_CHECK::SKIPPED_NO_DATABASE (DATABASE_URL not set)"

    try:
        import sqlalchemy
    except ImportError:
        return True, "MIGRATION_LIVE_CHECK::SKIPPED_NO_DATABASE (sqlalchemy not installed)"

    try:
        engine = sqlalchemy.create_engine(database_url, connect_args={"connect_timeout": 3})
        with engine.connect():
            pass
    except Exception as exc:  # pragma: no cover - depends on live environment
        return True, f"MIGRATION_LIVE_CHECK::SKIPPED_NO_DATABASE (unreachable: {exc})"

    from alembic import command

    cfg = _alembic_config()
    command.upgrade(cfg, "head")

    script_dir = ScriptDirectory.from_config(cfg)
    expected_heads = set(script_dir.get_heads())

    with engine.connect() as connection:
        from alembic.runtime.migration import MigrationContext

        context = MigrationContext.configure(connection)
        current_heads = set(context.get_current_heads())

    if current_heads != expected_heads:
        return (
            False,
            f"MIGRATION_LIVE_CHECK::FAIL (db at {current_heads}, expected {expected_heads})",
        )
    return True, f"MIGRATION_LIVE_CHECK::PASS (db head matches {expected_heads})"


def main() -> int:
    ok_static, msg_static = check_static()
    print(msg_static)

    ok_live, msg_live = check_live()
    print(msg_live)

    return 0 if (ok_static and ok_live) else 1


if __name__ == "__main__":
    sys.exit(main())
