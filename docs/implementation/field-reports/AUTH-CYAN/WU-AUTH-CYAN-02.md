# WORK UNIT REPORT
FIELD: PURPLE_AUTH ↔ CYAN_FRONTEND
WORK_UNIT: AUTH/CYAN-02 — CYAN typed auth/provider contract → presented provider contact on the CYAN login field
DATE: 2026-10-03 · BASE: `origin/frontend-symbiotic` @ `dd0b8d936b849a7ad536f517a23eec6cf29fa126` (docs over `checkpoint-AUTH-CYAN-01` `5877c13`)
AUTHORITY: `HA-AUTH-CYAN.md` → HA-AUTH-CYAN-02 (2026-10-03).

## Exact first broken relation
The typed contract of AUTH/CYAN-01 had no consumer: the Access Field could not show that the server offers an external
provider. This unit presents exactly that — one contact inside the existing Access core, only when the parsed
`GET /auth/providers` answer names `google`. Nothing else: no link, no account creation, no methods, sessions, unlink,
logout-all, recovery; no projection reading; no new route or panel.

## Producer
Unchanged from AUTH/CYAN-01: PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (live assembly
`auth-aa32c4d-20261001T081014Z`). Live body re-probed read-only 2026-10-03:
`{"kind":"ok","providers":[{"providerId":"google","label":"Google","proofClass":"PRODUCTION_PROVIDER"}]}`.
No PURPLE source changed. Nothing deployed.

## Delta (CYAN)
| File | Change |
|---|---|
| `apps/web/lib/field/providerContact.ts` (new) | pure derivation: `providerContactFrom(list, next)` = `googleLoginStart` on a PARSED list → `{kind:"contact", provider, url}` or `none`; `discoverProviderContact(next)` runs `listProviders` and turns every throw (malformed, unsafe next, non-JSON, network) into `none` |
| `apps/web/lib/field/useProviderContact.ts` (new) | one discovery per mount, React state only, cancelled on unmount; `none` until the parsed answer arrives |
| `apps/web/components/field/ProviderContact.tsx` (new) | renders nothing for `none`; for a contact one `<a class="button secondary access-provider-action" href={url}>Continue with {label}</a>` under an "or" rule, `data-provider-id`, `data-proof-class`; a non-production proof class is named, never hidden |
| `apps/web/app/login/page.tsx` | `useProviderContact("/")` + `<ProviderContact …/>` after the form inside the core; header comment updated (the 22 §45.1 "not shown" sentence is superseded by the parsed-truth rule). Form, submit, `login()`, redirect, pending/boundary lines untouched |
| `apps/web/app/globals.css` | appended block `.access-provider*` (rule with "or", full-width secondary action inside the core; existing tokens only; no green) |
| `apps/web/tests/field/providerContact.test.tsx` (new) | 26 falsifiers (proofs 1–10) incl. source laws: no provider literal in derivation/hook/component/page, no hand-built URL, no role/authority/persistence/timers, no link or account-creation vocabulary |
| `apps/web/tests/e2e/cy06-provider.spec.ts` (new) | 11 browser falsifiers × desktop + Pixel 7 |
| `apps/web/playwright.sf01.config.ts` | mobile project regex now includes `cy06` |
| `apps/web/scripts/auth02-mutation-proof.mjs` (new) | 6 mutations, byte-identical restore |
| `docs/implementation/field-reports/AUTH-CYAN/` | this record, `HUMAN_REVIEW_GUIDE_AUTH_CYAN_02.md`, `browser-evidence/auth-02/SUMMARY.md` (+ untracked screenshots), HA record |
Not touched: `authClient.ts`, every other component/route/rail, PURPLE, RED, the lanes' producer pins, production.

## Laws and where they hold
| Law | Materialization |
|---|---|
| Availability only from `listProviders()`; no hard-coded Google | the only path to a contact is `googleLoginStart` on the branded parsed list; the sources carry no provider literal (test "never name google … as a literal"); mutation M1/M2/M3/M6 killed |
| Fail closed: unknown kind / proofClass / fields / unavailable / denied / failed → no contact | 11 closed cases in unit + 8 in browser render nothing; the local login stays `current` |
| Typed login-start builder; unsafe next refused | URL = `loginStartUrl(provider, "/")`; an unsafe `next` yields `none`; M4 (link route) and M5 (hand-built URL) killed |
| LOGIN != LINK, LINK != ACCOUNT_CREATION | no link/account-creation vocabulary in sources or markup; the browser proves one GET to `/start`, no POST, no `/link/` |
| AUTHENTICATION != AUTHORIZATION, no role/authority inference | no role/authority/viewer tokens in the contact sources; the gates laws over `app/login/page.tsx` pass |
| GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN | the control navigates; no callback is exercised; the review runtime's start route is a labelled boundary |
| Access Field visually primary; no second surface | one core, one form, one provider navigation; the contact uses the core's own secondary-button vocabulary (screenshots) |

## Proof
| Lane | Result |
|---|---|
| Focused unit falsifiers `tests/field/providerContact.test.tsx` | **26 / 26** |
| authClient preservation `tests/lib/authClient.test.ts` | 149 / 149 (unchanged) |
| Full unit suite (gates laws incl. `app/login/page.tsx`) | **561 / 561** (33 files) |
| Mutation proof `scripts/auth02-mutation-proof.mjs` | **6 / 6 killed**, byte-identical restore: M1 hard-coded availability · M2 fail-open discovery · M3 fail-open rendering · M4 link route as start URL · M5 hand-built URL forwarding an unsafe next · M6 page bypasses the parsed contact |
| Mocked browser lane `cy06-provider` (desktop + Pixel 7) | **22 / 22** |
| Existing mocked auth lane `auth.spec.ts` | 6 / 6 |
| SF-05 login-field laws (`sf05-field.spec.ts` "Login field", desktop + Pixel 7) | 6 / 6 |
| `tsc --noEmit`, `eslint .` | clean (1 pre-existing warning, untouched file) |
| Review runtime `127.0.0.1:13500` | contact visible on both devices, inside the core, one GET on activation (`browser-evidence/auth-02/SUMMARY.md`) |
| Not run, by authorization | real Google callback, production login, deployment |

Disclosed finding (pre-existing, out of scope — no redesign): on Pixel 7 the fixed ambient background of `/login`
reports a document `scrollWidth` of 465 px against a 412 px viewport with and without the contact; the page is not
sideways-scrollable and the core fits. The browser law of this unit measures the contact, the core and sideways
scrollability, not the clipped background.

## Status
FBR AUTH/CYAN-02: TECHNICALLY CLOSED. **READY_FOR_HUMAN_FRONTEND_REVIEW** (`HUMAN_REVIEW_GUIDE_AUTH_CYAN_02.md`).
Not FIELD_GREEN, not REVIEWED_FIELD, not PUBLISHED_FIELD, not merged, not deployed.

**Claim ceiling:** PURPLE provider truth = CONSUMED AND PRESENTED BY CYAN · Google provider contact = GUI MATERIALIZED.
Still: REAL GOOGLE LOGIN = NOT PROVEN · REAL GOOGLE CALLBACK = NOT PROVEN · ACCOUNT LINKING = NOT MATERIALIZED ·
ACCOUNT CREATION = DENIED · AUTHORIZATION = UNCHANGED.

**Next FBR (not authorized):** AUTH/CYAN-03 — the `?auth=` projection of a login non-success presented on the
Access Field as a boundary (known word → safe sentence; `unknown` → nothing), so a cancelled or failed provider login
does not return to a silent page.

## Checkpoint
| | Value |
|---|---|
| Field commit | `b8e7b2110422d9c9d93b86d85e6284e4b4eb1887` (tree `412aa5f2f734a856f8b47f7f28ec1192f59599b0`) |
| Tag | `checkpoint-AUTH-CYAN-02` → tag object `7ecf17c708c4620246a4692621499ab4127c61c8` → `b8e7b21` |
| Remote | `origin/frontend-symbiotic` = `b8e7b21` (+ this docs commit); tag pushed |
| Producer | PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (unchanged) |
