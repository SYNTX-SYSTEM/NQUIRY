# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-07 — Google OIDC Provider Adapter (provider port, test provider, start / callback contacts)

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-07 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-07; §7 FBR-AUTH-001, -012, -016; §11.1–11.2, §11.12–11.13, §11.16–11.21; §12.3; §16.2; §19.9–19.12; §21.3–21.4; §23.4–23.6, §23.9–23.10; §24.2–24.3, §24.6; §25.2–25.3; §26; §27.1–27.2; §32.2–32.3; §47 items 10–13 |
| PREDECESSOR | WU-AUTH-06 `69b806a` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. §36 #1 and #6 (official login methods; Google production-enabled) **not decided**: Google is instantiable from complete configuration and is not configured anywhere; the test provider is refused outside DEVELOPMENT / TEST. §36 #3–#5 (account creation) **not decided**: every verified provider credential fails closed at the identity step. |

## FIRST_BROKEN_RELATION_BEFORE

External identity proof → canonical identity: no provider port, no
start/callback contact, no token exchange, no ID Token validation, no
provider error/cancel path, no test provider (FBR-AUTH-001); the nonce
validation order was unmaterialized (FBR-AUTH-012); the non-success callback
path did not exist (FBR-AUTH-016).

## ROOT_SWEEP

- Producers reused: the transaction gate (WU-AUTH-05), the redirect rule
  (WU-AUTH-06), the cookie mechanics of the local login, the runtime
  configuration discipline of `application.analysis_runtime` (HD-19 precedent).
- Consumers waiting: provider identity binding (WU-AUTH-08), account
  creation (WU-AUTH-09), linking (WU-AUTH-10), protocol callback semantics
  (WU-AUTH-15), the frontend provider surface (this unit, minimal).
- Authority chain: not touched. No session is created by this unit.

## CURRENT_RELATION

LOGIN START → transaction (PENDING, binding cookie set) → provider
authorization URL (code, S256, state, nonce) → CALLBACK → 24 §16.2 steps
1–10 in one committed transaction → token exchange with the original
verifier → ID Token validation (signature, audience, expiry by the library;
issuer by the adapter) → nonce against the transaction → trusted subject →
local effect gate → **fails closed** (no provider identity relation, no
account creation policy) → FAILED_TERMINAL → `/login?auth=unavailable`.
Provider error / cancel → CANCELLED_TERMINAL without exchange.

## INVARIANTS

1. A provider exists only from complete configuration; the provider list and
   the start contact answer `unavailable` otherwise. The test provider is
   refused outside DEVELOPMENT / TEST at startup and at runtime construction.
2. The start creates the transaction and the browser binding before the
   redirect; the redirect carries `response_type=code`, S256 challenge, state
   and nonce, never the verifier; the redirect target is validated (WU-AUTH-06).
3. The callback is a GET protocol contact whose every effect is behind the
   transaction pipeline; the claim is committed before the exchange.
4. Exchange and validation order is fixed: exchange → signature / audience /
   expiry → issuer → nonce → subject. The nonce claim of an unvalidated token
   is never read as a fact.
5. A rejected exchange, an uncertain exchange and every validation failure
   are FAILED_TERMINAL with 24 §32.2's reason; nothing is retried; a replay
   never reaches the token endpoint.
6. Provider error / cancel: validated like a callback, then
   CANCELLED_TERMINAL; no exchange, no identity, no session.
7. The browser sees only a projection class (`cancelled`,
   `provider_unavailable`, `provider_error`, `failed`, `unavailable`); never
   a code, token, verifier or state.
8. The pre-auth binding cookie is `HttpOnly`, `SameSite=Lax`, scoped to
   `/auth`, lives as long as the transaction, is cleared by the callback, and
   is not a session.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

| Relation | Home |
|---|---|
| Provider port and verified credential | `security.oidc_provider` |
| Standards-based adapter; Google metadata | `security.oidc_standard.StandardOidcProvider`, `google_provider` |
| Local test issuer (real RS256 tokens, JWKS, token endpoint over an in-process transport) | `security.oidc_test_issuer.LocalTestIssuer` |
| Provider runtime from configuration | `application.auth_runtime` |
| Start / callback pipeline, projections | `application.http_oidc` |
| Identity step (fails closed until WU-AUTH-08/-09) | `application.oidc_identity.resolve_provider_identity` |
| HTTP contacts | `apps/api/src/nquiry_api/http/oidc.py` |
| Frontend: provider buttons, projection messages | `apps/web/app/login/page.tsx`, `apps/web/lib/api/authClient.ts` |

## DELTA_MATERIALIZED / FILES_CHANGED

New: the seven modules above; `tests/e2e/test_auth_wu07_oidc_provider.py`
(32 cases); `apps/web/tests/lib/authProviders.test.ts` (9);
`apps/web/tests/e2e/oidc-login.spec.ts` (4). Changed: `nquiry_api/main.py`
(router; runtime validated at startup), `pyproject.toml` (dependencies
`PyJWT[crypto]>=2.3`, `httpx>=0.27`), `apps/web/playwright.auth.config.ts`
(spec match), `tests/e2e/test_pfc_f09_2_isolation_sweep.py` (the five new
unauthenticated protocol routes entered in `_UNAUTHENTICATED`, as that file
requires of any added route). No migration.

## API

| Contact | Result |
|---|---|
| `GET /auth/providers` | 200 `{"kind":"ok","providers":[{providerId,label,proofClass}]}` |
| `GET /auth/oidc/{provider}/start?next=` | 303 to the provider + binding cookie; 503 `unavailable PROVIDER_NOT_CONFIGURED` |
| `GET /auth/oidc/{provider}/callback` | 303 to the bound target (on identity success, later units) or `/login?auth=<projection>`; binding cookie cleared |
| `GET` / `POST /auth/test-provider/authorize` | DEVELOPMENT / TEST only: the test provider's consent page and decision; 404 otherwise |

## Configuration (24 §25.2)

`NQUIRY_AUTH_PROVIDER_MODE` (comma list: `google`, `test`),
`NQUIRY_GOOGLE_CLIENT_ID`, `NQUIRY_GOOGLE_CLIENT_SECRET`,
`NQUIRY_GOOGLE_REDIRECT_URI`, `NQUIRY_PUBLIC_API_BASE_URL` (test provider
only), `NQUIRY_ENVIRONMENT`, `NQUIRY_COOKIE_SECURE`. None is set in any
compose file or deployment by this unit.

## Case 2 choices (recorded)

- **Library.** PyJWT with its cryptography extra owns signature, audience
  and expiry validation; the adapter checks the issuer against the
  provider's accepted set (Google publishes two forms) and then the nonce.
  httpx performs the exchange and reads the JWKS. Both are declared runtime
  dependencies; neither is an AI-provider SDK.
- **Google metadata is static** (24 §26.2 permits "discovery/static
  metadata"); the endpoints are Google's published, stable ones.
- **Client authentication** is `client_secret_post`.
- **One adapter class** for Google and the test provider, so the test lane
  exercises the production adapter's mechanics against a real signer.
- **Uncertainty class.** Any transport failure or malformed token response
  is `TOKEN_EXCHANGE_OUTCOME_UNCERTAIN`; an answered refusal is
  `TOKEN_EXCHANGE_REJECTED`. Neither is retried (24 §11.9 default).
- **Malformed callback** (neither code nor error) changes no transaction
  state: nothing about it is validated enough to terminalize.
- **Provider tokens** other than the ID Token are not read or stored (24 §11.20).
- **Consent page** of the test provider is server-rendered HTML in the API
  (DEVELOPMENT / TEST only), so a real browser can walk the whole flow
  without a network provider.

## RED_RESULT

Collection error (`application.http_oidc` absent), 0 of 29 could run;
vitest 9 provider-client cases written with their implementation (deviation
classified: same step). The three consent-round-trip cases were added after
the first 29 were green (deviation classified).

## GREEN_RESULT

32 backend cases; 148 vitest (13 files); 18 mocked-browser cases on the
PURPLE lane; affected suites (`tests/security`, `tests/semantic`,
`tests/regression`, `test_http_auth`, `test_auth_wu04_session_evolution`):
439 passed, 1 skipped. `tsc` and ESLint clean.

## ADVERSARIAL_RESULT

Proven by the falsifiers: callback without a transaction; replayed callback
(no second exchange); callback delivered by another browser (rejected before
the exchange, transaction terminal); provider cancel and two provider error
classes (terminal, no exchange); malformed callback; each ID Token defect
class (signature, issuer, audience, expiry, missing subject, nonce) rejected
after the exchange with its own reason; a token wrong in both signature and
nonce failing on the signature; rejected exchange; uncertain exchange
(terminal, single attempt, replay refused); ID Token and verifier absent
from everything the browser receives; the verifier gone from the row before
the exchange is attempted; the consent page refusing a foreign redirect URI;
the test provider refused for PRODUCTION, STAGING, unknown and unset
environments; Google not instantiated from partial configuration.

## MUTATION_RESULT

No source-mutation script for this unit (disclosed, as for WU-AUTH-05/-06).
Each protection has a direct falsifier above; the validation-order falsifier
is the guard-necessity test for the nonce-after-validation rule.

## SECURITY_RESULT

No implicit flow; no provider token in the browser; the verifier never
leaves the server; the binding cookie is not a session; the client secret
appears only in the server-side token request; projections carry no
protocol material; production configuration cannot instantiate the test
provider. Google client credentials do not exist in this repository.

## CONSUMER_PROOF / PRESERVATION_RESULT

Local password login, sessions and every governed route: unchanged, suites
green. MOCKED BROWSER PROOF for the login page's provider buttons and
projection messages; REAL-STACK BROWSER PROOF still blocked on the
configurable allowed origin (WU-AUTH-14). REAL GOOGLE PROOF (24 §41):
**BLOCKED_EXTERNAL** — requires a Google OAuth client (id, secret,
registered redirect URI), which is an external secret PURPLE must not
create or guess. Every step of §41 that does not need Google is proven
against the test issuer.

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu07_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `f960c188daa32c4f62af34f99347879c53bc0c88a871aaac67e4b57a44194d79` |
| Live result | 2187 passed, 2 skipped, 0 failed, exit 0 (0:31:00) = 2155 + 32 |
| No-database result | 976 passed, 1213 skipped, 0 failed, exit 0 |
| Migrations | single head `c4e6a8b1d3f5` (unchanged); live check PASS |
| Post-run tree hash | identical; git status identical |
| Frontend | vitest 148; tsc, eslint clean; 18 mocked specs on `:13460` |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| authorization URL | server-generated state, nonce, challenge + provider metadata | PROTOCOL FACT |
| binding cookie | server random, hash bound to the transaction | PROTOCOL FACT |
| `code`, `state`, `error` on the callback | provider redirect via the browser | PROVIDER / USER CLAIM; validated, never trusted as such |
| ID Token | token endpoint, over the server's own request | PROVIDER CLAIM until validated |
| `VerifiedProviderCredential` | validation succeeded, nonce matched | AUTHENTICATION PROOF |
| a canonical identity | **none** | the identity step fails closed (UNPROVEN until WU-AUTH-08/-09) |
| projection in the URL | fixed server vocabulary | DERIVED FACT |

No provider claim becomes canonical truth in this unit.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: a login start is a transaction plus a browser
binding plus a provider request; a callback is a validated continuation
whose provider proof is a signed, audience- and issuer-bound, unexpired token
whose nonce matches the transaction; the proof ends at a verified external
credential that the identity Field has not yet been authorized to map. That
is 24 §11.1–11.2, §11.12–11.13, §11.16. No second callback path, no
frontend-held protocol state, no identity by side effect.

## FIRST_BROKEN_RELATION_AFTER

**Provider identity binding** (24 WU-AUTH-08; §11.13–11.14, §13.3): no
relation maps `provider_issuer + provider_subject` to a canonical `UserId`,
so an existing binding cannot be resolved and every provider login fails
closed. WU-AUTH-08 must add the relation; the account creation branch for an
unknown subject remains a §36 decision (WU-AUTH-09).

## Limitations and ceilings

- Real Google proof BLOCKED_EXTERNAL (credentials); Google enablement is a §36 decision.
- Real-stack browser lane blocked (allowed origin, WU-AUTH-14).
- No audit / SecurityEvent for provider login events yet (24 §31.1);
  owner: the security hardening step of §47 (item 24), tracked in STATUS.md.
- No source-mutation proof.
- Human decisions field-local; 16 §41 reconciliation deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-07 proven against the test issuer; real provider proof blocked externally. Next: WU-AUTH-08.
