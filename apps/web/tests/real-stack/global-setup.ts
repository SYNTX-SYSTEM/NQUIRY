import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";

const API = process.env.REAL_STACK_API_URL ?? "http://localhost:8000";
const WEB = process.env.REAL_STACK_WEB_URL ?? "http://localhost:3000";

// Fail closed: this lane's whole claim is "no mocking". A spec that
// intercepts the network cannot be allowed to run under this label.
const FORBIDDEN = [/\bpage\.route\s*\(/, /\bcontext\.route\s*\(/, /\broute\.fulfill\s*\(/, /\brouteFromHAR\s*\(/];

export default async function globalSetup(): Promise<void> {
  const dir = path.dirname(new URL(import.meta.url).pathname);
  for (const file of readdirSync(dir)) {
    if (!file.endsWith(".ts") || file === "global-setup.ts") continue;
    const source = readFileSync(path.join(dir, file), "utf8");
    for (const pattern of FORBIDDEN) {
      if (pattern.test(source)) {
        throw new Error(`REAL_STACK_LANE_VIOLATION: ${file} uses network mocking (${pattern})`);
      }
    }
  }
  for (const [label, url] of [
    ["api", `${API}/healthz`],
    ["web", `${WEB}/login`],
  ] as const) {
    let ok = false;
    try {
      ok = (await fetch(url)).ok;
    } catch {
      ok = false;
    }
    if (!ok) {
      throw new Error(`REAL_STACK_NOT_RUNNING: ${label} not reachable at ${url} (start it with scripts/run_real_stack_e2e.sh)`);
    }
  }
}
