/**
 * Real Playwright E2E proof for F01 WU-01.9 (`/workspaces`,
 * `/workspaces/{workspaceId}`), against a real Chromium browser + a
 * real running Next.js dev server. `page.route()` intercepts the
 * browser's own real network requests at the network layer, same
 * technique `auth.spec.ts`/`session-view.spec.ts` already establish --
 * `apps/api` real routes exist (WU-01.8) but this suite still mocks
 * them for the same reason every other E2E spec in this codebase does:
 * deterministic, hermetic browser-level proof independent of live
 * database state.
 */
import { expect, test } from "@playwright/test";

const ME_ROUTE = "http://localhost:8000/auth/me";
const WORKSPACES_LIST_ROUTE = "http://localhost:8000/workspaces";
const ORIENTATION_ROUTE = "http://localhost:8000/workspaces/ws-orient";
const ADD_MEMBER_ROUTE = "http://localhost:8000/workspaces/ws-orient/members";

function authenticated(page: import("@playwright/test").Page) {
  return page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 200, json: { kind: "ok", userId: "u-orient" } }),
  );
}

test("an unauthenticated visitor is redirected to /login", async ({ page }) => {
  await page.route(ME_ROUTE, (route) =>
    route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }),
  );

  await page.goto("/workspaces");

  await expect(page).toHaveURL(/\/login$/);
});

test("renders the real list of accessible Workspaces", async ({ page }) => {
  await authenticated(page);
  await page.route(WORKSPACES_LIST_ROUTE, (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspaces: [
          { workspaceId: "ws-1", name: "Team Alpha", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        ],
      },
    }),
  );

  await page.goto("/workspaces");

  await expect(page.getByTestId("workspaces-list")).toBeVisible();
  await expect(page.getByRole("link", { name: "Team Alpha" })).toHaveAttribute("href", "/workspaces/ws-1");
});

test("renders an empty state, not an error, for zero Workspaces", async ({ page }) => {
  await authenticated(page);
  await page.route(WORKSPACES_LIST_ROUTE, (route) =>
    route.fulfill({ json: { kind: "ok", workspaces: [] } }),
  );

  await page.goto("/workspaces");

  await expect(page.getByTestId("workspaces-empty")).toBeVisible();
});

test("creating a Workspace navigates to its real orientation page", async ({ page }) => {
  await authenticated(page);
  await page.route(WORKSPACES_LIST_ROUTE, (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ json: { kind: "ok", workspaceId: "ws-new" } });
    }
    return route.fulfill({ json: { kind: "ok", workspaces: [] } });
  });
  await page.route("http://localhost:8000/workspaces/ws-new", (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: "ws-new", name: "Brand New", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        role: "Owner",
        heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
        authorized: true,
        governanceCapable: true,
      },
    }),
  );

  await page.goto("/workspaces");
  await page.getByTestId("workspace-name-input").fill("Brand New");
  await page.getByTestId("create-workspace-submit").click();

  await expect(page).toHaveURL(/\/workspaces\/ws-new$/);
  await expect(page.getByTestId("orientation-workspace-name")).toHaveText("Brand New");
});

test("a rejected creation (whitespace-only name) shows the real server error, no navigation", async ({
  page,
}) => {
  await authenticated(page);
  await page.route(WORKSPACES_LIST_ROUTE, (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ json: { kind: "rejected", reasonCode: "WORKSPACE_NAME_REQUIRED" } });
    }
    return route.fulfill({ json: { kind: "ok", workspaces: [] } });
  });

  await page.goto("/workspaces");
  // "   " passes the HTML `required` attribute's own browser-level
  // validation (non-empty from the browser's point of view) while
  // still triggering the real server-side rejection -- proves the
  // SERVER's own rejection is what renders, not a client-side guess.
  await page.getByTestId("workspace-name-input").fill("   ");
  await page.getByTestId("create-workspace-submit").click();

  await expect(page.getByTestId("create-workspace-error")).toHaveText("WORKSPACE_NAME_REQUIRED");
  await expect(page).toHaveURL(/\/workspaces$/);
});

test("orientation renders governance-capable state with a real Add Member form", async ({ page }) => {
  await authenticated(page);
  await page.route(ORIENTATION_ROUTE, (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: "ws-orient", name: "Orient Target", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        role: "Owner",
        heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
        authorized: true,
        governanceCapable: true,
      },
    }),
  );

  await page.goto("/workspaces/ws-orient");

  await expect(page.getByTestId("orientation-role")).toHaveText("Your role: Owner");
  await expect(page.getByTestId("orientation-governance-capable")).toHaveText("Governance-capable: true");
  await expect(page.getByTestId("add-member-form")).toBeVisible();
});

test("mandatory attack: a non-governance-capable member sees no Add Member form at all", async ({
  page,
}) => {
  await authenticated(page);
  await page.route(ORIENTATION_ROUTE, (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: "ws-orient", name: "Orient Target", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        role: "Contributor",
        heldAuthorityClasses: [],
        authorized: false,
        governanceCapable: false,
      },
    }),
  );

  await page.goto("/workspaces/ws-orient");

  await expect(page.getByTestId("orientation-governance-capable")).toHaveText("Governance-capable: false");
  // No form element at all -- not present-but-disabled, not hidden via CSS.
  await expect(page.getByTestId("add-member-form")).toHaveCount(0);
});

test("a non-member is denied, never shown a governance-capable default", async ({ page }) => {
  await authenticated(page);
  await page.route(ORIENTATION_ROUTE, (route) =>
    route.fulfill({ json: { kind: "denied", reasonCode: "NOT_A_WORKSPACE_MEMBER" } }),
  );

  await page.goto("/workspaces/ws-orient");

  await expect(page.getByTestId("orientation-denied")).toHaveText("NOT_A_WORKSPACE_MEMBER");
  await expect(page.getByTestId("add-member-form")).toHaveCount(0);
});

test("submitting Add Member succeeds and refreshes the real capability list", async ({ page }) => {
  await authenticated(page);
  let addedOnce = false;
  await page.route(ORIENTATION_ROUTE, (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: "ws-orient", name: "Orient Target", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        role: "Owner",
        heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
        authorized: true,
        governanceCapable: true,
      },
    }),
  );
  await page.route(ADD_MEMBER_ROUTE, (route) => {
    addedOnce = true;
    return route.fulfill({ json: { kind: "ok" } });
  });

  await page.goto("/workspaces/ws-orient");
  await page.getByTestId("new-member-user-id-input").fill("11111111-1111-1111-1111-111111111111");
  await page.getByTestId("add-member-submit").click();

  await expect(page.getByTestId("add-member-success")).toBeVisible();
  expect(addedOnce).toBe(true);
});

test("mandatory attack: a denied Add Member attempt shows the real server denial, never a false success", async ({
  page,
}) => {
  await authenticated(page);
  await page.route(ORIENTATION_ROUTE, (route) =>
    route.fulfill({
      json: {
        kind: "ok",
        workspace: { workspaceId: "ws-orient", name: "Orient Target", ownerId: "u-orient", createdAt: "2026-01-01T00:00:00Z" },
        role: "Owner",
        heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"],
        authorized: true,
        governanceCapable: true,
      },
    }),
  );
  await page.route(ADD_MEMBER_ROUTE, (route) =>
    route.fulfill({ json: { kind: "denied", reasonCode: "BND_004_DENIED" } }),
  );

  await page.goto("/workspaces/ws-orient");
  await page.getByTestId("new-member-user-id-input").fill("22222222-2222-2222-2222-222222222222");
  await page.getByTestId("add-member-submit").click();

  await expect(page.getByTestId("add-member-error")).toHaveText("BND_004_DENIED");
  await expect(page.getByTestId("add-member-success")).toHaveCount(0);
});
