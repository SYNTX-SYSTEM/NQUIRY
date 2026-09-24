#!/usr/bin/env bash
# SF-01 ISOLATED real-stack lane (L6/L7), host entry point.
#
# Starts ONLY compose project `nquiry-sf01` (infra/sf01/compose.yaml): its own
# database volume, no published host ports, this tree's API/web/browser inside
# one private network namespace. It never starts, stops or reads any other
# project (the F03 environment runs as project `nquiry`).
#
# Guards, checked BEFORE anything starts:
#   - the resolved compose project name is exactly `nquiry-sf01`;
#   - no service publishes a host port.
# Each run starts from an empty SF-01 database (only `nquiry-sf01` volumes are
# removed). Proof output: apps/web/test-results/sf01-real-stack/ (gitignored).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="nquiry-sf01"
COMPOSE=(docker compose -p "$PROJECT" -f "$ROOT/infra/sf01/compose.yaml")

"${COMPOSE[@]}" config --format json | python3 -c '
import json, sys
config = json.load(sys.stdin)
name = config.get("name")
if name != "nquiry-sf01":
    sys.exit(f"SF01_GUARD: compose project is {name!r}, expected nquiry-sf01")
published = [s for s, svc in config.get("services", {}).items() if svc.get("ports")]
if published:
    sys.exit(f"SF01_GUARD: services publish host ports: {published}")
print("SF01_GUARD: project nquiry-sf01, no host ports")
'

mkdir -p "$ROOT/apps/web/test-results/sf01-real-stack"
"${COMPOSE[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
set +e
"${COMPOSE[@]}" run --build --rm runner bash infra/sf01/run-in-namespace.sh "$@"
status=$?
set -e
"${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
exit "$status"
