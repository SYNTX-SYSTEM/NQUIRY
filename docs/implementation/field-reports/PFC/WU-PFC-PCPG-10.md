# WU-PFC-PCPG-10 — R-10: current capability (stratum 4)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-10 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary" (standing since the R-06 approval turn), under the progressive proof-cadence recorded in `WU-PFC-PCPG-8.md` §12. |
| Predecessor | `pfc-integration` `3b8b0f9f0202c4f4d4bc9ba92b402bc19068438a` (`checkpoint-PFC-PCPG-9`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure computation over real R-04/R-08/R-09 output plus the already-real `ProviderContext`/`AI_CONTRACTS_ADMITTED`). |
| E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-9`) | Confirmed by repository search: `grep` for `GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND`/`derive_capability` outside the RED text itself: zero hits in `packages/`. R-09 (chain results) is real and has no consumer yet. R-10's own PRECONDITION ("R-09 is complete") is satisfied, and it is the sole named CONSUMER of R-09 with no further open precondition (R-11 additionally requires a non-empty MLT, vacuously never true today; R-12 additionally requires R-10 complete). **R-10 is the next First Broken Relation.** No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | `GOVERNANCE_ADMISSIBLE` covers bullets 1 (MLT non-empty, from R-09), 2 (composition COMPOSABLE, from R-08) and 4 (admitted operation class, via a small closed/grepped operation→contract table); bullets 3 (INDETERMINATE-dependency/input-sharing) and 5 (data-class route eligibility) have no producer and are disclosed absent. `PROVIDER_EXECUTABLE` reuses `04_OBSERVATION_RESULT.md` §8's own already-published, cited, unconditional value (`NO_ELIGIBLE_PROVIDER_ROUTE` — no provider-route producer exists anywhere in this codebase), plus the one real, additionally-checkable `NO_ENVIRONMENT_DECLARED` reason from `ProviderContext.environment`. `CAN_SEND` is the plain boolean AND. |
| Must become true | A pure function `derive_capability(chain_result, composed_effect, pulse, admitted_operation_classes, provider) -> Capability` exists, covering the above exactly. |
| Must remain true | `pcpg_chain_results.ChainResult`, `pcpg_composed_effect.ComposedEffect`, `pcpg_field_snapshot.ProviderContext`/`AI_CONTRACTS_ADMITTED`, `pcpg_field_pulse.Pulse` unchanged; every existing route, Command, migration and test. |
| Must remain impossible | `GOVERNANCE_ADMISSIBLE` ever reported `True` without every checked bullet genuinely holding; `PROVIDER_EXECUTABLE` ever reported `True` (no route producer exists at all, so the Field has no "unknown = true" state — FAILURE STATE, verbatim); `CAN_SEND` true without both operands independently true. |
| Falsifiers | `tests/e2e/test_pcpg_capability.py`: 17 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite was written first, importing `Capability`, `derive_capability`, and the reason constants from `application.pcpg_capability`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_capability'` — the correct reason. On the first real GREEN run, **2 of the originally-authored falsifiers failed** — a genuine test-authoring mistake, not a module defect, disclosed in full below (§2a).

**2a GENUINE TEST-AUTHORING GAP, FOUND AND CORRECTED BEFORE MUTATION PROOF.** The original `test_governance_admissible_is_true_when_every_checked_bullet_holds` assumed a hand-built `ALLOWED` `PROVIDER_COMPUTATION` delta would make `GOVERNANCE_ADMISSIBLE` true. It never can: `pcpg_composed_effect.compose_effect` (R-08, already checkpointed) returns `COMPOSABLE` only for an **empty** retained set and `INDETERMINATE` for **any non-empty** one (its own disclosed, already-proven design — the real composition sub-checks have no producer). Since bullet 1 needs a non-empty MLT and bullet 2 needs `COMPOSABLE`, and `compose_effect` makes those two conditions mutually exclusive by construction, `GOVERNANCE_ADMISSIBLE` can **never** be true in this Field as currently composed — not merely "for every real observation today" (WU-7/8/9's narrower claim about the MLT always being empty), but logically, even with a hand-built hypothetical record. This is a genuine, disclosed, further architectural fact this Work Unit's own testing found, not a defect in R-08 (whose own WU report fully justifies its design) and not something this Work Unit changes. The two mis-conceived tests were replaced with `test_governance_admissible_can_never_be_true_bullets_one_two_mutually_exclusive` (proving the fact directly, for both the empty and the hypothetical non-empty case) and `test_can_send_is_false_in_the_hypothetical_mlt_non_empty_case_too`. All 17 falsifiers passed after the correction.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no capability producer exists for R-11 (provider-safe projection eligibility)
                 or R-12 (actor-safe projection) to consume
CONSUMER         (future) R-12; later R-13 (re-derives, never consumes as authority, I-14) --
                 not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-10 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-10), current capability
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-10; `04_OBSERVATION_RESULT.md` §8 (capability, verbatim, including the already-published "Current NQUIRY values" paragraph this increment reuses directly for `PROVIDER_EXECUTABLE`); `pcpg_operation_index.py`'s own closed FBR-PCPG-2 catalog (the operation→contract correspondence); WU-PFC-PCPG-7/8/9's own already-proven facts — the load-bearing foundation this Work Unit builds on, plus the further mutual-exclusivity fact this Work Unit's own testing found (§2a).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_capability.py`: `Capability`, `derive_capability()`, and the reason constants `MLT_EMPTY`, `OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA`, `NO_ELIGIBLE_PROVIDER_ROUTE` (cited verbatim from §8), `NO_ENVIRONMENT_DECLARED`. A small, closed, grepped `_PROVIDER_COMPUTATION_CONTRACTS` table (`REQUEST_QUESTION_ANALYSIS`→`AIOP-001`, `REQUEST_QUESTION_CLUSTERING`→`AIOP-002`) sourced directly from `pcpg_operation_index.py`'s own cited `architecture_ref` strings, not invented.
- `tests/e2e/test_pcpg_capability.py`: 17 falsifiers (§3).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_chain_results` / `pcpg_composed_effect` / `pcpg_field_pulse` / `pcpg_field_snapshot` / `pcpg_operation_index` | NOT AFFECTED | Read-only consumption; no field or vocabulary changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-10 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |
| Global invariants (migration, shared persistence, session/auth substrate, authority/capability resolution, cross-field protocol/serialization, repository-wide import/runtime behavior) | NOT TOUCHED | Pure, no-I/O computation over already-real dataclasses; no new persistence, no schema, no session/auth change — full-repository regression is therefore not required at this proof radius (`WU-PFC-PCPG-8.md` §12). |

**6–9 PROOFS** (progressive cadence: LOCAL → AFFECTED, no full-repository regression — the delta touches no global invariant per the PROPAGATION table above).
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Producer proof: `test_an_empty_mlt_makes_governance_admissible_false_with_mlt_empty`, `test_a_retained_delta_mapping_to_an_admitted_contract_passes_bullet_four`, `test_provider_executable_is_unconditionally_false_with_the_cited_reason`.
- Adversarial proof: `test_governance_admissible_can_never_be_true_bullets_one_two_mutually_exclusive` (the mutual-exclusivity fact, proven directly, §2a); `test_a_retained_delta_with_an_unmapped_operation_fails_bullet_four` (a hypothetical operation outside the closed contract table is never silently waved through); `test_governance_admissible_reasons_contain_only_whats_actually_wrong` (the reasons set never fabricates a bullet-4 failure that did not occur); `test_an_undeclared_environment_adds_its_own_honest_reason`; `test_a_governance_blocking_pulse_does_not_change_the_capability` (the disclosed Pulse non-consumption, proven by direct comparison); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 5 guards, local falsifier suite only):**
  1. Neutralized the MLT-emptiness check (`if False and not mlt`) → 4 falsifiers failed. Restored.
  2. Neutralized the bullet-4 admitted-operation-class check → 2 falsifiers failed. Restored.
  3. Hardcoded `PROVIDER_EXECUTABLE` to `True` → 4 falsifiers failed. Restored.
  4. Neutralized the `NO_ENVIRONMENT_DECLARED` check → 1 falsifier failed. Restored.
  5. Hardcoded `CAN_SEND` to `True` → 2 falsifiers failed. Restored.
  Final restore hash `754e29399c6c5f0c59079e53be06b1b4b2939cbc361103c56fb3db828801e52a` confirmed byte-identical to the pre-mutation baseline after every mutation; all 17 local falsifiers green on the restored file.
  **Disclosed mutation-proof limitation (not hidden):** a mutation changing the `CAN_SEND = GOVERNANCE_ADMISSIBLE ∧ PROVIDER_EXECUTABLE` combinator from AND to OR is **not** observable by any honest, real-shaped test fixture today, because `PROVIDER_EXECUTABLE` is an unconditional `False` constant and `GOVERNANCE_ADMISSIBLE` can never be `True` (§2a) — both operands read `False` under every combinator. This is not a coverage gap to paper over with a fabricated input (there is no honest way to force either operand `True` without inventing a producer this codebase does not have); mutation 5 instead targets `can_send`'s own hardcoded-constant failure mode, which the real falsifiers do catch. Recorded directly in the module's own docstring.
- **AFFECTED SUITES.** Combined PCPG suite (capability + chain_results + composed_effect + delta_evaluation + candidate_deltas + field_pulse + field_snapshot + simplix + operation_index): **349 passed, 0 failed** (17 + 25 + 11 + 26 + 69 + 15 + 17 + 91 + 78); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed for this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a pure, no-I/O application module with no new persistence, no schema change, no session/authority/capability-resolution touch, and no cross-field protocol change — none of the enumerated full-regression triggers apply.

**10 INVERSE SWEEP (E6).**
```text
governance_admissible <- bullets 1/2/4, each from a real, already-produced value         -- canonical, sourced (a);
  (+ reasons)              (R-09's MLT, R-08's composition_result/reason, a closed/            bullets 3/5 disclosed
                            grepped operation->contract table checked against the real         absent, never assumed
                            AI_CONTRACTS_ADMITTED); bullets 3/5 never checked, never            true
                            assumed true
provider_executable    <- the already-published, cited `NO_ELIGIBLE_PROVIDER_ROUTE`       -- versioned SFE rule (c),
  (+ reasons)              fact (04_OBSERVATION_RESULT.md §8), unconditional (no route          static, cited
                           producer exists); `NO_ENVIRONMENT_DECLARED` real and additional
can_send               <- the plain boolean AND of the two values above                   -- canonical, sourced (a)
```
No CACHED value: every call recomputes from its own real input (`test_same_inputs_give_the_same_capability_every_time` proves determinism without a cache). No DUPLICATED value: `governance_admissible` reads `ChainResult.maximum_legitimate_transition`/`ComposedEffect.composition_result` directly, never re-evaluating R-08/R-09 a second time. No PROMOTED value: `Capability` is presented exactly as a derived stratum-4 projection, never as authority or an executed grant (I-14 — `CAN_SEND` is a projection, not a SEND). No BYPASSED value: no consumer exists yet (R-11/R-12 not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-10 is materialized and closed for its own disclosed scope. Re-running E1 against this now-committed state (to be re-derived fresh, not assumed here): R-11 (provider-safe projection eligibility) and R-12 (actor-safe projection → CYAN) both now have their stated PRECONDITIONs nominally reachable ("R-09 and R-10 are complete" / "R-10 is complete"), but R-11's own PRECONDITION additionally states "it exists only if the MLT is non-empty" — vacuously never true today (WU-7/8/9/10's own cross-checked fact) — so R-11 has no real work to materialize yet, only a (trivial, always-empty-input) producer to write, which is a materialization choice for the next Work Unit's own fresh E1 to weigh against R-12 (which has no such precondition gate and is this Field's final stated relation before the future R-13 SEND-gate boundary). Not a selection, not a Human Authority boundary, not a future Field.

## 3. Falsifier map (17 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_an_empty_mlt_makes_governance_admissible_false_with_mlt_empty` / `test_todays_real_field_has_no_delta_ever_resolve_allowed_so_mlt_is_always_empty` | 2 | bullet 1 |
| `test_a_composable_empty_mlt_still_fails_on_mlt_empty_alone` / `test_a_non_composable_composition_result_is_reported_by_its_own_real_reason` | 2 | bullet 2 |
| `test_a_retained_delta_mapping_to_an_admitted_contract_passes_bullet_four` / `test_a_retained_delta_mapping_to_a_contract_outside_admitted_fails_bullet_four` / `test_a_retained_delta_with_an_unmapped_operation_fails_bullet_four` | 3 | bullet 4, both sides |
| `test_governance_admissible_can_never_be_true_bullets_one_two_mutually_exclusive` | 1 | the further mutual-exclusivity fact (§2a) |
| `test_governance_admissible_reasons_contain_only_whats_actually_wrong` | 1 | reasons set honesty |
| `test_provider_executable_is_unconditionally_false_with_the_cited_reason` / `test_provider_executable_stays_false_even_with_a_declared_environment` / `test_an_undeclared_environment_adds_its_own_honest_reason` | 3 | PROVIDER_EXECUTABLE, both sides |
| `test_can_send_is_false_whenever_governance_admissible_is_false` / `test_can_send_is_false_in_the_hypothetical_mlt_non_empty_case_too` | 2 | CAN_SEND |
| `test_a_governance_blocking_pulse_does_not_change_the_capability` | 1 | disclosed Pulse non-consumption |
| `test_same_inputs_give_the_same_capability_every_time` | 1 | determinism |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static |

## 4. Deliberate exclusions (not defects; later Work Units)

- GOVERNANCE_ADMISSIBLE bullets 3 ("no INDETERMINATE delta is a dependency of, or shares inputs with, a retained delta") and 5 ("the composed data classes are eligible for at least one route class"): no per-delta input/data-sharing producer and no data-class classifier (FBR-PCPG-3/GAP-11-006, still OPEN) exist anywhere in this codebase.
- PROVIDER_EXECUTABLE's own richer bullets (an eligible configured route per operation contract and composed data classes; not MockProvider on a real scope, HD-19; not MockProvider on PRODUCTION, HD-LIVE-1): no per-operation provider-route-table or provider-identity producer exists; the provider-SDK-import-check gate unconditionally forbids a provider import in this application layer.
- `basis_identity` as a separate structured output field: §9's own "basis" is a cross-cutting re-derivation discipline (derive on read, never cache), already honored by this module's own purity, not a new field this relation computes.
- R-11 and R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-10 (current capability: GOVERNANCE_ADMISSIBLE bullets 1/2/4, PROVIDER_EXECUTABLE via the already-cited §8 value, CAN_SEND) is materialized for its own disclosed scope, independently falsified (17/17, after correcting a genuine test-authoring gap found and disclosed in §2a before any mutation proof), mutation-proven (5/5 guards killed and restored, byte-identical after restore, with one honestly-disclosed combinator-mutation limitation), and proven affected-suite-clean (349 passed / 0 failed, combined PCPG suite). No full-repository regression was run for this Work Unit, per the Human Authority proof-cadence decision recorded in `WU-PFC-PCPG-8.md` §12: this delta touches no global invariant.
