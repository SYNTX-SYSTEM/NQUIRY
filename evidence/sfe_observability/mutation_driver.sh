#!/usr/bin/env bash
# Mutation proof for SFE-PEO/1: every mutant of the observer (or of its sourced helper) must be KILLED by
# sfe_observe_falsifiers.sh. usage: mutation_driver.sh <scratch dir for mutant tooling copies>
set -u
E=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); L=$(cd "$E/../.." && pwd); W=${1:?scratch dir}
mkdir -p "$E/mutants" "$W"; : > "$E/mutation.log"; killed=0; total=0
mutant() {  # name, stdin = python body using sub(file, old, new)
  local name=$1 d=$W/$1; total=$((total + 1)); rm -rf "$d"; mkdir -p "$d"
  [ -e "$E/mutants/$name" ] && { echo "== $name: NOT RUN (evidence directory exists; a refusal is not a kill)" >> "$E/mutation.log"; return; }
  find "$L" -maxdepth 1 -type f -exec cp {} "$d/" \;
  ( cd "$d" && python3 -c '
import pathlib, sys
def sub(f, old, new, count=1):
    p = pathlib.Path(f); s = p.read_text(); assert s.count(old) == count, (f, old, s.count(old)); p.write_text(s.replace(old, new))
exec(sys.stdin.read())' ) || { echo "== $name: MUTATION NOT APPLIED" >> "$E/mutation.log"; return; }
  ( cd "$d" && for f in *; do cmp -s "$f" "$L/$f" || diff "$L/$f" "$f"; done ) > "$E/mutants/$name.mutation.diff"
  bash "$L/sfe_observe_falsifiers.sh" "$E/mutants/$name" "$d" > "$E/mutants/$name.log" 2>&1; local rc=$?
  if [ $rc -ne 0 ] && [ -s "$E/mutants/$name.mutation.diff" ]; then killed=$((killed + 1)); echo "== $name: rc=$rc -> KILLED" >> "$E/mutation.log"
  else echo "== $name: rc=$rc -> SURVIVED" >> "$E/mutation.log"; fi
  grep -E '::FAIL' "$E/mutants/$name.log" | sed 's/^/    /' >> "$E/mutation.log"
}
mutant MO1_exit_always_0 <<'PY'
sub("sfe_observe.sh", 'exit "$rc"\n', 'exit 0\n')
PY
mutant MO2_exit_mapped_to_0_or_1 <<'PY'
sub("sfe_observe.sh", 'exit "$rc"\n', 'exit $((rc != 0))\n')
PY
mutant MO3_events_on_stdout <<'PY'
sub("sfe_observe.sh", 'exec 9>&2  #', 'exec 9>&1  #')
PY
mutant MO4_terminal_event_always_rc_0 <<'PY'
sub("sfe_observe.sh", 'prog_end "$stage" "$rc" >&9', 'prog_end "$stage" 0 >&9')
PY
mutant MO5_stdin_dropped <<'PY'
sub("sfe_observe.sh", '"$@" 9>&-\n', '"$@" 9>&- < /dev/null\n')
PY
mutant MO6_arguments_reparsed <<'PY'
sub("sfe_observe.sh", '"$@" 9>&-\n', 'eval "$*" 9>&-\n')
PY
mutant MO7_command_line_echoed <<'PY'
sub("sfe_observe.sh", '"$@" 9>&-\n', 'echo "[00:00:00] COMMAND         $*" >&9\n"$@" 9>&-\n')
PY
mutant MO8_event_descriptor_leaked_to_child <<'PY'
sub("sfe_observe.sh", '"$@" 9>&-\n', '"$@"\n')
PY
mutant MO9_heartbeat_carries_a_verdict <<'PY'
sub("progress.sh", 'else prog_event HEARTBEAT "stage=$1" "elapsed=${el}s"; fi', 'else prog_event HEARTBEAT "stage=$1" "elapsed=${el}s" "status=PASS"; fi')
PY
mutant MO10_terminated_observer_stops_the_proof <<'PY'
sub("sfe_observe.sh", "trap '_prog_hb_stop' EXIT\n", "trap '_prog_hb_stop' EXIT\ntrap 'pkill -P $$; exit 143' TERM\n")
PY
mutant MO11_usage_error_exits_0 <<'PY'
sub("sfe_observe.sh", '>&2; exit 2; }', '>&2; exit 0; }')
PY
mutant MO12_unusable_event_sink_aborts_the_run <<'PY'
sub("sfe_observe.sh", 'if [ -n "$evfile" ] && { : >> "$evfile"; } 2>/dev/null; then exec 9>>"$evfile"; fi', 'if [ -n "$evfile" ]; then { : >> "$evfile"; } 2>/dev/null || exit 1; exec 9>>"$evfile"; fi')
PY
mutant MO13_observer_reports_a_verdict_on_success <<'PY'
sub("sfe_observe.sh", 'prog_end "$stage" "$rc" >&9', 'prog_end "$stage" "$rc" >&9; [ "$rc" -ne 0 ] || echo "[00:00:00] VERDICT         value=PASS" >&9')
PY
mutant MO14_verdict_machinery_installed <<'PY'
sub("sfe_observe.sh", 'prog_begin "$stage" "$plog" >&9 < /dev/null', 'prog_init observed >&9\nprog_begin "$stage" "$plog" >&9 < /dev/null')
PY
mutant MO15_observer_dumps_the_environment_into_events <<'PY'
sub("sfe_observe.sh", '"$@" 9>&-\n', 'env >&9\n"$@" 9>&-\n')
PY
mutant MO16_publication_gate_always_passes <<'PY'
sub("evidence_secret_gate.py", "    return 1 if hits else 0\n", "    return 0\n", count=2)
PY
mutant MO17_publication_gate_prints_the_value <<'PY'
sub("evidence_secret_gate.py", '        print(f"  environment value of {name} found in {path}")', '        print(f"  environment value of {name} = {os.environ[name]} found in {path}")')
PY
mutant MO18_gate_ignores_reachable_history <<'PY'
sub("evidence_secret_gate.py", '        if kind == b"blob":', '        if kind == b"blob" and False:')
PY
echo "MUTATION_RESULT::$([ $killed -eq $total ] && echo PASS || echo FAIL) ($killed/$total killed)" >> "$E/mutation.log"
[ $killed -eq $total ]
