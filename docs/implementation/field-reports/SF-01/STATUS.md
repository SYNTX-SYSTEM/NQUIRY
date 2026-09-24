# FIELD STATUS

## Field
SF-01 — SYMBIOTIC FRONTEND FOUNDATION (pulled forward)

## Governing architecture
`docs/implementation/frontend/21_SYMBIOTIC_FRONTEND_ARCHITECTURE.md` (doc 21).
Persisted with SF-01 on branch `frontend-symbiotic` (human decision SF01-HD-4). SFE execution law: 20.

## Semantic regime
The pre-Session Relational Interaction Field (21 §48 Stage 1 + Stage 3 primitives):
PF-01 Field Frame, CF-01 Position, CF-02 Context Establishment, and the CF-07 / CF-08 / CF-09
grammar (affordance, effect and boundary, proof depth). SF-01 does not replace F11 and invents no
F11 semantics (21 §44 F11-R01..R04).

## Status
**FIELD_GREEN_WITH_DISCLOSED_CEILINGS — AWAITING HUMAN FIELD REVIEW.** Not committed. No commit, tag
or push without explicit approval. The isolated real-stack proof exists (SF01-HD-2 satisfied).

**Timeline:** SF-01 reached Field Green while F03 was still isolated and excluded. F03 was published
afterwards (`0d59ae3f`, record `c9d86bab` = `origin/master`, signed tag `field-F03`). No F03 integration has
occurred inside SF-01; the branch is still at `bea864b`. The post-F03 integration law is now ACTIVE, not yet
executed (see Downstream and FIELD_REVIEW.md "Post-run timeline").

| Lane | Result (final tree) |
|---|---|
| L0/L1/L2 vitest | 170 passed (98 baseline + 72 SF-01) |
| L3/L4 isolated mocked browser (`playwright.sf01.config.ts`, own server :3301, dead-proxy fail-closed) | 81 passed (39 existing F01/F02 unchanged + 21 SF-01 × desktop + Pixel 7) |
| L3 RED against the pre-SF-01 pages (bea864b export) | 19 failed / 2 passed (isolation harness; CF-07 rule already held by F02) |
| L5 eslint / tsc / `next build` / static gates / diff gate | clean / clean / 8 routes / 13 passed / contact zone, backend, migrations, deps, existing tests untouched |
| L6 isolated environment (`nquiry-sf01`, no host ports) | guard PASS; DB principals; migrations static + live PASS on an empty DB (head b3d8e5f0a2c7) |
| L7 isolated real stack (`scripts/run_sf01_real_stack.sh`) | **10/10 passed**, run twice; the second run is on the final tree (F02 flow + a11y + WU-02.12 closure + SF-01 × desktop + Pixel 7) |

Review artefacts: FIELD_REVIEW.md, CHATGPT_REVIEW.txt, PROOF_MATRIX.md, visual/ (10 real-stack PNGs).

## Work Units
| WU | Title | Report |
|---|---|---|
| SF01.0 | Bootstrap reconstruction, human decisions, environment baseline | WU-SF01.0.md |
| SF01.1 | Effect & Boundary grammar (pure) | WU-SF01.1.md |
| SF01.2 | Position: Relation Trace (pure) | WU-SF01.2.md |
| SF01.3 | Semantic primitives | WU-SF01.3.md |
| SF01.4 | Adoption on pre-Session surfaces + isolated mocked lane | WU-SF01.4.md |
| SF01.5 | Static architecture gates | WU-SF01.5.md |
| SF01.6 | Isolated real-stack environment + L7 spec (prepared) | WU-SF01.6.md |
| SF01.7 | Isolated real-stack execution; application repair (proof-depth marker) + environment repair (output ownership) | WU-SF01.7.md |

## Human decisions (2026-09-24)
- **SF01-HD-1**: SF-01 is authorized as the pulled-forward Symbiotic Frontend Foundation governed by doc 21. It does not replace F11.
- **SF01-HD-2**: L6/L7 only in an isolated frontend real-stack environment (own compose project identity, ports, database). Do not interfere with the running F03 environment. L0–L5 proceed. No Field PASS before the isolated proof.
- **SF01-HD-3**: F03 contact zone EXCLUDED. No F03 contract may be modified, inferred, duplicated or locally stabilized (capture, QuestionBurst, PARTICIPATION, manual completion, F03 capability mapping, re-read, DTOs, real-stack acceptance). All of it stays WAIT_FOR_F03.
- **SF01-HD-4**: Doc 21 governs SF-01 and belongs to the SF-01 branch. It is persisted with SF-01, not published separately first.
- **SF01-HD-5** (Case-3, answered 2026-09-24): ledger reconciliation (16 §41, 20 §15) is DEFERRED to the post-F03 synchronization step, because the REC-/NQ-DEC- sequence is shared with the in-progress F03. The decisions are recorded here with the exact text to reconcile (below). 16 and 20 stay untouched on this branch. This is a documented deviation from the "same Work Unit" clause of 20 §14.
- **Integration law**: when F03 becomes PUBLISHED_FIELD, STOP before F03 integration → reconstruct F03 → synchronize this branch with the published F03 commit → contract and dependency DeepSweep → only then may WAIT_FOR_F03 relations become candidates.

## Pending ledger reconciliation (execute at post-F03 sync, SF01-HD-5)
Allocate the next free numbers after F03's own entries, then add to 16 §41 (+ §6 table, YAML, counts) and 20 §15:
1. REC-?? / NQ-DEC-??: SF-01 authorized as pulled-forward Symbiotic Frontend Foundation under doc 21; F11 unchanged (SF01-HD-1).
2. REC-?? / NQ-DEC-??: Real-stack proof for frontend-only Fields runs in an isolated environment (own project, DB, no shared ports) (SF01-HD-2).
3. REC-?? / NQ-DEC-??: Frontend Fields may not modify, infer, duplicate or stabilize an unpublished Field's contracts; contact-zone exclusion (SF01-HD-3).
4. REC-??: Doc 21 status as governing frontend architecture, persisted with SF-01 (SF01-HD-4); reconcile PF-01/CF-01..09 with the 19 F00–F12 DAG (open relation OR-A).
5. REC-??: The ledger deferral itself (SF01-HD-5).

## Upstream dependencies
F02 (published `2f33be1`, identity record `bea864b`, the SF-01 base). F03: in progress and excluded for the whole of
SF-01's execution; published afterwards as `0d59ae3f9be5f3a3297d43ab55c70005c41aa68d` (publication record
`c9d86bab64505845f406ba43a8c78ac185383680`, signed tag `field-F03`). Not yet integrated.

## Downstream
Integration law, **now ACTIVE** (F03 published), not yet executed. In order:
1. Reconstruct published F03.
2. Synchronize `frontend-symbiotic` with the published F03 commit.
3. Contract and dependency DeepSweep.
4. Ledger reconciliation (the pending entries above, SF01-HD-5).
5. Stage 2: Session-page integration (CF-03 on SF-01 primitives).

Every WAIT_FOR_F03 relation stays WAIT_FOR_F03 until steps 1–3 have run.
