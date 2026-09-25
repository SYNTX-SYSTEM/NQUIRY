"use client";
/**
 * Focus lens (human direction): when a satellite is encountered (pointer rests on it, or keyboard focus reaches it),
 * the field dims slightly and ONE breathing lens appears in the middle of the screen with everything the page already
 * knows about that entry — the same canonical facts the server sent, nothing inferred, nothing new.
 *
 * Projection-local and presentation only: the lens holds no state of the domain, sends no request and is never the
 * way to act (the satellite itself stays the link or button). It is a tooltip for the satellite (`role="tooltip"`,
 * referenced by the satellite's `aria-describedby`), so assistive technology reads the same facts. The intent delay is
 * a CSS animation delay (no timer, HD-11); leaving the satellite, blurring it or pressing Escape closes the lens.
 */
import { createContext, useContext, type ReactNode } from "react";
import type { VisualTone } from "../../../lib/field/projection";

export const FOCUS_LENS_ID = "focus-lens";

export type LensFact = { readonly label: string; readonly value: string };
export type LensContent = {
  readonly key: string;
  /** The relation family the entry belongs to (e.g. "People"). */
  readonly family: string;
  readonly title: string;
  /** The relation state in words (the node's marker). */
  readonly state: string;
  readonly tone: VisualTone;
  readonly facts: readonly LensFact[];
  /** What selecting the satellite does, in words (e.g. "Select to enter the Challenge field"). */
  readonly hint?: string;
};

export type LensControl = { readonly open: (content: LensContent) => void; readonly close: (key: string) => void };

export const LensContext = createContext<LensControl | null>(null);

export function useFocusLens(): LensControl | null {
  return useContext(LensContext);
}

export function FocusLens({ content }: { readonly content: LensContent }): ReactNode {
  return (
    <>
      <div className="lens-veil" aria-hidden="true" />
      <div className="focus-lens" id={FOCUS_LENS_ID} role="tooltip" data-tone={content.tone} data-testid="focus-lens">
        <span className="focus-lens-contour" aria-hidden="true" />
        <p className="focus-lens-eyebrow">
          <span>{content.family}</span>
          <span className="focus-lens-state">{content.state}</span>
        </p>
        <p className="focus-lens-title">{content.title}</p>
        {content.facts.length > 0 ? (
          <dl className="focus-lens-facts">
            {content.facts.map((f) => (
              <div key={f.label} className="focus-lens-fact">
                <dt>{f.label}</dt>
                <dd>{f.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}
        {content.hint ? <p className="focus-lens-hint">{content.hint}</p> : null}
      </div>
    </>
  );
}
