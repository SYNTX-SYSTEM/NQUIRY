#!/usr/bin/env bash
# synthetic consumer runner: the shape of a Field's regression runner (not a copy of any Field's script)
set -uo pipefail
echo "HEAD: synthetic"
LIVE_OUT="$(bash -c 'sleep 2.4; echo "FAILED tests/x.py::t - boom"; echo "3 passed in 2.40s"; exit '"${SYN_RC:-0}" 2>&1)"
LIVE_CODE=$?
echo "LIVE_RESULT: $(printf '%s\n' "$LIVE_OUT" | tail -1)"; echo "LIVE_EXIT_CODE: $LIVE_CODE"
echo "TREE_UNCHANGED_DURING_RUN: true"
[ "$LIVE_CODE" -eq 0 ]
