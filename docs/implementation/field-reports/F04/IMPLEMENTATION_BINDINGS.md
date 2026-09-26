# F04 — Implementation bindings and Case-2 materialization choices

**Status:** backend materialization in the RED worktree
(`worktrees/f04-implementation`, branch `f04-implementation`, base `d9410b3`).
Nothing is staged, committed, tagged or pushed.

This file records, in one place:

1. how each pre-implementation review binding (PI-1..PI-6) is materialized;
2. every **Case-2** choice (local, interchangeable, nonsemantic) that the
   reviewed architecture (revision 6) explicitly delegated to materialization;
3. the First Broken Relations found *during* implementation, which are not
   architecture changes.

No choice below changes meaning, authority, governance, an F03 semantic, or an
external effect. If one had, work would have stopped for Human Authority
(Case 3). **None did.**

## 1. Pre-implementation bindings

| Binding | Materialized as | Proof |
|---|---|---|
| **PI-1** VALIDATED + proof + acceptance atomically | **Repaired after the independent review (R1, R2; `REPAIR_R1_R2.md`).** The artifact content is the exact validated bytes. No VALIDATED proof exists outside the bundle. DB triggers of migration `e7c1d4a9b206` enforce both. `application/analysis_system.py::_accept`: one CommitCoordinator commit (T2b+T3) writes generation OUTPUT_RECEIVED → VALIDATED, the `ai_validation_proofs` row, the accepted `ai_derived_artifacts` row and (AIOP-001) OA-3 or (AIOP-002) the cluster run. A VALIDATED generation therefore never exists without its accepted artifact. | E2, `test_acceptance_denial_leaves_honest_failure_and_no_artifact` |
| **PI-2** multi-transaction orchestration | T1 human Command (own transaction, durable) → T2a EXECUTE (manifest + REQUESTED→RUNNING generation) → provider call outside every lock and transaction → T2b+T3 ACCEPT, or an operational terminal write. `UnitOfWork` = one transaction per call (`http_f04.transaction_uow`; tests: SAVEPOINT or a real engine). | `test_pi2_multi_transaction_run_commits_each_step_durably` (real commits, new connection reads) |
| **PI-3** fixed SYSTEM_SERVICE identity, F04-only | `authority/system_service.py::F04_ANALYSIS_SERVICE_ID` (a fixed, well-known UUID; not a `users` row). Constructed only in `application/analysis_system.py`. The SYSTEM_OPERATION resolver refuses any other SYSTEM_SERVICE id. The system path runs BND-001 (SYSTEM_SERVICE) and BND-002; **no BND-003** (a service has no membership). | `test_pi3_only_the_f04_system_module_constructs_the_service_actor`, C2 |
| **PI-4** explicit immutable OA table | `ai_operation_authorizations` (migration `a8d3f1c6e902`): one row per OA, CHECKed to the four §0.1 shapes, UNIQUE (authorizing_command_id, ai_operation_id), UNIQUE (session, operation, sequence_no), insert trigger for supersession / chain root / RETRY-RECOVERY case / X, UPDATE and DELETE rejected. | C8, `test_oa_shape_outside_rule_2_is_refused`, `test_request_case_must_match_persisted_state`, `test_operation_authorization_rows_are_immutable` |
| **PI-5** dev-only mock on the `Environment` vocabulary | `application/analysis_runtime.py`: `NQUIRY_AI_PROVIDER=mock` is honoured only for `NQUIRY_ENVIRONMENT` ∈ {DEVELOPMENT, TEST}; any other value (PRODUCTION, STAGING, unset, unknown) raises `MockProviderForbidden`. `apps/api/.../main.py` applies it at import, so the API refuses to start. | F1 (4 refusal cases + startup wiring) |
| **PI-6** cluster domain type and tables | `question_clusters` / `question_cluster_memberships` (migration `c2e7b9a4f513`, 09 §34/§35 fields + workspace/session), append-only, frozen-member trigger, `persistence/question_cluster_repository.py`. | K1-K5, `test_cluster_membership_of_a_non_frozen_question_is_refused` |
| **Concurrency** Session row lock + DB constraints | `SessionRepository.get_for_update` (`FOR NO KEY UPDATE`) taken first by BEGIN_ANALYSIS, both requests, EXECUTE, ACCEPT and the operational terminal write; partial unique index "one non-terminal generation per (Session, operation)". | `tests/e2e/test_f04_concurrency.py` (separate connections, real commits) |

## 2. Case-2 choices (delegated by the architecture)

| # | Choice | Why it is Case 2 | Where |
|---|---|---|---|
| C2-1 | HD-18 output field names and limits: `classification_proposals[{question_ref, proposed_class}]`, `question_families[{label, question_refs}]`, `unusual_question_flags[{question_ref, reason}]`, `pattern_descriptions[{text, supporting_question_refs}]`, `contradiction_proposals[{question_refs(≥2), description}]`; label ≤ 120, text ≤ 1000, ≤ 200 items; every key required, no other key at any level. | §7: "Exact field names and limits are Case 2, fixed in WU-04.4" | `ai_contracts/f04_operations.py` |
| C2-2 | AIOP-002 output `clusters[{label?, description?, question_refs}]`, each Question in at most one cluster of a run. | 08 §24 / 09 §34-35 name the content, not the encoding | same |
| C2-3 | Contract version `1.0` for both AIOPs; validator version `4.1`; prompt version `4.1` (the repository's `ContractVersion` / `PromptVersion` require dotted integers). | naming | `validator.py`, `analysis_input.py` |
| C2-4 | Manifest pins Questions by `content_digest` = sha256(`original_text`) and the Challenge context by the digest of title + description; `frozen_set_ref = burst:<id>`, `frozen_set_fingerprint` = the stored, re-verified F. | §7 fixes *what* is pinned (burst, F, ids, text digests), not the encoding | `analysis_input.py`, `InputArtifactRef.content_digest` |
| C2-5 | The exact persistence of the request Commands' write-once references (chain root, case, superseded OA, `retry_of`, X): columns of the immutable OA row the request commit writes. `commands` stores only a payload fingerprint, so it could not hold them. | §0.1 rule 8: "The exact column is a Case 2 materialization choice. Written once and never updatable is the architectural requirement." | `ai_operation_authorizations` |
| C2-6 | `sequence_no` per (Session, operation) as the representation of "latest OA"; RETRY / RECOVERY both record the superseded predecessor. | representation of rule 5 | same |
| C2-7 | `cluster_run_id` = the id of the accepted AIOP-002 artifact; the accepted clustering output is stored as an artifact like the analysis. One partial unique index then enforces both R2 and R8. | 09 §34.1 requires a `cluster_run_id`, not its source | `ai_derived_artifacts`, `question_clusters` |
| C2-8 | Outbox / audit event names: `SESSION_ANALYSIS_BEGUN`, `AI_GENERATION_REQUESTED`, `AI_OUTPUT_ACCEPTED`, `QUESTION_CLUSTERS_ACCEPTED`, `AI_OPERATION_REQUESTED`. | §10 F08: "The naming is Case 2" | handlers |
| ~~C2-9~~ | **WITHDRAWN: misclassified; it was not Case 2 (independent review FBR-F04-R2).** It changed what a persisted VALIDATED proof means for F05 and contradicted PI-1 and the 06 §16 home note. It is superseded by the R2 root repair: the acceptance-denied generation is FAILED (`ACCEPTANCE_DENIED:<reason>`, `failure_detail_ref = validated_output_fingerprint:<sha256>`) and **no** proof row exists; RETRY stays legal. *Original text:* A VALIDATED candidate whose acceptance is denied or fails before commit is recorded **FAILED** with `failure_code = ACCEPTANCE_DENIED:<reason>`, and its VALIDATED proof is persisted. So RETRY stays legal, and no VALIDATED-but-unaccepted generation can block the Session. | a failure-recording form; the architecture fixes only that acceptance must not happen and that RETRY follows failure | `analysis_system.run_authorized_operation` |
| C2-10 | Provider / validation endings without an effect (FAILED, REJECTED, INDETERMINATE → FAILED) are **operational** writes (generation + proof, Session-locked), with no Command and no audit row. The generation row is their record (08 §23 audit requirement: operation, generation, status, provider). | operational record, not an effect | `_finalize` |
| C2-11 | Environment settings `NQUIRY_ENVIRONMENT`, `NQUIRY_AI_PROVIDER`, and dev-only scripted outcomes `NQUIRY_AI_MOCK_OUTCOME_AIOP_00x`. STAGING and an unset environment are refused (conservative reading of "dev runtime only"). | configuration naming; the stricter reading adds no permission | `analysis_runtime.py` |
| C2-12 | HTTP paths: `…/transitions/begin-analysis`, `…/analysis/request`, `…/analysis/clustering/request`; body `{expectedVersion, case}`; `position.analysis`; actions `BEGIN_ANALYSIS`, `REQUEST_QUESTION_ANALYSIS`, `REQUEST_QUESTION_CLUSTERING` (with `case`). | named by §10 / §14; body shape is local | `apps/api/.../inquiry.py`, `http_f04.py` |
| C2-13 | The client names the RETRY / RECOVERY case it intends; a case that disagrees with the persisted state is **rejected** (400), never corrected. | E18 / K20 fix the refusal; carrying the case in the request is the local form | `analysis_request_handler.py` |

## 3. First Broken Relations found during implementation

These are defects in existing code, exposed by implementation evidence and
repaired at the root. None changes reviewed semantics.

| Id | Broken relation | Evidence | Root repair |
|---|---|---|---|
| FBR-F04-I1 | `audit.models.AuditEvent` carried its own closed source vocabulary, a sibling of the DB CHECK and `AuthoritySourceType`. The fifth source was rejected at audit construction, so the SYSTEM_OPERATION commit failed precommit. | first E2 run: `ValueError: unknown authority_source_type 'SYSTEM_OPERATION'` → FAILED_PRECOMMIT | `SYSTEM_OPERATION` added to the model vocabulary (same HD-17) |
| FBR-F04-I2 | P-23 gate: only `ai_gateway.gateway` may construct `MockProviderAdapter`. The first runtime module constructed it directly. | `tests/security/test_ai_gateway.py::test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider` | `ai_gateway.gateway.mock_gateway()` factory; the runtime uses it |
| FBR-F04-I3 | The F03 input law rejects a non-question statement, so the prompt-injection fixture was worded as a question. | `CaptureInputRejected: INPUT_NOT_A_QUESTION` | fixture text only (F03 semantics unchanged) |

## 3a. First Broken Relations found by the independent backend review

| Id | Broken relation | Root repair | Record |
|---|---|---|---|
| FBR-F04-R1 | The accepted artifact was not bound to the output its proof validated: content re-serialized under the raw fingerprint, and the resolver skipped the proof. | Raw validated bytes persisted; the resolver goes through the VALIDATED proof and checks the byte binding; BEFORE INSERT binding trigger. | `REPAIR_R1_R2.md` |
| FBR-F04-R2 | A VALIDATED proof was persisted outside the PI-1 bundle on a denied acceptance (C2-9). | No VALIDATED proof outside acceptance; the fingerprint is recorded on the FAILED generation; deferred PI-1 constraint triggers. | `REPAIR_R1_R2.md` |

Two tests were changed by this repair, each in the stricter direction:
- the acceptance-denial test now asserts **no** proof;
- C7 is proven on a genuine accepted artifact, and fabricating one is now
  asserted refused.

## 4. Superseded PKG-era tests (root repairs, not weakening)

- `tests/ai/test_gateway.py`: the PKG-19 Gateway persisted artifacts and was
  gated by a boolean (FBR-F04-1/2/7). It is rewritten for the candidate-only
  Gateway. Each moved intent names its new home in the module docstring.
- `tests/ai/test_validator.py`: the PKG-19 validator accepted one mock shape
  (FBR-F04-8). It is rewritten for the closed contracts. One reading changes,
  per architecture §15 D4: unparseable / partial output is REJECTED;
  INDETERMINATE means the validator itself failed (08:731-740). Both are
  tested.
- `tests/boundaries/test_bnd_009_ai_invocation.py`: its base input gains the
  two facts BND-009 now requires (Burst COMPLETED, F verified; FBR-F04-3).
  Every existing assertion is unchanged.
