# PURPLE → CONSUMER CONTRACT (post HD-AUTH-08)

Producer: `auth-identity` (this branch); live api = assembly
`auth-e069fc1-20261004T140533Z` (product `e069fc1`, migration head
`d2f4a6b8c1e3`). Written 2026-10-04 for the frontend lineage (CYAN,
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
| `GET /auth/me` | required | `200 {kind: ok, userId}` | `401 denied NO_SESSION` |
| `GET /auth/identity` | required | `200 {kind: ok, userId, displayName, canonicalEmail}` | `401 denied NO_SESSION` |
| `GET /auth/providers` | — | `200 {kind: ok, providers: [{providerId, label, proofClass}]}` (`PRODUCTION_PROVIDER` \| `TEST_PROVIDER`) | — |
| `GET /auth/oidc/{p}/start?next=<path>` | — (a live session is ignored; 24 §36 #18 open) | `303` to the provider | `503 unavailable PROVIDER_NOT_CONFIGURED`; `next` is validated server-side (path only) |
| `GET /auth/oidc/{p}/callback` | — | `303` to the validated `next` (+ session cookie) | `303 /login?auth=` `cancelled` \| `provider_unavailable` \| `provider_error` \| `failed` \| `unavailable` |
| `GET /auth/methods` | required | `200 {kind: ok, methods: [{methodId, methodType, status, createdAt, lastAuthenticatedAt, provider: null \| {providerId, email}}]}` | `401` |
| `POST /auth/oidc/{p}/link/start?next=<path>` (form POST) | required | `303` to the provider | `401`, `503` |
| `GET /auth/oidc/{p}/link/callback` | required | `303 <next>?link=ok` | `?link=already_linked` \| `collision` \| `cancelled` \| `failed`; default `next` is `/account/security` (a RED-line path — a consumer MUST pass its own `next`) |
| `POST /auth/methods/{id}/unlink` | required | `200 {kind: ok, methodId, remainingActiveMethods, currentSessionEnded}` (cookie cleared when the current session ended) | `400 rejected MALFORMED_METHOD_ID`, `403 denied UNLINK_DENIED` (unknown / foreign / already revoked — one class), `409 denied LAST_METHOD` |
| `GET /auth/sessions` | required | `200 {kind: ok, sessions: [{sessionId, issuedAt, expiresAt, current, methodType}]}` | `401` |
| `POST /auth/sessions/{id}/revoke` | required | `200 {kind: ok}` (cookie cleared when it was the current one) | `400 rejected MALFORMED_SESSION_ID`, `404 denied SESSION_NOT_FOUND` (foreign == missing) |
| `POST /auth/logout-all` | required | `200 {kind: ok, revokedSessions}` + cookie cleared | `401` |
| `POST /auth/email/verification/start`, `/complete`, `GET /auth/emails` | required | per `WU-AUTH-11.md` | production: `unavailable` (no mail provider, 24 §36 #16) |
| `POST /auth/recovery/start`, `/complete` | — | per `WU-AUTH-12.md` | production: `unavailable` (HA-AUTH-02 DENIED) |

## 4. What a human-facing consumer may and must expose (24 §24)

Must (24 §24.5 target UI contacts, all served by this branch): list methods,
add Google (link), remove method, revoke sessions, logout-all; show the
identity presentation. May (when the API says so): the provider button only
when `/auth/providers` lists it; a `TEST_PROVIDER` only with its label.
Must not: a recovery link while recovery is `unavailable`; self-registration
UI (bootstrap is the provider path, not a form); any local truth about
identity, session validity, role or authority (24 §24.3); raw protocol
material (24 §24.6).

## 5. Open on the producer side (not blocking consumption)

HA-AUTH-02 recovery (DENIED), HA-AUTH-03 last method (NEVER), 24 §36 #13
re-enable / administrative recovery, #16 mail provider, #18 multi-account UX
(a live session starting a provider login is not refused), PFC HA-10
business-path DB principal. None changes a shape above.
