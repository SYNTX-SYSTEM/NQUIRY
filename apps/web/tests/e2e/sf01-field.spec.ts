/**
 * SF-01 WU-SF01.4 (L3): component contract of the Relational Interaction Field
 * on the pre-Session surfaces. MOCKED lane (`playwright.sf01.config.ts`):
 * proves UI semantics against `page.route()`-fulfilled F02/F01 envelope shapes.
 * It is NOT runtime proof. The isolated real-stack lane (L6/L7) is separate.
 *
 * Every fixture mirrors a published F01/F02 producer (`inquiry_queries`,
 * `http_f02`, F01 `http_dispatch`). No F03 shape appears here.
 */
import { expect, test, type Page, type Request, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const WS = "11111111-1111-4111-8111-111111111111";
const CH = "22222222-2222-4222-8222-222222222222";
const SID = "33333333-3333-4333-8333-333333333333";

const WORKSPACE = { workspaceId: WS, name: "Field inquiry", governedFounding: true };
const AVAILABLE = { available: true, reasonCode: null, reason: null };
const NO_OPEN = {
  available: false,
  reasonCode: `NO_CHALLENGE_SESSION_CONTROL:${CH}`,
  reason: `Opening a Session requires SESSION_CONTROL_RIGHT for this Challenge (scope CHALLENGE:${CH}). Only the Workspace governance root can grant it.`,
};

function orientation(governanceCapable: boolean) {
  return {
    kind: "ok",
    workspace: { workspaceId: WS, name: WORKSPACE.name, ownerId: "u-root", createdAt: "2026-09-24T10:00:00Z" },
    role: governanceCapable ? "Owner" : "Facilitator",
    heldAuthorityClasses: governanceCapable ? ["WORKSPACE_GOVERNANCE_RIGHT"] : [],
    authorized: governanceCapable,
    governanceCapable,
  };
}

function overview(challenges: readonly { challengeId: string; title: string }[] = []) {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    viewer: { userId: "u-root", role: "Owner", isGovernanceRoot: true },
    members: [{ userId: "u-root", name: "Root", email: "root@nonproof.test", role: "Owner" }],
    challenges: challenges.map((c) => ({ ...c, description: null, createdAt: "2026-09-24T10:01:00Z" })),
    capabilities: { createChallenge: AVAILABLE, addMember: AVAILABLE },
  };
}

function detail(openSession: object = NO_OPEN, grant: object = AVAILABLE) {
  return {
    kind: "ok",
    workspace: WORKSPACE,
    challenge: { challengeId: CH, title: "Why signups dropped", description: "Understand before changing.", createdAt: "2026-09-24T10:01:00Z" },
    sessions: [{ sessionId: SID, state: "DRAFT", version: 1, createdAt: "2026-09-24T10:02:03Z" }],
    sessionControllers: [
      {
        bindingId: "b1",
        holderUserId: "u-fac",
        holderName: "Facilitator Fay",
        authorityClass: "SESSION_CONTROL_RIGHT",
        scope: `CHALLENGE:${CH}`,
        grantedByUserId: "u-root",
        grantedByName: "Root",
        grantedAt: "2026-09-24T10:01:30Z",
      },
    ],
    members: [
      { userId: "u-root", name: "Root", email: "root@nonproof.test", role: "Owner" },
      { userId: "u-fac", name: "Facilitator Fay", email: "fay@nonproof.test", role: "Facilitator" },
    ],
    capabilities: { openSession, grantSessionControl: grant },
  };
}

async function authenticated(page: Page): Promise<void> {
  await page.route(`${API}/auth/me`, (route) => route.fulfill({ json: { kind: "ok", userId: "u-root" } }));
}

/** A route whose response is released by the test (to observe REQUESTED / reconstruction reading). */
function gate(): { hold: (route: Route) => Promise<void>; release: (fulfil: (route: Route) => Promise<void>) => Promise<void> } {
  let pending: Route | null = null;
  let arrived: () => void = () => undefined;
  const arrival = new Promise<void>((resolve) => (arrived = resolve));
  return {
    hold: async (route) => {
      pending = route;
      arrived();
    },
    release: async (fulfil) => {
      await arrival;
      await fulfil(pending as unknown as Route);
    },
  };
}

async function workspacePage(page: Page, governanceCapable = true): Promise<{ overviewReads: () => number }> {
  let reads = 0;
  await authenticated(page);
  await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation(governanceCapable) }));
  await page.route(`${API}/workspaces/${WS}/overview`, (route) => {
    reads += 1;
    return route.fulfill({ json: overview() });
  });
  return { overviewReads: () => reads };
}

const outcome = (page: Page) => page.getByTestId("command-outcome");
const trace = (page: Page) => page.getByRole("navigation", { name: "Inquiry position" });

test.describe("isolation", () => {
  test("an unmocked API call cannot reach any running backend (fails closed)", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces`, (route) => route.fulfill({ json: { kind: "ok", workspaces: [] } }));
    await page.goto("/workspaces");
    const reached = await page.evaluate(async (api) => {
      try {
        await fetch(`${api}/healthz`);
        return true;
      } catch {
        return false;
      }
    }, API);
    expect(reached).toBe(false);
  });
});

test.describe("position (CF-01/CF-02, 21 §12)", () => {
  test("Challenge: trace comes from the projection; Session is only a relation, never a place", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);

    const items = trace(page).getByRole("listitem");
    await expect(items).toHaveCount(4);
    await expect(items.nth(0)).toHaveAttribute("data-status", "established");
    await expect(items.nth(1)).toHaveAttribute("data-coordinate", "workspace");
    await expect(items.nth(2)).toHaveAttribute("aria-current", "location");
    await expect(items.nth(2)).toContainText("Why signups dropped");
    await expect(items.nth(3)).toHaveAttribute("data-status", "unavailable");
    await expect(items.nth(3)).toContainText("not available now");
    await expect(items.nth(3).getByRole("link")).toHaveCount(0);
    await expect(trace(page).locator('[data-coordinate="session-state"]')).toHaveCount(0);
    // The current coordinate is not a link; established parents are.
    await expect(trace(page).getByRole("link", { name: "Field inquiry" })).toHaveAttribute("href", `/workspaces/${WS}`);
    await expect(items.nth(2).getByRole("link")).toHaveCount(0);
  });

  test("while the Challenge is unconfirmed, the trace holds only the confirmed access context", async ({ page }) => {
    await authenticated(page);
    const held = gate();
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, held.hold);
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await expect(page.getByTestId("challenge-loading")).toBeVisible();
    await expect(trace(page).getByRole("listitem")).toHaveCount(1);
    await expect(trace(page)).not.toContainText("Challenge");
    await expect(trace(page)).not.toContainText("Session");
    await held.release((route) => route.fulfill({ json: detail() }));
    await expect(trace(page).getByRole("listitem")).toHaveCount(4);
  });

  test("NOT_FOUND reconstructs to the nearest confirmed context and invents no replacement", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) =>
      route.fulfill({ status: 404, json: { kind: "not_found", reasonCode: "CHALLENGE_NOT_FOUND" } }),
    );
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await expect(page.getByTestId("load-failure")).toHaveAttribute("data-outcome", "not_found");
    await expect(page.getByTestId("load-failure")).toContainText("not available in the confirmed scope");
    await expect(trace(page).getByRole("listitem")).toHaveCount(1);
    await expect(page.getByRole("heading", { level: 1 })).toHaveCount(0);
  });

  test("Workspace: the Challenge relation is possible only when projected; no Session coordinate exists", async ({ page }) => {
    await workspacePage(page);
    await page.goto(`/workspaces/${WS}`);
    const items = trace(page).getByRole("listitem");
    await expect(items).toHaveCount(3);
    await expect(items.nth(1)).toHaveAttribute("aria-current", "location");
    await expect(items.nth(2)).toHaveAttribute("data-status", "possible");
    await expect(items.nth(2).getByRole("link")).toHaveCount(0);
    await expect(trace(page).locator('[data-coordinate="session"], [data-coordinate="session-state"]')).toHaveCount(0);
  });

  test("an existing Session is named by server projection (state, opening time), not a client ordinal", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const list = page.getByTestId("sessions-list");
    await expect(list.getByRole("link")).toContainText("Session opened");
    await expect(list).not.toContainText("Session 1");
    await expect(list.locator('[data-origin="system-state"]')).toContainText("DRAFT");
  });
});

test.describe("affordance (CF-07)", () => {
  test("an unavailable relation renders the server reason and no control (no disabled authority button)", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await expect(page.getByRole("button", { name: "Open Session" })).toHaveCount(0);
    await expect(page.getByTestId("session-create-unavailable")).toContainText("SESSION_CONTROL_RIGHT");
  });
});

test.describe("effect lifecycle (CF-08, 21 §17)", () => {
  test("REQUESTED is not COMMITTED: canonical state unchanged and no outcome until the server answers", async ({ page }) => {
    await workspacePage(page, false);
    const held = gate();
    await page.route(`${API}/workspaces/${WS}/challenges`, held.hold);
    await page.route(`${API}/workspaces/${WS}/challenges/new-ch`, (route) =>
      route.fulfill({ json: { ...detail(), challenge: { ...detail().challenge, challengeId: "new-ch", title: "Fresh" } } }),
    );
    await page.goto(`/workspaces/${WS}`);
    await page.getByLabel("Challenge title").fill("Fresh");
    await page.getByRole("button", { name: "Create Challenge" }).click();

    await expect(page.getByTestId("effect-requested")).toContainText("Not yet committed");
    await expect(page.getByTestId("challenges-empty")).toBeVisible();
    await expect(outcome(page)).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Create Challenge" })).toBeDisabled();

    await held.release((route) => route.fulfill({ json: { kind: "committed", challengeId: "new-ch" } }));
    await expect(page).toHaveURL(new RegExp(`/challenges/new-ch$`));
  });

  test("C3-01: network loss on a keyed Command → unknown consequence, re-read, same Idempotency-Key on repeat", async ({ page }) => {
    const reads = await workspacePage(page, false);
    const keys: string[] = [];
    let attempt = 0;
    await page.route(`${API}/workspaces/${WS}/challenges`, (route: Route, request: Request) => {
      keys.push(request.headers()["idempotency-key"] ?? "");
      attempt += 1;
      return attempt === 1 ? route.abort("connectionreset") : route.fulfill({ json: { kind: "committed", challengeId: "c2" } });
    });
    await page.route(`${API}/workspaces/${WS}/challenges/c2`, (route) => route.fulfill({ json: detail() }));
    await page.goto(`/workspaces/${WS}`);
    await expect(page.getByTestId("challenges-empty")).toBeVisible();
    const readsBefore = reads.overviewReads();

    await page.getByLabel("Challenge title").fill("Lost response");
    await page.getByRole("button", { name: "Create Challenge" }).click();

    await expect(outcome(page)).toHaveAttribute("data-outcome", "network_failure");
    await expect(outcome(page)).toHaveAttribute("data-consequence", "unknown");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await expect(outcome(page)).toContainText("unknown whether the change was made");
    await expect(outcome(page)).not.toContainText(/nothing (is assumed to have )?changed|no change was made/i);
    expect(reads.overviewReads()).toBeGreaterThan(readsBefore);

    await page.getByRole("button", { name: "Create Challenge" }).click();
    await expect(page).toHaveURL(/\/challenges\/c2$/);
    expect(keys).toHaveLength(2);
    expect(keys[0]).toMatch(/^[0-9a-f-]{36}$/);
    expect(keys[1]).toBe(keys[0]);
  });

  test("server INDETERMINATE retains the intent; a definitive outcome releases it", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail(AVAILABLE) }));
    const keys: string[] = [];
    const answers = [
      { status: 503, json: { kind: "indeterminate", reasonCode: "PRIOR_ATTEMPT_UNRESOLVED" } },
      { status: 403, json: { kind: "denied", reasonCode: "BND_005_NO_AUTHORITY" } },
      { status: 403, json: { kind: "denied", reasonCode: "BND_005_NO_AUTHORITY" } },
    ];
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}/sessions`, (route, request) => {
      keys.push(request.headers()["idempotency-key"] ?? "");
      return route.fulfill(answers[keys.length - 1]);
    });
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const open = page.getByRole("button", { name: "Open Session" });

    await open.click();
    await expect(outcome(page)).toHaveAttribute("data-outcome", "indeterminate");
    await expect(outcome(page)).toHaveAttribute("data-consequence", "unknown");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await open.click();
    await expect(outcome(page)).toHaveAttribute("data-outcome", "denied");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await open.click();
    await expect.poll(() => keys.length).toBe(3);
    expect(keys[1]).toBe(keys[0]);
    expect(keys[2]).not.toBe(keys[1]);
  });

  test("the commit marker claims a re-read only after the re-read happened", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation(true) }));
    let reads = 0;
    const held = gate();
    await page.route(`${API}/workspaces/${WS}/overview`, (route) => {
      reads += 1;
      return reads === 1 ? route.fulfill({ json: overview() }) : held.hold(route);
    });
    await page.route(`${API}/workspaces/${WS}/members`, (route) => route.fulfill({ json: { kind: "ok" } }));
    await page.goto(`/workspaces/${WS}`);
    await page.getByLabel("Member user id").fill("44444444-4444-4444-8444-444444444444");
    await page.getByRole("button", { name: "Add member" }).click();

    await expect(outcome(page)).toHaveAttribute("data-outcome", "committed");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "reading");
    await expect(outcome(page)).not.toContainText("was re-read");
    await expect(page.getByRole("button", { name: "Add member" })).toBeDisabled();

    await held.release((route) => route.fulfill({ json: overview() }));
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await expect(outcome(page)).toContainText("The state shown was re-read from the canonical source.");
    await expect(page.getByRole("button", { name: "Add member" })).toBeEnabled();
  });

  test("C3-06: committed but not re-readable stays committed, marks the view last-confirmed, blocks dependent effects", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}`, (route) => route.fulfill({ json: orientation(true) }));
    let reads = 0;
    await page.route(`${API}/workspaces/${WS}/overview`, (route) => {
      reads += 1;
      return reads === 2 ? route.abort("connectionreset") : route.fulfill({ json: overview() });
    });
    await page.route(`${API}/workspaces/${WS}/members`, (route) => route.fulfill({ json: { kind: "ok" } }));
    await page.goto(`/workspaces/${WS}`);
    await page.getByLabel("Member user id").fill("44444444-4444-4444-8444-444444444444");
    await page.getByRole("button", { name: "Add member" }).click();

    await expect(outcome(page)).toHaveAttribute("data-outcome", "committed");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "failed");
    await expect(outcome(page)).toContainText("The change committed, but the current state could not be re-read");
    await expect(outcome(page)).not.toContainText(/no change|unchanged|did not commit/i);
    await expect(page.getByTestId("projection-last-confirmed")).toBeVisible();
    await expect(page.getByRole("button", { name: "Add member" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Create Challenge" })).toBeDisabled();

    await page.getByRole("button", { name: "Re-read current state" }).click();
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await expect(page.getByTestId("projection-last-confirmed")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Add member" })).toBeEnabled();
  });

  test("keyless F01 founding: network loss → unknown, list re-read, never an invitation to try again", async ({ page }) => {
    await authenticated(page);
    let lists = 0;
    await page.route(`${API}/workspaces`, (route, request) => {
      if (request.method() === "POST") return route.abort("connectionreset");
      lists += 1;
      return route.fulfill({ json: { kind: "ok", workspaces: [] } });
    });
    await page.goto("/workspaces");
    await expect(page.getByTestId("workspaces-empty")).toBeVisible();
    await page.getByLabel("Workspace name").fill("Maybe founded");
    await page.getByRole("button", { name: "Create Workspace" }).click();

    await expect(outcome(page)).toHaveAttribute("data-outcome", "network_failure");
    await expect(outcome(page)).toHaveAttribute("data-consequence", "unknown");
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    expect(lists).toBe(2);
    await expect(page.locator("main")).not.toContainText(/try again/i);
  });

  test("an unrecognized response to a Command is INDETERMINATE, never a failure", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces`, (route, request) =>
      request.method() === "POST"
        ? route.fulfill({ status: 500, contentType: "text/plain", body: "Internal Server Error" })
        : route.fulfill({ json: { kind: "ok", workspaces: [] } }),
    );
    await page.goto("/workspaces");
    await page.getByLabel("Workspace name").fill("Unclear");
    await page.getByRole("button", { name: "Create Workspace" }).click();
    await expect(outcome(page)).toHaveAttribute("data-outcome", "indeterminate");
    await expect(outcome(page)).toHaveAttribute("data-consequence", "unknown");
  });
});

test.describe("boundary taxonomy (21 §14, falsifiers 21/22)", () => {
  const cases = [
    { status: 403, json: { kind: "denied", reasonCode: "NOT_GOVERNANCE_ROOT" }, consequence: "none", title: "not permitted" },
    { status: 400, json: { kind: "rejected", reasonCode: "MALFORMED_HUMAN_USER_ID" }, consequence: "none", title: "cannot be accepted" },
    { status: 409, json: { kind: "failed_precommit", reasonCode: "EFFECT_GATE_ROLLBACK" }, consequence: "none", title: "did not commit" },
    { status: 503, json: { kind: "indeterminate", reasonCode: "COMMIT_OUTCOME_UNPROVEN" }, consequence: "unknown", title: "cannot currently determine" },
  ] as const;

  for (const c of cases) {
    test(`grant → ${c.json.kind} is its own boundary`, async ({ page }) => {
      await authenticated(page);
      await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
      await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) => route.fulfill({ status: c.status, json: c.json }));
      await page.goto(`/workspaces/${WS}/challenges/${CH}`);
      await page.getByLabel("Grant session control to").selectOption("u-fac");
      await page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
      await expect(outcome(page)).toHaveAttribute("data-outcome", c.json.kind);
      await expect(outcome(page)).toHaveAttribute("data-consequence", c.consequence);
      await expect(outcome(page)).toContainText(c.title);
      await expect(outcome(page)).toContainText(c.json.reasonCode);
      await expect(outcome(page)).toHaveAttribute("role", "alert");
    });
  }
});

test.describe("proof depth (CF-09, 21 §40)", () => {
  test("authority proof is closed by default, opens in place by keyboard, and keeps position", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    const proof = page.getByTestId("challenge-authority-proof");
    await expect(proof).not.toHaveAttribute("open", "");
    await expect(page.getByTestId("challenge-authority-list")).toBeHidden();

    const summary = proof.locator("summary");
    // 21 §35: proof is an explicit, visibly openable activation target (not hover, not a bare heading).
    const marker = () => summary.evaluate((el) => getComputedStyle(el, "::before").content);
    const closedMarker = await marker();
    expect(closedMarker).not.toMatch(/^(none|normal)$/);
    await summary.focus();
    await page.keyboard.press("Enter");
    await expect.poll(marker).not.toBe(closedMarker);
    await expect(page.getByTestId("challenge-authority-list")).toBeVisible();
    await expect(page.getByTestId("challenge-authority-list")).toContainText("granted by Root");
    await expect(summary).toBeFocused();
    await expect(page).toHaveURL(new RegExp(`/challenges/${CH}$`));
    await expect(trace(page).locator('[aria-current="location"]')).toContainText("Why signups dropped");
  });
});

test.describe("responsive + motion (21 §33, §34)", () => {
  test("DOM and visual order follow the relation: position → active relation → affordance → proof; nothing overflows", async ({ page }) => {
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail(AVAILABLE) }));
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Why signups dropped");

    const top = async (selector: string) => (await page.locator(selector).first().boundingBox())?.y ?? Number.NaN;
    const y = {
      trace: await top('nav[aria-label="Inquiry position"]'),
      heading: await top("h1"),
      centre: await top('[data-field-zone="centre"]'),
      near: await top('[data-field-zone="near"]'),
      depth: await top('[data-field-zone="depth"]'),
    };
    expect(y.trace).toBeLessThan(y.heading);
    expect(y.heading).toBeLessThan(y.centre);
    if ((page.viewportSize()?.width ?? 1280) <= 860) {
      expect(y.centre).toBeLessThan(y.near);
      expect(y.near).toBeLessThan(y.depth);
    }
    await expect(page.getByTestId("challenge-authority-proof").locator("summary")).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
  });

  test("reduced motion removes animation but not meaning", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await authenticated(page);
    await page.route(`${API}/workspaces/${WS}/challenges/${CH}`, (route) => route.fulfill({ json: detail() }));
    await page.route(`${API}/workspaces/${WS}/authority-bindings`, (route) =>
      route.fulfill({ json: { kind: "committed", commitId: "c" } }),
    );
    await page.goto(`/workspaces/${WS}/challenges/${CH}`);
    await page.getByLabel("Grant session control to").selectOption("u-fac");
    await page.getByRole("button", { name: "Grant session control for this Challenge" }).click();
    await expect(outcome(page)).toHaveAttribute("data-reconstruction", "done");
    await expect(outcome(page)).toContainText("Committed.");
    await expect(outcome(page)).toHaveAttribute("role", "status");
    const animation = await outcome(page).evaluate((el) => getComputedStyle(el).animationName);
    expect(animation).toBe("none");
  });
});
