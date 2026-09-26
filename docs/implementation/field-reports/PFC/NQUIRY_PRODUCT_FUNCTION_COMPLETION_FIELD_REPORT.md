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
| 4 | WU-PFC-F08-2 delivery → projection → replay/rebuild; the running worker | `pfc-integration` | see `CHECKPOINT_WU-PFC-F08-2.md` | `checkpoint-PFC-F08-2` | TECHNICALLY_CLOSED, CHECKPOINTED |

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
| FBR-PFC-08 outbox written, never delivered | **CLOSED** for the backend: the durable basis (F08-1), plus delivery, projection, replay and rebuild with the running worker (F08-2), proven on the real stack. Remaining F08 items: diagnostics and freshness (F08-3); frontend freshness and history (needs an API read and CYAN); HA-18 dead-letter status. |
| FBR-PFC-02 REFLECTION gate | BLOCKED (HA-01) |
| FBR-PFC-03/04 Selection, ImpactChain | BLOCKED behind FBR-PFC-02 |
| FBR-PFC-05 Decision only by seed | BLOCKED (HA-14) |
| FBR-PFC-07 no Evidence producer | BLOCKED (HA-08) |
| FBR-PFC-09 runtime superuser | BLOCKED (HA-09/HA-10) |
| FBR-PFC-10 Export | BLOCKED (HA-04) |
| FBR-PFC-11 F04 projection invisible | BLOCKED (HA-03) |

## 5. Resulting Field status

**IN_PROGRESS (autonomous).** Four Work Units are technically closed and checkpointed (A1, I1, F08-1, F08-2). Test totals on `pfc-integration`: live 1773 passed / 2 skipped; no-DB 894 passed. None is REVIEWED_FIELD. Nothing is PUBLISHED_FIELD. BLUE/master is unchanged.
