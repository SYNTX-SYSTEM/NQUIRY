#!/usr/bin/env bash
# ORANGE execution decomposition (Human Authority "TEST IDENTITY EQUIVALENCE" option 1, 2026-10-01).
# SERIAL partition = serial_partition_selectors.txt (HA 2026-10-01: the 3 volatile-identity nodes +
# the 1 fixed-time-window node, SF-PX-03) = 4 nodes; XDIST partition = the exact complement (2235).
# Selection only: no test code, input, uuid, collection semantics or xdist behaviour is changed.
# This script only COLLECTS (DB-free, DATABASE_URL unset); it never executes a test.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
OUT=${ORANGE_PARTITION_DIR:-$P/evidence/partition_$(date +%Y%m%dT%H%M%S)}
mkdir -p "$OUT"
mapfile -t SERIAL_SELECTORS < "$P/serial_partition_selectors.txt"
printf "%s\n" "${SERIAL_SELECTORS[@]}" > "$OUT/serial_selector.txt"
DESELECT=(); for s in "${SERIAL_SELECTORS[@]}"; do DESELECT+=(--deselect "$s"); done
printf "%s\n" "${DESELECT[@]}" > "$OUT/xdist_selector.txt"
H() {  # TF-PX-10: governed children get an ALLOWLIST environment (env -i): process basics, locale, the catalog selector, and what this runner sets. Nothing ambient passes by default
  local n a=()
  for n in PATH HOME USER LOGNAME LANG LANGUAGE LC_ALL LC_CTYPE LC_COLLATE LC_MESSAGES LC_NUMERIC LC_TIME LC_MONETARY LC_ADDRESS LC_IDENTIFICATION LC_MEASUREMENT LC_NAME LC_PAPER LC_TELEPHONE TZ TMPDIR ORANGE_CATALOG_DB; do
    [ -n "${!n+x}" ] && a+=("$n=${!n}"); done
  env -i "${a[@]}" PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=$PYC "$@"; }
collect() {  # $1 = name, rest = selection args
  local name=$1; shift
  (cd "$O" && H "$V/bin/python" -m pytest -p no:cacheprovider --collect-only -q "$@") > "$OUT/${name}_raw.txt" 2>&1
  grep "::" "$OUT/${name}_raw.txt" | sort > "$OUT/${name}_nodeids.txt"
  echo "$name: $(wc -l < "$OUT/${name}_nodeids.txt") selected | $(tail -1 "$OUT/${name}_raw.txt")"
}
collect full
collect serial "${SERIAL_SELECTORS[@]}"
collect xdist "${DESELECT[@]}"
