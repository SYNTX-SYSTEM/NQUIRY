#!/usr/bin/env bash
# B3 timing margin probe (DB-free). Reproduces the ONLY tight wall-clock assertion of the frozen
# suite (test_pfc_f09_1::test_worker_loop_survives_a_database_outage_and_stops_gracefully:
# worker --interval 0.2 against an unreachable DB, SIGTERM after 2.5 s, requires >= 2 passes)
# 4x concurrently, WITH 4 extra CPU burners standing in for 4 busy xdist workers. Stricter than
# the real lane (8 contending processes instead of 4). Executes no test and touches no database.
set -u
N=/home/codi/Entwicklung/nquiry
V=$N/.venv-proof313-orange
O=$N/worktrees/orange-proof-infra
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # proof-infrastructure root = this script's directory (lineage)
PYC=$V/orange-proof/pycache  # runtime bytecode cache (env-owned, never versioned)
OUT=${ORANGE_TIMING_OUT:-$P/evidence/timing_$(date +%Y%m%dT%H%M%S)}; mkdir -p "$OUT"
ROUNDS=${ROUNDS:-5}
W() { exec env -u PYTHONDONTWRITEBYTECODE PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=$PYC \
        PYTHONPATH=$O/packages:$O/apps/worker/src DATABASE_URL=postgresql+psycopg://nquiry:x@127.0.0.1:1/none \
        "$V/bin/python" -m nquiry_worker --interval 0.2; }
echo "load before: $(cut -d' ' -f1-3 /proc/loadavg)  cpus: $(nproc)"
: > "$OUT/samples.txt"
for r in $(seq 1 "$ROUNDS"); do
  burners=(); for b in 1 2 3 4; do "$V/bin/python" -c "import time;t=time.time()
while time.time()-t<4: pass" & burners+=($!); done
  pids=(); for w in 1 2 3 4; do ( W ) 2> "$OUT/r${r}_w${w}.err" & pids+=($!); done
  sleep 2.5
  for p in "${pids[@]}"; do kill -TERM "$p" 2>/dev/null; done
  for p in "${pids[@]}"; do wait "$p" 2>/dev/null; done
  for b in "${burners[@]}"; do wait "$b" 2>/dev/null; done
  for w in 1 2 3 4; do echo "$(grep -c DATABASE_UNAVAILABLE "$OUT/r${r}_w${w}.err") $(grep -c stopped "$OUT/r${r}_w${w}.err")" >> "$OUT/samples.txt"; done
  echo "round $r: passes per worker = $(tail -4 "$OUT/samples.txt" | cut -d' ' -f1 | tr '\n' ' ') | load $(cut -d' ' -f1 /proc/loadavg)"
done
python3 - "$OUT/samples.txt" <<'EOF'
import sys
s = [tuple(map(int, l.split())) for l in open(sys.argv[1]) if l.strip()]
passes = [p for p, _ in s]; stopped = [x for _, x in s]
print(f"samples={len(s)} min_passes={min(passes)} max={max(passes)} mean={sum(passes)/len(passes):.1f} "
      f"all_stopped_gracefully={all(x >= 1 for x in stopped)} required>=2")
print("TIMING_MARGIN_UNDER_8_WAY_CONTENTION::" + ("PASS" if min(passes) >= 2 and all(x >= 1 for x in stopped) else "FAIL"))
EOF
