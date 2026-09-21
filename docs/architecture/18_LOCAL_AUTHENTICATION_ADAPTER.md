# 18: Local Authentication Adapter

## DOCUMENT STATUS

MATERIALIZED, PROVEN AGAINST REAL POSTGRESQL, A REAL RUNNING CONTAINER,
AND A REAL BROWSER (Playwright, `apps/web/tests/e2e/auth.spec.ts`),
NOT PRODUCTION-APPROVED. Classification remains `ARCHITECTURAL
PROTOTYPE` only (14 §43) — it does not claim production readiness,
regulatory compliance, or that HARD-DEP-001/HARD-DEP-002 are resolved.
Authored as an explicitly-authorized successor field to Architecture
17 (`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`)
and the "NQUIRY LOCAL FULL-STACK RUNTIME ACCEPTANCE" field
(`docs/implementation/proof-reports/FULLSTACK-RUNTIME-ACCEPTANCE.md`).

## AUTHORITY AND SCOPE

Authority hierarchy unchanged: LEVEL 1 → LEVEL 2 → 00 → … → 17 → this
document. This document does not redefine any upstream semantic; it
materializes the "deterministic test adapter" half of 14 §32's own
already-authorized pair ("pluggable OIDC adapter plus deterministic
test adapter `[IMPLEMENTATION CHOICE]`"), hardened into a REAL,
browser-usable local login — not a new authentication concept, and not
a decision about which production identity provider NQUIRY will
eventually use (GAP-14-001, still open).

## UPSTREAM AUTHORITATIVE SOURCES

- 14 §32 (AUTHENTICATION AND SERVICE IDENTITY: "Production-compatible
  adapter validates issuer, audience, signature, expiry and
  revocation/session state... Test adapter is deterministic." /
  `AuthenticatedPrincipal(UserId, authentication_session_ref,
  authentication_time, issuer_ref)`)
- 16 §56 GAP-14-001 ("Concrete production identity provider selection
  is not required for architectural prototype semantics" — this field
  does not close this gap; see HARD-DEP-001 RELATION below for the
  strictly separate, still-open bootstrap question)
- `packages/security/identity.py` (PKG-01's own `AuthenticatedPrincipal`/
  `IdentityPort`/`ExternalCredential` — reused, not reinvented; the new
  session mechanism resolves to this exact same type)
- `docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`'s
  own disclosed weakness: `application.http_dispatch.resolve_actor`
  trusted a bare `x-nquiry-actor-user-id` request header "at face
  value... No cryptographic verification occurs anywhere in this
  path." This field closes exactly that weakness for the two real,
  browser-facing production routes Architecture 17 built.

## FIELD PURPOSE

Materialize a real, local, browser-usable login: a human opens
`http://localhost:3000/`, is sent to a real `/login` page if not
authenticated, submits a real email/password, and receives a real,
server-verified session — closing the specific, disclosed GAP-14-001
transport weakness (an unverified header) without inventing a
production OIDC integration, and without touching HARD-DEP-001 (who
may legitimately be a Workspace's governance root).

## FIELD BOUNDARY

IN SCOPE: real password-credential storage and verification
(`local_auth_credentials`); real, server-verified HTTP sessions
(`local_auth_sessions`, an `HttpOnly` cookie); `POST /auth/login`,
`POST /auth/logout`, `GET /auth/me`; rewiring the two existing
Architecture-17 routes to require that session instead of trusting a
header; a real `/login` page and a real root-route session check/
redirect. OUT OF SCOPE (unchanged): a real external OIDC/IdP
integration (GAP-14-001 itself); self-service registration or password
reset; any Workspace-list/dashboard UI or Query; any change to
BND-001..018, `AuthorityResolver`, `CommitCoordinator`, or any other
domain/authority semantic; HARD-DEP-001 (see its own section below).

## CURRENT MATERIALIZED STATE

- `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` — real
  FastAPI routes (`apps/api/src/nquiry_api/http/auth.py`), proven
  against real PostgreSQL (`tests/e2e/test_auth_handler.py`,
  `tests/e2e/test_http_auth.py`) and against the real, running
  `docker compose` `api` container (curl transcripts,
  `docs/implementation/proof-reports/LOCAL-AUTH-ADAPTER.md`).
- `GET /workspaces/{w}/sessions/{s}` and `POST /decisions/{d}/decide`
  now require that same real session — the former header-trust path
  is removed entirely, not merely deprecated.
- Real `/login` page and a real root-route (`/`) session check,
  proven end-to-end with a real Chromium browser
  (`apps/web/tests/e2e/auth.spec.ts`).

## CURRENT UNMATERIALIZED STATE

- No real external OIDC/IdP integration exists (GAP-14-001 unchanged,
  open).
- No self-service registration/password reset UI or route.
- No Workspace-list/dashboard UI — the root route lands on one
  operator-configured default Session
  (`NEXT_PUBLIC_DEFAULT_WORKSPACE_ID`/`NEXT_PUBLIC_DEFAULT_SESSION_ID`),
  disclosed as a bounded routing convenience, not a new Query
  capability (14 §13 gains no new row).

## CAPABILITY CLASSIFICATION

| Capability | Classification |
|---|---|
| Real local email/password login, real session issuance | ALREADY_ARCHITECTURALLY_DEFINED (14 §32, "deterministic test adapter") → now MATERIALIZED |
| Session-cookie identity resolution replacing header trust | IMPLEMENTATION_MATERIALIZATION_REQUIRED (closes a disclosed weakness) → now MATERIALIZED |
| Real production authentication (OIDC) | HUMAN_DECISION_REQUIRED / BLOCKED (GAP-14-001, unchanged, open) |
| Legitimate first Workspace governance-root bootstrap | HUMAN_DECISION_REQUIRED / BLOCKED (HARD-DEP-001, unchanged, open — see its own section) |
| Workspace-list/dashboard UI | DEFERRED_OUTSIDE_FIELD (no frontend contract demands it yet) |

## PORTS AND ADAPTERS — WHERE EACH NEW MODULE SITS

Same 3-layer split as every other port/adapter pair already in this
codebase (`security.identity.IdentityPort` → its concrete adapters;
`security.workspace.WorkspaceContextPort` → `persistence.
SqlAlchemyWorkspaceContext`) — this field adds one more instance of
the identical pattern, not a new one:

```text
packages/security/local_auth.py          <- PORT layer (types + ports)
  - hash_password / verify_password / generate_session_token /
    hash_session_token   (pure functions, no I/O, no framework)
  - LocalCredentialRecord / LocalSessionRecord   (plain dataclasses)
  - LocalCredentialRepository / LocalSessionRepository
    (Protocols -- "what a concrete adapter must be able to do",
    no SQL, no database import at all: `security`'s own
    forbidden-dependency ceiling is `semantic_types` only)
        |
        | implemented by
        v
packages/persistence/local_auth_repository.py   <- ADAPTER layer
  - SqlAlchemyLocalCredentialRepository
  - SqlAlchemyLocalSessionRepository
    (the ONLY two classes in this whole field that import `sqlalchemy`
    or know the real table shapes -- `persistence` is the one layer
    14 section 3.1's own forbidden-dependency matrix permits to import
    a DB driver at all)
        |
        | used by
        v
packages/application/auth_handler.py     <- ORCHESTRATION layer
  - login() / resolve_session() / logout()
    (business logic: "verify a password, issue a session, check a
    session" -- takes the two Protocols above as parameters, never
    imports a concrete SqlAlchemy class directly, and never imports
    `sqlalchemy` itself; this is the same "application may import
    persistence's concrete classes to CONSTRUCT them, but the actual
    logic functions take the abstract port type" shape every other
    *_handler.py in this codebase already has)
        |
        | called by
        v
packages/application/http_dispatch.py    <- COMPOSITION ROOT
  - dispatch_login / dispatch_logout / dispatch_current_session
    (opens the real DB connection, builds the concrete
    SqlAlchemyLocal*Repository instances, calls auth_handler's
    functions with them -- the one place in this field where "which
    concrete adapter" is actually decided)
        |
        | called by
        v
apps/api/src/nquiry_api/http/auth.py     <- HTTP ADAPTER (thin)
  - POST /auth/login, /auth/logout, GET /auth/me
    (extracts a JSON body/cookie, calls exactly one dispatch_*
    function, translates the result into an HTTP response + sets/
    clears the cookie -- no business logic of its own, matching
    `queries.py`/`commands.py`'s own established thin-adapter
    discipline)
```

**Why this split, not one file**: it is the identical reason every
other port/adapter pair in this codebase is split this way -- a unit
test for `login()`'s own business logic (wrong password → rejected,
no session row created, etc., `tests/e2e/test_auth_handler.py`) can
run against the REAL `SqlAlchemyLocal*Repository` adapters (this
codebase's own established preference over hand-rolled fakes, see
`packages/application/human_decision_handler.py`'s own precedent) —
the Protocol boundary exists so a *different* concrete adapter could
be substituted later (e.g. a Redis-backed session store) without
touching a single line of `auth_handler.py`'s own logic, exactly the
same substitutability `security.identity.IdentityPort` already gives
`packages/test_support/identity.py`'s test double vs. a real future
OIDC adapter.

## AUTHENTICATION / IDENTITY RESOLUTION CONTRACT

`packages/application/auth_handler.py::login` verifies `email`/
`password` against a real, persisted `local_auth_credentials` row
(PBKDF2-HMAC-SHA256, 600,000 iterations, random per-row salt,
`packages/security/local_auth.py`) and, only on success, issues a real
`local_auth_sessions` row: a 256-bit random token, hashed (SHA-256)
before storage — the raw token is set as an `HttpOnly` cookie and never
appears in any JSON response body or is stored anywhere raw.
`resolve_session` verifies the cookie against that table on every
request (checking hash match, `revoked_at IS NULL`, `expires_at >
now()`) and resolves to a real `security.identity.AuthenticatedPrincipal`
— the exact same type PKG-01 already defined, unchanged. A session
resolved this way is ALWAYS `authority.actor.ActorClass.HUMAN_USER` —
a real password login structurally cannot authenticate as
`SYSTEM_SERVICE`/`AI_PROCESSOR`/`EXTERNAL_SYSTEM`.

The former `x-nquiry-actor-user-id`/`x-nquiry-actor-class` headers are
now fully inert on both production routes — supplying them, with or
without a valid session present, has zero effect (proven by
`tests/e2e/test_http_auth.py::
test_session_view_denies_a_foreign_user_id_header_when_no_session_is_present`
and `::test_session_view_ignores_a_forged_actor_class_header_when_a_real_session_is_present`).

## COMMAND / QUERY DISPATCH CONTRACT (UNCHANGED)

`dispatch_get_session_view`/`dispatch_record_human_decision` are
otherwise byte-for-byte unchanged from Architecture 17: the same
BND-001/002/003 read chain, the same BND-001..007/014 write chain, the
same `record_human_decision`/`get_session_view` handlers, the same
`CommitCoordinator`. Only WHO the resolved `ActorIdentity` names
changed (a verified session's real UserId instead of a trusted header
value) — WHAT happens once identity is resolved is identical.

## AUTHORITY PRESERVATION

Unchanged. `AuthorityResolver` is still invoked fresh, per request,
inside the same application handlers; this field resolves identity
only, never authority — `AuthenticatedPrincipal` still structurally
cannot carry a role/permission field (PKG-01's own non-collapse
proof, re-verified unchanged: `tests/security/test_identity.py`).

## SECURITY BOUNDARIES

- Password storage: PBKDF2-HMAC-SHA256, 600,000 iterations (OWASP 2023
  minimum), random 16-byte salt per credential — two hashes of the
  same password are never equal (proven,
  `tests/security/test_local_auth.py`).
- Session storage: only a SHA-256 hash of the raw token is persisted —
  a database read alone can never reconstruct a usable session.
- No user enumeration: an unknown email and a wrong password for a
  real account raise the identical exception with the identical
  message (`application.auth_handler.InvalidCredentials`); a
  constant-effort PBKDF2 decoy runs even for an unknown email, so wall-
  clock timing does not disclose account existence either
  (`tests/e2e/test_auth_handler.py::
  test_login_rejects_an_unknown_email_with_the_identical_exception_as_a_wrong_password`).
- Cookie flags: `HttpOnly` (client-side JavaScript can never read the
  token), `SameSite=Lax`, `Secure` off by default (this prototype's
  real running frontend is plain `http://localhost:3000` — a `Secure`
  cookie is never sent over plain HTTP at all; a real HTTPS deployment
  must set `NQUIRY_COOKIE_SECURE=1`, disclosed `[IMPLEMENTATION CHOICE]`,
  same class of honestly-scoped limitation as GAP-14-002).
- CORS: `Access-Control-Allow-Credentials: true` with the origin
  pinned to exactly `http://localhost:3000` (never a wildcard — the
  CORS spec itself forbids combining a wildcard origin with
  credentials).
- DB-principal capability mapping (PKG-25/26's `SECURITY_CAPABILITY_MAP`)
  is deliberately NOT extended to the two new tables — disclosed,
  consistent limitation; see migration `05794035ef3c`'s own docstring.

## HARD-DEP-001 RELATION

**Unchanged, still BLOCKED — deliberately, explicitly not touched by
this field.** This is the one boundary this field's own authorization
named explicitly: closing GAP-14-001's transport weakness (a real
login mechanism) is NOT the same thing as closing HARD-DEP-001
(legitimate first Workspace governance-root bootstrap), and this field
does not conflate the two. Every session this field lets a human
establish still resolves to a `UserId` whose own Workspace membership/
authority was seeded via `NonProofWorkspaceBootstrap`
(`FIXTURE_LEGITIMACY == "NON_PROOF_FIXTURE"`) — logging in proves WHO
is calling, in a real, cryptographically-verified way; it proves
NOTHING about whether that user's own governance root was ever
legitimately established. That question remains reserved to
Architecture 19/22, exactly as scoped before this field began. No
bootstrap-ordering question was reached during this field's own
construction that required escalation — see HUMAN_DECISION_REQUIRED
REGISTER below for why.

## HARD-DEP-002 RELATION

Unchanged, still BLOCKED and untouched — no AI/provider file is
touched anywhere in this field.

## DEFERRED CAPABILITIES

Real external OIDC/IdP integration (GAP-14-001 itself); self-service
registration/password reset; multi-factor authentication; a
Workspace-list/dashboard UI or Query; password rotation/complexity
policy beyond "non-empty"; any DB-principal scoping for the two new
tables (see SECURITY BOUNDARIES above).

## FORBIDDEN COLLAPSES

None introduced. Explicitly re-verified: no session claim became
authority (`AuthorityResolver` still runs fresh, unchanged); no header
of any kind is trusted anymore on either production route (proven
adversarially); no credential/session table is treated as a governance
record (`local_auth_credentials`/`local_auth_sessions` carry no
Workspace/authority-shaped field at all); HARD-DEP-001 was not
silently narrowed or reinterpreted to appear closed.

## TDD OBLIGATIONS / ADVERSARIAL TEST MATRIX / RUNTIME PROOF REQUIREMENTS

See `docs/implementation/proof-reports/LOCAL-AUTH-ADAPTER.md` for the
full TDD sequence, the complete adversarial test list (forged/
tampered/expired/revoked session, foreign-header-ignored, no-user-
enumeration, timing-parity), and the real Docker-container + real
browser runtime proof.

## TRACEABILITY TO EXISTING BND / PKG / P / TEST IDENTIFIERS

Reuses PKG-01's `AuthenticatedPrincipal`/`IdentityPort` unmodified;
reuses Architecture 17's `application.http_dispatch` composition root,
`get_session_view`/`record_human_decision` handlers, and BND-001..007/
014 chains unmodified. `test_support.nonproof_bootstrap.
NonProofWorkspaceBootstrap` reused unmodified for every new test's own
seeding, same PKG-04/14/25/30-era precedent. No new BoundaryId, no new
AuthorityClass, no new ActorClass.

## FIELD EXIT CONDITIONS

See implementation report FIELD EXIT VERDICT
(`docs/implementation/proof-reports/LOCAL-AUTH-ADAPTER.md`).

## HUMAN_DECISION_REQUIRED REGISTER

None encountered that blocked this field. The one item this field was
explicitly instructed to watch for — the bootstrap-authority question
("who gets Workspace governance authority at the very first start")
being touched while building login — was NOT reached: this field's own
scope (verify a password, issue/verify a session, resolve identity)
never required deciding who owns a Workspace, only who is calling.
Two items remain explicitly named, unchanged from every predecessor
document:

- **Real production authentication provider selection (GAP-14-001)**
  — question: "which concrete OIDC/IdP does NQUIRY's production
  deployment use, and what does token→UserId mapping look like for
  it?" Not resolved, not required for this field's own scope.
- **Legitimate first Workspace governance-root bootstrap
  (HARD-DEP-001)** — question: "who may legitimately become a
  Workspace's first governance authority, and by what provable
  mechanism?" Explicitly reserved to Architecture 19/22; this field
  neither answers it nor narrows it.
