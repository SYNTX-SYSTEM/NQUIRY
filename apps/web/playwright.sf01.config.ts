/**
 * SF-01 ISOLATED component-contract lane (MOCKED browser; not runtime proof).
 *
 * Why a separate config (SF-01 human decision 2, runbook §22 caution): the
 * default `playwright.config.ts` reuses whatever serves `:3000`, and while
 * F03 is in progress that is the F03 environment's `web` container, not this
 * tree. This lane therefore:
 *
 * - starts its OWN Next dev server from this tree on `:3301`
 *   (`reuseExistingServer: false`, so it never adopts a foreign server);
 * - sends every request that a spec did not fulfil with `page.route()` to a
 *   dead proxy (`127.0.0.1:9`). Playwright's Chromium proxies loopback when a
 *   proxy is set, so an unmocked call to `localhost:8000` (where the F03 API may
 *   be running) fails closed as a network failure instead of reaching it. Only
 *   this lane's own web server is bypassed. Proven by
 *   `sf01-field.spec.ts` › "isolation".
 *
 * Projects: every mocked spec on desktop (F01/F02 regression + SF-01), and the
 * SF-01 specs again on a phone viewport.
 */
import { defineConfig, devices } from "@playwright/test";

const PORT = 3301;
const BASE_URL = `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: BASE_URL,
    proxy: { server: "http://127.0.0.1:9", bypass: `localhost:${PORT}` },
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 860 } } },
    { name: "mobile", testMatch: /sf0[1345]-.*\.spec\.ts$/, use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: `npx next dev -p ${PORT}`,
    url: BASE_URL,
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
