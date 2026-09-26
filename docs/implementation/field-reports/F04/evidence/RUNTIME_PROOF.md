# F04 runtime proof: the RED API as a real process (backend, mock ceiling)

**Date:** 2026-09-25. **Tree:** RED worktree, uncommitted working copy over
`d9410b3`.

**Database:** isolated `nquiry_f04_red_runtime` on the shared local PostgreSQL
(created, roles applied from `infra/local/db_roles.sql`, migrated to head
`c2e7b9a4f513`, `verify_migrations` PASS). The shared `nquiry` / `nquiry_test`
databases and the running containers (which serve BLUE) were not touched.

**Driver:** `tests/e2e/f04_runtime_proof.py`. `seed` drives the real
F02/F03 handlers and commits a Session at QUESTION_CAPTURE. It includes one
prompt-injection Question. `drive` then speaks only HTTP to a separate
`uvicorn nquiry_api.main:app` process: login cookies, `Idempotency-Key`, the
real routes.

## 1. F1: the mock is refused in production

```
NQUIRY_ENVIRONMENT=PRODUCTION NQUIRY_AI_PROVIDER=mock uvicorn nquiry_api.main:app --port 18080
→ exit=1
application.analysis_runtime.MockProviderForbidden: MockProvider is dev-runtime only (HD-19); refused for NQUIRY_ENVIRONMENT='PRODUCTION'
```

## 2. Process A: dev + mock, AIOP-001 scripted to TIME OUT (H4 first half)

Settings: `NQUIRY_ENVIRONMENT=DEVELOPMENT NQUIRY_AI_PROVIDER=mock
NQUIRY_AI_MOCK_OUTCOME_AIOP_001=TIMEOUT`, port 18081. Full output:
`runtime_phase1_begin_failing.json`.

- The participant's begin → `denied` (`DENIED_NO_MATCHING_BINDING`) (H5).
- The controller's begin → `200 committed`. The run is a **separate fact**:
  `FAILED / PROVIDER_TIMEOUT`.
- Session `ANALYSIS`. `establishedBy = CMD_BEGIN_ANALYSIS`, BINDING,
  `SESSION:<id>` (H1).
- The participant sees `analysis.status = UNAVAILABLE` and
  `clustering.status = NOT_RUN` (H6 / K7). The frozen set is still served (F3).
- Controller capability: `REQUEST_QUESTION_ANALYSIS` available, `case = RETRY`.
  Participant: unavailable, with the server's reason (G5).

## 3. Process B: dev + mock, unscripted (H4 second half; H2, H3)

Port 18082: a new process over the same committed database. Full output:
`runtime_phase2_retry.json`.

- Controller request with the wrong case (`RECOVERY`) → `rejected
  REQUEST_CASE_MISMATCH:RETRY` (E18). The Owner's RETRY → 403.
- Controller RETRY → `200`. Its run: AIOP-001 `ACCEPTED`, then automatically
  AIOP-002 `ACCEPTED` (HD-23).
- `audience_views_identical: true` across controller, participant, Owner and
  member (G1 / H3). A non-member → 403 (G2).
- Marker `origin AI · derived · PROPOSAL · MOCK / NON_PROOF`; the artifact
  `proofClass = MOCK_NON_PROOF` (F2).
- Generations: `AIOP-001 FAILED OA-1`, `AIOP-001 VALIDATED OA-2 RETRY`,
  `AIOP-002 VALIDATED OA-3`. Two clusters.
- The human Questions are served verbatim, including the injection text,
  which stayed DATA (D6).
- After acceptance: `REQUEST_QUESTION_ANALYSIS` unavailable,
  `RESULT_ALREADY_ACCEPTED` (R2).

## 4. Inverse sweep over what the processes committed

`runtime_inverse_provenance.txt`: the persisted-only resolver walks both
accepted artifacts to the BEGIN_ANALYSIS root (BINDING, `SESSION:<id>`).
The analysis follows branch 2b (OA-2 RETRY ← CMD_REQUEST_QUESTION_ANALYSIS
BINDING). The clustering follows branch 4a, via OA-3 authorized by the request
(K9).

Audit rows:
- BEGIN_ANALYSIS and REQUEST: `HUMAN_USER / BINDING`.
- The two EXECUTE and two ACCEPT commands: `SYSTEM_SERVICE / SYSTEM_OPERATION`.
- Scope everywhere: `SESSION:<id>`.
- The only `session:*` after-state is BEGIN_ANALYSIS (EC-2).

`normalized_text` written: 0 (HD-18 / D8).

## 5. Re-run after the independent-review repair R1 / R2 (2026-09-25)

The pre-repair runtime rows are append-only and violated R1. Their before-state
is preserved in `repair_r1_r2_before_state.md`, and sections 1-4 above describe
that pre-repair run. The runtime DB was therefore **recreated** (migrated to
`e7c1d4a9b206`), and the whole proof was re-run the same way:
`runtime_r1r2_f1_production_refusal.txt`, `runtime_r1r2_phase1_begin_failing.json`,
`runtime_r1r2_phase2_retry.json`.

Behaviour is identical. The persisted state now closes PI-1
(`runtime_r1r2_persisted_closure.txt`):
- both accepted artifacts: `sha256(content) = content_fingerprint =
  proof.output_fingerprint`, VALIDATED;
- 0 VALIDATED proofs without their VALIDATED generation and artifact;
- 0 VALIDATED generations without their proof and artifact;
- the FAILED generation has no proof;
- the inverse chains pass through the VALIDATED proof.

## Not claimed

- The browser half (H1-H7 in a real browser) is WU-04.8:
  **BLOCKED_ON_H8_FOR_WU_04_8**.
- The provider is MockProvider. MOCK RESULT ≠ REAL PROVIDER PROOF.
  HARD-DEP-002 (real provider) is external and untouched.
