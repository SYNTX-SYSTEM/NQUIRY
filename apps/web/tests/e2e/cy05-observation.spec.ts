/**
 * CYAN-PCPG-05 (mocked lane): the actor's raw-intent observation drives the live membrane. Responses are
 * `page.route()`-fulfilled in the exact shape of the pinned producer checkpoint-PFC-PCPG-18 (`http_pcpg._result_body`).
 * Laws: membrane stays "No observation" until a real result; body exactness (no client-supplied governance, no
 * Idempotency-Key); not role-gated; unavailable → "Governance unavailable" only; failures never replace a valid
 * observation and keep the actor's text; malformed fails closed; a second Observe replaces; a canonical version change
 * → Superseded (no clock); reload → "No observation"; no storage; no send-like control; no provider call.
 */
import { expect, test, type Page, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SESSION = "55555550-5555-4555-8555-555555555555";
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NOT = (code: string) => ({ available: false, reasonCode: code, reason: `not possible: ${code}` });
const WORKSPACE = { workspaceId: WS, name: "Activation inquiry", governedFounding: true };
const PHASES = ["DRAFT", "SETUP", "CHALLENGE_CAPTURE", "QUESTION_GENERATION", "QUESTION_CAPTURE", "ANALYSIS"];
const QUESTION = { questionId: "q-1", originalText: "Which step do most new users abandon first?", origin: "HUMAN", captureOrigin: "TYPED", authorUserId: "u-fac", authorName: "Facilitator Fay", capturedOrder: 0, capturedAt: "2026-09-25T01:40:00Z" };
function position(sessionVersion = 4, viewer: "u-fac" | "u-c1" = "u-fac") {
  const actions = Object.fromEntries(["BEGIN_SETUP", "BEGIN_CHALLENGE_CAPTURE", "PREPARE_BURST", "ADMIT_PARTICIPANT", "OPEN_QUESTION_GENERATION", "GRANT_SESSION_CONTROL", "CAPTURE_QUESTION", "COMPLETE_BURST"].map((n) => [n, { ...(n === "GRANT_SESSION_CONTROL" && viewer === "u-fac" ? AVAILABLE : NOT("NOT_RELEVANT_IN_STATE")), relevant: n === "GRANT_SESSION_CONTROL" }]));
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why did activation stall after onboarding?", description: null },
    session: { sessionId: SESSION, state: "QUESTION_CAPTURE", version: sessionVersion, method: "HUMAN_QUESTION_BURST", createdAt: "2026-09-25T00:25:00Z" },
    phases: PHASES.map((state, i) => ({ state, status: i < 4 ? "done" : i === 4 ? "current" : "upcoming" })),
    serverNow: "2026-09-25T02:00:00Z",
    burst: { burstId: "b-1", state: "COMPLETED", mode: "HUMAN_ONLY", version: 2, startedAt: "2026-09-25T01:30:00Z", completedAt: "2026-09-25T01:50:00Z", guidanceSeconds: 600, guidanceIsAuthoritative: true },
    questionSet: { visibility: "FULL_FROZEN_SET", mine: [QUESTION], capturedCount: 1, frozen: { fingerprint: "fb294bbfe3e38cccc294affe7837daf763e4982e6de21c8ce9457e564abaeee6", verified: true, memberCount: 1, completedAt: "2026-09-25T01:50:00Z", questions: [QUESTION] } },
    participants: [{ userId: "u-fac", name: "Facilitator Fay", joinedAt: "2026-09-25T01:00:00Z", admittedByUserId: "u-root" }, { userId: "u-c1", name: "Contributor Constantine", joinedAt: "2026-09-25T01:01:00Z", admittedByUserId: "u-fac" }],
    sessionControllers: [{ bindingId: "b1", holderUserId: "u-fac", holderName: "Facilitator Fay", authorityClass: "SESSION_CONTROL_RIGHT", scope: `SESSION:${SESSION}`, grantedByUserId: "u-root", grantedByName: "Root Rosa", grantedAt: "2026-09-24T11:00:00Z" }],
    establishedBy: { commandType: "COMPLETE_BURST", actorName: "Facilitator Fay", occurredAt: "2026-09-25T01:50:00Z", commitId: "550446e3-1dce-4cf3-a58d-be57a95d5672", authoritySourceType: "SESSION_CONTROL_RIGHT", authoritySourceRef: "b1", authorityScopeRef: `SESSION:${SESSION}` },
    viewer: { userId: viewer, role: viewer === "u-fac" ? "Facilitator" : "Contributor", isSessionController: viewer === "u-fac", isGovernanceRoot: false },
    actions,
    admitCandidates: [],
    grantCandidates: [{ userId: "u-c1", name: "Contributor Constantine" }],
  };
}
const DELTA = { deltaId: "d-0", operation: "REQUEST_QUESTION_ANALYSIS", executionClass: "PROVIDER_COMPUTATION", target: null, sourceClause: "Analyse the questions", span: [0, 21], currentState: "QUESTION_CAPTURE", result: "INDETERMINATE", reasonCode: "DATA_GOVERNANCE_NOT_MATERIALIZED", flags: [], sessionProofCeiling: "GOVERNED" };
const HUMAN = { ...DELTA, deltaId: "d-1", operation: "SELECT_PRIMARY_QUESTION", executionClass: "HUMAN_COMMAND", sourceClause: "pick the primary question", span: [23, 48], result: "STATE_BOUNDARY", reasonCode: "SESSION_NOT_IN_QUESTION_SELECTION" };
function current(variant: "provider" | "boundary" = "provider", canSend = false) {
  return { kind: "current", contract: "PCPG-R12/1", basis: { rawIntentDigestSha256: "3f9a".padEnd(64, "0"), derivationTime: "2026-10-01T11:17:00+00:00" }, semanticObservation: { ruleSetVersion: "26/2026-09-29", clauses: ["Analyse the questions"], actions: [], unknownRelations: [], relationsTouched: ["REQUEST_QUESTION_ANALYSIS"], declaredPurpose: null, semanticPurpose: null, purposeAlignment: null, semanticDrift: false }, deltas: variant === "provider" ? [DELTA] : [HUMAN], chain: { firstBrokenRelation: variant === "boundary" ? { predecessor: null, broken: HUMAN } : null, maximumLegitimateTransition: [], nextValidTransition: null, humanAuthorityRequired: [], partial: variant === "boundary" }, capability: { governanceAdmissible: false, governanceAdmissibleReasons: ["MLT_EMPTY"], providerExecutable: false, providerExecutableReasons: ["NO_ELIGIBLE_PROVIDER_ROUTE"], canSend }, composedProofCeiling: null };
}
function envelope(governanceObservation: unknown, rawIntent = "Analyse the questions") {
  return { kind: "ok", field: "PRE_CALL_PROMPT_GOVERNANCE", workspace: { workspaceId: WS, name: WORKSPACE.name }, session: { sessionId: SESSION }, rawIntent, rawIntentLength: rawIntent.length, rawIntentDigestSha256: "3f9a".padEnd(64, "0"), declaredPurpose: null, observedAt: "2026-10-01T11:17:00+00:00", governanceObservation };
}
const SESSION_URL = `/workspaces/${WS}/sessions/${SESSION}`;
async function base(page: Page, viewer: "u-fac" | "u-c1" = "u-fac"): Promise<{ requested: string[] }> {
  const requested: string[] = [];
  page.on("request", (r) => {
    if (r.url().startsWith(API)) requested.push(`${r.method()} ${new URL(r.url()).pathname}`);
  });
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: viewer } }));
  await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: position(4, viewer) }));
  return { requested };
}
async function observe(page: Page, text: string): Promise<void> {
  await page.getByTestId("intent-text").fill(text);
  await page.getByTestId("observe-button").click();
}
const membrane = (page: Page) => page.getByTestId("field-core").getByTestId("governance-membrane");

test.describe("CYAN-PCPG-05: raw intent → live membrane", () => {
  test("1./2./3./5. the membrane stays 'No observation' until the real result; Observe sends exactly rawIntent + sessionId, no key, no governance; the real derived label then shows", async ({ page }) => {
    const { requested } = await base(page);
    let release: (route: Route) => Promise<void> = async () => undefined;
    const held = new Promise<Route>((resolve) => page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => { resolve(route); release = (r) => r.fulfill({ json: envelope(current("provider", true)) }); }));
    await page.goto(SESSION_URL);
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
    await observe(page, "Analyse the questions");
    const route = await held;
    expect(route.request().method()).toBe("POST");
    expect(route.request().postDataJSON()).toEqual({ rawIntent: "Analyse the questions", sessionId: SESSION });
    expect(route.request().headers()["idempotency-key"]).toBeUndefined();
    // while observing: pending text, membrane unchanged, control disabled
    await expect(page.getByTestId("observe-pending")).toBeVisible();
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
    await expect(page.getByTestId("observe-button")).toBeDisabled();
    await release(route);
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "PROVIDER_NOT_EXECUTABLE");
    await expect(membrane(page).getByTestId("membrane-words")).toHaveText("Provider not executable");
    await expect(membrane(page).getByTestId("membrane-observed-at")).toContainText("observed at");
    await expect(page.getByTestId("observation-facts")).toContainText("for this view only");
    await expect(page.getByTestId("intent-text")).toHaveValue("Analyse the questions");
    // 19./18. canSend true created no affordance; no send-like control anywhere in the field
    await expect(page.locator("main, aside").getByRole("button", { name: /^(Send|Run|Execute|Submit to AI)$/ })).toHaveCount(0);
    await expect(page.locator("main, aside").getByRole("button", { name: "Observe" })).toHaveCount(1);
    // 20. no provider call: only the known routes were requested
    expect([...new Set(requested)].sort()).toEqual([`GET /workspaces/${WS}/sessions/${SESSION}/position`, `POST /workspaces/${WS}/prompt-observations`]);
    // 16. no storage
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0]);
    // 17. no raw intent in the console
    await page.screenshot({ path: `test-results/cy05-visual/${test.info().project.name}-observed-provider.png` });
  });

  test("4. Observe is not role-gated: a Contributor who is not the Session controller observes too", async ({ page }) => {
    await base(page, "u-c1");
    await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => route.fulfill({ json: envelope(current("boundary")) }));
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("intent-chamber")).toBeVisible();
    await expect(page.getByTestId("observe-button")).toBeVisible();
    await observe(page, "pick the primary question");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "BOUNDARY_REACHED");
    await expect(membrane(page)).toHaveAttribute("data-prominence", "prominent");
  });

  test("6. unavailable becomes 'Governance unavailable' only", async ({ page }) => {
    await base(page);
    await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => route.fulfill({ json: envelope({ kind: "unavailable", reasonCode: "SEMANTIC_OBSERVATION_UNAVAILABLE" }, "日本語のテキストです") }));
    await page.goto(SESSION_URL);
    await observe(page, "日本語のテキストです");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "GOVERNANCE_UNAVAILABLE");
    await expect(membrane(page).getByTestId("membrane-words")).toHaveText("Governance unavailable");
    await expect(membrane(page)).not.toContainText(/admissible|Boundary|Authority|Provider/);
    await expect(page.getByTestId("observe-failure")).toHaveCount(0);
  });

  test("7./8./9./10./11. failures never replace the valid observation and keep the text; malformed fails closed", async ({ page }) => {
    await base(page);
    let answer: unknown = envelope(current("provider"));
    let abort = false;
    await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => (abort ? route.abort("connectionrefused") : route.fulfill({ json: answer })));
    await page.goto(SESSION_URL);
    await observe(page, "Analyse the questions");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "PROVIDER_NOT_EXECUTABLE");
    const digest = await page.getByTestId("observed-digest").innerText();
    for (const [body, kind, code] of [
      [{ kind: "rejected", reasonCode: "RAW_INTENT_TOO_LONG" }, "rejected", "RAW_INTENT_TOO_LONG"],
      [{ kind: "denied", reasonCode: "WORKSPACE_NOT_ACCESSIBLE" }, "denied", "WORKSPACE_NOT_ACCESSIBLE"],
      [{ kind: "not_found", reasonCode: "SESSION_NOT_FOUND" }, "not_found", "SESSION_NOT_FOUND"],
    ] as const) {
      answer = body;
      await page.getByTestId("intent-text").fill("a changed draft");
      await page.getByTestId("observe-button").click();
      await expect(page.getByTestId("observe-failure")).toHaveAttribute("data-outcome", kind);
      await expect(page.getByTestId("observe-failure-code")).toHaveText(code);
      await expect(membrane(page)).toHaveAttribute("data-membrane-label", "PROVIDER_NOT_EXECUTABLE");
      await expect(page.getByTestId("observed-digest")).toHaveText(digest);
      await expect(page.getByTestId("intent-text")).toHaveValue("a changed draft");
    }
    abort = true;
    await page.getByTestId("observe-button").click();
    await expect(page.getByTestId("observe-failure")).toHaveAttribute("data-outcome", "network_failure");
    await expect(page.getByTestId("observe-failure")).toContainText("Nothing is assumed");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "PROVIDER_NOT_EXECUTABLE");
    abort = false;
    answer = envelope({ ...current("provider"), contract: "PCPG-R12/2" });
    await page.getByTestId("observe-button").click();
    await expect(page.getByTestId("observe-failure")).toHaveAttribute("data-outcome", "malformed");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "GOVERNANCE_UNAVAILABLE");
    await expect(page.getByTestId("observation-facts")).toHaveCount(0);
  });

  test("12./13./14./15. a second Observe replaces; a canonical version change marks Superseded without a clock; reload returns to No observation", async ({ page }) => {
    await base(page);
    let version = 4;
    await page.unroute(`${API}/workspaces/${WS}/sessions/${SESSION}/position`);
    await page.route(`${API}/workspaces/${WS}/sessions/${SESSION}/position`, (route) => route.fulfill({ json: position(version) }));
    let variant: "provider" | "boundary" = "provider";
    await page.route(`${API}/workspaces/${WS}/prompt-observations`, (route) => route.fulfill({ json: envelope(current(variant)) }));
    await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => { version = 5; return route.fulfill({ json: { kind: "committed", replayed: false, bindingId: "b2" } }); });
    await page.goto(SESSION_URL);
    await observe(page, "Analyse the questions");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "PROVIDER_NOT_EXECUTABLE");
    variant = "boundary";
    await observe(page, "pick the primary question");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "BOUNDARY_REACHED");
    await expect(page.getByTestId("observe-superseded")).toHaveCount(0);
    // a committed command re-reads the Session (version 5): the observation is presented as superseded, unchanged otherwise
    const digest = await page.getByTestId("observed-digest").innerText();
    await page.getByLabel("Grant session control to").selectOption("u-c1");
    await page.getByRole("button", { name: "Grant session control for this Session" }).click();
    await expect(page.getByTestId("command-outcome")).toHaveAttribute("data-outcome", "committed");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "SUPERSEDED");
    await expect(membrane(page)).toHaveAttribute("data-observation", "superseded");
    await expect(page.getByTestId("observe-superseded")).toBeVisible();
    await expect(page.getByTestId("observed-digest")).toHaveText(digest);
    // a fresh observation on the current Field is current again
    await observe(page, "pick the primary question");
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "BOUNDARY_REACHED");
    // reload → honestly "No observation"
    await page.reload();
    await expect(membrane(page)).toHaveAttribute("data-membrane-label", "NO_OBSERVATION");
    await expect(page.getByTestId("intent-text")).toHaveValue("");
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0]);
  });

  test("22./23. the organism stays primary; the chamber adds no horizontal overflow; the membrane semantics of PCPG-04 are unchanged", async ({ page }) => {
    await base(page);
    await page.goto(SESSION_URL);
    await expect(page.getByTestId("session-phases")).toBeVisible();
    await expect(page.getByTestId("active-phase")).toHaveAttribute("data-semantic", "frozen");
    await expect(page.getByTestId("intent-chamber")).toHaveAttribute("data-semantic", "context");
    expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
    await expect(membrane(page)).toHaveAttribute("data-prominence", "quiet");
    await expect(membrane(page).locator("button, a, input, form")).toHaveCount(0);
    await page.screenshot({ path: `test-results/cy05-visual/${test.info().project.name}-chamber-no-observation.png` });
  });
});
