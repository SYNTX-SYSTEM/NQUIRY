# WU-PFC-PCPG-1 — FBR-PCPG-1: RAW USER INTENT → GOVERNED PROMPT OBSERVATION (R-01/R-02 only)

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-1 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application / API materialization |
| Human authorization | "NQUIRY / SIMPLIX — PRE_CALL_PROMPT_GOVERNANCE — BLUE MATERIALIZATION" (2026-09-30). Names the RED predecessor `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/`, checkpoint `checkpoint-PFC-SFE-PCPG`, expected commit `395ecf7a2f99d4a0134069d6ac8ce4f1d99ea8c3`, and the target FBR-PCPG-1. |
| RED predecessor (verified) | `checkpoint-PFC-SFE-PCPG` peels to `395ecf7a2f99d4a0134069d6ac8ce4f1d99ea8c3`, matching the authorization exactly. `pfc-integration` HEAD was already at that commit (clean except the withheld RED-freeze commit itself, `ahead 1` of `origin/pfc-integration`). |
| Worktree / branch | `worktrees/pfc-integration` · `pfc-integration`. No new worktree needed — the existing one already sat at the pinned checkpoint. |
| State isolation | `nquiry_pfc_int_test` (existing, already migrated to `e8c2a5f1b7d4`, `verify_migrations` PASS before and after — this Work Unit adds no migration). |
| Baseline | Live (pre-repair): the falsifier suite fails with `404` on every route call (the ingress does not exist) — see §2 RED. Full-repository live suite (launched before this Work Unit's files existed, running throughout): **2007 passed / 2 skipped / 0 failed** — see §2 PRESERVATION. |
| E1 (independently re-derived, not assumed from the brief) | Root relation: R-01 (ingress). No PCPG code, module or route exists anywhere in the tree or in `origin/master`/`pfc-integration` history beyond the RED-freeze commit itself (`grep` for `pcpg`/`PRE_CALL_PROMPT_GOVERNANCE`/`SIMPLIX` across `packages/`, `apps/`: zero hits). FBR chain confirmed in RED's own order: FBR-PCPG-1 (root, break type (a): nothing exists) → FBR-PCPG-2 (semantic delta → operation mapping, absent) → FBR-PCPG-3 (data classification, absent, GAP-11-006 OPEN) → FBR-PCPG-4 (Case 3: HA-PCPG-1) → FBR-PCPG-5 (external: HARD-DEP-002). Existing-bypass sweep: `ai_gateway` is imported only by `analysis_input.py`/`analysis_runtime.py`/`analysis_system.py`/the gateway itself/the mock provider/`ai_record_repository.py` — none reachable from a free-text HTTP body; the three existing free-text contracts (Burst capture `originalText`, Challenge frame fields, Decision `rationale`) are fixed contracts, not a raw-intent path (fixture X1 holds already). No SFE correction found. |
| Authorized delta | FBR-PCPG-1 only: R-01 (ingress) + R-02 (scope validation). Explicitly NOT R-03..R-12 (Field reconstruction, Pulse, semantic sweep, deltas, governance, composition, chain results, capability, projections) — those are FBR-PCPG-2 and later, each its own Work Unit. |
| Must become true | An authenticated, scope-validated, side-effect-free observation ingress exists: `POST /workspaces/{workspaceId}/prompt-observations`. |
| Must remain true | Every existing F01/F02/F03/F04/F05/F09 route, semantic and test; the migration head; the architecture/provider-SDK/test-only-import gates. |
| Must remain impossible | Any Command, Event, canonical write, authority mutation, provider call or network egress from this route; any raw-intent content in a log, an audit row or a security event; a foreign or non-member Workspace/Session fact disclosed; a fabricated semantic observation, delta or capability value (none of R-03..R-12 exist yet — emitting one would be FABRICATED per E6). |
| Falsifiers | `tests/e2e/test_pcpg_observation_ingress.py`: 28 cases (isolation, input-shape, verbatim/I-01, side-effect/X5, static bypass/mutation-source checks). |

## 2. Execution record

**1 RED (right reason).** The falsifier suite was written first and run against the unrepaired tree (the three new files moved aside, the router unwired from `main.py`): **28/28 failed**, every case for the correct reason — `404` (the route does not exist at all), confirming P-01 ("no relation exists") directly rather than by assumption. Two authoring bugs in the test harness itself were found and fixed before judging RED (both disclosed, neither touches the Field): the shared-fixture `SqlAlchemyLocalCredentialRepository.create(...)` call was missing its required `now=` argument, and `application.http_dispatch.connect` also needed monkeypatching (login goes through `http_dispatch.dispatch_login`, not `http_f02`) — the same two-module patch `test_http_f02.db_app` already uses.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   an authenticated, Workspace-scoped actor has no route that accepts a raw
                 drafted intent as a side-effect-free observation
CONSUMER         (future) R-05..R-12 — none exist yet; this Work Unit is R-01/R-02 only
PRODUCER         none (ABSENT — break type (a), not an invariant violation and not Case 3)
FBR              FBR-PCPG-1 (00_FIELD.md §12), confirmed root by E1 above
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-01, R-02 (this Field, the ingress); `application.workspace_context.resolve_workspace_context` (existing BND-002/BND-003 producer, consumed not re-implemented); `application.inquiry_queries.{QueryDenied,QueryNotFound}` (existing denial/not-found vocabulary, consumed not re-implemented).

**4 REPAIR** (3 new files, 2 files touched for wiring).
- `packages/application/pcpg_observation.py` — the real producer. `observe(...)`: validates the raw intent and declared purpose are present and bounded (R-01 precondition; `[IMPLEMENTATION CHOICE]` bounds, disclosed in the module docstring — RED leaves the exact size to BLUE); then calls `resolve_workspace_context` (BND-001 already proven by the caller's verified session; BND-002/BND-003 here) **before** touching any Session fact (I-06); then, only if a `session_id` was claimed, reads it and returns it **only if** it belongs to the validated Workspace, else `QueryNotFound("SESSION_NOT_FOUND")` — the identical vocabulary and shape every other Session-scoped query in this codebase already uses, so a foreign Session is indistinguishable from an unknown one. Computes a SHA-256 digest of the exact UTF-8 bytes of the raw intent (for a future basis, `04_OBSERVATION_RESULT.md` §9 — not built here, only the one fact worth capturing at the single point the text exists in memory). Calls no mutating repository method anywhere (proved statically, §3 falsifier `test_the_observation_producer_calls_no_mutating_repository_method`).
- `packages/application/http_pcpg.py` — the thin dispatch layer, reusing `_with_actor`/`_denied`/`_rejected`/`_uuid` from `http_f02` (the established cross-module reuse convention already used by `http_f04.py`/`http_f05.py`). Maps `ObservationInputRejected` → `rejected` (400), `QueryDenied` → `denied` (403), `QueryNotFound` → `not_found` (404), success → `kind: "ok"` (the EXISTING query envelope — no new top-level kind is introduced, I-20).
- `apps/api/src/nquiry_api/http/pcpg.py` — the thin FastAPI router, `POST /workspaces/{workspace_id}/prompt-observations`. No `Idempotency-Key` requirement (R-01 precondition: "not a Command").
- `apps/api/src/nquiry_api/main.py` — two lines: import and `include_router`.
- **Deliberately absent from the response body:** any semantic observation, delta, FBR/MLT/NVT/HAR, or capability value (`GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND`). The body carries a `governanceObservation: null` field, documented in the module as "always null until FBR-PCPG-2..5 close" — an honest absence marker, not a stub value, so a future Work Unit's real value is never confused with this one's placeholder.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| New route `POST /workspaces/{w}/prompt-observations` | NEW | This Work Unit. |
| Every existing route (F01/F02/F03/F04/F05/F09) | NOT AFFECTED | No existing file's behaviour changed; `main.py`'s only edits are additive (new import, new `include_router` line). |
| `resolve_workspace_context`, `QueryDenied`, `QueryNotFound`, `_with_actor` and siblings | NOT AFFECTED | Consumed exactly as already defined; nothing in them was edited. |
| Migrations | NOT AFFECTED | None added; head unchanged (`e8c2a5f1b7d4`). |
| CYAN | NOT AFFECTED | Out of this Field's boundary (00_FIELD.md §11) and untouched. |
| `ai_gateway` / provider path | NOT AFFECTED | No import from the two new `application` modules reaches it (static falsifier, §3). |

**6–9 PROOFS.**
- **Local:** `ruff check`/`ruff format --check` clean on all 5 touched/new files; `mypy` (same 4 source files, `packages`/`apps/api/src`/`apps/worker/src`/`scripts` on `MYPYPATH`) — 0 issues; `check_architecture_dependencies.py`, `check_provider_sdk_imports.py`, `check_test_only_imports.py` — all PASS; `verify_migrations.py` — unchanged head, PASS.
- **Producer proof:** `observe(...)` returns exactly R-01's OUTPUT ("an observation request bound to a verified principal", opaque raw-intent DATA) plus R-02's OUTPUT ("a validated scope ... the named Session ... only if it belongs to that Workspace") and nothing else — asserted by the `ok`-path tests (workspace fields, session presence/absence, byte-exact echo, correct digest) and by the absence of any `commands`/`audit_events`/`outbox_events`/`security_events`/`questions`/`sessions` row change across every branch (`test_no_row_changes_anywhere_for_ok_denied_rejected_or_not_found`).
- **Consumer proof:** the denial/not-found vocabulary is the SAME `QueryDenied`/`QueryNotFound` every other `inquiry_queries` read already answers with; the HTTP envelope mapping is the SAME `_denied`/`_rejected` helpers every other F02+ route uses — nothing downstream needs a new parser branch.
- **Adversarial proof (05 §2 cases touching R-01/R-02):** X1 (raw prompt bypass — no other path exists, proved by E1's sweep, not re-proved per-request since there is exactly one ingress); X2/I-16 (static import sweep, no `ai_gateway`/`ai_contracts`/provider import from either new `application` module); X3 (no client-supplied field is read as capability — the route accepts only `rawIntent`/`sessionId`/`declaredPurpose`, and no capability value exists in the response to forge); X4 (an outsider — a genuine cross-Workspace member, not `f03_support`'s same-Workspace `ctx["outsider"]` fixture, which is a member — gets the uniform `denied`, with and without a real Session id named, and the body carries `{kind, reasonCode}` only); X5 (no row changes, any branch).
- **MUTATION proof (manual, 3 guards; disclosed method — no permanent mutation script was authored for this single-relation Work Unit, unlike WU-PFC-F09-2's route-sweep scale):**
  1. Dropped `NotAWorkspaceMemberError` from the caught exception tuple → both outsider falsifiers failed (the exception propagated uncaught instead of a clean `denied`). Restored; suite green.
  2. Removed the `RAW_INTENT_MAX_CHARS` bound check → `test_oversized_raw_intent_is_rejected_and_nothing_is_read` failed (`200` instead of `400`). Restored; suite green.
  3. Removed the `session.workspace_id != context.workspace.id` ownership comparison → `test_a_session_of_another_workspace_is_not_found_never_disclosed` failed (`200` instead of `404`, the foreign Session accepted). Restored; suite green (byte-diff confirmed clean restoration).
- **PRESERVATION / REGRESSION — SUPERSEDED PRELIMINARY RUN.** A first full-repository live suite was launched in the background BEFORE any PCPG file was created (collection happens at process start, so it never imported or collected the new files at all) and ran for its full 38 minutes largely concurrently with this Work Unit's own edits, including the 3 mutation-proof edit/restore cycles — 2007 passed, 2 skipped, 0 failed. Correctly rejected as the closing proof (Human Authority, 2026-09-30): it never collected the final tree at all, so it could not have caught a defect that only exists once every file is present together. Superseded by the final run below, which found exactly such a defect.

- **PRESERVATION / REGRESSION — FINAL, AUTHORITATIVE RUN.** A fresh full-repository live suite was started only after `git status`/`git diff` confirmed every WU-PFC-PCPG-1 file and the final `main.py` edit already existed, with no file touched from that moment until the run exited (verified: `git diff` after the run is byte-identical to `git diff` before it, SHA-256 `f0e527564...`; the 5 untracked files' content hashes are unchanged). Result:

  ```text
  1 failed, 2034 passed, 2 skipped in 2132.45s (0:35:32)
  FAILED tests/e2e/test_pfc_f09_2_isolation_sweep.py::test_the_sweep_covers_every_route
  ```

  **This is a genuine regression, not noise, and this Work Unit is NOT closed.** `test_the_sweep_covers_every_route` (WU-PFC-F09-2's own coverage guard, "a route added later without an entry here fails `test_the_sweep_covers_every_route`" — its own docstring, quoted verbatim, predicting exactly this) computes `served` from live `app.routes` and compares it against a hand-maintained `ROUTES` table in that file. `POST /workspaces/{workspace_id}/prompt-observations` is now a real, authenticated route in `app.routes` and is correctly absent from `ROUTES`, since this Work Unit never touched that file (in scope for THIS materialization pass: FBR-PCPG-1 only; extending an F09 artifact was not authorized). The guard did exactly its job.

  Consequence for THIS Field's own law: `tests/e2e/test_pcpg_observation_ingress.py` proves R-01/R-02's own isolation falsifiers (X4) directly and those still pass (§6 below) — the new route is not provably unsafe. But the canonical, whole-route-table cross-Workspace sweep (13 P-22, 12 AC-12-024) does not yet cover it, so "every route" is no longer true of the tree as a global invariant, and closing WU-PFC-PCPG-1 as FIELD_GREEN for the repository as a whole would misstate that. The one-line, mechanical fix (adding `("POST", "/workspaces/{ws}/prompt-observations", {"rawIntent": "?"})` and its expected exemption/body shape to that file's `ROUTES` table) was identified but **not applied** in that pass, per that turn's explicit "do not modify code."

**COVERAGE GUARD REPAIR (Human Authority, 2026-09-30).** Worktree reconciliation confirmed `pfc-integration` isolated first (`git status --short`: the same 6 entries as before, nothing else; the unrelated F04 architecture/review files a UI showed belonged to a different worktree entirely — `.claude/worktrees/local-login-auth`, branch `worktree-local-login-auth`, `HEAD c9d86ba` — never touched by this Work Unit; see the worktree-reconciliation table below). With isolation proven and the ONLY remaining preservation failure being the known coverage guard, the minimum legitimate repair was applied: one entry added to `tests/e2e/test_pfc_f09_2_isolation_sweep.py`'s existing `ROUTES` table —

```text
("POST", "/workspaces/{ws}/prompt-observations", {"rawIntent": "Why would an outsider write here?"}),
```

— placed after the existing `/decisions/{decision}/decide` entry, with a comment explaining why the route (Session referenced only as an optional BODY field, never a path segment) structurally falls outside the file's own `_SESSION_ROUTES` filter without weakening it. Nothing else in that file was touched: no exemption added, no filter loosened, no case skipped or `xfail`ed, no assertion relaxed. This is a pure ADDITION: `served == swept` now holds because `swept` grew to match `served`, not because `served` shrank or a check was bypassed. `ruff format` reformatted the multi-line tuple for line length; `ruff check` and `mypy` (4-file scope) stay clean; `git diff --stat` for this file: `+13 lines` only (a comment block plus the one route tuple), no deletions.

**Isolation sweep re-run, scoped:** `tests/e2e/test_pfc_f09_2_isolation_sweep.py` — **84 passed** (was: 1 failed among the file's own tests, pre-repair; the new route added exactly 2 parametrized cases — one to the outsider-denial sweep, one to the expired-session sweep — both pass; it correctly does NOT appear in `_SESSION_ROUTES`, for the structural reason above, so its cross-Workspace-Session case stays proven by this Work Unit's own `test_a_session_of_another_workspace_is_not_found_never_disclosed` instead, not duplicated here).

**28 PCPG falsifiers re-run:** **28 passed**, unaffected (`tests/e2e/test_pcpg_observation_ingress.py` was not touched by the coverage repair).

**FINAL, AUTHORITATIVE full-repository run (second pass, over the complete, final tree including the coverage-guard repair):** started only after `git status`/`git diff` confirmed the complete 7-entry final state (2 modified, 5 new — the coverage-guard edit is the only addition since the first final run); tree verified byte-identical before/after (tracked `git diff` SHA-256 `7f4122d03...` both times; all 5 untracked files' content hashes unchanged). Result:

```text
2037 passed, 2 skipped in 2348.89s (0:39:08)
```

**Zero failures.** This is a real increase over the prior final run's 2034 passed (the coverage repair added 2 new parametrized isolation cases and kept the 1 previously-failing case, now passing: 2034 + 2 (new cases) + 1 (repaired case) = 2037). **This is now the closing preservation proof.**

**10 INVERSE SWEEP (E6, extended to the coverage-guard repair).**

The new `ROUTES` tuple's own trace: it names the literal path and method of a REAL route already registered in `app.routes` (origin class (a), confirmed by `test_the_sweep_covers_every_route` itself asserting `served == swept`); it is not a second, independently-computed description of routing (it reuses the EXISTING sweep mechanism every other route already goes through, not a new one); it grants no capability and asserts no authority result of its own — the actual DENIED/expired-session assertions come from the SAME shared `_call`/`_client`/`_counts` machinery every other `ROUTES` entry already uses. No FABRICATED, DUPLICATED, STALE-CAPABLE, BYPASSED or PROMOTED finding.

**10a INVERSE SWEEP (E6, over this Work Unit's own PCPG outputs — unchanged from the first pass, restated).**
```text
workspaceId/name      <- context.workspace (a real WorkspaceRecord read by resolve_workspace_context)   -- canonical, sourced (a)
session (if present)  <- ports.sessions.get(session_id), equality-checked against context.workspace.id  -- canonical, sourced (a)
rawIntent              <- the request body, carried through unmodified                                   -- raw-intent span (b), byte-identity asserted
rawIntentDigestSha256  <- sha256(rawIntent.encode("utf-8")), computed once, in this call only             -- pure function of (b); not persisted, not cached
declaredPurpose        <- the request body, carried through unmodified, or null                           -- raw-intent-adjacent claim (b); never read as fact
observedAt             <- ports.clock.now(), read at the moment of return                                 -- (a)/(c): the real clock, not stored, not reused across calls
governanceObservation  <- literal null                                                                    -- honest absence: no producer exists yet (FBR-PCPG-2..5)
```
No value traces to a cache, a client-supplied field, or another observation. No DUPLICATED value (nothing here is also produced by an existing readiness function — this relation is genuinely new). No PROMOTED value (nothing here is presented as authority, evidence or a decision). No BYPASSED value (the only way to reach `pcpg_observation.observe` is through this one route, which is the only caller of it in the tree). **VERDICT: CLEAN** for R-01/R-02's own outputs. E6 was not run over R-03..R-12 because they do not exist in this Work Unit — there is nothing yet to trace.

**11 FIELD RECONSTRUCTION.** FBR-PCPG-1 is closed. Given `00_FIELD.md` §12's own dependency order (re-verified, not merely trusted, in E1 above), the **next First Broken Relation is FBR-PCPG-2: SEMANTIC DELTA → CANONICAL OPERATION MAPPING** — "no vocabulary relation mapping an observed action onto the existing operation catalog... What is missing is its consumable index: per operation, its execution class, authority home, readiness producer, effect class and data inputs." This is NOT a Human Authority boundary (RED's own HA-PCPG-1 gates FBR-PCPG-4, three relations later) and not a future Field. It is the next legitimate Work Unit under this same authorization.

## 3. Falsifier map

| Falsifier (file: `tests/e2e/test_pcpg_observation_ingress.py`) | Cases | Proves |
|---|---|---|
| `test_a_member_gets_an_ok_observation_...` / `test_the_named_session_is_returned_only_when_...` | 2 | R-01/R-02 OUTPUT shape |
| `test_a_session_of_another_workspace_is_not_found_...` / `test_an_unknown_session_id_is_not_found` | 2 | R-02 "only if it belongs to that Workspace" |
| `test_an_outsider_is_denied_uniformly_...` / `..._naming_a_real_session_...` / `test_an_unauthenticated_caller_is_denied` / `test_an_unknown_workspace_is_denied_not_not_found` | 4 | I-06, X4 |
| `test_missing_raw_intent...` / `..._empty_or_whitespace...` (×3) / `..._non_string...` / `..._oversized_raw_intent...` / `..._raw_intent_at_the_boundary...` / `..._oversized_declared_purpose...` / `..._malformed_workspace_id...` / `..._malformed_session_id...` | 10 | R-01 FAILURE STATE (malformed/oversized input, nothing read) |
| `test_raw_intent_is_echoed_byte_exact_...` (×5) | 5 | I-01 "verbatim"; P-02-style traceability |
| `test_an_authority_claim_in_the_raw_intent_changes_nothing_but_the_echo` | 1 | I-01 (narrowed to what this Work Unit can prove — no governance evaluation exists yet) |
| `test_no_row_changes_anywhere_...` / `test_calling_twice_is_not_deduplicated_...` | 2 | X5, I-18, R-01 "not a Command" |
| `test_no_import_path_from_this_field_to_a_provider_or_ai_gateway` / `test_the_observation_producer_calls_no_mutating_repository_method` | 2 | X2/I-16, P-01 (static) |

## 4. Deliberate exclusions (not defects; FBR-PCPG-2..5, later Work Units)

- No semantic observation (R-05/SIMPLIX): no clause, action, target, modality or purpose is derived from the raw intent. The whole text is opaque DATA end to end in this Work Unit.
- No delta, no execution class, no RESULT/REASON (R-06/R-07): there is no operation index yet (FBR-PCPG-2's own target).
- No composition, FBR/MLT/NVT/HAR, no capability value (R-08..R-10): nothing to compose yet.
- No actor-safe projection distinct from the raw response (R-12): CYAN consumption is out of this Field's boundary entirely (00_FIELD.md §11) and this Work Unit's response is not yet shaped for it.
- No basis / freshness mechanism (R-14, `04_OBSERVATION_RESULT.md` §9): the digest is captured for future reuse, but no rule-set version, canonical-fact-version list or absence-fact list is assembled yet — there is nothing yet whose freshness would need proving.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW — CLOSED.** The coverage-guard regression found by the first final-preservation pass is repaired (§2, "COVERAGE GUARD REPAIR"), by pure addition — no existing check weakened, skipped, exempted or relaxed. The second, final full-repository run over the complete tree (including the repair) is clean: **2037 passed, 2 skipped, 0 failed**, tree verified byte-identical before and after. FBR-PCPG-1 (R-01/R-02) is materialized, independently falsified (28/28), and now also proven repository-wide by the pre-existing WU-PFC-F09-2 isolation sweep (84/84, the new route included). Not committed, not tagged, not pushed. FBR-PCPG-2 (SEMANTIC DELTA → CANONICAL OPERATION MAPPING): OPEN, not Case 3, next in dependency order.

## 6. Worktree reconciliation (Human Authority request, 2026-09-30)

A UI diff view appeared to show F04 architecture/review files alongside WU-PFC-PCPG-1's own changes. Reconciled against the actual repository state on disk:

| Item | Value |
|---|---|
| WORKTREE (this Work Unit) | `/home/codi/Entwicklung/nquiry/worktrees/pfc-integration` |
| BRANCH | `pfc-integration` |
| HEAD | `395ecf7a2f99d4a0134069d6ac8ce4f1d99ea8c3` (unchanged throughout — the pinned RED checkpoint; nothing committed) |

`git status --short` (this worktree, final):
```text
 M apps/api/src/nquiry_api/main.py
 M tests/e2e/test_pfc_f09_2_isolation_sweep.py
?? apps/api/src/nquiry_api/http/pcpg.py
?? docs/implementation/field-reports/PFC/WU-PFC-PCPG-1.md
?? packages/application/http_pcpg.py
?? packages/application/pcpg_observation.py
?? tests/e2e/test_pcpg_observation_ingress.py
```
`git diff --stat` (tracked files only, exact):
```text
 apps/api/src/nquiry_api/main.py             |  2 ++
 tests/e2e/test_pfc_f09_2_isolation_sweep.py | 13 +++++++++++++
 2 files changed, 15 insertions(+)
```

| File | Classification |
|---|---|
| `apps/api/src/nquiry_api/main.py` | `PCPG_WU_1` — 2 purely-additive lines (import + `include_router`) |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` | `PCPG_WU_1` — the coverage-guard repair, one `ROUTES` entry added |
| `apps/api/src/nquiry_api/http/pcpg.py` | `PCPG_WU_1` — new |
| `packages/application/http_pcpg.py` | `PCPG_WU_1` — new |
| `packages/application/pcpg_observation.py` | `PCPG_WU_1` — new |
| `tests/e2e/test_pcpg_observation_ingress.py` | `PCPG_WU_1` — new, 28 falsifiers |
| `docs/implementation/field-reports/PFC/WU-PFC-PCPG-1.md` | `PCPG_WU_1` — this report |
| `docs/implementation/field-reports/F04/review/BACKEND_REVIEW_BUNDLE.md` | `PRE_EXISTING_UNRELATED` — committed, hash-bound reviewed input from Field F04; the ONLY file `ruff format --check .` flags in this worktree, unchanged, matching the identical disclosed exception already recorded in `WU-PFC-I1.md` ("Inherited; not modified") |

**No F04 architecture/review file (`F04_ARCHITECTURE_RECONSTRUCTION.md`, `FIELD_REVIEW.md`, `HUMAN_DECISIONS.md`, `F04/review/`, or the modified `16_DECISION_GAP_REGISTER.md`/`20_SYSTEM_FIELD_ENGINEERING.md`/`F04/STATUS.md`) exists anywhere in `pfc-integration`.** They belong entirely to a DIFFERENT worktree on the same machine — `/home/codi/Entwicklung/nquiry/.claude/worktrees/local-login-auth`, branch `worktree-local-login-auth`, `HEAD c9d86ba` — a separate, unrelated BLUE line (F04, not PCPG) with its own pre-existing uncommitted work, confirmed present and unchanged there (read-only check; not modified by this session). Classification for those files, from `pfc-integration`'s perspective: **`OTHER_ACTIVE_FIELD`** (real modifications, but in a physically different worktree and Field). The most likely explanation for the UI showing them together is a diff view that aggregates across this machine's several concurrent worktrees (also present: `auth-identity`, `f04-implementation`, `frontend-symbiotic`, `pfc-a1`, plus at least one further, unrelated session running its own suite against a `nquiry_purple_test` database during this proof — none inspected further, none touched). No file outside `pfc-integration`'s own 7-entry change set was modified by this Work Unit.
