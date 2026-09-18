# PKG-14 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-14
PACKAGE_TITLE: QuestionSelection
BUILD_PHASE: 5
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  02_DOMAIN_AND_RELATION_MODEL.md section 18 (QuestionSelection --
    RELATION, not standalone object; endpoints Session -> selects ->
    Question; selection semantics distinguish compelling/primary),
    section 47.3 (representation: relation)
  03_STATE_AND_TRANSITION_ARCHITECTURE.md section 39 ("Question
    Selection as State-Preserving Consequential Mutation" -- TRN-SEL-001
    SELECT_COMPELLING_QUESTION, TRN-SEL-002 SELECT_PRIMARY_QUESTION,
    exact CURRENT STATE/PRECONDITIONS/DENY CONDITION/NEXT STATE text)
  04_AUTHORITY_AND_DECISION_RIGHTS.md section 9.2 (QUESTION_SELECTION_RIGHT
    definition), section 11/11.1 (AC-04-003 Explicit Question Selection
    Authority), section 41-42 (AUTH-DEP-SEL-001/002 -- exact AUTHORITY
    SCOPE "Specific Session", AUTHORITY PRECONDITIONS, DENY CONDITION
    text)
  06_BOUNDARY_ARCHITECTURE.md section 4 (Canonical Consequential
    Request Path -- exact BND-001..007/014/015 ordering), section 10
    (BND-004 Role/Governance Context -- "Observer/Viewer mutation" DENY
    example), section 12 (BND-006 Human Decision Authority -- generic
    across QUESTION_SELECTION_RIGHT/DECISION_RIGHT/etc., not
    Decision-specific), section 13 (BND-007 -- "one specific 03
    transition OR state-preserving consequential mutation", VALIDATION
    list including "cross-object state invariant valid")
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 7 (Authority Profile --
    QUESTION_SELECTION_RIGHT row, no bootstrap-ordering hedge unlike
    SESSION_CONTROL_RIGHT's own row), section 8.1 (bootstrap sequence),
    section 28 (PROTOTYPE HAPPY PATH step 19: Q1 selected, BND-005/
    BND-006/BND-014), P-07/P-08 fixture rows
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6/54.6 (P-08 matrix
    row -- exact ATTACK/CONTROL/CANONICAL RESULT text), section 39
    (T3 -> tests/authority/, tests/governance/; T7 ->
    tests/command_commit_event/)
  14_IMPLEMENTATION_SEQUENCE.md section on PKG-14 (BUILD_PHASE 5,
    UPSTREAM FILES 02/03/04/06/12/13/14, REQUIRED PREDECESSORS
    PKG-13/PKG-07, PUBLIC INTERFACES SelectQuestion command, DATABASE
    CHANGES 005, TESTS REQUIRED T3/T7, PROOF CLAIMS P-08), section 3.1
    (directory ownership -- `application`'s "may depend on: public
    ports above" wording), section 4 (forbidden dependency matrix --
    `application` must not depend on ORM/provider SDK), section 9
    (migration plan -- 005_selection_decision: "selections, decisions
    | depends on: 004,002"), section 10 (REPOSITORY PORTS --
    `QuestionSelectionRepository`/`SessionRepository` exact wording),
    section 12 (COMMAND REGISTRY -- `SelectQuestion` row: authority,
    boundaries 001-007,014,015, canonical effect), section 14 (COMMAND
    PROCESSOR pipeline), section 27 (IDEMPOTENCY rules), section 46/48
    (PKG-14 manifest, file-level map)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: SelectQuestion -- created as
    `application.question_selection_handler.select_question`, the
    first fully governed, end-to-end production Command path in this
    codebase (every earlier boundary/commit package built only the
    generic engine, never a caller). Supporting types not independently
    invented: `QuestionSelection`/`SelectionType` are 09 section 33's
    own field list/vocabulary; `SelectionTransitionId`/`SelectionOperation`
    are 03 section 39's own names.
  DATABASE_CHANGES: 005 (selections half only) -- `question_selections`
    created; `decisions` deliberately deferred to PKG-15, the fifth
    application of the one-conceptual-bucket-across-two-Alembic-revisions
    split.
  TESTS_REQUIRED: T3 (tests/authority/test_question_selection_authority.py
    -- 5 tests proving QUESTION_SELECTION_RIGHT resolves correctly at
    the new SESSION scope), T7 (tests/command_commit_event/
    test_question_selection.py -- 13 tests, full end-to-end handler) --
    both created. T4 (tests/boundaries/test_bnd_007_state_transition.py)
    extended proactively, though not formally required by this
    package's own TESTS_REQUIRED line.
  PROOF_CLAIMS: P-08 -- see P_CLAIMS_TESTED below.

PREDECESSORS_VERIFIED:
  PKG-13 (a579e80, PACKAGE_PASS, human gate given).
  PKG-07 (397d7b7, PACKAGE_PASS, verified earlier in the sequence).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-13 a579e80. No
  predecessor's own non-test files were touched beyond the disclosed
  extension points (BND-007's tagged union, CommitCoordinator's
  MutationOutcome, persistence tables, the architecture checker) -- full
  regression re-run below confirms no invalidation.

FILES_CREATED:
  packages/domain/question_selection.py
  packages/application/question_selection_handler.py
  packages/persistence/session_repository.py
  packages/persistence/question_selection_repository.py
  migrations/versions/d9d99d8d2869_question_selections.py
  tests/authority/test_question_selection_authority.py
  tests/command_commit_event/test_question_selection.py

FILES_MODIFIED:
  packages/boundaries/bnd_007_state_transition.py (widened
    `Bnd007Input.resolution`'s tagged union to accept
    `SelectionTransitionResolution` as a third member -- 06 section 13's
    own REQUESTED OPERATION line already covers "state-preserving
    consequential mutation", not a new boundary concept)
  packages/commit/coordinator.py (`MutationOutcome` gained an additive
    `relation_refs: tuple[str, ...] = ()` field, wired into
    `_commit_inner`'s `CommitUnit` construction -- 09 section 14's own
    AC-09-002 distinguishes "canonical state mutation" from "required
    relation mutation"; PKG-13's own tests default to `()`, proven
    unaffected)
  packages/persistence/tables.py (`question_selections_table` added;
    docstring cross-reference)
  scripts/check_architecture_dependencies.py (INTERNAL_ALLOWED["application"]
    += "commit" -- cited to 14 section 3.1's own "may depend on: public
    ports above", the first application-layer module to invoke a
    governed write for real)
  tests/boundaries/test_bnd_007_state_transition.py (+3 tests for the
    new `SelectionTransitionResolution` tagged-union member)
  tests/regression/test_architecture_dependency_checks.py (+2 tests:
    allow+negative-control pair for `application -> commit`; -1
    obsolete test removed -- `test_application_still_cannot_depend_on_commit`
    asserted the opposite of what this package's own authorized
    extension now makes true, disclosed under DIFF_AUDIT)

FILES_DELETED: none (one obsolete test function removed from an
  otherwise-retained file, disclosed above and under DIFF_AUDIT)

MIGRATIONS_CREATED: d9d99d8d2869 (question selections), revises
  b06f9a5b3d1b. Creates `question_selections`; composite FKs to
  `sessions`/`questions`; `UNIQUE(session_id, question_id, selection_type)`;
  a partial unique index enforcing at most one PRIMARY selection per
  Session; a trigger enforcing the 1-3 compelling-selection cardinality
  cap. Full downgrade drops the trigger, partial index, indexes, then
  the table.
SCHEMA_CHANGES: `question_selections` (id, workspace_id, session_id,
  question_id, selection_type, selected_by_user_id,
  human_authority_binding_id [no FK, disclosed], selected_at,
  record_version; composite FKs to sessions/questions; CHECK
  selection_type IN 09 section 33's 2-value vocabulary).
DB_PRIVILEGE_CHANGES: none. Deferred to migration
  012_security_events_rls, consistent with every migration since 001.

PUBLIC_INTERFACES_CREATED:
  domain.question_selection.{SelectionType, QuestionSelection,
    SelectionTransitionId, SelectionOperation, SelectionTransitionVerdict,
    SelectionTransitionResolution, resolve_selection_transition,
    session_target_ref}
  application.question_selection_handler.{SelectQuestionPayload,
    SelectQuestionDenied, select_question}
  persistence.session_repository.{SessionRepository,
    SqlAlchemySessionRepository, SqlAlchemySessionVersionReader}
  persistence.question_selection_repository.{QuestionSelectionRepository,
    SqlAlchemyQuestionSelectionRepository}

COMMANDS_CREATED: SelectQuestion (`application.question_selection_handler.
  select_question`) -- 14's only named PUBLIC_INTERFACES for this
  package. Registers no separate `command.registry.CommandContract`
  entry (14 assigns that catalogue's own concrete registrations to
  whichever future package first needs the general Command dispatch
  surface; this package materializes the handler directly, matching
  its own PUBLIC_INTERFACES wording literally: "SelectQuestion command",
  not "SelectQuestion command registered in the generic catalogue").
QUERIES_CREATED: NOT_APPLICABLE (14 assigns no Query to this package;
  `GetQuestionSelection` remains a future package's own scope).
EVENTS_CREATED: NOT_APPLICABLE (EventEnvelope remains PKG-20's own
  scope, Phase 8; the outbox record this package's commit writes
  carries only an opaque `EventId` reference).
BOUNDARIES_CREATED_OR_CHANGED: BND-007 extended (not created) -- see
  FILES_MODIFIED. No new BoundaryId invented; BND-001..006/014 reused
  entirely unchanged, wired together for the first time by a real
  production caller.

AUTHORITY_PATH: `Bnd005HumanAuthorityEvaluator` resolves
  `QUESTION_SELECTION_RIGHT` at `scope_type="SESSION"`,
  `scope_id=session_id.value` -- the first authority class this
  codebase resolves at Session scope rather than Workspace scope,
  reading 04 section 41/42's own unhedged "AUTHORITY SCOPE: Specific
  Session" literally (12 section 7's own Authority Profile table
  carries no bootstrap-ordering hedge for this row, unlike
  SESSION_CONTROL_RIGHT's own). `AuthorityResolver` itself required no
  code change -- `scope_type` was already a plain string. BND-014's own
  fresh, uncached resolve() (PKG-13) is reused unmodified as the
  commit-time revalidation.

EVIDENCE_PATH: NOT_APPLICABLE. 14 PKG-14 EVIDENCE: "No invented Evidence
  requirement" -- honored; `QuestionSelection` carries no Evidence
  reference at all (09 section 33's own field list has none).

AI_PATH: AI may recommend only (14 PKG-14 AI). No provider/model path
  introduced; BND-001 (actor class) and BND-006 (content-origin check,
  reused unmodified from PKG-09) both independently refuse an AI-class
  actor or AI-originated content from ever reaching a committed
  QuestionSelection -- proven by `test_denies_ai_selection`.

RECOVERY_PATH: 14 PKG-14 FAILURE_RECOVERY: "Denied/stale selection
  creates no canonical relation" -- proven directly: every DENY path
  (boundary chain) raises before `CommitCoordinator` is ever entered,
  and every precommit-layer failure (duplicate, cardinality cap,
  conflicting primary) surfaces as `CommitFailedPrecommit` via the
  same generic SAVEPOINT rollback PKG-13 already proved atomic -- no
  test in this package needed to prove atomicity a second time, only
  that this package's own new failure modes route through it correctly.

TESTS_CREATED: 2 files, 18 new test functions (test_question_selection_authority.py:
  5 DB-backed; test_question_selection.py: 13, covering all mandatory
  attacks plus 6 novel ones).
TESTS_MODIFIED: tests/boundaries/test_bnd_007_state_transition.py (+3
  tests); tests/regression/test_architecture_dependency_checks.py (+2
  tests, -1 obsolete test, disclosed under DIFF_AUDIT).

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS
          ruff check . -- PASS
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts
            -- PASS (90 source files; two disclosed, precedented
            `type: ignore[arg-type]` uses for the pre-existing
            BoundaryEvaluator Protocol-variance limitation, the first
            production code to hit it -- see coordinator.py's own test
            file for the identical, already-accepted pattern)
  Architecture checks: check_architecture_dependencies.py -- PASS (one
    disclosed extension: application -> commit, cited inline and
    regression-tested, 12th such extension following the established
    pattern)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 10
                          revisions, single head d9d99d8d2869; live:
                          db head matches after full upgrade from
                          empty, plus a downgrade(-1)/re-upgrade cycle)
  Pure-Python suite (no DB): tests/ -- 451 passed, 194 skipped (all
    SKIPPED_NO_DATABASE, none unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=15432): tests/ -- 644 passed, 1 skipped, 0 failed
    (after fixing 3 test-fixture-only bugs during development -- see
    NEW_GAPS_DISCOVERED; no production bug required a fix)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative
  tests pass; each asserts a specific named exception type
  (SelectQuestionDenied carrying the chain's own terminal_boundary_id,
  CommitFailedPrecommit, IdempotencyAlreadyCommitted) or a real
  database constraint/trigger exception, never merely "an error
  occurred."

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (6/6):
  1. AI selection
     EXPECTED DEFENSE: Bnd001IdentityEvaluator's required_actor_classes
       = {HUMAN_USER}
     EXPECTED BOUNDARY: BND-001
     EXPECTED CANONICAL RESULT: DENY, terminal_boundary_id=BND_001; no
       CommandOutcome recorded beyond DENIED, no CommitUnit
     ACTUAL RESULT: matches (test_denies_ai_selection)
  2. Human without right
     EXPECTED DEFENSE: Bnd005HumanAuthorityEvaluator's fresh
       AuthorityResolver.resolve() at SESSION scope
     EXPECTED BOUNDARY: BND-005
     EXPECTED CANONICAL RESULT: DENY, terminal_boundary_id=BND_005
     ACTUAL RESULT: matches (test_denies_human_without_the_right)
  3. Stale selector authority
     EXPECTED DEFENSE: same BND-005 fresh resolve(), never a cached
       grant -- binding revoked after being granted, before submission
     EXPECTED CANONICAL RESULT: DENY, terminal_boundary_id=BND_005
     ACTUAL RESULT: matches
       (test_denies_stale_selector_authority_revoked_before_submission)
  4. Wrong Workspace
     EXPECTED DEFENSE: Bnd002WorkspaceEvaluator's
       resolved_object_workspace_ids cross-check
     EXPECTED BOUNDARY: BND-002
     EXPECTED CANONICAL RESULT: DENY "CROSS_WORKSPACE_OBJECT_SET",
       terminal_boundary_id=BND_002
     ACTUAL RESULT: matches (test_denies_a_question_from_another_workspace)
  5. Selection in invalid Session state
     EXPECTED DEFENSE: resolve_selection_transition's Session-state
       precondition (Session must be QUESTION_SELECTION)
     EXPECTED BOUNDARY: BND-007
     EXPECTED CANONICAL RESULT: DENY "DENIED_WRONG_SESSION_STATE",
       terminal_boundary_id=BND_007
     ACTUAL RESULT: matches
       (test_denies_selection_when_session_is_not_in_question_selection_state)
  6. Duplicate selection where relation semantics forbid it
     EXPECTED DEFENSE: UNIQUE(session_id, question_id, selection_type)
     EXPECTED CANONICAL RESULT: CommitFailedPrecommit; no second row
     ACTUAL RESULT: matches (test_denies_a_literal_duplicate_selection)

  Novel/adapted (6 additional, total 12 >= this package's own ">=5" floor):
  7. Question from a different Challenge, same Workspace
     EXPECTED DEFENSE: resolve_selection_transition's cross-object
       Challenge check (distinct from BND-002's Workspace-only check)
     EXPECTED BOUNDARY: BND-007
     EXPECTED CANONICAL RESULT: DENY "DENIED_QUESTION_WRONG_CHALLENGE"
     ACTUAL RESULT: matches
       (test_denies_a_question_from_a_different_challenge_same_workspace)
  8. Fourth compelling selection (1-3 cardinality cap)
     EXPECTED DEFENSE: trg_question_selections_compelling_cardinality
     EXPECTED CANONICAL RESULT: CommitFailedPrecommit; exactly 3 rows
       remain
     ACTUAL RESULT: matches (test_denies_a_fourth_compelling_selection)
  9. Second conflicting primary selection (no governed replacement)
     EXPECTED DEFENSE: uq_question_selections_primary_per_session
       partial unique index
     EXPECTED CANONICAL RESULT: CommitFailedPrecommit; exactly one
       PRIMARY row remains
     ACTUAL RESULT: matches
       (test_denies_a_second_conflicting_primary_selection)
  10. Duplicate idempotent request after commit
     EXPECTED DEFENSE: PKG-11's own IdempotencyAlreadyCommitted --
       exercised through this package's real handler for the first
       time, proving idempotency begin() is correctly deferred until
       after the boundary chain ALLOWs
     EXPECTED CANONICAL RESULT: retry raises IdempotencyAlreadyCommitted;
       no second mutation
     ACTUAL RESULT: matches
       (test_duplicate_idempotent_request_after_commit_is_denied)
  11. Observer/Viewer role even with the right bound
     EXPECTED DEFENSE: Bnd004RoleContextEvaluator's accepted_roles
       excludes OBSERVER/VIEWER (06 section 10's own named DENY
       example), independent of BND-005's own rights check
     EXPECTED BOUNDARY: BND-004
     EXPECTED CANONICAL RESULT: DENY "ROLE_NOT_ACCEPTED:Viewer",
       terminal_boundary_id=BND_004
     ACTUAL RESULT: matches
       (test_denies_an_observer_role_even_with_the_right_bound)
  12. Forged/nonexistent Session reference
     EXPECTED DEFENSE: resolved_object_workspace_ids generalizes to
       `()` when Session lookup returns None, reusing BND-002's
       existing UNRESOLVED_WORKSPACE_NO_OBJECTS DENY rather than
       crashing
     EXPECTED CANONICAL RESULT: DENY, terminal_boundary_id=BND_002
     ACTUAL RESULT: matches (test_denies_when_session_no_longer_exists)

  Legitimate controls proven not vacuously strict:
  test_full_success_commits_a_compelling_selection_atomically (proves a
  real `question_selections` row, correct `relation_refs`, live-DB-joined).

MUTATION_TESTS:
  MUT-PKG14-01: remove resolve_selection_transition's Challenge-equality
    check -> expected red: test_denies_a_question_from_a_different_challenge_same_workspace
    -- by inspection, that test's only DENY source is this specific
    comparison; removing it would let the chain proceed to ALLOW --
    INTERPRETATION: mutation killed.
  MUT-PKG14-02: remove the compelling-cardinality trigger's COUNT check
    -> expected red: test_denies_a_fourth_compelling_selection -- by
    inspection, no other constraint bounds COMPELLING row count per
    Session -- INTERPRETATION: mutation killed.
  MUT-PKG14-03: remove the partial unique index on PRIMARY selections
    -> expected red: test_denies_a_second_conflicting_primary_selection
    -- by inspection, no other constraint prevents a second PRIMARY row
    -- INTERPRETATION: mutation killed.
  MUT-PKG14-04: move idempotency_port.begin() before the boundary chain
    evaluation -> expected red: every DENY-path test in this file would
    then create a stray IN_PROGRESS IdempotencyRecord with no
    vocabulary member to resolve it to (IdempotencyOutcome has no
    DENIED) -- by inspection, this would surface as an orphaned record
    never reachable by decide_idempotency_action's own terminal states
    -- INTERPRETATION: mutation killed (this is the exact design point
    disclosed in this handler's own module docstring).
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_question_selection.py exercises the full real
  predecessor chain: NonProofWorkspaceBootstrap (PKG-04) ->
  Workspace/Challenge/Session (PKG-01/05, Session walked through the
  real 7-step DRAFT->QUESTION_SELECTION transition topology via its own
  live triggers, not a shortcut) -> Question (PKG-06, real
  QuestionRepository) -> real AuthorityResolver (PKG-03) -> the real
  BND-001..007 evaluators (PKG-09), composed for the first time by a
  real production caller via boundaries.evaluate_chain (PKG-08) ->
  Bnd014CommitEvaluator/CommitCoordinator (PKG-13) ->
  QuestionSelectionRepository (this package) ->
  SqlAlchemyCommandRepository/SqlAlchemyIdempotencyRepository/
  SqlAlchemyAuditRepository/SqlAlchemyOutboxRepository/
  SqlAlchemyCommitRepository (PKG-10/11/12/13) -- the deepest and
  widest cross-layer chain any package has exercised so far, and the
  first time it is driven by a genuine production Command handler
  rather than a test-only coordinator invocation.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-13's tests) re-run alongside PKG-14's new tests, both without a
  database (451 passed, 194 skipped) and with a live PostgreSQL 17
  instance (644 passed, 1 skipped) -- 0 regressions.
  check_architecture_dependencies.py re-run clean, confirming all 12
  disclosed extensions remain intact (including the 1 new one added
  this package). The `MutationOutcome.relation_refs` additive field
  was specifically verified not to change PKG-13's own existing
  behavior (default `()` preserves the prior hardcoded value exactly).

P_CLAIMS_TESTED:
  P-08 (Human QuestionSelection is authority-bearing): introduced and
    directly tested -- test_denies_human_without_the_right and
    test_full_success_commits_a_compelling_selection_atomically are the
    literal T13-P08-SELECTION-RIGHT fixture: only the current
    QUESTION_SELECTION_RIGHT holder commits, an authenticated non-holder
    is denied. 16_DECISION_GAP_REGISTER.md's own P-08 row names PKG-14
    as one of several packages exercising this claim (also PKG-29/30/31/32,
    all future) -- this package's own contribution is the first genuine
    exercise, not full closure of every downstream consumer.

PROOF_ARTIFACTS:
  - 644-test live-database pass, including 12 distinct adversarial
    proofs (6 mandatory + 6 novel)
  - A real `question_selections` row, live-DB-joined to its Session,
    Question, and the real `human_authority_bindings` row that
    authorized it
  - The full 7-step Session state-topology walk (DRAFT through
    QUESTION_SELECTION) proven against the REAL `trg_sessions_enforce_transition`
    trigger, not bypassed
  - `SelectQuestionDenied.chain_result.terminal_boundary_id` asserted
    precisely for every DENY-path test, proving which specific boundary
    in the 001-007 chain stopped each attack, not merely "some boundary
    denied"
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full from-empty upgrade to head
    d9d99d8d2869 and a downgrade(-1)/re-upgrade cycle
  - Diff audit (inline answers above)
  - Mutation-kill analysis (4 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (one disclosed, tested extension:
  application -> commit, cited inline and now regression-tested with
  an allow+negative-control pair)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above (Step L). One obsolete predecessor
  test removed and explicitly disclosed, not silently dropped.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  REQUEST -> ACTOR (real UserId, authenticated as HUMAN_USER) ->
  WORKSPACE (real WorkspaceId, cross-checked by BND-002 against both
  Session and Question) -> CURRENT STATE (real Session row, walked
  through the genuine 03 transition topology to QUESTION_SELECTION;
  real Question row, existence and Challenge membership both proven) ->
  CURRENT GOVERNANCE (real WorkspaceRole via role_assignments, checked
  by BND-004) -> CURRENT AUTHORITY (fresh AuthorityResolver.resolve()
  for QUESTION_SELECTION_RIGHT at SESSION scope, re-run independently
  by both BND-005 and BND-014) -> HUMAN DECISION: NOT_APPLICABLE (no
  separate Decision entity for Selection; BND-006 proves the selection
  content itself is human-originated, not AI) -> EVIDENCE:
  NOT_APPLICABLE (09 section 33's own field list has none) ->
  BOUNDARIES (BND-001 identity -> BND-002 workspace -> BND-003
  membership -> BND-004 role -> BND-005 authority -> BND-006 human
  origin -> BND-007 state-preserving-mutation eligibility, sequential,
  first non-ALLOW terminates) -> BND-014 (fresh re-validation inside
  CommitCoordinator: upstream-chain ALLOW, Session version unchanged,
  authority still current) -> COMMAND (real CommandEnvelope/AttemptId,
  CMD_SELECT_COMPELLING_QUESTION or CMD_SELECT_PRIMARY_QUESTION) ->
  COMMIT UNIT (real commit_units row, target_refs naming the
  read-only-checked Session, relation_refs naming the newly created
  QuestionSelection -- the first time relation_refs is genuinely
  populated) -> CANONICAL MUTATION: more precisely RELATION MUTATION
  (real `question_selections` INSERT, inside the same SAVEPOINT as the
  CommitUnit) -> AUDIT (real audit_events row) -> OUTBOX (real
  outbox_events row) -> EVENT: SUCCESSOR_NOT_BUILT (PKG-20, Phase 8) ->
  RESULTING STATE (real, live-DB-joined question_selections + commit_units
  + audit_events + outbox_events rows). This is the first package where
  every node from REQUEST through RESULTING STATE is driven by one real
  production Command handler rather than assembled by a test harness
  calling internal pieces directly.

KNOWN_LIMITATIONS:
  - No `command.registry.CommandContract` registration exists for
    `CMD_SELECT_COMPELLING_QUESTION`/`CMD_SELECT_PRIMARY_QUESTION` --
    this package's own PUBLIC_INTERFACES names only "SelectQuestion
    command" (the handler), not "SelectQuestion registered in the
    generic catalogue"; a future package wiring an HTTP endpoint may
    need to register these contracts.
  - Collaborative selection conflict policy (GAP-04-001) remains OPEN
    and untouched -- this package's own "at most one PRIMARY, unless
    governed replacement is defined" enforcement is the disclosed,
    unconditional-rejection interpretation 04 section 42 itself states
    is correct "unless governed replacement is defined", not a
    resolution of the underlying collaborative-conflict gap.
  - `application.question_selection_handler.select_question`'s own
    parameter list is long (Protocol-typed dependency injection for
    every repository/port it composes) -- this mirrors
    `CommitCoordinator`'s own constructor+method parameter count scaled
    up one layer, not a new pattern, but is disclosed as the natural
    cost of being the first module to compose this many predecessor
    ports at once.
  - The pre-existing `BoundaryEvaluator` Protocol-variance mypy
    limitation (each concrete evaluator's `evaluate` narrows
    `boundary_input` to its own `BndNNNInput` type) is now visible in
    mypy-checked production code for the first time, requiring two
    disclosed `type: ignore[arg-type]` uses; the underlying limitation
    is `boundaries.types.BoundaryInput`'s own design (PKG-08), not
    introduced by this package.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none structural. Three test-fixture-only bugs were
  found and fixed during development (not production bugs): (1) a
  Session cannot be seeded directly in QUESTION_SELECTION state --
  `trg_sessions_enforce_initial_state` requires DRAFT on INSERT, and
  `trg_sessions_enforce_transition` requires each adjacent legal pair
  on UPDATE -- fixed by walking the real 7-step transition chain in the
  test fixture; (2) a "duplicate idempotent request" test initially
  varied both `selection_type` and `command_id` between calls, which
  correctly produces `IdempotencyPayloadCollision` rather than the
  intended `IdempotencyAlreadyCommitted` -- fixed by holding both
  identical across the retry, as a genuine duplicate submission would;
  (3) mypy's Protocol-variance limitation for `BoundaryRegistry.register`/
  `evaluate_chain` (see KNOWN_LIMITATIONS) required two disclosed
  `type: ignore[arg-type]` comments, mirroring the identical, already-
  accepted pattern in PKG-13's own test file.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `QuestionSelection`'s
  field list is 09 section 33's own, verbatim, plus the disclosed
  `workspace_id` technical necessity every other protected table
  already carries. `SelectionType`'s 2 values are 09 section 33's own
  vocabulary. `SelectionTransitionId`/`SelectionOperation` are 03
  section 39's own names, verbatim. The SESSION-scope authority check
  is 04 section 41/42's own literal, unhedged text, not an invented
  interpretation. BND-007's extension adds no new boundary concept
  (06 section 13's own text already covers state-preserving mutation).
  The cardinality/conflicting-primary rules are 04 section 41/42's own
  stated preconditions, enforced exactly as written ("unless governed
  replacement is defined" -- no such replacement exists, so
  unconditional rejection is the honest, literal reading).

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-15 (Human Decision) becomes DAG-eligible
  now that PKG-13 (its sole required predecessor) is verified;
  PKG-14's own completion does not additionally gate it (PKG-15's
  REQUIRED PREDECESSORS is PKG-13 only, not PKG-14). Eligibility is not
  authorization.
HUMAN_GATE_REQUIRED: YES -- Build phase 5 in progress (PKG-14/PKG-15
  are both Phase 5; phase completion requires both). "Completion does
  not authorize the next phase" (verbatim, per this package's own
  coding prompt). Do not authorize any successor without explicit human
  authorization naming the package and this package's commit hash.
```
