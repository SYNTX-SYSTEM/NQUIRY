# WU-PFC-PCPG-14 — FBR-PCPG-3: deterministic data-class classifier

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-14 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "PASS. Materialize FBR-PCPG-3 only." — full instruction quoted and honored clause-by-clause in §2–§7 below. Explicit boundary: do not begin R-13, do not materialize SEND, do not bind a provider, do not create a provider route, do not use an AI/model classifier, do not modify Architecture 26 unless a genuine contradiction is found (none was), do not invent the I-12 "Source status" producer. |
| Predecessor | `pfc-integration` `070b2ab18a3ea86a8760c3008b60d8191c4ec7ca` (`checkpoint-PFC-PCPG-13`, pushed; field-report-only, no code). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure computation over already-real `SemanticAction` fields). |
| E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-13`) | Confirmed by repository search: `grep` for `DataClass`/`DataClassification`/`classify_prompt_content` outside the RED text itself: zero hits. HD-29 (`checkpoint-PFC-PCPG-13`) names "Data Governance" among its own "at minimum" eligibility prerequisites; `WU-PFC-PCPG-13.md`'s own field reconstruction confirmed GAP-11-006/FBR-PCPG-3 as one of two active, independent blockers (the other, "Source" status/I-12, has no owning GAP/HA-PCPG-* row and is explicitly not built here, per instruction). **FBR-PCPG-3 is the next First Broken Relation.** No new bypass path found. |
| Authoritative relation reconstructed (step 1 of the proof cadence) | `00_FIELD.md` §12, verbatim: "FBR-PCPG-3: PROMPT CONTENT → DATA CLASS. No deterministic classifier exists for free text. GAP-11-006 is OPEN; the default is restrictive." HA-PCPG-4 (`00_FIELD.md` §13), verbatim, the ALREADY-DECIDED standing rule this Work Unit implements (no new Human Authority decision needed): "Deterministic, rule-based candidates. Ambiguous content takes the most restrictive class. No override." `11_SECURITY_PRIVACY_OBSERVABILITY.md` §25–26: the real DC-01..07 vocabulary and its own Data Class Handling Matrix. |
| Authorized delta (this Work Unit, disclosed scope) | A pure classifier consuming exactly three already-real, already-deterministic signals: `workspace_scoped` (caller-supplied, from R-01/R-02's own closed scope-validation fact), `SemanticAction.decision_substitution_requested` and `SemanticAction.possible_secret_content` (R-05's own already-real, already-deterministic fields — the latter's own module docstring already named this exact future relationship: "informational flags only, consumed ... by a later relation"). DC-01/DC-02 never produced (no real signal exists for either). No override, no model, no provider. |
| Must become true | A pure function `classify_prompt_content(action, *, workspace_scoped) -> DataClassification` exists: `candidate_classes` real and rule-fired; `unknown=True`/empty set when nothing fires (never a guessed class); `effective_handling_class` falls back to the ceiling (`AUDIT_SENSITIVE`) only for conservative handling, never asserted as a known fact; ambiguity resolves to `max()` of the real candidates. |
| Must remain true | `pcpg_simplix.SemanticAction` unchanged; every existing route, Command, migration and test; R-07 through R-12's own code files byte-unchanged (verified, §6). |
| Must remain impossible | DC-01/DC-02 ever produced from a guess; `unknown` content ever silently rewritten into a specific asserted class; any override/assignment path; any model or provider import; this classifier's output ever wired into R-07/R-08's governance decision in this Work Unit (explicitly out of scope — see §7). |
| Falsifiers | `tests/e2e/test_pcpg_data_classification.py`: 14 cases, covering every category the instruction required at minimum. |

## 2. Execution record

**1 RED (right reason).** The falsifier suite (14 cases) was written first, importing `DataClass`, `DataClassification`, `RESTRICTIVE_CEILING`, `classify_prompt_content` from `application.pcpg_data_classification`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_data_classification'` — the correct reason. All 14 falsifiers passed on the first real GREEN run.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no deterministic data-class producer exists for R-07's own future
                 Data Governance check (HD-29's own "at minimum" eligibility list) or
                 R-08's own disclosed-absent "data-class union" composition sub-check
CONSUMER         (future) R-07 per-delta governance, R-08 composition -- NOT wired in
                 this Work Unit (explicitly out of scope, see section 7)
PRODUCER         none (ABSENT -- break type (a))
FBR              FBR-PCPG-3 (00_FIELD.md section 12; GAP-11-006), data-class classifier
```

**3 HOME.** `00_FIELD.md` §12 (FBR-PCPG-3), §13 (HA-PCPG-4, the already-decided standing rule); `11_SECURITY_PRIVACY_OBSERVABILITY.md` §25–26 (DC-01..07, the Data Class Handling Matrix); `pcpg_simplix.py`'s own already-real `possible_secret_content`/`decision_substitution_requested` fields and their own module docstring, which already named this exact future relationship.

**4 REPAIR** (2 new files).
- `packages/application/pcpg_data_classification.py`: `DataClass` (an `IntEnum`, DC-01..07, ordinal = restrictiveness, an `[IMPLEMENTATION CHOICE]` disclosed and justified against §26's own monotonic prose — no other ordering exists in RED), `DataClassification`, `RESTRICTIVE_CEILING`, `classify_prompt_content()`.
- `tests/e2e/test_pcpg_data_classification.py`: 14 falsifiers (§3), covering the instruction's own required minimum list exactly.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_simplix` | NOT AFFECTED | Read-only consumption of two already-real fields; no field or vocabulary changed. |
| `pcpg_delta_evaluation` (R-07) / `pcpg_composed_effect` (R-08) / `pcpg_chain_results` (R-09) / `pcpg_capability` (R-10) / `pcpg_eligible_content` (R-11) / `pcpg_actor_projection` (R-12) | NOT AFFECTED, BYTE-IDENTICAL | `git diff --stat` against all six files: empty (§6). This classifier is not wired into any of them in this Work Unit. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched. |
| `ai_gateway` / provider path / model path | NOT AFFECTED | No import, no call (static AST falsifier, §3, extended this time to also forbid `model`/`torch`/`transformers` imports). |
| `docs/architecture/` (RED) | NOT TOUCHED | `git diff --stat` against `docs/architecture/`: empty. No contradiction was found requiring one. |

**6–9 PROOFS** (progressive cadence: LOCAL → AFFECTED, no full-repository regression — the delta touches no global invariant).
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Producer proof: `test_workspace_scoped_alone_is_an_unambiguous_low_restriction_result`, `test_possible_secret_content_alone_no_workspace_scope_is_unambiguous_high_restriction`, `test_provenance_cites_exactly_the_signals_that_fired`.
- Adversarial proof: `test_overlapping_signals_produce_multiple_real_candidates` + `test_ambiguity_resolves_to_the_most_restrictive_candidate` (the candidate SET vs. its RESOLUTION, proven separately); `test_decision_substitution_alone_resolves_to_sensitive_operational_not_escalated` (never escalates beyond what actually fired); `test_unknown_when_no_real_signal_fires_never_a_guessed_class` + `test_unknown_content_still_gets_the_restrictive_ceiling_for_handling` (the honest-report vs. conservative-handling distinction, proven on both sides); `test_empty_content_with_no_workspace_scope_is_also_unknown`; `test_the_module_exposes_no_override_or_assignment_function` (static AST, HA-PCPG-4's own "No override"); `test_the_module_touches_no_database_no_provider_and_no_model` (static AST, extended for `model`/`torch`/`transformers`).
- **MUTATION proof (manual, 4 guards, local falsifier suite only):**
  1. Weakened the restrictive ordering (reordered `SENSITIVE_OPERATIONAL`/`SECURITY_SENSITIVE`/`AUDIT_SENSITIVE` ordinals) → 2 falsifiers failed. Restored.
  2. Neutralized the `decision_substitution_requested` signal (`if False and ...`) → 2 falsifiers failed. Restored.
  3. Replaced the honest `unknown=True`/empty-set branch with a guessed `DataClass.INTERNAL` → 4 falsifiers failed. Restored.
  4. Weakened the handling-ceiling fallback from `AUDIT_SENSITIVE` to `DataClass.PUBLIC` → 1 falsifier failed. Restored.
  Final restore hash `ba5f17a80147ad67320e5d71a2363bf504fe6d3d42c7083c37b7c7c6b5a48487` confirmed byte-identical to the pre-mutation baseline after every mutation; all 14 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **412 passed, 753 deselected, 0 failed** (14 data_classification + 13 actor_projection + 17 capability + 25 chain_results + 11 composed_effect + 26 delta_evaluation + 69 candidate_deltas + 15 field_pulse + 17 field_snapshot + 91 simplix + 78 operation_index + 28 observation_ingress + 8 eligible_content); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed for this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a pure, no-I/O, no-model, no-provider application module with no new persistence, no schema change, no session/authority/capability-resolution touch, and no cross-field protocol change — none of the enumerated full-regression triggers apply, and the dependency graph does not require widening (step 7 of the proof cadence: not required).

**10 INVERSE SWEEP (E6).**
```text
candidate_classes      <- exactly the real, rule-fired signals (workspace_scoped,          -- canonical, sourced (a)
                           action.decision_substitution_requested,
                           action.possible_secret_content), each already real and
                           already deterministic from a closed relation
most_restrictive_       <- max() over candidate_classes when non-empty; None when          -- versioned SFE rule (c),
  candidate / unknown       empty -- never a guessed class for the empty case                  proven both sides
effective_handling_     <- most_restrictive_candidate when known; RESTRICTIVE_CEILING      -- versioned SFE rule (c);
  class                     (conservative upper bound, not an asserted fact) when              GAP-11-006's own
                           unknown                                                             cited default
provenance              <- the exact cited signal name(s) that fired, empty iff unknown   -- canonical, sourced (a)
```
No CACHED value: every call recomputes from its own given arguments (`test_same_inputs_give_the_same_classification_every_time` proves determinism without a cache). No DUPLICATED value: reads `SemanticAction`'s own two fields directly, never re-deriving SIMPLIX's own secret-pattern/decision-substitution logic a second way. No PROMOTED value: `DataClassification` is presented exactly as a derived classification fact — `CLASSIFICATION != AUTHORITY`, `CLASSIFICATION != PROVIDER ELIGIBILITY`, `DATA CLASS != SEND PERMISSION`, `UNKNOWN != PERMISSION` — nothing in this module or its falsifiers treats the output as a grant. No BYPASSED value: no consumer exists yet in this Field (not wired into R-07/R-08, §7); the static AST falsifier confirms no `ports`/`connection`/`db` parameter and no provider/model/`ai_gateway` import exists anywhere in the module, and a second static falsifier confirms no override/assignment function or parameter exists. **VERDICT: CLEAN.**

## 3. Falsifier map (14 cases, against the instruction's own required minimum list)

| Required category | Falsifier(s) |
|---|---|
| one unambiguous low-restriction input | `test_workspace_scoped_alone_is_an_unambiguous_low_restriction_result` |
| one unambiguous high-restriction input | `test_possible_secret_content_alone_no_workspace_scope_is_unambiguous_high_restriction` |
| overlapping classifications | `test_overlapping_signals_produce_multiple_real_candidates` |
| ambiguity resolving to the most restrictive class | `test_ambiguity_resolves_to_the_most_restrictive_candidate`, `test_decision_substitution_alone_resolves_to_sensitive_operational_not_escalated` |
| unknown/unclassifiable content | `test_unknown_when_no_real_signal_fires_never_a_guessed_class`, `test_unknown_content_still_gets_the_restrictive_ceiling_for_handling` |
| empty content where applicable | `test_empty_content_with_no_workspace_scope_is_also_unknown` |
| classification provenance | `test_provenance_cites_exactly_the_signals_that_fired`, `test_provenance_is_empty_exactly_when_unknown` |
| no override path | `test_the_module_exposes_no_override_or_assignment_function` |
| no model/provider dependency | `test_the_module_touches_no_database_no_provider_and_no_model` |
| deterministic replay on identical input | `test_same_inputs_give_the_same_classification_every_time` |
| mutation that weakens restrictive ordering must be caught | `test_restrictive_ordering_is_exactly_dc01_through_dc07_ascending` (proven directly by mutation 1, §6–9) |

## 4. Deliberate exclusions (not defects; later Work Units, or genuinely out of this Field)

- DC-01 PUBLIC, DC-02 INTERNAL: never produced — no real, deterministic signal anywhere in this codebase asserts "safe to treat as public" or "merely internal" for free-text prompt content.
- `action.possible_external_effect` and `action.target`: deliberately not used as classification signals — neither has a citable, non-speculative mapping to a specific DC class in `11` §25–26 (using them would mean inventing a new heuristic, which HA-PCPG-4 forbids).
- **I-12 "Source status"/provenance: NOT built, per explicit instruction.** Checked directly: this classifier's three real signals (workspace scope, decision substitution, possible secret content) require no source-status/provenance input at all — FBR-PCPG-3 closes honestly without I-12. The STOP condition in the instruction ("if FBR-PCPG-3 cannot close honestly without I-12 becoming authoritative input") was evaluated and did not trigger.
- FBR-PCPG-5 (provider route eligibility): untouched, as instructed — no file under any provider-route-shaped module was created or touched.
- Wiring this classifier into R-07's per-delta governance evaluation or R-08's composition sub-checks: the "narrowest legitimate producer" instruction scoped this Work Unit to the classifier alone. §7 reconstructs what this does and does not change.

## 5. R-13 / SEND / provider confirmations

- **R-13 not begun.** No file under any SEND-gate-shaped module was created or touched.
- **SEND not materialized.** No provider-facing payload, manifest, or route-selection code exists anywhere in this commit.
- **No provider bound, no provider route created, no model/AI classifier used.** `check_provider_sdk_imports.py` PASS; the module's own static AST falsifier additionally forbids `model`/`torch`/`transformers` imports, beyond the standard provider-import list every prior relation's own falsifier already checks.
- **Architecture 26 not modified.** No genuine architecture contradiction was discovered; `git diff --stat` against `docs/architecture/`: empty.

## 6. Field reconstruction: R-07 → R-08 → R-09 → R-10 → R-11 → R-12 (step 6 of the proof cadence)

**Mechanical fact, not an inference:** `git diff --stat -- packages/application/pcpg_delta_evaluation.py packages/application/pcpg_composed_effect.py packages/application/pcpg_chain_results.py packages/application/pcpg_capability.py packages/application/pcpg_eligible_content.py packages/application/pcpg_actor_projection.py` against `checkpoint-PFC-PCPG-13` is **empty**. Every one of R-07 through R-12's own producer files is byte-identical to before this Work Unit. Their own reachability conclusions, already independently proven in `WU-PFC-PCPG-10.md`/`WU-PFC-PCPG-12.md`/`WU-PFC-PCPG-13.md`, are therefore **mechanically unchanged, not merely reasoned to be unchanged**:

| Value | Status after this Work Unit | Why |
|---|---|---|
| `GOVERNANCE_ADMISSIBLE` | **Still fully UNREACHABLE. Unchanged.** | R-07's `OPERATION_CLASS_NOT_ADMITTED` reason for every `PROVIDER_COMPUTATION` delta is still unconditional code (byte-identical) — HD-29's conditional admission was recorded as a Human Authority decision but never wired into R-07's own evaluation in any Work Unit to date. R-08's own mutual-exclusivity finding (`WU-PFC-PCPG-10.md` §2a) is also untouched: `compose_effect()` is byte-identical. |
| `PROVIDER_EXECUTABLE` | **Still fully UNREACHABLE. Unchanged.** | `pcpg_capability.py` is byte-identical; `NO_ELIGIBLE_PROVIDER_ROUTE` remains unconditional, governed by the independent, untouched FBR-PCPG-5 (`HARD-DEP-002`/`GAP-08-002/008`). |
| `CAN_SEND` | **Still fully UNREACHABLE. Unchanged.** | Compound consequence of both rows above; neither operand changed. |

**No positive path was manufactured.** This classifier exists now as a real, falsified, mutation-proven producer — available for a future Work Unit to wire in — but wiring it in is a distinct, not-yet-begun act with its own First Broken Relation, named below.

**The next FBR this reconstruction exposes:** binding HD-29's conditionally-admitted `PROVIDER_COMPUTATION` operation class, together with this Work Unit's own data classifier, into R-07's per-delta governance evaluation (replacing the current unconditional `OPERATION_CLASS_NOT_ADMITTED` reason with HD-29's own conditional logic, and consuming `classify_prompt_content`'s own output as one of the "Data Governance" inputs HD-29's own decision names). Even that Work Unit would **not** make `ALLOWED`/`CAN_SEND` reachable by itself: the "Source" status/I-12 prerequisite (still no producer, `WU-PFC-PCPG-13.md` §5) and FBR-PCPG-5 (provider route, independent) would remain. **This Work Unit does not begin that wiring** — naming it is as far as the field reconstruction goes; the instruction's own proof cadence (step 6, "reconstruct the field") asked for this report, not the next materialization.

## 7. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** FBR-PCPG-3 (deterministic data-class classifier, three real signals, DC-01/DC-02 disclosed never-produced, I-12 confirmed not required) is materialized for its own disclosed scope, independently falsified (14/14, covering every required category), mutation-proven (4/4 guards killed and restored, byte-identical after restore), and proven affected-suite-clean (412 passed / 0 failed, full combined PCPG suite). `GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND` remain fully unreachable, mechanically unchanged (R-07 through R-12's own files are byte-identical to `checkpoint-PFC-PCPG-13`) — no positive path was manufactured. R-13 not begun; SEND not materialized; no provider bound; no provider route created; no model used; Architecture 26 not modified; I-12 not invented. The next FBR (wiring HD-29 and this classifier into R-07) is named, not begun.
