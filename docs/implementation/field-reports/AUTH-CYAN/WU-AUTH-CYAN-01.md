# WORK UNIT REPORT
FIELD: PURPLE_AUTH ↔ CYAN_FRONTEND (cross-field consumption; Architecture 24 producer, Architecture 27 v4 consumer line)
WORK_UNIT: AUTH/CYAN-01 — LIVE PURPLE PROVIDER OUTPUT → CYAN typed auth/provider contract
DATE: 2026-10-03 · BASE: `frontend-symbiotic` @ `28c485eab0dfef3e5b93938d774cb51ae3144e19` (docs commit over `checkpoint-CY-PCPG-05` `2d6163b`)
AUTHORITY: `HA-AUTH-CYAN.md` (HA-AUTH-CYAN-01, 2026-10-03) — implementation of the already reconstructed AUTH/CYAN-01 only.

## Exact first broken relation
LIVE PURPLE PROVIDER OUTPUT → CYAN typed auth/provider contract. Before this unit CYAN's `authClient.ts` knew only the
F02 contacts (`POST /auth/login`, `POST /auth/logout`, `GET /auth/me`); the live PURPLE contacts (providers, methods,
sessions, revoke, logout-all, unlink, OIDC login start, OIDC link start, the `?auth=` / `?link=` projections) had no
typed consumer. Only this relation is materialized. Nothing is presented.

## Producer (reconstructed read-only; PURPLE source untouched)
| | Value |
|---|---|
| PURPLE branch / commit | `auth-identity` @ `aa32c4d4faad23eea0bd3290641e7a66adcf26a9` (2026-10-01, "final global preservation proof on b47bc78 recorded"); proven product commit `b47bc78942b2d2bf3759ffb48b6d51deb5faea1e`, docs-only after it |
| Live assembly (nquiry.condyn.eu) | `/opt/nquiry/assembly/auth-aa32c4d-20261001T081014Z` (HA-AUTH-06 option (a), HA-AUTH-06a: API from AUTH lineage, WEB stays CYAN `field-CY-01` `54f8b4f`); runtime `NQUIRY_ENVIRONMENT=PRODUCTION`, `NQUIRY_AUTH_PROVIDER_MODE=google`, `NQUIRY_ACCOUNT_CREATION_POLICY=DENIED`, test provider not enabled |
| Contract files (blob at `aa32c4d`) | `packages/application/http_oidc.py` `8195221a` (sha256 `95d6d48a…` — identical on the live host), `packages/application/http_dispatch.py` `d0b4ada8`, `packages/application/http_revocation.py` `21a15d5f`, `packages/security/redirect_target.py` `3c095185` (sha256 `adb6c182…` — identical on the live host), `packages/security/auth_methods.py` `ac497cfa`, `apps/api/src/nquiry_api/http/{oidc,auth,revocation}.py` |
| Live probes (read-only, 2026-10-03) | `GET /api/auth/providers` → 200 `{"kind":"ok","providers":[{"providerId":"google","label":"Google","proofClass":"PRODUCTION_PROVIDER"}]}`; `/api/auth/methods` 401; `/api/auth/sessions` 401; `/api/auth/oidc/google/start` 303 |

### Wire contract consumed (copied from the serializers, not inferred)
| Contact | Body kinds · exact keys · closed values |
|---|---|
| `GET /auth/providers` | `ok {providers:[{providerId,label,proofClass}]}`; `proofClass ∈ {PRODUCTION_PROVIDER, TEST_PROVIDER}`; one shape only |
| `GET /auth/methods` | `ok {methods:[{methodId(uuid),methodType,status,createdAt,lastAuthenticatedAt|null,provider:{providerId,email|null}|null}]}` · `denied NO_SESSION`; `methodType ∈ {LOCAL_PASSWORD,GOOGLE_OIDC,TEST_PROVIDER}`, `status ∈ {ACTIVE,REVOKED}` |
| `GET /auth/sessions` | `ok {sessions:[{sessionId(uuid),issuedAt,expiresAt,current,methodType|null}]}` · `denied NO_SESSION` |
| `POST /auth/sessions/{id}/revoke` | `ok {}` · `denied NO_SESSION|SESSION_NOT_FOUND` · `rejected MALFORMED_SESSION_ID` |
| `POST /auth/logout-all` | `ok {revokedSessions:int≥0}` · `denied NO_SESSION` |
| `POST /auth/methods/{id}/unlink` | `ok {methodId(uuid),sessionsRevoked:int≥0,currentSessionEnded:bool}` · `denied NO_SESSION|UNLINK_DENIED|LAST_METHOD` · `rejected MALFORMED_METHOD_ID` |
| `GET /auth/oidc/{p}/start?next=` (LOGIN) | 303 to the provider (navigation); unknown provider → 503 `unavailable PROVIDER_NOT_CONFIGURED`; non-success ends at `/login?auth=<projection>` |
| `POST /auth/oidc/{p}/link/start?next=` (ACCOUNT_LINK) | session required (401 `denied NO_SESSION`); 303 to the provider; outcome ends at `next?link=<projection>` (server default `/account/security`) |
| `?auth=` vocabulary | `cancelled, provider_unavailable, provider_error, failed, unavailable` |
| `?link=` vocabulary | `ok, already_linked, collision, cancelled, failed` |
| `next` rule (`redirect_target.py`) | exactly one leading `/`, printable ASCII, no whitespace/control, no backslash, no `//`, no `%00–%1F`/`%7F`, ≤ 1024 |

## Delta (CYAN)
| File | Change |
|---|---|
| `apps/web/lib/api/authClient.ts` | **extended** (F02 section byte-for-byte untouched). New section AUTH/CYAN-01: `AUTH_CONTRACT_PRODUCER`; closed vocabularies `PROOF_CLASSES`, `AUTH_METHOD_TYPES`, `AUTH_METHOD_STATUSES`, `AUTH_PROJECTIONS`, `LINK_PROJECTIONS`, per-contact reason-code sets; `AUTH_FORBIDDEN_KEYS` (token/secret/subject keys fail closed before any field is read); `MalformedAuthResponse` (a `TypeError`), `UnsafeNextTarget`; exact-key parsers `parseProviderList`, `parseMethodList`, `parseSessionList`, `parseSessionRevoke`, `parseLogoutAll`, `parseUnlink`; fetchers `listProviders`, `listMethods`, `listSessions`, `revokeSession`, `logoutAll`, `unlinkMethod` (credentials included, non-JSON body fails closed); `availableProvider`; `isLocalNextTarget` (PURPLE's rule mirrored exactly); `loginStartUrl(provider, next)`, `googleLoginStart(list, next)`, `linkStartAction(provider, next)` → `{method:"POST", action}`; `readAuthProjection`, `readLinkProjection` → `none | projection | unknown`. `ProviderSummary` carries a module-private symbol brand: only `parseProviderList` can produce one, so no builder accepts a bare provider id. |
| `apps/web/tests/lib/authClient.test.ts` | **extended** (F02 tests kept verbatim): production fixture, Google-availability-only-from-parsed-list, 17 provider falsifiers, 21 unsafe-`next` falsifiers + 6 safe targets, LOGIN≠LINK builders, projection vocabularies (unknown stays unknown; repeated parameter unknown), methods/sessions/revoke/logout-all/unlink fixtures and falsifiers, forbidden-key law named explicitly, fetch mechanics, a type-level `@ts-expect-error` falsifier for a hand-built provider, F02 preservation |
| `apps/web/scripts/auth01-mutation-proof.mjs` (new) | 9 narrow mutations of `authClient.ts`, byte-identical restore (sha256 `d7835dc3…`) |
| `docs/implementation/field-reports/AUTH-CYAN/` (new) | this record, `HA-AUTH-CYAN.md` |
Not touched: every component, route, rail, the login page, `globals.css`, PURPLE, RED, the production host, the local lanes' pins.

## Laws and where they hold
| Law | Materialization |
|---|---|
| AUTHENTICATION != AUTHORIZATION · AUTHENTICATED_PRINCIPAL != ROLE · ROLE != AUTHORITY | no parsed shape has a role/authority/permission key; an extra `role` key on a method fails closed (test "extra key on a method") |
| LOGIN != LINK | distinct routes (`/start` vs `/link/start`), distinct HTTP shapes (GET navigation vs POST form action), distinct vocabularies (`auth=ok` is unknown; `link=provider_error` is unknown) |
| LINK != ACCOUNT_CREATION | `link=ok` is read as a projection word only; the module creates nothing and names no account creation; live policy `DENIED` is a producer fact, not a CYAN inference |
| GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN | `googleLoginStart` returns a URL, never a proof; no callback is exercised in this unit |
| API_LIVE != GUI_MATERIALIZED | no component imports the new exports; nothing is rendered |
| PROVIDER_OUTPUT != CYAN_INFERENCE | vocabularies copied from the serializers; unknown projection → `unknown` (PURPLE's own web client maps unknown → `failed`; CYAN does not infer) |
| UNKNOWN != OK · DENIED != OK | every unknown kind/key/enum/proofClass/reason/projection throws `MalformedAuthResponse` or reads `unknown`; `denied` and `rejected` are returned as themselves |
| Provider availability only from the parsed response | brand on `ProviderSummary`; `googleLoginStart` on an empty or test-only list → `unavailable`; mutation M4 killed |
| Unsafe `next` refused | `UnsafeNextTarget` on absolute, scheme-relative, backslash, whitespace/CRLF, encoded control, non-ASCII, over-long or non-string candidates; the refusal never echoes the candidate; CYAN refuses where PURPLE would fall back to `/` |

## Proof
| Lane | Result |
|---|---|
| Focused unit tests `tests/lib/authClient.test.ts` (F02 preservation + AUTH/CYAN-01 fixtures, adversarial parsers, unknown enum/kind/field falsifiers, unsafe-next falsifiers) | **149 / 149** |
| Mutation proof `scripts/auth01-mutation-proof.mjs` | **9 / 9 killed**, byte-identical restore: M1 proofClass widened · M2 unknown provider-list kind accepted · M3 unsafe next forwarded · M4 hard-coded Google availability · M5 unknown projection → failed · M6 unknown fields tolerated · M7 denied methods → empty ok · M8 forbidden keys tolerated · M9 unknown reason code accepted |
| Full unit suite (`tests/field`, `tests/lib`, `tests/components`; gates laws included) | **535 / 535** (32 files) |
| Existing mocked Playwright auth lane `tests/e2e/auth.spec.ts` | **6 / 6** on the isolated `:3301` server (`playwright.sf01.config.ts`, `reuseExistingServer: false`; the default config would have adopted the foreign `nquiry-web-1` container on `:3000`) |
| `tsc --noEmit` (includes `tests/lib`, so the `@ts-expect-error` falsifier is checked) | clean |
| `eslint .` | 0 errors (1 pre-existing warning in `components/field/Identity.tsx`, untouched) |
| Not run, by authorization | real-stack callback, production login, live deployment |

## Status
FBR AUTH/CYAN-01: CLOSED (TECHNICALLY). LOCAL_GREEN for the WU scope. Not FIELD_GREEN, not REVIEWED_FIELD, not
PUBLISHED_FIELD, not merged, not deployed. PURPLE's own ceiling is unchanged by this consumption (HA-AUTH-01 DENIED,
HA-AUTH-02 DENIED, HA-AUTH-03 NEVER; GOOGLE_OIDC_ALLOWED != GOOGLE_OIDC_REAL_PROOF_COMPLETE).

**Claim ceiling:** PURPLE AUTH truth = CONSUMABLE BY CYAN. Still: NOT PRESENTED · NOT GUI-INTEGRATED ·
NOT REAL-GOOGLE-CALLBACK-PROVEN. GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN.

**Next FBR (not authorized):** CYAN typed auth/provider contract → presented provider contact on the CYAN login
field (a Google control only when `googleLoginStart` is `available`, the `?auth=` reading as a safe projection) —
AUTH/CYAN-02, which would be the first login-page change and therefore needs Human Visual Authority.

**Checkpoint:** see the final section of this file after commit.
