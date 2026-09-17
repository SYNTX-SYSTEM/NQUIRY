import { defineConfig } from "@playwright/test";

/**
 * Skeleton only (14 §44 PHASE 0). No specs exist yet — architectural
 * E2E proof paths (human/AI distinction, Decision creation, Burst
 * protection) land in Phase 11.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
  },
});
