# 10_FAILURE_RECOVERY_ROLLBACK

**System:** N.Q.U.I.R.Y. Questions Are the Answer-System  
**Architecture Layer:** Failure, Recovery, Reconciliation and Rollback  
**Status:** DRAFT FOR HUMAN REVIEW  
**Authority order:** LEVEL 1 -> LEVEL 2 -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10

---

# 0. Document Authority

This document is authoritative for:

```text
failure classification
failure consequence certainty
failure-state reconstruction
LAST_PROVEN_VALID_STATE
recovery classification
recovery eligibility
recovery authority consumption
deterministic technical recovery
discretionary recovery routing
reconciliation
compensation semantics
rollback semantics
retry after failure
external-consequence reconciliation
governance recovery
AI recovery
Evidence/provenance preservation during recovery
audit/outbox recovery semantics
projection rebuild semantics
backup/restore reconciliation semantics
RecoveryRecord
Recovery Command requirements
BND-018 materialization
failure propagation
recovery termination
recovery idempotency
```

10 is not authoritative for:

```text
new domain objects
new domain state transitions
new human authority classes
new HumanAuthorityBinding assignment policies
new Evidence sufficiency rules
new Evidence validation authority
new governance rights
new privacy/retention policy
new security incident-response policy
implementation code
physical database technology
backup technology
broker technology
```

If recovery requires a domain transition not legal in 03:

```text
STOP THAT RECOVERY PATH
-> expose GAP
-> trace to 03
-> no local transition invention
```

If recovery requires human authority not defined in 04/05:

```text
STOP THAT RECOVERY PATH
-> expose GAP
-> trace to 04/05
-> no admin/operator fallback
```

If recovery requires an Evidence rule not defined in 07:

```text
STOP THAT RECOVERY PATH
-> expose GAP
-> trace to 07
-> no recovery-engine Evidence judgment
```

---

# 1. Fundamental Recovery Law

**[ARCHITECTURAL CLOSURE] AC-10-001**

```text
RECOVERY MAY RESTORE OR RECONCILE LEGITIMATE STATE.
RECOVERY MAY NOT CREATE LEGITIMACY THAT DID NOT EXIST.
```

Therefore:

```text
FAILURE != AUTHORITY
RECOVERY != AUTHORITY
ROLLBACK != AUTHORITY
RETRY != AUTHORITY
RECONCILIATION != AUTHORITY
ADMIN ACCESS != RECOVERY AUTHORITY
SYSTEM OPERATOR != HUMAN DECISION MAKER
TECHNICAL REVERSAL != DOMAIN REVERSAL
DATABASE RESTORE != LEGITIMATE DOMAIN STATE
EVENT REPLAY != RECOVERY AUTHORIZATION
HISTORICAL AUTHORITY != CURRENT AUTHORITY
PRE-FAILURE ALLOW != POST-FAILURE AUTHORITY
INDETERMINATE != FAILED
INDETERMINATE != COMMITTED
UNKNOWN CONSEQUENCE != NO CONSEQUENCE
COMPENSATION != ERASURE
ROLLBACK != HISTORY DELETION
RETRY != REPLAY
RECOVERY != SILENT MUTATION
AUDIT REPAIR != DOMAIN REPAIR
PROJECTION REBUILD != CANONICAL RECOVERY
AI RECOMMENDATION != RECOVERY DECISION
```

---

# 2. Recovery Is a Governed System Condition

Failure is not an exceptional escape from architecture.

Every failure path must answer:

```text
WHAT FAILED?
WHAT MAY HAVE HAPPENED?
WHAT DEFINITELY DID NOT HAPPEN?
WHAT IS THE LAST PROVEN VALID STATE?
WHICH CONSEQUENCES ARE CERTAIN?
WHICH CONSEQUENCES ARE UNCERTAIN?
WHAT MUST NOW BE BLOCKED?
WHAT MAY BE RETRIED?
WHAT MUST BE RECONCILED?
WHO MAY CHOOSE A DISCRETIONARY RECOVERY?
WHAT MAY SYSTEM_SERVICE RECOVER DETERMINISTICALLY?
WHEN IS ROLLBACK POSSIBLE?
WHEN IS ROLLBACK IMPOSSIBLE?
HOW IS AUTHORITY REVALIDATED AFTER FAILURE?
HOW IS EVIDENCE PRESERVED?
HOW DOES THE SYSTEM RETURN TO A VALID GOVERNED STATE?
```

A recovery mechanism that cannot answer the relevant questions is not permitted to create a consequential effect.

---

# 3. Semantic Separation

```text
FAILURE
= observed inability, invalidity or uncertainty in an operation or subsystem

RECOVERY
= governed process for returning the system to a provably valid operational condition

RECONCILIATION
= determination of what actually occurred and what state is legitimate now

ROLLBACK
= one specific reversal class, not a synonym for recovery

COMPENSATION
= new consequential operation intended to counter or mitigate a prior consequence

RETRY
= new attempt to execute the same logical Command semantics

REPLAY
= reconstruction from historical Event/Audit facts

PROJECTION REBUILD
= deterministic reconstruction of derived/read state

RESTORE
= infrastructure operation restoring persisted bytes from a backup/snapshot
```

None of these terms implies authority.

---

# 4. Preserve 03 Consequential Outcomes

The only generic consequential transition outcomes remain:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

10 does not add a fifth generic transition outcome.

## 4.1 DENIED

Meaning:

```text
the governed request was not permitted to execute
no legitimate consequential execution occurred
```

Recovery semantics:

```text
no bypass retry
same materially unchanged denied request remains subject to the same missing/failed prerequisite
materially changed request = new Command
```

A DENIED result may be retried only after the condition that caused denial has legitimately changed and the new attempt passes fresh boundaries. It is not a technical retry privilege.

## 4.2 FAILED_PRECOMMIT

Meaning:

```text
the attempt failed before canonical consequential commit
canonical consequence is proven absent
```

Recovery semantics:

```text
fresh governed attempt may be possible
same logical command_id where semantics are unchanged
new attempt_id
fresh boundary evaluation
fresh commit-time authority
fresh Evidence evaluation where required
fresh expected versions
```

## 4.3 COMMITTED

Meaning:

```text
canonical consequential commit is proven
```

A later:

```text
notification failure
broker failure
projection failure
external post-commit failure
client timeout
```

does not retroactively change COMMITTED into FAILED_PRECOMMIT.

Recovery addresses the later failure while preserving the committed occurrence.

## 4.4 INDETERMINATE

Meaning:

```text
the system cannot prove whether a relevant consequence occurred,
committed,
or completed sufficiently to determine safe next consequence
```

INDETERMINATE requires:

```text
block dependent consequential transitions
block blind retry
preserve all available evidence/provenance
preserve command/attempt/commit/correlation identity
preserve external-operation identity
route to BND-018 reconciliation
```

INDETERMINATE is not permission to choose the safer-looking historical branch.

---

# 5. Consequence Certainty Model

**[ARCHITECTURAL CLOSURE] AC-10-002**

Recovery reconstruction uses explicit certainty classes:

```text
PROVEN_COMMITTED
PROVEN_NOT_COMMITTED
EXTERNAL_CONSEQUENCE_PROVEN
EXTERNAL_CONSEQUENCE_PROVEN_ABSENT
EXTERNAL_CONSEQUENCE_UNKNOWN
CANONICAL_STATE_UNKNOWN
GOVERNANCE_STATE_UNKNOWN
```

These are recovery classifications, not new 03 domain states.

Rules:

```text
missing telemetry != proven absence
timeout != proven failure
local error != external non-occurrence
event missing != canonical non-commit
projection missing != canonical non-commit
database row present != legitimate commit
audit projection missing != audit record absent
```

---

# 6. Failure-State Reconstruction

**[ARCHITECTURAL CLOSURE] AC-10-003**

For every failed or uncertain consequential operation, reconstruction must resolve, where applicable:

```text
COMMAND
  command_id
  command_type
  command contract version
  requested payload
  target refs

ATTEMPT
  attempt_id
  attempt timestamps
  execution service

COMMIT UNIT
  commit_id if allocated
  mutation set
  expected versions
  commit result evidence

CANONICAL RECORD VERSION
  before version
  after version if proven

GOVERNANCE STATE
  membership
  roles
  HumanAuthorityBinding
  FacilitatorScopeBinding
  governance bundle versions

AUTHORITY STATE AT COMMIT ATTEMPT
  actor
  authority class
  authority source
  binding effectiveness
  revocation state

HUMAN DECISION
  exact Decision/reference where required

EVIDENCE SET / VERSIONS
  EvidenceSetReference
  Evidence identities
  content versions
  validation states
  relation versions

METHOD VERSION
  where applicable

AUDIT RECORDS
  AuditEvent identity
  durable audit state
  audit projection state separately

OUTBOX RECORDS
  outbox identity
  event identity
  delivery state

EVENT DELIVERY
  delivery attempts
  consumer acknowledgements where available

EXTERNAL TOOL/ACTION RECORDS
  external operation identity
  provider request identity
  idempotency identity
  authoritative external status evidence

AI GENERATION / TOOL LINEAGE
  generation_id
  AIOP
  provider/model
  tool call identity
  validation proof
  retry/fallback lineage

IDEMPOTENCY RECORD
  logical command identity
  payload fingerprint
  prior result

CORRELATION / CAUSATION CHAIN
  correlation_id
  causation_id
```

Reconstruction then assigns the certainty classes in Section 5.

No missing record may be silently interpreted as proof of non-occurrence.

---

# 7. LAST_PROVEN_VALID_STATE

**[ARCHITECTURAL CLOSURE] AC-10-004**

`LAST_PROVEN_VALID_STATE` is an operational recovery reference.

It is not a new domain Thing.

Definition:

```text
the most recent reconstructable system state for which legitimacy is proven
through all predicates required for the consequence that produced it
```

Where applicable the proof chain includes:

```text
legal prior state
legal transition
actor
current-at-commit authority
human Decision
Evidence set/version
boundary results
commit
canonical resulting version
audit/provenance correlation
```

It is not necessarily:

```text
latest timestamp
latest database row
latest Event
latest projection
latest cache
latest UI state
latest backup row
```

Recovery begins from the last proven valid state plus all later known/unknown consequences.

It does not erase later uncertain facts.

---

# 8. Last-Proven-Valid-State Selection Algorithm

For a failure correlation:

```text
1. locate original Command and attempts
2. locate every candidate CommitUnit
3. locate canonical versions before and after each candidate commit
4. reconstruct applicable authority/governance state at commit time
5. reconstruct required human Decision
6. reconstruct required Evidence/version set
7. reconstruct boundary/commit proof
8. reconstruct audit/outbox correlation
9. distinguish canonical commit from external side effects
10. order only states whose causal/commit relation is proven
11. select the latest state with complete legitimacy proof
12. retain every later uncertain artifact as unresolved consequence evidence
```

If step 11 cannot produce a unique legitimate state:

```text
CANONICAL_STATE_UNKNOWN
-> dependent consequence blocked
-> reconciliation remains UNRESOLVED
```

---

# 9. Failure Taxonomy

10 defines these explicit failure classes:

```text
F-VAL    VALIDATION FAILURE
F-AUTH   AUTHORITY FAILURE
F-BND    BOUNDARY FAILURE
F-CONC   CONCURRENCY FAILURE
F-PERS   PERSISTENCE FAILURE
F-PCOM   PARTIAL COMMIT FAILURE
F-AUD    AUDIT FAILURE
F-OUT    EVENT / OUTBOX FAILURE
F-AIGEN  AI GENERATION FAILURE
F-AIVAL  AI VALIDATION FAILURE
F-AITOOL AI TOOL FAILURE
F-EXT    EXTERNAL SIDE-EFFECT FAILURE
F-NET    NETWORK FAILURE
F-PROVDR PROVIDER FAILURE
F-EVID   EVIDENCE FAILURE
F-PROV   PROVENANCE FAILURE
F-GOV    GOVERNANCE MUTATION FAILURE
F-REC    RECOVERY FAILURE
F-SEC    SECURITY-RELEVANT FAILURE
```

A single attempt may have multiple failure classifications.

The system must not collapse them when consequence certainty differs.

---

# 10. F-VAL Validation Failure

## Detection Point

```text
transport/schema validation
operation-contract validation
AI response validation
domain precondition validation
```

## Known State

The validation predicate failed or could not produce an acceptable proof.

## Unknown State

Depends on timing. Precommit validation normally leaves canonical consequence absent.

## Canonical Consequence

If detected before BND-014 commit:

```text
FAILED_PRECOMMIT
```

or DENIED where the failure is a governed eligibility denial.

## External Consequence

Must be separately reconstructed if any external operation was already invoked.

## Audit Requirement

Record failure/correlation where audit policy requires.

## Retry Eligibility

Possible only through fresh governed attempt after the invalid condition is corrected.

## Reconciliation Requirement

Required if an external consequence or commit may already have occurred.

## Dependent-Transition Effect

Block only operations depending on the invalid/uncertain result.

## Recovery Authority Requirement

Deterministic technical correction may be SYSTEM_SERVICE only if it changes no domain choice. Otherwise normal authority path.

---

# 11. F-AUTH Authority Failure

## Detection Point

```text
BND-004
BND-005
BND-006
BND-011
BND-012
BND-014 commit-time revalidation
```

## Known State

Required authority is absent, ineffective, revoked, mismatched or unprovable.

## Canonical Consequence

Before commit:

```text
DENIED or FAILED_PRECOMMIT
```

according to the originating boundary contract.

## Unknown State

If authority changed during an uncertain commit:

```text
commit legitimacy/occurrence may require reconciliation
```

## External Consequence

Never infer absence solely from authority failure discovered after invocation.

## Retry Eligibility

No stale authority reuse. A fresh attempt requires current authority.

## Reconciliation Requirement

Required when commit/external consequence certainty is unknown.

## Dependent-Transition Effect

Block operations dependent on the failed authority.

## Recovery Authority Requirement

Recovery service cannot grant itself or the actor authority.

---

# 12. F-BND Boundary Failure

A boundary failure means an applicable boundary did not ALLOW.

It may produce:

```text
DENY
REQUIRE
ESCALATE
FAILED_PRECOMMIT
INDETERMINATE
```

according to the approved boundary semantics.

Boundary failure never creates an alternate recovery lane.

Recovery itself must pass applicable boundaries.

---

# 13. F-CONC Concurrency Failure

## Detection Point

```text
expected_versions mismatch
compare-and-set failure
serializable conflict
commit-sensitive predicate changed
```

## Known State

The attempted view of mutable state is stale.

## Canonical Consequence

If no mutation committed:

```text
FAILED_PRECOMMIT
```

## Retry Eligibility

Fresh governed attempt with:

```text
fresh authoritative reads
fresh authority
fresh Evidence
fresh boundaries
new attempt_id
```

## Reconciliation

Required only if commit result cannot be proven.

Concurrency conflict is not permission to overwrite the competing state.

---

# 14. F-PERS Persistence Failure

Persistence failure must distinguish:

```text
failure before any CommitUnit mutation
failure with proven transaction abort
failure after canonical commit
failure with uncertain commit
```

Results:

```text
proven abort -> FAILED_PRECOMMIT
proven commit -> COMMITTED
uncertain commit -> INDETERMINATE
```

A database exception by itself does not establish which result occurred.

---

# 15. F-PCOM Partial Commit Failure

A logical CommitUnit is partial when required coupled consequences cannot be proven to have committed consistently.

Examples:

```text
Session changed but QuestionBurst result uncertain
governance revoke applied but dependent cleanup uncertain
canonical mutation durable but required audit durability uncertain
multi-record state bundle partly visible without proof of atomic outcome
```

If atomic abort is proven:

```text
FAILED_PRECOMMIT
```

If full commit is proven:

```text
COMMITTED
```

If neither is proven:

```text
INDETERMINATE
```

No recovery script may choose the intended final values and write them directly.

---

# 16. F-AUD Audit Failure

Audit failure classes:

```text
AUDIT_PRECOMMIT_FAILURE
AUDIT_COMMIT_UNCERTAINTY
AUDIT_DELIVERY_OR_INDEX_FAILURE
AUDIT_CORRUPTION_DETECTED_LATER
```

## 16.1 Audit Failure Before Atomic Commit

If required audit durability fails and canonical commit is prevented:

```text
FAILED_PRECOMMIT
```

## 16.2 Audit Failure During Commit

If canonical/audit atomic result cannot be proven:

```text
INDETERMINATE
```

## 16.3 Audit Delivery or Index Failure After Durable Audit Commit

If durable audit record is proven and only projection/index/delivery failed:

```text
canonical outcome unchanged
audit delivery/index may be deterministically recovered
```

## 16.4 Later Audit Corruption

Later corruption does not retroactively authorize or deauthorize a historical transition.

It creates an integrity/reconstruction problem.

If legitimacy can no longer be proven for a required dependent operation:

```text
block that dependent operation
route to reconciliation/security handling
```

## 16.5 Prohibition

```text
fabricate audit after the fact
-> cannot legitimize prior mutation
```

Audit repair != domain repair.

---

# 17. F-OUT Event / Outbox Failure

Where canonical state and durable outbox entry committed atomically:

```text
canonical state = COMMITTED
outbox delivery = operationally pending/failed
```

Recovery may:

```text
retry outbox delivery
deduplicate consumer delivery
rebuild event-delivery projection
```

Recovery may not:

```text
repeat domain Command
repeat external consequence merely because Event delivery failed
```

If the required event/outbox basis itself cannot be proven:

```text
classify according to CommitUnit certainty
```

No authoritative Event may be regenerated from guesswork.

---

# 18. F-AIGEN AI Generation Failure

Preserve AIGeneration:

```text
REQUESTED
RUNNING
OUTPUT_RECEIVED
VALIDATED
REJECTED
FAILED
```

Pure generation failure with no canonicalized derived artifact:

```text
no domain consequence
new generation may be requested where allowed
new AIGeneration identity
```

A FAILED or REJECTED generation is not revived.

---

# 19. F-AIVAL AI Validation Failure

If output exists but validation fails:

```text
AIGeneration -> REJECTED
```

or FAILED where validation infrastructure failure prevents safe acceptance under 08.

No:

```text
AI_VALIDATION_PROOF
-> no downstream use that requires it
```

Retry/fallback:

```text
new AIGeneration
new provenance
new validation
```

Prior validation proof is never reused.

---

# 20. F-AITOOL AI Tool Failure

AI tool failure must distinguish:

```text
tool not invoked
tool invoked, proven no side effect
tool invoked, proven side effect
tool invoked, side effect unknown
```

If side effect unknown:

```text
INDETERMINATE
-> BND-018
-> no blind retry
```

AI_PROCESSOR cannot resolve its own uncertain consequence by assertion.

---

# 21. F-EXT External Side-Effect Failure

External consequences include:

```text
message sent
external API mutation
file export/disclosure
physical experiment start
external workflow invocation
notification to a human where consequential
```

Failure classification must preserve:

```text
external operation identity
provider/system
request payload/version
idempotency key where supported
request timestamp
response evidence
authoritative external status query where available
```

Timeout means:

```text
response unknown
```

not:

```text
external failure proven
```

---

# 22. F-NET Network Failure

Network failure is transport information, not consequence information.

It can mean:

```text
request never left
request left, response lost
provider executed, acknowledgement lost
local commit succeeded, response to client lost
```

Therefore network failure requires reconstruction before retry whenever consequence may exist.

---

# 23. F-PROVDR Provider Failure

Provider failure includes:

```text
AI provider outage
external API provider outage
broker outage
storage provider outage
```

Provider status does not determine domain outcome.

Provider fallback is governed by the affected subsystem contract.

For AI fallback, 08 applies:

```text
new AIGeneration
new provider/model provenance
new validation
```

---

# 24. F-EVID Evidence Failure

Evidence failure includes:

```text
required Evidence missing
Evidence INVALIDATED
Evidence UNAVAILABLE where current verification is required
Evidence version mismatch
EvidenceSetReference incomplete
source no longer resolves
claim anchor mismatch
```

Recovery cannot:

```text
manufacture Evidence
reinterpret Evidence sufficiency
silently substitute a historical version
```

If a current transition requires Evidence:

```text
evaluate current approved 07 Evidence rules
```

Historical Evidence consumed by an earlier legitimate Decision remains historical input.

---

# 25. F-PROV Provenance Failure

Provenance failure includes:

```text
origin unknown
source reference mismatch
claim anchor mismatch
AI/human origin ambiguity
generation lineage missing
authority source reference missing
commit correlation broken
```

If provenance is required to prove legitimacy:

```text
dependent consequential operation blocked
```

Repair may reconstruct an existing provenance fact from authoritative records.

It may not invent a provenance fact that did not exist.

---

# 26. F-GOV Governance Mutation Failure

Governance mutation failures are high-risk because they affect future authority.

Applicable operations include:

```text
membership grant/revoke
role assignment/removal
HumanAuthorityBinding grant/change/revoke
FacilitatorScopeBinding grant/revoke
authority reassignment
method approval where eventually supported
```

Approved governance bundles must be reconstructed as CommitUnits.

If effective governance cannot be proven:

```text
least-permissive interpretation
```

Specific rules:

```text
uncertain grant
-> treat as not granted

uncertain revocation
-> authority unavailable

uncertain membership grant
-> treat as non-member

uncertain membership revocation
-> do not permit authority that depends on the membership until reconciled

uncertain role elevation
-> treat as not elevated

uncertain HumanAuthorityBinding replacement
-> do not treat either candidate as a usable new authority merely because one row exists
```

This does not rewrite historical records.

It controls current consequence under uncertainty.

---

# 27. F-REC Recovery Failure

Recovery itself may fail.

Recovery failure must be classified using the same consequence-certainty rules.

A failed recovery may produce:

```text
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

for any consequential Recovery Command.

An INDETERMINATE recovery:

```text
cannot be blindly retried
must itself be reconciled
```

A RecoveryRecord must preserve nested recovery lineage.

---

# 28. F-SEC Security-Relevant Failure

10 defines recovery interaction, not full incident response.

If compromise is suspected:

```text
do not trust cached authority
do not trust stale ALLOW
do not automatically replay pending Commands
do not let AI determine integrity
preserve forensic/audit evidence
block consequential transitions whose legitimacy cannot be proven
route security controls and incident response to 11
```

Security suspicion does not grant operator recovery authority.

---

# 29. Failure Taxonomy Matrix

| Failure class | Detection point | Canonical consequence | External consequence | Retry | Reconciliation | Dependent effect | Recovery authority |
|---|---|---|---|---|---|---|---|
| VALIDATION | validators / preconditions | usually DENIED or FAILED_PRECOMMIT | separate | fresh attempt if safe | if consequence uncertain | dependency scoped | normal current authority if consequential |
| AUTHORITY | authority boundaries / commit | DENIED, FAILED_PRECOMMIT, or INDETERMINATE | separate | never with stale authority | if commit uncertain | authority-dependent blocked | current 04/05 authority |
| BOUNDARY | any BND | boundary-defined | separate | no bypass | when uncertainty remains | dependency scoped | normal boundary path |
| CONCURRENCY | commit freshness | FAILED_PRECOMMIT if no commit | separate | fresh attempt | if commit uncertain | target/dependents | current authority |
| PERSISTENCE | CommitUnit | FAILED_PRECOMMIT, COMMITTED, INDETERMINATE | separate | only after certainty | often | dependent if uncertain | current authority if new consequence |
| PARTIAL COMMIT | logical bundle | INDETERMINATE unless abort/full commit proven | separate | no blind retry | required | dependents blocked | deterministic only if no new choice |
| AUDIT | audit/commit path | depends on durability certainty | none/domain separate | delivery retry only where safe | if consistency uncertain | audit-dependent blocked | no domain authority from audit repair |
| EVENT/OUTBOX | outbox/delivery | COMMITTED may coexist | consumer consequence separate | delivery retry | if event basis uncertain | normally not domain-global | deterministic delivery service |
| AI GENERATION | AI Gateway/provider | no domain consequence by itself | tool separate | new generation | if tool consequence uncertain | only AI-dependent path | AI operation permission |
| AI VALIDATION | Response Validator | no accepted AI effect | tool separate | new generation | if external tool consequence | AI-dependent path | no AI recovery decision |
| AI TOOL | tool layer | separate | may be unknown | only if proven safe | required if unknown | affected dependents | current authority for new consequence |
| EXTERNAL SIDE EFFECT | external integration | canonical may differ | proven/absent/unknown | conditional | required if unknown | affected dependents | current authority for reissue/compensation |
| NETWORK | transport | unknown until reconstructed | unknown possible | conditional | often | affected dependents | none created by transport |
| PROVIDER | provider | subsystem-specific | subsystem-specific | contract-specific | if uncertainty | dependency scoped | no provider-derived authority |
| EVIDENCE | BND-013 / source | no valid Evidence-dependent commit | none | after current Evidence valid | if historical use affected | Evidence-dependent blocked | 07/04 authority |
| PROVENANCE | lineage validation | block if proof required | none | after reconstruction | often | proof-dependent blocked | no invented provenance |
| GOVERNANCE | governance CommitUnit | least-permissive if uncertain | none | no stale grant/revoke retry | required | authority dependents blocked | WORKSPACE_GOVERNANCE_RIGHT or approved System-derived cleanup |
| RECOVERY | BND-018 / recovery command | normal 03 outcome | may be uncertain | no blind retry if indeterminate | required | recovery dependents blocked | same rules as recovery operation |
| SECURITY | security/integrity detection | fail closed where legitimacy unprovable | unknown possible | no automatic retry | security + recovery | dependency based, conservative | 11 + existing authority only |

---

# 30. Recovery Classes

10 distinguishes:

```text
RC-01 DETERMINISTIC_TECHNICAL_RECOVERY
RC-02 RECONCILIATION
RC-03 COMPENSATION
RC-04 ROLLBACK
RC-05 PROJECTION_REBUILD
RC-06 RETRY
RC-07 MANUAL_DISCRETIONARY_RECOVERY
```

These classes are not authority classes.

---

# 31. RC-01 Deterministic Technical Recovery

SYSTEM_SERVICE may perform bounded deterministic recovery only when all are true:

```text
intended legitimate state is already established
no new human judgment is required
no new authority interpretation is required
no new Evidence sufficiency judgment is required
no new domain choice is created
recovery algorithm is approved/versioned
current recovery predicates are satisfied
recovery does not create a new external consequence unless that consequence is already authorized by an approved deterministic contract
```

Examples:

```text
rebuild projection from committed canonical state
resume transactional-outbox delivery
restore derived index
recompute deterministic derived data
deduplicate known repeated delivery
reconstruct audit view from durable audit records
complete a technically incomplete non-discretionary persistence step only where the approved atomicity/recovery contract proves the legitimate target and permits completion
```

SYSTEM_SERVICE may not use RC-01 to:

```text
select a Question
classify an Assumption
authorize an Experiment
create/finalize a Decision
authorize Action
grant human authority
choose between legitimate domain alternatives
reinterpret Evidence
reverse a human Decision
choose compensation
```

---

# 32. Deterministic Recovery Authority

**[ARCHITECTURAL CLOSURE] AC-10-005**

Deterministic recovery consumes the already-approved 04/05 `SYSTEM_DERIVED` procedural model.

10 does not create a new recovery authority class.

The recovery derivation is valid only if:

```text
service identity is known
algorithm/version is approved for the operation
target state/effect is uniquely determined by proven facts
scope is exact
no human Decision Right is exercised
no Evidence interpretation is exercised
no new authority is granted
BND-018 allows
BND-014 applies if canonical consequence is written
```

If any predicate fails:

```text
SYSTEM_SERVICE cannot choose
```

---

# 33. RC-02 Reconciliation

Reconciliation answers:

```text
what actually occurred?
what is proven?
what remains unknown?
what state is legitimate now?
```

Reconciliation may be deterministic fact reconstruction.

It becomes discretionary when facts do not uniquely determine the domain outcome that should bind.

Reconciliation itself must not convert uncertainty into a preferred business outcome.

---

# 34. RC-03 Compensation

Compensation is a new consequential operation.

Therefore:

```text
COMPENSATION
-> CommandEnvelope
-> current authority
-> human Decision where required
-> current Evidence where required
-> applicable boundaries
-> BND-018
-> BND-014
-> CommitUnit / external consequence
-> audit/outbox
```

Original authorization:

```text
may be provenance
!= sufficient current authority
```

A Saga engine or recovery worker cannot inherit the original actor's human authority.

Compensation does not erase the original occurrence.

---

# 35. RC-04 Rollback

Rollback is not one operation.

10 distinguishes four rollback meanings:

```text
RB-01 PRECOMMIT_TRANSACTION_ROLLBACK
RB-02 CANONICAL_STATE_REVERSAL
RB-03 COMPENSATING_TRANSITION
RB-04 INFRASTRUCTURE_RESTORE
```

## 35.1 RB-01 Precommit Transaction Rollback

If a transaction aborts before consequential commit and abort is proven:

```text
FAILED_PRECOMMIT
canonical state unchanged
```

This is technical rollback.

It requires no new domain Decision because no domain consequence committed.

## 35.2 RB-02 Canonical State Reversal

This means moving canonical state from a committed state to another legal canonical state.

It is a new consequential domain transition.

It is permitted only if:

```text
03 already defines a legal reversal transition
+
current authority exists
+
current Evidence/human Decision exists where required
+
boundaries pass
```

If 03 has no legal reversal transition:

```text
GAP
-> do not invent reversal in 10
```

## 35.3 RB-03 Compensating Transition

A compensating transition preserves the original occurrence and creates a new occurrence.

It follows Section 34.

## 35.4 RB-04 Infrastructure Restore

Restoring database/storage bytes is not a domain transition.

After restore, reconciliation is mandatory before the restored data is accepted as current legitimate system state.

---

# 36. Rollback of Human-Authoritative State

10 may not silently roll back:

```text
Decision DECIDED
Experiment AUTHORIZED
human QuestionSelection
human Assumption interpretation
Action authorization
HumanAuthorityBinding
FacilitatorScopeBinding
role/membership authority state
```

because a later technical operation failed.

Technical failure after a legitimate human-authoritative state does not erase that state.

If reversal is desired:

```text
legal upstream transition must exist
+
current authority must exist
```

Otherwise:

```text
GAP
-> no reversal
```

---

# 37. Irreversible Consequences

Some consequences cannot be rolled back:

```text
message sent
human informed
external API action executed
file exported
Evidence disclosed
experiment physically started
external system mutated
authority exercised before later revocation
```

For an irreversible consequence:

```text
preserve occurrence
do not call local reversal a rollback of reality
use reconciliation
use compensation where legitimate
preserve audit/provenance
```

A local database value can move backward while the external world cannot.

That mismatch must remain explicit.

---

# 38. RC-05 Projection Rebuild

Projection rebuild is permitted when:

```text
authoritative committed source exists
rebuild algorithm is deterministic
projection has no canonical authority
rebuild has no external consequence
```

Projection rebuild:

```text
does not require domain Decision Authority
does not create domain state
does not authorize a transition
does not establish canonical truth beyond its sources
```

A rebuilt projection may still lag or fail.

Canonical state remains authoritative.

---

# 39. RC-06 Retry

Preserve 09:

```text
FAILED_PRECOMMIT
-> retry may be possible
-> same logical command_id if semantics unchanged
-> new attempt_id
-> fresh boundaries

COMMITTED
-> return prior result
-> no re-execution

INDETERMINATE
-> no retry
-> reconciliation

DENIED
-> no retry as bypass mechanism
```

A changed request is a new Command.

Retry != replay.

---

# 40. Retry Freshness

Every consequential retry must re-evaluate:

```text
current canonical state
current governance state
current authority
current membership
current revocation state
current HumanAuthorityBinding
current FacilitatorScopeBinding
current Evidence versions/validation
current human Decision where required
current method version/approval where applicable
current external-consequence certainty
expected record versions
all applicable boundaries
```

An earlier BND-014 ALLOW is not reusable.

---

# 41. RC-07 Manual / Discretionary Recovery

Discretionary recovery exists when multiple legitimate outcomes remain possible and the system cannot select among them without domain judgment.

Examples:

```text
external action may or may not have happened
two human-authoritative outcomes conflict
Evidence changed during failure
authority changed during failure
compensation changes domain meaning
rollback would undo a human Decision
recovery would select a new operational path
experiment continuation is a human choice
```

Rule:

```text
SYSTEM CANNOT CHOOSE BY DEFAULT
```

The system must locate an already-approved 04/05 human authority path for the exact decision.

If no authority path exists:

```text
REQUIRE / ESCALATE
-> expose GAP
-> no consequence
```

10 does not create:

```text
RECOVERY_ADMIN
SUPERUSER_RECOVERY
OPERATOR_OVERRIDE
```

---

# 42. Human Decision Authority During Recovery

**[ARCHITECTURAL CLOSURE] AC-10-006**

When recovery reaches:

```text
WHICH OUTCOME SHOULD NOW BIND?
WHICH COMPENSATION SHOULD WE CHOOSE?
SHOULD WE REVERSE THE HUMAN DECISION?
SHOULD THE EXPERIMENT CONTINUE?
WHICH EXTERNAL CONSEQUENCE SHOULD BE ACCEPTED?
```

the recovery engine has reached the boundary of its authority.

The governing pattern is:

```text
recovery reconstruction
-> present facts/uncertainties/options
-> authorized human creates required Decision
-> new governed Recovery Command
-> current authority check
-> current Evidence check where required
-> BND-018
-> BND-014
-> consequence
```

Critical invariant:

```text
THE HUMAN DOES NOT APPROVE THE RECOVERY ENGINE'S DECISION.

THE HUMAN CREATES THE DECISION THE RECOVERY ENGINE WAS NEVER AUTHORIZED TO MAKE.
```

AI may assist in presenting options.

AI does not choose.

---

# 43. Recovery Authority Context

For every consequential recovery operation reconstruct:

```text
ACTOR
ACTOR CLASS
WORKSPACE
TARGET
CURRENT STATE
FAILURE STATE
RECOVERY CLASS
REQUIRED AUTHORITY
CURRENT AUTHORITY BINDING
HUMAN DECISION where required
EVIDENCE where required
BOUNDARY PATH
ALLOWED RECOVERY EFFECT
FORBIDDEN RECOVERY EFFECT
```

Historical authority is retained as provenance of the original operation.

It is not current recovery authority.

---

# 44. Authority Revocation During Failure

Scenario:

```text
Command authorized
-> failure occurs
-> authority revoked
-> recovery begins
```

If original transition is proven not committed:

```text
new consequential attempt requires fresh current authority
```

If original transition is proven committed:

```text
historical legitimacy remains recorded
revocation does not rewrite history
```

Any new:

```text
retry
compensation
reversal
external reissue
```

requires its own current authority path.

If original commit remains INDETERMINATE:

```text
reconcile first
do not use stale authorization
```

---

# 45. External Consequence Reconciliation

For uncertain external action:

```text
1. identify external operation identity
2. identify provider/system
3. identify original request and idempotency identity
4. query authoritative external state where possible
5. preserve raw/source response and provenance
6. classify consequence certainty
7. update RecoveryRecord
8. do not infer success from timeout
9. do not infer failure from missing local response
10. retry only if non-occurrence is proven or the external contract proves safe idempotent reissue
11. if still unknown -> remain INDETERMINATE
```

External reconciliation data is:

```text
SYSTEM_PROOF and/or Evidence input according to its approved semantic role
```

It is not broader domain truth than it actually proves.

---

# 46. External Idempotency Gap

`GAP-09-001 External Tool Idempotency Contracts` remains open.

10 cannot define idempotency for unknown future consequential tools.

Every future consequential external tool contract must define:

```text
external request identity
external idempotency support
duplicate semantics
partial-success semantics
authoritative reconciliation query
irreversibility
compensation capability
```

Until a tool contract proves safe retry:

```text
unknown external consequence
-> INDETERMINATE
-> no blind retry
```

---

# 47. AI Failure and Recovery

Preserve 08 exactly.

## 47.1 Pure Generation Failure

```text
AIGeneration FAILED
+
no accepted derived artifact
+
no tool side effect
```

Result:

```text
no canonical domain consequence
```

A new generation may be requested where the operation remains permitted.

## 47.2 Derived Artifact Already Canonicalized

If a prior AI output was validly canonicalized as a derived artifact:

```text
generation retry does not overwrite it silently
```

A new generation produces:

```text
new AIGeneration
new output identity/version
new provenance
```

Any replacement/supersession must use approved representation semantics.

## 47.3 AI Tool Unknown Consequence

```text
INDETERMINATE
-> external reconciliation
-> no blind retry
```

## 47.4 Provider Fallback

```text
new AIGeneration
new provider/model provenance
new validation
```

Never reuse prior `AI_VALIDATION_PROOF`.

## 47.5 AI Recovery Role

AI may:

```text
summarize failure state
identify missing proof
compare recovery options
propose non-authoritative recovery paths
identify contradictions
```

AI may not:

```text
choose discretionary recovery
grant authority
decide Evidence sufficiency beyond approved deterministic validation
mark unknown external action failed merely from timeout
reverse human-authoritative state
```

---

# 48. Evidence During Failure

Failure must preserve:

```text
Evidence identity
Evidence content version
SourceReference
ClaimAnchor
EvidenceRelation
validation state
supersession/invalidation
EvidenceSetReference consumed
provenance
human interpretation
commit correlation
```

If Evidence changes during recovery:

```text
historical Evidence remains historical input
new consequential transition evaluates current required Evidence
historical Decision is not silently rewritten
```

Recovery cannot manufacture Evidence that did not exist.

---

# 49. Evidence Invalidation After Historical Decision

`GAP-07-003 post-decision Evidence invalidation` remains an upstream Evidence/domain-policy gap.

10 closes only recovery behavior:

```text
preserve historical Decision
preserve exact Evidence version consumed
preserve later invalidation
do not silently rewrite historical Decision
block/re-evaluate any new Evidence-dependent consequence according to current 07 rules
```

Whether a prior Decision must be reconsidered is not invented in 10.

If a new human decision is required, normal Decision Authority applies.

---

# 50. Governance Recovery

Governance recovery must reconstruct:

```text
grant source
scope
effective state
revocation history
granting actor
target subject
record versions
timestamps
audit
supersession/replacement relation
dependent cleanup bundle
```

No inference:

```text
Owner can fix everything
admin can restore authority
database operator can grant rights
old authority can be replayed
```

If governance state cannot be reconstructed:

```text
least-permissive current interpretation
```

---

# 51. Governance Mutation Reconciliation

For each uncertain governance CommitUnit:

```text
1. reconstruct intended governance bundle
2. reconstruct each persisted mutation
3. reconstruct expected/current versions
4. reconstruct audit/outbox facts
5. determine whether atomic commit/abort is proven
6. determine effective current authority under least-permissive rule
7. if facts uniquely establish the intended legitimate result, deterministic reconciliation may materialize only the missing non-discretionary technical consequence where approved
8. if multiple governance outcomes remain possible, SYSTEM_SERVICE stops
9. any new governance choice uses WORKSPACE_GOVERNANCE_RIGHT through normal 05 governance path
```

A recovery service cannot invent a grant to make the system convenient again.

---

# 52. Governance Least-Permissive Rules

**[ARCHITECTURAL CLOSURE] AC-10-007**

For current consequential authorization while governance state is uncertain:

```text
uncertain grant -> unavailable
uncertain role elevation -> unavailable
uncertain Facilitator scope grant -> unavailable
uncertain HumanAuthorityBinding grant -> unavailable
uncertain membership grant -> unavailable
uncertain revocation -> authority unavailable
uncertain membership revocation -> membership-dependent authority unavailable
uncertain binding replacement -> no new binding assumed effective
```

This is a fail-closed operational interpretation.

It does not delete or rewrite the underlying uncertain records.

---

# 53. Recovery of Revoked Authority

A revoked `HumanAuthorityBinding` is terminal under 05.

Recovery may not:

```text
reactivate old binding
restore old ACTIVE flag from backup
replay grant Event as current authority
```

If authority must exist again:

```text
new governance operation
new binding
current WORKSPACE_GOVERNANCE_RIGHT
fresh boundaries
```

where the approved 05 mechanism permits it.

---

# 54. Method Approval Recovery

D8 and `GAP-04-008` remain open.

Therefore 10 cannot invent method approval recovery authority.

If a method approval record becomes uncertain:

```text
SYSTEM_DERIVED method-dependent authority unavailable
-> fail closed
-> reconcile record
-> if discretionary reapproval is required and no authority exists, GAP remains
```

---

# 55. Audit and Domain Recovery Separation

```text
audit repair
may restore/reconstruct audit representation

audit repair
may not mutate domain state

domain repair
may not fabricate audit history
```

If an unauthorized mutation occurred:

```text
adding an AuditEvent afterward
!= legitimizing the mutation
```

The unauthorized state must be treated according to canonical legitimacy reconstruction and security handling.

---

# 56. Outbox Recovery

If:

```text
canonical commit proven
+
durable outbox entry proven
```

then SYSTEM_SERVICE may deterministically:

```text
retry delivery
advance delivery operational status
deduplicate acknowledged delivery
```

The delivery worker does not rerun the originating Command.

At-least-once delivery means consumers must remain consequence-safe.

---

# 57. Event Replay During Recovery

Event replay may:

```text
rebuild projection
reconstruct read model
reconstruct audit view
verify history
assist LAST_PROVEN_VALID_STATE reconstruction
```

Event replay may not:

```text
invoke external side effect
submit new consequential Command automatically
rerun AI tool
advance canonical state
grant authority
```

If replay discovers a required current action:

```text
proposal/recovery finding
-> new governed Command
```

---

# 58. Projection Failure

Projection failure:

```text
does not change canonical state
does not invalidate canonical commit
does not create authority
```

Projection rebuild may be RC-05.

Projection state may not become recovery truth if it conflicts with canonical committed sources.

---

# 59. Backup / Restore

Infrastructure restore is not domain rollback.

After a restore, do not accept:

```text
restored database == current legitimate state
```

without reconciliation.

Required reconciliation includes:

```text
restore point identity
last durable canonical commit before restore
Commands committed after restore point
governance mutations after restore point
authority revocations after restore point
Evidence changes after restore point
audit continuity
outbox/event state
external consequences
AI/tool consequences
idempotency records
```

A backup may move bytes backward while reality moved forward.

---

# 60. Post-Restore Quarantine

**[ARCHITECTURAL CLOSURE] AC-10-008**

After an infrastructure restore that may have lost committed history:

```text
consequential write paths whose current predicates depend on unreconciled history
must remain blocked
```

until the relevant current canonical/governance/Evidence state is reconciled.

This is dependency-scoped, not necessarily a global shutdown.

Projection-only reads may remain available if clearly marked and safe.

---

# 61. Restore and Revoked Authority Attack

If backup state contains:

```text
HumanAuthorityBinding ACTIVE
```

but post-backup history contains a proven revocation:

```text
restored ACTIVE row is not current authority
```

Reconciliation must reapply the proven current governance truth through an approved restoration/reconstruction mechanism.

The backup copy cannot resurrect authority.

---

# 62. Deletion / Retention Failure

10 does not close retention policy.

Preserve:

```text
GAP-05-004 Governance record retention
GAP-07-004 Evidence deletion versus audit
GAP-07-006 provenance retention
GAP-09-004 retention materialization strategy
```

For partial or uncertain deletion:

```text
classify which canonical/Evidence/provenance/audit facts remain provable
do not fabricate deleted proof
block consequences requiring missing proof
preserve privacy/legal dependency for 11
```

A recovery backup may not be used as an ungoverned way to defeat deletion policy.

---

# 63. RecoveryRecord

**[ARCHITECTURAL CLOSURE] AC-10-009**

A reconstructable operational `RecoveryRecord` is required.

Classification:

```text
OPERATIONAL_RECORD
not domain Thing
not authority token
not Evidence by itself
```

Minimum semantics:

```text
recovery_id
workspace_scope_ref
failure_correlation_ref
original_command_id
original_attempt_id
original_commit_id nullable
failure_classifications[]
known_canonical_state_ref nullable
canonical_state_certainty
known_external_consequence_ref nullable
external_consequence_certainty
unknown_consequence_description nullable
last_proven_valid_state_ref
recovery_class
recovery_actor_type
recovery_actor_id
required_authority_ref nullable
current_authority_binding_ref nullable
human_decision_ref nullable
evidence_proof_refs[]
recovery_command_ids[]
recovery_attempt_refs[]
result
created_at
updated_at
resolved_at nullable
audit_linkage
```

`RecoveryRecord` may contain references to proof.

Its presence does not prove the referenced facts.

---

# 64. RecoveryRecord Outcomes

RecoveryRecord may terminate as:

```text
RECOVERED
RECONCILED
COMPENSATED
NO_ACTION_REQUIRED
UNRESOLVED
```

These are operational recovery outcomes only.

They do not replace:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

`UNRESOLVED` preserves blocking where relevant consequence remains uncertain.

---

# 65. RecoveryRecord Mutability

RecoveryRecord may accumulate new findings and attempts.

Historical findings must remain reconstructable.

Do not rewrite:

```text
UNKNOWN -> PROVEN_ABSENT
```

without preserving the proof and the prior uncertainty history.

Recovery history is append-oriented/auditable even if its operational representation uses mutable current-status fields.

Exact physical schema belongs to implementation.

---

# 66. Recovery Command

**[ARCHITECTURAL CLOSURE] AC-10-010**

Every consequential recovery effect is represented as a governed Command.

Examples:

```text
compensate external action
perform legal canonical reversal
reissue external action
apply human-selected recovery path
execute authorized governance correction
```

A Recovery Command is not privileged.

It uses `CommandEnvelope`.

It must include/refer to:

```text
command_id
new attempt_id
correlation to recovery_id
correlation to original command/failure
workspace scope
target refs
expected versions
AuthorityContextReference
human Decision where required
EvidenceSetReference where required
idempotency key
recovery class
payload
```

It passes normal boundaries.

---

# 67. Recovery Command Catalogue Status

`GAP-09-015 Recovery Command Catalogue` is partially closed by 10 at the semantic level.

10 defines the permitted command classes:

```text
RECOVERY_COMPENSATE
RECOVERY_LEGAL_REVERSAL
RECOVERY_EXTERNAL_REISSUE
RECOVERY_APPLY_HUMAN_SELECTED_PATH
RECOVERY_GOVERNANCE_CORRECTION
```

These names are contract categories, not new domain transitions.

Each activation still requires an existing legal 03/05 target operation.

If no legal target operation exists:

```text
command class is not executable
-> GAP
```

Non-consequential deterministic recovery operations such as projection rebuild/outbox delivery do not need to masquerade as domain Commands, provided they cannot create canonical/domain/external consequence.

---

# 68. BND-018 Recovery / Rollback Boundary

10 materializes BND-018.

## BOUNDARY ID

```text
BND-018
```

## PURPOSE

Ensure recovery restores/reconciles only architecture-valid state and cannot bypass authority, scope, Evidence, immutability, audit, idempotency or commit semantics.

## SUBJECT

One failure/recovery correlation.

## REQUESTING ACTOR

```text
SYSTEM_SERVICE for deterministic recovery/reconciliation
HUMAN_USER for authorized discretionary recovery decision/command
```

AI_PROCESSOR may provide analysis/proposals only.

## INPUT

```text
failure identity
Workspace
original Command/attempt
CommitUnit
last proven valid state
current canonical state
current governance state
current authority state
current Evidence where required
external consequence certainty
requested recovery class
recovery algorithm/version
idempotency state
audit/outbox state
expected versions
```

---

# 69. BND-018 Evaluation

BND-018 must determine:

```text
is failure identity reconstructable?
is Workspace exact?
is LAST_PROVEN_VALID_STATE established?
is current canonical state proven?
is governance state proven?
is current required authority proven?
is current Evidence sufficient under 07 where required?
is external consequence certainty adequate?
is recovery deterministic or discretionary?
does recovery create a new domain choice?
does recovery create a new external consequence?
is recovery legal under 03/05?
is recovery itself reversible?
is idempotency state known?
are expected versions current?
is audit/commit correlation sufficient?
```

---

# 70. BND-018 ALLOW

ALLOW only when the requested recovery effect is one of:

```text
deterministic restoration/reconstruction of already legitimate state
deterministic projection/outbox/index recovery
reconciliation that creates no domain choice
or
a new consequential Recovery Command with current approved authority and all normal prerequisites
```

---

# 71. BND-018 DENY

DENY:

```text
recovery grants authority
recovery uses admin/operator status as domain authority
recovery uses stale pre-failure ALLOW
recovery replays Event as Command
recovery writes illegal 03 state
recovery overwrites immutable Question original
recovery changes human Decision without legal transition
recovery treats projection/cache as canonical truth
recovery retries unknown external consequence blindly
recovery fabricates Evidence/provenance/audit
recovery treats backup bytes as current legitimacy
recovery lets AI choose discretionary outcome
recovery repeats already committed consequence
RecoveryRecord used as authority token
```

---

# 72. BND-018 REQUIRE / ESCALATE

REQUIRE:

```text
named missing proof
current authority
current human Decision
current Evidence
external reconciliation
legal reversal transition
recovery algorithm/version
```

ESCALATE:

```text
discretionary human choice -> existing 04/05 authority path
missing authority class -> architecture GAP, no consequence
security compromise -> 11 security path
unresolved deletion/retention -> 11/legal/privacy dependency
```

No "recovery mode" disables BND-014.

---

# 73. BND-018 and BND-014

For consequential recovery:

```text
BND-018
-> all normal applicable boundaries
-> BND-014 fresh commit
```

BND-018 does not replace BND-014.

At recovery commit time, revalidate:

```text
current state
current authority
current scope
current governance
current Evidence
human Decision
external certainty prerequisite
expected versions
idempotency
```

---

# 74. Recovery Idempotency

Every consequential recovery attempt requires:

```text
recovery_id
recovery command_id
attempt_id
idempotency_key
correlation to original failure
expected current versions
payload fingerprint
```

Duplicate same recovery Command after COMMITTED:

```text
return prior result
do not repeat compensation/reversal
```

Recovery Command INDETERMINATE:

```text
no blind retry
reconcile recovery itself
```

---

# 75. Duplicate Compensation Prevention

Compensation must have a stable logical identity tied to:

```text
original consequence
compensation purpose/type
target
payload fingerprint
```

A queue retry, user double-submit or worker restart must not create a second compensation.

If whether compensation occurred is unknown:

```text
INDETERMINATE
-> reconcile
```

---

# 76. Failure Propagation

Failure propagation is dependency-based.

## 76.1 INDETERMINATE Consequential State

```text
-> block dependent consequential transitions
```

Unrelated inquiry paths may continue if they do not consume the uncertain state.

## 76.2 Unknown Governance State

```text
-> block authority checks depending on that governance state
```

Do not necessarily block unrelated Workspace reads.

## 76.3 Unknown Evidence Integrity

```text
-> block Evidence-dependent transitions consuming that Evidence/version
```

## 76.4 Unknown Workspace Scope

```text
-> block operation
```

## 76.5 AI Failure

```text
-> block only operation paths requiring that AI result
```

It does not automatically block unrelated human inquiry.

## 76.6 Projection Failure

```text
-> does not block canonical state by default
```

It may operationally block an action if the action cannot be safely executed without that projection and no authoritative alternative exists.

Operational dependency does not make projection authoritative.

---

# 77. Failure Propagation Graph

Recovery should derive a dependency graph from:

```text
Command target refs
CommitUnit mutation refs
authority binding refs
EvidenceSetReference
human Decision refs
method refs
correlation/causation
event/outbox refs
external-operation refs
AI generation/tool refs
```

Blocking propagates only across edges that are necessary for the next consequence's legitimacy or safe execution.

No global "system failed" state is introduced in 10.

---

# 78. Recovery Termination

A recovery correlation terminates when one of these is proven:

## RECOVERED

The system has returned to a valid governed operational condition through deterministic or authorized recovery.

## RECONCILED

The actual consequence/state is proven and no further corrective consequence is required by the recovery path.

## COMPENSATED

A new authorized compensation committed/executed as defined, while the original occurrence remains historical fact.

## NO_ACTION_REQUIRED

Reconstruction proves the system is already in a valid governed state and no recovery consequence is required.

## UNRESOLVED

Material uncertainty remains.

Dependent blocking remains.

---

# 79. Recovery Evidence Preservation

Every recovery attempt preserves:

```text
original failure artifacts
original Command
all attempts
commit records
before/after versions
audit facts
outbox facts
external responses
reconciliation queries/responses
AI/tool lineage
Evidence versions
governance versions
human Decisions
recovery Commands
recovery outcomes
```

No recovery operation deletes history to make the trace look clean.

---

# 80. Recovery and Immutability

Recovery cannot violate approved immutability.

Examples:

```text
Question.original_text
-> never overwritten by recovery

immutable Event
-> corrected by new Event/finding, not historical edit

consumed Evidence version
-> remains reconstructable

revoked HumanAuthorityBinding
-> remains revoked historically
```

---

# 81. Recovery and Direct Persistence

Direct database repair is not a governed recovery path.

An emergency/operator database mutation may be physically possible.

Architecturally:

```text
physical capability != legitimacy
```

If such a mutation occurs:

```text
classify as security/integrity event
reconstruct prior valid state
do not treat resulting row as legitimate merely because it exists
use governed recovery to establish legitimate current state where possible
```

11 must enforce credential separation and operational controls.

---

# 82. Recovery and External Reality

Canonical state and external reality may diverge.

Recovery must model both separately:

```text
CANONICAL CONSEQUENCE CERTAINTY
EXTERNAL CONSEQUENCE CERTAINTY
```

Examples:

```text
canonical COMMITTED + external UNKNOWN
canonical FAILED_PRECOMMIT + external PROVEN
canonical COMMITTED + external PROVEN_ABSENT
canonical INDETERMINATE + external PROVEN
```

No single local status may collapse these dimensions.

---

# 83. Canonical COMMITTED, External Failure

If canonical transition legitimately committed but downstream external action is proven absent:

```text
do not undo canonical state automatically
```

Determine whether upstream architecture already defines:

```text
required compensation
legal reversal
retry/reissue authority
```

If not:

```text
GAP / authorized human decision may be required
```

10 does not invent a domain reversal.

---

# 84. Canonical FAILED_PRECOMMIT, External Consequence Proven

This is a dangerous divergence.

Example:

```text
external action executed
local canonical commit failed
```

Recovery must:

```text
preserve external occurrence
remain explicit that canonical operation did not commit
block dependent consequence if legitimacy depends on consistency
route to reconciliation
```

SYSTEM_SERVICE may not simply mark local canonical state COMMITTED unless the approved architecture proves that completing the local record is a deterministic completion of an already legitimate operation and the recovery contract explicitly permits it.

Otherwise discretionary authority is required.

---

# 85. Audit/Outbox Correlation After Failure

Recovery reconstruction should preserve the 09 trace:

```text
command_id
-> attempt_id
-> commit_id
-> canonical record versions
-> audit_event_id
-> outbox_id
-> event_id
-> delivery attempts
```

Missing links create a provenance/reconstruction failure.

They do not automatically negate links that are independently proven.

---

# 86. Recovery Concurrency

Recovery competes with live operations.

Therefore every consequential Recovery Command must use:

```text
expected_versions
fresh BND-014 predicates
idempotency
```

If current state changed during recovery evaluation:

```text
FAILED_PRECOMMIT / REQUIRE fresh evaluation
```

If recovery commit certainty becomes unknown:

```text
INDETERMINATE
```

Recovery never receives a lock on legitimacy merely because it started first.

---

# 87. Recovery and Current Evidence

If Evidence changes after failure but before a new Recovery Command:

```text
historical Evidence remains reconstructable
current Recovery Command uses current required Evidence
```

A historical human Decision remains historical fact.

Whether a new Decision is required depends on approved state/authority/Evidence semantics.

10 does not silently invalidate or rewrite the Decision.

---

# 88. Recovery and Current Method

Where a recovery operation depends on a method-derived System transition:

```text
current approved method version must be proven
```

If method approval is unavailable/unresolved:

```text
fail closed
```

Historical method version remains provenance of the original operation.

---

# 89. Recovery and Workspace Scope

Recovery scope must equal the affected authoritative Workspace scope.

No recovery may:

```text
cross Workspace because records share correlation IDs
copy authority across Workspace
use external reconciliation data from another Workspace as target authority
merge failures from separate Workspaces into one consequential recovery Command
```

Cross-Workspace operational observability may exist later under security policy, but it does not create cross-Workspace domain authority.

---

# 90. Recovery and Human Identity

For discretionary human recovery:

```text
authenticated User identity
+
active relevant Workspace membership
+
current exact authority binding/source
```

must be proven.

A system operator's infrastructure identity is not a substitute for human domain identity.

---

# 91. Recovery and SYSTEM_SERVICE

SYSTEM_SERVICE is permitted only:

```text
bounded deterministic procedural recovery
approved System-derived operations
```

It cannot impersonate the original User.

It cannot inherit:

```text
DecisionAuthority
ExperimentDecisionAuthority
ActionDecisionAuthority
AssumptionInterpretationAuthority
QuestionSelectionAuthority
```

from the original Command.

---

# 92. Recovery and AI_PROCESSOR

AI_PROCESSOR remains separate from SYSTEM_SERVICE.

An AI tool call executed by a service does not convert AI recommendation into System-derived authority.

If AI proposes:

```text
"compensate X"
```

the proposal remains derived until the required human/System authority path independently permits the operation.

---

# 93. Recovery API Materialization Requirements

10 does not define endpoint syntax, but every future recovery API must map to:

```text
Query
or
CommandEnvelope
```

No endpoint may expose:

```text
PATCH /recovery/fix-state
POST /admin/force-commit
POST /recovery/replay-event-as-command
POST /recovery/restore-authority
```

as privileged bypass semantics.

Operational deterministic actions may be service operations only if they satisfy Section 31.

---

# 94. Recovery Query Semantics

Recovery queries may expose:

```text
failure correlation
RecoveryRecord
certainty classification
last proven valid state
current blocking dependencies
audit/outbox status
external reconciliation status
AI/tool lineage
```

A recovery Query does not mutate canonical state.

Query projection data must identify its consistency class.

---

# 95. Recovery Audit Requirements

Every consequential Recovery Command must audit:

```text
recovery_id
original failure correlation
recovery class
actor
authority source
human Decision where required
Evidence refs where required
before state/version
after state/version
external consequence reference where relevant
command_id
attempt_id
commit_id
result
```

Deterministic operational recovery should also be auditable where it affects reconstructability or integrity.

---

# 96. Recovery Failure Escalation

Escalation means:

```text
the current operation cannot proceed automatically
```

It does not mean:

```text
a higher-privilege operator may bypass
```

Escalation targets only approved authority/governance/security processes.

If no such process exists:

```text
GAP remains
```

---

# 97. New Gaps Exposed in 10

## GAP-10-001 Legal Domain Reversal Catalogue

**Status:** `[OPEN UPSTREAM STATE DEPENDENCY]`

03 does not define general reversal transitions for:

```text
Decision DECIDED
Experiment AUTHORIZED
QuestionSelection
Assumption interpretation
ACTION-related human authority
```

10 cannot invent them.

## GAP-10-002 Discretionary Recovery Authority Mapping

**Status:** `[OPEN CONDITIONAL UPSTREAM AUTHORITY DEPENDENCY]`

Many recovery choices can reuse existing target-specific 04 authority classes.

If a future recovery choice cannot map to an existing authority class:

```text
controlled reconstruction of 04 is required
```

No generic RecoveryAuthority is created.

## GAP-10-003 External Consequential Tool Recovery Contracts

**Status:** `[UNDERDEFINED, carries GAP-08-003 / GAP-08-012 / GAP-09-001]`

Unknown tools prevent tool-specific:

```text
idempotency
reconciliation
compensation
irreversibility
```

contracts.

## GAP-10-004 Backup Restore Authority and Operational Procedure

**Status:** `[DEFERRED TO 11 / IMPLEMENTATION]`

10 defines semantic quarantine/reconciliation.

It does not assign infrastructure restore privileges or technology.

## GAP-10-005 Recovery Algorithm Approval Governance

**Status:** `[UNDERDEFINED]`

Deterministic recovery requires approved/versioned algorithms.

Existing architecture does not yet define the governance process that approves recovery algorithm versions.

Until defined:

```text
only architecture-explicit deterministic operations are semantically permitted
production activation remains blocked where approval is material
```

## GAP-10-006 RecoveryRecord Retention

**Status:** `[UNDERDEFINED, coupled to 11 and existing retention gaps]`

Recovery history may contain:

```text
authority
Evidence
external responses
security-relevant data
```

Retention cannot be invented in 10.

## GAP-10-007 External Consequence Truth Source

**Status:** `[UNDERDEFINED PER INTEGRATION]`

Each external integration must define what response/query is authoritative enough to prove occurrence/non-occurrence.

## GAP-10-008 Post-Restore Lost-History Source

**Status:** `[UNDERDEFINED IMPLEMENTATION / SECURITY]`

Reconciliation after restore requires an independent source for post-restore-point history where local restored storage lost it.

10 defines the requirement, not the infrastructure.

## GAP-10-009 Recovery API Exposure / Operator Access Control

**Status:** `[DEFERRED TO 11]`

10 defines semantic authority.

11 must constrain physical access to recovery/admin surfaces.

---

# 98. Carried Gaps

10 preserves material upstream gaps, including:

```text
CONFLICT-001 InquiryGraph prototype scope
CONFLICT-007 Burst duration semantics
D1-D10

GAP-01-001 Tenant versus Workspace
GAP-01-002 Organization relation
GAP-01-003 Active-Burst AI observer/recorder
GAP-01-005 AI Gateway enforcement

GAP-02-001 User.role versus Workspace role
GAP-02-002 Question text/original_text
GAP-02-004 cluster recomputation identity
GAP-02-005 Evidence ownership
GAP-02-007 Journey ownership
GAP-02-008 Journey materialization

GAP-03-002 timer/pause semantics
GAP-03-003 Question-only enforcement
GAP-03-010 Decision Evidence sufficiency
GAP-03-011 Experiment Evidence sufficiency
GAP-03-018 primary Question replacement
GAP-03-019 Assumption WEAK threshold

GAP-04-001 collaborative selection policy
GAP-04-004 Session controller multiplicity
GAP-04-007 timer identity/trust
GAP-04-008 Method Approval Authority
GAP-04-013 Export Authority

GAP-05-001 Workspace root creation/succession
GAP-05-004 Governance record retention
GAP-05-005 Method version identity
GAP-05-007 Governance concurrency

GAP-06-004 direct persistence physical enforcement
GAP-06-005 AI Gateway bypass enforcement
GAP-06-007 discretionary recovery authority dependency

GAP-07-001 Assumption sufficiency
GAP-07-002 Insight validation authority
GAP-07-003 post-decision Evidence invalidation
GAP-07-004 Evidence deletion versus audit
GAP-07-005 reliability semantics
GAP-07-006 provenance retention
GAP-07-007 source snapshot
GAP-07-008 Evidence reuse
GAP-07-010 EvidenceRelation acceptance workflow
GAP-07-011 method-specific Evidence sufficiency

GAP-08-001 AI context policy
GAP-08-002 provider compatibility
GAP-08-003 consequential tool catalogue
GAP-08-005 context freshness
GAP-08-006 partial output
GAP-08-007 cost override authority
GAP-08-008 provider privacy mapping
GAP-08-009 prompt approval governance
GAP-08-010 operation-contract approval governance
GAP-08-012 tool partial success
GAP-08-013 Mode B/C Question Pool representation
GAP-08-014 Coach Mode persistence/scope

GAP-09-001 external tool idempotency contracts
GAP-09-002 human adoption relation shape
GAP-09-003 Mode B/C membership physical shape
GAP-09-004 retention materialization strategy
GAP-09-005 query consistency mapping
GAP-09-006 Workspace creation authority/bootstrap
GAP-09-007 Session participation join/leave authority
GAP-09-008 Challenge.status vocabulary
GAP-09-009 Question text/original_text materialization
GAP-09-010 primary selection replacement representation
GAP-09-011 Journey materialization
GAP-09-012 Evidence ownership/reuse physical model
GAP-09-013 method approval record activation
GAP-09-014 export artifact schema activation
```

10 semantically advances/owns recovery handling for prior:

```text
GAP-03-016 audit atomicity
GAP-03-017 cross-object commit atomicity
GAP-05-003 governance operation atomicity
GAP-06-001 commit concurrency/freshness
GAP-06-003 idempotency identity
GAP-06-006 replay side-effect isolation
GAP-06-009 audit failure commit coupling
GAP-09-015 Recovery Command Catalogue
```

without changing their upstream state/authority semantics.

---

# 99. Architectural Closures Introduced by 10

```text
AC-10-001 Recovery may restore/reconcile legitimacy, never create it
AC-10-002 Explicit recovery consequence-certainty classes
AC-10-003 Deterministic failure-state reconstruction contract
AC-10-004 LAST_PROVEN_VALID_STATE definition
AC-10-005 Deterministic recovery consumes bounded existing SYSTEM_DERIVED model, no new authority class
AC-10-006 Human creates discretionary recovery Decision, not approval of engine decision
AC-10-007 Least-permissive governance interpretation under uncertainty
AC-10-008 Post-restore dependency-scoped quarantine
AC-10-009 RecoveryRecord operational representation
AC-10-010 Consequential recovery uses governed CommandEnvelope
AC-10-011 Rollback separated into precommit rollback, canonical reversal, compensation and infrastructure restore
AC-10-012 Compensation is a new governed consequence
AC-10-013 External consequence certainty is separate from canonical consequence certainty
AC-10-014 INDETERMINATE recovery itself requires reconciliation
AC-10-015 Recovery idempotency prevents duplicate compensation/reversal
AC-10-016 Audit repair cannot legitimize domain mutation
AC-10-017 Outbox delivery retry cannot repeat domain consequence
AC-10-018 Projection rebuild is deterministic reconstruction only
AC-10-019 Backup restore cannot resurrect revoked authority
AC-10-020 Recovery blocking propagates by dependency, not globally by default
AC-10-021 RecoveryRecord outcomes remain separate from 03 transition outcomes
AC-10-022 Direct database repair cannot establish legitimacy
AC-10-023 Historical authority remains provenance, not post-failure authority
AC-10-024 Historical Evidence remains reconstructable, current consequence uses current Evidence rules
AC-10-025 Irreversible occurrence remains historical even after compensation
```

---

# 100. Falsification Suite

For each attack, 10 evaluates:

```text
ENTRY PATH
FAILURE CLASS
LAST PROVEN VALID STATE
AUTHORITY REQUIREMENT
RECOVERY CLASS
EXPECTED BOUNDARY
EXPECTED RESULT
CAN UNAUTHORIZED CONSEQUENCE OCCUR?
```

---

# 101. FALS-10-001 Admin Changes Decision State

## Entry Path

```text
admin SQL
-> Decision state edited to DECIDED
```

## Failure Class

```text
F-SEC
F-PERS
F-PROV
```

## Last Proven Valid State

Last Decision state with valid 03 transition + human Decision Authority + CommitUnit.

## Authority Requirement

DecisionAuthority through normal 04/05 path.

## Recovery Class

RECONCILIATION, then legal recovery if available.

## Expected Boundary

```text
BND-007
BND-006
BND-014
BND-018
```

## Expected Result

Direct row is not legitimate state.

## Unauthorized Consequence?

```text
NO
```

provided 11 enforces write-path controls and 10 legitimacy reconstruction is used.

---

# 102. FALS-10-002 Operator Replays Old Event to Repeat Action

Entry:

```text
Event replay -> side-effect handler
```

Failure:

```text
F-SEC / replay misuse
```

LPVS:

Original committed state.

Authority:

New action requires current authority.

Recovery:

None via replay.

Boundary:

```text
BND-015
BND-017
BND-018
BND-014
```

Result:

```text
DENY side-effect execution
projection reconstruction only
```

Unauthorized consequence:

```text
NO
```

---

# 103. FALS-10-003 Retry After Authority Revocation

Entry:

```text
authorized Command
-> FAILED_PRECOMMIT
-> binding revoked
-> retry
```

Failure:

```text
F-AUTH
```

LPVS:

Pre-command canonical state.

Authority:

Current binding required.

Recovery:

RC-06 RETRY.

Boundary:

```text
BND-005
BND-014
```

Result:

```text
DENY / FAILED_PRECOMMIT
```

Unauthorized consequence:

```text
NO
```

---

# 104. FALS-10-004 Blind Retry of INDETERMINATE External Action

Entry:

```text
timeout -> unknown external consequence -> retry
```

Failure:

```text
F-EXT
F-NET
```

LPVS:

Last proven canonical/external pair.

Authority:

Current authority if reissue later becomes legal.

Recovery:

RC-02 reconciliation first.

Boundary:

```text
BND-017
BND-018
```

Result:

```text
BLOCK RETRY
```

Unauthorized consequence:

```text
NO
```

---

# 105. FALS-10-005 Backup Restore Resurrects Revoked Authority

Entry:

```text
restore old DB -> binding ACTIVE
```

Failure:

```text
F-GOV
F-SEC
```

LPVS:

Last governance state reconstructable including proven revocation.

Authority:

No recovery authority can reactivate old binding.

Recovery:

RB-04 + reconciliation.

Boundary:

BND-018, then normal governance boundary.

Result:

```text
old binding remains unavailable
```

Unauthorized consequence:

```text
NO
```

---

# 106. FALS-10-006 Projection Used as Recovery Truth

Entry:

```text
projection says Session=ACTION
-> recovery writes canonical ACTION
```

Failure:

```text
F-PERS / projection misuse
```

LPVS:

Canonical proven state.

Authority:

Normal transition authority.

Recovery:

Projection rebuild only.

Boundary:

```text
BND-014
BND-018
```

Result:

```text
DENY canonical mutation
```

Unauthorized consequence:

```text
NO
```

---

# 107. FALS-10-007 AI Chooses Compensation

Entry:

```text
AI recommends compensate X
-> recovery service executes
```

Failure:

```text
F-AUTH
```

LPVS:

State before compensation.

Authority:

Target-specific current human authority/Decision where required.

Recovery:

RC-03.

Boundary:

```text
BND-010
BND-006
BND-018
BND-014
```

Result:

```text
DENY until human-authoritative path exists
```

Unauthorized consequence:

```text
NO
```

---

# 108. FALS-10-008 AI Marks External Action Failed on Timeout

Entry:

```text
provider timeout
-> AI labels failed
-> retry
```

Failure:

```text
F-NET
F-EXT
F-AITOOL
```

LPVS:

External consequence remains unknown.

Authority:

None created by AI classification.

Recovery:

Reconciliation.

Boundary:

BND-017/BND-018.

Result:

```text
INDETERMINATE remains
```

Unauthorized consequence:

```text
NO
```

---

# 109. FALS-10-009 Fabricated Audit After Unauthorized Mutation

Entry:

```text
unauthorized DB write
-> manual AuditEvent inserted
```

Failure:

```text
F-AUD
F-SEC
```

LPVS:

Last legitimately committed state.

Authority:

Normal target authority.

Recovery:

Reconciliation/security.

Boundary:

BND-015/BND-018.

Result:

```text
audit insertion does not legitimize mutation
```

Unauthorized consequence:

```text
NO
```

---

# 110. FALS-10-010 Partial Governance Grant Treated Active

Entry:

```text
binding row created
-> audit/dependent bundle uncertain
-> service treats ACTIVE
```

Failure:

```text
F-GOV
F-PCOM
```

LPVS:

Last proven governance state.

Authority:

WORKSPACE_GOVERNANCE_RIGHT for any new grant.

Recovery:

Reconciliation.

Boundary:

BND-018 + BND-005/BND-014.

Result:

```text
grant unavailable
```

Unauthorized consequence:

```text
NO
```

---

# 111. FALS-10-011 Uncertain Revocation Treated Active

Entry:

```text
revoke attempt uncertain
-> old authority used
```

Failure:

F-GOV.

LPVS:

Historical binding plus unresolved revocation.

Authority:

Unavailable under least-permissive rule.

Recovery:

Reconciliation.

Boundary:

BND-005/BND-018/BND-014.

Result:

DENY.

Unauthorized consequence:

NO.

---

# 112. FALS-10-012 Invalidated Evidence Version Silently Reused

Entry:

```text
old Evidence STRUCTURALLY_VALID
-> later INVALIDATED
-> recovery reuses old status as current
```

Failure:

```text
F-EVID
```

LPVS:

Historical state remains reconstructable.

Authority:

Current target authority + current Evidence rules.

Recovery:

Fresh Evidence evaluation.

Boundary:

BND-013/BND-018/BND-014.

Result:

```text
old Evidence remains historical, cannot satisfy current predicate if invalid
```

Unauthorized consequence:

NO.

---

# 113. FALS-10-013 Human Decision Rolled Back Because API Failed

Entry:

```text
Decision DECIDED legitimately
-> downstream API fails
-> recovery sets Decision UNDER_CONSIDERATION
```

Failure:

F-EXT/F-PERS.

LPVS:

DECIDED remains legitimate.

Authority:

Legal reversal transition would be required.

Recovery:

No RB-02 path unless 03 defines it.

Boundary:

BND-007/BND-018.

Result:

```text
DENY reversal
GAP-10-001
```

Unauthorized consequence:

NO.

---

# 114. FALS-10-014 Experiment AUTHORIZED Erased After Execution Failure

Entry:

```text
Experiment AUTHORIZED
-> start execution fails
-> recovery deletes authorization
```

Failure:

F-EXT/F-PERS.

LPVS:

AUTHORIZED.

Authority:

Legal reversal required if desired.

Recovery:

Retry/reconciliation, not silent reversal.

Boundary:

BND-007/BND-018.

Result:

DENY erasure.

Unauthorized consequence:

NO.

---

# 115. FALS-10-015 Event Delivery Retry Repeats Domain Consequence

Entry:

```text
outbox redelivery
-> consumer repeats originating mutation
```

Failure:

F-OUT.

LPVS:

Original COMMITTED state.

Authority:

New consequence would need new Command/current authority.

Recovery:

Outbox delivery retry only.

Boundary:

BND-015/BND-017/BND-014.

Result:

No repeat.

Unauthorized consequence:

NO.

---

# 116. FALS-10-016 Recovery Service Inherits Original User Authority

Entry:

```text
original DecisionAuthority user
-> failure
-> recovery worker executes as if user
```

Failure:

F-AUTH.

LPVS:

Last proven state.

Authority:

Current human binding required for discretionary consequence.

Recovery:

RC-01 only if deterministic, otherwise RC-07.

Boundary:

BND-005/BND-018/BND-014.

Result:

DENY impersonated authority.

Unauthorized consequence:

NO.

---

# 117. FALS-10-017 Recovery Endpoint Bypasses BND-014

Entry:

```text
POST /recovery/fix
-> direct repository write
```

Failure:

F-SEC/F-PERS.

LPVS:

Last legitimate state.

Authority:

Normal.

Recovery:

None through bypass.

Boundary:

BND-018 + BND-014.

Result:

Architecturally invalid.

Unauthorized consequence:

NO, contingent on 11 physical enforcement.

---

# 118. FALS-10-018 RecoveryRecord Used as Authority Token

Entry:

```text
RecoveryRecord.required_authority_ref exists
-> service assumes authorized
```

Failure:

F-AUTH.

LPVS:

Unchanged.

Authority:

Fresh current binding/source required.

Recovery:

Normal.

Boundary:

BND-005/BND-014/BND-018.

Result:

DENY.

Unauthorized consequence:

NO.

---

# 119. FALS-10-019 Compensation Erases Original Occurrence

Entry:

```text
compensation succeeds
-> original external action removed from history
```

Failure:

F-PROV/F-AUD.

LPVS:

Includes original occurrence plus compensation.

Authority:

Compensation authority does not authorize history deletion.

Recovery:

RC-03.

Boundary:

BND-015/BND-018.

Result:

Preserve both.

Unauthorized consequence:

NO.

---

# 120. FALS-10-020 External Side Effect Called Rolled Back When Only Local State Changed

Entry:

```text
external message sent
-> local row restored
-> UI says rolled back
```

Failure:

F-EXT/F-PROV.

LPVS:

External occurrence proven.

Authority:

Compensation if available.

Recovery:

Reconciliation/compensation.

Boundary:

BND-018.

Result:

External occurrence remains.

Unauthorized consequence:

NO.

---

# 121. FALS-10-021 Restored Database Accepted Without Reconciliation

Entry:

```text
backup restore -> reopen writes immediately
```

Failure:

F-SEC/F-GOV/F-PERS.

LPVS:

Must be reconstructed across restore point.

Authority:

Current authority after reconciliation.

Recovery:

RB-04 + RC-02.

Boundary:

BND-018/BND-014.

Result:

Dependency-scoped quarantine.

Unauthorized consequence:

NO.

---

# 122. FALS-10-022 Duplicate Compensation from Retry

Entry:

```text
compensation request times out
-> automatic retry
-> two compensations
```

Failure:

F-REC/F-EXT.

LPVS:

Compensation consequence unknown.

Authority:

Current authority does not permit duplicate consequence.

Recovery:

Reconcile compensation first.

Boundary:

BND-017/BND-018.

Result:

No blind retry.

Unauthorized consequence:

NO.

---

# 123. FALS-10-023 AI Generation Retry Overwrites Prior Derived Artifact

Entry:

```text
validated AI artifact persisted
-> generation retry
-> same row overwritten
```

Failure:

F-AIGEN/F-PROV.

LPVS:

Prior derived artifact remains reconstructable.

Authority:

Canonicalization contract.

Recovery:

New AIGeneration/new artifact version.

Boundary:

BND-010/BND-014.

Result:

No silent overwrite.

Unauthorized consequence:

NO.

---

# 124. FALS-10-024 Provider Fallback Reuses Prior Validation Proof

Entry:

```text
provider A fails
-> provider B fallback
-> reuse A AI_VALIDATION_PROOF
```

Failure:

F-AIVAL/F-PROVDR.

LPVS:

No accepted fallback output.

Authority:

No proof inheritance.

Recovery:

New generation + validation.

Boundary:

BND-009/BND-010.

Result:

DENY reuse.

Unauthorized consequence:

NO.

---

# 125. FALS-10-025 Security Recovery Trusts Cached Authority

Entry:

```text
suspected compromise
-> cache says binding ACTIVE
-> recovery executes
```

Failure:

F-SEC/F-AUTH.

LPVS:

Must use authoritative current governance reconstruction.

Authority:

Cached value insufficient.

Recovery:

Security + reconciliation.

Boundary:

BND-005/BND-018/BND-014.

Result:

Fail closed.

Unauthorized consequence:

NO.

---

# 126. Falsification Result

**RESULT: PASS WITH EXPLICIT DOWNSTREAM PHYSICAL-ENFORCEMENT DEPENDENCIES**

No falsification path requires a new human authority class or new domain transition to prevent unauthorized consequence.

Where a desired recovery would require an undefined reversal or authority:

```text
the recovery path stops
the GAP is exposed
no consequence is permitted
```

Physical enforcement dependencies remain for 11, especially:

```text
database credential separation
recovery/admin surface access control
backup/restore security
audit integrity protection
broker/replay isolation
AI Gateway bypass prevention
forensic integrity
```

---

# 127. Recursive Validation Against 00

**PASS**

10 preserves:

```text
Human Decision Authority
Governance Before Consequence
traceability
Question immutability
human/AI provenance
auditability
```

Failure never becomes an exception to these principles.

No 00 reconstruction required.

---

# 128. Recursive Validation Against 01

**PASS**

10 preserves boundary separation:

```text
identity != authority
persistence != authority
AI != human
telemetry != provenance
external provider != product authority
recovery cannot create invalid canonical transition
```

No 01 reconstruction required.

---

# 129. Recursive Validation Against 02

**PASS**

10 introduces only `RecoveryRecord` as an OPERATIONAL_RECORD.

It does not create a new domain Thing.

It preserves:

```text
THING != RELATION != STATE != EVENT != AUTHORITY != EVIDENCE != PROJECTION != CONFIGURATION
```

No 02 reconstruction required.

---

# 130. Recursive Validation Against 03

**PASS**

10 preserves exactly:

```text
DENIED
FAILED_PRECOMMIT
COMMITTED
INDETERMINATE
```

No fifth transition outcome is added.

No new Session, Burst, Assumption, Experiment or Decision transition is added.

Desired reversal without a legal 03 transition becomes GAP-10-001.

No 03 reconstruction required.

---

# 131. Recursive Validation Against 04

**PASS**

10 consumes existing authority classes only.

It does not create:

```text
RecoveryAuthority
RecoveryAdmin
SuperuserOverride
OperatorDecisionRight
```

Human discretionary recovery uses the authority class of the actual domain/governance decision being made.

No 04 reconstruction required at this stage.

`GAP-10-002` explicitly identifies the condition that would require future controlled reconstruction.

---

# 132. Recursive Validation Against 05

**PASS**

10 preserves:

```text
revoked binding terminal
least-permissive uncertainty
governance cleanup
SYSTEM_DERIVED procedural authority
AI governance exclusion
```

It does not reactivate authority during recovery.

No 05 reconstruction required.

---

# 133. Recursive Validation Against 06

**PASS**

10 materializes BND-018 and preserves:

```text
BND-014 final commit
BND-015 audit/event semantics
BND-017 duplicate/indeterminate control
BND-018 recovery no exemption
```

Recovery re-enters normal boundaries.

No 06 reconstruction required.

---

# 134. Recursive Validation Against 07

**PASS**

10 preserves:

```text
Evidence version history
SourceReference
ClaimAnchor
EvidenceRelation
validation states
supersession/invalidation
EvidenceSetReference
```

It does not create Evidence sufficiency or validation authority.

No 07 reconstruction required.

---

# 135. Recursive Validation Against 08

**PASS**

10 preserves AIGeneration lifecycle and fallback rules.

It preserves:

```text
AI_VALIDATION_PROOF != Evidence
AI tool capability != authority
provider fallback = new generation + new provenance + new validation
AI proposal != recovery decision
```

No 08 reconstruction required.

---

# 136. Recursive Validation Against 09

**PASS**

10 preserves:

```text
DATA != AUTHORITY
COMMAND != EVENT
EVENT != COMMAND
EVENT != AUTHORITY
DATABASE WRITE != LEGITIMATE TRANSITION
EARLIER ALLOW != COMMIT AUTHORITY
IDEMPOTENCY != AUTHORIZATION
PROJECTION != CANONICAL STATE
CACHE != AUTHORITATIVE STATE
```

It consumes:

```text
CommandEnvelope
AuthorityContextReference
IdempotencyRecord
CommitUnit
EventEnvelope
QueryEnvelope
commit-time freshness
optimistic concurrency semantics
transaction/outbox semantics
event replay restrictions
write-path convergence
direct-persistence non-bypass
AI operational materialization
Evidence/provenance materialization
audit/commit correlation
```

No 09 reconstruction required.

---

# 137. Recursive Invariant Validation

```text
FAILURE -> does not create authority                         PASS
RECOVERY -> does not bypass governance                      PASS
ROLLBACK -> does not erase history                          PASS
COMPENSATION -> new governed consequence                    PASS
RETRY -> respects idempotency and current authority         PASS
INDETERMINATE -> blocks dependent consequence               PASS
AI -> proposal only where human recovery decision required  PASS
EVIDENCE -> preserved/versioned                             PASS
GOVERNANCE -> least permissive under uncertainty            PASS
EVENT -> post-commit fact, not replay authority              PASS
DATABASE RESTORE -> not automatically legitimate state      PASS
AUDIT -> reconstructs, never legitimizes retroactively      PASS
```

---

# 138. Failure Taxonomy Findings

The architecture requires consequence certainty, not merely error type.

The most important distinction is:

```text
technical failure classification
!=
proof of canonical/external consequence
```

Network, provider, persistence and audit errors can each map to different 03 outcomes depending on what is proven.

No generic "failed" flag is sufficient.

---

# 139. Last-Proven-Valid-State Findings

`LAST_PROVEN_VALID_STATE` is now closed as a reconstruction concept.

It is:

```text
legitimacy-proven
causally reconstructable
version-aware
authority-aware
Evidence-aware
audit/provenance-aware
```

It is not "last row wins".

---

# 140. Recovery Authority Findings

Recovery creates no new authority class.

Three cases exist:

```text
deterministic technical recovery
-> bounded SYSTEM_DERIVED procedural execution

new consequential operation with existing target-specific authority
-> current 04/05 authority

new discretionary choice with no approved authority path
-> GAP
-> STOP
```

Admin/operator identity never fills the gap.

---

# 141. Deterministic Recovery Findings

Deterministic recovery is permitted only when the legitimate result is uniquely determined and already authorized by architecture.

It can repair:

```text
projection
outbox delivery
derived index
deterministic reconstruction
certain technical incompleteness where completion semantics are approved
```

It cannot make domain judgments.

---

# 142. Discretionary Recovery Findings

Discretionary recovery is explicitly separated from technical recovery.

The engine may reconstruct and present.

The authorized human creates the decision.

This prevents a recovery service from becoming a hidden decision authority.

---

# 143. Rollback Findings

"Rollback" is now decomposed into:

```text
precommit transaction rollback
canonical state reversal
compensating transition
infrastructure restore
```

Only the first is inherently technical.

Canonical reversal requires a legal upstream transition.

Infrastructure restore requires post-restore reconciliation.

---

# 144. Compensation Findings

Compensation is a new consequence.

It requires:

```text
new Command
current authority
current Decision/Evidence where required
boundaries
fresh commit
idempotency
audit
```

It preserves the original occurrence.

---

# 145. External Consequence Findings

Canonical and external consequence certainty are independent dimensions.

External timeout is not failure proof.

Unknown external consequence remains INDETERMINATE until reconciled.

Tool-specific safe retry remains blocked by `GAP-10-003` where idempotency/reconciliation contracts are absent.

---

# 146. Governance Recovery Findings

Governance uncertainty is least-permissive.

A backup, partial bundle or stale row cannot resurrect/grant authority.

Revoked bindings remain historical and terminal.

Any new grant uses normal governance.

---

# 147. AI Recovery Findings

AI may analyze and propose.

AI cannot:

```text
choose compensation
choose reversal
choose accepted external consequence
grant authority
reuse validation proof across fallback
overwrite prior derived artifact silently
```

Unknown AI-tool side effect routes to reconciliation.

---

# 148. Evidence / Provenance Recovery Findings

Historical Evidence and provenance are preserved exactly enough to reconstruct historical decisions.

New recovery consequences use current Evidence rules.

Recovery does not rewrite historical Decision inputs or manufacture missing proof.

---

# 149. Audit / Outbox Recovery Findings

Audit durability is part of consequence certainty.

Audit projection failure is not audit-record absence.

Durable outbox delivery may be retried without repeating domain consequence.

Audit insertion after unauthorized mutation cannot legitimize it.

---

# 150. Backup / Restore Findings

Backup restore is infrastructure recovery only.

Post-restore reconciliation is mandatory where history may have moved beyond the restore point.

Authority revocations, external consequences and Evidence changes must not be lost semantically because bytes moved backward.

---

# 151. Idempotency Findings

Recovery idempotency extends 09:

```text
same logical recovery Command
+
new attempt identity
+
stable recovery correlation
+
expected versions
```

prevents duplicate compensation/reversal.

INDETERMINATE recovery cannot be blindly retried.

---

# 152. Baseline Blockers Relevant After 10

10 does not remove upstream prototype blockers.

Material blockers include:

```text
GAP-04-013 Export Authority
GAP-04-008 Method Approval Authority where method-derived automation is used
GAP-05-001 Workspace root creation/succession
GAP-04-001 collaborative selection policy if multi-selector prototype
CONFLICT-007 / GAP-04-007 timer trust if automatic Burst completion is used
GAP-09-006 Workspace creation authority/bootstrap
GAP-09-007 Session participation join/leave authority
retention/deletion policy and materialization for production
AI Gateway physical bypass prevention
direct persistence physical enforcement
```

New 10 blockers where affected capabilities are in scope:

```text
GAP-10-003 external consequential tool recovery contracts
GAP-10-005 recovery algorithm approval governance
GAP-10-009 recovery/admin surface physical access control
GAP-10-001 if prototype requires reversal of human-authoritative state
```

---

# 153. Upstream Contradictions

**NONE FOUND**

10 does not require reconstruction of 00 through 09.

Where upstream semantics are absent, 10 stops the affected recovery path and exposes a GAP.

---

# 154. Readiness for 11

11 may now own:

```text
Security
Privacy
Observability
physical canonical-write enforcement
database credential separation
recovery/admin surface access control
backup/restore operational security
audit integrity protection
forensic preservation
AI Gateway bypass prevention
broker/replay physical isolation
security incident controls
retention/privacy enforcement where architecture permits
observability for failure/recovery state
```

11 must preserve:

```text
security control != domain authority
operator access != recovery authority
observability != provenance
backup access != authority restoration right
incident response != human Decision Right
```

10 provides 11 with explicit security-sensitive recovery requirements.

## READINESS RESULT

```text
READY FOR HUMAN REVIEW
```

No 11 work is authorized by this document.

---

# 155. Stop Gate

**STOP CONDITION REACHED**

Await:

```text
HUMAN_REVIEW::10_APPROVED
```

and a separate explicit GO for 11.

No code implementation has begun.

No Architecture Baseline has been frozen.
