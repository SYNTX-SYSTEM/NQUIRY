# WORK UNIT REPORT
FIELD: NQUIRY_AUTHENTICATION_FIELD × CYAN (complete operational product field)
WORK_UNIT: AUTH/CYAN-RECOVERY-01 — self-service password recovery through verified e-mail: the e-mail verification relation in the Access security chamber, the mail-link landings, the recovery start and reset pages, the login's recovery contact
DATE: 2026-10-06 · BASE: `auth-cyan-reconstruction` @ `920c3df` · PURPLE producer: `auth-identity` @ `d03d5ce` (WU-AUTH-21: production e-mail delivery, `VERIFIED_EMAIL_SELF_SERVICE` admitted in every declared environment, `GET /auth/contacts`)
AUTHORITY: HD-AUTH-10 / HA-AUTH-02 (2026-10-05): "A complete production LOCAL_PASSWORD lifecycle requires legitimate self-service recovery through verified e-mail. This is part of the current Field … Operator-mediated recovery … does not replace the required self-service recovery path."

## Field (before the delta)
| Relation | State |
|---|---|
| a LOCAL_PASSWORD owner who lost the password | no contact in the product; the API's recovery routes (WU-AUTH-11/12) existed but were admitted only in DEVELOPMENT/TEST and no frontend page offered or completed them |
| the identity's verified address (24 §16; the precondition of recovery) | neither shown nor obtainable from the product; the verification challenge had no landing page, so a verification mail had nowhere to send its recipient |
| whether a deployment serves recovery / verification | undiscoverable by the frontend (the producer had no discovery contact; WU-AUTH-21 adds `/auth/contacts`) |
| the mail link | no frontend-owned path existed for it; the producer's `MailLinks` now names `/account/verify-email` and `/recover/reset` (configurable) — this unit materializes exactly those two contacts |

## Delta (CYAN only)
| File | Change |
|---|---|
| `lib/api/authClient.ts` | `fetchAuthContacts` / `parseAuthContacts` (`{kind: ok, recovery, emailVerification}` ∈ AVAILABLE/UNAVAILABLE, closed); `startRecovery` (200 `ok` = the one answer; 503 unavailable `RECOVERY_NOT_AVAILABLE`; 400 rejections), `completeRecovery` (`ok` / denied `RECOVERY_DENIED` one class / `PASSWORD_INVALID`); `startVerification` (`ok {challengeId, expiresAt}`; 401 / 403 / 503 `EMAIL_DELIVERY_FAILED`), `completeVerification` (`ok {email}` / denied classes), `listVerifiedEmails` (`{email, verifiedAt, active}` exact keys); producer pin → `d03d5ce`, liveAssembly → `auth-28e6620-20261005T152356Z` |
| `lib/field/useAuthContacts.ts` | the deployment's contacts read once per page; a failed or malformed read = nothing offered (fail closed) |
| `lib/field/mailLink.ts` | `useMailLink`: the link's query (`challengeId`/`recovery` + `token`) captured ONCE into a module store and removed from the address bar (`history.replaceState`) before any render reads it; nothing persisted; `resetMailLinkCapture` for tests |
| `app/recover/page.tsx` | `/recover`: one address field; the server's one answer ("If this address can recover an account, a message is on its way") for every address; a deployment without recovery says so and sends nothing; back to the login |
| `app/recover/reset/page.tsx` | `/recover/reset`: new password + confirmation (the only local check); submit disabled without the link or while mismatched; `done` → the login (recovery creates no session); denied = one class with "ask for a new link" |
| `app/account/verify-email/page.tsx` | `/account/verify-email`: completes the challenge once (ref-guarded) while logged in, shows the verified address, continues to `/workspaces`; without a session: "log in first, then open the link again"; without the link: incomplete |
| `app/login/page.tsx` | "Forgot your password?" (`<Link href="/recover">`) only when the deployment offers recovery |
| `lib/field/accountSecurity.ts` | `verification: VerificationRelation` — `none` (deployment without verification / no identity) or `{canonicalEmail, verified, verifiedAt, recoveryOffered}`; `verified` = an ACTIVE relation for the canonical address (case-folded), nothing inferred from the method list |
| `lib/field/accountEffects.ts` | `sendVerification` Settlement for the canonical address (nothing else can be sent from the chamber), `SEND_VERIFICATION_RELATION` |
| `lib/field/useIdentityProjection.ts` / `identityProjection.ts` | the two additional reads (`/auth/emails`, `/auth/contacts`) next to the pinned four; `IdentityReads.emails?`, `contacts?` |
| `components/field/AccountSecurity.tsx` | the E-mail section: the canonical address, verified (+ date, "it can recover your password") or unverified (+ "Send verification e-mail"); absent on a deployment without verification |
| `app/workspaces/page.tsx` | the send-verification effect through the page's effect field |
| `app/globals.css` | `.access-recovery` |
| `scripts/run_auth_cyan_real_lane.sh` | the API serves `NQUIRY_RECOVERY_POLICY=VERIFIED_EMAIL_SELF_SERVICE` (capture mail; the TEST outbox stands in for the deployment's provider) |
| tests | `tests/field/accountSecurity.test.tsx` (+V1–V3; the C7 law now also forbids the recovery contacts in the chamber's html and `register|/recover` in its sources), `tests/e2e/cy11-recovery.spec.ts` (V1–V5 × 2 devices), `tests/real-stack/cy09-account-security.real.spec.ts` (+1 real case: verification → recovery), `playwright.sf01.config.ts` (cy11 on the phone project) |

## Proof
| Lane | Result |
|---|---|
| vitest | **678 / 678** |
| tsc · eslint | clean (3 pre-existing warnings) |
| mocked lane cy11 (sf01 config) | **10 / 10** (5 × desktop, 5 × Pixel 7) |
| **cross-lineage REAL lane** (`scripts/run_auth_cyan_real_lane.sh`, PURPLE `d03d5ce`, head `e3a5c7d9f1b4`, `nquiry_purple_real`): LOCAL → LINK → LINKED → UNLINK · SESSIONS · PROVIDER_BOOTSTRAP · PASSWORD ROTATION · ROSTER · LOCKOUT · **E-MAIL VERIFICATION → SELF-SERVICE RECOVERY** (Send from the chamber → the mail's link verifies the canonical address while logged in → the link is single-use → log out → "Forgot your password?" → the one answer for the real and for an unknown address → the reset link sets a new password without creating a session → the old password is refused, the new one logs in → the used reset link is denied) | **14 / 14** (7 × desktop, 7 × Pixel 7) |

## Laws
SERVER CAPABILITY → UI AFFORDANCE (recovery and verification contacts exist only when `/auth/contacts` says so) · DELIVERY != VERIFICATION (the chamber shows the server's relation, never "sent" as "verified") · RECOVERY != LOGIN (the reset creates no session; the page leads to the login) · the one answer at `/recover` (no address is confirmed or denied) · the mail token lives in the link, the capture store and the request — never in the address bar after capture, the DOM, storage or a log · ROTATION != RECOVERY (the chamber rotates; `/recover` recovers) · every verdict is the server's.

## Status
**PROVEN, UNPUBLISHED.** Production serves `cyanroot-2fb7bfa-20261005T152356Z` / `auth-28e6620-20261005T152356Z`; there `/auth/contacts` does not exist yet and no recovery contact is offered. Publication (ASP-03) carries this unit together with PURPLE WU-AUTH-21 and requires the production mail-provider facts (sender identity and submission credentials on the deployment's SMTP service, `NQUIRY_PUBLIC_WEB_BASE_URL`) — an external dependency of the deployment, not of this unit; the code is deployable before them (the contacts stay UNAVAILABLE until the mail sink is configured, and the product says so).
