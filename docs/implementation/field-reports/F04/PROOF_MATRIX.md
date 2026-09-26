# F04 — Proof matrix (backend, pre-WU-04.8)

Every falsifier of `F04_ARCHITECTURE_RECONSTRUCTION.md` §15 (revision 6) and
every pre-implementation binding, mapped to the test that proves it.

- **Runner:** RED worktree, isolated database `nquiry_f04_red_test` (Alembic
  head `c2e7b9a4f513`).
- **Status:** PASS = green now. The falsifier was proven RED either before the
  repair, against the pre-F04 schema (`a8d3f1c6e902` downgraded: 27 of 28
  WU-04.1/04.3 tests fail), or by the mutation proof (`evidence/mutation_proof.txt`,
  originally 20 of 20 mutations killed; after the R1 / R2 repair 24 of 24,
  `evidence/mutation_proof_r1r2.txt`).
- **Mock ceiling:** every AI result here comes from MockProvider. MOCK RESULT ≠
  REAL PROVIDER PROOF (HARD-DEP-002 is external).

Paths abbreviated: `e2e/` = `tests/e2e/`, `reg/` = `tests/regression/`,
`bnd/` = `tests/boundaries/`.

## L: ledger (WU-04.0)

| Id | Test | Status |
|---|---|---|
| L-1 | `reg/test_f04_ledger.py` (4): 51 decisions, 42 ESTABLISHED, 80 gaps, REC-018..027, §6 rows, 20 §15B, home pointers in 04/06/08/09. RED before the pointers were written. | PASS |

## A: BEGIN_ANALYSIS (WU-04.1), `e2e/test_f04_begin_analysis.py`

| Id | Test | Status |
|---|---|---|
| A1 | `test_a1_controller_begins_analysis`: ANALYSIS, version +1, BINDING `SESSION:<id>`, `establishedBy`, exactly one unconsumed OA-1 | PASS (M10) |
| A2 | `test_a2_wrong_authority_is_denied`: participant, Owner, outsider, Challenge-scoped binding, non-member | PASS |
| A3 | `test_a3_wrong_state_is_blocked` | PASS |
| A4 | `test_a4_unverified_frozen_set_is_blocked` | PASS (M09) |
| A5 | `test_a5_unresolved_capture_is_blocked` | PASS |
| A6 | `test_a6_stale_expected_version` | PASS |
| A7 | `test_a7_idempotent_replay_and_key_collision` | PASS |
| A8 | `test_a8_no_ai_in_the_transition_commit` (static + no generation) | PASS |
| A9 | `test_a9_exactly_one_session_analysis_row` | PASS |
| A10 | `test_a10_failed_precommit_leaves_nothing` (3 injection points) | PASS |

## B: protected set (WU-04.2), `bnd/test_f04_protected_set_ai_boundary.py`

| Id | Test | Status |
|---|---|---|
| B1 | `test_b1_*`: 5 AI categories × ACTIVE/PAUSED × all 4 actor classes. **RED before repair: 30 failures** (every requester except AI_PROCESSOR). | PASS (M01) |
| B2 | `test_b2_bnd_009_denies_when_burst_not_completed` | PASS (M02) |
| B3 | `test_b3_bnd_009_denies_an_unverified_frozen_set` | PASS |
| B4 | the unchanged F03 suite and the BND-008 ↔ guard differential test (full regression green) | PASS |

## C: effect gate and records (WU-04.3), `e2e/test_f04_system_operation_gate.py`

| Id | Test | Status |
|---|---|---|
| C1 | `test_c1_human_actor_is_denied`; `test_bnd014_denies_system_operation_for_a_human_and_allows_the_service` | PASS (M03, M08) |
| C2 | `test_c2_ai_processor_and_foreign_service_are_denied` | PASS |
| C3 | `test_c3_missing_foreign_or_uncommitted_authorization_is_denied`; `test_c3_session_not_analysis_is_denied` | PASS (M07) |
| C4 | `test_c4_audit_check_accepts_system_operation_and_refuses_unknown`; the SYSTEM_OPERATION audit row itself in E2 and in `evidence/runtime_inverse_provenance.txt` | PASS |
| C5-C7 | `test_c5_c6_c7_proof_manifest_artifact_are_immutable` | PASS |
| C8 | `test_c8_second_generation_for_the_same_oa_is_refused`; `test_one_non_terminal_generation_per_session_operation` | PASS |
| C9 | `e2e/test_f04_clustering.py::test_c9_k8_original_run_then_automatic_clustering` | PASS |
| rule 5 / 8 / 9 | `test_superseded_oa_can_never_execute`, `test_request_case_must_match_persisted_state`, `test_generation_lineage_must_equal_its_oa`, `test_oa_shape_outside_rule_2_is_refused`, `test_operation_authorization_rows_are_immutable`, `test_generation_oa_fields_are_identity_immutable` | PASS |

## D: contract and input (WU-04.4), `e2e/test_f04_analysis_input.py`

| Id | Test | Status |
|---|---|---|
| D1 | `test_d1_manifest_is_exactly_the_frozen_set` | PASS |
| D2 | `test_d2_extra_missing_or_foreign_question_is_refused` (3); `test_d2_run_refuses_before_the_provider_when_the_set_is_unverified` | PASS (M13) |
| D3 | `test_d3_fingerprint_mismatch_is_refused` | PASS |
| D4 / D5 | `test_d4_d5_schema_is_closed_and_refs_are_manifest_only` (13 attacks); `tests/ai/test_validator.py` | PASS (M11, M12) |
| D6 | `test_d6_prompt_injection_changes_neither_structure_nor_output`; `tests/ai/test_gateway.py::test_prompt_injection_does_not_change_the_outcome` | PASS |
| D7 | `test_d7_no_cross_workspace_refs` | PASS |
| D8 | `test_d8_normalized_text_unchanged_after_the_full_flow`; runtime: `normalized_text written 0` | PASS |

## E: run, acceptance, RETRY / RECOVERY (WU-04.5), `e2e/test_f04_analysis_run.py`

| Id | Test | Status |
|---|---|---|
| E1 / E2 | `test_e1_e2_original_run_is_accepted_atomically` (PI-1; SYSTEM_OPERATION audit ref = BEGIN_ANALYSIS; OA-3 created) | PASS (M14) |
| E3 | `test_e3_failed_or_rejected_output_is_never_accepted` (6 outcomes) | PASS |
| E4 | `test_e4_the_gateway_writes_nothing_and_only_f04_system_code_calls_it` | PASS |
| E5 | snapshot diff in E1 / E3 / K-tests | PASS |
| E6 | `test_e6_a_second_run_for_the_same_oa_is_refused` | PASS (M05) |
| E7 / E15 / E16 | `test_e7_e15_e16_retry_after_failure`; `e2e/test_f04_inverse_provenance.py::test_p2_e16_branch_2b_retry` | PASS |
| E8 | `test_e8_request_after_accepted_success_is_blocked` | PASS |
| E9 | `test_e9_request_by_non_controller_is_denied` | PASS |
| E10 | `test_e10_request_while_a_generation_is_non_terminal_is_blocked` | PASS (M16) |
| E11 | `test_e11_recovery_of_an_unconsumed_oa1`, `test_e11_p4_repeated_recovery` | PASS (M04) |
| E12 | `test_e12_run_while_session_not_analysis_is_blocked` | PASS |
| E13 | `test_e13_ai_processor_cannot_invoke` | PASS |
| E14 | `test_e14_output_claiming_a_decision_is_denied_by_bnd_010` | PASS (M17) |
| E17 | `test_e17_latest_unconsumed_governs_over_an_older_failure` | PASS |
| E18 | `test_e18_case_mismatch_is_rejected`; HTTP 400 in `e2e/test_http_f04.py` | PASS (M15) |
| PI-1 failure branch | `test_acceptance_denial_leaves_honest_failure_and_no_artifact`, `test_execute_failed_precommit_leaves_oa_unconsumed` | PASS |

## F: mock lane (WU-04.6), `reg/test_f04_static_gates.py`

| Id | Test | Status |
|---|---|---|
| F1 | `test_f1_*` (PRODUCTION, STAGING, unset, unknown refused; DEVELOPMENT / TEST allowed; startup wiring). **Runtime:** a uvicorn process with `PRODUCTION` + mock exits 1 (`evidence/runtime_f1_production_refusal.txt`). | PASS (M18) |
| F2 | E1 (`provider = mock`, `proof_class = MOCK_NON_PROOF`); HTTP marker in `test_h1_h2_h3_g1_g3_g4_*`; runtime marker | PASS (M19) |
| F3 | E3 (TIMEOUT / PROVIDER_ERROR → FAILED); HTTP `test_h4_g5_*` (UNAVAILABLE, frozen set still served) | PASS |
| F4 | `test_f4_only_the_mock_adapter_exists`; `PROVIDER_SDK_IMPORT_CHECK::PASS` | PASS |
| F5 | the proof row references its generation (FK); `resolve_provenance` reads the provider from the generation (`test_p1_*`: `provider == "mock"`) | PASS |
| F6 | `test_f6_the_ai_lane_imports_no_network_or_sdk`, `test_f6_mock_invoke_performs_no_egress` (socket patched to fail) | PASS |

## K: clustering (WU-04.9), `e2e/test_f04_clustering.py`

| Id | Test | Status |
|---|---|---|
| K1 / K2 / K3 | `test_c9_k8_original_run_then_automatic_clustering`; `test_cluster_membership_of_a_non_frozen_question_is_refused` | PASS |
| K4 / K6 | `test_k4_k6_rejected_clustering_output_leaves_no_clusters` | PASS |
| K5 | `test_k5_no_priority_or_selection_field` (schema + validator) | PASS |
| K7 | `test_k7_no_clustering_when_analysis_fails_or_is_rejected` | PASS |
| K8 / C9 | `test_c9_k8_*` | PASS |
| K9 / K11 / K16 / K17 | `test_k9_k11_k16_clustering_retry_after_analysis_retry` | PASS |
| K10 | `test_k10_model_input_is_the_frozen_human_set_only` | PASS |
| K12 | `test_k12_non_controller_request_is_denied`, K7 (`NO_ACCEPTED_ANALYSIS`) | PASS |
| K13 | in `test_k9_*` (`RESULT_ALREADY_ACCEPTED`; a second run refused) | PASS |
| K14 / K19 | `test_k14_k19_recovery_of_an_unconsumed_oa3`; `test_p6_k19_*` | PASS |
| K15 | `test_k15_oa3_not_authorized_by_xs_command_is_denied_at_the_gate` | PASS (M06) |
| K18 | `test_k18_forged_precondition_artifact_is_refused` | PASS |
| K20 | `test_k20_request_while_clustering_non_terminal_is_blocked`; case mismatch in `test_k14_*` | PASS |

## G: projection (WU-04.7), `e2e/test_http_f04.py`, `e2e/test_f04_projection.py`

| Id | Test | Status |
|---|---|---|
| G1 | identical views for controller, participant, Owner and member; `test_no_derived_field_while_the_burst_is_active` | PASS (M20) |
| G2 | `test_g2_an_outsider_is_denied` (403); runtime `stranger_position: 403` | PASS |
| G3 | origin AI, generation refs, MOCK marker | PASS (M19) |
| G4 | human Questions unchanged, separate, verbatim (HTTP and runtime) | PASS |
| G5 | `test_h4_g5_failed_run_is_honest_then_controller_retry`; `test_states_are_honest_and_identical_for_the_audience` | PASS |

## H: real stack

| Id | Backend half (proven now) | Browser half |
|---|---|---|
| H1 | runtime phase 1: ANALYSIS, `establishedBy = CMD_BEGIN_ANALYSIS` (BINDING) | **BLOCKED_ON_H8_FOR_WU_04_8** |
| H2 | runtime phase 2: marker AI · DERIVED / PROPOSAL · MOCK / NON_PROOF; Questions verbatim | BLOCKED (WU-04.8) |
| H3 | `audience_views_identical: true` | BLOCKED (WU-04.8) |
| H4 | phase 1 (scripted TIMEOUT → UNAVAILABLE) → phase 2 (controller RETRY → ACCEPTED), on two independent processes | BLOCKED (WU-04.8) |
| H5 | participant begin → `denied`; the Owner's RETRY → 403; the capability names the server's reason | BLOCKED (WU-04.8) |
| H6 | `clustering_status: NOT_RUN` after the failure; ACCEPTED only after the accepted analysis | BLOCKED (WU-04.8) |
| H7 | — (axe, keyboard, mobile are frontend-only) | BLOCKED (WU-04.8) |

## Pre-implementation bindings and concurrency

| Binding | Test | Status |
|---|---|---|
| PI-1 | E1 / E2; acceptance-denial branch | PASS |
| PI-2 | `e2e/test_f04_concurrency.py::test_pi2_multi_transaction_run_commits_each_step_durably` (real commits); runtime phases 1-2 | PASS |
| PI-3 | `test_pi3_only_the_f04_system_module_constructs_the_service_actor`; C2 | PASS |
| PI-4 | the C group | PASS |
| PI-5 | F1 | PASS |
| PI-6 | the K group | PASS |
| Concurrency | `e2e/test_f04_concurrency.py` (6): open begin excludes a second; thread race of 4 begins (exactly 1); race of 4 executions of one OA (exactly 1 accepted, 1 generation); RECOVERY vs EXECUTE of the same unconsumed OA (exactly one side wins); race of 4 RETRY requests (exactly 1 OA-2) | PASS |

## Independent-review repairs R1 / R2 (`REPAIR_R1_R2.md`)

| Id | Test | Status |
|---|---|---|
| R1 must become true | `e2e/test_f04_accepted_output_binding.py::test_r1_every_accepted_artifact_is_the_validated_bytes` (Python and PostgreSQL over persisted rows); real commit `e2e/test_f04_concurrency.py::test_r1_r2_real_commit_happy_path_binds_every_accepted_artifact`; runtime `evidence/runtime_r1r2_persisted_closure.txt` | PASS (M21) |
| R1 must remain impossible (DB) | `test_r1_db_refuses_an_accepted_artifact_that_is_not_the_validated_bytes` (re-serialized content; self-consistent but foreign fingerprint; no VALIDATED proof) | PASS |
| R1 must remain impossible (resolver) | `test_r1_resolver_refuses_a_chain_without_the_validated_proof` (missing, REJECTED, fingerprint, operation); the chain carries `proof_id` | PASS (M22, M22b) |
| R2 must become true | `test_r2_denied_acceptance_persists_no_validated_proof`; `e2e/test_f04_analysis_run.py::test_acceptance_denial_leaves_honest_failure_and_no_artifact`; real commit `test_r2_real_commit_denied_acceptance_leaves_no_validated_proof` | PASS (M23) |
| R2 must remain impossible | `test_r2_db_refuses_a_validated_proof_without_its_accepted_artifact`, `test_r2_db_refuses_a_validated_generation_without_proof_and_artifact` (deferred checks forced IMMEDIATE); real commit `test_r2_real_commit_refuses_an_orphan_validated_proof` (refused AT COMMIT) | PASS |
| R2 unchanged behaviour | `test_r2_rejected_and_indeterminate_proofs_are_unchanged` | PASS |
| C7 after R1 | `e2e/test_f04_system_operation_gate.py::test_c5_c6_c7_*`: the fabricated artifact is refused; the genuine artifact is immutable | PASS |

## Inverse sweep, materialized (§11 items 2a / 2b / 4a / 4b; P1-P6)

`e2e/test_f04_inverse_provenance.py` (7) walks each branch, **through the
VALIDATED proof** (after R1), with an
immutable-records-only reader (statically proven to read no status, state or
current artifact). The runtime chain is in `evidence/runtime_inverse_provenance.txt`.
