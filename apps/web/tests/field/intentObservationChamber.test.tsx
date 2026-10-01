/**
 * CYAN-PCPG-05 chamber falsifiers (static markup): the control is "Observe" and nothing else; no role gating; the
 * legitimate failure presentation; the chamber never speaks governance (the membrane does); no persistence, no logs.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { IntentObservationChamber } from "../../components/field/IntentObservationChamber";
import { INITIAL_OBSERVATION, type ObservationState } from "../../lib/field/observation";

const WEB = join(__dirname, "..", "..");
const SRC = readFileSync(join(WEB, "components", "field", "IntentObservationChamber.tsx"), "utf8");
const code = SRC.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
const render = (state: ObservationState, superseded = false) =>
  renderToStaticMarkup(<IntentObservationChamber state={state} presence={state.presence.kind === "observation" ? { ...state.presence, supersededByObjectChange: superseded } : state.presence} onObserve={() => undefined} />);
const envelope = { field: "PRE_CALL_PROMPT_GOVERNANCE", workspace: { workspaceId: "w", name: "W" }, session: { sessionId: "s" }, rawIntent: "x", rawIntentLength: 1, rawIntentDigestSha256: "abcdef0123456789".repeat(4), declaredPurpose: null, observedAt: "2026-10-01T11:17:00+00:00", governanceObservation: { kind: "unavailable", reasonCode: "PROJECTION_INCOMPLETE" } } as const;
const OBSERVED: ObservationState = { presence: { kind: "observation", observation: envelope.governanceObservation, supersededByObjectChange: false }, envelope, observedVersions: { session: 1, burst: null }, phase: "idle", failure: null };

describe("the chamber (falsifiers 4, 18, 19, 22)", () => {
  it("is the architecture-defined context chamber: title 'Your intent', eyebrow 'observed, never sent', textarea, optional purpose, one control 'Observe'", () => {
    const html = render(INITIAL_OBSERVATION);
    expect(html).toContain('data-semantic="context"');
    expect(html).toContain('data-testid="intent-chamber"');
    expect(html).toMatch(/<h2[^>]*>Your intent<\/h2>/);
    expect(html).toContain("observed, never sent");
    expect(html).toMatch(/<label for="intent-text">Your intent<\/label>/);
    expect(html).toMatch(/<textarea[^>]*id="intent-text"[^>]*>/);
    expect(html).toMatch(/maxlength="8000"/i);
    expect(html).toContain('<label for="intent-purpose">Declared purpose (optional)</label>');
    expect(html.match(/<button[^>]*>/g)?.length).toBe(1);
    expect(html).toMatch(/<button[^>]*data-testid="observe-button"[^>]*>Observe<\/button>/);
  });
  it("18./19. no Send / Run / Execute / Submit-to-AI control, whatever the state", () => {
    for (const html of [render(INITIAL_OBSERVATION), render(OBSERVED), render({ ...OBSERVED, phase: "observing" })]) {
      expect(html).not.toMatch(/>\s*(Send|Run|Execute|Submit to AI|Submit)\s*</);
      expect(html).not.toMatch(/sendGate|Send allowed|Ready to send/);
    }
    expect(code).not.toMatch(/canSend|providerExecutable|governanceAdmissible/);
  });
  it("4. is not role-gated: the source reads no role, viewer flag, controller, binding, participation or capability", () => {
    expect(code).not.toMatch(/\.role\b|\brole\s*[!=]==?|viewer\.|isSessionController|isGovernanceRoot|binding|participant|actions\.|\bavailable\b/);
  });
  it("shows the pending state while observing and disables the control; never a provisional governance word", () => {
    const html = render({ ...INITIAL_OBSERVATION, phase: "observing" });
    expect(html).toContain('data-testid="observe-pending"');
    expect(html).toMatch(/<button[^>]*disabled[^>]*>Observe<\/button>/);
    expect(html).not.toMatch(/Observed<|Boundary|Authority required|unavailable/);
  });
  it("shows the legitimate failure presentation with the server's code, and keeps the previous observation facts", () => {
    for (const [kind, words] of [["rejected", "request was invalid"], ["denied", "denied the observation"], ["not_found", "not found"], ["network_failure", "could not be reached"], ["indeterminate", "Outcome unknown"], ["malformed", "fail closed"]] as const) {
      const html = render({ ...OBSERVED, failure: { kind, reasonCode: "X_CODE" } as never });
      expect(html).toContain(`data-outcome="${kind}"`);
      expect(html).toContain(words);
      expect(html).toContain("X_CODE");
      if (kind !== "malformed") expect(html).toContain('data-testid="observation-facts"');
    }
  });
  it("after an observation shows its own facts (observed at, digest, view-only note) and the superseded note only when superseded", () => {
    const html = render(OBSERVED);
    expect(html).toContain('data-testid="observed-at"');
    expect(html).toContain("abcdef012345…");
    expect(html).toContain("a reload returns to");
    expect(html).not.toContain("observe-superseded");
    expect(render(OBSERVED, true)).toContain('data-testid="observe-superseded"');
    // the chamber never states governance words: those belong to the membrane
    expect(html).not.toMatch(/Governance unavailable|Boundary reached|Human Authority|Provider not executable|Observed<\/span>/);
  });
  it("16./17. no persistence and no logging", () => {
    expect(code).not.toMatch(/localStorage|sessionStorage|indexedDB|console\.|fetch\(|pcpgClient/);
  });
});
