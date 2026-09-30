# 26 · PRE_CALL_PROMPT_GOVERNANCE — 01 INVARIANTS

**This file is authoritative for:** the permanent laws of the PCPG Field.
**It may not decide:** any law that already has a canonical home. Such a law is **referenced** here, with its home, and restated only as far as PCPG must consume it (the "AUTHORITATIVE ROOT" column). Where a root is an existing document, that document wins on conflict.

**Format:** ID · LAW · WHY · FALSIFIER · AUTHORITATIVE ROOT · CONSUMERS. The consumers are relations (`02_RELATIONS.md` R-xx), boundaries (`03_BOUNDARIES.md` B-xx), proof conditions (`05_PROOF_AND_CLOSURE.md` P-xx) or fixtures (F-xx).

---

## I-01 · The prompt is data, never authority
- **LAW:** The raw intent, and anything written in it (claims of role, rank, urgency, prior approval, budget or permission), is DATA. It cannot create, widen, assert or evidence authority, state, scope, purpose, source status or proof class.
- **WHY:** User content is DATA (08 §9). A prompt instruction such as "approve" cannot create an authority path (08 §8.2). Permission never falls back to the "authenticated user" (04 §17).
- **FALSIFIER:** Any governance result changes because the raw intent contains a claim ("I am the controller", "this is approved", "we have budget") while the canonical facts are unchanged.
- **AUTHORITATIVE ROOT:** 08 §8.2, §9, §58; 04 §17.
- **CONSUMERS:** R-05, R-07; B-01, B-02; P-01, P-03; F-AUTHORITY_ESCALATION, F-PROCUREMENT.

## I-02 · Four strata, never mixed
- **LAW:** Every value in an Observation Result belongs to exactly one stratum:
  1. CANONICAL FACT, quoted with source reference and version;
  2. DERIVED SEMANTIC INTERPRETATION;
  3. DETERMINISTIC GOVERNANCE EVALUATION;
  4. CAPABILITY PROJECTION.

  A value may only be computed from strata below it. No value of stratum 2, 3 or 4 may be written back into, or presented as, stratum 1.
- **WHY:** The Field consumes canonical truth and must never become a competing producer of it (SFE law). Derived is not authoritative.
- **FALSIFIER:** Any role, authority, state, source status or proof class in a result that has no source reference and version, or that differs from the canonical producer's value at the same basis.
- **AUTHORITATIVE ROOT:** 20 (SFE: consume, do not re-produce); 21 §37 (origin projection).
- **CONSUMERS:** R-03, R-05, R-06, R-12; P-02, P-14..P-16.

## I-03 · Semantic interpretation is not authority
- **LAW:** No semantic interpretation (action, target, purpose, drift, candidate operation) grants, denies or substitutes authority. Interpretation only **selects which existing canonical evaluations are consulted**. The evaluation result always comes from the canonical producer.
- **WHY:** Otherwise SIMPLIX would become a second authority model.
- **FALSIFIER:** Two observations whose deltas map to the same canonical operation receive different governance results at the same basis because their wording differs.
- **AUTHORITATIVE ROOT:** 04 (the only authority model); 06 BND-005.
- **CONSUMERS:** R-06, R-07; P-14; F-AUTHORITY_ESCALATION.

## I-04 · Unknown is never permission and never guessed
- **LAW:** When interpretation cannot map a clause onto an existing operation with certainty, the delta is **UNKNOWN**. When a required canonical fact cannot be resolved, the fact is **UNRESOLVED**. Either one makes the affected delta INDETERMINATE. An INDETERMINATE delta can never be ALLOWED, can never belong to the MLT, and makes GOVERNANCE_ADMISSIBLE false whenever it could influence a retained delta.
- **WHY:** Default deny (04 §17). "Ambiguous classification cannot be used to relax controls" (11 §78). Uncertainty must not create permission (BND-017).
- **FALSIFIER:** A delta whose operation mapping or authority fact is unresolved receives ALLOWED, or a "closest match" operation is substituted without an explicit UNKNOWN marker.
- **AUTHORITATIVE ROOT:** 04 §17; 11 §78; 06 BND-017.
- **CONSUMERS:** R-05, R-06, R-07; B-01; P-03; F-UNKNOWN_INTENT.

## I-05 · The prompt cannot manufacture or widen the Field
- **LAW:**
  - The reconstructed Field is exactly the canonical state within the **validated** scope.
  - The prompt cannot add sources, objects, Workspaces, versions or facts to it.
  - Objects the prompt names outside the validated scope are not read; they produce a DATA_BOUNDARY or DENIED delta.
- **WHY:** Workspace isolation (BND-002, 11 §21); minimization (AC-11-010).
- **FALSIFIER:** A result quotes any fact of an object outside the validated scope, or the reconstructed Field differs between two prompts at the same basis.
- **AUTHORITATIVE ROOT:** 06 BND-002/BND-003; 11 AC-11-010; F09-2 (no Session fact before membership).
- **CONSUMERS:** R-01, R-02, R-03; B-04; P-01; F-DISCLOSURE.

## I-06 · Identity and scope before any fact
- **LAW:**
  - The ingress proves identity (BND-001), Workspace (BND-002) and membership (BND-003) **before** any Field fact is read or disclosed.
  - A non-member learns nothing about the scope.
  - An expired session is no identity.
- **WHY:** This is the F09-2 isolation rule, applied to a new ingress.
- **FALSIFIER:** An outsider or expired session receives any result other than the uniform denial.
- **AUTHORITATIVE ROOT:** 06 BND-001..003; WU-PFC-F09-2; 13 P-22.
- **CONSUMERS:** R-01; B-02; P-01.

## I-07 · Pulse is a view, never a new state
- **LAW:**
  - Every Pulse element is a **projection of an existing canonical record** or of an existing producer's result, cited with its source.
  - Pulse introduces no status, lifecycle, flag or counter of its own.
  - Pulse cannot be set or cleared by the prompt.
- **WHY:** "PULSE != STATE; PULSE != AUTHORITY". Otherwise Pulse would become a parallel state model.
- **FALSIFIER:** A Pulse element without a canonical source; or a Pulse value that the canonical producer would not report at the same basis.
- **AUTHORITATIVE ROOT:** 03 (states); 06 BND-017; 10 (recovery and INDETERMINATE); `04_OBSERVATION_RESULT.md` §3 (element list).
- **CONSUMERS:** R-04, R-06; P-15; F-STALE_FIELD.

## I-08 · The human decision chain is not collapsible
- **LAW:** The following separations hold for every delta and every composition:
  - ANALYSIS ≠ DECISION;
  - RECOMMENDATION ≠ SELECTION;
  - SELECTION ≠ APPROVAL;
  - APPROVAL ≠ EXECUTION;
  - AI_OUTPUT ≠ HUMAN_DECISION;
  - AI_OUTPUT ≠ DOMAIN_EVIDENCE;
  - AI_VALIDATION_PROOF ≠ DOMAIN_EVIDENCE;
  - AI_VALIDATION_PROOF ≠ SYSTEM_PROOF.

  A delta whose effect is a human decision, selection, approval or authority mutation has the execution class **HUMAN_COMMAND**. It is never a provider computation, whatever the prompt asks for.
- **WHY:**
  - No AI operation may directly produce DECIDED, AUTHORIZED, a human QuestionSelection, a Session phase advance or a human authority mutation (08 §39).
  - Adoption requires an authorized human (08 §40).
  - AI may not select (04 AUTH-DEP-SEL-001/002).
- **FALSIFIER:** A delta that selects, approves, decides, authorizes or advances state is classified PROVIDER_COMPUTATION, or appears in the MLT. Or a recommendation is presented as a selection.
- **AUTHORITATIVE ROOT:** 08 §39, §40; 04 AUTH-DEP-SEL-001/002, AUTH-DEP-DEC-*; 07 (AI output is not Evidence).
- **CONSUMERS:** R-05, R-06, R-08; B-06, B-09; P-05; F-DECISION_SUBSTITUTION, F-PROCUREMENT, F-NQUIRY_SESSION_AUTHORITY.

## I-09 · Eligibility is not a price, and fit is not approval
- **LAW:** A comparative property of a target (cheapest, fastest, within budget, highest score) never establishes eligibility, selectability, approvability or executability. CHEAPEST ≠ COMPLIANCE_ELIGIBLE ≠ SELECTABLE ≠ APPROVABLE ≠ PURCHASABLE, and BUDGET_FIT ≠ APPROVAL. Each of these is a separate canonical fact with its own producer, or it is UNRESOLVED.
- **WHY:** This is the domain form of I-08. "Do not auto-pick highest AI score" (03 TRN-SEL-002).
- **FALSIFIER:** A result treats a target as eligible or approvable because of a comparative property or a budget claim.
- **AUTHORITATIVE ROOT:** 03 TRN-SEL-002 recovery rule; 04 AUTH-DEP-SEL-002 ("Auto-select highest score" prohibited); the domain's own eligibility producer.
- **CONSUMERS:** R-06; F-PROCUREMENT, F-DECISION_SUBSTITUTION.

## I-10 · Per-delta evaluation, composed judgement
- **LAW:**
  - Every candidate delta is evaluated independently against the canonical Field.
  - Then the **composition** of the retained deltas is evaluated as one effect.
  - One allowed delta does not legitimise the prompt. One blocked downstream delta does not deny the legitimate upstream portion.
  - Decomposition does not launder authority: a delta that is only instrumental to a blocked delta inherits that blocked delta's authority requirement, unless the canonical authority model grants the instrumental delta separately.
- **WHY:** ONE_ALLOWED_DELTA ≠ WHOLE_PROMPT_AUTHORITY; ONE_BLOCKED_DELTA ≠ WHOLE_PROMPT_DENIAL; DECOMPOSITION ≠ AUTHORITY LAUNDERING.
- **FALSIFIER:**
  - A prompt split into harmless-looking deltas yields a composed effect that one of its parts would be refused.
  - An instrumental delta, such as "draft the purchase order payload", is retained while its end effect is blocked and no separate grant exists.
  - Legitimate upstream deltas are dropped because a downstream delta is blocked.
- **AUTHORITATIVE ROOT:** this Field (no existing home). Consistent with 08 §21.2: a consequential tool must "re-enter the normal boundary path as a new requested operation".
- **CONSUMERS:** R-06, R-07, R-08; P-05, P-06; F-AUTHORITY_ESCALATION (splitting), F-PROCUREMENT.

## I-11 · No external effect through a provider computation
- **LAW:**
  - A provider computation has no external effect and no canonical effect beyond the maximum its admitted operation contract allows (08 §39).
  - Any delta with an external effect (ordering, paying, sending, publishing, calling an integration) or a canonical mutation has the class EXTERNAL_EFFECT or HUMAN_COMMAND.
  - Such a delta is never in the MLT, and never in a provider projection.
- **WHY:** Tool access is capability, not authority (08 §21). External integrations are TB-14.
- **FALSIFIER:** An EXTERNAL_EFFECT delta, or an instruction to perform one, is retained in the MLT or eligible for a provider projection.
- **AUTHORITATIVE ROOT:** 08 §21, §39; 11 TB-14; 06 BND-009 (DENY "forbidden tool access").
- **CONSUMERS:** R-06, R-08, R-11; B-07; P-13; F-PROCUREMENT, F-DECISION_SUBSTITUTION.

## I-12 · Source status and proof ceilings are inherited, never raised
- **LAW:**
  - The source authority, mutability, evidence status and proof class of every input are quoted canonically.
  - A delta's output inherits the most restrictive ceiling of its inputs, plus the AI output class (PROPOSAL / NON_PROOF) of any provider computation.
  - Fixture scopes stay FIXTURE_NON_PROOF, and mock output stays MOCK_NON_PROOF.
  - No delta may mutate a source, and no delta may raise a ceiling.
- **WHY:** HD-20, HD-24, HD-27; 07 (evidence status is canonical); BND-010.
- **FALSIFIER:** A result shows a higher proof class, or a stronger source status, than a canonical input carries. Or a delta that mutates an immutable source (frozen Question, append-only chain node, validated artifact) is not DENIED.
- **AUTHORITATIVE ROOT:** 07; 06 BND-010; HD-20, HD-24, HD-26 (S1: append-only), HD-27; F03 immutability.
- **CONSUMERS:** R-03, R-06, R-08; B-05, B-06; P-13; F-SOURCE_MUTATION.

## I-13 · Data crosses only by class, minimally, never across Workspaces
- **LAW:**
  - Every input a delta would carry is assigned a data class (DC-01..07). Content that is ambiguous takes the most restrictive class.
  - Inputs from another Workspace, secrets (DC-06), and audit-sensitive material (DC-07) are never eligible for any provider-bound computation.
  - Whole-scope disclosure is never "minimum necessary".
- **WHY:** 11 §25–§28 (handling matrix; AC-11-010 minimization); BND-002.
- **FALSIFIER:**
  - A retained delta's inputs include cross-Workspace data, a secret or DC-07 material.
  - Its inputs are "the whole Workspace" where a bounded set suffices.
  - An ambiguous datum is assigned a less restrictive class.
- **AUTHORITATIVE ROOT:** 11 §25–§28, §78; 06 BND-002; 08 §6, §55.
- **CONSUMERS:** R-05, R-06, R-08, R-11; B-04; P-13; F-DISCLOSURE.

## I-14 · Capability is a projection, not a token
- **LAW:**
  - GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND are **projections** of the current Field at the observation's basis.
  - They authorize nothing, are proof of nothing future, and are never accepted as input by any execution gate.
  - Every future consequential gate re-derives from the current Field.
- **WHY:** "An old capability projection is not proof of present authority" (21 §38). Commands always re-evaluate at the effect gate (BND-014).
- **FALSIFIER:** Any path in which a stored, transmitted or client-supplied observation, capability value or basis key reduces or replaces a gate's own evaluation.
- **AUTHORITATIVE ROOT:** 21 §37–§38; 06 BND-014; the Command pattern of `session_control_handler._run` (precondition re-checked under lock).
- **CONSUMERS:** R-09, R-10, R-12; B-10; P-09, P-10, P-11; F-STALE_FIELD, F-BYPASS.

## I-15 · CYAN projects, never derives
- **LAW:**
  - CYAN renders the actor-safe projection exactly as served.
  - It never inspects the raw intent to judge it, never computes or infers a capability, never enables Send without a served `CAN_SEND = true` at the current basis, and never hides a boundary the server reported.
  - A manipulated client can at most render; it cannot cause execution.
- **WHY:** The frontend is untrusted presentation (11 TB-02). 21 §38: "The frontend does not need internal authorization algorithms. It requires their projected result."
- **FALSIFIER:** A client-side governance computation exists; or a request forged by the client produces any execution, capability or state change.
- **AUTHORITATIVE ROOT:** 21 §37–§38; 11 TB-01/TB-02.
- **CONSUMERS:** R-12; B-10; P-11; F-BYPASS.

## I-16 · No provider before governance, and no provider in governance
- **LAW:**
  - The PCPG derivation calls no external provider.
  - No path from a raw intent reaches any provider except through a future SEND gate, which itself re-derives and then passes BND-009 and the AI Gateway.
  - The provider never decides whether its own invocation is legitimate.
  - Any model used inside PCPG is a model invocation under BND-009 (HA-PCPG-2).
- **WHY:** All LLM traffic goes through the Gateway (08 §3). PROVIDER ≠ GOVERNANCE_AUTHORITY.
- **FALSIFIER:**
  - A network egress to any model endpoint during an observation.
  - A code path from the observation ingress to a provider adapter.
  - Governance output that depends on a provider response.
- **AUTHORITATIVE ROOT:** 06 BND-009; 08 §3, §17; 11 TB-11/TB-12.
- **CONSUMERS:** R-10, R-11; B-08; P-12; F-BYPASS.

## I-17 · The full governance Field stays internal
- **LAW:**
  - The complete Observation Result, including authority facts, binding identities, internal reason chains and Pulse, stays inside NQUIRY.
  - A future provider projection may contain only the minimum necessary context of the MLT's admitted computation: no blocked delta, no forbidden instruction, no unnecessary authority data, no secret, no cross-Workspace context, no protected governance data, no ceiling or source-status escalation, no decision substitution.
  - The actor-safe projection shows the actor only facts the actor may already read.
- **WHY:** 11 AC-11-010; 08 §6 (context manifest); 11 §26 (SENSITIVE_OPERATIONAL, AUDIT_SENSITIVE).
- **FALSIFIER:**
  - Any blocked delta, its instruction text, or any authority or governance internal appears in a provider-projection eligibility set.
  - The actor-safe projection discloses a fact the actor cannot read through existing queries.
- **AUTHORITATIVE ROOT:** 11 AC-11-010, §26; 08 §6, §55.
- **CONSUMERS:** R-11, R-12; B-04, B-08; P-13; F-DISCLOSURE.

## I-18 · No side effect, no persistence by default
- **LAW:**
  - An observation writes nothing canonical: no Command, CommitUnit, audit row, outbox row, Event, AIGeneration or manifest.
  - By default it persists nothing, and it never logs the raw intent.
  - Any operational trace records identities and outcome only.
- **WHY:** This is the side-effect-free query discipline. F08: no free text in any Event. 11: minimal logging. GAP-11-007: retention is open.
- **FALSIFIER:** Any row count or log line in canonical, audit, outbox or event storage changes because of an observation. Or the raw intent appears in any log.
- **AUTHORITATIVE ROOT:** 09 (Query vs Command); F08 payload rule; 11 §26 logging; GAP-11-007.
- **CONSUMERS:** R-01, R-12; P-01, P-16; F-BYPASS.

## I-19 · Determinism of governance
- **LAW:**
  - Strata 3 and 4 are a pure function of the basis: canonical facts, Pulse, interpretation and rule-set version.
  - The same basis gives the same result.
  - Stratum 2 is reproducible for a given rule-set version and input (HA-PCPG-2 default).
- **WHY:** Reconstruction and inverse proof (20) require it; P-07 and P-08 depend on it.
- **FALSIFIER:** Two derivations with the same basis produce different strata-3 or strata-4 values.
- **AUTHORITATIVE ROOT:** 20 (reconstruction); this Field.
- **CONSUMERS:** R-06..R-10; P-07, P-08, P-17.

## I-20 · No parallel models
- **LAW:** The Field introduces no authority class, role, permission flag, state, lifecycle, policy, data class or operation contract. Every such concept it uses resolves to its existing home. A new concept may enter only through that home's own decision procedure.
- **WHY:** The additive law of this Field; 20 §14 (decision ledger).
- **FALSIFIER:** A PCPG vocabulary term used as authority, state, policy or data class that has no mapping to an existing home, or that has a second, divergent definition.
- **AUTHORITATIVE ROOT:** 20; 16 (register); 04, 03, 11, 08.
- **CONSUMERS:** all relations; P-14..P-16.
