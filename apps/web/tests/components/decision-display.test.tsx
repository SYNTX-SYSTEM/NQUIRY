/**
 * Rendering-output proofs for PKG-29's own PASSIVE display components
 * (`AiRecommendationPanel`, `DecisionProvenanceView`). Uses
 * `react-dom/server`'s `renderToStaticMarkup`, the same zero-new-
 * dependency mechanism PKG-28 established.
 *
 * `RecordDecisionForm`/`DecisionSection` are genuinely interactive
 * (onChange/onSubmit, double-click guard, async result state) --
 * `renderToStaticMarkup` cannot dispatch DOM events at all, and this
 * package's own 14 manifest entry names "TESTS REQUIRED: E2E"
 * specifically (unlike PKG-28's own "UI tests" wording), not unit/
 * component tests, as its primary test family. Their behavior is
 * proven instead by real Playwright E2E specs
 * (`tests/e2e/decision.spec.ts`) against a real browser, which is the
 * only mechanism that can dispatch a genuine double-click or observe
 * real submit-timing races -- see this package's own completion
 * report for the full disclosure of this test-family choice.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AiRecommendationPanel } from "../../components/AiRecommendationPanel";
import { DecisionProvenanceView } from "../../components/DecisionProvenanceView";
import type { AiRecommendationView, ChallengeId, DecisionId, DecisionView } from "../../lib/api/types";

describe("AiRecommendationPanel", () => {
  const recommendation: AiRecommendationView = {
    generationId: "gen-1",
    summary: "Consider Option A for lower cost.",
  };

  it("renders the summary and a clear 'not a Decision' label", () => {
    const html = renderToStaticMarkup(<AiRecommendationPanel recommendation={recommendation} />);
    expect(html).toContain("Consider Option A for lower cost.");
    expect(html).toMatch(/NOT A DECISION/i);
    expect(html).toContain("DERIVED / PROPOSAL");
  });

  it("contains no interactive element -- a click here can never create/affect a Decision", () => {
    const html = renderToStaticMarkup(<AiRecommendationPanel recommendation={recommendation} />);
    expect(html).not.toMatch(/<button|<input|<form|<select/);
  });
});

describe("DecisionProvenanceView", () => {
  const decidedDecision: DecisionView = {
    decisionId: "d-1" as DecisionId,
    challengeId: "c-1" as ChallengeId,
    decisionQuestionRef: null,
    decisionQuestionText: "Which approach?",
    options: ["Option A", "Option B"],
    criteria: [],
    selectedOption: "Option A",
    rationale: "Lower cost",
    confidence: "high",
    state: "DECIDED",
    decidedByUserId: "u-1",
    decisionAuthorityBindingId: "binding-1",
    aiRecommendationConsumedRef: null,
    decidedAt: "2026-01-01T00:00:00Z",
  };

  it("renders the minimal 07 section 54.8 provenance fields verbatim", () => {
    const html = renderToStaticMarkup(<DecisionProvenanceView decision={decidedDecision} />);
    expect(html).toContain("Option A");
    expect(html).toContain("Lower cost");
    expect(html).toContain("high");
    expect(html).toContain("2026-01-01T00:00:00Z");
    expect(html).toContain("u-1");
    expect(html).toContain("binding-1");
  });

  it("honestly renders an absent aiRecommendationConsumedRef, never fabricating a fake reference", () => {
    const html = renderToStaticMarkup(<DecisionProvenanceView decision={decidedDecision} />);
    expect(html).toContain("none consumed");
  });

  it("contains no interactive element -- a purely informational view", () => {
    const html = renderToStaticMarkup(<DecisionProvenanceView decision={decidedDecision} />);
    expect(html).not.toMatch(/<button|<input|<form|<select/);
  });
});
