⸻

title: “NQUIRY — Claude Code Field Execution Master”
document_id: “NQUIRY-CLAUDE-CODE-FIELD-EXECUTION-MASTER”
version: “1.0”
repository: “SYNTX-SYSTEM/NQUIRY”
mode:

* FIELD_SYSTEM_ENGINEERING
* TEST_DRIVEN_IMPLEMENTATION
* RECURSIVE_DEEPSWEEP
* INVERSE_DEEPSWEEP
* FIRST_BROKEN_RELATION
* LOCAL_FIRST
* PROTOTYPE_TO_PRODUCTION
* COMPLETE_BACKEND
* COMPLETE_SEMIOTIC_FRONTEND
    field_count: 13
    commit_mode: “HUMAN_REVIEW_REQUIRED”
    implementation_unit: “FIELD”
    internal_execution_unit: “WORK_UNIT”

⸻

NQUIRY

CLAUDE CODE FIELD EXECUTION MASTER

0. ROLE

You are implementing the existing NQUIRY architecture.

You are not designing a new product.

You are not free to reinterpret NQUIRY because a different implementation would be easier.

You are not executing a list of technical tickets.

You are materializing semantic Fields.

The governing law is:

FREEDOM OF FORM
≠
FREEDOM OF SEMANTICS

Inside a Field:

TECHNICAL AUTONOMY

At the Field boundary:

ARCHITECTURAL CONSTRAINT

Across Fields:

RECURSIVE VALIDATION

After every Work Unit:

UPWARD RECURSIVE TESTING

After every completed Field:

FULL FIELD PROOF
→ REVIEW REPORT
→ STOP BEFORE COMMIT

No commit occurs before human review.

⸻

1. PRIMARY TARGET

Transform the actual current NQUIRY repository into the strongest coherent local and production-capable implementation permitted by the authoritative architecture and resolved human decisions.

The product must materially support:

CHALLENGE
→ PROTECTED HUMAN QUESTION BURST
→ VERBATIM HUMAN QUESTIONS
→ POST-BURST AI
→ CLUSTERING
→ PERSPECTIVES
→ ASSUMPTIONS
→ REFLECTION
→ QUESTION SELECTION
→ CATALYTIC QUESTION
→ INVESTIGATION
→ EVIDENCE
→ INSIGHT
→ EXPERIMENT
→ HUMAN DECISION
→ AUTHORIZED ACTION / CONSEQUENCE
→ LEARNING
→ CHANGED FIELD
→ NEW QUESTION

NQUIRY must never collapse into:

PROBLEM
→ AI ANSWER

⸻

2. REPOSITORY AUTHORITY LAW

Before beginning any Field:

READ CURRENT REPOSITORY
→ READ AUTHORITATIVE ARCHITECTURE
→ READ CURRENT PROOF REPORTS
→ READ CURRENT RUNTIME RUNBOOK
→ INSPECT ACTUAL IMPLEMENTATION

Never treat this execution document as permission to overwrite more authoritative repository architecture.

Use this hierarchy:

AUTHORITATIVE PRODUCT / ARCHITECTURE
>
REVIEWED FIELD ARCHITECTURE
>
CURRENT IMPLEMENTATION CONTRACT
>
IMPLEMENTATION FORM

Code does not redefine architecture.

If code contradicts architecture:

CODE IS NOT AUTOMATICALLY RIGHT

If architecture is genuinely ambiguous:

STOP
→ HUMAN_DECISION_REQUIRED

⸻

3. CURRENT BASELINE MUST BE RECONSTRUCTED FIRST

At the start of execution verify the actual repository state.

Expected current baseline includes:

PKG-00 .. PKG-32
→ materialized
FastAPI
→ present
PostgreSQL
→ present
Alembic
→ present
Next.js
→ present
local verified login/session
→ present
limited real HTTP surface
→ present
broad application-layer capability
→ present
complete browser reachability
→ absent
real AI provider
→ absent / conditional
continuous production worker loop
→ absent
exact durable EventEnvelope reconstruction
→ incomplete
legitimate first Workspace governance root
→ unresolved unless a newer authoritative decision exists

Do not blindly assume this snapshot remains accurate.

Reconstruct current reality from HEAD before implementation.

⸻

4. FIELD GRANULARITY LAW

A Field is not:

a file
a function
a package
a migration
an endpoint
a React component
a screen
a test class

A Field is:

THE LARGEST SEMANTICALLY COHERENT ENGINEERING SPACE
THAT CAN BE MATERIALIZED AND FALSIFIED
UNDER ONE STABLE SEMANTIC REGIME

Within a Field Claude Code may create Work Units.

Example:

FIELD F03
PROTECTED HUMAN QUESTION FIELD

may internally contain:

WU-01 Burst state behavior
WU-02 timer
WU-03 Question persistence
WU-04 capture API
WU-05 provenance projection
WU-06 active Burst UI
WU-07 multi-human rendering
WU-08 contamination tests

These are:

WORK UNITS

not separately human-gated Fields.

Keep Work Units technically manageable.

Keep Fields semantically large.

⸻

5. SPEED LAW

We want deep proof without making implementation unnecessarily slow.

Therefore:

AFTER EVERY WORK UNIT

Do not run the entire repository test matrix blindly.

Run the Recursive Upward Test Ladder.

AFTER EVERY FIELD

Run:

complete affected regression
+
global architecture/static gates
+
full backend suite where feasible
+
full frontend suite where applicable
+
runtime proof
+
browser proof where human-visible

This gives:

FAST LOCAL FEEDBACK
+
SYSTEMIC VALIDATION

without:

FULL SUITE
after every tiny edit

⸻

6. NON-COLLAPSE LAWS

Preserve globally:

AUTHENTICATION
≠
AUTHORITY
MEMBERSHIP
≠
AUTHORITY
ROLE
≠
AUTHORITY
UI AFFORDANCE
≠
AUTHORITY
AI
≠
HUMAN
AI
≠
HUMAN AUTHORITY
AI
≠
HUMAN DECISION
AI CONFIDENCE
≠
EVIDENCE
PROVIDER CONNECTION
≠
PROVIDER ELIGIBILITY
EVIDENCE
≠
TRUTH
QUESTION SELECTION
≠
ANSWER
INSIGHT
≠
UNIVERSAL TRUTH
EXPERIMENT COMPLETE
≠
HYPOTHESIS TRUE
COMMAND
≠
EVENT
EVENT
≠
COMMAND
PROJECTION
≠
CANONICAL STATE
PROJECTION
≠
AUTHORITY
LOG
≠
AUDIT
DECISION
≠
EXECUTION
RECOVERY
≠
AUTHORITY
RESTORE
≠
LEGITIMACY
FIXTURE
≠
PRODUCTION PROOF
MOCK
≠
EXTERNAL ELIGIBILITY
LOCAL EXECUTABLE
≠
PRODUCTION ACCEPTED

⸻

7. GLOBAL TEST-FIRST LAW

Before implementing a Work Unit answer:

WHAT MUST BECOME TRUE?
WHAT MUST REMAIN IMPOSSIBLE?
WHAT EXISTING RELATIONS CAN THIS CHANGE?
WHAT WOULD FALSIFY THE WORK?

Then:

WRITE TESTS FIRST

Expected sequence:

TEST
→ EXPECTED FAILURE
→ IMPLEMENT MINIMUM COHERENT CHANGE
→ TEST
→ RECURSIVE UPWARD TEST
→ REPORT

Do not write implementation and then invent tests that merely agree with it.

⸻

8. RECURSIVE UPWARD TEST LADDER

This is mandatory after every Work Unit.

The purpose is:

LOCAL CHANGE
→ test local truth
→ test relations above it
→ test affected Field
→ test affected system boundaries

Use the following ladder.

⸻

L0 — DIRECT TEST

Run the smallest tests directly targeting the changed behavior.

Examples:

specific pytest test/module
specific Vitest test
specific contract test
specific state-machine test

If L0 fails:

STOP WORK UNIT

Fix the direct relation first.

⸻

L1 — OWNING MODULE / PACKAGE

Test the entire package/module containing the change.

Examples:

domain package
authority package
AI Gateway package
frontend component area
worker package

Purpose:

LOCAL CHANGE
→ surrounding local invariants

⸻

L2 — RELATION TESTS

Identify everything the changed element depends on and everything that depends on it.

Test those relations.

Examples:

authority
↔ boundary
QuestionBurst
↔ Question
Evidence
↔ Assumption
CommitUnit
↔ Audit
↔ Event
Event
↔ Worker
↔ Projection
API view model
↔ Frontend

This step is mandatory.

Do not rely only on the owning package.

⸻

L3 — FIELD INTEGRATION TEST

Run the integration tests covering the complete current Field.

Example:

Question capture change
→ run full Protected Human Question Field integration

not merely:

Question repository tests

⸻

L4 — ADJACENT FIELD REGRESSION

Run tests for Fields materially affected upstream or downstream.

Example:

Question provenance change
→ F03 Question Field
→ F04 AI Context
→ F05 Sensemaking
→ F12 Frontend provenance

Only affected adjacent Fields are required after every Work Unit.

Do not run unrelated product areas without cause.

⸻

L5 — GLOBAL INVARIANT GATES

Run architecture/static gates affected by the change.

At minimum when relevant:

architecture dependency gate
provider SDK import gate
test-only import gate
ruff
mypy
TypeScript typecheck
lint

⸻

L6 — RUNTIME SMOKE

If the Work Unit changes:

API
database
migration
worker
authentication
frontend interaction

run the smallest real runtime proof possible.

Examples:

real PostgreSQL integration
FastAPI request
migration verification
worker consumes test Event
Next.js page loads against real API

⸻

L7 — BROWSER SEMANTIC PROOF

Mandatory for human-visible Work Units.

Use real browser interaction where appropriate.

Validate:

rendered state
actual server interaction
keyboard behavior
loading
failure
authority affordance
provenance
responsive state

For a purely backend Work Unit without human-visible consequences, L7 may be NOT_APPLICABLE.

⸻

L8 — FIELD-END FULL REGRESSION

Run only after the complete Field is materially closed.

Includes:

all Field tests
all affected Field regressions
global static/architecture gates
backend regression
frontend regression where affected
real runtime proof
real browser proof

F13 additionally runs the full-system suite.

⸻

9. RECURSIVE DEEPSWEEP AFTER EVERY WORK UNIT

After tests pass, ask:

WHAT CHANGED BECAUSE THIS CHANGED?

Reinspect materially affected:

Domain
Relations
State
Authority
Governance
Boundaries
Evidence
AI
Persistence
Audit
Events
Workers
Projections
Recovery
Security
API
Frontend
Tests
Documentation
Runtime

If a new relation changes the interpretation of an earlier layer:

RETURN UPSTREAM
→ reconstruct
→ rerun tests

⸻

10. INVERSE DEEPSWEEP AFTER VISIBLE OR CONSEQUENTIAL WORK

When a Work Unit creates a visible or consequential effect, walk backwards from that effect.

Example:

VISIBLE DECISION
← DecisionView
← canonical Decision
← Commit
← Decision Boundary
← current Decision Authority
← governance ancestry
← membership
← Workspace
← verified identity

Example:

VISIBLE AI CLUSTER
← cluster semantic projection
← derived cluster
← AIGeneration
← AI Gateway
← approved AI operation
← frozen human Question set
← completed protected Burst

Example:

VISIBLE EVIDENCE SUPPORT
← EvidenceRelation
← Evidence version
← provenance
← Source
← claim target

If the inverse chain breaks:

WORK UNIT FAIL

Do not hide the break downstream.

⸻

11. FIRST BROKEN RELATION PROTOCOL

When anything fails:

LOCAL SYMPTOM
→ WALK UPSTREAM
→ FIND FIRST BROKEN RELATION
→ FIND AUTHORITATIVE HOME
→ FIX MINIMUM LEGITIMATE UPSTREAM LAYER
→ PROPAGATE DOWNSTREAM
→ RETEST

Never:

downstream workaround
→ semantic ambiguity remains hidden

⸻

12. NO-COMMIT REVIEW LAW

Claude Code must not commit automatically during Field implementation.

Default state:

CHANGES
→ UNCOMMITTED

After every Work Unit generate a short report.

After the complete Field generate a full Field Review Report.

Then:

STOP BEFORE COMMIT

Human may send that report to ChatGPT for review.

Only after explicit approval:

FIELD_COMMIT_APPROVED <FIELD_ID>

may Claude Code commit the Field.

If approval is not present:

DO NOT COMMIT

⸻

13. WORK UNIT REPORT

After every Work Unit write:

docs/implementation/field-reports/<FIELD_ID>/<WORK_UNIT_ID>.md

Use:

# WORK UNIT REPORT
FIELD:
WORK_UNIT:
## Mission
...
## Files changed
...
## Relation materialized
...
## Tests written first
...
## Initial failing proof
...
## Implementation
...
## L0 Direct Tests
...
## L1 Owning Module Tests
...
## L2 Relation Tests
...
## L3 Field Integration
...
## L4 Adjacent Field Regression
...
## L5 Static / Architecture Gates
...
## L6 Runtime Smoke
...
## L7 Browser Semantic Proof
...
## Recursive DeepSweep
What changed because this changed?
## Inverse DeepSweep
If applicable.
## First Broken Relation
NONE
or exact relation.
## Known limitations
...
## Unresolved blocker
...
## Current git status
...
## Result
PASS
FAIL_LOCAL
FAIL_RELATION
FAIL_INTEGRATION
BLOCKED_UPSTREAM
BLOCKED_EXTERNAL
HUMAN_DECISION_REQUIRED

Do not overclaim.

⸻

14. FIELD REVIEW REPORT

Before any commit generate:

docs/implementation/field-reports/<FIELD_ID>/FIELD_REVIEW.md

Required format:

# NQUIRY FIELD REVIEW REPORT
## Field
<id/name>
## Worktree State
git status
current branch
HEAD
## Architectural Authority
files and sections used
## Initial Field State
what existed before this Field
## Target Field State
what this Field was meant to make real
## Internal Work Units Executed
list
## Files Added
list
## Files Modified
list
## Migrations
list / NONE
## Dependencies Added
list / NONE
with justification
## Domain Changes
...
## Authority / Governance Changes
...
## Boundary Changes
...
## AI Changes
...
## Evidence / Provenance Changes
...
## Persistence Changes
...
## Event / Worker / Projection Changes
...
## API Changes
...
## Frontend Changes
...
## Test-First Evidence
tests that failed before implementation
## Tests Added
...
## Negative Tests
...
## Adversarial Tests
...
## Failure Injection
...
## Accessibility Proof
...
## Responsive Proof
...
## Visual Proof
...
## Recursive Upward Test Ladder
L0:
L1:
L2:
L3:
L4:
L5:
L6:
L7:
L8:
## Recursive DeepSweep Result
...
## Inverse DeepSweep Result
...
## First Broken Relation Result
NONE or exact relation
## Full Affected Regression
commands + results
## Runtime Proof
...
## Browser Proof
...
## Fixture Ceilings
...
## Mock Ceilings
...
## External Dependency Ceilings
...
## Known Limitations
...
## Architecture Drift
NONE or exact drift
## Downstream Fields Unlocked
...
## Git Diff Summary
git diff --stat
## Git Diff Check
git diff --check result
## Commit Status
NOT COMMITTED
## Recommended Status
FIELD_PASS
or failure/blocker classification

Then print a concise terminal summary that the human can paste into ChatGPT.

⸻

15. CHATGPT REVIEW PAYLOAD

At Field end also generate:

docs/implementation/field-reports/<FIELD_ID>/CHATGPT_REVIEW.txt

It should contain only the highest-value review information:

NQUIRY FIELD REVIEW
FIELD:
HEAD:
STATUS:
ARCHITECTURAL AUTHORITY:
MISSION:
WHAT CHANGED:
FILES:
MIGRATIONS:
NEW DEPENDENCIES:
TESTS ADDED:
TEST COMMANDS:
<exact commands>
RESULTS:
NEGATIVE/ADVERSARIAL RESULTS:
RECURSIVE DEEPSWEEP:
INVERSE DEEPSWEEP:
FIRST BROKEN RELATION:
FIXTURE/MOCK CEILINGS:
KNOWN LIMITATIONS:
GIT DIFF STAT:
COMMIT:
NOT YET COMMITTED

The human can give this directly to ChatGPT.

⸻

16. COMMIT PROTOCOL

After human review only.

Expected approval:

FIELD_COMMIT_APPROVED F03

Then:

1 rerun git diff --check
2 rerun critical Field tests
3 ensure worktree contains only intended Field changes
4 commit

Suggested message form:

field(F03): materialize protected human question field

After commit:

record commit hash
append it to FIELD_REVIEW.md
do not modify historical report except to record approved commit identity

Then begin next causally ready Field.

⸻

17. GLOBAL LOCAL TEST COMMANDS

At Field start re-read current repo scripts because commands may evolve.

Current expected baseline commands include:

pytest
ruff check .
mypy packages apps/api/src apps/worker/src scripts

Frontend:

cd apps/web
npm install
npm run lint
npm run typecheck
npm test
npm run e2e

Architecture/static scripts present in the repository should also be run where relevant, including dependency/provider/test-only import gates.

Do not assume one green command proves the Field.

⸻

18. CURRENT LOCAL RUNTIME BOOTSTRAP

At execution time prefer the repository’s current docs/RUNTIME_OPERATION.md.

Expected local lifecycle:

docker compose --profile app up -d --build

Prepare DB roles on a fresh database:

export PGPASSWORD=nquiry_local_dev_only
psql \
  -h localhost \
  -p 15432 \
  -U nquiry \
  -d nquiry \
  -f infra/local/db_roles.sql

Apply / verify migrations:

export DATABASE_URL="postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry"
source .venv/bin/activate
python scripts/verify_migrations.py

Current demo bootstrap:

python scripts/seed_local_demo.py

Browser:

http://localhost:3000/

Important:

seed_local_demo.py
=
LOCAL DEMO FIXTURE
NOT
PRODUCTION GOVERNANCE PROOF

When F01 eventually closes legitimate Workspace bootstrap, add a separate legitimate acceptance lane.

Do not rewrite historical fixture tests to pretend they proved it.

⸻

19. FIELD DAG

The coarse execution Fields are:

F00
EXECUTION CONTROL · BASELINE · PROOF HARNESS
F01
IDENTITY · WORKSPACE · GOVERNANCE
F02
CHALLENGE · SESSION · PARTICIPATION
F03
PROTECTED HUMAN QUESTION FIELD
F04
AI BOUNDARY · POST-BURST SENSEMAKING
F05
REFLECTION · SELECTION · INVESTIGATION
F06
EVIDENCE · INSIGHT · EXPERIMENT · LEARNING
F07
HUMAN DECISION · ACTION · RE-QUESTIONING
F08
CONSEQUENCE INTEGRITY · EVENTS · WORKERS · PROJECTIONS
F09
FAILURE · RECOVERY · SECURITY · PRIVACY · ISOLATION
F10
COMPLETE APPLICATION RUNTIME · API · LOCAL OPERATIONS
F11
SEMIOTIC FRONTEND SYSTEM
F12
FULL ACCEPTANCE · DEPLOYMENT · PRODUCTION PROMOTION

Dominant causality:

F00
↓
F01
↓
F02
↓
F03
├───────────────┐
↓               ↓
F04            F08 infrastructure may begin when event contracts stable
↓
F05
↓
F06
↓
F07
↓
F08
↓
F09
↓
F10
↓
F11
↓
F12

F11 begins foundational work earlier where projection contracts are stable.

This is not a pure waterfall.

⸻

20. FIELD F00

EXECUTION CONTROL · BASELINE · PROOF HARNESS

INTENT

Before product expansion, establish one reliable implementation/proof loop for every later Field.

WHY THIS FIELD EXISTS

Without F00, later Fields can differ in:

report format
test discipline
commit behavior
runtime procedure
proof claims

F00 standardizes the engineering process.

HUMAN PRODUCT EFFECT

Indirect.

It makes later implementation reviewable and prevents uncontrolled agent drift.

TARGET

Materialize:

Field report structure
Work Unit report structure
test command registry
architecture/static gate registry
local-runtime command registry
proof-report directory
pre-commit review gate

INTERNAL WORK UNITS

Expected:

WU-00.1 reconstruct current repo commands
WU-00.2 define field-report filesystem
WU-00.3 define reusable test runner / command manifest where useful
WU-00.4 verify architecture gates
WU-00.5 verify local runtime from fresh-ish environment
WU-00.6 generate baseline proof report

Do not build a large custom orchestration framework unless the existing scripts truly cannot support the process.

Prefer documentation + simple scripts over infrastructure invention.

TESTS FIRST

Prove current commands actually work.

At minimum classify:

backend suite
frontend suite
static gates
migration verification
Compose startup
API health
Web load
login

RECURSIVE UPWARD TEST SET

F00 touches everything operationally.

Validate:

scripts
CI
runtime docs
proof reports
Compose
backend commands
frontend commands

STOP CONDITIONS

If current repo baseline itself is broken:

STOP
→ classify pre-existing failure

Do not silently “fix” unrelated architecture while creating F00.

PASS

F00 passes when every later Field has a deterministic:

test
report
review
commit

protocol.

⸻

21. FIELD F01

IDENTITY · WORKSPACE · GOVERNANCE

SEMANTIC REGIME

Human legitimacy and operation-specific authority.

HUMAN PRODUCT EFFECT

Human can:

authenticate
→ see accessible Workspaces
→ establish or enter legitimate Workspace context
→ hold membership
→ receive/revoke governed rights
→ see actual available capabilities

CURRENT FIELD

Expected current state:

local auth
→ real
Workspace domain
→ real
Membership
→ real
Governance / HABB
→ real core
Workspace discovery
→ incomplete
legitimate first root
→ unresolved unless newer decision exists

TARGET

Complete vertical relation:

IDENTITY
→ WORKSPACE
→ MEMBERSHIP
→ GOVERNANCE
→ HUMAN AUTHORITY
→ CAPABILITY PROJECTION
→ FRONTEND

INTERNAL WORK UNITS

Likely:

WU-01.1 current identity adapter normalization
WU-01.2 accessible Workspace query
WU-01.3 current Workspace semantic context
WU-01.4 legitimate bootstrap branch
ONLY IF AUTHORITATIVELY RESOLVED
WU-01.5 membership governance operations
WU-01.6 HumanAuthorityBinding grant/revoke
WU-01.7 capability semantic projection
WU-01.8 HTTP surface
WU-01.9 Workspace orientation frontend
WU-01.10 adversarial governance proof

Claude Code may merge/reorganize Work Units.

BACKEND REQUIREMENTS

No:

first login = owner
role = right
DB admin = governance

Every consequential right remains reconstructable.

FRONTEND REQUIREMENTS

Render separately:

authenticated
member
authorized
governance-capable
non-proof demo state

TESTS FIRST

Mandatory:

valid login
invalid login
expired/revoked session
accessible Workspace list
revoked membership
cross-Workspace isolation
grant authority
revoke authority
role without right
wrong operation
wrong scope
authority revoked between view and commit
bootstrap self-grant attacks

RECURSIVE UPWARD TESTS

After authority-related Work Unit:

local authority tests
→ boundary tests
→ CommitUnit-related tests
→ Decision tests
→ Session control tests
→ security/isolation tests
→ frontend capability projection

INVERSE PROOF

visible capability
← semantic capability view
← current binding
← membership
← governance ancestry
← Workspace
← verified identity

STOP CONDITIONS

If legitimate first Workspace root is still undefined:

HUMAN_DECISION_REQUIRED

Continue downstream mechanics only through explicitly labeled non-proof fixtures.

PASS

F01 passes mechanically under fixture lane only with fixture ceiling.

Production-legitimate F01 requires real root mechanism.

⸻

22. FIELD F02

CHALLENGE · SESSION · PARTICIPATION

SEMANTIC REGIME

Inquiry context and process lifecycle.

HUMAN PRODUCT EFFECT

Human can:

create/access Challenge
→ create/access Session
→ participate
→ understand inquiry position
→ move through legitimate phases

TARGET

Everything required to reach the protected Question Field through real browser/API operations.

INTERNAL WORK UNITS

Challenge create/read
Challenge semantic projection
Session create/read
Session state Commands
participant context
legal state-transition API
inquiry-position frontend
state conflict/failure frontend
tests

BACKEND

No generic:

PATCH /session/status

Every movement maps to a semantic Command.

FRONTEND

Do not make phase navigation look like a normal wizard whose tabs can be clicked arbitrarily.

Navigation:

reflects state

It does not create state.

TESTS FIRST

all valid transitions
all invalid transitions
stale version
wrong Workspace
wrong Session authority
terminal state
participant ≠ controller
cross-Workspace access

UPWARD RECURSIVE TEST

Session change
→ state-machine suite
→ authority/boundary suite
→ Burst prerequisites
→ downstream phase prerequisite tests
→ API
→ frontend inquiry-position projection

INVERSE

visible "we are in reflection"
← canonical Session state
← legitimate transition
← authorized human

PASS

Human can create and enter a legitimate inquiry context using actual runtime.

⸻

23. FIELD F03

PROTECTED HUMAN QUESTION FIELD

SEMANTIC REGIME

Protected human generation.

HUMAN PRODUCT EFFECT

This must be one of the clearest signature experiences in NQUIRY.

Human enters:

QUESTION GENERATION

not:

AI ASSISTANCE

TARGET

Burst preparation
→ active protected Burst
→ four-minute temporal awareness
→ human Question capture
→ multi-human presence where allowed
→ Burst completion
→ frozen raw Question set

INTERNAL WORK UNITS

Burst lifecycle
timer
Question persistence
original_text immutability
human provenance
capture Command/API
duplicate/idempotent capture
multi-human representation
active Burst frontend
completion frontend
frozen field frontend
contamination enforcement
failure/reconnect
tests

BACKEND

Enforce protected Human-only mode server-side.

Do not rely on hidden frontend controls.

FRONTEND

During protected Burst no:

AI suggestions
AI chat
reframes
clusters
scores
ranking
answers
evidence analysis

Questions appear quickly.

Human remains in flow.

TIMER

Timer is perceptible.

Timer is not gamification.

If automatic completion authority is unresolved:

timer
→ presentation
human authorized completion
→ canonical transition

Do not let JavaScript clock become domain authority.

TESTS FIRST

verbatim Unicode text
original_text immutable
Question origin exact
AI request denied during protected Burst
late capture after completion denied
frozen membership immutable
duplicate submission
multiple participant provenance
disconnect/reconnect
timer boundary
client manipulation

UPWARD RECURSIVE TEST

After Question changes:

Question unit
→ Burst relation
→ provenance
→ AI context restrictions
→ sensemaking source integrity
→ history
→ frontend

After Burst changes:

Burst
→ Session state
→ AI eligibility
→ frozen-set consumers
→ browser contamination proof

INVERSE

visible Human Question
← canonical Question
← human author
← valid Burst membership
← active protected Burst

PASS

A real browser flow proves protected human generation without hidden AI contamination.

⸻

24. FIELD F04

AI BOUNDARY · POST-BURST SENSEMAKING

SEMANTIC REGIME

Derived machine participation after protected human generation.

This Field intentionally groups AI Gateway participation and the first post-Burst sensemaking because the human product experiences them as one transformation:

FROZEN HUMAN QUESTION FIELD
→ DERIVED RELATIONAL FIELD

Concrete provider eligibility remains a conditional branch inside this Field.

HUMAN PRODUCT EFFECT

After Burst completion:

relations emerge
clusters become visible
perspectives open
assumptions surface
contradictions become visible
AI-origin Questions may appear where permitted

without turning into chat.

INTERNAL WORK UNITS

AI operation eligibility
AIContextManifest
Gateway path
MockProvider structural lane
real provider conditional lane
AIGeneration persistence/provenance
Question clustering
unusual Questions / patterns
Perspective derivation
Assumption exposure
human/AI/system provenance projection
post-Burst API
post-Burst frontend transformation
AI unavailable state
tests

BACKEND

Provider response is untrusted input.

It passes:

validation
→ provenance
→ derived representation

before product use.

FRONTEND

AI enters by transformation of the field.

Not:

big assistant chat box

Human original Questions remain visually primary.

TESTS FIRST

AI blocked before completed Burst
exact frozen set used
provider bypass impossible
cross-Workspace context impossible
AIGeneration lineage exact
malformed provider response rejected
AI output not human
AI output not Evidence
AI output not Decision
clusters do not mutate raw membership
AI unavailable leaves human workflow usable

UPWARD RECURSIVE TEST

AI change
→ Gateway tests
→ security/provider gates
→ Question provenance
→ Assumption behavior
→ Evidence non-collapse
→ Decision authority exclusion
→ frontend provenance

INVERSE

visible AI cluster
← derived cluster
← validated AIGeneration
← Gateway
← approved operation
← completed Burst
← frozen Questions

STOP

Real provider branch stops if:

provider
data classification
privacy
data sovereignty

are not actually approved.

Structural Field may still pass with explicit Mock ceiling.

⸻

25. FIELD F05

REFLECTION · SELECTION · INVESTIGATION

SEMANTIC REGIME

Human orientation after expansion.

HUMAN PRODUCT EFFECT

The field changes from:

expand

to:

orient
→ focus
→ investigate

without implying that unselected Questions are wrong.

INTERNAL WORK UNITS

Reflection semantic view
reflection interaction
Question selection
1–3 selection invariant where authoritative
primary/catalytic Question
selection provenance
Impact/Five-Why chain
investigation transition
API
frontend
tests

FRONTEND

Reflection must feel materially different from Burst.

Selection must feel materially different from Decision.

TESTS FIRST

selection authority
selection count
selected Question provenance
unselected Questions preserved
AI cannot select authoritatively
ImpactChain ordering
human causal answers
stale candidate set
commit uncertainty

UPWARD RECURSIVE TEST

selection
→ Question provenance
→ Session state
→ authority
→ ImpactChain
→ Evidence/investigation prerequisites
→ frontend

INVERSE

visible catalytic Question
← canonical selection
← authorized human
← exact source Question

PASS

Human can narrow inquiry without product declaring truth.

⸻

26. FIELD F06

EVIDENCE · INSIGHT · EXPERIMENT · LEARNING

SEMANTIC REGIME

Epistemic investigation and governed testing.

HUMAN PRODUCT EFFECT

Human can:

investigate
→ examine Evidence
→ preserve contradiction
→ synthesize Insight
→ run Experiment
→ observe result
→ learn

INTERNAL WORK UNITS

Source/Evidence capture
ClaimAnchor projection
Evidence relation
EvidenceSet
provenance/versioning
contradiction preservation
uncertainty
Insight creation/lineage
Experiment proposal
Experiment authorization
Experiment state machine
result
learning projection
API
frontend
tests

BACKEND

Do not invent generic Claim object if architecture uses ClaimAnchor.

Do not invent universal Insight validation.

FRONTEND

No truth meter.

Evidence field must show:

SUPPORTS
CONTRADICTS
CONTEXTUAL
DOES_NOT_SUPPORT
UNASSESSED
UNCERTAIN

TESTS FIRST

Evidence provenance
Evidence version fidelity
support and contradiction coexist
cross-Workspace Evidence denied
AI confidence not accepted as Evidence
Experiment authority
Experiment state transitions
Experiment completion ≠ hypothesis truth
Result ≠ automatically admitted Evidence

UPWARD RECURSIVE TEST

Evidence change
→ provenance
→ Assumption transitions
→ Experiment
→ Decision
→ history
→ frontend

Experiment change:

Experiment
→ authority
→ state
→ result
→ Evidence candidate
→ learning
→ re-question

INVERSE

visible SUPPORTS relation
← EvidenceRelation
← exact Evidence version
← Source/provenance
← claim target

PASS

Uncertainty and contradiction survive backend → API → frontend.

⸻

27. FIELD F07

HUMAN DECISION · ACTION · RE-QUESTIONING

SEMANTIC REGIME

Human agency and consequential inquiry recursion.

HUMAN PRODUCT EFFECT

Human perceives the difference between:

AI proposal
consideration
selection
Decision
authorization
execution
result

Then the system reopens inquiry.

INTERNAL WORK UNITS

consideration view
Decision query
Decision command completion
decision provenance
Action-phase transition
separate action authority where applicable
resulting state
learning/re-questioning
new Question lineage
frontend decision experience
tests

FRONTEND

No optimistic Decision.

No AI-selected default treated as human choice.

No confetti.

Decision has gravity without theater.

TESTS FIRST

current Decision right
revoked right
authority revoked between render and commit
AI actor rejected
duplicate Decision
stale version
indeterminate commit
Decision ≠ external execution
new Question after changed field
history link back to sources

UPWARD RECURSIVE TEST

Decision
→ authority
→ Evidence requirements
→ CommitUnit
→ Event
→ history
→ recovery
→ frontend

INVERSE

visible DECIDED
← canonical Decision
← Commit
← final boundaries
← current human Decision right
← governance ancestry

STOP

If real external Action execution is requested but no integration/action semantics exist:

HUMAN_DECISION_REQUIRED

Do not invent an arbitrary action executor.

⸻

28. FIELD F08

CONSEQUENCE INTEGRITY · EVENTS · WORKERS · PROJECTIONS

SEMANTIC REGIME

Historical persistence of legitimate consequences.

HUMAN PRODUCT EFFECT

A user-visible consequence remains explainable after:

process crash
worker restart
projection rebuild
authority change

TARGET

legitimate Command
→ final boundary
→ CommitUnit
→ canonical mutation
 + Audit
 + durable immutable Event basis
 + Outbox
→ exact EventEnvelope
→ Worker
→ Projection
→ Replay/Rebuild

INTERNAL WORK UNITS

durable Event semantic contract
storage representation
migration
CommitUnit integration
EventEnvelope reconstruction
Outbox delivery
worker loop
worker startup/shutdown
duplicate handling
poison handling
Projection worker
projection freshness
replay
rebuild
diagnostics
tests

STORAGE FREEDOM

Claude Code may choose:

enriched outbox
separate committed event table
normalized immutable event representation

only if semantic reconstruction is exact.

HISTORICAL EVENT BASIS

Must reconstruct required historical fields without mutable-current lookups.

At minimum consider:

event_id
event_type
schema_version
occurred_at
Workspace reference
aggregate reference
aggregate version
command ID
commit ID
correlation ID
causation ID
actor reference
authority source reference
payload

TESTS FIRST

commit + crash
restart
exact Event equality
authority revoked later
aggregate changes later
historical Event unchanged
duplicate delivery
worker restart
poison event
projection failure
projection deletion
projection rebuild
replay does not execute Command

UPWARD RECURSIVE TEST

Event persistence
→ CommitUnit
→ audit
→ outbox
→ worker
→ projection
→ recovery
→ frontend freshness/history

INVERSE

visible projection
← Event
← immutable historical basis
← Commit
← legitimate canonical consequence

PASS

No worker needs to invent missing Event semantics.

⸻

29. FIELD F09

FAILURE · RECOVERY · SECURITY · PRIVACY · ISOLATION

SEMANTIC REGIME

System truth under adverse conditions.

HUMAN PRODUCT EFFECT

The system says what it actually knows.

It does not falsely claim:

success
failure
authority
recovery

INTERNAL WORK UNITS

failure taxonomy
HTTP failure mapping
INDETERMINATE handling
last proven valid state
reconciliation
recovery Commands
Workspace isolation sweep
session/security sweep
direct-write prevention
provider security
privacy/redaction
retention/deletion conditional policy
observability correlation
failure/recovery frontend
tests

REQUIRED OUTCOME DISTINCTIONS

DENIED
FAILED_PRECOMMIT
INDETERMINATE
COMMITTED
BLOCKED
STALE
PROJECTION_LAG
AI_UNAVAILABLE
EVIDENCE_UNAVAILABLE

TESTS FIRST

DB unavailable before operation
DB uncertainty around commit
worker crash
projection failure
session expiry
authority revoke
cross-Workspace access
backup restore
duplicate recovery
admin bypass
provider outage
telemetry sink failure

UPWARD RECURSIVE TEST

A security or recovery Work Unit must recheck all affected consequential Fields.

Example:

authority recovery change
→ F01
→ F02
→ F07
→ F08
→ frontend

INVERSE

visible RECOVERED
← current canonical state
← legitimate reconciliation
← last proven valid state
or
← newly governed Recovery Command

STOP

Legal/privacy/retention policy is not selected by coding agent.

⸻

30. FIELD F10

COMPLETE APPLICATION RUNTIME · API · LOCAL OPERATIONS

SEMANTIC REGIME

Transport and operational materialization of already-approved semantics.

HUMAN PRODUCT EFFECT

Nothing required for the bounded product remains:

"it exists in Python tests but cannot be used"

INTERNAL WORK UNITS

complete Command catalog
complete Query catalog
HTTP semantic routes
DTO/view contracts
common failure envelope
idempotency transport
auth middleware integration
Workspace context integration
AI endpoint integration
Evidence endpoint integration
recovery endpoints
worker process runtime
config validation
migrations
health
readiness
liveness
startup
shutdown
diagnostics
local Compose
runtime documentation
tests

ROUTE LAW

Every route answers:

PRODUCT PURPOSE
→ QUERY OR COMMAND
→ ACTOR
→ IDENTITY
→ WORKSPACE
→ AUTHORITY
→ PRECONDITIONS
→ BOUNDARIES
→ INPUT
→ OUTPUT
→ IDEMPOTENCY
→ PERSISTENCE
→ AUDIT
→ EVENT
→ FAILURE
→ FRONTEND CONSUMER

No generic CRUD for governed state.

No direct DB write route.

TESTS FIRST

route→handler
handler→authority
handler→boundary
real PostgreSQL
malformed payload
cross-Workspace
stale version
duplicate Command
infrastructure failure
migration mismatch
startup failure
readiness
graceful shutdown

UPWARD RECURSIVE TEST

Every route added:

route test
→ application handler
→ owning Field
→ authority/boundary
→ persistence/event if command
→ frontend contract

LOCAL RUNTIME ACCEPTANCE

At end of F10:

docker compose
→ DB
→ migrations
→ API
→ worker
→ web
→ login
→ semantic queries/commands

must run coherently.

PASS

Every non-blocked bounded capability is real runtime capability.

⸻

31. FIELD F11

SEMIOTIC FRONTEND SYSTEM

SEMANTIC REGIME

Human perception of the entire inquiry Field.

HUMAN PRODUCT EFFECT

The interface feels like:

INQUIRY

not:

CHAT

and not:

ADMIN SOFTWARE

INTERNAL WORK UNITS

Claude Code may internally organize by visual system + experience regimes, not screen tickets.

Expected:

design tokens
typography
type scale
spatial grammar
layout regimes
provenance language
human / AI distinction
authority language
uncertainty language
Evidence language
navigation / inquiry orientation
protected Burst
post-Burst transformation
reflection
selection
investigation
Evidence field
Experiment / Learning
Decision
re-questioning
history / graph
failure states
loading / empty states
motion
keyboard
screen reader
responsive
visual regression
tests

GLOBAL FRONTEND LAW

DISPLAYED LEGITIMACY
<=
RECONSTRUCTABLE LEGITIMACY
DISPLAYED CERTAINTY
<=
RECONSTRUCTABLE CERTAINTY
DISPLAYED AUTHORITY
<=
CURRENT AUTHORITY
DISPLAYED COMPLETION
<=
CANONICAL COMPLETION
DISPLAYED PROVENANCE
=
ACTUAL PROVENANCE

EXPERIENCE REGIMES

ENTRY

Orientation.

Not dashboard metrics.

WORKSPACE

Context and legitimate action space.

CHALLENGE

Open problem field.

PROTECTED BURST

Generation.

AI cognitively absent.

POST-BURST

Relations emerge.

REFLECTION

Slower orientation.

SELECTION

Focus without truth claim.

INVESTIGATION

Depth and relation.

EVIDENCE

Contradiction and uncertainty visible.

EXPERIMENT

Testing, not gamification.

DECISION

Human gravity.

LEARNING

Field changes.

RE-QUESTION

Field opens again.

FAILURE

Truthful reduced action space.

VISUAL SYSTEM

Typography

Human inquiry content has priority.

Space

Proximity can show relation.

Color

Never:

green = truth
red = false

Motion

Only semantic change.

Decision motion

Minimal.

Humor

Allowed only in low-gravity states.

No humor in:

protected Burst
authority denial
Evidence contradiction
Decision
INDETERMINATE
security failure
serious recovery

ACCESSIBILITY

Meaning cannot depend solely on:

color
motion
hover
fine motor control
spatial position

Required:

keyboard
screen reader
reduced motion
visible focus
color-vision robustness
zoom
mobile
tablet
desktop

Graph/relational views require non-visual structured equivalents.

RESPONSIVE

Mobile

Focus one relation/context at a time.

Tablet

Split context/detail where useful.

Desktop

Richer simultaneous relational field.

Never simply shrink desktop.

TESTS FIRST

Every frontend Work Unit begins with semantic assertions.

Test:

what is visible
what is absent
what provenance is exposed
what action is enabled
what action is unavailable
what happens on stale authority
what happens on server failure

UPWARD RECURSIVE TEST

For each human-visible change:

component
→ semantic view model
→ API
→ canonical/derived backend state
→ authority/provenance
→ owning product Field

BROWSER PROOF

Playwright or current browser suite must test:

keyboard
real API interaction
mobile viewport
desktop viewport
critical failure states
reduced-motion behavior where practical
semantic provenance

SEMIOTIC PASS QUESTIONS

Does Question precede Answer?
Does Burst feel protected?
Does AI disappear when required?
Does AI enter differently from a human?
Can human authorship be perceived?
Can relations be perceived?
Can uncertainty remain open?
Can contradictory Evidence coexist?
Does Reflection feel different from Generation?
Does Selection feel different from Truth?
Does Decision feel different from AI suggestion?
Does Learning reopen Questions?
Can the human orient without knowing enums?
Does complexity remain calm?
Does the UI avoid generic chatbot behavior?
Does it avoid generic SaaS-dashboard behavior?

Any required NO:

FAIL_FRONTEND_SEMANTIC

⸻

32. FIELD F12

FULL ACCEPTANCE · DEPLOYMENT · PRODUCTION PROMOTION

SEMANTIC REGIME

Whole-system proof and environment promotion.

HUMAN PRODUCT EFFECT

A real person can execute the complete intended product loop against the real running system.

PART A — LOCAL FULL PRODUCT ACCEPTANCE

From clean local state:

INSTALL
→ CONFIGURE
→ POSTGRESQL
→ ROLES
→ MIGRATIONS
→ BOOTSTRAP
→ API
→ WORKERS
→ WEB
→ BROWSER
→ LOGIN
→ WORKSPACE
→ CHALLENGE
→ SESSION
→ BURST
→ QUESTIONS
→ POST-BURST
→ REFLECTION
→ SELECTION
→ INVESTIGATION
→ EVIDENCE
→ INSIGHT
→ EXPERIMENT
→ DECISION
→ COMMIT
→ EVENT
→ WORKER
→ PROJECTION
→ FRONTEND CONVERGENCE
→ LEARNING
→ RE-QUESTION
→ HISTORY
→ RESTART
→ RECONSTRUCTION

LOCAL TEST LANES

Maintain distinct lanes:

LANE A
NON_PROOF FIXTURE LOCAL DEMO
LANE B
LEGITIMATE LOCAL WORKSPACE
only once F01 root is resolved
LANE C
MOCK AI
LANE D
REAL ELIGIBLE PROVIDER
only when F04 external dependencies are resolved

Never merge proof claims across lanes.

PART B — LOCAL CLEAN-ROOM PROOF

Acceptance must be repeatable from a fresh database.

Prove:

migration from empty DB
bootstrap
login
full product flow
restart
projection reconstruction

No hidden developer state.

⸻

33. DEPLOYMENT ARCHITECTURE

The repository currently has containerized local operation.

Do not choose a production platform without explicit requirement.

Use a platform-neutral container deployment contract.

Target process topology:

WEB
API
OUTBOX / PROJECTION WORKER
POSTGRESQL
AI PROVIDER EGRESS
OBSERVABILITY

Production deployment must preserve these separate responsibilities even if a platform chooses to place multiple processes on shared infrastructure.

⸻

34. BUILD ARTIFACTS

Production/staging deployment should use immutable build artifacts.

Expected:

API image
Worker image
Web image

Do not deploy production by:

SSH
→ git pull
→ run arbitrary source tree

unless an explicit deployment architecture later authorizes that pattern.

Prefer:

build once
→ identify artifact
→ promote same artifact

between environments.

⸻

35. CONFIGURATION

Configuration must be validated at startup.

Separate:

public configuration
secrets
domain policy
authority

Environment variables or secret possession never create product authority.

⸻

36. SECRETS

Production secrets must come from the selected deployment environment’s approved secret mechanism.

Do not commit secrets.

Do not expose secrets in:

logs
browser bundles
proof reports
screenshots

⸻

37. DATABASE DEPLOYMENT

Production/staging process:

database reachable
→ migration preflight
→ migration job
→ migration verification
→ application readiness

Migrations are not casually run concurrently by every API replica.

Use one controlled migration step/job.

Before destructive schema changes:

backup / recovery proof

must exist where relevant.

⸻

38. DEPLOYMENT ORDER

Recommended causal order:

1 verify environment config
2 verify DB connectivity
3 backup/check recovery prerequisite where necessary
4 apply migrations
5 start / update API
6 verify API readiness
7 start / update workers
8 verify workers ready and Event reconstruction functional
9 start / update Web
10 run smoke tests
11 run semantic browser tests
12 observe error/lag signals
13 promote environment status

⸻

39. STAGING

Before production, use an integration/staging environment when available.

Staging should use:

production-like images
real PostgreSQL
real workers
real projections
real secret mechanism
real routing/TLS model
eligible provider only if permitted

Staging does not automatically prove production.

But it should prove deployment mechanics.

⸻

40. PRODUCTION READINESS GATES

Do not deploy as production-accepted unless all required branches pass.

At minimum:

legitimate Workspace root
production identity policy
privacy/data-sovereignty
eligible AI provider if AI enabled in production
retention/deletion requirements
security review
backup/recovery
observability
migration safety
full causal acceptance

If AI provider is unresolved, production may only proceed if product architecture explicitly permits AI-disabled production mode.

Do not silently substitute MockProvider.

⸻

41. HEALTH AND READINESS

Separate:

LIVENESS
=
process running

from:

READINESS
=
process can perform declared responsibility

API readiness may require:

DB
schema
critical config

Worker readiness may require:

DB
schema
Event reconstruction
consumer configuration

Web readiness may require successful build/runtime startup, but not falsely claim backend health unless its contract explicitly checks it.

⸻

42. DEPLOYMENT SMOKE TEST

Immediately after deployment:

health
readiness
login
Workspace query
one safe read path
one governed write path in non-production test context where appropriate
worker lag
projection freshness
AI eligibility / disabled state
frontend load

Production smoke tests must not create harmful real-world consequences.

⸻

43. ROLLBACK

Rollback depends on what has changed.

CODE-ONLY

Previous immutable image may be redeployed if DB schema remains compatible.

MIGRATION INVOLVED

Do not assume code rollback is safe.

Check:

schema compatibility
data transformation
forward-fix possibility
backup restore implications

A DB restore does not automatically restore legitimate current governance.

F09/F10 laws still apply.

⸻

44. POST-DEPLOY ACCEPTANCE

After staging deployment:

runtime smoke
→ affected integration tests
→ browser critical path
→ worker/event/replay proof

After production deployment:

safe smoke
→ health/readiness
→ observation period
→ no architecture claim inflation

⸻

45. FULL SYSTEM TEST MATRIX

F12 must include explicit acceptance suites.

SUITE A — IDENTITY / GOVERNANCE

login
logout
session expiry
Workspace isolation
authority revoke

SUITE B — INQUIRY

Challenge
Session
Burst
Questions
post-Burst
reflection
selection
investigation

SUITE C — EPISTEMIC

Evidence
contradiction
Insight
Experiment
learning

SUITE D — CONSEQUENCE

Decision
Commit
Audit
Event
Worker
Projection

SUITE E — FAILURE

DB loss
worker restart
provider loss
projection lag
INDETERMINATE
recovery

SUITE F — FRONTEND

semantic states
keyboard
responsive
provenance
authority
motion
failure

SUITE G — RECONSTRUCTION

restart
replay
projection rebuild
history

⸻

46. F12 INVERSE ACCEPTANCE

Start from final human experience:

VISIBLE CHANGED FIELD
← frontend semantic projection
← canonical/projection state
← Event
← Commit
← authorized consequence
← Human Decision
← Evidence/Insight
← Investigation
← selected Question
← Reflection
← Post-Burst analysis
← frozen Human Questions
← protected Burst
← Session
← Challenge
← legitimate Workspace
← verified identity

Every link must be real.

⸻

47. FIELD EXECUTION ORDER

Recommended fast causal execution:

F00
↓
F01
↓
F02
↓
F03
↓
F04
↓
F05
↓
F06
↓
F07

Parallel infrastructure stream once stable semantics exist:

F08
→ F09

F10 starts incrementally as each semantic Field becomes stable, but its final PASS waits for F01–F09.

F11 begins its design-system and semantic-projection foundations after F01/F02 contracts are stable and then continuously interleaves.

Final:

F10 + F11
→ F12

⸻

48. PARALLELIZATION FOR SPEED

Safe examples:

F02 backend inquiry context
||
F08 Event infrastructure architecture
||
F11 visual foundation

after F01 contracts stabilize.

After F03:

F04 AI/Sensemaking
||
F08 Event implementation
||
F11 Protected Burst frontend refinement

After F05:

F06 epistemic backend
||
F11 investigation/evidence semiotic work

Do not parallelize two efforts that independently alter the same semantic contract without a shared stable interface.

⸻

49. FIELD PASS DEFINITION

A Field does not pass because:

code compiles
unit tests pass
endpoint returns 200
UI renders
Playwright clicked through
database row exists

A Field passes when:

intended semantic relation is materially real
forbidden states remain impossible
authority is legitimate
persistence is coherent
human projection is truthful
affected Fields remain coherent
recursive upward tests pass
DeepSweep passes
Inverse DeepSweep passes
runtime proof passes
proof report does not overclaim

⸻

50. GLOBAL STOP CONDITIONS

Stop and report rather than invent when:

authority meaning is absent
governance mechanism is absent
canonical object meaning is absent
state transition is absent
Evidence truth rule would need invention
provider eligibility is absent
privacy/legal policy is absent
real-world Action semantics are absent
downstream implementation would weaken an existing invariant

Use:

HUMAN_DECISION_REQUIRED

or:

BLOCKED_EXTERNAL

⸻

51. FIELD FAILURE CLASSIFICATION

Use exactly:

FIELD_PASS
FAIL_LOCAL
FAIL_RELATION
FAIL_INTEGRATION
FAIL_ARCHITECTURE_DRIFT
FAIL_BOUNDARY
FAIL_SECURITY
FAIL_PROVENANCE
FAIL_FRONTEND_SEMANTIC
BLOCKED_UPSTREAM
BLOCKED_EXTERNAL
HUMAN_DECISION_REQUIRED
INCONCLUSIVE

Never turn a blocker into PASS.

⸻

52. FINAL SYSTEM REPORT

After F12 produce:

docs/implementation/proof-reports/NQUIRY-FULL-SYSTEM-FINAL.md

It must include:

exact Git commit
environment
build artifacts
database schema revision
Fields passed
Fields conditional
blocked branches
human decisions used
external dependencies used
full test commands
test counts/results
browser acceptance
accessibility acceptance
responsive acceptance
event/replay acceptance
failure/recovery acceptance
AI acceptance
fixture ceilings
mock ceilings
production ceilings
Recursive DeepSweep result
Inverse DeepSweep result
architecture drift result
highest proven readiness tier

⸻

53. READINESS CLASSIFICATION

Report independently:

ARCHITECTURE_READY
FIELD_IMPLEMENTATION_COMPLETE
LOCAL_EXECUTABLE
DEVELOPMENT_READY
INTEGRATION_READY
PROVIDER_READY
PRODUCTION_ELIGIBLE
PRODUCTION_ACCEPTED

Never infer one from another.

Example:

LOCAL_EXECUTABLE
=
PASS
PROVIDER_READY
=
BLOCKED_EXTERNAL
PRODUCTION_ELIGIBLE
=
BLOCKED
PRODUCTION_ACCEPTED
=
NOT_EXECUTED

is valid.

⸻

54. REQUIRED HUMAN REVIEW LOOP

The intended collaboration is:

CLAUDE CODE
→ builds Work Units
→ recursively tests upward
→ writes reports
→ closes Field locally
→ writes FIELD_REVIEW + CHATGPT_REVIEW
→ STOPS BEFORE COMMIT
HUMAN
→ gives report to ChatGPT
CHATGPT
→ reviews architecture / proof / drift
HUMAN
→ approves or returns corrections
CLAUDE CODE
→ corrects if required
→ reruns proof
→ regenerates report
HUMAN
→ FIELD_COMMIT_APPROVED Fxx
CLAUDE CODE
→ commits
→ begins next causally ready Field

This review boundary is intentional.

⸻

55. REQUIRED AGENT OUTPUT AFTER EACH WORK UNIT

At the terminal, after every Work Unit print:

WORK_UNIT_COMPLETE
FIELD:
WORK_UNIT:
RELATION_MATERIALIZED:
TEST_LADDER:
L0 PASS/FAIL
L1 PASS/FAIL
L2 PASS/FAIL
L3 PASS/FAIL
L4 PASS/FAIL
L5 PASS/FAIL
L6 PASS/FAIL/NA
L7 PASS/FAIL/NA
RECURSIVE_DEEPSWEEP:
PASS / ISSUE
INVERSE_DEEPSWEEP:
PASS / NA / ISSUE
FIRST_BROKEN_RELATION:
NONE / <relation>
REPORT:
<path>
COMMIT:
NOT PERFORMED

⸻

56. REQUIRED AGENT OUTPUT AFTER EACH FIELD

Print:

FIELD_EXECUTION_COMPLETE
FIELD:
STATUS:
WORK_UNITS:
<count>
FIELD TESTS:
PASS/FAIL
AFFECTED REGRESSION:
PASS/FAIL
RUNTIME:
PASS/FAIL/NA
BROWSER:
PASS/FAIL/NA
ACCESSIBILITY:
PASS/FAIL/NA
RESPONSIVE:
PASS/FAIL/NA
RECURSIVE DEEPSWEEP:
PASS/FAIL
INVERSE DEEPSWEEP:
PASS/FAIL/NA
FIRST BROKEN RELATION:
NONE / <relation>
BLOCKERS:
...
MOCK/FIXTURE CEILINGS:
...
FIELD REVIEW REPORT:
<path>
CHATGPT REVIEW PAYLOAD:
<path>
GIT STATUS:
UNCOMMITTED
NEXT ACTION:
WAITING_FOR_HUMAN_REVIEW

Then stop.

⸻

57. FINAL CLAUDE CODE EXECUTION LAW

Do not build isolated features.

Build relations.

After every Work Unit:

TEST LOCAL
→ TEST RELATIONS
→ TEST FIELD
→ TEST AFFECTED SYSTEM
→ RECURSE
→ REPORT

After every visible effect:

TRACE BACKWARDS

After every failure:

FIND FIRST BROKEN RELATION

After every Field:

FULL PROOF
→ REPORT
→ STOP BEFORE COMMIT

When semantics are missing:

STOP

When only implementation form is open:

BUILD

Do not let:

frontend beauty
→ falsify backend truth

Do not let:

backend precision
→ destroy human inquiry

Do not let:

AI convenience
→ erase Human Authority

Do not let:

test success
→ masquerade as system legitimacy

The implementation target is:

A COHERENT NQUIRY FIELD
THAT REMAINS COHERENT
WHILE
HUMANS
AI
QUESTIONS
EVIDENCE
EXPERIMENTS
DECISIONS
EVENTS
FAILURES
RECOVERY
AND LEARNING
CONTINUOUSLY CHANGE IT

⸻

58. MASTER STATUS

FIELD_SYSTEM
SET
FIELD_COUNT
13
FIELD_GRANULARITY
COARSE / SEMANTIC
WORK_UNIT_GRANULARITY
CLAUDE-CODE-CONTROLLED
TEST_STRATEGY
TEST_FIRST
AFTER_EVERY_WORK_UNIT
RECURSIVE_UPWARD_TEST
AFTER_VISIBLE_EFFECT
INVERSE_DEEPSWEEP
AFTER_EVERY_WORK_UNIT
REPORT
AFTER_EVERY_FIELD
FULL REVIEW REPORT
COMMIT_POLICY
HUMAN REVIEW REQUIRED
LOCAL_FIRST
YES
FULL_BACKEND
IN SCOPE
FULL_FRONTEND
IN SCOPE
WORKERS
IN SCOPE
EVENTS / REPLAY
IN SCOPE
SECURITY / RECOVERY
IN SCOPE
LOCAL DEPLOYMENT
IN SCOPE
STAGING / PRODUCTION DEPLOYMENT ARCHITECTURE
IN SCOPE
PRODUCTION PLATFORM SELECTION
OUTSIDE SCOPE UNTIL SPECIFIED
IMPLEMENTATION
START ONLY AFTER HUMAN GO
NQUIRY_FIELD_EXECUTION_WURFRAUM::READY_FOR_HUMAN_REVIEW
