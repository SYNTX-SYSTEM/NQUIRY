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
. "$P/progress.sh"  # structured progress + heartbeat: observability only (see progress.sh)
prog_init canonical-orange "lineage=$(git -C "$P" rev-parse --short HEAD 2>/dev/null || echo unknown)" "run=$(basename "$F")"

# ---- 1. SERIAL REFERENCE under guard 1.2.0 (race clones TEMPLATE serial db -> catalog/observer via gw0)
S=$F/serial_ref; mkdir -p "$S"
export ORANGE_SERIAL_DIR=$S ORANGE_CATALOG_DB=nquiry_proof_gw0_test
prog_begin serial_pre
bash "$P/serial_baseline.sh" pre > "$F/serial_ref.pre.log" 2>&1; rc=$?; mv "$F/serial_ref.pre.log" "$S/pre.log"; cat "$S/pre.log"
prog_end serial_pre "$rc"
prog_verdicts serial_pre "$S/pre.log" ORANGE_IMPORT_ORIGIN PROOF_DB_PRECONDITIONS
[ $rc -eq 0 ] || { echo "CHAIN STOPPED: serial pre refused (rc=$rc)"; exit 1; }  # TF-PX-04: pre log written outside the dir the pre phase requires empty; chain stops on refusal
grep -E "test_direct_write.py|test_http_dispatch_real_connection_lifecycle.py" "$S/collected_nodeids.txt" > "$S/declared_skips.txt"
bash "$P/observer.sh" nquiry_proof_gw0_test "$S/observed_cluster_objects.log" "$S/observer.stop" &
OBS=$!
prog_begin serial_reference "$S/run.log"
date +%s.%N > "$S/t0"; bash "$P/serial_baseline.sh" run; date +%s.%N > "$S/t1"
prog_end serial_reference "$(prog_exitfile "$S/run_exit_code.txt")"
touch "$S/observer.stop"; wait $OBS
prog_event CLEANUP phase=serial observer=stopped
prog_begin serial_post
bash "$P/serial_baseline.sh" post > "$S/post.log" 2>&1; cat "$S/post.log"
prog_end serial_post unobserved
prog_begin serial_analysis
(cd "$P" && PY analyze_serial.py) > "$S/analysis.log" 2>&1; grep -E "::" "$S/analysis.log"
prog_end serial_analysis unobserved
prog_verdicts serial_analysis "$S/analysis.log" SERIAL_BASELINE

# ---- 2. GOVERNED PARTITION EXECUTION (xdist clones TEMPLATE gwN -> catalog/observer via serial db)
R=$F/parallel; mkdir -p "$R"
export ORANGE_PARALLEL_DIR=$R ORANGE_CATALOG_DB=nquiry_proof_serial_test
unset ORANGE_SERIAL_DIR
prog_begin parallel_pre
bash "$P/parallel_proof.sh" pre > "$F/parallel.pre.log" 2>&1; rc=$?; mv "$F/parallel.pre.log" "$R/pre.log"; cat "$R/pre.log"
prog_end parallel_pre "$rc"
prog_verdicts parallel_pre "$R/pre.log" ORANGE_IMPORT_ORIGIN PROOF_DB_PRECONDITIONS
[ $rc -eq 0 ] || { echo "CHAIN STOPPED: parallel pre refused (rc=$rc)"; exit 1; }  # TF-PX-04: pre log written outside the dir the pre phase requires empty; chain stops on refusal
prog_begin partition_proof
(cd "$P" && ORANGE_PARTITION_DIR=$R/partition PY partition_proof.py) > "$R/partition_proof.log" 2>&1; tail -1 "$R/partition_proof.log"
prog_end partition_proof unobserved
prog_verdicts partition_proof "$R/partition_proof.log" PARTITION_PROOF
bash "$P/observer.sh" nquiry_proof_serial_test "$R/observed_cluster_objects.log" "$R/observer.stop" &
OBS=$!
prog_begin xdist_partition "$R/xdist_run.log"
bash "$P/parallel_proof.sh" xdist
prog_end xdist_partition "$(prog_exitfile "$R/xdist_exit_code.txt")"
prog_begin serial_partition "$R/serial_run.log"
bash "$P/parallel_proof.sh" serial
prog_end serial_partition "$(prog_exitfile "$R/serial_exit_code.txt")"
touch "$R/observer.stop"; wait $OBS
prog_event CLEANUP phase=parallel observer=stopped
prog_begin parallel_post
bash "$P/parallel_proof.sh" post > "$R/post.log" 2>&1; cat "$R/post.log"
prog_end parallel_post unobserved

# ---- 3. AGGREGATION + EQUIVALENCE (reference = the NEW serial reference, same environment)
prog_begin aggregation
(cd "$P" && ORANGE_REFERENCE_DIR=$S PY run_aggregate.py "$R") > "$R/aggregate.log" 2>&1; cat "$R/aggregate.log"
prog_end aggregation unobserved
prog_verdicts aggregation "$R/aggregate.log" AGGREGATION_AND_EQUIVALENCE TREE_UNCHANGED ENV_MANIFEST_UNCHANGED MIGRATION_HEADS_AND_FINGERPRINT_UNCHANGED PROOF_DBS_CLEAN_AND_UNCONNECTED_AFTER NO_RESIDUAL_RACE_DB NO_RESIDUAL_ZZ_PKG25_ROLE PARALLEL_PROOF
prog_begin order_proof
(cd "$P" && PY order_proof.py "$R/binding" "$R/partition/xdist_nodeids.txt") > "$R/order_proof.log" 2>&1; tail -1 "$R/order_proof.log"
prog_end order_proof unobserved
prog_verdicts order_proof "$R/order_proof.log" ORDER_PROOF
prog_begin inertness
(cd "$P" && PY inertness_compare.py "$S" "${ORANGE_INERTNESS_REFERENCE:-$P/evidence/final_closure/serial_ref}") > "$F/inertness.log" 2>&1; cat "$F/inertness.log"
prog_end inertness unobserved
prog_verdicts inertness "$F/inertness.log" INSTRUMENTATION_INERT_FOR_SERIAL_OUTCOMES
echo "== final closure finished $(date -Iseconds); load $(cut -d' ' -f1-3 /proc/loadavg)"
prog_finish
