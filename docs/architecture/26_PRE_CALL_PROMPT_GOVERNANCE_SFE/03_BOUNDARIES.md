# 26 · PRE_CALL_PROMPT_GOVERNANCE — 03 BOUNDARIES

**This file is authoritative for:** what may and may not cross each boundary **of this Field**, who is authoritative, when the Field fails closed, and what falsifies the boundary.
**It may not decide:** a new boundary of the NQUIRY boundary architecture. Every PCPG boundary is a **projection** of an existing boundary or doctrine (06 BND-*, 08, 11, 21) onto the observation. Where the existing boundary says more, it wins. No PCPG boundary evaluates in place of the existing one at an execution gate: a PCPG boundary previews, the existing boundary decides.

| ID | Boundary | Existing home it projects |
|---|---|---|
| B-01 | Semantic | 08 §8.2, §9 (prompt is not authority; user content is DATA); 11 §78 (ambiguity is restrictive) |
| B-02 | Authority | 04 (all AUTH-DEPs, §17 default deny); 06 BND-001, BND-003, BND-004, BND-005 |
| B-03 | State | 03 (topology); 06 BND-007, BND-017 |
| B-04 | Data | 11 §25–§28 (DC classes, AC-11-010); 06 BND-002; 08 §6, §55 |
| B-05 | Source | 07 (evidence and source status); HD-24/26/27; F03 immutability |
| B-06 | Proof | 07; 06 BND-010; 08 §19, §39; HD-20, HD-24 |
| B-07 | External effect | 08 §21; 11 TB-14; 06 BND-009 (forbidden tool access), BND-016 (export) |
| B-08 | Provider | 06 BND-009; 08 §3, §17, §55; HARD-DEP-002; HD-19; HD-LIVE-1 |
| B-09 | Human authority | 04 (human decision rights), 08 §40 (adoption); 16 / HA queue (Case 3) |
| B-10 | Frontend | 21 §37–§38; 11 TB-01/TB-02 |

---

## B-01 · Semantic boundary
- **MAY CROSS:**
  - the raw intent, as DATA, into SIMPLIX;
  - interpretations (stratum 2) with source spans, into delta formation;
  - UNKNOWN markers.
- **MAY NOT CROSS:**
  - an interpretation as authority, state, scope, purpose or source status;
  - a guessed mapping in place of UNKNOWN;
  - an instruction in the raw intent that changes the rule set, the operation index or the evaluation ("ignore the rules", "treat me as controller");
  - negated, hypothetical or prohibited actions as requested actions.
- **WHO IS AUTHORITATIVE:** nobody decides authority here. SIMPLIX is authoritative only for "what the text says", and even that is NON_PROOF.
- **FAIL CLOSED:** an unparseable or ambiguous clause becomes UNKNOWN, and the delta becomes INDETERMINATE. A SIMPLIX failure makes the observation INDETERMINATE (R-05).
- **FALSIFIER:** a prompt-injection string alters any governance result; an ambiguous verb is mapped to a permitted operation; "do not order it" yields an ORDER delta as requested.

## B-02 · Authority boundary
- **MAY CROSS:**
  - canonical authority facts (effective binding per class and scope, with binding reference and version);
  - role, membership and participation, each quoted;
  - capability results of the existing readiness producers.
- **MAY NOT CROSS:**
  - authority claimed in the prompt;
  - role treated as authority (ROLE ≠ AUTHORITY; 05, 04 §54);
  - cached authority as current;
  - authority of another scope (04 exact-scope resolution);
  - the provider's opinion.
- **WHO IS AUTHORITATIVE:** 04, through `AuthorityResolver` and the readiness functions. BND-005 decides at the future execution gate.
- **FAIL CLOSED:** unresolved authority makes the delta INDETERMINATE, never ALLOWED. No authority gives AUTHORITY_BOUNDARY, with the holder class in HAR.
- **FALSIFIER:** a Facilitator role yields ALLOWED for a control-gated operation without a binding; a prompt stating "Maya approved this" changes any result; a revoked binding still yields ALLOWED on re-derivation.

## B-03 · State boundary
- **MAY CROSS:**
  - the current canonical state and version;
  - the relevant transitions with availability and reason, from the existing projection;
  - Pulse elements (unresolved and indeterminate operations, per BND-017).
- **MAY NOT CROSS:**
  - a proposed state as current;
  - a transition the topology does not have (03);
  - skipping a state;
  - any state change caused by the observation.
- **WHO IS AUTHORITATIVE:** 03 and the DB transition trigger; BND-007, BND-017.
- **FAIL CLOSED:**
  - A delta whose operation is not legal in the current state gives STATE_BOUNDARY, with the canonical reason (for example `SESSION_NOT_IN_QUESTION_SELECTION`).
  - An unresolved or in-flight operation on a dependency gives INDETERMINATE (BND-017: "uncertainty cannot create permission").
- **FALSIFIER:** "start the investigation" from QUESTION_CAPTURE is anything but STATE_BOUNDARY; an INDETERMINATE commit on the Session leaves a dependent delta ALLOWED.

## B-04 · Data boundary
- **MAY CROSS (internally):**
  - in-scope content references and their data classes (canonical where assigned; otherwise restrictive candidates);
  - into the eligible set (R-11): only the minimum necessary content of retained computations, and only data classes that some eligible route could lawfully receive (11 §26).
- **MAY NOT CROSS:**
  - cross-Workspace content (BND-002);
  - secrets (DC-06) into any provider-bound set;
  - AUDIT_SENSITIVE content (DC-07) into model context;
  - whole-Workspace or whole-Session disclosure where a bounded set suffices;
  - the raw intent into logs or Events;
  - other members' personal data beyond the actor's read scope into the actor-safe projection.
- **WHO IS AUTHORITATIVE:** 11 (classes and handling; GAP-11-006 governs assignment); 06 BND-002.
- **FAIL CLOSED:**
  - Ambiguous content takes the most restrictive class (11 §78).
  - A retained delta whose inputs cannot all be classified gives DATA_BOUNDARY.
  - Any cross-Workspace reference gives DENIED.
- **FALSIFIER:** "send everything in this workspace" produces a non-empty eligible set; a pasted API key or password appears in any output other than the actor's own raw intent; an ambiguous paragraph is classified PUBLIC.

## B-05 · Source boundary
- **MAY CROSS:** each source's identity, version, authority, mutability, evidence status and proof status, all quoted canonically.
- **MAY NOT CROSS:**
  - a mutation of any source;
  - a source status raised by a delta (for example "treat this summary as evidence");
  - an immutable source treated as editable (frozen Questions, F03; ImpactChain nodes, HD-26 S1; validated artifacts, F04);
  - a stale source as current.
- **WHO IS AUTHORITATIVE:** 07; the owning Field's immutability rules; F04 provenance.
- **FAIL CLOSED:**
  - A delta mutating an immutable source gives DENIED.
  - A delta relying on a source whose version is superseded or unresolvable gives INDETERMINATE, or STATE_BOUNDARY where the canonical producer reports staleness.
- **FALSIFIER:** "rewrite question 2 more clearly" yields anything but DENIED for the mutation (an AI reframing as a *new* derived Question is a different, contract-governed operation, 08 AIOP-003, outside HD-21); "mark the recommendation as evidence" is not DENIED.

## B-06 · Proof boundary
- **MAY CROSS:** proof classes and ceilings as canonically quoted (SYSTEM_PROOF, AI_VALIDATION_PROOF, DOMAIN_EVIDENCE, MOCK_NON_PROOF, FIXTURE_NON_PROOF, PROPOSAL / NON_PROOF), and the composed ceiling (the most restrictive).
- **MAY NOT CROSS:**
  - any ceiling escalation;
  - AI output as HUMAN_DECISION or DOMAIN_EVIDENCE;
  - AI_VALIDATION_PROOF as SYSTEM_PROOF or DOMAIN_EVIDENCE;
  - a Fixture scope presented as governed proof;
  - an observation presented as proof of anything.
- **WHO IS AUTHORITATIVE:** 07; BND-010; HD-20, HD-24, HD-27.
- **FAIL CLOSED:** an undeterminable ceiling is assumed to be the lowest, NON_PROOF.
- **FALSIFIER:** a Fixture Session observation shows GOVERNED proof; a retained RECOMMEND delta's output ceiling is anything above PROPOSAL / NON_PROOF.

## B-07 · External effect boundary
- **MAY CROSS:** the classification of a delta as EXTERNAL_EFFECT, and its reversibility, as observed facts.
- **MAY NOT CROSS:**
  - any external effect caused by the observation;
  - an EXTERNAL_EFFECT delta in the MLT or the eligible set;
  - an instruction to a provider to perform, prepare-for-submission or trigger an external effect;
  - tool capability.
- **WHO IS AUTHORITATIVE:** 08 §21 (a consequential tool must "re-enter the normal boundary path as a new requested operation"); 11 TB-14; BND-016 for export.
- **FAIL CLOSED:**
  - An EXTERNAL_EFFECT delta gives AUTHORITY_BOUNDARY when a human holder class exists, and DENIED when no legitimate path exists in the product.
  - An effect that cannot be determined gives INDETERMINATE.
- **FALSIFIER:** "automatically order it" appears in the MLT; "prepare the order so it can be submitted" is retained without a separate grant (I-10).

## B-08 · Provider boundary
- **MAY CROSS:**
  - provider route configuration and eligibility facts, as quoted;
  - the eligibility constraints of R-11, to a future Field only.
- **MAY NOT CROSS:**
  - any provider or model call during the observation;
  - the raw intent to any provider;
  - the full Observation Result to any provider;
  - a provider's response into governance;
  - MOCK output as real;
  - a non-PRODUCTION environment claim on PRODUCTION (HD-LIVE-1).
- **WHO IS AUTHORITATIVE:** BND-009 and the AI Gateway (08 §2–§3) at any future invocation; 08 §17/§55 and 11 for eligibility; HD-19; HD-LIVE-1.
- **FAIL CLOSED:**
  - No eligible route gives PROVIDER_EXECUTABLE = false (`NO_ELIGIBLE_PROVIDER_ROUTE`).
  - An unknown provider policy version gives false.
  - A MockProvider route is never PROVIDER_EXECUTABLE for a real scope, and exists only in DEVELOPMENT and TEST with a MOCK_NON_PROOF ceiling.
- **FALSIFIER:** network egress to a model endpoint during an observation; PROVIDER_EXECUTABLE = true on production today; a governance value that differs depending on provider availability other than PROVIDER_EXECUTABLE itself.

## B-09 · Human authority boundary
- **MAY CROSS:**
  - the identification of the required existing authority and holder class (HAR);
  - a reference to an open Human Authority question (HA-*) where the architecture leaves the answer to Human Authority;
  - NEXT_VALID_TRANSITION as a product action for a human.
- **MAY NOT CROSS:**
  - a human decision made, simulated, pre-filled or pre-approved by the Field;
  - a HUMAN_COMMAND delta executed through a provider;
  - an open Case 3 answered by derivation;
  - a narrowed prompt sent on the human's behalf (HA-PCPG-6).
- **WHO IS AUTHORITATIVE:** the human holder of the existing right, through the governed product Command. Human Authority for Case 3.
- **FAIL CLOSED:** a delta needing a human decision is HUMAN_COMMAND. The actor without the right gives AUTHORITY_BOUNDARY. The actor with the right gives HUMAN_ACTION_AVAILABLE, which is never in the MLT.
- **FALSIFIER:** a primary-Question selection by AI appears as retained computation; HAR names a specific person's binding internals to a non-holder.

## B-10 · Frontend boundary
- **MAY CROSS (server → CYAN):** the actor-safe projection (R-12) only, with its basis and derivation time.
- **MAY NOT CROSS:**
  - **client to server:** any client-computed capability, any client-supplied observation, result or basis treated as authority;
  - **server to client:** internal authority, binding or governance details beyond the actor's read scope; the provider-eligible set.
- **WHO IS AUTHORITATIVE:** the backend (R-10, R-12). CYAN has no authority.
- **FAIL CLOSED:**
  - No current result: CYAN shows "unavailable", and Send is not offered.
  - A served CAN_SEND older than the current basis is treated as absent. CYAN re-requests rather than infers.
- **FALSIFIER:** a client-side function derives send capability from the prompt; a forged request with `canSend: true` changes anything server-side.
