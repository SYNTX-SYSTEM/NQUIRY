/**
 * CYAN-ENTRY-01 browser law (mocked lane): the entry path of a person without an identity lives inside the Access
 * core below the contacts, as words only; its provider sentences exist only when the server listed a provider and
 * carry the server's labels; the operator sentence always; the `?auth=unavailable` boundary and the entry coexist;
 * no control; the surface unchanged; no sideways scroll; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const TWO = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }, { providerId: "acme", label: "Acme ID", proofClass: "TEST_PROVIDER" }] };

async function routes(page: Page, providers: unknown | null): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/contacts`, (route) => route.fulfill({ json: { kind: "ok", recovery: "UNAVAILABLE", emailVerification: "UNAVAILABLE" } }));
  await page.route(`${API}/auth/providers`, (route) => (providers === null ? route.fulfill({ status: 500, body: "boom" }) : route.fulfill({ json: providers })));
}

async function expectInsideCoreNoControl(page: Page): Promise<void> {
  const entry = page.getByTestId("access-entry");
  await expect(page.getByTestId("access-core").getByTestId("access-entry")).toBeVisible();
  expect(await entry.locator("a, button, input, form").count()).toBe(0);
  const core = await page.getByTestId("access-core").boundingBox();
  const box = await entry.boundingBox();
  expect(core && box && box.x >= core.x - 1 && box.x + box.width <= core.x + core.width + 1 && box.y + box.height <= core.y + core.height + 1).toBe(true);
  expect(await page.evaluate(() => { window.scrollTo(10000, 0); return window.scrollX; })).toBe(0);
  // below the contacts, above nothing that logs in: the entry follows the provider contact when one exists
  expect(await page.locator("main form").count()).toBe(1);
  await expect(page.getByTestId("login-submit")).toHaveText("Log in");
}

test("one listed provider → provider entry named by the server's label, the operator entry, LINK != LOGIN; words only", async ({ page }) => {
  await routes(page, LIVE);
  await page.goto("/login");
  await expect(page.getByTestId("provider-google")).toBeVisible();
  const entry = page.getByTestId("access-entry");
  await expect(entry).toHaveAttribute("data-providers", "1");
  await expect(entry.getByTestId("entry-provider")).toContainText("Continue with Google:");
  await expect(entry.getByTestId("entry-provider")).toContainText("decided by the server when you continue");
  await expect(entry.getByTestId("entry-operator")).toContainText("created by the operator of this deployment");
  await expect(entry.getByTestId("entry-link")).toContainText("add Google under Access security");
  await expect(entry.getByTestId("entry-link")).toContainText("does not attach it to an existing account");
  const contact = await page.getByTestId("provider-contact").boundingBox();
  const box = await entry.boundingBox();
  expect(contact && box && box.y >= contact.y + contact.height - 1).toBe(true);
  await expectInsideCoreNoControl(page);
  expect(await page.locator("main").innerText()).not.toMatch(/sign up|register now|create (an )?account|success|welcome/i);
});

test("two listed providers → both labels as the server gave them", async ({ page }) => {
  await routes(page, TWO);
  await page.goto("/login");
  const entry = page.getByTestId("access-entry");
  await expect(entry).toHaveAttribute("data-providers", "2");
  await expect(entry.getByTestId("entry-provider")).toContainText("Continue with Google or Acme ID:");
  await expect(page.getByTestId("provider-acme")).toContainText("test provider");
  await expectInsideCoreNoControl(page);
});

for (const [name, providers] of [["empty list", { kind: "ok", providers: [] }], ["failed discovery", null]] as const) {
  test(`${name} → the operator entry only; no provider named; no link sentence`, async ({ page }) => {
    await routes(page, providers);
    await page.goto("/login");
    await expect(page.getByTestId("login-submit")).toBeVisible();
    const entry = page.getByTestId("access-entry");
    await expect(entry).toBeVisible();
    await expect(entry).toHaveAttribute("data-providers", "0");
    await expect(entry.getByTestId("entry-operator")).toBeVisible();
    expect(await entry.getByTestId("entry-provider").count()).toBe(0);
    expect(await entry.getByTestId("entry-link").count()).toBe(0);
    expect(await entry.innerText()).not.toMatch(/google/i);
    expect(await page.getByTestId("provider-contact").count()).toBe(0);
    await expectInsideCoreNoControl(page);
  });
}

test("?auth=unavailable → the server's refusal and the entry coexist; the refusal sentence unchanged; no success", async ({ page }) => {
  await routes(page, LIVE);
  await page.goto("/login?auth=unavailable");
  const boundary = page.getByTestId("auth-boundary");
  await expect(boundary).toHaveText("Signing in with this provider is not available for this account. No access relation was established.");
  await expect(page.getByTestId("access-entry").getByTestId("entry-link")).toContainText("add Google under Access security");
  await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "boundary");
  await expectInsideCoreNoControl(page);
  expect(await page.locator("main").innerText()).not.toMatch(/success|signed in|welcome/i);
});
