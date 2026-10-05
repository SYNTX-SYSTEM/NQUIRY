/**
 * AUTH/CYAN-ACCOUNT-01 browser proof (mocked lane): the "Access security" chamber of the Workspaces field — sign-in
 * methods with Remove, the provider link offer, sessions with End, Sign out everywhere, the `?link=` result — over
 * the typed PURPLE contacts; the GOOGLE_BOOTSTRAP case; refusals as the server's own reason; the identity organisms
 * and the Workspace organism unchanged; desktop + Pixel 7.
 */
import { expect, test, type Page, type Request } from "@playwright/test";

const API = "http://localhost:8000";
const USER = "7dd6e767-1111-4111-8111-111111111111";
const USER_B = "3f7842f6-2222-4222-8222-222222222222";
const S_CUR = "aaaaaaaa-1111-4111-8111-111111111111";
const S_OLD = "bbbbbbbb-1111-4111-8111-111111111111";
const M_LOCAL = "cccccccc-1111-4111-8111-111111111111";
const M_GOOGLE = "dddddddd-1111-4111-8111-111111111111";
const PROVIDERS = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
const IDENTITY = { kind: "ok", userId: USER, displayName: "tobi", canonicalEmail: "tobias@thescaleforge.com" };
const LOCAL = { methodId: M_LOCAL, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: "2026-10-01T08:00:00+00:00", lastAuthenticatedAt: "2026-10-01T08:00:00+00:00", provider: null };
const GOOGLE = { methodId: M_GOOGLE, methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: "2026-10-03T08:00:00+00:00", lastAuthenticatedAt: "2026-10-03T08:00:00+00:00", provider: { providerId: "google", email: "person@example.test" } };
const session = (id: string, current: boolean, methodType: string | null) => ({ sessionId: id, issuedAt: "2026-10-03T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current, methodType });

type World = { me: unknown; identity: unknown; methods: unknown[]; sessions: unknown[]; requests: string[] };
function world(partial: Partial<World> = {}): World {
  return { me: { kind: "ok", userId: USER }, identity: IDENTITY, methods: [LOCAL, GOOGLE], sessions: [session(S_OLD, false, "LOCAL_PASSWORD"), session(S_CUR, true, "GOOGLE_OIDC")], requests: [], ...partial };
}
const record = (w: World, r: Request) => w.requests.push(`${r.method()} ${new URL(r.url()).pathname}`);

/** The mocked PURPLE: reads answer from the world; effects mutate it the way the server would, unless overridden. */
async function purple(page: Page, w: World, effects: { unlink?: { status: number; body: unknown }; revoke?: { status: number; body: unknown }; logoutAll?: { status: number; body: unknown } } = {}): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: w.me }));
  await page.route(`${API}/auth/identity`, (route) => route.fulfill({ json: w.identity }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: PROVIDERS }));
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ json: { kind: "ok", methods: w.methods } }));
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ json: { kind: "ok", sessions: w.sessions } }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [{ workspaceId: "ws-1", name: "Team Alpha", ownerId: USER, createdAt: "2026-01-01T00:00:00Z" }] } }));
  await page.route(`${API}/auth/logout`, (route) => route.fulfill({ json: { kind: "ok" } }));
  await page.route(`${API}/auth/methods/*/unlink`, (route) => {
    record(w, route.request());
    if (effects.unlink) return route.fulfill({ status: effects.unlink.status, json: effects.unlink.body });
    const id = new URL(route.request().url()).pathname.split("/")[3];
    const m = w.methods.find((x) => (x as { methodId: string }).methodId === id) as { methodType: string } | undefined;
    const ended = m !== undefined && (w.sessions.find((s) => (s as { current: boolean }).current) as { methodType: string }).methodType === m.methodType;
    w.methods = w.methods.filter((x) => (x as { methodId: string }).methodId !== id);
    if (ended) w.me = { kind: "denied", reasonCode: "NO_SESSION" };
    return route.fulfill({ json: { kind: "ok", methodId: id, sessionsRevoked: ended ? 1 : 0, currentSessionEnded: ended } });
  });
  await page.route(`${API}/auth/sessions/*/revoke`, (route) => {
    record(w, route.request());
    if (effects.revoke) return route.fulfill({ status: effects.revoke.status, json: effects.revoke.body });
    const id = new URL(route.request().url()).pathname.split("/")[3];
    w.sessions = w.sessions.filter((s) => (s as { sessionId: string }).sessionId !== id);
    return route.fulfill({ json: { kind: "ok" } });
  });
  await page.route(`${API}/auth/logout-all`, (route) => {
    record(w, route.request());
    if (effects.logoutAll) return route.fulfill({ status: effects.logoutAll.status, json: effects.logoutAll.body });
    const n = w.sessions.length;
    w.sessions = [];
    w.me = { kind: "denied", reasonCode: "NO_SESSION" };
    return route.fulfill({ json: { kind: "ok", revokedSessions: n } });
  });
}

async function expectOrganismsIntact(page: Page): Promise<void> {
  await expect(page.getByTestId("workspaces-list")).toBeVisible();
  await expect(page.getByTestId("create-workspace-form")).toBeVisible();
  await expect(page.getByTestId("identity-panel")).toBeVisible();
  await expect(page.getByTestId("identity-projection")).toBeVisible();
  await expect(page.getByTestId("logout-button")).toBeVisible();
  const text = await page.locator("main").innerText();
  expect(text).not.toMatch(/avatar|permission/i);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBe(true);
}

test("S1 · two methods, Google current: methods with Remove, no link offer, sessions with End only on the other one, Sign out everywhere; organisms intact", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber).toBeVisible();
  await expect(chamber).toContainText("Access security");
  await expect(chamber.getByTestId("account-method")).toHaveCount(2);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(2);
  await expect(chamber.locator('[data-testid="account-method"][data-current="true"]')).toHaveAttribute("data-method-type", "GOOGLE_OIDC");
  await expect(chamber.getByTestId("account-method-email")).toHaveText("person@example.test");
  await expect(chamber.getByTestId("account-link-form")).toHaveCount(0);
  await expect(chamber.getByTestId("account-session")).toHaveCount(2);
  await expect(chamber.getByTestId("account-session-end")).toHaveCount(1);
  await expect(chamber.getByTestId("account-session-current")).toHaveText("ended by Log out");
  await expect(chamber.getByTestId("account-sign-out-everywhere")).toBeVisible();
  // nothing in the chamber is a role, an authority or a right
  expect(await chamber.innerText()).not.toMatch(/\b(role|owner|facilitator|contributor|authority|permission|capability|member)\b/i);
  await expectOrganismsIntact(page);
});

test("S2 · Remove a method that is not the current one → the typed unlink, committed, the field re-read with one method and the provider offered again", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await chamber.locator(`[data-method-id="${M_LOCAL}"]`).getByTestId("account-method-remove").click();
  await expect(chamber.getByTestId("account-effect-committed")).toBeVisible();
  expect(w.requests).toEqual([`POST /auth/methods/${M_LOCAL}/unlink`]);
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(0);
  await expect(chamber.getByTestId("account-method-last")).toBeVisible();
  await expect(page).toHaveURL(/\/workspaces$/);
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Google");
});

test("S3 · Remove the method of the current session → the session ended on the server → the page leaves for /login (nothing assumed locally)", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces");
  await page.getByTestId("access-security-plane").locator(`[data-method-id="${M_GOOGLE}"]`).getByTestId("account-method-remove").click();
  await expect(page).toHaveURL(/\/login$/);
  expect(w.requests).toEqual([`POST /auth/methods/${M_GOOGLE}/unlink`]);
});

test("S4 · the server refuses (409 LAST_METHOD): the verbatim reason on the effect surface, the method list unchanged, no navigation", async ({ page }) => {
  const w = world();
  await purple(page, w, { unlink: { status: 409, body: { kind: "denied", reasonCode: "LAST_METHOD" } } });
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await chamber.locator(`[data-method-id="${M_LOCAL}"]`).getByTestId("account-method-remove").click();
  await expect(chamber.getByTestId("account-effect-reason")).toHaveText("LAST_METHOD");
  await expect(chamber.locator('[data-testid="command-outcome"]')).toHaveAttribute("data-outcome", "denied");
  await expect(chamber.getByTestId("account-method")).toHaveCount(2);
  await expect(page).toHaveURL(/\/workspaces$/);
});

test("S5 · End another session → the typed revoke, committed, the list re-read; the current session keeps no End", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await chamber.getByTestId("account-session-end").click();
  await expect(chamber.getByTestId("account-effect-committed")).toBeVisible();
  expect(w.requests).toEqual([`POST /auth/sessions/${S_OLD}/revoke`]);
  await expect(chamber.getByTestId("account-session")).toHaveCount(1);
  await expect(chamber.getByTestId("account-session-end")).toHaveCount(0);
  await expect(chamber.getByTestId("account-session-current")).toBeVisible();
  await expect(chamber).toContainText("ends this session");
});

test("S6 · Sign out everywhere → the typed logout-all → /login", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces");
  await page.getByTestId("account-sign-out-everywhere").click();
  await expect(page).toHaveURL(/\/login$/);
  expect(w.requests).toEqual(["POST /auth/logout-all"]);
});

test("S7 · a lost response is an UNKNOWN consequence: network failure named, no success, the field re-read", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.route(`${API}/auth/sessions/*/revoke`, (route) => route.abort("connectionrefused"));
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await chamber.getByTestId("account-session-end").click();
  await expect(chamber.locator('[data-testid="command-outcome"]')).toHaveAttribute("data-outcome", "network_failure");
  await expect(chamber.getByTestId("account-effect-reason")).toHaveText("NETWORK_FAILURE");
  await expect(chamber.getByTestId("account-session")).toHaveCount(2);
});

test("S8 · GOOGLE_BOOTSTRAP: a bootstrapped identity is its own principal — its own name and email, one provider method, no Remove, the last-method note, no offer", async ({ page }) => {
  const w = world({
    me: { kind: "ok", userId: USER_B },
    identity: { kind: "ok", userId: USER_B, displayName: "Provider Person", canonicalEmail: "person@example.test" },
    methods: [{ ...GOOGLE, methodId: "eeeeeeee-2222-4222-8222-222222222222" }],
    sessions: [session(S_CUR, true, "GOOGLE_OIDC")],
  });
  await purple(page, w);
  await page.goto("/workspaces");
  await expect(page.getByTestId("identity-panel-name")).toHaveText("Provider Person");
  await expect(page.getByTestId("identity-panel-email")).toHaveText("person@example.test");
  await expect(page.getByTestId("identity-panel-method")).toHaveText("Google");
  await expect(page.getByTestId("identity-user-id")).toHaveText(USER_B);
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-method")).toHaveCount(1);
  await expect(chamber.getByTestId("account-method-remove")).toHaveCount(0);
  await expect(chamber.getByTestId("account-method-last")).toBeVisible();
  await expect(chamber.getByTestId("account-link-form")).toHaveCount(0);
  await expect(chamber.getByTestId("account-session")).toHaveCount(1);
  await expect(chamber.getByTestId("account-session-end")).toHaveCount(0);
  expect(await page.locator("main").innerText()).not.toContain("tobi");
});

test("S9 · a local-only identity is offered the configured provider: a POST form to the typed link start with the page-owned return target; no fetch is made", async ({ page }) => {
  const w = world({ methods: [LOCAL], sessions: [session(S_CUR, true, "LOCAL_PASSWORD")] });
  await purple(page, w);
  await page.goto("/workspaces");
  const form = page.getByTestId("access-security-plane").getByTestId("account-link-form");
  await expect(form).toHaveAttribute("method", "POST");
  await expect(form).toHaveAttribute("action", `${API}/auth/oidc/google/link/start?next=%2Fworkspaces`);
  await expect(form.getByTestId("account-link-google")).toHaveText("Add Google");
  await expect(form).not.toContainText("test provider");
  expect(w.requests).toEqual([]);
});

test("S10 · the ?link= result: ok as a status in the chamber, collision as an alert, an unknown word renders nothing; the field is otherwise unchanged", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.goto("/workspaces?link=ok");
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("link-result")).toHaveAttribute("role", "status");
  await expect(chamber.getByTestId("link-result")).toHaveAttribute("data-settled", "committed");
  await expect(chamber.getByTestId("link-result")).toContainText("now linked to your nquiry identity");
  await expectOrganismsIntact(page);
  await page.goto("/workspaces?link=collision");
  await expect(chamber.getByTestId("link-result")).toHaveAttribute("role", "alert");
  await expect(chamber.getByTestId("link-result")).toContainText("different nquiry identity");
  await page.goto("/workspaces?link=linked");
  await expect(chamber.getByTestId("link-result")).toHaveCount(0);
});

test("S11 · failed relation reads: 'could not be read', no control; the identity presentation stays", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.route(`${API}/auth/methods`, (route) => route.fulfill({ status: 502, contentType: "text/html", body: "<html>bad gateway</html>" }));
  await page.route(`${API}/auth/sessions`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  await expect(chamber.getByTestId("account-methods-unknown")).toBeVisible();
  await expect(chamber.getByTestId("account-sessions-unknown")).toBeVisible();
  await expect(chamber.locator("button")).toHaveCount(0);
  await expect(page.getByTestId("identity-panel-name")).toHaveText("tobi");
});

test("S12 · no chamber before the /auth/me verdict; an unauthenticated visitor never sees it", async ({ page }) => {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.goto("/workspaces");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByTestId("access-security-plane")).toHaveCount(0);
});

// --- AUTH/CYAN-ACCOUNT-02 ------------------------------------------------------------------------------------------

test("S13 · Change password: confirm must agree locally; the typed rotation; committed; the sessions re-read; the form cleared", async ({ page }) => {
  const w = world({ sessions: [session(S_OLD, false, "LOCAL_PASSWORD"), session(S_CUR, true, "LOCAL_PASSWORD")] });
  await purple(page, w);
  let sent: unknown = null;
  await page.route(`${API}/auth/password/change`, async (route) => {
    sent = route.request().postDataJSON();
    w.sessions = w.sessions.filter((s) => (s as { current: boolean }).current);
    await route.fulfill({ json: { kind: "ok", sessionsRevoked: 1 } });
  });
  await page.goto("/workspaces");
  const form = page.getByTestId("access-security-plane").getByTestId("account-password-form");
  await expect(form).toBeVisible();
  await form.getByTestId("account-current-password").fill("old pass");
  await form.getByTestId("account-new-password").fill("new passphrase 1");
  await form.getByTestId("account-confirm-password").fill("new passphrase 2");
  await expect(form.getByTestId("account-password-mismatch")).toBeVisible();
  await expect(form.getByTestId("account-password-submit")).toBeDisabled();
  expect(sent).toBeNull();
  await form.getByTestId("account-confirm-password").fill("new passphrase 1");
  await expect(form.getByTestId("account-password-mismatch")).toHaveCount(0);
  await form.getByTestId("account-password-submit").click();
  await expect(page.getByTestId("access-security-plane").getByTestId("account-effect-committed")).toBeVisible();
  expect(sent).toEqual({ currentPassword: "old pass", newPassword: "new passphrase 1" });
  await expect(page.getByTestId("access-security-plane").getByTestId("account-session")).toHaveCount(1);
  await expect(form.getByTestId("account-current-password")).toHaveValue("");
  await expect(form.getByTestId("account-new-password")).toHaveValue("");
  await expect(page).toHaveURL(/\/workspaces$/);
});

test("S14 · a wrong current password is the server's refusal on the surface; a provider-only identity has no form", async ({ page }) => {
  const w = world();
  await purple(page, w);
  await page.route(`${API}/auth/password/change`, (route) => route.fulfill({ status: 403, json: { kind: "denied", reasonCode: "CURRENT_PASSWORD_INVALID" } }));
  await page.goto("/workspaces");
  const chamber = page.getByTestId("access-security-plane");
  const form = chamber.getByTestId("account-password-form");
  await form.getByTestId("account-current-password").fill("wrong");
  await form.getByTestId("account-new-password").fill("new passphrase 1");
  await form.getByTestId("account-confirm-password").fill("new passphrase 1");
  await form.getByTestId("account-password-submit").click();
  await expect(chamber.getByTestId("account-effect-reason")).toHaveText("CURRENT_PASSWORD_INVALID");
  await expect(page).toHaveURL(/\/workspaces$/);
  // a bootstrapped (provider-only) identity: no password form at all
  const b = world({ me: { kind: "ok", userId: USER_B }, identity: { kind: "ok", userId: USER_B, displayName: "Provider Person", canonicalEmail: "person@example.test" }, methods: [{ ...GOOGLE, methodId: "eeeeeeee-2222-4222-8222-222222222222" }], sessions: [session(S_CUR, true, "GOOGLE_OIDC")] });
  await purple(page, b);
  await page.goto("/workspaces");
  await expect(page.getByTestId("access-security-plane")).toBeVisible();
  await expect(page.getByTestId("account-password-form")).toHaveCount(0);
});

test("S15 · the login lockout boundary (429 RATE_LIMITED) is presented as a pause, not as wrong credentials", async ({ page }) => {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
  await page.route(`${API}/auth/providers`, (route) => route.fulfill({ json: PROVIDERS }));
  await page.route(`${API}/auth/login`, (route) => route.fulfill({ status: 429, json: { kind: "denied", reasonCode: "RATE_LIMITED" } }));
  await page.goto("/login");
  await page.getByTestId("login-email").fill("person@nonproof.test");
  await page.getByTestId("login-password").fill("pw");
  await page.getByTestId("login-submit").click();
  const alert = page.getByTestId("login-error");
  await expect(alert).toContainText("Too many attempts");
  await expect(alert).not.toContainText("Incorrect");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByTestId("login-submit")).toBeEnabled();
});
