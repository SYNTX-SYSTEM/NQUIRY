# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-17 — Runtime DB Principal Capability Boundary

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-17 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-17; §7 FBR-AUTH-006; §21.18; §18.3; §25.2; 14 §8 / PKG-25 (`ServicePrincipal`, `SECURITY_CAPABILITY_MAP`, migration `2feb99a01f9d`, `infra/local/db_roles.sql`); 11 §47; PFC HA-09 / HA-10 |
| PREDECESSOR | WU-AUTH-16 `a4c3bc3` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL falsifiers (33 live-principal cases, no DB structural cases) → AFFECTED suites: all of `tests/security`, `tests/semantic`, `tests/regression`, the sweep, WU-03/04/13/16, `test_http_auth`, the connection-lifecycle suite, HD-28's suite (610 / 2) + the AUTH real lane running with the scoped principal. Field closure's full regression follows this unit. |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01..04 OPEN. **HA-AUTH-05 recorded below (PFC HA-10): the deployment switch to the scoped principal is a production action PURPLE does not perform.** |

## FIRST_BROKEN_RELATION_BEFORE

Authentication persistence (the pre-existing `users` / `local_auth_*` and
every relation this Field added) was in no DB-principal capability map; the
live HTTP authentication path ran as whatever `DATABASE_URL` names — in the
local compose and the deployment the bootstrap owner `nquiry` (24 §21.18
"known limitation"; FBR-AUTH-006).

## CURRENT_RELATION

- **Explicit capability map** `security.db_capabilities.AUTH_PERSISTENCE_CAPABILITIES`:
  SELECT / INSERT / UPDATE on `users`, `local_auth_credentials`,
  `local_auth_sessions`, `authentication_methods`,
  `external_provider_identities`, `oidc_auth_transactions`,
  `auth_challenges`, `verified_emails`, `recovery_challenges`; INSERT only on
  `security_events`; DELETE nowhere; nothing of the business / authority
  field. Folded into the repository's own `SECURITY_CAPABILITY_MAP` as the
  tenth `ServicePrincipal`, `AUTH_RUNTIME`.
- **Real principal** `auth_runtime` (`infra/local/db_roles.sql`, LOGIN, no
  superuser / createdb / createrole / bypassrls) granted exactly the map by
  migration `c1e3a5b7d9f2`; `api_reader` and `governed_commit_writer`
  receive SELECT on the three session-resolution tables (the one auth read
  every governed request makes); `test_principal` receives DML on the
  authentication tables as on every other protected table.
- **Scoped connector** `persistence.engine.connect_auth`: with
  `NQUIRY_AUTH_DATABASE_URL` set, authentication persistence runs on that
  principal; unset, it is exactly `connect()` and the runtime declares
  `auth_persistence_scope() == "UNSCOPED_BOOTSTRAP"` — a declaration, never
  a claim. Bound by every authentication module (`http_oidc`, `http_email`,
  `http_recovery`, `http_revocation`, the six authentication dispatchers of
  `http_dispatch`, the two host-operator commands).
- **Proof over a real connection as `auth_runtime`**: the capability matrix
  of every table of the database equals the map exactly; fourteen
  out-of-scope statements fail with `permission denied`; every live
  authentication path works scoped (login, sessions, verification,
  recovery, link, unlink, logout-all, provider first login with account
  creation, account disable); the scoped principal cannot read or build
  business state; the AUTH real lane runs its three browser cases with the
  real API's authentication persistence on `auth_runtime`.

## INVARIANTS

1. The runtime principal of authentication persistence holds exactly the
   declared capability set — no more (measured over every table), no less
   (every live path works).
2. No principal of the authentication path can DELETE an authentication
   relation or read the audit it appends to.
3. Existing live auth persistence (`users`, `local_auth_*`) and the
   relations added by WU-02..13 are under one discipline (one map, one
   migration, one proof).
4. Business principals read sessions, methods and users only; they write
   none of the authentication relations.
5. Bootstrap / test authority is never represented as runtime authority:
   `SCOPED` is declared only when a scoped connector is configured.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/security/db_capabilities.py` | new: the capability map, session-resolution reads, principal name |
| `packages/security/identity.py` | `ServicePrincipal.AUTH_RUNTIME`; `AUTH_PROTECTED_TABLES`; the map folded into `SECURITY_CAPABILITY_MAP` (api_reader + session reads; governed writer + session reads; test_principal + auth tables) |
| `infra/local/db_roles.sql` | the `auth_runtime` role |
| `migrations/versions/c1e3a5b7d9f2_auth_runtime_principal.py` | new: the grants (reversible) |
| `packages/persistence/engine.py` | `connect_auth`, `auth_scope_configured`, `auth_persistence_scope`; `_connect_with` shared by both connectors |
| `packages/application/http_dispatch.py` | `_auth_connection()` for the six authentication dispatchers |
| `packages/application/http_oidc.py`, `http_email.py`, `http_recovery.py`, `http_revocation.py` | `connect` bound to `connect_auth` |
| `packages/application/identity_provisioning.py`, `account_disable.py` | operator commands default to the auth connector |
| `scripts/auth_real_stack.sh` | the real API runs its authentication persistence as `auth_runtime` |
| tests | `tests/security/test_auth_db_principal.py` (33, live), `test_service_identity.py` (+1, the ten-principal pin, api_reader / test_principal shapes, `users` leaves the no-writer list), `test_db_principals.py` (name of the all-principals test) |

## Case 2 choices (recorded)

- **A tenth principal, not a widened existing one.** 14's nine are
  component writers; none is "the authentication runtime". Mixing auth into
  `governed_commit_writer` would collapse AUTHENTICATION into the governed
  commit path; `api_reader` must never read hashes.
- **`users` gets a writer.** PKG-25 listed `users` among tables with no
  production writer; since HD-28 (host-operator creation) and WU-09 /
  WU-13 (policy creation, disable) it has one, and it is this principal.
- **Business principals read sessions.** Every governed request resolves
  the cookie; without the three SELECTs a scoped business runtime could not
  authenticate anyone. No write.
- **Fallback is identity, not silence.** Unscoped means `connect_auth() ==
  connect()`, byte-for-byte the pre-WU-17 behaviour, with the scope
  declared. The six dispatchers of `http_dispatch` keep the module's own
  `connect` in that case, which is also what every existing fixture
  redirects (no cross-Field fixture change was needed).
- **The API process identity** (one principal for the whole HTTP server, or
  separate connectors per path as materialized here) and **the deployment
  switch** are HA-10; `docker-compose.yml` is left unchanged.
- **Cross-Field test edits**, disclosed: the nine-principal pins in
  `test_service_identity.py` / `test_db_principals.py` (24 §21.18 extends
  14's list; the pins now name ten) and `users` leaving
  `_NO_GOVERNED_WRITER_YET_TABLES`.

## RED_RESULT

Collection error (`security.db_capabilities` absent): 0 of 33 could run.
First GREEN of the live suite on the first run after the grants. Affected
run 1: `test_service_identity::test_exactly_the_nine_named_principals_exist`
failed (the pin) → the map was folded into `SECURITY_CAPABILITY_MAP`, pins
updated, one own assertion corrected; run 2: 610 passed.

## GREEN_RESULT

33 live cases + the structural suite; static gates clean (ruff, mypy 260
files, architecture / test-only imports, migration static + live); migration
`c1e3a5b7d9f2` downgrade / upgrade PASS; AUTH real lane 3 passed with
`NQUIRY_AUTH_DATABASE_URL` on `auth_runtime` (`evidence/wu17_proof.txt`).

## ADVERSARIAL_RESULT

Capability matrix exact over every table; fourteen out-of-scope statements
refused (business reads and writes, every DELETE on an auth relation, audit
read and update, authority inserts); scoped principal cannot read
`workspaces`; business principals hold no write on any auth relation and no
read beyond session resolution; the role is no superuser; scope declaration
flips only with the connector.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..16); the grant
migration's necessity is proven by the exact-matrix test (any missing or
extra grant fails it).

## AFFECTED_SUITES_RESULT

`tests/security`, `tests/semantic`, `tests/regression`, the sweep,
WU-03/04/13/16, `test_http_auth`, connection lifecycle, HD-28's suite:
**610 passed, 2 skipped** (0:07:22). Real lane scoped: 3 passed.

## INVERSE_SWEEP_RESULT

AN AUTHENTICATION ROW WRITTEN AT RUNTIME → by a connection of the
authentication connector → under `auth_runtime` when the deployment is
scoped (and the grant for that table and verb exists in exactly one
migration, from exactly one map) or under the request connector when it
declares itself unscoped → never under a principal that could also write a
business row, and never a DELETE.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: the authentication Field has a database identity
of its own whose reach is the Field's relations and nothing beyond, the
reach is one declared map proven against the live database, and the
runtime states which identity it runs under instead of implying one. That
is 24 §21.18 complete up to the one act that is not PURPLE's: switching a
running deployment.

## TRUE_HUMAN_AUTHORITY_BOUNDARY (recorded, not crossed) — HA-AUTH-05

```
TRUE_HUMAN_AUTHORITY_BOUNDARY
HA_ID: HA-AUTH-05 (= PFC HA-10 "Deployment effect of runtime isolation"; 24 §21.18)
CURRENT_WORK_UNIT: WU-AUTH-17
FIRST_BROKEN_RELATION: live deployment / local compose runtime → scoped authentication principal → authentication persistence
EXACT_QUESTION: When and how does the running deployment (nquiry.condyn.eu) and the local compose stack switch their authentication persistence to `auth_runtime` (role creation on the server, production credential source, `NQUIRY_AUTH_DATABASE_URL` in the deployment's environment), and does the HTTP server as a whole receive a scoped identity (one principal for all paths) or per-path connectors as materialized here?
WHY_NOT_DERIVABLE: a production action with credentials (PFC HA-10, GAP-11-013; 11 §23 secret management); the API-process identity is not defined by 14's nine principals; HD-28's production precedent covers identity creation, not runtime principals.
AUTHORITATIVE_PREDECESSORS: 24 §21.18, §25.2; 14 §8 / PKG-25; PFC HA-09 / HA-10; deployment f5 §4 / §10; HD-28.
STRUCTURALLY_LEGITIMATE_OPTIONS:
  (a) SWITCH AUTH ONLY — run `infra/local/db_roles.sql` (production credential for `auth_runtime`), apply migrations, set `NQUIRY_AUTH_DATABASE_URL` for the API; business paths stay on the current principal.
  (b) SWITCH THE API PROCESS — define an API-process principal (or set `DATABASE_URL` itself to a scoped union) so that no path runs as the bootstrap owner; needs the business-path capability decision (HA-10 proper).
  (c) LOCAL COMPOSE FIRST — (a) for `docker-compose.yml` only, deployment later.
  (d) STAY UNSCOPED, DECLARED — nothing changes; the runtime keeps declaring UNSCOPED_BOOTSTRAP.
DEFAULT_IF_UNDECIDED: (d): unset connector = pre-WU-17 behaviour, declared as such; no production change by PURPLE.
DOWNSTREAM_RELATIONS_BLOCKED: the deployment's runtime isolation (HA-10). NOT blocked: Field closure.
FILES_CURRENTLY_CHANGED: none beyond this Work Unit's own commit.
CURRENT_PROOF_STATUS: WU-AUTH-17 proven in TEST with the scoped principal (unit, affected suites, real lane); production unswitched.
```

## FIRST_BROKEN_RELATION_AFTER

None inside 24 §37's seventeen Work Units. Next: FIELD closure (24 §46):
the one full fresh repository regression, the review bundle, FIELD_GREEN.

## Limitations and ceilings

- Deployment and compose remain on the bootstrap owner until HA-AUTH-05 /
  HA-10 (declared `UNSCOPED_BOOTSTRAP`).
- The business-path runtime principal of the HTTP server is outside this
  Field (HA-10).
- No source-mutation proof; ledger deferred to integration.

## CURRENT_FIELD_STATUS

IN_PROGRESS → closure. WU-AUTH-17 proven; HA-AUTH-05 OPEN with (d) in force.
