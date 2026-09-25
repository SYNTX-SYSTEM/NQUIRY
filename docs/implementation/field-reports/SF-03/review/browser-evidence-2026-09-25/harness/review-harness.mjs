/**
 * SF-03 visible-website review harness (evidence tool; not a product test) = the SF-02 harness (30 regression
 * states, unchanged) + the doc 23 acceptance states (31+): centred identity, symbiotic breadcrumb, living
 * background (+ reduced-motion depth), lifecycle labels readable, instrument constellation on a wide desktop,
 * Field/instrument reciprocity by keyboard, text containment, node collision resistance, long-label stress on a
 * second Workspace/Challenge founded through the product (`setup-scenario.mjs --stress`), phone capability.
 *
 * Real Chromium against the isolated inspection runtime (compose project
 * `nquiry-sf03-inspect`, http://127.0.0.1:13300). For every reviewed state it
 * records: URL, identity, viewport, canonical state from the server projection
 * (read with the same browser session), expected relation vs visible
 * affordances, console, page errors, failed requests (aborted `_rsc` prefetches
 * recorded separately), 4xx/5xx, `_next/static` results, stylesheet + design
 * tokens, horizontal overflow, axe WCAG 2 A/AA (all impacts), keyboard focus
 * walk with visible-focus check, redirect chain, and the Field topology
 * (`data-topology`, node states, path states). No network interception.
 * The Session lifecycle is driven through the real UI (Open Session → grant →
 * Begin setup → … → Open question generation → capture → Complete Burst…).
 * Reduced-motion states are captured with `emulateMedia`.
 *
 * Usage (worktree root, runtime up):
 *   EVIDENCE_RUN=<dir> node docs/…/SF-02/review/browser-evidence-2026-09-25/harness/review-harness.mjs <workspaceId> <challengeId>
 */
import { chromium, devices } from "@playwright/test";
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");
const BASE = process.env.INSPECT_BASE ?? "http://127.0.0.1:13300";
const API = `${BASE}/api`;
const EVIDENCE = join(dirname(fileURLToPath(import.meta.url)), "..");
const RUN = process.env.EVIDENCE_RUN ?? "run-1";
const ROOT = join(EVIDENCE, RUN);
const SHOTS = join(ROOT, "screenshots");
mkdirSync(SHOTS, { recursive: true });

const [WS, CH, STRESS_WS, STRESS_CH] = process.argv.slice(2);
if (!WS || !CH) throw new Error("usage: review-harness.mjs <workspaceId> <challengeId> [<stressWorkspaceId> <stressChallengeId>]");
let SID = null;

const ID = {
  owner: { email: "owner@inspect.local.test", password: "inspect-owner-2026", name: "Inspect Owner" },
  facilitator: { email: "facilitator@inspect.local.test", password: "inspect-fac-2026", name: "Inspect Facilitator" },
  outsider: { email: "outsider@inspect.local.test", password: "inspect-outsider-2026", name: "Inspect Outsider" },
};
const VIEWPORTS = { desktop: { viewport: { width: 1280, height: 860 } }, wide: { viewport: { width: 1600, height: 900 } }, "pixel-7": { ...devices["Pixel 7"] } };
const results = [];
let seq = 0;

async function newPage(browser, viewportName, opts = {}) {
  const context = await browser.newContext({ ...VIEWPORTS[viewportName], reducedMotion: opts.reducedMotion ?? "no-preference" });
  const page = await context.newPage();
  const log = { console: [], pageErrors: [], failed: [], prefetchAborted: [], http4xx5xx: [], statics: [], nav: [] };
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") log.console.push(`${m.type()}: ${m.text()}`); });
  page.on("pageerror", (e) => log.pageErrors.push(String(e)));
  page.on("requestfailed", (r) => {
    const line = `${r.method()} ${r.url().replace(BASE, "")} :: ${r.failure()?.errorText}`;
    if (r.url().includes("_rsc=") && /ERR_ABORTED|ERR_INTERNET_DISCONNECTED/.test(r.failure()?.errorText ?? "")) log.prefetchAborted.push(line);
    else log.failed.push(line);
  });
  page.on("response", (r) => {
    const u = r.url();
    if (u.includes("/_next/static/")) log.statics.push({ url: u.replace(BASE, ""), status: r.status() });
    if (r.status() >= 400) log.http4xx5xx.push(`${r.status()} ${r.request().method()} ${u.replace(BASE, "")}`);
  });
  page.on("framenavigated", (f) => { if (f === page.mainFrame()) log.nav.push(f.url().replace(BASE, "")); });
  return { context, page, log, viewportName, reducedMotion: opts.reducedMotion ?? "no-preference" };
}
const resetLog = (log) => { for (const k of Object.keys(log)) log[k].length = 0; };

async function login(p, who) {
  resetLog(p.log);
  await p.page.goto(`${BASE}/login`);
  await p.page.getByLabel("Email").fill(who.email);
  await p.page.getByLabel("Password").fill(who.password);
  await p.page.getByRole("button", { name: "Log in" }).click();
  await p.page.waitForURL(/\/workspaces$/);
  await p.page.locator('[data-testid="workspaces-list"], [data-testid="workspaces-empty"], [data-testid="workspaces-denied"]').first().waitFor();
  await p.page.waitForLoadState("networkidle");
  return [...p.log.nav];
}
async function api(p, path) {
  const r = await p.page.request.get(`${API}${path}`);
  let body = null; try { body = await r.json(); } catch { body = null; }
  return { status: r.status(), body };
}
async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    // @ts-ignore injected
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] } });
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, targets: v.nodes.slice(0, 3).map((n) => n.target.join(" ")) }));
  });
}
async function focusWalk(page, maxTabs = 40) {
  await page.evaluate(() => { if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur(); window.scrollTo(0, 0); });
  const steps = [];
  for (let i = 0; i < maxTabs; i++) {
    await page.keyboard.press("Tab");
    const s = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const cs = getComputedStyle(el);
      const outline = cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0;
      const name = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("name") || el.id || "").trim().replace(/\s+/g, " ").slice(0, 50);
      return { tag: el.tagName.toLowerCase(), name, visibleFocus: outline || cs.boxShadow !== "none" };
    });
    if (s === null) break;
    const key = `${s.tag}|${s.name}`;
    if (steps.length && steps[0].key === key) break;
    steps.push({ key, ...s });
  }
  return { reachable: steps.length, withoutVisibleFocus: steps.filter((s) => !s.visibleFocus).map((s) => `${s.tag}:${s.name}`), order: steps.map((s) => `${s.tag}:${s.name}`) };
}
const overflow = (page) => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
const cssLoaded = (page) => page.evaluate(() => ({
  stylesheets: [...document.styleSheets].map((s) => s.href?.replace(location.origin, "") ?? "inline"),
  tokens: { cyan: getComputedStyle(document.documentElement).getPropertyValue("--cyan").trim(), blue: getComputedStyle(document.documentElement).getPropertyValue("--blue").trim(), red: getComputedStyle(document.documentElement).getPropertyValue("--red").trim() },
  bodyBackground: getComputedStyle(document.body).backgroundColor,
  backgroundField: !!document.querySelector('[data-testid="field-background"]'),
}));
const topology = (page) => page.evaluate(() => {
  const stage = document.querySelector('[data-testid="field-stage"]');
  const core = document.querySelector(".core");
  const orbit = document.querySelector(".orbit");
  return {
    // semantic mode (count-based, in the DOM) and effective presentation mode (viewport may stack via CSS)
    mode: stage?.getAttribute("data-topology") ?? null,
    effectiveMode: orbit ? (getComputedStyle(orbit).position === "absolute" ? "orbit" : "stack") : null,
    surface: stage?.getAttribute("data-surface") ?? null,
    coreState: core?.getAttribute("data-core-state") ?? null,
    coreEyebrow: core?.querySelector(".eyebrow")?.textContent?.trim() ?? null,
    nodes: [...document.querySelectorAll(".node")].map((n) => ({ state: n.getAttribute("data-node-state"), text: (n.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 60) })),
    paths: [...document.querySelectorAll(".orbit-paths .path")].map((p) => p.getAttribute("data-path")),
    coreAnimation: core ? getComputedStyle(core).animationName : null,
    bgAnimation: (() => { const bg = document.querySelector(".field-bg"); return bg ? getComputedStyle(bg, "::after").animationName : null; })(),
  };
});
const texts = (loc) => loc.evaluateAll((els) => els.map((e) => (e.textContent ?? "").replace(/\s+/g, " ").trim()));
const traceData = (page) => page.getByRole("navigation", { name: "Inquiry position" }).getByRole("listitem").evaluateAll((lis) => lis.map((li) => [li.dataset.coordinate, li.dataset.status, (li.querySelector("a, .trace-label")?.textContent ?? "").trim()]));
const check = (claim, expected, actual, kind = "visible") => ({ claim, kind, expected, actual, pass: JSON.stringify(expected) === JSON.stringify(actual) });

async function record(p, meta, verify, { expectedHttp = [] } = {}) {
  const { page, log, viewportName } = p;
  await page.waitForLoadState("networkidle");
  seq += 1;
  const file = `${String(seq).padStart(2, "0")}-${viewportName}${p.reducedMotion === "reduce" ? "-reduced-motion" : ""}-${meta.slug}.png`;
  const v = verify ? await verify(page) : { projection: null, checks: [] };
  await page.screenshot({ path: join(SHOTS, file), fullPage: true });
  const axeViolations = await axe(page);
  const focus = meta.keyboard === false ? null : await focusWalk(page);
  const entry = {
    seq, screenshot: `screenshots/${file}`, url: page.url().replace(BASE, ""), route: meta.route, viewport: viewportName, reducedMotion: p.reducedMotion,
    identity: meta.identity, canonicalState: meta.canonicalState, expectedRelation: meta.expected,
    projection: v.projection, checks: v.checks, topology: await topology(page),
    redirectChain: meta.redirectChain ?? [...log.nav], console: [...log.console], pageErrors: [...log.pageErrors],
    failedRequests: [...log.failed], prefetchAborted: [...log.prefetchAborted], http4xx5xx: [...log.http4xx5xx],
    unexpectedHttp: log.http4xx5xx.filter((h) => !expectedHttp.some((re) => re.test(h))),
    staticRequests: log.statics.length, staticNon200: log.statics.filter((s) => s.status !== 200 && s.status !== 304),
    css: await cssLoaded(page), overflowPx: await overflow(page),
    axeSeriousCritical: axeViolations.filter((x) => x.impact === "serious" || x.impact === "critical"),
    axeOther: axeViolations.filter((x) => x.impact !== "serious" && x.impact !== "critical"),
    keyboard: focus,
    localTruthDetected: v.checks.some((c) => c.kind === "projection" && !c.pass),
  };
  const offline = meta.offline === true;
  entry.expectedOffline = offline;
  entry.pass = v.checks.every((c) => c.pass) && entry.pageErrors.length === 0 && (offline || entry.failedRequests.length === 0) && entry.unexpectedHttp.length === 0 &&
    entry.staticNon200.length === 0 && entry.overflowPx <= 1 && entry.axeSeriousCritical.length === 0 &&
    (offline || entry.console.filter((c) => c.startsWith("error")).every((c) => expectedHttp.some((re) => re.test(c)))) &&
    (entry.keyboard === null || entry.keyboard.withoutVisibleFocus.length === 0);
  results.push(entry);
  resetLog(log);
  console.log(`${entry.pass ? "PASS" : "FAIL"} #${seq} ${viewportName}${p.reducedMotion === "reduce" ? " (reduced motion)" : ""} ${meta.slug}`);
  return entry;
}

const browser = await chromium.launch();

// ---------------------------------------------------------------- Access Field (anonymous), desktop + phone + reduced motion
for (const [vp, rm] of [["desktop", "no-preference"], ["pixel-7", "no-preference"], ["desktop", "reduce"]]) {
  const a = await newPage(browser, vp, { reducedMotion: rm });
  await a.page.goto(`${BASE}/`);
  await a.page.waitForURL(/\/login$/);
  await record(a, { slug: "access-login", route: "/ -> /login", identity: "anonymous", canonicalState: "no NQUIRY session (GET /auth/me -> 401 denied)", expected: "Access core: dark field, centred identity entrance; no workspace topology; no external provider; Log in reachable" },
    async (page) => {
      const me = await api(a, "/auth/me");
      const t = await topology(page);
      return { projection: { authMe: me }, checks: [
        check("server: no session", 401, me.status, "projection"),
        check("ends at /login", "/login", new URL(page.url()).pathname),
        check("form fields", ["Email", "Password"], await texts(page.locator("form label"))),
        check("submit reachable", 1, await page.getByRole("button", { name: "Log in" }).count()),
        check("no workspace topology on access", null, t.mode),
        check("no external provider affordance", 0, await page.getByRole("button", { name: /google|github|provider/i }).count()),
        check("background field present", true, (await cssLoaded(page)).backgroundField),
        check("access core marked", 1, await page.locator('[data-testid="access-core"]').count()),
        ...(rm === "reduce" ? [check("reduced motion: background animation none", "none", t.bgAnimation)] : []),
      ] };
    }, { expectedHttp: [/^401 GET \/api\/auth\/me$/, /401 \(Unauthorized\)/] });
  // failure boundary: wrong credentials
  await a.page.getByLabel("Email").fill("nobody@inspect.local.test");
  await a.page.getByLabel("Password").fill("wrong");
  await a.page.getByRole("button", { name: "Log in" }).click();
  await a.page.getByTestId("login-error").waitFor();
  await record(a, { slug: "access-denied", route: "/login", identity: "anonymous (wrong credentials)", canonicalState: "POST /auth/login -> denied", expected: "boundary announced (role=alert), form retained, no success motion, submit still reachable" },
    async (page) => ({ projection: null, checks: [
      check("alert present", 1, await page.getByRole("alert").filter({ hasText: /Incorrect/ }).count()),
      check("stays on /login", "/login", new URL(page.url()).pathname),
      check("email retained", "nobody@inspect.local.test", await page.getByLabel("Email").inputValue()),
      check("submit reachable", true, await page.getByRole("button", { name: "Log in" }).isEnabled()),
    ] }), { expectedHttp: [/^401 (GET|POST) \/api\/auth\/(me|login)$/, /401 \(Unauthorized\)/] });
  await a.context.close();
}

// ---------------------------------------------------------------- Workspace overview + Workspace Field (owner), desktop + phone
const ownerPages = {};
for (const vp of ["desktop", "pixel-7"]) {
  const o = await newPage(browser, vp);
  ownerPages[vp] = o;
  const chain = await login(o, ID.owner);
  await record(o, { slug: "workspace-overview-owner", route: "/login -> / -> /workspaces", identity: ID.owner.email, canonicalState: "authenticated; accessible Workspaces from GET /workspaces", expected: "identity/access core; founding relation possible; accessible Workspaces as nodes (links); trace = access only", redirectChain: chain },
    async (page) => {
      const me = await api(o, "/auth/me"); const ws = await api(o, "/workspaces"); const names = ws.body.workspaces.map((w) => w.name); const t = await topology(page);
      return { projection: { authMe: me.body, workspaces: names }, checks: [
        check("session resolves", "ok", me.body.kind, "projection"),
        check("workspace links = server list", names, await texts(page.getByTestId("workspaces-list").getByRole("link")), "projection"),
        check("trace = access only", [["access", "current", "Workspaces"]], await traceData(page), "projection"),
        check("founding node possible", 1, await page.locator('[data-testid="found-workspace-node"][data-node-state="possible"]').count()),
        check("core = access, current", "current", t.coreState),
        check("logout reachable after identity confirmed", 1, await page.getByTestId("logout-button").count()),
      ] };
    });
  await o.page.goto(`${BASE}/workspaces/${WS}`);
  await o.page.locator('[data-testid="challenges-list"], [data-testid="challenges-empty"]').first().waitFor();
  await record(o, { slug: "workspace-field-owner", route: "/workspaces/[w]", identity: ID.owner.email, canonicalState: "Workspace; viewer = governance root (Owner), not Facilitator", expected: "workspace core; Challenge relation unavailable with server reason (node + reason); members/authority orbit; add member (governance-capable); proof depth" },
    async (page) => {
      const ov = await api(o, `/workspaces/${WS}/overview`); const cc = ov.body.capabilities.createChallenge; const t = await topology(page);
      return { projection: { createChallenge: cc, challenges: ov.body.challenges.map((c) => c.title), members: ov.body.members.map((m) => m.name) }, checks: [
        check("challenge links = server", ov.body.challenges.map((c) => c.title), await texts(page.getByTestId("challenges-list").getByRole("link")), "projection"),
        check("new-challenge node state = capability", cc.available ? "possible" : "unavailable", await page.getByTestId("new-challenge-node").getAttribute("data-node-state"), "projection"),
        check("reason = server reason", cc.reason, cc.available ? null : (await page.getByTestId("challenge-create-unavailable").textContent()).trim(), "projection"),
        check("member nodes = server members", ov.body.members.length, t.nodes.filter((n) => n.state === "human").length, "projection"),
        check("add-member form (governance root)", 1, await page.getByTestId("add-member-form").count()),
        check("effective topology mode", vp === "desktop" ? "orbit" : "stack", t.effectiveMode),
        check("no two nodes overlap (D8)", 0, await nodeOverlaps(page)),
      ] };
    });
}


// D8 guard: on an orbit, no two node bodies may intersect (rings never share a spoke; 22 §13.3).
async function nodeOverlaps(page) {
  return page.evaluate(() => {
    const r = [...document.querySelectorAll('[data-testid="field-stage"] .node-body')].map((e) => e.getBoundingClientRect());
    let n = 0;
    for (let i = 0; i < r.length; i++) for (let j = i + 1; j < r.length; j++) {
      const a = r[i], b = r[j];
      if (a.width && b.width && a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) n++;
    }
    return n;
  });
}
/** doc 23 §6 containment + legibility, measured on the rendered page (same probe as tests/e2e/sf03-field.spec.ts). */
async function containment(page) {
  return page.evaluate(() => {
    const frames = [...document.querySelectorAll(".node-body, .core, .plane, .trace li")];
    const escaping = [];
    let smallest = 99;
    const inside = (i, o) => i.left >= o.left - 1 && i.right <= o.right + 1 && i.top >= o.top - 1 && i.bottom <= o.bottom + 1;
    for (const b of frames) {
      if (b.scrollWidth > b.clientWidth + 2 || b.scrollHeight > b.clientHeight + 2) escaping.push(`scroll:${b.className}:${(b.textContent ?? "").slice(0, 30)}`);
      const f = b.getBoundingClientRect();
      for (const t of b.querySelectorAll(".node-label, .node-meta, .node-marker, .core-title, .core-state, .core-meta, h2, h3, .mono, .tag")) {
        if (getComputedStyle(t).position === "absolute" || t.closest("details:not([open])")) continue;
        const r = t.getBoundingClientRect();
        if (r.width > 0 && !inside(r, f)) escaping.push(`text:${t.className}:${(t.textContent ?? "").slice(0, 30)}`);
        if ((t.textContent ?? "").trim() && !t.classList.contains("visually-hidden")) smallest = Math.min(smallest, parseFloat(getComputedStyle(t).fontSize));
      }
    }
    const t = document.querySelector(".topology");
    return { escaping, smallest: Math.round(smallest * 100) / 100, fit: t?.getAttribute("data-fit") ?? null, compact: t?.getAttribute("data-compact") ?? null, box: t ? [Math.round(t.getBoundingClientRect().width), Math.round(t.getBoundingClientRect().height)] : null };
  });
}
const identityCentred = (page) => page.evaluate(() => { const el = document.querySelector('[data-testid="identity"]'); const r = el?.getBoundingClientRect(); return r ? Math.round(Math.abs(r.left + r.width / 2 - window.innerWidth / 2)) : null; });
const instrumentColumns = (page) => page.evaluate(() => { const el = document.querySelector(".instruments"); return el ? getComputedStyle(el).gridTemplateColumns.split(" ").length : null; });
const ambient = (page) => page.evaluate(() => { const bg = document.querySelector(".field-bg"); const layers = [...bg.querySelectorAll(".nebula, .particle, .drift, .traces")]; const durations = layers.map((l) => parseFloat(getComputedStyle(l).animationDuration)).filter((d) => d > 0); return { fixed: getComputedStyle(bg).position, coversViewport: bg.getBoundingClientRect().width >= window.innerWidth - 1 && bg.getBoundingClientRect().height >= window.innerHeight - 1, animated: layers.filter((l) => getComputedStyle(l).animationName !== "none").length, layersShown: [...bg.querySelectorAll(".nebula")].filter((l) => getComputedStyle(l).display !== "none").length, minDurationS: durations.length ? Math.min(...durations) : null, pointer: getComputedStyle(bg).pointerEvents }; });
const railStable = async (page) => { const cur = page.locator('.trace li[data-status="current"] .trace-label'); const a = await cur.boundingBox(); await page.waitForTimeout(600); const b = await cur.boundingBox(); const sep = await page.locator(".trace li").nth(1).evaluate((el) => ({ energy: getComputedStyle(el, "::before").animationName, text: getComputedStyle(el).animationName, transform: getComputedStyle(el).transform })).catch(() => ({ energy: null, text: null, transform: null })); const sizes = await page.locator(".trace a, .trace .trace-label").evaluateAll((els) => els.map((e) => parseFloat(getComputedStyle(e).fontSize))); return { textMoved: JSON.stringify(a) !== JSON.stringify(b), separatorEnergy: sep.energy, textAnimation: sep.text, textTransform: sep.transform, minFont: sizes.length ? Math.min(...sizes) : null }; };

// ---------------------------------------------------------------- Challenge Field (PRIMARY), facilitator, desktop + phone + reduced motion
for (const [vp, rm] of [["desktop", "no-preference"], ["pixel-7", "no-preference"], ["desktop", "reduce"]]) {
  const f = await newPage(browser, vp, { reducedMotion: rm });
  await login(f, ID.facilitator);
  await f.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
  await record(f, { slug: "challenge-field-PRIMARY-facilitator", route: "/workspaces/[w]/challenges/[c]", identity: ID.facilitator.email, canonicalState: "Challenge; Facilitator holds SESSION_CONTROL_RIGHT at CHALLENGE:<c>", expected: "PRIMARY SURFACE: challenge core central; sessions orbit with New Session POSSIBLE (Open Session effect node) + established session nodes; governance orbit with holder; relation paths; proof depth; living background" },
    async (page) => {
      const d = await api(f, `/workspaces/${WS}/challenges/${CH}`); const os = d.body.capabilities.openSession; const t = await topology(page);
      return { projection: { openSession: os, sessions: d.body.sessions.map((s) => s.state), controllers: d.body.sessionControllers.map((b) => b.holderName) }, checks: [
        check("trace", [["access", "established", "Workspaces"], ["workspace", "established", d.body.workspace.name], ["challenge", "current", d.body.challenge.title], ["session", os.available ? "possible" : "unavailable", "New Session"]], await traceData(page), "projection"),
        check("New Session node state = capability", os.available ? "possible" : "unavailable", await page.getByTestId("new-session-node").getAttribute("data-node-state"), "projection"),
        check("Open Session effect reachable iff capability", os.available, (await page.getByRole("button", { name: "Open Session" }).count()) === 1, "projection"),
        check("session nodes = server sessions", d.body.sessions.length, await page.getByTestId("sessions-list").getByRole("link").count(), "projection"),
        check("governance nodes = server controllers", d.body.sessionControllers.length, t.nodes.filter((n) => n.state === "governance").length, "projection"),
        check("relation paths exist only for real relations", t.nodes.length, t.paths.length),
        check("core state current", "current", t.coreState),
        check("effective topology mode", vp === "desktop" ? "orbit" : "stack", t.effectiveMode),
        check("not a card grid: no .panel grid inside the stage", 0, await page.locator('[data-testid="field-stage"] .grid-2').count()),
        check("no two nodes overlap (D8)", 0, await nodeOverlaps(page)),
        ...(rm === "reduce" ? [check("reduced motion: core animation none", "none", t.coreAnimation), check("reduced motion: New Session still reachable", os.available, (await page.getByRole("button", { name: "Open Session" }).count()) === 1, "projection")] : []),
      ] };
    });
  await f.context.close();
}

// ---------------------------------------------------------------- Session Field driven through the UI (desktop facilitator + owner), phone reads
const fac = await newPage(browser, "desktop");
await login(fac, ID.facilitator);
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
await fac.page.getByRole("button", { name: "Open Session" }).click();
await fac.page.waitForURL(/\/sessions\/[0-9a-f-]{36}$/);
SID = fac.page.url().split("/sessions/")[1];
const sessionUrl = `${BASE}/workspaces/${WS}/sessions/${SID}`;
await fac.page.getByTestId("session-state").filter({ hasText: /^DRAFT$/ }).waitFor();
await record(fac, { slug: "session-draft-no-control", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "Session DRAFT (created via the Open Session effect + re-read); Facilitator has NO SESSION-scoped control (HD-1)", expected: "session core state DRAFT; lifecycle orbit with DRAFT current; Begin setup visible only as unavailable with server reason; no controller affordance" },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`); const t = await topology(page);
    return { projection: { state: pos.body.session.state, beginSetup: pos.body.actions.BEGIN_SETUP, phases: pos.body.phases.filter((p) => p.status !== "upcoming").map((p) => `${p.state}:${p.status}`) }, checks: [
      check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
      check("current lifecycle node = server current phase", pos.body.phases.find((p) => p.status === "current").state, await page.locator('[data-testid="session-phases"] [aria-current="step"]').getAttribute("data-testid") ?? (await page.locator('[data-testid="session-phases"] [aria-current="step"] .node-label').textContent()).replace(/^\d+\.\s*/, "").toUpperCase().replace(/ \(PROTECTED\)/, "").replace(/ /g, "_"), "projection"),
      check("Begin setup control iff capability", pos.body.actions.BEGIN_SETUP.available, (await page.getByRole("button", { name: "Begin setup" }).count()) === 1, "projection"),
      check("lifecycle nodes = 13 projected phases", pos.body.phases.length, t.nodes.filter((n) => ["established", "current", "future"].includes(n.state)).length, "projection"),
      check("core state", "current", t.coreState),
    ] };
  });
const own = ownerPages.desktop;
await own.page.goto(sessionUrl);
await own.page.getByTestId("session-state").waitFor();
for (let attempt = 0; attempt < 10; attempt++) {
  await own.page.getByLabel("Grant session control to").selectOption({ label: ID.facilitator.name });
  if (await own.page.getByRole("button", { name: "Grant session control for this Session" }).isEnabled()) break;
  await own.page.waitForTimeout(300);
}
await own.page.getByRole("button", { name: "Grant session control for this Session" }).click();
await own.page.getByTestId("session-authority-provenance").getByText(ID.facilitator.name).waitFor();
await record(own, { slug: "session-grant-committed-owner", route: "/workspaces/[w]/sessions/[s]", identity: ID.owner.email, canonicalState: "SESSION_CONTROL_RIGHT granted at SESSION scope (committed + re-read)", expected: "committed outcome (blue, re-read line), governance node for the holder appears after re-read; no cyan/green success" },
  async (page) => {
    const pos = await api(own, `/workspaces/${WS}/sessions/${SID}/position`); const t = await topology(page);
    return { projection: { controllers: pos.body.sessionControllers.map((b) => b.holderName) }, checks: [
      check("outcome committed + reconstruction done", ["committed", "done"], [await page.getByTestId("command-outcome").getAttribute("data-outcome"), await page.getByTestId("command-outcome").getAttribute("data-reconstruction")]),
      check("holder in governance provenance", true, (await page.getByTestId("session-authority-provenance").textContent()).includes(ID.facilitator.name), "projection"),
      check("controller node present in relation orbit", true, t.nodes.some((n) => n.state === "governance" && n.text.includes(ID.facilitator.name)), "projection"),
    ] };
  });
// facilitator: lawful progression
await fac.page.goto(sessionUrl);
for (const [label, produced] of [
  ["Begin setup", () => fac.page.getByTestId("session-state").filter({ hasText: /^SETUP$/ }).waitFor()],
  ["Begin challenge capture", () => fac.page.getByTestId("session-state").filter({ hasText: /^CHALLENGE_CAPTURE$/ }).waitFor()],
  ["Prepare protected Burst", () => fac.page.getByTestId("burst-state").filter({ hasText: /^PREPARED$/ }).waitFor()],
]) {
  await fac.page.getByRole("button", { name: label }).click();
  await produced();
  await fac.page.waitForLoadState("networkidle");
}
await record(fac, { slug: "session-challenge-capture-burst-prepared", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "CHALLENGE_CAPTURE; Burst PREPARED; no participant yet", expected: "lifecycle reconstructed (DRAFT, SETUP passed; CHALLENGE_CAPTURE current); Open question generation BLOCKED with server reason (participant); admit affordance" },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`);
    return { projection: { state: pos.body.session.state, open: pos.body.actions.OPEN_QUESTION_GENERATION }, checks: [
      check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
      check("open-generation control iff capability", pos.body.actions.OPEN_QUESTION_GENERATION.available, (await page.getByRole("button", { name: "Open question generation" }).count()) === 1, "projection"),
      check("reason shown when unavailable", pos.body.actions.OPEN_QUESTION_GENERATION.available ? null : pos.body.actions.OPEN_QUESTION_GENERATION.reason, pos.body.actions.OPEN_QUESTION_GENERATION.available ? null : (await page.getByTestId("action-reason-OPEN_QUESTION_GENERATION").textContent()).trim(), "projection"),
      check("passed phases = server done", pos.body.phases.filter((p) => p.status === "done").length, await page.locator('[data-testid="session-phases"] [data-node-state="established"]').count(), "projection"),
    ] };
  });
for (const who of [ID.facilitator.name, ID.owner.name]) {
  for (let attempt = 0; attempt < 10; attempt++) {
    await fac.page.getByLabel("Admit participant").selectOption({ label: who });
    if (await fac.page.getByRole("button", { name: "Admit to Session" }).isEnabled()) break;
    await fac.page.waitForTimeout(300);
  }
  await fac.page.getByRole("button", { name: "Admit to Session" }).click();
  await fac.page.getByTestId("participants-list").getByText(who).waitFor();
  await fac.page.waitForLoadState("networkidle");
}
await fac.page.getByRole("button", { name: "Open question generation" }).click();
await fac.page.getByTestId("burst-state").filter({ hasText: /^ACTIVE$/ }).waitFor();
await fac.page.getByLabel("Your question", { exact: true }).fill("The checkout is slow.");
await fac.page.getByRole("button", { name: "Submit question" }).click();
await fac.page.getByTestId("command-outcome").filter({ hasText: /Nothing was stored/ }).waitFor();
await record(fac, { slug: "human-question-field-rejected-input", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "QUESTION_GENERATION; Burst ACTIVE HUMAN_ONLY; capture REJECTED (HD-12 form rule)", expected: "core = Human question field (cyan); REJECTED boundary announced with plain-words reason, text retained, nothing stored" },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`); const t = await topology(page);
    return { projection: { state: pos.body.session.state, burst: pos.body.burst.state, mine: pos.body.questionSet.mine.length }, checks: [
      check("core = human", "human", t.coreState),
      check("outcome rejected", ["rejected", "alert"], [await page.getByTestId("command-outcome").getAttribute("data-outcome"), await page.getByTestId("command-outcome").getAttribute("role")]),
      check("nothing stored (server mine = 0)", 0, pos.body.questionSet.mine.length, "projection"),
      check("text retained", "The checkout is slow.", await page.getByLabel("Your question", { exact: true }).inputValue()),
    ] };
  }, { expectedHttp: [/^400 POST \/api\/workspaces\/[0-9a-f-]+\/sessions\/[0-9a-f-]+\/burst\/questions$/, /400 \(Bad Request\)/] });
await fac.page.getByLabel("Your question", { exact: true }).fill("Which step do most new users abandon first?");
await fac.page.getByLabel("Your question", { exact: true }).press("Control+Enter");
await fac.page.getByTestId("own-question").first().waitFor();
await record(fac, { slug: "human-question-field-own-question-controller", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "QUESTION_GENERATION; own question committed; viewer = controller + participant", expected: "own question (exact text, human) after commit + re-read; count for controller; timer presentation-only; Complete Burst offered; no peer content" },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`);
    return { projection: { mine: pos.body.questionSet.mine.map((q) => q.originalText), capturedCount: pos.body.questionSet.capturedCount, complete: pos.body.actions.COMPLETE_BURST }, checks: [
      check("own texts = server (exact)", pos.body.questionSet.mine.map((q) => q.originalText), await page.getByTestId("own-question-text").evaluateAll((e) => e.map((x) => x.textContent)), "projection"),
      check("count = server", String(pos.body.questionSet.capturedCount), (await page.getByTestId("captured-count").locator("strong").textContent()).trim(), "projection"),
      check("Complete Burst iff capability", pos.body.actions.COMPLETE_BURST.available, (await page.getByRole("button", { name: /Complete Burst/ }).count()) === 1, "projection"),
      check("timer is presentation only", true, (await page.getByTestId("burst-timer").textContent()).includes("nothing closes it automatically")),
      check("no BEGIN_ANALYSIS", 0, await page.getByText(/begin analysis/i).count()),
    ] };
  });
await own.page.goto(sessionUrl);
await own.page.getByLabel("Your question", { exact: true }).fill("What did users expect to happen after signup?");
await own.page.getByRole("button", { name: "Submit question" }).click();
await own.page.getByTestId("own-question").first().waitFor();
// doc 23 §13.6 / §11: the Human Question Field on a wide desktop — input first, governance/proof beside it
{
  const facW = await newPage(browser, "wide");
  await login(facW, ID.facilitator);
  await facW.page.goto(sessionUrl);
  await facW.page.getByTestId("capture-form").waitFor();
  await record(facW, { slug: "human-question-field-wide-constellation", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "QUESTION_GENERATION; Burst ACTIVE HUMAN_ONLY; wide desktop 1600", expected: "instrument constellation: human input in the first column, governance and proof beside it (no waterfall); identity centred; text contained; no node overlaps; lifecycle labels readable" },
    async (page) => { const c = await containment(page); const cols = await instrumentColumns(page); const human = await page.locator('.plane[data-plane="human"]').boundingBox(); const gov = await page.locator('.plane[data-plane="governance"]').boundingBox(); const proof = await page.locator('.plane[data-plane="proof"]').boundingBox(); const labels = await page.locator('[data-testid="session-phases"] .node-label').evaluateAll((els) => els.map((e) => ({ w: e.getBoundingClientRect().width, fs: parseFloat(getComputedStyle(e).fontSize), hidden: e.classList.contains("visually-hidden") })));
      return { projection: null, checks: [
        check("two instrument columns", 2, cols), check("governance beside the human input (not below)", true, gov.x > human.x + human.width - 1 && proof.x > human.x + human.width - 1),
        check("governance above proof", true, gov.y < proof.y), check("identity centred (px off centre ≤ 12)", true, (await identityCentred(page)) <= 12),
        check("no text escapes its frame", [], c.escaping), check("no text below 11.5px", true, c.smallest >= 11.5), check("layout fits", "fits", c.fit),
        check("no two nodes overlap", 0, await nodeOverlaps(page)), check("all 13 lifecycle labels visible and ≥ 12.5px", true, labels.length === 13 && labels.every((l) => !l.hidden && l.w > 0 && l.fs >= 12.5)),
      ] }; });
  await facW.context.close();
}
await record(own, { slug: "human-question-field-participant-own-only", route: "/workspaces/[w]/sessions/[s]", identity: ID.owner.email, canonicalState: "QUESTION_GENERATION; Owner = participant, not controller", expected: "own question only (HD-13); peer question absent; no Complete Burst; participants visible as relation nodes without content" },
  async (page) => {
    const pos = await api(own, `/workspaces/${WS}/sessions/${SID}/position`); const t = await topology(page);
    return { projection: { visibility: pos.body.questionSet.visibility, mine: pos.body.questionSet.mine.map((q) => q.originalText) }, checks: [
      check("own texts = server", pos.body.questionSet.mine.map((q) => q.originalText), await page.getByTestId("own-question-text").evaluateAll((e) => e.map((x) => x.textContent)), "projection"),
      check("peer question hidden", 0, await page.getByText("Which step do most new users abandon first?").count()),
      check("no Complete Burst", 0, await page.getByRole("button", { name: /Complete Burst/ }).count()),
      check("participant nodes = server participants", pos.body.participants.length, t.nodes.filter((n) => n.state === "human").length, "projection"),
    ] };
  });
const facM = ownerPages["pixel-7"];
await facM.page.goto(sessionUrl);
await facM.page.getByTestId("own-question").first().waitFor();
await record(facM, { slug: "human-question-field-phone", route: "/workspaces/[w]/sessions/[s]", identity: ID.owner.email, canonicalState: "QUESTION_GENERATION on Pixel 7", expected: "relational stack: core → lifecycle → active phase (capture) → relations → governance → proof; capture reachable; no overflow" },
  async (page) => {
    const y = async (sel) => (await page.locator(sel).first().boundingBox())?.y ?? -1;
    const order = [await y('[data-testid="field-core"]'), await y('[data-testid="session-phases"]'), await y('[data-plane="human"]'), await y('[data-plane="governance"]'), await y('[data-plane="proof"]')];
    return { projection: null, checks: [check("stack order core → lifecycle → active phase → governance → proof", true, order.every((v, i) => i === 0 || v > order[i - 1])), check("capture reachable on phone", 1, await page.getByTestId("capture-form").count()), check("effective topology stack", "stack", (await topology(page)).effectiveMode),
      check("lifecycle rows uniform and full width (D3)", true, await page.locator('[data-testid="session-phases"] .node-body').evaluateAll((els) => { const w = els.map((e) => Math.round(e.getBoundingClientRect().width)); return w.length === 13 && w.every((x) => x === w[0] && x > 250); }))] };
  });
// controller completes
await fac.page.goto(sessionUrl);
await fac.page.getByRole("button", { name: "Complete Burst…" }).click();
await fac.page.getByTestId("complete-confirm").waitFor();
await record(fac, { slug: "human-question-field-complete-confirm", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "QUESTION_GENERATION; completion requested but NOT committed", expected: "explicit confirmation; still ACTIVE; no frozen topology before commit", keyboard: false },
  async (page) => ({ projection: (await api(fac, `/workspaces/${WS}/sessions/${SID}/position`)).body.burst, checks: [
    check("still ACTIVE before commit", "ACTIVE", (await page.getByTestId("burst-state").textContent()).trim(), "projection"),
    check("no frozen set before commit", 0, await page.getByTestId("frozen-set").count()),
    check("confirmation says irreversible", true, (await page.getByTestId("complete-confirm").textContent()).includes("cannot be undone")),
  ] }));
await fac.page.getByTestId("complete-confirm-button").click();
await fac.page.getByTestId("session-state").filter({ hasText: /^QUESTION_CAPTURE$/ }).waitFor();
for (const [p, who] of [[fac, ID.facilitator.email], [own, ID.owner.email]]) {
  await p.page.goto(sessionUrl);
  await record(p, { slug: `frozen-question-field-${who.split("@")[0]}`, route: "/workspaces/[w]/sessions/[s]", identity: who, canonicalState: "QUESTION_CAPTURE; Burst COMPLETED; frozen set verified", expected: "core = frozen artifact (blue); frozen entries with authors, exact text; verification; no capture form; no editable control; establishedBy = CMD_COMPLETE_BURST" },
    async (page) => {
      const pos = await api(p, `/workspaces/${WS}/sessions/${SID}/position`); const frozen = pos.body.questionSet.frozen; const t = await topology(page);
      return { projection: { state: pos.body.session.state, verified: frozen?.verified, members: frozen?.memberCount, establishedBy: pos.body.establishedBy?.commandType }, checks: [
        check("core = frozen", "frozen", t.coreState),
        check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
        check("frozen texts = server (order, exact)", frozen.questions.map((q) => q.originalText), await page.getByTestId("frozen-question-text").evaluateAll((e) => e.map((x) => x.textContent)), "projection"),
        check("verified = server", String(frozen.verified), await page.getByTestId("frozen-set").getAttribute("data-verified"), "projection"),
        check("no capture form / no editable control in the artifact", 0, await page.locator('[data-testid="frozen-set"] input, [data-testid="frozen-set"] textarea, [data-testid="frozen-set"] button').count() + (await page.getByTestId("capture-form").count())),
        check("establishedBy = server", pos.body.establishedBy?.commandType ?? null, (await page.getByTestId("session-last-transition").textContent()).includes("CMD_COMPLETE_BURST") ? "CMD_COMPLETE_BURST" : null, "projection"),
      ] };
    });
}
await facM.page.goto(sessionUrl);
await facM.page.getByTestId("frozen-set").waitFor();
await record(facM, { slug: "frozen-question-field-phone", route: "/workspaces/[w]/sessions/[s]", identity: ID.owner.email, canonicalState: "QUESTION_CAPTURE frozen, Pixel 7", expected: "frozen artifact first in stack after core; proof reachable; no overflow" },
  async (page) => {
    const y = async (sel) => (await page.locator(sel).first().boundingBox())?.y ?? -1;
    const order = [await y('[data-testid="field-core"]'), await y('[data-testid="session-phases"]'), await y(".frozen-artifact"), await y('[data-plane="governance"]'), await y('[data-plane="proof"]')];
    const rows = await page.locator('[data-testid="session-phases"] .node-body').evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().width)));
    return { projection: (await api(fac, `/workspaces/${WS}/sessions/${SID}/position`)).body.questionSet, checks: [
      check("frozen set rendered, no capture form", [1, 0], [await page.getByTestId("frozen-set").count(), await page.getByTestId("capture-form").count()], "projection"),
      check("core = frozen", "frozen", (await topology(page)).coreState),
      check("effective topology stack", "stack", (await topology(page)).effectiveMode),
      check("stack order core → lifecycle → frozen artifact → governance → proof", true, order.every((v, i) => i === 0 || v > order[i - 1])),
      check("lifecycle rows uniform and full width (D3)", true, rows.length === 13 && rows.every((w) => w === rows[0] && w > 250)),
    ] };
  });

// ---------------------------------------------------------------- boundaries: denied, not found, rejected, loading
const out = await newPage(browser, "desktop");
await login(out, ID.outsider);
await record(out, { slug: "workspace-overview-empty-outsider", route: "/workspaces", identity: ID.outsider.email, canonicalState: "authenticated; member of nothing", expected: "empty state; founding still possible" },
  async (page) => ({ projection: { workspaces: (await api(out, "/workspaces")).body.workspaces.length }, checks: [check("empty state", 1, await page.getByTestId("workspaces-empty").count(), "projection"), check("founding node possible", 1, await page.locator('[data-testid="found-workspace-node"][data-node-state="possible"]').count())] }));
await out.page.goto(`${BASE}/workspaces/${WS}`);
await record(out, { slug: "boundary-denied-outsider", route: "/workspaces/[w]", identity: ID.outsider.email, canonicalState: "not a member -> server denies", expected: "DENIED boundary core (red), server reason, no protected content, logout kept" },
  async (page) => { const r = await api(out, `/workspaces/${WS}`); const t = await topology(page); return { projection: r.body, checks: [
    check("denied boundary", 1, await page.getByTestId("orientation-denied").count(), "projection"),
    check("reason = server", r.body.reasonCode, (await page.getByTestId("orientation-denied").textContent()).trim(), "projection"),
    check("no Workspace name leaked", 0, await page.getByText("SF-02 Inspection").count()),
    check("core = boundary", "boundary", t.coreState),
    check("logout reachable (identity exists)", 1, await page.getByTestId("logout-button").count()),
  ] }; }, { expectedHttp: [/^403 GET \/api\/workspaces\/[0-9a-f-]+(\/overview)?$/, /403 \(Forbidden\)/] });
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/00000000-0000-4000-8000-000000000000`);
await record(fac, { slug: "boundary-not-found", route: "/workspaces/[w]/challenges/[unknown]", identity: ID.facilitator.email, canonicalState: "unknown Challenge id in this Workspace", expected: "NOT FOUND boundary; trace reduced to access; no stale Challenge topology" },
  async (page) => ({ projection: (await api(fac, `/workspaces/${WS}/challenges/00000000-0000-4000-8000-000000000000`)).body, checks: [
    check("not_found boundary", "not_found", await page.getByTestId("load-failure").getAttribute("data-outcome"), "projection"),
    check("trace = access only", [["access", "established", "Workspaces"]], await traceData(page), "projection"),
    check("no session nodes", 0, await page.locator(".node").count()),
  ] }), { expectedHttp: [/^404 GET /, /404 \(Not Found\)/] });
await fac.page.goto(`${BASE}/workspaces/not-a-uuid`);
await record(fac, { slug: "boundary-rejected-malformed", route: "/workspaces/not-a-uuid", identity: ID.facilitator.email, canonicalState: "malformed id -> server rejects (input, not authority)", expected: "REJECTED boundary distinct from denied" },
  async (page) => ({ projection: (await api(fac, "/workspaces/not-a-uuid")).body, checks: [check("rejected boundary", 1, await page.getByTestId("orientation-rejected").count(), "projection")] }), { expectedHttp: [/^400 GET /, /400 \(Bad Request\)/] });
// loading with real latency (CDP)
const cdp = await fac.context.newCDPSession(fac.page);
await cdp.send("Network.enable");
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 2000, downloadThroughput: -1, uploadThroughput: -1 });
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`, { waitUntil: "commit" });
await fac.page.getByTestId("challenge-loading").waitFor({ timeout: 15000 });
const lt = await topology(fac.page);
const loadingTrace = await traceData(fac.page);
seq += 1;
const loadingShot = `${String(seq).padStart(2, "0")}-desktop-boundary-loading-latency-2s.png`;
await fac.page.screenshot({ path: join(SHOTS, loadingShot), fullPage: true });
results.push({ seq, screenshot: `screenshots/${loadingShot}`, url: `/workspaces/${WS}/challenges/${CH}`, route: "/workspaces/[w]/challenges/[c]", viewport: "desktop", reducedMotion: "no-preference", identity: ID.facilitator.email, canonicalState: "projection pending (2 s latency, CDP; no interception)", expectedRelation: "loading core (dashed), no nodes, no invented count; trace = access only", checks: [check("loading core", "loading", lt.coreState), check("no invented nodes", 0, lt.nodes.length), check("trace while loading", [["access", "established", "Workspaces"]], loadingTrace, "projection")], topology: lt, pass: lt.coreState === "loading" && lt.nodes.length === 0 && JSON.stringify(loadingTrace) === JSON.stringify([["access", "established", "Workspaces"]]) });
console.log(`${results.at(-1).pass ? "PASS" : "FAIL"} #${seq} desktop boundary-loading`);
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
// unknown consequence: real offline on a keyed command (Challenge page, Owner grant)
await own.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
await own.page.getByLabel("Grant session control to").waitFor();
await own.context.setOffline(true);
await own.page.getByLabel("Grant session control to").selectOption({ index: 1 });
await own.page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
await own.page.getByTestId("command-outcome").waitFor();
await record(own, { slug: "boundary-unknown-offline-mutation", route: "/workspaces/[w]/challenges/[c]", identity: ID.owner.email, canonicalState: "mutation sent while offline: consequence UNKNOWN", expected: "network_failure with unknown consequence; last-confirmed marker; topology unchanged; no success; re-read offered", keyboard: false, offline: true },
  async (page) => ({ projection: null, checks: [
    check("outcome network_failure / unknown / reconstruction failed", ["network_failure", "unknown", "failed"], [await page.getByTestId("command-outcome").getAttribute("data-outcome"), await page.getByTestId("command-outcome").getAttribute("data-consequence"), await page.getByTestId("command-outcome").getAttribute("data-reconstruction")]),
    check("no 'nothing changed' claim", false, /nothing (is assumed to have )?changed|no change was made/i.test(await page.getByTestId("command-outcome").textContent())),
    check("last-confirmed marker", 1, await page.getByTestId("projection-last-confirmed").count()),
    check("re-read offered", 1, await page.getByRole("button", { name: "Re-read current state" }).count()),
  ] }), { expectedHttp: [/./] });
await own.context.setOffline(false);
await own.page.getByRole("button", { name: "Re-read current state" }).click();
await own.page.getByTestId("command-outcome").filter({ has: own.page.locator('[data-reconstruction="done"]') }).waitFor().catch(() => {});

// ================================================================ SF-03 / doc 23 acceptance states
// 1–3, 8–9, 13–15: Challenge Field (PRIMARY) on a wide desktop — identity, breadcrumb, background, constellation, containment, reciprocity
{
  const facW = await newPage(browser, "wide");
  await login(facW, ID.facilitator);
  await facW.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
  await facW.page.getByTestId("field-core").waitFor();
  await facW.page.waitForTimeout(500);
  await record(facW, { slug: "challenge-field-wide-constellation", route: "/workspaces/[w]/challenges/[c]", identity: ID.facilitator.email, canonicalState: "Challenge with its Sessions; wide desktop 1600", expected: "centred NQIRY identity; symbiotic breadcrumb (text static, separators breathe); living background across the viewport; expanded spatial distribution; two-column instruments; text contained; no collisions" },
    async (page) => { const c = await containment(page); const rail = await railStable(page); const amb = await ambient(page); const action = await page.locator('.plane[data-plane="action"]').boundingBox(); const gov = await page.locator('.plane[data-plane="governance"]').boundingBox();
      return { projection: null, checks: [
        check("identity centred (px off centre ≤ 12)", true, (await identityCentred(page)) <= 12), check("identity is a link named nquiry", 1, await page.getByRole("link", { name: "nquiry" }).count()),
        check("breadcrumb text does not move", false, rail.textMoved), check("breadcrumb separators breathe (pseudo-element)", true, rail.separatorEnergy !== "none" && rail.separatorEnergy !== null), check("breadcrumb text itself has no animation/transform", ["none", "none"], [rail.textAnimation, rail.textTransform]), check("breadcrumb ≥ 13.5px", true, rail.minFont >= 13.5),
        check("background fixed and covering the viewport", [true, "fixed"], [amb.coversViewport, amb.fixed]), check("ambient motion present, ≥ 90 s cycles, non-interactive", true, amb.animated >= 2 && amb.minDurationS >= 9 && amb.pointer === "none"),
        check("two instrument columns; governance beside action", true, (await instrumentColumns(page)) === 2 && gov.x > action.x + action.width - 1),
        check("no text escapes its frame", [], c.escaping), check("no text below 11.5px", true, c.smallest >= 11.5), check("layout fits the box", "fits", c.fit), check("no two nodes overlap", 0, await nodeOverlaps(page)),
        check("topology uses ≥ 780px of width", true, c.box !== null && c.box[0] >= 780),
      ] }; });
  // 15: reciprocity by keyboard — presentation only
  const stage = facW.page.getByTestId("field-stage");
  const grant = facW.page.getByRole("button", { name: "Grant session control for this Challenge" });
  const hasGrant = (await grant.count()) === 1;
  const plane = facW.page.locator('.plane[data-plane="governance"]');
  const resting = await plane.evaluate((el) => getComputedStyle(el).borderTopColor);
  // the facilitator holds no grant capability: the governance instrument's proof disclosure (a focusable summary)
  // is the keyboard entry into the governance relation
  if (hasGrant) await grant.focus(); else await facW.page.getByTestId("challenge-authority-proof").locator("summary").focus();
  await facW.page.waitForTimeout(300);
  const active = await stage.getAttribute("data-active-relation");
  const responding = await plane.evaluate((el) => getComputedStyle(el).borderTopColor);
  await record(facW, { slug: "reciprocity-keyboard-focus-governance", route: "/workspaces/[w]/challenges/[c]", identity: ID.facilitator.email, canonicalState: "same projection; keyboard focus inside the governance relation", expected: "the governance instrument and its nodes/paths respond; nothing else changes (no state, no capability, no request)", keyboard: false },
    async (page) => ({ projection: null, checks: [check("stage names the focused relation", "governance", active), check("governance instrument responds (border colour changes)", true, responding !== resting), check("unavailable relation unchanged", (await api(facW, `/workspaces/${WS}/challenges/${CH}`)).body.capabilities.openSession.available ? "possible" : "unavailable", await page.getByTestId("new-session-node").getAttribute("data-node-state"), "projection"), check("no outcome appeared", 0, await page.getByTestId("command-outcome").count())] }));
  await facW.page.evaluate(() => document.activeElement?.blur());
  await facW.context.close();
}
// 4, 6, 12–14: Workspace Field and Session Field (frozen) on the wide desktop; reduced-motion depth
for (const [slug, url, who, expected] of [
  ["workspace-field-wide-legibility", `/workspaces/${WS}`, ID.owner, "Workspace Field: member and challenge nodes readable (≥ 12.8px sm / 13.8px md), frames follow content, no collisions, breathing room"],
  ["session-field-wide-frozen", `/workspaces/${WS}/sessions/${SID}`, ID.facilitator, "Session Field (frozen): lifecycle labels readable, participants/controller on the outer ring, frozen instrument first, governance/proof beside"],
]) {
  const w = await newPage(browser, "wide");
  await login(w, who);
  await w.page.goto(`${BASE}${url}`);
  await w.page.getByTestId("field-core").waitFor();
  await w.page.waitForTimeout(500);
  await record(w, { slug, route: url.replace(WS, "[w]").replace(SID ?? "—", "[s]"), identity: who.email, canonicalState: "wide desktop 1600", expected },
    async (page) => { const c = await containment(page); const labels = await page.locator(".node .node-label").evaluateAll((els) => els.map((e) => ({ fs: parseFloat(getComputedStyle(e).fontSize), hidden: e.classList.contains("visually-hidden"), w: e.getBoundingClientRect().width })));
      return { projection: null, checks: [check("no text escapes its frame", [], c.escaping), check("no text below 11.5px", true, c.smallest >= 11.5), check("every node label visible and ≥ 12.5px", true, labels.every((l) => !l.hidden && l.w > 0 && l.fs >= 12.5)), check("layout fits", "fits", c.fit), check("no two nodes overlap", 0, await nodeOverlaps(page)), check("identity centred", true, (await identityCentred(page)) <= 12)] }; });
  await w.context.close();
}
{
  const r = await newPage(browser, "desktop", { reducedMotion: "reduce" });
  await login(r, ID.facilitator);
  await r.page.goto(`${BASE}/workspaces/${WS}/sessions/${SID}`);
  await r.page.getByTestId("field-core").waitFor();
  await record(r, { slug: "session-field-reduced-motion-depth", route: "/workspaces/[w]/sessions/[s]", identity: ID.facilitator.email, canonicalState: "QUESTION_CAPTURE frozen; prefers-reduced-motion: reduce", expected: "every animation off (background, rail, core, paths, nodes); every ambient layer still present (depth without motion); meaning unchanged" },
    async (page) => { const amb = await ambient(page); const rail = await railStable(page); const t = await topology(page); return { projection: null, checks: [check("no ambient animation", 0, amb.animated), check("ambient layers still shown", true, amb.layersShown >= 2), check("rail separators static", "none", rail.separatorEnergy), check("core animation none", "none", t.coreAnimation), check("frozen core still frozen", "frozen", t.coreState)] }; });
  await r.context.close();
}
// 12–14: STRESS Workspace/Challenge (long labels), desktop 1280 + wide + phone
if (STRESS_WS && STRESS_CH) {
  for (const [vp, who, url, slug] of [
    ["desktop", ID.facilitator, `/workspaces/${STRESS_WS}/challenges/${STRESS_CH}`, "stress-challenge-long-labels-desktop"],
    ["wide", ID.facilitator, `/workspaces/${STRESS_WS}/challenges/${STRESS_CH}`, "stress-challenge-long-labels-wide"],
    ["desktop", ID.owner, `/workspaces/${STRESS_WS}`, "stress-workspace-long-name-desktop"],
    ["pixel-7", ID.facilitator, `/workspaces/${STRESS_WS}/challenges/${STRESS_CH}`, "stress-challenge-long-labels-phone"],
  ]) {
    const s = await newPage(browser, vp);
    await login(s, who);
    await s.page.goto(`${BASE}${url}`);
    await s.page.getByTestId("field-core").waitFor();
    await s.page.waitForTimeout(500);
    await record(s, { slug, route: url.replace(STRESS_WS, "[w]").replace(STRESS_CH, "[c]"), identity: who.email, canonicalState: `stress content (104-char Workspace name, 150-char Challenge title) on ${vp}`, expected: "text stays inside every frame; frames follow content; no collisions; nothing below 11.5px; phone rows full width" },
      async (page) => { const c = await containment(page); const title = await page.getByTestId("field-core").getByRole("heading", { level: 1 }).evaluate((el) => ({ text: el.textContent.trim(), clipped: el.scrollHeight > el.clientHeight + 2 })); const rows = vp === "pixel-7" ? await page.locator('[data-testid="sessions-list"] .node-body, [data-testid="challenges-list"] .node-body').evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().width))) : null;
        return { projection: null, checks: [check("no text escapes its frame", [], c.escaping), check("no text below 11.5px", true, c.smallest >= 11.5), check("no two nodes overlap", 0, await nodeOverlaps(page)), check("core title complete and unclipped", false, title.clipped), ...(vp === "pixel-7" ? [check("phone rows full width", true, rows.length > 0 && rows.every((w) => w > 250))] : [check("fits or compacted to the stack (never overflow)", true, c.fit === "fits" || c.fit === "stack")])] }; });
    await s.context.close();
  }
}

await browser.close();
writeFileSync(join(ROOT, "results.json"), JSON.stringify({ base: BASE, workspace: WS, challenge: CH, session: SID, generatedAt: new Date().toISOString(), results }, null, 2));
const rows = results.map((r) => `| ${r.seq} | [${r.screenshot.split("/")[1]}](${r.screenshot}) | \`${r.route}\` | ${r.viewport}${r.reducedMotion === "reduce" ? " (reduced motion)" : ""} | ${r.canonicalState} | ${r.identity} | ${r.expectedRelation} | ${(r.checks ?? []).filter((c) => !c.pass).map((c) => `FAILED: ${c.claim} (expected ${JSON.stringify(c.expected)}, got ${JSON.stringify(c.actual)})`).join("; ") || `${(r.checks ?? []).length} checks met; topology ${r.topology?.mode ?? "n/a"}/${r.topology?.coreState ?? "n/a"}; axe s/c ${r.axeSeriousCritical?.length ?? "n/a"}; overflow ${r.overflowPx ?? "n/a"}px; unexpected HTTP ${r.unexpectedHttp?.length ?? "n/a"}`} | ${r.pass ? "PASS" : "FAIL"} |`);
writeFileSync(join(ROOT, "MANIFEST.md"), `# SF-03 browser evidence manifest (${RUN}; generated by harness/review-harness.mjs)\n\nBase: ${BASE} · Workspace \`${WS}\` · Challenge \`${CH}\` · Session \`${SID}\`\n\n| # | Screenshot | Route | Viewport | Canonical state (server projection) | Identity | Expected relation | Observed | Result |\n|---|---|---|---|---|---|---|---|---|\n${rows.join("\n")}\n\nFull per-state data (projection, checks, topology, console, network, statics, axe, keyboard walk, redirect chain): \`results.json\`.\n`);
console.log(`done: ${results.filter((r) => r.pass).length}/${results.length} PASS`);
