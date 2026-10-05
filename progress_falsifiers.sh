#!/usr/bin/env bash
# Falsifiers for the ORANGE structured progress + heartbeat (progress.sh, final_closure.sh). Narrow radius:
# synthetic chains for the semantics, ONE real canonical stage (serial pre: read-only catalog, guard, DB-free
# collect-only of the frozen tree) for integration, a real pytest-xdist run on a synthetic tree (no product
# code) for heartbeat progress. No product test is executed and no proof database is written.
# usage: progress_falsifiers.sh <new out dir> [<tooling dir under test>] [<base commit for the static proof>]
set -u
OUT=${1:?usage: $0 <new out dir> [tooling dir] [base commit]}
T=$(cd "${2:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)
BASE=${3:-6f7f83133c463ba8701d078c84388b3e552aabe7}
LINEAGE=/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage
XPY=/home/codi/Entwicklung/nquiry/.venv-swu-px-03/bin/python  # pytest + xdist, no ORANGE guard
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 2; }
mkdir -p "$OUT"
unset ORANGE_BYTECODE_ENV ORANGE_SERIAL_DIR ORANGE_PARALLEL_DIR
fails=0
check() { if [ "$2" = 0 ]; then echo "$1::PASS"; else echo "$1::FAIL ${3:-}"; fails=$((fails + 1)); fi; }
ev() { grep -E '^\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] ' "$1"; }  # event lines only
SECRET=S3CRET_FIXTURE_7f3a  # secret-like fixture value; must never appear in any event line

# synthetic chain runner: $1 = name, stdin = chain body (helper sourced, fresh process)
chain() {
  local name=$1; cat > "$OUT/$name.chain.sh"
  ( cd "$OUT" && env ORANGE_HEARTBEAT_SECONDS=1 PGPASSWORD=$SECRET \
      DATABASE_URL="postgresql://u:$SECRET@127.0.0.1:1/x" bash -c ". '$T/progress.sh'; . '$OUT/$name.chain.sh'" ) \
    > "$OUT/$name.out" 2>&1
  echo $? > "$OUT/$name.rc"
}
printf 'A::PASS\nB::PASS\n' > "$OUT/ok.log"
printf 'A::PASS\nB::FAIL x\n' > "$OUT/fail.log"
printf 'random words, [ 42%%] and %s and pw@%s\n' "$SECRET" "$SECRET" > "$OUT/stage.log"

# ---- main synthetic chain (PASS path) ----------------------------------------------------------
chain main <<EOF
prog_init synthetic "run=main"
prog_begin fast; true; prog_end fast "\$?"
prog_begin slow "$OUT/stage.log"; sleep 3.5; prog_end slow "\$?"
echo "\${_PROG_HB:-}" > "$OUT/main.hb_after_end"
prog_begin wait_for_hb; sleep 1.5; h=\$_PROG_HB; echo \$h > "$OUT/main.hb_during"; prog_end wait_for_hb 0; sleep 0.3
(kill -0 \$h 2>/dev/null && echo alive || echo gone; pgrep -P \$h >/dev/null && echo children || echo nochildren) > "$OUT/main.hb_state"
prog_event NOTE "url=\$DATABASE_URL" "token=\$PGPASSWORD" "note=pw@$SECRET" "plain=$SECRET x"
prog_verdicts phase_ok "$OUT/ok.log" A B
prog_finish
EOF
E=$OUT/main.events; ev "$OUT/main.out" > "$E"
[ "$(grep -c ' PROOF_START ' "$E")" -eq 1 ]; check F1_PROOF_START_ONCE $?
python3 - "$E" <<'PY'; check F2_STAGE_START_BEFORE_RESULT $?
import re, sys
lines = open(sys.argv[1]).read().splitlines()
pos = {}
for i, l in enumerate(lines):
    m = re.match(r"\[\S+\] (STAGE_START|STAGE_END|STAGE_FAIL|STAGE_TIMEOUT)\s+stage=(\S+)", l)
    if m: pos.setdefault(m.group(2), {}).setdefault(m.group(1) == "STAGE_START", i)
ok = pos and all(True in p and False in p and p[True] < p[False] for p in pos.values())
sys.exit(0 if ok else 1)
PY
[ "$(grep -c ' HEARTBEAT .*stage=slow' "$E")" -ge 2 ]; check F3_HEARTBEAT_DURING_SLOW_STAGE $? "($(grep -c ' HEARTBEAT .*stage=slow' "$E"))"
grep -q ' HEARTBEAT .*stage=slow .*pytest_progress=42%' "$E"; check F3b_HEARTBEAT_PROGRESS_FROM_LOG $?
! grep -E ' HEARTBEAT ' "$E" | grep -qE 'PASS|FAIL|verdict'; check F4_HEARTBEAT_NEVER_CLAIMS_A_VERDICT $?
[ "$(tail -1 "$E" | grep -c 'PROOF_END       verdict=PASS')" -eq 1 ] \
  && [ "$(grep -n ' VERDICT ' "$E" | tail -1 | cut -d: -f1)" -lt "$(grep -n ' PROOF_END ' "$E" | cut -d: -f1)" ]
check F5a_FINAL_PASS_ONLY_AFTER_REAL_VERDICTS $?

# ---- verdict truth: FAIL / MISSING / none / early exit never give PASS --------------------------
chain v_fail <<EOF
prog_init synthetic; prog_verdicts p "$OUT/fail.log" A; prog_finish
EOF
chain v_missing <<EOF
prog_init synthetic; prog_verdicts p "$OUT/ok.log" A B C; prog_finish
EOF
chain v_none <<EOF
prog_init synthetic; prog_finish
EOF
chain v_early <<EOF
prog_init synthetic; prog_verdicts p "$OUT/ok.log" A; prog_begin s; exit 1
EOF
r=0; for c in v_fail v_missing v_none v_early; do ev "$OUT/$c.out" | grep -q 'PROOF_END       verdict=FAIL' || r=1; ev "$OUT/$c.out" | grep -q 'verdict=PASS' && r=1; done
check F5b_FAIL_MISSING_EMPTY_OR_EARLY_EXIT_NEVER_PASS $r
ev "$OUT/v_early.out" | grep -q 'reason=chain_exited_before_final_verdict rc=1 stage=s'; check F5c_EARLY_EXIT_REPORTED_WITH_STAGE $?

# ---- failed child / timeout ----------------------------------------------------------------------
chain c_fail <<EOF
prog_init synthetic
prog_begin failing; bash -c 'exit 3'; prog_end failing "\$?"
prog_begin nofile; prog_end nofile "\$(prog_exitfile "$OUT/does_not_exist.txt")"
prog_verdicts p "$OUT/ok.log" A; prog_finish
EOF
r=0; ev "$OUT/c_fail.out" | grep -q 'STAGE_FAIL      stage=failing rc=3' || r=1
ev "$OUT/c_fail.out" | grep -q 'STAGE_FAIL      stage=nofile rc=255' || r=1
ev "$OUT/c_fail.out" | grep -q 'PROOF_END       verdict=FAIL failures=2' || r=1
check F6_FAILED_CHILD_REPORTS_STAGE_AND_EXIT_CODE $r
chain c_timeout <<EOF
prog_init synthetic
prog_begin bounded; timeout 1 sleep 5; prog_end bounded "\$?"
prog_verdicts p "$OUT/ok.log" A; prog_finish
EOF
r=0; ev "$OUT/c_timeout.out" | grep -q 'STAGE_TIMEOUT   stage=bounded rc=124' || r=1
ev "$OUT/c_timeout.out" | grep -q 'PROOF_END       verdict=FAIL' || r=1
check F7_TIMEOUT_REMAINS_TIMEOUT $r

# ---- heartbeat lifecycle ------------------------------------------------------------------------
hb=$(cat "$OUT/main.hb_during")
[ -n "$hb" ] && [ -z "$(cat "$OUT/main.hb_after_end")" ] && [ "$(tr '\n' ' ' < "$OUT/main.hb_state")" = "gone nochildren " ]
check F8_HEARTBEAT_ENDS_WITH_ITS_STAGE $? "(hb=$hb)"
cat > "$OUT/k.chain.sh" <<EOF
prog_init synthetic; prog_begin long; sleep 30 & echo \$! > "$OUT/k.stage"; echo \$_PROG_HB > "$OUT/k.hb"; wait \$!; prog_end long 0
EOF
( cd "$OUT" && ORANGE_HEARTBEAT_SECONDS=1 exec bash -c ". '$T/progress.sh'; . '$OUT/k.chain.sh'" ) > "$OUT/k.out" 2>&1 &
kp=$!
for _ in $(seq 1 50); do [ -s "$OUT/k.hb" ] && break; sleep 0.1; done
khb=$(cat "$OUT/k.hb" 2>/dev/null); sleep 1.2
kill -9 "$kp" 2>/dev/null; wait "$kp" 2>/dev/null
sleep 2.5
r=0; [ -n "$khb" ] || r=1; kill -0 "$khb" 2>/dev/null && r=1; [ -n "$(pgrep -P "$khb" 2>/dev/null)" ] && r=1
ks=$(cat "$OUT/k.stage" 2>/dev/null); [ -n "$ks" ] && kill "$ks" 2>/dev/null  # the synthetic stage child, by its recorded PID only (never a pattern kill)
check F9_NO_ORPHAN_HEARTBEAT_AFTER_CHAIN_KILL $r "(hb=$khb)"

# ---- canonical chain: ordering / membership / counts (static) -----------------------------------
git -C "$LINEAGE" show "$BASE:final_closure.sh" > "$OUT/base_final_closure.sh"
diff <(grep -vE '^(prog_[a-z]+ |prog_finish$|\. "\$P/progress\.sh")' "$T/final_closure.sh") "$OUT/base_final_closure.sh" > "$OUT/f10.diff"
check F10_COMMAND_LINES_IDENTICAL_AND_IN_ORDER $?
python3 - "$T/final_closure.sh" <<'PY'; check F10b_OBSERVABILITY_LINES_WELL_PLACED $?
import re, sys
L = open(sys.argv[1]).read().splitlines()
ok = L.count("prog_finish") == 1 and L.index("prog_finish") == max(i for i, l in enumerate(L) if l.strip()) \
    and L[L.index("prog_finish") - 1].startswith('echo "== final closure finished')
begins = [(i, l.split()[1]) for i, l in enumerate(L) if l.startswith("prog_begin ")]
for i, s in begins:  # each begin wraps exactly the next command line, then its own end
    ok = ok and not L[i + 1].startswith("prog_") and L[i + 2].startswith(f"prog_end {s} ")
sys.exit(0 if ok and begins else 1)
PY
r=0; for f in serial_baseline.sh parallel_proof.sh partition.sh serial_partition_selectors.txt analyze_serial.py aggregate.py run_aggregate.py partition_proof.py order_proof.py inertness_compare.py; do
  # successors of $BASE that are not selection / partition / proof semantics, each proven by stage_exit_falsifiers.sh: the
  # STAGE_EXIT_STATUS contract lines, and the H() environment helper (TF-PX-10 allowlist; H() is one block ending in `"$@"; }`)
  cmp -s <(sed '/^H() {/,/"\$@"; }$/d' "$T/$f" | grep -v 'STAGE_EXIT_STATUS') <(git -C "$LINEAGE" show "$BASE:$f" | sed '/^H() {/,/"\$@"; }$/d') || { r=1; echo "   changed: $f"; }; done
check F11_F12_SELECTION_PARTITION_AND_PROOF_SCRIPTS_UNCHANGED $r

# ---- integration: the real canonical serial pre stage, exactly as final_closure.sh runs it -----
F=$OUT/integration/closure; S=$F/serial_ref; mkdir -p "$S"
INT=$(sed -n '/^S=\$F\/serial_ref; mkdir -p/,/^prog_verdicts serial_pre /p' "$T/final_closure.sh")
printf '%s\n' "$INT" > "$OUT/integration/extracted_lines.txt"
( P=$T; export ORANGE_HEARTBEAT_SECONDS=5; . "$T/progress.sh"; prog_init canonical-orange-slice "run=integration"
  eval "$INT"; prog_finish ) > "$OUT/integration/chain.out" 2>&1
IE=$OUT/integration/events; ev "$OUT/integration/chain.out" > "$IE"
r=0; grep -q 'STAGE_START     stage=serial_pre' "$IE" || r=1; grep -q 'STAGE_END       stage=serial_pre rc=0' "$IE" || r=1
grep -q 'VERDICT .*name=ORANGE_IMPORT_ORIGIN value=PASS' "$IE" || r=1; grep -q 'VERDICT .*name=PROOF_DB_PRECONDITIONS value=PASS' "$IE" || r=1
grep -q 'PROOF_END       verdict=PASS' "$IE" || r=1
check F13a_REAL_STAGE_INTEGRATION $r
grep -q ' HEARTBEAT .*stage=serial_pre' "$IE"; check F13b_REAL_STAGE_HEARTBEAT $?
! grep -qE '^\[[0-9]{2}:' "$S/pre.log"; check F13c_NO_EVENT_LINES_IN_EVIDENCE_FILES $?
grep -q '^collected: 2239' "$S/pre.log"; check F13d_REAL_COLLECTION_COUNT_UNCHANGED $?

# ---- real pytest-xdist progress through the heartbeat (synthetic tree, no product code) ---------
X=$OUT/xdist; mkdir -p "$X/tree/tests" "$X/pyc"
printf '[pytest]\n' > "$X/tree/pytest.ini"
printf 'import time\n\nimport pytest\n\n\n@pytest.mark.parametrize("i", range(400))\ndef test_slow(i: int) -> None:\n    time.sleep(0.03)\n' > "$X/tree/tests/test_slow.py"
( . "$T/progress.sh"; _PROG_HB_S=1; prog_init synthetic-xdist
  prog_begin xdist_partition "$X/run.log"
  (cd "$X/tree" && env PYTHONPYCACHEPREFIX="$X/pyc" "$XPY" -m pytest -p no:cacheprovider -n 2 -rA > "$X/run.log" 2>&1); prog_end xdist_partition "$?"
  prog_finish ) > "$X/chain.out" 2>&1
ev "$X/chain.out" | grep -qE ' HEARTBEAT .*stage=xdist_partition .*pytest_progress=[0-9]+%'; check F3c_REAL_XDIST_HEARTBEAT_PROGRESS $?
[ -z "$(find "$X/tree" -name '*.pyc' -o -name __pycache__)" ]; check F13e_NO_TREE_MUTATION_BY_OBSERVABILITY $?

# ---- secrets ------------------------------------------------------------------------------------
r=0; for f in "$OUT"/*.out "$OUT"/integration/chain.out "$X/chain.out"; do ev "$f" | grep -qE "$SECRET|nquiry_local_dev_only|PGPASSWORD|://" && { r=1; echo "   leak in $f"; }; done
ev "$OUT/main.out" | grep -q 'NOTE .*<redacted>' || r=1
check F15_NO_SECRET_IN_VERBOSE_OUTPUT $r

echo "PROGRESS_FALSIFIERS::$([ $fails -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
exit $((fails > 0))
