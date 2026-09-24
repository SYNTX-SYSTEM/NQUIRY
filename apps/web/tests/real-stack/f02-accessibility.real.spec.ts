/**
 * F02 REAL-STACK accessibility, keyboard and responsive proof.
 *
 * Real stack, no mocking. axe-core 4.13 (already present through
 * eslint-plugin-jsx-a11y) is injected into the real page and run against
 * the real rendered F02 surfaces. Keyboard-only: the Session controller
 * advances the Session with Tab/Enter only. Responsive: no horizontal
 * overflow at the project's viewport.
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

test("F02 surfaces: axe (serious/critical), keyboard-only control, responsive layout", async ({ browser }) => {
  const owner = provisionIdentity("A11yOwner");
  const fac = provisionIdentity("A11yFac");

  const a = await openAs(browser, owner);
  expect(await axe(a)).toEqual([]);
  await noHorizontalOverflow(a);
  await a.getByLabel("Workspace name").fill("Accessible inquiry");
  await a.getByRole("button", { name: "Create Workspace" }).click();
  await expect(a.getByRole("heading", { level: 1, name: "Accessible inquiry" })).toBeVisible();
  const workspaceId = a.url().split("/workspaces/")[1];
  await a.getByLabel("Member user id").fill(fac.userId);
  await a.getByLabel("Role").selectOption("Facilitator");
  await a.getByRole("button", { name: "Add member" }).click();
  await expect(a.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  expect(await axe(a)).toEqual([]);
  await noHorizontalOverflow(a);

  const b = await openAs(browser, fac);
  await b.goto(`/workspaces/${workspaceId}`);
  await b.getByLabel("Challenge title").fill("Keyboard-first inquiry");
  await b.getByRole("button", { name: "Create Challenge" }).click();
  await expect(b.getByRole("heading", { level: 1 })).toHaveText("Keyboard-first inquiry");
  const challengeId = b.url().split("/challenges/")[1];
  expect(await axe(b)).toEqual([]);
  await noHorizontalOverflow(b);

  await a.goto(`/workspaces/${workspaceId}/challenges/${challengeId}`);
  await a.getByLabel("Grant session control to").selectOption(fac.userId);
  await a.getByRole("button", { name: "Grant session control for this Challenge" }).click();
  await expect(a.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");

  await b.reload();
  await b.getByRole("button", { name: "Open Session" }).click();
  await expect(b.getByTestId("session-state")).toHaveText("DRAFT");
  const sessionId = b.url().split("/sessions/")[1];
  expect(await axe(b)).toEqual([]);
  await noHorizontalOverflow(b);
  // The phase list exposes the current step to assistive technology.
  await expect(b.locator('[data-testid="session-phases"] [aria-current="step"]')).toContainText("Draft");

  await a.goto(`/workspaces/${workspaceId}/sessions/${sessionId}`);
  await a.getByLabel("Grant session control to").selectOption(fac.userId);
  await a.getByRole("button", { name: "Grant session control for this Session" }).click();
  await expect(a.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");

  // Keyboard only: reach "Begin setup" with Tab and activate with Enter.
  await b.reload();
  const target = b.getByRole("button", { name: "Begin setup" });
  await expect(target).toBeVisible();
  let reached = false;
  for (let i = 0; i < 40 && !reached; i += 1) {
    await b.keyboard.press("Tab");
    reached = await target.evaluate((el) => el === document.activeElement);
  }
  expect(reached).toBe(true);
  // Visible focus indicator on the focused control.
  const outline = await target.evaluate((el) => getComputedStyle(el).outlineStyle);
  expect(outline).not.toBe("none");
  await b.keyboard.press("Enter");
  await expect(b.getByTestId("session-state")).toHaveText("SETUP");
  await expect(b.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
  expect(await axe(b)).toEqual([]);
  await noHorizontalOverflow(b);
});
