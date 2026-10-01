import { defineConfig } from "@playwright/test";

/**
 * AUTH Field (PURPLE) MOCKED-browser lane: the authentication specs against a
 * Next.js dev server of THIS working tree on its own port.
 *
 * The default lane (`playwright.config.ts`) uses `:3000` with
 * `reuseExistingServer`, so it tests whatever already serves `:3000`
 * (RUNTIME_OPERATION §22 caution). This lane never reuses a server. API
 * responses are fulfilled by `page.route()`: component/contract proof only,
 * never runtime proof (20 §12).
 */
const PORT = Number(process.env.AUTH_WEB_PORT ?? 13460);

export default defineConfig({
  testDir: "./tests/e2e",
  // AUTH_SPEC_MATCH=".*" runs every mocked spec on this port (preservation check).
  testMatch: new RegExp(process.env.AUTH_SPEC_MATCH ?? "(auth|account-security|account-security-methods|oidc-login|verify-email|recover)\\.spec\\.ts$"),
  fullyParallel: true,
  reporter: "list",
  outputDir: "./test-results/auth-mocked",
  use: { baseURL: `http://localhost:${PORT}` },
  webServer: {
    command: `npx next dev --port ${PORT}`,
    url: `http://localhost:${PORT}/login`,
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
