# WU-PFC-F08-1 — Durable, immutable committed Event basis

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header (bound before the Delta)

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F08-1 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-F = F08 Consequence Integrity (19 §28) |
| Colour / role / model | RED · events / commit / persistence · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26): derive and execute every derivable Work Unit of the Field. |
| Derivation | After WU-PFC-I1 the main product chain is blocked at HA-01. F08 is derivable: 19 L1058 and L3026–3030 ("After F03: F04 ‖ F08 Event implementation"); 19 §28 STORAGE FREEDOM ("Claude Code may choose … only if semantic reconstruction is exact"); 12 §17 puts event delivery in prototype scope. F08 is split into Work Units; this is the first link of 19 §28's TARGET chain. |
| Current state | `pfc-integration` `5e5e694` (checkpoint-PFC-I1). Migration head `e7c1d4a9b206`. |
| Baseline evidence | Live 1735 passed / 2 skipped; no-DB 888 passed. F04 and A1 mutation proofs PASS (WU-PFC-I1). |
| Recoverable predecessor | `checkpoint-PFC-I1` → `a2cd36d` (signed, remote-verified). |
| State isolation | Worktree `worktrees/pfc-integration`; DB `nquiry_pfc_int_test`. |
| Authoritative home | 19 §28 (HISTORICAL EVENT BASIS, TESTS FIRST, PASS); 09 §15, §16, §17 (AC-09-003), §18, §70–§72, §174; 10 §17 (F-OUT: "No authoritative Event may be regenerated from guesswork"); 14 §8 (principals). |
| Producers | CommitCoordinator (the only writer), fed by the 19 production `MutationOutcome` sites in 13 handlers. |
| Consumers | `CommittedEventEnvelopeSource`, the `EventEnvelopeSource` that `nquiry_worker.outbox_worker` left SUCCESSOR_NOT_BUILT. Future consumers are the outbox and projection workers (next F08 Work Units). |
| Boundary / authority | Unchanged. The Event records the commit-time authority source (`proof.authority_source.source_ref`); it grants nothing (09 §16.2). |
| Authorized delta | Durable Event semantic contract, storage representation, migration, CommitUnit integration, EventEnvelope reconstruction (19 §28 internal Work Units 1–5). **Not in scope:** delivery loop, worker wiring, projection worker, replay and rebuild, poison handling (next F08 Work Units); any change to command semantics, event names, audit or outbox. |
| Must become true | Every governed commit durably records, in the same transaction, one immutable Event whose 14 envelope fields are exact committed facts. Any outbox row's envelope is reconstructable from it alone. |
| Must remain true | Every F02/F03/F04 outcome; audit and outbox writes unchanged; idempotency; the 11 named failure-injection points; atomicity; event names unchanged. |
| Must remain impossible | A commit without its Event basis; an Event without its commit or outbox record; editing or deleting a historical Event; a payload outside its contract; reconstruction from guesswork; user-authored free text inside an immutable Event. |
| Falsifiers | `tests/e2e/test_pfc_f08_1_event_basis.py` (24 cases; see §3). |
| Stop conditions | A needed change to an event name or command semantics; a Case 3 on payload meaning; a regression in any predecessor Field. |

## 2. Execution record

**1 FALSIFIER RED.** 22 cases written before the repair; 22 failed. Every failure was for the right reason: the Event basis does not exist.
- `relation "committed_events" does not exist` (×14)
- `No module named 'events.contracts'` (×6)
- `No module named 'persistence.committed_event_repository'` (×2)

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   a committed consequence cannot be delivered or replayed exactly
                 (19 §28 HUMAN PRODUCT EFFECT; FBR-PFC-08 "outbox written, never delivered")
CONSUMER         OutboxWorker.deliver_due -> EventEnvelopeSource.resolve (no implementation)
RELATION         OutboxRecord -> EventEnvelope
PRODUCER         CommitCoordinator._commit_inner writes audit + outbox only
AUTHORITY / STATE  intact: every commit is governed and audited
FBR              CommitUnit -> durable immutable Event basis: aggregate_ref,
                 aggregate_version_after_commit and payload have no durable source
                 (events.envelope docstring: "have no durable source at all yet")
```

**3 AUTHORITATIVE HOME.** 19 §28. Repair at the CommitUnit (the only producer of committed facts), not at the worker, where the gap is visible.

**4 MINIMUM LEGITIMATE ROOT REPAIR.** +326 / −1 in 16 existing files; 5 new files.

| Piece | Change |
|---|---|
| `packages/events/contracts.py` (new) | The durable Event semantic contract: one `EventContract` per event type the handlers commit today (22 types), each fixing the aggregate kind, whether it is versioned, and the exact payload keys. Also `EventFacts`, `validate_event_facts`, `EventContractViolation`, `EventBasisMissing`, and the replay and consumer policies (09 §18, §73.1, §74). |
| `migrations/versions/a9f3c2e81d57_pfc_f08_committed_events.py` (new) | `committed_events`: the 14 envelope fields. FK `event_id` → `outbox_events(event_id)`; FK `(commit_id, workspace_id)` → `commit_units`. BEFORE INSERT trigger binds workspace, commit, type and time to the outbox row. BEFORE UPDATE/DELETE reject. CHECKs on version ≥ 1, object payload and ref shape. Grants: commit writer INSERT and SELECT only; readers SELECT. |
| `packages/persistence/committed_event_repository.py` (new) | Repository (`append`, `get`). `CommittedEventEnvelopeSource.resolve`, which refuses a missing or disagreeing basis with `EventBasisMissing`. `committed_aggregate_version`, which reads the aggregate's `record_version` inside the committing transaction and refuses a foreign Workspace. |
| `packages/persistence/tables.py` | `committed_events_table`. |
| `packages/commit/coordinator.py` | `MutationOutcome.event`. `_append_committed_event`, run after the outbox append and inside the SAVEPOINT (between the existing BEFORE_OUTBOX and AFTER_OUTBOX points; no new injection name). Envelope fields come from the committed facts: outbox event id, type and time; command envelope identities; `actor_type:actor_id`; commit-time authority source; version read back. An injectable `event_contracts` registry defaults to production. |
| 13 handlers, 19 sites | Each states `EventFacts(aggregate_ref, payload)`. |
| `tests/command_commit_event/test_commit.py` | Adapted to the mandatory basis: its bare Burst-start mutation states its facts and declares its test-only contract. No assertion changed. |

**Case 2 choices (recorded):**
- **Storage:** a separate committed Event table (19 §28 option 2). The outbox stays delivery bookkeeping (09 §15).
- **The version is read, not asserted:** the coordinator reads the aggregate's `record_version` in the committing transaction.
- **Payload holds structural facts only:** no user-authored free text (Question text, Challenge title or frame, Decision option or rationale). Copying text into immutable, never-deleted Events would decide retention and deletion (GAP-11-007, NQ-GAP-057 OPEN) by construction. Consumers that need text read the canonical row.
- **Existing names kept,** including the PKG-era `<COMMAND>_COMMITTED` names. They are historical facts in outbox rows.
- **No backfill.** Pre-F08 outbox rows have no basis and remain unresolvable (10 §17).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| CommitCoordinator | AFFECTED | Producer of the basis. |
| 13 application handlers (F01, F02, F03, F04, PKG) | AFFECTED (additive) | They state Event facts. Commands, targets, audit and outbox are unchanged. |
| Persistence schema | AFFECTED | New table, migration `a9f3c2e81d57`, single head. |
| Domain | NOT AFFECTED | No domain type changed. |
| Authority / boundaries / effect gates | NOT AFFECTED | Unchanged. The Event records the source; it grants nothing. |
| Audit, outbox, commit units, idempotency | NOT AFFECTED | Same rows. Proven by the full regression. |
| API / HTTP / projections served to clients | NOT AFFECTED | No route or response changed. |
| `nquiry_worker` (outbox and projection workers) | NOT AFFECTED yet | Now has a real `EventEnvelopeSource`. Wiring is WU-PFC-F08-2. |
| `projection.consumer` | NOT AFFECTED | It already reads `payload["state"]`; Session events now carry `state`. Not wired yet. |
| CYAN | NOT AFFECTED | No API change. |
| Runtime DB principals | AFFECTED (grants only) | The principals are still unused at runtime (HA-09). |
| F02/F03/F04 Fields | NOT AFFECTED (behaviour) | Full regression is green. |
| Downstream: F08-2 delivery, F09, F05+ | ENABLED | F05+ handlers must state Event facts. The coordinator refuses otherwise. |
| Tests / reports | AFFECTED | New falsifiers, one adapted PKG-13 test, this record. |

**6 LOCAL PROOF.**
- `ruff check .`: clean.
- mypy (CI scope): 0 issues in 192 files.
- Architecture, SDK and test-only import checks: PASS.
- `verify_migrations`: STATIC PASS (29 revisions, single head `a9f3c2e81d57`), LIVE PASS.
- Migration round-trip: downgrade to `e7c1d4a9b206` drops the table; upgrade restores it.
- Grants verified in `information_schema`.

**7 INTEGRATION PROOF.**
- Real PostgreSQL. The falsifiers drive the complete accepted chain through the real governed handlers: F02 founding → F03 capture and completion → F04 BEGIN_ANALYSIS → MockProvider analysis and clustering acceptance. They assert, for every outbox row, one committed Event with identical id, type, commit and time, and envelope fields equal to the audit facts.
- The Session versions are exactly 1..n, and the last equals the row version.
- The state sequence is DRAFT → … → ANALYSIS, and each previous_state equals the prior state.
- **The whole repository regression is itself an integration proof:** the coordinator refuses any commit without valid Event facts, so all 1735 predecessor tests passing means every production commit path in F01–F04 and PKG writes a contract-valid basis.

**8 PRESERVATION PROOF.**
- MUST REMAIN TRUE: the full regression is green (all F02/F03/F04 suites). The failure-injection falsifier covers 5 of the named points: an Event is rolled back with its commit. Event names are unchanged.
- MUST REMAIN IMPOSSIBLE: missing facts, an unregistered type, a wrong aggregate, extra or missing keys and non-scalar values are all refused with the exact reason. A forged Event row (unknown outbox or commit) is refused by the DB. UPDATE and DELETE are refused by the DB. A missing or disagreeing basis is refused by the source. No Question or Challenge text appears in any payload.

**9 REGRESSION PROOF.** See `evidence/f08_1_regression.txt`.

**10 MUTATION PROOF.** `scripts/pfc_f08_1_mutation_proof.py`: **15/15 KILLED**, sources restored (sha256). The first run found one survivor: M05, an unregistered type accepted. The unregistered-type falsifier had been refused by the aggregate-kind rule instead. The falsifiers now assert the exact refusal reason, and the re-run killed all 15 (`evidence/f08_1_mutation_proof.txt`).

**11 INVERSE PROOF.**
```text
EventEnvelope (resolved)   <- committed_events row (only source; no current lookup)
  <- CommitCoordinator._append_committed_event, same SAVEPOINT as the CommitUnit
  <- outbox_events row (FK + insert trigger: same workspace, commit, type, time)
  <- commit_units row (FK)            <- audit_events (same identities, actor, authority)
  <- canonical mutation (version read back from the row in that transaction)
  <- BND-014 / authority source (recorded, not re-evaluated)
  <- governed Command (command_id)    <- governance (audit append-only)
```

**12 RECURSIVE DEEP SWEEP.**

| Risk | Finding |
|---|---|
| Semantic drift | None. Payloads restate committed facts already in the canonical rows. No name changed. No new transition (09 §71). |
| Authority leakage | None. Events carry `authority_source_ref` as history only (09 §16.2). |
| Hidden cross-field mutation | None. The only new write is `committed_events`. |
| State / persistence inconsistency | Prevented structurally: FKs, the bind trigger and the same transaction. |
| Projection inconsistency | Session events carry `state` and `previous_state`, matching `projection.consumer`'s key. |
| Dependency drift | Architecture check PASS: `commit`→`events`/`persistence` and `persistence`→`events` are already allowed. |
| Test drift | One PKG-13 test adapted; assertions unchanged. |
| Boundary expansion | None. |
| Documentation drift | The docstrings of `events.envelope` and `outbox_worker` still say SUCCESSOR_NOT_BUILT. They are superseded by this record and will be updated in F08-2 when the worker is wired, because that file is touched there. |

**13 INVERSE DEEP SWEEP.** Every new effect traced back:
- A `committed_events` row can only be inserted by `governed_commit_writer` or `test_principal`, and only through the coordinator in code.
- It must match an outbox row, which the same coordinator writes in the same commit after BND-014 ALLOW. Nothing else writes the table.

## 3. Falsifier map

| Falsifier | Proves |
|---|---|
| `test_every_commit_has_exactly_one_matching_committed_event` | one Event per outbox row: same id, type, commit, time |
| `test_envelope_fields_equal_the_committed_audit_facts` | command, correlation, causation, actor, authority, schema |
| `test_aggregate_versions_are_the_committed_row_versions` | versions are the committed row versions |
| `test_resolved_envelope_is_exact_and_needs_no_current_lookup` | exact EventEnvelope from the basis alone |
| `test_session_events_carry_the_state_the_projection_consumes` | state sequence and previous_state chain |
| `test_later_session_change_leaves_earlier_events_unchanged` | aggregate changes later (19 §28) |
| `test_authority_revoked_later_leaves_the_event_unchanged` | authority revoked later (19 §28) |
| `test_historical_event_is_immutable` ×2 | UPDATE and DELETE refused |
| `test_rolled_back_commit_leaves_no_event` ×5 | commit plus crash |
| `test_event_row_cannot_exist_without_its_outbox_and_commit` | AC-09-003 |
| `test_outbox_row_without_basis_is_never_reconstructed` | no guesswork (10 §17) |
| `test_outbox_record_that_disagrees_with_its_event_is_not_resolved` | binding of record and Event |
| `test_aggregate_of_another_workspace_is_refused` | Workspace isolation of the aggregate |
| `test_no_user_authored_free_text_is_copied_into_events` | privacy choice |
| `test_commit_without_event_facts_is_refused` | EVENT_BASIS_MISSING |
| `test_payload_outside_its_contract_is_refused` ×3 | contract keys and values |
| `test_unregistered_event_type_or_wrong_aggregate_is_refused` | contract type and aggregate |

## 4. Open / remaining in F08
- **WU-PFC-F08-2:** worker composition (delivery loop wiring, startup and shutdown, duplicate handling), projection worker wiring, poison handling within 09 §15.1's existing statuses, replay and rebuild tests ("replay does not execute Command").
- Diagnostics and freshness.
- The 14 Phase 8 human gate is a review at F08 completion.

## 5. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F08-1`; identity in `CHECKPOINT_WU-PFC-F08-1.md`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F08 as a Field: IN_PROGRESS.
