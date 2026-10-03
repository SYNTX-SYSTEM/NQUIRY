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

## Open for Human Authority
- AUTH/CYAN-04 — not defined, not authorized.
