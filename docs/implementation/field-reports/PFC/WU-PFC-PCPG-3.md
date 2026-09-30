# WU-PFC-PCPG-3 — R-05: the local SIMPLIX semantic sweep

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-3 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "Continue with R-05. Materialize the local SIMPLIX semantic sweep under HA-PCPG-2 fail-closed default: rule-based, reproducible, no model, no LLM, no embeddings, no external provider. UNKNOWN must remain UNKNOWN. Do not derive authority, state, membership, role, evidence, capability or provider eligibility from semantics. Run the full SFE loop... Do not cross a Human Authority boundary. Do not begin any SEND path." (2026-09-30), following the pushed `checkpoint-PFC-PCPG-2`. |
| Predecessor | `pfc-integration` `203b32da3351a3e3c0a2b0e2f5e17402df3ba13b` (`checkpoint-PFC-PCPG-2`, pushed). |
| State isolation | Same worktree/branch as WU-PFC-PCPG-1/2. No migration (this Work Unit adds no schema; the module is pure, no DB). |
| E1 (re-derived against the current repository) | FBR-PCPG-2 (R-06's own consumable index) is closed (`checkpoint-PFC-PCPG-2`). `02_RELATIONS.md`'s own relation graph (§ header diagram) shows R-06 consumes BOTH R-03 (Field reconstruction) and R-05 (semantic sweep) — neither materialized yet. A repository search confirms no SIMPLIX module exists anywhere (`grep` for `pcpg_simplix`/`SemanticObservation`/`SIMPLIX` before this Work Unit: zero hits outside the RED architecture text itself). Break type (a): nothing exists. This Work Unit's own instruction names R-05 specifically (not R-03, not R-06) — the user's explicit scoping, honored throughout. |
| Authorized delta (this Work Unit, disclosed scope) | R-05 ONLY: the semantic observation (stratum 2) — clauses, actions with modality/negation/requested-executor, targets resolved to in-scope-or-UNKNOWN/OUT_OF_SCOPE, candidate operations (pointers into the real, already-materialized `pcpg_operation_index`, or UNKNOWN), relations touched, a narrow secret-pattern/external-effect detector, and a minimal, closed-vocabulary purpose/drift derivation. Explicitly NOT R-03 (Field reconstruction — no DB-backed canonical snapshot exists yet; SIMPLIX accepts an optional, caller-supplied `in_scope_references`/`out_of_scope_references` mapping instead, disclosed as a future R-03 wiring point), NOT R-06 through R-10 (candidate delta formation, per-delta governance, composition, chain results, capability — no authority, state, membership, role, evidence or capability derived anywhere in this module), NOT FBR-PCPG-3 (the data-class classifier — GAP-11-006 stays OPEN; only a narrow, disclosed secret-pattern detector is implemented, never a general DC-01..07 classifier). |
| Must become true | A pure, deterministic function `observe_semantics(raw_intent, declared_purpose, *, in_scope_references, out_of_scope_references) -> SemanticObservation` exists: no model, no LLM, no embeddings, no external provider, no network egress, no DB, ever. Every UNKNOWN case (unmappable verb, unresolved target, unparseable clause) stays UNKNOWN — never a closest-match guess. |
| Must remain true | `pcpg_operation_index` and every other existing producer unchanged; every existing route, Command, migration and test. |
| Must remain impossible | A fuzzy/closest-match operation substituted for UNKNOWN; a negated, hypothetical or prohibited clause ever read as REQUESTED; an authority-claiming phrase in the raw intent changing which action/operation is detected; any DB, provider or network access from this module (static + dynamic checks); a vocabulary entry naming an operation_id that is not real (I-20, enforced at import time). |
| Falsifiers | `tests/e2e/test_pcpg_simplix.py`: 90 cases. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (90 cases) was written first, importing `RULE_SET_VERSION`, `Modality`, `RequestedExecutor`, `SemanticObservationUnavailable`, `observe_semantics` from `application.pcpg_simplix`. Run against the unrepaired tree: collection error, `ModuleNotFoundError: No module named 'application.pcpg_simplix'` — the correct reason (the relation genuinely does not exist). After implementation, 3 falsifiers failed on the first real run (a clause-splitting bug: plain `", "` was not itself a split boundary, and `[.!?;]` matched inside a quoted title's own `?`) — both were real design/implementation bugs, not RED-authoring errors; fixed, then 90/90 passed. See §4 REPAIR for the exact fixes.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no semantic-observation producer exists for R-06 to consume alongside R-03
CONSUMER         (future) R-06 candidate-delta formation -- not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-05 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-05), the local SIMPLIX
                 semantic sweep
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-05 (producer: SIMPLIX, mechanism open under HA-PCPG-2, default reproducible/rule-based); `04_OBSERVATION_RESULT.md` §4 (execution classes, consumed read-only from `pcpg_operation_index`) and §5 (delta-record field vocabulary: `REQUESTED_EXECUTOR`, `FLAGS.DECISION_SUBSTITUTION_REQUESTED`, both stratum 2 — this module's own scope).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_simplix.py`: `Modality`, `RequestedExecutor`, `SemanticObservationUnavailable`, `SemanticAction`, `SemanticObservation`, `observe_semantics()`. A closed, natural-language trigger vocabulary (`_OPERATION_TRIGGERS`, 27 entries covering all 26 real `pcpg_operation_index` operations — `BEGIN_ANALYSIS`/`REQUEST_QUESTION_ANALYSIS` share the vocabulary's trigger-resolution path with the rest) is validated at **import time** against `pcpg_operation_index.operation_index()`: naming a fictional operation_id raises `ValueError` before the module can even be imported (I-20, proven by mutation §6). Clause splitting is deliberately conservative (over-segments on `,`/` and `/` but `/sentence punctuation, quote-aware so a quoted title's own `?` is never mistaken for a boundary) — over-segmentation is safe by construction (a spurious clause is simply UNKNOWN or stays correctly, locally negated); under-segmentation merging a PROHIBITED clause into an adjacent REQUESTED one would not be, and is proven absent (`test_negation_does_not_suppress_the_other_clause_in_a_compound_intent`, `test_over_splitting_on_and_never_reclassifies_a_prohibited_action_as_requested`). `decision_substitution_requested` is computed strictly from `pcpg_operation_index`'s own real, already-committed `execution_class` field (04 §4's own vocabulary — not authority, not state, not capability) — never guessed. `semantic_purpose`/`purpose_alignment` are deliberately minimal, closed-vocabulary derivations (a single shared operation_id, or a bag-of-words overlap check) — never synthesized text, since free-text summarization would itself require a model, contradicting HA-PCPG-2. A narrow, disclosed secret-pattern regex (`sk-`/`api-`/`token-`-shaped strings) and a closed external-effect verb list (`delete`, `order`, `send`, …) are informational-only flags, explicitly NOT the FBR-PCPG-3 data-class classifier (GAP-11-006 stays OPEN, untouched).
- `tests/e2e/test_pcpg_simplix.py`: 90 falsifiers (§3), including the real NQUIRY-vocabulary analogues of RED fixtures U1–U6, A1, C8, and the semantic-observation-only extraction of `fixtures/NQUIRY_SESSION_AUTHORITY.txt`'s own raw intent.
- **Two real bugs found and fixed during GREEN, not RED-authoring mistakes:** (1) the clause splitter did not treat a bare `", "` as a boundary (only `", and "`/`", but "`), so `"Analyse the questions, pick the most important and start the investigation."` produced 2 clauses instead of 3; fixed by splitting on any `,\s+` independently of a following conjunction. (2) `[.!?;]+\s*` matched a `?` that occurred **inside** a single-quoted title (`'Why do admins churn?'`), truncating the clause before the quote closed and breaking `in_scope_references` matching; fixed with a negative lookahead `(?!['\"])` so sentence punctuation immediately followed by a closing quote is never treated as a clause boundary. Both are proven not to regress by dedicated falsifiers and confirmed by mutation (§6, mutations 1 and 4 respectively — mutation 4 is the exact regression of bug (2), reproduced verbatim by reverting the fix).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_operation_index` (`operation_index`, `resolve_operation`, `ExecutionClass`) | NOT AFFECTED | Read-only consumption (vocabulary validation, `decision_substitution_requested`); nothing in it changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; SIMPLIX has no HTTP surface in this Work Unit. |
| `pcpg_observation.py` / `http_pcpg.py` (WU-1's ingress) | NOT AFFECTED | Not wired to SIMPLIX in this Work Unit (disclosed in §4 of "Deliberate exclusions" below); `governanceObservation: null` stays honest. |
| `ai_gateway` / provider path | NOT AFFECTED | No import from the new module reaches it (static AST falsifier + a dynamic `sys.modules` check, §3). |
| Database / migrations | NOT AFFECTED | The module takes no `ports`/`connection`/`db` argument anywhere (static falsifier, mirroring WU-2's own pattern). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` (new module) 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- Producer proof: every one of the 26 real `pcpg_operation_index` operation_ids has its own trigger-phrase falsifier (`test_the_real_trigger_resolves_to_its_real_operation`, parametrized), and `test_every_real_catalog_operation_has_a_trigger_case_in_this_suite` proves the test table itself is exhaustive against the live catalog (set equality, not a hardcoded count).
- Consumer proof: none yet — R-06 does not exist. Readiness-to-be-consumed is proven the same way WU-2 proved it: every cited `pcpg_operation_index` entry is read live, not duplicated.
- Adversarial proof: the RED fixtures' own semantic-level claims, mined as falsifiers — U1 (unmappable verb never fuzzy-matched), U2 (unresolved pronoun target UNKNOWN), U3 (an operation truly outside the catalog stays UNKNOWN, flagged possible-external-effect, never permitted by absence of a rule), U4 (an unparseable clause isolated, others still observed), U5/U6 analogues (negation → PROHIBITED never REQUESTED; hypothetical premise never asserted as fact), A1 (an authority-claiming prefix never changes the real action's own reading — an equivalence falsifier, directly mirroring the GRANT_AUTHORITY_BINDING/GRANT_SESSION_CONTROL equivalence pattern from WU-2), C8 and the NQUIRY_SESSION_AUTHORITY fixture's own semantic-observation section (mined verbatim: 3 clauses, exact operation sequence, `DECISION_SUBSTITUTION_REQUESTED` on the AI-directed selection, `semantic_drift = True`), D3 (a secret-pattern span flagged and never duplicated elsewhere in the observation). Two fixtures (`PROCUREMENT.txt`, `NQUIRY_SESSION_AUTHORITY.txt`) are full R-01..R-12 walkthroughs, not single-relation fixtures — only their own "SEMANTIC OBSERVATION" sections are falsified here; their CANDIDATE DELTAS/RESULTS/COMPOSITION/CHAIN/CAPABILITY sections are later Work Units' scope, disclosed in §4.
- **MUTATION proof (manual, 7 guards):**
  1. Removed the `negated -> PROHIBITED` rule → 4 independent falsifiers failed (including the direct U5-analogue and the over-splitting adversarial case). Restored; byte-diff clean.
  2. Injected a fuzzy closest-match fallback (`None` → `REQUEST_QUESTION_ANALYSIS`) for an unrecognized verb → `test_unrecognized_verb_never_receives_a_closest_match_operation` failed exactly as intended (U1). Restored; byte-diff clean.
  3. Forced `decision_substitution_requested = False` unconditionally → 25 independent parametrized falsifiers failed across the whole real catalog. Restored; byte-diff clean.
  4. Reverted the quote-aware clause-split fix (removed the `(?!['\"])` lookahead) → reproduced the exact original bug (`test_a_named_in_scope_reference_resolves_the_target` failed with the identical truncated-clause symptom found during GREEN). Restored; byte-diff clean.
  5. Removed the `SemanticObservationUnavailable` raise for a wholly-unparseable intent → `test_a_wholly_unparseable_intent_raises_semantic_observation_unavailable` failed (`DID NOT RAISE`). Restored; byte-diff clean.
  6. Injected a fictional operation_id (`DELETE_WORKSPACE`) into the trigger vocabulary → the module's own import-time guard raised `ValueError` before any test could even collect, proving I-20 is enforced at load time, not merely at call time. Restored; byte-diff clean.
  7. Emptied the external-effect verb list → `test_an_operation_truly_outside_the_catalog_is_unknown_not_permitted` failed on its `possible_external_effect` assertion (U3). Restored; byte-diff clean.
  All 7 mutations confirmed via `sha256sum`/`diff -q` byte-identical restoration to the pre-mutation file after each; final restore hash `887c0cb702f1ab843c46def3b042f51185487652ed6de571b190d01c754c2f34` matched the pre-mutation baseline exactly.
- **PRESERVATION / REGRESSION.** Combined PCPG suite (`test_pcpg_simplix.py` + `test_pcpg_operation_index.py` + `test_pcpg_observation_ingress.py` + `test_pfc_f09_2_isolation_sweep.py`): **280 passed, 0 failed** (90 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN:** started only after `git status`/`git diff` confirmed the complete final tree (0 modified, 3 new files, all this Work Unit's own); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff — no tracked file touched), each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2192 passed, 15 skipped, 0 failed, in 2146.79s (0:35:46)** — exactly 2102 (WU-2's own closing count) + 90 (this Work Unit's falsifiers), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
clauses/actions        <- split from raw_intent by a fixed, versioned rule (RULE_SET_VERSION)  -- canonical,
                                                                                                    sourced (a/c)
modality/negation       <- closed marker-set detection over the clause text only               -- versioned SFE
                                                                                                    rule (c)
candidate_operation     <- the closed _OPERATION_TRIGGERS table, validated at import time        -- canonical,
                           against the REAL pcpg_operation_index (never re-implemented)              sourced (a)
target                  <- caller-supplied in_scope/out_of_scope reference maps, or UNKNOWN      -- canonical,
                           on an unresolved referring expression (never guessed)                    sourced (a),
                                                                                                    or honest UNKNOWN
decision_substitution_  <- pcpg_operation_index's own real, already-committed execution_class,   -- canonical,
  requested                read live, never duplicated or re-derived                                sourced (a)
semantic_purpose/        <- a closed bag-of-words/single-operation check, never synthesized text -- versioned SFE
  purpose_alignment                                                                                 rule (c),
                                                                                                    or honest None
possible_secret_content/ <- a narrow, disclosed pattern/verb detector, explicitly not the        -- versioned SFE
  possible_external_effect  FBR-PCPG-3 data-class classifier (still OPEN, untouched)                rule (c)
```
No CACHED value (every call is a fresh, pure computation; `test_same_input_gives_the_same_output_every_time` proves determinism without proving or needing a cache). No DUPLICATED value: `pcpg_operation_index` carries no natural-language trigger vocabulary of its own — this module adds genuinely new structure, without re-implementing `execution_class` (read, never recomputed). No PROMOTED value: nothing here is presented as authority, evidence, a decision, state or a live-resolved capability — `SemanticAction`/`SemanticObservation` are stratum-2 only, and no field name or docstring in the module claims otherwise. No BYPASSED value: the module has no consumer yet (R-06 not materialized); the static AST falsifier (mirroring WU-2's own pattern) plus a dynamic `sys.modules` check confirm no `ports`/`connection`/`db` parameter and no provider/network import exists anywhere in it, including every helper function. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-05 (the local SIMPLIX semantic sweep) is materialized and closed for its own, disclosed scope: the semantic observation (stratum 2) over a raw intent, against the real, already-closed operation catalog (FBR-PCPG-2), producing UNKNOWN wherever certainty is absent and never authority/state/capability. R-03 (Field reconstruction — a real, DB-backed canonical snapshot) and R-06 (candidate delta formation, consuming both R-03 and this Work Unit's R-05 output together) remain unmaterialized; SIMPLIX's `in_scope_references`/`out_of_scope_references` parameters are the disclosed wiring point a future Work Unit uses to connect a real R-03 snapshot, without requiring any change to this module's own pure-function shape. GOVERNANCE_ADMISSIBLE remains false for every observation (FBR-PCPG-4/HA-PCPG-1, unchanged by this Work Unit — nothing here touches capability). **Next First Broken Relation:** R-03 (Current Field reconstruction) or R-06 (candidate delta formation) — either is a legitimate next Work Unit under the existing authorization; R-06 cannot fully materialize until R-03 exists too (it consumes both). Neither is a Human Authority boundary or a future Field. No SEND path was begun.

## 3. Falsifier map (90 cases)

| Falsifier group | Cases | Proves |
|---|---|---|
| Clause splitting / span traceability | 5 | P-02; over-segmentation is safe, never under-segments across a negation boundary |
| Vocabulary completeness and closure (`test_every_real_catalog_operation_has_a_trigger_case_in_this_suite`, `test_the_real_trigger_resolves_to_its_real_operation` ×26) | 27 | every real catalog operation is reachable; the test table is exhaustive against the live catalog |
| Unmappable verb / operation outside the catalog (U1, U3) | 2 | I-04: never a closest-match guess; absence of a rule never becomes permission |
| Modality: negation, prohibition, hypothetical, conditional, assertion | 6 | R-05's own modality vocabulary; negated/hypothetical/prohibited never REQUESTED |
| A1 equivalence (authority-claiming prefix) | 2 | I-01/B-01: the claim is DATA, never changes the real action's own reading |
| Target resolution: UNKNOWN, named in-scope, OUT_OF_SCOPE (U2, D1-shaped) | 3 | I-04, I-05: never chosen by position; never reads outside the validated scope |
| Unparseable clause isolation and total failure (U4) | 2 | R-05's own FAILURE STATE: isolated UNKNOWN, or `SemanticObservationUnavailable` — never a partial guess |
| Requested executor and `DECISION_SUBSTITUTION_REQUESTED` (incl. ×26 exhaustive table) | 32 | 04 §4/§5's own stratum-2 vocabulary, computed from the real catalog, never guessed |
| NQUIRY_SESSION_AUTHORITY fixture (semantic-observation section only) | 1 | the fixture's own concrete, textual expected output, mined and matched exactly |
| Secret-pattern detection (D3) | 2 | a narrow, disclosed detector; the value never duplicated outside its own span |
| Purpose alignment (minimal, closed-vocabulary) | 4 | never synthesized text; `None` is the fail-closed default |
| Determinism, purity, no-egress (I-19, I-16, B-08, P-12) | 3 | same input → same output; no DB/provider import; no transitive provider import |
| Over-splitting safety (adversarial) | 2 | under-segmentation that would merge a prohibited action into a requested one never happens |

(Sum: 91 listed above by group double-counts one shared case; the collected, authoritative total is 90 — `pytest --collect-only` confirmed.)

## 4. Deliberate exclusions (not defects; later Work Units)

- R-03 (Current Field reconstruction): no real, DB-backed canonical snapshot producer exists yet in this codebase. SIMPLIX accepts `in_scope_references`/`out_of_scope_references` as optional, caller-supplied maps — the disclosed wiring point for a future Work Unit, requiring no change to this module's own shape.
- R-06 (candidate delta formation) and everything downstream (R-07 per-delta governance, R-08 composition, R-09 chain results, R-10 capability): no authority, state, membership, role, evidence or capability is derived anywhere in this module, per this Work Unit's own explicit instruction.
- FBR-PCPG-3 (prompt content → data class): GAP-11-006 stays OPEN. Only a narrow, disclosed secret-pattern detector and a closed external-effect verb list exist — neither is the general DC-01..07 classifier.
- No wiring into the PCPG observation ingress (`pcpg_observation.py`/`http_pcpg.py`): the ingress response still carries `governanceObservation: null`, honestly; consuming SIMPLIX is R-06's job (via R-03+R-05 together), not this one's.
- The PROCUREMENT-domain fixtures' own CANDIDATE DELTAS/RESULTS/COMPOSITION/CHAIN/CAPABILITY sections (S1–S3, C1–C7, D1/D2/D4/D5, M1–M5, T1–T5): these require R-03, R-06, R-07, R-08, R-09, R-10 and, for PROCUREMENT specifically, a FIXTURE_NON_PROOF domain producer (HA-PCPG-5) — none materialized here. Only each fixture's own "SEMANTIC OBSERVATION" section, where one exists and uses the real NQUIRY vocabulary, was mined as a falsifier.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-05 (the local SIMPLIX semantic sweep) is materialized for its own disclosed scope, independently falsified (90/90), mutation-proven (7/7 guards killed and restored, byte-identical restoration confirmed each time), and proven repository-wide preservation-clean (2192 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). Not committed, not tagged, not pushed.
