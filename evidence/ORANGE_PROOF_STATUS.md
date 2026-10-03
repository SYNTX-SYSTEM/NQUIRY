# ORANGE proof infrastructure — status of the frozen PCPG-5 proof pass

Human Authority decision (2026-10-01): close the frozen pass with an HONEST SCOPED CLAIM.
Frozen target: checkpoint-PFC-PCPG-5 @ e0a6b3b25d4309d16d6e3db3ee0958183a279dfd
(worktree `worktrees/orange-proof-infra`, branch `orange-proof-infra`, never modified).

## 1. Final proof status

```
FROZEN PCPG-5 PROOF INFRASTRUCTURE:
2238 / 2239 NODE EQUIVALENCE PROVEN

1 / 2239:
KNOWN LOAD-COUPLED TEST RELATION
FORMALLY OPEN
SUCCESSOR REQUIRED (SWU-PX-03)
```

2238_EQUIVALENT + 1_LOAD_COUPLED != 2239_EQUIVALENT.
NOT claimed: complete frozen-field equivalence; final parallel-proof PASS; "2239 nodes in parallel".

Verification of the number (from `parallel_run2/aggregated_outcomes.tsv` vs the accepted serial
reference `serial_run2/canonical_outcomes.tsv`): 2239 canonical nodes; 2238 equivalent
(xdist 2233 passed + 2 declared skips; serial 3 passed); 1 divergent:
`tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully`
(serial partition: failed, reference: passed).

## 2. Relations proven (evidence under `.venv-proof313-orange/orange-proof/evidence/`)

| Relation | Evidence |
|---|---|
| Frozen tree identity (HEAD = tag, 0 entries incl. ignored, content sha256 `ba25b56f…` constant across every run) | `*/pre_tree.txt`, `*/post_tree.txt` |
| Hermetic env: CPython 3.13.15, no user site, no first-party dist, exact historical pair fastapi 0.122.0 / starlette 0.50.0, 49 dists fully explained | `manifest.json`, `historical_state_delta.txt`, `px1_falsifiers_run3_pinned.log` |
| Import-origin guard (fail-closed, incl. xdist workers; exit never 5) | `px1_falsifiers*.log`, `*/pre_guard.txt`, `*/post_guard.txt` |
| Proof databases: 5 allowlisted, canonical provisioning, literal MIGRATION_LIVE_CHECK::PASS, identical sensitive schema fingerprint `3c899691…`, clean, unconnected; heads preserved | `db/`, `*/pre_proof_dbs.*`, `*/post_proof_dbs.*` |
| Serial baseline (accepted reference): 2237 passed / 2 declared skips / 0 failed | `serial_run2/` |
| Canonical identity (evidence-only, injective, 24 falsifiers) | `canonical_ids_proof.log` |
| Governed partition execution (2235 xdist + 4 serial; complete accounting, no overlap / omission / duplicate; 24 falsifiers) | `partition_v2/`, `parallel_run2/partition_proof.log` |
| Worker <-> DB isolation (gwN -> nquiry_proof_gwN_test; fail-closed; identity-checked) | `binding_proof_v2.log`, `parallel_run2/binding/` |
| Scheduling safety (per-worker increasing collection order; connection-leaking tests never precede race tests) | `parallel_run1/order_proof.log`, `parallel_run2` order proof |
| Aggregation fail-closed (exit 5 = failure, duplicates, drift, divergence; 22 falsifiers) | `partition_v2/aggregate_proof.log`, `parallel_run2/aggregate.log` |
| Cluster-global cleanup: 13 race_* DBs + zz_pkg25_mut01_no_grants_role created and dropped by the run, 0 residual; nothing pre-existing touched | `parallel_run2/observed_cluster_objects.log`, `post_race_dbs.txt`, `post_zz_roles.txt` |
| Connection cleanup (0 foreign connections on all proof DBs after every run) | `*/post_proof_conns.txt`, `post_proof_dbs.json` |
| Measured wall-clock evidence | section 4 |

## 3. The one unresolved relation

SF-PX-03 — FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT (see `SUCCESSOR_FINDINGS.md`).
The node assumes readiness / stoppability through a fixed 2.5 s wall-clock interval; the assumption is not
invariant under legitimate machine load. History: serial run 1 FAIL (no bytecode cache), serial run 2 PASS,
parallel run 1 FAIL (xdist partition), parallel run 2 FAIL (serial partition; other lanes' load). Idle
start-up + one pass: 0.77–0.88 s. No retry, no precondition, no worker reduction, no tree change.

## 4. Measured execution timings

| Run | Partition | Wall clock | Result |
|---|---|---|---|
| serial_run1 (fastapi 0.142.2, no bytecode cache) | full 2239 | 2032.6 s (pytest) | 3 failed |
| serial_run2 (accepted reference) | full 2239 | 2504.1 s (41:44) | PASS |
| parallel_run1 | xdist 2236 / serial 3 | 861.7 s / 9.9 s = 871.6 s | 1 failed (xdist) |
| parallel_run2 | xdist 2235 / serial 4 | 886.2 s / 11.1 s = 897.3 s | 1 failed (serial partition) |

All on a shared machine carrying other lanes' suites (load averages about 7–15 on 8 CPUs).

## 5. Legitimate performance claim ceiling (PROVISIONAL)

Measured: governed proof 897.3 s vs accepted serial baseline 2504.1 s = 2.79x wall-clock reduction
(parallel run 1: 2.87x), on a shared, heavily loaded machine.
Classification: EXECUTION EVIDENCE, PROVISIONAL — complete equivalence remains open (1 node), so it is
NOT a certified equivalent-proof speedup. Allowed statement: "governed 2235-node 4-worker partition + 4-node
serial partition completed in about 15 min vs about 42 min serially, with 2238/2239 nodes proven equivalent".

## 6. Successor SWU-PX-03 boundary

Authoritative text: `SUCCESSOR_FINDINGS.md` "SWU-PX-03 — AUTHORITATIVE SUCCESSOR WORK UNIT".
Purpose: replace the fixed wall-clock readiness assumption with readiness-based synchronization, preserving
the technical-failure semantics. Required falsifiers: delayed start-up, CPU contention, DB contention where
relevant, handler not yet installed, readiness reached, readiness never reached, graceful stop after
readiness, bounded failure. Product/test tree + a new frozen checkpoint; NOT part of this pass.
Other successors: SF-PX-01 (fastapi >= 0.138 blinds two route-inventory proofs), SWU-PX-02 (deterministic
test ids), canonical pyproject dependency declarations (test client, pytest-xdist).

## 7. Disclosed deviations (not normalized away)

- One read-only SELECT of `alembic_version` each on `nquiry` and `nquiry_test` during PX-1 (non-mutating
  boundary deviation; no evidence depends on it).
- The environment differs from the historical proof environment in 27 distributions beyond the pinned
  pair (e.g. SQLAlchemy 2.1.1 vs 2.0.36); only the pair was authorized to be pinned.
- The accepted serial reference ran under proof-owned guard 1.0.0; the parallel runs under guard 1.2.0
  (adds the worker-DB binding plugin and an order-observation hook). Identical interpreter, prefix, path
  binding and every other distribution. Inertness in serial is proven by planning (`--setup-plan`, N7),
  not by a fresh serial execution under 1.2.0.
- Two tooling defects of my own were found by their falsifiers and repaired at local radius (analyzer
  `::` split, aggregator duplicate blindness); one probe defect (SIGTERM to a subshell) orphaned 20 probe
  workers, all terminated, and the probe's B3 "closure" was later falsified by the real run.

## 8. FINAL ENVIRONMENT CLOSURE (Human Authority 2026-10-01; evidence `final_closure/`)

ONE proof environment (guard 1.2.0) for both phases; env manifest sha256 identical across all four
captures (serial pre/post, parallel pre/post: `82f6c73a…`, content `7a833a0c…`). Catalog/observer access
through PROOF databases only (gw0 during the serial reference, serial db during the partition phase;
static check NON_PROOF_DB_REFERENCES::PASS; no non-proof database was contacted).

| Phase | Result |
|---|---|
| Serial reference (2239, guard 1.2.0) | 2237 passed / 2 declared skips / 0 failed; all 15 serial criteria PASS; wall 1958.6 s |
| Instrumentation inertness vs accepted reference (serial_run2, guard 1.0.0) | 2239/2239 identical outcomes; INSTRUMENTATION_INERT_FOR_SERIAL_OUTCOMES::PASS |
| Governed partitions (2235 xdist / 4 serial) | xdist 2233 passed + 2 declared skips, exit 0, wall 755.7 s; serial partition 3 passed + SF-PX-03 node FAILED, wall 12.5 s |
| Aggregation vs the same-environment serial reference | 2238/2239 equivalent; FAIL only on the SF-PX-03 node (fail-closed) |
| Worker<->DB binding / partition / order / cleanup | PASS / 24/24 / PASS / 13+13 race DBs observed and dropped, role test passed in both phases, 0 residual |
| Tree / heads / guard | unchanged (`ba25b56f…`, `e8c2a5f1b7d4`, PASS) |

PROOF-INFRASTRUCTURE ENVIRONMENT RELATION: CLOSED (SERIAL_REFERENCE_ENVIRONMENT = PARALLEL_PROOF_ENVIRONMENT,
instrumentation inert). PRODUCT/TEST EQUIVALENCE: 2238/2239 — unchanged scoped claim; SF-PX-03 OPEN.
Wall clock, same environment: serial 1958.6 s vs governed 768.2 s (755.7 + 12.5) = 2.55x (provisional
for full equivalence; certified only for the 2238 equivalent nodes).

## 9. Versioned proof-infrastructure lineage (Human Authority 2026-10-01)

PRODUCT / TEST TARGET != PROOF INFRASTRUCTURE. The previously unversioned ORANGE material is versioned in
its own lineage: orphan branch `orange-proof-lineage`, worktree `worktrees/orange-proof-lineage` (no product
history, no product code, no frozen tests). It targets the immutable PCPG-5 tree externally (TARGET.json)
and never modifies it. Evidence policy: all final-closure evidence committed; curated evidence (<= 100 KB per
file) of earlier runs committed; 36 bulky raw files of superseded runs excluded but sha256-recorded in
EVIDENCE_MANIFEST.tsv (originals kept at .venv-proof313-orange/orange-proof/). Runtime artifacts (bytecode
cache, guard build output, observer stop markers) and the venv itself are never versioned.
Scripts were made location-independent and evidence-safe (no default ever overwrites committed evidence);
this is a path / IO change only, re-proven at local radius from the lineage (evidence/lineage_reproof/).
Status unchanged: PROOF INFRASTRUCTURE CLOSED (claim ceiling as recorded); PRODUCT/TEST 2238/2239;
SF-PX-03 OPEN; successors SF-PX-01, SWU-PX-02, SWU-PX-03, pyproject declarations, TF-PX-01.
Lineage re-proof found one tooling defect (cadence miss): px1 P8/N6 not re-run after guard 1.1.0; repaired in
the lineage and re-proven (TF-PX-02 in SUCCESSOR_FINDINGS.md). No closure evidence is affected.

## 10. SWU-PX-03 successor proof (Human Authority FINAL_PROOF_RECORDING, 2026-10-03)

The product successor `checkpoint-SWU-PX-03` (`944f1ae`, parent PCPG-5) replaces the fixed 2.5 s window with
readiness-based synchronization. The final ORANGE proof against it (successor binding of this lineage, guard
1.2.0+swupx03, PCPG-5 environment's distributions): PARALLEL_PROOF::PASS, ORDER_PROOF::PASS,
SUCCESSOR_PRESERVES_PCPG5_SERIAL_OUTCOMES::PASS. Serial reference 2250 passed / 2 declared skips / 0 failed (15/15).
Governed: xdist 2246 passed + 2 skips, serial 4/4.

```text
SWU-PX-03 = SUCCESSOR PRODUCT/TEST EQUIVALENCE PROVEN
          = 2252/2252 COMPLETE COVERAGE = 2248 GOVERNED PARALLEL + 4 GOVERNED SERIAL
          = SF-PX-03 CLOSED FOR SUCCESSOR
          = PCPG-5 HISTORICAL RECORD PRESERVED (2238/2239, SF-PX-03 OPEN, unchanged)
          = PERFORMANCE SPEEDUP / WALL-CLOCK STILL PROVISIONAL (637.2 s governed, SINGLE MEASUREMENT)
```

Never "2252 parallel". Tooling defects found on the way: TF-PX-04 and TF-PX-05 (proof-lineage
infrastructure, repaired in the successor binding, still present in this lineage's PCPG-5-bound scripts),
plus the historical PCPG-5 bytecode-prefix disclosure (SUCCESSOR_FINDINGS.md). Record and evidence:
`successors/SWU-PX-03/`.

## 11. Canonical tooling repair ORANGE-TF-PX-04-05 (2026-10-03)

TF-PX-04 and TF-PX-05 are CLOSED in the canonical lineage tooling (`final_closure.sh`, `parallel_proof.sh`).
The repairs are code-identical to the SWU-PX-03 successor binding. Falsifiers 12/12, mutants 3/3 killed, and the
existing lineage proofs are still green. No product code, no product test, no checkpoint and no historical
evidence changed. All claims above (PCPG-5 2238/2239; SWU-PX-03 2252/2252) are unchanged by this repair.
Details: SUCCESSOR_FINDINGS.md, `evidence/tf_px_04_05/`.
