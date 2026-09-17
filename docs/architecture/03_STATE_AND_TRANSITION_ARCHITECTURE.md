# 03_STATE_AND_TRANSITION_ARCHITECTURE

**Project:** N.Q.U.I.R.Y.  
**Document role:** Authoritative state and transition architecture  
**Architecture stage:** D, State + Transition Architecture  
**Upstream authority:** `00_NQUIRY_MASTER_ARCHITECTURE.md`, `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md`, `02_DOMAIN_AND_RELATION_MODEL.md`  
**LEVEL 1 authority:** `N.Q.U.I.R.Y. - Product & System Specification`  
**LEVEL 2 input:** `# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md`  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 04 not yet authorized

---

# 0. Document Authority

This file is authoritative for:

```text
state ownership
state vocabularies
state semantics
legal state-transition topology
transition eligibility structure
transition preconditions
transition proof requirements
transition allow and deny conditions
next-state semantics
state-preserving consequential mutations
cross-object state consistency
transition failure outcomes
transition recovery requirements
implicit-transition prohibition
AI-to-canonical-state leak prevention
```

This file is not authoritative for:

```text
operation-level actor-to-role authorization
role-action matrices
human decision-right allocation
authority delegation
governance implementation
boundary implementation
universal provenance schemas
evidence-validation schemas
database transaction design
API wire contracts
audit persistence design
recovery algorithm implementation
prototype scope
```

Those facts remain in later authoritative modules.

Where this file requires authority, it records an `AUTHORITY DEPENDENCY`.

It does not resolve the Authority Matrix belonging to 04.

---

# 1. High-Assurance State Principle

Consequential system state must not emerge merely because any of the following occurred:

```text
AI output was generated
AI output was persisted
a UI control was activated
a request was authenticated
an actor has a role label
a confidence score is high
derived analysis exists
an event was emitted
a database row was inserted
```

For a consequential state transition to be valid, the architecture must be able to reconstruct:

```text
CURRENT STATE
REQUESTED TRANSITION
ACTOR
AUTHORITY REQUIREMENT
PRECONDITIONS
REQUIRED EVIDENCE
BOUNDARY DEPENDENCIES
ALLOW CONDITION
DENY CONDITION
NEXT STATE
PERSISTENCE CONSEQUENCE
AUDIT CONSEQUENCE
FAILURE STATE
RECOVERY / ROLLBACK REQUIREMENT
```

This is the 03 specialization of the approved transition closure invariant in 00.

---

# 2. State Is Not Authority

State expresses:

```text
where an object or process currently is
```

State does not express:

```text
who may move it
why movement is legitimate
whether an actor has authority
whether evidence is sufficient
whether AI agrees
```

Therefore:

```text
STATE
!= AUTHORITY

ROLE LABEL
!= AUTHORITY

AUTHENTICATION
!= AUTHORITY

AI CONFIDENCE
!= AUTHORITY

EVENT OCCURRENCE
!= AUTHORITY
```

04 must resolve authority independently from the state topology defined here.

---

# 3. State Is Not Event

An event may record that a transition was:

```text
requested
allowed
denied
committed
failed
recovered
```

The event does not create the state by existing.

The state change is the result of an authorized and valid transition commit.

Therefore:

```text
event emitted
!= state transition committed
```

This preserves the approved 02 invariant:

```text
EVENT != STATE
```

---

# 4. State Is Not Persistence

Persistence is a mechanism through which state may be durably represented.

Persistence is not the semantic cause of state.

Therefore:

```text
row exists
!= transition valid

AI result stored
!= human decision

derived object stored
!= canonical authority state
```

A persistence write that violates a transition contract is invalid system state, not a new architectural fact.

---

# 5. State Is Not Epistemic Truth

The approved 02 invariant remains authoritative:

```text
canonical persistence
!= epistemic truth
```

Examples:

```text
Assumption status UNKNOWN
does not mean the assumption is false.

Assumption status SUPPORTED
does not mean the assumption is universally true.

AI-derived Insight persisted
does not mean the Insight is evidence.

Decision persisted
does not prove the decision was authorized unless its transition path establishes that fact.
```

---

# 6. Consequence Progression Model

The architecture distinguishes five different consequence stages.

These are not one universal object-state enum.

They are different architectural dimensions.

```text
1. PROPOSAL
2. HUMAN CONSIDERATION
3. HUMAN DECISION
4. TRANSITION AUTHORIZATION
5. EXECUTED / ACTUAL SYSTEM STATE
```

## 6.1 Proposal

A proposal may be:

```text
AI-generated
human-generated
imported
derived
```

A proposal may be persisted.

Persistence does not grant authority.

## 6.2 Human consideration

A human may inspect, compare, modify or consider a proposal.

Consideration does not equal a decision.

## 6.3 Human decision

Where LEVEL 1 assigns responsibility to a human, the relevant human decision must be separately represented or reconstructable.

Human decision does not by itself mean the requested system transition is executable.

## 6.4 Transition authorization

A requested transition must satisfy the authority requirements defined later in 04, plus all structural preconditions and boundaries.

Authorization is transition-specific.

## 6.5 Executed / actual system state

The target state becomes actual only when the transition commits.

Therefore:

```text
AI proposal
!= human consideration
!= human decision
!= authorized transition
!= executed state
```

This separation is an `[ARCHITECTURAL CLOSURE]` required by:

```text
LEVEL 1 Human Agency
00 Human Decision Authority
01 Human / AI Boundary
02 origin != authority
current high-assurance mandate
```

---

# 7. Transition Proof Types

The `REQUIRED EVIDENCE` field in transition contracts is typed to avoid collapsing domain Evidence with system proof.

## 7.1 SYSTEM_PROOF

A fact required to establish transition eligibility.

Examples:

```text
object exists
current state matches
required relation exists
QuestionBurst is completed
raw capture set is frozen
five Impact levels exist
```

SYSTEM_PROOF is not a domain Evidence object.

## 7.2 DOMAIN_EVIDENCE

A source-defined Evidence object or validated evidentiary relation required for an epistemic or decision consequence.

Validation semantics remain authoritative in 07.

## 7.3 HUMAN_DECISION

A human decision is not evidence.

It is an authority-bearing prerequisite where required.

It belongs under `AUTHORITY REQUIREMENT`, not `REQUIRED EVIDENCE`.

## 7.4 AI_VALIDATION_PROOF

A proof that an AI operation:

```text
completed
returned contract-valid output
passed required validation
```

This proves processing validity.

It does not prove truth or authority.

---

# 8. Transition Execution Outcomes

These are transition-attempt outcomes, not domain-object states.

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

## 8.1 DENIED

The transition is not eligible or not authorized.

Invariant:

```text
canonical state remains unchanged
```

## 8.2 FAILED_PRECOMMIT

A technical or validation failure occurs before commit.

Invariant:

```text
canonical state remains unchanged
```

## 8.3 COMMITTED

All required conditions are satisfied and target state becomes canonical.

## 8.4 INDETERMINATE

The system cannot prove whether the consequential transition committed completely and consistently.

High-assurance rule:

```text
no further consequential transition may rely on the uncertain result
until recovery/reconciliation establishes the last valid state.
```

Exact quarantine, replay, rollback and reconciliation mechanisms belong to 10.

This transition-outcome model is `[ARCHITECTURAL CLOSURE]`.

---

# 9. Transition Commit Rule

A consequential transition may commit only if all of the following resolve positively:

```text
current state
requested transition
actor identity
authority dependency
structural preconditions
required transition proof
required domain evidence where applicable
workspace scope
boundary dependencies
object invariants
cross-object invariants
```

A transition is denied if any required condition is known false.

A transition must not commit when any required condition remains unknown.

Therefore:

```text
UNKNOWN REQUIRED CONDITION
=> DENY / DO NOT COMMIT
```

unless a later authoritative module explicitly defines an allowed indeterminate policy for that transition.

---

# 10. Audit Consequence Rule

Every consequential transition must have a defined audit consequence.

The exact atomicity mechanism remains open under:

```text
DEC-A007 Audit atomicity
```

03 therefore does not silently declare state write and audit write technically atomic.

High-assurance requirement:

```text
a consequential transition cannot be considered architecture-complete
until 09/10 resolve how state and audit remain reconstructably consistent.
```

If audit consequence fails and commit status cannot be proven, transition outcome is:

```text
INDETERMINATE
```

until 10 resolves recovery semantics.

---

# 11. State Ownership Inventory

The approved 02 state-ownership map is refined as follows.

| Object / process | State status in 03 |
|---|---|
| User | No lifecycle state defined |
| Workspace | No lifecycle state defined |
| Challenge | Source `status` exists, vocabulary remains unresolved |
| Session | Explicit LEVEL 1 state machine, fully modeled in 03 |
| QuestionBurst | Lifecycle strongly implied, state vocabulary closed in 03 |
| Question | Source `status` exists, vocabulary remains unresolved |
| Assumption | Source state vocabulary exists, transition topology closed in 03 |
| Insight | No lifecycle state defined |
| Evidence | No lifecycle state defined in 03 |
| Experiment | Source `status` exists, high-assurance vocabulary closed in 03 |
| Decision | No source status, high-assurance lifecycle introduced in 03 |
| Journey | No lifecycle state defined |
| ImpactChain | Structural completeness, no lifecycle enum |
| QuestionCluster | No lifecycle state |
| AIGeneration | Lifecycle remains delegated to 08/09 |
| AuditEvent | Event, not state owner |

---

# 12. Challenge State Treatment

LEVEL 1 defines:

```text
Challenge.status
```

but provides no values.

## 12.1 GAP-02-012 preserved

**Status:** `[UNDERDEFINED]`

03 does not invent:

```text
OPEN
ACTIVE
CLOSED
ARCHIVED
```

or any other Challenge status vocabulary.

## 12.2 High-assurance rule

Until Challenge status vocabulary is authoritatively defined:

```text
Challenge.status
must not be used as:
transition guard
authority predicate
boundary predicate
prototype acceptance condition
```

## 12.3 Challenge creation

Challenge creation is modeled as an existential transition:

```text
ABSENT
-> PRESENT
```

This does not define `Challenge.status`.

### TRN-CH-001 CREATE_CHALLENGE

```text
CURRENT STATE:
Challenge does not exist.

REQUESTED TRANSITION:
CREATE_CHALLENGE.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-CH-001.
04 must resolve who may create a Challenge.
LEVEL 1 acceptance requires that a Facilitator can create a Challenge.

PRECONDITIONS:
Effective Workspace scope exists.
Actor identity is known.
Required source challenge fields accepted by later contract are available.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Workspace scope.
SYSTEM_PROOF that no conflicting object identity exists.

BOUNDARY DEPENDENCIES:
Identity.
Workspace.
Authority.
Audit.

ALLOW CONDITION:
All preconditions and 04 authority requirement pass.

DENY CONDITION:
Workspace cannot be resolved.
Authority unresolved at runtime.
Required creation contract invalid.
Conflicting identity exists.

NEXT STATE:
Challenge exists.
Challenge.status remains semantically unresolved.

PERSISTENCE CONSEQUENCE:
Create canonical Challenge record.

AUDIT CONSEQUENCE:
Challenge creation must be traceable.

FAILURE STATE:
DENIED or FAILED_PRECOMMIT leaves Challenge absent.
Uncertain write outcome becomes INDETERMINATE.

RECOVERY / ROLLBACK REQUIREMENT:
10 must define reconciliation for uncertain creation.
No duplicate Challenge may be created as a recovery shortcut.
```

---

# 13. Session State Machine

## 13.1 Source-defined states

**[SPECIFIED]**

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

## 13.2 Source-defined topology

LEVEL 1 presents the states as an ordered chain and says critical phases must not be accidentally skipped unless explicitly permitted.

03 therefore defines the default legal topology as:

```text
DRAFT
-> SETUP
-> CHALLENGE_CAPTURE
-> QUESTION_GENERATION
-> QUESTION_CAPTURE
-> ANALYSIS
-> REFLECTION
-> QUESTION_SELECTION
-> INVESTIGATION
-> EXPERIMENT
-> ACTION
-> REVIEW
-> CLOSED
```

No skip transition is legal unless later architecture provides explicit source-supported method semantics and authority.

## 13.3 Session state semantics

The state names are source-defined.

Their execution semantics require closure.

### DRAFT

**[ARCHITECTURAL CLOSURE]**

Session identity exists.

No active inquiry phase has begun.

### SETUP

**[ARCHITECTURAL CLOSURE]**

Session configuration and participation context are being established.

No protected Question Burst is active.

### CHALLENGE_CAPTURE

**[ARCHITECTURAL CLOSURE]**

Challenge context required for the inquiry method is being established or confirmed.

No protected Question Burst is active.

### QUESTION_GENERATION

**[ARCHITECTURAL CLOSURE]**

This is the protected Question Burst input-open phase for the Question Burst method.

Questions may be captured while the phase is active.

The fact that questions are persisted during this state does not advance Session state.

### QUESTION_CAPTURE

**[ARCHITECTURAL CLOSURE]**

Question-generation input is closed.

The raw captured set required by the completed Burst is frozen.

The Session is now eligible to consider post-burst analysis.

This resolves the otherwise ambiguous ordering between source workflow capture and the Session state name.

### ANALYSIS

**[ARCHITECTURAL CLOSURE]**

Post-burst analysis operations may run.

AI output may create derived records.

AI output cannot by itself advance Session state.

### REFLECTION

**[ARCHITECTURAL CLOSURE]**

Human reflection occurs after analysis.

Reflection does not itself equal question selection.

### QUESTION_SELECTION

**[ARCHITECTURAL CLOSURE]**

Human selection of 1 to 3 compelling Questions and one primary Question occurs here.

For the Question Burst method, the Five-Why Impact Chain is anchored here before investigation begins.

### INVESTIGATION

**[ARCHITECTURAL CLOSURE]**

The selected inquiry direction is investigated through observation, research, evidence collection or other method-supported inquiry.

### EXPERIMENT

**[ARCHITECTURAL CLOSURE]**

Experiment proposal, authorization and execution may occur here according to the Experiment state machine.

### ACTION

**[ARCHITECTURAL CLOSURE]**

The inquiry has moved into action phase.

Entry into ACTION does not prove an external real-world action already occurred.

It proves only that the Session has validly entered the action phase.

### REVIEW

**[ARCHITECTURAL CLOSURE]**

Outcome, learning and consequences are reviewed.

### CLOSED

**[ARCHITECTURAL CLOSURE]**

The Session is terminal.

No further transition inside the same Session is legal.

Iteration occurs through new Questions and, where the full inquiry cycle is restarted, a new Session under the same Challenge.

---

# 14. AC-03-001: Iteration Does Not Reopen CLOSED Session

LEVEL 1 requires iterative inquiry and re-questioning.

LEVEL 1 Session state topology ends in CLOSED.

Approved 02 permits multiple Sessions under one Challenge.

03 therefore closes the tension as follows:

```text
CLOSED Session
does not transition back to DRAFT, SETUP or CHALLENGE_CAPTURE.

A new inquiry cycle creates a new Session under the same Challenge.
```

Question-to-Question recursion may still occur inside an active Session through QuestionLineage.

This is `[ARCHITECTURAL CLOSURE]`.

---

# 15. Session Transition Contracts

## TRN-SESS-001 CREATE_SESSION

```text
CURRENT STATE:
Session absent.

REQUESTED TRANSITION:
CREATE_SESSION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-001.
04 must resolve who may create a Session.

PRECONDITIONS:
Challenge exists.
Challenge resolves to exactly one Workspace.
Actor identity is known.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Challenge existence.
SYSTEM_PROOF of Workspace scope.

BOUNDARY DEPENDENCIES:
Identity.
Workspace.
Authority.
Audit.

ALLOW CONDITION:
All structural conditions and authority pass.

DENY CONDITION:
Challenge absent.
Workspace scope unresolved.
Authority denied or unresolved.

NEXT STATE:
DRAFT.

PERSISTENCE CONSEQUENCE:
Create Session record linked to Challenge.

AUDIT CONSEQUENCE:
Session creation trace required.

FAILURE STATE:
Absent if precommit failure.
INDETERMINATE if creation commit cannot be proven.

RECOVERY / ROLLBACK REQUIREMENT:
10 must reconcile uncertain creation without duplicate Session creation.
```

## TRN-SESS-002 BEGIN_SETUP

```text
CURRENT STATE:
DRAFT.

REQUESTED TRANSITION:
BEGIN_SETUP.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-002.

PRECONDITIONS:
Session exists.
Challenge exists.
Workspace scope resolves.

REQUIRED EVIDENCE:
SYSTEM_PROOF of current state and ownership relations.

BOUNDARY DEPENDENCIES:
Identity.
Workspace.
Authority.
State Transition.
Audit.

ALLOW CONDITION:
Current state is exactly DRAFT and authority passes.

DENY CONDITION:
Current state differs.
Required ownership relations are missing.
Authority denied or unresolved.

NEXT STATE:
SETUP.

PERSISTENCE CONSEQUENCE:
Session state becomes SETUP.

AUDIT CONSEQUENCE:
Transition trace required.

FAILURE STATE:
State remains DRAFT unless commit is indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
10 must restore last confirmed state if commit is uncertain.
```

## TRN-SESS-003 BEGIN_CHALLENGE_CAPTURE

```text
CURRENT STATE:
SETUP.

REQUESTED TRANSITION:
BEGIN_CHALLENGE_CAPTURE.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-003.

PRECONDITIONS:
Required Session setup for the selected method is structurally present.

REQUIRED EVIDENCE:
SYSTEM_PROOF that required setup configuration exists.
No epistemic DOMAIN_EVIDENCE required.

BOUNDARY DEPENDENCIES:
Workspace.
Authority.
Methodology.
State Transition.
Audit.

ALLOW CONDITION:
Method-required setup is present and authority passes.

DENY CONDITION:
Required setup missing.
Method configuration unresolved.
Authority denied.

NEXT STATE:
CHALLENGE_CAPTURE.

PERSISTENCE CONSEQUENCE:
Session state becomes CHALLENGE_CAPTURE.

AUDIT CONSEQUENCE:
Transition trace required.

FAILURE STATE:
State remains SETUP unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Return to last confirmed SETUP state if transition did not commit.
```

## TRN-SESS-004 OPEN_QUESTION_GENERATION

This transition is logically coupled to QuestionBurst start.

```text
CURRENT STATE:
CHALLENGE_CAPTURE.

REQUESTED TRANSITION:
OPEN_QUESTION_GENERATION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-004.
LEVEL 1 establishes that a Facilitator can start a Question Burst.
04 must resolve complete operation authority.

PRECONDITIONS:
Challenge capture for the method is complete enough to begin Burst.
A QuestionBurst exists in PREPARED state.
Burst setup requirements are satisfied.
No other active Burst for the same Session is permitted unless later architecture explicitly supports it.

REQUIRED EVIDENCE:
SYSTEM_PROOF of QuestionBurst PREPARED.
SYSTEM_PROOF of challenge context.
SYSTEM_PROOF of required participant/configuration context.

BOUNDARY DEPENDENCIES:
Identity.
Workspace.
Authority.
Question Burst.
Methodology.
State Transition.
Audit.

ALLOW CONDITION:
All preconditions pass and Burst start authority passes.

DENY CONDITION:
Burst absent.
Burst not PREPARED.
Challenge context incomplete.
Competing active Burst.
Authority denied.

NEXT STATE:
Session -> QUESTION_GENERATION.
QuestionBurst -> ACTIVE.

PERSISTENCE CONSEQUENCE:
The Session and Burst state changes form one logical transition bundle.

AUDIT CONSEQUENCE:
Burst start and Session phase transition must be reconstructable together.

FAILURE STATE:
If neither state commits, remain CHALLENGE_CAPTURE/PREPARED.
If one state may have committed without the other, outcome is INDETERMINATE.

RECOVERY / ROLLBACK REQUIREMENT:
10 must reconcile the pair as one logical bundle.
A partial pair is invalid architecture state.
```

## TRN-SESS-005 CLOSE_QUESTION_GENERATION

This transition is logically coupled to QuestionBurst completion.

```text
CURRENT STATE:
QUESTION_GENERATION.

REQUESTED TRANSITION:
CLOSE_QUESTION_GENERATION.

ACTOR:
Human actor or System timer condition.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-005.
LEVEL 1 establishes that a Facilitator can end a Burst.
LEVEL 1 also defines timer end behavior.
04/05 must resolve human versus system completion authority.

PRECONDITIONS:
Associated QuestionBurst is ACTIVE or PAUSED.
No new question input may be accepted after completion commit.
All already-accepted Questions required for the raw set are durably represented or transition cannot commit.

REQUIRED EVIDENCE:
SYSTEM_PROOF of associated Burst.
SYSTEM_PROOF of captured Question membership.
SYSTEM_PROOF that accepted capture writes are complete.
No AI-derived content may be part of the raw human-only set.

BOUNDARY DEPENDENCIES:
Workspace.
Authority.
Question Burst.
Human / AI.
State Transition.
Persistence.
Audit.
Failure.

ALLOW CONDITION:
Completion request is authorized and raw-set freeze can be established.

DENY CONDITION:
Capture persistence is incomplete.
Burst state invalid.
Human/AI contamination detected.
Authority denied.

NEXT STATE:
QuestionBurst -> COMPLETED.
Session -> QUESTION_CAPTURE.

PERSISTENCE CONSEQUENCE:
Raw Burst membership becomes frozen.
Session becomes post-generation capture-finalized state.

AUDIT CONSEQUENCE:
Completion and frozen-set identity must be reconstructable.

FAILURE STATE:
Prior confirmed states remain unless commit is indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No later ANALYSIS transition may occur until 10 can prove a completed, frozen raw set.
```

## TRN-SESS-006 BEGIN_ANALYSIS

```text
CURRENT STATE:
QUESTION_CAPTURE.

REQUESTED TRANSITION:
BEGIN_ANALYSIS.

ACTOR:
Human or System actor as later authorized.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-006.

PRECONDITIONS:
Associated QuestionBurst is COMPLETED.
Raw Question set is frozen.
Protected Burst input is closed.
No unresolved capture failure exists.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Burst COMPLETED.
SYSTEM_PROOF of frozen raw membership.
SYSTEM_PROOF that Question.original_text invariants hold.

BOUNDARY DEPENDENCIES:
Authority.
Question Burst.
Human / AI.
AI Context.
State Transition.
Audit.
Failure.

ALLOW CONDITION:
Frozen raw set is valid and authority passes.

DENY CONDITION:
Burst still ACTIVE or PAUSED.
Raw set not provably frozen.
Capture recovery unresolved.
Authority denied.

NEXT STATE:
ANALYSIS.

PERSISTENCE CONSEQUENCE:
Session state becomes ANALYSIS.

AUDIT CONSEQUENCE:
Analysis phase start is traceable.

FAILURE STATE:
Session remains QUESTION_CAPTURE unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
If AI service is unavailable after entering ANALYSIS, Session remains ANALYSIS.
No automatic transition to REFLECTION is implied.
```

## TRN-SESS-007 BEGIN_REFLECTION

```text
CURRENT STATE:
ANALYSIS.

REQUESTED TRANSITION:
BEGIN_REFLECTION.

ACTOR:
Human or System actor as later authorized.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-007.

PRECONDITIONS:
Required analysis for the active method has completed validly.
For MVP Question Burst path, AI question analysis is a LEVEL 1 Must-have.
No invalid AI output may satisfy analysis completion.

REQUIRED EVIDENCE:
AI_VALIDATION_PROOF that required analysis operations completed under 08 contracts.
SYSTEM_PROOF that derived analysis did not alter raw Questions.

BOUNDARY DEPENDENCIES:
Authority.
AI.
Provenance.
State Transition.
Audit.
Failure.

ALLOW CONDITION:
Required analysis completion can be proven and authority passes.

DENY CONDITION:
AI output exists but failed validation.
Analysis is incomplete.
Derived output altered protected source state.
Authority denied.

NEXT STATE:
REFLECTION.

PERSISTENCE CONSEQUENCE:
Session state becomes REFLECTION.

AUDIT CONSEQUENCE:
Transition and analysis-completion proof reference must be traceable.

FAILURE STATE:
Session remains ANALYSIS unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
AI failure does not advance state.
Recovery/fallback remains to 08/10.

OPEN GAP:
No source-authorized "skip required analysis" path is defined for the MVP.
```

## TRN-SESS-008 BEGIN_QUESTION_SELECTION

```text
CURRENT STATE:
REFLECTION.

REQUESTED TRANSITION:
BEGIN_QUESTION_SELECTION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-008.

PRECONDITIONS:
Reflection phase has been explicitly completed according to later contract.
No AI output may create the selection transition by itself.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Reflection phase completion.
Reflection response persistence is not required by 03 because GAP-02-010 remains open.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
State Transition.
Audit.

ALLOW CONDITION:
Human-directed transition request satisfies authority and reflection completion.

DENY CONDITION:
AI is acting as decision authority.
Reflection phase completion cannot be established.
Authority denied.

NEXT STATE:
QUESTION_SELECTION.

PERSISTENCE CONSEQUENCE:
Session state becomes QUESTION_SELECTION.

AUDIT CONSEQUENCE:
Human-directed phase transition trace required.

FAILURE STATE:
Session remains REFLECTION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Return to last confirmed REFLECTION state if transition did not commit.
```

## TRN-SESS-009 BEGIN_INVESTIGATION

```text
CURRENT STATE:
QUESTION_SELECTION.

REQUESTED TRANSITION:
BEGIN_INVESTIGATION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-009.

PRECONDITIONS:
At least one compelling Question has been selected.
Exactly one primary Question required by the Question Burst method has been selected.
For the Question Burst method, the five-level ImpactChain is complete.
AI may have recommended Questions but may not create the authority-bearing selection.

REQUIRED EVIDENCE:
SYSTEM_PROOF of QuestionSelection relation(s).
SYSTEM_PROOF of exactly one primary selection.
SYSTEM_PROOF of complete five-level ImpactChain for this method.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
Decision.
State Transition.
Audit.

ALLOW CONDITION:
Required human selection state and ImpactChain structure exist and authority passes.

DENY CONDITION:
Only AI recommendation exists.
No primary Question exists.
ImpactChain incomplete for this method.
Authority denied.

NEXT STATE:
INVESTIGATION.

PERSISTENCE CONSEQUENCE:
Session state becomes INVESTIGATION.

AUDIT CONSEQUENCE:
Selection-to-investigation transition is traceable.

FAILURE STATE:
Session remains QUESTION_SELECTION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Invalid or incomplete selection cannot be repaired by auto-selecting an AI recommendation.
```

## TRN-SESS-010 BEGIN_EXPERIMENT_PHASE

```text
CURRENT STATE:
INVESTIGATION.

REQUESTED TRANSITION:
BEGIN_EXPERIMENT_PHASE.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-010.
Human responsibility for experiments is source-defined.
04 must resolve exact decision right.

PRECONDITIONS:
Investigation phase completion is explicitly asserted.
Any required Evidence conditions defined later by method/07 are satisfied.
An experiment proposal may exist but is not itself sufficient authority.

REQUIRED EVIDENCE:
SYSTEM_PROOF of investigation completion.
DOMAIN_EVIDENCE only where later method/07 requires it.

BOUNDARY DEPENDENCIES:
Authority.
Evidence.
Human / AI.
State Transition.
Audit.

ALLOW CONDITION:
Human-authorized transition and required investigation conditions pass.

DENY CONDITION:
AI proposal is the only basis for phase advancement.
Required domain evidence is unresolved or missing where mandatory.
Authority denied.

NEXT STATE:
EXPERIMENT.

PERSISTENCE CONSEQUENCE:
Session state becomes EXPERIMENT.

AUDIT CONSEQUENCE:
Transition trace required.

FAILURE STATE:
Session remains INVESTIGATION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No AI Experiment proposal may auto-advance Session state.
```

## TRN-SESS-011 BEGIN_ACTION_PHASE

```text
CURRENT STATE:
EXPERIMENT.

REQUESTED TRANSITION:
BEGIN_ACTION_PHASE.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-011.
Human responsibility for actions and experiments is source-defined.

PRECONDITIONS:
Experiment phase has reached a valid completion condition under the Experiment state model.
Required human decision to move into action exists.
AI recommendation is not sufficient.

REQUIRED EVIDENCE:
SYSTEM_PROOF of relevant Experiment completion or method-defined experiment-phase completion.
DOMAIN_EVIDENCE only where later architecture makes evidence a required action precondition.

BOUNDARY DEPENDENCIES:
Authority.
Decision.
Evidence.
State Transition.
Audit.

ALLOW CONDITION:
Human decision plus required structural conditions and authority pass.

DENY CONDITION:
Experiment is only PROPOSED or UNDER_CONSIDERATION.
AI recommends action but no human decision exists.
Authority denied.

NEXT STATE:
ACTION.

PERSISTENCE CONSEQUENCE:
Session state becomes ACTION.

AUDIT CONSEQUENCE:
Human-decision-backed phase transition trace required.

FAILURE STATE:
Session remains EXPERIMENT unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No external action is assumed merely because Session enters ACTION.
```

## TRN-SESS-012 BEGIN_REVIEW

```text
CURRENT STATE:
ACTION.

REQUESTED TRANSITION:
BEGIN_REVIEW.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-012.

PRECONDITIONS:
Action phase has been explicitly completed by an authorized human/system contract.
03 does not claim external-world verification of action.

REQUIRED EVIDENCE:
SYSTEM_PROOF of authorized Action-phase completion record/transition request.

BOUNDARY DEPENDENCIES:
Authority.
State Transition.
Audit.

ALLOW CONDITION:
Action phase completion is validly asserted and authority passes.

DENY CONDITION:
Only AI recommendation or UI navigation exists.
Authority denied.

NEXT STATE:
REVIEW.

PERSISTENCE CONSEQUENCE:
Session state becomes REVIEW.

AUDIT CONSEQUENCE:
Transition trace required.

FAILURE STATE:
Session remains ACTION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Review may not be entered solely because a page was opened.
```

## TRN-SESS-013 CLOSE_SESSION

```text
CURRENT STATE:
REVIEW.

REQUESTED TRANSITION:
CLOSE_SESSION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SESS-013.

PRECONDITIONS:
Review phase completion is explicitly established.
No unresolved INDETERMINATE transition affects the Session.

REQUIRED EVIDENCE:
SYSTEM_PROOF of REVIEW state and completion marker required by later contract.

BOUNDARY DEPENDENCIES:
Authority.
State Transition.
Audit.
Failure.
Recovery.

ALLOW CONDITION:
Review is complete, authority passes, no unresolved state uncertainty exists.

DENY CONDITION:
Prior transition is indeterminate.
Authority denied.
Review completion not established.

NEXT STATE:
CLOSED.

PERSISTENCE CONSEQUENCE:
Session becomes terminal CLOSED.

AUDIT CONSEQUENCE:
Session closure trace required.

FAILURE STATE:
Session remains REVIEW unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
CLOSED must not be used to hide unresolved failure.
```

---

# 16. Session Illegal Transitions

The following are illegal unless later source-supported architecture explicitly introduces them:

```text
DRAFT -> CHALLENGE_CAPTURE
DRAFT -> QUESTION_GENERATION
SETUP -> QUESTION_GENERATION
CHALLENGE_CAPTURE -> ANALYSIS
QUESTION_GENERATION -> ANALYSIS
QUESTION_CAPTURE -> REFLECTION
ANALYSIS -> QUESTION_SELECTION
REFLECTION -> INVESTIGATION
QUESTION_SELECTION -> EXPERIMENT
INVESTIGATION -> ACTION
EXPERIMENT -> REVIEW
ACTION -> CLOSED
REVIEW -> DRAFT
CLOSED -> any Session state
```

General rule:

```text
Skipping a named source state is denied by default.
```

---

# 17. Session Unreachable-State Analysis

Under the topology defined in 03:

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

are all structurally reachable from Session creation if every prior transition is valid.

No state is structurally orphaned.

However, runtime reachability is blocked if unresolved dependencies remain.

Examples:

```text
ANALYSIS cannot be reached if raw Burst freeze cannot be proven.
REFLECTION cannot be reached if required analysis cannot complete.
INVESTIGATION cannot be reached without valid human selection and ImpactChain completion for Question Burst.
ACTION cannot be reached while Experiment remains only a proposal.
CLOSED cannot be reached while a prior transition is indeterminate.
```

---

# 18. GAP-03-001: Session Cancellation / Abandonment

LEVEL 1 defines no:

```text
CANCELLED
ABANDONED
EXPIRED
VOID
```

Session state.

A user who intentionally abandons a Session before REVIEW currently has no source-defined terminal transition.

03 does not invent one.

Status:

```text
[UNDERDEFINED]
```

This is not a hidden skip to CLOSED.

A later human decision is required if cancellation semantics are needed for the prototype or full product.

---

# 19. QuestionBurst State Machine

## 19.1 State vocabulary

LEVEL 1 strongly implies QuestionBurst lifecycle but does not provide state names.

03 introduces the minimum state vocabulary required to materialize source behavior.

```text
PREPARED
ACTIVE
PAUSED
COMPLETED
```

Status:

```text
[ARCHITECTURAL CLOSURE]
```

No `CANCELLED` or `RECOVERING` domain state is introduced.

Failure and recovery are handled through transition outcomes and later 10 architecture.

## 19.2 PREPARED

Burst exists and setup context is available.

Question input is not open.

## 19.3 ACTIVE

Protected Question input is open.

Only accepted Question input may be captured.

No AI analysis/evaluation is permitted.

## 19.4 PAUSED

Burst remains open as the same process but input acceptance is suspended.

Pause exists because LEVEL 1 explicitly says a Facilitator can pause/end the Burst.

## 19.5 COMPLETED

Input is permanently closed.

Raw captured Question membership is frozen.

Post-burst analysis may become eligible.

`COMPLETED` is terminal for the same QuestionBurst.

---

# 20. QuestionBurst Transitions

## TRN-BURST-001 PREPARE_BURST

```text
CURRENT STATE:
QuestionBurst absent.

REQUESTED TRANSITION:
PREPARE_BURST.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-BURST-001.

PRECONDITIONS:
Session exists.
Session is in a pre-generation state compatible with later start.
QuestionBurst belongs to that Session.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Session identity and ownership.

BOUNDARY DEPENDENCIES:
Workspace.
Authority.
Question Burst.
Methodology.
Audit.

ALLOW CONDITION:
Structural ownership and authority pass.

DENY CONDITION:
Session absent.
Workspace unresolved.
Authority denied.

NEXT STATE:
PREPARED.

PERSISTENCE CONSEQUENCE:
Create QuestionBurst process object.

AUDIT CONSEQUENCE:
Preparation is traceable if consequential under later audit policy.

FAILURE STATE:
Burst remains absent unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Uncertain creation reconciled by 10.
```

## TRN-BURST-002 START_BURST

```text
CURRENT STATE:
PREPARED.

REQUESTED TRANSITION:
START_BURST.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-BURST-002.
LEVEL 1 guarantees Facilitator can start.

PRECONDITIONS:
Required setup exists.
Session transition bundle to QUESTION_GENERATION is valid.
Duration semantics are configured according to unresolved CONFLICT-007.
No competing active Burst violates later method rule.

REQUIRED EVIDENCE:
SYSTEM_PROOF of setup.
SYSTEM_PROOF of Session CHALLENGE_CAPTURE.

BOUNDARY DEPENDENCIES:
Authority.
Question Burst.
Methodology.
State Transition.
Audit.

ALLOW CONDITION:
Start authority and Session bundle pass.

DENY CONDITION:
Duration/configuration invalid.
Session state invalid.
Authority denied.

NEXT STATE:
ACTIVE.

PERSISTENCE CONSEQUENCE:
Start time/configuration becomes durable according to 09.

AUDIT CONSEQUENCE:
Start is traceable with Session transition.

FAILURE STATE:
PREPARED unless bundle commit indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Burst ACTIVE without Session QUESTION_GENERATION is invalid partial state.
```

## TRN-BURST-003 PAUSE_BURST

```text
CURRENT STATE:
ACTIVE.

REQUESTED TRANSITION:
PAUSE_BURST.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-BURST-003.
LEVEL 1 guarantees Facilitator can pause.

PRECONDITIONS:
Burst is ACTIVE.

REQUIRED EVIDENCE:
SYSTEM_PROOF of current state.

BOUNDARY DEPENDENCIES:
Authority.
Question Burst.
Audit.

ALLOW CONDITION:
Pause authority passes.

DENY CONDITION:
Burst not ACTIVE.
Authority denied.

NEXT STATE:
PAUSED.

PERSISTENCE CONSEQUENCE:
Question input acceptance is suspended.

AUDIT CONSEQUENCE:
Pause must be reconstructable if it affects timer/capture semantics.

FAILURE STATE:
ACTIVE unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No Question may be accepted under PAUSED semantics unless later source explicitly permits it.
```

## TRN-BURST-004 RESUME_BURST

```text
CURRENT STATE:
PAUSED.

REQUESTED TRANSITION:
RESUME_BURST.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-BURST-004.

PRECONDITIONS:
Burst is PAUSED.
Session remains QUESTION_GENERATION.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Burst and Session states.

BOUNDARY DEPENDENCIES:
Authority.
Question Burst.
State Transition.
Audit.

ALLOW CONDITION:
Resume authority passes and Session state remains compatible.

DENY CONDITION:
Session no longer in QUESTION_GENERATION.
Authority denied.

NEXT STATE:
ACTIVE.

PERSISTENCE CONSEQUENCE:
Question input acceptance reopens.

AUDIT CONSEQUENCE:
Resume trace required where timer semantics depend on pause.

FAILURE STATE:
PAUSED unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No implicit resume from UI navigation or timer process.
```

## TRN-BURST-005 COMPLETE_BURST

```text
CURRENT STATE:
ACTIVE or PAUSED.

REQUESTED TRANSITION:
COMPLETE_BURST.

ACTOR:
Human actor or authorized System timer.

AUTHORITY REQUIREMENT:
AUTH-DEP-BURST-005.
Human end and system timer completion must be distinguished in 04/05.

PRECONDITIONS:
Accepted Question captures are durably resolved.
No capture write acknowledged to the user remains unresolved.
No AI-generated content is silently present in Human-only raw set.
Session transition bundle to QUESTION_CAPTURE is valid.

REQUIRED EVIDENCE:
SYSTEM_PROOF of complete captured membership.
SYSTEM_PROOF of Question immutability invariants.
SYSTEM_PROOF of mode-consistent origin.

BOUNDARY DEPENDENCIES:
Question Burst.
Human / AI.
Authority.
Persistence.
Audit.
Failure.
Recovery.

ALLOW CONDITION:
Frozen raw membership can be established consistently.

DENY CONDITION:
Capture persistence unresolved.
Contamination detected.
Authority denied.
Session bundle invalid.

NEXT STATE:
COMPLETED.

PERSISTENCE CONSEQUENCE:
Membership set becomes immutable for raw-burst reconstruction.

AUDIT CONSEQUENCE:
Completion and frozen membership must be reconstructable.

FAILURE STATE:
Prior Burst state unless INDETERMINATE.

RECOVERY / ROLLBACK REQUIREMENT:
No analysis may begin until completion is proven.
```

---

# 21. CONFLICT-007 Preserved: Burst Duration

Source contains:

```text
approximately four minutes
Four-minute timer
configured duration
```

03 does not choose among:

```text
fixed four minutes
four-minute default with configuration
method-defined approximate duration
```

Timer expiry may request Burst completion only after this conflict is resolved.

Status:

```text
[OPEN SOURCE TENSION]
```

---

# 22. GAP-03-002: Pause and Timer Semantics

LEVEL 1 permits pause and defines timer behavior but does not state:

```text
whether timer stops while PAUSED
whether elapsed time is preserved
whether resume continues remaining time
whether pause may extend total wall-clock duration
whether timer may expire while PAUSED
```

Status:

```text
[UNDERDEFINED]
```

No timer implementation may invent these semantics before closure.

---

# 23. Consequential Question Capture

Question capture is a canonical state-changing operation even though Session remains in QUESTION_GENERATION.

## TRN-Q-001 CAPTURE_BURST_QUESTION

```text
CURRENT STATE:
Session = QUESTION_GENERATION.
QuestionBurst = ACTIVE.
Question = absent.

REQUESTED TRANSITION:
CAPTURE_BURST_QUESTION.

ACTOR:
Human participant.

AUTHORITY REQUIREMENT:
AUTH-DEP-Q-001.
LEVEL 1 establishes participants may submit Questions.
04 must resolve participant authorization semantics.

PRECONDITIONS:
Burst ACTIVE.
Input accepted as Question Burst-valid input.
Workspace scope resolves.
Author identity/timestamp requirements satisfied.

REQUIRED EVIDENCE:
SYSTEM_PROOF of active Burst.
SYSTEM_PROOF of author/session/burst context.

BOUNDARY DEPENDENCIES:
Identity.
Workspace.
Authority.
Question Burst.
Human / AI.
Audit.
Persistence.

ALLOW CONDITION:
Input satisfies Burst rule and actor is authorized.

DENY CONDITION:
Burst PAUSED or COMPLETED.
Input is answer/explanation under protected Burst rule.
AI is injecting content in Human-only mode.
Authority denied.

NEXT STATE:
Question exists.
Session remains QUESTION_GENERATION.
QuestionBurst remains ACTIVE.

PERSISTENCE CONSEQUENCE:
Create Question with immutable original_text.
Create Burst-capture membership relation.

AUDIT CONSEQUENCE:
Question capture must remain attributable and reconstructable.

FAILURE STATE:
Question absent if precommit failure.
If user acknowledgement and persistence outcome conflict, transition is INDETERMINATE.

RECOVERY / ROLLBACK REQUIREMENT:
10 must prevent silent loss of acknowledged capture.
No recovery may rewrite original_text.
```

---

# 24. GAP-03-003: Questions-Only Enforcement Mechanism

LEVEL 1 simultaneously requires:

```text
participants submit only questions
system prevents answers/explanations
AI != evaluator during active protected Burst
```

03 can define the eligibility predicate:

```text
BURST_INPUT_VALID
```

03 cannot define how that predicate is established without crossing into 05/06/08.

Status:

```text
[UNDERDEFINED]
```

High-assurance constraint:

```text
AI semantic evaluation during the protected Burst
cannot be silently introduced as the enforcement mechanism.
```

This is a prototype-critical governance/boundary dependency.

---

# 25. Question State Treatment

LEVEL 1 provides:

```text
Question.status
```

without values.

## 25.1 GAP-02-013 preserved

Question status vocabulary remains `[UNDERDEFINED]`.

## 25.2 High-assurance restriction

Until vocabulary is defined:

```text
Question.status must not be used as:
transition guard
authority predicate
selection authority
evidence status
AI validation status
```

## 25.3 Question creation

Creation is modeled existentially:

```text
ABSENT
-> PRESENT
```

## 25.4 Question reframe

Reframe is not a Question status transition.

It is:

```text
source Question remains unchanged
+
new Question created
+
QuestionLineage relation created
```

This preserves AC-02-003.

## 25.5 Question normalization

Normalization does not create a new Question state.

It creates or updates derived representation while preserving original_text.

## 25.6 Question classification / clustering

Classification and clustering do not advance Question lifecycle.

They create derived annotations/relations.

---

# 26. AI Analysis State-Preserving Operations

The Session may remain in ANALYSIS while AI operations create derived records.

AI output must not advance Session state merely because it exists.

## 26.1 AI classification

```text
Session state:
ANALYSIS -> ANALYSIS

Canonical consequence:
derived classification may be persisted.

Prohibited consequence:
Question original_text mutation.
Session auto-advance.
Human selection creation.
Evidence creation as validated fact.
```

## 26.2 AI clustering

```text
Session state:
ANALYSIS -> ANALYSIS

Canonical consequence:
QuestionCluster and derived memberships may be persisted.

Prohibited consequence:
Question ownership change.
Session auto-advance.
```

## 26.3 AI assumption detection

```text
Session state:
ANALYSIS -> ANALYSIS

Canonical consequence:
Assumption record may be created with initial state UNKNOWN.

Prohibited consequence:
Assumption created directly as SUPPORTED, WEAK or REFUTED solely from AI output.
```

## 26.4 AI reframing

```text
Session state:
ANALYSIS -> ANALYSIS

Canonical consequence:
new derived Question may be created with lineage to source Question.

Prohibited consequence:
overwrite source Question.
human attribution.
selection authority.
```

---

# 27. AC-03-002: New Assumptions Begin UNKNOWN

LEVEL 1 provides the Assumption states:

```text
UNKNOWN
SUPPORTED
WEAK
REFUTED
TESTING
```

Evidence over confidence and provenance rules prohibit an AI inference from becoming supported fact merely by generation.

03 therefore establishes:

```text
Every newly persisted Assumption begins in UNKNOWN
unless it enters through a future source-supported import path that explicitly carries validated state.
```

No such import path is currently defined.

Status:

```text
[ARCHITECTURAL CLOSURE]
```

---

# 28. Assumption State Machine

## 28.1 States

**[SPECIFIED]**

```text
UNKNOWN
TESTING
SUPPORTED
WEAK
REFUTED
```

## 28.2 State semantics

The names are source-defined.

Operational semantics require closure.

### UNKNOWN

**[ARCHITECTURAL CLOSURE]**

The system has an Assumption record but does not have sufficient validated basis to classify it as SUPPORTED, WEAK or REFUTED.

### TESTING

**[ARCHITECTURAL CLOSURE]**

The Assumption is under active evidence/experiment evaluation.

### SUPPORTED

**[ARCHITECTURAL CLOSURE]**

Current validated evidence meets the later-defined sufficiency rule for support.

This does not mean universal truth.

### WEAK

**[ARCHITECTURAL CLOSURE]**

Current validated basis is insufficient for SUPPORTED while not meeting the rule for REFUTED.

Exact evidence threshold belongs to 07.

### REFUTED

**[ARCHITECTURAL CLOSURE]**

Current validated evidence meets the later-defined rule for contradiction/refutation.

## 28.3 Legal topology

```text
UNKNOWN -> TESTING

SUPPORTED -> TESTING
WEAK -> TESTING
REFUTED -> TESTING

TESTING -> UNKNOWN
TESTING -> SUPPORTED
TESTING -> WEAK
TESTING -> REFUTED
```

Direct transitions among:

```text
SUPPORTED
WEAK
REFUTED
```

are illegal.

Reclassification must return through TESTING.

This makes evidentiary reconsideration explicit.

---

# 29. Assumption Transition Contracts

## TRN-ASM-001 BEGIN_ASSUMPTION_TEST

```text
CURRENT STATE:
UNKNOWN, SUPPORTED, WEAK or REFUTED.

REQUESTED TRANSITION:
BEGIN_ASSUMPTION_TEST.

ACTOR:
Human actor or governed System process.

AUTHORITY REQUIREMENT:
AUTH-DEP-ASM-001.
04 must resolve who may place an Assumption into TESTING.

PRECONDITIONS:
Assumption exists.
Workspace scope resolves.
Test/evidence evaluation context exists.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Assumption identity and current state.
No DOMAIN_EVIDENCE required merely to begin testing.

BOUNDARY DEPENDENCIES:
Authority.
Evidence.
Workspace.
Audit.

ALLOW CONDITION:
Testing request is authorized and context exists.

DENY CONDITION:
Assumption already TESTING.
Authority denied.
Workspace unresolved.

NEXT STATE:
TESTING.

PERSISTENCE CONSEQUENCE:
Assumption state becomes TESTING.

AUDIT CONSEQUENCE:
Testing start trace required.

FAILURE STATE:
Prior state unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Failed start cannot erase prior classification.
```

## TRN-ASM-002 CLASSIFY_TEST_RESULT

```text
CURRENT STATE:
TESTING.

REQUESTED TRANSITION:
CLASSIFY_TEST_RESULT.

ACTOR:
Human actor or governed System process.

AUTHORITY REQUIREMENT:
AUTH-DEP-ASM-002.
04 must determine who may authorize evidentiary classification.
07 must define evidence validation authority/sufficiency.

PRECONDITIONS:
Test/evidence evaluation is complete enough for one target classification.
Required Evidence relations are valid under 07.

REQUIRED EVIDENCE:
DOMAIN_EVIDENCE satisfying later 07 rule.
SYSTEM_PROOF of completed evaluation context.

BOUNDARY DEPENDENCIES:
Authority.
Evidence.
Provenance.
Audit.
State Transition.

ALLOW CONDITION:
Evidence sufficiency rule and authority both pass.

DENY CONDITION:
Only AI confidence exists.
Only AI inference exists.
Evidence validation unresolved.
Authority denied.

NEXT STATE:
UNKNOWN, SUPPORTED, WEAK or REFUTED.

PERSISTENCE CONSEQUENCE:
Assumption classification state changes.

AUDIT CONSEQUENCE:
Evidence-linked classification transition trace required.

FAILURE STATE:
Remain TESTING unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No automatic "best guess" classification on failure.
```

---

# 30. Assumption Illegal Transitions

Illegal:

```text
UNKNOWN -> SUPPORTED
UNKNOWN -> WEAK
UNKNOWN -> REFUTED

SUPPORTED -> WEAK
SUPPORTED -> REFUTED

WEAK -> SUPPORTED
WEAK -> REFUTED

REFUTED -> SUPPORTED
REFUTED -> WEAK
```

unless they pass through TESTING.

AI generation alone may not perform:

```text
UNKNOWN -> SUPPORTED
UNKNOWN -> REFUTED
```

---

# 31. Experiment State Machine

LEVEL 1 defines `Experiment.status` but not values.

LEVEL 1 allows AI Experiment Designer capability.

LEVEL 1 assigns experiment responsibility to humans.

A high-assurance system therefore requires proposal, consideration, authorization and actual execution to remain distinct.

## 31.1 State vocabulary

```text
PROPOSED
UNDER_CONSIDERATION
AUTHORIZED
IN_PROGRESS
COMPLETED
```

Status:

```text
[ARCHITECTURAL CLOSURE]
```

No cancellation/failure domain states are invented here.

## 31.2 PROPOSED

An Experiment specification exists.

It may originate from AI or human.

It has no execution authority.

## 31.3 UNDER_CONSIDERATION

An authorized human consideration process has adopted the proposal for evaluation.

This is not authorization to execute.

## 31.4 AUTHORIZED

The required human decision and operation authority for execution have been established.

No experiment execution is implied yet.

## 31.5 IN_PROGRESS

Experiment execution has actually begun within the system's record.

## 31.6 COMPLETED

Experiment execution has concluded and result/learning may be recorded.

`COMPLETED` does not imply success.

---

# 32. Experiment Transition Contracts

## TRN-EXP-001 CREATE_EXPERIMENT_PROPOSAL

```text
CURRENT STATE:
Experiment absent.

REQUESTED TRANSITION:
CREATE_EXPERIMENT_PROPOSAL.

ACTOR:
Human actor, AI-derived operation, or other permitted origin.

AUTHORITY REQUIREMENT:
Creation authority depends on origin.
AI may propose where 08 permits.
Creating PROPOSED state does not grant execution authority.

PRECONDITIONS:
Challenge exists.
Question/Assumption context is valid where linked.
Workspace scope resolves.

REQUIRED EVIDENCE:
SYSTEM_PROOF of owning Challenge and source relations.

BOUNDARY DEPENDENCIES:
Workspace.
Human / AI.
Provenance.
Audit.

ALLOW CONDITION:
Proposal creation is permitted by origin-specific contract.

DENY CONDITION:
Proposal attempts to enter AUTHORIZED or IN_PROGRESS directly.
Workspace unresolved.

NEXT STATE:
PROPOSED.

PERSISTENCE CONSEQUENCE:
Experiment record created as proposal.

AUDIT CONSEQUENCE:
Origin and proposal creation trace required.

FAILURE STATE:
Experiment absent unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
AI proposal failure may not create partial authorized state.
```

## TRN-EXP-002 BEGIN_HUMAN_CONSIDERATION

```text
CURRENT STATE:
PROPOSED.

REQUESTED TRANSITION:
BEGIN_HUMAN_CONSIDERATION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-EXP-002.

PRECONDITIONS:
Proposal exists.
Origin/provenance is distinguishable.
Required context is available.

REQUIRED EVIDENCE:
SYSTEM_PROOF of proposal identity and context.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
Provenance.
Audit.

ALLOW CONDITION:
Human consideration authority passes.

DENY CONDITION:
AI attempts to self-adopt its proposal.
Authority denied.

NEXT STATE:
UNDER_CONSIDERATION.

PERSISTENCE CONSEQUENCE:
Experiment state becomes UNDER_CONSIDERATION.

AUDIT CONSEQUENCE:
Human consideration start trace required.

FAILURE STATE:
Remain PROPOSED unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
AI output cannot substitute for consideration transition.
```

## TRN-EXP-003 AUTHORIZE_EXPERIMENT

```text
CURRENT STATE:
UNDER_CONSIDERATION.

REQUESTED TRANSITION:
AUTHORIZE_EXPERIMENT.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-EXP-003.
Human responsibility for experiments is source-defined.
04 must resolve exact decision right.

PRECONDITIONS:
Human consideration complete.
Required experiment specification exists.
Any evidence requirement defined later by method/07 is satisfied.

REQUIRED EVIDENCE:
SYSTEM_PROOF of consideration state and complete proposal.
DOMAIN_EVIDENCE only if later architecture requires it for this experiment.

BOUNDARY DEPENDENCIES:
Authority.
Human Decision.
Evidence.
Audit.

ALLOW CONDITION:
Required human decision exists and authority passes.

DENY CONDITION:
Only AI recommendation/confidence exists.
Authority denied.
Required evidence missing where mandatory.

NEXT STATE:
AUTHORIZED.

PERSISTENCE CONSEQUENCE:
Experiment state becomes AUTHORIZED.

AUDIT CONSEQUENCE:
Human-decision-backed authorization trace required.

FAILURE STATE:
Remain UNDER_CONSIDERATION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
No automatic authorization on timeout or AI confidence.
```

## TRN-EXP-004 START_EXPERIMENT

```text
CURRENT STATE:
AUTHORIZED.

REQUESTED TRANSITION:
START_EXPERIMENT.

ACTOR:
Human actor or governed System actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-EXP-004.

PRECONDITIONS:
Authorization remains valid.
Required execution conditions are present.

REQUIRED EVIDENCE:
SYSTEM_PROOF of AUTHORIZED state and execution prerequisites.

BOUNDARY DEPENDENCIES:
Authority.
Audit.
State Transition.

ALLOW CONDITION:
Execution start authority passes.

DENY CONDITION:
Experiment not AUTHORIZED.
Authorization invalidated.
Authority denied.

NEXT STATE:
IN_PROGRESS.

PERSISTENCE CONSEQUENCE:
Experiment state becomes IN_PROGRESS.

AUDIT CONSEQUENCE:
Actual start trace required.

FAILURE STATE:
Remain AUTHORIZED unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Do not infer execution merely from scheduled deadline or UI activity.
```

## TRN-EXP-005 COMPLETE_EXPERIMENT

```text
CURRENT STATE:
IN_PROGRESS.

REQUESTED TRANSITION:
COMPLETE_EXPERIMENT.

ACTOR:
Human actor or governed System actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-EXP-005.

PRECONDITIONS:
Execution completion can be asserted under later operation contract.
Result/learning fields required by later contract are valid.

REQUIRED EVIDENCE:
SYSTEM_PROOF of completion record.
DOMAIN_EVIDENCE may be produced by the experiment but is not automatically validated by completion.

BOUNDARY DEPENDENCIES:
Authority.
Evidence.
Audit.
State Transition.

ALLOW CONDITION:
Completion authority and structural result conditions pass.

DENY CONDITION:
Experiment never entered IN_PROGRESS.
Result is only AI-fabricated without permitted origin.
Authority denied.

NEXT STATE:
COMPLETED.

PERSISTENCE CONSEQUENCE:
Experiment state becomes COMPLETED.
Result/learning may be persisted.

AUDIT CONSEQUENCE:
Completion trace required.

FAILURE STATE:
Remain IN_PROGRESS unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Negative experiment outcome still completes the Experiment.
System failure is handled separately from experimental result.
```

---

# 33. Experiment Illegal Transitions

Illegal:

```text
PROPOSED -> AUTHORIZED
PROPOSED -> IN_PROGRESS
PROPOSED -> COMPLETED

UNDER_CONSIDERATION -> IN_PROGRESS
UNDER_CONSIDERATION -> COMPLETED

AUTHORIZED -> COMPLETED

AI proposal -> AUTHORIZED
AI proposal -> IN_PROGRESS
AI proposal -> COMPLETED
```

---

# 34. GAP-03-004: Experiment Cancellation / Abandonment

LEVEL 1 defines no Experiment cancellation or abandonment semantics.

Status:

```text
[UNDERDEFINED]
```

03 does not invent:

```text
CANCELLED
FAILED
ABORTED
EXPIRED
```

`COMPLETED` means the experiment ran to a recorded conclusion, not that it succeeded.

---

# 35. Decision State Architecture

02 established:

```text
Decision is a canonical domain object.
Decision lifecycle is underdefined.
Humans remain responsible for decisions.
AI Strategist may connect inquiry to decisions but has no decision authority.
```

High assurance requires AI proposal, human consideration, human decision and execution authority to remain distinct.

## 35.1 AI decision proposal is not a Decision state

An AI proposal concerning a decision remains:

```text
derived content
```

until a human-authorized process adopts it for consideration.

AI proposal persistence does not create a human Decision object in `DECIDED` state.

## 35.2 Decision state vocabulary

03 introduces the minimum Decision lifecycle:

```text
UNDER_CONSIDERATION
DECIDED
```

Status:

```text
[ARCHITECTURAL CLOSURE]
```

## 35.3 UNDER_CONSIDERATION

A human decision process exists.

Options, criteria and evidence may be assembled or reviewed.

No selected option is yet authority-bearing as a final decision.

## 35.4 DECIDED

An authorized human decision has been recorded.

The Decision contains a selected option and rationale according to later contract.

`DECIDED` does not mean a downstream action transition is automatically authorized.

---

# 36. Decision Transition Contracts

## TRN-DEC-001 OPEN_DECISION_CONSIDERATION

```text
CURRENT STATE:
Decision absent.

REQUESTED TRANSITION:
OPEN_DECISION_CONSIDERATION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-DEC-001.
04 must resolve who may initiate a human decision process.

PRECONDITIONS:
Challenge exists.
Decision Question relation can be established.
Workspace scope resolves.
Any AI recommendation remains distinguishable as derived input.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Challenge and decision-question context.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
Evidence.
Provenance.
Audit.

ALLOW CONDITION:
Human consideration process is authorized.

DENY CONDITION:
AI operation attempts to create a finalized Decision.
Workspace unresolved.
Authority denied.

NEXT STATE:
UNDER_CONSIDERATION.

PERSISTENCE CONSEQUENCE:
Decision object is created in UNDER_CONSIDERATION.

AUDIT CONSEQUENCE:
Decision consideration start is traceable.

FAILURE STATE:
Decision absent unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
AI proposal remains derived even if Decision creation fails.
```

## TRN-DEC-002 RECORD_HUMAN_DECISION

```text
CURRENT STATE:
UNDER_CONSIDERATION.

REQUESTED TRANSITION:
RECORD_HUMAN_DECISION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-DEC-002.
Human responsibility for decisions is source-defined.
04 must resolve exact decision right.

PRECONDITIONS:
Options and criteria required by later contract are present.
Evidence requirements defined by 07/method are satisfied where mandatory.
Selected option and rationale are supplied by or explicitly adopted by authorized human decision process.

REQUIRED EVIDENCE:
SYSTEM_PROOF of complete decision structure.
DOMAIN_EVIDENCE where later architecture requires it.

BOUNDARY DEPENDENCIES:
Authority.
Human Decision.
Evidence.
Provenance.
Audit.

ALLOW CONDITION:
Human decision authority and required structural/evidentiary conditions pass.

DENY CONDITION:
Only AI recommendation/confidence exists.
Selected option was auto-selected by AI without human decision.
Evidence requirement unresolved where mandatory.
Authority denied.

NEXT STATE:
DECIDED.

PERSISTENCE CONSEQUENCE:
Decision state becomes DECIDED.
Selected option and rationale become canonical record of the human decision.

AUDIT CONSEQUENCE:
Human decision must be attributable and reconstructable.

FAILURE STATE:
Remain UNDER_CONSIDERATION unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Failure must not leave an apparently DECIDED record without provable human authority.
```

---

# 37. Decision Does Not Equal Authorized Execution

A Decision in `DECIDED` state is a human decision record.

It does not itself grant every downstream transition.

For any downstream action:

```text
DECIDED Decision
+
requested transition
+
04 authority resolution
+
03 preconditions
+
06 boundary checks
=
potentially AUTHORIZED transition

AUTHORIZED transition
+
successful commit
=
actual target state
```

This preserves:

```text
human decision
!= authorized transition
!= executed state
```

---

# 38. GAP-03-005: Decision Revision / Supersession

LEVEL 1 does not define:

```text
decision revision
decision withdrawal
decision supersession
multiple decisions on same question
```

03 does not permit:

```text
DECIDED -> UNDER_CONSIDERATION
```

as a silent rewrite.

If a decision changes, later architecture must decide whether to:

```text
create a new Decision linked to the prior Decision
or
introduce an explicit supersession lifecycle
```

Status:

```text
[UNDERDEFINED]
```

---

# 39. Question Selection as State-Preserving Consequential Mutation

QuestionSelection is a relation, not a state.

Creating it is consequential.

## TRN-SEL-001 SELECT_COMPELLING_QUESTION

```text
CURRENT STATE:
Session = QUESTION_SELECTION.

REQUESTED TRANSITION:
SELECT_COMPELLING_QUESTION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SEL-001.

PRECONDITIONS:
Question belongs to the Session's Challenge.
Question is eligible for selection under later method contract.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Question and Session relation.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
Decision.
Audit.

ALLOW CONDITION:
Human selection authority passes.

DENY CONDITION:
AI attempts to create authority-bearing selection.
Question belongs to another Workspace/Challenge.
Selection cardinality would violate method rule.

NEXT STATE:
Session remains QUESTION_SELECTION.
QuestionSelection relation is added.

PERSISTENCE CONSEQUENCE:
Canonical selection relation created.

AUDIT CONSEQUENCE:
Human selection is traceable.

FAILURE STATE:
No selection relation on precommit failure.

RECOVERY / ROLLBACK REQUIREMENT:
No AI recommendation may be promoted as recovery.
```

## TRN-SEL-002 SELECT_PRIMARY_QUESTION

```text
CURRENT STATE:
Session = QUESTION_SELECTION.

REQUESTED TRANSITION:
SELECT_PRIMARY_QUESTION.

ACTOR:
Human actor.

AUTHORITY REQUIREMENT:
AUTH-DEP-SEL-002.

PRECONDITIONS:
Question is among valid candidate/compelling Questions.
No conflicting primary selection exists unless explicit replacement semantics are authorized later.

REQUIRED EVIDENCE:
SYSTEM_PROOF of Question identity and selection context.

BOUNDARY DEPENDENCIES:
Authority.
Human / AI.
Audit.

ALLOW CONDITION:
Human decision and authority pass.

DENY CONDITION:
AI-only selection.
Conflicting primary selection without governed replacement.
Cross-Challenge Question.

NEXT STATE:
Session remains QUESTION_SELECTION.
Primary QuestionSelection relation is established.

PERSISTENCE CONSEQUENCE:
One primary Question is recorded.

AUDIT CONSEQUENCE:
Primary selection is reconstructable.

FAILURE STATE:
Prior selection state preserved unless indeterminate.

RECOVERY / ROLLBACK REQUIREMENT:
Do not auto-pick highest AI score.
```

---

# 40. ImpactChain Structural State

ImpactChain has no source lifecycle enum.

03 therefore models completeness structurally.

## 40.1 Incomplete

An ImpactChain has fewer than the required five stored answer nodes.

## 40.2 Complete

An ImpactChain has exactly the five required ordered answer nodes for the source-defined Five-Why structure.

These are derived structural predicates, not persisted lifecycle states unless 09 later chooses to cache them.

## 40.3 Consequence

For Question Burst method progression to INVESTIGATION:

```text
ImpactChain.complete == true
```

is a SYSTEM_PROOF requirement.

No AI may fill missing answers as an authority substitute for the human inquiry sequence unless later source explicitly permits it.

---

# 41. AIGeneration Lifecycle Dependency

02 explicitly delegated AIGeneration lifecycle/status semantics to 08/09.

03 does not steal that authority.

03 imposes only transition dependencies:

```text
unvalidated AI output
must not satisfy a required analysis-completion proof

AI persistence
must not advance Session state

AI output
must not create human Decision state

AI output
must not authorize Experiment execution

AI output
must not create QuestionSelection authority
```

## GAP-02-009 preserved

AIGeneration lifecycle/status remains `[UNDERDEFINED]`.

03 requires 08 to provide enough lifecycle/validation state to satisfy:

```text
AI_VALIDATION_PROOF
```

for transitions such as `BEGIN_REFLECTION`.

---

# 42. AI-to-Canonical-State Leak Controls

The following paths are illegal:

```text
AI output
-> Session state advance

AI output
-> human QuestionSelection

AI output
-> Decision DECIDED

AI output
-> Experiment AUTHORIZED

AI output
-> Experiment IN_PROGRESS

AI confidence
-> Assumption SUPPORTED

AI confidence
-> Assumption REFUTED

AI-generated reframe
-> overwrite original Question

AI analysis event
-> state commit without transition evaluation
```

AI may produce derived records where 08 contracts permit.

Those records become inputs to later human/system transitions.

They are not transition authority.

---

# 43. UI-to-State Leak Controls

The following are illegal:

```text
screen opened
-> state advanced

button visible
-> action authorized

button clicked
-> state committed without transition evaluation

navigation route changed
-> Session state changed

client-side timer expired
-> Burst completed without governed transition

UI role label displayed
-> authority established
```

UI may request a transition.

The architecture decides whether it commits.

---

# 44. Authentication-to-State Leak Controls

Authentication proves identity.

It does not prove operation authority.

Illegal:

```text
authenticated actor
-> any transition permitted

authenticated Workspace member
-> any Session phase advancement permitted
```

04 must resolve operation authority.

---

# 45. Persistence-to-State Leak Controls

Illegal:

```text
INSERT Decision(selected_option)
-> implicitly DECIDED

INSERT Experiment
-> implicitly AUTHORIZED

INSERT AI result
-> implicitly ANALYSIS complete

INSERT QuestionSelection
without human authority
-> implicitly valid selection

UPDATE Session.state
without transition contract
-> valid state
```

All consequential persistence must correspond to valid transition/mutation contracts.

---

# 46. Derived-Analysis-to-State Leak Controls

Illegal:

```text
highest catalytic score
-> primary Question selection

AI cluster
-> Question status change

AI assumption confidence
-> Assumption evidence classification

AI recommendation
-> Decision DECIDED

AI experiment recommendation
-> Experiment AUTHORIZED
```

---

# 47. Implicit Transition Inventory

03 identifies source-implied transitions that were not explicit in the Session state chain.

## 47.1 Challenge creation

```text
absent -> present
```

## 47.2 Session creation

```text
absent -> DRAFT
```

## 47.3 QuestionBurst preparation/start/pause/resume/completion

Separate process state machine required by source behavior.

## 47.4 Question capture

State-preserving Session mutation that creates Question plus Burst membership.

## 47.5 Question reframe

Creates new Question + lineage.

Does not mutate original Question.

## 47.6 Question selection

Creates relation.

Does not itself move Session until explicit phase transition.

## 47.7 ImpactChain completion

Structural proof used by later phase transition.

## 47.8 AI analysis persistence

State-preserving ANALYSIS operation.

Does not auto-advance Session.

## 47.9 Assumption testing/reclassification

Independent Assumption state machine.

## 47.10 Experiment proposal/authorization/execution

Independent Experiment state machine.

## 47.11 Human Decision consideration/finalization

Independent Decision state machine.

## 47.12 Iterative re-entry

Creates new Session after prior Session CLOSED instead of reopening terminal Session.

---

# 48. Cross-Object State Invariants

## STATE-INV-01

```text
Session QUESTION_GENERATION
requires
associated QuestionBurst ACTIVE or PAUSED.
```

## STATE-INV-02

```text
QuestionBurst ACTIVE or PAUSED
requires
Session QUESTION_GENERATION.
```

## STATE-INV-03

```text
Session QUESTION_CAPTURE
requires
QuestionBurst COMPLETED.
```

## STATE-INV-04

```text
Session ANALYSIS or later
requires
raw QuestionBurst set frozen.
```

## STATE-INV-05

```text
QuestionBurst COMPLETED
forbids
new raw-set membership changes.
```

## STATE-INV-06

```text
Session QUESTION_SELECTION
or later
does not permit AI to create authority-bearing human selection.
```

## STATE-INV-07

```text
Assumption SUPPORTED/WEAK/REFUTED
requires
prior TESTING path.
```

## STATE-INV-08

```text
Experiment AUTHORIZED
requires
prior UNDER_CONSIDERATION.
```

## STATE-INV-09

```text
Experiment IN_PROGRESS
requires
prior AUTHORIZED.
```

## STATE-INV-10

```text
Decision DECIDED
requires
prior UNDER_CONSIDERATION.
```

## STATE-INV-11

```text
Decision DECIDED
does not imply
downstream action transition authorized.
```

## STATE-INV-12

```text
CLOSED Session
is terminal.
```

## STATE-INV-13

```text
INDETERMINATE transition outcome
blocks dependent consequential transitions
until recovery resolves last valid state.
```

---

# 49. Unreachable and Invalid Compound States

The following compound states are invalid:

```text
Session QUESTION_GENERATION
+
QuestionBurst COMPLETED

Session QUESTION_CAPTURE
+
QuestionBurst ACTIVE

Session ANALYSIS
+
QuestionBurst ACTIVE

Session REFLECTION
+
QuestionBurst not COMPLETED

Experiment IN_PROGRESS
+
Experiment never AUTHORIZED

Experiment COMPLETED
+
no prior IN_PROGRESS transition

Decision DECIDED
+
no attributable human decision path

Assumption SUPPORTED
+
no prior TESTING transition

Question original_text changed after creation

CLOSED Session
+
subsequent Session state transition

QuestionBurst COMPLETED
+
new raw Question membership added
```

A persistence layer capable of representing one of these combinations does not make it valid architecture state.

---

# 50. Failure-State Requirements Per Transition

03 does not define detailed recovery algorithms.

It does define required failure semantics.

## 50.1 Eligibility failure

Outcome:

```text
DENIED
```

Canonical state unchanged.

## 50.2 Validation failure

Outcome:

```text
FAILED_PRECOMMIT
```

Canonical state unchanged.

## 50.3 Technical failure before commit

Outcome:

```text
FAILED_PRECOMMIT
```

Canonical state unchanged.

## 50.4 Uncertain cross-object commit

Outcome:

```text
INDETERMINATE
```

Dependent transitions blocked.

## 50.5 AI failure in ANALYSIS

Session remains:

```text
ANALYSIS
```

unless a later explicit recovery/fallback contract establishes another valid path.

## 50.6 Burst capture uncertainty

No transition to QUESTION_CAPTURE or ANALYSIS until raw capture consistency is proven.

## 50.7 Audit uncertainty

If state/audit consistency cannot be proven due unresolved DEC-A007, transition outcome must be treated as INDETERMINATE for high-assurance purposes.

Exact implementation remains 09/10 work.

---

# 51. GAP-03-006: Required AI Analysis Failure / Bypass Path

LEVEL 1 MVP requires AI question analysis.

LEVEL 1 does not define what happens if required post-burst AI analysis:

```text
times out
fails repeatedly
is unavailable
returns invalid output
```

LEVEL 2 suggested skip/fallback behavior, but that is not source authority.

03 therefore defines:

```text
Session remains ANALYSIS
```

until 08/10 provide an accepted recovery path.

Status:

```text
[UNDERDEFINED]
```

This is prototype-critical because REFLECTION progression depends on analysis completion under current MVP source.

---

# 52. GAP-03-007: Reflection Completion Semantics

Reflection is a required phase.

02 identified Reflection persistence as underdefined.

03 requires an explicit proof that Reflection has been completed before entering QUESTION_SELECTION.

The source does not define:

```text
whether answering all reflection prompts is mandatory
whether zero answers can count as completion
whether responses must be persisted
whether human confirmation alone completes the phase
```

Status:

```text
[UNDERDEFINED]
```

No UI navigation may be used as implicit completion.

---

# 53. GAP-03-008: Investigation Completion Semantics

The Session state machine includes INVESTIGATION.

The source defines:

```text
evidence collection
research mode
observation
who to talk to
what to learn
```

but does not define a universal condition for completing INVESTIGATION.

Status:

```text
[UNDERDEFINED]
```

03 allows `BEGIN_EXPERIMENT_PHASE` only when a later method contract establishes investigation completion.

No generic "next" button may substitute for that proof.

---

# 54. GAP-03-009: Action Completion Semantics

The Session state machine includes ACTION and REVIEW.

02 correctly does not define an Action domain object.

LEVEL 1 does not define how N.Q.U.I.R.Y. proves an external action actually occurred.

03 therefore distinguishes:

```text
Session enters ACTION phase
from
external-world action objectively verified
```

Transition to REVIEW requires an authorized Action-phase completion assertion under later contract.

Status:

```text
[UNDERDEFINED]
```

This does not falsify 02.

No new Action object is introduced.

---

# 55. GAP-03-010: Decision Evidence Sufficiency

Decision contains Evidence in LEVEL 1.

Human agency requires human responsibility for decisions.

The source does not define:

```text
whether evidence is mandatory for every Decision
minimum evidence quantity
validation threshold
how contradictory evidence affects eligibility
```

Status:

```text
[UNDERDEFINED]
```

03 therefore does not make DOMAIN_EVIDENCE universally mandatory for every Decision.

07 must close evidence semantics.

04 must close decision authority.

---

# 56. GAP-03-011: Experiment Evidence Sufficiency

The source links Assumptions, Experiments and Evidence.

It does not define a universal evidence threshold for experiment authorization.

Status:

```text
[UNDERDEFINED]
```

03 requires evidence only where a later method/07 contract makes it mandatory.

---

# 57. GAP-03-012: Automated System Authority

The source implies system-driven behavior such as:

```text
timer ends Burst
AI processing occurs
stateful recovery may occur
```

04 must distinguish:

```text
human authority
system authority derived from configured policy/method
AI generation
```

03 does not treat:

```text
SYSTEM
AI
```

as equivalent actors.

Status:

```text
[UNDERDEFINED AUTHORITY DEPENDENCY]
```

---

# 58. GAP-03-013: Challenge Status Vocabulary

Carried from GAP-02-012.

Still unresolved.

## High-assurance effect

No transition may depend on Challenge.status until closed.

---

# 59. GAP-03-014: Question Status Vocabulary

Carried from GAP-02-013.

Still unresolved.

## High-assurance effect

No transition may depend on Question.status until closed.

---

# 60. GAP-03-015: AIGeneration Lifecycle

Carried from GAP-02-009.

Still unresolved and delegated to 08/09.

## High-assurance effect

08 must provide a status/validation model sufficient to distinguish:

```text
requested
successful but unvalidated
validated
rejected/invalid
failed
```

or an equivalent model.

03 does not prescribe the final enum.

---

# 61. GAP-03-016: Audit Atomicity

Carried from DEC-A007.

State and audit must remain reconstructably consistent.

Exact atomicity/compensation/replay mechanism remains unresolved.

This is baseline-blocking for a high-assurance prototype.

---

# 62. GAP-03-017: Cross-Object Commit Atomicity

Some state transitions logically update more than one object:

```text
Session CHALLENGE_CAPTURE -> QUESTION_GENERATION
+
QuestionBurst PREPARED -> ACTIVE

Session QUESTION_GENERATION -> QUESTION_CAPTURE
+
QuestionBurst ACTIVE/PAUSED -> COMPLETED
+
raw membership freeze
```

03 requires these to behave as one logical transition bundle.

09/10 must define whether this is achieved through:

```text
single database transaction
transaction + durable command
event-driven saga with proven invariants
other mechanism
```

Status:

```text
[ARCHITECTURAL CLOSURE REQUIREMENT, IMPLEMENTATION MECHANISM OPEN]
```

---

# 63. GAP-03-018: Primary Question Replacement

LEVEL 1 requires one most-important Question.

It does not define whether that primary selection may be changed after selection.

03 therefore prohibits silent replacement.

Later architecture must define:

```text
replacement authority
audit
ImpactChain invalidation/rebuild semantics
```

Status:

```text
[UNDERDEFINED]
```

---

# 64. GAP-03-019: Assumption WEAK Threshold

03 defines `WEAK` as an evidence classification distinct from SUPPORTED and REFUTED.

LEVEL 1 does not define the threshold.

07 must define evidence semantics or preserve it as methodology-specific.

Status:

```text
[UNDERDEFINED]
```

---

# 65. Authority Dependencies for 04

03 requires 04 to resolve authority for at least the following operations.

This is not an Authority Matrix.

It is a dependency inventory.

```text
AUTH-DEP-CH-001    Create Challenge

AUTH-DEP-SESS-001  Create Session
AUTH-DEP-SESS-002  Begin Setup
AUTH-DEP-SESS-003  Begin Challenge Capture
AUTH-DEP-SESS-004  Open Question Generation
AUTH-DEP-SESS-005  Close Question Generation
AUTH-DEP-SESS-006  Begin Analysis
AUTH-DEP-SESS-007  Begin Reflection
AUTH-DEP-SESS-008  Begin Question Selection
AUTH-DEP-SESS-009  Begin Investigation
AUTH-DEP-SESS-010  Begin Experiment Phase
AUTH-DEP-SESS-011  Begin Action Phase
AUTH-DEP-SESS-012  Begin Review
AUTH-DEP-SESS-013  Close Session

AUTH-DEP-BURST-001 Prepare Burst
AUTH-DEP-BURST-002 Start Burst
AUTH-DEP-BURST-003 Pause Burst
AUTH-DEP-BURST-004 Resume Burst
AUTH-DEP-BURST-005 Complete Burst

AUTH-DEP-Q-001     Capture Burst Question

AUTH-DEP-SEL-001   Select Compelling Question
AUTH-DEP-SEL-002   Select Primary Question

AUTH-DEP-ASM-001   Begin Assumption Test
AUTH-DEP-ASM-002   Classify Assumption Test Result

AUTH-DEP-EXP-002   Begin Human Experiment Consideration
AUTH-DEP-EXP-003   Authorize Experiment
AUTH-DEP-EXP-004   Start Experiment
AUTH-DEP-EXP-005   Complete Experiment

AUTH-DEP-DEC-001   Open Decision Consideration
AUTH-DEP-DEC-002   Record Human Decision
```

04 must preserve source-specific minimum facts, including:

```text
Facilitator can create a Challenge.
Facilitator can start a Question Burst.
Facilitator can pause/end a Question Burst.
Participants can submit Questions.
Humans remain responsible for decisions, interpretation, experiments, actions and ethical judgments.
AI cannot silently become human decision authority.
```

04 may not infer authority merely from state topology.

---

# 66. Boundary Dependencies for 06

03 requires 06 to supply executable boundary contracts for transitions that depend on:

```text
Identity
Workspace
Authority
Question Burst
Human / AI
AI Context
Evidence
Provenance
Decision
Audit
Failure
Recovery
```

03 defines transition topology.

06 defines boundary enforcement.

Neither may silently redefine the other.

---

# 67. Evidence Dependencies for 07

03 requires 07 to resolve:

```text
Assumption classification evidence sufficiency
Decision evidence sufficiency
Experiment evidence requirements
Evidence validation authority relationship to 04
contradictory evidence semantics
WEAK threshold semantics
```

03 does not use:

```text
AI confidence
AI classification
AI inference
```

as DOMAIN_EVIDENCE.

---

# 68. AI Dependencies for 08

03 requires 08 to define:

```text
AI operation lifecycle
AI_VALIDATION_PROOF
analysis completion semantics
failure/retry semantics
direct-call prohibition enforcement
derived-output contracts
active-Burst AI prohibition enforcement
```

08 may not make validated AI output equivalent to authority.

---

# 69. Data/Event Dependencies for 09

03 requires 09 to materialize:

```text
state fields
transition requests
cross-object transition bundles
QuestionBurst membership freeze
QuestionSelection relations
Decision state persistence
Experiment state persistence
Assumption state persistence
audit references
idempotency/replay support
```

09 may not permit direct state mutation that bypasses 03 transition contracts.

---

# 70. Failure/Recovery Dependencies for 10

03 requires 10 to define recovery for:

```text
INDETERMINATE transitions
partial cross-object commits
acknowledged Question capture with uncertain persistence
Burst completion uncertainty
AI analysis failure
audit failure
recovery of last confirmed Session/Burst states
```

10 may not reconstruct a state that 03 declares illegal.

---

# 71. State-Machine Consistency Validation

## 71.1 Session topology

**PASS**

All source-defined Session states are present.

No source state is silently removed.

No skip path is enabled.

## 71.2 QuestionBurst topology

**PASS WITH CLOSURE**

PREPARED, ACTIVE, PAUSED and COMPLETED are sufficient to materialize source start/pause/end/freeze behavior without importing LEVEL 2 CANCELLED/RECOVERING states.

## 71.3 Assumption topology

**PASS WITH CLOSURE**

All source-defined status values are present.

Reclassification requires TESTING.

AI generation cannot directly establish evidentiary classifications.

## 71.4 Experiment topology

**PASS WITH CLOSURE**

Source `status` field is made high-assurance through:

```text
PROPOSED
UNDER_CONSIDERATION
AUTHORIZED
IN_PROGRESS
COMPLETED
```

AI proposal does not equal authorized execution.

## 71.5 Decision topology

**PASS WITH CLOSURE**

Decision distinguishes:

```text
UNDER_CONSIDERATION
DECIDED
```

while transition authorization and actual execution remain separate dimensions.

## 71.6 Question and Challenge status

**PASS WITH EXPLICIT GAPS**

Undefined source status vocabularies are not silently invented.

They cannot be used as transition guards.

---

# 72. Illegal Transition Path Validation

**PASS**

The architecture explicitly rejects:

```text
state skipping
AI-driven Session advancement
AI-driven Decision finalization
AI-driven Experiment authorization
AI-driven Question selection
QuestionBurst analysis while active
Question mutation by reframe
Assumption evidentiary reclassification from AI confidence
CLOSED Session reopening
raw Burst membership changes after completion
```

---

# 73. Implicit Transition Validation

**PASS WITH EXPOSED GAPS**

Previously implicit consequential operations are now explicit:

```text
creation
Burst pause/resume
Question capture
Question selection
AI analysis persistence
Impact completeness
Assumption testing
Experiment proposal/authorization/execution
Decision consideration/finalization
iterative new Session creation
```

No UI navigation or event emission remains an accepted implicit state transition.

---

# 74. Authority Dependency Validation

**PASS**

03 identifies where authority is required without assigning a complete operation-to-role matrix.

Source-specific authority facts are preserved.

04 remains necessary.

No role label is treated as sufficient authority.

---

# 75. AI-to-Canonical-State Leak Validation

**PASS**

No legal transition permits:

```text
AI output
AI confidence
AI persistence
AI event
AI classification
```

to independently create:

```text
human selection
Decision DECIDED
Experiment AUTHORIZED
Session phase progression
Assumption evidentiary classification
```

---

# 76. Failure / Recovery Validation

**PASS WITH OPEN MECHANISM GAPS**

Every consequential transition resolves failure into:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

No failure silently advances state.

Exact recovery mechanisms remain correctly delegated to 10.

Cross-object commit and audit atomicity remain baseline-blocking open architecture dependencies.

---

# 77. Cross-Check Against 00

## Result

**PASS**

03 preserves:

```text
consequential transition closure invariant
Human Decision Authority
Governance Before Consequence
AI confidence != authority
recovery valid-state invariant
one authoritative home
recursive reconstruction
```

No 00 fact is falsified.

No 00 reconstruction is required.

---

# 78. Cross-Check Against 01

## Result

**PASS**

03 preserves:

```text
Identity != authority
Workspace scope
Question Burst protected boundary
Human / AI separation
AI context separation
provider independence
Evidence over confidence
Decision boundary
Failure / Recovery boundaries
```

No 01 fact is falsified.

No 01 reconstruction is required.

---

# 79. Cross-Check Against 02

## Result

**PASS**

03 preserves:

```text
THING != RELATION != STATE != EVENT != AUTHORITY != EVIDENCE != PROJECTION != CONFIGURATION

canonical persistence != epistemic truth

AI generation != authority

human authorship != automatic authority

origin != derivation

projection != canonical state

Question original_text immutability

Question reframe creates new identity

QuestionSelection remains relation

AuditEvent remains event

InquiryGraph remains projection

AIGeneration remains operational record
```

03 does not introduce:

```text
Action object
Tenant object
Organization object
Reflection object
universal provenance schema
authority matrix
```

No 02 fact is falsified.

No upstream reconstruction is required.

---

# 80. New Architectural Closures Introduced in 03

| ID | Addition | Status | Structural reason |
|---|---|---|---|
| AC-03-001 | CLOSED Session is terminal; renewed full inquiry creates a new Session under same Challenge | `[ARCHITECTURAL CLOSURE]` | Reconciles iterative inquiry with source terminal Session state |
| AC-03-002 | Every newly persisted Assumption begins UNKNOWN unless future validated import path exists | `[ARCHITECTURAL CLOSURE]` | Prevents AI/inference from becoming evidentiary classification |
| AC-03-003 | Proposal, Human Consideration, Human Decision, Transition Authorization and Executed State are separate architectural stages | `[ARCHITECTURAL CLOSURE]` | High-assurance Human Decision Authority |
| AC-03-004 | Transition outcomes DENIED / FAILED_PRECOMMIT / COMMITTED / INDETERMINATE | `[ARCHITECTURAL CLOSURE]` | Prevents uncertain failures from silently becoming state |
| AC-03-005 | Unknown required condition denies commit | `[ARCHITECTURAL CLOSURE]` | High-assurance fail-closed transition eligibility |
| AC-03-006 | Session state semantics for source-named states | `[ARCHITECTURAL CLOSURE]` | Source gives names/order but not executable meanings |
| AC-03-007 | QUESTION_GENERATION is input-open protected Burst phase; QUESTION_CAPTURE is input-closed frozen-raw-set phase | `[ARCHITECTURAL CLOSURE]` | Reconciles source Burst workflow with source Session state order |
| AC-03-008 | Session/Burst start and completion are logical cross-object transition bundles | `[ARCHITECTURAL CLOSURE]` | Prevents impossible partial compound state |
| AC-03-009 | QuestionBurst states PREPARED / ACTIVE / PAUSED / COMPLETED | `[ARCHITECTURAL CLOSURE]` | Required to materialize source start/pause/end/freeze semantics |
| AC-03-010 | Reclassification of Assumption must pass through TESTING | `[ARCHITECTURAL CLOSURE]` | Makes evidence-based classification explicit |
| AC-03-011 | Assumption operational meanings for UNKNOWN/TESTING/SUPPORTED/WEAK/REFUTED | `[ARCHITECTURAL CLOSURE]` | Source gives labels but not executable semantics |
| AC-03-012 | Experiment states PROPOSED / UNDER_CONSIDERATION / AUTHORIZED / IN_PROGRESS / COMPLETED | `[ARCHITECTURAL CLOSURE]` | Prevents AI proposal from becoming human-authorized execution |
| AC-03-013 | Decision states UNDER_CONSIDERATION / DECIDED | `[ARCHITECTURAL CLOSURE]` | Separates proposal, human decision, transition authorization and execution |
| AC-03-014 | ImpactChain completeness is structural, not a new lifecycle state | `[ARCHITECTURAL CLOSURE]` | Preserves 02 object/state discipline |
| AC-03-015 | INDETERMINATE transition blocks dependent consequential transitions until recovery | `[ARCHITECTURAL CLOSURE]` | High-assurance recovery invariant |
| AC-03-016 | AI analysis completion requires independent AI_VALIDATION_PROOF before Reflection transition | `[ARCHITECTURAL CLOSURE]` | AI persistence/event must not equal phase completion |
| AC-03-017 | Question/Challenge undefined status fields may not be used as guards until vocabulary closes | `[ARCHITECTURAL CLOSURE]` | Prevents hidden invented semantics |

No operation-level Authority Matrix is introduced.

---

# 81. New Gaps Exposed in 03

```text
GAP-03-001 Session cancellation / abandonment
GAP-03-002 Burst pause / timer semantics
GAP-03-003 Questions-only enforcement mechanism
GAP-03-004 Experiment cancellation / abandonment
GAP-03-005 Decision revision / supersession
GAP-03-006 Required AI analysis failure / bypass path
GAP-03-007 Reflection completion semantics
GAP-03-008 Investigation completion semantics
GAP-03-009 Action completion semantics
GAP-03-010 Decision evidence sufficiency
GAP-03-011 Experiment evidence sufficiency
GAP-03-012 Automated System authority
GAP-03-013 Challenge status vocabulary
GAP-03-014 Question status vocabulary
GAP-03-015 AIGeneration lifecycle
GAP-03-016 Audit atomicity
GAP-03-017 Cross-object commit atomicity
GAP-03-018 Primary Question replacement
GAP-03-019 Assumption WEAK threshold
```

These remain classified exactly as stated in their sections.

---

# 82. Readiness for 04

03 provides 04 with an explicit authority dependency surface.

04 can now assign decision rights without inventing the state machine.

Stable inputs to 04 include:

```text
which transitions exist
which transitions are consequential
which transitions are human-directed by source
which transitions may be system-triggered by source
where AI is prohibited from authority
where human decision is required
where authority is separate from state
where selection is authority-bearing
where experiment authorization is required
where Decision DECIDED still does not authorize execution
where Session/Burst transitions are logically coupled
```

04 must not:

```text
add state transitions merely to simplify authority
collapse AI proposal into human authority
use role labels as self-executing authority
treat authentication as authority
change state semantics defined in 03
authorize illegal skip paths
```

## Readiness result

**READY FOR HUMAN REVIEW**

`03_STATE_AND_TRANSITION_ARCHITECTURE.md` is structurally ready to become the authoritative State and Transition input for `04_AUTHORITY_AND_DECISION_RIGHTS.md`.

04 is not yet authorized.

No downstream architecture file has been built.

No implementation work has begun.

No Architecture Baseline has been frozen.

---

# 83. Stop Gate

**STOP CONDITION REACHED**

Await human review and explicit:

```text
HUMAN_REVIEW::03_APPROVED
GO::BUILD_04_AUTHORITY_AND_DECISION_RIGHTS
```
