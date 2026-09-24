/**
 * SF-01 WU-SF01.5 (L5): static architecture gates over every SF-01 source file.
 *
 * MUST REMAIN IMPOSSIBLE (SF-01 human decisions + 21 §43 anti-patterns):
 * - timer semantics (Presentation Time ≠ System Authority);
 * - client authority inference (role / viewer flags gating anything);
 * - F03 vocabulary (capture, Burst, participation, completion): WAIT_FOR_F03;
 * - AI invocation or AI vocabulary beyond the inert origin grammar;
 * - client persistence of state (Client State ≠ Authority);
 * - importing the F03 contact zone (Session page, F02 Outcome).
 *
 * Each predicate is proven non-vacuous against a violating sample first.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

const WEB = join(__dirname, "..", "..");

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}

const SF01_SOURCES = [
  ...walk(join(WEB, "components", "field")),
  ...walk(join(WEB, "lib", "field")),
  join(WEB, "app", "workspaces", "page.tsx"),
  join(WEB, "app", "workspaces", "[workspaceId]", "page.tsx"),
  join(WEB, "app", "workspaces", "[workspaceId]", "challenges", "[challengeId]", "page.tsx"),
].filter((p) => /\.(ts|tsx)$/.test(p));

/** Code only: comments are stripped so documentation may name what it forbids. */
function code(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
}

const GATES: readonly { readonly name: string; readonly pattern: RegExp; readonly violation: string }[] = [
  { name: "no timer semantics", pattern: /\bset(Timeout|Interval)\s*\(/, violation: "setTimeout(() => complete(), 1000)" },
  {
    name: "no role- or viewer-flag authority inference",
    pattern: /\brole\s*[!=]==?|\bviewer\.(role|isGovernanceRoot|isSessionController)\b|\bisGovernanceRoot\b|\bisSessionController\b/,
    violation: 'if (viewer.role === "Owner") showGrant()',
  },
  {
    name: "no F03 vocabulary (WAIT_FOR_F03)",
    pattern: /QuestionBurst|\bburst\b|capture|PARTICIPATION|participant|CLOSE_QUESTION_GENERATION|original_?[tT]ext|freeze|frozen/i,
    violation: "const capture = position.burst.questions",
  },
  { name: "no AI invocation", pattern: /ai_gateway|openai|anthropic|\/ai\/|generate\(/i, violation: "fetch('/ai/analyse')" },
  { name: "no client persistence of state", pattern: /localStorage|sessionStorage|indexedDB/, violation: "localStorage.setItem('state', s)" },
  {
    name: "no import from the F03 contact zone",
    pattern: /from\s+["'][^"']*(sessions\/\[sessionId\]|f02\/Outcome)["']/,
    violation: 'import { Outcome } from "../../components/f02/Outcome";',
  },
];

describe("gate predicates are non-vacuous", () => {
  for (const gate of GATES) {
    it(`${gate.name}: catches a violating sample`, () => {
      expect(gate.pattern.test(gate.violation)).toBe(true);
    });
  }

  it("covers every SF-01 source file (the file set is not empty or partial)", () => {
    const names = SF01_SOURCES.map((p) => relative(WEB, p)).sort();
    expect(names).toEqual(
      expect.arrayContaining([
        "app/workspaces/page.tsx",
        "components/field/EffectSurface.tsx",
        "components/field/FieldFrame.tsx",
        "lib/field/effectLifecycle.ts",
        "lib/field/outcomeSemantics.ts",
        "lib/field/position.ts",
        "lib/field/useEffectField.ts",
      ]),
    );
    expect(names.length).toBeGreaterThanOrEqual(13);
  });
});

describe("MUST REMAIN IMPOSSIBLE in SF-01 sources", () => {
  for (const gate of GATES) {
    it(gate.name, () => {
      const offenders = SF01_SOURCES.filter((p) => gate.pattern.test(code(readFileSync(p, "utf8")))).map((p) =>
        relative(WEB, p),
      );
      expect(offenders).toEqual([]);
    });
  }
});
