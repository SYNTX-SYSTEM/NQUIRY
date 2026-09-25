/**
 * SF-02/SF-04 Semantic Core Organism (22 §11.1, §12; doc 25 §6).
 *
 * The centre projects the canonical field identity (the page's confirmed context) as a nucleus with anatomy:
 *   outer aura → resonance rings (3, phase-shifted, irregular) → membrane → nucleus (identity, state, meta) →
 *   micro-orbit trace.
 * `state` is the core's NODE state (22 §14.2) from the authoritative projection: `current`, `human` (Human
 * Question Field active), `frozen`, `boundary`, `loading`. It is also written as text (`.core-state`), never carried
 * by the halo alone. Every anatomical layer is decorative (`aria-hidden`), painted with opacity/transform only, and
 * responds to the projection-local encounter vector the stage writes (`--vec-x/--vec-y/--vec-on`): a hovered or
 * focused node makes the aura and the facing ring lean toward it (doc 25 §6.4). Nothing here creates state
 * (doc 25 §6.3); the micro-orbit is a continuity trace, never a spinner (48 s, faint).
 */
import type { ReactNode } from "react";

export type CoreState = "current" | "human" | "frozen" | "boundary" | "loading" | "established";

export function FieldCore({
  kind,
  state,
  eyebrow,
  title,
  titleAs = "h1",
  stateText,
  meta,
  testId,
  children,
}: {
  readonly kind: string;
  readonly state: CoreState;
  readonly eyebrow: string;
  readonly title: ReactNode;
  readonly titleAs?: "h1" | "h2" | "p";
  /** The canonical state in words, e.g. "QUESTION_GENERATION" or "3 accessible Workspaces". */
  readonly stateText?: ReactNode;
  readonly meta?: ReactNode;
  readonly testId?: string;
  readonly children?: ReactNode;
}) {
  const Title = titleAs;
  return (
    <section className="core" data-core-kind={kind} data-core-state={state} data-testid={testId ?? "field-core"} aria-labelledby={`${kind}-core-title`}>
      <div className="core-aura" aria-hidden="true" />
      <div className="core-rings" aria-hidden="true">
        <span className="core-ring" data-ring="1" />
        <span className="core-ring" data-ring="2" />
        <span className="core-ring" data-ring="3" />
      </div>
      <div className="core-membrane" aria-hidden="true" />
      <div className="core-orbit-trace" aria-hidden="true">
        <span className="core-orbit-dot" />
      </div>
      <div className="core-nucleus">
        <p className="eyebrow">{eyebrow}</p>
        <Title id={`${kind}-core-title`} className="core-title">
          {title}
        </Title>
        {stateText ? <div className="core-state">{stateText}</div> : null}
        {meta ? <div className="core-meta">{meta}</div> : null}
        {children}
      </div>
    </section>
  );
}
