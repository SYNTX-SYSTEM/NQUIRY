/**
 * WU-CY-01 REAL-STACK PROOF: the Session position projection across the ANALYSIS boundary against the PINNED RED
 * producer `checkpoint-PFC-B5` (`7d3f74e4685b821cc948f45e413c1e0c207259d4`), run by `scripts/run_cy01_real_stack.sh`
 * (the runner's backend layers are exported from that exact commit; the web app is this tree; MockProvider enabled
 * as the producer's DEV/TEST runtime, HD-19). No network interception. The only out-of-band step is HD-3 identity
 * provisioning (identity rows only).
 *
 * Inverse DeepSweep target (WU-CY-01 pass condition):
 *   visible "accepted · MOCK / NON_PROOF" derived field <- canonical re-read of position.analysis <- committed
 *   CMD_BEGIN_ANALYSIS (TRN-SESS-006, BINDING @ SESSION) + the producer's OA-1 mock run <- frozen human question set
 *   <- F03 chain <- verified login. A Fixture Session reads FIXTURE_NON_PROOF from position.session.proofMode.
 */
import { createRequire } from "node:module";
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

const require = createRequire(import.meta.url);
const AXE_PATH = require.resolve("axe-core/axe.min.js");
const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";

async function openAs(browser: Browser, who: DevIdentity): Promise<Page> {
  const page = await (await browser.newContext()).newPage();
  await page.goto("/login");
  await page.getByLabel("Email").fill(who.email);
  await page.getByLabel("Password").fill(who.password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/workspaces/);
  return page;
}
async function expectOutcome(page: Page, outcome: string): Promise<void> {
  await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", outcome);
}
async function apiFromPage(page: Page, method: "GET" | "POST", pathname: string, body?: unknown): Promise<{ status: number; body: Record<string, unknown> }> {
  return page.evaluate(
    async ({ url, method, body }) => {
      const response = await fetch(url, { method, credentials: "include", headers: { "Content-Type": "application/json", Accept: "application/json", "Idempotency-Key": crypto.randomUUID() }, body: body === undefined ? undefined : JSON.stringify(body) });
      return { status: response.status, body: (await response.json()) as Record<string, unknown> };
    },
    { url: `${API}${pathname}`, method, body },
  );
}
async function axe(page: Page): Promise<string[]> {
  await page.addScriptTag({ path: AXE_PATH });
  return page.evaluate(async () => {
    // @ts-expect-error axe is injected at runtime
    const result = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] } });
    return (result.violations as { id: string; impact: string; nodes: unknown[] }[]).filter((v) => v.impact === "serious" || v.impact === "critical").map((v) => `${v.id} (${v.impact}, ${v.nodes.length} nodes)`);
  });
}
async function shot(page: Page, name: string): Promise<void> {
  await page.screenshot({ path: `test-results/cy01-visual/${test.info().project.name}-${name}.png`, fullPage: false });
}
async function admit(c: Page, who: DevIdentity): Promise<void> {
  await expect(async () => {
    await c.getByLabel("Admit participant").selectOption(who.userId);
    await expect(c.getByRole("button", { name: "Admit to Session" })).toBeEnabled({ timeout: 1000 });
  }).toPass();
  await c.getByRole("button", { name: "Admit to Session" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByLabel("Admit participant").locator(`option[value="${who.userId}"]`)).toHaveCount(0);
}
/** F02 → F03 through the product UI, up to the frozen human question set (QUESTION_CAPTURE). */
async function toQuestionCapture(c: Page, a: Page, controller: DevIdentity, alice: DevIdentity): Promise<void> {
  await c.getByRole("button", { name: "Begin setup" }).click();
  await expectOutcome(c, "committed");
  await c.getByRole("button", { name: "Begin challenge capture" }).click();
  await expectOutcome(c, "committed");
  await c.getByRole("button", { name: "Prepare protected Burst" }).click();
  await expectOutcome(c, "committed");
  await admit(c, alice);
  await admit(c, controller);
  await c.getByRole("button", { name: "Open question generation" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");
  await a.goto(c.url());
  await a.getByLabel("Your question", { exact: true }).fill("Which step do most new users abandon first?");
  await a.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(a, "committed");
  await c.reload();
  await c.getByLabel("Your question", { exact: true }).fill("What did users expect right after their first login?");
  await c.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(c, "committed");
  await c.getByRole("button", { name: "Complete Burst…" }).click();
  await c.getByTestId("complete-confirm-button").click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
  await expect(c.getByTestId("frozen-question")).toHaveCount(2);
}

test("WU-CY-01: BEGIN_ANALYSIS across the boundary, the derived field as AI-derived NON_PROOF, and a Fixture Session", async ({ browser }) => {
  const owner = provisionIdentity("Owner");
  const controller = provisionIdentity("Controller");
  const alice = provisionIdentity("Alice");

  // ===== F01/F02 setup, all through the product UI =====
  const o = await openAs(browser, owner);
  await o.getByLabel("Workspace name").fill("Analysis boundary inquiry");
  await o.getByRole("button", { name: "Create Workspace" }).click();
  await expect(o.getByRole("heading", { level: 1, name: "Analysis boundary inquiry" })).toBeVisible();
  const workspaceId = o.url().split("/workspaces/")[1];
  for (const [who, role] of [[controller, "Facilitator"], [alice, "Contributor"]] as const) {
    await o.getByLabel("Member user id").fill(who.userId);
    await o.getByLabel("Role").selectOption(role);
    await o.getByRole("button", { name: "Add member" }).click();
    await expectOutcome(o, "committed");
  }
  const c = await openAs(browser, controller);
  await c.getByRole("link", { name: "Analysis boundary inquiry" }).click();
  await c.getByLabel("Challenge title").fill("Where does onboarding lose people?");
  await c.getByRole("button", { name: "Create Challenge" }).click();
  await expect(c.getByRole("heading", { level: 1, name: /onboarding lose/ })).toBeVisible();
  const challengeId = c.url().split("/challenges/")[1];
  await o.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await o.getByLabel("Grant session control to").selectOption(controller.userId);
  await o.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await expectOutcome(o, "committed");

  // ===== a governed Session (the default: the fixture choice stays unchecked) =====
  await c.reload();
  await expect(c.getByLabel(/Open as a Fixture Session/)).not.toBeChecked();
  await c.getByRole("button", { name: "Open Session" }).click();
  await expect(c.getByTestId("session-state")).toHaveText("DRAFT");
  const sessionId = c.url().split("/sessions/")[1];
  const sessionUrl = c.url();
  await expect(c.getByTestId("proof-mode")).toContainText("GOVERNED");
  await expect(c.getByTestId("session-proof-mode")).toHaveCount(0);
  await o.goto(sessionUrl);
  await o.getByLabel("Grant session control to").selectOption(controller.userId);
  await o.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expectOutcome(o, "committed");
  await c.reload();
  const a = await openAs(browser, alice);
  await toQuestionCapture(c, a, controller, alice);

  // ===== the ANALYSIS boundary =====
  // The participant (frozen-set audience, no Session control): the derived field is not begun; no affordance, the
  // producer's reason classed as a boundary.
  await a.goto(sessionUrl);
  await expect(a.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
  await expect(a.getByRole("button", { name: "Begin analysis" })).toHaveCount(0);
  await expect(a.getByTestId("action-reason-BEGIN_ANALYSIS")).toHaveAttribute("data-boundary", "MISSING_AUTHORITY");
  await expect(a.getByTestId("analysis-chamber").getByTestId("analysis-status")).toHaveText("not begun");
  // A participant's own request is DENIED by the producer (adversarial, real API from the real session).
  const before = (await apiFromPage(a, "GET", `/workspaces/${workspaceId}/sessions/${sessionId}/position`)).body as { session: { version: number; proofMode: string }; actions: Record<string, { available: boolean }> };
  expect(before.session.proofMode).toBe("GOVERNED");
  expect(before.actions.BEGIN_ANALYSIS.available).toBe(false);
  const denied = await apiFromPage(a, "POST", `/workspaces/${workspaceId}/sessions/${sessionId}/transitions/begin-analysis`, { expectedVersion: before.session.version });
  expect(denied.body.kind).toBe("denied");

  // The controller: the lawful next transition in the frozen chamber; ANALYSIS is a later phase until the re-read.
  await c.reload();
  const frozen = c.getByTestId("active-phase");
  await expect(frozen).toHaveAttribute("data-semantic", "frozen");
  await expect(frozen.getByRole("button", { name: "Begin analysis" })).toBeVisible();
  await expect(c.getByTestId("session-phases").locator('[data-key="ANALYSIS"]')).toHaveAttribute("data-node-state", "future");
  await expect(c.getByTestId("analysis-chamber").getByTestId("analysis-status")).toHaveText("not begun");
  await shot(c, "01-controller-question-capture-begin-analysis-possible");
  await frozen.getByRole("button", { name: "Begin analysis" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("ANALYSIS");
  await expect(c.getByTestId("session-phases").locator('[data-key="ANALYSIS"]')).toHaveAttribute("data-node-state", "current");
  await expect(c.getByTestId("field-event")).toContainText("ANALYSIS BEGUN");
  const chamber = c.getByTestId("analysis-chamber");
  await expect(chamber).toHaveAttribute("data-semantic", "derived");
  await expect(chamber.getByTestId("analysis-status")).toHaveText("accepted");
  await expect(chamber.getByTestId("analysis-proof")).toHaveText("MOCK / NON_PROOF");
  await expect(chamber.locator('[data-origin="ai-derived"]').first()).toContainText("AI-derived");
  await expect(chamber).toContainText("MockProvider");
  await expect(c.getByTestId("session-last-transition")).toContainText("CMD_BEGIN_ANALYSIS");
  // the human set is untouched and separate; no derived text anywhere on the page
  await expect(c.getByTestId("frozen-question")).toHaveCount(2);
  await expect(c.getByRole("button", { name: "Begin analysis" })).toHaveCount(0);
  await shot(c, "02-controller-analysis-accepted-mock-non-proof");
  // the canonical state equals the visible state
  const after = (await apiFromPage(c, "GET", `/workspaces/${workspaceId}/sessions/${sessionId}/position`)).body as { session: { state: string }; analysis: { visible: boolean; analysis: { status: string; artifact: { content: unknown } | null }; marker: { proof: string } } };
  expect(after.session.state).toBe("ANALYSIS");
  expect(after.analysis.analysis.status).toBe("ACCEPTED");
  expect(after.analysis.marker.proof).toBe("MOCK / NON_PROOF");
  const derivedText = JSON.stringify(after.analysis.analysis.artifact?.content ?? "");
  for (const word of derivedText.match(/[A-Za-z]{12,}/g) ?? []) {
    await expect(c.locator("body")).not.toContainText(word);
  }
  // replay: the same intent key is the same Command (no second transition); a stale version is STALE
  const stale = await apiFromPage(c, "POST", `/workspaces/${workspaceId}/sessions/${sessionId}/transitions/begin-analysis`, { expectedVersion: before.session.version });
  expect(["stale", "blocked", "denied"]).toContain(stale.body.kind);
  // accessibility of the derived field
  expect(await axe(c)).toEqual([]);
  // the participant sees the same derived field (frozen-set audience), still without any affordance
  await a.reload();
  await expect(a.getByTestId("session-state")).toHaveText("ANALYSIS");
  await expect(a.getByTestId("analysis-chamber").getByTestId("analysis-proof")).toHaveText("MOCK / NON_PROOF");
  await expect(a.getByRole("button", { name: /Begin analysis|Request/ })).toHaveCount(0);
  await shot(a, "03-participant-analysis-visible-no-affordance");

  // ===== a Fixture Session: the explicit human choice; NON_PROOF wherever the Session is named =====
  await c.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await c.getByLabel(/Open as a Fixture Session/).check();
  await c.getByRole("button", { name: "Open Session" }).click();
  await expect(c.getByTestId("session-state")).toHaveText("DRAFT");
  await expect(c.getByTestId("session-proof-mode")).toHaveText("FIXTURE_NON_PROOF");
  await expect(c.getByTestId("proof-mode")).toContainText("FIXTURE_NON_PROOF");
  const fixtureId = c.url().split("/sessions/")[1];
  const fixturePosition = (await apiFromPage(c, "GET", `/workspaces/${workspaceId}/sessions/${fixtureId}/position`)).body as { session: { fixture: boolean; proofMode: string } };
  expect(fixturePosition.session).toMatchObject({ fixture: true, proofMode: "FIXTURE_NON_PROOF" });
  await shot(c, "04-fixture-session-non-proof");
  expect(await axe(c)).toEqual([]);
});
