# WU-PFC-F09-1 — The system says what it actually knows under technical failure

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F09-1 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-F = F09 FAILURE · RECOVERY · SECURITY · PRIVACY · ISOLATION (19 §29) |
| Colour / role / model | RED · persistence / application / API / worker · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26). |
| Derivation | F08 is technically closed. 19 L2998–3001: "Parallel infrastructure stream once stable semantics exist: F08 → F09". A read-only F09 derivability map (2026-09-26) ranked the API-edge technical failure envelope first. Its TESTS FIRST items "DB unavailable before operation" and "DB uncertainty around commit" were MISSING. |
| Current state / predecessor | `pfc-integration` `7d3bbf8`; `checkpoint-PFC-F08-3` → `aea783e`. Migration head `c3b8e5a1f7d2`. |
| Baseline | Live 1779 passed / 2 skipped; no-DB 895 passed. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. Unreachable-DB runs use `127.0.0.1:1`. Real API process on port 18432. The shared PostgreSQL was never stopped. |
| Authoritative home | 19 §29 ("The system says what it actually knows. It does not falsely claim success, failure, authority, recovery"; "HTTP failure mapping", "INDETERMINATE handling"); 10 §4 (four outcomes), §4.2, §4.4, §14 (F-PERS); 09 §77 (command identity in write outcomes), §78 (5xx: FAILED_PRECOMMIT or INDETERMINATE, never guessed from the status code). |
| Authorized delta | Typed technical failure facts at the transaction scope. One honest mapping installed at the API edge for every route. Worker survival across database outages. **Not in scope:** RecoveryRecord creation and BND-018 routing for INDETERMINATE (the reconciliation catalogue and discretionary recovery authority are HA-15; GAP-09-015, GAP-10-005, GAP-10-009); `commandId` / `correlationId` on *every* envelope (next Work Unit); CYAN no-blind-retry (a CYAN relation). |
| Must become true | A database failure before execution is FAILED_PRECOMMIT. A COMMIT the server rejected is FAILED_PRECOMMIT (proven abort). A COMMIT whose connection was lost is INDETERMINATE for a Command. An unknown failure never claims a proven outcome for a Command. Every Command failure envelope echoes its command identity. The worker keeps running across outages. |
| Must remain true | Every existing envelope kind and status for domain outcomes; success and caller-exception semantics of `connect()`; F02/F03/F04/F08 behaviour. |
| Must remain impossible | A bare non-envelope 500; claiming FAILED_PRECOMMIT when the commit is uncertain; claiming success; the worker loop dying on a database error; new wire vocabulary. |
| Falsifiers | `tests/e2e/test_pfc_f09_1_technical_failure.py` (13 cases). |

## 2. Execution record

**1 RED.** 12 failed and 1 passed. The passing case is the preservation case (success and caller-failure semantics).
- The engine raised a raw `OperationalError`.
- No envelope was produced: plain 500, or a TestClient exception.
- The worker died, or exited 0 on an unreachable database.
- The two route-family falsifiers first passed trivially: empty bodies were rejected by validation before any database access. They were strengthened to valid bodies and a strict 503 envelope before the repair.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   a database outage reaches the client as a bare plain-text 500, which the
                 web client reads as "indeterminate" (overstating uncertainty); the
                 worker's delivery loop dies on its first database error
CONSUMER         every HTTP route adapter; nquiry_worker loop
RELATION         transaction scope -> outcome (10 §14)
PRODUCER         persistence.engine.connect(): connect failure, body failure, COMMIT
                 failure and lost COMMIT are all raw driver exceptions, indistinguishable
FBR              the transaction scope does not state which of the 10 §14 cases occurred,
                 and no edge maps it to the 10 §4 outcomes
```

**3 HOME.** 10 §14, 10 §4, 09 §77/§78, 19 §29.

**4 REPAIR.**

| Piece | Change |
|---|---|
| `packages/persistence/engine.py` | `connect()` raises `DatabaseUnavailable` (connect failed), `CommitRejected` (COMMIT answered with Integrity/Programming/Data error: proven abort) or `CommitOutcomeUnknown` (other failure during COMMIT). A caller exception still propagates unchanged after rollback; a failing rollback on a lost connection never masks it. |
| `packages/application/technical_failure.py` (new) | `technical_failure_response(exc, method, idempotency_key)`. The Command/Query mapping in its docstring uses only existing kinds (`failed_precommit`, `indeterminate`). Command envelopes echo `commandId`. |
| `apps/api/src/nquiry_api/main.py` | `@app.exception_handler(Exception)` installs the mapping for every route family (F02+, older `http_dispatch`, auth). |
| `packages/projection/delivery.py`, `apps/worker/.../__main__.py` | `TECHNICAL_FAILURES`. The loop reports `delivery pass failed: <REASON>` and continues (the pass rolled back, so records stay due). `--once` and `--diagnose` exit 3. |

**Case 2 choices (recorded):**
- **A Query that cannot reach the database** is `failed_precommit` / DATABASE_UNAVAILABLE. It is true (nothing happened) and uses existing vocabulary; no "unavailable" kind is invented.
- **Technical FAILED_PRECOMMIT uses status 503** (09 §78: 5xx for technical failure). A rejected COMMIT keeps 409, the envelope's existing failed_precommit status.
- **An unknown Command failure is INDETERMINATE.** It may have occurred after COMMIT, and retrying with the same Idempotency-Key resolves it by replay (14 §27).
- **COMMIT errors are classified by driver class:** Integrity/Programming/Data means the server answered, so the abort is proven; other errors are unknown.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `persistence.engine.connect` callers (`http_f02`, `http_dispatch`, `http_f04`, `projection.delivery`) | AFFECTED (typed exceptions) | No caller catches the new types internally. They reach the edge or the worker. |
| API edge, all routes | AFFECTED | Honest envelope in place of a bare 500. |
| Existing envelope kinds and domain outcomes | NOT AFFECTED | The handler only sees exceptions that previously escaped as 500. Full regression green. |
| Worker | AFFECTED | Survives outages; `--once` exit 3. |
| Web client, CYAN | NOT AFFECTED (contract) | Existing kinds; the extra `commandId` key is ignored by `parseQuery`/`parseCommand`. A clearer UI for technical failure is a CYAN relation. |
| Coordinator INDETERMINATE path (`_record_indeterminate`) | NOT AFFECTED | Unchanged. RecoveryRecord and BND-018 remain open (HA-15). |
| Domain, authority, persistence schema | NOT AFFECTED | — |

**6 LOCAL PROOF.** ruff, format, mypy (CI scope), architecture and import checks, verify_migrations (no schema change).

**7 INTEGRATION PROOF.**
- **Engine against real PostgreSQL:**
  - A deferred UNIQUE on a temp table fails at COMMIT and raises `CommitRejected`.
  - A connection failure injected at the COMMIT event raises `CommitOutcomeUnknown`.
  - An unreachable host raises `DatabaseUnavailable`.
- **HTTP through the real FastAPI app:** all three route families, Commands and Queries.
- **Real API process** (`evidence/f09_1_runtime.txt`), with the database unreachable:
  - POST challenges → 503 `failed_precommit` DATABASE_UNAVAILABLE with `commandId`.
  - GET overview → 503 `failed_precommit`.
  - POST login → 503 `failed_precommit`.
  - `/healthz` → 200.
- **Real worker process:**
  - `--once` exits 3.
  - Loop mode keeps retrying (≥2 failure lines) and stops gracefully on SIGTERM.

**8 PRESERVATION.** `test_engine_success_and_body_failure_keep_their_semantics`, and the full regression: every existing HTTP suite asserts the existing kinds and statuses.

**9 REGRESSION.** `evidence/f09_1_regression.txt`.

**10 MUTATION.** `scripts/pfc_f09_1_mutation_proof.py`: **9/9 KILLED**, sources restored. The mutants are:
- unavailable not reported
- rejected treated as unproven
- **lost COMMIT claimed as proven abort**
- caller exception swallowed
- uncertain Command reported as failed_precommit
- unknown Command guessed
- identity not echoed
- edge not installed
- worker loop dies

**11 INVERSE PROOF.**
```text
{"kind":"indeterminate","reasonCode":"COMMIT_OUTCOME_UNPROVEN","commandId":K}
  <- technical_failure_response(CommitOutcomeUnknown, POST, K)   (API edge, every route)
  <- persistence.engine.connect: SQLAlchemyError (not Integrity/Programming/Data) during COMMIT
  <- the request transaction of the governed Command whose command_id is K (Idempotency-Key)
  <- resolution: the same K is retried -> the idempotency record replays COMMITTED or re-executes
```

**12 DEEP SWEEP.**
- No false claim: every mapping row either states a proven fact or says it cannot prove.
- No authority statement: technical failures never produce `denied`.
- No new vocabulary.
- **Residual observations:** the web client's no-blind-retry defect (a new intent key after `indeterminate`) is a CYAN relation, queued in the Field report. The decide route's STALE-as-denied mapping and the missing Idempotency-Key are the next F09 Work Unit.

**13 INVERSE DEEP SWEEP.** Every technical envelope traces back to exactly one typed fact from `connect()`, or to "unknown". No envelope is derived from an HTTP status or an exception message.

## 3. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F09-1`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F09: IN_PROGRESS.
