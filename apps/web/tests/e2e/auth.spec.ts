/**
 * Real Playwright E2E proof for the local-login field
 * (`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`), against a
 * real Chromium browser + a real running Next.js dev server.
 * `page.route()` intercepts the browser's own real network requests to
 * `/auth/login`/`/auth/me`/`/auth/logout` -- identical technique
 * `session-view.spec.ts` already establishes for this codebase.
 *
 * `NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/`NEXT_PUBLIC_DEFAULT_SESSION_ID`
 * (`app/page.tsx`) are inlined into the running app at `next dev`
 * server START time -- whether they are set depends on which process
 * is actually listening on `:3000` when this suite runs (Playwright's
 * own `reuseExistingServer` may reuse an already-running real
 * `docker compose` `web` container, which DOES set them, instead of
 * starting a fresh one that would not). Tests that reach the
 * authenticated landing screen therefore mock BOTH possible
 * destinations -- the `/workspaces/**\/sessions/**` Session-view route
 * AND the F01 WU-01.9 `/workspaces` list route -- and accept EITHER
 * outcome, deterministic either way, rather than assuming one specific
 * process's own environment.
 */
import { expect, test } from "@playwright/test";

const LOGIN_ROUTE = "http://localhost:8000/auth/login";
const ME_ROUTE = "http://localhost:8000/auth/me";
const LOGOUT_ROUTE = "http://localhost:8000/auth/logout";
const SESSION_VIEW_ROUTE = "http://localhost:8000/workspaces/**/sessions/**";
const WORKSPACES_LIST_ROUTE = "http://localhost:8000/workspaces";
const MOCK_SESSION_VIEW_BODY = {
  kind: "ok",
  data: {
    workspaceId: "mock-ws",
    challenge: { challengeId: "c-1", workspaceId: "mock-ws", title: "Mock Challenge", description: null },
    session: { sessionId: "mock-sess", challengeId: "c-1", workspaceId: "mock-ws", state: "DRAFT" },
    burst: null,
    decision: null,
    aiRecommendation: null,
  },
};

test("root route redirects to /login when no session exists", async ({ page }) => {
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );

  await page.goto("/");

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByTestId("login-form")).toBeVisible();
});

test("wrong credentials show an error and do not navigate away from /login", async ({ page }) => {
  await page.route(LOGIN_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "INVALID_CREDENTIALS" } }),
  );

  await page.goto("/login");
  await page.getByTestId("login-email").fill("wrong@nonproof.test");
  await page.getByTestId("login-password").fill("wrong-password");
  await page.getByTestId("login-submit").click();

  await expect(page.getByTestId("login-error")).toBeVisible();
  await expect(page).toHaveURL(/\/login$/);
});

test("WU-02.12: a rejected (malformed) login is not reported as wrong credentials", async ({ page }) => {
  await page.route(LOGIN_ROUTE, (route) =>
    route.fulfill({ status: 400, json: { kind: "rejected", reasonCode: "MALFORMED_REQUEST_BODY" } }),
  );

  await page.goto("/login");
  await page.getByTestId("login-email").fill("someone@nonproof.test");
  await page.getByTestId("login-password").fill("any-password");
  await page.getByTestId("login-submit").click();

  await expect(page.getByTestId("login-error")).toContainText("The login request was invalid");
  await expect(page.getByTestId("login-error")).not.toContainText("Incorrect email or password");
  await expect(page).toHaveURL(/\/login$/);
});

test("correct credentials log in and reach either the Workspaces list or its configured default Session", async ({
  page,
}) => {
  await page.route(LOGIN_ROUTE, (route) =>
    route.fulfill({ status: 200, json: { kind: "ok", userId: "11111111-1111-1111-1111-111111111111" } }),
  );
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 200, json: { kind: "ok", userId: "11111111-1111-1111-1111-111111111111" } }),
  );
  await page.route(SESSION_VIEW_ROUTE, (route) => route.fulfill({ json: MOCK_SESSION_VIEW_BODY }));
  await page.route(WORKSPACES_LIST_ROUTE, (route) =>
    route.fulfill({ json: { kind: "ok", workspaces: [] } }),
  );

  await page.goto("/login");
  await page.getByTestId("login-email").fill("demo-owner@nonproof.test");
  await page.getByTestId("login-password").fill("nquiry-demo-2026");
  await page.getByTestId("login-submit").click();

  // Never lands back on /login -- login genuinely succeeded either way.
  await expect(page).not.toHaveURL(/\/login$/);
  await expect(
    page.getByTestId("workspaces-empty").or(page.getByTestId("session-view-ok")),
  ).toBeVisible();
});

test("logging out returns to /login, from either the Workspaces list or a redirected Session view", async ({
  page,
}) => {
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 200, json: { kind: "ok", userId: "22222222-2222-2222-2222-222222222222" } }),
  );
  await page.route(LOGOUT_ROUTE, (route) => route.fulfill({ status: 200, json: { kind: "ok" } }));
  await page.route(SESSION_VIEW_ROUTE, (route) => route.fulfill({ json: MOCK_SESSION_VIEW_BODY }));
  await page.route(WORKSPACES_LIST_ROUTE, (route) =>
    route.fulfill({ json: { kind: "ok", workspaces: [] } }),
  );

  await page.goto("/");
  const logoutButton = page.getByTestId("logout-button");
  await expect(logoutButton).toBeVisible();

  // Once logged out, a fresh `/auth/me` must be treated as denied --
  // otherwise a subsequent visit to `/` would immediately bounce right
  // back to the authenticated screen.
  await page.unroute(ME_ROUTE);
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );
  await logoutButton.click();

  await expect(page).toHaveURL(/\/login$/);
});

test("the login form never renders any pre-filled credential or capability field", async ({ page }) => {
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );

  await page.goto("/");

  await expect(page.getByTestId("login-email")).toHaveValue("");
  await expect(page.getByTestId("login-password")).toHaveValue("");
});
