/**
 * REAL-STACK browser lane (F02 WU-02.5; 20_SYSTEM_FIELD_ENGINEERING.md §12).
 *
 * Real Chromium -> real Next.js web app (:3000) -> real FastAPI (:8000)
 * -> real local auth -> real PostgreSQL with migrations -> real governed
 * Commands. No `page.route()`, no fulfilled responses, no raw inserts
 * simulating governed effects. The only out-of-band setup is HD-3's
 * DEV-ONLY identity provisioning (identity rows only, no authority).
 *
 * The stack must already be running (see `scripts/run_real_stack_e2e.sh`
 * at repository root). `globalSetup` fails closed if it is not, and
 * refuses to run if any spec in this lane contains network mocking.
 */
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/real-stack",
  testMatch: /.*\.real\.spec\.ts$/,
  globalSetup: "./tests/real-stack/global-setup.ts",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: [["list"]],
  use: {
    baseURL: process.env.REAL_STACK_WEB_URL ?? "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 860 } } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
