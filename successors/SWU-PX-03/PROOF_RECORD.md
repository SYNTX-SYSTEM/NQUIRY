# SWU-PX-03 — ORANGE successor proof record

Human Authority "SFE::ORANGE MODE = FINAL_PROOF_RECORDING" (2026-10-03). Records the completed final ORANGE
proof against `checkpoint-SWU-PX-03`. Nothing here was re-run for this record.

## 1. Identity

| Item | Value |
|---|---|
| Checkpoint | `checkpoint-SWU-PX-03`, tag object `b331fb1db08fc3126490f5916989878104e389a8` (signed, good signature) |
| Commit / tree | `944f1ae94f027b400f07dbdb07a6b9f018395a33` / `3b900955bf06ffa4d89adcdfbcf9305eb912c900`, content sha256 `f247dc32…` |
| Parent | `checkpoint-PFC-PCPG-5` `e0a6b3b`. Delta = 5 files (worker readiness line, consumer, support module, 13 falsifiers, field report) |
| Environment | `.venv-proof313-orange-swu`: the PCPG-5 proof environment's 48 third-party distributions (freeze-identical) + guard `1.2.0+swupx03`, manifest `9b0bc9a9…` identical in every capture |
| Tooling | successor binding of this lineage at `c9f276fc`. Parameters (target, environment, frozen commit/tag, counts 2252 = 2248 + 4) plus the recorded repairs TF-PX-04 and TF-PX-05 and the successor preservation comparison. Full diff: `SUCCESSOR_BINDING.diff` |

## 2. Final result

```text
PARALLEL_PROOF::PASS
ORDER_PROOF::PASS
SUCCESSOR_PRESERVES_PCPG5_SERIAL_OUTCOMES::PASS
```

| Phase | Result | Evidence |
|---|---|---|
| Environment falsifiers (px1) | P1–P9 / N1–N8 / CONTROL as in PCPG-5; N6 refused by the import-origin guard (2/0) | `evidence/px1_falsifiers.log` |
| Worker <-> DB binding | P1, N1–N7, identity function and map all PASS | `evidence/binding_proof.log`, `evidence/binding/` |
| Serial reference (2252) | 2250 passed / 2 declared skips / 0 failed; 15/15 criteria PASS; 1785.0 s | `evidence/final_closure/serial_ref/` |
| Partition proof | 24/24 | `.../parallel_r2_after_TF-PX-05/partition_proof.log` |
| Governed execution | xdist 2248: 2246 passed + 2 declared skips (exit 0); serial 4: 4 passed (exit 0) | `.../parallel_r2_after_TF-PX-05/` |
| Aggregation / equivalence | 2252 / 2252 vs the same-environment serial reference | `.../parallel_r2_after_TF-PX-05/aggregate.log`, `aggregated_outcomes.tsv` |
| Tree / env / DBs / cluster objects | tree 0 entries before and after, content `f247dc32…`; env unchanged; proof DBs clean and unconnected; 13 race DBs observed and dropped; 0 residue | `.../parallel_r2_after_TF-PX-05/result.json` |
| Successor preservation | all 2239 PCPG-5 nodes keep their outcomes (no exemption, including the SF-PX-03 node); exactly the 13 declared falsifiers added, all passed; 5/5 falsifiers detect | `.../parallel_r2_after_TF-PX-05/inertness.log` |

**Claim ceiling (do not strengthen):**
SWU-PX-03 = SUCCESSOR PRODUCT/TEST EQUIVALENCE PROVEN = 2252/2252 COMPLETE COVERAGE = 2248 GOVERNED PARALLEL
+ 4 GOVERNED SERIAL = SF-PX-03 CLOSED FOR SUCCESSOR = PCPG-5 HISTORICAL RECORD PRESERVED = PERFORMANCE
SPEEDUP / WALL-CLOCK STILL PROVISIONAL. Never "2252 parallel". Valid only for `checkpoint-SWU-PX-03`.

## 3. SF-PX-03

**CLOSED for `checkpoint-SWU-PX-03`.** The formerly failing node
`tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully`
passed in the serial reference and in the governed serial partition. The governed serial partition is the
exact place where it failed for PCPG-5.
**Historical, permanent:** `checkpoint-PFC-PCPG-5` = 2238 / 2239, SF-PX-03 OPEN. Its evidence is not rewritten.

## 4. Run history (all preserved)

1. `evidence/final_closure_ABORTED_TF-PX-04/` + `closure_run_ABORTED_TF-PX-04.log`: the chain refused its own
   serial pre phase (TF-PX-04). The orphaned serial run was terminated by PID. Proof DBs were verified clean,
   with no cluster objects, afterwards.
2. `evidence/final_closure/serial_ref/` + `evidence/final_closure/parallel/` + `closure_run.log`: serial reference PASS.
   Partitions 2246+2 / 4 and AGGREGATION_AND_EQUIVALENCE::PASS, but **PARALLEL_PROOF::FAIL** on TREE_UNCHANGED:
   44 ignored `__pycache__/` directories were written into the successor tree (TF-PX-05). Kept as the failed run.
3. Successor tree restored to the exact tagged state: only those 44 git-ignored directories, containing only
   `.pyc`, were removed, leaving 0 entries and content `f247dc32…`.
4. `evidence/final_closure/parallel_r2_after_TF-PX-05/` + `rerun_after_TF-PX-05.log`: the governed partition phase
   (final_closure steps 2–3, verbatim, `parallel_rerun.sh`) re-run against the unchanged serial reference. Result:
   **PARALLEL_PROOF::PASS**, TREE_UNCHANGED::PASS, post-run tree 0 entries.

## 5. Performance

Governed wall clock 637.2 s (xdist 632.5 s + serial 4.8 s) vs the same-environment serial reference 1785.0 s =
2.80x. **SINGLE MEASUREMENT. PROVISIONAL PERFORMANCE EVIDENCE.** Not a stable performance claim. (The failed
first partition run measured 714.9 s with in-tree bytecode writes.)

## 6. Process cleanliness

After the final run: no worker process, no load process, no proof-chain process, no foreign pytest. The earlier
monitor `tail` processes have ended.

## 7. SWU-PX-03 product-field proof (before the ORANGE run)

`local-proof/` (curated): local falsifiers 13/13; mutation 5/5 killed; affected suites 428 passed / 2 declared
skips / 0 failed; load contention NEW 0/48 failures vs a verbatim PCPG-5 consumer witness 38/48; readiness
under 2 x CPU + cold start 8.8–15.2 s (at least 44.8 s headroom to the 60 s fail bound). The field report is
`docs/implementation/field-reports/PX/WU-SWU-PX-03.md` in the checkpoint (as committed; not changed by this
record).

## 8. Evidence policy

`EVIDENCE_MANIFEST.tsv` hashes every original file (ORANGE successor evidence and local proof). Committed: all
final-closure evidence (the aborted attempt, the failed run and the passing re-run), all other files <= 100 KB.
Excluded, hash-recorded only: 2 raw files > 100 KB (`binding/N2_five_workers.txt`,
`px1/collect_orange_env.txt`) and 3 `observer.stop` runtime markers. Originals stay at
`.venv-proof313-orange-swu/orange-proof/evidence/` and `.venv-swu-px-03/swu-proof/evidence/`.
