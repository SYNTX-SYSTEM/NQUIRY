# TEST GUIDE — AUTH/CYAN-01 · LIVE PURPLE PROVIDER OUTPUT → CYAN typed auth/provider contract

**Field:** PURPLE_AUTH ↔ CYAN_FRONTEND (producer Architecture 24 on `auth-identity`; consumer line `frontend-symbiotic`)
**Status of the Work Unit:** TECHNICALLY_CLOSED · LOCAL_GREEN (WU scope) · CHECKPOINTED (`checkpoint-AUTH-CYAN-01`).
Not FIELD_GREEN. Not REVIEWED_FIELD. Not PUBLISHED_FIELD. No Human Frontend Review is required for this unit: nothing is
presented. Authorization: `HA-AUTH-CYAN.md` (HA-AUTH-CYAN-01, 2026-10-03).
**This document:** a self-contained test manual (documentation only; it changes nothing).

## 1. Purpose and scope

AUTH/CYAN-01 materializes exactly one relation: the live PURPLE AUTH HTTP output becomes a typed, fail-closed contract
inside CYAN's auth client. No component, route, rail or login page consumes it yet.

```text
LIVE PURPLE AUTH (apps/api …/http/{oidc,auth,revocation}.py → application.http_oidc / http_dispatch / http_revocation)
→ JSON bodies, 303 redirects, ?auth= / ?link= projections
→ apps/web/lib/api/authClient.ts (section "AUTH/CYAN-01")        ← the only product delta
→ typed results: ok | denied | rejected | unknown  — or MalformedAuthResponse / UnsafeNextTarget
→ (no consumer yet: NOT PRESENTED, NOT GUI-INTEGRATED)
```

Laws this guide tests, verbatim from the authorization:

```text
AUTHENTICATION != AUTHORIZATION          AUTHENTICATED_PRINCIPAL != ROLE          ROLE != AUTHORITY
LOGIN != LINK                            LINK != ACCOUNT_CREATION
GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN  API_LIVE != GUI_MATERIALIZED
PROVIDER_OUTPUT != CYAN_INFERENCE        UNKNOWN != OK                            DENIED != OK
Provider availability must come ONLY from the parsed provider response. No hard-coded Google availability.
Unknown response kind / fields / enum values / proofClass / auth projection / link projection must fail closed.
Refuse unsafe or absolute/non-local next targets.
```

Out of scope, by authorization: a real Google callback, a production login, a live deployment, any PURPLE change.
None of the procedures below logs in anywhere. The only live contact is one unauthenticated read-only `GET`.

## 2. Checkpoint identities (verified from Git)

| Object | Identity |
|---|---|
| Base | `frontend-symbiotic` @ `28c485eab0dfef3e5b93938d774cb51ae3144e19` (docs commit over `checkpoint-CY-PCPG-05` `2d6163b`) |
| Field commit | `5877c138439582504ec746a3f8669a1ba771ac22` (tree `48bafbeeb765284d10d924e73b045af24d5e8a63`) |
| Tag | `checkpoint-AUTH-CYAN-01` → tag object `873f2f7f39af9088c6438b7d135d17593ef09ce9` → `5877c13` |
| Docs commit (checkpoint identity recorded) | `934b502ee8b6bb703e74b4624090e09fded270d9` |
| PURPLE producer pinned for CYAN AUTH consumption | `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (proven product commit `b47bc78942b2d2bf3759ffb48b6d51deb5faea1e`, docs-only after it) |
| Live assembly serving that producer | `/opt/nquiry/assembly/auth-aa32c4d-20261001T081014Z` on nquiry.condyn.eu (API only; the web service stays CYAN `field-CY-01` `54f8b4f`) |

Verify (from the worktree root):

```bash
git rev-parse 28c485e checkpoint-AUTH-CYAN-01 checkpoint-AUTH-CYAN-01^{commit} 5877c13^{tree}
git log --oneline 28c485e..origin/frontend-symbiotic        # expect exactly: 934b502 record(...), 5877c13 field(AUTH/CYAN-01)
git show --stat 5877c13 | tail -8                            # expect the 5 files of §13
```

## 3. Prerequisites

- Node toolchain of `apps/web` installed (`npm ci` already done in the worktree); Playwright browsers installed.
- Working tree at or after `934b502` (any later CYAN commit that does not touch `authClient.ts` is fine; if it does,
  the WU for that commit owns the guide).
- Network access to `https://nquiry.condyn.eu` only for the optional read-only probe of §6. No credentials of any kind
  are needed anywhere in this guide. Do not use production accounts.
- Port `3301` free (the mocked Playwright lane starts its own Next server there). Port `3000` is typically occupied by
  the local docker container `nquiry-web-1`; that server must NOT be used (§9, §17).

## 4. The contract under test

Copied from the PURPLE serializers at `aa32c4d` (`packages/application/http_oidc.py`, `http_dispatch.py`,
`http_revocation.py`, `packages/security/redirect_target.py`, `packages/security/auth_methods.py`). These two files are
byte-identical on the live host (sha256 `95d6d48a…` and `adb6c182…`; §6 shows how to re-check).

| Contact | Shapes CYAN accepts (exact keys, closed values); everything else fails closed |
|---|---|
| `GET /auth/providers` | `{"kind":"ok","providers":[{"providerId","label","proofClass"}]}` · `proofClass ∈ {PRODUCTION_PROVIDER, TEST_PROVIDER}` · one shape only (a `denied` here is malformed) |
| `GET /auth/methods` | `ok {methods:[{methodId(uuid), methodType, status, createdAt, lastAuthenticatedAt\|null, provider:{providerId,email\|null}\|null}]}` · `denied NO_SESSION` · `methodType ∈ {LOCAL_PASSWORD, GOOGLE_OIDC, TEST_PROVIDER}` · `status ∈ {ACTIVE, REVOKED}` |
| `GET /auth/sessions` | `ok {sessions:[{sessionId(uuid), issuedAt, expiresAt, current, methodType\|null}]}` (at most one `current`) · `denied NO_SESSION` |
| `POST /auth/sessions/{id}/revoke` | `ok {}` · `denied NO_SESSION \| SESSION_NOT_FOUND` · `rejected MALFORMED_SESSION_ID` |
| `POST /auth/logout-all` | `ok {revokedSessions: int ≥ 0}` · `denied NO_SESSION` |
| `POST /auth/methods/{id}/unlink` | `ok {methodId(uuid), sessionsRevoked: int ≥ 0, currentSessionEnded: bool}` · `denied NO_SESSION \| UNLINK_DENIED \| LAST_METHOD` · `rejected MALFORMED_METHOD_ID` |
| `GET /auth/oidc/{p}/start?next=` (LOGIN) | built, never fetched: a top-level navigation; the API answers 303 to the provider; a non-success returns to `/login?auth=<word>` |
| `POST /auth/oidc/{p}/link/start?next=` (ACCOUNT_LINK) | built as `{method:"POST", action}` for a form submit; session required (401 `NO_SESSION`); outcome returns to `next?link=<word>` |
| `?auth=` words | `cancelled, provider_unavailable, provider_error, failed, unavailable` |
| `?link=` words | `ok, already_linked, collision, cancelled, failed` |
| `next` candidate | exactly one leading `/`, printable ASCII only, no space/control, no backslash, not `//…`, no `%00–%1F`/`%7F`, ≤ 1024 chars; anything else → `UnsafeNextTarget` |
| Forbidden keys anywhere in a body | `sessionToken, token, tokenHash, state, nonce, codeVerifier, clientSecret, password, subject, sub, idToken, accessToken, refreshToken` (+ snake_case twins) → malformed before any field is read |

Exports to know (all in `apps/web/lib/api/authClient.ts`): `parseProviderList`, `parseMethodList`, `parseSessionList`,
`parseSessionRevoke`, `parseLogoutAll`, `parseUnlink` (pure parsers); `listProviders`, `listMethods`, `listSessions`,
`revokeSession`, `logoutAll`, `unlinkMethod` (fetchers, `credentials: "include"`); `availableProvider`,
`googleLoginStart`, `loginStartUrl`, `linkStartAction`, `isLocalNextTarget`; `readAuthProjection`, `readLinkProjection`;
the vocabularies `PROOF_CLASSES`, `AUTH_METHOD_TYPES`, `AUTH_METHOD_STATUSES`, `AUTH_PROJECTIONS`, `LINK_PROJECTIONS`,
`AUTH_FORBIDDEN_KEYS`; the errors `MalformedAuthResponse`, `UnsafeNextTarget`; `AUTH_CONTRACT_PRODUCER`.

## 5. Access and authority

- The parsers carry no authority. A parsed principal, method, session or provider is never a role, a permission or an
  authority; no parsed shape has such a key, and an extra `role` key on a method is malformed (§10).
- `ProviderSummary` is branded with a module-private symbol: it exists only as output of `parseProviderList`. A
  hand-written `{providerId:"google", …}` does not type-check against `loginStartUrl` / `linkStartAction` (§10, the
  `@ts-expect-error` falsifier, checked by `tsc`).
- `googleLoginStart(list, next)` is `unavailable` whenever the parsed list has no `google` entry. There is no other
  source of availability (mutation M4, §11).

## 6. Read-only live probe (optional; no login, no mutation)

This confirms that the production fixture the unit tests use is still the live truth. It is an unauthenticated GET.

```bash
curl -s https://nquiry.condyn.eu/api/auth/providers; echo
# expected, byte for byte:
# {"kind":"ok","providers":[{"providerId":"google","label":"Google","proofClass":"PRODUCTION_PROVIDER"}]}
curl -s -o /dev/null -w '%{http_code}\n' https://nquiry.condyn.eu/api/auth/methods     # 401 (no session; CYAN parses it as denied NO_SESSION)
curl -s -o /dev/null -w '%{http_code}\n' https://nquiry.condyn.eu/api/auth/sessions    # 401
```

Do NOT request `/api/auth/oidc/google/start` with a browser that has a Google session, and do not follow the 303: that
would start a real login transaction, which this unit does not prove and which is not authorized.

Producer identity re-check (host operator only, read-only; compares the live assembly with the pinned commit):

```bash
# local, from the worktree root
for f in packages/application/http_oidc.py packages/security/redirect_target.py; do git show origin/auth-identity:$f | sha256sum; done
# on the host (read-only)
ssh root@49.13.3.21 'cd /opt/nquiry/assembly/auth-aa32c4d-20261001T081014Z && sha256sum packages/application/http_oidc.py packages/security/redirect_target.py'
# expected: 95d6d48af53aeb74181ef48702ebc8624de13b3b0ace89798e00da26f67cabf2 and adb6c18275b9ad9782b1ed6f2938705d404f6c8962493ac9d38143ac20e0a553, both sides
```

If `origin/auth-identity` has moved past `aa32c4d`, compare against `aa32c4d:<path>` instead of the branch: the pinned
producer is the commit, not the moving branch (HA-AUTH-CYAN record).

## 7. Manual contract walk-through (no browser; a Node REPL through vitest)

Create a scratch spec outside the repo's test tree, run it once, delete it. It exercises the public surface by hand.

```bash
cd apps/web
mkdir -p /tmp/auth01-walk && cat > /tmp/auth01-walk/auth01-walk.test.ts <<'TS'
import { it } from "vitest";
import * as a from "/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic/apps/web/lib/api/authClient";
it("walk", () => {
  const live = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] };
  const list = a.parseProviderList(live);
  console.log("google start:", a.googleLoginStart(list, "/workspaces"));                 // kind available + url …/auth/oidc/google/start?next=%2Fworkspaces
  console.log("empty list:", a.googleLoginStart(a.parseProviderList({ kind: "ok", providers: [] }), "/"));  // { kind: 'unavailable' }
  console.log("link action:", a.linkStartAction(list.providers[0], "/workspaces"));      // { method: 'POST', action: …/link/start?next=%2Fworkspaces }
  console.log("auth=failed:", a.readAuthProjection("?auth=failed"));                     // projection failed
  console.log("auth=ok:", a.readAuthProjection("?auth=ok"));                             // unknown  (ok is a LINK word, not a LOGIN word)
  console.log("link=ok:", a.readLinkProjection("?link=ok"));                             // projection ok
  for (const bad of [{ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PROVEN" }] }, { kind: "denied", reasonCode: "NO_SESSION" }, { kind: "ok", providers: [], googleAvailable: true }]) {
    try { a.parseProviderList(bad); console.log("ACCEPTED (BUG)"); } catch (e) { console.log("refused:", (e as Error).message); }
  }
  for (const next of ["https://evil.example/", "//evil.example", "/\\evil", "/a b", "/a%0d%0ax"]) {
    try { a.loginStartUrl(list.providers[0], next); console.log("BUILT (BUG)", next); } catch (e) { console.log("refused next:", (e as Error).name); }
  }
});
TS
npx vitest run auth01-walk.test.ts --root /tmp/auth01-walk --reporter=dot 2>&1 | grep -vE '^\s*$' | head -40
rm -r /tmp/auth01-walk
```

Note: `--root` must be the scratch directory itself; a wider root (e.g. `/`) makes vitest scan the filesystem and hang.

Expected: every "refused" line names `malformed AUTH response at …` (with the offending path, e.g.
`providers.providers[0].proofClass`) or `UnsafeNextTarget`; no line says `BUG`; the refusal for an unsafe `next` never
prints the candidate.

## 8. Automated proof procedure (from `apps/web`)

Run in this order. Steps 1–4 and 6–7 are read-only; step 5 writes and restores `authClient.ts` and must not overlap
with anything that reads the source (no concurrent vitest/tsc/eslint/Playwright).

```bash
cd apps/web
# 1. focused unit tests: fixtures, adversarial parsers, enum/kind/field falsifiers, unsafe-next falsifiers, F02 preservation
npx vitest run tests/lib/authClient.test.ts --reporter=dot             # expect 149 passed
# 2. full unit suite (gates laws, field, lib, components)
npx vitest run --reporter=dot                                           # expect 535 passed / 32 files (or more after later WUs)
# 3. TypeScript — includes tests/lib, so the @ts-expect-error falsifier is enforced
npx tsc --noEmit -p .                                                   # expect no output, exit 0
# 4. ESLint
npx eslint .                                                            # expect 0 errors (1 pre-existing warning in components/field/Identity.tsx)
# 5. mutation proof (writes and restores lib/api/authClient.ts; run alone)
node scripts/auth01-mutation-proof.mjs                                  # expect "9/9 mutations killed; baseline sha256 d7835dc3…", exit 0
sha256sum lib/api/authClient.ts                                         # expect d7835dc31c191919c08ae237f41ef45b1d7ab349d747f68552847fde3a97196c
# 6. existing mocked Playwright auth lane on the ISOLATED server (:3301, never adopts a foreign server)
npx playwright test -c playwright.sf01.config.ts tests/e2e/auth.spec.ts --project=desktop \
  --output=/tmp/pw-auth01 --reporter=line                               # expect 6 passed
# 7. clean up what `next dev` leaves behind before any commit
git -C ../.. checkout -- apps/web/next-env.d.ts; rm -f AGENTS.md CLAUDE.md; git -C ../.. status --short | grep -v '^?? docs/'
```

Why `--output=/tmp/…`: `apps/web/test-results/sf01-real-stack/` is root-owned (written by a docker lane) and the default
output directory cannot be cleared. Why the sf01 config: `playwright.config.ts` has `reuseExistingServer` and would
adopt whatever answers on `:3000` (the docker container `nquiry-web-1`, a foreign tree).

## 9. Falsifier matrix (what each test class refutes)

| # | Class (test file section) | Refutes | Count |
|---|---|---|---|
| F1 | contract identity | vocabularies drift from the serializers; producer pin missing | 2 |
| F2 | production fixture | the live shape is not parsed exactly; a parsed provider carries extra or authority keys | 6 |
| F3 | providers falsifiers | unknown/mis-cased/missing `proofClass`, extra field (envelope and item), `denied` or unknown kind, non-array, non-object, empty id, non-string label, duplicate id, forbidden keys, array/null/string bodies, non-JSON body, hand-built provider (type-level) | 20 |
| F4 | next target | 6 safe targets accepted; 21 unsafe candidates refused by `isLocalNextTarget`, `loginStartUrl`, `linkStartAction`, `googleLoginStart`; refusal never echoes the candidate | 28 |
| F5 | LOGIN vs LINK builders | wrong route, wrong method, unencoded `next`, unencoded provider id | 3 |
| F6 | projections | none / each known word (5 + 5) / unknown words incl. cross-vocabulary words, case, whitespace, `<script>`, empty, NUL / repeated parameter | 27 |
| F7 | methods | serializer shape, provider without email, `denied NO_SESSION`, fetch mechanics; 16 falsifiers (unknown `methodType`/`status`, extra key incl. `role`, missing/extra provider keys, non-ISO instant, non-UUID id, wrong types, unknown reason, missing reason, extra key on denied, `rejected`, unknown kind, non-array, forbidden nested key) | 20 |
| F8 | sessions / revoke / logout-all | two `current`, unknown `methodType`, wrong types, missing key, extra key, `tokenHash`, cross-contact reason codes, unknown kinds, negative/fractional/string counts; fetch method/path/credentials incl. path encoding | 25 |
| F9 | unlink | all reason codes exactly; wrong types, missing/extra keys, non-UUID, unknown reason, `unavailable` kind, forbidden `sub`; fetch mechanics | 10 |
| F10 | forbidden-key law named | refusal reason says "forbidden key" (not merely "unexpected key") at envelope and nested levels | 1 |
| F11 | F02 preservation | the original `login`/`fetchCurrentSession`/`logout` tests, verbatim, plus one regression | 8+ |

Total 149 tests in `tests/lib/authClient.test.ts`.

## 10. Mutation proof (`apps/web/scripts/auth01-mutation-proof.mjs`)

Nine narrow mutations of `lib/api/authClient.ts`, each applied alone, the focused tests run, the file restored and its
sha256 compared with the baseline:

| Mutation | What it would silently allow | Killed by |
|---|---|---|
| M1 proofClass widened to any string | an unknown proof class presented as a provider | F3 |
| M2 unknown provider-list kind accepted | `{"kind":"providers"}` parsed as a list | F3 |
| M3 unsafe next forwarded (type check only) | absolute / scheme-relative / CRLF `next` sent to the API | F4 (17 tests) |
| M4 hard-coded Google availability | a Google start URL without a parsed provider | F2 |
| M5 unknown projection → `failed` | a CYAN inference in place of the producer's word | F6 (15 tests) |
| M6 unknown fields tolerated | extra keys entering auth truth | F3/F7/F8/F9 |
| M7 denied methods → empty `ok` | DENIED presented as OK | F7 |
| M8 forbidden keys tolerated | a token/subject key reaching the browser as "merely unexpected" | F10 |
| M9 unknown reason code accepted | an unknown denial class treated as a known one | F7/F8/F9 |

Expected output ends with `9/9 mutations killed; baseline sha256 d7835dc3…` and exit code 0. A `SURVIVED` line or a
`restored byte-identical: false` line is a failed proof; in the latter case restore with `git checkout -- lib/api/authClient.ts`.

## 11. Interpreting a run

- All of §8 green → the unit's claim holds: PURPLE AUTH truth is CONSUMABLE BY CYAN. Nothing more.
- Step 1 or 5 red after a PURPLE change → the producer moved; do not widen the parsers. Reconstruct the new producer,
  obtain a new authorization, re-pin (HA-AUTH-CYAN record).
- Step 6 red with `EACCES … test-results` → missing `--output`; with unexpected pages or 200s from `/auth/me` → a
  foreign server was adopted (wrong config), see §13.
- §6 probe body differs from the fixture → the live producer changed; the fixture test must keep failing until a human
  re-pins (the test is the alarm, not a nuisance).

## 12. CLAIM CEILING

```text
PURPLE AUTH truth = CONSUMABLE BY CYAN
Still: NOT PRESENTED · NOT GUI-INTEGRATED · NOT REAL-GOOGLE-CALLBACK-PROVEN
GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN
PURPLE's own ceiling unchanged: HA-AUTH-01 DENIED · HA-AUTH-02 DENIED · HA-AUTH-03 NEVER
GOOGLE_OIDC_ALLOWED != GOOGLE_OIDC_REAL_PROOF_COMPLETE
Live production: NQUIRY_ACCOUNT_CREATION_POLICY=DENIED (producer fact, not a CYAN inference)
```

## 13. Files changed by the checkpoint (`git show --stat 5877c13`)

| File | Role |
|---|---|
| `apps/web/lib/api/authClient.ts` | product delta (F02 section untouched; new section "AUTH/CYAN-01") |
| `apps/web/tests/lib/authClient.test.ts` | 149 tests (F02 tests verbatim + AUTH/CYAN-01) |
| `apps/web/scripts/auth01-mutation-proof.mjs` | mutation proof |
| `docs/implementation/field-reports/AUTH-CYAN/WU-AUTH-CYAN-01.md` | work-unit report (+ checkpoint identity in `934b502`) |
| `docs/implementation/field-reports/AUTH-CYAN/HA-AUTH-CYAN.md` | authorization, verbatim |

Not changed: any component, route, rail, the login page, `globals.css`, PURPLE, RED, the lanes' producer pins, production.

## 14. Next First Broken Relation (not authorized)

AUTH/CYAN-02: CYAN typed contract → presented provider contact on the CYAN login field (a Google control only when
`googleLoginStart` is `available`; `?auth=` read as a safe projection, `unknown` shown as nothing). It is the first
login-page change and therefore needs the Human Visual Authority for the frontend and its own review runtime.

## 15. Troubleshooting

| Symptom | Cause | Remedy |
|---|---|---|
| `EACCES … test-results/sf01-real-stack/.last-run.json` | root-owned lane output | add `--output=/tmp/pw-auth01` |
| Playwright adopts `:3000` | default config `reuseExistingServer` + docker `nquiry-web-1` | use `-c playwright.sf01.config.ts` (`:3301`, never adopts) |
| `apps/web/AGENTS.md`, `CLAUDE.md`, modified `next-env.d.ts` after Playwright | `next dev` artifacts | §8 step 7 |
| mutation proof reports `ANCHOR MISSING` | `authClient.ts` edited since the proof was written | update the anchor in the script in the WU that changed the source |
| failure count `1` for every mutation | regex matched "Test Files 1 failed" | the script uses `/Tests\s+(\d+) failed/`; keep it |
| `tsc` error "Unused '@ts-expect-error'" | the `ProviderSummary` brand was removed or exported | the brand is a law (availability only from the parsed response); restore it |
| §6 probe returns a different body | live producer changed | do not edit the fixture; reconstruct and re-pin under new authority |
