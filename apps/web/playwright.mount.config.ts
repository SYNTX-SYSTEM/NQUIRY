import { defineConfig, devices } from "@playwright/test";

/**
 * CYAN_REAL_E2E_FIELD_MOUNT_01: the REVIEW MOUNT lane. The same app, built/served with
 * NEXT_PUBLIC_FRONTEND_MOUNT=/cy-review (STATE B), on its own port; `reuseExistingServer: false` so a foreign
 * server is never adopted. Specs navigate to explicit `/cy-review/...` paths; the API stays `http://localhost:8000`.
 */
const PORT = 3302;
const BASE_URL = `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /mount-.*\.spec\.ts$/,
  fullyParallel: true,
  reporter: "list",
  use: { baseURL: BASE_URL },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 860 } } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: `npx next dev -p ${PORT}`,
    url: `${BASE_URL}/cy-review/login`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { NEXT_PUBLIC_FRONTEND_MOUNT: "/cy-review", NEXT_PUBLIC_API_BASE_URL: "http://localhost:8000" },
  },
});
