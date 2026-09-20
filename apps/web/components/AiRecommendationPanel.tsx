/**
 * 12 §24 item 11 (half): "Decision boundary showing that AI
 * recommendation is not a Decision" -- this half of that boundary is
 * the AI recommendation's own display: visually and structurally
 * separate from `DecisionSection`/`RecordDecisionForm`, never a
 * sibling option inside the Decision's own controls. This package's
 * own AI line: "Recommendation displayed separately."
 *
 * WHY THIS COMPONENT HAS ZERO INTERACTIVE ELEMENTS
 * --------------------------------------------------------------------
 * The mandatory adversarial attack "view-only action causing Decision"
 * requires that no click/interaction with the AI recommendation's own
 * display can ever create or affect a Decision. The only way to
 * structurally guarantee that is to never attach an interaction
 * handler here at all -- proven by the same "no button/input/form"
 * DOM-query proof PKG-28 already established for its own passive
 * components.
 */
import type { AiRecommendationView } from "../lib/api/types";

export function AiRecommendationPanel({ recommendation }: { readonly recommendation: AiRecommendationView }) {
  return (
    <section data-testid="ai-recommendation-panel" aria-label="AI recommendation, not a Decision">
      <span data-testid="ai-recommendation-label">AI RECOMMENDATION -- NOT A DECISION</span>
      <span data-testid="ai-recommendation-derived-label">DERIVED / PROPOSAL</span>
      <p data-testid="ai-recommendation-summary">{recommendation.summary}</p>
    </section>
  );
}
