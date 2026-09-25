// SF-05 (WU-26.11) performance probe = the SF-04 probe + the doc 26 layers (node breathing, chamber contours, dense stars)
// SF-04 (WU-12) performance probe = the SF-02/SF-03 perf-ab reconstruction, extended to the organism's layers.
// Real Chromium, CDP Emulation.setCPUThrottlingRate (THROTTLE, default 4), a `next dev` page server (BASE)
// whose /api/* calls are forwarded by Playwright route interception to the isolated inspection API (API).
// Per variant: rAF cadence (median / p90 of 40 frames) on the Access Field, the Workspaces Field and — new —
// the Challenge Field (currents, core anatomy, node auras, organ, atmosphere), plus click actionability times.
// Variants inject CSS to isolate one cost at a time (doc 25 §19: measure, do not assume).
//
// Usage: BASE=http://localhost:3341 API=http://127.0.0.1:13400 WS=<ws> CH=<ch> THROTTLE=4 node perf-ab.mjs
import { chromium } from "@playwright/test";
const BASE = process.env.BASE ?? "http://localhost:3341";
const API = process.env.API ?? "http://127.0.0.1:13400";
const RATE = Number(process.env.THROTTLE ?? 4);
const WS = process.env.WS;
const CH = process.env.CH;
const VARIANTS = {
  "A full": "",
  "B no background": ".field-bg{display:none!important}",
  "C no core layers": ".core-aura,.core-rings,.core-membrane,.core-orbit-trace{display:none!important}",
  "D no currents": ".current-pulse,.endpoint{display:none!important}",
  "E no node auras": ".node-aura{display:none!important}",
  "F no atmosphere": ".stage-atmosphere{display:none!important}",
  "G no organism anim": ".core-aura,.core-ring,.core-membrane,.core-orbit-dot,.current-pulse,.route-membrane{animation:none!important}",
  "H static everything": "*,*::before,*::after{animation:none!important;transition:none!important}",
  "I no node breathing": ".node-aura{animation:none!important}",
  "J no chamber contours": ".chamber-contour,.plane.chamber::after{display:none!important}",
  "K no dense stars": ".particles-dense{display:none!important}",
};
const cadence = (p) => p.evaluate(async () => { const t = []; let last = performance.now(); for (let i = 0; i < 40; i++) { await new Promise((r) => requestAnimationFrame(r)); const n = performance.now(); t.push(n - last); last = n; } t.sort((a, b) => a - b); return { median: Math.round(t[20] * 10) / 10, p90: Math.round(t[36] * 10) / 10 }; });
const b = await chromium.launch();
for (const [name, css] of Object.entries(VARIANTS)) {
  const ctx = await b.newContext({ viewport: { width: 1280, height: 860 }, baseURL: BASE });
  await ctx.route("**/api/**", async (route) => { const u = new URL(route.request().url()); const r = await route.fetch({ url: API + u.pathname + u.search }); await route.fulfill({ response: r }); });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p); await cdp.send("Emulation.setCPUThrottlingRate", { rate: RATE });
  await p.goto("/login"); await p.getByTestId("login-form").waitFor(); await p.waitForTimeout(2500);
  if (css) await p.addStyleTag({ content: css });
  await p.waitForTimeout(500);
  const access = await cadence(p);
  await p.getByLabel("Email").fill("facilitator@inspect.local.test"); await p.getByLabel("Password").fill("inspect-fac-2026");
  let t0 = Date.now(); await p.getByRole("button", { name: "Log in" }).click(); const loginClick = Date.now() - t0;
  await p.waitForURL(/\/workspaces/).catch(() => {}); await p.getByTestId("field-core").waitFor().catch(() => {});
  if (css) await p.addStyleTag({ content: css });
  await p.waitForTimeout(800);
  const workspaces = await cadence(p);
  let challenge = { median: null, p90: null }; let hoverMs = null;
  if (WS && CH) {
    await p.goto(`/workspaces/${WS}/challenges/${CH}`); await p.getByTestId("field-core").waitFor().catch(() => {});
    if (css) await p.addStyleTag({ content: css });
    await p.waitForTimeout(1200);
    challenge = await cadence(p);
    t0 = Date.now(); await p.locator("li.node").first().hover().catch(() => {}); hoverMs = Date.now() - t0;
  }
  t0 = Date.now(); await p.getByRole("button", { name: "Log out" }).click({ trial: true }).catch(() => {}); const trial = Date.now() - t0;
  console.log(`${name.padEnd(20)} access rAF ${access.median}/${access.p90} ms · login click ${loginClick} ms · workspaces rAF ${workspaces.median}/${workspaces.p90} ms · challenge rAF ${challenge.median}/${challenge.p90} ms · hover ${hoverMs} ms · trial click ${trial} ms`);
  await ctx.close();
}
await b.close();
