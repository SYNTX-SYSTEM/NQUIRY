/**
 * F03 REAL-STACK accessibility, keyboard and responsive proof for the
 * protected Burst surface. Real stack, no mocking. axe-core is injected into
 * the real rendered pages: participant with an open Burst, controller with the
 * completion confirmation, and the frozen set. Keyboard-only capture and
 * completion. No horizontal overflow at the project's viewport.
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

async function tabTo(page: Page, target: ReturnType<Page["getByRole"]>): Promise<void> {
  await expect(target).toBeVisible();
  let reached = false;
  for (let i = 0; i < 80 && !reached; i += 1) {
    await page.keyboard.press("Tab");
    reached = await target.evaluate((el) => el === document.activeElement);
  }
  expect(reached, "reachable with the keyboard alone").toBe(true);
  const outline = await target.evaluate((el) => getComputedStyle(el).outlineStyle);
  expect(outline).not.toBe("none");
}

test("F03 surfaces: axe, keyboard-only capture and completion, responsive layout", async ({ browser }) => {
  const owner = provisionIdentity("A11yOwner");
  const ctl = provisionIdentity("A11yCtl");
  const pat = provisionIdentity("A11yPat");

  const o = await openAs(browser, owner);
  await o.getByLabel("Workspace name").fill("Accessible protected inquiry");
  await o.getByRole("button", { name: "Create Workspace" }).click();
  await expect(o.getByRole("heading", { level: 1, name: "Accessible protected inquiry" })).toBeVisible();
  const workspaceId = o.url().split("/workspaces/")[1];
  for (const [who, role] of [
    [ctl, "Facilitator"],
    [pat, "Contributor"],
  ] as const) {
    await o.getByLabel("Member user id").fill(who.userId);
    await o.getByLabel("Role").selectOption(role);
    await o.getByRole("button", { name: "Add member" }).click();
    await expect(o.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  }

  const c = await openAs(browser, ctl);
  await c.goto(`/workspaces/${workspaceId}`);
  await c.getByLabel("Challenge title").fill("Keyboard-first protected inquiry");
  await c.getByRole("button", { name: "Create Challenge" }).click();
  await expect(c.getByRole("heading", { level: 1 })).toHaveText("Keyboard-first protected inquiry");
  const challengeId = c.url().split("/challenges/")[1];
  await o.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await o.getByLabel("Grant session control to").selectOption(ctl.userId);
  await o.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await expect(o.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  await c.reload();
  await c.getByRole("button", { name: "Open Session" }).click();
  await expect(c.getByTestId("session-state")).toHaveText("DRAFT");
  const sessionId = c.url().split("/sessions/")[1];
  const sessionUrl = c.url();
  await o.goto(`/workspaces/${workspaceId}/sessions/${sessionId}`);
  await o.getByLabel("Grant session control to").selectOption(ctl.userId);
  await o.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expect(o.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  await c.reload();
  for (const name of ["Begin setup", "Begin challenge capture", "Prepare protected Burst"]) {
    await c.getByRole("button", { name }).click();
    await expect(c.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  }
  await expect(async () => {
    await c.getByLabel("Admit participant").selectOption(pat.userId);
    await expect(c.getByRole("button", { name: "Admit to Session" })).toBeEnabled({ timeout: 1000 });
  }).toPass();
  await c.getByRole("button", { name: "Admit to Session" }).click();
  await expect(c.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  await c.getByRole("button", { name: "Open question generation" }).click();
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_GENERATION");

  // Participant: axe on the open Burst, keyboard-only capture.
  const p = await openAs(browser, pat);
  await p.goto(sessionUrl);
  await expect(p.getByTestId("capture-form")).toBeVisible();
  expect(await axe(p)).toEqual([]);
  await noHorizontalOverflow(p);
  const field = p.getByLabel("Your question", { exact: true });
  await tabTo(p, p.getByRole("textbox", { name: "Your question" }));
  await p.keyboard.type("Can a keyboard alone submit this?");
  await p.keyboard.press("Control+Enter");
  await expect(p.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  await expect(p.getByTestId("own-question")).toHaveCount(1);
  // Rejection is announced (role=alert) and explained.
  await field.fill("Not a question");
  await p.getByRole("button", { name: "Submit question" }).click();
  await expect(p.getByTestId("command-outcome")).toHaveAttribute("role", "alert");
  await expect(p.getByTestId("command-outcome")).toContainText("Nothing was stored");
  expect(await axe(p)).toEqual([]);
  await noHorizontalOverflow(p);

  // Controller: keyboard-only completion through the explicit confirmation.
  await c.reload();
  const complete = c.getByRole("button", { name: /Complete Burst/ });
  await tabTo(c, complete);
  await c.keyboard.press("Enter");
  const confirm = c.getByTestId("complete-confirm");
  await expect(confirm).toBeVisible();
  expect(await axe(c)).toEqual([]);
  await noHorizontalOverflow(c);
  const freeze = c.getByRole("button", { name: /Freeze the set/ });
  await tabTo(c, freeze);
  await c.keyboard.press("Enter");
  await expect(c.getByTestId("session-state")).toHaveText("QUESTION_CAPTURE");

  // Frozen set: axe + no overflow for controller and participant.
  await expect(c.getByTestId("frozen-set")).toBeVisible();
  expect(await axe(c)).toEqual([]);
  await noHorizontalOverflow(c);
  await p.goto(sessionUrl);
  await expect(p.getByTestId("frozen-set")).toBeVisible();
  expect(await axe(p)).toEqual([]);
  await noHorizontalOverflow(p);
});
