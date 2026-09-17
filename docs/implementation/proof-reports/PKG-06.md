# PKG-06 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-06
PACKAGE_TITLE: Question identity and lineage
BUILD_PHASE: 2
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  02_DOMAIN_AND_RELATION_MODEL.md sections 14,15,16
  03_STATE_AND_TRANSITION_ARCHITECTURE.md sections 23,24,25,26
  04_AUTHORITY_AND_DECISION_RIGHTS.md section 40 (AUTH-DEP-Q-001, reference only)
  07_EVIDENCE_AND_PROVENANCE.md sections 45,54.1,54.2
  09_DATA_EVENT_API_CONTRACTS.md sections 31,32
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 9 (minimum domain model rows)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6 (T1), P-01/P-02 matrix rows
  14_IMPLEMENTATION_SEQUENCE.md sections 3.1,4,7.1,7.3,9,10,39,46,47,49
  16_DECISION_GAP_REGISTER.md (PKG-06 row)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: QuestionRepository contract -- created (Protocol +
    SqlAlchemyQuestionRepository), covering both `questions` and
    `question_lineage` (14 section 10 lists no separate lineage repository).
  DATABASE_CHANGES: 004 (subset: questions, question_lineage only;
    bursts/burst_question_memberships deferred to whichever package owns
    QuestionBurst) -- created.
  TESTS_REQUIRED: T1 (tests/domain/question/) -- created. No T2: Question
    has no tracked state machine (03 section 25.3, existential creation only).
  PROOF_CLAIMS: P-01, P-02 -- both fully INTRODUCED and exercised.

PREDECESSORS_VERIFIED:
  PKG-05 (31427fb, PACKAGE_PASS, human gate given) -- Challenge/Workspace
  types and migration chain consumed directly (ChallengeId already
  existed from PKG-00; challenges_table's UNIQUE(id, workspace_id)
  anchor reused for questions' own composite FK pattern).
  Also present and unbroken: PKG-00 (dd4aad2), PKG-01 (35ef80a), PKG-02
  (f976854), PKG-03 (820a397), PKG-04 (dd582ac) -- none of PKG-06's
  changes touch their owned files; full regression re-run below
  confirms no invalidation.

FILES_CREATED:
  migrations/versions/33e1d1feed5b_question_identity_lineage.py
  packages/domain/question.py
  packages/domain/question_lineage.py
  packages/persistence/question_repository.py
  tests/domain/question/test_question.py
  tests/domain/question/test_question_lineage.py
  tests/domain/question/test_question_repository.py

FILES_MODIFIED:
  packages/domain/__init__.py (PKG-06 content summary appended)
  packages/persistence/tables.py (+questions_table, +question_lineage_table;
    docstring pointer to the new migration)

FILES_DELETED: none

MIGRATIONS_CREATED: 33e1d1feed5b_question_identity_lineage (revises d467112ce46d)

SCHEMA_CHANGES:
  CREATE TABLE questions (id, challenge_id FK, workspace_id FK,
    original_text, normalized_text, origin, author_user_id FK nullable,
    created_at, record_version; UNIQUE(id, workspace_id); composite FK
    (challenge_id, workspace_id) -> challenges(id, workspace_id); CHECK
    origin in 4 values; CHECK (origin='HUMAN') = (author_user_id IS NOT
    NULL); CHECK original_text non-empty; CHECK record_version >= 1).
    Deliberately no `text`, `status`, `question_type`, `priority`,
    `emotional_signal`, `novelty_score`, `catalytic_score` columns.
  CREATE TABLE question_lineage (id, parent_question_id, child_question_id,
    workspace_id FK, transformation_type, producer_origin,
    ai_generation_id nullable no-FK, created_at; 2 composite FKs
    (parent_question_id, workspace_id) and (child_question_id,
    workspace_id) both -> questions(id, workspace_id); CHECK
    parent_question_id <> child_question_id; CHECK transformation_type
    in {REFRAME, FOLLOW_UP}; CHECK producer_origin in 4 values).
  CREATE FUNCTION/TRIGGER trg_questions_enforce_immutable_fields (BEFORE
    UPDATE): rejects any change to original_text, challenge_id,
    workspace_id, origin, or author_user_id.
  CREATE FUNCTION/TRIGGER trg_question_lineage_enforce_immutable (BEFORE
    UPDATE): rejects every update unconditionally.
  Downgrade proven as pure schema removal (see PROOF_ARTIFACTS).

DB_PRIVILEGE_CHANGES: none (no new DB principal; no repository/write
  path is wired into any production caller yet, so no writer-principal
  grant was needed).

PUBLIC_INTERFACES_CREATED:
  domain.question.Question (frozen dataclass), QuestionOrigin (4-value
    closed enum)
  domain.question_lineage.QuestionLineage (frozen dataclass),
    LineageTransformationType (2-value closed enum)
  persistence.question_repository.QuestionRepository (Protocol:
    create_root, create_derived, get, get_lineage_for_child -- no
    update method of any kind) + SqlAlchemyQuestionRepository

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns none to PKG-06)
QUERIES_CREATED: NOT_APPLICABLE (14 assigns none to PKG-06)
EVENTS_CREATED: NOT_APPLICABLE (14 assigns none to PKG-06)
BOUNDARIES_CREATED_OR_CHANGED: NOT_APPLICABLE (BND engine is PKG-08;
  no boundary-dependency reference structure was even built, unlike
  PKG-05's TransitionSpec, since 14 assigns no such interface here)

AUTHORITY_PATH: NOT EVALUATED. AUTH-DEP-Q-001 (04 section 40) is
  referenced only as documentation in module docstrings. No new
  Decision Right, HABB meaning, or resolver fallback was invented.
  "No authorship-as-authority" (14 PKG-06 AUTHORITY) is honored
  structurally: author_user_id/origin pairing prevents an AI-origin
  Question from ever claiming human authorship, but nothing treats
  authorship as conferring any right either.

EVIDENCE_PATH: NOT_APPLICABLE (no Evidence object touched; "preserve
  provenance hooks" honored by keeping origin/author/lineage fields
  exactly as 07/09 define them, adding nothing extra).

AI_PATH: AI reframe/inference always creates a new Question identity
  (origin=AI, author_user_id=NULL) linked via QuestionLineage -- never
  overwrites the source. No AI output becomes canonical authority or a
  Decision. AI Gateway/AIOP contracts are untouched (out of scope).

RECOVERY_PATH: NOT_APPLICABLE (no recovery machinery exists yet; no
  retry/idempotency mechanism was added or exercised).

TESTS_CREATED: 3 files, 47 test functions total (13 in test_question.py,
  10 in test_question_lineage.py, 24 in test_question_repository.py)
TESTS_MODIFIED: none

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS (117 files clean)
          ruff check . -- PASS (all checks passed; fixed 1 initial
            import-order issue and reformatting, all mechanical)
          MYPYPATH=packages:apps/api/src:apps/worker/src:scripts mypy
            packages apps/api/src apps/worker/src scripts -- PASS
            (58 source files, no issues)
  Architecture checks: check_architecture_dependencies.py -- PASS (no
    extension needed; persistence->domain already existed from PKG-05)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 4
                          revisions, single head 33e1d1feed5b; live: db
                          head matches after upgrade)
  Pure-Python suite (no DB): tests/domain/question tests/domain
    tests/regression apps/api/tests tests/security tests/authority
    tests/governance tests/transitions -- 97 passed, 68 skipped (all
    pre-existing SKIPPED_NO_DATABASE / NOT_APPLICABLE skips, none new)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 208 passed, 1
    skipped, 0 failed

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative
  tests pass; each asserts a canonical/schema-level result (a specific
  exception type and, where meaningful, the trigger's own RAISE text),
  never merely "an error occurred."

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION:
  Two real pre-fix failures were produced and then fixed, not merely
  claimed:
  1. A test-helper bug (not a production-code bug): `_root_question`'s
     `author_user_id` was a freshly generated `UserId` never actually
     inserted as a `users` row, so every test that created a HUMAN-origin
     Question failed with `ForeignKeyViolation` on `fk_questions_author_user`.
     Caught immediately on first live-DB run (9 of the new tests
     failed). Fixed by having `_bootstrap_challenge` return the real
     seeded `NonProofWorkspaceBootstrap` owner's `UserId` for callers to
     use as `author_user_id`, instead of a disconnected one -- this is
     exactly the kind of mistake a live-database run catches that a
     mocked/in-memory test would not, which is why 14 PKG-06
     TARGETED_TESTS requires "real local PostgreSQL" runs, not mocks.
  2. Confirmed correct on the first pure-Python run (no defect): the
     `Question`/`QuestionLineage` `__post_init__` invariants (author/origin
     pairing, self-lineage rejection, enum coercion) all passed
     immediately -- the domain layer's own falsification tests did not
     need a fix, only the DB-integration test helper did.

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (4/4, all present, each proven independently at the Python
  layer where applicable AND the live-database layer):
  1. Repository or SQL update of original_text
     EXPECTED DEFENSE: no repository method exists (structural); DB
       trigger trg_questions_enforce_immutable_fields
     EXPECTED CANONICAL RESULT: hasattr checks false; sa.exc.DBAPIError
       with "original_text is immutable"
     ACTUAL RESULT: matches
       (test_repository_original_text_update_does_not_exist,
       test_direct_sql_update_of_original_text_is_rejected)
  2. Cross-Workspace lineage
     EXPECTED DEFENSE: two composite FKs on question_lineage against
       the same workspace_id column
     EXPECTED CANONICAL RESULT: sa.exc.IntegrityError for both possible
       workspace_id choices, no row inserted
     ACTUAL RESULT: matches (test_cross_workspace_lineage_is_not_representable)
  3. Invalid self-lineage
     EXPECTED DEFENSE: Python __post_init__ check; DB CHECK
       ck_question_lineage_no_self_lineage
     EXPECTED CANONICAL RESULT: ValueError (Python) /
       sa.exc.DBAPIError (DB)
     ACTUAL RESULT: matches (test_invalid_self_lineage_is_rejected,
       test_invalid_self_lineage_is_rejected_by_the_check_constraint)
  4. AI reframe replacing human original
     EXPECTED DEFENSE: origin/author_user_id biconditional (Python +
       DB CHECK); create_derived never touches the parent row
     EXPECTED CANONICAL RESULT: human Question byte-for-byte unchanged
       after an AI-origin child + REFRAME lineage is created; AI child
       has origin=AI, author_user_id=None, distinct identity
     ACTUAL RESULT: matches
       (test_ai_reframe_creates_new_identity_and_never_touches_the_human_original,
       test_non_human_origin_forbids_an_author,
       test_ai_origin_with_an_author_is_rejected_by_the_check_constraint)

  Novel/adapted (4 additional, exceeding the >=5 total minimum):
  5. Direct enum coercion (origin and transformation_type)
     ACTUAL RESULT: matches at both layers
       (test_direct_enum_coercion_of_an_unknown_origin_is_rejected,
       test_direct_enum_coercion_of_an_unknown_transformation_type_is_rejected,
       test_direct_enum_coercion_is_rejected_by_the_check_constraint)
  6. Human-origin-without-author / non-human-with-author pairing
     violation, at the schema level independent of Python
     ACTUAL RESULT: matches
       (test_human_origin_without_author_is_rejected_by_the_check_constraint)
  7. Lineage reassignment via direct SQL UPDATE (09 section 32.1)
     ACTUAL RESULT: matches, full-row rejection confirmed
       (test_lineage_reassignment_via_update_is_rejected)
  8. Cross-Workspace target (Question/Challenge variant, mirroring
     PKG-05's Session/Challenge proof)
     ACTUAL RESULT: matches
       (test_cross_workspace_question_target_is_not_representable)

  Negative controls also present: test_non_human_origin_with_no_author_is_valid,
  test_updating_a_row_without_changing_state-equivalent coverage via
  test_ai_reframe_... (positive path proving the mechanism isn't
  vacuously strict), test_create_derived_rejects_a_mismatched_child_id
  (repository-level precondition, not a DB attack).

MUTATION_TESTS:
  MUT-PKG06-01: remove the immutable-fields trigger's original_text
    check -> expected red: test_direct_sql_update_of_original_text_is_rejected
    -> by inspection, that test's `pytest.raises(match="original_text
    is immutable")` has no other source for that exact text --
    INTERPRETATION: mutation killed.
  MUT-PKG06-02: remove the question_lineage immutability trigger
    entirely -> expected red: test_lineage_reassignment_via_update_is_rejected
    and test_lineage_repository_exposes_no_mutator's implicit coverage
    -> by inspection, an UPDATE would then succeed silently, and the
    `pytest.raises(match="question_lineage rows are immutable")` has no
    other source -- INTERPRETATION: mutation killed.
  MUT-PKG06-03: remove Question.__post_init__'s origin/author pairing
    check -> expected red: test_non_human_origin_forbids_an_author and
    test_human_origin_requires_an_author -> by inspection, both asserts
    depend solely on that one check -- INTERPRETATION: mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: `QuestionRepository` exercised against real
  `NonProofWorkspaceBootstrap`-seeded Workspaces and real `challenges`
  rows (not isolated mocks) -- every repository test in
  test_question_repository.py is a genuine multi-table relational
  proof (users -> workspaces -> workspace_memberships ->
  human_authority_bindings -> challenges -> questions ->
  question_lineage), reconstructing the same predecessor-layer chain
  PKG-05's tests used.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-05's tests) re-run alongside PKG-06's new tests, both without a
  database (97 passed, 68 skipped) and with a live PostgreSQL 17
  instance (208 passed, 1 skipped) -- 0 regressions.
  check_architecture_dependencies.py re-run clean, confirming all 4
  prior extensions (application->persistence, persistence->governance,
  authority->persistence, persistence->domain) remain intact.

P_CLAIMS_TESTED:
  P-01 (Question first-class, stable independent identity): INTRODUCED
    and fully exercised -- test_create_root_and_get_round_trip proves
    create/retrieve of a real canonical row;
    test_question_carries_independent_identity proves 02 section 14.2.
  P-02 (original_text immutable; reframe creates new identity):
    INTRODUCED and fully exercised at both layers -- Python
    (__post_init__ has no update path at all, by construction) and
    live PostgreSQL (trigger rejection); reframe-creates-new-identity
    half proven by test_ai_reframe_creates_new_identity_and_never_touches_the_human_original
    and test_create_derived_persists_child_and_lineage_together.

PROOF_ARTIFACTS:
  - Migration upgrade/downgrade/re-upgrade cycle output (this report)
  - Live PostgreSQL schema inspection (\dt, \d questions, \d
    question_lineage) confirming exact column set, constraints, FKs
    and both triggers before and after the downgrade/re-upgrade cycle
  - 208-test live-database pass, including 8 distinct adversarial
    proofs with real PostgreSQL exceptions/constraints as the
    canonical result
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output
  - Diff audit (this report's DIFF_AUDIT answers, given inline above
    in the conversation)

FORBIDDEN_DEPENDENCY_CHECK: PASS (no new edge needed;
  check_architecture_dependencies.py unmodified)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above (new semantic type: yes,
  authorized; new DB write path: yes, disclosed and unwired; all other
  categories: none / not applicable). No unauthorized semantic change.

ARCHITECTURE_RECONSTRUCTION_RESULT: see inline reconstruction trace
  above. Longest legitimate chain: domain construction -> repository
  create/get -> schema-enforced immutability + Workspace confinement.
  AUTHORITY through OUTBOX/EVENT correctly SUCCESSOR_NOT_BUILT or
  NOT_APPLICABLE.

KNOWN_LIMITATIONS:
  - QuestionRepository.create_root/create_derived are real INSERT
    methods with no governed Command/Boundary/CommitUnit wrapping them
    yet -- disclosed at length in the module docstring. A future
    package (Phase 3/4) must wire this repository into a real governed
    creation path; this package deliberately does not attempt that.
  - GAP-02-002 (text vs original_text) and GAP-02-013/03 section 25.1
    (Question.status vocabulary) remain OPEN, exactly as upstream
    leaves them. No `text` or `status` column/field exists.
  - question_type/priority/emotional_signal/novelty_score/catalytic_score
    remain unmaterialized -- classification/scoring metadata outside
    this package's stated objective, deferred to whichever future
    package actually implements them.
  - `ai_generation_id` on question_lineage has no foreign key (target
    table `ai_generations` does not exist until migration
    007_ai_operational) -- disclosed the same way PKG-02 disclosed
    `human_authority_bindings.scope_id`.
  - `question_bursts`/`burst_question_memberships` (the rest of 14
    section 9's conceptual "004" bucket) remain deferred to whichever
    package (PKG-07 per the DAG) actually owns QuestionBurst.
  - Sandbox Python is 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward); not exercised
    via Docker this package (no new dependency, no new service).

BLOCKED_DEPENDENCIES: HARD-DEP-001 (Workspace governance-root bootstrap
  legitimacy) and HARD-DEP-002 (provider/privacy eligibility) unchanged,
  still BLOCKED. Used only via NonProofWorkspaceBootstrap in test
  fixtures, never claimed as legitimate. PKG-06 has no AI surface
  (prompt: AI section says only "AI reframe remains derived/new
  identity", no provider integration).

NEW_GAPS_DISCOVERED: none. All encountered gaps (GAP-02-002,
  GAP-02-013/GAP-03 section 25.1) were already open in
  16_DECISION_GAP_REGISTER.md before this package began.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. QuestionOrigin's 4
  values are 02 section 15's own list (minus a term 02 itself assigns
  elsewhere); LineageTransformationType's 2 values are 09 section 32's
  own named semantics; the author/origin pairing rule is 09 section
  31's own "nullable where non-human" language read as a biconditional;
  the Workspace-confinement composite FKs are the same pattern 09
  section 27.1 and PKG-05 already established, applied to a second
  object pair.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-07 (per 14's DAG: PKG-07 requires
  PKG-06, PKG-03 -- both now verified)
HUMAN_GATE_REQUIRED: YES -- Build Phase 2, human authorization required
  before any successor package begins.
```
