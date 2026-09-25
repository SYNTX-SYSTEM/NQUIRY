/**
 * SF-05 (doc 26 §27) Commit resonance — the derivation of a TRANSIENT FIELD EVENT from the effect lifecycle.
 *
 *   REQUEST → COMMIT → CANONICAL RE-READ → CONFIRMED EFFECT → TRANSIENT FIELD EVENT
 *
 * An event exists only for a settled, COMMITTED effect whose canonical re-read is DONE (the projection on screen is
 * the confirmed state); never before the re-read, never for a failed/unknown consequence, never for a relation the
 * surface did not describe (no generic "Success"). The event is projection only: it carries the human-readable
 * effect the surface described at request time (scope included — Challenge control ≠ Session control) and it is
 * never a source of truth; the persistent proof stays in the chamber. Pure: no I/O, no timers.
 */
import type { EffectField } from "./effectLifecycle";

export type FieldEventDescription = {
  /** Short uppercase effect name, e.g. "SESSION CONTROL GRANTED". */
  readonly title: string;
  /** One human-readable sentence naming the effect and its scope. */
  readonly text: string;
};

export type FieldEvent = FieldEventDescription & {
  /** Stable per confirmed effect: the relation plus its intent key (or "keyless"). */
  readonly id: string;
  readonly relation: string;
};

export function deriveFieldEvent(field: EffectField, describe: (relation: string) => FieldEventDescription | null): FieldEvent | null {
  const c = field.current;
  if (c.phase !== "settled" || c.kind !== "committed" || c.reconstruction !== "done") return null;
  const description = describe(c.relation);
  if (!description) return null;
  return { id: `${c.relation}:${c.intentKey ?? "keyless"}`, relation: c.relation, ...description };
}
