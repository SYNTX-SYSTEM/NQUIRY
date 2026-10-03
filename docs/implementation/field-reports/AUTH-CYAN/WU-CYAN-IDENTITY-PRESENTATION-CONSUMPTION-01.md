# WORK UNIT REPORT
FIELD: NQUIRY_IDENTITY_PRESENTATION_CONSUMPTION_FIELD
WORK_UNIT: CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01 — PURPLE human identity presentation → composed CYAN identity field
DATE: 2026-10-04 · BASE: `origin/frontend-symbiotic` @ `27f344c5744ebda10943885cda035ac675402f6b` (docs over `checkpoint-CYAN-MOUNT-01` `09f5f0e`)
AUTHORITY: `HA-AUTH-CYAN.md` → HA-CYAN-IDENTITY-PRESENTATION-CONSUMPTION-01 (2026-10-04). PURPLE producer: `auth-identity` @ `2ec05c0` (HD-AUTH-07), live as assembly `auth-2ec05c0-20261003T223212Z`.

## Field (before the delta)
| Relation | State at the base |
|---|---|
| PURPLE_HUMAN_IDENTITY_PRESENTATION → CYAN_IDENTITY_PROJECTION | **absent**: CYAN consumed `/auth/me` (userId) only; the userId was the primary human-facing label |
| IDENTITY_TRUTH + AUTH_SESSION_TRUTH + PROVIDER_TRUTH → COMPOSED_HUMAN_PRESENTATION | **absent**: the authentication relation existed (AUTH/CYAN-IDENTITY-01) without a human identity |
| current session → current method → provider account (AUTH/CYAN-IDENTITY-01, field repair) | proven, preserved |
| typed PURPLE contracts (AUTH/CYAN-01), provider contact (-02), `?auth=` boundary (-03), frontend mount (MOUNT-01) | proven, preserved |

## Delta (CYAN only; no PURPLE, no production change)
| File | Change |
|---|---|
| `apps/web/lib/api/authClient.ts` | `IdentityPresentationResult` (`ok {userId, displayName, canonicalEmail}` exact keys, UUID, non-empty strings · `denied NO_SESSION`), `parseIdentityPresentation`, `fetchIdentityPresentation` (`GET /auth/identity`, credentials included) |
| `apps/web/lib/field/identityProjection.ts` | `IdentityReads.identity`; `identity.presentation` = `presented {displayName, canonicalEmail}` ONLY when `/auth/identity` is `ok` for the SAME principal `/auth/me` verified, else `none`; everything else unchanged (pure composition) |
| `apps/web/lib/field/useIdentityProjection.ts` | the identity read joins the three reads (four in parallel, every throw → null); still the one producer for both organisms |
| `apps/web/components/field/IdentityPanel.tsx` | WHO (nquiry identity: displayName primary, canonicalEmail secondary) → HOW (Signed in with) → PROVIDER (account of the CURRENT provider method) → Log out; STATE D: "Authenticated" + short technical id; STATE E: identity + "Authenticated", no method |
| `apps/web/components/field/IdentityProjection.tsx` | NQUIRY IDENTITY → TECHNICAL IDENTITY (`<details>`, collapsed when a presentation exists, open otherwise; the copyable userId token) → CURRENT AUTHENTICATION with its account object → SESSION |
| `apps/web/app/globals.css` | `.identity-who/.identity-name/.identity-email`, the technical-identity disclosure, the panel's who/how blocks |
| tests: `tests/lib/authClient.test.ts` (+14), `tests/field/identityProjection.test.tsx` (+10 field falsifiers, 2 pre-producer laws narrowed), `tests/field/mount.test.tsx` (reads shape), `tests/e2e/cy08-identity.spec.ts` (identity route; F2/F6, F3/F4, F8/STATE D, F9/STATE E; successor truths), `scripts/auth-identity01-mutation-proof.mjs` (+P1–P15, five earlier anchors re-anchored) |

## Semantic falsifiers (all proven)
| F | Where | Result |
|---|---|---|
| F1 local current → name, canonical email, Local password, no Google, no provider email | unit STATE A; browser "local-password session" | ✓ |
| F2 Google current → same name/email, Google, provider email | unit STATE B; browser "Google session" + "DIFFERENT provider email" | ✓ |
| F3/F4 switch Google ↔ local → identity identical, only the provider relation changes | unit; browser "switching Google → local" (through the real logout/login transition, nothing cached) | ✓ |
| F5 Google linked, local current → no provider account | unit STATE C; browser local case | ✓ |
| F6 canonical email ≠ provider email → both in their positions (identity above authentication, account beneath it) | unit; browser (`tobias@thescaleforge.com` before `syntxsystem@protonmail.com` in both organisms) | ✓ |
| F7 equal strings → still separately labelled | unit | ✓ |
| F8 identity read unavailable / denied / foreign principal → "Authenticated", technical id open, provider email never the identity | unit STATE D; browser STATE D | ✓ |
| F9 method unavailable → identity visible, no method, no provider email | unit STATE E; browser STATE E | ✓ |
| F10 rail and chamber = one composition (same name, email, method, provider; components read no client; the hook feeds both) | unit source + markup law | ✓ |
| F11 userId remains technical evidence, not the primary label | unit (details collapsed, order); browser (`identity-user-id` present) | ✓ |
| F12 no role/membership/authority in the identity field | unit source + markup laws; gates laws | ✓ |
| F13/F14 desktop and Pixel 7 coherent, no overlap | browser lane both projects (rail panel inside the header, never over the mark, no sideways scroll) | ✓ |
| F15 parser accepts the exact production shape | `parseIdentityPresentation` live-shaped fixture; 12 parser falsifiers | ✓ |
| SEMANTIC_ERROR_07–09 no derivation of name/email from email, login input or provider email | source laws (`split("@")`, `canonicalEmail: …provider/email/login` forbidden); M7/M11 | ✓ |

## Proof
| Lane | Result |
|---|---|
| Focused units: `authClient` 163 / 163 · `identityProjection` 36 / 36 · `mount` 10 / 10 | **209 / 209** |
| Full unit suite (36 files, gates laws) | **648 / 648** |
| Browser `cy08-identity` (desktop + Pixel 7) with `workspaces`, `auth` | **56 / 56** |
| Preservation `cy06-provider`, `cy07-auth-boundary` (both devices) | **52 / 52** |
| Review-mount lane (`mount-review`, :3302, both devices) | **8 / 8** |
| `tsc --noEmit`, `eslint .` | clean |
| Mutation proof `scripts/auth-identity01-mutation-proof.mjs` | **30 / 30 killed**, byte-identical restore: M1–M16 (AUTH/CYAN-IDENTITY-01) + P1 provider email replaces canonicalEmail · P2 local login hides the displayName · P3 Google login replaces the displayName · P4 userId primary despite displayName · P5/P6 linked/unbacked provider account shown · P7 email local part as displayName · P8 rail fetches its own truth · P9 rail/body labels diverge · P10 identity failure falls back to the provider email · P11 foreign principal's identity accepted · P12 role leaks · P13 authority leaks · P14 provider label hard-coded · P15 previous state survives (browser-killed) |
| Not performed | real login of any kind; production cutover; PURPLE change |

## Field reconstruction (after the delta)
```text
PURPLE  /auth/me        → AUTHENTICATED PRINCIPAL (userId)                       verdict, unchanged
PURPLE  /auth/identity  → NQUIRY IDENTITY (displayName, canonicalEmail)         NEW consumption; same principal only
PURPLE  /auth/sessions  → CURRENT SESSION → methodType                           unchanged
PURPLE  /auth/methods   → CURRENT METHOD → PROVIDER RELATION (providerId, email) unchanged
PURPLE  /auth/providers → provider label                                         unchanged
        ──────────────── identityProjectionFrom (pure) ────────────────
CYAN    IdentityPanel (rail) · IdentityProjection (chamber) = WHO → HOW → PROVIDER → SESSION → LOGOUT, one composition
```
Changed: only the two relations named as broken. No authorization, role, membership or authority enters the field.

## Status
CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01: TECHNICALLY CLOSED (LOCAL_GREEN for the field scope; mocked lanes; the
staged candidate is rebuilt from this checkpoint against live PURPLE read-only contacts for the human's real review).
Claim ceiling: NQUIRY HUMAN IDENTITY, DISPLAY NAME, CANONICAL NQUIRY EMAIL, CURRENT AUTHENTICATION METHOD = PRESENTED
BY CYAN · CURRENT PROVIDER ACCOUNT = PRESENTED WHEN APPLICABLE · USER ID = TECHNICAL IDENTITY EVIDENCE · AUTHENTICATION
!= AUTHORIZATION · IDENTITY != ROLE · IDENTITY != AUTHORITY · PRODUCTION ROOT CUTOVER = NOT AUTHORIZED · HUMAN FRONTEND
ACCEPTANCE = PENDING UNTIL REAL E2E (CASE LOCAL, CASE GOOGLE on `/cy-review/`).

## Checkpoint
| | Value |
|---|---|
| Field commit | `bfd530016e4e25e761ecb0e3a04c0b8817e95f93` (tree `96bc4ec750cd58ff3fc15f96393de9ae9b7acf07`) |
| Tag | `checkpoint-CYAN-IDENTITY-PRESENTATION-01` → tag object `b02e6934280c57e5fc1dd30094c49f538fbdc2b2` → `bfd5300`; pushed |
| PURPLE producer | `auth-identity` @ `2ec05c03f55ee1b0dfc08a952fa508edae0c983a` (live assembly `auth-2ec05c0-20261003T223212Z`) |
