prog_init synthetic
prog_begin bounded; timeout 1 sleep 5; prog_end bounded "$?"
prog_verdicts p "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV7_timeout_not_reported/ok.log" A; prog_finish
