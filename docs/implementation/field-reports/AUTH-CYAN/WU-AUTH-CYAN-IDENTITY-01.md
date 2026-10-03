# WORK UNIT REPORT
FIELD: PURPLE_AUTH ↔ CYAN_FRONTEND
WORK_UNIT: AUTH/CYAN-IDENTITY-01 — authenticated principal → current session → authentication method → provider truth → CYAN identity projection
DATE: 2026-10-03 · BASE: `origin/frontend-symbiotic` @ `5feba9cce76b043c8813f11c4fda25e3d51581ac` (docs over `checkpoint-AUTH-CYAN-03` `bd6534c`)
AUTHORITY: `HA-AUTH-CYAN.md` → HA-AUTH-CYAN-IDENTITY-01 (2026-10-03).

## Exact relation
```text
AUTHENTICATED PRINCIPAL   /auth/me ok → userId                         (the only identity source; the page's existing gate)
→ CURRENT SESSION         /auth/sessions: exactly one session.current   (never newest / last / lastAuthenticatedAt)
→ AUTHENTICATION METHOD   /auth/methods: exactly one ACTIVE method of the current session's methodType
→ PROVIDER TRUTH          /auth/providers joined on provider.providerId → server-owned label, else the raw id
→ CYAN IDENTITY PROJECTION inside the existing "Identity and access" proof chamber of the Workspaces field
```
Every read goes through the typed client of AUTH/CYAN-01; every throw becomes a null read; every part of the
projection is `none` until its own read legitimately produced it.

## Producer
Unchanged: PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (live assembly `auth-aa32c4d-20261001T081014Z`).
The authorization records REAL_GOOGLE_LOGIN = PROVEN and REAL_GOOGLE_LINK = PROVEN on the live system for the same
pre-existing identity (GOOGLE_OIDC ACTIVE beside LOCAL_PASSWORD ACTIVE). This unit did not read the live relation; it
consumes the already-typed shapes. No PURPLE change, nothing deployed.

## Delta (CYAN)
| File | Change |
|---|---|
| `apps/web/lib/field/identityProjection.ts` (new) | pure `identityProjectionFrom(reads)` → `{identity, session, authentication, providerAccount}`; `authenticationWords` (Local password · server-owned label · raw provider id); `LOCAL_PASSWORD_LABEL`; `NO_IDENTITY_PROJECTION` |
| `apps/web/lib/field/useIdentityProjection.ts` (new) | after the page's `/auth/me` verdict: `listSessions`, `listMethods`, `listProviders` in parallel, each throw → null; React state only |
| `apps/web/components/field/IdentityProjection.tsx` (new) | inside the chamber: Authenticated identity (token + copy, unchanged primitive) · Current authentication · Provider account ("an attribute of the provider method, not your nquiry identity") · Session ("current · authenticated", instants as data); nothing for an unauthenticated projection; no control, link, role, authority, name, avatar |
| `apps/web/app/workspaces/page.tsx` | `useIdentityProjection(identity)`; the chamber's former `Identifiers` line is now rendered by `IdentityProjection` (same label, same token, new test id); orbit, founding form, `/auth/me` gate, `exit={identity ? <LogoutButton/> : null}` untouched |
| `apps/web/app/globals.css` | `.auth-relation`, `.auth-line`, `.auth-note` (existing tokens; the chamber vocabulary) |
| `apps/web/tests/field/identityProjection.test.tsx` (new) | 18 falsifiers (proofs 1–16) incl. source laws (no provider literal, no email-domain inference, no sort/last-element/lastAuthenticatedAt selection, no role/authority/permission/membership, no name/avatar) |
| `apps/web/tests/e2e/cy08-identity.spec.ts` (new) | 12 browser falsifiers × desktop + Pixel 7 |
| `apps/web/playwright.sf01.config.ts` | mobile project regex now includes `cy08` |
| `apps/web/scripts/auth-identity01-mutation-proof.mjs` (new) | 7 mutations, byte-identical restore |
| `docs/implementation/field-reports/AUTH-CYAN/` | this record, `HUMAN_REVIEW_GUIDE_AUTH_CYAN_IDENTITY_01.md`, `browser-evidence/identity-01/SUMMARY.md` (+ untracked screenshots), HA record |
Not touched: `authClient.ts`, the login page, provider contact, auth boundary, the rail (`FieldFrame`, `Identity`, `LogoutButton`), every other component/route, PURPLE, RED, production.

## Laws and where they hold
| Law | Materialization |
|---|---|
| `/auth/me` is the only identity source | without an `ok` verdict the whole projection is `NO_IDENTITY_PROJECTION`, whatever sessions/methods say (unit + browser: the page leaves for `/login`) |
| current session only from `current = true`, at most one | filter on `current`; zero or two → none; the older session marked current wins over the newest (unit + browser); M1 killed |
| methodType from the current session / authoritative method relation | the one ACTIVE method of the session's type; two candidates, a revoked one, a null methodType or a provider-type method without its provider attribute → no claim |
| Google label only from parsed provider truth | join on `providerId`; providers null/empty/other → the raw id `google`, never "Google"; label changes with the server's label; no provider literal in the sources; M2 killed |
| provider email = method attribute, not canonical identity | its own line "Provider account" with the sentence; the identity token is always the userId and never contains "@"; M3 killed |
| no role / authority / permission | none in markup or sources (regex laws); M4, M5 killed |
| failed method fetch → no "via" claim | methods null/denied → session stays, authentication none; M6 killed |
| unknown methodType → no friendly label | the typed parser refuses it (the derivation never sees it); M7 killed at the parser |
| human-facing name NOT_MATERIALIZED | no name/avatar/initials tokens anywhere (source law) |
| organism primary, access projection and Logout unchanged | browser: Workspaces core, orbit, founding form, Log out visible; no `a/form/select` inside the chamber; projection within the plane; no sideways scroll |

## Proof
| Lane | Result |
|---|---|
| Focused unit falsifiers `tests/field/identityProjection.test.tsx` | **18 / 18** |
| authClient preservation `tests/lib/authClient.test.ts` | 149 / 149 (unchanged) |
| Full unit suite (gates laws incl. `app/workspaces/page.tsx`) | **606 / 606** (35 files) |
| Mutation proof `scripts/auth-identity01-mutation-proof.mjs` | **7 / 7 killed**, byte-identical restore: M1 newest-as-current · M2 Google hard-coded from GOOGLE_OIDC · M3 provider email as canonical identity · M4 role inferred · M5 authority inferred · M6 failed method fetch still "via Google" · M7 unknown methodType → friendly value (M3 survived once: the token's value was not asserted; the test now checks the token equals the userId and carries no "@") |
| Mocked browser lane `cy08-identity` (desktop + Pixel 7) | **24 / 24** |
| Preservation lanes in the same run: `workspaces.spec` (desktop), `auth.spec` (desktop), `cy06-provider`, `cy07-auth-boundary` (both devices) | **68 / 68** (92 in total with cy08) |
| `tsc --noEmit`, `eslint .` | clean (1 pre-existing warning, untouched file) |
| Review runtime `127.0.0.1:13500` | relation presented on both devices (`browser-evidence/identity-01/SUMMARY.md`) |
| Not run, by authorization | live relation read, production login, deployment |

## Status
FBR AUTH/CYAN-IDENTITY-01: TECHNICALLY CLOSED. **READY_FOR_HUMAN_FRONTEND_REVIEW** (`HUMAN_REVIEW_GUIDE_AUTH_CYAN_IDENTITY_01.md`).
Not FIELD_GREEN, not REVIEWED_FIELD, not PUBLISHED_FIELD, not merged, not deployed.

**Claim ceiling:** AUTHENTICATED IDENTITY = PRESENTED BY CYAN · CURRENT AUTHENTICATION METHOD = PRESENTED BY CYAN ·
CURRENT SESSION PROVENANCE = PRESENTED BY CYAN. Still: HUMAN-FACING NQUIRY DISPLAY NAME = NOT MATERIALIZED ·
AUTHENTICATION != AUTHORIZATION · IDENTITY != ROLE · IDENTITY != AUTHORITY · ACCOUNT MANAGEMENT = NOT MATERIALIZED BY
THIS WORK UNIT.

**Next FBR:** none defined by this unit; no further AUTH/CYAN Work Unit is authorized.

## Checkpoint
| | Value |
|---|---|
| Field commit | `bf66e4588b338f849b205f84acd3fc559110c8a7` (tree `f6953bd55df8f1d2123c9c270289f367fe71c7ad`) |
| Tag | `checkpoint-AUTH-CYAN-IDENTITY-01` → tag object `aab7fbe371478875747d769f63242ca335a97ddb` → `bf66e45` |
| Remote | `origin/frontend-symbiotic` = `bf66e45` (+ this docs commit); tag pushed |
| Producer | PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (unchanged) |
