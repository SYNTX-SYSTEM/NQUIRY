// Review-runtime AUTH fixture (runtime-only, FIXTURE_NON_PROOF). The pinned RED producer has no PURPLE
// /auth/sessions or /auth/methods, so the review runtime answers them with live-SHAPED bodies that CAUSALLY FOLLOW the
// transition that produced the state:
//   local login (POST /api/auth/login → 200)   → review state "local"  → current session LOCAL_PASSWORD
//   Google review transition (explicit form)   → review state "google" → current session GOOGLE_OIDC
//   logout                                     → review state cleared
//   no transition recorded                     → current session with methodType null (UNKNOWN; CYAN must not guess)
// The linked methods (LOCAL_PASSWORD + GOOGLE_OIDC, both ACTIVE) never decide the current method.
export const REVIEW_COOKIE = "nquiry_review_auth";
export const STATES = ["local", "google"];
const S_LOCAL = "bbbbbbbb-2222-4222-8222-222222222222";
const S_GOOGLE = "aaaaaaaa-2222-4222-8222-222222222222";
const S_UNKNOWN = "eeeeeeee-2222-4222-8222-222222222222";
const PROVIDER_EMAIL = "review-fixture@cy01.local.test";

/** The recorded transition, from the Cookie header: "local" | "google" | null (unknown). */
export function reviewState(cookieHeader) {
  const m = /(?:^|;\s*)nquiry_review_auth=([a-z]+)/.exec(cookieHeader ?? "");
  return m && STATES.includes(m[1]) ? m[1] : null;
}
export function transitionCookie(state) {
  if (state === null) return `${REVIEW_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax`;
  if (!STATES.includes(state)) throw new Error("unknown review state");
  return `${REVIEW_COOKIE}=${state}; Path=/; HttpOnly; SameSite=Lax`;
}
/** GET /auth/sessions for the recorded transition. */
export function sessionsBody(state) {
  const local = { sessionId: S_LOCAL, issuedAt: "2026-10-01T08:00:00+00:00", expiresAt: "2026-10-05T08:00:00+00:00", current: false, methodType: "LOCAL_PASSWORD" };
  const google = { sessionId: S_GOOGLE, issuedAt: "2026-10-03T18:00:00+00:00", expiresAt: "2026-10-05T18:00:00+00:00", current: false, methodType: "GOOGLE_OIDC" };
  if (state === "local") return { kind: "ok", sessions: [{ ...local, current: true }] };
  if (state === "google") return { kind: "ok", sessions: [local, { ...google, current: true }] };
  return { kind: "ok", sessions: [{ sessionId: S_UNKNOWN, issuedAt: "2026-10-03T18:00:00+00:00", expiresAt: "2026-10-05T18:00:00+00:00", current: true, methodType: null }] };
}
/** GET /auth/methods: the linked methods, independent of the transition (LINKED != CURRENT). */
export function methodsBody() {
  return { kind: "ok", methods: [
    { methodId: "cccccccc-2222-4222-8222-222222222222", methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: "2026-09-27T20:00:00+00:00", lastAuthenticatedAt: "2026-10-01T08:00:00+00:00", provider: null },
    { methodId: "dddddddd-2222-4222-8222-222222222222", methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: "2026-10-03T18:00:00+00:00", lastAuthenticatedAt: "2026-10-03T18:00:00+00:00", provider: { providerId: "google", email: PROVIDER_EMAIL } },
  ] };
}
