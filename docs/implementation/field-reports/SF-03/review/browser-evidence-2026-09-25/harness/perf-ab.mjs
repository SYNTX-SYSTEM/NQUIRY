// SF-02 D5 reconstruction (WU-SF02.7) reused for SF-03 (WU-SF03.3): cost of the living background under CPU throttling.
// Real Chromium, CDP Emulation.setCPUThrottlingRate (THROTTLE, default 4), a `next dev` page server (BASE)
// whose /api/* calls are forwarded by Playwright route interception to the isolated inspection API (API).
// Per variant: rAF cadence (median / p90 of 40 frames) on the Access Field and on the Workspaces Field, and
// Playwright click actionability time. Variants inject CSS to isolate one cost at a time.
//
// Measured 2026-09-25 on the pre-D5 tree (THROTTLE=4):
//   A full                 login rAF 96-110 ms · workspaces rAF 132-143 ms · clicks 300-650 ms
//   B no background        16.4 ms · 16.5 ms · 158-227 ms
//   C no drift rings       25.8 ms · 75.6 ms
//   D no breathe           102 ms  · 162 ms          E no backdrop blur   101 ms · 133 ms
//   J static rings + will-change   21 ms · 56 ms     L J + no core-breathe + no path-pulse  21 ms · 43 ms
// After the SF-02 repair (static rings, bounded opacity-only breathing layer, core glow by opacity, no backdrop-filter):
//   A repaired             16.6 ms · 29.4 ms · 90-166 ms
//
// SF-03 (THROTTLE=4, API=http://127.0.0.1:13200, dev server on :3341):
//   first draft (three 54–62 vmax animated nebular blobs)   login 30.2 / p90 39.0 ms · workspaces 23.5 / 45.0 ms
//   without nebula                                          16.0 / 22.4 · 16.5 / 23.6
//   reduced (two 46/40 vmax animated blobs + static haze)   16.3 / 22.6 · 19.2 / 29.1   ← shipped
//   without background                                      16.7 / 20.0 · 16.7 / 20.2
import { chromium } from "@playwright/test";
const BASE = process.env.BASE ?? "http://localhost:3341";
const API = process.env.API ?? "http://127.0.0.1:13300";
const RATE = Number(process.env.THROTTLE ?? 4);
const VARIANTS = {
  "A full": "",
  "B no background": ".field-bg{display:none!important}",
  "C no nebula": ".field-bg .nebula{display:none!important}",
  "D no particles": ".field-bg .particles{display:none!important}",
  "E no rail energy": ".trace li::before{animation:none!important}",
  "F no core glow anim": ".core::after{animation:none!important}",
  "G no path-pulse": ".orbit-paths .path{animation:none!important}",
};
const b = await chromium.launch();
for (const [name, css] of Object.entries(VARIANTS)) {
  const ctx = await b.newContext({ viewport: { width: 1280, height: 860 }, baseURL: BASE });
  await ctx.route("**/api/**", async (route) => { const u = new URL(route.request().url()); const r = await route.fetch({ url: API + u.pathname + u.search }); await route.fulfill({ response: r }); });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p); await cdp.send("Emulation.setCPUThrottlingRate", { rate: RATE });
  await p.goto("/login"); await p.getByTestId("login-form").waitFor(); await p.waitForTimeout(2500);
  if (css) await p.addStyleTag({ content: css });
  await p.waitForTimeout(500);
  const frame = await p.evaluate(async () => { const t = []; let last = performance.now(); for (let i = 0; i < 40; i++) { await new Promise((r) => requestAnimationFrame(r)); const n = performance.now(); t.push(n - last); last = n; } t.sort((a, b) => a - b); return { median: t[20].toFixed(1), p90: t[36].toFixed(1) }; });
  await p.getByLabel("Email").fill("facilitator@inspect.local.test"); await p.getByLabel("Password").fill("inspect-fac-2026");
  let t0 = Date.now(); await p.getByRole("button", { name: "Log in" }).click(); const loginClick = Date.now() - t0;
  await p.waitForURL(/\/workspaces/).catch(() => {}); await p.getByTestId("field-core").waitFor().catch(() => {});
  if (css) await p.addStyleTag({ content: css });
  await p.waitForTimeout(800);
  const frame2 = await p.evaluate(async () => { const t = []; let last = performance.now(); for (let i = 0; i < 40; i++) { await new Promise((r) => requestAnimationFrame(r)); const n = performance.now(); t.push(n - last); last = n; } t.sort((a, b) => a - b); return { median: t[20].toFixed(1), p90: t[36].toFixed(1) }; });
  t0 = Date.now(); await p.getByRole("button", { name: "Log out" }).click({ trial: true }).catch(() => {}); const trial = Date.now() - t0;
  console.log(`${name.padEnd(20)} login: rAF median ${frame.median}ms p90 ${frame.p90}ms · login click ${loginClick}ms · workspaces: rAF median ${frame2.median}ms p90 ${frame2.p90}ms · trial click ${trial}ms`);
  await ctx.close();
}
await b.close();
