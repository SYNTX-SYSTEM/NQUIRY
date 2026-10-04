/**
 * CYAN-PCPG-06 browser proof (mocked lane): Architecture 27 v4 levels 0.5 / 1 / 2 on the Session organism. A current
 * observation places its crossed steps at the EXISTING object areas as quiet markers (words, no control); the intent
 * chamber carries the "Field / Governance" disclosure with the deep view and the §09.3 boundary card; without an
 * observation nothing is placed and the panel makes no statement; a superseded observation says so; INDETERMINATE is
 * never "denied"; Send is "not materialized"; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";
const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SESSION = "55555550-5555-4555-8555-555555555555";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NOT = (code: string) => ({ available: false, reasonCode: code, reason: `not possible: ${code}` });
const WORKSPACE = { workspaceId: WS, name: "Activation inquiry", governedFounding: true };
const PHASES = ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS"];
function position() {
  const actions = Object.fromEntries(["BEGIN_SETUP", "BEGIN_CHALLENGE_CAPTURE", "PREPARE_BURST", "ADMIT_PARTICIPANT", "OPEN_QUESTION_GENERATION", "GRANT_SESSION_CONTROL", "CAPTURE_QUESTION", "COMPLETE_BURST"].map((n) => [n, { ...(n === "GRANT_SESSION_CONTROL" ? AVAILABLE : NOT("NOT_RELEVANT_IN_STATE")), relevant: n === "GRANT_SESSION_CONTROL" }]));
  const question = { questionId: "q-1", originalText: "Which step do most new users abandon first?", origin: "HUMAN", captureOrigin: "TYPED", authorUserId: "u-fac", authorName: "Facilitator Fay", capturedOrder: 0, capturedAt: "2026-09-25T01:40:00Z" };
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: null },
    session: { sessionId: SESSION, state: "QUESTION_CAPTURE", version: 4, method: "HUMAN_QUESTION_BURST", createdAt: "2026-09-25T00:25:00Z" },
    phases: PHASES.map((state, i) => ({ state, status: i < 4 ? "done" : i === 4 ? "current" : "upcoming" })),
    serverNow: "2026-09-25T02:00:00Z",
    burst: { burstId: "b-1", state: "COMPLETED", mode: "HUMAN_ONLY", version: 2, startedAt: "2026-09-25T01:30:00Z", completedAt: "2026-09-25T01:50:00Z", guidanceSeconds: 600, guidanceIsAuthoritative: true },
    questionSet: { visibility: "FULL_FROZEN_SET", mine: [question], capturedCount: 1, frozen: { fingerprint: "fb294bbfe3e38cccc294affe7837daf763e4982e6de21c8ce9457e564abaeee6", verified: true, memberCount: 1, completedAt: "2026-09-25T01:50:00Z", questions: [question] } },
    participants: [{ userId: "u-fac", name: "Facilitator Fay", joinedAt: "2026-09-25T01:00:00Z", admittedByUserId: "u-root" }],
    sessionControllers: [{ bindingId: "b1", holderUserId: "u-fac", holderName: "Facilitator Fay", authorityClass: "SESSION_CONTROL_RIGHT", scope: `SESSION:${SESSION}`, grantedByUserId: "u-root", grantedByName: "Root Rosa", grantedAt: "2026-09-24T11:00:00Z" }],
    establishedBy: { commandType: "COMPLETE_BURST", actorName: "Facilitator Fay", occurredAt: "2026-09-25T01:50:00Z", commitId: "550446e3-1dce-4cf3-a58d-be57a95d5672", authoritySourceType: "SESSION_CONTROL_RIGHT", authoritySourceRef: "b1", authorityScopeRef: `SESSION:${SESSION}` },
    viewer: { userId: "u-fac", role: "Facilitator", isSessionController: true, isGovernanceRoot: false },
    actions,
    admitCandidates: [],
    grantCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
  };
}

const PROVIDER = { deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: "QUESTION_CAPTURE", result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED" };
const HUMAN = { ...PROVIDER, deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", sourceClause: "pick the primary question", span: [23, 48], result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION" };
const GRANT = { ...PROVIDER, deltaId: "d-2", operation: "GRANT_SESSION_CONTROL", executionClass: "HUMAN_COMMAND", sourceClause: "and give Constantine control", span: [50, 78], result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" };
const RAW = "Analyse the questions, pick the primary question, and give Constantine control";
function current(deltas: unknown[], chain: Record<string, unknown>, providerExecutable = false) {
  return {
    kind: "current", contract: "PCPG-R12/1", basis: { rawIntentDigestSha256: "3f9a".padEnd(64, "0"), derivationTime: "2026-10-01T11:17:00+00:00" },
    semanticObservation: { ruleSetVersion: "26/2026-09-29", clauses: [RAW], actions: [], unknownRelations: [], relationsTouched: ["REQUEST_QUESTION_ANALYSIS"], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false },
    deltas,
    chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: false, ...chain },
    capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable, providerExecutableReasons: providerExecutable ? [] : ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false },
    composedProofCeiling: "GOVERNED",
  };
}
function envelope(governanceObservation: unknown) {
  return { kind: "ok", field: "PRE_CALL_PROMPT_GOVERNANCE", workspace: { workspaceId: WS, name: WORKSPACE.name }, session: { sessionId: SESSION }, rawIntent: RAW, rawIntentLength: RAW.length, rawIntentDigestSha256: "3f9a".padEnd(64, "0"), declaredPurpose: null, observedAt: "2026-10-01T11:17:00+00:00", governanceObservation };
}
const ANALYSIS = { visible: true, audience: "FROZEN_SET_AUDIENCE", marker: "MOCK / NON_PROOF", analysis: { status: "NOT_BEGUN", reasonCode: null, artifact: null }, clustering: { status: "NOT_RUN", reasonCode: "NO_ACCEPTED_ANALYSIS", runId: null, marker: null, clusters: [] }, generations: [] };
const SESSION_URL = `/workspaces/${WS}/sessions/${SESSION}`;
async function base(page: Page, withDerived = true): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: withDerived ? { ...position(), analysis: ANALYSIS } : position() }));
}
async function observe(page: Page, body: unknown): Promise<void> {
  await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => route.fulfill({ json: body }));
  await page.getByTestId("intent-text").fill(RAW);
  await page.getByTestId("observe-button").click();
}
const markers = (page: Page) => page.locator("[data-governance-attachment]");

test("no observation: nothing is placed anywhere; the panel makes no governance statement (NO OBSERVATION != CURRENT)", async ({ page }) => {
  await base(page);
  await page.goto(SESSION_URL);
  await expect(page.getByTestId("governance-membrane")).toContainText("No observation");
  await expect(markers(page)).toHaveCount(0);
  await expect(page.getByTestId("boundary-card")).toHaveCount(0);
  // the panel exists as a disclosure of the same object; closed; its body states the absence only
  const panel = page.getByTestId("governance-panel");
  await expect(panel).toHaveAttribute("data-observation", "none");
  await panel.locator("summary").click();
  await expect(page.getByTestId("governance-panel-none")).toContainText("No observation");
  await expect(panel.locator("button, a, input, form")).toHaveCount(0);
});

test("provider step: placed at the derived field chamber with 'Provider not executable · Send not materialized'; the deep view names every axis; INDETERMINATE is never denied", async ({ page }) => {
  await base(page);
  await page.goto(SESSION_URL);
  await observe(page, envelope(current([PROVIDER], {})));
  const marker = page.getByTestId("governance-attachment-derived-chamber");
  await expect(marker).toBeVisible();
  await expect(page.getByTestId("analysis-chamber").getByTestId("governance-attachment-derived-chamber")).toBeVisible();
  await expect(marker).toHaveAttribute("data-prominence", "explicit");
  await expect(marker).toContainText("1 crossed step placed here");
  await expect(marker).toContainText("REQUEST_QUESTION_ANALYSIS · provider computation — indeterminate · DATA_GOVERNANCE_NOT_MATERIALIZED");
  await expect(marker.getByTestId("attachment-provider")).toContainText("Provider not executable");
  await expect(marker.getByTestId("attachment-provider")).toContainText("Send not materialized");
  expect(await marker.innerText()).not.toMatch(/denied|disabled|allowed|ready/i);
  await expect(markers(page)).toHaveCount(1);
  await expect(marker.locator("button, a, input, form")).toHaveCount(0);
  const panel = page.getByTestId("governance-panel");
  await panel.locator("summary").click();
  await expect(page.getByTestId("governance-capability")).toContainText("Governance admissible");
  await expect(page.getByTestId("governance-capability")).toContainText("false · MLT_EMPTY");
  await expect(page.getByTestId("governance-capability")).toContainText("Provider executable");
  await expect(page.getByTestId("governance-capability")).toContainText("NO_ELIGIBLE_PROVIDER_ROUTE");
  await expect(page.getByTestId("governance-capability")).toContainText("Can send");
  await expect(page.getByTestId("governance-send")).toHaveText("Send not materialized");
  await expect(page.getByTestId("governance-deltas")).toContainText("the derived field chamber");
  await expect(page.getByTestId("governance-deltas")).toContainText("target: unresolved");
  await expect(page.getByTestId("governance-ceiling")).toContainText("governed");
  await expect(page.getByTestId("governance-not-materialized")).toContainText("SEND relation (R-13)");
  await expect(page.getByTestId("boundary-card")).toHaveCount(0);
  await expect(panel.locator("button, a, input, form")).toHaveCount(0);
});

test("without a derived chamber the provider step is NOT placed at any invented surface: membrane + panel only (§11.3)", async ({ page }) => {
  await base(page, false);
  await page.goto(SESSION_URL);
  await observe(page, envelope(current([PROVIDER], {})));
  await expect(page.getByTestId("governance-membrane")).toContainText("Provider not executable");
  await expect(markers(page)).toHaveCount(0);
  await page.getByTestId("governance-panel").locator("summary").click();
  await expect(page.getByTestId("governance-deltas")).toContainText("REQUEST_QUESTION_ANALYSIS");
});

test("boundary: the broken human step is placed at the question set; the authority step at the Session control chamber and the decision entry; the boundary card reads what stopped, requested in, why, after, HAR, placement", async ({ page }) => {
  await base(page);
  await page.goto(SESSION_URL);
  await observe(page, envelope(current([PROVIDER, HUMAN, GRANT], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN }, humanAuthorityRequired: [{ deltaId: "d-2", result: "AUTHORITY_BOUNDARY", reasonCode: "NOT_SESSION_CONTROLLER" }], partial: true })));
  await expect(page.getByTestId("governance-membrane")).toContainText("Human Authority required");
  const question = page.getByTestId("governance-attachment-question-set");
  await expect(question).toBeVisible();
  await expect(page.getByTestId("active-phase").getByTestId("governance-attachment-question-set")).toBeVisible();
  await expect(question).toHaveAttribute("data-prominence", "prominent");
  await expect(question).toContainText("SELECT_PRIMARY_QUESTION · human command — state boundary · SESSION_NOT_IN_QUESTION_SELECTION");
  await expect(question).toContainText("first broken relation");
  const authority = page.getByTestId("governance-attachment-authority-chamber");
  await expect(authority).toBeVisible();
  await expect(authority).toContainText("GRANT_SESSION_CONTROL · human command — authority boundary · NOT_SESSION_CONTROLLER");
  await expect(authority).toContainText("Human Authority required");
  await expect(page.getByTestId("governance-attachment-decision-entry-chamber")).toContainText("GRANT_SESSION_CONTROL");
  await expect(page.getByTestId("governance-attachment-derived-chamber")).toBeVisible();
  // no marker invents a control; nothing lands at an unmapped area
  await expect(page.locator("[data-governance-attachment] button, [data-governance-attachment] a, [data-governance-attachment] input")).toHaveCount(0);
  const areas = await markers(page).evaluateAll((els) => els.map((e) => e.getAttribute("data-governance-attachment")).sort());
  expect(areas).toEqual(["authority-chamber", "decision-entry-chamber", "derived-chamber", "question-set"]);
  await page.getByTestId("governance-panel").locator("summary").click();
  const card = page.getByTestId("boundary-card");
  await expect(card).toBeVisible();
  await expect(card.getByTestId("boundary-what")).toHaveText("SELECT_PRIMARY_QUESTION · human command");
  await expect(card.getByTestId("boundary-clause")).toHaveText("“pick the primary question”");
  await expect(card.getByTestId("boundary-why")).toHaveText("state boundary · SESSION_NOT_IN_QUESTION_SELECTION");
  await expect(card.getByTestId("boundary-after")).toHaveText("REQUEST_QUESTION_ANALYSIS");
  await expect(card.getByTestId("boundary-har")).toHaveText("d-2 → AUTHORITY_BOUNDARY · NOT_SESSION_CONTROLLER");
  await expect(card.getByTestId("boundary-placed")).toHaveText("the human question set");
  await expect(card).toHaveAttribute("data-partial", "true");
  expect(await card.innerText()).not.toMatch(/holder|binding|grantor|approve|button/i);
  await expect(card.locator("button, a, input, form")).toHaveCount(0);
  // §17 spoken facts, in words
  const spoken = await page.getByTestId("governance-spoken").innerText();
  expect(spoken).toMatch(/Governance for this session: Human Authority required\./);
  expect(spoken).toMatch(/First broken relation: SELECT_PRIMARY_QUESTION · human command, state boundary · SESSION_NOT_IN_QUESTION_SELECTION\./);
  expect(spoken).toMatch(/Human authority required for 1 requested step\./);
  expect(spoken).toMatch(/Chain partial\./);
  expect(spoken).toMatch(/Can send: false\. Send relation not materialized\./);
});

test("an unplaced step (operation null) lands at the proof chamber only; its words are 'Unknown operation'", async ({ page }) => {
  await base(page);
  await page.goto(SESSION_URL);
  await observe(page, envelope(current([{ ...HUMAN, deltaId: "d-9", operation: null, result: "INDETERMINATE", reasonCode: null }], {})));
  const proof = page.getByTestId("governance-attachment-proof-chamber");
  await expect(proof).toBeVisible();
  await expect(proof).toContainText("Unknown operation · human command — indeterminate");
  await expect(markers(page)).toHaveCount(1);
});

test("superseded: after a canonical version change the markers stay, say so and lose prominence; the membrane says Superseded; no sideways scroll", async ({ page }) => {
  await base(page);
  let version = 4;
  await page.unroute(`${API}/workspaces/${WS}/sessions/${SESSION}/position`);
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => { const p = position(); return route.fulfill({ json: { ...p, analysis: ANALYSIS, session: { ...p.session, version } } }); });
  await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => { version = 5; return route.fulfill({ json: { kind: "committed", replayed: false, bindingId: "b2" } }); });
  await page.goto(SESSION_URL);
  await observe(page, envelope(current([PROVIDER, HUMAN], { firstBrokenRelation: { predecessor: PROVIDER, broken: HUMAN } })));
  await expect(page.getByTestId("governance-attachment-question-set")).toHaveAttribute("data-prominence", "prominent");
  await page.getByLabel("Grant session control to").selectOption("u-c1");
  await page.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  await expect(page.getByTestId("governance-membrane")).toHaveAttribute("data-membrane-label", "SUPERSEDED");
  const marker = page.getByTestId("governance-attachment-question-set");
  await expect(marker).toBeVisible();
  await expect(marker).toHaveAttribute("data-superseded", "true");
  await expect(marker).toContainText("observed before the Session changed");
  await expect(page.getByTestId("governance-panel")).toHaveAttribute("data-superseded", "true");
  await page.getByTestId("governance-panel").locator("summary").click();
  await expect(page.getByTestId("governance-capability")).toContainText("absent (observation superseded)");
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
});
