/**
 * WU-AUTH-07 MOCKED-browser proof of the provider contacts on the login page.
 * `page.route()` fulfils the API: component/contract proof only (20 §12).
 */
import { expect, test } from "@playwright/test";

const PROVIDERS_ROUTE = "http://localhost:8000/auth/providers";
const ME_ROUTE = "http://localhost:8000/auth/me";

test("no configured provider means no provider button", async ({ page }) => {
  await page.route(ME_ROUTE, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));

  await page.goto("/login");

  await expect(page.getByTestId("login-form")).toBeVisible();
  await expect(page.getByTestId("provider-logins")).toHaveCount(0);
});

test("a configured provider is offered as a navigation to the API start contact, labelled by proof class", async ({
  page,
}) => {
  await page.route(PROVIDERS_ROUTE, (route) =>
    route.fulfill({ json: { kind: "ok", providers: [{ providerId: "test", label: "Test provider", proofClass: "TEST_PROVIDER" }] } }),
  );

  await page.goto("/login");

  const button = page.getByTestId("provider-test");
  await expect(button).toBeVisible();
  await expect(button).toContainText("TEST_PROVIDER");
  await expect(button).toHaveAttribute("href", /http:\/\/localhost:8000\/auth\/oidc\/test\/start\?next=%2F$/);
});

test("a callback projection is shown as a safe message and the code is not rendered", async ({ page }) => {
  await page.route(PROVIDERS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));

  await page.goto("/login?auth=cancelled");
  await expect(page.getByTestId("auth-projection")).toContainText("cancelled the provider login");

  await page.goto("/login?auth=%3Cscript%3Ealert(1)%3C%2Fscript%3E");
  await expect(page.getByTestId("auth-projection")).toContainText("could not be completed");
  expect(await page.content()).not.toContain("<script>alert(1)</script>");
});

test("an unreachable provider list leaves the password form usable", async ({ page }) => {
  await page.route(PROVIDERS_ROUTE, (route) => route.abort());
  await page.goto("/login");
  await expect(page.getByTestId("login-form")).toBeVisible();
  await expect(page.getByTestId("login-submit")).toBeEnabled();
});
