/**
 * SF-01 Boundary Surface for a READ (21 §14): the projection could not be
 * confirmed. A read has no effect, so no consequence is claimed. Only the
 * confirmed context (the Relation Trace) remains, and nothing is invented to
 * replace what could not be read.
 */
import { describeOutcome, type SettledKind } from "../../lib/field/outcomeSemantics";

type ReadKind = Exclude<SettledKind, "committed">;

const READ_CONSEQUENCE: Readonly<Record<ReadKind, string>> = {
  denied: "Only the confirmed context above is shown.",
  rejected: "Only the confirmed context above is shown.",
  not_found: "Only the confirmed context above is shown.",
  stale: "Only the confirmed context above is shown.",
  blocked: "Only the confirmed context above is shown.",
  failed_precommit: "Only the confirmed context above is shown.",
  indeterminate: "No current projection is available. Nothing is shown as current.",
  network_failure: "No current projection is available. Nothing is shown as current.",
};

export function ReadBoundary({
  kind,
  reasonCode,
  testId = "read-boundary",
  reasonTestId,
}: {
  readonly kind: ReadKind;
  readonly reasonCode: string;
  readonly testId?: string;
  readonly reasonTestId?: string;
}) {
  const semantics = describeOutcome(kind, "read");
  return (
    <section className="read-boundary" data-testid={testId} data-outcome={kind} role="alert">
      <p className="t-boundary">
        <strong>{semantics.title}</strong>
      </p>
      <p className="t-proof mono" data-testid={reasonTestId}>
        {reasonCode}
      </p>
      <p className="muted">{READ_CONSEQUENCE[kind]}</p>
    </section>
  );
}
