# F08 Consequence Integrity: Field Review Bundle (READY_FOR_HUMAN_REVIEW)

**Field:** F08 CONSEQUENCE INTEGRITY · EVENTS · WORKERS · PROJECTIONS (Architecture 19 §28), as child Field PFC-F of NQUIRY_PRODUCT_FUNCTION_COMPLETION.

**Human gate:** 14 Phase 8 ("Implement outbox worker, EventEnvelope, projection, rebuild … Human gate: required"). This bundle is the input for that gate.

**Branch:** `pfc-integration`. **Checkpoints:** `checkpoint-PFC-F08-1`, `checkpoint-PFC-F08-2`, `checkpoint-PFC-F08-3`.

## 1. What the Field now does

```text
legitimate Command -> final boundary -> CommitUnit
  -> canonical mutation + Audit + durable immutable Event basis (committed_events) + Outbox   [F08-1]
  -> exact EventEnvelope (from committed_events alone)                                         [F08-1]
  -> Worker (python -m nquiry_worker: loop / --once / --diagnose)                             [F08-2, F08-3]
  -> Projection (session_read_model, inquiry_read_model; version-guarded, idempotent)          [F08-2]
  -> Replay / Rebuild (from committed history only; no Command, no canonical write)           [F08-2]
  -> Diagnostics / freshness (read-only)                                                       [F08-3]
```

## 2. 19 §28 coverage

| 19 §28 item | Where | Proof |
|---|---|---|
| durable Event semantic contract | `events/contracts.py` (22 event types) | F08-1 contract falsifiers; mutations M02–M06 |
| storage representation, migration | `committed_events`, `a9f3c2e81d57` | immutability, binding and FK falsifiers; round-trip |
| CommitUnit integration | `CommitCoordinator._append_committed_event` | full regression (every production commit path) |
| EventEnvelope reconstruction | `CommittedEventEnvelopeSource` | exact-equality, authority-revoked-later and aggregate-changed-later falsifiers |
| outbox delivery, worker loop, startup/shutdown | `nquiry_worker.delivery`, `__main__` | F08-2 falsifiers; real-process runtime proof (SIGTERM, --once, no-DB exit 2) |
| duplicate handling | consumer event-id and version guard | redelivery and restart falsifiers |
| poison handling | `BasisRequiredEnvelopeSource` | poison falsifier (within 09 §15.1; see HA-18) |
| Projection worker | `ProjectionEventPublisher` + `ProjectionWorker` | projection-failure falsifier (SAVEPOINT) |
| projection freshness, diagnostics | `persistence/delivery_diagnostics.py`, `--diagnose` | F08-3 falsifiers; runtime `--diagnose` |
| replay, rebuild | `rebuild_projections` | deletion-rebuild, corrupted-rebuild and no-Command falsifiers |
| tests | 44 falsifiers (24 + 14 + 6) | mutation proofs 15/15, 10/10 and 5/5 |

**TESTS FIRST list of 19 §28:** commit + crash, restart, exact Event equality, authority revoked later, aggregate changes later, historical Event unchanged, duplicate delivery, worker restart, poison event, projection failure, projection deletion, projection rebuild and "replay does not execute Command" are each covered by a named falsifier (see the three Work Unit records).

**PASS "No worker needs to invent missing Event semantics":** satisfied. Every event type has a contract. The worker reads only `committed_events`. A missing basis fails closed.

## 3. Decisions taken inside the Field (Case 2, for review)

1. **Separate committed Event table** (19 §28 storage option 2). The outbox stays bookkeeping.
2. **The version is read back** from the canonical row in the committing transaction, never asserted by a handler.
3. **Payload holds structural facts only.** No user-authored free text is copied into immutable Events, because retention and deletion are open (GAP-11-007, NQ-GAP-057).
4. **Existing event names kept,** including PKG-era `<CMD>_COMMITTED`.
5. **No backfill** of pre-F08 outbox rows. They stay unresolvable and fail closed.
6. **In-process delivery** to the projection (12 §17). One transaction per pass, one SAVEPOINT per event.
7. **Version-guarded consumer.** An older event never regresses a newer projection. Equal versions still apply, preserving PKG-21 semantics.
8. **Poison records** are FAILED_DELIVERY with backoff retry. No terminal status is invented (HA-18).
9. **Worker cadence** 5 s; retry backoff 300 s. Diagnostics are an operator CLI, not an HTTP surface.

## 4. What the reviewer should look at
- The **payload contracts** in `events/contracts.py`: is each event's structural payload the right set of committed facts?
- The **worker's changed runtime behaviour.** The local `worker` container now runs continuously; master still has the no-op.
- **HA-18:** whether a terminal dead-letter status is wanted.

## 5. Not in F08 (boundaries)
- **Frontend freshness and history** (19 §28 upward test): needs an API read of projections (09 §81 history, not in the 12 §23 proof set) and a CYAN Work Unit.
- **Runtime DB principals** for the worker (HA-09).
- **Deployment** (HA-10).

## 6. Status
**F08 (backend): TECHNICALLY_CLOSED, CHECKPOINTED, READY_FOR_HUMAN_REVIEW (14 Phase 8 gate).** Not REVIEWED_FIELD, not PUBLISHED_FIELD.
