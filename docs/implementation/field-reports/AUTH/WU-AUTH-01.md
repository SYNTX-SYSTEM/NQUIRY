# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-01 — Repository Binding Reconstruction

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-01 |
| ARCHITECTURE_SOURCE | `docs/architecture/24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md` §37 WU-AUTH-01 (source commit `6e7e402`) |
| PREDECESSOR | `checkpoint-PFC-AC1.1` → `e91961e` (HD-AUTH-02); migration head `e8c2a5f1b7d4` |
| Worktree / branch | `worktrees/auth-identity` / `auth-identity` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03 (`HUMAN_DECISIONS.md`). No §36 boundary reached. |

## Mission

24 WU-AUTH-01: "implementation agent maps actual files, tables, routes, tests
and architecture docs before coding." Must remain impossible: "implementing
from generic auth assumptions." Evidence only: no code, no schema, no route.

## FIRST_BROKEN_RELATION_BEFORE

None proven. The Field had not been reconstructed against the repository at
the pin. Architecture 24 §2–§7 was written against the F03 baseline
(`c9d86ba`); the pin is 43 RED commits later.

## ROOT_SWEEP — what was read

- Architecture 24, all 49 sections, WU-AUTH-01..17, the 116 falsifiers, §36.
- 18 (predecessor), 20 (SFE), and the identity / authentication / session /
  principal / SecurityEvent content of 03, 04, 05, 06, 11, 13, 14, 16, 17.
- Every file listed under "Repository binding" below.
- `PFC/HUMAN_DECISIONS.md` (HD-28), `PFC/HUMAN_AUTHORITY_QUEUE.md`,
  `PFC/WU-PFC-AC1.md`.

## Repository binding (the mapping report)

### Canonical identity
| Relation | Home |
|---|---|
| `UserId` | `packages/semantic_types/ids.py` |
| `users` (id, email UNIQUE, name, record_version, timestamps) | migration `72e4c8ea6772`; `persistence/tables.py::users_table` |
| `AuthenticatedPrincipal(user_id, authentication_session_ref, authentication_time, issuer_ref)`; no authority field | `packages/security/identity.py` (14 §32 shape) |
| `ActorIdentity(ActorClass.HUMAN_USER, user_id)` | `packages/authority/actor.py`; built in `application/http_dispatch.py::_resolve_actor_from_session` |

### Authentication methods
| Relation | State at the pin |
|---|---|
| Local password credential | `local_auth_credentials` (user_id UNIQUE, password_hash), migration `05794035ef3c`; PBKDF2-HMAC-SHA256, 600 000 iterations, 16-byte salt (`security/local_auth.py`) |
| Typed authentication method relation | **absent** (FBR-AUTH-002) |
| External provider identity, OIDC transaction, PKCE, user-agent binding | **absent** |
| Verified email, verification / recovery challenges | **absent** |

### Session
| Relation | Home |
|---|---|
| Server-side opaque session | `local_auth_sessions` (id, user_id, session_token_hash UNIQUE, issued_at, expires_at, revoked_at) |
| Token | 256-bit `secrets.token_urlsafe`; SHA-256 stored; raw value only in the cookie |
| Create / resolve / revoke | `application/auth_handler.py::login / resolve_session / logout`; 12 h lifetime; issuer `nquiry-local-credential-adapter` |
| Cookie | `nquiry_session`; `HttpOnly`; `SameSite=Lax`; path `/`; `Secure` only when `NQUIRY_COOKIE_SECURE=1` (`apps/api/.../http/auth.py`) |
| Session → authentication method or proof provenance | **absent** (no column) |
| All-session, method-scoped, account-disable revocation | **absent** (single session only) |
| Rotation | **absent** |
| Fixation | Login always issues a new token and sets the cookie; a presented cookie is never read by `/auth/login`. Not yet proven by a falsifier. |

### Account creation
| Path | Home | Authority |
|---|---|---|
| Host-operator command | `application/identity_provisioning.py`, `persistence/identity_repository.py`, `nquiry_api/operator/create_identity.py` | HD-28 / NQ-DEC-056: user + credential + SecurityEvent (TB-17), one transaction, no authority |
| Dev-only provisioning | `test_support/dev_identity.py`, `scripts/dev_provision_local_identity.py` | F02 HD-3; refused outside DEVELOPMENT / TEST |
| Demo seed | `scripts/seed_local_demo.py` | NON_PROOF |
| HTTP route that creates an identity | none (pinned by `test_no_http_route_creates_identities`) | — |
| External-provider account creation policy | not materialized; fail-closed by absence | 24 §36 #3–#5, open |

All three creators write the credential through one producer:
`SqlAlchemyLocalCredentialRepository.create`.

### API
`POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
(`apps/api/src/nquiry_api/http/auth.py` → `application/http_dispatch.py::dispatch_login /
dispatch_logout / dispatch_current_session`). Response kinds: `ok`, `denied`;
malformed body → `rejected` (400). No session token in JSON.

### Authorization handoff
Every governed dispatch function resolves identity through
`_resolve_actor_from_session` / `_resolve_principal_from_session` and then runs
the unchanged boundary chain (BND-001 → … → `AuthorityResolver` →
`CommitCoordinator` / BND-014). `x-nquiry-actor-*` headers are inert.

### Browser / HTTP boundary
| Relation | State |
|---|---|
| CORS | `allow_origins=["http://localhost:3000"]` hard-coded, `allow_credentials=True`, methods GET/POST, headers `Content-Type`, `Idempotency-Key` (`nquiry_api/main.py`) |
| Anti-CSRF for unsafe cookie-authenticated requests | **absent** (FBR-AUTH-009) |
| Local password login-CSRF boundary | **absent** (FBR-AUTH-018). The login body is JSON, but nothing rejects a cross-site submission. |
| Redirect target validation | not applicable yet (no redirect-taking route) |
| Rate limiting | **absent** |

### Runtime configuration
`DATABASE_URL`, `NQUIRY_COOKIE_SECURE`, `NQUIRY_ENVIRONMENT` (read by the
operator command and the dev guard; not set in `docker-compose.yml`, PFC HA-20),
`NQUIRY_DEV_IDENTITY_PROVISIONING`. None of 24 §25.2's other variables exist.

### Runtime DB principal
`persistence/engine.py::connect` uses `DATABASE_URL`, which in
`docker-compose.yml` is the bootstrap owner `nquiry` (superuser). The nine
14 §8 principals exist (`infra/local/db_roles.sql`, migration `2feb99a01f9d`)
and are proven only through `SET ROLE` tests. `local_auth_*` tables are in no
capability map (FBR-AUTH-006; owner WU-AUTH-17; PFC HA-09 / HA-10).

### Audit / provenance
Login, logout and session events write no record. The only auth-related
SecurityEvent is `IDENTITY_CREATED` (HD-28). `auth_events` (24 §22.2) is absent.

### Frontend (RED line at the pin)
`apps/web/app/login/page.tsx`, `apps/web/lib/api/authClient.ts`,
`apps/web/components/LogoutButton.tsx`, root route session check
(`apps/web/app/page.tsx`). Projection only; `credentials: "include"`.
The CYAN line (`frontend-symbiotic`) carries a different frontend and is not
part of this worktree.

### Tests at the pin
`tests/security/test_local_auth.py` (12), `tests/security/test_identity.py` (6),
`tests/e2e/test_auth_handler.py` (15), `tests/e2e/test_http_auth.py` (15),
`tests/e2e/test_pfc_ac1_production_account_creation.py` (24),
`tests/security/test_dev_identity_provisioning.py`,
`tests/security/test_db_principals.py`, `apps/web/tests/e2e/auth.spec.ts`
(mocked browser), `apps/web/tests/lib/authClient.test.ts`.

### Constraints from the older architecture that bind this Field
- 06 BND-001: identity carries actor class, is currently valid, carries no
  scope and no authority. "authentication -> authority" is a prohibited path.
- 04 §17: default deny; no fallback to "authenticated user" or "system administrator".
- 11 AC-11-002: a session is "a security credential state, not an authority
  record"; explicit lifetime; revoked or expired sessions cannot authenticate.
- 11 §23 / §38 / §50: no secrets or authentication material in logs, traces, client bundles.
- 11 §41–42: SecurityEvent is the security record for authentication failure and credential misuse.
- 11 GAP-11-008: MFA, credential types, session lifetimes, recovery policy are open product policy.
- 14 §3.1 (enforced by `scripts/check_architecture_dependencies.py`):
  `security` → `semantic_types` only, no DB driver; `application` and
  `nquiry_api` may not import a DB driver; `nquiry_api` → `application`,
  `observability`, `semantic_types`.
- 14 §32: a production adapter "validates issuer, audience, signature, expiry
  and revocation/session state"; "No authority classes are accepted from token claims".
- 13: security is proven negatively; mutation testing is mandatory (AC-13-010).

## Validation of Architecture 24 against the repository

| 24 statement | At the pin |
|---|---|
| §3.7 "no self-service registration … accounts are created only by the seed script or direct DB insert" | Superseded in part: HD-28 added the host-operator command. Still no HTTP creation path. |
| §7 FBR-AUTH-001..018 | All still hold except that FBR-AUTH-007's fail-closed default is in force by absence. |
| WU-AUTH-02..17 | None already satisfied. |
| §22.1 preserve `users`, `local_auth_credentials`, `local_auth_sessions` | All present, unchanged since `05794035ef3c`. |

## FIRST_BROKEN_RELATION_AFTER

**FBR-AUTH-002: canonical identity ↔ authentication method.** Walking the
forward chain `AUTHENTICATION REQUEST → PROTOCOL STATE → IDENTITY PROOF →
CANONICAL IDENTITY → SESSION`, the first relation that does not hold is the one
between a canonical `UserId` and the typed method by which it authenticates: a
credential exists only as an adapter-specific row. Every later relation
(session traceability, method revocation, provider identity, linking,
recovery) consumes that relation. Its owner is WU-AUTH-02, then WU-AUTH-03
(existing credentials through the method model).

The login-CSRF boundary (FBR-AUTH-018) is earlier in request order but its
owner WU-AUTH-14 depends on WU-AUTH-04 (24 §37), and it does not block the
identity relations. It stays queued in the architecture's order.

## Proof

| Item | Result |
|---|---|
| RED_RESULT / GREEN_RESULT | Not applicable: no relation is materialized. The falsifier of this unit ("new code ignores existing auth_handler, local_auth, http_dispatch or migration") is checked by every later unit against this mapping. |
| MIGRATIONS | None. `MIGRATION_STATIC_CHECK::PASS (32 revisions, single head e8c2a5f1b7d4)`; `MIGRATION_LIVE_CHECK::PASS`. |
| FULL_REPOSITORY_REGRESSION (baseline) | See `STATUS.md` "Baseline". |
| MUTATION / ADVERSARIAL / SECURITY | Not applicable (documentation only). |
| INVERSE_SWEEP_RESULT | The mapping traces each visible authentication effect back to its producer; the chain `visible authenticated state → /auth/me → cookie → hash lookup → session row → UserId` holds and ends without method or proof provenance (the FBR above). |
| FIELD_RECONSTRUCTION_RESULT | The Field reconstructs as 24 §3.2 plus HD-28. No accidental architecture found. |

## FILES_CHANGED

`docs/implementation/field-reports/AUTH/{WU-AUTH-01.md, STATUS.md, HUMAN_DECISIONS.md}` (new).

## Limitations and ceilings

- Proof infrastructure: an isolated PostgreSQL 17 container
  (`nquiry-purple-postgres`, 127.0.0.1:15460, database `nquiry_purple_test`)
  used only by PURPLE. Local interpreter is Python 3.10; the images run 3.13.
- Human decisions are recorded field-locally; 16 §41 reconciliation is deferred
  (`HUMAN_DECISIONS.md`, "Ledger reconciliation").
- The frontend in this worktree is the RED-line frontend, not CYAN's.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-01 PASS (evidence). Next: WU-AUTH-02.
