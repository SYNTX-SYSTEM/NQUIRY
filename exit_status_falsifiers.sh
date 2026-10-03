#!/usr/bin/env bash
# Falsifiers for the FINAL_VERDICT_EXIT_STATUS runner contract (progress.sh EXIT trap):
#   PROOF_END verdict=PASS -> exit 0;  FAIL / MISSING / failed or timed-out stage -> exit nonzero;
#   an exit before the final verdict keeps its nonzero code (refused pre phase = 1).
# Narrow radius: synthetic chains, the real canonical serial pre stage (refused before it does anything),
# and replays of the canonical final_closure.sh progress lines (taken verbatim) over recorded evidence.
# No product test is executed.
# usage: exit_status_falsifiers.sh <new out dir> [<tooling dir under test>] [<base commit for E11>]
set -u
OUT=${1:?usage: $0 <new out dir> [tooling dir] [base commit]}
T=$(cd "${2:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)
BASE=${3:-64e9113d65df80a67e384c250448880165dfc2ca}
LINEAGE=/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 2; }
mkdir -p "$OUT"
unset ORANGE_BYTECODE_ENV ORANGE_SERIAL_DIR ORANGE_PARALLEL_DIR ORANGE_CLOSURE_DIR
fails=0
check() { if [ "$2" = 0 ]; then echo "$1::PASS"; else echo "$1::FAIL ${3:-}"; fails=$((fails + 1)); fi; }
ev() { grep -E '^\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] ' "$1"; }
rcof() { cat "$OUT/$1.rc"; }
lastev() { ev "$OUT/$1.out" | tail -1; }

chain() {  # $1 name, stdin = body; runs in its own bash process (its own EXIT trap) with progress.sh from $2
  local name=$1 helper=${2:-$T/progress.sh}; cat > "$OUT/$name.chain.sh"
  ( cd "$OUT" && env ORANGE_HEARTBEAT_SECONDS=1 bash -c ". '$helper'; . '$OUT/$name.chain.sh'" ) > "$OUT/$name.out" 2>&1
  echo $? > "$OUT/$name.rc"
}
printf 'A::PASS\nB::PASS\n' > "$OUT/ok.log"; printf 'A::PASS\nB::FAIL x\n' > "$OUT/fail.log"

chain e1_pass <<EOF
prog_init synthetic; prog_begin slow; sleep 2.5; prog_end slow "\$?"; prog_verdicts p "$OUT/ok.log" A B; prog_finish
EOF
[ "$(rcof e1_pass)" -eq 0 ] && lastev e1_pass | grep -q 'PROOF_END       verdict=PASS' && ev "$OUT/e1_pass.out" | grep -q ' HEARTBEAT '
check E1_ALL_PASS_EXITS_0 $? "(rc=$(rcof e1_pass))"
chain e2_fail <<EOF
prog_init synthetic; prog_verdicts p "$OUT/fail.log" A B; prog_finish
EOF
[ "$(rcof e2_fail)" -ne 0 ] && lastev e2_fail | grep -q 'PROOF_END       verdict=FAIL'; check E2_FAIL_VERDICT_EXITS_NONZERO $? "(rc=$(rcof e2_fail))"
chain e3_missing <<EOF
prog_init synthetic; prog_verdicts p "$OUT/ok.log" A B C; prog_finish
EOF
[ "$(rcof e3_missing)" -ne 0 ] && ev "$OUT/e3_missing.out" | grep -q 'name=C value=MISSING' && lastev e3_missing | grep -q 'verdict=FAIL'
check E3_MISSING_VERDICT_EXITS_NONZERO $? "(rc=$(rcof e3_missing))"
chain e4_timeout <<EOF
prog_init synthetic; prog_begin bounded; timeout 1 sleep 5; prog_end bounded "\$?"; prog_verdicts p "$OUT/ok.log" A B; prog_finish
EOF
[ "$(rcof e4_timeout)" -ne 0 ] && ev "$OUT/e4_timeout.out" | grep -q 'STAGE_TIMEOUT   stage=bounded rc=124' && lastev e4_timeout | grep -q 'verdict=FAIL'
check E4_TIMEOUT_EXITS_NONZERO $? "(rc=$(rcof e4_timeout))"
chain e5_child <<EOF
prog_init synthetic; prog_begin failing; bash -c 'exit 3'; prog_end failing "\$?"; prog_verdicts p "$OUT/ok.log" A B; prog_finish
EOF
[ "$(rcof e5_child)" -ne 0 ] && ev "$OUT/e5_child.out" | grep -q 'STAGE_FAIL      stage=failing rc=3' && lastev e5_child | grep -q 'verdict=FAIL'
check E5_CHILD_STAGE_FAILURE_EXITS_NONZERO $? "(rc=$(rcof e5_child))"
chain e5b_early_zero <<EOF
prog_init synthetic; prog_verdicts p "$OUT/ok.log" A B; exit 0
EOF
[ "$(rcof e5b_early_zero)" -ne 0 ] && lastev e5b_early_zero | grep -q 'reason=chain_exited_before_final_verdict'
check E5b_EXIT_0_BEFORE_FINAL_VERDICT_BECOMES_NONZERO $? "(rc=$(rcof e5b_early_zero))"

# ---- E6: refused pre phase keeps its existing nonzero stop (real canonical lines, real serial_baseline.sh)
F=$OUT/e6/closure; S=$F/serial_ref; mkdir -p "$S"; echo "pre-existing evidence" > "$S/foreign.txt"
sed -n '/^S=\$F\/serial_ref; mkdir -p/,/CHAIN STOPPED: serial pre/p' "$T/final_closure.sh" > "$OUT/e6/extracted_lines.txt"
( env F="$F" P="$T" ORANGE_HEARTBEAT_SECONDS=1 bash -c ". '$T/progress.sh'; prog_init canonical-orange-slice run=e6
  . '$OUT/e6/extracted_lines.txt'; echo CHAIN_CONTINUED; prog_finish" ) > "$OUT/e6.out" 2>&1; echo $? > "$OUT/e6.rc"
[ "$(rcof e6)" -eq 1 ] && grep -q 'CHAIN STOPPED: serial pre refused' "$OUT/e6.out" && ! grep -q CHAIN_CONTINUED "$OUT/e6.out" \
  && lastev e6 | grep -q 'verdict=FAIL reason=chain_exited_before_final_verdict rc=1'
check E6a_REFUSED_PRE_PHASE_STOPS_WITH_1 $? "(rc=$(rcof e6))"
mkdir -p "$OUT/e6b_existing"
( ORANGE_CLOSURE_DIR="$OUT/e6b_existing" bash "$T/final_closure.sh" ) > "$OUT/e6b.out" 2>&1; echo $? > "$OUT/e6b.rc"
[ "$(rcof e6b)" -eq 1 ] && grep -q '^REFUSED: .* exists' "$OUT/e6b.out" && ! grep -q PROOF_START "$OUT/e6b.out"
check E6b_EXISTING_CLOSURE_DIR_STILL_REFUSED_WITH_1 $? "(rc=$(rcof e6b))"

# ---- E7 / E8: the canonical final_closure.sh progress lines, verbatim, replayed over recorded evidence
grep -E '^prog_' "$T/final_closure.sh" > "$OUT/canonical_progress_lines.txt"
replay() {  # name evidence_dir parallel_subdir helper [sed substitution]
  local name=$1 F=$2 Rsub=$3 helper=$4 sub=${5:-}
  local body; body=$(cat "$OUT/canonical_progress_lines.txt"); [ -n "$sub" ] && body=$(printf '%s\n' "$body" | sed "$sub")
  printf '%s\n' "$body" > "$OUT/$name.replay.sh"
  ( env F="$F" S="$F/serial_ref" R="$F/$Rsub" P="$T" rc=0 ORANGE_HEARTBEAT_SECONDS=30 \
      bash -c ". '$helper'; . '$OUT/$name.replay.sh'" ) > "$OUT/$name.out" 2>&1
  echo $? > "$OUT/$name.rc"
}
# rc=0 for the two pre stages: their pre phases completed in those runs (the chain only proceeds past a pre phase that is not refused)
replay e7_pcpg5_historical "$LINEAGE/evidence/final_closure" parallel "$T/progress.sh"
[ "$(rcof e7_pcpg5_historical)" -ne 0 ] && lastev e7_pcpg5_historical | grep -q 'verdict=FAIL' \
  && ev "$OUT/e7_pcpg5_historical.out" | grep -q 'STAGE_FAIL      stage=serial_partition rc=1'
check E7_HISTORICAL_PCPG5_FAIL_EVIDENCE_EXITS_NONZERO $? "(rc=$(rcof e7_pcpg5_historical))"
replay e8a_canonical_e2e_pass "$LINEAGE/evidence/final_closure_20261003T174103" parallel "$T/progress.sh"
[ "$(rcof e8a_canonical_e2e_pass)" -eq 0 ] && lastev e8a_canonical_e2e_pass | grep -q 'verdict=PASS'
check E8a_CANONICAL_E2E_PASS_EVIDENCE_EXITS_0 $? "(rc=$(rcof e8a_canonical_e2e_pass))"
# the SWU-PX-03 successor binding wrote its preservation verdict (instead of the PCPG-5 inertness verdict) into the re-run dir
SWU_SUB='s#"$F/inertness.log" INSTRUMENTATION_INERT_FOR_SERIAL_OUTCOMES#"$R/inertness.log" SUCCESSOR_PRESERVES_PCPG5_SERIAL_OUTCOMES#'
replay e8b_swu_px_03_pass "$LINEAGE/successors/SWU-PX-03/evidence/final_closure" parallel_r2_after_TF-PX-05 "$T/progress.sh" "$SWU_SUB"
[ "$(rcof e8b_swu_px_03_pass)" -eq 0 ] && lastev e8b_swu_px_03_pass | grep -q 'verdict=PASS'
check E8b_SWU_PX_03_PASS_EVIDENCE_EXITS_0 $? "(rc=$(rcof e8b_swu_px_03_pass))"
replay e8c_swu_px_03_failed_first_run "$LINEAGE/successors/SWU-PX-03/evidence/final_closure" parallel "$T/progress.sh" \
  's#"$F/inertness.log" INSTRUMENTATION_INERT_FOR_SERIAL_OUTCOMES#"$F/inertness.log" SUCCESSOR_PRESERVES_PCPG5_SERIAL_OUTCOMES#'
[ "$(rcof e8c_swu_px_03_failed_first_run)" -ne 0 ] && ev "$OUT/e8c_swu_px_03_failed_first_run.out" | grep -q 'name=TREE_UNCHANGED value=FAIL'
check E8c_SWU_PX_03_FAILED_FIRST_RUN_EXITS_NONZERO $? "(rc=$(rcof e8c_swu_px_03_failed_first_run))"

# ---- E9: a running heartbeat cannot turn a failure into exit 0
chain e9_hb_fail <<EOF
prog_init synthetic; prog_verdicts p "$OUT/fail.log" A B; prog_begin still_running; sleep 2.5; prog_finish
EOF
[ "$(rcof e9_hb_fail)" -ne 0 ] && ev "$OUT/e9_hb_fail.out" | grep -q 'HEARTBEAT .*stage=still_running' && lastev e9_hb_fail | grep -q 'verdict=FAIL'
check E9_HEARTBEAT_CANNOT_TURN_FAILURE_INTO_EXIT_0 $? "(rc=$(rcof e9_hb_fail))"

# ---- E10: PROOF_END is emitted exactly once and is the last event, in every run
r=0; for f in "$OUT"/*.out; do case "$f" in */e6b.out|*/e11_base_*) continue;; esac  # base outputs keep TF-PX-06 (checked in E11)
  [ "$(ev "$f" | grep -c ' PROOF_END ')" -eq 1 ] && ev "$f" | tail -1 | grep -q ' PROOF_END ' || { r=1; echo "   $f"; }; done
check E10_PROOF_END_ONCE_AND_LAST $r

git -C "$LINEAGE" show "$BASE:progress.sh" > "$OUT/base_progress.sh"
# ---- E10b: TF-PX-06 fork race -- zero-duration stages, repeated: PROOF_END must still be emitted exactly once
r=0; for i in $(seq 1 100); do
  c=$(cd "$OUT" && ORANGE_HEARTBEAT_SECONDS=1 bash -c ". '$T/progress.sh'; prog_init race; prog_begin a; prog_end a 0; prog_begin b; prog_end b 0; prog_verdicts p '$OUT/ok.log' A; prog_finish" 2>&1 | grep -c ' PROOF_END ')
  [ "$c" -eq 1 ] || r=1; done
check E10b_NO_SPURIOUS_PROOF_END_FROM_HEARTBEAT_FORK_RACE $r

# informational (not gating): the BASE helper's TF-PX-06 race rate on the same zero-duration chain
bn=0; for i in $(seq 1 30); do c=$(cd "$OUT" && ORANGE_HEARTBEAT_SECONDS=1 bash -c ". '$OUT/base_progress.sh'; prog_init race; prog_begin a; prog_end a 0; prog_begin b; prog_end b 0; prog_verdicts p '$OUT/ok.log' A; prog_finish" 2>&1 | grep -c ' PROOF_END '); [ "$c" -eq 1 ] || bn=$((bn+1)); done
echo "   info: base helper runs with a spurious PROOF_END: $bn/30 (TF-PX-06 present at $BASE)"

# ---- E11: event output unchanged versus the base helper (timestamps / elapsed normalized)
replay e11_base_e7 "$LINEAGE/evidence/final_closure" parallel "$OUT/base_progress.sh"
replay e11_base_e8a "$LINEAGE/evidence/final_closure_20261003T174103" parallel "$OUT/base_progress.sh"
chain e11_base_e2 "$OUT/base_progress.sh" < "$OUT/e2_fail.chain.sh"
norm() { ev "$1" | sed -E 's/^\[[0-9:]+\] //; s/ elapsed=[^ ]+//g'; }
# the only permitted difference: TF-PX-06 artifacts of the BASE helper (a non-final PROOF_END from a heartbeat subshell)
norm_base() { norm "$1" | awk '{l[NR]=$0} END{for(i=1;i<=NR;i++) if(!(i<NR && l[i] ~ /^PROOF_END +verdict=FAIL reason=chain_exited_before_final_verdict/)) print l[i]}'; }
r=0; for pair in "e7_pcpg5_historical e11_base_e7" "e8a_canonical_e2e_pass e11_base_e8a" "e2_fail e11_base_e2"; do set -- $pair
  echo "   base TF-PX-06 artifacts removed in $2: $(( $(norm "$OUT/$2.out" | wc -l) - $(norm_base "$OUT/$2.out" | wc -l) ))"
  diff <(norm "$OUT/$1.out") <(norm_base "$OUT/$2.out") > "$OUT/e11_$1.diff" || { r=1; echo "   events differ: $1"; }; done
check E11_EVENT_OUTPUT_UNCHANGED_VS_BASE $r
[ "$(rcof e11_base_e7)" -eq 0 ]; check E11b_BASE_HELPER_REALLY_EXITED_0_ON_FAIL $? "(documents the defect: rc=$(rcof e11_base_e7))"

# ---- E12: no orphan process
sleep 1.5
n=$(ps -eo args | grep -E -- "$OUT/[^ ]*\.(chain|replay)\.sh" | grep -v grep | wc -l); [ "$n" -eq 0 ]; check E12_NO_ORPHAN_PROCESS $? "($n)"  # synthetic chains / replays only

echo "EXIT_STATUS_FALSIFIERS::$([ $fails -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
exit $((fails > 0))
