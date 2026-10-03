# WORK UNIT REPORT
FIELD: PURPLE_AUTH ↔ CYAN_FRONTEND
WORK_UNIT: AUTH/CYAN-03 — `?auth=` projection → known provider-login boundary → Access Field presentation
DATE: 2026-10-03 · BASE: `origin/frontend-symbiotic` @ `71515fd4837fbbe51d081da8a875c1cb93dae1f4` (docs over `checkpoint-AUTH-CYAN-02` `b8e7b21`)
AUTHORITY: `HA-AUTH-CYAN.md` → HA-AUTH-CYAN-03 (2026-10-03).

## Exact first broken relation
A provider login's non-success returns the browser to `/login?auth=<word>` (PURPLE `http_oidc._login_projection`).
Since AUTH/CYAN-01 the word is readable (`readAuthProjection`, closed vocabulary) but the Access Field ignored it: a
cancelled or failed provider login landed on a silent page. This unit presents the known word as a boundary inside the
existing Access core. Nothing else: no success, no authority, no link, no new route, no URL rewriting.

## Vocabulary (verified from `authClient.ts` at the base)
`AUTH_PROJECTIONS = ["cancelled", "provider_unavailable", "provider_error", "failed", "unavailable"]`. One sentence per
word, each naming a non-success and "No access relation was established.":

| word | sentence |
|---|---|
| cancelled | The provider login was cancelled. No access relation was established. |
| provider_unavailable | The identity provider is unavailable right now. No access relation was established. |
| provider_error | The identity provider reported an error. No access relation was established. |
| failed | The provider login could not be completed. No access relation was established. |
| unavailable | Signing in with this provider is not available for this account. No access relation was established. |

## Delta (CYAN)
| File | Change |
|---|---|
| `apps/web/lib/field/authBoundary.ts` (new) | pure: `AUTH_BOUNDARY_MESSAGES` (exactly the closed vocabulary), `authBoundaryFrom(search)` = `readAuthProjection` → `{kind:"boundary", projection, message}` or `none` (missing, unknown, repeated, malformed → none) |
| `apps/web/lib/field/useAuthBoundary.ts` (new) | `useSyncExternalStore` over `window.location.search` (server snapshot "", re-read on `popstate`); no state of its own, no persistence, no URL rewriting |
| `apps/web/components/field/AuthBoundary.tsx` (new) | renders nothing for `none`; for a boundary one `<p role="alert" id="auth-boundary" class="read-boundary access-auth-boundary" data-projection>` with the sentence; no control, no link |
| `apps/web/app/login/page.tsx` | `useAuthBoundary()`; `providerBoundary` shown only while the local form is idle; `<AuthBoundary …/>` after the provider contact, before the pending/boundary lines; core `data-core-state` becomes `boundary` for a known word; form `aria-describedby` points at it. Form, submit, `login()`, redirect, pending/verdict lines, provider contact untouched |
| `apps/web/app/globals.css` | `.access-auth-boundary { margin-top }` (the existing `read-boundary` vocabulary does the rest) |
| `apps/web/tests/field/authBoundary.test.tsx` (new) | 27 falsifiers (proofs 1–11) incl. source laws: the derivation reads the query only through `readAuthProjection`, no own parsing, no word mapped to another, no success/authority/role/link vocabulary, no persistence/timers/history |
| `apps/web/tests/e2e/cy07-auth-boundary.spec.ts` (new) | 15 browser falsifiers × desktop + Pixel 7 |
| `apps/web/playwright.sf01.config.ts` | mobile project regex now includes `cy07` |
| `apps/web/scripts/auth03-mutation-proof.mjs` (new) | 6 mutations, byte-identical restore |
| `docs/implementation/field-reports/AUTH-CYAN/` | this record, `HUMAN_REVIEW_GUIDE_AUTH_CYAN_03.md`, `browser-evidence/auth-03/SUMMARY.md` (+ untracked screenshots), HA record |
Not touched: `authClient.ts`, `providerContact.ts`, `ProviderContact.tsx`, every other component/route/rail, PURPLE, RED, production.

## Laws and where they hold
| Law | Materialization |
|---|---|
| Known word → exact legitimate boundary; UNKNOWN/MISSING/malformed/duplicate → nothing | unit matrix (14 nothing-cases, 5 known) + browser (8 nothing-cases, 5 known) × 2 devices; `readAuthProjection` returns `unknown` for a repeated parameter, which is `none` here |
| UNKNOWN != FAILURE, UNKNOWN != SUCCESS | an unknown word is not mapped to `failed` (source law; mutation M1); no sentence contains success wording (law; M2) |
| Typed vocabulary only (PROVIDER_OUTPUT != CYAN_INFERENCE) | the derivation contains no own query parsing (law; M4); the message table keys equal `AUTH_PROJECTIONS` exactly |
| AUTHENTICATION != AUTHORIZATION, FAILED_LOGIN != DENIED_AUTHORITY | no sentence says denied/forbidden/authority/role; gates laws over the page pass |
| No success state synthesized | core state is `boundary`, never a success state (M6); `role=alert` boundary line in the `read-boundary` vocabulary |
| Access Field and Google contact remain primary and unchanged | browser: form empty, "Log in", provider contact with the typed URL, one core, one form; the boundary is placed after the contact; local request replaces it (M5) |
| LOGIN != LINK | `?auth=ok` / `already_linked` present nothing |

## Proof
| Lane | Result |
|---|---|
| Focused unit falsifiers `tests/field/authBoundary.test.tsx` | **27 / 27** |
| authClient preservation `tests/lib/authClient.test.ts` | 149 / 149 (unchanged) |
| provider-contact preservation `tests/field/providerContact.test.tsx` | 26 / 26 (unchanged) |
| Full unit suite (gates laws incl. `app/login/page.tsx`) | **588 / 588** (34 files) |
| Mutation proof `scripts/auth03-mutation-proof.mjs` | **6 / 6 killed**, byte-identical restore: M1 unknown→visible · M2 failed→success · M3 malformed/missing→visible · M4 bypass of the typed vocabulary · M5 boundary shown during a local request · M6 core success state |
| Mocked browser lane `cy07-auth-boundary` (desktop + Pixel 7) | **30 / 30** |
| Provider-contact lane `cy06-provider` (desktop + Pixel 7) | 22 / 22 |
| Existing auth lane `auth.spec.ts` + SF-05 login-field laws | 12 / 12 |
| `tsc --noEmit`, `eslint .` | clean (the first hook draft tripped `react-hooks/set-state-in-effect`; rewritten as an external-store read) |
| Review runtime `127.0.0.1:13500` | boundary presented for known words, nothing for unknown/conflicting, both devices (`browser-evidence/auth-03/SUMMARY.md`) |
| Not run, by authorization | real Google callback, production login, deployment |

Pre-existing Pixel 7 background width disclosure of AUTH/CYAN-02 unchanged; the boundary lies inside the core and the
page is not sideways-scrollable.

## Status
FBR AUTH/CYAN-03: TECHNICALLY CLOSED. **READY_FOR_HUMAN_FRONTEND_REVIEW** (`HUMAN_REVIEW_GUIDE_AUTH_CYAN_03.md`).
Not FIELD_GREEN, not REVIEWED_FIELD, not PUBLISHED_FIELD, not merged, not deployed.

**Claim ceiling:** KNOWN `?auth=` PROJECTION = PRESENTED BY CYAN. Still: REAL GOOGLE LOGIN = NOT PROVEN · REAL GOOGLE
CALLBACK = NOT PROVEN · ACCOUNT LINKING = NOT MATERIALIZED · AUTHORIZATION = UNCHANGED.

**Next FBR (not authorized, not defined by this unit):** the remaining PURPLE contacts have typed consumption but no
presentation (methods, sessions, link); any of them is a new surface and needs its own authorization. The real Google
callback remains unproven everywhere except on the live system, where it is not exercised.

## Checkpoint
(recorded after commit)
