/**
 * SF-03 (L3, mocked lane): the doc 23 delta as component contract in a real browser — containment, content-aware
 * geometry, centred identity, symbiotic breadcrumb, instrument constellation, reciprocity, ambient field, reduced
 * motion and phone capability — against `page.route()`-fulfilled F02 envelope shapes with STRESS content (labels
 * longer than any review fixture). It is not runtime proof; the isolated real-stack lane is separate.
 *
 * Falsifiers (doc 23 §20): 4, 6–14, 16, 19–26, 28–30, 37–41, 51–55.
 */
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";

const LONG_WS = "Cross-Functional Customer Activation and Retention Inquiry Workspace for the European Enterprise Segment";
const LONG_CH = "Why did activation stall after onboarding for enterprise customers who purchased through partners in the last two quarters, and what did we assume?";
const LONG_NAME = "Dr. Maria-Theresia von Hohenstein-Auerbach-Bergmann";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const LONG_REASON = {
  available: false,
  reasonCode: `NO_CHALLENGE_SESSION_CONTROL:${CH}`,
  reason: `Opening a Session requires SESSION_CONTROL_RIGHT for this Challenge (scope CHALLENGE:${CH}). Only the Workspace governance root can grant it, and it grants it per Challenge, never inherited from the Workspace role.`,
};
const WORKSPACE = { workspaceId: WS, name: LONG_WS, governedFounding: true };

function orientation() {
  return { kind: "ok", workspace: { workspaceId: WS, name: LONG_WS, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" }, role: "Owner", heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"], authorized: true, governanceCapable: true };
}
function overview() {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    viewer: { userId: "u-root", role: "Owner", isGovernanceRoot: true },
    members: [
      { userId: "u-root", name: LONG_NAME, email: "root@nonproof.test", role: "Owner" },
      { userId: "u-fac", name: "Facilitator Fay", email: "fay@nonproof.test", role: "Facilitator" },
      { userId: "u-c1", name: "Contributor Constantine Wolfgang", email: "c1@nonproof.test", role: "Contributor" },
      { userId: "u-c2", name: "Kim", email: "c2@nonproof.test", role: "Contributor" },
    ],
    challenges: [
      { challengeId: CH, title: LONG_CH, description: null, createdAt: "2026-09-24T10:01:00Z" },
      { challengeId: "33333333-3333-4333-8333-333333333333", title: "Short one", description: null, createdAt: "2026-09-24T10:02:00Z" },
      { challengeId: "44444444-4444-4444-8444-444444444444", title: "Where does support effort concentrate and why does it not move?", description: null, createdAt: "2026-09-24T10:03:00Z" },
    ],
    capabilities: { createChallenge: AVAILABLE, addMember: AVAILABLE },
  };
}
function detail(sessionCount: number) {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: LONG_CH, description: "Understand before changing.", createdAt: "2026-09-24T10:01:00Z" },
    sessions: Array.from({ length: sessionCount }, (_, i) => ({ sessionId: `5555555${i}-5555-4555-8555-555555555555`, state: i % 3 === 0 ? "QUESTION_GENERATION" : "QUESTION_CAPTURE", version: 3, createdAt: `2026-09-2${(i % 8) + 1}T1${i % 9}:02:03Z` })),
    sessionControllers: [
      { bindingId: "b1", holderUserId: "u-fac", holderName: LONG_NAME, authorityClass: "SESSION_CONTROL_RIGHT", scope: `CHALLENGE:${CH}`, grantedByUserId: "u-root", grantedByName: LONG_NAME, grantedAt: "2026-09-24T10:01:30Z" },
      { bindingId: "b2", holderUserId: "u-c1", holderName: "Contributor Constantine Wolfgang", authorityClass: "SESSION_CONTROL_RIGHT", scope: `CHALLENGE:${CH}`, grantedByUserId: "u-root", grantedByName: "Root", grantedAt: "2026-09-24T10:01:40Z" },
    ],
    members: overview().members,
    capabilities: { openSession: LONG_REASON, grantSessionControl: AVAILABLE },
  };
}

async function stressRoutes(page: Page, sessionCount = 6): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [{ workspaceId: WS, name: LONG_WS }, { workspaceId: "66666666-6666-4666-8666-666666666666", name: "Ops" }] } }));
  await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation() }));
  await page.route(`${API}/workspaces/${WS}/overview`, (route) => route.fulfill({ json: overview() }));
  await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail(sessionCount) }));
}

type Probe = { escaping: string[]; overlaps: string[]; hOverflow: number; smallest: number; fit: string | null };

/** Containment, collision and legibility, measured on the rendered page. */
async function probe(page: Page): Promise<Probe> {
  return page.evaluate(() => {
    // SF-04: a route node compressed into the phone chip (1 px, clipped, accessibility-tree only) is not a frame
    const bodies = [...document.querySelectorAll<HTMLElement>(".node-body, .core, .plane, .trace li")].filter((b) => b.getBoundingClientRect().width > 1);
    const escaping: string[] = [];
    const overlaps: string[] = [];
    let smallest = 99;
    const inside = (inner: DOMRect, outer: DOMRect) => inner.left >= outer.left - 1 && inner.right <= outer.right + 1 && inner.top >= outer.top - 1 && inner.bottom <= outer.bottom + 1;
    // SF-04: the organism's decorative layers (auras, rings, membranes; aria-hidden, absolutely positioned) extend
    // beyond their frame by design and would inflate scrollWidth/Height; the scroll metric measures material content
    const decorative = [...document.querySelectorAll<HTMLElement>(".node-aura, .core-aura, .core-rings, .core-membrane, .core-orbit-trace, .route-membrane, .organ-bridge")];
    const hidden = decorative.map((d) => d.style.display);
    for (const d of decorative) d.style.display = "none";
    const scrolls = bodies.map((b) => b.scrollWidth > b.clientWidth + 2 || b.scrollHeight > b.clientHeight + 2);
    decorative.forEach((d, i) => (d.style.display = hidden[i]));
    for (const [i, b] of bodies.entries()) {
      if (scrolls[i]) escaping.push(`scroll:${b.className}:${b.textContent?.slice(0, 30)}`);
      const frame = b.getBoundingClientRect();
      for (const t of b.querySelectorAll<HTMLElement>(".node-label, .node-meta, .node-marker, .core-title, .core-state, .core-meta, h2, h3, .mono, .tag")) {
        if (getComputedStyle(t).position === "absolute") continue;
        if (t.closest("details:not([open])")) continue; // closed proof depth: not rendered content
        const r = t.getBoundingClientRect();
        if (r.width > 0 && !inside(r, frame)) escaping.push(`text:${t.className}:${t.textContent?.slice(0, 30)}`);
        const fs = parseFloat(getComputedStyle(t).fontSize);
        if (t.textContent?.trim() && !t.classList.contains("visually-hidden")) smallest = Math.min(smallest, fs);
      }
    }
    const nodes = [...document.querySelectorAll<HTMLElement>(".node-body, .core")].map((e) => ({ e, r: e.getBoundingClientRect() }));
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i].r;
        const b = nodes[j].r;
        if (a.width && b.width && a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) {
          overlaps.push(`${nodes[i].e.textContent?.slice(0, 20)} x ${nodes[j].e.textContent?.slice(0, 20)}`);
        }
      }
    }
    return { escaping, overlaps, hOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth, smallest, fit: document.querySelector(".topology")?.getAttribute("data-fit") ?? null };
  });
}

const isPhone = (page: Page) => (page.viewportSize()?.width ?? 1280) < 861;

test.describe("typography and containment (doc 23 §6; falsifiers 6–11)", () => {
  for (const [name, path, sessions] of [
    ["Workspace Field", `/workspaces/${WS}`, 6],
    ["Challenge Field with nine Sessions and two long authority holders", `/workspaces/${WS}/challenges/${CH}`, 9],
    ["Workspace Overview", `/workspaces`, 6],
  ] as const) {
    test(`${name}: long content never escapes its frame, never overlaps, never shrinks below legible size`, async ({ page }) => {
      await stressRoutes(page, sessions);
      await page.goto(path);
      await page.getByTestId("field-core").waitFor();
      await page.waitForTimeout(400); // measured layout settle
      const p = await probe(page);
      expect(p.escaping, "material text inside its frame").toEqual([]);
      expect(p.overlaps, "no frame overlaps another frame or the core").toEqual([]);
      expect(p.hOverflow).toBeLessThanOrEqual(1);
      expect(p.smallest, "no material text below 11.5px").toBeGreaterThanOrEqual(11.5);
      // on desktop the content either fits the orbit or is compacted into the stack; it never overflows
      if (!isPhone(page)) expect(["fits", "stack"]).toContain(p.fit);
    });
  }
  test("a long core title is fully rendered (never clamped or clipped)", async ({ page }) => {
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const title = page.getByTestId("field-core").getByRole("heading", { level: 1 });
    await expect(title).toHaveText(LONG_CH);
    const clipped = await title.evaluate((el) => el.scrollHeight > el.clientHeight + 1 || getComputedStyle(el).webkitLineClamp !== "none");
    expect(clipped).toBe(false);
  });
});

test.describe("content-aware geometry (doc 23 §7; falsifiers 12–18)", () => {
  test("geometry is deterministic: the same content yields identical node positions on reload", async ({ page }) => {
    test.skip(isPhone(page), "orbit geometry is a desktop representation");
    await stressRoutes(page, 7);
    const read = async () => {
      await page.goto(`/workspaces/${WS}/challenges/${CH}`);
      await page.getByTestId("field-core").waitFor();
      await page.waitForTimeout(400);
      return page.locator(".node").evaluateAll((els) => els.map((e) => (e as HTMLElement).style.cssText));
    };
    const a = await read();
    const b = await read();
    expect(a).toEqual(b);
    expect(a.length).toBe(10);
  });
  test("wide nodes get more arc and the ring radius follows the content; no node touches the core", async ({ page }) => {
    test.skip(isPhone(page), "orbit geometry is a desktop representation");
    await stressRoutes(page, 3);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.getByTestId("field-core").waitFor();
    await page.waitForTimeout(400);
    const few = await page.locator(".orbit-paths[data-orbit='containment'] ellipse").getAttribute("rx");
    await stressRoutes(page, 9);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.getByTestId("field-core").waitFor();
    await page.waitForTimeout(400);
    const many = await page.locator(".orbit-paths[data-orbit='containment'] ellipse").getAttribute("rx");
    expect(Number(many)).toBeGreaterThanOrEqual(Number(few));
    expect((await probe(page)).overlaps).toEqual([]);
  });
});

test.describe("orientation rail: centred identity and symbiotic breadcrumb (doc 23 §9–§10; falsifiers 19–24)", () => {
  test("the NQIRY identity is centred in the rail on desktop and does not displace the trace or the exit", async ({ page }) => {
    test.skip(isPhone(page), "phone uses the identity row");
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const box = await page.getByTestId("identity").boundingBox();
    const vw = page.viewportSize()!.width;
    expect(Math.abs(box!.x + box!.width / 2 - vw / 2)).toBeLessThanOrEqual(12);
    await expect(page.getByRole("link", { name: "nquiry" })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Inquiry position" })).toBeVisible();
    await expect(page.getByTestId("logout-button")).toBeVisible();
  });
  test("the trace stays readable and its text never moves while its separators breathe", async ({ page }) => {
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const trace = page.getByRole("navigation", { name: "Inquiry position" });
    const sizes = await trace.locator("a, .trace-label").evaluateAll((els) => els.map((e) => parseFloat(getComputedStyle(e).fontSize)));
    for (const s of sizes) expect(s).toBeGreaterThanOrEqual(13.5);
    const current = trace.locator('li[data-status="current"] .trace-label');
    await expect(current).toHaveText(LONG_CH);
    const before = await current.boundingBox();
    await page.waitForTimeout(700);
    const after = await current.boundingBox();
    expect(after).toEqual(before);
    const sep = await trace.locator("li").nth(1).evaluate((el) => ({ anim: getComputedStyle(el, "::before").animationName, textAnim: getComputedStyle(el).animationName, transform: getComputedStyle(el).transform }));
    expect(sep.textAnim).toBe("none");
    expect(sep.transform).toBe("none");
    expect(sep.anim).not.toBe("none");
  });
});

test.describe("instrument constellation and reciprocity (doc 23 §8, §11; falsifiers 25–39)", () => {
  test("on a wide desktop the instruments compose in two columns: the active relation first, governance and proof beside it", async ({ page }) => {
    test.skip(isPhone(page), "phone stacks");
    await page.setViewportSize({ width: 1600, height: 900 });
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.getByTestId("field-core").waitFor();
    const cols = await page.locator(".instruments").evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(" ").length);
    expect(cols).toBe(2);
    const action = await page.locator('.plane[data-plane="action"]').boundingBox();
    const gov = await page.locator('.plane[data-plane="governance"]').boundingBox();
    const proof = await page.locator('.plane[data-plane="proof"]').boundingBox();
    expect(gov!.x).toBeGreaterThan(action!.x + action!.width - 1);
    expect(proof!.x).toBeGreaterThan(action!.x + action!.width - 1);
    expect(gov!.y).toBeLessThan(proof!.y);
    await expect(page.getByRole("button", { name: "Grant session control for this Challenge" })).toBeVisible();
    await expect(page.getByTestId("challenge-authority-proof")).toBeVisible();
  });
  test("focusing a governance node by keyboard makes the governance instrument respond; nothing else changes", async ({ page }) => {
    test.skip(isPhone(page), "reciprocity is measured on the orbit representation");
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const stage = page.getByTestId("field-stage");
    await expect(stage).not.toHaveAttribute("data-active-relation", /.+/);
    const grant = page.getByRole("button", { name: "Grant session control for this Challenge" });
    await grant.focus();
    await expect(stage).toHaveAttribute("data-active-relation", "governance");
    const plane = page.locator('.plane[data-plane="governance"]');
    const responding = await plane.evaluate((el) => getComputedStyle(el).borderTopColor);
    await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
    await expect(stage).not.toHaveAttribute("data-active-relation", /.+/);
    const resting = await plane.evaluate((el) => getComputedStyle(el).borderTopColor);
    expect(responding).not.toBe(resting);
    // the unavailable relation stays unavailable and its reason stays (no state from reciprocity)
    await expect(page.getByTestId("session-create-unavailable")).toContainText("SESSION_CONTROL_RIGHT");
  });
  test("hovering the Open-Session relation makes the action instrument respond, and hover never becomes a commit", async ({ page }) => {
    test.skip(isPhone(page), "hover is a pointer interaction");
    let posts = 0;
    await stressRoutes(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}/sessions`, (route) => {
      posts += 1;
      return route.fulfill({ status: 500, json: {} });
    });
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.locator('[data-testid="sessions-list"] .node').first().hover();
    await expect(page.getByTestId("field-stage")).toHaveAttribute("data-active-relation", "action");
    expect(posts).toBe(0);
    await expect(page.getByTestId("command-outcome")).toHaveCount(0);
  });
});

test.describe("ambient field and reduced motion (doc 23 §5; falsifiers 1–5, 41)", () => {
  test("the living background spans the viewport behind rail and instruments, moves only ambiently, and is never content", async ({ page }) => {
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const bg = page.getByTestId("field-background");
    await expect(bg).toHaveAttribute("aria-hidden", "true");
    const info = await bg.evaluate((el) => {
      const r = el.getBoundingClientRect();
      const nebula = el.querySelector(".nebula-a") as HTMLElement;
      const cs = getComputedStyle(nebula);
      return { w: r.width, h: r.height, pos: getComputedStyle(el).position, anim: cs.animationName, duration: parseFloat(cs.animationDuration), pointer: getComputedStyle(el).pointerEvents, z: getComputedStyle(el).zIndex };
    });
    expect(info.w).toBeGreaterThanOrEqual(page.viewportSize()!.width - 1);
    expect(info.h).toBeGreaterThanOrEqual(page.viewportSize()!.height - 1);
    expect(info.pos).toBe("fixed");
    expect(info.anim).not.toBe("none");
    expect(info.duration).toBeGreaterThanOrEqual(90); // extremely slow (seconds)
    expect(info.pointer).toBe("none");
  });
  test("reduced motion keeps every ambient layer (depth) and removes every animation", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const names = await page.getByTestId("field-background").evaluate((el) => [...el.querySelectorAll(".nebula, .particle, .drift, .traces")].map((n) => getComputedStyle(n).animationName));
    expect(names.length).toBeGreaterThanOrEqual(5);
    for (const n of names) expect(n).toBe("none");
    const sep = await page.locator(".trace li").nth(1).evaluate((el) => getComputedStyle(el, "::before").animationName);
    expect(sep).toBe("none");
    const layers = await page.getByTestId("field-background").evaluate((el) => [...el.querySelectorAll(".nebula")].filter((n) => getComputedStyle(n).display !== "none").length);
    expect(layers).toBeGreaterThanOrEqual(2);
  });
});

test.describe("phone (doc 23 §14.3; falsifiers 40–41)", () => {
  test("the stack keeps every capability reachable with full-width, readable rows", async ({ page }) => {
    test.skip(!isPhone(page), "phone representation");
    await stressRoutes(page);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.getByTestId("field-core").waitFor();
    const p = await probe(page);
    const page_width = page.viewportSize()!.width;
    expect(p.escaping).toEqual([]);
    expect(p.overlaps).toEqual([]);
    expect(p.hOverflow).toBeLessThanOrEqual(1);
    // SF-04 (doc 25 §15.4): the phone representation is a breathing constellation of capsules, not rows — every
    // capsule is a full tap target inside the viewport with its whole label visible (containment probed above)
    const boxes = await page.locator('[data-testid="sessions-list"] .node-body').evaluateAll((els) => els.map((e) => ({ w: Math.round(e.getBoundingClientRect().width), h: Math.round(e.getBoundingClientRect().height) })));
    expect(boxes.every((b) => b.h >= 40 && b.w >= 120 && b.w <= page_width), `capsules ${JSON.stringify(boxes)}`).toBe(true);
    await expect(page.getByRole("button", { name: "Grant session control for this Challenge" })).toBeVisible();
    await expect(page.getByTestId("session-create-unavailable")).toBeVisible();
    await expect(page.getByTestId("identity")).toBeVisible();
  });
});
