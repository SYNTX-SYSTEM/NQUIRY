# WU-PFC-PCPG-9 — R-09: chain results (FBR, MLT, NVT, HAR, PARTIAL)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-9 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary" (standing since the R-06 approval turn), now executed under the **new proof-cadence** the Human Authority decision recorded in `WU-PFC-PCPG-8.md` §12: local falsifiers → local mutation proof → affected suites, no full-repository regression unless a global invariant is genuinely touched. |
| Predecessor | `pfc-integration` `1d6d41bda47bd34fafc34bea72795741b7edf348` (`checkpoint-PFC-PCPG-8`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure computation over real R-06/R-07/R-08/R-04 output). |
| E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-8`) | Confirmed by repository search: `grep` for `FIRST_BROKEN_RELATION`/`FirstBrokenRelation`/`ChainResult`/`derive_chain_result`: zero hits outside this Work Unit's own new files — R-09 genuinely absent. `02_RELATIONS.md`'s own header diagram and R-07/R-08's own `CONSUMER` lines both name R-09 as the sole unmaterialized direct successor. R-09's own INPUT ("the delta records, their dependency order, the composition result and the Pulse") is satisfied now: R-06's deltas, R-07's records, R-08's `ComposedEffect`, R-04's `Pulse` are all real. **R-09 is the next First Broken Relation.** No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | `FIRST_BROKEN_RELATION` and `MAXIMUM_LEGITIMATE_TRANSITION` fully, against §7.2/§7.3's own definitions. `NEXT_VALID_TRANSITION` covers only §7.4 rule 1 (the first `HUMAN_ACTION_AVAILABLE` record at or before the FBR); rule 2 (a canonical-chain-to-product-transition lookup) has no producer and is disclosed, not guessed. `HUMAN_AUTHORITY_REQUIRED` covers only `AUTHORITY_BOUNDARY` and `GOVERNANCE_BOUNDARY` records (the two RESULT classes this Field can already answer honestly); the real reason code/HA-* citation is surfaced rather than invented holder-class prose beyond the two literal examples the RED text itself gives. `PARTIAL` fully, against §7.6. `Pulse` is accepted as a parameter (R-09's own declared INPUT) but not consumed by any branch: no producer translates a bare `Pulse.governance_blockers` entry into a delta-shaped FBR/HAR entry, matching R-07's own already-disclosed non-consumption of Pulse. |
| Must become true | A pure function `derive_chain_result(records, composed_effect, pulse) -> ChainResult` exists, covering FBR/MLT/NVT(rule 1)/HAR(disclosed subset)/PARTIAL exactly as defined above. |
| Must remain true | `pcpg_delta_evaluation.Result`/`DeltaRecord`, `pcpg_composed_effect.ComposedEffect`, `pcpg_field_pulse.Pulse` unchanged; every existing route, Command, migration and test. |
| Must remain impossible | A record strictly after the FBR ever selected as NVT; a `STATE_BOUNDARY`/`DATA_BOUNDARY`/`DENIED`/`INDETERMINATE` record ever fabricating a HAR entry it cannot honestly answer; PARTIAL computed from anything other than the real retained-vs-requested comparison; a later broken record ever reported as the FBR ahead of an earlier one. |
| Falsifiers | `tests/e2e/test_pcpg_chain_results.py`: 25 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (25 cases) was written first, importing `AuthorityRequirement`, `FirstBrokenRelation`, `derive_chain_result`, `GOVERNANCE_QUESTION_HA_PCPG_1` from `application.pcpg_chain_results`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_chain_results'` — the correct reason. All 25 falsifiers passed on the first real GREEN run: the design was fully grounded in R-06/R-07/R-08's own already-proven facts (dependency order coincides with tuple order; `ALLOWED` is never emitted for a `HUMAN_COMMAND` delta; the retained set is always empty today) before any code was written.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no chain-result producer exists for R-10 (current capability), R-11
                 (provider-safe projection eligibility) or R-12 (actor-safe projection)
                 to consume
CONSUMER         (future) R-10, R-11, R-12 -- not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-09 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-09), chain results
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-09; `04_OBSERVATION_RESULT.md` §7.2–§7.6 (FBR/MLT/NVT/HAR/PARTIAL, verbatim); `00_FIELD.md` §13 (HA-PCPG-1, the cited open Human Authority question); WU-PFC-PCPG-6/7/8's own already-proven facts (dependency order, the always-empty retained set, the unconditional `GOVERNANCE_BOUNDARY`) — the load-bearing foundation this Work Unit builds on rather than re-derives.

**4 REPAIR** (2 new files).
- `packages/application/pcpg_chain_results.py`: `FirstBrokenRelation`, `AuthorityRequirement`, `ChainResult`, `derive_chain_result()`, `GOVERNANCE_QUESTION_HA_PCPG_1`. FBR is the first record whose `result` is not in `{ALLOWED, HUMAN_ACTION_AVAILABLE}`, with a by-construction-legitimate predecessor. MLT is `composed_effect.retained` verbatim (HUMAN_COMMAND exclusion holds by construction, not by a second filter). NVT is the first `HUMAN_ACTION_AVAILABLE` record in `records[:broken_index+1]` (or the whole list when there is no FBR). HAR is produced only for `AUTHORITY_BOUNDARY`/`GOVERNANCE_BOUNDARY` records. PARTIAL is `len(retained) < len(records)`.
- `tests/e2e/test_pcpg_chain_results.py`: 25 falsifiers (§3).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_delta_evaluation` / `pcpg_composed_effect` / `pcpg_field_pulse` | NOT AFFECTED | Read-only consumption; no field or vocabulary changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-09 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |
| Global invariants (migration, shared persistence, session/auth substrate, authority/capability resolution, cross-field protocol/serialization, repository-wide import/runtime behavior) | NOT TOUCHED | Pure, no-I/O computation over already-real dataclasses; no new persistence, no schema, no session/auth change — full-repository regression is therefore not required at this proof radius (Human Authority proof-cadence decision, `WU-PFC-PCPG-8.md` §12). |

**6–9 PROOFS** (new cadence: LOCAL → AFFECTED, no full-repository regression — the delta touches no global invariant per the PROPAGATION table above).
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Producer proof: `test_the_first_non_legitimate_record_is_the_broken_one_with_no_predecessor`, `test_mlt_is_exactly_the_composed_effects_retained_set`, `test_har_covers_an_authority_boundary_delta_with_its_own_real_reason_code`, `test_partial_is_true_when_any_requested_delta_is_outside_the_retained_set`.
- Adversarial proof: `test_only_the_first_broken_record_is_reported_never_a_later_one` (a second, independently-broken record must never surface ahead of the first); `test_mlt_never_contains_a_human_command_delta_even_though_it_is_a_positive_result` (I-08/§7.3, proven against a positive-but-wrong-class result); `test_nvt_a_record_strictly_after_the_fbr_is_never_selected`; `test_har_never_covers_a_state_boundary_delta` / `test_har_never_covers_an_indeterminate_delta` / `test_har_never_covers_a_human_action_available_delta` (the disclosed-subset boundary, proven on both sides); `test_a_governance_blocking_pulse_does_not_change_the_chain_result` (the disclosed Pulse non-consumption, proven by direct comparison, not merely asserted in prose); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 5 guards, local falsifier suite only):**
  1. Neutralized the FBR-detection condition (`if False and ...`) → 4 falsifiers failed (`test_the_first_non_legitimate_record_is_the_broken_one_with_no_predecessor`, `test_the_broken_records_predecessor_is_the_immediately_preceding_legitimate_record`, `test_only_the_first_broken_record_is_reported_never_a_later_one`, `test_nvt_a_record_strictly_after_the_fbr_is_never_selected`). Restored.
  2. Hardcoded MLT to `()` → `test_mlt_retains_a_hand_built_allowed_provider_computation_delta` failed. Restored.
  3. Widened `_AUTHORITY_ANSWERABLE_RESULTS` to also include `STATE_BOUNDARY` → `test_har_never_covers_a_state_boundary_delta` failed. Restored.
  4. Hardcoded PARTIAL to `False` → `test_partial_is_true_when_any_requested_delta_is_outside_the_retained_set` failed. Restored.
  5. Removed the NVT search-range ceiling (searched the whole list regardless of the FBR) → `test_nvt_a_record_strictly_after_the_fbr_is_never_selected` failed. Restored.
  Final restore hash `772511af97e01cb6f60a87d2595c5e9641178eb1a139e85d8a86e40b36a1debb` confirmed byte-identical to the pre-mutation baseline after every mutation; all 25 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Combined PCPG suite (chain_results + composed_effect + delta_evaluation + candidate_deltas + field_pulse + field_snapshot + simplix + operation_index): **332 passed, 0 failed** (25 + 11 + 26 + 69 + 15 + 17 + 91 + 78) — exactly 307 (WU-8's own combined-PCPG count minus the isolation/ingress suites not touched by this delta) + 25 (this Work Unit's own falsifiers); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed for this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a pure, no-I/O application module with no new persistence, no schema change, no session/authority/capability-resolution touch, and no cross-field protocol change — none of the enumerated full-regression triggers apply.

**10 INVERSE SWEEP (E6).**
```text
first_broken_relation <- the first DeltaRecord in the given order whose result is not     -- canonical, sourced (a)
                          in {ALLOWED, HUMAN_ACTION_AVAILABLE}; predecessor is the             producer; dependency
                          immediately preceding record (legitimate by construction)            order == given order,
                                                                                                vacuously true (R-06)
maximum_legitimate_    <- composed_effect.retained, unmodified                             -- canonical, sourced (a)
  transition
next_valid_transition <- the first HUMAN_ACTION_AVAILABLE record at or before the FBR;     -- versioned SFE rule (c);
                          rule 2 (product-transition lookup) disclosed absent, not             rule 2 disclosed
                          guessed                                                              absence, never
                                                                                                fabricated
human_authority_       <- the delta's own real (result, reason), for AUTHORITY_BOUNDARY    -- canonical, sourced (a);
  required                 and GOVERNANCE_BOUNDARY only; the cited open HA-PCPG-1             disclosed narrower
                          question for GOVERNANCE_BOUNDARY; no entry for the other four        subset, never
                          RESULT classes                                                       fabricated
partial                <- len(retained) < len(records), the real §7.6 definition           -- canonical, sourced (a)
```
No CACHED value: every call recomputes from its own real input (`test_same_inputs_give_the_same_chain_result_every_time` proves determinism without a cache). No DUPLICATED value: FBR/MLT/HAR all read `DeltaRecord.result`/`ComposedEffect.retained` directly, never re-evaluating governance a second time. No PROMOTED value: `ChainResult` is presented exactly as a derived chain fact, never as authority or a capability grant. No BYPASSED value: no consumer exists yet (R-10/R-11/R-12 not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-09 is materialized and closed for its own disclosed scope. Re-running E1 against this now-committed state (to be re-derived fresh, not assumed here, per the same discipline as every prior transition): R-10 (current capability, stratum 4) becomes the candidate next relation, since its own PRECONDITION ("R-09 is complete") is now satisfied and it is the sole named CONSUMER of R-09 that has no INDIRECT precondition still open (R-11 additionally requires "it exists only if the MLT is non-empty" — vacuously never today, given the always-empty MLT — so R-11 has no real work to materialize yet; R-12 additionally requires "R-10 is complete" first). This is a candidate, not a selection: it must be re-derived fresh against the published checkpoint, not assumed from this note. Not a Human Authority boundary, not a future Field.

## 3. Falsifier map (25 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_no_records_gives_no_broken_relation` / `test_all_legitimate_records_give_no_broken_relation` | 2 | the empty-case rule (§7.2) |
| `test_the_first_non_legitimate_record_is_the_broken_one_with_no_predecessor` / `test_the_broken_records_predecessor_is_the_immediately_preceding_legitimate_record` | 2 | FBR form and predecessor |
| `test_only_the_first_broken_record_is_reported_never_a_later_one` | 1 | "first" is enforced, not just "a" |
| `test_mlt_is_exactly_the_composed_effects_retained_set` | 1 | MLT passthrough |
| `test_mlt_never_contains_a_human_command_delta_even_though_it_is_a_positive_result` | 1 | I-08/§7.3, by construction |
| `test_mlt_retains_a_hand_built_allowed_provider_computation_delta` | 1 | the filter itself, independent of today's degenerate instance |
| `test_nvt_is_the_first_human_action_available_record_at_or_before_the_fbr` / `test_nvt_is_none_when_no_human_action_available_record_precedes_the_fbr` / `test_nvt_searches_the_whole_list_when_there_is_no_broken_relation` / `test_nvt_a_record_strictly_after_the_fbr_is_never_selected` | 4 | §7.4 rule 1, both sides |
| `test_har_covers_an_authority_boundary_delta_with_its_own_real_reason_code` / `test_har_covers_a_governance_boundary_delta_with_the_cited_open_ha_question` | 2 | the disclosed HAR subset |
| `test_har_never_covers_a_state_boundary_delta` / `test_har_never_covers_an_indeterminate_delta` / `test_har_never_covers_a_human_action_available_delta` | 3 | the disclosed HAR boundary |
| `test_har_lists_every_qualifying_delta_in_order_not_only_the_first` | 1 | HAR is exhaustive, not first-match |
| `test_partial_is_false_when_there_are_no_requested_deltas_at_all` / `test_partial_is_true_when_any_requested_delta_is_outside_the_retained_set` / `test_partial_is_false_when_the_retained_set_equals_the_full_requested_set` | 3 | §7.6, both sides |
| `test_a_governance_blocking_pulse_does_not_change_the_chain_result` | 1 | disclosed Pulse non-consumption |
| `test_same_inputs_give_the_same_chain_result_every_time` | 1 | determinism |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static |
| `test_composition_result_import_is_not_unused` | 1 | import hygiene |

## 4. Deliberate exclusions (not defects; later Work Units)

- NVT rule 2 ("the product transition ... that the FBR depends on"): needs a canonical-chain-to-product-transition lookup that has no producer anywhere in this codebase.
- HAR for `STATE_BOUNDARY`/`DATA_BOUNDARY`/`DENIED`/`INDETERMINATE`: a state-legality wall or an unresolved/unknown delta names no authority holder; `DATA_BOUNDARY`/`DENIED` are never emitted by R-07 today regardless.
- HAR's full RED-described shape ("the SESSION_CONTROL_RIGHT holder of this Session", "the QUESTION_SELECTION_RIGHT holder who selected the current primary") for all six real `AUTHORITY_BOUNDARY` reason codes: requires a binding-holder-identity lookup this module does not perform; the real reason code is surfaced instead.
- Cycle detection for an undeterminable dependency order (§7.2 FAILURE STATE): cannot occur today given R-06's own disclosed `dependency_edges == ()`; no producer built for a case with no real input data to exercise it.
- R-10 through R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-09 (chain results: FBR/MLT/NVT(rule 1)/HAR(disclosed subset)/PARTIAL) is materialized for its own disclosed scope, independently falsified (25/25), mutation-proven (5/5 guards killed and restored, byte-identical after restore), and proven affected-suite-clean (332 passed / 0 failed, combined PCPG suite). No full-repository regression was run for this Work Unit, per the Human Authority proof-cadence decision recorded in `WU-PFC-PCPG-8.md` §12: this delta touches no global invariant.
