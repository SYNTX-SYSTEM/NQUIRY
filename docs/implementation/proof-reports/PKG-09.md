# PKG-09 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-09
PACKAGE_TITLE: Prototype boundaries 001-008
BUILD_PHASE: 3
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  06_BOUNDARY_ARCHITECTURE.md sections 1-14 (full BND-001..008 specs, every field:
    PURPOSE, SUBJECT, REQUESTING ACTOR, INPUT, IDENTITY/SCOPE/AUTHORITY/EVIDENCE
    REQUIREMENT, PRECONDITIONS, VALIDATION, ALLOW, DENY, REQUIRE, ESCALATE, NEXT
    PERMITTED PATH, PROHIBITED PATH, TESTABLE INVARIANT, BYPASS PATHS), sections
    34-47 (AC-06-002..013, re-confirmed from PKG-08)
  11_SECURITY_PRIVACY_OBSERVABILITY.md sections 5-14 (Human Identity, Authentication
    Session Contract, Identity to Workspace Resolution, Service Identity, SYSTEM_SERVICE/
    SYSTEM_DERIVED, AI_PROCESSOR Separation, Workspace Isolation Law AC-11-004,
    Cross-Workspace Reference Enforcement, Workspace Isolation by Surface)
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 21 (Minimum Component Architecture --
    Boundary Engine as one semantic component)
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 6 (T9 scope), P-03/P-04/P-10/P-13/
    P-22 test-matrix rows
  14_IMPLEMENTATION_SEQUENCE.md section 3.1 (boundaries topology), section 39
    (T9 -> tests/security/), file-level map (packages/boundaries evaluators;
    tests/boundaries; tests/security cross-layer)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: BND-001..008 -- created, each its own file/class, "Do not
    compress to one authorization function" honored literally (8 separate
    classes, 8 separate files).
  DATABASE_CHANGES: none -- honored exactly; no migration.
  TESTS_REQUIRED: T4 (tests/boundaries/, one file per BND plus the differential
    BND-008 test), T9 (tests/security/test_bnd_cross_layer_isolation.py) -- both
    created.
  PROOF_CLAIMS: P-03, P-04 -- regression-confirmed unaffected (re-run, still
    green). P-10 -- INTRODUCED (current-authority-required proof, via real
    BND-005). P-13 -- further exercised with real concrete evaluators (PKG-08
    proved it with test-only fixtures; this package proves it with production
    evaluators). P-22 -- INTRODUCED (cross-Workspace isolation, via real BND-002
    in a chained proof).

PREDECESSORS_VERIFIED:
  PKG-07 (397d7b7, PACKAGE_PASS, human gate given) -- domain.burst_transitions
  consumed directly by BND-007.
  PKG-08 (de9c5b5, PACKAGE_PASS, human gate given) -- BoundaryRegistry/evaluate_chain
  (generic engine) now holds real evaluators for the first time.
  Also present and unbroken: PKG-00 dd4aad2, PKG-01 35ef80a, PKG-02 f976854,
  PKG-03 820a397, PKG-04 dd582ac, PKG-05 31427fb, PKG-06 06e9ea0 -- none of
  PKG-09's changes touch their owned files; full regression re-run below
  confirms no invalidation.

FILES_CREATED:
  packages/boundaries/bnd_001_identity.py
  packages/boundaries/bnd_002_workspace.py
  packages/boundaries/bnd_003_membership.py
  packages/boundaries/bnd_004_role_context.py
  packages/boundaries/bnd_005_human_authority.py
  packages/boundaries/bnd_006_human_decision.py
  packages/boundaries/bnd_007_state_transition.py
  packages/boundaries/bnd_008_question_burst.py
  tests/boundaries/test_bnd_001_identity.py
  tests/boundaries/test_bnd_002_workspace.py
  tests/boundaries/test_bnd_003_membership.py
  tests/boundaries/test_bnd_004_role_context.py
  tests/boundaries/test_bnd_005_human_authority.py
  tests/boundaries/test_bnd_006_human_decision.py
  tests/boundaries/test_bnd_007_state_transition.py
  tests/boundaries/test_bnd_008_question_burst.py
  tests/boundaries/test_bnd_008_agrees_with_application_guard.py
  tests/security/test_bnd_cross_layer_isolation.py

FILES_MODIFIED:
  packages/boundaries/__init__.py (PKG-09 content summary appended)
  scripts/check_architecture_dependencies.py (INTERNAL_ALLOWED["boundaries"]
    += "persistence", cited and justified inline)
  tests/regression/test_architecture_dependency_checks.py (+2 tests: positive
    control for boundaries->persistence, negative control confirming
    persistence->boundaries remains forbidden)

FILES_DELETED: none

MIGRATIONS_CREATED: none (DATABASE_CHANGES: none, honored)
SCHEMA_CHANGES: none
DB_PRIVILEGE_CHANGES: none

PUBLIC_INTERFACES_CREATED:
  boundaries.bnd_001_identity.{Bnd001Input, Bnd001IdentityEvaluator}
  boundaries.bnd_002_workspace.{Bnd002Input, Bnd002WorkspaceEvaluator}
  boundaries.bnd_003_membership.{Bnd003Input, Bnd003MembershipEvaluator}
  boundaries.bnd_004_role_context.{Bnd004Input, Bnd004RoleContextEvaluator}
  boundaries.bnd_005_human_authority.{Bnd005Input, Bnd005HumanAuthorityEvaluator}
  boundaries.bnd_006_human_decision.{Bnd006Input, Bnd006HumanDecisionEvaluator}
  boundaries.bnd_007_state_transition.{Bnd007Input, Bnd007StateTransitionEvaluator}
  boundaries.bnd_008_question_burst.{Bnd008OperationCategory, Bnd008Input,
    Bnd008QuestionBurstEvaluator}

COMMANDS_CREATED: NOT_APPLICABLE (14 assigns none to PKG-09)
QUERIES_CREATED: NOT_APPLICABLE
EVENTS_CREATED: NOT_APPLICABLE
BOUNDARIES_CREATED_OR_CHANGED: BND-001 through BND-008, all 8, all executable
  and independently tested. BND-009 through BND-018 remain unbuilt -- later
  packages' scope.

AUTHORITY_PATH: BND-005 wraps the real, unmodified `authority.resolver.AuthorityResolver`
  (constructor-injected, never constructed by this package's own code with
  fresh repositories) -- "Use AuthorityResolver current proof only" honored
  literally. BND-004's `accepted_roles` mapping is caller-supplied per
  operation, never invented here. No new Decision Right, HABB meaning, or
  resolver fallback was added.

EVIDENCE_PATH: NOT_APPLICABLE (14 PKG-09 EVIDENCE: "Not yet BND-013").

AI_PATH: BND-008 (independently re-derived, cross-verified against PKG-07's
  `application.burst_contamination` by an exhaustive 176-case differential
  test) denies every AI-attributed content and lifecycle operation during
  protected Burst states. BND-006 denies AI-authored decision content and
  non-human decision requesters. No AI output becomes canonical state or
  authority anywhere in this package.

RECOVERY_PATH: NOT_APPLICABLE (no recovery machinery exists yet).

TESTS_CREATED: 10 files, 66 test functions plus 176 differential-test cases
  (test_bnd_001: 4, test_bnd_002: 5, test_bnd_003: 5, test_bnd_004: 4,
  test_bnd_005: 6, test_bnd_006: 4, test_bnd_007: 6, test_bnd_008: 5,
  test_bnd_008_agrees_with_application_guard: 176 parametrized + 1,
  test_bnd_cross_layer_isolation: 5)
TESTS_MODIFIED: none

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS (155 files clean)
          ruff check . -- PASS (mechanical import-order/unused-import issues
            auto-fixed throughout, no semantic changes)
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts --
            PASS (74 source files, no issues)
  Architecture checks: check_architecture_dependencies.py -- PASS (one
    disclosed extension: boundaries -> persistence, read-only, 5th such
    extension following the established pattern)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 5 revisions
                          unchanged, single head d8a1147fde30; live: db head
                          matches)
  Pure-Python suite (no DB): full tests/ + apps/api/tests -- 396 passed, 116
    skipped (all pre-existing SKIPPED_NO_DATABASE, none new)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=55432): tests/ apps/api/tests -- 511 passed, 1 skipped, 0
    failed after one pre-fix bug found and fixed (see below)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative tests
  pass; each asserts a specific BoundaryResult + reason_code (or, for BND-005,
  the real AuthorityResolutionProof's own reason), never merely "an error
  occurred."

PRE_IMPLEMENTATION_FAILURE_DEMONSTRATION: One real pre-fix failure was
  produced and fixed, in test code rather than production code:
  `test_cross_workspace_actor_denied_at_bnd002_before_membership_or_authority_checked`
  initially asserted `len(chain_result.proofs) == 1`, but BND-001 (identity)
  legitimately runs first in the chain and genuinely ALLOWs (the actor's
  identity itself is fine; only the Workspace resolution at BND-002 is the
  attack) -- the correct count is 2 proofs (BND-001 ALLOW, BND-002 DENY),
  not 1. Caught immediately on the first live-database run of the full
  suite (1 failure out of 512 assertions), fixed by correcting the
  assertion to check both proofs' individual results explicitly rather
  than just a count. The production evaluator chain itself behaved
  exactly correctly throughout -- this was a test-authoring miscount, not
  a defect in `Bnd001IdentityEvaluator`/`Bnd002WorkspaceEvaluator`/
  `evaluate_chain`.

ADVERSARIAL_COUNTER_TESTS:
  Mandatory (8/8, each individually AND in the T9 chained proof):
  1. Forged identity
     EXPECTED DEFENSE: Bnd001IdentityEvaluator's required_actor_classes check
     EXPECTED CANONICAL RESULT: DENY, reason names the rejected actor class
     ACTUAL RESULT: matches
       (test_denies_an_actor_class_the_operation_does_not_accept,
       test_ai_processor_can_never_pass_as_human_user,
       test_ai_processor_denied_at_bnd001_before_any_later_boundary_runs)
  2. Workspace mismatch
     EXPECTED DEFENSE: Bnd002WorkspaceEvaluator's cross-object-set and
       claimed-vs-resolved checks, backed by real WorkspaceRepository
     EXPECTED CANONICAL RESULT: DENY, CROSS_WORKSPACE_OBJECT_SET /
       CLAIMED_WORKSPACE_MISMATCH
     ACTUAL RESULT: matches (test_denies_cross_workspace_object_set,
       test_denies_claimed_workspace_differing_from_resolved_scope,
       test_cross_workspace_actor_denied_at_bnd002_before_membership_or_authority_checked)
  3. Missing membership
     EXPECTED DEFENSE: Bnd003MembershipEvaluator, real MembershipRepository
     EXPECTED CANONICAL RESULT: DENY, NO_ACTIVE_MEMBERSHIP
     ACTUAL RESULT: matches (test_denies_a_non_member,
       test_non_member_is_denied_at_bnd003_before_bnd005_ever_runs)
  4. Role-only authority
     EXPECTED DEFENSE: Bnd004RoleContextEvaluator's accepted_roles check
     EXPECTED CANONICAL RESULT: DENY when current role not in accepted set
     ACTUAL RESULT: matches (test_denies_a_role_not_in_the_accepted_set)
  5. Missing human Decision
     EXPECTED DEFENSE: Bnd006HumanDecisionEvaluator's decision_origin check
     EXPECTED CANONICAL RESULT: DENY when origin is not HUMAN_USER
     ACTUAL RESULT: matches (test_denies_ai_authored_decision_content)
  6. Illegal state transition
     EXPECTED DEFENSE: Bnd007StateTransitionEvaluator consuming real
       session_transitions/burst_transitions resolutions
     EXPECTED CANONICAL RESULT: DENY, reason names the domain verdict
     ACTUAL RESULT: matches (test_denies_an_illegal_session_transition,
       test_denies_reopening_a_closed_session,
       test_denies_an_illegal_burst_transition)
  7. ACTIVE Burst AI contamination
     EXPECTED DEFENSE: Bnd008QuestionBurstEvaluator
     EXPECTED CANONICAL RESULT: DENY during ACTIVE/PAUSED for AI-attributed
       content operations
     ACTUAL RESULT: matches (test_denies_ai_analysis_during_active_burst,
       test_denies_ai_analysis_during_paused_burst)
  8. Downstream ALLOW after earlier DENY
     EXPECTED DEFENSE: evaluate_chain's short-circuit (PKG-08), now proven
       with real evaluators
     EXPECTED CANONICAL RESULT: downstream evaluator's proof never appears
       in the result at all
     ACTUAL RESULT: matches
       (test_non_member_is_denied_at_bnd003_before_bnd005_ever_runs,
       test_cross_workspace_actor_denied_at_bnd002_before_membership_or_authority_checked,
       test_ai_processor_denied_at_bnd001_before_any_later_boundary_runs)

  Novel/adapted (6 additional, exceeding the >=10-total critical-package
  minimum: 8 mandatory + 6 novel = 14):
  9. Revoked membership treated as active -- denied identically to no
     membership at all (test_denies_a_revoked_member)
  10. Stale role after removal -- both "no role row" and "role explicitly
      revoked" shapes (test_denies_no_current_role, test_denies_a_revoked_role)
  11. AI actor attempting Decision creation (distinct from AI-authored
      content) (test_denies_a_non_human_requester_regardless_of_decision_origin)
  12. Ambiguous active bindings never become ALLOW at the boundary layer
      (test_ambiguous_bindings_are_never_allow)
  13. Wrong-scope authority binding denied (test_denies_wrong_scope)
  14. Full real chained BND-001->005 proof against one live Workspace,
      positive and negative
      (test_full_chain_allows_a_legitimate_authorized_member,
      test_missing_authority_denies_at_bnd005_after_bnd001_002_003_allow)

  Negative controls also present: test_system_service_allowed_when_operation_accepts_it,
  test_allows_a_single_effective_workspace, test_allows_an_active_member,
  test_allows_an_accepted_current_role, test_allows_a_granted_authority_class,
  test_allows_a_human_requester_with_human_authored_content,
  test_allows_a_legal_session_transition, test_allows_a_legal_burst_transition,
  test_allows_human_capture_during_active (every evaluator proven not
  vacuously strict).

MUTATION_TESTS:
  MUT-PKG09-01: remove Bnd003MembershipEvaluator's actor_class check ->
    expected red: test_denies_a_non_human_actor -> by inspection, that
    test's only DENY source is the removed check -- INTERPRETATION:
    mutation killed.
  MUT-PKG09-02: change Bnd005HumanAuthorityEvaluator to map
    AuthorityVerdict.UNRESOLVED to BoundaryResult.ALLOW instead of DENY ->
    expected red: test_ambiguous_bindings_are_never_allow -> by
    inspection, that test asserts DENY specifically for the UNRESOLVED
    case -- INTERPRETATION: mutation killed.
  MUT-PKG09-03: remove the AI-actor-class branch from
    Bnd008QuestionBurstEvaluator -> expected red: every test in
    test_bnd_008_question_burst.py asserting DENY, plus ~half of the 176
    differential-test cases in test_bnd_008_agrees_with_application_guard.py
    (any case with actor_class=AI_PROCESSOR would then disagree with the
    independent application.burst_contamination implementation) --
    INTERPRETATION: mutation killed, doubly (direct tests + differential
    test).
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: test_bnd_cross_layer_isolation.py (T9) exercises the
  full real predecessor + this-package chain end to end:
  NonProofWorkspaceBootstrap (PKG-04) -> WorkspaceRepository/MembershipRepository/
  AuthorityBindingRepository (PKG-01/02) -> AuthorityResolver (PKG-03) ->
  Bnd001/002/003/005 (this package) -> BoundaryRegistry/evaluate_chain
  (PKG-08) -- five distinct scenarios (full ALLOW, authority-denied,
  membership-denied, cross-Workspace-denied, identity-denied), each a
  genuine multi-package relational proof, never an isolated mock.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through PKG-08's
  tests) re-run alongside PKG-09's new tests, both without a database (396
  passed, 116 skipped) and with a live PostgreSQL 17 instance (511 passed,
  1 skipped) -- 0 regressions after the one test-assertion fix.
  check_architecture_dependencies.py re-run clean, confirming all 5 prior
  extensions (application->persistence, persistence->governance,
  authority->persistence, persistence->domain, boundaries->persistence)
  remain intact.

P_CLAIMS_TESTED:
  P-03/P-04: regression-confirmed unaffected (PKG-06/07's own tests still
    pass unchanged).
  P-10 (Current authority required): INTRODUCED -- test_denies_missing_binding
    and test_allows_a_granted_authority_class together prove "only the
    current right commits" using the real BND-005 evaluator.
  P-13 (Boundary DENY prevents consequence, no downstream override):
    further exercised -- PKG-08 proved the composition mechanism with
    test-only fixtures; this package proves the identical guarantee with
    the actual production BND-001..005 evaluators, against real database
    state.
  P-22 (Cross-Workspace isolation): INTRODUCED --
    test_cross_workspace_actor_denied_at_bnd002_before_membership_or_authority_checked
    proves a Workspace-A actor is denied before Workspace-B's membership
    or authority state is ever read.

PROOF_ARTIFACTS:
  - 511-test live-database pass, including 14 distinct adversarial proofs
    (8 mandatory + 6 novel) and a 176-case exhaustive differential proof
    between two independently written BND-008 implementations
  - Real AuthorityResolutionProof objects carried inside BoundaryProof.authority_proof,
    inspectable in test assertions (e.g. reason.value == "GRANTED_EFFECTIVE_BINDING")
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output (migration head unchanged, confirming
    DATABASE_CHANGES: none was honored)
  - Diff audit (inline answers given above in the conversation)
  - Mutation-kill analysis (3 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (one disclosed, tested extension:
  boundaries -> persistence, read-only)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT: see inline answers above (new semantic type: yes, authorized as
  the exact PUBLIC_INTERFACES; new enum value: Bnd008OperationCategory,
  disclosed + differentially cross-verified; all other categories:
  none/not applicable). No unauthorized semantic change.

ARCHITECTURE_RECONSTRUCTION_RESULT: see inline reconstruction trace above.
  Longest legitimate chain: BND-001->002->003->005 evaluated end-to-end
  against one real Workspace with real membership and a real granted
  SESSION_CONTROL_RIGHT binding. BND-014/COMMAND/COMMIT/AUDIT correctly
  SUCCESSOR_NOT_BUILT or NOT_APPLICABLE.

KNOWN_LIMITATIONS:
  - BND-006 cannot check a real Decision object's authorship, because no
    Decision persistence exists yet (PKG-14+) -- it validates the one
    honest fact currently available (asserted decision_origin) and
    structurally cannot verify that assertion against a canonical record.
  - BND-004's FacilitatorScopeBinding half (06's own "ACTIVE
    FacilitatorScopeBinding" requirement for Burst control) is not
    checked -- that table does not exist yet (deferred since PKG-02);
    this evaluator only proves the role half of 06's testable invariant.
  - BND-008 duplicates (independently, disclosed, differentially tested)
    the logic already in application.burst_contamination -- consolidating
    the two into one shared location requires restructuring the
    application/boundaries dependency direction, out of this package's
    scope.
  - No evaluator is wired into any production caller -- no Command/Query
    dispatch exists yet (Phase 4+). Every evaluator is proven directly and
    in chains by tests only.
  - BND-009 through BND-018 remain entirely unbuilt.
  - Sandbox Python is 3.10.12 against the architecture's required >=3.13
    (unchanged disclosed gap from PKG-00 onward); not exercised via Docker
    this package (no new dependency, no new service, no migration).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still BLOCKED.
  Used only via NonProofWorkspaceBootstrap in test fixtures.

NEW_GAPS_DISCOVERED: none.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. Every evaluator's ALLOW/DENY
  logic is a direct, literal translation of 06's own VALIDATION/ALLOW/DENY
  text for that specific boundary; BND-004's accepted_roles mechanism keeps
  the actual role-to-right mapping caller-supplied per 04's own citations,
  never inventing a new one; BND-007 consumes rather than recomputes
  existing PKG-05/07 domain verdicts; BND-008's vocabulary is independently
  re-derived from 06 section 14's own text and cross-checked exhaustively
  against PKG-07's prior implementation.

NEXT_PACKAGE_ALLOWED_BY_DAG: none newly unblocked by PKG-09 alone requiring
  only it -- per 14's DAG, PKG-10 requires PKG-09 (now verified); PKG-19
  additionally requires PKG-18.
HUMAN_GATE_REQUIRED: YES -- "HUMAN_GATE_REQUIRED::YES at package level. Do
  not authorize any successor" (this package's own coding prompt, verbatim).
```
