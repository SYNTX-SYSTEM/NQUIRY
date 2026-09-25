# 24 NQIRY IDENTITY & AUTHENTICATION FIELD ARCHITECTURE

## 0. Document Identity

DOCUMENT: `24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`

FIELD: NQIRY Identity & Authentication Field

MODE: Online repository reconstruction, systemic Field reconstruction, recursive Deep Sweep, inverse Deep Sweep, threat-model reconstruction, protocol validation, transaction state-machine validation, concurrency validation, failure-path validation, authentication-to-authorization boundary architecture, consolidated root repair, surgical two-defect repair, implementation-ready semantic Field synthesis.

REPOSITORY: `SYNTX-SYSTEM/NQUIRY`

REFERENCE BASELINE: Published F03 reference commit `c9d86bab64505845f406ba43a8c78ac185383680`, as specified by the source instruction.

SOURCE BASIS: Surgical two-defect repair instruction for `24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`. 

PRIMARY SCOPE:

* canonical user identity
* authentication methods
* local password authentication
* local password login-CSRF boundary
* email verification
* OIDC login start
* OIDC authorization transaction
* initiating user-agent binding
* state
* nonce
* PKCE
* authorization code
* token exchange
* ID Token trust
* provider subject
* provider email attribute
* account creation policy
* account linking
* session creation
* session rotation
* session revocation
* account recovery
* authentication-method revocation
* authentication-to-authorization boundary
* browser security
* CSRF
* CORS
* redirect handling
* provider failure
* user cancel
* runtime DB-principal capability boundary
* concurrency
* persistence
* API
* frontend projection
* runtime configuration
* audit
* provenance
* real provider proof
* tests
* review evidence
* reconstruction

OUTPUT STATUS: Architecture file only. No implementation performed.

ARCHITECTURE STATUS: IMPLEMENTATION_READY_WITH_HUMAN_AUTHORITY_BOUNDARIES

This document is repository-grounded against the public GitHub repository and repository-accessible raw files referenced by the current architecture reconstruction. The repository itself remains the evidence authority for current code. If a branch, private artifact, unpublished local change, hidden CI artifact or historical implementation is not publicly accessible, this document marks the relation UNKNOWN rather than inventing its content.

This document treats Identity & Authentication as one complete Field. It does not patch isolated OIDC prose. It reconstructs the complete causal architecture from human/browser intent through authentication request, protocol state, identity proof, canonical identity, local session, authorization boundary and visible effect, then reconstructs each visible effect backward to its authoritative root.

This final version repairs and preserves:

* repository reconstruction
* authentication-to-authorization separation
* canonical `UserId` model
* server-side opaque session model
* local password adapter boundary
* local password login-CSRF boundary
* Google OIDC direction
* OIDC Authorization Code Flow with PKCE
* OIDC transaction state machine
* initiating user-agent binding
* PKCE confidential verifier handling
* ID Token trust ordering
* provider error and cancel terminal paths
* redirect target validation
* login/session swapping threat boundary
* account linking law
* recovery architecture
* revocation architecture
* provider abstraction
* browser security boundaries
* CSRF/CORS distinction
* protocol callback GET distinction
* runtime DB-principal capability boundary
* Work Unit structure
* falsifier coverage
* proof requirements
* System Field Engineering laws

## 1. Architecture Thesis

NQUIRY currently has a real local email/password authentication adapter with real server-side session persistence, a real `HttpOnly` browser cookie and real replacement of the previously disclosed header-trust weakness. It does not currently have a production external identity provider, self-service registration, password reset, account linking, email verification or a complete identity-method model.

The current authentication Field already preserves the most important semantic boundary:

AUTHENTICATION != AUTHORIZATION

The current local adapter resolves WHO is calling. It does not decide WHICH Workspace the caller may govern, what role the caller holds, what authority the caller has or what capability the caller may execute. The upstream `AuthenticatedPrincipal` type structurally carries user identity, session reference, authentication time and issuer reference, but no role or permission field.

The target architecture must preserve that separation while extending authentication from a local prototype adapter into a complete identity/authentication Field:

HUMAN / BROWSER INTENT
→ AUTHENTICATION REQUEST
→ PROTOCOL STATE
→ IDENTITY PROOF
→ CANONICAL NQUIRY IDENTITY
→ LOCAL SESSION
→ AUTHORIZATION BOUNDARY
→ VISIBLE EFFECT

The architecture must also remain reconstructable backward:

VISIBLE EFFECT
→ LOCAL COMMIT
→ AUTHORITY
→ VALIDATION
→ STATE
→ PRODUCER
→ ROOT

The architecture must not collapse:

* authentication into authorization
* email into identity
* email equality into identity equivalence
* external provider subject into canonical NQUIRY identity
* authentication method into recovery proof
* OIDC transaction into provider identity
* authorization code into authenticated identity
* token response into trusted identity
* parsed ID Token into validated ID Token
* nonce expectation into nonce validation
* PKCE verifier into PKCE verifier hash
* provider callback into local commit
* provider proof into local commit
* local password login request into login effect
* valid password into permission for unrelated browser session swapping
* identity creation into membership
* membership into role
* role into authority
* session into authorization
* login into account creation
* account link into email equality
* LOGIN transaction into ACCOUNT_LINK transaction
* PENDING into PROCESSING
* PROCESSING into COMPLETED
* retry into recovery
* application CSRF proof into OIDC state
* OIDC state into application CSRF proof
* application authenticated-CSRF boundary into local login-CSRF boundary
* local password login CSRF into OIDC callback CSRF / login-swapping proof
* safe application GET into business mutation
* protocol callback GET into general GET mutation authority
* request into commit
* candidate into effect
* bootstrap/test database authority into production runtime authority

NQUIRY should move toward a provider-agnostic authentication method architecture with Google OIDC as the first production-capable external identity provider, while preserving the existing local password adapter as a bounded local/prototype or explicitly approved product credential method.

OpenID Connect Authorization Code Flow with PKCE is the selected external-provider flow. In this flow:

1. Login start creates local transaction state before provider redirect.
2. The browser callback returns an authorization code and state.
3. The ID Token is not available before the authorization code is exchanged at the Token Endpoint.
4. The original PKCE `code_verifier` is required during the token request.
5. The Token Endpoint response contains the ID Token.
6. The nonce claim is inside the ID Token.
7. Nonce claim validation cannot occur before token exchange.
8. ID Token cryptographic and semantic validation must precede trusted claim use.
9. An OAuth authorization code is single-use.
10. NQUIRY must enforce its own callback single-processing and must not depend on the provider to resolve callback races.

The target Google OIDC callback order is:

OIDC CALLBACK CANDIDATE
→ TRANSACTION LOOKUP
→ VERIFY TRANSACTION EXISTS
→ VERIFY TRANSACTION STATE IS PENDING
→ VERIFY INITIATING USER-AGENT BINDING
→ VALIDATE RETURNED STATE AGAINST TRANSACTION
→ VALIDATE TRANSACTION EXPIRY
→ VALIDATE TRANSACTION PURPOSE
→ VALIDATE INITIATING USER ID WHEN ACCOUNT_LINK
→ ATOMICALLY CLAIM TRANSACTION FOR PROCESSING
→ CONFIDENTIALLY RETRIEVE TRANSACTION-BOUND PKCE `code_verifier`
→ TOKEN EXCHANGE USING AUTHORIZATION CODE + ORIGINAL `code_verifier`
→ RECEIVE TOKEN RESPONSE
→ VALIDATE ID TOKEN SIGNATURE
→ VALIDATE ISSUER
→ VALIDATE AUDIENCE
→ VALIDATE EXPIRATION
→ VALIDATE OTHER REQUIRED OIDC TOKEN CONDITIONS
→ VALIDATE NONCE CLAIM AGAINST TRANSACTION NONCE
→ EXTRACT TRUSTED PROVIDER SUBJECT
→ EXTRACT EMAIL ONLY AS PROVIDER ATTRIBUTE
→ RESOLVE PROVIDER IDENTITY OR ACCOUNT CREATION BOUNDARY
→ EXECUTE LEGITIMATE LOCAL EFFECT GATE
→ FINALIZE OIDC TRANSACTION TERMINAL STATE
→ MAKE PKCE VERIFIER UNAVAILABLE / UNUSABLE
→ RE-READ LOCAL AUTHENTICATION STATE
→ RECONSTRUCT VISIBLE AUTHENTICATED FIELD

This is semantic protocol order, not mandatory implementation pseudocode. A standards-compliant maintained OIDC library may implement protocol mechanics. It may not replace the architectural relations.

The local password login effect order is:

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH LOCAL SESSION COMMIT

The local password login-CSRF boundary is distinct from both OIDC callback continuation proof and application CSRF for already cookie-authenticated unsafe requests.

The architecture must explicitly close the first Google login boundary:

VALID GOOGLE PROVIDER PROOF
→ LOOKUP `provider_issuer + provider_subject`

IF EXISTING BINDING:
→ resolve existing canonical `UserId`
→ continue toward local session commit

IF NO EXISTING BINDING:
→ evaluate ACCOUNT CREATION POLICY

ACCOUNT CREATION POLICY may resolve to:

* SELF_REGISTRATION_ALLOWED
* INVITATION_REQUIRED
* PRE_PROVISIONED_IDENTITY_REQUIRED
* GOVERNANCE_MEDIATED_CREATION
* DENIED / UNAVAILABLE

The exact product policy remains HUMAN_AUTHORITY_REQUIRED.

Until such policy is explicitly established, unknown provider subject must fail closed and must not create a canonical user by implementation convenience.

The architecture must preserve HTTP method semantics:

ORDINARY SAFE APPLICATION REQUESTS
MUST NOT ACQUIRE BUSINESS MUTATION SEMANTICS.

PROTOCOL CALLBACKS MAY MATERIALIZE ONLY THEIR
PROTOCOL-DEFINED SECURITY / IDENTITY EFFECTS
THROUGH THEIR DEDICATED PROOF AND EFFECT GATES.

An OIDC callback route may use GET as a protocol response contact. That does not mean arbitrary GET routes may mutate application state. The callback gains no effect merely because the route is reached.

## 2. Repository Evidence Basis

### 2.1 Public Repository Evidence

The public repository identifies itself as N.Q.U.I.R.Y., an inquiry system whose architecture defines what may exist and whose code materializes that architecture. The README states that all originally scoped packages are complete and that two further fields extended the base: Architecture 17 and a Local Authentication Adapter. It explicitly says the Local Authentication Adapter provides “a real, local email/password login with a genuine server-verified session,” closing the earlier GAP-14-001 header-trust weakness but not production provider selection.

The public repository topology includes `apps`, `packages`, `migrations`, `tests`, `docs`, `infra` and scripts; the reference stack is Python 3.13, FastAPI, PostgreSQL 17, Alembic, SQLAlchemy Core, Next.js 16, pytest, Vitest, Playwright, Docker Compose and GitHub Actions.

### 2.2 Runtime Operation Evidence

`docs/RUNTIME_OPERATION.md` describes the current local runtime as a real login flow:

1. human submits email/password on `/login`
2. server checks password against a securely hashed database credential
3. server creates a database session row
4. browser receives an opaque random token in an `HttpOnly` cookie
5. every later request validates that token against the database
6. logout revokes/deletes the effective session relation
7. the old `?as=<user-id>` trust shortcut no longer works for the real routes

The same runtime document states that the current runtime exposes `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`, `GET /workspaces/{workspaceId}/sessions/{sessionId}` and `POST /decisions/{decisionId}/decide`, and that identity now comes from the real `HttpOnly` `nquiry_session` cookie rather than the former `?as=` parameter or `x-nquiry-actor-*` headers.

The runtime document also states what is not materialized:

* no production authentication provider
* no Challenge/Session creation UI
* no Workspace-list/dashboard UI
* no self-service account creation/password reset
* no readiness endpoint distinct from liveness

### 2.3 Architecture 18 Evidence

`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md` states that the local authentication adapter is materialized and proven against real PostgreSQL, a real running container and a real browser, but remains an architectural prototype and is not production-approved.

Architecture 18 defines the current scope:

* real password credential storage and verification through `local_auth_credentials`
* real server-verified HTTP sessions through `local_auth_sessions`
* `HttpOnly` cookie
* `POST /auth/login`
* `POST /auth/logout`
* `GET /auth/me`
* replacement of the two Architecture 17 routes’ header trust with session resolution
* no production OIDC provider
* no self-service registration/password reset
* no Workspace-list/dashboard UI
* no change to boundary, authority or commit semantics

Architecture 18 also classifies production OIDC as still open and legitimate first Workspace governance-root bootstrap as still blocked.

### 2.4 Code Evidence

`packages/security/local_auth.py` defines the local deterministic credential/session adapter. It explicitly states that it is the deterministic test adapter half of the upstream authorized pair, hardened into a real local browser login, and that it does not talk to an external identity provider. It defines PBKDF2 password hashing, 256-bit random session tokens and SHA-256 session-token hashing.

`packages/application/auth_handler.py` defines login, session resolution and logout, with a 12-hour session lifetime, normalized email/password input at the login boundary, constant-effort dummy hash for unknown emails and fail-closed session resolution for missing, forged, revoked or expired tokens.

`apps/api/src/nquiry_api/http/auth.py` is a thin FastAPI adapter for `/auth/login`, `/auth/logout` and `/auth/me`. It sets the `nquiry_session` cookie as `HttpOnly`, `SameSite=Lax`, path `/`, and `Secure` only when `NQUIRY_COOKIE_SECURE=1`.

`migrations/versions/05794035ef3c_local_auth.py` adds `local_auth_credentials` and `local_auth_sessions`, separates credential material from `users`, stores only hashed session tokens, and explicitly excludes external provider integration from this migration.

`packages/persistence/local_auth_repository.py` implements SQLAlchemy repositories for the credential and session ports, joining `local_auth_credentials` to `users` for email lookup because credentials do not own the email attribute.

`apps/web/lib/api/authClient.ts` performs real `fetch` calls to `/auth/login`, `/auth/logout` and `/auth/me` with `credentials: "include"` and makes no client-side authority decision.

`apps/web/app/login/page.tsx` is a real email/password form, calls the real login route, redirects only after server success and shows server-denied/error states without client-side authority claims.

### 2.5 Proof Evidence

The Local Auth Adapter proof report lists created files, modified files, test surfaces and adversarial proofs. It states that new files include the migration, security local auth module, persistence repository, application auth handler, API auth router, web auth client, login page, logout button, seed script and tests.

The proof report records static gates, frontend gates and browser proof: pytest, ruff, mypy, architecture dependency checks, provider SDK import checks, test-only import checks, ESLint, TypeScript, Vitest, Playwright and Next build.

The proof report records adversarial tests: no cookie, forged cookie, tampered cookie, expired session, revoked session, forged actor headers, second user without membership, wrong password/unknown email parity, empty password rejection, per-session logout isolation, duplicate decision denial and no raw session token in login response body.

## 3. Complete Field Reconstruction

### 3.1 Field Causal Graph

The Identity & Authentication Field resolves candidate human/browser intent into server-validated local session state without granting business authority.

Canonical forward graph:

HUMAN / BROWSER INTENT
→ AUTHENTICATION REQUEST
→ REQUEST CANDIDATE
→ PROTOCOL OR CREDENTIAL STATE
→ VALIDATION
→ AUTHORITY
→ LOCAL EFFECT GATE
→ CANONICAL IDENTITY
→ AUTHENTICATED SESSION
→ SERVER-SIDE SESSION RECONSTRUCTION
→ AUTHORIZATION BOUNDARY
→ VISIBLE FIELD STATE

Canonical inverse graph:

VISIBLE FIELD STATE
→ SERVER-READ LOCAL STATE
→ COMMITTED SESSION / METHOD / IDENTITY RELATION
→ VALIDATED AUTHENTICATION PROOF
→ PROTOCOL OR CREDENTIAL PRODUCER
→ INITIATING USER / USER-AGENT CONTEXT
→ ROOT REQUEST

No visible authenticated state may terminate in frontend state, email equality, provider callback reachability, unclaimed OIDC transaction, authorization code receipt, token response bytes, parsed unvalidated token, mock provider, unpersisted convention, implicit product policy, over-broad runtime DB principal or unproven local login request boundary.

### 3.2 Current Field

FIELD: Local Authentication Adapter Field

STATE: Materialized local/prototype authentication with server-side sessions.

AUTHORITATIVE CURRENT MECHANISM:

* local email/password credential lookup
* password verification against persisted PBKDF2 hash
* local session issuance
* raw opaque token delivered only as cookie
* hashed token persisted in `local_auth_sessions`
* request identity resolved from cookie/session row
* application routes use resolved identity
* authority is still evaluated downstream by existing authorization code

CLASSIFICATION: PRODUCTION-ADJACENT LOCAL PROTOTYPE / DEVELOPMENT-CAPABLE / NOT PRODUCTION PROVIDER APPROVED.

The current field is more than a mock. It is a real browser-usable local authentication path. It is not a production identity provider integration and does not close the production authentication provider gap.

### 3.3 Current Local Email/Password Mechanism

INPUT: email + password submitted to `/auth/login`.

IDENTITY CLAIM: “The caller controls the local credential associated with this email.”

CREDENTIAL OR PROOF: password compared against stored PBKDF2-HMAC-SHA256 hash.

VALIDATOR: `application.auth_handler.login`.

AUTHORITATIVE SOURCE: `users.email` joined to `local_auth_credentials.password_hash`.

APPLICATION SERVICE: `packages/application/auth_handler.py::login`.

PERSISTENCE: `local_auth_credentials`, `local_auth_sessions`.

LOGIN-CSRF BOUNDARY: explicit architecture boundary required before credential validation may produce a fresh authenticated session.

SESSION EFFECT: creates a fresh `local_auth_sessions` row.

COOKIE EFFECT: API sets/replaces `nquiry_session` cookie with raw opaque token.

EXPIRATION: 12 hours from issue time.

REVOCATION: logout sets session revoked state through repository update.

FAILURE BEHAVIOR: invalid credentials produce denied response; unknown email and wrong password collapse to same failure shape.

FRONTEND CONTACT: `/login` page and `authClient.ts`.

API CONTACT: `POST /auth/login`.

SECURITY BOUNDARY: password hash cannot be reversed from DB; raw session token cannot be reconstructed from DB; cookie is `HttpOnly`; client-side code never receives token in JSON; hostile cross-site login submission must not create authenticated session into attacker-selected account.

PROOF / EVIDENCE: repository code and proof report for local auth; login-CSRF boundary proof required by this architecture before the local login request contract can be considered complete.

CLASSIFICATION: MATERIALIZED LOCAL AUTHENTICATION ADAPTER; NOT PRODUCTION IDP.

### 3.4 Current Session Mechanism

INPUT: cookie `nquiry_session`.

IDENTITY CLAIM: browser presents opaque session token.

VALIDATOR: `application.auth_handler.resolve_session`.

AUTHORITATIVE SOURCE: `local_auth_sessions` row matching SHA-256 token hash, not revoked, not expired.

APPLICATION SERVICE: `resolve_session`.

PERSISTENCE: `local_auth_sessions`.

COOKIE OR TOKEN EFFECT: raw cookie value is never stored raw, only hashed.

EXPIRATION: `SESSION_LIFETIME = timedelta(hours=12)`.

REVOCATION: `logout` marks the session token hash revoked; missing or unknown token is a no-op.

FAILURE BEHAVIOR: no token, unknown token, forged token, revoked token and expired token all resolve to no principal.

SECURITY BOUNDARY: session does not carry role, permission or authority.

CLASSIFICATION: MATERIALIZED SERVER-SIDE SESSION.

### 3.5 Current Authentication to Application Boundary

`application.http_dispatch` is the composition root that converts HTTP-facing requests into application calls. It removed the old header-trust path and now resolves identity only from a real server-verified session. Supplying `x-nquiry-actor-user-id` or `x-nquiry-actor-class` has structurally zero effect on the real browser-facing routes.

The dispatch layer converts a resolved `AuthenticatedPrincipal` into `ActorIdentity(ActorClass.HUMAN_USER, user_id)` for routes that expect actor identity.

### 3.6 Current External Provider State

No production external OIDC/IdP integration exists.

GAP-14-001 remains open.

### 3.7 Current Registration, Verification, Recovery and Linking State

Current public evidence supports:

* no self-service registration
* no password reset
* no account recovery route
* no email verification route
* no account linking
* no external provider identity persistence
* no provider subject mapping table
* no OIDC auth transaction relation
* no OIDC transaction state machine
* no initiating user-agent binding relation
* no confidential PKCE verifier binding
* no redirect target validation relation
* no provider error/cancel terminal path
* no provider token storage
* no explicit all-session logout
* no credential rotation UI/API

The runtime document explicitly states no self-service account creation/password reset and that accounts are created only by the seed script or direct DB insert.

## 4. Current Identity Model

### 4.1 Canonical Identity Key

The current canonical human identity key is `users.id`, represented in code as `semantic_types.ids.UserId` and surfaced through `security.identity.AuthenticatedPrincipal.user_id`.

The local credential table references `users.id`.

The session table also references `users.id`.

### 4.2 Identity vs Credential

The repository deliberately separates identity from credentials:

* `users` is the canonical identity table.
* `local_auth_credentials` stores password hash material separately.
* mixing authentication-secret material into `users` would blur IDENTITY != CREDENTIAL.

### 4.3 Email Address Status

Current evidence shows email exists on `users`, and `local_auth_credentials` does not carry its own email column; the local credential repository joins to `users` for email lookup.

CURRENT CLASSIFICATION:

* email is currently used as login lookup attribute
* email is not stored as password credential secret material
* email is not yet modeled as a verified proof relation
* email is not sufficient to prove identity equivalence across methods
* email-change semantics are not materialized
* multiple authentication methods per user are not materialized

### 4.4 Multiple Authentication Methods

Current persistence supports one local password credential per user because `local_auth_credentials.user_id` is unique.

It does not yet support:

* multiple authentication methods
* external provider links
* explicit auth-method records
* OIDC transaction records
* OIDC transaction state machine
* initiating user-agent binding records
* confidential PKCE verifier binding
* account creation policy execution records

### 4.5 Identity Continuity

Current identity continuity comes from `users.id`.

Current authentication continuity comes from:

* persisted local credential row
* persisted session rows
* session issuer reference `nquiry-local-credential-adapter`

What is missing:

* provider subject continuity
* auth-method continuity
* email verification continuity
* recovery continuity
* explicit identity-link provenance
* explicit first-provider-login account creation policy
* explicit OIDC transaction continuity
* explicit OIDC transaction exclusive-claim lifecycle
* explicit initiating user-agent continuation relation
* explicit PKCE verifier lifecycle
* explicit token-validation trust boundary
* explicit local password login-CSRF boundary proof

## 5. Current Session Model

### 5.1 Current Session Type

NQUIRY currently uses server-side sessions backed by database rows in `local_auth_sessions`, not stateless JWT sessions.

### 5.2 Token Model

* token is generated as high-entropy random session token
* raw token is set in the cookie
* SHA-256 hash is stored in DB
* lookup computes token hash and compares against DB
* DB read alone cannot reconstruct usable session

### 5.3 Cookie Model

Cookie name: `nquiry_session`

Flags:

* `HttpOnly`
* `SameSite=Lax`
* `Secure` only when `NQUIRY_COOKIE_SECURE=1`
* path `/`

The `Secure` flag defaults off because current local runtime uses plain `http://localhost:3000`; real HTTPS deployment must set `NQUIRY_COOKIE_SECURE=1`.

### 5.4 Lifetime

Current session lifetime is 12 hours.

No current evidence supports:

* idle lifetime
* refresh-token rotation
* sliding expiration
* session-device metadata
* all-session revocation
* credential-change revokes all sessions
* provider-unlink revokes dependent sessions

### 5.5 Logout

Current logout revokes the session named by the cookie and clears the cookie in the HTTP adapter.

Missing/unknown/already revoked logout is a no-op.

### 5.6 Concurrent Sessions

Concurrent sessions are currently allowed.

Logging out one session does not invalidate a second independently issued session for the same user.

## 6. Authentication to Authorization Boundary

### 6.1 Boundary Definition

Authentication ends when NQUIRY has resolved an `AuthenticatedPrincipal` or an `ActorIdentity` for a request.

Authorization begins when NQUIRY evaluates membership, role, governance root, authority binding, capability and command boundary for the resolved identity.

### 6.2 Current Preservation

The current implementation preserves:

IDENTITY != AUTHORITY

`AuthenticatedPrincipal` has no role/permission field by construction.

The Local Authentication Adapter field resolves identity only, never authority.

### 6.3 Workspace Membership Boundary

A logged-in user without membership does not become authorized.

Authenticated but unauthorized must remain distinct from unauthenticated.

### 6.4 Governance Root Boundary

Legitimate first Workspace governance-root bootstrap remains open and blocked.

Authentication proves who is calling.

It does not prove that the user’s governance root was legitimately established.

Identity creation, if later approved, must not close Workspace governance bootstrap.

## 7. First Broken Relations

### FBR-AUTH-001: Production Identity Provider Gap

SYMPTOM: Repository has real local email/password login but no production external provider.

CONSUMER: NQUIRY runtime, browser login, future product identity.

BROKEN RELATION: external identity proof → canonical NQUIRY identity.

PRODUCER: no concrete OIDC provider adapter currently materialized.

AUTHORITY: unresolved human/product/provider decision plus technical provider integration.

STATE: GAP-14-001 remains open.

FIRST BROKEN RELATION: Production authentication provider selection and mapping to canonical `UserId` are undefined.

AUTHORITATIVE HOME: Authentication Provider Architecture / Identity Method Persistence / Human Authority Boundary.

ROOT REPAIR: Introduce provider-agnostic authentication-method architecture and implement Google OIDC as first production-capable provider only after human/provider configuration authority exists.

DEPENDENCY PROPAGATION:

* provider identity table
* auth method model
* OIDC transaction field
* OIDC transaction state machine
* initiating user-agent binding
* confidential PKCE verifier binding
* account creation boundary
* account linking
* collision handling
* recovery
* provider tests
* frontend login contact

FALSIFIER: production login relies on local prototype credential or mock provider while claiming production provider proof.

TEST: production-mode provider configuration rejects missing real provider and rejects mock/test provider.

EVIDENCE: real provider proof bundle.

### FBR-AUTH-002: Identity Method Model Missing

SYMPTOM: Local credentials and local sessions exist, but there is no generalized `authentication_methods` relation.

CONSUMER: future Google OIDC, Microsoft/GitHub provider support, account linking, revocation, recovery.

BROKEN RELATION: canonical NQUIRY identity ↔ authentication method.

PRODUCER: current persistence has `local_auth_credentials` only.

AUTHORITY: identity architecture.

STATE: partial.

FIRST BROKEN RELATION: Credential is persisted as a local adapter-specific relation, not as one member of a typed identity-method set.

AUTHORITATIVE HOME: Canonical Identity Model / Persistence Architecture.

ROOT REPAIR: Add explicit auth-method model while preserving current local credential table through migration compatibility or migration into a generalized method relation.

FALSIFIER: recovery challenge or OIDC transaction appears as a persistent authentication method.

TEST: method list excludes recovery challenges and OIDC transactions.

EVIDENCE: auth-method persistence proof.

### FBR-AUTH-003: Email Address Used for Login but Not Proof

SYMPTOM: `users.email` is used as credential lookup key, but email verification state is not materialized.

CONSUMER: password login, recovery, linking, future provider collision handling.

BROKEN RELATION: email address → verified email proof → identity relation.

PRODUCER: no `verified_emails` / verification challenge table currently materialized.

AUTHORITY: verification architecture.

STATE: unsafe if treated as identity proof beyond current local seeded credential context.

FIRST BROKEN RELATION: Email is an attribute and lookup key but not a verified proof relation.

AUTHORITATIVE HOME: Verification Architecture.

ROOT REPAIR: Add explicit email verification relation before using email for linking, recovery, password reset or identity equivalence.

FALSIFIER: same email silently links local and provider identity.

TEST: same-email different-provider-subject collision fails closed.

EVIDENCE: email collision proof.

### FBR-AUTH-004: Recovery Undefined

SYMPTOM: No self-service password reset or account recovery exists.

CONSUMER: password auth, provider loss, account linking, support operations.

BROKEN RELATION: loss of auth method → recovery proof → restored authentication method or authenticated access.

PRODUCER: no recovery challenge for authentication recovery.

AUTHORITY: recovery architecture and human policy.

STATE: missing.

FIRST BROKEN RELATION: No proof-bearing recovery path exists for restoring authentication.

AUTHORITATIVE HOME: Recovery Architecture.

ROOT REPAIR: Define recovery challenge persistence, proof gates and human authority boundaries.

CORRECTION: A recovery challenge is not an authentication method. It is a temporary proof-bearing recovery relation used to authorize restoration, replacement or establishment of an authentication method or authenticated access.

FALSIFIER: password reset succeeds by email string alone.

TEST: attacker knowing email cannot reset credential.

EVIDENCE: recovery proof tests.

### FBR-AUTH-005: Auth Session Revocation Scope Too Narrow

SYMPTOM: Current logout revokes one session; no all-session logout, credential-change revocation or provider-unlink propagation is materialized.

CONSUMER: security response, credential compromise, provider unlink, account disable.

BROKEN RELATION: revoked auth method/session → downstream session invalidation.

PRODUCER: session table supports `revoked_at` per session but no broader revocation relation.

AUTHORITY: revocation architecture.

STATE: partial.

FIRST BROKEN RELATION: Revocation exists at single-session granularity only.

AUTHORITATIVE HOME: Revocation Architecture / Session Architecture.

ROOT REPAIR: Add explicit revocation scopes: single session, all sessions, method-specific sessions, account disable.

FALSIFIER: revoked provider method continues producing sessions.

TEST: provider method disable denies new login and invalidates dependent sessions where policy requires.

EVIDENCE: revocation propagation proof.

### FBR-AUTH-006: DB Principal Boundary Not Extended to Auth Tables

SYMPTOM: Migration explicitly does not extend the DB-principal capability map to local auth tables and notes the live HTTP path still connects through the existing bootstrap connection pattern.

CONSUMER: security hardening, production readiness, live authentication persistence.

BROKEN RELATION: runtime service identity → auth persistence capability.

PRODUCER: no scoped DB principal for auth tables yet.

AUTHORITY: security architecture.

STATE: known disclosed limitation.

FIRST BROKEN RELATION: Authentication persistence writes are not yet governed by runtime DB-principal separation.

AUTHORITATIVE HOME: Security Architecture / Runtime and Configuration Architecture / WU-AUTH-17 Runtime DB Principal Capability Boundary.

ROOT REPAIR: Extend service-principal connection discipline consistently for all live HTTP persistence, including but not only auth tables.

FALSIFIER: runtime DB actor can perform authentication persistence operations outside its intended capability scope.

TEST: DB-principal capability tests after runtime connection discipline is implemented.

EVIDENCE: DB capability proof showing legitimate auth persistence still works and unauthorized DB operations fail.

### FBR-AUTH-007: First Google Login Account Creation Boundary Undefined

SYMPTOM: Architecture knows that Google provider subject maps to canonical `UserId`, but does not fully define what happens when a valid provider subject has no existing binding.

CONSUMER: Google OIDC login, canonical identity creation, login frontend, provider callback handler.

BROKEN RELATION: provider proof → provider subject lookup → identity resolution or account creation policy.

PRODUCER: no account creation policy relation is currently materialized.

AUTHORITY: human product/governance policy.

STATE: missing.

FIRST BROKEN RELATION: Unknown provider subject resolution lacks an explicit account creation boundary.

AUTHORITATIVE HOME: Account Creation Boundary / Human Authority Boundaries / Google OIDC Architecture.

ROOT REPAIR: Add explicit Account Creation Boundary. Unknown provider subject must fail closed until a human-approved policy exists.

FALSIFIER: unknown Google subject creates `UserId` without policy.

TEST: account creation disabled fails closed; approved policy creates identity without authority.

EVIDENCE: first-login proof.

### FBR-AUTH-008: OIDC Auth Transaction Relation Missing

SYMPTOM: Architecture requires state, nonce and PKCE but does not model the temporary transaction binding between OIDC start and callback as its own authoritative relation.

CONSUMER: Google login, account linking, callback validation, replay resistance, purpose binding.

BROKEN RELATION: OIDC start → transaction commit → provider redirect → callback lookup → local validation → atomic transaction claim → verifier retrieval → token exchange → token validation → local effect gate.

PRODUCER: no current OIDC transaction table/service.

AUTHORITY: OIDC Auth Transaction Field.

STATE: missing.

FIRST BROKEN RELATION: OIDC callback validation lacks a persisted or equivalently authoritative transaction relation.

AUTHORITATIVE HOME: OIDC Auth Transaction Field.

ROOT REPAIR: Add single-use, expiring, purpose-bound OIDC auth transaction relation with atomic `PENDING → PROCESSING` claim before verifier retrieval and token exchange.

FALSIFIER: callback creates session without transaction lookup.

TEST: missing transaction callback fails closed.

EVIDENCE: transaction proof.

### FBR-AUTH-009: Explicit Anti-CSRF Boundary Missing

SYMPTOM: Browser cookie authentication exists, but the CSRF architecture boundary was too conditional.

CONSUMER: all unsafe cookie-authenticated ordinary application requests.

BROKEN RELATION: unsafe browser request → anti-CSRF proof → application request.

PRODUCER: no explicit anti-CSRF architecture invariant in current field.

AUTHORITY: Security Architecture.

STATE: underdefined.

FIRST BROKEN RELATION: Cookie-authenticated unsafe application requests lack a mandatory anti-CSRF validation relation.

AUTHORITATIVE HOME: Security Architecture / API Architecture.

ROOT REPAIR: Add invariant: UNSAFE COOKIE-AUTHENTICATED APPLICATION REQUEST → EXPLICIT ANTI-CSRF VALIDATION → APPLICATION REQUEST.

FALSIFIER: hostile origin commits unsafe request with credentials.

TEST: CSRF adversarial browser/API tests.

EVIDENCE: anti-CSRF proof.

### FBR-AUTH-010: PKCE Verifier Confidential Material Boundary Missing

SYMPTOM: A hash alone is insufficient because the original `code_verifier` must be presented during authorization-code token exchange.

CONSUMER: Google OIDC callback, provider token exchange, PKCE validation.

BROKEN RELATION: PKCE verifier generation → confidential server-side binding → code challenge in provider request → callback transaction claim → token exchange uses original verifier → terminal transaction state → verifier unavailable.

PRODUCER: no explicit confidential PKCE verifier lifecycle relation.

AUTHORITY: OIDC Auth Transaction Field / Security Architecture.

STATE: underdefined.

FIRST BROKEN RELATION: PKCE verifier evidence was not distinguished from retrievable confidential PKCE verifier material.

AUTHORITATIVE HOME: OIDC Auth Transaction Field.

ROOT REPAIR: Add PKCE confidential material law.

PKCE VERIFIER CONFIDENTIAL MATERIAL
!=
PKCE VERIFIER HASH / EVIDENCE

FALSIFIER: token exchange cannot retrieve original verifier.

TEST: token exchange receives original verifier and verifier is unavailable after terminal state.

EVIDENCE: PKCE lifecycle proof.

### FBR-AUTH-011: Safe HTTP Method Law vs OIDC Callback Effect

SYMPTOM: Architecture said safe methods must not gain mutation semantics, but OIDC callback may use GET and legitimately cause OIDC transaction processing, provider identity binding, account creation where policy permits, local session creation or link effect.

CONSUMER: API Architecture, Security Architecture, CSRF, HTTP Adapter Law, Google OIDC callback, tests.

BROKEN RELATION: ordinary application safe method semantics vs protocol callback semantics.

PRODUCER: overly absolute method-safety wording.

AUTHORITY: Protocol Callback Semantics Law.

STATE: underdefined.

FIRST BROKEN RELATION: GET application-resource law was not distinguished from GET protocol callback contact.

AUTHORITATIVE HOME: Security Architecture / API Architecture / SFE Laws.

ROOT REPAIR:

ORDINARY SAFE APPLICATION REQUESTS
MUST NOT ACQUIRE BUSINESS MUTATION SEMANTICS.

PROTOCOL CALLBACKS MAY MATERIALIZE ONLY THEIR
PROTOCOL-DEFINED SECURITY / IDENTITY EFFECTS
THROUGH THEIR DEDICATED PROOF AND EFFECT GATES.

FALSIFIER: ordinary GET route mutates business state.

TEST: ordinary GET non-mutation test and callback bounded-effect test.

EVIDENCE: protocol callback proof.

### FBR-AUTH-012: Nonce Validation Order

SYMPTOM: Nonce validation can be accidentally ordered before token exchange and before ID Token validation.

CONSUMER: Google OIDC callback, provider verification, Work Units, tests, inverse trace.

BROKEN RELATION: nonce claim validation → ID Token artifact containing nonce claim.

PRODUCER: protocol-order error.

AUTHORITY: OpenID Connect Authorization Code Flow with PKCE.

STATE: wrong if performed before token exchange and ID Token validation.

FIRST BROKEN RELATION: claim validation is ordered before production and validation of the artifact containing the claim.

AUTHORITATIVE HOME: Google OIDC Architecture / Verification Architecture / Effect Gates.

ROOT REPAIR: token exchange first, then required ID Token validation, then nonce claim validation against transaction-bound expected nonce.

FALSIFIER: nonce is checked before token exchange.

TEST: OIDC protocol-order test.

EVIDENCE: real provider proof and unit protocol proof.

### FBR-AUTH-013: Callback Exclusive Processing

SYMPTOM: Multiple callbacks could reach token exchange before local transaction consumption, relying on provider authorization-code single-use behavior.

CONSUMER: OIDC Auth Transaction Field, concurrency architecture, PKCE verifier access, token exchange, tests.

BROKEN RELATION: transaction ownership → verifier access → external exchange.

PRODUCER: transaction consumption was too late.

AUTHORITY: OIDC transaction state machine.

STATE: wrong if provider exchange begins before exclusive local claim.

FIRST BROKEN RELATION: single-use transaction ownership is established after external effect rather than before it.

AUTHORITATIVE HOME: OIDC Auth Transaction Field / Concurrency Architecture.

ROOT REPAIR: authoritative atomic `PENDING → PROCESSING` claim before verifier retrieval and token exchange.

FALSIFIER: two concurrent callbacks both reach token exchange.

TEST: parallel callback race test.

EVIDENCE: atomic claim proof.

### FBR-AUTH-014: Initiating User-Agent Binding Missing

SYMPTOM: A valid OIDC callback could be transplanted into a different browser/user-agent context if transaction continuation is only state-based and not bound to the initiating interaction.

VISIBLE EFFECT: victim browser may become authenticated as attacker or another unintended canonical identity.

CONSUMER: login callback, account-link callback, session creation, browser security.

BROKEN RELATION: login start user-agent interaction → callback user-agent continuation.

PRODUCER: no explicit initiating user-agent binding relation.

AUTHORITY: Browser Security / OIDC Transaction Field.

STATE: underdefined.

FIRST BROKEN RELATION: the system validates protocol transaction material without proving the callback is delivered by the legitimate continuation of the user-agent interaction that started the transaction.

AUTHORITATIVE HOME: Initiating User-Agent Binding Architecture / Browser Security / OIDC Transaction Field.

ROOT REPAIR: add transaction-specific initiating user-agent binding validated before transaction claim.

Required law:

LOGIN TRANSACTION
→ INITIATING USER-AGENT BINDING

VALID OIDC STATE
!=
VALID INITIATING USER-AGENT RELATION

TRANSFERRED CALLBACK
!=
LEGITIMATE LOGIN CONTINUATION

DEPENDENCY PROPAGATION:

* OIDC start
* OIDC callback
* cookie/browser security
* persistence
* API
* frontend
* runtime
* tests
* falsifiers
* threat model
* Real Google Proof

FALSIFIER: callback valid for one initiating interaction produces session in unrelated browser.

TEST: login/session swapping callback transplantation test.

EVIDENCE: user-agent binding proof.

### FBR-AUTH-015: Redirect Target Legitimacy Undefined

SYMPTOM: Architecture referred to “redirect target if legitimate” without defining legitimacy.

VISIBLE EFFECT: arbitrary attacker-controlled absolute URLs could become post-auth redirects or error redirects.

CONSUMER: login start, post-login redirect, post-link redirect, error redirect, cancel redirect, recovery redirect.

BROKEN RELATION: redirect target candidate → validation → legitimate local destination.

PRODUCER: no explicit redirect-target validation relation.

AUTHORITY: Redirect Target Security.

STATE: underdefined.

FIRST BROKEN RELATION: redirect target legitimacy terminates in convention rather than explicit validation.

AUTHORITATIVE HOME: Redirect Target Architecture / API / Frontend / Security.

ROOT REPAIR: define safe redirect target law.

REDIRECT TARGET CANDIDATE
→ VALIDATION
→ LEGITIMATE LOCAL DESTINATION
→ REDIRECT

Arbitrary attacker-controlled absolute URLs must not become post-authentication redirects.

OIDC PROVIDER REDIRECT URI
!=
POST-AUTH APPLICATION REDIRECT TARGET

FALSIFIER: post-auth redirect sends browser to attacker-controlled origin.

TEST: open redirect adversarial tests.

EVIDENCE: redirect validation proof.

### FBR-AUTH-016: Provider Error / User Cancel Callback Path Missing

SYMPTOM: Callback behavior when provider does not return a successful authorization code was not fully terminalized.

VISIBLE EFFECT: provider denial/cancel/malformed callback could leave transaction reusable, leak details, or create inconsistent frontend projection.

CONSUMER: Google callback, frontend error projection, transaction state machine, audit.

BROKEN RELATION: provider error/cancel callback → safe terminal no-effect state.

PRODUCER: no complete provider error/cancel path.

AUTHORITY: OIDC Callback Failure Architecture.

STATE: underdefined.

FIRST BROKEN RELATION: non-success provider callback path was not modeled as a terminal, no-token-exchange, no-local-effect path.

AUTHORITATIVE HOME: Provider Error / Cancel Callback Architecture.

ROOT REPAIR: add provider-denied/cancel/error callback terminal path:

CALLBACK
→ LOOKUP TRANSACTION
→ VALIDATE INITIATING USER-AGENT BINDING
→ VALIDATE STATE WHERE PROTOCOL PROVIDES IT
→ VALIDATE TRANSACTION
→ TERMINALIZE SAFELY
→ MAKE VERIFIER UNAVAILABLE
→ NO TOKEN EXCHANGE
→ NO PROVIDER IDENTITY
→ NO LOCAL SESSION
→ NO BUSINESS EFFECT
→ SAFE DENIED / CANCELLED / ERROR PROJECTION

FALSIFIER: provider `access_denied` creates local session or leaves transaction replayable.

TEST: provider cancel/error callback tests.

EVIDENCE: provider error proof.

### FBR-AUTH-017: Session Fixation / Replacement Boundary Underdefined

SYMPTOM: Successful authentication could accidentally preserve attacker-controlled authenticated session identity if session replacement behavior is undefined.

VISIBLE EFFECT: browser may continue with stale or attacker-associated session state after login.

CONSUMER: login success, callback success, local session creation, cookie replacement.

BROKEN RELATION: successful authentication → new authoritative session relation → prior session handling.

PRODUCER: session creation architecture did not explicitly define replacement/fixation boundary.

AUTHORITY: Session Architecture / Browser Security.

STATE: underdefined.

FIRST BROKEN RELATION: new authentication success does not explicitly govern pre-existing session cookie state.

AUTHORITATIVE HOME: Session Field / Cookie Security.

ROOT REPAIR: successful authentication must create a fresh local session relation and set/replace session cookie; stale or pre-existing session identity must not become authority for the new authentication result.

FALSIFIER: login preserves attacker-controlled authenticated session identity.

TEST: session fixation / login replacement test.

EVIDENCE: session replacement proof.

### FBR-AUTH-018: Local Password Login CSRF Boundary Underdefined

SYMPTOM: Local password login can create a fresh authenticated session, while the existing general CSRF law is scoped to requests already authenticated by cookies.

VISIBLE EFFECT: A hostile origin could potentially attempt to submit attacker-selected credentials into a victim browser and cause session swapping unless the actual HTTP/browser contract prevents it.

CONSUMER:

* `POST /auth/login`
* local password login
* session creation
* browser security
* CSRF architecture
* frontend login

BROKEN RELATION:

unauthenticated login request
→ legitimate browser/login interaction
→ credential validation
→ fresh session creation

PRODUCER: local password login HTTP contact.

AUTHORITY: Browser Security / Login CSRF Boundary.

STATE: underdefined until implementation proves that cross-site login submission cannot create an unintended authenticated session.

FIRST BROKEN RELATION: The architecture defines CSRF for already cookie-authenticated unsafe requests and OIDC callback continuation, but does not explicitly define equivalent login-CSRF protection for local password login.

AUTHORITATIVE HOME:

* Browser, Cookie and HTTP Security Architecture
* API Architecture
* Local Password Authentication
* Anti-CSRF Work Unit

ROOT REPAIR:

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH SESSION COMMIT

Required non-collapse:

LOGIN REQUEST
!=
LOGIN EFFECT

VALID PASSWORD
!=
PERMISSION FOR AN UNRELATED BROWSER CONTEXT TO BE SILENTLY SESSION-SWAPPED

LOCAL PASSWORD LOGIN CSRF
!=
OIDC CALLBACK CSRF / LOGIN-SWAPPING PROOF

APPLICATION AUTHENTICATED-CSRF BOUNDARY
!=
LOCAL LOGIN-CSRF BOUNDARY

Implementation may satisfy the boundary through a repository-compatible proven mechanism such as:

* pre-auth CSRF token bound to a pre-auth browser interaction
* strict Origin validation
* Fetch Metadata validation
* a request media-type / same-origin contract that structurally prevents cross-site form submission
* a defensible combination of these mechanisms
* another mechanism that proves the same architectural invariant

The architecture requires proof of the invariant, not a specific mechanism.

FALSIFIER: A hostile origin can cause a victim browser to authenticate into an attacker-selected local account.

TEST: Browser/API adversarial login-CSRF test using the actual HTTP request contract.

EVIDENCE: Login-CSRF boundary proof.

## 8. Target Identity Architecture

### 8.1 Target Field

FIELD: Canonical NQUIRY Identity & Authentication Field

PURPOSE: Resolve a verified authentication proof into a canonical NQUIRY identity and authenticated session without granting business authority.

PARENT FIELD: NQUIRY governance, authority, boundary and command architecture.

CHILD FIELDS:

* Canonical Identity Field
* Authentication Method Field
* Local Credential Field
* Local Login-CSRF Boundary Field
* Email Verification Field
* Google OIDC Field
* OIDC Auth Transaction Field
* Initiating User-Agent Binding Field
* OIDC Transaction State Machine Field
* PKCE Confidential Verifier Field
* ID Token Trust Field
* Provider Identity Field
* Protocol Callback Field
* Redirect Target Field
* Provider Error / Cancel Field
* Account Creation Boundary Field
* Future Provider Field
* Session Field
* Verification Field
* Account Linking Field
* Recovery Field
* Revocation Field
* Browser Security Field
* Anti-CSRF Boundary Field
* CORS Boundary Field
* Runtime DB Principal Capability Field
* Audit/Evidence Field

### 8.2 Canonical Flow

AUTH METHOD PROOF
→ VALIDATION
→ CANONICAL IDENTITY RESOLUTION
→ SESSION COMMIT
→ REQUEST IDENTITY RESOLUTION
→ AUTHORIZATION BOUNDARY
→ MEMBERSHIP / ROLE / AUTHORITY / CAPABILITY

### 8.3 Local Password Login Flow

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ CANONICAL IDENTITY RESOLUTION
→ FRESH LOCAL SESSION COMMIT
→ COOKIE SET / REPLACEMENT
→ RE-READ `/auth/me`
→ AUTHENTICATED FIELD RECONSTRUCTION

The selected implementation mechanism for the login-CSRF boundary is autonomous, but must prove that a hostile origin cannot cause a victim browser to authenticate into an attacker-selected local account.

### 8.4 OIDC Login Start Flow

LOGIN START
→ CREATE TRANSACTION
→ BIND INITIATING USER AGENT
→ VALIDATE POST-AUTH REDIRECT TARGET CANDIDATE
→ GENERATE STATE
→ GENERATE NONCE
→ GENERATE PKCE VERIFIER
→ STORE CONFIDENTIAL VERIFIER BINDING
→ DERIVE CODE CHALLENGE
→ REDIRECT TO PROVIDER

### 8.5 OIDC Callback Flow

CALLBACK
→ TRANSACTION LOOKUP
→ VERIFY TRANSACTION EXISTS
→ VERIFY PENDING
→ VERIFY INITIATING USER-AGENT RELATION
→ VALIDATE RETURNED STATE
→ VALIDATE EXPIRY
→ VALIDATE PURPOSE
→ VALIDATE INITIATING USER ID WHEN ACCOUNT_LINK
→ ATOMIC PENDING TO PROCESSING CLAIM
→ RETRIEVE TRANSACTION-BOUND PKCE VERIFIER
→ TOKEN EXCHANGE
→ RECEIVE ID TOKEN
→ VALIDATE SIGNATURE
→ VALIDATE ISSUER
→ VALIDATE AUDIENCE
→ VALIDATE EXPIRATION
→ VALIDATE ALL OTHER REQUIRED TOKEN CONDITIONS
→ VALIDATE NONCE CLAIM
→ EXTRACT TRUSTED PROVIDER SUBJECT
→ RESOLVE LOCAL IDENTITY
→ EXECUTE LOCAL EFFECT GATE
→ FINALIZE TRANSACTION
→ DESTROY OR DISABLE VERIFIER
→ RE-READ LOCAL STATE
→ RECONSTRUCT AUTHENTICATED FIELD

### 8.6 First External Provider Login Flow

VALID GOOGLE PROVIDER PROOF
→ LOOKUP `provider_issuer + provider_subject`

IF EXISTING BINDING:
→ resolve existing canonical `UserId`
→ continue toward local session commit

IF NO EXISTING BINDING:
→ evaluate ACCOUNT CREATION POLICY

ACCOUNT CREATION POLICY may resolve to:

* SELF_REGISTRATION_ALLOWED
* INVITATION_REQUIRED
* PRE_PROVISIONED_IDENTITY_REQUIRED
* GOVERNANCE_MEDIATED_CREATION
* DENIED / UNAVAILABLE

Until account creation policy is explicitly established, implementation must fail closed.

A valid Google identity must never automatically create:

* Workspace membership
* role
* governance root
* authority
* participation
* capability

### 8.7 Target Non-Collapse Law

The target Field must preserve all non-collapse laws listed in section 1 and system laws in section 34.

### 8.8 Target Persistence Shape

Minimum legitimate target relations:

* canonical user identity
* authentication method
* local password credential if allowed
* local password login-CSRF proof relation or equivalent request-bound validation mechanism where selected mechanism requires state
* external provider identity
* OIDC auth transaction
* OIDC transaction lifecycle state
* initiating user-agent binding
* confidential PKCE verifier binding or secure server-side verifier reference
* redirect target validation result or safe named destination
* account creation policy result / account creation event where policy allows creation
* verified email relation
* session
* session revocation
* verification challenge
* recovery challenge
* account link event
* account unlink/revocation event
* authentication event / audit evidence
* anti-CSRF proof relation or equivalent request-bound validation mechanism
* runtime DB-principal capability mapping/evidence where repository architecture requires explicit materialization

Do not add tables merely because this list exists. Add only where the Work Units require persistence or equivalent authoritative state to close a relation.

## 9. Authentication Methods

### 9.1 Method Classes

NQUIRY target authentication methods include only persistent or repeatable methods by which a canonical identity may authenticate:

1. LOCAL_PASSWORD
2. GOOGLE_OIDC
3. FUTURE_OIDC_PROVIDER
4. TEST_PROVIDER where explicitly bounded to development/test

RECOVERY_CHALLENGE is not an authentication method.

OIDC_TRANSACTION is not an authentication method.

INITIATING_USER_AGENT_BINDING is not an authentication method.

LOCAL_LOGIN_CSRF_PROOF is not an authentication method.

AUTHENTICATION METHOD != RECOVERY PROOF

### 9.2 Local Password

CURRENT: materialized and real.

TARGET: preserve as bounded method.

Required local password login law:

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH LOCAL SESSION COMMIT

The local password login-CSRF boundary must prove that a hostile origin cannot submit attacker-selected credentials into a victim browser and create an unintended authenticated session.

The local login-CSRF boundary may be satisfied by:

* pre-auth CSRF token bound to a pre-auth browser interaction
* strict Origin validation
* Fetch Metadata validation
* request media-type / same-origin contract that structurally prevents cross-site form submission
* a defensible combination of these mechanisms
* another repository-compatible mechanism proving the same invariant

CORS alone is not sufficient proof.

SameSite alone is not sufficient proof.

If pre-auth state is used:

* it must not become authenticated session
* it must not fix the authenticated session
* successful login must still create a fresh authenticated session
* it must not become canonical identity
* it must not become authorization

Production status depends on human authority:

* If password login is an official product method, add verification, reset, rate limiting, credential rotation, all-session revocation and email verification.
* If password login is not official product method, retain it as local/development adapter and do not expose it as production identity provider.

### 9.3 Google OIDC

TARGET: first production-capable external provider.

BOUNDARY:

* Google validates provider identity proof through Authorization Code Flow with PKCE.
* NQUIRY validates local OIDC transaction state before external token exchange.
* NQUIRY validates initiating user-agent binding before transaction claim.
* NQUIRY atomically claims transaction ownership before PKCE verifier retrieval and token exchange.
* NQUIRY retrieves original PKCE `code_verifier` from confidential server-side binding for token exchange only after successful claim.
* NQUIRY validates the ID Token before trusting nonce or subject claims.
* NQUIRY resolves provider subject to canonical `UserId` or account creation boundary.
* NQUIRY creates local session after local commit.
* Google never owns membership, role, governance or capability.

### 9.4 Future Provider Methods

Future Microsoft, GitHub or other OIDC providers may be added only through the provider abstraction and only when human product authority approves their product role. No future provider may bypass:

* transaction state machine
* initiating user-agent binding
* PKCE or equivalent proof where required by selected flow
* ID Token trust boundary
* account creation boundary
* account linking authority
* authentication-to-authorization separation

## 10. Email Authentication Architecture

### 10.1 Repository Fact

Current repository has local email/password login, no self-service registration, no password reset, no email verification and no email infrastructure claim.

### 10.2 Comparison

EMAIL + PASSWORD:

* fits current repository best because code and schema already exist
* requires verification, reset, rate limiting, rotation and revocation before product status
* stores credential secret material and therefore owns password-security obligations
* requires explicit local login-CSRF boundary before login request may produce fresh authenticated session

EMAIL + MAGIC LINK:

* requires reliable email delivery infrastructure
* requires challenge storage and replay resistance
* avoids password storage
* collapses login availability into email delivery availability
* not currently supported

EMAIL + ONE-TIME CODE:

* requires email delivery infrastructure
* requires attempt counters, expiry, replay resistance and enumeration resistance
* better for short-lived login proof than long-term credential
* not currently supported

HYBRID:

* can support local password plus verified email recovery
* can support OIDC primary plus email recovery
* more complex account linking and recovery policy

### 10.3 Recommended Email Model

Use the existing local password method as the lowest-disruption email-based method only if password login is approved as a product capability.

Minimum product-ready additions:

* verified email relation
* password reset challenge
* rate limiting
* credential rotation
* all-session revocation on credential reset
* audit evidence
* account enumeration resistance preserved
* email delivery proof lane
* local login-CSRF proof lane

If human authority does not approve password login as product capability, keep local password as development/prototype and make Google OIDC the production method.

### 10.4 Email Must Not Prove Identity Equivalence

Same email between Google and local credential must not automatically link accounts.

Email can be:

* lookup attribute
* verified contact route
* recovery proof component
* displayed identity attribute

Email cannot be:

* canonical identity key
* proof of same human across providers
* account-link authority by itself
* account creation authority by itself

## 11. Google OIDC Architecture

### 11.1 Selected Flow

Use OpenID Connect Authorization Code Flow with PKCE.

Do not use implicit flow.

Do not use frontend-stored provider tokens.

Do not infer identity from callback reachability.

Do not infer identity from authorization code receipt.

Do not infer identity from token response bytes.

Do not infer identity from parsed but unvalidated ID Token.

### 11.2 Login Start

LOGIN START validates and creates:

* transaction purpose LOGIN
* initiating user-agent binding
* transaction-specific state
* transaction-specific nonce
* transaction-specific PKCE verifier
* confidential server-side verifier binding
* derived code challenge
* legitimate post-auth redirect target or safe default destination
* expiration
* audit/provenance record

LOGIN START does not create:

* canonical identity
* provider identity
* authentication method
* local session
* Workspace membership
* role
* authority

### 11.3 OIDC Auth Transaction Field

FIELD: OIDC Auth Transaction Field

PURPOSE: represent the temporary authoritative relation created when NQUIRY starts an external OIDC authentication attempt.

Conceptual fields:

* transaction_id
* provider
* transaction_state
* state_hash or equivalent expected-state binding
* nonce_hash or equivalent expected-nonce binding
* initiating_user_agent_binding_ref
* confidential_pkce_verifier_ref or encrypted/sealed verifier value
* pkce_code_challenge metadata where useful
* post_auth_redirect_target_ref or safe named destination
* purpose: LOGIN or ACCOUNT_LINK
* initiating_user_id nullable for LOGIN, required for ACCOUNT_LINK
* created_at
* expires_at
* claimed_at
* completed_at
* failed_terminal_at
* expired_at
* cancelled_at where modeled separately
* verifier_unavailable_at or equivalent
* failure_reason nullable
* provenance_ref

Exact persistence technology remains implementation-autonomous, provided the transaction is authoritative, expiring, single-use, replay-resistant, purpose-bound, initiating-user-agent-bound, atomically claimable and contains a confidential server-side binding from which the original PKCE `code_verifier` can be retrieved only by the callback processor that successfully claims the transaction.

### 11.4 Transaction State Machine

Required semantic states:

PENDING
→ PROCESSING
→ COMPLETED

or:

PENDING
→ PROCESSING
→ FAILED_TERMINAL

or:

PENDING
→ EXPIRED

or, where useful:

PENDING
→ CANCELLED_TERMINAL

Exact enum names are implementation-autonomous.

Required semantics are not.

PENDING:

* transaction exists
* transaction has not been claimed by a callback
* initiating user-agent binding can be validated
* returned state, expiry, purpose and initiating user can be validated
* only PENDING can transition to PROCESSING
* provider error/cancel may terminalize safely without token exchange

PROCESSING:

* exactly one callback has atomically claimed the transaction
* only the winning processor may retrieve the PKCE verifier
* only the winning processor may enter token exchange
* no second callback may enter token exchange
* PROCESSING must never return to PENDING

COMPLETED:

* dedicated OIDC protocol processing reached legitimate terminal success state
* transaction can never be reused
* PKCE verifier is unavailable / unusable

FAILED_TERMINAL:

* processing began or security validation failed in a way that makes reuse unsafe
* transaction can never return to PENDING
* PKCE verifier is unavailable / unusable
* user-level recovery is a new OIDC authentication flow unless a standards-compliant provider/library mechanism proves safe retry

EXPIRED:

* transaction expired before legitimate processing
* transaction cannot be claimed
* PKCE verifier is unavailable / unusable

CANCELLED_TERMINAL:

* provider/user cancel or provider denial was safely projected
* no token exchange occurred
* no provider identity was produced
* no local session was created
* transaction cannot be replayed
* PKCE verifier is unavailable / unusable

Essential invariant:

AFTER SUCCESSFUL PENDING → PROCESSING CLAIM,
THE TRANSACTION IS NEVER AGAIN ELIGIBLE FOR ANOTHER CALLBACK PROCESSOR.

### 11.5 Initiating User-Agent Binding

FIELD: Initiating User-Agent Binding Field

PURPOSE: bind the OIDC transaction to the browser/user-agent interaction that started it, preventing callback transplantation and login/session swapping.

Required law:

LOGIN TRANSACTION
→ INITIATING USER-AGENT BINDING

VALID OIDC STATE
!=
VALID INITIATING USER-AGENT RELATION

TRANSFERRED CALLBACK
!=
LEGITIMATE LOGIN CONTINUATION

Required semantics:

* transaction-specific
* unpredictable or cryptographically protected where appropriate
* not canonical identity
* not authorization
* not business authority
* validated before transaction claim
* expires with the transaction
* invalid after terminal transaction state
* not browser-visible authority
* prevents cross-browser session swapping
* applies to LOGIN
* applies to ACCOUNT_LINK where link equivalence proof would be weakened by callback transplantation

Implementation mechanism remains autonomous. Legitimate mechanisms may include:

* HttpOnly pre-auth correlation cookie
* signed or sealed browser binding
* server-side pre-auth browser session
* another equivalent architecture-compatible mechanism

The mechanism must not break OIDC callback delivery through normal provider redirects.

### 11.6 Login CSRF / Session Swapping Threat Relation

Attack trace:

ATTACKER STARTS GOOGLE AUTHENTICATION
→ ATTACKER OBTAINS VALID CALLBACK MATERIAL
→ VICTIM BROWSER RECEIVES OR FOLLOWS TRANSFERRED CALLBACK
→ CALLBACK HAS VALID PROVIDER MATERIAL
→ WITHOUT USER-AGENT BINDING, VICTIM BROWSER COULD RECEIVE LOCAL SESSION FOR ATTACKER IDENTITY

Target boundary:

A callback valid for one initiating user-agent interaction cannot be transplanted into another unrelated user-agent interaction and produce a legitimate local authenticated session.

Repair:

* start creates initiating user-agent binding
* callback validates initiating user-agent binding before claim
* callback with missing/mismatched binding fails closed
* no token exchange if binding fails
* no local session if binding fails
* transaction terminalization follows failure semantics

### 11.7 Atomic Claim Law

Required relation:

CALLBACK
→ LOCAL TRANSACTION VALIDATION
→ ATOMIC CLAIM

PENDING
→ PROCESSING

Only the process that successfully performs this transition may continue to:

* PKCE verifier retrieval
* token exchange
* provider proof validation
* identity resolution
* local effect processing

A concurrent callback that observes:

* PROCESSING
* COMPLETED
* FAILED_TERMINAL
* EXPIRED
* CANCELLED_TERMINAL

must not continue to token exchange.

It must fail closed.

This transition must be enforced by authoritative state, not process-local memory.

Possible implementation mechanisms may include:

* conditional database update
* row lock
* compare-and-swap
* transactional state transition
* another repository-compatible atomic mechanism

### 11.8 No Return to Pending

Once a transaction enters PROCESSING:

PROCESSING → PENDING

MUST REMAIN IMPOSSIBLE.

PROCESSING means the authorization code may already have been presented to the external provider.

After that boundary, the system may not safely assume that the authorization code remains unused.

### 11.9 Uncertain External Outcome Law

RETRY != RECOVERY

If NQUIRY has atomically claimed an OIDC transaction and then:

* network failure occurs
* process crashes
* timeout occurs
* provider response becomes uncertain
* token exchange outcome cannot be reconstructed safely

the implementation must not blindly retry the same authorization code and PKCE verifier.

Default architecture:

UNCERTAIN TOKEN EXCHANGE OUTCOME
→ FAILED_TERMINAL
→ ORIGINAL TRANSACTION CANNOT RESTART
→ NEW OIDC AUTHENTICATION FLOW REQUIRED

This prevents ambiguous duplicate exchange behavior.

Do not invent provider-safety proof.

If a standards-compliant provider/library mechanism proves retrying is safe for the actual failure condition, implementation may follow that proof, but architecture default remains fail closed into non-reusable transaction.

### 11.10 PKCE Confidential Verifier Field

FIELD: PKCE Confidential Verifier Field

PURPOSE: preserve the original PKCE `code_verifier` as confidential server-side material until the winning callback processor performs provider token exchange.

Required relation:

PKCE VERIFIER GENERATION
→ CONFIDENTIAL SERVER-SIDE BINDING
→ PROVIDER AUTHORIZATION REQUEST USES derived code_challenge
→ CALLBACK TRANSACTION LOOKUP
→ USER-AGENT BINDING VALIDATION
→ LOCAL TRANSACTION VALIDATION
→ ATOMIC PENDING → PROCESSING CLAIM
→ CONFIDENTIAL VERIFIER ACCESS BY WINNER ONLY
→ TOKEN EXCHANGE USES original code_verifier
→ TERMINAL TRANSACTION STATE
→ VERIFIER BECOMES UNAVAILABLE / UNUSABLE

Guarantees:

* raw `code_verifier` is never exposed to browser JavaScript
* raw `code_verifier` is never placed in frontend state
* raw `code_verifier` is never written to logs
* raw `code_verifier` is never emitted into proof reports
* raw `code_verifier` is not stored in an irretrievable hash-only form
* verifier is bound to exactly one OIDC transaction
* verifier is bound to transaction purpose
* verifier retrieval is authorized only for callback processor that successfully claimed matching transaction
* verifier is unavailable after transaction terminal state
* transaction replay cannot recover or reuse verifier
* verifier from one transaction cannot satisfy another transaction
* verifier from LOGIN transaction cannot satisfy ACCOUNT_LINK transaction
* verifier from ACCOUNT_LINK transaction cannot satisfy LOGIN transaction

### 11.11 State, Nonce and PKCE Distinctions

STATE:

* protocol correlation / anti-forgery value
* travels through browser redirect flow
* must be unpredictable and validated
* must not be unnecessarily logged
* expected protected binding remains server-side

NONCE:

* sent in authentication request
* returned inside ID Token claim
* expected value must be bound to transaction
* checked only after the ID Token containing it has passed required validation

PKCE `code_verifier`:

* confidential transaction material
* must not be sent in authorization request
* only derived `code_challenge` goes to authorization endpoint
* original verifier is sent to token endpoint
* must remain confidential from browser JavaScript in this server-side architecture

### 11.12 ID Token Trust Law

TOKEN RESPONSE RECEIVED
!=
VERIFIED IDENTITY

ID TOKEN PARSED
!=
TRUSTED ID TOKEN

ID TOKEN SIGNATURE VALID
!=
COMPLETE ID TOKEN VALIDATION

PROVIDER SUBJECT
MUST NOT BECOME TRUSTED IDENTITY INPUT
UNTIL REQUIRED ID TOKEN VALIDATION HAS SUCCEEDED.

NONCE CLAIM
MUST NOT BE TRUSTED
UNTIL THE ID TOKEN CONTAINING IT HAS PASSED REQUIRED CRYPTOGRAPHIC AND SEMANTIC VALIDATION.

At minimum preserve validation of:

* signature
* issuer
* audience
* expiration
* nonce
* any other validation required by the selected OIDC library/specification for the actual token shape

Do not hand-roll token validation where a standards-compliant maintained OIDC library can own protocol mechanics.

The provider adapter may own protocol validation.

It may not own NQUIRY canonical identity or authorization.

### 11.13 Provider Subject

Canonical external identity key:

`provider_issuer` + `provider_subject`

NOT email.

Provider subject collision rules:

* same issuer + same subject linked to existing NQUIRY identity → login existing identity
* same issuer + same subject linked to another NQUIRY identity while authenticated as different identity → deny/reject link attempt
* same email but different subject → collision boundary, not automatic link
* changed provider email → update attribute only after provider proof; do not change canonical link

Provider subject is trusted only after:

* transaction was claimed
* token exchange succeeded
* ID Token validation succeeded
* nonce validation succeeded

### 11.14 First Google Login / Account Creation Boundary

VALID GOOGLE PROVIDER PROOF
→ LOOKUP `provider_issuer + provider_subject`

IF EXISTING BINDING:

* resolve existing canonical `UserId`
* validate auth method active
* continue toward local session commit

IF NO EXISTING BINDING:

* evaluate ACCOUNT CREATION POLICY

ACCOUNT CREATION POLICY outcomes:

SELF_REGISTRATION_ALLOWED:

* create canonical `UserId`
* create provider identity binding
* create authentication method
* audit account creation
* continue toward local session commit
* no Workspace authority is created unless separately authorized

INVITATION_REQUIRED:

* require valid invitation relation
* invitation must authorize identity creation only
* no Workspace authority unless invitation explicitly and legitimately carries separate membership/governance relation

PRE_PROVISIONED_IDENTITY_REQUIRED:

* require existing unlinked NQUIRY identity prepared for provider binding
* link provider subject to that identity only after matching approved pre-provisioning rule

GOVERNANCE_MEDIATED_CREATION:

* require governance-approved creation relation
* account creation remains distinct from Workspace authority unless governance relation explicitly establishes it

DENIED / UNAVAILABLE:

* fail closed
* no user created
* no session created
* safe error boundary returned

The exact product policy remains HUMAN_AUTHORITY_REQUIRED.

Until policy is established, default behavior is DENIED / UNAVAILABLE.

### 11.15 Local Effect Commit After Provider Proof

PROVIDER PROOF
!=
LOCAL COMMIT

After provider proof succeeds, NQUIRY still performs local effect gates:

* provider subject lookup
* account creation policy if required
* account linking authority if required
* canonical identity resolution
* authentication method validation
* fresh session creation
* audit/provenance

Where multiple local persistence effects form one semantic effect, use legitimate local transactional boundaries so partial identity creation/binding is not silently represented as full authentication success.

Especially preserve:

ACCOUNT CREATION
+
PROVIDER IDENTITY BINDING

as one coherent local effect where architecture requires both.

If local effect commit fails after provider proof:

* transaction must not return to PENDING
* transaction must not be replayable
* transaction should enter FAILED_TERMINAL unless coherent local committed state can be proven and reconstructed
* browser may begin a fresh login attempt
* subsequent valid login may encounter already committed local relations if prior local effect partially committed
* local effect boundaries must be coherent and reconstructable

Prefer atomic local commits where relations are inseparable.

### 11.16 Provider Error / Cancel Callback

Provider non-success callback path:

CALLBACK
→ LOOKUP TRANSACTION
→ VALIDATE INITIATING USER-AGENT BINDING
→ VALIDATE STATE WHERE PROTOCOL PROVIDES IT
→ VALIDATE TRANSACTION
→ TERMINALIZE SAFELY
→ MAKE VERIFIER UNAVAILABLE
→ NO TOKEN EXCHANGE
→ NO PROVIDER IDENTITY
→ NO LOCAL SESSION
→ NO BUSINESS EFFECT
→ SAFE DENIED / CANCELLED / ERROR PROJECTION

Handle at minimum:

* user denies consent
* user cancels
* provider returns `access_denied`
* provider returns another defined OAuth/OIDC error
* provider temporarily unavailable
* malformed callback
* state missing
* state mismatch
* transaction missing
* transaction expired
* transaction already processing
* transaction already terminal

Internal distinctions may include:

* USER_CANCEL
* PROVIDER_DENIAL
* PROVIDER_FAILURE
* SECURITY_REJECTION
* LOCAL_FAILURE

Public responses may collapse sensitive distinctions.

### 11.17 Redirect Target Security

OIDC PROVIDER REDIRECT URI
!=
POST-AUTH APPLICATION REDIRECT TARGET

Redirect target law:

REDIRECT TARGET CANDIDATE
→ VALIDATION
→ LEGITIMATE LOCAL DESTINATION
→ REDIRECT

Arbitrary attacker-controlled absolute URLs must not become post-authentication redirects.

Valid mechanisms may include:

* relative internal destinations
* explicit allowlist
* named internal destinations
* equivalent safe mechanism

Redirect target validation applies to:

* login start redirect target
* post-login redirect
* post-link redirect
* error redirect
* cancel redirect
* recovery redirect where relevant

Sensitive authorization artifacts must not be sent to arbitrary hostile origins through application redirect behavior.

### 11.18 Session Commit Boundary

Provider callback success is not local session commit.

Effect gate:

OIDC callback candidate
→ transaction lookup
→ verify transaction exists
→ verify transaction state is PENDING
→ verify initiating user-agent binding
→ validate returned state
→ validate transaction expiry
→ validate transaction purpose
→ validate initiating user when ACCOUNT_LINK
→ atomically claim transaction PENDING → PROCESSING
→ retrieve original PKCE `code_verifier` confidentially
→ token exchange using authorization code + original `code_verifier`
→ receive token response
→ validate ID Token signature
→ validate issuer
→ validate audience
→ validate expiration
→ validate other required token conditions
→ validate nonce claim against transaction nonce
→ extract trusted provider subject
→ resolve provider identity or account creation boundary
→ execute legitimate local effect gate
→ create fresh local session relation
→ set/replace session cookie
→ finalize transaction terminal state
→ make verifier unavailable / unusable
→ re-read local authentication state
→ reconstruct visible authenticated field

### 11.19 Protocol Callback Semantics

OIDC callback may be implemented as a GET route because it is a protocol response contact.

OIDC callback GET is not an ordinary application-resource GET.

GET / ordinary application resource
!=
mutation command

# OIDC callback GET

protocol response contact

OIDC callback GET
!=
authority by HTTP verb alone

PROTOCOL CALLBACK
!=
LOCAL COMMIT

The callback may materialize only protocol-defined security / identity effects through dedicated proof and effect gates.

Callback must not:

* perform arbitrary business commands
* grant Workspace authority
* bypass authorization
* bypass account creation policy
* bypass account linking authority
* bypass user-agent binding
* bypass transaction claim
* bypass replay resistance
* create a general precedent for GET mutation semantics

### 11.20 Provider Token Storage

Default target: do not store Google access/refresh tokens unless a later product relation requires provider API access.

NQUIRY needs authentication proof, not Google API access.

If provider tokens are stored later:

* encrypted persistence required
* scope minimization required
* revocation required
* audit required
* human authority required if external API access changes product behavior

### 11.21 Required Google Routes

Implementation may choose exact route names, but semantic contacts must exist:

* start Google login
* Google callback
* start Google account link from authenticated session
* Google link callback
* unlink Google method
* provider test endpoint only in test mode, never production

Recommended public shape:

* `GET /auth/google/start`
* `GET /auth/google/callback`
* `POST /auth/google/link/start`
* `GET /auth/google/link/callback`
* `POST /auth/methods/{methodId}/unlink`

Exact names are implementation-autonomous if semantics remain true.

## 12. Additional Provider Decision

### 12.1 Microsoft

Microsoft OIDC should be architecturally supported by the provider abstraction but not implemented unless human authority declares enterprise compatibility as a product requirement.

### 12.2 GitHub

GitHub should be architecturally possible but not implemented by default. It is suitable if NQUIRY’s actual user population includes developer/operator identity workflows.

### 12.3 Provider Abstraction Rule

NQUIRY should not hard-code Google-only domain semantics.

Provider adapter owns:

* provider metadata/discovery
* redirect construction
* token exchange
* ID Token validation
* provider error/cancel normalization
* claim normalization after validation

Provider adapter does not own:

* OIDC transaction persistence
* OIDC transaction exclusive claim
* initiating user-agent binding
* redirect target validation
* PKCE verifier lifecycle outside provider token exchange
* canonical identity
* account creation policy
* Workspace membership
* role
* governance
* authority
* recovery policy
* account linking policy beyond provider proof

## 13. Canonical Identity Model

### 13.1 Canonical Identity

Canonical identity remains `UserId`.

Target `users` semantics:

* canonical human identity
* stable across authentication methods
* not a credential
* not a role
* not a Workspace member by itself
* not an authority holder by itself
* not an account creation policy by itself

### 13.2 Authentication Method Relation

Target relation:

`authentication_methods`

Fields conceptually include:

* method_id
* user_id
* method_type
* status
* created_at
* revoked_at
* last_authenticated_at
* provenance_ref

Method-specific tables can hold method data:

* local password credential
* external provider identity
* verified email relation where method uses verified email

Excluded:

* recovery challenge
* OIDC transaction
* initiating user-agent binding
* PKCE verifier
* CSRF proof
* local login-CSRF proof

These are proof, protocol or browser-security relations, not persistent authentication methods.

### 13.3 External Provider Identity

Target relation:

`external_provider_identities`

Conceptual fields:

* method_id
* provider_issuer
* provider_subject
* provider_email_at_last_auth
* provider_email_verified_at_last_auth
* provider_display_name_at_last_auth
* linked_at
* revoked_at
* provenance_ref

Unique constraint:

* provider_issuer + provider_subject unique

Provider subject may enter this relation only after required ID Token validation and nonce validation.

### 13.4 OIDC Transaction Identity Boundary

An OIDC transaction is not a provider identity.

An OIDC transaction is:

* temporary
* start/callback correlation state
* user-agent continuation state
* proof-preparation state
* state / nonce / PKCE verifier binding
* redirect target binding
* explicit lifecycle state
* consumed or terminal before identity effect is considered complete

It does not establish canonical identity.

It does not authenticate the user by itself.

It does not persist as an auth method.

### 13.5 Initiating User-Agent Boundary

Initiating user-agent binding is not identity.

It proves callback continuation relation.

It does not prove:

* canonical user
* provider subject
* membership
* role
* authority
* capability

### 13.6 Local Login-CSRF Boundary

Local login-CSRF proof is not identity.

It proves the local login request is allowed to proceed to credential validation under the actual browser/API request contract.

It does not prove:

* canonical user
* password validity
* session validity
* authorization
* membership
* role
* capability

### 13.7 PKCE Verifier Boundary

PKCE verifier confidential material is not identity.

PKCE verifier confidential material is:

* temporary
* confidential
* transaction-bound
* purpose-bound
* accessible only after atomic transaction claim
* required for provider token exchange
* unavailable after transaction terminal state

It does not identify a user.

It does not link an account.

It does not authorize an application command.

### 13.8 ID Token Claim Boundary

ID Token claims are not trusted identity input until required ID Token validation has succeeded.

Provider subject is not canonical identity.

Provider subject is an external identifier that NQUIRY maps to canonical identity through provider identity binding or account creation policy.

Nonce claim is not trusted merely because the token was parsed.

Nonce claim is trusted only after ID Token validation and nonce match against transaction-bound expected nonce.

### 13.9 Verified Email

Target relation:

`verified_emails`

Conceptual fields:

* user_id
* email
* verified_at
* verification_method
* superseded_at
* revoked_at
* provenance_ref

Email is not canonical identity.

### 13.10 Identity Equivalence

Identity equivalence can be established by:

* authenticated existing NQUIRY session linking a new method
* account creation policy producing a new canonical identity
* recovery authority proving account ownership
* administrative/governance intervention if explicitly authorized
* migration script with recorded non-proof or proof provenance

Identity equivalence cannot be established by:

* same email alone
* same display name
* provider success alone
* login attempt
* unverified email possession
* recovery request without verified recovery proof
* unclaimed OIDC transaction
* unvalidated ID Token
* PKCE verifier possession alone
* initiating user-agent binding alone
* local login-CSRF proof alone
* OIDC callback route reachability alone
* token response bytes alone

## 14. Account Linking Architecture

### 14.1 Linking Law

ACCOUNT LINKING != AUTHENTICATION

ACCOUNT LINKING != AUTHORIZATION

SAME EMAIL != PROVEN SAME HUMAN

OIDC LOGIN TRANSACTION != OIDC LINK TRANSACTION

LINK CALLBACK GET != LINK COMMIT

VALID OIDC STATE != VALID INITIATING USER-AGENT RELATION

### 14.2 Legitimate Link Flow: Authenticated User Adds Google

Candidate:

authenticated NQUIRY session requests Google link.

Start:

* existing session valid
* canonical `UserId` known
* link request authorized for own identity
* ACCOUNT_LINK transaction created
* initiating `UserId` bound to transaction
* initiating user-agent binding created
* state/nonce/PKCE created
* redirect target validated

Callback validation before token exchange:

* transaction exists
* transaction is PENDING
* initiating user-agent binding valid
* transaction purpose is ACCOUNT_LINK
* transaction initiating user matches current authenticated canonical `UserId`
* returned state matches transaction
* transaction not expired
* transaction atomically claimed PENDING → PROCESSING

Provider proof:

* winner retrieves transaction-bound PKCE verifier
* token exchange uses original verifier
* ID Token validation succeeds
* nonce claim matches transaction-bound nonce
* provider subject is extracted only after validation

Authority:

* current authenticated user may link method to own identity
* provider subject collision checks pass
* same email does not link
* additional step-up may be required if method is high risk or last method changes

Effect gate:

* create external provider identity relation
* create auth method relation
* audit link event
* finalize transaction terminal state
* make verifier unavailable / unusable
* re-read identity methods
* reconstruct account security surface

### 14.3 Legitimate Link Flow: Google User Adds Verified Email/Password

Candidate:

authenticated Google-based session wants local email/password method.

Validation:

* current session valid
* email verification challenge completed
* password credential created
* no existing credential method conflict

Authority:

* authenticated identity + verified email proof

Effect:

* create verified email
* create local password method
* audit link event

### 14.4 Collision: Provider Identity Already Linked Elsewhere

Behavior:

* deny/reject linking
* do not disclose unnecessary protected details
* do not merge accounts automatically
* audit collision event
* OIDC transaction remains terminal after processing began; it cannot be replayed

### 14.5 Email Collision

Same email on different accounts is not automatic link.

Behavior:

* if email is already verified on another identity, linking requires stronger proof or human authority
* do not silently merge
* do not silently transfer credential
* do not silently grant access

### 14.6 Unlink Last Authentication Method

Must remain impossible unless recovery authority is established or account disable is intended.

FALSIFIER: user can unlink last method and strand identity without explicit recovery/disable effect gate.

### 14.7 Provider Email Change

Provider email change updates provider attribute only after provider proof.

It does not change:

* canonical user ID
* Workspace membership
* role
* authority
* verified local email relation

## 15. Session Architecture

### 15.1 Target Session Model

Preserve server-side opaque sessions.

Reasons:

* current repository already implements DB-backed sessions
* sessions are revocable
* no stateless JWT authorization semantics are needed
* NQUIRY authorization is server-side and must be re-evaluated per request

### 15.2 Session Persistence

Target session fields:

* session_id
* user_id
* auth_method_id where applicable
* proof provenance where auth method is not directly applicable
* token_hash
* issued_at
* expires_at
* revoked_at
* revoked_reason
* last_seen_at if needed
* user_agent_hash if needed
* ip_hash if needed
* provenance_ref

Do not store raw token.

### 15.3 Session Traceability

Each session can be traced to:

* canonical `UserId`
* authentication method or proof provenance
* issued time
* expiration
* revocation state

A session must not carry business authority.

### 15.4 Session Creation and Replacement

Successful authentication creates a fresh local session relation.

A new successful authentication must not accidentally preserve an attacker-controlled authenticated session identity.

On login/callback success:

* create new server-side session row
* set or replace authenticated session cookie
* ensure visible authenticated state reconstructs from new session
* do not reuse stale identity from prior cookie as proof of new login identity
* preserve existing independent sessions only where concurrent-session policy allows

If pre-auth state is used for local password login-CSRF protection:

* it must not become the authenticated session
* it must not fix the authenticated session
* it must not become canonical identity
* it must not become authorization
* successful login must still create a fresh authenticated session

### 15.5 Expiration

Current default: 12 hours.

Production session lifetime is HUMAN_AUTHORITY_REQUIRED.

Implementation may keep 12 hours until policy changes.

### 15.6 Rotation

Target architecture should support session rotation after high-risk events:

* login
* account linking
* password reset
* provider link/unlink
* recovery completion
* method revocation
* account security change

Exact rotation implementation is autonomous if:

* old token stops working when required
* new token is committed
* replay resistance is preserved

### 15.7 Revocation Propagation

Credential reset, auth method revoke, provider unlink and account disable must revoke dependent sessions.

Single-session logout remains current behavior.

All-session logout must be added for account security.

Session revocation scopes:

* single-session scope
* all-session scope
* authentication-method scope
* account-disable scope

### 15.8 Session Must Remain Non-Authority

SESSION != AUTHORIZATION

A session proves that a canonical identity has an active authenticated browser/server relation.

A session does not prove:

* Workspace membership
* role
* grant
* governance root
* capability
* participation

## 16. Verification Architecture

### 16.1 Email Verification

State machine:

UNVERIFIED
→ CHALLENGE_ISSUED
→ VERIFIED
→ SUPERSEDED / REVOKED / EXPIRED

Challenge properties:

* random high-entropy token or code
* token stored hashed
* short expiry
* attempt limit
* resend throttling
* email enumeration resistance
* audit event

Email delivery alone is not verification.

Verification commit occurs only after correct challenge proof.

### 16.2 Provider Verification

Provider verification is OIDC validation.

Required order:

1. OIDC transaction lookup.
2. Verify transaction exists.
3. Verify transaction state is PENDING.
4. Verify initiating user-agent binding.
5. Validate returned state against transaction.
6. Validate transaction expiry.
7. Validate transaction purpose.
8. Validate initiating user binding when ACCOUNT_LINK.
9. Atomically claim transaction PENDING → PROCESSING.
10. Retrieve transaction-bound PKCE verifier confidentially.
11. Exchange authorization code using original PKCE verifier.
12. Receive token response.
13. Validate ID Token signature.
14. Validate issuer.
15. Validate audience.
16. Validate expiration.
17. Validate other required token conditions.
18. Validate nonce claim against transaction-bound expected nonce.
19. Extract trusted provider subject.
20. Extract email only as provider attribute.
21. Resolve provider identity or account creation boundary.
22. Execute local effect gate.
23. Finalize transaction terminal state.
24. Make PKCE verifier unavailable / unusable.

Provider email verified claim may support email verification only if policy accepts provider email claim as sufficient. That policy is HUMAN_AUTHORITY_REQUIRED if not already established.

### 16.3 Local Password Credential Verification

Password verification remains PBKDF2.

Credential validity requires:

* local password login-CSRF boundary satisfied for browser login requests
* method active
* credential active
* user identity active
* no account disable
* password hash verifies
* no active lockout/rate-limit boundary

## 17. Recovery Architecture

### 17.1 Distinctions

Authentication retry: same credential, no identity state change.

Credential reset: replace password credential after proof.

Account recovery: regain access to canonical identity when method unavailable.

Session recovery: re-authenticate or reissue session after verified recovery authority.

Provider recovery: handle external provider unavailable/revoked/deleted.

Identity recovery: establish continuity of canonical `UserId`.

Authorization recovery: restore membership/role/authority; not an authentication concern.

OIDC retry: not the same as recovery. After transaction claim and uncertain external outcome, the safe user-level recovery is a new OIDC authentication flow.

### 17.2 Recovery Proof Law

RECOVERY_CHALLENGE is not an authentication method.

AUTHENTICATION METHOD != RECOVERY PROOF

EMAIL STRING != RECOVERY AUTHORITY

RECOVERY REQUEST != RECOVERY EFFECT

RECOVERY REQUEST
→ RECOVERY CHALLENGE
→ VERIFIED RECOVERY PROOF
→ RECOVERY AUTHORITY
→ RESTORATION / REPLACEMENT EFFECT
→ AUTH METHOD OR SESSION RESULT

### 17.3 Required Recovery Relations

Recovery challenge:

* recovery_id
* user_id or candidate identity
* recovery_type
* challenge_hash
* issued_at
* expires_at
* verified_at
* consumed_at
* failed_attempts
* provenance_ref

A recovery challenge is temporary and proof-bearing.

It is not a persistent method by which a user normally authenticates.

### 17.4 Recovery Authorities

Recovery may require one of:

* existing authenticated session
* verified email
* external provider proof
* recovery token
* human/operator intervention
* governance-approved administrative action

### 17.5 Recovery Effects

Recovery may result in:

* replacement of local password credential
* addition of new authentication method
* restoration of access through new method
* creation of session only after verified recovery authority and explicit session commit
* revocation of compromised methods/sessions

Recovery request alone does not create any effect.

### 17.6 Provider Loss and Method Loss

Loss of Google provider, loss of password, email change and account disable are not automatically recoverable by implementation convenience.

Recovery policy remains HUMAN_AUTHORITY_REQUIRED.

Default unresolved behavior: fail closed.

### 17.7 Product Policy Boundary

Whether self-service recovery is allowed, and what proof level it requires, is HUMAN_AUTHORITY_REQUIRED.

## 18. Revocation Architecture

### 18.1 Revocation Types

* single session logout
* all sessions logout
* credential revocation
* provider unlink
* auth method disable
* account disable
* compromised credential response
* compromised provider response
* recovery challenge revocation
* verification challenge revocation
* OIDC transaction expiry
* OIDC transaction processing failure terminal state
* OIDC transaction completion
* OIDC transaction cancellation/denial terminal state
* PKCE verifier unavailability after transaction terminal state
* initiating user-agent binding invalidation after terminal state
* pre-auth local login-CSRF state invalidation where such mechanism is used

### 18.2 Revocation Propagation

If a credential is revoked:

* dependent sessions must be revoked unless policy explicitly allows survival
* future login with that credential denied
* audit event recorded

If a provider method is unlinked:

* provider login denied
* provider-dependent sessions revoked
* canonical identity remains unless disabled

If account disabled:

* all sessions revoked
* all auth methods blocked
* authorization must fail before business capability

If recovery challenge is revoked:

* challenge cannot restore method or session
* recovery flow must restart

If OIDC transaction is PROCESSING, COMPLETED, FAILED_TERMINAL, CANCELLED_TERMINAL or EXPIRED:

* second callback cannot enter token exchange
* transaction cannot return to PENDING
* associated PKCE verifier becomes unavailable at terminal state
* initiating user-agent binding becomes invalid for the transaction
* transaction replay cannot recover verifier or local effect

### 18.3 Deletion vs Revocation

Deletion is not revocation.

Revocation preserves evidence.

Auth relations should prefer revoked/superseded/terminal state over destructive deletion unless retention policy requires deletion.

## 19. Authentication Effect Gates

### 19.1 Login Effect Gate

CANDIDATE: submitted credential/provider callback.

VALIDATION:

* local password login-CSRF boundary plus password verification
* or OIDC transaction claim + provider proof validation

AUTHORITY:

* credential/provider proof
* active method
* account creation policy where provider subject has no binding

EFFECT GATE:

* canonical identity resolution
* fresh local session creation

COMMIT:

* session row persisted
* cookie emitted/replaced

RE-READ:

* session resolves via `/auth/me` or internal equivalent

RECONSTRUCTION:

* frontend authenticated state resolves from server session

### 19.2 Local Password Login Effect Gate

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH LOCAL SESSION COMMIT

The local password login effect gate must prove:

* hostile cross-site login submission cannot create authenticated session in victim browser
* attacker-selected credentials cannot silently session-swap an unrelated browser context
* successful legitimate login creates fresh authenticated session
* pre-auth state, if used, does not become authenticated session or authorization

### 19.3 Session Creation

Provider success or password success is not enough.

Session creation requires:

* canonical `UserId`
* active auth method or explicit proof provenance
* no account disable
* login-CSRF boundary satisfied for local password browser login
* account creation policy closed where first login creates identity
* fresh persisted session
* cookie set/replaced
* server re-resolves session

### 19.4 Email Verification

Email sent != verified.

Verification commit requires:

* challenge match
* not expired
* not consumed
* attempt boundary satisfied
* verified relation persisted

### 19.5 Account Linking

Provider proof != link commit.

Link commit requires:

* current user authority
* ACCOUNT_LINK OIDC transaction
* transaction bound to initiating user
* transaction bound to initiating user-agent interaction
* transaction atomically claimed before token exchange
* confidential PKCE verifier bound to same transaction
* token exchange using original verifier
* ID Token validation
* nonce validation after trusted ID Token validation
* provider proof
* collision checks
* method relation persisted
* audit event
* re-read methods

### 19.6 Credential Reset

Reset request != reset.

Reset commit requires:

* verified recovery proof
* recovery authority
* new credential hash persisted
* previous credential superseded/revoked
* dependent sessions revoked per policy
* audit event

### 19.7 Recovery Effect Gate

Recovery request != recovery effect.

Recovery flow:

RECOVERY REQUEST
→ RECOVERY CHALLENGE
→ VERIFIED RECOVERY PROOF
→ RECOVERY AUTHORITY
→ RESTORATION / REPLACEMENT EFFECT
→ AUTH METHOD OR SESSION RESULT

### 19.8 Revocation

Revocation request != revoked.

Revocation commit requires:

* authority to revoke
* target method/session exists or no-op semantics defined
* revoked state persisted
* downstream sessions invalidated
* re-read confirms invalidation

### 19.9 OIDC Transaction Effect Gate

OIDC START request != provider proof.

OIDC callback != local effect.

Transaction effect gate:

OIDC START
→ transaction commit in PENDING
→ initiating user-agent binding
→ redirect target validation
→ PKCE verifier confidential binding
→ provider redirect with derived code challenge
→ callback candidate
→ transaction lookup
→ verify transaction exists
→ verify PENDING state
→ validate initiating user-agent binding
→ state validation
→ expiry validation
→ purpose validation
→ initiating-user validation when ACCOUNT_LINK
→ atomic PENDING → PROCESSING claim
→ PKCE verifier retrieval by winner only
→ provider token exchange using authorization code + original verifier
→ token response received
→ ID Token signature validation
→ issuer validation
→ audience validation
→ expiration validation
→ other required ID Token validation
→ nonce claim validation against transaction-bound expected nonce
→ trusted provider subject extraction
→ identity resolution
→ local effect gate
→ terminal transaction state
→ verifier unavailable / unusable
→ re-read / reconstruction

### 19.10 Protocol Callback Effect Gate

OIDC callback GET is a protocol contact, not a general mutation route.

OIDC callback may materialize only:

* transaction validation effects
* initiating user-agent binding validation
* atomic transaction claim
* PKCE verifier access by winning processor
* provider token exchange
* ID Token validation
* nonce validation
* transaction terminal state
* PKCE verifier unavailability
* provider identity proof validation
* account creation boundary effect where policy permits
* provider identity binding
* local session creation
* account link effect
* provider cancel/error projection

It may not materialize arbitrary business commands.

It may not grant Workspace authority.

### 19.11 Local Effect Failure After Provider Proof

If provider proof succeeds but local effect commit fails:

* transaction must not return to PENDING
* transaction must not be replayable
* transaction should enter FAILED_TERMINAL unless the implementation can prove a coherent completed local state
* user-level recovery is a new login/link attempt
* any partially committed local relation must be reconstructable and not silently represented as full success

Prefer atomic local commits where relations are inseparable.

### 19.12 Provider Error / Cancel Effect Gate

Provider error/cancel callback:

* does not enter token exchange
* does not produce trusted provider subject
* does not create canonical identity
* does not create authentication method
* does not create local session
* does not create business effect
* terminalizes transaction safely where transaction can be validated
* projects safe cancelled/denied/error state
* does not leak security-sensitive detail

## 20. Authorization Boundary

### 20.1 Boundary Contract

Authentication may produce only:

* `AuthenticatedPrincipal`
* `ActorIdentity`
* session metadata
* issuer reference
* authentication time
* auth method/proof provenance

Authentication must never produce:

* role
* Workspace membership
* grant
* governance root
* capability
* command approval
* participation authority

### 20.2 Existing Authorization Preservation

Existing `AuthorityResolver`, boundary chains and command handlers remain authoritative for business effects.

Local authentication field already preserved those relations.

### 20.3 Workspace Bootstrap Boundary

Authentication architecture must not close HARD-DEP-001 unless separately authorized.

If self-registration or Google login creates a user, it must not automatically create legitimate Workspace governance root unless the governance bootstrap policy is explicitly approved.

IDENTITY CREATION != GOVERNANCE BOOTSTRAP

IDENTITY CREATION != MEMBERSHIP

MEMBERSHIP != ROLE

ROLE != AUTHORITY

OIDC CALLBACK != BUSINESS AUTHORITY

LOCAL PASSWORD LOGIN != BUSINESS AUTHORITY

## 21. Browser, Cookie and HTTP Security Architecture

### 21.1 Password Security

Preserve:

* PBKDF2-HMAC-SHA256
* per-row random salt
* constant-time digest comparison
* fail-closed malformed hash handling
* no plaintext storage
* no session token in JSON

Potential future upgrade:

* Argon2id or stronger KDF may be chosen if repository dependency policy allows
* migration must support existing hashes by algorithm prefix

### 21.2 Session Cookie Security

Preserve:

* opaque high-entropy token
* DB-stored token hash only
* `HttpOnly` cookie
* `SameSite=Lax`
* secure flag enabled in HTTPS deployment
* revocation check per request
* expiry check per request

Add:

* all-session revocation
* auth-method-scoped session revocation
* account-disable session revocation
* session rotation/replacement after high-risk changes
* optional device/session management

### 21.3 Pre-Auth Correlation Cookie / Binding

If the initiating user-agent binding uses a cookie, that cookie must be:

* transaction-specific or bound to transaction-specific server state
* unpredictable or cryptographically protected where appropriate
* not canonical identity
* not authorization
* not local session
* limited to authentication transaction purpose
* expired/invalid after terminal transaction state
* compatible with OIDC provider redirect behavior

The architecture permits alternate mechanisms that satisfy the same relation.

If local password login-CSRF protection uses pre-auth state:

* it must not become authenticated session
* it must not fix the authenticated session
* it must not become canonical identity
* it must not become authorization
* it must be validated before credential validation can create fresh session
* successful login must create a fresh authenticated session

### 21.4 Cross-Site Callback Behavior

OIDC provider callback crosses from provider to NQUIRY.

Cookie/security settings must not accidentally break legitimate callback delivery.

Cookie/security settings must also not permit callback transplantation to become local authenticated session.

The initiating user-agent binding relation owns that boundary.

### 21.5 Session Fixation Boundary

A successful login or provider callback must create a fresh authoritative session relation and set/replace the authenticated session cookie.

Pre-existing session cookie state must not determine the authenticated identity produced by the new login.

If a browser already has an authenticated session, product behavior for switching accounts is a UX/policy choice, but session identity must be reconstructed from committed server session state after login.

### 21.6 Local Password Login-CSRF Boundary

FIELD: Local Password Login-CSRF Boundary

PURPOSE: prevent hostile cross-site submission of attacker-selected local credentials from authenticating an unrelated victim browser into an attacker-selected account.

Required law:

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH LOCAL SESSION COMMIT

Required non-collapse:

LOGIN REQUEST
!=
LOGIN EFFECT

VALID PASSWORD
!=
PERMISSION FOR AN UNRELATED BROWSER CONTEXT TO BE SILENTLY SESSION-SWAPPED

LOCAL PASSWORD LOGIN CSRF
!=
OIDC CALLBACK CSRF / LOGIN-SWAPPING PROOF

APPLICATION AUTHENTICATED-CSRF BOUNDARY
!=
LOCAL LOGIN-CSRF BOUNDARY

The local password login request occurs before the new authenticated session exists. Therefore the existing rule for unsafe cookie-authenticated application requests does not automatically cover local login.

The implementation may satisfy this boundary through a repository-compatible proven mechanism such as:

* pre-auth CSRF token bound to a pre-auth browser interaction
* strict Origin validation
* Fetch Metadata validation
* a request media-type / same-origin contract that structurally prevents cross-site form submission
* a defensible combination of these mechanisms
* another mechanism that proves the same architectural invariant

CORS alone must not be claimed as sufficient proof.

SameSite alone must not be claimed as sufficient proof.

The actual selected mechanism must be proven against the real browser/API request contract.

### 21.7 CSRF Invariant

NQUIRY uses browser cookies for authentication.

State-changing requests authenticated by cookies require an explicit anti-CSRF boundary.

UNSAFE COOKIE-AUTHENTICATED APPLICATION REQUEST
→ EXPLICIT ANTI-CSRF VALIDATION
→ APPLICATION REQUEST

Implementation may autonomously choose a coherent mechanism such as:

* CSRF token
* Origin validation
* Fetch Metadata
* same-origin enforcement
* a defensible layered combination

provided the mechanism is appropriate to the actual application architecture.

Ordinary safe application requests must not gain business mutation semantics.

CORS must not be treated as a substitute for CSRF protection.

SameSite must not be treated as the sole security boundary.

CSRF failure must be represented as boundary failure, not successful application effect.

Local password login requires its own explicit login-CSRF boundary because it can create a fresh authenticated session before the new session exists.

### 21.8 CSRF and OIDC Callback Relation

APPLICATION CSRF PROOF
!=
OIDC STATE

OIDC state protects the external authorization transaction.

Application anti-CSRF protects unsafe cookie-authenticated application requests.

Local password login-CSRF protection protects unauthenticated login requests that can create a fresh authenticated session.

An OIDC provider callback using a protocol-defined GET contact is governed by:

* OIDC transaction
* initiating user-agent binding
* state
* transaction lifecycle state
* atomic claim
* nonce expected binding
* PKCE verifier binding
* provider token validation
* purpose binding
* terminal transaction state

It is not a generic exemption allowing unsafe application requests without anti-CSRF protection.

Protocol callbacks have their own dedicated anti-forgery proof architecture.

### 21.9 CORS Boundary

CORS must remain explicit and origin-pinned for credentialed browser requests.

CORS != CSRF protection.

CORS alone is not sufficient proof for local password login-CSRF protection.

FALSIFIER: credentialed hostile origin can commit unsafe application request.

FALSIFIER: CORS wildcard permits credentialed hostile origin.

FALSIFIER: CORS is claimed as sufficient local password login-CSRF proof without adversarial browser/API evidence.

### 21.10 XSS

`HttpOnly` protects session token from JavaScript read, but XSS can still perform same-origin actions.

Target:

* maintain no raw token in JSON
* avoid storing auth tokens in localStorage/sessionStorage
* use server-side authorization per request
* keep frontend auth client as projection only
* anti-CSRF boundary still required for unsafe cookie-authenticated application requests
* local password login-CSRF boundary required for local login request
* raw PKCE verifier never reaches frontend JavaScript
* frontend state never becomes authority

### 21.11 OIDC Security

Required:

* OIDC auth transaction field
* explicit transaction lifecycle
* initiating user-agent binding
* redirect target validation
* state validation before atomic claim
* expiry validation before atomic claim
* purpose validation before atomic claim
* ACCOUNT_LINK initiating-user validation before atomic claim
* atomic PENDING → PROCESSING claim before verifier retrieval
* no second callback reaches token exchange
* confidential PKCE verifier retrieval by winner only
* token exchange using original PKCE `code_verifier`
* ID Token signature validation
* issuer validation
* audience validation
* expiration validation
* other required token validation
* nonce validation only after trusted ID Token validation
* PKCE verifier single-transaction binding
* PKCE verifier purpose binding
* PKCE verifier unavailable after transaction terminal state
* PKCE S256
* redirect URI exact allowlist
* transaction expiry
* transaction terminal state
* login transaction cannot become link transaction
* link transaction bound to initiating user
* no implicit flow
* no provider access token in frontend URL
* no provider token stored unless product relation requires it
* no raw PKCE verifier in browser state, logs or proof reports
* uncertain token exchange outcome becomes non-reusable transaction by default
* provider error/cancel produces no local identity/session effect

### 21.12 PKCE Confidentiality Boundary

PKCE verifier confidential material must remain server-side and retrievable for token exchange exactly once by the winning callback processor.

Forbidden:

* storing verifier only as a hash
* exposing verifier to browser JavaScript
* storing verifier in frontend state
* logging verifier
* emitting verifier in proof reports
* retrieving verifier before transaction claim
* retrieving verifier by a losing callback
* reusing verifier after terminal transaction state
* using verifier across transactions
* using LOGIN verifier for ACCOUNT_LINK transaction
* using ACCOUNT_LINK verifier for LOGIN transaction

### 21.13 ID Token Trust Boundary

TOKEN RESPONSE RECEIVED
!=
TRUSTED IDENTITY

ID TOKEN PARSED
!=
VALIDATED ID TOKEN

ID TOKEN SIGNATURE VALID
!=
COMPLETE ID TOKEN VALIDATION

Nonce and subject claims must not enter the NQUIRY identity Field as trusted input until required ID Token validation has succeeded.

### 21.14 Protocol Callback Security Boundary

OIDC callback GET is a protocol response contact.

It may perform only protocol-defined security and identity effects after all proof gates pass.

It may not:

* perform arbitrary business commands
* grant Workspace authority
* bypass authorization
* bypass account creation policy
* bypass account linking authority
* bypass initiating user-agent binding
* bypass transaction claim
* bypass replay resistance
* create general GET mutation semantics

### 21.15 Redirect Security Boundary

Redirect target validation must ensure:

* no arbitrary hostile origin receives post-auth navigation
* no sensitive authorization artifacts are forwarded to untrusted origins
* provider redirect URI registration is separate from application post-auth redirect target
* error/cancel redirects are also validated
* recovery redirects are validated where present

### 21.16 Rate Limiting and Enumeration

Current unknown email and wrong password collapse to identical exception and constant-effort hash.

Add:

* IP/user/email-keyed rate limits
* lockout/step-up policy
* audit security events
* ensure login, verification, recovery and provider callbacks do not disclose account existence beyond necessary boundaries

### 21.17 Secret and Protocol Material Management

Required secrets / protocol-sensitive materials:

* cookie/session secrets if introduced
* Google client ID/secret
* provider redirect URIs
* OIDC state expected binding
* OIDC nonce expected binding
* initiating user-agent binding secret/seal if used
* local login-CSRF token/secret if selected mechanism uses one
* confidential PKCE verifier storage key if encryption/sealing used
* email provider credentials
* recovery token secret if HMAC-signing challenges
* CSRF secret if chosen mechanism requires one

Do not leak into browser-visible application state, logs, audit payloads, proof reports, error messages or frontend telemetry unless the protocol necessarily carries the value through browser redirect flow.

State and nonce may travel through browser protocol flow as defined by OAuth/OIDC. Their authoritative expected values or protected bindings remain server-side, and they must not be unnecessarily logged or emitted into review evidence.

Raw PKCE `code_verifier`, raw client secret, raw provider access token, raw provider refresh token, raw local session token and raw recovery token must not appear in browser-visible application state, logs, audit payloads, proof reports, error messages or frontend telemetry.

### 21.18 DB Principal Boundary

Known limitation: auth tables were not integrated into DB-principal capability mapping in the local auth migration.

Target:

* extend runtime DB-principal discipline consistently
* avoid partial security hardening that only covers new auth tables while leaving existing live HTTP path unscoped
* runtime service identity receives only the database capabilities legitimately required for authentication persistence operations
* existing live authentication persistence and newly introduced authentication persistence follow the same runtime-principal discipline
* bootstrap/test DB authority is not represented as production runtime authority
* DB principal capability is explicit and testable

Ownership: WU-AUTH-17 Runtime DB Principal Capability Boundary.

## 22. Persistence Architecture

### 22.1 Preserve Existing Tables

Preserve:

* `users`
* `local_auth_credentials`
* `local_auth_sessions`

Do not destructively migrate without compatibility plan.

### 22.2 New Tables / Relations

Minimum target additions:

`authentication_methods`

* id
* user_id
* method_type
* status
* created_at
* revoked_at
* provenance_ref

`external_provider_identities`

* id
* authentication_method_id
* provider_issuer
* provider_subject
* provider_email
* provider_email_verified
* linked_at
* revoked_at

`oidc_auth_transactions`

* transaction_id
* provider
* transaction_state
* state_hash or equivalent expected-state binding
* nonce_hash or equivalent expected-nonce binding
* initiating_user_agent_binding_ref or equivalent
* confidential_pkce_verifier_ref or encrypted/sealed verifier value
* pkce_code_challenge metadata where useful
* post_auth_redirect_target_ref or safe named destination
* purpose: LOGIN or ACCOUNT_LINK
* initiating_user_id nullable for LOGIN, required for ACCOUNT_LINK
* created_at
* expires_at
* claimed_at
* completed_at
* failed_terminal_at
* expired_at
* cancelled_at nullable
* verifier_unavailable_at or equivalent
* failure_reason nullable
* provenance_ref

`verified_emails`

* id
* user_id
* email
* verified_at
* revoked_at
* superseded_at

`auth_challenges`

* id
* challenge_type
* user_id nullable
* email nullable
* token_hash
* issued_at
* expires_at
* consumed_at
* failed_attempts

`recovery_challenges`

* id
* user_id or candidate identity
* recovery_type
* challenge_hash
* issued_at
* expires_at
* verified_at
* consumed_at
* failed_attempts
* provenance_ref

`auth_events`

* id
* user_id nullable
* event_type
* method_id nullable
* session_id nullable
* transaction_id nullable
* occurred_at
* issuer_ref
* provenance

Optional after policy:

* `account_recovery_cases`
* `account_link_events`
* `session_metadata`
* `auth_rate_limits`
* `account_creation_events`
* `csrf_tokens` or equivalent anti-CSRF proof storage if chosen mechanism requires persistence
* local login-CSRF proof state where selected mechanism requires persistence

### 22.3 Constraints

Required constraints:

* provider issuer + subject unique
* local password method one active credential per method
* no active method without canonical user
* no session without canonical user
* no verified email duplication policy violation
* challenge token hash unique
* recovery challenge hash unique
* session token hash unique
* OIDC transaction state hash unique within active transactions
* OIDC transaction can transition PENDING → PROCESSING at most once
* PROCESSING can never return to PENDING
* terminal states cannot be claimed
* ACCOUNT_LINK transaction requires initiating user
* LOGIN transaction must not contain link-only effect
* terminal OIDC transaction cannot produce local effect through replay
* PKCE verifier reference/value cannot be reused across transactions
* PKCE verifier must become unavailable after transaction terminal state
* verifier from one transaction cannot satisfy another transaction
* verifier retrieval requires PROCESSING state owned by winning callback processor
* initiating user-agent binding expires with transaction
* initiating user-agent binding is invalid after terminal state
* local login-CSRF proof state, if persisted, cannot become authenticated session
* local login-CSRF proof state, if persisted, cannot become canonical identity or authorization

### 22.4 Migration Compatibility

Existing local credentials must map to LOCAL_PASSWORD auth methods.

Existing local sessions should either:

* continue until expiry using current table fields
* or migrate into expanded session model with compatibility view/repository

No existing legitimate authorization semantics may be invalidated by auth migration.

### 22.5 Recovery Persistence Boundary

Recovery challenge persistence is not auth method persistence.

It must not appear in authentication method list.

It must not authenticate normally.

It only supports recovery authority after verification.

### 22.6 PKCE Persistence Boundary

PKCE verifier confidential material must be stored or referenced in a recoverable confidential server-side form until the winning transaction processor performs token exchange or the transaction reaches terminal state.

Hash-only storage is insufficient.

After terminal state, verifier must become unavailable / unusable.

Do not persist raw verifier in logs, proof evidence or client-visible state.

### 22.7 Transaction Claim Persistence Boundary

The atomic `PENDING → PROCESSING` claim must be enforced by authoritative state, not process-local memory.

Valid implementation mechanisms may include conditional update, row lock, compare-and-swap, transactional state transition or another repository-compatible atomic mechanism.

The architecture requires semantics, not a specific mechanism.

### 22.8 Redirect Target Persistence Boundary

Redirect target candidate must not persist as unvalidated authority.

Persist or bind only:

* safe relative destination
* named internal destination
* allowlisted local destination
* or equivalent validated local target

Arbitrary absolute attacker URLs must not become committed redirect targets.

### 22.9 Runtime DB Principal Persistence Boundary

Runtime database principal capability does not add new domain truth.

It changes which runtime database principal is legitimately capable of performing existing and newly introduced authentication persistence operations.

Authentication persistence operations must be executable by the legitimate scoped runtime principal and rejected when attempted outside that capability boundary.

The repair covers the live persistence path, not merely newly added tables.

## 23. API Architecture

### 23.1 Preserve Existing API

Preserve:

* `POST /auth/login`
* `POST /auth/logout`
* `GET /auth/me`

Do not break frontend without compatibility.

### 23.2 Add Provider API

Semantic API contacts:

* start Google login
* Google callback
* list authentication methods
* start account link
* provider link callback
* unlink authentication method
* start email verification
* complete email verification
* start password reset
* complete password reset
* revoke session
* revoke all sessions

Exact route names are implementation-autonomous.

### 23.3 Local Login API Semantics

`POST /auth/login` must remain a local password authentication contact.

Before credential validation can create a fresh session, the route must satisfy the local password login-CSRF boundary.

The selected mechanism may be:

* pre-auth CSRF token bound to browser interaction
* strict Origin validation
* Fetch Metadata validation
* request media-type / same-origin contract
* defensible combination
* equivalent proven mechanism

The actual HTTP/browser request contract must prove:

* legitimate same-origin login succeeds
* hostile cross-site submission fails before fresh session commit
* attacker-selected credential login attempt against victim browser fails
* successful legitimate login creates fresh session
* pre-existing or pre-auth state does not become authenticated session

### 23.4 Add OIDC Start API Semantics

Provider start endpoint must:

* validate redirect target candidate
* create OIDC transaction in PENDING
* create initiating user-agent binding
* generate state
* generate nonce
* generate PKCE `code_verifier`
* create confidential server-side verifier binding
* derive code challenge for provider request
* bind purpose
* bind initiating user when ACCOUNT_LINK
* return redirect or redirect response to provider

### 23.5 Add OIDC Callback API Semantics

Provider callback endpoint may use GET as protocol response contact.

Provider callback endpoint must handle both success and non-success callback forms.

Successful callback path must:

* load transaction
* verify transaction exists
* verify transaction state is PENDING
* validate initiating user-agent binding
* validate returned state
* validate transaction expiry
* validate transaction purpose
* validate initiating user when ACCOUNT_LINK
* atomically claim transaction PENDING → PROCESSING
* retrieve original PKCE `code_verifier` confidentially
* exchange authorization code using original `code_verifier`
* validate token response and ID Token
* validate nonce claim after ID Token validation
* extract trusted provider subject
* continue to identity/link/account creation effect gate
* finalize transaction terminal state
* make verifier unavailable / unusable
* redirect only to legitimate local destination

Provider error/cancel path must:

* load transaction where possible
* validate initiating user-agent binding where possible
* validate state where protocol provides it
* validate transaction state/expiry where possible
* terminalize safely where appropriate
* make verifier unavailable / unusable
* perform no token exchange
* create no identity/session/business effect
* project safe cancelled/denied/error state
* redirect only to legitimate local destination

### 23.6 Account Creation Boundary API Semantics

Unknown provider subject must not implicitly create a user.

Callback must either:

* resolve existing binding
* invoke established account creation policy
* fail closed with denied/unavailable boundary

### 23.7 Anti-CSRF API Boundary

All unsafe cookie-authenticated ordinary application methods must pass explicit anti-CSRF validation before application request execution.

Local password login must pass explicit login-CSRF boundary validation before credential validation can create a fresh authenticated session.

CORS is not a substitute.

SameSite is not sole security boundary.

OIDC callback protocol validation is distinct from application CSRF validation.

Local password login-CSRF validation is distinct from OIDC callback validation and authenticated-request CSRF validation.

### 23.8 HTTP Method Law

ORDINARY SAFE APPLICATION REQUESTS
MUST NOT ACQUIRE BUSINESS MUTATION SEMANTICS.

PROTOCOL CALLBACKS MAY MATERIALIZE ONLY THEIR
PROTOCOL-DEFINED SECURITY / IDENTITY EFFECTS
THROUGH THEIR DEDICATED PROOF AND EFFECT GATES.

An OIDC callback GET route does not authorize arbitrary GET mutation.

### 23.9 Response Shape

Auth APIs must return discriminated boundary shapes:

* `ok`
* `denied`
* `rejected`
* `cancelled`
* `unavailable`
* `unknown` only where unavoidable

They must not return raw session token in JSON.

They must not return raw PKCE verifier, raw recovery token, provider access token, provider refresh token, authorization code or client secret in JSON.

State and nonce must not be unnecessarily exposed outside protocol-defined flow.

### 23.10 HTTP Adapter Law

HTTP adapter remains thin:

* parse request
* validate local login-CSRF boundary for local password login
* validate anti-CSRF for unsafe cookie-authenticated ordinary application requests
* validate protocol callback through OIDC transaction pipeline where route is an OIDC callback
* call application dispatch / auth application service
* set/clear/replace cookie
* translate status code
* no business logic
* no authority decision

## 24. Frontend Contact Architecture

### 24.1 Current Frontend

Current login page is a real email/password form and redirects only after server success.

Current auth client uses `credentials: "include"` and computes no authority.

### 24.2 Target Login Surface

Frontend may expose:

* local email/password login if enabled
* Google login if configured
* future Microsoft/GitHub if product-approved
* recovery links if recovery architecture exists

Frontend must not expose:

* provider button with missing backend config
* mock provider as production
* self-registration unless approved
* account linking without authenticated session and backend capability
* account creation success from unknown Google subject unless account creation policy is established
* raw PKCE verifier
* raw provider access token
* raw provider refresh token
* local session token
* unvalidated redirect targets

### 24.3 Frontend Auth State

Frontend state is projection only.

Allowed local state:

* email/password form values
* loading state
* selected provider
* error message
* redirect target candidate before backend validation
* safe error/cancel display
* local login-CSRF candidate material where selected mechanism requires it and where safe

Forbidden local truth:

* logged-in identity
* provider proof
* OIDC transaction validity
* initiating user-agent binding validity
* PKCE verifier
* session validity
* Workspace membership
* role
* capability
* account creation policy result
* token response identity claims
* redirect target legitimacy
* login-CSRF proof as identity or authority

### 24.4 Local Login Frontend Contact

The local login frontend must participate in the selected login-CSRF boundary mechanism where the mechanism requires frontend participation.

The frontend may submit login candidates.

It must not decide:

* credential validity
* session commit
* login-CSRF boundary success
* canonical identity
* authorization

### 24.5 Account Security Surface

Target UI contacts:

* list linked methods
* add Google
* remove method
* verify email
* reset password
* revoke sessions
* show last login/audit evidence where safe

### 24.6 Error / Cancel Projection

Frontend may display:

* user cancelled provider login
* provider denied login
* provider unavailable
* authentication failed
* account creation unavailable
* account link collision
* recovery failed
* expired session
* logged out
* login request rejected by security boundary

Frontend must not display:

* raw provider error details that leak protocol/security material
* raw state
* raw nonce
* raw code
* raw verifier
* raw tokens
* account existence distinctions where enumeration-sensitive

### 24.7 CSRF Frontend Contact

Frontend must participate in the chosen anti-CSRF mechanism for unsafe cookie-authenticated ordinary application requests.

Frontend must also participate in the chosen local password login-CSRF mechanism where required by that mechanism.

Implementation may choose mechanism, but unsafe state-changing UI requests must carry or satisfy anti-CSRF proof, and local password login requests must satisfy local login-CSRF proof.

OIDC provider callback is not a normal frontend-originating unsafe application request. It is a protocol response contact governed by OIDC transaction validation.

## 25. Runtime and Configuration Architecture

### 25.1 Current Runtime

Docker Compose starts Postgres, API, worker and web; web runs Next.js; API runs FastAPI; browser talks to API at `localhost:8000`.

### 25.2 Required Configuration

For target:

* `NQUIRY_COOKIE_SECURE`
* `NQUIRY_COOKIE_DOMAIN` if needed
* `NQUIRY_ALLOWED_ORIGINS`
* `NQUIRY_GOOGLE_CLIENT_ID`
* `NQUIRY_GOOGLE_CLIENT_SECRET`
* `NQUIRY_GOOGLE_REDIRECT_URI`
* `NQUIRY_AUTH_PROVIDER_MODE`
* `NQUIRY_ACCOUNT_CREATION_POLICY`
* `NQUIRY_PKCE_VERIFIER_STORAGE_MODE` or equivalent if implementation requires explicit configuration
* `NQUIRY_PKCE_VERIFIER_SEALING_KEY` or equivalent if verifier storage uses sealing/encryption
* `NQUIRY_PREAUTH_BINDING_MODE` or equivalent if implementation requires explicit configuration
* `NQUIRY_LOCAL_LOGIN_CSRF_MODE` or equivalent if local login-CSRF mechanism needs configuration
* `NQUIRY_CSRF_MODE` or equivalent anti-CSRF configuration if mechanism needs configuration
* email provider config if email verification/recovery enabled
* rate-limit config
* session lifetime config if policy-approved
* runtime DB principal / database role configuration where repository architecture requires it

### 25.3 Environment Boundaries

Development mode may use:

* local password adapter
* fake provider
* local email sink
* localhost insecure cookie
* explicit test account creation policy for test only
* bootstrap/test DB authority for test-only workflows when explicitly marked

Production-like mode must require:

* HTTPS
* secure cookies
* real provider config
* no fake provider
* no default demo credential
* no non-proof bootstrap represented as proof
* explicit account creation policy
* anti-CSRF boundary for unsafe cookie-authenticated ordinary application requests
* local login-CSRF boundary for local password login
* confidential server-side PKCE verifier handling
* authoritative transaction claim semantics
* initiating user-agent binding semantics
* safe redirect target validation
* scoped runtime DB-principal capability for live authentication persistence

## 26. Provider Abstraction

### 26.1 Provider Port

Define an external provider port conceptually:

* start_auth
* exchange_code_with_verifier
* validate_token_response
* validate_id_token
* normalize_verified_credential
* normalize_provider_error
* provider_issuer
* provider_subject
* provider_email attributes

### 26.2 Provider Adapter

Google adapter owns:

* OIDC discovery/static metadata
* auth URL
* token exchange with original PKCE `code_verifier`
* ID Token validation
* provider error/cancel normalization
* claim normalization after validation

It does not own:

* OIDC transaction persistence
* OIDC transaction exclusive claim
* initiating user-agent binding
* redirect target validation
* PKCE verifier lifecycle outside provider token exchange
* canonical identity
* account creation policy
* Workspace membership
* role
* governance
* capability

### 26.3 Identity Resolver

NQUIRY identity resolver owns:

* map provider credential to user
* enforce account creation policy
* enforce linking/collision policy
* create/deny auth method relation
* create local session after commit

### 26.4 Replacement Boundary

A provider adapter can be replaced if it produces the same verified external credential relation.

Provider replacement may not change:

* account linking policy
* account creation policy
* canonical identity model
* authorization boundary
* session semantics
* recovery semantics
* initiating user-agent binding semantics
* PKCE verifier confidentiality semantics
* OIDC transaction semantics
* ID Token trust boundary
* transaction claim semantics
* redirect target validation semantics

## 27. Development and Test Provider Boundary

### 27.1 Mock Provider

A mock/fake provider may exist only in test/development.

It must be:

* clearly marked TEST_PROVIDER
* impossible in production config
* unable to produce production proof
* covered by tests that prove production config rejects it

### 27.2 Provider Sandbox / Test Account

Provider sandbox/test account is closer to real provider proof than mock, but still not production proof.

### 27.3 Real Provider Flow

Real Google proof requires:

* real redirect
* real callback
* real transaction creation in PENDING
* real initiating user-agent binding
* real PKCE verifier confidential binding
* real state validation
* real expiry validation
* real purpose validation
* real atomic PENDING → PROCESSING claim
* real PKCE verifier retrieval by winner
* real token exchange using original verifier
* real ID Token validation
* real nonce validation after ID Token validation
* real provider subject
* local identity binding or account creation boundary
* fresh session creation
* cookie replacement/set
* logout
* linking/collision handling
* provider cancel/error handling

### 27.4 Secret Evidence Boundary

Proof reports must not expose secrets.

They may show:

* redacted config presence
* provider issuer
* callback success
* provider cancel/error behavior
* subject hash/pseudonym
* transaction id hash/pseudonym
* state/nonce mismatch tests
* PKCE verifier redaction evidence
* transaction claim evidence
* initiating user-agent binding evidence
* redirect validation evidence
* local login-CSRF boundary evidence
* scoped DB-principal capability evidence
* local session creation

They must not show:

* raw PKCE verifier
* raw authorization code
* raw provider access token
* raw provider refresh token
* raw local session token
* raw recovery token
* client secret
* raw local login-CSRF secret/token if sensitive

State and nonce may pass through browser protocol flow, but they must not be unnecessarily logged or emitted into review evidence.

## 28. Migration Architecture

### 28.1 Existing Development Users

Existing local demo users must migrate without being represented as production-proof identities.

`NonProofWorkspaceBootstrap` remains non-proof.

Authentication does not make Workspace bootstrap legitimate.

### 28.2 Existing Local Credentials

Existing `local_auth_credentials` rows should become LOCAL_PASSWORD authentication methods.

Migration must preserve:

* password hash
* user link
* created/updated timestamps where available
* no plaintext password requirement

### 28.3 Existing Sessions

Existing sessions may continue under current validation until expiration, or migrate to extended session model.

Do not invalidate current sessions unexpectedly unless migration explicitly chooses a security boundary.

### 28.4 OIDC Transaction Migration

No existing OIDC transaction relation exists.

New OIDC transaction persistence starts empty.

### 28.5 PKCE Verifier Migration

No existing PKCE verifier binding exists.

New confidential PKCE verifier handling starts with OIDC implementation.

No legacy data can be treated as PKCE verifier material.

### 28.6 Initiating User-Agent Binding Migration

No existing initiating user-agent binding exists.

New binding starts with OIDC implementation.

No existing browser state can be treated as proof of initiating interaction.

### 28.7 Local Login-CSRF Boundary Migration

No existing local login-CSRF boundary proof is established by architecture.

The selected mechanism starts with the local password login-CSRF implementation.

No existing frontend form behavior, SameSite configuration or CORS configuration may be represented as sufficient proof without adversarial browser/API evidence.

### 28.8 Runtime DB Principal Migration

Runtime DB-principal capability boundary must be applied after authentication persistence shape is sufficiently materialized.

Existing live authentication persistence and newly introduced authentication persistence must be treated consistently.

Bootstrap/test database authority must not be represented as production runtime authority.

### 28.9 Rollback

Rollback must preserve ability to authenticate local demo users or clearly require session invalidation.

Rollback must not expose PKCE verifier material or leave claimed/terminal transactions replayable.

Rollback must not leave validated redirect targets replaced by arbitrary redirect candidates.

Rollback must not silently restore an over-broad runtime DB principal in production-like mode while claiming scoped runtime capability.

### 28.10 Test Fixture Migration

Test fixtures must distinguish:

* production proof
* provider sandbox proof
* test provider proof
* recovery proof
* non-proof bootstrap
* OIDC transaction proof
* initiating user-agent binding proof
* local login-CSRF proof
* PKCE confidential verifier proof without revealing verifier
* transaction claim proof
* redirect target validation proof
* runtime DB-principal capability proof

## 29. Responsive / UI Semantic Contact where relevant

Authentication UI semantics are simple but still Field-bound:

* login form projects candidate credential, not identity
* submitting projects request, not commit
* local login-CSRF material projects request eligibility, not identity
* provider start projects request, not provider proof
* provider callback projects callback candidate, not session
* provider cancel projects cancellation candidate, not local effect
* server success projects session commit candidate
* `/auth/me` confirms session state
* Workspace content appears only after session reconstruction
* provider buttons project available methods only if backend config says available
* first provider login cannot display account-created success unless account creation policy committed
* frontend never sees PKCE verifier
* frontend never treats token response or ID Token claims as identity source
* frontend never decides redirect target legitimacy
* frontend never decides runtime DB-principal capability

Responsive layout may transform presentation but must not hide:

* primary login method
* recovery path if recovery is enabled
* provider boundary label where required
* error state
* cancel state
* account creation denied/unavailable boundary where relevant

## 30. Accessibility Contact where relevant

Authentication surfaces must provide:

* explicit labels for email/password
* keyboard-operable submit
* provider buttons as semantic buttons/links
* error messages with `role="alert"` or equivalent
* no prefilled demo credentials in production-like UI
* non-color failure meaning
* provider cancel/error messages readable by screen readers
* recovery flows readable by screen readers
* focus movement after redirect or error
* accessible indication when account creation is unavailable
* accessible indication when recovery proof is required

The current login page already labels email/password inputs and uses `role="alert"` for error.

## 31. Audit, Evidence and Provenance

### 31.1 Required Audit Events

Record:

* login success
* login failure aggregated safely
* local login-CSRF boundary failure where security-relevant
* logout
* session created
* session replaced/rotated where applicable
* session revoked
* all sessions revoked
* provider login start
* OIDC transaction created
* initiating user-agent binding created
* initiating user-agent binding failed
* OIDC transaction claimed for processing
* OIDC transaction completed
* OIDC transaction failed terminal
* OIDC transaction expired
* OIDC transaction cancelled/denied terminal
* OIDC transaction replay rejected
* PKCE verifier consumed/unavailable without exposing value
* token exchange rejected
* token exchange outcome uncertain
* ID Token validation failed
* nonce validation failed
* redirect target rejected
* provider login success/failure
* provider link success/failure
* provider unlink
* account creation denied/unavailable
* account creation committed where policy allows
* email verification issued/completed/failed
* recovery issued/completed/failed
* password reset
* auth method disabled
* account disabled
* anti-CSRF failure where security-relevant
* protocol callback security failure where relevant
* runtime DB-principal capability violation where security-relevant

### 31.2 Provenance

Every material authentication relation should have provenance:

* issuer
* method
* time
* user where known
* challenge/session/method id
* OIDC transaction id
* transaction lifecycle state
* initiating user-agent binding id/ref where safe
* local login-CSRF proof class where relevant
* runtime DB principal / database role evidence where relevant
* proof class
* environment class

### 31.3 Privacy

Audit must not record:

* raw passwords
* raw session tokens
* raw recovery tokens
* raw PKCE verifier
* raw authorization code
* provider access tokens
* provider refresh tokens
* client secret
* full secret values
* unnecessary provider claims
* sensitive login-CSRF token/secret values

State and nonce may travel through browser redirect flow according to protocol. Do not falsely classify them as values that never pass through the browser. They must still not be unnecessarily logged or emitted into review evidence.

### 31.4 Evidence Redaction

Proof reports may include:

* evidence that verifier was generated
* evidence that transaction was claimed
* evidence that verifier was available only after claim
* evidence that verifier was used for token exchange
* evidence that verifier became unavailable after terminal state
* evidence that wrong verifier fails
* evidence that replay fails
* evidence that nonce validation occurs after ID Token validation
* evidence that user-agent binding prevents callback transplantation
* evidence that redirect target validation blocks hostile origins
* evidence that local password login-CSRF boundary blocks hostile-origin login
* evidence that scoped DB principal permits legitimate auth persistence and rejects unauthorized operations

Proof reports must not include the verifier value, raw code, tokens, client secret or sensitive local login-CSRF secret/token.

## 32. Error and Boundary Semantics

### 32.1 Login Failure

Current denied shape for invalid credentials remains correct.

Do not distinguish unknown email vs wrong password in user-visible response.

Local login-CSRF boundary failure must not be represented as successful login or credential failure. It is a security/request-boundary failure.

### 32.2 Provider Failure Classes

Internal evidence must distinguish at least:

* MISSING_TRANSACTION
* EXPIRED_TRANSACTION
* INVALID_STATE
* USER_AGENT_BINDING_MISSING
* USER_AGENT_BINDING_MISMATCH
* PURPOSE_MISMATCH
* INITIATING_USER_MISMATCH
* ALREADY_PROCESSING
* ALREADY_COMPLETED
* CANCELLED_TERMINAL
* FAILED_TERMINAL
* MISSING_PKCE_VERIFIER
* TOKEN_EXCHANGE_REJECTED
* TOKEN_EXCHANGE_OUTCOME_UNCERTAIN
* INVALID_ID_TOKEN_SIGNATURE
* INVALID_ISSUER
* INVALID_AUDIENCE
* EXPIRED_ID_TOKEN
* INVALID_NONCE
* PROVIDER_SUBJECT_MISSING
* PROVIDER_SUBJECT_COLLISION
* PROVIDER_ACCESS_DENIED
* USER_CANCEL
* PROVIDER_FAILURE
* MALFORMED_CALLBACK
* REDIRECT_TARGET_REJECTED
* ACCOUNT_CREATION_POLICY_UNRESOLVED
* ACCOUNT_LINK_AUTHORITY_FAILURE
* LOCAL_EFFECT_FAILURE

Exact public error messages may collapse security-sensitive distinctions.

Internal evidence must preserve enough provenance for diagnosis without exposing secrets.

### 32.3 Provider Failure Semantics

Provider failures:

* missing transaction → rejected/security boundary
* invalid state → rejected/security boundary
* missing/mismatched user-agent binding → rejected/security boundary
* expired transaction → rejected/security boundary
* already processing → rejected/security boundary
* already completed → rejected/security boundary
* cancelled terminal → rejected/security boundary
* failed terminal → rejected/security boundary
* consumed transaction replay → rejected/security boundary
* invalid nonce → rejected/security boundary after token validation
* missing/unretrievable PKCE verifier → rejected/security boundary
* invalid PKCE / token exchange failure → rejected/security boundary
* uncertain token exchange outcome → FAILED_TERMINAL and new authentication flow required
* invalid ID Token signature → rejected/security boundary
* invalid issuer → rejected/security boundary
* invalid audience → rejected/security boundary
* expired ID Token → rejected/security boundary
* provider access denied → cancelled/denied projection, no token exchange, no local effect
* user cancel → cancelled projection, no token exchange, no local effect
* provider unavailable → failed dependency
* provider subject already linked → rejected collision
* email collision → boundary requiring link/recovery flow
* unknown provider subject with no account creation policy → unavailable/denied account creation boundary
* local effect failure → non-replayable transaction and reconstructable local boundary

### 32.4 Session Failure

Missing, expired, revoked, forged and unknown sessions should collapse to unauthenticated for public HTTP response, while internally auditable at appropriate level.

### 32.5 Authorization Failure

Authenticated but unauthorized must remain distinct from unauthenticated.

A logged-in user without membership must receive authorization boundary, not login boundary.

### 32.6 CSRF Failure

CSRF failure must be boundary/security failure.

It must not reach application command execution.

It must not be represented as successful application effect.

### 32.7 Local Login-CSRF Failure

Local login-CSRF failure must be boundary/security failure.

It must not reach credential-validation-to-session-commit effect.

It must not be represented as successful authentication.

It must not leak account existence or credential validity.

### 32.8 Redirect Failure

Invalid redirect target must fail to safe local default or rejected boundary.

Invalid redirect target must not:

* send browser to hostile origin
* preserve sensitive protocol artifacts
* convert into successful auth effect

### 32.9 Runtime DB Principal Failure

DB-principal capability failure must be represented as infrastructure/security boundary failure.

It must not be treated as successful persistence effect.

It must not silently fall back to over-broad bootstrap authority in production-like runtime.

### 32.10 Protocol Callback Failure

OIDC callback failure must be protocol/security boundary.

It must not become business mutation.

It must not be retried by replaying claimed or terminal transaction.

It must not leak raw verifier, authorization code or token.

## 33. Concurrency Architecture

### 33.1 Concurrent Login

Multiple sessions per user currently allowed; preserve unless policy changes.

### 33.2 Two Login Starts Same Browser

Two login starts in the same browser must remain distinguishable by transaction and initiating user-agent binding.

Valid behavior may be:

* newest transaction supersedes prior local browser binding
* multiple concurrent pre-auth transactions coexist safely
* older callback fails due to binding/state/transaction policy

Implementation may choose, but no callback may authenticate through ambiguous browser binding.

### 33.3 Two Login Starts Different Browsers/Tabs

Transactions must remain independent.

Callback for one initiating user-agent interaction must not satisfy another.

### 33.4 Concurrent Local Password Login Attempts

Concurrent local password login attempts must not cause pre-auth local login-CSRF state to become authenticated session state.

If a pre-auth mechanism is selected, concurrent attempts must terminate at authoritative state and must not fix or reuse authenticated session identity.

### 33.5 Concurrent Link

Account linking must guard against races:

* provider subject unique constraint
* transaction around collision check and insert
* idempotent callback handling where safe
* transaction lifecycle state
* ACCOUNT_LINK transaction bound to initiating user
* ACCOUNT_LINK transaction bound to initiating user-agent interaction
* PKCE verifier bound to same ACCOUNT_LINK transaction

### 33.6 Concurrent OIDC Callback

Parallel callbacks for the same transaction must result in only one successful claim.

Required behavior:

* first valid callback performs local validation
* first valid callback atomically transitions PENDING → PROCESSING
* only winner retrieves verifier
* only winner enters token exchange
* second callback observes PROCESSING, COMPLETED, FAILED_TERMINAL, CANCELLED_TERMINAL or EXPIRED
* second callback fails closed
* no duplicate session/link/account creation effect

NQUIRY must not depend on provider authorization-code reuse rejection for this invariant.

### 33.7 Concurrent Recovery

Recovery challenge consumption must be atomic.

A consumed recovery token cannot be replayed.

### 33.8 Concurrent Revocation

Revocation must win against session validation as soon as committed.

Session validation checks DB state per request, so this fits current server-side model.

### 33.9 Concurrent Account Creation

Unknown provider subject with approved account creation policy must still protect against races:

* provider issuer + subject unique
* account creation event transactionally paired with provider binding where required
* duplicate callback cannot create duplicate users
* account creation policy must be evaluated inside effect gate
* local effect boundaries must be coherent and reconstructable

### 33.10 Concurrent PKCE Verifier Use

PKCE verifier use must be single-processor.

A verifier can be retrieved only by the callback processor that won the atomic claim.

A losing callback must never retrieve a usable verifier.

A verifier from one transaction must not satisfy another transaction.

A verifier from LOGIN transaction must not satisfy ACCOUNT_LINK transaction.

### 33.11 Concurrent Verification and Recovery Tokens

Verification and recovery tokens must be single-use.

Parallel completions must result in one success at most.

Terminal/consumed challenges cannot be replayed.

## 34. System Field Engineering Laws

### 34.1 Field Law

FIELD + RELATION + STATE + DELTA + BOUNDARY + AUTHORITY + RECONSTRUCTION

### 34.2 Authentication Field Law

Authentication Field resolves identity proof into canonical identity session.

It does not create Workspace authority.

### 34.3 Non-Collapse Law

AUTHENTICATION != AUTHORIZATION

EMAIL != IDENTITY

EMAIL EQUALITY != IDENTITY EQUIVALENCE

EXTERNAL PROVIDER SUBJECT != CANONICAL NQUIRY IDENTITY

AUTHENTICATION METHOD != RECOVERY PROOF

OIDC TRANSACTION != PROVIDER IDENTITY

AUTHORIZATION CODE != AUTHENTICATED IDENTITY

TOKEN RESPONSE != TRUSTED IDENTITY

PARSED ID TOKEN != VALIDATED ID TOKEN

NONCE EXPECTATION != NONCE VALIDATION

PKCE VERIFIER != PKCE VERIFIER HASH

PROVIDER CALLBACK != LOCAL COMMIT

PROVIDER PROOF != LOCAL COMMIT

LOCAL PASSWORD LOGIN REQUEST != LOGIN EFFECT

VALID PASSWORD != PERMISSION FOR AN UNRELATED BROWSER CONTEXT TO BE SILENTLY SESSION-SWAPPED

LOCAL PASSWORD LOGIN CSRF != OIDC CALLBACK CSRF / LOGIN-SWAPPING PROOF

APPLICATION AUTHENTICATED-CSRF BOUNDARY != LOCAL LOGIN-CSRF BOUNDARY

IDENTITY CREATION != MEMBERSHIP

MEMBERSHIP != ROLE

ROLE != AUTHORITY

SESSION != AUTHORIZATION

LOGIN != ACCOUNT CREATION

ACCOUNT LINK != EMAIL EQUALITY

LOGIN TRANSACTION != ACCOUNT_LINK TRANSACTION

PENDING != PROCESSING

PROCESSING != COMPLETED

RETRY != RECOVERY

APPLICATION CSRF PROOF != OIDC STATE

OIDC STATE != APPLICATION CSRF PROOF

SAFE APPLICATION GET != BUSINESS MUTATION

PROTOCOL CALLBACK GET != GENERAL GET MUTATION AUTHORITY

REQUEST != COMMIT

CANDIDATE != EFFECT

VALID OIDC STATE != VALID INITIATING USER-AGENT RELATION

TRANSFERRED CALLBACK != LEGITIMATE LOGIN CONTINUATION

OIDC PROVIDER REDIRECT URI != POST-AUTH APPLICATION REDIRECT TARGET

BOOTSTRAP/TEST DATABASE AUTHORITY != PRODUCTION RUNTIME AUTHORITY

### 34.4 Effect Law

REQUEST != COMMIT

CANDIDATE != EFFECT

LOCAL PASSWORD LOGIN REQUEST != LOGIN EFFECT

AUTHORIZATION CODE RECEIVED != AUTHENTICATED IDENTITY

TOKEN RESPONSE RECEIVED != TRUSTED IDENTITY

ID TOKEN PARSED != VALIDATED ID TOKEN

NONCE EXPECTATION != NONCE VALIDATION

PENDING TRANSACTION != PROCESSING TRANSACTION

PROCESSING TRANSACTION != COMPLETED TRANSACTION

RETRY != RECOVERY

PROVIDER SUCCESS != LOCAL SESSION COMMIT

PROVIDER CALLBACK != LOCAL COMMIT

EMAIL DELIVERY != VERIFICATION

SAME EMAIL != IDENTITY EQUIVALENCE

AUTHENTICATION METHOD != RECOVERY PROOF

OIDC TRANSACTION != PROVIDER IDENTITY

PKCE VERIFIER CONFIDENTIAL MATERIAL != PKCE VERIFIER HASH / EVIDENCE

TRANSACTION CLAIM != LOCAL IDENTITY COMMIT

USER-AGENT BINDING != IDENTITY

LOCAL LOGIN-CSRF PROOF != IDENTITY

PROVIDER PROOF != LOCAL COMMIT

PROVIDER PROOF != CANONICAL IDENTITY

CANONICAL IDENTITY != ACCOUNT CREATION POLICY

IDENTITY CREATION != MEMBERSHIP

SESSION != AUTHORIZATION

ACCOUNT LINK != EMAIL EQUALITY

OIDC LOGIN TRANSACTION != OIDC LINK TRANSACTION

OIDC CALLBACK GET != GENERAL GET MUTATION SEMANTICS

RECOVERY REQUEST != RECOVERY EFFECT

REVOCATION REQUEST != REVOCATION COMMIT

APPLICATION CSRF PROOF != OIDC STATE

OIDC STATE != APPLICATION CSRF PROOF

REDIRECT TARGET CANDIDATE != LEGITIMATE REDIRECT TARGET

DB PRINCIPAL CAPABILITY CLAIM != DB PRINCIPAL CAPABILITY PROOF

### 34.5 Reconstruction Law

After material authentication change:

* re-read auth method/session state
* reconstruct session validity
* reconstruct frontend auth state
* do not reuse stale session truth
* do not infer authorization from authentication
* do not infer identity from email equality
* do not infer account creation from provider proof
* do not infer provider identity from OIDC transaction alone
* do not infer recovery effect from recovery request
* do not infer application CSRF proof from OIDC state
* do not infer OIDC state validity from application CSRF proof
* do not infer local login-CSRF proof from authenticated-request CSRF proof
* do not infer local commit from callback route reachability
* do not infer token-exchange capability from non-recoverable verifier hash
* do not infer nonce validation before ID Token validation
* do not infer trusted provider subject before ID Token validation
* do not infer callback exclusivity from provider-side code reuse rejection
* do not infer callback legitimacy from state alone
* do not infer redirect safety from redirect candidate existence
* do not infer runtime DB-principal capability from bootstrap/test authority

## 35. Agent Autonomy

Implementation agent may choose:

* exact file layout
* exact route names where semantics preserved
* exact SQLAlchemy model organization
* exact OIDC client library
* exact email client library
* exact internal service decomposition
* exact frontend component boundaries
* exact test fixture structure
* exact migration split
* exact provider abstraction interfaces
* exact cookie helper structure
* exact OIDC transaction persistence technology
* exact secure PKCE verifier storage implementation
* exact atomic claim mechanism
* exact initiating user-agent binding mechanism
* exact local password login-CSRF mechanism
* exact redirect target validation mechanism
* exact anti-CSRF mechanism if it satisfies architecture boundary
* exact runtime DB-principal capability implementation consistent with repository architecture
* exact account creation policy configuration mechanism

Implementation agent may not choose:

* to collapse authentication and authorization
* to auto-link by email
* to treat mock provider as production proof
* to expose provider methods without config
* to create production self-registration without human authority
* to create user automatically for unknown provider subject unless policy exists
* to close Workspace governance bootstrap by side effect
* to store raw session tokens
* to put session token in JSON response
* to accept provider callback as session commit without local validation
* to accept callback without OIDC transaction
* to accept callback without initiating user-agent binding validation
* to accept local password login without explicit login-CSRF boundary proof
* to validate nonce before token exchange and ID Token validation
* to trust provider subject before ID Token validation
* to let two callbacks reach token exchange for the same transaction
* to rely solely on provider authorization-code rejection for transaction concurrency
* to allow PROCESSING → PENDING
* to blind-retry an uncertain token exchange outcome
* to store PKCE verifier only as hash
* to expose PKCE verifier to browser, frontend state, logs or proof reports
* to reuse PKCE verifier after terminal transaction state
* to reuse LOGIN transaction for LINK
* to reuse claimed/terminal transaction
* to allow transferred callback to authenticate unrelated browser context
* to allow arbitrary redirect target
* to classify recovery challenge as authentication method
* to silently bypass email verification/recovery proof
* to accept unsafe cookie-authenticated ordinary application requests without anti-CSRF proof
* to treat OIDC state as general application CSRF proof
* to treat application CSRF proof as OIDC transaction proof
* to treat authenticated-request CSRF proof as automatic proof for unauthenticated local password login
* to claim CORS or SameSite alone proves local login-CSRF boundary without adversarial browser/API evidence
* to let ordinary GET application resources mutate business state
* to harden only new auth tables while leaving existing live auth persistence outside runtime DB-principal discipline
* to represent bootstrap/test database authority as production runtime authority

## 36. Human Authority Boundaries

HUMAN_AUTHORITY_REQUIRED:

1. Which login methods are official product capabilities.
2. Whether password authentication is allowed in production.
3. Whether self-registration is allowed.
4. Whether account creation is invitation-only, open or governance-mediated.
5. Whether unknown Google provider subject may create a canonical NQUIRY user.
6. Whether Google OIDC is production-enabled for first release.
7. Whether Microsoft login is required.
8. Whether GitHub login is required.
9. Whether provider-email verified claim can establish NQUIRY verified email.
10. Session lifetime policy.
11. Account recovery policy and proof requirements.
12. Whether unlinking last auth method is ever allowed.
13. Whether administrative recovery exists and who may perform it.
14. Whether provider tokens are stored for API access.
15. Workspace governance-root bootstrap policy.
16. Production email delivery provider selection.
17. Rate-limit thresholds if product/security policy requires human approval.
18. Multi-account UX policy for already-authenticated browser starting login as different identity.

NOT HUMAN AUTHORITY REQUIRED:

* exact OIDC library
* route naming
* table naming if semantics preserved
* component boundaries
* test fixture organization
* SQLAlchemy repository shape
* UI layout details
* exact implementation of PKCE helper
* exact secure PKCE verifier storage implementation
* exact OIDC transaction atomic claim mechanism
* exact initiating user-agent binding mechanism
* exact local password login-CSRF mechanism where invariant is proven
* exact redirect target validation mechanism
* exact runtime DB-principal implementation where repository capability semantics are preserved
* exact challenge token length above security minimum
* exact anti-CSRF implementation mechanism where boundary is satisfied
* exact OIDC transaction storage shape where semantics are preserved

Default behavior for unresolved human authority:

* fail closed for identity creation
* fail closed for production provider enablement
* fail closed for production password enablement
* fail closed for recovery effects
* fail closed for governance bootstrap
* fail closed for unsafe cookie-authenticated request without CSRF proof
* fail closed for local password login without login-CSRF boundary proof
* fail closed for ambiguous account-linking authority

## 37. Work Units

### WU-AUTH-01: Repository Binding Reconstruction

FIELD: Evidence

MUST BECOME TRUE: implementation agent maps actual files, tables, routes, tests and architecture docs before coding.

MUST REMAIN IMPOSSIBLE: implementing from generic auth assumptions.

FALSIFIER: new code ignores existing `auth_handler`, `local_auth`, `http_dispatch` or migration.

DEPENDENCIES: none.

AUTHORITATIVE SOURCE: public repository.

PERSISTENCE EFFECT: none.

API EFFECT: none.

FRONTEND EFFECT: none.

SECURITY BOUNDARY: prevents repository drift.

TEST SURFACE: architecture/evidence checklist.

PROOF REQUIREMENT: mapping report.

### WU-AUTH-02: Authentication Method Model

FIELD: Identity

MUST BECOME TRUE: canonical `UserId` can have typed authentication methods.

MUST REMAIN IMPOSSIBLE: email equality links accounts; recovery challenge appears as auth method; OIDC transaction appears as auth method; initiating user-agent binding appears as auth method.

FALSIFIER: provider login creates/links identity solely by email.

DEPENDENCIES: WU-AUTH-01.

AUTHORITATIVE SOURCE: Canonical Identity Model.

PERSISTENCE EFFECT: add auth method relation.

API EFFECT: list methods internally or publicly as allowed.

FRONTEND EFFECT: account security surface later.

SECURITY BOUNDARY: method status controls login.

TEST SURFACE: persistence/domain tests.

PROOF REQUIREMENT: method uniqueness/status tests; recovery challenge exclusion test; OIDC transaction exclusion test; user-agent binding exclusion test.

### WU-AUTH-03: Local Credential Migration Compatibility

FIELD: Local Password

MUST BECOME TRUE: existing local credentials work through method model.

MUST REMAIN IMPOSSIBLE: plaintext password migration.

FALSIFIER: existing demo login breaks without explicit migration decision.

DEPENDENCIES: WU-AUTH-02.

AUTHORITATIVE SOURCE: Local Password Architecture.

PERSISTENCE EFFECT: method rows for local credentials.

API EFFECT: `/auth/login` compatibility.

FRONTEND EFFECT: existing login still works.

SECURITY BOUNDARY: preserve hash semantics.

TEST SURFACE: e2e login tests.

PROOF REQUIREMENT: existing tests plus migration test.

### WU-AUTH-04: Authenticated Session Evolution

FIELD: Authenticated Session

MUST BECOME TRUE:

* sessions remain server-side and opaque
* each session can be traced to canonical `UserId`
* each session can be traced to authentication method or proof provenance
* each session records issued time, expiration and revocation state
* successful authentication creates fresh session relation
* successful authentication sets/replaces session cookie
* session revocation can operate at single-session scope
* session revocation can operate at all-session scope
* session revocation can operate at authentication-method scope
* session revocation can operate at account-disable scope
* session rotation can occur after high-risk authentication changes where architecture requires it

MUST REMAIN IMPOSSIBLE:

* raw session token stored in DB
* session token returned in JSON
* revoked session resolves identity
* expired session resolves identity
* revoked authentication method continues creating sessions
* session grants business authority
* session survives a revocation relation that explicitly invalidates it
* login preserves attacker-controlled authenticated session identity

FALSIFIER: session fixation succeeds across login.

DEPENDENCIES: WU-AUTH-02 and WU-AUTH-03.

AUTHORITATIVE SOURCE: Session Architecture.

PERSISTENCE EFFECT: extend or wrap local session persistence.

API EFFECT: logout, all-session logout, session revoke contacts.

FRONTEND EFFECT: account/session management surface.

SECURITY BOUNDARY: server-side opaque session, revocation propagation, session fixation prevention.

TEST SURFACE: session tests, revocation tests, JSON leakage tests, session fixation tests, authorization regression tests.

PROOF REQUIREMENT: session traceability, fresh session creation and post-revocation denial proof.

### WU-AUTH-05: OIDC Auth Transaction Field

FIELD: OIDC Auth Transaction

MUST BECOME TRUE:

* transaction has explicit lifecycle state
* LOGIN/ACCOUNT_LINK purpose is bound
* transaction has initiating user-agent binding
* transaction has redirect target binding to legitimate local destination
* only PENDING can be claimed
* claim is atomic
* exactly one callback enters PROCESSING
* PROCESSING cannot return to PENDING
* second callback never reaches token exchange
* transaction stores protected state binding
* transaction stores expected nonce binding
* transaction binds a confidentially retrievable PKCE verifier
* ACCOUNT_LINK transaction binds initiating `UserId`
* transaction expires
* only claiming processor gains verifier access
* nonce validation occurs after token exchange and trusted ID Token validation
* terminal uncertain outcome cannot be blindly retried
* provider error/cancel terminalizes without token exchange
* transaction enters terminal state after completion, expiry, cancel/denial or unsafe failure
* verifier becomes unavailable / unusable after terminal state
* initiating user-agent binding invalid after terminal state

MUST REMAIN IMPOSSIBLE:

* callback succeeds without transaction
* transaction replay succeeds
* LOGIN transaction becomes LINK
* LINK transaction binds to wrong identity
* expired transaction reaches token exchange
* terminal transaction reaches token exchange
* PROCESSING returns to PENDING
* second callback reaches token exchange
* token exchange cannot retrieve original verifier
* verifier stored only as non-recoverable hash
* verifier reused after terminal state
* verifier from one transaction satisfies another transaction
* nonce checked before token exchange
* nonce trusted before ID Token validation
* provider subject trusted before ID Token validation
* transaction single-use depends solely on provider authorization-code rejection
* callback transplantation produces session
* provider cancel/error leaves replayable transaction

FALSIFIER: callback valid for one user-agent interaction creates session in another browser.

DEPENDENCIES: WU-AUTH-02.

AUTHORITATIVE SOURCE: OIDC Auth Transaction Field.

PERSISTENCE EFFECT: OIDC transaction relation, lifecycle state, initiating user-agent binding and confidential PKCE verifier binding.

API EFFECT: provider start/callback routes.

FRONTEND EFFECT: provider login/link start contacts.

SECURITY BOUNDARY: state/user-agent/expiry/purpose/initiating-user/atomic claim/nonce/PKCE/replay protection.

TEST SURFACE: OIDC transaction state machine, user-agent binding and PKCE verifier lifecycle tests.

PROOF REQUIREMENT: invalid/expired/replayed/purpose-mismatch/verifier-mismatch/concurrency/order/callback-transplant tests.

### WU-AUTH-06: Redirect Target Validation

FIELD: Redirect Target

MUST BECOME TRUE:

* redirect target candidates are validated before binding
* post-auth redirects target legitimate local destinations only
* provider redirect URI and post-auth application redirect remain distinct
* error/cancel redirects are safe

MUST REMAIN IMPOSSIBLE:

* arbitrary attacker-controlled absolute URL becomes post-auth redirect
* sensitive artifacts are forwarded to hostile origin
* redirect candidate becomes authority by existence

FALSIFIER: post-auth redirect sends browser to hostile origin.

DEPENDENCIES: WU-AUTH-05.

AUTHORITATIVE SOURCE: Redirect Target Architecture.

PERSISTENCE EFFECT: safe redirect target binding or named destination if persisted.

API EFFECT: login start, link start, callback, error/cancel, recovery redirects.

FRONTEND EFFECT: redirect candidates remain candidates until backend validation.

SECURITY BOUNDARY: open redirect prevention.

TEST SURFACE: redirect validation adversarial tests.

PROOF REQUIREMENT: hostile redirect target rejected or normalized to safe default.

### WU-AUTH-07: Google OIDC Provider Adapter

FIELD: External Provider

MUST BECOME TRUE: Google proof validates via OIDC Authorization Code + PKCE and OIDC transaction state machine.

MUST REMAIN IMPOSSIBLE: implicit flow, unchecked callback, unvalidated ID Token, token exchange without original verifier, nonce validation before token response.

FALSIFIER: forged callback creates local session.

DEPENDENCIES: WU-AUTH-05 and WU-AUTH-06.

AUTHORITATIVE SOURCE: Google OIDC Architecture.

PERSISTENCE EFFECT: provider state/challenge if needed beyond transaction.

API EFFECT: start/callback routes.

FRONTEND EFFECT: Google login button when configured.

SECURITY BOUNDARY: state/user-agent/expiry/purpose/claim/nonce/PKCE/issuer/audience/signature/transaction.

TEST SURFACE: provider mock/sandbox/real test lanes.

PROOF REQUIREMENT: invalid state/nonce/token/PKCE verifier/order tests and provider cancel/error tests.

### WU-AUTH-08: Provider Identity Binding

FIELD: Canonical Identity

MUST BECOME TRUE: provider issuer+subject maps to canonical `UserId`.

MUST REMAIN IMPOSSIBLE: same email auto-link; provider subject trusted before ID Token validation.

FALSIFIER: two different provider subjects with same email silently merge.

DEPENDENCIES: WU-AUTH-07.

AUTHORITATIVE SOURCE: Provider Identity Architecture.

PERSISTENCE EFFECT: external provider identity rows.

API EFFECT: login resolution.

FRONTEND EFFECT: session after provider login.

SECURITY BOUNDARY: collision handling.

TEST SURFACE: provider collision tests.

PROOF REQUIREMENT: subject uniqueness proof and trusted-claims-order proof.

### WU-AUTH-09: Account Creation Boundary

FIELD: Account Creation

MUST BECOME TRUE:

* unknown provider subject evaluates explicit account creation policy
* unresolved policy fails closed
* approved policy can create canonical `UserId`
* created identity receives no Workspace authority by default
* account creation and provider identity binding are coherent local effect where architecture requires both

MUST REMAIN IMPOSSIBLE:

* valid Google subject automatically creates user by implementation convenience
* same email creates binding
* new user receives Workspace membership/role/governance root/capability by auth side effect
* partial identity creation is represented as full authentication success

FALSIFIER: unknown provider subject creates `UserId` without policy.

DEPENDENCIES: WU-AUTH-08.

AUTHORITATIVE SOURCE: Account Creation Boundary.

PERSISTENCE EFFECT: account creation event and user row only when policy allows.

API EFFECT: provider callback account creation branch.

FRONTEND EFFECT: account creation unavailable/denied boundary.

SECURITY BOUNDARY: fail-closed identity creation.

TEST SURFACE: first-login tests.

PROOF REQUIREMENT: disabled policy denies; approved policy creates identity without authority; partial commit reconstructability.

### WU-AUTH-10: Account Linking

FIELD: Linking

MUST BECOME TRUE: authenticated user can link new method with proof and ACCOUNT_LINK transaction.

MUST REMAIN IMPOSSIBLE: unauthenticated link, link to already-linked provider subject, link callback transplanted into wrong browser/user identity context.

FALSIFIER: provider subject moves accounts without authority.

DEPENDENCIES: WU-AUTH-05, WU-AUTH-07, WU-AUTH-08.

AUTHORITATIVE SOURCE: Account Linking Architecture.

PERSISTENCE EFFECT: link event/method row.

API EFFECT: link start/callback.

FRONTEND EFFECT: account settings link action.

SECURITY BOUNDARY: authenticated session + ACCOUNT_LINK transaction + user-agent binding + transaction claim + provider proof + PKCE verifier binding.

TEST SURFACE: linking/collision/callback transplantation tests.

PROOF REQUIREMENT: link audit event and wrong-initiating-user denial.

### WU-AUTH-11: Email Verification

FIELD: Verification

MUST BECOME TRUE: email verification has challenge state and commit.

MUST REMAIN IMPOSSIBLE: email delivery equals verification.

FALSIFIER: verified email created before token proof.

DEPENDENCIES: WU-AUTH-02.

AUTHORITATIVE SOURCE: Email Verification Architecture.

PERSISTENCE EFFECT: verified email + challenge rows.

API EFFECT: start/complete verification.

FRONTEND EFFECT: verification UI.

SECURITY BOUNDARY: token hash/expiry/attempt limit.

TEST SURFACE: verification tests.

PROOF REQUIREMENT: expired/replayed challenge denied.

### WU-AUTH-12: Recovery

FIELD: Recovery

MUST BECOME TRUE:

* password/account recovery uses explicit recovery challenge
* verified recovery proof can authorize restoration/replacement effect
* recovery challenge remains distinct from authentication method

MUST REMAIN IMPOSSIBLE:

* reset by email string alone
* recovery challenge listed as persistent auth method
* recovery request commits effect

FALSIFIER: attacker knowing email resets credential.

DEPENDENCIES: WU-AUTH-11 or provider proof policy.

AUTHORITATIVE SOURCE: Recovery Architecture.

PERSISTENCE EFFECT: recovery challenges.

API EFFECT: recovery start/complete.

FRONTEND EFFECT: recovery UI.

SECURITY BOUNDARY: proof gate and rate limit.

TEST SURFACE: recovery tests.

PROOF REQUIREMENT: replay/expiry/rate tests.

### WU-AUTH-13: Revocation Expansion

FIELD: Revocation

MUST BECOME TRUE: single session, all sessions, method revocation, provider unlink, terminal OIDC transaction state and account disable exist.

MUST REMAIN IMPOSSIBLE: revoked method continues login; terminal transaction continues callback processing.

FALSIFIER: session created by revoked provider remains valid when policy says revoke.

DEPENDENCIES: WU-AUTH-04 and WU-AUTH-02.

AUTHORITATIVE SOURCE: Revocation Architecture.

PERSISTENCE EFFECT: revocation fields/events and transaction terminal states.

API EFFECT: revoke endpoints.

FRONTEND EFFECT: session management UI.

SECURITY BOUNDARY: dependency propagation.

TEST SURFACE: revocation tests.

PROOF REQUIREMENT: post-revocation session denial and terminal transaction replay denial.

### WU-AUTH-14: Anti-CSRF Boundary

FIELD: Request Security

MUST BECOME TRUE:

* unsafe cookie-authenticated ordinary application requests pass explicit anti-CSRF validation before application execution
* ordinary safe application requests do not gain business mutation semantics
* OIDC callback protocol validation remains distinct from application CSRF
* local password login has an explicit login-CSRF boundary
* local login request cannot create authenticated session through hostile cross-site submission
* actual selected local login-CSRF mechanism is proven against the real browser/API request contract
* successful local login still creates a fresh authenticated session
* CORS is not treated as CSRF substitute
* SameSite is not sole security boundary

MUST REMAIN IMPOSSIBLE:

* unsafe cookie-authenticated ordinary application request accepted without CSRF proof
* cross-origin hostile unsafe request commits effect
* CSRF failure becomes successful application effect
* OIDC state treated as general application CSRF proof
* hostile origin logs victim browser into attacker-selected local account
* authenticated-request CSRF protection is incorrectly assumed to cover unauthenticated login automatically
* CORS alone is treated as sufficient without actual browser/API proof
* SameSite alone is treated as sufficient login-CSRF proof
* pre-auth state becomes authenticated session if a pre-auth mechanism is used

FALSIFIER: hostile origin causes victim browser to authenticate into attacker-selected local account.

DEPENDENCIES: WU-AUTH-04.

AUTHORITATIVE SOURCE: CSRF Architecture / Local Password Login-CSRF Boundary.

PERSISTENCE EFFECT: optional, depending on selected mechanism.

API EFFECT: unsafe method validation and local password login boundary validation.

FRONTEND EFFECT: frontend supplies or satisfies anti-CSRF / local login-CSRF proof where selected mechanism requires it.

SECURITY BOUNDARY:

* explicit CSRF proof before unsafe cookie-authenticated application request
* explicit login-CSRF boundary before local password credential validation can create fresh session

TEST SURFACE:

* API/browser/security tests
* cross-site local login submission attempt
* attacker-selected credential login attempt against victim browser
* actual Origin / CSRF / Fetch Metadata / request-contract mechanism succeeds for legitimate same-origin login
* hostile-origin attempt fails before fresh authenticated session commit
* successful legitimate login creates fresh session
* pre-existing or pre-auth state does not become authenticated session

PROOF REQUIREMENT:

* CSRF adversarial proof
* login-CSRF boundary proof
* legitimate same-origin local login still works
* hostile-origin local login attempt fails before session commit
* CORS or SameSite is not represented as sufficient proof without adversarial browser/API evidence

### WU-AUTH-15: Protocol Callback Semantics

FIELD: Protocol Callback

MUST BECOME TRUE:

* OIDC callback GET is treated as protocol response contact
* callback effects are limited to protocol-defined security / identity effects
* callback effects occur only through OIDC transaction, user-agent binding, state, transaction claim, PKCE, token exchange, ID Token validation, nonce validation, provider proof and local effect gates
* ordinary GET application routes remain non-mutating

MUST REMAIN IMPOSSIBLE:

* arbitrary GET route mutates business state
* callback grants Workspace authority
* callback bypasses account creation policy
* callback bypasses account linking authority
* callback bypasses user-agent binding
* callback bypasses transaction claim
* callback bypasses PKCE verifier validation
* callback trusts nonce or subject before ID Token validation

FALSIFIER: OIDC callback performs non-auth business command.

DEPENDENCIES: WU-AUTH-05 and WU-AUTH-14.

AUTHORITATIVE SOURCE: Protocol Callback Architecture.

PERSISTENCE EFFECT: none beyond transaction/effects already defined.

API EFFECT: callback route semantics.

FRONTEND EFFECT: callback page/redirect handling if any.

SECURITY BOUNDARY: protocol callback limited to dedicated proof/effect gate.

TEST SURFACE: API and browser protocol callback tests.

PROOF REQUIREMENT: callback cannot perform arbitrary business command.

### WU-AUTH-16: Authorization Regression

FIELD: Authorization Boundary

MUST BECOME TRUE: auth changes do not alter membership/role/authority.

MUST REMAIN IMPOSSIBLE: provider login grants Workspace authority.

FALSIFIER: Google login creates governance root without approved policy.

DEPENDENCIES: all auth WUs.

AUTHORITATIVE SOURCE: Authorization Boundary.

PERSISTENCE EFFECT: none unless approved.

API EFFECT: existing protected routes still use authority resolver.

FRONTEND EFFECT: authenticated but unauthorized distinct.

SECURITY BOUNDARY: auth-to-authz boundary.

TEST SURFACE: membership/authority regression.

PROOF REQUIREMENT: unauthorized logged-in user denied.

### WU-AUTH-17: Runtime DB Principal Capability Boundary

FIELD: Runtime Persistence Security / DB Principal Capability

MUST BECOME TRUE:

* authentication persistence participates in the repository's runtime DB-principal capability discipline
* live HTTP authentication paths no longer depend on an over-broad bootstrap/database principal where the architecture requires scoped runtime capability
* new auth tables and existing live auth persistence are treated consistently
* the runtime principal receives only the database capabilities legitimately required for its authentication persistence operations
* DB principal capability is explicit and testable
* the repair covers the live persistence path, not merely newly added tables

MUST REMAIN IMPOSSIBLE:

* authentication tables are added while runtime service identity remains implicitly over-privileged
* only new auth tables receive hardening while existing live auth persistence bypasses the same boundary
* runtime DB actor performs authentication persistence operations outside its intended capability scope
* DB principal separation is claimed without real capability proof
* test/bootstrap database authority is represented as production runtime authority

FALSIFIER: A runtime DB principal can perform an authentication persistence operation outside the capability set required by the legitimate runtime authentication Field.

DEPENDENCIES:

* WU-AUTH-02
* WU-AUTH-04
* WU-AUTH-05
* WU-AUTH-08
* WU-AUTH-09
* WU-AUTH-10
* WU-AUTH-11
* WU-AUTH-12
* WU-AUTH-13

AUTHORITATIVE SOURCE:

* FBR-AUTH-006
* Security Architecture / DB Principal Boundary
* Runtime and Configuration Architecture
* actual repository DB-principal capability architecture

PERSISTENCE EFFECT: No new domain truth merely for this Work Unit. It changes which runtime database principal is legitimately capable of performing existing authentication persistence operations.

API EFFECT: No API semantic change. Live authentication API operations must continue to function through the legitimate scoped runtime persistence capability.

FRONTEND EFFECT: None.

SECURITY BOUNDARY:

runtime service identity
→ scoped DB capability
→ authentication persistence operation

TEST SURFACE:

* DB-principal capability tests
* authentication persistence integration tests
* negative capability tests
* real runtime authentication path using scoped DB principal

PROOF REQUIREMENT:

Evidence must show that:

* legitimate auth persistence still works
* unauthorized DB operations fail
* existing and newly introduced auth persistence follow the same runtime-principal discipline
* bootstrap/test authority is not represented as production runtime authority

## 38. Falsifiers

1. External provider email auto-links accounts.
2. Google callback creates session without OIDC transaction lookup.
3. Google callback creates session without initiating user-agent binding validation.
4. Callback valid for one initiating interaction creates session in unrelated browser.
5. Google callback creates session without state validation.
6. Google callback reaches token exchange before expiry validation.
7. Google callback reaches token exchange before purpose validation.
8. ACCOUNT_LINK callback reaches token exchange before initiating-user validation.
9. Google callback reaches token exchange without atomic transaction claim.
10. Two concurrent callbacks both reach token exchange.
11. PROCESSING transaction returns to PENDING.
12. Second callback retrieves usable PKCE verifier.
13. FAILED_TERMINAL transaction can be replayed.
14. COMPLETED transaction can be replayed.
15. CANCELLED_TERMINAL transaction can be replayed.
16. EXPIRED transaction can be replayed.
17. Consumed transaction reaches token exchange again.
18. Expired transaction reaches token exchange.
19. Wrong-purpose transaction reaches token exchange.
20. ACCOUNT_LINK transaction binds to wrong `UserId`.
21. Nonce is checked before token exchange.
22. Nonce is trusted before required ID Token cryptographic and semantic validation.
23. Token response is treated as authenticated identity before ID Token validation.
24. Provider subject is trusted before ID Token validation.
25. Invalid nonce still produces local session.
26. Token exchange failure produces local identity effect.
27. Provider proof failure leaves transaction reusable.
28. Local effect failure causes callback transaction to become replayable.
29. Raw PKCE verifier is available to callback that did not win transaction claim.
30. Transaction single-use depends solely on provider authorization-code rejection.
31. Provider access token appears in frontend URL or logs.
32. Raw session token appears in JSON.
33. Raw session token stored in DB.
34. Local session resolves after `revoked_at`.
35. Local session resolves after `expires_at`.
36. Password reset succeeds by email string alone.
37. Email verification succeeds before challenge proof.
38. Recovery token replay succeeds.
39. Recovery challenge appears as authentication method.
40. Recovery request commits recovery effect.
41. Mock provider accepted in production config.
42. Provider subject collision silently merges users.
43. Same email silently merges users.
44. Authenticated identity carries role/permission.
45. Session cookie grants Workspace authority without membership.
46. Google login creates Workspace governance root without approved bootstrap policy.
47. Unknown Google provider subject creates `UserId` without account creation policy.
48. Unknown Google provider subject with disabled account creation policy creates local session.
49. Same email matching existing account without provider binding links account.
50. Newly created `UserId` receives Workspace membership/role/governance root/authority/capability by authentication side effect.
51. Logout one session revokes unrelated session unless policy says all-session revoke.
52. Credential revocation leaves dependent sessions active when policy requires invalidation.
53. Unlinking last method strands account without explicit authority.
54. Production password method lacks reset/recovery policy.
55. Secure cookie disabled in HTTPS production config.
56. CORS allows wildcard with credentials.
57. Login failure reveals unknown email vs wrong password.
58. Provider button rendered when backend provider config unavailable.
59. Account linking works while unauthenticated.
60. Account linking uses LOGIN transaction.
61. LINK transaction binds to wrong authenticated identity.
62. DB read can reconstruct usable session.
63. Auth migration invalidates existing authorization semantics.
64. Auth tables are treated as Workspace-scoped without evidence.
65. Callback succeeds without OIDC transaction.
66. State correct but transaction expired still succeeds.
67. Transaction replay succeeds.
68. Parallel callback consumes same transaction twice.
69. Unsafe cookie-authenticated ordinary application request accepted without anti-CSRF proof.
70. Cross-origin unsafe application request commits effect.
71. CORS configuration permits credentialed hostile origin.
72. CSRF failure represented as successful application effect.
73. SameSite treated as sole CSRF boundary.
74. Session grants business authority.
75. Revoked authentication method continues creating sessions.
76. Session survives revocation relation that explicitly invalidates it.
77. Token exchange cannot retrieve the original PKCE verifier.
78. PKCE verifier is stored only as a non-recoverable hash.
79. Raw PKCE verifier reaches browser JavaScript.
80. Raw PKCE verifier appears in frontend state.
81. Raw PKCE verifier appears in logs.
82. Raw PKCE verifier appears in proof report.
83. PKCE verifier reused after transaction terminal state.
84. PKCE verifier from one transaction satisfies another transaction.
85. PKCE verifier from LOGIN transaction satisfies ACCOUNT_LINK transaction.
86. OIDC callback GET causes arbitrary business mutation.
87. Ordinary application GET route mutates business state.
88. OIDC state treated as application CSRF proof.
89. Application CSRF proof treated as OIDC state.
90. Protocol callback bypasses account creation policy.
91. Protocol callback bypasses account linking authority.
92. Protocol callback bypasses user-agent binding.
93. Protocol callback bypasses transaction claim.
94. Protocol callback grants Workspace authority.
95. Uncertain exchange outcome automatically retries same authorization code.
96. Token exchange failure returns transaction to PENDING.
97. ID Token parsed but not validated produces provider subject input.
98. ID Token signature valid but invalid issuer/audience/expiry still produces provider subject input.
99. Provider subject missing still produces local identity effect.
100. Provider `access_denied` creates local session.
101. Provider cancel leaves transaction replayable.
102. Malformed callback creates local effect.
103. Post-auth redirect sends browser to attacker-controlled origin.
104. OIDC provider redirect URI is treated as post-auth application redirect target.
105. Login preserves attacker-controlled authenticated session identity.
106. Two login starts in same browser create ambiguous callback identity.
107. Two first-login attempts for same provider subject create duplicate users.
108. Provider binding partial failure is represented as full authentication success.
109. Account creation partial failure is represented as full authentication success.
110. Security material appears in review evidence.
111. Runtime DB principal can perform authentication persistence outside its legitimate capability scope.
112. Authentication DB-principal hardening covers new auth tables but leaves the existing live authentication persistence path over-privileged.
113. Hostile origin can cause victim browser to authenticate into attacker-selected local account.
114. Local password login relies on authenticated-request CSRF protection even though no authenticated session yet exists.
115. CORS or SameSite is claimed as sufficient login-CSRF proof without adversarial browser/API evidence.
116. A pre-auth login state, if used, becomes or fixes the authenticated session instead of a fresh session being created.

## 39. Test Architecture

### 39.1 Unit Tests

* password hashing/verification
* session token generation/hash
* provider claim normalization
* challenge token hashing
* recovery challenge hashing
* state helper
* nonce helper
* initiating user-agent binding helper
* local login-CSRF helper if selected mechanism uses local proof material
* redirect target validator
* PKCE verifier generation
* PKCE challenge derivation
* PKCE verifier confidential storage/retrieval abstraction
* OIDC transaction creation
* OIDC transaction expiry
* OIDC transaction state transitions
* PENDING → PROCESSING claim
* terminal-state claim rejection
* provider error normalization
* boundary parsing
* CSRF proof helper if used

### 39.2 State Machine Tests

Required:

* PENDING → PROCESSING succeeds once
* second claim fails
* PROCESSING → PENDING impossible
* PROCESSING → COMPLETED
* PROCESSING → FAILED_TERMINAL
* PENDING → EXPIRED
* PENDING → CANCELLED_TERMINAL where modeled
* COMPLETED cannot be claimed
* FAILED_TERMINAL cannot be claimed
* CANCELLED_TERMINAL cannot be claimed
* EXPIRED cannot be claimed
* verifier unavailable after terminal state
* initiating user-agent binding invalid after terminal state

### 39.3 Application / Protocol Tests

Required:

* state invalid prevents claim
* user-agent binding missing prevents claim
* user-agent binding mismatch prevents claim
* expired transaction prevents claim
* purpose mismatch prevents claim
* ACCOUNT_LINK wrong initiating user prevents claim
* claim succeeds before verifier retrieval
* verifier retrieval requires claimed transaction
* token exchange receives original verifier
* ID Token is obtained from token response
* signature validation occurs before trusted claim use
* issuer validation occurs before trusted claim use
* audience validation occurs before trusted claim use
* expiration validation occurs before trusted claim use
* nonce is validated against transaction after token validation
* provider subject used only after token validation
* provider cancel/error performs no token exchange
* provider cancel/error creates no local session

### 39.4 Domain/Application Tests

* login success/failure
* local login-CSRF success/failure
* OIDC callback success/failure
* OIDC transaction purpose enforcement
* user-agent binding enforcement
* redirect target validation
* PKCE verifier retrieval and unavailability after terminal state
* identity resolution
* account creation boundary
* account linking
* collision handling
* recovery
* revocation
* auth-to-authz boundary
* CSRF boundary
* protocol callback semantics

### 39.5 Persistence Tests

* constraints
* migration up/down
* unique provider subject
* session revocation
* method status
* challenge replay prevention
* recovery challenge replay prevention
* OIDC transaction single-use
* OIDC transaction expiry
* OIDC transaction purpose binding
* OIDC transaction atomic claim
* initiating user-agent binding lifecycle
* confidential PKCE verifier binding
* verifier unavailable after terminal state
* verifier cannot cross transaction or purpose boundary
* account creation event where policy allows
* redirect target stored only after validation if persisted
* local login-CSRF state cannot become authenticated session if persisted
* runtime DB principal capability constraints

### 39.6 API Tests

* auth routes
* local password login-CSRF request contract
* provider start/callback
* provider cancel/error callback
* method list/link/unlink
* verification
* recovery
* revocation
* malformed body rejection
* account creation disabled/enabled policy
* unsafe request anti-CSRF enforcement
* callback GET protocol semantics
* ordinary GET non-mutation semantics
* redirect target rejection
* status code contract

### 39.7 Browser Tests

* login page
* local password legitimate same-origin login succeeds
* cross-site local login submission attempt fails
* attacker-selected credential login attempt against victim browser fails
* successful legitimate local login creates fresh session
* pre-existing or pre-auth state does not become authenticated session
* Google login configured/unconfigured
* Google login existing provider binding
* Google login unknown subject with account creation disabled
* Google login unknown subject with approved creation policy
* Google cancel
* provider error
* callback transplantation blocked
* denied login
* logout
* account linking UI
* recovery UI
* no prefilled credentials
* no token in URL
* no PKCE verifier in browser-visible state
* CSRF-protected unsafe requests through real frontend path
* open redirect attempt blocked
* session fixation blocked

### 39.8 Security Boundary Tests

* forged cookie
* tampered cookie
* expired session
* revoked session
* forged actor headers inert
* CSRF failure
* local login-CSRF failure
* hostile origin unsafe request
* hostile origin local password login request
* state mismatch
* user-agent binding mismatch
* nonce mismatch after token validation
* missing verifier
* wrong verifier
* verifier reuse
* PKCE mismatch
* missing transaction
* expired transaction
* consumed transaction replay
* cancelled transaction replay
* purpose mismatch
* provider subject collision
* same-email collision
* rate limiting

### 39.9 Authorization Regression Tests

* authenticated nonmember denied
* member without role denied where required
* role without authority denied where required
* authority resolver still invoked
* provider claims containing `role` ignored
* newly created user has no Workspace authority unless separately established
* OIDC callback cannot trigger business command
* local password login cannot grant business authority

### 39.10 First Google Login Tests

Required tests:

* existing provider binding resolves existing `UserId`
* unknown provider subject with account creation disabled fails closed
* unknown provider subject with approved creation policy creates `UserId`
* same email matching existing account without provider binding does not link
* provider subject collision denied
* new `UserId` creation does not create Workspace authority
* duplicate first-login race does not create duplicate users

### 39.11 PKCE Tests

Required tests:

* token exchange can retrieve original verifier after claim
* verifier not stored hash-only
* verifier never reaches browser
* verifier not logged
* verifier not emitted in proof evidence
* verifier unavailable after COMPLETED
* verifier unavailable after FAILED_TERMINAL
* verifier unavailable after CANCELLED_TERMINAL
* verifier unavailable after EXPIRED
* verifier from transaction A cannot satisfy transaction B
* LOGIN verifier cannot satisfy ACCOUNT_LINK transaction
* parallel callback cannot reuse verifier

### 39.12 Protocol Callback Tests

Required tests:

* OIDC GET callback can complete protocol identity effect after proof gates
* OIDC GET callback cannot perform arbitrary business mutation
* ordinary GET application resource cannot mutate state
* callback without transaction fails
* callback without user-agent binding fails
* callback without account creation policy fails for unknown subject
* callback cannot bypass link initiating user
* callback cannot validate nonce before token exchange and ID Token validation
* provider cancel/error does not create local effect

### 39.13 Concurrency Tests

Required tests:

* two parallel callbacks for same transaction
* exactly one wins PENDING → PROCESSING
* only winner reaches token exchange
* loser receives rejected boundary
* only winner can retrieve verifier
* no duplicate identity/session/link effect
* two account-link callbacks same provider subject
* two first-login attempts same provider subject
* concurrent local password login attempts with pre-auth state where selected mechanism uses it
* method revocation during login
* account disable during login
* session revoke during request
* recovery token double use
* verification token double use
* two password reset completions

### 39.14 Failure Tests

Required tests:

* DB unavailable before transaction commit
* DB unavailable after provider proof
* provider unavailable
* provider timeout
* token endpoint rejection
* uncertain token exchange outcome
* invalid ID Token
* invalid nonce
* state mismatch
* expired transaction
* duplicate callback
* process crash after claim where testable
* process crash after provider proof where testable
* local DB failure after provider proof
* session persistence failure
* cookie emission failure
* account creation partial failure
* provider binding partial failure
* audit persistence failure where material
* email delivery failure
* recovery delivery failure
* CSRF failure
* local login-CSRF failure
* rate-limit denial

Every failure test must assert:

* state before failure
* Delta already committed
* whether retry is safe
* whether new transaction is required
* terminal state
* evidence retained
* user-visible projection
* what remains impossible

### 39.15 DB Principal Capability Tests

Required tests:

* legitimate authentication persistence works under scoped runtime DB principal
* unauthorized authentication persistence operation fails
* existing live auth persistence follows same capability boundary as newly introduced auth persistence
* bootstrap/test DB authority is not production runtime proof
* runtime DB actor cannot perform auth persistence outside intended capability set

## 40. Real Stack Proof

Real-stack proof requires:

* Docker Compose full stack
* real Postgres
* migrations applied
* seeded or real user
* real browser
* real API
* local password legitimate login
* local password login-CSRF boundary proof
* session read
* protected route access
* logout
* post-logout denial
* adversarial forged/tampered cookie checks
* unsafe ordinary application request anti-CSRF proof
* CSRF failure proof
* ordinary GET non-mutation proof
* protocol callback route bounded-effect proof if OIDC is implemented
* transaction claim proof if OIDC is implemented
* user-agent binding proof if OIDC is implemented
* redirect validation proof if OIDC is implemented
* provider cancel/error proof if OIDC is implemented
* concurrency proof if OIDC is implemented
* session fixation proof
* runtime DB-principal capability proof where scoped runtime principal is implemented

Existing Local Auth Adapter already has real-stack proof for local login and session behavior.

Target real-stack proof must extend it without degrading existing evidence.

## 41. Real Google Proof

Real Google proof must demonstrate:

1. configured Google client
2. start route creates OIDC transaction in PENDING
3. start route creates initiating user-agent binding
4. start route validates and binds safe post-auth redirect target
5. start route creates confidential PKCE verifier binding
6. start route derives code challenge without exposing verifier
7. start route redirects to Google
8. returned callback looks up transaction
9. returned callback validates initiating user-agent binding
10. returned callback validates state
11. returned callback validates expiry
12. returned callback validates purpose
13. ACCOUNT_LINK callback validates initiating user before token exchange
14. callback atomically claims transaction PENDING → PROCESSING
15. second callback cannot reach token exchange
16. returned callback retrieves original PKCE verifier confidentially after claim
17. returned callback exchanges code using original verifier
18. Token Endpoint response contains ID Token
19. ID Token signature valid
20. ID Token issuer valid
21. ID Token audience valid
22. ID Token expiration valid
23. other required token validation complete
24. nonce claim validated after trusted ID Token validation
25. transaction reaches terminal state
26. verifier becomes unavailable / unusable
27. provider subject extracted only after ID Token validation
28. existing provider subject binding resolves existing identity
29. unknown provider subject with disabled account creation fails closed
30. unknown provider subject with approved account creation creates canonical `UserId`
31. local identity binding created or found
32. fresh local session row created
33. cookie set/replaced
34. `/auth/me` resolves
35. logout revokes
36. same provider subject logs into same identity
37. email collision does not auto-link
38. provider subject collision denied
39. LOGIN transaction cannot be reused for LINK
40. LINK transaction cannot bind to wrong user
41. verifier from LOGIN cannot satisfy LINK
42. terminal transaction cannot replay
43. uncertain token exchange outcome does not blindly retry same transaction
44. provider cancel/error creates no local session
45. callback transplantation into unrelated browser fails
46. hostile post-auth redirect target rejected
47. secrets redacted from evidence
48. raw PKCE verifier absent from browser, logs and proof reports

## 42. Email Proof

Email proof requires:

* challenge issuance
* email delivery through local sink/test provider
* challenge hash stored, raw challenge not stored
* wrong token denied
* expired token denied
* replay denied
* correct token verifies
* verified email relation created only after commit
* reset/recovery uses verified proof, not email string alone
* delivery failure handled without false verification
* recovery challenge remains distinct from authentication method

## 43. Recursive Deep Sweep Requirements

Implementation agent must recursively inspect:

* producer
* consumer
* parent
* children
* siblings
* identity
* session
* membership
* role
* authority
* persistence
* API
* frontend
* runtime
* configuration
* email
* provider
* browser security
* redirects
* CSRF
* CORS
* security
* tests
* evidence
* downstream effects

For each relation:

* authentication method
* local credential
* local login-CSRF boundary
* provider identity
* OIDC auth transaction
* OIDC transaction lifecycle state
* OIDC atomic claim
* initiating user-agent binding
* redirect target validation
* PKCE confidential verifier binding
* ID Token validation
* nonce validation
* provider error/cancel
* protocol callback
* account creation boundary
* verified email
* session
* recovery challenge
* recovery proof
* revocation
* account link
* anti-CSRF boundary
* runtime DB-principal capability boundary
* authorization boundary

Stop condition: no material relation terminates in implicit convention, unpersisted semantic state, unmarked development shortcut, ambiguous authority, undefined identity equivalence, implicit account creation, hash-only PKCE verifier, wrong OIDC protocol order, provider-dependent callback single-processing, absent browser/user-agent binding, unsafe redirect target, undefined local login-CSRF boundary, unproven runtime DB-principal capability or undefined security boundary.

## 44. Inverse Deep Sweep Requirements

### 44.1 Visible Authenticated State

VISIBLE AUTHENTICATED STATE
→ `/auth/me`
→ cookie
→ session hash lookup
→ active unexpired unrevoked server-side session
→ canonical `UserId`
→ auth method/proof provenance

### 44.2 Visible Local Password Login

VISIBLE AUTHENTICATED STATE
→ LOCAL SESSION
→ FRESH LOCAL SESSION COMMIT
→ CANONICAL `UserId`
→ VALID PASSWORD CREDENTIAL
→ LOCAL PASSWORD LOGIN-CSRF BOUNDARY
→ LOCAL PASSWORD LOGIN REQUEST
→ LEGITIMATE BROWSER/API LOGIN INTERACTION

No chain may terminate in hostile cross-site submission, frontend state or authenticated-request CSRF boundary alone.

### 44.3 Visible Google Login

VISIBLE AUTHENTICATED STATE
→ LOCAL SESSION
→ FRESH LOCAL SESSION COMMIT
→ CANONICAL `UserId`
→ TRUSTED PROVIDER SUBJECT
→ VALIDATED ID TOKEN
→ NONCE MATCH AGAINST TRANSACTION
→ TOKEN RESPONSE
→ AUTHORIZATION CODE EXCHANGE
→ ORIGINAL TRANSACTION-BOUND PKCE VERIFIER
→ PROCESSING OIDC TRANSACTION
→ ATOMIC TRANSACTION CLAIM
→ VALID USER-AGENT BINDING
→ VALID STATE / EXPIRY / PURPOSE
→ CALLBACK CANDIDATE
→ ORIGINAL PENDING OIDC TRANSACTION
→ LOGIN START
→ INITIATING USER-AGENT INTERACTION

### 44.4 First Google Login

LOCAL SESSION
→ canonical `UserId`
→ account creation effect
→ account creation policy
→ trusted provider subject
→ validated ID Token
→ nonce match against transaction
→ token response
→ authorization code exchange
→ original transaction-bound PKCE verifier
→ PROCESSING transaction
→ atomic claim
→ valid user-agent binding
→ original PENDING transaction
→ provider redirect flow
→ login start

No chain may terminate in provider callback alone or email equality.

### 44.5 Account Link

VISIBLE LINKED METHOD
→ auth method
→ link effect
→ authenticated existing `UserId`
→ provider subject collision check
→ trusted provider subject
→ validated ID Token
→ nonce match
→ token exchange
→ link-purpose PROCESSING OIDC transaction
→ initiating user binding
→ valid user-agent binding
→ atomic claim
→ original PENDING ACCOUNT_LINK transaction
→ authenticated link start

### 44.6 Verified Email

VISIBLE VERIFIED EMAIL
→ verified email relation
→ verification challenge consumed
→ correct proof
→ issued challenge
→ target email candidate
→ verification start

### 44.7 Recovered Account

VISIBLE RECOVERED ACCOUNT
→ restoration/replacement effect
→ recovery authority
→ verified recovery proof
→ recovery challenge
→ recovery request

### 44.8 Logged-Out State

VISIBLE LOGGED-OUT STATE
→ session no longer resolves
→ session revocation / cookie clear
→ logout request
→ authenticated session or no-op semantics

### 44.9 Authorization

VISIBLE AUTHORIZED BUSINESS ACTION
→ capability
→ authority
→ role / grant
→ membership
→ canonical `UserId`
→ authenticated session

### 44.10 Provider Cancel Error

VISIBLE PROVIDER CANCEL ERROR
→ safe cancelled projection
→ provider non-success callback
→ transaction lookup where possible
→ user-agent/state validation where possible
→ safe terminal state
→ no token exchange
→ no local session
→ no business effect

### 44.11 Failed Callback

VISIBLE FAILED CALLBACK
→ rejected/error projection
→ failure class
→ transaction state / binding / token validation failure
→ no unauthorized local effect
→ terminal or safe no-op state

### 44.12 Runtime Auth Persistence

VISIBLE AUTHENTICATION PERSISTENCE EFFECT
→ legitimate auth persistence operation
→ scoped runtime DB principal capability
→ repository DB-principal capability architecture
→ runtime service identity

No inverse chain may terminate in bootstrap/test database authority when production runtime authority is claimed.

No inverse chain may terminate in:

* frontend state
* email equality
* provider callback
* authorization code received
* token response received
* parsed token
* unclaimed transaction
* unbound browser callback
* arbitrary redirect target
* hostile local login submission
* authenticated-request CSRF proof as local login-CSRF proof
* implicit policy
* mock provider
* unpersisted convention
* unretrievable hash-only PKCE verifier
* application CSRF proof as OIDC transaction proof
* OIDC state as application CSRF proof
* bootstrap/test database authority as production runtime capability

## 45. Threat Model Requirements

### 45.1 Credential Stuffing / Password Brute Force

ATTACK INPUT: repeated password attempts.

TARGET RELATION: local credential verification.

BOUNDARY: local login-CSRF boundary, rate limiting, constant-effort unknown email behavior, password hash verification.

FALSIFIER: attacker distinguishes unknown email or brute-forces without throttling.

TEST: enumeration and rate-limit tests.

### 45.2 Account Enumeration

ATTACK INPUT: login/recovery/verification attempts against email addresses.

TARGET RELATION: identity lookup.

BOUNDARY: collapsed public errors, audit internally.

FALSIFIER: public response reveals account existence.

TEST: public error parity tests.

### 45.3 Local Password Login CSRF / Session Swapping

ATTACK INPUT: hostile origin submits attacker-selected local credentials into victim browser.

TARGET RELATION: local password login request → credential validation → fresh session commit.

BOUNDARY: local password login-CSRF boundary.

ROOT REPAIR:

LOCAL PASSWORD LOGIN REQUEST
→ LOGIN-CSRF BOUNDARY
→ CREDENTIAL VALIDATION
→ FRESH LOCAL SESSION COMMIT

FALSIFIER: hostile origin logs victim browser into attacker-selected local account.

TEST: cross-site local login submission and attacker-selected credential browser tests.

EVIDENCE: local login-CSRF boundary proof.

### 45.4 Session Fixation

ATTACK INPUT: pre-existing attacker-controlled session cookie or pre-auth state.

TARGET RELATION: successful login session creation.

BOUNDARY: fresh session relation and cookie set/replacement.

FALSIFIER: login preserves attacker-associated session identity or pre-auth state becomes authenticated session.

TEST: fixation browser test.

### 45.5 Login CSRF / Session Swapping

ATTACK INPUT: attacker-originated valid provider callback delivered to victim browser.

TARGET RELATION: OIDC callback continuation.

BOUNDARY: initiating user-agent binding.

FALSIFIER: transferred callback authenticates victim browser as attacker.

TEST: callback transplantation test.

### 45.6 OAuth State Replay

ATTACK INPUT: reused state/callback.

TARGET RELATION: OIDC transaction.

BOUNDARY: transaction lifecycle and terminal replay denial.

FALSIFIER: replayed callback creates second session.

TEST: replay callback test.

### 45.7 Authorization Code Replay

ATTACK INPUT: reused authorization code.

TARGET RELATION: token exchange.

BOUNDARY: NQUIRY transaction claim before token exchange plus provider single-use.

FALSIFIER: transaction single-use relies solely on provider code rejection.

TEST: local concurrent callback race test.

### 45.8 PKCE Verifier Leakage / Cross-Transaction Use

ATTACK INPUT: leaked or wrong verifier.

TARGET RELATION: token exchange proof.

BOUNDARY: confidential server-side verifier binding and winner-only access.

FALSIFIER: wrong transaction verifier works.

TEST: cross-transaction verifier tests.

### 45.9 Nonce Misuse / ID Token Substitution

ATTACK INPUT: forged/substituted ID Token or invalid nonce.

TARGET RELATION: ID Token trust.

BOUNDARY: signature/issuer/audience/expiration/nonce validation.

FALSIFIER: provider subject trusted before validation.

TEST: invalid token and invalid nonce tests.

### 45.10 Same-Email Account Takeover

ATTACK INPUT: external provider account with same email as existing user.

TARGET RELATION: identity equivalence.

BOUNDARY: provider subject binding / no email auto-link.

FALSIFIER: same email links accounts.

TEST: same-email collision tests.

### 45.11 Open Redirect

ATTACK INPUT: hostile redirect target.

TARGET RELATION: post-auth redirect.

BOUNDARY: redirect target validation.

FALSIFIER: browser redirected to attacker origin after auth.

TEST: open redirect tests.

### 45.12 Account Linking Takeover

ATTACK INPUT: transferred link callback or provider subject collision.

TARGET RELATION: account link authority.

BOUNDARY: authenticated session, ACCOUNT_LINK purpose, initiating user ID, user-agent binding, collision checks.

FALSIFIER: provider subject moves accounts silently.

TEST: link takeover tests.

### 45.13 Recovery Takeover

ATTACK INPUT: email string or replayed recovery token.

TARGET RELATION: recovery effect.

BOUNDARY: recovery proof, token consumption, rate limiting, human policy.

FALSIFIER: reset by email string alone.

TEST: recovery adversarial tests.

### 45.14 CSRF / CORS Misconfiguration

ATTACK INPUT: hostile origin request with credentials.

TARGET RELATION: unsafe application request or local login request.

BOUNDARY: explicit anti-CSRF for authenticated unsafe requests; explicit local login-CSRF boundary for local password login; origin-pinned CORS.

FALSIFIER: hostile origin commits effect or local login session.

TEST: CSRF/CORS/local-login-CSRF tests.

### 45.15 XSS Impact

ATTACK INPUT: script execution in application origin.

TARGET RELATION: session-protected actions.

BOUNDARY: HttpOnly tokens, server authorization, anti-CSRF where applicable.

FALSIFIER: frontend token theft via JS.

TEST: no token in frontend-visible storage.

### 45.16 Mock Provider Reaching Production

ATTACK INPUT: production mode configured with fake provider.

TARGET RELATION: production identity proof.

BOUNDARY: environment gating.

FALSIFIER: mock provider accepted in production.

TEST: production config rejects mock provider.

### 45.17 Partial Persistence Commit

ATTACK INPUT: failure after partial local effect.

TARGET RELATION: local commit.

BOUNDARY: transactional local effect or reconstructable partial relation.

FALSIFIER: partial account creation represented as full auth success.

TEST: DB failure after provider proof tests.

### 45.18 Runtime DB Principal Over-Privilege

ATTACK INPUT: runtime DB actor performs authentication persistence outside legitimate capability set.

TARGET RELATION: runtime service identity → scoped DB capability → authentication persistence operation.

BOUNDARY: runtime DB-principal capability discipline.

FALSIFIER: runtime principal can perform unauthorized auth persistence operation.

TEST: negative DB-principal capability tests.

EVIDENCE: DB-principal capability proof.

## 46. Review Evidence Requirements

A review bundle must include:

* repository HEAD
* branch
* files changed
* migrations added
* auth routes added
* persistence schema diff
* tests added
* local stack proof
* browser proof
* local login-CSRF boundary proof
* Google proof if implemented
* OIDC transaction proof
* transaction state machine proof
* atomic claim proof
* initiating user-agent binding proof
* login/session swapping prevention proof
* redirect target validation proof
* provider cancel/error proof
* concurrency proof
* PKCE verifier confidentiality proof
* ID Token validation order proof
* nonce validation order proof
* account creation boundary proof
* account linking proof
* email proof if implemented
* recovery proof if implemented
* anti-CSRF proof
* CORS proof if changed
* runtime DB-principal capability proof
* protocol callback bounded-effect proof
* adversarial proof
* authorization regression proof
* session fixation proof
* secret redaction statement
* unresolved human authority boundaries

## 47. Implementation Sequence

1. Repository binding reconstruction.
2. Authentication-method model.
3. Local credential compatibility.
4. Authenticated session evolution.
5. OIDC auth transaction field.
6. OIDC transaction state machine and atomic claim.
7. Initiating user-agent binding.
8. Redirect target validation.
9. PKCE confidential verifier binding.
10. Google provider abstraction.
11. Google OIDC start/callback.
12. Provider error/cancel callback path.
13. ID Token validation and nonce validation order.
14. Provider identity binding.
15. Account creation boundary.
16. Account linking.
17. Email verification.
18. Recovery.
19. Revocation expansion.
20. Anti-CSRF boundary, including local password login-CSRF boundary.
21. Protocol callback semantics validation.
22. Frontend login/method/error/cancel surfaces.
23. Runtime DB Principal Capability Boundary.
24. Security hardening.
25. Authorization regression.
26. Real-stack proof.
27. Real Google proof.
28. Review bundle.

Human authority decisions must be resolved before:

* product-visible provider enablement
* production password enablement
* self-registration
* account creation policy
* recovery policy
* provider email trust policy
* Workspace bootstrap behavior
* production email provider selection
* production session lifetime policy
* official multi-account/login switching UX

## 48. Final Acceptance Condition

The architecture is accepted only if:

1. No authentication relation grants authorization by side effect.
2. No email equality creates identity equivalence.
3. No provider callback alone creates local session.
4. No unknown provider subject creates user without policy.
5. No new user gains Workspace authority automatically.
6. OIDC LOGIN and ACCOUNT_LINK remain distinct.
7. LOGIN transaction is bound to legitimate initiating user-agent interaction where required.
8. Callback cannot be transplanted into unrelated browser context and create legitimate session.
9. State validation is correct.
10. PKCE is correct.
11. Nonce validation occurs only after trustworthy ID Token validation.
12. Provider subject is trusted only after token validation.
13. Transaction is atomically claimed before external exchange.
14. Only one callback reaches token exchange.
15. PROCESSING never returns to PENDING.
16. Uncertain exchange outcome is not blindly retried.
17. Provider cancel/error cannot produce local identity/session effect.
18. Provider cancel/error does not leave replayable transaction.
19. PKCE verifier is inaccessible after terminal state.
20. Redirect targets cannot create open redirect.
21. Provider redirect URI and application post-login redirect are not collapsed.
22. Session fixation is prevented.
23. Session remains opaque and server-side.
24. Revocation propagates correctly.
25. Recovery remains proof-bearing.
26. Recovery challenge is not auth method.
27. CSRF remains distinct from OIDC state.
28. OIDC callback GET does not create general GET mutation semantics.
29. CORS does not replace CSRF.
30. SameSite does not replace CSRF.
31. Local password login has explicit login-CSRF boundary proof.
32. Authenticated-request CSRF is not assumed to cover unauthenticated local password login.
33. Hostile origin cannot authenticate victim browser into attacker-selected local account.
34. CORS or SameSite alone is not claimed as sufficient local login-CSRF proof without adversarial browser/API evidence.
35. Pre-auth state, if used, does not become or fix authenticated session.
36. Runtime DB-principal capability boundary has an owning Work Unit.
37. Existing live auth persistence and newly introduced auth persistence follow the same runtime-principal discipline.
38. Bootstrap/test DB authority is not represented as production runtime authority.
39. Mock/test provider cannot become production proof.
40. Development shortcuts cannot become production proof.
41. Security material is not leaked into evidence.
42. Every material invariant has falsifier.
43. Every material FBR has root repair.
44. Every root repair propagates to consumers.
45. Work Units own all required implementation relations.
46. Implementation Sequence respects dependencies.
47. Forward Deep Sweep terminates in authoritative state.
48. Inverse Deep Sweep terminates in authoritative producer.
49. No material failure path terminates in undefined behavior.
50. No material concurrency path terminates in process-local assumption.
51. No Human Authority boundary has been silently decided.
52. No known internal contradiction remains.
53. Canonical truth lives in repository-backed identity/session/auth-method/protocol persistence or equivalent authoritative state.
54. Authentication ends at `AuthenticatedPrincipal` / `ActorIdentity`.
55. Authorization begins at membership/role/governance/authority/capability evaluation.
56. Local password remains bounded and not silently production-approved.
57. Google OIDC validates transaction, user-agent binding and provider proof before local session commit.
58. Same email never auto-links identity.
59. Account linking has explicit authority and proof.
60. Recovery has explicit challenge, verified proof and authority.
61. Revocation propagates to dependent sessions.
62. Real-stack evidence exists before implementation is claimed.
63. Provider evidence exists before provider is claimed.

## 49. Implementation Agent Directive

Do not implement from generic authentication practice.

Start from the repository.

Preserve:

* `AuthenticatedPrincipal` non-collapse
* server-side session validation
* no raw token in JSON
* local auth tests and adversarial properties
* authorization resolver boundaries
* HARD-DEP-001 separation
* ordinary safe application request non-mutation semantics
* Authorization Code Flow with PKCE

Add:

* authentication method model
* local password login-CSRF boundary
* OIDC auth transaction field
* OIDC transaction state machine
* atomic PENDING → PROCESSING claim
* initiating user-agent binding
* redirect target validation
* confidential PKCE verifier binding
* correct token exchange and ID Token validation order
* nonce validation after trusted ID Token validation
* provider error/cancel terminal path
* Google OIDC provider proof
* provider identity binding
* account creation boundary
* account linking proof
* email verification if email is used for recovery/linking
* recovery challenge and recovery proof
* revocation propagation
* session evolution
* session fixation prevention
* anti-CSRF boundary
* protocol callback bounded-effect semantics
* runtime DB-principal capability boundary
* provider test boundaries
* real-stack evidence

Do not:

* treat email as identity
* treat authorization code receipt as authenticated identity
* treat token response receipt as trusted identity
* treat parsed ID Token as validated ID Token
* validate nonce before token exchange and trusted ID Token validation
* trust provider subject before required ID Token validation
* treat provider success as session commit
* treat provider callback as local commit
* treat local password login request as login effect without login-CSRF boundary proof
* treat OIDC transaction as provider identity
* treat OIDC state as application CSRF proof
* treat application CSRF proof as OIDC transaction proof
* treat authenticated-request CSRF proof as automatic proof for unauthenticated local password login
* store PKCE verifier only as non-recoverable hash
* expose PKCE verifier to browser, frontend state, logs or proof reports
* retrieve PKCE verifier before atomic transaction claim
* allow losing callback to retrieve verifier
* let two callbacks reach token exchange
* rely on provider authorization-code rejection for local transaction single-processing
* return PROCESSING to PENDING
* blindly retry uncertain external token exchange
* reuse PKCE verifier after terminal transaction state
* use PKCE verifier from one transaction for another transaction
* accept OIDC callback without initiating user-agent binding
* allow callback transplantation to create session
* allow arbitrary post-auth redirect targets
* let provider cancel/error create local identity/session
* treat session as authority
* treat login as membership
* treat account creation as governance bootstrap
* auto-create user for unknown provider subject without account creation policy
* auto-create Workspace membership, role, governance root, authority, participation or capability from authentication
* auto-link by email
* classify recovery challenge as authentication method
* treat recovery request as recovery effect
* treat mock provider as production
* store raw tokens
* expose secrets
* accept unsafe cookie-authenticated ordinary application request without anti-CSRF proof
* accept local password login without login-CSRF boundary proof
* claim CORS alone proves local login-CSRF boundary
* claim SameSite alone proves local login-CSRF boundary
* allow pre-auth state to become or fix authenticated session
* let OIDC callback GET imply arbitrary GET mutation
* silently replace real repository relations
* harden only new auth tables while existing live auth persistence bypasses runtime DB-principal discipline
* represent bootstrap/test database authority as production runtime authority
