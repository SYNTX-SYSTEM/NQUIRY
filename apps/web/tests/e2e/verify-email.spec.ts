/**
 * WU-AUTH-11 MOCKED-browser proof of the verification surfaces. `page.route()`
 * fulfils the API (20 §12).
 */
import { expect, test } from "@playwright/test";

const API = "http://localhost:8000";
const SESSION = {
  sessionId: "11111111-1111-4111-8111-111111111111",
  issuedAt: "2030-01-01T08:00:00+00:00",
  expiresAt: "2030-01-01T20:00:00+00:00",
  current: true,
  methodType: "LOCAL_PASSWORD",
};

async function accountRoutes(page: import("@playwright/test").Page, emails: unknown[]) {
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ json: { kind: "ok", sessions: [SESSION] } }));
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ json: { kind: "ok", methods: [] } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));
  await page.route(`${API}/auth/emails`, (route) => route.fulfill({ json: { kind: "ok", emails } }));
}

test("sending a verification email is reported as sent, not as verified", async ({ page }) => {
  await accountRoutes(page, []);
  const bodies: string[] = [];
  await page.route(`${API}/auth/email/verification/start`, (route) => {
    bodies.push(route.request().postData() ?? "");
    return route.fulfill({ json: { kind: "ok", challengeId: "c-1", expiresAt: "2030-01-01T00:30:00+00:00" } });
  });

  await page.goto("/account/security");
  await expect(page.getByTestId("emails-empty")).toBeVisible();
  await page.getByTestId("verify-address").fill("me@example.test");
  await page.getByTestId("verify-send").click();

  await expect(page.getByTestId("verify-notice")).toContainText("verification email was sent");
  await expect(page.getByTestId("verified-email")).toHaveCount(0);
  expect(bodies).toEqual([JSON.stringify({ email: "me@example.test" })]);
});

test("a throttled resend is shown as such", async ({ page }) => {
  await accountRoutes(page, [{ email: "me@example.test", verifiedAt: "2030-01-01T00:00:00+00:00", active: true }]);
  await page.route(`${API}/auth/email/verification/start`, (route) =>
    route.fulfill({ status: 429, json: { kind: "denied", reasonCode: "VERIFICATION_RESEND_THROTTLED" } }),
  );
  await page.goto("/account/security");
  await expect(page.getByTestId("verified-email")).toHaveText("me@example.test");
  await page.getByTestId("verify-address").fill("me@example.test");
  await page.getByTestId("verify-send").click();
  await expect(page.getByTestId("sessions-error")).toContainText("a moment ago");
});

test("the mailed link completes once with challenge id and token in the body, and the token is not rendered", async ({
  page,
}) => {
  const bodies: string[] = [];
  await page.route(`${API}/auth/email/verification/complete`, (route) => {
    bodies.push(route.request().postData() ?? "");
    return route.fulfill({ json: { kind: "ok", email: "me@example.test" } });
  });

  await page.goto("/account/verify-email?challenge=c-1&token=very-secret-token");

  await expect(page.getByTestId("verify-ok")).toContainText("me@example.test is verified");
  expect(bodies).toEqual([JSON.stringify({ challengeId: "c-1", token: "very-secret-token" })]);
  // After completion the token is neither shown nor kept in the URL / history.
  const visible = await page.evaluate(() => [document.body.innerText, window.location.href]);
  expect(visible[0]).not.toContain("very-secret-token");
  expect(visible[1]).toBe("http://localhost:13460/account/verify-email");
});

test("a denied completion and an incomplete link are told apart; no session goes to /login", async ({ page }) => {
  await page.route(`${API}/auth/email/verification/complete`, (route) =>
    route.fulfill({ status: 403, json: { kind: "denied", reasonCode: "VERIFICATION_DENIED" } }),
  );
  await page.goto("/account/verify-email?challenge=c-1&token=t");
  await expect(page.getByTestId("verify-denied")).toBeVisible();

  await page.goto("/account/verify-email?challenge=c-1");
  await expect(page.getByTestId("verify-malformed")).toBeVisible();

  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: { kind: "ok", providers: [] } }));
  await page.route(`${API}/auth/email/verification/complete`, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );
  await page.goto("/account/verify-email?challenge=c-1&token=t");
  await expect(page).toHaveURL(/\/login$/);
});
