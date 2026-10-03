#!/usr/bin/env bash
# ORANGE FINAL ENVIRONMENT CLOSURE (Human Authority 2026-10-01). ONE proof environment (guard 1.2.0)
# for BOTH the serial reference and the governed parallel/serial partition execution.
# FROZEN TREE -> ENV -> MANIFEST -> COLLECTION -> SERIAL REFERENCE -> PARTITION EXECUTION ->
# AGGREGATION -> EQUIVALENCE -> CLEANUP -> TREE/ENV/DB RECONSTRUCTION.
# No retries, no dependency change, no non-proof database contact.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
F=${ORANGE_CLOSURE_DIR:-$P/evidence/final_closure_$(date +%Y%m%dT%H%M%S)}
[ -e "$F" ] && { echo "REFUSED: $F exists (evidence is never overwritten)"; exit 1; }
mkdir -p "$F"
export ORANGE_BYTECODE_ENV="PYTHONPYCACHEPREFIX=$PYC"
PY() { env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 "$V/bin/python" "$@"; }
echo "== final closure started $(date -Iseconds); load $(cut -d' ' -f1-3 /proc/loadavg)"

# ---- 1. SERIAL REFERENCE under guard 1.2.0 (race clones TEMPLATE serial db -> catalog/observer via gw0)
S=$F/serial_ref; mkdir -p "$S"
export ORANGE_SERIAL_DIR=$S ORANGE_CATALOG_DB=nquiry_proof_gw0_test
bash "$P/serial_baseline.sh" pre > "$F/serial_ref.pre.log" 2>&1; rc=$?; mv "$F/serial_ref.pre.log" "$S/pre.log"; cat "$S/pre.log"
[ $rc -eq 0 ] || { echo "CHAIN STOPPED: serial pre refused (rc=$rc)"; exit 1; }  # TF-PX-04: pre log written outside the dir the pre phase requires empty; chain stops on refusal
grep -E "test_direct_write.py|test_http_dispatch_real_connection_lifecycle.py" "$S/collected_nodeids.txt" > "$S/declared_skips.txt"
bash "$P/observer.sh" nquiry_proof_gw0_test "$S/observed_cluster_objects.log" "$S/observer.stop" &
OBS=$!
date +%s.%N > "$S/t0"; bash "$P/serial_baseline.sh" run; date +%s.%N > "$S/t1"
touch "$S/observer.stop"; wait $OBS
bash "$P/serial_baseline.sh" post > "$S/post.log" 2>&1; cat "$S/post.log"
(cd "$P" && PY analyze_serial.py) > "$S/analysis.log" 2>&1; grep -E "::" "$S/analysis.log"

# ---- 2. GOVERNED PARTITION EXECUTION (xdist clones TEMPLATE gwN -> catalog/observer via serial db)
R=$F/parallel; mkdir -p "$R"
export ORANGE_PARALLEL_DIR=$R ORANGE_CATALOG_DB=nquiry_proof_serial_test
unset ORANGE_SERIAL_DIR
bash "$P/parallel_proof.sh" pre > "$F/parallel.pre.log" 2>&1; rc=$?; mv "$F/parallel.pre.log" "$R/pre.log"; cat "$R/pre.log"
[ $rc -eq 0 ] || { echo "CHAIN STOPPED: parallel pre refused (rc=$rc)"; exit 1; }  # TF-PX-04: pre log written outside the dir the pre phase requires empty; chain stops on refusal
(cd "$P" && ORANGE_PARTITION_DIR=$R/partition PY partition_proof.py) > "$R/partition_proof.log" 2>&1; tail -1 "$R/partition_proof.log"
bash "$P/observer.sh" nquiry_proof_serial_test "$R/observed_cluster_objects.log" "$R/observer.stop" &
OBS=$!
bash "$P/parallel_proof.sh" xdist
bash "$P/parallel_proof.sh" serial
touch "$R/observer.stop"; wait $OBS
bash "$P/parallel_proof.sh" post > "$R/post.log" 2>&1; cat "$R/post.log"

# ---- 3. AGGREGATION + EQUIVALENCE (reference = the NEW serial reference, same environment)
(cd "$P" && ORANGE_REFERENCE_DIR=$S PY run_aggregate.py "$R") > "$R/aggregate.log" 2>&1; cat "$R/aggregate.log"
(cd "$P" && PY order_proof.py "$R/binding" "$R/partition/xdist_nodeids.txt") > "$R/order_proof.log" 2>&1; tail -1 "$R/order_proof.log"
(cd "$P" && PY inertness_compare.py "$S" "${ORANGE_INERTNESS_REFERENCE:-$P/evidence/final_closure/serial_ref}") > "$F/inertness.log" 2>&1; cat "$F/inertness.log"
echo "== final closure finished $(date -Iseconds); load $(cut -d' ' -f1-3 /proc/loadavg)"
