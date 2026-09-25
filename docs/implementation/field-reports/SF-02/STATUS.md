# FIELD STATUS

## Field
SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)

## Governing architecture
`docs/implementation/frontend/22_NQIRY_SYMBIOTIC_SURFACE_ARCHITECTURE.md` (doc 22; persisted with SF-02, byte-identical
to the main-checkout copy). Foundation: doc 21 / SF-01. SFE execution law: 20.

## Semantic regime
The whole frontend as a Symbiotic Interaction Field: Access Field, Workspace Overview Field, Workspace Field,
Challenge Field (primary), Session Field (lifecycle, Human Question Field, Frozen Field). Bound to F01/F02/F03 as
published. The analysis contact zone (F04) is absent: not implemented, not mocked, not referenced (gate).

## Status
**READY_FOR_HUMAN_FRONTEND_REVIEW — UNCOMMITTED (not tagged, not pushed, not PUBLISHED).**
Local proof is GREEN on the final tree (L0 219/219 · L3 81/81 · L7 14/14 · evidence run-6 30/30); FIELD_GREEN is not claimed on that basis — the human Field
Review decides. No Case 3. Ledger reconciliation: WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION (unchanged, see
SF-01 STATUS.md; nothing written to 16 §41 / 20 §15B).

| Lane | Result (final tree) |
|---|---|
| L0 vitest | 219 passed (196 baseline + 23 SF-02); RED non-vacuity on `644e1c8`: 3 files unloadable + 8 failed / 38 passed |
| L5 tsc / eslint / static gates | 0 errors / clean / 5 gate groups (each predicate proven against a planted violation) |
| L3 isolated mocked browser (`playwright.sf01.config.ts`, :3301, dead proxy; desktop + Pixel 7) | 81/81 (1.4 min; re-run alone on the final tree after the ladder-4 mocked stage failed 49/81 with dev-server timeouts on unchanged legacy pages — environment, host load average 6–8 from other Fields' containers) |
| L6 isolated environment (`nquiry-sf01`, no host ports) | guard PASS; migrations static + live PASS on an empty DB (head f6b2c4d9a318) |
| L7 isolated real stack (`scripts/run_sf01_real_stack.sh`, lane alone) | 14/14 (8.5 min, lane alone; F03 protected-question spec desktop 1.4 min within its 90 s budget this run) |
| E browser evidence (production build + real API, `nquiry-sf02-inspect` :13200) | run-6 30/30 (85 explicit checks + D3/D8 guards; axe serious/critical 0 on every state; overflow 0; no unexpected HTTP) (runs 1–5 kept: 19/30, 30/30, 30/30, aborted by D7, aborted by D8) |
| Performance (D5, `harness/perf-ab.mjs`, ×4 CPU throttle) | rAF 16.6 ms Access / 29 ms Workspaces (from 96–143 ms); clicks 90–170 ms (from 300–650 ms) |

Review artefacts: FIELD_REVIEW.md, CHATGPT_REVIEW.txt, PROOF_MATRIX.md (falsifiers 1–77 → evidence),
review/FRONTEND_BROWSER_REVIEW.md, review/browser-evidence-2026-09-25/{harness,runtime,run-1..run-6}.

## Work Units
| WU | Title | Report |
|---|---|---|
| SF02.0 | Binding gate (22 §9 → real contracts), Case-3 register closed, plan | WU-SF02.0.md |
| SF02.1 | Dark Field identity, lifecycle extensions (detail, relation families), gates | WU-SF02.1.md |
| SF02.2 | Topology primitives (Core/Orbit/Node/Path/planes/background/human position) | WU-SF02.2.md |
| SF02.3 | Challenge Field (primary) | WU-SF02.3.md |
| SF02.4 | Workspace Overview + Workspace Field; logout-race root repair | WU-SF02.4.md |
| SF02.5 | Session Field, Human Question Field, Frozen Field; F03 panel re-homed | WU-SF02.5.md |
| SF02.6 | Access Field | WU-SF02.6.md |
| SF02.7 | Proof ladder, run history, D5 background cost | WU-SF02.7.md |
| SF02.8 | Browser evidence, defects D1–D6, reviews | WU-SF02.8.md |

## Human decisions
See FIELD_REVIEW.md (SF02-HD-1..5). SF-01 decisions (SF01-HD-1..5) remain in force.

## Open visible items for the human (Case 2, presentation)
OV-1 closed as D8; OV-2 lifecycle label density (one next phase named); OV-3 no reduced-motion
Session/Frozen screenshot. See review/FRONTEND_BROWSER_REVIEW.md §6.

## Upstream dependencies
F02 (`2f33be1` / `bea864b`), F03 (`0d59ae3f` / `c9d86bab`, tag `field-F03`), SF-01 (`447b24e`, `c944b95`, sync `45b6f2f`, `644e1c8`).

## Downstream
1. Human Field Review of SF-02 (this state). 2. Commit only on explicit instruction. 3. Ledger reconciliation after
the F04 architecture field is reconciled. 4. F04 analysis contact zone when published (its relation is absent here by design).

## Runtimes still up (tear down when the review is done)
`nquiry-sf02-inspect` (:13200) and `nquiry-sf01-inspect` (:13100):
`docker compose -p <project> -f infra/sf01/compose.yaml down -v --remove-orphans`.
