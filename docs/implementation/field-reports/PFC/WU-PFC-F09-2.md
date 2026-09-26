# WU-PFC-F09-2 — Workspace isolation and session sweep over every route

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F09-2 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · F09 |
| Colour / role / model | RED · application / boundaries / API · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26). |
| Derivation | 19 §29 internal Work Units "Workspace isolation sweep" and "session/security sweep"; TESTS FIRST "cross-Workspace access" and "session expiry". The F09 map found HTTP cross-Workspace coverage for only ~7 of 26 routes, and expiry coverage for one. |
| Current state / predecessor | `pfc-integration` `e5bc490`; `checkpoint-PFC-F09-1` → `3dbb6c6`. Migration head `c3b8e5a1f7d2`. |
| Baseline | Live 1792 passed / 2 skipped; no-DB 905 passed. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. |
| Authoritative home | 13 P-22 (T13-P22-CROSS-WORKSPACE: "no disclosure/mutation", DENIED); 12 AC-12-024 ("Workspace mismatch is denied before protected data disclosure"); 06 BND-001 (identity), BND-002 (Workspace resolution), BND-003 (membership); 10 §4.1 (a denied attempt is recorded, not executed). |
| Authorized delta | A sweep generated against the application's route table, plus the root repair of every defect it exposes within the Field. **Not in scope:** normalizing "unknown UUID" versus "not your Workspace" reason codes (see §4); SecurityEvent persistence on denial (touches principals, HA-09/HA-10). |
| Must become true | Every route denies an outsider (member of another Workspace) targeting Workspace A. The response carries no protected data (`kind`/`reasonCode`/`result` only; no A identifiers, versions or states). No canonical or governance row changes. Any logged attempt is DENIED. Every route answers an expired session with 401 `denied`, with no change. |
| Must remain true | Members' outcomes: `stale` (with versions) for members, 404 for a member naming an unknown Session, all F02/F03/F04 HTTP semantics. |
| Must remain impossible | A Session fact (version, state) reaching a non-member; a member of B reaching A's Session through B's URL; a route silently escaping the sweep. |
| Falsifiers | `tests/e2e/test_pfc_f09_2_isolation_sweep.py`: 57 cases, including a route-coverage guard generated from `app.routes`. |

## 2. Execution record

**1 RED (right reason).** The corrected sweep was run on the pre-repair handlers: **9 failed, 38 passed**. All 9 are the same defect.
- An outsider calling any of the 9 Session-command routes on Workspace A received HTTP 409 `{"kind":"stale","reasonCode":"STALE_VERSION","expectedVersion":1,"currentVersion":4,"currentState":"QUESTION_GENERATION"}`.
- That discloses A's Session version and state to a non-member (`evidence/f09_2_red.txt`).

The first draft of the sweep had wrong assumptions. They were corrected before the repair was judged:
- The older route family answers every outcome with HTTP 200 and states it in `kind` (09 §77). It was accepted as such.
- A denied attempt is recorded in the command log (10 §4.1). That is checked to be DENIED instead of being counted as a mutation, and scoped to Workspace A attempts only.
- `POST /workspaces` was added to the sweep (the coverage guard caught it).
- The members body used an invalid role literal (`Contributor`, not `CONTRIBUTOR`).

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   a non-member receives A's Session version + state in a `stale` envelope
CONSUMER         9 Session-command routes (begin-setup, begin-challenge-capture,
                 open-question-generation, burst, participants, complete-burst,
                 begin-analysis, analysis/request, analysis/clustering/request)
RELATION         caller -> identity/Workspace/membership -> Session state
PRODUCER         session_control_handler._load_fresh (4 routes), analysis_begin_handler,
                 analysis_request_handler, burst_completion_handler: the expected-version
                 comparison raised SessionVersionStale(current, state) BEFORE the boundary
                 chain in _run (BND-001/002/003) was evaluated
FBR              protected Session state is disclosed before BND-002/BND-003 (12 AC-12-024)
```

**3 HOME.** 06 BND-001/002/003 order; 12 AC-12-024; 13 P-22.

**4 REPAIR** (+ ~95 lines in 4 files).
- `session_control_handler.deny_unless_member(...)` evaluates BND-001 → BND-002 (when the Session exists) → BND-003 against the Workspace the caller names. It raises `SessionCommandDenied` (mapped to `denied`) before any Session fact.
- It is called from `_load_fresh` (4 routes) and in `analysis_begin_handler`, `analysis_request_handler` and `burst_completion_handler`, right after the Session is read and before the not-found and stale checks.
- `burst_capture_handler` already evaluated its authority chain first and is unchanged.
- Precedent kept: like `_run`'s existing foreign-Workspace precheck, this denial records no command attempt.
- A member naming an unknown Session keeps the accepted 404: BND-002 is only in the precheck when the Session exists.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| 9 Session-command routes | AFFECTED | Deny before disclosure. |
| Members' outcomes (stale, blocked, not_found, committed) | NOT AFFECTED | Precheck ALLOWs members. The F02/F03/F04 HTTP suites are green. |
| `burst_capture`, F02 queries, legacy routes, auth, decide | NOT AFFECTED (already correct) | Proven by the sweep. |
| Boundary evaluators / authority | NOT AFFECTED | Reused unchanged. |
| CYAN | NOT AFFECTED | Members never see a changed outcome. |
| Existence-disclosure normalization | NOT CHANGED (observation) | See §4. |

**6–9 PROOFS.**
- **Local:** ruff, mypy and the checks.
- **Integration:** real HTTP through FastAPI on PostgreSQL, for every route. That covers the outsider case, the cross-URL case (member of B, A's Session, B's URL) and the expired-session case.
- **Preservation:** the F02/F03/F04 HTTP suites and the full regression.
- **Regression:** `evidence/f09_2_regression.txt`.

**10 MUTATION.** `scripts/pfc_f09_2_mutation_proof.py`: **6/6 KILLED**, sources restored. The mutants are:
- the precheck removed at each of the 4 sites
- BND-002 dropped (the cross-URL path)
- the precheck result not enforced

**11 INVERSE.**
```text
{"kind":"denied","reasonCode":<BND-002/003 reason>} for a non-member
  <- deny_unless_member (BND-001 -> BND-002 -> BND-003 on the named Workspace)
  <- before SessionVersionStale / SessionNotFound can be raised
  <- the Session row is read but none of its facts leave the handler
```

**12 DEEP SWEEP.** Authority leakage: none, since the precheck only adds denials for non-members. Semantic drift: none for members. The route-coverage guard makes a future unswept route fail CI.

**13 INVERSE DEEP SWEEP.** For each route, the only information a non-member receives is `kind=denied` plus a boundary reason code. This is asserted by the key-set and no-A-identifier checks.

## 3. Falsifier map

| Falsifier | Cases | Proves |
|---|---|---|
| `test_the_sweep_covers_every_route` | 1 | the sweep equals `app.routes` minus the two unauthenticated entry points |
| `test_an_outsider_is_denied_on_every_route_without_disclosure_or_mutation` | 21 | P-22 / AC-12-024 on every Workspace-scoped route |
| `test_an_outsiders_workspace_list_never_contains_workspace_a` | 1 | list scoping |
| `test_an_expired_session_is_no_identity_on_every_route` | 24 | BND-001 on every authenticated route |
| `test_a_member_of_b_cannot_reach_a_session_of_a_through_bs_own_url` | 10 | BND-002 object/Workspace match |

## 4. Observations (not changed, recorded)
- **Existence signals on unguessable identifiers.** Several routes answer "unknown id" differently from "exists but not yours": the decide route gives `rejected DECISION_NOT_FOUND` versus `denied NO_ACTIVE_MEMBERSHIP`; the older routes give `WORKSPACE_NOT_FOUND` / `SESSION_NOT_FOUND` versus a membership denial.
  - No protected data is disclosed. The identifiers are random UUIDs.
  - Normalizing would change the accepted F01–F03 denial vocabulary seen by members and CYAN.
  - Left unchanged. The recovery precedent (`test_recovery_service.py`) shows the stricter form if Human Authority wants it.
- **SecurityEvent on denial** (11 TH-04, 13 P-22 "SecurityEvent"): no live path writes one. `security_event_writer` has no grants, so this touches principals (HA-09) and remains open.

## 5. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F09-2`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F09: IN_PROGRESS.
