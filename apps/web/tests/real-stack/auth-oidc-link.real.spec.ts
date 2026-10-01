/**
 * WU-AUTH-14 REAL-STACK proof that the anti-CSRF boundary admits every
 * legitimate leg of the provider link flow and that cross-site callback
 * delivery still works (24 §21.4, §21.8): the app's link-start form POST
 * (app origin → API), the TEST_PROVIDER consent POST (API origin → API), the
 * provider's callback GET (cross-site navigation), and the account security
 * surface afterwards. Real Chromium, real app, real API, real PostgreSQL, the
 * local test issuer (24 §27.1). No network mocking of any kind.
 */
import { expect, test } from "@playwright/test";
import { provisionIdentity } from "./identities";

test("an authenticated identity links the test provider through the real consent page and callback", async ({
  page,
}) => {
  const me = provisionIdentity("linker");
  await page.goto("/login");
  await page.getByTestId("login-email").fill(me.email);
  await page.getByTestId("login-password").fill(me.password);
  await page.getByTestId("login-submit").click();
  await expect(page).not.toHaveURL(/\/login$/);

  await page.goto("/account/security");
  await expect(page.getByTestId("method-item")).toHaveCount(1);
  await page.getByTestId("link-test").click();

  // the API's own consent page (same-origin form POST on the API)
  await expect(page.getByTestId("test-provider-form")).toBeVisible();
  await page.getByTestId("test-provider-subject").fill(`real-subject-${Date.now()}`);
  await page.getByTestId("test-provider-approve").click();

  // cross-site callback delivered, link committed, back on the app
  await expect(page).toHaveURL(/\/account\/security\?link=ok$/);
  await expect(page.getByTestId("link-projection")).toBeVisible();
  await expect(page.getByTestId("method-item")).toHaveCount(2);
  await expect(page.getByTestId("method-list")).toContainText("Test provider");
  // and the session is still the identity's (rotated, 24 §15.6), not lost
  await expect(page.getByTestId("session-item")).toHaveCount(1);
});
