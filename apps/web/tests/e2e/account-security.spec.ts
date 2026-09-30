/**
 * WU-AUTH-04 MOCKED-browser proof of the account security surface
 * (`app/account/security/page.tsx`). `page.route()` fulfils the API: this
 * proves what the page projects and sends, not the runtime (20 §12).
 */
import { expect, test, type Page } from "@playwright/test";

const SESSIONS_ROUTE = "http://localhost:8000/auth/sessions";
const LOGOUT_ALL_ROUTE = "http://localhost:8000/auth/logout-all";
const REVOKE_ROUTE = "http://localhost:8000/auth/sessions/*/revoke";
const ME_ROUTE = "http://localhost:8000/auth/me";

const CURRENT = {
  sessionId: "11111111-1111-4111-8111-111111111111",
  issuedAt: "2030-01-01T08:00:00+00:00",
  expiresAt: "2030-01-01T20:00:00+00:00",
  current: true,
  methodType: "LOCAL_PASSWORD",
};
const OTHER = {
  sessionId: "22222222-2222-4222-8222-222222222222",
  issuedAt: "2030-01-01T06:00:00+00:00",
  expiresAt: "2030-01-01T18:00:00+00:00",
  current: false,
  methodType: "LOCAL_PASSWORD",
};

async function noSessionEverywhereElse(page: Page) {
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );
}

test("lists the caller's sessions and marks the current one", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [OTHER, CURRENT] } }));

  await page.goto("/account/security");

  await expect(page.getByRole("heading", { level: 1, name: "Account security" })).toBeVisible();
  await expect(page.getByTestId("session-item")).toHaveCount(2);
  await expect(page.getByTestId("session-current")).toHaveCount(1);
  await expect(page.getByTestId("session-item").nth(1)).toContainText("This browser");
  await expect(page.getByTestId("session-item").first()).toContainText("Email and password");
});

test("without a session the page goes to /login and shows no session data", async ({ page }) => {
  await noSessionEverywhereElse(page);
  await page.route(SESSIONS_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );

  await page.goto("/account/security");

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByTestId("session-item")).toHaveCount(0);
});

test("ending another session calls the server and re-reads the list", async ({ page }) => {
  let revoked = false;
  const revokeCalls: string[] = [];
  await page.route(SESSIONS_ROUTE, (route) =>
    route.fulfill({ json: { kind: "ok", sessions: revoked ? [CURRENT] : [OTHER, CURRENT] } }),
  );
  await page.route(REVOKE_ROUTE, (route) => {
    revokeCalls.push(`${route.request().method()} ${new URL(route.request().url()).pathname}`);
    revoked = true;
    return route.fulfill({ json: { kind: "ok" } });
  });

  await page.goto("/account/security");
  await page.getByTestId("session-revoke").first().click();

  await expect(page.getByTestId("sessions-notice")).toHaveText("The session was ended.");
  await expect(page.getByTestId("session-item")).toHaveCount(1);
  expect(revokeCalls).toEqual([`POST /auth/sessions/${OTHER.sessionId}/revoke`]);
});

test("a refused revocation is shown as an error and the list is the server's, not a local guess", async ({
  page,
}) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [OTHER, CURRENT] } }));
  await page.route(REVOKE_ROUTE, (route) =>
    route.fulfill({ status: 404, json: { kind: "denied", reasonCode: "SESSION_NOT_FOUND" } }),
  );

  await page.goto("/account/security");
  await page.getByTestId("session-revoke").first().click();

  await expect(page.getByTestId("sessions-error")).toBeVisible();
  await expect(page.getByTestId("sessions-notice")).toHaveCount(0);
  await expect(page.getByTestId("session-item")).toHaveCount(2);
});

test("ending the current session leads to /login once the server no longer knows it", async ({ page }) => {
  let revoked = false;
  await noSessionEverywhereElse(page);
  await page.route(SESSIONS_ROUTE, (route) =>
    revoked
      ? route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } })
      : route.fulfill({ json: { kind: "ok", sessions: [CURRENT] } }),
  );
  await page.route(REVOKE_ROUTE, (route) => {
    revoked = true;
    return route.fulfill({ json: { kind: "ok" } });
  });

  await page.goto("/account/security");
  await page.getByTestId("session-revoke").click();

  await expect(page).toHaveURL(/\/login$/);
});

test("log out of all sessions posts once and leaves for /login only after the server's ok", async ({ page }) => {
  const calls: string[] = [];
  await noSessionEverywhereElse(page);
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [OTHER, CURRENT] } }));
  await page.route(LOGOUT_ALL_ROUTE, (route) => {
    calls.push(route.request().method());
    return route.fulfill({ json: { kind: "ok", revokedSessions: 2 } });
  });

  await page.goto("/account/security");
  await page.getByTestId("logout-all").click();

  await expect(page).toHaveURL(/\/login$/);
  expect(calls).toEqual(["POST"]);
});

test("an unreachable server is reported as unknown, never as an empty list", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.abort());

  await page.goto("/account/security");

  await expect(page.getByTestId("sessions-unreachable")).toBeVisible();
  await expect(page.getByTestId("session-list")).toHaveCount(0);
  await expect(page.getByTestId("logout-all")).toBeDisabled();
});

test("the surface is keyboard-operable and carries no token in the page", async ({ page }) => {
  await page.route(SESSIONS_ROUTE, (route) => route.fulfill({ json: { kind: "ok", sessions: [CURRENT] } }));

  await page.goto("/account/security");
  await expect(page.getByTestId("session-item")).toHaveCount(1);

  await page.getByTestId("session-revoke").focus();
  await expect(page.getByTestId("session-revoke")).toBeFocused();
  await expect(page.getByTestId("session-revoke")).toHaveAccessibleName("End this session");
  await expect(page.getByTestId("logout-all")).toHaveAccessibleName("Log out of all sessions");
  const storage = await page.evaluate(() => JSON.stringify([{ ...localStorage }, { ...sessionStorage }, document.cookie]));
  expect(storage).toBe('[{},{},""]');
});
