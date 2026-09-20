/**
 * Real Playwright E2E proof for PKG-28's own Session-view route,
 * against a real Chromium browser + a real running Next.js dev
 * server. `page.route()` intercepts the browser's own real network
 * request (issued by `lib/api/client.ts`'s `fetchSessionView`, called
 * from `SessionViewContainer`'s `useEffect`) at the network layer --
 * standard, industry-normal practice for testing a frontend against a
 * backend contract that has not shipped the corresponding route yet
 * (`apps/api` still only exposes `/healthz`). This is NOT a
 * test-only code path in `apps/web` itself: no shipped component or
 * module branches on being "in a test."
 */
import { expect, test } from "@playwright/test";

const WORKSPACE_ID = "ws-real";
const SESSION_ID = "sess-real";
// Scoped to the API's own origin (`lib/api/client.ts`'s default
// `http://localhost:8000`), not just the path -- the page's own
// navigation URL (`http://localhost:3000/workspaces/.../sessions/...`)
// shares the same path shape, so an origin-unscoped glob would
// intercept the top-level page navigation itself, not only the
// client's own background fetch.
const ROUTE_PATTERN = "http://localhost:8000/workspaces/**/sessions/**";
const PAGE_PATH = `/workspaces/${WORKSPACE_ID}/sessions/${SESSION_ID}`;

const OK_BODY = {
  kind: "ok",
  data: {
    workspaceId: WORKSPACE_ID,
    challenge: { challengeId: "c-1", workspaceId: WORKSPACE_ID, title: "Reduce onboarding drop-off", description: null },
    session: { sessionId: SESSION_ID, challengeId: "c-1", workspaceId: WORKSPACE_ID, state: "QUESTION_CAPTURE" },
    burst: {
      burstId: "b-1",
      sessionId: SESSION_ID,
      state: "ACTIVE",
      mode: "HUMAN_ONLY",
      questions: [
        { questionId: "q-1", originalText: "Why do users abandon step 3?", origin: "HUMAN" },
        { questionId: "q-2", originalText: "Is step 3 latency the driver?", origin: "AI" },
      ],
    },
    decision: null,
    aiRecommendation: null,
  },
};

test("renders the ok Session view with Workspace, Challenge, Session state, Burst state, HUMAN_ONLY indicator, and origin-marked questions", async ({
  page,
}) => {
  await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: OK_BODY }));

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("workspace-badge")).toContainText(WORKSPACE_ID);
  await expect(page.getByTestId("challenge-summary")).toContainText("Reduce onboarding drop-off");
  await expect(page.getByTestId("session-state-badge")).toContainText("QUESTION_CAPTURE");
  await expect(page.getByTestId("burst-state")).toContainText("ACTIVE");
  await expect(page.getByTestId("burst-human-only-indicator")).toBeVisible();
  const items = page.getByTestId("question-item");
  await expect(items).toHaveCount(2);
  await expect(items.nth(0)).toContainText("Why do users abandon step 3?");
  await expect(items.nth(0)).toContainText("HUMAN");
  await expect(items.nth(1)).toContainText("Is step 3 latency the driver?");
  await expect(items.nth(1).getByTestId("question-ai-derived-label")).toContainText("DERIVED / PROPOSAL");
});

test("shows the frozen raw-set indicator once the Burst is COMPLETED", async ({ page }) => {
  const body = { ...OK_BODY, data: { ...OK_BODY.data, burst: { ...OK_BODY.data.burst, state: "COMPLETED" } } };
  await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: body }));

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("burst-frozen-indicator")).toBeVisible();
});

test("renders the denied surface for a DENY/REQUIRE/ESCALATE server verdict, never the ok view", async ({ page }) => {
  await page.route(ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "denied", result: "REQUIRE", reasonCode: "BND-017-dependency-blocked" } }),
  );

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("denied-banner")).toBeVisible();
  await expect(page.getByTestId("denied-result")).toContainText("REQUIRE");
  await expect(page.getByTestId("denied-reason-code")).toContainText("BND-017-dependency-blocked");
  await expect(page.getByTestId("session-view-ok")).toHaveCount(0);
});

test("renders the INDETERMINATE surface with no retry control at all", async ({ page }) => {
  await page.route(ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "indeterminate", blockedTargetRef: "recovery:target-abc" } }),
  );

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("indeterminate-banner")).toBeVisible();
  await expect(page.getByTestId("indeterminate-blocked-target-ref")).toContainText("recovery:target-abc");
});

test("mandatory attack: no hidden/disabled action element exists in the DOM for any response shape", async ({ page }) => {
  // Scoped to `main` -- Next.js's own dev-mode overlay (its "Open
  // Next.js Dev Tools" / issues-badge chrome) legitimately contains
  // `<button>` elements outside our app's own root, which are not part
  // of shipped `apps/web` output at all; the proof is about THIS
  // package's own rendered content.
  const appRoot = page.locator("main");
  for (const body of [
    OK_BODY,
    { kind: "denied", result: "DENY", reasonCode: "x" },
    { kind: "indeterminate", blockedTargetRef: "y" },
  ]) {
    await page.unroute(ROUTE_PATTERN).catch(() => {});
    await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: body }));
    await page.goto(PAGE_PATH);
    await appRoot.locator(
      '[data-testid^="session-view-"], [data-testid="denied-banner"], [data-testid="indeterminate-banner"]',
    ).waitFor();
    const actionElementCount = await appRoot.locator("button, input, form, [role='button']").count();
    expect(actionElementCount).toBe(0);
  }
});

test("mandatory attack: forged Workspace in client -- rendering is a pure function of the server's response, never the URL", async ({
  page,
}) => {
  const forgedWorkspaceInResponse = "ws-server-authoritative";
  const body = { ...OK_BODY, data: { ...OK_BODY.data, workspaceId: forgedWorkspaceInResponse } };
  await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: body }));

  await page.goto(`/workspaces/ws-attacker-claimed/sessions/${SESSION_ID}`);

  await expect(page.getByTestId("workspace-badge")).toContainText(forgedWorkspaceInResponse);
  await expect(page.getByTestId("workspace-badge")).not.toContainText("ws-attacker-claimed");
});

test("mandatory attack: attempt AI control during an ACTIVE Burst -- no AI-control element renders, only passive origin labels", async ({
  page,
}) => {
  await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: OK_BODY }));

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("burst-state")).toContainText("ACTIVE");
  const appRoot = page.locator("main");
  await expect(appRoot.locator("button, input, form, [role='button']")).toHaveCount(0);
  await expect(appRoot.getByText(/start analysis/i)).toHaveCount(0);
  await expect(appRoot.getByText(/run ai/i)).toHaveCount(0);
  await expect(appRoot.getByText(/trigger/i)).toHaveCount(0);
});

test("mandatory attack: manipulate client capability flag -- no capability-flag-shaped field exists in the rendered response at all", async ({
  page,
}) => {
  const bodyWithInjectedCapabilityFlag = {
    ...OK_BODY,
    canRetry: true,
    capabilities: { admin: true },
    data: { ...OK_BODY.data, canOverride: true },
  };
  await page.route(ROUTE_PATTERN, (route) => route.fulfill({ json: bodyWithInjectedCapabilityFlag }));

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("session-view-ok")).toBeVisible();
  const bodyText = await page.locator("body").innerText();
  expect(bodyText).not.toMatch(/canRetry|capabilities|canOverride|admin/i);
});

// Retrofit (external review): a failed fetch previously left the page
// stuck on "Loading..." forever, invisible to the viewer -- this
// proves the real fix (SessionViewContainer.tsx's `.catch()` +
// NetworkErrorBanner), not merely that the happy path still works.
test("network failure renders a visible error state instead of hanging on Loading forever", async ({ page }) => {
  await page.route(ROUTE_PATTERN, (route) => route.abort());

  await page.goto(PAGE_PATH);

  await expect(page.getByTestId("network-error-banner")).toBeVisible();
  await expect(page.getByTestId("session-view-loading")).toHaveCount(0);
});
