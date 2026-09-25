# SF-04 — STATUS
FIELD: SF-04 — NQUIRY SYMBIOTIC FIELD ORGANISM (doc 25 materialization on the SF-02/SF-03 tree)
STATE: READY_FOR_HUMAN_FRONTEND_REVIEW
DATE: 2026-09-25

| Item | Value |
|---|---|
| worktree / branch / HEAD | `worktrees/frontend-symbiotic` · `frontend-symbiotic` · `644e1c8` (+ uncommitted SF-02/SF-03/SF-04 tree) |
| commit / tag / push / PUBLISHED / FIELD_GREEN | none (human commit gate) |
| BLUE (F02/F03) / RED (F04) | untouched |
| architecture | doc 25 `25_NQIRY_SYMBIOTIC_FIELD_ORGANISM_ARCHITECTURE.md` (sha256 `1e2b4666f587855d…`) |
| L0 / L5 | vitest 267/267 · tsc 0 · eslint clean |
| L3 mocked (desktop + phone) | 132 / 132 (run 8, final tree; desktop + Pixel 7; 30 SF-04 cases + SF-01/SF-03/F01/F02 regression) |
| L7 real stack (alone) | 14 / 14 (run 8, final tree, 8.3 min at load ≈ 4.6; earlier runs 12/14 with the F03 protected spec over its 90 s budget — root-repaired, see tests/SF04-tests.md) |
| H harness (53 states, runtime :13400) | 53 / 53 PASS (run-7, final tree; axe 0 findings, every focus stop visible, no page errors, no overflow) |
| P perf-ab (×4 throttle) | Access 16.6 · Workspaces 16.6 · Challenge 16.8 ms rAF median at ×4 throttle (p90 ≤ 19.2); hover 89 ms, trial click 184 ms (performance/SF04-performance.md) |
| runtime for the human review | http://127.0.0.1:13400 (compose `nquiry-sf04-inspect`; SF-03 :13300 and SF-02 :13200 still up) |
| reports | architecture-binding/ (WU-00, WU-02-04, WU-05-09) · projection-authority/ (WU-01) · tests/ · accessibility/ · performance/ · browser-evidence/ (harness, run-1..4) · review/ (FRONTEND_BROWSER_REVIEW, SWEEPS) · PROOF_MATRIX · CHATGPT_REVIEW · FIELD_REVIEW |
| Case 3 | none raised |
| human items | FIELD_REVIEW.md §6 |
