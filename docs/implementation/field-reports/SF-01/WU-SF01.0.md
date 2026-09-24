# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.0 — Bootstrap reconstruction, human decisions, environment baseline

## Mission
Before any code: reconstruct the current frontend against doc 21 (PF-01, CF-01..09) and the published F02 truth.
Classify every relation as SAFE_TO_IMPLEMENT_NOW / WAIT_FOR_F03 / WAIT_FOR_F04_OR_LATER, and find the
first broken frontend relation. Read-only. F03 WIP was not inspected.

## Parent / current Field
Parent: PF-01 (doc 21 §7). Current: pre-Session regime on published F02 (`bea864b`).

## Reconstruction result
- The frontend has two strata: the F01/F02 governed path (`inquiryClient` envelope, server capabilities, `expectedVersion` + Idempotency-Key, canonical re-read) and the PKG-28/29 legacy `/decision` surface.
- Verified absent: client authority inference, client next-state computation, optimistic canonical mutation, timers, and AI on the governed path.
- **First Broken Relation:** `CANONICAL CONTEXT/STATE → HUMAN POSITION`. The route/page, not the canonical relation, composes the field.
  - Position was page navigation: literal crumb arrays (`AppShell`), and a crumb like "Workspaces › Session" was shown while nothing was confirmed.
  - The Session state was a value inside a layout that did not change with state.
- Downstream symptoms of that break:
  - proof flattened into width;
  - a single page-level `outcome` slot, so residue survived later intents;
  - the effect lifecycle collapsed to a `busy` flag;
  - "re-read" was claimed before the re-read happened (Workspace/Challenge pages);
  - mutation network loss read "Nothing is assumed to have changed" (falsifier 17);
  - the keyless F01 founding invited "Please try again";
  - Session identity was invented as `Session {i+1}`;
  - on mobile, phases were hidden by index.

## Classification
- **SAFE_TO_IMPLEMENT_NOW:** Field Frame; Relation Trace (pre-Session; the Session primitive is built but not adopted); effect lifecycle; unknown consequence on mutation network loss (C3-01); commit marker and reconstruction honesty (C3-06); boundary taxonomy (21 §39); affordance grammar; proof depth D2/D3; origin grammar (applied only to SYSTEM STATE); typography, motion and responsive order.
- **WAIT_FOR_F03:** capture, the QuestionBurst projection beyond F02, the participant/PARTICIPATION projection, manual completion, the frozen source, the CLOSED-capture kind, F03 re-read and outcome mapping, lanes G/H, Stage 2 adoption on the Session page, and everything in the contact zone.
- **WAIT_FOR_F04_OR_LATER:** AI derivation, results, provider ceilings, AI provenance, evidence, the legacy `/decision` re-homing (F07), and F11 closure.

## Human decisions used
SF01-HD-1..4 (given after this reconstruction), and SF01-HD-5 (Case-3 raised in this WU: ledger numbering is shared with F03, so reconciliation is deferred). See STATUS.md.

## Environment baseline (L-1)
- `npm ci`: 395 packages; `package-lock.json` sha256 identical before and after (`eb6e3ac3…`).
- Baseline gates at `bea864b`: eslint clean, tsc clean, vitest **98 passed** (equal to F02's record).
- Running F03 environment observed read-only: compose project `nquiry` on :3000 / :8000 / :15432.
- The existing mocked lane (`playwright.config.ts`, `reuseExistingServer` on :3000) would therefore test the F03 web build, so SF-01 uses its own isolated lane (WU-SF01.4).

## Limitations / ceilings
Doc 21 §4 lists "manual completion" and "immutable original text" as existing fits. They are decided (HD-9, NQ-DEC-017/002) but not materialized in the F02 runtime or UI. Not treated as present.

## Git state
Read-only WU. No change.

## Result
PASS (reconstruction). The Case-3 ledger boundary was closed by SF01-HD-5.
