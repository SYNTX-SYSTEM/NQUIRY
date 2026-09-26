# 04_AUTHORITY_AND_DECISION_RIGHTS

**Project:** N.Q.U.I.R.Y.  
**Document role:** Authoritative Authority and Decision Rights Architecture  
**Architecture stage:** E, Authority + Decision Rights  
**Upstream authority:** `00_NQUIRY_MASTER_ARCHITECTURE.md`, `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md`, `02_DOMAIN_AND_RELATION_MODEL.md`, `03_STATE_AND_TRANSITION_ARCHITECTURE.md`  
**LEVEL 1 authority:** `N.Q.U.I.R.Y. - Product & System Specification`  
**LEVEL 2 input:** `# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md`  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 05 not yet authorized

---

# 0. Document Authority

This file is authoritative for:

```text
actor classes
identity requirements for consequential operations
authority-source hierarchy
authority scope
decision-right semantics
operation-authority semantics
human authority bindings
system-derived procedural authority
AI authority limits
delegation semantics
default-deny rules
authority failure behavior
authority dependencies exposed by 03
authority requirements for every consequential operation
```

This file is not authoritative for:

```text
state topology
new state transitions
domain-object identity
governance execution mechanisms
boundary implementation
evidence-validation semantics
provenance field schemas
database schemas
API schemas
audit event schemas
recovery algorithms
prototype scope
```

03 remains authoritative for state and transition topology.

04 does not add, remove, reorder or bypass any 03 state transition.

---

# 1. Authority Invariants

The following approved invariants are binding.

```text
authentication != authority

role label != authority

AI generation != authority

human authorship != automatic authority

human decision != transition authorization

transition authorization != executed state

persistence != authority

event occurrence != authority

confidence != authority

derived analysis != authority
```

A system may know:

```text
who the actor is
what role label appears on the actor
what the AI recommends
what object was persisted
what event occurred
```

and still lack authority for the requested consequential operation.

---

# 2. Authority Dimensions

Authority is modeled across separate dimensions.

## 2.1 ACTOR

Who or what requested or executes an operation.

Actor classes:

```text
HUMAN_USER
SYSTEM_SERVICE
AI_PROCESSOR
EXTERNAL_SYSTEM
```

## 2.2 IDENTITY

The authenticated or otherwise cryptographically/systemically established identity of the actor.

Identity proves actor identity.

Identity does not prove authority.

## 2.3 ROLE

A descriptive or scoped role such as:

```text
Owner
Facilitator
Contributor
Observer
Viewer
Session Participant
```

Role may be an input to authority evaluation.

Role alone does not grant authority unless this file explicitly binds an operation to that role.

## 2.4 DECISION RIGHT

The legitimate right to make a discretionary human choice that changes the meaning or direction of inquiry.

Examples:

```text
select primary Question
classify Assumption after evaluation
authorize Experiment
record human Decision
decide movement into Action
```

## 2.5 OPERATION AUTHORITY

The legitimate right to request a consequential system operation.

This may belong to:

```text
an authorized human
a deterministic System service
```

An operation may require a human decision plus a separate operation authorization.

## 2.6 AUTHORITY SOURCE

The architectural basis for the authority.

Permitted sources:

```text
LEVEL_1_EXPLICIT
ARCHITECTURAL_CLOSURE
EXPLICIT_AUTHORITY_BINDING
SYSTEM_DERIVED
OPEN_UNRESOLVED
```

## 2.7 AUTHORITY SCOPE

The exact object/context boundary within which the authority is valid.

Examples:

```text
Workspace
Challenge
Session
QuestionBurst
Question
Assumption
Experiment
Decision
```

Authority outside its scope is invalid.

## 2.8 AUTHORITY PRECONDITIONS

Facts that must hold before authority can be exercised.

Examples:

```text
authenticated identity
active Workspace membership
required role binding
Session participation
object in correct state
human decision already exists
authority grant not revoked
```

## 2.9 DELEGATION STATUS

Whether authority may be transferred or exercised by another actor.

## 2.10 HUMAN DECISION REQUIREMENT

Whether the operation requires an actual human discretionary decision.

## 2.11 SYSTEM-DERIVED AUTHORITY

Whether a non-discretionary System operation may derive authority from already-authorized state, method and policy.

## 2.12 AI PERMITTED ROLE

What AI may do around the operation.

## 2.13 AI PROHIBITED ROLE

What AI may not do.

---

# 3. Actor Identity Model

## 3.1 HUMAN_USER

**[ARCHITECTURAL CLOSURE]**

Every human actor performing a consequential mutation must resolve to an authenticated User identity.

Trace:

```text
LEVEL 1 User authentication MVP requirement
LEVEL 1 security chain:
Identity -> Authentication -> Authorization
01 Identity != authority
```

Anonymous mutation is not part of the current high-assurance architecture.

If guest/anonymous contribution is later required, it must be explicitly architected.

## 3.2 SYSTEM_SERVICE

**[ARCHITECTURAL CLOSURE]**

A System service performing a consequential operation must use an identifiable internal service identity.

`SYSTEM_SERVICE` is not the same as AI.

System authority can only be derived where 04 explicitly permits it.

## 3.3 AI_PROCESSOR

**[ARCHITECTURAL CLOSURE]**

AI_PROCESSOR identifies an AI/model operation executor.

AI_PROCESSOR may:

```text
analyze
classify
cluster
reframe
detect assumptions
generate proposals
generate questions where permitted
produce derived artifacts
```

AI_PROCESSOR may not receive:

```text
human decision rights
Workspace governance authority
transition authorization requiring human judgment
authority delegation from a human
```

## 3.4 EXTERNAL_SYSTEM

External systems have no consequential N.Q.U.I.R.Y. authority merely because they are integrated.

Any accepted external operation requires later explicit authority architecture.

No current AUTH-DEP is assigned to EXTERNAL_SYSTEM.

---

# 4. Workspace Role Semantics

LEVEL 1 names:

```text
Owner
Facilitator
Contributor
Observer
Viewer
```

02 places Workspace-scoped team role assignment on `WorkspaceMembership`.

`User.role` remains underdefined and is not used as the authoritative Workspace permission role.

## 4.1 Owner

Source support:

```text
Workspace.owner_id
Owner role label
```

LEVEL 1 does not enumerate Owner operation permissions.

Therefore:

```text
Owner role label alone
!= authority to execute every Workspace operation
```

## 4.2 Facilitator

LEVEL 1 explicitly gives Facilitator rights to:

```text
create a Challenge
start Question Burst
pause Question Burst
end Question Burst
```

These are direct source authority rights within the relevant Workspace/Session scope.

## 4.3 Contributor

LEVEL 1 names Contributor as a role but does not explicitly bind a consequential operation to the Contributor label.

No authority is granted merely from the label.

## 4.4 Observer

No consequential mutation authority is source-defined.

Default deny applies.

## 4.5 Viewer

No consequential mutation authority is source-defined.

Default deny applies.

## 4.6 Session Participant

`Session Participant` is a participation relation, not a Workspace role.

LEVEL 1 explicitly states:

```text
participants submit questions
participants cannot edit others' questions
```

Therefore active Session participation is a direct source authority input for Question submission during an active Burst.

---

# 5. AC-04-001: Workspace Governance Root

**Status:** `[ARCHITECTURAL CLOSURE]`

A high-assurance system requires a legitimate root from which human authority bindings can be established.

LEVEL 1 provides:

```text
Workspace.owner_id
Workspace.members
Workspace.permissions
Owner role
```

04 therefore establishes:

```text
Workspace.owner_id
=
root human governance authority for that Workspace
```

This closure does **not** mean:

```text
Workspace Owner
=
automatic executor of every operation
```

The root authority is limited to governance of:

```text
Workspace membership
Workspace-scoped authority bindings
role assignments
revocation of delegated Workspace authority
```

Exact governance mechanisms belong to 05.

Exact persistence contracts belong to 09.

## 5.1 Scope

Workspace only.

## 5.2 Delegation

Workspace governance authority may create explicit human authority bindings through 05 governance.

It may not delegate human decision authority to AI.

## 5.3 Why required

Without a governance root, source-defined:

```text
members
permissions
roles
```

cannot become executable authority without arbitrary assignment.

---

# 6. Human Authority Binding

## 6.1 Definition

**[ARCHITECTURAL CLOSURE]**

Where LEVEL 1 identifies a human responsibility but does not identify the exact role holder, authority must be represented as an explicit `HumanAuthorityBinding`.

A HumanAuthorityBinding conceptually binds:

```text
human User identity
+
operation or decision-right class
+
scope
+
authority source
+
validity status
```

This is an authority construct.

It is not a domain object introduced into 02.

05 will determine governance mechanics.

09 will determine persistence representation.

## 6.2 Binding is required when role labels are insufficient

Example:

```text
LEVEL 1:
humans remain responsible for decisions

LEVEL 1 does not say:
Owner decides
Facilitator decides
Contributor decides
```

Therefore a specific human Decision Authority Holder must be bound explicitly.

## 6.3 No implicit binding

The following do not create a HumanAuthorityBinding:

```text
being authenticated
being author of an object
having highest AI score
being Workspace Owner
being Session creator
being first participant
having Facilitator label
```

unless the operation is separately source-bound to that role.

---

# 7. Delegation Model

## 7.1 Default

**[ARCHITECTURAL CLOSURE]**

No consequential authority is transitively delegable by default.

```text
A can perform X
does not imply
A can grant X to B
```

## 7.2 Explicit governance delegation

Human authority may be reassigned only through an explicit governance operation defined in 05.

## 7.3 Human-to-AI delegation

Prohibited.

```text
human decision right
-> AI
```

is never valid under the current architecture.

## 7.4 System-derived authority is not delegation

A System service executing a deterministic operation under previously authorized conditions does not receive a human decision right.

It receives bounded procedural authority.

---

# 8. System-Derived Procedural Authority

## 8.1 Definition

**[ARCHITECTURAL CLOSURE]**

`SYSTEM_DERIVED` authority is the right of an identified System service to execute a deterministic, non-discretionary operation because all of the following already exist:

```text
valid current state
valid prior human/system authority
approved method or system rule
deterministic preconditions
required proof
boundary clearance
no unresolved human decision
```

## 8.2 System-derived authority may not

```text
make a human decision
select the primary Question
authorize an Experiment
record a human Decision
reinterpret evidence
override a denied human authority check
grant itself new scope
```

## 8.3 AI is not System authority

An AI model may execute computation used by a System-authorized operation.

The authority source remains System policy/governance, not the model output.

---

# 9. Decision Right Classes

04 defines these authority classes.

## 9.1 SESSION_CONTROL_RIGHT

Right to request procedural Session phase movement where no human substantive decision is being made.

## 9.2 QUESTION_SELECTION_RIGHT

Right to:

```text
select 1 to 3 compelling Questions
select the primary Question
```

## 9.3 ASSUMPTION_INTERPRETATION_RIGHT

Right to make the human interpretive classification required for Assumption state change after evaluation.

## 9.4 EXPERIMENT_DECISION_RIGHT

Right to:

```text
adopt Experiment proposal for consideration
authorize Experiment execution
```

## 9.5 DECISION_RIGHT

Right to record an actual human Decision as `DECIDED`.

## 9.6 ACTION_DECISION_RIGHT

Right to make the human decision to move the Session toward Action where required.

## 9.7 WORKSPACE_GOVERNANCE_RIGHT

Right to govern Workspace-scoped authority assignments and membership.

---

# 10. Session Control Authority

## 10.1 Source condition

LEVEL 1 supports:

```text
individual inquiry
facilitated sessions
Facilitator control of Burst start/pause/end
```

but does not define all Session phase-control rights.

## 10.2 AC-04-002: Explicit Session Control Authority

**[ARCHITECTURAL CLOSURE]**

Every active Session must have at least one authenticated human identity bound to:

```text
SESSION_CONTROL_RIGHT
```

before human-requested procedural Session transitions can occur.

In a facilitated Session, a Facilitator is eligible to hold this binding.

In individual inquiry, the authenticated human conducting the inquiry is eligible to hold it through Workspace governance.

Eligibility is not authority.

The binding is the authority.

## 10.3 Session Control Authority does not include

```text
Question Selection Right
Assumption Interpretation Right
Experiment Decision Right
Decision Right
Action Decision Right
```

unless those rights are separately bound.

---

# 11. Question Selection Authority

LEVEL 1 states:

```text
the user identifies 1 to 3 questions that compel action
the user selects the question that matters most
users can select 1 to 3 compelling questions
one question can be selected as most important
```

It does not specify which human holds this right in a collaborative Session.

## 11.1 AC-04-003: Explicit Question Selection Authority

**[ARCHITECTURAL CLOSURE]**

A Session entering Question Selection must have one or more authenticated human Users explicitly bound to:

```text
QUESTION_SELECTION_RIGHT
```

Only these humans may create authority-bearing `QuestionSelection` relations.

AI may recommend candidates.

AI may not perform the selection.

## 11.2 Collaborative selection policy

The exact rule for:

```text
single selector
multiple selectors
consensus
majority
Facilitator decision
Owner decision
```

is not specified by LEVEL 1.

Status:

```text
[OPEN]
```

See `GAP-04-001`.

---

# 12. Assumption Interpretation Authority

LEVEL 1 assigns interpretation responsibility to humans.

Assumption status classification is interpretive and evidentiary.

## 12.1 AC-04-004

**[ARCHITECTURAL CLOSURE]**

A human User must hold:

```text
ASSUMPTION_INTERPRETATION_RIGHT
```

to authorize:

```text
TESTING -> SUPPORTED
TESTING -> WEAK
TESTING -> REFUTED
TESTING -> UNKNOWN
```

AI may:

```text
detect an Assumption
recommend classification
summarize Evidence
identify contradictions
```

AI may not authorize the final classification.

Evidence sufficiency remains 07 authority.

---

# 13. Experiment Authority

LEVEL 1 states:

```text
human remains responsible for experiments
```

AI Experiment Designer may produce proposals.

## 13.1 AC-04-005

**[ARCHITECTURAL CLOSURE]**

An authenticated human User must hold:

```text
EXPERIMENT_DECISION_RIGHT
```

before an Experiment may move:

```text
PROPOSED -> UNDER_CONSIDERATION
UNDER_CONSIDERATION -> AUTHORIZED
```

## 13.2 Execution authority

Starting or completing an Experiment also requires human operation authority under the current architecture.

No source-defined automated experiment execution authority exists.

If later architecture permits machine-executed experiments, a new bounded System authority path must be explicitly introduced.

## 13.3 AI prohibition

AI may not:

```text
self-adopt its Experiment proposal
authorize Experiment
start Experiment under its own authority
declare Experiment completed under its own authority
```

---

# 14. Decision Authority

LEVEL 1 states:

```text
human remains responsible for decisions
```

No source role is designated as the universal decision maker.

## 14.1 AC-04-006

**[ARCHITECTURAL CLOSURE]**

Every Decision process must resolve an authenticated human User holding:

```text
DECISION_RIGHT
```

for that Decision scope before:

```text
UNDER_CONSIDERATION -> DECIDED
```

may commit.

## 14.2 Decision authority is object-scoped

A User authorized for one Decision is not automatically authorized for another Decision.

## 14.3 AI role

AI may:

```text
prepare options
summarize criteria
surface Evidence
identify contradictions
generate recommendations
```

AI may not:

```text
hold DECISION_RIGHT
choose the final selected_option as human authority
record DECIDED solely from model output
```

---

# 15. Action Decision Authority

03 requires a human decision before movement into ACTION.

LEVEL 1 assigns responsibility for actions to humans.

## 15.1 AC-04-007

**[ARCHITECTURAL CLOSURE]**

The transition:

```text
Session EXPERIMENT -> ACTION
```

requires an authenticated human holding:

```text
ACTION_DECISION_RIGHT
```

for the Session/Challenge scope.

This human may be the same person who holds:

```text
EXPERIMENT_DECISION_RIGHT
DECISION_RIGHT
SESSION_CONTROL_RIGHT
```

but no equivalence is automatic.

## 15.2 AI prohibition

AI may recommend an action.

AI may not create the human action decision.

---

# 16. Authority Grant Bootstrap

Workspace Owner is the governance root under AC-04-001.

05 must define how that root creates or revokes:

```text
SESSION_CONTROL_RIGHT
QUESTION_SELECTION_RIGHT
ASSUMPTION_INTERPRETATION_RIGHT
EXPERIMENT_DECISION_RIGHT
DECISION_RIGHT
ACTION_DECISION_RIGHT
```

Until 05 defines the executable mechanism:

```text
authority semantics are closed
authority administration mechanism is not yet closed
```

This is a downstream governance dependency, not an 04 authority ambiguity.

---

# 17. Default Deny

**[ARCHITECTURAL CLOSURE]**

For every consequential operation:

```text
if no valid authority source resolves
=> DENY
```

No fallback exists to:

```text
Owner
Facilitator
object author
AI recommendation
authenticated user
highest role
system administrator
```

unless the operation explicitly permits that authority source.

---

# 18. Authority Failure Behavior

Authority failure is not a state transition failure that may be retried under a different interpretation.

On authority failure:

```text
operation denied
canonical state unchanged
no compensating domain mutation
no AI fallback
no role escalation
no silent Owner override
```

The denial must be auditable where the operation is consequential or security relevant.

Exact audit schema remains 09.

---

# 19. Audit Requirement for Authority Decisions

Every consequential authority evaluation must be reconstructable with at least semantic access to:

```text
actor identity
actor type
claimed role/binding
operation
scope
authority source
authority preconditions evaluated
authority result
denial reason if denied
related human decision reference where required
System-derived authority basis where used
timestamp
correlation to requested transition
```

04 defines the semantic requirement.

09 defines the event/schema representation.

---

# 20. Authority Evaluation Order

Authority evaluation must follow this semantic order:

```text
1. resolve actor identity
2. resolve Workspace scope
3. resolve operation
4. resolve object/current state from 03
5. resolve explicit source authority if any
6. resolve HumanAuthorityBinding if required
7. resolve System-derived authority if explicitly allowed
8. resolve human decision prerequisite if required
9. resolve delegation validity
10. reject AI authority substitution
11. return ALLOW or DENY
```

Authority evaluation does not itself commit the state transition.

03 transition evaluation still applies.

---

# 21. AUTH-DEP-CH-001: Create Challenge

```text
OPERATION:
CREATE_CHALLENGE

ACTOR:
HUMAN_USER

IDENTITY:
Authenticated User.

ROLE:
Facilitator.

DECISION RIGHT:
No separate substantive decision right required to create the Challenge record.

OPERATION AUTHORITY:
Yes, Facilitator may create Challenge.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT.
MVP acceptance explicitly says a Facilitator can create a Challenge.

AUTHORITY SCOPE:
Workspace in which Facilitator role/binding is valid.

AUTHORITY PRECONDITIONS:
Authenticated identity.
Active Workspace membership.
Facilitator role valid in target Workspace.

DELEGATION STATUS:
No implicit delegation.
Workspace governance may change Facilitator binding through 05.
AI delegation prohibited.

HUMAN DECISION REQUIREMENT:
No separate human decision object required.

SYSTEM-DERIVED AUTHORITY:
None in current architecture.

AI PERMITTED ROLE:
May assist drafting Challenge text if later permitted.

AI PROHIBITED ROLE:
May not create Challenge under its own authority.
May not assign itself Facilitator authority.

ALLOW CONDITION:
Authenticated Facilitator in target Workspace plus 03 structural preconditions.

DENY CONDITION:
Actor unauthenticated.
Facilitator role not valid in target Workspace.
AI/System attempts direct creation without explicit later authority path.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Challenge remains absent.

AUDIT REQUIREMENT:
Record actor, Workspace, Facilitator authority source and result.
```

---

# 22. AUTH-DEP-SESS-001: Create Session

```text
OPERATION:
CREATE_SESSION

ACTOR:
HUMAN_USER

IDENTITY:
Authenticated User.

ROLE:
SessionControlAuthority holder.
Facilitator is eligible in facilitated mode.

DECISION RIGHT:
No separate substantive decision right.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE AC-04-002.

AUTHORITY SCOPE:
Target Challenge within one Workspace.

AUTHORITY PRECONDITIONS:
Valid HumanAuthorityBinding for SESSION_CONTROL_RIGHT.
Challenge exists.
Workspace scope valid.

DELEGATION STATUS:
No implicit delegation.
Binding may be changed only through 05 governance.

HUMAN DECISION REQUIREMENT:
Human request to create/start an inquiry Session.

SYSTEM-DERIVED AUTHORITY:
None for Session creation in current architecture.

AI PERMITTED ROLE:
May not be authority source.
May later assist setup after Session exists.

AI PROHIBITED ROLE:
May not create autonomous Session.

ALLOW CONDITION:
Authenticated SessionControlAuthority holder plus 03 preconditions.

DENY CONDITION:
No controller binding.
Workspace mismatch.
AI-only request.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Session remains absent.

AUDIT REQUIREMENT:
Record controller binding and scope.
```

---

# 23. AUTH-DEP-SESS-002: Begin Setup

```text
OPERATION:
BEGIN_SETUP

ACTOR:
HUMAN_USER

IDENTITY:
Authenticated User.

ROLE:
SessionControlAuthority holder.

DECISION RIGHT:
No separate substantive decision right.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE AC-04-002.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Valid controller binding.
Session = DRAFT.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human procedural request only.

SYSTEM-DERIVED AUTHORITY:
Not required.

AI PERMITTED ROLE:
None required.

AI PROHIBITED ROLE:
May not advance Session.

ALLOW CONDITION:
Controller authority plus 03 preconditions.

DENY CONDITION:
No binding.
Wrong Session scope.
AI-only request.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain DRAFT.

AUDIT REQUIREMENT:
Record procedural authority evaluation.
```

---

# 24. AUTH-DEP-SESS-003: Begin Challenge Capture

```text
OPERATION:
BEGIN_CHALLENGE_CAPTURE

ACTOR:
HUMAN_USER

IDENTITY:
Authenticated User.

ROLE:
SessionControlAuthority holder.

DECISION RIGHT:
No separate substantive decision right.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Valid controller binding.
Session = SETUP.
Method-required setup proof exists.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Procedural human request.

SYSTEM-DERIVED AUTHORITY:
None required.

AI PERMITTED ROLE:
May assist with context only after permitted by later AI contract.

AI PROHIBITED ROLE:
May not advance state.

ALLOW CONDITION:
Controller authority plus 03 conditions.

DENY CONDITION:
No controller binding.
Setup incomplete.
AI-only request.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain SETUP.

AUDIT REQUIREMENT:
Trace actor, scope and authority binding.
```

---

# 25. AUTH-DEP-SESS-004: Open Question Generation

```text
OPERATION:
OPEN_QUESTION_GENERATION

ACTOR:
HUMAN_USER

IDENTITY:
Authenticated User.

ROLE:
Facilitator within Session scope.

DECISION RIGHT:
No separate substantive decision right.

OPERATION AUTHORITY:
Direct source right to start Question Burst.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT.

AUTHORITY SCOPE:
QuestionBurst and Session being facilitated.

AUTHORITY PRECONDITIONS:
Facilitator authority valid for Session.
03 Burst and Session preconditions satisfied.

DELEGATION STATUS:
No implicit delegation.
AI prohibited.

HUMAN DECISION REQUIREMENT:
Human Facilitator requests start.

SYSTEM-DERIVED AUTHORITY:
System may execute the validated transition after Facilitator request.
System is executor, not source of discretionary authority.

AI PERMITTED ROLE:
None during Human-only start authority.

AI PROHIBITED ROLE:
May not start protected Human-only Burst.

ALLOW CONDITION:
Authenticated Facilitator plus 03 bundle preconditions.

DENY CONDITION:
Non-Facilitator without explicit source-equivalent binding.
AI request.
Invalid Session/Burst state.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Session and Burst remain in prior states.

AUDIT REQUIREMENT:
Record Facilitator start authority and transition bundle.
```

---

# 26. AUTH-DEP-SESS-005: Close Question Generation

```text
OPERATION:
CLOSE_QUESTION_GENERATION

ACTOR:
HUMAN_USER or SYSTEM_SERVICE.

IDENTITY:
Authenticated Facilitator for human path.
Identified timer/orchestration service for System path.

ROLE:
Human path: Facilitator.
System path: bounded timer authority.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
Human Facilitator may end Burst.
System may complete Burst only under timer-derived authority.

AUTHORITY SOURCE:
Human path: LEVEL_1_EXPLICIT.
System path: SYSTEM_DERIVED from source timer behavior.

AUTHORITY SCOPE:
Specific active/paused QuestionBurst.

AUTHORITY PRECONDITIONS:
Human:
Facilitator authority valid.
System:
Configured timer semantics have resolved CONFLICT-007 and GAP-03-002.
Timer condition deterministically satisfied.
03 freeze preconditions pass.

DELEGATION STATUS:
Human authority not delegated to System.
System path is independently derived procedural authority.

HUMAN DECISION REQUIREMENT:
No human decision required for timer expiry.
Human Facilitator may end early where source permits.

SYSTEM-DERIVED AUTHORITY:
Yes, timer completion only.

AI PERMITTED ROLE:
None as authority source.

AI PROHIBITED ROLE:
May not end Burst because analysis is ready or model decides enough Questions exist.

ALLOW CONDITION:
Either valid Facilitator end request OR valid System timer condition, plus 03 completion proof.

DENY CONDITION:
AI-driven completion.
Timer semantics unresolved at runtime.
Unauthorized human.
Capture consistency unresolved.

AUTHORITY FAILURE BEHAVIOR:
Deny completion.
No raw-set freeze.

AUDIT REQUIREMENT:
Record whether authority source was Facilitator or timer System authority.
```

---

# 27. AUTH-DEP-SESS-006: Begin Analysis

> **Post-baseline materialization note (2026-09-25, F04 WU-04.0):** the
> human path is materialized as `CMD_BEGIN_ANALYSIS`, held by
> `SESSION_CONTROL_RIGHT` at exactly `SESSION:<id>` (BINDING; HD-1 / HD-9
> narrowing). By **HD-16** (16 §41 REC-018 / NQ-DEC-044) the committed Command
> creates exactly one operation authorization (BEGIN_ANALYSIS, AIOP-001),
> executed right after the commit by a SYSTEM_SERVICE under the typed effect-gate
> source **SYSTEM_OPERATION** of **HD-17** (REC-019 / NQ-DEC-045), which is
> *not* SYSTEM_DERIVED. The System path above (SYSTEM_DERIVED, method-derived)
> is not materialized and stays REQUIRE/DENY under D8 (BND-011/012). Nothing
> above is rewritten. Field report: `docs/implementation/field-reports/F04/`.

```text
OPERATION:
BEGIN_ANALYSIS

ACTOR:
HUMAN_USER or SYSTEM_SERVICE.

IDENTITY:
Authenticated SessionControlAuthority holder for human path.
Identified orchestration service for System path.

ROLE:
Human path: SessionControlAuthority holder.
System path: procedural orchestrator.

DECISION RIGHT:
None.
Beginning required post-Burst analysis is not a human substantive decision.

OPERATION AUTHORITY:
Human controller may request.
System may begin automatically if approved InquiryMethod explicitly requires post-Burst analysis.

AUTHORITY SOURCE:
Human: ARCHITECTURAL_CLOSURE.
System: SYSTEM_DERIVED.

AUTHORITY SCOPE:
Specific Session after valid Burst completion.

AUTHORITY PRECONDITIONS:
03 frozen raw-set proof.
AI analysis is allowed only post-Burst.
System path requires approved method rule and no unresolved D8 method-authority conflict for that configured method version.

DELEGATION STATUS:
Not human-to-System delegation.
System authority is procedural.

HUMAN DECISION REQUIREMENT:
None.

SYSTEM-DERIVED AUTHORITY:
Yes, bounded to starting required analysis.

AI PERMITTED ROLE:
AI may execute analysis once operation is authorized.

AI PROHIBITED ROLE:
AI may not authorize its own invocation.
AI may not advance Session state by returning output.

ALLOW CONDITION:
Valid human controller request OR approved deterministic method trigger, plus 03 preconditions.

DENY CONDITION:
Burst not completed/frozen.
AI self-trigger without System authorization.
Method rule not approved.
Workspace/context boundary fails.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Session remains QUESTION_CAPTURE.

AUDIT REQUIREMENT:
Record authority source and method/system rule if System-derived.
```

---

# 28. AUTH-DEP-SESS-007: Begin Reflection

```text
OPERATION:
BEGIN_REFLECTION

ACTOR:
HUMAN_USER or SYSTEM_SERVICE.

IDENTITY:
Authenticated controller or identified orchestration service.

ROLE:
Human: SessionControlAuthority.
System: procedural orchestrator.

DECISION RIGHT:
None.

OPERATION AUTHORITY:
Human controller may request.
System may transition when required analysis has validly completed under approved method.

AUTHORITY SOURCE:
Human: ARCHITECTURAL_CLOSURE.
System: SYSTEM_DERIVED.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
03 AI_VALIDATION_PROOF.
No analysis failure.
Approved method permits deterministic progression.

DELEGATION STATUS:
No human-decision delegation involved.

HUMAN DECISION REQUIREMENT:
None.

SYSTEM-DERIVED AUTHORITY:
Yes, conditional and non-discretionary.

AI PERMITTED ROLE:
May produce analysis and reflection prompts.

AI PROHIBITED ROLE:
May not declare its own analysis authoritative enough to advance state.
May not make the human reflection.

ALLOW CONDITION:
Human controller request or deterministic System rule plus valid analysis proof.

DENY CONDITION:
Invalid/unvalidated AI output.
AI self-authorization.
Missing controller/System authority.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain ANALYSIS.

AUDIT REQUIREMENT:
Record analysis proof reference and authority source.
```

---

# 29. AUTH-DEP-SESS-008: Begin Question Selection

```text
OPERATION:
BEGIN_QUESTION_SELECTION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.

DECISION RIGHT:
No selection decision occurs merely by opening the phase.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Reflection completion proof required by 03.
Controller binding valid.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human procedural confirmation of Reflection completion where required by later closure.
Actual Question selection requires separate QUESTION_SELECTION_RIGHT.

SYSTEM-DERIVED AUTHORITY:
Not enabled until GAP-03-007 Reflection completion semantics are closed.

AI PERMITTED ROLE:
May provide reflection prompts or candidate summaries.

AI PROHIBITED ROLE:
May not decide Reflection complete.
May not select Questions.

ALLOW CONDITION:
Controller authority plus Reflection completion proof.

DENY CONDITION:
Only UI navigation.
Only AI output.
No controller binding.
Reflection completion unresolved.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain REFLECTION.

AUDIT REQUIREMENT:
Record controller authority and completion proof basis.
```

---

# 30. AUTH-DEP-SESS-009: Begin Investigation

```text
OPERATION:
BEGIN_INVESTIGATION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.

DECISION RIGHT:
Question selection decision must already exist from QUESTION_SELECTION_RIGHT holder.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Valid compelling selection.
Exactly one primary selection where method requires.
Complete ImpactChain where required.
Selection was created by valid Question Selection Authority.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Yes, but the required human decision is the prior Question selection, not this operation authorization.

SYSTEM-DERIVED AUTHORITY:
Not required.

AI PERMITTED ROLE:
May recommend investigation paths.

AI PROHIBITED ROLE:
May not substitute for primary Question selection.

ALLOW CONDITION:
Controller authority plus valid human selection prerequisites.

DENY CONDITION:
Only AI recommendation exists.
Selection authority invalid.
ImpactChain incomplete.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain QUESTION_SELECTION.

AUDIT REQUIREMENT:
Link transition authority to selection authority evidence.
```

---

# 31. AUTH-DEP-SESS-010: Begin Experiment Phase

```text
OPERATION:
BEGIN_EXPERIMENT_PHASE

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.

DECISION RIGHT:
No Experiment authorization is implied by phase entry.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Investigation completion semantics satisfied.
Required Evidence conditions, if any, satisfied.
Controller binding valid.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
No Experiment execution decision is created by this phase transition.

SYSTEM-DERIVED AUTHORITY:
Not enabled while GAP-03-008 Investigation completion semantics remain open.

AI PERMITTED ROLE:
May propose Experiment candidates.

AI PROHIBITED ROLE:
May not authorize Experiment.
May not use proposal existence to advance Session.

ALLOW CONDITION:
Controller authority plus valid 03 preconditions.

DENY CONDITION:
Investigation completion not established.
AI proposal is sole basis.
No controller authority.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain INVESTIGATION.

AUDIT REQUIREMENT:
Record controller authority and phase-completion proof.
```

---

# 32. AUTH-DEP-SESS-011: Begin Action Phase

```text
OPERATION:
BEGIN_ACTION_PHASE

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
Operation requester must hold SESSION_CONTROL_RIGHT.
Human substantive decision must come from ACTION_DECISION_RIGHT holder.

DECISION RIGHT:
ACTION_DECISION_RIGHT required.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT required to request/authorize technical phase transition.

AUTHORITY SOURCE:
Both rights: ARCHITECTURAL_CLOSURE grounded in LEVEL 1 Human Agency.

AUTHORITY SCOPE:
Specific Session/Challenge.

AUTHORITY PRECONDITIONS:
Valid human Action decision exists.
Experiment phase meets 03 completion condition.
Both bindings valid.
Required Evidence conditions satisfied where later required.

DELEGATION STATUS:
No implicit delegation.
AI delegation prohibited.

HUMAN DECISION REQUIREMENT:
Yes.

SYSTEM-DERIVED AUTHORITY:
System may execute commit after both human authority conditions are satisfied.
System may not create the Action decision.

AI PERMITTED ROLE:
May recommend action.
May summarize Experiment result/Evidence.

AI PROHIBITED ROLE:
May not hold ACTION_DECISION_RIGHT.
May not auto-advance Session because recommendation score is high.

ALLOW CONDITION:
Valid Action human decision plus valid Session operation authority plus 03 preconditions.

DENY CONDITION:
Missing Action decision.
Missing controller authority.
AI-only recommendation.
Experiment not in valid condition.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain EXPERIMENT.

AUDIT REQUIREMENT:
Record both human decision authority and operation authority separately.
```

---

# 33. AUTH-DEP-SESS-012: Begin Review

```text
OPERATION:
BEGIN_REVIEW

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.

DECISION RIGHT:
No new substantive decision right by default.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Action-phase completion assertion valid under later closure.
Controller binding valid.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human responsibility for Action completion remains.
No separate Decision object required merely to open Review.

SYSTEM-DERIVED AUTHORITY:
Not enabled while GAP-03-009 remains unresolved.

AI PERMITTED ROLE:
May summarize recorded outcomes.

AI PROHIBITED ROLE:
May not assert external-world Action completion.

ALLOW CONDITION:
Controller authority plus valid Action completion proof.

DENY CONDITION:
Only UI navigation.
Only AI inference that action occurred.
No controller authority.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain ACTION.

AUDIT REQUIREMENT:
Record controller authority and completion basis.
```

---

# 34. AUTH-DEP-SESS-013: Close Session

```text
OPERATION:
CLOSE_SESSION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.

DECISION RIGHT:
No separate source-defined substantive decision.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Session = REVIEW.
Review completion proof exists.
No unresolved INDETERMINATE transition affects Session.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human procedural closure request.

SYSTEM-DERIVED AUTHORITY:
No autonomous close path in current architecture.

AI PERMITTED ROLE:
May prepare review summary.

AI PROHIBITED ROLE:
May not close Session.

ALLOW CONDITION:
Controller authority plus 03 closure preconditions.

DENY CONDITION:
Unresolved failure.
No controller.
AI/system auto-close attempt.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain REVIEW.

AUDIT REQUIREMENT:
Record human closure authority.
```

---

# 35. AUTH-DEP-BURST-001: Prepare Burst

```text
OPERATION:
PREPARE_BURST

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated SessionControlAuthority holder.

ROLE:
SessionControlAuthority.
Facilitator eligible in facilitated mode.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
SESSION_CONTROL_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Session exists.
Controller binding valid.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
No separate human decision.

SYSTEM-DERIVED AUTHORITY:
None.

AI PERMITTED ROLE:
None required.

AI PROHIBITED ROLE:
May not create autonomous Burst.

ALLOW CONDITION:
Controller authority plus 03 structure.

DENY CONDITION:
No controller.
AI-only request.

AUTHORITY FAILURE BEHAVIOR:
Deny, Burst absent.

AUDIT REQUIREMENT:
Trace preparation authority if required by later audit policy.
```

---

# 36. AUTH-DEP-BURST-002: Start Burst

> **Post-baseline prototype narrowing (2026-09-24, F02 WU-02.12):** for the
> current prototype, Burst start is closed by a current Session-scoped
> `SESSION_CONTROL_RIGHT` binding at `SESSION:<session_id>`, not by the
> Facilitator role + ACTIVE Session FacilitatorScopeBinding described in
> this section. Human decision HD-9, 16 §41 REC-009 / NQ-DEC-037. This
> section is preserved unchanged as the architecture's broader model, which
> stays OPEN for production (16 NQ-GAP-080).


```text
OPERATION:
START_BURST

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
Facilitator.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
Direct source right.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT.

AUTHORITY SCOPE:
Specific Session/Burst the Facilitator controls.

AUTHORITY PRECONDITIONS:
Facilitator authority valid.
03 start conditions satisfied.

DELEGATION STATUS:
No implicit delegation.
AI prohibited.

HUMAN DECISION REQUIREMENT:
Human start request.

SYSTEM-DERIVED AUTHORITY:
System executes validated transition only after human request.

AI PERMITTED ROLE:
None during Human-only Burst start.

AI PROHIBITED ROLE:
May not start Burst.

ALLOW CONDITION:
Authenticated Facilitator plus structural eligibility.

DENY CONDITION:
Non-Facilitator without explicit later binding.
AI request.
Invalid Burst state.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain PREPARED.

AUDIT REQUIREMENT:
Record Facilitator authority.
```

---

# 37. AUTH-DEP-BURST-003: Pause Burst

```text
OPERATION:
PAUSE_BURST

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
Facilitator.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
Direct source right.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT.

AUTHORITY SCOPE:
Specific active Burst.

AUTHORITY PRECONDITIONS:
Facilitator authority valid.
Burst ACTIVE.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human pause request.

SYSTEM-DERIVED AUTHORITY:
None.

AI PERMITTED ROLE:
None.

AI PROHIBITED ROLE:
May not pause based on content evaluation.

ALLOW CONDITION:
Facilitator plus ACTIVE state.

DENY CONDITION:
Unauthorized actor.
Wrong state.
AI request.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain ACTIVE.

AUDIT REQUIREMENT:
Record pause authority.
```

---

# 38. AUTH-DEP-BURST-004: Resume Burst

LEVEL 1 gives Facilitator pause/end authority but does not explicitly mention resume.

Resume is structurally required once PAUSED exists.

```text
OPERATION:
RESUME_BURST

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
Facilitator.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
Facilitator resume right.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE derived from source pause authority.

AUTHORITY SCOPE:
Specific paused Burst.

AUTHORITY PRECONDITIONS:
Same Facilitator scope requirement as pause.
Burst PAUSED.
Session compatible.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human resume request.

SYSTEM-DERIVED AUTHORITY:
None.

AI PERMITTED ROLE:
None.

AI PROHIBITED ROLE:
May not resume Burst.

ALLOW CONDITION:
Valid Facilitator authority plus 03 preconditions.

DENY CONDITION:
Unauthorized actor.
Wrong state.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain PAUSED.

AUDIT REQUIREMENT:
Record resume authority.
```

---

# 39. AUTH-DEP-BURST-005: Complete Burst

> **Post-baseline prototype narrowing (2026-09-24, F02 WU-02.12):** for the
> current prototype, Burst manual completion (human path) is closed by a current Session-scoped
> `SESSION_CONTROL_RIGHT` binding at `SESSION:<session_id>`, not by the
> Facilitator role + ACTIVE Session FacilitatorScopeBinding described in
> this section. Human decision HD-9, 16 §41 REC-009 / NQ-DEC-037. This
> section is preserved unchanged as the architecture's broader model, which
> stays OPEN for production (16 NQ-GAP-080).


```text
OPERATION:
COMPLETE_BURST

ACTOR:
HUMAN_USER or SYSTEM_SERVICE.

IDENTITY:
Authenticated Facilitator or identified timer service.

ROLE:
Facilitator or bounded System timer authority.

DECISION RIGHT:
No substantive inquiry decision.

OPERATION AUTHORITY:
Facilitator end right or System timer completion authority.

AUTHORITY SOURCE:
Human: LEVEL_1_EXPLICIT.
System: SYSTEM_DERIVED from source timer behavior.

AUTHORITY SCOPE:
Specific active/paused Burst.

AUTHORITY PRECONDITIONS:
Human path:
Facilitator authority valid.
System path:
Resolved timer semantics.
03 raw-set freeze conditions.
No contamination.

DELEGATION STATUS:
System timer authority is not delegated human authority.

HUMAN DECISION REQUIREMENT:
No human decision for timer expiry.
Human may end via Facilitator source right.

SYSTEM-DERIVED AUTHORITY:
Yes, timer completion only.

AI PERMITTED ROLE:
None as authority source.

AI PROHIBITED ROLE:
May not determine Burst is complete based on semantic content.

ALLOW CONDITION:
Valid Facilitator or deterministic timer authority plus 03 proof.

DENY CONDITION:
AI-driven end.
Unresolved timer rule.
Unauthorized human.
Capture inconsistency.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Burst remains prior state.

AUDIT REQUIREMENT:
Record authority path and timer basis if System.
```

---

# 40. AUTH-DEP-Q-001: Capture Burst Question

> **Post-baseline materialization note (2026-09-24, F03 WU-03.0):** the
> "direct source participation right" is materialized as a current
> `SessionParticipation` (09 §28, admitted per 16 §41 REC-006 / REC-015),
> recorded at the effect gate as the typed authority source **PARTICIPATION**
> (reference = the participation id, scope `SESSION:<id>`; 16 §41 REC-016 /
> NQ-DEC-043; `20_SYSTEM_FIELD_ENGINEERING.md` §7 successor note). "Input
> satisfies protected Burst rule" is the prototype form rule of 16 §41
> REC-013 / NQ-DEC-040. Nothing above is rewritten.

```text
OPERATION:
CAPTURE_BURST_QUESTION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User participating in the Session.

ROLE:
Session Participant.
Workspace role label alone is not sufficient or necessary unless later governance requires it.

DECISION RIGHT:
Right to author and submit own Question during active Burst.

OPERATION AUTHORITY:
Direct source participation right.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT:
participants submit Questions.

AUTHORITY SCOPE:
Specific active QuestionBurst in which User participates.

AUTHORITY PRECONDITIONS:
Authenticated User.
Valid SessionParticipation.
Burst ACTIVE.
Input satisfies protected Burst rule.
Workspace scope matches.

DELEGATION STATUS:
Question authorship/submission right is personal to participant identity.
No AI delegation.

HUMAN DECISION REQUIREMENT:
Human authors Question.

SYSTEM-DERIVED AUTHORITY:
System captures/persists after valid submission.
System does not author Question.

AI PERMITTED ROLE:
Observer/recorder only according unresolved GAP-01-003.
No semantic authority during protected Human-only Burst.

AI PROHIBITED ROLE:
May not submit disguised human Question.
May not evaluate or rewrite Question before canonical capture.

ALLOW CONDITION:
Authenticated participant plus 03 input eligibility and boundary checks.

DENY CONDITION:
Not a participant.
Burst not ACTIVE.
Answer/explanation under protected mode.
AI-origin input in Human-only mode.
Cross-Workspace context.

AUTHORITY FAILURE BEHAVIOR:
Deny input.
No Question created.

AUDIT REQUIREMENT:
Capture author identity and Session/Burst context.
```

---

# 41. AUTH-DEP-SEL-001: Select Compelling Question

```text
OPERATION:
SELECT_COMPELLING_QUESTION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
QuestionSelectionAuthority holder.
No generic Workspace role is sufficient.

DECISION RIGHT:
QUESTION_SELECTION_RIGHT.

OPERATION AUTHORITY:
Same explicit human authority binding.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT human/user selection requirement
+
ARCHITECTURAL_CLOSURE AC-04-003 for exact holder binding.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Valid QuestionSelectionAuthority binding.
Session QUESTION_SELECTION.
Question belongs to Session Challenge.

DELEGATION STATUS:
No implicit delegation.
AI cannot receive binding.

HUMAN DECISION REQUIREMENT:
Yes.

SYSTEM-DERIVED AUTHORITY:
System may persist/validate human selection.
System may not choose.

AI PERMITTED ROLE:
Recommend candidate Questions.
Explain derived classifications.

AI PROHIBITED ROLE:
Create authority-bearing selection.
Rank result as automatic selection.

ALLOW CONDITION:
Authorized human selection holder plus 03 cardinality and scope rules.

DENY CONDITION:
AI-only recommendation.
Unauthenticated human.
No binding.
Wrong Session/Question scope.

AUTHORITY FAILURE BEHAVIOR:
Deny.
No selection relation created.

AUDIT REQUIREMENT:
Record human selector identity and authority binding.
```

---

# 42. AUTH-DEP-SEL-002: Select Primary Question

```text
OPERATION:
SELECT_PRIMARY_QUESTION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
QuestionSelectionAuthority holder.

DECISION RIGHT:
QUESTION_SELECTION_RIGHT.

OPERATION AUTHORITY:
Same explicit human binding.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT human/user primary selection
+
ARCHITECTURAL_CLOSURE for collaborative holder resolution.

AUTHORITY SCOPE:
Specific Session.

AUTHORITY PRECONDITIONS:
Valid binding.
Question eligible.
No conflicting primary selection unless governed replacement is defined.

DELEGATION STATUS:
No implicit delegation.
AI prohibited.

HUMAN DECISION REQUIREMENT:
Yes.

SYSTEM-DERIVED AUTHORITY:
System may validate cardinality and persist.

AI PERMITTED ROLE:
Recommend candidate.
Surface impact-related context.

AI PROHIBITED ROLE:
Auto-select highest score.
Replace current primary Question.

ALLOW CONDITION:
Authorized human decision and 03 conditions.

DENY CONDITION:
AI-only selection.
No authority binding.
Conflicting primary selection under unresolved GAP-03-018.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Existing selection state preserved.

AUDIT REQUIREMENT:
Record human primary selection authority.
```

---

# 43. AUTH-DEP-ASM-001: Begin Assumption Test

```text
OPERATION:
BEGIN_ASSUMPTION_TEST

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
AssumptionInterpretationAuthority holder.

DECISION RIGHT:
ASSUMPTION_INTERPRETATION_RIGHT.

OPERATION AUTHORITY:
Explicit human authority binding.

AUTHORITY SOURCE:
LEVEL 1 Human Agency for interpretation
+
ARCHITECTURAL_CLOSURE AC-04-004.

AUTHORITY SCOPE:
Specific Assumption/Challenge.

AUTHORITY PRECONDITIONS:
Binding valid.
Assumption belongs to Workspace scope.
Test context exists.

DELEGATION STATUS:
No implicit delegation.
AI prohibited from holding right.

HUMAN DECISION REQUIREMENT:
Yes, human elects to test/retest the Assumption.

SYSTEM-DERIVED AUTHORITY:
System may create/process test workflow after human request.

AI PERMITTED ROLE:
Detect Assumption.
Suggest test.
Suggest observations.

AI PROHIBITED ROLE:
Self-initiate authoritative TESTING transition solely from model inference.

ALLOW CONDITION:
Authorized human interpretation holder plus 03 preconditions.

DENY CONDITION:
AI-only request.
No authority binding.
Cross-Workspace object.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Assumption state unchanged.

AUDIT REQUIREMENT:
Record human authority and test initiation.
```

---

# 44. AUTH-DEP-ASM-002: Classify Assumption Test Result

```text
OPERATION:
CLASSIFY_ASSUMPTION_TEST_RESULT

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
AssumptionInterpretationAuthority holder.

DECISION RIGHT:
ASSUMPTION_INTERPRETATION_RIGHT.

OPERATION AUTHORITY:
Explicit human authority binding.

AUTHORITY SOURCE:
LEVEL 1 Human Agency for interpretation
+
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Assumption.

AUTHORITY PRECONDITIONS:
Binding valid.
Assumption TESTING.
07 evidence requirements satisfied.
Evidence validation authority resolved.

DELEGATION STATUS:
No AI delegation.

HUMAN DECISION REQUIREMENT:
Yes.

SYSTEM-DERIVED AUTHORITY:
System validates structure and commits after human classification decision.
System does not choose target state.

AI PERMITTED ROLE:
Summarize Evidence.
Recommend SUPPORTED/WEAK/REFUTED/UNKNOWN.
Identify contradictions.

AI PROHIBITED ROLE:
Authorize target classification.
Use confidence as evidence.

ALLOW CONDITION:
Human interpretation decision plus valid 07 evidence proof and 03 conditions.

DENY CONDITION:
Only AI recommendation.
Evidence validation unresolved.
No human authority binding.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Remain TESTING.

AUDIT REQUIREMENT:
Record human classifier, evidence basis reference and authority source.
```

---

# 45. AUTH-DEP-EXP-002: Begin Human Experiment Consideration

```text
OPERATION:
BEGIN_HUMAN_EXPERIMENT_CONSIDERATION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
ExperimentDecisionAuthority holder.

DECISION RIGHT:
EXPERIMENT_DECISION_RIGHT.

OPERATION AUTHORITY:
Explicit human binding.

AUTHORITY SOURCE:
LEVEL 1 Human responsibility for experiments
+
ARCHITECTURAL_CLOSURE AC-04-005.

AUTHORITY SCOPE:
Specific Experiment.

AUTHORITY PRECONDITIONS:
Experiment PROPOSED.
Binding valid.
Origin/provenance distinguishable.

DELEGATION STATUS:
No AI delegation.

HUMAN DECISION REQUIREMENT:
Yes, human adopts proposal for consideration.

SYSTEM-DERIVED AUTHORITY:
System may persist transition after valid human request.

AI PERMITTED ROLE:
Create Experiment proposal.

AI PROHIBITED ROLE:
Adopt its own proposal into human consideration.

ALLOW CONDITION:
Human Experiment authority plus 03 conditions.

DENY CONDITION:
AI self-adoption.
No binding.
Wrong Workspace scope.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain PROPOSED.

AUDIT REQUIREMENT:
Record human adoption authority and proposal origin.
```

---

# 46. AUTH-DEP-EXP-003: Authorize Experiment

```text
OPERATION:
AUTHORIZE_EXPERIMENT

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
ExperimentDecisionAuthority holder.

DECISION RIGHT:
EXPERIMENT_DECISION_RIGHT.

OPERATION AUTHORITY:
Explicit human binding.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT human responsibility for experiments
+
ARCHITECTURAL_CLOSURE.

AUTHORITY SCOPE:
Specific Experiment.

AUTHORITY PRECONDITIONS:
Experiment UNDER_CONSIDERATION.
Required evidence/method criteria satisfied.
Binding valid.

DELEGATION STATUS:
No AI delegation.
Human-to-human reassignment only through 05 governance.

HUMAN DECISION REQUIREMENT:
Yes.

SYSTEM-DERIVED AUTHORITY:
System commits after human authorization.
System may not create authorization decision.

AI PERMITTED ROLE:
Recommend Experiment.
Analyze expected signals.
Summarize Evidence.

AI PROHIBITED ROLE:
Authorize execution.

ALLOW CONDITION:
Valid human Experiment decision authority plus 03/07 preconditions.

DENY CONDITION:
Only AI recommendation.
No binding.
Evidence requirement unsatisfied where mandatory.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain UNDER_CONSIDERATION.

AUDIT REQUIREMENT:
Record human authorizer and decision basis references.
```

---

# 47. AUTH-DEP-EXP-004: Start Experiment

```text
OPERATION:
START_EXPERIMENT

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
ExperimentDecisionAuthority holder or separately bound ExperimentExecutionAuthority if 05 later separates them.

DECISION RIGHT:
The Experiment authorization decision must already exist.

OPERATION AUTHORITY:
Current architecture reuses EXPERIMENT_DECISION_RIGHT for execution start.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE grounded in Human responsibility for experiments.

AUTHORITY SCOPE:
Specific Experiment.

AUTHORITY PRECONDITIONS:
Experiment AUTHORIZED.
Human authority binding valid.
Execution prerequisites satisfied.

DELEGATION STATUS:
No implicit delegation.
Automated execution not authorized by current source.

HUMAN DECISION REQUIREMENT:
Prior human Experiment authorization required.

SYSTEM-DERIVED AUTHORITY:
No autonomous System start path in current architecture.

AI PERMITTED ROLE:
May provide execution guidance.

AI PROHIBITED ROLE:
Start Experiment.

ALLOW CONDITION:
Authorized Experiment plus human execution authority.

DENY CONDITION:
No human authority.
Experiment not AUTHORIZED.
AI/system autonomous start.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain AUTHORIZED.

AUDIT REQUIREMENT:
Record human execution-start authority.
```

---

# 48. AUTH-DEP-EXP-005: Complete Experiment

```text
OPERATION:
COMPLETE_EXPERIMENT

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
ExperimentDecisionAuthority holder or later explicit completion authority.

DECISION RIGHT:
Human asserts Experiment execution has concluded.

OPERATION AUTHORITY:
Current architecture uses EXPERIMENT_DECISION_RIGHT.

AUTHORITY SOURCE:
ARCHITECTURAL_CLOSURE grounded in Human responsibility for experiments.

AUTHORITY SCOPE:
Specific Experiment.

AUTHORITY PRECONDITIONS:
Experiment IN_PROGRESS.
Result/completion information valid.
Binding valid.

DELEGATION STATUS:
No implicit delegation.

HUMAN DECISION REQUIREMENT:
Human completion assertion required under current architecture.

SYSTEM-DERIVED AUTHORITY:
None currently.
Automated measurement completion would require later explicit closure.

AI PERMITTED ROLE:
Summarize result.
Suggest learning.

AI PROHIBITED ROLE:
Declare real-world Experiment complete under own authority.

ALLOW CONDITION:
Valid human completion authority plus 03 conditions.

DENY CONDITION:
AI-only completion.
No human binding.
Experiment not IN_PROGRESS.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain IN_PROGRESS.

AUDIT REQUIREMENT:
Record completion authority and result provenance.
```

---

# 49. AUTH-DEP-DEC-001: Open Decision Consideration

```text
OPERATION:
OPEN_DECISION_CONSIDERATION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
DecisionAuthority holder.

DECISION RIGHT:
DECISION_RIGHT.

OPERATION AUTHORITY:
Explicit human authority binding.

AUTHORITY SOURCE:
LEVEL 1 Human responsibility for decisions
+
ARCHITECTURAL_CLOSURE AC-04-006.

AUTHORITY SCOPE:
Specific Decision/Challenge.

AUTHORITY PRECONDITIONS:
Binding valid.
Decision Question context valid.
Workspace scope valid.

DELEGATION STATUS:
No AI delegation.

HUMAN DECISION REQUIREMENT:
Yes, human opens an actual decision process.

SYSTEM-DERIVED AUTHORITY:
System may persist/open process after human request.

AI PERMITTED ROLE:
Suggest Decision questions/options/criteria.

AI PROHIBITED ROLE:
Open a human Decision process under its own authority.

ALLOW CONDITION:
Authorized human Decision holder plus 03 conditions.

DENY CONDITION:
AI-only request.
No binding.
Cross-Workspace context.

AUTHORITY FAILURE BEHAVIOR:
Deny.
Decision remains absent.

AUDIT REQUIREMENT:
Record human decision-process authority.
```

---

# 50. AUTH-DEP-DEC-002: Record Human Decision

```text
OPERATION:
RECORD_HUMAN_DECISION

ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated User.

ROLE:
DecisionAuthority holder.

DECISION RIGHT:
DECISION_RIGHT.

OPERATION AUTHORITY:
Explicit human authority binding.

AUTHORITY SOURCE:
LEVEL_1_EXPLICIT Human Agency
+
ARCHITECTURAL_CLOSURE for exact holder.

AUTHORITY SCOPE:
Specific Decision.

AUTHORITY PRECONDITIONS:
Decision UNDER_CONSIDERATION.
Binding valid.
Required options/criteria/evidence conditions satisfied.
Selected option/rationale explicitly adopted by human.

DELEGATION STATUS:
No AI delegation.
No implicit Owner/Facilitator substitution.

HUMAN DECISION REQUIREMENT:
Yes, mandatory.

SYSTEM-DERIVED AUTHORITY:
System may commit the human decision record only after authority validation.
System may not choose selected option.

AI PERMITTED ROLE:
Prepare options.
Summarize criteria.
Surface Evidence.
Recommend.

AI PROHIBITED ROLE:
Hold Decision Right.
Select final option as human authority.
Convert recommendation into DECIDED automatically.

ALLOW CONDITION:
Valid human Decision Right plus 03 and 07 prerequisites.

DENY CONDITION:
Only AI recommendation.
No human authority binding.
Evidence requirement unresolved where mandatory.
Selected option not explicitly human-adopted.

AUTHORITY FAILURE BEHAVIOR:
Deny, remain UNDER_CONSIDERATION.

AUDIT REQUIREMENT:
Record human decision maker, authority binding, selected option and decision trace.
```

---

# 51. Operations Without 03 AUTH-DEP but Authority-Relevant

03 exposed the required transition authority surface.

04 also records two cross-cutting authority operations required for governance correctness.

## 51.1 ASSIGN_HUMAN_AUTHORITY_BINDING

```text
ACTOR:
HUMAN_USER.

IDENTITY:
Authenticated Workspace Owner governance root.

ROLE:
Workspace Governance Authority.

DECISION RIGHT:
WORKSPACE_GOVERNANCE_RIGHT.

OPERATION AUTHORITY:
May assign scope-bounded human authority binding.

AUTHORITY SOURCE:
AC-04-001.

SCOPE:
Same Workspace only.

DELEGATION:
May bind other human Users.
May not bind AI to human decision rights.

FAILURE:
Default deny.

AUTHORITATIVE EXECUTION HOME:
05 Governance Inside System.
```

## 51.2 REVOKE_HUMAN_AUTHORITY_BINDING

Same governance root and scope rules apply.

Revocation mechanics and effects on in-flight transitions belong to 05/10.

---

# 52. Owner Does Not Mean Superuser

The following are expressly prohibited:

```text
Workspace owner_id exists
=> Owner may execute any transition

Owner role label exists
=> Owner may decide every Decision

Owner created Workspace
=> Owner may override human decision holder

Owner wants operation
=> authority checks bypassed
```

Workspace Owner is governance root under AC-04-001.

Execution authority remains operation-specific.

---

# 53. Facilitator Does Not Mean Decision Maker

Source-explicit Facilitator rights are:

```text
create Challenge
start Burst
pause Burst
end Burst
```

04 additionally permits Facilitator eligibility for Session Control Authority.

This does not grant by role alone:

```text
Question Selection Right
Assumption Interpretation Right
Experiment Decision Right
Decision Right
Action Decision Right
```

A Facilitator may hold those rights only through separate explicit bindings.

---

# 54. Participant Does Not Mean General Contributor Authority

Session participation grants the source-specific Question submission right during active Burst.

It does not grant:

```text
Session control
Question primary selection
Decision authority
Experiment authorization
Assumption classification
Export authority
Workspace governance
```

unless separately bound later.

---

# 55. AI Authority Model

## 55.1 AI permitted

AI may act as:

```text
proposal generator
classifier
clusterer
reframer
assumption detector
perspective generator
insight synthesizer
experiment designer
reflection coach
research assistant
strategic recommender
```

where source/mode permits.

## 55.2 AI prohibited

AI may never act as:

```text
Workspace governance authority
HumanAuthorityBinding grantor
Question Selection Authority
Assumption Interpretation Authority
Experiment Decision Authority
Decision Authority
Action Decision Authority
Session Control Authority
Facilitator for source-bound human control operations unless a future source-authorized AI facilitator mode explicitly defines bounded non-human authority
```

## 55.3 D2 AI autonomy remains open

LEVEL 1 D2 asks how proactive AI should be.

04 does not resolve D2 by granting authority.

AI proactivity may change:

```text
when AI may propose
when AI may ask
when AI may initiate non-consequential analysis
```

It may not erase Human Decision Authority.

## 55.4 AI Facilitator Version 2

LEVEL 1 Version 2 includes AI facilitator.

That future capability does not retroactively grant AI the source-defined human Facilitator authority used in current transitions.

A later architecture extension must distinguish:

```text
facilitation behavior
from
human operation authority
```

---

# 56. System Authority Model

System may hold bounded procedural authority only where explicitly stated in 04.

Current System-derived authority paths:

```text
QuestionBurst completion by timer, after timer semantics close
Begin Analysis under approved deterministic method
Begin Reflection under approved deterministic method and valid AI analysis proof
transition commit execution after human authority validation
persistence after valid transition decision
```

System may not derive authority for:

```text
primary Question selection
Assumption interpretation
Experiment authorization
human Decision
Action decision
Workspace authority grant
```

---

# 57. Human Authorship Does Not Equal Authority

A human who authored:

```text
Question
Assumption
Experiment proposal
Decision option
Evidence entry
```

does not automatically gain authority to:

```text
select it
validate it
authorize it
execute it
decide it
classify it
```

Authorship is provenance.

Authority is separate.

---

# 58. Human Decision Does Not Equal Transition Authorization

Example:

```text
Human Action decision exists
```

does not automatically mean:

```text
Session may enter ACTION
```

03 structural preconditions and 04 operation authority must also pass.

Likewise:

```text
Decision DECIDED
```

does not automatically authorize an unrelated downstream state transition.

---

# 59. Transition Authorization Does Not Equal Executed State

Authority resolution may return:

```text
ALLOW
```

and the transition may still:

```text
fail precommit
become indeterminate
fail persistence
fail audit consistency
```

Only 03 `COMMITTED` outcome establishes actual state.

---

# 60. Delegation Matrix

| Authority class | Human-to-human reassignment | AI delegation | System-derived substitute |
|---|---|---|---|
| Workspace Governance Right | Through 05 only | Prohibited | No |
| Session Control Right | Through 05 only | Prohibited | Limited procedural paths explicitly listed |
| Question Selection Right | Through 05 only | Prohibited | No |
| Assumption Interpretation Right | Through 05 only | Prohibited | No |
| Experiment Decision Right | Through 05 only | Prohibited | No |
| Decision Right | Through 05 only | Prohibited | No |
| Action Decision Right | Through 05 only | Prohibited | No |
| Burst timer completion | N/A | Prohibited | Yes, deterministic timer only |

---

# 61. Authority Source Precedence

When multiple apparent authority claims exist, apply:

```text
1. LEVEL_1_EXPLICIT source right
2. approved ARCHITECTURAL_CLOSURE
3. valid EXPLICIT_AUTHORITY_BINDING
4. explicitly permitted SYSTEM_DERIVED authority
5. otherwise DENY
```

Role labels not bound by one of these sources have no consequential authority.

---

# 62. Authority Conflict Rules

## 62.1 Explicit denial wins over lower-order apparent permission

If a boundary or governance rule denies an operation:

```text
role label
cannot override denial
```

## 62.2 AI cannot override human authority failure

If no valid human decision holder exists:

```text
AI recommendation
does not fill the gap
```

## 62.3 System cannot self-expand

A System service cannot derive authority merely because:

```text
transition is convenient
workflow is blocked
human is unavailable
AI confidence is high
```

---

# 63. GAP-04-001: Collaborative Question Selection Rule

**Status:** `[OPEN]`

LEVEL 1 says:

```text
users can select 1 to 3 compelling Questions
one Question can be selected as most important
```

It does not define in collaborative Sessions:

```text
who gets selection authority
whether one human or several humans select
whether Facilitator decides
whether participants vote
whether consensus is required
```

04 closes the need for explicit `QUESTION_SELECTION_RIGHT`.

The assignment policy remains open.

This is prototype-critical if collaborative Question Burst is in the Minimum Closed Prototype.

---

# 64. GAP-04-002: Workspace Owner Governance Semantics Beyond Authority Binding

**Status:** `[UNDERDEFINED]`

AC-04-001 establishes Workspace Owner as governance root because a root is structurally required.

LEVEL 1 does not specify:

```text
co-owners
owner transfer
owner removal
owner succession
emergency governance
```

05 must expose governance behavior.

No further authority is inferred here.

---

# 65. GAP-04-003: Individual Inquiry Authority Bootstrap

**Status:** `[ARCHITECTURAL CLOSURE REQUIREMENT]`

LEVEL 1 supports individual inquiry.

An individual Workspace still needs:

```text
Workspace governance root
Session Control Authority
Question Selection Authority
and where applicable
Decision/Experiment/Action authority
```

04 permits the same authenticated human to hold multiple explicit bindings.

It does not collapse the bindings into one generic superuser right.

05 must define the bootstrap flow.

---

# 66. GAP-04-004: Session Control Multiplicity

**Status:** `[UNDERDEFINED]`

LEVEL 1 does not specify whether a Session may have:

```text
one controller
multiple co-facilitators
controller handoff
```

04 requires at least one valid SessionControlAuthority holder.

Multiplicity policy remains open.

---

# 67. GAP-04-005: Facilitator Scope Binding

**Status:** `[UNDERDEFINED]`

LEVEL 1 names Facilitator but does not specify whether Facilitator role is:

```text
Workspace-wide
Challenge-specific
Session-specific
```

02 places role semantics on WorkspaceMembership.

High assurance requires the operation to resolve exact scope.

05/09 must define how a Workspace Facilitator is bound to a specific Session/Challenge for source-explicit rights.

Until then:

```text
Facilitator label alone
does not authorize control of every Session in the Workspace.
```

---

# 68. GAP-04-006: Authority Revocation During Active Operation

**Status:** `[UNDERDEFINED]`

If authority is revoked while:

```text
Session is active
Decision is under consideration
Experiment is authorized/in progress
```

the source does not define in-flight effects.

05/10 must resolve:

```text
revocation effective immediately
graceful completion
operation-specific freeze
reassignment requirement
```

No silent continuation is assumed.

---

# 69. GAP-04-007: System Timer Identity and Trust

**Status:** `[UNDERDEFINED]`

System timer completion requires:

```text
trusted service identity
configured duration semantics
tamper-resistant authoritative clock basis
```

03 already preserves CONFLICT-007 and GAP-03-002.

04 adds the authority requirement that client-side timer expiry alone is not sufficient System authority.

11/09 must define trusted execution/telemetry basis.

---

# 70. GAP-04-008: Method Approval Authority and System-Derived Transitions

**Status:** `[OPEN]`

System-derived authority for:

```text
Begin Analysis
Begin Reflection
```

depends on an approved InquiryMethod rule.

D8 Methodology governance remains open:

```text
Who owns and approves the inquiry methodology encoded in the system?
```

Therefore System-derived authority may be architecturally defined, but no unapproved method configuration may grant it.

05 must bind methodology governance to System authority.

---

# 71. GAP-04-009: Decision Authority Assignment Policy

**Status:** `[OPEN]`

LEVEL 1 says humans decide but does not define whether Decision Right follows:

```text
Workspace Owner
Facilitator
Challenge owner
named decision maker
organizational hierarchy
Session participant
another human authority
```

04 requires explicit object-scoped DecisionAuthority binding.

The binding policy remains open.

This is required before Decision tracking can be high-assurance.

---

# 72. GAP-04-010: Experiment Authority Assignment Policy

**Status:** `[OPEN]`

LEVEL 1 says humans remain responsible for experiments.

It does not define which human.

04 requires explicit ExperimentDecisionAuthority binding.

Assignment policy remains open.

---

# 73. GAP-04-011: Action Decision Assignment Policy

**Status:** `[OPEN]`

LEVEL 1 says humans remain responsible for actions.

It does not identify the action decision holder.

04 requires explicit ActionDecisionAuthority binding.

Assignment policy remains open.

---

# 74. GAP-04-012: Assumption Interpretation Authority Assignment Policy

**Status:** `[OPEN]`

LEVEL 1 says humans remain responsible for interpretation.

It does not define which human may classify an Assumption.

04 requires explicit binding.

Assignment policy remains open.

---

# 75. GAP-04-013: Export Authority

**Status:** `[OPEN]`

Export is source-required and must be controlled.

03 did not expose Export as a state transition AUTH-DEP.

04 cannot silently assign export rights to Owner or Facilitator based on LEVEL 2.

05/06/09/12 must define:

```text
who may export
scope
redaction
derived-content inclusion
audit inclusion
```

No current role receives export authority in 04.

---

# 76. GAP-04-014: Membership Administration Authority

**Status:** `[ARCHITECTURAL CLOSURE REQUIREMENT]`

AC-04-001 makes Workspace Owner the governance root.

05 must define exact operations for:

```text
invite/add member
remove member
assign Workspace role
change role
revoke role
```

until then, the root semantic authority exists but execution contract is not closed.

---

# 77. GAP-04-015: AI Facilitator Future Authority

**Status:** `[DEFERRED]`

Version 2 includes AI facilitator.

Current architecture does not permit AI to inherit source-defined human Facilitator authority.

Future extension must explicitly define whether AI facilitation is:

```text
advisory only
procedural System authority
or another governed mode
```

Human decision rights remain non-transferable.

---

# 78. Authority Dependency Resolution Matrix

| AUTH-DEP | Operation | Authority status |
|---|---|---|
| AUTH-DEP-CH-001 | Create Challenge | `[SPECIFIED]` Facilitator |
| AUTH-DEP-SESS-001 | Create Session | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-002 | Begin Setup | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-003 | Begin Challenge Capture | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-004 | Open Question Generation | `[SPECIFIED]` Facilitator |
| AUTH-DEP-SESS-005 | Close Question Generation | `[SPECIFIED]` Facilitator + `[SYSTEM_DERIVED]` timer |
| AUTH-DEP-SESS-006 | Begin Analysis | `[ARCHITECTURAL CLOSURE]` controller or bounded System |
| AUTH-DEP-SESS-007 | Begin Reflection | `[ARCHITECTURAL CLOSURE]` controller or bounded System |
| AUTH-DEP-SESS-008 | Begin Question Selection | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-009 | Begin Investigation | `[ARCHITECTURAL CLOSURE]` controller + prior valid human selection |
| AUTH-DEP-SESS-010 | Begin Experiment Phase | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-011 | Begin Action Phase | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority + ActionDecisionAuthority |
| AUTH-DEP-SESS-012 | Begin Review | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-SESS-013 | Close Session | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-BURST-001 | Prepare Burst | `[ARCHITECTURAL CLOSURE]` SessionControlAuthority |
| AUTH-DEP-BURST-002 | Start Burst | `[SPECIFIED]` Facilitator |
| AUTH-DEP-BURST-003 | Pause Burst | `[SPECIFIED]` Facilitator |
| AUTH-DEP-BURST-004 | Resume Burst | `[ARCHITECTURAL CLOSURE]` Facilitator |
| AUTH-DEP-BURST-005 | Complete Burst | `[SPECIFIED]` Facilitator + `[SYSTEM_DERIVED]` timer |
| AUTH-DEP-Q-001 | Capture Burst Question | `[SPECIFIED]` Session Participant |
| AUTH-DEP-SEL-001 | Select Compelling Question | `[SPECIFIED HUMAN RIGHT + CLOSURE HOLDER BINDING]` |
| AUTH-DEP-SEL-002 | Select Primary Question | `[SPECIFIED HUMAN RIGHT + CLOSURE HOLDER BINDING]` |
| AUTH-DEP-ASM-001 | Begin Assumption Test | `[ARCHITECTURAL CLOSURE]` AssumptionInterpretationAuthority |
| AUTH-DEP-ASM-002 | Classify Assumption Result | `[ARCHITECTURAL CLOSURE]` AssumptionInterpretationAuthority |
| AUTH-DEP-EXP-002 | Begin Experiment Consideration | `[SPECIFIED HUMAN RESPONSIBILITY + CLOSURE HOLDER BINDING]` |
| AUTH-DEP-EXP-003 | Authorize Experiment | `[SPECIFIED HUMAN RESPONSIBILITY + CLOSURE HOLDER BINDING]` |
| AUTH-DEP-EXP-004 | Start Experiment | `[ARCHITECTURAL CLOSURE]` human Experiment authority |
| AUTH-DEP-EXP-005 | Complete Experiment | `[ARCHITECTURAL CLOSURE]` human Experiment authority |
| AUTH-DEP-DEC-001 | Open Decision Consideration | `[SPECIFIED HUMAN RESPONSIBILITY + CLOSURE HOLDER BINDING]` |
| AUTH-DEP-DEC-002 | Record Human Decision | `[SPECIFIED HUMAN RESPONSIBILITY + CLOSURE HOLDER BINDING]` |

No AUTH-DEP remains without an authority path.

Several binding-assignment policies remain OPEN and block high-assurance baseline freeze until the relevant prototype path is resolved.

---

# 79. Authority Matrix Correction Against LEVEL 2

LEVEL 2 proposed a prototype authority matrix assigning broad permissions to:

```text
Owner
Facilitator
Contributor
Observer
Viewer
AI/System
```

04 does not adopt that matrix as source truth.

Corrections:

```text
Owner
!= automatic operation superuser

Facilitator
= source rights only where LEVEL 1 explicitly says so
+ eligibility for SessionControlAuthority through closure

Contributor
!= automatic Question submit right
Session Participation is the source-backed submit right

Observer
Viewer
= no consequential authority by label

AI/System
must be separated
AI != System procedural authority
```

This preserves `CONFLICT-004`.

---

# 80. Authority Closure Validation: 00

## Result

**PASS**

04 preserves:

```text
Human Decision Authority
Governance Before Consequence
one authoritative home
AI recommendation != human decision
AI confidence != authority
```

No 00 reconstruction required.

---

# 81. Authority Closure Validation: 01

## Result

**PASS**

04 preserves:

```text
authentication != authority
Workspace scope
human / AI boundary
method configuration != runtime authority
external provider != product authority
```

No 01 reconstruction required.

---

# 82. Authority Closure Validation: 02

## Result

**PASS**

04 preserves:

```text
THING != RELATION != STATE != EVENT != AUTHORITY != EVIDENCE != PROJECTION != CONFIGURATION

WorkspaceMembership is relation, not authority itself

SessionParticipation is relation and only gains source-specific submit authority where LEVEL 1 grants it

human authorship != authority

AI generation != authority

origin != authority
```

No domain object or relation is added to patch authority.

HumanAuthorityBinding is an authority construct, not a 02 domain object.

No 02 reconstruction required.

---

# 83. Authority Closure Validation: 03

## Result

**PASS**

Every AUTH-DEP exposed by 03 now has one of:

```text
LEVEL_1_EXPLICIT authority
ARCHITECTURAL_CLOSURE authority
SYSTEM_DERIVED authority
explicit HumanAuthorityBinding requirement
```

04 does not modify:

```text
Session topology
QuestionBurst topology
Assumption topology
Experiment topology
Decision topology
transition preconditions
illegal transition paths
```

No 03 transition is rendered authority-impossible.

No 03 reconstruction required.

---

# 84. Coherent Legitimate Authority Path Validation

## Challenge creation

**CLOSED**

Facilitator has source authority.

## Session orchestration

**CLOSED STRUCTURALLY**

SessionControlAuthority provides a legitimate human control path.

Assignment/governance mechanics remain 05 work.

## Burst start/pause/end

**CLOSED**

Facilitator source rights.

Timer completion path conditional on unresolved timer semantics.

## Question submission

**CLOSED**

Authenticated Session Participant.

## Question selection

**CLOSED STRUCTURALLY, POLICY OPEN**

Human QuestionSelectionAuthority required.

Collaborative holder policy remains open.

## Assumption classification

**CLOSED STRUCTURALLY, POLICY OPEN**

Human AssumptionInterpretationAuthority required.

Assignment policy and 07 evidence semantics remain open.

## Experiment authorization

**CLOSED STRUCTURALLY, POLICY OPEN**

Human ExperimentDecisionAuthority required.

Assignment policy remains open.

## Decision finalization

**CLOSED STRUCTURALLY, POLICY OPEN**

Human DecisionAuthority required.

Assignment policy remains open.

## Action transition

**CLOSED STRUCTURALLY, POLICY OPEN**

Human ActionDecisionAuthority plus SessionControlAuthority required.

Assignment policy remains open.

---

# 85. New Architectural Closures Introduced in 04

| ID | Addition | Status | Reason |
|---|---|---|---|
| AC-04-001 | Workspace owner_id is Workspace governance root, not execution superuser | `[ARCHITECTURAL CLOSURE]` | Required to bootstrap source-defined members/permissions without role-superuser collapse |
| AC-04-002 | Explicit SessionControlAuthority binding | `[ARCHITECTURAL CLOSURE]` | Required to close Session procedural authority across individual/facilitated modes |
| AC-04-003 | Explicit QuestionSelectionAuthority binding | `[ARCHITECTURAL CLOSURE]` | Source requires human/user selection but does not identify collaborative holder |
| AC-04-004 | Explicit AssumptionInterpretationAuthority binding | `[ARCHITECTURAL CLOSURE]` | Human interpretation must remain authority-bearing |
| AC-04-005 | Explicit ExperimentDecisionAuthority binding | `[ARCHITECTURAL CLOSURE]` | Human experiment responsibility must be executable |
| AC-04-006 | Explicit DecisionAuthority binding | `[ARCHITECTURAL CLOSURE]` | Human decision responsibility must be executable |
| AC-04-007 | Explicit ActionDecisionAuthority binding | `[ARCHITECTURAL CLOSURE]` | Human action responsibility must remain separate from transition operation |
| AC-04-008 | HumanAuthorityBinding as scope-bounded authority construct | `[ARCHITECTURAL CLOSURE]` | Prevents role labels/authorship from becoming implicit authority |
| AC-04-009 | No implicit/transitive delegation | `[ARCHITECTURAL CLOSURE]` | High-assurance authority containment |
| AC-04-010 | Human decision authority cannot be delegated to AI | `[ARCHITECTURAL CLOSURE]` | Human Agency invariant |
| AC-04-011 | System-derived procedural authority model | `[ARCHITECTURAL CLOSURE]` | Allows deterministic automation without converting System/AI into decision maker |
| AC-04-012 | All human consequential mutations require authenticated User identity | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 authentication MVP + security chain |
| AC-04-013 | System consequential actor requires identifiable service identity | `[ARCHITECTURAL CLOSURE]` | Auditability and authority reconstruction |
| AC-04-014 | Default deny when no authority source resolves | `[ARCHITECTURAL CLOSURE]` | High-assurance fail-closed authority |
| AC-04-015 | Owner governance right does not imply domain-operation authority | `[ARCHITECTURAL CLOSURE]` | Prevents superuser collapse |
| AC-04-016 | Facilitator source rights do not imply human Decision Rights | `[ARCHITECTURAL CLOSURE]` | Prevents facilitation/decision collapse |
| AC-04-017 | Question submission authority derives from Session participation, not Contributor label | `[ARCHITECTURAL CLOSURE]` | LEVEL 1 says participants submit |
| AC-04-018 | AI and System are separate actor/authority classes | `[ARCHITECTURAL CLOSURE]` | Prevents AI output from inheriting procedural System authority |

---

# 86. New Gaps Exposed in 04

```text
GAP-04-001 Collaborative Question Selection Rule
GAP-04-002 Workspace Owner governance semantics beyond authority binding
GAP-04-003 Individual inquiry authority bootstrap
GAP-04-004 Session Control multiplicity
GAP-04-005 Facilitator scope binding
GAP-04-006 Authority revocation during active operation
GAP-04-007 System timer identity and trust
GAP-04-008 Method approval authority for System-derived transitions
GAP-04-009 Decision Authority assignment policy
GAP-04-010 Experiment Authority assignment policy
GAP-04-011 Action Decision Authority assignment policy
GAP-04-012 Assumption Interpretation Authority assignment policy
GAP-04-013 Export Authority
GAP-04-014 Membership administration authority execution
GAP-04-015 AI Facilitator future authority
```

All remain classified exactly in their sections.

---

# 87. Baseline-Blocking Authority Items

The following are high-assurance baseline blockers **if their affected capability is inside the Minimum Closed Prototype**:

```text
GAP-04-001 Collaborative Question Selection Rule
GAP-04-003 Individual inquiry authority bootstrap
GAP-04-005 Facilitator scope binding
GAP-04-008 Method approval authority for System-derived transitions
GAP-04-009 Decision Authority assignment policy, if Decision tracking is prototype scope
GAP-04-010 Experiment Authority assignment policy, if Experiments are prototype scope
GAP-04-011 Action Decision Authority assignment policy, if ACTION phase is executable in prototype
GAP-04-012 Assumption Interpretation Authority assignment policy, if Assumption status mutation is prototype scope
GAP-04-013 Export Authority
GAP-04-014 Membership administration authority execution
```

Prototype scope remains authoritative in 12 and is not resolved here.

---

# 88. Readiness for 05

04 now provides 05 with an executable authority model to govern.

05 must define how governance enforces:

```text
Workspace governance root
HumanAuthorityBinding creation
binding revocation
binding scope
Facilitator scope
Session control assignment
Question selection authority assignment
Assumption interpretation authority assignment
Experiment decision authority assignment
Decision authority assignment
Action decision authority assignment
System-derived authority activation
method approval relation to System authority
default deny
authority audit
```

05 must not:

```text
invent new state transitions
turn Owner into superuser
turn Facilitator into universal decision maker
turn HumanAuthorityBinding into domain ownership
grant human decision rights to AI
treat System and AI as equivalent
```

## Readiness result

**READY FOR HUMAN REVIEW**

`04_AUTHORITY_AND_DECISION_RIGHTS.md` is structurally ready to become the authoritative Authority and Decision Rights input for `05_GOVERNANCE_INSIDE_SYSTEM.md`.

No AUTH-DEP from 03 lacks a coherent authority path.

Open assignment policies remain explicit and are not silently resolved.

05 is not yet authorized.

No downstream architecture file has been built.

No implementation work has begun.

No Architecture Baseline has been frozen.

---

# 89. Stop Gate

**STOP CONDITION REACHED**

Await human review and explicit:

```text
HUMAN_REVIEW::04_APPROVED
GO::BUILD_05_GOVERNANCE_INSIDE_SYSTEM
```
