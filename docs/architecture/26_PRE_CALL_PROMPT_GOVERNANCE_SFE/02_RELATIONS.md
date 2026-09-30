# 26 · PRE_CALL_PROMPT_GOVERNANCE — 02 RELATIONS

**This file is authoritative for:** the relational graph of the PCPG Field: which relation produces what, for whom, under which precondition and boundary, how it fails, and how it is proven.
**It may not decide:** implementation structure (modules, classes, ports, functions), the semantics of existing producers, or result vocabulary. Result vocabulary lives in `04_OBSERVATION_RESULT.md`.

Relations are **system relations**. A BLUE agent may materialize several relations in one component, or one relation across several, as long as each relation's contract, boundary, failure state and proof hold.

```
R-01 ingress ─► R-02 scope ─► R-03 field ─┬─► R-04 pulse ─┐
                                           │               ├─► R-06 deltas ─► R-07 per-delta ─► R-08 composition ─► R-09 chain ─► R-10 capability ─► R-12 actor-safe projection ─► CYAN
R-01 raw intent ───────────────────────────┴─► R-05 semantic sweep ┘                                                              └─► R-11 provider-projection eligibility (constraints only)
R-13 future SEND gate: re-derives R-02..R-11 from the current Field (boundary relation; not materialized here)
R-14 reconstruction after material change: governs when any observation is stale (derive-on-read)
```

---

## R-01 · Observation ingress
- **PRODUCER:** the authenticated actor's client. **CONSUMER:** R-02.
- **AUTHORITATIVE HOME:** this Field (the ingress). Identity comes from 18 / BND-001.
- **INPUT:** raw intent (text), claimed scope (Workspace id, optionally a Session or object id), optional declared purpose, and the session credential (HttpOnly cookie).
- **OUTPUT:** an observation request bound to a verified principal. The raw intent is carried as opaque DATA.
- **PRECONDITION:**
  - The request is side-effect-free by contract: it is not a Command and carries no Idempotency semantics of a Command.
  - The raw intent is present and within a bounded size.
- **BOUNDARY:** B-02 (authority: identity first), B-10 (frontend: nothing from the client is trusted except the credential).
- **FAILURE STATE:**
  - No valid session: a uniform denial (401). Nothing is read.
  - Malformed or oversized input: rejected. Nothing is read.
  - Nothing is persisted or logged with content (I-18).
- **DOWNSTREAM:** R-02.
- **PROOF:**
  - An unauthenticated request, an expired session, oversized input or a non-text payload each yield the uniform refusal.
  - Storage and log row counts are unchanged, and the log carries no content (P-01, P-16).

## R-02 · Scope validation
- **PRODUCER:** the existing boundaries BND-001, BND-002 and BND-003, as already used by `deny_unless_member` (F09-2). **CONSUMER:** R-03, R-05.
- **AUTHORITATIVE HOME:** 06 BND-001..003; 13 P-22.
- **INPUT:** the verified principal and the claimed scope.
- **OUTPUT:** a **validated scope**: the Workspace the actor is a member of, and the named Session or object only if it belongs to that Workspace.
- **PRECONDITION:** R-01 succeeded.
- **BOUNDARY:** B-02, B-04.
- **FAILURE STATE:**
  - A non-member, a foreign Workspace, or an object of another Workspace: the uniform denial, before any fact is read (I-06).
  - An unknown object for a member: not found.
- **DOWNSTREAM:** R-03 (reads only within the validated scope), R-05 (targets outside it become boundary deltas).
- **PROOF:** the outsider, cross-URL and expiry cases of the F09-2 isolation sweep, applied to the ingress (P-01).

## R-03 · Current Field reconstruction
- **PRODUCER:** the existing canonical producers of `00_FIELD.md` §7, read-only. **CONSUMER:** R-04, R-06, R-07.
- **AUTHORITATIVE HOME:** each fact's own home (03, 04, 05, 07, 08, 11, HD-*).
- **INPUT:** the validated scope, the actor, and the current time.
- **OUTPUT:** the **Field snapshot**: canonical facts, each with its source reference and version. At minimum:
  - **Actor context:** actor; Workspace membership and role; participation; effective authority per class and scope, with the binding reference.
  - **Session context:** current Session state and version; the transitions currently relevant and their availability with reason codes, from the existing capability projection (`session_position.actions`).
  - **Sources:** each source with version, authority, mutability, evidence status and proof status (including Fixture and NON_PROOF).
  - **Data handling:** the data classes and handling rules of in-scope sources.
  - **AI contracts:** the admitted AI operation contracts (HD-21 scope).
  - **Provider:** provider route configuration and environment (HD-19, HD-LIVE-1).
  - **External effects and dependencies:** current external-effect state and dependencies.
- **PRECONDITION:** R-02 succeeded. Every fact is read at one consistent snapshot. Facts that could not be read are recorded as UNRESOLVED.
- **BOUNDARY:** B-03 (state), B-05 (source), B-04 (data: only in-scope facts).
- **FAILURE STATE:**
  - A canonical producer is unavailable, or a fact is unresolvable: that fact is UNRESOLVED, which propagates to INDETERMINATE (I-04).
  - Never defaulted, never cached as current (I-14).
- **DOWNSTREAM:** R-04, R-06, R-07; basis identity (R-14).
- **PROOF:**
  - Every quoted fact equals the canonical producer's value at the same basis (P-02, P-14..P-15).
  - The snapshot is identical for any two raw intents at the same basis (I-05).

## R-04 · Field Pulse
- **PRODUCER:** a derived view over existing records; element list in `04_OBSERVATION_RESULT.md` §3. **CONSUMER:** R-07, R-09.
- **AUTHORITATIVE HOME:** 06 BND-017; 10; 03; the existing readiness producers.
- **INPUT:** the Field snapshot.
- **OUTPUT:** Pulse elements, each citing its canonical source:
  - transitions currently open or blocked;
  - pending human decisions and pending authority requirements;
  - in-flight and unresolved operations;
  - indeterminate consequences;
  - stale sources;
  - recent authority change (a binding changed after a source it gates);
  - unresolved eligibility;
  - current governance blockers.
- **PRECONDITION:** R-03 produced the snapshot.
- **BOUNDARY:** B-03.
- **FAILURE STATE:** an element whose source is unresolvable is itself UNRESOLVED and propagates as I-04 requires.
- **DOWNSTREAM:** R-07 (a delta depending on an unresolved or indeterminate relation becomes INDETERMINATE); R-09 (Pulse blockers can be the First Broken Relation).
- **PROOF:** every element traces to a canonical record or producer result (P-15). No element exists that the producer would not report (I-07).

## R-05 · Local SIMPLIX semantic sweep
- **PRODUCER:** SIMPLIX, inside the trusted backend boundary. Mechanism is open (HA-PCPG-2); the default is reproducible, rule-based derivation. **CONSUMER:** R-06.
- **AUTHORITATIVE HOME:** this Field (stratum 2).
- **INPUT (the SIMPLIX run):**
  - the scope;
  - the authoritative Field files (this directory, versioned);
  - the Field snapshot and the Pulse;
  - the actor and the actor's authority facts, as context only, never as something to modify;
  - the data-handling rules;
  - the raw intent and the declared purpose.
- **OUTPUT:** the semantic observation:
  - clauses; actions, each with modality (asserted, requested, conditional, prohibited, hypothetical); negation; conjunctions and dependencies;
  - targets, resolved to in-scope objects or else UNKNOWN / OUT_OF_SCOPE;
  - relations touched; declared purpose; semantic purpose; purpose alignment; semantic drift;
  - candidate operations: pointers into the operation index, or UNKNOWN;
  - possible external effects; unknown relations;
  - data-class candidates of every referenced content, restrictive under ambiguity.

  Every item traces to its source span in the raw intent.
- **PRECONDITION:** R-02 succeeded. SIMPLIX makes no network egress to any model endpoint (I-16).
- **BOUNDARY:** B-01 (semantic), B-08 (provider: none), B-04 (data).
- **FAILURE STATE:**
  - An unparseable clause, an unsupported language, or an ambiguous action or target: the item is UNKNOWN (I-04).
  - A SIMPLIX failure leaves the whole observation INDETERMINATE with reason `SEMANTIC_OBSERVATION_UNAVAILABLE`. Never a partial guess.
- **DOWNSTREAM:** R-06.
- **PROOF:**
  - Every semantic item cites its span (P-02).
  - The same input and rule-set version give the same output (I-19).
  - Negated, hypothetical and prohibited actions never become requested actions (fixtures).
  - No egress (P-12).

## R-06 · Candidate delta formation
- **PRODUCER:** the governance evaluation (stratum 3), from R-05 and the operation index. **CONSUMER:** R-07.
- **AUTHORITATIVE HOME:**
  - the operation catalog in its existing homes: 03 transitions, 09 Commands, 04 AUTH-DEPs and 08 AIOP contracts;
  - the domain's canonical transition chain, for implied intermediate deltas;
  - this Field, for execution classes (`04_OBSERVATION_RESULT.md` §4).
- **INPUT:** the semantic observation and the Field snapshot.
- **OUTPUT:** the ordered **candidate deltas**. Each has:
  - an identity and a source clause (with span), or the marker IMPLIED together with the canonical chain relation that implies it;
  - its target and source relation;
  - its operation reference (an existing operation) or UNKNOWN;
  - its **execution class**: PROVIDER_COMPUTATION, HUMAN_COMMAND, EXTERNAL_EFFECT, DISCLOSURE or UNKNOWN;
  - its current and proposed state, and its dependency edges.
- **PRECONDITION:**
  - Every requested action yields a delta; none is dropped.
  - An intermediate delta is added only where the canonical chain requires it and the Field snapshot shows it is **not already satisfied**. Example: an order requires an approval in the domain's model. Never on a guess. For instance, on a Session already in ANALYSIS no BEGIN_ANALYSIS delta is implied.
- **BOUNDARY:** B-01, B-06 (human authority: decision-class effects are HUMAN_COMMAND, I-08), B-07 (external effect).
- **FAILURE STATE:** an action without a certain operation mapping becomes an UNKNOWN delta. An execution class that cannot be determined becomes UNKNOWN. Both are INDETERMINATE downstream.
- **DOWNSTREAM:** R-07.
- **PROOF:**
  - The delta set is complete: every requested action span maps to at least one delta (P-04).
  - Every IMPLIED delta cites its chain relation.
  - Selection, approval, decision and authority effects are never PROVIDER_COMPUTATION (P-05).

## R-07 · Per-delta governance evaluation
- **PRODUCER:** the governance evaluation (stratum 3), consulting only existing canonical producers. **CONSUMER:** R-08, R-09.
- **AUTHORITATIVE HOME:**
  - authority: 04, via `AuthorityResolver` and the readiness functions;
  - state: 03;
  - source and proof: 07, HD-20/24/26/27;
  - data: 11;
  - AI contracts: 08, HD-21;
  - external effects: 08 §21, 11 TB-14.
- **INPUT:** each delta, the Field snapshot and the Pulse.
- **OUTPUT:** one **delta record** per delta, with every field of `04_OBSERVATION_RESULT.md` §5, and exactly one RESULT class with its reason.
- **PRECONDITION:**
  - For NQUIRY operations, the required authority, the actual authority and the state availability are taken from the **existing** readiness producer for that operation. For operations with a projected capability, that is the `session_position.actions` entry at the same basis.
  - The evaluation never re-implements a readiness rule.
- **BOUNDARY:** B-02, B-03, B-04, B-05, B-06, B-07.
- **FAILURE STATE:** any required fact that is UNRESOLVED gives an INDETERMINATE delta. A delta with no authoritative producer for its authority gives INDETERMINATE with reason `NO_AUTHORITATIVE_PRODUCER`.
- **DOWNSTREAM:** R-08, R-09.
- **PROOF:**
  - For every NQUIRY operation, the delta's authority and state result equals the canonical capability result at the same basis (P-14).
  - Every result has a reason traceable to a canonical producer or to an invariant (P-05).

## R-08 · Composed effect
- **PRODUCER:** the governance evaluation (stratum 3). **CONSUMER:** R-09.
- **AUTHORITATIVE HOME:** this Field (I-10), constrained by 11 (data union), 08 §21/§39 (effects) and 07 (ceilings).
- **INPUT:** the delta records.
- **OUTPUT:**
  - the **retained set**: deltas that are ALLOWED as PROVIDER_COMPUTATION and whose dependencies are all retained;
  - its composed effect: the union of inputs and data classes; external effects (must be none); canonical effects (must stay within each contract's maximum); the composed proof ceiling (most restrictive); purpose coherence (each retained delta has a legitimate standalone purpose);
  - the instrumental-to-blocked analysis;
  - the composition result: COMPOSABLE, or the boundary class with a reason.
- **PRECONDITION:** R-07 is complete for every delta.
- **BOUNDARY:** B-04, B-05, B-07.
- **FAILURE STATE:**
  - A composition that crosses a boundary none of its parts crosses alone removes the offending deltas from the retained set, with the reason `COMPOSITION_<CLASS>`. Examples: a data union that exceeds a class; parts that together form an external effect.
  - An undeterminable composition makes the retained set empty for the affected branch (INDETERMINATE).
- **DOWNSTREAM:** R-09, R-11.
- **PROOF:** the splitting fixtures. A composed effect that any single part would be refused is refused (P-06).

## R-09 · Chain results: FBR, MLT, NVT, HAR
- **PRODUCER:** the governance evaluation (stratum 3). **CONSUMER:** R-10, R-11, R-12.
- **AUTHORITATIVE HOME:** this Field (`04_OBSERVATION_RESULT.md` §6–§7).
- **INPUT:** the delta records, their dependency order, the composition result and the Pulse.
- **OUTPUT:**
  - **FIRST_BROKEN_RELATION:** the first delta along the dependency order whose result is neither ALLOWED nor HUMAN_ACTION_AVAILABLE. It is expressed as "predecessor → broken delta", with the canonical relation that breaks and its producer's reason.
  - **MAXIMUM_LEGITIMATE_TRANSITION:** the retained, composable set, in order.
  - **NEXT_VALID_TRANSITION:** the first transition that a human, or the actor, can legitimately take next, through the product and never through a provider.
  - **HUMAN_AUTHORITY_REQUIRED:** for each boundary delta, which existing authority and holder class would be needed, or which open Human Authority question (HA-*) governs it.
  - **PARTIAL:** true when the MLT is strictly narrower than the requested deltas.
- **PRECONDITION:** R-08 is complete.
- **BOUNDARY:** B-06, B-09.
- **FAILURE STATE:** if the order is undeterminable (for example, cyclic or ambiguous dependencies), FBR is INDETERMINATE and the MLT is empty.
- **DOWNSTREAM:** R-10, R-11, R-12.
- **PROOF:** FBR and MLT are reconstructable from the delta records alone (P-07, P-08).

## R-10 · Current capability
- **PRODUCER:** the capability projection (stratum 4). **CONSUMER:** R-12; later R-13, which re-derives rather than consuming the value.
- **AUTHORITATIVE HOME:** `04_OBSERVATION_RESULT.md` §8; 21 §37–§38; 06 BND-009 (the criteria it previews); 08 §17, §55; HD-19; HD-LIVE-1; HD-21.
- **INPUT:** the MLT, the composition, the Pulse, the admitted operation classes and the provider route configuration.
- **OUTPUT:** GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND, each with its reasons, plus the basis identity.
- **PRECONDITION:** R-09 is complete.
- **BOUNDARY:** B-08, B-09, B-10.
- **FAILURE STATE:** any unresolved input makes the affected value false, with a reason. The Field has no "unknown = true" state.
- **DOWNSTREAM:** R-12. R-13 must **not** consume it as authority (I-14).
- **PROOF:** the truth tables of §8 in `04_OBSERVATION_RESULT.md`; the stale and bypass fixtures (P-09, P-10).

## R-11 · Provider-safe projection eligibility (constraints only)
- **PRODUCER:** the governance evaluation (stratum 3). **CONSUMER:** the future SEND Field only.
- **AUTHORITATIVE HOME:** 11 AC-11-010, §26; 08 §6 (context manifest), §55; this Field (I-17).
- **INPUT:** the MLT, its composed inputs and data classes.
- **OUTPUT:** the **eligible content set**: the minimum necessary inputs and the retained instruction semantics, with explicit exclusions. It is not a provider payload, it is not transmitted, and it produces no manifest.
- **PRECONDITION:** R-09 and R-10 are complete. It exists only if the MLT is non-empty.
- **BOUNDARY:** B-04, B-08.
- **FAILURE STATE:** any content that cannot be classified, or that is not provably necessary, is excluded. An empty MLT gives no eligible set.
- **DOWNSTREAM:** none in this Field.
- **PROOF:** no blocked delta, forbidden instruction, secret, cross-Workspace datum, DC-07 datum or governance internal is ever in the eligible set (P-13).

## R-12 · Actor-safe projection → CYAN
- **PRODUCER:** the backend (stratum 4). **CONSUMER:** CYAN.
- **AUTHORITATIVE HOME:** 21 §37–§38; 11 AC-11-010; this Field (`04_OBSERVATION_RESULT.md` §10).
- **INPUT:** the full Observation Result.
- **OUTPUT:** only what the actor may already read:
  - the actor's own raw intent;
  - the semantic observation;
  - the delta results with reason codes;
  - FBR, MLT, NVT and HAR (as holder classes, not other people's binding internals);
  - the capability values with reasons;
  - the proof ceiling;
  - the basis identity and its derivation time.
- **PRECONDITION:** R-10 is complete.
- **BOUNDARY:** B-10, B-04.
- **FAILURE STATE:** no projection without a complete result. On failure, CYAN receives an honest "unavailable" state with a reason, never a default capability.
- **DOWNSTREAM:** CYAN (display only).
- **PROOF:**
  - The projection contains no fact beyond the actor's existing read scope.
  - CYAN code contains no governance derivation.
  - A forged client request cannot cause execution (P-11).

## R-13 · Future SEND gate (boundary relation; not materialized)
- **PRODUCER:** the future SEND Field. **CONSUMER:** BND-009, then the AI Gateway (08 §2).
- **AUTHORITATIVE HOME:** a future Field, subject to HA-PCPG-1 and HA-PCPG-6; 06 BND-009, BND-014.
- **CONSTRAINT FIXED NOW:**
  - The gate **re-derives R-02..R-11 from the current Field** at execution time.
  - It accepts no observation, capability value or basis key from the client or from storage as authority.
  - It then passes BND-009, where the Gateway Policy Engine may be stricter, never weaker.
  - Only the eligible content (R-11) of the re-derived MLT may enter a Gateway request.
  - The raw intent itself never does, if it contains any non-retained delta.
- **PROOF (future):** a stored or forged CAN_SEND = true with a changed Field yields no invocation (P-10).

## R-14 · Reconstruction after material change
- **PRODUCER:** every consumer of an observation. **CONSUMER:** R-12 and the future R-13.
- **AUTHORITATIVE HOME:** `04_OBSERVATION_RESULT.md` §9.
- **RULE:**
  - An observation is valid only for its basis.
  - Any change of a versioned canonical fact in the basis, any authority change within the scope (including new or revoked bindings, which are absence-sensitive), any Pulse change, any rule-set, data-policy or provider-policy change, and any change of the raw intent makes it stale.
  - Because absence facts carry no version, a projection is **re-derived on every read**. The basis identity serves correlation and display, never as proof of currency.
- **PROOF:** the stale fixtures (P-09).
