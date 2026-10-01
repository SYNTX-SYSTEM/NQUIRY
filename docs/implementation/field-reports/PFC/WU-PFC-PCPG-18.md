# WU-PFC-PCPG-18 — Runtime composition R-03 → R-12 + actor-safe `PCPG-R12/1` serialization

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-18 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization (new composition; one existing module extended) |
| Human authorization | "SYNTX::SFE MODE = IMPLEMENTATION … WORK_UNIT = WU-PFC-PCPG-18 … RUNTIME COMPOSITION R-03 → R-12 + ACTOR-SAFE PCPG-R12/1 SERIALIZATION." Full instruction (wire contract, B-10 deny-list, EXPLICITLY ABSENT list, laws, failure path, 22 falsifier categories) honored clause-by-clause below. |
| Predecessor | `pfc-integration` `a6c39bfbe358a3805d8dd02a1beaa8d05c50f2b5` (`checkpoint-PFC-PCPG-17`, pushed). |
| FBR-PCPG-18 | `R-02 OUTPUT → runtime composition of R-03…R-12 (never R-11, never R-13) → ActorSafeProjection → PCPG-R12/1 serialization → governanceObservation`. |
| Preservation confirmed | `git diff --stat` against every R-01…R-12 producer module except `http_pcpg.py` itself: **empty**. `pcpg_observation.py` (R-01/R-02), `pcpg_field_snapshot.py` (R-03), `pcpg_field_pulse.py` (R-04), `pcpg_simplix.py` (R-05), `pcpg_candidate_deltas.py` (R-06), `pcpg_delta_evaluation.py` (R-07), `pcpg_composed_effect.py` (R-08), `pcpg_chain_results.py` (R-09), `pcpg_capability.py` (R-10), `pcpg_eligible_content.py` (R-11, never called), `pcpg_actor_projection.py` (R-12): all byte-identical to `checkpoint-PFC-PCPG-17`. `docs/architecture/` diff: empty — Architecture 26 not touched. |
| Files touched | `packages/application/pcpg_runtime_composition.py` (new), `packages/application/http_pcpg.py` (extended), `tests/e2e/test_pcpg_runtime_composition.py` (new), `tests/e2e/test_http_pcpg.py` (new), `tests/e2e/test_pcpg_observation_ingress.py` (two stale falsifiers repaired, §3). |

## 2. Execution record

**Narrowest intended delta, honored exactly:**
- New file `packages/application/pcpg_runtime_composition.py`: the pure R-03→R-12 composition, `derive_governance_observation(ports, principal, ingress) -> ActorSafeProjection | GovernanceObservationUnavailable`. Calls, in canonical order: `reconstruct_field` (R-03) → `derive_pulse` (R-04) → `observe_semantics` (R-05) → `form_candidate_deltas` (R-06) → `evaluate_deltas` (R-07) → `compose_effect` (R-08) → `derive_chain_result` (R-09) → `derive_capability` (R-10) → `derive_actor_safe_projection` (R-12). **R-11 is never called** — its own PRECONDITION (non-empty MLT) is vacuously never satisfied (WU-7 through WU-17's own cross-checked fact) and its own output is on the B-10 DENY list regardless.
- `packages/application/http_pcpg.py` extended (not refactored): `dispatch_submit_observation` now calls `derive_governance_observation` immediately after R-01/R-02 succeed; `_result_body` takes the real result instead of hardcoding `None`; the whole `PCPG-R12/1` wire-serialization layer (`_delta_wire`, `_action_wire`, `_semantic_observation_wire`, `_first_broken_relation_wire`, `_authority_requirement_wire`, `_chain_result_wire`, `_capability_wire`, `_governance_observation_wire`) is new, pure presentation code — every value read verbatim from the real producers' own dataclasses, nothing computed.
- No producer module from R-01 through R-12 was refactored for convenience; no migration; no CYAN/Architecture 26 change; no provider SDK import (`check_provider_sdk_imports.py`: PASS).

**Wire contract `PCPG-R12/1`**, exactly as directed:
```
governanceObservation =
    {"kind": "unavailable", "reasonCode": <one of 3 real codes>}
  | {"kind": "current", "contract": "PCPG-R12/1",
     "basis": {rawIntentDigestSha256, derivationTime},
     "semanticObservation": {...}, "deltas": [...], "chain": {...},
     "capability": {...}, "composedProofCeiling": str | None}
```
The outer HTTP envelope's own `"kind": "ok"` / 200 status is governed solely by R-01/R-02's own success, unchanged by this Work Unit — `governanceObservation`'s own nested `kind` is FBR-PCPG-18's own, independent discriminator (a query that honestly cannot derive today's governance state is still a successful query about the real, current Field).

**Fail-closed, three real reason codes, each from its own real cause:**
- `SEMANTIC_OBSERVATION_UNAVAILABLE` ← R-05's own `SemanticObservationUnavailable` (no clause of the raw intent could be parsed).
- `FIELD_RECONSTRUCTION_UNAVAILABLE` ← R-03's own `reconstruct_field` **raising** (`QueryDenied`, see §4 discrepancy note below) — never for a merely-`unresolved` snapshot, which R-03's own design already carries gracefully (ABSENT != FALSE, UNKNOWN != DENIED).
- `PROJECTION_INCOMPLETE` ← any other, genuinely unexpected failure from R-04 onward, caught broadly and deliberately so a real incident never surfaces as an uncaught 500 and never as a silently-synthesized partial capability value.

**Scope deliberately not covered, disclosed in the new module's own docstring, not silently narrowed:**
- `data_classifications_by_delta_id` / `flags_by_delta_id` (R-07's own optional richer inputs) are not populated: correlating a `CandidateDelta` back to its originating `SemanticAction` is a new index this Work Unit does not build. Every `PROVIDER_COMPUTATION` delta in the real runtime therefore resolves to `INDETERMINATE`/`DATA_GOVERNANCE_NOT_MATERIALIZED` — R-07's own already-honest, already-proven branch for an unsupplied classification, not a regression.
- `observe_semantics` is called without `in_scope_references`/`out_of_scope_references`: every `target` resolves honestly to `None` (UNKNOWN) rather than a guessed reference.

## 3. Two genuinely stale pre-existing falsifiers, found and repaired, not hidden

The affected PCPG suite's first run surfaced 2 failures, both in `test_pcpg_observation_ingress.py` (R-01/R-02's own, previously-closed test file). Neither is a regression in R-01/R-02's own behavior (`git diff --stat` on that file's own production module, `pcpg_observation.py`: empty) — both tests had baked in the historical fact that `governanceObservation` was a hardcoded `None`, a fact this Work Unit's own, authorized change legitimately ends:

1. `test_a_member_gets_an_ok_observation_bound_to_workspace_and_no_session` asserted `body["governanceObservation"] is None  # FBR-PCPG-2..5 not materialized`. Repaired to assert `body["governanceObservation"]["kind"] == "current"` — the real, current, honest value; the full shape is not re-asserted here (that is `test_pcpg_runtime_composition.py`'s/`test_http_pcpg.py`'s own job).
2. `test_an_authority_claim_in_the_raw_intent_changes_nothing_but_the_echo` asserted the entire `governanceObservation` was byte-identical between two requests differing only by an embedded authority claim in the raw intent. That assumption was only ever true vacuously (`None == None`); now that `governanceObservation` is real and itself echoes the raw intent's own text (clauses, spans), the two responses legitimately differ in their text-derived parts. Repaired, and made strictly MORE rigorous than before: a new `_redact_text_derived` helper strips exactly the fields whose own value is a function of the raw intent's own text/length (`basis`, the whole `semanticObservation` sub-object, each delta's own `sourceClause`/`span`) and the test then asserts everything else — in particular `capability`, `composedProofCeiling`, and every delta's own `result`/`reasonCode`/`operation`/`executionClass`/`flags`/`sessionProofCeiling`/`deltaId` — is identical. This is now a real, positive proof of I-01 ("PROMPT != AUTHORITY") at the governance-result level, not merely a vacuous `None == None` check as before.

Both repairs were verified to introduce no new `mypy` issues (pre-existing-noise baseline on this file: 37 errors with `MYPYPATH` unset to match CI's own gate scope, identical before and after this Work Unit's edit) and no new `ruff` issues. The file's own header docstring was updated by one sentence to stop claiming "none of those exist yet" about a semantic observation/delta/capability/governance result, since FBR-PCPG-18 now makes that claim false; the file's own FALSIFIER SCOPE (R-01/R-02 only) is otherwise unchanged.

## 4. A discrepancy found, disclosed, not fixed (R-03 untouched by law)

`pcpg_field_snapshot.py`'s own module docstring claims `reconstruct_field` "Raises `WorkspaceNotFoundError`/`NotAWorkspaceMemberError` (from `workspace_overview`, unchanged)". Direct inspection of `inquiry_queries.workspace_overview` → `_context()` (fresh `grep`, this Work Unit) shows `_context()` already translates both into `QueryDenied("WORKSPACE_NOT_ACCESSIBLE")` before they ever propagate — R-03's own docstring is stale documentation, not stale behavior. This Work Unit's `except QueryDenied:` (not `except (WorkspaceNotFoundError, NotAWorkspaceMemberError):`) is the behaviorally correct catch, confirmed directly by `test_non_member_principal_maps_to_field_reconstruction_unavailable` (a real non-member principal, real DB, real exception type observed). R-03's own file is explicitly out of scope for this Work Unit ("existing R-01…R-12 producer modules must remain semantically unchanged") and was not touched; the discrepancy is recorded here for a future documentation-only pass.

## 5. A disclosed architectural fact this Work Unit's own testing re-confirmed at the composition level

`composed_proof_ceiling` is **always `None`** in the real runtime composition today, for every real request, not merely the ones this Work Unit's own fixtures construct: `compose_effect` (R-08) only ever retains `Result.ALLOWED` deltas, and `evaluate_deltas` (R-07) never assigns `Result.ALLOWED` to any delta anywhere in its own code (confirmed by direct inspection of the full function body this Work Unit re-read) — the same structural, already-disclosed root cause `pcpg_capability.py`'s own module docstring already names for `GOVERNANCE_ADMISSIBLE`. Proven directly, not merely asserted: `test_composed_proof_ceiling_is_honestly_none_in_the_real_runtime_today` (composition level) and the real end-to-end HTTP test both assert it. Not a defect of this Work Unit.

## 6. Falsifier map

**`tests/e2e/test_pcpg_runtime_composition.py`** (11, DB-backed, direct producer call — the established PCPG test convention):
1. `test_successful_composition_produces_a_real_actor_safe_projection`
2. `test_r11_eligible_content_is_never_produced_or_imported` (AST-based: R-11's module is never imported)
3. `test_r13_send_and_provider_execution_are_never_touched` (AST-based: no provider/AI-contract import)
4. `test_unparseable_raw_intent_maps_to_semantic_observation_unavailable`
5. `test_non_member_principal_maps_to_field_reconstruction_unavailable`
6. `test_unexpected_producer_failure_maps_to_projection_incomplete` (monkeypatched `derive_pulse`)
7. `test_governance_observation_unavailable_rejects_an_unknown_reason_code`
8. `test_an_unknown_session_is_unresolved_not_a_composition_failure` (ABSENT != FALSE)
9. `test_per_delta_session_proof_ceiling_reaches_the_real_delta_records`
10. `test_composed_proof_ceiling_is_honestly_none_in_the_real_runtime_today`
11. `test_two_observations_project_independently`

**`tests/e2e/test_http_pcpg.py`** (15: 10 pure wire-serialization, 1 contract-shape, 2 B-10, 4 real end-to-end HTTP over `nquiry_api.main.app` + real cookies + real PostgreSQL, the same harness `test_http_f04.py` established):
1. `test_current_observation_has_the_exact_contract_tag`
2. `test_unavailable_observation_carries_only_kind_and_reason_code`
3. `test_basis_carries_exactly_the_digest_and_derivation_time`
4. `test_composed_proof_ceiling_is_projected_verbatim_including_none`
5. `test_delta_wire_has_exactly_the_named_field_set`
6. `test_chain_wire_carries_first_broken_relation_as_nested_deltas`
7. `test_chain_wire_first_broken_relation_is_null_when_there_is_none`
8. `test_semantic_observation_wire_serializes_every_real_action_field`
9. `test_result_body_governance_observation_is_no_longer_hardcoded_none`
10. `test_b10_forbidden_tokens_never_appear_in_the_current_wire`
11. `test_b10_forbidden_tokens_never_appear_in_the_unavailable_wire`
12. `test_a_real_request_over_http_returns_a_current_governance_observation`
13. `test_a_real_request_over_http_with_unparseable_intent_returns_unavailable`
14. `test_a_real_request_over_http_contains_no_b10_forbidden_token`
15. `test_existing_r01_r02_envelope_fields_are_unaffected_by_this_work_unit` (regression guard)

**26/26 passed**, plus the 2 pre-existing falsifiers repaired in §3 (28/28 across all three files touched). Together these cover every required falsifier category from the instruction: real composition success; R-11/R-13/provider exclusion (structural, AST-based, not textual); all three fail-closed reason codes from their own real causes; the ABSENT != FALSE unresolved-session case; per-delta vs. composed proof-ceiling independence; `GovernanceObservationUnavailable`'s own closed reason-code set; no shared mutable state; exact wire field sets (deny-by-omission, not just by filter); B-10 negative disclosure scanned over the full serialized JSON, twice (unit level and real HTTP level); the real FastAPI route end-to-end, real cookies, real PostgreSQL; a regression guard on every R-01/R-02 field this Work Unit did not touch; and, after repair, a real (not vacuous) proof of I-01 at the governance-result level.

## 7. Mutation proof (manual, 4 guards, production files restored byte-identical after each)

1. **`pcpg_runtime_composition.py`**: removed `except QueryDenied:` around `reconstruct_field` → `test_non_member_principal_maps_to_field_reconstruction_unavailable` failed (real `QueryDenied` propagated uncaught). Restored; `sha256` confirmed byte-identical (`fa3d3fc…`) to the pre-mutation file.
2. **`pcpg_runtime_composition.py`**: removed the broad `except Exception: … PROJECTION_INCOMPLETE` fail-closed wrapper → `test_unexpected_producer_failure_maps_to_projection_incomplete` failed (real `RuntimeError` propagated uncaught). Restored; `sha256` confirmed byte-identical.
3. **`http_pcpg.py`**: dropped `"result"` from `_delta_wire`'s own returned dict → `test_delta_wire_has_exactly_the_named_field_set` failed (exactly 1/14 wire-file falsifiers, the one targeting this field). Restored; `sha256` confirmed byte-identical (`39913da…`).
4. **`http_pcpg.py`**: added a forbidden `"pulse": None` key to `_governance_observation_wire`'s own `"current"` branch → both B-10 falsifiers failed, **including the real end-to-end HTTP one** (`test_a_real_request_over_http_contains_no_b10_forbidden_token`), proving the deny-list check is not merely a unit-level artifact. Restored; `sha256` confirmed byte-identical.

Every mutation was caught by exactly the falsifier(s) targeting it, with no unrelated falsifier flipping — no over-broad or coincidental coverage.

## 8. Proofs (progressive cadence)

- Local: `ruff check` / `ruff format --check` clean on both new production files, both new test files, and the one repaired pre-existing test file; `mypy packages/application/http_pcpg.py packages/application/pcpg_runtime_composition.py`: 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py`: all `PASS`. (`mypy` run directly against `tests/e2e/*.py` is not part of this repository's own mypy gate — CI's own invocation is `mypy packages apps/api/src apps/worker/src scripts`, confirmed from `pyproject.toml`/`ci.yml`; run with `MYPYPATH` set to match CI's intent, both new test files are 0-issue, and the repaired pre-existing file's own pre-existing-noise baseline — 37 errors, none touching this Work Unit's own additions — is unchanged before/after.)
- Local + mutation falsifiers: 28/28 green on the restored files (§3, §6, §7).
- **Affected PCPG suite**: `pytest tests/e2e/ -k pcpg` — **464 passed, 753 deselected, 0 failed** (156.45s), re-run after the §3 repair to confirm the full suite is green, not merely the two files this Work Unit added. First run (before the §3 repair): 462 passed, 2 failed — both accounted for and repaired in §3.
- No full-repository regression performed this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12) and this turn's own explicit instruction ("Do not run a full-repository regression unless the reconstructed Field scope genuinely requires it"): this delta adds one new, narrowly-scoped composition module, extends one HTTP dispatch function's own response body, and repairs two now-stale assertions in one existing test file; no schema change, no migration, no authority/capability-resolution change, no change to any already-closed producer's own semantics.

## 9. Final reconstruction

| | Status |
|---|---|
| **FBR-PCPG-18** | **CLOSED** |
| **R-03…R-12 real request composition** | **MATERIALIZED** (R-11 deliberately excluded, vacuous precondition; R-13 not begun) |
| **PCPG-R12/1 serialization** | **MATERIALIZED** |
| **B-10** | **PRESERVED** (falsified twice: unit level and real end-to-end HTTP level; mutation-proven) |
| **I-12 session-level proof ceiling** | **PARTIAL** — per-delta ceiling reaches the real wire; the composed/aggregate ceiling is real machinery but structurally always `None` today (§5) |
| **Full I-12** | **PARTIAL / NOT COMPLETE** |
| **PROVIDER_EXECUTABLE** | unchanged, current derived value only: `False` |
| **CAN_SEND** | unchanged, current derived value only: `False` |
| **R-13** | **NOT STARTED** |
| **Provider call** | **NONE** |
| **CYAN** | **UNTOUCHED** |

## 10. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** The real R-01…R-12 request pipeline (R-11 deliberately excluded) now runs for one real HTTP request and serializes an honest `PCPG-R12/1` governance observation, fail-closed on every real failure path, never synthesizing a partial capability value. 28/28 falsifiers green (26 new + 2 pre-existing, now-stale falsifiers found and repaired, §3), including 4 real end-to-end HTTP tests against `nquiry_api.main.app` with real cookies and real PostgreSQL. 4/4 mutation guards caught, production files restored byte-identical after each. The full affected PCPG suite is green: 464 passed, 0 failed. Every R-01…R-12 producer module remains byte-identical to `checkpoint-PFC-PCPG-17`; Architecture 26 untouched. R-13, SEND, and provider execution remain untouched; CYAN remains untouched. Per instruction: **does not continue into SOURCE_RELATION, R-13, or CYAN.**
