/**
 * CYAN_REAL_E2E_FIELD_MOUNT_01: the FRONTEND MOUNT — the one CYAN-owned location relation.
 *
 *   ORIGIN → FRONTEND MOUNT (M) → CYAN page routes · internal navigation · CYAN static assets · CYAN-owned auth return target
 *   ORIGIN → API MOUNT (/api, `NEXT_PUBLIC_API_BASE_URL`) → PURPLE (sessions, methods, providers, OIDC callback)
 *
 * M is "" for the default build (the origin root) and e.g. "/cy-review" for a staged review build on the same
 * origin. It is fixed at build time from `NEXT_PUBLIC_FRONTEND_MOUNT`, read here once; `next.config.ts` derives
 * `basePath` from the same value, so routes, `next/link` and the app router are prefixed by Next itself, and the two
 * remaining CYAN-owned root references (the brand asset, the auth return target) derive from `mountPath`.
 *
 * FRONTEND_MOUNT != API_MOUNT: nothing under `lib/api` may read this module; a mount of "/api" or beneath it is
 * refused. Authentication truth never depends on M (PURPLE owns it); the Google callback never moves beneath M.
 */

const SEGMENT = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;

/** "" or "/seg(/seg)*": one leading slash, no trailing slash, safe segments, never the API mount. */
export function normalizeMount(raw: string | undefined): string {
  const value = (raw ?? "").trim();
  if (value === "" || value === "/") return "";
  if (!value.startsWith("/") || value.endsWith("/")) throw new Error(`NEXT_PUBLIC_FRONTEND_MOUNT must be "" or "/segment(/segment)*", got ${JSON.stringify(value)}`);
  const segments = value.slice(1).split("/");
  if (!segments.every((s) => SEGMENT.test(s))) throw new Error(`NEXT_PUBLIC_FRONTEND_MOUNT has an unsafe segment: ${JSON.stringify(value)}`);
  if (segments[0] === "api") throw new Error("NEXT_PUBLIC_FRONTEND_MOUNT must not be the API mount (FRONTEND_MOUNT != API_MOUNT)");
  return value;
}

/** The build's frontend mount (inlined by Next at build time). */
export const FRONTEND_MOUNT: string = normalizeMount(process.env.NEXT_PUBLIC_FRONTEND_MOUNT);

/** A CYAN-owned path beneath the mount: mountPath("/brand/x.png") → "/cy-review/brand/x.png" or "/brand/x.png". */
export function mountPath(path: `/${string}`): string {
  return `${FRONTEND_MOUNT}${path}`;
}
