# FIELD STATUS

## Field
F04 — AI BOUNDARY · POST-BURST SENSEMAKING

## Semantic regime
Derived machine participation after protected human generation (§24).

## Status
**F04_BACKEND_REVIEW_PASS_PRE_WU04_8 — REVIEWED BACKEND, CHECKPOINTED (not PUBLISHED_FIELD)** (2026-09-26)

Successor record, written by WU-PFC-00 (predecessor consolidation) under explicit
human authority. The history below is kept unchanged.

- **Independent re-review:** `F04_BACKEND_REVIEW_PASS_PRE_WU04_8` (2026-09-25,
  independent read-only session). Persisted verbatim in
  `review/INDEPENDENT_BACKEND_REVIEW_2_PASS.md`. The first review
  (`F04_BACKEND_REPAIR_REQUIRED`) is in
  `review/INDEPENDENT_BACKEND_REVIEW_1_REPAIR_REQUIRED.md`.
- **What is reviewed:** the F04 **backend** before WU-04.8. It is a reviewed field
  for that scope only.
- **Checkpoint:** the backend and this evidence are committed on branch
  `f04-implementation` and tagged `checkpoint-F04-backend-review-pass`. The
  commit identity is recorded in `CHECKPOINT_WU-PFC-00.md` by the follow-up
  identity commit (F02/F03 precedent).
- **Reconstruction:** the committed tree is byte-identical to the tree the
  re-review covered (`CHECKPOINT_WU-PFC-00.md` §3).
- **Not claimed:** FIELD_GREEN for all of F04, PUBLISHED_FIELD, COMPLETE. The
  checkpoint is a recoverable predecessor, not a publication.
- **Still open:** WU-04.8 BLOCKED_ON_H8_FOR_WU_04_8; HARD-DEP-002 external
  (MockProvider ceiling unchanged; HD-20 unchanged); the re-review's
  non-blocking findings 1–11 (items 3/4 before HARD-DEP-002, item 11 → F08);
  observations O-1, O-3..O-7 (SWEEPS §4).
- **Drift recorded, not rewritten:** master's `F04/STATUS.md` stub still says
  NOT_STARTED (master is not touched by this Work Unit).

## Previous status (history)
**F04_R1_R2_REPAIR_READY_FOR_INDEPENDENT_REVIEW** (2026-09-25)

The independent read-only backend review returned **F04_BACKEND_REPAIR_REQUIRED**
with exactly two material defects, FBR-F04-R1 and FBR-F04-R2. Both are now
repaired at their root and re-proven (`REPAIR_R1_R2.md`):

- **R1:** the accepted artifact is the exact validated bytes, bound to its
  VALIDATED proof. The resolver goes through the proof, and a DB binding
  trigger enforces it.
- **R2:** no VALIDATED proof exists outside the PI-1 bundle. A denied
  acceptance is FAILED and has no proof. Deferred constraint triggers enforce
  it at commit. C2-9 is withdrawn.

Proof after the repair:
- regression 1712 passed / 2 skipped, and 888 passed without a DB;
- mutation proof 24 / 24;
- 3 new real-commit proofs;
- runtime proof re-run on a recreated `nquiry_f04_red_runtime`, with the PI-1
  closure evaluated by PostgreSQL over the committed rows.

The reviewed input `review/BACKEND_REVIEW_BUNDLE.md` (sha256 `c27af32d…`) is
preserved unchanged. The independent re-review is **not** performed here.

Previous state, kept below as history: READY_FOR_HUMAN_BACKEND_REVIEW_PRE_WU04_8
(2026-09-25). The text below describes that state; its proof counts were
superseded by the repair.

The backend of the reviewed architecture (revision 6, handoff `d9410b3`) is
materialized in the RED worktree `worktrees/f04-implementation`, branch
`f04-implementation`, as an **uncommitted working copy**. Nothing is staged,
committed, tagged, pushed or published. No APPROVED / FIELD_GREEN /
RELEASE_READY / F04 COMPLETE claim is made: WU-04.8 is blocked and the provider
is the MockProvider.

| WU | State | Report |
|---|---|---|
| 04.0 ledger / home pointers, bindings | DONE | WU-04.0.md, IMPLEMENTATION_BINDINGS.md |
| 04.1 BEGIN_ANALYSIS | DONE | WU-04.1.md |
| 04.2 protected set ↔ AI (FBR-3) | DONE | WU-04.2.md |
| 04.3 SYSTEM_OPERATION, OA relation, record integrity | DONE | WU-04.3.md |
| 04.4 contracts + frozen-set manifest | DONE | WU-04.4.md |
| 04.5 run, acceptance, RETRY / RECOVERY | DONE | WU-04.5.md |
| 04.6 mock lane | DONE | WU-04.6.md |
| 04.9 clustering | DONE | WU-04.9.md |
| 04.7 projection | DONE | WU-04.7.md |
| 04.10 backend proof | DONE (backend; mock ceiling) | WU-04.10.md, PROOF_MATRIX.md, SWEEPS.md, evidence/ |
| **04.8 frontend** | **BLOCKED_ON_H8_FOR_WU_04_8** | WU-04.8.md |

**Proof (evidence/):**
- Full regression 1699 passed / 2 skipped (baseline 1535 / 2); no-DB run 888
  passed; F04 tests 180 passed.
- Mutation proof 20 / 20 killed.
- 6 real-concurrency proofs.
- Runtime proof on two live uvicorn processes over an isolated DB; F1
  startup refusal on a third.
- ruff, format, mypy and every repository gate clean.

**FBR status:**
- FBR-F04-1..9 and 11..13 are materialized (IMPLEMENTATION_BINDINGS,
  PROOF_MATRIX).
- Three implementation-time relations were found and repaired at the root
  (FBR-F04-I1..I3). None changes reviewed semantics.
- No new Case 3.

**External / open:**
- H-8 (SF-01 integration order) blocks WU-04.8 only.
- HARD-DEP-002 (real provider) is external. MOCK RESULT ≠ REAL PROVIDER PROOF.

**Field protection (re-verified 2026-09-25 12:30, after the R1 / R2 repair):**
BLUE `c9d86ba` (9 entries) and main `c529d3d` (32) are unchanged. CYAN `644e1c8`
is at 44 entries, still changing under the other active session; this work
wrote nothing there. Shared DBs are at `f6b2c4d9a318`. No clone DB is left.

**Field protection (verified 2026-09-25 11:02):**
- BLUE (`.claude/worktrees/local-login-auth` `c9d86ba`, 9 status entries)
  and the main checkout (`c529d3d`, 32 entries) are unchanged since
  09:59.
- CYAN (`worktrees/frontend-symbiotic` `644e1c8`) went from 41 to 47 entries
  under `apps/web`, through another active session. This work wrote nothing
  there.
- Shared DBs `nquiry` / `nquiry_test` are unchanged (`f6b2c4d9a318`).

## Status before implementation (architecture phase, kept as history)
NOT_STARTED — ARCHITECTURE_REVIEW_PASS (architecture revision 6)

**F04_ARCHITECTURE_REVIEW_PASS** (ChatGPT architecture review, relayed by the
human operator, 2026-09-24). The record is in FIELD_REVIEW.md, including the
review conclusions and the pinned checksums of the approved revision-6
inputs.

Review history:

| Revision | Result |
|---|---|
| 3 | HOLD |
| 4 | HOLD |
| 5 | HOLD |
| 6 | **PASS** |

No F04 Case-3 decision is open. H-8 (SF-01 integration order) is open and
non-blocking. Implementation is **NOT_STARTED** and needs explicit F04
implementation authority.

**Implementation has not started.** Every First Broken Relation has a
defined root repair at architecture level; none is materialized in code,
schema or tests.

The architecture was reconstructed on 2026-09-24 from published F03
(`0d59ae3`, tag `field-F03`, `origin/master` `c9d86ba`). See
F04_ARCHITECTURE_RECONSTRUCTION.md (revision 6) and HUMAN_DECISIONS.md.

**Review history** (reviewed inputs preserved in `review/`; revision 6
PASS, see FIELD_REVIEW.md):
- Revision 3 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 and ledger drift.
- Revision 4 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 PASS, with the
  operation-scoped authorization model accepted; FBR-F04-12 and
  current-state drift remained.
- Revision 5 → ARCHITECTURE_REVIEW_HOLD: FBR-F04-11 and FBR-F04-12 PASS;
  FBR-F04-13 (the end boundary did not admit the legal
  unconsumed-authorization recovery path) remained.

**Revision 6 resolves at architecture level:**
- FBR-F04-13. An OA is consumed by at most one generation and may remain
  unconsumed. Controller requests are either RETRY (after a FAILED / REJECTED
  generation) or RECOVERY (superseding an unconsumed OA, with the case
  persisted). A superseded OA never executes. The end boundary, Work Units
  and falsifiers are updated, and a final closure sweep covers all paths
  P1-P9.

**Revision 5 resolved at architecture level:**
- FBR-F04-12. The accepted AIOP-001 artifact behind every AIOP-002
  authorization (OA-3 and OA-4) and every retry chain reference is persisted
  write-once and resolved from immutable records only (§0.1 rule 8). The
  Inverse DeepSweep covers the original and re-run branches of both
  operations.
- Current-state drift: ledger 51 decisions / 42 ESTABLISHED / REC-027;
  H-7 no longer listed as open; NOT_STARTED wording.

Derived from HD-16, HD-17 and HD-23; no new human decision.

**Decisions and open items:**
- **Closed:** all seven F04 Case-3 decisions, C3-F04-1..7, by HD-16..HD-23
  (NQ-DEC-044..051; 16 §41 REC-018..REC-027; 20 §7 SYSTEM_OPERATION
  successor note, decided and not yet materialized; §15B). No F04 Case-3
  relation is open.
- **H-7 closed:** historical documentation drift. Published F03 is not
  rewritten; F04 uses the verified published identities.
- **H-8 open, non-blocking.** SF-01:
  - Field commit `447b24e`, documentation identity commit `c944b95`;
  - worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic`,
    branch `frontend-symbiotic`;
  - clean, locally committed, not tagged, not pushed;
  - F03 integration not started.

  The integration order is decided before WU-04.8. It is not a Case 3.

**First Broken Relations:** thirteen.
- FBR-F04-1..9 and 11..13 have defined root repairs. None is materialized
  (FBR-F04-11..13 are resolved at architecture level).
- FBR-F04-10 is closed by the H-7 resolution.

**Real provider lane:** blocked by HARD-DEP-002. F04 passes under a
declared MockProvider ceiling (HD-19). Mock proofs never count toward
BEGIN_REFLECTION for non-fixture Sessions (HD-20).

## Upstream dependencies
F03

## Downstream dependencies
F05
