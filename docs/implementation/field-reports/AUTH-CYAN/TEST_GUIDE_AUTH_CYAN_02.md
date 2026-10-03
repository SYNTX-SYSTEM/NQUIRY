# TEST GUIDE — AUTH/CYAN-02 · provider contact on the Access Field

**Field:** PURPLE_AUTH ↔ CYAN_FRONTEND (producer Architecture 24 on `auth-identity`; consumer line `frontend-symbiotic`)
**Status of the Work Unit:** FIELD_GREEN_WITH_DISCLOSED_CEILINGS · TECHNICALLY_CLOSED · HUMAN_FRONTEND_ACCEPTED ·
CHECKPOINTED (`checkpoint-AUTH-CYAN-02`). NOT REVIEWED_FIELD. NOT PUBLISHED_FIELD. Not merged, not deployed.
**Authority:** `HA-AUTH-CYAN.md` → HA-AUTH-CYAN-02 (2026-10-03). **Human review:** `HUMAN_REVIEW_RESULT_AUTH_CYAN_02.md`
(ACCEPTED, 2026-10-03).
**This document:** a self-contained, reproducible test manual (documentation only; it changes nothing).

## 1. The relation materialized

```text
PURPLE provider truth                     GET /auth/providers on the live PURPLE API (auth-identity @ aa32c4d)
→ CYAN typed auth/provider contract       apps/web/lib/api/authClient.ts :: listProviders / parseProviderList / googleLoginStart   (AUTH/CYAN-01)
→ provider availability projection        apps/web/lib/field/providerContact.ts :: providerContactFrom / discoverProviderContact   (AUTH/CYAN-02)
                                          apps/web/lib/field/useProviderContact.ts (one discovery per mount, React state only)
→ provider contact on the Access Field    apps/web/components/field/ProviderContact.tsx, mounted in apps/web/app/login/page.tsx
```

Only this relation. Laws preserved, verbatim:

```text
AUTHENTICATION != AUTHORIZATION      LOGIN != LINK                 LINK != ACCOUNT_CREATION
GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN                            API_LIVE != GUI_MATERIALIZED
PROVIDER_OUTPUT != CYAN_INFERENCE    UNKNOWN != AVAILABLE
```

Out of scope, by authorization: account linking, account creation, recovery, methods/sessions management, unlink,
logout-all, any PURPLE change, a real Google callback, a deployment, the `?auth=` projection (AUTH/CYAN-03).

## 2. Checkpoint identities (verified from Git, 2026-10-03)

| Object | Identity |
|---|---|
| Base | `origin/frontend-symbiotic` @ `dd0b8d936b849a7ad536f517a23eec6cf29fa126` (AUTH/CYAN-01 test guide, over `checkpoint-AUTH-CYAN-01` `5877c13`) |
| Product checkpoint | **`checkpoint-AUTH-CYAN-02`** → tag object `7ecf17c708c4620246a4692621499ab4127c61c8` → commit `b8e7b2110422d9c9d93b86d85e6284e4b4eb1887` (tree `412aa5f2f734a856f8b47f7f28ec1192f59599b0`) |
| Docs commits after the checkpoint | `5347a999bcb57256b808bda094e24cfe13d4e786` (checkpoint identity recorded), `dfd95d9754903e516a72cd6572fbfbdb0d7931f4` (Human Frontend Acceptance) |
| Producer (unchanged since AUTH/CYAN-01) | PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9`; live assembly `auth-aa32c4d-20261001T081014Z` |

Verify:

```bash
git rev-parse checkpoint-AUTH-CYAN-02 checkpoint-AUTH-CYAN-02^{commit} checkpoint-AUTH-CYAN-02^{tree}
git show --stat --format= checkpoint-AUTH-CYAN-02      # 13 files, 628 insertions, 6 deletions (list in §16)
git log --oneline dd0b8d9..origin/frontend-symbiotic    # dfd95d9 record(acceptance) · 5347a99 record(identity) · b8e7b21 field(AUTH/CYAN-02)
```

## 3. Prerequisites

- `apps/web` toolchain installed; Playwright browsers installed; port `3301` free. Port `3000` is normally held by the
  foreign docker container `nquiry-web-1` and must not be used (the default Playwright config would adopt it).
- For the visual review: the local review runtime `nquiry-cy01-inspect-runner` on `127.0.0.1:13500` (§10). No
  credentials are needed anywhere in this guide; never enter production credentials in the review runtime.

## 4. The product surface

The existing Access Field (`/login`, `main.access-field` → `section.access-core`, `data-testid="access-core"`):

| Element | Test id | Unchanged / new |
|---|---|---|
| eyebrow "Access", title "Log in to nquiry", lede | — | unchanged |
| Email, Password inputs; **Log in** submit | `login-email`, `login-password`, `login-submit` | unchanged (SF-05 attention/focus laws intact) |
| pending line "Requested. Not yet authenticated…"; boundary line (`role=alert`) | `login-pending`, `login-error` | unchanged |
| separator **or** (`.access-provider-rule`) and **Continue with Google** (`<a class="button secondary access-provider-action">`) | `provider-contact`, `provider-google` (`data-provider-id="google"`, `data-proof-class="PRODUCTION_PROVIDER"`) | **new**, inside the core, after the form, before the pending/boundary lines |

The contact is part of the Access Field. It is NOT a second login surface, a provider-management surface, an
account-security surface, account linking, account creation or recovery. There is no new route, panel or dashboard.
The label text is the parsed `label`; a non-production `proofClass` would be named (" · test provider"), never hidden.

## 5. Provider truth (availability only from the parsed contract)

The exact live-shaped fixture, proven by AUTH/CYAN-01 and re-probed read-only on 2026-10-03:

```json
{"kind":"ok","providers":[{"providerId":"google","label":"Google","proofClass":"PRODUCTION_PROVIDER"}]}
```

Field names and values are those of the checkpoint (`parseProviderList`: exact keys `providerId`, `label`,
`proofClass`; `proofClass ∈ {PRODUCTION_PROVIDER, TEST_PROVIDER}`). The only path to a contact is
`providerContactFrom(list, next)` = `googleLoginStart(list, next)` on a PARSED, branded list. No source of this unit
names `google`, a label or a proof class as a literal (unit law "never name google … as a literal"; mutation M1/M6).
Nothing beyond the parsed response is inferred: no provider → no contact; the contact proves no login.

## 6. Fail-closed matrix (proven in unit + browser)

| Case | Discovery result | Rendering | Unit | Browser (desktop + Pixel 7) |
|---|---|---|---|---|
| unknown response kind (`"providers"`, `"denied"` on the list route) | `none` | nothing | ✓ | ✓ |
| malformed: unknown `proofClass` (`PROVEN`, `PROVEN_PROVIDER`) | `none` | nothing | ✓ | ✓ |
| malformed: missing `proofClass` | `none` | nothing | ✓ | — |
| extra / forbidden fields (`available`, `googleAvailable`, `clientSecret`) | `none` | nothing | ✓ | ✓ (`googleAvailable`) |
| `denied NO_SESSION` | `none` | nothing | ✓ | ✓ |
| `unavailable PROVIDER_NOT_CONFIGURED` (503) | `none` | nothing | ✓ | ✓ |
| empty provider list | `none` | nothing | ✓ | ✓ |
| only another provider (`test`) | `none` | nothing | ✓ | — |
| non-JSON body (502/503 HTML) | `none` | nothing | ✓ | ✓ |
| network failure (rejected fetch / connection refused) | `none` | nothing | ✓ | ✓ |
| `null` body | `none` | nothing | ✓ | — |
| unsafe `next` (`https://…`, `//…`) | `none` (builder refuses `UnsafeNextTarget`; derivation fails closed) | nothing | ✓ | — |

In every browser case the local login stays intact and `access-core` stays `data-core-state="current"`. No unknown
state becomes provider availability (`UNKNOWN != AVAILABLE`).

## 7. Local password preservation

| Proven | Where |
|---|---|
| form, inputs and **Log in** still present and empty on load | `cy06-provider` (`expectLocalLoginIntact`), `auth.spec.ts` "never renders any pre-filled credential" |
| local submit behaviour unchanged (`login(email, password)` → `router.replace("/")`, denied/rejected/network boundaries) | unit source law (proof 6), `auth.spec.ts` 6/6, `sf05-field.spec.ts` Login field 6/6 |
| F02 login request unchanged (`POST /auth/login`, JSON body, credentials included) | `tests/lib/authClient.test.ts` 149/149 (F02 tests verbatim) |
| pending/boundary presentation unchanged (`login-pending`, `login-error`, core states loading/boundary) | `sf05-field.spec.ts` "a request is not a success", `cy06-provider` "denied verdict stays a boundary; the contact stays" |
| the contact does not replace the local login (placed after the form; one form, one core) | `cy06-provider` counts: one `access-core`, one `main form`, one `/auth/oidc/` anchor |

## 8. Typed login start

- `Continue with Google` is `<a href={url}>` with `url = loginStartUrl(provider, "/")` from AUTH/CYAN-01, i.e.
  `${API}/auth/oidc/google/start?next=%2F` (GET navigation; the API answers 303 to the provider). `"/"` is the same
  destination the local login uses (`/` re-checks the session and routes onward).
- No hand-built URL: the derivation, hook and component contain no `/auth/oidc`, `/start`, `/link` or `apiBaseUrl`
  text (unit law; mutations M4, M5).
- No link-start route: the browser proves exactly one `GET …/auth/oidc/google/start?next=%2F` on activation, no POST,
  no `/link/` (`cy06-provider` "activating the contact…").
- No unsafe `next` forwarding: §6 last row.
- No real callback proof: nothing in this unit follows the provider redirect.

## 9. Automated proof procedure (from `apps/web`)

Steps 1–5 are read-only; step 6 writes and restores sources and must run alone.

```bash
cd apps/web
# 1. provider-contact falsifiers (proofs 1–10)
npx vitest run tests/field/providerContact.test.tsx --reporter=dot          # expect 26 passed
# 2. authClient preservation (AUTH/CYAN-01 + F02)
npx vitest run tests/lib/authClient.test.ts --reporter=dot                  # expect 149 passed
# 3. full unit suite incl. the gates laws over app/login/page.tsx
npx vitest run --reporter=dot                                                # expect 561 passed / 33 files (or more after later WUs)
# 4. TypeScript and ESLint
npx tsc --noEmit -p .                                                        # exit 0, no output
npx eslint .                                                                 # 0 errors (1 pre-existing warning in components/field/Identity.tsx)
# 5. mocked browser lane on the ISOLATED :3301 server, desktop + Pixel 7
npx playwright test -c playwright.sf01.config.ts tests/e2e/cy06-provider.spec.ts \
  --output=/tmp/pw-auth02 --reporter=line                                    # expect 22 passed
npx playwright test -c playwright.sf01.config.ts tests/e2e/auth.spec.ts --project=desktop \
  --output=/tmp/pw-auth02-auth --reporter=line                               # expect 6 passed
npx playwright test -c playwright.sf01.config.ts tests/e2e/sf05-field.spec.ts --grep "Login field" \
  --output=/tmp/pw-auth02-sf05 --reporter=line                               # expect 6 passed (3 × desktop, 3 × Pixel 7)
# 6. mutation proof (writes and restores 3 source files + the login page; run alone)
node scripts/auth02-mutation-proof.mjs                                       # expect "6/6 mutations killed", every row "restored byte-identical: true", exit 0
# 7. remove what `next dev` leaves behind before any commit
git -C ../.. checkout -- apps/web/next-env.d.ts; rm -f AGENTS.md CLAUDE.md
```

Why `--output=/tmp/…`: `apps/web/test-results/sf01-real-stack/` is root-owned. Why the sf01 config: it starts its own
server on `:3301` and never adopts a foreign one.

### Browser falsifiers (`tests/e2e/cy06-provider.spec.ts`, 11 × 2 devices)
| # | Falsifier |
|---|---|
| B1 | contact from the live-shaped body: visible, text "Continue with Google", `href` = typed start URL, `data-proof-class`, inside the core; one core, one form, one `/auth/oidc/` anchor, no `/link/`; URL stays `/login`; contact within the core, core within the viewport, `scrollX` stays 0 after a sideways scroll attempt |
| B2 | activation = exactly one `GET …/start?next=%2F`, never POST, never `/link/` |
| B3–B10 | malformed (unknown proofClass), malformed (extra availability field), unknown kind, denied, unavailable, empty list, non-JSON 502, network failure → no contact, local login intact, core `current` |
| B11 | denied local login with the contact present: boundary shown, core `boundary`, contact still visible |

## 10. Local visual review runtime

```text
http://127.0.0.1:13500/login          container nquiry-cy01-inspect-runner (loopback only); no credentials required
```

Boundary of this runtime: it serves the pinned RED producer (`checkpoint-PFC-PCPG-18`, `41b4324`) plus this unit's
CYAN tree. The RED producer does not expose the live PURPLE AUTH routes. Therefore the review proxy (runtime-only,
not in the repository) supplies provider discovery as a labelled FIXTURE_NON_PROOF copy of the live-shaped body
(header `x-nquiry-review-fixture: FIXTURE_NON_PROOF live-shape copy 2026-10-03` on `GET /api/auth/providers`), and the
typed login-start route `GET /api/auth/oidc/google/start` leads to an explicit **Review Boundary** page. The Review
Boundary is NOT a Google login result: it states that the provider start is not available in this runtime, that no
login is proven (`GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN`) and links "Back to the Access Field".

Check the fixture label before reviewing:

```bash
curl -s -D - http://127.0.0.1:13500/api/auth/providers | grep -iE 'x-nquiry-review-fixture|^\{'
```

Evidence of the automated pass over this runtime: `browser-evidence/auth-02/SUMMARY.md` (screenshots untracked).

## 11. Manual tests

**A — Initial Access Field.** Open `http://127.0.0.1:13500/login`. Expected: the existing Access Field is visually
primary; Email, Password, **Log in** visible; separator **or**; **Continue with Google** below it inside the core; no
second login surface, no provider-management UI, no account-security UI, no visual break caused by the contact.

**B — Provider contact.** Inspect **Continue with Google**. Expected: it sits inside the existing Access core
(`data-testid="provider-google"`, `data-provider-id="google"`, `data-proof-class="PRODUCTION_PROVIDER"`); the label is
the parsed provider label; the control is outlined/secondary, the filled **Log in** stays first and primary; the local
password login remains available; nothing implies authority, a role or an account link.

**C — Login start boundary.** Click **Continue with Google**. Expected navigation: the typed Google login-start route
`/api/auth/oidc/google/start?next=%2F` (GET). Expected local result: the explicit Review Boundary page stating that the
provider start is not available in this review runtime and that no login is proven. Expected absences: no fake
callback, no simulated success, no account creation, no login success claim.

**D — Return path.** Click **Back to the Access Field**. Expected: the original Access Field returns; the local login
is intact and empty; **Continue with Google** is presented again exactly as before; no broken navigation state; no
second auth surface.

**E — Fail-closed (optional).** Block `/api/auth/providers` in devtools and reload: the contact disappears, the local
login is untouched.

## 12. Human Frontend Review

Authoritative result: `HUMAN_REVIEW_RESULT_AUTH_CYAN_02.md` (2026-10-03, local review runtime, the Human Visual
Authority for the frontend). **HUMAN_FRONTEND_ACCEPTANCE = ACCEPTED.** Observed there: the Access Field remained
visually primary; the local password login remained intact; the Google provider contact was integrated into the
existing login field; the "or" separation was visually clear; no second login surface; no account-security or
provider-management UI; the contact navigated through the typed login-start route; the runtime stopped at the explicit
Review Boundary, which clearly stated that Google login was not proven; no fake callback or simulated login; "Back to
the Access Field" returned correctly; the contact remained available after the return; no provider-contact-caused
visual overflow was observed on desktop; `GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN` remained preserved. The result file
is the record; this section does not replace it.

## 13. Automated proof results (as recorded in `WU-AUTH-CYAN-02.md`, verified 2026-10-03)

| Lane | Result |
|---|---|
| Provider-contact falsifiers (`tests/field/providerContact.test.tsx`) | **26 / 26** |
| authClient preservation (`tests/lib/authClient.test.ts`) | **149 / 149** |
| Full unit suite including the login-field gate laws (33 files) | **561 / 561** |
| Browser lane `cy06-provider`, desktop + Pixel 7 | **22 / 22** |
| Existing auth lane (`auth.spec.ts`) | **6 / 6** |
| SF-05 login-field laws (`sf05-field.spec.ts` "Login field"), desktop + Pixel 7 | **6 / 6** |
| TypeScript (`tsc --noEmit`) | clean |
| ESLint | clean (0 errors; 1 pre-existing warning in an untouched file) |

## 14. Mutation proof (`apps/web/scripts/auth02-mutation-proof.mjs`)

**6 / 6 killed; every file restored byte-identical** (sha256 compared before/after each mutation).

| Mutation | What it would allow | Killed by |
|---|---|---|
| M1 hard-coded provider availability (contact without a parsed provider) | a Google contact from nothing | fail-closed and literal laws (4 tests) |
| M2 fail-open discovery (a thrown parse becomes a contact) | malformed/denied/failed → contact | fail-closed matrix (14 tests) |
| M3 fail-open rendering (component renders for `none`) | the contact shown without truth | render-nothing laws (14 tests) |
| M4 link route used as the login-start route | LOGIN presented as LINK | typed-URL law (4 tests) |
| M5 hand-built URL forwarding an unsafe `next` | open redirect candidate sent to the API | unsafe-next law (3 tests) |
| M6 page bypassing the parsed provider contact | the page hard-codes a contact | page source law (1 test) |

## 15. Visual disclosure (Pixel 7)

On Pixel 7 the fixed ambient login-page background (`.field-bg` nebula/starfield) reports a document width of 465 px
against a 412 px viewport, both with and without the provider contact (identical measurements). The Access core itself
fits (24–388 px) and the page is not sideways-scrollable (`scrollX` stays 0 after a sideways scroll attempt). This
condition predates AUTH/CYAN-02 and was not modified because no redesign was authorized. It is not caused by the
provider contact. The browser law of this unit therefore measures the contact, the core and sideways scrollability.

## 16. Files of the checkpoint (`git show --stat checkpoint-AUTH-CYAN-02`: 13 files, +628 −6)

`apps/web/lib/field/providerContact.ts`, `apps/web/lib/field/useProviderContact.ts`,
`apps/web/components/field/ProviderContact.tsx` (new); `apps/web/app/login/page.tsx`, `apps/web/app/globals.css`,
`apps/web/playwright.sf01.config.ts` (changed); `apps/web/tests/field/providerContact.test.tsx`,
`apps/web/tests/e2e/cy06-provider.spec.ts`, `apps/web/scripts/auth02-mutation-proof.mjs` (new);
`docs/implementation/field-reports/AUTH-CYAN/{WU-AUTH-CYAN-02.md, HUMAN_REVIEW_GUIDE_AUTH_CYAN_02.md, HA-AUTH-CYAN.md,
browser-evidence/auth-02/SUMMARY.md}`. Not touched: `authClient.ts`, every other component/route/rail, PURPLE, RED,
the lanes' producer pins, production.

## 17. CLAIM CEILING

```text
PURPLE provider truth      = CONSUMED AND PRESENTED BY CYAN
Google provider contact    = GUI MATERIALIZED

Still:
REAL GOOGLE LOGIN          = NOT PROVEN
REAL GOOGLE CALLBACK       = NOT PROVEN
ACCOUNT LINKING            = NOT MATERIALIZED
ACCOUNT CREATION           = DENIED
AUTHORIZATION              = UNCHANGED

GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN

AUTH/CYAN-02 is:     FIELD_GREEN_WITH_DISCLOSED_CEILINGS · TECHNICALLY_CLOSED · HUMAN_FRONTEND_ACCEPTED
AUTH/CYAN-02 is NOT: REVIEWED_FIELD · PUBLISHED_FIELD
```

## 18. Next First Broken Relation (NOT STARTED · NOT AUTHORIZED)

AUTH/CYAN-03: `?auth=` projection → known failed/cancelled provider-login boundary → Access Field presentation.
Rules: known projection words only (`cancelled, provider_unavailable, provider_error, failed, unavailable`, read by
`readAuthProjection`); unknown shows nothing. Not implemented by this guide or by anything it describes.

## 19. Troubleshooting

| Symptom | Cause | Remedy |
|---|---|---|
| contact missing in the review runtime | proxy fixture not active (header absent on `/api/auth/providers`) | the runtime-only proxy must serve the labelled fixture; the product is behaving correctly (fail closed) |
| contact missing in a mocked lane | `/auth/providers` not routed or routed with a non-live shape | that is the fail-closed law; route the exact fixture of §5 |
| Playwright `EACCES … test-results` | root-owned lane output | `--output=/tmp/…` |
| Playwright adopts `:3000` | default config + foreign docker container | `-c playwright.sf01.config.ts` |
| mobile project skips `cy06` | the mobile `testMatch` regex lists prefixes explicitly | it includes `cy0[1456]` at this checkpoint |
| mutation proof `ANCHOR MISSING` | a source edited since the proof was written | update the anchor in the WU that changed the source |
