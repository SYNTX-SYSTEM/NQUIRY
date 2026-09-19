# PKG-21 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-21
PACKAGE_TITLE: Projection and replay
BUILD_PHASE: 8
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  06_BOUNDARY_ARCHITECTURE.md section 13 (BND-007's own BYPASS PATHS
    list explicitly names "event consumer projection writing state" as
    a FORBIDDEN path -- all such attempts must pass BND-007/BND-014,
    which a projection consumer structurally cannot reach)
  09_DATA_EVENT_API_CONTRACTS.md section 15.2 (At-Least-Once Delivery --
    "must not produce duplicate consequential effects solely because
    delivery repeats"), section 18 (Event Replay Contract -- replay MAY
    "rebuild projections / reconstruct read models / verify histories";
    replay MAY NOT "invoke external side effects / submit new
    consequential Commands automatically / re-run AI tools as if newly
    authorized / advance canonical state"), section 123 (Query
    Projections -- "Session history" named as an approved projection),
    section 124 (InquiryGraph Query Materialization -- the full
    9-Thing/Relation graph, explicitly NOT this package's scope, see
    12 below)
  10_FAILURE_RECOVERY_ROLLBACK.md section 31/32 (RC-01 Deterministic
    Technical Recovery -- "rebuild projection from committed canonical
    state" named as a SYSTEM_SERVICE-eligible example; AC-10-005
    deterministic recovery authority)
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md ("Full Inquiry Graph | EXCLUDED |
    Projection semantics not required for proof"; "DEC-A001 | graph
    scope | later"; "Projection | DERIVED | Read model for event replay
    proof"; AC-12-016/AC-12-019: projection worker cannot mutate
    canonical state, replay proof is projection-only)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 39 (T7 ->
    tests/command_commit_event/, T11 -> tests/mutation/ -- this
    package's own file map instead assigns a package-scoped
    `tests/command_commit_event/mutation/` subdirectory, distinct from
    the top-level placeholder, see DIFF_AUDIT), P-17 matrix row
    (T13-P17-EVENT-REPLAY), AS-007 ("Projection remains
    non-authoritative")
  14_IMPLEMENTATION_SEQUENCE.md PKG-21 package manifest (BUILD_PHASE 8,
    UPSTREAM FILES 06/09/10/13/14, REQUIRED PREDECESSORS PKG-20, PUBLIC
    INTERFACES "ProjectionRepository", DATABASE CHANGES 010, TESTS
    REQUIRED T7/T11, PROOF CLAIMS P-17, BOUNDARIES "None created"),
    section 3.1 (`projection`'s exact allow-list: "events, projection
    persistence" -- no `domain`, no `authority`; `nquiry_worker`'s
    package-level ceiling), section 7.1 (core tables:
    `projection_checkpoints`/`session_read_model`/`inquiry_read_model`,
    each "Workspace key: yes"), section 8 (`projection_writer`
    principal: reads outbox/Event source, writes projection only,
    forbidden canonical/governance/Evidence writes), section 9
    (migration `010_projection`: "read models, checkpoints", depends
    on `009`, gate "rebuild tests"), section 10 ("ProjectionRepository:
    projection-only read/write"), section 41 ("event consumer cannot
    import direct consequential handler"), section 48 (file-level map
    names `packages/projection/consumer.py` exactly)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: "ProjectionRepository" -- materialized as
    `projection.models.{ProjectionRepository, SessionReadModel,
    InquiryReadModel, ProjectionCheckpoint}`, backed by the real
    `persistence.projection_repository.SqlAlchemyProjectionRepository`.
  DATABASE_CHANGES: 010 -- `projection_checkpoints`, `session_read_model`,
    `inquiry_read_model` created (migration `1bc6021cb651`, revises
    `7c2e8a4f1d6b`).
  TESTS_REQUIRED: T7/T11 -- `tests/command_commit_event/test_projection.py`
    (new, T7), `tests/command_commit_event/test_projection_worker.py`
    (new, T7), `tests/command_commit_event/mutation/test_projection_mutations.py`
    (new, T11 -- this package's own `FILES_ALLOWED_TO_CREATE` names
    this exact package-scoped subdirectory, distinct from the
    top-level `tests/mutation/` placeholder reserved for a later
    package's general mutation-runner tooling);
    `tests/security/test_projection_worker_exclusivity.py` added
    beyond the literal T7/T11 assignment for the dynamic P-17/
    section-41 proof, the same precedented extension PKG-19/20 each
    made to their own `tests/security/` files.
  PROOF_CLAIMS: P-17 -- see P_CLAIMS_TESTED below.
  BOUNDARIES: "None created" -- confirmed: no `boundaries` file
    created or modified this package.

PREDECESSORS_VERIFIED:
  PKG-20 (461d36a, PACKAGE_PASS -- Event and outbox worker, plus its
    own cleanup commit; `ed36c22` is PKG-20's own original commit,
    `461d36a` its disclosed follow-up).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-20's cleanup 461d36a.
  Only two predecessor files were touched, both explicitly disclosed
  extension points of this package's own scope (see FILES_MODIFIED);
  no architecture document was touched.

FILES_CREATED:
  packages/projection/models.py
  packages/projection/consumer.py
  packages/persistence/projection_repository.py
  apps/worker/src/nquiry_worker/projection_worker.py
  migrations/versions/1bc6021cb651_projection.py
  tests/command_commit_event/test_projection.py
  tests/command_commit_event/test_projection_worker.py
  tests/command_commit_event/mutation/test_projection_mutations.py
  tests/security/test_projection_worker_exclusivity.py

FILES_MODIFIED:
  packages/persistence/tables.py (`projection_checkpoints_table`,
    `session_read_model_table`, `inquiry_read_model_table` added;
    header docstring extended with the PKG-21 cross-reference, the
    same pattern every prior migration-adding package followed)
  scripts/check_architecture_dependencies.py
    (INTERNAL_ALLOWED["persistence"] += "projection", the one new
    disclosed extension this package needs -- see DIFF_AUDIT)

FILES_DELETED: none

MIGRATIONS_CREATED: 1bc6021cb651 (projection), revises 7c2e8a4f1d6b.
  Creates `projection_checkpoints` (composite PK
  `(projection_name, workspace_id)`, no surrogate id, mirroring
  `idempotency_records`' own precedent), `session_read_model` (real
  composite FK into `sessions(id, workspace_id)` -- the "corrupt
  projection" mandatory attack's own structural defense),
  `inquiry_read_model` (deliberately generic per-aggregate JSONB
  snapshot, NOT the full InquiryGraph -- see DIFF_AUDIT/KNOWN_LIMITATIONS).
  Full downgrade drops all three tables in dependency order; upgrade,
  downgrade(-1), re-upgrade cycle verified live.
SCHEMA_CHANGES: `projection_checkpoints`, `session_read_model`,
  `inquiry_read_model` (see above). No other table touched.
DB_PRIVILEGE_CHANGES: none. `projection_writer` (14 section 8) remains
  deferred to migration `012_security_events_rls`, consistent with
  every migration since `001`.

PUBLIC_INTERFACES_CREATED:
  projection.models.{ProjectionCheckpoint, SessionReadModel,
    InquiryReadModel, ProjectionRepository}
  projection.consumer.{ProjectionConsumer, session_aggregate_ref,
    projection_name_for, SESSION_PROJECTION_NAME, INQUIRY_PROJECTION_NAME}
  persistence.projection_repository.SqlAlchemyProjectionRepository
  nquiry_worker.projection_worker.{ProjectionWorker, ProjectionApplyResult}

COMMANDS_CREATED: NOT_APPLICABLE. 14 assigns no Command to this
  package.
QUERIES_CREATED: NOT_APPLICABLE.
EVENTS_CREATED: NOT_APPLICABLE. No new event contract -- this package
  is a CONSUMER of `events.envelope.EventEnvelope` (PKG-20), not a
  producer.

BOUNDARIES_CREATED_OR_CHANGED: none. 14's own BOUNDARIES line for this
  package is "None created" -- honored exactly.

AUTHORITY_PATH: "Projection never authority source" (14 PKG-21
  AUTHORITY). `projection`'s own 14 section 3.1 allow-list has no
  `authority`/`domain` entry, making this structurally impossible, not
  merely avoided by convention --
  `test_projection_package_never_imports_ai_or_authority_or_domain`
  scans the real production source and proves it directly.
  `current_state`/`snapshot` are plain string/JSONB mirrors of upstream
  truth, never consulted by any boundary or authority resolver.

EVIDENCE_PATH: "Projection Evidence views non-authoritative" (14 PKG-21
  EVIDENCE). No Evidence-shaped field exists on either read model;
  `projection` cannot import `evidence` (not on its own allow-list),
  making an "Evidence view" projection out of this package's own
  scope entirely -- disclosed, not built.

AI_PATH: "Replay cannot invoke AI" (14 PKG-21 AI). `projection`'s own
  allow-list excludes `ai_gateway`/`ai_contracts` --
  `test_projection_package_never_imports_ai_or_authority_or_domain`
  proves no file under `packages/projection/` imports either, and
  `test_projection_worker_imports_no_canonical_writer` proves the same
  for `apps/worker/src/nquiry_worker/projection_worker.py`. Mandatory
  adversarial attack "replay reruns AI": structurally impossible, not
  merely untested.

RECOVERY_PATH: "Projection failure does not alter canonical legitimacy"
  (14 PKG-21 FAILURE_RECOVERY). `ProjectionWorker`/`ProjectionConsumer`
  have no code path into `command`/`commit`/`persistence`'s own
  canonical writers at all (structural proof,
  `test_projection_worker_imports_no_canonical_writer` +
  `test_projection_worker_has_no_command_or_commit_repository_capability`).
  `ProjectionWorker.rebuild()` IS 10 section 31's own named RC-01
  example ("rebuild projection from committed canonical state"),
  proven end to end by `test_rebuild_wipes_and_replays_to_identical_state`.

TESTS_CREATED:
  tests/command_commit_event/test_projection.py: 15 test functions
    (6 pure, 9 DB-backed).
  tests/command_commit_event/test_projection_worker.py: 4 test
    functions (1 pure, 3 DB-backed).
  tests/command_commit_event/mutation/test_projection_mutations.py:
    3 test functions (1 pure, 2 DB-backed).
  tests/security/test_projection_worker_exclusivity.py: 6 test
    functions, all pure Python.
  Net new: 28 tests (14 pure, 14 DB-backed).
TESTS_MODIFIED: none. No previously-green test's own assumption was
  invalidated this package -- a second package in a row with zero
  predecessor-test fixes (after PKG-20), since no existing test ever
  asserted `packages/projection/` stayed empty (only a synthetic
  fixture-tree test in `tests/regression/test_architecture_dependency_checks.py`
  exercises a fake `projection` package name, unrelated to the real one).

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS (257 files)
          ruff check . -- PASS
          MYPYPATH=... mypy packages apps/api/src apps/worker/src
            scripts -- PASS (120 source files)
  Architecture checks: check_architecture_dependencies.py -- PASS (one
    new extension this package: persistence -> projection [18th
    disclosed extension overall], cited inline)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 15
                          revisions, single head 1bc6021cb651; live: db
                          head matches after full upgrade, plus a
                          downgrade(-1)/re-upgrade cycle verified live,
                          resulting schema inspected via psql)
  Pure-Python suite (no DB): tests/ -- 581 passed, 314 skipped (all
    SKIPPED_NO_DATABASE, none unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=15432): tests/ -- 894 passed, 1 skipped, 0 failed
    (866 baseline + 28 new; the 1 skip is the same pre-existing,
    unrelated skip carried since PKG-17)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative
  tests pass; each asserts a specific structured outcome (a
  `ValueError`/`TypeError`/database FK-violation with a matching
  message, or an exact `SessionReadModel`/`InquiryReadModel` equality),
  never merely "an error occurred."

ADVERSARIAL_TEST_RESULTS:
  Package-specific mandatory (6/6, 14 PKG-21's own list):
  1. ATTACK: Delete projection then rebuild
     EXPECTED DEFENSE: `reset_projection` wipes exactly one named
       projection's rows and checkpoint; `ProjectionWorker.rebuild()`
       then replays the full given history and reproduces IDENTICAL
       read-model state
     EXPECTED CANONICAL RESULT: unchanged -- rebuild touches only
       projection tables
     EXPECTED PROOF ARTIFACT: `SessionReadModel` equality before/after
       rebuild
     ACTUAL RESULT: matches (test_rebuild_wipes_and_replays_to_identical_state)
  2. ATTACK: Replay twice
     EXPECTED DEFENSE: a duplicate `event_id` redelivered through
       `ProjectionConsumer`/`ProjectionWorker.apply_batch` is a safe
       no-op at both the consumer and the repository layer
     EXPECTED PROOF ARTIFACT: unchanged `projection_version`
     ACTUAL RESULT: matches (test_consumer_is_idempotent_on_duplicate_event_id,
       test_replay_of_the_full_history_twice_does_not_duplicate)
  3. ATTACK: Corrupt projection
     EXPECTED DEFENSE: a `SessionReadModel` claiming a Workspace that
       does not match the real Session's own Workspace is rejected by
       the real composite foreign key
     EXPECTED PROOF ARTIFACT: `sa.exc.IntegrityError`
     ACTUAL RESULT: matches (test_session_read_model_rejects_cross_workspace_corruption)
  4. ATTACK: Use projection in authority/commit
     EXPECTED DEFENSE: `projection`'s own allow-list excludes
       `authority`/`domain`/`command`/`commit`; `ProjectionWorker`'s
       method surface carries no reference to any of them
     EXPECTED PROOF ARTIFACT: AST import scan +
       `inspect.signature(ProjectionWorker.__init__)`
     ACTUAL RESULT: matches (test_projection_package_never_imports_ai_or_authority_or_domain,
       test_projection_worker_has_no_command_or_commit_repository_capability)
  5. ATTACK: Replay tries Command
     EXPECTED DEFENSE: same structural exclusion as #4 -- no code path
       from replay back into `command`/`commit`
     EXPECTED PROOF ARTIFACT: AST import scan of
       `projection_worker.py`
     ACTUAL RESULT: matches (test_projection_worker_imports_no_canonical_writer)
  6. ATTACK: Replay reruns AI
     EXPECTED DEFENSE: `projection`'s own allow-list excludes
       `ai_gateway`/`ai_contracts`
     EXPECTED PROOF ARTIFACT: AST import scan
     ACTUAL RESULT: matches (test_projection_package_never_imports_ai_or_authority_or_domain)

  Novel/adapted (>=5 required for this package; 6 delivered, 12 total):
  7. ATTACK: Session-shaped and generic envelopes interleaved in one
       batch must update the correct read model and advance the
       correct, independent checkpoint each
     ACTUAL RESULT: matches
       (test_apply_batch_applies_in_order_and_advances_checkpoints_per_projection)
  8. ATTACK: A payload carrying no recognizable state information must
       never invent one
     ACTUAL RESULT: matches (test_consumer_preserves_state_when_payload_has_no_state_key)
  9. ATTACK: An already-DELIVERED-to-projection generic aggregate must
       be updatable to a new version, not stuck
     ACTUAL RESULT: matches (test_upsert_inquiry_read_model_creates_then_updates)
  10. ATTACK: Checkpoint must genuinely persist and monotonically
        advance across independent calls, not merely appear to
      ACTUAL RESULT: matches (test_checkpoint_advances_monotonically)
  11. ATTACK: Missing consumer-level idempotency guard alone (removing
        only ONE of two independent defense-in-depth layers)
      EXPECTED DEFENSE: the repository's own independent
        `last_event_id` guard still prevents corruption
      ACTUAL RESULT: matches -- the mutant does NOT corrupt the read
        model, confirming defense-in-depth
        (test_mut_pkg21_01_missing_consumer_guard_alone_does_not_survive,
        see MUTATION_TESTS below for the full interpretation)
  12. ATTACK: Missing repository-level idempotency guard (an
        unconditional-overwrite repository, bypassing the guarded
        adapter entirely)
      EXPECTED DEFENSE: none exists once this specific layer is
        removed with nothing else in the way -- this is the genuine,
        confirmed kill target
      ACTUAL RESULT: matches -- the mutant DOES let a stale replay
        overwrite with corrupted content
        (test_mut_pkg21_02_unguarded_repository_overwrite_is_killed)

MUTATION_TESTS:
  MUT-PKG21-01: remove ONLY the consumer-level idempotency guard from
    `ProjectionConsumer._apply_to_session_read_model` -> expected red
    (naive assumption): `test_consumer_is_idempotent_on_duplicate_event_id`.
    ACTUAL: the mutant does NOT corrupt the read model --
    `SqlAlchemyProjectionRepository`'s own independent guard catches
    the redelivery anyway.
    INTERPRETATION: defense-in-depth confirmed, not a surviving
    mutation and not a `TEST_DESIGN_DEFECT` -- the original test design
    assumed a single point of failure that this codebase's own
    deliberate two-layer guard does not have. The genuinely correct
    single-layer-removal kill target is MUT-PKG21-02.
  MUT-PKG21-02: an unconditional-overwrite repository bypassing the
    guarded `SqlAlchemyProjectionRepository` adapter entirely -> expected
    red: `test_upsert_session_read_model_is_idempotent_on_same_event_id`.
    ACTUAL: the mutant DOES let a stale replay overwrite with corrupted
    content.
    INTERPRETATION: mutation killed -- the repository-level guard is
    independently load-bearing.
  MUT-PKG21-03 (mandatory attacks: "replay tries Command"; "use
    projection in authority/commit"): a mutant `ProjectionWorker`
    subclass gaining a `command_repository` constructor parameter ->
    expected red:
    `test_projection_worker_has_no_command_or_commit_repository_capability`.
    ACTUAL: the mutant's own signature exposes the forbidden parameter,
    caught directly.
    INTERPRETATION: mutation killed.
  No prohibited mutation survived silently; MUT-PKG21-01's own
  non-survival is explicitly interpreted above rather than reported as
  a bare PASS, per 15's own "record: invariant removed or weakened,
  expected red test, actual result, and interpretation" requirement.

CROSS_LAYER_TEST_RESULTS: `tests/command_commit_event/test_projection_worker.py`
  exercises the full real predecessor chain: `NonProofWorkspaceBootstrap`
  (PKG-04) -> a real, directly-seeded `sessions` row (DRAFT, its legal
  initial state) -> real `SqlAlchemyProjectionRepository` (this
  package) -> real `ProjectionConsumer` (this package) -> real
  `ProjectionWorker` (this package) -> real `EventEnvelope` instances
  (PKG-20's own `build_event_envelope`, standing in for the disclosed
  `SUCCESSOR_NOT_BUILT` envelope-resolution gap PKG-20 already named,
  not a new gap this package introduces). Every FK/CHECK constraint
  exercised (`session_read_model`'s composite FK into `sessions`,
  `projection_checkpoints`' composite PK) is the real, live-PostgreSQL
  schema from this package's own migration, not a fixture double.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-20's tests) re-run alongside PKG-21's new tests, both without a
  database (581 passed, 314 skipped) and with a live PostgreSQL 17
  instance (894 passed, 1 skipped) -- 0 regressions, 0 previously-green
  tests required a fix this package (second in a row, after PKG-20).
  Architecture dependency/provider-SDK/test-only-import checks re-run
  clean.

P_CLAIMS_TESTED:
  P-17 (Replay cannot repeat consequence): closed for this package's
    own scope -- `test_rebuild_wipes_and_replays_to_identical_state`
    and `test_replay_of_the_full_history_twice_does_not_duplicate`
    prove a REAL projection consumer/worker rebuilding from a REAL,
    committed-shaped history reproduces identical state and never
    duplicates a consequential effect; the structural AST/signature
    proofs close "replay tries Command"/"replay reruns AI" completely
    for this package's own surface. PKG-20's own disclosed gap (no
    real `EventEnvelopeSource` reconstructing history from a bare
    `commit_id`) is NOT re-opened or re-disclosed here as a NEW gap --
    it is the same, already-named boundary this package's own
    `ProjectionWorker.apply_batch`/`rebuild` take an explicit
    `Sequence[EventEnvelope]` around, exactly like `OutboxWorker`'s own
    `EventEnvelopeSource` injection point.

PROOF_ARTIFACTS:
  - 894-test live-database pass, including 12 distinct adversarial
    proofs (6 mandatory package-specific + 6 novel/adapted)
  - A real `SessionReadModel` row rebuilt from a wiped state to
    byte-identical content via `ProjectionWorker.rebuild()`
  - A real FK-violation proof for a `SessionReadModel` claiming a
    Workspace that does not match its own Session's real Workspace
  - Three programmatic, executable mutation tests (a first for this
    codebase -- prior packages recorded mutation analysis as textual
    narration only), including one whose own first-draft assumption
    was falsified by the real code's defense-in-depth and was
    corrected, not weakened, before being reported
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full upgrade to head
    1bc6021cb651, a downgrade(-1)/re-upgrade cycle, and a `psql`
    schema inspection
  - Diff audit (inline answers below), cross-checked against `git
    status --short` before staging per this session's own explicit
    instruction to re-verify no incidental tooling/lock file is staged
  - Mutation-kill analysis (3 mutations, 2 killed, 1 correctly
    reinterpreted as defense-in-depth confirmation)

FORBIDDEN_DEPENDENCY_CHECK: PASS (one new, disclosed, cited extension:
  persistence -> projection, 18th overall)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: none. `SessionReadModel.current_state`/
    `InquiryReadModel.snapshot` are plain string/JSONB mirrors, never a
    closed vocabulary of their own; `checkpoint_version`/
    `projection_version` are plain ints, deliberately NOT a
    `RecordVersion` reuse (disclosed, not a new closed type either).
  New transition: none. No state-machine/trigger topology was touched
    or added; the two CHECK constraints added
    (`projection_version >= 1`, `checkpoint_version >= 0`) are simple
    non-negativity guards, not a transition topology.
  New authority path: none -- see AUTHORITY_PATH above.
  New DB write path: yes, disclosed -- exactly migration `010`'s own
    three tables, all `projection`-owned, none touching any canonical
    table for a write.
  Weakened boundary: none -- no boundary file touched at all.
  Easier test / removed negative test / admin shortcut / projection or
    cache truth / AI canonical authority / broader Workspace scope:
    none. (Projection is explicitly proven NEVER treated as
    authoritative -- AUTHORITY_PATH/EVIDENCE_PATH above.)
  Changed migration semantics: none -- no prior migration edited, only
    a new additive migration.
  Forbidden dependency: one new, disclosed, cited extension --
    persistence -> projection (18th overall). `projection`'s OWN
    allow-list is unchanged from its Phase-0 skeleton value
    (`{events, persistence, semantic_types}`), regression-tested by
    `test_persistence_projection_extension_is_the_only_new_architecture_dependency`.
  Files touched outside this package's own new-file set:
    `packages/persistence/tables.py`, `scripts/check_architecture_dependencies.py`
    -- both explicitly the concrete-adapter/architecture-configuration
    extension points this package's own new read port requires; no
    other predecessor file touched. `tests/command_commit_event/mutation/`
    is a NEW subdirectory this package's own `FILES_ALLOWED_TO_CREATE`
    explicitly names (distinct from the top-level `tests/mutation/`
    placeholder, left untouched). No previously-green test required a
    fix this package. One real mutation-test design defect was found
    and fixed DURING this package's own development, before any commit
    (see MUTATION_TESTS: MUT-PKG21-01's own reinterpretation) --
    disclosed as a corrected test assumption, not a production bug.
    Confirmed via `git status --short`, re-checked against this exact
    DIFF_AUDIT list before any `git add`, per this session's own
    explicit instruction: no `.claude/` or other tooling/lock file is
    present in the working tree changes (`.claude/scheduled_tasks.lock`
    exists on disk but is correctly excluded by the `.gitignore` entry
    PKG-20's own cleanup commit added).

ARCHITECTURE_RECONSTRUCTION_RESULT:
  REQUEST -> ACTOR: NOT_APPLICABLE (no HTTP-reachable request path in
  this package's own scope) -> WORKSPACE: real `WorkspaceId` carried on
  every read-model row and checkpoint -> CURRENT STATE: real,
  already-COMMITTED `sessions`/other canonical rows this package's
  consumer MIRRORS but never mutates -> CURRENT GOVERNANCE / CURRENT
  AUTHORITY / HUMAN DECISION: NOT_APPLICABLE (14 PKG-21 AUTHORITY:
  "Projection never authority source") -> EVIDENCE: NOT_APPLICABLE (no
  Evidence-shaped projection built) -> BOUNDARIES: NOT_APPLICABLE
  ("None created") -> BND-014: NOT_APPLICABLE (this package never calls
  `CommitCoordinator`) -> COMMAND: NOT_APPLICABLE (no Command assigned)
  -> COMMIT UNIT: NOT_APPLICABLE (read only, incidentally, via
  predecessor `EventEnvelope.commit_id`, never written by this package)
  -> CANONICAL MUTATION: NOT_APPLICABLE -- this package cannot reach
  one, by design and by structural proof -> AUDIT: NOT_APPLICABLE ->
  OUTBOX: NOT_APPLICABLE (this package consumes `EventEnvelope`s,
  never touches `outbox_events` directly) -> EVENT: real
  `EventEnvelope` (PKG-20), the sole input to this package's own
  pipeline -> RESULTING STATE: the real `session_read_model`/
  `inquiry_read_model`/`projection_checkpoints` columns, live-DB-joined
  and FK-proven, updated and REBUILT by the real `ProjectionWorker` for
  the first time in this codebase. This package's own longest
  legitimate chain runs EVENT -> PROJECTION APPLY -> RESULTING STATE
  (REBUILDABLE); every node upstream of EVENT is correctly
  `NOT_APPLICABLE` for a package whose own 14 manifest grants it no
  Command, no Boundary, and no canonical write at all -- the same
  shape PKG-20's own reconstruction took, one hop further downstream.

KNOWN_LIMITATIONS:
  - `inquiry_read_model` is a deliberately generic per-aggregate
    snapshot, NOT the full InquiryGraph 09 section 124 describes --
    12_MINIMUM_PROTOTYPE_ARCHITECTURE.md explicitly excludes that graph
    from this build's required proof ("DEC-A001 | graph scope | later").
    A future package building the full graph projection would need a
    new, dedicated data model and consumer logic; this package's own
    generic snapshot is not a partial implementation of it.
  - No production `EventEnvelopeSource` exists yet (PKG-20's own
    disclosed gap, unchanged) -- `ProjectionWorker.apply_batch`/
    `rebuild` therefore take an already-resolved
    `Sequence[EventEnvelope]` rather than reading live from the
    outbox/commit history. This package proves the projection
    MECHANICS; real end-to-end replay from actual production commits
    remains `SUCCESSOR_NOT_BUILT` until that gap closes.
  - Dispatch between `session_read_model`/`inquiry_read_model` is by an
    `aggregate_ref` string-prefix convention (`"session:<uuid>"`),
    disclosed as an `[IMPLEMENTATION CHOICE]` -- `projection` cannot
    import `domain.question_selection.session_target_ref` (the
    function that already establishes this exact format) since
    `projection`'s own allow-list excludes `domain`.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Neither is touched by this package's own scope (no AI path,
  no Workspace-governance-root bootstrap path).

NEW_GAPS_DISCOVERED: none new. The InquiryGraph exclusion and the
  EventEnvelopeSource gap above are both pre-existing, already-named
  scope boundaries (12's own DEC-A001; PKG-20's own disclosed
  limitation), not new discoveries. The mutation-test design correction
  (MUT-PKG21-01) was caught and fixed during this package's own
  development, before any commit -- disclosed under DIFF_AUDIT, not a
  gap in the architecture.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `SessionReadModel`/
  `InquiryReadModel`/`ProjectionCheckpoint`'s field shapes are this
  package's own minimal, disclosed design within 14 section 7.1's
  named table list -- no field claims a closed vocabulary or authority
  meaning 09/14 do not already assign elsewhere.
  `ProjectionRepository`/`ProjectionConsumer`/`ProjectionWorker`
  introduce no new Decision Right, authority class, transition,
  Command, Query, Boundary, or canonical write path. The full
  InquiryGraph is deliberately NOT built (12's own exclusion honored,
  not silently narrowed further or quietly expanded).

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-22 (Failure classification and
  certainty) becomes DAG-eligible now that both its required
  predecessors (PKG-13, PKG-20) are verified. Eligibility is not
  authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-21's own coding prompt: "Respect the
  phase boundary. Package completion does not authorize the next
  phase." Build Phase 8 (Event/Projection) is now FULLY COMPLETE across
  both its assigned packages (PKG-20, PKG-21). Do not authorize PKG-22
  (Phase 9) without explicit human authorization naming the package and
  this package's own commit hash.
```
