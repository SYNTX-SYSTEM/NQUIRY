#!/usr/bin/env bash
# SFE proof-execution observer (contract SFE-PEO/1: SFE_PROOF_OBSERVABILITY_CONTRACT.md). OBSERVATION ONLY.
#
# Runs ONE command as its foreground child and reports process facts about it as structured events:
#   STAGE_START, HEARTBEAT (liveness: stage, elapsed, optional pytest progress %), then exactly one of
#   STAGE_END rc=0 | STAGE_FAIL rc=N | STAGE_TIMEOUT rc=124.
# Laws: progress and heartbeat are observations, never verdicts (no event ever says PASS); the child's real exit
# status is this process's exit status, unmapped; the child's stdin, stdout, stderr, arguments, environment and
# working directory are untouched; the observer never signals, stops or retries the child; a failing event sink
# never changes what runs or what is returned. The consuming Field keeps its own proof semantics and authority.
# Events go to stderr, or to the file named by --events (appended). They never go to stdout.
# The event grammar, redaction and heartbeat are the ones of progress.sh (one implementation, sourced).
# Closure: this file + progress.sh. Interval: SFE_HEARTBEAT_SECONDS (default 30).
#
# usage: sfe_observe.sh [--stage NAME] [--progress-log FILE] [--events FILE] -- COMMAND [ARG...]
#   exit: the child's exit status (128+n if a signal ended it); 2 = usage error of the observer (no event emitted,
#   nothing was run).
set -u
usage() { echo "usage: sfe_observe.sh [--stage NAME] [--progress-log FILE] [--events FILE] -- COMMAND [ARG...]" >&2; exit 2; }
stage=""; plog=""; evfile=""
while [ $# -gt 0 ]; do
  case "$1" in
    --stage) [ $# -ge 2 ] || usage; stage=$2; shift 2 ;;
    --progress-log) [ $# -ge 2 ] || usage; plog=$2; shift 2 ;;
    --events) [ $# -ge 2 ] || usage; evfile=$2; shift 2 ;;
    --) shift; break ;;
    *) usage ;;
  esac
done
[ $# -gt 0 ] || usage
[ -n "$stage" ] || stage=$(basename -- "$1")
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/progress.sh"
_PROG_HB_S=${SFE_HEARTBEAT_SECONDS:-$_PROG_HB_S}
exec 9>&2  # event sink: stderr, or the events file if it can be opened (an unusable sink never stops the run)
if [ -n "$evfile" ] && { : >> "$evfile"; } 2>/dev/null; then exec 9>>"$evfile"; fi
trap '_prog_hb_stop' EXIT
prog_begin "$stage" "$plog" >&9 < /dev/null
"$@" 9>&-
rc=$?
prog_end "$stage" "$rc" >&9
exit "$rc"
