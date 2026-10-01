#!/usr/bin/env bash
# Read-only cluster-object observer. Connects ONLY to the given PROOF database (shared catalogs are
# readable from any database). Must be a database NOT used as a TEMPLATE in the observed phase.
# usage: observer.sh <proof-db> <log> <stop-file>
set -u
DB=$1; LOG=$2; STOP=$3
case "$DB" in nquiry_proof_serial_test|nquiry_proof_gw[0-3]_test) ;; *) echo "REFUSED: $DB is not a proof db"; exit 1;; esac
export PGPASSWORD=nquiry_local_dev_only
: > "$LOG"; prev=""
while [ ! -f "$STOP" ]; do
  cur=$(psql -h 127.0.0.1 -p 15432 -U nquiry -d "$DB" -Atc "select 'db:'||datname from pg_database where datname like 'race\_%' union all select 'role:'||rolname from pg_roles where rolname like 'zz\_pkg25\_%' order by 1" 2>/dev/null | tr '\n' ' ')
  if [ "$cur" != "$prev" ]; then echo "$(date -Iseconds) present=[$cur]" >> "$LOG"; prev="$cur"; fi
  sleep 0.2
done
echo "$(date -Iseconds) observer stopped (via $DB)" >> "$LOG"
