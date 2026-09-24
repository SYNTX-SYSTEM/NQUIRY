/**
 * Real Playwright E2E proof for PKG-29's own Decision UI
 * (`DecisionSection`/`RecordDecisionForm`/`AiRecommendationPanel`/
 * `DecisionProvenanceView`), against a real Chromium browser + a real
 * running Next.js dev server. Both the `GET /workspaces/{w}/sessions/{s}`
 * query and the `POST /decisions/{d}/decide` command are intercepted
 * at the network layer via `page.route()` -- neither has a real
 * backend route yet (see `lib/api/client.ts`'s own header docstring).
 *
 * This file, not Vitest, is where `RecordDecisionForm`/`DecisionSection`'s
 * own interactive/adversarial behavior is proven -- see
 * `tests/components/decision-display.test.tsx`'s own header docstring
 * for why `renderToStaticMarkup` cannot exercise these two components
 * at all.
 */
import { expect, test } from "@playwright/test";

const WORKSPACE_ID = "ws-real";
const SESSION_ID = "sess-real";
const SESSION_ROUTE_PATTERN = "http://localhost:8000/workspaces/**/sessions/**";
const DECIDE_ROUTE_PATTERN = "http://localhost:8000/decisions/**/decide";
// F02 WU-02.10: the PKG-28/29 surface moved to `.../decision` (the canonical
// Session page is now the governed inquiry-position page).
const PAGE_PATH = `/workspaces/${WORKSPACE_ID}/sessions/${SESSION_ID}/decision`;

const AI_RECOMMENDATION = {
  generationId: "gen-1",
  summary: "The data suggests Option A minimizes long-term cost.",
};

const DECISION_UNDER_CONSIDERATION = {
  decisionId: "d-1",
  challengeId: "c-1",
  decisionQuestionRef: null,
  decisionQuestionText: "Which approach should we take?",
  options: ["Option A", "Option B"],
  criteria: ["Cost", "Speed"],
  selectedOption: null,
  rationale: null,
  confidence: null,
  state: "UNDER_CONSIDERATION",
  decidedByUserId: null,
  decisionAuthorityBindingId: "binding-1",
  aiRecommendationConsumedRef: null,
  decidedAt: null,
};

function sessionOkBody(decision: unknown, aiRecommendation: unknown = AI_RECOMMENDATION) {
  return {
    kind: "ok",
    data: {
      workspaceId: WORKSPACE_ID,
      challenge: { challengeId: "c-1", workspaceId: WORKSPACE_ID, title: "Reduce cost", description: null },
      session: { sessionId: SESSION_ID, challengeId: "c-1", workspaceId: WORKSPACE_ID, state: "REVIEW" },
      burst: null,
      decision,
      aiRecommendation,
    },
  };
}

async function gotoWithDecision(page: import("@playwright/test").Page, decision: unknown) {
  await page.route(SESSION_ROUTE_PATTERN, (route) => route.fulfill({ json: sessionOkBody(decision) }));
  await page.goto(PAGE_PATH);
  await page.getByTestId("decision-section").waitFor();
}

test("renders the AI recommendation separately from an UNDER_CONSIDERATION Decision, with a real interactive record-decision form", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await expect(page.getByTestId("ai-recommendation-panel")).toBeVisible();
  await expect(page.getByTestId("ai-recommendation-summary")).toContainText("Option A minimizes long-term cost");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("record-decision-form")).toBeVisible();
  await expect(page.getByTestId("decision-option-select")).toBeVisible();
});

test("recording a decision shows the fresh, server-returned DECIDED state -- never a client-guessed one", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({
      json: {
        kind: "committed",
        decision: {
          ...DECISION_UNDER_CONSIDERATION,
          state: "DECIDED",
          selectedOption: "Option A",
          rationale: "Lower cost",
          confidence: "high",
          decidedByUserId: "u-1",
          decidedAt: "2026-01-01T00:00:00Z",
        },
      },
    }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("decision-rationale-input").fill("Lower cost");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED");
  await expect(page.getByTestId("decision-provenance-view")).toBeVisible();
  await expect(page.getByTestId("decision-selected-option")).toContainText("Option A");
  await expect(page.getByTestId("record-decision-form")).toHaveCount(0);
});

test("mandatory attack: no label or action implies approving the AI recommendation as the Decision", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const section = page.getByTestId("decision-section");
  await expect(section.getByText(/approve/i)).toHaveCount(0);
  await expect(section.getByText(/accept ai/i)).toHaveCount(0);
  // The select's own initial value must never equal the AI-recommended content.
  await expect(page.getByTestId("decision-option-select")).toHaveValue("");
});

test("mandatory attack: view-only action on the AI recommendation panel never creates or affects a Decision", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const panel = page.getByTestId("ai-recommendation-panel");
  await expect(panel.locator("button, input, form, select, [role='button']")).toHaveCount(0);
  await panel.click();
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("mandatory attack: disabled-button bypass -- rapid double-click submits only one command", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  let decideRequestCount = 0;
  await page.route(DECIDE_ROUTE_PATTERN, async (route) => {
    decideRequestCount += 1;
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({
      json: { kind: "committed", decision: { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" } },
    });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  const submitButton = page.getByTestId("record-decision-submit");
  await submitButton.click({ trial: false });
  // Second click while the first request is still in flight (button
  // should already be disabled, but the assertion is on network
  // traffic, not the disabled attribute, to prove the JS-level guard
  // rather than only the DOM affordance).
  await submitButton.click({ force: true }).catch(() => {});

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED", { timeout: 5000 });
  expect(decideRequestCount).toBe(1);
});

test("mandatory attack: role-only actor -- server DENY leaves the Decision unchanged, never DECIDED", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "denied", result: "DENY", reasonCode: "NOT_DECISION_RIGHT_HOLDER" } }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("denied-banner")).toBeVisible();
  await expect(page.getByTestId("denied-result")).toContainText("DENY");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("decision-provenance-view")).toHaveCount(0);
});

test("mandatory attack: no admin-labeled path exists anywhere in the Decision section", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  const section = page.getByTestId("decision-section");
  await expect(section.getByText(/admin/i)).toHaveCount(0);
});

test("mandatory attack: auto-action after DECIDED -- no further action control renders", async ({ page }) => {
  await gotoWithDecision(page, { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" });

  await expect(page.getByTestId("decision-provenance-view")).toBeVisible();
  const section = page.getByTestId("decision-section");
  await expect(section.locator("button, input, form, select")).toHaveCount(0);
});

test("novel attack: server responds DENY after the click -- UI never shows a transiently-assumed DECIDED state", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    await route.fulfill({ json: { kind: "denied", result: "ESCALATE", reasonCode: "REQUIRES_ESCALATION" } });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  // Immediately after the click (before the delayed response), the
  // Decision must still show UNDER_CONSIDERATION, never a client-
  // assumed DECIDED -- this is the "no optimistic rendering" proof.
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
  await expect(page.getByTestId("denied-banner")).toBeVisible({ timeout: 5000 });
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: network failure during the decision submission shows a visible error, never a silent hang", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) => route.abort());

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("network-error-banner")).toBeVisible();
  await expect(page.getByTestId("network-error-banner")).toContainText(/decision/i);
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: forged/rejected selected option is shown distinctly, never accepted as a false success", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "rejected", reasonCode: "SELECTED_OPTION_NOT_CANDIDATE" } }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-rejected-banner")).toBeVisible();
  await expect(page.getByTestId("decision-rejected-banner")).toContainText("SELECTED_OPTION_NOT_CANDIDATE");
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("WU-02.12: a proven rollback is shown as failed_precommit, never as a rejection or a success", async ({
  page,
}) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  await page.route(DECIDE_ROUTE_PATTERN, (route) =>
    route.fulfill({ json: { kind: "failed_precommit", reasonCode: "SAVEPOINT_ROLLED_BACK" } }),
  );

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-failed-precommit-banner")).toBeVisible();
  await expect(page.getByTestId("decision-failed-precommit-banner")).toContainText("SAVEPOINT_ROLLED_BACK");
  await expect(page.getByTestId("decision-rejected-banner")).toHaveCount(0);
  await expect(page.getByTestId("decision-state")).toContainText("UNDER_CONSIDERATION");
});

test("novel attack: the request always carries the real decisionId, never a DOM-tamperable value", async ({ page }) => {
  await gotoWithDecision(page, DECISION_UNDER_CONSIDERATION);

  let capturedUrl: string | null = null;
  await page.route(DECIDE_ROUTE_PATTERN, (route) => {
    capturedUrl = route.request().url();
    return route.fulfill({
      json: { kind: "committed", decision: { ...DECISION_UNDER_CONSIDERATION, state: "DECIDED", selectedOption: "Option A", decidedByUserId: "u-1", decidedAt: "2026-01-01T00:00:00Z" } },
    });
  });

  await page.getByTestId("decision-option-select").selectOption("Option A");
  await page.getByTestId("record-decision-submit").click();

  await expect(page.getByTestId("decision-state")).toContainText("DECIDED");
  expect(capturedUrl).toContain(`/decisions/${DECISION_UNDER_CONSIDERATION.decisionId}/decide`);
});

test("no Decision under consideration renders a passive placeholder, no interactive element at all", async ({ page }) => {
  await gotoWithDecision(page, null);

  await expect(page.getByTestId("decision-none")).toBeVisible();
  const section = page.getByTestId("decision-section");
  await expect(section.locator("button, input, form, select")).toHaveCount(0);
});
