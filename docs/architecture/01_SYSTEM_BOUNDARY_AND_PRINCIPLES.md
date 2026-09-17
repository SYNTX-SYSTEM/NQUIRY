# 01_SYSTEM_BOUNDARY_AND_PRINCIPLES

**Project:** N.Q.U.I.R.Y.  
**Document role:** Authoritative detailed system boundary and architecture principles  
**Architecture stage:** B, System Boundary + Principles  
**Upstream authority:** `00_NQUIRY_MASTER_ARCHITECTURE.md`  
**LEVEL 1 authority:** `N.Q.U.I.R.Y. - Product & System Specification`  
**LEVEL 2 input:** `# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md`  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 02 not yet authorized

---

# 0. Document Authority and Scope

This file is authoritative for:

```text
detailed system boundary
system inclusion and exclusion rules
boundary-level product scope
architecture principles
principle consequences
cross-principle invariants
boundary obligations passed downstream
boundary-level open decisions and gaps
```

This file is not authoritative for:

```text
domain object schemas
relation cardinalities
state-machine definitions
transition eligibility tables
operation-level authority matrices
governance enforcement implementation
detailed boundary contracts
provenance field schemas
API schemas
event schemas
failure-state mechanics
recovery algorithms
prototype final inclusion/exclusion
test-case implementation
implementation sequence
```

Those facts belong to later authoritative modules.

This file may identify a downstream requirement.

It must not implement a downstream contract.

If a detailed boundary or principle exposes a contradiction in `00_NQUIRY_MASTER_ARCHITECTURE.md`, this build must stop instead of patching the contradiction locally.

No such contradiction has been identified during construction of this file.

---

# 1. Source and Upstream Authority

## 1.1 Upstream architecture authority

`00_NQUIRY_MASTER_ARCHITECTURE.md` is approved as the authoritative upstream system map.

This file preserves without reinterpretation:

```text
source hierarchy
status semantics
system identity
system purpose
LEVEL 1 MVP anchor
Human Decision Authority
Governance Before Consequence
one-authoritative-home rule
consequential transition closure invariant
recursive architecture reconstruction rule
recovery-valid-state invariant
known source conflicts
open decisions
baseline freeze criteria
```

## 1.2 LEVEL 1 authority

LEVEL 1 remains authoritative for:

```text
product principles P1 through P10
product architecture
core domain concepts
Question Burst methodology
collaboration modes
session-state names
AI Coach modes
research mode
Question-to-Action pipeline
NFR catalogue
security requirements
privacy requirements
AI safety
data architecture direction
AI Gateway direction
method library
source attribution
MVP scope
acceptance criteria
open decisions D1 through D10
project prioritization
Definition of Done
engineering starting point
```

## 1.3 LEVEL 2 role

LEVEL 2 remains architectural reconstruction input.

Its boundary reconstruction is useful as a gap map.

Its labels and mechanisms do not become `[SPECIFIED]` merely because they are structurally plausible.

---

# 2. Boundary Model

N.Q.U.I.R.Y. has multiple distinct boundary dimensions.

A system boundary is not one perimeter.

The architecture must keep separate:

```text
product boundary
prototype boundary
identity boundary
workspace boundary
organization / tenancy boundary
authority boundary
state-transition boundary
Question Burst boundary
human / AI boundary
AI processing-context boundary
model-provider boundary
methodology boundary
evidence boundary
provenance boundary
decision boundary
research boundary
export boundary
privacy boundary
audit boundary
failure boundary
recovery boundary
```

The detailed allow/deny/require/escalate contracts for these boundaries belong to `06_BOUNDARY_ARCHITECTURE.md`.

This file defines what each boundary protects and which source principles constrain it.

---

# 3. Product Boundary

## 3.1 Full product boundary

**[SPECIFIED]**

The full N.Q.U.I.R.Y. product boundary covers inquiry-driven leadership and problem solving across the lifecycle from challenge framing through evolving questions, assumptions, evidence, experiments, action, learning and re-questioning.

The product boundary includes product capabilities for:

```text
challenge articulation
question creation
question preservation
question reframing
question classification
question clustering
assumption exposure
perspective expansion
Question Burst
reflection
question selection
impact inquiry
quality-question support
question audits
question journeys
listening and reflection
evidence connection
experiment design
research support
decision support
inquiry history
longitudinal learning
team inquiry
facilitated inquiry
AI-assisted inquiry
export
auditability
method configuration
```

The full product boundary is broader than the Minimum Closed Prototype boundary.

## 3.2 Product boundary does not imply immediate implementation

**[IMPLIED]**

LEVEL 1 separates:

```text
MVP
Version 2
Version 3
Phase 1
Phase 2
Phase 3
Phase 4
```

Therefore inclusion in the product vision does not mean inclusion in the first implementation.

No product capability may be excluded from the full product architecture merely because it is deferred from the prototype.

No deferred capability may be silently pulled into the prototype merely because it exists in the full product specification.

## 3.3 Product boundary versus implementation-provider boundary

**[ARCHITECTURAL CLOSURE]**

The semantic product boundary is independent from the technology provider used to materialize it.

Provider selection may change.

Canonical N.Q.U.I.R.Y. semantics must not depend on one specific LLM vendor, database product, identity provider, deployment vendor or external research provider unless later architecture explicitly establishes such a dependency.

Trace:

```text
LEVEL 1 configurable model selection
LEVEL 1 AI Gateway direction
00 provider-specific behavior does not become canonical product semantics
```

---

# 4. Minimum Product Boundary Anchor

## 4.1 LEVEL 1 MVP anchor

**[SPECIFIED]**

The LEVEL 1 MVP requires:

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

These capabilities define the minimum source boundary that later prototype architecture must preserve.

## 4.2 MVP acceptance boundary

**[SPECIFIED]**

LEVEL 1 additionally requires the Question Burst MVP to support:

```text
facilitator creates a challenge
participants join
facilitator starts Question Burst
timer runs for configured duration
participants submit questions
answers/explanations are prevented in Question Burst mode
questions are stored verbatim
each question has author and timestamp
questions cannot be silently modified
AI analysis begins only after burst completion
questions can be clustered
users select 1 to 3 compelling questions
one question can be selected as most important
five-level impact inquiry is supported
session can be exported
```

## 4.3 Dedicated Inquiry Graph scope

**[OPEN]**

This file preserves `CONFLICT-001`.

Source-supported graph semantics are inside the product boundary.

The dedicated Inquiry Graph component's inclusion in the Minimum Closed Prototype remains unresolved.

This file does not reinterpret that scope as closed.

---

# 5. External Dependency Boundary

## 5.1 External systems

The following may participate in the system environment without becoming canonical N.Q.U.I.R.Y. product semantics:

```text
LLM providers
external research providers
enterprise identity providers
deployment infrastructure
external collaboration platforms
organizational data sources
calendar systems
CRM systems
product-data systems
meeting systems
Slack / Teams or similar systems
```

Some of these belong only to later product versions.

## 5.2 External-provider authority

**[ARCHITECTURAL CLOSURE]**

An external provider may supply:

```text
compute
model inference
identity assertion
source material
search results
storage infrastructure
message transport
integration data
```

An external provider does not acquire product authority merely by supplying a service.

Provider output becomes product state only through N.Q.U.I.R.Y. architecture.

The exact acceptance, validation and persistence mechanisms belong downstream.

## 5.3 Regulatory interpretation

**[SPECIFIED]**

LEVEL 1 explicitly states that regulatory requirements such as GDPR are to be confirmed based on deployment and target market rather than assumed.

Therefore regulatory interpretation is not silently embedded in the product boundary at this stage.

D1, D3 and D4 remain open where they affect deployment-specific requirements.

---

# 6. Identity Boundary

## 6.1 Identity is inside the system architecture

**[SPECIFIED]**

LEVEL 1 requires user authentication in the MVP.

Its minimum security architecture begins with:

```text
Identity
→ Authentication
→ Authorization
→ Workspace isolation
→ Data access
→ AI Gateway
→ Model provider
```

Identity therefore participates in the architecture before protected workspace access.

## 6.2 Identity does not equal authority

**[ARCHITECTURAL CLOSURE]**

Successful authentication establishes identity.

It does not by itself establish authority for every consequential action.

Authority must be resolved separately.

Trace:

```text
LEVEL 1 authentication requirement
LEVEL 1 collaboration roles
00 Human Decision Authority
00 authority boundary
```

## 6.3 Identity-provider implementation

**[OPEN]**

LEVEL 1 does not choose the identity-provider technology.

No external identity provider is introduced as an architecture requirement in 01.

---

# 7. Workspace Boundary

## 7.1 Workspace as source-defined container

**[SPECIFIED]**

LEVEL 1 defines Workspace as:

```text
a container for an organization, team or personal inquiry practice
```

Workspace includes source concepts for:

```text
owner
members
permissions
```

LEVEL 1 NFRs require workspace data to be accessible only according to explicit authorization rules.

LEVEL 1 also requires AI requests not to expose data belonging to unauthorized workspaces.

## 7.2 Workspace isolation principle

**[SPECIFIED]**

Workspace boundaries constrain:

```text
data access
AI processing context
authorization
privacy exposure
export
```

The exact enforcement mechanism belongs downstream.

## 7.3 Workspace boundary cannot be inferred from UI context

**[ARCHITECTURAL CLOSURE]**

The presence of a workspace identifier in the UI or request is not sufficient to establish valid workspace access.

A downstream architecture must bind workspace scope to authenticated identity and applicable authority.

This closes the gap between explicit workspace-isolation NFRs and executable enforcement.

---

# 8. Organization and Tenancy Boundary

## 8.1 Source observations

LEVEL 1 includes:

```text
User.organization_id
Workspace as organization, team or personal container
tenant isolation in AI Gateway requirements
workspace isolation in NFRs
```

LEVEL 1 does not define:

```text
Organization as a first-class object
Tenant as a first-class object
Tenant-to-Workspace cardinality
Organization-to-Workspace cardinality
User-to-Organization cardinality
whether Tenant and Workspace are identical
```

## 8.2 GAP-01-001: Tenant versus Workspace semantics

**Status:** `[UNDERDEFINED]`

`tenant isolation` and `workspace isolation` must not be treated as synonyms without architectural resolution.

The source provides a concrete Workspace concept.

It does not provide a canonical Tenant object.

Required downstream handling:

```text
02_DOMAIN_AND_RELATION_MODEL.md
11_SECURITY_PRIVACY_OBSERVABILITY.md
```

No `Tenant = Workspace` decision is made in 01.

## 8.3 GAP-01-002: Organization relation semantics

**Status:** `[UNDERDEFINED]`

`User.organization_id` exists in the LEVEL 1 User object.

No Organization object appears in the LEVEL 1 first-class object list or initial relational table list.

The system must not silently invent an Organization domain object in 01.

Required downstream handling:

```text
02_DOMAIN_AND_RELATION_MODEL.md
```

02 must determine whether `organization_id` is:

```text
external identity metadata
a future domain relation
a tenancy relation
a legacy/specification placeholder
or evidence of a missing Organization object
```

until then the relation remains unresolved.

---

# 9. Authority Boundary

## 9.1 Source-defined roles

**[SPECIFIED]**

LEVEL 1 names:

```text
Owner
Facilitator
Contributor
Observer
Viewer
```

## 9.2 Source-defined Question Burst permissions

**[SPECIFIED]**

During Question Burst:

```text
participants submit questions
participants cannot edit others' questions
facilitator can pause/end burst
AI analysis remains disabled until completion
```

## 9.3 Authority is operation-specific

**[ARCHITECTURAL CLOSURE]**

Role names do not by themselves determine all system actions.

A later authority architecture must resolve authority at the level required by the consequential operation.

01 does not define that matrix.

Authoritative home:

```text
04_AUTHORITY_AND_DECISION_RIGHTS.md
```

## 9.4 LEVEL 2 authority matrix status

**[SWEEP-DERIVED]**

The LEVEL 2 prototype authority matrix remains candidate input only.

It is not promoted to `[SPECIFIED]`.

`CONFLICT-004` remains preserved.

---

# 10. Human Decision Boundary

## 10.1 Human agency

**[SPECIFIED]**

LEVEL 1 states that the human remains responsible for:

```text
decisions
interpretation
experiments
actions
ethical judgments
```

## 10.2 Human decision authority

**[ARCHITECTURAL CLOSURE]**

Where a consequential transition requires one of these human decisions, the human decision is authority-bearing system state.

AI output may prepare or inform the decision where permitted.

AI output does not satisfy the human decision requirement.

## 10.3 AI assistance does not collapse decision authority

LEVEL 1 permits AI components such as:

```text
Insight Synthesizer
Experiment Designer
Researcher mode
Strategist mode
Reflection Coach
```

Those capabilities do not transfer human authority to the AI.

The architecture must preserve:

```text
AI experiment design
≠ human experiment decision

AI synthesis
≠ human interpretation

AI recommendation
≠ human decision

AI proposed action
≠ human action authority
```

Exact operation-level semantics belong to modules 04 and 08.

---

# 11. State-Transition Boundary

## 11.1 Source state lifecycle

**[SPECIFIED]**

LEVEL 1 defines:

```text
DRAFT
SETUP
CHALLENGE_CAPTURE
QUESTION_GENERATION
QUESTION_CAPTURE
ANALYSIS
REFLECTION
QUESTION_SELECTION
INVESTIGATION
EXPERIMENT
ACTION
REVIEW
CLOSED
```

LEVEL 1 also states that users must not accidentally skip critical phases unless explicitly permitted.

## 11.2 Transition eligibility

**[UNDERDEFINED]**

The source does not fully define:

```text
all legal source states
all legal target states
all actors
all authority conditions
all preconditions
all required evidence
all denial semantics
all failure behavior
```

Authoritative home:

```text
03_STATE_AND_TRANSITION_ARCHITECTURE.md
```

## 11.3 Principle consequence

No UI flow may be treated as the state machine.

No state label grants transition authority.

No AI output grants transition eligibility.

---

# 12. Question Burst Boundary

## 12.1 Protected human Question Burst

**[SPECIFIED]**

The signature Question Burst requires:

```text
rapid question generation
approximately four minutes in the methodology description
questions only
no discussion
no answers
no explanations
verbatim capture
freeze raw question set at burst end
AI analysis only after burst
```

## 12.2 Raw-set integrity

**[SPECIFIED]**

The original burst must remain auditable.

Human questions are captured exactly as entered.

AI-generated questions must not be invisibly blended with human questions.

## 12.3 Distinct AI participation modes

**[SPECIFIED]**

LEVEL 1 allows later distinct modes:

```text
Mode A: Human-only
Mode B: Human + AI
Mode C: AI challenge after humans finish
```

AI participation is therefore mode-bound.

The protected human-only burst cannot be silently converted into Human + AI mode.

## 12.4 CONFLICT-002 preservation

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

LEVEL 2 `allowed raw` semantics do not apply to the protected Question Burst.

LEVEL 1 requires Question Burst mode to prevent answers and explanations.

## 12.5 GAP-01-003: Active-burst AI observer / recorder semantics

**Status:** `[UNDERDEFINED]`

LEVEL 1 states:

```text
AI = observer / recorder
AI != answer generator
AI != question generator
AI != evaluator
AI != moderator unless explicitly enabled
```

and also:

```text
AI analysis remains disabled until burst completion
```

The source does not determine whether `observer / recorder` means:

```text
non-LLM application capture only
LLM-visible passive context
a model call with no generated output
or another technical mechanism
```

01 does not choose one.

This gap must be resolved by:

```text
06_BOUNDARY_ARCHITECTURE.md
08_AI_ARCHITECTURE_AND_CONTRACTS.md
```

without violating raw-burst integrity.

## 12.6 CONFLICT-007: Burst duration semantics

**Status:** `[OPEN SOURCE TENSION]`

LEVEL 1 contains three related formulations:

```text
approximately four minutes
MVP Must-have: Four-minute timer
acceptance criterion: timer runs for configured duration
```

The architecture must not silently treat these as identical.

Possible interpretations include:

```text
four minutes as default configurable duration
four minutes as fixed MVP duration
methodology target near four minutes with configuration allowed
```

No interpretation is selected in 01.

Downstream resolution is required before timer behavior becomes implementation-authoritative.

Relevant homes:

```text
03_STATE_AND_TRANSITION_ARCHITECTURE.md
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md
16_DECISION_AND_GAP_REGISTER.md
```

---

# 13. Human / AI Boundary

## 13.1 Source distinction

**[SPECIFIED]**

LEVEL 1 requires the system to distinguish:

```text
USER QUESTION
AI QUESTION
INFERRED QUESTION
REFRAMED QUESTION
FOLLOW-UP QUESTION
```

It explicitly prohibits silent attribution of an AI-generated question to a human.

## 13.2 Human-authored state protection

**[SPECIFIED]**

AI suggestions must never silently replace original human questions.

`original_text` must never be overwritten.

## 13.3 AI interpretation boundary

**[SPECIFIED]**

AI speculative interpretations must not be presented as facts.

AI-generated suggestions are hypotheses.

## 13.4 Consequential AI boundary

**[ARCHITECTURAL CLOSURE]**

AI may create or propose derived inquiry artifacts where a permitted operation allows it.

Derived AI output does not acquire consequential authority merely through persistence.

Any transition from AI-derived proposal to human-authorized consequential state must respect the authority architecture.

---

# 14. AI Processing Context Boundary

## 14.1 User visibility and control

**[SPECIFIED]**

NFR-PRIV-001 requires users to be able to determine what personal/workspace information is included in AI processing.

## 14.2 Workspace isolation

**[SPECIFIED]**

NFR-SEC-002 requires AI requests not to expose data belonging to unauthorized workspaces.

## 14.3 Context minimization obligation

**[IMPLIED]**

The combination of:

```text
workspace isolation
user visibility into AI processing
sensitive inquiry content
avoidance of unnecessary sensitive prompt logging
```

requires AI context to be bounded to permitted system context.

The exact context-selection contract is not defined in 01.

Authoritative homes:

```text
06_BOUNDARY_ARCHITECTURE.md
08_AI_ARCHITECTURE_AND_CONTRACTS.md
11_SECURITY_PRIVACY_OBSERVABILITY.md
```

---

# 15. Model Provider Boundary

## 15.1 AI Gateway direction

**[SPECIFIED]**

LEVEL 1 defines the internal abstraction:

```text
Application
→ AI Gateway
→ Policy Engine
→ Prompt Builder
→ Model Router
→ LLM Provider
→ Response Validator
→ Application
```

and states that all LLM traffic should pass through it.

## 15.2 Provider independence

**[SPECIFIED]**

The source states that this abstraction prevents business logic from becoming coupled to one model vendor.

Model selection should be configurable.

## 15.3 Enforcement status

**[UNDERDEFINED]**

LEVEL 1 gives the architectural direction.

It does not fully specify:

```text
runtime bypass prevention
provider adapter contract
gateway failure semantics
direct-call detection
tool-call boundaries
model fallback authority
```

These belong to module 08 and supporting boundary/security modules.

01 does not silently strengthen the source wording into a complete gateway runtime contract.

---

# 16. Methodology Boundary

## 16.1 Method library

**[SPECIFIED]**

N.Q.U.I.R.Y. should have an internal Inquiry Method Library.

Methods should be represented as configuration rather than hard-coded UI.

## 16.2 Methodology as product logic

**[SPECIFIED]**

Question Burst rules include method knowledge such as:

```text
do_not_answer
do_not_explain
capture_verbatim
```

## 16.3 Method knowledge attribution

**[SPECIFIED]**

LEVEL 1 distinguishes:

```text
Method knowledge
AI inference
User knowledge
External research
```

Methodology must not be silently fabricated by AI and represented as source methodology.

## 16.4 D8 methodology governance

**[OPEN]**

LEVEL 1 asks:

```text
Who owns and approves the inquiry methodology encoded in the system?
```

01 cannot resolve D8.

Until D8 is resolved:

```text
method configuration is inside product architecture
method approval authority remains open
```

## 16.5 Method configuration does not equal runtime permission

**[ARCHITECTURAL CLOSURE]**

A configured method may define expected inquiry behavior.

Configuration alone does not grant actors authority to bypass system boundaries.

Method rules and authority rules remain separate architectural dimensions.

---

# 17. Evidence Boundary

## 17.1 Evidence over confidence

**[SPECIFIED]**

AI confidence is not evidence.

AI interpretation is not evidence merely because it has a score.

## 17.2 Evidence is source-connected

**[SPECIFIED]**

LEVEL 1 contains an Evidence object with:

```text
type
source
content
question_id
reliability
timestamp
```

Research mode also maintains a path through:

```text
Question
→ Research plan
→ Sources
→ Evidence
→ Findings
→ Contradictions
→ Remaining uncertainty
→ New questions
```

## 17.3 Evidence validation gap

**[UNDERDEFINED]**

LEVEL 1 does not fully specify:

```text
who validates evidence
what validation states exist
when evidence is sufficient
when evidence may support a consequential decision
how contradictory evidence is governed
```

Authoritative home:

```text
07_EVIDENCE_AND_PROVENANCE.md
```

No evidence-lifecycle mechanism is introduced in 01.

---

# 18. Provenance Boundary

## 18.1 Source-level requirement

**[SPECIFIED]**

AI-generated content must remain distinguishable from human-generated content.

LEVEL 1 identifies provenance categories:

```text
human
ai
imported
inferred
```

For inferred objects it names:

```text
confidence
source_nodes
created_by_model
created_at
```

## 18.2 Provenance field-set status

**[OPEN ARCHITECTURAL CLOSURE CANDIDATE]**

`CONFLICT-005` remains preserved.

The LEVEL 2 requirement making a uniform mandatory field set apply to every derived object exceeds direct LEVEL 1 wording.

01 preserves the provenance obligation.

01 does not define the universal field schema.

Authoritative homes:

```text
07_EVIDENCE_AND_PROVENANCE.md
09_DATA_EVENT_API_CONTRACTS.md
```

---

# 19. Decision Boundary

## 19.1 Decision support is inside the product

**[SPECIFIED]**

LEVEL 1 includes Decision as a first-class object and identifies decision support as a system capability.

## 19.2 Human responsibility

**[SPECIFIED]**

Humans remain responsible for decisions.

## 19.3 AI strategist capability

**[SPECIFIED]**

AI Strategist mode may connect inquiry to decisions and experiments.

This does not grant AI decision authority.

## 19.4 Decision tracking scope

LEVEL 1 Version 2 lists decision tracking as a later addition.

Therefore:

```text
decision semantics exist in the full product boundary
full decision-tracking implementation is not automatically MVP
```

The exact prototype scope belongs to module 12.

---

# 20. Research Boundary

## 20.1 Research capability

**[SPECIFIED]**

LEVEL 1 defines a Research Mode entered when the user chooses:

```text
Investigate this question
```

Research output must remain connected to the originating question.

## 20.2 Research does not automatically become evidence

**[IMPLIED]**

Research mode explicitly passes through sources and evidence.

AI findings remain subject to the evidence and provenance principles.

## 20.3 D6 research scope

**[OPEN]**

LEVEL 1 asks whether external web research should be part of the core product.

The presence of a Research Mode definition does not resolve D6.

## 20.4 GAP-01-004: Roadmap placement of research and inquiry capabilities

**Status:** `[UNDERDEFINED]`

LEVEL 1 contains multiple roadmap views:

```text
Version 2 includes research mode, Inquiry Graph, Question Audits, Question Journeys
Phase 3 includes Question Journeys, Question Audits, Listening to Learn
Phase 4 includes Research and enterprise-level capabilities
```

The version and phase roadmaps are not a one-to-one mapping.

This does not block the full product boundary.

It does mean later implementation sequencing must not infer exact version-to-phase equivalence without explicit architecture treatment.

Relevant homes:

```text
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md
14_IMPLEMENTATION_SEQUENCE.md
16_DECISION_AND_GAP_REGISTER.md
```

---

# 21. Collaboration Boundary

## 21.1 Product collaboration modes

**[SPECIFIED]**

N.Q.U.I.R.Y. should support:

```text
individual inquiry
pair inquiry
team inquiry
facilitated sessions
asynchronous question contribution
```

## 21.2 MVP collaborative behavior

**[SPECIFIED]**

Question Burst acceptance criteria include:

```text
facilitator creates a challenge
participants join
facilitator starts burst
participants submit questions
```

Therefore the MVP is not source-defined as strictly solo-only.

## 21.3 D5 real-time collaboration

**[OPEN]**

LEVEL 1 asks whether real-time team collaboration belongs to MVP or later.

01 does not interpret participant joining and question submission as proof of a particular real-time transport architecture.

## 21.4 Collaboration transport is not product authority

**[ARCHITECTURAL CLOSURE]**

Whatever transport is later selected, message arrival does not itself establish:

```text
identity
workspace membership
operation authority
transition eligibility
canonical persistence
```

Those remain governed by their authoritative architecture layers.

---

# 22. Privacy Boundary

## 22.1 Sensitive inquiry content

**[SPECIFIED]**

Questions may contain sensitive organizational or personal content.

They must be treated as potentially sensitive.

## 22.2 Source privacy obligations

**[SPECIFIED]**

LEVEL 1 requires:

```text
workspace boundaries enforced
AI provider processing configuration explicit
retention configurable
deletion propagated where legally/technically required
exports controlled
analytics avoids unnecessary content exposure
user can determine what information enters AI processing
```

## 22.3 Deletion versus audit retention

**[OPEN]**

The interaction between deletion and audit/reconstruction requirements remains unresolved.

01 does not define retention semantics.

Relevant homes:

```text
10_FAILURE_RECOVERY_ROLLBACK.md
11_SECURITY_PRIVACY_OBSERVABILITY.md
16_DECISION_AND_GAP_REGISTER.md
```

---

# 23. Security Boundary

## 23.1 Source security chain

**[SPECIFIED]**

```text
Identity
→ Authentication
→ Authorization
→ Workspace isolation
→ Data access
→ AI Gateway
→ Model provider
```

## 23.2 Security is cross-cutting

Security constraints apply across:

```text
identity
workspace access
AI context
external model access
tool permissions
exports
shared content
research
logging
```

## 23.3 Security does not redefine product semantics

**[ARCHITECTURAL CLOSURE]**

Security enforcement may deny or constrain an operation.

It does not silently change the meaning of canonical product state.

Any state consequence caused by security behavior must still be represented through the relevant state, failure and audit architecture.

---

# 24. Observability and Cost Boundary

## 24.1 Observability

**[SPECIFIED]**

AI requests must be observable through:

```text
latency
errors
model
token / cost metrics
```

while avoiding unnecessary sensitive prompt logging.

## 24.2 Cost controls

**[SPECIFIED]**

AI operations should record:

```text
model
input_tokens
output_tokens
latency
estimated_cost
workspace
user
operation
```

and the system should support budget and rate-control concepts.

## 24.3 Observability is not provenance

**[ARCHITECTURAL CLOSURE]**

Operational telemetry and product provenance are distinct.

Telemetry may describe execution.

It does not by itself prove semantic origin or authority.

This distinction must be maintained downstream.

---

# 25. Export Boundary

## 25.1 Export is inside MVP

**[SPECIFIED]**

LEVEL 1 requires export in MVP and session export in acceptance criteria.

NFR-INT-001 requires machine-readable export for questions, insights, assumptions and decisions.

## 25.2 Export control

**[SPECIFIED]**

LEVEL 1 privacy requirements state that exported data must be controlled.

## 25.3 Export scope remains underdefined

**[UNDERDEFINED]**

LEVEL 1 does not fully define:

```text
who may export
which objects are included
redaction rules
derived-content inclusion
audit inclusion
reconstruction guarantees
deletion interaction
format contract
```

Authoritative homes:

```text
04_AUTHORITY_AND_DECISION_RIGHTS.md
06_BOUNDARY_ARCHITECTURE.md
09_DATA_EVENT_API_CONTRACTS.md
11_SECURITY_PRIVACY_OBSERVABILITY.md
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md
```

---

# 26. Audit Boundary

## 26.1 Traceability requirement

**[SPECIFIED]**

Changes to:

```text
questions
assumptions
decisions
experiments
```

must be traceable.

The original Question Burst must remain auditable.

## 26.2 Audit is not merely UI history

**[ARCHITECTURAL CLOSURE]**

A visible history screen alone does not satisfy auditability.

Auditability must support reconstruction appropriate to the requirement being tested.

The exact event and persistence contracts belong downstream.

## 26.3 Audit atomicity

**[OPEN]**

01 preserves `DEC-A007`.

The source does not fully state whether failure to write audit data must block a consequential state transition.

That decision belongs to later closure.

---

# 27. Failure Boundary

## 27.1 Source failure requirements

**[SPECIFIED]**

LEVEL 1 requires testing for:

```text
model failures
timeouts
retry behavior
persistence
infrastructure failure
```

and requires completed Question Bursts not to lose captured questions.

## 27.2 Failure containment principle

**[ARCHITECTURAL CLOSURE]**

A failure in an external or derived subsystem must not silently create a canonical state transition that would be invalid under normal architecture.

Failure behavior must be explicit before implementation.

Authoritative home:

```text
10_FAILURE_RECOVERY_ROLLBACK.md
```

---

# 28. Recovery Boundary

## 28.1 Recovery objective

**[SPECIFIED]**

LEVEL 1 disaster recovery requires:

```text
completed Question Burst
→ infrastructure failure
→ recovery
→ questions still present
→ audit history intact
```

## 28.2 Valid-state recovery

**[ARCHITECTURAL CLOSURE]**

Recovery must preserve or reconstruct a state permitted by the architecture.

Recovery cannot bypass:

```text
immutability
authority
workspace isolation
Question Burst integrity
human / AI distinction
auditability
```

## 28.3 RPO / RTO

**[OPEN]**

LEVEL 1 requires recovery according to defined RPO/RTO.

The values are not defined.

`DEC-A011` remains open.

---

# 29. Architecture Principles and Consequences

This section is authoritative for the architecture consequence of LEVEL 1 product principles.

It does not implement downstream mechanisms.

## P1: Questions before answers

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
The system must preserve an inquiry phase in which premature answer generation can be prevented.
```

Prohibited collapse:

```text
challenge input
→ immediate answer generation as default product behavior
```

Relevant downstream modules:

```text
03
05
06
08
12
13
```

## P2: Challenge the frame

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
challenge representation must remain available to inquiry mechanisms that can expose ambiguity, assumptions and alternative framing.
```

Prohibited collapse:

```text
initial challenge framing
= unquestionable canonical truth
```

Relevant modules:

```text
02
07
08
```

## P3: Preserve the user's thinking

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
human-authored original question content must remain reconstructable and must not be silently overwritten by normalization, reframe or AI analysis.
```

Prohibited collapse:

```text
AI reframe
→ overwrite original_text
```

Relevant modules:

```text
02
07
09
10
13
```

## P4: Make assumptions visible

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
assumptions must be representable separately from the text in which they were inferred.
```

Prohibited collapse:

```text
AI-detected assumption
= source fact
```

Relevant modules:

```text
02
07
08
```

## P5: Diversity increases inquiry quality

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
the system may introduce perspectives different from the user's initial framing while preserving their origin and advisory nature.
```

Prohibited collapse:

```text
alternative perspective
→ silent replacement of user framing
```

Relevant modules:

```text
07
08
```

## P6: Psychological safety

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
system behavior must not require evaluative labeling of user questions as stupid, naive or incorrect.
```

Additional source constraint:

```text
Emotional Temperature is a self-reported reflection signal, not a psychological diagnosis.
```

Prohibited collapse:

```text
question-quality analytics
→ judgment of person

emotional score
→ diagnosis
```

Relevant modules:

```text
08
11
13
```

## P7: Questions should create movement

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
the product architecture must support movement from inquiry toward investigation, evidence, experiment or action rather than endless question generation.
```

Prohibited collapse:

```text
successful use
= number of questions generated
```

Relevant modules:

```text
03
12
13
```

## P8: Evidence over confidence

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
AI confidence cannot satisfy an evidence requirement.
```

Prohibited collapse:

```text
high model confidence
= evidence
```

Relevant modules:

```text
07
08
13
```

## P9: Human agency

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
human-responsibility domains cannot be silently executed as AI-authoritative transitions.
```

Prohibited collapse:

```text
AI recommendation
= human decision

AI experiment design
= human experiment authority

AI strategy output
= action authority
```

Relevant modules:

```text
03
04
05
06
08
09
13
```

## P10: Inquiry is iterative

**Source status:** `[SPECIFIED]`

Architecture consequence:

```text
domain and relation architecture must support recursive inquiry and question-to-question lineage.
```

This does not resolve whether a dedicated Inquiry Graph implementation belongs in the Minimum Closed Prototype.

Prohibited collapse:

```text
chat transcript ordering
= complete inquiry relation model
```

Relevant modules:

```text
02
09
12
```

---

# 30. Additional Approved Upstream Architecture Principles

These principles originate in approved 00.

01 preserves them and states their boundary consequence.

## AP-01: Human Decision Authority

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
human-authorized decisions must remain distinguishable from AI preparation or recommendation.
```

## AP-02: Governance Before Consequence

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
a consequential operation must cross applicable governance boundaries before its consequence is accepted.
```

## AP-03: One Authoritative Home

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
01 defines scope and principles.
It does not redefine facts owned by later modules.
```

## AP-04: Recovery Valid State

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
recovery cannot create a state forbidden by ordinary architecture.
```

## AP-05: Recursive Architecture Reconstruction

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
downstream contradictions return to the authoritative upstream file.
They are not patched locally.
```

## AP-06: Baseline Freeze Gate

**Status:** `[ARCHITECTURAL CLOSURE]`

Boundary consequence:

```text
implementation cannot acquire authority while prototype-blocking architecture contradictions remain.
```

---

# 31. Cross-Principle Invariants

The following invariants arise from the combined source principles and approved upstream architecture.

## INV-01: Original question preservation

```text
human original question
!= replaceable AI artifact
```

## INV-02: AI confidence separation

```text
AI confidence
!= evidence
!= authority
```

## INV-03: Human decision separation

```text
AI proposal
!= human decision
```

## INV-04: Protected burst separation

```text
protected human Question Burst
!= answer mode
!= analysis mode
!= silent Human + AI mode
```

## INV-05: Workspace isolation

```text
authorized context in Workspace A
does not imply access to Workspace B
```

## INV-06: Source attribution separation

```text
method knowledge
!= AI inference
!= user knowledge
!= external research
```

## INV-07: Product boundary versus prototype boundary

```text
inside full N.Q.U.I.R.Y. product
does not imply
inside Minimum Closed Prototype
```

## INV-08: Provider separation

```text
provider implementation
!= canonical product semantics
```

## INV-09: Telemetry separation

```text
operational telemetry
!= semantic provenance
```

## INV-10: Recovery validity

```text
recovered state
must be valid under architecture
```

---

# 32. Known Conflicts Carried Forward

## CONFLICT-001: Inquiry Graph prototype scope

**Status:** `[OPEN]`

Preserved exactly.

01 distinguishes:

```text
graph-like inquiry semantics
= source-supported

dedicated Inquiry Graph in prototype
= unresolved
```

## CONFLICT-002: Question Burst `allowed raw`

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

Protected Question Burst remains questions-only.

## CONFLICT-003: D1 and D7 terminology

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

Canonical terms remain:

```text
D1 Target market
D7 Measurement
```

## CONFLICT-004: LEVEL 2 authority matrix

**Status:** `[CLASSIFICATION CORRECTED, CONTENT UNRESOLVED]`

Still `[SWEEP-DERIVED]`.

## CONFLICT-005: Mandatory provenance fields

**Status:** `[OPEN ARCHITECTURAL CLOSURE CANDIDATE]`

Still unresolved.

## CONFLICT-006: Authentication omitted from LEVEL 2 prototype boundary

**Status:** `[RESOLVED BY SOURCE PRECEDENCE]`

Authentication remains source-defined MVP scope.

## CONFLICT-007: Question Burst duration

**Status:** `[OPEN SOURCE TENSION]`

Newly exposed by 01.

Source simultaneously uses:

```text
approximately four minutes
Four-minute timer
configured duration
```

No implementation interpretation is selected.

---

# 33. Newly Discovered Gaps

## GAP-01-001: Tenant versus Workspace

**Status:** `[UNDERDEFINED]`

The source uses both concepts but defines only Workspace concretely.

No equivalence is assumed.

## GAP-01-002: Organization relation

**Status:** `[UNDERDEFINED]`

`User.organization_id` exists without a defined Organization object or relation model.

No Organization object is invented in 01.

## GAP-01-003: Active-burst AI observer / recorder semantics

**Status:** `[UNDERDEFINED]`

The source does not specify whether active-burst observation involves LLM processing or only non-interpretive system capture.

## GAP-01-004: Version and Phase roadmap mapping

**Status:** `[UNDERDEFINED]`

The Version 2/3 roadmap and Phase 2/3/4 prioritization are not exact equivalents.

No exact mapping is inferred.

## GAP-01-005: AI Gateway enforcement level

**Status:** `[UNDERDEFINED]`

LEVEL 1 states that all LLM traffic should pass through the AI Gateway.

The detailed architecture has not yet established the runtime mechanism that prevents direct model-call bypass.

This is not resolved in 01.

Relevant homes:

```text
06
08
13
```

## GAP-01-006: Export reconstruction semantics

**Status:** `[UNDERDEFINED]`

Export is source-required.

The source does not define whether prototype export must be:

```text
snapshot only
audit-backed reconstruction
graph projection
full replay package
or another machine-readable form
```

Relevant homes:

```text
09
12
13
```

---

# 34. Open LEVEL 1 Decisions and Boundary Impact

| Decision | Boundary impact in 01 | 01 status |
|---|---|---|
| D1 Target market | Deployment profile, packaging, privacy/regulatory context, UX emphasis | `[OPEN]` |
| D2 AI autonomy | Human/AI boundary, coach modes, authority risk | `[OPEN]` |
| D3 Data sovereignty | Processing location, storage boundary, model provider boundary | `[OPEN]` |
| D4 Enterprise deployment | Infrastructure boundary, identity integration, deployment isolation | `[OPEN]` |
| D5 Collaboration | Concurrency and transport boundary | `[OPEN]` |
| D6 Research | External research boundary and prototype scope | `[OPEN]` |
| D7 Measurement | Success metric boundary and analytics interpretation | `[OPEN]` |
| D8 Methodology governance | Method approval and configuration authority | `[OPEN]` |
| D9 AI provider | Provider implementation choice | `[OPEN]` |
| D10 Business model | Packaging, quotas, billing boundary | `[OPEN]` |

01 does not resolve any of D1 through D10.

---

# 35. Boundary Obligations Passed to 02

`02_DOMAIN_AND_RELATION_MODEL.md` must derive its domain model without violating these boundary facts.

At minimum, 02 must determine:

```text
which LEVEL 1 concepts are canonical objects
which are derived artifacts
which are configuration objects
which are external references
which concepts own state
which relations cross Workspace boundaries
how User, Workspace and organization_id relate
whether a Tenant object exists or does not exist
how Question Burst is represented
how Impact Chain is represented
how recursive question lineage is represented
how source attribution is represented at domain level
how human and AI authored artifacts remain distinguishable
how original_text immutability attaches to Question identity
```

02 must not:

```text
infer Tenant = Workspace without resolution
invent Organization silently
promote LEVEL 2 authority rules into domain semantics
resolve Inquiry Graph prototype scope
define operation-level authority
define transition tables
define universal provenance fields without tracing them
```

---

# 36. Source Consistency Validation

## 36.1 LEVEL 1 validation result

**Result:** PASS WITH PRESERVED SOURCE TENSIONS

The following 01 boundary/principle claims are directly supported by LEVEL 1:

```text
question-first product behavior
P1 through P10
human agency
workspace isolation
AI workspace isolation
Question Burst questions-only behavior
verbatim capture
post-burst AI analysis
distinct AI-generated question labeling
collaboration modes
session-state names
AI Coach modes
research-origin linkage
evidence over confidence
privacy sensitivity
AI Gateway direction
model configurability
method-library configurability
source attribution categories
MVP authentication
MVP export
MVP audit
MVP human vs AI provenance
```

The following source tensions remain visible:

```text
Inquiry Graph prototype scope
Question Burst duration
Version/Phase roadmap mapping
tenant versus workspace terminology
organization_id without organization model
active-burst AI observer/recorder semantics
```

No source tension is silently resolved.

## 36.2 LEVEL 2 validation result

**Result:** PASS WITH SOURCE-STATUS DISCIPLINE

LEVEL 2 boundary categories remain useful as reconstruction input.

01 does not promote these LEVEL 2 additions into source truth:

```text
full role-action matrix
uniform mandatory provenance field set
specific evidence lifecycle
specific export redaction policy
specific recovery mechanism
specific audit atomicity mechanism
specific direct-call gateway enforcement
```

---

# 37. Cross-Check Against 00

## 37.1 Upstream contradiction check

**Result:** NO CONTRADICTION FOUND

01 does not falsify an approved 00 fact.

Newly exposed issues refine unresolved areas rather than contradicting 00.

Specifically:

```text
Tenant/Workspace ambiguity
does not contradict 00 because 00 never equated them.

Organization relation ambiguity
does not contradict 00 because 00 did not define organization semantics.

Burst duration tension
does not contradict 00 because 00 listed the four-minute MVP anchor without closing configuration semantics.

Active-burst observer/recorder ambiguity
does not contradict 00 because 00 preserved Question Burst integrity without defining technical observation mechanics.

Roadmap mapping ambiguity
does not contradict 00 because 00 did not equate versions and phases.

Gateway enforcement gap
does not contradict 00 because 00 deferred the exact AI runtime contract.
```

## 37.2 Recursive stop condition

Not triggered.

There is no requirement to reconstruct 00 before proceeding to human review of 01.

---

# 38. New Architectural Closures Introduced in 01

Every non-source mechanism added by 01 is listed here.

| ID | Addition | Status | Trace |
|---|---|---|---|
| AC-01-001 | Product semantics remain independent of specific providers | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 model configurability + AI Gateway + 00 provider independence |
| AC-01-002 | Authentication establishes identity, not universal authority | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 auth + roles + 00 authority boundary |
| AC-01-003 | Workspace ID/UI context alone cannot establish workspace access | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 workspace isolation NFRs |
| AC-01-004 | External providers do not acquire product authority by service participation | `[ARCHITECTURAL CLOSURE]` | provider boundary + Human Decision Authority |
| AC-01-005 | Method configuration does not grant runtime authority | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 method config + 00 authority/governance separation |
| AC-01-006 | AI-derived persistence does not create consequential authority | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 human agency + 00 Human Decision Authority |
| AC-01-007 | Collaboration transport does not establish identity, authority or canonical persistence | `[ARCHITECTURAL CLOSURE]` | workspace/authority/state boundaries |
| AC-01-008 | Security enforcement constrains operations without redefining canonical semantics | `[ARCHITECTURAL CLOSURE]` | 00 one-authoritative-home + failure/state separation |
| AC-01-009 | Operational telemetry is distinct from semantic provenance | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 observability + provenance requirements |
| AC-01-010 | Visible history alone is insufficient to satisfy auditability | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 audit/recovery requirements |
| AC-01-011 | Failure in derived/external subsystem cannot silently create invalid canonical transition | `[ARCHITECTURAL CLOSURE]` | 00 recovery-valid-state + LEVEL 1 failure testing |

No domain object, state, transition, role permission or persistence schema is introduced by these closures.

---

# 39. Structural Readiness for 02

## 39.1 Stable upstream facts available to 02

01 establishes enough boundary and principle structure for 02 to begin domain and relation modeling.

Stable inputs include:

```text
full product boundary
source-defined MVP boundary anchor
identity/workspace separation
tenant/workspace ambiguity
organization relation ambiguity
authority separated from identity
Human Decision Authority
Question Burst protected boundary
human/AI distinction
AI context boundary
provider boundary
methodology boundary
evidence boundary
provenance obligation
decision boundary
research boundary
collaboration boundary
privacy/security constraints
export/audit/failure/recovery principles
P1 through P10 architecture consequences
approved 00 architectural invariants
```

## 39.2 Items 02 must preserve as unresolved

02 must not silently resolve:

```text
CONFLICT-001 Inquiry Graph prototype scope
CONFLICT-004 operation-level authority matrix
CONFLICT-005 exact mandatory provenance field set
CONFLICT-007 Burst duration semantics

GAP-01-001 Tenant versus Workspace
GAP-01-002 Organization relation
GAP-01-003 active-burst AI observer/recorder semantics
GAP-01-004 roadmap mapping
GAP-01-005 AI Gateway enforcement level
GAP-01-006 export reconstruction semantics

D1 through D10
DEC-A004 transition eligibility
DEC-A005 Question Burst enforcement mechanism
DEC-A006 recovery/rollback mechanism
DEC-A007 audit atomicity
DEC-A008 deletion versus audit retention
DEC-A009 export reconstruction format
DEC-A010 evidence validation authority
DEC-A011 RPO/RTO
DEC-A012 accessibility standard
```

## 39.3 Readiness result

**READY FOR HUMAN REVIEW**

`01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md` is structurally ready to become the approved upstream boundary/principle input for `02_DOMAIN_AND_RELATION_MODEL.md`.

02 is not yet authorized.

No file after 01 has been built.

No implementation work has begun.

No Architecture Baseline has been frozen.

---

# 40. Stop Gate

**STOP CONDITION REACHED**

Await human review and explicit:

```text
HUMAN_REVIEW::01_APPROVED
GO::BUILD_02_DOMAIN_AND_RELATION_MODEL
```
