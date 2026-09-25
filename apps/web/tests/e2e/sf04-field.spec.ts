/**
 * SF-04 (L3, mocked lane): the Symbiotic Field Organism (doc 25) as component contract in a real browser — core
 * anatomy and bounded breathing, projected entities with provenance, relation currents by canonical class, the
 * encounter cascade (hover = focus, never a commit), the contextual organ (one body, chambers, reciprocity), the
 * traversal trace (route nodes, phone chip), the atmospheric medium, responsive redistribution (desktop / tablet /
 * threshold / mobile) and reduced motion — against `page.route()`-fulfilled F02/F03 envelope shapes. Not runtime
 * proof; the isolated real-stack lane and the review harness are separate.
 *
 * Falsifiers (doc 25 §21.11): 1–15; mandate §22 visual falsifiers (dashboard in space, prettier sidebar, decorative
 * motion, motion without relation meaning, invented semantics).
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SESSION = "55555550-5555-4555-8555-555555555555";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NOT = (code: string) => ({ available: false, reasonCode: code, reason: `not possible: ${code}` });
const WORKSPACE = { workspaceId: WS, name: "Activation inquiry", governedFounding: true };
const CONTROLLER = { bindingId: "b1", holderUserId: "u-fac", holderName: "Facilitator Fay", authorityClass: "SESSION_CONTROL_RIGHT", scope: `CHALLENGE:${CH}`, grantedByUserId: "u-root", grantedByName: "Root Rosa", grantedAt: "2026-09-24T11:00:00Z" };
const MEMBERS = [
  { userId: "u-root", name: "Root Rosa", email: "root@nonproof.test", role: "Owner" },
  { userId: "u-fac", name: "Facilitator Fay", email: "fay@nonproof.test", role: "Facilitator" },
  { userId: "u-c1", name: "Contributor Constantine", email: "c1@nonproof.test", role: "Contributor" },
];

function orientation() {
  return { kind: "ok", workspace: { workspaceId: WS, name: WORKSPACE.name, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" }, role: "Owner", heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"], authorized: true, governanceCapable: true };
}
function overview() {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    viewer: { userId: "u-root", role: "Owner", isGovernanceRoot: true },
    members: MEMBERS,
    challenges: [
      { challengeId: CH, title: "Why did activation stall after onboarding?", description: null, createdAt: "2026-09-24T10:01:00Z" },
      { challengeId: "33333333-3333-4333-8333-333333333333", title: "Where does support effort concentrate?", description: null, createdAt: "2026-09-24T10:02:00Z" },
    ],
    capabilities: { createChallenge: AVAILABLE, addMember: AVAILABLE },
  };
}
function detail(sessionCount = 3) {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: "Understand before changing.", createdAt: "2026-09-24T10:01:00Z" },
    sessions: Array.from({ length: sessionCount }, (_, i) => ({ sessionId: `5555555${i}-5555-4555-8555-555555555555`, state: i % 2 === 0 ? "QUESTION_GENERATION" : "QUESTION_CAPTURE", version: 3, createdAt: `2026-09-25T0${i}:25:00Z` })),
    sessionControllers: [CONTROLLER],
    members: MEMBERS,
    capabilities: { openSession: AVAILABLE, grantSessionControl: AVAILABLE },
  };
}
function position() {
  const actions = Object.fromEntries(
    ["BEGIN_SETUP", "BEGIN_CHALLENGE_CAPTURE", "PREPARE_BURST", "ADMIT_PARTICIPANT", "OPEN_QUESTION_GENERATION", "GRANT_SESSION_CONTROL", "CAPTURE_QUESTION", "COMPLETE_BURST"].map((name) => [
      name,
      name === "ADMIT_PARTICIPANT" ? { ...AVAILABLE, relevant: true } : { ...NOT("NOT_RELEVANT_IN_STATE"), relevant: false },
    ]),
  );
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: null },
    session: { sessionId: SESSION, state: "QUESTION_GENERATION", version: 4, method: "HUMAN_QUESTION_BURST", createdAt: "2026-09-25T00:25:00Z" },
    phases: [
      { state: "DRAFT", status: "done" },
      { state: "SETUP", status: "done" },
      { state: "CHALLENGE_CAPTURE", status: "done" },
      { state: "QUESTION_GENERATION", status: "current" },
      { state: "QUESTION_CAPTURE", status: "upcoming" },
      { state: "ANALYSIS", status: "upcoming" },
    ],
    serverNow: "2026-09-25T02:00:00Z",
    burst: null,
    questionSet: { visibility: "NONE", mine: [], capturedCount: null, frozen: null },
    participants: [{ userId: "u-fac", name: "Facilitator Fay", joinedAt: "2026-09-25T01:00:00Z", admittedByUserId: "u-root" }],
    sessionControllers: [{ ...CONTROLLER, scope: `SESSION:${SESSION}` }],
    establishedBy: { commandType: "OPEN_QUESTION_GENERATION", actorName: "Facilitator Fay", occurredAt: "2026-09-25T01:30:00Z", commitId: "c-1", authoritySourceType: "SESSION_CONTROL_RIGHT", authoritySourceRef: "b1", authorityScopeRef: `SESSION:${SESSION}` },
    viewer: { userId: "u-root", role: "Owner", isSessionController: false, isGovernanceRoot: true },
    actions,
    admitCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
    grantCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
  };
}

async function routes(page: Page, sessionCount = 3): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [{ workspaceId: WS, name: WORKSPACE.name }] } }));
  await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation() }));
  await page.route(`${API}/workspaces/${WS}/overview`, (route) => route.fulfill({ json: overview() }));
  await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail(sessionCount) }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: position() }));
}

const isPhone = (page: Page) => (page.viewportSize()?.width ?? 1280) < 768;
const challengeUrl = `/workspaces/${WS}/challenges/${CH}`;
const sessionUrl = `/workspaces/${WS}/sessions/${SESSION}`;

type Probe = { escaping: string[]; overlaps: string[]; hOverflow: number };
/** Containment and collision of the rendered field (same law as SF-03). */
async function probe(page: Page): Promise<Probe> {
  return page.evaluate(() => {
    const escaping: string[] = [];
    const overlaps: string[] = [];
    // a route node compressed into the phone chip (1 px, clipped, accessibility-tree only) is not a frame
    const bodies = [...document.querySelectorAll<HTMLElement>(".node-body, .core-nucleus, .plane, .trace li")].filter((b) => b.getBoundingClientRect().width > 1);
    for (const b of bodies) {
      const r = b.getBoundingClientRect();
      for (const t of b.querySelectorAll<HTMLElement>(".node-label, .node-meta, .node-marker, .core-title, .core-state, .core-meta, h2, h3, p, .trace-label, a")) {
        if (t.closest("details:not([open])") || t.classList.contains("visually-hidden")) continue;
        // SF-06: a satellite's label is an encounter pop-over beside its small sphere, not content inside it
        if (t.closest(".node[data-satellite]") && t.classList.contains("node-label")) continue;
        const tr = t.getBoundingClientRect();
        if (tr.width === 0) continue;
        if (tr.left < r.left - 1.5 || tr.right > r.right + 1.5 || tr.top < r.top - 1.5 || tr.bottom > r.bottom + 1.5) escaping.push(`${t.className}:${t.textContent?.slice(0, 24)}`);
      }
    }
    const nodes = [...document.querySelectorAll<HTMLElement>(".node-body, .core-nucleus")].map((e) => ({ e, r: e.getBoundingClientRect() }));
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i].r;
        const b = nodes[j].r;
        if (a.left < b.right - 2 && b.left < a.right - 2 && a.top < b.bottom - 2 && b.top < a.bottom - 2) overlaps.push(`${nodes[i].e.textContent?.slice(0, 20)} × ${nodes[j].e.textContent?.slice(0, 20)}`);
      }
    }
    return { escaping, overlaps, hOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
  });
}

test.describe("Semantic Core Organism (doc 25 §6; falsifiers 9, 4)", () => {
  test("the core breathes through its aura, rings and membrane only — bounded (≤ 2.4 %), slow, never the text, never a spinner", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    const core = page.getByTestId("field-core");
    await core.waitFor();
    const info = await core.evaluate((el) => {
      const cs = (sel: string) => getComputedStyle(el.querySelector(sel)!);
      const ring = cs('.core-ring[data-ring="1"]');
      return {
        aura: cs(".core-aura").animationName,
        auraDuration: parseFloat(cs(".core-aura").animationDuration),
        ring: ring.animationName,
        ringDuration: parseFloat(ring.animationDuration),
        membrane: cs(".core-membrane").animationName,
        orbit: cs(".core-orbit-dot").animationName,
        orbitDuration: parseFloat(cs(".core-orbit-dot").animationDuration),
        nucleus: cs(".core-nucleus").animationName,
        title: cs(".core-title").animationName,
        titleTransform: cs(".core-title").transform,
        layers: ["core-aura", "core-rings", "core-membrane", "core-orbit-trace", "core-nucleus"].map((c) => getComputedStyle(el.querySelector(`.${c}`)!).display !== "none"),
      };
    });
    expect(info.aura).toBe("aura-breathe");
    expect(info.auraDuration).toBeGreaterThanOrEqual(8);
    expect(info.auraDuration).toBeLessThanOrEqual(14);
    expect(info.ring).toBe("ring-breathe");
    expect(info.ringDuration).toBeGreaterThanOrEqual(8);
    expect(info.membrane).toBe("membrane-breathe");
    expect(info.orbit).toBe("micro-orbit");
    expect(info.orbitDuration).toBeGreaterThanOrEqual(40);
    expect(info.nucleus).toBe("none");
    expect(info.title).toBe("none");
    expect(info.titleTransform).toBe("none");
    expect(info.layers).toEqual([true, true, true, true, true]);
    // the breathing scale is bounded: sample the membrane's live transform several times
    const scales: number[] = [];
    for (let i = 0; i < 6; i += 1) {
      scales.push(await core.locator(".core-membrane").evaluate((el) => new DOMMatrix(getComputedStyle(el).transform).a));
      await page.waitForTimeout(150);
    }
    for (const s of scales) expect(s).toBeLessThanOrEqual(1.0241);
    for (const s of scales) expect(s).toBeGreaterThanOrEqual(0.999);
  });
  test("reduced motion keeps every core layer and removes every animation; the state stays in text", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await routes(page);
    await page.goto(challengeUrl);
    const core = page.getByTestId("field-core");
    const names = await core.evaluate((el) => [...el.querySelectorAll(".core-aura, .core-ring, .core-membrane, .core-orbit-dot")].map((n) => getComputedStyle(n).animationName));
    expect(names).toHaveLength(6);
    for (const n of names) expect(n).toBe("none");
    await expect(core.locator(".core-state")).toHaveText(/3 Sessions/);
    await expect(core).toHaveAttribute("data-core-state", "current");
  });
});

test.describe("Living Field Entities + Relational Currents (doc 25 §7, §8; falsifiers 1–3, 11–13)", () => {
  test("every entity carries band, tone, role and the rule chain; every current carries its canonical class — never tension", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const nodes = await page.locator("li.node").evaluateAll((els) => els.map((e) => ({ band: e.getAttribute("data-band"), tone: e.getAttribute("data-tone"), role: e.getAttribute("data-role"), prov: e.getAttribute("data-provenance"), mass: (e as HTMLElement).style.getPropertyValue("--mass") })));
    expect(nodes.length).toBeGreaterThanOrEqual(5);
    for (const n of nodes) {
      expect(["inner", "middle", "outer"]).toContain(n.band);
      expect(["living", "stable", "boundary", "neutral"]).toContain(n.tone);
      expect(n.prov).toBe("RULE-W;RULE-B;RULE-T");
      expect(parseFloat(n.mass)).toBeGreaterThan(0.8);
      expect(parseFloat(n.mass)).toBeLessThan(1.25);
    }
    // SF-06: every entry keeps its own relation; a family sphere adds its own relation to the core on top
    const rels = await page.locator("g.relation:not(.family-relation)").evaluateAll((els) => els.map((e) => ({ key: e.getAttribute("data-key"), type: e.getAttribute("data-relation-type"), dir: e.getAttribute("data-direction"), prov: e.getAttribute("data-provenance") })));
    expect(rels.length).toBe(nodes.length);
    for (const r of rels) {
      expect(["directional", "reciprocal", "latent", "context"]).toContain(r.type);
      expect(r.prov).toMatch(/^RULE-R:canonical-relation:\w+,canonical-state:\w+$/);
    }
    expect(rels.find((r) => r.key === "new-session")).toMatchObject({ type: "directional", dir: "source-to-target" });
    expect(rels.find((r) => r.key === "b1")).toMatchObject({ type: "directional", dir: "target-to-source" });
  });
  test("motion follows the relation class: directional currents drift (reverse for node→core), latent traces never move, curves never straight lines", async ({ page }) => {
    test.skip(isPhone(page), "currents are drawn on the orbit representation");
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const motion = await page.locator("g.relation:not(.family-relation)").evaluateAll((els) =>
      els.map((e) => {
        const key = e.getAttribute("data-key")!;
        const pulse = document.querySelector(`.current-pulse[data-key="${CSS.escape(key)}"]`);
        const cs = pulse ? getComputedStyle(pulse) : null;
        return { key, type: e.getAttribute("data-relation-type"), anim: cs?.animationName ?? "none", direction: cs?.animationDirection ?? null, duration: parseFloat(cs?.animationDuration ?? "0"), pulse: !!pulse, d: e.querySelector(".path-base")!.getAttribute("d") };
      }),
    );
    const possible = motion.find((m) => m.key === "new-session")!;
    expect(possible.anim).toBe("current-travel");
    expect(possible.direction).toBe("normal");
    expect(possible.duration).toBeGreaterThanOrEqual(5);
    expect(possible.duration).toBeLessThanOrEqual(12);
    const gov = motion.find((m) => m.key === "b1")!;
    expect(gov.anim).toBe("current-travel");
    expect(gov.direction).toBe("reverse");
    for (const m of motion.filter((x) => x.type === "latent")) expect(m.pulse).toBe(false);
    for (const m of motion) expect(m.d).toMatch(/^M [\d.]+ [\d.]+ Q /);
    expect(await page.locator(".orbit-paths line").count()).toBe(0);
  });
  test("on the Session field the active phase is a breathing context current and participation is a reciprocal (alternating) current", async ({ page }) => {
    test.skip(isPhone(page), "currents are drawn on the orbit representation");
    await routes(page);
    await page.goto(sessionUrl);
    await page.getByTestId("field-core").waitFor();
    const rel = async (key: string) =>
      page.locator(`g.relation[data-key="${key}"]`).evaluate((e) => {
        const pulse = document.querySelector(`.current-pulse[data-key="${CSS.escape(e.getAttribute("data-key")!)}"]`);
        const cs = pulse ? getComputedStyle(pulse) : null;
        return { type: e.getAttribute("data-relation-type"), dir: e.getAttribute("data-direction"), anim: cs?.animationName ?? "none", direction: cs?.animationDirection ?? null, pulse: !!pulse };
      });
    expect(await rel("QUESTION_GENERATION")).toMatchObject({ type: "context", anim: "current-breathe" });
    expect(await rel("DRAFT")).toMatchObject({ type: "latent", pulse: false });
    expect(await rel("ANALYSIS")).toMatchObject({ type: "latent", pulse: false });
    expect(await rel("p-u-fac")).toMatchObject({ type: "reciprocal", dir: "bidirectional", anim: "current-travel", direction: "alternate" });
    expect(await page.locator('g.relation[data-relation-type="tension"]').count()).toBe(0);
  });
});

test.describe("Encounter cascade (doc 25 §13; falsifiers 6, 7, 14)", () => {
  test("hovering an entity resonates its aura, its current, the core's lean, the organ's mirrored token and the atmosphere — and sends nothing", async ({ page }) => {
    test.skip(isPhone(page), "hover is a pointer interaction");
    let posts = 0;
    await routes(page);
    await page.route(`${API}/workspaces/**`, (route) => {
      if (route.request().method() !== "GET") {
        posts += 1;
        return route.fulfill({ status: 500, json: {} });
      }
      return route.fallback();
    });
    await page.goto(challengeUrl);
    const stage = page.getByTestId("field-stage");
    const gov = page.locator('li.node[data-key="b1"]');
    await gov.waitFor();
    const restWash = await page.locator(".resonance-wash").evaluate((el) => parseFloat(getComputedStyle(el).opacity));
    await gov.hover();
    await expect(stage).toHaveAttribute("data-encounter", "hover");
    await expect(stage).toHaveAttribute("data-hover-key", "b1");
    await expect(stage).toHaveAttribute("data-active-relation", "governance");
    expect(await stage.evaluate((el) => (el as HTMLElement).style.getPropertyValue("--vec-on"))).toBe("1");
    const vec = await stage.evaluate((el) => [parseFloat((el as HTMLElement).style.getPropertyValue("--vec-x")), parseFloat((el as HTMLElement).style.getPropertyValue("--vec-y"))]);
    expect(Math.hypot(vec[0], vec[1])).toBeCloseTo(1, 2);
    await expect(gov).toHaveAttribute("data-resonating", "true");
    await expect(page.locator('g.relation[data-key="b1"]')).toHaveAttribute("data-resonating", "true");
    await expect(page.locator('.current-pulse[data-key="b1"]')).toHaveAttribute("data-resonating", "true");
    await expect(page.locator('[data-relation-key="b1"]')).toHaveAttribute("data-resonating", "true");
    await expect(page.locator('.chamber[data-plane="governance"]')).toHaveAttribute("data-chamber-resonating", "true");
    await expect.poll(() => page.locator(".resonance-wash").evaluate((el) => parseFloat(getComputedStyle(el).opacity))).toBeGreaterThan(restWash + 0.2);
    const lean = await page.locator(".core-aura").evaluate((el) => getComputedStyle(el).transform);
    expect(lean).not.toBe("none");
    expect(lean).not.toBe("matrix(1, 0, 0, 1, 0, 0)");
    expect(posts).toBe(0);
    await expect(page.getByTestId("command-outcome")).toHaveCount(0);
    // leaving the entity releases the cascade
    await page.mouse.move(2, 2);
    await expect(stage).not.toHaveAttribute("data-encounter", /.+/);
    await expect(gov).not.toHaveAttribute("data-resonating", /.+/);
    expect(await page.locator("[data-resonating]").count()).toBe(0);
  });
  test("keyboard focus produces the identical cascade (focus parity) and the focus ring is visible", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    const stage = page.getByTestId("field-stage");
    const link = page.locator('li.node[data-key="55555550-5555-4555-8555-555555555555"] a.node-main');
    await link.focus();
    await expect(stage).toHaveAttribute("data-encounter", "focus");
    await expect(stage).toHaveAttribute("data-hover-key", "55555550-5555-4555-8555-555555555555");
    await expect(page.locator('li.node[data-key="55555550-5555-4555-8555-555555555555"]')).toHaveAttribute("data-resonating", "true");
    if (!isPhone(page)) {
      expect(await stage.evaluate((el) => (el as HTMLElement).style.getPropertyValue("--vec-on"))).toBe("1");
      await expect(page.locator('g.relation[data-key="55555550-5555-4555-8555-555555555555"]')).toHaveAttribute("data-resonating", "true");
    }
    const ring = await link.evaluate((el) => getComputedStyle(el).outlineStyle);
    expect(ring).not.toBe("none");
    await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
    await expect(stage).not.toHaveAttribute("data-encounter", /.+/);
  });
  test("hovering an organ token resonates its field entity (context ↔ field reciprocity)", async ({ page }) => {
    test.skip(isPhone(page), "hover is a pointer interaction");
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("challenge-authority-proof").locator("summary").click();
    await page.locator('[data-relation-key="b1"]').hover();
    await expect(page.getByTestId("field-stage")).toHaveAttribute("data-encounter", "context");
    await expect(page.locator('li.node[data-key="b1"]')).toHaveAttribute("data-resonating", "true");
    await expect(page.locator('g.relation[data-key="b1"]')).toHaveAttribute("data-resonating", "true");
  });
});

test.describe("Contextual Semantic Organ (doc 25 §10; falsifiers 5, 6)", () => {
  test("one organ grown from the active state: live region, membrane header naming the core, chambers sharing the surface — not cards", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    const organ = page.getByTestId("context-organ");
    await expect(organ).toHaveAttribute("aria-live", "polite");
    await expect(organ).toHaveAttribute("aria-label", "Active semantic context");
    expect(await page.locator("aside").count()).toBe(1);
    await expect(organ.locator(".organ-title")).toHaveText("Why did activation stall after onboarding?");
    await expect(organ.locator(".organ-state")).toHaveText("3 Sessions");
    const shell = await organ.evaluate((el) => ({ radius: getComputedStyle(el).borderTopLeftRadius, border: getComputedStyle(el).borderTopWidth }));
    // SF-06 (human direction): the organ is a translucent HUD lens with an 8 px radius, not a rounded card
    expect(shell.radius).toBe("8px");
    expect(shell.border).toBe("1px");
    const chambers = await organ.locator(".plane").evaluateAll((els) =>
      els.map((e) => ({ chamber: e.getAttribute("data-chamber"), shadow: getComputedStyle(e).boxShadow, borderTop: parseFloat(getComputedStyle(e).borderTopWidth), borderColor: getComputedStyle(e).borderTopColor, bg: getComputedStyle(e).backgroundColor })),
    );
    expect(chambers.map((c) => c.chamber)).toEqual(["primary", "relational", "logic"]);
    // SF-05 (doc 26 §17): a chamber is a faint translucent membrane inside the organ — never a card: at most a
    // 1 px low-alpha membrane, no outer shadow, a translucent (never opaque) fill
    for (const c of chambers) {
      expect(c.borderTop).toBeLessThanOrEqual(1);
      expect(parseFloat(c.borderColor.match(/[\d.]+\)$/)?.[0] ?? "1")).toBeLessThan(0.2);
      expect(c.shadow === "none" || c.shadow.startsWith("rgba") && c.shadow.includes("inset")).toBe(true);
      expect(parseFloat(c.bg.match(/[\d.]+\)$/)?.[0] ?? "1")).toBeLessThan(0.7);
    }
    // the organ carries no state of its own
    expect(await organ.evaluate((el) => [...el.attributes].map((a) => a.name).filter((n) => /state|selected|active/.test(n)))).toEqual([]);
  });
  test("the organ hosts the request surfaces unchanged: the possible effect is still requestable and the unavailable one still names its reason", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    await expect(page.getByTestId("context-organ").getByRole("button", { name: "Grant session control for this Challenge" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Open Session" })).toBeVisible();
  });
});

test.describe("Traversal Trace (doc 25 §11; falsifier 8)", () => {
  test("desktop: every coordinate is a route node with a membrane; the current one breathes; no chip", async ({ page }) => {
    test.skip(isPhone(page), "desktop trace");
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const nav = page.getByRole("navigation", { name: "Inquiry position" });
    expect(await nav.locator("li.route-node").count()).toBeGreaterThanOrEqual(3);
    await expect(nav.locator(".trace-chip-toggle")).toBeHidden();
    const current = nav.locator('li[data-status="current"] .route-membrane');
    expect(await current.evaluate((el) => getComputedStyle(el).animationName)).toBe("aura-breathe");
    expect(await nav.locator('li[data-status="established"] .route-membrane').first().evaluate((el) => parseFloat(getComputedStyle(el).opacity))).toBeLessThan(1);
    const hidden = await nav.locator("li").evaluateAll((els) => els.filter((e) => getComputedStyle(e).display === "none").length);
    expect(hidden).toBe(0);
  });
  test("phone: the trace compresses to the current route node as a chip; the toggle expands the whole route", async ({ page }) => {
    test.skip(!isPhone(page), "phone trace");
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const nav = page.getByRole("navigation", { name: "Inquiry position" });
    const toggle = page.getByTestId("trace-toggle");
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(nav.locator('li[data-status="current"]')).toBeVisible();
    // collapsed parents are compressed (1 px, clipped) but stay in the accessibility tree and keep their links
    const collapsed = await nav.locator('li[data-status="established"]').first().boundingBox();
    expect(collapsed!.width).toBeLessThanOrEqual(1);
    expect(await nav.getByRole("link").count()).toBeGreaterThanOrEqual(2);
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect((await nav.locator('li[data-status="established"]').first().boundingBox())!.width).toBeGreaterThan(20);
    await expect(nav.locator('li[data-status="established"] a').first()).toBeVisible();
    expect((await probe(page)).hOverflow).toBeLessThanOrEqual(1);
  });
});

test.describe("Responsive redistribution (doc 25 §15; falsifier 10)", () => {
  const widths = [
    { name: "wide desktop", w: 1600, h: 900, columns: 2 },
    { name: "normal desktop", w: 1280, h: 860, columns: 2 },
    { name: "desktop threshold", w: 1200, h: 800, columns: 2 },
    { name: "SF-03 threshold weakness", w: 1150, h: 800, columns: 1 },
    { name: "tablet", w: 1024, h: 800, columns: 1 },
    { name: "small tablet", w: 800, h: 1000, columns: 1 },
  ];
  for (const v of widths) {
    test(`${v.name} (${v.w}×${v.h}): the field and the organ compose without overflow, escape or overlap`, async ({ page }) => {
      test.skip(isPhone(page), "desktop/tablet widths");
      await page.setViewportSize({ width: v.w, height: v.h });
      await routes(page, 5);
      await page.goto(challengeUrl);
      await page.getByTestId("field-core").waitFor();
      await page.waitForTimeout(400);
      const topology = (await page.locator(".topology").boundingBox())!;
      const organ = (await page.getByTestId("context-organ").boundingBox())!;
      if (v.columns === 2) expect(organ.x).toBeGreaterThanOrEqual(topology.x + topology.width - 1);
      else expect(organ.y).toBeGreaterThanOrEqual(topology.y + topology.height - 1);
      const p = await probe(page);
      expect(p.hOverflow, "horizontal overflow").toBeLessThanOrEqual(1);
      expect(p.escaping).toEqual([]);
      expect(p.overlaps).toEqual([]);
      await expect(page.locator(".core-aura")).toBeVisible();
    });
  }
  test("phone: the field is a breathing constellation of capsules around the core and the organ is a membrane sheet", async ({ page }) => {
    test.skip(!isPhone(page), "phone representation");
    await routes(page, 5);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const orbit = await page.locator('[data-testid="sessions-list"]').evaluate((el) => ({ display: getComputedStyle(el).display, wrap: getComputedStyle(el).flexWrap, direction: getComputedStyle(el).flexDirection, borderLeft: getComputedStyle(el).borderLeftWidth }));
    expect(orbit).toMatchObject({ display: "flex", wrap: "wrap", direction: "row", borderLeft: "0px" });
    const rows = await page.locator('[data-testid="sessions-list"] .node').evaluateAll((els) => new Set(els.map((e) => Math.round(e.getBoundingClientRect().top))).size);
    expect(rows).toBeGreaterThan(1);
    expect(await page.locator('[data-testid="sessions-list"] .node').first().evaluate((el) => getComputedStyle(el, "::before").content)).toBe("none");
    const core = (await page.getByTestId("field-core").boundingBox())!;
    const first = (await page.locator('[data-testid="sessions-list"] .node').first().boundingBox())!;
    expect(first.y).toBeGreaterThan(core.y + core.height - 1);
    const sheet = await page.getByTestId("context-organ").evaluate((el) => ({ tl: getComputedStyle(el).borderTopLeftRadius, bl: getComputedStyle(el).borderBottomLeftRadius, live: el.getAttribute("aria-live") }));
    expect(sheet).toMatchObject({ tl: "8px", bl: "0px", live: "polite" });
    const p = await probe(page);
    expect(p.hOverflow).toBeLessThanOrEqual(1);
    expect(p.escaping).toEqual([]);
    expect(p.overlaps).toEqual([]);
    const targets = await page.locator("li.node .node-body").evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().height)));
    for (const h of targets) expect(h).toBeGreaterThanOrEqual(40);
  });
  test("compact phone (360 px): nothing overflows, type floors hold", async ({ page }) => {
    test.skip(!isPhone(page), "phone representation");
    await page.setViewportSize({ width: 360, height: 780 });
    await routes(page, 5);
    await page.goto(sessionUrl);
    await page.getByTestId("field-core").waitFor();
    const p = await probe(page);
    expect(p.hOverflow).toBeLessThanOrEqual(1);
    expect(p.escaping).toEqual([]);
    const smallest = await page.locator(".node-label, .node-meta, .node-marker, .core-title").evaluateAll((els) => Math.min(...els.map((e) => parseFloat(getComputedStyle(e).fontSize))));
    expect(smallest).toBeGreaterThanOrEqual(11);
  });
});

test.describe("Atmospheric medium (doc 25 §12) and reduced motion (doc 25 §18.5)", () => {
  test("the field box has a decorative pressure zone that breathes and a wash that is inert at rest", async ({ page }) => {
    await routes(page);
    await page.goto(challengeUrl);
    const atmo = page.getByTestId("stage-atmosphere");
    await expect(atmo).toHaveAttribute("aria-hidden", "true");
    const info = await atmo.evaluate((el) => ({ pointer: getComputedStyle(el).pointerEvents, pressure: getComputedStyle(el.querySelector(".pressure-zone")!).animationName, wash: parseFloat(getComputedStyle(el.querySelector(".resonance-wash")!).opacity) }));
    expect(info.pointer).toBe("none");
    expect(info.pressure).toBe("none"); // static presence: the breathing lives on the core's aura (measured cost)
    expect(info.wash).toBe(0);
  });
  test("reduced motion: no current drifts, no aura breathes, no organ emerges — every layer and every meaning stays", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const names = await page.evaluate(() => [...document.querySelectorAll(".current-pulse, .core-aura, .pressure-zone, .organ, .route-membrane, .node-aura")].map((n) => getComputedStyle(n).animationName));
    expect(names.length).toBeGreaterThanOrEqual(6);
    for (const n of names) expect(n).toBe("none");
    expect(await page.locator("g.relation[data-relation-type]").count()).toBeGreaterThan(0);
    await expect(page.getByTestId("context-organ")).toBeVisible();
    await expect(page.locator('li.node[data-key="b1"] .node-marker')).toContainText("authority");
  });
});
