"use client";

/**
 * 12 §24 item 12: "human Decision action for authorized holder" --
 * the ONE interactive control this package introduces. Rendered only
 * while `decision.state === "UNDER_CONSIDERATION"` (see
 * `DecisionSection`), and never renders anything from
 * `AiRecommendationView` into its own initial field values.
 *
 * WHY THIS COMPONENT NEVER CALLS THE NETWORK ITSELF
 * --------------------------------------------------------------------
 * `onSubmit` is a plain callback into the parent (`DecisionSection`),
 * which owns the actual `recordHumanDecision` call and the resulting
 * `submitting`/result state machine. This form is a pure, dumb input
 * collector -- it cannot itself decide anything happened, and holds no
 * "the action succeeded" state of its own. This is what makes "no
 * optimistic rendering" structurally true rather than merely a
 * discipline this file would otherwise have to remember to uphold:
 * there is no local success state HERE that could diverge from the
 * server's own answer.
 *
 * WHY A REF-BASED GUARD EXISTS IN ADDITION TO THE `disabled` ATTRIBUTE
 * --------------------------------------------------------------------
 * Mandatory-adjacent adversarial attack (double/rapid double-click):
 * `disabled={submitting}` is a React prop update, not synchronous --
 * two `click` events dispatched in the same task can both fire this
 * handler before React re-renders the disabled button. `submittedRef`
 * makes the SECOND invocation within that same window a no-op at the
 * JavaScript level, not merely a browser-level "the button looked
 * disabled" affordance (12 §28-style ARCHITECTURAL_INVARIANT elsewhere
 * in this codebase: "HIDING BUTTON != SECURITY" -- the true safety net
 * remains PKG-11's own server-side idempotency; this guard only
 * prevents this ONE component from gratuitously firing a second
 * request for a single user gesture).
 */
import { useEffect, useRef, useState } from "react";
import type { DecisionView } from "../lib/api/types";

export function RecordDecisionForm({
  decision,
  submitting,
  onSubmit,
}: {
  readonly decision: DecisionView;
  readonly submitting: boolean;
  readonly onSubmit: (selectedOption: string, rationale: string | null, confidence: string | null) => void;
}) {
  const [selectedOption, setSelectedOption] = useState("");
  const [rationale, setRationale] = useState("");
  const [confidence, setConfidence] = useState("");
  const submittedRef = useRef(false);

  useEffect(() => {
    if (!submitting) {
      submittedRef.current = false;
    }
  }, [submitting]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || submittedRef.current || selectedOption === "") {
      return;
    }
    submittedRef.current = true;
    onSubmit(selectedOption, rationale.length > 0 ? rationale : null, confidence.length > 0 ? confidence : null);
  }

  return (
    <form data-testid="record-decision-form" onSubmit={handleSubmit}>
      {decision.options.length > 0 ? (
        <select
          data-testid="decision-option-select"
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          disabled={submitting}
          required
        >
          <option value="" disabled>
            Select an option
          </option>
          {decision.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          data-testid="decision-option-input"
          type="text"
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          disabled={submitting}
          required
        />
      )}
      <textarea
        data-testid="decision-rationale-input"
        value={rationale}
        onChange={(e) => setRationale(e.target.value)}
        disabled={submitting}
      />
      <input
        data-testid="decision-confidence-input"
        type="text"
        value={confidence}
        onChange={(e) => setConfidence(e.target.value)}
        disabled={submitting}
      />
      <button data-testid="record-decision-submit" type="submit" disabled={submitting}>
        Record Decision
      </button>
    </form>
  );
}
