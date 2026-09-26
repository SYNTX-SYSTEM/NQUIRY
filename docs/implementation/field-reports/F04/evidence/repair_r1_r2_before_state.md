# R1 / R2 before-state (captured 2026-09-25T11:58:52+02:00, before any repair)

## R1: nquiry_f04_red_runtime (produced by the pre-repair runtime proof)
 ai_operation_id | content_fingerprint |  sha256_content  | content_matches_fp | fp_eq_proof | validation_result 
-----------------+---------------------+------------------+--------------------+-------------+-------------------
 AIOP-001        | 260821878d0e0435    | b4922abd5c3a787e | f                  | t           | VALIDATED
 AIOP-002        | 820903103b41d820    | 8f7effd3f64a1a54 | f                  | t           | VALIDATED
(2 rows)

## R2: producer and asserting test (pre-repair source)
```
585:                content=_canonical(validation.payload),  # type: ignore[arg-type]
586:                content_fingerprint=proof.output_fingerprint,
        failure_detail_ref=candidate.failure_detail,
    )
    proof: AIValidationProof | None = candidate.proof
    if proof is not None:
        records.create_validation_proof(proof, workspace_id=generation.workspace_id)
    assert f04.artifacts(db_connection, ctx) == []
    assert f04.authorizations(db_connection, ctx, "AIOP-002") == []
    # the proof is persisted (it proves the contract validation, nothing more)
    proofs = f04.rows(db_connection, ai_validation_proofs_table, ai_generation_id=gen["id"])
```
