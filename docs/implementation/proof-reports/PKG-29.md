PACKAGE_ID: PKG-29
PACKAGE_TITLE: Human Decision UI
BUILD_PHASE: 11
VERDICT: PACKAGE_PASS

DESIGN_REVIEW_APPLIED_UPFRONT: Before any code was written, the user
relayed explicit reviewer guidance (following PKG-28's own externally-
found defects) that this package's own risk profile is categorically
higher than PKG-28's (PKG-28 was pure display; this package introduces
this codebase's first real interactive frontend controls that trigger
Commands). The following four requirements were treated as
DESIGN CONSTRAINTS from the first line of code, not retrofitted after
review:
1. No optimistic rendering -- addressed structurally in
   `DecisionSection`: the visible Decision state is EITHER the
   original server-read `decision` prop OR `override`, and `override`
   is set in exactly one place in the entire file: the `committed`
   branch of a real `recordHumanDecision` response. See AUTHORITY_PATH.
2. Each Decision action triggers only a Command, computes nothing
   itself -- `RecordDecisionForm` has no `if (userIsAllowed)` branch of
   any kind; `recordHumanDecision`'s only output is whatever
   `DecisionActionResult` the server actually returned. See
   AUTHORITY_PATH.
3. Adversarial tests (double-click, DENY-after-click, network failure
   during the decision call, forged/rejected option) written as part
   of this same implementation pass, not appended afterward -- see
   ADVERSARIAL_TEST_RESULTS, all 13 in `tests/e2e/decision.spec.ts`
   from this package's own first commit.
4. Every new closed vocabulary (`DecisionState`,
   `BoundaryDenialResult`) built as a `const` array with the type
   DERIVED from it, using `requireEnum` for runtime validation, from
   this package's own first line -- not cast with `as X` and retrofitted
   later. See `types.ts`'s own `DECISION_STATES`/`BOUNDARY_DENIAL_RESULTS`.

UPSTREAM_FILES_READ:
- `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md`: PKG-29 manifest
  entry (predecessors PKG-15,PKG-19,PKG-28; PROOF CLAIMS P-07,P-08,P-09;
  `GATE`/DAG line `PKG-15 + PKG-19 + PKG-28 -> PKG-29`), repository
  topology (`apps/web/app/...` single row, Phase 11, only PKG-28/29
  ever authorized to create files there), proof-claim table (P-07:
  `tests/authority/test_ai_non_authority.py` "AI sets DECIDED" -> BND-006
  DENY; P-08: `tests/authority/test_question_selection.py`; P-09:
  `tests/e2e/test_ai_decision_boundary.py` "recommendation persistence"
  -> "Decision remains UNDER_CONSIDERATION").
- `docs/architecture/NQUIRY_IMPLEMENTATION_MASTER.md:19111-19422` (the
  full embedded PKG-29 coding prompt) -- AUTHORIZATION, OBJECTIVE,
  ARCHITECTURAL_INVARIANTS ("AI RECOMMENDATION != HUMAN DECISION; HUMAN
  DECISION UI CREATES A NEW HUMAN-OWNED DECISION; DECIDED DOES NOT
  AUTO-EXECUTE"), NON_COLLAPSE_RULES, PACKAGE_BOUNDARY,
  FILES_ALLOWED_TO_CREATE ("apps/web Decision components/routes; typed
  API client extension; Playwright E2E" -- explicitly NOT
  "Question-selection components"), BOUNDARIES ("Server BND chain
  authoritative"), AUTHORITY ("UI never calculates DECISION_RIGHT"),
  EVIDENCE ("Consumed refs sent as context only"), AI ("Recommendation
  displayed separately"), FAILURE_RECOVERY ("Denied/stale server
  response leaves Decision unchanged"), PRE_IMPLEMENTATION_ATTACK_MODEL
  (6 mandatory package-specific attacks, minimum 5 total novel).
- 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §23 (`POST /decisions/{d}/consider`,
  `POST /decisions/{d}/decide` COMMAND rows -- "The exact HTTP paths
  are prototype interface choices"), §24 (items 10-12/15: "Question
  selection control", "Decision boundary showing that AI recommendation
  is not a Decision", "human Decision action for authorized holder",
  "minimal provenance/audit reconstruction view").
- `docs/architecture/07_EVIDENCE_AND_PROVENANCE.md` §54.8 ("Provenance
  Minimums by Artifact Class: Decision" -- exact minimal field list
  this package's own `DecisionProvenanceView` materializes).
- `docs/architecture/06_BOUNDARY_ARCHITECTURE.md` §12 (BND-006, "No AI
  output can cross BND-006 as an authority-bearing human decision").
- `packages/domain/decision.py` (PKG-15) -- `Decision`, `DecisionState`
  (2-value closed vocabulary), full field list and `__post_init__`
  invariants (a DECIDED row can never lack `decided_by_user_id`/
  `decided_at`/`selected_option`), read to transcribe `DecisionView`
  verbatim.
- `packages/application/human_decision_handler.py` (PKG-15) --
  `open_decision_consideration`/`record_human_decision`'s own real
  boundary-chain (BND-001..007), `HumanDecisionDenied`,
  `SelectedOptionNotCandidate` (the real backend guard this package's
  own "rejected" `DecisionActionResult` case mirrors), authority-scope
  convention (`CHALLENGE` for OPEN, `DECISION` for RECORD).
- `packages/boundaries/bnd_006_human_decision.py` -- `Bnd006Input`'s
  own `decision_origin` field, the exact mechanism 06 §12 uses to
  refuse AI-authored content presented as a human decision.
- `packages/ai_contracts/generation.py` (PKG-19) -- `AIGeneration`,
  `AIGenerationStatus`, confirmed `output_artifact_ref` is itself an
  opaque forward reference (no structured recommendation content is
  materialized anywhere in this codebase yet) -- read to justify
  `AiRecommendationView.summary`'s own disclosed opaqueness.
- Every existing PKG-28 file this package extends: `lib/api/types.ts`,
  `lib/api/client.ts`, `components/SessionViewContainer.tsx`,
  `components/NetworkErrorBanner.tsx`, `components/DeniedBanner.tsx`,
  `components/IndeterminateBanner.tsx`.
- `docs/implementation/proof-reports/PKG-15.md`, `PKG-19.md`,
  `PKG-28.md` -- PREDECESSORS_VERIFIED below.

PREDECESSORS_VERIFIED:
- PKG-15 (Human Decision, Build Phase 4): present, `PKG-15.md` exists
  with `VERDICT: PACKAGE_PASS`. Verified against actual
  `packages/domain/decision.py`/`packages/application/human_decision_handler.py`
  state at HEAD -- both real, both exercised by this package's own
  typed contract.
- PKG-19 (AI Gateway and MockProvider, Build Phase 6): present,
  `PKG-19.md` exists with `VERDICT: PACKAGE_PASS`. Verified against
  `packages/ai_contracts/generation.py` at HEAD.
- PKG-28 (Minimum frontend shell, Build Phase 11): present, commit
  `0a8569c`, `PKG-28.md` exists with `VERDICT: PACKAGE_PASS` (this
  session's own external review + retrofit already validated in full
  before this Human Gate).
Not self-reported: all three verified against actual repository state,
not only their own completion reports' own claims.

FILES_CREATED:
- `apps/web/lib/api/decisionClient.ts` -- `recordHumanDecision()`,
  `parseDecisionActionResult()`: the typed client extension for
  `POST /decisions/{d}/decide`. Reuses `client.ts`'s own
  `isRecord`/`requireString`/`requireEnum`/`apiBaseUrl` rather than a
  new generic helper file (this package's own FILES_FORBIDDEN_TO_MODIFY
  line explicitly forbids "broad generic utils/helpers/services/common
  dumping grounds").
- `apps/web/components/AiRecommendationPanel.tsx` -- 12 §24 item 11
  (AI-recommendation half): passive, zero interactive elements,
  visually/structurally separate from the Decision's own controls.
- `apps/web/components/RecordDecisionForm.tsx` -- 12 §24 item 12: the
  ONE interactive control this package introduces. A pure, dumb input
  collector with no network call and no success state of its own (see
  DESIGN_REVIEW_APPLIED_UPFRONT #1/#2); a ref-based double-submission
  guard in addition to the `disabled` attribute.
- `apps/web/components/DecisionProvenanceView.tsx` -- 12 §24 item 15:
  07 §54.8's own minimal Decision-provenance field list, rendered once
  `state === "DECIDED"`.
- `apps/web/components/DecisionSection.tsx` -- composes the above three
  plus the state machine (`idle`/`submitting`/`result`/`network_error`)
  that makes "no optimistic rendering" structurally true; renders
  `DeniedBanner`/`IndeterminateBanner` (reused from PKG-28) and a new
  inline rejected-banner for `SelectedOptionNotCandidate`/
  `StaleVersionConflict`-shaped rejections.
- `apps/web/tests/lib/decisionClient.test.ts` -- 12 Vitest tests.
- `apps/web/tests/components/decision-display.test.tsx` -- 5 Vitest
  tests (the two PASSIVE new components only -- see TESTS_CREATED for
  why `RecordDecisionForm`/`DecisionSection` are not tested here).
- `apps/web/tests/e2e/decision.spec.ts` -- 13 real Playwright tests
  against a real Chromium browser + a real running Next.js dev server.

FILES_MODIFIED:
- `apps/web/lib/api/types.ts`: added `DecisionId`, `DECISION_STATES`/
  `DecisionState`, `BOUNDARY_DENIAL_RESULTS`/`BoundaryDenialResult`
  (extracted from `SessionReadResult`'s own inline literal union, now
  reused by both `SessionReadResult` and the new `DecisionActionResult`),
  `AiRecommendationView`, `DecisionView`, `DecisionActionResult`;
  extended `SessionView` with `decision`/`aiRecommendation` (nullable,
  on the SAME `GET /workspaces/{w}/sessions/{s}` query PKG-28 already
  established, not a second invented endpoint).
- `apps/web/lib/api/client.ts`: exported `isRecord`/`requireString`/
  `requireEnum`/`apiBaseUrl`/`DEFAULT_API_BASE_URL`/`parseDecisionView`
  (previously module-private, now reused by `decisionClient.ts`);
  added `parseDecisionView`/`parseAiRecommendationView`, wired into
  `parseSessionView`; refactored `parseSessionReadResult`'s own
  `denied`/`indeterminate` cases to use `requireEnum`/a new
  `requireNonEmptyString` helper instead of inline literal comparisons
  (a minor, disclosed consistency cleanup enabled by the new shared
  vocabulary array, not a behavior change -- covered by PKG-28's own
  unmodified, still-passing tests).
- `apps/web/components/SessionViewContainer.tsx`: renders the new
  `DecisionSection` inside the existing `ok` branch, passing through
  `result.data.decision`/`result.data.aiRecommendation` -- still a
  pure pass-through of the server's own response, the same discipline
  every other field on this component already followed.
- `apps/web/components/NetworkErrorBanner.tsx`: `message` is now an
  optional prop (default unchanged, `"Unable to load this Session."`)
  so `DecisionSection` reuses this exact component for a
  `recordHumanDecision` network failure instead of a near-duplicate
  new file.
- `apps/web/tests/lib/client.test.ts`, `apps/web/tests/e2e/session-view.spec.ts`:
  `OK_BODY` fixtures updated to include `decision`/`aiRecommendation`
  (required by the now-extended `SessionView` type) -- one PKG-28
  fixture includes a real `UNDER_CONSIDERATION` Decision + AI
  recommendation (exercising the new parsing path from the existing
  test), the other sets both to `null` (PKG-28's own tests remain
  about Session/Burst, not Decision).

FILES_DELETED: none.

FILES_TOUCHED_BY_TOOLING, NOT PART OF THIS PACKAGE'S OWN DIFF: same
disclosed Next.js scaffold files as PKG-28 (`apps/web/AGENTS.md`,
`apps/web/CLAUDE.md`, regenerated by `next dev` on every run;
`apps/web/next-env.d.ts` reverted to HEAD before this report was
finalized) -- see PKG-28.md's own DIFF_AUDIT for the full disclosure,
unchanged here.

MIGRATIONS_CREATED: none. 14's own DATABASE_CHANGES mapping: "none."

SCHEMA_CHANGES: none.

DB_PRIVILEGE_CHANGES: none. Zero Python files touched.

PUBLIC_INTERFACES_CREATED:
- `recordHumanDecision(decisionId, selectedOption, rationale, confidence, fetchImpl?): Promise<DecisionActionResult>`
  (`decisionClient.ts`) -- 14's own "Decision UI contract".
- `parseDecisionActionResult(body: unknown): DecisionActionResult` --
  fail-closed response-shape narrower, exported for direct testing.
- `DecisionView`, `AiRecommendationView`, `DecisionActionResult`,
  `DecisionState`/`DECISION_STATES`, `BoundaryDenialResult`/
  `BOUNDARY_DENIAL_RESULTS` (`types.ts`).
No generic `Repository<T>`, no generic status setter, no generic
authority boolean, no unversioned dict payload.

COMMANDS_CREATED: `CMD_RECORD_HUMAN_DECISION` materialized as this
package's own ONE interactive UI action (`recordHumanDecision`),
mirroring `application.human_decision_handler.record_human_decision`'s
own already-governed backend command via 12 §23's `POST
/decisions/{d}/decide` row (disclosed prototype interface choice, no
real backend route exists yet -- see KNOWN_LIMITATIONS).
`CMD_OPEN_DECISION_CONSIDERATION` is NOT exposed as an interactive UI
action by this package -- see KNOWN_LIMITATIONS for the full,
disclosed scope reasoning.

QUERIES_CREATED: none new. `decision`/`aiRecommendation` extend the
SAME `GET /workspaces/{w}/sessions/{s}` query PKG-28 already
established (12 §23 assigns no separate Decision-read route).

EVENTS_CREATED: NOT_APPLICABLE. No Event contract assigned.

BOUNDARIES_CREATED_OR_CHANGED: none. This package's own BOUNDARIES
line is a constraint on ITSELF ("Server BND chain authoritative") --
`DecisionSection`/`RecordDecisionForm` never evaluate BND-001..007 or
BND-014 themselves; `DecisionActionResult`'s `denied`/`rejected` cases
are passive echoes of a boundary/application-level decision made
entirely server-side.

AUTHORITY_PATH: This package's own AUTHORITY line -- "UI never
calculates DECISION_RIGHT" -- is honored by construction, not merely
by convention:
- `RecordDecisionForm` contains no conditional of any shape based on
  role, capability, or any cached/mitted authority fact. Its only
  logic is: is a non-empty option selected, and is a submission
  already in flight (the double-click guard, itself not an authority
  check -- see below).
- `recordHumanDecision`'s only output is whichever `DecisionActionResult`
  case the server's own response actually parses to. There is no
  branch anywhere in `decisionClient.ts` that could turn a `denied`/
  `rejected`/`indeterminate` server response into anything resembling
  success, and no branch that could invent a `committed` result the
  server did not itself send.
- `DecisionSection`'s own `override` -- the ONLY thing that ever
  changes the visibly-rendered Decision state after the initial page
  load -- is set in exactly one place: `.then((result) => { if
  (result.kind === "committed") setOverride(result.decision); ...
  })`. A `denied`/`indeterminate`/`rejected` result reaches this same
  `.then()` branch but never calls `setOverride` at all -- structurally,
  not by an `if` a future edit could accidentally invert, since the
  ONLY code path that calls `setOverride` is nested inside the
  `result.kind === "committed"` check itself.
- The double-click guard (`submittedRef` in `RecordDecisionForm`,
  `inFlightRef` in `DecisionSection`) is explicitly disclosed as UX-only,
  never a security boundary -- the true safety net against a genuine
  duplicate command remains PKG-11's own server-side idempotency,
  unmodified and unconsulted by this package at all.

EVIDENCE_PATH: This package's own EVIDENCE line -- "Consumed refs sent
as context only" -- `AiRecommendationView.summary`/`generationId` are
displayed verbatim, never interpreted, scored, or used to pre-fill
`RecordDecisionForm`'s own initial `selectedOption` (proven by the
mandatory "Label/action implying Approve AI Decision" adversarial
test: the `<select>`'s own initial value is asserted empty, never
equal to any AI-recommended text).

AI_PATH: This package's own AI line -- "Recommendation displayed
separately" -- `AiRecommendationPanel` and `DecisionSection`'s own
Decision-state panel are two separate DOM subtrees with distinct
`data-testid`s and an explicit "AI RECOMMENDATION -- NOT A DECISION"
label; there is no code path connecting the two beyond both being
rendered as siblings inside the same `<section>` -- proven by the
mandatory "view-only action causing Decision" adversarial test
(clicking anywhere inside `AiRecommendationPanel` cannot change
`decision-state` at all, since the panel contains zero interactive
elements and zero references to `DecisionSection`'s own state).

RECOVERY_PATH: This package's own FAILURE_RECOVERY line -- "Denied/
stale server response leaves Decision unchanged" -- is exactly
DESIGN_REVIEW_APPLIED_UPFRONT #1's own structural guarantee: `override`
is never set except from a `committed` result, so a `denied`/
`indeterminate`/`rejected`/network-error response leaves
`effectiveDecision` byte-identical to what it was before the click,
proven by the "novel attack: server responds DENY after the click"
E2E test (asserts `decision-state` still reads `UNDER_CONSIDERATION`
immediately after the click AND after the delayed DENY arrives).

TESTS_CREATED:
- `apps/web/tests/lib/decisionClient.test.ts` -- 12 tests (request
  construction, identifier URL-encoding, fail-closed parsing for all
  four `DecisionActionResult` cases and every malformed/unrecognized
  shape, including a malformed NESTED `DecisionView` inside a
  `committed` body).
- `apps/web/tests/components/decision-display.test.tsx` -- 5 tests
  (rendering output + "no interactive element" proofs for
  `AiRecommendationPanel`/`DecisionProvenanceView` ONLY).
- `apps/web/tests/e2e/decision.spec.ts` -- 13 real Playwright tests:
  2 positive flow proofs, 6 mandatory package-specific attacks, 5
  novel/adapted attacks (double-click-adjacent decisionId-tamper
  proof, DENY-after-click, network failure during submission,
  forged/rejected option, null-Decision placeholder).

WHY `RecordDecisionForm`/`DecisionSection` HAVE NO VITEST-LEVEL TEST
(DISCLOSED, NOT AN OMISSION): `react-dom/server`'s `renderToStaticMarkup`
(PKG-28's own zero-new-dependency mechanism, reused here for the two
PASSIVE new components) cannot dispatch DOM events (`onChange`,
`onSubmit`, `click`) at all -- there is no DOM, no event loop, and no
React reconciliation happening after the initial render. Genuinely
testing `RecordDecisionForm`'s own double-submit guard or
`DecisionSection`'s own async state machine at the Vitest level would
require adding `jsdom` + `@testing-library/react` as new dependencies,
which PKG-28 explicitly avoided and disclosed as unnecessary for its
OWN non-interactive components -- that reasoning does not extend to
this package's own genuinely interactive ones. Rather than add new
dependencies for a redundant proof, this package's own 14 manifest
entry ALREADY names "TESTS REQUIRED: E2E" specifically (distinct from
PKG-28's own "UI tests" wording) -- read as the architecture's own
signal that E2E is this package's own primary, sufficient test family.
All interactive/adversarial behavior is instead proven by real
Playwright E2E specs against a real browser, which is also more
realistic for timing-sensitive proofs (double-click races) than a
simulated jsdom event.

TESTS_MODIFIED:
- `apps/web/tests/lib/client.test.ts`: `OK_BODY` fixture extended with
  a real `decision`/`aiRecommendation` (exercises the new parsing path
  from an existing PKG-28 test, not merely kept passing).
- `apps/web/tests/e2e/session-view.spec.ts`: `OK_BODY` fixture extended
  with `decision: null, aiRecommendation: null` (PKG-28's own tests
  remain about Session/Burst; confirmed this renders the
  `decision-none` placeholder harmlessly, no regression).

TARGETED_TEST_RESULTS (fresh run):
- `npm run test` (Vitest): 5 test files, 53 passed, 0 failed (was 36
  before this package; +17 new).
- `npm run e2e` (Playwright, real Chromium, real `next dev` server):
  22 passed, 0 failed (was 9 before this package; +13 new). Re-ran the
  double-click test 5 additional consecutive times: 5/5 passed, exactly
  1 `/decide` request captured every time.
- `npm run typecheck` (`tsc --noEmit`): clean, zero errors.
- `npm run lint`: clean, zero warnings/errors.

NEGATIVE_TEST_RESULTS: every `parseDecisionActionResult` fail-closed
path is asserted to THROW (`TypeError`), never to silently default to
`committed`: missing `kind`, unrecognized `kind`, unrecognized
`denied.result`, missing `rejected.reasonCode`, a malformed/invalid
nested `DecisionView` inside a `committed` body (both missing-fields
and an unrecognized nested `state` value). All covered in
`decisionClient.test.ts`; all pass with the expected `TypeError`.

ADVERSARIAL_TEST_RESULTS:

MANDATORY (6 of 6, per this package's own PRE_IMPLEMENTATION_ATTACK_MODEL):

1. ATTACK: Label/action implying Approve AI Decision.
   EXPECTED DEFENSE: no label/button anywhere reads "approve"/"accept
   AI"; the record-decision control's own initial value is never
   pre-filled from AI content.
   EXPECTED BOUNDARY: AI line -- "Recommendation displayed separately."
   EXPECTED CANONICAL RESULT: `<select>` initial value is empty string.
   EXPECTED PROOF ARTIFACT: real DOM text-content scan + form-value
   assertion on a real rendered page.
   ACTUAL RESULT: PASS.

2. ATTACK: view-only action causing Decision.
   EXPECTED DEFENSE: clicking anywhere inside `AiRecommendationPanel`
   cannot change `decision-state`.
   EXPECTED BOUNDARY: same AI line.
   EXPECTED CANONICAL RESULT: `decision-state` unchanged
   (`UNDER_CONSIDERATION`) after the click.
   EXPECTED PROOF ARTIFACT: real click + real DOM assertion.
   ACTUAL RESULT: PASS.

3. ATTACK: disabled button bypass (rapid double-click).
   EXPECTED DEFENSE: the client-side JS guard
   (`submittedRef`/`inFlightRef`) prevents a second real `fetch` from
   firing for the same user gesture, independent of the `disabled`
   DOM attribute's own React-render timing.
   EXPECTED BOUNDARY: N/A (client-side request-construction
   discipline; the real safety net is PKG-11's own server-side
   idempotency, explicitly disclosed as not consulted here).
   EXPECTED CANONICAL RESULT: exactly 1 `/decide` request captured by
   `page.route()`, even with two dispatched clicks.
   EXPECTED PROOF ARTIFACT: real network-request count from a real
   browser, 5x re-run for reliability.
   ACTUAL RESULT: PASS (5/5 re-runs).

4. ATTACK: role-only actor (holds SOME workspace role, not
   DECISION_RIGHT).
   EXPECTED DEFENSE: a server DENY is rendered as denied, never
   collapsed into a false DECIDED state.
   EXPECTED BOUNDARY: BND-005 (human authority)/BND-006 (human-origin
   content), echoed here as the `denied`/`DENY` case.
   EXPECTED CANONICAL RESULT: `decision-state` remains
   `UNDER_CONSIDERATION`, `DeniedBanner` visible, no
   `DecisionProvenanceView`.
   EXPECTED PROOF ARTIFACT: real rendered page after a real (mocked)
   DENY response.
   ACTUAL RESULT: PASS.

5. ATTACK: admin path.
   EXPECTED DEFENSE: no admin-labeled bypass exists anywhere in the
   Decision section's own DOM.
   EXPECTED BOUNDARY: N/A (structural absence, not a runtime check).
   EXPECTED CANONICAL RESULT: zero matches for `/admin/i` text anywhere
   in `decision-section`.
   EXPECTED PROOF ARTIFACT: real DOM text scan.
   ACTUAL RESULT: PASS.

6. ATTACK: auto-action after DECIDED.
   EXPECTED DEFENSE: once `state === "DECIDED"`, `RecordDecisionForm`
   does not render at all -- no further action control of any kind.
   EXPECTED BOUNDARY: `domain.decision._TERMINAL_DECISION_STATES`'s own
   real backend closure echoed at the UI layer (DECIDED has no further
   legal transition per 03 §38/GAP-03-005).
   EXPECTED CANONICAL RESULT: zero `<button>`/`<input>`/`<form>`/
   `<select>` anywhere in `decision-section` once DECIDED.
   EXPECTED PROOF ARTIFACT: real DOM query on a real DECIDED render.
   ACTUAL RESULT: PASS.

NOVEL/ADAPTED (6, exceeding the "at least 5 total" requirement):

7. ATTACK (novel, no-optimistic-rendering under delay): server
   responds DENY only AFTER a deliberate 200ms delay past the click.
   EXPECTED DEFENSE: `decision-state` reads `UNDER_CONSIDERATION`
   BOTH immediately after the click and after the delayed DENY
   arrives -- never transiently "looks DECIDED" in between.
   EXPECTED CANONICAL RESULT: no intermediate DOM state exists showing
   a DECIDED-looking Decision before the real response.
   EXPECTED PROOF ARTIFACT: two sequential real-DOM assertions
   straddling the delayed response.
   ACTUAL RESULT: PASS.

8. ATTACK (novel, silent-failure): the `/decide` request itself is
   aborted (`route.abort()`), simulating a genuine network failure
   during submission (not the initial page load, which PKG-28 already
   covers).
   EXPECTED DEFENSE: a visible, Decision-submission-specific error
   banner renders; `decision-state` remains unchanged; nothing hangs
   silently.
   EXPECTED CANONICAL RESULT: `network-error-banner` visible with
   decision-specific text, `decision-state` still `UNDER_CONSIDERATION`.
   EXPECTED PROOF ARTIFACT: real aborted network request + real DOM
   assertion.
   ACTUAL RESULT: PASS.

9. ATTACK (novel, forged/rejected content): server returns `rejected`
   with `SELECTED_OPTION_NOT_CANDIDATE` (mirrors the real backend's own
   `SelectedOptionNotCandidate` exception).
   EXPECTED DEFENSE: shown as a DISTINCT rejection, never collapsed
   into "denied" or, worse, treated as success.
   EXPECTED CANONICAL RESULT: `decision-rejected-banner` visible with
   the exact reason code; `decision-state` still `UNDER_CONSIDERATION`.
   EXPECTED PROOF ARTIFACT: real DOM assertion after a real (mocked)
   rejection response.
   ACTUAL RESULT: PASS.

10. ATTACK (novel, identifier-tamper): verify the ACTUAL captured
    request URL, not an assumption -- proves `recordHumanDecision`
    always sends the real `decisionId` it was constructed with, with
    no DOM-controllable override.
    EXPECTED CANONICAL RESULT: captured request URL contains
    `/decisions/d-1/decide` exactly.
    EXPECTED PROOF ARTIFACT: `route.request().url()` from the real
    intercepted request.
    ACTUAL RESULT: PASS.

11. ATTACK (novel, fail-closed/collapse, Vitest-level): a `committed`
    body whose nested `Decision.state` is an unrecognized value
    (`"FOOBAR"`) -- proves the fail-closed discipline extends through
    a NESTED parse call (`parseDecisionView`, reused from `client.ts`),
    not only the top-level `DecisionActionResult.kind` discriminator.
    EXPECTED CANONICAL RESULT: `TypeError` thrown, no partially-valid
    `DecisionView` ever returned.
    ACTUAL RESULT: PASS.

12. ATTACK (novel, absent-precondition): `decision === null` (no
    Decision currently under consideration) renders a passive
    placeholder with zero interactive elements -- proves this package
    never fabricates a phantom Decision or a phantom "start a Decision"
    control outside its own disclosed scope (see KNOWN_LIMITATIONS on
    `CMD_OPEN_DECISION_CONSIDERATION`).
    ACTUAL RESULT: PASS.

CROSS_LAYER_TEST_RESULTS: identical disclosed situation to PKG-28: no
real `apps/api` route exists for either
`GET /workspaces/{w}/sessions/{s}` (extended) or
`POST /decisions/{d}/decide`. `tests/e2e/decision.spec.ts` runs a real
Chromium browser against a real running Next.js server, with both
routes intercepted only at the network layer via `page.route()` -- the
same "prove the mechanism for real, disclose the missing concrete
route" pattern PKG-28 already established, extended to a Command
rather than only a Query.

RECURSIVE_REGRESSION_RESULTS:
- Python side (zero `.py` files touched): `check_architecture_dependencies.py`
  -> PASS; `check_provider_sdk_imports.py` -> PASS;
  `check_test_only_imports.py` -> PASS. Live PostgreSQL 17 (full suite
  `tests/ apps/api/tests apps/worker`): 1078 passed, 1 skipped --
  byte-identical to PKG-28's own reported baseline. Zero regressions.
- Frontend side: `npm run lint`/`npm run typecheck` clean; `npm run
  test` 53/53 (36 PKG-28 + 17 new, all passing unmodified in behavior);
  `npm run e2e` 22/22 (9 PKG-28 + 13 new, all passing).
- Every already-existing P claim this package could invalidate:
  P-07/P-08/P-09's own real backend proof tests
  (`tests/authority/test_decision_authority.py`,
  `tests/authority/test_question_selection_authority.py`,
  `tests/e2e/test_human_decision.py`, `tests/boundaries/test_bnd_006_human_decision.py`)
  are all included unmodified in the 1078-passed live-DB count.

P_CLAIMS_TESTED:
- P-07 (AI sets DECIDED -> BND-006 DENY): POTENTIALLY AFFECTED,
  re-exercised at the UI layer via mandatory adversarial attacks #1/#2
  (no AI-authored content can reach `RecordDecisionForm`'s own initial
  value, and no view-only AI-panel interaction can create a Decision).
  Backend enforcement (`Bnd006HumanDecisionEvaluator`) is untouched and
  unmodified.
- P-08 (AI/no-right selection -> exact QUESTION_SELECTION_RIGHT proof):
  NOT_APPLICABLE to this package's own UI surface -- Question
  Selection (12 §24 item 10) is explicitly out of this package's own
  scope (see KNOWN_LIMITATIONS); this proof claim's own real backend
  test (`tests/authority/test_question_selection_authority.py`) is
  unaffected and still passing, unmodified, in the regression count.
- P-09 (recommendation persistence -> Decision remains
  UNDER_CONSIDERATION): POTENTIALLY AFFECTED, re-exercised at the UI
  layer via mandatory adversarial attack #6 (auto-action after DECIDED)
  and novel attack #7 (no-optimistic-rendering under delay) --
  together proving the UI never advances a Decision's own visible
  state past what the server has actually committed. Backend
  enforcement (`resolve_decision_transition_to_state`,
  `_TERMINAL_DECISION_STATES`) is untouched and unmodified.
No proof claim was newly introduced or subjected to regression risk by
this package.

PROOF_ARTIFACTS: This package is a pure display + single-Command-
trigger layer -- it produces no canonical state, no `BoundaryProof`,
`CommitUnit`, `AuditEvent`, Outbox/Event, Evidence/version reference,
AI lineage record, `RecoveryRecord`, or `SecurityEvent` of its own. Its
own proof artifacts: (1) the real Vitest run (53/53), (2) the real
Playwright run against a real browser + real server (22/22, including
5 additional stress-reruns of the double-click test), (3) the
unmodified, still-passing backend proof artifacts for P-07/P-08/P-09
this package's own UI merely re-displays or, for P-08, does not touch
at all.

FORBIDDEN_DEPENDENCY_CHECK: PASS. Python-side unaffected and
re-verified. Manually verified `decisionClient.ts` imports nothing
beyond `./client`/`./types`; no component imports anything outside
`../lib/api/*`/sibling components/React.

PROVIDER_SDK_CHECK: PASS (Python-side, unaffected, re-verified). Not
applicable to `apps/web`.

TEST_ONLY_IMPORT_CHECK: PASS (Python-side, unaffected, re-verified).
The one test-only construct (`fetchImpl` injection parameter on
`recordHumanDecision`, mirroring `fetchSessionView`'s own PKG-28
precedent) is not a forbidden "test-only path reachable from
production" -- production always uses the real default.

DIFF_AUDIT: `git status --short` cross-checked against
FILES_CREATED/FILES_MODIFIED above, entry by entry:
```
 M apps/web/components/NetworkErrorBanner.tsx      <- FILES_MODIFIED, matches
 M apps/web/components/SessionViewContainer.tsx    <- FILES_MODIFIED, matches
 M apps/web/lib/api/client.ts                      <- FILES_MODIFIED, matches
 M apps/web/lib/api/types.ts                       <- FILES_MODIFIED, matches
 M apps/web/tests/e2e/session-view.spec.ts         <- FILES_MODIFIED (fixture), matches
 M apps/web/tests/lib/client.test.ts               <- FILES_MODIFIED (fixture), matches
?? apps/web/components/AiRecommendationPanel.tsx   <- FILES_CREATED, matches
?? apps/web/components/DecisionProvenanceView.tsx  <- FILES_CREATED, matches
?? apps/web/components/DecisionSection.tsx         <- FILES_CREATED, matches
?? apps/web/components/RecordDecisionForm.tsx      <- FILES_CREATED, matches
?? apps/web/lib/api/decisionClient.ts              <- FILES_CREATED, matches
?? apps/web/tests/components/decision-display.test.tsx <- FILES_CREATED, matches
?? apps/web/tests/e2e/decision.spec.ts             <- FILES_CREATED, matches
?? apps/web/tests/lib/decisionClient.test.ts       <- FILES_CREATED, matches
```
`apps/web/AGENTS.md`/`apps/web/CLAUDE.md` (Next.js scaffold,
regenerated by `next dev`) again appear untracked and are again
DELIBERATELY EXCLUDED from any `git add` -- identical disclosure as
PKG-28. No architecture file, no unrelated package, no unrelated
migration, and no unrelated test was touched.

ARCHITECTURE_RECONSTRUCTION_RESULT:
REQUEST (a human clicks "Record Decision" with a selected option)
-> ACTOR (the real, requesting human -- this package invents nothing
   about who they are; the server resolves `ActorIdentity` from the
   real request)
-> WORKSPACE (untouched by this package; carried implicitly by
   whatever real session/auth mechanism a real backend would attach --
   `SUCCESSOR_NOT_BUILT`, no real backend route exists)
-> CURRENT STATE (`Decision.state`, read verbatim from the prior `GET`
   query -- never recomputed here)
-> CURRENT GOVERNANCE / CURRENT AUTHORITY (NOT_APPLICABLE at this
   layer -- 06's own BND-001..007 chain and BND-005's own
   `AuthorityResolver` lookup happen entirely server-side;
   `RecordDecisionForm` supplies no authority-shaped input at all)
-> HUMAN DECISION (`selectedOption`/`rationale`/`confidence`, exactly
   the human-authored content `RecordHumanDecisionPayload` already
   carries server-side, PKG-15)
-> EVIDENCE (NOT_APPLICABLE -- no Evidence set is attached by this
   package's own UI; `evidence_set_ref` remains `None` on this path)
-> BOUNDARIES (BND-001..007, entirely server-side, echoed here only as
   the RESULT this package renders)
-> BND-014 (server-side, echoed only as the `committed` case)
-> COMMAND (`CMD_RECORD_HUMAN_DECISION`, real, already governed,
   PKG-15)
-> COMMIT UNIT / CANONICAL MUTATION (server-side, real, PKG-15 --
   `_RecordDecisionMutation`)
-> AUDIT / OUTBOX / EVENT (server-side, real, unmodified by this
   package)
-> RESULTING STATE (`Decision.state == DECIDED`, echoed back to this
   UI as the `committed.decision` this package then renders)
Every node past BOUNDARIES is `SUCCESSOR_NOT_BUILT` only in the sense
that no real HTTP route yet carries this exact request from a real
browser to the real, already-fully-built backend chain -- the backend
chain itself is 100% real and unmodified (PKG-15). This package's own
contribution is everything up to and including constructing the real
`POST` request and faithfully rendering whatever real result comes
back.

KNOWN_LIMITATIONS:
- **`CMD_OPEN_DECISION_CONSIDERATION` (TRN-DEC-001) is NOT exposed as
  an interactive UI action.** 12 §24 item 12 names, literally, "human
  Decision action for authorized holder" (singular) -- read as
  TRN-DEC-002/RecordHumanDecision specifically (the human's own act of
  DECIDING), the same way PKG-28 treated Session/Challenge/Burst
  creation as an already-satisfied precondition of its own page, never
  a UI action it had to build. A Decision already `UNDER_CONSIDERATION`
  is likewise treated as an existing precondition here. Building an
  "author a Decision's own question/options/criteria" form for OPEN
  would have required inventing UI surface 12 §24's own item list does
  not literally name, and risked exactly the "future-generic
  abstraction"/"successor behavior" this package's own PACKAGE_BOUNDARY
  forbids. `SUCCESSOR_NOT_BUILT`, disclosed, not fabricated.
- **12 §24 item 10 ("Question selection control") is out of this
  package's own scope entirely**, not merely deferred. Evidence: (a)
  PKG-14 (QuestionSelection) is NOT named in this package's own
  REQUIRED PREDECESSORS (`PKG-15,PKG-19,PKG-28`); (b)
  FILES_ALLOWED_TO_CREATE names only "Decision components/routes",
  never Question-selection components. This is a real, pre-existing
  gap in the 32-package DAG's own minimum prototype -- no package in
  this DAG is ever assigned a Question-selection UI -- not something
  this package could close without exceeding its own
  HUMAN_AUTHORIZED_SCOPE. The reviewer's own adversarial-attack
  suggestion for "forged/manipulated Question-ID in the selection" is
  honored in its GENUINE analogous form instead: novel attack #9
  (forged/rejected `selectedOption` not among the real Decision's own
  `options`, mirroring `SelectedOptionNotCandidate`'s own real backend
  guard) -- the concrete mechanism this package's own real interactive
  control actually has, rather than a mechanism (Question selection)
  it was never authorized to build.
- **The deeper Command/CommitUnit/AuditEvent/Outbox reconstruction
  chain (`GET /commands/{c}/reconstruction`) is not built.** 12 §24
  item 15's own "minimal provenance/audit reconstruction view" is
  materialized here using 07 §54.8's own PER-ARTIFACT minimal field
  list for Decision specifically (human authoritative origin,
  DecisionAuthority holder, AI recommendations consumed, Evidence set
  consumed, selected option, rationale, decision time) -- 14 assigns no
  specific Query to this package beyond "Decision UI contract"
  generically, and the deeper reconstruction chain is a separate,
  unassigned QUERY row 12 §23 itself lists independently.
- **No real backend HTTP route exists for either the extended
  `GET /workspaces/{w}/sessions/{s}` or the new
  `POST /decisions/{d}/decide`.** Identical disclosed situation to
  PKG-28 -- `apps/api` still exposes only `/healthz`. Proven via real
  Playwright E2E with `page.route()` interception, not a mocked module.
- **`AiRecommendationView.aiRecommendationConsumedRef`-equivalent field
  on `DecisionView` (`aiRecommendationConsumedRef`, mirroring
  `Decision.provenance_ref`) will always render `null` in practice
  today** -- no code path in this codebase (including PKG-15's own
  `open_decision_consideration`) ever populates
  `Decision.provenance_ref`. Disclosed, not hidden:
  `DecisionProvenanceView` renders "none consumed" honestly rather than
  fabricating a plausible-looking reference.

BLOCKED_DEPENDENCIES: HARD-DEP-001/HARD-DEP-002 unchanged, still
BLOCKED.

NEW_GAPS_DISCOVERED: none beyond the already-disclosed,
already-tracked "no real backend route yet" (unchanged since PKG-00)
and the pre-existing DAG gap around Question-selection UI (item 10,
disclosed above, not newly created by this package).

NO_SEMANTIC_INVENTION_CONFIRMATION: Confirmed. `DecisionState` is
transcribed verbatim from `packages/domain/decision.py`'s own 2-value
closed vocabulary; `DecisionActionResult`'s `denied` case reuses the
identical `BoundaryDenialResult` vocabulary `SessionReadResult` already
established (PKG-28); its `rejected` case mirrors
`SelectedOptionNotCandidate`/`StaleVersionConflict`, two real,
already-existing backend exception types, not invented ones; its
`indeterminate` case mirrors PKG-28's own already-established
BND-017 concept. `DecisionProvenanceView`'s own field set is 07 §54.8's
own literal minimal list, not an invented richer view. No new
authority concept, no new capability concept, no new boundary, no new
Command beyond the one 14 already assigns (`CMD_RECORD_HUMAN_DECISION`)
was invented anywhere in this package.

NEXT_PACKAGE_ALLOWED_BY_DAG: PKG-30 ("TestProofBundle and E2E proof
paths") becomes DAG-eligible once this package's own commit is
accepted (`PKG-24,PKG-26,PKG-29` -- PKG-24/26 already long-completed;
PKG-29 is the last gating dependency).

HUMAN_GATE_REQUIRED: YES -- per this package's own coding prompt's
STOP discipline and this session's own standing rule: no commit or
push occurs without the user's literal "PASS, committe das" or the
exact git command given verbatim. This report is presented for that
Human Gate now.

================================================================
RAW_EVIDENCE_APPENDIX (embedded per explicit reviewer request --
raw file contents / raw test output, not prose about them)
================================================================

--- apps/web/lib/api/types.ts (full file) ---

/**
 * Typed domain shapes for the "typed API client" (14 §46 PKG-28
 * PUBLIC_INTERFACES: "typed API client").
 *
 * Source: 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §23 ("MINIMUM API
 * SURFACE" -- "The exact HTTP paths are prototype interface choices.
 * The semantic Commands are authoritative"; `GET /sessions/{s}` is a
 * QUERY, "read scope only"), §24 ("MINIMUM UI" -- items 1-8, 13-14 are
 * this package's own scope: authenticated Workspace context, Challenge
 * frame, current Session state, Burst state, HUMAN_ONLY mode
 * indicator, verbatim human Question list, frozen raw-set indicator,
 * origin marker HUMAN or AI, AI analysis shown explicitly as DERIVED /
 * PROPOSAL, blocked/denied result surface, INDETERMINATE surface that
 * disables blind retry -- items 10-12/15 (Question selection control,
 * Decision boundary, human Decision action, provenance/audit view) are
 * PKG-29's own scope, "Human Decision UI").
 *
 * [... unchanged PKG-28 header docstring, omitted here for length --
 * see the file itself for the full text ...]
 */

export type WorkspaceId = string & { readonly __brand: "WorkspaceId" };
export type ChallengeId = string & { readonly __brand: "ChallengeId" };
export type SessionId = string & { readonly __brand: "SessionId" };
export type BurstId = string & { readonly __brand: "BurstId" };
export type QuestionId = string & { readonly __brand: "QuestionId" };
export type DecisionId = string & { readonly __brand: "DecisionId" };

export const SESSION_STATES = [
  "DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION",
  "QUESTION_CAPTURE", "ANALYSIS", "REFLECTION", "QUESTION_SELECTION",
  "INVESTIGATION", "EXPERIMENT", "ACTION", "REVIEW", "CLOSED",
] as const;
export type SessionState = (typeof SESSION_STATES)[number];

export const BURST_STATES = ["PREPARED", "ACTIVE", "PAUSED", "COMPLETED"] as const;
export type BurstState = (typeof BURST_STATES)[number];

export const BURST_MODES = ["HUMAN_ONLY", "HUMAN_PLUS_AI", "AI_CHALLENGE_AFTER_HUMANS"] as const;
export type BurstMode = (typeof BURST_MODES)[number];

export const QUESTION_ORIGINS = ["HUMAN", "AI", "IMPORTED", "INFERRED"] as const;
export type QuestionOrigin = (typeof QUESTION_ORIGINS)[number];

/**
 * `packages/domain/decision.py`'s own `DecisionState` -- 03 §35.2's
 * exact 2-value closed vocabulary, `[ARCHITECTURAL CLOSURE]`. Built as
 * a `const` array with the type derived from it from day one (per the
 * PKG-28 external-review retrofit lesson), never as a bare union a
 * caller could bypass with a compile-time-only cast.
 */
export const DECISION_STATES = ["UNDER_CONSIDERATION", "DECIDED"] as const;
export type DecisionState = (typeof DECISION_STATES)[number];

/**
 * `boundaries.types.BoundaryResult`'s own DENY/REQUIRE/ESCALATE
 * outcomes (06 §2), reused verbatim for `DecisionActionResult` below --
 * the identical vocabulary `SessionReadResult`'s own `denied` case
 * already uses (PKG-28). Kept as its own named array (not re-exported
 * from `SessionReadResult`) because it is the second, independent site
 * this package needs runtime membership-checked, not because the
 * vocabulary itself differs.
 */
export const BOUNDARY_DENIAL_RESULTS = ["DENY", "REQUIRE", "ESCALATE"] as const;
export type BoundaryDenialResult = (typeof BOUNDARY_DENIAL_RESULTS)[number];

export interface ChallengeView {
  readonly challengeId: ChallengeId;
  readonly workspaceId: WorkspaceId;
  readonly title: string;
  readonly description: string | null;
}

export interface SessionSummary {
  readonly sessionId: SessionId;
  readonly challengeId: ChallengeId;
  readonly workspaceId: WorkspaceId;
  readonly state: SessionState;
}

export interface QuestionView {
  readonly questionId: QuestionId;
  readonly originalText: string;
  readonly origin: QuestionOrigin;
}

export interface BurstView {
  readonly burstId: BurstId;
  readonly sessionId: SessionId;
  readonly state: BurstState;
  readonly mode: BurstMode;
  readonly questions: readonly QuestionView[];
}

export function isBurstFrozen(burst: BurstView): boolean {
  return burst.state === "COMPLETED";
}

export interface AiRecommendationView {
  readonly generationId: string;
  readonly summary: string;
}

export interface DecisionView {
  readonly decisionId: DecisionId;
  readonly challengeId: ChallengeId;
  readonly decisionQuestionRef: QuestionId | null;
  readonly decisionQuestionText: string | null;
  readonly options: readonly string[];
  readonly criteria: readonly string[];
  readonly selectedOption: string | null;
  readonly rationale: string | null;
  readonly confidence: string | null;
  readonly state: DecisionState;
  readonly decidedByUserId: string | null;
  readonly decisionAuthorityBindingId: string | null;
  readonly aiRecommendationConsumedRef: string | null;
  readonly decidedAt: string | null;
}

export interface SessionView {
  readonly workspaceId: WorkspaceId;
  readonly challenge: ChallengeView;
  readonly session: SessionSummary;
  readonly burst: BurstView | null;
  readonly decision: DecisionView | null;
  readonly aiRecommendation: AiRecommendationView | null;
}

export type SessionReadResult =
  | { readonly kind: "ok"; readonly data: SessionView }
  | { readonly kind: "denied"; readonly result: BoundaryDenialResult; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string };

export type DecisionActionResult =
  | { readonly kind: "committed"; readonly decision: DecisionView }
  | { readonly kind: "denied"; readonly result: BoundaryDenialResult; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string }
  | { readonly kind: "rejected"; readonly reasonCode: string };

--- apps/web/lib/api/client.ts (full file) ---

import {
  BOUNDARY_DENIAL_RESULTS,
  BURST_MODES,
  BURST_STATES,
  DECISION_STATES,
  QUESTION_ORIGINS,
  SESSION_STATES,
  type AiRecommendationView,
  type BurstView,
  type ChallengeView,
  type DecisionView,
  type SessionId,
  type SessionReadResult,
  type SessionSummary,
  type WorkspaceId,
} from "./types";

export const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

export async function fetchSessionView(
  workspaceId: WorkspaceId,
  sessionId: SessionId,
  fetchImpl: typeof fetch = fetch,
): Promise<SessionReadResult> {
  const response = await fetchImpl(
    `${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}`,
    { headers: { Accept: "application/json" } },
  );
  const body: unknown = await response.json();
  return parseSessionReadResult(body);
}

export function parseSessionReadResult(body: unknown): SessionReadResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("SessionReadResult response body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok":
      return { kind: "ok", data: parseSessionView(body.data) };
    case "denied":
      return {
        kind: "denied",
        result: requireEnum(body, "result", BOUNDARY_DENIAL_RESULTS),
        reasonCode: requireNonEmptyString(body, "reasonCode"),
      };
    case "indeterminate":
      return { kind: "indeterminate", blockedTargetRef: requireNonEmptyString(body, "blockedTargetRef") };
    default:
      throw new TypeError(`unrecognized SessionReadResult kind ${JSON.stringify(body.kind)}`);
  }
}

function parseSessionView(value: unknown): SessionView {
  if (!isRecord(value)) {
    throw new TypeError("SessionView body must be an object");
  }
  return {
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    challenge: parseChallengeView(value.challenge),
    session: parseSessionSummary(value.session),
    burst: value.burst === null ? null : parseBurstView(value.burst),
    decision: value.decision === null ? null : parseDecisionView(value.decision),
    aiRecommendation: value.aiRecommendation === null ? null : parseAiRecommendationView(value.aiRecommendation),
  };
}

export function parseDecisionView(value: unknown): DecisionView {
  if (!isRecord(value)) {
    throw new TypeError("DecisionView body must be an object");
  }
  if (!Array.isArray(value.options) || !value.options.every((o) => typeof o === "string")) {
    throw new TypeError("DecisionView.options must be an array of strings");
  }
  if (!Array.isArray(value.criteria) || !value.criteria.every((c) => typeof c === "string")) {
    throw new TypeError("DecisionView.criteria must be an array of strings");
  }
  return {
    decisionId: requireString(value, "decisionId") as DecisionView["decisionId"],
    challengeId: requireString(value, "challengeId") as DecisionView["challengeId"],
    decisionQuestionRef:
      value.decisionQuestionRef === null
        ? null
        : (requireString(value, "decisionQuestionRef") as DecisionView["decisionQuestionRef"]),
    decisionQuestionText: value.decisionQuestionText === null ? null : requireString(value, "decisionQuestionText"),
    options: value.options,
    criteria: value.criteria,
    selectedOption: value.selectedOption === null ? null : requireString(value, "selectedOption"),
    rationale: value.rationale === null ? null : requireString(value, "rationale"),
    confidence: value.confidence === null ? null : requireString(value, "confidence"),
    state: requireEnum(value, "state", DECISION_STATES),
    decidedByUserId: value.decidedByUserId === null ? null : requireString(value, "decidedByUserId"),
    decisionAuthorityBindingId:
      value.decisionAuthorityBindingId === null ? null : requireString(value, "decisionAuthorityBindingId"),
    aiRecommendationConsumedRef:
      value.aiRecommendationConsumedRef === null ? null : requireString(value, "aiRecommendationConsumedRef"),
    decidedAt: value.decidedAt === null ? null : requireString(value, "decidedAt"),
  };
}

function parseAiRecommendationView(value: unknown): AiRecommendationView {
  if (!isRecord(value)) {
    throw new TypeError("AiRecommendationView body must be an object");
  }
  return {
    generationId: requireString(value, "generationId"),
    summary: requireString(value, "summary"),
  };
}

function parseChallengeView(value: unknown): ChallengeView {
  if (!isRecord(value)) {
    throw new TypeError("ChallengeView body must be an object");
  }
  return {
    challengeId: requireString(value, "challengeId") as ChallengeView["challengeId"],
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    title: requireString(value, "title"),
    description: value.description === null ? null : requireString(value, "description"),
  };
}

function parseSessionSummary(value: unknown): SessionSummary {
  if (!isRecord(value)) {
    throw new TypeError("SessionSummary body must be an object");
  }
  return {
    sessionId: requireString(value, "sessionId") as SessionId,
    challengeId: requireString(value, "challengeId") as SessionSummary["challengeId"],
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    state: requireEnum(value, "state", SESSION_STATES),
  };
}

function parseBurstView(value: unknown): BurstView {
  if (!isRecord(value)) {
    throw new TypeError("BurstView body must be an object");
  }
  if (!Array.isArray(value.questions)) {
    throw new TypeError("BurstView.questions must be an array");
  }
  return {
    burstId: requireString(value, "burstId") as BurstView["burstId"],
    sessionId: requireString(value, "sessionId") as SessionId,
    state: requireEnum(value, "state", BURST_STATES),
    mode: requireEnum(value, "mode", BURST_MODES),
    questions: value.questions.map((q) => {
      if (!isRecord(q)) {
        throw new TypeError("QuestionView body must be an object");
      }
      return {
        questionId: requireString(q, "questionId") as BurstView["questions"][number]["questionId"],
        originalText: requireString(q, "originalText"),
        origin: requireEnum(q, "origin", QUESTION_ORIGINS),
      };
    }),
  };
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function requireString(record: Record<string, unknown>, key: string): string {
  const value = record[key];
  if (typeof value !== "string") {
    throw new TypeError(`expected string field '${key}', got ${JSON.stringify(value)}`);
  }
  return value;
}

function requireNonEmptyString(record: Record<string, unknown>, key: string): string {
  const value = requireString(record, key);
  if (value.length === 0) {
    throw new TypeError(`expected non-empty string field '${key}'`);
  }
  return value;
}

export function requireEnum<T extends string>(record: Record<string, unknown>, key: string, allowed: readonly T[]): T {
  const value = requireString(record, key);
  if (!(allowed as readonly string[]).includes(value)) {
    throw new TypeError(`expected one of ${JSON.stringify(allowed)} for field '${key}', got ${JSON.stringify(value)}`);
  }
  return value as T;
}

import type { SessionView } from "./types";
export type { SessionView };

--- apps/web/lib/api/decisionClient.ts (full file) ---

import { apiBaseUrl, isRecord, parseDecisionView, requireEnum, requireString } from "./client";
import { BOUNDARY_DENIAL_RESULTS, type DecisionActionResult, type DecisionId } from "./types";

export async function recordHumanDecision(
  decisionId: DecisionId,
  selectedOption: string,
  rationale: string | null,
  confidence: string | null,
  fetchImpl: typeof fetch = fetch,
): Promise<DecisionActionResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/decisions/${encodeURIComponent(decisionId)}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ selectedOption, rationale, confidence }),
  });
  const body: unknown = await response.json();
  return parseDecisionActionResult(body);
}

export function parseDecisionActionResult(body: unknown): DecisionActionResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("DecisionActionResult response body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "committed":
      return { kind: "committed", decision: parseDecisionView(body.decision) };
    case "denied":
      return {
        kind: "denied",
        result: requireEnum(body, "result", BOUNDARY_DENIAL_RESULTS),
        reasonCode: requireNonEmptyString(body, "reasonCode"),
      };
    case "indeterminate":
      return { kind: "indeterminate", blockedTargetRef: requireNonEmptyString(body, "blockedTargetRef") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireNonEmptyString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized DecisionActionResult kind ${JSON.stringify(body.kind)}`);
  }
}

function requireNonEmptyString(record: Record<string, unknown>, key: string): string {
  const value = requireString(record, key);
  if (value.length === 0) {
    throw new TypeError(`expected non-empty string field '${key}'`);
  }
  return value;
}

--- apps/web/components/RecordDecisionForm.tsx (full file) ---

"use client";
import { useEffect, useRef, useState } from "react";
import type { DecisionView } from "../lib/api/types";

export function RecordDecisionForm({
  decision,
  submitting,
  onSubmit,
}: {
  readonly decision: DecisionView;
  readonly submitting: boolean;
  readonly onSubmit: (selectedOption: string, rationale: string | null, confidence: string | null) => void;
}) {
  const [selectedOption, setSelectedOption] = useState("");
  const [rationale, setRationale] = useState("");
  const [confidence, setConfidence] = useState("");
  const submittedRef = useRef(false);

  useEffect(() => {
    if (!submitting) {
      submittedRef.current = false;
    }
  }, [submitting]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || submittedRef.current || selectedOption === "") {
      return;
    }
    submittedRef.current = true;
    onSubmit(selectedOption, rationale.length > 0 ? rationale : null, confidence.length > 0 ? confidence : null);
  }

  return (
    <form data-testid="record-decision-form" onSubmit={handleSubmit}>
      {decision.options.length > 0 ? (
        <select
          data-testid="decision-option-select"
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          disabled={submitting}
          required
        >
          <option value="" disabled>
            Select an option
          </option>
          {decision.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          data-testid="decision-option-input"
          type="text"
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          disabled={submitting}
          required
        />
      )}
      <textarea
        data-testid="decision-rationale-input"
        value={rationale}
        onChange={(e) => setRationale(e.target.value)}
        disabled={submitting}
      />
      <input
        data-testid="decision-confidence-input"
        type="text"
        value={confidence}
        onChange={(e) => setConfidence(e.target.value)}
        disabled={submitting}
      />
      <button data-testid="record-decision-submit" type="submit" disabled={submitting}>
        Record Decision
      </button>
    </form>
  );
}

--- apps/web/components/DecisionSection.tsx (full file -- note setOverride
    appears exactly once, inside the `result.kind === "committed"` branch) ---

"use client";
import { useRef, useState } from "react";
import { recordHumanDecision } from "../lib/api/decisionClient";
import type { AiRecommendationView, DecisionActionResult, DecisionView } from "../lib/api/types";
import { AiRecommendationPanel } from "./AiRecommendationPanel";
import { DecisionProvenanceView } from "./DecisionProvenanceView";
import { DeniedBanner } from "./DeniedBanner";
import { IndeterminateBanner } from "./IndeterminateBanner";
import { NetworkErrorBanner } from "./NetworkErrorBanner";
import { RecordDecisionForm } from "./RecordDecisionForm";

type ActionState =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "result"; readonly result: DecisionActionResult }
  | { readonly kind: "network_error" };

export function DecisionSection({
  decision,
  aiRecommendation,
}: {
  readonly decision: DecisionView | null;
  readonly aiRecommendation: AiRecommendationView | null;
}) {
  const [override, setOverride] = useState<DecisionView | null>(null);
  const [actionState, setActionState] = useState<ActionState>({ kind: "idle" });
  const inFlightRef = useRef(false);

  const effectiveDecision = override ?? decision;
  const submitting = actionState.kind === "submitting";

  function handleSubmit(selectedOption: string, rationale: string | null, confidence: string | null) {
    if (inFlightRef.current || effectiveDecision === null) {
      return;
    }
    inFlightRef.current = true;
    setActionState({ kind: "submitting" });
    recordHumanDecision(effectiveDecision.decisionId, selectedOption, rationale, confidence)
      .then((result) => {
        inFlightRef.current = false;
        if (result.kind === "committed") {
          setOverride(result.decision);
        }
        setActionState({ kind: "result", result });
      })
      .catch(() => {
        inFlightRef.current = false;
        setActionState({ kind: "network_error" });
      });
  }

  return (
    <section data-testid="decision-section" aria-label="Decision">
      {aiRecommendation !== null ? <AiRecommendationPanel recommendation={aiRecommendation} /> : null}

      {effectiveDecision === null ? (
        <p data-testid="decision-none">No Decision is currently under consideration.</p>
      ) : (
        <div data-testid="decision-state-panel">
          <span data-testid="decision-state">{effectiveDecision.state}</span>

          {effectiveDecision.state === "UNDER_CONSIDERATION" ? (
            <>
              <ul data-testid="decision-options-list">
                {effectiveDecision.options.map((option) => (
                  <li key={option} data-testid="decision-option-item">
                    {option}
                  </li>
                ))}
              </ul>
              <RecordDecisionForm decision={effectiveDecision} submitting={submitting} onSubmit={handleSubmit} />
            </>
          ) : (
            <DecisionProvenanceView decision={effectiveDecision} />
          )}
        </div>
      )}

      {actionState.kind === "result" && actionState.result.kind === "denied" ? (
        <DeniedBanner result={actionState.result.result} reasonCode={actionState.result.reasonCode} />
      ) : null}
      {actionState.kind === "result" && actionState.result.kind === "indeterminate" ? (
        <IndeterminateBanner blockedTargetRef={actionState.result.blockedTargetRef} />
      ) : null}
      {actionState.kind === "result" && actionState.result.kind === "rejected" ? (
        <div data-testid="decision-rejected-banner" role="alert">
          {actionState.result.reasonCode}
        </div>
      ) : null}
      {actionState.kind === "network_error" ? (
        <NetworkErrorBanner message="Unable to record this Decision. Nothing was saved." />
      ) : null}
    </section>
  );
}

--- apps/web/components/AiRecommendationPanel.tsx (full file) ---

export function AiRecommendationPanel({ recommendation }: { readonly recommendation: AiRecommendationView }) {
  return (
    <section data-testid="ai-recommendation-panel" aria-label="AI recommendation, not a Decision">
      <span data-testid="ai-recommendation-label">AI RECOMMENDATION -- NOT A DECISION</span>
      <span data-testid="ai-recommendation-derived-label">DERIVED / PROPOSAL</span>
      <p data-testid="ai-recommendation-summary">{recommendation.summary}</p>
    </section>
  );
}

--- apps/web/components/DecisionProvenanceView.tsx (full file) ---

export function DecisionProvenanceView({ decision }: { readonly decision: DecisionView }) {
  return (
    <section data-testid="decision-provenance-view" aria-label="Decision provenance">
      <span data-testid="decision-selected-option">{decision.selectedOption}</span>
      {decision.rationale !== null ? <p data-testid="decision-rationale">{decision.rationale}</p> : null}
      {decision.confidence !== null ? <span data-testid="decision-confidence">{decision.confidence}</span> : null}
      <span data-testid="decision-decided-at">{decision.decidedAt}</span>
      <span data-testid="decision-decided-by">{decision.decidedByUserId}</span>
      <span data-testid="decision-authority-binding">{decision.decisionAuthorityBindingId}</span>
      <span data-testid="decision-ai-recommendation-consumed-ref">
        {decision.aiRecommendationConsumedRef ?? "none consumed"}
      </span>
    </section>
  );
}

--- apps/web/tests/e2e/decision.spec.ts (full file, 13 tests) ---

import { expect, test } from "@playwright/test";

const WORKSPACE_ID = "ws-real";
const SESSION_ID = "sess-real";
const SESSION_ROUTE_PATTERN = "http://localhost:8000/workspaces/**/sessions/**";
const DECIDE_ROUTE_PATTERN = "http://localhost:8000/decisions/**/decide";
const PAGE_PATH = `/workspaces/${WORKSPACE_ID}/sessions/${SESSION_ID}`;

const AI_RECOMMENDATION = {
  generationId: "gen-1",
  summary: "The data suggests Option A minimizes long-term cost.",
};

const DECISION_UNDER_CONSIDERATION = {
  decisionId: "d-1",
  challengeId: "c-1",
  decisionQuestionRef: null,
  decisionQuestionText: "Which approach should we take?",
  options: ["Option A", "Option B"],
  criteria: ["Cost", "Speed"],
  selectedOption: null,
  rationale: null,
  confidence: null,
  state: "UNDER_CONSIDERATION",
  decidedByUserId: null,
  decisionAuthorityBindingId: "binding-1",
  aiRecommendationConsumedRef: null,
  decidedAt: null,
};

function sessionOkBody(decision: unknown, aiRecommendation: unknown = AI_RECOMMENDATION) {
  return {
    kind: "ok",
    data: {
      workspaceId: WORKSPACE_ID,
      challenge: { challengeId: "c-1", workspaceId: WORKSPACE_ID, title: "Reduce cost", description: null },
      session: { sessionId: SESSION_ID, challengeId: "c-1", workspaceId: WORKSPACE_ID, state: "REVIEW" },
      burst: null,
      decision,
      aiRecommendation,
    },
  };
}

async function gotoWithDecision(page: import("@playwright/test").Page, decision: unknown) {
  await page.route(SESSION_ROUTE_PATTERN, (route) => route.fulfill({ json: sessionOkBody(decision) }));
  await page.goto(PAGE_PATH);
  await page.getByTestId("decision-section").waitFor();
}

test("renders the AI recommendation separately from an UNDER_CONSIDERATION Decision, with a real interactive record-decision form", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await expect(page.getByTestId("ai-recommendation-panel")).toBeVisible();
  await expect(page.getByTestId("ai-recommendation-summary")).toContainText("Option A minimizes long-term cost");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("record-decision-form")).toBeVisible();
  await expect(page.getByTestId("decision-option-select")).toBeVisible();
});

test("recording a decision shows the fresh, server-returned DECIDED state -- never a client-guessed one", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({
      json: {
        kind: "committed",
        decision: {
          ...DECISION_UNDER_CONSIDERATION,
          state: "DECIDED",
          selectedOption: "Option A",
          rationale: "Lower cost",
          confidence: "high",
          decidedByUserId: "u-1",
          decidedAt: "2026-01-01T00:00:00Z",
        },
      },
    }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("decision-rationale-input").fill("Lower cost");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED");
  await expect(page.getByTestId("decision-provenance-view")).toBeVisible();
  await expect(page.getByTestId("decision-selected-option")).toContainText("Option A");
  await expect(page.getByTestId("record-decision-form")).toHaveCount(0);
});

test("mandatory attack: no label or action implies approving the AI recommendation as the Decision", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const section = page.getByTestId("decision-section");
  await expect(section.getByText(/approve/i)).toHaveCount(0);
  await expect(section.getByText(/accept ai/i)).toHaveCount(0);
  await expect(page.getByTestId("decision-option-select")).toHaveValue("");
});

test("mandatory attack: view-only action on the AI recommendation panel never creates or affects a Decision", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const panel = page.getByTestId("ai-recommendation-panel");
  await expect(panel.locator("button, input, form, select, [role='button']")).toHaveCount(0);
  await panel.click();
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("mandatory attack: disabled-button bypass -- rapid double-click submits only one command", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  let decideRequestCount = 0;
  await page.route(DECIDE_ROUTE_PATTERN, async (route) => {
    decideRequestCount += 1;
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({
      json: { kind: "committed", decision: { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" } },
    });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  const submitButton = page.getByTestId("record-decision-submit");
  await submitButton.click({ trial: false });
  await submitButton.click({ force: true }).catch(() => {});

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED", { timeout: 5000 });
  expect(decideRequestCount).toBe(1);
});

test("mandatory attack: role-only actor -- server DENY leaves the Decision unchanged, never DECIDED", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "denied", result: "DENY", reasonCode: "NOT_DECISION_RIGHT_HOLDER" } }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("denied-banner")).toBeVisible();
  await expect(page.getByTestId("denied-result")).toContainText("DENY");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("decision-provenance-view")).toHaveCount(0);
});

test("mandatory attack: no admin-labeled path exists anywhere in the Decision section", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const section = page.getByTestId("decision-section");
  await expect(section.getByText(/admin/i)).toHaveCount(0);
});

test("mandatory attack: auto-action after DECIDED -- no further action control renders", async ({ page }) => {
  await gotoWithDecision(page, { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" });

  await expect(page.getByTestId("decision-provenance-view")).toBeVisible();
  const section = page.getByTestId("decision-section");
  await expect(section.locator("button, input, form, select")).toHaveCount(0);
});

test("novel attack: server responds DENY after the click -- UI never shows a transiently-assumed DECIDED state", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    await route.fulfill({ json: { kind: "denied", result: "ESCALATE", reasonCode: "REQUIRES_ESCALATION" } });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("denied-banner")).toBeVisible({ timeout: 5000 });
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: network failure during the decision submission shows a visible error, never a silent hang", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) => route.abort());

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("network-error-banner")).toBeVisible();
  await expect(page.getByTestId("network-error-banner")).toContainText(/decision/i);
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: forged/rejected selected option is shown distinctly, never accepted as a false success", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "rejected", reasonCode: "SELECTED_OPTION_NOT_CANDIDATE" } }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-rejected-banner")).toBeVisible();
  await expect(page.getByTestId("decision-rejected-banner")).toContainText("SELECTED_OPTION_NOT_CANDIDATE");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: the request always carries the real decisionId, never a DOM-tamperable value", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  let capturedUrl: string | null = null;
  await page.route(DECIDE_ROUTE_PATTERN, (route) => {
    capturedUrl = route.request().url();
    return route.fulfill({
      json: { kind: "committed", decision: { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" } },
    });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED");
  expect(capturedUrl).toContain(`/decisions/${DECISION_UNDER_CONSIDERATION.decisionId}/decide`);
});

test("no Decision under consideration renders a passive placeholder, no interactive element at all", async ({ page }) => {
  await gotoWithDecision(page, null);

  await expect(page.getByTestId("decision-none")).toBeVisible();
  const section = page.getByTestId("decision-section");
  await expect(section.locator("button, input, form, select")).toHaveCount(0);
});

--- RAW TERMINAL OUTPUT (freshly re-run for this appendix) ---

=== typecheck ===
> nquiry-web@0.0.0 typecheck
> tsc --noEmit
EXIT:0

=== lint ===
> nquiry-web@0.0.0 lint
> eslint .
EXIT:0

=== vitest ===
> nquiry-web@0.0.0 test
> vitest run

 RUN  v4.1.11 /home/codi/Entwicklung/nquiry/apps/web

 Test Files  5 passed (5)
      Tests  53 passed (53)
   Start at  18:33:10
   Duration  508ms (transform 388ms, setup 0ms, import 675ms, tests 181ms, environment 1ms)
EXIT:0

=== playwright (full) ===
Running 22 tests using 4 workers

  ✓   3 tests/e2e/decision.spec.ts:110:1 › mandatory attack: no label or action implies approving the AI recommendation as the Decision (2.8s)
  ✓   4 tests/e2e/decision.spec.ts:120:1 › mandatory attack: view-only action on the AI recommendation panel never creates or affects a Decision (2.9s)
  ✓   2 tests/e2e/decision.spec.ts:78:1 › recording a decision shows the fresh, server-returned DECIDED state -- never a client-guessed one (3.3s)
  ✓   1 tests/e2e/decision.spec.ts:66:1 › renders the AI recommendation separately from an UNDER_CONSIDERATION Decision, with a real interactive record-decision form (3.1s)
  ✓   7 tests/e2e/decision.spec.ts:172:1 › mandatory attack: no admin-labeled path exists anywhere in the Decision section (1.4s)
  ✓   8 tests/e2e/decision.spec.ts:179:1 › mandatory attack: auto-action after DECIDED -- no further action control renders (1.4s)
  ✓   6 tests/e2e/decision.spec.ts:156:1 › mandatory attack: role-only actor -- server DENY leaves the Decision unchanged, never DECIDED (1.5s)
  ✓   5 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (1.8s)
  ✓  12 tests/e2e/decision.spec.ts:240:1 › novel attack: the request always carries the real decisionId, never a DOM-tamperable value (1.4s)
  ✓  11 tests/e2e/decision.spec.ts:223:1 › novel attack: forged/rejected selected option is shown distinctly, never accepted as a false success (1.6s)
  ✓  10 tests/e2e/decision.spec.ts:208:1 › novel attack: network failure during the decision submission shows a visible error, never a silent hang (1.7s)
  ✓   9 tests/e2e/decision.spec.ts:187:1 › novel attack: server responds DENY after the click -- UI never shows a transiently-assumed DECIDED state (2.0s)
  ✓  13 tests/e2e/decision.spec.ts:258:1 › no Decision under consideration renders a passive placeholder, no interactive element at all (1.4s)
  ✓  15 tests/e2e/session-view.spec.ts:67:1 › shows the frozen raw-set indicator once the Burst is COMPLETED (1.3s)
  ✓  14 tests/e2e/session-view.spec.ts:47:1 › renders the ok Session view with Workspace, Challenge, Session state, Burst state, HUMAN_ONLY indicator, and origin-marked questions (1.4s)
  ✓  16 tests/e2e/session-view.spec.ts:76:1 › renders the denied surface for a DENY/REQUIRE/ESCALATE server verdict, never the ok view (1.2s)
  ✓  19 tests/e2e/session-view.spec.ts:123:1 › mandatory attack: forged Workspace in client -- rendering is a pure function of the server's response, never the URL (1.4s)
  ✓  18 tests/e2e/session-view.spec.ts:89:1 › renders the INDETERMINATE surface with no retry control at all (1.5s)
  ✓  20 tests/e2e/session-view.spec.ts:136:1 › mandatory attack: attempt AI control during an ACTIVE Burst -- no AI-control element renders, only passive origin labels (1.5s)
  ✓  17 tests/e2e/session-view.spec.ts:100:1 › mandatory attack: no hidden/disabled action element exists in the DOM for any response shape (2.4s)
  ✓  21 tests/e2e/session-view.spec.ts:151:1 › mandatory attack: manipulate client capability flag -- no capability-flag-shaped field exists in the rendered response at all (1.2s)
  ✓  22 tests/e2e/session-view.spec.ts:173:1 › network failure renders a visible error state instead of hanging on Loading forever (1.1s)

  22 passed (13.7s)
EXIT:0

=== double-click run 1 ===
Running 1 test using 1 worker
  ✓  1 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (2.2s)
  1 passed (5.1s)

=== double-click run 2 ===
Running 1 test using 1 worker
  ✓  1 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (2.2s)
  1 passed (5.5s)

=== double-click run 3 ===
Running 1 test using 1 worker
  ✓  1 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (2.1s)
  1 passed (5.4s)

=== double-click run 4 ===
Running 1 test using 1 worker
  ✓  1 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (2.2s)
  1 passed (5.7s)

=== double-click run 5 ===
Running 1 test using 1 worker
  ✓  1 tests/e2e/decision.spec.ts:131:1 › mandatory attack: disabled-button bypass -- rapid double-click submits only one command (2.2s)
  1 passed (5.2s)

--- packages/domain/decision.py (full file, cat -n) ---

     1	"""Decision canonical object and its transition topology.
     2	
     3	Source: 02_DOMAIN_AND_RELATION_MODEL.md §26 (Decision -- CANONICAL_DOMAIN_OBJECT,
     4	identity via `Decision.id`, belongs to a Challenge, relates to Question/
     5	Evidence; §26.6 GAP-02-006 explicitly defers lifecycle/authority
     6	interaction to 03/04); 03_STATE_AND_TRANSITION_ARCHITECTURE.md §35
     7	(Decision State Architecture -- exact 2-value vocabulary
     8	UNDER_CONSIDERATION/DECIDED, `[ARCHITECTURAL CLOSURE]`), §36 (TRN-DEC-001
     9	OPEN_DECISION_CONSIDERATION, TRN-DEC-002 RECORD_HUMAN_DECISION -- exact
    10	CURRENT STATE/PRECONDITIONS/DENY CONDITION/NEXT STATE text), §37
    11	(Decision Does Not Equal Authorized Execution); 09_DATA_EVENT_API_CONTRACTS.md
    12	§47 (DATA CONTRACT: Decision -- exact field list).
    13	
    14	[... full module docstring omitted here for length, see file itself ...]
    15	"""
    16	
    17	from __future__ import annotations
    18	
    19	from dataclasses import dataclass
    20	from datetime import datetime
    21	from enum import Enum
    22	from uuid import UUID
    23	
    24	from semantic_types.ids import (
    25	    AuthorityBindingId,
    26	    ChallengeId,
    27	    DecisionId,
    28	    QuestionId,
    29	    UserId,
    30	    WorkspaceId,
    31	)
    32	from semantic_types.versions import RecordVersion
    33	
    34	
    35	class DecisionState(Enum):
    36	    """03 §35.2's exact 2-value closed vocabulary. `[ARCHITECTURAL
    37	    CLOSURE]`. Closed -- there is no third Decision state; 03 §38
    38	    (GAP-03-005) explicitly forbids `DECIDED -> UNDER_CONSIDERATION`
    39	    as a silent rewrite, so this vocabulary is not extended for
    40	    revision/supersession either.
    41	    """
    42	
    43	    UNDER_CONSIDERATION = "UNDER_CONSIDERATION"
    44	    DECIDED = "DECIDED"


NOTE: `DecisionState` real backend values -- `UNDER_CONSIDERATION`,
`DECIDED` -- CONFIRMED IDENTICAL to `types.ts`'s own
`DECISION_STATES = ["UNDER_CONSIDERATION", "DECIDED"] as const`
above, byte-for-byte, same order.

--- packages/application/human_decision_handler.py (SelectedOptionNotCandidate, lines 183-190 and 652-664) ---

183	class SelectedOptionNotCandidate(Exception):
184	    """Raised when `selected_option` is not among the Decision's own
185	    recorded `options` (only checked when `options` is non-empty --
186	    03/09 do not mandate a non-empty options list, so an empty list
187	    imposes no further constraint on `selected_option`'s content).
188	    """
189	
190	
...

652	    assert decision is not None  # BND-007 only ALLOWs when a Decision was resolved above.
653	
654	    # 04 section 50 DENY CONDITION: "Selected option not explicitly
655	    # human-adopted" -- the narrowest structural reading available
656	    # without inventing a sufficiency algorithm: when candidate options
657	    # were recorded at OPEN time, the human's selection must be one of
658	    # them.
659	    if decision.options and selected_option not in decision.options:
660	        raise SelectedOptionNotCandidate(
661	            f"selected_option {selected_option!r} is not among the Decision's own "
662	            f"options {decision.options!r}"
663	        )

NOTE: this package's own client-side "rejected" `DecisionActionResult`
case (kind: "rejected", reasonCode: "SELECTED_OPTION_NOT_CANDIDATE")
mirrors this exact real backend exception -- same trigger condition
(`selected_option not in decision.options`, only checked when
`options` is non-empty), same semantic distinction from a boundary
DENY (this check runs AFTER the BND-001..007 chain already ALLOWed,
per line 652's own assertion that `decision is not None` only holds
once BND-007 resolved).

================================================================
END RAW_EVIDENCE_APPENDIX
================================================================
