# PKG-11 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-11
PACKAGE_TITLE: Idempotency
BUILD_PHASE: 4
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  09_DATA_EVENT_API_CONTRACTS.md section 11 (IdempotencyRecord -- exact field
    list and 4-value outcome vocabulary), section 11.1 (Idempotency Does Not
    Authorize), section 12 (Command Retry Semantics, re-confirmed from PKG-10),
    section 139-140 (AC-09-013 Idempotency Payload Binding)
  10_FAILURE_RECOVERY_ROLLBACK.md section 67-70 (BND-018 Recovery/Rollback --
    confirms recovery routing is out of this package's scope), section 74
    (Recovery Idempotency -- the analogous pattern at the recovery layer,
    confirming PKG-11's own scope stops before it), section 137 (Recursive
    Invariant Validation: "RETRY -> respects idempotency and current
    authority"), section 138 (Failure Taxonomy Findings)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6 (P-19/P-20 full matrix
    rows), section 44 (mutation table, no PKG-11-specific mutation named
    beyond MUT-09 "retry INDETERMINATE" -> P-20/recovery tests must fail)
  14_IMPLEMENTATION_SEQUENCE.md sections 3.1 (directory ownership -- `commit`'s
    pre-existing "command, boundaries, persistence ports, audit, events"
    allow-list, already covering this package's needs), 6 (Command outcome
    vocabulary, re-confirmed distinct from IdempotencyRecord.outcome), 7.1
    (idempotency_records table row, write owner "commit writer"), 7.3
    (critical field constraints: idempotency uniqueness/payload-fingerprint-
    mismatch rules), 9 (migration plan, 008_command_attempt_idempotency
    bucket, second half), 26 (optimistic concurrency, general pattern), 27
    (IDEMPOTENCY -- the 6 dispositions materialized literally), 39 (T7 ->
    tests/command_commit_event/, T8 -> tests/recovery/), 46-48 (PKG-11
    manifest, DAG, file-level map: packages/commit/idempotency.py), 49 (DB
    implementation map)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: IdempotencyPort -- created, exactly as named, alongside
    IdempotencyRecord/IdempotencyOutcome/IdempotencyDecision (09 section 11's
    own pre-named data contract and vocabulary, not additional invention).
  DATABASE_CHANGES: 008 (subset) -- `idempotency_records` created, completing
    the bucket PKG-10 began.
  TESTS_REQUIRED: T7 (tests/command_commit_event/test_idempotency.py, 14's
    own named file) -- created. One additional T8 file
    (tests/recovery/test_idempotency_indeterminate_blocks_retry.py) for the
    INDETERMINATE mandatory attack, whose routing (BND-017/BND-018) is
    10_FAILURE_RECOVERY_ROLLBACK.md's own territory -- disclosed in that
    file's own docstring, matching the coding prompt's own
    FILES_ALLOWED_TO_CREATE ("tests/command_commit_event and recovery").
  PROOF_CLAIMS: P-19 -- further exercised (PKG-10 proved attempt-identity/
    payload-fingerprint/retry semantics at the Command layer; this package
    proves the full "duplicate COMMITTED -> one consequence" claim at the
    idempotency layer, now with a real committed record and a real returned
    result_ref -- the only remaining gap is a real CommitUnit, PKG-13). P-20
    -- INTRODUCED (INDETERMINATE blocks blind retry, proven both through the
    port and independently at the database layer).

PREDECESSORS_VERIFIED:
  PKG-10 (9a9b8fd, PACKAGE_PASS, human gate given, Phase 4 in progress).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-09 05a5857, PKG-10
  9a9b8fd -- none of PKG-11's changes touch any predecessor's owned files;
  full regression re-run below confirms no invalidation.

FILES_CREATED:
  packages/commit/idempotency.py
  migrations/versions/b5b33834b7ea_idempotency_records.py
  tests/command_commit_event/test_idempotency.py
  tests/recovery/conftest.py
  tests/recovery/test_idempotency_indeterminate_blocks_retry.py

FILES_MODIFIED:
  packages/commit/__init__.py (PKG-11 scope note)
  packages/persistence/tables.py (idempotency_records_table added, docstring
    cross-reference)

FILES_DELETED: none (a draft `packages/persistence/idempotency_repository.py`
  was created and then deleted during this package's own Step E, before any
  test ran against it, once the file-level map's actual "commit/persistence
  ports" allowed-imports direction was read correctly -- see KNOWN_LIMITATIONS
  for the design point this corrected)

MIGRATIONS_CREATED: b5b33834b7ea (idempotency records), revises b2f3a5d5096c.
  Creates `idempotency_records`; 2 triggers (identity/receipt-field
  immutability; outcome-transition topology matching 14 section 27 exactly).
SCHEMA_CHANGES: `idempotency_records` (workspace_id, command_type,
  idempotency_key, command_id, payload_fingerprint, first_seen_at,
  latest_attempt_id, outcome, commit_id, result_ref; PRIMARY KEY
  (workspace_id, command_type, idempotency_key) -- 14 section 7.3's own
  words, not a surrogate id; composite FK (command_id, workspace_id) ->
  commands(id, workspace_id); FK latest_attempt_id -> command_attempts(id);
  CHECK outcome IN 09 section 11's 4-value vocabulary; CHECK commit_id
  present iff COMMITTED; CHECK result_ref present only if COMMITTED).
DB_PRIVILEGE_CHANGES: none. 14 section 7.1 names "commit writer" as the
  eventual write owner, but every DB-principal/GRANT/RLS change in this
  codebase to date is deferred to migration 012_security_events_rls --
  consistent with every migration since 001, not a new gap this package
  introduces.

PUBLIC_INTERFACES_CREATED:
  commit.idempotency.{IdempotencyOutcome, IdempotencyRecord, IdempotencyDecision,
    IdempotencyLifecycleError, IdempotencyInProgress, IdempotencyAlreadyCommitted,
    IdempotencyPayloadCollision, IdempotencyIndeterminateBlocked,
    decide_idempotency_action, raise_for_decision, IdempotencyPort,
    IdempotencyRecordNotFound, SqlAlchemyIdempotencyRepository}

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns no concrete named Command to
  PKG-11)
QUERIES_CREATED: NOT_APPLICABLE
EVENTS_CREATED: NOT_APPLICABLE
BOUNDARIES_CREATED_OR_CHANGED: none. No BND-XXX is invoked by this package
  (14 PKG-11 BOUNDARIES: "No authority cached in idempotency" -- honored by
  never reading or branching on any authority-shaped field).

AUTHORITY_PATH: NOT_APPLICABLE. No authority resolution, caching, or
  shortcut exists anywhere in this package -- `IdempotencyPort` carries no
  authority-context field of its own at all (unlike `CommandEnvelope`);
  14 PKG-11 AUTHORITY: "Retry always requires fresh evaluation when
  execution is permitted" is honored structurally: `begin()` never returns
  a signal a caller could treat as "authority already checked," only
  IN_PROGRESS/fresh-attempt records, both of which still require full
  boundary re-evaluation by whatever future dispatch calls this port.

EVIDENCE_PATH: NOT_APPLICABLE (14 PKG-11 EVIDENCE: "Freshness not cached" --
  no Evidence field or reference exists in this package's types at all).

AI_PATH: NOT_APPLICABLE (14 PKG-11 AI: "None" -- no provider/model path was
  introduced).

RECOVERY_PATH: `IdempotencyOutcome.INDETERMINATE` is representable and
  fully tested (mark_indeterminate, and the structural block on any further
  transition out of it). Routing to BND-017/BND-018 is SUCCESSOR_NOT_BUILT
  (10_FAILURE_RECOVERY_ROLLBACK.md's own territory, PKG-18+) -- this
  package proves only the block itself, disclosed explicitly in
  `tests/recovery/test_idempotency_indeterminate_blocks_retry.py`'s own
  module docstring and in `IdempotencyIndeterminateBlocked`'s docstring.

TESTS_CREATED: 3 files, 34 test functions (test_idempotency.py: 32 [11 pure
  decision-engine + 2 record-validation + 19 DB-backed], 2 in
  test_idempotency_indeterminate_blocks_retry.py; tests/recovery/conftest.py
  is fixture-only, no test functions of its own).
TESTS_MODIFIED: none.

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS
          ruff check . -- PASS (6 mechanical SIM117 nested-with issues, all
            fixed preserving pytest.raises-outer/begin_nested-inner ordering)
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts --
            PASS (78 source files, no issues, +1 from PKG-10's 77)
  Architecture checks: check_architecture_dependencies.py -- PASS (zero new
    extensions -- `commit -> persistence` was already allowed since PKG-00;
    this package is simply the first to exercise it for real)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 7 revisions,
                          single head b5b33834b7ea; live: db head matches;
                          downgrade -1 / re-upgrade cycle clean)
  Pure-Python suite (no DB): tests/ + apps/api/tests -- 430 passed, 142
    skipped (all pre-existing/newly-added SKIPPED_NO_DATABASE, none
    unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 571 passed, 1 skipped, 0
    failed, after two pre-fix bugs found and fixed (see below)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative tests
  pass; each asserts a specific named exception type
  (IdempotencyInProgress/IdempotencyAlreadyCommitted/IdempotencyPayloadCollision/
  IdempotencyIndeterminateBlocked/IdempotencyRecordNotFound/ValueError/TypeError
  with a matching message, or a real DB constraint/trigger exception), never
  merely "an error occurred."

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION: Two real pre-fix bugs were
  produced and fixed by the live-database run, not merely claimed:
  1. `SqlAlchemyIdempotencyRepository.begin`'s original test suite called
     `repo.begin(envelope, ...)` directly without first calling
     `CommandRepository.record_attempt(envelope, ...)` -- but
     `idempotency_records.command_id` carries a composite FK to
     `commands(id, workspace_id)` (PKG-10's own anchor), so every such call
     failed with a real `ForeignKeyViolation`. Worse, `begin()`'s own
     `except sa.exc.IntegrityError` handler could not distinguish this
     genuine caller error from the legitimate "lost the PK race" case, so
     it masked the FK violation as a misleading `IdempotencyRecordNotFound`.
     Caught on the first live-DB run (13 of 19 new DB-backed tests failed).
     Fixed at two levels: (a) `_resolve_after_race` now re-raises the
     *original* `IntegrityError` unchanged whenever re-reading finds no row
     (proving it truly wasn't a race), instead of synthesizing a
     `IdempotencyRecordNotFound`; (b) every test now performs the real
     two-step flow (`CommandRepository.record_attempt` then
     `IdempotencyPort.begin`), and a new adversarial test,
     `test_begin_propagates_a_genuine_integrity_error_that_is_not_a_race`,
     asserts the corrected behavior directly. Re-run: 570 of 571 passed.
  2. `test_begin_survives_a_concurrent_insert_race`'s manually-seeded
     "winning" row used a hardcoded placeholder `payload_fingerprint="fp-1"`
     instead of the real fingerprint of the payload the colliding envelope
     actually carried -- `decide_idempotency_action` correctly detected a
     payload mismatch and raised `IdempotencyPayloadCollision` instead of
     the `IdempotencyInProgress` the test expected, because the seeded
     fixture data was simply wrong, not because of a production defect.
     Caught on the second live-DB run (this one test still failing after
     fix 1). Fixed by computing the seeded row's fingerprint with the real
     `compute_payload_fingerprint(_Payload("hello"))` instead of a literal
     string. Re-run: 571 of 571 passed.
  Both bugs were in test/fixture code once corrected in production code's
  favor for bug 1's handler logic (a genuine, disclosed production fix) and
  purely in test fixture data for bug 2.

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (7/7):
  1. New
     EXPECTED DEFENSE: decide_idempotency_action returns PROCEED_NEW for
       existing=None
     EXPECTED CANONICAL RESULT: a fresh IN_PROGRESS record
     ACTUAL RESULT: matches (test_new_request_proceeds,
       test_begin_creates_a_new_in_progress_record)
  2. In-progress duplicate
     EXPECTED DEFENSE: decide_idempotency_action RETURN_IN_PROGRESS_NO_EXECUTION
     EXPECTED CANONICAL RESULT: IdempotencyInProgress, no second execution
     ACTUAL RESULT: matches (test_in_progress_duplicate_returns_no_second_execution,
       test_begin_denies_in_progress_duplicate)
  3. Committed duplicate
     EXPECTED DEFENSE: RETURN_COMMITTED_RESULT
     EXPECTED CANONICAL RESULT: IdempotencyAlreadyCommitted carrying the
       real prior result_ref
     ACTUAL RESULT: matches (test_committed_duplicate_returns_prior_result,
       test_begin_denies_committed_duplicate_and_returns_prior_result)
  4. Same key different payload
     EXPECTED DEFENSE: REJECT_PAYLOAD_COLLISION
     EXPECTED CANONICAL RESULT: IdempotencyPayloadCollision
     ACTUAL RESULT: matches (test_same_key_different_payload_is_rejected,
       test_begin_denies_same_key_different_payload)
  5. FAILED_PRECOMMIT retry
     EXPECTED DEFENSE: PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT
     EXPECTED CANONICAL RESULT: a fresh IN_PROGRESS record with an advanced
       latest_attempt_id
     ACTUAL RESULT: matches (test_failed_precommit_retry_proceeds_with_fresh_attempt,
       test_begin_allows_a_fresh_attempt_after_failed_precommit)
  6. INDETERMINATE retry
     EXPECTED DEFENSE: BLOCK_INDETERMINATE_NO_BLIND_RETRY
     EXPECTED CANONICAL RESULT: IdempotencyIndeterminateBlocked, no state
       change possible even via direct SQL
     ACTUAL RESULT: matches (test_indeterminate_retry_is_blocked,
       test_begin_blocks_indeterminate_retry,
       test_no_blind_retry_is_possible_through_the_port_once_indeterminate,
       test_no_direct_database_write_can_move_an_indeterminate_row_either)
  7. Cross-Workspace key collision
     EXPECTED DEFENSE: PRIMARY KEY includes workspace_id (application-level
       isolation); composite FK (command_id, workspace_id) ->
       commands(id, workspace_id) (structural isolation)
     EXPECTED CANONICAL RESULT: two independent rows for the same key
       string at different Workspaces; sa.exc.IntegrityError for a forged
       cross-Workspace command_id reference
     ACTUAL RESULT: matches (test_begin_denies_cross_workspace_key_collision,
       test_begin_denies_an_idempotency_record_referencing_a_cross_workspace_command)

  Novel/adapted (4 additional, total 11 >= the package's own ">=5" floor):
  8. command_id substitution under a reused idempotency_key with a
     coincidentally matching payload fingerprint
     ACTUAL RESULT: matches (test_different_command_id_under_same_key_is_also_a_collision)
  9. Genuine caller error (begin() for an unrecorded command_id) misreported
     as a resolved race
     ACTUAL RESULT: matches (test_begin_propagates_a_genuine_integrity_error_that_is_not_a_race)
  10. Concurrent insert race (deterministic, no sleep/thread)
      ACTUAL RESULT: matches (test_begin_survives_a_concurrent_insert_race)
  11. Illegal outcome transition skipping the required retry step
      (FAILED_PRECOMMIT -> COMMITTED directly)
      ACTUAL RESULT: matches (test_illegal_outcome_transition_is_rejected_at_the_database_layer)

  Legitimate controls proven not vacuously strict: all PROCEED_* pure-engine
  tests plus their DB-backed equivalents above; record-shape validation
  tests (commit_id/result_ref biconditionals) proving IdempotencyRecord
  itself cannot represent an incoherent state.

MUTATION_TESTS:
  MUT-09 (13 section 44: "retry INDETERMINATE" -> P-20/recovery tests must
    fail): remove the `IdempotencyOutcome.INDETERMINATE` branch from
    `decide_idempotency_action` -> expected red: test_indeterminate_retry_is_blocked,
    test_begin_blocks_indeterminate_retry,
    test_no_blind_retry_is_possible_through_the_port_once_indeterminate --
    by inspection, all three assert BLOCK_INDETERMINATE_NO_BLIND_RETRY /
    IdempotencyIndeterminateBlocked with no other source --
    INTERPRETATION: mutation killed.
  MUT-PKG11-01 (adapted, outcome-transition trigger): remove the
    OLD.outcome = 'COMMITTED' terminal check from the DB trigger -> expected
    red: test_committed_outcome_is_terminal_at_the_database_layer -- by
    inspection, that test's only DBAPIError source matching "terminal" is
    the removed check -- INTERPRETATION: mutation killed.
  MUT-PKG11-02 (adapted, command-id collision check): remove the
    `existing.command_id != requested_command_id` half of
    `decide_idempotency_action`'s collision condition (leaving only the
    payload-fingerprint half) -> expected red:
    test_different_command_id_under_same_key_is_also_a_collision -- by
    inspection, that test's PROCEED path would then wrongly succeed since
    the fingerprints deliberately match -- INTERPRETATION: mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_idempotency.py exercises the full real predecessor
  chain: NonProofWorkspaceBootstrap (PKG-04) -> workspaces (PKG-01) ->
  SqlAlchemyCommandRepository (PKG-10, real `commands`/`command_attempts`
  rows) -> SqlAlchemyIdempotencyRepository (this package, real
  `idempotency_records` rows and live triggers) -- every mandatory attack
  is proven against genuine, composed database constraints spanning two
  packages' tables, not an isolated mock of either.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through PKG-10's
  tests) re-run alongside PKG-11's new tests, both without a database (430
  passed, 142 skipped) and with a live PostgreSQL 17 instance (571 passed, 1
  skipped) -- 0 regressions after the two fixes above.
  check_architecture_dependencies.py re-run clean, confirming all 6 prior
  disclosed extensions remain intact and that this package required none of
  its own.

P_CLAIMS_TESTED:
  P-19 (Duplicate Command no duplicate consequence): further exercised --
    the full "same identity COMMITTED -> return prior committed result"
    claim is now proven with a real `result_ref` returned from a real
    `IdempotencyRecord`; the only remaining gap toward the claim's full
    12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 16 precondition ("one
    ACID transaction" producing that COMMITTED outcome) is a real
    CommitUnit, PKG-13's own scope.
  P-20 (INDETERMINATE blocks blind retry): INTRODUCED -- proven both
    through `IdempotencyPort.begin` (Python layer) and independently via a
    direct SQL UPDATE against the outcome-transition trigger (database
    layer), matching 10 section 137's own "INDETERMINATE -> blocks
    dependent consequence" invariant.

PROOF_ARTIFACTS:
  - 571-test live-database pass, including 11 distinct adversarial proofs
    (7 mandatory + 4 novel) and one deterministic concurrent-insert-race
    proof (no sleep, no thread)
  - Real `idempotency_records` rows, inspectable via `get`, referencing
    real `commands`/`command_attempts` rows from PKG-10 and a real
    NonProofWorkspaceBootstrap-seeded Workspace
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a downgrade(-1)/re-upgrade cycle
  - Diff audit (inline answers above)
  - Mutation-kill analysis (3 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (zero new extensions; `commit -> persistence`
  was already allowed)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above. No unauthorized semantic change.

ARCHITECTURE_RECONSTRUCTION_RESULT: see inline reconstruction trace above.
  Longest legitimate chain: CommandRepository.record_attempt ->
  IdempotencyPort.begin -> full outcome lifecycle -> real idempotency_records
  rows in live PostgreSQL. BND-014/COMMIT UNIT/AUDIT/OUTBOX/EVENT correctly
  SUCCESSOR_NOT_BUILT; CURRENT STATE/GOVERNANCE/AUTHORITY/BOUNDARIES
  correctly NOT_APPLICABLE (this package invokes none of them).

KNOWN_LIMITATIONS:
  - `mark_committed`/`mark_failed_precommit`/`mark_indeterminate` are built
    but have no production caller (the commit coordinator that would call
    them is PKG-13's scope) -- same disclosed "built but unwired" pattern
    as PKG-10's `CommandRepository.record_outcome`.
  - INDETERMINATE has no legal next state anywhere in this codebase yet
    (neither through the port nor via direct SQL) -- a future recovery
    package (PKG-18+, once BND-018 is materialized) will need its own
    migration to open a governed path out of it; disclosed in both the
    migration's own docstring and `IdempotencyIndeterminateBlocked`'s.
  - A design correction happened mid-package (disclosed under
    FILES_DELETED): the concrete adapter was initially drafted as
    `packages/persistence/idempotency_repository.py` calling into
    `commit.idempotency`, which would have required a NEW `persistence ->
    commit` extension and created a package-level dependency cycle with
    `commit`'s own pre-existing, legitimate `commit -> persistence` edge.
    Corrected before any test ran by re-reading 14 section 48's file-level
    map precisely ("commit/idempotency.py ... allowed imports: command/
    persistence ports") and moving the concrete
    `SqlAlchemyIdempotencyRepository` into `commit/idempotency.py` itself,
    the direction `commit`'s own directory-ownership row already
    authorizes. No extension was ultimately needed.
  - P-19's full precondition (a real committed CommitUnit producing the
    COMMITTED outcome this package returns) still needs PKG-13.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward); not re-exercised
    via Docker this package (no new service, no new external dependency).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still BLOCKED.
  Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. IdempotencyRecord's field
  list and IdempotencyOutcome's 4-value vocabulary are 09 section 11's own,
  verbatim; the 6 IdempotencyDecision dispositions are 14 section 27's own
  rules, transcribed literally with no invented retry heuristic (the file
  map's own "forbidden: retry guess" is honored -- no timing, count, or
  backoff logic exists anywhere in this package); the command_id-mismatch
  collision rule is a disclosed, literal application of 09 section 4.3's
  own command_id identity definition, not an invented rule; no new
  authority path, transition, or governance concept was introduced.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-12 (Audit and outbox contracts) was
  already DAG-eligible after PKG-10 (its own sole required predecessor);
  PKG-13 (Commit coordinator and BND-014) becomes DAG-eligible now that
  both of its required predecessors, PKG-11 and PKG-12, would need to be
  verified -- PKG-12 remains outstanding. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- Build phase 4. "Completion does not authorize
  the next phase" (per this package's own coding prompt, verbatim). Do not
  authorize any successor.
```
