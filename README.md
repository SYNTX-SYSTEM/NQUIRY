# ORANGE proof infrastructure lineage

**Role:** proof executor / verifier. **Not** the proof target and never part of it.

```
FROZEN PRODUCT TREE              -> proof target   (checkpoint-PFC-PCPG-5 @ e0a6b3b, worktrees/orange-proof-infra)
ORANGE PROOF INFRASTRUCTURE      -> proof executor / verifier   (this orphan branch: orange-proof-lineage)
```

The exact target, environment and tool version this lineage proves are recorded in `TARGET.json`. A
commit of this lineage does not change the target identity it claims: the target is read-only, external,
and re-verified (HEAD, tag, content hash) by every proof run.

## Current claim (do not overstate)

- PROOF INFRASTRUCTURE: CLOSED for the governed PCPG-5 proof lane, subject to the recorded claim ceiling.
- PRODUCT / TEST EQUIVALENCE: **2238 / 2239** equivalent.
- OPEN: SF-PX-03 FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT (successor SWU-PX-03).
- Claim ceiling: 2235 nodes under governed 4-worker parallel execution + 4 nodes under governed serial
  execution = complete 2239-node coverage. Never "2239 parallel", never "2239 equivalent".
- Performance (same environment): 1958.6 s serial vs 768.2 s governed = 2.55x, PROVISIONAL.

Full record: `evidence/ORANGE_PROOF_STATUS.md`; findings / successors: `evidence/SUCCESSOR_FINDINGS.md`.

## Layout

| Path | Content |
|---|---|
| `guard/` | proof-owned pytest plugins (distribution `nquiry-orange-guard` 1.2.0): import-origin guard, worker <-> DB binding (+ order observation) |
| `px1_falsifiers.sh`, `negative-fixtures/` | environment / import-origin falsifiers and their adversarial fixtures |
| `env_manifest.py`, `provenance_manifest.py`, `equivalence-pins.txt` | environment manifest and dependency provenance; the exact historical fastapi/starlette pair |
| `provision_proof_dbs.sh`, `verify_proof_dbs.py` | proof DB provisioning (canonical NQUIRY sequence) and read-only verification (head, fingerprint, clean, allowlist, connections) |
| `serial_partition_selectors.txt`, `partition.sh`, `partition_proof.py` | execution decomposition (4 serial / 2235 xdist) and its proof |
| `canonical_ids.py`, `canonical_ids_proof.py` | evidence-only canonical identity for the volatile uuid node ids |
| `serial_baseline.sh`, `analyze_serial.py` | serial reference run + analysis |
| `parallel_proof.sh`, `binding_proof.sh`, `order_proof.py`, `observer.sh` | governed parallel execution, binding falsifiers, scheduling-order proof, cluster-object observer |
| `aggregate.py`, `aggregate_proof.py`, `run_aggregate.py`, `inertness_compare.py` | fail-closed aggregation, per-node equivalence, instrumentation inertness |
| `final_closure.sh` | the complete closure chain under one environment |
| `progress.sh`, `progress_falsifiers.sh` | structured progress + heartbeat for the chain (observability only; liveness, never verdicts) and its falsifiers |
| `tooling_falsifiers_tf_px_04_05.sh` | falsifiers for the chain's own pre phase (TF-PX-04) and the governed-subshell bytecode prefix (TF-PX-05) |
| `timing_stress_probe.sh` | B3 timing probe (its earlier "closure" was falsified by the real run; kept as provenance) |
| `evidence/` | curated evidence + full final-closure evidence; `EVIDENCE_MANIFEST.tsv` hashes every original file |
| `evidence/lineage_reproof/` | local re-proof of the scripts from this lineage (raw outputs > 100 KB hash-recorded in `RAW_EXCLUDED.tsv`, not versioned) |

## Reproducing the environment (not executed by this lineage; recorded procedure)

```
uv venv --python <uv CPython 3.13.15> --no-project .venv-proof313-orange
uv pip install --python .venv-proof313-orange/bin/python -r <target>/pyproject.toml --extra dev \
    pytest-xdist "httpx==0.28.1" -c evidence/constraints-from-venv-proof313.txt
uv pip install --python .venv-proof313-orange/bin/python -r equivalence-pins.txt
uv pip install --python .venv-proof313-orange/bin/python ./guard
printf '%s\n' <target>/packages <target>/apps/api/src <target>/apps/worker/src <target>/scripts \
    > .venv-proof313-orange/lib/python3.13/site-packages/nquiry_orange_tree.pth
```
Then verify with `env_manifest.py` against `TARGET.json`. NOTE: the guard has the target and env paths
compiled in (`ORANGE_ROOT`, `ENV_PREFIX`); that binding is deliberate (fail-closed import origin).

## Running (evidence is never overwritten)

Drivers write only to NEW directories (`ORANGE_SERIAL_DIR`, `ORANGE_PARALLEL_DIR`, `ORANGE_CLOSURE_DIR`, ...;
`pre` refuses a non-empty directory). Catalog / observer access goes through PROOF databases only
(`ORANGE_CATALOG_DB`). Proof DBs: `nquiry_proof_serial_test`, `nquiry_proof_gw{0..3}_test` on 127.0.0.1:15432.
Local-dev-only credentials (`nquiry_local_dev_only`) follow the repository's existing local convention.

## Provenance kept on purpose

Disclosed deviations and the tooling defects found during the pass are recorded, not normalized away
(`evidence/ORANGE_PROOF_STATUS.md` §7–§9, `evidence/SUCCESSOR_FINDINGS.md`).

## Successor proofs

`successors/<WU>/` records ORANGE proofs against product successor checkpoints, each with its own target identity
(`SUCCESSOR_TARGET.json`), the exact successor binding of this tooling (`SUCCESSOR_BINDING.diff`), evidence
with a hash manifest, and a proof record. The PCPG-5 record above is never rewritten by a successor.
- `successors/SWU-PX-03/`: `checkpoint-SWU-PX-03` (944f1ae), 2252/2252, SF-PX-03 CLOSED for the successor.
