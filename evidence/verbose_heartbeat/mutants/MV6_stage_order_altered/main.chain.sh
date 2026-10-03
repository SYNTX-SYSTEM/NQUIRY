prog_init synthetic "run=main"
prog_begin fast; true; prog_end fast "$?"
prog_begin slow "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV6_stage_order_altered/stage.log"; sleep 3.5; prog_end slow "$?"
echo "${_PROG_HB:-}" > "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV6_stage_order_altered/main.hb_after_end"
prog_begin wait_for_hb; sleep 1.5; h=$_PROG_HB; echo $h > "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV6_stage_order_altered/main.hb_during"; prog_end wait_for_hb 0; sleep 0.3
(kill -0 $h 2>/dev/null && echo alive || echo gone; pgrep -P $h >/dev/null && echo children || echo nochildren) > "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV6_stage_order_altered/main.hb_state"
prog_event NOTE "url=$DATABASE_URL" "token=$PGPASSWORD" "note=pw@S3CRET_FIXTURE_7f3a" "plain=S3CRET_FIXTURE_7f3a x"
prog_verdicts phase_ok "/home/codi/Entwicklung/nquiry/worktrees/orange-proof-lineage/evidence/verbose_heartbeat/mutants/MV6_stage_order_altered/ok.log" A B
prog_finish
