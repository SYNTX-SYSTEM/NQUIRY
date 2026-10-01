/**
 * CYAN-PCPG-04 narrow browser proof (mocked lane): the Session object carries the membrane as a quiet strip inside
 * its core; with no observation producer on the surface it reads "No observation"; it adds no control and no
 * governance appears at any attachment target (falsifiers 1, 10, 17, 18, 19 in a real browser).
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
async function routes(page: Page): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-fac" } }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: position() }));
}

test("the Session object carries the membrane inside its core: 'No observation', quiet, no control, nothing at any attachment target", async ({ page }) => {
  const prompt: string[] = [];
  await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => {
    prompt.push(route.request().method());
    return route.fulfill({ json: { kind: "rejected", reasonCode: "RAW_INTENT_REQUIRED" } });
  });
  await routes(page);
  await page.goto(`/workspaces/${WS}/sessions/${SESSION}`);
  await expect(page.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
  const membrane = page.getByTestId("field-core").getByTestId("governance-membrane");
  await expect(membrane).toHaveCount(1);
  await expect(membrane).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
  await expect(membrane).toHaveAttribute("data-prominence", "quiet");
  await expect(membrane.getByTestId("membrane-words")).toHaveText("No observation");
  await expect(membrane).toHaveAttribute("role", "status");
  await expect(membrane.locator("button, a, input, select, textarea, form")).toHaveCount(0);
  // no observation is ever requested without the actor's intent: the query was never called
  expect(prompt).toEqual([]);
  // nothing is rendered at any attachment target yet (PCPG-05)
  await expect(page.locator("[data-governance-attachment], [data-membrane-label]:not([data-testid='governance-membrane'])")).toHaveCount(0);
  // the organism is unchanged around it
  await expect(page.getByTestId("session-phases")).toBeVisible();
  await expect(page.getByTestId("active-phase")).toHaveAttribute("data-semantic", "frozen");
  await expect(page.getByTestId("context-organ")).toBeVisible();
  // the strip is legible and inside the core box
  const sizes = await membrane.evaluate((el) => {
    const r = el.getBoundingClientRect();
    const core = el.closest(".core")?.getBoundingClientRect();
    const fs = Math.min(...[...el.querySelectorAll(".membrane-words, .membrane-time")].map((n) => parseFloat(getComputedStyle(n).fontSize)));
    return { inside: !!core && r.left >= core.left - 1 && r.right <= core.right + 1 && r.bottom <= core.bottom + 1, fs, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
  });
  expect(sizes.inside).toBe(true);
  expect(sizes.fs).toBeGreaterThanOrEqual(11.5);
  expect(sizes.overflow).toBeLessThanOrEqual(0);
  await page.screenshot({ path: `test-results/cy04-visual/${test.info().project.name}-membrane-no-observation.png` });
});
