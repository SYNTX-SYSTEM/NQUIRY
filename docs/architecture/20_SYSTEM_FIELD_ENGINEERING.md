# 20: System Field Engineering: Governing Execution Architecture

## DOCUMENT STATUS

HUMAN AUTHORIZED (2026-09-24, F02 execution instruction: "persist the System
Field Engineering parent architecture into the repository").
Persisted during Field F02. Not a product-semantics document.

## 0. AUTHORITY AND SCOPE

System Field Engineering (SFE) is the **governing engineering architecture**
of this repository.

- It does **not** replace NQUIRY product semantics (LEVEL 1, 00–12).
- It does **not** redefine the NQUIRY domain, authority, governance,
  boundary, evidence, AI, data or failure architecture (01–11).
- It governs **how** NQUIRY Fields are resolved, implemented, tested,
  documented, reconstructed, reviewed and committed.

Relation to existing documents:

| Document | Relation to 20 |
|---|---|
| 00–12 | Product and system semantics. 20 never overrides them |
| 13 | Test/falsification semantics. 20's test ladder materializes them per Field |
| 14 / 15 | Historical package-level execution (PKG-00..32, closed). 20 governs execution from there on |
| 16 | Canonical decision/gap ledger. Human decisions made during a Field are reconciled into 16 (§14 below) |
| 19 | Field Execution Master: the concrete F00–F12 plan. 19 is the applied form of 20; if they conflict, 20's laws hold and 19's Field content holds |
| 00_AGENT_WORKFLOW | PKG-era process record. Superseded for Field execution by 19/20 |

Authority stack (flows downward; a lower level may narrow, never silently
redefine a higher one):

```text
LEVEL 1  SFE (this document)            — how engineering happens
LEVEL 2  NQUIRY product/software architecture (00–18, 16 ledger)
LEVEL 3  current repository HEAD        — evidence of materialization, not authority
LEVEL 4  active Field (19 F00–F12)
LEVEL 5  Work Unit
```

Code is evidence of implementation. **Code does not have authority to
silently redefine architecture.**

## 1. CORE ONTOLOGY

| Term | Definition |
|---|---|
| FIELD | The currently resolved relational context: the objects, relations, states, authorities and boundaries that together determine which next transitions are legitimate |
| RELATION | A connection through which one thing affects what is true or legitimate for another |
| STATE | The current authoritative configuration (canonical records and their versions) |
| DELTA | A material change of that configuration: one admitted effect |
| BOUNDARY | The point where the current Field cannot legitimately close the next relation autonomously |
| AUTHORITY | The instance that closes what autonomy may not close |
| RECONSTRUCTION | Re-resolving the Field from the state that exists after a Delta |

The system is not `OBJECT + CONTEXT`. It is **a dynamic relational
configuration in a Field.**

## 2. MATERIAL CHANGE LAW

After every material Delta: `OLD FIELD != ASSUMED CURRENT FIELD`.

```text
STATE 1 → FIELD 1 → DELTA → STATE 2 → RECONSTRUCT → FIELD 2 → NEXT TRANSITION
```

Reconstruction is normal runtime behavior, not error recovery. In NQUIRY
runtime terms:
- authority is resolved fresh per request and again at commit;
- versions are compared at commit;
- the UI renders the server's post-commit reread, never an assumed result.

In engineering terms, every Field and Work Unit starts by re-reading HEAD,
reports and ledger, not memory.

## 3. FIELD HIERARCHY LAW (TREE)

`PARENT FIELD → SUBFIELD → WORK UNIT`. A child inherits the parent's
relations, boundaries, authority, constraints and state context.

A child MAY narrow its parent. A child MAY NOT:
- expand parent authority;
- remove parent boundaries;
- redefine parent semantics;
- create new domain truth without authority.

**A CHILD FIELD MAY NARROW ITS PARENT. IT MAY NEVER SILENTLY REDEFINE IT.**

## 4. TREE + GRAPH LAW

NQUIRY is simultaneously a hierarchy and a relation graph.

- The tree answers: where does this live, what does it inherit, who may authorize it?
- The graph answers: what does this change affect, which sibling Fields depend on it, what must be rechecked?

**THE TREE SAYS WHERE THE EXECUTOR IS. THE GRAPH SAYS WHAT WAS AFFECTED.**

## 5. THE FIELD IS THE IMPLEMENTATION UNIT

A Field is the **largest semantically coherent engineering space that can be
materialized and falsified under one stable semantic regime.**

A Field is NOT a ticket, file, component, endpoint, table, test suite, screen
or backend module.

| Unit | Meaning | Gated by human? |
|---|---|---|
| Field | One semantic regime (19 F00–F12) | Yes: review + commit approval |
| Subfield | Narrower region inside a Field, used for impact analysis | No |
| Work Unit | Bounded technical package inside a Field | No: reported, not separately committed |
| Package | Historical PKG-00..32 unit (14/15) | Closed |

Execution rule: the executor returns control to the human only at
`FIELD_COMPLETE` or at a **true new Case-3 boundary** (§8). Completing a Work
Unit is not a reason to return.

## 6. LOCAL AUTONOMY

Inside a Work Unit, the executor may freely choose: implementation form,
refactoring, internal naming, equivalent algorithms, test design, local
restructuring, tools, technical retry.

Local autonomy may never change: domain meaning, human preference,
authority, governance, protected effects, parent boundaries, canonical state
semantics.

**FREEDOM OF FORM ≠ FREEDOM OF SEMANTICS.**

## 7. CANDIDATE, EFFECT, GOVERNANCE

```text
CANDIDATE ≠ EFFECT        AI OUTPUT ≠ CANONICAL STATE
PROPOSAL ≠ AUTHORITY      PERSISTED ≠ TRUE        EXISTS ≠ AUTHORIZED
```

**Governance** is the relational structure of possible and effective
change: which states are reachable, which relations hold, where boundaries
arise, which changes may become effective. Approval workflows, policies,
monitoring and role lists are at most mechanisms inside governance.

**Effect gate**: the boundary immediately before a candidate becomes
effective state.

```text
CANDIDATE → FIELD RESOLUTION → VALIDITY → EVIDENCE → AUTHORITY → BOUNDARY
          → EFFECT GATE → EFFECTIVE STATE → RECONSTRUCTION
```

In NQUIRY the effect gate is `commit.coordinator.CommitCoordinator` with
BND-014 commit-time revalidation (NQ-DEC-011, NQ-DEC-014). It is the
**single governed commit boundary** for canonical writes. A parallel writer
that bypasses it is a First Broken Relation (§11), even when it is locally
correct.

**Authority provenance** recorded by the effect gate must reference the
*actual* authority source. It must never be fabricated to satisfy a column
shape. Since F02 (HD-6, §13) the effect gate admits exactly these typed
authority sources:

| Source | Meaning | Reference recorded |
|---|---|---|
| BINDING | A current `HumanAuthorityBinding` of the required class at the exact scope | the binding id |
| ROLE | A role-sourced operation authority the architecture names explicitly (e.g. AUTH-DEP-CH-001 Facilitator creates Challenge) | the current role assignment id |
| FOUNDING | The HARD-DEP-001 Option-A founding act: a verified human creating a Workspace | the founding Command id |

## 8. THE RECURSION CONDITION (THREE CASES)

For every unresolved next relation: *can it be legitimately derived from the
current Field?*

1. **YES**: resolve autonomously, test, continue.
2. **NO, but the options are functionally interchangeable** and do not
   materially change the Field: choose a coherent option, record it, test,
   continue.
3. **NO, and closing it would create** human meaning, preference, business
   purpose, authority, a protected effect, a parent-Field change, an
   external consequence or new semantic truth: stop autonomous closure →
   request authority → record the boundary → incorporate the decision →
   reconstruct → continue.

There is no hidden fourth case.

**Meaning condition**: `UNKNOWN ≠ HUMAN AUTHORITY REQUIRED`. Ask only when
resolving the unknown would *create* meaning, preference, value, purpose or
authority the Field does not contain. Technical openness is resolved
locally.

## 9. HUMAN AUTHORITY AS BOUNDARY CLOSURE

Human authority is not continuous supervision. It is a closure event at a
genuine boundary:

```text
UNRESOLVED RELATION → AUTHORITY REQUEST → HUMAN DECISION → RELATION CLOSED
→ FIELD RECONSTRUCTION → AUTONOMY CONTINUES
```

Previously closed relations are invalidated only if the new Delta actually
affects them. Every human decision is recorded as provenance (Work Unit
report + reconciliation into 16, §14).

## 10. REUSABLE GOVERNED RUNTIME

| # | Capability | NQUIRY home |
|---|---|---|
| 01 | Distributed state machine | `domain.*_transitions`, DB transition triggers, record versions |
| 02 | Field resolver | Workspace/Session/Challenge context queries, capability projections |
| 03 | Transition engine | `resolve_session_transition*`, `resolve_burst_transition*` |
| 04 | Integration and acceptance tests | `tests/`, `apps/web/tests`, real-stack lane |
| 05 | Authority resolver | `authority.resolver.AuthorityResolver` |
| 06 | Effect gate | `CommitCoordinator` + BND-014 |
| 07 | Provenance and audit | commands/attempts, commit_units, audit_events, outbox |
| 08 | Reconstruction loop | per-request re-resolution, post-commit reread, projection/replay |

**THE RUNTIME REMAINS. THE FIELD CHANGES.**

## 11. FAILURE AND SWEEP PROTOCOLS

**First Broken Relation**: symptom → walk upstream → find the first relation
that does not hold → identify its authoritative home → repair the minimum
legitimate root → propagate forward → retest → reconstruct. Never patch the
frontend, handler, repository or test merely because that is where the
failure became visible.

**Recursive DeepSweep** (after every meaningful change): trace outward:
changed relation → producer → consumer → parent Field → siblings →
persistence → runtime → API → frontend → tests → reports. Ask: *what else
did this touch?*

**Inverse DeepSweep** (for every visible or consequential effect): walk
backwards: visible effect ← frontend ← projection ← API ← application ←
command/query ← boundary ← authority ← domain transition ← evidence ←
canonical state ← persistence ← originating relation. If any link is
mocked, inferred, fabricated or fixture-created, the Work Unit is not
complete.

## 12. TEST-DRIVEN FIELD EXECUTION

Before every Work Unit, record:
- what must become true;
- what must remain impossible;
- what relations may change;
- what would falsify the work.

Then: RED → minimum coherent change → GREEN → relation tests → Field
integration → affected sibling regression → architecture gates → runtime
proof → browser proof (human-visible work) → reconstruction.

A test written after its implementation is accepted only when the report
classifies the deviation.

Test ladder (expand by relation impact, not by habit):

| Level | Scope |
|---|---|
| L0 | direct behavior |
| L1 | owning module |
| L2 | producer / consumer relations |
| L3 | active Field integration |
| L4 | affected sibling Fields |
| L5 | global architecture and static gates |
| L6 | real runtime proof |
| L7 | real browser semantic proof |
| L8 | Field-end affected regression |

`LOCAL GREEN ≠ FIELD GREEN`.

**Browser proof classes**. Always name which class a claim rests on:
- **MOCKED BROWSER PROOF**: real browser, API responses fulfilled by
  `page.route()`. Proves component/contract behavior only. It is **never**
  runtime proof.
- **REAL-STACK BROWSER PROOF**: real browser → real web app → real FastAPI →
  real authentication → real database with migrations → real Commands,
  governance, authority and persistence. No `page.route()`, no fabricated
  responses, no raw inserts simulating governed effects.

## 13. FRONTEND-FIRST MATERIALIZATION LAW

**FRONTEND-FIRST MATERIALIZATION ≠ FRONTEND-DEFINED SEMANTICS.**

Frontend-first changes **implementation order**. It does not change
**semantic authority**. Within a Field, each visible capability is built as a
vertical slice, starting from the stakeholder-visible behavior and walking
backwards:

```text
VISIBLE ACTION → FRONTEND → API → APPLICATION → BOUNDARY → AUTHORITY
→ DOMAIN TRANSITION → EFFECT GATE → COMMIT → AUDIT → PERSISTENCE
→ PROJECTION → UPDATED FRONTEND
```

A clickable UI that bypasses this chain is not complete.

Rules:
- Controls derive from **server capability projections**
  (`SERVER CAPABILITY → UI AFFORDANCE`), never from client role checks.
  A capability projection is a presentation of currently resolved
  authority, not authority itself. Commands always re-resolve.
- Distinct outcomes stay distinct in the UI: COMMITTED, DENIED, REJECTED,
  STALE, INDETERMINATE, NOT_FOUND, NETWORK_FAILURE.
- `UI DEBOUNCE ≠ IDEMPOTENCY`. Idempotency reaches the application boundary.
- Fixtures may be shown only when labelled NON_PROOF and never as canonical
  stakeholder proof.
- A semantic Field contains its own frontend. Do not split one capability
  into a backend Field, then an API Field, then a frontend Field.

## 14. PERSISTENT DOCUMENTATION, REVIEW AND COMMIT

After every Work Unit: `docs/implementation/field-reports/<FIELD>/<WU>.md`.
Minimum sections: mission, parent/current Field, relation materialized,
initial/target state, files changed, test-first intent, RED, implementation,
GREEN, direct/producer/consumer tests, Field integration, sibling regression,
architecture gates, runtime/browser/accessibility/responsive/visual proof,
Recursive and Inverse DeepSweep, First Broken Relation, authority
boundaries, human decisions used, limitations, mock/fixture/external
ceilings, git state, result.

After every Field: `FIELD_REVIEW.md` and `CHATGPT_REVIEW.txt` (19 §14/§15).

**DOCUMENTATION HARD LAW** (human-authorized 2026-09-24, applied from F02 on):

- Documentation is part of implementation, not a report written afterwards.
- Every Work Unit is documented under `docs/implementation/field-reports/<FIELD>/`.
  **No undocumented Work Unit may be considered complete.**
- Architecture-level resolutions (human decisions, closure of a gap,
  authority/scope rules, effect-gate contract changes) are reconciled into
  the authoritative ledgers (16 §41, this document §15, the affected
  architecture file) in the same Work Unit that makes them. A Work-Unit
  report alone is not enough.
- After every material Delta the report documents the recursive integration
  and reconstruction chain:
  `changed relation → parent → affected siblings → governance → authority →
  persistence → API → frontend → tests → reconstructed Field`.
- **No undocumented Field may be FIELD_GREEN.**

Human decisions recorded in Field reports are reconciled into the 16
ledger with provenance (16 §41). A historical proof report is never
rewritten. It is corrected by a successor reconciliation record.

**No-commit law**:

```text
WORK UNIT COMPLETE ≠ COMMIT AUTHORIZED
FIELD GREEN        ≠ COMMIT AUTHORIZED
FIELD COMPLETE → FULL PROOF → FIELD REVIEW → CHATGPT REVIEW → HUMAN REVIEW
→ EXPLICIT COMMIT APPROVAL (FIELD_COMMIT_APPROVED Fxx) → COMMIT
```

Never stage, commit or push without that explicit approval.

## 15. HUMAN DECISIONS RECORDED UNDER THIS ARCHITECTURE (F02)

Supplied by the human operator on 2026-09-24 for Field F02. Reconciled into
16 §41 as NQ-DEC-032..037 (REC-002..REC-009; HD-7/HD-8 were added after the
first reconciliation, HD-9 in WU-02.12, so the earlier range "032..034" was
incomplete. Corrected in F02 WU-02.12).

- **HD-1 (Session control scope)**: `SESSION_CONTROL_RIGHT` is
  **SESSION-scoped** for Session transition authority. Exact authority must
  resolve at `SESSION:<session_id>`. No implicit Challenge→Session
  inheritance. A WORKSPACE-scoped binding is not sufficient for a specific
  Session transition. No undocumented automatic Session authority. The
  CreateSession → transition lineage must be explicit and testable.
- **HD-3 (second local human)**: a DEV-ONLY local identity provisioning
  mechanism may create a local identity record for development proof only.
  It must not create membership, role, binding, Facilitator status or
  Session authority. Those flow only through the governed product.
  `DEV IDENTITY ≠ MEMBERSHIP`, `IDENTITY ≠ ROLE`, `ROLE ≠ AUTHORITY`.
- **HD-6 (effect-gate authority source)**: hand-written writers beside the
  effect gate are not accepted as permanent architecture. CommitCoordinator
  / BND-014 carry typed authority sources (at minimum BINDING, ROLE,
  FOUNDING). No fabricated UUID provenance. No fake binding. Audit provenance
  references actual, reconstructable authority provenance.

- **HD-7 (Session participation join authority, GAP-09-007)**: the holder
  of `SESSION_CONTROL_RIGHT` at `SESSION:<id>` admits an active member of
  the Session's Workspace as a participant (explicit, audited, BINDING-
  sourced Command). No self-join. Participation still grants no operation
  authority beyond the source-explicit question-submission right (02 §12.4,
  09 §28). Decided by the human operator on 2026-09-24 when F02 hit the
  boundary.
- **HD-8 (TRN-SESS-004 participant context)**: at least one current
  SessionParticipation must exist before the Session opens Question
  Generation (and the coupled Burst start). Decided by the human operator,
  2026-09-24.
- **HD-9 (prototype Burst control, 16 §41 REC-009 / NQ-DEC-037)**: for the
  current prototype, Session-scoped `SESSION_CONTROL_RIGHT` (at
  `SESSION:<id>`) closes Burst control, for Burst start and manual Burst
  completion. An explicit PROTOTYPE NARROWING of 04 §36–39 / 05 §20
  (Facilitator + ACTIVE Session FacilitatorScopeBinding), which remain the
  architecture's broader model and stay OPEN for production (NQ-GAP-080).
  No automatic Session control grant, no inheritance from Challenge
  authority, no role-only inference. Decided by the human operator,
  2026-09-24, in answer to the bootstrap reconstruction's Case-3 request.
  Corrects F02 WU-02.7, which had classified this reading as Case 1.

## 16. FINAL LAW

Do not sacrifice architecture to make the product look finished. Do not
sacrifice product visibility to keep architecture invisible. **Make the
governed architecture visible and clickable.**
