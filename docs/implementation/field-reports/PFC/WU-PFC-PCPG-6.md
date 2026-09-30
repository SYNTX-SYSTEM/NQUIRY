# WU-PFC-PCPG-6 — R-06: candidate delta formation (DIRECT deltas)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-6 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "APPROVED. Commit the completed R-04 work unit... then continue autonomously with the derived next First Broken Relation R-06 under the same SFE discipline. Do not choose a successor manually. Derive it from the reconstructed field after checkpoint publication." (2026-09-30). |
| Predecessor | `pfc-integration` `e0a6b3b25d4309d16d6e3db3ee0958183a279dfd` (`checkpoint-PFC-PCPG-5`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (this Work Unit adds no schema; it composes existing real outputs only). |
| E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-5`) | Confirmed by repository search: `pcpg_field_snapshot.py` (R-03), `pcpg_field_pulse.py` (R-04), `pcpg_simplix.py` (R-05) all real; `grep` for `CandidateDelta`/`candidate_delta`/`form_candidate`: zero hits. R-06's own two prerequisites (R-03, R-05) are both satisfied; no sibling ambiguity remained (§0/§11 of `WU-PFC-PCPG-5.md` had already shown closing R-04 unblocks nothing R-06 doesn't already gate). No new bypass path found (re-swept). **R-06 is the next First Broken Relation**, derived, not assumed. |
| Authorized delta (this Work Unit, disclosed scope) | R-06 for DIRECT deltas ONLY: one `CandidateDelta` per REQUESTED-modality semantic action, formed straight from R-05's own output (`SemanticAction`) plus the real, already-closed `pcpg_operation_index`. NOT covered: IMPLIED intermediate deltas (R-06's own PRECONDITION worked example — "on a Session already in ANALYSIS no BEGIN_ANALYSIS delta is implied" — needs a canonical "operation X requires relation/state Y, satisfied or not" index that exists nowhere in this codebase; building one now would be a second, separate, large relation, not this increment's minimum coherent delta). `dependency_edges` is always `()` and `proposed_state` is always `None` in this increment, both disclosed. |
| Must become true | A pure function `form_candidate_deltas(observation, snapshot) -> tuple[CandidateDelta, ...]` exists: every REQUESTED action yields exactly one delta (P-04), none dropped; `operation`/`execution_class` quoted from the real catalog, never re-derived. |
| Must remain true | `pcpg_simplix.observe_semantics`, `pcpg_operation_index.resolve_operation`, `pcpg_field_snapshot.reconstruct_field` all unchanged in their own real behavior (SIMPLIX gained a bug fix — see §2 — but no falsifier of its own regressed); every existing route, Command, migration and test. |
| Must remain impossible | A PROHIBITED/HYPOTHETICAL/CONDITIONAL/ASSERTED action forming a delta; a delta's `execution_class` diverging from the real catalog's own value (P-14-style, I-20); a selection/approval/decision/authority-effect delta ever `PROVIDER_COMPUTATION` (P-05); a delta silently dropped for a genuinely REQUESTED action. |
| Falsifiers | `tests/e2e/test_pcpg_candidate_deltas.py`: 69 cases; `tests/e2e/test_pcpg_simplix.py`: +1 regression case (91 total, up from 90). |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (69 cases) was written first, importing `CandidateDelta`, `form_candidate_deltas` from `application.pcpg_candidate_deltas`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_candidate_deltas'` — the correct reason.

**A real, pre-existing bug found by R-06's own adversarial testing, fixed at its root (SIMPLIX, not R-06).** Two falsifiers failed on the first real GREEN run, both traced to the SAME cause, not to `pcpg_candidate_deltas.py` itself: `pcpg_simplix.py`'s `_looks_like_bare_imperative` used plain substring containment (`"are " in clause_lower`) to detect assertion-claim markers. The verb **"compare"** itself contains the literal substring `"are "` (`comp-are-our`), so any clause beginning with "Compare..." was silently misclassified `ASSERTED` instead of `REQUESTED` — a real defect in the already-checkpointed `checkpoint-PFC-PCPG-3`, invisible to WU-3's own 90 falsifiers because none of them happened to test a verb containing an assertion-marker substring. Fixed at the root: `_ASSERTION_MARKERS` matching now uses a word-boundary regex (`_ASSERTION_MARKER_PATTERN`) instead of plain `in` containment. A dedicated regression falsifier (`test_a_verb_containing_an_assertion_marker_as_a_substring_is_not_misread`) was added directly to `test_pcpg_simplix.py` (now 91 cases, up from 90); all 90 pre-existing SIMPLIX falsifiers were re-run and confirmed still green (no regression from the fix itself). This follows the exact "repair the root, not the symptom, disclose it" discipline this Field has used throughout (WU-PFC-PCPG-1's coverage-guard repair; WU-PFC-PCPG-2's stale-test-scope repair). Two of `test_pcpg_candidate_deltas.py`'s own falsifiers were corrected afterward to assert the CORRECT post-fix behavior, not weakened versions of the original (wrong) expectation — see §6 for the exact before/after.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no candidate-delta producer exists for R-07 to evaluate
CONSUMER         (future) R-07 (per-delta governance evaluation) -- not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-06 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-06), candidate delta
                 formation
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-06 (its own prose, not the header diagram — `WU-PFC-PCPG-4.md` §0's SFE correction); the operation catalog's own real home, `application.pcpg_operation_index` (already closed, FBR-PCPG-2); the semantic observation's own real home, `application.pcpg_simplix` (already closed, R-05).

**4 REPAIR** (2 new files, 1 file repaired).
- `packages/application/pcpg_candidate_deltas.py`: `CandidateDelta`, `form_candidate_deltas()`. Only `Modality.REQUESTED` actions form a delta (R-05's own PROOF — "negated, hypothetical and prohibited actions never become requested actions" — read literally against R-06's PRECONDITION "every requested action yields a delta"). `operation`/`target`/`source_clause`/`span` are read straight from the real `SemanticAction`; `execution_class` is read from `pcpg_operation_index.resolve_operation()` when `operation` is known, `ExecutionClass.UNKNOWN` otherwise (never guessed); `current_state` is read straight from the real `FieldSnapshot.session.state`.
- `tests/e2e/test_pcpg_candidate_deltas.py`: 69 falsifiers (§3).
- `packages/application/pcpg_simplix.py`: the word-boundary regex fix above (§2), disclosed as a repair, not a redesign of SIMPLIX's own scope.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_operation_index` / `pcpg_field_snapshot` | NOT AFFECTED | Read-only consumption; nothing in either changed. |
| `pcpg_simplix` | AFFECTED (bug fix, disclosed) | `_looks_like_bare_imperative`'s assertion-marker matching now uses word boundaries; all 90 pre-existing falsifiers re-run green; 1 new regression falsifier added. |
| `pcpg_field_pulse` | NOT AFFECTED | No import from this module reaches it; confirmed by the end-to-end integration falsifier composing both without collision. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-06 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` (both files) 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- **Two falsifiers corrected to their actual-correct expectation, not weakened, disclosed in full:**
  1. `test_hypothetical_premise_forms_no_delta` originally asserted `deltas == ()` for `"If supplier B were approved, which one would you recommend?"` — wrong: the clause `"which one would you recommend"` is a genuine second, separate REQUESTED action (an unrecognized verb in the real vocabulary, so it legitimately forms its own UNKNOWN delta) — the falsifier's own concern is only that the HYPOTHETICAL premise clause itself never forms one. Corrected to assert exactly that, narrower and more precise, not weaker.
  2. `test_out_of_scope_target_is_carried_through` initially failed because of the SIMPLIX bug above (`"Compare..."` misread as `ASSERTED`); after the root fix, it passes unmodified with its original, correct expectation.
- Producer proof: `test_a_single_requested_action_forms_one_delta`, `test_multiple_requested_actions_form_one_delta_each_none_dropped` (P-04), `test_execution_class_equals_the_real_catalogs_own_value` (×26, parametrized over the whole real catalog — P-14-style equivalence, I-20).
- Adversarial proof: `test_prohibited_action_forms_no_delta`, `test_hypothetical_premise_forms_no_delta`, `test_conditional_premise_forms_no_delta`, `test_asserted_claim_forms_no_delta` (the four non-REQUESTED modalities, each proven to form no delta); `test_unrecognized_verb_forms_an_unknown_delta_never_a_guess` (U1); `test_unresolved_target_is_carried_through_as_unknown` (U2); `test_selection_approval_decision_and_authority_effects_are_never_provider_computation` (×16, exhaustive over the real catalog's whole HUMAN_COMMAND half — P-05); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 6 guards, including the SIMPLIX fix):**
  1. Removed the `Modality.REQUESTED` filter (every action forms a delta) → 3 independent falsifiers failed (prohibited/hypothetical/asserted). Restored; byte-diff clean.
  2. Forced `execution_class = ExecutionClass.UNKNOWN` unconditionally (real catalog lookup removed) → 26 independent parametrized falsifiers failed across the whole real catalog. Restored; byte-diff clean.
  3. Forced `target = None` unconditionally → `test_out_of_scope_target_is_carried_through` failed. Restored; byte-diff clean.
  4. Hardcoded `current_state` to a literal instead of quoting the snapshot → `test_current_state_is_none_when_no_session_is_named` failed. Restored; byte-diff clean.
  5. Broke `delta_id` uniqueness (constant `"D0"`) → NOT initially caught (the falsifier's own fixture produced only one delta, so any constant id trivially satisfied uniqueness) — disclosed and corrected before re-attempting: strengthened to a genuine 3-delta fixture (mirroring R-04's and R-05's own prior disclosed near-misses, the same discipline applied a third time), then the identical mutation was correctly caught (`3 == 1` false). Restored; byte-diff clean.
  6. Reverted the SIMPLIX word-boundary fix to plain substring containment → `test_a_verb_containing_an_assertion_marker_as_a_substring_is_not_misread` failed, reproducing the exact original bug. Restored; byte-diff clean.
  Final restore hashes confirmed byte-identical to each pre-mutation baseline after every mutation (`pcpg_candidate_deltas.py`: `1b42bbdec192f7d939c02c97fb093f1948b9ecc69cc6e0739edf700d0692105e`; `pcpg_simplix.py`: `3802c7f366c89317a0d883ae7b5671fe3264f5512ef9a2cebf428d8a3d379fda`).
- **PRESERVATION / REGRESSION.** Combined PCPG suite (candidate_deltas + field_pulse + field_snapshot + simplix + operation_index + observation_ingress + isolation_sweep): **382 passed, 0 failed** (69 + 15 + 17 + 91 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN:** started only after `git status`/`git diff` confirmed the complete final tree (2 modified files — the SIMPLIX root-cause fix and its own new falsifier — and 3 new files, all this Work Unit's own); tracked-diff SHA-256 `676dc75c747e74bfb67231efdae0035a44e0be57254f6a6cfc4d95dafc32f745`, each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2294 passed, 15 skipped, 0 failed, in 2643.91s (0:44:03)** — exactly 2224 (WU-5's own closing count) + 69 (this Work Unit's own falsifiers) + 1 (the SIMPLIX regression falsifier), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
source_clause / span     <- the real SemanticAction's own clause_text/span (R-05)         -- canonical, sourced (a)
target                    <- the real SemanticAction's own target (R-05)                    -- canonical, sourced (a)
operation                 <- the real SemanticAction's own candidate_operation (R-05),       -- canonical, sourced (a)
                              itself already validated against pcpg_operation_index
execution_class           <- pcpg_operation_index.resolve_operation()'s own real value,      -- canonical, sourced (a)
                              or ExecutionClass.UNKNOWN when operation is unknown                or honest UNKNOWN
current_state              <- FieldSnapshot.session.state, the real R-03 value, or None      -- canonical, sourced (a),
                              when no Session is named                                          or honest absence
proposed_state /          <- always None / () in this increment -- disclosed, never          -- disclosed absence,
  dependency_edges            fabricated (IMPLIED-delta formation out of scope)                  never fabricated
```
No CACHED value: every field is read fresh from its own two real inputs on each call (`test_same_inputs_give_the_same_deltas_every_time` proves determinism without a cache). No DUPLICATED value: `execution_class` is read from `pcpg_operation_index` directly, never re-typed or re-classified by a second, potentially-divergent rule (proven, not assumed, by the 26-case exhaustive equivalence sweep). No PROMOTED value: `CandidateDelta` carries no RESULT, no authority fact, no capability — it is stratum-3 identity/classification only, exactly R-06's own OUTPUT shape, nothing more. No BYPASSED value: no consumer exists yet (R-07 not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-06 is materialized and closed for its own disclosed DIRECT-delta scope. Re-running E1 against this now-committed state: **R-06's remaining IMPLIED-delta scope, or R-07 (per-delta governance evaluation)**, are the two candidates for the next Work Unit. R-07's own INPUT is "each delta, the Field snapshot and the Pulse" — all three now real (R-06's direct deltas, R-03, R-04) — so R-07 is buildable NOW for the same DIRECT-delta subset this Work Unit produces, without waiting for IMPLIED-delta formation (R-07 evaluates whatever deltas R-06 hands it; an incomplete delta set from R-06 does not block R-07 from evaluating the deltas that do exist — R-06's own PRECONDITION "none is dropped" concerns REQUESTED actions, not IMPLIED ones, which are a `SUCCESSOR_NOT_BUILT`, disclosed gap, not an unmet input R-07 requires to start). Both are legitimate next Work Units; neither is a Human Authority boundary or a future Field.

## 3. Falsifier map (69 cases, `test_pcpg_candidate_deltas.py`; +1 in `test_pcpg_simplix.py`)

| Falsifier group | Cases | Proves |
|---|---|---|
| Basic formation (single/multiple actions, delta-id uniqueness) | 3 | P-04: complete, none dropped |
| Only REQUESTED modality forms a delta | 5 | R-05's own negation/hypothetical/conditional/assertion PROOF, applied literally |
| UNKNOWN operation / target | 3 | I-04: never a closest-match guess |
| Execution class equivalence (×26, exhaustive) | 27 | P-14-style equivalence; I-20: no parallel classification |
| Selection/approval/decision/authority never PROVIDER_COMPUTATION (×16, exhaustive) | 17 | P-05 |
| current_state / span traceability / purity / determinism | 6 | P-02, P-01/I-16, I-19 |
| End-to-end, real DB-backed | 1 | the whole chain (R-03 → R-05 → R-06) composes correctly against a real Session |
| `test_a_verb_containing_an_assertion_marker_as_a_substring_is_not_misread` (in `test_pcpg_simplix.py`) | 1 | the root-cause SIMPLIX fix |

## 4. Deliberate exclusions (not defects; later Work Units)

- IMPLIED intermediate deltas: no canonical "operation X requires relation/state Y, satisfied or not" index exists in this codebase. A future Work Unit that materializes it (its own completeness proof, its own adversarial fixtures against the canonical transition chain) closes this gap.
- `proposed_state`: always `None` in this increment — computing a transition's own target state requires the same canonical-chain index as IMPLIED deltas.
- `dependency_edges`: always `()` — ordering deltas by their canonical dependency requires the same index.
- R-07 through R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-06 (candidate delta formation, DIRECT deltas) is materialized for its own disclosed scope, independently falsified (69/69, plus 1 new SIMPLIX regression falsifier), mutation-proven (6/6 guards killed and restored — one guard's coverage gap was recognized and disclosed, the falsifier strengthened, then correctly caught), and proven repository-wide preservation-clean (2294 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). A genuine pre-existing bug in the already-checkpointed SIMPLIX module was found, fixed at its root, and disclosed in full. Not committed, not tagged, not pushed.
