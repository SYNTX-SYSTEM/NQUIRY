"use client";
/**
 * SF-01 effect runner: binds the pure lifecycle (`effectLifecycle.ts`) to one
 * surface's consequential relations.
 *
 *   request → send (one intent key per logical intent) → settle(kind)
 *   → committed + navigation to the newly established context, OR
 *   → canonical re-read (reconstruction) → done | failed
 *
 * Every settled outcome that stays on the surface is followed by a canonical
 * re-read (21 §22). Failures are re-read too, so a STALE or UNKNOWN outcome is
 * reconciled before anything may be repeated. A thrown `send` (a response
 * outside every known kind) is INDETERMINATE: consequence unknown, never
 * "failed".
 *
 * `inFlight` is a synchronous guard. Two clicks inside one render must not
 * send two Commands (the reducer would ignore the second request, but its
 * network call would already be on the wire).
 */
import { useReducer, useRef } from "react";
import { blocksConsequence, effectReducer, INITIAL_EFFECT_FIELD, intentKeyFor } from "./effectLifecycle";
import type { SettledKind } from "./outcomeSemantics";

export type Settlement<T> =
  | { readonly kind: "committed"; readonly reasonCode: null; readonly body: T; readonly detail?: string }
  | { readonly kind: Exclude<SettledKind, "committed">; readonly reasonCode: string; readonly detail?: string };

type EffectRunBase<T> = {
  readonly relation: string;
  /** Canonical re-read of this surface. Resolves true only if a current projection was obtained. */
  readonly reconstruct: () => Promise<boolean>;
  /** Called on commit. Return true when it moved to the newly established context (no re-read here). */
  readonly onCommitted?: (body: T) => boolean;
};

/** `keyed`: the Command carries an Idempotency-Key (F02 routes). Keyless: F01 routes without one. */
export type EffectRun<T> =
  | (EffectRunBase<T> & { readonly keyed: true; readonly send: (intentKey: string) => Promise<Settlement<T>> })
  | (EffectRunBase<T> & { readonly keyed: false; readonly send: () => Promise<Settlement<T>> });

/** Map an F02 envelope `CommandResult` (or F01 result of the same shape) to a Settlement. */
export function settleCommand<T>(
  result: { readonly kind: "committed"; readonly body: T } | { readonly kind: Exclude<SettledKind, "committed">; readonly reasonCode: string },
): Settlement<T> {
  return result.kind === "committed"
    ? { kind: "committed", reasonCode: null, body: result.body }
    : { kind: result.kind, reasonCode: result.reasonCode };
}

export function useEffectField() {
  const [field, dispatch] = useReducer(effectReducer, INITIAL_EFFECT_FIELD);
  const inFlight = useRef(false);

  async function reread(reconstruct: () => Promise<boolean>): Promise<void> {
    dispatch({ type: "reconstruction", result: "reading" });
    let ok = false;
    try {
      ok = await reconstruct();
    } catch {
      ok = false;
    }
    dispatch({ type: "reconstruction", result: ok ? "done" : "failed" });
  }

  async function run<T>(spec: EffectRun<T>): Promise<void> {
    if (inFlight.current || blocksConsequence(field)) return;
    inFlight.current = true;
    try {
      let send: () => Promise<Settlement<T>>;
      if (spec.keyed) {
        const intentKey = intentKeyFor(field, spec.relation, crypto.randomUUID());
        dispatch({ type: "request", relation: spec.relation, intentKey });
        send = () => spec.send(intentKey);
      } else {
        dispatch({ type: "request", relation: spec.relation, intentKey: null });
        send = spec.send;
      }
      let settlement: Settlement<T>;
      try {
        settlement = await send();
      } catch {
        settlement = { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" };
      }
      dispatch({ type: "settle", kind: settlement.kind, reasonCode: settlement.reasonCode, detail: settlement.detail });
      if (settlement.kind === "committed" && spec.onCommitted?.(settlement.body)) return;
      await reread(spec.reconstruct);
    } finally {
      inFlight.current = false;
    }
  }

  /** Manual re-read (after a failed reconstruction). A read, never a consequence. */
  async function rereadNow(reconstruct: () => Promise<boolean>): Promise<void> {
    if (inFlight.current) return;
    const c = field.current;
    if (c.phase !== "settled") return;
    inFlight.current = true;
    try {
      await reread(reconstruct);
    } finally {
      inFlight.current = false;
    }
  }

  return { field, run, rereadNow, blocked: blocksConsequence(field) };
}
