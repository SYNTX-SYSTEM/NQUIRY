# 05_GOVERNANCE_INSIDE_SYSTEM

**Project:** N.Q.U.I.R.Y.  
**Document role:** Authoritative Governance Inside System Architecture  
**Architecture stage:** F, Governance Inside System  
**Upstream authority:** `00_NQUIRY_MASTER_ARCHITECTURE.md`, `01_SYSTEM_BOUNDARY_AND_PRINCIPLES.md`, `02_DOMAIN_AND_RELATION_MODEL.md`, `03_STATE_AND_TRANSITION_ARCHITECTURE.md`, `04_AUTHORITY_AND_DECISION_RIGHTS.md`  
**LEVEL 1 authority:** `N.Q.U.I.R.Y. - Product & System Specification`  
**LEVEL 2 input:** `# 00 EXECUTIVE SYSTEM VERDICT_SWEEP_PROCESSED.md`  
**Status:** DRAFT FOR HUMAN REVIEW  
**Baseline:** Not frozen  
**Downstream authorization:** 06 not yet authorized

---

# 0. Document Authority

This file is authoritative for:

```text
governance bootstrap semantics
governance control points
HumanAuthorityBinding lifecycle
membership administration governance
Workspace role administration governance
Facilitator scope governance
authority-binding grant/change/revoke mechanisms
authority reassignment behavior
in-flight revocation behavior
method-approval governance gate
SYSTEM_DERIVED authority activation governance
export governance gate
default-deny governance behavior
governance persistence semantics
governance audit semantics
governance failure/recovery requirements
```

This file is not authoritative for:

```text
domain-object identity
domain relation semantics
state topology
new domain state transitions
operation-level authority classes
new decision-right classes
boundary implementation
evidence-validation rules
universal provenance fields
database wire schema
API endpoint schema
audit event payload schema
recovery implementation
prototype scope
```

02 remains authoritative for THING and RELATION.

03 remains authoritative for STATE and TRANSITION.

04 remains authoritative for AUTHORITY and DECISION RIGHTS.

05 operationalizes those facts.

---

# 1. Governance Objective

Governance exists to ensure that consequential system effects occur only through authority and transition structures already defined upstream.

Governance is not:

```text
policy prose
UI hiding
prompt instructions
role names
documentation
confidence scores
manual convention
```

Governance is the executable control layer that determines whether a consequential request may reach the transition and persistence path.

The governance path is:

```text
REQUEST
-> IDENTITY RESOLUTION
-> SCOPE RESOLUTION
-> GOVERNANCE SUBJECT RESOLUTION
-> AUTHORITY SOURCE RESOLUTION
-> AUTHORITY BINDING VALIDATION
-> PRECONDITION VALIDATION
-> BOUNDARY CHECK
-> HUMAN DECISION CHECK WHERE REQUIRED
-> SYSTEM_DERIVED AUTHORITY CHECK WHERE PERMITTED
-> ALLOW OR DENY
-> 03 TRANSITION EVALUATION
-> COMMIT OR FAILURE
-> AUDIT
```

Governance does not replace 03 transition evaluation.

Governance does not replace 04 authority semantics.

---

# 2. Binding Invariants Preserved

05 preserves:

```text
authentication != authority

role != authority

AI != System

AI generation != authority

human authorship != automatic authority

human decision != transition authorization

transition authorization != executed state

canonical persistence != epistemic truth

THING != RELATION != STATE != EVENT != AUTHORITY != EVIDENCE != PROJECTION != CONFIGURATION
```

Governance mechanisms may reference these dimensions.

They may not collapse them.

---

# 3. Governance Subjects

A governance mechanism must name the thing whose authority or control status is being governed.

Permitted governance subjects in 05 include:

```text
Workspace governance root
WorkspaceMembership
Workspace role assignment
Facilitator scope
HumanAuthorityBinding
SYSTEM_DERIVED authority rule
InquiryMethod approval status
Export request governance
```

A governance subject is not automatically a domain object.

---

# 4. Governance Actors

05 permits these governance actor classes:

```text
HUMAN_USER
SYSTEM_SERVICE
```

`AI_PROCESSOR` is not a governance actor for granting, changing or revoking human authority.

An AI may provide information to governance workflows.

It may not execute a human-governance decision.

---

# 5. Governance Authority

Governance authority must resolve to one of the authority sources approved in 04:

```text
LEVEL_1_EXPLICIT
ARCHITECTURAL_CLOSURE
EXPLICIT_AUTHORITY_BINDING
SYSTEM_DERIVED
OPEN_UNRESOLVED
```

Governance may not invent:

```text
implicit role authority
implicit Owner override
implicit administrator override
AI authority
emergency superuser
```

---

# 6. Governance State Is Separate From Domain State

05 introduces governance-state semantics only for governance constructs already anticipated by 04.

These do not alter 03 domain/process state topology.

Examples:

```text
HumanAuthorityBinding ACTIVE / REVOKED
FacilitatorScopeBinding ACTIVE / REVOKED
membership relation present / absent
role assignment present / absent
method approval gate satisfied / unsatisfied
```

These are governance facts.

They are not:

```text
Session states
QuestionBurst states
Experiment states
Decision states
Assumption states
```

---

# 7. Governance Default Deny

**[ARCHITECTURAL CLOSURE, inherited from AC-04-014]**

If governance cannot prove a valid authority path:

```text
DENY
```

If governance cannot prove the scope:

```text
DENY
```

If governance cannot prove the binding is effective:

```text
DENY
```

If governance cannot prove a required human decision exists:

```text
DENY
```

If governance cannot prove a SYSTEM_DERIVED rule is active and deterministic:

```text
DENY
```

If an OPEN authority question is required for the operation:

```text
DENY
```

No lower-assurance fallback is permitted.

---

# 8. HumanAuthorityBinding Lifecycle

04 defines `HumanAuthorityBinding` as a scope-bounded authority construct.

05 defines its lifecycle.

## 8.1 States

```text
ACTIVE
REVOKED
```

Status:

```text
[ARCHITECTURAL CLOSURE]
```

`REVOKED` is terminal for that binding record.

A changed authority assignment creates a new binding rather than mutating historical authority semantics in place.

## 8.2 Binding identity

A binding must be independently reconstructable.

It must distinguish:

```text
human subject
authority class
scope
authority source
granting actor
grant time
revocation status
revocation actor
revocation time
```

Exact field schema belongs to 09.

## 8.3 No generic ACL semantics

A HumanAuthorityBinding does not contain arbitrary strings such as:

```text
can_do_anything
admin
superuser
*
```

It binds one approved authority class to one bounded scope.

Permitted authority classes remain those defined in 04.

---

# 9. GOV-001 Workspace Governance Bootstrap

## GOVERNANCE SUBJECT

```text
Workspace governance root
```

## GOVERNANCE ACTOR

Initial bootstrap actor remains structurally dependent on the authoritative Workspace creation path.

No new Workspace creation authority is invented in 05.

## GOVERNANCE AUTHORITY

```text
Workspace.owner_id
```

is the approved 04 governance root.

## TARGET SCOPE

Exactly one Workspace.

## GRANT / CHANGE / REVOKE OPERATION

Bootstrap establishes:

```text
owner_id
+
active WorkspaceMembership for the owner
+
WORKSPACE_GOVERNANCE_RIGHT root semantics
```

05 does not define Workspace ownership transfer or root replacement.

## PRECONDITIONS

```text
Workspace exists or is being validly created by a later authoritative creation contract.
owner_id references an authenticated human User.
owner User resolves to the same Workspace membership context.
no second conflicting governance root exists.
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
Workspace identity
owner User identity
owner_id consistency
membership consistency
```

## BOUNDARY CHECK

```text
Identity
Workspace
Authority
Audit
```

## EFFECTIVE STATE

Governance-ready predicate is true only when:

```text
Workspace exists
+
owner_id resolves to one human User
+
owner has active WorkspaceMembership
```

No new Workspace lifecycle state is introduced.

## IN-FLIGHT CONSEQUENCE

Not applicable before bootstrap is valid.

No consequential Workspace governance operation may proceed while governance-ready predicate is false.

## DEFAULT-DENY BEHAVIOR

If root cannot be proven:

```text
all Workspace governance mutations denied
```

## PERSISTENCE REQUIREMENT

The root relation and membership must be durably reconstructable.

Exact persistence mechanism belongs to 09.

## AUDIT REQUIREMENT

Bootstrap must record:

```text
Workspace
owner identity
bootstrap source
time
correlation to Workspace creation/provisioning
```

## FAILURE BEHAVIOR

Partial bootstrap is invalid.

Examples:

```text
owner_id exists but owner membership missing
owner membership exists but owner_id unresolved
multiple conflicting roots
```

Governance must fail closed.

## RECOVERY / REASSIGNMENT PATH

Recovery may repair a partial bootstrap only by reconciling to one provable root.

Owner transfer/replacement is not defined.

See `GAP-05-001`.

---

# 10. GAP-05-001 Workspace Root Creation and Succession

**Status:** `[UNDERDEFINED]`

04 establishes `owner_id` as governance root.

LEVEL 1 does not define:

```text
who may create the first Workspace
how owner_id is initially chosen
owner transfer
owner succession
co-owner semantics
recovery if owner identity disappears
```

05 does not invent those rights.

High-assurance effect:

```text
a Workspace without a provable governance root is governance-inactive
```

This does not require reconstruction of 00 through 04.

It is a newly exposed bootstrap dependency.

---

# 11. GOV-002 Grant Workspace Membership

## GOVERNANCE SUBJECT

```text
WorkspaceMembership
```

## GOVERNANCE ACTOR

Authenticated HUMAN_USER holding Workspace governance root authority.

Under current 04 architecture:

```text
Workspace owner
```

## GOVERNANCE AUTHORITY

```text
WORKSPACE_GOVERNANCE_RIGHT
```

derived from AC-04-001.

## TARGET SCOPE

Exactly the governed Workspace.

## GRANT / CHANGE / REVOKE OPERATION

```text
GRANT_MEMBERSHIP
```

creates the User-to-Workspace membership relation.

## PRECONDITIONS

```text
governance-ready Workspace
target User identity exists
target User is human User
target User is not already an active member under conflicting membership
grantor is current Workspace governance root
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
grantor root authority
target identity
Workspace identity
membership non-conflict
```

## BOUNDARY CHECK

```text
Identity
Workspace
Authority
Audit
```

## EFFECTIVE STATE

Target User gains active Workspace membership.

Membership does not itself grant any consequential authority beyond source rights explicitly tied to participation or later role/binding governance.

## IN-FLIGHT CONSEQUENCE

No active operation is retroactively affected merely by adding membership.

New authority remains unavailable until separately assigned.

## DEFAULT-DENY BEHAVIOR

No root authority:

```text
membership grant denied
```

## PERSISTENCE REQUIREMENT

Membership relation must be durable and uniquely scoped to Workspace/User pair.

## AUDIT REQUIREMENT

Record:

```text
grantor
target User
Workspace
operation
time
initial role assignment if performed separately
```

## FAILURE BEHAVIOR

No partial authority grant.

If membership persistence cannot be proven:

```text
target remains non-member for governance purposes
```

## RECOVERY / REASSIGNMENT PATH

Retry only after current membership state is reconciled.

---

# 12. GOV-003 Revoke Workspace Membership

## GOVERNANCE SUBJECT

```text
WorkspaceMembership
+
dependent governance bindings
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

```text
WORKSPACE_GOVERNANCE_RIGHT
```

## TARGET SCOPE

One User membership in one Workspace.

## GRANT / CHANGE / REVOKE OPERATION

```text
REVOKE_MEMBERSHIP
```

## PRECONDITIONS

```text
target membership exists
grantor is current governance root
target is not the sole Workspace governance root unless a valid succession mechanism exists
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
membership
grantor authority
dependent HumanAuthorityBindings
dependent FacilitatorScopeBindings
active Session participation references where governance impact matters
```

## BOUNDARY CHECK

```text
Workspace
Authority
Audit
Failure
Recovery
```

## EFFECTIVE STATE

Target membership becomes absent/inactive.

All Workspace-scoped HumanAuthorityBindings for that User become ineffective immediately because active membership is an authority precondition.

Governance must revoke or invalidate dependent bindings as the same logical governance bundle.

## IN-FLIGHT CONSEQUENCE

Operations not yet COMMITTED must re-evaluate authority at commit boundary.

If membership has been revoked before commit:

```text
authority fails
operation denied or failed precommit
```

Already COMMITTED transitions remain legitimate historical state.

Long-running domain processes do not roll back solely because membership was revoked.

Future consequential operations require reassignment.

## DEFAULT-DENY BEHAVIOR

If dependent governance state cannot be reconciled:

```text
deny further authority for target User
```

## PERSISTENCE REQUIREMENT

Membership revocation and dependent authority invalidation must be reconstructably consistent.

Exact atomicity mechanism belongs to 09/10.

## AUDIT REQUIREMENT

Record:

```text
revoking actor
target User
Workspace
dependent bindings invalidated
affected active scopes
time
```

## FAILURE BEHAVIOR

If membership revocation outcome is uncertain:

```text
target User is treated as unauthorized for new consequential operations
until reconciliation
```

## RECOVERY / REASSIGNMENT PATH

05 governance must permit another eligible human to receive required bindings before blocked workflows continue.

Owner self-removal is denied until owner succession is explicitly architected.

---

# 13. GOV-004 Assign Workspace Role

## GOVERNANCE SUBJECT

```text
Workspace role assignment on WorkspaceMembership
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

```text
WORKSPACE_GOVERNANCE_RIGHT
```

## TARGET SCOPE

One active WorkspaceMembership.

## GRANT / CHANGE / REVOKE OPERATION

Permitted role values remain source-defined:

```text
Owner
Facilitator
Contributor
Observer
Viewer
```

05 does not introduce new Workspace role labels.

Changing a role is modeled as:

```text
revoke prior role assignment semantics
+
assign new role assignment semantics
```

with historical audit preserved.

## PRECONDITIONS

```text
active membership
valid source role
grantor root authority
role assignment does not create a second Owner/root under unresolved owner semantics
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of membership, role vocabulary and root authority.

## BOUNDARY CHECK

```text
Workspace
Authority
Audit
```

## EFFECTIVE STATE

Role label becomes effective for that Workspace membership.

Role label alone still does not grant authority except where 04 explicitly binds source rights to the role.

## IN-FLIGHT CONSEQUENCE

If `Facilitator` role is removed:

```text
source-explicit Facilitator operations become unavailable immediately
unless another valid authority path exists
```

Existing COMMITTED transitions remain valid.

## DEFAULT-DENY BEHAVIOR

Unknown role:

```text
deny assignment
```

## PERSISTENCE REQUIREMENT

Role history must be reconstructable.

## AUDIT REQUIREMENT

Record prior role, new role, actor, scope, time.

## FAILURE BEHAVIOR

If role change cannot be proven, governance must not grant the more permissive interpretation.

## RECOVERY / REASSIGNMENT PATH

Reconcile to last confirmed role assignment.

---

# 14. Owner Role Change Restriction

Because Owner is the governance root:

```text
Owner role/root semantics
cannot be removed, transferred or duplicated
through ordinary GOV-004 role assignment
```

until `GAP-05-001` is closed.

This prevents role administration from silently becoming ownership succession.

---

# 15. GOV-005 Grant HumanAuthorityBinding

## GOVERNANCE SUBJECT

```text
HumanAuthorityBinding
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

```text
WORKSPACE_GOVERNANCE_RIGHT
```

## TARGET SCOPE

One approved authority class within one explicit scope.

Examples:

```text
SESSION_CONTROL_RIGHT on Challenge or Session
QUESTION_SELECTION_RIGHT on Session
ASSUMPTION_INTERPRETATION_RIGHT on Assumption/Challenge scope
EXPERIMENT_DECISION_RIGHT on Experiment
DECISION_RIGHT on Decision
ACTION_DECISION_RIGHT on Session/Challenge
```

## GRANT / CHANGE / REVOKE OPERATION

```text
GRANT_HUMAN_AUTHORITY_BINDING
```

creates a new ACTIVE binding.

## PRECONDITIONS

```text
target User authenticated identity exists
target User has active WorkspaceMembership
authority class exists in 04
scope is inside same Workspace
grantor is governance root
binding does not violate an unresolved cardinality rule
binding is not granted to AI_PROCESSOR or SYSTEM_SERVICE
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
membership
authority-class validity
scope ownership
grantor authority
```

## BOUNDARY CHECK

```text
Identity
Workspace
Authority
Audit
```

## EFFECTIVE STATE

One new ACTIVE HumanAuthorityBinding exists.

The binding grants only the named authority class in the named scope.

## IN-FLIGHT CONSEQUENCE

New binding affects authority checks after its effective grant commit.

It does not retroactively legitimize a previously denied or unauthorized operation.

## DEFAULT-DENY BEHAVIOR

Any unresolved scope or class mismatch:

```text
deny grant
```

## PERSISTENCE REQUIREMENT

Binding must be independently reconstructable and immutable as historical grant record.

## AUDIT REQUIREMENT

Record:

```text
grantor
target human
authority class
scope
authority source
time
```

## FAILURE BEHAVIOR

Failed or indeterminate grant:

```text
binding is not considered ACTIVE
```

until reconciliation proves grant commit.

## RECOVERY / REASSIGNMENT PATH

Retry or create a new binding only after duplicate/conflict check.

---

# 16. GOV-006 Change HumanAuthorityBinding

## GOVERNANCE SUBJECT

Existing ACTIVE HumanAuthorityBinding.

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

Existing binding plus replacement binding scope.

## GRANT / CHANGE / REVOKE OPERATION

05 prohibits in-place mutation of authority semantics.

Change is:

```text
REVOKE old binding
+
GRANT new binding
```

as one logical governance change.

## PRECONDITIONS

Both revocation and new grant are valid under GOV-005/GOV-007.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of old binding identity and new scope/class validity.

## BOUNDARY CHECK

Workspace, Authority, Audit, Failure, Recovery.

## EFFECTIVE STATE

Old binding:

```text
REVOKED
```

New binding:

```text
ACTIVE
```

## IN-FLIGHT CONSEQUENCE

Any not-yet-committed operation relying on old binding must re-evaluate authority.

## DEFAULT-DENY BEHAVIOR

If the replacement cannot be proven:

```text
do not treat the new authority as active
```

## PERSISTENCE REQUIREMENT

Old history preserved, new record created.

## AUDIT REQUIREMENT

Link replacement binding to revoked binding.

## FAILURE BEHAVIOR

Partial change is INDETERMINATE governance state.

Until reconciled:

```text
old binding cannot be assumed valid
new binding cannot be assumed valid
dependent consequential operations are denied
```

## RECOVERY / REASSIGNMENT PATH

Reconcile old/new commit results, then explicitly establish one valid authority path.

---

# 17. GOV-007 Revoke HumanAuthorityBinding

## GOVERNANCE SUBJECT

One ACTIVE HumanAuthorityBinding.

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

Binding's exact authority class and scope.

## GRANT / CHANGE / REVOKE OPERATION

```text
REVOKE_HUMAN_AUTHORITY_BINDING
```

## PRECONDITIONS

```text
binding exists
binding ACTIVE
grantor has governance root authority
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of binding identity and current status.

## BOUNDARY CHECK

Workspace, Authority, Audit, Failure, Recovery.

## EFFECTIVE STATE

Binding becomes:

```text
REVOKED
```

REVOKED is terminal.

## IN-FLIGHT CONSEQUENCE

See GOV-015.

Core rule:

```text
authority must still be valid when consequential operation is allowed to commit
```

A request evaluated before revocation but not yet committed cannot rely on stale authority.

## DEFAULT-DENY BEHAVIOR

If revocation outcome is uncertain:

```text
treat binding as unavailable for new consequential operations
```

## PERSISTENCE REQUIREMENT

Historical binding remains reconstructable with revocation metadata.

## AUDIT REQUIREMENT

Record revoker, reason where supplied, scope, time and affected in-flight operations if known.

## FAILURE BEHAVIOR

No silent reactivation.

## RECOVERY / REASSIGNMENT PATH

A revoked right requires a new binding.

The old record is never reactivated.

---

# 18. HumanAuthorityBinding Effectiveness Predicate

A HumanAuthorityBinding is effective only when all conditions are true:

```text
binding = ACTIVE
target User identity exists
target User has active WorkspaceMembership
scope resolves to same Workspace
authority class is valid
scope has not ceased to exist
no overriding governance denial applies
```

Role labels are not part of this predicate unless the specific authority rule in 04 explicitly requires one.

---

# 19. GOV-008 Facilitator Scope Binding

04 leaves Facilitator scope underdefined.

05 closes the governance mechanism without turning Facilitator into universal authority.

## GOVERNANCE SUBJECT

```text
FacilitatorScopeBinding
```

This is a governance scope record, not a domain object.

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Session.

Challenge creation remains Workspace-scoped under the source-explicit Facilitator role.

Burst control requires Session scope.

## GRANT / CHANGE / REVOKE OPERATION

Grant:

```text
bind active Workspace Facilitator to one Session
```

Change:

```text
revoke old binding + grant new binding
```

Revoke:

```text
mark binding REVOKED
```

## PRECONDITIONS

```text
target User has active WorkspaceMembership
target User has Facilitator role in that Workspace
Session belongs to same Workspace
grantor is governance root
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of role, membership, Session scope and root authority.

## BOUNDARY CHECK

Identity, Workspace, Authority, Audit.

## EFFECTIVE STATE

Facilitator source rights become effective for that Session:

```text
START_BURST
PAUSE_BURST
RESUME_BURST by AC-04 closure
COMPLETE_BURST
```

## IN-FLIGHT CONSEQUENCE

Revocation before commit invalidates pending Facilitator-authorized operations.

Already COMMITTED transitions remain valid.

## DEFAULT-DENY BEHAVIOR

Workspace Facilitator label without Session FacilitatorScopeBinding:

```text
may create Challenge in Workspace
may not control arbitrary Session Burst
```

## PERSISTENCE REQUIREMENT

Scope binding must be reconstructable independently from role assignment.

## AUDIT REQUIREMENT

Record grant/revoke actor, Facilitator User, Session and time.

## FAILURE BEHAVIOR

Uncertain binding:

```text
deny Session-specific Facilitator operation
```

## RECOVERY / REASSIGNMENT PATH

Grant a new Session Facilitator binding to an eligible Facilitator.

---

# 20. Facilitator Scope Result

`GAP-04-005 Facilitator scope binding` is structurally closed by 05 as:

```text
Workspace Facilitator role
-> Workspace-scoped right to create Challenge

Workspace Facilitator role
+
ACTIVE Session FacilitatorScopeBinding
-> source-explicit Burst control rights in that Session
```

This does not grant generic Session Control or Human Decision Rights.

> **Post-baseline prototype narrowing (2026-09-24, F02 WU-02.12):** in the
> current prototype, FacilitatorScopeBinding is not materialized. Burst start
> and manual Burst completion are closed instead by a current Session-scoped
> `SESSION_CONTROL_RIGHT` binding at `SESSION:<session_id>` (human decision
> HD-9, 16 §41 REC-009 / NQ-DEC-037). The closure above is preserved as the
> architecture's broader model and stays OPEN for production
> (16 NQ-GAP-080). The narrowing does not make a Facilitator role, or any
> role, sufficient on its own (`ROLE ≠ AUTHORITY`).

Status:

```text
[ARCHITECTURAL CLOSURE]
```

---

# 21. GOV-009 SessionControlAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding for:

```text
SESSION_CONTROL_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

Either:

```text
Challenge scope for AUTH-DEP-SESS-001 Create Session
```

or:

```text
specific Session scope for subsequent Session control
```

No broader wildcard scope is permitted.

## GRANT / CHANGE / REVOKE OPERATION

Use GOV-005, GOV-006, GOV-007.

## PRECONDITIONS

```text
active member
same Workspace
human subject
scope exists
```

In facilitated mode, assignment to an active Session Facilitator is eligible and expected.

In individual mode, Workspace Owner may grant the binding to themselves.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of active membership and scope.

## BOUNDARY CHECK

Identity, Workspace, Authority, Audit.

## EFFECTIVE STATE

Human may request only the Session operations 04 binds to SESSION_CONTROL_RIGHT.

## IN-FLIGHT CONSEQUENCE

Revocation blocks uncommitted Session-control operations and future phase changes.

## DEFAULT-DENY BEHAVIOR

No active SessionControlAuthority:

```text
Session control request denied
```

## PERSISTENCE REQUIREMENT

Scope-specific binding history.

## AUDIT REQUIREMENT

Grant/revoke and each later authority use traceable.

## FAILURE BEHAVIOR

No fallback to Owner, Facilitator or creator.

## RECOVERY / REASSIGNMENT PATH

Workspace governance root grants a replacement binding.

---

# 22. Individual Inquiry Governance Bootstrap

`GAP-04-003` is structurally closed without creating superuser semantics.

For individual inquiry:

```text
Workspace Owner
may grant themselves
the required scope-bounded HumanAuthorityBindings
```

This includes, where needed:

```text
SESSION_CONTROL_RIGHT
QUESTION_SELECTION_RIGHT
ASSUMPTION_INTERPRETATION_RIGHT
EXPERIMENT_DECISION_RIGHT
DECISION_RIGHT
ACTION_DECISION_RIGHT
```

Each remains a separate binding.

No single generic "individual owner can do everything" permission is introduced.

Status:

```text
[ARCHITECTURAL CLOSURE]
```

---

# 23. GOV-010 QuestionSelectionAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding:

```text
QUESTION_SELECTION_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Session.

## GRANT / CHANGE / REVOKE OPERATION

Use generic binding lifecycle.

## PRECONDITIONS

```text
target human is active member
Session belongs to same Workspace
```

No role label is required.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of human membership and Session scope.

## BOUNDARY CHECK

Identity, Workspace, Authority, Audit.

## EFFECTIVE STATE

Target human may perform authority-bearing QuestionSelection operations in that Session.

## IN-FLIGHT CONSEQUENCE

Revocation before selection commit invalidates pending selection.

Committed historical selection remains valid.

Replacement of primary Question remains governed by unresolved `GAP-03-018`.

## DEFAULT-DENY BEHAVIOR

No binding:

```text
selection denied
```

## PERSISTENCE REQUIREMENT

Binding history and selected scope.

## AUDIT REQUIREMENT

Grantor, selector, Session, time.

## FAILURE BEHAVIOR

No fallback to Facilitator or AI.

## RECOVERY / REASSIGNMENT PATH

Grant binding to another eligible human.

## OPEN POLICY

`GAP-04-001 Collaborative Question Selection Rule` remains OPEN.

05 defines who may hold the right.

It does not define whether collaborative Sessions use:

```text
single selector
multiple selectors
consensus
vote
Facilitator choice
```

---

# 24. GOV-011 AssumptionInterpretationAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding:

```text
ASSUMPTION_INTERPRETATION_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Assumption or an explicitly bounded Challenge scope if later governance chooses repeated interpretation responsibility.

## GRANT / CHANGE / REVOKE OPERATION

Generic binding lifecycle.

## PRECONDITIONS

Active human Workspace membership.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of scope and membership.

## BOUNDARY CHECK

Identity, Workspace, Authority, Evidence, Audit.

## EFFECTIVE STATE

Human may perform the interpretive decision operations defined in 04.

## IN-FLIGHT CONSEQUENCE

Revocation before Assumption classification commit invalidates pending classification authority.

## DEFAULT-DENY BEHAVIOR

No binding:

```text
final Assumption classification denied
```

AI recommendations remain non-authoritative.

## PERSISTENCE REQUIREMENT

Binding history.

## AUDIT REQUIREMENT

Grant/revoke and later classification authority use.

## FAILURE BEHAVIOR

Assumption remains in current 03 state.

## RECOVERY / REASSIGNMENT PATH

Governance root assigns replacement.

## STATUS OF GAP-04-012

The assignment mechanism is now structurally closed:

```text
Workspace governance root explicitly chooses the human holder.
```

The system does not infer the holder from role or authorship.

---

# 25. GOV-012 ExperimentDecisionAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding:

```text
EXPERIMENT_DECISION_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Experiment.

## GRANT / CHANGE / REVOKE OPERATION

Generic binding lifecycle.

## PRECONDITIONS

```text
active human member
Experiment belongs to same Workspace
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of membership and Experiment scope.

## BOUNDARY CHECK

Identity, Workspace, Authority, Evidence, Audit.

## EFFECTIVE STATE

Holder may perform 04 Experiment Decision operations for that Experiment.

## IN-FLIGHT CONSEQUENCE

Revocation invalidates not-yet-committed authorization/start/completion operations.

Experiment domain state does not roll back automatically.

## DEFAULT-DENY BEHAVIOR

No active holder:

```text
Experiment authority operations denied
```

## PERSISTENCE REQUIREMENT

Binding history.

## AUDIT REQUIREMENT

Grantor, holder, Experiment, authority use.

## FAILURE BEHAVIOR

No fallback to Experiment author or AI proposer.

## RECOVERY / REASSIGNMENT PATH

Grant replacement binding.

## STATUS OF GAP-04-010

Assignment mechanism is structurally closed.

Selection of the human holder remains a Workspace governance decision, not a role inference.

---

# 26. GOV-013 DecisionAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding:

```text
DECISION_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Decision.

## GRANT / CHANGE / REVOKE OPERATION

Generic binding lifecycle.

## PRECONDITIONS

```text
active human member
Decision belongs to same Workspace
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of scope and membership.

## BOUNDARY CHECK

Identity, Workspace, Authority, Evidence, Audit.

## EFFECTIVE STATE

Holder may open and finalize the human Decision process defined in 04.

## IN-FLIGHT CONSEQUENCE

Revocation before DECIDED commit blocks finalization.

Already DECIDED historical Decision remains valid if authority was valid at commit.

## DEFAULT-DENY BEHAVIOR

No active DecisionAuthority:

```text
Decision finalization denied
```

## PERSISTENCE REQUIREMENT

Binding history.

## AUDIT REQUIREMENT

Grantor, holder, Decision, time and later authority use.

## FAILURE BEHAVIOR

No fallback to Owner, Facilitator, author or AI.

## RECOVERY / REASSIGNMENT PATH

Grant replacement binding.

## STATUS OF GAP-04-009

Assignment mechanism is structurally closed.

Human selection policy is explicit governance, not inferred role hierarchy.

---

# 27. GOV-014 ActionDecisionAuthority Assignment

## GOVERNANCE SUBJECT

HumanAuthorityBinding:

```text
ACTION_DECISION_RIGHT
```

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

One Session or Challenge, depending the operation contract already defined in 04.

## GRANT / CHANGE / REVOKE OPERATION

Generic binding lifecycle.

## PRECONDITIONS

Active human membership and same Workspace scope.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of scope.

## BOUNDARY CHECK

Identity, Workspace, Authority, Audit.

## EFFECTIVE STATE

Holder may make the human Action decision required before the 03 Session transition into ACTION.

## IN-FLIGHT CONSEQUENCE

Revocation before transition commit invalidates the Action decision authority for that pending transition.

A previously valid Action transition does not roll back automatically.

## DEFAULT-DENY BEHAVIOR

No holder:

```text
Session cannot enter ACTION
```

even if AI recommends action.

## PERSISTENCE REQUIREMENT

Binding history.

## AUDIT REQUIREMENT

Grantor, holder, scope and use.

## FAILURE BEHAVIOR

No AI/System substitute.

## RECOVERY / REASSIGNMENT PATH

Grant replacement binding.

## STATUS OF GAP-04-011

Assignment mechanism structurally closed.

---

# 28. GOV-015 Authority Revocation During In-Flight Operations

This closes the main structural part of `GAP-04-006`.

## GOVERNANCE SUBJECT

Any ACTIVE HumanAuthorityBinding, role-dependent source right or FacilitatorScopeBinding used by an uncommitted consequential operation.

## GOVERNANCE ACTOR

Workspace governance root performing revocation, plus governance enforcement service.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT for revocation.

SYSTEM_DERIVED procedural authority for enforcement.

## TARGET SCOPE

The revoked binding and every pending operation depending on it.

## GRANT / CHANGE / REVOKE OPERATION

Revocation follows GOV-007 or role/facilitator revocation.

## PRECONDITIONS

A pending operation exists or may exist.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of:

```text
binding status
authority-evaluation time
commit status
correlation to pending operation
```

## BOUNDARY CHECK

Authority, State Transition, Audit, Failure, Recovery.

## EFFECTIVE STATE

Rule:

```text
Authority must be valid at consequential commit authorization point.
```

If revoked before commit:

```text
pending operation may not commit
```

If already COMMITTED:

```text
committed state remains legitimate history
```

## IN-FLIGHT CONSEQUENCE

### Not yet committed

```text
re-evaluate authority
deny if revoked
```

### COMMITTED

```text
do not retroactively roll back solely due later revocation
```

### INDETERMINATE

```text
block dependent operations
reconcile under 10
```

### Long-running domain object already in state

Example:

```text
Experiment IN_PROGRESS
```

Revocation does not rewrite Experiment to prior state.

Future operations such as COMPLETE_EXPERIMENT require a new valid authority holder.

## DEFAULT-DENY BEHAVIOR

If commit time versus revocation time cannot be proven:

```text
treat pending/future authority as invalid
block dependent consequential operation
```

## PERSISTENCE REQUIREMENT

Authority evaluation and commit correlation must be reconstructable.

## AUDIT REQUIREMENT

Record revocation, affected pending operations and resulting deny/reassignment outcome.

## FAILURE BEHAVIOR

No stale cached authorization may be trusted after revocation.

## RECOVERY / REASSIGNMENT PATH

Workspace governance root may grant replacement HumanAuthorityBinding.

The replacement does not retroactively authorize a failed operation.

---

# 29. GAP-05-002 Cached Authorization and Commit Recheck

**Status:** `[ARCHITECTURAL CLOSURE REQUIREMENT]`

GOV-015 requires authority validity at commit.

09/05 implementation must prevent:

```text
long-lived cached ALLOW decision
```

from surviving a later revocation.

The exact token/version mechanism is not defined in 05.

Potential mechanisms belong to 09/11.

The semantic requirement is authoritative:

```text
stale authorization cannot commit consequential state
```

---

# 30. GOV-016 Reassignment After Revocation

## GOVERNANCE SUBJECT

A required authority role with no current active holder.

## GOVERNANCE ACTOR

Workspace governance root.

## GOVERNANCE AUTHORITY

WORKSPACE_GOVERNANCE_RIGHT.

## TARGET SCOPE

Blocked operation/object scope.

## GRANT / CHANGE / REVOKE OPERATION

Grant new HumanAuthorityBinding under GOV-005.

## PRECONDITIONS

```text
prior binding revoked/ineffective
new human active member
scope valid
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of missing valid holder and new holder eligibility.

## BOUNDARY CHECK

Workspace, Authority, Audit.

## EFFECTIVE STATE

New holder becomes authoritative prospectively.

## IN-FLIGHT CONSEQUENCE

Previously failed/denied operation must be re-requested or re-evaluated under the new authority.

## DEFAULT-DENY BEHAVIOR

No replacement:

```text
workflow remains blocked at next authority-requiring operation
```

## PERSISTENCE REQUIREMENT

New binding distinct from prior binding.

## AUDIT REQUIREMENT

Link reassignment to prior revocation where relevant.

## FAILURE BEHAVIOR

No automatic fallback holder.

## RECOVERY / REASSIGNMENT PATH

This mechanism is itself the reassignment path.

---

# 31. GOV-017 Method Approval Governance Gate

D8 remains source-level OPEN:

```text
Who owns and approves the inquiry methodology encoded in the system?
```

05 must not resolve the actor locally.

## GOVERNANCE SUBJECT

One versioned InquiryMethod configuration.

## GOVERNANCE ACTOR

```text
OPEN_UNRESOLVED
```

The Method Approval Authority actor is not assigned by 00 through 04.

## GOVERNANCE AUTHORITY

```text
OPEN_UNRESOLVED
```

D8 must be resolved before an authority source exists.

## TARGET SCOPE

Specific method version.

## GRANT / CHANGE / REVOKE OPERATION

Semantically required:

```text
APPROVE_METHOD_VERSION
WITHDRAW_METHOD_VERSION
```

05 does not invent the authority holder.

## PRECONDITIONS

Method configuration is version-identifiable and immutable enough to know what was approved.

Exact version schema belongs to 09.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of exact method version/configuration.

## BOUNDARY CHECK

Methodology, Authority, Audit.

## EFFECTIVE STATE

Until D8 is resolved:

```text
method approval gate = UNSATISFIED
```

for any System-derived authority path that depends on approved methodology.

## IN-FLIGHT CONSEQUENCE

No method-triggered SYSTEM_DERIVED transition may rely on an unapproved or unverifiable method version.

## DEFAULT-DENY BEHAVIOR

Unapproved or approval-authority-unresolved method:

```text
SYSTEM_DERIVED authority disabled
```

Human-authorized paths already permitted by 04 remain available where 03 conditions allow them.

## PERSISTENCE REQUIREMENT

Future approval must bind to exact method version.

## AUDIT REQUIREMENT

Future approval/withdrawal must be attributable to the resolved D8 authority holder.

## FAILURE BEHAVIOR

No implicit approval from deployment, configuration presence or AI use.

## RECOVERY / REASSIGNMENT PATH

Resolve D8 upstream in authoritative decision process, then activate governance mechanism.

---

# 32. GAP-04-008 Preserved

`GAP-04-008 Method approval authority for System-derived transitions` remains:

```text
[OPEN]
```

05 operationalizes the fail-closed gate.

It does not choose the D8 authority holder.

No upstream contradiction exists.

---

# 33. GOV-018 Activate SYSTEM_DERIVED Authority

SYSTEM_DERIVED authority is not granted like a human permission.

It is derived at operation time from approved conditions.

## GOVERNANCE SUBJECT

One operation-specific System authority rule.

Current 04 examples:

```text
QuestionBurst completion by trusted timer
Begin Analysis under approved deterministic method
Begin Reflection under approved deterministic method and valid AI analysis proof
commit execution after successful human authority validation
```

## GOVERNANCE ACTOR

Identified SYSTEM_SERVICE.

## GOVERNANCE AUTHORITY

`SYSTEM_DERIVED` as defined in 04.

## TARGET SCOPE

One specific operation and object scope.

No wildcard System authority.

## GRANT / CHANGE / REVOKE OPERATION

No generic grant.

Authority is active only while its derivation predicate is true.

Governance may enable or disable the underlying approved rule/configuration, but the System service does not receive a reusable human permission.

## PRECONDITIONS

All operation-specific conditions from 03/04, including where applicable:

```text
trusted service identity
approved method version
valid current state
required proof
no unresolved human decision
no boundary denial
```

Timer authority additionally requires resolved:

```text
CONFLICT-007
GAP-03-002
GAP-04-007
```

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of every derivation predicate.

AI output may provide AI_VALIDATION_PROOF where 03 requires it.

AI output is not the authority source.

## BOUNDARY CHECK

Authority, State Transition, Methodology, AI, Audit, Failure.

## EFFECTIVE STATE

System authority exists only for that single evaluated operation instance.

## IN-FLIGHT CONSEQUENCE

If any derivation predicate becomes false before commit:

```text
System authority expires
operation denied
```

## DEFAULT-DENY BEHAVIOR

Missing proof or unresolved gate:

```text
no SYSTEM_DERIVED authority
```

## PERSISTENCE REQUIREMENT

The basis for each System-authorized consequential operation must be reconstructable.

## AUDIT REQUIREMENT

Record:

```text
service identity
operation
scope
derivation rule
method version where applicable
proof references
authority result
```

## FAILURE BEHAVIOR

System service failure does not transfer authority to AI or another service automatically.

## RECOVERY / REASSIGNMENT PATH

Retry only under a currently valid derivation predicate.

Human path may be used only if independently authorized by 04.

---

# 34. AI_PROCESSOR Governance Exclusion

AI_PROCESSOR may never:

```text
grant membership
revoke membership
assign Workspace role
grant HumanAuthorityBinding
change HumanAuthorityBinding
revoke HumanAuthorityBinding
bind Facilitator scope
approve method
activate SYSTEM_DERIVED authority by model judgment
grant export authority
override default deny
```

AI may assist by:

```text
summarizing governance state
identifying missing binding
explaining why operation was denied
preparing non-authoritative governance suggestions
```

Any such output remains derived.

---

# 35. GOV-019 Export Governance Gate

04 leaves `GAP-04-013 Export Authority` OPEN.

05 cannot choose an export decision right without modifying the authoritative 04 authority layer.

Therefore export governance is explicitly fail-closed.

## GOVERNANCE SUBJECT

Export request.

## GOVERNANCE ACTOR

HUMAN_USER.

## GOVERNANCE AUTHORITY

```text
OPEN_UNRESOLVED
```

No Owner, Facilitator or other role receives export authority in 05.

## TARGET SCOPE

Requested Workspace/Challenge/Session data.

## GRANT / CHANGE / REVOKE OPERATION

No export authority grant mechanism is activated until 04/12 resolves the authority class and scope.

## PRECONDITIONS

Future export governance will require at least:

```text
authenticated identity
active Workspace membership
explicit export authority
defined export scope
defined redaction/content policy
```

## EVIDENCE REQUIREMENT

Future SYSTEM_PROOF of authority and export scope.

## BOUNDARY CHECK

Workspace, Authority, Export, Privacy, Audit.

## EFFECTIVE STATE

Current architecture:

```text
export authority unresolved
=> export request denied by governance
```

This does not remove Export from LEVEL 1 MVP scope.

It exposes a baseline blocker.

## IN-FLIGHT CONSEQUENCE

No export generation may begin before authority resolves.

## DEFAULT-DENY BEHAVIOR

Always deny while GAP-04-013 remains open.

## PERSISTENCE REQUIREMENT

No export artifact should be created from an unauthorized request.

## AUDIT REQUIREMENT

Denied export attempts should be auditable where security policy requires.

## FAILURE BEHAVIOR

No partial export.

No fallback to Owner or Facilitator.

## RECOVERY / REASSIGNMENT PATH

Resolve Export Authority in the authoritative authority architecture before prototype freeze.

---

# 36. Export Governance Status

`GAP-04-013 Export Authority` remains:

```text
[OPEN]
```

Because Export is explicitly MVP scope, this is:

```text
baseline-blocking for Minimum Closed Prototype
```

05 does not patch it.

---

# 37. GOV-020 Membership Removal Dependency Cleanup

This mechanism ensures membership revocation cannot leave active authority residue.

## GOVERNANCE SUBJECT

All governance bindings whose subject loses Workspace membership.

## GOVERNANCE ACTOR

Governance enforcement SYSTEM_SERVICE acting under the root-authorized membership revocation.

## GOVERNANCE AUTHORITY

SYSTEM_DERIVED procedural authority.

## TARGET SCOPE

All bindings in the revoked Workspace for that User.

## GRANT / CHANGE / REVOKE OPERATION

Revoke/invalidate:

```text
HumanAuthorityBindings
FacilitatorScopeBindings
role assignments
Session-specific governance bindings
```

No new authority is granted.

## PRECONDITIONS

Root-authorized membership revocation exists.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of revoked membership and dependent-binding inventory.

## BOUNDARY CHECK

Workspace, Authority, Audit, Failure, Recovery.

## EFFECTIVE STATE

No dependent authority remains effective.

## IN-FLIGHT CONSEQUENCE

GOV-015 rules apply.

## DEFAULT-DENY BEHAVIOR

If cleanup completeness cannot be proven:

```text
target User denied consequential operations
```

## PERSISTENCE REQUIREMENT

Cleanup must be reconstructable as one logical governance bundle.

## AUDIT REQUIREMENT

Record all invalidated governance bindings.

## FAILURE BEHAVIOR

Partial cleanup yields fail-closed authority.

## RECOVERY / REASSIGNMENT PATH

Reconcile inventory and revoke remaining active records.

---

# 38. GOV-021 Facilitator Role Removal Dependency Cleanup

## GOVERNANCE SUBJECT

Session FacilitatorScopeBindings for a User whose Workspace Facilitator role is removed.

## GOVERNANCE ACTOR

SYSTEM_SERVICE under root-authorized role change.

## GOVERNANCE AUTHORITY

SYSTEM_DERIVED procedural cleanup authority.

## TARGET SCOPE

Same Workspace.

## GRANT / CHANGE / REVOKE OPERATION

Revoke all FacilitatorScopeBindings dependent on the removed role.

## PRECONDITIONS

Valid Facilitator role removal.

## EVIDENCE REQUIREMENT

SYSTEM_PROOF of prior role and dependent scope bindings.

## BOUNDARY CHECK

Workspace, Authority, Audit.

## EFFECTIVE STATE

Source-explicit Facilitator rights cease in affected Sessions.

Separate HumanAuthorityBindings not dependent on Facilitator role remain unaffected.

Example:

```text
a User may lose Facilitator role
while retaining separately granted QUESTION_SELECTION_RIGHT
```

if governance has not revoked that binding.

## IN-FLIGHT CONSEQUENCE

Pending Facilitator operations re-evaluate and fail.

## DEFAULT-DENY BEHAVIOR

Uncertain cleanup:

```text
Facilitator source rights denied
```

## PERSISTENCE REQUIREMENT

Role and dependent binding change linked.

## AUDIT REQUIREMENT

Record affected Sessions.

## FAILURE BEHAVIOR

No stale Facilitator authority.

## RECOVERY / REASSIGNMENT PATH

Assign another Facilitator role and Session scope binding.

---

# 39. Session Controller Multiplicity

`GAP-04-004` remains:

```text
[UNDERDEFINED]
```

05 can govern any explicit SessionControlAuthority binding.

It does not decide whether a Session should support:

```text
one controller
multiple controllers
controller handoff
```

High-assurance effect:

If multiple active SessionControlAuthority bindings exist and an operation requires unique controller semantics not defined by source:

```text
governance must not infer precedence
```

This remains a design gap for later closure.

---

# 40. Governance of Question Selection Multiplicity

`GAP-04-001` remains OPEN.

05 may store multiple active QUESTION_SELECTION_RIGHT bindings only if later policy defines how conflicting or concurrent selections are resolved.

Until that policy is defined:

```text
governance must not use multiple bindings as proof that conflicting primary selections are legitimate
```

`GAP-03-018 Primary Question replacement` remains preserved.

---

# 41. Governance of Decision Authority Assignment

`GAP-04-009` is partially closed structurally.

05 establishes:

```text
Workspace governance root
-> explicit HumanAuthorityBinding
-> one named human Decision holder per binding scope
```

What LEVEL 1 does not determine is the organizational criterion by which the Workspace Owner chooses that person.

That criterion remains outside current source authority.

No role inference is introduced.

---

# 42. Governance of Experiment Authority Assignment

`GAP-04-010` is partially closed structurally.

Mechanism:

```text
Workspace governance root
-> explicit ExperimentDecisionAuthority binding
```

No role inference.

No AI assignment.

Organizational selection criterion remains human governance discretion.

---

# 43. Governance of Action Decision Authority Assignment

`GAP-04-011` is partially closed structurally.

Mechanism:

```text
Workspace governance root
-> explicit ActionDecisionAuthority binding
```

No role inference.

No AI assignment.

---

# 44. Governance of Assumption Interpretation Authority Assignment

`GAP-04-012` is partially closed structurally.

Mechanism:

```text
Workspace governance root
-> explicit AssumptionInterpretationAuthority binding
```

No role inference.

No AI assignment.

---

# 45. Membership Administration Authority

`GAP-04-014` is structurally closed by:

```text
Workspace governance root
-> grant membership
-> revoke membership
-> assign/change/remove Workspace role
```

Constraints:

```text
cannot silently transfer Owner root
cannot grant human decision rights through role label
cannot create AI membership as human User authority
```

Status:

```text
[ARCHITECTURAL CLOSURE]
```

---

# 46. Authority Revocation During Active Operations

`GAP-04-006` is structurally closed by GOV-015.

Core invariant:

```text
valid when requested
!= valid when committed
```

Authority must remain effective at commit authorization point.

No retroactive rollback of already committed legitimate state.

No stale cached allow.

---

# 47. System Timer Governance

`GAP-04-007` remains:

```text
[UNDERDEFINED]
```

05 requires:

```text
identified trusted timer service
authoritative configured duration
tamper-resistant server-side or equivalent trusted time basis
operation-specific SYSTEM_DERIVED rule
```

Exact trust/clock implementation belongs to 09/11.

No browser/client timer alone grants authority.

---

# 48. Governance and D8 Methodology Ownership

05 does not resolve D8.

Therefore:

```text
method configuration may exist
method configuration may be used manually
method configuration does not automatically grant System-derived transition authority
```

Automatic System transition authority dependent on method approval remains disabled until D8 resolution.

This preserves:

```text
CONFIGURATION != AUTHORITY
```

---

# 49. Governance and D2 AI Autonomy

D2 remains OPEN.

05 allows D2 to affect:

```text
AI proposal frequency
AI initiative in non-authoritative analysis
coach mode behavior
```

D2 may not alter:

```text
HumanAuthorityBinding ownership
human Decision Rights
Workspace governance authority
default-deny authority semantics
```

Even an "Autonomous Researcher" mode cannot become a human decision authority.

---

# 50. Governance and AI Facilitator

`GAP-04-015` remains `[DEFERRED]`.

Future AI Facilitator may perform facilitation behavior.

It may not automatically inherit:

```text
Facilitator role source rights
SessionControlAuthority
QuestionSelectionAuthority
DecisionAuthority
ExperimentDecisionAuthority
ActionDecisionAuthority
```

Any future non-human procedural authority must be explicitly modeled as SYSTEM_DERIVED, not AI authority.

---

# 51. Governance Control Point Before Transition

Every consequential transition from 03 must pass governance before commit.

Governance outcome:

```text
ALLOW
DENY
```

`ALLOW` means:

```text
governance found a legitimate authority path
```

It does not mean:

```text
transition preconditions passed
boundary checks passed
persistence succeeded
state committed
```

03 remains authoritative for those results.

---

# 52. Governance Control Point Before State-Preserving Consequential Mutation

The same governance rules apply to consequential mutations that do not change Session state, including:

```text
Question capture
Question selection
Assumption classification
Experiment authorization
Decision finalization
membership changes
authority binding changes
role changes
```

State-preserving does not mean non-consequential.

---

# 53. Governance Control Point Before AI Invocation

Governance must distinguish:

```text
authority to invoke AI
from
AI authority
```

Where 04/03 allow a System or human to begin analysis:

```text
governance authorizes the operation
AI executes the bounded computation
```

The AI result cannot grant itself another operation.

---

# 54. Governance Persistence Requirements

05 requires persistent governance facts sufficient to reconstruct:

```text
Workspace governance root
membership history
role history
Facilitator scope history
HumanAuthorityBinding grant history
HumanAuthorityBinding revocation history
authority replacement lineage
method approval status when D8 resolves
System-derived authority basis for each consequential System operation
```

Exact schema belongs to 09.

No governance fact may exist only in:

```text
frontend state
prompt text
session memory
undurable cache
```

when it is required to justify consequential authority.

---

# 55. Governance Audit Requirements

Every governance mutation must record enough information to reconstruct:

```text
governance actor
actor identity
governance authority
subject
target scope
prior governance status
requested operation
result
new governance status
authority source
time
correlation ID
reason where required
dependent bindings affected
```

Exact audit event schema belongs to 09.

---

# 56. Governance Failure Outcomes

Governance uses:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

semantically aligned with 03 transition outcomes.

These are governance-operation outcomes.

## DENIED

Governance authority or precondition failed.

No governance change.

## FAILED_PRECOMMIT

Technical failure before durable change.

No governance change.

## COMMITTED

Governance change is effective.

## INDETERMINATE

Governance cannot prove whether the change committed consistently.

High-assurance effect:

```text
choose the less permissive effective interpretation
until recovery proves otherwise
```

Examples:

```text
uncertain grant
=> treat as not granted

uncertain revocation
=> treat as revoked/unavailable for new operations

uncertain role elevation
=> treat as not elevated

uncertain membership grant
=> treat as non-member
```

---

# 57. AC-05-001 Least-Permissive Uncertainty Rule

**[ARCHITECTURAL CLOSURE]**

For governance INDETERMINATE outcomes:

```text
effective authority
=
least permissive interpretation consistent with known facts
```

This rule applies until 10 recovery resolves the committed governance state.

It prevents ambiguous failure from creating authority.

---

# 58. AC-05-002 Governance Change Is Prospective

**[ARCHITECTURAL CLOSURE]**

A governance grant/revocation affects operations according to its committed effective time.

It does not silently rewrite the legitimacy of previously COMMITTED state.

This preserves audit history and 03 executed-state semantics.

---

# 59. AC-05-003 Authority Binding Change Is Revoke Plus Grant

**[ARCHITECTURAL CLOSURE]**

HumanAuthorityBinding semantics are immutable as historical authority facts.

A change does not overwrite:

```text
subject
authority class
scope
source
```

It revokes one binding and creates another.

---

# 60. AC-05-004 Membership Is Authority Precondition, Not Authority

**[ARCHITECTURAL CLOSURE]**

WorkspaceMembership is required for Workspace-scoped authority.

Membership itself does not grant:

```text
SessionControlAuthority
QuestionSelectionAuthority
DecisionAuthority
ExperimentDecisionAuthority
ActionDecisionAuthority
AssumptionInterpretationAuthority
```

---

# 61. AC-05-005 Role Assignment Is Governance Context, Not Generic Permission

**[ARCHITECTURAL CLOSURE]**

Workspace role assignment affects only:

```text
source-explicit role rights
eligibility for later scoped bindings
```

It does not become a generic ACL permission set.

---

# 62. AC-05-006 Facilitator Rights Are Session-Scoped for Burst Control

**[ARCHITECTURAL CLOSURE]**

Workspace Facilitator role plus Session FacilitatorScopeBinding is required for Session-specific Burst control.

Workspace Facilitator role alone does not grant control of all Workspace Sessions.

---

# 63. AC-05-007 HumanAuthorityBinding Cannot Target AI or System

**[ARCHITECTURAL CLOSURE]**

HumanAuthorityBinding subject must be a human User.

AI and System use their own non-human authority architecture.

---

# 64. AC-05-008 Revocation Requires Commit-Time Recheck

**[ARCHITECTURAL CLOSURE]**

A consequential operation may not rely solely on an earlier authority evaluation.

Authority validity must be revalidated at the final authorization point before commit.

---

# 65. AC-05-009 System-Derived Authority Is Ephemeral

**[ARCHITECTURAL CLOSURE]**

SYSTEM_DERIVED authority exists only for the current operation instance while all derivation predicates hold.

It is not a reusable permission token.

---

# 66. AC-05-010 Method Configuration Cannot Self-Approve

**[ARCHITECTURAL CLOSURE]**

Presence of a configured InquiryMethod does not satisfy method approval.

D8 approval authority remains separate.

---

# 67. AC-05-011 Export Remains Fail-Closed Until Authority Is Resolved

**[ARCHITECTURAL CLOSURE]**

Because 04 deliberately leaves Export Authority open, 05 cannot infer it.

Export remains denied until the authoritative authority layer closes the right.

---

# 68. AC-05-012 Dependent Authority Cleanup on Membership Revocation

**[ARCHITECTURAL CLOSURE]**

Membership revocation invalidates and triggers cleanup of every Workspace-dependent authority binding for that human.

---

# 69. AC-05-013 Owner Is Governance Root, Not Runtime Superuser

**[ARCHITECTURAL CLOSURE, preserves AC-04-001/015]**

Owner governance authority is limited to governance administration defined here.

It does not bypass domain operation authority.

---

# 70. AC-05-014 AI Cannot Execute Governance Mutations

**[ARCHITECTURAL CLOSURE]**

AI may advise.

AI may not:

```text
grant
change
revoke
approve
delegate
activate
```

authority.

---

# 71. Open and Carried Governance Gaps

## GAP-04-001 Collaborative Question Selection Rule

**Status:** `[OPEN]`

Preserved.

## GAP-04-002 Workspace Owner Governance Semantics Beyond Authority Binding

**Status:** `[UNDERDEFINED]`

Partially operationalized.

Owner transfer/succession remains open.

## GAP-04-003 Individual Inquiry Authority Bootstrap

**Status:** `[STRUCTURALLY CLOSED BY 05]`

Owner may self-grant separate bindings.

No superuser permission introduced.

## GAP-04-004 Session Control Multiplicity

**Status:** `[UNDERDEFINED]`

Preserved.

## GAP-04-005 Facilitator Scope Binding

**Status:** `[STRUCTURALLY CLOSED BY 05]`

Workspace role + Session scope binding.

## GAP-04-006 Authority Revocation During Active Operation

**Status:** `[STRUCTURALLY CLOSED BY 05]`

Commit-time authority recheck.

## GAP-04-007 System Timer Identity and Trust

**Status:** `[UNDERDEFINED]`

Preserved with stronger governance requirement.

## GAP-04-008 Method Approval Authority

**Status:** `[OPEN]`

Preserved due D8.

## GAP-04-009 Decision Authority Assignment Policy

**Status:** `[STRUCTURALLY CLOSED, HUMAN HOLDER CHOICE REMAINS GOVERNANCE DISCRETION]`

Explicit binding by Workspace governance root.

## GAP-04-010 Experiment Authority Assignment Policy

**Status:** `[STRUCTURALLY CLOSED, HUMAN HOLDER CHOICE REMAINS GOVERNANCE DISCRETION]`

Explicit binding by Workspace governance root.

## GAP-04-011 Action Decision Authority Assignment Policy

**Status:** `[STRUCTURALLY CLOSED, HUMAN HOLDER CHOICE REMAINS GOVERNANCE DISCRETION]`

Explicit binding by Workspace governance root.

## GAP-04-012 Assumption Interpretation Authority Assignment Policy

**Status:** `[STRUCTURALLY CLOSED, HUMAN HOLDER CHOICE REMAINS GOVERNANCE DISCRETION]`

Explicit binding by Workspace governance root.

## GAP-04-013 Export Authority

**Status:** `[OPEN]`

Preserved and fail-closed.

## GAP-04-014 Membership Administration Authority

**Status:** `[STRUCTURALLY CLOSED BY 05]`

Workspace governance root administers membership and role assignments.

## GAP-04-015 AI Facilitator Future Authority

**Status:** `[DEFERRED]`

Preserved.

---

# 72. New Gaps Exposed in 05

## GAP-05-001 Workspace Root Creation and Succession

**Status:** `[UNDERDEFINED]`

Initial Workspace creation authority, owner transfer and succession remain undefined.

## GAP-05-002 Cached Authorization and Commit Recheck Mechanism

**Status:** `[ARCHITECTURAL CLOSURE REQUIREMENT]`

Semantic commit-time recheck is closed.

Implementation mechanism remains for 09/11.

## GAP-05-003 Governance Operation Atomicity

**Status:** `[UNDERDEFINED]`

Logical governance bundles include:

```text
membership revocation + binding invalidation
role removal + facilitator-scope cleanup
binding replacement = revoke + grant
```

09/10 must define atomicity/compensation/reconciliation mechanism.

## GAP-05-004 Governance Record Retention

**Status:** `[UNDERDEFINED]`

Privacy deletion and audit retention may conflict for:

```text
membership history
authority binding history
revocation history
```

11/10 must define retention treatment.

## GAP-05-005 Method Version Identity

**Status:** `[UNDERDEFINED]`

System-derived method authority requires exact approved method version.

09 must define method version identity/configuration persistence.

## GAP-05-006 Governance Reason Requirements

**Status:** `[UNDERDEFINED]`

Source does not define whether:

```text
authority grant
revocation
role change
membership removal
```

must include human-readable rationale.

Audit may require a reason for selected high-risk operations, but 05 does not invent universal rationale requirements.

## GAP-05-007 Governance Concurrency

**Status:** `[UNDERDEFINED]`

Concurrent:

```text
grant/revoke
role changes
membership removal
authority use
```

must not yield contradictory effective authority.

09/10 must define concurrency/version control.

## GAP-05-008 Export Authority Resolution Home

**Status:** `[OPEN UPSTREAM AUTHORITY DEPENDENCY]`

Because 04 is authoritative for authority classes, closing Export Authority later may require a controlled reconstruction of 04 before 05 can activate export governance.

05 does not patch this locally.

---

# 73. Governance Mechanism Coverage Matrix

| Mechanism | Status |
|---|---|
| Workspace governance bootstrap | Structurally defined, root creation/succession gap exposed |
| Membership grant | Closed |
| Membership revoke | Closed |
| Workspace role assignment | Closed |
| Owner transfer | Open |
| HumanAuthorityBinding grant | Closed |
| HumanAuthorityBinding change | Closed as revoke + grant |
| HumanAuthorityBinding revoke | Closed |
| Facilitator scope binding | Closed |
| SessionControlAuthority assignment | Closed |
| QuestionSelectionAuthority assignment | Closed, collaborative policy open |
| AssumptionInterpretationAuthority assignment | Closed |
| ExperimentDecisionAuthority assignment | Closed |
| DecisionAuthority assignment | Closed |
| ActionDecisionAuthority assignment | Closed |
| Revocation during active operations | Closed semantically |
| Authority reassignment | Closed |
| Method approval authority | Open due D8 |
| SYSTEM_DERIVED activation | Closed with fail-closed method/timer dependencies |
| Export governance | Structurally exposed, authority open |
| AI governance mutations | Prohibited |
| Membership-dependent binding cleanup | Closed |
| Facilitator-role cleanup | Closed |

---

# 74. Governance Failure Injection Questions

05 must later be testable against at least these falsification questions:

```text
Can a non-member receive effective Workspace authority?

Can a Viewer execute a consequential operation because the UI exposes it?

Can an Owner execute a Decision without DecisionAuthority?

Can a Facilitator control a Session without Session scope binding?

Can a removed member retain an effective HumanAuthorityBinding?

Can a revoked binding commit an operation from a cached ALLOW?

Can AI grant itself authority?

Can SYSTEM_SERVICE behave as AI decision maker?

Can an unapproved method activate SYSTEM_DERIVED transitions?

Can a client-side timer complete a Burst without trusted System authority?

Can an unresolved export authority fall back to Owner or Facilitator?

Can an indeterminate authority grant be treated as active?

Can revocation retroactively erase a legitimate committed state?

Can role removal leave stale Facilitator scope authority?

Can a binding change overwrite history instead of revoke + grant?
```

Every answer must ultimately be:

```text
No
```

through executable architecture and tests.

---

# 75. Recursive Governance Closure Validation: 00

## RESULT

**PASS**

05 preserves:

```text
Governance Before Consequence
Human Decision Authority
one authoritative home
recursive reconstruction
default-deny consequence
```

No 00 reconstruction required.

---

# 76. Recursive Governance Closure Validation: 01

## RESULT

**PASS**

05 preserves:

```text
Identity != authority
Workspace boundary
Human / AI boundary
Method configuration != runtime authority
Export control requirement
AI context boundary
```

No 01 reconstruction required.

---

# 77. Recursive Governance Closure Validation: 02

## RESULT

**PASS**

05 does not convert governance records into domain objects.

Preserved:

```text
WorkspaceMembership = relation
SessionParticipation = relation
HumanAuthorityBinding = authority construct
FacilitatorScopeBinding = governance scope construct
Audit = event domain later, not state
InquiryMethod = configuration
```

No 02 reconstruction required.

---

# 78. Recursive Governance Closure Validation: 03

## RESULT

**PASS**

05 introduces no new domain/process state or transition.

No Session topology is changed.

No QuestionBurst topology is changed.

No Experiment/Decision/Assumption topology is changed.

Governance revocation changes authority availability, not domain state.

Already committed state is not retroactively rewritten.

No 03 reconstruction required.

---

# 79. Recursive Governance Closure Validation: 04

## RESULT

**PASS**

05 operationalizes exactly the approved 04 model:

```text
Workspace governance root
HumanAuthorityBinding
default deny
scope-bounded authority
no implicit delegation
AI != System
System-derived procedural authority
Owner != superuser
Facilitator != universal decision maker
Participant Question submission right
```

05 does not add a new human decision-right class.

05 does not assign Export Authority locally.

05 does not assign Method Approval Authority locally.

No 04 reconstruction required at this stage.

---

# 80. Upstream Contradiction Check

**RESULT: NO UPSTREAM CONTRADICTION FOUND**

Governance did not require:

```text
new domain object
new domain relation
new Session state
new QuestionBurst state
new Experiment state
new Decision state
new Assumption state
new 03 transition
new 04 human decision-right class
```

to operationalize the approved authority model.

The unresolved cases are represented as:

```text
OPEN
UNDERDEFINED
DEFERRED
```

and fail closed.

Recursive stop condition is not triggered.

---

# 81. Baseline-Blocking Governance Items

The following remain baseline-blocking when their affected capability is inside the Minimum Closed Prototype.

## GOV-BLOCK-001 Export Authority

Export is LEVEL 1 MVP.

`GAP-04-013` remains OPEN.

Therefore export governance is not yet executable.

## GOV-BLOCK-002 Collaborative Question Selection Policy

If collaborative Question Burst is in the Minimum Closed Prototype and more than one human may hold QuestionSelectionAuthority, conflict policy must close.

## GOV-BLOCK-003 Method Approval Authority

If prototype uses automatic SYSTEM_DERIVED progression from configured methods:

```text
D8 must resolve
```

Human-authorized manual phase progression may remain available if 03/04 permit it.

## GOV-BLOCK-004 Workspace Root Bootstrap

A running prototype must have a deterministic first governance root.

`GAP-05-001` must be closed before Workspace provisioning is implementation-ready.

## GOV-BLOCK-005 Timer Trust

If timer automatically completes Burst:

```text
CONFLICT-007
GAP-03-002
GAP-04-007
```

must close.

## GOV-BLOCK-006 Governance Atomicity

Membership/binding revocation and replacement require 09/10 atomicity/reconciliation closure.

---

# 82. Governance Readiness for 06

06 will own executable boundary contracts.

05 now gives 06 governance facts for:

```text
identity requirement
Workspace membership requirement
role assignment semantics
Facilitator scope
HumanAuthorityBinding effectiveness
binding revocation
commit-time authority recheck
System-derived authority
method-approval fail-closed gate
AI governance prohibition
export default deny
```

06 must translate these into boundary:

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

06 must not:

```text
invent Export Authority
invent Method Approval Authority
turn Owner into superuser
grant AI a human authority binding
allow stale authority tokens
override 03 state topology
```

## READINESS RESULT

**READY FOR HUMAN REVIEW**

`05_GOVERNANCE_INSIDE_SYSTEM.md` is structurally ready to become the authoritative Governance Inside System input for `06_BOUNDARY_ARCHITECTURE.md`.

Open governance blockers remain explicit.

06 is not yet authorized.

No downstream architecture file has been built.

No implementation work has begun.

No Architecture Baseline has been frozen.

---

# 83. New Architectural Closures Introduced in 05

| ID | Addition | Status | Reason |
|---|---|---|---|
| AC-05-001 | Least-permissive interpretation for indeterminate governance change | `[ARCHITECTURAL CLOSURE]` | Prevent ambiguous failure from creating authority |
| AC-05-002 | Governance changes are prospective, not retroactive rewrites of committed state | `[ARCHITECTURAL CLOSURE]` | Preserve 03 committed-state legitimacy and audit history |
| AC-05-003 | HumanAuthorityBinding change is revoke plus grant, never in-place semantic overwrite | `[ARCHITECTURAL CLOSURE]` | Preserve authority history |
| AC-05-004 | WorkspaceMembership is authority precondition, not authority | `[ARCHITECTURAL CLOSURE]` | Preserve 02/04 separation |
| AC-05-005 | Workspace role is governance context, not generic permission | `[ARCHITECTURAL CLOSURE]` | Prevent role-to-authority collapse |
| AC-05-006 | Facilitator Burst control requires Session-scoped Facilitator binding | `[ARCHITECTURAL CLOSURE]` | Close GAP-04-005 without Workspace-wide superauthority |
| AC-05-007 | HumanAuthorityBinding cannot target AI_PROCESSOR or SYSTEM_SERVICE | `[ARCHITECTURAL CLOSURE]` | Preserve human decision authority |
| AC-05-008 | Authority must be rechecked at commit after possible revocation | `[ARCHITECTURAL CLOSURE]` | Close stale-authority leak |
| AC-05-009 | SYSTEM_DERIVED authority is operation-instance ephemeral | `[ARCHITECTURAL CLOSURE]` | Prevent reusable System superpermission |
| AC-05-010 | Method configuration cannot self-approve | `[ARCHITECTURAL CLOSURE]` | Preserve D8 and CONFIGURATION != AUTHORITY |
| AC-05-011 | Export remains fail-closed until 04 authority gap is resolved | `[ARCHITECTURAL CLOSURE]` | Prevent Owner/Facilitator authority invention |
| AC-05-012 | Membership revocation invalidates dependent Workspace authority bindings | `[ARCHITECTURAL CLOSURE]` | Prevent stale authority |
| AC-05-013 | Owner is governance root only, never runtime superuser | `[ARCHITECTURAL CLOSURE]` | Preserve AC-04-001/015 |
| AC-05-014 | AI cannot execute governance mutations | `[ARCHITECTURAL CLOSURE]` | Preserve AI != System and human authority |
| AC-05-015 | Individual inquiry bootstraps by separate self-bindings, not a generic superuser permission | `[ARCHITECTURAL CLOSURE]` | Close GAP-04-003 safely |
| AC-05-016 | Facilitator role removal revokes dependent Session Facilitator scope bindings | `[ARCHITECTURAL CLOSURE]` | Prevent stale source-explicit authority |
| AC-05-017 | Human authority reassignment is prospective and requires a new binding | `[ARCHITECTURAL CLOSURE]` | Preserve non-transitive delegation |
| AC-05-018 | Governance operations use the same DENIED/FAILED_PRECOMMIT/COMMITTED/INDETERMINATE outcome discipline as consequential transitions | `[ARCHITECTURAL CLOSURE]` | High-assurance failure semantics |

---

# 84. Stop Gate

**STOP CONDITION REACHED**

Await human review and explicit:

```text
HUMAN_REVIEW::05_APPROVED
GO::BUILD_06_BOUNDARY_ARCHITECTURE
```
