# WU-PFC-F08-2 — Delivery → Projection → Replay/Rebuild (the running worker)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header (bound before the Delta)

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F08-2 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-F = F08 Consequence Integrity |
| Colour / role / model | RED · worker / projection / persistence · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26). |
| Derivation | After F08-1 the exact envelope exists, but nothing delivers it. The next links of 19 §28's TARGET are "→ Worker → Projection → Replay/Rebuild", plus the internal Work Units "outbox delivery, worker loop, startup/shutdown, duplicate handling, poison handling, Projection worker, replay, rebuild". 12 §17 puts the delivery path and a replay test in prototype scope. |
| Current state | `pfc-integration` `4ed761a` (checkpoint-PFC-F08-1). Migration head `a9f3c2e81d57`. `nquiry_worker.__main__` is the Phase-0 no-op. `OutboxWorker` and `ProjectionWorker` are proven but unwired. |
| Baseline evidence | Live 1759 passed / 2 skipped; no-DB 892 passed. F08-1 mutation 15/15. |
| Recoverable predecessor | `checkpoint-PFC-F08-1` → `298a5d8` (signed, remote-verified). |
| State isolation | Worktree `pfc-integration`. Test DB `nquiry_pfc_int_test`. Runtime DB `nquiry_pfc_int_runtime` (new; roles; head). API on port 18431. The shared `nquiry` DB and the running containers were not touched. |
| Authoritative home | 19 §28; 09 §15 (at-least-once; PENDING / DELIVERED / FAILED_DELIVERY), §18 (replay), §73.1, §74 (dedupe, no duplicated projection rows); 10 §17 (F-OUT), §31 (RC-01), §56 (SYSTEM_SERVICE delivery retry); 12 §17 (in-process delivery to projection); 14 §41 (no consequential import in a consumer). |
| Producers | `committed_events` (F08-1) and `outbox_events`. |
| Consumers | `session_read_model`, `inquiry_read_model`, `projection_checkpoints`. No API or UI reads them yet (17 L273–280). |
| Boundary / authority | Delivery is SYSTEM_SERVICE deterministic recovery (10 §31/§56). It creates no domain choice, issues no Command and grants nothing. |
| Authorized delta | Wire delivery end to end, fix the consumer's dedupe and ordering defect exposed by delivery, add replay/rebuild, and turn the worker entrypoint into the loop. **Not in scope:** a terminal dead-letter status (09 vocabulary, see §4); an API or CYAN projection read; runtime DB principals (HA-09); deployment. |
| Must become true | A committed consequence reaches the projection exactly, at least once and idempotently. It survives worker restart. A poison record fails closed. A failed projection write leaves nothing partial and is retried. A deleted or corrupted projection is rebuilt identically from committed history. |
| Must remain true | The F08-1 basis and every predecessor suite; the PKG-20/21 worker and projection proofs, including file-level import exclusivity; 09 §15.1 status vocabulary; `OutboxWorker` mechanics. |
| Must remain impossible | Delivery or replay executing a Command or changing canonical state; an older event regressing a newer projection; a poison record crashing the pass or being reconstructed from guesswork; a projection failure marked DELIVERED; the worker starting without a database. |
| Falsifiers | `tests/e2e/test_pfc_f08_2_delivery.py` (14 cases). |
| Stop conditions | A needed new delivery status (Case 3); any canonical write from the pipeline. |

## 2. Execution record

**1 FALSIFIER RED.** 12 cases written first; 12 failed for the right reasons:
- `No module named 'nquiry_worker.delivery'` (×6)
- `No module named 'projection.delivery'` (×3)
- `delivery.py` missing
- the worker printed "Phase 0 skeleton — no workers implemented yet."
- the worker exited 0 without a DATABASE_URL

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   committed consequences never reach any read model; outbox rows stay PENDING
CONSUMER         ProjectionConsumer / ProjectionWorker (proven, unwired)
RELATION         outbox record -> exact EventEnvelope -> projection
PRODUCER         nquiry_worker.__main__: Phase-0 no-op
FBR              the delivery pipeline is not composed. The consumer's dedupe
                 (last_event_id equality) is also too weak for at-least-once delivery
                 with retries: a late older event overwrites a newer state (09 §74).
```

**3 AUTHORITATIVE HOME.** 19 §28 worker and projection Work Units; 09 §74 for the consumer.

**4 MINIMUM LEGITIMATE ROOT REPAIR.**

| Piece | Change |
|---|---|
| `packages/projection/delivery.py` (new) | `DeliveryPorts`: outbox, envelope source, history, projection store and consumer, all on one connection. `isolated()` wraps each event in a SAVEPOINT and reports `SQLAlchemyError` as `ProjectionStoreFailure`. `open_delivery()`: one real transaction per pass. |
| `apps/worker/src/nquiry_worker/delivery.py` (new) | `BasisRequiredEnvelopeSource` (a poison record raises `EventDeliveryFailure`); `ProjectionEventPublisher` (in-process, isolated per event); `run_delivery_pass`; `rebuild_projections` (replay from `committed_events` only). |
| `apps/worker/src/nquiry_worker/__main__.py` | The loop: `--once`, `--interval`, `--retry-backoff`; graceful SIGTERM/SIGINT; exit 2 without DATABASE_URL; observation per startup and per pass. |
| `packages/persistence/committed_event_repository.py` | `list_for_workspace` (history in per-aggregate order). `SqlAlchemyAggregateOrderedOutbox`: due selection by (created_at, aggregate, version), otherwise delegating to the real outbox repository. |
| `packages/projection/consumer.py`, `models.py`, `persistence/projection_repository.py`, `tables.py` | Read models record `last_aggregate_version`. The consumer skips an event whose aggregate version is lower than the projected one. Equal versions are applied, so the PKG-21 semantics are unchanged. |
| migration `c3b8e5a1f7d2` | Nullable `last_aggregate_version` on both read models (derived, rebuildable tables). |
| Documentation drift (successor truth, not rewrites) | `outbox_worker.py` now cites the real test file `test_outbox_worker_exclusivity.py` (it previously cited `test_outbox_worker.py`, which does not exist) and has a successor note. Successor notes added to `projection_worker.py` and `events/envelope.py`. `docs/RUNTIME_OPERATION.md` §7 updated for the delivery loop, stating that master still carries the no-op. |

**Case 2 choices (recorded):**
- **In-process delivery** to the projection consumer (12 §17, one committed event path); no broker.
- **One transaction per pass, one SAVEPOINT per event.** A crash rolls the pass back, and the records are redelivered (at-least-once).
- **Poison within the existing vocabulary:** FAILED_DELIVERY plus a backoff retry. A terminal dead-letter status is **not** invented and is queued as **HA-18**.
- **Ordering:** by committed aggregate version in due selection, and a version guard in the consumer (both, defence in depth).
- **Worker cadence:** 5 s default interval, 300 s retry backoff.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| Worker process | AFFECTED | No-op → delivery loop. Local compose runs it; master is unchanged. |
| Projection read models (derived) | AFFECTED | Now populated; new nullable column. |
| Projection consumer | AFFECTED | Version guard; PKG-21 suites green. |
| Outbox rows | AFFECTED (delivery fields only) | Status and attempts per 09 §15.1 triggers. |
| committed_events, canonical tables, audit, commands | NOT AFFECTED | Runtime proof: counts unchanged. Falsifier: no Command, no canonical change. |
| API / HTTP / CYAN | NOT AFFECTED | No route reads projections (17). A freshness or history API would be a separate relation. |
| `OutboxWorker` / `ProjectionWorker` | NOT AFFECTED (code) | Composed, not changed. Import exclusivity tests still pass. |
| Domain / authority / boundaries | NOT AFFECTED | — |
| F02/F03/F04/F08-1 | NOT AFFECTED | Full regression green. |
| Runtime compose (`docker-compose.yml`) | NOT AFFECTED (file) | `python -m nquiry_worker` now loops; no restart policy change needed. |
| Deployment (f5) | NOT AFFECTED | Not deployed (HA-10). |
| Downstream: F09 recovery wiring, frontend freshness/history | ENABLED / not started | F09 by ordering and HA-15. The frontend is a CYAN relation needing an API read (see Field report). |

**6 LOCAL PROOF.** ruff, ruff format, mypy (CI scope) and the architecture, SDK and test-only import checks pass. `verify_migrations`: 30 revisions, single head `c3b8e5a1f7d2` (`evidence/f08_2_regression.txt`).

**7 INTEGRATION PROOF.**
- The falsifiers drive the full accepted chain on real PostgreSQL and deliver through the real composition: every outbox row DELIVERED; Session projection ANALYSIS; `projection_version` = `last_aggregate_version` = canonical `record_version`; checkpoints for both projections.
- **Real-stack runtime proof** (`evidence/f08_2_runtime_proof.txt`):
  - The real API process committed a Session through HTTP: login, Idempotency-Key, `transitions/begin-analysis` → 200 committed, ANALYSIS, clustering ACCEPTED.
  - 24 outbox rows = 24 committed Events.
  - The real worker process `python -m nquiry_worker --once` delivered 24/24 with 1 attempt each. `session_read_model` ANALYSIS, versions 6/6/6.
  - The restart pass delivered 0. Continuous mode stops on SIGTERM (exit 0). No DATABASE_URL gives exit 2.
  - commands/commit_units/audit/committed_events counts are unchanged by delivery.

**8 PRESERVATION PROOF.**
- MUST REMAIN TRUE: the full regression is green, including the PKG-20/21 outbox, projection and worker suites and both exclusivity scans.
- MUST REMAIN IMPOSSIBLE:
  - No Command and no canonical change: `test_delivery_and_replay_execute_no_command_and_change_no_canonical_state` and the runtime counts.
  - No regression by stale events: `test_stale_retry_never_regresses_a_newer_projected_state` and `..._non_session_snapshot`.
  - A poison record neither crashes the pass nor is invented: `test_poison_event_fails_closed_and_blocks_nothing_else`.
  - A projection failure is never marked delivered: `test_projection_failure_rolls_back_the_projection_and_is_retried`.
  - The worker never starts without a DB: exit code 2 test.
  - No consequential import: AST scan of the two new delivery files.

**9 REGRESSION PROOF.** `evidence/f08_2_regression.txt`.

**10 MUTATION PROOF.** `scripts/pfc_f08_2_mutation_proof.py`: **10/10 KILLED**, sources restored. The mutants are:
- stale guard removed ×2
- equal-version wrongly treated as stale (killed by PKG-21)
- poison crash
- no isolation
- swallowed failure
- order removed
- rebuild without reset
- start without a DB
- version not recorded

M07 (order removed) is killed with probability 719/720 per run: without ordering, six same-timestamp Session events are delivered in random UUID order. The explicit `projection_version == record_version` falsifier catches every non-identity permutation.

**11 INVERSE PROOF.**
```text
session_read_model.current_state = ANALYSIS (visible projection)
  <- ProjectionConsumer (version-guarded)  <- ProjectionEventPublisher (SAVEPOINT)
  <- EventEnvelope resolved from committed_events only (no current lookup)
  <- outbox record DELIVERED by OutboxWorker (SYSTEM_SERVICE, 10 §56)
  <- CommitUnit of CMD_BEGIN_ANALYSIS (commit, audit, outbox, Event in one transaction)
  <- BND-014 / SESSION_CONTROL_RIGHT binding  <- governed Command  <- audit
```

**12 RECURSIVE DEEP SWEEP.**

| Risk | Finding |
|---|---|
| Semantic drift | None. The projection mirrors payload `state` only. |
| Authority leakage | None. The projection is never an authority source (14 PKG-21). |
| Hidden cross-field mutation | The only writes are delivery fields and the projection tables. |
| State / projection inconsistency | Closed. Version guard, ordered delivery, and rebuild equality are proven. |
| Persistence inconsistency | One transaction per pass. A crash leaves the records PENDING. |
| Runtime drift | The worker now loops. Documented in `RUNTIME_OPERATION.md` §7. |
| Documentation drift | Fixed (the wrong test-file citation; successor notes). |
| Test drift | None; the PKG-20/21 suites are unchanged. |
| Boundary expansion / authority transfer | None. |

**13 INVERSE DEEP SWEEP.**
- Every read-model row traces to one committed Event: `last_event_id` and `last_aggregate_version`.
- Every DELIVERED outbox row traces to one publish in a pass whose transaction committed.
- A FAILED_DELIVERY row carries its attempt count and retry time.

## 3. Falsifier map

| Falsifier | Proves |
|---|---|
| `test_delivery_projects_the_committed_session_state` | end-to-end delivery; versions; ordered; checkpoints |
| `test_every_non_session_aggregate_gets_its_committed_snapshot` | inquiry snapshots |
| `test_redelivery_of_the_same_events_changes_nothing` | duplicate delivery (09 §74) |
| `test_worker_restart_delivers_nothing_twice` | worker restart |
| `test_stale_retry_never_regresses_a_newer_projected_state` | ordering, Session |
| `test_stale_retry_never_regresses_a_non_session_snapshot` | ordering, generic |
| `test_poison_event_fails_closed_and_blocks_nothing_else` | poison event |
| `test_projection_failure_rolls_back_the_projection_and_is_retried` | projection failure |
| `test_projection_deletion_and_rebuild_reproduce_the_identical_read_model` | projection deletion and rebuild |
| `test_rebuild_repairs_a_corrupted_projection_from_committed_history` | rebuild from history, not from the projection |
| `test_delivery_and_replay_execute_no_command_and_change_no_canonical_state` | replay does not execute Commands |
| `test_delivery_files_import_no_command_path` | 14 §41 |
| `test_worker_entrypoint_runs_one_real_pass_and_exits_cleanly` | real process |
| `test_worker_entrypoint_refuses_to_run_without_a_database` | fail-closed start |

## 4. Open / remaining
- **HA-18:** poison and dead-letter terminal status (09 §15.1 defines none). Poison records are retried with backoff indefinitely and are visible as FAILED_DELIVERY with an attempt count.
- **F08 diagnostics and projection freshness:** next Work Unit, WU-PFC-F08-3.
- **Frontend freshness and history** (19 §28 upward test): needs an API read of the projection (09 §81 `GET /sessions/{s}/history`, not in the 12 §23 proof set) and a CYAN projection. Not started.
- The 14 Phase 8 human gate: a review of the F08 Field.

## 5. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F08-2`; identity in `CHECKPOINT_WU-PFC-F08-2.md`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F08: IN_PROGRESS.
