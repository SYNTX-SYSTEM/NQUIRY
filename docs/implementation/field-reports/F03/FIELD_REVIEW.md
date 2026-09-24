# NQUIRY FIELD REVIEW REPORT

## Field
F03 — PROTECTED HUMAN QUESTION FIELD (19 §23; regime: protected human generation)

## Status
FIELD_GREEN_WITH_DISCLOSED_CEILINGS. Implemented in the worktree `.claude/worktrees/local-login-auth`
(branch `worktree-local-login-auth`, HEAD `bea864b` = F02 published). NOT committed, NOT tagged, NOT pushed.
Awaiting human Field Review. LOCAL_GREEN != FIELD_GREEN != PUBLISHED_FIELD.

## Authoritative parent
SFE (20) -> product architecture 00-18 + 16 -> F02 (`2f33be1`, tag `field-F02`). Homes: 02 §12/§13/§14/§17, 03 TRN-Q-001 / TRN-BURST-005 / TRN-SESS-005 / §16 / §25.5, 04 AUTH-DEP-Q-001 / BURST-005 / SESS-005, 06 BND-008 / BND-014, 09 §4.3/§28/§30, 10 §4.4/§64, 16 §41 REC-011..017.

## Target path (achieved)
QUESTION_GENERATION -> ACTIVE HUMAN_ONLY Burst -> authorized participant -> human capture -> exact immutable `original_text` -> manual authorized completion -> capture closed (Session QUESTION_CAPTURE) -> frozen human question set -> provenance.
The Field ends at QUESTION_CAPTURE (03 §16 forbids QUESTION_GENERATION -> ANALYSIS; TRN-SESS-006 is F04).

## Human decisions used
HD-10 PAUSE/RESUME out of scope (NQ-DEC-038); HD-11 no automatic timer completion (NQ-DEC-039); HD-12 deterministic questions-only form rule (NQ-DEC-040, prototype narrowing, NQ-GAP-023 open); HD-13 visibility (NQ-DEC-041); HD-14 controller self-admission (NQ-DEC-042); HD-15 PARTICIPATION source (NQ-DEC-043). Existing: HD-1, HD-6, HD-7, HD-8, HD-9. No new Case-3 boundary appeared.

## Initial state
F02 published. Materialized but unused in production: `questions` (immutability trigger), `question_bursts`, `burst_question_memberships`, `BurstRepository.add_member/complete`, `QuestionRepository.create_root`. No Command, route or UI for capture or completion. Baseline live-DB suite: 1360 passed / 2 skipped.

## Final state
Capture and completion are governed Commands through CommitCoordinator/BND-014; HTTP + UI + real-stack proof exist. Live-DB suite 1535 passed / 2 skipped (+175 tests).

## Work Units
WU-03.0 ledger reconciliation; WU-03.1 FBR-F03-5; WU-03.2 FBR-F03-2/6 + EC-1; WU-03.3 FBR-F03-4; WU-03.4 FBR-F03-3 + FBR-F03-7; WU-03.5 HD-12 + BND-008; WU-03.6 capture Command; WU-03.7 completion Command + real concurrency; WU-03.8 read side; WU-03.9 HTTP; WU-03.10 frontend + real stack; WU-03.11 closure + FBR-F03-8. Reports: `WU-03.*.md`.

## First Broken Relations (FBR) found / repaired
| Id | Relation | Repaired at |
|---|---|---|
| FBR-F03-2 | freeze <-> concurrent capture; PREPARED Burst accepted memberships | migration e5a1b3c8f204 (trigger: ACTIVE-only, row lock) + handler row lock |
| FBR-F03-3 | completion <-> unresolved acknowledged capture (no persisted link) | migration f6b2c4d9a318 `commands.target_refs`; `list_unresolved_for_target`; completion blocker |
| FBR-F03-4 | fingerprint <-> reconstructability (mutable inputs) | `domain.burst_membership` scheme V2 over immutable birth facts (disclosed deviation from 14 §19) |
| FBR-F03-5 | effect gate <-> participation authority | PARTICIPATION source: `authority_source`, BND-014, migration c4e9a2b7d135 |
| FBR-F03-6 | membership order <-> concurrency | `UNIQUE (burst, captured_order)` + order assignment under the row lock |
| FBR-F03-7 (discovered) | a BND-014 DENY left the attempt IN_PROGRESS forever (would block completion once attempts are linked) | `CommitCoordinator._mark_denied_at_gate` |
| FBR-F03-8 (discovered, Inverse DeepSweep) | PKG-28 GetSession returned every captured Question to any member while ACTIVE (bypass of HD-13) | `application.session_view_query` (COMPLETED only); seed fixture frozen |
| EC-1 hardening | one Burst per Session only partly enforced | full `UNIQUE (session_id)` |
FBR-F03-1 was Case 3, closed by HD-12.

## Architecture materialization
- Domain: `burst_input` (HD-12), `burst_membership` fingerprint V2.
- Boundaries: `participation_right` (one definition), `bnd_005_participation` (precommit), BND-014 PARTICIPATION branch, BND-008 capture actor + BURST_INPUT_VALID (REQUIRE when not established); application guard mirrors the actor rule.
- Application: `burst_capture_handler`, `burst_completion_handler`, `frozen_set`, `inquiry_queries` (HD-13 server-side filtering, capabilities), `session_view_query`.
- Persistence: 3 migrations (below); `burst_repository` locking + order; `command_repository` target refs; `inquiry_directory` captured-question reads.
- API: `POST .../burst/questions`, `POST .../transitions/complete-burst`; wire contract carries only `originalText` + `expectedBurstVersion`.
- Frontend: `components/f03/*`, `lib/burst.ts`, Session page integration.

## Effect gate / provenance
Capture audit: PARTICIPATION, ref = participation id, scope `SESSION:<id>`, `state_after_ref` never `session:*` (EC-2). Completion audit: BINDING at `SESSION:<id>`, before `session:QUESTION_GENERATION|burst:ACTIVE`, after `session:QUESTION_CAPTURE|burst:COMPLETED`; `establishedBy` resolves QUESTION_CAPTURE and QUESTION_GENERATION uniquely.

## MIGRATIONS
c4e9a2b7d135 (audit CHECK admits PARTICIPATION); e5a1b3c8f204 (freeze trigger ACTIVE-only + FOR SHARE, capture-law trigger, UNIQUE(burst,order), UNIQUE(session_id)); f6b2c4d9a318 (`commands.target_refs` + GIN index). Head f6b2c4d9a318. Down-migrations provided. Applied to `nquiry_test` and to the dev DB `nquiry` (no session had more than one Burst).

## TDD RED evidence (chronological)
# F03 RED evidence log
## WU-03.1 (FBR-F03-5) tests/e2e/test_participation_authority_source.py
RED: collection ImportError: cannot import name 'ParticipationAuthority' from 'boundaries.authority_source'. GREEN after: authority_source.py + bnd_014_commit.py + audit/models.py + migration c4e9a2b7d135 -> 12 passed.
## WU-03.2 (FBR-F03-2, -6, EC-1) tests/e2e/test_f03_membership_law.py
RED: 9 failed, 2 passed (PREPARED insert, non-participant x3, left participant, foreign author, foreign challenge, duplicate order, second burst row all DID NOT RAISE). GREEN after migration e5a1b3c8f204 -> 11 passed. Side effects: PKG-07 constraint tests adapted (participation plumbing), seed_local_demo adapted.
## WU-03.3 (FBR-F03-4) tests/domain/test_burst_membership_fingerprint.py
RED: 8 failed, 1 passed (AttributeError: 'str' object has no attribute 'value' -- old signature keyed on record versions). GREEN: domain/burst_membership.py V2 scheme -> 9 passed. PKG-07 constraint tests adapted to new signature.
## WU-03.4 (FBR-F03-3 + discovered FBR-F03-7) tests/e2e/test_f03_unresolved_capture.py
RED: 6 failed (AttributeError: 'SqlAlchemyCommandRepository' has no 'list_unresolved_for_target'); FBR-F03-7 test RED: attempt.outcome None after BND-014 DENY (assert outcome is DENIED). GREEN after migration f6b2c4d9a318 + command_repository + coordinator._mark_denied_at_gate -> 7 passed; full suite 1393 passed, 2 skipped.
## WU-03.5 (HD-12) tests/domain/test_burst_input.py
RED (module absent): ModuleNotFoundError: No module named 'domain.burst_input' (collection error). NOTE: test and implementation were authored in the same step; RED reproduced afterwards by removing the module. GREEN: 36 passed.
## WU-03.5b BND-008 capture input tests/boundaries/test_bnd_008_capture_input.py
RED: 8 failed (no input_check field / no CAPTURE_REQUIRES_HUMAN_ACTOR). GREEN after bnd_008 + burst_contamination -> 8 passed; legacy BND-008 tests + differential adapted (valid input supplied for capture).
## WU-03.6 capture handler tests/e2e/test_capture_burst_question.py
RED: ModuleNotFoundError: No module named 'application.burst_capture_handler' (collection error). GREEN: 39 passed (one test-helper fix: retry uses fresh attempt id).
## WU-03.7 completion + frozen_set tests/e2e/test_complete_burst.py, test_f03_concurrency.py
RED: collection error (application.burst_completion_handler / frozen_set absent). GREEN: 23 passed (one test fix: a retry re-sends the same expected versions).
Concurrency mutation check: removing FOR NO KEY UPDATE from get_by_session_for_update -> all 4 concurrency tests FAIL; restored -> 4 passed. (real two-connection race on a cloned DB)
## WU-03.8 projection tests/e2e/test_f03_projection.py
RED: 11 failed, 1 passed (KeyError 'questionSet'/'serverNow'/actions CAPTURE_QUESTION). GREEN after inquiry_queries + inquiry_directory -> 12 passed.
## WU-03.9 HTTP tests/e2e/test_http_f03.py
RED: 11 failed, 1 passed (404 route absent). GREEN after http_f02 dispatch + inquiry routes -> 12 passed.
## FBR-F03-8 (found by Inverse DeepSweep) tests/e2e/test_f03_legacy_session_view.py
RED: 1 failed, 1 passed (legacy GetSession returned Alice's question to every member while ACTIVE). GREEN after session_view_query (COMPLETED only) + seed freezes its fixture set -> 2 passed.
Disclosed deviations: WU-03.5 test and implementation were authored in the same step (RED reproduced afterwards by removing the module); the real-stack specs, vitest and components were written after their contracts and their RED is the missing module / failing real-stack run (a failed first run is recorded in WU-03.10).

## Direct tests (new)
175 backend tests in 12 files (participation source 12, membership law 11, fingerprint 9, unresolved capture 7, form rule 36, BND-008 capture 8, capture handler 39, completion 23, concurrency 4, projection 12, HTTP 12, legacy view 2) + 25 vitest. See `PROOF_MATRIX.md`.

## Integration / regression
Affected suites adapted with disclosure: PKG-07 constraint tests (participation plumbing; fingerprint signature), BND-008 legacy + differential tests (valid input supplied), `seed_local_demo.py`. Live DB (`nquiry_test`): 1535 passed / 2 skipped. Pure: 808 passed / 729 skipped. Concurrency mutation check: removing the row lock fails all 4 race tests.

## STATIC GATES
ruff format/check clean; mypy 172 files clean; architecture dependency, provider-SDK import, test-only import gates PASS; migrations static + live PASS (25 revisions, single head); eslint, tsc clean; `next build` OK (7 routes). AST gate against parallel canonical writers still passes (no new writer beside the coordinator). No AI gateway import on the F03 path (static test).

## REAL STACK PROOF (containers rebuilt from this tree; no network interception)
Whole lane 10 passed (F02 6 + F03 4; desktop + Pixel 7). F03 path: Session at QUESTION_GENERATION with ACTIVE HUMAN_ONLY Burst; Alice submits A (exactly as typed, HUMAN); a statement is rejected with "Nothing was stored"; Alice submits B; Bob sees none of Alice's questions; the self-admitted controller captures and sees only its own + a count; the Owner has no capture form and the server's reason is shown; in-page API calls: Owner capture denied, forged `origin` rejected, participant completion denied, outsider read/write denied; a stale tab is `blocked` after completion; the controller completes through an explicit confirmation; every member (controller, Alice, Bob, Owner) sees the identical frozen set in capture order, exactly as typed, with authors, HUMAN marks, "Verified", and established-by = CMD_COMPLETE_BURST / controller / BINDING / `SESSION:<id>`. Screenshots: `visual/`.
Mocked component-contract lane (against the rebuilt web): 39 passed (no F03-specific mocked spec added; component contracts are vitest).

## ACCESSIBILITY / RESPONSIVE
axe-core WCAG 2.0 A/AA on the real pages (participant with open Burst incl. rejection alert, controller with the completion confirmation, frozen set for controller and participant): 0 serious/critical. Keyboard-only capture (Tab to the textbox, type, Ctrl+Enter) and completion (Tab, Enter, confirm with Enter); visible focus asserted. No horizontal overflow at 1280 px and Pixel 7. The timer is not a live region; outcomes use `role=status|alert`. Ceiling: no screen-reader run, no automated contrast beyond axe.

## Recursive DeepSweep
PASS. Reconstruction chain per WU: participation source -> membership law -> fingerprint -> unresolved-capture link -> validator -> capture -> completion -> read side -> HTTP -> UI -> real stack. Producers and consumers agree: every outcome kind emitted by the two routes is parsed as that kind by `inquiryClient` (vitest, 6 kinds); the wire contract, the projection and the Command share the same blocker functions (`capture_blocker`, `complete_burst_blocker`) and the same participation rule.

## Inverse DeepSweep
PASS after FBR-F03-8. Visible frozen set <- server `questionSet.frozen` <- canonical re-read (`verify_frozen_set` recomputes the fingerprint) <- committed CMD_COMPLETE_BURST (BINDING @ SESSION:<id>, one bundle) <- Burst ACTIVE with committed human Questions <- N committed CMD_CAPTURE_BURST_QUESTION (PARTICIPATION right, exact text, HUMAN origin, DB triggers) <- admission by the controller <- F02 chain <- verified login. The sweep from the READ side found FBR-F03-8 (a second read path for the same Questions). No other reader of Question text exists (`grep`: only `inquiry_directory` and the legacy view).

## Known limitations / ceilings
- HD-12 is FORM only: a statement ending in "?" is accepted; a question ending in a closing quote/bracket is rejected. NQ-GAP-023 stays open.
- The 2000-character cap and NUL/surrogate refusal are technical storage safeguards (disclosed, not product rules).
- Empty Burst cannot complete (`NO_CAPTURED_QUESTIONS`, readiness O-6; derivable, not a new decision; Case 3 only if stakeholders need empty Bursts).
- INDETERMINATE capture blocks completion until a recovery record resolves it; the recovery worker/UI that resolves records is F09 scope.
- Timer: elapsed + about four minutes as non-authoritative guidance; no countdown, no effect (HD-11). Exact duration (CONFLICT-007, NQ-GAP-022/032) stays open.
- Leave/remove participation (NQ-GAP-079 remainder) and production Burst control (NQ-GAP-080) open.
- Two different keys with identical text are two legitimate captures (no content dedup: not in the architecture).
- No live shared list, no author names to peers during ACTIVE (HD-13).
- `apps/web` frontend uses a client-side interval for the elapsed display only.
- The concurrency proof clones `nquiry_test` (needs CREATEDB; skipped otherwise).
- Legacy PKG-28/29 decision surface remains; its Burst questions now appear only after completion.

## MOCK / FIXTURE / EXTERNAL CEILINGS
Fixture: `seed_local_demo.py` (NON_PROOF; now starts, fills and freezes its Burst by direct inserts); dev identities carry no authority (HD-3). Mock: DB `connect` monkeypatch in HTTP tests; scripted failure injectors; hand-inserted participation `left_at` / membership revocation as test plumbing (leave/revoke Commands are not in scope). External: no AI provider path exists in F03 (HARD-DEP-002 untouched); GAP-14-001 production identity provider open.

## F04 readiness
Prerequisites for TRN-SESS-006 / AIOP-001 are delivered: Session QUESTION_CAPTURE, Burst COMPLETED, `verify_frozen_set` (fingerprint recomputable from immutable facts, also after normalization), human origin + author on every raw Question, DB-immutable membership. Open F04 tensions: GAP-03-006 (AI unavailable vs no-skip path), NQ-GAP-003 (AI observer), HARD-DEP-002. F04 NOT started.

## Documentation status
Persisted in the canonical tree: 16 §41 REC-011..017 + §6 table/YAML, 20 §7 + §15A, 04 §40 note, README, RUNTIME_OPERATION, `F03/` (STATUS, WU-03.0..03.11, PROOF_MATRIX, this review, CHATGPT_REVIEW, readiness §16, visual/). The final reports live in the canonical documentation tree (`docs/implementation/field-reports/F03/`) of the working tree of branch `worktree-local-login-auth`, not in a scratch location. They must be synchronized to the main checkout at publication (as in F02).

## Publication diff classification (git diff, uncommitted)
- Tracked modified (30): 3 architecture docs + STATUS, README, RUNTIME_OPERATION; application/boundaries/commit/persistence/audit/domain modules; `apps/api` routes; `apps/web` page, client, css; `scripts/seed_local_demo.py`; adapted tests (PKG-07 constraints, BND-008 x2).
- Untracked (F03 work): 3 migrations, new modules (domain, boundaries, application), 12 backend test files + helper, web components/lib/tests/real-stack specs, `F03/` reports and 6 PNGs.
- WITHHOLD from publication (not F03 work, as in F02): `apps/web/AGENTS.md`, `apps/web/CLAUDE.md` (generated by `next dev`).
- Ignored/not part of the diff: `apps/web/.next`, `apps/web/test-results`, `.env`.
- Secrets scan of the diff and new files: clean (matches are field names `session_token`, `password` labels only). `git diff --check` clean. Index empty.
- Git diff summary at writing: 30 tracked files changed (+1075/-60 before this report), plus untracked entries listed above.

## Commit status
Committed locally as `0d59ae3f9be5f3a3297d43ab55c70005c41aa68d` after `FIELD_COMMIT_APPROVED F03`. Not pushed, not tagged.

## Recommended status
READY FOR HUMAN FIELD REVIEW: YES.
