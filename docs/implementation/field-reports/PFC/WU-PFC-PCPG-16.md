# WU-PFC-PCPG-16 — I-12 Session-level proof ceiling (R-03 → R-06 → R-08)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-16 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization (repair of three already-closed modules: R-06, R-07, R-08) |
| Human authorization | "PASS WITH ONE BINDING CORRECTION. Authorize the narrow SESSION-LEVEL I-12 materialization only." Full instruction honored clause-by-clause below. |
| Predecessor | `pfc-integration` `8a5f0177781cb30ccd8d839071a534b3ab634f11` (`checkpoint-PFC-PCPG-15`, pushed). |
| Authoritative finding reconstructed and followed exactly | `FieldSnapshot.session.proof_mode` is the already-real, already-authoritative fact (R-03, `checkpoint-PFC-PCPG-4`; produced by `inquiry_queries.proof_mode`, HD-24 rule 5). **No duplicate R-03 producer created.** Chain materialized exactly as directed: R-03's own existing value → R-06 `CandidateDelta` carries it → R-07 passes it through unconsulted → R-08 composes it. **R-12 projection NOT touched** (the instruction's own falsifier 8 phrasing, "if touched", is conditional; threading the value all the way to R-12 would additionally require touching R-09's `ChainResult`, which the instruction did not authorize and this Work Unit did not do — disclosed, not silently skipped, §6). |
| Claim ceiling honored | FIXTURE scope → `"FIXTURE_NON_PROOF"`; non-fixture scope → the already-authoritative `"GOVERNED"` value; no session → `None`, never guessed. **No** full source authority, mutability status, evidence status, per-input proof class, AI-provider output class, complete provenance, or complete source reconstruction is claimed anywhere in this Work Unit. |

## 2. Execution record

**Step "first reconstruct the exact R-06 `CandidateDelta` and R-08 composition shapes" (honored before any code was written):** `CandidateDelta` (`pcpg_candidate_deltas.py`, unchanged since `checkpoint-PFC-PCPG-6`) has 9 fields, none with a default; `ComposedEffect`/`compose_effect()` (`pcpg_composed_effect.py`, unchanged since `checkpoint-PFC-PCPG-8`) filters `records` by `result is Result.ALLOWED`. Both were read fresh from disk before any edit (not assumed from memory).

**Implementation (preferred relation, honored exactly):**
```text
FieldSnapshot.session.proof_mode
  -> CandidateDelta.session_proof_ceiling   (R-06, new field, default None, backward compatible)
  -> DeltaRecord.session_proof_ceiling      (R-07, pure passthrough, new field, default None)
  -> ComposedEffect.composed_proof_ceiling  (R-08, new field; _compose_proof_ceiling())
```
- **R-06** (`form_candidate_deltas`): `session_proof_ceiling = snapshot.session.proof_mode if snapshot.session is not None else None`, quoted onto every delta formed from that snapshot. No new R-03 call; the existing `FieldSnapshot` parameter already carries the value.
- **R-07** (`evaluate_deltas`): `session_proof_ceiling=delta.session_proof_ceiling` added to the one existing `DeltaRecord(...)` construction site — never read anywhere else in the module (proven, §3).
- **R-08** (`compose_effect`): `_compose_proof_ceiling(retained)` — the most restrictive real value (`"FIXTURE_NON_PROOF"` > `"GOVERNED"`, `_PROOF_CEILING_RESTRICTIVENESS`) among `retained`'s own ceilings; honestly `None` if `retained` is empty or any contributing ceiling is unknown (never silently diluted toward a weaker, known value).

**Both new dataclass fields were added with a `None` default at the end of each dataclass**, specifically so that no other already-closed test file's own direct `DeltaRecord(...)`/`CandidateDelta(...)` construction (7 and 2 sites respectively, across 6 other test files, confirmed by `grep` before writing any code) needed to change. Confirmed: `tests/e2e/test_pcpg_chain_results.py`, `test_pcpg_capability.py`, `test_pcpg_eligible_content.py`, `test_pcpg_actor_projection.py` all pass unmodified (63/63, §6–9).

**No semantic architecture decision was required beyond what HD-24 and I-12 already authorize** — the STOP condition in the prior discovery pass's own finding did not apply here; this report does not invoke it, since the narrow slice closed honestly on already-authoritative facts alone.

## 3. Falsifier map (against the instruction's own required minimum list)

| Required category | Falsifier(s) | Where |
|---|---|---|
| 1. fixture Session produces FIXTURE_NON_PROOF at R-06 | `test_a_fixture_session_produces_fixture_non_proof_on_every_delta` | R-06 |
| 2. no later R-08 step can raise FIXTURE_NON_PROOF | `test_no_later_step_can_raise_a_retained_fixture_non_proof_ceiling` | R-08 |
| 3. mixed retained deltas cannot produce a stronger (less restrictive) ceiling than the most restrictive real input | `test_mixed_retained_deltas_compose_to_the_most_restrictive_ceiling`, `test_a_single_fixture_delta_composes_to_fixture_non_proof`, `test_all_governed_retained_deltas_compose_to_governed` | R-08 |
| 4. absence/unknown proof_mode never becomes stronger proof | `test_an_unknown_ceiling_on_even_one_retained_delta_never_becomes_stronger_proof`, `test_no_session_named_gives_no_ceiling_never_guessed` | R-08, R-06 |
| 5. R-06 does not infer provenance from `CandidateDelta.target` strings | `test_session_proof_ceiling_is_quoted_not_derived_from_target` | R-06 |
| 6. no provider-output proof class is invented | `test_the_module_invents_no_provider_output_or_evidence_proof_class` | R-08 |
| 7. no Evidence provenance is invented | `test_the_module_invents_no_provider_output_or_evidence_proof_class` (same falsifier, same source list) | R-08 |
| 8. R-12 projection, if touched, exposes only the explicit session-level ceiling | Not touched — see §1, §6. No falsifier needed; `git diff --stat` on `pcpg_actor_projection.py` is empty. | — |
| 9. FBR-PCPG-5 remains OPEN / BLOCKED_EXTERNAL | `git diff --stat` on `pcpg_capability.py`: empty; no provider-route file touched | field-level |
| 10. PROVIDER_EXECUTABLE remains false | Same — R-10 untouched | field-level |
| 11. CAN_SEND remains false | Same — R-10 untouched | field-level |
| 12. R-13 remains NOT STARTED | No SEND-gate-shaped file created or touched | field-level |

Plus the pure-passthrough guarantee: `test_session_proof_ceiling_is_passed_through_never_consulted_for_a_result` (R-07, AST-proven: the attribute never appears inside any `If`/`Compare`/`BoolOp`/`IfExp` anywhere in the module) and `test_the_module_never_invents_a_producer_for_source_status` (R-07, updated from WU-15's own now-partially-stale version — `proof_ceiling` is now a legitimate substring; the narrower, still-real claim — no `source_status`/`source_authority`/`evidence_status` — is what's checked).

## 4. R-13 / SEND / provider / FBR-PCPG-5 confirmations

- **R-13 not begun. SEND not materialized. No provider bound. No provider routing touched.** `git diff --stat` confirms only `pcpg_candidate_deltas.py`, `pcpg_delta_evaluation.py`, `pcpg_composed_effect.py` and their own three test files changed — nothing under any provider-route-shaped module.
- **FBR-PCPG-5 preserved exactly as OPEN / BLOCKED_EXTERNAL.** `pcpg_capability.py` (R-10, where `PROVIDER_EXECUTABLE`/`NO_ELIGIBLE_PROVIDER_ROUTE` live) is byte-unchanged.
- **Architecture 26 not modified.** `git diff --stat` against `docs/architecture/`: empty.

## 5. Proofs (progressive cadence)

- Local: `ruff check` / `ruff format --check` clean (one line-length/formatting pass applied and re-verified); `mypy` 0 issues (one `cast`-equivalent list-comprehension narrowing added for `max()`'s own key function, disclosed inline); `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all `PASS`; no migration.
- Local falsifiers: **123 passed, 2 deselected** (R-06/R-07/R-08 combined, DB-backed end-to-end tests excluded from the local run, included in the affected-suite run below).
- **MUTATION proof (manual, 3 guards, local falsifier suite only):**
  1. R-06: hardcoded `session_proof_ceiling = "GOVERNED"` regardless of fixture/session state → 3 falsifiers failed. Restored.
  2. R-08: flipped "most restrictive wins" to `min()` (least restrictive) → 2 falsifiers failed. Restored.
  3. R-08: silently dropped unknown (`None`) ceilings instead of honestly propagating `None` (defaulting to `["GOVERNED"]` when all were unknown) → 1 falsifier failed. Restored.
  Final restore hashes confirmed byte-identical to the pre-mutation baseline for all three modules after every mutation; all 123 local falsifiers green on the restored files.
- **AFFECTED SUITES.** Full combined PCPG suite via `pytest tests/e2e/ -k pcpg`: **431 passed, 753 deselected, 0 failed** (all 13 pcpg test files, including the 63 R-09–R-12 tests confirmed unaffected and the DB-backed end-to-end tests for R-06/R-07); run against a live `pfc-integration` Postgres (roles bootstrapped, migrations at head), torn down immediately after.
- No full-repository regression performed, per the Human Authority proof-cadence decision (`WU-PFC-PCPG-8.md` §12): this delta is a pure, no-I/O passthrough/composition change across three already-closed application modules, with no new persistence, no schema change, no session/authority/capability-resolution infrastructure touch, and no cross-field protocol change.

## 6. Field reconstruction: R-03 → R-06 → R-08 → R-12

**Mechanical fact, not an inference:** `git diff --stat` against `pcpg_field_snapshot.py` (R-03), `pcpg_chain_results.py` (R-09), `pcpg_capability.py` (R-10), `pcpg_eligible_content.py` (R-11), `pcpg_actor_projection.py` (R-12) is **empty**. All five are byte-identical to `checkpoint-PFC-PCPG-15`.

- **R-03**: unchanged — `FieldSnapshot.session.proof_mode` was already real and already correctly produced; this Work Unit only reads it, never re-derives it.
- **R-06**: now carries `session_proof_ceiling` on every `CandidateDelta` — materialized.
- **R-08**: now composes `composed_proof_ceiling` across the retained set — materialized, for the narrow Session-level slice.
- **R-12**: **not touched.** `derive_actor_safe_projection()`'s own signature (`ingress, semantic_observation, delta_records, chain_result, capability`) does not take `composed_effect` directly — projecting the composed ceiling to R-12 would require ALSO threading it through R-09's `ChainResult` (itself untouched), a materially larger surface the instruction's own "narrowest" framing and the conditional "if touched" phrasing did not authorize. Disclosed here explicitly, not silently dropped: `delta_records` (already projected by R-12 today) DOES carry each delta's own `session_proof_ceiling` individually (R-07's passthrough), so the per-delta fact is not entirely absent from the projection — only the single composed/aggregate ceiling is not yet surfaced there.

## 7. Resulting status

**I-12 SESSION-LEVEL SLICE: MATERIALIZED.** The narrow chain `FieldSnapshot.session.proof_mode → CandidateDelta → DeltaRecord → ComposedEffect` is real, falsified (new falsifiers covering every required category), mutation-proven (3/3 guards killed and restored, byte-identical after restore), and proven affected-suite-clean (431 passed / 0 failed, full combined PCPG suite).

**FULL I-12: PARTIAL / NOT COMPLETE.** Explicitly not claimed: full source authority, mutability status of arbitrary inputs, evidence status of arbitrary inputs, proof class of every canonical input, AI-provider output proof class, complete provenance, complete source reconstruction, or R-12 projection of the composed ceiling. `SESSION PROOF MODE != FULL SOURCE PROVENANCE`. `PARTIAL I-12 != I-12 COMPLETE`.

`GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND` remain fully unreachable, mechanically unchanged (R-10 byte-identical). `FBR-PCPG-5` remains `OPEN / BLOCKED_EXTERNAL`, untouched. `R-13` not started. **WORK_UNIT_READY_FOR_HUMAN_REVIEW.** This Work Unit does not continue into the next I-12 slice automatically, per instruction.
