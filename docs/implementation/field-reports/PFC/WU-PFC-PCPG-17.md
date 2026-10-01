# WU-PFC-PCPG-17 — I-12 composed proof ceiling → R-12 actor-safe projection

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-17 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization (repair of one already-closed module: R-12) |
| Human authorization | "PASS. Authorize the narrowest implementation Work Unit: WU-PFC-PCPG-17." Full instruction honored clause-by-clause below. |
| Predecessor | `pfc-integration` `6c0ea91878dd35e807e5b9f9dabc8feed9b00a18` (`checkpoint-PFC-PCPG-16`, pushed). |
| Authoritative relation materialized, exactly as directed | `ComposedEffect.composed_proof_ceiling` (R-08) → **directly** → `ActorSafeProjection.composed_proof_ceiling` (R-12). **Not** routed through R-09 `ChainResult`, R-10 `Capability`, or R-11 `EligibleContentSet` — none of them owns the proof-ceiling semantic, confirmed by the companion discovery pass (prior turn, not a committed file) against the real, freshly-read code of all five relations. |
| Preservation confirmed | `git diff --stat` against `pcpg_field_snapshot.py` (R-03), `pcpg_candidate_deltas.py` (R-06), `pcpg_delta_evaluation.py` (R-07), `pcpg_composed_effect.py` (R-08), `pcpg_chain_results.py` (R-09), `pcpg_capability.py` (R-10), `pcpg_eligible_content.py` (R-11): **empty**. All seven byte-identical to `checkpoint-PFC-PCPG-16`. **R-08 itself needed no change** — `composed_proof_ceiling` was already real there since `checkpoint-PFC-PCPG-16`. |

## 2. Execution record

**Narrowest intended delta, honored exactly:** `packages/application/pcpg_actor_projection.py` only (plus its own test file — an "unavoidable mechanical call-site change", explicitly anticipated by the instruction, since the module's own 5-parameter, all-non-optional signature structurally enforces completeness and the test file's own direct calls needed the new argument).

- `derive_actor_safe_projection()` gains a sixth, non-optional parameter: `composed_effect: ComposedEffect`.
- `ActorSafeProjection` gains one field: `composed_proof_ceiling: str | None`.
- The value is copied by exactly one line: `composed_proof_ceiling=composed_effect.composed_proof_ceiling` — no computation, no inference, no derivation, no fallback. Proven directly, not merely asserted (§3, `test_r12_reads_the_ceiling_only_from_composed_effect_never_elsewhere`): the AST of the real `ActorSafeProjection(...)` call site is inspected, and the `composed_proof_ceiling=` keyword's own value must be exactly the attribute expression `composed_effect.composed_proof_ceiling` — a different expression shape fails the falsifier, not just a different runtime value.

**Laws preserved, each checked directly:**
- `R-12 MAY PROJECT != R-12 MAY RECOMPUTE` — the AST falsifier above.
- `PER-DELTA CEILING != COMPOSED CEILING` — `test_per_delta_session_proof_ceiling_remains_independently_present` constructs a delta with `session_proof_ceiling="FIXTURE_NON_PROOF"` inside a `composed_effect` whose own `composed_proof_ceiling="GOVERNED"`, and proves both values survive independently, unmerged.
- `UNKNOWN CEILING != GOVERNED` — `test_none_from_r08_remains_none_in_r12`.
- `PROOF CEILING != GOVERNANCE RESULT / CAPABILITY / PROVIDER ELIGIBILITY / SEND AUTHORITY` — `Capability`, `EligibleContentSet`, and the SEND path are untouched (confirmed, §1); the new field is sourced from neither.
- `SESSION-LEVEL I-12 != FULL I-12`; `PARTIAL I-12 != I-12 COMPLETE` — only `"FIXTURE_NON_PROOF"` / `"GOVERNED"` / `None` are ever projected; the module docstring states explicitly what is still not claimed.

## 3. Falsifier map (against the instruction's own required minimum list)

| Required category | Falsifier(s) |
|---|---|
| 1. FIXTURE_NON_PROOF from R-08 reaches R-12 unchanged | `test_fixture_non_proof_from_r08_reaches_r12_unchanged` |
| 2. GOVERNED from R-08 reaches R-12 unchanged | `test_governed_from_r08_reaches_r12_unchanged` |
| 3. None from R-08 remains None in R-12 | `test_none_from_r08_remains_none_in_r12` |
| 4. R-12 does not recompute the ceiling from delta_records | `test_r12_reads_the_ceiling_only_from_composed_effect_never_elsewhere` |
| 5. R-12 does not default an unknown ceiling to GOVERNED | `test_none_from_r08_remains_none_in_r12` (same falsifier, explicit `!= "GOVERNED"` assertion) |
| 6. R-12 does not derive the ceiling from ChainResult | `test_r12_reads_the_ceiling_only_from_composed_effect_never_elsewhere` |
| 7. R-12 does not derive the ceiling from Capability | `test_r12_reads_the_ceiling_only_from_composed_effect_never_elsewhere` |
| 8. per-delta session_proof_ceiling remains independently present | `test_per_delta_session_proof_ceiling_remains_independently_present` |
| 9. changing only ComposedEffect.composed_proof_ceiling changes only the projected aggregate ceiling | `test_changing_only_composed_effect_changes_only_the_projected_ceiling` |
| 10. no source provenance is added | `test_no_source_provenance_or_provider_output_proof_class_is_invented` |
| 11. no provider-output proof class is invented | same falsifier, same source list |
| 12. FBR-PCPG-5 remains OPEN / BLOCKED_EXTERNAL | `git diff --stat` on `pcpg_capability.py`: empty (§1) |
| 13. PROVIDER_EXECUTABLE remains false | same — R-10 untouched |
| 14. CAN_SEND remains false | same — R-10 untouched |
| 15. R-13 remains NOT STARTED | no SEND-gate-shaped file created or touched |

Plus the pre-existing `test_projection_adds_no_field_beyond_the_seven_named_items` (updated to the now-8-field shape, since R-12's own 7th named OUTPUT item is now covered) and `test_two_different_observations_project_independently_no_shared_mutable_state` (updated call site only, logic unchanged).

## 4. R-13 / SEND / provider / FBR-PCPG-5 confirmations

- **R-13 not begun. SEND not materialized. No provider bound. No provider routing touched.**
- **FBR-PCPG-5 preserved exactly as OPEN / BLOCKED_EXTERNAL.** `pcpg_capability.py` byte-unchanged.
- **Architecture 26 not modified.** `git diff --stat` against `docs/architecture/`: empty.

## 5. Proofs (progressive cadence)

- Local: `ruff check` / `ruff format --check` clean; `mypy` 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Local falsifiers: **20 passed** (13 pre-existing, unmodified in logic, + 7 new).
- **MUTATION proof (manual, 2 guards, local falsifier suite only):**
  1. Defaulted an unknown ceiling to `"GOVERNED"` (`composed_effect.composed_proof_ceiling or "GOVERNED"`) → 2 falsifiers failed, **including the AST purity check** (the `or` expression is no longer a bare attribute access, caught structurally, not just by value). Restored.
  2. Recomputed the ceiling from `delta_records[0].session_proof_ceiling` instead of reading `composed_effect` → 5 falsifiers failed. Restored.
  Final restore hash `724d26d420ed02384c2fe2e25700d23f782727e8cf8e87c73d93d4ffa1fda179` confirmed byte-identical to the pre-mutation baseline after every mutation; all 20 local falsifiers green on the restored file.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **438 passed, 753 deselected, 0 failed** (all 13 pcpg test files); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after. Confirmed by `grep`: no other file in the repository calls `derive_actor_safe_projection` or constructs `ActorSafeProjection` directly — the signature change is fully contained.
- No full-repository regression performed, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a single-module, additive, backward-incompatible-only-at-its-own-call-sites wiring change, with no new persistence, no schema change, no session/authority/capability-resolution touch, and no cross-field protocol change.

## 6. Field reconstruction: R-08 → R-12

**Mechanical fact:** `git diff --stat` against R-03, R-06, R-07, R-08, R-09, R-10, R-11's own seven files is **empty**. All byte-identical to `checkpoint-PFC-PCPG-16`. Only R-12 changed.

| | Status |
|---|---|
| **I-12 SESSION-LEVEL PER-DELTA CEILING** | **MATERIALIZED** (since `checkpoint-PFC-PCPG-16`; confirmed still present and independent, §3 falsifier 8) |
| **I-12 SESSION-LEVEL COMPOSED CEILING** | **MATERIALIZED** (this Work Unit) — reaches R-12's own actor-safe projection, the relation that legitimately owns "the proof ceiling" per its own RED-declared OUTPUT |
| **FULL I-12** | **PARTIAL / NOT COMPLETE** — full source authority, mutability status, evidence status, per-input proof class, AI-provider output class, and the richer "basis identity" composite all remain genuinely open, exactly as already disclosed |
| **FBR-PCPG-5** | **OPEN / BLOCKED_EXTERNAL**, untouched |
| **GOVERNANCE_ADMISSIBLE / PROVIDER_EXECUTABLE / CAN_SEND** | fully UNREACHABLE, mechanically unchanged |
| **R-13** | **NOT STARTED** |

## 7. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** The composed/aggregate slice of I-12's own Session-level proof ceiling now reaches R-12's actor-safe projection, via the single legitimate direct path (R-08 → R-12), proven never routed through R-09/R-10/R-11, never recomputed, never inferred, never defaulted. Independently falsified (20/20, covering every required category), mutation-proven (2/2 guards killed and restored, byte-identical after restore, one caught structurally by an AST purity check), and proven affected-suite-clean (438 passed / 0 failed, full combined PCPG suite). R-03 through R-11 remain byte-identical. `GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND` remain fully unreachable; `FBR-PCPG-5` remains `OPEN / BLOCKED_EXTERNAL`; `R-13` not started. This Work Unit does not continue into another I-12 slice automatically, per instruction.
