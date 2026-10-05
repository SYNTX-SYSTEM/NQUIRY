# ORANGE proof lane — successor findings

## SF-PX-01 — CURRENT_RUNTIME_DEPENDENCY_STATE_CAN_BLIND_TWO_ROUTE_INVENTORY_SECURITY_PROOFS

Recorded by Human Authority decision "EQUIVALENCE ENVIRONMENT" (2026-09-30).
Classification: **SUCCESSOR PROOF FINDING**. It is **not** classified as a product security
vulnerability from this evidence alone.

**Observed (ORANGE serial run 1, 2026-09-30 23:01–23:35, frozen PCPG-5 @ e0a6b3b):**
- Under fastapi 0.142.2 / starlette 1.7.0, `app.include_router()` adds opaque `_IncludedRouter`
  entries to `app.routes` (6 here, no `path`/`methods`) instead of flattening the included routes.
- Two frozen-tree security proofs build their route inventory from `app.routes` and therefore see
  an empty set, and fail:
  - `tests/e2e/test_http_f03.py::test_no_route_can_update_delete_or_rewrite_a_question`
  - `tests/e2e/test_pfc_f09_2_isolation_sweep.py::test_the_sweep_covers_every_route`
- The routes are still served (34 OpenAPI paths; every HTTP test passed).
- Published wheels: `_IncludedRouter` is absent in fastapi 0.122.0 and 0.135.0, present in 0.138.0,
  0.140.0, 0.141.1, 0.142.2. The current BLUE runtime container (`nquiry-api-1`) resolves fastapi
  0.141.1. The frozen tree declares `fastapi>=0.115`, which admits all of these.

**Open question for the successor Work Unit (to be determined, not assumed):**
- do the tests require adaptation to the newer framework API, or
- does the runtime dependency require constraint, or
- did an actual product-visible security invariant change?

**Constraint during the frozen equivalence pass:** the two tests are NOT modified. The equivalence
environment pins the historically proven pair fastapi==0.122.0 / starlette==0.50.0
(`orange-proof/equivalence-pins.txt`).

## SF-PX-02 — nondeterministic parametrize node ids (context for the xdist relation)

`tests/security/test_dev_identity_provisioning.py::_email()` returns `dev-{uuid4().hex[:10]}@dev.local.test`
at import time; two parametrize node ids therefore differ on every collection. Reported by the serial
analyzer as NONDETERMINISTIC_NODE_ID (never silently equated). Not modified.

## SWU-PX-02 — SUCCESSOR WORK UNIT: deterministic test identity in the product/test tree

Human Authority "TEST IDENTITY EQUIVALENCE" (2026-10-01). Out of scope for the frozen PCPG-5 pass.
Make `tests/security/test_dev_identity_provisioning.py::test_malformed_input_is_refused` parametrize
node ids deterministic in the tree itself (e.g. explicit `ids=`), without changing what is asserted.
Until then the ORANGE lane uses the proof-only canonicalization below for EVIDENCE COMPARISON ONLY.

### Proof-lane canonical identity (orange-proof/canonical_ids.py; proof: canonical_ids_proof.py, 24/24 PASS)
- Scope: node ids starting `tests/security/test_dev_identity_provisioning.py::test_malformed_input_is_refused[`.
- Volatile span: exactly `dev-<10 lowercase hex>@dev.local.test` (source: `_email()` = uuid4().hex[:10]).
- Token: `dev-<uuid4hex10>@dev.local.test`. Raw ids preserved (`canonical_outcomes.tsv`).
- Proven: evidence-only (not in tree, not in any pytest-loaded plugin); only 2 of 2239 ids affected;
  deterministic; injective over both full collections; canonical sets equal across collections;
  junit form consistent; 8 no-collapse falsifiers; the injectivity guard detects a sloppy mutant.
- NOT closed by it: xdist's own execution-time identical-collection check (xdist/remote.py:259-261 sends
  RAW ids; xdist/scheduler/load.py:258-259 aborts on difference) — comparison-only canonicalization
  cannot and must not alter that.

## SF-PX-03 — FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT (authoritative label, Human Authority 2026-10-01; earlier label: FIXED_TIME_WINDOW_NOT_PARALLEL_LOAD_SAFE)

`tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully`
spawns `python -m nquiry_worker`, sleeps a FIXED 2.5 s, sends SIGTERM and requires returncode 0 and >= 2
failing passes. Its precondition (subprocess start-up << 2.5 s) held serially (sibling `--once` test:
1.28 s, serial run 2) but not under the governed 4-worker lane (sibling: 4.87 s; the node itself got
SIGTERM before installing its handler -> returncode -15), parallel_run1, 2026-10-01 01:09-01:24, with
BLUE's own suite running concurrently on :15433. The earlier 8-way contention probe (min 3 passes) did
not model the real lane load; its B3 closure is FALSIFIED by this run and recorded as such.
Not modified. Decision on the execution partition belongs to Human Authority; a successor Work Unit may
make the window relative to process readiness in the tree itself.
Human Authority disposition (2026-10-01): the node is moved, unchanged, from the governed xdist partition
into the governed serial partition (orange-proof/serial_partition_selectors.txt). New decomposition:
2235 governed 4-worker parallel + 4 governed serial = 2239 coverage. The failing parallel_run1 evidence
is kept unchanged as the permanent record of this finding.

## SWU-PX-03 — (superseded proposal text; see AUTHORITATIVE SWU-PX-03 below)

Scope: `tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully`
(product/test tree; out of scope for the frozen PCPG-5 equivalence pass).
Relation to repair: the test couples its assertion to a fixed wall-clock window (`time.sleep(2.5)` before
SIGTERM) and therefore to machine load, not to the worker's observable state.
Proposed direction (to be derived and reviewed in that Work Unit, not assumed here):
- wait for an observable readiness signal (e.g. the first `DATABASE_UNAVAILABLE` line on stderr, i.e. the
  loop is running and its signal handler is installed) with a generous upper-bound timeout, instead of a
  fixed sleep;
- then wait for a second failing pass (the "kept trying" property) by observation, again upper-bounded;
- only then send SIGTERM and assert returncode 0 and the "stopped" line — the same three semantic
  assertions as today, none weakened.
Falsifiers to include: worker never becomes ready -> fails at the timeout (not a hang); worker exits on
the first failure -> fails the ">= 2 passes" assertion; SIGTERM before handler installation is impossible
by construction.
Proof obligation after that Work Unit: re-derive the ORANGE partition (the node could return to the xdist
partition only if proven load-safe under the governed lane).

### SF-PX-03 — addendum after parallel_run2 (2026-10-01 01:31–01:46)
With the node moved to the SERIAL partition (2235 xdist + 4 serial), the xdist partition was fully green
and equivalent, but the node FAILED AGAIN in the serial partition (returncode -15 after 2.51 s), with the
xdist workers already finished and BLUE's and PURPLE's own suites loading the machine (load 1/5 min 7.8/12.1).
Minutes later, with no other suite running, subprocess start-up + one pass measured 0.77–0.88 s (5/5).
History of this node: serial run 1 FAIL (no bytecode cache), serial run 2 PASS (2.77 s), parallel run 1
FAIL (xdist load), parallel run 2 FAIL (serial partition, external machine load).
=> The coupling is to MACHINE-WIDE load (including other lanes), not to the ORANGE lane's parallelism.
No retry was performed. The node was not modified.

## SF-PX-03 — Human Authority disposition (final for the frozen PCPG-5 pass, 2026-10-01)
Status: FORMALLY OPEN. The frozen test assumes readiness / stoppability through a fixed 2.5 s wall-clock
interval; observed evidence shows this assumption is not invariant under legitimate machine load.
Node: tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully
= FORMALLY LOAD-COUPLED / NON-DETERMINISTIC UNDER THE CURRENT FIXED-TIME TEST SEMANTICS.
Not addressed by: a load precondition, retries, fewer workers, or any tree change (all refused).

## SWU-PX-03 — AUTHORITATIVE SUCCESSOR WORK UNIT (NOT implemented in the frozen pass)
Purpose: replace the fixed wall-clock readiness assumption with readiness-based synchronization while
preserving the intended technical-failure semantics (the worker loop survives a database outage, keeps
trying pass after pass, and stops gracefully with returncode 0 and "stopped").
Scope: product/test tree (the test, and the worker only if an observable readiness signal must be added);
a new frozen checkpoint afterwards; then re-derivation of the ORANGE partition for this node.
Required falsifiers:
1. delayed subprocess startup (start-up artificially delayed beyond 2.5 s) -> the test still proves the
   semantics, no false failure;
2. high CPU contention -> same;
3. DB contention where relevant (the scenario is an unreachable DB; prove the result is independent of
   load on the proof cluster);
4. signal handler not yet installed -> SIGTERM is never sent before readiness (impossible by construction);
5. readiness reached -> graceful stop after readiness asserts returncode 0 and "stopped";
6. readiness never reached -> bounded failure at an upper-bound timeout (a fail, never a hang);
7. graceful stop after readiness -> ">= 2 failing passes" (kept trying) still asserted, not weakened;
8. bounded failure when readiness cannot be established -> clear diagnostic, no retry.
Exit proof: the node's outcome is invariant across serial, governed 4-worker parallel and loaded-machine
execution (repeated runs), after which it may be re-evaluated for the xdist partition.

### SF-PX-03 — addendum after the FINAL ENVIRONMENT CLOSURE (2026-10-01 01:58–02:44, guard 1.2.0)
Full serial reference: the node PASSED (2.69 s), immediately preceded by its sibling
`test_worker_once_reports_an_unavailable_database_and_fails_the_pass` (1.15 s; warm worker start).
4-node serial partition (no other lane's suite running): the node FAILED again (-15 after 2.51 s);
there it is the first worker start of its window (the sibling runs in the xdist partition).
=> The coupling is to EXECUTION CONTEXT (cold vs warm subprocess start-up, partition placement) as well as
machine load. Status unchanged: FORMALLY OPEN, successor SWU-PX-03. No retry.

## TF-PX-01 — TOOLING FINDING: provision_proof_dbs.sh contacts the maintenance database (still real)
`provision_proof_dbs.sh create-serial` checks for and creates the serial proof database through
`psql ... -d postgres` / `createdb` (the `postgres` maintenance database). It was NOT part of the final
closure chain and did not execute there; it ran once, earlier, under explicit authority to create
`nquiry_proof_serial_test`. Since the boundary "never query non-proof databases" every chain script reads
cluster catalogs through a PROOF database only (ORANGE_CATALOG_DB). Successor: either keep provisioning as an
explicitly authorized, separately recorded exception (CREATE DATABASE needs some existing database to connect
to), or route it through an existing proof database. Not changed in this lineage creation.

## TF-PX-02 — TOOLING DEFECT (repaired in the lineage): px1_falsifiers.sh not re-run after guard 1.1.0 (cadence miss)
Found by the lineage re-proof (`evidence/lineage_reproof/px1_falsifiers*.log`): guard >= 1.1.0 added the
`nquiry_orange_workerdb` plugin, which refuses any xdist worker outside the governed lane. px1_falsifiers.sh
was not re-run after that change. Consequences:
- P8 (`-n 2` DB-free apps/api TestClient tests) failed with `WorkerBindingRefused` (exit 1) instead of 6 passed;
- N6 (worker-only poison) still exited 1, but AMBIGUOUSLY: the refusal could come from the binding plugin
  rather than the import-origin guard it is meant to prove.
Repair (local radius, lineage only): P8 and N6 run under the governed lane (ORANGE_XDIST_LANE=1 +
ORANGE_DB_BASE; workers bind to nquiry_proof_gw{0,1}_test); N6 now asserts the import-origin guard's message
and absence of the binding message. Re-run (`evidence/lineage_reproof/px1_falsifiers_repaired.log`):
P8 6 passed exit 0; N6 2 errors, refused_by_import_origin_guard=2 refused_by_binding=0, exit 1; all other
P/N/CONTROL results unchanged. Impact on closure evidence: none. The final-closure runs exercised the guard
under the lane (pre/post_guard, IMPORT_ORIGIN_GUARD_VALID) and the binding proof separately; the pre-1.1.0
px1 logs remain valid for guard 1.0.0 as recorded. The ORIGINAL px1_falsifiers.sh (unversioned location) is
left unrepaired and superseded by the lineage copy.

## TF-PX-03 — EMPTY_IGNORED_DIRECTORY_NOT_CAPTURED_BY_GIT_OR_CONTENT_HASH (Human Authority classification, 2026-10-01; recorded 2026-10-03)
The frozen PCPG-5 worktree `worktrees/orange-proof-infra` contains an empty `pycache/` directory skeleton
(0 files), created at 01:09:28 by the xdist start of `parallel_run1`. Neither `git status --ignored` nor the
file-content hash sees it. No effect on product semantics, the frozen git tree, the recorded content hash
or the PCPG-5 2238/2239 claim. "Filesystem pristine at directory level" is NOT claimed for that historical
worktree state. Left untouched by decision. The published lineage commit is not amended.

## TF-PX-04 — TOOLING DEFECT (proof-lineage infrastructure, NOT a product failure): the chain driver refuses its own pre phase
`final_closure.sh` (lineage c9f276fc) redirects `serial_baseline.sh pre` (and `parallel_proof.sh pre`) into
`$S/pre.log` / `$R/pre.log`. The shell creates that file inside the evidence directory before the pre phase
runs, so the pre phase's evidence-safety refusal (introduced by this lineage's refactor) finds the directory
non-empty and refuses. The driver has no `set -e` and kept running in the broken state (it started a serial run
without a pre state). The lineage re-proof never ran the chain end to end, so the defect was not caught there.
Found by the first SWU-PX-03 successor run (2026-10-01 14:09). Handling: the orphaned run was terminated by
PID, proof DBs were verified clean with no residual cluster objects, and the attempt is preserved
(`successors/SWU-PX-03/evidence/final_closure_ABORTED_TF-PX-04/`).
Repair (successor binding only): the pre log goes to a sibling file and moves in afterwards, and the chain
STOPS when a pre phase is refused. The lineage's own PCPG-5-bound `final_closure.sh` still carries the defect
(not changed by this record).

## TF-PX-05 — TOOLING DEFECT (proof-lineage infrastructure, NOT a product failure): PYC not exported into the governed subshell
`parallel_proof.sh` runs the xdist and serial partitions as `bash -c "... $(declare -f H); H ..."`. The
serialized function `H` sets `PYTHONPYCACHEPREFIX=$PYC`, but `PYC` was not exported into that subshell.
Effect: `PYTHONPYCACHEPREFIX` resolved EMPTY (no prefix), and the xdist workers wrote `.pyc` files into the
successor tree (44 ignored `__pycache__/` directories). TREE_UNCHANGED failed, and so did PARALLEL_PROOF.
Introduced by this lineage's refactor (`$P/pycache` -> `$PYC`).
Repair: `export PYC` right after its definition, so the governed subshell uses the authorized proof prefix
(`.venv-proof313-orange-swu/orange-proof/pycache`). Verified directly (serialized function without export: empty;
with export: the prefix).
Proof: the failed run is preserved (`successors/SWU-PX-03/evidence/final_closure/parallel/`). The successor tree was
restored to the exact tagged state: only the 44 git-ignored directories, containing only `.pyc`, were removed,
leaving 0 entries and content `f247dc32…`. The governed partition phase was re-run against the unchanged serial
reference (`.../parallel_r2_after_TF-PX-05/`): PARALLEL_PROOF::PASS, post-run tree 0 entries,
TREE_UNCHANGED::PASS. The lineage's own PCPG-5-bound `parallel_proof.sh` still carries the defect (not changed
by this record).
HISTORICAL DISCLOSURE (PCPG-5, not a rewrite): in the ORIGINAL PCPG-5 `parallel_proof.sh` the same serialized `H`
referenced `$P/pycache` with `P` unset in the subshell. The prefix was therefore `/pycache` (unwritable).
The PCPG-5 governed partitions did NOT use the recorded ORANGE bytecode prefix: bytecode caching was
effectively disabled (every partition import was cold), and nothing was written into the frozen tree. No
PCPG-5 outcome or evidence changes. The published PCPG-5 proof is not rewritten.

## SF-PX-03 — successor closure (addendum; the PCPG-5 entry above stays as recorded)
SF-PX-03 = CLOSED for `checkpoint-SWU-PX-03` (`944f1ae`, tag object `b331fb1d`). The formerly failing node passed in
the successor's serial reference and in its governed serial partition. Successor product/test equivalence
2252 / 2252 (2248 governed parallel + 4 governed serial). All 2239 PCPG-5 nodes preserved, plus the 13 SWU-PX-03
falsifiers. `checkpoint-PFC-PCPG-5` remains permanently 2238 / 2239 with SF-PX-03 OPEN.
Record: `successors/SWU-PX-03/PROOF_RECORD.md`.

## TF-PX-04 / TF-PX-05 — CLOSED in the canonical ORANGE lineage (Work Unit ORANGE-TF-PX-04-05, 2026-10-03)
Base `c4ceec2`. The discovery records above and all failed evidence are preserved unchanged. The repairs are
the ones already proven in the SWU-PX-03 successor binding, materialized code-identically (only the trailing
comments say "canonical"):
- TF-PX-04 (`final_closure.sh`): each pre phase logs to a sibling file outside the directory it requires
  empty, which is moved in afterwards; the chain STOPS when a pre phase is refused. 2 lines -> 4 lines.
- TF-PX-05 (`parallel_proof.sh`): `export PYC` right after its definition, so the governed `bash -c` subshell
  (H serialized via declare -f) uses the authorized proof prefix. 1 line added.
Proof (`tooling_falsifiers_tf_px_04_05.sh`, evidence `evidence/tf_px_04_05/`), narrow radius, no product test run:
- T04a: the chain's own serial pre invocation (lines taken verbatim from `final_closure.sh`) runs the real
  `serial_baseline.sh pre` (read-only catalog, guard, DB-free collect-only of the frozen PCPG-5 tree, 2239) and is
  not refused; T04b: a refused pre phase stops the chain, existing evidence untouched;
- T05a: inside the governed subshell `PYTHONPYCACHEPREFIX` and `sys.pycache_prefix` = the authorized prefix
  `.venv-proof313-orange/orange-proof/pycache`; T05b: real xdist workers (synthetic tree, no product code)
  write 0 `.pyc` into the tree and their bytecode into the prefix;
- 12/12 checks PASS on the canonical lineage; mutants killed 3/3 (M04 old redirect: refused, no collection, no
  stop; M04b stop guard removed: chain continues; M05 export removed: empty prefix, `sys.pycache_prefix=None`, 3
  `.pyc` in the tree);
- existing lineage proofs still green: canonical ids 25/25, partition 24/24, aggregation 22/22, order PASS, all
  10 scripts pass `bash -n`;
- before/after snapshot identical: frozen PCPG-5 worktree (incl. directory listing), SWU-PX-03 worktree, both
  checkpoint tags, the lineage's committed evidence, the PCPG-5 originals, both proof environments.
TF-PX-04 = CLOSED in canonical ORANGE lineage. TF-PX-05 = CLOSED in canonical ORANGE lineage.
Not re-proven at full radius: no complete ORANGE chain was run after the repair (not required at this radius).
The next full ORANGE run is the first end-to-end use of the repaired canonical chain.

## TF-PX-06 — TOOLING DEFECT (proof-lineage infrastructure, NOT a product failure): spurious PROOF_END from a heartbeat fork race
Found 2026-10-03 by falsifier E10 of Work Unit FINAL_VERDICT_EXIT_STATUS. Present in `progress.sh` since the
structured verbose + heartbeat commit `64e9113`. When a stage ends right after it starts, `prog_end` kills the
just-forked background heartbeat before bash has reset the inherited EXIT trap in that child. The child then
ran the chain's EXIT handler and emitted a false `PROOF_END verdict=FAIL reason=chain_exited_before_final_verdict`
mid-run. Reproduced with the base helper: 1 of 10 zero-duration stages; 1–2 of 30 two-stage zero-duration
chains (evidence `exit_status_v1_FAIL_*`, `exit_status/canonical.log` info line). It never changed the chain
process's own exit status (only the child's), but it broke "PROOF_END once and last" in the event stream. The real
chain's stages all run real commands, so it was unlikely there, but possible.
Repair (same relation as the exit-status contract): `prog_init` records the chain's own `BASHPID`, and the EXIT
handler returns at once in any other process: no event, no exit-status change. Falsifier E10b (100 zero-duration
two-stage chains, PROOF_END exactly once) and mutant MX7 (guard removed: killed) prove it.
TF-PX-06 = CLOSED in canonical ORANGE lineage.

## TF-PX-07 — TOOLING DEFECT (proof-lineage infrastructure, NOT a product failure): stage runners exit 0 on a failed governed proof
Found 2026-10-04 by reconstructing the runner contracts (Work Unit STAGE_EXIT_STATUS). Present since the first
lineage commit. `serial_baseline.sh run` and `parallel_proof.sh xdist | serial` wrote the governed pytest exit code
to `*_exit_code.txt` and printed it, but ended on an unrelated `tail -1`, so the process status was always 0. It
never produced a false proof verdict: every canonical consumer (`final_closure.sh` via `prog_exitfile`,
`analyze_serial.py` EXIT_CODE_0, `run_aggregate.py` / `aggregate.py`) reads the file. It did misreport to any
standalone caller that trusts the process status. Repair: process status follows the recorded code (0 -> 0, anything
else -> 1), five added lines; proof and claim ceiling in `ORANGE_PROOF_STATUS.md` §15.
TF-PX-07 = CLOSED in canonical ORANGE lineage.

## TF-PX-08 — TOOLING FINDING (kept unchanged by Human Authority decision, 2026-10-04): the `pre` / `post` process status is not a verdict
Found 2026-10-04 in the same reconstruction. `pre` exits 1 only when it refuses (non-empty directory, HEAD not
frozen); otherwise it ends on an `echo` and exits 0 even if the guard, the proof-DB verification or the collection
failed. `post` exits with the status of its last `grep`; measured: a `post` whose verdict line is
`PROOF_DB_PRECONDITIONS::FAIL` exits 0 (`evidence/stage_exit_status/canonical.log`, info lines). No false proof
verdict follows from it: the chain requires the verdict lines (`prog_verdicts`, absent = MISSING = FAIL) and the
analyzers re-check guard, proof DBs, tree and collection count.
Not repaired on purpose: unlike `run` / `xdist` / `serial`, these phases have no recorded single truth to follow, and
the chain DOES consume the `pre` status (`[ $rc -eq 0 ] || CHAIN STOPPED`). Making `pre` exit nonzero on a FAIL
verdict would stop the canonical chain early instead of completing its evidence, which is a change of canonical
chain semantics. Options were: (a) keep (status = refusal only; documented in the README), or (b) authorize a
verdict-following `pre` / `post` status together with the resulting early chain stop.
Human Authority decision 2026-10-04: (a). TF-PX-08 stays unchanged and documented: the `pre` / `post` process
status means refusal only and is never a verdict; their `NAME::PASS|FAIL` lines are the truth.
TF-PX-08 = DOCUMENTED, NOT REPAIRED (by decision).

## TF-PX-09 — TOOLING DEFECT (proof-lineage infrastructure): a falsifier persisted the proof process environment as evidence
Found 2026-10-05 when GitHub Push Protection rejected the publication of the unpublished local commit dcf4a82. To
prove that the SFE-PEO/1 observer leaves the child's environment unchanged, falsifier O3e wrote the child's full
`env` output to `o3_env_obs.out` / `o3_env_dir.out`. The operator's shell profile exports credentials into every
process, so their values were persisted and committed. First broken relation: evidence generation ("prove equality
by persisting the values"); there was also no check between evidence persistence and commit. The observer itself
was not involved. Credentials in a consumer's environment are legitimate and stay untouched.
Repair (provider- and name-neutral; `ORANGE_PROOF_STATUS.md` §16): names + digest instead of values; the harness
runs under `env -i` with an allowlist and a fixture credential; `evidence_secret_gate.py` before every commit, over
the files to be versioned and over reachable history. dcf4a82 was withdrawn and its objects deleted; never
published.
TF-PX-09 = CLOSED in canonical ORANGE lineage.

## TF-PX-10 — TOOLING FINDING (OPEN, needs Human Authority): governed proof children inherit ambient credentials
Found 2026-10-05 in the same reconstruction. `serial_baseline.sh` and `parallel_proof.sh` scrub a fixed list of
variables before running pytest on the proof target (a denylist), so every other ambient variable, including
application and provider credentials exported by the operator's shell, reaches the governed tests. No evidence of
this lineage persists such a value (gate over the versioned tree and the reachable history: PASS), and no effect on
a proof outcome is known. Not changed: replacing the denylist by an allowlist changes the proof environment of the
canonical chain, which is a global-invariant change and needs Human Authority and a fresh chain.

