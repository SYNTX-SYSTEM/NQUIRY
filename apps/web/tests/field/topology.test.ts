/**
 * SF-02 WU-SF02.1 (L0): Field topology derivation is pure and deterministic (22 §29.2:
 * "Derived state must be deterministic from authoritative input and local presentation
 * constraints"), so SSR and client agree (22 §35.7) and resize changes nothing semantic (§35.11).
 *
 * MUST BECOME TRUE: orbit positions are a function of (index, count) only; the first node sits at
 * the top; nodes are evenly spaced; too many nodes fall back to a relational stack (22 §11.2 "Orbit
 * must not be used when … viewport would destroy semantic order"); node/path state derives from
 * capability and projection state only; lifecycle label density follows gravity (22 §16.2).
 * MUST REMAIN IMPOSSIBLE: a possible relation from a false capability (falsifier 2); a position that
 * depends on viewport, time or randomness; a relation path state that is not one of 22 §11.4.
 */
import { describe, expect, it } from "vitest";
import {
  affordanceState,
  lifecycleEmphasis,
  PATH_STATES,
} from "../../lib/field/topology";

describe("affordanceState", () => {
  it("possible only when the server capability is true; unavailable otherwise", () => {
    expect(affordanceState({ available: true, reasonCode: null, reason: null })).toBe("possible");
    expect(affordanceState({ available: false, reasonCode: "NO_X", reason: "…" })).toBe("unavailable");
  });
  it("the path vocabulary is exactly 22 §11.4", () => {
    expect([...PATH_STATES].sort()).toEqual(
      ["authority", "current", "denied", "dependency", "established", "governance", "historical", "loading", "possible", "unavailable"].sort(),
    );
  });
});

describe("lifecycleEmphasis (doc 23 §13.5: emphasis, never visibility)", () => {
  const phases = ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS"].map((state, i) => ({
    state,
    status: (i < 2 ? "done" : i === 2 ? "current" : "upcoming") as "done" | "current" | "upcoming",
  }));
  it("gives full emphasis to every passed phase, the current phase and the next one; later phases are low-gravity", () => {
    const e = lifecycleEmphasis(phases);
    expect(e.get("DRAFT")).toBe("full");
    expect(e.get("SETUP")).toBe("full");
    expect(e.get("CHALLENGE_CAPTURE")).toBe("full");
    expect(e.get("QUESTION_GENERATION")).toBe("full");
    expect(e.get("QUESTION_CAPTURE")).toBe("low");
    expect(e.get("ANALYSIS")).toBe("low");
  });
  it("never drops a phase", () => {
    expect(lifecycleEmphasis(phases).size).toBe(phases.length);
  });
});
