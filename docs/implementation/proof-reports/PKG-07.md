# PKG-07 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-07
PACKAGE_TITLE: Question Burst and frozen set
BUILD_PHASE: 2
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  01 §12.5 GAP-01-003 (Active-burst AI observer/recorder semantics, UNDERDEFINED)
  03 §19 QuestionBurst State Machine, §20 TRN-BURST-001..005, §21 CONFLICT-007
    (Burst duration, OPEN SOURCE TENSION), §22 GAP-03-002 (pause/timer, UNDERDEFINED)
  04 §2.7 Authority Scope, §10 Session Control Authority (AC-04-002), §35-39
    AUTH-DEP-BURST-001..005
  06 §14 BND-008 Question Burst Contamination Boundary (full spec)
  08 §12 Question Burst AI Participation Modes (Mode A/B/C), §13 Mode Precedence
  12 §7 Authority Profile for Prototype, §8.1 Bootstrap sequence, §11 Question Burst
    Prototype (12-step sequence)
  13 §6 T4 scope, P-03/P-04 test-matrix rows
  14 §7.1 core tables, §9 migration plan, §10 repository ports (BurstRepository),
    §19 QUESTION AND BURST IMPLEMENTATION (fingerprint IMPLEMENTATION CHOICE)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: Burst operations -- created (domain state/transition types,
    BurstRepository, application-layer readiness compositor, contamination guard).
  DATABASE_CHANGES: 004 (burst subset, completing PKG-06's questions/lineage half of
    the conceptual bucket) -- created: question_bursts, burst_question_memberships,
    plus a retrofitted uq_sessions_id_workspace anchor on sessions.
  TESTS_REQUIRED: T2 (tests/transitions/), T4 (tests/boundaries/) -- both created,
    plus tests/ai/ for the mandatory AI-exclusion attack (14 §39: T6 -> tests/ai/).
  PROOF_CLAIMS: P-03 (frozen raw set) -- INTRODUCED-PARTIAL. P-04 (no AI
    contamination) -- INTRODUCED, fully exercised.

PREDECESSORS_VERIFIED:
  PKG-06 (06e9ea0, PACKAGE_PASS, human gate given) -- Question/QuestionOrigin types
  and questions/question_lineage tables consumed directly (composite-FK anchor
  pattern reused for question_bursts/burst_question_memberships).
  PKG-03 (820a397, PACKAGE_PASS, human gate given) -- AuthorityResolver genuinely
  invoked for the first time outside its own predecessor's test proofs.
  Also present and unbroken: PKG-00 dd4aad2, PKG-01 35ef80a, PKG-02 f976854,
  PKG-04 dd582ac, PKG-05 31427fb -- none of PKG-07's changes touch their owned
  files; full regression re-run below confirms no invalidation.

FILES_CREATED:
  migrations/versions/d8a1147fde30_burst_and_membership.py
  packages/domain/burst.py
  packages/domain/burst_membership.py
  packages/domain/burst_transitions.py
  packages/application/burst_contamination.py
  packages/application/burst_operations.py
  packages/persistence/burst_repository.py
  tests/transitions/test_burst_transition_registry.py
  tests/transitions/test_burst_transition_constraints.py
  tests/transitions/test_burst_operations_readiness.py
  tests/boundaries/test_burst_contamination_guard.py
  tests/ai/test_burst_ai_block.py

FILES_MODIFIED:
  packages/domain/__init__.py (PKG-07 content summary appended)
  packages/application/__init__.py (PKG-07 content summary appended)
  packages/persistence/tables.py (+question_bursts_table,
    +burst_question_memberships_table; +uq_sessions_id_workspace retrofit on
    sessions_table; docstring pointers to the new migration)

FILES_DELETED: none

MIGRATIONS_CREATED: d8a1147fde30_burst_and_membership (revises 33e1d1feed5b)

SCHEMA_CHANGES:
  ALTER TABLE sessions ADD CONSTRAINT uq_sessions_id_workspace UNIQUE (id, workspace_id)
    -- additive retrofit; PKG-05's migration had no consumer for this anchor yet.
  CREATE TABLE question_bursts (id, session_id, workspace_id FK, state, mode,
    started_at/paused_at/completed_at nullable, frozen_membership_fingerprint
    nullable, record_version; UNIQUE(id, workspace_id); composite FK
    (session_id, workspace_id) -> sessions(id, workspace_id); CHECK state in 4
    values; CHECK mode in 3 approved values AND separately CHECK mode='HUMAN_ONLY'
    (package-scope restriction); CHECK freeze-fingerprint biconditional with
    state='COMPLETED'; CHECK completed_at requires COMPLETED; CHECK
    record_version >= 1). Deliberately no duration/timer columns
    (CONFLICT-007/GAP-03-002, both open).
  CREATE TABLE burst_question_memberships (id, question_burst_id, question_id
    UNIQUE, workspace_id FK, captured_order, captured_at, capture_actor_user_id
    nullable FK, capture_origin, record_version; 2 composite FKs against
    question_bursts(id, workspace_id) and questions(id, workspace_id); CHECK
    capture_origin in 4 approved values AND separately ='HUMAN' (package-scope
    restriction); CHECK human-origin/actor biconditional; CHECK captured_order
    >= 0).
  CREATE FUNCTION/TRIGGER trg_question_bursts_enforce_initial_state (BEFORE
    INSERT): new Burst must be PREPARED.
  CREATE FUNCTION/TRIGGER trg_question_bursts_enforce_transition (BEFORE
    UPDATE): rejects any update once COMPLETED (full-row, not just state);
    otherwise validates the 5-pair 03 section 20 topology and record_version
    advance.
  CREATE FUNCTION/TRIGGER trg_burst_memberships_enforce_freeze (BEFORE INSERT
    OR DELETE): rejects the operation if the parent Burst is already COMPLETED.
  CREATE FUNCTION/TRIGGER trg_burst_memberships_enforce_immutable (BEFORE
    UPDATE): rejects every update unconditionally.
  Downgrade proven as pure schema removal, including clean removal of the
  sessions retrofit with all PKG-05-owned constraints/triggers left untouched
  (see PROOF_ARTIFACTS).

DB_PRIVILEGE_CHANGES: none (no new DB principal; BurstRepository's mutating
  methods are exercised only by tests, wired into no production caller).

PUBLIC_INTERFACES_CREATED:
  domain.burst.{BurstState, BurstMode, QuestionBurst} (frozen dataclass; mode
    restricted to HUMAN_ONLY by constructor)
  domain.burst_membership.{QuestionBurstMembership, compute_frozen_membership_fingerprint}
  domain.burst_transitions.{BurstTransitionId, BurstOperation,
    BurstAuthorityDependency, BurstTransitionSpec, BURST_TRANSITION_SPECS,
    BurstTransitionVerdict, BurstTransitionResolution,
    resolve_burst_transition[_by_operation_name|_to_state], legal_state_pairs}
    -- reuses session_transitions' BoundaryDependency/TransitionProofType/
    ProofObligation/ProofRequirement rather than duplicating them
  application.burst_contamination.{BurstOperationCategory,
    BurstContaminationVerdict, ContaminationDenyReason, BurstContaminationResult,
    evaluate_burst_contamination_guard} -- BND-008's testable invariant only,
    disclosed as necessary-not-sufficient
  application.burst_operations.{BurstOperationOutcome, BurstOperationReadinessResult,
    check_burst_operation_readiness} -- read-only; composes domain transition
    eligibility with a genuine AuthorityResolver.resolve() call, never writes
  persistence.burst_repository.{BurstRepository (Protocol), BurstConflict,
    SqlAlchemyBurstRepository} -- create/transition/freeze/get/add_member/
    list_members; no update_state, no post-freeze mutator of any kind

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns none to PKG-07's own manifest;
  the Command names in 14's architecture-wide registry table are Phase-4
  planning references, not this package's scope)
QUERIES_CREATED: NOT_APPLICABLE
EVENTS_CREATED: NOT_APPLICABLE
BOUNDARIES_CREATED_OR_CHANGED: a narrow, explicitly disclosed subset of
  BND-008 (the AI-exclusion testable invariant only) -- not the full boundary,
  not BoundaryEvaluationRecord persistence, not BND-001..018 (PKG-08 scope).

AUTHORITY_PATH: REAL for the first time in this codebase outside PKG-03/04's
  own predecessor proofs -- application.burst_operations.check_burst_operation_readiness
  calls AuthorityResolver.resolve() for AuthorityClass.SESSION_CONTROL_RIGHT at
  scope_type="WORKSPACE" (12 section 7's own resolution of the 04 section 2.7 /
  section 35-39 scope tension -- see domain.burst_transitions' module docstring
  for the full citation chain). No extension to AuthorityResolver itself was
  needed or made.

EVIDENCE_PATH: NOT_APPLICABLE (14 PKG-07 EVIDENCE: "None").

AI_PATH: AI is structurally excluded from every Burst lifecycle and
  content operation during ACTIVE/PAUSED, proven at three independent layers:
  (1) application.burst_contamination's pure fact function, (2)
  AuthorityResolver's actor-class check (AI_PROCESSOR can never hold a HABB),
  (3) no AI Gateway/provider/AIGeneration module exists to call at all. No AI
  output becomes canonical state or authority anywhere in this package.

RECOVERY_PATH: NOT_APPLICABLE (no recovery machinery exists yet).

TESTS_CREATED: 5 files, 47 test functions total (13 in
  test_burst_transition_registry.py, 8 in test_burst_contamination_guard.py,
  5 in test_burst_ai_block.py [1 parametrized x4], 8 in
  test_burst_operations_readiness.py, 13 in test_burst_transition_constraints.py)
TESTS_MODIFIED: none

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS (129 files clean)
          ruff check . -- PASS (2 mechanical import-order issues fixed, no
            semantic changes)
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts --
            PASS (64 source files, no issues)
  Architecture checks: check_architecture_dependencies.py -- PASS (no
    extension needed at all -- every dependency edge this package uses
    already existed from PKG-01/05/06)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 5 revisions,
                          single head d8a1147fde30; live: db head matches)
  Pure-Python suite (no DB): full tests/ + apps/api/tests -- 170 passed, 88
    skipped (all pre-existing SKIPPED_NO_DATABASE, none new)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 257 passed, 1 skipped, 0
    failed -- passed cleanly on the first live-DB run (no pre-fix failures
    this package; PKG-05/06's own pre-fix bugs were in test-harness code,
    and the same care applied here produced none this time)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative tests
  pass; each asserts a canonical/schema-level result (a specific exception
  type plus, where meaningful, the trigger's own RAISE text), never merely
  "an error occurred."

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION: A real dependency-architecture
  mistake was caught and fixed *before* any test ran: the first draft of
  the BND-008 contamination-guard module was written under
  `packages/domain/burst_contamination.py`, importing
  `authority.actor.ActorClass` -- but 14 section 3.1 gives `domain` exactly
  one permitted dependency (`semantic_types`), and `authority -> domain` is
  the only sanctioned direction. Caught during static review (the actual
  `check_architecture_dependencies.py` run would have failed it, but the
  mistake was found before that run was even needed), fixed by relocating
  the module to `packages/application/burst_contamination.py` -- the
  lowest layer in this package's authorized scope that may depend on both
  `domain` and `authority`. A second, smaller bug: the first draft of
  `QuestionBurstMembership` had no `workspace_id` field at all, but its
  matching persistence table requires one for the composite-FK
  Workspace-confinement pattern -- caught while writing the repository's
  row-mapping code (a placeholder value was about to be silently
  substituted), fixed by adding the field to the domain type with full
  validation, before any test was run against it.

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (6/6, all present, each proven at the layer(s) where a real
  proof exists):
  1. AI invocation ACTIVE
     EXPECTED DEFENSE: application.burst_contamination's contamination
       guard; independently, AuthorityResolver's actor-class check
     EXPECTED CANONICAL RESULT: BurstContaminationVerdict.DENY;
       AuthorityVerdict.DENIED
     ACTUAL RESULT: matches (test_ai_operation_during_active_is_denied,
       test_ai_analysis_during_active_human_only_burst_is_denied,
       test_ai_processor_actor_is_denied_authority_for_any_burst_operation)
  2. Modify Question after freeze
     EXPECTED DEFENSE: questions.origin/original_text immutability triggers
       (PKG-06, re-verified unaffected by this package's changes)
     ACTUAL RESULT: full regression suite re-run confirms PKG-06's own
       immutability tests still pass unchanged (208 -> 257 total, no
       regression)
  3. Add raw member after freeze
     EXPECTED DEFENSE: trg_burst_memberships_enforce_freeze (BEFORE INSERT)
     EXPECTED CANONICAL RESULT: sa.exc.DBAPIError, "raw membership is frozen"
     ACTUAL RESULT: matches (test_add_raw_member_after_freeze_is_rejected)
  4. Remove member after freeze
     EXPECTED DEFENSE: trg_burst_memberships_enforce_freeze (BEFORE DELETE)
     ACTUAL RESULT: matches (test_remove_member_after_freeze_is_rejected)
  5. Analyze before COMPLETED
     EXPECTED DEFENSE: contamination guard denies AI_ANALYSIS during
       ACTIVE/PAUSED; no analysis capability exists to invoke regardless
     ACTUAL RESULT: matches
       (test_ai_operation_during_active_is_denied,
       test_ai_operation_during_paused_is_also_denied)
  6. Timer auto-completes without authority
     EXPECTED DEFENSE: no timer field/mechanism exists at all (03 section 21/22
       omission); AuthorityResolver structurally denies SYSTEM_SERVICE actors
       (only HUMAN_USER can hold a HABB)
     ACTUAL RESULT: matches
       (test_system_service_actor_cannot_complete_a_burst_via_this_compositor)

  Novel/adapted (6 additional, exceeding the >=5 total minimum):
  7. PAUSED-state AI invocation (protection does not lapse when input is
     merely suspended, 03 section 19.4)
     ACTUAL RESULT: matches (test_ai_operation_during_paused_is_also_denied)
  8. Direct enum coercion (state, mode)
     ACTUAL RESULT: matches at both layers
       (test_direct_enum_coercion_of_state_is_rejected in the registry test,
       test_direct_enum_coercion_of_state_is_rejected in the DB constraint test)
  9. Non-HUMAN_ONLY mode construction
     ACTUAL RESULT: matches
       (test_non_human_only_mode_is_rejected_by_the_check_constraint)
  10. Cross-Workspace Burst target
      ACTUAL RESULT: matches
        (test_cross_workspace_burst_target_is_not_representable)
  11. Membership reassignment via direct UPDATE
      ACTUAL RESULT: matches
        (test_membership_reassignment_via_update_is_rejected)
  12. Ambiguous authority bindings never treated as success
      ACTUAL RESULT: matches
        (test_unresolved_ambiguous_bindings_is_never_treated_as_success)

  Negative controls also present: test_human_capture_during_active_is_allowed,
  test_human_actor_can_control_burst_lifecycle,
  test_system_service_can_control_burst_lifecycle (contamination guard is not
  vacuously strict), test_ready_when_authority_granted_and_transition_eligible
  (compositor proves a real positive path, not just denials).

MUTATION_TESTS:
  MUT-PKG07-01: remove the freeze-check SELECT from
    trg_burst_memberships_enforce_freeze -> expected red:
    test_add_raw_member_after_freeze_is_rejected and
    test_remove_member_after_freeze_is_rejected -> by inspection, both
    tests' pytest.raises(match="raw membership is frozen") has no other
    source for that text -- INTERPRETATION: mutation killed.
  MUT-PKG07-02: remove the COMPLETED full-row-immutability check from
    trg_question_bursts_enforce_transition (leaving only the pair-topology
    check) -> expected red: test_completed_burst_is_fully_immutable -> by
    inspection, that test updates only record_version (not state), which
    the pair-topology check alone would not catch -- INTERPRETATION:
    mutation killed.
  MUT-PKG07-03: remove the AI_PROCESSOR branch from
    evaluate_burst_contamination_guard -> expected red: all of
    test_ai_operation_during_active_is_denied,
    test_ai_operation_during_paused_is_also_denied,
    test_ai_actor_cannot_control_burst_lifecycle_in_any_state -> by
    inspection, every one of those asserts DENY specifically for
    ActorClass.AI_PROCESSOR with no other source -- INTERPRETATION:
    mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_burst_operations_readiness.py exercises the full
  predecessor chain for real: NonProofWorkspaceBootstrap (PKG-04) ->
  MembershipRepository/AuthorityBindingRepository (PKG-02) ->
  AuthorityResolver (PKG-03) -> domain.burst_transitions (this package) ->
  application.burst_operations (this package) -- a genuine multi-package
  relational proof, not an isolated mock of any layer.
  test_burst_transition_constraints.py exercises
  NonProofWorkspaceBootstrap -> challenges/sessions (PKG-05) ->
  questions (PKG-06) -> question_bursts/burst_question_memberships (this
  package) end to end.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through PKG-06's
  tests) re-run alongside PKG-07's new tests, both without a database (170
  passed, 88 skipped) and with a live PostgreSQL 17 instance (257 passed,
  1 skipped) -- 0 regressions. check_architecture_dependencies.py re-run
  clean, confirming all 4 prior extensions (application->persistence,
  persistence->governance, authority->persistence, persistence->domain)
  remain intact and unaffected by this package's use of already-existing
  edges only.

P_CLAIMS_TESTED:
  P-03 (Frozen human raw set): INTRODUCED-PARTIAL. The DB-trigger +
    repository layer fully proves append/remove-after-freeze denial and
    fingerprint immutability; full BND-008+CommitUnit convergence (12's
    own P-03 table row: "BND-008 + CommitUnit") remains SUCCESSOR_NOT_BUILT
    pending the boundary engine and Command/Commit infrastructure.
  P-04 (No AI contamination active HUMAN_ONLY Burst): INTRODUCED, fully
    exercised -- this proof does not depend on any not-yet-built
    infrastructure, since it only requires proving no AI capability is
    reachable, which this package's own scope already fully determines.

PROOF_ARTIFACTS:
  - Migration upgrade/downgrade/re-upgrade cycle output (this report)
  - Live PostgreSQL schema inspection (\\dt, \\d question_bursts, \\d
    burst_question_memberships, \\d sessions) confirming exact column
    set, constraints, FKs, and all 4 new triggers before and after the
    downgrade/re-upgrade cycle, including clean removal/restoration of
    the sessions retrofit
  - 257-test live-database pass, including 12 distinct adversarial
    proofs with real PostgreSQL exceptions/constraints or real
    AuthorityResolver verdicts as the canonical result
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output
  - Diff audit (inline answers given above in the conversation)

FORBIDDEN_DEPENDENCY_CHECK: PASS (no new edge needed at all)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above (new semantic type: yes, authorized;
  new DB write path: yes, disclosed and unwired; new real authority
  evaluation: yes, explicitly required by this package's own AUTHORITY
  instruction; all other categories: none/not applicable). No unauthorized
  semantic change.

ARCHITECTURE_RECONSTRUCTION_RESULT: see inline reconstruction trace above.
  Longest legitimate chain: domain transition eligibility + real
  current-authority resolution -> schema-enforced topology/freeze/
  Workspace confinement, independently proven at both layers. AUTHORITY
  is REAL for the first time (a deeper chain than PKG-05/06 reached);
  BOUNDARIES/COMMAND/COMMIT/AUDIT correctly SUCCESSOR_NOT_BUILT or
  NOT_APPLICABLE.

KNOWN_LIMITATIONS:
  - BurstRepository's mutating methods (create_prepared/start/pause/
    resume/complete/add_member) are real, tested, and entirely unwired
    from production -- a future package (boundary engine + Command/Commit,
    Phase 3/4) must build the governed path that calls through this port.
  - The BND-008 contamination guard covers exactly one testable invariant
    (AI exclusion); the full boundary (IDENTITY/SCOPE/EVIDENCE
    requirements, REQUIRE/ESCALATE outcomes, BoundaryEvaluationRecord,
    convergence with BND-009/010/014/018) remains PKG-08 scope.
  - CONFLICT-007 (Burst duration) and GAP-03-002 (pause/timer semantics)
    remain OPEN, exactly as upstream leaves them -- no duration/timer
    field or mechanism exists anywhere in this package.
  - Mode B (HUMAN_PLUS_AI) and Mode C (AI_CHALLENGE_AFTER_HUMANS) remain
    entirely unimplemented -- 08 section 12.2 explicitly leaves Mode B's
    prototype inclusion unresolved; this package's own types structurally
    refuse to construct anything but HUMAN_ONLY.
  - GAP-03-003 (BURST_INPUT_VALID enforcement mechanism, i.e. how
    "questions only, no answers/explanations" is actually validated)
    remains OPEN and unimplemented -- this package's contamination guard
    only covers the AI-exclusion half of BND-008, not the questions-only
    enforcement half.
  - Sandbox Python is 3.10.12 against the architecture's required >=3.13
    (unchanged disclosed gap from PKG-00 onward); not exercised via Docker
    this package (no new dependency, no new service).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still BLOCKED.
  Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none. All encountered gaps (CONFLICT-007, GAP-03-002,
  GAP-03-003, GAP-01-003, GAP-08-014) were already open in
  16_DECISION_GAP_REGISTER.md before this package began.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. BurstState/BurstMode's
  values are 03 section 19.1's/09 section 29.1's own vocabularies;
  SESSION_CONTROL_RIGHT at WORKSPACE scope is 12 section 7's own explicit
  resolution of a real 04 scope-model tension, not an invented rule; the
  fingerprint algorithm is 14 section 19's own IMPLEMENTATION CHOICE,
  transcribed exactly; every composite-FK Workspace-confinement pattern
  reuses the mechanism PKG-05/06 already established.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-08 (per 14's DAG: PKG-08 requires
  PKG-03, PKG-05 -- both already verified; PKG-08 does not itself list
  PKG-07 as a predecessor, but PKG-09/PKG-14 do)
HUMAN_GATE_REQUIRED: YES -- Build Phase 2, human authorization required
  before any successor package begins.
```
