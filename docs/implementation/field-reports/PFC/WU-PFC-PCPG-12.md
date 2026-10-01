# WU-PFC-PCPG-12 — R-11: provider-safe projection eligibility (constraints only)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-12 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary" (standing since the R-06 approval turn), under the progressive proof-cadence recorded in `WU-PFC-PCPG-8.md` §12. |
| Predecessor | `pfc-integration` `96320bcd55122a0d657588fabb91d2f40cb66bf2` (`checkpoint-PFC-PCPG-11`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure computation over real R-09 output). |
| E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-11`) | Confirmed by repository search: `grep` for `EligibleContentSet`/`derive_eligible_content`/`EligibilityResult` outside the RED text: zero hits in `packages/`. R-12 (actor-safe projection) is real; R-11 is the one ordinary relation in `02_RELATIONS.md`'s own table not yet materialized — R-13 (future SEND gate) and R-14 (reconstruction after material change) are both explicitly marked "boundary relation; not materialized" / cross-cutting by the RED text itself, never ordinary Work Units. **R-11 is the next First Broken Relation.** It is NOT a Human Authority boundary and NOT the SEND path: its own OUTPUT is explicitly "not a provider payload, it is not transmitted, and it produces no manifest." No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | The eligible content set, honestly empty today under BOTH of R-11's own FAILURE STATE clauses: an empty MLT (`MLT_EMPTY`) and — a further simplification this Work Unit's own analysis found — a hypothetical non-empty MLT (`CONTENT_NOT_CLASSIFIABLE`, since no data-class classifier producer exists anywhere, FBR-PCPG-3/GAP-11-006 still OPEN). The richer real-world content (minimum-necessary-input selection, instruction-semantics retention over an actually-classifiable MLT) has no producer and is disclosed absent. |
| Must become true | A pure function `derive_eligible_content(mlt) -> EligibleContentSet` exists: `eligible_inputs`/`retained_instruction_semantics` are `()` for both FAILURE STATE clauses, each clause distinguished by its own `reasons`/`excluded_delta_ids`. |
| Must remain true | `pcpg_chain_results.ChainResult.maximum_legitimate_transition`, `pcpg_delta_evaluation.DeltaRecord` unchanged; every existing route, Command, migration and test. |
| Must remain impossible | A non-empty `eligible_inputs` or `retained_instruction_semantics` ever produced today (P-13: nothing blocked, forbidden, secret, cross-Workspace, DC-07 or governance-internal may ever be eligible — trivially, provably true while the set is always empty). |
| Falsifiers | `tests/e2e/test_pcpg_eligible_content.py`: 8 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite was written first, importing `EligibilityResult`, `EligibleContentSet`, `derive_eligible_content`, `MLT_EMPTY`, `CONTENT_NOT_CLASSIFIABLE` from `application.pcpg_eligible_content`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_eligible_content'` — the correct reason. All 8 falsifiers passed on the first real GREEN run, a direct result of the design already being fully grounded in the relation's own FAILURE STATE text and the already-cross-checked always-empty-MLT fact before any code was written.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no eligibility producer exists for the future SEND Field (R-13) to consume
CONSUMER         the future SEND Field only (R-13, explicitly not materialized here)
PRODUCER         none (ABSENT -- break type (a))
FBR              R-11 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-11), provider-safe
                 projection eligibility
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-11; `01_INVARIANTS.md` I-17; `03_BOUNDARIES.md` B-04, B-08; WU-7/8/9/10's own already-proven, cross-checked architectural fact (the MLT is always empty today) — the load-bearing foundation this Work Unit builds on, plus the further simplification this Work Unit's own analysis found (§4).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_eligible_content.py`: `EligibilityResult`, `EligibleContentSet`, `derive_eligible_content()`, `MLT_EMPTY` (reusing `pcpg_capability.MLT_EMPTY`'s exact name for the identical real-world condition, I-20), `CONTENT_NOT_CLASSIFIABLE`. A genuine, disclosed finding: R-11's own FAILURE STATE names two separate reasons for an empty eligible set ("cannot be classified" and "an empty MLT"); since no data-class classifier exists anywhere in this codebase, the FIRST clause alone already makes the eligible set empty regardless of MLT emptiness — both clauses are honored (the `reasons` field distinguishes which applied), but the actual `eligible_inputs`/`retained_instruction_semantics` value is `()` unconditionally today.
- `tests/e2e/test_pcpg_eligible_content.py`: 8 falsifiers (§3), including a direct proof of P-13 over a 5-delta retained set, not merely the single-delta degenerate case.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_chain_results` / `pcpg_delta_evaluation` | NOT AFFECTED | Read-only consumption; no field or vocabulary changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-11 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |
| Global invariants | NOT TOUCHED | Pure, no-I/O computation; no new persistence, no schema, no session/auth change. |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Producer proof: `test_an_empty_mlt_gives_an_empty_eligible_set_with_mlt_empty_reason`, `test_a_non_empty_mlt_still_gives_an_empty_eligible_set_not_classifiable`.
- Adversarial proof: `test_mlt_empty_and_not_classifiable_are_reported_as_distinct_reasons` (the two FAILURE STATE clauses stay honestly distinguishable even though both yield the same empty result); `test_a_non_empty_mlt_excludes_every_one_of_its_own_delta_ids`; `test_p13_nothing_is_ever_eligible_regardless_of_how_many_deltas_are_retained` (P-13, proven directly over a 5-delta set, not asserted in prose); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 4 guards, local falsifier suite only):**
  1. Fabricated a non-empty `eligible_inputs` for the non-empty-MLT branch → 3 falsifiers failed. Restored.
  2. Swapped the two branches' `reasons` constants (MLT_EMPTY for the non-empty case, CONTENT_NOT_CLASSIFIABLE for the empty case) → 2 falsifiers failed. Restored.
  3. Dropped `excluded_delta_ids` for the non-empty-MLT branch to `()` → 1 falsifier failed. Restored.
  Final restore hash `eb6fb0e92ca13d5b4af59ab1a95acd066e058b97d887e2ce34013ab15d850096` confirmed byte-identical to the pre-mutation baseline after every mutation; all 8 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **398 passed, 753 deselected, 0 failed** (8 eligible_content + 13 actor_projection + 17 capability + 25 chain_results + 11 composed_effect + 26 delta_evaluation + 69 candidate_deltas + 15 field_pulse + 17 field_snapshot + 91 simplix + 78 operation_index + 28 observation_ingress); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head).
- **FULL REPOSITORY REGRESSION (final PCPG field closure).** This Work Unit closes the last ordinary PCPG relation (R-01 through R-12 are now all materialized; only R-13's future-SEND-gate boundary and R-14's cross-cutting reconstruction duty remain, both explicitly not ordinary Work Units). Per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12: "Use FULL REPOSITORY regression only at: final PCPG field closure..."), a fresh full-repository regression was run as the global preservation proof. Pre-run tree-unchanged baseline: `git status --short` showed exactly the 3 files this Work Unit itself adds (`pcpg_eligible_content.py`, `test_pcpg_eligible_content.py`, this report); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff); per-untracked-file content hashes recorded before starting. No file was modified while it ran (detached background process, watched to completion via its own PID, zero intervening edits). **Result: 2394 passed, 15 skipped, 0 failed, in 2205.01s (0:36:45)** — exactly 2331 (WU-8's own closing count) + 25 (R-09) + 17 (R-10) + 13 (R-12) + 8 (R-11, this Work Unit), confirming nothing else moved. After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
eligible_inputs /             <- () unconditionally today: an empty MLT is MLT_EMPTY        -- canonical, sourced (a);
  retained_instruction_          (R-11's own first FAILURE STATE clause); a non-empty            disclosed
  semantics                      MLT is CONTENT_NOT_CLASSIFIABLE (its second clause, since        simplification,
                                  no classifier producer exists) -- both clauses proven,           proven not assumed
                                  neither assumed
excluded_delta_ids             <- () for an empty MLT (nothing to exclude); every retained    -- canonical, sourced (a)
                                  delta's own id for a non-empty one
```
No CACHED value: every call recomputes from its own given `mlt` argument (`test_same_inputs_give_the_same_eligible_set_every_time` proves determinism without a cache). No DUPLICATED value: reads `DeltaRecord.delta_id` directly, never re-evaluating R-07/R-08/R-09 a second time. No PROMOTED value: `EligibleContentSet` is presented exactly as a derived, always-empty-today eligibility fact, never as a provider payload or a manifest (R-11's own OUTPUT text, verbatim). No BYPASSED value: no consumer exists in this Field (R-11's own DOWNSTREAM: "none in this Field"; only the future SEND Field, R-13, not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-11 is materialized and closed for its own disclosed scope. This closes every ordinary relation in `02_RELATIONS.md`'s own table: R-01 through R-12 are all now materialized (each for its own disclosed, honestly-narrowed scope — no relation claims full real-world coverage; every gap is named, not hidden). The only relations left unmaterialized are R-13 (future SEND gate — explicitly, by the RED text's own words, "not materialized" here: "a future Field, subject to HA-PCPG-1 and HA-PCPG-6") and R-14 (reconstruction after material change — a cross-cutting duty "every consumer of an observation" owes, not a Work Unit of its own with a dedicated producer file). **R-13 is the genuine Human Authority / SEND-path boundary this Field has deliberately never crossed, and does not cross here.** Re-running E1 against this now-committed state finds no further ordinary First Broken Relation to materialize. This is the natural stopping point for the BLUE materialization lane of Architecture 26 under the standing autonomous-continuation authorization: not because a Human Authority question blocks the next step, but because there is no next ordinary relation left — the next step would be R-13 itself, which is the SEND path the user has repeatedly, explicitly instructed never to begin.

## 3. Falsifier map (8 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_an_empty_mlt_gives_an_empty_eligible_set_with_mlt_empty_reason` / `test_an_empty_mlt_excludes_no_delta_ids_there_are_none` | 2 | FAILURE STATE clause 1 |
| `test_a_non_empty_mlt_still_gives_an_empty_eligible_set_not_classifiable` / `test_a_non_empty_mlt_excludes_every_one_of_its_own_delta_ids` | 2 | FAILURE STATE clause 2 |
| `test_mlt_empty_and_not_classifiable_are_reported_as_distinct_reasons` | 1 | both clauses stay honestly distinguishable |
| `test_p13_nothing_is_ever_eligible_regardless_of_how_many_deltas_are_retained` | 1 | P-13, directly |
| `test_same_inputs_give_the_same_eligible_set_every_time` | 1 | determinism |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static |

## 4. Deliberate exclusions (not defects; a future Field, if HA-PCPG-1 is ever resolved)

- The real content of a genuinely non-empty, classifiable MLT (minimum-necessary-input selection, instruction-semantics retention): no data-class classifier producer exists anywhere in this codebase (FBR-PCPG-3/GAP-11-006, still OPEN). Building it now would be materializing FBR-PCPG-3's own still-OPEN scope under this Work Unit.
- R-13 (future SEND gate): explicitly not materialized by the RED text itself; the genuine, never-crossed Human Authority / SEND-path boundary.
- R-14 (reconstruction after material change): cross-cutting, not an ordinary Work Unit with its own producer file.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-11 (provider-safe projection eligibility, honestly empty today under both of its own FAILURE STATE clauses) is materialized for its own disclosed scope, independently falsified (8/8), mutation-proven (3/3 guards killed and restored, byte-identical after restore), proven affected-suite-clean (398 passed / 0 failed, full combined PCPG suite), and proven repository-wide preservation-clean as the final PCPG field closure proof (2394 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). This closes every ordinary relation in Architecture 26's `02_RELATIONS.md`: R-01 through R-12 are now all materialized, each for its own disclosed scope. The only remaining relations (R-13, R-14) are explicitly not ordinary Work Units; R-13 is the genuine, never-crossed SEND-path boundary. **This is the natural stopping point for autonomous continuation**, not a Human Authority block but the honest absence of any further ordinary relation to materialize.
