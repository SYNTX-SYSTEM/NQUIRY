# WU-PFC-F08-3 — Delivery diagnostics and projection freshness

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F08-3 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · F08 |
| Colour / role / model | RED · persistence / worker · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26). |
| Derivation | 19 §28 internal Work Units "projection freshness" and "diagnostics": the last two backend units of F08. 09 §122 (AC-09-010) requires delivery observability. |
| Current state / predecessor | `pfc-integration` `02c74a1`; `checkpoint-PFC-F08-2` → `461ade4`. Migration head `c3b8e5a1f7d2`. |
| Baseline | Live 1773 passed / 2 skipped; no-DB 894 passed. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`; runtime evidence against `nquiry_pfc_int_runtime` (read-only). |
| Authorized delta | Read-only freshness per Workspace; read-only delivery diagnostics per Workspace or overall; the operator command `python -m nquiry_worker --diagnose`. **Not in scope:** an HTTP or API surface (no consumer needs it yet; read authority for operator data is part of HA-11); CYAN. |
| Must become true | A stale projection is distinguishable from a fresh one. Pending, failed, delivered and without-basis backlogs are countable without raw SQL. |
| Must remain true | Delivery semantics; every predecessor suite. |
| Must remain impossible | Diagnostics writing anything; one Workspace's backlog leaking into another's freshness; a poison backlog reported as fresh. |
| Falsifiers | `tests/e2e/test_pfc_f08_3_diagnostics.py` (6 cases). |

## 2. Execution record

1. **RED.** 6/6 failed for the right reasons: `DeliveryPorts` had no `freshness` and no `diagnostics` (×4), and `--diagnose` was unrecognized (×2).
2. **FBR.** Delivery runs (F08-2), but nothing states how far a Workspace's projections trail its committed history, or how large the pending, failing and poison backlog is. A stale projection is indistinguishable from a fresh one.
3. **Home.** 19 §28; 09 §122.
4. **Repair.**
   - `packages/persistence/delivery_diagnostics.py` (new): `projection_freshness` and `delivery_diagnostics`. Single aggregate SELECTs, with counts filtered per 09 §15.1 status and a basis check via an outer join to `committed_events`.
   - `DeliveryPorts.freshness` and `.diagnostics`.
   - `--diagnose` prints JSON and exits 0; it inherits the fail-closed start (exit 2 without a DB).
   - **Case 2 choice:** a record that failed without a basis counts as undelivered, so a poison backlog is never reported as fresh.
5. **Propagation.**
   - AFFECTED: `projection.delivery` ports; worker CLI; new persistence read module.
   - NOT AFFECTED: delivery, projection and consumer semantics; canonical, audit and outbox writes; API; CYAN; migrations (no schema change).
6. **Local proof.**
   - ruff, format, mypy (CI scope) and architecture checks.
   - `projection` → `persistence` / `semantic_types` is already allowed.
7. **Integration proof.**
   - The falsifiers run real commits and a real delivery pass on PostgreSQL. Freshness is stale (count = outbox rows, oldest = min commit time), then fresh after the pass (`last_delivered_at` = pass time).
   - Diagnostics count PENDING, FAILED, DELIVERED and without-basis correctly before and after a poison pass.
   - The real process `--diagnose` runs against the runtime DB (`evidence/f08_3_runtime.txt`): `{"delivered": 24, "failed": 0, "pending": 0, "without_basis": 0, ...}`.
8. **Preservation.** The write-nothing falsifier: outbox status and attempts are identical after every read. The Workspace-scope falsifier. The full regression.
9. **Regression.** `evidence/f08_3_regression.txt`.
10. **Mutation.** `scripts/pfc_f08_3_mutation_proof.py`: **5/5 KILLED**, sources restored. Equivalent mutants (max attempts over all rows, which is equal in every reachable fixed-clock state) were deliberately not counted.
11. **Inverse.** Each JSON field traces to one aggregate over `outbox_events` and `committed_events`. Those rows trace to CommitUnits (F08-1) and delivery passes (F08-2).
12. **Deep sweep.**
    - No write path.
    - No authority read: operator data is served only to a process holding DATABASE_URL, never over HTTP.
    - No semantic drift.
13. **Inverse deep sweep.** "fresh = true" holds only when zero outbox rows of that Workspace are non-DELIVERED, and each DELIVERED row traces to a committed pass.

## 3. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F08-3`). Not REVIEWED_FIELD, not PUBLISHED_FIELD.

With F08-3, every backend internal Work Unit of 19 §28 is materialized. See `F08_FIELD_REVIEW_BUNDLE.md` for the Field-level status.
