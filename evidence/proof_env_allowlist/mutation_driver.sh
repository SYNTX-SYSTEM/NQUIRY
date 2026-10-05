#!/usr/bin/env bash
# Mutation proof for the proof-environment allowlist (TF-PX-10) and, because the harness was reworked for it, again for
# the STAGE_EXIT_STATUS contract: every mutant must be KILLED by stage_exit_falsifiers.sh.
# usage: mutation_driver.sh <scratch dir for mutant tooling copies>
set -u
E=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); L=$(cd "$E/../.." && pwd); W=${1:?scratch dir}
BASE=3cab23b27e0d75cd7ce2aebd53c14caf9fa64e37  # last lineage commit with the denylist H()
mkdir -p "$E/mutants" "$W"; : > "$E/mutation.log"; killed=0; total=0
mutant() {  # name, stdin = python body using sub(file, old, new[, count]) and old_H(file)
  local name=$1 d=$W/$1; total=$((total + 1)); rm -rf "$d"; mkdir -p "$d"
  [ -e "$E/mutants/$name" ] && { echo "== $name: NOT RUN (evidence directory exists; a refusal is not a kill)" >> "$E/mutation.log"; return; }
  find "$L" -maxdepth 1 -type f -exec cp {} "$d/" \;
  ( cd "$d" && L="$L" BASE="$BASE" python3 -c '
import os, pathlib, re, subprocess, sys
HRE = re.compile(r"^H\(\) \{.*?\"\$@\"; \}\n", re.S | re.M)
def sub(f, old, new, count=1):
    p = pathlib.Path(f); s = p.read_text(); assert s.count(old) == count, (f, old, s.count(old)); p.write_text(s.replace(old, new))
def old_H(f):
    base = subprocess.run(["git", "-C", os.environ["L"], "show", os.environ["BASE"] + ":" + f], capture_output=True, text=True, check=True).stdout
    p = pathlib.Path(f); s = p.read_text(); new, old = HRE.search(s), HRE.search(base); assert new and old, f
    p.write_text(s.replace(new.group(0), old.group(0)))
exec(sys.stdin.read())' ) || { echo "== $name: MUTATION NOT APPLIED" >> "$E/mutation.log"; return; }
  ( cd "$d" && for f in *; do cmp -s "$f" "$L/$f" || diff "$L/$f" "$f"; done ) > "$E/mutants/$name.mutation.diff"
  bash "$L/stage_exit_falsifiers.sh" "$E/mutants/$name" "$d" > "$E/mutants/$name.log" 2>&1; local rc=$?
  if [ $rc -eq 1 ] && [ -s "$E/mutants/$name.mutation.diff" ]; then killed=$((killed + 1)); echo "== $name: rc=$rc -> KILLED" >> "$E/mutation.log"
  else echo "== $name: rc=$rc -> SURVIVED" >> "$E/mutation.log"; fi
  grep -E '::FAIL' "$E/mutants/$name.log" | sed 's/^/    /' >> "$E/mutation.log"
}
R3="serial_baseline.sh parallel_proof.sh partition.sh"; R="serial_baseline.sh parallel_proof.sh"
# ---- proof-environment allowlist
mutant MA1_denylist_restored <<PY
for f in "$R3".split(): old_H(f)
PY
mutant MA2_allowlist_passes_a_credential_variable <<PY
for f in "$R3".split(): sub(f, "TZ TMPDIR ORANGE_CATALOG_DB; do", "TZ TMPDIR ORANGE_CATALOG_DB SFE_AMBIENT_API_KEY; do")
PY
mutant MA3_allowlist_passes_a_variable_the_target_reads <<PY
for f in "$R3".split(): sub(f, "TZ TMPDIR ORANGE_CATALOG_DB; do", "TZ TMPDIR ORANGE_CATALOG_DB NQUIRY_SESSION_AUTHORITY; do")
PY
mutant MA4_catalog_selector_dropped <<PY
for f in "$R".split(): sub(f, "TZ TMPDIR ORANGE_CATALOG_DB; do", "TZ TMPDIR; do")
PY
mutant MA5_env_not_cleared <<PY
for f in "$R3".split(): sub(f, 'env -i "\${a[@]}"', 'env "\${a[@]}"')
PY
mutant MA6_only_the_serial_runner_converted <<PY
for f in ("parallel_proof.sh", "partition.sh"): old_H(f)
PY
mutant MA7_partition_collection_not_converted <<PY
old_H("partition.sh")
PY
mutant MA8_bytecode_prefix_dropped_from_the_parallel_child <<PY
sub("parallel_proof.sh", 'PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=\$PYC "\$@"; }', 'PYTHONNOUSERSITE=1 "\$@"; }')
PY
# ---- STAGE_EXIT_STATUS (same mutants as evidence/stage_exit_status/, against the reworked harness)
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
