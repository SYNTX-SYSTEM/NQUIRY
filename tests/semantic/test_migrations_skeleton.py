"""T0 semantic test: the Alembic pipeline is structurally valid.

14 §7/§9. This wraps `scripts/verify_migrations.py::check_static`,
which does not require a live database. As of PKG-01, migration
`001_semantic_identity_workspace` exists (14 §9); the check now proves
"single linear head, no branching" rather than "empty pipeline" (that
was the PKG-00/Phase-0 requirement — see git history for the prior
assertion).
"""

from __future__ import annotations

from verify_migrations import check_static


def test_migration_pipeline_is_a_single_linear_chain() -> None:
    ok, message = check_static()
    assert ok, message
