/**
 * AUTH/CYAN-ACCOUNT-01 REAL-STACK proof (the cross-lineage lane): this CYAN web against the real PURPLE API
 * (`auth-identity`, NQUIRY_ENVIRONMENT=TEST, the local test issuer of 24 §27.1, SELF_REGISTRATION_ALLOWED), real
 * PostgreSQL, real Chromium. No network mocking. The three identity cases of PURPLE's CONSUMER_CONTRACT.md §1 as a
 * human meets them in the product UI, plus every 24 §24.5 contact of the Access security chamber:
 *
 *   LOCAL            → local login · identity presented · one method, not removable · provider offered
 *   LINK             → Add <provider> (form POST) → consent → ?link=ok → two methods
 *   PROVIDER_LINKED  → provider login reaches the SAME identity (same userId, same name, same canonical email)
 *   UNLINK           → Remove the current provider method → the session ends on the server → /login
 *   SESSIONS         → a second browser's session is listed · End it → that browser is signed out · Sign out everywhere
 *   PROVIDER_BOOTSTRAP → an unbound subject logs in → its OWN identity, name and email from the provider's claims,
 *                      one method, not removable; the binding persists across logins
 */
import { expect, test, type Page } from "@playwright/test";
import { provisionIdentity } from "./identities";

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";

async function localLogin(page: Page, email: string, password: string): Promise<void> {
  await page.goto("/login");
  await page.getByTestId("login-email").fill(email);
  await page.getByTestId("login-password").fill(password);
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/workspaces$/);
}

/** The test issuer's consent page (served by the API itself): approve for a subject, optionally with an email. */
async function consent(page: Page, subject: string, email: string | null): Promise<void> {
  await expect(page.getByTestId("test-provider-form")).toBeVisible();
  await page.getByTestId("test-provider-subject").fill(subject);
  if (email !== null) await page.getByTestId("test-provider-email").fill(email);
  await page.getByTestId("test-provider-approve").click();
}

test("LOCAL → LINK → PROVIDER_LINKED → UNLINK: one identity through every contact of the chamber", async ({ page }) => {
  const me = provisionIdentity("cyanacct");
  const subject = `cyan-linked-${Date.now()}`;
  await localLogin(page, me.email, me.password);

  // LOCAL: the identity is presented from /auth/identity; the chamber shows one method, not removable, the offer
  await expect(page.getByTestId("identity-panel-name")).toHaveText(me.name);
  await expect(page.getByTestId("identity-panel-email")).toHaveText(me.email);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(0);
  await expect(chamber.getByTestId("account-method-last")).toBeVisible();
  const form = chamber.getByTestId("account-link-form");
  await expect(form).toHaveAttribute("action", `${API}/auth/oidc/test/link/start?next=%2Fworkspaces`);
  await expect(chamber.getByTestId("account-link-test")).toContainText("test provider");

  // LINK: the browser submits the form (app origin → API), the API's consent page, the callback, back with ?link=ok
  await chamber.getByTestId("account-link-test").click();
  await consent(page, subject, "linked-account@provider.test");
  await expect(page).toHaveURL(/\/workspaces\?link=ok$/);
  await expect(chamber.getByTestId("link-result")).toHaveAttribute("data-settled", "committed");
  await expect(chamber.getByTestId("account-method")).toHaveCount(2);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(2);
  await expect(chamber.getByTestId("account-link-form")).toHaveCount(0);
  await expect(chamber.getByTestId("account-method-email")).toHaveText("linked-account@provider.test");
  // the session survived the link (rotated, 24 §15.6): still the identity, still Local password as the sign-in
  await expect(page.getByTestId("identity-panel-name")).toHaveText(me.name);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  const userId = (await page.getByTestId("identity-user-id").textContent()) ?? "";
  expect(userId).toMatch(/^[0-9a-f-]{36}$/);

  // PROVIDER_LINKED: log out, log in through the provider contact of the Access Field → the SAME identity
  await page.getByTestId("logout-button").click();
  await expect(page).toHaveURL(/\/login$/);
  await page.getByTestId("provider-test").click();
  await consent(page, subject, "linked-account@provider.test");
  await expect(page).toHaveURL(/\/workspaces$/);
  await expect(page.getByTestId("identity-user-id")).toHaveText(userId);
  await expect(page.getByTestId("identity-panel-name")).toHaveText(me.name);
  await expect(page.getByTestId("identity-panel-email")).toHaveText(me.email);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Test provider");
  await expect(page.getByTestId("identity-panel-account")).toContainText("linked-account@provider.test");
  await expect(chamber.locator('[data-testid="account-method"][data-current="true"]')).toHaveAttribute("data-method-type", "TEST_PROVIDER");

  // UNLINK the current provider method: the server ends the provider-produced session → the page leaves
  await chamber.locator('[data-testid="account-method"][data-current="true"]').getByTestId("account-method-remove").click();
  await expect(page).toHaveURL(/\/login$/);
  await localLogin(page, me.email, me.password);
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-link-form")).toHaveCount(1);
  await expect(page.getByTestId("identity-user-id")).toHaveText(userId);
});

test("SESSIONS: another browser's session is listed, End signs that browser out, Sign out everywhere ends this one", async ({ page, browser }) => {
  const me = provisionIdentity("cyansess");
  const other = await browser.newContext();
  const otherPage = await other.newPage();
  await localLogin(otherPage, me.email, me.password);
  await localLogin(page, me.email, me.password);
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-session")).toHaveCount(2);
  await expect(chamber.getByTestId("account-session-end")).toHaveCount(1);
  await chamber.getByTestId("account-session-end").click();
  await expect(chamber.getByTestId("account-effect-committed")).toBeVisible();
  await expect(chamber.getByTestId("account-session")).toHaveCount(1);
  // the other browser's session is gone on the server: its next page load is sent to /login
  await otherPage.goto("/workspaces");
  await expect(otherPage).toHaveURL(/\/login$/);
  await other.close();
  await chamber.getByTestId("account-sign-out-everywhere").click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto("/workspaces");
  await expect(page).toHaveURL(/\/login$/);
});

test("PROVIDER_BOOTSTRAP: an unbound subject reaches its OWN identity — name and email from the provider's claims, one method, the binding persists", async ({ page }) => {
  const subject = `cyan-bootstrap-${Date.now()}`;
  const email = `bootstrap-${Date.now()}@provider.test`;
  await page.goto("/login");
  await page.getByTestId("provider-test").click();
  await consent(page, subject, email);
  await expect(page).toHaveURL(/\/workspaces$/);
  // the test issuer's display-name claim becomes the identity's name once, at creation; the verified email its canonical email
  await expect(page.getByTestId("identity-panel-name")).toHaveText("Test Subject");
  await expect(page.getByTestId("identity-panel-email")).toHaveText(email);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Test provider");
  await expect(page.getByTestId("identity-panel-account")).toContainText(email);
  const userId = (await page.getByTestId("identity-user-id").textContent()) ?? "";
  expect(userId).toMatch(/^[0-9a-f-]{36}$/);
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(0);
  await expect(chamber.getByTestId("account-method-last")).toBeVisible();
  await expect(chamber.getByTestId("account-link-form")).toHaveCount(0);
  await expect(chamber.getByTestId("account-session")).toHaveCount(1);
  // a bootstrapped identity has no Workspace: founding stays possible, nothing was granted
  await expect(page.getByTestId("workspaces-empty")).toBeVisible();
  // the binding persists: the same subject reaches the same identity again
  await page.getByTestId("logout-button").click();
  await page.getByTestId("provider-test").click();
  await consent(page, subject, email);
  await expect(page).toHaveURL(/\/workspaces$/);
  await expect(page.getByTestId("identity-user-id")).toHaveText(userId);
});

// --- AUTH/CYAN-ACCOUNT-02 (real) --------------------------------------------------------------------------------

test("PASSWORD ROTATION: the owner changes the password in the chamber; the old one stops working, the other session ends, this one continues", async ({ page, browser }) => {
  const me = provisionIdentity("cyanrot");
  const other = await browser.newContext();
  const otherPage = await other.newPage();
  await localLogin(otherPage, me.email, me.password);
  await localLogin(page, me.email, me.password);
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-session")).toHaveCount(2);
  const form = chamber.getByTestId("account-password-form");
  await form.getByTestId("account-current-password").fill(me.password);
  await form.getByTestId("account-new-password").fill(`${me.password}-rotated`);
  await form.getByTestId("account-confirm-password").fill(`${me.password}-rotated`);
  await form.getByTestId("account-password-submit").click();
  await expect(chamber.getByTestId("account-effect-committed")).toBeVisible();
  await expect(chamber.getByTestId("account-session")).toHaveCount(1);
  await expect(page.getByTestId("identity-panel-name")).toHaveText(me.name);
  await otherPage.goto("/workspaces");
  await expect(otherPage).toHaveURL(/\/login$/);
  await other.close();
  // a wrong current password is refused on the surface and changes nothing
  await form.getByTestId("account-current-password").fill("not the password");
  await form.getByTestId("account-new-password").fill("another passphrase 9");
  await form.getByTestId("account-confirm-password").fill("another passphrase 9");
  await form.getByTestId("account-password-submit").click();
  await expect(chamber.getByTestId("account-effect-reason")).toHaveText("CURRENT_PASSWORD_INVALID");
  // the old password is gone, the rotated one logs in
  await page.getByTestId("logout-button").click();
  await page.getByTestId("login-email").fill(me.email);
  await page.getByTestId("login-password").fill(me.password);
  await page.getByTestId("login-submit").click();
  await expect(page.getByTestId("login-error")).toContainText("Incorrect");
  await localLogin(page, me.email, `${me.password}-rotated`);
});

test("ROSTER: the governance root changes a member's role and then ends the membership through the Members chamber", async ({ page }) => {
  const owner = provisionIdentity("cyanroot");
  const member = provisionIdentity("cyanmember");
  await localLogin(page, owner.email, owner.password);
  await page.getByTestId("workspace-name-input").fill("Roster Field");
  await page.getByTestId("create-workspace-submit").click();
  await expect(page).toHaveURL(/\/workspaces\/[0-9a-f-]{36}$/);
  await page.getByTestId("new-member-user-id-input").fill(member.userId);
  await page.getByTestId("add-member-submit").click();
  await expect(page.getByTestId("add-member-success")).toBeVisible();
  const admin = page.getByTestId("roster-admin");
  const row = admin.locator(`[data-user="${member.userId}"]`);
  await expect(row).toBeVisible();
  await expect(admin.locator(`[data-user="${owner.userId}"]`)).toHaveCount(0); // the root is never administrable
  await expect(row).toHaveAttribute("data-role", "Contributor");
  await row.getByTestId("roster-change-role").click();
  await expect(admin.getByTestId("roster-admin-success")).toBeVisible();
  await expect(row).toHaveAttribute("data-role", "Facilitator");
  await row.getByTestId("roster-remove").click();
  await expect(admin.getByTestId("roster-admin-success")).toBeVisible();
  await expect(admin.locator(`[data-user="${member.userId}"]`)).toHaveCount(0);
  await expect(page.getByTestId("members-list").locator(`[data-user="${member.userId}"]`)).toHaveCount(0);
});

test("LOCKOUT: five wrong passwords pause the address; the right password is paused too; the login page says so", async ({ page }) => {
  const me = provisionIdentity("cyanlock");
  await page.goto("/login");
  for (let i = 0; i < 5; i += 1) {
    await page.getByTestId("login-email").fill(me.email);
    await page.getByTestId("login-password").fill("wrong");
    await page.getByTestId("login-submit").click();
    await expect(page.getByTestId("login-error")).toContainText("Incorrect");
  }
  await page.getByTestId("login-password").fill(me.password);
  await page.getByTestId("login-submit").click();
  await expect(page.getByTestId("login-error")).toContainText("Too many attempts");
  await expect(page).toHaveURL(/\/login$/);
});
