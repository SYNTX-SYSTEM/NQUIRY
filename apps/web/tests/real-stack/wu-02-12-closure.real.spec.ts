/**
 * F02 WU-02.12 REAL-STACK PROOF — Field-closure repairs.
 *
 * Real browser -> real web app -> real FastAPI -> real local auth -> real
 * PostgreSQL -> real governed Commands. Nothing is mocked. The only
 * out-of-band step is HD-3 identity provisioning (identity rows only).
 * Governed setup steps that are not under test here (membership, Challenge,
 * grants, Session) are issued as real cross-origin `fetch` calls from the
 * page with the real session cookie: the same routes and Commands the UI
 * uses, no raw inserts.
 *
 * FBR-B: a reused Idempotency-Key with a different payload, or on another
 *        Session, is `rejected`, and canonical state is unchanged.
 * FBR-C: server verdicts reach the UI as verdicts: `rejected` renders as a
 *        rejection (not as a network error) on the F01 Workspace page and on
 *        the PKG-28/29 decision view; framework validation is `rejected`.
 */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { provisionIdentity, type DevIdentity } from "./identities";

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";

async function openAs(browser: Browser, who: DevIdentity): Promise<Page> {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/login");
  await page.getByLabel("Email").fill(who.email);
  await page.getByLabel("Password").fill(who.password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/workspaces/);
  return page;
}

type ApiResult = { status: number; body: Record<string, unknown> };

async function api(page: Page, pathname: string, body: unknown, key: string | null = null): Promise<ApiResult> {
  return page.evaluate(
    async ({ url, body, key }) => {
      const headers: Record<string, string> = { "Content-Type": "application/json", Accept: "application/json" };
      headers["Idempotency-Key"] = key ?? crypto.randomUUID();
      const response = await fetch(url, { method: "POST", credentials: "include", headers, body: JSON.stringify(body) });
      return { status: response.status, body: (await response.json()) as Record<string, unknown> };
    },
    { url: `${API}${pathname}`, body, key },
  );
}

test("WU-02.12: idempotency identity and outcome vocabulary hold on the real stack", async ({ browser }) => {
  const owner = provisionIdentity("Owner");
  const facilitator = provisionIdentity("Facilitator");

  // --- Governance root founds a Workspace through the UI ---
  const a = await openAs(browser, owner);
  await a.getByLabel("Workspace name").fill("Closure inquiry");
  await a.getByRole("button", { name: "Create Workspace" }).click();
  await expect(a.getByRole("heading", { level: 1, name: "Closure inquiry" })).toBeVisible();
  const ws = a.url().split("/workspaces/")[1];

  // --- Governed setup over the real API (same routes the UI uses) ---
  const added = await api(a, `/workspaces/${ws}/members`, { userId: facilitator.userId, role: "Facilitator" });
  expect(added.body.kind).toBe("ok");
  const b = await openAs(browser, facilitator);
  const challenge = await api(b, `/workspaces/${ws}/challenges`, { title: "Why do trials stall?" });
  expect(challenge.body.kind).toBe("committed");
  const cid = challenge.body.challengeId as string;
  const grant = (scopeType: string, scopeId: string) =>
    api(a, `/workspaces/${ws}/authority-bindings`, {
      humanUserId: facilitator.userId,
      authorityClass: "SESSION_CONTROL_RIGHT",
      scopeType,
      scopeId,
    });
  expect((await grant("CHALLENGE", cid)).body.kind).toBe("committed");
  const sessions: string[] = [];
  for (let i = 0; i < 2; i += 1) {
    const created = await api(b, `/workspaces/${ws}/challenges/${cid}/sessions`, {});
    expect(created.body.kind).toBe("committed");
    sessions.push(created.body.sessionId as string);
    expect((await grant("SESSION", created.body.sessionId as string)).body.kind).toBe("committed");
  }
  const [s1, s2] = sessions;

  // --- FBR-B: one key = one logical Command ---
  const key = crypto.randomUUID();
  const setup = `/workspaces/${ws}/sessions/${s1}/transitions/begin-setup`;
  const first = await api(b, setup, { expectedVersion: 1 }, key);
  expect(first.body).toMatchObject({ kind: "committed", replayed: false });
  const retry = await api(b, setup, { expectedVersion: 1 }, key);
  expect(retry.body).toMatchObject({ kind: "committed", replayed: true });

  const changedPayload = await api(b, setup, { expectedVersion: 2 }, key);
  expect(changedPayload.status).toBe(400);
  expect(changedPayload.body).toEqual({ kind: "rejected", reasonCode: "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND" });

  const otherSession = await api(b, `/workspaces/${ws}/sessions/${s2}/transitions/begin-setup`, { expectedVersion: 1 }, key);
  expect(otherSession.body).toEqual({ kind: "rejected", reasonCode: "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_COMMAND" });

  // Canonical state, as the UI renders it from the server.
  await b.goto(`/workspaces/${ws}/sessions/${s1}`);
  await expect(b.getByTestId("session-state")).toHaveText(/SETUP/);
  await b.goto(`/workspaces/${ws}/sessions/${s2}`);
  await expect(b.getByTestId("session-state")).toHaveText(/DRAFT/);

  // --- FBR-C: framework validation is `rejected` in the envelope shape ---
  const malformed = await api(b, `/workspaces/${ws}/challenges`, { description: "no title" });
  expect(malformed.status).toBe(400);
  expect(malformed.body).toEqual({ kind: "rejected", reasonCode: "MALFORMED_REQUEST_BODY" });
  const badLogin = await api(b, `/auth/login`, { email: "x@y.z" });
  expect(badLogin.body).toEqual({ kind: "rejected", reasonCode: "MALFORMED_REQUEST_BODY" });

  // --- FBR-C: `rejected` renders as a verdict, not as a network error ---
  await a.goto("/workspaces/not-a-uuid");
  await expect(a.getByTestId("orientation-rejected")).toBeVisible();
  await expect(a.getByTestId("orientation-error")).toHaveCount(0);

  await b.goto(`/workspaces/${ws}/sessions/not-a-uuid/decision`);
  await expect(b.getByTestId("session-view-rejected")).toBeVisible();
  await expect(b.getByText("Unable to load this Session.")).toHaveCount(0);
});
