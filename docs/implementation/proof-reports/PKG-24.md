# PKG-24 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-24
PACKAGE_TITLE: BND-017/BND-018 and Recovery Command
BUILD_PHASE: 9
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  06_BOUNDARY_ARCHITECTURE.md section 24 ("BND-017 FAILURE /
    INDETERMINATE BOUNDARY" -- full spec: PURPOSE "Contain uncertain or
    failed consequential operations so uncertainty cannot create
    permission, duplicate consequence or downstream state"; ALLOW known
    FAILED_PRECOMMIT/COMMITTED; DENY "dependent consequential operation
    after INDETERMINATE; blind retry when duplicate consequence is
    possible; assume rollback without proof; assume commit without
    proof"; REQUIRE "Recovery/reconciliation for INDETERMINATE";
    TESTABLE INVARIANT "An INDETERMINATE consequential operation blocks
    every dependent consequence until reconciliation establishes the
    last valid state"), section 25 ("BND-018 RECOVERY / ROLLBACK
    BOUNDARY" -- PURPOSE "Ensure recovery restores or reconciles only
    architecture-valid state and cannot bypass normal authority, scope,
    immutability or audit semantics"; REQUESTING ACTOR "SYSTEM_SERVICE
    for deterministic reconciliation. HUMAN_USER only where 10 later
    defines a discretionary recovery decision with valid authority";
    AUTHORITY REQUIREMENT "Recovery cannot invent a new domain
    decision. Deterministic reconciliation may use bounded
    SYSTEM_DERIVED recovery authority only if 10 can prove it is
    restoring a state already legitimized by the original operation.
    Any discretionary new decision requires the normal 04 authority
    path"; the exact 8-item VALIDATION list; DENY list including "AI
    chooses recovery outcome"; TESTABLE INVARIANT "Recovery can never
    produce a state that could not have been validly reached or
    legitimately restored under 00-06")
  10_FAILURE_RECOVERY_ROLLBACK.md section 32 (AC-10-005: deterministic
    recovery consumes the already-approved 04/05 SYSTEM_DERIVED
    procedural model), section 34 ("A Saga engine or recovery worker
    cannot inherit the original actor's human authority"), section 63
    ("[ARCHITECTURAL CLOSURE] AC-10-009" -- RecoveryRecord's exact
    field list, including the literal "record_version"/"blocked
    target refs" this package retrofits)
  14_IMPLEMENTATION_SEQUENCE.md PKG-24's own package manifest
    (BUILD_PHASE 9, CRITICAL classification, OBJECTIVE "Implement
    BND-017 INDETERMINATE blocking, dependent-operation detection,
    BND-018 reconciliation routing, Recovery Command through normal
    identity, Workspace, current authority, Evidence if required,
    boundaries, BND-014 and CommitUnit. Deterministic recovery only
    restores already-established legitimate state. Discretionary
    domain choice requires existing human authority"), section 7.1
    (`recovery_records` core-tables row naming "record_version" as its
    literal Version column), section 3.1 (`boundaries`'s own
    allow-list, unexercised `recovery` ceiling since PKG-00), STOP
    CONDITIONS ("recovery needs a new domain choice", "required
    authority is undefined")
  04_AUTHORITY_GOVERNANCE_MODEL.md section 9 (AuthorityClass's own
    7-value closed list, all HUMAN Decision Rights), section 563
    ("SYSTEM_DERIVED" authority category -- not represented in
    `AuthorityClass`)
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md's own minimum-proof list
    (RecoveryRecord, BND-018, service identity, Workspace isolation --
    no human discretionary recovery flow named)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md T4 (-> tests/boundaries/)
    and T8 (-> tests/recovery/) rows, P-20/P-21 matrix rows
    (T13-P20-INDETERMINATE, T13-P21-RECOVERY-NO-AUTH)

PREDECESSORS_VERIFIED:
  PKG-23 (25d39e7, PACKAGE_PASS -- LPVS and RecoveryRecord;
    `RecoveryRecord`/`RecoveryRepository`/`RecoveryClass`/
    `RecoveryOutcome` directly extended, not replaced).
  PKG-22 (aa74639, PACKAGE_PASS -- `FailureClass`/`ConsequenceCertainty`
    reused directly in BND-017's own `known_consequence_certainty`
    field).
  PKG-01 (Workspace) -- `WorkspaceRepository`/`SqlAlchemyWorkspaceRepository`
    reused directly by BND-002/`RecoveryService`, unmodified.
  Full chain unbroken: PKG-00 dd4aad2 through PKG-23 25d39e7. No file
  outside this package's own new-file set was touched beyond the five
  disclosed extension points (see FILES_MODIFIED).

FILES_CREATED:
  migrations/versions/b7ec21429b53_recovery_command_fields.py
  packages/boundaries/bnd_017_failure_indeterminate.py
  packages/boundaries/bnd_018_recovery_rollback.py
  packages/application/recovery_handler.py
  tests/boundaries/test_bnd_017_failure_indeterminate.py
  tests/boundaries/test_bnd_018_recovery_rollback.py
  tests/recovery/boundaries/conftest.py
  tests/recovery/boundaries/test_recovery_service.py

FILES_MODIFIED:
  packages/persistence/tables.py (`recovery_records_table` gains
    `record_version`/`blocked_target_refs` columns + a
    `ck_recovery_records_record_version_positive` CHECK; header
    docstring extended with a PKG-24 cross-reference)
  packages/persistence/recovery_repository.py (`create`/`record_attempt`/
    `mark_resolved` now read/write `record_version`/`blocked_target_refs`;
    `record_attempt`/`mark_resolved` now advance `record_version` by one
    on every write; new `is_target_blocked` method; `_record_from_row`
    reads both new columns)
  packages/recovery/models.py (`RecoveryRecord` gains a REQUIRED
    `record_version: RecordVersion` field and a defaulted
    `blocked_target_refs: tuple[str, ...] = ()` field, plus
    `__post_init__` validation for the former; `RecoveryRepository`
    Protocol gains `is_target_blocked`; new `recovery_target_ref` helper;
    module docstring extended with the "WHY record_version/
    blocked_target_refs WERE ADDED AT PKG-24, NOT PKG-23" section)
  scripts/check_architecture_dependencies.py
    (`INTERNAL_ALLOWED["boundaries"] += "recovery"`, the one new
    disclosed extension this package needs -- see DIFF_AUDIT)
  tests/recovery/test_recovery_record.py (PKG-23's own file --
    regression fix REQUIRED by `RecoveryRecord`'s new non-default
    `record_version` field: both existing construction sites, in the
    `_record()` helper and in
    `test_denies_a_non_failure_class_in_failure_classifications`, now
    pass `record_version=RecordVersion.initial()`; three NEW PKG-24
    tests added -- `record_version` advancing across `record_attempt`/
    `mark_resolved`, `is_target_blocked` true-while-unresolved/false-
    once-resolved, and `exclude_recovery_id` self-exclusion)

FILES_DELETED: none

MIGRATIONS_CREATED: b7ec21429b53 (recovery_command_fields), revises
  fb881bc022b1. Adds `record_version BIGINT NOT NULL DEFAULT 1` (+ CHECK
  `record_version >= 1`) and `blocked_target_refs TEXT[] NOT NULL
  DEFAULT '{}'` to `recovery_records`. No new trigger -- neither column
  needs one (the existing identity-immutability/result-transition
  triggers from PKG-23 are untouched and unaffected). Purely additive:
  no prior migration edited, no existing column type-changed or
  dropped. Applied live to a fresh compose PostgreSQL 17; downgrade(-1)
  then re-upgrade cycle verified; resulting schema inspected via
  `psql \d recovery_records` (both new columns, the CHECK, and all
  three PKG-23 triggers confirmed present and correct).
SCHEMA_CHANGES: `recovery_records` gains 2 columns (see above). No
  other table touched.
DB_PRIVILEGE_CHANGES: none. Deferred to `012_security_events_rls`,
  consistent with every migration since `001`.

PUBLIC_INTERFACES_CREATED:
  boundaries.bnd_017_failure_indeterminate.{Bnd017Input,
    Bnd017FailureIndeterminateEvaluator}
  boundaries.bnd_018_recovery_rollback.{Bnd018Input,
    Bnd018RecoveryRollbackEvaluator}
  application.recovery_handler.{RecoveryResolutionFacts,
    RecoveryResolutionDenied, RecoveryResolutionStaleVersion,
    RecoveryService}
  recovery.models.recovery_target_ref (new helper)
  recovery.models.RecoveryRepository.is_target_blocked (new Protocol
    method, both `RecoveryRepository` implementations updated)

COMMANDS_CREATED: `RecoveryService.resolve_recovery` -- the one
  deterministic Recovery Command this package builds (SYSTEM_SERVICE
  actor only, enforced at BND-001). NOT modeled as a
  `CommitCoordinator`-issued `CommitUnit` -- see AUTHORITY_PATH for the
  full, human-confirmed disclosure of why.
QUERIES_CREATED: NOT_APPLICABLE. `is_target_blocked` is a repository
  read, not a CQRS Query object; 14's own manifest introduces no Query
  for this package.
EVENTS_CREATED: NOT_APPLICABLE. `RecoveryService.resolve_recovery`
  produces no Event, no `OutboxRecord`, and no `AuditEvent` -- disclosed
  as the central, human-confirmed architectural shape of this package
  (see AUTHORITY_PATH); `RecoveryRecord` itself remains 10 section 63's
  own "OPERATIONAL_RECORD, not domain Thing", carrying no
  `audit_event_ids`/`outbox_ids` fields to populate even if this
  package wanted to.

BOUNDARIES_CREATED_OR_CHANGED:
  BND-017 (Failure/Indeterminate) -- created, holds a real
    `RecoveryRepository`, re-reads `is_target_blocked` fresh on every
    call (never cached).
  BND-018 (Recovery/Rollback) -- created, pure-function over caller-
    supplied facts (no repository dependency of its own).
  No pre-existing boundary evaluator was modified. `RecoveryService`
    wires BND-001 (existing, PKG-19)/BND-002 (existing, PKG-01) into
    the SAME chain, reused unmodified.

AUTHORITY_PATH: [HUMAN-CONFIRMED ARCHITECTURAL DECISION, PKG-24]
  `commit.coordinator.CommitCoordinator.commit()` hard-requires a
  `required_authority_class: governance.authority_binding.
  AuthorityClass` -- a closed 7-value enum whose every member is a
  HUMAN Decision Right (04 section 9). None represents 04 section 563's
  own "SYSTEM_DERIVED" authority category a deterministic,
  SYSTEM_SERVICE-driven recovery actor would need, and no BND-011
  (SYSTEM_DERIVED AUTHORITY BOUNDARY) evaluator exists anywhere in this
  codebase to resolve one -- confirmed via
  `find packages/boundaries -iname "*bnd_011*"` returning empty; BND-011
  is neither built nor assigned to PKG-24 or any earlier package.
  Passing any of the 7 human-shaped classes for a SYSTEM_SERVICE actor
  here would itself BE "recovery inherits human authority" -- exactly
  the P-21 violation (10 section 34) this package's own OBJECTIVE
  exists to prevent, and exactly the "inferred authority" shortcut this
  package's own FORBIDDEN_SHORTCUTS names.

  This tension was surfaced to the user as a genuine STOP-shaped
  decision (14 section 35: "STOP if required authority is undefined"),
  via the `AskUserQuestion` tool, rather than resolved silently. The
  question asked, verbatim in substance: how should the deterministic
  (SYSTEM_SERVICE) recovery path handle BND-014/CommitUnit given
  `AuthorityClass` has no SYSTEM_DERIVED value? The user selected the
  recommended option: build the deterministic path WITHOUT
  `CommitCoordinator`/`CommitUnit`.

  Confirmed resolution, as implemented: the deterministic Recovery
  Command performs its own governed write -- BND-001/002/017/018
  evaluated via the real `boundaries.registry.evaluate_chain`, followed
  by a real atomic transaction (`connection.begin_nested()`, the
  identical SAVEPOINT-as-production-transaction-boundary
  `[IMPLEMENTATION CHOICE]` `CommitCoordinator` itself already uses
  internally, PKG-13) wrapping `RecoveryRepository.mark_resolved` --
  producing NO `CommitUnit`/`AuditEvent`/`OutboxRecord` row. This is not
  merely a workaround: 10 section 63 itself classifies `RecoveryRecord`
  as an "OPERATIONAL_RECORD, not domain Thing" whose own exact field
  list (unlike `QuestionSelection`/`Decision`) carries no
  `commit_id`/`audit_event_ids`/`outbox_ids` fields at all --
  RecoveryRecord's own resolution was never modeled as a
  CommitUnit-producing canonical write to begin with.

  BND-001's own `required_actor_classes={SYSTEM_SERVICE}` (deliberately
  excluding HUMAN_USER) proves the mandatory "admin recovery" attack
  directly: a HUMAN_USER invoking THIS command is denied before
  anything else runs. The version-freshness check BND-014 would
  otherwise provide is performed directly in `RecoveryService` (see
  `RecoveryResolutionStaleVersion`) rather than via BND-014, since
  BND-014's own internal `AuthorityResolver.resolve()` call has the
  identical SYSTEM_DERIVED problem.

  The HUMAN_USER discretionary path (RC-07), which WOULD have a real,
  applicable `AuthorityClass` to check through the full
  `CommitCoordinator`, remains `SUCCESSOR_NOT_BUILT` -- disclosed, not
  fabricated; 12's own MINIMUM scope names only the deterministic/
  SYSTEM_SERVICE path.

EVIDENCE_PATH: 14's own OBJECTIVE phrase "Evidence if required" is
  conditioned on this prototype's own MINIMUM scope (12), which never
  requires Evidence for the one deterministic path this package builds
  and tests. `RecoveryResolutionFacts` carries no
  `evidence_set_ref_id`/freshness field; BND-013 is not in this
  package's own `_PRECOMMIT_CHAIN`. This is a disclosed
  `SUCCESSOR_NOT_BUILT` extension point, not a violation -- BND-013 is
  independently composable and a future, richer Recovery Command could
  add it to its own chain without changing anything this package built.
AI_PATH: "AI chooses recovery outcome" (06 section 25's own PROHIBITED
  PATH) is now denied TWICE, independently: BND-018's own unconditional
  first check (`AI_CANNOT_CHOOSE_RECOVERY_OUTCOME`), AND structurally
  pre-empted at BND-001 (`required_actor_classes={SYSTEM_SERVICE}`,
  which also excludes `AI_PROCESSOR`) before BND-018 ever runs in the
  wired `RecoveryService` path -- proven as genuine defense-in-depth by
  `test_denies_ai_processor_actor_before_bnd_018_ever_runs`
  (`tests/recovery/boundaries/test_recovery_service.py`), whose
  `chain_result.terminal_boundary_id` is `BND_001`, not `BND_018`.
RECOVERY_PATH: BND-017 now materializes "An INDETERMINATE consequential
  operation blocks every dependent consequence until reconciliation
  establishes the last valid state" as a live, DB-backed check (14
  section 29's "dependency blocking metadata", via `blocked_target_refs`
  -- a derived predicate on `RecoveryRecord` itself, no separate join
  table). BND-018 now materializes "Recovery can never produce a state
  that could not have been validly reached or legitimately restored" --
  `lpvs_resolved`/`restores_already_legitimized_state` are both checked
  before any write. RC-07 (Manual/Discretionary Recovery) remains
  `SUCCESSOR_NOT_BUILT` (see AUTHORITY_PATH).

TESTS_CREATED:
  tests/boundaries/test_bnd_017_failure_indeterminate.py (16 tests --
    blocking DENY, per-target isolation, self-exclusion, PROVEN_COMMITTED/
    PROVEN_NOT_COMMITTED/uncertain branches, construction validation,
    registry composition, MUT-PKG24-01)
  tests/boundaries/test_bnd_018_recovery_rollback.py (13 tests --
    full-ALLOW positive control, LPVS-unresolved-first DENY, AI DENY,
    HUMAN_USER with/without current authority, SYSTEM_SERVICE/
    EXTERNAL_SYSTEM deterministic branch, all 7 invariants individually
    and jointly, construction validation, registry composition,
    MUT-PKG24-02)
  tests/recovery/boundaries/test_recovery_service.py (13 tests -- full
    end-to-end ALLOW, admin recovery DENY, AI DENY, blind retry DENY,
    dependent-operation-blocked DENY, never-legitimate-state DENY,
    audit-invariant DENY, nonexistent/cross-Workspace recovery_id DENY
    (both collapsing to BND-002), stale-version DENY, event-replay DENY,
    full-chain-order proof, MUT-PKG24-03)
  tests/recovery/boundaries/conftest.py (shared `db_connection` fixture,
    identical `SKIPPED_NO_DATABASE` convention as every other T4/T8
    conftest)

TESTS_MODIFIED: tests/recovery/test_recovery_record.py (PKG-23's own
  file) -- regression fix (two existing `RecoveryRecord(...)`
  construction sites given the new required `record_version` field) +
  3 new PKG-24 tests (12 -> 15 tests total in this file).

TARGETED_TEST_RESULTS:
  Pure-Python (no `DATABASE_URL`): 660 passed, 356 skipped (skips are
    the established `SKIPPED_NO_DATABASE` convention -- every DB-backed
    test in this and every prior package).
  Live PostgreSQL 17 (`DATABASE_URL=postgresql+psycopg://nquiry:
    nquiry_local_dev_only@localhost:15432/nquiry`), full suite
    (`tests/ apps/api/tests apps/worker`): 1016 passed, 1 skipped (the
    one pre-existing, unrelated, disclosed skip from earlier packages).
    Zero failures, zero new skips, zero regressions against PKG-23's own
    970-passed baseline.

NEGATIVE_TEST_RESULTS: `Bnd017Input`/`Bnd018Input` construction
  rejects a mismatched `boundary_id` (both), an empty
  `requested_operation`/`target_ref` (BND-017), and a non-`RecoveryClass`
  `recovery_class` (BND-018) -- all designed-before-implementation
  negative cases, all pass.

ADVERSARIAL_TEST_RESULTS:
  Mandatory (14/14, drawn from 06 section 24/25's own DENY lists and
  this package's own CRITICAL-classification OBJECTIVE):
  1. ATTACK: Admin recovery (HUMAN_USER invokes the deterministic
       Recovery Command)
     EXPECTED DEFENSE / BOUNDARY: BND-001 denies before BND-017/018 run
     ACTUAL RESULT: matches (test_denies_admin_recovery_attempt_by_a_human_user,
       terminal_boundary_id == BND_001)
  2. ATTACK: AI chooses recovery outcome
     EXPECTED DEFENSE / BOUNDARY: denied at BND-001 (actor-class scope)
       AND independently at BND-018 (unconditional AI check) --
       defense-in-depth
     ACTUAL RESULT: matches
       (test_denies_ai_processor_actor_before_bnd_018_ever_runs,
       test_denies_ai_processor_unconditionally)
  3. ATTACK: Blind retry when duplicate consequence is possible
     EXPECTED DEFENSE / BOUNDARY: BND-017 DENY
       (BLIND_RETRY_ON_UNCERTAIN_CONSEQUENCE)
     ACTUAL RESULT: matches (test_denies_blind_retry_on_uncertain_consequence,
       test_uncertain_consequence_denies_blind_retry)
  4. ATTACK: Dependent consequential operation after INDETERMINATE
     EXPECTED DEFENSE / BOUNDARY: BND-017 DENY
       (DEPENDENT_OPERATION_BLOCKED_BY_INDETERMINATE), unconditional,
       checked first
     ACTUAL RESULT: matches
       (test_denies_dependent_operation_blocked_by_another_indeterminate_record,
       test_denies_dependent_operation_while_target_is_blocked)
  5. ATTACK: Assume commit/rollback without proof
     EXPECTED DEFENSE / BOUNDARY: BND-017 DENY
       (CANNOT_ASSUME_OUTCOME_WITHOUT_PROOF:<op>)
     ACTUAL RESULT: matches (test_uncertain_consequence_denies_assumption_operations)
  6. ATTACK: Repeat a known-COMMITTED consequence
     EXPECTED DEFENSE / BOUNDARY: BND-017 DENY
       (COMMITTED_CONSEQUENCE_MUST_NOT_REPEAT)
     ACTUAL RESULT: matches (test_proven_committed_denies_a_repeat_attempt)
  7. ATTACK: Recover to a state that was never legitimate
     EXPECTED DEFENSE / BOUNDARY: BND-018 DENY
       (DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE)
     ACTUAL RESULT: matches
       (test_denies_recovering_to_a_never_legitimate_state,
       test_deterministic_actor_must_restore_an_already_legitimized_state)
  8. ATTACK: No proven legitimate state to recover to at all (LPVS
       unresolved)
     EXPECTED DEFENSE / BOUNDARY: BND-018 DENY
       (NO_PROVEN_LEGITIMATE_STATE_TO_RECOVER_TO), checked before
       everything else
     ACTUAL RESULT: matches (test_denies_when_lpvs_is_not_resolved)
  9. ATTACK: Erase audit/history via recovery
     EXPECTED DEFENSE / BOUNDARY: BND-018 DENY
       (RECOVERY_VALIDATION_INVARIANT_VIOLATED:audit_reconstruction_preserved)
     ACTUAL RESULT: matches (test_denies_when_audit_reconstruction_would_be_broken,
       test_each_validation_invariant_individually_denies_when_violated)
  10. ATTACK: Discretionary recovery without CURRENT (not merely
        historical) human authority
      EXPECTED DEFENSE / BOUNDARY: BND-018 DENY
        (DISCRETIONARY_RECOVERY_REQUIRES_CURRENT_HUMAN_AUTHORITY)
      ACTUAL RESULT: matches (test_human_user_without_current_authority_is_denied)
  11. ATTACK: Service uses old/invented authority to recover to an
        unlegitimized state
      EXPECTED DEFENSE / BOUNDARY: same as #7 -- SYSTEM_SERVICE branch
        requires `restores_already_legitimized_state`, never a fresh
        authority grant
      ACTUAL RESULT: matches (same tests as #7)
  12. ATTACK: Unresolvable/forged/nonexistent `recovery_id`
      EXPECTED DEFENSE / BOUNDARY: BND-002 DENY
        (UNRESOLVED_WORKSPACE_NO_OBJECTS) -- collapses to "no
        resolvable objects" rather than leaking a distinguishable
        not-found signal
      ACTUAL RESULT: matches
        (test_a_nonexistent_recovery_id_is_denied_without_disclosing_existence)
  13. ATTACK: Cross-Workspace recovery target
      EXPECTED DEFENSE / BOUNDARY: the Workspace-scoped repository read
        makes a foreign-Workspace record invisible before BND-002 even
        runs its own cross-check -- same DENY as #12
      ACTUAL RESULT: matches
        (test_a_record_from_a_different_workspace_is_treated_as_nonexistent)
  14. ATTACK: Stale/concurrent recovery attempt (TOCTOU) and event
        replay as recovery
      EXPECTED DEFENSE / BOUNDARY: `RecoveryService`'s own
        `record_version` freshness check raises
        `RecoveryResolutionStaleVersion`; no second write is ever
        applied
      ACTUAL RESULT: matches
        (test_denies_a_stale_record_version_after_a_concurrent_attempt,
        test_event_replay_with_the_original_expected_version_cannot_double_resolve)

  Novel/adapted (>=10 required for this CRITICAL package; 12 delivered,
  26 total):
  15. ATTACK: A `RecoveryRecord` improperly blocked by its OWN row
        while resolving itself
      ACTUAL RESULT: matches (test_a_recovery_record_excludes_itself_from_its_own_blocking_check)
  16. ATTACK: Wrong `boundary_id` smuggled into `Bnd017Input`/`Bnd018Input`
      ACTUAL RESULT: matches (test_denies_construction_with_the_wrong_boundary_id,
        both files)
  17. ATTACK: Non-`RecoveryClass` value smuggled into `Bnd018Input`
      ACTUAL RESULT: matches (test_denies_construction_with_a_non_recovery_class)
  18. ATTACK: `EXTERNAL_SYSTEM` actor bypasses the deterministic-branch
        legitimacy check (not HUMAN_USER, so could a bug route it
        around BND-018's own SYSTEM_SERVICE handling?)
      ACTUAL RESULT: matches (test_external_system_actor_follows_the_deterministic_branch)
  19. ATTACK: Unrecognized/fabricated `requested_operation` guessed
        into an ALLOW
      ACTUAL RESULT: matches
        (test_uncertain_consequence_requires_reconciliation_for_unrecognized_operations
        -- fail-closed REQUIRE, never a guess)
  20. ATTACK: Multiple BND-018 invariants violated at once, only the
        first reported (hiding the true blast radius from audit)
      ACTUAL RESULT: matches (test_reports_all_violated_invariants_together
        -- both names appear in one reason code)
  21. ATTACK: Chain short-circuit / a boundary silently skipped on the
        ALLOW path
      ACTUAL RESULT: matches (test_full_precommit_chain_runs_in_order_on_the_allowed_path
        plus the 4 DENY tests above, each independently proving a
        DIFFERENT `terminal_boundary_id` -- structural proof all four
        boundaries are real and load-bearing, not merely present)
  22. ATTACK (MUT-PKG24-01): blocking guard silently broken/neutered
      ACTUAL RESULT: matches (test_mut_pkg24_01_a_broken_blocking_guard_would_wrongly_allow
        -- see MUTATION_TESTS)
  23. ATTACK (MUT-PKG24-02): AI-actor check silently removed
      ACTUAL RESULT: matches (test_mut_pkg24_02_removing_the_ai_check_would_wrongly_allow_ai_to_recover
        -- see MUTATION_TESTS)
  24. ATTACK (MUT-PKG24-03): service-layer version guard bypassed by
        calling the repository directly
      ACTUAL RESULT: matches (test_mut_pkg24_03_bypassing_the_service_guard_allows_a_stale_write
        -- see MUTATION_TESTS; disclosed in KNOWN_LIMITATIONS as a real,
        not-yet-DB-enforced gap)
  25. ATTACK: `PROVEN_NOT_COMMITTED` certainty used to justify anything
        OTHER than retry/reconcile (e.g. a fabricated assumption
        operation riding on a real non-commit proof)
      ACTUAL RESULT: matches
        (test_proven_not_committed_requires_a_fresh_chain_for_anything_else
        -- REQUIRE, not ALLOW)
  26. ATTACK: An unrelated `RecoveryRecord`'s own blocked target leaking
        into a DIFFERENT target's evaluation (workspace-wide over-blocking)
      ACTUAL RESULT: matches
        (test_unblocked_target_is_not_affected_by_an_unrelated_blocked_record)

MUTATION_TESTS:
  A NOTE ON METHODOLOGY CHANGE, DISCLOSED: PKG-20 through PKG-23 used
  this codebase's established textual/inspection-based mutation
  discipline (temporarily editing production source in place,
  confirming the target test goes red, then reverting). Attempting the
  identical technique on `boundaries/bnd_017_failure_indeterminate.py`
  this package (neutralizing the `is_target_blocked` guard) was DENIED
  by this session's own auto-mode tool classifier as a
  "[Security Weaken]" action -- a genuine environment/tooling change,
  not a package-scope decision. The edit was immediately reverted
  (confirmed via `ruff check --diff`/re-reading the affected lines)
  before any further work. All three mutation proofs below were instead
  built using PKG-21's own established alternative technique --
  test-only mutant code that NEVER edits the shipped module -- or, for
  MUT-PKG24-03, a structural "guard necessity" proof using only real,
  unmodified production code.

  MUT-PKG24-01: a test-only mutant repository
    (`_AlwaysUnblockedRecoveryRepository`, defined only in
    `tests/boundaries/test_bnd_017_failure_indeterminate.py`) wraps a
    REAL `SqlAlchemyRecoveryRepository` but always answers
    `is_target_blocked=False`, simulating the guard having no effect ->
    expected: the SAME scenario that
    `test_denies_dependent_operation_while_target_is_blocked` proves
    DENY for now wrongly ALLOWs. ACTUAL: confirmed
    (test_mut_pkg24_01_a_broken_blocking_guard_would_wrongly_allow --
    result is ALLOW/COMMITTED_CONSEQUENCE_ACKNOWLEDGED instead of DENY).
    INTERPRETATION: mutation killed by the real evaluator; the mutant
    proves the guard is genuinely load-bearing, not coincidental.
  MUT-PKG24-02: a test-only mutant class (`_Bnd018WithoutAiCheck`,
    defined only in `tests/boundaries/test_bnd_018_recovery_rollback.py`)
    duplicates `Bnd018RecoveryRollbackEvaluator.evaluate`'s own dispatch
    with the AI-actor check removed -> expected: an AI_PROCESSOR actor,
    with every other fact proven true, is wrongly granted
    `RECOVERY_PERMITTED`. ACTUAL: confirmed
    (test_mut_pkg24_02_removing_the_ai_check_would_wrongly_allow_ai_to_recover).
    INTERPRETATION: mutation killed by the real evaluator.
  MUT-PKG24-03: guard-necessity structural proof, not a code mutation --
    calling `SqlAlchemyRecoveryRepository.mark_resolved` directly
    (bypassing `RecoveryService` entirely) after a concurrent
    `record_attempt` already advanced `record_version` SUCCEEDS with no
    complaint, where the SAME scenario through `RecoveryService.
    resolve_recovery` raises `RecoveryResolutionStaleVersion`
    (`test_denies_a_stale_record_version_after_a_concurrent_attempt`).
    ACTUAL: confirmed
    (test_mut_pkg24_03_bypassing_the_service_guard_allows_a_stale_write).
    INTERPRETATION: the version-staleness guard is real and enforced,
    but ONLY at the `RecoveryService` layer -- no independent, second
    layer of defense exists at the repository/DB layer for THIS
    specific invariant (unlike the identity-immutability/
    result-transition invariants, which PKG-23's own DB triggers
    enforce independently of the Python layer). Disclosed as a genuine,
    not-yet-closed gap in KNOWN_LIMITATIONS, not silently accepted.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TEST_RESULTS: `tests/recovery/boundaries/test_recovery_service.py`
  exercises the full, real governed path end to end:
  `NonProofWorkspaceBootstrap` (PKG-04) -> real
  `SqlAlchemyCommandRepository`/`SqlAlchemyCommitRepository` (PKG-10/13)
  -> a real, committed `Command`/`CommitUnit` pair -> a real, persisted
  `RecoveryRecord` (PKG-23) -> `RecoveryService.resolve_recovery` ->
  `boundaries.registry.evaluate_chain` over REAL
  `Bnd001IdentityEvaluator`/`Bnd002WorkspaceEvaluator(SqlAlchemyWorkspaceRepository)`/
  `Bnd017FailureIndeterminateEvaluator(SqlAlchemyRecoveryRepository)`/
  `Bnd018RecoveryRollbackEvaluator` -> a real `connection.begin_nested()`
  SAVEPOINT write via `SqlAlchemyRecoveryRepository.mark_resolved` -> a
  fresh re-read confirming the persisted result. No fake/mock repository
  anywhere in this chain.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-23's tests) re-run alongside PKG-24's new tests, both without a
  live database (660 passed, 356 skipped) and against a real
  PostgreSQL 17 instance with all 17 migrations applied
  (`tests/ apps/api/tests apps/worker`: 1016 passed, 1 skipped). Zero
  regressions; every previously-green test remains green.

P_CLAIMS_TESTED:
  P-20 (INDETERMINATE blocks blind retry): FULL CLOSURE for the first
    time -- a real BND-017 evaluator now consumes `LpvsResult`/
    `RecoveryRecord`-shaped facts and structurally blocks every
    dependent consequential operation on a target while it remains
    UNRESOLVED, proven against a real, persisted, blocking
    `RecoveryRecord` row (attack #4/#15/#26 above).
  P-21 (Recovery cannot create/inherit authority): FULL CLOSURE for the
    deterministic (SYSTEM_SERVICE) path -- BND-018's own unconditional
    AI-actor DENY, BND-001's own SYSTEM_SERVICE-only actor scoping
    (double-enforced, attack #2), the explicit, human-confirmed
    CommitCoordinator-bypass disclosure (AUTHORITY_PATH), and the
    `restores_already_legitimized_state`-gated write together prove
    recovery neither invents nor inherits human authority for this
    path. The HUMAN_USER discretionary (RC-07) dimension of P-21
    remains `SUCCESSOR_NOT_BUILT` -- no real `AuthorityResolver` wiring
    exists for it yet, disclosed, not fabricated.

PROOF_ARTIFACTS:
  - 1016-test live-database pass (0 regressions against PKG-23's own
    970-test baseline), including 26 distinct adversarial proofs (14
    mandatory + 12 novel/adapted) and 3 mutation-kill proofs
  - A real, persisted, blocking `RecoveryRecord` row whose
    `blocked_target_refs` structurally denies a dependent operation
    through the real BND-017 evaluator and the real
    `SqlAlchemyRecoveryRepository.is_target_blocked` SQL query
  - A real end-to-end `RecoveryService.resolve_recovery` write, proven
    through 4 independently-terminal DENY paths (one per boundary) plus
    one full ALLOW path -- structural proof the entire 4-boundary chain
    is load-bearing, not merely present
  - A real, live-DB proof that replaying an already-resolved Recovery
    Command with its original `expected_record_version` is refused, not
    silently re-applied
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full upgrade to head b7ec21429b53,
    a downgrade(-1)/re-upgrade cycle, and a `psql` schema inspection
  - Diff audit (inline answers below), cross-checked against `git
    status --short` before staging per this session's own standing
    instruction
  - Mutation-kill analysis (3 mutations, all verified killed, using a
    disclosed, permission-safe adaptation of this session's established
    methodology)

FORBIDDEN_DEPENDENCY_CHECK: PASS (one new, disclosed, cited extension:
  boundaries -> recovery, 20th overall; justified as
  bidirectional-but-disjoint-submodule, mirroring the existing
  commit <-> persistence precedent from PKG-11/13 -- `recovery`'s own
  allow-list already included `boundaries` since PKG-00, and no file in
  `packages/boundaries/` other than the two new BND-017/018 evaluators
  imports `recovery`, so no actual Python import cycle exists)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: none new. `RecoveryOutcome`/
    `RecoveryClass`/`ConsequenceCertainty`/`FailureClass` are all
    reused, unmodified, from PKG-22/23. `RecordVersion` (a predecessor
    type, `semantic_types.versions`) is reused, not invented.
  New transition: none -- `recovery_records.result`'s own
    UNRESOLVED -> terminal topology (PKG-23) is unchanged; the two new
    columns are plain data, not new state.
  New authority path: yes, extensively disclosed -- see AUTHORITY_PATH.
    This is the one significant architectural decision this package
    makes, and it was surfaced to and confirmed by the user via
    `AskUserQuestion` rather than invented silently.
  New DB write path: yes, disclosed -- `RecoveryService.resolve_recovery`
    -> `RecoveryRepository.mark_resolved`, wrapped in a real
    `connection.begin_nested()` SAVEPOINT, producing NO `CommitUnit`/
    `AuditEvent`/`OutboxRecord` (see AUTHORITY_PATH for why this is
    correct, not a shortcut).
  Weakened boundary: none -- two NEW boundaries were created (BND-017/
    018), no existing boundary was modified or weakened. The mutation-
    testing methodology itself was adapted mid-package (see
    MUTATION_TESTS) because this session's own tool classifier now
    denies in-place source edits that weaken a security check, even
    temporarily and reverted -- a tooling-environment change, not a
    package-scope decision, and not a weakening of anything shipped.
  Easier test / removed negative test / admin shortcut / projection or
    cache truth / AI canonical authority / broader Workspace scope:
    none.
  Changed migration semantics: none -- no prior migration edited, only
    a new, purely additive migration on this package's own predecessor
    table (`recovery_records`, PKG-23's own).
  Changed a predecessor's own public dataclass shape: yes, disclosed --
    `RecoveryRecord` (PKG-23's own) gained a new REQUIRED
    `record_version: RecordVersion` field with no default, which
    required a regression fix to PKG-23's own
    `tests/recovery/test_recovery_record.py` (two construction sites).
    This follows this codebase's own established "retrofit a
    predecessor's own disclosed gap in the package that first needs it"
    pattern (PKG-13's four FK retrofits, PKG-18/19's forward-reference
    closures) -- 14 section 7.1's own core-tables row for
    `recovery_records` named "record_version" as its literal Version
    column from the start; PKG-23's own field list (built strictly from
    10 section 63's "Minimum semantics" list, which itself has no
    version field) never added one until this package, the first to
    genuinely need a real optimistic-concurrency value.
  Forbidden dependency: one new, disclosed, cited extension --
    boundaries -> recovery (20th overall, see
    FORBIDDEN_DEPENDENCY_CHECK).
  Files touched outside this package's own new-file set:
    `packages/persistence/tables.py`,
    `packages/persistence/recovery_repository.py`,
    `packages/recovery/models.py`,
    `scripts/check_architecture_dependencies.py`,
    `tests/recovery/test_recovery_record.py` -- all five explicitly the
    disclosed retrofit/extension points this package's own new fields/
    boundaries require; no other predecessor file touched. No
    previously-green test required a fix beyond the one disclosed
    `record_version` regression above. No production bug was found this
    package -- every new test passed on its first run, pure and
    live-DB alike, except the anticipated (not a bug) PKG-23 regression
    fix.
  `git status --short` immediately before staging matched this section
    exactly: 5 modified files, 4 new files
    (`migrations/versions/b7ec21429b53_recovery_command_fields.py`,
    `packages/application/recovery_handler.py`,
    `packages/boundaries/bnd_017_failure_indeterminate.py`,
    `packages/boundaries/bnd_018_recovery_rollback.py`) plus 2 new test
    files and 1 new test directory
    (`tests/boundaries/test_bnd_017_failure_indeterminate.py`,
    `tests/boundaries/test_bnd_018_recovery_rollback.py`,
    `tests/recovery/boundaries/`), nothing else, no tooling/lock files.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  REQUEST -> ACTOR: `RecoveryService.resolve_recovery`'s own `actor:
  ActorIdentity` parameter, proven at BND-001
  (`required_actor_classes={SYSTEM_SERVICE}`) -> WORKSPACE: proven at
  BND-002 against a real `SqlAlchemyWorkspaceRepository`, using the
  target `RecoveryRecord`'s own `workspace_scope_ref` as the one
  resolved object -> CURRENT STATE: the target `RecoveryRecord` itself,
  freshly re-read from `RecoveryRepository.get` -> CURRENT GOVERNANCE /
  CURRENT AUTHORITY: NOT resolved via `AuthorityResolver` for this path
  -- see AUTHORITY_PATH; `restores_already_legitimized_state` is the
  caller-supplied fact substituting for it, per the confirmed
  architectural decision -> HUMAN DECISION: NOT_APPLICABLE for the
  deterministic path (no `Decision` object; the HUMAN_USER branch,
  unexercised by this prototype's own MINIMUM scope, would need one) ->
  EVIDENCE: NOT_APPLICABLE for this package's own scope -- see
  EVIDENCE_PATH -> BOUNDARIES: BND-001 -> BND-002 -> BND-017 -> BND-018,
  strictly sequential, first non-ALLOW terminal (proven by attack #21)
  -> BND-014: NOT_APPLICABLE, deliberately -- see AUTHORITY_PATH ->
  COMMAND: `RecoveryService.resolve_recovery` itself is the Command,
  but issues no `CommandEnvelope`/`AttemptId` of its own (14's own
  manifest names no such Command type for this package; the underlying
  `original_command_id` it reads is a read-only reference to an ALREADY
  -committed predecessor Command) -> COMMIT UNIT: NOT_APPLICABLE,
  deliberately -- see AUTHORITY_PATH -> CANONICAL MUTATION:
  NOT_APPLICABLE -- `RecoveryRecord` remains an OPERATIONAL_RECORD, 10
  section 63's own explicit classification -> AUDIT: NOT_APPLICABLE for
  this write (no `AuditEvent` produced; `audit_reconstruction_preserved`
  is a caller-supplied invariant fact BND-018 checks, not something
  this package itself writes) -> OUTBOX / EVENT: NOT_APPLICABLE (no
  Event, no OutboxRecord -- see EVENTS_CREATED) -> RESULTING STATE: a
  real, persisted `recovery_records` row transitioned from UNRESOLVED to
  a terminal `RecoveryOutcome`, `record_version` advanced by one, live-
  DB-joined and constraint-proven end to end via
  `tests/recovery/boundaries/test_recovery_service.py`.

KNOWN_LIMITATIONS:
  - RC-07 (Manual/Discretionary Recovery, HUMAN_USER) remains
    `SUCCESSOR_NOT_BUILT` -- `current_human_authority_confirmed` is a
    caller-supplied fact, not a real `AuthorityResolver` read; no
    concrete `AuthorityClass`/Decision Right is wired to it anywhere in
    04. 12's own MINIMUM scope never exercises this branch.
  - BND-011 (SYSTEM_DERIVED AUTHORITY BOUNDARY) does not exist anywhere
    in this codebase and is not assigned to any package -- the central
    finding of this package's own `AskUserQuestion` consultation.
    `restores_already_legitimized_state` is this package's own honest
    substitute, disclosed, not a resolution of the underlying gap.
  - `RecoveryService` does not call BND-013 (Evidence) -- see
    EVIDENCE_PATH. A future, richer Recovery Command needing
    Evidence-gated recovery would add it to its own chain.
  - The `record_version` staleness guard is enforced ONLY at the
    `RecoveryService` Python layer -- `SqlAlchemyRecoveryRepository.
    mark_resolved`'s own SQL `WHERE` clause has no `record_version`
    condition, proven exploitable by MUT-PKG24-03 when the repository
    is called directly, bypassing the service. Unlike the identity-
    immutability/result-transition invariants (PKG-23's own DB
    triggers, independent of the Python layer), this specific guard has
    no second, independent layer of defense. Mitigated structurally
    (`RecoveryService` is the one documented production caller,
    PUBLIC_INTERFACES_CREATED), but disclosed as a real, not-yet-closed
    gap a future hardening pass could close with a
    `WHERE record_version = :expected` condition and a rowcount check.
  - This session's mutation-testing methodology changed mid-package:
    the previously-used "temporarily weaken production source in
    place, confirm red, revert" technique (used successfully PKG-20
    through PKG-23) is now denied by this session's own auto-mode tool
    classifier as a security-weakening action. Adapted to test-only
    mutant code (PKG-21's own precedent) and a structural
    guard-necessity proof -- disclosed as a tooling-environment change,
    not a package-scope decision.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Neither is touched by this package's own scope.

NEW_GAPS_DISCOVERED:
  1. `record_version` gap on `recovery_records` (14 section 7.1's own
     core-tables row named it; PKG-23 never added it) -- retrofitted
     THIS package, disclosed above and in `recovery.models`'s own
     module docstring.
  2. BND-011 (SYSTEM_DERIVED AUTHORITY BOUNDARY) does not exist and is
     not assigned to any package (see AUTHORITY_PATH/KNOWN_LIMITATIONS).
  3. The service-layer-only, non-DB-enforced `record_version` staleness
     check (see KNOWN_LIMITATIONS/MUT-PKG24-03).

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. BND-017/018's own ALLOW/
  DENY/REQUIRE reason codes transcribe 06 section 24/25's own PURPOSE/
  ALLOW/DENY/REQUIRE/VALIDATION lists directly. `requested_operation`
  stays a plain string, per 06's own "Examples:" (not "defines"/"exact")
  language for that field -- not formalized into an invented closed
  enum. `RecoveryResolutionFacts`/`RecoveryService` are disclosed
  `[IMPLEMENTATION CHOICE]` shapes for wiring already-specified
  boundaries into one governed write, not new domain concepts. The
  CommitCoordinator-bypass is the one significant architectural
  decision made this package, and it was surfaced to and confirmed by
  the user rather than invented silently (see AUTHORITY_PATH). No new
  Decision Right, `AuthorityClass` value, Event, or canonical write path
  was introduced.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-25 becomes DAG-eligible once its own
  required predecessors are verified. Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-24's own coding prompt: "Respect the
  phase boundary. Package completion does not authorize the next
  phase." Do not authorize PKG-25 without explicit human authorization
  naming the package and this package's own commit hash.
```
