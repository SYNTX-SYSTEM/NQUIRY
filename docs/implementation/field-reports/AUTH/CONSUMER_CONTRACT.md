# PURPLE → CONSUMER CONTRACT (post HD-AUTH-08, extended for HD-AUTH-10 and HD-AUTH-13)

Producer: `auth-identity` (this branch); live api = assembly
`auth-28e6620-20261005T152356Z` (product `28e6620`, migration head
`e3a5c7d9f1b4`, WU-AUTH-19/20 + WU-AUTHZ-01); the next assembly carries
WU-AUTH-21 (`d03d5ce`, HD-AUTH-10: self-service recovery through verified
e-mail, production mail delivery, `GET /auth/contacts`; no migration). Written 2026-10-04 for the frontend lineage (CYAN,
`frontend-symbiotic`) whose FIELD_RECONSTRUCTION_HOLD (`618d7a6`) waits for
"PURPLE's reconstructed production Field, provider-bootstrap behaviour,
identity presentation contract and real runtime proof". This document is that
statement. It adds no contact and changes no shape; every line names code that
exists on this branch and a proof that ran.

## 1. What changed upstream, and what did not

| Relation | Before (CYAN consumed `2ec05c0`) | Now (`e069fc1`, live) |
|---|---|---|
| `GET /auth/identity` shape and derivation | `{kind, userId, displayName, canonicalEmail}` = `users.name`, `users.email` of the session's identity | **unchanged** (`packages/application/identity_presentation.py`, `http_identity.py`) |
| Presentation across the sessions of ONE identity | identical for every method | **unchanged** — method-invariant *per identity* (`tests/e2e/test_auth_identity_presentation.py` FALSIFIER_01/03/15/16) |
| Which identity a provider LOGIN resolves to | bound subject → the bound identity; unbound → `ACCOUNT_CREATION_POLICY_UNRESOLVED` (DENIED everywhere in production) | bound subject → the bound identity; **unbound subject → a NEW identity bootstrapped from the provider claims** when the environment's policy is `SELF_REGISTRATION_ALLOWED` (production since HD-AUTH-08) |
| `users.name` / `users.email` of a bootstrapped identity | — | copied once from the provider `name` and verified `email` claims (`nameSource PROVIDER_DISPLAY_NAME_CLAIM`, `emailSource PROVIDER_VERIFIED_EMAIL_CLAIM`); no local-part derivation; missing name → login refused (`PROVIDER_PROFILE_INCOMPLETE` → `/login?auth=unavailable`) |
| Authority of a bootstrapped identity | — | none (`workspaceAuthority NONE`): no membership, role, binding; it may found its own workspace like every identity (HARD-DEP-001 Option A) |
| Everything else CYAN consumes (`/auth/me`, `/auth/providers`, `/auth/methods`, `/auth/sessions`, logout, link, unlink, revoke, logout-all, `?auth=` / `?link=` projections) | | **unchanged** |

Consequence for the stale CYAN expectation "LOCAL_PASSWORD identity =
GOOGLE_OIDC identity": it is **not universal and never was a law**; it is the
LINKED case. The three cases a consumer meets are:

| Case | How it arises | `/auth/me` userId | `/auth/identity` | `/auth/methods` |
|---|---|---|---|---|
| LOCAL | local password login | identity A | A's name / email | A's methods |
| GOOGLE_LINKED | A linked the subject (`link/start` from A's live session), later Google login | identity A (same) | **same** as LOCAL | LOCAL_PASSWORD + GOOGLE_OIDC(provider email) |
| GOOGLE_BOOTSTRAP | unbound subject logs in under `SELF_REGISTRATION_ALLOWED` | **new** identity B | B's name = provider display name, B's email = provider verified email | GOOGLE_OIDC only |

A consumer's invariants therefore are: (i) presentation is a function of
`userId` only — never of the current method; (ii) the same-principal guard
(`/auth/identity.userId == /auth/me.userId`) stays mandatory; (iii) nothing
in the identity field carries role, membership or authority. CYAN's F3/F4
tests remain valid *as the GOOGLE_LINKED case*; the review guide's
"CASE GOOGLE → SAME name, SAME canonical email" is true only for a linked
subject and must be split into GOOGLE_LINKED and GOOGLE_BOOTSTRAP.

## 2. Live proof (production, read-only, redacted)

| Relation | Proven | Evidence |
|---|---|---|
| REAL GOOGLE ACCOUNT_LINK | 2026-10-03 16:48:42Z | `HUMAN_DECISIONS.md` HA-AUTH-07 reconstruction |
| REAL GOOGLE LOGIN (linked) | 2026-10-03 23:23Z | same |
| OWNER UNLINK (24 §18) | 2026-10-04 14:25:01Z | `evidence/ha_auth_07_production_transition.txt` |
| REAL GOOGLE LOGIN → PROVIDER_BOOTSTRAP (new identity, `previouslyBound: true`) | 2026-10-04 14:28:16Z | same |
| `GET /auth/identity` live | 401 `NO_SESSION` without a session | probe 2026-10-04 |
| `GET /auth/providers` live | `[{providerId: google, label: Google, proofClass: PRODUCTION_PROVIDER}]` | probe 2026-10-04 |

## 3. Contacts and shapes (exact, as served)

All under the deployed prefix `/api`. Session = HttpOnly cookie
`nquiry_session`; every browser call uses `credentials: "include"`. Unsafe
methods must come from an allowed `Origin` (`NQUIRY_ALLOWED_ORIGINS`) or be
same-site (24 §21.7; WU-AUTH-14); `POST /auth/login` additionally requires
`Content-Type: application/json` (login-CSRF contract). No token, subject,
code, state or nonce ever appears in a body.

| Contact | Session | Success body | Denials |
|---|---|---|---|
| `POST /auth/login` `{email,password}` | — | `200 {kind: ok, userId}` + cookie | `401 denied INVALID_CREDENTIALS`, `403 rejected LOGIN_CSRF_REJECTED`, `400 rejected …` |
| `POST /auth/logout` | optional | `200 {kind: ok}` + cookie cleared | — |
| `GET /auth/me` | required | `200 {kind: ok, userId, establishment: ESTABLISHED \| PENDING_EMAIL_VERIFICATION}` (WU-AUTH-22: PENDING = a self-registered identity whose own address is not yet verified — it may use every `/auth/*` contact; every business contact answers `403 {kind: denied, result: DENY, reasonCode: IDENTITY_NOT_ESTABLISHED}` until the verification completes) | `401 denied NO_SESSION` |
| `GET /auth/identity` | required | `200 {kind: ok, userId, displayName, canonicalEmail}` | `401 denied NO_SESSION` |
| `GET /auth/providers` | — | `200 {kind: ok, providers: [{providerId, label, proofClass}]}` (`PRODUCTION_PROVIDER` \| `TEST_PROVIDER`) | — |
| `GET /auth/oidc/{p}/start?next=<path>` | — (a live session is ignored; 24 §36 #18 open) | `303` to the provider | `503 unavailable PROVIDER_NOT_CONFIGURED`; `next` is validated server-side (path only) |
| `GET /auth/oidc/{p}/callback` | — | `303` to the validated `next` (+ session cookie) | `303 /login?auth=` `cancelled` \| `provider_unavailable` \| `provider_error` \| `failed` \| `unavailable` |
| `GET /auth/methods` | required | `200 {kind: ok, methods: [{methodId, methodType, status, createdAt, lastAuthenticatedAt, provider: null \| {providerId, email}}]}` | `401` |
| `POST /auth/oidc/{p}/link/start?next=<path>` (form POST) | required | `303` to the provider | `401`, `503` |
| `GET /auth/oidc/{p}/link/callback` | required | `303 <next>?link=ok` | `?link=already_linked` \| `collision` \| `cancelled` \| `failed`; fallback target when no bound `next` is known = `NQUIRY_ACCOUNT_SECURITY_PATH` (default `/account/security`, production `/workspaces` once deployed) — a consumer still passes its own `next` |
| `POST /auth/methods/{id}/unlink` | required | `200 {kind: ok, methodId, remainingActiveMethods, currentSessionEnded}` (cookie cleared when the current session ended) | `400 rejected MALFORMED_METHOD_ID`, `403 denied UNLINK_DENIED` (unknown / foreign / already revoked — one class), `409 denied LAST_METHOD` |
| `GET /auth/sessions` | required | `200 {kind: ok, sessions: [{sessionId, issuedAt, expiresAt, current, methodType}]}` | `401` |
| `POST /auth/sessions/{id}/revoke` | required | `200 {kind: ok}` (cookie cleared when it was the current one) | `400 rejected MALFORMED_SESSION_ID`, `404 denied SESSION_NOT_FOUND` (foreign == missing) |
| `POST /auth/logout-all` | required | `200 {kind: ok, revokedSessions}` + cookie cleared | `401` |
| `POST /auth/password/change` `{currentPassword, newPassword}` (WU-AUTH-19) | required | `200 {kind: ok, sessionsRevoked}` (the proving session continues) | `401 NO_SESSION`, `403 denied CURRENT_PASSWORD_INVALID \| NO_LOCAL_CREDENTIAL`, `400 rejected PASSWORD_INVALID` |
| `POST /auth/login` under the lockout boundary (WU-AUTH-20) | — | — | `429 {kind: denied, reasonCode: RATE_LIMITED}` (the address or the client is paused; identical for known and unknown addresses) |
| `POST /workspaces/{ws}/members/{user}/revoke`, `POST /workspaces/{ws}/members/{user}/role {role}` (WU-AUTHZ-01) | required | `200 {kind: ok}` | `{kind: denied, result: DENY, reasonCode: NOT_GOVERNANCE_ROOT \| MEMBERSHIP_NOT_FOUND \| GOVERNANCE_ROOT_NOT_REMOVABLE \| …}`, `{kind: rejected, reasonCode: ROLE_UNCHANGED \| UNKNOWN_ROLE:* \| OWNER_ROLE_NOT_ASSIGNABLE:*}`; the overview carries `capabilities.revokeMembership / changeMemberRole` and per member `administrable` (the root is never administrable) — a consumer offers the controls on those, never on a role |
| `GET /auth/contacts` (WU-AUTH-21/22) | — | `200 {kind: ok, recovery: AVAILABLE \| UNAVAILABLE, emailVerification: AVAILABLE \| UNAVAILABLE, registration: AVAILABLE \| UNAVAILABLE}` — what THIS deployment serves (recovery policy ≠ DENIED and a mail sink; a mail sink and a declared environment). A consumer offers the two contact groups below on these words only | — |
| `POST /auth/register` `{email, name, password}` (WU-AUTH-22; HD-AUTH-13) | — (login-CSRF class: admitted Origin / Fetch-Metadata AND `Content-Type: application/json`, else `403 LOGIN_CSRF_REJECTED`) | `200 {kind: ok}` — THE ONE ANSWER for a new and for a taken address; no session; the identity exists PENDING with a LOCAL_PASSWORD credential and ONE verification message is on its way; the person logs in with the chosen password and opens the link while logged in | `503 unavailable REGISTRATION_NOT_AVAILABLE` (not the open policy, no mail sink or undeclared environment), `400 rejected EMAIL_INVALID \| NAME_REQUIRED \| PASSWORD_INVALID` (12..1024 chars, no surrounding whitespace), `429 denied RATE_LIMITED` (per client), `503 unavailable EMAIL_DELIVERY_FAILED` (nothing created) |
| `POST /auth/email/verification/start` `{email}` (WU-AUTH-11/21) | required | `200 {kind: ok, challengeId, expiresAt}`; the message goes to the address with ONE link `<NQUIRY_PUBLIC_WEB_BASE_URL><NQUIRY_EMAIL_VERIFY_PATH>?challengeId=&token=` (default path `/account/verify-email`) | `401 NO_SESSION`, `400 rejected EMAIL_INVALID`, `429 denied VERIFICATION_RESEND_THROTTLED`, `503 unavailable EMAIL_DELIVERY_NOT_CONFIGURED \| ENVIRONMENT_NOT_DECLARED \| EMAIL_DELIVERY_FAILED` |
| `POST /auth/email/verification/complete` `{challengeId, token}` | required (the SAME identity that started it) | `200 {kind: ok, email}` — the address is now an ACTIVE verified relation of the identity | `401 NO_SESSION`, `400 rejected MALFORMED_CHALLENGE_ID \| MALFORMED_TOKEN`, `403 denied VERIFICATION_DENIED` (expired / used / foreign / wrong token — one class), `503 ENVIRONMENT_NOT_DECLARED` |
| `GET /auth/emails` | required | `200 {kind: ok, emails: [{email, verifiedAt, active}]}` (`active` = neither superseded nor revoked) | `401` |
| `POST /auth/recovery/start` `{email}` (WU-AUTH-12/21) | — | `200 {kind: ok}` — THE ONE ANSWER for every address (known, unknown, unverified, delivery failed); a message with ONE link `<NQUIRY_PUBLIC_WEB_BASE_URL><NQUIRY_RECOVERY_COMPLETE_PATH>?recovery=&token=` (default path `/recover/reset`) goes only to an ACTIVE verified address of a LOCAL_PASSWORD identity | `503 unavailable RECOVERY_NOT_AVAILABLE` (policy DENIED, no mail sink or undeclared environment); a malformed address gets the one answer too |
| `POST /auth/recovery/complete` `{recoveryId, token, newPassword}` | — (creates NO session; every ACTIVE session of the identity is revoked) | `200 {kind: ok}` | `503 RECOVERY_NOT_AVAILABLE`, `400 rejected MALFORMED_RECOVERY_ID \| MALFORMED_TOKEN \| PASSWORD_INVALID`, `403 denied RECOVERY_DENIED` (expired / used / unknown / wrong token — one class) |

## 4. What a human-facing consumer may and must expose (24 §24)

Must (24 §24.5 target UI contacts, all served by this branch): list methods,
add Google (link), remove method, revoke sessions, logout-all; show the
identity presentation. May (when the API says so): the provider button only
when `/auth/providers` lists it; a `TEST_PROVIDER` only with its label.
Since WU-AUTH-21 (HD-AUTH-10) also: the verified-address relation and its
Send control; the two mail-link landings (`/account/verify-email`,
`/recover/reset` — the paths the producer renders, configurable); the
recovery start; a "forgot password" contact on the login — each only while
`/auth/contacts` says AVAILABLE (the product frontend materializes exactly
this: CYAN AUTH/CYAN-RECOVERY-01).
Since WU-AUTH-22 (HD-AUTH-13) also: a registration contact (address, name,
password; the one answer; then the login) only while
`/auth/contacts.registration` is AVAILABLE; the PENDING state of `/auth/me`
projected as "verify your address to continue" with the chamber's
verification control (business reads answer 403 `IDENTITY_NOT_ESTABLISHED`).
Must not: a recovery link while `/auth/contacts.recovery` is `UNAVAILABLE`;
a registration contact while `registration` is `UNAVAILABLE`; any local
truth about identity, session validity, role or authority (24 §24.3); raw
protocol material (24 §24.6) — the mail token is presented to the API once and
leaves the address bar, the DOM and storage.

## 5. Open on the producer side (not blocking consumption)

HA-AUTH-03 last method (NEVER), 24 §36 #13 re-enable / administrative
recovery, #18 multi-account UX (a live session starting a provider login is
not refused), PFC HA-10 business-path DB principal. HA-AUTH-02 is resolved
(HD-AUTH-10) and **live since 2026-10-06 (HD-AUTH-12): production
`/auth/contacts` answers AVAILABLE / AVAILABLE and the lifecycle is proven
with real delivery**. None changes a shape above.
