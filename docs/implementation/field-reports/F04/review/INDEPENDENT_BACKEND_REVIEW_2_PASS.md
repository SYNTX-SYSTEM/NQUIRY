# F04 independent backend re-review (pre-WU-04.8)

**Verdict:** `F04_BACKEND_REVIEW_PASS_PRE_WU04_8`

## Provenance

| Property | Value |
|---|---|
| Review mode | Independent, read-only (Claude Opus 5.5, separate session; no file modified by the reviewer) |
| Review session | `f778c2b3-09aa-4bc7-816c-b911cb710804` (Claude Code project `worktrees/f04-implementation`) |
| Instruction received | 2026-09-25T10:42:53.835Z |
| Verdict emitted | 2026-09-25T10:46:05.028Z |
| Transcript at persistence time | `~/.claude/projects/-home-codi-Entwicklung-nquiry-worktrees-f04-implementation/f778c2b3-09aa-4bc7-816c-b911cb710804.jsonl`, sha256 `f5f8d7f1ab4df018cc319b6a37f181f176ed97c26dc29e0a6ad234fbd36345c3` |
| Verdict text sha256 | `5d11d9fda8f616ff8b37174901bcf4ef105bca0c14112579e7e2b90ae6481b71` |
| Persisted by | WU-PFC-00 (predecessor consolidation), 2026-09-26, under explicit human authority |

The verdict below is copied **verbatim** from the review session. It was not edited. It reviewed the post-repair tree; the reconstruction in `CHECKPOINT_WU-PFC-00.md` shows that the committed tree is byte-identical to the tree it reviewed.

## Reviewer instruction (verbatim)

````text
<pasted_content id="ebdf">
R1 and R2 have now been repaired and re-proven by the F04 implementation field.

Re-run the COMPLETE independent systemic review against the CURRENT materialized F04 backend state.

Remain strictly READ ONLY.

Do not implement.
Do not modify files.
Do not repair during review.
Do not commit.
Do not push.
Do not enter WU-04.8.
Do not decide H-8.

Reconstruct the whole F04 field again before judging the repairs.

Re-run:

ARCHITECTURE BINDING
RECURSIVE DEEP SWEEP
INVERSE DEEP SWEEP
DATABASE PROOF REVIEW
PERSISTENCE REVIEW
AUTHORIZATION REVIEW
OPERATION IDENTITY REVIEW
EFFECT GATE REVIEW
RETRY / RECOVERY REVIEW
SUPERSESSION REVIEW
MOCK CEILING REVIEW
ANALYSIS OUTPUT REVIEW
F05 BOUNDARY REVIEW
CONCURRENCY REVIEW
FAILURE SEMANTICS REVIEW
BLUE / F03 REGRESSION REVIEW
R1 REPAIR REVIEW
R2 REPAIR REVIEW
EVIDENCE SUFFICIENCY REVIEW
FINAL FIELD RECONSTRUCTION

Explicitly verify that:

R1 is closed at its First Broken Relation.

R2 is closed at its First Broken Relation.

The repairs did not weaken tests.

The repairs did not bypass authority.

The repairs did not alter reviewed F04 semantics.

The real PostgreSQL proof still holds.

MOCK RESULT != PROOF still holds.

ANALYSIS OUTPUT != F05 PROOF still holds.

Accepted artifacts are correctly bound to their validation proofs.

HARD-DEP-002 remains external.

H-8 remains open.

WU-04.8 remains unentered.

BLUE remains unchanged.

Return exactly one of:

F04_BACKEND_REVIEW_PASS_PRE_WU04_8

or:

F04_BACKEND_REPAIR_REQUIRED

If repair is still required, return the COMPLETE remaining FBR repair set in ONE pass.

Do not perform fragmentary review.
Do not discover one issue at a time.
Review the entire field before producing the verdict.
</pasted_content id="ebdf">
````

## Reviewer verdict (verbatim)

# F04 independent backend re-review: pre-WU-04.8, read-only

## Verdict: **F04_BACKEND_REVIEW_PASS_PRE_WU04_8**

R1 and R2 are both closed where they first broke. I found no new material First Broken Relation anywhere in the field. This makes the **backend** a reviewed field before WU-04.8. It is not a complete field, not FIELD_GREEN and not published: WU-04.8 is still blocked on H-8, and the provider is still the MockProvider.

**How I reviewed:**
- **Rebuilt the change set exactly.** The previously reviewed bundle holds a checksum for every file. I compared all 83 against the current tree and rebuilt the pre-repair versions from the bundle, byte-exact.
- **What changed:** 3 production modules (`analysis_system`, `analysis_provenance`, `provenance_reader`), 3 tests, the mutation script, one new migration (`e7c1d4a9b206`) and one new test file. Every other source file is byte-identical to what the first review covered, so that reconstruction still holds. I re-swept each area below for effects of the new code.
- **Checked the database directly**, with read-only SQL on the runtime database, the test database and the shared databases.
- **Not re-run:** the test suites, the mutation script and the runtime proof. They write to the database, which this mode forbids. The pass counts below are the implementation's evidence, which I checked against the code and against persisted database state.

## R1: the accepted artifact is bound to what its proof validated — closed

- **Producer:** `_accept` now stores `content = response.raw_content`, the exact bytes the validator fingerprinted. `_canonical` is gone. Clusters and OA-3 are built from those same bytes, parsed.
- **Inverse chain:** the resolver now goes artifact → immutable proof. It requires the proof to be VALIDATED, for the same operation, and `sha256(content) = content_fingerprint = proof.output_fingerprint`. Otherwise it raises `ProvenanceBroken`. The chain is now the full §11 shape: "← persisted proof VALIDATED ← generation".
- **Database second line:** an immediate trigger, `trg_ai_derived_artifacts_validated_binding`, refuses to insert any accepted artifact without that binding.
- **Proven in the database:** on the recreated `nquiry_f04_red_runtime`, both accepted artifacts have content equal to the fingerprint and the fingerprint equal to the proof, with the proof VALIDATED, the generation VALIDATED and the provider `mock`.

## R2: no VALIDATED proof outside the acceptance bundle — closed

- **Producer:** `_finalize` never writes a VALIDATED proof. A denied acceptance is recorded as FAILED with `ACCEPTANCE_DENIED:<reason>`, the validated fingerprint goes in `failure_detail_ref`, there is no proof row, and RETRY stays legal.
- **Database second line:** two constraint triggers checked at commit. Together with R1's trigger they make "VALIDATED proof ⇔ VALIDATED generation ⇔ one accepted artifact" a persisted, two-way invariant. A proof rolled back inside a savepoint drops its pending trigger checks.
- **Proven in the database:** the runtime database has 0 orphan VALIDATED proofs and 0 VALIDATED generations without their proof and artifact.
- **Home note now true:** the 06 §16 note is accurate without an edit. C2-9 is withdrawn in IMPLEMENTATION_BINDINGS.

## The checks you asked for

| Check | Result |
|---|---|
| Tests not weakened | **Holds.** The denial test swaps "a proof exists" for the stricter "no proof, plus the fingerprint record". C7 still asserts UPDATE/DELETE are refused, now on a genuinely accepted artifact, and additionally asserts that a forged one is refused. There are 10 new binding tests and 3 new real-commit tests. The static guard "the resolver reads no mutable state" is unchanged and still covers the extended reader. |
| No authority bypassed | **Holds.** No effect-gate, resolver, BND or handler file changed (all byte-identical). The repair adds only persistence constraints. |
| Reviewed F04 semantics unchanged | **Holds.** No table, column, foreign key or uniqueness changed. The repair restores PI-1 and the 06 note. The Human-Authority alternative for R2 was not taken. The pinned architecture inputs still match their checksums, and the reviewed bundle is preserved (`c27af32d…`). |
| Real PostgreSQL proof still holds | **Holds.** Both F04 databases are at head `e7c1d4a9b206` and all three triggers are present (two deferred). Runtime chain: OA-1, then OA-2 RETRY, then OA-3. Exactly one `session:ANALYSIS` row. 5 SYSTEM_OPERATION audit rows, all by SYSTEM_SERVICE. `normalized_text` written 0. The test database is clean, no race clone databases are left over, and the shared `nquiry` / `nquiry_test` are unchanged at `f6b2c4d9a318`. |
| MOCK RESULT ≠ PROOF | **Holds.** 0 non-mock generations, 0 accepted artifacts that are not MOCK_NON_PROOF, and the projection marker is unchanged. |
| ANALYSIS OUTPUT ≠ F05 PROOF | **Holds, and is stronger.** A VALIDATED proof now implies an accepted artifact. HD-20 stays enforceable through proof → generation → `mock`. |
| Accepted artifacts bound to their proofs | **Holds.** The same binding is enforced in three places: the producer writes it, the resolver checks it, and the database refuses anything else. |
| Evidence sufficiency | **Sufficient.** Regression 1712 passed = 1699 + 13 new; no-DB run 888. Mutation proof 24/24 killed. The mutation-M21 case was handled correctly: a variant that could not survive against the mock was disclosed and re-targeted at the exact pre-repair code. The before-state is preserved in evidence. |

## The rest of the review

All of these were reviewed again and pass: architecture binding, both DeepSweeps, persistence, authorization, operation identity, the effect gate, RETRY / RECOVERY, supersession, analysis output, concurrency, and failure semantics. None of those source files changed.

Two points in failure semantics:
- A breached trigger at commit fails closed. The transaction rolls back and the generation stays RUNNING. That is within the disclosed stuck-generation ceiling (P8) and only happens if the invariant is violated.
- One minor inaccuracy: `test_r2_rejected_and_indeterminate_proofs_are_unchanged` only exercises REJECTED. The code path that stores INDETERMINATE proofs is logically unaffected, but no end-to-end test covers it.

## Status

| Item | Status |
|---|---|
| **HARD-DEP-002** | External and open. Only the mock adapter exists. |
| **H-8** | Open, for Human Authority. |
| **WU-04.8** | Not entered. BLOCKED_ON_H8_FOR_WU_04_8; `apps/web` has 0 changes. |
| **BLUE** | Unchanged: `c9d86ba`, 9 status entries. The main checkout is also unchanged at `c529d3d`, 32 entries. |
| **CYAN** | At `644e1c8`, now 44 entries (was 47). That churn comes from another session; F04 wrote nothing there. |
| **Carried forward, disclosed, not blocking** | Non-blocking findings 1–11 from the first review stay open. Items 3 and 4 must close before the HARD-DEP-002 lane opens; item 11 belongs to F08. |
| **Remaining Human Authority decisions** | H-8; commit and publication authority; what to do with the isolated databases (O-6); updating 20 §7 at publication (O-7); and optionally, whether BEGIN_ANALYSIS should be offered when no provider is configured. |

LOCAL_GREEN ≠ FIELD_GREEN ≠ REVIEWED_FIELD ≠ PUBLISHED_FIELD. This review makes only the backend, before WU-04.8, a reviewed field. It does not publish, does not cross H-8 and does not enter WU-04.8.
