/**
 * SF-01 REAL-STACK proof (L7), PREPARED. It counts as proof only when run in
 * the ISOLATED SF-01 environment (`scripts/run_sf01_real_stack.sh`, compose
 * project `nquiry-sf01`), never against another Field's running stack
 * (SF-01 human decision 2).
 *
 * Real browser → real Next.js (this tree) → real FastAPI → real PostgreSQL.
 * No network interception of any kind (global-setup enforces it). Transport
 * loss is produced by the browser's own offline mode, so the request
 * genuinely never gets an answer.
 *
 * Proves on the pre-Session surfaces (Workspaces, Workspace, Challenge):
 * - the Relation Trace is rebuilt identically from canonical reads after a reload;
 * - no Session coordinate exists before CreateSession commits, and the Session
 *   relation turns from unavailable to possible only through a real grant;
 * - commit markers claim a re-read only after it happened;
 * - transport loss → unknown consequence; the view is marked last confirmed;
 *   a manual re-read restores it; repeating the same intent yields exactly ONE effect;
 * - authority proof is depth (closed by default, keyboard-openable);
 * - axe (serious/critical) = 0, no horizontal overflow, reduced motion keeps meaning.
 */
import { createRequire } from "node:module";
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

const require = createRequire(import.meta.url);
const AXE_PATH = require.resolve("axe-core/axe.min.js");

async function openAs(browser: Browser, who: DevIdentity): Promise<Page> {
  const page = await (await browser.newContext()).newPage();
  await page.goto("/login");
  await page.getByLabel("Email").fill(who.email);
  await page.getByLabel("Password").fill(who.password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/workspaces/);
  return page;
}

async function axe(page: Page): Promise<string[]> {
  await page.addScriptTag({ path: AXE_PATH });
  return page.evaluate(async () => {
    // @ts-expect-error axe is injected at runtime
    const result = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] } });
    return (result.violations as { id: string; impact: string; nodes: unknown[] }[])
      .filter((v) => v.impact === "serious" || v.impact === "critical")
      .map((v) => `${v.id} (${v.impact}, ${v.nodes.length} nodes)`);
  });
}

async function noHorizontalOverflow(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
}

async function shot(page: Page, name: string): Promise<void> {
  const project = test.info().project.name;
  await page.screenshot({ path: `test-results/sf01-visual/${project}-${name}.png`, fullPage: true });
}

const trace = (page: Page) => page.getByRole("navigation", { name: "Inquiry position" });
const outcome = (page: Page) => page.getByTestId("command-outcome");

/** The trace as data: [coordinate, status, label] per segment. */
async function traceOf(page: Page): Promise<string[][]> {
  return trace(page)
    .getByRole("listitem")
    .evaluateAll((items) =>
      items.map((li) => [
        li.getAttribute("data-coordinate") ?? "",
        li.getAttribute("data-status") ?? "",
        (li.querySelector("a, .trace-label")?.textContent ?? "").trim(),
      ]),
    );
}

async function committedAndReread(page: Page): Promise<void> {
  await expect(outcome(page)).toHaveAttribute("data-outcome", "committed");
  await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
  await expect(outcome(page)).toContainText("The state shown was re-read from the canonical source.");
}

test("SF-01: relational position, effect lifecycle and proof depth on the real pre-Session path", async ({ browser }) => {
  const owner = provisionIdentity("Sf01Owner");
  const fac = provisionIdentity("Sf01Fac");
  const wsName = `Relational inquiry ${Date.now().toString(36)}`;

  // --- access context --------------------------------------------------------
  const a = await openAs(browser, owner);
  expect(await traceOf(a)).toEqual([["access", "current", "Workspaces"]]);
  expect(await axe(a)).toEqual([]);
  await noHorizontalOverflow(a);
  await shot(a, "01-access");

  // --- founding: the Workspace becomes the current coordinate ------------------
  await a.getByLabel("Workspace name").fill(wsName);
  await a.getByRole("button", { name: "Create Workspace" }).click();
  await expect(a.getByRole("heading", { level: 1, name: wsName })).toBeVisible();
  const workspaceId = new URL(a.url()).pathname.split("/")[2];
  // Owner is not a Facilitator: the Challenge relation is visible but unavailable (server reason).
  await expect(trace(a).locator('[data-coordinate="challenge"]')).toHaveAttribute("data-status", "unavailable");
  const ownerWorkspaceTrace = await traceOf(a);
  await a.reload();
  await expect(a.getByRole("heading", { level: 1, name: wsName })).toBeVisible();
  await expect(trace(a).locator('[data-coordinate="challenge"]')).toHaveAttribute("data-status", "unavailable");
  expect(await traceOf(a)).toEqual(ownerWorkspaceTrace);
  expect(await axe(a)).toEqual([]);
  await noHorizontalOverflow(a);
  await shot(a, "02-workspace-owner");

  // --- add a Facilitator: commit marker only after the canonical re-read -------
  await a.getByLabel("Member user id").fill(fac.userId);
  await a.getByLabel("Role").selectOption("Facilitator");
  await a.getByRole("button", { name: "Add member" }).click();
  await committedAndReread(a);
  await expect(a.getByTestId("members-list")).toContainText(fac.name);

  // --- Facilitator frames a Challenge: Session is a relation, not a place ------
  const b = await openAs(browser, fac);
  await b.goto(`/workspaces/${workspaceId}`);
  await expect(trace(b).locator('[data-coordinate="challenge"]')).toHaveAttribute("data-status", "possible");
  await b.getByLabel("Challenge title").fill("Why did activation stall?");
  await b.getByRole("button", { name: "Create Challenge" }).click();
  await expect(b.getByRole("heading", { level: 1 })).toHaveText("Why did activation stall?");
  const challengeUrl = new URL(b.url()).pathname;
  expect(await traceOf(b)).toEqual([
    ["access", "established", "Workspaces"],
    ["workspace", "established", wsName],
    ["challenge", "current", "Why did activation stall?"],
    ["session", "unavailable", "New Session"],
  ]);
  await expect(trace(b).locator('[data-coordinate="session-state"]')).toHaveCount(0);
  await expect(b.getByTestId("session-create-unavailable")).toContainText("SESSION_CONTROL_RIGHT");
  expect(await axe(b)).toEqual([]);
  await noHorizontalOverflow(b);
  await shot(b, "03-challenge-session-unavailable");

  // --- governance root: authority proof is depth; the grant is re-read ---------
  await a.goto(challengeUrl);
  const proof = a.getByTestId("challenge-authority-proof");
  await expect(a.getByTestId("challenge-authority-empty")).toBeHidden();
  await proof.locator("summary").focus();
  await a.keyboard.press("Enter");
  await expect(a.getByTestId("challenge-authority-empty")).toBeVisible();
  await a.getByLabel("Grant session control to").selectOption(fac.userId);
  await a.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await committedAndReread(a);
  await expect(a.getByTestId("challenge-authority-list")).toContainText(fac.name);
  expect(await axe(a)).toEqual([]);
  await shot(a, "04-challenge-authority-proof-open");

  // --- the Session relation becomes possible only through that real grant ------
  await b.reload();
  await expect(trace(b).locator('[data-coordinate="session"]')).toHaveAttribute("data-status", "possible");
  await b.getByRole("button", { name: "Open Session" }).click();
  await expect(b).toHaveURL(/\/sessions\/[0-9a-f-]{36}$/);
  await expect(b.getByTestId("session-state")).toHaveText("DRAFT");
  await b.goto(challengeUrl);
  await expect(b.getByTestId("sessions-list").getByRole("link")).toContainText("Session opened");
  await expect(b.getByTestId("sessions-list")).not.toContainText("Session 1");
  await expect(b.getByTestId("sessions-list").locator('[data-origin="system-state"]')).toContainText("DRAFT");

  // --- transport loss: unknown consequence, last confirmed view, one effect only
  await b.goto(`/workspaces/${workspaceId}`);
  await expect(b.getByTestId("challenges-list")).toBeVisible();
  await b.context().setOffline(true);
  await b.getByLabel("Challenge title").fill("Offline attempt");
  await b.getByRole("button", { name: "Create Challenge" }).click();
  await expect(outcome(b)).toHaveAttribute("data-outcome", "network_failure");
  await expect(outcome(b)).toHaveAttribute("data-consequence", "unknown");
  await expect(outcome(b)).toHaveAttribute("data-reconstruction", "failed");
  await expect(outcome(b)).not.toContainText(/nothing (is assumed to have )?changed|no change was made/i);
  await expect(b.getByTestId("projection-last-confirmed")).toBeVisible();
  await expect(b.getByRole("button", { name: "Create Challenge" })).toBeDisabled();
  await shot(b, "05-unknown-consequence-last-confirmed");
  await b.context().setOffline(false);
  await b.getByRole("button", { name: "Re-read current state" }).click();
  await expect(outcome(b)).toHaveAttribute("data-reconstruction", "done");
  await expect(b.getByTestId("projection-last-confirmed")).toHaveCount(0);
  // Repeat of the same intent (same Idempotency-Key, retained) → exactly one Challenge.
  await b.getByRole("button", { name: "Create Challenge" }).click();
  await expect(b.getByRole("heading", { level: 1 })).toHaveText("Offline attempt");
  await b.goto(`/workspaces/${workspaceId}`);
  await expect(b.getByTestId("challenges-list").getByRole("link", { name: "Offline attempt", exact: true })).toHaveCount(1);
});

test("SF-01: reduced motion keeps every effect meaning", async ({ browser }) => {
  const owner = provisionIdentity("Sf01Motion");
  const a = await openAs(browser, owner);
  await a.emulateMedia({ reducedMotion: "reduce" });
  await a.getByLabel("Workspace name").fill(`Motion ${Date.now().toString(36)}`);
  await a.getByRole("button", { name: "Create Workspace" }).click();
  await expect(a.getByRole("heading", { level: 1 })).toBeVisible();
  await a.getByLabel("Member user id").fill("not-a-uuid");
  await a.getByRole("button", { name: "Add member" }).click();
  // Malformed input is REJECTED by the server (F02 WU-02.12): a boundary, announced, with no effect.
  await expect(outcome(a)).toHaveAttribute("data-outcome", "rejected");
  await expect(outcome(a)).toHaveAttribute("data-consequence", "none");
  await expect(outcome(a)).toHaveAttribute("role", "alert");
  expect(await outcome(a).evaluate((el) => getComputedStyle(el).animationName)).toBe("none");
});
