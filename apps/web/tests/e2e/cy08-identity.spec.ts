/**
 * AUTH/CYAN-IDENTITY-01 browser proof (mocked lane): the current authentication relation inside the existing
 * "Identity and access" chamber of the Workspaces field; Google and local states; every malformed or unavailable read
 * fails closed; the Workspace organism, the access projection and Logout are unchanged; desktop + Pixel 7.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const USER = "7dd6e767-1111-4111-8111-111111111111";
const S_CUR = "aaaaaaaa-1111-4111-8111-111111111111";
const S_OLD = "bbbbbbbb-1111-4111-8111-111111111111";
const PROVIDERS = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
/** Live-shaped identity presentation (values evidence-derived from the production proof of 2026-10-03). */
const IDENTITY = { kind: "ok", userId: USER, displayName: "tobi", canonicalEmail: "tobias@thescaleforge.com" };
const METHODS = {
  kind: "ok",
  methods: [
    { methodId: "cccccccc-1111-4111-8111-111111111111", methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: "2026-10-01T08:00:00+00:00", lastAuthenticatedAt: "2026-10-01T08:00:00+00:00", provider: null },
    { methodId: "dddddddd-1111-4111-8111-111111111111", methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: "2026-10-03T08:00:00+00:00", lastAuthenticatedAt: "2026-10-03T08:00:00+00:00", provider: { providerId: "google", email: "person@example.test" } },
  ],
};
const sessionsBody = (currentType: string | null, currentIsNewest = true) => ({
  kind: "ok",
  sessions: [
    { sessionId: S_OLD, issuedAt: "2026-10-01T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: !currentIsNewest, methodType: "LOCAL_PASSWORD" },
    { sessionId: S_CUR, issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: currentIsNewest, methodType: currentType },
  ],
});
type Handler = Parameters<Page["route"]>[1];
async function base(page: Page, identity: unknown = IDENTITY): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: USER } }));
  await page.route(`${API}/auth/identity`, (route) => route.fulfill(identity === null ? { status: 502, contentType: "text/html", body: "<html>bad gateway</html>" } : { json: identity }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [{ workspaceId: "ws-1", name: "Team Alpha", ownerId: USER, createdAt: "2026-01-01T00:00:00Z" }] } }));
}
async function auth(page: Page, sessions: Handler, methods: Handler, providers: Handler): Promise<void> {
  await page.route(`${API}/auth/sessions`, sessions);
  await page.route(`${API}/auth/methods`, methods);
  await page.route(`${API}/auth/providers`, providers);
}
const json = (body: unknown, status = 200): Handler => (route) => route.fulfill({ status, json: body });

async function expectOrganismIntact(page: Page): Promise<void> {
  await expect(page.getByTestId("workspaces-list")).toBeVisible();
  await expect(page.getByTestId("create-workspace-form")).toBeVisible();
  await expect(page.getByTestId("logout-button")).toBeVisible();
  await expect(page.getByTestId("identity-user-id")).toHaveText(USER);
  expect(await page.locator("main").innerText()).not.toMatch(/avatar|permission/i);
}
async function expectIdentityPresented(page: Page): Promise<void> {
  await expect(page.getByTestId("identity-display-name")).toHaveText("tobi");
  await expect(page.getByTestId("identity-canonical-email")).toHaveText("tobias@thescaleforge.com");
  await expect(page.getByTestId("identity-panel-name")).toHaveText("tobi");
  await expect(page.getByTestId("identity-panel-email")).toHaveText("tobias@thescaleforge.com");
}

test("a Google session: identity · Current authentication Google · Provider account (attribute) · Session current, inside the Identity and access chamber", async ({ page }) => {
  await base(page);
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(METHODS), json(PROVIDERS));
  await page.goto("/workspaces");
  const chamber = page.locator('[aria-labelledby="access-proof-title"]');
  await expect(chamber.getByTestId("identity-projection")).toBeVisible();
  await expectIdentityPresented(page);
  // WHO before HOW: the identity above the authentication in the chamber; the technical identity collapsed
  const chamberText = await chamber.innerText();
  expect(chamberText.toLowerCase().indexOf("tobi")).toBeLessThan(chamberText.toLowerCase().indexOf("current authentication"));
  await expect(chamber.locator("details")).not.toHaveAttribute("open", /.*/);
  await expect(chamber.getByTestId("auth-method")).toHaveAttribute("data-method-type", "GOOGLE_OIDC");
  await expect(chamber.getByTestId("auth-method").locator(".auth-words")).toHaveText("Google");
  await expect(chamber.getByTestId("auth-method").getByTestId("auth-provider-account")).toContainText("Google account");
  await expect(chamber.getByTestId("auth-provider-account")).toContainText("person@example.test");
  await expect(chamber.getByTestId("auth-provider-account")).toContainText("not your nquiry identity");
  // the rail panel: Signed in with Google · Google account email · Log out; no menu
  const panel = page.getByTestId("identity-panel");
  await expect(panel).toBeVisible();
  await expect(panel).toHaveAttribute("data-method-type", "GOOGLE_OIDC");
  await expect(panel).toContainText("Signed in with");
  await expect(panel.getByTestId("identity-panel-method")).toHaveText("Google");
  await expect(panel.getByTestId("identity-panel-account")).toContainText("Google account");
  await expect(panel.getByTestId("identity-panel-account")).toContainText("person@example.test");
  await expect(panel.getByTestId("logout-button")).toBeVisible();
  expect(await panel.locator("a, form, select, input, [role=menu], [aria-haspopup]").count()).toBe(0);
  expect(await page.locator("header.shell-header").innerText()).not.toMatch(/Ottavio|Braun|avatar|profile|settings/i);
  const header = await page.locator("header.shell-header").boundingBox();
  const panelBox = await panel.boundingBox();
  expect(header && panelBox && panelBox.x >= header.x && panelBox.x + panelBox.width <= header.x + header.width + 1).toBe(true);
  // the panel never covers the product mark (SF-03 rail: trace · identity · exit), on any width
  const mark = await page.getByTestId("identity").boundingBox();
  expect(mark && panelBox && (panelBox.x >= mark.x + mark.width - 1 || panelBox.y >= mark.y + mark.height - 1 || panelBox.x + panelBox.width <= mark.x + 1)).toBe(true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
  await expect(chamber.getByTestId("auth-session")).toHaveAttribute("data-session-id", S_CUR);
  await expect(chamber.getByTestId("auth-session")).toContainText("current · authenticated");
  await expectOrganismIntact(page);
  // the chamber is a proof plane of the organism: the core (Workspaces) stays primary; no profile surface
  await expect(page.getByTestId("field-core")).toBeVisible();
  expect(await page.locator('[aria-labelledby="access-proof-title"] a, [aria-labelledby="access-proof-title"] form, [aria-labelledby="access-proof-title"] select').count()).toBe(0);
  const box = await chamber.getByTestId("identity-projection").boundingBox();
  const plane = await chamber.boundingBox();
  expect(plane && box && box.x >= plane.x - 1 && box.x + box.width <= plane.x + plane.width + 1).toBe(true);
  expect(await page.evaluate(() => { window.scrollTo(10000, 0); return window.scrollX; })).toBe(0);
});

test("a local-password session: Current authentication Local password, no provider account", async ({ page }) => {
  await base(page);
  await auth(page, json(sessionsBody("LOCAL_PASSWORD")), json(METHODS), json(PROVIDERS));
  await page.goto("/workspaces");
  await expectIdentityPresented(page);
  await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveText("Local password");
  await expect(page.getByTestId("auth-provider-account")).toHaveCount(0);
  await expect(page.getByTestId("auth-session")).toBeVisible();
  // the rail panel: a linked Google method is NOT the current authentication → no Google, no email
  const panel = page.getByTestId("identity-panel");
  await expect(panel).toHaveAttribute("data-method-type", "LOCAL_PASSWORD");
  await expect(panel.getByTestId("identity-panel-method")).toHaveText("Local password");
  await expect(panel.getByTestId("identity-panel-account")).toHaveCount(0);
  expect(await panel.innerText()).not.toMatch(/google|person@|protonmail/i);
  await expect(panel.getByTestId("logout-button")).toBeVisible();
  await expectOrganismIntact(page);
});

test("the current session comes only from current=true: the older session marked current wins over the newest", async ({ page }) => {
  await base(page);
  await auth(page, json(sessionsBody("GOOGLE_OIDC", false)), json(METHODS), json(PROVIDERS));
  await page.goto("/workspaces");
  await expect(page.getByTestId("auth-session")).toHaveAttribute("data-session-id", S_OLD);
  await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveText("Local password");
});

const closed: ReadonlyArray<[string, (p: Page) => Promise<void>, ReadonlyArray<[string, number]>]> = [
  ["sessions malformed (two current)", (p) => auth(p, json({ kind: "ok", sessions: [{ ...sessionsBody("GOOGLE_OIDC").sessions[0], current: true }, sessionsBody("GOOGLE_OIDC").sessions[1]] }), json(METHODS), json(PROVIDERS)), [["auth-session", 0], ["auth-method", 0], ["auth-provider-account", 0]]],
  ["sessions unavailable (503 html)", (p) => auth(p, (route) => route.fulfill({ status: 503, contentType: "text/html", body: "<html>unavailable</html>" }), json(METHODS), json(PROVIDERS)), [["auth-session", 0], ["auth-method", 0], ["auth-provider-account", 0]]],
  ["sessions network failure", (p) => auth(p, (route) => route.abort("connectionrefused"), json(METHODS), json(PROVIDERS)), [["auth-session", 0], ["auth-method", 0]]],
  ["methods malformed (unknown methodType)", (p) => auth(p, json(sessionsBody("GOOGLE_OIDC")), json({ kind: "ok", methods: [{ ...METHODS.methods[1], methodType: "APPLE_OIDC" }] }), json(PROVIDERS)), [["auth-session", 1], ["auth-method", 0], ["auth-provider-account", 0]]],
  ["methods denied", (p) => auth(p, json(sessionsBody("GOOGLE_OIDC")), json({ kind: "denied", reasonCode: "NO_SESSION" }, 401), json(PROVIDERS)), [["auth-session", 1], ["auth-method", 0], ["auth-provider-account", 0]]],
  ["providers malformed (unknown proofClass)", (p) => auth(p, json(sessionsBody("GOOGLE_OIDC")), json(METHODS), json({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PROVEN" }] })), [["auth-session", 1], ["auth-method", 1]]],
  ["providers empty", (p) => auth(p, json(sessionsBody("GOOGLE_OIDC")), json(METHODS), json({ kind: "ok", providers: [] })), [["auth-session", 1], ["auth-method", 1]]],
];
for (const [name, routes, counts] of closed) {
  test(`${name} → fails closed; identity and organism unchanged`, async ({ page }) => {
    await base(page);
    await routes(page);
    await page.goto("/workspaces");
    await expect(page.getByTestId("identity-user-id")).toHaveText(USER);
    for (const [id, n] of counts) await expect(page.getByTestId(id)).toHaveCount(n);
    if (name.startsWith("providers")) {
      // the label is the raw provider id, never an invented Google — in the chamber and in the rail panel
      await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveText("google");
      await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveAttribute("data-label-kind", "provider");
      await expect(page.getByTestId("identity-panel-method")).toHaveText("google");
      expect(await page.getByTestId("identity-panel").innerText()).not.toMatch(/Google/);
    }
    if (name.startsWith("methods") || name.startsWith("sessions")) {
      // no method truth → no "Signed in with" claim in the rail; Logout stays
      expect(await page.getByTestId("identity-panel").innerText()).not.toMatch(/Signed in with|person@example/);
      // STATE E: the identity presentation stays (name), the method is omitted; the technical id is not the label
      await expect(page.getByTestId("identity-panel-name")).toHaveText("tobi");
      await expect(page.getByTestId("identity-panel-identity")).toHaveCount(0);
      await expect(page.getByTestId("identity-panel").getByTestId("logout-button")).toBeVisible();
    }
    await expectOrganismIntact(page);
  });
}

test("no /auth/me → no projection at all (the page leaves for /login as before)", async ({ page }) => {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(METHODS), json(PROVIDERS));
  await page.goto("/workspaces");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByTestId("identity-projection")).toHaveCount(0);
});

test("Logout is unchanged: it posts to /auth/logout and returns to /login", async ({ page }) => {
  await base(page);
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(METHODS), json(PROVIDERS));
  await page.route(`${API}/auth/logout`, (route) => route.fulfill({ json: { kind: "ok" } }));
  await page.goto("/workspaces");
  await expect(page.getByTestId("identity-panel").getByTestId("logout-button")).toBeVisible();
  const logoutRequest = page.waitForRequest((r) => r.url() === `${API}/auth/logout` && r.method() === "POST");
  await page.getByTestId("logout-button").click();
  await logoutRequest;
  await page.unroute(`${API}/auth/me`);
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await expect(page).toHaveURL(/\/login$/);
});

// --- Field reconstruction cases (the CURRENT method is the method that produced the CURRENT session) -----------------

test("CASE 1 · the local login transition itself: form → local session → projection Local password, no Google, no email", async ({ page }) => {
  let authenticated = false;
  await page.route(`${API}/auth/me`, (route) => route.fulfill(authenticated ? { json: { kind: "ok", userId: USER } } : { status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/login`, async (route) => {
    authenticated = true;
    await route.fulfill({ json: { kind: "ok", userId: USER } });
  });
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [] } }));
  await auth(page, json(sessionsBody("LOCAL_PASSWORD")), json(METHODS), json(PROVIDERS));
  await page.goto("/login");
  await page.getByTestId("login-email").fill("person@nonproof.test");
  await page.getByTestId("login-password").fill("pw");
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/workspaces$/);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveText("Local password");
  await expect(page.getByTestId("identity-panel-account")).toHaveCount(0);
  await expect(page.getByTestId("auth-provider-account")).toHaveCount(0);
  // CURRENT METHOD != ANY LINKED METHOD holds in both identity organisms; the linked Google method is listed only
  // where held methods are the relation (the Access security chamber, AUTH/CYAN-ACCOUNT-01), never as the sign-in
  expect(await page.locator('[data-testid="identity-panel"], [data-testid="identity-projection"]').allInnerTexts()).not.toContainEqual(expect.stringMatching(/google|person@/i));
  await expect(page.getByTestId("access-security-plane").locator('[data-testid="account-method"][data-current="true"]')).toHaveAttribute("data-method-type", "LOCAL_PASSWORD");
});

test("CASE 5 · the current session names no method: Authenticated only, no friendly method invented, Logout stays", async ({ page }) => {
  await base(page);
  await auth(page, json({ kind: "ok", sessions: [{ sessionId: S_CUR, issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: true, methodType: null }] }), json(METHODS), json(PROVIDERS));
  await page.goto("/workspaces");
  await expect(page.getByTestId("auth-session")).toBeVisible();
  await expect(page.getByTestId("auth-method")).toHaveCount(0);
  await expect(page.getByTestId("identity-panel-name")).toHaveText("tobi");
  await expect(page.getByTestId("identity-panel-method")).toHaveCount(0);
  expect(await page.getByTestId("identity-panel").innerText()).not.toMatch(/Signed in with|Google|Local password|person@example/);
  await expect(page.getByTestId("identity-panel").getByTestId("logout-button")).toBeVisible();
});

test("CASE 6 · Google current with no provider email: Google stays the current method, the account row is absent", async ({ page }) => {
  await base(page);
  const noEmail = { kind: "ok", methods: [METHODS.methods[0], { ...METHODS.methods[1], provider: { providerId: "google", email: null } }] };
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(noEmail), json(PROVIDERS));
  await page.goto("/workspaces");
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Google");
  await expect(page.getByTestId("identity-panel-account")).toHaveCount(0);
  await expect(page.getByTestId("auth-provider-account")).toHaveCount(0);
  expect(await page.getByTestId("identity-panel").innerText()).not.toContain("person@example");
});

test("RECONSTRUCTION · no projection survives a transition: Google session → logout → local login → Local password (nothing cached)", async ({ page }) => {
  let authenticated = true;
  let currentType = "GOOGLE_OIDC";
  await page.route(`${API}/auth/me`, (route) => route.fulfill(authenticated ? { json: { kind: "ok", userId: USER } } : { status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/logout`, async (route) => {
    authenticated = false;
    await route.fulfill({ json: { kind: "ok" } });
  });
  await page.route(`${API}/auth/login`, async (route) => {
    authenticated = true;
    currentType = "LOCAL_PASSWORD";
    await route.fulfill({ json: { kind: "ok", userId: USER } });
  });
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [] } }));
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ json: sessionsBody(currentType) }));
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ json: METHODS }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: PROVIDERS }));
  await page.goto("/workspaces");
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Google");
  await expect(page.getByTestId("identity-panel-account")).toContainText("person@example.test");
  await page.getByTestId("logout-button").click();
  await expect(page).toHaveURL(/\/login$/);
  await page.getByTestId("login-email").fill("person@nonproof.test");
  await page.getByTestId("login-password").fill("pw");
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/workspaces$/);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  await expect(page.getByTestId("identity-panel-account")).toHaveCount(0);
  await expect(page.getByTestId("auth-method").locator(".auth-words")).toHaveText("Local password");
  await expect(page.getByTestId("auth-provider-account")).toHaveCount(0);
});

// --- CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01 -----------------------------------------------------------------------

test("F2/F6 · Google current with a DIFFERENT provider email: nquiry identity and provider account in their own positions, both organisms", async ({ page }) => {
  await base(page);
  const methods = { kind: "ok", methods: [METHODS.methods[0], { ...METHODS.methods[1], provider: { providerId: "google", email: "syntxsystem@protonmail.com" } }] };
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(methods), json(PROVIDERS));
  await page.goto("/workspaces");
  await expectIdentityPresented(page);
  await expect(page.getByTestId("auth-provider-account")).toContainText("syntxsystem@protonmail.com");
  await expect(page.getByTestId("identity-panel-account")).toContainText("syntxsystem@protonmail.com");
  const panel = await page.getByTestId("identity-panel").innerText();
  expect(panel.indexOf("tobias@thescaleforge.com")).toBeLessThan(panel.indexOf("syntxsystem@protonmail.com"));
  expect(panel).toMatch(/nquiry identity[\s\S]*tobi[\s\S]*Signed in with[\s\S]*Google[\s\S]*Google account[\s\S]*syntxsystem@protonmail\.com[\s\S]*Log out/i);
});

test("F3/F4 · GOOGLE_LINKED: switching Google → local for ONE identity keeps the identity identical and removes only the provider relation", async ({ page }) => {
  let authenticated = true;
  let currentType = "GOOGLE_OIDC";
  await page.route(`${API}/auth/me`, (route) => route.fulfill(authenticated ? { json: { kind: "ok", userId: USER } } : { status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/identity`, (route) => route.fulfill(authenticated ? { json: IDENTITY } : { status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/logout`, async (route) => { authenticated = false; await route.fulfill({ json: { kind: "ok" } }); });
  await page.route(`${API}/auth/login`, async (route) => { authenticated = true; currentType = "LOCAL_PASSWORD"; await route.fulfill({ json: { kind: "ok", userId: USER } }); });
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [] } }));
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ json: sessionsBody(currentType) }));
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ json: METHODS }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: PROVIDERS }));
  await page.goto("/workspaces");
  await expectIdentityPresented(page);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Google");
  await page.getByTestId("logout-button").click();
  await expect(page).toHaveURL(/\/login$/);
  await page.getByTestId("login-email").fill("person@nonproof.test");
  await page.getByTestId("login-password").fill("pw");
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/workspaces$/);
  await expectIdentityPresented(page);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Local password");
  await expect(page.getByTestId("identity-panel-account")).toHaveCount(0);
  // the canonical email is never taken from the login input
  expect(await page.locator("main, header.shell-header").allInnerTexts()).not.toContainEqual(expect.stringMatching(/person@nonproof/));
});

test("F8 / STATE D · identity read unavailable: Authenticated + technical identity; the provider email stays a provider account only", async ({ page }) => {
  await base(page, { kind: "denied", reasonCode: "NO_SESSION" });
  const methods = { kind: "ok", methods: [METHODS.methods[0], { ...METHODS.methods[1], provider: { providerId: "google", email: "syntxsystem@protonmail.com" } }] };
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), json(methods), json(PROVIDERS));
  await page.goto("/workspaces");
  await expect(page.getByTestId("identity-unpresented")).toHaveText("Authenticated");
  await expect(page.getByTestId("identity-display-name")).toHaveCount(0);
  await expect(page.getByTestId("identity-panel-name")).toHaveCount(0);
  await expect(page.getByTestId("identity-panel-identity")).toHaveText(`${USER.slice(0, 8)}…`);
  await expect(page.locator('[data-testid="identity-technical"] details')).toHaveAttribute("open", "");
  await expect(page.getByTestId("identity-user-id")).toBeVisible();
  await expect(page.getByTestId("identity-panel-account")).toContainText("syntxsystem@protonmail.com");
  const who = await page.getByTestId("identity-panel-who").innerText();
  expect(who).not.toContain("@");
});

test("F9 / STATE E · method unavailable: identity visible, no method, no provider email, both organisms", async ({ page }) => {
  await base(page);
  await auth(page, json(sessionsBody("GOOGLE_OIDC")), (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }), json(PROVIDERS));
  await page.goto("/workspaces");
  await expectIdentityPresented(page);
  await expect(page.getByTestId("auth-method")).toHaveCount(0);
  await expect(page.getByTestId("identity-panel-method")).toHaveCount(0);
  expect(await page.getByTestId("identity-panel").innerText()).not.toMatch(/Google|Local password|protonmail|person@/);
});
