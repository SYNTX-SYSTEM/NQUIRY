# NQUIRY_PRODUCT_FUNCTION_COMPLETION — HUMAN DECISIONS

Authoritative record of the Human Authority decisions taken inside the PFC
Field. Each decision is copied verbatim. The ledger entry lives in
`docs/architecture/16_DECISION_GAP_REGISTER.md` §41. HD numbering continues the
F02–F04 series (HD-1..HD-23).

---

## HD-24 — HA-01 REFLECTION gate: Option 03 for Fixture Sessions (2026-09-27)

**Question (HA-01):** by what legitimate path may a governed Session move from
ANALYSIS to REFLECTION (TRN-SESS-007 BEGIN_REFLECTION) while the only runtime
AI is the MockProvider? The options presented from the sources:
- 01: real provider lane (HARD-DEP-002 via NQ-DEC-024 / NQ-DEC-031);
- 02: decide NQ-GAP-024 (a recovery/bypass exit);
- 03: a mock proof may count for Fixture (NON_PROOF) Sessions only (REC-022
  scope, "not decided (F05)").

**Decision (human operator, verbatim):**

> Choose Option 03 as the current working path for Fixture Sessions.
>
> Keep Option 01 as the target path for real Sessions.
>
> Option 02 is not selected.
>
> Fixture Session semantics are hereby defined as follows:
>
> 1. A Session may be declared a Fixture Session only at Session creation.
> 2. The Fixture Session marker is immutable after creation.
> 3. A normal Session can never be converted into a Fixture Session.
> 4. A Fixture Session can never be converted into a real Session.
> 5. Every state, read model, API representation and projection that exposes Session proof semantics must preserve the Fixture / NON_PROOF status.
> 6. MockProvider results for Fixture Sessions may satisfy the controlled development proof path required to exercise and prove the REFLECTION lifecycle.
> 7. Such results remain NON_PROOF and must never be represented as real provider proof.
> 8. For non-Fixture Sessions, HD-20 remains fully binding: MockProvider proof does not satisfy the real proof requirement.
> 9. Real non-Fixture Sessions remain on Option 01 and therefore remain blocked by provider eligibility / HARD-DEP-002 until that external dependency is legitimately resolved.
> 10. BEGIN_REFLECTION remains a Human Controller Command requiring SESSION_CONTROL_RIGHT.
> 11. Existing SYSTEM_DERIVED REQUIRE / DENY semantics remain unchanged.
> 12. Implement the Option 03 path so that transition to Option 01 later requires changing only the eligible proof source, not redesigning the REFLECTION state path.
>
> This Human Authority Decision resolves HA-01 for Fixture Sessions.

**Ledger:** NQ-DEC-052 · 16 §41 REC-028.

**What it does not decide:**
- NQ-GAP-024 stays OPEN (Option 02 not selected).
- HARD-DEP-002 / NQ-GAP-060 stays EXTERNAL_DEPENDENCY (NQ-DEC-024, NQ-DEC-031 REQUIRED).
- Reflection completion (GAP-03-007) and reflection answer persistence (NQ-GAP-016, HA-05) remain undecided.
- Who may create a Fixture Session is not narrowed by the decision. It is the existing CMD_CREATE_SESSION authority, with the Fixture declaration as part of that Command.

---

## HD-25 — HA-21 Reflection completion: C-a together with C-c (2026-09-27)

**Question (HA-21, 03 §52 GAP-03-007):** what counts as "Reflection phase has
been explicitly completed according to later contract", the precondition of
TRN-SESS-008 BEGIN_QUESTION_SELECTION (required evidence: "SYSTEM_PROOF of
Reflection phase completion")? The options presented were:
- C-a: human procedural confirmation (named by 04 AUTH-DEP-SESS-008);
- C-b: answers required;
- C-c: zero answers count (together with C-a).

**Decision (human operator, verbatim):**

> Choose C-a together with C-c.
>
> Reflection completion is based on explicit human procedural confirmation.
>
> Zero persisted Reflection responses are permitted for completion.
>
> Reflection response persistence is NOT a precondition for TRN-SESS-008.
>
> HA-05 remains OPEN and decoupled from Reflection completion.
>
> The Human Controller holding SESSION_CONTROL_RIGHT is the Authority that may confirm Reflection completion.
>
> UI navigation does not constitute completion.
>
> AI output does not constitute completion.
>
> SYSTEM_DERIVED completion remains unavailable.
>
> If explicit human procedural confirmation cannot be established, the Session remains in REFLECTION.
>
> The completion proof basis must be audited as:
>
> HUMAN_PROCEDURAL_CONFIRMATION
>
> Do not invent a separate Reflection-complete state or transition if the accepted architecture does not define one.
>
> Materialize the confirmation through the existing TRN-SESS-008 / CMD_BEGIN_QUESTION_SELECTION path.
>
> A request to begin QUESTION_SELECTION without explicit Reflection completion confirmation must be refused.
>
> Fixture Sessions must preserve FIXTURE_NON_PROOF semantics after entering QUESTION_SELECTION.
>
> This decision closes HA-21.

**Ledger:** NQ-DEC-053 · 16 §41 REC-029.

**What it does not decide:**
- NQ-GAP-016 / HA-05 (reflection answer persistence) stays OPEN.
- AI reflection prompts (AIOP-016) stay outside the accepted AI scope (HD-21, HA-07).
- Question selection semantics beyond the existing architecture (NQ-GAP-026) are not touched.
