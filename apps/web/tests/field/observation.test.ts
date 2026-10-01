/**
 * CYAN-PCPG-05 falsifiers at the state-machine level (Architecture 27 v4 §14, §21; commit b0a5101): no provisional
 * result while observing, failures never replace a valid observation, malformed fails closed, supersession by
 * canonical versions only (no clock), a new observation replaces the previous one, nothing persisted.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { parsePromptObservation, type PromptObservation, type PromptObservationResult } from "../../lib/api/pcpgClient";
import { INITIAL_OBSERVATION, observationReducer, presenceFor, runObservation, type ObservationState } from "../../lib/field/observation";
import { membraneLabel, presentationOf } from "../../lib/field/pcpgPresentation";

const WEB = join(__dirname, "..", "..");
const D = { deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: null, result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED" };
function envelope(governanceObservation: unknown, digest = "ab".repeat(32)): PromptObservationResult {
  return parsePromptObservation({ kind: "ok", field: "PRE_CALL_PROMPT_GOVERNANCE", workspace: { workspaceId: "w", name: "W" }, session: { sessionId: "s" }, rawIntent: "Analyse the questions", rawIntentLength: 21, rawIntentDigestSha256: digest, declaredPurpose: null, observedAt: "2026-10-01T11:17:00+00:00", governanceObservation });
}
const CURRENT = (partial = false, digest?: string) => envelope({ kind: "current", contract: "PCPG-R12/1", basis: { rawIntentDigestSha256: "ab".repeat(32), derivationTime: "2026-10-01T11:17:00+00:00" }, semanticObservation: { ruleSetVersion: "v", clauses: [], actions: [], unknownRelations: [], relationsTouched: [], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false }, deltas: [D], chain: { firstBrokenRelation: null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial }, capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend: false }, composedProofCeiling: null }, digest);
const UNAVAILABLE = envelope({ kind: "unavailable", reasonCode: "SEMANTIC_OBSERVATION_UNAVAILABLE" });
const MALFORMED = envelope({ kind: "current", contract: "PCPG-R12/2" });
const V1 = { session: 4, burst: 2 };
const V2 = { session: 5, burst: 2 };
const observe = (state: ObservationState, result: PromptObservationResult, versions = V1) => observationReducer(observationReducer(state, { type: "requested" }), { type: "result", result, versions });
const label = (s: ObservationState, v = V1) => membraneLabel(presenceFor(s, v));

describe("state machine (falsifiers 1, 5, 6, 7, 8, 9, 10, 11, 12)", () => {
  it("1. requested keeps the presence untouched: the membrane stays 'No observation' (or the previous observation) until a real result", () => {
    const s = observationReducer(INITIAL_OBSERVATION, { type: "requested" });
    expect(s.phase).toBe("observing");
    expect(presenceFor(s, V1)).toEqual({ kind: "none" });
    expect(label(s)).toBe("NO_OBSERVATION");
    const after = observe(INITIAL_OBSERVATION, CURRENT());
    const again = observationReducer(after, { type: "requested" });
    expect(label(again)).toBe("PROVIDER_NOT_EXECUTABLE");
    expect(again.failure).toBeNull();
  });
  it("5. ok + current stores the observation with supersededByObjectChange false and the versions; the membrane shows the real derived label", () => {
    const s = observe(INITIAL_OBSERVATION, CURRENT());
    expect(s.presence).toMatchObject({ kind: "observation", supersededByObjectChange: false });
    expect(s.observedVersions).toEqual(V1);
    expect(s.phase).toBe("idle");
    expect(s.failure).toBeNull();
    expect(label(s)).toBe("PROVIDER_NOT_EXECUTABLE");
    expect((s.envelope as PromptObservation).observedAt).toBe("2026-10-01T11:17:00+00:00");
  });
  it("6. ok + unavailable becomes 'Governance unavailable' only: nothing synthesized", () => {
    const s = observe(INITIAL_OBSERVATION, UNAVAILABLE);
    expect(label(s)).toBe("GOVERNANCE_UNAVAILABLE");
    expect(presentationOf(presenceFor(s, V1)).aggregates).toEqual({ observation: "unavailable" });
    expect(s.observedVersions).toEqual(V1);
  });
  it("7./8./9./10. rejected, denied, not_found, indeterminate and network failure never replace a valid observation; the failure is exposed", () => {
    const valid = observe(INITIAL_OBSERVATION, CURRENT());
    for (const failure of [
      { kind: "rejected", reasonCode: "RAW_INTENT_TOO_LONG" },
      { kind: "denied", reasonCode: "WORKSPACE_NOT_ACCESSIBLE" },
      { kind: "not_found", reasonCode: "SESSION_NOT_FOUND" },
      { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" },
      { kind: "network_failure", reasonCode: "NETWORK_FAILURE" },
    ] as const) {
      const s = observe(valid, failure);
      expect(s.presence).toBe(valid.presence);
      expect(s.envelope).toBe(valid.envelope);
      expect(s.observedVersions).toEqual(V1);
      expect(s.failure).toEqual(failure);
      expect(label(s)).toBe("PROVIDER_NOT_EXECUTABLE");
      // and from "none", a failure leaves "none": nothing is assumed
      const n = observe(INITIAL_OBSERVATION, failure);
      expect(n.presence).toEqual({ kind: "none" });
      expect(label(n)).toBe("NO_OBSERVATION");
    }
  });
  it("11. a malformed projection fails closed: presence malformed → 'Governance unavailable', no envelope, no versions", () => {
    const s = observe(observe(INITIAL_OBSERVATION, CURRENT()), MALFORMED);
    expect(s.presence).toEqual({ kind: "malformed" });
    expect(s.envelope).toBeNull();
    expect(s.observedVersions).toBeNull();
    expect(s.failure).toMatchObject({ kind: "malformed", reasonCode: "MALFORMED_PROJECTION" });
    expect(label(s)).toBe("GOVERNANCE_UNAVAILABLE");
  });
  it("12. a second observation replaces the previous one entirely (new label, new digest, new versions)", () => {
    const first = observe(INITIAL_OBSERVATION, CURRENT(false, "aa".repeat(32)));
    const second = observe(first, CURRENT(true, "bb".repeat(32)), V2);
    expect(label(second, V2)).toBe("PARTIAL");
    expect((second.envelope as PromptObservation).rawIntentDigestSha256).toBe("bb".repeat(32));
    expect(second.observedVersions).toEqual(V2);
    expect(presenceFor(second, V2)).toMatchObject({ supersededByObjectChange: false });
  });
});

describe("supersession (falsifiers 13, 14)", () => {
  it("13. a changed canonical session or burst version marks the presentation superseded without mutating the observation", () => {
    const s = observe(INITIAL_OBSERVATION, CURRENT());
    const before = JSON.stringify(s);
    expect(presenceFor(s, V1)).toMatchObject({ supersededByObjectChange: false });
    expect(presenceFor(s, { session: 5, burst: 2 })).toMatchObject({ supersededByObjectChange: true });
    expect(presenceFor(s, { session: 4, burst: 3 })).toMatchObject({ supersededByObjectChange: true });
    expect(presenceFor(s, { session: 4, burst: null })).toMatchObject({ supersededByObjectChange: true });
    expect(label(s, V2)).toBe("SUPERSEDED");
    expect(JSON.stringify(s)).toBe(before);
    expect(presentationOf(presenceFor(s, V2)).aggregates.current?.capability.canSend).toBeNull();
  });
  it("14. no clock-based supersession: the module uses no Date, timers or observedAt comparison", () => {
    const src = readFileSync(join(WEB, "lib", "field", "observation.ts"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
    expect(src).not.toMatch(/Date\.|new Date|setTimeout|setInterval|observedAt|derivationTime|performance\.now/);
  });
});

describe("runner and persistence (falsifiers 3, 15, 16, 17)", () => {
  it("the runner dispatches requested then result with the versions it was given; the client decides the body (PCPG-01)", async () => {
    const events: unknown[] = [];
    const result = await runObservation((e) => events.push(e), async () => CURRENT(), V1);
    expect(result.kind).toBe("ok");
    expect(events).toEqual([{ type: "requested" }, { type: "result", result, versions: V1 }]);
  });
  it("16./17. no persistence and no logging of raw intent anywhere in the observation modules", () => {
    for (const f of ["lib/field/observation.ts", "lib/field/useObservation.ts", "components/field/IntentObservationChamber.tsx"]) {
      const src = readFileSync(join(WEB, f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
      expect(src, f).not.toMatch(/localStorage|sessionStorage|indexedDB|IndexedDB|document\.cookie|console\.|navigator\.sendBeacon/);
    }
  });
  it("3. the hook forwards exactly rawIntent, sessionId and an optional declaredPurpose to the PCPG-01 client — nothing else exists to forward", () => {
    const src = readFileSync(join(WEB, "lib", "field", "useObservation.ts"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
    expect(src).toMatch(/submitPromptObservation\(workspaceId, \{ rawIntent, sessionId, \.\.\.\(declaredPurpose \? \{ declaredPurpose \} : \{\}\) \}\)/);
    expect(src).not.toMatch(/capability|authority|governanceObservation|basis|providerEligib|sendGate|proofCeiling/);
  });
});
