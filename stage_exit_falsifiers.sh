#!/usr/bin/env bash
# Falsifiers for the STAGE_EXIT_STATUS runner contract of the standalone stage runners
# (serial_baseline.sh run, parallel_proof.sh xdist | serial):
#   recorded *_exit_code.txt == 0 -> process exit 0;  anything else (nonzero, absent, garbage) -> process exit 1;
#   the recorded raw code, the stage's stdout, its evidence files and the canonical chain are unchanged.
# Narrow radius: the REAL runner scripts are executed with exactly ONE substituted line (N= -> a synthetic root),
# so their governed child is a stub (chosen exit code) or a real pytest / pytest-xdist on a synthetic tree.
# No product test is executed, no product tree is read, no database is contacted.
#
# PROOF-ENVIRONMENT BOUNDARY (TF-PX-10): the runners give their governed children an ALLOWLIST environment
# (env -i). S12 proves it on the real runners: ambient variables (a fixture credential, variables the target reads,
# PYTHONPATH, an ambient DATABASE_URL) never reach the child; the allowlisted and runner-set ones do. The stub is
# therefore configured through a file, not through the environment.
# SECRET HYGIENE (TF-PX-09): this harness re-executes itself under `env -i` with a fixed allowlist plus a FIXTURE
# credential; only variable NAMES are ever written; S13 fails if the fixture value reaches any evidence file.
# usage: stage_exit_falsifiers.sh <new out dir> [<tooling dir under test>] [<base commit>]
set -u
SECRET=S3CRET_FIXTURE_4d7e  # fixture only; stands for any credential in the operator environment
if [ "${SFE_PEO_SCRUBBED:-}" != 1 ]; then
  exec env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 SFE_PEO_SCRUBBED=1 SFE_FIXTURE_API_KEY="$SECRET" bash "${BASH_SOURCE[0]}" "$@"
fi
OUT=${1:?usage: $0 <new out dir> [tooling dir] [base commit]}
T=$(cd "${2:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)
BASE=${3:-ca9cbf94eff5c7d37ed0c5e6aa4bcabf9577b28d}  # last lineage commit whose stage runners exit 0 regardless
LINEAGE=/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage
XPY=/home/codi/Entwicklung/nquiry/.venv-swu-px-03/bin/python  # pytest + xdist, no ORANGE guard, no path binding
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 2; }
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
unset ORANGE_BYTECODE_ENV ORANGE_SERIAL_DIR ORANGE_PARALLEL_DIR ORANGE_CLOSURE_DIR ORANGE_CATALOG_DB PYTEST_ADDOPTS
fails=0
check() { if [ "$2" = 0 ]; then echo "$1::PASS"; else echo "$1::FAIL ${3:-}"; fails=$((fails + 1)); fi; }
ev() { grep -E '^\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] ' "$1"; }
rcof() { cat "$OUT/$1.rc"; }

# ---- synthetic root: stub environment python + synthetic tree (the runners derive V and O from N) --------
ROOT=$OUT/root; O=$ROOT/worktrees/orange-proof-infra; mkdir -p "$ROOT/.venv-proof313-orange/bin" "$ROOT/stubbin" "$O/tests"
cat > "$ROOT/.venv-proof313-orange/bin/python" <<'STUB'
#!/usr/bin/env bash
# stub for the governed child, configured by <root>/stub.conf (never by the environment: the runners scrub it).
# rc:<n> = print and exit n; real = the same argv on a real pytest; verdictfail = a failing verdict producer;
# envnames = report the NAMES of the environment this child received (never a value)
. "$(cd "$(dirname "$0")/../.." && pwd)/stub.conf"
case "$MODE" in
  rc:*) echo "stub governed child: $*"; echo "= stub finished ="; exit "${MODE#rc:}" ;;
  real) [ -n "$SYNTH_FAIL" ] && export ORANGE_SYNTH_FAIL=1; exec "$XPY" "$@" $ADDOPTS ;;
  verdictfail) echo "PROOF_DB_PRECONDITIONS::FAIL (stub)"; exit 1 ;;
  envnames) env -0 | cut -z -d= -f1 | sort -z | tr '\0' '\n' | sed 's/^/ENVNAME /'
    echo "DBNAME ${DATABASE_URL:+${DATABASE_URL##*/}}"; echo "CATALOG ${ORANGE_CATALOG_DB:-}"; exit 0 ;;
esac
STUB
printf '#!/usr/bin/env bash\nexit 2\n' > "$ROOT/stubbin/psql"  # info probe only: the post phase never reaches a database
chmod +x "$ROOT/.venv-proof313-orange/bin/python" "$ROOT/stubbin/psql"
printf '[pytest]\n' > "$O/pytest.ini"
BODY='    assert os.environ.get("ORANGE_SYNTH_FAIL") != "1"\n'
while IFS= read -r sel; do [ -n "$sel" ] || continue
  mkdir -p "$O/$(dirname "${sel%%::*}")"; printf "import os\n\n\ndef ${sel##*::}() -> None:\n$BODY" > "$O/${sel%%::*}"
done < "$T/serial_partition_selectors.txt"
printf "import os\n\nimport pytest\n\n\n@pytest.mark.parametrize(\"i\", range(8))\ndef test_other(i: int) -> None:\n$BODY" > "$O/tests/test_other.py"
tree_before=$(cd "$O" && find . | sort | sha256sum)

mktool() {  # dir source-getter...: the runners with ONLY the N= line substituted
  local d=$1; shift; mkdir -p "$d"
  for f in serial_baseline.sh parallel_proof.sh partition.sh serial_partition_selectors.txt; do "$@" "$f" > "$d/$f.orig"
    sed "s#^N=.*#N=$ROOT#" "$d/$f.orig" > "$d/$f"; diff "$d/$f.orig" "$d/$f" > "$d/$f.substitution.diff"; rm "$d/$f.orig"; done
}
from_t() { cat "$T/$1"; }; from_base() { git -C "$LINEAGE" show "$BASE:$1"; }
mktool "$OUT/tool" from_t; mktool "$OUT/base_tool" from_base
r=0; for f in serial_baseline.sh parallel_proof.sh partition.sh; do [ "$(grep -c '^[<>]' "$OUT/tool/$f.substitution.diff")" -eq 2 ] || r=1; done
[ ! -s "$OUT/tool/serial_partition_selectors.txt.substitution.diff" ] || r=1
check S0_ONLY_THE_ROOT_LINE_IS_SUBSTITUTED $r

AMB=()  # ambient environment given to the runner process for one stage (what an operator shell might export)
conf() {  # mode [SYNTH_FAIL=1] [ADDOPTS=...]: the stub's configuration file
  local mode=$1 kv; shift
  { printf 'MODE=%q\nXPY=%q\nSYNTH_FAIL=\nADDOPTS=\n' "$mode" "$XPY"; for kv in "$@"; do printf '%s=%q\n' "${kv%%=*}" "${kv#*=}"; done; } > "$ROOT/stub.conf"
}
stage() {  # name tooldir script phase mode [stub conf KEY=value ...]
  local name=$1 tool=$2 script=$3 phase=$4 mode=$5; shift 5
  conf "$mode" "$@"
  ( cd "$OUT" && env ORANGE_SERIAL_DIR="$OUT/$name.d" ORANGE_PARALLEL_DIR="$OUT/$name.d" "${AMB[@]}" \
      bash "$tool/$script" "$phase" ) > "$OUT/$name.out" 2>&1
  echo $? > "$OUT/$name.rc"
}
STAGES="sb_run:serial_baseline.sh:run pp_xdist:parallel_proof.sh:xdist pp_serial:parallel_proof.sh:serial"
each() { local s; for s in $STAGES; do IFS=: read -r id script phase <<< "$s"; "$@"; done; }
recorded() { tr -d '[:space:]' < "$OUT/$1.d/${phase}_exit_code.txt" 2>/dev/null; }

# ---- S1 / S2: the governed child's result -> recorded truth -> process exit status ------------------------
s1() { stage "s1_$id" "$OUT/tool" "$script" "$phase" rc:0
  [ "$(rcof "s1_$id")" -eq 0 ] && [ "$(recorded "s1_$id")" = 0 ] && grep -q 'exit=0' "$OUT/s1_$id.out"
  check "S1_PASSED_PROOF_EXITS_0[$script $phase]" $? "(rc=$(rcof "s1_$id") recorded=$(recorded "s1_$id"))"; }
each s1
s2() { stage "s2_$id" "$OUT/tool" "$script" "$phase" rc:1
  [ "$(rcof "s2_$id")" -eq 1 ] && [ "$(recorded "s2_$id")" = 1 ] && grep -q 'exit=1' "$OUT/s2_$id.out"
  check "S2_FAILED_PROOF_EXITS_NONZERO[$script $phase]" $? "(rc=$(rcof "s2_$id") recorded=$(recorded "s2_$id"))"; }
each s2

# ---- S3: every nonzero raw code -> process exit exactly 1 (never 2 = usage, never 0 for exit 5); raw code kept
s3() { local r=0 c; for c in 2 3 4 5 124 137 255; do stage "s3_${id}_$c" "$OUT/tool" "$script" "$phase" "rc:$c"
    [ "$(rcof "s3_${id}_$c")" -eq 1 ] && [ "$(recorded "s3_${id}_$c")" = "$c" ] && grep -q "exit=$c" "$OUT/s3_${id}_$c.out" \
      || { r=1; echo "   raw=$c rc=$(rcof "s3_${id}_$c") recorded=$(recorded "s3_${id}_$c")"; }; done
  check "S3_ANY_NONZERO_RAW_CODE_EXITS_1_AND_STAYS_RECORDED[$script $phase]" $r; }
each s3

# ---- S4: a real pytest / pytest-xdist child on the synthetic tree (pass, fail, no tests collected) -------
s4() { stage "s4p_$id" "$OUT/tool" "$script" "$phase" real
  [ "$(rcof "s4p_$id")" -eq 0 ] && [ "$(recorded "s4p_$id")" = 0 ] && grep -qE '[0-9]+ passed' "$OUT/s4p_$id.out" && ! grep -q failed "$OUT/s4p_$id.out"
  check "S4a_REAL_PYTEST_PASS_EXITS_0[$script $phase]" $? "(rc=$(rcof "s4p_$id") $(tail -1 "$OUT/s4p_$id.out"))"
  stage "s4f_$id" "$OUT/tool" "$script" "$phase" real SYNTH_FAIL=1
  [ "$(rcof "s4f_$id")" -eq 1 ] && [ "$(recorded "s4f_$id")" = 1 ] && grep -qE '[0-9]+ failed' "$OUT/s4f_$id.out"
  check "S4b_REAL_PYTEST_FAILURE_EXITS_NONZERO[$script $phase]" $? "(rc=$(rcof "s4f_$id") $(tail -1 "$OUT/s4f_$id.out"))"
  stage "s4n_$id" "$OUT/tool" "$script" "$phase" real ADDOPTS="-k matches_no_test_at_all"
  [ "$(rcof "s4n_$id")" -eq 1 ] && [ "$(recorded "s4n_$id")" = 5 ]
  check "S4c_REAL_NO_TESTS_COLLECTED_EXIT_5_IS_FAILURE[$script $phase]" $? "(rc=$(rcof "s4n_$id") recorded=$(recorded "s4n_$id"))"; }
each s4
n=$(grep -c 'testcase' "$OUT/s4p_pp_xdist.d/xdist_junit.xml" 2>/dev/null); grep -q 'created: 4/4 workers' "$OUT/s4p_pp_xdist.d/xdist_run.log" 2>/dev/null \
  && [ "$(grep -o 'tests="[0-9]*"' "$OUT/s4p_pp_xdist.d/xdist_junit.xml" | head -1)" = 'tests="8"' ] \
  && [ "$(grep -o 'tests="[0-9]*"' "$OUT/s4p_pp_serial.d/serial_junit.xml" | head -1)" = "tests=\"$(grep -c . "$T/serial_partition_selectors.txt")\"" ]
check S4d_REAL_PARTITION_SELECTION_STILL_APPLIED $? "(xdist deselects the serial selectors under 4 workers; serial runs exactly them)"

# ---- S5: recorded truth, stdout and evidence files identical to the base runners (only the status differs)
normdir() { sed -e "s#$OUT/$1\.d#DIR#g" -e "s#$OUT/\(base_\)\?tool#TOOL#g" -e 's/ wall=[^ ]* s$/ wall=N s/'; }
s5() { local r=0 m f a b; for m in 0 1 5; do a="s5_${id}_$m"; b="s5base_${id}_$m"
    stage "$a" "$OUT/tool" "$script" "$phase" "rc:$m"; stage "$b" "$OUT/base_tool" "$script" "$phase" "rc:$m"
    diff <(normdir "$a" < "$OUT/$a.out") <(normdir "$b" < "$OUT/$b.out") > "$OUT/$a.stdout.diff" || { r=1; echo "   stdout differs: $a"; }
    diff <(cd "$OUT/$a.d" && find . | sort) <(cd "$OUT/$b.d" && find . | sort) > "$OUT/$a.files.diff" || { r=1; echo "   file set differs: $a"; }
    for f in $(cd "$OUT/$a.d" && find . -type f ! -name '*_t0' ! -name '*_t1' ! -name '*_started.txt' ! -name '*_finished.txt'); do
      cmp -s <(normdir "$a" < "$OUT/$a.d/$f") <(normdir "$b" < "$OUT/$b.d/$f") || { r=1; echo "   content differs: $a/$f"; }; done
    [ "$(recorded "$a")" = "$m" ] && [ "$(recorded "$b")" = "$m" ] || { r=1; echo "   recorded code: $a"; }
  done
  check "S5_RECORDED_TRUTH_STDOUT_AND_EVIDENCE_IDENTICAL_TO_BASE[$script $phase]" $r
  [ "$(rcof "s5base_${id}_1")" -eq 0 ] && [ "$(rcof "s5base_${id}_5")" -eq 0 ]
  check "S5b_BASE_RUNNER_REALLY_EXITED_0_ON_FAILED_PROOF[$script $phase]" $? "(documents the defect: rc=$(rcof "s5base_${id}_1"))"; }
each s5

# ---- S6: the status mapping itself is fail-closed (absent / empty / garbage exit-code file is never success)
printf '0\n' > "$OUT/s6_zero"; : > "$OUT/s6_empty"; echo "garbage" > "$OUT/s6_garbage"; echo "1" > "$OUT/s6_one"; echo "-0" > "$OUT/s6_minus"
for f in serial_baseline.sh parallel_proof.sh; do
  def=$(grep -E '^stage_exit\(\) \{' "$T/$f"); r=0; [ -n "$def" ] || r=1
  for c in zero:0 empty:1 garbage:1 one:1 minus:1 absent:1; do
    ( eval "$def"; stage_exit "$OUT/s6_${c%%:*}"; exit 97 ) > /dev/null 2>&1; g=$?
    [ "$g" -eq "${c##*:}" ] || { r=1; echo "   $f ${c%%:*} -> $g (want ${c##*:})"; }; done
  check "S6_STATUS_MAPPING_IS_FAIL_CLOSED[$f]" $r
done

# ---- S7: usage and refusal contracts unchanged (2 = usage, 1 = refusal) ----------------------------------
r=0; for f in serial_baseline.sh parallel_proof.sh; do for t in tool base_tool; do
  stage "s7u_${t}_$f" "$OUT/$t" "$f" "" rc:0; stage "s7b_${t}_$f" "$OUT/$t" "$f" bogus rc:0
  mkdir -p "$OUT/s7r_${t}_$f.d"; echo "pre-existing evidence" > "$OUT/s7r_${t}_$f.d/foreign.txt"
  stage "s7r_${t}_$f" "$OUT/$t" "$f" pre rc:0
  [ "$(rcof "s7u_${t}_$f")" -eq 2 ] && [ "$(rcof "s7b_${t}_$f")" -eq 2 ] && grep -q '^usage: ' "$OUT/s7u_${t}_$f.out" || r=1
  [ "$(rcof "s7r_${t}_$f")" -eq 1 ] && grep -q '^REFUSED: ' "$OUT/s7r_${t}_$f.out" && [ "$(ls "$OUT/s7r_${t}_$f.d")" = foreign.txt ] || r=1; done; done
check S7_USAGE_2_AND_REFUSAL_1_UNCHANGED $r

# ---- S8: canonical chain semantics: the chain's own stage lines (verbatim), fed by the runners under test --
SR=$(grep -A2 -E '^prog_begin serial_reference ' "$T/final_closure.sh")
XP=$(sed -n '/^prog_begin xdist_partition /,/^prog_end serial_partition /p' "$T/final_closure.sh")
printf '%s\n%s\n' "$SR" "$XP" > "$OUT/s8_extracted_lines.txt"
printf 'A::PASS\nB::PASS\n' > "$OUT/ok.log"
slice() {  # name tooldir mode
  local name=$1 F=$OUT/$1.d; mkdir -p "$F/serial_ref" "$F/parallel"; conf "$3"
  ( cd "$OUT" && env F="$F" S="$F/serial_ref" R="$F/parallel" P="$2" ORANGE_HEARTBEAT_SECONDS=30 \
      bash -c ". '$T/progress.sh'; prog_init stage-exit-slice run=slice; export ORANGE_SERIAL_DIR=\$S
        $SR
        unset ORANGE_SERIAL_DIR; export ORANGE_PARALLEL_DIR=\$R
        $XP
        echo CHAIN_CONTINUED; prog_verdicts slice '$OUT/ok.log' A B; prog_finish" ) > "$OUT/$name.out" 2>&1
  echo $? > "$OUT/$name.rc"
}
slice s8_fail "$OUT/tool" rc:4; slice s8_pass "$OUT/tool" rc:0; slice s8base_fail "$OUT/base_tool" rc:4; slice s8base_pass "$OUT/base_tool" rc:0
r=0; for st in serial_reference xdist_partition serial_partition; do
  ev "$OUT/s8_fail.out" | grep -q "STAGE_FAIL      stage=$st rc=4" || r=1; ev "$OUT/s8_pass.out" | grep -q "STAGE_END       stage=$st rc=0" || r=1; done
grep -q CHAIN_CONTINUED "$OUT/s8_fail.out" || r=1
check S8a_CHAIN_CONTINUES_PAST_A_FAILED_STAGE_AND_REPORTS_THE_RAW_CODE $r
[ "$(rcof s8_fail)" -eq 1 ] && ev "$OUT/s8_fail.out" | tail -1 | grep -q 'PROOF_END       verdict=FAIL failures=3' \
  && [ "$(rcof s8_pass)" -eq 0 ] && ev "$OUT/s8_pass.out" | tail -1 | grep -q 'PROOF_END       verdict=PASS'
check S8b_CHAIN_FINAL_VERDICT_AND_EXIT_STATUS_UNCHANGED $? "(fail rc=$(rcof s8_fail), pass rc=$(rcof s8_pass))"
normev() { sed -E 's/^\[[0-9:]+\] //; s/ elapsed=[^ ]+//g; s/ wall=[^ ]* s$/ wall=N s/'; }
r=0; for k in fail pass; do diff <(normev < "$OUT/s8_$k.out") <(normev < "$OUT/s8base_$k.out") > "$OUT/s8_$k.vs_base.diff" || r=1
  [ "$(rcof "s8_$k")" = "$(rcof "s8base_$k")" ] || r=1; done
check S8c_CHAIN_OUTPUT_AND_STATUS_IDENTICAL_WITH_BASE_RUNNERS $r

# ---- S9 / S10: static -- the chain does not consume the stage process status; nothing else changed --------
r=0; cmp -s "$T/final_closure.sh" <(git -C "$LINEAGE" show "$BASE:final_closure.sh") || { r=1; echo "   final_closure.sh differs from $BASE"; }
grep -nE '^[^#]*(set -[a-zA-Z]*e|set -o (errexit|pipefail)|trap [^#]*ERR)' "$T/final_closure.sh" "$T/progress.sh" && r=1
calls=$(grep -cE '^[^#]*(serial_baseline\.sh" run|parallel_proof\.sh" (xdist|serial))' "$T/final_closure.sh")
bad=$(grep -E '^[^#]*(serial_baseline\.sh" run|parallel_proof\.sh" (xdist|serial))' "$T/final_closure.sh" | grep -cE '&&|\|\||^ *(if|while|until|!) |\$\?')
[ "$calls" -eq 3 ] && [ "$bad" -eq 0 ] || r=1
check S9_CHAIN_UNCHANGED_AND_NEVER_CONSUMES_THE_STAGE_PROCESS_STATUS $r "(calls=$calls conditional=$bad)"
# outside the STAGE_EXIT_STATUS lines and the H() environment helper (TF-PX-10, proven by S12) the scripts equal the base
normrunner() { sed '/^H() {/,/"\$@"; }$/d' | grep -v 'STAGE_EXIT_STATUS'; }
r=0; for f in serial_baseline.sh:2 parallel_proof.sh:3 partition.sh:0; do n=${f##*:}; f=${f%%:*}
  diff <(normrunner < "$T/$f") <(git -C "$LINEAGE" show "$BASE:$f" | normrunner) > "$OUT/s10_$f.diff" || { r=1; echo "   $f: more than the contract lines and H() changed"; }
  [ "$(grep -c 'STAGE_EXIT_STATUS' "$T/$f")" -eq "$n" ] || { r=1; echo "   $f: contract lines $(grep -c 'STAGE_EXIT_STATUS' "$T/$f"), want $n"; }
  [ "$(grep -c '^H() {' "$T/$f")" -eq 1 ] || { r=1; echo "   $f: H() definitions"; }; done
for f in serial_partition_selectors.txt analyze_serial.py aggregate.py run_aggregate.py partition_proof.py order_proof.py inertness_compare.py observer.sh canonical_ids.py verify_proof_dbs.py env_manifest.py; do
  cmp -s "$T/$f" <(git -C "$LINEAGE" show "$BASE:$f") || { r=1; echo "   changed: $f"; }; done
check S10_ONLY_CONTRACT_LINES_AND_ENV_HELPER_DIFFER_SELECTION_PARTITION_AGGREGATION_UNCHANGED $r

# ---- S11: no tree mutation, no orphan process ---------------------------------------------------------------
[ "$tree_before" = "$(cd "$O" && find . | sort | sha256sum)" ] && [ -z "$(find "$O" -name '*.pyc' -o -name __pycache__)" ]
check S11a_SYNTHETIC_TREE_UNCHANGED_NO_BYTECODE_IN_TREE $?
sleep 1.5
n=$(ps -eo args | grep -E -- "$OUT/(tool|base_tool|root)/" | grep -v grep | wc -l); [ "$n" -eq 0 ]; check S11b_NO_ORPHAN_PROCESS $? "($n)"

# ---- S12: proof-environment boundary: governed children receive the allowlist, never the ambient environment ---
ALLOWED=" PATH HOME USER LOGNAME LANG LANGUAGE LC_ALL LC_CTYPE LC_COLLATE LC_MESSAGES LC_NUMERIC LC_TIME LC_MONETARY LC_ADDRESS LC_IDENTIFICATION LC_MEASUREMENT LC_NAME LC_PAPER LC_TELEPHONE TZ TMPDIR ORANGE_CATALOG_DB PYTHONNOUSERSITE PYTHONDONTWRITEBYTECODE PYTHONPYCACHEPREFIX DATABASE_URL ORANGE_XDIST_LANE ORANGE_DB_BASE ORANGE_BINDING_EVIDENCE PWD OLDPWD SHLVL _ "
AMBIENT=(SFE_AMBIENT_API_KEY="$SECRET" NQUIRY_AI_PROVIDER=fixture NQUIRY_SESSION_AUTHORITY=fixture NQUIRY_COOKIE_SECURE=0 F04_PROOF_STATE=fixture
  PYTHONPATH=/nonexistent-ambient DATABASE_URL=postgresql://ambient.invalid/ambient_db COVERAGE_PROCESS_START=/nonexistent ORANGE_CATALOG_DB=catalog_fixture TZ=UTC)
FORBIDDEN="SFE_AMBIENT_API_KEY SFE_FIXTURE_API_KEY SFE_PEO_SCRUBBED NQUIRY_AI_PROVIDER NQUIRY_SESSION_AUTHORITY NQUIRY_COOKIE_SECURE F04_PROOF_STATE PYTHONPATH COVERAGE_PROCESS_START"
envcheck() {  # log expected-dbname must-not-have-DATABASE_URL(0|1) -> 0 if the child environment is the boundary
  local log=$1 want_db=$2 no_db=$3 r=0 n names; names=$(grep '^ENVNAME ' "$log" | cut -d' ' -f2)
  [ -n "$names" ] || return 1
  for n in $names; do case "$ALLOWED" in *" $n "*) ;; *) r=1; echo "   outside the allowlist: $n" ;; esac; done
  for n in $FORBIDDEN; do grep -qx "$n" <<< "$names" && { r=1; echo "   ambient variable reached the child: $n"; }; done
  for n in PATH HOME PYTHONNOUSERSITE TZ ORANGE_CATALOG_DB; do grep -qx "$n" <<< "$names" || { r=1; echo "   missing: $n"; }; done
  grep -qx 'CATALOG catalog_fixture' "$log" || { r=1; echo "   catalog selector not passed"; }
  grep -qx "DBNAME $want_db" "$log" || { r=1; echo "   database: $(grep '^DBNAME' "$log")"; }
  [ "$no_db" = 0 ] || ! grep -qx DATABASE_URL <<< "$names" || { r=1; echo "   DATABASE_URL in the xdist controller"; }
  return $r
}
logof() { case "$2" in run) echo "$OUT/$1.d/run.log" ;; *) echo "$OUT/$1.d/${2}_run.log" ;; esac; }
s12() { AMB=("${AMBIENT[@]}"); stage "s12_$id" "$OUT/tool" "$script" "$phase" envnames; stage "s12base_$id" "$OUT/base_tool" "$script" "$phase" envnames; AMB=()
  if [ "$phase" = xdist ]; then envcheck "$(logof "s12_$id" "$phase")" "" 1; else envcheck "$(logof "s12_$id" "$phase")" nquiry_proof_serial_test 0; fi
  check "S12a_GOVERNED_CHILD_ENVIRONMENT_IS_THE_ALLOWLIST[$script $phase]" $?
  grep -qx 'ENVNAME SFE_AMBIENT_API_KEY' "$(logof "s12base_$id" "$phase")" && grep -qx 'ENVNAME NQUIRY_SESSION_AUTHORITY' "$(logof "s12base_$id" "$phase")"
  check "S12b_BASE_RUNNER_REALLY_PASSED_AMBIENT_VARIABLES_TO_THE_CHILD[$script $phase]" $? "(documents the defect)"; }
each s12
conf envnames; ( cd "$OUT" && env ORANGE_PARTITION_DIR="$OUT/s12_partition.d" "${AMBIENT[@]}" bash "$OUT/tool/partition.sh" ) > "$OUT/s12_partition.out" 2>&1
envcheck "$OUT/s12_partition.d/full_raw.txt" "" 1; check "S12a_GOVERNED_CHILD_ENVIRONMENT_IS_THE_ALLOWLIST[partition.sh collect]" $?
conf envnames; ( cd "$OUT" && env ORANGE_SERIAL_DIR="$OUT/s12_noamb.d" bash "$OUT/tool/serial_baseline.sh" run ) > "$OUT/s12_noamb.out" 2>&1
n=$(grep -c '^ENVNAME ' "$OUT/s12_noamb.d/run.log"); ! grep -qE '^ENVNAME (TZ|ORANGE_CATALOG_DB|TMPDIR|LC_ALL)$' "$OUT/s12_noamb.d/run.log" && grep -qx 'ENVNAME PATH' "$OUT/s12_noamb.d/run.log"
check S12c_ALLOWLISTED_VARIABLES_PASS_ONLY_WHEN_SET_NEVER_INVENTED $? "($n names)"

# ---- S13: secret hygiene of this proof (TF-PX-09) -----------------------------------------------------------
extra=$(env -0 | cut -z -d= -f1 | tr '\0' '\n' | grep -vxE 'PATH|HOME|LANG|SFE_PEO_SCRUBBED|SFE_FIXTURE_API_KEY|PWD|OLDPWD|SHLVL|_' | tr '\n' ' ')
[ -z "$extra" ]; check S13a_PROOF_PROCESS_ENVIRONMENT_IS_THE_ALLOWLIST_ONLY $? "($extra)"
n=$(grep -rlF -- "$SECRET" "$OUT" | wc -l); [ "$n" -eq 0 ]; check S13b_NO_CREDENTIAL_VALUE_IN_ANY_EVIDENCE_FILE $? "($n file(s))"

# ---- informational (not gating): the pre / post phases are state-capture phases; their process status is NOT
#      a verdict (their verdict lines are consumed by the chain and by the analyzers). Recorded, not changed here.
for f in serial_baseline.sh parallel_proof.sh; do
  AMB=(PATH="$ROOT/stubbin:$PATH"); stage "info_post_$f" "$OUT/tool" "$f" post verdictfail; AMB=()
  echo "   info: $f post with a FAIL verdict line exits $(rcof "info_post_$f") ($(grep -c '::FAIL' "$OUT/info_post_$f.out") FAIL line(s) on stdout)"
done

echo "STAGE_EXIT_FALSIFIERS::$([ $fails -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
exit $((fails > 0))
