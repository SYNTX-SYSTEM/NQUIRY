# WU-PFC-PCPG-13 — HA-PCPG-1 decision recording and field reconstruction (no code materialized)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23). This Work Unit is a DECISION-RECORDING AND AUDIT Work Unit, not a BLUE materialization — no producer code is added, changed or proved here; it closes with a field-reconstruction and a derived next-WU candidate instead of a falsifier/mutation/regression cycle.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-13 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | Human Authority decision recording + field reconstruction (no BLUE code) |
| Human authorization | Two explicit instructions, verbatim, quoted in full in §2 and §3 below: (1) "SFE FIELD-CLOSURE AUDIT ONLY ... Do NOT begin R-13 ... Do NOT implement a data-class classifier yet ... Do NOT modify Architecture 26"; (2) "HUMAN AUTHORITY DECISION — HA-PCPG-1 ... YES, conditionally ... After recording this Human Authority decision: 1. reconstruct the field; 2. determine whether GAP-11-006/FBR-PCPG-3 now becomes the active blocker; 3. do not begin R-13; 4. do not materialize SEND; 5. do not bind a provider; 6. derive the next legitimate Work Unit from the reconstructed field. Stop if a new Human Authority boundary appears." |
| Predecessor | `pfc-integration` `126ede1f07577e4c5d5b54035326949499cca623` (`checkpoint-PFC-PCPG-12`, pushed, final PCPG field closure). |
| What changed | Two field-report files only: `docs/implementation/field-reports/PFC/HUMAN_DECISIONS.md` (new entry HD-29), `docs/implementation/field-reports/PFC/HUMAN_AUTHORITY_QUEUE.md` (HA-PCPG-1 row updated OPEN → RESOLVED, conditionally). **No file under `docs/architecture/` touched. No file under `packages/` touched. No test file touched. No migration.** |
| Must remain impossible | Any change to RED architecture text; any R-13/SEND materialization; any provider binding; any code change implying `ALLOWED`, `COMPOSABLE`, `GOVERNANCE_ADMISSIBLE=true`, `PROVIDER_EXECUTABLE=true` or `CAN_SEND=true` is now reachable (none of those are changed by this Work Unit — see §5). |

## 2. Regression-result ambiguity — resolved from the raw artifact (audit instruction, part 1)

Re-examined `full_regression_wu12.log` (the raw process output of WU-PFC-PCPG-12's full-repository regression, not a summary of it) directly, not inferred:

- Final pytest summary line, verbatim: `2394 passed, 15 skipped in 2205.01s (0:36:45)`.
- `grep -c "FAILED"` on the raw log: **0** matches.
- ANSI-stripped log, `grep -in "fail\|error"`: **0** matches anywhere in the entire run.
- pytest's own summary-line convention lists only non-zero categories; neither `failed` nor `error` appears at all.

**Result confirmed: 2394 passed / 15 skipped / 0 failed.** `FIELD_GREEN` for the regression proof is correctly claimable; this is a claim about proof-suite status only, not about operational executability (§3).

## 3. Semantic closure audit — MATERIALIZATION COMPLETE vs OPERATIONALLY EXECUTABLE (audit instruction, part 2–3)

R-01 through R-12 are each MATERIALIZATION COMPLETE for their own disclosed scope. The following relations' positive/boundary-crossing paths are OPERATIONALLY UNREACHABLE as of `checkpoint-PFC-PCPG-12`:

| Finding | Classification (as of checkpoint-12) |
|---|---|
| 1. R-08 composition makes a true `GOVERNANCE_ADMISSIBLE` unreachable | REQUIRED CONSEQUENCE OF CURRENT ARCHITECTURE, root-caused by an OPEN GOVERNANCE GAP (GAP-11-006) |
| 2. `CAN_SEND`'s meaningful true-path is unreachable | REQUIRED CONSEQUENCE OF CURRENT ARCHITECTURE, directly BLOCKED BY HUMAN AUTHORITY (HA-PCPG-1) |
| 3. R-11's eligible content set is empty under current FAILURE STATE semantics | REQUIRED CONSEQUENCE OF CURRENT ARCHITECTURE (RED-mandated, not a BLUE gap) |
| 4. The `CAN_SEND` combinator mutation is unobservable | TESTABILITY LIMIT (downstream of 1–2, already disclosed in `pcpg_capability.py`'s own docstring) |

Full reasoning for each: see the audit response given inline in this conversation immediately before HD-29 was recorded (not duplicated here to avoid two diverging copies of the same analysis; the HD-29 entry and the HA-PCPG-1 row summarize the load-bearing conclusions).

## 4. Human Authority decision recorded: HD-29 / NQ-DEC-057 (HA-PCPG-1)

Recorded verbatim in `docs/implementation/field-reports/PFC/HUMAN_DECISIONS.md` under `## HD-29 — HA-PCPG-1 user-authored instruction as provider computation: conditional admission, governed-source-material contract (2026-10-01)`. Summary (full text is in that file, not duplicated here, per this Field's own established convention — see every prior `HD-NN` entry):

- `PROVIDER_COMPUTATION` is admitted as an operation class, but only under the contract `USER_AUTHORED_INSTRUCTION → governed source material`, never `USER_AUTHORED_INSTRUCTION → direct provider command`.
- Eligibility additionally requires the full reconstructed field: current Field, Pulse, Actor, Authority, Purpose, Source, Data Governance, candidate deltas/operations, per-delta governance, composition result, provider eligibility, provider-safe projection — all "at minimum."
- `USER REQUEST != AUTHORIZATION`; `PROMPT != AUTHORITY`. Authority is derived from the governed field's own authority relations, never from prompt authorship. No direct `USER INPUT → PROVIDER` path is permitted.
- R-13 explicitly remains NOT STARTED by this decision.

**Ledger / reconciliation:** `NQ-DEC-057`, assigned as the next free pair after this worktree's own copy of `16_DECISION_GAP_REGISTER.md`'s last entry (`NQ-DEC-056`/`HD-28`). `16_DECISION_GAP_REGISTER.md` itself was **not** modified from this worktree — it is a cross-field registry shared with concurrent, isolated BLUE lanes this worktree does not merge with or read live state from (consistent with the standing discipline never to touch anything outside `pfc-integration`). Whoever reconciles this worktree to a shared branch must confirm `HD-29`/`NQ-DEC-057` were not independently claimed by a concurrent session, and must add the registry entry at that time. This is disclosed as an open reconciliation step, not silently assumed complete.

`HUMAN_AUTHORITY_QUEUE.md`'s HA-PCPG-1 row was updated in place (its own file's own stated convention: "No question is repeated; an entry is updated in place") from `OPEN` to `RESOLVED, conditionally`, with a summary and a pointer to this report and to HD-29. No other row in that shared file was touched.

## 5. Field reconstruction — does GAP-11-006/FBR-PCPG-3 become the active blocker? (audit instruction, part 4; decision instruction, step 1–2)

Re-deriving the field's reachability under HD-29's new contract, checking every item HD-29 itself lists as "at minimum" required for eligibility, against what this codebase actually has a producer for:

| HD-29 prerequisite | Real producer in this codebase? |
|---|---|
| current Field | Yes — R-03, `pcpg_field_snapshot.py` |
| Pulse | Yes (7/10 elements) — R-04, `pcpg_field_pulse.py` |
| Actor | Yes — `FieldSnapshot.actor` (R-03) |
| Authority | Yes — `FieldSnapshot.actor.authority` (R-03) |
| Purpose | Yes, narrowly — `SemanticObservation.declared_purpose`/`semantic_purpose`/`purpose_alignment`/`semantic_drift` (R-05, SIMPLIX's own minimal check) |
| **Source** | **No** — no "source status" producer exists anywhere (`01_INVARIANTS.md` I-12 states the rule — "inherited, never raised" — but no code computes or carries it; `grep` for `source_status`/`SourceStatus`/`proof_ceiling` across every `pcpg_*.py` module: zero hits). **This prerequisite has no owning GAP number or HA-PCPG-* row in the RED text today** — it is not GAP-11-006 (that governs data *class*, not source *status*/provenance), and no FBR-PCPG-* entry names it either. |
| **Data Governance** | **No** — GAP-11-006/FBR-PCPG-3, explicitly OPEN in RED, governed by HA-PCPG-4's own already-decided standing rule ("deterministic, rule-based candidates ... no override") — an engineering gap under an existing rule, not an open decision |
| candidate deltas / operations | Yes — R-06, `pcpg_candidate_deltas.py` |
| per-delta governance | Yes — R-07, `pcpg_delta_evaluation.py` (though its own `ALLOWED` branch is unreachable per finding 1–2, §3) |
| composition result | Yes — R-08, `pcpg_composed_effect.py` (its own non-empty-retained/COMPOSABLE path unreachable per finding 1, §3) |
| provider eligibility | Yes — R-11, `pcpg_eligible_content.py` (honestly empty today, finding 3, §3) |
| provider-safe projection | Yes — R-12, `pcpg_actor_projection.py` |

**Answer to the audit's own question 2: yes, GAP-11-006/FBR-PCPG-3 (Data Governance) becomes one of two active blockers — not the sole one.** "Source" (I-12 status/provenance) is a second, independent, currently-unnamed-in-RED blocker surfaced by HD-29's own text, not by this Field's prior relations. Separately and independently, `PROVIDER_EXECUTABLE` remains unconditionally `False` regardless of either: `FBR-PCPG-5` ("ADMITTED COMPUTATION → ELIGIBLE PROVIDER ROUTE", `00_FIELD.md` line 183) is its own, already-named, already-OPEN engineering gap (`HARD-DEP-002`, `GAP-08-002/008`), governed by HD-19/HD-LIVE-1's own already-decided MockProvider/production defaults — not by HA-PCPG-1 at all. HD-29 does not touch it.

**No code was changed to reflect HD-29.** R-07's `OPERATION_CLASS_NOT_ADMITTED` static reason remains, today, an accurate description of this Field's own current reachable state: even though the operation *class* is now conditionally admitted in principle, the delta can still never honestly resolve to `ALLOWED` while Data Governance and Source producers are absent — the correct value the code *would* need to compute is a different, more precise `INDETERMINATE`-family reason (missing producer), never `ALLOWED`. Materializing that precision is itself the next Work Unit's own job (§6), not assumed or silently applied here.

## 6. Confirmations (decision instruction, steps 3–5)

- **R-13 not begun.** No file under any SEND-gate-shaped module was created or touched.
- **SEND not materialized.** No provider-facing payload, manifest, or route-selection code exists anywhere in this commit.
- **No provider bound.** `check_provider_sdk_imports.py` was not re-run for this Work Unit because no `packages/` file was touched (confirmed via `git diff --stat`, §1) — there is nothing for it to check.

## 7. Next legitimate Work Unit, derived (not materialized)

The next legitimate Work Unit is: **materialize FBR-PCPG-3 (the data-class classifier, GAP-11-006), governed by HA-PCPG-4's own already-decided, standing rule** ("deterministic, rule-based candidates. Ambiguous content takes the most restrictive class. No override.") — because:

- It requires no new Human Authority decision (HA-PCPG-4 already answers "who may assign the data class" and "what happens when ambiguous").
- It is the more tractable of the two newly-surfaced blockers (Data Governance has a named GAP number and a governing rule; Source status has neither, see §5 — attempting Source first would mean inventing scope RED does not name, which this Field's own discipline forbids).
- Building it would NOT, by itself, make `ALLOWED`/`COMPOSABLE`/`GOVERNANCE_ADMISSIBLE=true`/`CAN_SEND=true` reachable — Source status would remain absent, and `PROVIDER_EXECUTABLE` would remain unconditionally `False` via the independent FBR-PCPG-5 gap. It would, honestly and incrementally, change R-07's current `OPERATION_CLASS_NOT_ADMITTED` reason (now stale, since HD-29 conditionally admits the class) to a more precise, still-non-`ALLOWED` reason for the right cause.

**This Work Unit does not begin that materialization.** Per the audit instruction's own closing line ("Do not proceed beyond that boundary") and the decision instruction's own step 6 asking only to *derive*, not build, the next Work Unit — this report names and justifies the candidate and stops.

## 8. New Human Authority boundary check (decision instruction's own stop condition)

No new Human Authority boundary was found. Specifically:
- HA-PCPG-4 (data class assignment authority) already has a standing decided default — building FBR-PCPG-3 against it is BLUE engineering, not a new HA question.
- "Source" status (I-12) has no owning HA-PCPG-* row, but I-12 itself already states the governing rule ("inherited, never raised") — this reads as an unbuilt producer under an already-stated invariant, the same shape as GAP-11-006, not as an undecided question requiring a new Human Authority answer. It is flagged in §5 as a disclosed gap in the RED text's own bookkeeping (no FBR/GAP number names it), which a future Human Authority pass may wish to formalize with its own number — but that formalization is not itself a blocking decision this session needs an answer to before proceeding to FBR-PCPG-3.
- FBR-PCPG-5 (provider route) is governed by already-decided defaults (HD-19, HD-LIVE-1), not an open question.

**No new boundary. Stopping at the derived-but-not-materialized next Work Unit, per the instruction's own scope.**
