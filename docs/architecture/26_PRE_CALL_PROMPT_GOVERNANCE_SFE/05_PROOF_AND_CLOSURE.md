# 26 · PRE_CALL_PROMPT_GOVERNANCE — 05 PROOF AND CLOSURE

**This file is authoritative for:**
- the proof conditions of the PCPG Field;
- the coverage of the adversarial falsifiers;
- the closure levels: when RED may call the SFE architecture complete, and when BLUE may call the Field green.

**It may not decide:** the test tree, test names or tooling (BLUE derives them), or any status beyond the ladder `LOCAL_GREEN ≠ FIELD_GREEN ≠ REVIEWED_FIELD ≠ PUBLISHED_FIELD` (20, 25).

Each proof condition has two proof forms:
- **RED:** a derivation on paper, from this SFE and the existing architecture, that the condition holds for every fixture and follows from the invariants.
- **BLUE:** an executable falsifier against the materialized Field. Each falsifier fails first against the unrepaired tree, then passes; a mutation proof kills its guard.

---

## 1. Proof conditions

| ID | Condition | Established by | RED proof | BLUE proof (falsifier shape) |
|---|---|---|---|---|
| P-01 | **Raw intent has no bypass path.** The only relations from a raw intent are R-01 → R-12. No path reaches a Command, a provider, storage or a log with content. | I-06, I-16, I-18; R-01, R-13 | the relation graph has no other outgoing edge from the raw intent; R-13 re-derives | route and egress sweep: an outsider or expired session gets the uniform denial; no provider adapter is reachable from the ingress; row counts and logs are unchanged after observations |
| P-02 | **Semantic observation is traceable.** Every stratum-2 item cites its span; every stratum-1 value cites its source and version. | I-02; R-03, R-05 | the §5 record requires it | each item's span is inside the raw intent; each quoted fact equals the producer's value at the basis |
| P-03 | **Unknown does not become guessed.** | I-04; B-01 | the precedence puts INDETERMINATE before any permission | the fixture UNKNOWN_INTENT; ambiguous-verb and out-of-vocabulary cases give INDETERMINATE and never ALLOWED |
| P-04 | **All candidate deltas are explicit.** Every requested action yields a delta; implied deltas cite their chain relation. | R-06 | completeness rule in R-06 | every requested action span maps to a delta; no IMPLIED delta is without a chain relation |
| P-05 | **All material deltas have governance results.** Every delta has exactly one RESULT with a reason; decision-class effects are HUMAN_COMMAND. | I-08; R-07; `04_OBSERVATION_RESULT.md` §4–§6 | the §6 precedence is total | every delta has a result and a reason; no selection, approval or decision is PROVIDER_COMPUTATION |
| P-06 | **The composed effect is evaluated.** | I-10; R-08 | §7.1 | the splitting fixtures (AUTHORITY_ESCALATION §S) |
| P-07 | **FBR is reconstructable** from the delta records alone. | I-19; R-09 | §7.2 is a function of the records | recompute FBR from the served records; it equals the served FBR |
| P-08 | **MLT is reconstructable.** | I-19; R-09 | §7.3 | recompute the MLT; it equals the served MLT; it contains no HUMAN_COMMAND or EXTERNAL_EFFECT |
| P-09 | **Freshness is enforced.** | §9; R-14 | derive-on-read; no cache | the fixture STALE_FIELD: after each basis change the next read differs accordingly |
| P-10 | **A stale observation cannot authorize execution.** | I-14; R-13 | no gate consumes an observation | there is no execution path in this Field; a static check proves no consumer accepts an observation as authority (future R-13 proves the forged case) |
| P-11 | **CYAN cannot create capability.** | I-15; B-10 | CYAN has no input path to the server's evaluation | a forged request with capability fields changes nothing; CYAN code contains no derivation (review plus a static check) |
| P-12 | **No provider can be reached before governance.** | I-16; B-08 | no edge to a provider exists | an egress guard during observation fixtures; no import path from the ingress to a provider adapter |
| P-13 | **No blocked delta can cross provider projection.** | I-11, I-13, I-17; R-11 | §11 | for every fixture the eligible set contains no blocked delta's semantics, no forbidden instruction, secret, cross-Workspace or DC-07 content |
| P-14 | **No parallel authority model exists.** | I-03, I-20; R-07 | every authority result is sourced from 04 producers | for every NQUIRY operation the delta's authority and state result equals the existing capability result at the same basis; no new authority vocabulary exists |
| P-15 | **No parallel state model exists.** | I-07, I-20 | Pulse is a view | every Pulse element maps to a canonical record; no PCPG-owned status exists |
| P-16 | **No parallel policy model exists.** | I-20 | data classes and provider policy are quoted | no PCPG-owned data class, provider rule or permission flag; no persistence of observations |
| P-17 | **Inverse reconstruction succeeds.** Every stratum-3 and stratum-4 output walks back to canonical facts, interpretations with spans, and the rule set. | I-02, I-19 | E6 over the fixtures | an automated inverse check over the fixture results |
| P-18 | **Field reconstruction after material change is defined.** | R-14 | §9 enumerates the changes | each change class in STALE_FIELD produces the defined re-derivation |
| P-19 | **All fixtures pass:** every fixture's expected result is derived. | fixtures/ | each fixture file's DERIVATION section | each fixture is executed against the materialized Field |
| P-20 | **All falsifiers fail correctly:** each adversarial case is refused for the stated reason, not by accident. | §2 | each case names its invariant and boundary | each case asserts the exact RESULT and REASON; a mutation of the guard makes it pass wrongly |

## 2. Adversarial coverage (every required falsifier has a home)

| Required falsifier | Fixture file (section) | Invariant / boundary |
|---|---|---|
| Prompt claiming authority | AUTHORITY_ESCALATION (A1) | I-01; B-02 |
| Role treated as authority | AUTHORITY_ESCALATION (A2) | B-02 |
| Unknown authority treated as permission | AUTHORITY_ESCALATION (A3); UNKNOWN_INTENT (U3) | I-04 |
| Delta splitting used to evade authority | AUTHORITY_ESCALATION (S1–S3) | I-10 |
| Raw prompt bypass | BYPASS (X1) | I-18; P-01 |
| Direct provider bypass | BYPASS (X2) | I-16 |
| Frontend-created capability | BYPASS (X3) | I-15 |
| Cross-Workspace context | DISCLOSURE (D1) | I-05, I-13 |
| Whole-Workspace disclosure | DISCLOSURE (D2) | I-13 |
| Secret disclosure | DISCLOSURE (D3) | I-13, I-17 |
| Blocked delta leaking into provider projection | DISCLOSURE (D4); PROCUREMENT | I-17; P-13 |
| Analysis becoming decision | DECISION_SUBSTITUTION (C1) | I-08 |
| Recommendation becoming selection | DECISION_SUBSTITUTION (C2); PROCUREMENT | I-08 |
| Selection becoming approval | DECISION_SUBSTITUTION (C3) | I-08 |
| Approval becoming execution | DECISION_SUBSTITUTION (C4) | I-08, I-11 |
| Lowest price becoming eligibility | PROCUREMENT; DECISION_SUBSTITUTION (C5) | I-09 |
| Budget fit becoming approval | PROCUREMENT; DECISION_SUBSTITUTION (C6) | I-09 |
| AI output becoming domain evidence | DECISION_SUBSTITUTION (C7); SOURCE_MUTATION (M3) | I-08, I-12 |
| AI output becoming human decision | DECISION_SUBSTITUTION (C8); NQUIRY_SESSION_AUTHORITY | I-08 |
| Source mutation | SOURCE_MUTATION (M1–M2) | I-12; B-05 |
| Proof ceiling escalation | SOURCE_MUTATION (M4–M5) | I-12; B-06 |
| Stale field / authority / source / provider policy | STALE_FIELD (T1–T4) | §9; I-14 |
| Unknown semantic relation guessed | UNKNOWN_INTENT (U1–U2, U4) | I-04; B-01 |

## 3. Closure levels

### 3.1 SFE_ARCHITECTURE_COMPLETE (RED may declare)
All of the following hold:
1. **Traceability:** every file has an authority statement, and no two files are authoritative for the same concept (inverse sweep, E6).
2. **Root references:** every invariant has a falsifier and an authoritative root; no invariant restates a canonical law without referencing its home.
3. **Relations:** every relation has producer, consumer, home, input, output, precondition, boundary, failure state, downstream and proof.
4. **Boundaries:** every boundary maps to an existing home.
5. **Coverage:** every required adversarial falsifier has a fixture section (§2).
6. **Derived expectations:** every fixture's expected result is **derived** in its file from the invariants and the canonical facts it states, and matches the brief's expected governance; or the file records and justifies the correction.
7. **Human Authority:** every open question is listed with a fail-closed default (00_FIELD §13), and none is answered by derivation.
8. **Inverse sweep:** the inverse sweep over this SFE finds no duplicate authority, state, boundary or policy; no interpretation promoted to authority; no capability token; no authoritative CYAN; no provider dependency; no prescribed implementation tree; no bypass.

### 3.2 FIELD_GREEN (BLUE may claim, per Work Unit and for the Field)
Beyond LOCAL_GREEN, each materialized relation has:
- producer proof and consumer proof;
- adversarial proof (§2 cases for that relation);
- a mutation proof killing its guards;
- an inverse sweep over its outputs;
- a Field reconstruction recording the next First Broken Relation.

The Field is FIELD_GREEN when P-01..P-20 hold executably and the remaining First Broken Relations are only Human Authority boundaries (HA-PCPG-*) or future Fields (SEND, provider).

### 3.3 Beyond
REVIEWED_FIELD requires human review of the materialized Field. PUBLISHED_FIELD is never claimed by an agent.

## 4. The closure loop (every material delta)

```
CURRENT FIELD → FIRST BROKEN RELATION → MINIMUM COHERENT DELTA → PRODUCER PROOF → CONSUMER PROOF
→ ADVERSARIAL PROOF → INVERSE SWEEP → FIELD RECONSTRUCTION → NEXT FIRST BROKEN RELATION
```

"File completed" and "tests green" are never closure by themselves.
