/**
 * F03 WU-03.10: what the frozen human question set and the capture panel
 * render, from server data only.
 *
 * MUST BECOME TRUE: every Question is shown EXACTLY as stored (whitespace kept),
 * marked HUMAN with its author and order; the frozen marker, verified state and
 * fingerprint are visible; an unavailable capture shows the server's own reason.
 * MUST REMAIN IMPOSSIBLE: an affordance the server did not offer (no capture
 * form for a non-participant, none after the freeze); a rewritten/trimmed text;
 * an AI mark on a captured Question; a control in the frozen set (it is a
 * record, not a form).
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { FrozenQuestionSet } from "../../components/f03/FrozenQuestionSet";
import { OwnQuestions } from "../../components/f03/OwnQuestions";
import type { CapturedQuestion } from "../../lib/api/inquiryClient";

const q = (over: Partial<CapturedQuestion>): CapturedQuestion => ({
  questionId: "q-1",
  originalText: "Why did it drop?",
  origin: "HUMAN",
  captureOrigin: "HUMAN",
  authorUserId: "u-1",
  authorName: "Alice",
  capturedOrder: 0,
  capturedAt: "2026-09-24T09:00:00+00:00",
  ...over,
});

describe("FrozenQuestionSet", () => {
  const frozen = {
    fingerprint: "ab".repeat(32),
    verified: true,
    memberCount: 2,
    completedAt: "2026-09-24T09:05:00+00:00",
    questions: [q({}), q({ questionId: "q-2", originalText: "  How  如何 ?\n", authorName: "Bob", capturedOrder: 1 })],
  };

  it("shows each question exactly as stored, human-marked, with author and order", () => {
    const html = renderToStaticMarkup(<FrozenQuestionSet frozen={frozen} />);
    expect(html).toContain("Why did it drop?");
    expect(html).toContain("  How  如何 ?\n"); // whitespace preserved verbatim
    expect(html).toContain("Alice");
    expect(html).toContain("Bob");
    expect(html.match(/data-testid="frozen-question"/g)).toHaveLength(2);
    expect(html.match(/tag human/g)?.length).toBeGreaterThanOrEqual(2);
    expect(html).not.toMatch(/tag ai/);
  });

  it("shows the frozen marker, the verification state and the fingerprint", () => {
    const html = renderToStaticMarkup(<FrozenQuestionSet frozen={frozen} />);
    expect(html).toContain('data-testid="frozen-marker"');
    expect(html).toContain("Verified");
    expect(html).toContain("ab".repeat(32));
    expect(html).toContain("2 questions");
  });

  it("reports a fingerprint that does NOT verify instead of hiding it", () => {
    const html = renderToStaticMarkup(<FrozenQuestionSet frozen={{ ...frozen, verified: false }} />);
    expect(html).toContain('data-verified="false"');
    expect(html).toMatch(/does not match/i);
  });

  it("is a record: no form controls", () => {
    const html = renderToStaticMarkup(<FrozenQuestionSet frozen={frozen} />);
    expect(html).not.toMatch(/<form|<input|<textarea|<button|<select/);
  });
});

describe("OwnQuestions", () => {
  it("lists only what it is given, exactly as typed, with human mark", () => {
    const html = renderToStaticMarkup(<OwnQuestions questions={[q({ originalText: "  spaced  ?" })]} />);
    expect(html).toContain("  spaced  ?");
    expect(html).toContain('data-testid="own-question"');
    expect(html).toContain("human");
  });

  it("says so when the viewer has captured nothing yet", () => {
    const html = renderToStaticMarkup(<OwnQuestions questions={[]} />);
    expect(html).toContain('data-testid="own-questions-empty"');
  });
});
