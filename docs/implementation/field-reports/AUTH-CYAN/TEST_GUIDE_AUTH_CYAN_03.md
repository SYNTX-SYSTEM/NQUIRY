# TEST GUIDE — AUTH/CYAN-03 · provider-login result boundary on the Access Field

**Field:** PURPLE_AUTH ↔ CYAN_FRONTEND (producer Architecture 24 on `auth-identity`; consumer line `frontend-symbiotic`)
**Status of the Work Unit:** FIELD_GREEN_WITH_DISCLOSED_CEILINGS · TECHNICALLY_CLOSED · HUMAN_FRONTEND_ACCEPTED ·
CHECKPOINTED (`checkpoint-AUTH-CYAN-03`). NOT REVIEWED_FIELD. NOT PUBLISHED_FIELD. Not merged, not deployed.
**Authority:** `HA-AUTH-CYAN.md` → HA-AUTH-CYAN-03 (2026-10-03). **Human review:** `HUMAN_REVIEW_RESULT_AUTH_CYAN_03.md`
(ACCEPTED, 2026-10-03; docs-only commit `8d7d5ace49aa4dc9e073b88297c28f9fee274143`).
**This document:** a self-contained, reproducible test manual (documentation only; it changes nothing).

## 1. The relation materialized

```text
?auth= projection                         a provider login's NON-success returns the browser to /login?auth=<word>
                                          (PURPLE http_oidc._login_projection; the browser sees a class, never a code)
→ typed AUTH projection vocabulary        apps/web/lib/api/authClient.ts :: AUTH_PROJECTIONS, readAuthProjection   (AUTH/CYAN-01)
→ known provider-login boundary           apps/web/lib/field/authBoundary.ts :: AUTH_BOUNDARY_MESSAGES, authBoundaryFrom   (AUTH/CYAN-03)
                                          apps/web/lib/field/useAuthBoundary.ts (external-store read of window.location.search)
→ Access Field presentation               apps/web/components/field/AuthBoundary.tsx, mounted in apps/web/app/login/page.tsx
```

Only this relation. Laws preserved, verbatim:

```text
KNOWN     → MAY PRESENT EXACT KNOWN BOUNDARY        UNKNOWN   → PRESENT NOTHING
MISSING   → PRESENT NOTHING                         MALFORMED → PRESENT NOTHING
AUTHENTICATION != AUTHORIZATION        FAILED LOGIN != DENIED AUTHORITY
UNKNOWN != FAILURE                     UNKNOWN != SUCCESS        GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN
```

Out of scope, by authorization: a second auth surface, a modal, account security, provider management, account
linking, account creation, recovery, role or authority presentation, any PURPLE change, a real Google callback, a
deployment, any new surface.

## 2. Checkpoint identities (verified from Git, 2026-10-03)

| Object | Identity |
|---|---|
| Base | `origin/frontend-symbiotic` @ `71515fd4837fbbe51d081da8a875c1cb93dae1f4` (AUTH/CYAN-02 test guide, over `checkpoint-AUTH-CYAN-02` `b8e7b21`) |
| Product checkpoint | **`checkpoint-AUTH-CYAN-03`** → signed tag object `cc323572e29d051c3ceaea4b1d537a042b8effea` → commit `bd6534c424fa2efae77b152d6783dfd45feb8c55` (tree `5d0e2e9023a38b2ae32ae8e2088a264eb4bb82ae`) |
| Docs commits after the checkpoint | `bd8ca7ac9e5a22424326ef679ed6413c938d82b6` (checkpoint identity recorded), `8d7d5ace49aa4dc9e073b88297c28f9fee274143` (Human Frontend Acceptance) |
| Producer (unchanged since AUTH/CYAN-01) | PURPLE `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9`; live assembly `auth-aa32c4d-20261001T081014Z` |

Verify:

```bash
git rev-parse checkpoint-AUTH-CYAN-03 checkpoint-AUTH-CYAN-03^{commit} checkpoint-AUTH-CYAN-03^{tree}
git cat-file -p checkpoint-AUTH-CYAN-03 | grep -c gpgsig            # 1 (signed tag object)
git show --stat --format= checkpoint-AUTH-CYAN-03 | tail -1          # 13 files changed, 534 insertions(+), 4 deletions(-)
git log --oneline 71515fd..origin/frontend-symbiotic                 # 8d7d5ac record(acceptance) · bd8ca7a record(identity) · bd6534c field(AUTH/CYAN-03)
```

## 3. Prerequisites

- `apps/web` toolchain installed; Playwright browsers installed; port `3301` free (`:3000` is a foreign docker
  container and must not be adopted).
- For the visual review: the local review runtime `nquiry-cy01-inspect-runner` on `127.0.0.1:13500` (§10). No
  credentials are needed anywhere in this guide; never enter production credentials in the review runtime.

## 4. The product surface

The existing Access Field (`/login`, `section.access-core`, `data-testid="access-core"`) keeps Email, Password,
**Log in**, the "or" rule and **Continue with Google** (AUTH/CYAN-02) unchanged. AUTH/CYAN-03 adds exactly one element:

| Element | Test id / data | When |
|---|---|---|
| boundary line `<p role="alert" id="auth-boundary" class="read-boundary access-auth-boundary">` with one sentence | `auth-boundary`, `data-projection="<word>"` | only while the local form is idle and `?auth=` resolves to exactly one known word |
| core edge state | `access-core[data-core-state="boundary"]` | same condition (otherwise `current`; `loading` while a local request is pending; `boundary` for a local verdict) |

Placement: after the provider contact, before the pending/verdict lines, inside the core. The form's
`aria-describedby` points at the boundary while it is shown. Nothing else is added: no second login surface, no modal,
no account-security or provider-management surface, no linking, creation, recovery, role or authority presentation,
no URL rewriting.

## 5. The closed `?auth=` vocabulary (read from `authClient.ts` at the checkpoint)

```ts
AUTH_PROJECTIONS = ["cancelled", "provider_unavailable", "provider_error", "failed", "unavailable"]
```

Exactly these five words. The message table of `authBoundary.ts` is keyed by exactly this set (unit law "the message
table covers exactly the closed vocabulary"):

| word | boundary sentence |
|---|---|
| `cancelled` | The provider login was cancelled. No access relation was established. |
| `provider_unavailable` | The identity provider is unavailable right now. No access relation was established. |
| `provider_error` | The identity provider reported an error. No access relation was established. |
| `failed` | The provider login could not be completed. No access relation was established. |
| `unavailable` | Signing in with this provider is not available for this account. No access relation was established. |

Every sentence names a non-success and the absence of an access relation; none contains success, authority, role,
denial, creation or link wording (unit law). `readAuthProjection` returns `unknown` for a repeated parameter and for any
word outside the set; `authBoundaryFrom` turns `none` and `unknown` alike into no boundary. UNKNOWN is never mapped to
`failed`.

## 6. Fail-closed matrix (the authoritative cases of the test suite)

Unit (`tests/field/authBoundary.test.tsx`, all → none, nothing rendered):

| Case | Search |
|---|---|
| missing (empty search) | `` |
| missing (other params only) | `?next=%2F&link=ok` |
| link word on the auth key (LOGIN != LINK) | `?auth=ok` |
| link word `already_linked` | `?auth=already_linked` |
| unknown word | `?auth=success` |
| case variant | `?auth=FAILED` |
| trailing space | `?auth=failed%20` |
| embedded NUL | `?auth=failed%00` |
| script injection | `?auth=%3Cscript%3Ealert(1)%3C%2Fscript%3E` |
| empty value | `?auth=` |
| duplicate identical | `?auth=failed&auth=failed` |
| conflicting values | `?auth=failed&auth=cancelled` |
| malformed key | `?auth%00=failed` |
| key with suffix | `?auth2=failed` |

Browser (`tests/e2e/cy07-auth-boundary.spec.ts`, desktop + Pixel 7; no boundary, no local verdict, core `current`,
form empty, provider contact with its typed URL): missing `/login`; unknown `?auth=success`; link word `?auth=ok`; case
variant `?auth=FAILED`; malformed (script) `?auth=%3Cscript%3E…`; malformed (empty) `?auth=`; duplicate
`?auth=failed&auth=failed`; conflicting `?auth=failed&auth=cancelled`.

## 7. Preservation

| Claim | Proof |
|---|---|
| LOCAL PASSWORD LOGIN = PRESERVED | page source law (form, `login(email, password)`, `router.replace("/")` unchanged); `auth.spec.ts` + SF-05 login-field laws 12/12; browser: with `?auth=failed` a held local request shows `login-pending` and core `loading` while the provider boundary is gone, then the local verdict `login-error` with core `boundary` — never two boundaries |
| GOOGLE PROVIDER CONTACT = PRESERVED | `tests/field/providerContact.test.tsx` 26/26 unchanged; `cy06-provider` 22/22; every cy07 case asserts the contact visible with `href` `…/auth/oidc/google/start?next=%2F`; the boundary is also presented with no provider contact at all |
| PURPLE = UNCHANGED | producer `aa32c4d` unchanged; no PURPLE file in the checkpoint |
| AUTHORIZATION = UNCHANGED | no role/authority/viewer tokens in the new sources; gates laws over `app/login/page.tsx` pass |
| ACCOUNT LINKING = NOT MATERIALIZED | no link vocabulary or link route in sources or markup; `?auth=ok` / `already_linked` present nothing |
| ACCOUNT CREATION = DENIED | live policy `DENIED` is a producer fact; the `unavailable` sentence names the account boundary without creating anything |
| REAL GOOGLE LOGIN / CALLBACK = NOT PROVEN | nothing in this unit follows a provider redirect; the review runtime has no PURPLE routes |

## 8. Automated proof procedure (from `apps/web`)

Steps 1–5 are read-only; step 6 writes and restores sources and must run alone.

```bash
cd apps/web
# 1. focused AUTH projection / typed vocabulary / unknown-malformed-conflicting / preservation falsifiers
npx vitest run tests/field/authBoundary.test.tsx --reporter=dot                 # expect 27 passed
# 2. preservation of the typed contract and the provider contact
npx vitest run tests/lib/authClient.test.ts tests/field/providerContact.test.tsx --reporter=dot   # expect 175 passed (149 + 26)
# 3. full unit suite incl. the gates laws over app/login/page.tsx
npx vitest run --reporter=dot                                                   # expect 588 passed / 34 files (or more after later WUs)
# 4. TypeScript and ESLint
npx tsc --noEmit -p .                                                           # exit 0
npx eslint .                                                                    # 0 errors (1 pre-existing warning in components/field/Identity.tsx)
# 5. mocked browser lanes on the ISOLATED :3301 server
npx playwright test -c playwright.sf01.config.ts tests/e2e/cy07-auth-boundary.spec.ts \
  --output=/tmp/pw-auth03 --reporter=line                                       # expect 30 passed (15 × desktop, 15 × Pixel 7)
npx playwright test -c playwright.sf01.config.ts tests/e2e/cy06-provider.spec.ts \
  --output=/tmp/pw-auth03-cy06 --reporter=line                                  # expect 22 passed
npx playwright test -c playwright.sf01.config.ts tests/e2e/auth.spec.ts tests/e2e/sf05-field.spec.ts \
  --grep "Login field|credentials|root route|logging out|login" --output=/tmp/pw-auth03-auth --reporter=line   # expect 12 passed
# 6. mutation proof (writes and restores authBoundary.ts, AuthBoundary.tsx, login page; run alone)
node scripts/auth03-mutation-proof.mjs                                          # expect "6/6 mutations killed", every row "restored byte-identical: true", exit 0
# 7. remove what `next dev` leaves behind before any commit
git -C ../.. checkout -- apps/web/next-env.d.ts; rm -f AGENTS.md CLAUDE.md
```

### Browser falsifiers (`cy07-auth-boundary.spec.ts`, 15 × 2 devices)
| # | Falsifier |
|---|---|
| B1–B5 | each known word: boundary visible with its exact sentence, `data-projection`, `role=alert`, inside the core, core `boundary`; surface intact (form empty, "Log in", provider contact with the typed URL, one core, one form); URL unchanged; no success wording in `main`; no control inside the boundary; boundary within the core; `scrollX` 0 after a sideways scroll attempt |
| B6–B13 | the eight nothing-cases of §6 |
| B14 | a local login request replaces the provider boundary (pending → local verdict; never two boundaries) |
| B15 | the boundary does not depend on provider discovery (empty provider list: boundary shown, no contact) |

## 9. Automated proof results (from `WU-AUTH-CYAN-03.md`, verified 2026-10-03)

| Lane | Result |
|---|---|
| Focused AUTH projection falsifiers (`tests/field/authBoundary.test.tsx`: known rendering, typed vocabulary, unknown/malformed/conflicting, no success/authority, local-login and Google-contact preservation) | **27 / 27** |
| authClient preservation (`tests/lib/authClient.test.ts`) | **149 / 149** (unchanged by this unit) |
| Google-contact preservation (`tests/field/providerContact.test.tsx`) | **26 / 26** (unchanged by this unit) |
| Full unit suite including the login-field gate laws (34 files) | **588 / 588** |
| Browser lane `cy07-auth-boundary`, Desktop + Pixel 7 | **30 / 30** |
| Browser lane `cy06-provider` (provider-contact preservation), Desktop + Pixel 7 | **22 / 22** |
| Existing auth lane (`auth.spec.ts`, desktop) + SF-05 login-field laws (desktop + Pixel 7) | **12 / 12** (the WU record keeps these two lanes as one figure; no separate split is recorded) |
| TypeScript (`tsc --noEmit`) | clean |
| ESLint | clean (0 errors; 1 pre-existing warning in an untouched file) |

## 10. Mutation proof (`apps/web/scripts/auth03-mutation-proof.mjs`)

**6 / 6 killed; every file restored byte-identical** (sha256 compared before/after each mutation). Names as recorded
by the script:

| Mutation | What it would allow |
|---|---|
| M1 unknown → visible (unknown word presented as failed) | an unknown word shown as a failure |
| M2 failed → success (a success sentence synthesized) | a success claim for a non-success |
| M3 malformed/missing → visible (component renders for none) | a boundary without a known word |
| M4 bypass of the typed vocabulary (own query parsing) | query text read outside `readAuthProjection` |
| M5 page presents the boundary while a local request is in flight | two boundaries / a stale boundary over a pending request |
| M6 page makes the core a success state for a projection | a success state on the core |

### Implementation / proof note
The first draft of `useAuthBoundary` set component state inside an effect and was rejected by ESLint
(`react-hooks/set-state-in-effect`). The final implementation reads `window.location.search` as an external store
(`useSyncExternalStore`, server snapshot empty, re-read on `popstate`), which removed component-owned state for this
projection. Recorded as an implementation note only.

## 11. Local visual review runtime

```text
http://127.0.0.1:13500          container nquiry-cy01-inspect-runner (loopback only); no credentials required
```

The runtime serves the pinned RED producer (`checkpoint-PFC-PCPG-18`) plus this unit's CYAN tree. It has no PURPLE
AUTH routes, so no callback produces the `?auth=` word there: the words are opened directly in the URL. The provider
contact is present through the labelled FIXTURE_NON_PROOF providers answer of AUTH/CYAN-02.

## 12. Manual tests

**A — Known `cancelled` projection.** Open `http://127.0.0.1:13500/login?auth=cancelled`. Expected: a boundary inside
the existing Access Field with the reviewed text "The provider login was cancelled. No access relation was
established."; local email/password login visible; **Continue with Google** visible; the Access Field visually
primary; no second auth surface; no role or authority semantics; no login success implied.

**B — Unknown projection.** Open `http://127.0.0.1:13500/login?auth=unknown_test`. Expected: no authentication
boundary; the Access Field in its normal state (core `current`). UNKNOWN → PRESENT NOTHING: no generic error, no
success, no authority state is invented.

**C — Other known projections.** Open `/login?auth=provider_unavailable`, `/login?auth=provider_error`,
`/login?auth=failed`, `/login?auth=unavailable`. Expected: each maps only to its predefined sentence of §5; the server
meaning is not rewritten or inferred.

**D — Missing projection.** Open `http://127.0.0.1:13500/login`. Expected: no AUTH/CYAN-03 boundary; the normal Access
Field only.

**E — Malformed / conflicting input.** Use the cases of §6 as URLs on the runtime, e.g. `/login?auth=`,
`/login?auth=FAILED`, `/login?auth=ok`, `/login?auth=%3Cscript%3Ealert(1)%3C%2Fscript%3E`,
`/login?auth=failed&auth=failed`, `/login?auth=failed&auth=cancelled`. Expected: fail closed — no boundary unless the
typed reader resolves exactly one known word.

## 13. Human Frontend Review

Authoritative record: `HUMAN_REVIEW_RESULT_AUTH_CYAN_03.md` (2026-10-03, local review runtime, the Human Visual
Authority for the frontend; docs-only commit `8d7d5ac`). **HUMAN_FRONTEND_ACCEPTANCE = ACCEPTED.** Manually observed
there: `?auth=cancelled` renders the legitimate boundary with the exact text visible; the local login remains unchanged;
the Google provider contact remains unchanged; the boundary stays inside the existing Access Field; no second auth
surface; no authority/role semantics; `?auth=unknown_test` renders no boundary, so unknown fails closed; no success
state is synthesized; the Access Field remains visually primary. This section summarizes; the result file is the record.

## 14. Evidence

Root: `docs/implementation/field-reports/AUTH-CYAN/browser-evidence/auth-03/`

| Item | Path | Tracked |
|---|---|---|
| browser summary over the review runtime (known `cancelled`/`unavailable`, unknown `success`, conflicting; both devices; boundary text, core state, inside-core, `scrollX`) | `browser-evidence/auth-03/SUMMARY.md` | yes (commit `bd6534c`) |
| Desktop screenshots: known `cancelled`, unknown | `browser-evidence/auth-03/screenshots/login-cancelled-desktop-1280.png`, `login-unknown-desktop-1280.png` | no (untracked by repository convention; present on the authoring machine only) |
| Pixel 7 screenshots: known `cancelled`, unknown | `browser-evidence/auth-03/screenshots/login-cancelled-pixel-7.png`, `login-unknown-pixel-7.png` | no (untracked; not durable evidence) |
| mutation evidence | the script's own output (`6/6 mutations killed`, byte-identical restore) is recorded in `WU-AUTH-CYAN-03.md`; no separate evidence file exists | — |
| checkpoint identity | `WU-AUTH-CYAN-03.md` → Checkpoint (commit `bd8ca7a`) | yes |
| Human review | `HUMAN_REVIEW_RESULT_AUTH_CYAN_03.md` (commit `8d7d5ac`) | yes |

The durable evidence is the tracked summary, the WU record, the review result and the test suites themselves
(reproducible by §8). The untracked screenshots are illustrations, not proof.

## 15. CLAIM CEILING

```text
KNOWN ?auth= PROJECTION    = PRESENTED BY CYAN

Still:
REAL GOOGLE LOGIN          = NOT PROVEN
REAL GOOGLE CALLBACK       = NOT PROVEN
ACCOUNT LINKING            = NOT MATERIALIZED
AUTHORIZATION              = UNCHANGED

GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN

AUTH/CYAN-03               = FIELD_GREEN_WITH_DISCLOSED_CEILINGS
AUTH/CYAN-03 is NOT:         REVIEWED_FIELD · PUBLISHED_FIELD
```

## 16. Next FBR / open surfaces

**NEXT_FBR = NONE DEFINED BY AUTH/CYAN-03.** Remaining PURPLE contacts with typed CYAN consumption (AUTH/CYAN-01) but
no presentation: methods (`listMethods`), sessions (`listSessions`, `revokeSession`, `logoutAll`), link
(`linkStartAction`, `readLinkProjection`, `unlinkMethod`). Each would create a new user-visible surface and requires
its own explicit authorization and reconstruction. Status: NOT STARTED · NOT AUTHORIZED. No AUTH/CYAN-04 exists.

## 17. Files of the checkpoint (`git show --stat checkpoint-AUTH-CYAN-03`: 13 files, +534 −4)

`apps/web/lib/field/authBoundary.ts`, `apps/web/lib/field/useAuthBoundary.ts`, `apps/web/components/field/AuthBoundary.tsx`
(new); `apps/web/app/login/page.tsx`, `apps/web/app/globals.css`, `apps/web/playwright.sf01.config.ts` (changed);
`apps/web/tests/field/authBoundary.test.tsx`, `apps/web/tests/e2e/cy07-auth-boundary.spec.ts`,
`apps/web/scripts/auth03-mutation-proof.mjs` (new); `docs/implementation/field-reports/AUTH-CYAN/{WU-AUTH-CYAN-03.md,
HUMAN_REVIEW_GUIDE_AUTH_CYAN_03.md, HA-AUTH-CYAN.md, browser-evidence/auth-03/SUMMARY.md}`. Not touched:
`authClient.ts`, `providerContact.ts`, `ProviderContact.tsx`, every other component/route/rail, PURPLE, RED, production.

## 18. Troubleshooting

| Symptom | Cause | Remedy |
|---|---|---|
| boundary never appears in the review runtime | the word was not opened in the URL (no callback exists there) | open `/login?auth=<known word>` directly |
| boundary appears for a word not in §5 | impossible at this checkpoint (unit law + M1/M4) — a later change widened the vocabulary | treat as a regression of the WU that changed it |
| Playwright `EACCES … test-results` | root-owned lane output | `--output=/tmp/…` |
| Playwright adopts `:3000` | default config + foreign docker container | `-c playwright.sf01.config.ts` |
| mobile project skips `cy07` | the mobile `testMatch` regex lists prefixes explicitly | it includes `cy0[14567]` at this checkpoint |
| mutation proof `ANCHOR MISSING` | a source edited since the proof was written | update the anchor in the WU that changed the source |
