# SF-05 — STATUS
FIELD: NQUIRY Symbiotic Frontend Human Review Repair (doc 26 on the SF-04 tree)
STATE: READY_FOR_HUMAN_FRONTEND_REVIEW
DATE: 2026-09-25

| Item | Value |
|---|---|
| worktree / branch / HEAD | `worktrees/frontend-symbiotic` · `frontend-symbiotic` · `644e1c8` (+ uncommitted SF-02…SF-05 tree) |
| commit / tag / push / merge / publish | none (commit gate: human) |
| BLUE / RED | untouched |
| architecture | doc 26 `26_NQIRY_SYMBIOTIC_FRONTEND_HUMAN_REVIEW_REPAIR_ARCHITECTURE.md` (sha256 `14ed130a7b8c5568…`) |
| L0 / L5 | 287 / 287 (25 files; SF-05 adds workspaces 7 · sf05-primitives 9 · fieldEvent 4; sf03/sf04 primitives updated) · tsc 0 errors · eslint clean (React Compiler rules) |
| L3 mocked (desktop + phone) | 168 / 168 — desktop 1280 + Pixel 7, 2.7 min (sf05 36 cases incl. reduced motion; sf04 30; sf01/sf03/decision/etc. regression) |
| L7 real stack (alone) | F03 protected human question spec alone 2 / 2 (2.6 min, load ≈ 5) · full lane: 12 / 14 in 9.5 min (full parallel lane, load ≈ 6): the F03 protected human question spec (desktop + mobile) hit its 90 s budget while taking a screenshot, exactly as in chain 5; it passes alone 2 / 2 on this tree (11 min earlier) and in every isolated run since chain 6 — recorded as observation 7, not a regression |
| H harness (68 states, runtime :13400) | 68 / 68 (run-10; SF-04 states 1–53 + SF-05 54–68; runtime rebuilt from this tree, 30 same-named Workspaces in the scenario) |
| P perf-ab (×4) | access 16.7 ms · Challenge 16.9 ms · Workspaces overview 22.8 ms (30-capsule constellation) rAF median at ×4; hover 138 ms; trial click 315 ms |
| runtime for the human review | http://127.0.0.1:13400 (persistent review service; rebuilt from this tree) |
| reports | FIELD_REVIEW.md · PROOF_MATRIX.md · CHATGPT_REVIEW.md · architecture-binding/ · tests/ · review/ (browser review guide, sweeps) · browser-evidence/ (harness, run-1…run-10; run-10 = final) · performance/perf-ab-final.md |
| Case 3 | none raised |

## Post-review note (2026-09-25, late)
The human review rejected the Workspace overview geometry of this Field (ring segmentation + capsule constellation) and a follow-up bounded-visibility experiment. By human instruction the Workspace field was restored to the SF-04 single containment ring (founding relation + every accessible Workspace; id normalization and homonym distinguisher kept), the stack capsule tuning was reverted to SF-04 (`width: auto`, 320 px membrane), and the review runtime database (:13400) was recreated with the three identities and one review scenario. The HR-01/HR-02 geometry rows, harness states 57–60 and the run-1…run-10 Workspace screenshots above describe the superseded geometry. Run screenshots are kept on disk, not in git (MANIFEST.md / results.json are committed).
