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

PKG-13 SCOPE (Build Phase 4, "Commit coordinator and BND-014"):
    coordinator.py -- CommitCoordinator (14 PUBLIC INTERFACES), CommitUnit
                       (09 section 13's exact field list), CommitOutcome
                       (09 section 13's own 3-value closed vocabulary,
                       distinct from both command.envelope.CommandOutcome
                       and this package's own IdempotencyOutcome -- see
                       that module's docstring), FailureInjectionPort
                       (14 section 40's 11 named deterministic hook
                       points, as a production-importable Protocol --
                       the concrete deterministic double lives in
                       `test_support.failure_injector`, mirroring
                       `semantic_types.clock.Clock`/`test_support.clock.
                       FixedClock`). `packages/boundaries/bnd_014_commit.py`
                       implements the actual BND-014 evaluator this
                       package's coordinator holds and calls.
                       `packages/persistence/commit_repository.py`
                       implements the durable storage for
                       `CommitRepository`, a deliberate split from this
                       package (unlike PKG-11's single-file idempotency
                       design) -- 14 PKG-13's own FILES_ALLOWED_TO_CREATE
                       names them as two distinct creation targets.
"""
