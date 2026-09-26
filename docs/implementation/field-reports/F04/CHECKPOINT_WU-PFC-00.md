# WU-PFC-00 — Predecessor consolidation for the reviewed F04 backend

**Parent Field:** NQUIRY_PRODUCT_FUNCTION_COMPLETION.
**Child Field:** PFC-0 Predecessor Consolidation. **Colour:** RED.
**Human authorization (2026-09-26):** "WU-PFC-00 IS AUTHORIZED … Human Authority
granted for WU-PFC-00 only."
**Execution invariant:** Architecture 25 §23 ("EVERY MATERIAL WORK UNIT MUST
CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE"). This is a non-code Work
Unit (§23.7): its proof is the checkpoint verification of §11 plus field
reconstruction. No product code, schema, API or projection is changed by it.

## 1. Authorized Delta

Make the independently reviewed F04 backend a recoverable, remote-verifiable
predecessor:
- persist the accepted review PASS as repository evidence;
- record successor truth in STATUS / FIELD_REVIEW;
- reconstruct and verify the change set;
- commit on `f04-implementation`, push, tag, verify.

Not authorized and not done: any product function, WU-PFC-A1, PFC-B, F05+,
F04 semantic change, real-provider eligibility, CYAN change, BLUE change,
history rewrite.

## 2. Bound before the Delta

| Item | Value |
|---|---|
| Current state | `f04-implementation` = `origin/f04-implementation` = `d9410b3` (signed). 93 working-copy paths (modified + untracked). DB head of the RED test DB `e7c1d4a9b206`. |
| Recoverable predecessor | `d9410b3` on the remote (architecture revision 6 handoff). |
| State isolation | RED worktree `worktrees/f04-implementation`; isolated DBs `nquiry_f04_red_test`, `nquiry_f04_red_runtime`. |
| Must become true | reviewed backend recoverable and remote-verifiable; review PASS persisted; (Architecture 25 persisted — see §6). |
| Must remain true | F03 semantics; F04 HD-16..23 and PI-1..6; MockProvider ceiling; HD-20; BLUE read-only; CYAN unchanged; no product capability added. |
| Must remain impossible | F05+ behaviour; F04 semantic expansion; invented provider eligibility; CYAN materialization; history rewrite; unverified tag; a PUBLISHED_FIELD claim. |

## 3. Change-set reconstruction (reviewed tree = committed tree)

Method: every working-copy path was hashed and compared with the per-file
checksums in the reviewed input `review/BACKEND_REVIEW_BUNDLE.md` (sha256
`c27af32dd48d9e9157d766d3b0fcb4e7d4f7cf0791023095fa95ab32639bcf7f`), and every
file's modification time was compared with the start of the independent
re-review (2026-09-25T10:42:53Z).

- **No working-copy file was modified after the re-review started.** The newest
  is `STATUS.md`, 2026-09-25 12:30:31 +0200 (10:30:31Z), before this Work Unit.
- **67 of the 83 bundle files are byte-identical** to the first reviewed input.
- **16 bundle files changed** and **10 files are new**. They are exactly the R1/R2
  repair set that the re-review rebuilt from the bundle and reviewed:
  - production: `packages/application/analysis_system.py`,
    `packages/application/analysis_provenance.py`,
    `packages/persistence/provenance_reader.py`;
  - migration: `migrations/versions/e7c1d4a9b206_f04_accepted_output_binding.py`;
  - tests: `tests/e2e/test_f04_accepted_output_binding.py` (new),
    `test_f04_analysis_run.py`, `test_f04_concurrency.py`,
    `test_f04_system_operation_gate.py`; `scripts/f04_mutation_proof.py`;
  - field evidence: `STATUS.md`, `IMPLEMENTATION_BINDINGS.md`, `PROOF_MATRIX.md`,
    `SWEEPS.md`, `WU-04.3.md`, `WU-04.5.md`, `WU-04.10.md`, `REPAIR_R1_R2.md`,
    `evidence/RUNTIME_PROOF.md`, `evidence/regression.txt`, and the new
    `evidence/*r1r2*` and `evidence/repair_r1_r2_before_state.md` files;
  - the reviewed input itself: `review/BACKEND_REVIEW_BUNDLE.md`.
- **Added by this Work Unit (documentation only):**
  `review/INDEPENDENT_BACKEND_REVIEW_1_REPAIR_REQUIRED.md`,
  `review/INDEPENDENT_BACKEND_REVIEW_2_PASS.md`, this file, and successor
  sections in `STATUS.md` and `FIELD_REVIEW.md`.

No production, schema, test or API file differs from the reviewed tree.

## 4. Baseline evidence on the committed tree

Full regression on the exact staged tree (2026-09-26), isolated test DB
`nquiry_f04_red_test` at head `e7c1d4a9b206`:
- live suite: **1712 passed, 2 skipped** (11:07);
- no-DB suite: **888 passed**, 826 skipped.

Identical to the counts the independent re-review accepted (1712 = 1699 + 13
R1/R2 tests). The reviewed bundle is unchanged (sha256 `c27af32d…`).

## 5. Checkpoint identity

Recorded by the follow-up identity commit (F02/F03 precedent: materialization
commit, then an identity-record commit):

| Identity | Value |
|---|---|
| F04 commit | `b31264ec88efd647d0db9143e76a1aeaf93e8a47` (signed, good signature) |
| Predecessor of that commit | `d9410b3a697fb465e1d766f758d9959f44219f62` (fast-forward, no history rewrite) |
| Remote branch | `origin/f04-implementation` |
| Checkpoint tag | `checkpoint-F04-backend-review-pass`, tag object `3f206fd7d67b27bb5b06f8292f9454a78dd690db` (annotated, signed, good signature) |
| Tag target | `b31264ec88efd647d0db9143e76a1aeaf93e8a47` |
| This identity record | the follow-up commit on `f04-implementation` that adds this table (the tag stays on the materialization commit, F02/F03 precedent) |

## 6. Architecture 25

Not handled on this branch. See the WU-PFC-00 completion report: persisting
Architecture 25 on `master` would write to BLUE, which this Work Unit requires
to stay read-only, and carrying it on the F04 branch would mix its authority
with F04. That effect is stopped at a Case-3 boundary for human decision.
