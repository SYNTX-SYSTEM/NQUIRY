"""commit: BND-014, transaction orchestration, mutation application.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : BND-014, transaction orchestration, mutation application.
    May depend on      : command, boundaries, persistence ports, audit, events.
    Must not depend on : frontend, provider SDK.
    Canonical write    : exclusive governed writer.

PKG-00 SCOPE NOTE: this build phase (Phase 0, "Repository and
architecture skeleton") materializes only the package boundary and
its place in the dependency-enforcement graph
(`scripts/check_architecture_dependencies.py`). No domain, authority,
or persistence behavior is implemented here. Implementation lands in
the build phase assigned to this package by
14_IMPLEMENTATION_SEQUENCE.md §46 (CODING PACKAGE MANIFEST).
"""
