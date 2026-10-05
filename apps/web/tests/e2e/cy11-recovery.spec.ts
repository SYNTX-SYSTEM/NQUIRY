/**
 * AUTH/CYAN-RECOVERY-01 browser proof (mocked lane): the recovery and e-mail verification contacts of the product —
 * offered only when `/auth/contacts` says so; the one answer at /recover; the mail link captured once and removed
 * from the address bar on /recover/reset and /account/verify-email; the server's verdicts; the chamber's
 * verification relation and its Send control; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const USER = "7dd6e767-1111-4111-8111-111111111111";
const S_CUR = "aaaaaaaa-1111-4111-8111-111111111111";
const CHALLENGE = "3a0a0a0a-1111-4111-8111-111111111111";
const RECOVERY = "4b0b0b0b-1111-4111-8111-111111111111";
const CONTACTS_ON = { kind: "ok", recovery: "AVAILABLE", emailVerification: "AVAILABLE" };
const CONTACTS_OFF = { kind: "ok", recovery: "UNAVAILABLE", emailVerification: "UNAVAILABLE" };
const PROVIDERS = { kind: "ok", providers: [] };
const IDENTITY = { kind: "ok", userId: USER, displayName: "tobi", canonicalEmail: "tobias@thescaleforge.com" };
const LOCAL = { methodId: "cccccccc-1111-4111-8111-111111111111", methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: "2026-10-01T08:00:00+00:00", lastAuthenticatedAt: "2026-10-01T08:00:00+00:00", provider: null };

async function noSession(page: Page, contacts: unknown = CONTACTS_ON): Promise<void> {
  await page.route(`${API}/auth/me`, (r) => r.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (r) => r.fulfill({ json: PROVIDERS }));
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ json: contacts }));
}

async function session(page: Page, emails: unknown[], contacts: unknown = CONTACTS_ON): Promise<{ sent: unknown[] }> {
  const w = { sent: [] as unknown[] };
  await page.route(`${API}/auth/me`, (r) => r.fulfill({ json: { kind: "ok", userId: USER } }));
  await page.route(`${API}/auth/identity`, (r) => r.fulfill({ json: IDENTITY }));
  await page.route(`${API}/auth/providers`, (r) => r.fulfill({ json: PROVIDERS }));
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ json: contacts }));
  await page.route(`${API}/auth/methods`, (r) => r.fulfill({ json: { kind: "ok", methods: [LOCAL] } }));
  await page.route(`${API}/auth/sessions`, (r) => r.fulfill({ json: { kind: "ok", sessions: [{ sessionId: S_CUR, issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: true, methodType: "LOCAL_PASSWORD" }] } }));
  await page.route(`${API}/auth/emails`, (r) => r.fulfill({ json: { kind: "ok", emails } }));
  await page.route(`${API}/workspaces`, (r) => r.fulfill({ json: { kind: "ok", workspaces: [] } }));
  await page.route(`${API}/auth/email/verification/start`, (r) => {
    w.sent.push(r.request().postDataJSON());
    return r.fulfill({ json: { kind: "ok", challengeId: CHALLENGE, expiresAt: "2026-10-05T08:00:00+00:00" } });
  });
  return w;
}

test("V1 · the login offers 'Forgot your password?' only when the deployment serves recovery", async ({ page }) => {
  await noSession(page);
  await page.goto("/login");
  await expect(page.getByTestId("login-submit")).toBeVisible();
  await expect(page.getByTestId("recover-link")).toHaveAttribute("href", "/recover");
  await page.unroute(`${API}/auth/contacts`);
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ json: CONTACTS_OFF }));
  await page.goto("/login");
  await expect(page.getByTestId("login-submit")).toBeVisible();
  await expect(page.getByTestId("recover-link")).toHaveCount(0);
  await page.unroute(`${API}/auth/contacts`);
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ status: 502, contentType: "text/html", body: "bad" }));
  await page.goto("/login");
  await expect(page.getByTestId("login-submit")).toBeVisible();
  await expect(page.getByTestId("recover-link")).toHaveCount(0);
});

test("V2 · /recover: the one answer for any address; unavailable deployment says so and sends nothing", async ({ page }) => {
  await noSession(page);
  const requests: unknown[] = [];
  await page.route(`${API}/auth/recovery/start`, (r) => {
    requests.push(r.request().postDataJSON());
    return r.fulfill({ json: { kind: "ok" } });
  });
  await page.goto("/recover");
  await page.getByTestId("recover-email").fill("Someone@Example.test");
  await page.getByTestId("recover-submit").click();
  await expect(page.getByTestId("recover-sent")).toContainText("If this address can recover an account");
  expect(requests).toEqual([{ email: "Someone@Example.test" }]);
  await expect(page.getByTestId("recover-form")).toHaveCount(0);
  expect(await page.locator("main").innerText()).not.toMatch(/no account|does not exist|unknown address/i);
  // not offered: the page says so, the control is disabled, nothing is sent
  await page.unroute(`${API}/auth/contacts`);
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ json: CONTACTS_OFF }));
  await page.goto("/recover");
  await expect(page.getByTestId("recover-unavailable")).toBeVisible();
  await expect(page.getByTestId("recover-submit")).toBeDisabled();
  expect(requests).toHaveLength(1);
});

test("V3 · /recover/reset: the link is captured once and leaves the address bar; confirm must agree; success leads to the login; denied is the server's one class", async ({ page }) => {
  await noSession(page);
  let verdict: unknown = { kind: "ok" };
  const sent: unknown[] = [];
  await page.route(`${API}/auth/recovery/complete`, (r) => {
    sent.push(r.request().postDataJSON());
    return r.fulfill({ status: verdict === null ? 403 : 200, json: verdict ?? { kind: "denied", reasonCode: "RECOVERY_DENIED" } });
  });
  await page.goto(`/recover/reset?recovery=${RECOVERY}&token=secret-token-value`);
  await expect(page.getByTestId("reset-form")).toBeVisible();
  await expect(page).toHaveURL(/\/recover\/reset$/); // the token left the address bar
  await page.getByTestId("reset-password").fill("a brand new passphrase");
  await page.getByTestId("reset-confirm").fill("a brand new passphrasX");
  await expect(page.getByTestId("reset-mismatch")).toBeVisible();
  await expect(page.getByTestId("reset-submit")).toBeDisabled();
  await page.getByTestId("reset-confirm").fill("a brand new passphrase");
  await page.getByTestId("reset-submit").click();
  await expect(page.getByTestId("reset-done")).toBeVisible();
  await expect(page.getByTestId("reset-login")).toHaveAttribute("href", "/login");
  expect(sent).toEqual([{ recoveryId: RECOVERY, token: "secret-token-value", newPassword: "a brand new passphrase" }]);
  expect(await page.locator("main").innerText()).not.toContain("secret-token-value");
  // a used / expired / foreign link: one class
  verdict = null;
  await page.goto(`/recover/reset?recovery=${RECOVERY}&token=other`);
  await page.getByTestId("reset-password").fill("a brand new passphrase");
  await page.getByTestId("reset-confirm").fill("a brand new passphrase");
  await page.getByTestId("reset-submit").click();
  await expect(page.getByTestId("reset-error")).toHaveAttribute("data-outcome", "denied");
  await expect(page.getByTestId("reset-again")).toHaveAttribute("href", "/recover");
  // without the link: the page asks for it, the control stays disabled
  await page.goto("/recover/reset");
  await expect(page.getByTestId("reset-incomplete")).toBeVisible();
  await expect(page.getByTestId("reset-submit")).toBeDisabled();
});

test("V4 · /account/verify-email: completes once while logged in, strips the link, names the address; without a session it says to log in first", async ({ page }) => {
  const w = await session(page, []);
  const completions: unknown[] = [];
  await page.route(`${API}/auth/email/verification/complete`, (r) => {
    completions.push(r.request().postDataJSON());
    return r.fulfill({ json: { kind: "ok", email: "tobias@thescaleforge.com" } });
  });
  await page.goto(`/account/verify-email?challengeId=${CHALLENGE}&token=verify-token`);
  await expect(page.getByTestId("verify-done")).toBeVisible();
  await expect(page.getByTestId("verify-email")).toHaveText("tobias@thescaleforge.com");
  await expect(page).toHaveURL(/\/account\/verify-email$/);
  expect(completions).toEqual([{ challengeId: CHALLENGE, token: "verify-token" }]);
  await expect(page.getByTestId("verify-continue")).toHaveAttribute("href", "/workspaces");
  expect(w.sent).toEqual([]);
  // no session
  await page.unroute(`${API}/auth/email/verification/complete`);
  await page.route(`${API}/auth/email/verification/complete`, (r) => r.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.goto(`/account/verify-email?challengeId=${CHALLENGE}&token=verify-token`);
  await expect(page.getByTestId("verify-no-session")).toBeVisible();
  await page.goto("/account/verify-email");
  await expect(page.getByTestId("verify-incomplete")).toBeVisible();
});

test("V5 · the chamber shows the verification relation: unverified → Send (the canonical address is sent, nothing else); verified → no control", async ({ page }) => {
  const w = await session(page, []);
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-email")).toHaveAttribute("data-verified", "false");
  await expect(chamber.getByTestId("account-email-address")).toHaveText("tobias@thescaleforge.com");
  await expect(chamber.getByTestId("account-email-unverified")).toContainText("verified address");
  await chamber.getByTestId("account-email-verify").click();
  await expect(chamber.getByTestId("account-effect-committed")).toBeVisible();
  expect(w.sent).toEqual([{ email: "tobias@thescaleforge.com" }]);
  await page.unroute(`${API}/auth/emails`);
  await page.route(`${API}/auth/emails`, (r) => r.fulfill({ json: { kind: "ok", emails: [{ email: "tobias@thescaleforge.com", verifiedAt: "2026-10-05T08:00:00+00:00", active: true }] } }));
  await page.goto("/workspaces");
  await expect(chamber.getByTestId("account-email")).toHaveAttribute("data-verified", "true");
  await expect(chamber.getByTestId("account-email-verified")).toContainText("it can recover your password");
  await expect(chamber.getByTestId("account-email-verify")).toHaveCount(0);
  // a deployment without verification: no e-mail section at all
  await page.unroute(`${API}/auth/contacts`);
  await page.route(`${API}/auth/contacts`, (r) => r.fulfill({ json: CONTACTS_OFF }));
  await page.goto("/workspaces");
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-email")).toHaveCount(0);
});
