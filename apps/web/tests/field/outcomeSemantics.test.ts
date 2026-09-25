/**
 * SF-01 WU-SF01.1 (L0): Effect & Boundary grammar, consequence semantics.
 * Governing: 21 §14 (boundary taxonomy), §17 (effect lifecycle), §39 (verdict language),
 * §46 C3-01 (mutation transport loss), §42 falsifiers 17/18/21/22.
 */
import { describe, expect, it } from "vitest";
import { describeOutcome, SETTLED_KINDS, type SettledKind } from "../../lib/field/outcomeSemantics";

const NON_COMMIT: readonly SettledKind[] = ["denied", "rejected", "stale", "blocked", "failed_precommit", "not_found"];

describe("MUST BECOME TRUE: each settled kind has its own consequence semantics", () => {
  it("covers exactly the published F02 envelope kinds plus client-side network_failure", () => {
    expect([...SETTLED_KINDS].sort()).toEqual(
      [
        "blocked",
        "committed",
        "denied",
        "failed_precommit",
        "indeterminate",
        "network_failure",
        "not_found",
        "rejected",
        "stale",
      ].sort(),
    );
  });

  it("uses the 21 §39 verdict language for every boundary", () => {
    expect(describeOutcome("denied", "mutation").title).toBe(
      "This action is not permitted in the current authority and scope.",
    );
    expect(describeOutcome("rejected", "mutation").title).toBe("This request cannot be accepted in its current form.");
    expect(describeOutcome("stale", "mutation").title).toBe(
      "The visible state has changed since this action became available.",
    );
    expect(describeOutcome("blocked", "mutation").title).toBe(
      "This relation cannot continue until the required prerequisite exists.",
    );
    expect(describeOutcome("failed_precommit", "mutation").title).toBe("The requested change did not commit.");
    expect(describeOutcome("indeterminate", "mutation").title).toBe(
      "The system cannot currently determine whether the requested change committed.",
    );
    expect(describeOutcome("not_found", "read").title).toBe(
      "The referenced context is not available in the confirmed scope.",
    );
    expect(describeOutcome("network_failure", "read").title).toBe("The canonical system could not be reached.");
  });

  it("a commit is the only committed consequence", () => {
    expect(describeOutcome("committed", "mutation").consequence).toBe("committed");
    for (const kind of NON_COMMIT) {
      expect(describeOutcome(kind, "mutation").consequence).toBe("none");
    }
  });

  it("a mutation whose commit certainty is unknown stays unknown (C3-01)", () => {
    expect(describeOutcome("indeterminate", "mutation").consequence).toBe("unknown");
    expect(describeOutcome("network_failure", "mutation").consequence).toBe("unknown");
  });

  it("an unknown consequence keeps the logical intent and reconciles before any repeat", () => {
    for (const kind of ["indeterminate", "network_failure"] as const) {
      const d = describeOutcome(kind, "mutation");
      expect(d.retainIntent).toBe(true);
      expect(d.reconcileFirst).toBe(true);
    }
    for (const kind of [...NON_COMMIT, "committed"] as const) {
      const d = describeOutcome(kind, "mutation");
      expect(d.retainIntent).toBe(false);
      expect(d.reconcileFirst).toBe(false);
    }
  });

  it("a read has no effect consequence at all", () => {
    for (const kind of SETTLED_KINDS) {
      if (kind === "committed") continue;
      expect(describeOutcome(kind, "read").consequence).toBeNull();
    }
  });

  it("a commit is announced as status, a boundary as alert", () => {
    expect(describeOutcome("committed", "mutation").announce).toBe("status");
    for (const kind of [...NON_COMMIT, "indeterminate", "network_failure"] as const) {
      expect(describeOutcome(kind, "mutation").announce).toBe("alert");
    }
  });
});

describe("MUST REMAIN IMPOSSIBLE", () => {
  it("F17: network failure during a mutation never claims that nothing happened", () => {
    const d = describeOutcome("network_failure", "mutation");
    const text = `${d.title} ${d.consequenceText ?? ""}`.toLowerCase();
    expect(text).not.toMatch(/nothing (is assumed to have |has )?changed|no change was made|did not commit/);
    expect(d.consequenceText).toMatch(/unknown whether/i);
  });

  it("F18: INDETERMINATE never reads as a failure", () => {
    const d = describeOutcome("indeterminate", "mutation");
    expect(`${d.title} ${d.consequenceText ?? ""}`.toLowerCase()).not.toMatch(/failed|did not commit|no change/);
  });

  it("F21/F22: DENIED ≠ REJECTED and FAILED_PRECOMMIT ≠ INDETERMINATE (text and consequence)", () => {
    const denied = describeOutcome("denied", "mutation");
    const rejected = describeOutcome("rejected", "mutation");
    expect(denied.title).not.toBe(rejected.title);
    const fpc = describeOutcome("failed_precommit", "mutation");
    const ind = describeOutcome("indeterminate", "mutation");
    expect(fpc.title).not.toBe(ind.title);
    expect(fpc.consequence).not.toBe(ind.consequence);
  });

  it("no two kinds share a title (no generic error collapse)", () => {
    const titles = SETTLED_KINDS.map((k) => describeOutcome(k, "mutation").title);
    expect(new Set(titles).size).toBe(titles.length);
  });

  it("rejects kinds outside the published vocabulary (fail closed, no F03 kind invented)", () => {
    expect(() => describeOutcome("closed" as SettledKind, "mutation")).toThrow();
  });
});

describe("SF-02: read failure must not use mutation language (22 §4.7, falsifier 13; SF-01 review D-2)", () => {
  it("INDETERMINATE and NETWORK_FAILURE on a READ speak of the projection, never of a requested change", () => {
    for (const kind of ["indeterminate", "network_failure"] as const) {
      const d = describeOutcome(kind, "read");
      expect(d.title.toLowerCase()).not.toMatch(/requested change|committed|change was made/);
      expect(d.title.toLowerCase()).toMatch(/projection|reached/);
    }
  });
  it("the same kinds on a MUTATION keep the 21 §39 consequence language", () => {
    expect(describeOutcome("indeterminate", "mutation").title).toMatch(/requested change committed/);
  });
  it("read titles stay distinct per kind (no generic error collapse)", () => {
    const titles = SETTLED_KINDS.filter((k) => k !== "committed").map((k) => describeOutcome(k, "read").title);
    expect(new Set(titles).size).toBe(titles.length);
  });
});
