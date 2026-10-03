/**
 * CYAN_REAL_E2E_FIELD_MOUNT_01 browser proof, REVIEW MOUNT (STATE B: NEXT_PUBLIC_FRONTEND_MOUNT=/cy-review). The CYAN
 * pages, navigation, brand asset and the auth return target live beneath /cy-review; the API contacts stay
 * http://localhost:8000/...; the root paths are not CYAN's here; the identity projection reads the same truth.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const MOUNT = "/cy-review";
const USER = "7dd6e767-1111-4111-8111-111111111111";
const LIVE = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };

async function routes(page: Page, authenticated: () => boolean): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill(authenticated() ? { json: { kind: "ok", userId: USER } } : { status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: LIVE }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [] } }));
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ json: { kind: "ok", sessions: [{ sessionId: "aaaaaaaa-1111-4111-8111-111111111111", issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: true, methodType: "LOCAL_PASSWORD" }] } }));
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ json: { kind: "ok", methods: [{ methodId: "cccccccc-1111-4111-8111-111111111111", methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: "2026-10-01T08:00:00+00:00", lastAuthenticatedAt: null, provider: null }] } }));
}

test("FALSIFIER_02/05/07/09 · the Access Field lives at /cy-review/login, its brand asset beneath the mount, the start contact at /api, no /cy-review/api", async ({ page }) => {
  await routes(page, () => false);
  const requests: string[] = [];
  page.on("request", (r) => requests.push(r.url()));
  const asset = page.waitForResponse((r) => r.url().includes("/brand/nquiry-logo"));
  await page.goto(`${MOUNT}/login`);
  await expect(page.getByTestId("login-form")).toBeVisible();
  const assetResponse = await asset;
  expect(assetResponse.url()).toMatch(/\/cy-review\/brand\/nquiry-logo(@2x)?\.png$/);
  expect(assetResponse.status()).toBe(200);
  await expect(page.getByTestId("provider-google")).toHaveAttribute("href", `${API}/auth/oidc/google/start?next=%2Fcy-review%2F`);
  expect(requests.filter((u) => u.includes("/cy-review/api/"))).toEqual([]);
  expect(requests.filter((u) => u.startsWith(`${API}/`)).every((u) => !u.includes("/cy-review"))).toBe(true);
  expect(requests.some((u) => u === `${API}/auth/providers`)).toBe(true);
});

test("FALSIFIER_03/04/16 · local login navigates inside the mount to /cy-review/workspaces; the projection reads the same truth; Logout returns inside the mount", async ({ page }) => {
  let authenticated = false;
  await routes(page, () => authenticated);
  await page.route(`${API}/auth/login`, async (route) => { authenticated = true; await route.fulfill({ json: { kind: "ok", userId: USER } }); });
  await page.route(`${API}/auth/logout`, async (route) => { authenticated = false; await route.fulfill({ json: { kind: "ok" } }); });
  await page.goto(`${MOUNT}/login`);
  await page.getByTestId("login-email").fill("person@nonproof.test");
  await page.getByTestId("login-password").fill("pw");
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(new RegExp(`${MOUNT}/workspaces$`));
  await expect(page.getByTestId("identity-user-id")).toHaveText(USER);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  // the product mark links inside the mount
  await expect(page.getByTestId("identity")).toHaveAttribute("href", `${MOUNT}/workspaces`);
  await page.getByTestId("logout-button").click();
  await expect(page).toHaveURL(new RegExp(`${MOUNT}/login$`));
});

test("FALSIFIER_04 · the root route redirect stays inside the mount (/cy-review → /cy-review/login when unauthenticated)", async ({ page }) => {
  await routes(page, () => false);
  await page.goto(`${MOUNT}`);
  await expect(page).toHaveURL(new RegExp(`${MOUNT}/login$`));
});

test("FALSIFIER_10 · the root paths are not CYAN's in the review build: /login and /workspaces are not served", async ({ page }) => {
  await routes(page, () => false);
  for (const path of ["/login", "/workspaces", "/"]) {
    const response = await page.goto(path);
    expect(response?.status(), path).toBe(404);
  }
});
