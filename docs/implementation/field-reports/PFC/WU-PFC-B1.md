# WU-PFC-B1 — TRN-SESS-007 BEGIN_REFLECTION under HD-24

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B1 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (19 §25) |
| Colour / role / model | RED · application / API / projection · Claude Opus 5.5 |
| Human authorization | HD-24 / NQ-DEC-052 (2026-09-27), rules 6–12, plus "Derive all newly eligible RED Work Units downstream of HA-01". |
| Derivation | With the Fixture identity in place (WU-PFC-B0), TRN-SESS-007 is the first relation HD-24 unlocks. |
| Predecessor / baseline | `checkpoint-PFC-B0` → `ea3af40`; identity record `9c04a00`. Live 1872 / 2; no-DB 911. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. Runtime: `nquiry_pfc_int_runtime` @ `d4f7b2c9e6a1`, API :18433. |
| Authoritative home | 03 TRN-SESS-007 (required evidence, DENY conditions, "AI failure does not advance state"); 04 AUTH-DEP-SESS-007 (human controller path; "No analysis failure"); 12 §39 ("Required: AIOP-001. Optional: AIOP-002."); 06 BND-017; 16 REC-018 (SYSTEM_DERIVED stays REQUIRE/DENY), REC-022 (HD-20, enforcement "proof → generation → provider provenance"), REC-028 (HD-24). |
| Authorized delta | The Command, handler, route, proof-source rule and projection for TRN-SESS-007. **Not in scope:** TRN-SESS-008 and later (GAP-03-007, HA-05); reflection prompts and answers; CYAN; any real provider (HARD-DEP-002). |
| Must become true | A Fixture Session with an accepted, VALIDATED mock AIOP-001 proof enters REFLECTION through a human controller Command. The committed facts record the proof reference, its MOCK_NON_PROOF class, the FIXTURE_MOCK source and the Fixture status. |
| Must remain true | HD-16, HD-19, HD-20; F04 semantics (analysis, acceptance, clustering, visibility); F02/F03/F08/F09 behaviour; the B0 Fixture identity. |
| Must remain impossible | A mock proof carrying a real Session into REFLECTION (HD-20), even under a misconfigured eligible set; a NON_PROOF result presented as real provider proof; REFLECTION without accepted, validated required analysis; REFLECTION while an AI operation is unresolved; a SYSTEM_SERVICE actor or a non-controller beginning REFLECTION; REFLECTION twice. |
| Falsifiers | `tests/e2e/test_pfc_b1_begin_reflection.py` (15 cases). |

## 2. Execution record

1. **RED.** 14 of 14 written cases failed for the right reasons: no route (404 ×5), no `BEGIN_REFLECTION` capability (×2), no `reflection_handler` or `reflection_proof` module, and envelope KeyErrors. Two falsifier corrections were made **before** the repair:
   - The in-progress case first tampered with `ai_generations`. PostgreSQL refuses `DISABLE TRIGGER` while F04's deferred integrity triggers are pending, so it was replaced by a legitimate scenario: failed clustering, then a controller RETRY that is authorized and not executed. A case pinning "a failed optional clustering does not block" was added.
   - "Right after BEGIN_ANALYSIS" answers `ANALYSIS_IN_PROGRESS`, because OA-1 is authorized and not yet executed, which F04's own `request_availability` classifies as unresolved. The failed-run case pins `REQUIRED_ANALYSIS_NOT_COMPLETED`.
2. **FBR.** TRN-SESS-007 exists in the domain topology (`session_transitions.py`, AI_VALIDATION_PROOF required), but no Command, handler, route, eligibility rule or projection realizes it, so every Session stays in ANALYSIS.
3. **Home.** 03 TRN-SESS-007 and HD-24.
4. **Repair.**
   - **`packages/application/reflection_proof.py` (new).** `ProofEligibility`, the `ReflectionProofSource` protocol, `FIXTURE_MOCK` (Fixture ∧ provider mock ∧ class MOCK_NON_PROOF), and `RealProviderProofSource(eligible_providers)`. It refuses the mock unconditionally and requires class PROVIDER_OUTPUT. The eligible set is **empty** (HARD-DEP-002).
   - **`ELIGIBLE_PROOF_SOURCES`** and **`decide_eligibility`**. The HD-20 reason is `MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION`; the Option 01 reason is `NO_ELIGIBLE_PROVIDER_PROOF`.
   - **`reflection_readiness(ports, session)`** is the one definition used by the Command and the projection:
     1. state ANALYSIS;
     2. no unresolved AIOP-001/002 operation (non-terminal generation, or latest authorization never executed; BND-017);
     3. accepted AIOP-001 artifact;
     4. its provenance resolves through the F04 write-once resolver (VALIDATED proof bound to the bytes → generation → provider → authorization → this Session's human BEGIN_ANALYSIS root);
     5. the frozen set verifies;
     6. a source admits the proof.
   - **`packages/application/reflection_handler.py` (new).** `begin_reflection`, CMD_BEGIN_REFLECTION:
     - replay guard, membership precheck (F09-2), stale check;
     - BND-007 TRN-SESS-007;
     - `_run`: BND-001 HUMAN_USER only, BINDING SESSION_CONTROL_RIGHT at `SESSION:<id>`;
     - readiness re-checked under the Session row lock;
     - one commit: ANALYSIS → REFLECTION;
     - event **SESSION_REFLECTION** carrying the proof reference, provider, proof class and source, `is_real_provider_proof` and `fixture`.
   - **API.** `POST /workspaces/{w}/sessions/{s}/transitions/begin-reflection`, via `http_f04.dispatch_begin_reflection`.
   - **Projection.** Position `actions.BEGIN_REFLECTION` (from readiness; relevant in ANALYSIS) and `reflection` (from the committed SESSION_REFLECTION event: class, source, `isRealProviderProof`, provider, artifact, proof, fixture).
   - **Test support.** `fixture` keyword in the F02/F03/F04 context builders (default False). The route was added to the F09-2 isolation sweep; its coverage guard requires this.
5. **Propagation.**
   - **AFFECTED:** the new Command path; position (additive keys); the event contract registry (+ SESSION_REFLECTION); the isolation sweep (+1 route: outsider, cross-URL and expiry cases all pass).
   - **NOT AFFECTED:** F04 analysis, acceptance and clustering (read only); authority vocabulary (the existing SESSION_CONTROL_RIGHT BINDING); the DB transition trigger (already legal in 03's topology); CYAN (out of scope).
6. **Local proof.** ruff, mypy (205 files), architecture check.
7. **Integration.**
   - **Falsifiers:** real HTTP → PostgreSQL, through the complete F02 → F03 → F04 chain.
   - **Real stack** (`evidence/b1_runtime_proof.txt`, two runs):
     - **Fixture Session:** 200 committed, MOCK_NON_PROOF / FIXTURE_MOCK / `isRealProviderProof: false`; REFLECTION; `proofMode` FIXTURE_NON_PROOF.
     - **Real Session:** 422 `MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION`; stays ANALYSIS; the capability reports the same reason.
     - **Real worker:** `session_read_model` shows REFLECTION | fixture=true and ANALYSIS | fixture=false. Diagnostics show 0 failed.
8. **Preservation.**
   - **HD-16:** there is no new AI run.
   - **HD-19:** the mock is only in the dev runtime, and its result is labelled.
   - **HD-20:** a falsifier, and the misconfigured-set case.
   - **Rule 11:** the SYSTEM_SERVICE actor is denied (falsifier).
   - **Full regression:** see item 9.
9. **Regression.** `evidence/b1_regression.txt`.
10. **Mutation.** **11/11 KILLED** (`evidence/b1_mutation_proof.txt`). The first run found a survivor: M04, the real-provider source admitting the mock. It is equivalent unless the eligible set is misconfigured to contain `"mock"`, and that is exactly the Option 01 misconfiguration that would silently break HD-20. The falsifier now proves that even that set refuses a mock proof for a real Session.
11. **Inverse.** Projection `reflection.proofClass = MOCK_NON_PROOF` traces back as follows:
    - the committed SESSION_REFLECTION event, whose `validation_proof_id` is the VALIDATED AIOP-001 proof;
    - that proof is bound to the accepted bytes;
    - which lead to generation (provider mock), then OA-1, then the human BINDING BEGIN_ANALYSIS of this Session;
    - the CommitUnit is CMD_BEGIN_REFLECTION, BINDING SESSION_CONTROL_RIGHT at `SESSION:<id>`;
    - the audit row records it;
    - the Session's `fixture = true` (immutable, B0).
12. **Deep sweep.**
    - **Semantic drift:** none; 03 TRN-SESS-007 is unchanged, and the proof source is the only variable.
    - **Authority leakage:** none.
    - **Cross-field:** F04 records are read only.
    - **Late clustering after REFLECTION:** its acceptance re-checks "Session still ANALYSIS" (REC-019) and fails closed.
13. **Inverse deep sweep.** Every REFLECTION traces to exactly one validated proof and one admitting source.

**Case 2 choices (recorded):**
- Required analysis is AIOP-001 (12 §39).
- A failed optional clustering does not block.
- Any unresolved AI operation of the Session blocks (BND-017).
- The event name `SESSION_REFLECTION` follows the existing `SESSION_<STATE>` naming.
- The projection reads the committed event (F08), not current state.

## 3. After B1 (derivation)
TRN-SESS-008 BEGIN_QUESTION_SELECTION requires "Reflection phase has been explicitly completed according to later contract" (03). That contract is GAP-03-007, `[UNDERDEFINED]`: whether answering all prompts is mandatory, whether zero answers count, whether responses are persisted (NQ-GAP-016 / HA-05), and whether human confirmation alone completes it. Nothing further in F05 is derivable, so the chain stops at REFLECTION. See HUMAN_AUTHORITY_QUEUE HA-21.

## 4. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B1`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F05: IN_PROGRESS for Fixture Sessions (REFLECTION reached); real Sessions remain on Option 01 (HA-02).
