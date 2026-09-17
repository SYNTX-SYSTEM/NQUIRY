"""application: use-case orchestration and Query/Command dispatch.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : use-case orchestration and Query/Command dispatch.
    May depend on      : public ports above.
    Must not depend on : ORM mutation, provider SDK.
    Canonical write    : no direct write.

PKG-01 SCOPE NOTE: `workspace_context.py` materializes "request
Workspace context" (14 PKG-01 OBJECTIVE) by pairing an
`AuthenticatedPrincipal` with a proven `WorkspaceRecord` read through
`persistence.WorkspaceRepository` (a `CanonicalReadPort` use, 14 §11 —
see `scripts/check_architecture_dependencies.py`'s `INTERNAL_ALLOWED`
extension for `application -> persistence`, read-only). No Command/
Query dispatch is implemented yet.
"""
