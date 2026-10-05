# ORANGE structured progress + heartbeat (sourced by final_closure.sh). OBSERVABILITY ONLY.
#
# Laws: observability != proof semantics; heartbeat != success; progress != verdict; no output != failure.
# - Events go to the chain's stdout, one line each: [HH:MM:SS] EVENT  key=value ...
#   Timestamps are elapsed time since PROOF_START and are never part of proof truth.
# - STAGE_START / STAGE_END / STAGE_FAIL / STAGE_TIMEOUT report process facts (the child's exit code). They
#   never say PASS: the canonical stage drivers exit 0 whatever pytest did, so the real exit code is read from
#   the stage's own *_exit_code.txt, and "unobserved" is reported where the chain itself discards it.
# - HEARTBEAT is a liveness signal only (stage, elapsed, optional pytest progress %). It never carries a
#   verdict. A hang shows as growing elapsed time without a STAGE_END, so it is never masked.
# - VERDICT copies PASS / FAIL only from the verdict lines the chain already writes (NAME::PASS|FAIL). A
#   required verdict that is absent is reported MISSING and counts as a failure.
# - PROOF_END verdict=PASS only if the final verdict step was reached, every stage exit was 0 (or
#   unobserved), at least one verdict was read and no verdict is FAIL or MISSING. If the chain exits early,
#   the EXIT trap reports PROOF_END verdict=FAIL. If emitting fails, nothing is reported (never a PASS).
# - The heartbeat subshell is stopped by prog_end and by the EXIT trap, and it exits by itself within one
#   interval if the chain process disappears (no orphan).
# - Field values are restricted to a safe character set; any value that looks like a credential, URL or
#   connection string is replaced by <redacted>.
# Interval: ORANGE_HEARTBEAT_SECONDS (default 30).

_PROG_T0=$(date +%s)
_PROG_HB=""
_PROG_STAGE=""
_PROG_STAGE_T0=0
_PROG_FAILS=0
_PROG_VERDICTS=0
_PROG_DONE=0
_PROG_HB_S=${ORANGE_HEARTBEAT_SECONDS:-30}

_prog_clock() {
  local s=$(( $(date +%s) - _PROG_T0 ))
  printf '%02d:%02d:%02d' $((s / 3600)) $((s % 3600 / 60)) $((s % 60))
}

_prog_safe() {  # one key=value field -> safe field
  local f=$1 k v
  k=${f%%=*}; v=${f#*=}
  [ "$k" = "$f" ] && v=""
  if [[ ! $k =~ ^[A-Za-z0-9_.]+$ ]] || [[ $k =~ [Pp][Aa][Ss][Ss]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Tt][Oo][Kk][Ee][Nn]|[Cc][Oo][Oo][Kk][Ii][Ee]|[Kk][Ee][Yy]|[Aa][Uu][Tt][Hh]|[Cc][Rr][Ee][Dd]|[Dd][Ss][Nn]|[Uu][Rr][Ll] ]]; then
    printf '%s' "<redacted>"; return
  fi
  local safe='^[][A-Za-z0-9_.:%/+-]*$'
  if [[ $v == *"@"* || $v == *"://"* || ! $v =~ $safe ]]; then v="<redacted>"; fi
  if [ "$k" = "$f" ]; then printf '%s' "$k"; else printf '%s=%s' "$k" "$v"; fi
}

prog_event() {  # EVENT [key=value ...]
  local ev=$1 out f; shift
  [[ $ev =~ ^[A-Z_]+$ ]] || ev=EVENT
  out=""
  for f in "$@"; do out="$out $(_prog_safe "$f")"; done
  printf '[%s] %-15s%s\n' "$(_prog_clock)" "$ev" "$out" 2>/dev/null || true
}

_prog_heartbeat() {  # stage start log parent
  local sp=""
  trap '[ -n "$sp" ] && kill "$sp" 2>/dev/null; exit 0' TERM
  while :; do
    sleep "$_PROG_HB_S" & sp=$!
    wait "$sp"
    kill -0 "$4" 2>/dev/null || exit 0  # the chain is gone: never outlive it
    local pr="" el=$(( $(date +%s) - $2 ))
    if [ -n "$3" ] && [ -r "$3" ]; then
      pr=$(tail -c 4096 "$3" 2>/dev/null | grep -oE '\[ *[0-9]{1,3}%\]' | tail -1 | tr -dc '0-9')
    fi
    if [ -n "$pr" ]; then prog_event HEARTBEAT "stage=$1" "elapsed=${el}s" "pytest_progress=${pr}%"
    else prog_event HEARTBEAT "stage=$1" "elapsed=${el}s"; fi
  done
}

_prog_hb_stop() {
  if [ -n "$_PROG_HB" ]; then
    kill "$_PROG_HB" 2>/dev/null
    wait "$_PROG_HB" 2>/dev/null
    _PROG_HB=""
  fi
}

prog_init() {  # name [key=value ...]
  local name=$1; shift
  trap '_prog_on_exit' EXIT
  prog_event PROOF_START "chain=$name" "$@"
}

prog_begin() {  # stage [pytest log for progress]
  _prog_hb_stop
  _PROG_STAGE=$1; _PROG_STAGE_T0=$(date +%s)
  prog_event STAGE_START "stage=$1"
  _prog_heartbeat "$1" "$_PROG_STAGE_T0" "${2:-}" "$$" &
  _PROG_HB=$!
}

prog_end() {  # stage rc|unobserved -- the child's real exit code
  local stage=$1 rc=${2:-unobserved} el
  _prog_hb_stop
  el=$(( $(date +%s) - _PROG_STAGE_T0 ))
  local els="${el}s"; [ "$_PROG_STAGE_T0" -eq 0 ] && els="n/a"  # prog_end without prog_begin: no elapsed time is invented
  if [ "$rc" = "unobserved" ]; then
    prog_event STAGE_END "stage=$stage" "rc=unobserved" "elapsed=$els"
  elif [[ ! $rc =~ ^[0-9]+$ ]]; then
    _PROG_FAILS=$((_PROG_FAILS + 1)); prog_event STAGE_FAIL "stage=$stage" "rc=invalid" "elapsed=$els"
  elif [ "$rc" -eq 124 ]; then
    _PROG_FAILS=$((_PROG_FAILS + 1)); prog_event STAGE_TIMEOUT "stage=$stage" "rc=$rc" "elapsed=$els"
  elif [ "$rc" -ne 0 ]; then
    _PROG_FAILS=$((_PROG_FAILS + 1)); prog_event STAGE_FAIL "stage=$stage" "rc=$rc" "elapsed=$els"
  else
    prog_event STAGE_END "stage=$stage" "rc=0" "elapsed=$els"
  fi
  _PROG_STAGE=""; _PROG_STAGE_T0=0
}

prog_exitfile() {  # stage exit-code file -> integer (absent or garbage -> 255, never 0)
  local v
  v=$(tr -d '[:space:]' < "$1" 2>/dev/null)
  if [[ $v =~ ^[0-9]+$ ]]; then printf '%s' "$v"; else printf '255'; fi
}

prog_verdicts() {  # phase log REQUIRED_NAME... -- copies NAME::PASS|FAIL lines, requires the named ones
  local phase=$1 log=$2 line name value req seen; shift 2
  local re='^([A-Z][A-Za-z0-9_]*(\[[^]]*\])?)::(PASS|FAIL)'
  seen=" "
  if [ -r "$log" ]; then
    while IFS= read -r line; do
      [[ $line =~ $re ]] || continue
      name=${BASH_REMATCH[1]}; value=${BASH_REMATCH[3]}
      [[ $name == *"["* ]] && name="${name%%\[*}[...]"  # display only: bracket labels are never echoed; counted either way
      _PROG_VERDICTS=$((_PROG_VERDICTS + 1)); seen="$seen$name "
      [ "$value" = PASS ] || _PROG_FAILS=$((_PROG_FAILS + 1))
      prog_event VERDICT "phase=$phase" "name=$name" "value=$value"
    done < "$log"
  fi
  for req in "$@"; do
    case "$seen" in *" $req "*) ;; *)
      _PROG_FAILS=$((_PROG_FAILS + 1)); prog_event VERDICT "phase=$phase" "name=$req" "value=MISSING" ;;
    esac
  done
}

prog_finish() {  # the final verdict step has been reached
  _prog_hb_stop
  local el=$(( $(date +%s) - _PROG_T0 )) v=FAIL
  [ "$_PROG_FAILS" -eq 0 ] && [ "$_PROG_VERDICTS" -gt 0 ] && v=PASS
  _PROG_DONE=1
  prog_event PROOF_END "verdict=$v" "failures=$_PROG_FAILS" "verdicts_read=$_PROG_VERDICTS" "elapsed=${el}s"
}

_prog_on_exit() {
  local rc=$?
  _prog_hb_stop
  if [ "$_PROG_DONE" -ne 1 ]; then
    prog_event PROOF_END "verdict=FAIL" "reason=chain_exited_before_final_verdict" "rc=$rc" \
      "stage=${_PROG_STAGE:-none}"
  fi
}
