import type { NextConfig } from "next";

/**
 * PKG-00 SCOPE: toolchain shell only. No backend/database/authority
 * access is configured here — the frontend must reach the backend
 * only through a typed HTTP client calling `apps/api`
 * (14_IMPLEMENTATION_SEQUENCE.md §3.1: "frontend | Must not depend
 * on: DB, governance repository, authority resolver").
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
