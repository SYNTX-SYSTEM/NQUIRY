# AUTH-CYAN — HUMAN AUTHORITY RECORD (CYAN-side)

The PURPLE AUTH field keeps its own authority ledger on `auth-identity` (`docs/implementation/field-reports/AUTH/`;
HA-AUTH-01…06, HD-AUTH-06). This file is the CYAN line's record of the authority that governs CYAN's consumption of
PURPLE AUTH (Architecture 25 §18: the evidence of a Field must let a new agent reconstruct which authority authorized
the Delta). Nothing in this file upgrades PURPLE's status.

---

## HA-AUTH-CYAN-01 — AUTH/CYAN-01 authorized (2026-10-03, Human Authority, verbatim)

> SYNTX::SFE · MODE = IMPLEMENTATION · FIELD = PURPLE_AUTH ↔ CYAN_FRONTEND · WORK_UNIT = AUTH/CYAN-01
>
> AUTHORIZE implementation of the already reconstructed AUTH/CYAN-01 only. BASE = frontend-symbiotic @ 28c485e
>
> EXACT FIRST BROKEN RELATION: LIVE PURPLE PROVIDER OUTPUT → CYAN typed auth/provider contract. Materialize ONLY this relation.
>
> SCOPE: Extend `apps/web/lib/api/authClient.ts` with typed, fail-closed consumption for the already-live PURPLE AUTH
> contract. Implement: listProviders · listMethods · listSessions · unlinkMethod · revokeSession · logoutAll · Google
> login start URL builder · Google link-start action/URL handling · AUTH projection vocabulary · LINK projection
> vocabulary. Provider availability must come ONLY from the parsed provider response. No hard-coded Google availability.
>
> HARD LAWS: AUTHENTICATION != AUTHORIZATION · AUTHENTICATED_PRINCIPAL != ROLE · ROLE != AUTHORITY · LOGIN != LINK ·
> LINK != ACCOUNT_CREATION · GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN · API_LIVE != GUI_MATERIALIZED ·
> PROVIDER_OUTPUT != CYAN_INFERENCE · UNKNOWN != OK · DENIED != OK
>
> FAIL CLOSED: Unknown response kind, fields, enum values, proofClass, auth projection, link projection must fail
> closed. Never map unknown to success. Refuse unsafe or absolute/non-local next targets.
>
> PRODUCTION PROVIDER FIXTURE: Prove the exact current live shape
> `{"kind":"ok","providers":[{"providerId":"google","label":"Google","proofClass":"PRODUCTION_PROVIDER"}]}`.
> Do not infer anything beyond that contract.
>
> FILES: apps/web/lib/api/authClient.ts · apps/web/tests/lib/authClient.test.ts ·
> docs/implementation/field-reports/AUTH-CYAN/WU-AUTH-CYAN-01.md · docs/implementation/field-reports/AUTH-CYAN/HA-AUTH-CYAN.md.
> No component changes. No route changes. No rail changes. No login-page changes. No PURPLE source changes.
>
> PROOF: focused authClient unit tests · adversarial parser tests · unknown enum/kind/field falsifiers · unsafe
> next-target falsifiers · existing CYAN auth preservation tests · existing mocked Playwright auth lane · TypeScript ·
> ESLint. No real-stack callback. No production login. No live deployment.
>
> CLAIM CEILING: After closure only: PURPLE AUTH truth = CONSUMABLE BY CYAN. Still: NOT PRESENTED · NOT GUI-INTEGRATED ·
> NOT REAL-GOOGLE-CALLBACK-PROVEN. GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN.
>
> Commit/tag/push only if proof is green. Then STOP. Do not continue to AUTH/CYAN-02 automatically.

**Reading applied by the executing agent.** The "already reconstructed" contract was re-derived in this session from
the PURPLE sources at `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` and checked byte-identical against
the live assembly `auth-aa32c4d-20261001T081014Z` (see `WU-AUTH-CYAN-01.md` → Producer). The producer for CYAN's
AUTH consumption is therefore that commit, not the moving `auth-identity` head; a change of this producer requires a
new reconstruction and a new authorization (the same discipline as HD-27 for RED).

**What this authorization does not grant.** No presentation, no component/route/rail/login-page change, no PURPLE
change, no real Google callback, no production login, no deployment, no merge, no FIELD_GREEN / REVIEWED_FIELD /
PUBLISHED_FIELD, no AUTH/CYAN-02.

**Standing laws inherited.** HD-27 (separate lines, pinned producers, consumption never upgrades the producer),
HA-20 / HD-LIVE-1 (production is PRODUCTION; no impersonation of TEST), the PURPLE ceiling (HA-AUTH-01 DENIED,
HA-AUTH-02 DENIED, HA-AUTH-03 NEVER; GOOGLE_OIDC_ALLOWED != GOOGLE_OIDC_REAL_PROOF_COMPLETE), the commit gate
(commit/tag/push only on green proof, as granted above).

## HA-AUTH-CYAN-02 — AUTH/CYAN-02 authorized (2026-10-03, Human Authority, verbatim)

> SYNTX::SFE · MODE = IMPLEMENTATION · FIELD = PURPLE_AUTH ↔ CYAN_FRONTEND · WORK_UNIT = AUTH/CYAN-02
> BASE = origin/frontend-symbiotic dd0b8d936b849a7ad… · PURPOSE = Present the already-consumable PURPLE provider
> truth on the existing CYAN login field.
>
> EXACT FIRST BROKEN RELATION: CYAN typed auth/provider contract → presented provider contact on the CYAN login field.
> Materialize ONLY this relation.
>
> CURRENT TRUTH: AUTH/CYAN-01 is complete. PURPLE provider truth is consumable by CYAN. Provider availability must come
> ONLY from: listProviders(). No hard-coded Google availability. Current production provider truth: providerId = google,
> label = Google, proofClass = PRODUCTION_PROVIDER.
>
> SURFACE: Use the existing CYAN login page / Access Field. Do NOT create a second login experience. Do NOT redesign
> the page. Add the narrowest legitimate external-provider contact to the existing login field. The provider contact
> must appear ONLY when the parsed provider response says the provider is available. If provider discovery is
> unavailable, malformed, denied, unknown or fails closed: do not invent or show provider availability.
>
> SEMANTICS: This Work Unit presents authentication availability only. It does NOT prove a real Google login.
> GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN · LOGIN != LINK · LINK != ACCOUNT_CREATION · AUTHENTICATION != AUTHORIZATION ·
> AUTHENTICATED_PRINCIPAL != ROLE · ROLE != AUTHORITY
>
> GOOGLE CONTACT: Use the existing typed Google login-start builder from AUTH/CYAN-01. The visual control may initiate
> the legitimate login-start route. Do not: implement account linking; account creation; recovery; methods management;
> sessions management; unlink; logout-all; change PURPLE; add provider inference; add test-provider assumptions.
>
> FAIL CLOSED: Unknown provider response → no provider contact · Unknown proofClass → no provider contact · Malformed
> provider response → no provider contact · Provider unavailable → no provider contact. Never turn an unknown state into
> Google availability.
>
> VISUAL LAW: The existing Access Field remains visually primary. The Google provider contact must look like part of
> the existing login field. Do not create: a second dashboard; an account-security panel; a provider-management panel;
> a new auth route. Human Frontend Review is required after technical proof.
>
> PROOF (at minimum, 1–15): Google contact only from parsed live-shaped provider truth; no hard-coded Google
> availability; malformed response hides the contact; unknown proofClass fails closed; unavailable response hides the
> contact; local-password login unchanged; contact uses the typed login-start builder; unsafe next target remains
> refused; no link/account-creation behavior; no authority/role semantics inferred; no PURPLE source changes; no
> production deployment; existing auth preservation tests green; browser proof on desktop and Pixel 7; no visual
> overflow or second login surface. Run: focused component/unit tests; authClient preservation tests; mocked browser
> auth lane; TypeScript; ESLint; mutation proof for hard-coded availability / fail-open rendering / wrong start URL.
> Do not perform a real Google callback in this Work Unit.
>
> CLAIM CEILING (after closure only): PURPLE provider truth = CONSUMED AND PRESENTED BY CYAN · Google provider contact
> = GUI MATERIALIZED · Still: REAL GOOGLE LOGIN = NOT PROVEN · REAL GOOGLE CALLBACK = NOT PROVEN · ACCOUNT LINKING =
> NOT MATERIALIZED · ACCOUNT CREATION = DENIED · AUTHORIZATION = UNCHANGED
>
> Commit/tag/push only if proof is green. Then STOP. Do not continue into AUTH/CYAN-03 automatically.

**Reading applied by the executing agent.** The `?auth=` projection reading (a login non-success returns to
`/login?auth=<word>`) is NOT presented in this unit: the authorization materializes the provider contact only. It is
disclosed as the next relation. The human review runtime cannot execute the start route (the pinned RED producer has no
PURPLE routes); it serves a labelled FIXTURE_NON_PROOF copy of the live providers body and a labelled review boundary
for the start route — review infrastructure, not product code.

**Human Frontend Acceptance (2026-10-03): ACCEPTED** — `HUMAN_REVIEW_RESULT_AUTH_CYAN_02.md`.

## HA-AUTH-CYAN-03 — AUTH/CYAN-03 authorized (2026-10-03, Human Authority, verbatim)

> SYNTX::SFE · MODE = IMPLEMENTATION · FIELD = PURPLE_AUTH ↔ CYAN_FRONTEND · WORK_UNIT = AUTH/CYAN-03
> BASE = origin/frontend-symbiotic 71515fd4837fbbe51d081da8a875c1cb93dae1f4 · PURPOSE = Present the already-defined
> ?auth= provider-login result projection on the existing CYAN Access Field as a fail-closed authentication boundary.
>
> EXACT FIRST BROKEN RELATION: ?auth= projection → known provider-login boundary → Access Field presentation.
> Materialize ONLY this relation.
>
> KNOWN AUTH PROJECTIONS: Use ONLY the closed AUTH projection vocabulary already defined by AUTH/CYAN-01 (such as
> unavailable, failed, cancelled, provider_unavailable, provider_error). Verify the exact vocabulary from authClient.ts
> before implementation. Do not invent values. UNKNOWN → render nothing. MISSING → render nothing.
>
> SEMANTICS: The projection represents an authentication boundary/result only. It does NOT represent successful Google
> login, authorization, role, authority, account creation, account linking, recovery. AUTHENTICATION != AUTHORIZATION ·
> FAILED_LOGIN != DENIED_AUTHORITY · UNKNOWN != FAILURE · UNKNOWN != SUCCESS
>
> SURFACE: Render the boundary inside the existing Access Field. Do not create a second auth surface, a modal, an
> account-security panel, a provider-management panel, a new route. The existing email/password form and Google
> provider contact remain visually primary.
>
> FAIL CLOSED: Known projection → render the exact legitimate boundary presentation. Unknown projection → render
> nothing. Malformed query → render nothing. Duplicate/conflicting projection → fail closed. Do not infer intent from
> arbitrary query text.
>
> PROOF (1–15): every known AUTH projection renders its legitimate boundary; unknown renders nothing; missing renders
> nothing; malformed renders nothing; conflicting/duplicate fails closed; local password login unchanged; Continue with
> Google unchanged; no success state synthesized; no authority/role semantics inferred; no PURPLE source change; no
> account-linking behavior; no production deployment; Desktop browser proof; Pixel 7 browser proof; no visual overflow
> caused by the boundary. Run: focused unit/component tests; authClient preservation; existing auth lane;
> provider-contact preservation; browser proof Desktop + Pixel 7; TypeScript; ESLint; mutation proof for
> unknown→visible, failed→success, malformed→visible, and bypass of typed vocabulary.
>
> CLAIM CEILING (after closure only): KNOWN ?auth= PROJECTION = PRESENTED BY CYAN · Still: REAL GOOGLE LOGIN = NOT
> PROVEN · REAL GOOGLE CALLBACK = NOT PROVEN · ACCOUNT LINKING = NOT MATERIALIZED · AUTHORIZATION = UNCHANGED
>
> Commit/tag/push only if proof is green. Then STOP. Do not continue into AUTH/CYAN-04 automatically.

**Reading applied by the executing agent.** Vocabulary verified from `authClient.ts` at the base:
`cancelled, provider_unavailable, provider_error, failed, unavailable` (exactly the five named). The boundary is shown
only while the local form is idle: a local request (pending) or a local verdict replaces it, so two boundaries never
stack. The URL is not rewritten. The review runtime presents the boundary by opening `/login?auth=<word>` directly;
no callback produces it there (the pinned RED producer has no PURPLE routes).

**Human Frontend Acceptance (2026-10-03): ACCEPTED** — `HUMAN_REVIEW_RESULT_AUTH_CYAN_03.md`.

## HA-AUTH-CYAN-IDENTITY-01 — AUTH/CYAN-IDENTITY-01 authorized (2026-10-03, Human Authority, verbatim essentials)

> SYNTX::SFE · MODE = IMPLEMENTATION · FIELD = PURPLE_AUTH ↔ CYAN_FRONTEND · WORK_UNIT = AUTH/CYAN-IDENTITY-01
> PURPOSE = Materialize the authenticated human/session identity projection inside the existing CYAN organism using
> only already-live PURPLE read truth. BASE = the CURRENT origin/frontend-symbiotic HEAD (expected 5feba9cce76b043c…;
> verify from git; do NOT branch from the stale 28c485e base).
>
> AUTHORITATIVE PURPLE TRUTH: REAL_GOOGLE_LINK = PROVEN · REAL_GOOGLE_LOGIN = PROVEN. The successful Google login
> authenticated the SAME pre-existing NQUIRY identity. No account was created. No authority relation changed.
> Authentication method GOOGLE_OIDC / ACTIVE; the linked LOCAL_PASSWORD method remains ACTIVE. Read contacts:
> GET /api/auth/me · /api/auth/sessions · /api/auth/methods · /api/auth/providers.
>
> EXACT RELATION: AUTHENTICATED PRINCIPAL → CURRENT SESSION → AUTHENTICATION METHOD → PROVIDER TRUTH → CYAN IDENTITY
> PROJECTION. Materialize this relation only.
>
> DESIGN LAW: NOT a profile dashboard, NOT account management, NOT provider management. The existing organism remains
> visually primary. Prefer the existing "Identity and access" proof plane / chamber. A small rail projection may be
> reused only if subordinate.
>
> SEMANTIC MODEL / SAFE PROJECTION: authenticated, userId; currentSession (sessionId, issuedAt, expiresAt,
> methodType); current method (methodType, status, lastAuthenticatedAt, provider.providerId, provider.email);
> provider label derived ONLY by joining providerId to parsed /auth/providers truth. Do NOT label provider email as the
> canonical NQUIRY identity. Do not hard-code provider labels.
>
> IMPORTANT ABSENCE: PURPLE exposes no authoritative human-facing NQUIRY display name. Do NOT invent a human name,
> initials, avatar identity or display name. Human-facing name is NOT_MATERIALIZED.
>
> HARD LAWS: IDENTITY != ROLE · AUTHENTICATION != AUTHORIZATION · AUTH_METHOD != ACCESS_RIGHT · PROVIDER_EMAIL !=
> CANONICAL_IDENTITY · SESSION != AUTHORITY · WORKSPACE_MEMBERSHIP != AUTHENTICATION · UNKNOWN != INFERRED ·
> GOOGLE_OIDC != GOOGLE_AUTHORITY.
>
> FAIL CLOSED: /auth/me failure → no identity projection · /auth/sessions malformed/unavailable → no "current session"
> claim · /auth/methods malformed/unavailable → no "signed in via" claim · /auth/providers malformed/unavailable → no
> invented label · unknown methodType → fail closed · unknown providerId → raw id only if the typed contract permits it.
> Never synthesize Google from an email domain. CURRENT SESSION only from session.current = true; never from the
> newest timestamp, the last array element or lastAuthenticatedAt; at most one.
>
> RAIL: a minimal secondary projection MAY show a narrow authenticated-method marker; no avatar menu, account dropdown,
> settings menu or account-security UI.
>
> PRESERVATION: local login, Google login contact, ?auth= boundary, Workspace organism, Logout, existing Identity and
> access semantics, AUTH/CYAN-01..03. No PURPLE changes. No production deployment.
>
> PROOF 1–20 and MUTATIONS (newest-as-current, Google hard-coded, email as identity, role/authority inferred, failed
> method fetch still "via Google", unknown methodType friendly) as listed in the authorization. HUMAN FRONTEND REVIEW
> required. CLAIM CEILING: AUTHENTICATED IDENTITY / CURRENT AUTHENTICATION METHOD / CURRENT SESSION PROVENANCE =
> PRESENTED BY CYAN; HUMAN-FACING NQUIRY DISPLAY NAME = NOT MATERIALIZED; AUTHENTICATION != AUTHORIZATION; IDENTITY !=
> ROLE; IDENTITY != AUTHORITY; ACCOUNT MANAGEMENT = NOT MATERIALIZED BY THIS WORK UNIT. Commit/tag/push only if proof
> is green. Then STOP.

**Reading applied by the executing agent.** Base verified: `origin/frontend-symbiotic` = `5feba9cce76b043c8813f11c4fda25e3d51581ac`
(the AUTH/CYAN-03 test guide). The projection lives in the existing "Identity and access" proof plane of the Workspaces
field; the rail is left untouched (the optional marker was not needed and would have added a fourth rail item to the
SF-03 grid). The method relation is read as "exactly one ACTIVE method of the current session's methodType"; the
sessions wire carries no methodId, so this is the only authoritative join. The review runtime presents the relation
through labelled FIXTURE_NON_PROOF sessions/methods answers (the pinned RED producer has no PURPLE routes); the live
system's real relation was not read by this unit.

**Human Frontend Review (2026-10-03, first pass): CHANGES_REQUESTED** — technical semantics accepted; one symbiotic
integration pass required under the same gate (verbatim essentials): (1) the Google provider email must be visibly
attached to the Google authentication (CURRENT AUTHENTICATION · Google · Google account <email>), staying a PROVIDER
METHOD ATTRIBUTE, never canonical identity / display name / role / authority; (2) replace the isolated "Log out" in the
upper-right rail with a compact SYMBIOTIC IDENTITY / LOGOUT PANEL in the organism's language (dark translucent
surface, blue/cyan/lilac glow, subtle orbital cues; no SaaS account dropdown), conceptually SIGNED IN WITH · Google ·
Google account <email> · [Log out]; local case SIGNED IN WITH · Local password · [Log out], no email; a linked Google
method that is not the current authentication is never shown (CURRENT AUTHENTICATION METHOD != ANY LINKED METHOD);
everything from the ONE proven projection (no second auth truth); no invented name/avatar/initials (an ornamental
glyph allowed); no dropdown, settings, provider/methods/sessions management, unlink or authority control; fail closed
on provider/method truth; Logout = the existing legitimate effect; preserve all AUTH/CYAN-IDENTITY-01 laws and
AUTH/CYAN-01..03; proof 1–15 and mutations (Google when LOCAL_PASSWORD current; email as identity; invented name;
Google hard-coded; email shown when missing; Logout disconnected); rebuild the review runtime; acceptance PENDING.

**Delta applied (same Work Unit, 2026-10-03):** `components/field/IdentityPanel.tsx` (rail panel, consumes the same
projection, embeds the unchanged `LogoutButton`) as the Workspaces exit; the chamber nests "<label> account <email>"
under "Current authentication". The panel exists on the Workspaces field only (the Workspace field already shows no
exit; the Session view keeps the plain Log out — it holds no `/auth/me` verdict and a self-fetching panel would be a
second auth truth). Narrow screens: the header grid gives the mark its intrinsic width when a panel is present.

## HA-AUTH-CYAN-IDENTITY-01/F — NQUIRY identity/authentication field reconstruction and repair (2026-10-03, verbatim essentials)

> MODE = FIELD_RECONSTRUCTION_AND_IMPLEMENTATION · FIELD = NQUIRY_IDENTITY_AUTHENTICATION_FIELD · SCOPE =
> CURRENT_AUTHENTICATION_RELATION_TO_CYAN_PROJECTION. The field is NQUIRY-owned; Google is only an external producer:
> GOOGLE != IDENTITY FIELD / AUTHORITY / CURRENT SESSION TRUTH; PROVIDER AVAILABILITY != CURRENT AUTHENTICATION;
> LINKED PROVIDER != CURRENT AUTHENTICATION. The field answers: WHO is authenticated; BY WHICH method the CURRENT
> session was produced; WHICH provider relation belongs to that method; WHAT CYAN may project. CRITICAL LAW: CURRENT
> AUTHENTICATION METHOD = METHOD THAT PRODUCED THE CURRENT SESSION — never from available providers, linked methods,
> list order, timestamps, provider email, provider availability, a previous session, a review fixture default or
> frontend memory. REVIEW RUNTIME LAW: the runtime is part of the proof field; it must not contain a globally fixed
> Google truth; LOCAL LOGIN TRANSITION → local current session; GOOGLE REVIEW TRANSITION → Google current session; a
> fixture may not contradict the transition that produced the state (LOCAL LOGIN + GOOGLE CURRENT SESSION FIXTURE =
> INVALID FIELD STATE). FIRST BROKEN RELATION observed: local login → CYAN projection Google ⇒ LOGIN TRANSITION →
> CURRENT SESSION PRODUCER (the review producer). Repair the authoritative state producer, not the label. BOUNDARY:
> unknown producer → CURRENT_AUTHENTICATION_METHOD = UNKNOWN → CYAN shows "Authenticated" only. ALLOWED DELTA: make
> review-runtime current-session truth causally follow the login transition; NOT allowed: hard-coding either method,
> deriving the method from linked methods / provider availability / email, changing production PURPLE semantics, a
> second frontend auth truth. Proof CASES 1–7, mutations (linked Google forces Google; email forces Google; newest
> method; available provider; local login still Google fixture; Google state produces local; unknown → Google; unknown
> → Local password; frontend caches), RECONSTRUCTION RULE after every transition. No production deployment.

**Reconstruction by the executing agent.** CYAN's derivation (`identityProjectionFrom`) already obeys the law: the
method is the producer of the one `current` session; the mocked lane had proven the local case. The broken relation
was the review-runtime producer: the proxy served one fixed GOOGLE_OIDC current session regardless of the transition.
**Repair (runtime-only, `cy01-inspect/review-auth-fixture.mjs` + `proxy.mjs`, copies in
`browser-evidence/identity-01/review-runtime/`):** a successful local login (`POST /api/auth/login` → 200) records the
transition "local"; the review boundary page offers an explicit, labelled "Enter the Google review state" transition
(records "google"; no Google contacted); logout clears it; no recorded transition → one current session with
`methodType: null` (UNKNOWN → CYAN shows "Authenticated" + short id). The linked methods are the same pair in every
state and never decide. Product code: unchanged; tests and the mutation script extended (CASE 1 through the real
login form, CASE 5, CASE 6, the reconstruction sequence Google → logout → local login; mutations M13–M16 incl. a
frontend cache killed through the browser lane).

**Human Review decision (2026-10-03):** the local fixture review is insufficient for final acceptance; a REAL
end-to-end proof of the current CYAN build against the real PURPLE Google authentication field is required
("Enter the Google review state" proves CYAN projection semantics under FIXTURE_NON_PROOF only). The reconstruction
answered: same origin, path-prefixed candidate mount `/cy-review/` beside the live `/`, both on `/api/`; a separate
host is excluded by the host-scoped session and binding cookies, the single allowed origin and the registered callback.
Acceptance of AUTH/CYAN-IDENTITY-01 stays PENDING until that proof.

## HA-CYAN-REAL-E2E-FIELD-MOUNT-01 — CYAN same-origin review mount (2026-10-03, verbatim essentials)

> MODE = FIELD_ENGINEERING · FIELD = NQUIRY_CYAN_SAME_ORIGIN_REVIEW_MOUNT_FIELD · WORK_UNIT = CYAN_REAL_E2E_FIELD_MOUNT_01.
> PURPOSE: the narrowest legitimate Field that lets the CURRENT CYAN assembly coexist beside the live CYAN on the SAME
> origin while consuming the SAME real PURPLE authentication Field — preparation for the later real E2E proof, which
> this Work Unit does NOT perform. Begin from the relations, not from "add a basePath". TARGET: `/` → live CYAN
> unchanged; `/cy-review/` → candidate CYAN; both → `/api/` → production PURPLE. FRONTEND_MOUNT (M) owns CYAN page
> routes, static assets, internal navigation and MAY define the auth return target; FRONTEND_MOUNT != API_MOUNT; the
> Google callback stays `/api/auth/oidc/google/callback`; the host session is shared across same-host paths; one
> authentication Field, multiple frontend projections. FIRST BROKEN RELATION: CYAN_OWNED_LOCATION → IMPLICIT_ROOT
> instead of → EXPLICIT_FRONTEND_MOUNT; repair at the authoritative home, never patch visible URLs one by one.
> SEMANTIC ERRORS 01–12 (mount prefixes API; localhost consuming the production session; new callback URI; review
> changes live root; changes PURPLE session semantics; changes Google credentials; navigation escapes the mount; asset
> hard-coded to root; auth return lands on live root when candidate continuation is meant; review config forced into
> default builds; auth truth from the mount; independent identities). VALID: STATE A (M=/, api=/api), STATE B
> (M=/cy-review, api=/api). BOUNDARIES: no PURPLE change, no Google change, no deployment or nginx change, live root
> unchanged, auth semantics unchanged, unknown route ownership → STOP. HUMAN AUTHORITY: only making CYAN's own mount
> relation explicit and configurable. ALLOWED DELTA: mount configuration, routing/navigation/asset/auth-return
> reconstruction, build configuration expressing the mount. FALSIFIERS 01–16, MUTATIONS M1–M12, progressive proof
> radius (reconstruction → semantic falsifiers → mount unit tests → affected suites → browser proof for both mounts →
> mutation proof); no real production E2E, no deployment. NEXT FIELD BOUNDARY: STAGED_SAME_ORIGIN_E2E_ASSEMBLY — not
> entered automatically.

**Reconstruction by the executing agent.** Root-bound CYAN-owned locations found: the brand asset reference in
`components/field/Identity.tsx`, the auth return target `"/"` in `app/login/page.tsx`, and the absent mount expression
in `next.config.ts`. Page routes, `next/link` and the app router (22 call sites) are prefixed by Next's own mount
mechanism (`basePath`), so they need no change. No CSS `url()`, no raw root anchors, no `location` writes. Authoritative
home materialized: `lib/field/mount.ts` (`NEXT_PUBLIC_FRONTEND_MOUNT` → `FRONTEND_MOUNT`, `mountPath`; refuses malformed
mounts and the API mount); `next.config.ts` derives `basePath` from it; the asset and the return target derive from
`mountPath`. Nothing under `lib/api` or in the identity/auth modules reads the mount. Disclosed: PURPLE's own login
non-success projection `/login?auth=<word>` is PURPLE-owned and root-bound, so under `/cy-review` a failed or cancelled
provider login lands on the live `/login` (CY-01 web) — not changed (BOUNDARY_01).

## Open for Human Authority
- STAGED_SAME_ORIGIN_E2E_ASSEMBLY (candidate web beneath `/cy-review/` on the production origin; one nginx location;
  no PURPLE, Google or live-root change) — not authorized, not entered.
- Human Frontend Acceptance of AUTH/CYAN-IDENTITY-01 — PENDING the real E2E proof.
- No further AUTH/CYAN Work Unit is defined or authorized.
