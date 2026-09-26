# F04 — Independent-review repair set R1 / R2

**Trigger:** the independent read-only Opus backend review (session
`f778c2b3`), verdict **F04_BACKEND_REPAIR_REQUIRED**. It found exactly two
material First Broken Relations, FBR-F04-R1 and FBR-F04-R2. Both sit on the
PI-1 relation: the accepted effect must provably *be* the VALIDATED candidate
and its persisted proof.

**Reviewed input:** `review/BACKEND_REVIEW_BUNDLE.md`, sha256
`c27af32dd48d9e9157d766d3b0fcb4e7d4f7cf0791023095fa95ab32639bcf7f`. It is
preserved unchanged. The evidence files that bundle embedded are also kept
unchanged; post-repair evidence is added under new names.

**Scope:** R1 and R2 only, plus their dependency propagation. The reviewer's
non-blocking findings 1-11 are not in scope and stay open (see "Remaining").
No architecture semantics changed. No F03, BLUE or CYAN change. No WU-04.8.
Nothing committed.

---

## FBR-F04-R1: the accepted artifact is not bound to the output its proof validated

| Aspect | Reconstruction |
|---|---|
| Visible effect | In the real DB `nquiry_f04_red_runtime`, both accepted artifacts had `sha256(content) ≠ content_fingerprint`, while `content_fingerprint = proof.output_fingerprint` (`evidence/repair_r1_r2_before_state.md`). The inverse resolver never visited the proof. |
| Consumer | The inverse resolver (E16 / K17 / K19); F05's HD-20 / REFLECTION check; any auditor. |
| Relation | accepted artifact ≡ VALIDATED candidate ≡ the bytes the proof fingerprinted. |
| Producer | `analysis_system._accept`: `content=_canonical(validation.payload)` (compact re-serialization) under `content_fingerprint=proof.output_fingerprint` (sha256 of the raw provider bytes). The raw bytes were persisted nowhere. |
| Authority | 09 §118 (output fingerprint + AI_VALIDATION_PROOF reference, "mandatory for high-assurance use"); reconstruction §11 items 2a / 2b / 4a / 4b ("← BND-010 ← persisted proof VALIDATED ← generation"); §0.1 rule 8; PI-1. |
| First broken relation | (a) The producer persisted a re-serialization under the fingerprint of different bytes. (b) `analysis_provenance._link` skipped the immutable proof link §11 requires. |
| Why it is broken | CANDIDATE ≠ EFFECT requires the effect to be *derived from* the candidate in a checkable way. Before the repair, the equivalence rested on trusting code, not on persisted records. |
| Root repair | 1. `_accept` persists `content = candidate.response.raw_content`, the exact validated bytes. `_canonical` is removed. Clusters, OA-3 and the projection read the same bytes parsed. 2. The resolver reads the immutable proof by generation (`ProofFact`, `SqlAlchemyImmutableProvenanceReader.validation_proof`). It requires VALIDATED, the same operation, and `sha256(content) = content_fingerprint = proof.output_fingerprint`; otherwise `ProvenanceBroken`. `ChainLink` carries `proof_id` and `output_fingerprint`. 3. DB second line (migration `e7c1d4a9b206`): trigger `trg_ai_derived_artifacts_validated_binding`, BEFORE INSERT on accepted artifacts (`session_id` set). It requires the VALIDATED proof of the same generation and operation, with `output_fingerprint = content_fingerprint = encode(sha256(convert_to(content,'UTF8')),'hex')`. |
| Must become true | Every accepted artifact's content is byte-identical to the validated output. The persisted-only chain includes the VALIDATED proof. |
| Must remain impossible | An accepted artifact whose content differs from the validated bytes, or which has no VALIDATED proof of the same operation. A chain that resolves without a VALIDATED proof. |

## FBR-F04-R2: a VALIDATED proof is persisted outside the PI-1 acceptance bundle

| Aspect | Reconstruction |
|---|---|
| Visible effect | On a failed or denied acceptance, the generation became FAILED (`ACCEPTANCE_DENIED:*`) with no artifact, yet an immutable VALIDATED proof was persisted. A test asserted exactly that. |
| Consumer | F05 BEGIN_REFLECTION (03 TRN-SESS-007: "AI_VALIDATION_PROOF that required analysis operations completed"); HD-20 enforcement. |
| Relation | A persisted VALIDATED proof ⇔ a VALIDATED generation with exactly one accepted artifact, all in one commit. |
| Producer | `run_authorized_operation` → `finish(ACCEPTANCE_DENIED)` → `_finalize` wrote `candidate.proof`. |
| Authority | PI-1; the 06 §16 home note (VALIDATED, the persisted proof and the accepted artifact "are committed in one atomic bundle"); 08 §23 (the proof "may contribute … toward BEGIN_REFLECTION"). |
| First broken relation | C2-9 was misclassified as Case 2. It changed what a persisted VALIDATED proof means for the F05 consumer, and it contradicted the 06 home note written by this same materialization. |
| Root repair (the reviewer's primary option; restores reviewed semantics, **no** Human-Authority redefinition of the proof class) | 1. `_finalize` never persists a VALIDATED proof. The denial branch records OUTPUT_RECEIVED → FAILED with `failure_code = ACCEPTANCE_DENIED:<reason>` and `failure_detail_ref = validated_output_fingerprint:<sha256>`. RETRY stays legal. REJECTED and INDETERMINATE proofs are unchanged. 2. DB second line (migration `e7c1d4a9b206`): `DEFERRABLE INITIALLY DEFERRED` constraint triggers, checked at COMMIT. `trg_ai_validation_proofs_pi1_bundle`: a VALIDATED proof needs its VALIDATED generation and accepted artifact. `trg_ai_generations_pi1_bundle`: an F04 generation becoming VALIDATED needs its VALIDATED proof and accepted artifact. |
| Must become true | A VALIDATED proof exists iff its generation is VALIDATED and has exactly one accepted artifact. |
| Must remain impossible | A VALIDATED proof on a FAILED or non-VALIDATED generation. A VALIDATED proof or VALIDATED generation without its accepted artifact at commit. A RETRY blocked by a denied acceptance. |

The **reclassification of C2-9** is recorded in `IMPLEMENTATION_BINDINGS.md`
(C2-9 withdrawn and superseded by R2).

---

## Propagation

| Surface | Change |
|---|---|
| Producer | `application/analysis_system.py`: `_accept` stores the raw bytes; `_finalize` and `finish` carry an explicit failure detail and skip VALIDATED proofs; the module docstring is updated. |
| Resolver / reader | `persistence/provenance_reader.py`: `ArtifactFact` gains `content` and `content_fingerprint`; new `ProofFact` and `validation_proof()`. `application/analysis_provenance.py`: the chain goes through the proof; `ChainLink.proof_id` and `output_fingerprint`; steps name the proof. |
| Persistence | New migration `e7c1d4a9b206` (3 triggers). No table, column, FK or uniqueness change. The existing append-only, one-per-generation and one-per-(Session, operation) constraints are unchanged and still hold. |
| API / projection | Unchanged in shape. `artifact.content` is now the raw validated JSON; the projection already calls `json.loads` on it. |
| Tests | New `tests/e2e/test_f04_accepted_output_binding.py` (10). `test_f04_analysis_run.py`: the denial test now asserts **no** proof plus the fingerprint record (the opposite of before, same strictness). `test_f04_system_operation_gate.py`: C7 is proven on a genuinely accepted artifact, and the former fabrication on a REJECTED-proof generation is now asserted **refused**. `test_f04_concurrency.py`: 3 real-commit tests. `scripts/f04_mutation_proof.py`: M21, M22, M22b, M23. |
| Runtime DB | `nquiry_f04_red_runtime` was recreated (its pre-repair rows are append-only; the before-state is preserved in evidence). The full runtime proof was re-run on it. |
| Docs | PROOF_MATRIX, IMPLEMENTATION_BINDINGS, SWEEPS, WU-04.3 / 04.5 / 04.10, RUNTIME_PROOF, STATUS. |
| Not changed | The approved architecture and its pinned inputs, the reviewed bundle, F03 code and tests, 04 / 06 / 08 / 09 (the 06 note is now *true*; no edit needed), BLUE, CYAN. |

## Proof

| Proof | Result |
|---|---|
| RED before repair | The new falsifiers failed for the right reasons. R1: the DB accepted a re-serialized artifact, and the resolver had no proof link. R2: a VALIDATED proof was stored on denial, there was no failure record, and the DB accepted an orphan VALIDATED proof or generation. |
| Falsifiers after repair | `test_f04_accepted_output_binding.py` 10 passed. E group 22 passed. C group 16 passed. |
| Real-commit (cloned DB, deferred triggers fire at COMMIT) | `test_r2_real_commit_denied_acceptance_leaves_no_validated_proof`, `test_r2_real_commit_refuses_an_orphan_validated_proof` (refused **at COMMIT** with PI-1), `test_r1_r2_real_commit_happy_path_binds_every_accepted_artifact`: 3 / 3, plus the 6 earlier concurrency proofs, 9 / 9. |
| Mutation proof | 24 / 24 killed (`evidence/mutation_proof_r1r2.txt`), sources restored byte-identically. M21 was first written as a default-separator re-serialization. That is an **equivalent mutant for the mock**: the mock emits `json.dumps(sort_keys=True)`, which survives a json round-trip byte-for-byte. It survived, and was re-targeted at the exact pre-repair code (compact separators), which is killed. The DB binding refuses any divergence for every provider. |
| Real PostgreSQL closure (fresh runtime DB, two live uvicorn processes) | R1: both accepted artifacts `content_matches_fp = t`, `fp_eq_proof = t`, VALIDATED. R2: VALIDATED proofs without a VALIDATED generation and artifact = 0; VALIDATED F04 generations without proof and artifact = 0. The FAILED generation has no proof. The three PI-1 triggers are present (two deferred). `evidence/runtime_r1r2_persisted_closure.txt` |
| Inverse | The persisted-only resolver on the runtime DB walks artifact ← proof VALIDATED (sha256 prefix) ← generation (mock) ← OA-2 RETRY ← request (BINDING) ← root BEGIN_ANALYSIS (BINDING, `SESSION:<id>`). The clustering follows the same path via OA-3. Inverse test file 7 / 7. |
| Runtime behaviour | Unchanged from the pre-repair proof: F1 refusal (exit 1); begin → committed + FAILED / PROVIDER_TIMEOUT; RETRY → ACCEPTED + clustering ACCEPTED; audience views identical; MOCK_NON_PROOF; wrong case rejected; Owner 403; non-member 403. |
| Regression | See `evidence/regression.txt` (updated with the post-repair run). |
| Gates | ruff and format clean on the changed files; mypy clean (176 files); architecture-dependency, provider-SDK and test-only-import checks PASS; migrations 28 revisions, single head `e7c1d4a9b206`, upgrade → downgrade → upgrade clean. |

## Mock ceiling after R2

- MOCK RESULT ≠ PROOF: every generation is still `provider = mock`, every
  accepted artifact is `proof_class = MOCK_NON_PROOF`, and the projection marker
  is unchanged.
- ANALYSIS OUTPUT ≠ F05 PROOF: a VALIDATED proof now exists only together with
  its accepted artifact, and the proof → generation → provider chain still
  shows `mock`. So HD-20 (a mock proof never counts toward BEGIN_REFLECTION for a
  non-fixture Session) stays enforceable by F05 on persisted records.
- PROVIDER RESULT ≠ CANONICAL EFFECT: the Gateway still writes nothing. The
  effect is only the SYSTEM_OPERATION acceptance commit.

## Remaining (not in this repair's scope)

- The independent review's non-blocking findings 1-11 are unchanged and open.
  Items 3 and 4 are bound to the HARD-DEP-002 lane; item 11 to F08.
- H-8 is open (Human Authority). WU-04.8 is BLOCKED_ON_H8_FOR_WU_04_8.
  HARD-DEP-002 is external.
