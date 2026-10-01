/**
 * WU-AUTH-14 REAL-STACK proof of the anti-CSRF boundary (24 §21.6–21.9).
 *
 * Real Chromium → real Next.js app (AUTH real lane port) → real FastAPI → real
 * PostgreSQL. A hostile page is served from a THIRD origin
 * (`tests/real-stack/hostile/attack.html`). No network mocking of any kind.
 *
 * Proven here against the real browser/API request contract:
 *  - a hostile origin cannot log the victim browser into an attacker-selected
 *    local account (form POST urlencoded, form POST text/plain, fetch text/plain,
 *    fetch JSON);
 *  - a hostile origin cannot end or alter the victim's real session
 *    (logout-all / unlink by form and by credentialed fetch);
 *  - the legitimate same-app login still creates a fresh session and the
 *    legitimate logout-all still works.
 */
import { expect, test, type BrowserContext, type Page } from "@playwright/test";
import { provisionIdentity } from "./identities";

declare global {
  interface Window {
    __attacks: {
      formLoginUrlencoded(): void;
      formLoginTextPlain(): void;
      formLogoutAll(): void;
      formUnlink(methodId: string): void;
      fetchLogoutAll(): Promise<string>;
      fetchLoginTextPlain(): Promise<string>;
      fetchLoginJson(): Promise<string>;
    };
  }
}

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:18460";
const HOSTILE = process.env.REAL_STACK_HOSTILE_URL ?? "http://localhost:13471";

async function sessionCookies(context: BrowserContext): Promise<string[]> {
  return (await context.cookies(API)).filter((c) => c.name === "nquiry_session").map((c) => c.value);
}

async function meStatus(page: Page): Promise<number> {
  // read through the real app origin: the only origin allowed to read the API
  return page.evaluate(async (api) => (await fetch(`${api}/auth/me`, { credentials: "include" })).status, API);
}

async function hostile(context: BrowserContext, attackerEmail: string, attackerPassword: string): Promise<Page> {
  const page = await context.newPage();
  const url = new URL(`${HOSTILE}/attack.html`);
  url.searchParams.set("api", API);
  url.searchParams.set("email", attackerEmail);
  url.searchParams.set("password", attackerPassword);
  await page.goto(url.toString());
  await expect(page.getByRole("heading", { name: "hostile page" })).toBeVisible();
  return page;
}

async function settle(page: Page): Promise<void> {
  // let the sink iframe navigations complete
  await page.waitForTimeout(1500);
}

test("a hostile origin cannot log the visiting browser into an attacker-selected account", async ({ context, page }) => {
  const attacker = provisionIdentity("attacker");
  await page.goto("/login");
  expect(await sessionCookies(context)).toEqual([]);

  const evil = await hostile(context, attacker.email, attacker.password);
  await evil.evaluate(() => window.__attacks.formLoginUrlencoded());
  await settle(evil);
  await evil.evaluate(() => window.__attacks.formLoginTextPlain());
  await settle(evil);
  const plain = await evil.evaluate(() => window.__attacks.fetchLoginTextPlain());
  const json = await evil.evaluate(() => window.__attacks.fetchLoginJson());

  // whatever the hostile page observed, no session exists in this browser
  expect(plain).toMatch(/^(blocked:|status:403)/);
  expect(json).toMatch(/^blocked:/);
  expect(await sessionCookies(context)).toEqual([]);
  expect(await meStatus(page)).toBe(401);
});

test("a hostile origin cannot end or alter the victim's real session; the legitimate app still can", async ({
  context,
  page,
}) => {
  const victim = provisionIdentity("victim");
  const attacker = provisionIdentity("attacker2");

  // legitimate login through the real form: a fresh session
  await page.goto("/login");
  await page.getByTestId("login-email").fill(victim.email);
  await page.getByTestId("login-password").fill(victim.password);
  await page.getByTestId("login-submit").click();
  await expect(page).not.toHaveURL(/\/login$/);
  const [token] = await sessionCookies(context);
  expect(token).toBeTruthy();
  expect(await meStatus(page)).toBe(200);
  const methodId = await page.evaluate(async (api) => {
    const body = await (await fetch(`${api}/auth/methods`, { credentials: "include" })).json();
    return body.methods[0].methodId as string;
  }, API);

  const evil = await hostile(context, attacker.email, attacker.password);
  await evil.evaluate(() => window.__attacks.formLogoutAll());
  await settle(evil);
  await evil.evaluate((id) => window.__attacks.formUnlink(id), methodId);
  await settle(evil);
  const fetched = await evil.evaluate(() => window.__attacks.fetchLogoutAll());
  expect(fetched).toMatch(/^(blocked:|status:403)/);
  // the hostile login attempts must not have swapped the victim's session either
  await evil.evaluate(() => window.__attacks.formLoginUrlencoded());
  await settle(evil);

  expect(await sessionCookies(context)).toEqual([token]);
  expect(await meStatus(page)).toBe(200);
  const methods = await page.evaluate(async (api) => (await fetch(`${api}/auth/methods`, { credentials: "include" })).json(), API);
  expect(methods.methods[0].status).toBe("ACTIVE");

  // the legitimate app ends the session through the same contact the hostile page could not use
  await page.goto("/account/security");
  await page.getByTestId("logout-all").click();
  await expect(page).toHaveURL(/\/login/);
  expect(await meStatus(page)).toBe(401);
});
