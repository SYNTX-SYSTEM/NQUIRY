# SFE FRONTEND SYMBIOSIS ARCHITECTURE — v4 · PCPG-R12/1 RECONCILIATION
**Scope update:** `FULL OBJECT SYMBIOSIS` reconciled onto the materialized RED→CYAN contract `PCPG-R12/1`
**Mode:** `ARCHITECTURE_UPDATE` (architecture only)
**Lane:** `CYAN / FRONTEND PROJECTION`
**Target:** `CURRENT_NQUIRY_FRONTEND`
**Implementation:** forbidden by this document
**RED anchor:** `checkpoint-PFC-PCPG-18` (commit `41b4324`): Architecture 26 R-01 → … → R-10 → R-12 → B-10, serialized as `governanceObservation`
**Canonical correction (v4):** the backend emits **`PCPG-R12/1`**, the actor-safe R-12 projection. It does not emit semantic loci, display labels, gate states or attachment categories. CYAN maps already-crossed RED facts to presentation, and that mapping is never governance truth.

---

## 00 — RECONCILIATION RECORD (v3 → v4)

v3 had been written before a backend producer existed. It named backend fields that RED does not produce, or that B-10 forbids. v4 replaces every backend-contract statement of v3 with the materialized contract `PCPG-R12/1`. The CYAN symbiosis model (object membrane, action-adjacent friction, panel, deep inspection, attachment map) is kept, rebased onto that contract.

Governing laws for this reconciliation:

```text
PCPG-R12/1                      = the canonical RED → CYAN contract
PRESENTATION != AUTHORITY
PROJECTION != GOVERNANCE DERIVATION
ACTOR-SAFE PROJECTION != RAW BACKEND STATE
ABSENT != FALSE
UNKNOWN != DENIED
canSend != SEND gate
PCPG-R12/1 contains no SEND relation
ELIGIBLE CONTENT STATUS != ELIGIBLE CONTENT SET
PARTIAL I-12 != FULL PROVENANCE
PRESENTATION LOCATION != GOVERNANCE TRUTH
```

| v3 term | v4 disposition |
|---|---|
| `eligibleContent` (status axis) | **removed** (§13.5) |
| `providerEligibility` / `ProviderEligibilityProjection` | **removed** (B-10: the provider-eligible set may not cross) |
| `sendGate` / `SendGateState` | **removed from the backend contract**; future-only (§11) |
| `evidence` / `EvidenceProjection`, `evidenceRefs` | **removed**; future-only (§12) |
| `provenance` / `ProvenanceProjection`, `provenanceRefs` | **removed**; future-only (§12) |
| full `FreshnessProjection` | **removed**; only `basis` crosses (§13.2) |
| `actorProjection` | **removed** |
| `pulse` (`pulseId`, `stateRelation`) | **removed** (Pulse internals do not cross) |
| `field.snapshotId`, `field.reconstructionId`, `field.fieldId`, `field.purpose` | **removed** (no producer) |
| `projectionId`, `objectRef` (`decisionId`) | **removed** (no producer; observations are ephemeral) |
| `authorityBoundary` / `AuthorityProjection` (`membershipRef`, `authority.sourceRef`, `role`, `canAttempt`) | **removed** (binding identities and authority internals do not cross) |
| HAR holder classes | **removed**; future-only (not materialized) |
| `affectedSemanticLoci` as one backend-emitted field | **removed**; split (§06.3) |
| `displaySummary` / `GovernanceDisplaySummary` | **removed from the backend**; CYAN-local derived label (§06.1) |
| status axes `reconstruction`, `boundary`, `humanAuthority`, `chainState` | **removed from the backend**; CYAN-local aggregates over crossed facts (§06.2) |
| `GovernanceProjection` kinds `stale`, `rejected` | **removed**; kinds are `current` and `unavailable` only |
| `fbrCode`, `FbrProjection.authorityRef` | **removed** |
| `DeltaGovernanceStatus` (`retainedInComposedEffect`, `providerExecutableImpact`, …) | **removed**; replaced by RED `result` / `reasonCode` / `flags` |
| `GovernanceProjection` | **renamed** `GovernanceObservation` (wire field `governanceObservation`) |
| `candidateDeltas` | **renamed** `deltas` |
| `intendedTransition` | **renamed** `operation` |
| `sourceRelation` (v3 sense: text origin) | **renamed** `sourceClause` + `span`. The name `SOURCE_RELATION` is reserved for RED 04 §5 (future-only) |
| `freshness` | **renamed / narrowed** `basis` |
| `FbrProjection` | **renamed / narrowed** `chain.firstBrokenRelation {predecessor, broken}` |
| `governanceAdmissible`, `providerExecutable`, `canSend` | **narrowed** `TriState` → `boolean` + closed reason codes |
| proof ceiling | **labelled** "Session-level proof ceiling (partial I-12)" |

---

## 01 — EXECUTIVE ARCHITECTURE SUMMARY

The architecture remains full symbiosis: governance lives in the normal behaviour of the object, not in a badge plus a panel.

```text
Ambient layer + action-adjacent friction + inspection depth.
```

v3 corrected one coupling error: the backend must not decide UI topology (`surface = DECISION / BOUNDARY_BANNER / AI_RECOMMENDATION`). v4 corrects a second one: the backend must not emit a **second semantic vocabulary** either (`affectedSemanticLoci`, `displaySummary`, status axes, `sendGate`) when RED already produces the facts those terms re-encode (I-20: no parallel result vocabulary).

Corrected relation:

```text
RED (Architecture 26, R-12 via B-10)
→ PCPG-R12/1: semantic observation, deltas, chain, capability, basis, Session-level proof ceiling

CYAN
→ CYAN-local presentation categories derived deterministically from crossed facts
→ presentation attachment

CROSSED RED FACT
!= UI COMPONENT

PRESENTATION MAPPING
!= GOVERNANCE DERIVATION

PRESENTATION LOCATION
!= GOVERNANCE TRUTH
```

### Final symbiosis model

```text
SESSION / DECISION OBJECT
        │
        ├── NORMAL PRODUCT INTERACTION
        │
        ├── GOVERNANCE PERCEPTION LAYER
        │      ├── object membrane
        │      ├── fact-anchored presentation signals
        │      ├── action-adjacent friction
        │      └── fail-closed perception
        │
        ├── CONTEXTUAL GOVERNANCE INSPECTION
        │
        └── DEEP FIELD INSPECTION
```

### Current repo anchor

`SessionViewContainer` remains the right object-level host. It loads `SessionReadResult`, handles `loading/error/loaded`, then dispatches over `ok / denied / indeterminate / rejected`, and its own comment states that it never re-derives or overrides server verdicts (`apps/web/components/SessionViewContainer.tsx`).

The governance source is the materialized PCPG query:

```text
POST /workspaces/{workspaceId}/prompt-observations
body: { rawIntent, sessionId?, declaredPurpose? }
→ 200 { kind: "ok", field: "PRE_CALL_PROMPT_GOVERNANCE", workspace, session,
        rawIntent, rawIntentLength, rawIntentDigestSha256, declaredPurpose,
        observedAt, governanceObservation: GovernanceObservation }
```

It is a **query, not a command** (Architecture 26 I-18): side-effect-free, no Idempotency-Key, nothing persisted. Each observation is the governance derivation for **one submitted raw intent**, optionally scoped to one Session. There is **no standing per-object governance projection**. The object membrane therefore carries governance only for an observation that the actor has actually submitted for that object (§03, §14).

---

## 02 — CURRENT FRONTEND RECONSTRUCTION

### 02.1 Current object surface

The current NQUIRY frontend core is a Session/Decision surface, not a large admin shell. In the `ok` case, `SessionViewContainer` renders:

```text
WorkspaceBadge
ChallengeSummary
SessionStateBadge
BurstPanel
DecisionSection
```

and it renders its own state surfaces for `denied`, `indeterminate`, `rejected` and `error`.

This confirms:

```text
Governance belongs inside current Session/Decision object.
```

not:

```text
Governance belongs in a second application.
```

### 02.2 Current server-verdict discipline

The API types define closed vocabularies and typed shapes. `SessionReadResult` is a server-side verdict union type (`apps/web/lib/api/types.ts`).

Relevant for CYAN:

```text
client receives typed server projection
client renders
client does not invent authority
```

### 02.3 Current fail-closed parser discipline

The client sends `workspaceId` to the server only and decides nothing locally. There is no client-side allow path against denied or indeterminate server answers (`apps/web/lib/api/client.ts`).

```text
route params
!= authority

server result
→ projection

malformed / failed parsing
→ no silent allow
```

### 02.4 Existing component topology

```text
WorkspaceBadge
ChallengeSummary
SessionStateBadge
BurstPanel
DecisionSection
DeniedBanner
IndeterminateBanner
NetworkErrorBanner
```

These components are **CYAN presentation surfaces**. They never enter the backend contract.

```text
UI component names
→ CYAN attachment map only

crossed RED facts (PCPG-R12/1)
→ backend projection contract
```

### 02.5 Current PCPG consumer state

As of `checkpoint-PFC-PCPG-18`, no CYAN code consumes `POST /workspaces/{workspaceId}/prompt-observations` or `governanceObservation`. There is no typed client, no parser and no component. See FBR-CYAN-CONTRACT-01 (§23).

---

## 03 — SYMBIOSIS MODEL

The symbiosis keeps its five levels. v4 corrects the transport between RED and CYAN.

### Level -1 — Semantic Field Attachment

The invisible side is the PCPG-R12/1 observation for the current object:

```text
governanceObservation.kind          current | unavailable
contract                            "PCPG-R12/1"
basis                               rawIntentDigestSha256, derivationTime
semanticObservation                 clauses, actions, relationsTouched, purpose, drift
deltas                              per-delta RED result + Session-level proof ceiling
chain                               FBR, MLT, NVT, HAR, partial
capability                          governanceAdmissible, providerExecutable, canSend (+ reasons)
composedProofCeiling                Session-level proof ceiling (partial I-12)
```

It is bound to the object only through the request: `sessionId` is sent, and the response's `session` and `workspace` are echoed. Its validity is the observation itself, at `basis.derivationTime`.

Important:

```text
crossed RED facts
!= frontend component list
```

### Level 0 — Ambient Governance Perception

The object carries a subtle governance membrane. Every label is a **CYAN-local derived label** (§06.1), not backend truth:

```text
Field · No observation
Field · Observed            (current observation, no material boundary)
Field · Boundary reached
Field · Human Authority required
Field · Provider not executable
Field · Partial
Field · Governance unavailable
Field · Superseded          (CYAN-local: object changed after derivationTime)
```

This is perception, not authority.

### Level 0.5 — Action-Adjacent Friction

Governance becomes perceptible where action becomes relevant:

```text
human commands the actor asked for       (deltas, executionClass HUMAN_COMMAND)
provider computation the actor asked for (executionClass PROVIDER_COMPUTATION)
external effects / disclosure            (executionClass EXTERNAL_EFFECT / DISCLOSURE)
the first broken relation                (chain.firstBrokenRelation)
```

CYAN maps these crossed facts onto current UI surfaces (§06.3, §06.4).

### Level 1 — Contextual Governance Panel

The panel is deliberate inspection of the same object. Not a governance app; the same object, inspected more deeply.

### Level 2 — Deep Field Inspection

```text
FIELD (PRE_CALL_PROMPT_GOVERNANCE, contract PCPG-R12/1)
→ BASIS
→ SEMANTIC OBSERVATION
→ DELTAS
→ CHAIN (FBR / MLT / NVT / HAR / PARTIAL)
→ CAPABILITY (+ reasons)
→ SESSION-LEVEL PROOF CEILING (partial I-12)
→ NOT MATERIALIZED: SEND relation (R-13), evidence, provenance, HAR holder classes, SOURCE_RELATION
```

The deep view states what is not materialized explicitly. It does not hide it and does not fill it.

---

## 04 — PRIMARY USER FLOW

### 04.1 Normal flow

```text
User opens Session / Decision object
→ SessionViewContainer loads server result
→ normal NQUIRY object renders
→ membrane: "Field · No observation" (no PCPG observation exists for this object yet)
→ actor submits a raw intent for this Session (prompt-observation query)
→ governanceObservation (PCPG-R12/1) attaches to the object
→ membrane shows the CYAN-derived label
→ CYAN maps crossed facts to current UI presentation attachments
→ user continues normal interaction
→ user opens details only when needed
```

### 04.2 Boundary flow

```text
RED (PCPG-R12/1):
  chain.firstBrokenRelation = { predecessor, broken }
  broken.result = STATE_BOUNDARY, broken.reasonCode = <closed code>
  broken.executionClass = HUMAN_COMMAND, broken.operation = e.g. SELECT_PRIMARY_QUESTION
  chain.partial = true

CYAN (local presentation only):
  derives membrane label "Boundary reached" (an AUTHORITY_BOUNDARY / GOVERNANCE_BOUNDARY
  FBR, or a non-empty HAR, derives "Human Authority required" instead, §06.1)
  attaches the FBR to the question/boundary area by executionClass + operation
  opens panel directly to Boundary/FBR if inspected
```

No bypass. No retry-as-governance. No approval button unless the backend exposes an actual authority action through an existing product command.

### 04.3 Provider flow

```text
RED (PCPG-R12/1):
  a delta with executionClass = PROVIDER_COMPUTATION
  capability.providerExecutable = false
  capability.providerExecutableReasons includes NO_ELIGIBLE_PROVIDER_ROUTE
  capability.canSend = false

CYAN:
  attaches the delta to the AI/provider-related surface (CYAN-local)
  displays "Provider not executable" with the reason codes
  displays "Send not materialized" as a contract-level fact of PCPG-R12/1 (§11), never from a backend value
```

No SEND surrogate.

### 04.4 Rebuild-safe UI evolution

If the UI changes tomorrow:

```text
DecisionSection
→ DecisionPane
→ DecisionCard
→ inline Decision block
```

the backend contract remains unchanged:

```text
deltas[].operation = SELECT_PRIMARY_QUESTION
deltas[].executionClass = HUMAN_COMMAND
```

Only the CYAN attachment map changes.

---

## 05 — COMPONENT ARCHITECTURE

### 05.1 Existing components retained

```text
SessionViewContainer
WorkspaceBadge
ChallengeSummary
SessionStateBadge
BurstPanel
QuestionList
DecisionSection
DeniedBanner
IndeterminateBanner
NetworkErrorBanner
DecisionProvenanceView
```

### 05.2 Frontend architecture role names

`GovernanceNervousSystem` remains valid as a **frontend architecture metaphor / provider role**, not as backend domain vocabulary.

Allowed in frontend architecture:

```text
GovernanceNervousSystemProvider
GovernanceObjectMembrane
GovernanceAttachment
ActionAdjacentGovernance
BoundaryPerception
AuthorityPerception
ProviderReadinessPerception
ObservationTimePerception
```

Never in the backend contract:

```text
nervePoints
surface = DECISION
surface = BOUNDARY_BANNER
surface = AI_RECOMMENDATION
affectedSemanticLoci
displaySummary
sendGate
```

The backend contract is `PCPG-R12/1` (§13), and only that.

### 05.3 Corrected architecture

```text
SessionViewContainer
  ├── GovernanceObservationProvider
  │     consumes PCPG-R12/1 (typed client + fail-closed parser)
  │     owns no governance truth
  │
  ├── GovernanceObjectMembrane
  │     displays the CYAN-derived object-level label
  │
  ├── PresentationAttachmentMap
  │     maps crossed RED facts → CYAN presentation category → UI attachment
  │     does not decide whether anything is affected, admissible or allowed
  │
  ├── WorkspaceBadge
  ├── ChallengeSummary
  ├── SessionStateBadge
  ├── BurstPanel
  ├── DecisionSection
  ├── DeniedBanner / IndeterminateBanner
  │
  └── GovernancePanel / DeepFieldInspector
```

### 05.4 Ownership split

```text
RED Field (Architecture 26)
→ owns governance truth

PCPG-R12/1 (R-12 via B-10)
→ owns the actor-safe projection of that truth

RED deltas[].target / semanticObservation.relationsTouched
→ own the currently materialized object-relation hints

CYAN PresentationCategory (local)
→ owns a deterministic presentation grouping of crossed facts

CYAN PresentationAttachmentMap
→ owns where those categories appear in current UI

CYAN component state
→ owns openness / focus / expansion only
```

---

## 06 — PANEL INFORMATION ARCHITECTURE

Panel hierarchy:

```text
Governance Panel
  1. Derived label (CYAN-local)
  2. Capability (governanceAdmissible / providerExecutable / canSend + reasons)
  3. Observation basis (derivation time, raw-intent digest)
  4. Object coupling (workspace, session echo)
  5. Semantic observation (clauses, actions, purpose, drift)
  6. Presentation attachments (CYAN-local)
  7. Deltas
  8. Boundary / FBR
  9. Human Authority required (deltaId, result, reasonCode)
  10. Provider governance (providerExecutable + reasons; Send not materialized)
  11. Session-level proof ceiling (partial I-12)
  12. Not materialized (SEND relation, evidence, provenance, HAR holder classes, SOURCE_RELATION)
  13. Deep Field
```

### 06.1 Derived label (CYAN-local; replaces backend `displaySummary`)

The backend emits no display summary. CYAN derives exactly one membrane label, deterministically and in this precedence order, from crossed facts only:

```text
no observation submitted                                  → "No observation"
governanceObservation.kind = "unavailable"                → "Governance unavailable"
response unparseable / unknown contract / unknown value   → "Governance unavailable" (fail closed)
object changed after basis.derivationTime (CYAN-local)    → "Superseded"
chain.firstBrokenRelation.broken.result = AUTHORITY_BOUNDARY
  or chain.humanAuthorityRequired non-empty               → "Human Authority required"
chain.firstBrokenRelation != null                         → "Boundary reached"
chain.partial = true                                      → "Partial"
capability.providerExecutable = false and some delta has
  executionClass PROVIDER_COMPUTATION                     → "Provider not executable"
otherwise                                                 → "Observed"
```

This label is **not canonical truth**. It never changes an affordance. "Observed" never means "allowed".

### 06.2 Capability and chain (real RED values; replaces the v3 status vector)

The backend axes are exactly the RED R-10 capability and the R-09 chain:

```ts
interface Capability {                         // RED R-10
  readonly governanceAdmissible: boolean;
  readonly governanceAdmissibleReasons: readonly string[];   // sorted closed codes, e.g. MLT_EMPTY
  readonly providerExecutable: boolean;
  readonly providerExecutableReasons: readonly string[];     // e.g. NO_ELIGIBLE_PROVIDER_ROUTE, NO_ENVIRONMENT_DECLARED
  readonly canSend: boolean;                                 // projection only; never a gate, never a token
}
```

There is no backend `TriState`. R-10 has no UNKNOWN value. "Unknown" is expressed only by `governanceObservation.kind = "unavailable"`, or by the absence of an observation.

CYAN-local aggregates. They may be shown as a status vector, but each is a deterministic function of crossed facts, and none is ever sent back as input:

```text
boundary (CYAN)        = chain.firstBrokenRelation != null ? PRESENT : NONE
humanAuthority (CYAN)  = chain.humanAuthorityRequired.length > 0 ? REQUIRED : NOT_REQUIRED
chainState (CYAN)      = firstBrokenRelation != null ? BLOCKED : partial ? PARTIAL : COMPLETE
observation (CYAN)     = none | current | unavailable | superseded
```

Removed from the backend: `reconstruction`, `eligibleContent`, `sendGate`, `boundary`, `humanAuthority`, `chainState`, every `TriState`.

### 06.3 Semantic placement (replaces the backend `affectedSemanticLoci`)

The v3 `affectedSemanticLoci` mixed two different things. v4 splits them.

**(a) Object-relation hints: RED, materialized, already crossed.**

```text
deltas[].target                         canonical in-scope ref | "OUT_OF_SCOPE" | null (unresolved)
semanticObservation.actions[].target    same vocabulary
semanticObservation.relationsTouched    operation-index ids (sorted)
deltas[].operation                      operation-index id | null (UNKNOWN)
```

These are the **only** currently materialized object-relation hints. Runtime disclosure at `checkpoint-PFC-PCPG-18`: the R-03 → R-05 in-scope reference map is not yet supplied by the runtime composition, so every `target` is currently `null` (UNKNOWN), never a guess and never `OUT_OF_SCOPE`. Today `operation` and `relationsTouched` carry the usable hints.

**(b) `SOURCE_RELATION`: RED-defined (Architecture 26, 04 §5), not materialized. Future-only.** CYAN must not approximate it.

**(c) Presentation categories: CYAN-local.** Deterministic grouping of crossed facts for placement:

```ts
type PresentationCategory =                   // CYAN-local; never on the wire
  | "SESSION_STATE"                           // operation ∈ session-state transitions (BEGIN_SETUP … BEGIN_INVESTIGATION)
  | "BURST"                                   // PREPARE_BURST, COMPLETE_BURST, OPEN_QUESTION_GENERATION
  | "QUESTION"                                // CAPTURE_QUESTION, SELECT_PRIMARY_QUESTION, SELECT_COMPELLING_QUESTION
  | "DECISION"                                // OPEN_DECISION_CONSIDERATION, RECORD_HUMAN_DECISION
  | "AUTHORITY"                               // result AUTHORITY_BOUNDARY | HUMAN_ACTION_AVAILABLE; GRANT_/REVOKE_ operations
  | "PROVIDER"                                // executionClass PROVIDER_COMPUTATION
  | "EXTERNAL_OR_DISCLOSURE"                  // executionClass EXTERNAL_EFFECT | DISCLOSURE
  | "UNPLACED";                               // operation null / not in the CYAN map → panel only
```

A delta may fall into several categories (e.g. QUESTION and AUTHORITY); placement then repeats, it never selects. The operation list is CYAN's copy of RED operation-index ids, used only for placement. An id CYAN does not know maps to `UNPLACED`; it is never guessed into an area.

Law:

```text
CYAN may say:   this crossed delta is shown in the Decision area.
CYAN may not:   this delta affects the decision / authority / provider path.
PRESENTATION LOCATION != GOVERNANCE TRUTH
```

### 06.4 Presentation Attachments

CYAN-local mapping:

```ts
type PresentationAttachment =
  | "OBJECT_MEMBRANE"
  | "SESSION_STATE_AREA"
  | "BURST_AREA"
  | "QUESTION_AREA"
  | "DECISION_AREA"
  | "BOUNDARY_AREA"
  | "PROVIDER_RELATED_AREA"
  | "FIELD_PANEL"
  | "DEEP_FIELD_INSPECTOR";

const presentationAttachmentMap = {
  SESSION_STATE: ["SESSION_STATE_AREA"],
  BURST: ["BURST_AREA"],
  QUESTION: ["QUESTION_AREA"],
  DECISION: ["DECISION_AREA"],
  AUTHORITY: ["BOUNDARY_AREA", "DECISION_AREA"],
  PROVIDER: ["PROVIDER_RELATED_AREA"],
  EXTERNAL_OR_DISCLOSURE: ["BOUNDARY_AREA"],
  UNPLACED: ["FIELD_PANEL"],
} as const;
```

This map is **presentation logic**, not governance derivation. The membrane, panel and deep inspector always show the whole observation, whatever the placement.

### 06.5 Corrected law

```text
RED says (PCPG-R12/1):
  delta Δ2: operation = SELECT_PRIMARY_QUESTION, executionClass = HUMAN_COMMAND,
            result = STATE_BOUNDARY, reasonCode = <closed code>

CYAN says:
  Δ2 is placed in the Question area (CYAN-local category QUESTION)

CYAN does not say:
  this delta affects authority
  this delta is allowed / blocked for a reason RED did not give
```

---

## 07 — AMBIENT GOVERNANCE ARCHITECTURE

The ambient layer uses crossed RED facts plus CYAN-local placement. It never uses backend UI surfaces or backend loci.

### 07.1 Object membrane

Always object-bound, with the label derived per §06.1:

```text
Field · No observation
Field · Observed
Field · Boundary reached
Field · Governance unavailable
Field · Superseded
```

### 07.2 Fact-anchored perception

```text
RED:   a delta with executionClass = PROVIDER_COMPUTATION, capability.providerExecutable = false
CYAN:  PROVIDER category → provider-related current surface
```

### 07.3 Action-adjacent perception

```text
RED:   chain.firstBrokenRelation.broken = { operation: BEGIN_ANALYSIS, executionClass: HUMAN_COMMAND,
                                            result: AUTHORITY_BOUNDARY, reasonCode: <closed code> }
CYAN:  SESSION_STATE + AUTHORITY categories → session state area, decision-adjacent boundary area
```

### 07.4 Adaptive prominence

Prominence is derived from the CYAN-local label and aggregates (§06.1, §06.2), never from a new backend value:

```text
Observed, no FBR, no HAR                  → quiet
No observation                            → quiet, neutral (never "current", never "allowed")
Governance unavailable                    → visible
Superseded                                → visible + "observed at <derivationTime>" note
FBR present                               → prominent
HAR non-empty                             → prominent
PROVIDER category present                 → explicit "Provider not executable" + "Send not materialized"
                                            near the provider-related locus
```

---

## 08 — DELTA PROJECTION ARCHITECTURE

### 08.1 Backend delta projection (RED R-07 `DeltaRecord`, field-for-field)

```ts
interface DeltaWire {
  readonly deltaId: string;
  readonly operation: string | null;                 // operation-index id; null = UNKNOWN
  readonly executionClass:
    | "PROVIDER_COMPUTATION" | "HUMAN_COMMAND" | "EXTERNAL_EFFECT" | "DISCLOSURE" | "UNKNOWN";
  readonly target: string | null;                    // canonical ref | "OUT_OF_SCOPE" | null (unresolved)
  readonly sourceClause: string;                     // the actor's own clause text
  readonly span: readonly [number, number];          // offsets into rawIntent
  readonly currentState: string | null;              // null = not applicable / unresolved
  readonly result:
    | "ALLOWED" | "HUMAN_ACTION_AVAILABLE" | "STATE_BOUNDARY" | "AUTHORITY_BOUNDARY"
    | "DATA_BOUNDARY" | "GOVERNANCE_BOUNDARY" | "DENIED" | "INDETERMINATE";
  readonly reasonCode: string | null;
  readonly flags: readonly string[];                 // sorted closed codes
  readonly sessionProofCeiling: "GOVERNED" | "FIXTURE_NON_PROOF" | null;   // Session-level proof ceiling (partial I-12)
}
```

Removed against v3: `sourceRelation` (v3 sense), `intendedTransition`, `affectedSemanticLoci`, `status: DeltaGovernanceStatus`, `evidenceRefs`, `provenanceRefs`.

Runtime disclosure at `checkpoint-PFC-PCPG-18`:
- `flags` is currently always empty, because the per-delta flag correlation is not supplied by the runtime composition.
- Every `PROVIDER_COMPUTATION` delta currently resolves `INDETERMINATE` / `DATA_GOVERNANCE_NOT_MATERIALIZED`.

CYAN renders these values as given. `INDETERMINATE` is never rendered as `DENIED`.

### 08.2 Delta status (CYAN-local reading)

There is no backend delta status vector. CYAN reads the single RED `result`, plus `reasonCode` and `flags`. Membership of a delta in `chain.maximumLegitimateTransition` may be shown as "retained". That is a CYAN-local derivation over crossed facts, never a backend field.

### 08.3 CYAN delta attachment

```text
operation / executionClass / result
→ CYAN PresentationCategory
→ presentationAttachmentMap
→ current UI attachment
```

Not:

```text
delta text
→ frontend guesses component
```

### 08.4 User-visible delta example

```text
Delta Δ1
  "Analyse the questions"          (sourceClause, span 0–21)

Operation: REQUEST_QUESTION_ANALYSIS · PROVIDER_COMPUTATION
Result: INDETERMINATE · DATA_GOVERNANCE_NOT_MATERIALIZED
Session-level proof ceiling (partial I-12): GOVERNED

Current UI attachment (CYAN-local): Provider-related area

Provider executable: false (NO_ELIGIBLE_PROVIDER_ROUTE)
Send: not materialized (PCPG-R12/1 contains no SEND relation)
```

---

## 09 — BOUNDARY + FBR ARCHITECTURE

### 09.1 Backend projection (RED R-09)

```ts
interface ChainWire {
  readonly firstBrokenRelation: {
    readonly predecessor: DeltaWire | null;
    readonly broken: DeltaWire;
  } | null;                                        // null = no broken delta
  readonly maximumLegitimateTransition: readonly DeltaWire[];   // in order; currently always empty
  readonly nextValidTransition: DeltaWire | null;
  readonly humanAuthorityRequired: readonly {
    readonly deltaId: string;
    readonly result: string;
    readonly reasonCode: string | null;
  }[];
  readonly partial: boolean;
}
```

Removed against v3: `fbrCode`, `relation` (string), `affectedSemanticLoci`, `authorityRef`. The FBR reason is the `broken` delta's own `reasonCode`.

### 09.2 CYAN attachment

```text
broken.operation / executionClass / result
→ CYAN categories (e.g. SESSION_STATE + AUTHORITY)
→ Session state area + Boundary area
```

### 09.3 Boundary card

```text
BOUNDARY REACHED

What stopped?
  <broken.operation> · <broken.executionClass>       ("Unknown operation" if null)

Requested in:
  "<broken.sourceClause>"

Why?
  <broken.result> · <broken.reasonCode>

After:
  <predecessor.operation> or "first in chain"

Human Authority required for:
  <humanAuthorityRequired[].deltaId → result · reasonCode>

Current presentation (CYAN-local):
  Boundary area · Session state area
```

The card shows no holder class (not materialized), no binding and no grantor.

### 09.4 No UI-topology leakage

The backend does not mention:

```text
DeniedBanner
DecisionSection
BoundaryBanner
```

Those are CYAN-local.

---

## 10 — AUTHORITY PROJECTION

Authority remains separate from actor, role and capability. **PCPG-R12/1 carries no authority structure.**

### 10.1 What crosses

```text
deltas[].result ∈ { HUMAN_ACTION_AVAILABLE, AUTHORITY_BOUNDARY }   + reasonCode
chain.humanAuthorityRequired[] = { deltaId, result, reasonCode }
chain.nextValidTransition       (a human action the actor may take themselves)
```

### 10.2 What never crosses (B-10 / Architecture 26 04 §10)

```text
authority binding ids / binding versions (AuthorityFact)
grantor details
other members' data beyond the actor's existing read scope
membershipRef, authority.sourceRef
HAR holder classes — not materialized (future-only); never inferred by CYAN
```

The actor's own identity, role and existing product capabilities come from the **existing** producers (`/auth/me`, `session_position.actions`), not from this contract. The v3 `AuthorityProjection` and `actorProjection` are removed.

### 10.3 CYAN attachment

```text
result AUTHORITY_BOUNDARY / HUMAN_ACTION_AVAILABLE, GRANT_/REVOKE_ operations
→ CYAN category AUTHORITY
→ boundary area + action-adjacent decision area
```

### 10.4 Preserved laws

```text
ROLE != AUTHORITY
CAPABILITY != AUTHORITY
USER REQUEST != AUTHORIZATION
BUTTON != PERMISSION
APPROVAL != EXECUTION
HUMAN_ACTION_AVAILABLE != A BUTTON IN THE GOVERNANCE PANEL
```

`HUMAN_ACTION_AVAILABLE` may point to the existing product action (e.g. "Begin analysis" in the session controls). The governance panel never renders its own command control.

---

## 11 — PROVIDER-GOVERNANCE PROJECTION AND SEND

### 11.1 Backend semantic contract

```text
deltas[].executionClass = PROVIDER_COMPUTATION
capability.providerExecutable (+ providerExecutableReasons)
capability.governanceAdmissible (+ governanceAdmissibleReasons)
capability.canSend
```

### 11.2 Removed

```text
eligibleContent        — removed (§13.5)
providerEligibility    — removed (B-10: the provider-eligible set never crosses)
sendGate               — removed from the backend contract (§11.4)
```

### 11.3 CYAN presentation

```text
PROVIDER category
→ provider-related area

If the current UI has no dedicated provider-related area:
→ object membrane + panel only
```

CYAN must not invent a provider-readiness surface where no native surface exists.

### 11.4 R-13 discipline

R-13 (Future Send Effect Gate) is **NOT STARTED**. Therefore:

```text
canSend != SEND gate
PCPG-R12/1 contains no SEND relation
R-13 NOT MATERIALIZED != SEND GATE FALSE
ABSENT != FALSE
```

- `capability.canSend` is the R-10 capability projection. It is `false` with reasons, and it is never a gate, token or affordance.
- No backend field carries SEND state. CYAN renders "Send not materialized" because the **contract identity** is `PCPG-R12/1`, a contract that by definition has no SEND relation. It never reads that text from a backend value and never infers it from `canSend = false`.

Render:

```text
Send not materialized
```

not:

```text
Send disabled
Send unavailable
Send allowed
Ready to send
```

`disabled` implies an existing gate; `not materialized` means the gate does not exist. A future contract version that includes R-13 will carry its own produced field; until then CYAN renders no send-like control.

---

## 12 — EVIDENCE + PROVENANCE AND PROOF CEILING

### 12.1 Proof ceiling: Session-level proof ceiling (partial I-12)

```text
deltas[].sessionProofCeiling   GOVERNED | FIXTURE_NON_PROOF | null
composedProofCeiling           GOVERNED | FIXTURE_NON_PROOF | null
```

- **Label everywhere:** "Session-level proof ceiling (partial I-12)".
- **Never:** "proof", "proven", "provenance", "evidence".
- **`null` means unknown** (no Session scope, or nothing retained). It never means GOVERNED.
- **Current runtime value:** `composedProofCeiling` is always `null`, because `chain.maximumLegitimateTransition` is always empty.
- **Not materialized:** per-input source authority, mutability, evidence status, per-input proof class and provider-output class (full I-12).
- **Fixture:** a `FIXTURE_NON_PROOF` ceiling is rendered as Fixture / non-proof and is never presented as governed proof.

### 12.2 Evidence: not materialized (future-only)

No PCPG producer emits evidence. `evidence`, `EvidenceProjection` and `evidenceRefs` are removed. CYAN renders "Evidence: not materialized" in the deep view only.

### 12.3 Provenance: partial; not projected as provenance (future-only)

Crossed today: `basis.rawIntentDigestSha256`, `basis.derivationTime`, `semanticObservation.ruleSetVersion` and the per-delta `span`. The structured basis of canonical fact, authority and Pulse versions is not materialized. `provenance`, `ProvenanceProjection` and `provenanceRefs` are removed.

```text
PARTIAL I-12 != FULL PROVENANCE
```

### 12.4 Opaque refs stay opaque

The existing API types treat `decidedByUserId` and `decisionAuthorityBindingId` as opaque display refs; the frontend never decodes them. Governance follows the same law:

```text
opaque ref remains opaque
missing ref remains missing
frontend does not invent semantic name
```

---

## 13 — BACKEND → FRONTEND DATA CONTRACT: `PCPG-R12/1`

### 13.1 Contract principle

```text
Canonical RED → CYAN contract:
  PCPG-R12/1 = governanceObservation in the prompt-observation response
  producer: Architecture 26 R-12 (application.pcpg_actor_projection), serialized at B-10
            (application.http_pcpg), composed per request by application.pcpg_runtime_composition
  anchor:   checkpoint-PFC-PCPG-18 (41b4324)

Frontend-local terms (never on the wire):
  derived membrane label, CYAN status aggregates, PresentationCategory,
  PresentationAttachmentMap, object membrane, decision area, provider-related area,
  boundary area, panel, "Superseded"
```

### 13.2 Exact TypeScript shape (mirrors the materialized serializer)

```ts
type GovernanceObservation =
  | { readonly kind: "unavailable"; readonly reasonCode: UnavailableReason }
  | GovernanceObservationCurrent;

type UnavailableReason =
  | "SEMANTIC_OBSERVATION_UNAVAILABLE"    // R-05 failure
  | "FIELD_RECONSTRUCTION_UNAVAILABLE"    // R-03 structural failure
  | "PROJECTION_INCOMPLETE";              // any other failure R-04 onward

interface GovernanceObservationCurrent {
  readonly kind: "current";
  readonly contract: "PCPG-R12/1";
  readonly basis: {
    readonly rawIntentDigestSha256: string;
    readonly derivationTime: string;      // ISO-8601
  };
  readonly semanticObservation: {
    readonly ruleSetVersion: string;
    readonly clauses: readonly string[];
    readonly actions: readonly {
      readonly clauseIndex: number;
      readonly span: readonly [number, number];
      readonly clauseText: string;
      readonly modality: "ASSERTED" | "REQUESTED" | "CONDITIONAL" | "PROHIBITED" | "HYPOTHETICAL";
      readonly negated: boolean;
      readonly requestedExecutor: "HUMAN" | "AI" | "NONE";
      readonly candidateOperation: string | null;
      readonly target: string | null;
      readonly possibleExternalEffect: boolean;
      readonly possibleSecretContent: boolean;
      readonly decisionSubstitutionRequested: boolean;
    }[];
    readonly unknownRelations: readonly string[];
    readonly relationsTouched: readonly string[];
    readonly declaredPurpose: string | null;
    readonly semanticPurpose: string | null;          // null = not determinable
    readonly purposeAlignment: "ALIGNED" | "DRIFTED" | null;
    readonly semanticDrift: boolean;
  };
  readonly deltas: readonly DeltaWire[];              // §08.1
  readonly chain: ChainWire;                          // §09.1
  readonly capability: Capability;                    // §06.2
  readonly composedProofCeiling: "GOVERNED" | "FIXTURE_NON_PROOF" | null;   // Session-level proof ceiling (partial I-12)
}
```

`rawIntent`, `observedAt`, `workspace` and `session` are siblings of `governanceObservation` in the outer `kind: "ok"` envelope and are not repeated inside it. An input rejection uses the outer HTTP envelope (`rejected` / `denied` / `not_found`), never a `governanceObservation` kind.

### 13.3 Absent / unknown semantics

```text
null                      = UNKNOWN / not determinable / not applicable — never false, never empty-as-value
kind "unavailable"        = no current governance result exists; no Send offered, nothing allowed
no observation submitted  = no governance statement at all (not "current", not "allowed")
target null               = unresolved referent; never OUT_OF_SCOPE
INDETERMINATE             = never rendered as DENIED
sets (reasons, flags, relationsTouched) are sorted arrays; order carries no meaning
```

### 13.4 B-10: what never crosses

```text
R-11 EligibleContentSet (eligible inputs, retained instruction semantics, excluded delta ids, result, reasons)
AuthorityFact binding_id / binding_version, grantor details
Pulse internals
ProviderContext (environment, provider configuration) as raw material
DataClassification structures (their effect crosses only as result / reasonCode)
operation-index internals (readiness producer, http route, architecture ref)
any client-supplied capability, observation or basis as an input (client → server)
```

### 13.5 `eligibleContent`: removed

- The eligible-content **set** is forbidden by B-10.
- A **status** is not derivable without invention: R-11's own vocabulary has a single value (`NO_ELIGIBLE_CONTENT`), and R-11 is not part of R-12's output (the runtime composition never calls it).
- Non-emptiness is already implied by crossed facts (`chain.maximumLegitimateTransition`, `capability.governanceAdmissibleReasons` incl. `MLT_EMPTY`).

```text
ELIGIBLE CONTENT STATUS != ELIGIBLE CONTENT SET
```

### 13.6 CYAN-only attachment map

```ts
type PresentationAttachmentMap =
  Readonly<Record<PresentationCategory, readonly PresentationAttachment[]>>;
```

This map is not backend truth. It is CYAN projection placement.

### 13.7 Contract evolution

Any change to the shape above is a new contract identity (`PCPG-R12/2`, …), produced by RED first. A CYAN parser that sees an unknown `contract` value fails closed ("Governance unavailable"). CYAN never extends the contract by expectation.

---

## 14 — FRONTEND STATE MACHINE

The UI state machine remains separate from governance truth.

```text
NO_OBSERVATION
OBSERVATION_REQUESTED
LOADING
CURRENT
SUPERSEDED            (CYAN-local: object changed after derivationTime)
UNAVAILABLE           (governanceObservation.kind = "unavailable")
REQUEST_REJECTED      (outer envelope rejected / denied / not_found)
BACKEND_ERROR
MALFORMED_PROJECTION  (parser failure / unknown contract / unknown closed value)
```

Display states derived from `CURRENT` (CYAN-local, §06.1):

```text
OBSERVED
BOUNDARY_REACHED
HUMAN_AUTHORITY_REQUIRED
PARTIAL
PROVIDER_NOT_EXECUTABLE
```

Correct relation:

```text
PCPG-R12/1
+ CYAN-local derivations (label, aggregates, PresentationCategory)
+ PresentationAttachmentMap
→ object membrane
→ component-level presentation
→ action-adjacent friction
→ panel
```

Not:

```text
component state
→ governance truth
```

---

## 15 — DESKTOP ARCHITECTURE

```text
<header>
  [Log out]
</header>

<main>
  ┌───────────────────────────────────────────────────────┐
  │ Object Governance Membrane                            │
  │ Field · <derived label> · observed at <time>          │
  │ [Details]                                             │
  └───────────────────────────────────────────────────────┘

  WorkspaceBadge

  ChallengeSummary

  SessionStateBadge
    └─ attachment for SESSION_STATE category if present

  BurstPanel
    └─ attachment for BURST / PROVIDER categories if present

  QuestionList
    └─ attachment for QUESTION category if present

  DecisionSection
    └─ attachment for DECISION / AUTHORITY categories if present

  DeniedBanner / IndeterminateBanner
    └─ attachment for AUTHORITY / EXTERNAL_OR_DISCLOSURE categories if present

  <details>
    <summary>Field / Governance</summary>
    GovernancePanel
  </details>
</main>
```

The UI keeps `DecisionSection`, `DeniedBanner` and the rest because that is CYAN-local attachment. The backend never names those components.

---

## 16 — MOBILE ARCHITECTURE

```text
<header>
  [Log out]
</header>

<main>
  Field · Boundary reached [Details]

  Workspace
  Challenge

  Session state

  Burst
    Provider not executable (if PROVIDER category present)

  Questions
    Boundary at SELECT_PRIMARY_QUESTION (if QUESTION category present)
    AI · DERIVED / PROPOSAL

  Decision
    (AUTHORITY attachments, if present)

  ▾ Governance
    Label
    Capability
    Basis
    Semantic observation
    Presentation attachments
    Deltas
    Boundary / FBR
    Human Authority required
    Provider · Send not materialized
    Session-level proof ceiling (partial I-12)
    Not materialized
</main>
```

Mobile law:

```text
same PCPG-R12/1 observation
same CYAN-local derivations
same object-bound model
different presentation attachment
```

---

## 17 — ACCESSIBILITY

Accessibility describes crossed facts and their meaning, not just visual position.

### Required labels

```text
Governance for this session: Human Authority required. Observed at 11:17.

Provider execution: not executable. Reason: no eligible provider route.

Send: not materialized.

Human authority required for 2 requested steps.
```

### Screen-reader detail

```text
Governance admissible: false. Reason: MLT empty.
Provider executable: false. Reasons: no eligible provider route.
Can send: false. Send relation not materialized.
First broken relation: select primary question, state boundary.
Chain partial.
Session-level proof ceiling, partial: governed.
```

### Keyboard / focus

```text
object membrane reachable
details trigger reachable
attachment marker reachable where material
panel focus enters same-object inspection
escape/back returns to object
```

---

## 18 — MICROINTERACTIONS

### Allowed

```text
Field membrane opens panel
attachment marker focuses the attached object area
delta selection highlights its CYAN attachment and its span in the raw intent
boundary card reveals the exact FBR (predecessor → broken)
HAR row focuses the action-adjacent attachment
provider row focuses provider-related attachment
presentation attachment updates if object layout changes
```

### Forbidden

```text
backend-provided UI component names
frontend guesses a governance consequence
single status hiding the capability axes
fake scanning animation
AI thought-process stream
approval button from HUMAN_ACTION_AVAILABLE / HAR
send-like control before R-13
green/red truth collapse
rendering canSend = false as a send gate
rendering null as false
```

---

## 19 — VISUAL DESIGN SPECIFICATION

### Visual entities

```text
Object membrane
→ object-level governance strip

Attachment marker
→ small inline label placed by the CYAN map

Boundary
→ alert-like card

Human Authority required
→ definition list (deltaId · result · reasonCode)

Provider readiness
→ capability axis list with reasons

Send
→ explicit "Send not materialized" text

Session-level proof ceiling
→ labelled row "(partial I-12)"

Not materialized
→ plain list in deep view

Deep Field
→ relation inspector
```

### Visual law

```text
CROSSED FACT
→ user-perceptible placement

UI COMPONENT
→ replaceable transport shell
```

No decorative graph. No second cockpit. No admin dashboard.

---

## 20 — USER LANGUAGE ↔ CANONICAL SFE LANGUAGE MAP

| User language | Canonical / contract language |
|---|---|
| “This part of the object is involved.” | CYAN attachment of a delta (by `operation` / `executionClass`) |
| “This action cannot proceed yet.” | `chain.firstBrokenRelation.broken` · `result` · `reasonCode` |
| “This provider path is not executable.” | `executionClass PROVIDER_COMPUTATION` + `capability.providerExecutable false` + reasons |
| “Send does not exist yet.” | contract `PCPG-R12/1` contains no SEND relation (R-13 NOT STARTED) |
| “Authority is needed here.” | `chain.humanAuthorityRequired[]` / `result AUTHORITY_BOUNDARY` |
| “This view is older than the object.” | CYAN-local Superseded: object changed after `basis.derivationTime` |
| “Which part of my request caused this?” | delta `sourceClause` + `span` |
| “Where does this appear in the UI?” | CYAN presentation attachment |
| “How strong is the basis?” | Session-level proof ceiling (partial I-12) |
| “What stopped?” | FBR (`predecessor` → `broken`) |

---

## 21 — FAIL-CLOSED UX RULES

```text
UNKNOWN != ALLOW
UNKNOWN != DENIED
ABSENT != FALSE
NO OBSERVATION != CURRENT
CACHE != CURRENT AUTHORITY
DERIVED LABEL != FIELD TRUTH
PRESENTATION ATTACHMENT != GOVERNANCE DERIVATION
PRESENTATION LOCATION != GOVERNANCE TRUTH
CROSSED FACT != UI COMPONENT
canSend != SEND gate
BUTTON != PERMISSION
USER CLICK != AUTHORIZATION
FRONTEND != AUTHORITY
```

| Condition | UX |
|---|---|
| no observation submitted | "No observation"; no governance statement |
| `kind = "unavailable"` | Governance unavailable (+ reason code); nothing allowed, no Send |
| unknown `contract` value | Malformed projection; fail closed |
| unknown closed value (result, executionClass, modality, …) | Malformed projection; fail closed |
| `operation` null or not in CYAN map | `UNPLACED`; panel only, not guessed |
| `target` null | "unresolved"; never "out of scope" |
| `INDETERMINATE` | Indeterminate; never rendered as denied |
| object changed after `derivationTime` | Superseded; an older `canSend` is treated as absent |
| any SEND context | Send not materialized |
| FBR present | Boundary reached |
| HAR non-empty | no approval control unless an existing product action exists for this actor |

---

## 22 — SECURITY / INFORMATION DISCLOSURE

### Backend emits the actor-safe R-12 projection only

```text
PCPG-R12/1 contains only R-12 OUTPUT within B-10's ALLOW set (§13.4).
No eligible-content set, no binding identity, no Pulse internals, no provider-policy material.
```

### CYAN must not leak or invent

```text
show:
  Not materialized / Governance unavailable / unresolved

do not show or infer:
  holder names or classes
  provider payload or eligible content
  existence of out-of-scope objects (target OUT_OF_SCOPE is existence-blind by RED design)
  evidence sources
```

Raw intent may contain secrets (Architecture 26 DISCLOSURE D3). CYAN shows the actor's own raw intent only back to the actor. It may mask it, but it never logs, stores or forwards it.

### Existing repo alignment

The current API client already avoids local authority decisions from route ids and returns server-parsed results only. Governance preserves this exact relation.

---

## 23 — FBR REGISTER

### FBR-CYAN-LOCUS-01 — Backend nervePoints encoded UI topology

**Status:** repaired in v3, superseded in v4. The backend emits neither UI topology nor semantic loci; it emits `PCPG-R12/1`. Placement is the CYAN-local `PresentationCategory` → `PresentationAttachmentMap`.
**Proof required:** a Decision UI component can be renamed or restructured without any backend contract change.

### FBR-CYAN-LOCUS-02 — v3 `affectedSemanticLoci` re-encoded crossed RED facts

**Status:** repaired by v4 (§06.3).
**Repair:** object-relation hints = `target` + `relationsTouched` (+ `operation`); facet categories are CYAN-local; `SOURCE_RELATION` is future-only.

### FBR-CYAN-SYMBIOSIS-01 — Governance panel-centric scope

**Status:** repaired by full object symbiosis.
**Remaining proof:** the user can perceive boundary, provider, send and observation-time state without opening a panel.

### FBR-CYAN-STATUS-01 — Single canonical status collapses orthogonal Field truth

**Status:** repaired by v4. The capability axes are three independent booleans with reasons, and the chain is separate.
**Proof:** simultaneous `governanceAdmissible false + providerExecutable false + canSend false + FBR present + partial` renders without loss.

### FBR-CYAN-CONTRACT-01 — No CYAN consumer for PCPG-R12/1

**Producer:** RED R-12 via B-10, materialized at `checkpoint-PFC-PCPG-18` (producer side **closed**).
**Consumer:** CYAN GovernanceObservationProvider.
**Current relation:** `apps/web` has no typed client, no type definition and no fail-closed parser for `POST /workspaces/{workspaceId}/prompt-observations` / `governanceObservation`.
**Expected relation:** a typed client plus a parser equivalent to the existing typed API discipline (§02.3), exact to §13.2, failing closed on unknown contract, kind or closed value.
**Proof:** parser falsifiers per §13.3 / §21. B-10-forbidden fields are rejected if present. No allow path on parse failure.
**Status:** **OPEN. This is the first broken relation of CYAN.**

### FBR-CYAN-R13-01 — SEND not materialized

**Producer:** R-13 Future Send Effect Gate (NOT STARTED).
**Consumer:** provider/send UI.
**Current relation:** `PCPG-R12/1` contains no SEND relation.
**Expected relation:** the UI shows `Send not materialized`, keyed to the contract identity, with no send affordance.
**Proof:** E2E asserts no send-like control for any `PCPG-R12/1` observation, whatever the value of `canSend`.

### FBR-CYAN-FRESHNESS-01 — Observation time, not freshness

**Producer:** `basis.derivationTime` (RED); Superseded (CYAN-local).
**Expected relation:** an observation is a point-in-time derivation (derive on read). CYAN treats it as superseded when the object changed after `derivationTime`, and never as current authority. A full freshness projection is future-only.
**Proof:** a superseded observation does not render as current; an older `canSend` is treated as absent.

### FBR-CYAN-AUTHORITY-01 — Authority relation projection absent

**Status:** re-scoped by v4. `PCPG-R12/1` carries no authority structure, by B-10 design. Actor, role and existing capabilities come from the existing producers. HAR holder classes are future-only.
**Proof:** a role-present, authority-absent actor renders as no authority, and no holder class or binding is shown.

---

## 24 — IMPLEMENTATION WORK-UNIT MAP

Architecture only.

### CYAN-PCPG-01 — PCPG-R12/1 Typed Client + Fail-Closed Parser

Closes FBR-CYAN-CONTRACT-01.
- TypeScript types exact to §13.2, a client function for the prompt-observation query, and a parser.
- No component and no UI.
- Unknown contract, kind or closed value is rejected. Absent and `null` are preserved as distinct from `false`. B-10-forbidden keys are rejected.

### CYAN-PCPG-02 — CYAN-local derivations

The membrane label (§06.1), aggregates (§06.2) and `PresentationCategory` (§06.3): pure functions over parsed `PCPG-R12/1`.

### CYAN-PCPG-03 — Presentation Attachment Map

CYAN-local `PresentationCategory → PresentationAttachment[]`. No governance derivation.

### CYAN-PCPG-04 — Object Membrane

Object-level ambient governance, including "No observation" and "Superseded".

### CYAN-PCPG-05 — Attachment Rendering

Attach crossed facts to current UI surfaces via the CYAN map.

### CYAN-PCPG-06 — Action-Adjacent Friction

Session-state, decision, provider and authority areas show legitimate friction, plus "Send not materialized".

### CYAN-PCPG-07 — Inline Governance Panel

Same-object inspection.

### CYAN-PCPG-08 — Deep Field Inspector

Same-object relation view, including the explicit "Not materialized" list.

### CYAN-PCPG-09 — E2E Proofs

```text
no UI component names and no semantic loci in the backend projection
crossed fact maps to current UI attachment via the CYAN map
unknown contract / closed value fails closed
unmapped operation shows panel-only fallback
no send affordance for PCPG-R12/1
null never renders as false; INDETERMINATE never renders as denied
superseded observation does not render as current authority
boundary visible without opening panel
HAR / HUMAN_ACTION_AVAILABLE does not auto-render approval
proof ceiling labelled "Session-level proof ceiling (partial I-12)"
component rename does not require backend contract change
```

### CYAN-PCPG-10 — Human Authority Review

Stop before canonicalization.

---

## 25 — ACCEPTANCE CRITERIA

Full canonical frontend symbiosis means:

```text
1. Governance lives inside the Session/Decision object.
2. User perceives governance before opening a panel.
3. Panel is inspection depth, not the governance system itself.
4. The backend emits PCPG-R12/1 only: no UI topology, no semantic loci, no display labels.
5. CYAN owns presentation categories and attachment only.
6. Presentation mapping is not governance derivation; presentation location is not governance truth.
7. A crossed fact is not a UI component.
8. Capability axes remain separate (governanceAdmissible / providerExecutable / canSend, each with reasons).
9. Any display label remains CYAN-derived.
10. Boundary/FBR is impossible to miss when material.
11. Authority remains separate from actor, role, membership and capability; no authority internals cross.
12. Provider readiness does not imply send; canSend is not a SEND gate.
13. R-13 absence is visible as Send not materialized, keyed to the contract identity.
14. Unknown never becomes allowed; absent never becomes false.
15. A superseded observation never becomes current authority.
16. The proof ceiling is labelled Session-level (partial I-12); evidence and provenance are shown as not materialized.
17. Opaque refs remain opaque unless backend resolves them.
18. UI can be refactored without backend governance contract changes.
19. No second app, no dashboard, no AI control center.
20. User stays in the object and changes only inspection depth.
```

---

# REQUIRED WIREFRAMES — CORRECTED FULL SYMBIOSIS (v4)

## A — Normal NQUIRY State With Quiet Object Membrane

```text
<header>
  [Log out]
</header>

<main>
  ┌──────────────────────────────────────────────┐
  │ Field · No observation                   [i] │
  └──────────────────────────────────────────────┘

  Workspace: ws-...
  Challenge:
    Reduce onboarding drop-off

  Session state: QUESTION_CAPTURE

  Burst state: ACTIVE
  HUMAN_ONLY

  Questions
    HUMAN  Why do users abandon step 3?
    AI     DERIVED / PROPOSAL  Is step 3 latency the driver?

  Decision
    No Decision is currently under consideration.

  ▸ Field / Governance details
</main>
```

## B — Governance Panel Open (current observation)

```text
<main>
  ┌──────────────────────────────────────────────┐
  │ Field · Provider not executable         [–] │
  └──────────────────────────────────────────────┘

  ┌─ Governance for this Session · PCPG-R12/1 ───────────────────┐
  │ Observed at: 2026-10-01T11:17Z · digest 3f9a…                │
  │                                                              │
  │ Capability                                                   │
  │   Governance admissible: false   (MLT_EMPTY)                 │
  │   Provider executable:   false   (NO_ELIGIBLE_PROVIDER_ROUTE)│
  │   Can send:              false                               │
  │   Send: not materialized (no SEND relation in PCPG-R12/1)    │
  │                                                              │
  │ Your request                                                 │
  │   "Analyse the questions" → REQUEST_QUESTION_ANALYSIS        │
  │                                                              │
  │ Current presentation attachments (CYAN-local)                │
  │   Provider-related area                                      │
  │                                                              │
  │ Deltas · Boundary / FBR · Human Authority required           │
  │ Session-level proof ceiling (partial I-12): —  (none retained)│
  │ Not materialized: evidence, provenance, HAR holder classes   │
  └──────────────────────────────────────────────────────────────┘
</main>
```

## C — Blocked / FBR State

```text
<main>
  ┌──────────────────────────────────────────────┐
  │ Field · Boundary reached                [i] │
  └──────────────────────────────────────────────┘

  Questions
    Boundary at: SELECT_PRIMARY_QUESTION

  ┌─ Boundary / FBR ─────────────────────────────────────────────┐
  │ What stopped?  SELECT_PRIMARY_QUESTION · HUMAN_COMMAND       │
  │ Requested in:  "pick the primary question"                   │
  │ Why?           STATE_BOUNDARY · <reasonCode>                 │
  │ After:         first in chain                                │
  │ Chain:         partial                                       │
  │ Current presentation (CYAN-local):                           │
  │   Question area                                              │
  │ No bypass action is available.                               │
  └──────────────────────────────────────────────────────────────┘
</main>
```

## D — Human Authority Required State

```text
<main>
  ┌──────────────────────────────────────────────┐
  │ Field · Human Authority required        [i] │
  └──────────────────────────────────────────────┘

  ┌─ Human Authority required ───────────────────────────────────┐
  │ Δ0 BEGIN_ANALYSIS          · AUTHORITY_BOUNDARY  · <reason> │
  │ Δn <operation>             · GOVERNANCE_BOUNDARY · <reason> │
  │                                                              │
  │ Holder: not materialized                                     │
  │ No approval control is available here. A human action the    │
  │ actor may take appears only through existing product controls.│
  └──────────────────────────────────────────────────────────────┘
</main>
```

## E — Delta Detail

```text
<main>
  ┌─ Delta Δ1 ───────────────────────────────────────────────────┐
  │ Requested: "Analyse the questions"   (span 0–21)             │
  │ Operation: REQUEST_QUESTION_ANALYSIS · PROVIDER_COMPUTATION  │
  │ Result:    INDETERMINATE · DATA_GOVERNANCE_NOT_MATERIALIZED  │
  │ Target:    unresolved                                        │
  │ Session-level proof ceiling (partial I-12): GOVERNED         │
  │                                                              │
  │ Current presentation attachment (CYAN-local)                 │
  │   Provider-related area                                      │
  │                                                              │
  │ Evidence: not materialized · Provenance: not materialized    │
  └──────────────────────────────────────────────────────────────┘
</main>
```

## F — Advanced Field Inspection

```text
<main>
  ┌─ Deep Field Inspector · PCPG-R12/1 ──────────────────────────┐
  │ FIELD PRE_CALL_PROMPT_GOVERNANCE                             │
  │  ├─ BASIS                                                    │
  │  ├─ SEMANTIC OBSERVATION (rule set <ruleSetVersion>)         │
  │  ├─ DELTAS                                                   │
  │  ├─ CHAIN  FBR · MLT · NVT · HAR · PARTIAL                   │
  │  ├─ CAPABILITY (+ reasons)                                   │
  │  ├─ SESSION-LEVEL PROOF CEILING (partial I-12)               │
  │  ├─ PRESENTATION ATTACHMENTS (CYAN-local)                    │
  │  └─ NOT MATERIALIZED                                         │
  │       SEND relation (R-13) · evidence · provenance ·         │
  │       HAR holder classes · SOURCE_RELATION                   │
  └──────────────────────────────────────────────────────────────┘
</main>
```

## G — Mobile Full Symbiosis

```text
<main>
  Field · Boundary reached  [Details]

  Workspace: ws-...
  Challenge: ...
  Session: QUESTION_CAPTURE

  Burst
    Provider not executable

  Questions
    Boundary at SELECT_PRIMARY_QUESTION
    AI · DERIVED / PROPOSAL

  Decision
    No action available here

  ▾ Governance
    Label · Capability · Basis · Deltas · Boundary / FBR ·
    Human Authority required · Send not materialized ·
    Session-level proof ceiling (partial I-12) · Not materialized
</main>
```

---

# CRITICAL ACCEPTANCE TEST

Does this architecture make governance feel like a second application?

```text
No — governance is distributed through the Session/Decision object itself:
object membrane, fact-anchored signals, action-adjacent friction, context panel, deep field view.
```

Does it enter the user’s “nervous system” without violating SFE?

```text
Yes — relevant governance states become perceptible where the user reads, decides, acts or hits a boundary.
No SFE violation — RED emits PCPG-R12/1 (truth); CYAN derives presentation only and never sends it back.
```

Does CYAN need to invent backend truth?

```text
No. Every rendered governance fact is a PCPG-R12/1 field or a deterministic CYAN-local function of one.
Everything else is shown as "not materialized".
```

---

# FINAL SYSTEM MODEL

```text
NQUIRY SESSION / DECISION OBJECT
        │
        ├──────────── NORMAL PRODUCT INTERACTION
        │              Workspace · Challenge · Session state · Burst · Questions · Decision
        │
        ├──────────── GOVERNANCE PERCEPTION LAYER
        │              Object membrane · fact-anchored signals · action-adjacent friction
        │              Boundary · Authority · Provider readiness · Observation time
        │
        └──────────── GOVERNANCE INSPECTION DEPTH (PCPG-R12/1)
                       Basis · Semantic observation · Deltas · Chain · Capability
                       Session-level proof ceiling (partial I-12) · Presentation attachments
                       Not materialized: SEND relation, evidence, provenance,
                                         HAR holder classes, SOURCE_RELATION
```

Final corrected state:

```text
CANONICAL RED → CYAN CONTRACT
→ PCPG-R12/1, materialized at checkpoint-PFC-PCPG-18

MULTIDIMENSIONAL CAPABILITY
→ real (three booleans + reasons; no backend TriState)

FULL OBJECT SYMBIOSIS / ACTION-ADJACENT GOVERNANCE
→ retained

FRONTEND != AUTHORITY
→ preserved

BACKEND SEMANTIC-LOCUS / DISPLAY / SEND-GATE INVENTION
→ removed

CANONIZATION READINESS
→ backend producer: materialized
→ CYAN consumer: open (FBR-CYAN-CONTRACT-01 → CYAN-PCPG-01)
→ pending E2E proof
→ pending Human Authority review
```

**STOP FOR HUMAN AUTHORITY REVIEW.**
