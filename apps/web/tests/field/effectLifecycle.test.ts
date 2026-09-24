/**
 * SF-01 WU-SF01.1 (L0): effect lifecycle as a pure relation reducer.
 * Governing: 21 §17 (POSSIBLE → REQUESTED → … → COMMITTED | typed outcome), §22 (reconstruction,
 * C3-06 committed-but-reconstruction-unavailable), CF-08; 20 §13 (UI DEBOUNCE ≠ IDEMPOTENCY).
 */
import { describe, expect, it } from "vitest";
import {
  blocksConsequence,
  effectReducer,
  INITIAL_EFFECT_FIELD,
  intentKeyFor,
  type EffectField,
} from "../../lib/field/effectLifecycle";

function run(...events: Parameters<typeof effectReducer>[1][]): EffectField {
  return events.reduce(effectReducer, INITIAL_EFFECT_FIELD);
}

describe("MUST BECOME TRUE", () => {
  it("starts possible, with nothing requested and nothing retained", () => {
    expect(INITIAL_EFFECT_FIELD.current).toEqual({ phase: "possible" });
    expect(INITIAL_EFFECT_FIELD.retained).toEqual({});
    expect(blocksConsequence(INITIAL_EFFECT_FIELD)).toBe(false);
  });

  it("request → requested; the request itself is not an effect", () => {
    const f = run({ type: "request", relation: "create-challenge", intentKey: "k1" });
    expect(f.current).toEqual({ phase: "requested", relation: "create-challenge", intentKey: "k1" });
    expect(blocksConsequence(f)).toBe(true);
  });

  it("settle → settled with reconstruction not yet started", () => {
    const f = run(
      { type: "request", relation: "add-member", intentKey: null },
      { type: "settle", kind: "committed", reasonCode: null },
    );
    expect(f.current).toMatchObject({ phase: "settled", relation: "add-member", kind: "committed", reconstruction: "not_started" });
  });

  it("reconstruction progresses reading → done, and only a finished reconstruction releases consequence controls", () => {
    let f = run(
      { type: "request", relation: "add-member", intentKey: null },
      { type: "settle", kind: "committed", reasonCode: null },
      { type: "reconstruction", result: "reading" },
    );
    expect(f.current).toMatchObject({ reconstruction: "reading" });
    expect(blocksConsequence(f)).toBe(true);
    f = effectReducer(f, { type: "reconstruction", result: "done" });
    expect(f.current).toMatchObject({ reconstruction: "done" });
    expect(blocksConsequence(f)).toBe(false);
  });

  it("C3-06: committed + failed reconstruction keeps the commit and blocks dependent consequence", () => {
    const f = run(
      { type: "request", relation: "grant", intentKey: "k" },
      { type: "settle", kind: "committed", reasonCode: null },
      { type: "reconstruction", result: "reading" },
      { type: "reconstruction", result: "failed" },
    );
    expect(f.current).toMatchObject({ phase: "settled", kind: "committed", reconstruction: "failed" });
    expect(blocksConsequence(f)).toBe(true);
  });

  it("unknown consequence retains the intent key for the SAME relation; a definitive outcome releases it", () => {
    let f = run(
      { type: "request", relation: "create-challenge", intentKey: "k1" },
      { type: "settle", kind: "network_failure", reasonCode: "NETWORK_FAILURE" },
    );
    expect(f.retained).toEqual({ "create-challenge": "k1" });
    expect(intentKeyFor(f, "create-challenge", "fresh")).toBe("k1");
    expect(intentKeyFor(f, "grant", "fresh")).toBe("fresh");

    // Another relation in between does not lose the retained intent.
    f = effectReducer(f, { type: "request", relation: "grant", intentKey: "g1" });
    f = effectReducer(f, { type: "settle", kind: "denied", reasonCode: "X" });
    expect(intentKeyFor(f, "create-challenge", "fresh")).toBe("k1");

    f = effectReducer(f, { type: "request", relation: "create-challenge", intentKey: "k1" });
    f = effectReducer(f, { type: "settle", kind: "committed", reasonCode: null });
    expect(f.retained).toEqual({});
  });

  it("server INDETERMINATE also retains the intent (a new key could duplicate the effect)", () => {
    const f = run(
      { type: "request", relation: "open-session", intentKey: "k" },
      { type: "settle", kind: "indeterminate", reasonCode: "COMMIT_OUTCOME_UNPROVEN" },
    );
    expect(intentKeyFor(f, "open-session", "fresh")).toBe("k");
  });

  it("keyless relations (F01 routes without Idempotency-Key) never retain anything", () => {
    const f = run(
      { type: "request", relation: "create-workspace", intentKey: null },
      { type: "settle", kind: "network_failure", reasonCode: "NETWORK_FAILURE" },
    );
    expect(f.retained).toEqual({});
  });

  it("a new request replaces the previous outcome (no page-local residue survives the next intent)", () => {
    const f = run(
      { type: "request", relation: "add-member", intentKey: null },
      { type: "settle", kind: "committed", reasonCode: null },
      { type: "reconstruction", result: "reading" },
      { type: "reconstruction", result: "done" },
      { type: "request", relation: "create-challenge", intentKey: "k" },
    );
    expect(f.current).toEqual({ phase: "requested", relation: "create-challenge", intentKey: "k" });
  });
});

describe("MUST REMAIN IMPOSSIBLE", () => {
  it("F7/F8: no transition to settled without a request (a click cannot fabricate an outcome)", () => {
    const f = run({ type: "settle", kind: "committed", reasonCode: null });
    expect(f).toEqual(INITIAL_EFFECT_FIELD);
  });

  it("no second request while one is requested (duplicate consequence)", () => {
    const f = run(
      { type: "request", relation: "a", intentKey: "k1" },
      { type: "request", relation: "b", intentKey: "k2" },
    );
    expect(f.current).toEqual({ phase: "requested", relation: "a", intentKey: "k1" });
  });

  it("no request while reconstruction is still reading (stale view must not be actionable)", () => {
    const f = run(
      { type: "request", relation: "a", intentKey: null },
      { type: "settle", kind: "stale", reasonCode: "STALE_VERSION" },
      { type: "reconstruction", result: "reading" },
      { type: "request", relation: "a", intentKey: null },
    );
    expect(f.current).toMatchObject({ phase: "settled", kind: "stale", reconstruction: "reading" });
  });

  it("reconstruction events without a settled outcome are ignored", () => {
    expect(run({ type: "reconstruction", result: "done" })).toEqual(INITIAL_EFFECT_FIELD);
  });

  it("a settle event for a request never made is ignored even after an earlier outcome", () => {
    const f = run(
      { type: "request", relation: "a", intentKey: null },
      { type: "settle", kind: "denied", reasonCode: "X" },
      { type: "settle", kind: "committed", reasonCode: null },
    );
    expect(f.current).toMatchObject({ kind: "denied" });
  });
});
