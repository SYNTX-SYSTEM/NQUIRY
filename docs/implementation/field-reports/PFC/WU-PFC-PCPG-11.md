# WU-PFC-PCPG-11 — R-12: actor-safe projection → CYAN

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-11 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary" (standing since the R-06 approval turn), under the progressive proof-cadence recorded in `WU-PFC-PCPG-8.md` §12. |
| Predecessor | `pfc-integration` `3420c93b49bb8295055952a871240336f33b56f5` (`checkpoint-PFC-PCPG-10`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure re-packaging of real R-01/R-05/R-07/R-09/R-10 output). |
| E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-10`) | Confirmed by repository search: `grep` for `ActorSafeProjection`/`derive_actor_safe_projection`: zero hits outside the RED text. R-10 (capability) is real and has no consumer yet; its own DOWNSTREAM names only R-12 (R-13 "must not consume it as authority"). R-11's own PRECONDITION additionally requires "it exists only if the MLT is non-empty" — vacuously never true today (WU-7 through WU-10's own cross-checked fact) — so R-11 has no real work beyond a trivial always-empty-input producer. R-12 is named CONSUMER by both R-09 and R-10 (R-11 by R-09 alone) — the same evidence-based tie-break this field already used once before (R-04 over R-06, WU-PFC-PCPG-4). **R-12 is the next First Broken Relation.** No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | 5 of R-12's 7 named OUTPUT items, each a direct re-packaging of an already-real producer: the actor's own raw intent + its fingerprint (R-01's `ObservationIngressResult.raw_intent`/`.raw_intent_digest_sha256`); the semantic observation (R-05's `SemanticObservation`); the delta results with reason codes (R-07's `DeltaRecord` tuple); FBR/MLT/NVT/HAR as holder classes (R-09's `ChainResult`, already holder-class-safe by construction); the capability values with reasons (R-10's `Capability`). "The proof ceiling" (no producer anywhere, R-07's own already-disclosed gap) and the richer "basis identity" composite beyond the fingerprint/derivation-time pair are disclosed absent. |
| Must become true | A pure function `derive_actor_safe_projection(ingress, semantic_observation, delta_records, chain_result, capability) -> ActorSafeProjection` exists, re-packaging exactly the 5 covered items verbatim. |
| Must remain true | `pcpg_observation.ObservationIngressResult`, `pcpg_simplix.SemanticObservation`, `pcpg_delta_evaluation.DeltaRecord`, `pcpg_chain_results.ChainResult`, `pcpg_capability.Capability` unchanged; every existing route, Command, migration and test. |
| Must remain impossible | Any field appearing in `ActorSafeProjection` that is not one of the 5 covered real OUTPUT items (no fabrication); any other actor's binding internals leaking through FBR/MLT/NVT/HAR (I-17). |
| Falsifiers | `tests/e2e/test_pcpg_actor_projection.py`: 13 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite was written first, importing `ActorSafeProjection`, `derive_actor_safe_projection` from `application.pcpg_actor_projection`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_actor_projection'` — the correct reason. All 13 falsifiers passed on the first real GREEN run (after one Python-3.10-compatibility fix to the test fixture itself: `datetime.UTC` is 3.11+; this environment runs 3.10.12, so `timezone.utc` was used instead — a fixture-construction detail, not a module defect, corrected before any assertion ran).

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no actor-safe projection exists for CYAN to consume; every PCPG relation's
                 output remains backend-internal
CONSUMER         CYAN (display only) -- not materialized here (no frontend/HTTP wiring in
                 this Work Unit, matching every prior relation's own disclosed scope)
PRODUCER         none (ABSENT -- break type (a))
FBR              R-12 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-12), actor-safe projection
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-12; `04_OBSERVATION_RESULT.md` §10 (actor-safe projection, verbatim); `01_INVARIANTS.md` I-17 (no other actor's binding internals); `pcpg_observation.py`'s own already-real fingerprint producer (built explicitly "so a future Work Unit can reuse it", now reused here for the first time).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_actor_projection.py`: `ActorSafeProjection`, `derive_actor_safe_projection()` — a pure re-packaging function with no new governance logic, consuming exactly five already-real producers' output.
- `tests/e2e/test_pcpg_actor_projection.py`: 13 falsifiers (§3), including a static, by-construction proof that no dataclass in the pipeline (`DeltaRecord`, `FirstBrokenRelation`, `AuthorityRequirement`, `ChainResult`, `Capability`) carries another actor's binding reference.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_observation` / `pcpg_simplix` / `pcpg_delta_evaluation` / `pcpg_chain_results` / `pcpg_capability` | NOT AFFECTED | Read-only consumption; no field or vocabulary changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-12 has no HTTP surface in this Work Unit (same as every PCPG relation since R-03). |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |
| Global invariants (migration, shared persistence, session/auth substrate, authority/capability resolution, cross-field protocol/serialization, repository-wide import/runtime behavior) | NOT TOUCHED | Pure, no-I/O re-packaging of already-real dataclasses; no new persistence, no schema, no session/auth change — full-repository regression is therefore not required at this proof radius (`WU-PFC-PCPG-8.md` §12). |

**6–9 PROOFS** (progressive cadence: LOCAL → AFFECTED, no full-repository regression — the delta touches no global invariant per the PROPAGATION table above).
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Producer proof: `test_raw_intent_is_carried_through_verbatim`, `test_semantic_observation_is_carried_through_verbatim`, `test_delta_records_are_carried_through_verbatim`, `test_chain_result_is_carried_through_verbatim`, `test_capability_is_carried_through_verbatim`.
- Adversarial proof: `test_projection_adds_no_field_beyond_the_seven_named_items` (no fabrication, mirrors the E6 FABRICATED check structurally); `test_no_field_in_the_projection_carries_another_actors_identity` + `test_authority_requirement_carries_only_delta_id_result_and_reason` (I-17, proven directly against the real dataclass shapes); `test_two_different_observations_project_independently_no_shared_mutable_state`; `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 4 guards, local falsifier suite only):**
  1. Swapped `raw_intent_digest_sha256` for a fabricated constant → 1 falsifier failed. Restored.
  2. Swapped the carried-through `capability` for a fabricated, fully-permissive `Capability` → 1 falsifier failed. Restored.
  3. Swapped `derivation_time` for `datetime.min` → 1 falsifier failed. Restored.
  4. Dropped `delta_records` to `()` → 1 falsifier failed. Restored.
  Final restore hash `5374f6ed439411c6842db9a1ac228cef62a9fd8963c896e9294b1bfb6962b959` confirmed byte-identical to the pre-mutation baseline after every mutation; all 13 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **390 passed, 753 deselected, 0 failed** (13 actor_projection + 17 capability + 25 chain_results + 11 composed_effect + 26 delta_evaluation + 69 candidate_deltas + 15 field_pulse + 17 field_snapshot + 91 simplix + 78 operation_index + 28 observation_ingress); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed for this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a pure, no-I/O re-packaging module with no new persistence, no schema change, no session/authority/capability-resolution touch, and no cross-field protocol change — none of the enumerated full-regression triggers apply.

**10 INVERSE SWEEP (E6).**
```text
raw_intent / fingerprint    <- ObservationIngressResult.raw_intent /                    -- canonical, sourced (a)
                               .raw_intent_digest_sha256 (R-01), verbatim
derivation_time             <- ObservationIngressResult.observed_at (R-01), verbatim    -- canonical, sourced (a)
semantic_observation         <- SemanticObservation (R-05), verbatim                     -- canonical, sourced (a)
delta_records                <- DeltaRecord tuple (R-07), verbatim                       -- canonical, sourced (a)
chain_result                 <- ChainResult (R-09), verbatim; already holder-class-safe  -- canonical, sourced (a)
                                 by construction (I-17), proven directly
capability                   <- Capability (R-10), verbatim                              -- canonical, sourced (a)
proof_ceiling                <- NOT PROJECTED: no producer exists anywhere (R-07's own    -- disclosed absence,
                                 already-disclosed gap)                                      never fabricated
richer basis identity        <- NOT PROJECTED beyond fingerprint + derivation time: no    -- disclosed absence,
                                 (reference, version) bookkeeping producer exists             never fabricated
```
No CACHED value: every call recomputes from its own given arguments, never storing or reusing a prior projection (`test_same_inputs_give_the_same_projection_every_time` / `test_two_different_observations_project_independently_no_shared_mutable_state` prove this together). No DUPLICATED value: every field is read once from its own real producer's output, never re-derived a second way. No PROMOTED value: `ActorSafeProjection` presents exactly what its five source objects already established, never upgrading a boundary result into an authority grant. No BYPASSED value: no HTTP route or CYAN wiring exists yet; the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-12 is materialized and closed for its own disclosed scope. Re-running E1 against this now-committed state (to be re-derived fresh, not assumed here): R-11 (provider-safe projection eligibility) is the one relation in `02_RELATIONS.md`'s own table not yet materialized. It is **not** a Human Authority boundary and not the SEND path itself — its own OUTPUT is explicitly "not a provider payload, it is not transmitted, and it produces no manifest" — it is a backend-only, pre-SEND relation like every other one in this Field, honestly producible even though its real value is vacuously empty today (its own PRECONDITION, "it exists only if the MLT is non-empty", is never satisfied, the same already-cross-checked fact this Field has proven from four independent directions, WU-7/8/9/10). R-13 (future SEND gate) and R-14 (reconstruction after material change) remain explicitly marked "boundary relation; not materialized" / cross-cutting by the RED text itself — R-13 specifically is the genuine Human Authority / SEND-path boundary this Field continues to never cross. Having closed every relation with real, non-vacuous work (R-01 through R-10, R-12), this Work Unit flags that the combined PCPG suite (390/390, §6–9 above) is a natural "broader regression at a meaningful field boundary" point, as the proof-cadence decision anticipates — already satisfied by this Work Unit's own AFFECTED-SUITES run, which already is the full combined suite. R-11 itself is not a stopping point: it is the next candidate relation, to be re-derived fresh (not assumed) and materialized under the same autonomous continuation already authorized. Not a future Field.

## 3. Falsifier map (13 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_raw_intent_is_carried_through_verbatim` / `test_raw_intent_digest_is_the_real_ingress_producers_own_value` / `test_derivation_time_is_the_real_ingress_observed_at` | 3 | item 1 (raw intent + fingerprint + derivation time) |
| `test_semantic_observation_is_carried_through_verbatim` | 1 | item 2 |
| `test_delta_records_are_carried_through_verbatim` | 1 | item 3 |
| `test_chain_result_is_carried_through_verbatim` | 1 | item 4 |
| `test_capability_is_carried_through_verbatim` | 1 | item 5 |
| `test_projection_adds_no_field_beyond_the_seven_named_items` | 1 | no fabrication |
| `test_two_different_observations_project_independently_no_shared_mutable_state` | 1 | no shared state |
| `test_no_field_in_the_projection_carries_another_actors_identity` / `test_authority_requirement_carries_only_delta_id_result_and_reason` | 2 | I-17 |
| `test_same_inputs_give_the_same_projection_every_time` | 1 | determinism |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static |

## 4. Deliberate exclusions (not defects; later Work Units)

- "The proof ceiling": no producer anywhere in this codebase (R-07's own already-disclosed gap, one of ~15 delta-record fields it does not yet produce).
- The richer "basis identity" composite beyond the raw-intent fingerprint and derivation time (canonical facts consulted as (reference, version) pairs; authority facts including absence facts; Pulse elements by reference; rule-set/data-policy/provider-policy versions): no structured version-bookkeeping producer exists anywhere today — `pcpg_capability.py`'s own module docstring already disclosed this same gap.
- A top-level "unavailable" projection variant for the FAILURE STATE: this pure function's own non-optional signature already enforces structural completeness; wiring an honest "unavailable" HTTP response for a genuine upstream exception is a dispatch-layer concern, out of scope (no PCPG relation has an HTTP route yet).
- R-11: not materialized; vacuously gated by "exists only if the MLT is non-empty", never true today.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-12 (actor-safe projection, 5 of 7 named OUTPUT items covered, 2 disclosed absent) is materialized for its own disclosed scope, independently falsified (13/13), mutation-proven (4/4 guards killed and restored, byte-identical after restore), and proven affected-suite-clean (390 passed / 0 failed, full combined PCPG suite — itself the broader PCPG-integration regression this field boundary calls for). No full-repository regression was run for this Work Unit, per the Human Authority proof-cadence decision recorded in `WU-PFC-PCPG-8.md` §12: this delta touches no global invariant. §11 notes the Field has closed every relation with real, non-vacuous work except R-11 (vacuously gated, not a Human Authority boundary) and R-13/R-14 (explicitly not materialized by the RED text itself; R-13 is the genuine SEND-path boundary). Continuing autonomously to R-11 under the standing authorization.
