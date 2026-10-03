prog_init canonical-orange "lineage=$(git -C "$P" rev-parse --short HEAD 2>/dev/null || echo unknown)" "run=$(basename "$F")"
prog_begin serial_pre
prog_end serial_pre "$rc"
prog_verdicts serial_pre "$S/pre.log" ORANGE_IMPORT_ORIGIN PROOF_DB_PRECONDITIONS
prog_begin serial_reference "$S/run.log"
prog_end serial_reference "$(prog_exitfile "$S/run_exit_code.txt")"
prog_event CLEANUP phase=serial observer=stopped
prog_begin serial_post
prog_end serial_post unobserved
prog_begin serial_analysis
prog_end serial_analysis unobserved
prog_verdicts serial_analysis "$S/analysis.log" SERIAL_BASELINE
prog_begin parallel_pre
prog_end parallel_pre "$rc"
prog_verdicts parallel_pre "$R/pre.log" ORANGE_IMPORT_ORIGIN PROOF_DB_PRECONDITIONS
prog_begin partition_proof
prog_end partition_proof unobserved
prog_verdicts partition_proof "$R/partition_proof.log" PARTITION_PROOF
prog_begin xdist_partition "$R/xdist_run.log"
prog_end xdist_partition "$(prog_exitfile "$R/xdist_exit_code.txt")"
prog_begin serial_partition "$R/serial_run.log"
prog_end serial_partition "$(prog_exitfile "$R/serial_exit_code.txt")"
prog_event CLEANUP phase=parallel observer=stopped
prog_begin parallel_post
prog_end parallel_post unobserved
prog_begin aggregation
prog_end aggregation unobserved
prog_verdicts aggregation "$R/aggregate.log" AGGREGATION_AND_EQUIVALENCE TREE_UNCHANGED ENV_MANIFEST_UNCHANGED MIGRATION_HEADS_AND_FINGERPRINT_UNCHANGED PROOF_DBS_CLEAN_AND_UNCONNECTED_AFTER NO_RESIDUAL_RACE_DB NO_RESIDUAL_ZZ_PKG25_ROLE PARALLEL_PROOF
prog_begin order_proof
prog_end order_proof unobserved
prog_verdicts order_proof "$R/order_proof.log" ORDER_PROOF
prog_begin inertness
prog_end inertness unobserved
prog_verdicts inertness "$R/inertness.log" SUCCESSOR_PRESERVES_PCPG5_SERIAL_OUTCOMES
prog_finish
