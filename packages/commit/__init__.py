"""commit: BND-014, transaction orchestration, mutation application.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : BND-014, transaction orchestration, mutation application.
    May depend on      : command, boundaries, persistence ports, audit, events.
    Must not depend on : frontend, provider SDK.
    Canonical write    : exclusive governed writer.

PKG-11 SCOPE (Build Phase 4, "Idempotency"):
    idempotency.py -- IdempotencyPort, IdempotencyRecord (09 section 11's
                       exact field list), IdempotencyOutcome (09 section
                       11's own 4-value closed vocabulary, distinct from
                       command.envelope.CommandOutcome -- see that
                       module's docstring), decide_idempotency_action
                       (pure decision engine implementing 14 section
                       27's 6 dispositions), and SqlAlchemyIdempotencyRepository
                       (the concrete durable adapter over `idempotency_records`
                       -- `commit`'s own directory-ownership row already
                       permits "persistence ports", so the adapter lives
                       here directly rather than in `persistence/`, the
                       opposite direction from `command`'s own split in
                       PKG-10; no new INTERNAL_ALLOWED extension was
                       needed for this package).

`coordinator.py` (BND-014, CommitUnit transaction orchestration) remains
PKG-13's scope -- nothing here performs a canonical mutation, resolves
authority, or evaluates a boundary.
"""
