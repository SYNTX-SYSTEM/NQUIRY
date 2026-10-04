#!/usr/bin/env bash
# Mutation proof for STAGE_EXIT_STATUS: every mutant of the tooling must be KILLED by stage_exit_falsifiers.sh.
# usage: mutation_driver.sh <scratch dir for mutant tooling copies>   (outputs: mutants/<name>/, mutants/<name>.log, mutation.log next to this file)
set -u
E=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); L=$(cd "$E/../.." && pwd); W=${1:?scratch dir}
mkdir -p "$E/mutants" "$W"; : > "$E/mutation.log"; killed=0; total=0
mutant() {  # name, stdin = python body operating on files in cwd via sub(file, old, new)
  local name=$1 d=$W/$1; total=$((total + 1)); rm -rf "$d"; mkdir -p "$d"
  find "$L" -maxdepth 1 -type f -exec cp {} "$d/" \;
  ( cd "$d" && python3 -c '
import pathlib, sys
def sub(f, old, new, count=1):
    p = pathlib.Path(f); s = p.read_text(); assert s.count(old) == count, (f, old, s.count(old)); p.write_text(s.replace(old, new))
exec(sys.stdin.read())' ) || { echo "== $name: MUTATION NOT APPLIED" >> "$E/mutation.log"; return; }
  ( cd "$d" && for f in *; do cmp -s "$f" "$L/$f" || diff "$L/$f" "$f"; done ) > "$E/mutants/$name.mutation.diff"
  bash "$L/stage_exit_falsifiers.sh" "$E/mutants/$name" "$d" > "$E/mutants/$name.log" 2>&1; local rc=$?
  if [ $rc -ne 0 ] && [ -s "$E/mutants/$name.mutation.diff" ]; then killed=$((killed + 1)); echo "== $name: rc=$rc -> KILLED" >> "$E/mutation.log"
  else echo "== $name: rc=$rc -> SURVIVED" >> "$E/mutation.log"; fi
  grep -E '::FAIL' "$E/mutants/$name.log" | sed 's/^/    /' >> "$E/mutation.log"
}
R="serial_baseline.sh parallel_proof.sh"
mutant MS1_always_exit_0 <<PY
for f in "$R".split(): sub(f, "&& exit 0; exit 1; }", "&& exit 0; exit 0; }")
PY
mutant MS2_inverted_exit_status <<PY
for f in "$R".split(): sub(f, '= 0 ] && exit 0; exit 1; }', '!= 0 ] && exit 0; exit 1; }')
PY
mutant MS3_only_raw_code_1_is_failure <<PY
for f in "$R".split(): sub(f, '= 0 ] && exit 0; exit 1; }', '= 1 ] && exit 1; exit 0; }')
PY
mutant MS4_raw_code_propagated_as_status <<PY
for f in "$R".split(): sub(f, '&& exit 0; exit 1; }', '&& exit 0; exit "\$(cat "\$1")"; }')
PY
mutant MS5a_recorded_truth_forced_to_0 <<PY
sub("serial_baseline.sh", 'echo \$? > "\$OUT/run_exit_code.txt"', 'echo 0 > "\$OUT/run_exit_code.txt"')
sub("parallel_proof.sh", 'echo "\$rc" > "\$OUT/\${label}_exit_code.txt"', 'echo 0 > "\$OUT/\${label}_exit_code.txt"')
PY
mutant MS5b_recorded_raw_code_normalized_to_1 <<PY
sub("serial_baseline.sh", 'echo \$? > "\$OUT/run_exit_code.txt"', 'echo \$(( \$? != 0 )) > "\$OUT/run_exit_code.txt"')
sub("parallel_proof.sh", 'echo "\$rc" > "\$OUT/\${label}_exit_code.txt"', 'echo "\$((rc != 0))" > "\$OUT/\${label}_exit_code.txt"')
PY
mutant MS6_status_before_the_visible_summary <<PY
a = '    echo "exit=\$(cat "\$OUT/run_exit_code.txt")"; tail -1 "\$OUT/run.log"\n'; c = '    stage_exit "\$OUT/run_exit_code.txt"  # STAGE_EXIT_STATUS\n'
sub("serial_baseline.sh", a + c, c + a)
for ph in ("xdist", "serial"):
    a = f'    tail -1 "\$OUT/{ph}_run.log"\n'; c = f'    stage_exit "\$OUT/{ph}_exit_code.txt"  # STAGE_EXIT_STATUS\n'
    sub("parallel_proof.sh", a + c, c + a)
PY
mutant MS7_parallel_runner_not_repaired <<PY
for ph in ("xdist", "serial"): sub("parallel_proof.sh", f'    stage_exit "\$OUT/{ph}_exit_code.txt"  # STAGE_EXIT_STATUS\n', "")
PY
mutant MS8_chain_consumes_the_stage_status <<PY
sub("final_closure.sh", 'bash "\$P/parallel_proof.sh" xdist\n', 'bash "\$P/parallel_proof.sh" xdist || exit 1\n')
PY
mutant MS9_parallel_selection_changed <<PY
sub("parallel_proof.sh", "-n 4 --dist load --max-worker-restart=0 \$(printf", "-n 2 --dist load --max-worker-restart=0 \$(printf")
PY
mutant MS10_absent_exit_code_file_is_success <<PY
for f in "$R".split(): sub(f, '''< "\$1" 2>/dev/null)" = 0 ]''', '''< "\$1" 2>/dev/null || echo 0)" = 0 ]''')
PY
echo "MUTATION_RESULT::$([ $killed -eq $total ] && echo PASS || echo FAIL) ($killed/$total killed)" >> "$E/mutation.log"
[ $killed -eq $total ]
