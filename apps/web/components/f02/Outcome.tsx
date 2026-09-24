/**
 * The ONE place a Command outcome is rendered. `data-outcome` carries the
 * exact server kind (or `network_failure`), so tests and humans see the same
 * distinction: committed ≠ denied ≠ rejected ≠ stale ≠ blocked ≠
 * failed_precommit ≠ indeterminate ≠ not_found ≠ network_failure.
 */
import { OUTCOME_TEXT, type FailureKind } from "../../lib/api/inquiryClient";

export type ShownOutcome = { readonly kind: FailureKind | "committed"; readonly reasonCode?: string; readonly detail?: string };

export function Outcome({ outcome }: { readonly outcome: ShownOutcome | null }) {
  if (outcome === null) {
    return null;
  }
  const isProblem = outcome.kind !== "committed";
  return (
    <div
      className="outcome"
      data-testid="command-outcome"
      data-outcome={outcome.kind}
      role={isProblem ? "alert" : "status"}
    >
      <strong>{OUTCOME_TEXT[outcome.kind]}</strong>
      {outcome.reasonCode ? <span className="mono">{outcome.reasonCode}</span> : null}
      {outcome.detail ? <p className="muted">{outcome.detail}</p> : null}
    </div>
  );
}
