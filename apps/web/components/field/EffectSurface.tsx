/**
 * SF-01 Effect Intent Surface + Commit Marker + Boundary Surface (21 §17, §22, §36, §39).
 *
 * Both surfaces render only for the relation that owns the current effect, so
 * an outcome stays attached to the relation that caused it (near field, 21 §30)
 * and is replaced by the next intent (no page-local residue).
 *
 * `data-outcome` keeps the exact kind (F02 contract: `command-outcome`);
 * `data-consequence` and `data-reconstruction` expose the two further
 * semantics this Field adds, so tests and humans read the same distinction:
 *   what the server said / what that means for canonical state / whether the
 *   visible state was re-read since.
 */
import type { EffectField, Reconstruction } from "../../lib/field/effectLifecycle";
import { describeOutcome } from "../../lib/field/outcomeSemantics";

export function EffectIntent({ field, relation }: { readonly field: EffectField; readonly relation: string }) {
  const c = field.current;
  if (c.phase !== "requested" || c.relation !== relation) return null;
  return (
    <p className="effect-intent t-system" role="status" data-testid="effect-requested" data-effect="requested">
      Requested. Not yet committed: the state shown stays canonical until the server confirms.
    </p>
  );
}

/**
 * Reconstruction Surface (21 §22, §36): after an outcome whose re-read failed,
 * the projection on screen is only the LAST CONFIRMED state and says so
 * (21 §14 read path). Rendered in the centre zone, independent of which
 * relation caused the outcome.
 */
export function ReconstructionNote({ field }: { readonly field: EffectField }) {
  const c = field.current;
  if (c.phase !== "settled" || c.reconstruction !== "failed") return null;
  return (
    <p className="reconstruction-note" data-testid="projection-last-confirmed" data-projection="last-confirmed">
      Last confirmed state. It could not be re-read, so it may no longer be current.
    </p>
  );
}

function reconstructionText(reconstruction: Reconstruction, committed: boolean): string {
  switch (reconstruction) {
    case "not_started":
    case "reading":
      return "Re-reading the canonical state…";
    case "done":
      return "The state shown was re-read from the canonical source.";
    case "failed":
      return committed
        ? "The change committed, but the current state could not be re-read. Re-read it before acting on it."
        : "The current state could not be re-read. Re-read it before acting on it.";
  }
}

export function EffectOutcome({
  field,
  relation,
  onReread,
  reasonTestId,
  committedTestId,
}: {
  readonly field: EffectField;
  readonly relation: string;
  readonly onReread?: () => void;
  /** Legacy contract hook: element whose text is exactly the server reason code. */
  readonly reasonTestId?: string;
  /** Legacy contract hook: marker present only for a committed outcome. */
  readonly committedTestId?: string;
}) {
  const c = field.current;
  if (c.phase !== "settled" || c.relation !== relation) return null;
  const semantics = describeOutcome(c.kind, "mutation");
  const committed = c.kind === "committed";
  return (
    <div
      className="effect-outcome"
      data-testid="command-outcome"
      data-outcome={c.kind}
      data-consequence={semantics.consequence ?? undefined}
      data-reconstruction={c.reconstruction}
      role={semantics.announce}
    >
      <p className="effect-title t-boundary">
        <strong data-testid={committed ? committedTestId : undefined}>{semantics.title}</strong>
      </p>
      {!committed && c.reasonCode ? (
        <p className="effect-reason t-proof mono" data-testid={reasonTestId}>
          {c.reasonCode}
        </p>
      ) : null}
      {!committed ? <p className="effect-consequence">{semantics.consequenceText}</p> : null}
      <p className="effect-reconstruction muted" data-testid="effect-reconstruction">
        {reconstructionText(c.reconstruction, committed)}
      </p>
      {c.reconstruction === "failed" && onReread ? (
        <button className="button secondary" type="button" onClick={onReread}>
          Re-read current state
        </button>
      ) : null}
    </div>
  );
}
