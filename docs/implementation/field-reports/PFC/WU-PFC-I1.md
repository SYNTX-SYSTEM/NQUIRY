# WU-PFC-I1 — Predecessor Integration (F04 line + PFC-A1 line)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-I1 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-0 Predecessor Consolidation (integration) |
| Colour / role / model | RED · integration · Claude Opus 5.5 |
| Human authorization | "NQUIRY_PRODUCT_FUNCTION_COMPLETION AUTONOMOUS SFE EXECUTION AUTHORIZATION" (2026-09-26). It names the accepted predecessors (`origin/pfc-architecture`, `checkpoint-F04-backend-review-pass`, WU-PFC-A1) and grants: create isolated branches and worktrees, commit, push, checkpoint-tag. |
| Why this Work Unit exists (derived) | The remaining derivable relations must be built on the complete accepted backend. F08 events include the F04 event producers (AI_OPERATION_REQUESTED, AI_GENERATION_REQUESTED, SESSION_ANALYSIS_BEGUN), and 19 L3040 forbids parallel efforts that change the same semantic contract. Until now the two accepted lines diverged at `c9d86ba`: F04 on `f04-implementation`, and PFC-A1 plus Architecture 25 plus the master docs on `pfc-a1-challenge-frame`. |
| Current state | `f04-implementation` = `9d21018` (tag `checkpoint-F04-backend-review-pass` → `b31264e`). `pfc-a1-challenge-frame` = `0ea136d` (tag `checkpoint-PFC-A1` → `71b3bab`). Merge base `c9d86ba`. |
| Baseline evidence | F04: 1712 passed / 2 skipped live, 888 passed no-DB (CHECKPOINT_WU-PFC-00). PFC-A1: 1558 / 2 live (incl. 23 A1 falsifiers). F04 mutation proof PASS. A1 mutation 18/18. |
| Recoverable predecessors | Both tags above (signed, remote-verified). |
| State isolation | New worktree `worktrees/pfc-integration`, branch `pfc-integration`. New DB `nquiry_pfc_int_test` (roles applied, migrated to `e7c1d4a9b206`, verify_migrations PASS). |
| Authorized delta | A merge commit only. No content edits to either line. |
| Must become true | One tree carries F04 and PFC-A1 together, and every proof of both lines holds on it. |
| Must remain true | F02/F03 semantics; F04 HD-16..23, PI-1..6, MockProvider ceiling, HD-20; PFC-A1 invariants; BLUE/master untouched; CYAN untouched. |
| Must remain impossible | History rewrite; a changed F04 or A1 semantic; a merged migration fork (two heads); a claim of REVIEWED_FIELD or PUBLISHED_FIELD. |
| Falsifiers | The complete suites and both mutation proofs of the two lines; `verify_migrations` single head. |
| Stop conditions | A merge conflict with semantic content; any regression; two migration heads. |

## Execution

1. **Merge.** `git merge --no-ff -S 9d21018` into `0ea136d` gives `81f208b` (signed, parents `0ea136d` and `9d21018`). Automatic merge, no conflicts. Git auto-merged the only two files both lines changed: `apps/api/src/nquiry_api/http/inquiry.py` (A1: body fields; F04: analysis routes) and `packages/application/inquiry_queries.py` (A1: the frame in `challenge_detail`; F04: `position.analysis`). They touch disjoint regions. The merged tree differs from the F04 line only by the PFC-A1 change set plus the master documentation, and from the PFC-A1 line only by the F04 change set.
2. **Migrations.** A1 has no migration, so the F04 chain continues from `f6b2c4d9a318`. Result: 28 revisions, **single head `e7c1d4a9b206`**, STATIC and LIVE PASS.
3. **Regression (`evidence/i1_regression.txt`).**
   - Live: **1735 passed, 2 skipped** = 1712 (F04) + 23 (A1).
   - No-DB: **888 passed**, 849 skipped = 826 + 23 A1 skips.
   - Both counts are exact sums of the predecessor baselines, so no test was lost or silently changed.
4. **Static checks.**
   - ruff check: clean.
   - mypy (CI scope): 0 issues in 190 files.
   - Three architecture/import checks: PASS.
   - `ruff format --check` reports one file, the hash-bound reviewed input `F04/review/BACKEND_REVIEW_BUNDLE.md`, which reports identically on the F04 checkpoint itself. Inherited; not modified.
5. **Mutation proofs on the merged tree.**
   - F04: `F04_MUTATION_PROOF::PASS`, 24 mutants killed (`evidence/i1_f04_mutation_proof.txt`).
   - PFC-A1: 18/18 killed (`evidence/i1_a1_mutation_proof.txt`).
   - The merged files still carry guarded relations for both lines.
6. **Propagation.** AFFECTED: the branch topology only. NOT AFFECTED (content unchanged relative to the respective predecessor): domain, persistence, authority, API, projections, CYAN, BLUE/master.
7. **Inverse proof.** Every line of the merged tree traces to one of two signed, tagged predecessors through a signed merge commit.
8. **Deep sweeps.** No semantic drift, since there are no content edits. No authority leakage. Migration drift: none (single head).
9. **Field reconstruction.** See `NQUIRY_PRODUCT_FUNCTION_COMPLETION_FIELD_REPORT.md`.

## Resulting status

**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-I1`; identity in `CHECKPOINT_WU-PFC-I1.md`). Not REVIEWED_FIELD, not PUBLISHED_FIELD, not merged into master. `pfc-integration` is the predecessor line for all later PFC Work Units.
