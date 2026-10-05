prog_init synthetic
prog_begin failing; bash -c 'exit 3'; prog_end failing "$?"
prog_begin nofile; prog_end nofile "$(prog_exitfile "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/sfe_observability/regression/progress_falsifiers/does_not_exist.txt")"
prog_verdicts p "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/sfe_observability/regression/progress_falsifiers/ok.log" A; prog_finish
