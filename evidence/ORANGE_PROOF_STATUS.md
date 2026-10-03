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

## 12. First complete canonical ORANGE chain after the TF-PX-04/05 repair (2026-10-03 17:41–18:14)

`final_closure.sh` at `347ed5d`, unmodified, against the frozen `checkpoint-PFC-PCPG-5` (`e0a6b3b`), PCPG-5 proof
environment. Evidence: `evidence/final_closure_20261003T174103/` (hash manifest `EVIDENCE_MANIFEST.tsv`; run stdout
`closure.log`; directory-level before/after snapshots). Nothing was re-run for this record.

| Phase | Result |
|---|---|
| Pre phases (TF-PX-04) | not refused; serial collection 2239; PARTITION_PROOF 24/24 |
| Serial reference | 2237 passed / 2 declared skips / 0 failed; SERIAL_BASELINE::PASS; instrumentation inert 2239/2239 vs `final_closure/serial_ref` |
| Governed xdist (2235) | 2233 passed + 2 declared skips, exit 0 |
| Governed serial (4) | 4 / 4 passed, exit 0 |
| Aggregation / order | AGGREGATION_AND_EQUIVALENCE::PASS (2239 nodes); PARALLEL_PROOF::PASS; ORDER_PROOF::PASS |
| Tree / env / DBs | frozen tree 0 entries before and after, content `ba25b56f…`, directory-level snapshot identical; env manifest `82f6c73a…` unchanged; heads and fingerprint unchanged, proof DBs clean and unconnected, 13 race DBs observed and dropped, 0 residue |
| Bytecode (TF-PX-05) | no bytecode in the tree; the authorized prefix was used (already warm: 0 new `.pyc` needed) |
| Processes | none left |

Canonical chain = PASS end to end. NEW_FBR = none.

Claim ceiling (unchanged by this run):
- historical `checkpoint-PFC-PCPG-5` remains **2238 / 2239, SF-PX-03 OPEN**. This run's 2239 / 2239 (the SF-PX-03
  node passed once in the governed serial partition) is an OBSERVATION, not a historical closure. The node is
  load-coupled, and the partitions now really use bytecode caching (before TF-PX-05 they ran fully cold);
- `checkpoint-SWU-PX-03` remains the legitimate successor closure at 2252 / 2252;
- performance remains provisional: serial 1363.2 s vs governed 613.5 s (608.2 + 5.3) = 2.22x, for this single
  measurement only.

## 13. Structured verbose + heartbeat (Work Unit STRUCTURED_VERBOSE_HEARTBEAT, 2026-10-03)

FBR: a legitimate long-running proof stayed silent for many minutes, so RUNNING and STALLED were
indistinguishable without inspecting processes. Repair (observability only): `progress.sh`, sourced by
`final_closure.sh`. 36 lines were inserted, none changed or removed. Stripping them gives the base
`final_closure.sh` (6f7f831) byte-identical, so command order, partition membership, test selection,
databases, environment and aggregation are unchanged.
Events (stdout, `[HH:MM:SS]` = elapsed since PROOF_START, never proof truth):
- PROOF_START;
- STAGE_START / STAGE_END / STAGE_FAIL / STAGE_TIMEOUT with the child's real exit code (read from
  `*_exit_code.txt`, because the stage drivers exit 0 regardless; `unobserved` where the chain discards it);
- HEARTBEAT every ORANGE_HEARTBEAT_SECONDS (default 30): stage, elapsed and optional pytest progress %.
  Liveness only, never a verdict;
- VERDICT copied from the chain's own NAME::PASS|FAIL lines; required verdicts that are absent report
  MISSING;
- CLEANUP;
- PROOF_END verdict=PASS only after the final verdict step, with every verdict PASS and every stage exit 0
  or unobserved; the EXIT trap reports FAIL on early exit.

Stages covered: serial_pre, serial_reference, serial_post, serial_analysis (tree / env / DB invariance
verdicts), parallel_pre, partition_proof, xdist_partition, serial_partition, parallel_post, aggregation
(equivalence, tree, env, DB, residue verdicts), order_proof, inertness, cleanup, final verdict. Field values
are restricted to a safe charset, and credential-like keys and values are replaced by <redacted>. Bracket
labels of verdict lines are never echoed.

Proof (`progress_falsifiers.sh`, `evidence/verbose_heartbeat/`), narrow radius, no product test:
- falsifiers 22/22 (F1–F15 as specified, plus progress from a real pytest-xdist log, a real canonical stage
  (serial pre, collect 2239, heartbeats, verdicts) and no event lines inside evidence files);
- mutants 8/8 killed (heartbeat PASS, heartbeat survives its stage, final PASS before aggregation, final
  always PASS, failed child ignored, secret emitted, stage order altered, timeout unreported);
- real-evidence replay: the canonical end-to-end run gives PASS (59 verdicts), and historical PCPG-5
  `final_closure` gives FAIL (serial_partition rc=1, SF-PX-03);
- existing tooling proofs green (TF-PX-04/05 harness, canonical ids 25/25, partition 24/24, aggregation
  22/22, order PASS, bash -n 12/12);
- before/after snapshot identical; no leftover processes.

No full canonical chain was run: command lines are byte-identical, the mechanics are proven on a real stage
and on real xdist, and verdict / exit-code extraction is proven on real PASS and FAIL evidence.

Disclosed (own harness defect, caught before acceptance): the first harness version cleaned its synthetic
stage with `pkill -f 'sleep 30.4321'`, which also matched (and killed) the tool shell whose command line
contained that string. The mutation run was interrupted. The orphaned driver tree was stopped by PID, and no
heartbeat survived (they exit when their chain disappears). The harness now kills only the recorded PID.
That run's evidence is preserved as `evidence/verbose_heartbeat_v1_SUPERSEDED_harness_pkill_selfkill/`.
Also fixed before acceptance: `prog_end` without `prog_begin` reports elapsed=n/a.

Claim ceiling: LONG-RUNNING ORANGE PROOF EXECUTION = STRUCTURALLY OBSERVABLE; HEARTBEAT = LIVENESS SIGNAL
ONLY; PROOF SEMANTICS = UNCHANGED. Existing claims unchanged: PCPG-5 2238/2239 with SF-PX-03 OPEN; SWU-PX-03
2252/2252 (2248 governed parallel + 4 governed serial); performance provisional. The final_closure.sh exit
code contract is unchanged (0 unless a pre phase is refused); PROOF_END is the observable summary.

## 14. Final verdict -> process exit status (Work Unit FINAL_VERDICT_EXIT_STATUS, 2026-10-03)

FBR: `final_closure.sh` could emit `PROOF_END ... FAIL` while the process exited 0, so an external machine could
observe success while the proof said FAIL. Human Authority authorized this runner-contract change.

EXIT CONTRACT (`progress.sh` EXIT trap; `final_closure.sh` itself unchanged):
- `0` = the complete canonical proof finished (final verdict step reached) with `PROOF_END verdict=PASS`;
- `1` = `PROOF_END verdict=FAIL`: any FAIL or MISSING required verdict, any failed or timed-out stage, or no
  verdict read. This follows the lineage convention (1 = failure / refusal, 2 = usage);
- an exit before the final verdict keeps its own nonzero code (a refused pre phase stays `1`, an existing
  closure directory is still refused with `1` before anything starts), and an early exit with status 0 becomes `1`.
The heartbeat never influences the exit status. Proof semantics, verdict derivation and the event stream are
unchanged: `PROOF_END` stays the single, final event, and only the exit status follows it.

Proof (`exit_status_falsifiers.sh`, `evidence/exit_status/`), narrow radius, no product test: 18/18 (E1–E12 as
specified, plus an early exit 0 becoming 1, the SWU-PX-03 failed first run, and the TF-PX-06 race):
- synthetic PASS -> exit 0; FAIL, MISSING, timeout and child failure -> exit 1;
- refused pre phase with the real canonical lines and real `serial_baseline.sh` -> 1;
- replays of the canonical `final_closure.sh` progress lines, verbatim, over recorded evidence: historical PCPG-5
  -> nonzero, canonical e2e PASS -> 0, SWU-PX-03 passing closure -> 0 (its preservation verdict substituted for
  the PCPG-5 inertness verdict, documented), SWU-PX-03 failed first run -> nonzero;
- the event stream is identical to the base helper's (normalized; the only permitted difference is a TF-PX-06
  artifact of the base, 0 removed in this run); the base helper really exited 0 on the PCPG-5 FAIL evidence
  (documents the FBR).
Mutants 7/7 killed: always exit 0, inverted status, missing verdict exits 0, timeout exits 0, PASS emitted
regardless, heartbeat controls exit, TF-PX-06 guard removed. Existing proofs green: progress falsifiers 22/22,
TF-PX-04/05 harness, canonical ids 25/25, partition 24/24, aggregation 22/22, order PASS, bash -n 13/13.
Snapshot identical; no leftover processes.
Found and fixed on the way: TF-PX-06 (SUCCESSOR_FINDINGS.md). Superseded harness runs are preserved:
`exit_status_v1_FAIL_*` (TF-PX-06 caught; the E12 check matched the harness's own command line),
`exit_status_v2_*` (the E10 base-output skip was not applied, because a sed delimiter collided),
`exit_status_v3_*` (E10b with 30 runs; raised to 100 so the TF-PX-06 mutant is killed reliably).

Claim ceiling: CANONICAL PROOF VERDICT = REFLECTED BY PROCESS EXIT STATUS; PASS -> exit 0, non-PASS -> exit nonzero.
Proof semantics unchanged; verbose + heartbeat remain liveness / presentation only. Product claims unchanged:
PCPG-5 2238/2239 with SF-PX-03 OPEN; SWU-PX-03 2252/2252; performance provisional.
