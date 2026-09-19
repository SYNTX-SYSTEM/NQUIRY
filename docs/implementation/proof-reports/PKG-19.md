# PKG-19 PACKAGE COMPLETION REPORT

```text
PACKAGE_ID: PKG-19
PACKAGE_TITLE: AI Gateway and MockProvider
BUILD_PHASE: 7
VERDICT: PACKAGE_PASS

UPSTREAM_FILES_READ:
  06_BOUNDARY_ARCHITECTURE.md section 15 (BND-009 AI Invocation
    Boundary -- full spec: PURPOSE "Ensure every LLM/model invocation
    occurs through the approved AI Gateway context..."; REQUESTING
    ACTOR "AI_PROCESSOR may not self-authorize a new invocation"; DENY/
    REQUIRE/ESCALATE lists; NEXT PERMITTED PATH "AI provider execution
    then BND-010 for returned output"), section 16 (BND-010 AI Output /
    Canonical State Boundary -- full spec: PURPOSE "Prevent AI output
    from becoming human-authoritative, evidentiary or canonical
    consequence merely because it was generated, validated or
    persisted"; DENY list; TESTABLE INVARIANT)
  08_AI_ARCHITECTURE_AND_CONTRACTS.md section 2 (AI System Architecture
    -- Application/Gateway/Policy Engine/Prompt Builder/Model Router/
    LLM Provider/Response Validator), section 3 (All LLM Traffic
    Through Gateway), section 6/6.1/6.2 (AI Context Manifest), section
    8/8.1/8.2 (Prompt Architecture -- modular templates, prompt is not
    authority), section 9 (Prompt Injection and Retrieved-Content
    Instruction Boundary -- "[ARCHITECTURAL CLOSURE]"), section 10
    (AI Coach Modes -- exact 7-value closed list), section 14/15/16
    (AIGeneration lifecycle, reused from PKG-18), section 17/17.1/17.2
    (Model and Provider Boundary), section 19/19.1 (Response
    Validation), section 22 (Direct Persistence Prohibition), section
    23 (AIOP-001 QUESTION_ANALYSIS -- full contract, the one AIOP this
    package's own tests actually exercise end to end)
  11_SECURITY_AND_INFRASTRUCTURE (referenced via 14 section 8's own
    `ai_gateway_writer` DB principal row: "approved context source
    views | AI operational and derived artifact tables only |
    Decision, HABB, QuestionSelection, canonical transition tables
    [forbidden]")
  12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 12.1 (Minimum AIOPs --
    AIOP-001 required), section 12.2 (AI execution chain), section
    12.3 (Provider rule, AC-12-008: "One eligible provider is
    sufficient; gateway exclusivity and provider independence remain")
  13_TEST_AND_FALSIFICATION_ARCHITECTURE.md section 39 (T6 ->
    tests/ai/, T9 -> tests/security/), P-04/P-05/P-06/P-07/P-23 matrix
    rows, P-23's own row (T13-P23-GATEWAY-EXCLUSIVE)
  14_IMPLEMENTATION_SEQUENCE.md PKG-19 package manifest (BUILD_PHASE 7,
    UPSTREAM FILES 08/11/12/13/14, REQUIRED PREDECESSORS PKG-18/PKG-09,
    PUBLIC INTERFACES "AIGateway", DATABASE CHANGES 007, TESTS REQUIRED
    T6/T9, PROOF CLAIMS P-04/P-05/P-06/P-07/P-23, BOUNDARIES "BND-008
    and AI invocation boundaries as mapped by 14"), section 3.1 (May-
    depend-on table -- `ai_gateway`: "ai_contracts, security,
    operational persistence", explicitly excluding `boundaries` --
    load-bearing for this package's own design, see DIFF_AUDIT),
    section 7.1/7.3 (ai_gateway_writer principal, core tables), section
    9 (migration plan, 007_ai_operational bucket split confirmed
    across PKG-18/PKG-19), section 15/16 (BND-009/010 status:
    "IMPLEMENTED" in the prototype's own final boundary status map),
    section 41 (provider SDK import only under provider adapter),
    section 48 (file-level map -- the four explicit rows for this
    package: context.py/prompt.py/validator.py/adapters/providers/mock.py)

14_REQUIREMENTS_MATERIALIZED:
  PUBLIC_INTERFACES: "AIGateway" -- materialized as
    `ai_gateway.gateway.{AIGateway, AIGatewayResult,
    InvocationNotAuthorized, ContextManifestWorkspaceMismatch}`,
    orchestrating the four named components:
    `ai_gateway.context.{AIContextManifest, build_context_manifest}`,
    `ai_gateway.prompt.{InvocationPrompt, build_invocation_prompt}`,
    `ai_gateway.adapters.providers.mock.MockProviderAdapter`,
    `ai_gateway.validator.validate_response`.
  BOUNDARIES: "BND-008 and AI invocation boundaries as mapped by 14" --
    `boundaries.bnd_009_ai_invocation.Bnd009AiInvocationEvaluator`,
    `boundaries.bnd_010_ai_output.Bnd010AiOutputEvaluator` created;
    BND-008 reused unmodified from PKG-09.
  DATABASE_CHANGES: 007 (remainder) -- `ai_context_manifests` created,
    closing PKG-18's own disclosed forward-reference gap on
    `ai_generations.ai_context_manifest_id` with a real retrofitted FK.
  TESTS_REQUIRED: T6 (tests/ai/ -- test_context.py, test_prompt.py,
    test_mock_provider.py, test_validator.py, test_gateway.py all new;
    test_burst_ai_block.py fixed for a now-outdated assumption), T9
    (tests/security/test_ai_gateway.py extended with the dynamic P-23
    proof its own original docstring promised) -- all created/extended.
  PROOF_CLAIMS: P-04, P-05, P-06, P-07, P-23 -- see P_CLAIMS_TESTED
    below.

PREDECESSORS_VERIFIED:
  PKG-18 (22f4114, PACKAGE_PASS, human gate given).
  PKG-09 (verified earlier in the DAG, BND-001..008 IMPLEMENTED).
  Full chain unbroken: PKG-00 dd4aad2 through PKG-18 22f4114. No
  predecessor's own non-test files were touched beyond the disclosed
  extension points (persistence tables/repository, architecture
  checker) plus two previously-green tests whose own assumptions this
  package's legitimate new capability invalidated (fixed, not
  bypassed) -- full regression re-run below confirms no invalidation
  of any underlying architectural claim.

FILES_CREATED:
  packages/ai_gateway/context.py
  packages/ai_gateway/prompt.py
  packages/ai_gateway/validator.py
  packages/ai_gateway/adapters/providers/mock.py
  packages/ai_gateway/gateway.py
  packages/boundaries/bnd_009_ai_invocation.py
  packages/boundaries/bnd_010_ai_output.py
  migrations/versions/7c2e8a4f1d6b_ai_context_manifests.py
  tests/ai/test_context.py
  tests/ai/test_prompt.py
  tests/ai/test_mock_provider.py
  tests/ai/test_validator.py
  tests/ai/test_gateway.py
  tests/boundaries/test_bnd_009_ai_invocation.py
  tests/boundaries/test_bnd_010_ai_output.py

FILES_MODIFIED:
  packages/persistence/ai_record_repository.py
    (`create_context_manifest`/`get_context_manifest` added, closing
    PKG-18's own disclosed "no manifest methods yet" gap)
  packages/persistence/tables.py (`ai_context_manifests_table` added;
    retrofitted composite `ai_context_manifest_id` foreign key onto
    `ai_generations_table` now that its own long-disclosed
    forward-reference gap, PKG-18, has a real target)
  scripts/check_architecture_dependencies.py
    (INTERNAL_ALLOWED["boundaries"] += "ai_contracts", 16th disclosed
    extension; INTERNAL_ALLOWED["persistence"] += "ai_gateway", 17th
    disclosed extension, a bidirectional-but-disjoint-submodule edge
    mirroring `commit <-> persistence`'s own precedent)
  tests/ai/test_burst_ai_block.py (one test's own now-outdated
    assumption -- "the whole `ai_gateway` package is empty" -- fixed
    the same way PKG-18 already fixed its `ai_contracts` counterpart;
    see DIFF_AUDIT)
  tests/security/test_ai_gateway.py (docstring updated; +1 test
    delivering the dynamic P-23 proof this file's own original
    docstring explicitly promised would land at PKG-19)

FILES_DELETED: none

MIGRATIONS_CREATED: 7c2e8a4f1d6b (ai context manifests), revises
  4a7c1e9f2b3d. Creates `ai_context_manifests` (09 section 54's exact
  field list; `coach_mode` CHECK-constrained to 08 section 10's own
  7-value closed list; `source_classifications`/`excluded_context_classes`
  left plain `TEXT[]`, no definitive closure language in 08/09 for
  either). Retrofits composite `ai_generations.ai_context_manifest_id
  -> ai_context_manifests(id, workspace_id)` FK, closing PKG-18's own
  disclosed gap. Full downgrade drops the retrofitted FK then the new
  table; downgrade(-1)/re-upgrade cycle verified live.
SCHEMA_CHANGES: `ai_context_manifests` (see above). No other table
  touched.
DB_PRIVILEGE_CHANGES: none. `ai_gateway_writer` (14 section 8) remains
  deferred to migration 012_security_events_rls, consistent with every
  migration since 001.

PUBLIC_INTERFACES_CREATED:
  ai_gateway.context.{CoachMode, InputArtifactRef, AIContextManifest,
    compute_context_fingerprint, build_context_manifest}
  ai_gateway.prompt.{DataBlock, InvocationPrompt, build_invocation_prompt}
  ai_gateway.validator.validate_response
  ai_gateway.adapters.providers.mock.{MockProviderOutcome,
    ProviderTimeout, ProviderError, MockProviderResponse,
    MockProviderAdapter}
  ai_gateway.gateway.{InvocationNotAuthorized,
    ContextManifestWorkspaceMismatch, AIGatewayResult, AIGateway}
  boundaries.bnd_009_ai_invocation.{Bnd009Input, Bnd009AiInvocationEvaluator}
  boundaries.bnd_010_ai_output.{Bnd010Input, Bnd010AiOutputEvaluator}

COMMANDS_CREATED: NOT_APPLICABLE. 14 assigns no Command to this
  package (COMMANDS section: "If none are assigned, NOT_APPLICABLE" --
  none are). `RequestAIAnalysis` (14 section 12's own named Command)
  remains unassigned to any package in the DAG so far;
  `AIGateway.run_operation` is a real, directly-callable orchestration
  method proven end to end by tests, but no CommandEnvelope/
  CommitCoordinator-based governed wrapper exists yet for it --
  disclosed, not fabricated.
QUERIES_CREATED: NOT_APPLICABLE.
EVENTS_CREATED: NOT_APPLICABLE.

BOUNDARIES_CREATED_OR_CHANGED:
  BND-009 (AI Invocation): created. `Bnd009AiInvocationEvaluator` --
    DENY on AI_PROCESSOR self-invocation (unconditional) or
    cross-Workspace context; REQUIRE when the AIOP contract is not
    approved; ALLOW otherwise. Deliberately does NOT re-check Burst
    contamination (BND-008's own job, consumed via chain sequencing,
    not recomputed).
  BND-010 (AI Output / Canonical State): created.
    `Bnd010AiOutputEvaluator` -- DENY unless the generation is
    VALIDATED, its own AI_VALIDATION_PROOF is VALIDATED, and the
    source Workspace matches; ALLOW populates `evidence_proof_refs`
    with the AI_VALIDATION_PROOF reference (the second package ever to
    populate that field, after BND-013/PKG-17's own DOMAIN_EVIDENCE
    use).
  BND-008 (Question Burst): unchanged, reused from PKG-09.
  Neither BND-009 nor BND-010 is invoked from inside `AIGateway`
  itself -- see AUTHORITY_PATH and DIFF_AUDIT for why `ai_gateway`'s
  own 14 section 3.1 allowed-dependency row excludes `boundaries`.

AUTHORITY_PATH: "No AI authority. Prompt text cannot grant it." (14
  PKG-19 AUTHORITY). Structurally enforced at two independent layers:
  (1) `ai_gateway`/`ai_contracts` import no `authority` module at all;
  (2) `ai_gateway.prompt.InvocationPrompt` keeps `system_instructions`
  and `data_blocks` as separate, distinctly-typed fields, and no code
  path anywhere in this package reads `DataBlock.content` to derive a
  boundary/authority decision --
  `tests/ai/test_prompt.py::test_prompt_injection_attempt_does_not_change_prompt_structure`,
  `tests/ai/test_mock_provider.py::test_output_is_independent_of_data_block_content`,
  and `tests/ai/test_gateway.py::test_prompt_injection_attempt_does_not_change_the_outcome`
  each prove this at a different layer of the real pipeline.

EVIDENCE_PATH: "Context allowlist uses exact refs; AI_VALIDATION_PROOF
  not Evidence" (14 PKG-19 EVIDENCE). `AIContextManifest`'s own
  `input_artifact_refs_with_versions` are exact `(ref, version)` pairs,
  never a broader query (`build_context_manifest`'s own signature has
  no parameter through which "everything" could be supplied -- proven
  by `test_build_context_manifest_never_accepts_an_unresolved_query`).
  `AIValidationProof` (reused from PKG-18, produced here by the real
  Response Validator) carries no Evidence-shaped field --
  `tests/ai/test_validator.py::test_validator_never_returns_anything_evidence_shaped`.

AI_PATH: "Exclusive provider path. MockProvider default. Real provider
  execution BLOCKED by HARD-DEP-002" (14 PKG-19 AI). Proven end to end:
  the real `AIGateway` orchestrates context -> prompt -> the one real
  `MockProviderAdapter` -> validator -> persisted `AIDerivedArtifact`,
  against live PostgreSQL, for the first time in this codebase. No
  real provider adapter file exists (`SUCCESSOR_NOT_BUILT`, not merely
  a disabled flag); `MockProviderAdapter` carries no credential field
  of any kind
  (`tests/ai/test_mock_provider.py::test_adapter_has_no_credential_field`).
  Exclusivity proven dynamically (P-23):
  `tests/security/test_ai_gateway.py::test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider`
  scans this repository's REAL production source and proves
  `MockProviderAdapter` is importable by exactly one production
  module, `ai_gateway.gateway`.

RECOVERY_PATH: "Provider failure creates AIGeneration FAILED/
  appropriate operational outcome, no domain consequence.
  HUMAN_GATE_REQUIRED" (14 PKG-19 FAILURE_RECOVERY). Proven directly:
  timeout/provider-error paths mark the generation FAILED with no
  derived artifact
  (`test_provider_timeout_marks_the_generation_failed`,
  `test_provider_error_marks_the_generation_failed`); an invalid/
  partial response marks it REJECTED, likewise with no artifact
  (`test_partial_response_marks_the_generation_rejected_no_artifact`);
  a retry after FAILED creates a genuinely new, independently-tracked
  generation rather than reviving the old one
  (`test_retry_creates_a_new_generation_correlated_to_the_original`).

TESTS_CREATED:
  tests/boundaries/test_bnd_009_ai_invocation.py: 8 test functions, all
    pure Python.
  tests/boundaries/test_bnd_010_ai_output.py: 7 test functions, all
    pure Python.
  tests/ai/test_context.py: 8 test functions (6 pure, 2 DB-backed).
  tests/ai/test_prompt.py: 8 test functions, all pure Python.
  tests/ai/test_mock_provider.py: 7 test functions, all pure Python.
  tests/ai/test_validator.py: 6 test functions, all pure Python.
  tests/ai/test_gateway.py: 10 test functions (9 DB-backed, 1 pure).
TESTS_MODIFIED:
  tests/ai/test_burst_ai_block.py: 1 test updated (see DIFF_AUDIT), 7
    unchanged and still passing.
  tests/security/test_ai_gateway.py: +1 test (dynamic P-23 proof), 2
    unchanged and still passing.
  Net new: 55 tests (44 pure, 11 DB-backed).

TARGETED_TEST_RESULTS:
  Static: ruff format --check . -- PASS (241 files)
          ruff check . -- PASS
          MYPYPATH=... mypy packages apps/api/src apps/worker/src scripts
            -- PASS (113 source files)
  Architecture checks: check_architecture_dependencies.py -- PASS (two
    disclosed extensions this package: boundaries -> ai_contracts
    [16th], persistence -> ai_gateway [17th], both cited inline and
    regression-tested)
                        check_provider_sdk_imports.py -- PASS
                        check_test_only_imports.py -- PASS
                        verify_migrations.py -- PASS (static: 14
                          revisions, single head 7c2e8a4f1d6b; live: db
                          head matches after full upgrade, plus a
                          downgrade(-1)/re-upgrade cycle)
  Pure-Python suite (no DB): tests/ -- 549 passed, 293 skipped (all
    SKIPPED_NO_DATABASE, none unexpected)
  Live-PostgreSQL 17 suite (full tree, DATABASE_URL set,
    POSTGRES_PORT=15432): tests/ -- 841 passed, 1 skipped, 0 failed
    (786 baseline + 55 new; the 1 skip is pre-existing and unrelated
    to this package)

NEGATIVE_TEST_RESULTS: all designed-before-implementation negative
  tests pass; each asserts a specific structured outcome (a named
  `BoundaryResult`/exception type/`AIValidationResult`/database
  constraint violation with a matching message), never merely "an
  error occurred."

ADVERSARIAL_COUNTER_TESTS:
  Package-specific mandatory (13/13, 14 PKG-19's own list):
  1. Mock valid
     ACTUAL RESULT: matches (test_success_returns_a_well_formed_response,
       test_full_success_path_creates_generation_and_derived_artifact)
  2. Invalid schema
     ACTUAL RESULT: matches (test_wrong_declared_operation_is_rejected,
       test_missing_required_field_is_rejected)
  3. Timeout
     ACTUAL RESULT: matches (test_timeout_raises_provider_timeout,
       test_provider_timeout_marks_the_generation_failed)
  4. Provider error
     ACTUAL RESULT: matches (test_provider_error_raises_provider_error,
       test_provider_error_marks_the_generation_failed)
  5. Partial response
     ACTUAL RESULT: matches (test_partial_response_returns_truncated_content,
       test_unparseable_response_is_indeterminate,
       test_partial_response_marks_the_generation_rejected_no_artifact)
  6. Duplicate response
     ACTUAL RESULT: matches
       (test_two_invocations_are_independent_generations_worth_of_output,
       test_two_invocations_never_collapse_into_one_generation)
  7. Prompt injection
     ACTUAL RESULT: matches
       (test_prompt_injection_attempt_does_not_change_prompt_structure,
       test_output_is_independent_of_data_block_content,
       test_prompt_injection_attempt_does_not_change_the_outcome)
  8. Wrong Workspace artifact
     ACTUAL RESULT: matches (test_denies_cross_workspace_context [BND-009],
       test_denies_cross_workspace_derived_artifact [BND-010],
       test_cross_workspace_context_manifest_is_not_representable,
       test_cross_workspace_context_manifest_is_denied [gateway])
  9. Forbidden canonical effect
     ACTUAL RESULT: matches (test_ai_gateway_has_no_domain_mutation_capability,
       test_denies_persistence_when_generation_is_not_validated)
  10. Missing provenance
      EXPECTED DEFENSE: unchanged from PKG-18 --
        `ai_derived_artifacts.ai_generation_id` remains NOT NULL with a
        real composite FK
      ACTUAL RESULT: matches (regression-confirmed by
        `tests/ai/test_derived_artifact.py::test_denies_a_derived_artifact_referencing_a_nonexistent_generation`,
        still passing)
  11. Direct provider import
      ACTUAL RESULT: matches
        (test_direct_provider_import_outside_gateway_adapter_is_rejected,
        test_provider_import_through_the_approved_adapter_boundary_is_not_flagged,
        both unchanged and still passing;
        test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider,
        new, the dynamic proof)
  12. Prompt/retrieved text attempting to grant authority
      ACTUAL RESULT: matches
        (test_prompt_injection_attempt_does_not_change_the_outcome)
  13. Active Burst invocation
      ACTUAL RESULT: matches
        (test_unauthorized_invocation_is_denied_and_creates_no_generation;
        test_ai_analysis_during_active_human_only_burst_is_denied,
        unchanged, still passing)

  Novel/adapted (>=10 required for this critical package; 12
  additional, 25 total):
  14. AI self-invocation (unconditional, independent of Burst state)
      ACTUAL RESULT: matches (test_denies_ai_self_invocation,
        test_ai_self_invocation_denial_precedes_every_other_check)
  15. AI self-invocation denial precedence over cross-Workspace/REQUIRE
      ACTUAL RESULT: matches
        (test_ai_self_invocation_denial_precedes_every_other_check)
  16. DENY precedence over REQUIRE at BND-009
      ACTUAL RESULT: matches
        (test_cross_workspace_denial_precedes_the_contract_require)
  17. Approved-contract REQIURE distinct from a known-bad DENY
      ACTUAL RESULT: matches (test_requires_an_approved_operation_contract)
  18. Persisting from a not-VALIDATED generation
      ACTUAL RESULT: matches
        (test_denies_persistence_when_generation_is_not_validated)
  19. VALIDATED generation status alone is insufficient without a
      VALIDATED AI_VALIDATION_PROOF
      ACTUAL RESULT: matches
        (test_denies_persistence_when_validation_result_is_not_validated)
  20. BND-010 ordering: generation-status DENY precedes Workspace check
      ACTUAL RESULT: matches
        (test_generation_status_denial_precedes_workspace_check)
  21. BND-009/010 compose cleanly with the generic chain engine
      ACTUAL RESULT: matches (test_registers_cleanly_in_the_boundary_registry,
        both files)
  22. Retry AC-09-022 (new identity, correlated, original never revived)
      ACTUAL RESULT: matches
        (test_retry_creates_a_new_generation_correlated_to_the_original)
  23. Context manifest allowlist structurally cannot accept an
      unresolved/broad query
      ACTUAL RESULT: matches
        (test_build_context_manifest_never_accepts_an_unresolved_query)
  24. AIDerivedArtifact/AIValidationProof structurally cannot carry an
      origin/authorship field to misrepresent AI output as human
      ACTUAL RESULT: matches (regression-confirmed,
        test_ai_derived_artifact_has_no_field_that_could_misrepresent_ai_output_as_human)
  25. Cross-Workspace context manifest at rest (not merely at
      invocation time)
      ACTUAL RESULT: matches
        (test_cross_workspace_context_manifest_is_not_representable)

  Legitimate controls proven not vacuously strict:
  test_allows_a_well_formed_human_requested_invocation,
  test_allows_a_system_service_requested_invocation,
  test_allows_persisting_a_validated_derived_artifact,
  test_full_round_trip_create_and_get (context manifest),
  test_full_success_path_creates_generation_and_derived_artifact,
  test_render_delimited_text_keeps_data_blocks_distinguishable.

MUTATION_TESTS:
  MUT-PKG19-01: remove the AI_PROCESSOR self-invocation check from
    `Bnd009AiInvocationEvaluator` -> expected red:
    test_denies_ai_self_invocation -- INTERPRETATION: mutation killed.
  MUT-PKG19-02: remove the generation-status VALIDATED check from
    `Bnd010AiOutputEvaluator` -> expected red:
    test_denies_persistence_when_generation_is_not_validated --
    INTERPRETATION: mutation killed.
  MUT-05 (14 section 54's own named mutation, reused): allow direct AI
    provider access -> expected red:
    test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider,
    test_direct_provider_import_outside_gateway_adapter_is_rejected --
    INTERPRETATION: mutation killed.
  MUT-PKG19-04: make `MockProviderAdapter._deterministic_content` read
    `DataBlock.content` -> expected red:
    test_output_is_independent_of_data_block_content --
    INTERPRETATION: mutation killed.
  MUT-PKG19-05: make `AIGateway.run_operation` skip the
    `ContextManifestWorkspaceMismatch` check -> expected red:
    test_cross_workspace_context_manifest_is_denied --
    INTERPRETATION: mutation killed.
  No prohibited mutation survived; none required a TEST_DESIGN_DEFECT
  classification.

CROSS_LAYER_TESTS: `tests/ai/test_gateway.py`'s own tests exercise the
  full real predecessor chain: NonProofWorkspaceBootstrap (PKG-04) ->
  real `SqlAlchemyAIRecordRepository` (PKG-18/19) -> real `AIGateway`
  (this package) -> real `ai_gateway.context.build_context_manifest` ->
  real `ai_gateway.prompt.build_invocation_prompt` -> real
  `MockProviderAdapter.invoke` -> real
  `ai_gateway.validator.validate_response` -> real
  `ai_generations`/`ai_context_manifests`/`ai_derived_artifacts` rows,
  live-DB-joined and constraint-proven end to end for the first time in
  this codebase's AI path. `tests/boundaries/test_bnd_009_ai_invocation.py`/
  `test_bnd_010_ai_output.py` additionally prove both new evaluators
  compose with the generic `boundaries.registry.evaluate_chain` engine
  (PKG-08) unmodified.

RECURSIVE_REGRESSION_RESULTS: Full existing suite (PKG-00 through
  PKG-18's tests) re-run alongside PKG-19's new tests, both without a
  database (549 passed, 293 skipped) and with a live PostgreSQL 17
  instance (841 passed, 1 skipped) -- 0 regressions after fixing two
  previously-green tests' own now-outdated assumptions (disclosed
  below, the identical "a previously green package that becomes
  semantically invalid blocks this package, fix it in scope" rule
  PKG-13/PKG-18 already applied). check_architecture_dependencies.py
  re-run clean, confirming all 17 disclosed extensions remain intact.

P_CLAIMS_TESTED:
  P-04 (AI cannot contaminate protected Burst): further exercised --
    `test_unauthorized_invocation_is_denied_and_creates_no_generation`
    now proves, against the REAL `AIGateway`, that a denied invocation
    creates literally zero `ai_generations` rows (not merely that a
    pure function returns DENY, PKG-07/09's own prior proof).
  P-05 (AI analysis only through an approved post-Burst operation):
    substantially exercised -- a real `AIGateway`/`MockProviderAdapter`/
    BND-009 now exist and are proven correct together; full exercise
    (a real HTTP request through a governed `RequestAIAnalysis`
    Command evaluating the full BND-001..009 chain) remains
    SUCCESSOR_NOT_BUILT -- no Command is assigned to this package.
  P-06 (AI output remains derived/proposal): substantially exercised --
    a real, validated `AIDerivedArtifact` is now persisted end to end,
    structurally incapable of becoming any of BND-010's own named
    forbidden effects.
  P-07 (AI cannot directly write canonical storage): substantially
    exercised -- `ai_gateway`/`ai_contracts`/`persistence.
    ai_record_repository` import no canonical-write machinery; the
    `ai_gateway_writer` DB-principal separation (14 section 8) remains
    unchanged and still deferred to migration 012_security_events_rls.
  P-23 (AI Gateway exclusive provider path): introduced and dynamically
    exercised for the first time -- `test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider`
    scans the real repository and proves exactly one production module
    can reach the one provider adapter that exists. Full exercise
    against a REAL provider (not the mock) remains BLOCKED by
    HARD-DEP-002, unchanged.

PROOF_ARTIFACTS:
  - 841-test live-database pass, including 25 distinct adversarial
    proofs (13 mandatory package-specific + 12 novel/adapted)
  - Real `ai_generations`/`ai_context_manifests`/`ai_derived_artifacts`
    rows produced end to end by the real `AIGateway`, live-DB-joined
    and FK-proven (including the newly-closed
    `ai_generations.ai_context_manifest_id` retrofit)
  - A real, dynamic P-23 exclusivity proof scanning actual production
    source, not a fixture tree
  - Real `BoundaryProof.evidence_proof_refs` populated by BND-010 for
    an AI_VALIDATION_PROOF reference (second use of that field, after
    BND-013/PKG-17's own DOMAIN_EVIDENCE use)
  - A genuine prompt-injection payload flowing through the REAL
    pipeline (context -> prompt -> mock provider -> validator ->
    persistence) with a byte-identical outcome to a benign control
  - Architecture dependency/provider-SDK/test-only-import/migration
    checker PASS output, including a full upgrade to head
    7c2e8a4f1d6b and a downgrade(-1)/re-upgrade cycle
  - Diff audit (inline answers below)
  - Mutation-kill analysis (5 mutations, all killed)

FORBIDDEN_DEPENDENCY_CHECK: PASS (two disclosed, tested extensions:
  boundaries -> ai_contracts, persistence -> ai_gateway, both cited
  inline and now regression-tested)
PROVIDER_SDK_CHECK: PASS
TEST_ONLY_IMPORT_CHECK: PASS

DIFF_AUDIT:
  New semantic type/enum value: yes, but none invented -- `CoachMode`'s
    7 values are 08 section 10's own exact closed list;
    `MockProviderOutcome`'s 4 values are this package's own disclosed
    `[IMPLEMENTATION CHOICE]` for deterministic scenario selection
    (mirrors `commit.coordinator.CommitInjectionPoint`'s own precedent
    of naming test/failure scenarios as a closed enum). No new
    AIGeneration/AIOP/AI_VALIDATION_PROOF vocabulary was added --
    PKG-18's own closed vocabularies are reused verbatim.
  New DB write path: yes, disclosed -- exactly the `ai_context_manifests`
    remainder of 14 section 9's own 007_ai_operational bucket, plus the
    retrofitted FK PKG-18 explicitly named as its own forward-reference
    gap.
  New authority path: none -- `ai_gateway`/`boundaries.bnd_009_*`/
    `bnd_010_*` import no new authority concept; BND-009/010 never
    resolve or grant authority, only gate on caller-supplied facts.
  Weakened boundary: none -- BND-009/BND-010 are new evaluators adding
    strictly new DENY/REQUIRE conditions where none existed before; no
    existing boundary's own ALLOW path was widened.
  Easier test / removed negative test / admin shortcut /
    projection/cache truth / AI canonical authority / broader Workspace
    scope: none.
  Changed migration semantics: no prior migration edited, only a new
    additive migration plus one additive retrofit FK on a predecessor
    table that already disclosed exactly this future closure.
  Forbidden dependency: two new, disclosed, regression-tested
    extensions -- boundaries -> ai_contracts, persistence -> ai_gateway.
  Files touched outside this package's own new-file set:
    `persistence/ai_record_repository.py`, `persistence/tables.py`,
    `scripts/check_architecture_dependencies.py` -- all
    explicitly-named predecessor extension points; and TWO
    previously-green tests whose own assumptions this package's
    legitimate new capability invalidated:
    (1) `tests/ai/test_burst_ai_block.py`'s own
    `test_no_ai_gateway_or_provider_module_is_reachable_from_this_package`
    asserted the WHOLE `ai_gateway` package stays empty -- no longer
    true now that this package gave it real (non-invocation)
    orchestration content; fixed to check the precise claim it always
    meant (no Burst-protected module imports `ai_gateway`/`ai_contracts`
    at all), the identical fix PKG-18 already applied to this same
    test's `ai_contracts` half.
    (2) `tests/security/test_ai_gateway.py`'s own docstring explicitly
    promised its dynamic P-23 half would land at PKG-19 -- delivered
    here, not a defect, an intentional deferred completion.
    No production bug found this package; no test-expectation bug in
    this package's OWN new tests either, except one real GATEWAY
    design gap caught by its own first live-DB test run (not a
    test-only bug): `AIGateway.run_operation` initially referenced
    `context_manifest.ai_context_manifest_id` on the newly-created
    `AIGeneration` without ever persisting the manifest itself, which
    the real composite FK correctly rejected
    (`ForeignKeyViolation`) -- fixed by having `run_operation` persist
    the manifest (idempotently, supporting legitimate retry reuse per
    08 section 54.1) before creating the generation, the correct
    architectural fix, not a test workaround.

ARCHITECTURE_RECONSTRUCTION_RESULT:
  REQUEST -> ACTOR: real `ActorIdentity` (test fixtures) /
  SUCCESSOR_NOT_BUILT for a real HTTP path -> WORKSPACE (real
  WorkspaceId carried on every construct) -> CURRENT STATE (real
  `AIGeneration`/`AIContextManifest`/`AIDerivedArtifact` rows, walked
  through the genuine 08 section 15 lifecycle) -> CURRENT GOVERNANCE /
  CURRENT AUTHORITY: NOT_APPLICABLE (14 PKG-19 AUTHORITY: "No AI
  authority"; structurally impossible, no authority import) -> HUMAN
  DECISION: NOT_APPLICABLE -> EVIDENCE: NOT_APPLICABLE (AI_VALIDATION_PROOF
  explicitly distinct from DOMAIN_EVIDENCE) -> BOUNDARIES: real
  `Bnd009AiInvocationEvaluator`/`Bnd010AiOutputEvaluator`, each
  independently proven correct, but NOT invoked from inside
  `AIGateway` itself (14 section 3.1's own dependency ceiling for
  `ai_gateway` excludes `boundaries` -- see DIFF_AUDIT/AUTHORITY_PATH)
  -> BND-014: SUCCESSOR_NOT_BUILT (AI operational writes go through
  `ai_gateway_writer`, not `governed_commit_writer`/CommitCoordinator,
  per 14 section 8's own DB-principal separation) -> COMMAND:
  SUCCESSOR_NOT_BUILT (no Command assigned) -> COMMIT UNIT:
  NOT_APPLICABLE for this write path -> CANONICAL MUTATION: real
  (`AIRecordRepository` INSERT/UPDATE, proven directly against live
  PostgreSQL, structurally incapable of reaching any OTHER canonical
  table) -> AUDIT / OUTBOX / EVENT: SUCCESSOR_NOT_BUILT -> RESULTING
  STATE: real, live-DB-joined rows across all three AI-operational
  tables. This is a substantially longer legitimate chain than PKG-18's
  own (which stopped at "CANONICAL MUTATION" with no orchestration at
  all) -- the first package to prove a complete, real Gateway pipeline
  end to end, even though the boundary-to-orchestrator wiring itself
  remains a disclosed hand-off point for a future package.

KNOWN_LIMITATIONS:
  - `AIGateway.run_operation` has no production caller yet -- no
    Command (`RequestAIAnalysis`) is assigned to this package; the
    same disclosed "engine built, no concrete production caller"
    pattern `CommitCoordinator` (PKG-13, before PKG-14/15) and
    `EvidenceRepository` (PKG-16) already carry.
  - BND-009/BND-010 are NOT invoked from inside `AIGateway` itself --
    14 section 3.1's own "May depend on" table for `ai_gateway`
    excludes `boundaries`, so a future package (with `application`-
    layer scope, outside this package's own `FILES_ALLOWED_TO_CREATE`)
    must evaluate the real boundary chain and pass its verdict into
    `run_operation`'s own `invocation_authorized: bool` parameter --
    disclosed, not silently deferred.
  - No real provider adapter exists -- HARD-DEP-002 (real provider
    eligibility) remains BLOCKED; `MockProviderAdapter` is the only
    and permanent-for-this-phase provider.
  - `AIContextManifest`'s own allowlist builder takes caller-resolved
    `(ref, version)` pairs; no live Evidence/Question read-port wiring
    exists yet to resolve those refs automatically -- disclosed,
    matches `evidence.freshness`'s own identical "caller performs the
    read" precedent.
  - Sandbox Python remains 3.10.12 against the architecture's required
    >=3.13 (unchanged disclosed gap from PKG-00 onward).

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
  BLOCKED. Used only via NonProofWorkspaceBootstrap in test fixtures;
  HARD-DEP-002 specifically blocks any real (non-mock) provider
  adapter from ever being built.

NEW_GAPS_DISCOVERED: none new. Two previously-green tests' own
  assumptions became outdated by this package's own legitimate,
  in-scope work -- fixed, fully disclosed under DIFF_AUDIT above, not
  new gaps in the architecture itself. One real design gap (context
  manifest persistence ordering) was caught and fixed during this
  package's own development, also disclosed under DIFF_AUDIT.

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `CoachMode`'s 7 values
  are 08 section 10's own exact, verbatim closed vocabulary.
  `AIContextManifest`'s field list is 09 section 54's own, verbatim.
  `InvocationPrompt`'s own shape materializes 08 section 8's own
  closure formula exactly (AI Operation Contract + Prompt Template
  Version + Mode Template + Bounded Context; Tool Declaration
  NOT_APPLICABLE, no tool access in scope). BND-009/BND-010 introduce
  no new Decision Right, authority class, or transition -- both gate
  purely on facts 06 sections 15/16 already name. No new Command,
  Query, Event, or canonical write path was introduced; BND-009/010
  are built but not wired into a concrete caller, matching this
  package's own explicit dependency ceiling rather than a shortcut.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-20 (Event and outbox worker) becomes
  DAG-eligible now that its required predecessors are verified.
  Eligibility is not authorization.
HUMAN_GATE_REQUIRED: YES -- 14 PKG-19's own coding prompt:
  "HUMAN_GATE_REQUIRED::YES at package level. Do not authorize any
  successor." Phase 7 (AI Gateway / Derived Artifacts) is now complete
  across both its assigned packages (PKG-18, PKG-19). Do not authorize
  PKG-20 (Phase 8, Event/Projection) without explicit human
  authorization naming the package and this package's commit hash.
```
