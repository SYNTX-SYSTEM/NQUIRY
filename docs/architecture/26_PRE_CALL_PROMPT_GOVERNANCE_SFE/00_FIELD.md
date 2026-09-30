# 26 · PRE_CALL_PROMPT_GOVERNANCE — 00 FIELD

**Ownership:** RED (architecture). **Status:** SFE architecture text; not implemented, not reviewed, not published.
**Execution law:** `20_SYSTEM_FIELD_ENGINEERING.md`; closure discipline of Architecture 25 §23.
**This file is authoritative for:** the Field's identity, scope, timeline, inputs, outputs, non-effects, producers and consumers, and its Human Authority boundaries.
**It may not decide:** authority, state, governance, data classes, AI operation contracts or provider policy. Those stay in their existing homes (§7).
Result semantics live in `04_OBSERVATION_RESULT.md`, laws in `01_INVARIANTS.md`, relations in `02_RELATIONS.md`, boundaries in `03_BOUNDARIES.md`, and closure in `05_PROOF_AND_CLOSURE.md`.

---

## 1. Field identity

| Item | Value |
|---|---|
| Field | PRE_CALL_PROMPT_GOVERNANCE (PCPG) |
| Field instance | one **Prompt Observation** = the derivation for one (actor, scope, raw intent) at one moment |
| Parent Field | NQUIRY_PRODUCT_FUNCTION_COMPLETION (Architecture 25). The observation layer sits above the AI Invocation Boundary (06 BND-009) and the AI Gateway Policy Engine (08 §2.3), whose outcome it previews. It does not replace either. |
| Colour | RED defines it; BLUE later materializes it; CYAN later projects it |
| Canonical location | `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/`. The next free architecture number after 25; one directory because the Field has several authority homes (see §13). |

## 2. Purpose

When a human drafts a prompt, NQUIRY observes the draft as a **proposed transition**. It then derives, without any side effect:

- how every part of that proposal relates to the **current authoritative Field** (state, authority, governance, sources, data handling, AI contracts, provider policy);
- the largest part that is legitimate now (**Maximum Legitimate Transition**);
- where the proposal first breaks (**First Broken Relation**);
- the next valid transition, and which human authority is required;
- the **current send capability**, expressed as three separate facts: GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND.

The Field produces **derived governance metadata only**. It creates no truth, no authority, no decision, no evidence and no transition.

## 3. Input

The Field receives two kinds of input.

**Runtime input (untrusted content, trusted identity):**
- the **raw user intent**: the drafted text, verbatim. It is DATA, never instruction or authority (08 §8.2, §9);
- the authenticated **actor** (BND-001; a verified local session, `security.identity.AuthenticatedPrincipal`);
- the **scope** the actor names: a Workspace, optionally a Session or another scoped object. The scope is a *claim*, validated by BND-002/BND-003 before any Field fact is read;
- optionally a **declared purpose**, supplied by the actor. It is a claim. It is compared with the semantic purpose and never trusted.

**Authoritative Field material (read-only, from the existing producers in §7):**
- the current canonical records within the validated scope;
- the capability results of the existing readiness functions;
- authority resolution, the operation catalog and its contracts;
- data classes and handling rules;
- the provider route configuration;
- the unresolved and indeterminate records that make up the **Pulse** (`04_OBSERVATION_RESULT.md` §3);
- the SFE's own **rule set**: this directory, with its version.

## 4. Output

One **Observation Result** (contract in `04_OBSERVATION_RESULT.md`):

- **Canonical facts quoted:** each with a source reference and version.
- **Pulse.**
- **Semantic observation:** clauses, actions, targets, modality, negation, conjunctions, declared and semantic purpose, drift, unknown relations.
- **Candidate deltas:** each with its execution class and full governance record.
- **Composed effect.**
- **The delta sets:** ALLOWED, HUMAN_ACTION_AVAILABLE, the four boundary sets, DENIED and INDETERMINATE.
- **Chain results:** FIRST_BROKEN_RELATION, MAXIMUM_LEGITIMATE_TRANSITION, NEXT_VALID_TRANSITION, HUMAN_AUTHORITY_REQUIRED.
- **Capability:** GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND, each with its reasons.
- **The eligibility** of a PROVIDER_SAFE_PROJECTION. Only its eligibility and constraints; see §10.
- **The basis:** freshness identity and rule-set version.

Plus an **actor-safe projection** of that result for CYAN (`03_BOUNDARIES.md` B-10).

## 5. Non-effects (what never happens in this Field)

- no provider or model call of any kind (see §12, HA-PCPG-2), and no external disclosure;
- no business execution, and no Command, CommitUnit, OperationAuthorization, AIGeneration or AIContextManifest;
- no canonical domain mutation, and no state transition;
- no authority, binding, membership, role, participation or decision created or changed;
- no Event carrying prompt text (F08 payload rule), and no prompt text in logs (11 §26 logging, AC-11-010);
- no prompt execution, and no tool invocation;
- no persistence of the raw intent or of the observation, by default (§9; HA-PCPG-3);
- no capability granted: CAN_SEND is a projection, never a token.

## 6. Producers and consumers

| Role | Who |
|---|---|
| Producer of the Observation Result | the backend PCPG derivation, inside the trusted boundary (TB-04 Application Service), with SIMPLIX as its semantic-observation step |
| Producers of every canonical fact | the existing NQUIRY producers of §7; PCPG only consumes them |
| Consumers now | CYAN, which projects only the actor-safe projection |
| Consumers later (future Fields; boundary defined only) | the future SEND execution gate, which **re-derives** and never trusts a stored observation; the future provider-safe projection builder, which works through the AI Gateway (08 §2) |

## 7. Authoritative predecessors (consumed, never re-produced)

| Concern | Authoritative home | Existing producer (code) |
|---|---|---|
| Identity | 18; 06 BND-001 | `security.local_auth`, `application.http_dispatch` session resolution |
| Workspace scope and membership | 02, 05; BND-002/BND-003 | membership repository; `deny_unless_member` (F09-2) |
| Role | 02 §7.4; BND-004 | membership and role records |
| Authority (HumanAuthorityBinding) | 04, 05; BND-005 | `authority.resolver.AuthorityResolver`; `human_authority_bindings` |
| Participation | 04 §4.6, AC-04-017 | `session_participations` |
| Session state and transitions | 03; BND-007 | `domain.session_transitions`; DB transition trigger |
| Session control, question selection, ImpactChain, investigation | 04 AUTH-DEP-SESS-*, AUTH-DEP-SEL-*; HD-25, HD-26 | the readiness and blocker functions (`reflection_readiness`, `question_selection_blocker`, `selection_blocker`, `impact_chain_blocker`, `investigation_readiness`, begin-analysis readiness) and their projection `inquiry_queries.session_position.actions` |
| Decision rights | 04 AUTH-DEP-DEC-*; HA-14 | the decision records and handler |
| Governance | 05 | governance records |
| Evidence and proof | 07; SYSTEM_PROOF, AI_VALIDATION_PROOF | proof and provenance records (`application.analysis_provenance`) |
| AI invocation | 06 BND-009; 08 §2, §3 | `ai_gateway` (gateway, context, prompt builder, validator) |
| AI output to canonical state | 06 BND-010; 08 §39, §40 | acceptance handlers |
| AI operation catalog and contracts | 08 §4–§5, §23–§38; HD-21 (accepted scope AIOP-001/002) | `ai_contracts.aiop`, `ai_contracts.f04_operations` |
| Invocation prompt | 08 §2.4, §8 (template + contract + bounded context) | `ai_gateway.prompt` |
| Context manifest | 08 §6 | `ai_context_manifests` |
| Provider boundary and eligibility | 08 §17, §18, §55; HARD-DEP-002; HD-19; HD-LIVE-1 | `application.analysis_runtime` (environment and provider configuration) |
| Unresolved and indeterminate consequences | 06 BND-017; 10 | unresolved-operation checks (`reflection_proof._unresolved`), recovery records, INDETERMINATE commits |
| Data classes and handling | 11 §25–§28 (DC-01..07, AC-11-009/010); GAP-11-006/007 | none materialized as a classifier; the classes are architectural |
| Fixture and NON_PROOF ceilings | HD-20, HD-24, HD-27; MOCK_NON_PROOF | `sessions.fixture`, `proof_mode()` |
| Capability projection doctrine | 21 §37–§38 ("An old capability projection is not proof of present authority") | `session_position.actions` |
| Security records | 11 §41–§47 | `security_events` |

## 8. Derived state

The Observation Result is **derived state**. It has four strata (laws in `01_INVARIANTS.md` I-02):

1. **CANONICAL FACT:** quoted from a predecessor, with source reference and version. Never re-derived.
2. **DERIVED SEMANTIC INTERPRETATION:** SIMPLIX's reading of the raw intent. Uncertain, NON_PROOF, fails closed.
3. **DETERMINISTIC GOVERNANCE EVALUATION:** a pure function of strata 1 and 2 and the rule set.
4. **CAPABILITY PROJECTION:** GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND, plus the actor-safe projection for CYAN.

## 9. Freshness (summary; full rule in `04_OBSERVATION_RESULT.md` §9)

- **Two rules decide freshness:**
  - Every observation carries its **basis**.
  - No observation, fresh or stale, is ever an input to an execution gate. Every consequential gate re-derives from the current Field.
- **Why the basis is not a gate:** absence facts ("no binding exists") carry no version. A basis key alone can therefore not prove freshness.
- **No caching:** observations are **derived on read** and never served from a cache as current. By default they are not persisted.

## 10. Timeline (validated against the repository)

```
RAW USER INTENT                    (client draft; not canonical; not sent anywhere)
→ OBSERVATION INGRESS              (authenticated, scope-validated, side-effect-free request; BND-001..003 first)
→ CURRENT FIELD RECONSTRUCTION     (read-only canonical snapshot within scope; versions recorded)
→ FIELD PULSE                      (view over existing unresolved/indeterminate/blocking records; no new state)
→ LOCAL SIMPLIX SEMANTIC SWEEP     (clauses, actions, targets, modality, negation, purpose, unknowns; inside the backend)
→ CANDIDATE DELTAS                 (each mapped to an existing operation or marked UNKNOWN; execution class assigned)
→ PER-DELTA GOVERNANCE EVALUATION  (existing readiness/authority/state/data/contract facts; one result per delta)
→ COMPOSED EFFECT                  (union of disclosure, effects, purposes of the retained deltas)
→ FIRST BROKEN RELATION
→ MAXIMUM LEGITIMATE TRANSITION  +  NEXT VALID TRANSITION  +  HUMAN AUTHORITY REQUIRED
→ CURRENT CAPABILITY               (GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE, CAN_SEND; with reasons and basis)
→ ACTOR-SAFE PROJECTION → CYAN     (projection only)
→ STOP
[future Fields, not here: SEND request → execution gate re-derives → BND-009 → AI Gateway → provider → BND-010]
```

Three corrections against the candidate timeline of the brief:

1. **The order of Pulse and reconstruction is logical, not temporal.** Both read the same snapshot and must share one basis (§9).
2. **Field reconstruction does not depend on the prompt.** It is the canonical snapshot of the validated scope. The prompt cannot widen it (I-05).
3. **The ingress is itself a relation.** Identity, Workspace and membership are proven **before** any Field fact is read (the F09-2 rule: no Session fact reaches a non-member).

## 11. Field boundary and out of scope

**Inside the boundary:**
- the observation ingress;
- reconstruction, Pulse, semantic sweep, delta evaluation, composition, the chain results and capability;
- the actor-safe projection;
- the **eligibility constraints** of a future provider-safe projection.

**Out of scope, defined only as boundary relations:**
- the SEND request and its execution gate;
- the construction and transmission of a provider-safe projection;
- any provider call or provider response, and post-provider governance (BND-010, acceptance);
- persistence and retention of observations;
- a CYAN visual design;
- a real non-NQUIRY domain (procurement) as a producer;
- any change to the existing authority, state, policy or data-class architecture.

## 12. First Broken Relation (repository, 2026-09-29)

**FBR-PCPG-1: RAW USER INTENT → GOVERNED PROMPT OBSERVATION.** No relation exists that takes a raw user intent into the backend as an authenticated, scope-validated, side-effect-free observation. Today user text enters only as DATA of fixed contracts: Burst capture, Challenge frame, ImpactChain answers.

Behind it, in dependency order:

- **FBR-PCPG-2: SEMANTIC DELTA → CANONICAL OPERATION.** There is no vocabulary relation mapping an observed action onto the existing operation catalog. That catalog is Commands (09), transitions (03), AUTH-DEPs (04) and AIOP contracts (08). The catalog exists, spread across these homes, with per-operation capability in `session_position.actions`. What is missing is its **consumable index**: per operation, its execution class, authority home, readiness producer, effect class and data inputs.
- **FBR-PCPG-3: PROMPT CONTENT → DATA CLASS.** No deterministic classifier exists for free text. GAP-11-006 is OPEN; the default is restrictive.
- **FBR-PCPG-4: RETAINED COMPUTATION → ADMITTED OPERATION CLASS.** A provider computation that a *user-authored* instruction would carry has no admitted operation class. Today prompts are System configuration (08 §2.4), and HD-21 admits only AIOP-001/002, each invoked only through its own human-authorized path. Consequence: in NQUIRY today **GOVERNANCE_ADMISSIBLE is false for every observation**, and HA-PCPG-1 governs the change.
- **FBR-PCPG-5: ADMITTED COMPUTATION → ELIGIBLE PROVIDER ROUTE.** HARD-DEP-002 and GAP-08-002/008 are open. HD-LIVE-1: production has no provider, and the MockProvider exists only in DEVELOPMENT and TEST (HD-19) with a MOCK_NON_PROOF ceiling. **PROVIDER_EXECUTABLE is false for every real route.**

Therefore CAN_SEND is currently false for every observation. That is correct, not a defect. The observation, with every other part of its result, is fully materializable now (FBR-PCPG-1..3).

## 13. Human Authority boundaries

These are proposed queue rows. They are **not** recorded in `field-reports/PFC/HUMAN_AUTHORITY_QUEUE.md` by this pass, because this pass writes nothing outside this directory. Each has a fail-closed default, so none blocks the SFE or the materialization of FBR-PCPG-1..3.

| ID | Question | Fail-closed default until decided | Existing home |
|---|---|---|---|
| HA-PCPG-1 | May a **user-authored instruction** ever become the instruction of a provider computation? If so, as which operation class, and with which contract and authority? This defines what SEND is. | GOVERNANCE_ADMISSIBLE = false with reason `OPERATION_CLASS_NOT_ADMITTED`. | 08 §2.4, §8, §9; HD-21; HA-07 / NQ-DEC-026 |
| HA-PCPG-2 | May SIMPLIX ever use a **model**, even a local one? Any model invocation is governed by BND-009 and 08, and would need an AIOP contract and a place in the HD-21 scope. | Only derivations that are reproducible from (rule-set version, inputs) are admitted. Uncertainty becomes UNKNOWN, never a guess. | 06 BND-009; 08 §3; HD-21 |
| HA-PCPG-3 | May raw intents or observations be **persisted**? For how long, and who may read them? | Ephemeral and derived on read. Visible only to the drafting actor. | 11 GAP-11-007, AC-11-010; F08 payload rule |
| HA-PCPG-4 | Who may **assign or override** the data class of prompt content? | Deterministic, rule-based candidates. Ambiguous content takes the most restrictive class (11 §78). No override. | 11 GAP-11-006 |
| HA-PCPG-5 | May a **non-NQUIRY domain**, such as procurement, supply authoritative facts to this Field, and through which producer? | Only as a **fixture producer**, marked FIXTURE_NON_PROOF. It is never a real domain. | 20; HD-24 ceiling semantics |
| HA-PCPG-6 | When the MLT is narrower than the raw intent, may a future SEND carry **only the MLT**? If so, with what human acknowledgement? | Not decidable here; the SEND Field is out of scope. The result exposes `PARTIAL = true` and never rewrites the intent. | future SEND Field |
