/**
 * SF-01 visible-website review harness (evidence tool; not a product test).
 *
 * Drives a REAL Chromium against the running isolated inspection runtime
 * (compose project `nquiry-sf01-inspect`, http://127.0.0.1:13100) and records,
 * for every reviewed state: URL, identity, viewport, canonical state from the
 * server projection, expected vs visible affordances, console messages, page
 * errors, failed / 4xx / 5xx requests, `_next/static` results, axe WCAG 2 A/AA,
 * horizontal overflow, keyboard focus walk and redirect chain. No network
 * interception is used. Session progression is driven through the real UI.
 *
 * Usage (from the worktree root, with the inspection runtime up):
 *   node docs/implementation/field-reports/SF-01/review/browser-evidence-2026-09-25/harness/review-harness.mjs \
 *     <workspaceId> <challengeId>
 * The harness opens its own fresh Session through the SF-01 "Open Session" relation in the UI.
 * Output: ../screenshots/*.png, ../results/results.json, ../MANIFEST.md
 *   (or, with EVIDENCE_RUN=<name>: ../<name>/screenshots, ../<name>/results.json, ../<name>/MANIFEST.md,
 *   so an earlier run's evidence is never overwritten).
 * Aborted Next.js link prefetches (`?_rsc=` + net::ERR_ABORTED, cancelled by a navigation) are
 * recorded separately as `prefetchAborted` and are not failures; any COMPLETED prefetch that is
 * not 2xx still appears in http4xx5xx and fails the state.
 */
import { chromium, devices } from "@playwright/test";
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");
const BASE = "http://127.0.0.1:13100";
const API = `${BASE}/api`;
const EVIDENCE = join(dirname(fileURLToPath(import.meta.url)), "..");
const RUN = process.env.EVIDENCE_RUN ?? "";
const ROOT = RUN ? join(EVIDENCE, RUN) : EVIDENCE;
const SHOTS = join(ROOT, "screenshots");
const RESULTS = RUN ? join(ROOT, "results.json") : join(ROOT, "results", "results.json");
mkdirSync(SHOTS, { recursive: true });
mkdirSync(dirname(RESULTS), { recursive: true });

const [WS, CH] = process.argv.slice(2);
if (!WS || !CH) throw new Error("usage: review-harness.mjs <workspaceId> <challengeId>");
let SID = null;

const ID = {
  owner: { email: "owner@inspect.local.test", password: "inspect-owner-2026", name: "Inspect Owner" },
  facilitator: { email: "facilitator@inspect.local.test", password: "inspect-fac-2026", name: "Inspect Facilitator" },
  outsider: { email: "outsider@inspect.local.test", password: "inspect-outsider-2026", name: "Inspect Outsider" },
};
const VIEWPORTS = {
  desktop: { viewport: { width: 1280, height: 860 } },
  "pixel-7": { ...devices["Pixel 7"] },
};

const results = [];
let seq = 0;

async function newPage(browser, viewportName) {
  const context = await browser.newContext(VIEWPORTS[viewportName]);
  const page = await context.newPage();
  const log = { console: [], pageErrors: [], failed: [], prefetchAborted: [], http4xx5xx: [], statics: [], nav: [] };
  page.on("console", (m) => {
    if (m.type() === "error" || m.type() === "warning") log.console.push(`${m.type()}: ${m.text()}`);
  });
  page.on("pageerror", (e) => log.pageErrors.push(String(e)));
  page.on("requestfailed", (r) => {
    const line = `${r.method()} ${r.url().replace(BASE, "")} :: ${r.failure()?.errorText}`;
    if (r.url().includes("_rsc=") && r.failure()?.errorText === "net::ERR_ABORTED") log.prefetchAborted.push(line);
    else log.failed.push(line);
  });
  page.on("response", (r) => {
    const u = r.url();
    if (u.includes("/_next/static/")) log.statics.push({ url: u.replace(BASE, ""), status: r.status() });
    if (r.status() >= 400) log.http4xx5xx.push(`${r.status()} ${r.request().method()} ${u.replace(BASE, "")}`);
  });
  page.on("framenavigated", (f) => {
    if (f === page.mainFrame()) log.nav.push(f.url().replace(BASE, ""));
  });
  return { context, page, log, viewportName };
}

function resetLog(log) {
  for (const k of Object.keys(log)) log[k].length = 0;
}

async function login(p, who) {
  resetLog(p.log);
  await p.page.goto(`${BASE}/login`);
  await p.page.getByLabel("Email").fill(who.email);
  await p.page.getByLabel("Password").fill(who.password);
  await p.page.getByRole("button", { name: "Log in" }).click();
  await p.page.waitForURL(/\/workspaces$/);
  await p.page.waitForLoadState("networkidle");
  return [...p.log.nav];
}

async function api(p, path) {
  const r = await p.page.request.get(`${API}${path}`);
  let body = null;
  try {
    body = await r.json();
  } catch {
    body = null;
  }
  return { status: r.status(), body };
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    // @ts-ignore injected
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] } });
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }));
  });
}

async function focusWalk(page, maxTabs = 25) {
  await page.evaluate(() => {
    if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
    window.scrollTo(0, 0);
  });
  const steps = [];
  for (let i = 0; i < maxTabs; i++) {
    await page.keyboard.press("Tab");
    const s = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const cs = getComputedStyle(el);
      const outline = cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0;
      const name = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("name") || el.id || "").trim().replace(/\s+/g, " ").slice(0, 60);
      return { tag: el.tagName.toLowerCase(), name, visibleFocus: outline || cs.boxShadow !== "none" };
    });
    if (s === null) break;
    const key = `${s.tag}|${s.name}`;
    if (steps.length && steps[0].key === key && i > 0) break; // wrapped around
    steps.push({ key, ...s });
  }
  return {
    reachable: steps.length,
    withoutVisibleFocus: steps.filter((s) => !s.visibleFocus).map((s) => `${s.tag}:${s.name}`),
    order: steps.map((s) => `${s.tag}:${s.name}`),
  };
}

async function overflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
}

async function cssLoaded(page) {
  return page.evaluate(() => ({
    stylesheets: [...document.styleSheets].map((s) => s.href?.replace(location.origin, "") ?? "inline"),
    tokenAccent: getComputedStyle(document.documentElement).getPropertyValue("--accent").trim(),
    bodyBackground: getComputedStyle(document.body).backgroundColor,
  }));
}

/** Records one reviewed state. `verify(page)` returns {projection, visible, checks:[{claim, expected, actual, pass}]} */
async function record(p, meta, verify, { expectedHttp = [] } = {}) {
  const { page, log, viewportName } = p;
  await page.waitForLoadState("networkidle");
  seq += 1;
  const file = `${String(seq).padStart(2, "0")}-${viewportName}-${meta.slug}.png`;
  const v = verify ? await verify(page) : { projection: null, checks: [] };
  await page.screenshot({ path: join(SHOTS, file), fullPage: true });
  const axeViolations = await axe(page);
  const focus = meta.keyboard === false ? null : await focusWalk(page);
  const entry = {
    seq,
    screenshot: `screenshots/${file}`,
    url: page.url().replace(BASE, ""),
    route: meta.route,
    viewport: viewportName,
    identity: meta.identity,
    canonicalState: meta.canonicalState,
    expectedRelation: meta.expected,
    projection: v.projection,
    checks: v.checks,
    redirectChain: meta.redirectChain ?? [...log.nav],
    console: [...log.console],
    pageErrors: [...log.pageErrors],
    failedRequests: [...log.failed],
    prefetchAborted: [...log.prefetchAborted],
    http4xx5xx: [...log.http4xx5xx],
    unexpectedHttp: log.http4xx5xx.filter((h) => !expectedHttp.some((re) => re.test(h))),
    staticRequests: log.statics.length,
    staticNon200: log.statics.filter((s) => s.status !== 200 && s.status !== 304),
    css: await cssLoaded(page),
    overflowPx: await overflow(page),
    axeSeriousCritical: axeViolations.filter((x) => x.impact === "serious" || x.impact === "critical"),
    axeOther: axeViolations.filter((x) => x.impact !== "serious" && x.impact !== "critical"),
    keyboard: focus,
    localTruthDetected: v.checks.some((c) => c.kind === "projection" && !c.pass),
  };
  entry.pass =
    v.checks.every((c) => c.pass) &&
    entry.pageErrors.length === 0 &&
    entry.failedRequests.length === 0 &&
    entry.unexpectedHttp.length === 0 &&
    entry.staticNon200.length === 0 &&
    entry.overflowPx <= 1 &&
    entry.axeSeriousCritical.length === 0 &&
    entry.console.filter((c) => c.startsWith("error")).every((c) => expectedHttp.some((re) => re.test(c))) &&
    (entry.keyboard === null || entry.keyboard.withoutVisibleFocus.length === 0);
  results.push(entry);
  resetLog(log);
  console.log(`${entry.pass ? "PASS" : "FAIL"} #${seq} ${viewportName} ${meta.slug}`);
  return entry;
}

const check = (claim, expected, actual, kind = "visible") => ({
  claim,
  kind,
  expected,
  actual,
  pass: JSON.stringify(expected) === JSON.stringify(actual),
});
const texts = (loc) => loc.evaluateAll((els) => els.map((e) => (e.textContent ?? "").replace(/\s+/g, " ").trim()));
const traceData = (page) =>
  page
    .getByRole("navigation", { name: "Inquiry position" })
    .getByRole("listitem")
    .evaluateAll((lis) =>
      lis.map((li) => [li.dataset.coordinate, li.dataset.status, (li.querySelector("a, .trace-label")?.textContent ?? "").trim()]),
    );

const browser = await chromium.launch();

// ---------------------------------------------------------------- anonymous
for (const vp of ["desktop", "pixel-7"]) {
  const a = await newPage(browser, vp);
  await a.page.goto(`${BASE}/`);
  await a.page.waitForURL(/\/login$/);
  await record(
    a,
    {
      slug: "login-anonymous",
      route: "/ -> /login",
      identity: "anonymous",
      canonicalState: "no NQUIRY session (GET /auth/me -> 401 denied)",
      expected: "root redirects an anonymous visitor to /login; login form with Email, Password, Log in",
    },
    async (page) => {
      const me = await api(a, "/auth/me");
      return {
        projection: { authMe: me },
        checks: [
          check("server says: no session", 401, me.status, "projection"),
          check("redirect ends at /login", "/login", new URL(page.url()).pathname),
          check("form fields", ["Email", "Password"], await texts(page.locator("form label"))),
          check("submit control present", 1, await page.getByRole("button", { name: "Log in" }).count()),
          check("login uses a layout container (shell/field/button classes)", true, (await page.locator("main.shell-main, main .field, main .button").count()) > 0, "style"),
        ],
      };
    },
    { expectedHttp: [/^401 GET \/api\/auth\/me$/, /401 \(Unauthorized\)/] },
  );
  await a.context.close();
}

// ---------------------------------------------------------------- owner: landing, workspace, challenge
const ownerPages = {};
for (const vp of ["desktop", "pixel-7"]) {
  const o = await newPage(browser, vp);
  ownerPages[vp] = o;
  const chain = await login(o, ID.owner);
  await record(
    o,
    {
      slug: "landing-owner",
      route: "/login -> / -> /workspaces",
      identity: ID.owner.email,
      canonicalState: "authenticated; member of SF-01 Inspection",
      expected: "after login: redirect to /workspaces; list shows exactly the server's accessible Workspaces; access-context trace only",
      redirectChain: chain,
    },
    async (page) => {
      const me = await api(o, "/auth/me");
      const ws = await api(o, "/workspaces");
      const names = ws.body.workspaces.map((w) => w.name);
      return {
        projection: { authMe: me.body, workspaces: names },
        checks: [
          check("session resolves to a user", "ok", me.body.kind, "projection"),
          check("visible Workspaces = server list", names, await texts(page.getByTestId("workspaces-list").getByRole("link")), "projection"),
          check("trace = access context only", [["access", "current", "Workspaces"]], await traceData(page), "projection"),
          check("redirect chain passes / and ends at /workspaces", true, chain.includes("/") && chain[chain.length - 1] === "/workspaces"),
        ],
      };
    },
  );
  await o.page.goto(`${BASE}/workspaces/${WS}`);
  await record(
    o,
    {
      slug: "workspace-owner",
      route: "/workspaces/[w]",
      identity: ID.owner.email,
      canonicalState: "Workspace SF-01 Inspection; viewer = governance root (Owner), not Facilitator",
      expected: "Challenge relation visible but unavailable with the server reason; Add member offered (governance-capable); Challenges listed from the server",
    },
    async (page) => {
      const ov = await api(o, `/workspaces/${WS}/overview`);
      const cc = ov.body.capabilities.createChallenge;
      return {
        projection: { createChallenge: cc, challenges: ov.body.challenges.map((c) => c.title), role: ov.body.viewer.role },
        checks: [
          check("Challenges = server list", ov.body.challenges.map((c) => c.title), await texts(page.getByTestId("challenges-list").getByRole("link")), "projection"),
          check("create-challenge form iff capability available", cc.available, (await page.getByTestId("create-challenge-form").count()) === 1, "projection"),
          check("unavailable reason = server reason", cc.available ? null : cc.reason, cc.available ? null : (await page.getByTestId("challenge-create-unavailable").textContent()).trim(), "projection"),
          check("trace challenge relation status", cc.available ? "possible" : "unavailable", await page.locator('[data-coordinate="challenge"]').getAttribute("data-status"), "projection"),
          check("add-member form (governance root)", true, (await page.getByTestId("add-member-form").count()) === 1),
        ],
      };
    },
  );
  await o.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
  await record(
    o,
    {
      slug: "challenge-owner",
      route: "/workspaces/[w]/challenges/[c]",
      identity: ID.owner.email,
      canonicalState: "Challenge framed; 1 Session DRAFT; Owner holds no Challenge-scoped Session control",
      expected: "New Session relation unavailable with server reason; Governance grant form offered; authority proof closed by default",
    },
    async (page) => {
      const d = await api(o, `/workspaces/${WS}/challenges/${CH}`);
      const os = d.body.capabilities.openSession;
      return {
        projection: { openSession: os, sessions: d.body.sessions.map((s) => s.state), grant: d.body.capabilities.grantSessionControl.available },
        checks: [
          check("trace", [["access", "established", "Workspaces"], ["workspace", "established", "SF-01 Inspection"], ["challenge", "current", d.body.challenge.title], ["session", os.available ? "possible" : "unavailable", "New Session"]], await traceData(page), "projection"),
          check("Session states = server", d.body.sessions.map((s) => s.state), await texts(page.getByTestId("sessions-list").locator('[data-origin="system-state"] .state')), "projection"),
          check("Open Session control iff capability", os.available, (await page.getByRole("button", { name: "Open Session" }).count()) === 1, "projection"),
          check("grant form iff capability", d.body.capabilities.grantSessionControl.available, (await page.getByLabel("Grant session control to").count()) === 1, "projection"),
          check("proof closed by default", null, await page.getByTestId("challenge-authority-proof").getAttribute("open")),
        ],
      };
    },
  );
}

// ---------------------------------------------------------------- facilitator: primary SF-01 surface
const fac = await newPage(browser, "desktop");
await login(fac, ID.facilitator);
await fac.page.goto(`${BASE}/workspaces/${WS}`);
await record(
  fac,
  {
    slug: "workspace-facilitator",
    route: "/workspaces/[w]",
    identity: ID.facilitator.email,
    canonicalState: "Workspace; viewer = Facilitator (not governance root)",
    expected: "Frame-a-Challenge form offered (server capability); no Add member form",
  },
  async (page) => {
    const ov = await api(fac, `/workspaces/${WS}/overview`);
    return {
      projection: { createChallenge: ov.body.capabilities.createChallenge },
      checks: [
        check("create-challenge form iff capability", ov.body.capabilities.createChallenge.available, (await page.getByTestId("create-challenge-form").count()) === 1, "projection"),
        check("no add-member form", 0, await page.getByTestId("add-member-form").count()),
      ],
    };
  },
);
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
await record(
  fac,
  {
    slug: "challenge-facilitator-PRIMARY",
    route: "/workspaces/[w]/challenges/[c]",
    identity: ID.facilitator.email,
    canonicalState: "Challenge; Facilitator holds SESSION_CONTROL_RIGHT at CHALLENGE:<c>; 1 Session DRAFT",
    expected: "PRIMARY SF-01 SURFACE: trace Workspaces → SF-01 Inspection → Challenge (current) → New Session (possible); Open Session offered; Sessions named by server projection; authority proof depth",
  },
  async (page) => {
    const d = await api(fac, `/workspaces/${WS}/challenges/${CH}`);
    return {
      projection: { openSession: d.body.capabilities.openSession, controllers: d.body.sessionControllers.map((b) => b.holderName) },
      checks: [
        check("trace", [["access", "established", "Workspaces"], ["workspace", "established", "SF-01 Inspection"], ["challenge", "current", d.body.challenge.title], ["session", "possible", "New Session"]], await traceData(page), "projection"),
        check("Open Session offered", true, (await page.getByRole("button", { name: "Open Session" }).count()) === 1, "projection"),
        check("no client ordinal", 0, await page.getByText(/^Session \d+$/).count()),
      ],
    };
  },
);
await fac.page.getByTestId("challenge-authority-proof").locator("summary").focus();
await fac.page.keyboard.press("Enter");
await record(
  fac,
  {
    slug: "challenge-facilitator-proof-open",
    route: "/workspaces/[w]/challenges/[c]",
    identity: ID.facilitator.email,
    canonicalState: "same, D2 authority proof opened by keyboard",
    expected: "proof opens in place; lists the server's Session controllers with grantor and scope; position kept",
    keyboard: false,
  },
  async (page) => {
    const d = await api(fac, `/workspaces/${WS}/challenges/${CH}`);
    const names = d.body.sessionControllers.map((b) => b.holderName);
    return {
      projection: { controllers: names },
      checks: [
        check("proof open", "", await page.getByTestId("challenge-authority-proof").getAttribute("open")),
        check("controllers = server", names.length, await page.getByTestId("challenge-authority-list").getByRole("listitem").count(), "projection"),
        check("focus stays on summary", "summary", await page.evaluate(() => document.activeElement?.tagName.toLowerCase())),
      ],
    };
  },
);
// mobile primary surface
const facM = await newPage(browser, "pixel-7");
await login(facM, ID.facilitator);
await facM.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
await record(
  facM,
  {
    slug: "challenge-facilitator-PRIMARY",
    route: "/workspaces/[w]/challenges/[c]",
    identity: ID.facilitator.email,
    canonicalState: "same as desktop primary surface",
    expected: "relational order on phone: position → Challenge → Sessions → Open Session → proof; no overflow",
  },
  async (page) => {
    const y = async (sel) => (await page.locator(sel).first().boundingBox())?.y ?? -1;
    const order = [await y('nav[aria-label="Inquiry position"]'), await y("h1"), await y('[data-field-zone="centre"]'), await y('[data-field-zone="near"]'), await y('[data-field-zone="depth"]')];
    return {
      projection: null,
      checks: [check("vertical relational order", true, order.every((v, i) => i === 0 || v > order[i - 1]))],
    };
  },
);

// ---------------------------------------------------------------- SF-01 effect relation in the real UI: Open Session
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`);
await fac.page.getByRole("button", { name: "Open Session" }).click();
await fac.page.waitForURL(/\/sessions\/[0-9a-f-]{36}$/);
SID = fac.page.url().split("/sessions/")[1];
const sessionUrl = `${BASE}/workspaces/${WS}/sessions/${SID}`;
await fac.page.getByTestId("session-state").filter({ hasText: "DRAFT" }).waitFor();
await record(
  fac,
  {
    slug: "session-draft-facilitator",
    route: "/workspaces/[w]/sessions/[s]",
    identity: ID.facilitator.email,
    canonicalState: "Session DRAFT; Facilitator has NO SESSION-scoped control yet (HD-1)",
    expected: "Begin setup visible only as unavailable with the server reason (no disabled control)",
  },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`);
    return {
      projection: { state: pos.body.session.state, beginSetup: pos.body.actions.BEGIN_SETUP },
      checks: [
        check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
        check("Begin setup control iff capability", pos.body.actions.BEGIN_SETUP.available, (await page.getByRole("button", { name: "Begin setup" }).count()) === 1, "projection"),
      ],
    };
  },
);
// owner grants SESSION-scoped control through the UI
const own = ownerPages.desktop;
await own.page.goto(sessionUrl);
await own.page.getByTestId("session-state").waitFor();
for (let attempt = 0; attempt < 10; attempt++) {
  await own.page.getByLabel("Grant session control to").selectOption({ label: "Inspect Facilitator" });
  if (await own.page.getByRole("button", { name: "Grant session control for this Session" }).isEnabled()) break;
  await own.page.waitForTimeout(300);
}
await own.page.getByRole("button", { name: "Grant session control for this Session" }).click();
await own.page.getByTestId("session-authority-provenance").getByText("Inspect Facilitator").waitFor();
// facilitator walks the lawful path through the UI
await fac.page.goto(sessionUrl);
// Wait on the canonical state each step must produce (never on a possibly stale outcome element).
for (const [label, produced] of [
  ["Begin setup", () => fac.page.getByTestId("session-state").filter({ hasText: /^SETUP$/ }).waitFor()],
  ["Begin challenge capture", () => fac.page.getByTestId("session-state").filter({ hasText: /^CHALLENGE_CAPTURE$/ }).waitFor()],
  ["Prepare protected Burst", () => fac.page.getByTestId("burst-state").filter({ hasText: /^PREPARED$/ }).waitFor()],
]) {
  await fac.page.getByRole("button", { name: label }).click();
  await produced();
  await fac.page.waitForLoadState("networkidle");
}
for (const who of ["Inspect Facilitator", "Inspect Owner"]) {
  // Same retry as the F03 real-stack spec: a selection made while a prior Command is still
  // settling is reset by the page's own post-commit setParticipant("") (observation O-1).
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
await fac.page.getByTestId("burst-state").filter({ hasText: "ACTIVE" }).waitFor();
await fac.page.getByLabel("Your question", { exact: true }).fill("Which step do most new users abandon first?");
await fac.page.getByRole("button", { name: "Submit question" }).click();
await fac.page.getByTestId("own-question").first().waitFor();
await record(
  fac,
  {
    slug: "session-question-generation-controller-participant",
    route: "/workspaces/[w]/sessions/[s]",
    identity: ID.facilitator.email,
    canonicalState: "Session QUESTION_GENERATION; Burst ACTIVE HUMAN_ONLY; viewer = controller + participant",
    expected: "capture form; own questions only (HD-13); presentation-only timer; Complete Burst offered to controller",
    keyboard: true,
  },
  async (page) => {
    const pos = await api(fac, `/workspaces/${WS}/sessions/${SID}/position`);
    return {
      projection: { state: pos.body.session.state, burst: pos.body.burst?.state, visibility: pos.body.questionSet.visibility, mine: pos.body.questionSet.mine.length, complete: pos.body.actions.COMPLETE_BURST },
      checks: [
        check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
        check("burst = server", pos.body.burst.state, (await page.getByTestId("burst-state").textContent()).trim(), "projection"),
        check("own questions = server mine", pos.body.questionSet.mine.length, await page.getByTestId("own-question").count(), "projection"),
        check("capture form iff capability", pos.body.actions.CAPTURE_QUESTION.available, (await page.getByTestId("capture-form").count()) === 1, "projection"),
        check("Complete Burst iff capability", pos.body.actions.COMPLETE_BURST.available, (await page.getByRole("button", { name: /Complete Burst/ }).count()) === 1, "projection"),
        check("no BEGIN_ANALYSIS anywhere", 0, await page.getByText(/begin analysis/i).count()),
      ],
    };
  },
);
// owner as participant: own-only view
await own.page.goto(sessionUrl);
await own.page.getByLabel("Your question", { exact: true }).fill("What did users expect to happen after signup?");
await own.page.getByRole("button", { name: "Submit question" }).click();
await own.page.getByTestId("own-question").first().waitFor();
await record(
  own,
  {
    slug: "session-question-generation-owner-participant",
    route: "/workspaces/[w]/sessions/[s]",
    identity: ID.owner.email,
    canonicalState: "QUESTION_GENERATION; Owner = participant, not Session controller",
    expected: "sees only own question (HD-13), no Complete Burst",
  },
  async (page) => {
    const pos = await api(own, `/workspaces/${WS}/sessions/${SID}/position`);
    return {
      projection: { visibility: pos.body.questionSet.visibility, mine: pos.body.questionSet.mine.map((q) => q.originalText) },
      checks: [
        check("own questions = server mine (exact text)", pos.body.questionSet.mine.map((q) => q.originalText), await page.getByTestId("own-question-text").evaluateAll((e) => e.map((x) => x.textContent)), "projection"),
        check("no Complete Burst", 0, await page.getByRole("button", { name: /Complete Burst/ }).count()),
        check("peer question not visible", 0, await page.getByText("Which step do most new users abandon first?").count()),
      ],
    };
  },
);
// controller completes the Burst manually
await fac.page.goto(sessionUrl);
await fac.page.getByRole("button", { name: "Complete Burst…" }).click();
await fac.page.getByTestId("complete-confirm-button").click();
await fac.page.getByTestId("session-state").filter({ hasText: "QUESTION_CAPTURE" }).waitFor();
for (const [p, who] of [[fac, ID.facilitator.email], [own, ID.owner.email]]) {
  await p.page.goto(sessionUrl);
  await record(
    p,
    {
      slug: `session-question-capture-frozen-${who.split("@")[0]}`,
      route: "/workspaces/[w]/sessions/[s]",
      identity: who,
      canonicalState: "Session QUESTION_CAPTURE; Burst COMPLETED; frozen human set (fingerprint verified)",
      expected: "frozen set for every member with authors; no capture form; no Complete Burst; no BEGIN_ANALYSIS",
    },
    async (page) => {
      const pos = await api(p, `/workspaces/${WS}/sessions/${SID}/position`);
      const frozen = pos.body.questionSet.frozen;
      return {
        projection: { state: pos.body.session.state, burst: pos.body.burst.state, verified: frozen?.verified, members: frozen?.memberCount },
        checks: [
          check("state = server", pos.body.session.state, (await page.getByTestId("session-state").textContent()).trim(), "projection"),
          check("frozen texts = server (order, exact)", frozen.questions.map((q) => q.originalText), await page.getByTestId("frozen-question-text").evaluateAll((e) => e.map((x) => x.textContent)), "projection"),
          check("verified flag = server", String(frozen.verified), await page.getByTestId("frozen-set").getAttribute("data-verified"), "projection"),
          check("no capture form", 0, await page.getByTestId("capture-form").count()),
          check("no BEGIN_ANALYSIS", 0, await page.getByText(/begin analysis/i).count()),
        ],
      };
    },
  );
}
const ownM = ownerPages["pixel-7"];
await ownM.page.goto(sessionUrl);
await record(
  ownM,
  {
    slug: "session-question-capture-frozen-owner",
    route: "/workspaces/[w]/sessions/[s]",
    identity: ID.owner.email,
    canonicalState: "QUESTION_CAPTURE, frozen set",
    expected: "frozen set readable on phone; no overflow",
  },
  async () => ({ projection: null, checks: [] }),
);

// ---------------------------------------------------------------- empty / error / loading states
const out = await newPage(browser, "desktop");
await login(out, ID.outsider);
await record(
  out,
  {
    slug: "landing-outsider-empty",
    route: "/workspaces",
    identity: ID.outsider.email,
    canonicalState: "authenticated; member of nothing",
    expected: "empty state (no Workspaces), founding offered",
  },
  async (page) => {
    const ws = await api(out, "/workspaces");
    return { projection: { workspaces: ws.body.workspaces.length }, checks: [check("empty state visible", 1, await page.getByTestId("workspaces-empty").count(), "projection")] };
  },
);
await out.page.goto(`${BASE}/workspaces/${WS}`);
await record(
  out,
  {
    slug: "workspace-outsider-denied",
    route: "/workspaces/[w]",
    identity: ID.outsider.email,
    canonicalState: "not a member → server denies",
    expected: "denied boundary with the server reason; nothing of the Workspace shown",
  },
  async (page) => {
    const r = await api(out, `/workspaces/${WS}`);
    return {
      projection: r.body,
      checks: [
        check("denied boundary shown", 1, await page.getByTestId("orientation-denied").count(), "projection"),
        check("reason = server", r.body.reasonCode, (await page.getByTestId("orientation-denied").textContent()).trim(), "projection"),
        check("no h1 with the Workspace name", 0, await page.getByRole("heading", { level: 1, name: "SF-01 Inspection" }).count()),
      ],
    };
  },
  { expectedHttp: [/^403 GET \/api\/workspaces\/[0-9a-f-]+(\/overview)?$/, /403 \(Forbidden\)/] },
);
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/00000000-0000-4000-8000-000000000000`);
await record(
  fac,
  {
    slug: "challenge-not-found",
    route: "/workspaces/[w]/challenges/[unknown]",
    identity: ID.facilitator.email,
    canonicalState: "Challenge id unknown in this Workspace",
    expected: "NOT_FOUND boundary; trace reduced to the confirmed access context; nothing invented",
  },
  async (page) => ({
    projection: (await api(fac, `/workspaces/${WS}/challenges/00000000-0000-4000-8000-000000000000`)).body,
    checks: [
      check("load-failure boundary is not_found", "not_found", await page.getByTestId("load-failure").getAttribute("data-outcome"), "projection"),
      check("trace = access only", [["access", "established", "Workspaces"]], await traceData(page), "projection"),
    ],
  }),
  { expectedHttp: [/^404 GET \/api\/workspaces\/[0-9a-f-]+\/challenges\/0{8}-/, /404 \(Not Found\)/] },
);
await fac.page.goto(`${BASE}/workspaces/not-a-uuid`);
await record(
  fac,
  {
    slug: "workspace-malformed-rejected",
    route: "/workspaces/not-a-uuid",
    identity: ID.facilitator.email,
    canonicalState: "malformed id → server rejects (input, not authority)",
    expected: "REJECTED boundary, distinct from denied",
  },
  async (page) => ({
    projection: (await api(fac, "/workspaces/not-a-uuid")).body,
    checks: [check("rejected boundary shown", 1, await page.getByTestId("orientation-rejected").count(), "projection")],
  }),
  { expectedHttp: [/^400 GET \/api\/workspaces\/not-a-uuid(\/overview)?$/, /400 \(Bad Request\)/] },
);
// loading state: real latency via CDP network conditions (no interception)
const cdp = await fac.context.newCDPSession(fac.page);
await cdp.send("Network.enable");
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 2000, downloadThroughput: -1, uploadThroughput: -1 });
await fac.page.goto(`${BASE}/workspaces/${WS}/challenges/${CH}`, { waitUntil: "commit" });
await fac.page.getByTestId("challenge-loading").waitFor({ timeout: 15000 });
seq += 1;
const loadingShot = `${String(seq).padStart(2, "0")}-desktop-challenge-loading-latency-2s.png`;
await fac.page.screenshot({ path: join(SHOTS, loadingShot), fullPage: true });
const loadingTrace = await traceData(fac.page);
results.push({
  seq,
  screenshot: `screenshots/${loadingShot}`,
  url: `/workspaces/${WS}/challenges/${CH}`,
  route: "/workspaces/[w]/challenges/[c]",
  viewport: "desktop",
  identity: ID.facilitator.email,
  canonicalState: "projection not yet confirmed (2 s network latency, CDP emulation; no interception)",
  expectedRelation: "loading state; trace holds only the confirmed access context",
  checks: [check("trace while loading", [["access", "established", "Workspaces"]], loadingTrace, "projection")],
  pass: JSON.stringify(loadingTrace) === JSON.stringify([["access", "established", "Workspaces"]]),
});
console.log(`${results.at(-1).pass ? "PASS" : "FAIL"} #${seq} desktop challenge-loading`);
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });

await browser.close();

writeFileSync(RESULTS, JSON.stringify({ base: BASE, workspace: WS, challenge: CH, session: SID, generatedAt: new Date().toISOString(), results }, null, 2));

const rows = results.map(
  (r) =>
    `| ${r.seq} | [${r.screenshot.split("/")[1]}](${r.screenshot}) | \`${r.route}\` | ${r.viewport} | ${r.canonicalState} | ${r.identity} | ${r.expectedRelation} | ${
      (r.checks ?? []).filter((c) => !c.pass).map((c) => `FAILED: ${c.claim}`).join("; ") ||
      `${(r.checks ?? []).length} checks met; axe s/c ${r.axeSeriousCritical?.length ?? "n/a"}; overflow ${r.overflowPx ?? "n/a"}px; unexpected HTTP ${r.unexpectedHttp?.length ?? "n/a"}`
    } | ${r.pass ? "PASS" : "FAIL"} |`,
);
writeFileSync(
  join(ROOT, "MANIFEST.md"),
  `# SF-01 browser evidence manifest (generated by harness/review-harness.mjs)\n\nBase: ${BASE} · Workspace \`${WS}\` · Challenge \`${CH}\` · Session \`${SID}\`\n\n| # | Screenshot | Route | Viewport | Canonical state | Identity | Expected relation | Observed | Result |\n|---|---|---|---|---|---|---|---|---|\n${rows.join("\n")}\n\nFull per-state data (console, network, statics, axe, keyboard walk, redirect chain, projection): \`${RUN ? "results.json" : "results/results.json"}\`.\n`,
);
console.log(`done: ${results.filter((r) => r.pass).length}/${results.length} PASS`);
