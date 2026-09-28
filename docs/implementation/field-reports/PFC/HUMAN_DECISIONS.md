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

## HD-26 — HA-22 ImpactChain authoring authority: Option A, S1(i), S2(i) (2026-09-27)

**Question (HA-22):** who may create an ImpactChain (CMD_CREATE_IMPACT_CHAIN)
and append its human answer nodes (CMD_APPEND_IMPACT_CHAIN_NODE)? 04 has no
AUTH-DEP for either; 09 §63 keeps command activation blocked where authority
is undefined; 09 §86.1: "Exact authority to author Impact answers remains the
human inquiry actor under product flow and must not be inferred as a new
Decision Right". Options presented: A selector, B Session controller, C
participants, D split, E new explicit right, F no decision; secondary S1
mutability, S2 cardinality.

**Decision (human operator, verbatim):**

> Choose Option A.
>
> The holder of QUESTION_SELECTION_RIGHT who selected the current Primary Question is the sole Human Authority for authoring the Five-Why ImpactChain associated with that Primary Question.
>
> Authority semantics:
>
> 1. The same QUESTION_SELECTION_RIGHT holder may create the ImpactChain for the current Primary Question.
>
> 2. The same holder may append the human answer nodes for levels 1 through 5.
>
> 3. SESSION_CONTROL_RIGHT does not confer ImpactChain content authority.
>
> 4. PARTICIPATION alone does not confer ImpactChain authoring authority.
>
> 5. AI has no authority to create, append, generate, suggest, complete or substitute ImpactChain answers.
>
> 6. Each answer level is a human-authored content act.
>
> 7. No additional human confirmation is required after level 5.
>
> 8. ImpactChain completion is the derived structural fact that exactly levels 1 through 5 exist in valid successive order.
>
> Secondary decision S1:
>
> Choose S1(i).
>
> ImpactChain answer nodes are append-only.
>
> No stored answer may be silently edited, overwritten or replaced.
>
> Any future correction or supersession semantics require a separate authoritative decision and audited relation.
>
> Secondary decision S2:
>
> Choose S2(i).
>
> Exactly one ImpactChain exists per current Primary Question.
>
> A change of Primary Question does not silently reuse or mutate the existing chain.
>
> Replacement, invalidation or rebuild semantics remain governed by GAP-03-018 until separately resolved.
>
> Level ordering:
>
> Levels are strictly successive from 1 through 5 as already defined by the authoritative sources.
>
> Provenance:
>
> Every stored node must preserve its human author, level, capture time, chain identity, Session identity and Primary Question anchor.
>
> Fixture Sessions continue to preserve FIXTURE_NON_PROOF semantics.
>
> This Human Authority Decision closes HA-22.

**Ledger:** NQ-DEC-054 · 16 §41 REC-030.

**What it does not decide:**
- Correction or supersession of an answer node (needs a separate decision).
- GAP-03-018 (Primary Question replacement, ImpactChain invalidation/rebuild) stays `[UNDERDEFINED]`.
- NQ-GAP-026 (collaborative selection) and HA-13 (collaboration) are not touched.
- AI scope (HD-21, HA-07) is unchanged: no AI operation for Impact inquiry.
- GAP-03-008 (Investigation completion) is not touched.

## HD-27 — HA-03 CYAN / RED integration order: Option B (2026-09-27)

**Question (HA-03, F04 H-8):** the integration order of the SF (CYAN) line
with the backend (RED) lines, which diverge since 2026-09-26
(`pfc-integration` versus `frontend-symbiotic`).

**Decision (human operator, verbatim):**

> Option B.
>
> CYAN and RED remain separate Field lines.
>
> CYAN predecessor:
> field-SF-06 @ d3d9bd6
>
> RED producer:
> checkpoint-PFC-B5 @ 7d3f74e4685b821cc948f45e413c1...
>
> The RED producer is pinned.
> The moving pfc-integration branch is not a producer identity.
> No merge, rebase, publication or deployment is authorized.
> CYAN consumption does not upgrade RED status.
> FIXTURE_NON_PROOF and MOCK / NON_PROOF remain explicit ceilings.

**Identity resolution (verified at persistence, 2026-09-27):**
- CYAN predecessor `field-SF-06` → `d3d9bd6722bbddabeca56f18d468a8e78bfa294b`.
- RED producer `checkpoint-PFC-B5` → `7d3f74e4685b821cc948f45e413c1e0c207259d4`
  (signed annotated tag object `fd3d5600132e4dcb9203702d500daccf4c6d0439`). The
  decision's abbreviated hash is a prefix of this commit.

**Ledger:** NQ-DEC-055 · 16 §41 REC-031.

**What it does not decide:**
- No merge, rebase, publication or deployment of either line.
- No change to the RED producer checkpoint, and no RED status upgrade
  (TECHNICALLY_CLOSED stays; not REVIEWED_FIELD, not PUBLISHED_FIELD).
- No CYAN Work Unit, scope or content. CYAN remains out of scope for the RED
  autonomous run.
- The FIXTURE_NON_PROOF and MOCK / NON_PROOF ceilings are not lifted.

## HD-28 — Production account creation authority: Option A, host-operator command (2026-09-28)

**Question (HA-24; doc 24 §1 / §11.14 "ACCOUNT CREATION POLICY … The exact
product policy remains HUMAN_AUTHORITY_REQUIRED"; 04 §17 default deny, no
fallback to "system administrator"):** which authority may create a production
NQUIRY identity (user + local credential)? Options presented: A server-operator
command (host authority, no route); B a new in-app identity-admin right; C
creation by a Workspace governance root.

**Decision (human operator, verbatim):**

> Choose A.
>
> PRODUCTION ACCOUNT CREATION AUTHORITY DECISION
>
> 1. Authority model
>
> Use the server-operator command.
>
> Account creation on PRODUCTION is an explicit host/operator authority.
>
> Do not introduce:
> - a new in-app admin role
> - Workspace-owner account creation
> - public registration
> - self-service registration
>
> Identity creation remains separate from Workspace governance,
> membership, roles and Session authority.
>
> Record the host operator as:
>
> otti@condyn.eu
>
> 2. Credential lifecycle
>
> The credential may be set only at account creation for this Work Unit.
>
> Do not add operator password reset.
>
> Password reset is a separate authority relation and is explicitly
> out of scope for this Field.
>
> The production account-creation command must:
>
> - require explicit operator execution
> - work legitimately under NQUIRY_ENVIRONMENT=PRODUCTION
> - use the canonical application/domain identity creation path
> - hash the credential using the existing authentication mechanism
> - never persist plaintext credentials
> - never print the password to normal logs
> - reject duplicate identities
> - create no Workspace membership automatically
> - create no role automatically
> - create no governance authority automatically
> - create no Session authority automatically
> - record audit provenance for the creation

**Ledger:** NQ-DEC-056 · 16 §41 REC-032. Queue: HA-24.

**What it does not decide:**
- Password reset, credential rotation, account recovery or deactivation.
- Doc 24's account creation policy for external providers (OIDC, GAP-14-001):
  it stays fail-closed.
- HARD-DEP-001 (legitimate first Workspace governance root) and every
  membership, role, binding or participation relation: unchanged, product-only.
- Runtime DB-principal isolation (HA-09 / WU-AUTH-17): unchanged.
