"""audit: AuditEvent contracts and append port.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : AuditEvent contracts and append port.
    May depend on      : semantic_types.
    Must not depend on : domain mutation.
    Canonical write    : append only.

PKG-12 SCOPE (Build Phase 4, "Audit and outbox contracts"):
    models.py -- AuditEvent (09 section 58's exact field list),
                 AuditRepository (append-only port; no update/delete
                 method exists on the Protocol at all).

`packages/persistence/audit_repository.py` implements the durable
storage for `AuditRepository`, depending on this package's types the
same one-directional way `persistence` already depends on `command`/
`domain`/`governance` -- this package still performs no direct write of
its own.
"""
