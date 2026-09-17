# 12_MINIMUM_PROTOTYPE_ARCHITECTURE

**Status:** DRAFT FOR HUMAN REVIEW  
**Layer:** 12, Minimum Closed Architectural Prototype  
**Upstream authority:** LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11  
**Downstream authorization:** NONE  
**Implementation authorization:** NONE  
**Architecture freeze:** NOT AUTHORIZED

## Authority statement

This file defines the smallest executable architectural proof of N.Q.U.I.R.Y.

It does not redefine the product MVP.

It does not weaken any approved invariant.

It does not create a prototype superuser, prototype authority, prototype transition, prototype Evidence rule, prototype recovery privilege, or prototype security bypass.

The prototype exists to answer one falsifiable question:

> CAN THE MINIMUM N.Q.U.I.R.Y. INQUIRY FLOW RUN END TO END WITHOUT ANY CONSEQUENTIAL STATE TRANSITION OCCURRING OUTSIDE THE APPROVED AUTHORITY, EVIDENCE, BOUNDARY AND COMMIT MODEL?

The governing rule is:

```text
MINIMUM != WEAKENED

FEATURE MAY BE EXCLUDED
INVARIANT MAY NOT BE EXCLUDED

MINIMUM FEATURE COUNT
!=
MINIMUM ARCHITECTURAL PROOF

PROTOTYPE EXECUTION
!=
PROTOTYPE EXCEPTION
```

The prototype is successful only if both legitimate paths succeed and forbidden paths fail.



# 1. PROTOTYPE QUESTION

The prototype question is binary.

```text
CAN ONE BOUNDED INQUIRY PATH EXECUTE
FROM LEGITIMATE WORKSPACE CONTEXT
THROUGH QUESTION CREATION
THROUGH PROTECTED HUMAN QUESTION BURST
THROUGH POST-BURST AI ANALYSIS
THROUGH EXPLICIT HUMAN QUESTION SELECTION
THROUGH ONE HUMAN-AUTHORITATIVE CONSEQUENCE
THROUGH GOVERNED COMMIT
THROUGH AUDIT / EVENT RECONSTRUCTION
WHILE FAILURE, RECOVERY, SECURITY AND WORKSPACE ISOLATION REMAIN ENFORCEABLE?
```

A working screen is not proof.

A successful API response is not proof.

A database row is not proof.

An AI answer is not proof.

The proof exists only when the occurrence can be reconstructed through the approved architecture and the forbidden alternatives demonstrably fail.

### 1.1 Prototype success condition

PASS requires all mandatory proof claims P-01 through P-25 to pass.

Any mandatory claim failure means:

```text
PROTOTYPE FAIL
```

There is no percentage score and no compensating maturity score.


# 2. PROTOTYPE PRINCIPLE

## 2.1 Minimum Architectural Proof Set

The prototype contains only capabilities needed to falsify the approved architecture.

A capability enters the prototype when at least one of these is true:

1. it proves a mandatory claim P-01 through P-25;
2. it is a legal prerequisite of an included transition;
3. it is required to reconstruct legitimacy;
4. it is required to exercise a mandatory denial or failure path;
5. removing it would force semantic collapse.

A capability remains outside when all of these are true:

1. no mandatory proof depends on it;
2. no included transition legally requires it;
3. its exclusion does not create a bypass;
4. its exclusion does not change an approved invariant.

## 2.2 Product MVP versus architectural prototype

| Dimension | LEVEL 1 MVP PRODUCT REQUIREMENT | 12 MINIMUM ARCHITECTURAL PROTOTYPE |
|---|---|---|
| Purpose | Minimum product behavior | Minimum falsifiable architecture |
| Scope rule | Product capability inclusion | Proof claim inclusion |
| Success | Product behavior exists | Legitimate path succeeds and invalid path fails |
| AI | MVP AI capabilities | Only AIOPs needed to prove bounded AI |
| Export | MVP includes Export | Excluded because Export Authority remains unresolved |
| Timer | MVP includes four-minute timer | UI timer may display, automatic completion excluded while authority/trust semantics remain unresolved |
| Collaboration | Product supports participation | One controlled participant path is sufficient |
| Full lifecycle | Product workflow | Only legal states needed by selected path |
| Research | Product direction | Excluded |
| Enterprise deployment | Product direction | Excluded |

No LEVEL 1 product requirement is deleted by prototype exclusion.

Exclusion means only that the capability is not necessary to prove the architecture in 12.


# 3. REQUIRED PROOF CLAIMS

The following claims are mandatory and binary.

| ID | CLAIM | PROOF TEST | INVALID PATH | REQUIRED RESULT |
|---|---|---|---|---|
| P-01 | Question is a first-class canonical object. | Create and retrieve Question by stable identity. | Store text only as Session field. | Canonical Question exists independently. |
| P-02 | Question.original_text cannot be silently overwritten. | Attempt direct replacement of original_text. | Update original row in place. | Write denied; reframe requires new Question lineage. |
| P-03 | Question Burst preserves frozen human raw set. | Complete HUMAN_ONLY Burst and fingerprint membership. | Append member after completion. | Frozen membership remains unchanged. |
| P-04 | AI cannot contaminate Human-only active Burst. | Invoke AI analysis while Burst ACTIVE. | Provider receives active raw set for analysis. | BND-008/BND-009 denies before provider. |
| P-05 | AI analysis only through approved post-Burst operation. | Complete Burst, then invoke approved AIOP. | Direct model call or pre-freeze analysis. | Only approved post-freeze gateway path runs. |
| P-06 | AI output remains derived/proposal state. | Persist validated analysis result. | Treat output as canonical human decision. | Derived status retained. |
| P-07 | AI cannot directly create human-authoritative state. | AI recommends selection/decision. | AI writes QuestionSelection or Decision.DECIDED. | Authority boundary denies. |
| P-08 | Human QuestionSelection is authority-bearing. | Authorized selector selects Question. | Authenticated non-holder selects. | Only current QUESTION_SELECTION_RIGHT holder commits. |
| P-09 | Recommendation != Decision. | Create AI recommendation then inspect Decision state. | Recommendation automatically finalizes Decision. | Decision remains absent/UNDER_CONSIDERATION until human action. |
| P-10 | Consequential transition requires current authority. | Request included human-authoritative transition. | Remove binding. | No commit without current binding. |
| P-11 | Revoked authority cannot survive to commit. | Prepare Command, revoke binding, then commit attempt. | Use earlier ALLOW. | BND-014 detects revocation and denies. |
| P-12 | Governance is executable state/binding. | Grant explicit bindings and evaluate them. | Use prose policy or role label only. | Binding state is required. |
| P-13 | Boundary DENY prevents consequence. | Trigger authority or Workspace denial. | Continue to persistence anyway. | Canonical state unchanged. |
| P-14 | Evidence/provenance consumed is reconstructable. | Commit Evidence-dependent human Decision. | Omit consumed version/provenance. | Commit rejected or proof incomplete. |
| P-15 | AI confidence cannot become Evidence. | Submit confidence as Evidence substitute. | Treat confidence score as Evidence. | Evidence boundary rejects substitution. |
| P-16 | Command != Event. | Commit one Command and inspect Event. | Submit Event as mutation request. | Event cannot authorize mutation. |
| P-17 | Event replay cannot repeat consequence. | Replay committed Event into projection. | Replay event into command/external action. | Projection rebuild only. |
| P-18 | Direct canonical persistence is not legitimate application path. | Attempt app-principal direct write. | Bypass command processor. | Technical privilege denies normal path; any privileged tamper remains illegitimate and detected. |
| P-19 | Duplicate Command does not duplicate consequence. | Repeat committed command_id/idempotency key. | Create second mutation. | Existing committed result returned. |
| P-20 | INDETERMINATE blocks blind retry and dependent consequence. | Inject uncertain operation outcome. | Retry immediately. | Retry denied; reconciliation required. |
| P-21 | Recovery cannot create authority. | Attempt recovery without current required binding. | Recovery service inherits original actor authority. | BND-018 denies. |
| P-22 | Workspace isolation prevents cross-Workspace protected-data use. | Reference Workspace B Evidence from Workspace A. | Assemble cross-Workspace context. | Denied before AI/context/commit. |
| P-23 | AI Gateway is exclusive provider path. | Attempt provider call from app/worker. | Use provider credential outside gateway. | Credential/network path unavailable. |
| P-24 | Admin/root technical capability is not domain authority. | Use admin identity to finalize Decision. | admin=true or DB owner as authority. | Governed path denies; direct tamper is illegitimate and detectable. |
| P-25 | Consequential occurrence is reconstructable. | Trace actor, authority, state, Evidence, boundaries, commit, audit, event/provenance. | Remove one required proof link. | Occurrence cannot be accepted as fully proven legitimate. |

No claim may be weakened because a baseline blocker is inconvenient.

A blocker either receives a source-consistent prototype closure, is not exercised, is an implementation choice under already approved semantics, is deferred without weakening proof, or blocks the prototype.


# 4. PROTOTYPE SCOPE

## 4.1 Selected bounded inquiry path

The minimum coherent proof path is:

```text
AUTHENTICATED USER
-> WORKSPACE
-> ACTIVE MEMBERSHIP
-> EXPLICIT AUTHORITY BINDINGS
-> CHALLENGE
-> SESSION
-> SETUP
-> CHALLENGE_CAPTURE
-> QUESTION_GENERATION
-> QUESTION BURST PREPARED
-> QUESTION BURST ACTIVE
-> VERBATIM HUMAN QUESTIONS
-> QUESTION BURST COMPLETED
-> FROZEN HUMAN RAW SET
-> SESSION ANALYSIS
-> POST-BURST AI ANALYSIS
-> DERIVED AI ARTIFACT
-> SESSION REFLECTION
-> SESSION QUESTION_SELECTION
-> HUMAN QUESTION SELECTION
-> SESSION INVESTIGATION
-> EVIDENCE ATTACHMENT / VERSIONED CONSUMPTION
-> HUMAN DECISION CONSIDERATION
-> HUMAN DECISION
-> GOVERNED CONSEQUENCE
-> COMMIT UNIT
-> AUDIT
-> EVENT
-> RECONSTRUCTION
```

The selected human-authoritative proof uses `DECISION_RIGHT`.

It does not use Assumption classification beyond UNKNOWN.

It does not require Experiment authorization.

It does not require Action authorization.

It does not require Export.

## 4.2 Why this path is minimum

Question and Burst semantics prove inquiry-first behavior.

Post-Burst AI proves bounded AI.

QuestionSelection proves a domain-specific human authority distinct from Session control.

Decision proves Recommendation != Decision and Human Decision Authority.

Evidence linkage proves reconstructable epistemic dependency without inventing Assumption sufficiency.

Commit/Event/Audit prove operational legitimacy.

Failure and recovery fixtures prove that success semantics survive uncertainty.

Security fixtures prove that technical access cannot replace authority.


# 5. PROTOTYPE EXCLUSIONS

| CAPABILITY | PROTOTYPE STATUS | REASON |
|---|---|---|
| Multi-provider production routing | EXCLUDED | One eligible provider is enough to prove gateway and provenance |
| Provider fallback | EXCLUDED | Not required for P-01 through P-25 |
| Full Research Mode | EXCLUDED | D6 remains open and no proof claim requires it |
| Full collaboration | EXCLUDED | One participant and one selector avoid unresolved collaborative selection semantics |
| Production-scale analytics | EXCLUDED | Metrics are not proof of domain legitimacy |
| Advanced visualization | EXCLUDED | No proof claim requires it |
| Export execution | BLOCKED / EXCLUDED | Export Authority unresolved |
| Production deployment topology | EXCLUDED | Semantic boundaries can be proven in a smaller deployment |
| Complete methodology catalogue | EXCLUDED | One pinned prototype method/configuration is sufficient if it creates no unapproved method authority |
| Automatic method progression | EXCLUDED | Avoids unresolved D8 Method Approval Authority |
| Advanced impact measurement | EXCLUDED | D7 not needed |
| AI Burst modes B/C | EXCLUDED | HUMAN_ONLY proves protected boundary with less ambiguity |
| Consequential AI tools | EXCLUDED | Not needed to prove bounded AI and would activate external idempotency blocker |
| Full enterprise administration | EXCLUDED | No proof claim requires it |
| Full retention automation | EXCLUDED | Retention policy remains unresolved and deletion is not exercised |
| Full incident response automation | EXCLUDED | Security containment and 10 recovery semantics can be tested without full automation |
| Automatic Burst completion timer | EXCLUDED | Timer semantics/trust remain unresolved |
| Assumption SUPPORTED/WEAK/REFUTED classification | EXCLUDED | Sufficiency semantics remain unresolved |
| Experiment execution | EXCLUDED | Decision path proves human authority with smaller surface |
| Action execution | EXCLUDED | Decision path is sufficient |
| Journey materialization | EXCLUDED | No mandatory proof requires it |
| Full Inquiry Graph | EXCLUDED | Projection semantics not required for proof |


# 6. BASELINE BLOCKER RESOLUTION

| BLOCKER / DEPENDENCY | DISPOSITION | PROTOTYPE RULE | SOURCE HOME |
|---|---|---|---|
| Workspace Governance Root / bootstrap | BLOCKS PROTOTYPE | Needs explicit legitimate creation of first Workspace governance root. Seed magic is forbidden. | GAP-05-001 / GAP-09-006 |
| Export Authority | NOT EXERCISED BY PROTOTYPE | Export remains blocked. | GAP-04-013 |
| Commit concurrency / atomicity | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Prototype must use one physical transaction boundary for canonical mutation, required audit and durable outbox where co-located. | AC-09-002 |
| Governance atomicity | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Prototype governance bundle must commit atomically or become least-permissive INDETERMINATE. | 05 / 09 |
| Audit / commit consistency | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Required audit and outbox participate in CommitUnit transaction. | 09 / 10 |
| Direct persistence enforcement | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | 11 closes architecture; prototype needs separate DB capabilities/principals or equivalent enforceable repository capability. | AC-11 direct-write closure |
| AI Gateway enforcement | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Provider credential and egress available only to gateway capability. | AC-11 gateway closure |
| Timer semantics | NOT EXERCISED BY PROTOTYPE | Manual authorized Burst completion only. | GAP-04-007 / CONFLICT-007 |
| Method Approval | NOT EXERCISED BY PROTOTYPE | No automatic method authority or approval transition. | D8 |
| Collaborative QuestionSelection | NOT EXERCISED BY PROTOTYPE | Exactly one active QUESTION_SELECTION_RIGHT holder for prototype Session. | GAP-04-001 |
| Assumption Evidence sufficiency | NOT EXERCISED BY PROTOTYPE | Assumption may exist UNKNOWN only; no classification requiring unresolved threshold. | GAP-07-001 |
| Evidence commit-version mechanism | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Expected Evidence versions and EvidenceSetReference checked at BND-014. | 07 / 09 |
| Deletion / audit tension | DEFERRED WITHOUT WEAKENING PROOF | No deletion workflow exercised. | DEC-A008 / 11 retention gaps |
| Provider/privacy eligibility | MUST CLOSE BEFORE PROTOTYPE | A selected provider can receive only data classes whose eligibility is proven under prototype configuration. | GAP-08-008 / D3 / D4 / D9 |
| Authentication implementation | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | One standards-based identity implementation may be selected later; semantics fixed by 11. | 11 |
| Service identity | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Distinct service identities/capabilities required for governed writer, gateway, worker. | 11 |
| Workspace isolation | IMPLEMENTATION CHOICE WITH APPROVED SEMANTICS | Every protected access carries resolved Workspace scope and rejects mismatch. | 11 |
| External tool idempotency | NOT EXERCISED BY PROTOTYPE | No consequential AI external tool. | GAP-09-001 |
| Recovery discretionary authority | NOT EXERCISED BY HAPPY PATH | Mandatory recovery fixture uses deterministic reconciliation or remains UNRESOLVED unless existing authority applies. | 10 |

## 6.1 Hard blockers before executable proof

Two matters must be closed or concretely proven before the prototype can claim executable architectural success:

1. legitimate first Workspace governance-root bootstrap;
2. provider/privacy eligibility for the exact prototype data class and selected provider path.

12 does not invent either answer.

The prototype architecture is buildable, but final execution acceptance remains blocked until those two dependencies are satisfied.


# 7. AUTHORITY PROFILE FOR PROTOTYPE

The minimum human authority configuration uses distinct approved rights.

| RIGHT | REQUIRED? | USE |
|---|---|---|
| WORKSPACE_GOVERNANCE_RIGHT | YES | Establish/revoke prototype bindings after legitimate bootstrap |
| SESSION_CONTROL_RIGHT | YES | Create/control legal Session and Burst progression where upstream assigns it |
| QUESTION_SELECTION_RIGHT | YES | Create human QuestionSelection |
| ASSUMPTION_INTERPRETATION_RIGHT | NO | Assumption classification beyond UNKNOWN excluded |
| EXPERIMENT_DECISION_RIGHT | NO | Experiment authorization excluded |
| DECISION_RIGHT | YES | Create/finalize included human Decision |
| ACTION_DECISION_RIGHT | NO | Action authorization excluded |

The same human may hold multiple bindings.

The bindings remain separate facts.

```text
ONE HUMAN
+ MULTIPLE BINDINGS
!=
ONE UNIVERSAL RIGHT
```

Prototype roles may aid UI presentation.

They do not replace HumanAuthorityBinding evaluation.

Owner remains governance root semantics only, not universal runtime authority.


# 8. PROTOTYPE GOVERNANCE BOOTSTRAP

## 8.1 Required sequence

```text
BOOTSTRAP REQUEST
-> CREATE WORKSPACE
-> ESTABLISH owner_id GOVERNANCE ROOT
-> ESTABLISH ACTIVE MEMBERSHIP
-> ESTABLISH WORKSPACE_GOVERNANCE_RIGHT
-> GRANT SESSION_CONTROL_RIGHT
-> GRANT QUESTION_SELECTION_RIGHT
-> GRANT DECISION_RIGHT
-> ESTABLISH FacilitatorScopeBinding IF BURST CONTROL PATH REQUIRES IT
-> CREATE CHALLENGE
-> CREATE SESSION
-> ESTABLISH SESSION CONTROL
```

## 8.2 Bootstrap gap

The first Workspace governance root remains an upstream blocker.

12 refuses these shortcuts:

```text
seed_owner = authority
database creator = authority
admin = authority
first login = authority
environment variable = authority
root user = authority
```

Required upstream closure:

A legitimate bootstrap rule must identify who may create the first Workspace and how `owner_id`, initial membership and initial `WORKSPACE_GOVERNANCE_RIGHT` become authoritative facts.

Until closed, bootstrap can be represented in deterministic test fixtures for architecture falsification, but cannot be claimed as a production-legitimate creation path.

Fixture seeding is explicitly labeled TEST PRECONDITION, not runtime authority.


# 9. MINIMUM DOMAIN MODEL

| CONSTRUCT | CLASS | PROTOTYPE PURPOSE |
|---|---|---|
| User | CANONICAL | Human identity reference |
| Workspace | CANONICAL | Scope root |
| WorkspaceMembership | RELATION / GOVERNANCE | Membership |
| HumanAuthorityBinding | GOVERNANCE | Explicit rights |
| FacilitatorScopeBinding | GOVERNANCE | Burst facilitation scope if used |
| Challenge | CANONICAL | Inquiry frame |
| Session | CANONICAL | Workflow state owner |
| SessionParticipation | RELATION | Burst participant relation |
| QuestionBurst | CANONICAL PROCESS OBJECT | Protected capture lifecycle |
| QuestionBurstQuestion | RELATION | Frozen Burst membership |
| Question | CANONICAL | First-class inquiry object |
| QuestionLineage | RELATION | Reframe lineage |
| QuestionSelection | RELATION | Human authority-bearing selection |
| QuestionCluster | DERIVED | Optional post-Burst AI clustering |
| QuestionClusterMembership | RELATION / DERIVED | Optional clustering relation |
| AIGeneration | OPERATIONAL | AI lineage |
| AIContextManifest | OPERATIONAL | Minimum context lineage |
| AI_VALIDATION_PROOF | OPERATIONAL PROOF | AI contract validation |
| Insight or AnalysisArtifact | DERIVED | Validated AI analysis output, only if existing 08 contract maps to it |
| Evidence | CANONICAL | Evidence identity/version |
| SourceReference | PROVENANCE SUPPORT | Source identity |
| ClaimAnchor | SEMANTIC REFERENCE | Exact target/version |
| EvidenceRelation | RELATION | Evidence to claim relation |
| EvidenceSetReference | OPERATIONAL REFERENCE | Exact consumed Evidence set |
| Decision | CANONICAL | Human-authoritative Decision |
| InquiryMethod version reference | CONFIGURATION | Pinned Session configuration only |
| CommandExecutionRecord | OPERATIONAL | Command attempt reconstruction |
| BoundaryEvaluationRecord | OPERATIONAL | Boundary reconstruction |
| AuditEvent | AUDIT | Append-oriented audit |
| OutboxRecord | OPERATIONAL | Durable event delivery basis |
| RecoveryRecord | OPERATIONAL | 10 recovery reconstruction |
| SecurityEvent | SECURITY OPERATIONAL | Security detection, not domain Event |
| Projection | DERIVED | Read model for event replay proof |

Objects not listed are not required merely for table completeness.

Physical co-location is permitted.

Semantic collapse is not.


# 10. MINIMUM STATE MACHINES

The prototype uses real 03 transitions only.

| TRANSITION / MUTATION | ACTOR AUTHORITY | PRECONDITIONS | EVIDENCE / PROOF | BOUNDARIES |
|---|---|---|---|---|
| Session DRAFT -> SETUP | SESSION_CONTROL_RIGHT | Workspace/membership/binding, expected version | SYSTEM_PROOF | BND-001..014 applicable |
| SETUP -> CHALLENGE_CAPTURE | SESSION_CONTROL_RIGHT | Setup legal | SYSTEM_PROOF | BND-014 |
| CHALLENGE_CAPTURE -> QUESTION_GENERATION | SESSION_CONTROL_RIGHT | Challenge captured | SYSTEM_PROOF | BND-014 |
| QuestionBurst PREPARED -> ACTIVE | SESSION_CONTROL_RIGHT plus facilitator scope where applicable | Burst prepared, HUMAN_ONLY mode | SYSTEM_PROOF | BND-008, BND-014 |
| Question capture while ACTIVE | Participant permission under Burst rules | ACTIVE, same Workspace, questions-only | SYSTEM_PROOF | BND-008, BND-014 where canonical mutation commits |
| QuestionBurst ACTIVE/PAUSED -> COMPLETED | Authorized manual controller | No automatic timer dependency | SYSTEM_PROOF | BND-008, BND-014 |
| QUESTION_GENERATION -> ANALYSIS | SESSION_CONTROL_RIGHT | Burst COMPLETED and raw set frozen | SYSTEM_PROOF | BND-009, BND-014 |
| ANALYSIS -> REFLECTION | SESSION_CONTROL_RIGHT | Approved analysis path complete or explicit legal condition from 03 | SYSTEM_PROOF | BND-014 |
| REFLECTION -> QUESTION_SELECTION | SESSION_CONTROL_RIGHT | Reflection phase legal | SYSTEM_PROOF | BND-014 |
| Create QuestionSelection | QUESTION_SELECTION_RIGHT | Current selector binding, candidate Question same Workspace | HUMAN_DECISION style authority fact per 04 | BND-005, BND-006, BND-014 |
| QUESTION_SELECTION -> INVESTIGATION | SESSION_CONTROL_RIGHT | Question selection exists | SYSTEM_PROOF | BND-014 |
| Open Decision consideration | DECISION_RIGHT path per 03/04 | Decision object/target exists | EvidenceSetReference where required | BND-005, BND-006, BND-013, BND-014 |
| Record human Decision | DECISION_RIGHT | Current binding, current Evidence where required | HUMAN_DECISION | BND-005, BND-006, BND-013, BND-014 |

Every consequential row additionally requires:

```text
CURRENT STATE
+ REQUESTED TRANSITION
+ ACTOR
+ CURRENT AUTHORITY
+ PRECONDITIONS
+ REQUIRED EVIDENCE / PROOF
+ BOUNDARY CHECK
+ ALLOWED / DENIED ACTION
+ NEXT STATE
+ PERSISTENCE
+ AUDIT
+ FAILURE
+ RECOVERY
+ TEST
```

No prototype-only state or transition is created.


# 11. QUESTION BURST PROTOTYPE

The prototype uses:

```text
MODE = HUMAN_ONLY
```

Required sequence:

1. create QuestionBurst in PREPARED;
2. persist HUMAN_ONLY mode;
3. authorized controller starts Burst;
4. Burst becomes ACTIVE;
5. authenticated participant submits questions only;
6. each Question receives stable identity, human origin and immutable `original_text`;
7. AI analysis, clustering, evaluation and reframing are denied while ACTIVE;
8. authorized human completes Burst manually;
9. Burst becomes COMPLETED;
10. raw human membership is frozen;
11. frozen membership receives reconstructable identity/fingerprint;
12. only after freeze may approved AI analysis begin.

Automatic four-minute completion is not part of the proof.

A visible timer may exist only as non-authoritative UI information if it cannot trigger completion.

This avoids resolving timer authority/trust accidentally.


# 12. AI PROTOTYPE

## 12.1 Minimum AIOPs

Required:

```text
AIOP-001 QUESTION ANALYSIS
```

Optional only if needed to make the derived artifact visually useful:

```text
AIOP-002 QUESTION CLUSTERING
```

No other AIOP is required for minimum proof.

## 12.2 AI execution chain

```text
COMPLETED BURST
-> FROZEN HUMAN RAW SET
-> AI OPERATION COMMAND
-> AI GATEWAY
-> CONTRACT VERSION CHECK
-> WORKSPACE CHECK
-> AIContextManifest
-> PROVIDER ADAPTER
-> AIGeneration
-> OUTPUT_RECEIVED
-> AI_VALIDATION_PROOF
-> VALIDATED
-> DERIVED ANALYSIS ARTIFACT
```

The derived artifact may inform a human.

It cannot create:

QuestionSelection
Decision.DECIDED
HumanAuthorityBinding
Session transition authority
Evidence sufficiency
Experiment authorization
Action authorization.

## 12.3 Provider rule

One provider is enough for prototype proof only after eligibility for the exact outbound data class is proven.

Provider independence remains an architecture property.

Provider fallback is not required.


# 13. HUMAN DECISION AUTHORITY PROOF

The mandatory proof uses an existing `Decision` and `DECISION_RIGHT`.

Sequence:

```text
AI ANALYSIS / RECOMMENDATION EXISTS
-> AI STOPS AT AUTHORITY BOUNDARY
-> DECISION IS NOT DECIDED
-> AUTHORIZED HUMAN OPENS / HOLDS DECISION CONTEXT
-> HUMAN CONSIDERS CURRENT EVIDENCE
-> HUMAN CREATES THE DECISION
-> SYSTEM RESOLVES CURRENT DECISION_RIGHT
-> BND-005
-> BND-006
-> BND-013 WHERE EVIDENCE REQUIRED
-> BND-014 FRESH REVALIDATION
-> COMMIT UNIT
-> DECISION BECOMES DECIDED
-> AUDIT
-> EVENT
```

Mandatory visible assertion:

```text
THE HUMAN DOES NOT APPROVE THE RECOVERY ENGINE OR AI DECISION.

THE HUMAN CREATES THE DECISION THE AI WAS NEVER AUTHORIZED TO MAKE.
```

For the normal Decision path:

```text
AI RECOMMENDATION
!=
HUMAN CONSIDERATION
!=
HUMAN DECISION
!=
TRANSITION AUTHORIZATION
!=
COMMITTED STATE
```


# 14. EVIDENCE / PROVENANCE PROOF

The prototype exercises one Evidence-consuming Decision path without inventing Assumption sufficiency.

Minimum evidence chain:

```text
SourceReference
-> Evidence identity
-> Evidence version
-> ClaimAnchor to exact target/version
-> EvidenceRelation
-> EvidenceSetReference
-> Decision Command
-> BND-013
-> BND-014 freshness
-> CommitUnit
-> AuditEvent
```

Required demonstrations:

1. Evidence content/version is stable and reconstructable.
2. SourceReference is preserved where applicable.
3. ClaimAnchor references an exact target/version.
4. EvidenceRelation records the exact Evidence and ClaimAnchor versions.
5. EvidenceSetReference fingerprints the exact consumed set.
6. ProvenanceEnvelope preserves origin/transformation.
7. changing or invalidating Evidence after Command preparation invalidates stale commit assumptions.
8. AI confidence is rejected as a substitute for Evidence.
9. historical Decision retains the historical Evidence set it consumed.
10. current recovery or new transition evaluates current required Evidence.

No new Evidence sufficiency threshold is defined in 12.

If the selected Decision operation requires a sufficiency rule not already approved, that exact operation is blocked and the prototype must choose an already source-supported Evidence dependency or expose the blocker.


# 15. GOVERNED COMMAND PROOF

Every consequential mutation enters through a CommandEnvelope.

Minimum fields exercised:

```text
command_id
command_type
contract_version
attempt_id
correlation_id
causation_id
requested_at
actor
workspace_scope
target_refs
expected_versions
authority_context_ref
human_decision_ref where required
evidence_set_ref where required
method_version_ref where applicable
idempotency_key
payload
```

Forbidden client inputs include:

```text
authorized=true
is_owner_therefore_allow=true
evidence_ok=true
decision_approved_by_ai=true
recovery_override=true
skip_boundaries=true
```

No generic state PATCH endpoint is part of the prototype.


# 16. COMMIT PROOF

The prototype uses a single governed CommitUnit transaction for co-located critical records.

Minimum commit proof:

```text
FRESH CANONICAL VERSION
+ FRESH MEMBERSHIP
+ FRESH GOVERNANCE
+ FRESH AUTHORITY
+ FRESH EVIDENCE VERSION WHERE REQUIRED
+ CURRENT METHOD VERSION WHERE APPLICABLE
+ BOUNDARY RESULTS
+ CANONICAL MUTATION
+ REQUIRED AUDIT EVENT
+ DURABLE OUTBOX RECORD
= ONE GOVERNED COMMIT UNIT
```

For the prototype, the required implementation mechanism is:

**one ACID transaction over the co-located canonical, governance, required audit and outbox persistence boundary.**

This is an implementation selection under approved 09 semantics, not a new semantic rule.

Projection persistence is outside the authoritative commit and may update asynchronously.

If the prototype storage technology cannot prove the critical transaction boundary, the prototype fails P-10, P-11, P-16, P-19 and P-25.


# 17. EVENT PROOF

One committed event family is sufficient.

Preferred proof event:

```text
QUESTION_SELECTED
```

or a committed Decision event if that path gives clearer reconstruction.

Required:

```text
COMMAND
-> COMMIT
-> DURABLE OUTBOX
-> EventEnvelope
-> DELIVERY
-> PROJECTION UPDATE
```

Replay test:

```text
EventEnvelope
-> REPLAY CONSUMER
-> PROJECTION REBUILD
```

Forbidden:

```text
EventEnvelope
-> COMMAND AUTHORITY
EventEnvelope
-> EXTERNAL SIDE EFFECT
EventEnvelope
-> HUMAN DECISION
EventEnvelope
-> SECOND DOMAIN COMMIT OF ORIGINAL CONSEQUENCE
```


# 18. IDEMPOTENCY PROOF

### 18.1 Committed duplicate

```text
COMMAND C1
ATTEMPT A1
-> COMMITTED
-> RESULT R1

SAME command_id
SAME idempotency key
SAME payload fingerprint
-> RETURN R1
-> NO SECOND CONSEQUENCE
```

### 18.2 Failed precommit retry

```text
COMMAND C2
ATTEMPT A1
-> FAILED_PRECOMMIT

SAME LOGICAL COMMAND C2
NEW ATTEMPT A2
-> FRESH BOUNDARIES
-> MAY COMMIT
```

### 18.3 Indeterminate

```text
COMMAND C3
ATTEMPT A1
-> INDETERMINATE

BLIND RETRY
-> DENY

RECONCILIATION
-> BND-018
```

A controlled fixture may create uncertainty at the commit/external adapter seam.

It proves architecture behavior under uncertainty, not production external integration reliability.


# 19. FAILURE / RECOVERY PROOF

Two mandatory failure outcomes are exercised.

## 19.1 FAILED_PRECOMMIT fixture

Cause:

expected canonical version is stale before commit.

Required result:

```text
FAILED_PRECOMMIT
canonical mutation = NONE
audit/operational failure correlation = PRESENT
retry eligibility = YES, subject to fresh governed attempt
```

## 19.2 INDETERMINATE fixture

Cause:

controlled fixture makes commit/external consequence certainty unavailable.

Required result:

```text
INDETERMINATE
-> dependent consequence BLOCKED
-> blind retry BLOCKED
-> RecoveryRecord CREATED
-> LAST_PROVEN_VALID_STATE reconstructed
-> reconciliation required
```

## 19.3 Recovery authority

Recovery service receives no inherited human authority.

Deterministic reconciliation may establish what happened.

If a discretionary domain choice is required:

```text
SYSTEM STOPS
-> CURRENT HUMAN AUTHORITY REQUIRED
```

If no approved authority path exists:

```text
UNRESOLVED
```


# 20. SECURITY PROOF

Mandatory security proof set:

| TEST | EXPECTED RESULT |
|---|---|
| Authenticate User A | Identity established, no authority implied |
| Workspace A query for Workspace B protected object | DENY |
| Workspace A Evidence reference in AI context for Workspace B | DENY before provider |
| Application principal direct canonical DB write | Technical denial on normal application capability |
| Projection worker canonical write | Technical denial |
| Direct provider invocation from application/worker | Credential/network capability unavailable |
| Admin attempts Decision mutation | No domain authority, governed path denies |
| Stale authority cache after revocation | BND-014 current check denies |
| Operational log unavailable | Audit record remains separately reconstructable |
| Secret inspection in prompt/trace fixture | Secret absent/redacted |

Technical root access can still alter bytes in many real systems.

Such alteration is not made legitimate by capability.

Prototype proof therefore has two layers:

1. normal service capability cannot bypass;
2. privileged tamper is detectable and cannot produce reconstructable legitimate provenance.


# 21. MINIMUM COMPONENT ARCHITECTURE

The preferred prototype deployment is a **modular monolith plus isolated provider adapter capability**, not a microservice fleet.

Semantic components:

```text
WEB CLIENT
API EDGE
APPLICATION / QUERY MODULE
GOVERNED COMMAND PROCESSOR
GOVERNANCE MODULE
BOUNDARY ENGINE
CANONICAL REPOSITORY
AUDIT / OUTBOX MODULE
PROJECTION MODULE
AI GATEWAY
MODEL PROVIDER ADAPTER
BACKGROUND PROJECTION WORKER
RECOVERY / RECONCILIATION MODULE
SECURITY / IDENTITY ADAPTER
OBSERVABILITY MODULE
```

## 21.1 Semantic boundary versus deployment boundary

A semantic component does not require a separate process.

Prototype deployment may co-locate:

API Edge
Application
Command Processor
Governance
Boundary Engine
Repositories
Audit/Outbox
Recovery

inside one server process.

However, capability interfaces remain explicit and testable.

AI provider credentials are not exposed to general application modules.

Projection worker has no canonical write capability.

The governed writer capability is narrow and only reachable after boundary evaluation.


# 22. MINIMUM DATA STORES

Minimum physical topology:

### Store A: Governed relational persistence

May physically co-locate:

canonical domain records
governance records
CommandExecutionRecord
BoundaryEvaluationRecord
AuditEvent
OutboxRecord
AIGeneration operational records
AIContextManifest
RecoveryRecord

provided semantic typing and privilege boundaries remain explicit.

### Store B: Projection/read model

May be a separate schema/database or an explicitly non-authoritative projection area.

It is rebuildable from authoritative committed sources.

### Secrets

Secrets are outside both application data stores and are injected only into the permitted runtime capability.

### Why two logical stores

The proof requires projection != canonical state.

A separate physical database is optional.

A separate semantic and access capability is mandatory.


# 23. MINIMUM API SURFACE

| OPERATION | TYPE | CALLER | AUTHORITY | COMMAND / CONTRACT | VERSION / EVIDENCE | IDEMPOTENCY |
|---|---|---|---|---|---|---|
| POST /workspaces/{w}/challenges | COMMAND | authenticated member with applicable creation semantics | Workspace | CMD_CREATE_CHALLENGE | none unless upstream requires | idempotent |
| POST /workspaces/{w}/sessions | COMMAND | authorized human | SESSION_CONTROL_RIGHT where upstream requires | CMD_CREATE_SESSION | expected Workspace/Challenge version | idempotent |
| POST /sessions/{s}/transitions/setup | COMMAND | authorized controller | SESSION_CONTROL_RIGHT | CMD_BEGIN_SETUP | expected Session version | idempotent |
| POST /sessions/{s}/transitions/challenge-capture | COMMAND | authorized controller | SESSION_CONTROL_RIGHT | CMD_BEGIN_CHALLENGE_CAPTURE | expected Session version | idempotent |
| POST /sessions/{s}/bursts | COMMAND | authorized controller | SESSION_CONTROL_RIGHT | CMD_PREPARE_BURST | expected Session version | idempotent |
| POST /bursts/{b}/start | COMMAND | authorized controller | SESSION_CONTROL_RIGHT plus applicable facilitator scope | CMD_START_BURST | expected Burst version | idempotent |
| POST /bursts/{b}/questions | COMMAND | authorized participant | Burst participant permission | CMD_CAPTURE_BURST_QUESTION | expected Burst ACTIVE | idempotent |
| POST /bursts/{b}/complete | COMMAND | authorized controller | SESSION_CONTROL_RIGHT plus applicable scope | CMD_COMPLETE_BURST | expected Burst version | idempotent |
| POST /sessions/{s}/ai/question-analysis | COMMAND | approved application/system caller | AIOP contract, no human domain authority implied | AI operation command | frozen Burst fingerprint | idempotent request, new generation on retry |
| POST /sessions/{s}/question-selections | COMMAND | human selector | QUESTION_SELECTION_RIGHT | CMD_SELECT_COMPELLING_QUESTION | expected Session/Question versions | idempotent |
| POST /evidence | COMMAND | authorized Evidence contributor path | existing Evidence operation authority only | Evidence creation/attach command | source/version refs | idempotent |
| POST /decisions/{d}/consider | COMMAND | authorized human | DECISION_RIGHT path | CMD_OPEN_DECISION_CONSIDERATION | expected Decision version | idempotent |
| POST /decisions/{d}/decide | COMMAND | authorized human | DECISION_RIGHT | CMD_RECORD_HUMAN_DECISION | expected Decision and Evidence versions | idempotent |
| GET /sessions/{s} | QUERY | authorized reader | read scope only | QueryEnvelope | none | n/a |
| GET /sessions/{s}/provenance | QUERY | authorized reader | read scope only | QueryEnvelope | none | n/a |
| GET /commands/{c}/reconstruction | QUERY | authorized diagnostic/audit reader | read scope only | QueryEnvelope | none | n/a |
| POST /recoveries/{r}/reconcile | COMMAND | SYSTEM_SERVICE for deterministic reconciliation or current human authority if discretionary | BND-018 | Recovery Command | expected recovery/current versions | idempotent |

Only operations actually exercised by the proof are implemented.

The exact HTTP paths are prototype interface choices.

The semantic Commands are authoritative.

No generic `PATCH state` operation exists.


# 24. MINIMUM UI

Minimum UI surfaces:

1. authenticated Workspace context;
2. Challenge frame;
3. current Session state;
4. Burst state;
5. HUMAN_ONLY mode indicator;
6. verbatim human Question list;
7. frozen raw-set indicator after completion;
8. origin marker HUMAN or AI on relevant artifacts;
9. AI analysis shown explicitly as DERIVED / PROPOSAL;
10. Question selection control only when current authority allows it;
11. Decision boundary showing that AI recommendation is not a Decision;
12. human Decision action for authorized holder;
13. blocked/denied result surface;
14. INDETERMINATE surface that disables blind retry;
15. minimal provenance/audit reconstruction view.

UI does not calculate authority independently.

UI may hide or disable actions for usability.

Backend boundaries remain authoritative.


# 25. PROTOTYPE OBSERVABILITY

Minimum causal chain:

```text
request_id
-> correlation_id
-> command_id
-> attempt_id
-> authority evaluation reference
-> boundary evaluation reference
-> commit_id
-> audit_event_id
-> outbox/event_id
-> generation_id where AI
-> recovery_id where recovery
```

Required reconstruction questions:

```text
WHO REQUESTED?
WHICH WORKSPACE?
WHICH COMMAND?
WHICH ATTEMPT?
WHICH CURRENT AUTHORITY WAS EVALUATED?
WHICH BOUNDARIES PASSED OR DENIED?
WHICH VERSIONS WERE CONSUMED?
DID COMMIT OCCUR?
WHICH AUDIT RECORD EXISTS?
WHICH EVENT WAS EMITTED?
WHICH AI GENERATION CONTRIBUTED?
WHICH RECOVERY RECORD EXISTS?
```

Operational telemetry may aid diagnosis.

It is never substituted for authoritative audit/provenance.


# 26. PROTOTYPE SECURITY TOPOLOGY

Minimum capabilities:

| PRINCIPAL / CAPABILITY | MAY READ CANONICAL | MAY WRITE CANONICAL | PROVIDER CREDENTIAL | PROJECTION WRITE | DOMAIN AUTHORITY |
|---|---|---|---|---|---|
| Browser client | NO direct | NO | NO | NO | NONE from technical capability |
| API/query module | scoped through repository | NO unrestricted | NO | NO | NONE |
| Governed command writer | scoped | YES only inside validated CommitUnit | NO | NO | NONE, executes proven authority |
| Governance module | scoped governance read | via governed Commands only | NO | NO | NONE from service identity |
| AI Gateway | minimum context only | NO | YES | NO | NONE |
| Projection worker | committed event/read basis | NO | NO | YES | NONE |
| Recovery module | scoped reconstruction | only through Recovery Command/CommitUnit | NO by default | optional rebuild | NONE |
| Observability | references/redacted telemetry | NO | NO | NO | NONE |
| Infrastructure admin | technical as operationally required | technical capability may exist | controlled | technical | NONE |

If one process hosts multiple modules, capability objects/repositories are not globally injectable.

The application/query module never receives the canonical write-capable repository.

The provider adapter never exports raw provider credentials to callers.

Tests must attempt forbidden capability acquisition.


# 27. TEST FIXTURES

Required deterministic fixtures:

```text
Workspace A
Workspace B

User Alpha
User Beta

Alpha:
ACTIVE membership in A
SESSION_CONTROL_RIGHT in A
QUESTION_SELECTION_RIGHT in A
DECISION_RIGHT in A

Beta:
ACTIVE membership in A
NO DECISION_RIGHT in A

Binding R1:
ACTIVE then REVOKED during stale-authority test

Command C_DUP:
committed then duplicated

Command C_STALE:
prepared before R1 revocation

AIGeneration G1:
validated recommendation / analysis

Evidence E1 v1
Evidence E1 v2:
version change after Command preparation

Cross-Workspace reference:
Evidence in B referenced from A

Failure F_PRE:
FAILED_PRECOMMIT fixture

Failure F_IND:
INDETERMINATE fixture

Event EV1:
committed event replayed into projection

Recovery RCV1:
reconciliation attempt

Direct write fixture:
application principal attempts canonical write

Gateway bypass fixture:
worker/application attempts direct provider invocation
```

Fixtures are explicitly non-production proof instruments.

No fixture seed grants runtime authority by implication.


# 28. PROTOTYPE HAPPY PATH

Exact proof path:

| STEP | OBJECT / STATE | ACTOR | AUTHORITY | COMMAND | BOUNDARY / PROOF | COMMIT / EVENT / AUDIT |
|---|---|---|---|---|---|---|
| 1 | Workspace A exists legitimately | bootstrap actor | approved bootstrap authority, pending closure | workspace bootstrap command | governance root proof | governance audit |
| 2 | Challenge created | Alpha | applicable scoped right | CMD_CREATE_CHALLENGE | Workspace/membership | CommitUnit, CHALLENGE_CREATED |
| 3 | Session DRAFT | Alpha | SESSION_CONTROL_RIGHT | CMD_CREATE_SESSION | state/version | CommitUnit, SESSION_CREATED |
| 4 | Session -> SETUP | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_SETUP | BND-014 | state event/audit |
| 5 | Session -> CHALLENGE_CAPTURE | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_CHALLENGE_CAPTURE | BND-014 | state event/audit |
| 6 | Session -> QUESTION_GENERATION | Alpha | SESSION_CONTROL_RIGHT | CMD_OPEN_QUESTION_GENERATION | BND-014 | state event/audit |
| 7 | Burst PREPARED | Alpha | SESSION_CONTROL_RIGHT | CMD_PREPARE_BURST | HUMAN_ONLY | commit/audit |
| 8 | Burst ACTIVE | Alpha | SESSION_CONTROL_RIGHT plus scope | CMD_START_BURST | BND-008/BND-014 | QUESTION_BURST_STARTED |
| 9 | Question Q1 captured | Alpha | participant permission | CMD_CAPTURE_BURST_QUESTION | ACTIVE, questions-only | QUESTION_CAPTURED |
| 10 | Question Q2 captured | Beta | participant permission | CMD_CAPTURE_BURST_QUESTION | ACTIVE, same Workspace | QUESTION_CAPTURED |
| 11 | Burst COMPLETED | Alpha | SESSION_CONTROL_RIGHT plus scope | CMD_COMPLETE_BURST | freeze proof | QUESTION_BURST_COMPLETED |
| 12 | raw set frozen | SYSTEM_SERVICE | deterministic system effect | same governed completion | fingerprint/membership proof | audit/outbox |
| 13 | Session -> ANALYSIS | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_ANALYSIS | completed Burst proof | commit/event/audit |
| 14 | AI analysis requested | approved caller | AIOP permission only | AIOP-001 command | BND-009, AI Gateway | AIGeneration REQUESTED |
| 15 | AI output validated | AI Gateway/System | no domain authority | generation lifecycle | AI_VALIDATION_PROOF | AIGeneration VALIDATED |
| 16 | derived analysis persisted | SYSTEM_SERVICE | contract-bounded derived write | AI canonicalization command | BND-010/BND-014 | derived artifact audit |
| 17 | Session -> REFLECTION | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_REFLECTION | 03 preconditions | commit/audit |
| 18 | Session -> QUESTION_SELECTION | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_QUESTION_SELECTION | 03 preconditions | commit/audit |
| 19 | Q1 selected | Alpha | QUESTION_SELECTION_RIGHT | CMD_SELECT_COMPELLING_QUESTION | BND-005/BND-006/BND-014 | QUESTION_SELECTED |
| 20 | Session -> INVESTIGATION | Alpha | SESSION_CONTROL_RIGHT | CMD_BEGIN_INVESTIGATION | selection exists | commit/audit |
| 21 | Evidence E1 v1 attached | authorized path | existing Evidence operation semantics | Evidence command | BND-013 | evidence audit |
| 22 | Decision opened | Alpha | DECISION_RIGHT | CMD_OPEN_DECISION_CONSIDERATION | current Evidence refs | commit/audit |
| 23 | AI recommendation visible | AI derived | NONE | none consequential | proposal only | no Decision commit |
| 24 | Human Decision created | Alpha | DECISION_RIGHT | CMD_RECORD_HUMAN_DECISION | EvidenceSet, BND-005/006/013/014 | Decision commit/event/audit |
| 25 | Reconstruction queried | authorized reader | read scope | QueryEnvelope | correlation chain | actor -> authority -> Evidence -> commit -> audit -> event |

The exact Session progression may include any additional intermediate 03 state that upstream requires before the selected Decision context.

No state may be skipped for convenience.


# 29. PROTOTYPE DENIAL PATH

```text
AI RECOMMENDATION EXISTS
-> Beta AUTHENTICATED
-> Beta HAS UI ACCESS
-> Beta REQUESTS CMD_RECORD_HUMAN_DECISION
-> DECISION_RIGHT LOOKUP
-> NO CURRENT BINDING
-> BND-005 / BND-006 DENY
-> BND-014 NEVER PERMITS COMMIT
-> Decision STATE UNCHANGED
-> ATTEMPT CORRELATED IN AUDIT / OPERATIONAL RECORD AS APPROPRIATE
```

Proof:

```text
RECOMMENDATION != DECISION
IDENTITY != AUTHORITY
UI ACCESS != TRANSITION AUTHORITY
```


# 30. PROTOTYPE STALE-AUTHORITY PATH

Mandatory sequence:

```text
T0 Alpha holds DECISION_RIGHT binding R1
T1 Command C_STALE prepared
T2 early authority evaluation = ALLOW
T3 R1 revoked by legitimate governance Command
T4 C_STALE reaches commit
T5 BND-014 reloads current binding state
T6 R1 = REVOKED
T7 commit = DENIED
T8 canonical Decision unchanged
```

Required assertion:

```text
EARLIER ALLOW
!=
COMMIT AUTHORITY

HISTORICAL AUTHORITY
!=
CURRENT AUTHORITY
```

No stale cache may satisfy T5.


# 31. PROTOTYPE CROSS-WORKSPACE PATH

```text
Alpha authenticated
-> Workspace A context
-> request references Evidence E_B from Workspace B
-> target Workspace resolved
-> Evidence Workspace resolved
-> mismatch
-> Workspace boundary DENY
-> AIContextManifest NOT assembled with E_B
-> provider NOT called with E_B
-> canonical mutation NONE
-> SecurityEvent / audit correlation recorded according to 11
```

The test is repeated for:

1. direct Evidence read;
2. EvidenceRelation creation;
3. AI context assembly.

All must fail before protected data crosses the boundary.


# 32. PROTOTYPE AI-BOUNDARY PATH

```text
Burst COMPLETED
-> AIOP-001
-> AI Gateway
-> AIGeneration G1
-> AI_VALIDATION_PROOF = VALIDATED
-> derived recommendation persisted
-> Decision remains NOT DECIDED
-> no HumanAuthorityBinding created
-> no QuestionSelection created by AI

later:

Alpha with current DECISION_RIGHT
-> human consideration
-> human Decision
-> fresh authority evaluation
-> Evidence freshness
-> BND-014
-> commit
```

This path proves:

```text
AI OUTPUT
!=
HUMAN DECISION

AI_VALIDATION_PROOF
!=
DOMAIN EVIDENCE

AI GATEWAY ACCESS
!=
AUTHORITY
```


# 33. PROTOTYPE RECOVERY PATH

Mandatory controlled sequence:

```text
Command C_IND
-> attempt A1
-> consequence certainty lost
-> outcome INDETERMINATE
-> dependent consequential transition BLOCKED
-> duplicate/blind retry BLOCKED
-> RecoveryRecord RCV1
-> failure-state reconstruction
-> LAST_PROVEN_VALID_STATE identified
-> BND-018
-> deterministic reconciliation
```

Branch A:

```text
PROVEN NOT COMMITTED
-> current authority revalidated
-> new attempt may be permitted
```

Branch B:

```text
PROVEN COMMITTED
-> prior result returned/reconstructed
-> no re-execution
```

Branch C:

```text
still unknown
-> UNRESOLVED
-> blocking preserved
```

If reconciliation reveals a discretionary domain choice:

```text
SYSTEM CANNOT CHOOSE
-> existing current human authority path required
```

RecoveryRecord is never an authority token.


# 34. PROTOTYPE FALSIFICATION MATRIX

| CLAIM | TEST | ATTACK / INVALID PATH | EXPECTED BOUNDARY | EXPECTED RESULT | CAN INVALID CONSEQUENCE OCCUR? | EVIDENCE OF PASS |
|---|---|---|---|---|---|---|
| P-01 | Create and retrieve Question by stable identity. | Store text only as Session field. | Domain repository contract | Canonical Question exists independently. | NO | command/audit/security/provenance fixture |
| P-02 | Attempt direct replacement of original_text. | Update original row in place. | Question immutability / command contract | Write denied; reframe requires new Question lineage. | NO | command/audit/security/provenance fixture |
| P-03 | Complete HUMAN_ONLY Burst and fingerprint membership. | Append member after completion. | BND-008 + CommitUnit | Frozen membership remains unchanged. | NO | command/audit/security/provenance fixture |
| P-04 | Invoke AI analysis while Burst ACTIVE. | Provider receives active raw set for analysis. | BND-008/BND-009 | BND-008/BND-009 denies before provider. | NO | command/audit/security/provenance fixture |
| P-05 | Complete Burst, then invoke approved AIOP. | Direct model call or pre-freeze analysis. | BND-009 + AI Gateway | Only approved post-freeze gateway path runs. | NO | command/audit/security/provenance fixture |
| P-06 | Persist validated analysis result. | Treat output as canonical human decision. | BND-010 | Derived status retained. | NO | command/audit/security/provenance fixture |
| P-07 | AI recommends selection/decision. | AI writes QuestionSelection or Decision.DECIDED. | BND-005/BND-006/BND-010 | Authority boundary denies. | NO | command/audit/security/provenance fixture |
| P-08 | Authorized selector selects Question. | Authenticated non-holder selects. | BND-005/BND-006/BND-014 | Only current QUESTION_SELECTION_RIGHT holder commits. | NO | command/audit/security/provenance fixture |
| P-09 | Create AI recommendation then inspect Decision state. | Recommendation automatically finalizes Decision. | BND-006 | Decision remains absent/UNDER_CONSIDERATION until human action. | NO | command/audit/security/provenance fixture |
| P-10 | Request included human-authoritative transition. | Remove binding. | BND-005/BND-014 | No commit without current binding. | NO | command/audit/security/provenance fixture |
| P-11 | Prepare Command, revoke binding, then commit attempt. | Use earlier ALLOW. | BND-014 | BND-014 detects revocation and denies. | NO | command/audit/security/provenance fixture |
| P-12 | Grant explicit bindings and evaluate them. | Use prose policy or role label only. | BND-004/BND-005 | Binding state is required. | NO | command/audit/security/provenance fixture |
| P-13 | Trigger authority or Workspace denial. | Continue to persistence anyway. | Applicable DENY boundary | Canonical state unchanged. | NO | command/audit/security/provenance fixture |
| P-14 | Commit Evidence-dependent human Decision. | Omit consumed version/provenance. | BND-013/BND-014 | Commit rejected or proof incomplete. | NO | command/audit/security/provenance fixture |
| P-15 | Submit confidence as Evidence substitute. | Treat confidence score as Evidence. | BND-013 | Evidence boundary rejects substitution. | NO | command/audit/security/provenance fixture |
| P-16 | Commit one Command and inspect Event. | Submit Event as mutation request. | Commit/Event contract | Event cannot authorize mutation. | NO | command/audit/security/provenance fixture |
| P-17 | Replay committed Event into projection. | Replay event into command/external action. | Replay side-effect boundary | Projection rebuild only. | NO | command/audit/security/provenance fixture |
| P-18 | Attempt app-principal direct write. | Bypass command processor. | 11 canonical write capability | Technical privilege denies normal path; any privileged tamper remains illegitimate and detected. | NO | command/audit/security/provenance fixture |
| P-19 | Repeat committed command_id/idempotency key. | Create second mutation. | IdempotencyRecord | Existing committed result returned. | NO | command/audit/security/provenance fixture |
| P-20 | Inject uncertain operation outcome. | Retry immediately. | BND-017/BND-018 | Retry denied; reconciliation required. | NO | command/audit/security/provenance fixture |
| P-21 | Attempt recovery without current required binding. | Recovery service inherits original actor authority. | BND-018 + current authority | BND-018 denies. | NO | command/audit/security/provenance fixture |
| P-22 | Reference Workspace B Evidence from Workspace A. | Assemble cross-Workspace context. | Workspace boundary | Denied before AI/context/commit. | NO | command/audit/security/provenance fixture |
| P-23 | Attempt provider call from app/worker. | Use provider credential outside gateway. | 11 AI Gateway enforcement | Credential/network path unavailable. | NO | command/audit/security/provenance fixture |
| P-24 | Use admin identity to finalize Decision. | admin=true or DB owner as authority. | BND-005/BND-014 + tamper detection | Governed path denies; direct tamper is illegitimate and detectable. | NO | command/audit/security/provenance fixture |
| P-25 | Trace actor, authority, state, Evidence, boundaries, commit, audit, event/provenance. | Remove one required proof link. | Traceability chain | Occurrence cannot be accepted as fully proven legitimate. | NO | command/audit/security/provenance fixture |

Any row producing `YES` in the invalid-consequence column fails 12 and the executable prototype.


# 35. PROTOTYPE ACCEPTANCE CRITERIA

Binary only.

| ID | PASS CONDITION | FAILURE |
|---|---|---|
| AC-12-001 | PASS if Unauthorized Decision transition cannot commit. | FAIL otherwise |
| AC-12-002 | PASS if Revoked authority cannot survive BND-014. | FAIL otherwise |
| AC-12-003 | PASS if Duplicate committed Command cannot create duplicate consequence. | FAIL otherwise |
| AC-12-004 | PASS if Cross-Workspace Evidence cannot enter AI context. | FAIL otherwise |
| AC-12-005 | PASS if Direct provider path is unavailable outside AI Gateway. | FAIL otherwise |
| AC-12-006 | PASS if Event replay cannot trigger original domain consequence. | FAIL otherwise |
| AC-12-007 | PASS if INDETERMINATE cannot blind retry. | FAIL otherwise |
| AC-12-008 | PASS if AI output cannot become human-authoritative state. | FAIL otherwise |
| AC-12-009 | PASS if Question.original_text cannot be overwritten in place. | FAIL otherwise |
| AC-12-010 | PASS if Completed HUMAN_ONLY Burst membership cannot be silently changed. | FAIL otherwise |
| AC-12-011 | PASS if AI analysis cannot run against active HUMAN_ONLY Burst through approved path. | FAIL otherwise |
| AC-12-012 | PASS if Canonical mutation can be reconstructed to actor, current authority, boundaries and commit. | FAIL otherwise |
| AC-12-013 | PASS if Evidence-dependent Decision can be reconstructed to exact Evidence versions. | FAIL otherwise |
| AC-12-014 | PASS if AI confidence cannot satisfy Evidence requirement. | FAIL otherwise |
| AC-12-015 | PASS if Application principal cannot perform normal direct canonical write. | FAIL otherwise |
| AC-12-016 | PASS if Projection worker cannot mutate canonical state. | FAIL otherwise |
| AC-12-017 | PASS if Admin identity alone cannot finalize Decision. | FAIL otherwise |
| AC-12-018 | PASS if FAILED_PRECOMMIT produces no canonical consequence. | FAIL otherwise |
| AC-12-019 | PASS if Recovery service cannot inherit original human authority. | FAIL otherwise |
| AC-12-020 | PASS if LAST_PROVEN_VALID_STATE can be reconstructed for mandatory recovery fixture. | FAIL otherwise |
| AC-12-021 | PASS if Required audit and durable outbox are atomic with included consequential commit. | FAIL otherwise |
| AC-12-022 | PASS if Provider credential is unavailable to browser, application and worker paths. | FAIL otherwise |
| AC-12-023 | PASS if Operational log loss does not erase required audit reconstruction. | FAIL otherwise |
| AC-12-024 | PASS if Workspace mismatch is denied before protected data disclosure. | FAIL otherwise |
| AC-12-025 | PASS if All P-01 through P-25 pass. | FAIL otherwise |

No weighted average is permitted.

No maturity percentage is permitted.

Any mandatory invariant failure means:

```text
PROTOTYPE FAIL
```


# 36. DEFERRED FEATURES

| FEATURE | WHY NOT REQUIRED | UPSTREAM STATUS | DEPENDENCY | TARGET |
|---|---|---|---|---|
| Export | Not needed for proof and authority unresolved | LEVEL 1 MVP / GAP-04-013 | Export Authority | post-authority closure |
| Automatic four-minute completion | Manual completion proves Burst boundary without timer authority | LEVEL 1 / CONFLICT-007 | timer trust/duration | later prototype/product increment |
| Research Mode | No P claim depends on it | D6 open | research identity/provider policy | later |
| Multi-provider routing/fallback | One eligible provider proves gateway | 08 | provider compatibility/privacy | later |
| Consequential AI tools | No proof claim requires external tool consequence | 08/09 | tool idempotency/reconciliation | later |
| Assumption classification beyond UNKNOWN | Would activate unresolved sufficiency | 03/07 | GAP-07-001 | later |
| Experiment lifecycle | Decision path is smaller authority proof | 03/04 | none for core proof | later |
| Action lifecycle | Decision path sufficient | 03/04 | ACTION_DECISION_RIGHT | later |
| Collaborative QuestionSelection | Single selector avoids unresolved conflict semantics | GAP-04-001 | selection conflict policy | later |
| Method approval automation | Pinned non-authoritative config is enough | D8 | method approval authority | later |
| Deletion workflows | Not needed for proof | DEC-A008 / 11 | retention/privacy policy | 11+ policy layer |
| Journey | No proof claim depends on materialization | GAP-02-007/008, GAP-09-011 | representation | later |
| Full Inquiry Graph | Projection not required for minimum proof | DEC-A001 | graph scope | later |
| Production observability stack | IDs and reconstruction sufficient | 11 | implementation selection | 14/15 |
| Production incident response | Recovery/security invariants can be fixture-tested | 10/11 | operational policy | later |

Deferred means intentionally outside this proof, not removed from architecture.


# 37. IMPLEMENTATION BOUNDARY

12 defines enough technical structure to make the prototype unambiguous.

12 does not define:

full implementation sequence
coding task order
repository scaffolding
framework-specific classes
migration files
application code
complete test implementation
AI coding prompts
deployment automation

Those remain downstream.

13 owns Test and Falsification Architecture.

14 owns Implementation Sequence.

15 owns AI Coding Prompts.

No code is authorized by 12 approval alone.


# 38. RECURSIVE VALIDATION

| UPSTREAM | RESULT | VALIDATION |
|---|---|---|
| 00 MASTER | PASS | Questions remain first-class; inquiry-first path preserved; LEVEL 1 MVP distinguished from prototype proof. |
| 01 SYSTEM BOUNDARY + PRINCIPLES | PASS | Product, Workspace, authority, AI, provider and audit boundaries preserved. |
| 02 DOMAIN + RELATION | PASS | No new domain Thing; semantic classes remain distinct. |
| 03 STATE + TRANSITION | PASS | Only approved states/transitions used; no prototype transition invented. |
| 04 AUTHORITY + DECISION RIGHTS | PASS | Existing rights only; Owner/Admin not universal authority. |
| 05 GOVERNANCE INSIDE SYSTEM | PASS WITH CARRIED BOOTSTRAP BLOCKER | Explicit bindings required; first governance-root creation remains unresolved. |
| 06 BOUNDARY | PASS | DENY terminal; BND-014 fresh commit revalidation; BND-018 recovery. |
| 07 EVIDENCE + PROVENANCE | PASS | Exact versions and provenance preserved; confidence not Evidence; no new sufficiency rule. |
| 08 AI ARCHITECTURE + CONTRACTS | PASS | AIOP-001 through gateway; derived output; no AI authority. |
| 09 DATA EVENT API CONTRACTS | PASS | Command/Event separation, CommitUnit, idempotency, outbox, replay restrictions preserved. |
| 10 FAILURE RECOVERY ROLLBACK | PASS | FAILED_PRECOMMIT and INDETERMINATE exercised; recovery creates no legitimacy. |
| 11 SECURITY PRIVACY OBSERVABILITY | PASS WITH PROVIDER ELIGIBILITY DEPENDENCY | Workspace isolation, direct-write restriction, gateway exclusivity and audit/log separation preserved. |

## 38.1 Non-collapse checks

```text
MINIMUM != SEMANTIC COLLAPSE                 PASS
PROTOTYPE USER != SUPERUSER                  PASS
OWNER != ALL AUTHORITY                       PASS
AI != DECISION MAKER                         PASS
DATABASE != AUTHORITY                        PASS
EVENT != COMMAND                             PASS
RECOVERY != BYPASS                           PASS
SECURITY != DOMAIN GOVERNANCE                PASS
WORKSPACE != OPTIONAL FILTER                 PASS
EVIDENCE != CONFIDENCE                       PASS
PROJECTION != CANONICAL STATE                PASS
```

## 38.2 Upstream contradiction result

No new upstream contradiction was found.

Two carried dependencies remain blocking for a claim of fully legitimate executable prototype:

1. first Workspace governance-root bootstrap;
2. provider/privacy eligibility for the exact selected provider/data class.

Neither is silently closed in 12.


# 39. COMPLETION REPORT

## 39.1 PROTOTYPE ARCHITECTURAL VERDICT

**CONDITIONALLY READY FOR TEST ARCHITECTURE.**

12 defines a minimum coherent architectural proof without weakening 00 through 11.

The prototype can be specified and tested.

A claim of fully legitimate executable end-to-end operation remains conditional on closure of the Workspace bootstrap authority path and proof of provider/privacy eligibility for the exact selected model/data path.

## 39.2 MINIMUM PROOF SET

Mandatory:

P-01 through P-25.

Core positive chain:

```text
Workspace
-> Challenge
-> Session
-> HUMAN_ONLY Question Burst
-> frozen human raw Questions
-> post-Burst AIOP-001
-> derived AI analysis
-> human QuestionSelection
-> Evidence version linkage
-> human Decision
-> BND-014
-> CommitUnit
-> Audit
-> Event
-> reconstruction
```

Core negative chain:

```text
unauthorized Decision
stale authority
cross-Workspace reference
AI authority attempt
direct DB write
AI Gateway bypass
duplicate Command
Event replay
FAILED_PRECOMMIT
INDETERMINATE blind retry
recovery without authority
```

## 39.3 INCLUDED CAPABILITIES

Authentication, Workspace scope, explicit governance bindings, Challenge, Session subset, HUMAN_ONLY Burst, Question capture, immutable original text, post-Burst AI analysis, derived AI artifact, human QuestionSelection, one Evidence path, one human Decision path, governed Commands, CommitUnit, Audit/Outbox, Event, projection replay, idempotency, FAILED_PRECOMMIT, INDETERMINATE, RecoveryRecord, BND-018, service identity, Workspace isolation, canonical-write restriction, AI Gateway exclusivity, minimal observability.

## 39.4 EXCLUDED CAPABILITIES

Export execution, automatic Burst timer completion, full Research Mode, multi-provider routing/fallback, consequential AI tools, full collaboration, Assumption classification beyond UNKNOWN, Experiment execution, Action execution, Journey materialization, full Inquiry Graph, full retention/deletion automation, production incident-response automation, production-scale analytics.

## 39.5 PROOF CLAIMS P-01 THROUGH P-25

All 25 are retained as mandatory binary claims.

None is waived.

## 39.6 BASELINE BLOCKER DISPOSITION

Hard pre-execution blockers:

1. Workspace governance-root bootstrap;
2. provider/privacy eligibility for real provider disclosure.

Other blockers are either not exercised, deferred without weakening proof, or implementation choices under approved semantics.

## 39.7 AUTHORITY PROFILE

Required rights:

WORKSPACE_GOVERNANCE_RIGHT  
SESSION_CONTROL_RIGHT  
QUESTION_SELECTION_RIGHT  
DECISION_RIGHT

No prototype super-right exists.

## 39.8 GOVERNANCE BOOTSTRAP

Required sequence is defined.

First legitimate governance-root creation remains GAP-12-001.

## 39.9 MINIMUM DOMAIN MODEL

Defined in Section 9.

No new domain Thing introduced.

## 39.10 MINIMUM STATE / TRANSITION SET

Uses only 03 states and transitions.

No prototype transition exists.

## 39.11 MINIMUM AI OPERATIONS

Required: AIOP-001.

Optional: AIOP-002.

All provider access through AI Gateway.

## 39.12 MINIMUM EVIDENCE PATH

SourceReference -> Evidence/version -> ClaimAnchor -> EvidenceRelation -> EvidenceSetReference -> Decision Command -> BND-013/BND-014 -> CommitUnit.

No new sufficiency rule.

## 39.13 MINIMUM COMMAND / EVENT PATH

CommandEnvelope -> fresh boundaries -> CommitUnit -> AuditEvent + durable outbox -> EventEnvelope -> projection.

Command != Event.

## 39.14 MINIMUM FAILURE / RECOVERY PATH

FAILED_PRECOMMIT fixture plus INDETERMINATE fixture.

INDETERMINATE blocks retry and dependent consequence.

RecoveryRecord + LAST_PROVEN_VALID_STATE + BND-018 required.

## 39.15 MINIMUM SECURITY TOPOLOGY

Client has no DB access.

Application/query module has no unrestricted canonical write.

Governed writer has narrow CommitUnit capability.

AI Gateway owns provider credential path.

Projection worker cannot write canonical domain state.

Observability cannot mutate domain state.

Admin technical capability is not domain authority.

## 39.16 MINIMUM COMPONENT ARCHITECTURE

Modular monolith is preferred for proof efficiency.

Semantic boundaries remain explicit and falsifiable.

## 39.17 MINIMUM DATA TOPOLOGY

One governed relational persistence boundary plus one logical projection boundary is sufficient.

Secrets remain outside application data.

## 39.18 MINIMUM API SURFACE

Semantic Command and Query operations only.

No generic state PATCH.

## 39.19 MINIMUM UI SURFACE

UI exposes Session/Burst state, origin, frozen raw set, AI derived status, human authority boundary, blocked/failure state and reconstruction.

## 39.20 TEST FIXTURES

All mandatory fixtures from Section 27 are defined.

## 39.21 HAPPY PATH

Defined in Section 28.

## 39.22 DENIAL PATH

Defined in Section 29.

## 39.23 STALE-AUTHORITY PATH

Defined in Section 30 and mandatory.

## 39.24 CROSS-WORKSPACE PATH

Defined in Section 31 and mandatory.

## 39.25 AI-BOUNDARY PATH

Defined in Section 32 and mandatory.

## 39.26 RECOVERY PATH

Defined in Section 33 and mandatory.

## 39.27 FALSIFICATION MATRIX

P-01 through P-25 mapped to invalid paths and expected boundaries in Section 34.

## 39.28 BINARY ACCEPTANCE CRITERIA

Defined in Section 35.

No percentages.

## 39.29 NEW ARCHITECTURAL CLOSURES

| ID | STATUS | CLOSURE |
|---|---|---|
| AC-12-001 | [ARCHITECTURAL CLOSURE] | Minimum Architectural Proof Set is defined by falsifiable claims, not feature count. |
| AC-12-002 | [ARCHITECTURAL CLOSURE] | Prototype selects one bounded HUMAN_ONLY Burst path. |
| AC-12-003 | [ARCHITECTURAL CLOSURE] | Automatic timer completion is excluded; authorized manual completion avoids unresolved timer authority. |
| AC-12-004 | [ARCHITECTURAL CLOSURE] | Single active QUESTION_SELECTION_RIGHT holder is used, avoiding collaborative selection ambiguity. |
| AC-12-005 | [ARCHITECTURAL CLOSURE] | DECISION_RIGHT path is the mandatory human-authority proof; Experiment and Action authority are not required. |
| AC-12-006 | [ARCHITECTURAL CLOSURE] | Assumption may remain UNKNOWN; unresolved sufficiency classification is not exercised. |
| AC-12-007 | [ARCHITECTURAL CLOSURE] | AIOP-001 is the minimum required AI operation; AIOP-002 is optional. |
| AC-12-008 | [ARCHITECTURAL CLOSURE] | One eligible provider is sufficient; gateway exclusivity and provider independence remain. |
| AC-12-009 | [ARCHITECTURAL CLOSURE] | Prototype CommitUnit uses one ACID transaction for co-located canonical, governance, required audit and durable outbox records. |
| AC-12-010 | [ARCHITECTURAL CLOSURE] | Projection remains outside canonical authority and is rebuildable. |
| AC-12-011 | [ARCHITECTURAL CLOSURE] | Preferred deployment is modular monolith with enforceable semantic capabilities, not mandatory microservices. |
| AC-12-012 | [ARCHITECTURAL CLOSURE] | Application/query capability does not receive unrestricted canonical write capability. |
| AC-12-013 | [ARCHITECTURAL CLOSURE] | Provider credential exists only on AI Gateway/provider adapter path. |
| AC-12-014 | [ARCHITECTURAL CLOSURE] | Mandatory Evidence proof uses exact Evidence versions and EvidenceSetReference without inventing new sufficiency threshold. |
| AC-12-015 | [ARCHITECTURAL CLOSURE] | Mandatory failure proof exercises FAILED_PRECOMMIT and INDETERMINATE through deterministic fixtures. |
| AC-12-016 | [ARCHITECTURAL CLOSURE] | Mandatory recovery proof uses RecoveryRecord and BND-018; recovery service has no inherited human authority. |
| AC-12-017 | [ARCHITECTURAL CLOSURE] | Minimum UI must expose human/AI origin, authority boundary, frozen Burst, blocked state and reconstruction. |
| AC-12-018 | [ARCHITECTURAL CLOSURE] | P-01 through P-25 are binary prototype acceptance claims. |
| AC-12-019 | [ARCHITECTURAL CLOSURE] | Event replay proof is projection-only and cannot re-execute original consequence. |
| AC-12-020 | [ARCHITECTURAL CLOSURE] | Physical co-location of semantic records is permitted only where semantic typing and capability separation remain enforceable. |

## 39.30 NEW GAPS

| ID | GAP | EFFECT | HOME |
|---|---|---|---|
| GAP-12-001 | Workspace bootstrap executable authority | First legitimate Workspace governance-root creation remains unresolved. | 05/09 |
| GAP-12-002 | Prototype provider eligibility | Exact provider/data-class privacy eligibility must be established before real model data leaves boundary. | 08/11 |
| GAP-12-003 | Decision Evidence requirement selection | Exact selected Decision use case must use only an already approved Evidence dependency; if none is source-defined, prototype Evidence consequence needs upstream closure. | 03/07 |
| GAP-12-004 | Prototype authentication mechanism | Vendor/mechanism not selected; semantics fixed by 11. | 11 -> implementation |
| GAP-12-005 | Prototype service identity mechanism | Concrete mechanism not selected; semantics fixed by 11. | 11 -> implementation |
| GAP-12-006 | Physical capability enforcement mechanism | Exact DB roles/repository capability mechanism remains implementation selection. | 11 -> 14/15 |
| GAP-12-007 | Provider egress enforcement mechanism | Exact network/runtime enforcement remains implementation selection. | 11 -> 14/15 |
| GAP-12-008 | Derived AI artifact physical type | Prototype must map AIOP-001 output to an approved 08/09 derived representation without inventing a new domain Thing. | 08/09 |
| GAP-12-009 | Audit read authorization | Minimum reconstruction UI needs an existing legitimate read-scope policy; 12 does not create a new audit-reader authority. | 04/11 |
| GAP-12-010 | Controlled INDETERMINATE fixture seam | 13 must define a deterministic falsification fixture that creates uncertainty without weakening production semantics. | 13 |

## 39.31 CARRIED GAPS

Carried without silent closure:

```text
GAP-05-001 Workspace governance-root bootstrap
GAP-04-013 Export Authority
GAP-04-001 collaborative QuestionSelection
GAP-04-007 timer identity/trust
D8 Method Approval Authority
GAP-07-001 Assumption Evidence sufficiency
GAP-08-001 AI context policy
GAP-08-008 provider privacy mapping
GAP-09-001 external tool idempotency
retention / deletion / audit policy dependencies
Journey materialization
Export artifact activation
recovery command catalogue beyond exercised fixture
```

Only the first bootstrap gap and exact provider/privacy eligibility are hard blockers for the selected real executable proof.

## 39.32 UPSTREAM CONTRADICTIONS

```text
NONE FOUND
```

No upstream reconstruction is required by 12.

## 39.33 READINESS FOR 13

```text
12 STATUS:
READY FOR HUMAN REVIEW

13 STATUS:
NOT BUILT

IMPLEMENTATION:
NOT STARTED

ARCHITECTURE BASELINE:
NOT FROZEN
```

13 may begin only after explicit:

```text
HUMAN_REVIEW::12_APPROVED
GO::BUILD_13_TEST_AND_FALSIFICATION_ARCHITECTURE
```

STOP.
