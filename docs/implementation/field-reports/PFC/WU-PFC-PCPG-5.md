# WU-PFC-PCPG-5 — R-04: Field Pulse

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-5 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "PASS. Human Authority approves the completed R-03 Work Unit... After that continue autonomously with the derived next First Broken Relation: R-04 — FIELD PULSE. Do not redesign R-04. Derive its minimum coherent implementation from Architecture 26 and the current repository... Do not cross a TRUE Human Authority boundary. Do not begin any SEND path." (2026-09-30). |
| Predecessor | `pfc-integration` `2ad794f1b8b9d41ef0f26a7c1838c2b59c355fd1` (`checkpoint-PFC-PCPG-4`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (this Work Unit adds no schema; it composes existing read-only producers only). |
| Authorized delta (this Work Unit, disclosed scope) | R-04 ONLY, 7 of its 10 §3 Pulse elements, each with a real, already-existing producer: ACTIVE_TRANSITIONS / PENDING_AUTHORITY_REQUIREMENTS (from `session_position.actions`'s own `relevant`/`available`/`reasonCode`, already carried by R-03's `SessionContext`); IN_FLIGHT_OPERATIONS (`application.reflection_proof._unresolved`, `00_FIELD.md` §7's own named home); STALE_SOURCES (`application.frozen_set.verify_frozen_set`, F03); EXTERNAL_DEPENDENCIES (the same static fact R-03 already materializes); UNRESOLVED_ELIGIBILITY (static, cited — GAP-11-006/HARD-DEP-002/GAP-08-008 are unconditionally OPEN today); GOVERNANCE_BLOCKERS (HA-23, R-04's own worked example, cited exactly while the named Session is in INVESTIGATION). Three elements (PENDING_HUMAN_DECISIONS, INDETERMINATE_CONSEQUENCES beyond what `_unresolved` covers, RECENT_AUTHORITY_CHANGE) have no real listing producer in this codebase today — "do not redesign R-04" was read as "do not invent new persistence surface to fill them"; each is named in `Pulse.unresolved`, never silently dropped. |
| Must become true | A pure function `derive_pulse(ports, snapshot, *, workspace_id, session_id) -> Pulse` exists, composing only real, already-proven producers; introduces no status, lifecycle, flag or counter of its own (I-07). |
| Must remain true | `session_position`, `reflection_proof._unresolved`, `frozen_set.verify_frozen_set`, `pcpg_field_snapshot.reconstruct_field` all unchanged; every existing route, Command, migration and test. |
| Must remain impossible | Any Pulse element the real producer would not itself report (P-15); a Pulse element invented from nothing (I-07); a governance blocker asserted outside the one real, cited HA-23/INVESTIGATION case; a mutation that hardcodes a per-call-varying element to a constant without a falsifier catching it. |
| Falsifiers | `tests/e2e/test_pcpg_field_pulse.py`: 15 cases. |

## 0. E1 re-derivation (against `checkpoint-PFC-PCPG-4`)

Before this Work Unit, R-03 and R-05 were both real; R-04 and R-06 were the two unblocked siblings (§0/§11 of `WU-PFC-PCPG-4.md`), tie-broken toward R-04 on the evidence that it is named CONSUMER by two later relations (R-07, R-09) against R-06's one (R-07). This Work Unit closes R-04. Re-deriving now: R-06 (candidate delta formation) remains the sole relation whose own prerequisites (R-03, R-05) are both already real and which is not yet itself materialized — closing R-04 does not newly unblock anything else, since R-07 (the next relation after R-06) needs delta records from R-06 itself, still absent, regardless of Pulse now existing. **R-06 is therefore the next First Broken Relation**, unambiguously this time (no sibling tie remains).

## 2. Execution record

**1 RED (right reason).** The falsifier suite (15 cases, including one added after the first GREEN pass — see §6) was written first, importing `GOVERNANCE_BLOCKER_HA23`, `UNRESOLVED_ELIGIBILITY_REASONS`, `derive_pulse` from `application.pcpg_field_pulse`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_field_pulse'` — the correct reason. All falsifiers passed on the first real run against the implementation (no authoring-bug detour), a direct result of researching each Pulse element's real producer before writing any code (§0 of `tests/e2e/test_pcpg_field_pulse.py`'s own module docstring).

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no Pulse view exists for R-07/R-09 to consume alongside R-03's snapshot
CONSUMER         (future) R-07 (per-delta governance evaluation), R-09 (chain results) --
                 not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-04 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-04), Field Pulse
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-04; `04_OBSERVATION_RESULT.md` §3 (the 10-element list, verbatim); each covered element's own real home (`00_FIELD.md` §7): `application.inquiry_queries.session_position`, `application.reflection_proof._unresolved`, `application.frozen_set.verify_frozen_set`; `docs/implementation/field-reports/PFC/HUMAN_AUTHORITY_QUEUE.md` (HA-23).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_field_pulse.py`: `Pulse`, `derive_pulse()`, and two named, cited constants (`GOVERNANCE_BLOCKER_HA23`, `UNRESOLVED_ELIGIBILITY_REASONS`). `ACTIVE_TRANSITIONS`/`PENDING_AUTHORITY_REQUIREMENTS` are read directly from `FieldSnapshot.session.actions` (no new DB call — R-03's own output already carries `relevant`/`available`/`reasonCode` per R-04's own citation). `IN_FLIGHT_OPERATIONS` calls `reflection_proof._unresolved` directly (imported despite its leading underscore, because `00_FIELD.md` §7 itself names this exact private symbol as the canonical producer — no public wrapper of the same fact exists to prefer instead). `STALE_SOURCES` re-calls `frozen_set.verify_frozen_set` for a COMPLETED Burst, exactly as `session_position` itself already does. `EXTERNAL_DEPENDENCIES` reuses `pcpg_field_snapshot.EXTERNAL_EFFECTS` directly (the identical real fact, not a second definition — I-20). `UNRESOLVED_ELIGIBILITY` is a static `True`, cited against three unconditionally-OPEN gaps (GAP-11-006, HARD-DEP-002, GAP-08-008). `GOVERNANCE_BLOCKERS` cites `HA-23` exactly when `snapshot.session.state == "INVESTIGATION"` — R-04's own worked example, the one concrete case this Field's own text names, not a general Case-3 scanner over the whole HA queue (no such scanner's producer exists). Three elements (`PENDING_HUMAN_DECISIONS`, `INDETERMINATE_CONSEQUENCES` beyond `_unresolved`'s own coverage, `RECENT_AUTHORITY_CHANGE`) are named in the static `_NOT_YET_COVERED` tuple and surfaced via `Pulse.unresolved` — disclosed, not silently dropped, because no real listing producer exists in this codebase for any of the three today (`DecisionRepository`/`recovery_repository` are get-only; "a source changed after it gated something" has no generic, delta-free comparison basis at R-04's own level).
- `tests/e2e/test_pcpg_field_pulse.py`: 15 falsifiers (§3).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `session_position` / `reflection_proof._unresolved` / `frozen_set.verify_frozen_set` / `pcpg_field_snapshot.reconstruct_field` | NOT AFFECTED | Read-only consumption in every case; nothing in any of them changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-04 has no HTTP surface in this Work Unit. |
| `pcpg_simplix.py` / `pcpg_operation_index.py` / `pcpg_observation.py` | NOT AFFECTED | No import from this module reaches any of them. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` (new module) 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- Producer proof: `test_active_transitions_equals_the_relevant_subset_of_session_actions`, `test_pending_authority_requirements_equals_unavailable_relevant_reason_codes`, `test_in_flight_operations_equals_the_real_unresolved_function` — each a direct equality against the real producer's own live value, both non-empty-case-checked (`assert expected` / `assert real_relevant`) so an accidentally-trivial (empty-everywhere) fixture could never pass silently.
- **A disclosed test-strength gap closed before mutation proof, not after:** the first version of `IN_FLIGHT_OPERATIONS`'s equivalence falsifier only exercised a fixture where the real value is `False` — a mutation hardcoding `in_flight_operations = False` would have passed undetected. Recognized during design (informed by WU-PFC-PCPG-4's own disclosed near-miss with its authority-binding equivalence test) and closed BEFORE running mutation proofs: `test_in_flight_operations_is_true_for_an_authorized_not_yet_executed_analysis` (via `f04_support.analysis_context`, mirroring `fixtures/NQUIRY_SESSION_AUTHORITY.txt`'s own "Session C" variant) proves the real `True` case.
- Adversarial proof: `test_no_session_named_gives_no_active_transitions_or_requirements` (I-05-adjacent: Pulse is conditioned on what the snapshot actually names, never fabricated for an absent Session); `test_governance_blockers_is_empty_outside_investigation` / `test_governance_blockers_cites_ha23_while_in_investigation` (a real Session driven to INVESTIGATION via the already-proven WU-PFC-B4/B5 product path, not assumed); `test_pulse_introduces_no_status_or_counter_of_its_own` (I-07, static field-name check); `test_the_module_touches_no_provider_and_makes_no_egress` (I-16/B-08, static AST check).
- **MUTATION proof (manual, 5 guards):**
  1. Removed the `relevant` filter on `ACTIVE_TRANSITIONS` (included every action) → `test_active_transitions_equals_the_relevant_subset_of_session_actions` failed (14 extra items). Restored; byte-diff clean.
  2. Hardcoded `in_flight_operations = False` unconditionally → caught by the STRENGTHENED falsifier above (`test_in_flight_operations_is_true_for_an_authorized_not_yet_executed_analysis`, added specifically because the original equivalence test alone would have missed this exact mutation — disclosed, not hidden). Restored; byte-diff clean.
  3. Removed the `INVESTIGATION` condition on `GOVERNANCE_BLOCKERS` (always empty) → `test_governance_blockers_cites_ha23_while_in_investigation` failed. Restored; byte-diff clean.
  4. Hardcoded `unresolved_eligibility = False` → `test_unresolved_eligibility_is_always_true_today_citing_the_real_open_gaps` failed. Restored; byte-diff clean.
  5. Silently shrank `_NOT_YET_COVERED` from 3 names to 1 (hiding two real, disclosed gaps) → `test_unresolved_names_the_three_not_yet_covered_elements` failed. Restored; byte-diff clean.
  Final restore hash `b5e8de4fe9f3c4ce58093c362abd5cc3a0964f6282a058873e185aa4fee57121` confirmed byte-identical to the pre-mutation baseline after every mutation.
- **PRESERVATION / REGRESSION.** Combined PCPG suite (field_pulse + field_snapshot + simplix + operation_index + observation_ingress + isolation_sweep): **312 passed, 0 failed** (15 + 17 + 90 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN:** started only after `git status`/`git diff` confirmed the complete final tree (0 modified, 3 new files, all this Work Unit's own, including this report); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff), each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2224 passed, 15 skipped, 0 failed, in 1923.71s (0:32:03)** — exactly 2209 (WU-4's own closing count) + 15 (this Work Unit's falsifiers), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
active_transitions /         <- session_position.actions's own relevant/available/     -- canonical,
  pending_authority_             reasonCode fields, quoted (already real via R-03)          sourced (a)
  requirements
in_flight_operations          <- reflection_proof._unresolved's own live result           -- canonical, sourced (a)
stale_sources                 <- frozen_set.verify_frozen_set's own live result            -- canonical, sourced (a)
external_dependencies         <- pcpg_field_snapshot.EXTERNAL_EFFECTS, the SAME real       -- canonical,
                                  constant (I-20: no second, divergent definition)             sourced (a), reused
unresolved_eligibility        <- a static, cited fact (three unconditionally-OPEN gaps)    -- versioned SFE fact (c)
governance_blockers           <- HA-23, cited against a real, live session.state read      -- canonical, sourced (a),
                                                                                                plus a cited HA fact
unresolved                    <- a static, disclosed list of the 3 elements this Work      -- versioned SFE fact (c),
                                  Unit does not yet cover                                       self-disclosed as such
```
No CACHED value: every element is read fresh on each call (`test_pulse_is_identical_for_two_calls_at_the_same_basis` proves determinism without a cache). No DUPLICATED value: `EXTERNAL_DEPENDENCIES` reuses R-03's own constant BY REFERENCE (the same object), not a re-typed literal that could drift; every other element reads its own real producer once, never reimplemented. No PROMOTED value: `Pulse` and its fields are used purely as a stratum-1 view — nothing here is labeled or treated as authority, evidence, a decision or a capability; `test_pulse_introduces_no_status_or_counter_of_its_own` statically confirms no id/timestamp/version field exists that Pulse itself would own. No BYPASSED value: no consumer exists yet (R-06/R-07 not materialized); the static AST falsifier confirms no forbidden method call and no `ai_gateway`/provider-SDK import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-04 (Field Pulse) is materialized and closed for its own disclosed 7-of-10-element scope. Re-running E1 against this now-committed state (§0 above): **R-06 (candidate delta formation) is the next First Broken Relation**, unambiguously — its own two prerequisites (R-03, R-05) are both already real, and closing R-04 did not newly unblock anything beyond what R-06 itself still gates (R-07 needs R-06's delta records regardless of Pulse's own existence). Not a Human Authority boundary, not a future Field.

## 3. Falsifier map (15 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_active_transitions_equals_the_relevant_subset_of_session_actions` | 1 | P-15: ACTIVE_TRANSITIONS is exactly the relevant subset, quoted |
| `test_pending_authority_requirements_equals_unavailable_relevant_reason_codes` | 1 | P-15: PENDING_AUTHORITY_REQUIREMENTS is exactly the unavailable-relevant reason codes |
| `test_no_session_named_gives_no_active_transitions_or_requirements` | 1 | Pulse never fabricates a Session-scoped element for an absent Session |
| `test_in_flight_operations_is_false_with_no_analysis_yet_requested` / `..._equals_the_real_unresolved_function` / `..._is_true_for_an_authorized_not_yet_executed_analysis` | 3 | P-15, including the genuinely non-trivial `True` case |
| `test_stale_sources_is_empty_with_no_completed_burst` | 1 | STALE_SOURCES is conditioned on a real precondition, never guessed |
| `test_external_dependencies_is_empty_matching_00_field_section_3` | 1 | the identical, reused static fact |
| `test_unresolved_eligibility_is_always_true_today_citing_the_real_open_gaps` | 1 | the cited, unconditionally-OPEN gaps |
| `test_governance_blockers_is_empty_outside_investigation` / `..._cites_ha23_while_in_investigation` | 2 | HA-23 cited exactly for the one real, worked case |
| `test_unresolved_names_the_three_not_yet_covered_elements` | 1 | the disclosed gap list is exact, never silently narrowed |
| `test_pulse_introduces_no_status_or_counter_of_its_own` | 1 | I-07, static shape proof |
| `test_the_module_touches_no_provider_and_makes_no_egress` | 1 | I-16/B-08, static AST proof |
| `test_pulse_is_identical_for_two_calls_at_the_same_basis` | 1 | determinism |

## 4. Deliberate exclusions (not defects; later Work Units)

- PENDING_HUMAN_DECISIONS, INDETERMINATE_CONSEQUENCES (beyond `_unresolved`'s own coverage), RECENT_AUTHORITY_CHANGE: no real listing producer exists in this codebase today for any of the three (§0 of the test file's own docstring). Each is named in `Pulse.unresolved`. A future Work Unit that adds the needed persistence-layer listing methods (a `DecisionRepository.list_under_consideration`-shaped method, a `recovery_repository` listing method, a generic binding-history-vs-source-version comparator) closes them — not invented speculatively here.
- GOVERNANCE_BLOCKERS beyond HA-23: no generic "which HA question governs which relation" index exists; only the one case the RED text itself names is covered.
- R-06 through R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-04 (Field Pulse) is materialized for its own disclosed scope, independently falsified (15/15), mutation-proven (5/5 guards killed and restored — one guard's coverage gap was recognized and closed BEFORE mutation proof, informed directly by the prior Work Unit's own disclosed near-miss), and proven repository-wide preservation-clean (2224 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). Not committed, not tagged, not pushed.
