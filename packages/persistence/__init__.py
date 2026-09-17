"""persistence: PostgreSQL adapters implementing typed ports.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : PostgreSQL adapters implementing typed ports.
    May depend on      : semantic contracts.
    Must not depend on : UI semantics.
    Canonical write    : capability limited by DB principal.

PKG-01 SCOPE NOTE: `tables.py` and `workspace_repository.py` materialize
the read-only `WorkspaceRepository` (14 §10) over migration
`001_semantic_identity_workspace`. No governed mutation path exists
yet — Workspace creation is additionally blocked by `HARD-DEP-001`.
"""
