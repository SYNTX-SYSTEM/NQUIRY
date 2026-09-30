# 26 · PRE_CALL_PROMPT_GOVERNANCE — 04 OBSERVATION RESULT

**This file is authoritative for:** the semantics of the Observation Result:
- strata;
- Pulse elements;
- execution classes;
- the delta record;
- result classes and their precedence;
- composition, FBR, MLT, NVT and HAR;
- the capability values;
- freshness;
- the actor-safe projection;
- the provider-projection constraints.

**It may not decide:** any authority, state, data class, contract or provider policy. It defines only how existing facts are **combined** into derived metadata. It fixes the semantics, not the wire format, field names or storage (BLUE derives those).

---

## 1. Shape (semantic, not a schema)

```
ObservationResult
  basis                        §9
  canonical facts              stratum 1 (quoted, sourced, versioned)
  pulse                        §3 (stratum 1 view)
  semantic observation         stratum 2 (R-05)
  deltas[]                     §4–§6 (stratum 2 identity + stratum 3 evaluation)
  composition                  §7.1 (stratum 3)
  chain                        §7.2–§7.5 FBR, MLT, NVT, HAR, PARTIAL (stratum 3)
  capability                   §8 (stratum 4)
  provider projection eligibility   §11 (stratum 3; internal only)
  actor-safe projection        §10 (stratum 4; the only thing CYAN receives)
```

## 2. Strata (I-02)

| Stratum | Kind | Source | May be wrong? | Consequence of uncertainty |
|---|---|---|---|---|
| 1 | CANONICAL FACT | existing producer, with reference and version | No. It is what the producer says at the basis. | Unreadable becomes UNRESOLVED |
| 2 | DERIVED SEMANTIC INTERPRETATION | SIMPLIX over the raw intent | Yes. NON_PROOF. | UNKNOWN |
| 3 | DETERMINISTIC GOVERNANCE EVALUATION | pure function of strata 1–2 and the rule set | No, given its inputs | inherits UNKNOWN and UNRESOLVED as INDETERMINATE |
| 4 | CAPABILITY PROJECTION | pure function of stratum 3 | No, given its inputs | false, with a reason |

## 3. Pulse: the minimum model derived from the repository

Pulse is the set of **currently active or unresolved canonical relations that constrain what may happen next** within the scope. Each element is a view of an existing record or producer result (I-07):

| Pulse element | Canonical source (existing) | Effect on evaluation |
|---|---|---|
| ACTIVE_TRANSITIONS | the relevant transitions and their availability in the existing capability projection (`session_position.actions`: `relevant`, `available`, `reasonCode`) | the state and authority results of deltas that map to them |
| PENDING_HUMAN_DECISIONS | open canonical decision points: a Decision UNDER_CONSIDERATION (04 AUTH-DEP-DEC-*); a selection pending in QUESTION_SELECTION; an incomplete ImpactChain (HD-26) | a delta that would substitute them is HUMAN_COMMAND (I-08) |
| PENDING_AUTHORITY_REQUIREMENTS | the reason codes of unavailable relevant actions (for example `NO_SESSION_CONTROL`, `NO_QUESTION_SELECTION_RIGHT`) | the source of HAR |
| IN_FLIGHT_OPERATIONS | non-terminal AI generations, and authorizations without an executed generation (06 BND-017; `reflection_proof._unresolved` semantics) | a dependent delta is INDETERMINATE |
| INDETERMINATE_CONSEQUENCES | INDETERMINATE commits and open recovery records (10; BND-017) | a dependent delta is INDETERMINATE |
| STALE_SOURCES | sources whose canonical producer reports a superseded or unverifiable version (for example frozen-set verification failure, F03; provenance not reconstructable, F04) | a dependent delta is INDETERMINATE or STATE_BOUNDARY, per the producer's reason |
| RECENT_AUTHORITY_CHANGE | bindings granted or revoked within the scope after a source they gate was produced (binding history, 05) | informational only; never changes a result by itself (re-derivation already reflects current authority) |
| UNRESOLVED_ELIGIBILITY | provider route or data-class eligibility that is not resolvable (HARD-DEP-002; GAP-08-008; GAP-11-006) | PROVIDER_EXECUTABLE is false, or DATA_BOUNDARY |
| GOVERNANCE_BLOCKERS | open Case 3 questions that govern a touched relation (HA queue; for example HA-23 for leaving INVESTIGATION) | GOVERNANCE_BOUNDARY, with HAR citing the question |
| EXTERNAL_DEPENDENCIES | external effects in progress or required (none exist in NQUIRY today) | informational; an EXTERNAL_EFFECT delta stays bounded by B-07 |

**Not in Pulse:** anything the prompt says, any status invented by PCPG, and any counter or timer of PCPG's own.

## 4. Execution classes (this Field; derived from 08 §39–§40, §21 and 04)

| Class | Meaning | May be in the MLT? | Evaluated against |
|---|---|---|---|
| PROVIDER_COMPUTATION | a computation a model could perform whose maximum canonical effect is **derived output only** (08 §39: analysis, comparison, recommendation, summarization, drafting of non-binding text) | Yes, if ALLOWED | the actor's authority to request it; state; admitted operation class (HD-21, HA-PCPG-1); data; ceiling |
| HUMAN_COMMAND | any effect that is a human decision, selection, approval, authorization, state transition or authority mutation (I-08) | **Never** | the actor's own authority and state, through the existing readiness producer, giving HUMAN_ACTION_AVAILABLE or a boundary |
| EXTERNAL_EFFECT | any effect outside NQUIRY (order, pay, send, publish, call an integration) (I-11) | **Never** | whether a governed product path exists, giving AUTHORITY_BOUNDARY or DENIED |
| DISCLOSURE | an effect of revealing data to a party (export, share, include in model context beyond need) | only as bounded inputs of a retained computation (§11) | data class, scope, export authority (BND-016) |
| UNKNOWN | no certain class | Never | INDETERMINATE |

The class is determined by the **effect**, not by the verb or the requested executor. "Let the AI pick" is still a selection, and therefore HUMAN_COMMAND. When the prompt requests that AI perform a HUMAN_COMMAND, the delta carries the flag `DECISION_SUBSTITUTION_REQUESTED`.

## 5. Delta record (every delta; all fields required, UNRESOLVED where unknown)

| Field | Stratum | Meaning |
|---|---|---|
| DELTA_ID | 3 | stable within the observation |
| SOURCE_CLAUSE | 2 | span in the raw intent, or IMPLIED with the canonical chain relation that implies it |
| SOURCE_RELATION | 1/2 | the canonical relation the delta would touch |
| TARGET | 1/2 | the in-scope object, or OUT_OF_SCOPE / UNKNOWN |
| OPERATION | 1 | the reference into the existing catalog (Command, transition, AUTH-DEP, AIOP), or UNKNOWN |
| EXECUTION_CLASS | 3 | §4 |
| REQUESTED_EXECUTOR | 2 | human, AI or unspecified, as the prompt asks |
| CURRENT_STATE / PROPOSED_STATE | 1 / 2 | canonical current; proposed as interpreted |
| REQUIRED_AUTHORITY | 1 | from the operation's authority home (AUTH-DEP), including scope |
| ACTUAL_AUTHORITY | 1 | the actor's effective authority for it (resolver or readiness producer), with binding reference, or NONE |
| AUTHORITY_SOURCE / AUTHORITY_SCOPE | 1 | BINDING, PARTICIPATION, ROLE or FOUNDING (typed sources, HD-6), with the exact scope |
| DECLARED_PURPOSE / SEMANTIC_PURPOSE / PURPOSE_ALIGNMENT | 2 / 2 / 3 | whether the semantic purpose matches the declared one and the operation's canonical purpose |
| SOURCE_AUTHORITY | 1 | the authority and mutability of the delta's inputs |
| DATA_CLASSIFICATION | 1/2 | canonical classes, or restrictive candidates (I-13) |
| EXTERNAL_EFFECT / REVERSIBILITY | 3 | whether it has an external effect; REVERSIBLE, IRREVERSIBLE or UNKNOWN |
| PROOF_CEILING | 3 | the most restrictive of the inputs, plus AI output class if PROVIDER_COMPUTATION |
| OUTPUT_CONTRACT | 1 | the admitted operation contract's output class, or NONE |
| BOUNDARY | 3 | which of B-01..B-10 decided the result |
| ELIGIBILITY | 3 | for PROVIDER_COMPUTATION: whether its inputs are eligible for any route (§11) |
| FLAGS | 3 | DECISION_SUBSTITUTION_REQUESTED, AUTHORITY_CLAIMED_IN_PROMPT, INSTRUMENTAL_TO_BLOCKED, OUT_OF_SCOPE_TARGET, NEGATED, HYPOTHETICAL |
| RESULT / REASON | 3 | §6; the reason is a canonical producer's reason code or an invariant ID |

## 6. Result classes and precedence

| Result | Meaning |
|---|---|
| ALLOWED | a PROVIDER_COMPUTATION that is legitimate under the current Field in every respect |
| HUMAN_ACTION_AVAILABLE | a HUMAN_COMMAND the actor may perform now through the product. Never sendable. |
| STATE_BOUNDARY | the operation is not legal in the current state (03) |
| AUTHORITY_BOUNDARY | the actor lacks the required authority, but a legitimate holder class exists |
| DATA_BOUNDARY | the inputs cannot lawfully cross (11) |
| GOVERNANCE_BOUNDARY | the operation class is not admitted (HD-21, HA-PCPG-1), no contract exists, or an open Case 3 governs it |
| DENIED | no actor may legitimately do this through this path: cross-Workspace; secret disclosure; mutation of an immutable source; ceiling escalation; an external effect with no product path |
| INDETERMINATE | UNKNOWN or UNRESOLVED input, or a dependency on an in-flight or indeterminate relation |

**Precedence** (when several findings apply, the RESULT is the first match; all findings stay listed):
1. DENIED
2. INDETERMINATE
3. STATE_BOUNDARY
4. AUTHORITY_BOUNDARY
5. DATA_BOUNDARY
6. GOVERNANCE_BOUNDARY
7. HUMAN_ACTION_AVAILABLE or ALLOWED

The order follows dependency. A state that does not allow the operation makes authority moot. Authority precedes data and admission, because who may request the computation is decided before what it may carry.

## 7. Chain results

### 7.1 Composition (R-08)
- The **candidate retained set** consists of the ALLOWED PROVIDER_COMPUTATION deltas whose dependencies are also retained.
- A delta flagged INSTRUMENTAL_TO_BLOCKED is removed unless the canonical authority model grants it separately (I-10). "Instrumental" means its output is consumed only by a blocked delta and it has no standalone purpose within the actor's authority.
- The **composed effect** is evaluated as one effect:
  - the union of input data classes, which must remain eligible;
  - no external or canonical effect beyond each contract's maximum;
  - the composed ceiling, which is the most restrictive;
  - purpose coherence.
- A composition that crosses a boundary removes the deltas responsible, with the reason `COMPOSITION_<BOUNDARY>`.

### 7.2 FIRST_BROKEN_RELATION
- **Order:** the deltas' dependency order, which follows the canonical chain (for example compare → recommend → select → approve → order; or analysis → reflection → selection → ImpactChain → investigation).
- **Definition:** FBR is the first delta in that order whose RESULT is neither ALLOWED nor HUMAN_ACTION_AVAILABLE.
- **Form:** `<last legitimate predecessor> → <broken delta>`. The broken delta carries its RESULT and the canonical reason.
- **Empty case:** none if all deltas are legitimate.
- **Undeterminable order:** FBR is INDETERMINATE.

### 7.3 MAXIMUM_LEGITIMATE_TRANSITION
- The MLT is the retained set after composition, in dependency order. It is empty when nothing is retained.
- It contains only PROVIDER_COMPUTATION deltas. HUMAN_COMMAND and EXTERNAL_EFFECT deltas never enter it, even when HUMAN_ACTION_AVAILABLE (I-08, I-11).

### 7.4 NEXT_VALID_TRANSITION
The earliest legitimate next step, in this order of preference:
1. the first HUMAN_ACTION_AVAILABLE delta at or before the FBR;
2. else the product transition, available to the actor now (existing projection), that the FBR depends on;
3. else none.

It is always a human product action, never a provider call.

### 7.5 HUMAN_AUTHORITY_REQUIRED
For each boundary delta:
- the required existing authority class and scope, and the holder class ("the SESSION_CONTROL_RIGHT holder of this Session", "the QUESTION_SELECTION_RIGHT holder who selected the current primary");
- or the open HA-* question that governs it.

It names no other person's binding internals to a non-holder (I-17).

### 7.6 PARTIAL
PARTIAL is true exactly when some requested delta is outside the MLT. The Field never rewrites the raw intent into a narrowed prompt (HA-PCPG-6).

## 8. Capability (stratum 4; I-14)

- **GOVERNANCE_ADMISSIBLE** is true exactly when all of these hold:
  - the MLT is non-empty;
  - the composition is COMPOSABLE;
  - no INDETERMINATE delta is a dependency of, or shares inputs with, a retained delta;
  - every retained delta maps to an **admitted operation class** whose invocation this path may request (HD-21 scope; HA-PCPG-1 for user-authored instructions);
  - the composed data classes are eligible for at least one route class under 11 §26 (ignoring whether a provider exists).
- **PROVIDER_EXECUTABLE** is true exactly when all of these hold:
  - an eligible, configured, legitimate provider route exists **now** for the retained computation's operation contract and composed data classes;
  - the environment is declared (AC-11-017);
  - the route is not a MockProvider route on a real scope (HD-19);
  - on PRODUCTION, the route is not the MockProvider (HD-LIVE-1).
- **CAN_SEND** = GOVERNANCE_ADMISSIBLE ∧ PROVIDER_EXECUTABLE.

Each value carries all failing reasons, never just "false".

| GOV_ADMISSIBLE | PROV_EXECUTABLE | CAN_SEND | Meaning shown to the actor |
|---|---|---|---|
| false | false | false | the legitimate portion is empty or not admitted, and no route exists |
| false | true | false | a route exists, but this proposal is not admissible |
| true | false | false | admissible, but no legitimate route exists now |
| true | true | true | a projection only: a future SEND gate re-derives everything |

**Current NQUIRY values (2026-09-29):** GOVERNANCE_ADMISSIBLE is false for every observation, with reason `OPERATION_CLASS_NOT_ADMITTED` (FBR-PCPG-4 / HA-PCPG-1). This holds even for a delta mapping to AIOP-001, because AIOP-001 is invoked only through the human BEGIN_ANALYSIS authorization path (HD-16), never through a prompt. PROVIDER_EXECUTABLE is false for every real scope (`NO_ELIGIBLE_PROVIDER_ROUTE`). CAN_SEND is false. This is correct, not a defect.

## 9. Freshness

- **Basis:** the set of everything that can change the result, and nothing else:
  - the actor identity (and a valid session at derivation);
  - the validated scope;
  - the raw-intent fingerprint (a one-way digest; the raw intent itself is not kept, I-18);
  - the declared purpose, if any;
  - the canonical facts consulted, as (reference, version) pairs;
  - the authority facts consulted, as binding references and versions **plus** the absence facts consulted ("no effective binding for class X at scope Y");
  - the Pulse elements consulted, by reference;
  - the rule-set version (this directory);
  - the data-policy version;
  - the provider-policy version and declared environment;
  - the derivation time.
- **Why no smaller key is correct:**
  - Each dimension can independently change a stratum-3 or stratum-4 value.
  - Absence facts carry no version, so no finite key over versions detects a new grant.
  - Therefore **no key proves currency**.
- **Rules:**
  1. **Derive on read.** Every projection request re-derives. No observation is served from a cache as current.
  2. **Never an input to a gate.** A future execution gate re-derives from the current Field (R-13). It may compare its fresh basis with a presented one only to tell the actor "this changed", never to skip evaluation.
  3. **Stale is a display state.** A client holding an older result must treat its CAN_SEND as absent (B-10).

## 10. Actor-safe projection (the only thing CYAN receives)

**Contains:**
- the actor's own raw intent (echoed);
- the semantic observation (spans, actions, targets, purposes, drift, unknowns);
- per delta: its operation label, execution class, RESULT, REASON code and HAR holder class;
- FBR, MLT, NVT and PARTIAL;
- the composed proof ceiling;
- GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND, with reasons;
- the basis identity (opaque) and the derivation time.

**Excludes:**
- binding identities and grantor details;
- other members' data beyond the actor's existing read scope;
- Pulse internals the actor cannot read through existing queries;
- the provider-eligible set;
- rule-set internals beyond reason codes.

## 11. Provider-safe projection constraints (eligibility only; the future Field builds it)

The eligible set (R-11) may contain only:
- the retained deltas' instruction semantics, expressed without any blocked delta, forbidden execution instruction, authority claim or governance internal;
- the minimum necessary input content;
- only data classes eligible under 11 §26;
- no secret, no DC-07 material, no cross-Workspace content;
- no internal authority data;
- no source-status or proof-ceiling claim above the canonical one;
- no decision-substituting instruction.

It is never the raw intent when PARTIAL is true.
