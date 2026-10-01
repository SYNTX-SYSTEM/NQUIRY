# WU-SWU-PX-03 — worker readiness instead of a fixed time window (SF-PX-03)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Field | SWU-PX-03 · product successor field of the ORANGE proof pass (SF-PX-03 FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT) |
| Human authorization | "PASS. Start SWU-PX-03 as a NEW PRODUCT SUCCESSOR FIELD." and "HUMAN AUTHORITY DECISION — SF-PX-03 SUCCESSOR PREPARATION ... Proceed with SWU-PX-03." (2026-10-01). |
| Base | `checkpoint-PFC-PCPG-5` = `e0a6b3b25d4309d16d6e3db3ee0958183a279dfd`, branch `swu-px-03-worker-readiness`, worktree `worktrees/swu-px-03`. `checkpoint-PFC-PCPG-11` (`96320bc`) descends from the base and touches neither changed product/test file. |
| Historical claim (unchanged, permanent) | PCPG-5 PRODUCT / TEST EQUIVALENCE 2238 / 2239; SF-PX-03 OPEN for PCPG-5. Published ORANGE lineage `orange-proof-lineage` @ `c9f276fc` is not modified. |
| Must become true | WORKER PROCESS START → SIGTERM and SIGINT handlers actually installed → explicit readiness observable → required DATABASE_UNAVAILABLE passes observed → SIGTERM → graceful stop → returncode 0 + "stopped". |
| Must remain true | Every existing worker behaviour (`--once` exit 3/0, `--diagnose`, exit 2 without `DATABASE_URL`, pass reports, graceful stop); the three graceful-stop assertions of the node, byte-identical; no migration. |
| Must remain impossible | SIGTERM sent on an assumed elapsed time; a longer or another arbitrary sleep; retry-until-green; a weakened assertion; a suppressed load-sensitive failure; a hang (every wait is bounded and fails with a diagnostic); a process outliving its test. |

## 2. Execution record

**1 RECONSTRUCTION OF SF-PX-03 (from the published ORANGE evidence).** `evidence/final_closure/parallel/serial_run.log`: the node failed with `assert -15 == 0` and an EMPTY assertion message (`err == ""`). The worker had written nothing in 2.5 s, so it had not yet reached its handler installation, and SIGTERM met the default disposition. The same node passed in the full serial reference straight after its `--once` sibling (warm start), and failed in the 4-node serial partition as the first worker start of its window (cold start). The coupling is to execution context and load, not to the worker's behaviour.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   returncode -15 / empty stderr under load or cold start
CONSUMER         tests/e2e/test_pfc_f09_1_technical_failure.py::
                 test_worker_loop_survives_a_database_outage_and_stops_gracefully
                 (time.sleep(2.5) -> SIGTERM)
PRODUCER         apps/worker/src/nquiry_worker/__main__.py: handlers installed only after
                 the heavy imports and the startup observation; NO readiness signal
FBR              the consumer infers "imported + handlers installed + >= 2 passes" from
                 2.5 s of wall clock; the producer offers nothing observable instead
```

**3 REPAIR** (1 product line + docstring, 1 consumer, 1 support module, 1 falsifier module).
- Producer `apps/worker/src/nquiry_worker/__main__.py`: `nquiry_worker: ready.` on stderr (flushed), printed immediately AFTER both `signal.signal` calls and BEFORE the first pass. Printed in `--once` mode too (its handlers are installed as well). Docstring states the contract.
- Consumer `tests/e2e/test_pfc_f09_1_technical_failure.py`: `time.sleep(2.5)` removed. It now waits for the ready line, then for two observed `DATABASE_UNAVAILABLE` pass reports, then sends SIGTERM. The three assertions (`returncode == 0`, `count("DATABASE_UNAVAILABLE") >= 2`, `"stopped" in err`) are unchanged. The unused `import time` is removed.
- `tests/e2e/worker_readiness_support.py` (new, `tests/e2e/*_support.py` convention): `WorkerProcess` drains both pipes on reader threads and waits on observed stderr under a condition variable. Every wait has a 60 s FAIL / NO-HANG bound (the sibling `--once` test's own bound), which is never a readiness proof. A worker that exits before the awaited state fails AT ONCE with its exit status. `close()` kills, reaps, joins, and closes the pipes only after the readers have ended.
- `tests/e2e/test_swu_px_03_worker_readiness.py` (new): the falsifiers (§3).

**4 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `nquiry_worker --once` / `--diagnose` / no `DATABASE_URL` | NOT AFFECTED (proven) | `--diagnose` and the exit-2 refusal return before the handlers. `--once` gains one stderr line, and its consumers assert only substrings (`delivery pass`, `DATABASE_UNAVAILABLE`, `DATABASE_URL`) and exit codes. |
| `test_pfc_f09_3_telemetry` (in-process `main(["--once"])`) | NOT AFFECTED (proven) | Same handler installation as before, plus one print. |
| Delivery semantics (`run_delivery_pass`, `open_delivery`) | NOT AFFECTED | Untouched. |
| Schema / migrations | NOT AFFECTED | None. Migration head stays `e8c2a5f1b7d4`. |

**5 PROOFS.**
- Static: `ruff check` / `ruff format --check` clean on the 4 changed Python files. `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` PASS. `mypy` reports no issue in the changed files; 2 errors remain in untouched `packages/persistence/*` (pre-existing at the base).
- RED (right reason): the unrepaired producer is mutant M2 (no ready line). The repaired consumer then fails at its bound with `readiness not observed within the 60 s fail bound`. It does not hang and does not pass.
- Local falsifiers: 13 cases (§3), together with `test_pfc_f09_1_technical_failure.py`. Result: 22 passed, 3 skipped (the file's own `DATABASE_URL` skips, DB-free run), and the CPU case run separately in the load window.
- Mutation (5 guards, each applied to a COPY of the tree, never to the worktree):
  M1 ready line before handler installation → killed (ordering falsifier);
  M2 ready line removed → killed (node + both stop-after-readiness cases, bounded 60 s failures);
  M3 SIGINT handler not installed → killed (ordering falsifier + SIGINT case);
  M4 wait ignores an early exit → killed (exit-before-readiness case);
  M5 cleanup neither kills nor reaps → killed. The helper fails at its bound and the residue fixture reports and reaps the leftover worker; the driver sweep found 0 leftovers.
  A first M5 run exposed a hang: closing a pipe a reader still blocked on waited for that reader's lock. Fixed before acceptance. `close()` closes the pipes only after the readers end, and the residue fixture kills and reaps before it fails. All 5 mutants were re-run after the fix.
- Affected suites (proof database `nquiry_proof_serial_test`, verified clean, unconnected and at head before and after): 19 selections (every consumer of `nquiry_worker` / `apps/worker`, every `tests/e2e` scanner, all of `tests/regression`, `tests/security`, `tests/mutation`). Result: 428 passed, 2 skipped (the 2 declared skips of the accepted serial reference), 0 failed. Deselected (12): `tests/security/test_db_principals.py` (11; it creates the cluster-global `zz_pkg25` role, authorized only inside ORANGE runs, and is covered by the successor ORANGE run) and the CPU case (run in the load window).
- Load-contention proof (out of suite, run only in an idle window: no foreign pytest process, checked at the OS level before the run and before every round). NEW = the repaired node. OLD = a verbatim copy of the PCPG-5 consumer used only as a witness, never part of the product; it runs against the same successor worker.

  | Condition | NEW runs / failures | OLD witness runs / failures | max load1 |
  |---|---|---|---|
  | C0 idle, warm bytecode | 10 / 0 | 10 / 0 | 6.0 |
  | C1 cold start (no bytecode cache, nothing written) | 10 / 0 | 10 / 10 | 8.6 |
  | C2 2 x CPU busy processes, warm | 10 / 0 | 10 / 10 | 34.0 |
  | C3 2 x CPU busy processes, cold | 10 / 0 | 10 / 10 | 32.3 |
  | C4 2 x CPU busy, cold, 4 concurrent runs | 8 / 0 | 8 / 8 | 27.8 |

  NEW_CONSUMER_FAILURES=0 of 48. OLD_WITNESS_FAILURES=38 of 48. LOAD_CONTENTION_PROOF::PASS. The conditions are effective: the old relation breaks in every loaded or cold condition. 37 witness failures carry the published SF-PX-03 signature (`assert -15 == 0`, SIGTERM before the handlers). One (C2) shows the second failure mode of the fixed window (`assert 1 >= 2`: handlers installed, one pass only). The repaired consumer covers both, because it waits for readiness and for two observed passes. Residue after the run: 0 workers, 0 busy processes.
  Bound headroom under C3, measured directly (5 starts): readiness after 8.8–15.2 s (3.5x to 6x the old 2.5 s assumption), two passes 1.7–2.9 s later, all graceful. The 60 s fail bound kept at least 44.8 s of headroom. Beyond about 4x the C3 contention, the node would end in a bounded diagnostic failure (`readiness not observed within the 60 s fail bound`), never in a hang or a false pass.

## 3. Falsifier map (`tests/e2e/test_swu_px_03_worker_readiness.py`, 13 cases)

| Required falsifier | Case |
|---|---|
| handlers installed before readiness (deterministic) | `test_readiness_is_announced_only_after_both_stop_handlers_are_installed` (in-process event order) |
| SIGTERM before handler installation | `test_sigterm_before_handler_installation_is_not_a_graceful_stop` (gated start: returncode -15, no ready, no stopped) |
| old relation falsified (witness) | `test_the_old_fixed_window_consumer_fails_when_startup_outlasts_it` (the published SF-PX-03 signature: -15, empty stderr) |
| readiness reached / graceful stop after readiness | `test_a_stop_right_after_readiness_is_graceful[SIGTERM,SIGINT]`, `test_readiness_reached_then_passes_then_graceful_stop` |
| delayed startup | `test_delayed_startup_beyond_the_old_window_still_stops_gracefully` (5 s delay before import) |
| high CPU contention | `test_high_cpu_contention_does_not_change_the_outcome` (one busy process per CPU) |
| relevant DB contention | `test_a_slowly_failing_database_does_not_change_the_outcome` (each connection held 1 s, then dropped) |
| readiness never reached / bounded diagnostic failure | `test_readiness_never_reached_fails_at_the_bound_with_a_diagnostic`, `test_a_worker_that_exits_before_readiness_fails_at_once` |
| no orphan processes / deterministic cleanup | autouse `no_process_residue` (every case), `test_cleanup_reaps_a_running_worker_and_its_readers`, `test_cleanup_is_idempotent_after_a_graceful_stop` |

## 4. Disclosures

- TF-PX-03 EMPTY_IGNORED_DIRECTORY_NOT_CAPTURED_BY_GIT_OR_CONTENT_HASH (Human Authority classification, 2026-10-01). The historical frozen worktree `worktrees/orange-proof-infra` contains an empty `pycache/` directory skeleton (0 files), created at 01:09:28 by the xdist start of ORANGE `parallel_run1`. It is invisible to `git status --ignored` and to the file-content hash. No change to product semantics, the frozen git tree, the recorded content hash or the PCPG-5 2238/2239 claim. "Filesystem pristine at directory level" is NOT claimed for that historical worktree. Left untouched by decision. The published `orange-proof-lineage` commit is not amended.
- The CPU falsifier loads the machine for a few seconds. Under a parallel run it is a noisy neighbour for the other workers, and on a shared machine for other lanes. The in-suite load is limited to one busy process per CPU. Heavier and longer contention is in the out-of-suite load proof, run only in an idle window (no other lane's suite running). One earlier local run used 2 x CPU for about 4.6 s while the PURPLE lane's suite was running; no effect on PURPLE is known.
- Local proof environment: `.venv-swu-px-03`, the ORANGE environment's exact 48 distributions minus the ORANGE guard (freeze identical), no first-party distribution, no path binding. Bytecode is written outside the tree.
- Not run here: the full ORANGE proof against the successor checkpoint. It is the next step and needs the successor checkpoint first.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** SF-PX-03 is repaired in the successor: the tested relation depends on an observable readiness condition produced only after both stop handlers are installed, not on elapsed wall-clock time. Local falsifiers 13/13; mutation 5/5 killed; affected suites 428 passed / 2 declared skips / 0 failed; load-contention 0/48 failures (witness 38/48). Not committed, not tagged, not pushed. The successor ORANGE proof (full governed run against the new successor checkpoint) has not been run. Until it has, no successor equivalence claim exists. The historical claim stays PCPG-5 2238 / 2239 with SF-PX-03 OPEN.
