/**
 * F02 REAL-STACK PROOF — Challenge · Session · Participation.
 *
 * Every step below goes through the real browser UI (or, for the
 * adversarial steps, a real cross-origin `fetch` issued from the page
 * with the real session cookie). Nothing is mocked. The only
 * out-of-band step is HD-3 identity provisioning (identity rows only).
 *
 * Inverse DeepSweep target (F02 pass condition):
 *   visible QUESTION_GENERATION ← server state ← API ← canonical Session
 *   reread ← committed transition ← BND-014 ← Session controller ←
 *   SESSION_CONTROL_RIGHT @ SESSION:<id> ← lawful grant by governance
 *   root ← active membership ← governance root ← authenticated identity.
 */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";

async function openAs(browser: Browser, who: DevIdentity): Promise<Page> {
  const context = await browser.newContext();
  const page = await context.newPage();
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

/** Real network call from inside the page, carrying the real cookie. */
async function apiFromPage(
  page: Page,
  method: "GET" | "POST",
  pathname: string,
  body?: unknown,
): Promise<{ status: number; body: Record<string, unknown> }> {
  return page.evaluate(
    async ({ url, method, body }) => {
      const response = await fetch(url, {
        method,
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      return { status: response.status, body: (await response.json()) as Record<string, unknown> };
    },
    { url: `${API}${pathname}`, method, body },
  );
}

/** Visual proof: real rendered pages, one file per project and step. */
async function shot(page: Page, name: string): Promise<void> {
  const project = test.info().project.name;
  await page.screenshot({ path: `test-results/f02-visual/${project}-${name}.png`, fullPage: true });
}

test("F02: a governed inquiry context is created and lawfully reaches QUESTION_GENERATION", async ({ browser }) => {
  const owner = provisionIdentity("Owner");
  const facilitator = provisionIdentity("Facilitator");
  const outsider = provisionIdentity("Outsider");

  // --- A founds a Workspace (F01 semantics, real CMD_CREATE_WORKSPACE) ---
  const a = await openAs(browser, owner);
  await a.getByLabel("Workspace name").fill("Conversion inquiry");
  await a.getByRole("button", { name: "Create Workspace" }).click();
  await expect(a.getByRole("heading", { level: 1, name: "Conversion inquiry" })).toBeVisible();
  const workspaceUrl = a.url();
  const workspaceId = workspaceUrl.split("/workspaces/")[1];

  // A, as governance root, admits B as a Facilitator member.
  await a.getByLabel("Member user id").fill(facilitator.userId);
  await a.getByLabel("Role").selectOption("Facilitator");
  await a.getByRole("button", { name: "Add member" }).click();
  await expectOutcome(a, "committed");
  await expect(a.getByTestId("members-list")).toContainText(facilitator.name);

  // The Owner is not a Facilitator: no Challenge creation affordance, and the reason is shown.
  await expect(a.getByRole("button", { name: "Create Challenge" })).toHaveCount(0);
  await expect(a.getByTestId("challenge-create-unavailable")).toContainText("Facilitator");
  await shot(a, "01-workspace-owner");

  // --- B creates a Challenge (ROLE-sourced authority, AUTH-DEP-CH-001) ---
  const b = await openAs(browser, facilitator);
  await b.getByRole("link", { name: "Conversion inquiry" }).click();
  await b.getByLabel("Challenge title").fill("Signup conversion dropped 18% after the redesign");
  await b.getByLabel("Description").fill("Understand why before choosing what to change.");
  await b.getByRole("button", { name: "Create Challenge" }).click();
  await expect(b.getByRole("heading", { level: 1, name: /Signup conversion dropped/ })).toBeVisible();
  const challengeId = b.url().split("/challenges/")[1];

  // Without SESSION_CONTROL_RIGHT @ CHALLENGE, B cannot open a Session, and is told why.
  await expect(b.getByRole("button", { name: "Open Session" })).toHaveCount(0);
  await expect(b.getByTestId("session-create-unavailable")).toContainText("SESSION_CONTROL_RIGHT");
  await shot(b, "02-challenge-no-session-control");

  // A grants B SESSION_CONTROL_RIGHT for this Challenge (governance, BINDING).
  await a.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await a.getByLabel("Grant session control to").selectOption(facilitator.userId);
  await a.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await expectOutcome(a, "committed");

  // --- B opens a Session (TRN-SESS-001) ---
  await b.reload();
  await b.getByRole("button", { name: "Open Session" }).click();
  await expect(b.getByTestId("session-state")).toHaveText("DRAFT");
  const sessionUrl = b.url();
  const sessionId = sessionUrl.split("/sessions/")[1];

  // HD-1: Challenge-scoped control does NOT cover the Session. No transition yet.
  await expect(b.getByRole("button", { name: "Begin setup" })).toHaveCount(0);
  await expect(b.getByTestId("action-reason-BEGIN_SETUP")).toContainText("SESSION");
  await shot(b, "03-session-draft-no-control");

  // A grants B SESSION_CONTROL_RIGHT at SESSION:<id> explicitly.
  await a.goto(`/workspaces/${workspaceId}/sessions/${sessionId}`);
  await a.getByLabel("Grant session control to").selectOption(facilitator.userId);
  await a.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expectOutcome(a, "committed");
  // The Owner still holds no Session control: no transition affordance for A.
  await expect(a.getByRole("button", { name: "Begin setup" })).toHaveCount(0);

  // --- Unauthorized human: real API call is DENIED, never committed ---
  const denied = await apiFromPage(a, "POST", `/workspaces/${workspaceId}/sessions/${sessionId}/transitions/begin-setup`, {
    expectedVersion: 1,
  });
  expect(denied.body.kind).toBe("denied");

  // --- Stale version: a second, stale view of the same Session ---
  const stale = await b.context().newPage();
  await stale.goto(sessionUrl);
  await expect(stale.getByTestId("session-state")).toHaveText("DRAFT");

  await b.reload();
  await b.getByRole("button", { name: "Begin setup" }).click();
  await expectOutcome(b, "committed");
  await expect(b.getByTestId("session-state")).toHaveText("SETUP");

  await stale.getByRole("button", { name: "Begin setup" }).click();
  await expectOutcome(stale, "stale");
  await expect(stale.getByTestId("session-state")).toHaveText("SETUP");
  await shot(stale, "04-stale-outcome");

  // --- Cross-Workspace actor: denied on read and on write ---
  const c = await openAs(browser, outsider);
  const crossRead = await apiFromPage(c, "GET", `/workspaces/${workspaceId}/sessions/${sessionId}/position`);
  expect(crossRead.body.kind).toBe("denied");
  const crossWrite = await apiFromPage(
    c,
    "POST",
    `/workspaces/${workspaceId}/sessions/${sessionId}/transitions/begin-challenge-capture`,
    { expectedVersion: 2 },
  );
  expect(crossWrite.body.kind).toBe("denied");

  // --- Malformed input is REJECTED, not DENIED ---
  const malformed = await apiFromPage(b, "POST", `/workspaces/${workspaceId}/sessions/not-a-uuid/transitions/begin-setup`, {
    expectedVersion: 1,
  });
  expect(malformed.body.kind).toBe("rejected");

  // --- Lawful progression to QUESTION_GENERATION ---
  await b.getByRole("button", { name: "Begin challenge capture" }).click();
  await expectOutcome(b, "committed");
  await expect(b.getByTestId("session-state")).toHaveText("CHALLENGE_CAPTURE");

  // HD-8: Question Generation cannot open without a participant.
  await b.getByRole("button", { name: "Prepare protected Burst" }).click();
  await expectOutcome(b, "committed");
  await expect(b.getByTestId("burst-state")).toHaveText("PREPARED");
  await expect(b.getByRole("button", { name: "Open question generation" })).toHaveCount(0);
  await expect(b.getByTestId("action-reason-OPEN_QUESTION_GENERATION")).toContainText("participant");
  await shot(b, "05-blocked-no-participant");

  // HD-7: the Session controller admits participants.
  await b.getByLabel("Admit participant").selectOption(owner.userId);
  await b.getByRole("button", { name: "Admit to Session" }).click();
  await expectOutcome(b, "committed");
  await expect(b.getByTestId("participants-list")).toContainText(owner.name);

  await b.getByRole("button", { name: "Open question generation" }).click();
  await expectOutcome(b, "committed");
  await expect(b.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");
  await expect(b.getByTestId("burst-state")).toHaveText("ACTIVE");
  await expect(b.getByTestId("burst-mode")).toHaveText("HUMAN_ONLY");

  // Canonical, not client-held: a fresh load shows the same state and its provenance.
  await b.reload();
  await expect(b.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");
  const provenance = b.getByTestId("session-authority-provenance");
  await expect(provenance).toContainText("SESSION_CONTROL_RIGHT");
  await expect(provenance).toContainText(owner.name);
  await expect(b.getByTestId("session-last-transition")).toContainText("OPEN_QUESTION_GENERATION");
  await shot(b, "06-question-generation-controller");

  // The Owner sees the same canonical state, still without control affordances.
  await a.reload();
  await expect(a.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");
  await expect(a.getByRole("button", { name: /Begin|Open question|Prepare/ })).toHaveCount(0);
  await shot(a, "07-question-generation-owner");
});
