import { defineConfig } from "@playwright/test";

/**
 * PKG-28 (Phase 11): real E2E specs against a real Next.js dev server
 * + a real Chromium browser, using `page.route()` network-layer
 * interception to simulate the `SessionReadResult` shapes a real
 * backend route does not exist to produce yet (`apps/api` still only
 * has `/healthz` -- see `lib/api/client.ts`'s own header docstring).
 * `webServer` boots the real app so these specs exercise real
 * rendering, not a hand-rolled test harness.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
