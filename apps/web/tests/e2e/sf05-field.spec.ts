/**
 * SF-05 (L3, mocked lane): the doc 26 human-review repairs as component contract in a real browser — Workspace
 * normalization and field geometry, the semantic chamber grammar, the commit resonance event (after the canonical
 * re-read only), the breadcrumb field path, the login field, the Decision Surface in the field language, reduced
 * motion — against `page.route()`-fulfilled F02/F03 envelope shapes. Not runtime proof; the real-stack lane and the
 * review harness are separate. Doc 26 §41–§47 falsifiers; §50 test matrix.
 */
import { expect, test, type Page, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SESSION = "55555550-5555-4555-8555-555555555555";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NOT = (code: string, reason = `not possible: ${code}`) => ({ available: false, reasonCode: code, reason });
const WORKSPACE = { workspaceId: WS, name: "Activation inquiry", governedFounding: true };
const MEMBERS = [
  { userId: "u-root", name: "Root Rosa", email: "root@nonproof.test", role: "Owner" },
  { userId: "u-fac", name: "Facilitator Fay", email: "fay@nonproof.test", role: "Facilitator" },
  { userId: "u-c1", name: "Contributor Constantine", email: "c1@nonproof.test", role: "Contributor" },
];
const CONTROLLER = { bindingId: "b1", holderUserId: "u-fac", holderName: "Facilitator Fay", authorityClass: "SESSION_CONTROL_RIGHT", scope: `CHALLENGE:${CH}`, grantedByUserId: "u-root", grantedByName: "Root Rosa", grantedAt: "2026-09-24T11:00:00Z" };

const wsRecord = (id: string, name: string, createdAt: string) => ({ workspaceId: id, name, ownerId: "u-root", createdAt });
/** 14 Workspaces in 7 same-named pairs (distinct ids), plus one id repeated three times (three membership records). */
function manyWorkspaces() {
  const list = [];
  for (let i = 0; i < 7; i += 1) {
    list.push(wsRecord(`aaaaaaa${i}-0000-4000-8000-00000000000${i}`, "SF-03 Inspection", `2026-09-25T0${i}:25:04Z`));
    list.push(wsRecord(`bbbbbbb${i}-0000-4000-8000-00000000000${i}`, "Cross-Functional Customer Activation and Retention Inquiry Workspace for the European Enterprise Segment", `2026-09-25T0${i}:25:06Z`));
  }
  list.push(wsRecord("aaaaaaa0-0000-4000-8000-000000000000", "SF-03 Inspection", "2026-09-25T00:25:04Z"));
  list.push(wsRecord("aaaaaaa0-0000-4000-8000-000000000000", "SF-03 Inspection", "2026-09-25T00:25:04Z"));
  return list;
}
function orientation() {
  return { kind: "ok", workspace: { workspaceId: WS, name: WORKSPACE.name, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" }, role: "Owner", heldAuthorityClasses: ["WORKSPACE_GOVERNANCE_RIGHT"], authorized: true, governanceCapable: true };
}
function overview() {
  return { kind: "ok", workspace: WORKSPACE, viewer: { userId: "u-root", role: "Owner", isGovernanceRoot: true }, members: MEMBERS, challenges: [{ challengeId: CH, title: "Why did activation stall after onboarding?", description: null, createdAt: "2026-09-24T10:01:00Z" }], capabilities: { createChallenge: AVAILABLE, addMember: AVAILABLE } };
}
function detail(sessionCount = 2, grantAvailable = true) {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: "Understand before changing.", createdAt: "2026-09-24T10:01:00Z" },
    sessions: Array.from({ length: sessionCount }, (_, i) => ({ sessionId: `5555555${i}-5555-4555-8555-555555555555`, state: "QUESTION_CAPTURE", version: 3, createdAt: `2026-09-25T0${i}:25:00Z` })),
    sessionControllers: [CONTROLLER],
    members: MEMBERS,
    capabilities: { openSession: NOT(`NO_CHALLENGE_SESSION_CONTROL:${CH}`, "Opening a Session requires SESSION_CONTROL_RIGHT for this Challenge."), grantSessionControl: grantAvailable ? AVAILABLE : NOT("NOT_GOVERNANCE_ROOT", "Only the governance root grants Session control.") },
  };
}
const ACTIONS = ["BEGIN_SETUP", "BEGIN_CHALLENGE_CAPTURE", "PREPARE_BURST", "ADMIT_PARTICIPANT", "OPEN_QUESTION_GENERATION", "GRANT_SESSION_CONTROL", "CAPTURE_QUESTION", "COMPLETE_BURST"] as const;
function position(variant: "generation" | "capture" | "draft" = "generation") {
  const active = variant === "generation";
  const frozen = variant === "capture";
  const actions = Object.fromEntries(
    ACTIONS.map((name) => {
      if (variant === "draft") return [name, name === "BEGIN_SETUP" ? { ...AVAILABLE, relevant: true } : name === "ADMIT_PARTICIPANT" ? { ...NOT("SESSION_NOT_IN_STATE", "Participants are admitted after the Burst is prepared."), relevant: true } : { ...NOT("NOT_RELEVANT_IN_STATE"), relevant: false }];
      if (name === "CAPTURE_QUESTION" || name === "COMPLETE_BURST") return [name, active ? { ...AVAILABLE, relevant: true } : { ...NOT("BURST_NOT_ACTIVE"), relevant: false }];
      if (name === "ADMIT_PARTICIPANT") return [name, { ...AVAILABLE, relevant: true }];
      if (name === "GRANT_SESSION_CONTROL") return [name, { ...AVAILABLE, relevant: true }];
      return [name, { ...NOT("NOT_RELEVANT_IN_STATE"), relevant: false }];
    }),
  );
  const question = { questionId: "q-1", originalText: "Which step do most new users abandon first?", origin: "HUMAN", captureOrigin: "TYPED", authorUserId: "u-fac", authorName: "Facilitator Fay", capturedOrder: 0, capturedAt: "2026-09-25T01:40:00Z" };
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: null },
    session: { sessionId: SESSION, state: variant === "draft" ? "DRAFT" : active ? "QUESTION_GENERATION" : "QUESTION_CAPTURE", version: 4, method: "HUMAN_QUESTION_BURST", createdAt: "2026-09-25T00:25:00Z" },
    phases: ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS"].map((state, i) => ({ state, status: variant === "draft" ? (i === 0 ? "current" : "upcoming") : active ? (i < 3 ? "done" : i === 3 ? "current" : "upcoming") : i < 4 ? "done" : i === 4 ? "current" : "upcoming" })),
    serverNow: "2026-09-25T02:00:00Z",
    burst: variant === "draft" ? null : { burstId: "b-1", state: active ? "ACTIVE" : "COMPLETED", mode: "HUMAN_ONLY", version: 2, startedAt: "2026-09-25T01:30:00Z", completedAt: active ? null : "2026-09-25T01:50:00Z", guidanceSeconds: 600, guidanceIsAuthoritative: true },
    questionSet: active ? { visibility: "OWN_ONLY_WHILE_ACTIVE", mine: [], capturedCount: 1, frozen: null } : frozen ? { visibility: "FULL_FROZEN_SET", mine: [question], capturedCount: 1, frozen: { fingerprint: "fb294bbfe3e38cccc294affe7837daf763e4982e6de21c8ce9457e564abaeee6", verified: true, memberCount: 1, completedAt: "2026-09-25T01:50:00Z", questions: [question] } } : { visibility: "NONE", mine: [], capturedCount: null, frozen: null },
    participants: [{ userId: "u-fac", name: "Facilitator Fay", joinedAt: "2026-09-25T01:00:00Z", admittedByUserId: "u-root" }],
    sessionControllers: [{ ...CONTROLLER, scope: `SESSION:${SESSION}` }],
    establishedBy: { commandType: active ? "OPEN_QUESTION_GENERATION" : "COMPLETE_BURST", actorName: "Facilitator Fay", occurredAt: "2026-09-25T01:30:00Z", commitId: "550446e3-1dce-4cf3-a58d-be57a95d5672", authoritySourceType: "SESSION_CONTROL_RIGHT", authoritySourceRef: "b1", authorityScopeRef: `SESSION:${SESSION}` },
    viewer: { userId: "u-fac", role: "Facilitator", isSessionController: true, isGovernanceRoot: false },
    actions,
    admitCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
    grantCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
  };
}
async function routes(page: Page, opts: { workspaces?: unknown[]; detail?: unknown; position?: unknown } = {}): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
  await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: opts.workspaces ?? [{ workspaceId: WS, name: WORKSPACE.name, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" }] } }));
  await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation() }));
  await page.route(`${API}/workspaces/${WS}/overview`, (route) => route.fulfill({ json: overview() }));
  await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: opts.detail ?? detail() }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: opts.position ?? position() }));
}
/** A route whose response is released by the test (to observe the re-read gate). */
function gate(): { hold: (route: Route) => Promise<void>; release: (fulfil: (route: Route) => Promise<void>) => Promise<void> } {
  let pending: Route | null = null;
  let arrived: () => void = () => undefined;
  const arrival = new Promise<void>((resolve) => (arrived = resolve));
  return { hold: async (route) => { pending = route; arrived(); }, release: async (fulfil) => { await arrival; await fulfil(pending as unknown as Route); } };
}
const isPhone = (page: Page) => (page.viewportSize()?.width ?? 1280) < 768;
const sessionUrl = `/workspaces/${WS}/sessions/${SESSION}`;
const challengeUrl = `/workspaces/${WS}/challenges/${CH}`;

/** No two node bodies intersect; no material text escapes its frame. */
async function nodeOverlaps(page: Page): Promise<number> {
  return page.evaluate(() => {
    const r = [...document.querySelectorAll('[data-testid="field-stage"] .node-body, [data-testid="field-stage"] .core-nucleus')].map((e) => e.getBoundingClientRect());
    let n = 0;
    for (let i = 0; i < r.length; i += 1) for (let j = i + 1; j < r.length; j += 1) { const a = r[i], b = r[j]; if (a.width && b.width && a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) n += 1; }
    return n;
  });
}
const hOverflow = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);

test.describe("Workspace normalization (doc 26 §7, §41)", () => {
  test("one canonical id → one primary node: three records of one Workspace merge; seven same-named pairs stay fourteen, each disambiguated", async ({ page }) => {
    await routes(page, { workspaces: manyWorkspaces() });
    await page.goto("/workspaces");
    await page.getByTestId("workspaces-list").waitFor();
    const nodes = page.locator('[data-testid="workspaces-list"] li.node');
    await expect(nodes).toHaveCount(15); // founding relation + 14 canonical Workspaces
    const keys = await nodes.evaluateAll((els) => els.map((e) => e.getAttribute("data-key")));
    expect(new Set(keys).size).toBe(15);
    expect(keys.filter((k) => k === "aaaaaaa0-0000-4000-8000-000000000000")).toHaveLength(1);
    const metas = await page.locator('[data-testid="workspaces-list"] .node-meta').evaluateAll((els) => els.map((e) => e.textContent ?? ""));
    const homonymMetas = metas.filter((m) => m.startsWith("Workspace · founded"));
    expect(homonymMetas).toHaveLength(14);
    expect(new Set(homonymMetas).size).toBe(14);
    expect(homonymMetas[0]).toMatch(/founded 25 Sept,? 00:25 UTC · aaaaaaa0/);
    // the merged Workspace carries its three relations as one entity, never as three bodies
    await expect(page.locator('li.node[data-key="aaaaaaa0-0000-4000-8000-000000000000"]')).toHaveCount(1);
  });
  test("two different Workspaces with the same name are never collapsed; a unique name carries no distinguisher", async ({ page }) => {
    await routes(page, { workspaces: [wsRecord("a1000000-0000-4000-8000-000000000001", "Twin", "2026-09-25T08:00:00Z"), wsRecord("a2000000-0000-4000-8000-000000000002", "Twin", "2026-09-25T09:00:00Z"), wsRecord("a3000000-0000-4000-8000-000000000003", "Solo", "2026-09-25T10:00:00Z")] });
    await page.goto("/workspaces");
    await page.getByTestId("workspaces-list").waitFor();
    await expect(page.getByRole("link", { name: "Twin" })).toHaveCount(2);
    await expect(page.locator('li.node[data-key="a3000000-0000-4000-8000-000000000003"] .node-meta')).toHaveText("accessible Workspace");
    await expect(page.locator('li.node[data-key="a1000000-0000-4000-8000-000000000001"] .node-meta')).toContainText("a1000000");
  });
  test("long Workspace labels stay contained at a narrow width", async ({ page }) => {
    await routes(page, { workspaces: manyWorkspaces().slice(0, 6) });
    await page.setViewportSize({ width: isPhone(page) ? 360 : 1024, height: 900 });
    await page.goto("/workspaces");
    await page.getByTestId("workspaces-list").waitFor();
    await page.waitForTimeout(500);
    expect(await hOverflow(page)).toBeLessThanOrEqual(1);
    expect(await nodeOverlaps(page)).toBe(0);
  });
});

test.describe("Semantic chambers (doc 26 §16–§26, §42)", () => {
  test("the Session organ has differentiated chambers: question · authority · participation · proof · decision entry", async ({ page }) => {
    await routes(page);
    await page.goto(sessionUrl);
    await page.getByTestId("context-organ").waitFor();
    const classes = await page.locator(".organ .plane").evaluateAll((els) => els.map((e) => e.getAttribute("data-semantic")));
    expect(classes).toEqual(["question", "authority", "participation", "proof", "decision-entry"]);
    const tones = await page.locator(".organ .plane").evaluateAll((els) => els.map((e) => getComputedStyle(e).getPropertyValue("--chamber-tone").trim()));
    expect(new Set(tones).size).toBeGreaterThanOrEqual(4);
    await expect(page.locator('.plane[data-semantic="question"] .chamber-marker')).toHaveText("HUMAN_ONLY");
    await expect(page.locator(".question-surface")).toHaveAttribute("data-human-only", "true");
  });
  test("authority reads as SOURCE → AUTHORITY → HOLDER → SCOPE with the SESSION scope, apart from role and participation", async ({ page }) => {
    await routes(page);
    await page.goto(sessionUrl);
    const relation = page.locator('.plane[data-semantic="authority"] .authority-relation');
    await expect(relation).toHaveCount(1);
    await expect(relation).toHaveAttribute("data-scope-type", "SESSION");
    await expect(relation).toHaveAttribute("data-held", "true");
    await expect(relation.locator(".chain-role")).toHaveText(["granted by", "authority", "held by", "scope"]);
    await expect(relation).toContainText("Root Rosa");
    await expect(relation).toContainText("this Session");
    const marks = page.locator('.plane[data-semantic="participation"] .relation-mark');
    await expect(marks).toHaveText(["you", "participant", "Session controller"]);
    const [participantStyle, controllerStyle] = await marks.evaluateAll((els) => els.slice(1).map((e) => getComputedStyle(e).borderTopStyle + ":" + getComputedStyle(e).color));
    expect(participantStyle).not.toBe(controllerStyle);
  });
  test("proof is a provenance spine with commit and authority source; identifiers are tokens that never break mid-token", async ({ page }) => {
    await routes(page);
    await page.goto(sessionUrl);
    const spine = page.getByTestId("session-last-transition");
    await expect(spine.locator(".spine-step")).toHaveCount(5);
    await expect(spine).toContainText("OPEN_QUESTION_GENERATION");
    await expect(spine).toContainText("SESSION_CONTROL_RIGHT");
    await expect(spine).toContainText("550446e3-");
    await page.getByTestId("session-identifiers").locator("summary").click();
    const token = page.getByTestId("session-identifiers").locator(".token").first();
    await expect(token).toContainText(SESSION.slice(0, 8));
    const info = await token.evaluate((el) => ({ wordBreak: getComputedStyle(el).wordBreak, lines: el.getClientRects().length }));
    expect(info.wordBreak).toBe("keep-all");
    expect(await page.locator('[aria-label="Copy Session"]').count()).toBe(1);
  });
  test("boundaries are classed and differ visually; none is an alert", async ({ page }) => {
    await routes(page, { position: position("draft") });
    await page.goto(sessionUrl);
    const admit = page.getByTestId("action-reason-ADMIT_PARTICIPANT");
    await expect(admit).toHaveAttribute("data-boundary", "MISSING_PREREQUISITE");
    await expect(admit).toContainText("missing prerequisite");
    await expect(admit).toContainText("Participants are admitted after the Burst is prepared.");
    await page.goto(challengeUrl);
    const open = page.getByTestId("session-create-unavailable");
    await expect(open).toHaveAttribute("data-boundary", "MISSING_AUTHORITY");
    const openStyle = await open.locator(".boundary-edge").evaluate((el) => getComputedStyle(el).borderLeftColor + getComputedStyle(el).borderLeftStyle);
    await page.goto(sessionUrl);
    const admitStyle = await admit.locator(".boundary-edge").evaluate((el) => getComputedStyle(el).borderLeftColor + getComputedStyle(el).borderLeftStyle);
    expect(openStyle).not.toBe(admitStyle);
    expect(await page.locator('.boundary-mark[role="alert"]').count()).toBe(0);
  });
  test("QUESTION_CAPTURE: the frozen set is a sealed artifact chamber, immutable and verified", async ({ page }) => {
    await routes(page, { position: position("capture") });
    await page.goto(sessionUrl);
    await expect(page.locator('.plane[data-semantic="frozen"]')).toHaveCount(1);
    await expect(page.locator(".frozen-artifact")).toHaveAttribute("data-immutable", "true");
    await expect(page.getByTestId("frozen-marker")).toHaveText("FROZEN");
    await expect(page.getByTestId("frozen-verified")).toContainText("Verified");
    await expect(page.locator(".artifact[data-immutable='true'] .verbatim")).toHaveText("Which step do most new users abandon first?");
    expect(await page.locator(".frozen-artifact textarea, .frozen-artifact input").count()).toBe(0);
  });
  test("the irreversible confirmation is a confirmation chamber naming what freezes, what cannot happen, cancel and commit", async ({ page }) => {
    await routes(page);
    await page.goto(sessionUrl);
    await page.getByTestId("complete-button").click();
    const confirm = page.getByTestId("complete-confirm");
    await expect(confirm).toHaveAttribute("data-boundary", "IRREVERSIBLE_CONFIRMATION");
    await expect(confirm).toContainText("becomes immutable");
    await expect(confirm).toContainText("cannot happen afterwards");
    await expect(confirm.getByRole("button", { name: "Freeze the set and complete the Burst" })).toBeVisible();
    await expect(confirm.getByRole("button", { name: "Keep the Burst open" })).toBeVisible();
  });
});

test.describe("Commit resonance (doc 26 §27, §43)", () => {
  test("after a committed grant the event appears only once the canonical re-read confirmed it, names the CHALLENGE scope, does not block, and leaves; the proof line stays", async ({ page }) => {
    test.skip(isPhone(page), "measured on the desktop composition");
    await routes(page);
    let reread = 0;
    const held = gate();
    await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => route.fulfill({ json: { kind: "committed", commitId: "c-1" } }));
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    // the re-read after the commit is held: no event may exist before it
    await page.unroute(`${API}/workspaces/${WS}/challenges/${CH}`);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => { reread += 1; return held.hold(route); });
    await page.getByLabel("Grant session control to").selectOption("u-c1");
    await page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-reconstruction", "reading");
    await expect(page.getByTestId("field-event")).toHaveCount(0);
    await held.release((route) => route.fulfill({ json: detail(2, true) }));
    const event = page.getByTestId("field-event");
    await expect(event).toBeVisible();
    await expect(event.locator(".event-title")).toHaveText("SESSION CONTROL GRANTED");
    await expect(event.locator(".event-text")).toContainText("Contributor Constantine now holds Session control for this Challenge");
    await expect(event.locator(".event-text")).not.toContainText("for this Session");
    expect(await event.evaluate((el) => getComputedStyle(el).pointerEvents)).toBe("none");
    expect(await event.evaluate((el) => getComputedStyle(el).animationName)).toBe("event-life");
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-quiet", "true");
    await expect(page.getByTestId("command-outcome")).toContainText("Committed.");
    await expect(event).toHaveCount(0, { timeout: 9000 });
    await expect(page.getByTestId("command-outcome")).toHaveCount(1);
    expect(reread).toBe(1);
  });
  test("no event for a denied grant, and the boundary stays in the chamber", async ({ page }) => {
    test.skip(isPhone(page), "measured on the desktop composition");
    await routes(page);
    await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => route.fulfill({ status: 403, json: { kind: "denied", reasonCode: "NOT_GOVERNANCE_ROOT" } }));
    await page.goto(challengeUrl);
    await page.getByLabel("Grant session control to").selectOption("u-c1");
    await page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "denied");
    await page.waitForTimeout(600);
    await expect(page.getByTestId("field-event")).toHaveCount(0);
  });
  test("reduced motion: the event appears without motion and still leaves", async ({ page }) => {
    test.skip(isPhone(page), "measured on the desktop composition");
    await page.emulateMedia({ reducedMotion: "reduce" });
    await routes(page);
    await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => route.fulfill({ json: { kind: "committed", commitId: "c-1" } }));
    await page.goto(challengeUrl);
    await page.getByLabel("Grant session control to").selectOption("u-c1");
    await page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
    const event = page.getByTestId("field-event");
    await expect(event).toBeVisible();
    const anim = await event.evaluate((el) => ({ name: getComputedStyle(el).animationName, timing: getComputedStyle(el).animationTimingFunction, particles: getComputedStyle(el.querySelector(".event-particle")!).opacity }));
    expect(anim.name).toBe("event-hold");
    expect(anim.timing).toMatch(/steps\(1/);
    expect(anim.particles).toBe("0");
    await expect(event).toHaveCount(0, { timeout: 9000 });
  });
});

test.describe("Breadcrumb field path (doc 26 §29–§30, §45)", () => {
  test("at a normal desktop width the Session path is one line, the current lifecycle state is complete, the identity stays centred, logout is clear", async ({ page }) => {
    test.skip(isPhone(page), "desktop path");
    await page.setViewportSize({ width: 1280, height: 860 });
    await routes(page);
    await page.goto(sessionUrl);
    await page.getByTestId("field-core").waitFor();
    const nav = page.getByRole("navigation", { name: "Inquiry position" });
    const tops = await nav.locator("li").evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().top)));
    expect(new Set(tops).size, `route nodes on one line: ${tops.join(",")}`).toBe(1);
    const current = nav.locator('li[data-status="current"] .trace-label');
    await expect(current).toHaveText("QUESTION_GENERATION");
    expect(await current.evaluate((el) => el.scrollWidth <= el.clientWidth + 1)).toBe(true);
    const identity = (await page.getByTestId("identity").boundingBox())!;
    const vw = page.viewportSize()!.width;
    expect(Math.abs(identity.x + identity.width / 2 - vw / 2)).toBeLessThan(6);
    const navBox = (await nav.boundingBox())!;
    const logout = (await page.getByTestId("logout-button").boundingBox())!;
    expect(navBox.x + navBox.width).toBeLessThanOrEqual(identity.x + 1);
    expect(identity.x + identity.width).toBeLessThanOrEqual(logout.x + 1);
    // compressed established segments stay inspectable
    await expect(nav.locator('li[data-coordinate="challenge"] a')).toHaveAttribute("title", "Why did activation stall after onboarding?");
  });
  test("a long Workspace name compresses instead of wrapping the state below the path (1024 px)", async ({ page }) => {
    test.skip(isPhone(page), "desktop path");
    await page.setViewportSize({ width: 1024, height: 800 });
    await routes(page, { position: { ...position(), workspace: { ...WORKSPACE, name: "Cross-Functional Customer Activation and Retention Inquiry Workspace for the European Enterprise Segment" } } });
    await page.goto(sessionUrl);
    await page.getByTestId("field-core").waitFor();
    const nav = page.getByRole("navigation", { name: "Inquiry position" });
    const tops = await nav.locator("li").evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().top)));
    expect(new Set(tops).size).toBe(1);
    await expect(nav.locator('li[data-status="current"] .trace-label')).toHaveText("QUESTION_GENERATION");
  });
});

test.describe("Login field (doc 26 §28, §44)", () => {
  test("idle is calm; attention on Login gathers the field (denser, brighter ambient) without implying success; focus responds locally", async ({ page }) => {
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
    await page.goto("/login");
    const field = page.locator("main.access-field");
    await expect(field).not.toHaveAttribute("data-attract", /.+/);
    const denseRest = await page.locator(".particles-dense .particle").first().evaluate((el) => parseFloat(getComputedStyle(el).fillOpacity));
    expect(denseRest).toBeLessThan(0.5);
    await page.getByTestId("login-submit").hover();
    await expect(field).toHaveAttribute("data-attract", "login");
    await expect.poll(() => page.locator(".particles-dense .particle").first().evaluate((el) => parseFloat(getComputedStyle(el).fillOpacity))).toBeGreaterThan(0.9);
    const glow = await page.getByTestId("login-submit").evaluate((el) => getComputedStyle(el).boxShadow);
    expect(glow).not.toBe("none");
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "current");
    await expect(page).toHaveURL(/\/login$/);
    await page.mouse.move(2, 2);
    await page.getByTestId("login-email").focus();
    await expect(field).toHaveAttribute("data-focus", "email");
    await expect(field).not.toHaveAttribute("data-attract", /.+/);
    await page.getByTestId("login-password").focus();
    await expect(field).toHaveAttribute("data-focus", "password");
  });
  test("a request is not a success: while the verdict is pending the core is loading and nothing celebrates; a denial is a boundary", async ({ page }) => {
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
    const held = gate();
    await page.route(`${API}/auth/login`, held.hold);
    await page.goto("/login");
    await page.getByTestId("login-email").fill("owner@nonproof.test");
    await page.getByTestId("login-password").fill("secret");
    await page.getByTestId("login-submit").click();
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "loading");
    await expect(page.getByTestId("login-pending")).toBeVisible();
    expect(await page.locator("[data-success], .field-event").count()).toBe(0);
    await held.release((route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "INVALID_CREDENTIALS" } }));
    await expect(page.getByTestId("login-error")).toBeVisible();
    await expect(page.getByTestId("access-core")).toHaveAttribute("data-core-state", "boundary");
    await expect(page).toHaveURL(/\/login$/);
  });
  test("reduced motion keeps the attention semantics and removes the motion", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ status: 401, json: { kind: "denied", reasonCode: "NO_SESSION" } }));
    await page.goto("/login");
    await page.getByTestId("login-submit").hover();
    await expect(page.locator("main.access-field")).toHaveAttribute("data-attract", "login");
    const names = await page.evaluate(() => [...document.querySelectorAll(".particle, .nebula, .access-membrane")].map((n) => getComputedStyle(n).animationName + "|" + getComputedStyle(n).transitionDuration));
    for (const n of names) expect(n).toBe("none|0s");
  });
});

test.describe("Decision Surface in the field language (doc 26 §31, §46)", () => {
  const DECISION_ROUTE = "http://localhost:8000/workspaces/**/sessions/**";
  const OK = { kind: "ok", data: { workspaceId: WS, challenge: { challengeId: CH, workspaceId: WS, title: "Reduce onboarding drop-off", description: null }, session: { sessionId: SESSION, challengeId: CH, workspaceId: WS, state: "QUESTION_CAPTURE" }, burst: { burstId: "b-1", sessionId: SESSION, state: "COMPLETED", mode: "HUMAN_ONLY", questions: [{ questionId: "q-1", originalText: "Why do users abandon step 3?", origin: "HUMAN" }] }, decision: null, aiRecommendation: null } };
  test("the surface is framed, backgrounded and chambered like the field, keeps every component, and never falls back to raw text", async ({ page }) => {
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
    await page.route(DECISION_ROUTE, (route) => route.fulfill({ json: OK }));
    await page.goto(`${sessionUrl}/decision`);
    await page.getByTestId("session-view-ok").waitFor();
    await expect(page.getByTestId("field-background")).toHaveCount(1);
    await expect(page.getByTestId("identity")).toBeVisible();
    await expect(page.getByTestId("context-organ")).toBeVisible();
    const classes = await page.locator(".organ .plane").evaluateAll((els) => els.map((e) => e.getAttribute("data-semantic")));
    expect(classes).toEqual(["context", "frozen", "decision-entry"]);
    await expect(page.getByTestId("field-core")).toContainText("NON_PROOF");
    await expect(page.getByTestId("burst-human-only-indicator")).toBeVisible();
    await expect(page.getByTestId("burst-frozen-indicator")).toBeVisible();
    await expect(page.getByTestId("decision-none")).toBeVisible();
    // no raw fallback: the decision section sits inside a chamber with the organ's surface
    const styled = await page.getByTestId("decision-section").evaluate((el) => !!el.closest(".plane.chamber") && getComputedStyle(el.closest(".organ")!).borderTopWidth === "1px");
    expect(styled).toBe(true);
    expect(await page.locator("main button, main input, main form").count()).toBe(0);
    const trace = page.getByRole("navigation", { name: "Inquiry position" });
    await expect(trace.locator('li[data-status="current"]')).toContainText("Decision surface");
    await expect(trace.locator('li[data-coordinate="session"] a')).toHaveAttribute("href", sessionUrl);
  });
  test("a denied Session view stays a boundary in the field with no action element in main", async ({ page }) => {
    await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
    await page.route(DECISION_ROUTE, (route) => route.fulfill({ json: { kind: "denied", result: "DENY", reasonCode: "x" } }));
    await page.goto(`${sessionUrl}/decision`);
    await expect(page.getByTestId("denied-banner")).toBeVisible();
    await expect(page.getByTestId("field-core")).toHaveAttribute("data-core-state", "boundary");
    expect(await page.locator("main button, main input, main form, main [role='button']").count()).toBe(0);
  });
});

test.describe("Intensification stays calm (doc 26 §10–§14, §37)", () => {
  test("nodes breathe subtly and out of phase; an encounter strengthens the aura and the pulse; reduced motion removes the breathing", async ({ page }) => {
    test.skip(isPhone(page), "orbit representation");
    await routes(page);
    await page.goto(challengeUrl);
    await page.getByTestId("field-core").waitFor();
    const breath = await page.locator("li.node .node-aura").evaluateAll((els) => els.map((e) => ({ name: getComputedStyle(e).animationName, delay: getComputedStyle(e).animationDelay, duration: parseFloat(getComputedStyle(e).animationDuration) })));
    for (const b of breath) { expect(b.name).toBe("node-breathe"); expect(b.duration).toBeGreaterThanOrEqual(9); expect(b.duration).toBeLessThanOrEqual(14); }
    expect(new Set(breath.map((b) => b.delay)).size).toBeGreaterThan(1);
    const rest = await page.locator('.current-pulse[data-key="b1"]').evaluate((el) => parseFloat(getComputedStyle(el).width));
    await page.locator('li.node[data-key="b1"]').hover();
    await expect(page.locator('.current-pulse[data-key="b1"]')).toHaveAttribute("data-resonating", "true");
    await expect.poll(() => page.locator('.current-pulse[data-key="b1"]').evaluate((el) => parseFloat(getComputedStyle(el).width))).toBeGreaterThan(rest);
    await expect(page.locator('.chamber[data-plane="governance"]')).toHaveAttribute("data-chamber-resonating", "true");
    await page.emulateMedia({ reducedMotion: "reduce" });
    expect(await page.locator("li.node .node-aura").first().evaluate((el) => getComputedStyle(el).animationName)).toBe("none");
  });
});
