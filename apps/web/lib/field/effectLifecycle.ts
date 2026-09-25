/**
 * SF-01 effect lifecycle for the consequential relations of one surface
 * (21 §17, §22, CF-08, C3-01, C3-06).
 *
 *   POSSIBLE → REQUESTED → SETTLED(kind) → reconstruction reading → done | failed
 *
 * PENDING (21 §17) is deliberately not a phase. The F02 transport is one
 * synchronous request/response per Command and projects no "accepted but not
 * yet committed" signal, so the client cannot tell REQUESTED from PENDING.
 * Showing a separate PENDING state would display certainty the system does not
 * provide (DISPLAYED CERTAINTY <= RECONSTRUCTABLE CERTAINTY). Both mean the
 * same thing for the human: the canonical state is unchanged until confirmed.
 *
 * One surface holds one current effect: a new request replaces the previous
 * outcome, so no page-local success residue survives the next intent. Intent
 * keys whose consequence is UNKNOWN are retained per relation, so a repeat of
 * the same intent is the same logical Command on the server (20 §13:
 * UI DEBOUNCE ≠ IDEMPOTENCY). This module is pure: no I/O, no timers.
 */
import { describeOutcome, type SettledKind } from "./outcomeSemantics";

export type Reconstruction = "not_started" | "reading" | "done" | "failed";

export type EffectState =
  | { readonly phase: "possible" }
  | { readonly phase: "requested"; readonly relation: string; readonly intentKey: string | null }
  | {
      readonly phase: "settled";
      readonly relation: string;
      readonly intentKey: string | null;
      readonly kind: SettledKind;
      readonly reasonCode: string | null;
      /** Relation-specific explanation supplied by the caller (e.g. an input-rejection reason in plain words). */
      readonly detail: string | null;
      readonly reconstruction: Reconstruction;
    };

export type EffectField = {
  readonly current: EffectState;
  /** relation → intent key whose consequence is still unknown. */
  readonly retained: Readonly<Record<string, string>>;
};

export type EffectEvent =
  | { readonly type: "request"; readonly relation: string; readonly intentKey: string | null }
  | { readonly type: "settle"; readonly kind: SettledKind; readonly reasonCode: string | null; readonly detail?: string }
  | { readonly type: "reconstruction"; readonly result: "reading" | "done" | "failed" };

export const INITIAL_EFFECT_FIELD: EffectField = { current: { phase: "possible" }, retained: {} };

function withoutKey(retained: Readonly<Record<string, string>>, relation: string): Readonly<Record<string, string>> {
  if (!(relation in retained)) return retained;
  const next = { ...retained };
  delete next[relation];
  return next;
}

export function effectReducer(field: EffectField, event: EffectEvent): EffectField {
  const current = field.current;
  switch (event.type) {
    case "request": {
      if (blocksConsequence(field)) return field;
      return { ...field, current: { phase: "requested", relation: event.relation, intentKey: event.intentKey } };
    }
    case "settle": {
      if (current.phase !== "requested") return field;
      const semantics = describeOutcome(event.kind, "mutation");
      const retained =
        semantics.retainIntent && current.intentKey !== null
          ? { ...field.retained, [current.relation]: current.intentKey }
          : withoutKey(field.retained, current.relation);
      return {
        retained,
        current: {
          phase: "settled",
          relation: current.relation,
          intentKey: current.intentKey,
          kind: event.kind,
          reasonCode: event.reasonCode,
          detail: event.detail ?? null,
          reconstruction: "not_started",
        },
      };
    }
    case "reconstruction": {
      if (current.phase !== "settled") return field;
      return { ...field, current: { ...current, reconstruction: event.result } };
    }
  }
}

/** The key a new request for `relation` must carry: the retained one, if any. */
export function intentKeyFor(field: EffectField, relation: string, fresh: string): string {
  return field.retained[relation] ?? fresh;
}

/**
 * True while a consequential control must not be operable: a request is in
 * flight, or the canonical state is being (or could not be) re-read after an
 * outcome (21 §22: re-read before permitting dependent effects).
 */
export function blocksConsequence(field: EffectField): boolean {
  const c = field.current;
  if (c.phase === "requested") return true;
  if (c.phase === "settled") return c.reconstruction === "reading" || c.reconstruction === "failed";
  return false;
}
