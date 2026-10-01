/**
 * AUTH REAL-STACK browser lane (WU-AUTH-14; 20 §12). Real Chromium → real
 * Next.js app of THIS working tree (:13470) → real FastAPI (:18460) → real
 * PostgreSQL; a hostile third origin (:13471) for the anti-CSRF proof. No
 * mocking (the shared real-stack global setup refuses it). The stack is
 * started by `scripts/auth_real_stack.sh` at the repository root.
 */
import { defineConfig, devices } from "@playwright/test";

const WEB = process.env.REAL_STACK_WEB_URL ?? "http://localhost:13470";

export default defineConfig({
  testDir: "./tests/real-stack",
  // Anchored on the file name (the working tree's own path contains "auth-").
  // AUTH_REAL_SPEC_MATCH=".*" runs every real-stack spec on this stack (preservation).
  testMatch: new RegExp(`(^|/)${process.env.AUTH_REAL_SPEC_MATCH ?? "auth-[^/]*"}\\.real\\.spec\\.ts$`),
  globalSetup: "./tests/real-stack/global-setup.ts",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: [["list"]],
  outputDir: "test-results/auth-real",
  use: { baseURL: WEB, trace: "retain-on-failure" },
  projects: [{ name: "desktop", use: { ...devices["Desktop Chrome"] } }],
});
