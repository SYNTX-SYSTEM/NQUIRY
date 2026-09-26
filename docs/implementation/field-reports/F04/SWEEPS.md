# F04 — Recursive and inverse DeepSweep after backend materialization

This sweep runs over the materialized code, schema and tests, not over the
architecture text. The architecture sweeps (§10 / §11 of the reconstruction)
are the expectation. Each finding below is checked against evidence.

## 1. Recursive (outward) sweep

| Edge | Finding | Evidence |
|---|---|---|
| **Producer: F03 frozen set** | Read-only. BEGIN_ANALYSIS and every run re-verify F (`verify_frozen_set`); a mismatch is BLOCKED / NOT_EXECUTED. No F04 write reaches `questions`, `burst_question_memberships` or `question_bursts`. `normalized_text` stays NULL. | A4, D2, D8, E5 snapshots, runtime `normalized_text written 0` |
| **F03 semantics** | Unchanged. The only F03-adjacent code change is the BND-008 / guard repair (FBR-F04-3), which *narrows* AI during the Burst. Every F03 test is green. | B4, full regression |
| **Parent / governance** | HD-17's fifth source exists in the audit CHECK, `AuthoritySourceType`, the audit model and BND-014. It is never SYSTEM_DERIVED. D8 / BND-011 / BND-012 are not consulted. HD-1 is intact: only BEGIN_ANALYSIS changes Session state. | C1-C4, A9 / EC-2, runtime audit |
| **Authority** | Every AI effect resolves to one human BINDING act (BEGIN_ANALYSIS or a controller request). SYSTEM_SERVICE is a fixed identity, constructed only by `analysis_system`. | PI-3 gate, inverse tests, runtime chain |
| **Siblings** | `_run` is reused for BEGIN_ANALYSIS and the requests. `establishedBy` is unaffected: system commits write no `session:*` after-state. The BND-008 twin (`burst_contamination`) was repaired identically, and the differential test stays green. **Found and repaired:** the audit-model vocabulary (FBR-F04-I1) and the P-23 mock-construction gate (FBR-F04-I2). | IMPLEMENTATION_BINDINGS §3 |
| **Persistence** | Two migrations: upgrade, downgrade and re-upgrade are clean, with a single head. New tables carry RLS; the RLS registry test is updated. Every uniqueness rule of §10 is a DB constraint. | `verify_migrations`, `tests/security/test_workspace.py` |
| **Runtime** | Mock dev-only; startup refusal proven on a real process. No provider means UNAVAILABLE, never a substitute. Execution is synchronous after the commit, with no worker. The worker imports no AI (gate). | F1, static gates |
| **API** | Three routes. The response separates the committed Command from the run outcome. A replay executes nothing (rule 5). Malformed input → `rejected`. | `test_http_f04.py` |
| **Frontend (RED `apps/web`)** | Unchanged. Actions are addressed by name, with no generic iteration and no runtime schema, so the additive `analysis` / actions cannot surface. **BLUE and CYAN:** untouched (see §3). | grep over `apps/web` |
| **F05** | HD-20 is enforceable: proof → generation → `provider = mock`, and the artifact carries `proof_class = MOCK_NON_PROOF`. In the mock runtime, governed Sessions stay in ANALYSIS (R5), unchanged. | F5, provenance |
| **F08 / F09** | New outbox event names (C2-8) have no consumer yet. A generation stuck RUNNING (a process stop after T2a, or an INDETERMINATE acceptance) blocks RETRY and RECOVERY. This is the disclosed ceiling P8 / E10, and its recovery belongs to F09. | E10, K20 |

## 2. Inverse sweep (from each visible result back to its human origin)

| Result | Chain (persisted records only) | Proof |
|---|---|---|
| Session ANALYSIS | projection ← Session ← CMD_BEGIN_ANALYSIS audit (BINDING `SESSION:<id>`, controller) ← grant ← FOUNDING | A1, runtime `establishedBy` |
| Analysis artifact, branch 2a | artifact ← **proof VALIDATED over the exact bytes (R1)** ← accept (SYSTEM_OPERATION, ref BEGIN_ANALYSIS) ← generation (OA-1) ← BEGIN_ANALYSIS (BINDING) | `test_p1_*` |
| Analysis artifact, branch 2b RETRY | … generation (OA-2 RETRY, `retry_of`) ← request (BINDING) → chain root BEGIN_ANALYSIS | `test_p2_e16_*`, runtime |
| Analysis artifact, branch 2b RECOVERY | … OA-2 RECOVERY, supersedes OA-1, no `retry_of` | `test_p3_*` |
| Clusters, branch 4a | cluster run ← accept (ref C) ← generation (OA-3, X) ← X's chain (2a / 2b) ← BEGIN_ANALYSIS | `test_p1_*`, runtime |
| Clusters, branch 4b | OA-4 RETRY / RECOVERY, X persisted on the request's OA row and on the generation | `test_p5_*`, `test_p6_k19_*` |
| "Analysis unavailable" | projection ← generation FAILED / REJECTED (failure code) ← EXECUTE (SYSTEM_OPERATION) ← OA | G5, runtime phase 1 |
| Negative inverse | no accepted AIOP-001 artifact → no OA-3, no AIOP-002 generation, no cluster | K7 |

The resolver reads only immutable records. The static test proves it reads no
`status`, `state`, `record_version` or Session table. Every link it follows
is write-once: an UPDATE of any of them is a DB error.

## 3. Field protection

- **BLUE** (`.claude/worktrees/local-login-auth`, `c9d86ba`) and the main
  checkout (`c529d3d`, uncommitted entries from another session): not
  modified by this work.
- **CYAN** (`worktrees/frontend-symbiotic`, `644e1c8`; its uncommitted entries
  belong to another active session): not modified by this work.
- HEAD and status counts were recorded before and after (see STATUS.md).
- Shared DBs `nquiry` / `nquiry_test`: untouched (head `f6b2c4d9a318`).
- The shared containers were not rebuilt.

## 4. Observations for the human backend review (not Case 3)

1. **O-1 (BND-007 form).** BND-007 has no state-preserving form (it evaluates
   transitions). The system path's "Session ANALYSIS" predicate (§6) is
   therefore enforced by the SYSTEM_OPERATION resolver at precommit and again
   at commit, not by a BND-007 proof. It is behaviour-equivalent (E12, C3).
   The recorded boundary id differs.
2. **O-2 (C2-9): superseded by the R2 repair (independent review).** A
   VALIDATED candidate whose acceptance fails is recorded FAILED
   (`ACCEPTANCE_DENIED:*`, `failure_detail_ref =
   validated_output_fingerprint:<sha256>`) with **no** proof row. RETRY
   applies. See `REPAIR_R1_R2.md`.
3. **O-3 (C2-10).** Effect-free endings (FAILED / REJECTED) are operational
   writes without an audit row. The generation row is the record.
4. **O-4 (C2-11).** STAGING is refused for the mock (a stricter reading of
   "dev runtime only").
5. **O-5.** The system run executes synchronously inside the HTTP request (no
   worker by design). With a real provider this is request latency: an
   F08 / HARD-DEP-002 concern.
6. **O-6.** Two isolated databases were created on the shared PostgreSQL:
   `nquiry_f04_red_test` and `nquiry_f04_red_runtime`. Keeping or dropping
   them is the operator's choice.
7. **O-7.** `20_SYSTEM_FIELD_ENGINEERING.md` §7 still says SYSTEM_OPERATION is
   "decided, not yet materialized". It was not edited, because it is a pinned
   review input. It should be updated when the materialization is reviewed
   and published.

No new Case-3 relation was found.

## 5. Delta sweep for the R1 / R2 repair (independent review)

- **Recursive.**
  - The producer (`_accept`, `_finalize`) and the resolver / reader changed.
  - One migration adds three triggers. No schema shape changed, and no
    API / projection shape changed.
  - No F03, authority, supersession, RETRY / RECOVERY, SYSTEM_OPERATION or
    mock-lane code changed; their suites are green.
  - F05 now receives the PI-1 guarantee on persisted records.
- **Inverse.** Every accepted artifact resolves through its immutable VALIDATED
  proof, whose fingerprint equals `sha256(content)`, to the generation, OA,
  authorizing Command and BINDING root. No chain ends in trust in code, an
  unbound artifact or an unbound proof. Proven on the fresh runtime DB
  (`evidence/runtime_r1r2_persisted_closure.txt`).
- **No new Case 3.** The reviewer's Human-Authority alternative for R2
  (redefining the proof class) was **not** taken. The chosen repair restores
  the reviewed PI-1 and 06 §16 semantics.
