# NQUIRY FIELD REVIEW REPORT — AUTH (PURPLE)

## Field

AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD
(`docs/architecture/24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`,
WU-AUTH-01..17). Materialized autonomously under the PURPLE brief
(HD-AUTH-01), one proven relation at a time, in the isolated worktree
`worktrees/auth-identity`, branch `auth-identity`.

## Status

**FIELD_GREEN — READY_FOR_HUMAN_REVIEW.** Seventeen Work Units proven and
locally committed (never pushed, never tagged; HD-AUTH-03). Five Human
Authority boundaries were recorded; HA-AUTH-04 is resolved (HD-AUTH-05,
HOST_OPERATOR); HA-AUTH-01, -02, -03, -05 remain OPEN with their fail-closed
defaults in force. The real Google provider proof is BLOCKED_EXTERNAL.

## Review bundle (24 §46)

| Item | Where / what |
|---|---|
| Repository HEAD | `b939037667eecc33c9cd618edeaff60e0750ba68` |
| Branch | `auth-identity` (17 commits on `checkpoint-PFC-AC1.1` = `e91961e`; HD-AUTH-02) |
| Files changed | 145 (125 added, 20 modified; `evidence/field_files_changed.txt`) |
| Migrations added | 10, chain `e8c2a5f1b7d4` → `f1a7c3d9b2e4` → `a2c4e6f8b1d3` → `b3d5f7a9c2e6` → `c4e6a8b1d3f5` → `d5f7b9c1e3a7` → `e6a8c1d3f5b9` → `f7b9d1e3a5c8` → `a8c1e3f5b7d9` → `b9d2f4a6c8e1` → `c1e3a5b7d9f2` (42 revisions, single head; every one downgrade / upgrade proven in its unit) |
| Auth routes added | `GET /auth/sessions`, `POST /auth/logout-all`, `POST /auth/sessions/{id}/revoke` (WU-04); `GET /auth/providers`, `GET /auth/oidc/{provider}/start`, `GET /auth/oidc/{provider}/callback`, `GET|POST /auth/test-provider/authorize` (WU-07); `POST /auth/oidc/{provider}/link/start`, `GET /auth/oidc/{provider}/link/callback`, `GET /auth/methods` (WU-10); `POST /auth/email/verification/start|complete`, `GET /auth/emails`, `GET /auth/test-mail/outbox` (WU-11); `POST /auth/recovery/start|complete` (WU-12); `POST /auth/methods/{method_id}/unlink` (WU-13). Pre-existing: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`. No HTTP route creates or disables identities (operator commands). |
| Persistence schema diff | `packages/persistence/tables.py` +322 lines: `authentication_methods`, `oidc_auth_transactions`, `external_provider_identities`, `auth_challenges`, `verified_emails`, `recovery_challenges`; `local_auth_credentials.authentication_method_id`; `local_auth_sessions` method / provenance / reason; `users.disabled_at` / `disabled_provenance`; CHECKs, triggers and partial indexes in the migrations |
| Tests added | 34 test files (backend e2e / security / semantic, vitest, mocked Playwright, real-stack Playwright); full live lane 2007 / 2 at the pin → 2456 / 2 at HEAD |
| Local stack proof | `evidence/field_closure_regression.txt`: live 2456 passed / 2 skipped (0:36:46), no-DB 1020 passed, migrations PASS, tree hash unchanged during the run |
| Browser proof | mocked AUTH lane 33 (66 with every mocked spec); **real stack** `scripts/auth_real_stack.sh`: 3 AUTH real cases, 8 with every real-stack spec of the repository, run with the real API's authentication persistence on the scoped principal |
| Local login-CSRF boundary proof | WU-14: `tests/e2e/test_auth_wu14_csrf.py` (origin verdict + JSON contract before credential validation) and `apps/web/tests/real-stack/auth-csrf.real.spec.ts` (hostile third origin, real browser: urlencoded / text-plain forms, text-plain and JSON fetch → no session) |
| Google proof | **BLOCKED_EXTERNAL**: `StandardOidcProvider` is instantiable from configuration, configured nowhere (no client id / secret / redirect URI — an external secret PURPLE must not create). Proven against the local RS256 test issuer only (WU-07) |
| OIDC transaction proof | WU-05 (`tests/security/test_auth_oidc_transactions.py`), WU-07 |
| Transaction state machine proof | WU-05 (CHECKs + transition trigger, "exactly 24 §11.4"); WU-13 terminal states at the HTTP contact |
| Atomic claim proof | WU-05 (`UPDATE … FROM (SELECT … FOR UPDATE) RETURNING`, two connections, verifier returned once) |
| Initiating user-agent binding proof | WU-05/07 (binding cookie, transplanted callback fails before the exchange); WU-15 bypass matrix |
| Login / session swapping prevention proof | WU-07 (transplant), WU-14 (login-CSRF, real browser), WU-16 (principal from committed session state) |
| Redirect target validation proof | WU-06 (`security.redirect_target`, guard-necessity falsifiers), WU-07 start binding |
| Provider cancel / error proof | WU-07 (`access_denied`, provider error → terminal without exchange), WU-13/15 |
| Concurrency proof | WU-05 claim, WU-08 duplicate subject, WU-09 two first logins, WU-11 two completions, WU-12 two completions, WU-13 (DB uniqueness), two real connections with `lock_timeout` |
| PKCE verifier confidentiality proof | WU-05 (never returned at start, consumed once, NULL at terminal), WU-07 (gone from the row before the exchange), WU-15 |
| ID Token validation order proof | WU-07 (signature / audience / expiry by PyJWT, issuer by adapter, defects rejected after the exchange) |
| Nonce validation order proof | WU-07 (`test_the_nonce_is_not_trusted_before_the_id_token_is_validated`) |
| Account creation boundary proof | WU-09 (DENIED default; SELF_REGISTRATION DEV / TEST only; email collision; unverified email; no authority) |
| Account linking proof | WU-10 (own-identity link, collision, purpose binding, rotation); WU-13 re-link of an unlinked subject |
| Email proof | WU-11 (challenge hash only, single use, attempt limit, one active relation per address) |
| Recovery proof | WU-12 (non-enumerating start, single-use proof, credential replaced once, `CREDENTIAL_RESET`, no session) |
| Anti-CSRF proof | WU-14 (7 contacts × 7 hostile shapes; real browser against a logged-in victim) |
| CORS proof | WU-14 (pinned to `NQUIRY_ALLOWED_ORIGINS`; wildcard refuses startup; foreign preflight unanswered; CORS ≠ boundary) |
| Runtime DB-principal capability proof | WU-17 (`tests/security/test_auth_db_principal.py`: exact matrix over every table as `auth_runtime`; 14 refused statements; every live path scoped; real lane scoped) |
| Protocol callback bounded-effect proof | WU-15 (declared contacts and write sets measured over every table; 13 bypass shapes; 16 ordinary GETs write nothing) |
| Adversarial proof | each unit's ADVERSARIAL_RESULT; mutation step = guard-necessity falsifiers (no source-mutation script since WU-05, disclosed) |
| Authorization regression proof | WU-16 (6 identity kinds × the full F09-2 protected route table; membership path; founding parity; disabled identity) |
| Session fixation proof | WU-04 (fresh session per login, rotation keeps issued_at / expires_at), WU-14 (second login = new token), WU-16 |
| Secret redaction statement | No secret in the repository: Google credentials absent; local roles use the `*_local_dev_only` convention of the existing `db_roles.sql`; tokens, verifiers and hashes never appear in responses, logs, SecurityEvents or report prose (checked per unit); report prose carries no attack-payload lists (classifier constraint since WU-05/06, disclosed) |
| Unresolved human authority boundaries | HA-AUTH-01 production account creation policy (DENIED); HA-AUTH-02 production recovery policy (DENIED); HA-AUTH-03 last-method unlink (NEVER); HA-AUTH-04 **resolved** by HD-AUTH-05 (HOST_OPERATOR, 2026-10-01); HA-AUTH-05 deployment switch to `auth_runtime` (= PFC HA-10; UNSCOPED_BOOTSTRAP declared). Touched, undecided, non-blocking: 24 §36 #1 / #6, #9, #10, #13, #15, #16, #18. Blocks: `WU-AUTH-09/12/13/17.md`; queue: `HUMAN_DECISIONS.md` |

## Human decisions used

HD-AUTH-01 (Field authorization), HD-AUTH-02 (base pin `checkpoint-PFC-AC1.1`),
HD-AUTH-03 (local per-unit commits, no push, no tags), HD-AUTH-04
(progressive proof radius from WU-11; full regression at closure), HD-AUTH-05
(HA-AUTH-04 → HOST_OPERATOR, after FIELD_GREEN). Consumed
from predecessors: HD-28 / NQ-DEC-056, F02 HD-3, F02 HD-6. 16 §41 ledger
reconciliation deferred to integration (disclosed in `HUMAN_DECISIONS.md`).

## Initial state (the pin)

Local password login only (`/auth/login`, `/auth/logout`, `/auth/me`),
sessions without method attribution or reason, no provider, no
verification, no recovery, no unlink, no disable, no CSRF boundary beyond
CORS + SameSite, auth tables outside the DB-principal map (WU-AUTH-01's
reconstruction).

## Final state

Authentication method model; local credentials through it; sessions with
method, provenance, closed revocation reasons and scopes; OIDC Authorization
Code + PKCE transactions with atomic claim, binding and terminal states;
redirect target validation; provider adapter (Google-shaped, test issuer);
provider identity binding; account creation boundary; linking; email
verification; recovery; revocation expansion (unlink, disable); anti-CSRF
and login-CSRF boundaries with pinned origins; declared protocol contacts;
authorization regression; scoped authentication DB principal. The Field
ends at `AuthenticatedPrincipal` — proven unchanged in shape and reach.

## Work Units

| WU | Commit | Report |
|---|---|---|
| 01 Repository Binding Reconstruction | `a0f5982` | `WU-AUTH-01.md` |
| 02 Authentication Method Model | `53823d6` | `WU-AUTH-02.md` |
| 03 Local Credential Migration Compatibility | `bf046b9` | `WU-AUTH-03.md` |
| 04 Authenticated Session Evolution | `3ffbd1b` | `WU-AUTH-04.md` |
| 05 OIDC Auth Transaction Field | `4495345` | `WU-AUTH-05.md` |
| 06 Redirect Target Validation | `69b806a` | `WU-AUTH-06.md` |
| 07 OIDC Provider Adapter | `5aa13ae` | `WU-AUTH-07.md` |
| 08 Provider Identity Binding | `e097de1` | `WU-AUTH-08.md` |
| 09 Account Creation Boundary | `8d3df59` | `WU-AUTH-09.md` (HA-AUTH-01) |
| 10 Account Linking | `4e29c9f` | `WU-AUTH-10.md` |
| 11 Email Verification | `8ae8b9e` | `WU-AUTH-11.md` |
| 12 Recovery | `f171484` | `WU-AUTH-12.md` (HA-AUTH-02) |
| 13 Revocation Expansion | `171a6e7` | `WU-AUTH-13.md` (HA-AUTH-03, -04) |
| 14 Anti-CSRF Boundary | `26a134c` | `WU-AUTH-14.md` |
| 15 Protocol Callback Semantics | `5fe3cd6` | `WU-AUTH-15.md` |
| 16 Authorization Regression | `a4c3bc3` | `WU-AUTH-16.md` |
| 17 Runtime DB Principal Capability Boundary | `b939037` | `WU-AUTH-17.md` (HA-AUTH-05) |

## First Broken Relations found / repaired

| Id | Relation | Repaired at |
|---|---|---|
| FBR-AUTH-001 | authentication method as a relation | WU-02 / WU-03 |
| FBR-AUTH-002 | provider proof → canonical identity (transaction, claim, binding, validation, policy) | WU-05..09 |
| FBR-AUTH-003 | email → verified relation | WU-11 |
| FBR-AUTH-004 | loss of method → recovery proof → restored access | WU-12 |
| FBR-AUTH-005 | revocation scopes and propagation (method, binding, account) | WU-04, WU-13 |
| FBR-AUTH-006 | authentication persistence ↔ DB-principal capability | WU-17 |
| discovered (WU-14, real lane) | relative post-auth `Location` landed on the API on split origins | `NQUIRY_PUBLIC_WEB_BASE_URL` |
| discovered (WU-14) | real-stack commits in the pytest proof database caused 11 pollution failures | real lane on its own database; runner refuses proof databases; proof database rebuilt |

## Disclosed deviations and limits

- No source-mutation scripts since WU-05 (classifier constraint); the
  mutation step is carried by guard-necessity falsifiers in every unit.
- Report prose keeps no attack-payload lists (same constraint).
- Cross-Field test edits, each disclosed in its unit: the F09-2 sweep's
  route registration (by that file's own rule), WU-08's adapter surface pin
  (WU-13), the nine-principal pins and `users` leaving the no-writer list
  (WU-17), `test_auth_wu04`'s reason vocabulary (WU-12).
- One pre-existing `ruff format` finding in a RED Markdown bundle under
  `field-reports/F04/review/`, not touched (since WU-02).
- HD-AUTH-04 cadence: WU-11..17 proven at the affected radius (WU-14
  escalated to the whole HTTP surface); this closure run is the full
  regression.
- 16 §41 ledger reconciliation deferred to integration.

## Integration notes for the reviewer

- Databases need `infra/local/db_roles.sql` re-run once (idempotent) for the
  new `auth_runtime` role before migration `c1e3a5b7d9f2` is applied.
- New runtime variables (all optional, all fail closed): `NQUIRY_AUTH_PROVIDER_MODE`,
  `NQUIRY_GOOGLE_*`, `NQUIRY_PUBLIC_API_BASE_URL`, `NQUIRY_ACCOUNT_CREATION_POLICY`,
  `NQUIRY_EMAIL_DELIVERY_MODE`, `NQUIRY_RECOVERY_POLICY`,
  `NQUIRY_ALLOWED_ORIGINS`, `NQUIRY_PUBLIC_WEB_BASE_URL`,
  `NQUIRY_AUTH_DATABASE_URL`. `docker-compose.yml` and the deployment are
  unchanged (HA-AUTH-05 / HA-10).
- The real-stack runner must never point at a pytest proof database.
