# WU-PFC-PCPG-15 — binding HD-29 + FBR-PCPG-3 into R-07's per-delta governance evaluation

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-15 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization (repair of an already-closed module, R-07) |
| Human authorization | "PASS. Continue with the next active PCPG relation only." Full instruction honored clause-by-clause below. Explicit boundary, all honored: do not begin R-13; do not materialize SEND; do not bind a provider; do not create a provider route; do not invent I-12/Source provenance; do not modify Architecture 26 (none touched; no contradiction found); the goal is NOT to make `CAN_SEND` true; preserve all independent blockers (I-12, FBR-PCPG-5) as OPEN. |
| Predecessor | `pfc-integration` `e4e75a6f038da0b838df6840118a5e4b076d4361` (`checkpoint-PFC-PCPG-14`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (pure logic change to an already-real, pure function). |
| Step 1 — exact current R-07 producer and FAILURE STATE reconstructed | `pcpg_delta_evaluation.evaluate_deltas()` (R-07), unchanged since `checkpoint-PFC-PCPG-7` (`eb0e138`, verified via `git log` before this Work Unit). FAILURE STATE, verbatim (R-07's own module docstring, carried forward): "a delta with no authoritative producer for its authority gives `INDETERMINATE` with reason `NO_AUTHORITATIVE_PRODUCER`." |
| Step 2 — historical unconditional branch identified | `elif delta.execution_class is ExecutionClass.PROVIDER_COMPUTATION: result, reason = Result.GOVERNANCE_BOUNDARY, OPERATION_CLASS_NOT_ADMITTED` — unconditional for every `PROVIDER_COMPUTATION` delta, regardless of operation identity or any other fact, since `checkpoint-PFC-PCPG-7`. |
| Step 3 — narrowest binding determined | A caller-supplied `data_classifications_by_delta_id: Mapping[str, DataClassification] \| None = None` parameter, the SAME established pattern this module's own `flags_by_delta_id` already uses for R-05's `DECISION_SUBSTITUTION_REQUESTED` flag — R-07 never re-derives a fact a real producer already computed. The admitted-operation check reuses `snapshot.ai_contracts_admitted` (R-03's own already-real per-call fact, already passed into `evaluate_deltas`) plus a small, duplicated, disclosed operation→contract table (duplicating `pcpg_capability.py`'s own identical table to avoid a circular import — that module already imports FROM this one). No change to `CandidateDelta` (R-06, untouched), no change to `evaluate_deltas`'s own positional signature (only an additional keyword-only parameter, backward compatible with every existing caller). |

## 2. Execution record

**4 CONSUME THE DETERMINISTIC DATA-CLASS RESULT ONLY WHERE THE AUTHORITATIVE RELATION REQUIRES IT.** The rebuilt `PROVIDER_COMPUTATION` branch is now a real, three-step, cited decision:

1. **Operation-class admission** (unchanged reason for the non-admitted case): `delta.operation` must map to one of the two real `PROVIDER_COMPUTATION` operations in `pcpg_operation_index.py`'s own closed catalog (FBR-PCPG-2, CLOSED), and that operation's own contract ID must be a member of `snapshot.ai_contracts_admitted`. If not: `GOVERNANCE_BOUNDARY`/`OPERATION_CLASS_NOT_ADMITTED` — the literally correct, still-applicable historical reason for any operation HD-29 itself does not name.
2. **Data Governance** (HD-29's own named prerequisite, FBR-PCPG-3's real producer consumed): if no classification was supplied, or the supplied one honestly reports `unknown=True` — `INDETERMINATE`, reason `DATA_GOVERNANCE_NOT_MATERIALIZED` or `DATA_CLASS_UNKNOWN` respectively. HA-PCPG-4's own "UNKNOWN must remain UNKNOWN... never guessed" is preserved exactly; neither reason is ever treated as a path toward `ALLOWED`.
3. **Provider-eligibility-by-class policy** (a genuinely independent, already-OPEN gap this Work Unit discovers R-07 itself now depends on, not invents): a KNOWN classification still cannot cross into a provider computation, because `11_SECURITY_PRIVACY_OBSERVABILITY.md` §26's own Handling Matrix conditions every class's own AI/Provider Eligibility on a per-class policy with no producer anywhere in this codebase (`GAP-08-002/008`, FBR-PCPG-5's own cited gap) — `DATA_BOUNDARY` (§6's own verbatim definition: "the inputs cannot lawfully cross (11)"), reason `PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED`.

`ALLOWED` is never assigned by any branch of this decision — not structurally reachable, not merely untested.

**5 PRESERVE ALL INDEPENDENT BLOCKERS.** I-12 (Source status/provenance) is never referenced, imported or consulted anywhere in this module (proven directly, §3, `test_the_module_never_references_source_status_or_proof_ceiling`). FBR-PCPG-5 (provider route) is untouched: no file under any provider-route-shaped module was created or touched; `git diff --stat` confirms only `pcpg_delta_evaluation.py` and its own test file changed (§6). **The STOP condition ("if R-07 cannot honestly derive an ALLOWED state without I-12") did not trigger**: R-07's own decision bottoms out at `DATA_BOUNDARY`/GAP-08-008 — an independently-open, already-named gap — before I-12 would ever need to be consulted. I-12 therefore never becomes a required input to this relation's own closure.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   R-07's own decision for an admitted PROVIDER_COMPUTATION delta was a stale,
                 unconditional placeholder that no longer reflected HD-29's own conditional
                 admission, and could not consume FBR-PCPG-3's real output at all
CONSUMER         R-08 through R-12 (read R-07's own result/reason generically; none needed
                 code changes -- confirmed, section 6)
PRODUCER         existed but stale (REPAIR type (b): a real producer whose own justification
                 no longer matched the current, Human-Authority-updated Field)
FBR              the binding of HD-29 + FBR-PCPG-3 into R-07, the next relation this field
                 reconstruction names after FBR-PCPG-3's own closure (WU-PFC-PCPG-14 §6)
```

**3 HOME.** `HUMAN_DECISIONS.md` HD-29 (`checkpoint-PFC-PCPG-13`); `pcpg_data_classification.py` FBR-PCPG-3 (`checkpoint-PFC-PCPG-14`); `04_OBSERVATION_RESULT.md` §6 (`DATA_BOUNDARY`'s own verbatim definition); `11_SECURITY_PRIVACY_OBSERVABILITY.md` §26 (the per-class eligibility policy gap); `00_FIELD.md` §12 (FBR-PCPG-5, `GAP-08-002/008`, cited verbatim).

**REPAIR** (2 files modified, both already-closed: `pcpg_delta_evaluation.py` at `checkpoint-PFC-PCPG-7`, `test_pcpg_delta_evaluation.py` at the same checkpoint).
- `packages/application/pcpg_delta_evaluation.py`: new constants `DATA_GOVERNANCE_NOT_MATERIALIZED`, `DATA_CLASS_UNKNOWN`, `PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED`, `_PROVIDER_COMPUTATION_CONTRACTS`; new `data_classifications_by_delta_id` parameter; the `PROVIDER_COMPUTATION` branch rebuilt as the three-step decision above. Module docstring rewritten to disclose the WU-PFC-PCPG-15 update in full, citing HD-29 and FBR-PCPG-3 by name.
- `tests/e2e/test_pcpg_delta_evaluation.py`: one genuinely stale test (`test_provider_computation_is_always_governance_boundary_never_allowed`, whose own title was no longer true post-HD-29) removed and replaced with 6 falsifiers covering each real branch of the new decision; 2 further falsifiers added (I-12 non-reference, downstream R-08 integration). All other 24 pre-existing falsifiers (including the DB-backed end-to-end test) required no change and still pass unmodified.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `pcpg_composed_effect` (R-08) / `pcpg_chain_results` (R-09) / `pcpg_capability` (R-10) / `pcpg_eligible_content` (R-11) / `pcpg_actor_projection` (R-12) | NOT AFFECTED, BYTE-IDENTICAL | `git diff --stat` against all five: empty (§6). Each already treats any non-`ALLOWED` result generically (`compose_effect`'s own filter is `result is Result.ALLOWED`; R-09's HAR filter already only answers `AUTHORITY_BOUNDARY`/`GOVERNANCE_BOUNDARY`, `DATA_BOUNDARY` deltas correctly get no HAR entry, already-disclosed WU-9 scope) — no code anywhere needed to learn about the two new reason codes. |
| `pcpg_candidate_deltas` (R-06) | NOT AFFECTED | No change to `CandidateDelta`'s own shape; the new parameter is supplied by R-07's own caller, not derived from R-06. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched. |
| `ai_gateway` / provider path / model path | NOT AFFECTED | No import, no call (static AST falsifier, unchanged, still passes). |
| `docs/architecture/` (RED) | NOT TOUCHED | `git diff --stat` against `docs/architecture/`: empty. No contradiction was found requiring one. |

**6–9 PROOFS** (progressive cadence: LOCAL → AFFECTED, no full-repository regression — the delta touches no global invariant).
- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Local falsifiers: 32/32 (31 non-DB + 1 DB-backed, run separately per the established DB-bootstrap pattern) — see §3 for the mapping against every category the instruction required at minimum.
- **MUTATION proof (manual, 3 guards, local falsifier suite only):**
  1. Restored the historical unconditional `OPERATION_CLASS_NOT_ADMITTED` (the entire three-step decision replaced by the old one-liner) → 4 falsifiers failed. Restored.
  2. Treated a known classification as authority (the `DATA_BOUNDARY` branch replaced with `Result.ALLOWED, None`) → 3 falsifiers failed, **including the downstream R-08 integration falsifier** (`test_even_the_best_case_provider_delta_never_survives_into_r08s_retained_set`), directly proving a classification-as-authority leak would have reached R-08's own real `compose_effect` and produced a non-empty retained set. Restored.
  3. Weakened the admitted-operation check to ignore `snapshot.ai_contracts_admitted` (checked only the operation→contract table, not the per-call admitted set) → 1 falsifier failed. Restored.
  Final restore hash `08774b5cabc0abfb0efa26b5f6ac2c3354fa1cd21f7c1895f342d616464dd442` confirmed byte-identical to the pre-mutation baseline after every mutation; all 32 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **419 passed, 753 deselected, 0 failed** (33 delta_evaluation [32 + the DB-backed end-to-end test deselected from the local-only run but included here] + 14 data_classification + 13 actor_projection + 17 capability + 25 chain_results + 11 composed_effect + 69 candidate_deltas + 15 field_pulse + 17 field_snapshot + 91 simplix + 78 operation_index + 28 observation_ingress + 8 eligible_content); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed for this Work Unit, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this repair is a pure, no-I/O logic change to a single application module's own already-real decision function, with no new persistence, no schema change, no session/authority/capability-resolution infrastructure touch, and no cross-field protocol change — none of the enumerated full-regression triggers apply.

**10 INVERSE SWEEP (E6).**
```text
PROVIDER_COMPUTATION   <- snapshot.ai_contracts_admitted (R-03's own real, per-call fact) +   -- canonical, sourced (a)
  admission                a closed, grepped operation->contract table (FBR-PCPG-2's own
                           closed catalog) -- never a guess, never hardcoded
Data Governance         <- classify_prompt_content (FBR-PCPG-3, CLOSED), consumed via the      -- canonical, sourced (a)
                           same caller-supplied-mapping pattern flags_by_delta_id already
                           established
PROVIDER_ELIGIBILITY_    <- GAP-08-002/008, FBR-PCPG-5's own cited, already-OPEN gap --         -- disclosed absence,
  POLICY_NOT_MATERIALIZED   named, never fabricated, never silently worked around                  never fabricated
I-12 Source status       <- never referenced (static falsifier, section 3)                      -- disclosed absence,
                                                                                                     never invented
```
No CACHED value: every call recomputes from its own given arguments (`test_same_inputs_give_the_same_records_every_time`, unchanged, still passes). No DUPLICATED value: reads `snapshot.ai_contracts_admitted` and the caller-supplied classification directly, never re-deriving either. No PROMOTED value: `CLASSIFICATION != AUTHORITY` proven directly (`test_an_admitted_operation_with_a_known_classification_is_data_boundary_not_allowed`); operation-class admission is never treated as authority; `GOVERNANCE_ADMISSIBLE != CAN_SEND` — this module computes neither. No BYPASSED value: the downstream integration falsifier (§6–9, mutation 2) proves directly, against the real unmodified R-08, that no admitted/classified delta reaches a non-empty, composable retained set. **VERDICT: CLEAN.**

## 3. Falsifier map (against the instruction's own required minimum list)

| Required category | Falsifier(s) |
|---|---|
| provider computation still denied when HD-29 conditions are not satisfied | `test_a_provider_computation_operation_hd29_does_not_admit_is_still_governance_boundary`, `test_an_admitted_operation_whose_contract_is_not_in_the_snapshot_is_governance_boundary` |
| admitted operation class is not equivalent to authority | `test_an_admitted_operation_with_a_known_classification_is_data_boundary_not_allowed` |
| restrictive/unknown data class cannot be weakened | `test_an_admitted_operation_with_an_unknown_classification_is_indeterminate_never_allowed`, `test_a_more_restrictive_known_classification_still_never_reaches_allowed` |
| classifier UNKNOWN never becomes permission | `test_an_admitted_operation_with_an_unknown_classification_is_indeterminate_never_allowed` |
| no direct USER INPUT → PROVIDER path | `test_the_module_touches_no_database_and_no_provider` (unchanged, still passes); `ALLOWED` structurally never assigned (§2) |
| no provider route exists | `git diff --stat`: no provider-route-shaped file touched (§5) |
| I-12 absence remains observable where required | `test_the_module_never_references_source_status_or_proof_ceiling` |
| downstream CAN_SEND remains false unless every independent gate is satisfied | `test_even_the_best_case_provider_delta_never_survives_into_r08s_retained_set` |
| mutation restoring unconditional OPERATION_CLASS_NOT_ADMITTED is caught | mutation 1, §6–9 |
| mutation treating classification as authority is caught | mutation 2, §6–9 |

## 4. R-13 / SEND / provider / I-12 confirmations

- **R-13 not begun. SEND not materialized. No provider bound. No provider route created. No model used.** Unchanged from every prior PCPG Work Unit's own confirmation.
- **I-12 not invented.** Checked directly (static falsifier) and architecturally (§5): R-07's own decision never needs it, bottoming out at the independent GAP-08-008 first.
- **Architecture 26 not modified.** `git diff --stat` against `docs/architecture/`: empty. No contradiction was found requiring one.

## 5. Field reconstruction: R-07 → R-08 → R-09 → R-10 → R-11 → R-12

| Value | Status |
|---|---|
| **R-07 `ALLOWED` path** | **UNREACHABLE.** The decision is now genuinely conditional (branches on real, admitted-operation and real-classification facts, replacing the old unconditional placeholder) — but no branch of the rebuilt decision ever assigns `Result.ALLOWED`; it is not merely untested, it is not assigned anywhere in the code. |
| **`GOVERNANCE_ADMISSIBLE`** | **UNREACHABLE. Unchanged.** `pcpg_capability.py` is byte-identical (§6–9 propagation table). Bullet 1 ("MLT non-empty") still fails unconditionally, since R-08's retained set is still always empty (no delta is ever `ALLOWED`). |
| **`PROVIDER_EXECUTABLE`** | **UNREACHABLE. Unchanged.** `NO_ELIGIBLE_PROVIDER_ROUTE` remains unconditional — governed by the independent, untouched FBR-PCPG-5. |
| **`CAN_SEND`** | **UNREACHABLE. Unchanged.** Compound of both rows above; neither operand changed. |

No positive path was manufactured or forced. The goal stated by the instruction — "materialize the next legitimate governance relation so that R-07 can consume already-authoritative facts rather than its historical unconditional fail-closed placeholder" — is met: R-07's own reasons for every `PROVIDER_COMPUTATION` delta are now real, cited, and specific (`OPERATION_CLASS_NOT_ADMITTED` / `DATA_GOVERNANCE_NOT_MATERIALIZED` / `DATA_CLASS_UNKNOWN` / `PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED`), never a blanket placeholder — while the Field's own operationally-reachable surface is provably, mechanically unchanged.

**The exact next First Broken Relation:** **FBR-PCPG-5 — ADMITTED COMPUTATION → ELIGIBLE PROVIDER ROUTE** (`00_FIELD.md` §12, `GAP-08-002/008`, `HARD-DEP-002`). This Work Unit's own new code directly, mechanically names it as the real reason a known-classified, admitted-operation delta still cannot reach `ALLOWED` (`PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED`) — it is the single gap R-07's own decision now bottoms out on. It is explicitly preserved as independent and untouched in this Work Unit, per instruction. **I-12 (Source status/provenance)** remains a second, structurally still-open prerequisite named by HD-29's own text, with no owning GAP/HA-PCPG-* row in the RED text today (`WU-PFC-PCPG-13.md` §5) — not reached by R-07's own decision path, but still open for any future relation that might need it. **This Work Unit does not proceed into FBR-PCPG-5** — naming it is as far as this field reconstruction goes, per the instruction's own explicit "do not proceed into that next FBR automatically."

## 6. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** HD-29 and FBR-PCPG-3 are bound into R-07's per-delta governance evaluation for the narrowest honest scope: the decision is now conditional and cites real, specific reasons, independently falsified (32/32, covering every required category), mutation-proven (3/3 guards killed and restored, byte-identical after restore, one mutation caught directly by a downstream R-08 integration falsifier), and proven affected-suite-clean (419 passed / 0 failed, full combined PCPG suite). `GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND` remain fully unreachable, mechanically unchanged (R-08 through R-12's own files are byte-identical to `checkpoint-PFC-PCPG-14`) — no positive path was manufactured. R-13 not begun; SEND not materialized; no provider bound; no provider route created; I-12 not invented; Architecture 26 not modified. The next FBR (FBR-PCPG-5, provider route eligibility) is named, not begun.
