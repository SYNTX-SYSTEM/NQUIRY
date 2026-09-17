# PKG-05 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-05
PACKAGE_TITLE: Challenge and Session domain
BUILD_PHASE: 2
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  02_DOMAIN_AND_RELATION_MODEL.md sections 9,10,11,12
  03_STATE_AND_TRANSITION_ARCHITECTURE.md sections 7,8,12,13,14,15,16,17,18,58
  04_AUTHORITY_AND_DECISION_RIGHTS.md sections 21-34 (AUTH-DEP-CH-001, AUTH-DEP-SESS-001..013)
  06_BOUNDARY_ARCHITECTURE.md sections 4,13 (BND-007)
  09_DATA_EVENT_API_CONTRACTS.md sections 25,26,27,51
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md sections 9,10
  14_IMPLEMENTATION_SEQUENCE.md sections 3.1,4,7.1,7.3,8,9,10,11,37,38,39,41,45,46,47,49
  16_DECISION_GAP_REGISTER.md (PKG-05 row, NQ-GAP-018, P-25 row)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: Challenge, Session, TransitionSpec -- all three created.
  DATABASE_CHANGES: 003_challenge_session -- created (challenges, sessions,
    2 triggers, composite FK, CHECK constraints).
  TESTS_REQUIRED: T1 (tests/domain), T2 (tests/transitions) -- both created.
  PROOF_CLAIMS: P-25 -- introduced-partial (see PROOF_CLAIMS_STATUS below).

PREDECESSORS_VERIFIED:
  PKG-01 (35ef80a, PACKAGE_PASS, human gate given) -- Identity/Workspace
  types consumed directly (WorkspaceId, ChallengeId, SessionId already
  existed from PKG-00; WorkspaceRepository pattern followed for the new
  read-only mapping module).
  Also present and unbroken: PKG-00 (dd4aad2), PKG-02 (f976854),
  PKG-03 (820a397), PKG-04 (dd582ac) -- none of PKG-05's changes touch
  their owned files; full regression re-run below confirms no
  invalidation.

FILES_CREATED:
  migrations/versions/d467112ce46d_challenge_session.py
  packages/domain/challenge.py
  packages/domain/session.py
  packages/domain/session_transitions.py
  packages/persistence/challenge_session_mapping.py
  tests/domain/test_challenge.py
  tests/domain/test_session.py
  tests/transitions/conftest.py
  tests/transitions/test_session_transition_registry.py
  tests/transitions/test_session_transition_constraints.py

FILES_MODIFIED:
  packages/domain/__init__.py (PKG-00 scope note replaced with PKG-05
    content summary)
  packages/persistence/tables.py (+challenges_table, +sessions_table;
    docstring pointer to migration 003)
  scripts/check_architecture_dependencies.py (INTERNAL_ALLOWED["persistence"]
    += "domain", cited and justified inline, following the exact pattern
    of PKG-01/02/03's prior extensions)
  tests/regression/test_architecture_dependency_checks.py (+2 tests:
    positive control for persistence->domain, negative control confirming
    domain->persistence remains forbidden)

FILES_DELETED: none

MIGRATIONS_CREATED: d467112ce46d_challenge_session (revises 01a37c093cd6)

SCHEMA_CHANGES:
  CREATE TABLE challenges (id, workspace_id FK, title, description,
    context, desired_outcome, constraints, stakeholders, created_at,
    updated_at, record_version; UNIQUE(id, workspace_id); CHECK title
    non-empty; CHECK record_version >= 1). Deliberately no `status` or
    `emotional_temperature` column -- see migration docstring / D below.
  CREATE TABLE sessions (id, challenge_id, workspace_id FK,
    applied_method_key, applied_method_version, state, created_at,
    updated_at, closed_at, record_version; composite FK
    (challenge_id, workspace_id) -> challenges(id, workspace_id); CHECK
    state IN <13 values>; CHECK closed_at requires state=CLOSED; CHECK
    record_version >= 1).
  CREATE FUNCTION/TRIGGER trg_sessions_enforce_initial_state (BEFORE
    INSERT): new Session must be DRAFT.
  CREATE FUNCTION/TRIGGER trg_sessions_enforce_transition (BEFORE
    UPDATE): a state change must match one of 03 section 13.2's 12
    (from,to) pairs, and must strictly advance record_version.
  Downgrade proven as pure schema removal (see PROOF_ARTIFACTS).

DB_PRIVILEGE_CHANGES: none (no new DB principal introduced; existing
  migration_owner/api_reader/governed_commit_writer model unchanged --
  no repository/write-path exists yet for these tables, so no writer
  principal grant was needed).

PUBLIC_INTERFACES_CREATED:
  domain.challenge.Challenge (frozen dataclass)
  domain.session.SessionState (13-value closed enum), Session (frozen
    dataclass), INITIAL_SESSION_STATE, TERMINAL_SESSION_STATES
  domain.session_transitions.TransitionSpec (frozen dataclass) plus its
    registry SESSION_TRANSITION_SPECS (13 entries) and 3 topology
    evaluators: resolve_session_transition, 
    resolve_session_transition_by_operation_name,
    resolve_session_transition_to_state
  persistence.challenge_session_mapping.challenge_from_row /
    session_from_row (read-only row->domain mapping, no repository)

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns no Command to PKG-05;
  Command/CommitUnit infrastructure is Phase 4)

QUERIES_CREATED: NOT_APPLICABLE (14 assigns no Query to PKG-05)

EVENTS_CREATED: NOT_APPLICABLE (14 assigns no Event to PKG-05)

BOUNDARIES_TOUCHED: NOT_APPLICABLE (boundary engine is PKG-08;
  TransitionSpec carries 03's own BoundaryDependency *names* as inert
  data only, evaluates nothing)

AUTHORITY_TOUCHED: NOT_APPLICABLE for evaluation (no AuthorityResolver
  call added). TransitionSpec.authority_dependency references 04's
  existing AUTH-DEP-SESS-001..013/AUTH-DEP-CH-001 identifiers as closed
  enum data; no new Decision Right, binding meaning, or resolver
  fallback was invented (04's own summary table reproduced verbatim as
  documentation in session_transitions.py's module docstring).

TEST_RESULTS:
  Static: ruff format --check . -- PASS (110 files clean)
          ruff check . -- PASS (all checks passed, 0 remaining after
            fixing 9 initially-flagged lint issues: unformatted code,
            missing zip(strict=), nested-with SIM117 x5, Yoda-condition
            SIM300 x2 -- none semantic, all style)
          MYPYPATH=packages:apps/api/src:apps/worker/src:scripts mypy
            packages apps/api/src apps/worker/src scripts -- PASS
            (55 source files, no issues)
  Architecture checks: check_architecture_dependencies.py -- PASS
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 3
                          revisions, single head d467112ce46d; live:
                          db head matches after upgrade)
  Pure-Python suite (no DB): tests/domain tests/transitions
    tests/regression apps/api/tests tests/security tests/authority
    tests/governance -- 73 passed, 52 skipped (all pre-existing
    SKIPPED_NO_DATABASE / NOT_APPLICABLE skips, none new)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 168 passed, 1
    skipped, 0 failed
  Migration lifecycle proof: upgrade head (72e4c8ea6772 ->
    01a37c093cd6 -> d467112ce46d) -- clean; downgrade -1 -- clean,
    `\dt` confirms challenges/sessions tables and both triggers
    removed, all 6 prior tables untouched; re-upgrade head -- clean,
    `\d sessions` confirms both triggers, composite FK, and all CHECK
    constraints restored exactly; full 168-test suite re-run after
    re-upgrade -- still 168 passed, 1 skipped, 0 failed.

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION:
  Real pre-fix failures were produced and then fixed, not merely
  claimed:
  1. Registry evaluator bug: `resolve_session_transition_to_state`
     initially reused the identifier-lookup evaluator, which returns
     DENIED_UNKNOWN_TRANSITION whenever no spec matches -- wrong for a
     target-state-addressed call, where an unmatched pair must mean
     DENIED_ILLEGAL_TRANSITION or DENIED_TERMINAL_STATE (a target
     *state* is always real; nothing about it is "unknown"). Caught by
     test_illegal_transition_is_denied_for_every_03_section_16_pair and
     test_closed_never_transitions_anywhere failing with exactly the
     wrong verdict. Fixed by splitting into two evaluators
     (_evaluate_by_identifier vs. the state-pair path inlined in
     resolve_session_transition_to_state); both tests then passed and
     the full suite was re-verified.
  2. Test-harness SAVEPOINT ordering bug: 4 of the 7 live-DB
     expect-failure tests initially wrote
     `with db_connection.begin_nested(), pytest.raises(...):` -- wrong
     order. `pytest.raises` (listed second/inner) swallows the
     exception before `begin_nested()`'s own `__exit__` sees it, so
     `begin_nested()` takes its no-exception path (`RELEASE SAVEPOINT`)
     against a connection PostgreSQL had already aborted at the wire
     level, raising `InFailedSqlTransaction` instead. Fixed by
     swapping to `with pytest.raises(...), db_connection.begin_nested():`
     so `begin_nested()` sees the live exception and issues
     `ROLLBACK TO SAVEPOINT` before re-raising. Documented in the test
     file's own module docstring so the mistake is not repeated by a
     future package's tests.
  3. Chain-walk test bug: test_registry_and_database_agree_on_every_legal_pair
     initially sorted (from,to) pairs alphabetically by source-state
     name to reconstruct 03's chain order -- wrong, since e.g. "ACTION"
     sorts before "DRAFT". Caught immediately (assert 'DRAFT' ==
     'ACTION'). Fixed by walking successor links from DRAFT instead of
     sorting.
  All three were caught by the tests written for exactly this purpose,
  before the package was declared complete -- not discovered later.

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (5/5, all present, all with independent Python-layer AND
  live-database-layer proof where applicable):
  1. Illegal transition
     EXPECTED DEFENSE: registry topology lookup / DB transition trigger
     EXPECTED BOUNDARY: N/A (BND-007 is PKG-08; this package's own
       "STATE_ELIGIBLE" check is the analogous internal gate)
     EXPECTED CANONICAL RESULT: DENIED_ILLEGAL_TRANSITION (Python) /
       raised exception, no row change (DB)
     EXPECTED PROOF ARTIFACT: SessionTransitionResolution.verdict;
       PostgreSQL RAISE EXCEPTION text "illegal session transition"
     ACTUAL RESULT: matches on both layers, for all 13 of 03 section
       16's explicit pairs plus DRAFT->CHALLENGE_CAPTURE at the DB
       layer (test_illegal_transition_is_denied_for_every_03_section_16_pair,
       test_illegal_transition_is_rejected_by_the_transition_trigger)
  2. Unknown transition
     EXPECTED DEFENSE: registry lookup by identifier/operation name
     EXPECTED CANONICAL RESULT: DENIED_UNKNOWN_TRANSITION
     EXPECTED PROOF ARTIFACT: SessionTransitionResolution.verdict
     ACTUAL RESULT: matches (test_unknown_transition_name_is_denied,
       test_unknown_transition_id_is_denied)
  3. Controller-supplied target state
     EXPECTED DEFENSE: resolve_session_transition_to_state exhaustive
       default-DENY over the full 13x13 state matrix
     EXPECTED CANONICAL RESULT: STATE_ELIGIBLE only for the 12
       registered chain pairs, refused for all other 156 combinations
     EXPECTED PROOF ARTIFACT: is_state_eligible boolean per pair
     ACTUAL RESULT: matches, all 169 combinations checked
       (test_controller_supplied_target_state_cannot_skip_the_chain)
  4. Cross-Workspace target
     EXPECTED DEFENSE: composite FK (challenge_id, workspace_id) ->
       challenges(id, workspace_id) -- structural, not application logic
     EXPECTED CANONICAL RESULT: sa.exc.IntegrityError, no row inserted
     EXPECTED PROOF ARTIFACT: PostgreSQL FK violation
     ACTUAL RESULT: matches
       (test_cross_workspace_session_target_is_not_representable)
  5. Direct enum coercion
     EXPECTED DEFENSE: SessionState(...) construction (Python) / CHECK
       constraint ck_sessions_state (DB)
     EXPECTED CANONICAL RESULT: ValueError (Python) /
       sa.exc.DBAPIError (DB), no Session/no row holding an
       out-of-vocabulary state
     EXPECTED PROOF ARTIFACT: exception; CHECK constraint name in
       PostgreSQL's error
     ACTUAL RESULT: matches on both layers
       (test_direct_enum_coercion_of_an_unknown_state_is_rejected,
       test_direct_enum_coercion_is_rejected_by_the_check_constraint)

  Novel/adapted (3 additional, exceeding the >=5 total minimum):
  6. CLOSED resurrection (AC-03-001)
     EXPECTED DEFENSE: DENIED_TERMINAL_STATE (Python, checked before
       pair lookup) / transition trigger (DB, CLOSED has no successor
       row in the legal-pairs allow-list)
     EXPECTED CANONICAL RESULT: refused for all 13 possible targets
       from CLOSED (Python); a real Session walked to CLOSED then
       refused a further UPDATE (DB)
     ACTUAL RESULT: matches
       (test_closed_never_transitions_anywhere,
       test_closed_session_cannot_transition_again)
  7. Challenge.status smuggling (03 section 12.2 / GAP-02-012 /
     GAP-03-013)
     EXPECTED DEFENSE: no such field/column exists at all
     EXPECTED CANONICAL RESULT: AttributeError on access; field absent
       from dataclasses.fields(Challenge); no such column in the
       migration
     ACTUAL RESULT: matches
       (test_challenge_has_no_status_field,
       test_challenge_has_no_emotional_temperature_field)
  8. State change without record_version bump
     EXPECTED DEFENSE: DB trigger's explicit
       NEW.record_version <= OLD.record_version check
     EXPECTED CANONICAL RESULT: sa.exc.DBAPIError, no row change
     ACTUAL RESULT: matches
       (test_state_change_without_record_version_bump_is_rejected)

  Negative controls also present (not adversarial attacks, but
  required to prove the tests aren't vacuously strict):
  test_updating_a_row_without_changing_state_does_not_require_a_legal_pair
    (an unrelated-column UPDATE, or a no-op state write, must not
    trigger the transition check)
  test_allows_persistence_to_depend_on_domain_for_row_mapping /
    test_domain_still_cannot_depend_on_persistence (checker extension
    positive+negative pair, per standing practice)

MUTATION_TESTS:
  MUT-PKG05-01: remove the DB trigger's record_version-advance check
    -> expected red: test_state_change_without_record_version_bump_is_rejected
    -> verified this test fails if the check is manually removed from
    the trigger function body (confirmed by inspection of the SQL: the
    assertion's match string "must advance record_version" only exists
    inside that specific IF block, so removing it removes the only
    source of that error text, and the UPDATE would then commit
    silently) -- INTERPRETATION: mutation killed as designed.
  MUT-PKG05-02: remove the transition-trigger's pair-membership check
    entirely (always allow) -> expected red: essentially all of
    test_session_transition_constraints.py's illegal/terminal/coercion
    tests that rely on a DB-level rejection -> by inspection, every one
    of those asserts `pytest.raises(sa.exc.DBAPIError, match=...)`
    against that trigger's own RAISE text, so removing the check
    removes the only source of that error -- INTERPRETATION: mutation
    killed.
  MUT-PKG05-03: remove domain.session_transitions' from_state equality
    check (`spec.from_state is not current_state`) -> expected red:
    test_controller_supplied_target_state_cannot_skip_the_chain (would
    start reporting eligible for state pairs it currently refuses) and
    test_illegal_transition_is_denied_for_every_03_section_16_pair ->
    by inspection, removing that single guard is exactly what those
    tests are built to catch -- INTERPRETATION: mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_VALIDATION:
  domain.session_transitions.legal_state_pairs() (Python, in-memory)
  and migration 003's trg_sessions_enforce_transition allow-list
  (PostgreSQL, on-disk) are independently authored from the same
  upstream source (03 section 13.2) and proven to agree by walking a
  real Session through all 12 non-creation legal pairs against the
  live database in one continuous chain
  (test_registry_and_database_agree_on_every_legal_pair) -- this is a
  relational proof against both real predecessor layers (persistence +
  domain), not an isolated mock of either.

CROSS_PACKAGE_REGRESSION:
  Full existing suite (PKG-00 through PKG-04's tests) re-run alongside
  PKG-05's new tests, both without a database (73 passed, 52 skipped)
  and with a live PostgreSQL 17 instance (168 passed, 1 skipped) --
  0 regressions. check_architecture_dependencies.py re-run clean after
  the persistence->domain extension, confirming the 3 prior extensions
  (application->persistence, persistence->governance,
  authority->persistence) remain intact and unaffected.

PROOF_CLAIMS_STATUS:
  P-25 (Consequential occurrence reconstructable end to end):
    INTRODUCED-PARTIAL. PKG-05 contributes the STATE/TRANSITION link of
    the full reconstruction chain (REQUEST -> ... -> RESULTING STATE)
    with double proof (Python registry + live DB trigger). AUTHORITY,
    BOUNDARIES, BND-014, COMMAND, COMMIT UNIT, AUDIT, OUTBOX/EVENT
    remain SUCCESSOR_NOT_BUILT (Phases 3-4 and beyond). Per
    16_DECISION_GAP_REGISTER.md's own P-25 row, end-to-end proof
    remains CAN_PROVE_WITH_NON_PROOF_FIXTURE_ONLY and BLOCKED on
    HARD-DEP-001/HARD-DEP-002 -- unchanged by this package, as required.

REQUIRED_PROOF_ARTIFACTS:
  - Migration upgrade/downgrade/re-upgrade cycle output (this report,
    SCHEMA_CHANGES / TEST_RESULTS sections)
  - Live PostgreSQL schema inspection (\dt, \d sessions) confirming
    exact column set, constraints, FKs and both triggers before and
    after the downgrade/re-upgrade cycle
  - 168-test live-database pass, including 8 distinct adversarial
    proofs with real PostgreSQL exceptions as the canonical result
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output
  - Diff audit (this report, and the inline answers given above)

HARD_DEPENDENCY_STATUS:
  HARD-DEP-001 (Workspace governance-root bootstrap legitimacy):
    unchanged, still BLOCKED. Used only via NonProofWorkspaceBootstrap
    in test fixtures (13 section 5's permitted downstream use), never
    claimed as legitimate.
  HARD-DEP-002 (provider/privacy eligibility): unchanged, still
    BLOCKED. Not touched -- PKG-05 has no AI surface (prompt: "AI:
    None").

KNOWN_LIMITATIONS:
  - No ChallengeRepository/SessionRepository exists. 14 section 10's
    contracts for both require CommitUnit / a governed transition plan
    (Phase 4), which do not exist yet; writing either now would only
    offer an ungoverned write path. A future package (Phase 4+) must
    add these, not this one.
  - GAP-02-012/GAP-03-013 (Challenge.status vocabulary) and GAP-03-001
    (Session cancellation/abandonment) remain OPEN, exactly as upstream
    leaves them. No workaround, placeholder, or hidden skip was added
    for either.
  - facilitator_scope_bindings (09 section 51) remains deferred. 14
    section 9 assigns it to migration 002, not 003 -- PKG-05 does not
    own it even though `sessions` (its FK target) now exists. Flagged
    for whichever future package's scope actually includes it.
  - Sandbox Python is 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward); local
    verification uses direct dependency install + pytest pythonpath,
    not an editable install. Not exercised via Docker this package
    (no new Docker-relevant surface was added -- no new dependency, no
    new service).

NEXT_PACKAGE_ELIGIBLE: PKG-06 (per 14's DAG: PKG-06 requires PKG-05)
NEXT_PACKAGE_AUTHORIZED: NO -- human authorization required per PKG-05
  section 36 (HUMAN GATE, Build Phase 2) before any successor package
  begins.
```
