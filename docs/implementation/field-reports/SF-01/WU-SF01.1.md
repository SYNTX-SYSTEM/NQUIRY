# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.1 — Effect & Boundary grammar (pure)

## Mission
Give every settled outcome its own consequence semantics, and model the effect lifecycle as a pure
relation reducer (21 §14, §17, §22, §39; CF-08; C3-01; C3-06).

## Relation materialized
`REQUEST → OUTCOME(kind) → CONSEQUENCE (committed | none | unknown) → RECONSTRUCTION (reading | done | failed)`

## Files changed
- NEW `apps/web/lib/field/outcomeSemantics.ts`
  - `SETTLED_KINDS` is closed to the published F02 envelope plus `network_failure`; an unknown kind throws.
  - `describeOutcome(kind, path)` gives the §39 title, consequence, `announce` (status/alert), `retainIntent` and `reconcileFirst`.
- NEW `apps/web/lib/field/effectLifecycle.ts`
  - `effectReducer`: possible → requested → settled → reconstruction.
  - `intentKeyFor` retains the Idempotency-Key per relation while the consequence is unknown.
  - `blocksConsequence` blocks while a request is requested, reading or failed.
- NEW `apps/web/tests/field/outcomeSemantics.test.ts` (12), `apps/web/tests/field/effectLifecycle.test.ts` (14).

## Test-first intent
- **TRUE:**
  - one distinct title per kind;
  - commit is the only committed consequence;
  - network loss or INDETERMINATE on a mutation is `unknown`, retains the intent and reconciles first;
  - a read has no consequence;
  - a new request replaces the previous outcome;
  - a committed outcome whose re-read failed keeps blocking dependent effects (C3-06).
- **IMPOSSIBLE:**
  - F17 "network failure ⇒ nothing happened";
  - F18 INDETERMINATE read as failure;
  - F21/F22 collapse;
  - settle without request;
  - a second request in flight;
  - a request while the re-read is running;
  - an unknown kind.

## RED → GREEN
- RED: both suites failed at import (module absent, the RED-by-absence class disclosed in F02).
- Non-vacuity: the F17 predicate, run against the F02 text "The server could not be reached. Nothing is assumed to have changed.", returns `true`. It catches the real pre-SF-01 wording.
- GREEN: 26 passed.

## Implementation notes
- **PENDING (21 §17) is deliberately not a phase.** The F02 transport is one synchronous request/response and projects no "accepted, not committed" signal, so showing PENDING would display certainty the system does not provide (DISPLAYED CERTAINTY ≤ RECONSTRUCTABLE CERTAINTY). Case 1, derived from 21 §3; recorded as open relation OR-I.
- **Server INDETERMINATE now also retains the intent key** (F02 pages rotated it). A new key after an unproven commit could duplicate the effect; 21 §14 says "prevent blind duplicate consequence".

## DeepSweep
- Reconstruction chain: changed relation (effect semantics) → parent CF-08 → siblings CF-07 (blocking) and CF-09 (reconstruction) → governance/authority unchanged (no authority computed) → persistence/API unchanged → frontend (consumed in WU-SF01.3/4) → tests.
- Inverse: a visible `data-consequence="unknown"` ← `describeOutcome(network_failure | indeterminate, mutation)` ← a transport rejection or the server's 503 envelope.

## Git state
Uncommitted, nothing staged.

## Result
PASS.
