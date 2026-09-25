# FIELD STATUS

## Field
SF-03 — NQIRY SYMBIOTIC SURFACE EVOLUTION (materialization of doc 23 on the SF-02 Field)

## Governing architecture
Delta: `docs/implementation/frontend/23_NQIRY_SYMBIOTIC_SURFACE_EVOLUTION_ARCHITECTURE.md` (persisted with SF-03,
byte-identical to the main checkout). Protected semantics: doc 22. Foundation: doc 21 / SF-01. SFE law: 20.

## Status
**READY_FOR_HUMAN_FRONTEND_REVIEW — UNCOMMITTED (not tagged, not pushed, not PUBLISHED, not FIELD_GREEN).**
Baseline = the uncommitted SF-02 tree on `644e1c8` (kept intact). No Case 3. Ledger reconciliation unchanged:
WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION (nothing written to 16 §41 / 20 §15B).

| Lane | Result (final tree) |
|---|---|
| L0 vitest | 232 passed (geometry 11, SF-03 primitives 8, SF-02 suites) |
| L5 tsc / eslint / gates | 0 / clean / SF-02 gates GREEN |
| L3 isolated mocked (`playwright.sf01.config.ts`; sf01 + sf03 specs on Pixel 7) | **102 / 102** (2.0 min; 81 SF-02 regression + 21 SF-03 stress/acceptance; desktop + Pixel 7; lane alone) |
| L6 isolated environment | guard PASS; migrations static + live PASS (head f6b2c4d9a318) |
| L7 isolated real stack (alone) | **14 / 14** (6.9 min, lane alone, host load 4–6; earlier runs on the same lane at load 9–17: 12/14, 12/14, 13/14 — only the F03 protected spec's 90 s budget, no assertion ever failed) |
| E browser evidence (`nquiry-sf03-inspect` :13300, production build, real API) | run-5 **40 / 40** (30 SF-02 regression states + 10 doc 23 acceptance states; axe serious/critical 0, overflow 0, no unexpected HTTP, keyboard focus visible everywhere) (runs 1–4: 39/40, 39/40, 38/40, 40/40 — each RED a repaired root; run-4 preceded D-SF03-5) |
| P performance (`harness/perf-ab.mjs`, ×4 CPU throttle) | Access 16.3 ms · Workspaces 19.2 ms rAF median; ambient cost ≈ 2.5 ms/frame |

Review artefacts: FIELD_REVIEW.md, CHATGPT_REVIEW.txt, PROOF_MATRIX.md (doc 23 falsifiers 1–58 → evidence),
review/FRONTEND_BROWSER_REVIEW.md, review/browser-evidence-2026-09-25/{harness (review-harness, setup-scenario, perf-ab),
runtime, run-1 … run-5}. Pre-existing SF-02 evidence remains under `SF-02/`.

## Work Units
| WU | Title | Report |
|---|---|---|
| SF03.0 | Baseline reconstruction, delta → roots, plan | WU-SF03.0.md |
| SF03.1 | Typography and containment law | WU-SF03.1.md |
| SF03.2 | Content-aware, viewport-aware, collision-resistant geometry | WU-SF03.2.md |
| SF03.3 | Global living Field (+ performance proof) | WU-SF03.3.md |
| SF03.4 | Orientation rail: centred identity, symbiotic breadcrumb | WU-SF03.4.md |
| SF03.5 | Instrument constellation + relational reciprocity | WU-SF03.5.md |
| SF03.6 | Surface evolution | WU-SF03.6.md |
| SF03.7 | Proof ladder, regression, root repairs | WU-SF03.7.md |
| SF03.8 | Browser evidence, defects, handoff | WU-SF03.8.md |

## Open items for the human (Case 2 / decisions)
OV-1 two-column threshold (1500 px) · OV-2 ordinals on later lifecycle labels · OV-3 breadcrumb → Field reciprocity
(optional, not implemented) · OV-4 F03 real-stack spec budget (90 s) on a loaded host · which evidence runs to commit.

## Runtimes up for the review (tear down when done)
`nquiry-sf03-inspect` (http://127.0.0.1:13300) and `nquiry-sf02-inspect` (http://127.0.0.1:13200, for comparison):
`docker compose -p <project> -f infra/sf01/compose.yaml down -v --remove-orphans`.

## Upstream / downstream
Upstream: SF-02 (uncommitted), SF-01 (`447b24e`/`c944b95`/`45b6f2f`/`644e1c8`), F03 (`0d59ae3f`), F02 (`2f33be1`).
Downstream: human Field Review → commit only on explicit instruction → ledger reconciliation after F04 → F04 contact zone.
