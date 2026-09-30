# WU-PFC-PCPG-7 — R-07: per-delta governance evaluation (RESULT/REASON increment)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-7 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "APPROVED. Commit the completed R-06 work unit... Then reconstruct the field from the published checkpoint and derive the next First Broken Relation from that state. Do not select between the remaining IMPLIED scope and R-07 from the pre-publication candidate list. Re-derive after publication. Continue autonomously under the same SFE discipline and stop only at a true Human Authority boundary." (2026-09-30). |
| Predecessor | `pfc-integration` `28dd2c27729014ff6f5cda64b109a48b0dbb2173` (`checkpoint-PFC-PCPG-6`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (this Work Unit adds no schema; it composes existing real outputs only). |
| E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-6`) | Confirmed by repository search: `pcpg_candidate_deltas.py` (R-06 DIRECT deltas), `pcpg_field_snapshot.py` (R-03), `pcpg_field_pulse.py` (R-04) all real; `grep` for `DeltaRecord`/`Result.`/the RESULT vocabulary: zero hits — R-07 genuinely absent. R-07's own INPUT ("each delta, the Field snapshot and the Pulse") is satisfied NOW for the DIRECT-delta subset R-06 already produces; nothing in R-07's own PRECONDITION or FAILURE STATE names R-06's disclosed IMPLIED-delta gap as a blocker (R-07 evaluates "each delta" generically, whatever list it receives). **R-07 is the next First Broken Relation**, re-derived after publication, not selected from the pre-publication candidate list. No new bypass path found. |
| Authorized delta (this Work Unit, disclosed scope) | R-07 for `RESULT` + `REASON` only, plus a passthrough of the delta fields already real from R-05/R-06 (`delta_id`, `operation`, `execution_class`, `target`, `source_clause`, `span`, `current_state`, and the one real FLAG already computed, `DECISION_SUBSTITUTION_REQUESTED`). `04_OBSERVATION_RESULT.md` §5 names roughly twenty delta-record fields; the remaining ~15 (`REQUIRED_AUTHORITY`, `ACTUAL_AUTHORITY` with binding reference, `AUTHORITY_SOURCE`/`SCOPE`, `DATA_CLASSIFICATION`, `PROOF_CEILING`, `OUTPUT_CONTRACT`, `ELIGIBILITY`, ...) each need a producer that does not exist in this codebase (a data-class classifier, FBR-PCPG-3, still OPEN; an AUTH-DEP-to-authority-class lookup table; an AI-contract output-class registry) — disclosed, not fabricated. |
| Must become true | A pure function `evaluate_deltas(deltas, snapshot, *, flags_by_delta_id) -> tuple[DeltaRecord, ...]` exists: every delta gets exactly one record with exactly one `Result`; the algorithm never re-implements a readiness rule, reading `session_position.actions`'s own `available`/`reasonCode` unchanged (R-07's own PRECONDITION, verbatim). |
| Must remain true | `pcpg_candidate_deltas.form_candidate_deltas`, `pcpg_field_snapshot.reconstruct_field`, `pcpg_operation_index.resolve_operation` all unchanged; every existing route, Command, migration and test. |
| Must remain impossible | A `PROVIDER_COMPUTATION` delta ever resolving `ALLOWED` in the current, already-decided Field (HA-PCPG-1's own fail-closed default); an authority-lack reason code classified `STATE_BOUNDARY` or vice versa; a delta silently dropped; a `RESULT` invented without a real, cited source. |
| Falsifiers | `tests/e2e/test_pcpg_delta_evaluation.py`: 26 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (26 cases) was written first, importing `Result`, `evaluate_deltas` from `application.pcpg_delta_evaluation`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_delta_evaluation'` — the correct reason. One authoring bug found on the first real GREEN run (not a RED-authoring mistake): a test's own `_delta()` helper never set `current_state` on the input delta it built, so its own passthrough assertion trivially failed against a delta that never carried the value to pass through; fixed by adding a `current_state` parameter to the helper and passing the real value explicitly. 26/26 passed after the fix.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no per-delta RESULT/REASON producer exists for R-08 (composition) to consume
CONSUMER         (future) R-08 (composed effect), R-09 (chain results) -- not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-07 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-07), per-delta governance
                 evaluation
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-07; `04_OBSERVATION_RESULT.md` §5 (delta record fields) and §6 (RESULT vocabulary, verbatim); `00_FIELD.md` §13 HA-PCPG-1 and `04_OBSERVATION_RESULT.md` §8 (the Field's own already-decided `GOVERNANCE_ADMISSIBLE = false` value, restated here as a static, cited fact); `application.inquiry_queries.session_position`'s own `actions` dict (already real, already quoted by R-03/R-04); `application.inquiry_queries.py`'s own real reason-code strings (grepped, not guessed).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_delta_evaluation.py`: `Result` (this Field's own §6 vocabulary, its first materialization — all 8 real values defined, I-20 — this increment's own producer emits 5 of them: `INDETERMINATE`, `GOVERNANCE_BOUNDARY`, `HUMAN_ACTION_AVAILABLE`, `AUTHORITY_BOUNDARY`, `STATE_BOUNDARY`), `DeltaRecord`, `evaluate_deltas()`. The mapping algorithm, each branch cited (full text in the test file's own module docstring, not repeated here): UNKNOWN operation → `INDETERMINATE`/`SEMANTIC_UNKNOWN` (I-04); `PROVIDER_COMPUTATION` → `GOVERNANCE_BOUNDARY`/`OPERATION_CLASS_NOT_ADMITTED` unconditionally (HA-PCPG-1's own already-decided fail-closed default, static, cited — **this is why `ALLOWED` is correctly never produced by this increment: the current real Field has no path to it at all, an architectural fact this module only quotes, not a gap**); operation not present in `snapshot.session.actions` (no Session named, or a root-scope operation) → `INDETERMINATE`/`NO_AUTHORITATIVE_PRODUCER` (R-07's own FAILURE STATE, verbatim); otherwise, `available`/`reasonCode` read straight from the real `session.actions` entry, with a closed, directly-grepped set of the real authority-lack reason codes (`_AUTHORITY_REASON_CODES`, six strings verified against `inquiry_queries.py`'s own source) distinguishing `AUTHORITY_BOUNDARY` from the residual `STATE_BOUNDARY` category.
- `tests/e2e/test_pcpg_delta_evaluation.py`: 26 falsifiers (§3).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_candidate_deltas` / `pcpg_field_snapshot` / `pcpg_operation_index` | NOT AFFECTED | Read-only consumption; nothing in any of them changed. |
| `pcpg_field_pulse` | NOT AFFECTED | No import from this module reaches it; the end-to-end falsifier composes both without collision, confirming R-07 and R-04 remain independent consumers of R-03's snapshot. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-07 has no HTTP surface in this Work Unit. |
| `ai_gateway` / provider path | NOT AFFECTED | No import, no call (static AST falsifier, §3). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` (new module, 2 `cast()` uses, documented — `session_position.actions` is loosely-typed `Mapping[str, object]`) 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- Producer proof: `test_available_human_command_is_human_action_available`, the 6-case `test_the_closed_set_of_real_authority_lack_codes_gives_authority_boundary` and 6-case `test_every_other_real_reason_code_gives_state_boundary` (12 total, each a direct, cited reason-code classification), `test_delta_id_operation_target_and_current_state_are_quoted_not_recomputed`.
- Adversarial proof: `test_unknown_operation_is_indeterminate_semantic_unknown` (I-04); `test_provider_computation_is_always_governance_boundary_never_allowed` + `test_allowed_is_never_produced_by_this_increment` (the HA-PCPG-1 fail-closed default, proven both directly and end-to-end through a real `form_candidate_deltas` → `evaluate_deltas` chain); `test_no_session_named_gives_no_authoritative_producer` + `test_a_root_scope_operation_not_in_session_actions_gives_no_authoritative_producer` (R-07's own FAILURE STATE, both the no-Session and the root-scope-operation shape); `test_result_is_this_fields_own_complete_vocabulary` (I-20, static); `test_the_module_touches_no_database_and_no_provider` (static AST, P-01/I-16).
- **MUTATION proof (manual, 5 guards):**
  1. Removed the `PROVIDER_COMPUTATION → GOVERNANCE_BOUNDARY` rule entirely → `test_provider_computation_is_always_governance_boundary_never_allowed` failed (fell through to `INDETERMINATE`/`NO_AUTHORITATIVE_PRODUCER` instead — still never `ALLOWED`, but the specific, cited reason was lost, correctly caught). Restored; byte-diff clean.
  2. Inverted the `AUTHORITY_BOUNDARY`/`STATE_BOUNDARY` classification → all 12 of the two exhaustive parametrized falsifiers failed. Restored; byte-diff clean.
  3. Removed the `NO_AUTHORITATIVE_PRODUCER` branch entirely (operations absent from `session.actions` fell through to a `KeyError`) → both no-Session and root-scope-operation falsifiers failed with the real exception. Restored; byte-diff clean.
  4. Broke `flags` passthrough (always empty) → `test_decision_substitution_requested_flag_is_carried_through` failed. Restored; byte-diff clean.
  5. Silently dropped the first delta (`for delta in deltas[1:]`) → `test_every_delta_gets_exactly_one_record_none_dropped` failed (`2 == 3` false). Restored; byte-diff clean.
  Final restore hash `f760bfa6503f9bbda94b89176291731f5ad4dd49ea13b1d821d491a42e93b35a` confirmed byte-identical to the pre-mutation baseline after every mutation.
- **PRESERVATION / REGRESSION.** Combined PCPG suite (delta_evaluation + candidate_deltas + field_pulse + field_snapshot + simplix + operation_index + observation_ingress + isolation_sweep): **408 passed, 0 failed** (26 + 69 + 15 + 17 + 91 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN:** started only after `git status`/`git diff` confirmed the complete final tree (0 modified, 3 new files, all this Work Unit's own, including this report); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff), each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2320 passed, 15 skipped, 0 failed, in 3283.18s (0:54:43)** — exactly 2294 (WU-6's own closing count) + 26 (this Work Unit's own falsifiers), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
delta_id / operation /       <- the real CandidateDelta's own fields, quoted unchanged (R-06)    -- canonical,
  execution_class / target /                                                                          sourced (a)
  source_clause / span /
  current_state
result (INDETERMINATE,        <- I-04 / R-07's own FAILURE STATE, verbatim                          -- versioned SFE
  UNKNOWN-operation or                                                                                  rule (c), cited
  no-producer cases)
result (GOVERNANCE_BOUNDARY,  <- 00_FIELD.md §13 HA-PCPG-1's own already-decided fail-closed         -- canonical,
  PROVIDER_COMPUTATION case)      default, restated by 04_OBSERVATION_RESULT.md §8 as the                sourced (a),
                                  Field's CURRENT value -- not computed per call                          a static fact
result (HUMAN_ACTION_          <- session_position.actions's own available/reasonCode fields,        -- canonical,
  AVAILABLE, AUTHORITY_            read unchanged, classified against a closed, directly-grepped          sourced (a)
  BOUNDARY, STATE_BOUNDARY)        set of real authority-lack codes
flags                          <- the real SemanticAction.decision_substitution_requested fact       -- canonical,
                                   (R-05), passed through a caller-supplied mapping, never re-derived      sourced (a)
```
No CACHED value: every record is computed fresh from its two real inputs on each call (`test_same_inputs_give_the_same_records_every_time` proves determinism without a cache). No DUPLICATED value: `available`/`reasonCode` are read from `session_position.actions` exactly once, never re-implemented by a second, potentially-divergent rule (the closed `_AUTHORITY_REASON_CODES` set is a CLASSIFICATION of the real, already-produced reason-code strings, not a second readiness computation). No PROMOTED value: a `DeltaRecord`'s `result`/`reason` are presented exactly as derived facts, never as authority, evidence or a decision of their own. No BYPASSED value: no consumer exists yet (R-08 not materialized); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/`ai_gateway` import exists anywhere in the module. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-07 is materialized and closed for its own disclosed RESULT/REASON scope. A genuinely important, provable fact surfaced by this Work Unit and worth stating plainly: in the CURRENT real NQUIRY Field, **no delta can ever resolve `ALLOWED`** — every `PROVIDER_COMPUTATION` delta is unconditionally `GOVERNANCE_BOUNDARY` (HA-PCPG-1's own fail-closed default), and no other execution class is eligible for `ALLOWED` at all (04 §6: "ALLOWED: a PROVIDER_COMPUTATION that is legitimate ... in every respect"). This matches `04_OBSERVATION_RESULT.md` §8's own already-published conclusion ("CAN_SEND is currently false for every observation. That is correct, not a defect.") from a second, independent direction (per-delta RESULT rather than the whole-observation capability projection) — the two now agree, which is itself a form of cross-checked proof. Re-running E1 against this now-committed state (to be re-derived fresh, not assumed here): R-08 (composed effect) becomes the candidate next relation, since its own INPUT ("the delta records") is now satisfied by this Work Unit's own output for the DIRECT-delta subset; R-06's own disclosed IMPLIED-delta scope remains open in parallel, non-blocking. Neither is a Human Authority boundary or a future Field.

## 3. Falsifier map (26 cases)

| Falsifier group | Cases | Proves |
|---|---|---|
| UNKNOWN operation | 1 | I-04 |
| PROVIDER_COMPUTATION → GOVERNANCE_BOUNDARY, never ALLOWED | 2 | HA-PCPG-1's own already-decided fail-closed default |
| No authoritative producer (no Session / root-scope operation) | 2 | R-07's own FAILURE STATE, verbatim |
| HUMAN_COMMAND result classification (available, ×6 authority codes, ×6 state codes) | 13 | the readiness producer is quoted, never re-derived; the classification is closed and cited |
| Passthrough fields, flags, defaults | 3 | quoting, not recomputation |
| Completeness, determinism, purity, vocabulary completeness | 4 | P-04-style completeness, I-19, P-01/I-16, I-20 |
| End-to-end, real DB-backed | 1 | the whole chain (R-03 → R-05 → R-06 → R-07) composes correctly against a real Session, P-14-style equivalence against the live producer |

## 4. Deliberate exclusions (not defects; later Work Units)

- ~15 delta-record fields from `04_OBSERVATION_RESULT.md` §5 (`REQUIRED_AUTHORITY`, `ACTUAL_AUTHORITY` with binding reference, `AUTHORITY_SOURCE`/`SCOPE`, `DECLARED_PURPOSE`/`SEMANTIC_PURPOSE`/`PURPOSE_ALIGNMENT`, `SOURCE_AUTHORITY`, `DATA_CLASSIFICATION`, `EXTERNAL_EFFECT`/`REVERSIBILITY`, `PROOF_CEILING`, `OUTPUT_CONTRACT`, `BOUNDARY`, `ELIGIBILITY`): each needs a producer that does not exist in this codebase today.
- `DATA_BOUNDARY` and `DENIED` as producible `Result` values: no data-class classifier (FBR-PCPG-3, GAP-11-006, still OPEN) or immutable-source-mutation detector exists.
- R-08 through R-12: not materialized; this module has no consumer yet.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-07 (per-delta governance evaluation, RESULT/REASON increment) is materialized for its own disclosed scope, independently falsified (26/26), mutation-proven (5/5 guards killed and restored), and proven repository-wide preservation-clean (2320 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). A genuinely important architectural fact was surfaced and cross-checked: no delta can currently resolve ALLOWED in the real Field, matching `04_OBSERVATION_RESULT.md` §8's own independently-stated conclusion from a different direction. Not committed, not tagged, not pushed.
