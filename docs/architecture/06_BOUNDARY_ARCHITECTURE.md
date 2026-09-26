# 06_BOUNDARY_ARCHITECTURE

**Project:** N.Q.U.I.R.Y.  
**Document role:** Authoritative Boundary Architecture  
**Architecture stage:** G, Boundary Architecture  
**Upstream authority:** `00_NQUIRY_MASTER_ARCHITECTURE.md`, `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md`, `02_DOMAIN_AND_RELATION_MODEL.md`, `03_STATE_AND_TRANSITION_ARCHITECTURE.md`, `04_AUTHORITY_AND_DECISION_RIGHTS.md`, `05_GOVERNANCE_INSIDE_SYSTEM.md`  
**LEVEL 1 authority:** `N.Q.U.I.R.Y. - Product & System Specification`  
**LEVEL 2 input:** `# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md`  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 07 not yet authorized

---

# 0. Document Authority

This file is authoritative for:

```text
boundary composition
boundary evaluation semantics
boundary ordering
boundary allow/deny/require/escalate semantics
identity boundary contract
Workspace boundary contract
membership boundary contract
role/governance-context boundary contract
human authority boundary contract
human decision authority boundary contract
state-transition boundary contract
Question Burst contamination boundary contract
AI invocation boundary contract
AI output/canonical-state boundary contract
SYSTEM_DERIVED authority boundary contract
method approval boundary contract
evidence boundary contract
persistence/commit boundary contract
audit boundary contract
export boundary contract
failure/indeterminate boundary contract
recovery/rollback boundary contract
boundary bypass convergence requirements
commit-time revalidation requirements
```

This file is not authoritative for:

```text
domain-object identity
domain relation semantics
state topology
new state transitions
new authority classes
new human decision-right classes
methodology approval-holder selection
Export Authority assignment
evidence validation rules
provenance field schema
database schema
API schema
audit event schema
transaction implementation
recovery implementation
prototype scope
```

02 remains authoritative for domain and relations.

03 remains authoritative for state and transitions.

04 remains authoritative for authority and decision rights.

05 remains authoritative for governance operations.

06 converts those layers into enforceable control-point contracts.

---

# 1. Boundary Definition

A boundary is a system control point where a requested consequential operation is evaluated before consequence.

A boundary is not:

```text
documentation
policy prose
prompt instruction
frontend visibility
button visibility
route visibility
role label
AI confidence
logging after the fact
```

A valid boundary must be capable of preventing a request from reaching consequential state or persistence.

---

# 2. Boundary Decision Semantics

Every boundary returns exactly one semantic result:

```text
ALLOW
DENY
REQUIRE
ESCALATE
```

## 2.1 ALLOW

`ALLOW` means:

```text
this boundary has no current reason to prevent the request
```

It does not mean:

```text
the operation is authorized overall
the transition is legal overall
the operation may commit
the persistence write may occur
```

## 2.2 DENY

`DENY` is terminal for the current requested consequential operation.

A downstream boundary cannot override it.

## 2.3 REQUIRE

`REQUIRE` means a named prerequisite is missing.

The request cannot continue until that prerequisite exists and the boundary chain is evaluated again.

Examples:

```text
active membership required
HumanAuthorityBinding required
approved method version required
validated Evidence required
trusted timer predicate required
```

`REQUIRE` is not permission.

## 2.4 ESCALATE

`ESCALATE` means the unresolved condition must be routed to an explicitly authorized human or governance process.

Examples:

```text
authority reassignment
evidence interpretation
recovery reconciliation
governance root repair
```

`ESCALATE` never authorizes the requested transition.

The original consequential request remains blocked until the escalation produces the required authoritative prerequisite and the full boundary chain is rerun.

---

# 3. Boundary Composition Algebra

Boundary composition is monotonic toward restriction.

```text
upstream DENY
cannot become downstream ALLOW

upstream REQUIRE
cannot become downstream ALLOW without satisfying and re-evaluating the prerequisite

upstream ESCALATE
cannot become downstream ALLOW without completing the authorized escalation and restarting evaluation

ALLOW
only permits evaluation of the next required boundary
```

A boundary may add restrictions.

A boundary may not invent authority.

---

# 4. Canonical Consequential Request Path

A typical consequential request is evaluated through composable boundaries.

Not every operation uses every boundary.

The required subset is operation-specific.

Canonical ordering:

```text
REQUEST INGRESS
-> BND-001 IDENTITY
-> BND-002 WORKSPACE
-> BND-003 MEMBERSHIP
-> BND-004 ROLE / GOVERNANCE CONTEXT
-> BND-005 HUMAN AUTHORITY
-> BND-006 HUMAN DECISION AUTHORITY where required
-> BND-007 SESSION / STATE TRANSITION where state-sensitive
-> domain-specific boundary:
     BND-008 QUESTION BURST
     BND-009 AI INVOCATION
     BND-010 AI OUTPUT / CANONICAL STATE
     BND-011 SYSTEM_DERIVED AUTHORITY
     BND-012 METHOD APPROVAL
     BND-013 EVIDENCE
     BND-016 EXPORT
-> BND-014 PERSISTENCE / COMMIT
-> BND-015 AUDIT
-> result
```

Failure or uncertainty at any point routes through:

```text
BND-017 FAILURE / INDETERMINATE
-> BND-018 RECOVERY / ROLLBACK
```

The exact order of domain-specific boundaries may vary by operation.

Core rule:

```text
all applicable boundaries must pass
before BND-014 may permit consequential commit.
```

---

# 5. Commit-Sensitive Revalidation Rule

**[ARCHITECTURAL CLOSURE]**

An earlier `ALLOW` is never sufficient for a consequential commit.

Immediately before consequential commit, BND-014 must revalidate every commit-sensitive condition that could have changed.

At minimum:

```text
current state
current authority
current Workspace scope
current membership effectiveness
current role/governance context where relevant
HumanAuthorityBinding effectiveness
revocation status
required human decision validity
required Evidence validity
relevant governance gate
relevant method approval
SYSTEM_DERIVED derivation predicates
boundary denial status
object version / concurrency condition where required
```

Therefore:

```text
ALLOW at request time
!= COMMIT permission
```

---

# 6. Universal Boundary Bypass Rule

Every consequential execution path must converge on the same authoritative boundary semantics.

Paths include:

```text
frontend request
direct API request
service-to-service request
background worker
scheduled job
AI tool invocation
retry
event replay
recovery process
admin/governance action
direct persistence attempt
```

No transport path may own a weaker authority model.

---

# 7. BND-001 IDENTITY BOUNDARY

## BOUNDARY ID

```text
BND-001
```

## BOUNDARY PURPOSE

Establish the actor class and provable identity before any consequential authority evaluation.

Identity is necessary.

Identity is not authority.

## BOUNDARY SUBJECT

The requesting actor.

## REQUESTING ACTOR

One of:

```text
HUMAN_USER
SYSTEM_SERVICE
AI_PROCESSOR
EXTERNAL_SYSTEM
```

## CURRENT STATE

Actor identity context as presented at request time.

## REQUESTED OPERATION

Any consequential operation.

## INPUT

```text
actor identity assertion
actor class
authentication/service-auth context
request correlation
```

## IDENTITY REQUIREMENT

Human consequential mutation:

```text
authenticated User identity required
```

System consequential operation:

```text
identified trusted service identity required
```

AI operation:

```text
AI_PROCESSOR identity must remain distinguishable from HUMAN_USER and SYSTEM_SERVICE
```

External system:

```text
integration identity alone does not confer N.Q.U.I.R.Y. authority
```

## SCOPE REQUIREMENT

Identity itself has no operation scope.

Scope is resolved downstream.

## AUTHORITY REQUIREMENT

None is granted by BND-001.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF that the identity assertion is currently valid.

## PRECONDITIONS

Authentication/service identity mechanism can verify the actor.

## VALIDATION

Validate:

```text
actor class
identity validity
authentication/service credential validity
identity not revoked/expired according to later security contract
identity class not misrepresented
```

## ALLOW

Identity is valid and actor class is established.

## DENY

```text
missing identity
invalid identity
expired/revoked identity
AI presented as human
unidentified System service
external actor presented as internal System service
```

## REQUIRE

Fresh authentication/service identity proof where absent or stale.

## ESCALATE

Identity recovery may escalate to authorized account/security process.

Escalation does not authorize the requested operation.

## NEXT PERMITTED PATH

BND-002 Workspace Boundary.

## PROHIBITED PATH

```text
identity -> direct persistence
authentication -> authority
service credential -> unrestricted System authority
```

## PERSISTENCE CONSEQUENCE

None.

Identity boundary does not mutate domain state.

## AUDIT CONSEQUENCE

Security-significant identity denial may be auditable.

Exact logging policy belongs to 11.

## FAILURE BEHAVIOR

Failure denies consequential operation.

## RECOVERY / ROLLBACK DEPENDENCY

Identity recovery does not replay the denied operation automatically.

The operation must be re-requested and re-evaluated.

## TESTABLE INVARIANT

```text
No consequential human mutation can commit without a valid authenticated human identity.
No SYSTEM_DERIVED operation can commit without an identified System service.
AI_PROCESSOR can never pass as HUMAN_USER or SYSTEM_SERVICE.
```

## BYPASS PATHS

Potential bypasses:

```text
direct API with forged actor ID
background worker with no service identity
AI tool call carrying user ID
internal service trusting frontend identity field
direct DB write with no actor context
```

Prevented by:

```text
BND-001 plus BND-014
```

---

# 8. BND-002 WORKSPACE BOUNDARY

## BOUNDARY ID

```text
BND-002
```

## BOUNDARY PURPOSE

Ensure every protected consequential operation resolves to one effective Workspace and cannot cross Workspace scope.

## BOUNDARY SUBJECT

Requested object/data/process scope.

## REQUESTING ACTOR

Any actor that passed BND-001.

## CURRENT STATE

Current object ownership relations from 02.

## REQUESTED OPERATION

Any operation reading or mutating Workspace-scoped protected state.

## INPUT

```text
requested object IDs
claimed Workspace ID if supplied
resolved ownership relations
actor identity
```

## IDENTITY REQUIREMENT

BND-001 ALLOW.

## SCOPE REQUIREMENT

Every protected persisted inquiry artifact involved in the operation must resolve to exactly one effective Workspace.

Claimed Workspace IDs are not authoritative by themselves.

## AUTHORITY REQUIREMENT

None granted here.

Authority is evaluated later.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of object-to-Workspace resolution.

## PRECONDITIONS

02 ownership/relation path exists.

## VALIDATION

Validate:

```text
all objects belong to same permitted Workspace where operation requires one scope
no cross-Workspace object mixing
AI context inputs resolve to permitted Workspace
requested target scope equals authoritative relation-derived scope
```

## ALLOW

One unambiguous effective Workspace is proven.

## DENY

```text
cross-Workspace object set
unresolvable Workspace
claimed Workspace differs from authoritative scope
AI context includes another Workspace
attempt to attach one Workspace object to another Workspace's protected object
```

## REQUIRE

Resolve missing ownership relation before operation proceeds.

## ESCALATE

Structural ownership inconsistency may escalate to recovery/data-integrity process.

It does not authorize cross-scope access.

## NEXT PERMITTED PATH

BND-003 Membership Boundary for human Workspace-scoped operations.

System/AI paths continue to operation-specific authority boundaries.

## PROHIBITED PATH

```text
request.workspace_id -> trusted scope without relation validation
Owner of Workspace A -> access Workspace B
AI context aggregation across unauthorized Workspaces
```

## PERSISTENCE CONSEQUENCE

None directly.

Cross-Workspace write is denied before commit.

## AUDIT CONSEQUENCE

Cross-Workspace denial is security-relevant.

## FAILURE BEHAVIOR

Least-permissive:

```text
unresolved scope -> DENY
```

## RECOVERY / ROLLBACK DEPENDENCY

Ownership corruption routes to BND-018.

## TESTABLE INVARIANT

```text
No consequential operation can combine protected objects from different Workspaces unless a future explicit cross-Workspace architecture permits it.
```

## BYPASS PATHS

```text
frontend changes Workspace ID
direct API supplies foreign object ID
worker loads object without Workspace predicate
AI tool requests foreign object
direct DB foreign-key manipulation
replay uses stale Workspace context
```

All must converge on BND-002 before consequence.

---

# 9. BND-003 MEMBERSHIP BOUNDARY

## BOUNDARY ID

```text
BND-003
```

## BOUNDARY PURPOSE

Ensure human Workspace-scoped authority is exercised only by an active Workspace member where membership is required.

Membership is an authority precondition.

Membership is not authority.

## BOUNDARY SUBJECT

WorkspaceMembership relation.

## REQUESTING ACTOR

HUMAN_USER.

## CURRENT STATE

Current membership relation status.

## REQUESTED OPERATION

Workspace-scoped consequential operation.

## INPUT

```text
human User identity
Workspace identity
membership relation
membership effectiveness
```

## IDENTITY REQUIREMENT

Authenticated human identity.

## SCOPE REQUIREMENT

Membership must belong to the effective Workspace from BND-002.

## AUTHORITY REQUIREMENT

None granted by membership itself.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of active membership.

## PRECONDITIONS

Membership relation exists and is currently effective.

## VALIDATION

Validate:

```text
User is active member
membership belongs to exact Workspace
membership has not been revoked
membership cleanup is not INDETERMINATE
```

## ALLOW

Membership is active.

## DENY

```text
non-member
removed member
membership in different Workspace
membership revocation committed
membership state indeterminate in a way that cannot prove active status
```

## REQUIRE

Valid active membership.

## ESCALATE

Membership grant/reassignment may escalate to Workspace governance root through 05.

Original operation remains blocked.

## NEXT PERMITTED PATH

BND-004 Role / Governance Context Boundary.

## PROHIBITED PATH

```text
authenticated user -> treated as member
former member -> stale authority use
HumanAuthorityBinding -> used after membership removal
```

## PERSISTENCE CONSEQUENCE

None.

## AUDIT CONSEQUENCE

Denied removed-member attempts may be auditable.

## FAILURE BEHAVIOR

05 least-permissive uncertainty rule:

```text
uncertain membership grant -> treat as non-member
uncertain membership revoke -> treat as unavailable for new operations
```

## RECOVERY / ROLLBACK DEPENDENCY

Governance reconciliation under BND-018 / 10.

## TESTABLE INVARIANT

```text
A removed Workspace member cannot commit a Workspace-scoped consequential operation even if an older authority binding still exists in storage.
```

## BYPASS PATHS

```text
cached membership
stale token
background job created before removal
direct API with old session
binding lookup without membership check
```

BND-003 and BND-014 both revalidate membership.

---

# 10. BND-004 ROLE / GOVERNANCE CONTEXT BOUNDARY

## BOUNDARY ID

```text
BND-004
```

## BOUNDARY PURPOSE

Resolve source-explicit role rights and governance context without converting role labels into generic authority.

## BOUNDARY SUBJECT

Workspace role assignment, Session participation and FacilitatorScopeBinding where applicable.

## REQUESTING ACTOR

HUMAN_USER.

## CURRENT STATE

Current role/governance context.

## REQUESTED OPERATION

Operation whose authority semantics depend on:

```text
Facilitator
Session Participant
Workspace governance root
```

## INPUT

```text
Workspace role
SessionParticipation
FacilitatorScopeBinding
owner root relation
requested operation
target Session/Challenge/Burst
```

## IDENTITY REQUIREMENT

BND-001 ALLOW.

## SCOPE REQUIREMENT

Role/context must apply to the exact Workspace/Session scope.

## AUTHORITY REQUIREMENT

Only source-explicit rights may be derived directly from role/context.

Examples:

```text
Facilitator in Workspace:
may create Challenge

Facilitator role + ACTIVE Session FacilitatorScopeBinding:
may start/pause/resume/complete Burst in that Session

Session Participant:
may submit own Question during active Burst
```

Owner root supplies governance authority only.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of active role/context and scope.

## PRECONDITIONS

Applicable 05 governance bindings are effective.

## VALIDATION

Validate:

```text
role current
role scope current
FacilitatorScopeBinding ACTIVE where Session control uses source Facilitator right
SessionParticipation current where Question submission uses participant right
Owner root only used for governance operations
```

## ALLOW

Role/context supports the specific source-explicit operation.

## DENY

```text
Owner attempting runtime superuser operation
Facilitator outside assigned Session attempting Burst control
Contributor label used as generic submit/decision authority
Observer/Viewer mutation
role removed but stale scope binding remains
```

## REQUIRE

Correct governance context or separate HumanAuthorityBinding where operation is not role-derived.

## ESCALATE

Role/scope assignment may escalate to Workspace governance root.

Original operation remains blocked.

## NEXT PERMITTED PATH

BND-005 Human Authority Boundary when operation requires authority beyond source-explicit role right.

## PROHIBITED PATH

```text
role == Owner -> all operations
role == Facilitator -> all Session operations
role == Contributor -> selection/decision rights
```

## PERSISTENCE CONSEQUENCE

None.

## AUDIT CONSEQUENCE

Role-derived authority basis must be reconstructable for consequential operation.

## FAILURE BEHAVIOR

Uncertain role/scope:

```text
DENY
```

## RECOVERY / ROLLBACK DEPENDENCY

Governance reconciliation.

## TESTABLE INVARIANT

```text
A Facilitator cannot control a QuestionBurst in a Session lacking an ACTIVE FacilitatorScopeBinding.
A Workspace Owner cannot finalize a Decision without a separate DecisionAuthority binding.
```

## BYPASS PATHS

```text
frontend showing Facilitator controls globally
API checking only role string
service checking only owner_id
cached role after removal
AI tool invocation using Facilitator label
```

BND-004 prevents role-to-authority collapse.

---

# 11. BND-005 HUMAN AUTHORITY BOUNDARY

## BOUNDARY ID

```text
BND-005
```

## BOUNDARY PURPOSE

Validate the exact human operation authority required by 04 for the requested consequential operation.

## BOUNDARY SUBJECT

Source-explicit human right or HumanAuthorityBinding.

## REQUESTING ACTOR

HUMAN_USER.

## CURRENT STATE

Current authority/governance state.

## REQUESTED OPERATION

Any operation with an AUTH-DEP or explicit 04 authority requirement.

## INPUT

```text
actor identity
operation
scope
authority class
authority source
HumanAuthorityBinding if required
membership state
revocation state
```

## IDENTITY REQUIREMENT

Authenticated human.

## SCOPE REQUIREMENT

Authority source/binding must match exact object/Session/Challenge/Workspace scope.

No wildcard inference.

## AUTHORITY REQUIREMENT

One of:

```text
LEVEL_1_EXPLICIT
approved ARCHITECTURAL_CLOSURE
effective HumanAuthorityBinding
```

as defined in 04.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of current authority source.

## PRECONDITIONS

```text
active membership where Workspace-scoped
binding ACTIVE
binding subject matches actor
binding class matches operation
binding scope matches target
binding not revoked
governance cleanup not indeterminate
```

## VALIDATION

Validate current effectiveness using 05 predicate.

## ALLOW

Exact required authority is proven.

## DENY

```text
missing binding
wrong authority class
wrong scope
revoked binding
removed member
Owner attempting implicit override
Facilitator attempting non-source decision right
human author attempting authority from authorship
```

## REQUIRE

Named HumanAuthorityBinding where 04 requires one.

## ESCALATE

Route authority assignment/reassignment to Workspace governance root.

Original operation remains blocked.

## NEXT PERMITTED PATH

BND-006 if human decision is required.

Otherwise operation-specific BND-007 or later boundary.

## PROHIBITED PATH

```text
authentication -> authority
membership -> authority
role label -> authority
human authorship -> authority
prior ALLOW -> current authority
```

## PERSISTENCE CONSEQUENCE

None.

## AUDIT CONSEQUENCE

Authority evaluation basis must be reconstructable.

## FAILURE BEHAVIOR

Default deny.

Uncertain grant is treated as not granted.

Uncertain revocation is treated as unavailable.

## RECOVERY / ROLLBACK DEPENDENCY

Governance reconciliation and reassignment.

## TESTABLE INVARIANT

```text
No operation requiring a HumanAuthorityBinding can commit if the binding is revoked, out of scope, assigned to another User or dependent on removed membership.
```

## BYPASS PATHS

```text
direct API skips role service
worker reuses previously authorized job
cached permission
admin endpoint
AI calls operation tool with human ID
direct DB write
```

BND-005 and BND-014 must independently enforce fresh authority.

---

# 12. BND-006 HUMAN DECISION AUTHORITY BOUNDARY

## BOUNDARY ID

```text
BND-006
```

## BOUNDARY PURPOSE

Ensure a required human decision is actually created by the correct authorized human, rather than inferred from AI output, approval UI, persistence or workflow progression.

## BOUNDARY SUBJECT

Authority-bearing human decision prerequisite.

## REQUESTING ACTOR

HUMAN_USER for decision creation.

SYSTEM_SERVICE may validate an existing human decision but may not create it.

## CURRENT STATE

Relevant decision/selection/interpretation/experiment/action context.

## REQUESTED OPERATION

Operations requiring:

```text
QUESTION_SELECTION_RIGHT
ASSUMPTION_INTERPRETATION_RIGHT
EXPERIMENT_DECISION_RIGHT
DECISION_RIGHT
ACTION_DECISION_RIGHT
```

or another approved human decision prerequisite.

## INPUT

```text
human identity
authority class
scope
explicit human decision payload/reference
AI-prepared inputs if any
current object state
```

## IDENTITY REQUIREMENT

Authenticated human actor for decision creation.

## SCOPE REQUIREMENT

Decision and HumanAuthorityBinding must match the exact target scope.

## AUTHORITY REQUIREMENT

BND-005 ALLOW for the relevant human decision right.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF that the authority-bearing decision was created/adopted by the authorized human.

DOMAIN_EVIDENCE may also be required by 03/07 for specific decisions.

AI recommendation is not evidence of human decision.

## PRECONDITIONS

```text
AI preparation, if any, remains distinguishable
required human authority active
required current state permits decision
decision content is explicitly human-created or human-adopted
```

## VALIDATION

Validate:

```text
decision actor = authorized human
scope matches
decision not synthesized solely from AI output
decision timestamp/current context compatible
decision has not been invalidated/superseded under future rules
```

## ALLOW

Required authority-bearing human decision exists.

## DENY

```text
AI selected the option
AI generated the selection and system auto-accepted it
human merely viewed recommendation
UI checkbox interpreted as decision without authorized decision record
decision actor lacks right
decision is out of scope
```

## REQUIRE

Authorized human decision.

## ESCALATE

Route to correct authorized human or governance process for authority assignment.

Escalation does not create the decision.

## NEXT PERMITTED PATH

BND-007 State Transition Boundary or operation-specific boundary.

## PROHIBITED PATH

```text
AI decides -> human approves as generic token
AI recommendation -> persisted Decision DECIDED
highest score -> primary Question selection
AI experiment proposal -> Experiment AUTHORIZED
```

Correct model:

```text
AI may prepare
-> AI authority ends
-> authorized human creates required decision
-> System validates decision
-> transition may become eligible
```

## PERSISTENCE CONSEQUENCE

Human decision may be persisted only under its authoritative object/relation contract.

Its existence still does not mean downstream transition committed.

## AUDIT CONSEQUENCE

Human decision actor, authority source, scope and relation to AI inputs must be reconstructable.

## FAILURE BEHAVIOR

Missing/invalid human decision:

```text
DENY or REQUIRE
```

No AI fallback.

## RECOVERY / ROLLBACK DEPENDENCY

Recovery may restore a valid persisted human decision record.

Recovery may not fabricate one.

## TESTABLE INVARIANT

```text
No AI output can cross BND-006 as an authority-bearing human decision.
```

## BYPASS PATHS

```text
AI writes Decision row directly
background worker auto-selects recommended Question
frontend treats click on AI recommendation as implicit authorized decision without current authority check
admin database edit
event replay recreates DECIDED state without human decision provenance
```

Prevented by BND-006 and BND-014.

---

# 13. BND-007 SESSION / STATE TRANSITION BOUNDARY

## BOUNDARY ID

```text
BND-007
```

## BOUNDARY PURPOSE

Enforce the 03 state topology, current-state requirements, legal transition path and transition preconditions.

## BOUNDARY SUBJECT

State-owning object/process.

## REQUESTING ACTOR

Human or System actor already passing required authority boundaries.

## CURRENT STATE

Authoritative current state from 03 owner.

## REQUESTED OPERATION

One specific 03 transition or state-preserving consequential mutation.

## INPUT

```text
object identity
current state
requested transition
required relation state
required cross-object states
03 preconditions
```

## IDENTITY REQUIREMENT

Applicable identity boundary passed.

## SCOPE REQUIREMENT

All state-owning objects belong to valid same operation scope.

## AUTHORITY REQUIREMENT

04 authority requirement already satisfied or deferred to BND-005/BND-006.

BND-007 does not invent authority.

## EVIDENCE REQUIREMENT

03 `SYSTEM_PROOF`, and `DOMAIN_EVIDENCE` only where 03 requires it.

## PRECONDITIONS

Exactly those defined in 03.

## VALIDATION

Validate:

```text
current state exact
requested transition legal
no state skip
cross-object state invariant valid
no unresolved INDETERMINATE predecessor
required structural proof present
```

## ALLOW

Transition is state-eligible.

## DENY

```text
illegal source state
illegal target path
state skip
CLOSED Session reopening
QuestionBurst ACTIVE while Session ANALYSIS
Experiment start before AUTHORIZED
Decision DECIDED without valid path
```

## REQUIRE

Named missing 03 precondition.

## ESCALATE

State corruption or indeterminate prior transition routes to recovery.

It does not authorize target transition.

## NEXT PERMITTED PATH

Relevant domain-specific boundary then BND-014.

## PROHIBITED PATH

```text
UI navigation -> state
event occurrence -> state
database state field edit -> valid transition
role label -> state change
```

## PERSISTENCE CONSEQUENCE

None yet.

Transition remains proposed until BND-014 commit.

## AUDIT CONSEQUENCE

Requested transition and state eligibility result must be correlatable to final audit.

## FAILURE BEHAVIOR

03 outcome discipline applies.

## RECOVERY / ROLLBACK DEPENDENCY

BND-017/018 for state uncertainty.

## TESTABLE INVARIANT

```text
No object can reach a 03-illegal state through any transport or persistence path.
```

## BYPASS PATHS

```text
direct state-update API
ORM save of state field
worker progression
event consumer projection writing state
replay
manual admin mutation
```

All must pass BND-007 and BND-014.

---

# 14. BND-008 QUESTION BURST CONTAMINATION BOUNDARY

## BOUNDARY ID

```text
BND-008
```

## BOUNDARY PURPOSE

Protect the raw Question Burst from answers, explanations, silent AI contamination, mutation and premature AI analysis.

## BOUNDARY SUBJECT

QuestionBurst, raw Question capture membership and AI operations touching Burst context.

## REQUESTING ACTOR

HUMAN_USER, SYSTEM_SERVICE or AI_PROCESSOR depending requested operation.

## CURRENT STATE

QuestionBurst:

```text
PREPARED
ACTIVE
PAUSED
COMPLETED
```

and Session state from 03.

## REQUESTED OPERATION

Examples:

```text
START_BURST
CAPTURE_BURST_QUESTION
PAUSE_BURST
RESUME_BURST
COMPLETE_BURST
AI_ANALYSIS
REFRAME
CLASSIFY
CLUSTER
GENERATE_QUESTION
```

## INPUT

```text
Burst state
Session state
Burst mode
input text
actor origin
Question origin
capture membership
AI operation type
```

## IDENTITY REQUIREMENT

Human submission requires authenticated Session Participant.

System timer path requires identified System service.

AI must remain AI_PROCESSOR.

## SCOPE REQUIREMENT

Exact Session/Burst/Workspace scope.

## AUTHORITY REQUIREMENT

Use 04 rights:

```text
Facilitator Session scope for Burst control
Session Participant right for own Question submission
SYSTEM_DERIVED only where permitted
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of Burst state, actor context, capture membership and mode.

## PRECONDITIONS

During protected Human-only ACTIVE Burst:

```text
questions only
no discussion
no answers
no explanations
verbatim capture
no AI analysis
no AI evaluation
no AI reframing
no AI question generation
```

## VALIDATION

Validate operation category against current Burst state and mode.

For CAPTURE_BURST_QUESTION:

```text
input must satisfy BURST_INPUT_VALID
```

Exact source-compatible validator remains `GAP-03-003`.

## ALLOW

During ACTIVE Human-only Burst:

```text
valid human Question capture
Facilitator pause/end
trusted permitted System timer path when closed
non-semantic recording required to preserve input
```

After COMPLETED/frozen:

```text
post-Burst AI analysis may become eligible
```

subject to BND-009/BND-010.

## DENY

During ACTIVE protected Human-only Burst:

```text
answer generation
explanation generation
question evaluation
classification
clustering
reframing
AI question generation
AI moderation unless explicitly enabled by future source-authorized mode
mutation of already captured original_text
"allowed raw" non-question semantics
```

After COMPLETED:

```text
new raw-set membership
raw Question mutation
```

## REQUIRE

If BURST_INPUT_VALID cannot be established by a source-compatible mechanism:

```text
REQUIRE compliant validation mechanism
```

If AI observer/recorder semantics require model processing:

```text
REQUIRE resolution of GAP-01-003 before model call
```

## ESCALATE

Methodology ambiguity may escalate only to authorized methodology governance once D8 resolves.

No current escalation may weaken protected Burst rules.

## NEXT PERMITTED PATH

Question capture -> BND-014.

Post-Burst AI -> BND-009.

## PROHIBITED PATH

```text
AI tool invoked directly during ACTIVE Burst
raw Question text sent to evaluator model to decide quality
client bypass posts answer as raw accepted content
worker performs clustering before freeze
replay adds Question to completed raw set
```

## PERSISTENCE CONSEQUENCE

Captured human Question must preserve immutable `original_text`.

Raw membership freeze becomes effective at completed Burst commit.

## AUDIT CONSEQUENCE

Capture origin, author, timestamp and Burst membership must remain reconstructable.

## FAILURE BEHAVIOR

Capture uncertainty blocks Burst completion.

Contamination detection denies affected operation.

No auto-clean/rewrite of human input.

## RECOVERY / ROLLBACK DEPENDENCY

Recovery must preserve accepted verbatim Questions and raw-set integrity.

## TESTABLE INVARIANT

```text
No AI analysis/evaluation/reframe/generation can affect the protected raw Human-only Burst before valid completion and freeze.
No Question accepted into the raw set can have original_text silently rewritten.
```

## BYPASS PATHS

```text
direct AI provider call
background cluster worker
AI tool callback
frontend local analysis
direct DB insert of AI Question into raw membership
event consumer adding cluster during ACTIVE
retry of late Question after COMPLETED
recovery replay adding Question twice
```

Boundaries BND-008, BND-009, BND-010, BND-014 and BND-018 must converge.

---

# 15. BND-009 AI INVOCATION BOUNDARY

## BOUNDARY ID

```text
BND-009
```

## BOUNDARY PURPOSE

Ensure every LLM/model invocation occurs through the approved AI Gateway context and only when current state, scope, mode and authority permit the operation.

## BOUNDARY SUBJECT

AI operation request.

## REQUESTING ACTOR

HUMAN_USER or SYSTEM_SERVICE.

AI_PROCESSOR may not self-authorize a new invocation.

## CURRENT STATE

Relevant Session/Burst/domain state.

## REQUESTED OPERATION

One specific AI operation:

```text
classification
clustering
reframing
assumption detection
question generation
reflection support
experiment proposal
research support
other source-permitted AI operation
```

## INPUT

```text
operation type
Workspace context
allowed object IDs
current state
method/mode
input context selection
requesting authority context
```

## IDENTITY REQUIREMENT

Valid requesting actor identity.

AI provider identity is external execution context, not authority.

## SCOPE REQUIREMENT

AI context restricted to authorized Workspace and operation-relevant objects.

## AUTHORITY REQUIREMENT

Operation invocation must be authorized by applicable human/System path.

AI does not authorize its own call.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
allowed state
allowed Workspace context
permitted operation
required human/System authority
QuestionBurst completion where post-Burst analysis
```

## PRECONDITIONS

All LLM traffic passes through internal AI Gateway abstraction.

## VALIDATION

Validate:

```text
operation permitted in current state
input objects in scope
no unauthorized Workspace data
method/mode permits operation
AI Gateway policy permits tools/provider/context
no direct provider bypass
```

## ALLOW

Bounded invocation through AI Gateway.

## DENY

```text
direct application-to-provider call
AI self-invocation without authority
analysis during protected ACTIVE Human-only Burst
cross-Workspace context
forbidden tool access
operation not allowed in current state/mode
```

## REQUIRE

Required:

```text
approved context
operation contract
provider route
method/mode prerequisite
```

Where SYSTEM_DERIVED authority is used, BND-011 and potentially BND-012 must also ALLOW.

## ESCALATE

No AI invocation escalation grants permission.

Missing authority goes to governance/human path.

## NEXT PERMITTED PATH

AI provider execution then BND-010 for returned output.

## PROHIBITED PATH

```text
direct SDK call bypassing gateway
model tool calls internal API directly without boundary
background worker calls provider with stale context
developer/admin script writes model output into canonical tables
```

## PERSISTENCE CONSEQUENCE

Invocation itself does not create canonical domain consequence.

AIGeneration operational record may later persist under 08/09.

## AUDIT CONSEQUENCE

AI operation, model/provider route, scope and authority basis must be observable/reconstructable under 08/11 requirements.

## FAILURE BEHAVIOR

Provider failure does not advance state.

AI invocation failure cannot create authority fallback.

## RECOVERY / ROLLBACK DEPENDENCY

08/10 retry behavior.

If duplicate consequence is possible, retry must pass BND-017 first.

## TESTABLE INVARIANT

```text
No LLM invocation can access unauthorized Workspace context or bypass the AI Gateway and still produce accepted N.Q.U.I.R.Y. consequential output.
```

## BYPASS PATHS

```text
direct provider SDK
AI tool invocation
worker
server action
admin script
fallback provider
retry path
```

All require BND-009.

---

# 16. BND-010 AI OUTPUT / CANONICAL STATE BOUNDARY

> **Post-baseline materialization note (2026-09-25, F04 WU-04.0):** in F04 the
> accepted derived output is written only by a separate acceptance Command
> (`CMD_ACCEPT_QUESTION_ANALYSIS_OUTPUT`, `CMD_ACCEPT_CLUSTERING_OUTPUT`; 09 §68),
> actor SYSTEM_SERVICE, effect-gate source **SYSTEM_OPERATION** (**HD-17**,
> 16 §41 REC-019 / NQ-DEC-045). BND-010 runs before BND-014 on the validated
> candidate; the generation's VALIDATED status, the persisted
> AI_VALIDATION_PROOF (09 §56) and the accepted artifact are committed in one
> atomic bundle (F04 pre-implementation binding PI-1). The AI Gateway never
> persists an artifact itself (FBR-F04-1/2). Nothing below is rewritten.

## BOUNDARY ID

```text
BND-010
```

## BOUNDARY PURPOSE

Prevent AI output from becoming human-authoritative, evidentiary or canonical consequence merely because it was generated, validated or persisted.

## BOUNDARY SUBJECT

AI-generated or AI-inferred output.

## REQUESTING ACTOR

SYSTEM_SERVICE attempting to accept/persist AI output.

AI_PROCESSOR supplies output but is not acceptance authority.

## CURRENT STATE

Relevant domain/process state.

## REQUESTED OPERATION

Examples:

```text
persist derived classification
persist QuestionCluster
persist AI-generated Question
persist inferred Assumption
persist AI-derived Insight
apply reframe
advance Session
select Question
authorize Experiment
finalize Decision
classify Assumption evidence state
```

## INPUT

```text
AI output
operation contract
source nodes
origin/derivation semantics
current state
target object type
```

## IDENTITY REQUIREMENT

Identified AI generation and accepting System service.

## SCOPE REQUIREMENT

Output source and target resolve to same permitted Workspace context.

## AUTHORITY REQUIREMENT

AI has no human decision authority.

Persistence of derived output requires only the bounded AI operation acceptance authority defined later in 08/09.

Any human-authoritative consequence requires separate BND-006.

## EVIDENCE REQUIREMENT

AI_VALIDATION_PROOF for schema/contract validity.

AI confidence is not DOMAIN_EVIDENCE.

## PRECONDITIONS

Output contract permits the specific derived artifact.

## VALIDATION

Validate:

```text
output type permitted
origin/derivation distinguishable
source Question original_text not mutated
human authorship not fabricated
AI output not presented as Evidence merely from confidence
target state not advanced implicitly
```

## ALLOW

Only the bounded derived artifact accepted by the AI contract.

Examples:

```text
derived classification
QuestionCluster
AI reframe as new Question identity + lineage
inferred Assumption in UNKNOWN
AI proposal
```

## DENY

```text
AI output -> Decision DECIDED
AI output -> Experiment AUTHORIZED
AI output -> QuestionSelection
AI confidence -> Assumption SUPPORTED/REFUTED
AI output -> Session state advance
AI reframe -> overwrite original Question
AI output -> method approval
AI output -> governance mutation
```

## REQUIRE

For human-authoritative effect:

```text
REQUIRE BND-006 authorized human decision
```

For evidentiary effect:

```text
REQUIRE BND-013 evidence path and later 07 validation
```

## ESCALATE

AI recommendation may be routed to an authorized human for consideration.

Escalation ends AI authority.

The human must create a new authority-bearing decision under BND-006.

## NEXT PERMITTED PATH

Derived persistence -> BND-014.

Human adoption -> BND-006 then downstream path.

## PROHIBITED PATH

```text
AI output inserted directly into authoritative Decision/Selection/Authorization field
worker auto-applies top recommendation
event handler treats AI_ANALYSIS_COMPLETED as Session transition
```

## PERSISTENCE CONSEQUENCE

Only permitted derived state may be written.

Canonical persistence still does not imply epistemic truth.

## AUDIT CONSEQUENCE

AI origin, operation and target lineage must remain reconstructable.

## FAILURE BEHAVIOR

Invalid output:

```text
DENY persistence
```

No repair path may silently change human source content.

## RECOVERY / ROLLBACK DEPENDENCY

Invalid/partial AI writes handled by 10.

## TESTABLE INVARIANT

```text
Persisting a valid AI output can never, by itself, create an authority-bearing human decision or a 03 state transition.
```

## BYPASS PATHS

```text
direct DB write
ORM callback
AI tool mutates domain object
worker auto-applies result
event subscriber copies AI recommendation into Decision
recovery reconstructs derived state as human state
```

BND-010 and BND-014 prevent consequence.

---

# 17. BND-011 SYSTEM_DERIVED AUTHORITY BOUNDARY

## BOUNDARY ID

```text
BND-011
```

## BOUNDARY PURPOSE

Reconstruct bounded System authority from current predicates for one operation instance only.

## BOUNDARY SUBJECT

One SYSTEM_DERIVED operation instance.

## REQUESTING ACTOR

SYSTEM_SERVICE.

## CURRENT STATE

Current authoritative system/governance state.

## REQUESTED OPERATION

Only operations explicitly permitted by 04/05 as SYSTEM_DERIVED.

Current examples:

```text
trusted timer Burst completion
Begin Analysis under approved deterministic method
Begin Reflection under approved deterministic method plus valid analysis proof
procedural commit after successful human authority validation
governance cleanup after valid membership/role revocation
```

## INPUT

```text
service identity
operation
scope
current state
derivation predicates
method version where applicable
timer proof where applicable
human authority result where applicable
```

## IDENTITY REQUIREMENT

Identified trusted SYSTEM_SERVICE.

AI_PROCESSOR cannot satisfy this identity class.

## SCOPE REQUIREMENT

Exact operation/object scope.

## AUTHORITY REQUIREMENT

Every current derivation predicate from 04/05 must be true now.

No reusable System permission.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of each derivation predicate.

## PRECONDITIONS

No unresolved discretionary human decision is being substituted.

## VALIDATION

Recompute predicates from authoritative current data.

Do not trust cached prior derivation.

## ALLOW

One operation-instance SYSTEM_DERIVED authority exists.

## DENY

```text
stale derivation
service identity invalid
required human decision missing
method not approved
timer trust unresolved
state changed
scope changed
AI is actual requesting authority
```

## REQUIRE

Named missing predicate.

Examples:

```text
approved method
trusted timer
valid analysis proof
fresh human authority result
```

## ESCALATE

Missing human decision/authority routes to appropriate human/governance process.

System does not self-promote.

## NEXT PERMITTED PATH

BND-007 / operation-specific boundary / BND-014.

## PROHIBITED PATH

```text
cache SYSTEM_DERIVED authority as token
reuse authority on another object
reuse after state change
AI output decides derivation
client timer asserts trusted expiry
```

## PERSISTENCE CONSEQUENCE

None before BND-014.

## AUDIT CONSEQUENCE

Derivation basis for consequential System operation must be reconstructable.

## FAILURE BEHAVIOR

Missing/uncertain predicate:

```text
DENY or REQUIRE
```

## RECOVERY / ROLLBACK DEPENDENCY

Retry must recompute from current predicates.

## TESTABLE INVARIANT

```text
SYSTEM_DERIVED authority cannot survive a change to any predicate on which it depends.
```

## BYPASS PATHS

```text
scheduled worker with stale job payload
cached service permission
client callback
AI tool masquerading as System service
replay triggering old System action
```

BND-011 plus BND-014 revalidation prevents consequence.

---

# 18. BND-012 METHOD APPROVAL BOUNDARY

## BOUNDARY ID

```text
BND-012
```

## BOUNDARY PURPOSE

Prevent configured methodology from acquiring authority merely because configuration exists.

## BOUNDARY SUBJECT

One InquiryMethod version used as authority predicate.

## REQUESTING ACTOR

SYSTEM_SERVICE or HUMAN_USER requesting method-dependent operation.

## CURRENT STATE

Method configuration/version and approval status.

## REQUESTED OPERATION

Any operation whose authority derives from an approved method.

Current high-assurance focus:

```text
automatic Begin Analysis
automatic Begin Reflection
other future method-triggered SYSTEM_DERIVED operations
```

## INPUT

```text
method identifier
method version
method configuration
approval reference if any
requested operation
```

## IDENTITY REQUIREMENT

Requesting actor already identified.

## SCOPE REQUIREMENT

Method version must be the exact configuration used by the operation.

## AUTHORITY REQUIREMENT

Method Approval Authority remains unresolved under D8.

Therefore current approved authority source cannot be proven unless D8 is resolved later.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of exact method version plus valid approval once available.

## PRECONDITIONS

Method version identity must be stable enough to distinguish approved from modified configuration.

## VALIDATION

Current architecture checks:

```text
is exact method version identifiable?
does an authoritative approval exist?
is approval still effective?
does approval cover this operation?
```

## ALLOW

Only if future D8 resolution provides a valid approval authority and exact approval exists.

## DENY

```text
configuration exists but no approval
method modified after approval
AI-generated method configuration presented as approved
System assumes deployment == approval
```

## REQUIRE

```text
D8 Method Approval Authority resolution
exact approved method version
```

## ESCALATE

Route to future authorized Method Approval governance process.

Until D8 resolves, escalation cannot complete.

## NEXT PERMITTED PATH

BND-011 SYSTEM_DERIVED Authority Boundary.

Manual human paths independent of method-derived System authority may continue through their own boundaries where 03/04 permit.

## PROHIBITED PATH

```text
configured method -> authority
default method -> approved
deployment -> approval
AI recommendation -> method approval
```

## PERSISTENCE CONSEQUENCE

None.

## AUDIT CONSEQUENCE

Future method approval/withdrawal must be auditable.

## FAILURE BEHAVIOR

Fail closed.

## RECOVERY / ROLLBACK DEPENDENCY

Method approval corruption requires governance reconciliation.

## TESTABLE INVARIANT

```text
An unapproved InquiryMethod can never activate SYSTEM_DERIVED consequential authority.
```

## BYPASS PATHS

```text
hard-coded default method
configuration file flag
frontend method selector
worker assumes named method approved
AI prompt includes method name
```

BND-012 denies authority implication.

---

# 19. BND-013 EVIDENCE BOUNDARY

## BOUNDARY ID

```text
BND-013
```

## BOUNDARY PURPOSE

Prevent non-evidence signals from satisfying a transition or human decision that requires DOMAIN_EVIDENCE.

## BOUNDARY SUBJECT

Evidence prerequisite for a consequential operation.

## REQUESTING ACTOR

HUMAN_USER or SYSTEM_SERVICE validating a request.

## CURRENT STATE

Current Evidence relations and later 07 validation status.

## REQUESTED OPERATION

Any 03/04 operation with DOMAIN_EVIDENCE requirement.

Examples may include:

```text
Assumption classification
Decision finalization where evidence is required
Experiment authorization where evidence is required
```

## INPUT

```text
Evidence objects
source references
reliability/validation information
target object
requested consequence
AI summaries
```

## IDENTITY REQUIREMENT

Applicable actor identity already passed.

## SCOPE REQUIREMENT

Evidence must resolve to the same permitted Workspace context.

Exact ownership/multi-target semantics remain 07/09 dependencies.

## AUTHORITY REQUIREMENT

Evidence validation authority must be defined by 07/04 coordination.

06 does not invent it.

## EVIDENCE REQUIREMENT

The boundary itself evaluates whether the named DOMAIN_EVIDENCE prerequisite can be proven.

## PRECONDITIONS

07 must define:

```text
validation semantics
sufficiency
contradiction handling
authority for validation
```

where the operation depends on them.

## VALIDATION

At minimum reject substitution of:

```text
AI confidence
AI classification
AI inference
raw user assertion
imported source with no required source metadata
```

for validated DOMAIN_EVIDENCE where validation is required.

## ALLOW

Required Evidence condition is valid under 07 rules.

## DENY

Known invalid/out-of-scope Evidence or prohibited substitution.

## REQUIRE

If evidence policy/validation required by the operation is not yet closed:

```text
REQUIRE validated Evidence or 07 rule
```

## ESCALATE

Evidence interpretation may escalate only to the authorized human/evidence governance process later defined.

Escalation does not satisfy Evidence automatically.

## NEXT PERMITTED PATH

BND-014 after all other boundaries pass.

## PROHIBITED PATH

```text
high AI confidence -> Evidence
model citation -> validated Evidence automatically
user statement -> validated Evidence automatically
```

## PERSISTENCE CONSEQUENCE

None directly.

## AUDIT CONSEQUENCE

Evidence references used for consequential decision/transition must be reconstructable.

## FAILURE BEHAVIOR

Fail closed when Evidence is required and validity cannot be proven.

## RECOVERY / ROLLBACK DEPENDENCY

Evidence corruption/inconsistency routes to BND-018.

## TESTABLE INVARIANT

```text
No consequential operation requiring DOMAIN_EVIDENCE can commit using AI confidence as the evidentiary substitute.
```

## BYPASS PATHS

```text
AI output carries confidence
frontend marks Evidence as accepted
direct DB sets reliability
worker auto-classifies Assumption
replay restores old Evidence status without validation context
```

BND-013 plus future 07/09 contracts prevent consequence.

---

# 20. BND-014 PERSISTENCE / COMMIT BOUNDARY

## BOUNDARY ID

```text
BND-014
```

## BOUNDARY PURPOSE

Serve as the final authority-sensitive control point before any consequential canonical persistence or transition commit.

This is the critical commit boundary.

## BOUNDARY SUBJECT

One proposed consequential commit.

## REQUESTING ACTOR

SYSTEM_SERVICE executing a validated human/System request.

AI_PROCESSOR cannot own commit authority.

## CURRENT STATE

Fresh authoritative current state at commit time.

## REQUESTED OPERATION

Any consequential canonical mutation.

Examples:

```text
create Challenge
change Session state
start/complete Burst
capture Question
create selection
change Assumption state
authorize/start/complete Experiment
finalize Decision
governance grant/revoke
persist accepted AI-derived artifact
export generation start
```

## INPUT

```text
operation
actor identity
scope
current state
authority source
binding references
membership state
governance state
human decision reference where required
Evidence references where required
method approval where required
SYSTEM_DERIVED predicates where required
all upstream boundary results
correlation/request identity
```

## IDENTITY REQUIREMENT

Freshly resolvable actor/service identity.

## SCOPE REQUIREMENT

Fresh BND-002 scope resolution.

## AUTHORITY REQUIREMENT

Fresh authority evaluation.

No stale ALLOW.

## EVIDENCE REQUIREMENT

Fresh validation of required SYSTEM_PROOF and DOMAIN_EVIDENCE.

## PRECONDITIONS

Every applicable upstream boundary currently allows.

No upstream DENY/REQUIRE/ESCALATE remains unresolved.

## VALIDATION

Immediately before commit revalidate at minimum:

```text
current state
current authority
current scope
binding effectiveness
membership effectiveness
revocation status
required human decision
required Evidence validity
relevant governance gate
relevant method approval
SYSTEM_DERIVED predicates
boundary denial status
concurrency/object version where implementation requires
```

## ALLOW

Only when every commit-sensitive predicate is currently valid.

This ALLOW authorizes one commit attempt for the current operation instance.

## DENY

Any changed/failed predicate.

Examples:

```text
binding revoked after earlier ALLOW
member removed after request
state advanced by competing operation
method approval withdrawn
Evidence invalidated
Workspace scope changed
human decision no longer valid under future supersession rule
```

## REQUIRE

Named missing current prerequisite.

No commit occurs.

## ESCALATE

Indeterminate prior outcome routes to BND-017/018.

Governance gap routes to authorized governance process.

## NEXT PERMITTED PATH

Persistence mechanism plus BND-015 audit consistency.

Exact transaction ordering belongs to 09/10.

## PROHIBITED PATH

```text
direct DB write bypassing boundaries
ORM save of state field
background worker using stale ALLOW
cached authorization token as commit authority
event replay as command
admin SQL mutation
AI tool direct persistence
```

## PERSISTENCE CONSEQUENCE

If commit succeeds:

```text
03 COMMITTED
```

or corresponding 05 governance COMMITTED outcome.

If commit cannot be proven:

```text
INDETERMINATE
```

## AUDIT CONSEQUENCE

Commit must correlate to an auditable request/authority/transition context.

Exact audit atomicity remains unresolved.

## FAILURE BEHAVIOR

```text
precommit failure -> FAILED_PRECOMMIT
uncertain commit -> INDETERMINATE
known no-commit -> state unchanged
```

## RECOVERY / ROLLBACK DEPENDENCY

BND-017 and BND-018.

## TESTABLE INVARIANT

```text
No consequential persistence can commit solely from an earlier ALLOW or from direct write access.
Every commit uses fresh current-state, scope and authority revalidation.
```

## BYPASS PATHS

All listed universal bypass paths converge here.

This includes:

```text
frontend
API
service-to-service
worker
scheduler
AI tool
retry
replay
recovery
admin/governance operation
direct persistence attempt
```

---

# 21. AC-06-001 Commit Permit Is Ephemeral

**[ARCHITECTURAL CLOSURE]**

BND-014 approval exists only for:

```text
one operation
one correlation context
one current-state snapshot/revalidation point
one commit attempt
```

It is not a reusable permission.

If the commit does not occur within the current validated operation context, the boundary chain must be reevaluated.

No persistent "commit token" is defined here.

---

# 22. BND-015 AUDIT BOUNDARY

## BOUNDARY ID

```text
BND-015
```

## BOUNDARY PURPOSE

Ensure consequential state/governance effects remain reconstructable without allowing audit events to become commands or authority.

## BOUNDARY SUBJECT

Consequential operation audit consequence.

## REQUESTING ACTOR

SYSTEM_SERVICE responsible for commit/audit recording.

## CURRENT STATE

Requested operation outcome and audit subsystem availability/status.

## REQUESTED OPERATION

Record or correlate audit consequence.

## INPUT

At minimum semantic access to:

```text
actor identity
actor type
operation
scope
authority source
human decision reference where required
current/prior state
target/new state where applicable
boundary result
commit result
correlation ID
```

## IDENTITY REQUIREMENT

Identified System service.

## SCOPE REQUIREMENT

Audit record scope must match consequential operation scope.

## AUTHORITY REQUIREMENT

Audit recording is procedural System behavior.

Audit event itself grants no authority.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of operation correlation.

## PRECONDITIONS

Operation/audit correlation exists.

## VALIDATION

Validate:

```text
audit references correct operation
audit cannot mutate domain state
event replay is not treated as a new command
before/after semantics do not fabricate state
```

## ALLOW

Audit consequence may be recorded/correlated.

## DENY

```text
audit event used to authorize operation
event payload attempts canonical mutation
uncorrelated audit record presented as transition proof
```

## REQUIRE

Auditability capability required for consequential operation.

Exact atomicity mechanism remains `GAP-03-016`.

## ESCALATE

Audit subsystem inconsistency routes to BND-017/018.

## NEXT PERMITTED PATH

Successful operation finalization or failure/recovery path.

## PROHIBITED PATH

```text
event emitted -> state changed
event replay -> operation executed again
audit log edit -> canonical state edit
```

## PERSISTENCE CONSEQUENCE

Audit persistence itself is non-domain event persistence.

## AUDIT CONSEQUENCE

Self-evident: audit chain must be reconstructable.

## FAILURE BEHAVIOR

If audit failure occurs before domain commit and commit can be prevented:

```text
FAILED_PRECOMMIT
```

If domain/audit consistency cannot be proven:

```text
INDETERMINATE
```

06 does not choose an atomicity implementation.

## RECOVERY / ROLLBACK DEPENDENCY

10 must reconcile state/audit consistency.

## TESTABLE INVARIANT

```text
An audit event can record a transition but can never cause or authorize that transition.
```

## BYPASS PATHS

```text
event replay
event consumer side effect
manual audit insertion
recovery from event log
notification handler
analytics pipeline
```

Any path causing consequence must re-enter normal boundaries.

---

# 23. BND-016 EXPORT BOUNDARY

## BOUNDARY ID

```text
BND-016
```

## BOUNDARY PURPOSE

Structurally govern Export without inventing unresolved Export Authority.

## BOUNDARY SUBJECT

Export request and requested export scope.

## REQUESTING ACTOR

HUMAN_USER.

## CURRENT STATE

Current Workspace/data scope and governance state.

## REQUESTED OPERATION

```text
CREATE_EXPORT
```

or equivalent export operation.

## INPUT

```text
actor
Workspace/Challenge/Session scope
requested object classes
requested format
redaction/content policy when later defined
```

## IDENTITY REQUIREMENT

Authenticated human.

## SCOPE REQUIREMENT

All requested data must resolve to authorized Workspace scope.

## AUTHORITY REQUIREMENT

`GAP-04-013 Export Authority` remains OPEN.

Therefore current authority cannot be proven.

## EVIDENCE REQUIREMENT

Future SYSTEM_PROOF of explicit export authority.

## PRECONDITIONS

Future:

```text
Export Authority resolved in 04
export content scope defined
privacy/redaction policy defined
```

## VALIDATION

Current architecture validates that authority remains unresolved.

## ALLOW

Not currently reachable.

## DENY

Export execution while Export Authority is unresolved.

## REQUIRE

```text
authoritative Export Authority closure
defined export scope/content policy
```

## ESCALATE

Route to architecture/governance resolution.

No role fallback.

## NEXT PERMITTED PATH

None until prerequisite is closed.

Future path will proceed to BND-014.

## PROHIBITED PATH

```text
Owner fallback
Facilitator fallback
download button
direct API export
admin export
background export job
AI-generated export
```

## PERSISTENCE CONSEQUENCE

No export artifact generation while unresolved.

## AUDIT CONSEQUENCE

Denied export attempts may be security-audited.

## FAILURE BEHAVIOR

Fail closed.

## RECOVERY / ROLLBACK DEPENDENCY

Not applicable until authority is resolved.

## TESTABLE INVARIANT

```text
No user, including Workspace Owner or Facilitator, can currently execute Export solely from role status.
```

## BYPASS PATHS

All export-producing transports must hit BND-016.

## BASELINE STATUS

```text
BASELINE BLOCKER
```

because Export is LEVEL 1 MVP scope.

---

# 24. BND-017 FAILURE / INDETERMINATE BOUNDARY

## BOUNDARY ID

```text
BND-017
```

## BOUNDARY PURPOSE

Contain uncertain or failed consequential operations so uncertainty cannot create permission, duplicate consequence or downstream state.

## BOUNDARY SUBJECT

Failed or uncertain operation.

## REQUESTING ACTOR

SYSTEM_SERVICE handling failure path.

## CURRENT STATE

Last provably confirmed state plus operation outcome information.

## REQUESTED OPERATION

Examples:

```text
retry
continue dependent workflow
assume commit
assume rollback
emit compensating mutation
```

## INPUT

```text
operation correlation
known prior state
commit acknowledgement
persistence outcome
audit outcome
authority state at attempt
failure information
```

## IDENTITY REQUIREMENT

Identified System recovery/failure service.

## SCOPE REQUIREMENT

Exact failed operation scope.

## AUTHORITY REQUIREMENT

Failure handling itself cannot create new human authority.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of known outcome where available.

## PRECONDITIONS

Classify outcome as:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

## VALIDATION

Determine whether prior consequence is provably absent, present or uncertain.

## ALLOW

```text
known FAILED_PRECOMMIT -> safe re-request may be possible after full boundary reevaluation
known COMMITTED -> do not repeat consequence
```

## DENY

```text
dependent consequential operation after INDETERMINATE
blind retry when duplicate consequence is possible
assume rollback without proof
assume commit without proof
```

## REQUIRE

Recovery/reconciliation for INDETERMINATE.

## ESCALATE

To BND-018 recovery/reconciliation.

Where discretionary human choice is required, route to explicitly authorized human/governance process.

## NEXT PERMITTED PATH

BND-018 or fresh full boundary chain after safe failure resolution.

## PROHIBITED PATH

```text
retry immediately after unknown commit
continue workflow because request timed out
duplicate Question capture
duplicate Decision finalization
duplicate governance grant
```

## PERSISTENCE CONSEQUENCE

No new consequential persistence while INDETERMINATE.

Failure evidence may be preserved.

## AUDIT CONSEQUENCE

Failure and uncertainty must be auditable.

## FAILURE BEHAVIOR

Least-permissive.

## RECOVERY / ROLLBACK DEPENDENCY

BND-018.

## TESTABLE INVARIANT

```text
An INDETERMINATE consequential operation blocks every dependent consequence until reconciliation establishes the last valid state.
```

## BYPASS PATHS

```text
automatic retry library
queue redelivery
HTTP client retry
worker restart
event consumer retry
user double-submit
recovery script
```

All retries with possible duplicate consequence must pass BND-017.

---

# 25. BND-018 RECOVERY / ROLLBACK BOUNDARY

## BOUNDARY ID

```text
BND-018
```

## BOUNDARY PURPOSE

Ensure recovery restores or reconciles only architecture-valid state and cannot bypass normal authority, scope, immutability or audit semantics.

## BOUNDARY SUBJECT

Indeterminate/failed state or governance condition requiring reconciliation.

## REQUESTING ACTOR

SYSTEM_SERVICE for deterministic reconciliation.

HUMAN_USER only where 10 later defines a discretionary recovery decision with valid authority.

## CURRENT STATE

Last provably valid state plus uncertain artifacts.

## REQUESTED OPERATION

Examples:

```text
reconcile commit
restore last valid state
complete interrupted logical bundle
roll back partial uncommitted effect
replay reconstruction
reassign authority after revocation
```

## INPUT

```text
failure correlation
known persistence facts
audit facts
state facts
authority facts
scope facts
idempotency/replay evidence
```

## IDENTITY REQUIREMENT

Identified recovery System service or future authorized human recovery actor.

## SCOPE REQUIREMENT

Recovery scope must match the failed operation scope.

## AUTHORITY REQUIREMENT

Recovery cannot invent a new domain decision.

Deterministic reconciliation may use bounded SYSTEM_DERIVED recovery authority only if 10 can prove it is restoring a state already legitimized by the original operation.

Any discretionary new decision requires the normal 04 authority path.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF sufficient to determine valid prior/committed state.

## PRECONDITIONS

Recovery operation is defined by 10 and does not violate 03 legal-state invariants.

## VALIDATION

Validate:

```text
recovery result is a state legal under 03
Workspace scope preserved
Question immutability preserved
raw Burst integrity preserved
human/AI distinction preserved
authority history preserved
audit reconstruction preserved
no duplicate consequence
```

## ALLOW

Only deterministic restore/reconciliation to an architecture-valid state.

## DENY

```text
recovery bypasses Human Decision Authority
recovery grants authority
recovery writes illegal target state
recovery rewrites original Question
recovery adds raw Question after Burst completion
recovery converts AI output into human state
recovery repeats an already committed consequence
```

## REQUIRE

Exact recovery contract from 10 and sufficient reconciliation proof.

## ESCALATE

If deterministic reconciliation is impossible:

```text
route to explicitly authorized human/governance recovery process
```

The original operation remains blocked.

## NEXT PERMITTED PATH

After recovery resolves state:

```text
fresh full boundary chain
```

for any further consequential operation.

## PROHIBITED PATH

```text
replay events as commands
restore stale authority binding
bypass membership because "recovery"
direct DB repair to desired business state
AI chooses recovery outcome
```

## PERSISTENCE CONSEQUENCE

Only recovery writes defined by 10 and consistent with upstream architecture.

## AUDIT CONSEQUENCE

Recovery action and proof basis must be auditable.

## FAILURE BEHAVIOR

Recovery failure remains INDETERMINATE.

No cascading speculative repair.

## RECOVERY / ROLLBACK DEPENDENCY

10 is authoritative for actual recovery algorithms.

## TESTABLE INVARIANT

```text
Recovery can never produce a state that could not have been validly reached or legitimately restored under 00-06.
```

## BYPASS PATHS

```text
admin repair script
event replay
database restore
queue replay
manual SQL
disaster recovery
reconciliation worker
```

Every one must preserve BND-018 semantics.

---

# 26. GAP-06-001 Recovery Operation Authority Detail

**Status:** `[UNDERDEFINED]`

04 does not define a general human Recovery Authority class.

06 therefore permits only:

```text
deterministic System reconciliation
that restores/proves previously legitimate state
```

without a new human decision right.

If recovery requires discretionary business/domain choice:

```text
10 must identify the existing 04 decision/authority class that applies
or trigger controlled upstream reconstruction if none exists.
```

06 does not invent a Recovery superauthority.

---

# 27. Boundary Composition Examples

## 27.1 Human primary Question selection

```text
BND-001 Identity
-> BND-002 Workspace
-> BND-003 Membership
-> BND-005 QuestionSelectionAuthority
-> BND-006 Human Decision
-> BND-007 Session QUESTION_SELECTION state
-> BND-014 Commit fresh revalidation
-> BND-015 Audit
```

AI recommendation may enter as input before BND-006.

It cannot replace BND-006.

## 27.2 Facilitator starts Burst

```text
BND-001
-> BND-002
-> BND-003
-> BND-004 Facilitator role + Session scope
-> BND-007 CHALLENGE_CAPTURE -> QUESTION_GENERATION eligibility
-> BND-008 Burst contamination/mode boundary
-> BND-014 fresh revalidation
-> BND-015 audit
```

## 27.3 Post-Burst AI analysis

Human controller path:

```text
BND-001
-> BND-002
-> BND-003
-> BND-005 SessionControlAuthority
-> BND-007 QUESTION_CAPTURE -> ANALYSIS
-> BND-008 Burst must be COMPLETED/frozen
-> BND-009 AI Invocation
-> model
-> BND-010 AI Output
-> BND-014 derived persistence
-> BND-015 audit
```

System-derived path additionally requires:

```text
BND-012 Method Approval
-> BND-011 SYSTEM_DERIVED Authority
```

Because D8 is unresolved, that automatic method-derived path is currently REQUIRE/DENY.

## 27.4 Human Decision finalization

```text
BND-001
-> BND-002
-> BND-003
-> BND-005 DecisionAuthority
-> BND-006 Human Decision
-> BND-007 Decision UNDER_CONSIDERATION -> DECIDED
-> BND-013 Evidence if required by later 07 rule
-> BND-014 fresh commit revalidation
-> BND-015 audit
```

## 27.5 Timer completes Burst

```text
BND-001 System identity
-> BND-002 Workspace
-> BND-007 valid Burst/Session state
-> BND-008 Burst completion integrity
-> BND-011 SYSTEM_DERIVED Authority
-> BND-014 commit
-> BND-015 audit
```

Current result:

```text
REQUIRE
```

until timer trust and duration/pause semantics close.

## 27.6 Export

```text
BND-001
-> BND-002
-> BND-003
-> BND-016
```

Current result:

```text
DENY / REQUIRE Export Authority
```

No path reaches BND-014.

---

# 28. Direct Persistence Prohibition

**[ARCHITECTURAL CLOSURE]**

Canonical persistence is not an alternate entrypoint to the architecture.

A direct storage mutation that has not passed required boundaries is:

```text
invalid system state
```

not an authorized shortcut.

Implementation therefore must ensure that canonical consequential storage cannot be used as a weaker bypass path.

Exact technical mechanism belongs to 09/11.

---

# 29. Event Replay Prohibition

**[ARCHITECTURAL CLOSURE]**

An event is historical evidence of occurrence.

An event is not a command.

Therefore:

```text
replay for reconstruction
may rebuild a projection/state representation according to authoritative history

replay
must not re-trigger external/consequential side effects merely because event handlers execute
```

Any replay path that creates a new consequence must re-enter normal boundaries and prove the operation is not already committed.

---

# 30. Retry Prohibition After Uncertain Consequence

**[ARCHITECTURAL CLOSURE]**

A retry is safe only when the prior outcome is provably non-committed or the operation contract is proven idempotent under 09/10.

If prior outcome is:

```text
INDETERMINATE
```

the retry is denied until BND-018 reconciliation.

---

# 31. Admin and Governance Path Rule

Administrative/governance operations are not boundary-exempt.

Examples:

```text
membership changes
role changes
authority grant/revoke
method approval
future export authority grant
```

must pass:

```text
Identity
Workspace
Membership where applicable
Governance Authority
Commit
Audit
Failure/Recovery
```

No hidden admin backdoor is permitted by architecture.

---

# 32. AI Tool Invocation Rule

An AI tool call that can produce consequential effect is treated as a request from:

```text
AI_PROCESSOR
```

unless a separately identified SYSTEM_SERVICE owns and independently validates the operation.

AI tool invocation does not inherit the human authority of the conversation participant.

If the tool requires a human decision:

```text
AI tool path stops
-> BND-006 requires actual human decision
```

---

# 33. Background Worker Rule

A background worker does not inherit authority merely because the job was queued earlier.

At execution and especially commit time:

```text
scope
state
authority
membership
revocation
method approval
System derivation
```

must be current.

Stale job payload is not authority.

---

# 34. Boundary Ordering Invariant

For any operation requiring multiple boundaries:

```text
later boundary cannot weaken earlier boundary
later boundary cannot invent missing authority
later boundary cannot reinterpret DENY as ALLOW
commit boundary must revalidate commit-sensitive upstream conditions
```

---

# 35. Boundary Decision Persistence

Boundary evaluation results may be recorded for audit/observability.

Recorded `ALLOW` is not reusable authority.

A persisted boundary decision is historical evidence of a prior evaluation.

It is not a commit token.

---

# 36. AC-06-002 Boundary ALLOW Is Non-Transitive

**[ARCHITECTURAL CLOSURE]**

An ALLOW from one boundary means only:

```text
continue to next applicable boundary
```

It cannot authorize another operation, scope or future time.

---

# 37. AC-06-003 Downstream Cannot Override Upstream DENY

**[ARCHITECTURAL CLOSURE]**

Boundary result precedence:

```text
DENY is terminal

REQUIRE blocks

ESCALATE blocks

ALLOW continues
```

No "higher privileged" downstream boundary exists.

---

# 38. AC-06-004 REQUIRE Is Named and Re-evaluated

**[ARCHITECTURAL CLOSURE]**

Every REQUIRE result must identify the missing prerequisite.

After prerequisite creation, the request must rerun applicable boundaries.

The original ALLOW chain is not resumed from cache.

---

# 39. AC-06-005 ESCALATE Is Non-Authorizing

**[ARCHITECTURAL CLOSURE]**

Escalation routes work.

It does not grant the requested consequence.

After escalation produces a legitimate prerequisite:

```text
fresh boundary evaluation required
```

---

# 40. AC-06-006 Boundary Path Convergence

**[ARCHITECTURAL CLOSURE]**

Every consequential path must converge on equivalent boundary semantics regardless of transport or execution mechanism.

This prohibits a privileged:

```text
worker path
admin path
AI path
replay path
recovery path
```

with weaker controls.

---

# 41. AC-06-007 Commit-Time Revalidation

**[ARCHITECTURAL CLOSURE]**

BND-014 must freshly evaluate all commit-sensitive conditions immediately before consequential commit.

This operationalizes AC-05-008 and GAP-05-002 semantics.

Exact technical concurrency/version mechanism remains downstream.

---

# 42. AC-06-008 Direct Persistence Is Not an Authority Path

**[ARCHITECTURAL CLOSURE]**

Storage access is implementation capability.

It is not operation authority.

---

# 43. AC-06-009 Event Replay Is Reconstruction, Not Command Re-execution

**[ARCHITECTURAL CLOSURE]**

Replay cannot duplicate consequential side effects.

---

# 44. AC-06-010 Retry Requires Proven Non-Commit or Proven Idempotency

**[ARCHITECTURAL CLOSURE]**

Unknown prior commit status routes to recovery.

---

# 45. AC-06-011 AI Tool Invocation Does Not Inherit Human Authority

**[ARCHITECTURAL CLOSURE]**

A model acting through tools remains AI_PROCESSOR.

It does not become the human User.

---

# 46. AC-06-012 Recovery Has No Boundary Exemption

**[ARCHITECTURAL CLOSURE]**

Recovery is subject to scope, authority, state validity, immutability and audit constraints.

---

# 47. AC-06-013 Boundary Uncertainty Uses Least-Permissive Interpretation

**[ARCHITECTURAL CLOSURE]**

If a boundary cannot determine whether a consequential operation is permitted:

```text
do not permit consequence
```

Use:

```text
DENY
REQUIRE
ESCALATE
```

according to the known failure type.

---

# 48. Carried Gaps and Blockers

## CONFLICT-001 Inquiry Graph prototype scope

Preserved.

Not resolved by boundaries.

## CONFLICT-007 Burst duration semantics

Preserved.

BND-011 timer authority remains blocked.

## GAP-01-003 Active-Burst AI observer/recorder semantics

Preserved.

BND-008 prevents model analysis/evaluation until resolved.

## GAP-03-002 Pause and Timer semantics

Preserved.

## GAP-03-003 Questions-only enforcement mechanism

Preserved.

BND-008 defines the boundary requirement but not the validator mechanism.

## GAP-03-006 Required AI Analysis failure/bypass

Preserved.

BND-017/018 route failure.

No skip authority invented.

## GAP-03-016 Audit atomicity

Preserved.

BND-015 defines semantics, not transaction mechanism.

## GAP-03-017 Cross-object commit atomicity

Preserved.

BND-014 requires logical consistency.

## GAP-04-001 Collaborative Question Selection Rule

Preserved OPEN.

## GAP-04-004 Session Control multiplicity

Preserved UNDERDEFINED.

## GAP-04-007 System Timer Identity and Trust

Preserved UNDERDEFINED.

## GAP-04-008 Method Approval Authority

Preserved OPEN.

BND-012 fail-closed.

## GAP-04-013 Export Authority

Preserved OPEN.

BND-016 fail-closed.

## GAP-05-001 Workspace Root Creation and Succession

Preserved UNDERDEFINED.

## GAP-05-002 Cached Authorization and Commit Recheck

Semantic requirement closed by BND-014.

Implementation mechanism remains downstream.

## GAP-05-003 Governance Operation Atomicity

Preserved UNDERDEFINED.

## GAP-05-005 Method Version Identity

Preserved UNDERDEFINED.

## GAP-05-007 Governance Concurrency

Preserved UNDERDEFINED.

## GAP-05-008 Export Authority Resolution Home

Preserved OPEN upstream dependency.

---

# 49. New Gaps Exposed in 06

## GAP-06-001 Commit Concurrency / Freshness Mechanism

**Status:** `[UNDERDEFINED]`

BND-014 requires fresh commit-time revalidation.

09/10/11 must define how implementation proves:

```text
state did not change after check
binding did not revoke after check
membership did not revoke after check
governance predicate did not change after check
```

Possible mechanisms are not selected in 06.

## GAP-06-002 Boundary Evaluation Correlation

**Status:** `[UNDERDEFINED]`

Audit and recovery require one operation's boundary evaluations, commit and audit consequences to be correlated.

Exact correlation identifier/schema belongs to 09.

## GAP-06-003 Idempotency Identity

**Status:** `[UNDERDEFINED]`

Retries require the system to identify whether a request is the same consequential operation.

Exact idempotency key/command identity belongs to 09/10.

## GAP-06-004 Direct Persistence Enforcement Mechanism

**Status:** `[UNDERDEFINED]`

06 prohibits direct canonical writes that bypass boundaries.

09/11 must define how repository/database access is technically constrained so bypass is not merely convention.

## GAP-06-005 AI Gateway Bypass Enforcement Mechanism

**Status:** `[UNDERDEFINED]`

BND-009 requires all model traffic through the gateway.

08/11 must define how direct provider calls are prevented/detected.

## GAP-06-006 Event Replay Side-Effect Isolation Mechanism

**Status:** `[UNDERDEFINED]`

06 prohibits replay from re-triggering consequences.

09/10 must define replay mode and side-effect isolation.

## GAP-06-007 Recovery Authority for Discretionary Reconciliation

**Status:** `[UNDERDEFINED]`

Deterministic recovery is structurally allowed.

If recovery needs a new discretionary human choice and no existing 04 authority class fits, controlled upstream reconstruction may be required.

## GAP-06-008 Evidence Boundary Closure Dependency

**Status:** `[UNDERDEFINED UNTIL 07]`

BND-013 cannot fully ALLOW evidence-dependent transitions until 07 defines validation/sufficiency/authority semantics.

This is expected downstream work, not an upstream contradiction.

## GAP-06-009 Audit Failure Commit Coupling

**Status:** `[UNDERDEFINED]`

BND-015 defines outcome semantics.

09/10 must define how state and audit writes avoid unresolvable divergence.

This carries the architectural substance of GAP-03-016 into the boundary layer.

## GAP-06-010 Export Boundary Content Policy

**Status:** `[UNDERDEFINED]`

Even after Export Authority closes, the boundary still needs:

```text
object inclusion
derived-content inclusion
audit inclusion
redaction
privacy filtering
format reconstruction
```

from 09/11/12.

---

# 50. Boundary Bypass Falsification

The following adversarial paths were constructed against 06.

## 50.1 Owner without DecisionAuthority

Attempt:

```text
Workspace Owner
-> direct API
-> RECORD_HUMAN_DECISION
```

Preventing boundaries:

```text
BND-004 Owner governance context
BND-005 Human Authority
BND-006 Human Decision Authority
BND-014 Commit
```

Result:

```text
DENY
```

Owner root is not DECISION_RIGHT.

## 50.2 Facilitator outside assigned Session

Attempt:

```text
Workspace Facilitator
-> start Burst in arbitrary Session
```

Preventing boundaries:

```text
BND-004 requires ACTIVE Session FacilitatorScopeBinding
BND-014 revalidates scope
```

Result:

```text
DENY
```

## 50.3 Revoked human authority

Attempt:

```text
request authorized
-> binding revoked
-> stale worker commits
```

Preventing boundaries:

```text
BND-005 current authority
BND-014 commit-time revalidation
```

Result:

```text
DENY
```

## 50.4 Removed Workspace member

Attempt:

```text
old HumanAuthorityBinding
-> operation after membership removal
```

Preventing boundaries:

```text
BND-003 Membership
BND-005 binding effectiveness
BND-014 revalidation
```

Result:

```text
DENY
```

## 50.5 AI attempting governance mutation

Attempt:

```text
AI tool
-> grant DecisionAuthority
```

Preventing boundaries:

```text
BND-001 identifies AI_PROCESSOR
BND-004/BND-005 no governance human authority
05 AI governance exclusion
BND-014
```

Result:

```text
DENY
```

## 50.6 AI output directly persisted as authoritative state

Attempt:

```text
AI recommendation
-> write Decision DECIDED
```

Preventing boundaries:

```text
BND-010 AI Output / Canonical State
BND-006 Human Decision
BND-007 Decision state path
BND-014
```

Result:

```text
DENY
```

## 50.7 SYSTEM_SERVICE using stale derivation

Attempt:

```text
System gets derivation ALLOW
-> method/binding/state changes
-> worker commits
```

Preventing boundaries:

```text
BND-011 recomputes derivation
BND-014 fresh commit revalidation
```

Result:

```text
DENY
```

## 50.8 Unapproved InquiryMethod

Attempt:

```text
configured Question Burst method
-> auto Begin Analysis
```

Preventing boundaries:

```text
BND-012 Method Approval
BND-011 System Authority
```

Result:

```text
REQUIRE D8 approval authority / approved version
```

No fallback.

## 50.9 Client-side timer completion

Attempt:

```text
browser says timer expired
-> Complete Burst
```

Preventing boundaries:

```text
BND-011 requires trusted System derivation
BND-008 Burst integrity
BND-014
```

Result:

```text
REQUIRE trusted timer semantics
```

## 50.10 Direct database mutation

Attempt:

```text
admin SQL:
UPDATE sessions SET state='ACTION'
```

Preventing architecture:

```text
BND-007 says illegal without transition path
BND-014 says direct persistence is not authority path
AC-06-008
```

Result:

```text
architecturally invalid state
```

09/11 must technically prevent/enforce this.

## 50.11 Event replay

Attempt:

```text
replay QUESTION_SELECTED
-> selection handler executes again
```

Preventing boundaries:

```text
BND-015 Audit/Event semantics
AC-06-009
BND-017 duplicate-consequence check
BND-018 recovery semantics
```

Result:

```text
DENY side-effect re-execution
```

Projection reconstruction remains allowed.

## 50.12 Retry after INDETERMINATE

Attempt:

```text
timeout
-> unknown commit
-> automatic retry
```

Preventing boundary:

```text
BND-017
```

Result:

```text
REQUIRE reconciliation
```

No blind retry.

## 50.13 Unresolved Export request

Attempt:

```text
Owner clicks Export
```

Preventing boundary:

```text
BND-016
```

Result:

```text
DENY / REQUIRE Export Authority
```

## 50.14 Recovery path bypassing normal authority

Attempt:

```text
recovery script
-> write desired Decision/Session state directly
```

Preventing boundaries:

```text
BND-018
BND-007
BND-014
```

Result:

```text
DENY
```

Recovery may only restore/reconcile valid prior legitimacy.

---

# 51. Boundary Bypass Result

**RESULT: PASS WITH DOWNSTREAM ENFORCEMENT DEPENDENCIES**

Every required falsification case has an identified preventing boundary.

No bypass case currently lacks a semantic control point.

Technical enforcement still depends on downstream architecture for:

```text
database access control
commit concurrency
idempotency
gateway bypass prevention
event replay isolation
audit/commit consistency
recovery algorithms
```

These are explicit gaps, not silent assumptions.

---

# 52. Boundary to Authority Validation

**PASS**

No boundary invents a new authority class.

BND-005 consumes 04 authority.

BND-006 consumes 04 human decision rights.

BND-011 consumes 04/05 SYSTEM_DERIVED authority.

BND-016 preserves unresolved Export Authority.

BND-012 preserves unresolved Method Approval Authority.

---

# 53. Boundary to State Validation

**PASS**

BND-007 consumes 03 topology unchanged.

BND-008 uses 03 Burst states unchanged.

BND-014 commits only 03-valid target state.

BND-018 cannot create a state illegal under 03.

No state was added to simplify boundary enforcement.

---

# 54. Boundary to Evidence Validation

**PASS WITH EXPECTED DOWNSTREAM DEPENDENCY**

BND-013 distinguishes:

```text
SYSTEM_PROOF
DOMAIN_EVIDENCE
AI_VALIDATION_PROOF
human decision
```

It does not treat AI confidence as Evidence.

07 remains required to close Evidence validation semantics.

---

# 55. Boundary to Persistence Validation

**PASS WITH GAP-06-004 / GAP-06-001**

BND-014 defines the final commit control point.

Direct persistence is architecturally invalid.

Technical enforcement and concurrency mechanism belong to 09/11.

---

# 56. Boundary to Audit Validation

**PASS WITH GAP-03-016 / GAP-06-009**

BND-015 ensures event/audit semantics cannot create authority/state.

Audit atomicity remains unresolved downstream.

No silent assumption made.

---

# 57. Boundary to Failure Validation

**PASS**

Uncertainty never creates permission.

Outcomes route to:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

with least-permissive handling.

---

# 58. Boundary to Recovery Validation

**PASS WITH GAP-06-007**

Recovery must preserve:

```text
legal state
scope
authority history
immutability
Burst integrity
human/AI distinction
auditability
```

Discretionary recovery authority remains underdefined rather than invented.

---

# 59. Recursive Validation Against 00

## RESULT

**PASS**

06 implements the boundary classes and executable control-point requirement established by 00.

Preserved:

```text
Human Decision Authority
Governance Before Consequence
consequential transition closure invariant
recovery-valid-state invariant
one authoritative home
```

No 00 reconstruction required.

---

# 60. Recursive Validation Against 01

## RESULT

**PASS**

06 operationalizes:

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
Provenance dependency
Decision Boundary
Export Boundary
Audit Boundary
Failure Boundary
Recovery Boundary
```

without altering 01 source classifications.

No 01 reconstruction required.

---

# 61. Recursive Validation Against 02

## RESULT

**PASS**

06 does not collapse:

```text
THING
RELATION
STATE
EVENT
AUTHORITY
EVIDENCE
PROJECTION
CONFIGURATION
```

Key preserved facts:

```text
WorkspaceMembership remains relation
HumanAuthorityBinding remains authority construct
AuditEvent remains event
InquiryMethod remains configuration
InquiryGraph remains projection
AI persistence remains separate from epistemic truth
```

No 02 reconstruction required.

---

# 62. Recursive Validation Against 03

## RESULT

**PASS**

06 does not modify:

```text
Session topology
QuestionBurst topology
Assumption topology
Experiment topology
Decision topology
illegal transitions
INDETERMINATE semantics
```

BND-007 enforces them.

BND-017/018 preserve failure/recovery semantics.

No 03 reconstruction required.

---

# 63. Recursive Validation Against 04

## RESULT

**PASS**

06 consumes, rather than invents:

```text
source-explicit rights
HumanAuthorityBindings
SessionControlAuthority
QuestionSelectionAuthority
AssumptionInterpretationAuthority
ExperimentDecisionAuthority
DecisionAuthority
ActionDecisionAuthority
SYSTEM_DERIVED authority
```

Export Authority remains OPEN.

Method Approval Authority remains OPEN.

No 04 reconstruction required.

---

# 64. Recursive Validation Against 05

## RESULT

**PASS**

06 preserves:

```text
HumanAuthorityBinding ACTIVE/REVOKED
commit-time authority revalidation
least-permissive uncertainty
Owner governance root, not superuser
Session FacilitatorScopeBinding
membership-dependent cleanup
SYSTEM_DERIVED ephemerality
AI governance exclusion
Export fail-closed
Method approval fail-closed
```

No 05 reconstruction required.

---

# 65. Upstream Contradiction Check

**RESULT: NO UPSTREAM CONTRADICTION FOUND**

Every required boundary can be represented using approved 00-05 architecture.

06 did not require:

```text
new domain object
new relation
new 03 state
new 03 transition
new 04 authority class
new human decision-right class
Owner superuser semantics
AI authority
```

The recursive STOP condition is not triggered.

---

# 66. New Architectural Closures Introduced in 06

| ID | Addition | Status | Reason |
|---|---|---|---|
| AC-06-001 | Commit approval is ephemeral to one operation/current evaluation | `[ARCHITECTURAL CLOSURE]` | Prevent stale ALLOW reuse |
| AC-06-002 | Boundary ALLOW is non-transitive | `[ARCHITECTURAL CLOSURE]` | ALLOW only advances to next boundary |
| AC-06-003 | Downstream boundary cannot override upstream DENY | `[ARCHITECTURAL CLOSURE]` | Composable high-assurance boundary semantics |
| AC-06-004 | REQUIRE names missing prerequisite and requires fresh reevaluation | `[ARCHITECTURAL CLOSURE]` | Prevent resumed stale authorization chain |
| AC-06-005 | ESCALATE is non-authorizing | `[ARCHITECTURAL CLOSURE]` | Preserve Human/Governance authority separation |
| AC-06-006 | All consequential transport paths converge on equivalent boundary semantics | `[ARCHITECTURAL CLOSURE]` | Prevent API/worker/admin/recovery bypass |
| AC-06-007 | Commit-time fresh revalidation of all commit-sensitive predicates | `[ARCHITECTURAL CLOSURE]` | Operationalize stale-authority prevention |
| AC-06-008 | Direct persistence is never an authority path | `[ARCHITECTURAL CLOSURE]` | Persistence != authority |
| AC-06-009 | Event replay reconstructs but does not re-execute consequence | `[ARCHITECTURAL CLOSURE]` | Event != command/state |
| AC-06-010 | Retry requires proven non-commit or proven idempotency | `[ARCHITECTURAL CLOSURE]` | Prevent duplicate consequence |
| AC-06-011 | AI tool invocation never inherits human authority | `[ARCHITECTURAL CLOSURE]` | AI != human/system authority |
| AC-06-012 | Recovery has no boundary exemption | `[ARCHITECTURAL CLOSURE]` | Recovery-valid-state invariant |
| AC-06-013 | Boundary uncertainty uses least-permissive interpretation | `[ARCHITECTURAL CLOSURE]` | Uncertainty cannot create permission |
| AC-06-014 | Boundary results may be audited but persisted ALLOW is not reusable authority | `[ARCHITECTURAL CLOSURE]` | Historical decision != current authority |
| AC-06-015 | AI output acceptance and human adoption are separate boundary paths | `[ARCHITECTURAL CLOSURE]` | AI proposal ends before human authority begins |
| AC-06-016 | Export cannot reach commit while Export Authority remains unresolved | `[ARCHITECTURAL CLOSURE]` | Preserve GAP-04-013 and MVP blocker |
| AC-06-017 | Unapproved method cannot activate System-derived authority | `[ARCHITECTURAL CLOSURE]` | CONFIGURATION != AUTHORITY |
| AC-06-018 | Direct database/ORM capability does not establish legitimate canonical state | `[ARCHITECTURAL CLOSURE]` | High-assurance commit boundary |
| AC-06-019 | Recovery may deterministically restore prior legitimacy but cannot create a new discretionary business decision | `[ARCHITECTURAL CLOSURE]` | Avoid recovery superauthority |

---

# 67. New Gaps Exposed in 06

```text
GAP-06-001 Commit Concurrency / Freshness Mechanism
GAP-06-002 Boundary Evaluation Correlation
GAP-06-003 Idempotency Identity
GAP-06-004 Direct Persistence Enforcement Mechanism
GAP-06-005 AI Gateway Bypass Enforcement Mechanism
GAP-06-006 Event Replay Side-Effect Isolation Mechanism
GAP-06-007 Recovery Authority for Discretionary Reconciliation
GAP-06-008 Evidence Boundary Closure Dependency
GAP-06-009 Audit Failure Commit Coupling
GAP-06-010 Export Boundary Content Policy
```

No gap is silently treated as closed.

---

# 68. Baseline Blockers After 06

## BLOCK-06-001 Export Authority

```text
GAP-04-013
```

OPEN.

Export is MVP.

Baseline-blocking.

## BLOCK-06-002 Workspace Governance Root Bootstrap

```text
GAP-05-001
```

Running Workspace provisioning needs deterministic first owner/root semantics.

Baseline-blocking for implementation.

## BLOCK-06-003 Commit Concurrency / Atomicity

```text
GAP-03-017
GAP-05-003
GAP-05-007
GAP-06-001
```

Must close before high-assurance commit implementation.

## BLOCK-06-004 Audit / Commit Consistency

```text
GAP-03-016
GAP-06-009
```

Must close before high-assurance baseline freeze.

## BLOCK-06-005 Direct Persistence Enforcement

```text
GAP-06-004
```

Implementation must not expose a weaker canonical write path.

## BLOCK-06-006 Timer Trust and Semantics

If automatic timer completion is prototype behavior:

```text
CONFLICT-007
GAP-03-002
GAP-04-007
```

must close.

## BLOCK-06-007 Method Approval for Automatic System Progression

If prototype uses method-triggered SYSTEM_DERIVED progression:

```text
D8
GAP-04-008
GAP-05-005
```

must close.

Manual authorized paths may avoid this blocker if 03/04 permit them.

## BLOCK-06-008 Collaborative Question Selection Policy

If multiple human selectors are in prototype:

```text
GAP-04-001
```

must close.

## BLOCK-06-009 Evidence-Dependent Transition Rules

Only baseline-blocking for prototype operations that require DOMAIN_EVIDENCE.

07 determines whether this applies to the Minimum Closed Prototype.

---

# 69. Readiness for 07

07 will own Evidence and Provenance semantics.

06 now gives 07 explicit boundary requirements:

```text
DOMAIN_EVIDENCE must remain distinct from SYSTEM_PROOF
AI confidence cannot satisfy Evidence
Evidence must be Workspace-scoped
Evidence validity may be a commit-sensitive predicate
Evidence used for consequential transitions must be reconstructable
Evidence uncertainty must fail closed when Evidence is required
AI-generated/inferred material cannot become evidence merely by persistence
```

07 must not:

```text
invent authority to validate Evidence
collapse AI confidence into Evidence
make persistence equal truth
make provenance equal authority
change 03 transition topology
change 04 authority classes
weaken BND-013
```

## READINESS RESULT

**READY FOR HUMAN REVIEW**

`06_BOUNDARY_ARCHITECTURE.md` is structurally ready to become the authoritative Boundary Architecture input for `07_EVIDENCE_AND_PROVENANCE.md`.

Every requested falsification path has a preventing semantic boundary.

No upstream contradiction was found.

07 is not yet authorized.

No implementation work has begun.

No Architecture Baseline has been frozen.

---

# 70. Stop Gate

**STOP CONDITION REACHED**

Await human review and explicit:

```text
HUMAN_REVIEW::06_APPROVED
GO::BUILD_07_EVIDENCE_AND_PROVENANCE
```
