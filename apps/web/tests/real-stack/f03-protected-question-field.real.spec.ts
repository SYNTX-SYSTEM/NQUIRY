/**
 * F03 REAL-STACK PROOF: the protected human question field.
 *
 * Real Chromium -> real Next.js -> real FastAPI -> real local auth -> real
 * PostgreSQL -> real governed Commands. No network interception, no fulfilled
 * responses. The only out-of-band step is HD-3 identity provisioning
 * (identity rows only, no authority); every membership, role, control and
 * participation below is created through the product UI.
 *
 * Inverse DeepSweep target (F03 pass condition):
 *   visible frozen human question set <- canonical re-read <- committed
 *   CMD_COMPLETE_BURST (BINDING @ SESSION:<id>) <- ACTIVE Burst with committed
 *   human Questions <- committed CMD_CAPTURE_BURST_QUESTION x N (PARTICIPATION
 *   right, exact original text, HUMAN origin) <- lawful admission by the
 *   Session controller <- QUESTION_GENERATION <- F02 chain <- verified login.
 */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

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
        headers: { "Content-Type": "application/json", Accept: "application/json", "Idempotency-Key": crypto.randomUUID() },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      return { status: response.status, body: (await response.json()) as Record<string, unknown> };
    },
    { url: `${API}${pathname}`, method, body },
  );
}

async function shot(page: Page, name: string): Promise<void> {
  const project = test.info().project.name;
  await page.screenshot({ path: `test-results/f03-visual/${project}-${name}.png`, fullPage: true });
}

/** The exact characters of a rendered verbatim block (Playwright's text matchers normalize whitespace). */
async function exactText(locator: ReturnType<Page["getByTestId"]>): Promise<string> {
  return locator.evaluate((el) => el.textContent ?? "");
}

const QUESTION_A = "  Why did “the checkout” drop after step 2 — 如何 تحسين ?  ";
const QUESTION_B = "Which segment abandons first?";
const QUESTION_C = "Is the latency real,\nor only perceived?";
const QUESTION_F = "What would change our minds?";

test("F03: protected human question capture, manual completion and the frozen set", async ({ browser }) => {
  const owner = provisionIdentity("Owner");
  const controller = provisionIdentity("Controller");
  const alice = provisionIdentity("Alice");
  const bob = provisionIdentity("Bob");
  const outsider = provisionIdentity("Outsider");

  // ===== F01/F02 setup, all through the product UI =====
  const o = await openAs(browser, owner);
  await o.getByLabel("Workspace name").fill("Protected inquiry");
  await o.getByRole("button", { name: "Create Workspace" }).click();
  await expect(o.getByRole("heading", { level: 1, name: "Protected inquiry" })).toBeVisible();
  const workspaceId = o.url().split("/workspaces/")[1];

  for (const [who, role] of [
    [controller, "Facilitator"],
    [alice, "Contributor"],
    [bob, "Contributor"],
  ] as const) {
    await o.getByLabel("Member user id").fill(who.userId);
    await o.getByLabel("Role").selectOption(role);
    await o.getByRole("button", { name: "Add member" }).click();
    await expectOutcome(o, "committed");
    await expect(o.getByTestId("members-list")).toContainText(who.name);
  }

  const c = await openAs(browser, controller);
  await c.getByRole("link", { name: "Protected inquiry" }).click();
  await c.getByLabel("Challenge title").fill("Why did signup conversion drop?");
  await c.getByRole("button", { name: "Create Challenge" }).click();
  await expect(c.getByRole("heading", { level: 1, name: /signup conversion/ })).toBeVisible();
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

  await o.goto(`/workspaces/${workspaceId}/sessions/${sessionId}`);
  await o.getByLabel("Grant session control to").selectOption(controller.userId);
  await o.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expectOutcome(o, "committed");

  await c.reload();
  await c.getByRole("button", { name: "Begin setup" }).click();
  await expectOutcome(c, "committed");
  await c.getByRole("button", { name: "Begin challenge capture" }).click();
  await expectOutcome(c, "committed");
  await c.getByRole("button", { name: "Prepare protected Burst" }).click();
  await expectOutcome(c, "committed");

  // Before ACTIVE nothing can be captured: no participant has a capture form yet.
  // HD-7 + HD-14: the controller admits participants, including themselves.
  for (const who of [alice, bob, controller]) {
    // A control used right after a reload can be touched before hydration; retry until React has it.
    await expect(async () => {
      await c.getByLabel("Admit participant").selectOption(who.userId);
      await expect(c.getByRole("button", { name: "Admit to Session" })).toBeEnabled({ timeout: 1000 });
    }).toPass();
    await c.getByRole("button", { name: "Admit to Session" }).click();
    await expectOutcome(c, "committed");
    await expect(c.getByTestId("participants-list")).toContainText(who.name);
    // wait for the re-read to drop the admitted member from the candidates (selection reset)
    await expect(c.getByLabel("Admit participant").locator(`option[value="${who.userId}"]`)).toHaveCount(0);
  }
  await c.getByRole("button", { name: "Open question generation" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");

  // ===== the protected Burst =====
  const a = await openAs(browser, alice);
  await a.goto(sessionUrl);
  await expect(a.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");
  await expect(a.getByTestId("burst-state")).toHaveText("ACTIVE");
  await expect(a.getByTestId("burst-mode")).toHaveText("HUMAN_ONLY");
  await expect(a.getByTestId("burst-timer")).toContainText("Elapsed");
  await expect(a.getByTestId("burst-timer")).toContainText("nothing closes it automatically");
  await expect(a.getByTestId("capture-form")).toBeVisible();
  await shot(a, "01-participant-burst-active");

  // A statement is REJECTED (HD-12): explained, nothing stored, text kept for editing.
  await a.getByLabel("Your question", { exact: true }).fill("The checkout is slow.");
  await a.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(a, "rejected");
  await expect(a.getByTestId("command-outcome")).toContainText("Nothing was stored");
  await expect(a.getByTestId("own-questions-empty")).toBeVisible();
  await expect(a.getByLabel("Your question", { exact: true })).toHaveValue("The checkout is slow.");

  // Question A: exactly as typed (leading/trailing spaces, quotes, dash, CJK, Arabic), by keyboard.
  await a.getByLabel("Your question", { exact: true }).fill(QUESTION_A);
  await a.getByLabel("Your question", { exact: true }).press("Control+Enter");
  await expectOutcome(a, "committed");
  await expect(a.getByTestId("own-question")).toHaveCount(1);
  expect(await exactText(a.getByTestId("own-question-text").first())).toBe(QUESTION_A);
  await expect(a.getByTestId("own-question").first()).toContainText("human");
  await expect(a.getByLabel("Your question", { exact: true })).toHaveValue("");

  // Question B.
  await a.getByLabel("Your question", { exact: true }).fill(QUESTION_B);
  await a.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(a, "committed");
  await expect(a.getByTestId("own-question")).toHaveCount(2);
  expect(await exactText(a.getByTestId("own-question-text").nth(1))).toBe(QUESTION_B);
  await shot(a, "02-participant-two-questions");

  // HD-13: participant Bob sees NONE of Alice's questions while the Burst is ACTIVE.
  const b = await openAs(browser, bob);
  await b.goto(sessionUrl);
  await expect(b.getByTestId("own-questions-empty")).toBeVisible();
  await expect(b.locator("body")).not.toContainText("Which segment abandons first?");
  await b.getByLabel("Your question", { exact: true }).fill(QUESTION_C);
  await b.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(b, "committed");
  expect(await exactText(b.getByTestId("own-question-text").first())).toBe(QUESTION_C);
  await expect(b.getByTestId("own-question")).toHaveCount(1);

  // HD-14: the controller (self-admitted) captures too, sees ONLY their own + a count.
  await c.reload();
  await c.getByLabel("Your question", { exact: true }).fill(QUESTION_F);
  await c.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("own-question")).toHaveCount(1);
  await expect(c.getByTestId("captured-count")).toContainText("4");
  await expect(c.locator("body")).not.toContainText("Which segment abandons first?");
  await expect(c.locator("body")).not.toContainText("only perceived");
  await shot(c, "03-controller-count-only");

  // The Owner (Workspace root, NOT a participant) has no capture affordance; the server's reason is shown.
  await o.goto(sessionUrl);
  await expect(o.getByTestId("capture-form")).toHaveCount(0);
  await expect(o.getByTestId("action-reason-CAPTURE_QUESTION")).toContainText("participant");
  await expect(o.getByTestId("captured-count")).toHaveCount(0);
  await expect(o.locator("body")).not.toContainText("Which segment abandons first?");
  await expect(o.getByRole("button", { name: /Complete Burst/ })).toHaveCount(0);
  await shot(o, "04-owner-no-capture");

  // ===== adversarial: real API calls from real sessions =====
  const burstVersion = ((await apiFromPage(a, "GET", `/workspaces/${workspaceId}/sessions/${sessionId}/position`)).body as {
    burst: { version: number };
    session: { version: number };
  });
  const captureUrl = `/workspaces/${workspaceId}/sessions/${sessionId}/burst/questions`;
  // Owner (not a participant): denied.
  const ownerCapture = await apiFromPage(o, "POST", captureUrl, {
    originalText: "Owner sneaks in?",
    expectedBurstVersion: burstVersion.burst.version,
  });
  expect(ownerCapture.body.kind).toBe("denied");
  // Client-supplied origin is REJECTED, never honoured.
  const forged = await apiFromPage(a, "POST", captureUrl, {
    originalText: "Forged origin?",
    expectedBurstVersion: burstVersion.burst.version,
    origin: "AI",
  });
  expect(forged.body).toMatchObject({ kind: "rejected" });
  // A participant cannot complete.
  const participantComplete = await apiFromPage(
    a,
    "POST",
    `/workspaces/${workspaceId}/sessions/${sessionId}/transitions/complete-burst`,
    { expectedVersion: burstVersion.session.version, expectedBurstVersion: burstVersion.burst.version },
  );
  expect(participantComplete.body.kind).toBe("denied");
  // Cross-Workspace outsider: read and write denied.
  const x = await openAs(browser, outsider);
  const crossRead = await apiFromPage(x, "GET", `/workspaces/${workspaceId}/sessions/${sessionId}/position`);
  expect(crossRead.body.kind).toBe("denied");
  const crossWrite = await apiFromPage(x, "POST", captureUrl, {
    originalText: "From outside?",
    expectedBurstVersion: burstVersion.burst.version,
  });
  expect(crossWrite.body.kind).toBe("denied");

  // A second, soon-to-be-stale view of Alice's page.
  const staleAlice = await a.context().newPage();
  await staleAlice.goto(sessionUrl);
  await expect(staleAlice.getByTestId("capture-form")).toBeVisible();

  // ===== manual, authorized completion =====
  await c.reload();
  await c.getByRole("button", { name: "Complete Burst…" }).click();
  await expect(c.getByTestId("complete-confirm")).toContainText("cannot be undone");
  await shot(c, "05-controller-confirm-complete");
  await c.getByTestId("complete-confirm-button").click();
  await expectOutcome(c, "committed");
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");
  await expect(c.getByTestId("burst-state")).toHaveText("COMPLETED");
  await expect(c.getByTestId("capture-form")).toHaveCount(0);

  // Late capture from the stale tab is blocked and nothing is stored.
  await staleAlice.getByLabel("Your question", { exact: true }).fill("Too late to matter?");
  await staleAlice.getByRole("button", { name: "Submit question" }).click();
  await expectOutcome(staleAlice, "blocked");

  // ===== the frozen human question set, visible to every member =====
  const expected = [QUESTION_A, QUESTION_B, QUESTION_C, QUESTION_F];
  for (const [page, label] of [
    [c, "controller"],
    [a, "alice"],
    [b, "bob"],
    [o, "owner"],
  ] as const) {
    await page.goto(sessionUrl);
    await expect(page.getByTestId("burst-state")).toHaveText("COMPLETED");
    await expect(page.getByTestId("frozen-set")).toBeVisible();
    await expect(page.getByTestId("frozen-marker")).toBeVisible();
    await expect(page.getByTestId("frozen-question")).toHaveCount(4);
    await expect(page.getByTestId("frozen-verified")).toContainText("Verified");
    await expect(page.getByTestId("capture-form")).toHaveCount(0);
    const texts = await page.getByTestId("frozen-question-text").evaluateAll((els) => els.map((el) => el.textContent ?? ""));
    expect(texts, `${label} sees the frozen set in capture order, exactly as typed`).toEqual(expected);
    await expect(page.getByTestId("frozen-question").first()).toContainText(alice.name);
    await expect(page.getByTestId("frozen-question").nth(2)).toContainText(bob.name);
    await expect(page.getByTestId("frozen-question").nth(3)).toContainText(controller.name);
    await expect(page.getByTestId("frozen-question").first()).toContainText("human");
    // Established-by provenance: the completion Command, BINDING at SESSION:<id>.
    const established = page.getByTestId("session-last-transition");
    await expect(established).toContainText("CMD_COMPLETE_BURST");
    await expect(established).toContainText(controller.name);
    await expect(established).toContainText("BINDING");
    await expect(established).toContainText(`SESSION:${sessionId}`);
  }
  await shot(a, "06-frozen-set-participant");
  await shot(o, "07-frozen-set-owner");

  // Once frozen, the capture API stays closed for everyone, including the controller.
  const late = await apiFromPage(a, "POST", captureUrl, { originalText: "Still late?", expectedBurstVersion: 1 });
  expect(["blocked", "stale"]).toContain(late.body.kind);
  const lateController = await apiFromPage(c, "POST", captureUrl, { originalText: "Controller late?", expectedBurstVersion: 1 });
  expect(["blocked", "stale"]).toContain(lateController.body.kind);
});
