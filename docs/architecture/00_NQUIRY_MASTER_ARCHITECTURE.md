# 00_NQUIRY_MASTER_ARCHITECTURE

**Project:** N.Q.U.I.R.Y.  
**Subtitle:** Questions Are the Answer-System  
**Document role:** Authoritative system-level architecture map  
**Architecture stage:** A, Master Architecture  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 01 not yet authorized

---

## 0. Document Authority

This file is the authoritative system-level map for the N.Q.U.I.R.Y. architecture.

It does not duplicate the detailed contracts that belong to downstream architecture modules. It establishes the system identity, source hierarchy, architectural invariants, major structural relations, module authority boundaries, unresolved source conflicts, open decisions, dependency order, completion criteria and baseline freeze gate.

Where a downstream module requires detail, this file points to the authoritative home of that detail instead of redefining it.

No downstream architecture file may silently contradict this file. If a downstream discovery falsifies an upstream assumption contained here, architecture construction stops at the contradiction, the authoritative upstream structure is reconstructed, dependent modules are propagated, and the affected path is validated again.

---

# 1. System Identity and Purpose

## 1.1 Product identity

**[SPECIFIED]**

N.Q.U.I.R.Y. is an AI-augmented inquiry system for leadership, decision-making, innovation and complex problem solving.

Its primary product behavior is not answer generation.

Its purpose is to help individuals and teams improve the quality of inquiry around complex, ambiguous or consequential challenges by discovering better questions, challenging assumptions, generating alternative perspectives, connecting inquiry to evidence, and moving inquiry toward action.

The central product hypothesis is:

> A better question can change the problem, which can change the available options, which can change the decision and ultimately the outcome.

The question is therefore a first-class product object.

## 1.2 Canonical product progression

**[SPECIFIED]**

```text
Problem
→ Questions
→ Perspectives
→ Assumptions
→ Insights
→ Evidence
→ Experiments
→ Learning
→ Action
```

The progression must remain visible as inquiry evolves.

N.Q.U.I.R.Y. must not collapse by default into:

```text
Problem
→ AI Answer
```

before the problem frame has been examined.

## 1.3 Iterative inquiry

**[SPECIFIED]**

Inquiry is iterative.

A question may produce another question.

The source therefore establishes graph-like inquiry relations rather than a purely linear chat history.

The exact implementation scope of the dedicated Inquiry Graph remains unresolved because LEVEL 1 contains conflicting MVP/V2/engineering-scope statements. See `CONFLICT-001`.

---

# 2. Architecture Objective

The architecture exists to transform the authoritative product specification into a system that can be implemented without requiring the implementation layer to invent consequential behavior.

The target path is:

```text
LEVEL 1 PRODUCT SPECIFICATION
→ SYSTEM ARCHITECTURE
→ ARCHITECTURAL CLOSURE
→ MINIMUM CLOSED PROTOTYPE
→ IMPLEMENTATION CONTRACTS
→ TESTABLE BUILD SEQUENCE
→ IMPLEMENTATION
→ RECURSIVE BUILD VALIDATION
→ RUNNING MINIMUM CLOSED PROTOTYPE
```

Architecture determines implementation.

Implementation may materialize architecture.

Implementation may not invent:

- domain objects with consequential semantics;
- canonical state semantics;
- states;
- state transitions;
- decision authority;
- governance bypasses;
- boundary exceptions;
- AI authority;
- provenance semantics;
- failure semantics;
- recovery semantics.

If implementation exposes an architectural contradiction, implementation stops and the contradiction returns to its authoritative architecture layer.

---

# 3. Source Hierarchy

## 3.1 LEVEL 1

**Authoritative source:**

```text
N.Q.U.I.R.Y.: Product & System Specification
```

The DOCX and Markdown files are two representations of the same LEVEL 1 specification.

LEVEL 1 is authoritative for:

- product intent;
- terminology;
- product principles;
- methodology as specified in the product source;
- requirements;
- core domain concepts;
- user journey;
- workflow;
- NFRs;
- security and privacy requirements;
- AI participation rules;
- roadmap;
- MVP scope;
- acceptance criteria;
- open decisions;
- engineering starting point.

LEVEL 1 terminology is preserved unless a human-authorized architecture decision explicitly changes it.

## 3.2 LEVEL 2

**Architectural reconstruction input:**

```text
# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md
```

LEVEL 2 provides:

- system reconstruction;
- capability reconstruction;
- gap analysis;
- authority reconstruction;
- governance reconstruction;
- boundary reconstruction;
- transition reconstruction;
- evidence and provenance reconstruction;
- failure reconstruction;
- inverse reconstruction;
- minimum prototype reconstruction;
- implementation architecture proposals;
- build sequence proposals;
- test architecture proposals.

LEVEL 2 does not override LEVEL 1.

A LEVEL 2 statement remains `[SWEEP-DERIVED]`, `[RECOMMENDED]`, `[MISSING]` or `[UNDERDEFINED]` unless LEVEL 1 independently supports it or a later human-authorized architectural closure accepts it.

## 3.3 LEVEL 3

**[ARCHITECTURAL CLOSURE]**

LEVEL 3 contains new architectural mechanisms introduced only when a demonstrated structural gap cannot be closed by direct LEVEL 1 specification.

Every LEVEL 3 mechanism must trace to one or more of:

```text
LEVEL 1 requirement
LEVEL 1 invariant
LEVEL 1 acceptance criterion
LEVEL 1 NFR
LEVEL 1 open decision after human resolution
LEVEL 2 demonstrated structural gap
```

A mechanism must not be introduced merely because it is common software practice.

---

# 4. Architecture Status Semantics

The architecture uses the following status vocabulary.

| Status | Meaning |
|---|---|
| `[SPECIFIED]` | Explicitly present in LEVEL 1. |
| `[IMPLIED]` | Structurally implied by LEVEL 1, without a complete mechanism. |
| `[SWEEP-DERIVED]` | Introduced or reconstructed by LEVEL 2. |
| `[ARCHITECTURAL CLOSURE]` | New mechanism accepted because a demonstrated gap requires it. |
| `[OPEN]` | Unresolved and requires later architectural or human decision. |
| `[DEFERRED]` | Explicitly postponed beyond the current architecture/prototype scope. |
| `[UNKNOWN]` | Cannot be determined from supplied authoritative material. |

Status conversion is never silent.

`[OPEN]` remains open until resolved.

`[UNKNOWN]` remains unknown until authoritative evidence exists.

---

# 5. Source Traceability Model

Every consequential architectural mechanism must be traceable through the following path where applicable:

```text
SOURCE
→ REQUIREMENT / CLAIM
→ CAPABILITY
→ ARCHITECTURAL MECHANISM
→ AUTHORITATIVE MODULE
→ COMPONENT
→ STATE / TRANSITION
→ AUTHORITY
→ BOUNDARY
→ PERSISTENCE / AUDIT
→ FAILURE / RECOVERY
→ TEST
```

Stable IDs may be introduced where they improve cross-module traceability.

Permitted ID families include:

```text
REQ
CAP
OBJ
REL
STATE
TRN
AUTH
GOV
BND
EVD
AI
FAIL
API
EVT
TEST
DEC
BUILD
CONFLICT
GAP
```

IDs are not used as bureaucratic decoration. They exist only where they support reconstruction across files.

---

# 6. System Boundary

## 6.1 Product system boundary

**[SPECIFIED]**

The N.Q.U.I.R.Y. product boundary includes the capabilities and information structures required to support inquiry from challenge capture through question development, reflection, evidence connection, experimentation, action and learning.

At system level this includes:

```text
User / participant context
Workspace
Challenge
Inquiry session
Question creation and preservation
Question Burst
Question analysis
Question classification and clustering
Reframing
Assumption detection
Reflection
Question selection
Impact inquiry
Evidence connection
Experiment concepts
Decision concepts
Inquiry history
Inquiry methods
AI orchestration
Human / AI provenance distinction
Auditability
Export
Security
Privacy
Observability
Cost telemetry
```

Not every product capability belongs to the Minimum Closed Prototype.

Prototype inclusion is authoritative in `12_MINIMUM_PROTOTYPE_ARCHITECTURE.md` after the LEVEL 1 scope conflict around the Inquiry Graph is resolved.

## 6.2 External systems and unresolved providers

The following are not yet defined as owned internal implementation components:

```text
LLM provider infrastructure
external research providers
enterprise identity provider
external collaboration platforms
deployment platform
external organizational data sources
```

Interfaces to these systems may later fall inside N.Q.U.I.R.Y. architecture.

Provider-specific behavior does not become canonical product semantics.

## 6.3 Prototype boundary anchor

**[SPECIFIED]**

LEVEL 1 MVP explicitly requires at least:

```text
User authentication
Workspace
Challenge creation
Question creation
Question Burst
Four-minute timer
Verbatim question capture
Question clustering
AI question analysis
Assumption detection
Question selection
Reflection
Impact / five-why chain
Basic inquiry history
Export
Audit trail
Human vs AI provenance
```

`Authentication` therefore belongs to the source-defined prototype boundary and cannot be omitted by the LEVEL 2 prototype reconstruction.

The dedicated Inquiry Graph remains subject to `CONFLICT-001`.

---

# 7. Architecture Principles

## 7.1 Questions before answers

**[SPECIFIED]**

Inquiry precedes premature solution generation.

## 7.2 Challenge the frame

**[SPECIFIED]**

The system actively tests whether the initial framing restricts the solution space.

## 7.3 Preserve user thinking

**[SPECIFIED]**

AI suggestions must never silently replace the user's original questions.

`Question.original_text` must never be overwritten.

## 7.4 Make assumptions visible

**[SPECIFIED]**

Assumptions embedded in questions and problem statements must be surfaceable as explicit inquiry artifacts.

## 7.5 Evidence over confidence

**[SPECIFIED]**

AI-generated suggestions are hypotheses, not facts.

AI confidence is not evidence.

## 7.6 Human agency

**[SPECIFIED]**

Humans remain responsible for:

- decisions;
- interpretation;
- experiments;
- actions;
- ethical judgments.

The exact operation-level authority matrix is not fully specified in LEVEL 1 and belongs to `04_AUTHORITY_AND_DECISION_RIGHTS.md`.

## 7.7 Inquiry is iterative

**[SPECIFIED]**

The inquiry model supports recursive question generation and relations between inquiry artifacts.

## 7.8 Question Burst integrity

**[SPECIFIED]**

During the protected human Question Burst:

```text
questions only
no discussion
no answers
no explanations
verbatim capture
AI analysis disabled until burst completion
```

AI participation inside a burst may only occur in a distinct mode explicitly defined for that purpose.

The LEVEL 2 phrase `text is question-like or allowed raw` is not authoritative for the protected Question Burst and is rejected by source precedence. See `CONFLICT-002`.

## 7.9 Human decision authority

**[ARCHITECTURAL CLOSURE]**

Trace:

```text
LEVEL 1 P9 Human agency
+
current architecture build mandate
```

Where a decision transition is assigned to a human role, the human is not modeled as a generic approval token.

The human decision is an authority-bearing system fact.

For any transition requiring human decision authority:

```text
AI proposal
≠
human decision
```

and:

```text
AI confidence
≠
decision authority
```

The transition cannot become valid until the required authorized human decision exists.

This principle does not create new human-only decisions by itself. Operation-level human authority must trace to LEVEL 1 or to a demonstrated and explicitly accepted closure requirement.

## 7.10 Governance before consequence

**[ARCHITECTURAL CLOSURE]**

Trace:

```text
LEVEL 1 state, authorization, audit and provenance requirements
+
LEVEL 2 demonstrated enforcement gaps
+
build closure invariant
```

Consequential transitions must be governed before execution, not merely documented after execution.

Detailed enforcement belongs to modules 03 through 06.

## 7.11 One authoritative home

**[ARCHITECTURAL CLOSURE]**

Every architectural fact has one authoritative module.

Other modules reference that fact.

They do not independently redefine it.

---

# 8. High-Level Domain Map

## 8.1 LEVEL 1 first-class product objects

**[SPECIFIED]**

LEVEL 1 explicitly defines these first-class objects:

```text
User
Workspace
Challenge
Question
Insight
Assumption
Evidence
Experiment
Decision
Journey
```

`Question` is the central product object.

## 8.2 LEVEL 1 persistence and system objects

**[SPECIFIED]**

The LEVEL 1 data architecture additionally names:

```text
WorkspaceMember / workspace_members
QuestionCluster / question_clusters
Session / sessions
SessionParticipant / session_participants
AIGeneration / ai_generations
AuditEvent / audit_events
```

These names establish source support for persistence-level system concepts.

Their exact canonical schemas and ownership are not defined here.

## 8.3 Workflow concepts requiring domain closure

The source defines the behavior of:

```text
Question Burst
Five-Why Impact Chain
Inquiry Method
Inquiry Graph
```

without fully settling all of them as canonical domain objects.

Their object status, identity, ownership and persistence semantics belong to:

```text
02_DOMAIN_AND_RELATION_MODEL.md
```

Any new canonical object required there must be marked `[ARCHITECTURAL CLOSURE]` unless LEVEL 1 already defines it.

## 8.4 Canonical versus derived state

**[SPECIFIED + UNDERDEFINED]**

LEVEL 1 requires human-authored questions to remain distinguishable from AI-generated and inferred material.

It explicitly distinguishes question/source categories and requires AI-generated content to remain distinguishable from human-generated content.

The complete canonical-versus-derived state model is not yet closed.

Authoritative home:

```text
02_DOMAIN_AND_RELATION_MODEL.md
07_EVIDENCE_AND_PROVENANCE.md
09_DATA_EVENT_API_CONTRACTS.md
```

Each file owns only its assigned dimension.

---

# 9. High-Level Relation Map

This map expresses system-level relations only.

Detailed cardinality, ownership, referential integrity and edge semantics belong to `02_DOMAIN_AND_RELATION_MODEL.md`.

```text
User
  ↓ membership / participation

Workspace
  ↓ contains

Challenge
  ↓ explored through

Session
  ↓ contains protected inquiry phases

Question Burst
  ↓ captures

Human Questions
  ↓ preserved verbatim
  ↓ may later be analyzed

AI Analysis
  ↓ produces derived classifications / clusters / reframes / assumptions / prompts

Human Reflection
  ↓ informs

Human Question Selection
  ↓ selects consequential inquiry direction

Selected Question
  ↓ drives

Impact Inquiry
  ↓ may connect onward to

Assumptions
Evidence
Insights
Experiments
Decisions
Actions
Learning
New Questions
```

Cross-cutting relations:

```text
AI operations
→ pass through AI architecture boundary

Consequential state changes
→ require authority and transition eligibility

Derived artifacts
→ require provenance appropriate to their source semantics

Changes requiring traceability
→ produce audit evidence

Export
→ reconstructs permitted system state and history
```

No relation in this map grants transition authority by itself.

---

# 10. High-Level State Lifecycle

## 10.1 Session lifecycle

**[SPECIFIED]**

LEVEL 1 defines the following session state names:

```text
DRAFT
→ SETUP
→ CHALLENGE_CAPTURE
→ QUESTION_GENERATION
→ QUESTION_CAPTURE
→ ANALYSIS
→ REFLECTION
→ QUESTION_SELECTION
→ INVESTIGATION
→ EXPERIMENT
→ ACTION
→ REVIEW
→ CLOSED
```

LEVEL 1 also states that users must not accidentally skip critical phases unless the product explicitly permits it.

## 10.2 Transition closure status

**[UNDERDEFINED]**

LEVEL 1 specifies state names and some workflow constraints.

It does not completely define executable transition eligibility for every consequential transition.

The authoritative transition model belongs to:

```text
03_STATE_AND_TRANSITION_ARCHITECTURE.md
```

## 10.3 Consequential transition invariant

**[ARCHITECTURAL CLOSURE]**

Every consequential transition must ultimately be reconstructable as:

```text
CURRENT STATE
+
REQUESTED TRANSITION
+
ACTOR
+
AUTHORITY
+
PRECONDITIONS
+
REQUIRED EVIDENCE
+
BOUNDARY CHECK
+
ALLOWED ACTION
+
DENIED ACTION
+
NEXT STATE
+
PERSISTENCE
+
AUDIT
+
FAILURE BEHAVIOR
+
RECOVERY / ROLLBACK
+
TEST
```

This file establishes the invariant.

Module 03 owns the transition definitions.

Modules 04 through 13 close and test the dependent dimensions.

---

# 11. High-Level Authority Model

## 11.1 Source-defined roles

**[SPECIFIED]**

LEVEL 1 names:

```text
Owner
Facilitator
Contributor
Observer
Viewer
```

LEVEL 1 explicitly defines some Question Burst permissions:

- participants submit questions;
- participants cannot edit others' questions;
- facilitator can pause or end the burst;
- AI analysis remains disabled until the burst is completed.

## 11.2 Authority gap

**[UNDERDEFINED]**

LEVEL 1 does not provide a complete operation-by-role authority matrix.

The LEVEL 2 prototype authority matrix therefore cannot be treated as `[SPECIFIED]`.

It remains a `[SWEEP-DERIVED]` candidate input for:

```text
04_AUTHORITY_AND_DECISION_RIGHTS.md
```

## 11.3 Authority model invariant

**[ARCHITECTURAL CLOSURE]**

A consequential action is not authorized merely because:

- the UI exposes a control;
- an AI recommends it;
- an actor is generally authenticated;
- an actor has a broad role name;
- a prompt says it is allowed.

Authority must resolve at the relevant operation and state boundary.

---

# 12. High-Level Governance Model

Governance in N.Q.U.I.R.Y. exists at the points where system consequences can occur.

At master level, governance includes:

```text
identity and authentication
workspace isolation
operation authority
state-transition eligibility
Question Burst integrity
human / AI separation
AI context control
provenance preservation
auditability
export control
failure containment
recovery integrity
```

The source provides requirements for several of these controls but does not fully define their executable mechanisms.

The detailed governance mechanisms belong to:

```text
05_GOVERNANCE_INSIDE_SYSTEM.md
```

Governance must not be reduced to:

```text
documentation only
policy prose only
UI warnings only
prompt instructions only
AI confidence
generic human review
```

where a consequential transition requires enforceable control.

---

# 13. High-Level Boundary Model

The architecture must ultimately resolve these boundary classes where relevant:

```text
Identity Boundary
Workspace Boundary
Authority Boundary
State Transition Boundary
Question Burst Boundary
Human / AI Boundary
AI Context Boundary
Model Provider Boundary
Evidence Boundary
Provenance Boundary
Decision Boundary
Export Boundary
Audit Boundary
Failure Boundary
Recovery / Rollback Boundary
```

The authoritative contract for each boundary belongs to:

```text
06_BOUNDARY_ARCHITECTURE.md
```

At minimum, each consequential boundary will later determine:

```text
INPUT
CONDITION
AUTHORITY
VALIDATION
ALLOW
DENY
REQUIRE
ESCALATE
AUDIT
FAILURE
```

This structure is an `[ARCHITECTURAL CLOSURE]` derived from the build closure invariant and the LEVEL 2 boundary-gap reconstruction.

---

# 14. Evidence and Provenance Role

## 14.1 Evidence principle

**[SPECIFIED]**

Evidence is distinct from AI confidence.

AI-generated suggestions and interpretations are hypotheses, not facts.

## 14.2 Human / AI distinction

**[SPECIFIED]**

LEVEL 1 requires the system to distinguish human-generated and AI-generated content.

It also distinguishes source categories including:

```text
human
ai
imported
inferred
```

and requires additional provenance information for inferred objects.

## 14.3 Provenance closure gap

**[UNDERDEFINED]**

LEVEL 1 does not establish the complete mandatory provenance field set for every derived object.

The LEVEL 2 rule making `source`, `source_nodes` and `generation_id` mandatory for every derived object exceeds direct LEVEL 1 wording.

That rule is therefore not `[SPECIFIED]`.

It remains a closure candidate for:

```text
07_EVIDENCE_AND_PROVENANCE.md
09_DATA_EVENT_API_CONTRACTS.md
```

and must be justified field by field against reconstructability, AI/human distinction, audit and failure requirements.

See `CONFLICT-005`.

---

# 15. AI Role and Prohibition Boundary

## 15.1 Permitted source-level AI role

**[SPECIFIED]**

LEVEL 1 permits AI to support inquiry through operations including:

```text
question generation outside protected human-only burst conditions
question classification
question clustering
reframing
assumption detection
perspective generation
insight synthesis
experiment design
reflection prompting
conversation analysis
research support where enabled
```

Specific operation contracts remain downstream work.

## 15.2 AI Gateway

**[SPECIFIED]**

LEVEL 1 states that all LLM traffic should pass through an internal AI Gateway abstraction containing:

```text
AI Gateway
→ Policy Engine
→ Prompt Builder
→ Model Router
→ LLM Provider
→ Response Validator
```

The exact runtime enforcement contract belongs to:

```text
08_AI_ARCHITECTURE_AND_CONTRACTS.md
```

## 15.3 AI prohibitions

**[SPECIFIED + ARCHITECTURAL CLOSURE]**

The system must preserve these source-level prohibitions:

```text
AI must not silently replace original human questions.
AI must not silently attribute AI-generated questions to humans.
AI must not contaminate the protected raw human Question Burst.
AI interpretations must not be presented as facts.
AI analysis must remain disabled until protected Question Burst completion.
```

Additional authority prohibition:

**[ARCHITECTURAL CLOSURE]**

```text
AI recommendation
≠ human decision
AI confidence
≠ authority
AI derived state
≠ automatic human-authorized canonical decision
```

No AI component receives decision authority merely because it can generate a recommendation.

---

# 16. Human Decision Authority Principle

This architecture distinguishes human presence from human authority.

**[SPECIFIED]**

LEVEL 1 assigns responsibility for decisions, interpretation, experiments, actions and ethical judgments to humans.

**[ARCHITECTURAL CLOSURE]**

When a downstream transition requires one of those human decisions as an authority-bearing prerequisite, the system must represent enough information to establish:

```text
which human role may decide
what decision was made
which object the decision concerns
which state the object was in
which evidence or inputs were available where required
when the decision occurred
what transition the decision authorizes
how the decision is audited
```

The exact decision record and authority semantics belong to modules 04, 07 and 09 according to their authority boundaries.

No new human-only decision category is created here.

---

# 17. Failure and Recovery Principle

## 17.1 Source requirements

**[SPECIFIED]**

LEVEL 1 requires at minimum:

- a completed Question Burst must not lose captured questions;
- original user questions remain immutable after capture;
- completed inquiry sessions survive infrastructure failure according to defined RPO/RTO;
- audit history remains intact through disaster recovery testing;
- AI gateway behavior is tested for failures, timeouts and retry behavior.

## 17.2 Recovery architecture gap

**[UNDERDEFINED]**

LEVEL 1 requires recovery outcomes but does not fully define the recovery mechanism.

The authoritative failure and recovery architecture belongs to:

```text
10_FAILURE_RECOVERY_ROLLBACK.md
```

## 17.3 Master recovery invariant

**[ARCHITECTURAL CLOSURE]**

Recovery must restore or preserve a valid architectural state.

Recovery may not silently bypass:

```text
immutability
authority
workspace isolation
provenance
auditability
Question Burst integrity
```

A recovery path that produces a state which could not have been validly reached through the architecture is invalid.

---

# 18. Module Authority Map

Each architectural fact has one authoritative home.

| Module | Authoritative responsibility |
|---|---|
| `00_NQUIRY_MASTER_ARCHITECTURE.md` | System identity, source hierarchy, top-level system map, cross-module invariants, source conflicts, dependency map, completion and freeze gates. |
| `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md` | Detailed system boundary, inclusion/exclusion rules, architecture principles and their consequences. |
| `02_DOMAIN_AND_RELATION_MODEL.md` | Domain objects, canonical/derived classification, ownership, identity, relations, cardinality and relation semantics. |
| `03_STATE_AND_TRANSITION_ARCHITECTURE.md` | State machines, transition eligibility, preconditions, guards, next-state rules and transition invariants. |
| `04_AUTHORITY_AND_DECISION_RIGHTS.md` | Actor roles, operation authority, decision rights, human decision authority and authority-denial semantics. |
| `05_GOVERNANCE_INSIDE_SYSTEM.md` | Executable governance mechanisms and consequence interception. |
| `06_BOUNDARY_ARCHITECTURE.md` | Boundary contracts and allow/deny/require/escalate semantics. |
| `07_EVIDENCE_AND_PROVENANCE.md` | Evidence semantics, provenance semantics, validation status, source lineage and evidence integrity. |
| `08_AI_ARCHITECTURE_AND_CONTRACTS.md` | AI Gateway, AI operations, context rules, AI output contracts, AI authority limits, validation and retry contracts. |
| `09_DATA_EVENT_API_CONTRACTS.md` | Technical schemas, persistence contracts, event contracts, API contracts and transaction-facing data semantics. |
| `10_FAILURE_RECOVERY_ROLLBACK.md` | Failure states, containment, recovery, rollback, replay and recovery validity. |
| `11_SECURITY_PRIVACY_OBSERVABILITY.md` | Security, privacy, telemetry, cost controls, logging and operational visibility. |
| `12_MINIMUM_PROTOTYPE_ARCHITECTURE.md` | Exact Minimum Closed Prototype inclusion/exclusion and vertical-slice closure. |
| `13_TEST_AND_FALSIFICATION_ARCHITECTURE.md` | Architecture tests, falsification tests, invariants, acceptance conditions and failure injection. |
| `14_IMPLEMENTATION_SEQUENCE.md` | Dependency-derived implementation batches and gates after architecture freeze. |
| `15_AI_CODING_PROMPTS/` | Bounded coding contracts derived from the frozen architecture. |
| `16_DECISION_AND_GAP_REGISTER.md` | Authoritative unresolved decision, conflict and gap register. |

If a downstream module discovers a conflict with an upstream authoritative fact, the downstream file must not locally redefine the fact.

---

# 19. Known Source Conflicts and Classification Problems

The following items are explicitly preserved.

## CONFLICT-001: Inquiry Graph prototype scope

**Status:** `[OPEN]`  
**Blocking level:** Prototype scope decision  
**Human authority required:** Yes, if LEVEL 1 cannot be deterministically reconciled in module 12.

LEVEL 1 contains three relevant signals:

1. Product principle P10 says inquiry should be modeled as a graph rather than a linear chat.
2. Version 2 lists `inquiry graph` as an addition.
3. Engineering Starting Point includes `Epic 7: Inquiry Graph` and calls that epic set the smallest architecture proving the thesis.

The LEVEL 2 Minimum Closed Prototype includes Inquiry Graph reconstruction and says this aligns with the source Phase 1 path.

That statement is too strong because LEVEL 1 itself contains scope tension.

**Master architecture treatment:**

```text
graph-like inquiry relations = source-supported product principle
dedicated Inquiry Graph implementation in Minimum Closed Prototype = OPEN
```

No final prototype-scope decision is made in 00.

Authoritative closure location:

```text
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md
16_DECISION_AND_GAP_REGISTER.md
```

## CONFLICT-002: Question Burst `allowed raw`

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

LEVEL 2 proposed:

```text
text is question-like or allowed raw
```

for Question Burst submission.

LEVEL 1 explicitly requires:

```text
participants submit only questions
no discussion
no answers
no explanations
system prevents answers/explanations
verbatim capture
```

LEVEL 1 therefore rejects unrestricted `allowed raw` semantics for the protected Question Burst.

The exact validation and failure behavior are not defined here and belong to modules 03, 05 and 06.

## CONFLICT-003: D1 and D7 terminology drift

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

Canonical LEVEL 1 names remain:

```text
D1: Target market
D7: Measurement
```

LEVEL 2 labels:

```text
D1 Product center
D7 Impact meaning
```

are non-authoritative aliases and must not replace source terminology.

## CONFLICT-004: Prototype Authority Matrix exceeds LEVEL 1

**Status:** `[CLASSIFICATION CORRECTED, CONTENT UNRESOLVED]`

LEVEL 1 defines role names and a limited set of Question Burst permissions.

LEVEL 2 creates a fuller operation-level authority matrix.

The additional operation rights are:

```text
[SWEEP-DERIVED]
```

until accepted or reconstructed in:

```text
04_AUTHORITY_AND_DECISION_RIGHTS.md
```

They are not `[SPECIFIED]`.

## CONFLICT-005: Mandatory provenance fields exceed LEVEL 1 wording

**Status:** `[OPEN ARCHITECTURAL CLOSURE CANDIDATE]`

LEVEL 1 requires human/AI distinguishability, provenance for AI-derived objects, and additional lineage information for inferred objects.

LEVEL 2 makes a particular field set mandatory for all derived objects.

The semantic need for provenance is source-supported.

The exact mandatory field set is not yet source-authoritative.

Closure belongs to modules 07 and 09.

## CONFLICT-006: Authentication omitted from LEVEL 2 prototype boundary

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

LEVEL 1 lists `User authentication` as MVP Must-have.

Authentication is therefore part of the Minimum Closed Prototype source baseline.

The LEVEL 2 prototype-boundary omission is not authoritative.

---

# 20. Open Decisions

## 20.1 LEVEL 1 named open decisions

The canonical LEVEL 1 decision names are:

```text
D1: Target market
D2: AI autonomy
D3: Data sovereignty
D4: Enterprise deployment
D5: Collaboration
D6: Research
D7: Measurement
D8: Methodology governance
D9: AI provider
D10: Business model
```

These remain `[OPEN]` unless a human decision has explicitly resolved them.

00 does not silently apply the LEVEL 2 recommended answers.

## 20.2 Architecture-exposed open items

The following additional architecture decisions or gaps are currently visible:

```text
DEC-A001  Dedicated Inquiry Graph inclusion in Minimum Closed Prototype
DEC-A002  Exact operation-level authority matrix
DEC-A003  Exact mandatory provenance schema for each derived object class
DEC-A004  Exact transition eligibility rules
DEC-A005  Exact Question Burst enforcement mechanism
DEC-A006  Exact recovery / rollback mechanism
DEC-A007  Exact audit atomicity contract
DEC-A008  Exact deletion versus audit-retention semantics
DEC-A009  Exact export reconstruction format
DEC-A010  Exact evidence validation authority and lifecycle
DEC-A011  Exact RPO/RTO values
DEC-A012  Selected accessibility standard
```

These items are not all equally blocking at Stage A.

Blocking classification is owned by `16_DECISION_AND_GAP_REGISTER.md` and later refined as dependent modules expose actual closure needs.

## 20.3 Missing external methodology material

The LEVEL 1 specification refers to a Question Burst Toolkit and course material.

Those external materials are not part of the current architecture source set.

Their absence does not invalidate LEVEL 1 as the product/system authority.

It does mean that claims about what the external toolkit/course itself says cannot be independently reconstructed beyond what LEVEL 1 already incorporates.

Status:

```text
[UNKNOWN] external-source completeness
non-blocking for 00
```

---

# 21. Downstream Construction Dependencies

Architecture construction proceeds top down and recursively.

```text
00 Master Architecture
  ↓
01 System Boundary + Principles
  ↓
02 Domain + Relation Model
  ↓
03 State + Transition Architecture
  ↓
04 Authority + Decision Rights
  ↓
05 Governance Inside System
  ↓
06 Boundary Architecture
  ↓
07 Evidence + Provenance
  ↓
08 AI Architecture + Contracts
  ↓
09 Data + Events + APIs
  ↓
10 Failure + Recovery + Rollback
  ↓
11 Security + Privacy + Observability
  ↓
12 Minimum Closed Prototype
  ↓
13 Test + Falsification Architecture
  ↓
16 Decision / Gap Closure Review
  ↓
Recursive Cross-Architecture Consistency Sweep
  ↓
Architecture Baseline v1.0 Freeze
  ↓
14 Implementation Sequence
  ↓
15 AI Coding Prompts
  ↓
Implementation
  ↓
Test-driven recursive build validation
  ↓
Running Minimum Closed Prototype
```

The sequence is dependency-driven.

It may only change if dependency analysis demonstrates that another order is structurally necessary.

Any change must be recorded.

---

# 22. Recursive Architecture Rule

For every downstream architecture module:

```text
1. derive from authoritative upstream sources
2. materialize only the assigned architecture layer
3. validate its internal relations and invariants
4. test it against every already-built layer
5. expose contradictions, authority leaks, boundary failures,
   missing states, missing evidence and undefined transitions
6. stop when a downstream layer falsifies an upstream assumption
7. return to the authoritative upstream home
8. reconstruct the minimum affected structure
9. propagate the change through every dependent layer
10. validate the complete affected path again
```

A downstream patch must not conceal an upstream architectural contradiction.

---

# 23. Architecture Completion Criteria

The architecture is not complete merely because all files exist.

It is complete only when an independent engineer or bounded coding AI can determine, for every consequential prototype behavior:

```text
what exists
what is canonical
what is derived
who may act
under what authority
from which state
under which boundary
using which required evidence
which transition is allowed
which transition is denied
what persists
what is immutable
what is audited
what happens on failure
how recovery works
how rollback works where applicable
how provenance is reconstructed
what AI may do
what AI may not do
which human decision is authoritative where required
what is inside the prototype
what is deferred
how the mechanism is tested
what implementation dependency precedes it
```

If a structurally required answer is absent, architecture closure is incomplete.

---

# 24. Architecture Baseline Freeze Criteria

`ARCHITECTURE BASELINE v1.0` may not be frozen until all of the following are true.

## 24.1 Required module state

```text
00 through 13 completed
16 Decision and Gap Register closure review completed
```

## 24.2 Recursive cross-architecture consistency sweep completed

The sweep must validate at minimum:

```text
domain ↔ state
state ↔ transition
transition ↔ authority
authority ↔ governance
governance ↔ boundary
boundary ↔ evidence
evidence ↔ AI contract
AI contract ↔ persistence
persistence ↔ audit
failure ↔ recovery
recovery ↔ state
prototype ↔ LEVEL 1 MVP
prototype ↔ tests
tests ↔ architectural invariants
```

## 24.3 Conflict closure

No prototype-blocking P0/P1 architectural contradiction may remain unresolved.

A source-level human decision may remain open only if the Minimum Closed Prototype can be proven structurally valid without depending on that decision.

## 24.4 Traceability

Every consequential mechanism in the Minimum Closed Prototype must trace from source or accepted closure through implementation-facing contract and test.

## 24.5 No authority ambiguity

No consequential transition may rely on an unspecified actor or ambiguous authority.

## 24.6 No AI authority collapse

No AI output may become an authority-bearing human decision implicitly.

## 24.7 No boundary bypass

No implementation path may bypass the authoritative transition, authority, provenance, AI, audit or workspace boundaries defined by the architecture.

Only after these criteria are satisfied may modules 14 and 15 become implementation-authoritative.

---

# 25. Internal Consistency Check for 00

## 25.1 Check against LEVEL 1

**Result:** PASS WITH PRESERVED OPEN CONFLICTS

The system identity, product purpose, question-first thesis, human agency, Question Burst integrity, session state names, AI Gateway direction, MVP authentication requirement, audit/provenance distinction, NFR anchors and LEVEL 1 open-decision names remain source-faithful.

00 does not promote the LEVEL 2 authority matrix or provenance field set into `[SPECIFIED]`.

00 does not silently resolve the dedicated Inquiry Graph prototype scope conflict.

## 25.2 Check against LEVEL 2

**Result:** PASS WITH EXPLICIT OVERRIDES BY SOURCE PRECEDENCE

LEVEL 2 remains valid as reconstruction input where it does not contradict LEVEL 1.

The following LEVEL 2 elements are explicitly constrained:

```text
`allowed raw` in protected Question Burst
→ rejected by LEVEL 1

D1 Product center
→ canonical term restored to D1 Target market

D7 Impact meaning
→ canonical term restored to D7 Measurement

full prototype authority matrix
→ retained only as SWEEP-DERIVED candidate

mandatory provenance field set
→ retained only as closure candidate

prototype boundary without authentication
→ corrected by LEVEL 1 MVP requirement

Inquiry Graph prototype inclusion
→ remains open due LEVEL 1 internal scope tension
```

## 25.3 Internal master-map consistency

**Result:** PASS

No relation in 00 grants authority by implication.

No AI capability in 00 grants decision authority.

No detailed downstream contract has been silently defined inside the master map.

No Stage B / file 01 content has been constructed.

---

# 26. Non-Source Additions Introduced in 00

Every new architecture-level addition in this file is classified below.

| Addition | Status | Reason |
|---|---|---|
| Consequential transition closure invariant | `[ARCHITECTURAL CLOSURE]` | Required by current build mandate to make consequential behavior reconstructable and implementation-bounded. |
| Human decision as authority-bearing system fact | `[ARCHITECTURAL CLOSURE]` | Required to materialize LEVEL 1 Human Agency without collapsing human authority into generic HITL. |
| Governance-before-consequence principle | `[ARCHITECTURAL CLOSURE]` | Required because LEVEL 1 names state, authorization, provenance and audit requirements without fully executable enforcement. |
| One-authoritative-home rule | `[ARCHITECTURAL CLOSURE]` | Required to prevent architecture drift across the modular repository. |
| Boundary contract dimensions `INPUT/CONDITION/AUTHORITY/VALIDATION/ALLOW/DENY/REQUIRE/ESCALATE/AUDIT/FAILURE` | `[ARCHITECTURAL CLOSURE]` | Required to close the boundary reconstruction consistently across modules. |
| Recovery-valid-state invariant | `[ARCHITECTURAL CLOSURE]` | Required so recovery cannot create states forbidden by normal architecture. |
| Recursive architecture reconstruction rule | `[ARCHITECTURAL CLOSURE]` | Explicitly mandated for this build to prevent downstream patching of upstream contradictions. |
| Baseline freeze gate | `[ARCHITECTURAL CLOSURE]` | Explicitly mandated to prevent implementation before architecture closure. |

No other new system behavior is introduced by 00.

---

# 27. Readiness for 01

## Structural readiness result

**READY FOR HUMAN REVIEW**

`00_NQUIRY_MASTER_ARCHITECTURE.md` is structurally capable of serving as the upstream map for `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md`.

The following facts are stable enough for 01:

```text
system identity
system purpose
source hierarchy
status semantics
source traceability rule
product-level boundary anchor
LEVEL 1 MVP anchor
architecture principles
high-level domain classes
high-level relation map
session state names
authority model boundary
human decision authority principle
governance model boundary
boundary classes
evidence/provenance role
AI role and prohibition boundary
failure/recovery invariant
module authority map
known source conflicts
open-decision preservation
construction dependency path
architecture completion gate
baseline freeze gate
```

The following remain intentionally unresolved and must not be treated as closed by 01:

```text
CONFLICT-001 dedicated Inquiry Graph prototype scope
CONFLICT-004 operation-level authority matrix content
CONFLICT-005 exact mandatory provenance field set
DEC-A004 exact transition eligibility
DEC-A005 exact Question Burst enforcement mechanism
DEC-A006 recovery / rollback mechanism
DEC-A007 audit atomicity
DEC-A008 deletion vs audit retention
DEC-A009 export reconstruction format
DEC-A010 evidence validation authority
DEC-A011 RPO/RTO values
DEC-A012 accessibility standard
LEVEL 1 D1 through D10 unless separately human-resolved
```

No prototype implementation is authorized.

No architecture baseline is frozen.

No downstream file has been built.

---

**STOP CONDITION REACHED**

Await human review and explicit:

```text
GO::BUILD_01_SYSTEM_BOUNDARY_AND_PRINCIPLES
```
