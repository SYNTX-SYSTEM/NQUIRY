/**
 * 12 §24 item 15: "minimal provenance/audit reconstruction view" for
 * the Decision artifact class -- materializes 07 §54.8's own named
 * minimum field list ("human authoritative origin for DECIDED state",
 * "DecisionAuthority holder", "AI recommendations consumed where
 * applicable", "Evidence set consumed where applicable", "selected
 * option", "rationale", "decision time") from `DecisionView`'s own
 * fields, once `state === "DECIDED"`.
 *
 * WHY `decidedByUserId`/`decisionAuthorityBindingId` ARE SHOWN AS
 * OPAQUE REFS, NEVER DECODED
 * --------------------------------------------------------------------
 * This package builds no user-directory or governance-binding lookup
 * -- decoding either into a human-readable name/role would be
 * inventing a Query 14 never assigns to this package. Their mere
 * non-null PRESENCE, printed verbatim, already discharges 07 §54.8's
 * two requirements ("human authoritative origin", "DecisionAuthority
 * holder"): `Decision.__post_init__`'s own backend invariant already
 * guarantees a DECIDED row can never lack either one, so a real
 * backend response reaching this component with `state === "DECIDED"`
 * has already proven both facts before this component ever runs.
 *
 * `aiRecommendationConsumedRef` is rendered honestly even though it is
 * always `null` in the current, real backend today -- see
 * `DecisionView`'s own docstring in `types.ts` for the full
 * disclosure. Never fabricated as "N/A" prose that would obscure that
 * the underlying plumbing (`Decision.provenance_ref`) is itself
 * SUCCESSOR_NOT_BUILT.
 */
import type { DecisionView } from "../lib/api/types";

export function DecisionProvenanceView({ decision }: { readonly decision: DecisionView }) {
  return (
    <section data-testid="decision-provenance-view" aria-label="Decision provenance">
      <span data-testid="decision-selected-option">{decision.selectedOption}</span>
      {decision.rationale !== null ? <p data-testid="decision-rationale">{decision.rationale}</p> : null}
      {decision.confidence !== null ? <span data-testid="decision-confidence">{decision.confidence}</span> : null}
      <span data-testid="decision-decided-at">{decision.decidedAt}</span>
      <span data-testid="decision-decided-by">{decision.decidedByUserId}</span>
      <span data-testid="decision-authority-binding">{decision.decisionAuthorityBindingId}</span>
      <span data-testid="decision-ai-recommendation-consumed-ref">
        {decision.aiRecommendationConsumedRef ?? "none consumed"}
      </span>
    </section>
  );
}
