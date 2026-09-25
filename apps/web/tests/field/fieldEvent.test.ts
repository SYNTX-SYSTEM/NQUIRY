/**
 * SF-05 WU-26.5 (L0): the commit resonance derivation (doc 26 §27, §43 falsifiers 1–4, 9–10).
 */
import { describe, expect, it } from "vitest";
import { effectReducer, INITIAL_EFFECT_FIELD, type EffectEvent, type EffectField } from "../../lib/field/effectLifecycle";
import { deriveFieldEvent } from "../../lib/field/fieldEvent";

const run = (...events: EffectEvent[]): EffectField => events.reduce(effectReducer, INITIAL_EFFECT_FIELD);
const describeGrant = (relation: string) => (relation === "grant" ? { title: "SESSION CONTROL GRANTED", text: "Fay now holds Session control for this Challenge." } : null);

describe("deriveFieldEvent: only a confirmed, re-read, described effect becomes an event", () => {
  it("is null at rest, while requested, and while the re-read is pending (falsifier 1: never before the re-read)", () => {
    expect(deriveFieldEvent(INITIAL_EFFECT_FIELD, describeGrant)).toBeNull();
    expect(deriveFieldEvent(run({ type: "request", relation: "grant", intentKey: "k1" }), describeGrant)).toBeNull();
    const settled = run({ type: "request", relation: "grant", intentKey: "k1" }, { type: "settle", kind: "committed", reasonCode: null });
    expect(deriveFieldEvent(settled, describeGrant)).toBeNull();
    const reading = effectReducer(settled, { type: "reconstruction", result: "reading" });
    expect(deriveFieldEvent(reading, describeGrant)).toBeNull();
  });
  it("exists after the canonical re-read confirmed the effect, with the described scope and a stable id", () => {
    const done = run({ type: "request", relation: "grant", intentKey: "k1" }, { type: "settle", kind: "committed", reasonCode: null }, { type: "reconstruction", result: "reading" }, { type: "reconstruction", result: "done" });
    const event = deriveFieldEvent(done, describeGrant);
    expect(event).toEqual({ id: "grant:k1", relation: "grant", title: "SESSION CONTROL GRANTED", text: "Fay now holds Session control for this Challenge." });
    expect(deriveFieldEvent(done, describeGrant)).toEqual(event);
  });
  it("never says success for a failed, denied or unknown consequence (falsifier 2)", () => {
    for (const kind of ["denied", "rejected", "stale", "blocked", "failed_precommit", "indeterminate", "network_failure"] as const) {
      const f = run({ type: "request", relation: "grant", intentKey: "k1" }, { type: "settle", kind, reasonCode: "X" }, { type: "reconstruction", result: "reading" }, { type: "reconstruction", result: "done" });
      expect(deriveFieldEvent(f, describeGrant)).toBeNull();
    }
  });
  it("is null when the re-read failed (the confirmed state is unknown) and for a relation the surface did not describe (no generic Success)", () => {
    const failed = run({ type: "request", relation: "grant", intentKey: "k1" }, { type: "settle", kind: "committed", reasonCode: null }, { type: "reconstruction", result: "reading" }, { type: "reconstruction", result: "failed" });
    expect(deriveFieldEvent(failed, describeGrant)).toBeNull();
    const other = run({ type: "request", relation: "something-else", intentKey: null }, { type: "settle", kind: "committed", reasonCode: null }, { type: "reconstruction", result: "reading" }, { type: "reconstruction", result: "done" });
    expect(deriveFieldEvent(other, describeGrant)).toBeNull();
    expect(deriveFieldEvent(other, () => ({ title: "MEMBER ADDED", text: "…" }))?.id).toBe("something-else:keyless");
  });
});
