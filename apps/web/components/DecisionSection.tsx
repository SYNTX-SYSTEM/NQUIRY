"use client";

/**
 * Composes 12 §24 items 11/12/15 into one section: the AI
 * recommendation (separate, item 11), the current Decision state and
 * (while `UNDER_CONSIDERATION`) the human Decision action (item 12),
 * and the minimal provenance view once `DECIDED` (item 15).
 *
 * NO OPTIMISTIC RENDERING -- HOW THIS IS STRUCTURALLY, NOT JUST
 * BY-CONVENTION, TRUE
 * --------------------------------------------------------------------
 * `effectiveDecision` is EITHER the `decision` prop this component was
 * originally handed (the last real server-read state) OR `override`,
 * which is set to a new value in EXACTLY ONE place in this file: the
 * `.then()` branch of `recordHumanDecision`'s own `committed` case,
 * i.e. only after the server has actually confirmed a commit. There is
 * no third code path -- no `onSubmit` handler, no click handler,
 * nothing -- that ever calls `setOverride` before that. A click on
 * "Record Decision" moves this component into `submitting`, which
 * `RecordDecisionForm` renders as a disabled form; the visible Decision
 * state itself does not change again until a real response arrives, in
 * ANY of its four possible shapes (committed/denied/indeterminate/
 * rejected) -- including the DENY-after-click case, where
 * `effectiveDecision` simply never changes at all, because `override`
 * was never set.
 *
 * WHY A FAILED/DENIED ACTION RESULT REPLACES NOTHING
 * --------------------------------------------------------------------
 * `actionResult` (denied/indeterminate/rejected/network-error) is
 * tracked SEPARATELY from `override` -- rendering an inline banner
 * ALONGSIDE the unchanged Decision, never instead of it and never by
 * mutating it. This is the concrete mechanism behind "the UI shows the
 * previously-intended state, never a rolled-back one": there is
 * nothing to roll back, because nothing was ever advanced.
 */
import { useRef, useState } from "react";
import { recordHumanDecision } from "../lib/api/decisionClient";
import type { AiRecommendationView, DecisionActionResult, DecisionView } from "../lib/api/types";
import { AiRecommendationPanel } from "./AiRecommendationPanel";
import { DecisionProvenanceView } from "./DecisionProvenanceView";
import { DeniedBanner } from "./DeniedBanner";
import { IndeterminateBanner } from "./IndeterminateBanner";
import { NetworkErrorBanner } from "./NetworkErrorBanner";
import { RecordDecisionForm } from "./RecordDecisionForm";

type ActionState =
  | { readonly kind: "idle" }
  | { readonly kind: "submitting" }
  | { readonly kind: "result"; readonly result: DecisionActionResult }
  | { readonly kind: "network_error" };

export function DecisionSection({
  decision,
  aiRecommendation,
}: {
  readonly decision: DecisionView | null;
  readonly aiRecommendation: AiRecommendationView | null;
}) {
  const [override, setOverride] = useState<DecisionView | null>(null);
  const [actionState, setActionState] = useState<ActionState>({ kind: "idle" });
  const inFlightRef = useRef(false);

  const effectiveDecision = override ?? decision;
  const submitting = actionState.kind === "submitting";

  function handleSubmit(selectedOption: string, rationale: string | null, confidence: string | null) {
    if (inFlightRef.current || effectiveDecision === null) {
      return;
    }
    inFlightRef.current = true;
    setActionState({ kind: "submitting" });
    recordHumanDecision(effectiveDecision.decisionId, selectedOption, rationale, confidence)
      .then((result) => {
        inFlightRef.current = false;
        if (result.kind === "committed") {
          setOverride(result.decision);
        }
        setActionState({ kind: "result", result });
      })
      .catch(() => {
        inFlightRef.current = false;
        setActionState({ kind: "network_error" });
      });
  }

  return (
    <section data-testid="decision-section" aria-label="Decision">
      {aiRecommendation !== null ? <AiRecommendationPanel recommendation={aiRecommendation} /> : null}

      {effectiveDecision === null ? (
        <p data-testid="decision-none">No Decision is currently under consideration.</p>
      ) : (
        <div data-testid="decision-state-panel">
          <span data-testid="decision-state">{effectiveDecision.state}</span>

          {effectiveDecision.state === "UNDER_CONSIDERATION" ? (
            <>
              <ul data-testid="decision-options-list">
                {effectiveDecision.options.map((option) => (
                  <li key={option} data-testid="decision-option-item">
                    {option}
                  </li>
                ))}
              </ul>
              <RecordDecisionForm decision={effectiveDecision} submitting={submitting} onSubmit={handleSubmit} />
            </>
          ) : (
            <DecisionProvenanceView decision={effectiveDecision} />
          )}
        </div>
      )}

      {actionState.kind === "result" && actionState.result.kind === "denied" ? (
        <DeniedBanner result={actionState.result.result} reasonCode={actionState.result.reasonCode} />
      ) : null}
      {actionState.kind === "result" && actionState.result.kind === "indeterminate" ? (
        <IndeterminateBanner blockedTargetRef={actionState.result.blockedTargetRef} />
      ) : null}
      {actionState.kind === "result" && actionState.result.kind === "rejected" ? (
        <div data-testid="decision-rejected-banner" role="alert">
          {actionState.result.reasonCode}
        </div>
      ) : null}
      {actionState.kind === "network_error" ? (
        <NetworkErrorBanner message="Unable to record this Decision. Nothing was saved." />
      ) : null}
    </section>
  );
}
