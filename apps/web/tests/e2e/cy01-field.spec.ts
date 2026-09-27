/**
 * WU-CY-01 (L3, mocked lane): the Session position projection across the ANALYSIS boundary as component contract in a
 * real browser, against `page.route()`-fulfilled envelopes in the EXACT shape of the pinned RED producer
 * `checkpoint-PFC-B5` (`7d3f74e4685b821cc948f45e413c1e0c207259d4`; `packages/application/inquiry_queries.py`
 * `session_position`, `analysis_projection.py`). Not runtime proof: the real-stack lane against the pinned producer is
 * `tests/real-stack/cy01-analysis.real.spec.ts`.
 *
 * Laws proven here (HD-27; doc 21 §16 origin grammar; 22 §30 re-read gate):
 * - an affordance exists exactly when the producer says `available`; the reason is the producer's, classed;
 * - the ring never advances on the request: ANALYSIS becomes current only after the canonical re-read;
 * - the derived field carries its AI-derived origin and NON_PROOF marker in words; no artifact text is rendered;
 * - a Fixture Session reads FIXTURE_NON_PROOF wherever the Session is named;
 * - an F03-shaped position (no new keys) renders exactly as before (regression against the F03 producer).
 */
import { expect, test, type Page, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SESSION = "55555550-5555-4555-8555-555555555555";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NOT = (code: string, reason = `not possible: ${code}`) => ({ available: false, reasonCode: code, reason });
const WORKSPACE = { workspaceId: WS, name: "Activation inquiry", governedFounding: true };
const MEMBERS = [
  { userId: "u-root", name: "Root Rosa", email: "root@nonproof.test", role: "Owner" },
  { userId: "u-fac", name: "Facilitator Fay", email: "fay@nonproof.test", role: "Facilitator" },
  { userId: "u-c1", name: "Contributor Constantine", email: "c1@nonproof.test", role: "Contributor" },
];
const CONTROLLER = { bindingId: "b1", holderUserId: "u-fac", holderName: "Facilitator Fay", authorityClass: "SESSION_CONTROL_RIGHT", scope: `SESSION:${SESSION}`, grantedByUserId: "u-root", grantedByName: "Root Rosa", grantedAt: "2026-09-24T11:00:00Z" };
const PHASES = ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS", "REFLECTION", "QUESTION_SELECTION", "INVESTIGATION", "EXPERIMENT", "ACTION", "REVIEW", "CLOSED"];
/** Every action key the pinned producer projects (inquiry_queries.py `actions`). */
const RED_ACTIONS = ["BEGIN_SETUP", "BEGIN_CHALLENGE_CAPTURE", "PREPARE_BURST", "ADMIT_PARTICIPANT", "OPEN_QUESTION_GENERATION", "GRANT_SESSION_CONTROL", "CAPTURE_QUESTION", "COMPLETE_BURST", "BEGIN_ANALYSIS", "REQUEST_QUESTION_ANALYSIS", "REQUEST_QUESTION_CLUSTERING", "BEGIN_REFLECTION", "BEGIN_QUESTION_SELECTION", "SELECT_COMPELLING_QUESTION", "SELECT_PRIMARY_QUESTION", "CREATE_IMPACT_CHAIN", "APPEND_IMPACT_CHAIN_NODE", "BEGIN_INVESTIGATION"] as const;
const F03_ACTIONS = RED_ACTIONS.slice(0, 8);
const MOCK_MARKER = { origin: "AI", derived: true, kind: "PROPOSAL", provider: "mock", proof: "MOCK / NON_PROOF", isMock: true, note: "Produced by the development MockProvider. It is not an analysis of these Questions and is not proof of anything." };
const SENTINEL = "SENTINEL_DERIVED_TEXT_NEVER_RENDERED";
const QUESTION = { questionId: "q-1", originalText: "Which step do most new users abandon first?", origin: "HUMAN", captureOrigin: "TYPED", authorUserId: "u-fac", authorName: "Facilitator Fay", capturedOrder: 0, capturedAt: "2026-09-25T01:40:00Z" };

type Opts = {
  readonly state?: "QUESTION_CAPTURE" | "ANALYSIS";
  readonly begin?: { available: boolean; reasonCode: string | null; reason: string | null };
  readonly fixture?: boolean;
  readonly analysisStatus?: "NOT_BEGUN" | "PENDING" | "RUNNING" | "UNAVAILABLE" | "ACCEPTED";
  readonly analysisVisible?: boolean;
  readonly viewer?: "u-fac" | "u-c1";
};

/** The pinned producer's `position` for a Session whose Burst is COMPLETED (frozen set served). */
function redPosition(o: Opts = {}) {
  const state = o.state ?? "QUESTION_CAPTURE";
  const inAnalysis = state === "ANALYSIS";
  const currentIndex = PHASES.indexOf(state);
  const actions = Object.fromEntries(
    RED_ACTIONS.map((name) => {
      if (name === "BEGIN_ANALYSIS") return [name, { ...(o.begin ?? AVAILABLE), relevant: !inAnalysis }];
      if (name === "GRANT_SESSION_CONTROL") return [name, { ...AVAILABLE, relevant: true }];
      if (name === "ADMIT_PARTICIPANT") return [name, { ...AVAILABLE, relevant: true }];
      if (name === "REQUEST_QUESTION_ANALYSIS" || name === "REQUEST_QUESTION_CLUSTERING") return [name, { ...NOT("NO_SESSION_CONTROL"), case: null, relevant: inAnalysis }];
      if (name === "BEGIN_QUESTION_SELECTION") return [name, { ...NOT("SESSION_NOT_IN_REFLECTION"), requiresReflectionCompletionConfirmation: true, relevant: false }];
      return [name, { ...NOT("NOT_RELEVANT_IN_STATE"), relevant: false }];
    }),
  );
  const status = o.analysisStatus ?? (inAnalysis ? "ACCEPTED" : "NOT_BEGUN");
  const artifact = status === "ACCEPTED" ? { artifactId: "a-1", generationId: "g-1", proofClass: "MOCK_NON_PROOF", isMockNonProof: true, acceptedAt: "2026-09-27T10:00:00Z", acceptedByCommandId: "c-9", marker: MOCK_MARKER, content: { items: [{ question_id: "q-1", text: SENTINEL }] } } : null;
  return {
    kind: "ok",
    serverNow: "2026-09-27T10:01:00Z",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: null },
    session: { sessionId: SESSION, state, version: 5, method: "HUMAN_QUESTION_BURST 1", createdAt: "2026-09-25T00:25:00Z", fixture: o.fixture ?? false, proofMode: o.fixture ? "FIXTURE_NON_PROOF" : "GOVERNED" },
    phases: PHASES.map((s, i) => ({ state: s, status: i < currentIndex ? "done" : i === currentIndex ? "current" : "upcoming" })),
    burst: { burstId: "b-1", state: "COMPLETED", mode: "HUMAN_ONLY", version: 3, startedAt: "2026-09-25T01:30:00Z", completedAt: "2026-09-25T01:50:00Z", guidanceSeconds: 600, guidanceIsAuthoritative: false },
    questionSet: { visibility: "FULL_FROZEN_SET", mine: [QUESTION], capturedCount: 1, frozen: { fingerprint: "fb294bbfe3e38cccc294affe7837daf763e4982e6de21c8ce9457e564abaeee6", verified: true, memberCount: 1, completedAt: "2026-09-25T01:50:00Z", questions: [QUESTION] } },
    analysis:
      o.analysisVisible === false
        ? { visible: false }
        : {
            visible: true,
            audience: "FROZEN_SET_AUDIENCE",
            marker: MOCK_MARKER,
            analysis: { status, reasonCode: status === "UNAVAILABLE" ? "PROVIDER_TIMEOUT" : status === "PENDING" ? "AUTHORIZATION_NOT_EXECUTED" : null, artifact },
            clustering: { status: "NOT_RUN", reasonCode: "NO_ACCEPTED_ANALYSIS", runId: null, marker: null, clusters: [{ clusterId: "k", label: SENTINEL, description: SENTINEL, questionIds: ["q-1"], generationId: "g-1" }] },
            generations: inAnalysis ? [{ generationId: "g-1", operation: "AIOP-001", status: "ACCEPTED", provider: "mock", model: "mock", failureCode: null, retryOf: null, authorization: null, requestedAt: "2026-09-27T09:59:00Z", completedAt: "2026-09-27T10:00:00Z" }] : [],
          },
    reflection: { fixture: o.fixture ?? false, eligible: false },
    reflectionCompletion: { basis: null },
    investigation: { fixture: o.fixture ?? false, begun: false },
    selection: { proofMode: o.fixture ? "FIXTURE_NON_PROOF" : "GOVERNED", primaryQuestionId: null, selections: [] },
    impactChain: { levels: [], nextLevel: 1, complete: false, answersVisible: true },
    participants: [
      { userId: "u-fac", name: "Facilitator Fay", joinedAt: "2026-09-25T01:00:00Z", admittedByUserId: "u-fac" },
      { userId: "u-c1", name: "Contributor Constantine", joinedAt: "2026-09-25T01:01:00Z", admittedByUserId: "u-fac" },
    ],
    sessionControllers: [CONTROLLER],
    establishedBy: { commandType: inAnalysis ? "CMD_BEGIN_ANALYSIS" : "COMPLETE_BURST", actorName: "Facilitator Fay", occurredAt: "2026-09-25T01:50:00Z", commitId: "550446e3-1dce-4cf3-a58d-be57a95d5672", authoritySourceType: "SESSION_CONTROL_RIGHT", authoritySourceRef: "b1", authorityScopeRef: `SESSION:${SESSION}` },
    viewer: { userId: o.viewer ?? "u-fac", role: o.viewer === "u-c1" ? "Contributor" : "Facilitator", isSessionController: o.viewer !== "u-c1", isGovernanceRoot: false },
    actions,
    admitCandidates: [],
    grantCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
  };
}

/** The F03 producer's `position` (published `field-F03`): no proofMode, no analysis, eight action keys. */
function f03Position() {
  const p = redPosition();
  const session: Record<string, unknown> = { ...p.session };
  const rest: Record<string, unknown> = { ...p };
  for (const key of ["fixture", "proofMode"]) delete session[key];
  for (const key of ["analysis", "reflection", "reflectionCompletion", "investigation", "selection", "impactChain"]) delete rest[key];
  return { ...rest, session, phases: PHASES.slice(0, 6).map((s, i) => ({ state: s, status: i < 4 ? "done" : i === 4 ? "current" : "upcoming" })), actions: Object.fromEntries(F03_ACTIONS.map((n) => [n, p.actions[n]])) };
}

function detail() {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: "Understand before changing.", createdAt: "2026-09-24T10:01:00Z" },
    sessions: [{ sessionId: SESSION, state: "QUESTION_CAPTURE", version: 5, createdAt: "2026-09-25T00:25:00Z" }],
    sessionControllers: [{ ...CONTROLLER, scope: `CHALLENGE:${CH}` }],
    members: MEMBERS,
    capabilities: { openSession: AVAILABLE, grantSessionControl: NOT("NOT_GOVERNANCE_ROOT", "Only the governance root grants Session control.") },
  };
}

async function routes(page: Page, position: unknown): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [{ workspaceId: WS, name: WORKSPACE.name, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" }] } }));
  await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: position }));
}
function gate(): { hold: (route: Route) => Promise<void>; release: (fulfil: (route: Route) => Promise<void>) => Promise<void> } {
  let held: Route | null = null;
  let resolveHeld: () => void = () => {};
  const arrived = new Promise<void>((r) => (resolveHeld = r));
  return {
    hold: (route) => { held = route; resolveHeld(); return arrived; },
    release: async (fulfil) => { await arrived; await fulfil(held as Route); },
  };
}
const hOverflow = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
const SESSION_URL = `/workspaces/${WS}/sessions/${SESSION}`;

test.describe("WU-CY-01: the ANALYSIS boundary as a projected affordance (HD-27, pinned producer B5)", () => {
  test("QUESTION_CAPTURE with BEGIN_ANALYSIS available: the lawful next transition sits in the frozen chamber; ANALYSIS is a later phase; the ring waits for the canonical re-read; then ANALYSIS is current and the derived chamber appears AI-derived and NON_PROOF", async ({ page }) => {
    let afterCommit = false;
    const g = gate();
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
    await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, async (route) => {
      if (!afterCommit) return route.fulfill({ json: redPosition() });
      await g.hold(route);
    });
    await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/transitions/begin-analysis`, async (route) => {
      expect(route.request().headers()["idempotency-key"]).toMatch(/[0-9a-f-]{36}/);
      expect(route.request().postDataJSON()).toEqual({ expectedVersion: 5 });
      afterCommit = true;
      await route.fulfill({ json: { kind: "committed", replayed: false, commandType: "CMD_BEGIN_ANALYSIS", commitId: "c-9", authorizationId: "oa-1", analysis: { status: "ACCEPTED" }, position: redPosition({ state: "ANALYSIS" }) } });
    });
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
    const frozen = page.getByTestId("active-phase");
    await expect(frozen).toHaveAttribute("data-semantic", "frozen");
    const begin = frozen.getByRole("button", { name: "Begin analysis" });
    await expect(begin).toBeVisible();
    await expect(frozen).toContainText("Begin analysis");
    // the producer already serves the derived field to the frozen-set audience: honest "not begun", no artifact
    await expect(page.getByTestId("analysis-chamber").getByTestId("analysis-status")).toHaveText("not begun");
    await expect(page.getByTestId("analysis-proof")).toHaveCount(0);
    const analysisNode = page.getByTestId("session-phases").locator('[data-key="ANALYSIS"]');
    await expect(analysisNode).toHaveAttribute("data-node-state", "future");

    await begin.click();
    // committed on the wire but not yet re-read: the ring and the state word stay put (22 §30)
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-reconstruction", "reading");
    await expect(page.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
    await expect(analysisNode).toHaveAttribute("data-node-state", "future");
    await expect(page.getByTestId("analysis-chamber").getByTestId("analysis-status")).toHaveText("not begun");
    await expect(page.getByTestId("field-event")).toHaveCount(0);

    await g.release((route) => route.fulfill({ json: redPosition({ state: "ANALYSIS" }) }));
    await expect(page.getByTestId("session-state")).toHaveText("ANALYSIS");
    await expect(analysisNode).toHaveAttribute("data-node-state", "current");
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-reconstruction", "done");
    await expect(page.getByTestId("field-event")).toContainText("ANALYSIS BEGUN");
    const chamber = page.getByTestId("analysis-chamber");
    await expect(chamber).toBeVisible();
    await expect(chamber).toHaveAttribute("data-semantic", "derived");
    await expect(chamber.locator('[data-origin="ai-derived"]').first()).toBeVisible();
    await expect(chamber.getByTestId("analysis-status")).toHaveText("accepted");
    await expect(chamber.getByTestId("analysis-proof")).toHaveText("MOCK / NON_PROOF");
    await expect(chamber).toContainText("MockProvider");
    // the frozen human set stays a separate, verbatim, human artifact; the derived field never becomes a question
    await expect(page.getByTestId("frozen-question")).toHaveCount(1);
    await expect(page.locator("body")).not.toContainText(SENTINEL);
    // no request affordance: RETRY / clustering are not in WU-CY-01
    await expect(page.getByRole("button", { name: /Begin analysis|Request|cluster/i })).toHaveCount(0);
  });

  test("not available: no button; the producer's reason stays verbatim as a classed boundary (MISSING_AUTHORITY), never an alert", async ({ page }) => {
    await routes(page, redPosition({ begin: NOT("NO_SESSION_CONTROL", "Only the Session controller may begin analysis."), viewer: "u-c1" }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
    await expect(page.getByRole("button", { name: "Begin analysis" })).toHaveCount(0);
    const reason = page.getByTestId("action-reason-BEGIN_ANALYSIS");
    await expect(reason).toContainText("Only the Session controller may begin analysis.");
    await expect(reason).toHaveAttribute("data-boundary", "MISSING_AUTHORITY");
    await expect(reason.locator('[role="alert"]')).toHaveCount(0);
    await expect(page.locator("main, aside").getByRole("alert")).toHaveCount(0);
  });

  test("a Fixture Session reads FIXTURE_NON_PROOF at the core, on the path and in the proof chamber; a mock artifact is MOCK / NON_PROOF; no derived text is rendered", async ({ page }) => {
    await routes(page, redPosition({ state: "ANALYSIS", fixture: true }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-proof-mode")).toHaveText("FIXTURE_NON_PROOF");
    await expect(page.getByTestId("proof-mode")).toContainText("FIXTURE_NON_PROOF");
    await expect(page.getByTestId("analysis-proof")).toHaveText("MOCK / NON_PROOF");
    await expect(page.getByTestId("analysis-chamber").locator('[data-origin="ai-derived"]').first()).toContainText("AI-derived");
    await expect(page.locator("body")).not.toContainText(SENTINEL);
    // the proof spine still names the governed commit: fixture is a proof CEILING, not a missing commit
    await expect(page.getByTestId("session-last-transition")).toContainText("CMD_BEGIN_ANALYSIS");
  });

  test("a governed Session shows its proof mode in the proof chamber only (no fixture tag at the core)", async ({ page }) => {
    await routes(page, redPosition({ state: "ANALYSIS" }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-proof-mode")).toHaveCount(0);
    await expect(page.getByTestId("proof-mode")).toContainText("GOVERNED");
  });

  test("UNAVAILABLE / PENDING analysis: honest state words with the producer's reason code; not an error", async ({ page }) => {
    await routes(page, redPosition({ state: "ANALYSIS", analysisStatus: "UNAVAILABLE" }));
    await page.goto(SESSION_URL);
    const chamber = page.getByTestId("analysis-chamber");
    await expect(chamber.getByTestId("analysis-status")).toHaveText("unavailable");
    await expect(chamber.getByTestId("analysis-reason")).toHaveText("PROVIDER_TIMEOUT");
    await expect(chamber).toHaveAttribute("data-tone", "boundary");
    await expect(page.locator("main, aside").getByRole("alert")).toHaveCount(0);
    await expect(chamber.getByTestId("analysis-proof")).toHaveCount(0);
  });

  test("outside the frozen-set audience the producer hides the derived field; nothing is shown and nothing is inferred", async ({ page }) => {
    await routes(page, redPosition({ state: "ANALYSIS", analysisVisible: false, viewer: "u-c1" }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-state")).toHaveText("ANALYSIS");
    await expect(page.getByTestId("analysis-chamber")).toHaveCount(0);
  });

  test("REGRESSION: an F03-shaped position (no new keys) renders exactly as before — no analysis chamber, no Begin analysis, no proof mode", async ({ page }) => {
    await routes(page, f03Position());
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
    await expect(page.getByTestId("active-phase")).toHaveAttribute("data-semantic", "frozen");
    await expect(page.getByTestId("frozen-set")).toBeVisible();
    await expect(page.getByRole("button", { name: "Begin analysis" })).toHaveCount(0);
    await expect(page.getByTestId("action-reason-BEGIN_ANALYSIS")).toHaveCount(0);
    await expect(page.getByTestId("analysis-chamber")).toHaveCount(0);
    await expect(page.getByTestId("proof-mode")).toHaveCount(0);
    await expect(page.getByTestId("session-proof-mode")).toHaveCount(0);
    await expect(page.getByTestId("session-phases").locator("li")).toHaveCount(6);
  });

  test("Challenge field: opening a Fixture Session is an explicit human choice sent as `fixture: true`; the default body stays `{}`", async ({ page }) => {
    const bodies: unknown[] = [];
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}/sessions`, (route) => {
      bodies.push(route.request().postDataJSON());
      return route.fulfill({ json: { kind: "denied", reasonCode: "NO_CHALLENGE_SESSION_CONTROL" } });
    });
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const choice = page.getByLabel(/Open as a Fixture Session/);
    await expect(choice).not.toBeChecked();
    await page.getByRole("button", { name: "Open Session" }).click();
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "denied");
    await choice.check();
    await page.getByRole("button", { name: "Open Session" }).click();
    await expect.poll(() => bodies.length).toBe(2);
    expect(bodies).toEqual([{}, { fixture: true }]);
    await expect(page.getByTestId("open-session-fixture-note")).toContainText("NON_PROOF");
  });

  test("responsive: the derived chamber adds no horizontal overflow and keeps its text ≥ 11.5 px", async ({ page }) => {
    await routes(page, redPosition({ state: "ANALYSIS", fixture: true }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("analysis-chamber")).toBeVisible();
    expect(await hOverflow(page)).toBeLessThanOrEqual(0);
    // the SF-03 material-text law (sf03-field.spec.ts `probe`): titles, monospace tokens, tags, state words and facts;
    // the chamber marker pill is a label, measured nowhere in the organ
    const small = await page.getByTestId("analysis-chamber").evaluate((el) => {
      const sizes: number[] = [];
      el.querySelectorAll("h2, h3, .mono, .tag, .state, dd, p").forEach((n) => {
        const cs = getComputedStyle(n);
        if (cs.display !== "none" && (n.textContent ?? "").trim() && !n.classList.contains("visually-hidden")) sizes.push(parseFloat(cs.fontSize));
      });
      return Math.min(...sizes);
    });
    expect(small).toBeGreaterThanOrEqual(11.5);
  });
});
