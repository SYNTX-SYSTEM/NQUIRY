"""T0 semantic test: the Alembic pipeline is structurally valid and empty.

14 §7/§9: "No domain tables... empty Alembic pipeline only" at Phase 0.
This wraps `scripts/verify_migrations.py::check_static`, which does not
require a live database.
"""

from __future__ import annotations

from verify_migrations import check_static


def test_migration_pipeline_is_empty_at_phase_0() -> None:
    ok, message = check_static()
    assert ok, message
    assert "empty pipeline" in message
