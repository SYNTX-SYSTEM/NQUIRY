# NQUIRY_PRODUCT_FUNCTION_COMPLETION — Rolling Field Report

**Governing architecture:** Architecture 25 (branch `pfc-architecture`, `1eb3799`); §23 execution invariant.
**Method:** SFE Operating Manual v1.4.
**Human authority:** "AUTONOMOUS SFE EXECUTION AUTHORIZATION" (2026-09-26).
**Case 3 boundaries:** `HUMAN_AUTHORITY_QUEUE.md`.
**Predecessor line:** `pfc-integration`.

Product functions use PF numbering (PF01–PF27). F00–F12 are repository Fields.

## 1. Work Units and checkpoints

| # | Work Unit | Branch | Materialization | Tag | Status |
|---|---|---|---|---|---|
| 0 | WU-PFC-00 F04 predecessor consolidation | `f04-implementation` | `b31264e` | `checkpoint-F04-backend-review-pass` | CHECKPOINTED |
| — | Architecture 25 (option b) | `pfc-architecture` | `1eb3799` | — | pushed, not merged |
| 1 | WU-PFC-A1 Challenge frame completion | `pfc-a1-challenge-frame` | `71b3bab` | `checkpoint-PFC-A1` | TECHNICALLY_ACCEPTED, CHECKPOINTED |
| 2 | WU-PFC-I1 predecessor integration (F04 + A1) | `pfc-integration` | `81f208b` | `checkpoint-PFC-I1` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 3 | WU-PFC-F08-1 durable immutable committed Event basis | `pfc-integration` | `298a5d8` | `checkpoint-PFC-F08-1` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 4 | WU-PFC-F08-2 delivery → projection → replay/rebuild; the running worker | `pfc-integration` | `461ade4` | `checkpoint-PFC-F08-2` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 5 | WU-PFC-F08-3 delivery diagnostics and projection freshness | `pfc-integration` | `aea783e` | `checkpoint-PFC-F08-3` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 6 | WU-PFC-F09-1 technical failure envelope (engine facts, API edge, worker survival) | `pfc-integration` | `3dbb6c6` | `checkpoint-PFC-F09-1` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 7 | WU-PFC-F09-2 Workspace isolation and session sweep over every route; fix of a Session-state disclosure to non-members | `pfc-integration` | `0a05e7c` | `checkpoint-PFC-F09-2` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 8 | WU-PFC-F09-3 telemetry non-interference and governed-Command correlation | `pfc-integration` | `d71ab5a` | `checkpoint-PFC-F09-3` | TECHNICALLY_CLOSED, CHECKPOINTED |
| — | **HD-24 (HA-01, Option 03 for Fixture Sessions)** recorded | `pfc-integration` | `c4fded8` | — | Human Authority record (REC-028 / NQ-DEC-052) |
| 9 | WU-PFC-B0 Fixture Session identity (HD-24 rules 1–5) | `pfc-integration` | `ea3af40` | `checkpoint-PFC-B0` | TECHNICALLY_CLOSED, CHECKPOINTED |
| 10 | WU-PFC-B1 TRN-SESS-007 BEGIN_REFLECTION under HD-24 (Fixture Sessions: MOCK_NON_PROOF; real Sessions: HD-20 / Option 01) | `pfc-integration` | see `CHECKPOINT_WU-PFC-B1.md` | `checkpoint-PFC-B1` | TECHNICALLY_CLOSED, CHECKPOINTED |
| — | **F08 Field (backend)** | `pfc-integration` | — | F08-1..3 | **READY_FOR_HUMAN_REVIEW** (14 Phase 8 gate; `F08_FIELD_REVIEW_BUNDLE.md`) |

## 2. Field derivation after WU-PFC-I1

This derivation is based on three read-only reconstructions of 2026-09-26: F08 events, F09 isolation, and the other non-REFLECTION relations.

**Blocked by Human Authority or external dependency** (see the queue): HA-01 … HA-17. The main product chain (F05 → F06 → F07 → graph and export) is blocked at HA-01.

**Derivable now:**

| Candidate | Home | Verdict |
|---|---|---|
| **F08 Consequence Integrity: durable Event basis → envelope → delivery → projection → replay/rebuild** | 19 §28 (STORAGE FREEDOM; "Claude Code may choose"); 19 L1058, L3026–3030 ("After F03: F04 ‖ F08 Event implementation"); 12 §17 (in prototype scope); 09 §15–§18, §70–§75; 10 §17, §56 | **DERIVABLE.** Next Work Units: WU-PFC-F08-1 onward. |
| Documentation drift: stale docstrings (`session_creation_handler` roles; `decision.py` "provenance.py not yet built"; `outbox_worker` citing a missing test file; `IndeterminateBanner` citing a missing test) | code comments | DERIVABLE (Case 2). Folded into the F08 or a sweep Work Unit where the file is touched. |
| `OWNER_ROLE_NOT_ASSIGNABLE` reason code also used for OBSERVER/VIEWER | `membership_operations_handler.py:284`, `http_dispatch.py:676` | Observation only. Renaming a wire reason code is an API contract change; Observer/Viewer assignment itself is HA-13. |

**Not derivable, with reasons:**
- Provenance and reconstruction queries: HA-11 (GAP-11-001).
- Opening a Decision: HA-14.
- Runtime isolation: HA-09 and HA-10.
- F09 recovery: F08 order plus HA-15.
- Challenge update: no command is specified (09 §63/§80), so it would be invented.
- Governance list and revoke endpoints and question queries: specified in 09 but not in the 12 §23 proof set ("Only operations actually exercised by the proof are implemented"). Deferred by 12.

## 3. Product-function status (current)

| PF | Function | Status | Change in this run |
|---|---|---|---|
| PF01 | Challenge Setup | **PARTIAL → frame IMPLEMENTED** (status NQ-GAP-018 and Emotional Temperature HA-06 remain open) | WU-PFC-A1 |
| PF04 | Question Burst | IMPLEMENTED (published F03) | — |
| PF24 | AI Orchestration | PARTIAL: AIOP-001/002 now on a checkpointed predecessor line | WU-PFC-00, I1 |
| PF22 | Audit & Provenance | PARTIAL (views: HA-11) | — |
| PF20 | Session Lifecycle | PARTIAL (007–013: HA-01; cancel: HA-12) | — |
| PF19 | Collaboration | PARTIAL (HA-13) | — |
| PF23 | Domain objects | PARTIAL (Insight, Assumption, Experiment, ImpactChain: HA-01/HA-08) | — |
| PF25/26 | Gateway, cost | PARTIAL (HA-02) | — |
| PF15, PF21 | Selection, Export | BLOCKED (HA-01, HA-04) | — |
| PF02, 03, 08, 09, 12, 13, 16, 17, 27 | — | ARCHITECTURE_ONLY (blocked or excluded; see queue) | — |
| PF05, 06, 07, 11, 14, 18 | — | INTENTIONALLY_DEFERRED | — |
| PF10 | Quality Question Coaching | MISSING (no architecture home) | — |

## 4. First Broken Relations

| FBR | Status |
|---|---|
| FBR-PFC-01 F04 had no recoverable predecessor | **CLOSED** (WU-PFC-00) |
| FBR-PFC-06 Challenge wire contract dropped the frame | **CLOSED** (WU-PFC-A1) |
| FBR-PFC-08 outbox written, never delivered | **CLOSED** for the backend: the durable basis (F08-1), plus delivery, projection, replay and rebuild with the running worker (F08-2), proven on the real stack. Diagnostics and freshness were closed in F08-3. Remaining: frontend freshness and history (needs an API read and CYAN); HA-18 dead-letter status. |
| FBR-PFC-02 REFLECTION gate | BLOCKED (HA-01) |
| FBR-PFC-03/04 Selection, ImpactChain | BLOCKED behind FBR-PFC-02 |
| FBR-PFC-05 Decision only by seed | BLOCKED (HA-14) |
| FBR-PFC-07 no Evidence producer | BLOCKED (HA-08) |
| FBR-PFC-09 runtime superuser | BLOCKED (HA-09/HA-10) |
| FBR-PFC-10 Export | BLOCKED (HA-04) |
| FBR-PFC-11 F04 projection invisible | BLOCKED (HA-03) |

## 5. Resulting Field status

**IN_PROGRESS (autonomous).** Eight Work Units are technically closed and checkpointed (A1, I1, F08-1, F08-2, F08-3, F09-1, F09-2, F09-3). F08 is READY_FOR_HUMAN_REVIEW. F09 is IN_PROGRESS. Test totals on `pfc-integration`: live 1856 passed / 2 skipped; no-DB 908 passed. None is REVIEWED_FIELD. Nothing is PUBLISHED_FIELD. BLUE/master is unchanged.

---

## 6. Field reconstruction at the end of the autonomous run (2026-09-27)

**Global stop condition reached: B, all remaining paths blocked.** Every remaining relation of NQUIRY_PRODUCT_FUNCTION_COMPLETION is one of the following:
- blocked on Human Authority (HA-01, 03–09, 11–16, 18–20)
- blocked on an external dependency (HA-02, HA-10)
- intentionally deferred (HA-17)
- a cross-Field contract the autonomous authority excludes (HA-19)

### 6.1 Derivation after WU-PFC-F09-3

| Candidate | Verdict |
|---|---|
| F09 INDETERMINATE → RecoveryRecord + dependent blocking + LPVS (12 §19.2) | Blocked: dependency scope undefined in 06 §24; PKG-24 human-confirmed recovery design (HA-15) |
| F09 reconciliation / recovery Commands / backup restore | Blocked: HA-15, GAP-09-015, GAP-10-004/005/008/009, HA-10 |
| F09 direct-write prevention at runtime (principals, RLS) | Blocked: HA-09 (Architecture 24 WU-AUTH-17), HA-10 |
| F09 TH-04 SecurityEvent on cross-Workspace reference | Blocked: HA-20 (runtime environment identity) |
| F09 privacy / retention / deletion | Blocked: GAP-11-007, 19 §29 STOP |
| F09 decide-route outcome parity | Cross-Field contract (HA-19) |
| F08 frontend freshness / history, CYAN frame, CYAN analysis | Blocked: HA-03 (SF ↔ PFC backend integration order, H-8) |
| Session history API (09 §81) | Beyond projection state, a history entry is audit data (actor, authority): HA-11 |
| Main product chain (F05 → F06 → F07 → graph, export) | Blocked: HA-01 (REFLECTION gate), HA-04, HA-05, HA-08, HA-14 |
| AI expansion, cost model, coach modes | Blocked: HA-02, HA-07 |

### 6.2 Work Units completed in the run

A1, I1, F08-1, F08-2, F08-3, F09-1, F09-2 and F09-3: eight technically closed and checkpointed Work Units, plus WU-PFC-00 before the run.

### 6.3 First Broken Relations: closed in the run

| FBR | Closed by |
|---|---|
| FBR-PFC-01 F04 had no recoverable predecessor | WU-PFC-00 |
| FBR-PFC-06 Challenge frame dropped on the wire | WU-PFC-A1 |
| FBR-PFC-08 outbox never delivered (backend) | WU-PFC-F08-1/2/3 |
| (new) Technical failures escaped as a bare 500; the worker died on DB errors | WU-PFC-F09-1 |
| (new) Session version/state disclosed to non-members on 9 routes | WU-PFC-F09-2 |
| (new) A telemetry failure could stop delivery or liveness; Commands untraced | WU-PFC-F09-3 |

### 6.4 Observations (recorded, not changed)
- **Legacy master web** (`apps/web` on master / `pfc-integration`): it creates a new intent key after `indeterminate` (challenge page, workspace page, BurstCapturePanel), so a blind retry bypasses the idempotency block. **CYAN** (`frontend-symbiotic`) already retains the key per relation (`field.retained[relation]`) and blocks consequences while re-reading. The live frontend is therefore correct; the legacy web is superseded by CYAN.
- **Existence signals on unguessable identifiers.** "Unknown id" and "not yours" answers differ, but no protected data is disclosed (WU-PFC-F09-2 §4).
- **Stale docstrings in accepted PKG-era code:**
  - `session_creation_handler` says WorkspaceRole has no Observer/Viewer, but it has since PKG-02.
  - `domain/decision.py` says `evidence/provenance.py` is "not yet built", but it now exists.
  - `membership_operations_handler` raises `OwnerRoleNotAssignable` also for Observer/Viewer; changing that would be a wire reason change.
- **Pre-existing `ruff format` finding** on the hash-bound F04 review bundle; not touched.

### 6.5 Resulting Field status

**NQUIRY_PRODUCT_FUNCTION_COMPLETION: IN_PROGRESS, autonomous run STOPPED at global condition B.**
- The derivable surface is closed and checkpointed on `pfc-integration`.
- The F08 backend is READY_FOR_HUMAN_REVIEW (14 Phase 8 gate).
- F09 is technically closed for its derivable part; the rest is blocked as listed.
- No Work Unit is REVIEWED_FIELD. Nothing is PUBLISHED_FIELD. master (BLUE) and `frontend-symbiotic` (CYAN) are unchanged.

**Test totals on the final predecessor line** (`checkpoint-PFC-F09-3`): live **1856 passed / 2 skipped**; no-DB **908 passed**. Mutation proofs across the run: A1 18/18, F08-1 15/15, F08-2 10/10, F08-3 5/5, F09-1 9/9, F09-2 6/6, F09-3 5/5, plus the inherited F04 PASS.

---

## 7. Field reconstruction after HD-24 (2026-09-27)

**Human Authority:** HD-24 / NQ-DEC-052 (REC-028) resolved HA-01 for Fixture Sessions: Option 03 is the working path for Fixture Sessions, Option 01 is the target for real Sessions, and Option 02 is not selected.

**Work Units derived and closed:**
- **WU-PFC-B0**, Fixture Session identity (rules 1–5): `checkpoint-PFC-B0` → `ea3af40`.
- **WU-PFC-B1**, TRN-SESS-007 BEGIN_REFLECTION (rules 6–12): `checkpoint-PFC-B1` → `ea4755d`.

**What changed in the product:**
- A Fixture Session goes F02 → F03 → F04 (mock analysis, NON_PROOF) → **REFLECTION**. Every surface marks it FIXTURE_NON_PROOF / MOCK_NON_PROOF, and it is never real provider proof. This is proven on the real stack.
- A real Session with a mock proof stays in ANALYSIS (`MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION`, HD-20) until HARD-DEP-002 supplies an eligible real provider (HA-02).
- Supplying that provider changes only the eligible proof source (rule 12).

**Derivation after B1: global stop condition B again.** TRN-SESS-008 requires the Reflection completion contract (03 §52 GAP-03-007 `[UNDERDEFINED]`) and answer persistence (NQ-GAP-016). Both are now queued as **HA-21** (with HA-05). Every relation after REFLECTION (QuestionSelection, ImpactChain, INVESTIGATION, F06, F07, graph, export) depends on it. CYAN remains out of scope.

**FBR status change:** FBR-PFC-02 (REFLECTION gate) is **CLOSED for Fixture Sessions**, and blocked for real Sessions (HA-02). The next first broken relation is REFLECTION → QUESTION_SELECTION (HA-21, HA-05).

**Test totals:** live **1890 passed / 2 skipped**; no-DB **912 passed**. Mutation: B0 9/9, B1 11/11.

**Resulting Field status:** IN_PROGRESS; the autonomous run is STOPPED at global condition B. Nothing is REVIEWED_FIELD or PUBLISHED_FIELD. BLUE is unchanged and CYAN is untouched.

## 8. Field reconstruction after HD-25 (2026-09-27)

**Human Authority:** HD-25 / NQ-DEC-053 (REC-029) resolved HA-21 with C-a + C-c. Reflection completion is the explicit human procedural confirmation by the SESSION_CONTROL_RIGHT holder. Zero responses are allowed, the confirmation is carried by CMD_BEGIN_QUESTION_SELECTION, and it is audited as HUMAN_PROCEDURAL_CONFIRMATION. HA-05 stays OPEN and decoupled.

**Work Unit derived and closed:**
- **WU-PFC-B2**, TRN-SESS-008 BEGIN_QUESTION_SELECTION: `checkpoint-PFC-B2` → `10d4517`.

**What changed in the product:** a Fixture Session goes F02 → F03 → F04 → REFLECTION → **QUESTION_SELECTION**. It gets there only through the controller's explicit confirmation, and a request without it is refused while the Session stays in REFLECTION. The Session stays FIXTURE_NON_PROOF throughout. This is proven on the real stack with the real worker.

**Derivation after B2** (sources re-read: 02 §18/§28, 03 §39/§40/TRN-SESS-009, 04 AUTH-DEP-SEL-001/002 and SESS-009, 05 GOV-010/§40, 09 §33/§48/§63/§85/§86, 12 §5/§6/§10/AC-12-004):
- **QuestionSelection (TRN-SEL-001/002): DERIVABLE for one selector.**
  - The governed handler exists (`question_selection_handler`), but no product path reaches it: no route, no read model, no capability.
  - 12 fixes one active QUESTION_SELECTION_RIGHT holder (§6, AC-12-004). Collaborative selection (NQ-GAP-026 / GAP-04-001) is NOT EXERCISED.
  - Next Work Unit: **WU-PFC-B3**.
- **Replacing or withdrawing a selection:** BLOCKED (GAP-03-018, `[UNDERDEFINED]`). Selections stay append-only.
- **Five-Why ImpactChain:** BLOCKED. There is no authoring or creation authority: 04 has none, 09 §63 blocks, and 09 §86.1 forbids inferring a Decision Right. This is a new Case 3: **HA-22**.
- **TRN-SESS-009 BEGIN_INVESTIGATION:** BLOCKED transitively through HA-22. 03 requires a complete ImpactChain for the Question Burst method.
- **AI in selection:** EXCLUDED. The AI recommends only, and no recommendation operation is in HD-21 scope.
