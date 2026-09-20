/**
 * Rendering-output proofs for PKG-28's own non-interactive display
 * components. Uses `react-dom/server`'s `renderToStaticMarkup` --
 * verified standalone with zero new npm dependencies (no jsdom/
 * @testing-library needed) since every component here is pure and
 * non-interactive.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { BurstPanel } from "../../components/BurstPanel";
import { ChallengeSummary } from "../../components/ChallengeSummary";
import { DeniedBanner } from "../../components/DeniedBanner";
import { IndeterminateBanner } from "../../components/IndeterminateBanner";
import { NetworkErrorBanner } from "../../components/NetworkErrorBanner";
import { QuestionList } from "../../components/QuestionList";
import { SessionStateBadge } from "../../components/SessionStateBadge";
import { WorkspaceBadge } from "../../components/WorkspaceBadge";
import type { BurstView, ChallengeId, ChallengeView, QuestionId, SessionId, WorkspaceId } from "../../lib/api/types";

const WORKSPACE_ID = "ws-1" as WorkspaceId;

describe("WorkspaceBadge", () => {
  it("renders exactly the given workspaceId, verbatim", () => {
    const html = renderToStaticMarkup(<WorkspaceBadge workspaceId={WORKSPACE_ID} />);
    expect(html).toContain("ws-1");
  });

  it("contains no input/form element a viewer could use to change the Workspace", () => {
    const html = renderToStaticMarkup(<WorkspaceBadge workspaceId={WORKSPACE_ID} />);
    expect(html).not.toMatch(/<input|<form|<select/);
  });
});

describe("ChallengeSummary", () => {
  const challenge: ChallengeView = {
    challengeId: "c-1" as ChallengeId,
    workspaceId: WORKSPACE_ID,
    title: "Reduce onboarding drop-off",
    description: "Users abandon signup at step 3.",
  };

  it("renders title and description", () => {
    const html = renderToStaticMarkup(<ChallengeSummary challenge={challenge} />);
    expect(html).toContain("Reduce onboarding drop-off");
    expect(html).toContain("Users abandon signup at step 3.");
  });

  it("omits the description paragraph entirely when null", () => {
    const html = renderToStaticMarkup(<ChallengeSummary challenge={{ ...challenge, description: null }} />);
    expect(html).not.toContain("<p>");
  });
});

describe("SessionStateBadge", () => {
  it("renders the exact SessionState value, not a relabeled subset", () => {
    const html = renderToStaticMarkup(<SessionStateBadge state="QUESTION_SELECTION" />);
    expect(html).toContain("QUESTION_SELECTION");
  });
});

describe("QuestionList", () => {
  it("renders originalText verbatim and an origin marker for a HUMAN question", () => {
    const html = renderToStaticMarkup(
      <QuestionList questions={[{ questionId: "q-1" as QuestionId, originalText: "Why do users churn?", origin: "HUMAN" }]} />,
    );
    expect(html).toContain("Why do users churn?");
    expect(html).toContain("HUMAN");
    expect(html).not.toContain("DERIVED / PROPOSAL");
  });

  it("renders the DERIVED / PROPOSAL label only for AI-origin questions", () => {
    const html = renderToStaticMarkup(
      <QuestionList
        questions={[
          { questionId: "q-1" as QuestionId, originalText: "Human question", origin: "HUMAN" },
          { questionId: "q-2" as QuestionId, originalText: "AI question", origin: "AI" },
        ]}
      />,
    );
    const occurrences = html.split("DERIVED / PROPOSAL").length - 1;
    expect(occurrences).toBe(1);
  });

  it("never truncates or normalizes originalText", () => {
    const verbatim = "  Why -- exactly -- did this happen??  ";
    const html = renderToStaticMarkup(
      <QuestionList questions={[{ questionId: "q-1" as QuestionId, originalText: verbatim, origin: "HUMAN" }]} />,
    );
    expect(html).toContain(verbatim.trim());
  });
});

describe("BurstPanel", () => {
  const baseBurst: BurstView = {
    burstId: "b-1" as never,
    sessionId: "s-1" as SessionId,
    state: "ACTIVE",
    mode: "HUMAN_ONLY",
    questions: [],
  };

  it("shows the HUMAN_ONLY indicator for HUMAN_ONLY mode", () => {
    const html = renderToStaticMarkup(<BurstPanel burst={baseBurst} />);
    expect(html).toContain("HUMAN_ONLY");
  });

  it("omits the HUMAN_ONLY indicator for other modes", () => {
    const html = renderToStaticMarkup(<BurstPanel burst={{ ...baseBurst, mode: "HUMAN_PLUS_AI" }} />);
    expect(html).not.toContain("burst-human-only-indicator");
  });

  it("shows the frozen indicator only when state is COMPLETED", () => {
    const active = renderToStaticMarkup(<BurstPanel burst={baseBurst} />);
    const completed = renderToStaticMarkup(<BurstPanel burst={{ ...baseBurst, state: "COMPLETED" }} />);
    expect(active).not.toContain("Frozen");
    expect(completed).toContain("Frozen");
  });

  it("never renders any interactive/action element, including while ACTIVE", () => {
    const html = renderToStaticMarkup(<BurstPanel burst={baseBurst} />);
    expect(html).not.toMatch(/<button|<input|<form/);
  });
});

describe("DeniedBanner", () => {
  it("renders the result and reasonCode verbatim for each BoundaryResult value", () => {
    for (const result of ["DENY", "REQUIRE", "ESCALATE"] as const) {
      const html = renderToStaticMarkup(<DeniedBanner result={result} reasonCode="BND-CODE" />);
      expect(html).toContain(result);
      expect(html).toContain("BND-CODE");
    }
  });

  it("never renders a retry/override control", () => {
    const html = renderToStaticMarkup(<DeniedBanner result="DENY" reasonCode="x" />);
    expect(html).not.toMatch(/<button|<input|<form/);
  });
});

describe("IndeterminateBanner", () => {
  it("renders the blocked target ref", () => {
    const html = renderToStaticMarkup(<IndeterminateBanner blockedTargetRef="recovery:abc-123" />);
    expect(html).toContain("recovery:abc-123");
  });

  it("never renders a retry control -- the component accepts no canRetry-shaped prop at all", () => {
    const html = renderToStaticMarkup(<IndeterminateBanner blockedTargetRef="x" />);
    expect(html).not.toMatch(/<button|<input|<form/);
    expect(html).not.toMatch(/retry/i);
  });
});

// Retrofit (external review): the 4th load state (fetch failure) had
// no rendered representation at all before this fix.
describe("NetworkErrorBanner", () => {
  it("renders a visible error, not an empty/blank output", () => {
    const html = renderToStaticMarkup(<NetworkErrorBanner />);
    expect(html.length).toBeGreaterThan(0);
    expect(html).toMatch(/unable to load/i);
  });

  it("never renders a retry control -- the component accepts no props at all", () => {
    const html = renderToStaticMarkup(<NetworkErrorBanner />);
    expect(html).not.toMatch(/<button|<input|<form/);
    expect(html).not.toMatch(/retry/i);
  });
});
