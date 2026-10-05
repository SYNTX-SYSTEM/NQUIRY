#!/usr/bin/env bash
# Falsifiers for the SFE proof-execution observability contract SFE-PEO/1 (sfe_observe.sh, closure: + progress.sh).
# Narrow radius: synthetic children only, including a consumer-shaped runner (captures its child's output, prints an
# evidence block on stdout, exits on its own conjunction). No product test, no product tree, no database, and no
# consumer Field is read, modified or executed.
# SECRET HYGIENE (TF-PX-09): the harness re-executes itself under `env -i` with a fixed allowlist, so no ambient
# application / provider / session credential ever enters the proof process environment, whatever its name. A
# FIXTURE credential is placed in that environment instead; environment preservation is proven by variable
# NAMES and one digest, never by persisted values, and O14 fails if the fixture value reaches any evidence file.
# usage: sfe_observe_falsifiers.sh <new out dir> [<tooling dir under test>] [<base commit>]
set -u
SECRET=S3CRET_FIXTURE_91c2  # fixture only; stands for any credential in the proof process environment
if [ "${SFE_PEO_SCRUBBED:-}" != 1 ]; then
  exec env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 SFE_PEO_SCRUBBED=1 SFE_FIXTURE_API_KEY="$SECRET" bash "${BASH_SOURCE[0]}" "$@"
fi
OUT=${1:?usage: $0 <new out dir> [tooling dir] [base commit]}
T=$(cd "${2:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)
BASE=${3:-26bd82ed38f28a8015026d1fd618961030f3fd1a}  # the lineage commit the ORANGE chain was last proven at
LINEAGE=/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 2; }
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd); cd "$OUT"
unset ORANGE_HEARTBEAT_SECONDS; export SFE_HEARTBEAT_SECONDS=1
OBS=$T/sfe_observe.sh
fails=0
check() { if [ "$2" = 0 ]; then echo "$1::PASS"; else echo "$1::FAIL ${3:-}"; fails=$((fails + 1)); fi; }
ev() { grep -E '^\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] ' "$1"; }
nonev() { grep -vE '^\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] ' "$1"; }
run() { local n=$1; shift; "$@" > "$n.out" 2> "$n.err"; echo $? > "$n.rc"; }  # name, command...
rcof() { cat "$1.rc"; }

# ---- O1: the child's real exit status is the observer's exit status, unmapped ---------------------------
r=0; for c in 0 1 2 3 5 77 124 126 127 255; do run "o1_$c" bash "$OBS" --stage s -- bash -c "exit $c"
  [ "$(rcof "o1_$c")" -eq "$c" ] || { r=1; echo "   child=$c observer=$(rcof "o1_$c")"; }; done
check O1a_CHILD_EXIT_STATUS_IS_RETURNED_UNMAPPED $r
run o1_sig bash "$OBS" --stage s -- bash -c 'kill -TERM $$'; run o1_kill bash "$OBS" --stage s -- bash -c 'kill -KILL $$'
[ "$(rcof o1_sig)" -eq 143 ] && [ "$(rcof o1_kill)" -eq 137 ]; check O1b_SIGNAL_DEATH_OF_THE_CHILD_IS_128_PLUS_N $? "($(rcof o1_sig), $(rcof o1_kill))"
run o1_nf bash "$OBS" --stage s -- no_such_command_sfe_peo; [ "$(rcof o1_nf)" -eq 127 ] && ev o1_nf.err | tail -1 | grep -q 'STAGE_FAIL      stage=s rc=127'
check O1c_UNSTARTABLE_COMMAND_IS_127_AND_REPORTED $? "($(rcof o1_nf))"

# ---- O2: event grammar: START first, exactly one terminal event last, heartbeat in between ----------------
run o2_ok bash "$OBS" --stage slow -- sleep 2.4; run o2_fail bash "$OBS" --stage f -- bash -c 'exit 7'; run o2_to bash "$OBS" --stage t -- timeout 1 sleep 5
r=0; ev o2_ok.err | head -1 | grep -q 'STAGE_START     stage=slow$' || r=1; ev o2_ok.err | tail -1 | grep -qE 'STAGE_END       stage=slow rc=0 elapsed=[0-9]+s$' || r=1
[ "$(ev o2_ok.err | grep -c ' HEARTBEAT       stage=slow elapsed=')" -ge 1 ] || r=1
ev o2_fail.err | tail -1 | grep -q 'STAGE_FAIL      stage=f rc=7' || r=1; ev o2_to.err | tail -1 | grep -q 'STAGE_TIMEOUT   stage=t rc=124' || r=1; [ "$(rcof o2_to)" -eq 124 ] || r=1
for f in o2_ok o2_fail o2_to; do [ "$(ev $f.err | grep -cE ' (STAGE_END|STAGE_FAIL|STAGE_TIMEOUT) ')" -eq 1 ] && [ "$(ev $f.err | grep -c ' STAGE_START ')" -eq 1 ] || r=1; done
check O2_START_HEARTBEAT_AND_EXACTLY_ONE_TERMINAL_EVENT $r

# ---- O3: the child's streams, arguments, environment, working directory and descriptors are untouched -----
child_io='cat; seq 1 5000; printf "no-newline"; echo "to-stderr" >&2'
printf 'line1\nline2\n' | run o3_obs bash "$OBS" --stage io -- bash -c "$child_io"; printf 'line1\nline2\n' | run o3_dir bash -c "$child_io"
cmp -s o3_obs.out o3_dir.out && [ "$(head -2 o3_obs.out | tr '\n' ' ')" = "line1 line2 " ]; check O3a_STDIN_AND_STDOUT_BYTE_IDENTICAL $?
cmp -s <(nonev o3_obs.err) o3_dir.err && [ -z "$(ev o3_obs.out)" ]; check O3b_STDERR_IS_CHILD_STDERR_PLUS_EVENTS_AND_NO_EVENT_ON_STDOUT $?
run o3_ev bash "$OBS" --stage io --events "$OUT/o3.events" -- bash -c 'echo "to-stderr" >&2'; run o3_ev2 bash "$OBS" --stage io2 --events "$OUT/o3.events" -- true
[ "$(cat o3_ev.err)" = "to-stderr" ] && [ ! -s o3_ev2.err ] && [ "$(ev o3.events | grep -c ' STAGE_START ')" -eq 2 ] && [ "$(nonev o3.events | wc -l)" -eq 0 ]
check O3c_EVENTS_FILE_KEEPS_STDERR_BYTE_IDENTICAL_AND_IS_APPENDED $?
args='printf "<%s>" "$@"'; run o3_args_obs bash "$OBS" --stage a -- bash -c "$args" x "two words" "" '*' '$HOME' "--stage" -- "a'b"; run o3_args_dir bash -c "$args" x "two words" "" '*' '$HOME' "--stage" -- "a'b"
cmp -s o3_args_obs.out o3_args_dir.out && grep -q "<two words><><\*><\$HOME><--stage><--><a'b>" o3_args_obs.out; check O3d_ARGUMENTS_VERBATIM $?
# the child reports variable NAMES and one digest over the whole environment (values are never written anywhere)
envfp='env -0 | grep -zvE "^(SHLVL|_)=" | sort -z | sha256sum | cut -d" " -f1; env -0 | cut -z -d= -f1 | grep -zvE "^(SHLVL|_)$" | sort -z | tr "\0" "\n"; pwd; ls /proc/$$/fd | sort -n | tr "\n" " "'
run o3_env_obs bash "$OBS" --stage e -- bash -c "$envfp"; run o3_env_dir bash -c "$envfp"
diff o3_env_obs.out o3_env_dir.out > o3_env.diff && grep -qx 'SFE_FIXTURE_API_KEY' o3_env_obs.out && [ "$(head -1 o3_env_obs.out | wc -c)" -eq 65 ]
check O3e_ENVIRONMENT_CWD_AND_DESCRIPTORS_UNCHANGED $? "(names + digest; a credential in the environment reaches the child unchanged)"

# ---- O4: observations are never verdicts; nothing of the command line or of secrets is echoed --------------
run o4 env SFE_TOKEN=$SECRET bash "$OBS" -- bash -c "echo $SECRET > /dev/null; sleep 1.3" "$SECRET"
run o4b bash "$OBS" --stage "pw=$SECRET x" -- true
r=0; for f in *.err *.events; do
  ev "$f" | grep -vE '^\[[0-9:]{8}\] (STAGE_START|HEARTBEAT|STAGE_END|STAGE_FAIL|STAGE_TIMEOUT) +stage=[^ ]+( (rc|elapsed|pytest_progress)=[^ ]+)*$' | grep -q . && { r=1; echo "   outside the grammar: $f"; }
  ev "$f" | grep -qiE 'PASS|VERDICT|PROOF_|SUCCESS|GREEN' && { r=1; echo "   verdict word: $f"; }; done
check O4a_EVENTS_STAY_INSIDE_THE_GRAMMAR_AND_NEVER_CARRY_A_VERDICT $r
! grep -q "$SECRET" o4.err o4b.err && ev o4b.err | head -1 | grep -q 'stage=<redacted>'; check O4b_NO_COMMAND_LINE_NO_SECRET_IN_EVENTS $?

# ---- O5: heartbeat progress from a log the consumer names (optional) --------------------------------------
run o5 bash "$OBS" --stage prog --progress-log "$OUT/o5.log" -- bash -c "echo 'tests/a.py ....  [ 42%]' > '$OUT/o5.log'; sleep 2.4"
ev o5.err | grep -q ' HEARTBEAT       stage=prog elapsed=[0-9]*s pytest_progress=42%'; check O5_OPTIONAL_PROGRESS_FROM_A_NAMED_LOG $?

# ---- O6: a consumer-shaped runner (opaque capture, evidence block on stdout, own exit conjunction) ----------
cat > consumer_runner.sh <<'RUNNER'
#!/usr/bin/env bash
# synthetic consumer runner: the shape of a Field's regression runner (not a copy of any Field's script)
set -uo pipefail
echo "HEAD: synthetic"
LIVE_OUT="$(bash -c 'sleep 2.4; echo "FAILED tests/x.py::t - boom"; echo "3 passed in 2.40s"; exit '"${SYN_RC:-0}" 2>&1)"
LIVE_CODE=$?
echo "LIVE_RESULT: $(printf '%s\n' "$LIVE_OUT" | tail -1)"; echo "LIVE_EXIT_CODE: $LIVE_CODE"
echo "TREE_UNCHANGED_DURING_RUN: true"
[ "$LIVE_CODE" -eq 0 ]
RUNNER
for c in 0 1; do run "o6_obs_$c" env SYN_RC=$c bash "$OBS" --stage closure_regression -- bash consumer_runner.sh; run "o6_dir_$c" env SYN_RC=$c bash consumer_runner.sh; done
r=0; for c in 0 1; do cmp -s "o6_obs_$c.out" "o6_dir_$c.out" || r=1; [ "$(rcof "o6_obs_$c")" = "$(rcof "o6_dir_$c")" ] || r=1; done; [ "$(rcof o6_obs_1)" -eq 1 ] && [ "$(rcof o6_obs_0)" -eq 0 ] || r=1
check O6a_CONSUMER_EVIDENCE_BLOCK_AND_EXIT_STATUS_IDENTICAL_WITH_AND_WITHOUT_OBSERVER $r
[ ! -s o6_dir_0.err ] && [ "$(ev o6_obs_0.err | grep -c ' HEARTBEAT ')" -ge 1 ] && ev o6_obs_1.err | tail -1 | grep -q 'STAGE_FAIL      stage=closure_regression rc=1'
check O6b_OPAQUE_CONSUMER_RUN_BECOMES_OBSERVABLE_WITHOUT_CHANGING_THE_CONSUMER $? "(direct run: $(wc -c < o6_dir_0.err) bytes of liveness; observed: $(ev o6_obs_0.err | grep -c ' HEARTBEAT ') heartbeat(s))"

# ---- O7: nested observation composes (a Field may observe its own inner stages) ---------------------------
run o7 bash "$OBS" --stage outer -- bash -c "bash '$OBS' --stage inner_a -- true; bash '$OBS' --stage inner_b -- bash -c 'exit 6'"
[ "$(rcof o7)" -eq 6 ] && [ "$(ev o7.err | sed -E 's/^\[[0-9:]+\] //; s/ elapsed=[^ ]+//; s/  +/ /' | tr '\n' ';')" = \
  "STAGE_START stage=outer;STAGE_START stage=inner_a;STAGE_END stage=inner_a rc=0;STAGE_START stage=inner_b;STAGE_FAIL stage=inner_b rc=6;STAGE_FAIL stage=outer rc=6;" ]
check O7_NESTED_OBSERVATION_COMPOSES $? "($(rcof o7))"

# ---- O8: the observer never stops the proof; an ending observer is never success; no heartbeat survives ----
bash "$OBS" --stage termed -- bash -c 'echo $$ > o8.child; sleep 5; echo done > o8.done' 2> o8.err & op=$!
sleep 1.6; kill -TERM "$op"; wait "$op"; orc=$?; sleep 0.3; cp=$(cat o8.child); alive=1; kill -0 "$cp" 2>/dev/null || alive=0
hb1=$(ev o8.err | grep -c ' HEARTBEAT '); sleep 2.2; hb2=$(ev o8.err | grep -c ' HEARTBEAT '); sleep 2.5
[ "$orc" -eq 143 ] && [ "$alive" -eq 1 ] && [ "$hb1" -eq "$hb2" ] && [ -f o8.done ] && ! ev o8.err | grep -qE ' (STAGE_END|STAGE_FAIL|STAGE_TIMEOUT) '
check O8a_TERMINATED_OBSERVER_IS_NONZERO_REPORTS_NO_END_AND_LEAVES_THE_PROOF_RUNNING $? "(rc=$orc child_alive=$alive hb=$hb1/$hb2)"
bash "$OBS" --stage killed -- bash -c 'echo $$ > o8k.child; sleep 30' 2> o8k.err & op=$!
sleep 1.6; kill -KILL "$op"; wait "$op" 2>/dev/null; sleep 2.4; cp=$(cat o8k.child); alive=1; kill -0 "$cp" 2>/dev/null || alive=0
hb1=$(ev o8k.err | grep -c ' HEARTBEAT '); sleep 2.2; hb2=$(ev o8k.err | grep -c ' HEARTBEAT '); kill "$cp" 2>/dev/null
[ "$alive" -eq 1 ] && [ "$hb1" -eq "$hb2" ]; check O8b_KILLED_OBSERVER_LEAVES_NO_HEARTBEAT_AND_THE_PROOF_RUNNING $? "(child_alive=$alive hb=$hb1/$hb2)"

# ---- O9: a failing event sink never changes what runs or what is returned ----------------------------------
bash "$OBS" --stage closed -- bash -c 'echo ran > o9.ran; exit 3' 2>&-; a=$?
run o9b bash "$OBS" --stage badsink --events /nonexistent-sfe-peo/dir/events -- bash -c 'echo ran > o9b.ran; exit 4'
[ "$a" -eq 3 ] && [ -f o9.ran ] && [ "$(rcof o9b)" -eq 4 ] && [ -f o9b.ran ] && ev o9b.err | grep -q 'STAGE_FAIL      stage=badsink rc=4'
check O9_EVENT_SINK_FAILURE_NEVER_CHANGES_THE_RUN_OR_ITS_STATUS $? "(closed stderr rc=$a, bad sink rc=$(rcof o9b))"

# ---- O10: usage errors run nothing, emit no event, exit 2 ---------------------------------------------------
r=0; i=0; for a in "" "--stage x" "--stage x --" "--bogus -- true" "true" "--events"; do i=$((i + 1))
  # shellcheck disable=SC2086
  run "o10_$i" bash "$OBS" $a; [ "$(rcof "o10_$i")" -eq 2 ] && [ -z "$(ev "o10_$i.err")" ] && grep -q '^usage: ' "o10_$i.err" || { r=1; echo "   args='$a' rc=$(rcof "o10_$i")"; }; done
check O10_USAGE_ERROR_IS_2_RUNS_NOTHING_EMITS_NOTHING $r

# ---- O11: the closure is exactly sfe_observe.sh + progress.sh, with nothing ORANGE-target-specific ---------
mkdir closure; cp "$T/sfe_observe.sh" "$T/progress.sh" closure/
run o11 bash closure/sfe_observe.sh --stage c -- bash -c 'exit 9'; [ "$(rcof o11)" -eq 9 ] && ev o11.err | tail -1 | grep -q 'STAGE_FAIL      stage=c rc=9'
check O11a_SELF_CONTAINED_CLOSURE_OF_TWO_FILES $? "($(rcof o11))"
! grep -nE '/home/|venv|DATABASE|nquiry|ORANGE_|serial_baseline|parallel_proof|final_closure|psql|xdist' "$T/sfe_observe.sh"
check O11b_NO_TARGET_ENVIRONMENT_OR_FIELD_SPECIFIC_REFERENCE $?
[ "$(grep -cE '^[^#]*printf' "$T/sfe_observe.sh")" -eq 0 ] && [ "$(grep -cE '^prog_begin ' "$T/sfe_observe.sh")" -eq 1 ] && [ "$(grep -cE '^prog_end ' "$T/sfe_observe.sh")" -eq 1 ] \
  && ! grep -qE '^[^#]*(prog_init|prog_verdicts|prog_finish)' "$T/sfe_observe.sh"
check O11c_ONE_EVENT_IMPLEMENTATION_AND_NO_VERDICT_MACHINERY $?

# ---- O12: the proven ORANGE chain is untouched ---------------------------------------------------------------
r=0; for f in progress.sh final_closure.sh serial_baseline.sh parallel_proof.sh partition.sh analyze_serial.py aggregate.py run_aggregate.py; do
  cmp -s "$T/$f" <(git -C "$LINEAGE" show "$BASE:$f") || { r=1; echo "   changed: $f"; }; done
check O12_ORANGE_CHAIN_AND_HELPER_BYTE_IDENTICAL_TO_BASE $r

# ---- O13: no orphan process (by recorded PID and by this run's own paths) ------------------------------------
sleep 1.5
n=$(ps -eo args | grep -E -- "(sfe_observe\.sh|consumer_runner\.sh) " | grep -F -- "$OUT" | grep -v grep | wc -l)
m=$(ps -eo args | grep -E -- "$T/sfe_observe\.sh --stage (termed|killed|slow|prog|outer|closure_regression) " | grep -v grep | wc -l)
[ "$n" -eq 0 ] && [ "$m" -eq 0 ]; check O13_NO_ORPHAN_PROCESS $? "($n, $m)"

# ---- O14: secret hygiene of the proof itself ------------------------------------------------------------------
extra=$(env -0 | cut -z -d= -f1 | tr '\0' '\n' | grep -vxE 'PATH|HOME|LANG|SFE_PEO_SCRUBBED|SFE_FIXTURE_API_KEY|SFE_HEARTBEAT_SECONDS|PWD|OLDPWD|SHLVL|_' | tr '\n' ' ')
[ -z "$extra" ]; check O14a_PROOF_PROCESS_ENVIRONMENT_IS_THE_ALLOWLIST_ONLY $? "($extra)"
n=$(grep -rlF -- "$SECRET" "$OUT" | wc -l); [ "$n" -eq 0 ] && [ "$SFE_FIXTURE_API_KEY" = "$SECRET" ]
check O14b_NO_CREDENTIAL_VALUE_FROM_THE_ENVIRONMENT_IN_ANY_EVIDENCE_FILE $? "($n file(s))"
# the publication gate: detects a planted environment value by variable name, never prints it, passes on clean evidence
mkdir gate_planted; printf 'x=%s\n' "$SFE_FIXTURE_API_KEY" > gate_planted/leak.txt; mkdir gate_clean; echo "clean" > gate_clean/a.txt
python3 "$T/evidence_secret_gate.py" gate_planted > gate_planted.log 2>&1; g1=$?; python3 "$T/evidence_secret_gate.py" gate_clean > gate_clean.log 2>&1; g2=$?
rm -rf gate_planted  # the planted fixture is not evidence
[ "$g1" -eq 1 ] && grep -q 'environment value of SFE_FIXTURE_API_KEY found in leak.txt' gate_planted.log && ! grep -q "$SECRET" gate_planted.log gate_clean.log \
  && [ "$g2" -eq 0 ] && grep -q '^EVIDENCE_SECRET_GATE::PASS' gate_clean.log
check O14c_PUBLICATION_GATE_DETECTS_AN_ENVIRONMENT_VALUE_WITHOUT_PRINTING_IT $? "(planted rc=$g1, clean rc=$g2)"
# reachable history: a value committed once and deleted by the next commit is still published with the history
G=(git -c user.name=fixture -c user.email=fixture@invalid -c init.defaultBranch=main -c commit.gpgsign=false)
"${G[@]}" init -q gate_repo; printf 'x=%s\n' "$SFE_FIXTURE_API_KEY" > gate_repo/leak.txt; "${G[@]}" -C gate_repo add leak.txt; "${G[@]}" -C gate_repo commit -q -m planted
"${G[@]}" -C gate_repo rm -q leak.txt; echo clean > gate_repo/a.txt; "${G[@]}" -C gate_repo add a.txt; "${G[@]}" -C gate_repo commit -q -m removed
python3 "$T/evidence_secret_gate.py" gate_repo > gate_repo_tree.log 2>&1; g3=$?; python3 "$T/evidence_secret_gate.py" --rev HEAD gate_repo > gate_repo_history.log 2>&1; g4=$?
python3 "$T/evidence_secret_gate.py" --rev HEAD~1 gate_repo > /dev/null 2>&1; g5=$?
rm -rf gate_repo  # the planted fixture repository is not evidence
[ "$g3" -eq 0 ] && [ "$g4" -eq 1 ] && [ "$g5" -eq 1 ] && grep -q 'environment value of SFE_FIXTURE_API_KEY found in reachable blob' gate_repo_history.log && ! grep -q "$SECRET" gate_repo_history.log gate_repo_tree.log
check O14e_GATE_SEES_A_VALUE_THAT_ONLY_REACHABLE_HISTORY_STILL_HOLDS $? "(tree rc=$g3, history rc=$g4)"
python3 "$T/evidence_secret_gate.py" "$OUT" > gate_own_evidence.log 2>&1; check O14d_THIS_RUNS_OWN_EVIDENCE_PASSES_THE_GATE $? "($(tail -1 gate_own_evidence.log))"

echo "SFE_OBSERVE_FALSIFIERS::$([ $fails -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
exit $((fails > 0))
