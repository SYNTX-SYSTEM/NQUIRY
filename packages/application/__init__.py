"""application: use-case orchestration and Query/Command dispatch.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : use-case orchestration and Query/Command dispatch.
    May depend on      : public ports above.
    Must not depend on : ORM mutation, provider SDK.
    Canonical write    : no direct write.

PKG-00 SCOPE NOTE: this build phase (Phase 0, "Repository and
architecture skeleton") materializes only the package boundary and
its place in the dependency-enforcement graph
(`scripts/check_architecture_dependencies.py`). No domain, authority,
or persistence behavior is implemented here. Implementation lands in
the build phase assigned to this package by
14_IMPLEMENTATION_SEQUENCE.md §46 (CODING PACKAGE MANIFEST).
"""
