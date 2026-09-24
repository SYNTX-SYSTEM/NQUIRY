# NQUIRY :: SYMBIOTIC FRONTEND ARCHITECTURE

**Architecture Class:** Frontend System Architecture
**Mode:** System Field Engineering · Canonical Projection · Relational Interface Architecture
**Implementation:** Out of scope
**Primary Law:** Frontend projects state. Frontend does not create truth.

---

# 1. EXECUTIVE ARCHITECTURE VIEW

NQUIRY is not modeled as a collection of pages, dashboards, panels or workflow screens.

The frontend is a **canonically reconstructed relational interaction environment**.

Its primary causal model is:

```text
CANONICAL CONTEXT
→ CANONICAL STATE
→ HUMAN POSITION
→ VALID RELATIONS
→ VISIBLE AFFORDANCES
→ POSSIBLE EFFECT
→ REQUEST
→ COMMIT
→ RECONSTRUCTION
```

Parallel proof model:

```text
VISIBLE CLAIM
→ ORIGIN
→ ESTABLISHING RELATION
→ AUTHORITY SOURCE
→ SCOPE
→ COMMIT
→ EVIDENCE
→ PROVENANCE
→ PREVIOUS STATE
```

The frontend never becomes:

```text
semantic authority
canonical truth
governance engine
business-rule engine
state-transition engine
AI authority
optimistic substitute for committed state
```

The interface operates through three persistent conceptual planes.

## ORIENTATION PLANE

Answers:

* Where is the human?
* Which Workspace, Challenge and Session context exists?
* Which canonical state currently applies?
* Which relation established this position?
* Which prior relations are closed?
* Which future relations are merely possible?

## ACTIVE RELATION PLANE

Answers:

* What is happening now?
* What can be done here?
* What cannot be done?
* Which boundary prevents closure?
* Which visible content is human, system-derived, AI-derived or external evidence?

## PROOF PLANE

Answers:

* Why is this state valid?
* Why is this action available?
* Which authority source applies?
* Which command established the visible effect?
* What evidence exists?
* What was the previous state?
* Can the visible condition be reconstructed?

The primary experience remains calm because the Proof Plane is deep rather than permanently wide.

The interface does not continuously display machinery.

The interface behaves according to machinery.

---

# 2. SYSTEM CONTEXT

NQUIRY is organized around:

```text
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
```

The relevant visible path begins before a Session exists:

```text
LOGIN
→ WORKSPACE
→ GOVERNANCE
→ CHALLENGE
→ SESSION CREATION
→ DRAFT
→ SETUP
→ CHALLENGE_CAPTURE
→ QUESTION_GENERATION
→ QUESTION_CAPTURE
→ ANALYSIS
→ later Session phases
```

Within that state topology, the protected Human Question experience is not its own invented Session state.

The canonical relation is:

```text
CHALLENGE_CAPTURE
→ OPEN_QUESTION_GENERATION
→ Session = QUESTION_GENERATION
→ QuestionBurst = ACTIVE
→ Human Question Capture
→ manual CLOSE_QUESTION_GENERATION
→ QuestionBurst = COMPLETED
→ frozen raw Human Question membership
→ Session = QUESTION_CAPTURE
→ BEGIN_ANALYSIS
→ Session = ANALYSIS
```

The state-transition architecture explicitly defines `QUESTION_GENERATION → QUESTION_CAPTURE → ANALYSIS`; `QUESTION_CAPTURE` is therefore a canonical Session state, but Human Question capture occurs while the Session is in `QUESTION_GENERATION`. `QUESTION_CAPTURE` is the post-generation, capture-finalized state in which the raw set is frozen and input is closed.

Session creation begins from Session absence and establishes `DRAFT`, followed by `SETUP`, `CHALLENGE_CAPTURE` and then `QUESTION_GENERATION`.

Current prototype decisions further establish manual authorized Burst completion and presentation-only timing; the frontend must therefore not use timer expiry as completion authority.

The frontend architecture must preserve these canonical relations rather than flattening them into a visual workflow.

---

# 3. ARCHITECTURAL LAWS

The following laws are binding throughout the frontend.

```text
Capability != Authority

Candidate != Effect

Role != Authority

Authentication != Authority

Evidence != Authority

Derived != Human Source

Requested != Committed

Visible UI != Canonical State

Client State != Authority

Client Projection != Canonical Persistence

Presentation Time != System Authority

Network Failure != Proof Of No Effect

Local Green != Field Green

Field Green != Published Field
```

Additional frontend laws:

```text
VISIBLE EFFECT
<=
RECONSTRUCTABLE EFFECT
```

```text
DISPLAYED AUTHORITY
<=
SERVER-PROJECTED CURRENT AUTHORITY
```

```text
DISPLAYED CERTAINTY
<=
RECONSTRUCTABLE CERTAINTY
```

```text
STATE CHANGE
→
INTERFACE RECONSTRUCTION
```

```text
HUMAN SOURCE
→ immutable origin lineage
```

```text
AI DERIVED
→ visible source lineage
→ no implicit authority
```

```text
RESULT
!=
SESSION STATE
unless canonical architecture explicitly defines it as one
```

No frontend convenience may override these relations.

---

# 4. CURRENT FRONTEND RECONSTRUCTION

## F02

F02 establishes the lawful route into the inquiry context.

Materialized or explicitly established concerns include:

```text
LOGIN
→ WORKSPACE
→ GOVERNANCE
→ CHALLENGE
→ SESSION
→ lawful Session progression
→ QUESTION_GENERATION
```

Current F02 proof records establish that a Session can lawfully reach `QUESTION_GENERATION` with an `ACTIVE HUMAN_ONLY` Burst, participants and Session-scoped control.

F02 also establishes structural foundations needed by the symbiotic frontend:

* server capability projections
* authority provenance
* controlled outcome vocabulary
* canonical re-read after Commands
* state/version-aware Session transitions
* real-stack browser proof lane
* responsive and accessibility foundations
* visible provenance language
* separation of role from authority
* typed authority-source provenance

Current provenance material includes command, actor, authority type, scope and commit information for newly established state.

## F03

F03 owns the protected Human Question regime.

F03 does **not** introduce a new Session state for human input.

Its Human Question Capture occurs inside:

```text
Session = QUESTION_GENERATION
QuestionBurst = ACTIVE HUMAN_ONLY
```

The protected field owns:

* authorized participant capture
* exact `original_text`
* HUMAN origin
* no AI participation in capture
* manual completion
* Burst completion
* frozen raw membership
* capture closure
* presentation-only timer semantics

Completion closes `QUESTION_GENERATION` and establishes the canonical `QUESTION_CAPTURE` state.

## F04

F04 begins only after a valid frozen Human Source exists and the Session lawfully enters `ANALYSIS`.

Its frontend responsibilities include:

* source/derivation separation
* analysis status
* derived provenance
* explicit AI origin
* visible provider/mock ceilings where relevant
* no mutation of frozen Human Source

## Existing elements that already fit

The following existing relations align directly with the target architecture:

* server capability projection
* typed outcome vocabulary
* authority-source provenance
* exact canonical re-read
* version-aware transitions
* HUMAN_ONLY protected Burst
* immutable original text
* manual completion
* explicit effect gate
* real-stack browser proof

## Transitional elements

The following must not become the final mental model:

* page-centric Workspace/Challenge/Session hierarchy
* status badges as primary state representation
* independent panels for governance concepts
* generic Decision Surface as a button collection
* page-local success state
* client-inferred progression

---

# 5. FRONTEND FIRST BROKEN RELATIONS

Every frontend defect is traced to its first false relation.

| Visible defect                             | First broken relation                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------------ |
| Dashboard appearance                       | canonical state did not reorganize the interaction field                       |
| Card-grid proliferation                    | distinct relations were flattened into generic containers                      |
| Too many badges                            | state semantics were converted into labels instead of structure                |
| Governance wall                            | proof depth was flattened into permanent surface width                         |
| AI-chat appearance                         | derivation was modeled as conversation instead of source-bound transformation  |
| Human and AI content look alike            | Origin was lost before rendering                                               |
| Click appears immediately successful       | Request was collapsed into Effect                                              |
| Spinner becomes success                    | Pending was collapsed into Committed                                           |
| Role unlocks control                       | Role was collapsed into Authority                                              |
| Timer ends Burst                           | presentation time was collapsed into system authority                          |
| Human capture placed in `QUESTION_CAPTURE` | interaction relation was assigned to the wrong canonical state                 |
| Completion jumps directly to ANALYSIS      | `QUESTION_CAPTURE` canonical state and `BEGIN_ANALYSIS` transition were erased |
| RESULT displayed as Session phase          | derived artifact was promoted into invented canonical state                    |
| Network error shows failure                | transport failure was collapsed into consequence certainty                     |
| Mobile becomes cards                       | spatial semantics were tied to desktop geometry rather than relations          |
| Proof disappears on small screens          | progressive disclosure was implemented as optional layout chrome               |
| Stale controls remain active               | projection version was detached from affordance validity                       |
| Optimistic question appears canonical      | local draft was promoted before commit                                         |
| Frozen questions editable after completion | source status and source content invariants were not separated                 |

The repair rule is always:

```text
VISIBLE SYMPTOM
→ FIRST FALSE RELATION
→ AUTHORITATIVE REPAIR
→ RECURSIVE PROPAGATION
```

---

# 6. SYMBIOTIC FRONTEND PRINCIPLES

## 6.1 Canonical before visible

Material truth reaches the frontend from canonical state or an explicitly typed projection.

## 6.2 Relation before component

The primary design unit is a system relation, not a UI component.

## 6.3 State shapes space

State affects:

* focus
* density
* openness
* closure
* interaction
* available motion
* visual hierarchy
* proof depth
* affordance proximity

## 6.4 Position is relational

Position is not a breadcrumb.

It expresses how the current visible field was established.

## 6.5 Proof without bureaucracy

Proof remains completely accessible without becoming the permanent visual foreground.

## 6.6 Explicit uncertainty

Unknown consequence remains visibly unresolved.

## 6.7 Immutable origin

Transformation does not rewrite provenance.

## 6.8 Reconstruction over mutation theatre

After committed material change, the interface is reconstructed from canonical state.

## 6.9 Source before derivation

Human Source remains perceptually prior to AI interpretation.

## 6.10 No visual semantics without system semantics

Decoration may never masquerade as architecture.

---

# 7. FRONTEND PARENT FIELD

## FIELD ID

`PF-01`

## FIELD NAME

**NQUIRY RELATIONAL INTERACTION FIELD**

## PURPOSE

Provide one frontend Parent Field capable of containing the complete human-visible path before and after Session creation without pretending a Session exists prematurely.

## PARENT

NQUIRY application boundary.

## CHILDREN

```text
CF-01 POSITION & ORIENTATION FIELD
CF-02 CONTEXT ESTABLISHMENT FIELD
CF-03 RELATIONAL SESSION FIELD
CF-04 PROTECTED HUMAN SOURCE FIELD
CF-05 AI DERIVATION FIELD
CF-06 RESULT PROJECTION FIELD
CF-07 AUTHORITY & AFFORDANCE FIELD
CF-08 EFFECT & BOUNDARY FIELD
CF-09 PROOF & RECONSTRUCTION FIELD
```

## ENTRY RELATIONS

* authenticated or authentication-required application entry
* Workspace discovery/creation according to canonical governance
* existing deep link to an accessible canonical context

## EXIT RELATIONS

No invented terminal frontend relation.

Exit may occur through:

* leaving the application
* moving to another accessible context
* later canonical Session closure
* future relations not defined by this architecture

## CANONICAL INPUTS

* identity/session context
* Workspace projection
* governance projection
* Challenge projection
* Session projection where a Session exists
* capabilities
* authority projection
* outcome state
* provenance
* evidence
* derived artifacts
* freshness/version information

## CANONICAL STATE DEPENDENCIES

The Parent Field itself owns no domain state machine.

It contains contexts before a Session exists and projects Session state after creation.

## AUTHORITY DEPENDENCIES

None for existence as an interface container.

Every consequential child relation uses server-projected and backend-enforced authority.

## BOUNDARIES

* authentication loss
* inaccessible context
* NOT_FOUND
* DENIED
* STALE
* NETWORK_FAILURE
* INDETERMINATE
* unsupported/open downstream relation

## VISIBLE SEMANTICS

The Parent Field maintains continuity while the active semantic regime changes.

## PROOF REQUIREMENTS

Any consequential visible claim must be traceable to server projection and canonical cause.

## DOWNSTREAM CONSUMERS

All frontend Fields.

### Why `RELATIONAL SESSION FIELD` cannot remain the Parent

A Session Field cannot truthfully contain:

```text
LOGIN
WORKSPACE
GOVERNANCE
CHALLENGE before Session creation
Session absent
```

The Session Field therefore remains an important Child Field but is not the frontend root.

---

# 8. CHILD FIELD ARCHITECTURE

## CF-01 — POSITION & ORIENTATION FIELD

**Purpose:** preserve human position across context, state, transition and proof depth.

**Parent Relation:** direct child of PF-01.

**Inputs:** accessible contexts, active Workspace, Challenge, optional Session, Session state, previous transition, provenance reference.

**Canonical Sources:** server context projections and canonical Session reads.

**State Dependencies:** none before Session; canonical Session state afterward.

**Authority Dependencies:** none to display position; authority may restrict accessible branches.

**Origin Dependencies:** System State.

**Effect Dependencies:** previous committed effect may establish current position.

**Boundaries:** inaccessible parent, stale context, deleted/missing reference.

**Transitions:** global context change; Session transition; proof drill-in/out.

**Visible Semantics:** closed past, dominant present, non-guaranteed future.

**Provenance:** current position can expose establishing command/transition.

**Temporality:** state age and transition time remain separate.

**Responsive:** relational sequence becomes vertical on narrow layouts without losing parent-child context.

**Accessibility:** position exposed as ordered structural description, not coordinates alone.

**Acceptance Proof:** reload reconstructs the same position from canonical server data.

**Upstream Dependencies:** context projections.

**Downstream Dependencies:** every active Field.

**Open Relations:** none required for F03/F04.

---

## CF-02 — CONTEXT ESTABLISHMENT FIELD

**Purpose:** contain the pre-Session path truthfully.

**Parent Relation:** PF-01.

**Children:** Login relation, Workspace relation, Governance relation, Challenge relation, Session creation relation.

**Inputs:** identity, Workspace accessibility, governance, Challenge data, create-Session capability.

**Canonical Sources:** backend identity/context/governance/Challenge projections.

**State Dependencies:** no Session state before successful Session creation.

**Authority Dependencies:** server-evaluated operation authority.

**Origin Dependencies:** System State + Human Source where Challenge framing is human-origin content.

**Effect Dependencies:** Workspace/Challenge/Session creation effects.

**Boundaries:** DENIED, REJECTED, NOT_FOUND, FAILED_PRECOMMIT, INDETERMINATE.

**Transitions:** Session absence → `CREATE_SESSION` → Session `DRAFT`.

**Visible Semantics:** context becomes progressively established without implying future objects already exist.

**Provenance:** establishing actor, command, authority source and scope available where material.

**Temporality:** creation/commit time, not UI navigation time.

**Responsive:** linear context trace; no sidebar dependency.

**Accessibility:** structural headings and explicit current-context announcement.

**Acceptance Proof:** browser-created Session re-reads as canonical `DRAFT`.

**Upstream Dependencies:** F01/F02 runtime projections.

**Downstream Dependencies:** CF-03.

**Open Relations:** later governance extensions do not block current architecture.

---

## CF-03 — RELATIONAL SESSION FIELD

**Purpose:** represent the canonical Session lifecycle after Session existence.

**Parent Relation:** PF-01.

**Children:** CF-04, CF-05, CF-06 as state-dependent semantic subfields.

**Inputs:** Session projection, transition capabilities, challenge relation, participants, Burst relation.

**Canonical Sources:** canonical Session + transition projections.

**State Dependencies:**

```text
DRAFT
SETUP
CHALLENGE_CAPTURE
QUESTION_GENERATION
QUESTION_CAPTURE
ANALYSIS
```

and later canonical states when their frontend architecture is materialized.

**Authority Dependencies:** server-evaluated transition authority.

**Origin Dependencies:** primarily System State; child content introduces Human and AI origins.

**Effect Dependencies:** every Session transition.

**Boundaries:** wrong state, missing prerequisite, DENIED, STALE, INDETERMINATE.

**Transitions:** only named canonical transitions.

**Visible Semantics:** active Session state reorganizes the interaction space.

**Provenance:** every material state exposes its establishing transition.

**Temporality:** state age, transition time and effect time separated.

**Responsive:** current state remains dominant even when proof is sequenced.

**Accessibility:** canonical state announced as structural context, not badge-only.

**Acceptance Proof:** browser progression cannot skip a named canonical state.

**Upstream Dependencies:** CF-02.

**Downstream Dependencies:** CF-04/05/06.

**Open Relations:** later lifecycle frontend semantics beyond current bounded path.

---

## CF-04 — PROTECTED HUMAN SOURCE FIELD

**Purpose:** capture immutable human questions under the HUMAN_ONLY regime.

**Parent Relation:** CF-03.

**Inputs:** active Burst, authorized participants, capture capability, existing accepted Questions.

**Canonical Sources:** QuestionBurst, Question records, participation relation.

**State Dependencies:**

Active capture:

```text
Session = QUESTION_GENERATION
QuestionBurst = ACTIVE
```

Frozen presentation:

```text
Session = QUESTION_CAPTURE or later
QuestionBurst = COMPLETED
```

**Authority Dependencies:** capture authority for participants; completion authority separately projected.

**Origin Dependencies:** HUMAN only for captured Questions.

**Effect Dependencies:** capture Question command; manual close-generation command.

**Boundaries:** DENIED, STALE, CLOSED CAPTURE, FAILED_PRECOMMIT, INDETERMINATE.

**Transitions:** `QUESTION_GENERATION → QUESTION_CAPTURE`.

**Visible Semantics:** source-first, AI absent during capture, exact original text.

**Provenance:** actor, capture command, origin, commit, Burst membership.

**Temporality:** timer presentation only; capture commit time separate.

**Responsive:** input remains central; source list does not become generic cards.

**Accessibility:** HUMAN origin and frozen status explicitly announced.

**Acceptance Proof:** exact accepted `original_text` survives freeze unchanged.

**Upstream Dependencies:** valid QUESTION_GENERATION + active Burst + participation.

**Downstream Dependencies:** CF-05.

**Open Relations:** PAUSE/RESUME only if later exposed.

---

## CF-05 — AI DERIVATION FIELD

**Purpose:** project post-Burst AI analysis without contaminating Human Source.

**Parent Relation:** CF-03.

**Inputs:** frozen Human Source, analysis operation/status, derived artifacts, model/provider provenance.

**Canonical Sources:** frozen Question membership + AI derivation/provenance records.

**State Dependencies:** `ANALYSIS`.

**Authority Dependencies:** frontend does not authorize AI; `BEGIN_ANALYSIS` authority remains backend-owned.

**Origin Dependencies:** AI DERIVED.

**Effect Dependencies:** analysis invocation/status may have operational effects; model output itself is not authority.

**Boundaries:** source invalid, provider unavailable, validation failure, analysis incomplete.

**Transitions:** `QUESTION_CAPTURE → ANALYSIS`; later `ANALYSIS → REFLECTION` only when canonical conditions are met.

**Visible Semantics:** derivation appears downstream from frozen source.

**Provenance:** exact source set, analysis operation, provider/mode where available, validation proof.

**Temporality:** analysis start, completion and evidence freshness remain distinct.

**Responsive:** source lineage remains reachable without merging source and output.

**Accessibility:** AI origin included in structural accessible name/description.

**Acceptance Proof:** derived output cannot mutate source records.

**Upstream Dependencies:** valid freeze + lawful BEGIN_ANALYSIS.

**Downstream Dependencies:** CF-06.

**Open Relations:** AI-unavailable progression beyond ANALYSIS remains governed by upstream architecture.

---

## CF-06 — RESULT PROJECTION FIELD

**Purpose:** present derived analysis output without inventing a Session state or later Effect.

**Parent Relation:** CF-03, semantically downstream of CF-05.

**Inputs:** validated derived result, analysis status, lineage and provenance.

**Canonical Sources:** derived artifact/projection.

**State Dependencies:** exists within `ANALYSIS` unless a later canonical state explicitly carries it.

**Authority Dependencies:** none derived from AI output.

**Origin Dependencies:** AI DERIVED.

**Effect Dependencies:** none implied.

**Boundaries:** incomplete result, invalid derivation, stale source lineage, missing provenance.

**Transitions:** Result availability does not itself transition Session state.

**Visible Semantics:** outcome of derivation, not canonical Session phase.

**Provenance:** source → analysis operation → result.

**Temporality:** generated/validated time.

**Responsive:** result remains visually downstream from source.

**Accessibility:** result announced as derived, not human-authored.

**Acceptance Proof:** existence of result does not unlock an unprojected consequential control.

**Upstream Dependencies:** CF-05.

**Downstream Dependencies:** future candidate/effect relations only if later defined.

**Open Relations:** Result → Candidate → later consequence.

---

## CF-07 — AUTHORITY & AFFORDANCE FIELD

**Purpose:** translate server-projected action legitimacy into interface availability.

**Parent Relation:** PF-01, cross-cutting.

**Inputs:** capabilities, scope, reason, authority reference, state/version context.

**Canonical Sources:** server authority evaluation output and capability projection.

**State Dependencies:** current canonical context.

**Authority Dependencies:** backend only.

**Origin Dependencies:** System State.

**Effect Dependencies:** action requests.

**Boundaries:** DENIED, BLOCKED, STALE.

**Transitions:** none owned.

**Visible Semantics:** available, unavailable, not-yet, no-longer, out-of-field.

**Provenance:** authority source reference can drill into proof.

**Temporality:** projection freshness.

**Responsive:** control availability remains equivalent at all sizes.

**Accessibility:** reason for non-availability programmatically associated with control.

**Acceptance Proof:** no action becomes available from client-side role inference.

**Upstream Dependencies:** server capability and authority projections.

**Downstream Dependencies:** all consequential controls.

**Open Relations:** concrete transport shape may evolve.

---

## CF-08 — EFFECT & BOUNDARY FIELD

**Purpose:** preserve consequence certainty and distinct failure semantics.

**Parent Relation:** PF-01, cross-cutting.

**Inputs:** request status, outcome kind, commit proof, reconciliation state.

**Canonical Sources:** Command/outcome/commit projection.

**State Dependencies:** expected canonical version and current state.

**Authority Dependencies:** authority result may cause DENIED but is not evaluated here.

**Origin Dependencies:** System State.

**Effect Dependencies:** entire effect lifecycle.

**Boundaries:** all typed outcome classes.

**Transitions:** Possible → Requested → Pending → Committed or typed non-commit/uncertain outcome.

**Visible Semantics:** state change only after confirmed commit.

**Provenance:** command and commit reference.

**Temporality:** request time ≠ commit time.

**Responsive:** consequence state remains explicit without relying on animation.

**Accessibility:** outcome category and consequence certainty announced.

**Acceptance Proof:** network loss after mutation can remain INDETERMINATE.

**Upstream Dependencies:** outcome contracts.

**Downstream Dependencies:** Reconstruction.

**Open Relations:** reconciliation mechanism may differ physically without changing semantic contract.

---

## CF-09 — PROOF & RECONSTRUCTION FIELD

**Purpose:** preserve deep proof, evidence and canonical rebuilding.

**Parent Relation:** PF-01, cross-cutting.

**Inputs:** canonical read, previous state, command, actor, authority source, scope, commit, evidence, freshness.

**Canonical Sources:** audit/provenance/evidence/persistence projections.

**State Dependencies:** all material visible states.

**Authority Dependencies:** consumes provenance only.

**Origin Dependencies:** all origin classes.

**Effect Dependencies:** committed effects.

**Boundaries:** missing proof, stale projection, reconstruction failure.

**Transitions:** proof drilldown; canonical reconstruction.

**Visible Semantics:** semantic depth rather than permanent panel.

**Provenance:** owns complete reconstruction chain.

**Temporality:** commit/event/evidence times distinguished.

**Responsive:** proof becomes focused sequential depth on narrow screens.

**Accessibility:** proof path represented as ordered relations.

**Acceptance Proof:** every newly visible committed state traces back to establishing cause.

**Upstream Dependencies:** audit/provenance/re-read.

**Downstream Dependencies:** acceptance and falsification.

**Open Relations:** pre-existing rows with incomplete provenance remain explicit ceilings where relevant.

---

# 9. SEMIOTIC DIMENSION MODEL

| Dimension      | Structural responsibility                                    |
| -------------- | ------------------------------------------------------------ |
| SYSTEM STATE   | determines current spatial regime                            |
| POSITION       | determines relational orientation                            |
| AFFORDANCE     | projects possible human action                               |
| BOUNDARY       | exposes why a relation cannot close                          |
| AUTHORITY      | explains legitimate operation source                         |
| ORIGIN         | distinguishes source class                                   |
| EFFECT         | distinguishes possibility, request and committed consequence |
| PROVENANCE     | reconstructs visible cause                                   |
| TEMPORALITY    | distinguishes time meanings                                  |
| TRANSITION     | explains state closure and emergence                         |
| EVIDENCE       | exposes support without becoming authority                   |
| RECONSTRUCTION | replaces stale projection with canonical truth               |

No dimension may exist solely as a badge or metadata label.

---

# 10. SEMIOTIC CONSTANTS

| Constant          | System meaning                                | Visible role                   | Spatial behaviour                                          | Interaction behaviour                            | Accessibility equivalent                        | Must never be confused with |
| ----------------- | --------------------------------------------- | ------------------------------ | ---------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------- | --------------------------- |
| HUMAN SOURCE      | human-authored canonical source               | primary source material        | occupies source layer; stable under derivation             | editable only while lawful capture remains open  | “Human source”; frozen/editable state announced | AI DERIVED                  |
| SYSTEM STATE      | canonical system condition                    | environment/frame              | shapes entire active field                                 | not edited as content                            | canonical state named structurally              | human opinion               |
| AI DERIVED        | computed derivative                           | downstream interpretation      | linked from source, never overlays it                      | inspect lineage; no implicit consequence control | “AI-derived from…”                              | HUMAN SOURCE, Authority     |
| EXTERNAL EVIDENCE | referenced support/contradiction              | evidence depth                 | attached to claim/relation, outside canonical source layer | inspect source/freshness                         | evidence source and freshness announced         | System State, Authority     |
| POSSIBLE EFFECT   | server-projected possible consequence         | open action                    | near active relation, visually unclosed                    | may be requested                                 | “Available action”                              | committed effect            |
| REQUESTED EFFECT  | intent sent                                   | transient intent layer         | remains attached to old canonical state                    | prevent accidental duplicate where applicable    | “Requested; not yet committed”                  | Pending/Committed           |
| PENDING EFFECT    | processing without commit confirmation        | unresolved processing relation | old state remains canonical                                | wait/reconcile; no success claim                 | “Processing; state unchanged until confirmed”   | Committed                   |
| COMMITTED EFFECT  | canonical material change                     | established relation           | new field becomes structurally closed/real                 | proof drilldown available                        | “Committed” + new state                         | Requested                   |
| BOUNDARY          | invalid closure under current relation        | interruption                   | interrupts path rather than painting whole field red       | reason and valid next relation reachable         | boundary type + reason                          | generic error               |
| STALE             | projection no longer current                  | invalidated projection         | recedes and loses active affordances                       | reconstruct                                      | “Out of date; refresh/reconstruct required”     | DENIED                      |
| INDETERMINATE     | consequence certainty unavailable             | unresolved relation            | neither open nor closed                                    | reconcile before repeat                          | “Outcome unknown”                               | failure                     |
| PROVENANCE        | reconstructable cause chain                   | proof depth                    | extends inward/deeper                                      | drill down and return in place                   | ordered proof chain                             | primary workflow            |
| OPEN FIELD        | current relation admits lawful future closure | active/open geometry           | allows forward affordance                                  | perform server-projected actions                 | “Open/current”                                  | incomplete proof            |
| CLOSED FIELD      | relation has been canonically completed       | stable/contained geometry      | retains content but removes obsolete input                 | inspect, not mutate                              | “Closed”                                        | disabled due to failure     |
| TRANSITION        | canonical relation change                     | change boundary                | preserves unchanged elements, replaces changed elements    | no transition before commit                      | old/new state and cause announced               | navigation                  |
| RECONSTRUCTION    | canonical projection replacement              | restoration of truth           | stale view yields to re-read state                         | temporarily suppress stale consequence actions   | “State refreshed from canonical source”         | cosmetic refresh            |

Color may reinforce these constants but may never define them.

---

# 11. CANONICAL STATE TO INTERFACE MATRIX

Pre-Session context is not represented as invented Session states.

| Context / Canonical State | Human Position                 | Primary Focus                       | Allowed Affordances                                                                    | Unavailable Affordances                    | Authority                                                           | Boundary                                 | Origin Mix                         | Effect Semantics                                              | Proof Depth                          | Temporal Semantics                           | Spatial Behaviour                          | Transition In             | Transition Out             |
| ------------------------- | ------------------------------ | ----------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------- | ------------------------------------------------------------- | ------------------------------------ | -------------------------------------------- | ------------------------------------------ | ------------------------- | -------------------------- |
| Login / no Session        | application entry              | establish identity                  | server-supported authentication                                                        | inquiry actions                            | identity only, not domain authority                                 | auth failure                             | System                             | auth effect only                                              | low                                  | session freshness                            | narrow entry field                         | none                      | Workspace context          |
| Workspace / no Session    | inside Workspace context       | orientation/governance              | projected Workspace actions                                                            | Session-state actions                      | server projection                                                   | DENIED/BLOCKED                           | System + Human where relevant      | contextual effects                                            | medium                               | commit times                                 | contextual field                           | Login                     | Governance/Challenge       |
| Governance / no Session   | authority context              | legitimate capability establishment | server-projected governance actions                                                    | client-inferred grants                     | backend authority                                                   | DENIED/REJECTED                          | System                             | governed effects                                              | deep proof available                 | authority freshness                          | proof near action only when needed         | Workspace                 | Challenge                  |
| Challenge / no Session    | problem context                | Challenge relation                  | create Session when projected                                                          | Session transitions                        | create-Session authority                                            | DENIED/BLOCKED                           | Human + System                     | Session creation possible                                     | medium                               | Challenge age/commit                         | Challenge central                          | Governance                | CREATE_SESSION             |
| `DRAFT`                   | Session exists                 | established inquiry object          | BEGIN_SETUP if projected                                                               | later transitions                          | Session control                                                     | DENIED/STALE                             | System                             | possible transition                                           | medium                               | state age                                    | new Session field opens                    | CREATE_SESSION            | `SETUP`                    |
| `SETUP`                   | preparing Session              | setup relation                      | setup + BEGIN_CHALLENGE_CAPTURE as projected                                           | question generation                        | Session control                                                     | BLOCKED if setup missing                 | Human/System                       | request/commit separation                                     | medium                               | setup/state age                              | configurable space                         | DRAFT                     | `CHALLENGE_CAPTURE`        |
| `CHALLENGE_CAPTURE`       | framing active inquiry         | Challenge capture                   | OPEN_QUESTION_GENERATION when prerequisites pass                                       | Human Question capture before Burst active | Session/Burst control                                               | BLOCKED/DENIED                           | Human + System                     | transition bundle possible                                    | medium/deep                          | transition time                              | challenge framing dominant                 | SETUP                     | `QUESTION_GENERATION`      |
| `QUESTION_GENERATION`     | inside ACTIVE HUMAN_ONLY Burst | Human Question Source               | authorized question capture; manual completion where projected                         | AI derivation; post-Burst analysis         | participant capture + Session-scoped prototype completion authority | DENIED/STALE/CLOSED/FPC/INDETERMINATE    | HUMAN dominant + System frame      | capture commits; completion remains requested until committed | source provenance directly reachable | timer presentation-only; capture commit time | Human Source occupies central field        | OPEN_QUESTION_GENERATION  | CLOSE_QUESTION_GENERATION  |
| `QUESTION_CAPTURE`        | Burst completed; source frozen | frozen Human Source                 | BEGIN_ANALYSIS when projected                                                          | new Human Question capture                 | backend-evaluated BEGIN_ANALYSIS authority                          | BLOCKED if freeze proof incomplete       | HUMAN frozen + System State        | no capture effect; analysis transition possible               | freeze proof prominent but calm      | freeze commit time                           | source field visibly closed                | CLOSE_QUESTION_GENERATION | `ANALYSIS`                 |
| `ANALYSIS`                | post-Burst derivation          | source-bound AI analysis            | analysis/query interactions defined by backend; later BEGIN_REFLECTION only when valid | source mutation; AI self-authorization     | backend only                                                        | provider/validation/authority boundaries | HUMAN frozen + AI DERIVED + System | AI output ≠ Effect                                            | derivation lineage deep              | analysis event/completion time               | source stable; derivation grows downstream | BEGIN_ANALYSIS            | later canonical transition |

`RESULT` is intentionally absent from the canonical state column.

A derived result is an artifact/projection in the analysis regime, not an invented Session state.

---

# 12. POSITION ARCHITECTURE

Position consists of six coordinates:

```text
ACCESS CONTEXT
WORKSPACE
CHALLENGE
SESSION OR SESSION-ABSENCE
CANONICAL SESSION STATE
ESTABLISHING TRANSITION
```

Position is represented as a **Relation Trace**, not a breadcrumb:

```text
established parent
→ established child
→ current relation
→ lawful possible relation
```

Rules:

* completed relations are perceptually closed
* current relation is dominant
* future relations are never rendered as already-existing destinations
* unavailable future relations may remain understandable when their boundary matters
* proof can be entered without losing position
* returning from proof restores the exact prior relational context

Before Session creation:

```text
Workspace
→ Challenge
→ Session possible
```

After Session creation:

```text
Workspace
→ Challenge
→ Session
→ current canonical state
```

The interface never fabricates a Session-level position before the Session exists.

---

# 13. AFFORDANCE ARCHITECTURE

Affordance is a server-projected possibility.

The frontend may not calculate authority from:

* role
* route
* page
* local state
* user identity alone
* presence of a button
* timer expiry
* possession of data

Minimum semantic projection for a consequential affordance:

```text
relation
availability
scope
reason if unavailable
authority source reference where relevant
canonical state/version context
command relation
freshness/revalidation context
```

## Visible and executable

Used when:

* relation exists now
* server projects availability
* current projection remains valid
* action is relevant to human position

## Visible but not executable

Used when understanding the boundary is itself important.

Examples:

* Manual completion exists but current actor lacks projected authority.
* BEGIN_ANALYSIS is blocked because freeze proof is incomplete.
* An action was available before the visible projection became stale.

## Hidden

Used only when the relation is not semantically part of the current field.

Hidden must not be used to conceal an important governance boundary.

## No longer possible

A previously active affordance becomes a historical relation after commit.

It is no longer presented as an active control.

---

# 14. BOUNDARY ARCHITECTURE

Boundary means:

> A relation cannot validly close under the current canonical conditions.

## DENIED

Cause class:

Authority/scope does not permit the operation.

UI consequence:

* no canonical mutation
* authority reason accessible
* source/state remains stable
* no technical-failure styling required

## REJECTED

Cause class:

Request is structurally or semantically invalid before lawful effect.

Examples include malformed or conflicting request identity.

UI consequence:

* request-specific correction
* no authority implication unless denial is actually the cause
* no success residue

## STALE

Cause class:

Visible projection no longer matches the canonical state/version required by the action.

UI consequence:

* stale controls lose consequence ability
* reconstruction becomes primary
* old state may remain readable as explicitly stale

## BLOCKED

Cause class:

Relation exists but prerequisite is currently absent.

UI consequence:

* target remains conceptually visible
* missing prerequisite exposed
* no suggestion that an attempted effect failed

## FAILED_PRECOMMIT

Cause class:

The system can prove the attempted effect did not commit.

UI consequence:

* canonical prior state remains
* retry may be offered only where command semantics permit it

## INDETERMINATE

Cause class:

The system cannot prove whether the effect committed.

UI consequence:

* neither success nor failure
* prevent blind duplicate consequence
* reconciliation/re-read takes precedence

## NOT_FOUND

Cause class:

Referenced canonical object or relation is unavailable in valid scope.

UI consequence:

* do not invent replacement
* reconstruct nearest confirmed parent context

## NETWORK_FAILURE

Read path:

* latest projection unavailable
* last confirmed state may remain only when explicitly marked as last confirmed/stale

Mutation path:

* if commit certainty is unknown, escalate semantically to INDETERMINATE

No meaning is transported only through red/green styling.

---

# 15. AUTHORITY ARCHITECTURE

Authority has three separate layers.

```text
AUTHORITY EVALUATION
!=
AUTHORITY PROJECTION
!=
AUTHORITY PROVENANCE
```

## AUTHORITY EVALUATION

Owned exclusively by backend/application/domain boundaries.

May include:

* current membership
* HumanAuthorityBinding
* current Role where Role is a typed authority source
* Founding relation
* Session scope
* current state
* current version
* operation-specific constraints

The frontend never reproduces these rules.

Current effect-gate materialization uses typed authority sources and requires a resolvable `AuthoritySourceProof`; newly established provenance can identify BINDING, ROLE or FOUNDING as typed source categories without reducing Role itself to universal authority.

## AUTHORITY PROJECTION

The frontend needs only enough server output to understand the current action relation:

```text
available / unavailable
operation or relation
scope
reason
authority source reference
state/version context
freshness/revalidation result where relevant
```

This is not permission logic.

It is the projection of permission logic.

## AUTHORITY PROVENANCE

When proof depth is opened:

```text
operation
→ actor
→ authority source type
→ authority source ref
→ scope
→ evaluation context
→ command
→ commit
```

## Disclosure Levels

### Level 0 — Embedded legitimacy

Control exists or does not.

### Level 1 — Reason

Why available/not available.

### Level 2 — Authority proof

Source, scope, freshness/revalidation.

### Level 3 — Full provenance

Command, actor, authority source, commit and previous state.

---

# 16. ORIGIN ARCHITECTURE

Four visible origin classes are mandatory.

## HUMAN SOURCE

Characteristics:

* exact authored content
* canonical source identity
* no AI reinterpretation inside the source surface
* remains human after later AI processing
* frozen status does not alter origin

## SYSTEM STATE

Characteristics:

* canonical condition
* belongs to interface structure rather than conversational voice
* never styled as human opinion

## AI DERIVED

Characteristics:

* explicitly downstream from source
* retains source lineage
* does not inherit human origin
* does not inherit authority
* may be a Candidate
* is not automatically a Candidate unless system semantics establish one

## EXTERNAL EVIDENCE

Characteristics:

* source/freshness/provenance visible
* independent from NQUIRY canonical state
* may support or contradict
* never creates operation authority

Origin grammar combines:

* container relation
* structural level
* typography
* explicit accessible origin
* interaction behaviour
* provenance link

Color alone is invalid.

---

# 17. EFFECT ARCHITECTURE

Canonical frontend effect lifecycle:

```text
POSSIBLE
→ REQUESTED
→ PENDING
→ COMMITTED
```

Alternative outcomes:

```text
DENIED
REJECTED
FAILED_PRECOMMIT
INDETERMINATE
STALE
```

## POSSIBLE EFFECT

Projected capability.

No request exists.

## REQUESTED EFFECT

Human or system intent has been submitted.

Canonical state remains unchanged.

## PENDING EFFECT

Execution has not yet produced confirmed commit.

Canonical prior state remains visually authoritative.

## COMMITTED EFFECT

Only commit establishes material change.

The frontend then:

```text
receives/recognizes commit
→ invalidates old consequence projection
→ acquires canonical post-commit projection
→ reconstructs active field
```

## DENIED EFFECT

No effect.

Authority boundary.

## REJECTED EFFECT

No effect.

Request invalid or inconsistent.

## FAILED EFFECT

No commit where precommit failure is provable.

## INDETERMINATE EFFECT

Effect certainty unknown.

The interface must retain uncertainty until canonical reconciliation closes it.

Candidate is outside this lifecycle until an actual authorized Command relation exists.

---

# 18. PROVENANCE ARCHITECTURE

Primary proof chain:

```text
VISIBLE STATE
→ ESTABLISHED BY
→ COMMAND
→ ACTOR
→ AUTHORITY SOURCE
→ SCOPE
→ COMMIT
→ EVIDENCE
→ PREVIOUS STATE
```

For Human Source:

```text
VISIBLE QUESTION
→ HUMAN ORIGIN
→ CAPTURE COMMAND
→ HUMAN ACTOR
→ BURST MEMBERSHIP
→ COMMIT
```

For AI Derived:

```text
VISIBLE DERIVED RESULT
→ DERIVATION
→ FROZEN SOURCE SET
→ ANALYSIS OPERATION
→ PROVIDER / MODE PROVENANCE
→ VALIDATION
→ DERIVED ARTIFACT
```

For state transition:

```text
VISIBLE SESSION STATE
→ TRANSITION COMMAND
→ PREVIOUS SESSION STATE
→ AUTHORITY
→ COMMIT
→ NEW SESSION STATE
```

Provenance is deep navigation.

It is not a permanent admin sidebar.

---

# 19. TEMPORALITY ARCHITECTURE

The frontend recognizes distinct time semantics:

```text
ELAPSED TIME
STATE AGE
EVENT TIME
REQUEST TIME
COMMIT TIME
EVIDENCE FRESHNESS
PRESENTATION-ONLY TIME
SYSTEM-TRIGGERING TIME
```

These are never collapsed into one visual “time” category.

## Burst timer

Current prototype law:

```text
Timer = presentation only
Timer expiry != completion request
Timer expiry != authority
Timer expiry != canonical transition
```

Manual authorized completion establishes the closing request.

The frontend may display elapsed/remaining presentation time but must not:

* automatically call completion
* disable valid capture solely because local clock reached zero
* display frozen status before committed completion
* imply canonical state changed because the timer reached zero

---

# 20. TRANSITION ARCHITECTURE

A transition is:

```text
OLD CANONICAL STATE
+
AUTHORIZED / VALID TRANSITION RELATION
+
COMMIT
+
NEW CANONICAL STATE
+
RECONSTRUCTION
```

Transitions must make perceptible:

* what closed
* what persisted
* what became newly possible
* what became impossible
* which source remained unchanged
* which state was established
* which relation caused the change

## Canonical Human Source transition

```text
Session QUESTION_GENERATION
QuestionBurst ACTIVE
Human capture open

→ manual CLOSE_QUESTION_GENERATION request

→ commit

→ QuestionBurst COMPLETED
→ raw membership frozen
→ Session QUESTION_CAPTURE
→ Human capture closed
```

Only afterward:

```text
QUESTION_CAPTURE
→ authorized BEGIN_ANALYSIS
→ commit
→ ANALYSIS
```

A single animation must never visually erase these two canonical transitions.

---

# 21. EVIDENCE ARCHITECTURE

Evidence answers:

> What supports, contradicts or establishes the basis for this visible claim?

Authority answers:

> Why could this operation validly create an effect?

These relations remain independent.

Evidence presentation includes where available:

* evidence source
* relation to claim/artifact
* version
* freshness
* provenance
* support/contradiction role

Missing evidence is a visible semantic state where evidence is required.

No frontend may translate:

```text
evidence exists
```

into:

```text
operation authorized
```

or:

```text
claim universally true
```

---

# 22. RECONSTRUCTION ARCHITECTURE

Material state is never maintained by client fiction.

The required sequence is:

```text
REQUEST
→ OUTCOME
→ COMMIT CONFIRMED
→ CANONICAL RE-READ
→ NEW PROJECTION
→ INTERFACE RECONSTRUCTION
```

Current runtime work already uses canonical re-read after Session Commands, establishing the correct architectural direction.

## Old projection

After a committed material effect:

* old consequence controls are invalidated
* old state may remain transiently visible only to communicate transition
* old projection must not remain actionable

## New projection

The new field derives from canonical state.

## Stale prevention

Consequential affordances are bound to:

* current state
* expected version or equivalent freshness context
* server-projected capability

## Reconstruction failure

If a commit is known but post-commit projection cannot be loaded:

* do not fall back to old state as though unchanged
* show a committed-but-reconstruction-unavailable condition
* re-read before permitting dependent effects

---

# 23. HUMAN QUESTION FIELD EXPERIENCE

The active protected experience exists in:

```text
Session = QUESTION_GENERATION
QuestionBurst = ACTIVE HUMAN_ONLY
```

The central visible relation is:

```text
HUMAN PARTICIPANT
→ HUMAN QUESTION
→ CAPTURE REQUEST
→ COMMITTED HUMAN QUESTION
```

AI is absent from the capture field.

No:

* AI suggestions
* AI autocomplete
* AI rewriting
* AI ranking
* AI sorting
* AI clustering
* AI merging
* AI evaluation
* AI prompt surface
* AI chat
* AI “helpful” additions

The source field visually communicates:

```text
this is human raw material
```

without requiring repeated textual disclaimers.

## Input behaviour

Local input is a draft.

After submission:

```text
draft
→ REQUESTED
→ server outcome
```

Only a committed response/re-read may add the Question to canonical Human Source.

## Existing captured Questions

They display:

* exact original text
* Human origin
* no hidden normalization presented as source content
* capture provenance on demand

## Timer

Present but subordinate.

The timer cannot visually dominate the source field because it has no completion authority.

---

# 24. HUMAN SOURCE FREEZE EXPERIENCE

Freeze is not a visual styling toggle.

It is the visible consequence of a committed canonical transition.

## Before completion request

```text
Session = QUESTION_GENERATION
Burst = ACTIVE
capture open
manual completion may be available
```

## After completion request but before commit

```text
capture is not yet canonically frozen
Session is not yet QUESTION_CAPTURE
Requested != Committed
```

The interface must not prematurely:

* remove canonical capture because of local optimism
* declare the set frozen
* enter ANALYSIS
* display AI derivation

## After committed CLOSE_QUESTION_GENERATION

```text
Burst = COMPLETED
Session = QUESTION_CAPTURE
raw membership = frozen
capture = closed
original_text = unchanged
```

The space changes structurally:

* input affordance disappears
* source collection becomes closed
* questions retain their exact spatial/content identity
* freeze boundary becomes visible
* proof of closure is reachable
* no AI content enters the source container

The semantic message is:

```text
SOURCE STATUS CHANGED
SOURCE CONTENT DID NOT
```

---

# 25. HUMAN TO AI TRANSITION

The protected boundary is:

```text
QUESTION_GENERATION
    HUMAN SOURCE CAPTURE

→ COMMITTED FREEZE

QUESTION_CAPTURE
    FROZEN HUMAN SOURCE

→ BEGIN_ANALYSIS

ANALYSIS
    AI DERIVATION FROM FROZEN SOURCE
```

Interface model:

```text
SOURCE
|
| immutable lineage
v
DERIVATION BOUNDARY
|
v
AI DERIVATION
|
v
DERIVED RESULT
```

The source remains visible or immediately reachable as the immutable upstream basis.

The visual relation must mean:

```text
derived from
```

not:

```text
replaced by
```

---

# 26. AI DERIVATION FIELD

AI processing exists only after protected source closure.

## Required conditions

* Burst completed
* Human source membership frozen
* original text invariants preserved
* Session lawfully enters ANALYSIS
* AI invocation permitted by server/application architecture

`BEGIN_ANALYSIS` may be authorized by a human controller or bounded system procedure where the approved method permits it; AI itself may not authorize its own invocation.

## Visible structure

### Source anchor

Frozen human set.

### Derivation relation

The operation applied to the source.

### Analysis status

Distinct from Session state.

### Derived artifacts

Clearly AI-derived.

### Validation/provenance

Accessible without dominating the primary result.

## Invalid architecture

```text
AI result
→ edits Human Source
```

```text
AI result
→ advances Session by itself
```

```text
AI result
→ gains Authority
```

```text
AI result
→ becomes Committed Effect merely because generation completed
```

---

# 27. AI DERIVED RESULT EXPERIENCE

A Result is not a canonical Session state.

It is a visible derived artifact inside a valid analysis relation.

Model:

```text
FROZEN HUMAN SOURCE
→ ANALYSIS OPERATION
→ AI DERIVED RESULT
```

A Result surface must expose:

* AI origin
* source lineage
* analysis status
* derivation provenance
* validation state where applicable
* relevant evidence where applicable

It must not imply:

* Human authorship
* operation authority
* downstream approval
* committed external/system consequence
* a new Session phase unless a canonical transition actually occurred

The Result Field can therefore exist completely even when **no later effect is defined**.

---

# 28. RESULT TO POSSIBLE EFFECT BOUNDARY

The frontend architecture supports this general boundary only as a conditional shape:

```text
AI DERIVED RESULT
→ [POSSIBLE CANDIDATE RELATION]
→ [HUMAN / SYSTEM DECISION RELATION]
→ [AUTHORIZED COMMAND]
→ EFFECT
```

Brackets mean the relation must be independently established.

The architecture currently guarantees only:

```text
AI DERIVED RESULT
!= EFFECT

AI DERIVED RESULT
!= AUTHORITY

CANDIDATE
!= EFFECT
```

No generic approval workflow is introduced.

No automatic AI consequence is introduced.

No control is shown simply because a Result exists.

When no later relation is canonically defined:

```text
RESULT
→ terminal visible derived artifact for the current bounded frontend scope
```

This is structurally complete.

It is not a missing UI action.

---

# 29. NAVIGATION ARCHITECTURE

Navigation follows relationships, not a permanent module tree.

## Global Context Movement

Between accessible NQUIRY contexts such as Workspaces and Challenges.

## Context Establishment Movement

```text
Workspace
→ Governance
→ Challenge
→ Session creation
```

## Session Relational Movement

Movement is constrained by canonical state.

Future states are not arbitrary destinations.

## Proof Movement

Moves vertically into:

* authority
* origin
* evidence
* provenance
* commit
* previous state

Proof movement does not destroy primary position.

## Past

Past relations are reconstructable.

They are not reactivated by navigation.

## Future

Future relations are displayed as possibilities only when system projection supports them.

No sidebar may imply every future state is an independently navigable page.

---

# 30. SPATIAL ARCHITECTURE

Spatial meaning is stable.

## Centre

Current active relation.

## Near field

Immediate lawful affordances and directly relevant boundaries.

## Outer field

Context and already-closed relations.

## Depth

Proof, authority, evidence and provenance.

## Open edge

Possible continuation.

## Closed edge

Committed closure.

## Interrupted edge

Boundary.

## Stable source plane

Human Source after freeze.

## Downstream derivation plane

AI-derived material.

The interface therefore changes not by decorating cards differently but by changing what occupies the spatial centre.

---

# 31. VISUAL SEMIOTIC SYSTEM

The visual system uses a small grammar.

## Containment

Indicates whether a relation is:

* open
* closed
* derived
* interrupted

## Edge treatment

Communicates:

* possible continuation
* committed closure
* boundary
* stale invalidation

## Depth

Communicates proof relation.

## Density

Current active relation gets sufficient information density.

Inactive relations reduce density without disappearing from orientation.

## Alignment

Source and derivation remain aligned by lineage but do not share the same visual substrate.

## Repetition

Repeated visual primitives represent repeated system relations, not generic layout convenience.

No decorative distinction may carry an architectural meaning unless the same meaning is available non-visually.

---

# 32. TYPOGRAPHIC SEMANTICS

Typography has semantic roles.

## Human Source Type

Prioritizes authored content.

Does not resemble machine/system labels.

## System State Type

Compact, structural, environmental.

Never resembles a chat speaker.

## AI Derived Type

Distinct derived hierarchy with explicit origin context.

## Proof Type

Dense but readable; optimized for:

* IDs where needed
* command names
* authority source
* scope
* commit
* timestamps
* evidence provenance

## Boundary Type

Names consequence semantics precisely without theatrical alarm language.

Typography reinforces origin and state but never serves as the sole distinction.

---

# 33. MOTION SEMANTICS

Motion is permitted only to explain relation change.

## Valid uses

* state transition
* source freeze
* committed effect
* reconstruction
* proof drilldown
* stale invalidation
* derivation appearing downstream from source

## Invalid uses

* ambient decorative movement
* pulsing status for aesthetic activity
* gamified timer movement
* animation implying success before commit
* AI “thinking” theatrics unrelated to real analysis status

## Reduced Motion

Every animated semantic event has a static equivalent:

* changed containment
* updated heading/state description
* explicit status
* focus placement
* screen-reader announcement

---

# 34. RESPONSIVE ARCHITECTURE

Responsive transformation preserves relation topology.

## Desktop

Can expose:

```text
orientation
+
active relation
+
limited proof affordance
```

simultaneously.

## Tablet

Reduces lateral concurrency.

Proof and context become more sequential.

## Mobile

Primary order:

```text
POSITION
→ ACTIVE RELATION
→ AVAILABLE ACTION / BOUNDARY
→ SOURCE / DERIVATION
→ PROOF
```

Mobile must not become:

```text
desktop panels
→ vertical generic card stack
```

Human Source and AI Derived retain different structural grammar at every width.

Proof depth becomes a focused layer with deterministic return to previous context.

---

# 35. ACCESSIBILITY ARCHITECTURE

Every semantic distinction survives:

* keyboard-only interaction
* Screen Reader
* reduced motion
* high zoom
* color-vision deficiency
* no hover
* touch
* narrow viewport

## Keyboard

Logical order follows relational order.

Proof opening does not create keyboard traps.

## Screen Reader

Programmatic semantics include:

* current canonical state
* Human Source
* AI Derived
* frozen/open source
* boundary category
* requested/pending/committed
* stale
* indeterminate
* available/unavailable action reason

## High Zoom

Source/derivation lineage remains ordered rather than side-by-side dependent.

## Color Vision

No distinction exists only in hue.

## No Hover / Touch

Reasons and proof are explicit activation targets.

## Spatial alternatives

Any semantic meaning conveyed by position also exists in structure, accessible names or ordered descriptions.

---

# 36. COMPONENT AND SURFACE ARCHITECTURE

Components are compiled from semantic primitives.

## Field Frame

Projects current Parent/Child Field and canonical context.

## Position Trace

Projects relational location.

## Source Surface

Projects Human Source.

## Derived Surface

Projects AI-derived artifacts.

## Affordance Surface

Projects one server-defined actionable relation.

## Effect Intent Surface

Represents REQUESTED/PENDING without state mutation.

## Commit Marker

Represents confirmed canonical consequence.

## Boundary Surface

Represents a typed relation failure/limit.

## Transition Surface

Explains committed old→new relation.

## Proof Surface

Projects authority/evidence/provenance depth.

## Reconstruction Surface

Represents stale invalidation/canonical re-read.

## Frozen Field Surface

Represents a closed source relation.

These are semantic roles.

They do not mandate React components, HTML topology or styling technology.

---

# 37. SERVER PROJECTION TO INTERFACE CONTRACTS

No fake endpoint architecture is defined.

The frontend needs semantic contracts.

## Context Projection

Minimum semantics:

```text
identity context
accessible Workspace context
governance context
Challenge reference
Session reference or explicit absence
canonical Session state when present
state/version context
previous establishing transition reference
```

## Capability Projection

```text
relation
availability
scope
reason
authority source reference where relevant
state/version context
freshness
```

## Command Outcome Projection

```text
request identity
outcome kind
consequence certainty
commit reference if committed
result reference where relevant
canonical post-command projection or re-read relation
```

## Origin Projection

```text
origin class
source identity
source lineage
```

## Provenance Projection

```text
visible state/artifact
establishing command/operation
actor
authority source
scope
commit
evidence refs
previous state
```

## Temporal Projection

Time values require semantic type.

A timestamp without meaning is insufficient.

## Reconstruction Projection

Must let the client determine:

* latest canonical state
* version/freshness
* currently valid capability projection
* committed outcome state

---

# 38. AUTHORITY PROJECTION AND REVALIDATION CONTRACT

The frontend does not need internal authorization algorithms.

It requires their projected result.

## Backend responsibility

```text
evaluate current authority
re-read current authority dependencies
evaluate current canonical state
evaluate current scope
apply operation-specific boundaries
revalidate where consequence semantics require it
record provenance
```

Current architecture already re-reads current membership/role for typed authority cases and requires authority proof before effect-gate ALLOW.

## Frontend responsibility

Consume:

```text
ACTION_AVAILABLE / ACTION_UNAVAILABLE
scope
reason
authority-source reference
canonical state/version context
projection freshness
revalidation result where surfaced
provenance reference
```

## Revalidation rule

An old capability projection is not proof of present authority.

A material Command may still be denied after the interface rendered it if canonical authority changed.

The UI therefore treats capability as:

```text
current server projection
```

not:

```text
permission guarantee
```

## Exact API shape

Not architecturally prescribed.

The semantic contract is binding; endpoint/DTO decomposition may vary.

---

# 39. FAILURE AND VERDICT LANGUAGE

UI language follows consequence semantics.

## DENIED

“This action is not permitted in the current authority and scope.”

## REJECTED

“This request cannot be accepted in its current form.”

## STALE

“The visible state has changed since this action became available.”

## BLOCKED

“This relation cannot continue until the required prerequisite exists.”

## FAILED_PRECOMMIT

“The requested change did not commit.”

## INDETERMINATE

“The system cannot currently determine whether the requested change committed.”

## NOT_FOUND

“The referenced context is not available in the confirmed scope.”

## NETWORK_FAILURE

“The canonical system could not be reached.”

For mutation uncertainty, NETWORK_FAILURE may lead to INDETERMINATE rather than FAILED_PRECOMMIT.

Technical tokens need not always be shown literally.

Their semantics must remain distinct.

---

# 40. PROGRESSIVE DISCLOSURE MODEL

Four semantic depths:

## D0 — ACT

* position
* current relation
* primary source/content
* current affordance

## D1 — UNDERSTAND

* why possible
* why blocked/denied
* origin
* immediate transition meaning

## D2 — VERIFY

* authority source
* scope
* commit
* evidence
* source lineage
* freshness

## D3 — RECONSTRUCT

* command
* actor
* full authority provenance
* previous state
* causal sequence
* reconciliation history where applicable

Proof completeness does not require permanent proof visibility.

---

# 41. REAL STACK ACCEPTANCE MODEL

Real Stack proof requires:

```text
BROWSER
→ REAL API
→ APPLICATION
→ CANONICAL PERSISTENCE
→ CANONICAL RE-READ
→ RECONSTRUCTED INTERFACE
```

Mocks cannot establish Real Stack truth.

## Acceptance lane A — Login

Browser authenticates against real application/runtime.

Resulting context must come from real identity/session state.

## Acceptance lane B — Workspace

Browser discovers or creates a lawful Workspace through actual runtime semantics.

## Acceptance lane C — Governance

Authority-related action/display originates from real server projection.

Role-only frontend inference fails acceptance.

## Acceptance lane D — Challenge

Challenge framing persists and re-reads.

## Acceptance lane E — Session

Browser creates Session from real Challenge.

Canonical re-read establishes `DRAFT`.

Then lawful progression proves:

```text
DRAFT
→ SETUP
→ CHALLENGE_CAPTURE
→ QUESTION_GENERATION
```

## Acceptance lane F — Active Human-Only Burst

At `QUESTION_GENERATION`:

* QuestionBurst is ACTIVE
* authorized participants exist
* AI capture assistance absent

Current F02 proof establishes the required downstream starting condition for F03.

## Acceptance lane G — Human Question Capture

Browser submits exact text.

Proof chain:

```text
browser input
→ real capture API
→ application authority/capture boundary
→ Question persistence
→ canonical re-read
→ exact original_text rendered
```

Assertions:

* HUMAN origin
* no AI contamination
* no optimistic canonical append

## Acceptance lane H — Manual Completion

Browser issues manual authorized completion.

Proof chain:

```text
browser completion intent
→ real Command
→ authority evaluation
→ freeze preconditions
→ commit
→ Burst COMPLETED
→ Session QUESTION_CAPTURE
→ canonical re-read
→ reconstructed closed source field
```

Assertions:

* timer did not cause completion
* exact Question texts unchanged
* capture closed
* source frozen

## Acceptance lane I — Begin Analysis

From canonical `QUESTION_CAPTURE`:

```text
BEGIN_ANALYSIS
→ valid authority/system procedural source
→ commit
→ Session ANALYSIS
→ re-read
→ derivation field opens
```

No direct frontend jump from active capture to AI analysis counts as proof.

## Acceptance lane J — AI Derivation Boundary

Assertions:

* frozen source remains unchanged
* derived content clearly AI-origin
* provider/mock ceiling truthful where applicable
* AI does not establish authority

## Acceptance lane K — Derived Result

Result renders as derived artifact within valid analysis context.

No Result→Effect implication.

## Acceptance lane L — Provenance

From visible state/result, user can reach:

```text
command / operation
actor
authority source
scope
commit
source lineage
previous state
```

## Acceptance lane M — Controlled outcomes

Real Stack tests cover:

* DENIED
* REJECTED
* STALE
* BLOCKED where applicable
* FAILED_PRECOMMIT
* INDETERMINATE
* NOT_FOUND
* NETWORK_FAILURE

---

# 42. FRONTEND TDD / FALSIFIER MODEL

The architecture is falsified if any of the following can occur.

1. `QUESTION_GENERATION` is rendered as pre-capture preparation while the ACTIVE Human-Only Burst is already canonical.
2. Human Question capture is restricted to `QUESTION_CAPTURE`.
3. `QUESTION_CAPTURE` allows new Human Question capture after committed Burst completion.
4. Manual completion visually jumps directly from active Human capture to ANALYSIS without representing the canonical freeze relation.
5. `QUESTION_CAPTURE` is removed from canonical Session topology.
6. RESULT is introduced as an invented Session state.
7. A click changes visible canonical state before commit.
8. A captured Question appears canonical before server confirmation.
9. Frozen `original_text` changes.
10. AI content enters the frozen Human Source set.
11. AI Derived content uses Human Source styling/semantics.
12. AI output unlocks a consequential action without a server-projected relation.
13. Candidate appears committed.
14. Role alone determines action availability.
15. Evidence is presented as operation authority.
16. Timer expiry automatically closes the Burst.
17. Network failure proves “nothing happened.”
18. INDETERMINATE is rendered as FAILED.
19. stale affordance remains consequential.
20. old capability survives state reconstruction without revalidation.
21. DENIED and REJECTED collapse into one generic error.
22. FAILED_PRECOMMIT and INDETERMINATE look equivalent.
23. provenance disappears after responsive transformation.
24. Screen Reader cannot distinguish Human Source from AI Derived.
25. reduced motion removes transition meaning.
26. proof drilldown loses the originating position.
27. canonical re-read differs from visible post-command state.
28. mobile turns Origin classes into identical cards.
29. BEGIN_ANALYSIS is triggered by AI output rather than authorized application/system relation.
30. result availability is presented as committed downstream effect.
31. hidden client logic computes the next Session state.
32. future Session state becomes arbitrary navigation destination.
33. an unavailable AI provider silently advances ANALYSIS.
34. a committed freeze cannot be reconstructed to the completion command.
35. an action availability projection is treated as permanent permission.

---

# 43. ANTI PATTERNS

Explicitly rejected:

```text
generic dashboard
card grid
KPI tiles
admin console
governance wall
everything-is-a-badge
everything-is-a-modal
everything-is-red-on-failure
AI chat everywhere
persistent side panel per concern
client-side authority inference
client-side next-state calculation
optimistic canonical mutation
human/AI mixed content
hidden provenance
invisible boundaries
status text without spatial consequence
decorative motion
color-only semantics
desktop semantics collapsed into mobile cards
timer-driven completion
role-as-permission
evidence-as-authority
candidate-as-effect
result-as-session-state
page-navigation-as-transition
spinner-as-proof-of-commit
```

---

# 44. F11 RELATION

The current frontend execution context establishes F11 as a future full semiotic/frontend system strand whose foundations may be pulled forward into earlier Fields. Current frontend-first planning explicitly keeps F03's signature UI inside F03 while allowing minimal provenance, Human/AI/Authority vocabulary and design tokens to begin earlier; full semiotic closure remains a later F11 concern.

## ESTABLISHED

### F11-R01

F11 is not the owner of F03 semantics.

Protected Human Question UI belongs to the semantic Field that owns those relations.

### F11-R02

F11 may own later full-system semiotic coherence.

### F11-R03

Foundational vocabulary can be materialized earlier and reused.

### F11-R04

F11 cannot create canonical state, authority or effect semantics.

## DERIVABLE

### F11-R05

The Parent Field defined here can remain stable when F11 arrives because it is based on semantic responsibilities rather than current page structure.

### F11-R06

F11 can consume the stable grammar for:

* Origin
* Effect
* Boundary
* Provenance
* Position
* Reconstruction

and extend it to downstream product Fields.

## OPEN

### F11-R07

The exact final closure boundary between current symbiotic frontend architecture and later F11 cross-product implementation remains open.

### F11-R08

The complete downstream set of product relations F11 must visually unify is not required to close the current F02–F04 architecture.

## NOT YET DEFINED

No F11-specific:

* canonical Session state
* authority source
* effect type
* AI permission
* new Origin class

is invented here.

## Attachment to Parent Field

F11 attaches **across** PF-01 as a future semantic-language closure Field.

It does not replace PF-01.

It standardizes and extends its grammar.

## What may proceed without F11 closure

* Parent Field
* Context Establishment
* Position
* current Session topology
* F03
* Human Source freeze
* F04 source/derivation boundary
* effect lifecycle
* authority projection
* boundary taxonomy
* provenance
* responsive semantic rules
* accessibility semantic rules
* Real Stack acceptance

---

# 45. OPEN RELATIONS

## OR-01 — F11 FULL CLOSURE

**Relation:** Current architecture → later full F11 semiotic system.

**Why open:** exact full downstream product scope is not required for F02–F04 closure.

**Authoritative home:** future F11 architecture/execution contract.

**Depends on it:** final cross-product semantic harmonization.

**Does not depend on it:** present Parent Field and F02–F04 experience.

**Closing event:** authoritative F11 scope and acceptance contract.

**Implementation may proceed:** YES.

---

## OR-02 — RESULT → CANDIDATE

**Relation:**

```text
AI DERIVED RESULT
→ CANDIDATE
```

**Why open:** not every derived result is defined as a Candidate.

**Authoritative home:** downstream product/application semantics.

**Depends on it:** candidate-specific affordances.

**Does not depend on it:** Result display and provenance.

**Closing event:** canonical candidate relation definition.

**Implementation may proceed:** YES.

---

## OR-03 — CANDIDATE → DECISION → COMMAND → EFFECT

**Relation:** consequential use of AI-derived or other Candidate output.

**Why open:** no generic future consequence is authorized.

**Authoritative home:** operation-specific downstream Field.

**Depends on it:** later consequential controls.

**Does not depend on it:** F03/F04/Result architecture.

**Closing event:** explicit decision right, authority and Command contract.

**Implementation may proceed:** YES.

---

## OR-04 — ANALYSIS FAILURE / BYPASS PROGRESSION

**Relation:**

```text
ANALYSIS
→ next canonical state when required AI analysis is unavailable
```

**Why open:** current state architecture does not authorize an automatic skip; unavailable AI leaves the Session in ANALYSIS unless later architecture closes the gap.

**Authoritative home:** AI/recovery/state-transition architecture.

**Depends on it:** progression beyond failed/unavailable analysis.

**Does not depend on it:** entry into ANALYSIS or faithful rendering of the failure.

**Closing event:** source-authorized fallback/bypass rule.

**Implementation may proceed:** YES, provided the frontend does not invent progression.

---

## OR-05 — FULL PRODUCTION BURST CONTROL MODEL

**Relation:** prototype manual completion authority → broader production completion semantics.

**Why open:** current prototype narrowing establishes Session-scoped manual completion while broader production semantics remain open.

**Authoritative home:** authority/governance decision architecture.

**Depends on it:** future production completion alternatives.

**Does not depend on it:** prototype F03 manual completion.

**Closing event:** authoritative production Burst-control decision.

**Implementation may proceed:** YES for the current prototype.

---

# 46. CASE-3 BOUNDARIES

Case-3 means the frontend must preserve an unresolved structural branch rather than choose semantics locally.

## C3-01 — MUTATION TRANSPORT LOSS

```text
request sent
→ connection lost
→ commit unknown
```

Resolution:

```text
INDETERMINATE
→ reconcile
```

No blind retry.

---

## C3-02 — PARTIAL SESSION/BURST BUNDLE CERTAINTY

Opening question generation couples Session and QuestionBurst state.

If the system cannot prove both committed consistently:

```text
INDETERMINATE
```

The frontend must not display a coherent active Burst from a partial pair. The canonical transition architecture explicitly treats partial bundle certainty as invalid.

---

## C3-03 — PAUSE / RESUME

If future F03 surfaces PAUSE/RESUME while its authority/interaction semantics remain unresolved:

* do not invent controls
* do not model pause as a local timer feature
* leave relation absent until canonical contract exists

---

## C3-04 — TIMER COMPLETION

Earlier architectural paths allowed a possible system timer authority, but the current prototype decision establishes manual authorized completion and presentation-only timer behaviour. Any future reintroduction of system-triggering completion is a new authoritative relation, not a frontend switch.

---

## C3-05 — ANALYSIS UNAVAILABLE

When the Session is `ANALYSIS` and required AI analysis cannot complete:

* remain in ANALYSIS unless a canonical recovery transition exists
* show provider/analysis boundary
* preserve frozen source
* do not move to Reflection

---

## C3-06 — COMMITTED EFFECT / RECONSTRUCTION UNAVAILABLE

If commit is known but fresh projection acquisition fails:

* do not revert visually to “unchanged”
* do not fabricate new detailed state
* represent committed consequence plus reconstruction boundary
* re-read before enabling dependent actions

---

# 47. IMPLEMENTATION DEPENDENCIES

The architecture depends on semantic availability of:

1. canonical context projection
2. canonical Session state
3. state/version or equivalent freshness identity
4. server capability projection
5. typed outcome projection
6. authority evaluation at backend
7. authority source provenance
8. scope
9. command/effect identity
10. commit identity
11. canonical re-read
12. QuestionBurst state
13. participant/capture authority projection
14. exact `original_text`
15. frozen raw-set identity
16. Human origin
17. AI-derived origin
18. derivation provenance
19. analysis validation/status
20. evidence reference/freshness where relevant
21. reconstruction path
22. INDETERMINATE reconciliation semantics

No dependency requires the frontend to implement business rules.

---

# 48. FRONTEND FIELD IMPLEMENTATION ORDER

## Stage 1 — Parent and Position

Compile:

```text
PF-01
CF-01
CF-02
```

Prove pre-Session context works without Session assumptions.

## Stage 2 — Canonical Session Projection

Compile:

```text
CF-03
```

Support:

```text
DRAFT
SETUP
CHALLENGE_CAPTURE
QUESTION_GENERATION
QUESTION_CAPTURE
ANALYSIS
```

as canonical states relevant to current bounded path.

## Stage 3 — Authority / Affordance / Boundary

Compile:

```text
CF-07
CF-08
```

No client authority.

## Stage 4 — Protected Human Source

Compile:

```text
CF-04
```

inside `QUESTION_GENERATION`.

## Stage 5 — Completion / Freeze

Materialize:

```text
CLOSE_QUESTION_GENERATION
→ QUESTION_CAPTURE
```

Do not collapse BEGIN_ANALYSIS into the same frontend assumption.

## Stage 6 — Reconstruction

Complete canonical re-read after all material effects.

## Stage 7 — Analysis Entry

Materialize:

```text
QUESTION_CAPTURE
→ BEGIN_ANALYSIS
→ ANALYSIS
```

## Stage 8 — AI Derivation

Compile CF-05.

## Stage 9 — Result Projection

Compile CF-06 without later-effect assumptions.

## Stage 10 — Proof

Compile CF-09.

## Stage 11 — Responsive + Accessibility Closure

Falsify semantic preservation across devices and assistive modes.

## Stage 12 — Real Stack Acceptance

Run complete real runtime causal chain.

## Stage 13 — F11 Harmonization

Later F11 may extend and close cross-product semiotics without rewriting these canonical relations.

---

# 49. INVERSE VALIDATION RESULT

## Position

```text
VISIBLE POSITION
→ context projection
→ Workspace/Challenge/Session refs
→ canonical state
→ establishing transition
```

VALID.

## Current State

```text
VISIBLE STATE
→ Session projection
→ canonical Session
```

VALID.

## Human Source

```text
VISIBLE QUESTION
→ Question record
→ capture command
→ human actor
→ Burst membership
```

VALID.

## AI Derived

```text
VISIBLE RESULT
→ derived artifact
→ analysis operation
→ frozen source lineage
```

VALID.

## Available Action

```text
VISIBLE AFFORDANCE
→ capability projection
→ backend authority evaluation
→ canonical context
```

VALID.

## Unavailable Action

```text
VISIBLE NON-AFFORDANCE / BOUNDARY
→ projection reason
→ authority/state/prerequisite result
```

VALID.

## Boundary

```text
VISIBLE BOUNDARY
→ typed outcome
→ application relation
```

VALID.

## Committed Effect

```text
VISIBLE CHANGE
→ commit
→ command
→ canonical persistence
→ re-read
```

VALID.

## Freeze

```text
FROZEN SOURCE
→ CLOSE_QUESTION_GENERATION commit
→ Burst COMPLETED
→ Session QUESTION_CAPTURE
→ frozen membership
```

VALID.

## Provenance

```text
VISIBLE CLAIM
→ audit/provenance projection
→ canonical cause
```

VALID subject to available historical provenance ceilings.

## Authority

```text
VISIBLE AUTHORITY EXPLANATION
→ server projection/provenance
→ backend evaluation
```

VALID.

## Evidence

```text
VISIBLE EVIDENCE
→ evidence reference/version/provenance
```

VALID.

## Result

```text
VISIBLE RESULT
→ derived artifact
→ analysis provenance
```

VALID.

Result → Effect is explicitly not inferred.

## Indeterminate Effect

```text
VISIBLE UNCERTAINTY
→ unresolved commit certainty
→ reconciliation path
```

VALID.

## Reconstruction

```text
RECONSTRUCTED FIELD
→ canonical re-read
```

VALID.

---

# 50. RECURSIVE DEEPSWEEP RESULT

The architecture has been checked recursively across:

```text
Parent Field
Child Fields
State
Transition
Boundary
Authority
Origin
Effect
Provenance
Temporality
Evidence
Persistence
Server Projection
Frontend
Accessibility
Responsive
Tests
Real Stack
F03
F04
F11
```

## Parent ↔ Child

PASS.

Parent exists before Session; Session Field begins only after Session creation.

## State ↔ Transition

PASS.

Human capture occurs in QUESTION_GENERATION.

Freeze establishes QUESTION_CAPTURE.

BEGIN_ANALYSIS establishes ANALYSIS.

## State ↔ Result

PASS.

Result is not promoted to Session state.

## Affordance ↔ Authority

PASS.

Frontend projection only.

## Boundary ↔ Outcome

PASS.

Distinct taxonomy preserved.

## Origin ↔ Source

PASS.

Human and AI remain structurally distinct.

## Effect ↔ Commit

PASS.

Requested/Pending cannot masquerade as Committed.

## Provenance ↔ Reconstruction

PASS.

Visible material effects require backward trace.

## Temporality ↔ Authority

PASS.

Presentation timer has no completion authority.

## Evidence ↔ Authority

PASS.

Independent dimensions.

## Responsive ↔ Semantics

PASS.

Semantics transform sequentially rather than collapse into cards.

## Accessibility ↔ Semantics

PASS.

All required distinctions have non-visual equivalents.

## F03 ↔ canonical states

PASS.

## F04 ↔ frozen source

PASS.

## F11 ↔ current Parent Field

PASS with explicit open downstream closure.

---

# 51. ARCHITECTURE COMPLETENESS CHECK

### Can the complete frontend path exist before a Session exists?

YES.

PF-01 and CF-02 explicitly model Session absence.

### Does the Parent Field legitimately contain LOGIN through derived Result?

YES.

It owns no Session-state assumption.

### Are canonical states correctly named?

YES for the bounded path:

```text
DRAFT
SETUP
CHALLENGE_CAPTURE
QUESTION_GENERATION
QUESTION_CAPTURE
ANALYSIS
```

### Is ACTIVE HUMAN_ONLY attached to the correct canonical state?

YES.

`QUESTION_GENERATION`.

### Is Human Question Capture attached to the correct canonical state?

YES.

`QUESTION_GENERATION`.

### Is manual completion attached to the correct transition?

YES.

`CLOSE_QUESTION_GENERATION`.

### Which Session state follows committed manual completion?

`QUESTION_CAPTURE`.

### Is QUESTION_CAPTURE canonical?

YES.

It is the capture-finalized, frozen-source Session state.

### Does ANALYSIS require a distinct transition?

YES.

`BEGIN_ANALYSIS`.

### Does Freeze change source status without changing source content?

YES.

### Can Human Source be confused with AI Derived?

No under the Origin grammar.

### Can AI Derived gain implicit Authority?

No.

### Can Result look like Effect?

No.

### Can Result exist without later Effect?

YES.

### Can Candidate look committed?

No.

### Can Role masquerade as Authority?

No.

### Can Evidence masquerade as Authority?

No.

### Can client state masquerade as canonical?

No.

### Can Requested look Committed?

No.

### Can Network Failure prove no Effect?

No.

### Can INDETERMINATE remain unresolved without fabricated certainty?

YES.

### Can every visible newly committed state be reconstructed backward?

Required by architecture.

### Do state changes force Interface Reconstruction?

YES.

### Does Mobile preserve semantics?

YES.

### Does Screen Reader preserve Origin, Effect and Boundary semantics?

YES.

### Does Reduced Motion preserve transitions?

YES.

### Can complete Proof remain non-dominant?

YES through depth-based disclosure.

### Can F11 remain open without destabilizing the Parent architecture?

YES.

### Can frontend Authority remain understandable while evaluation stays backend-owned?

YES.

### Does the architecture remain non-dashboard?

YES.

The active canonical relation determines the space.

---

# 52. RESULTING FRONTEND MODEL

The final frontend model is:

```text
NQUIRY RELATIONAL INTERACTION FIELD
│
├── POSITION & ORIENTATION
│
├── CONTEXT ESTABLISHMENT
│   │
│   ├── LOGIN
│   ├── WORKSPACE
│   ├── GOVERNANCE
│   ├── CHALLENGE
│   └── CREATE SESSION
│
└── RELATIONAL SESSION FIELD
    │
    ├── DRAFT
    │   ↓
    ├── SETUP
    │   ↓
    ├── CHALLENGE_CAPTURE
    │   ↓
    ├── QUESTION_GENERATION
    │   │
    │   ├── QuestionBurst ACTIVE HUMAN_ONLY
    │   ├── Human Question Capture
    │   ├── HUMAN SOURCE
    │   └── Manual Completion
    │
    ├── CLOSE_QUESTION_GENERATION
    │   ↓
    ├── QUESTION_CAPTURE
    │   │
    │   ├── QuestionBurst COMPLETED
    │   ├── Frozen Human Question Set
    │   ├── Capture Closed
    │   └── HUMAN SOURCE immutable
    │
    ├── BEGIN_ANALYSIS
    │   ↓
    └── ANALYSIS
        │
        ├── Frozen Human Source
        │   ↓
        ├── Derivation Boundary
        │   ↓
        ├── AI DERIVED
        │   ↓
        └── Derived Result
```

Cross-cutting:

```text
AUTHORITY
→ server evaluated
→ frontend projected

EFFECT
→ Possible
→ Requested
→ Pending
→ Committed
→ Reconstruction

BOUNDARY
→ typed
→ non-collapsing

PROVENANCE
→ always reachable

EVIDENCE
!= Authority

RESULT
!= Effect

CANDIDATE
!= Effect

AI
!= Authority
```

The resulting interface does not place a human in front of system telemetry.

It places the human inside a canonically reconstructed relational field.

The field itself communicates:

```text
where the human is
what is true
what is source
what is derived
what is possible
what is closed
what is blocked
what was requested
what committed
what remains uncertain
what established the visible state
```

without requiring those meanings to be permanently rendered as administrative metadata.

---

# OPEN RELATION REGISTER SUMMARY

| ID    | Relation                                | Implementation may proceed |
| ----- | --------------------------------------- | -------------------------: |
| OR-01 | F11 full semiotic closure               |                        YES |
| OR-02 | AI Derived Result → Candidate           |                        YES |
| OR-03 | Candidate → Decision → Command → Effect |                        YES |
| OR-04 | AI-unavailable ANALYSIS progression     |           YES, fail closed |
| OR-05 | broader production Burst-control model  |          YES for prototype |

# CASE-3 BOUNDARY REGISTER SUMMARY

| ID    | Boundary                                         |
| ----- | ------------------------------------------------ |
| C3-01 | mutation transport loss / unknown commit         |
| C3-02 | partial Session/Burst bundle certainty           |
| C3-03 | PAUSE/RESUME without closed semantics            |
| C3-04 | future timer-triggered completion semantics      |
| C3-05 | required analysis unavailable                    |
| C3-06 | committed effect with unavailable reconstruction |

---

SYMBIOTIC FRONTEND ARCHITECTURE STATUS:

STRUCTURALLY_COMPLETE_WITH_OPEN_RELATIONS

CANONICAL STATE ALIGNMENT: PASS

PARENT FIELD ALIGNMENT: PASS

HUMAN SOURCE / AI ORIGIN SEPARATION: PASS

AUTHORITY SEPARATION: PASS

EFFECT / CANDIDATE SEPARATION: PASS

BOUNDARY TAXONOMY: PASS

PROVENANCE RECONSTRUCTION: PASS

RESPONSIVE SEMANTIC PRESERVATION: PASS

ACCESSIBILITY SEMANTIC PRESERVATION: PASS

REAL STACK ACCEPTANCE ARCHITECTURE: PASS

F11 STATUS: OPEN DOWNSTREAM CLOSURE; CURRENT ARCHITECTURE INDEPENDENTLY VALID

RESULT → EFFECT STATUS: OPEN; NO EFFECT IMPLIED

AUTHORITY REVALIDATION STATUS: SEMANTIC CONTRACT CLOSED; BACKEND-OWNED EVALUATION; PHYSICAL API SHAPE NOT PRESCRIBED

OPEN RELATIONS COUNT: 5

CASE-3 BOUNDARIES COUNT: 6
