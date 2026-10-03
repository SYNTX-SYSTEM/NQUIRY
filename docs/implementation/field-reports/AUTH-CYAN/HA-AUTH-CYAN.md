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

## Open for Human Authority
- AUTH/CYAN-03 (presenting the `?auth=` projection on the Access Field) — not authorized.
