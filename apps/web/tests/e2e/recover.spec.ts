/**
 * WU-AUTH-12 MOCKED-browser proof of the recovery surfaces. `page.route()`
 * fulfils the API (20 §12).
 */
import { expect, test } from "@playwright/test";

const API = "http://localhost:8000";

test("the login page offers recovery and the request reports a sent message, never an account state", async ({
  page,
}) => {
  const bodies: string[] = [];
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));
  await page.route(`${API}/auth/recovery/start`, (route) => {
    bodies.push(route.request().postData() ?? "");
    return route.fulfill({ json: { kind: "ok" } });
  });

  await page.goto("/login");
  await page.getByTestId("login-forgot").click();
  await expect(page).toHaveURL(/\/recover$/);
  await page.getByTestId("recover-email").fill("me@example.test");
  await page.getByTestId("recover-submit").click();

  await expect(page.getByTestId("recover-sent")).toContainText("If an account can be recovered");
  expect(bodies).toEqual([JSON.stringify({ email: "me@example.test" })]);
});

test("an unavailable recovery policy is shown as such", async ({ page }) => {
  await page.route(`${API}/auth/recovery/start`, (route) =>
    route.fulfill({ status: 503, json: { kind: "unavailable", reasonCode: "RECOVERY_NOT_AVAILABLE" } }),
  );
  await page.goto("/recover");
  await page.getByTestId("recover-email").fill("me@example.test");
  await page.getByTestId("recover-submit").click();
  await expect(page.getByTestId("recover-unavailable")).toBeVisible();
});

test("the mailed link strips its material from the URL, sends it once in the body and creates no session", async ({
  page,
}) => {
  const bodies: string[] = [];
  await page.route(`${API}/auth/recovery/complete`, (route) => {
    bodies.push(route.request().postData() ?? "");
    return route.fulfill({ json: { kind: "ok" } });
  });

  await page.goto("/recover/reset?recovery=r-1&token=the-mailed-token");
  await expect(page.getByTestId("reset-password")).toBeVisible();
  await expect(page).toHaveURL(/\/recover\/reset$/);
  expect(await page.evaluate(() => window.location.search)).toBe("");
  await expect(page.getByTestId("reset-password")).not.toContainText("the-mailed-token");

  await page.getByTestId("reset-password").fill("a brand new passphrase 2030");
  await page.getByTestId("reset-confirm").fill("a brand new passphrase 2030");
  await page.getByTestId("reset-submit").click();

  await expect(page.getByTestId("reset-done")).toContainText("every existing login was ended");
  expect(bodies).toEqual([
    JSON.stringify({ recoveryId: "r-1", token: "the-mailed-token", newPassword: "a brand new passphrase 2030" }),
  ]);
  expect(await page.evaluate(() => document.cookie)).not.toContain("nquiry_session");
  await expect(page.getByTestId("reset-submit")).toHaveCount(0);
  const historyUrl = await page.evaluate(() => window.location.href);
  expect(historyUrl).not.toContain("the-mailed-token");
});

test("mismatched entries are refused locally and a denied proof is reported without detail", async ({ page }) => {
  let calls = 0;
  await page.route(`${API}/auth/recovery/complete`, (route) => {
    calls += 1;
    return route.fulfill({ status: 403, json: { kind: "denied", reasonCode: "RECOVERY_DENIED" } });
  });
  await page.goto("/recover/reset?recovery=r-1&token=t");
  await page.getByTestId("reset-password").fill("a brand new passphrase 2030");
  await page.getByTestId("reset-confirm").fill("a different passphrase 2030");
  await page.getByTestId("reset-submit").click();
  await expect(page.getByTestId("reset-password-invalid")).toBeVisible();
  expect(calls).toBe(0);

  await page.getByTestId("reset-confirm").fill("a brand new passphrase 2030");
  await page.getByTestId("reset-submit").click();
  await expect(page.getByTestId("reset-denied")).toContainText("not valid");
  expect(calls).toBe(1);
});

test("a link without its material is reported as incomplete and offers no form", async ({ page }) => {
  await page.goto("/recover/reset?recovery=r-1");
  await expect(page.getByTestId("reset-malformed")).toBeVisible();
  await expect(page.getByTestId("reset-password")).toHaveCount(0);
});
