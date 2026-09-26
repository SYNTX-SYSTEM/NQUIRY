# F04 independent backend review 1 (pre-WU-04.8)

**Verdict:** `F04_BACKEND_REPAIR_REQUIRED`

## Provenance

| Property | Value |
|---|---|
| Review mode | Independent, read-only (Claude Opus 5.5, separate session; no file modified by the reviewer) |
| Review session | `f778c2b3-09aa-4bc7-816c-b911cb710804` (Claude Code project `worktrees/f04-implementation`) |
| Instruction received | 2026-09-25T09:19:02.727Z |
| Verdict emitted | 2026-09-25T09:33:40.323Z |
| Transcript at persistence time | `~/.claude/projects/-home-codi-Entwicklung-nquiry-worktrees-f04-implementation/f778c2b3-09aa-4bc7-816c-b911cb710804.jsonl`, sha256 `f5f8d7f1ab4df018cc319b6a37f181f176ed97c26dc29e0a6ad234fbd36345c3` |
| Verdict text sha256 | `6585ff40b50cc87ae654f286f9c5f335fc124c6e53ddd971c4413da1fadd83c6` |
| Persisted by | WU-PFC-00 (predecessor consolidation), 2026-09-26, under explicit human authority |

The verdict below is copied **verbatim** from the review session. It was not edited. Its two material findings (FBR-F04-R1, FBR-F04-R2) are repaired in `REPAIR_R1_R2.md`. Its reviewed input is `review/BACKEND_REVIEW_BUNDLE.md` (sha256 `c27af32dd48d9e9157d766d3b0fcb4e7d4f7cf0791023095fa95ab32639bcf7f`).

## Reviewer instruction (verbatim)

````text
<pasted_content id="ebdf">
SFE::F04_INDEPENDENT_BACKEND_REVIEW

ROLE:
Independent F04 Backend Reviewer

MODE:
READ ONLY

MODEL:
Claude Opus 5.5

CONTEXT:
1M

EFFORT:
HIGH

WORKTREE:
/home/codi/Entwicklung/nquiry/worktrees/f04-implementation

PRIMARY DIRECTIVE:

Perform one complete independent systemic review of the materialized F04 backend field.

DO NOT IMPLEMENT.

DO NOT MODIFY FILES.

DO NOT REPAIR DURING REVIEW.

DO NOT COMMIT.

DO NOT PUSH.

DO NOT MODIFY BLUE.

DO NOT MODIFY CYAN.

DO NOT ENTER WU-04.8.

H-8 remains Human Authority.

First reconstruct the complete authoritative F04 architecture, revision 6, including PI-1 through PI-6 and all existing architecture/review evidence in this worktree.

Then reconstruct the actual materialized backend implementation and compare implementation against architecture as one complete field.

Use the full System Field Engineering procedure:

FIELD
+
RELATION
+
STATE
+
DELTA
+
BOUNDARY
+
AUTHORITY
+
RECONSTRUCTION

Perform:

1. COMPLETE FIELD RECONSTRUCTION
2. ARCHITECTURE TO IMPLEMENTATION BINDING
3. RECURSIVE DEEP SWEEP
4. INVERSE DEEP SWEEP
5. FAILURE SEMANTICS REVIEW
6. CONCURRENCY REVIEW
7. RETRY / RECOVERY REVIEW
8. SUPERSESSION REVIEW
9. AUTHORIZATION REVIEW
10. OPERATION IDENTITY REVIEW
11. EFFECT GATE REVIEW
12. PERSISTENCE REVIEW
13. REAL DATABASE PROOF REVIEW
14. MOCK BOUNDARY REVIEW
15. ANALYSIS OUTPUT CLASS REVIEW
16. F05 BOUNDARY REVIEW
17. REGRESSION REVIEW AGAINST F03 / BLUE
18. EVIDENCE SUFFICIENCY REVIEW
19. FIRST BROKEN RELATION ANALYSIS
20. FINAL FIELD RECONSTRUCTION

Preserve all reviewed laws, including:

QUESTION_CAPTURE
→ BEGIN_ANALYSIS
→ ANALYSIS

BEGIN_ANALYSIS belongs to F04.

Human Question Capture remains an F03 concern.

AUTHORIZATION IDENTITY
!=
OPERATION IDENTITY

REQUEST
!=
COMMIT

CANDIDATE
!=
EFFECT

RETRY
!=
RECOVERY

MOCK RESULT
!=
PROOF

PROVIDER RESULT
!=
CANONICAL EFFECT

ANALYSIS OUTPUT
!=
F05 PROOF

Review operation-scoped authorization.

Review AIOP-001 and AIOP-002.

Review superseded Authorization semantics.

Review SYSTEM_OPERATION Effect Gate semantics.

Review Analysis Output classes.

Review MockProvider boundaries.

Review persistence and inverse reconstruction.

Review meaningful concurrency cases.

Review the actual PostgreSQL proof produced during implementation.

Review HARD-DEP-002 exactly as an external dependency.

Do not treat HARD-DEP-002 as closed.

Review all implementation-time repairs.

Determine whether they are legitimate First Broken Relation repairs or whether any repair weakened tests, bypassed authority, introduced convention, or changed architecture semantics.

IMPORTANT:

Do not review fragment by fragment and then repeatedly discover new defects.

Reconstruct the entire field first.

Identify ALL material First Broken Relations in one complete review pass.

If defects exist, produce ONE COMPLETE REPAIR SET.

For every defect provide:

FBR ID

VISIBLE EFFECT

BACKWARD TRACE:
consumer
→ relation
→ producer
→ authority
→ state
→ first broken relation

AUTHORITATIVE HOME

WHY IT IS BROKEN

MINIMUM LEGITIMATE ROOT REPAIR

PROPAGATION SURFACE

MUST BECOME TRUE

MUST REMAIN IMPOSSIBLE

FALSIFIER

REQUIRED RE-PROOF

Do not implement the repair.

If no material defect remains, return:

F04_BACKEND_REVIEW_PASS_PRE_WU04_8

If material defects remain, return:

F04_BACKEND_REPAIR_REQUIRED

followed by the COMPLETE repair set.

Also explicitly report:

H-8 status

WU-04.8 status

HARD-DEP-002 status

BLUE regression status

database proof status

mock ceiling status

remaining Human Authority decisions

FINAL RULE:

LOCAL_GREEN
!=
FIELD_GREEN
!=
REVIEWED_FIELD
!=
PUBLISHED_FIELD

This review may establish REVIEWED_FIELD only if the complete field passes.

It may not publish.

It may not cross H-8.

It may not enter WU-04.8.
</pasted_content id="ebdf">
````

## Reviewer verdict (verbatim)

# F04 independent backend review: pre-WU-04.8, read-only

## Verdict: **F04_BACKEND_REPAIR_REQUIRED**

The backend is close. The authorization model, supersession, RETRY/RECOVERY, SYSTEM_OPERATION, concurrency and the mock lane all match revision 6 and PI-1..PI-6. Two material First Broken Relations remain. Both sit on one relation that PI-1 defines: the accepted effect must provably *be* the VALIDATED candidate and its persisted proof.

So **REVIEWED_FIELD is not established.** I published nothing, crossed no H-8 and did not enter WU-04.8.

**How I reviewed:**
- **Read:** all of revision 6 (§0.1 rules 1-9, §5/§6/§9/§11/§15/§16), HUMAN_DECISIONS, FIELD_REVIEW, IMPLEMENTATION_BINDINGS (PI-1..PI-6, C2-1..13, I1..I3), PROOF_MATRIX, SWEEPS, the WU reports and the evidence. Also both migrations, every new or changed package module, the rewritten PKG-era tests, and the F04 tests.
- **Read-only SQL** on the isolated databases (`SET default_transaction_read_only`).
- **Not re-executed:** the test suites, the mutation script and the runtime proof. They write rows and create clone databases, which this mode forbids. So the pass counts are the implementer's evidence, checked here against code and persisted database state.
- **Pinned architecture inputs:** sha256 still matches FIELD_REVIEW for the reconstruction, HUMAN_DECISIONS, 16, 20 and the rev-6 bundle. The 04/06/08/09 edits are additive only (+56/−0).

---

## Material First Broken Relations

### FBR-F04-R1: the accepted artifact is not bound to the output its proof validated

**VISIBLE EFFECT**
- In the runtime database `nquiry_f04_red_runtime`, both accepted artifacts have `sha256(content) ≠ content_fingerprint`. I confirmed this with a read-only query.
- The inverse resolver never visits the proof.
- Nothing persisted shows that the accepted content is the validated output.

**BACKWARD TRACE**
- **Consumer:** the inverse resolver (E16/K17/K19), F05's HD-20 and REFLECTION check, and any auditor.
- **Relation:** artifact ≡ VALIDATED candidate ≡ proof over the same bytes.
- **Producer:** `_accept` in `packages/application/analysis_system.py:585-586`. It writes `content=_canonical(validation.payload)` (compact separators, `ensure_ascii=False`) but copies `content_fingerprint=proof.output_fingerprint`. That fingerprint is sha256 of the raw provider bytes (`mock.py:110`, default separators). The raw output is persisted nowhere.
- **Authority:** 09 §118 (the output fingerprint plus the proof reference, "mandatory for high-assurance use"). Also reconstruction §11 items 2a/2b/4a/4b ("← BND-010 ← persisted proof VALIDATED ← generation") and PI-1.
- **State:** three different byte sequences are in play, and only two of them match.
- **First broken relation:** `_accept` persists a re-serialization under the fingerprint of different bytes. On top of that, `analysis_provenance._link` (`analysis_provenance.py:74`) walks artifact → generation → OA → audits and skips the immutable proof link that §11 requires.

**AUTHORITATIVE HOME:** 09 §118, F04 §11 and §0.1 rule 8, PI-1.

**WHY IT IS BROKEN:** CANDIDATE ≠ EFFECT requires the effect to be *derived from* the candidate in a way that can be checked. Today the equivalence rests on trusting code, not on persisted records. The materialized E16 chain is also shorter than the reviewed branch 2b.

**MINIMUM LEGITIMATE ROOT REPAIR**
1. `_accept` persists `content = candidate.response.raw_content`, the exact bytes the validator fingerprinted. The projection already calls `json.loads` on the content, and clusters come from the same parsed bytes.
2. `resolve_provenance` reads the immutable proof by generation id. It requires `validation_result = VALIDATED`, the same operation, and `sha256(content) == content_fingerprint == proof.output_fingerprint`. Otherwise it raises `ProvenanceBroken`.
3. Recommended second line: an insert trigger on accepted `ai_derived_artifacts` rows (`session_id NOT NULL`). It requires a VALIDATED proof for the generation with a matching fingerprint and `encode(sha256(convert_to(content,'UTF8')),'hex') = content_fingerprint`. The proof is already inserted first (`:578`).

**PROPAGATION SURFACE**
- Code: `analysis_system._accept`, `analysis_provenance`, `provenance_reader` (a new `ProofFact`), and optionally a migration.
- Tests: E1/E2, the K group, `test_f04_inverse_provenance.py` (P1-P6), and the runtime driver.
- Docs: PROOF_MATRIX, SWEEPS §2.
- The two runtime artifacts are append-only and stay pre-repair. Either recreate `nquiry_f04_red_runtime` or disclose them.

**MUST BECOME TRUE:** every accepted artifact's content is byte-identical to the validated output, and the persisted-only chain includes proof VALIDATED.

**MUST REMAIN IMPOSSIBLE:** an accepted artifact whose content differs from the validated bytes, and a provenance chain that resolves without a VALIDATED proof.

**FALSIFIER:** the fingerprint equality holds for every accepted artifact. The resolver raises on a missing, REJECTED or mismatched proof. New mutations are killed: M21 (re-serialized content) and M22 (resolver skips the proof).

**REQUIRED RE-PROOF:** the F04 suite, the inverse tests, the mutation script, the runtime proof on a fresh isolated database, and full regression.

### FBR-F04-R2: a VALIDATED proof is persisted outside the PI-1 acceptance bundle

**VISIBLE EFFECT**
- If the acceptance commit fails or is denied, the generation becomes FAILED (`ACCEPTANCE_DENIED:*`) with no artifact.
- An immutable `ai_validation_proofs` row with result **VALIDATED** is still persisted.
- A test asserts exactly that (`tests/e2e/test_f04_analysis_run.py:379`).

**BACKWARD TRACE**
- **Consumer:** F05 BEGIN_REFLECTION. 03 TRN-SESS-007 requires "AI_VALIDATION_PROOF that required analysis operations completed". Also the HD-20 enforcement that reads proofs.
- **Relation:** a persisted VALIDATED proof implies an accepted artifact in the same commit.
- **Producer:** `run_authorized_operation` calls `finish(ACCEPTANCE_DENIED)`, then `_finalize` writes `candidate.proof` (`analysis_system.py:723`, `:826`).
- **Authority:** PI-1. Also the authoritative home note written in this very materialization, `06_BOUNDARY_ARCHITECTURE.md:1907-1915`: VALIDATED, the persisted proof and the accepted artifact "are committed in one atomic bundle".
- **First broken relation:** C2-9 (IMPLEMENTATION_BINDINGS:43) was classified Case 2. It is not: it changes what a persisted VALIDATED proof means for the F05 consumer, and it contradicts the 06 home note.

**AUTHORITATIVE HOME:** PI-1, 06 §16 note, 08 §23 (AI_VALIDATION_PROOF "may contribute … toward BEGIN_REFLECTION").

**MINIMUM LEGITIMATE ROOT REPAIR**
- In the acceptance-failure branch, persist no VALIDATED proof.
- Record OUTPUT_RECEIVED → FAILED with `failure_code = ACCEPTANCE_DENIED:<reason>` and the validated output fingerprint in `failure_detail_ref`.
- RETRY stays legal. REJECTED and INDETERMINATE proofs are unchanged.
- Recommended second line: a deferred constraint trigger. At commit it requires every VALIDATED proof to have an accepted artifact for the same generation.
- The alternative is to keep the proof, amend the 06 note, and record an F05 obligation that "proof VALIDATED is necessary, not sufficient". That redefines a proof class, so it is a **Human Authority** choice, not Case 2.

**PROPAGATION SURFACE:** `_finalize` or `finish`, the acceptance-denial test, C2-9 and SWEEPS O-2, and an optional migration.

**MUST BECOME TRUE:** a VALIDATED proof exists if and only if its generation is VALIDATED and has exactly one accepted artifact.

**MUST REMAIN IMPOSSIBLE:** a VALIDATED proof on a FAILED generation, and a RETRY blocked by a denied acceptance.

**FALSIFIER:** the updated denial test finds no VALIDATED proof, and RETRY is still legal. With the trigger, a real-commit test (clone database) refuses a VALIDATED proof that has no artifact. Mutation M23 (persist the proof on denial) is killed.

**REQUIRED RE-PROOF:** E-group, mutation script, full regression.

---

## Review areas (1-20)

| Area | Result |
|---|---|
| Field and binding (§0.1, §5, §6, §9, §16; PI-1..6) | Matches, except R1/R2 at PI-1. O-1 is acceptable: the ANALYSIS predicate is enforced by the SYSTEM_OPERATION resolver, so BND-007 is not used on the system path |
| OA identity, AIOP-001/002 | UNIQUE (command, operation) on OA rows and on generations. C9 holds: an AIOP-001 run and an AIOP-002 run can share BEGIN_ANALYSIS. The shape CHECK matches the four legal shapes |
| Supersession, RETRY / RECOVERY | Enforced three times: the resolver's latest check, a generation insert trigger, and the OA insert trigger (which checks the predecessor's state and requires `retry_of` only for RETRY). E17/E18 are correct |
| SYSTEM_OPERATION effect gate | One resolver serves both precommit and BND-014. Fixed service id; the authorizing command and the chain root must be COMMITTED; X is always read from its persisted reference |
| Authorization | BINDING `SESSION_CONTROL_RIGHT` at `SESSION:<id>` through the F02 `_run`. Participant, Owner and outsider are denied |
| Concurrency | Session row lock (`FOR NO KEY UPDATE`) first on every F04 path, with database constraints as a second line. The six real-connection races are credible |
| Failure / retry / recovery | Honest endings. Stuck RUNNING is the disclosed ceiling P8 |
| Persistence | Immutability triggers exist (verified in the runtime database). A downgrade restores the pre-F04 trigger function byte-identically. R1 and R2 are the gaps |
| Real database proof | Runtime database state matches the claims: OA-1, OA-2 RETRY, OA-3; 3 generations; exactly one `session:ANALYSIS` row; `normalized_text` written 0. Shared `nquiry` and `nquiry_test` are unchanged at `f6b2c4d9a318`. No `race_*` clone databases left over |
| Mock boundary | F1 refusal proven on a real process. Only the mock adapter exists, with no egress. STAGING and an unset environment are refused (stricter than required, which is legitimate) |
| Analysis output class | The HD-18 schema is closed: no new-question field, no priority field. Artifacts are MOCK_NON_PROOF; the projection marks them AI · PROPOSAL · MOCK / NON_PROOF |
| F05 boundary | BEGIN_REFLECTION is untouched. The HD-20 hook (proof → generation → provider) exists. R2 must close before F05 consumes proofs |
| Implementation-time repairs | I1, I2 and I3 are legitimate root repairs. The PKG-era test rewrites move each intent to a named new home; partial output → REJECTED is backed by §15 D4. No test was weakened and no authority is bypassed. **C2-9 is misclassified (R2)** |
| F03 / BLUE regression | The BND-008 change and its twin only narrow AI during the Burst, as FBR-F04-3 intends. No F03 test was edited |

## Non-blocking findings (disclose now; the tagged ones are due before HARD-DEP-002)

1. **Rule 5 "never executed later" rests on the call graph alone.** The resolver has no timing predicate. Add a static gate: only `http_f04._run_after_commit` and the in-function follow-up may call `run_authorized_operation`.
2. **The follow-up run picks its OA indirectly.** It selects `latest(AIOP-002)` with a matching X (`:834`) instead of the OA-3 id the acceptance commit just created. It can therefore execute a controller's OA-4. That is harmless, because each OA is consumed once, but it should use the OA-3 id.
3. **[Before HARD-DEP-002] The Gateway maps only two exceptions to FAILED.** Only `ProviderTimeout` and `ProviderError` become FAILED (`gateway.py:88-90`). Any other adapter exception leaves the generation stuck RUNNING, which widens P8. This cannot happen with the mock.
4. **[Before HARD-DEP-002 / WU-04.8] Provider text can reach an unmarked field.** The validator echoes provider-controlled values (`validator.py:116`) into `failure_code`, which is projected as `reasonCode` without an AI marker.
5. **Cluster runs are append-only but not closed.** A later INSERT into an accepted run is not prevented at database level.
6. **The BEGIN_ANALYSIS capability omits UNRESOLVED_CAPTURE** (`inquiry_queries.py:476`). The command still blocks, but the "one shared definition" claim is inexact.
7. **Case-mismatch requests are recorded as DENIED/PRECONDITION_UNMET**, while the response says `rejected`.
8. **D6 is structure-only under a content-blind mock.** The PROOF_MATRIX row should carry the mock-ceiling caveat.
9. **Session→Burst lock order (BEGIN) is the inverse of F03 completion's Burst→Session.** Only a stale-state begin racing completion can hit it, and it fails safe (deadlock abort, no state change).
10. **Inherited, not F04's:** the runtime role `nquiry` is superuser/bypassrls, so RLS on the new tables is declared but not exercised.
11. **No outbox event for effect-free endings.** FAILED and REJECTED emit nothing, although §10 lists `AI_GENERATION_*` for F08. Record it as an F08 relation.

## Status report

| Item | Status |
|---|---|
| **H-8** | OPEN, Human Authority. CYAN is now at `644e1c8` (47 entries, another session), which differs from the `447b24e`/`c944b95` the architecture recorded |
| **WU-04.8** | BLOCKED_ON_H8_FOR_WU_04_8. Not entered; `apps/web` is unchanged |
| **HARD-DEP-002** | OPEN, external, not closed. There is no real adapter; any other provider value is refused and no provider means UNAVAILABLE. Items 3 and 4 above bind to its lane |
| **BLUE regression** | No BLUE change. Still at `c9d86ba` with 9 entries, and the main checkout at `c529d3d` with 32, both as recorded. The claim that F03 is green (1699/2) comes from evidence; I did not re-run it |
| **Database proof** | Real PostgreSQL on isolated databases. Constraints and triggers are present, and persisted state matches the claims apart from the R1 defect, which the database itself shows |
| **Mock ceiling** | Holds. MOCK RESULT ≠ PROOF, and ANALYSIS OUTPUT ≠ F05 PROOF, once R2 is fixed |
| **Remaining Human Authority decisions** | H-8. Choosing the R2 alternative, if preferred. Commit and publication authority. What to do with the isolated databases (O-6). The 20 §7 update at publication (O-7). Optionally, whether BEGIN_ANALYSIS may be offered when no provider is configured, since it leads to an irreversible ANALYSIS with NQ-GAP-024 open |

LOCAL_GREEN ≠ FIELD_GREEN ≠ REVIEWED_FIELD ≠ PUBLISHED_FIELD. After R1 and R2 are repaired and re-proven, this review can be re-run for **F04_BACKEND_REVIEW_PASS_PRE_WU04_8**. I can also turn this report into a shareable page if that helps relay it.
