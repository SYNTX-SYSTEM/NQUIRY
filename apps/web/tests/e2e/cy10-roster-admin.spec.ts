/**
 * AUTH/CYAN-ACCOUNT-02 browser proof (mocked lane): membership administration in the Members chamber of the
 * Workspace field — Remove (05 GOV-003) and Change role (GOV-004) — rendered ONLY from the server's overview
 * capabilities and the per-member `administrable` flag (never from a role); effects through the page's effect
 * field; refusals as the server's reason; the roster re-read; nothing for a member without the capability;
 * desktop + Pixel 7.
 */
import { expect, test, type Page, type Request } from "@playwright/test";

const API = "http://localhost:8000";
const OWNER = "7dd6e767-1111-4111-8111-111111111111";
const FAC = "aaaaaaaa-2222-4222-8222-222222222222";
const CON = "bbbbbbbb-3333-4333-8333-333333333333";
const WS = "11111111-1111-4111-8111-111111111111";

type Member = { userId: string; name: string; email: string; role: string; administrable: boolean };
type World = { members: Member[]; root: boolean; requests: string[] };
const members = (): Member[] => [
  { userId: OWNER, name: "Owner Person", email: "owner@example.test", role: "Owner", administrable: false },
  { userId: FAC, name: "Fay Facilitator", email: "fay@example.test", role: "Facilitator", administrable: true },
  { userId: CON, name: "Con Tributor", email: "con@example.test", role: "Contributor", administrable: true },
];

async function world(page: Page, w: World, refusal?: { body: unknown }): Promise<void> {
  const cap = (available: boolean) => (available ? { available: true, reasonCode: null, reason: null } : { available: false, reasonCode: "NOT_GOVERNANCE_ROOT", reason: "Governance root only." });
  await page.route(`${API}/auth/me`, (r) => r.fulfill({ json: { kind: "ok", userId: w.root ? OWNER : CON } }));
  await page.route(`${API}/workspaces/${WS}`, (r) =>
    r.fulfill({ json: { kind: "ok", workspace: { workspaceId: WS, name: "Roster Field", ownerId: OWNER, createdAt: "2026-01-01T00:00:00Z" }, role: w.root ? "Owner" : "Contributor", heldAuthorityClasses: w.root ? ["WORKSPACE_GOVERNANCE_RIGHT"] : [], authorized: true, governanceCapable: w.root } }),
  );
  await page.route(`${API}/workspaces/${WS}/overview`, (r) =>
    r.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: WS, name: "Roster Field", governedFounding: true },
        viewer: { userId: w.root ? OWNER : CON, role: w.root ? "Owner" : "Contributor", isGovernanceRoot: w.root },
        members: w.members,
        challenges: [],
        capabilities: { createChallenge: cap(false), addMember: cap(w.root), revokeMembership: cap(w.root), changeMemberRole: cap(w.root) },
      },
    }),
  );
  const record = (req: Request) => w.requests.push(`${req.method()} ${new URL(req.url()).pathname} ${req.postData() ?? ""}`.trim());
  await page.route(`${API}/workspaces/${WS}/members/*/revoke`, (r) => {
    record(r.request());
    if (refusal) return r.fulfill({ json: refusal.body });
    const id = new URL(r.request().url()).pathname.split("/")[4];
    w.members = w.members.filter((m) => m.userId !== id);
    return r.fulfill({ json: { kind: "ok" } });
  });
  await page.route(`${API}/workspaces/${WS}/members/*/role`, (r) => {
    record(r.request());
    if (refusal) return r.fulfill({ json: refusal.body });
    const id = new URL(r.request().url()).pathname.split("/")[4];
    const role = (r.request().postDataJSON() as { role: string }).role;
    w.members = w.members.map((m) => (m.userId === id ? { ...m, role } : m));
    return r.fulfill({ json: { kind: "ok" } });
  });
}

test("R1 · the root sees administration for administrable members only — never itself, never the root; the chamber's roster and Add member stay", async ({ page }) => {
  const w: World = { members: members(), root: true, requests: [] };
  await world(page, w);
  await page.goto(`/workspaces/${WS}`);
  const admin = page.getByTestId("roster-admin");
  await expect(admin).toBeVisible();
  await expect(admin.getByTestId("roster-admin-row")).toHaveCount(2);
  await expect(admin.locator(`[data-user="${OWNER}"]`)).toHaveCount(0);
  await expect(admin.getByTestId("roster-remove")).toHaveCount(2);
  await expect(admin.getByTestId("roster-change-role")).toHaveCount(2);
  // the role select offers only the other role (no no-op change)
  const facRow = admin.locator(`[data-user="${FAC}"]`);
  await expect(facRow.getByTestId("roster-role-select").locator("option")).toHaveText(["Contributor"]);
  await expect(page.getByTestId("members-list")).toBeVisible();
  await expect(page.getByTestId("add-member-form")).toBeVisible();
  expect(await admin.innerText()).not.toMatch(/\bpermission\b|\bcapability\b/i);
});

test("R2 · Remove → the typed revoke, committed, roster re-read without the member", async ({ page }) => {
  const w: World = { members: members(), root: true, requests: [] };
  await world(page, w);
  await page.goto(`/workspaces/${WS}`);
  const admin = page.getByTestId("roster-admin");
  await admin.locator(`[data-user="${CON}"]`).getByTestId("roster-remove").click();
  await expect(admin.getByTestId("roster-admin-success")).toBeVisible();
  expect(w.requests).toEqual([`POST /workspaces/${WS}/members/${CON}/revoke`]);
  await expect(admin.getByTestId("roster-admin-row")).toHaveCount(1);
  await expect(page.getByTestId("members-list").locator(`[data-user="${CON}"]`)).toHaveCount(0);
});

test("R3 · Change role → the typed role command with the chosen role, committed, the roster shows the new role", async ({ page }) => {
  const w: World = { members: members(), root: true, requests: [] };
  await world(page, w);
  await page.goto(`/workspaces/${WS}`);
  const admin = page.getByTestId("roster-admin");
  await admin.locator(`[data-user="${CON}"]`).getByTestId("roster-change-role").click();
  await expect(admin.getByTestId("roster-admin-success")).toBeVisible();
  expect(w.requests).toEqual([`POST /workspaces/${WS}/members/${CON}/role {"role":"Facilitator"}`]);
  await expect(admin.locator(`[data-user="${CON}"]`)).toHaveAttribute("data-role", "Facilitator");
  await expect(page.getByTestId("members-list").locator(`[data-user="${CON}"] [data-relation-kind="facilitator"]`)).toHaveCount(1);
});

test("R4 · the server refuses (GOVERNANCE_ROOT_NOT_REMOVABLE): the verbatim reason, roster unchanged", async ({ page }) => {
  const w: World = { members: members(), root: true, requests: [] };
  await world(page, w, { body: { kind: "denied", result: "DENY", reasonCode: "GOVERNANCE_ROOT_NOT_REMOVABLE" } });
  await page.goto(`/workspaces/${WS}`);
  const admin = page.getByTestId("roster-admin");
  await admin.locator(`[data-user="${FAC}"]`).getByTestId("roster-remove").click();
  await expect(admin.getByTestId("roster-admin-error")).toHaveText("GOVERNANCE_ROOT_NOT_REMOVABLE");
  await expect(admin.locator('[data-testid="command-outcome"]')).toHaveAttribute("data-outcome", "denied");
  await expect(admin.getByTestId("roster-admin-row")).toHaveCount(2);
});

test("R5 · a member without the capability sees no administration at all (and no control anywhere for it)", async ({ page }) => {
  const w: World = { members: members(), root: false, requests: [] };
  await world(page, w);
  await page.goto(`/workspaces/${WS}`);
  await expect(page.getByTestId("members-list")).toBeVisible();
  await expect(page.getByTestId("roster-admin")).toHaveCount(0);
  await expect(page.getByTestId("roster-remove")).toHaveCount(0);
  await expect(page.getByTestId("add-member-form")).toHaveCount(0);
  expect(w.requests).toEqual([]);
});

test("R6 · an older producer without the capabilities or the flag → no administration (fail closed)", async ({ page }) => {
  const w: World = { members: members().map(({ administrable: _a, ...m }) => ({ ...m, administrable: undefined as unknown as boolean })), root: true, requests: [] };
  await world(page, w);
  await page.route(`${API}/workspaces/${WS}/overview`, (r) =>
    r.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: WS, name: "Roster Field", governedFounding: true },
        viewer: { userId: OWNER, role: "Owner", isGovernanceRoot: true },
        members: w.members.map(({ administrable: _a, ...m }) => m),
        challenges: [],
        capabilities: { createChallenge: { available: false, reasonCode: "NOT_FACILITATOR", reason: "x" }, addMember: { available: true, reasonCode: null, reason: null } },
      },
    }),
  );
  await page.goto(`/workspaces/${WS}`);
  await expect(page.getByTestId("add-member-form")).toBeVisible();
  await expect(page.getByTestId("roster-admin")).toHaveCount(0);
});
