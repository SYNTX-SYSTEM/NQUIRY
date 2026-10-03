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

## Open for Human Authority
- Human Frontend Review of AUTH/CYAN-IDENTITY-01 (see `HUMAN_REVIEW_GUIDE_AUTH_CYAN_IDENTITY_01.md`).
- No further AUTH/CYAN Work Unit is defined or authorized.
