# WU-PFC-PCPG-8 — R-08: composed effect

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-8 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary." (2026-09-30, carried forward from the R-06 approval turn). |
| Predecessor | `pfc-integration` `eb0e1385a32a736388c35b2a45c596f63e7a4080` (`checkpoint-PFC-PCPG-7`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure composition of real R-07 output). |
| E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-7`) | Confirmed by repository search: `pcpg_delta_evaluation.py` (R-07) real; `grep` for `ComposedEffect`/`retained_set`/`COMPOSABLE`: zero hits — R-08 genuinely absent. R-08's own INPUT ("the delta records") and PRECONDITION ("R-07 is complete for every delta") are both satisfied for the RESULT/REASON subset R-07 already produces. **R-08 is the next First Broken Relation.** No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | The `retained` set (deltas with `Result.ALLOWED` — dependency-graph traversal is unnecessary this increment since R-06's own disclosed scope makes `dependency_edges` always `()`, so "all dependencies retained" is vacuously true) and an honestly-computed `composition_result`: `COMPOSABLE` for an empty retained set (the always-true-today case, proven as a real architectural fact by WU-7); `INDETERMINATE`/`COMPOSITION_CHECKS_NOT_MATERIALIZED` for a non-empty one, since the richer sub-checks R-08's own OUTPUT names (data-class union, external-effect check, composed proof ceiling, purpose coherence, instrumental-to-blocked analysis) have no producer anywhere in this codebase. |
| Must become true | A pure function `compose_effect(records) -> ComposedEffect` exists: the retained set is exactly the `ALLOWED` deltas, in order; the composition result is never a guessed `COMPOSABLE` for a case this module cannot actually check. |
| Must remain true | `pcpg_delta_evaluation.Result`/`DeltaRecord` unchanged; every existing route, Command, migration and test. |
| Must remain impossible | A `HUMAN_ACTION_AVAILABLE` delta ever entering the retained set (I-08/§7.3: HUMAN_COMMAND never enters the MLT, even when available); a non-empty retained set waved through as `COMPOSABLE` without the missing checks being disclosed. |
| Falsifiers | `tests/e2e/test_pcpg_composed_effect.py`: 11 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (11 cases) was written first, importing `CompositionResult`, `compose_effect` from `application.pcpg_composed_effect`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_composed_effect'` — the correct reason. All 11 falsifiers passed on the first real GREEN run (no authoring-bug detour), a direct result of the design already being fully grounded in WU-7's own already-proven fact (no delta is ever `ALLOWED` today) before any code was written.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no composed-effect producer exists for R-09 (chain results) to consume
CONSUMER         (future) R-09 (FBR/MLT/NVT/HAR), R-11 (provider-projection eligibility) --
                 not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-08 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-08), composed effect
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-08; `04_OBSERVATION_RESULT.md` §7.1 (composition, verbatim); WU-PFC-PCPG-7's own already-proven fact (no delta is ever `ALLOWED` today) — the load-bearing foundation this Work Unit builds on rather than re-derives.

**4 REPAIR** (2 new files).
- `packages/application/pcpg_composed_effect.py`: `CompositionResult` (this Field's own §7.1 vocabulary, first materialized here — I-20), `ComposedEffect`, `compose_effect()`. The retained-set filter is `result is Result.ALLOWED`; a non-empty result is `INDETERMINATE`/`COMPOSITION_CHECKS_NOT_MATERIALIZED`, never a guessed `COMPOSABLE`.
- `tests/e2e/test_pcpg_composed_effect.py`: 11 falsifiers (§3), including a falsifier proving the filter's own correctness via a hand-built `ALLOWED` record — independent of today's degenerate real-world instance, matching I-19's own "the relation's defined behavior, not only its narrower current observable case."

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_delta_evaluation` | NOT AFFECTED | Read-only consumption; `Result`/`DeltaRecord` unchanged. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-08 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- Producer proof: `test_no_allowed_deltas_gives_an_empty_retained_set_and_composable`, `test_the_retained_filter_selects_exactly_the_allowed_deltas`.
- Adversarial proof: `test_human_action_available_is_never_retained_even_though_it_is_a_positive_result` (I-08/§7.3, directly against a positive-but-wrong-class result, not just a negative one); `test_a_non_empty_retained_set_is_honestly_indeterminate_never_guessed_composable` + `test_multiple_allowed_deltas_all_retained_together` (the honesty guarantee, proven against a real, hand-built `ALLOWED` record); `test_composition_result_is_this_fields_own_complete_vocabulary` (I-20, static); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 3 guards):**
  1. Widened the retained filter to also include `HUMAN_ACTION_AVAILABLE` → `test_human_action_available_is_never_retained_even_though_it_is_a_positive_result` failed. Restored; byte-diff clean.
  2. Made a non-empty retained set return `COMPOSABLE` (the guess this module is designed to never make) → both `test_a_non_empty_retained_set_is_honestly_indeterminate_never_guessed_composable` and `test_multiple_allowed_deltas_all_retained_together` failed. Restored; byte-diff clean.
  3. Broke order preservation (sorted the retained set by `delta_id`) → `test_retained_set_preserves_delta_order` failed. Restored; byte-diff clean.
  Final restore hash `093cbb7a3f1c9e7f7b24543b80a19611315982dc21f27a39bc6cf723982430a2` confirmed byte-identical to the pre-mutation baseline after every mutation.
- **PRESERVATION / REGRESSION.** Combined PCPG suite (composed_effect + delta_evaluation + candidate_deltas + field_pulse + field_snapshot + simplix + operation_index + observation_ingress + isolation_sweep): **419 passed, 0 failed** (11 + 26 + 69 + 15 + 17 + 91 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN (the last one at this cadence — see §12 below):** started only after `git status`/`git diff` confirmed the complete final tree (0 modified, 3 new files, all this Work Unit's own, including this report); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff), each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits; a mid-run Human Authority proof-cadence decision explicitly directed that this already-running regression NOT be interrupted). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2331 passed, 15 skipped, 0 failed, in 3057.61s (0:50:57)** — exactly 2320 (WU-7's own closing count) + 11 (this Work Unit's own falsifiers), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**12 PROOF-CADENCE CHANGE (Human Authority decision, received while this Work Unit's regression was already running).** From the next Work Unit onward, a local defect, failed falsifier or failed mutation proof no longer automatically triggers a full-repository regression. Proof radius is now progressive and derived from the relations a delta actually affects: `IMPLEMENT/REPAIR → LOCAL FALSIFIERS → LOCAL MUTATION PROOF → AFFECTED SUITES → CONTINUE`, escalating to a broader PCPG-integration regression at meaningful field boundaries, and to the full-repository regression only at final PCPG field closure, a deliberately selected major checkpoint, or when a change genuinely touches a global invariant (migrations, shared persistence, session/auth substrate, authority/capability resolution, cross-field protocol/serialization, repository-wide import/runtime behavior). This Work Unit's own full-repository run, already in flight when the decision arrived, was explicitly preserved as the current broad preservation checkpoint rather than interrupted — it remains valid and is not superseded by the cadence change.

**10 INVERSE SWEEP (E6).**
```text
retained            <- DeltaRecord.result is Result.ALLOWED, quoted from the real R-07     -- canonical, sourced (a)
                        producer; dependency-completeness is vacuously true given R-06's
                        own disclosed dependency_edges == () (not re-derived here)
composition_result   <- COMPOSABLE for an empty retained set (trivially true: nothing can    -- versioned SFE
  (empty case)            cross a boundary that contains nothing)                                rule (c)
composition_result    <- INDETERMINATE, honestly disclosed: the real sub-checks this          -- disclosed absence,
  (non-empty case)        relation's own OUTPUT names have no producer anywhere in this           never fabricated
                           codebase -- never guessed COMPOSABLE
```
No CACHED value: every call recomputes from its own real input (`test_same_inputs_give_the_same_effect_every_time` proves determinism without a cache). No DUPLICATED value: the `ALLOWED` filter reads `DeltaRecord.result` directly, never re-evaluating readiness a second time. No PROMOTED value: `ComposedEffect` is presented exactly as a derived composition fact, never as authority or a capability grant. No BYPASSED value: no consumer exists yet (R-09 not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-08 is materialized and closed for its own disclosed scope. Re-running E1 against this now-committed state (to be re-derived fresh, not assumed here, per the same discipline as every prior transition): R-09 (chain results: FBR/MLT/NVT/HAR/PARTIAL) becomes the candidate next relation, since its own INPUT ("the delta records, their dependency order, the composition result and the Pulse") is now satisfied — R-06's deltas, R-07's records, this Work Unit's composition result, and R-04's Pulse are all real. Neither R-08's remaining richer sub-checks nor R-06's IMPLIED-delta scope block R-09 directly (R-09 evaluates whatever it is given, the same principle that let R-07 and R-08 proceed on R-06's DIRECT-delta subset alone). Not a Human Authority boundary, not a future Field.

## 3. Falsifier map (11 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_no_allowed_deltas_gives_an_empty_retained_set_and_composable` / `test_an_empty_delta_list_is_also_trivially_composable` | 2 | the always-true-today case |
| `test_the_retained_filter_selects_exactly_the_allowed_deltas` | 1 | the filter itself, proven independent of today's degenerate instance |
| `test_a_non_empty_retained_set_is_honestly_indeterminate_never_guessed_composable` / `test_multiple_allowed_deltas_all_retained_together` | 2 | never a guessed COMPOSABLE |
| `test_human_action_available_is_never_retained_even_though_it_is_a_positive_result` | 1 | I-08/§7.3 |
| `test_retained_set_preserves_delta_order` | 1 | ordering fidelity |
| `test_same_inputs_give_the_same_effect_every_time` | 1 | determinism |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static |
| `test_composition_result_is_this_fields_own_complete_vocabulary` | 1 | I-20 |
| `test_candidate_delta_type_is_not_imported_unused` | 1 | import hygiene |

## 4. Deliberate exclusions (not defects; later Work Units)

- Data-class union, external-effect check, composed proof ceiling, purpose coherence, instrumental-to-blocked analysis: each needs a producer that does not exist in this codebase today (a data-class classifier, FBR-PCPG-3/GAP-11-006 still OPEN; an AI-contract output-class registry; a proof-ceiling producer; a purpose-coherence rule beyond SIMPLIX's own minimal one).
- R-09 through R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-08 (composed effect) is materialized for its own disclosed scope, independently falsified (11/11), mutation-proven (3/3 guards killed and restored), and proven repository-wide preservation-clean (2331 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). This is the last Work Unit closed under the full-repository-regression-per-WU cadence; §12 records the Human Authority proof-cadence change now in effect for subsequent Work Units.
