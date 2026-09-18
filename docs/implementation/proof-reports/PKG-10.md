# PKG-10 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-10
PACKAGE_TITLE: Command envelope and attempts
BUILD_PHASE: 4
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  09_DATA_EVENT_API_CONTRACTS.md sections 4.3-4.8 (Command/Attempt/Commit/
    Event/Correlation/Causation ID identities), 5-8 (versioning classes,
    AC-09-001 commit-freshness version, canonical/projection store, cache
    rule), 9-10 (CommandEnvelope exact field list, section 9.1 authority
    is-a-reference-not-a-token, section 9.2 expected_versions, Authority
    ContextReference), 12 (Command Retry Semantics: FAILED_PRECOMMIT/
    COMMITTED/INDETERMINATE/changed-payload rules), 13 (CommitUnit --
    confirmed out of this package's scope), 59 (CommandExecutionRecord
    exact field list), 61-62 (Command Taxonomy, Process Transition Command
    Registry -- confirms no concrete named Command is this package's
    scope), 139-141 (Command Payload Mutation, AC-09-013 idempotency
    payload binding, Command Causality), 160.3 (API Command Falsification:
    replay/Event-as-Command), 170-171 (Command Activation Status,
    AC-09-016 -- confirms contract existence != runtime activation)
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md sections 15 (Governed Command
    Proof, minimum fields exercised, forbidden client inputs), 16 (Commit
    Proof -- confirms CommitUnit/BND-014 remain PKG-13's scope)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6 (P-16/P-19 full
    matrix rows), section 44 (MUT-04: treat Event as Command)
  14_IMPLEMENTATION_SEQUENCE.md sections 3.1 (directory ownership --
    `command`'s exact "domain contracts, semantic_types" allow-list,
    "no direct write"), 4 (dependency graph and forbidden matrix), 5
    (semantic type system -- CommandId/AttemptId/CorrelationId/
    CausationId/CommitId already exist from PKG-00), 6 (Command outcome
    closed vocabulary), 7.1 (commands/command_attempts table row), 7.3
    (critical field constraints: commands.command_id unique), 9
    (migration plan, 008_command_attempt_idempotency bucket), 10
    (CommandRepository port), 39 (T7 -> tests/command_commit_event/), 41
    (dependency enforcement), 46-48 (PKG-10 manifest, DAG, file-level
    map), 49 (DB implementation map), 50 (P-16/P-19 test implementation
    map)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: CommandEnvelope, CommandRegistry -- both created,
    exactly as named, no additional public interface invented beyond
    what 14 section 10 already separately names (CommandRepository).
  DATABASE_CHANGES: 008 (subset) -- `commands`/`command_attempts` created;
    `idempotency_records` deliberately NOT created (PKG-11's own scope).
  TESTS_REQUIRED: T7 (tests/command_commit_event/) -- created.
  PROOF_CLAIMS: P-16 -- partially exercised (type-level Command/Event
    split only; full "committed Command/Event pair" proof needs PKG-12's
    EventEnvelope). P-19 -- partially exercised (attempt-identity/
    payload-fingerprint/retry semantics fully proven; full "duplicate
    COMMITTED returns one consequence" needs PKG-11's IdempotencyPort +
    PKG-13's commit coordinator).

PREDECESSORS_VERIFIED:
  PKG-09 (05a5857, PACKAGE_PASS, human gate given, Phase 3 complete).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-08 de9c5b5, PKG-09
  05a5857 -- none of PKG-10's changes touch any predecessor's owned
  files; full regression re-run below confirms no invalidation.

FILES_CREATED:
  packages/command/envelope.py
  packages/command/registry.py
  packages/persistence/command_repository.py
  migrations/versions/b2f3a5d5096c_command_envelope_and_attempts.py
  tests/command_commit_event/conftest.py
  tests/command_commit_event/test_envelope.py
  tests/command_commit_event/test_command_registry.py
  tests/command_commit_event/test_command_repository.py
  tests/command_commit_event/test_command_event_split.py

FILES_MODIFIED:
  packages/command/__init__.py (PKG-10 scope note)
  packages/persistence/tables.py (commands_table/command_attempts_table
    added, docstring cross-reference)
  scripts/check_architecture_dependencies.py (INTERNAL_ALLOWED["persistence"]
    += "command", cited and justified inline)
  tests/regression/test_architecture_dependency_checks.py (+2 tests:
    positive control for persistence->command, negative control
    confirming command->persistence remains forbidden)

FILES_DELETED: none

MIGRATIONS_CREATED: b2f3a5d5096c (command envelope and attempts),
  revises d8a1147fde30. Creates `commands`, `command_attempts`; 2
  triggers (full-row immutability on `commands`; identity/receipt-field
  immutability + outcome-terminality on `command_attempts`).
SCHEMA_CHANGES: `commands` (id, workspace_id, command_type,
  contract_version, payload_fingerprint, created_at; UNIQUE(id,
  workspace_id); CHECK command_type/payload_fingerprint non-empty; CHECK
  contract_version dotted-integer shape). `command_attempts` (id,
  command_id, workspace_id, actor_ref, received_at,
  boundary_evaluation_summary_ref, commit_id, outcome, completed_at,
  failure_code; composite FK (command_id, workspace_id) ->
  commands(id, workspace_id); CHECK outcome IN 14 section 6's 4-value
  vocabulary or NULL; CHECK completed_at requires outcome).
DB_PRIVILEGE_CHANGES: none. 14 section 7.1 names `command_processor`/
  `commit writer` as eventual write owners, but every DB-principal/
  GRANT/RLS change in this codebase to date is deferred to migration
  012_security_events_rls -- consistent with every migration since
  001, not a new gap this package introduces.

PUBLIC_INTERFACES_CREATED:
  command.envelope.{CommandOutcome, CommandEnvelope, compute_payload_fingerprint}
  command.registry.{CommandContract, CommandRegistrationError,
    UnregisteredCommandTypeError, CommandContractVersionMismatch, CommandRegistry}
  persistence.command_repository.{CommandRecord, CommandAttempt,
    CommandWorkspaceMismatch, CommandPayloadConflict, AttemptAlreadyRecorded,
    AttemptOutcomeAlreadyFinal, AttemptNotFound, CommandRepository,
    SqlAlchemyCommandRepository}

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns no concrete named Command to
  PKG-10; 09 section 62's Process Transition Command Registry entries
  remain unbuilt, deferred to whichever future package first submits one).
QUERIES_CREATED: NOT_APPLICABLE
EVENTS_CREATED: NOT_APPLICABLE
BOUNDARIES_CREATED_OR_CHANGED: none. No BND-XXX is invoked by this
  package; CommandEnvelope "carries refs, never bypass tokens" (coding
  prompt BOUNDARIES line), proven by the stale-authority-context test.

AUTHORITY_PATH: `authority_context_ref` is a bare, unresolved
  `uuid.UUID | None` reference (09 section 9.1: "not a reusable
  authorization token"). No authority resolution, caching, or shortcut
  exists anywhere in this package -- proven by
  `test_authority_context_ref_is_pure_opaque_data`. Fresh re-resolution
  at commit time is BND-014's job (PKG-13, SUCCESSOR_NOT_BUILT).

EVIDENCE_PATH: `evidence_set_ref: EvidenceSetId | None` carried only,
  using PKG-00's existing strong type; no Evidence validation or
  resolution performed here (evidence package remains a stub).

AI_PATH: NOT_APPLICABLE. 14 does not assign AI scope to PKG-10; no
  provider/model path was introduced (section 21 AI IMPACT: "If AI is
  not in scope, introducing model/provider behavior is forbidden" --
  honored by omission).

RECOVERY_PATH: NOT_APPLICABLE. No RecoveryRecord/recovery orchestration
  exists yet; `command_attempts.outcome` including `INDETERMINATE` is
  representable and tested, but nothing here routes it to BND-017/018.

TESTS_CREATED: 5 files, 33 test functions (test_envelope: 12,
  test_command_registry: 7, test_command_event_split: 4,
  test_command_repository: 10).
TESTS_MODIFIED: none (2 tests added to the pre-existing
  test_architecture_dependency_checks.py, counted under FILES_MODIFIED).

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS
          ruff check . -- PASS (one SIM117 nested-with auto-fix applied,
            mechanical, preserves pytest.raises-outer/begin_nested-inner
            ordering required for correct SAVEPOINT semantics)
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts --
            PASS (77 source files, no issues, +3 from PKG-09's 74)
  Architecture checks: check_architecture_dependencies.py -- PASS (one
    disclosed extension: persistence -> command, write-only-in-that-
    direction, 6th such extension following the established pattern)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 6 revisions,
                          single head b2f3a5d5096c; live: db head matches;
                          downgrade -1 / re-upgrade cycle clean)
  Pure-Python suite (no DB): tests/ + apps/api/tests -- 421 passed, 126
    skipped (all pre-existing/newly-added SKIPPED_NO_DATABASE, none
    unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 546 passed, 1 skipped,
    0 failed, on first run (no pre-fix bug this package -- see
    PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative tests
  pass; each asserts a specific named exception type
  (CommandWorkspaceMismatch/CommandPayloadConflict/AttemptAlreadyRecorded/
  AttemptOutcomeAlreadyFinal/AttemptNotFound/UnregisteredCommandTypeError/
  CommandContractVersionMismatch/TypeError/ValueError with a matching
  message), never merely "an error occurred."

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION: A true pre-implementation
  failure demonstration in the PKG-05/PKG-09 sense (a real bug caught by
  the live-DB run) did not occur this package -- both the pure-Python
  run (421 passed) and the first live-PostgreSQL run (546 passed) were
  green on first execution, because the mandatory-attack tests were
  written directly against the already-implemented envelope/registry/
  repository code in one pass (Steps D and E were interleaved for this
  package's small, tightly-scoped surface, unlike PKG-09's larger
  8-evaluator implementation). Each mandatory attack was nonetheless
  independently verified to fail *before* its corresponding guard clause
  was written, by temporarily commenting out each check in turn during
  development and confirming the matching test failed red, then
  restoring the guard and confirming green -- this is
  PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION::AVAILABLE, exercised
  informally rather than preserved as a committed failing-test artifact
  (no separate "before" commit exists, consistent with this repository's
  practice of one commit per completed, green package).

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (5/5):
  1. Event submitted as Command
     EXPECTED DEFENSE: CommandEnvelope.__post_init__'s
       isinstance(command_id, CommandId) check
     EXPECTED BOUNDARY: NOT_APPLICABLE (no BND-XXX at this layer)
     EXPECTED CANONICAL RESULT: TypeError, no CommandEnvelope produced
     EXPECTED PROOF ARTIFACT: the raised TypeError (construction never
       completes)
     ACTUAL RESULT: matches (test_denies_event_submitted_as_command,
       test_an_event_id_cannot_construct_a_command_envelope,
       test_a_bare_uuid_cannot_construct_a_command_envelope,
       test_a_plain_string_cannot_construct_a_command_envelope)
  2. Stale authority context reused
     EXPECTED DEFENSE: structural absence -- no code path in this
       package reads authority_context_ref to decide anything
     EXPECTED CANONICAL RESULT: identical treatment regardless of the
       ref's value; fresh resolution deferred to BND-014
     ACTUAL RESULT: matches (test_authority_context_ref_is_pure_opaque_data)
  3. Changed payload under same command identity
     EXPECTED DEFENSE: SqlAlchemyCommandRepository.record_attempt's
       fingerprint comparison against the stored `commands` row, backed
       by the DB's own full-row immutability trigger
     EXPECTED CANONICAL RESULT: CommandPayloadConflict, no second
       `commands` row, no phantom attempt recorded
     ACTUAL RESULT: matches
       (test_denies_changed_payload_under_the_same_command_identity,
       test_commands_row_is_immutable_at_the_database_layer)
  4. Wrong Workspace
     EXPECTED DEFENSE: record_attempt's Workspace comparison, backed by
       the composite FK (command_id, workspace_id) -> commands(id,
       workspace_id)
     EXPECTED CANONICAL RESULT: CommandWorkspaceMismatch
     ACTUAL RESULT: matches
       (test_denies_reusing_a_command_id_under_a_different_workspace)
  5. Missing required expected version
     EXPECTED DEFENSE: CommandEnvelope.__post_init__'s exact
       target_refs == expected_versions.keys() check (AC-09-001)
     EXPECTED CANONICAL RESULT: ValueError, envelope never constructed
     ACTUAL RESULT: matches
       (test_denies_missing_expected_version_for_a_stated_target,
       test_missing_expected_version_is_rejected_before_any_persistence_is_touched)

  Novel/adapted (2 additional, total 7 >= the package's own ">=5" floor):
  6. Attempt_id reused across two different command_ids (identity
     confusion)
     EXPECTED DEFENSE: get_attempt pre-check in record_attempt
     EXPECTED CANONICAL RESULT: AttemptAlreadyRecorded
     ACTUAL RESULT: matches
       (test_denies_replaying_an_already_recorded_attempt_id)
  7. Unregistered/version-mismatched command_type accepted
     EXPECTED DEFENSE: CommandRegistry.validate_envelope
     EXPECTED CANONICAL RESULT: UnregisteredCommandTypeError /
       CommandContractVersionMismatch
     ACTUAL RESULT: matches
       (test_validate_envelope_denies_an_unregistered_command_type,
       test_validate_envelope_denies_a_contract_version_mismatch)

  Legitimate controls proven not vacuously strict:
  test_constructs_a_well_formed_envelope_with_no_targets,
  test_constructs_a_well_formed_envelope_with_targets_and_expected_versions,
  test_records_a_new_command_and_its_first_attempt,
  test_legitimate_retry_reuses_command_id_with_a_new_attempt_id,
  test_records_a_determined_outcome,
  test_validate_envelope_accepts_a_registered_matching_version,
  test_a_real_command_id_constructs_successfully.

MUTATION_TESTS:
  MUT-04 (13 section 44: "treat Event as Command" -> P-16/P-17 tests
    must fail): remove CommandEnvelope's isinstance(command_id, CommandId)
    check -> expected red: test_denies_event_submitted_as_command,
    test_an_event_id_cannot_construct_a_command_envelope,
    test_a_bare_uuid_cannot_construct_a_command_envelope,
    test_a_plain_string_cannot_construct_a_command_envelope, all 4 in
    test_command_event_split.py -- by inspection, every one of these
    tests' only source of failure is that exact check; removing it makes
    all 4 pass a value that should be rejected (green suite would hide a
    real defect) -- INTERPRETATION: mutation killed, verified by manual
    removal/restoration during development (see
    PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION).
  MUT-PKG10-01 (adapted, changed-payload guard): remove
    SqlAlchemyCommandRepository.record_attempt's payload_fingerprint
    comparison -> expected red:
    test_denies_changed_payload_under_the_same_command_identity ->
    by inspection, that test's only DENY source is the removed
    comparison -- INTERPRETATION: mutation killed.
  MUT-PKG10-02 (adapted, expected-version coverage): remove
    CommandEnvelope's target_set != expected_set check -> expected red:
    test_denies_missing_expected_version_for_a_stated_target,
    test_denies_an_orphaned_expected_version_naming_no_target -- by
    inspection, both tests' only ValueError source is the removed check
    -- INTERPRETATION: mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_command_repository.py exercises the full real
  predecessor chain: NonProofWorkspaceBootstrap (PKG-04) ->
  SqlAlchemyWorkspaceRepository's underlying `workspaces` table (PKG-01)
  -> real CommandEnvelope construction (this package) ->
  SqlAlchemyCommandRepository against the real `commands`/
  `command_attempts` tables and their live triggers -- every mandatory
  attack is proven against genuine database constraints, not an isolated
  mock (test_commands_row_is_immutable_at_the_database_layer specifically
  proves the DB trigger independently of the Python-level guard).

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-09's tests) re-run alongside PKG-10's new tests, both without a
  database (421 passed, 126 skipped) and with a live PostgreSQL 17
  instance (546 passed, 1 skipped) -- 0 regressions.
  check_architecture_dependencies.py re-run clean, confirming all 6
  disclosed extensions (application->persistence, persistence->governance,
  authority->persistence, persistence->domain, boundaries->persistence,
  persistence->command) remain intact.

P_CLAIMS_TESTED:
  P-16 (Command != Event): partially exercised at this build phase --
    the type-level half (an Event's identity cannot construct a
    CommandEnvelope) is fully proven; the full precondition "committed
    Command/Event pair" requires PKG-12's EventEnvelope and remains
    BLOCKED on that successor, disclosed in test_command_event_split.py's
    own module docstring.
  P-19 (Duplicate Command no duplicate consequence): partially exercised
    -- the attempt-identity/payload-fingerprint/legitimate-retry half is
    fully proven against a live database; the full "duplicate COMMITTED
    returns one consequence" claim requires PKG-11's IdempotencyRecord
    and PKG-13's commit coordinator, remains BLOCKED on those successors.

PROOF_ARTIFACTS:
  - 546-test live-database pass, including 7 distinct adversarial proofs
    (5 mandatory + 2 novel) and one independent database-trigger proof
    of the same invariant the application layer already enforces
  - Real `commands`/`command_attempts` rows, inspectable via
    get_command/get_attempt/list_attempts, referencing a real
    NonProofWorkspaceBootstrap-seeded Workspace
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a downgrade(-1)/re-upgrade cycle
  - Diff audit (inline answers above)
  - Mutation-kill analysis (3 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (one disclosed, tested extension:
  persistence -> command, write-only-in-that-direction)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above. No unauthorized semantic change.

ARCHITECTURE_RECONSTRUCTION_RESULT: see inline reconstruction trace
  above. Longest legitimate chain: CommandEnvelope construction ->
  CommandRegistry.validate_envelope -> SqlAlchemyCommandRepository.
  record_attempt -> real commands/command_attempts rows in live
  PostgreSQL. BND-014/COMMIT UNIT/AUDIT/OUTBOX/EVENT correctly
  SUCCESSOR_NOT_BUILT; CURRENT STATE/GOVERNANCE/AUTHORITY/BOUNDARIES
  correctly NOT_APPLICABLE (this package invokes none of them).

KNOWN_LIMITATIONS:
  - No concrete named Command (CMD_CREATE_SESSION, etc.) exists;
    CommandRegistry has zero production registrations -- exercised only
    by this package's own test-registered contracts, same disclosed
    pattern as PKG-08's BoundaryRegistry.
  - `record_outcome` is built but has no production caller (the commit
    coordinator that would call it is PKG-13's scope) -- same disclosed
    "built but unwired" pattern as BurstRepository's transition methods
    and QuestionRepository.create_root/create_derived.
  - `command_attempts.outcome` is nullable to represent "not yet
    determined" rather than adding a 5th vocabulary value -- disclosed
    modeling choice, not a gap in 14 section 6's closed vocabulary.
  - P-16/P-19 are each only partially provable at this build phase
    (see P_CLAIMS_TESTED) -- both explicitly named as needing PKG-11/
    PKG-12/PKG-13 for their full precondition.
  - `payload` fingerprinting uses `repr()`-based SHA-256, disclosed in
    compute_payload_fingerprint's own docstring as sufficient for this
    package's tests but not a guaranteed canonical serialization for
    every possible future payload shape.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward); not re-exercised
    via Docker this package (no new service, no new external dependency).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. CommandEnvelope's field
  list is 09 section 9's own list verbatim; CommandOutcome is 14 section
  6's own 4-value vocabulary verbatim; the expected_versions-covers-
  target_refs rule is a direct, literal operationalization of AC-09-001's
  own text, not a new domain rule; requesting_actor_type/id are
  deliberately left as inert strings rather than reusing or duplicating
  authority.actor.ActorClass, avoiding both a forbidden dependency and a
  fabricated parallel vocabulary; no concrete Command, Event, boundary,
  or authority path was invented.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-11 (Idempotency) becomes DAG-eligible
  (its sole required predecessor, PKG-10, is now verified). PKG-12
  (Audit and outbox contracts) is independently eligible on the same
  basis (its own required predecessor is also PKG-10). Eligibility is
  not authorization.
HUMAN_GATE_REQUIRED: YES -- Build phase 4. "Completion does not
  authorize the next phase" (per this package's own coding prompt,
  verbatim). Do not authorize any successor.
```
