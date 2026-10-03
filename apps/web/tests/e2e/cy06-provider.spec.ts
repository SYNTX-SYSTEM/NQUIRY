/**
 * AUTH/CYAN-02 browser proof (mocked lane): the Google provider contact is part of the existing Access core and
 * exists only when the server's parsed provider answer names it; malformed, unknown, unavailable, empty or failed
 * discovery shows nothing; the local-password login is unchanged; the contact is a GET navigation to the typed
 * LOGIN start URL and nothing else (no link route, no POST); no overflow, no second login surface; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const START = `${API}/auth/oidc/google/start?next=%2F`;

async function noSession(page: Page): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
}

async function expectLocalLoginIntact(page: Page): Promise<void> {
  await expect(page.getByTestId("login-email")).toBeVisible();
  await expect(page.getByTestId("login-password")).toBeVisible();
  await expect(page.getByTestId("login-submit")).toBeVisible();
  await expect(page.getByTestId("login-email")).toHaveValue("");
  await expect(page.getByTestId("login-password")).toHaveValue("");
  await expect(page.getByTestId("login-submit")).toHaveText("Log in");
}

test("the contact appears from the live-shaped provider truth, inside the core, as one GET navigation to the typed start URL", async ({ page }) => {
  await noSession(page);
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: LIVE }));
  await page.goto("/login");
  const contact = page.getByTestId("provider-google");
  await expect(contact).toBeVisible();
  await expect(contact).toHaveText("Continue with Google");
  await expect(contact).toHaveAttribute("href", START);
  await expect(contact).toHaveAttribute("data-proof-class", "PRODUCTION_PROVIDER");
  await expect(page.getByTestId("access-core").getByTestId("provider-contact")).toBeVisible();
  await expectLocalLoginIntact(page);
  // one access core, one form, one provider navigation; no second login surface, no panel, no new route
  expect(await page.getByTestId("access-core").count()).toBe(1);
  expect(await page.locator("main form").count()).toBe(1);
  expect(await page.locator("main a[href*='/auth/oidc/']").count()).toBe(1);
  expect(await page.locator("main a[href*='/link/']").count()).toBe(0);
  await expect(page).toHaveURL(/\/login$/);
  // no overflow: the contact lies within the core, the core within the viewport, and the page cannot be scrolled
  // sideways (the fixed ambient background is clipped and pointer-inert; it is measured by the SF lanes, not here)
  const core = await page.getByTestId("access-core").boundingBox();
  const box = await contact.boundingBox();
  expect(core && box && box.x >= core.x - 1 && box.x + box.width <= core.x + core.width + 1 && box.y + box.height <= core.y + core.height + 1).toBe(true);
  const viewport = page.viewportSize();
  expect(core && viewport && core.x >= 0 && core.x + core.width <= viewport.width).toBe(true);
  expect(await page.evaluate(() => { window.scrollTo(10000, 0); return window.scrollX; })).toBe(0);
});

test("activating the contact navigates by GET to the LOGIN start route, never POST, never the link route", async ({ page }) => {
  await noSession(page);
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: LIVE }));
  const requests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/auth/oidc/")) requests.push(`${request.method()} ${request.url()}`);
  });
  await page.route(`${API}/auth/oidc/**`, (route) => route.fulfill({ status: 200, contentType: "text/plain", body: "provider boundary (mocked lane: no real provider is contacted)" }));
  await page.goto("/login");
  await page.getByTestId("provider-google").click();
  await expect.poll(() => requests.length).toBe(1);
  expect(requests[0]).toBe(`GET ${START}`);
  expect(requests.some((r) => r.startsWith("POST") || r.includes("/link/"))).toBe(false);
});

const closed: ReadonlyArray<[string, (route: Parameters<Parameters<Page["route"]>[1]>[0]) => Promise<void>]> = [
  ["malformed (unknown proofClass)", (route) => route.fulfill({ json: { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PROVEN" }] } })],
  ["malformed (extra availability field)", (route) => route.fulfill({ json: { kind: "ok", providers: [], googleAvailable: true } })],
  ["unknown kind", (route) => route.fulfill({ json: { kind: "providers", providers: LIVE.providers } })],
  ["denied", (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } })],
  ["unavailable", (route) => route.fulfill({ status: 503, json: { kind: "unavailable", reasonCode: "PROVIDER_NOT_CONFIGURED" } })],
  ["empty list", (route) => route.fulfill({ json: { kind: "ok", providers: [] } })],
  ["non-JSON 502", (route) => route.fulfill({ status: 502, contentType: "text/html", body: "<html>bad gateway</html>" })],
  ["network failure", (route) => route.abort("connectionrefused")],
];
for (const [name, handler] of closed) {
  test(`${name} → no provider contact; the local login is unchanged`, async ({ page }) => {
    await noSession(page);
    await page.route(`${API}/auth/providers`, handler);
    const requested = page.waitForRequest(`${API}/auth/providers`);
    await page.goto("/login");
    await requested;
    await expectLocalLoginIntact(page);
    await expect(page.getByTestId("provider-contact")).toHaveCount(0);
    expect(await page.locator("main a[href*='/auth/oidc/']").count()).toBe(0);
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "current");
  });
}

test("the local-password login still works with the contact present (a denied verdict stays a boundary; the contact stays)", async ({ page }) => {
  await noSession(page);
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: LIVE }));
  await page.route(`${API}/auth/login`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "INVALID_CREDENTIALS" } }));
  await page.goto("/login");
  await expect(page.getByTestId("provider-google")).toBeVisible();
  await page.getByTestId("login-email").fill("owner@nonproof.test");
  await page.getByTestId("login-password").fill("wrong");
  await page.getByTestId("login-submit").click();
  await expect(page.getByTestId("login-error")).toBeVisible();
  await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "boundary");
  await expect(page.getByTestId("provider-google")).toBeVisible();
  await expect(page).toHaveURL(/\/login$/);
});
