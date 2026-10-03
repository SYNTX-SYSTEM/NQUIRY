import type { NextConfig } from "next";
import { normalizeMount } from "./lib/field/mount";

/**
 * PKG-00 SCOPE: toolchain shell only. No backend/database/authority
 * access is configured here — the frontend must reach the backend
 * only through a typed HTTP client calling `apps/api`
 * (14_IMPLEMENTATION_SEQUENCE.md §3.1: "frontend | Must not depend
 * on: DB, governance repository, authority resolver").
 *
 * CYAN_REAL_E2E_FIELD_MOUNT_01: the FRONTEND MOUNT. `NEXT_PUBLIC_FRONTEND_MOUNT`
 * (default "", the origin root) becomes Next's `basePath`, so page routes, the
 * app router and `next/link` live beneath the mount; the same value is inlined
 * for the two CYAN-owned root references (`lib/field/mount.ts`). The API mount
 * (`NEXT_PUBLIC_API_BASE_URL`) is untouched: FRONTEND_MOUNT != API_MOUNT.
 */
const mount = normalizeMount(process.env.NEXT_PUBLIC_FRONTEND_MOUNT);

const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(mount === "" ? {} : { basePath: mount }),
};
export default nextConfig;
