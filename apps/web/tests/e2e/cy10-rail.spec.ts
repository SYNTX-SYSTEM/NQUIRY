/**
 * CYAN-RAIL-01 browser law (mocked lane, desktop widths): the route (five stations: Workspaces · Workspace · Challenge ·
 * Session · state) stays on one line LEFT of the centred mark at every desktop width, with the current station complete
 * and the established stations compressed but inspectable (title). Measured on every station, not only on the nav box.
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

const SESSION_URL = `/workspaces/${WS}/sessions/${SESSION}`;
const LONG_WS = "Cross-Functional Customer Activation and Retention Inquiry Workspace for the European Enterprise Segment";
async function routes(page: Page, state: string, longNames = false): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => {
    const p = position();
    const body = { ...p, session: { ...p.session, state }, workspace: longNames ? { ...p.workspace, name: LONG_WS } : p.workspace, challenge: longNames ? { ...p.challenge, title: "Why did activation stall after onboarding across every enterprise cohort we admitted this quarter?" } : p.challenge };
    return route.fulfill({ json: body });
  });
}
async function expectRouteInsideRail(page: Page, state: string): Promise<void> {
  const nav = page.getByRole("navigation", { name: "Inquiry position" });
  await nav.locator("li").first().waitFor();
  const identity = (await page.getByTestId("identity").boundingBox())!;
  const logout = (await page.getByTestId("logout-button").boundingBox())!;
  const vw = page.viewportSize()!.width;
  const boxes = await nav.locator("li").evaluateAll((els) => els.map((e) => { const b = e.getBoundingClientRect(); return { left: b.left, right: b.right, top: Math.round(b.top), status: (e as HTMLElement).dataset.status }; }));
  expect(boxes.length).toBe(5);
  expect(new Set(boxes.map((b) => b.top)).size, `one line: ${boxes.map((b) => b.top).join(",")}`).toBe(1);
  for (const b of boxes) expect(b.right, `${b.status} station ends before the mark`).toBeLessThanOrEqual(identity.x + 1);
  expect(Math.abs(identity.x + identity.width / 2 - vw / 2)).toBeLessThan(6);
  expect(identity.x + identity.width).toBeLessThanOrEqual(logout.x + 1);
  const current = nav.locator('li[data-status="current"] .trace-label');
  await expect(current).toHaveText(state);
  expect(await current.evaluate((el) => el.scrollWidth <= el.clientWidth + 1), "current label complete").toBe(true);
  // sub-pixel: the label's box carries its whole text advance (a box short by a fraction of a pixel already draws the ellipsis)
  expect(await current.evaluate((el) => { const r = document.createRange(); r.selectNodeContents(el); return el.getBoundingClientRect().width - r.getBoundingClientRect().width; }), "label box carries the text advance").toBeGreaterThanOrEqual(-0.01);
  await expect(nav.locator('li[data-coordinate="challenge"] a')).toHaveAttribute("title", /.+/);
  for (const li of await nav.locator("li").all()) expect(await li.locator("a, .trace-label").first().evaluate((el) => parseFloat(getComputedStyle(el).fontSize))).toBeGreaterThanOrEqual(13.5);
}
for (const width of [1024, 1180, 1280, 1366, 1440, 1600]) {
  for (const [state, longNames] of [["ANALYSIS", false], ["QUESTION_GENERATION", false], ["QUESTION_GENERATION", true], ["CHALLENGE_CAPTURE", true]] as const) {
    test(`${width} px · ${state}${longNames ? " · long names" : ""}: five stations on one line left of the centred mark, current complete`, async ({ page }, info) => {
      test.skip(info.project.name === "mobile", "desktop rail law");
      await page.setViewportSize({ width, height: 860 });
      await routes(page, state, longNames);
      await page.goto(SESSION_URL);
      await page.getByTestId("field-core").waitFor();
      await expectRouteInsideRail(page, state);
    });
  }
}
