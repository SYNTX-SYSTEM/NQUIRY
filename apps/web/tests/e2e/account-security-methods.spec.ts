/**
 * WU-AUTH-10 MOCKED-browser proof of the methods / linking surface on
 * `/account/security`. `page.route()` fulfils the API (20 §12).
 */
import { expect, test } from "@playwright/test";

const SESSIONS_ROUTE = "http://localhost:8000/auth/sessions";
const METHODS_ROUTE = "http://localhost:8000/auth/methods";
const PROVIDERS_ROUTE = "http://localhost:8000/auth/providers";

const SESSION = {
  sessionId: "11111111-1111-4111-8111-111111111111",
  issuedAt: "2030-01-01T08:00:00+00:00",
  expiresAt: "2030-01-01T20:00:00+00:00",
  current: true,
  methodType: "LOCAL_PASSWORD",
};
const LOCAL = {
  methodId: "aaaaaaaa-1111-4111-8111-111111111111",
  methodType: "LOCAL_PASSWORD",
  status: "ACTIVE",
  createdAt: "2030-01-01T00:00:00+00:00",
  lastAuthenticatedAt: null,
  provider: null,
};
const LINKED = {
  ...LOCAL,
  methodId: "bbbbbbbb-2222-4222-8222-222222222222",
  methodType: "TEST_PROVIDER",
  provider: { providerId: "test", email: "p@example.test" },
};
const TEST_PROVIDER = { providerId: "test", label: "Test provider", proofClass: "TEST_PROVIDER" };

test("methods are listed and an unlinked configured provider gets a link action posting to the API", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [SESSION] } }));
  await page.route(METHODS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", methods: [LOCAL] } }));
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [TEST_PROVIDER] } }));

  await page.goto("/account/security");

  await expect(page.getByTestId("method-item")).toHaveCount(1);
  await expect(page.getByTestId("method-item").first()).toContainText("Email and password");
  const link = page.getByTestId("link-test");
  await expect(link).toBeVisible();
  await expect(link).toContainText("TEST_PROVIDER");
  const form = link.locator("xpath=ancestor::form");
  await expect(form).toHaveAttribute("method", "post");
  await expect(form).toHaveAttribute("action", /\/auth\/oidc\/test\/link\/start\?next=%2Faccount%2Fsecurity$/);
});

test("a linked provider is shown with its provider email and gets no second link action", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [SESSION] } }));
  await page.route(METHODS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", methods: [LOCAL, LINKED] } }));
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [TEST_PROVIDER] } }));

  await page.goto("/account/security");

  await expect(page.getByTestId("method-item")).toHaveCount(2);
  await expect(page.getByTestId("method-list")).toContainText("p@example.test");
  await expect(page.getByTestId("link-actions")).toHaveCount(0);
});

test("a link projection is shown as a safe message and never as the raw code", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [SESSION] } }));
  await page.route(METHODS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", methods: [LOCAL] } }));
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));

  await page.goto("/account/security?link=collision");
  await expect(page.getByTestId("link-projection")).toContainText("another account");

  await page.goto("/account/security?link=%3Cb%3Ex%3C%2Fb%3E");
  await expect(page.getByTestId("link-projection")).toContainText("could not be linked");
  expect(await page.content()).not.toContain("<b>x</b>");
});

test("an unknown method list is stated, not shown as empty", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [SESSION] } }));
  await page.route(METHODS_ROUTE, (route) => route.abort());
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [TEST_PROVIDER] } }));

  await page.goto("/account/security");

  await expect(page.getByTestId("methods-unknown")).toBeVisible();
  await expect(page.getByTestId("link-actions")).toHaveCount(0);
});
