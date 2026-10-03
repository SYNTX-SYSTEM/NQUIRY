/**
 * AUTH/CYAN-03 browser proof (mocked lane): a known `?auth=` word is presented as a boundary inside the Access core
 * while the form is idle; missing, unknown, malformed or conflicting values present nothing; the local login and the
 * provider contact stay unchanged; no success is synthesized; no overflow; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const KNOWN: ReadonlyArray<[string, string]> = [
  ["cancelled", "The provider login was cancelled. No access relation was established."],
  ["provider_unavailable", "The identity provider is unavailable right now. No access relation was established."],
  ["provider_error", "The identity provider reported an error. No access relation was established."],
  ["failed", "The provider login could not be completed. No access relation was established."],
  ["unavailable", "Signing in with this provider is not available for this account. No access relation was established."],
];

async function routes(page: Page): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: LIVE }));
}

async function expectSurfaceIntact(page: Page): Promise<void> {
  await expect(page.getByTestId("login-email")).toHaveValue("");
  await expect(page.getByTestId("login-password")).toHaveValue("");
  await expect(page.getByTestId("login-submit")).toHaveText("Log in");
  await expect(page.getByTestId("provider-google")).toBeVisible();
  await expect(page.getByTestId("provider-google")).toHaveAttribute("href", `${API}/auth/oidc/google/start?next=%2F`);
  expect(await page.getByTestId("access-core").count()).toBe(1);
  expect(await page.locator("main form").count()).toBe(1);
}

for (const [word, sentence] of KNOWN) {
  test(`?auth=${word} → the boundary inside the core, the surface unchanged, no success`, async ({ page }) => {
    await routes(page);
    await page.goto(`/login?auth=${word}`);
    const boundary = page.getByTestId("auth-boundary");
    await expect(boundary).toBeVisible();
    await expect(boundary).toHaveText(sentence);
    await expect(boundary).toHaveAttribute("data-projection", word);
    await expect(boundary).toHaveAttribute("role", "alert");
    await expect(page.getByTestId("access-core").getByTestId("auth-boundary")).toBeVisible();
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "boundary");
    await expectSurfaceIntact(page);
    await expect(page).toHaveURL(new RegExp(`/login\\?auth=${word}$`));
    expect(await page.locator("main").innerText()).not.toMatch(/success|signed in|welcome/i);
    expect(await boundary.locator("a, button, input, form").count()).toBe(0);
    const core = await page.getByTestId("access-core").boundingBox();
    const box = await boundary.boundingBox();
    expect(core && box && box.x >= core.x - 1 && box.x + box.width <= core.x + core.width + 1 && box.y + box.height <= core.y + core.height + 1).toBe(true);
    expect(await page.evaluate(() => { window.scrollTo(10000, 0); return window.scrollX; })).toBe(0);
  });
}

const nothing: ReadonlyArray<[string, string]> = [
  ["missing", "/login"],
  ["unknown word", "/login?auth=success"],
  ["link word on the auth key", "/login?auth=ok"],
  ["case variant", "/login?auth=FAILED"],
  ["malformed (script)", "/login?auth=%3Cscript%3Ealert(1)%3C%2Fscript%3E"],
  ["malformed (empty)", "/login?auth="],
  ["duplicate", "/login?auth=failed&auth=failed"],
  ["conflicting", "/login?auth=failed&auth=cancelled"],
];
for (const [name, url] of nothing) {
  test(`${name} → nothing presented; core current; surface unchanged`, async ({ page }) => {
    await routes(page);
    await page.goto(url);
    await expect(page.getByTestId("provider-google")).toBeVisible();
    await expect(page.getByTestId("auth-boundary")).toHaveCount(0);
    await expect(page.getByTestId("login-error")).toHaveCount(0);
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "current");
    await expectSurfaceIntact(page);
  });
}

test("a local login request replaces the provider boundary: pending while held, then the local verdict, never two boundaries", async ({ page }) => {
  await routes(page);
  let release: (() => void) | null = null;
  await page.route(`${API}/auth/login`, async (route) => {
    await new Promise<void>((resolve) => { release = resolve; });
    await route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "INVALID_CREDENTIALS" } });
  });
  await page.goto("/login?auth=failed");
  await expect(page.getByTestId("auth-boundary")).toBeVisible();
  await page.getByTestId("login-email").fill("owner@nonproof.test");
  await page.getByTestId("login-password").fill("wrong");
  await page.getByTestId("login-submit").click();
  await expect(page.getByTestId("login-pending")).toBeVisible();
  await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "loading");
  await expect(page.getByTestId("auth-boundary")).toHaveCount(0);
  await expect.poll(() => release !== null).toBe(true);
  release!();
  await expect(page.getByTestId("login-error")).toBeVisible();
  await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "boundary");
  await expect(page.getByTestId("auth-boundary")).toHaveCount(0);
  await expect(page.getByTestId("provider-google")).toBeVisible();
  await expect(page).toHaveURL(/\/login\?auth=failed$/);
});

test("the boundary does not depend on provider discovery: with no provider contact it is still presented", async ({ page }) => {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));
  await page.goto("/login?auth=cancelled");
  await expect(page.getByTestId("auth-boundary")).toHaveText(KNOWN[0][1]);
  await expect(page.getByTestId("provider-contact")).toHaveCount(0);
  await expect(page.getByTestId("login-submit")).toBeVisible();
});
