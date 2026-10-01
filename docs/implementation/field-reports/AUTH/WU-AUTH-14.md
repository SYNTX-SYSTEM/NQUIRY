# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-14 — Anti-CSRF Boundary

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-14 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-14; §21.3–21.9; §11.16; §24.6; §38 falsifiers 62–66; §44.7; 20 §12 (real-stack lane) |
| PREDECESSOR | WU-AUTH-13 `171a6e7` |
| PROOF_RADIUS (HD-AUTH-04) | **Escalated.** The boundary wraps every unsafe HTTP request of the repository (a repo-wide protocol change, one of HD-AUTH-04's named escalators): security, semantic, regression and the whole `tests/e2e` HTTP surface (1388 / 2), plus frontend gates, the mocked lane and — new — the **AUTH real-stack lane** (real Chromium, real app, real API, real PostgreSQL, a hostile third origin). Not a full repository regression (unit / domain / authority suites not re-run; next checkpoint). |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01..04 OPEN, unchanged. No new boundary: 24 §21.6–21.7 leave the mechanism to implementation ("may autonomously choose a coherent mechanism"). |

## FIRST_BROKEN_RELATION_BEFORE

Unsafe cookie-authenticated requests reached the application with no
explicit anti-CSRF boundary; the local password login had no login-CSRF
boundary; CORS was origin-pinned but hard-coded and, with `SameSite=Lax`,
was the only thing standing between a hostile page and the API (24 §21.7:
neither may be the boundary). The browser-facing proof of the request
contract was blocked because the allowed origin was not configurable.

## CURRENT_RELATION

**Application anti-CSRF (24 §21.7).** An ASGI middleware inside the CORS
layer asks `application.request_security.guard_request` for every unsafe
method before routing, body parsing, session resolution or any application
code. The verdict is a pure function (`security.request_security`) of the
request's browser metadata against an explicit, pinned origin list:
`Origin` present → must be a configured origin or the API's own origin;
otherwise `Sec-Fetch-Site` must be `same-origin` or `none`; neither header →
not a browser (admitted as such). Failure → `403 CSRF_REJECTED`, a boundary
failure with no application effect. Safe methods are never touched.

**Login-CSRF (24 §21.6).** `POST /auth/login` is governed by the same
origin verdict **and** by the JSON request contract: anything a cross-site
HTML form can produce (`application/x-www-form-urlencoded`,
`multipart/form-data`, `text/plain`, no media type) is refused as
`403 LOGIN_CSRF_REJECTED` before credential validation. A legitimate login
still creates a fresh session (24 §21.5).

**Configuration.** `NQUIRY_ALLOWED_ORIGINS` (comma-separated explicit
origins; default `http://localhost:3000`; a wildcard, a path, a bare host or
`null` refuse startup) feeds both the boundary and CORS from one list.
`NQUIRY_PUBLIC_WEB_BASE_URL` (found necessary by the real lane): when the app
is served from another origin than the API, local post-authentication
destinations (login projection, post-login target, link projection) are
prefixed with it; it must itself be an allowed origin; unset keeps them
relative (the deployment's `/api/` proxy, one origin).

**Protocol callbacks (24 §21.8).** The provider callback GET — a cross-site
navigation by nature — is untouched by the boundary and remains governed by
its own proof (transaction, binding, state, nonce, PKCE, purpose, terminal
state), proven again here with `Sec-Fetch-Site: cross-site`.

## INVARIANTS

1. No unsafe request executes application code unless its browser metadata
   attests an allowed or the API's own origin, or it carries no browser
   metadata at all.
2. No local password login executes credential validation unless, in
   addition, the body is `application/json`.
3. CSRF failure is a boundary failure (`denied`), never an application
   effect; the same hostile request against every unsafe contact changes no
   row and leaves the victim's session intact.
4. CORS and the boundary are pinned to the same explicit origins; neither
   admits a wildcard; CORS is not the boundary (simple requests have no
   preflight and are still refused).
5. Safe requests commit nothing.
6. The provider callback and the API's own consent page keep working
   (cross-site navigation; same-origin form POST).
7. Local destinations after authentication reach the browser-facing app on
   split origins and stay relative on one origin; provider URLs are never
   rewritten.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/security/request_security.py` | new: `Verdict`, `RequestSecurityPolicy`, `evaluate_unsafe_request`, `login_contract_satisfied`, `parse_allowed_origins`, `is_origin` (pure) |
| `packages/application/request_security.py` | new: `guard_request`, policy configuration from `NQUIRY_ALLOWED_ORIGINS`, the two refusal classes |
| `apps/api/src/nquiry_api/http/request_security.py` | new: `RequestSecurityMiddleware` (pure ASGI; own origin from `Host` / `X-Forwarded-*`) |
| `apps/api/src/nquiry_api/main.py` | middleware inside CORS; CORS origins from the same list; web base must be an allowed origin |
| `packages/application/auth_runtime.py` | `web_base_url` from `NQUIRY_PUBLIC_WEB_BASE_URL` (validated origin) |
| `packages/application/http_oidc.py` | `_browser_destination` applied to the four local redirects |
| `scripts/auth_real_stack.sh` | new: AUTH real-stack runner (API :18460, app :13470, hostile origin :13471; refuses a pytest proof database; process-group cleanup) |
| `apps/web/playwright.auth-real.config.ts` | new: AUTH real lane (file-name-anchored match; `AUTH_REAL_SPEC_MATCH=".*"` for every real spec) |
| `apps/web/tests/real-stack/hostile/attack.html` | new: the hostile third-origin page (form POSTs of every shape, credentialed simple fetches) |
| `apps/web/tests/real-stack/auth-csrf.real.spec.ts`, `auth-oidc-link.real.spec.ts` | new: 3 real-browser cases |
| tests | `tests/security/test_auth_request_security.py` (18, no DB), `tests/e2e/test_auth_wu14_csrf.py` (67) |

No frontend code change: the real app's `fetch` and forms already carry the
metadata the boundary reads.

## Case 2 choices (recorded)

- **Mechanism:** Origin / Fetch Metadata against a pinned list, layered with
  CORS, `SameSite=Lax` and the JSON contract (24 §21.7 "defensible layered
  combination"). No synchronizer token: the frontend is a separate origin
  calling a cookie-authenticated API, where a token would add state without
  adding a relation the metadata does not already carry.
- **No browser metadata → admitted.** A client that sends neither `Origin`
  nor `Sec-Fetch-Site` is not a browser; it presents the cookie it holds on
  purpose and is no CSRF victim. Every browser that sends cookies cross-site
  sends `Origin` on POST. Recorded explicitly because it is the one
  deliberate opening of the verdict.
- **Login contract strict:** no media type is refused too (fail closed);
  the test suites and the documented `curl` usage send `application/json`.
- **Distinct refusal classes** for application CSRF and login-CSRF (24 §21.6
  non-collapse), both `denied`.
- **`Sec-Fetch-Site: same-site` is cross-origin** for this boundary (another
  port is another origin); `Origin` decides when present.
- **Own origin from `Host` (+ `X-Forwarded-Proto/Host`)**: needed for the
  API's own consent page form; a hostile page cannot forge `Origin`.
- **CSRF refusals are not persisted as SecurityEvents** (a hostile page could
  fill the audit table at will); 24 §31.1 "where security-relevant" is read
  as: not per hostile request. Disclosed.
- **Real lane database:** the real stack commits; it gets its own database
  (`nquiry_purple_real`) and the runner refuses a pytest proof database.

## RED_RESULT

Collection errors (`security.request_security`, `application.request_security`
absent): 0 of 85 could run. After GREEN the real lane found a product defect
the mocked lane could not: post-authentication `Location` values were relative
paths and, with the app on another origin than the API, landed the browser on
the API (`{"detail":"Not Found"}`). Repaired by `NQUIRY_PUBLIC_WEB_BASE_URL`
with two new falsifiers (85 total). One test expectation corrected (the
DENIED creation policy projects `unavailable`, WU-09's class, not `failed`).
The lane's no-mocking guard refused the first spec for a docstring that
mentioned the mocking call by name — reworded, the guard was right.

**Escalated radius, first run: 11 failed / 1377 passed / 2 skipped.** Two of
the named tests passed in isolation; the proof database held rows the
real-stack runs had committed (identities, Workspaces, Sessions). The proof
database was rebuilt from scratch, the real lane moved to its own database,
the runner now refuses a proof database, and the run was repeated:
**1388 passed, 2 skipped, 0 failed.** The eleven were pollution, not
defects; disclosed with both runs in `evidence/wu14_proof.txt`.

## GREEN_RESULT

85 backend cases (18 pure + 67 API); `tsc` / ESLint clean; vitest 181 (no
change); mocked AUTH lane 33; **AUTH real lane 3 passed**, and with
`AUTH_REAL_SPEC_MATCH=".*"` **8 passed** (every real-stack spec of the
repository on the real stack with the boundary in place — F02 / F03 /
WU-02.12 real flows unchanged); ruff / mypy (259 files) / architecture /
test-only / migration checks clean (`evidence/wu14_proof.txt`,
`evidence/wu14_real_stack.txt`).

## ADVERSARIAL_RESULT

API: 7 unsafe contacts × 7 hostile metadata shapes refused with
`CSRF_REJECTED`, zero row change, victim session intact; 6 legitimate shapes
commit; the boundary answers before the application even without a session;
safe requests commit nothing; attacker-credential login refused from a
foreign / null origin and from cross-site metadata with no session row; four
form-shaped logins refused even from the allowed origin and with no metadata;
legitimate login creates a fresh session twice, wrong password still a
credential denial; the cross-site callback is processed by its own proof;
the consent form passes from the API's origin and is refused from a foreign
one; wildcard / bare-host origins refuse startup; CORS pinned to the same
list and silent for a foreign preflight; split-origin destinations prefixed,
single-origin ones relative; web base must be an explicit origin.
Real browser: the hostile page's urlencoded form, text/plain form, text/plain
fetch and JSON fetch leave no session cookie and `/auth/me` at 401; against a
logged-in victim its logout-all / unlink forms and credentialed fetch leave
the session token, `/auth/me` 200 and the method ACTIVE, while the app's own
logout-all ends the session; the link flow passes all three legs.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..13); the
guard-necessity falsifiers above (every hostile shape × every contact) stand
in.

## AFFECTED_SUITES_RESULT

Escalated to `tests/security`, `tests/semantic`, `tests/regression`,
`tests/e2e`: **1388 passed, 2 skipped** on the rebuilt proof database (the
first, polluted run disclosed above). Real lane 3 / 8; mocked lane 33.

## INVERSE_SWEEP_RESULT

AN EFFECT COMMITTED BY AN UNSAFE REQUEST → the application ran → the
boundary admitted it → `Origin` was allowed or own, or Fetch Metadata said
same-origin / none, or no browser sent it → the request came from the app,
from the API's own page, from an address bar, or from a non-browser holding
its own cookie. For a login: additionally the body was `application/json`,
which no HTML form produces (24 §44.7).

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: a browser's ambient credential can only be spent
by the origins NQUIRY names, and a password can only be spent by a request
no foreign page can shape; everything else fails as a boundary, before
anything happens. CORS and SameSite remain what they are — layers, not the
law (24 §21.7, §21.9).

## FIRST_BROKEN_RELATION_AFTER

**Protocol callback semantics** (24 WU-AUTH-15): the callback contact's
GET-with-effect nature is governed by the transaction proof, but the unit
that states the semantic contract (why the protocol-defined GET may commit a
local session, which steps are proof and which are effect, what a duplicate
delivery sees) and proves it as a whole has not been written; §21.14's
boundary list is to be reconciled against WU-05/07/13's proofs.

## Limitations and ceilings

- Hostile-origin proof uses Chromium only (Firefox / WebKit send the same
  headers; not run here).
- No real Google provider in the real lane (BLOCKED_EXTERNAL).
- CSRF refusals not persisted as audit facts (recorded above).
- No source-mutation proof; ledger deferred; full repository regression at
  the next checkpoint.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-14 proven at an escalated radius including the real
browser/API contract. Next: WU-AUTH-15.
