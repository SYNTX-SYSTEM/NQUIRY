/**
 * CYAN-PCPG-05 REAL-STACK PROOF against the pinned producer checkpoint-PFC-PCPG-18 (41b4324a75077ec33b00ed3a878db7a318fc00d8),
 * run by scripts/run_cy01_real_stack.sh (local/test lane only). No network interception. The actor types an intent
 * for a real Session and observes it: the real PCPG-R12/1 projection drives the membrane; nothing is executed, sent,
 * granted or persisted; a committed command afterwards supersedes the observation; a reload returns to "No observation".
 */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";
const LABELS = ["OBSERVED", "PARTIAL", "BOUNDARY_REACHED", "HUMAN_AUTHORITY_REQUIRED", "PROVIDER_NOT_EXECUTABLE"];

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
async function positionOf(page: Page, workspaceId: string, sessionId: string): Promise<Record<string, unknown>> {
  return page.evaluate(async (url) => (await (await fetch(url, { credentials: "include" })).json()) as Record<string, unknown>, `${API}/workspaces/${workspaceId}/sessions/${sessionId}/position`);
}
const membrane = (page: Page) => page.getByTestId("field-core").getByTestId("governance-membrane");

test("CYAN-PCPG-05: a real intent observation drives the membrane; observe ≠ execute; supersession; reload", async ({ browser }) => {
  const owner = provisionIdentity("Owner");
  const controller = provisionIdentity("Controller");
  const alice = provisionIdentity("Alice");

  const o = await openAs(browser, owner);
  await o.getByLabel("Workspace name").fill("Observation inquiry");
  await o.getByRole("button", { name: "Create Workspace" }).click();
  await expect(o.getByRole("heading", { level: 1, name: "Observation inquiry" })).toBeVisible();
  const workspaceId = o.url().split("/workspaces/")[1];
  for (const [who, role] of [[controller, "Facilitator"], [alice, "Contributor"]] as const) {
    await o.getByLabel("Member user id").fill(who.userId);
    await o.getByLabel("Role").selectOption(role);
    await o.getByRole("button", { name: "Add member" }).click();
    await expectOutcome(o, "committed");
  }
  const c = await openAs(browser, controller);
  await c.getByRole("link", { name: "Observation inquiry" }).click();
  await c.getByLabel("Challenge title").fill("Where does onboarding lose new admins?");
  await c.getByRole("button", { name: "Create Challenge" }).click();
  await expect(c.getByRole("heading", { level: 1, name: /onboarding lose/ })).toBeVisible();
  const challengeId = c.url().split("/challenges/")[1];
  await o.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await o.getByLabel("Grant session control to").selectOption(controller.userId);
  await o.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await expectOutcome(o, "committed");
  await c.reload();
  await c.getByRole("button", { name: "Open Session" }).click();
  await expect(c.getByTestId("session-state")).toHaveText("DRAFT");
  const sessionId = c.url().split("/sessions/")[1];
  const sessionUrl = c.url();

  // 1. no standing observation
  await expect(membrane(c)).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
  const before = await positionOf(c, workspaceId, sessionId);

  // 24./5. a real observation (PCPG-18 runtime composition) through the product UI
  await c.getByTestId("intent-text").fill("begin the setup of this session");
  await c.getByTestId("observe-button").click();
  await expect(membrane(c)).not.toHaveAttribute("data-membrane-label", "NO_OBSERVATION", { timeout: 20000 });
  const label = await membrane(c).getAttribute("data-membrane-label");
  expect(LABELS).toContain(label);
  await expect(membrane(c).getByTestId("membrane-observed-at")).toContainText("observed at");
  await expect(c.getByTestId("observation-facts")).toBeVisible();
  await expect(c.getByTestId("observe-failure")).toHaveCount(0);
  await c.screenshot({ path: `test-results/cy05-visual/${test.info().project.name}-real-observed.png` });
  // observe ≠ execute: the canonical Session is unchanged
  const after = await positionOf(c, workspaceId, sessionId);
  expect((after.session as { state: string; version: number })).toEqual((before.session as { state: string; version: number }));
  expect(JSON.stringify(after.analysis)).toBe(JSON.stringify(before.analysis));
  // no send-like control anywhere
  await expect(c.locator("main, aside").getByRole("button", { name: /^(Send|Run|Execute|Submit to AI)$/ })).toHaveCount(0);

  // 6. a genuinely unparseable intent (R-05 failure) → Governance unavailable, nothing synthesized
  await c.getByTestId("intent-text").fill("日本語のテキストです");
  await c.getByTestId("observe-button").click();
  await expect(membrane(c)).toHaveAttribute("data-membrane-label", "GOVERNANCE_UNAVAILABLE", { timeout: 20000 });
  await expect(membrane(c)).not.toContainText(/admissible|Boundary|Authority|Provider/);

  // 12. observe again → replaced
  await c.getByTestId("intent-text").fill("begin the setup of this session");
  await c.getByTestId("observe-button").click();
  await expect(membrane(c)).not.toHaveAttribute("data-membrane-label", "GOVERNANCE_UNAVAILABLE", { timeout: 20000 });
  const digest = await c.getByTestId("observed-digest").innerText();

  // 13. a committed command changes the canonical version → Superseded; observation unchanged
  await o.goto(sessionUrl);
  await o.getByLabel("Grant session control to").selectOption(controller.userId);
  await o.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expectOutcome(o, "committed");
  // 15. reload → honestly "No observation" (the grant above is read on this reload; the observation is gone by design)
  await c.reload();
  await expect(membrane(c)).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
  await expect(c.getByTestId("intent-text")).toHaveValue("");
  // supersession on a live re-read: observe, then commit a transition on the same page
  await c.getByTestId("intent-text").fill("begin the setup of this session");
  await c.getByTestId("observe-button").click();
  await expect(membrane(c)).not.toHaveAttribute("data-membrane-label", "NO_OBSERVATION", { timeout: 20000 });
  const digest2 = await c.getByTestId("observed-digest").innerText();
  expect(digest2).toBe(digest);
  await c.getByRole("button", { name: "Begin setup" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("SETUP");
  await expect(membrane(c)).toHaveAttribute("data-membrane-label", "SUPERSEDED");
  await expect(c.getByTestId("observe-superseded")).toBeVisible();
  await expect(c.getByTestId("observed-digest")).toHaveText(digest2);
  // a participant without authority may observe as well (4.)
  const a = await openAs(browser, alice);
  await a.goto(sessionUrl);
  await expect(a.getByTestId("observe-button")).toBeVisible();
  await a.getByTestId("intent-text").fill("begin the setup of this session");
  await a.getByTestId("observe-button").click();
  await expect(membrane(a)).not.toHaveAttribute("data-membrane-label", "NO_OBSERVATION", { timeout: 20000 });
  expect(await a.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0]);
});
