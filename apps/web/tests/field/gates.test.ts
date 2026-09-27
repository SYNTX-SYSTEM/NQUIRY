/**
 * SF-02 WU-SF02.1 (L5): static architecture gates over every Symbiotic Field source file.
 * Supersedes the SF-01 gates: F03 is published and synced, so its vocabulary is no longer
 * WAIT_FOR_F03; F04 is not, so its vocabulary is (22 §36.4, §45.2/45.3: analysis contact is
 * absent from this tree, never mocked).
 *
 * MUST REMAIN IMPOSSIBLE (22 §29.4, §43; falsifiers 1, 2, 27, 30, 41):
 * - a timer that drives an effect (HD-11: the only timer is the elapsed-time PRESENTATION);
 * - client authority inference (role / viewer flags gating a control; humanPosition is a label);
 * - WU-CY-01 (HD-27, pinned producer checkpoint-PFC-B5): the ANALYSIS boundary is consumed, so `BEGIN_ANALYSIS`
 *   and its route may appear ONLY where the position projection is consumed (the Session page and
 *   lib/field/analysis.ts); a provider, an AI operation id or an analysis contact is still never named in the
 *   client, and the derived artifact's content is never rendered (no AI text in the human voice);
 * - AI invocation; client persistence of state; the F02 page-local Outcome; green as an identity.
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

const FIELD_SOURCES = [
  ...walk(join(WEB, "components", "field")),
  ...walk(join(WEB, "components", "f03")),
  ...walk(join(WEB, "lib", "field")),
  join(WEB, "lib", "burst.ts"),
  join(WEB, "app", "login", "page.tsx"),
  join(WEB, "app", "workspaces", "page.tsx"),
  join(WEB, "app", "workspaces", "[workspaceId]", "page.tsx"),
  join(WEB, "app", "workspaces", "[workspaceId]", "challenges", "[challengeId]", "page.tsx"),
  join(WEB, "app", "workspaces", "[workspaceId]", "sessions", "[sessionId]", "page.tsx"),
].filter((p) => /\.(ts|tsx)$/.test(p));

const rel = (p: string) => relative(WEB, p).split("\\").join("/");

/** Code only: comments are stripped so documentation may name what it forbids. */
function code(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
}

const COMMAND_FUNCTIONS =
  /\b(captureBurstQuestion|completeBurst|runSessionCommand|grantSessionControl|openSession|createChallenge|addMemberCommand|createWorkspace|login|logout)\s*\(/;

type Gate = {
  readonly name: string;
  readonly pattern: RegExp;
  readonly violation: string;
  /** Presentation-only files that may name the vocabulary (never a command or auth call). */
  readonly allow?: readonly string[];
  /** Files that CONSUME the producer's projection (they run commands through the effect lifecycle); WU-CY-01. */
  readonly consumers?: readonly string[];
};

const GATES: readonly Gate[] = [
  {
    name: "no timer semantics outside the elapsed-time presentation (HD-11)",
    pattern: /\bset(Timeout|Interval)\s*\(/,
    violation: "setTimeout(() => complete(), 1000)",
    allow: ["components/f03/BurstTimer.tsx"],
  },
  {
    name: "no role- or viewer-flag authority inference (human position is a label, not a gate)",
    pattern: /\brole\s*[!=]==?|\bviewer\.(role|isGovernanceRoot|isSessionController)\b|\bisGovernanceRoot\b|\bisSessionController\b/,
    violation: 'if (viewer.role === "Owner") showGrant()',
    allow: ["lib/field/humanPosition.ts"],
  },
  {
    name: "BEGIN_ANALYSIS is consumed only where the position projection is consumed (WU-CY-01, HD-27)",
    pattern: /BEGIN_ANALYSIS|begin-analysis|TRN_SESS_006/,
    violation: "actions.BEGIN_ANALYSIS.available",
    consumers: ["app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx", "lib/field/analysis.ts"],
  },
  {
    name: "no provider, AI operation or analysis contact is named in the client (the producer decides; never mocked here)",
    pattern: /AIOP|MockProvider|ai_gateway|AnalysisContact|analysis-contact|NQUIRY_AI_PROVIDER/,
    violation: "if (provider === 'MockProvider')",
  },
  {
    name: "no AI-derived text is rendered: the artifact content and the clusters never reach the projection (WU-CY-01 scope)",
    pattern: /artifact\??\.content|\.clusters\b|clustering\??\.clusters/,
    violation: "analysis.artifact.content.items.map(render)",
  },
  { name: "no AI invocation", pattern: /openai|anthropic|\/ai\/|generate\(/i, violation: "fetch('/ai/analyse')" },
  { name: "no client persistence of state", pattern: /localStorage|sessionStorage|indexedDB/, violation: "localStorage.setItem('state', s)" },
  {
    name: "no page-local F02 Outcome in Field sources (one effect lifecycle per surface)",
    pattern: /from\s+["'][^"']*f02\/Outcome["']/,
    violation: 'import { Outcome } from "../../components/f02/Outcome";',
  },
];

describe("gate predicates are non-vacuous", () => {
  for (const gate of GATES) {
    it(`${gate.name}: catches a violating sample`, () => {
      expect(gate.pattern.test(gate.violation)).toBe(true);
    });
  }

  it("covers every Field source file (the file set is not empty or partial)", () => {
    const names = FIELD_SOURCES.map(rel).sort();
    expect(names).toEqual(
      expect.arrayContaining([
        "app/login/page.tsx",
        "app/workspaces/page.tsx",
        "app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx",
        "components/f03/BurstCapturePanel.tsx",
        "components/field/EffectSurface.tsx",
        "components/field/FieldFrame.tsx",
        "lib/field/effectLifecycle.ts",
        "lib/field/outcomeSemantics.ts",
        "lib/field/position.ts",
        "lib/field/topology.ts",
        "lib/field/useEffectField.ts",
      ]),
    );
    expect(names.length).toBeGreaterThanOrEqual(20);
  });
});

describe("MUST REMAIN IMPOSSIBLE in Field sources", () => {
  for (const gate of GATES) {
    it(gate.name, () => {
      const offenders = FIELD_SOURCES.filter((p) => !(gate.allow ?? []).includes(rel(p)) && !(gate.consumers ?? []).includes(rel(p)))
        .filter((p) => gate.pattern.test(code(readFileSync(p, "utf8"))))
        .map(rel);
      expect(offenders).toEqual([]);
    });
  }

  it("every allowlisted file is presentation-only: it never calls a command or auth function", () => {
    const allowlisted = [...new Set(GATES.flatMap((g) => g.allow ?? []))];
    expect(allowlisted.length).toBeGreaterThan(0);
    for (const name of allowlisted) {
      expect(COMMAND_FUNCTIONS.test(code(readFileSync(join(WEB, name), "utf8"))), name).toBe(false);
    }
  });

  it("green is not a Field identity (22 §18.5): the stylesheet defines no green token or color word", () => {
    const css = readFileSync(join(WEB, "app", "globals.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    expect(css).not.toMatch(/\bgreen\b|--settled|#2f5d62|#9fd0d4/i);
  });
});
