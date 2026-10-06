# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-22 — local self-registration: a non-actor becomes an identity that exists, and is established for normal use by verifying its own address (HD-AUTH-13)

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §11.14 (ACCOUNT CREATION BOUNDARY; `SELF_REGISTRATION_ALLOWED`: identity + method + audit, "no Workspace authority is created unless separately authorized"), §11.15 (one coherent local effect), §20.3 (IDENTITY CREATION != GOVERNANCE BOOTSTRAP), §23.6/§23.7 (unknown subject never implicit; login-CSRF class for a session-creating or identity-creating unauthenticated POST), §16 (verified-email relation), §21.16 (keyed rate limits), §31 (provenance, no secret in evidence), §45.2 (the one answer); 06 §7 ("identity is necessary, identity is not authority"); HARD-DEP-001 Option A |
| PREDECESSOR | `06eff01` (closure #4, ASP-03 live, MAIL-01/02 proven) |
| AUTHORITY | **HD-AUTH-13 (2026-10-07):** "A person may create a NQUIRY identity in production using a local e-mail address and password. Registration establishes identity only … does not grant Workspace ownership, membership, roles, grants, governance authority, Session authority, or any other domain authority. The e-mail address must be verified through the existing verified-email relation before the local identity becomes fully established for normal use." Supersedes the "no public / self-service registration" clause of NQ-DEC-056 (HD-28) for the self-service case; HD-28's operator path stays. |
| PROOF_RADIUS | WU-22 falsifiers (10) → every suite that turns a session into an actor or writes identities (WU-11..21, workspaces, session view, record decision, identity presentation, provider bootstrap, security) → hash-proven full regression at the closure |
| HUMAN_AUTHORITY_STATE | 24 §36 #3 (self-registration) and #4 (open) decided by HD-AUTH-13 for the local case (provider case: HD-AUTH-08). No new boundary. |

## THE TRANSITION (resolved from the Field, not from a dialog)
```
NON-ACTOR  --POST /auth/register {email, name, password}-->  IDENTITY EXISTS (pending)
   users row (established_at NULL) + LOCAL_PASSWORD credential + IDENTITY_CREATED
   {SELF_REGISTERED_IDENTITY, SELF_ASSERTED / SELF_ASSERTED_UNVERIFIED, PENDING_EMAIL_VERIFICATION,
    workspaceAuthority NONE} + EMAIL_VERIFICATION challenge + ONE message   — one transaction, no session
IDENTITY EXISTS  --login-->  authenticated, authentication surface open, EVERY business relation 403 IDENTITY_NOT_ESTABLISHED
IDENTITY EXISTS  --verification of ITS OWN address completes-->  ESTABLISHED (established_at set, IDENTITY_ESTABLISHED)
```
What establishes: only the verified-email relation for the identity's canonical address. What it grants: nothing — the identity may then found a workspace through the ordinary act like every identity (RED/F01), separately.

## FIRST_BROKEN_RELATION_BEFORE
No transition existed for a person without an external-provider account: the only creation paths were the host operator (HD-28) and provider bootstrap (HD-AUTH-08). The system had no notion of an identity that exists but is not yet established — every identity was established by its creation path.

## DELTA
| File | Change |
|---|---|
| `migrations/versions/a7c9e1b3d5f7_users_established_at.py` | `users.established_at` (NULL = pending), backfill `= created_at` for every pre-existing identity (all created by established paths); `auth_rate_limits.key_kind` += `REGISTRATION`; grants unchanged (table-level) |
| `packages/persistence/tables.py`, `identity_repository.py` | the column; `create(..., established_at)` (every creation path states it), `canonical_email`, `is_established`, `establish` (one conditional write) |
| `packages/application/identity_provisioning.py`, `oidc_identity.py` | HD-28 creation and provider bootstrap establish at creation |
| `packages/security/account_creation.py` | `SELF_REGISTERED_IDENTITY`, `SELF_ASSERTED`, `SELF_ASSERTED_UNVERIFIED`, `ESTABLISHED` / `PENDING_EMAIL_VERIFICATION`; the policy docstring carries HD-AUTH-13 |
| `packages/security/login_throttle.py`, `application/login_throttle.py`, `auth_runtime.py` | `ThrottleKeyKind.REGISTRATION` (5 attempts / window per client; `NQUIRY_REGISTRATION_ATTEMPTS`), `RegistrationThrottle` (every attempt counts) |
| `packages/application/local_registration.py` | `validate_registration` (HD-28's rules), `register_local_identity` (the transition; None + `REGISTRATION_REFUSED` for a taken address) |
| `packages/application/http_registration.py`, `apps/api/.../http/auth.py` | **`POST /auth/register`** → 200 `{kind: ok}` (the one answer) · 400 `rejected EMAIL_INVALID \| NAME_REQUIRED \| PASSWORD_INVALID` · 429 `RATE_LIMITED` · 503 `REGISTRATION_NOT_AVAILABLE` / `EMAIL_DELIVERY_FAILED` (rolled back, audited); availability = `SELF_REGISTRATION_ALLOWED` ∧ mail sink ∧ declared environment |
| `packages/security/request_security.py`, `application/request_security.py` | `/auth/register` is in the login-CSRF class (admitted metadata AND the JSON contract → else `LOGIN_CSRF_REJECTED`) |
| `packages/application/email_verification.py` | completing the verification of the identity's own address establishes it (`IDENTITY_ESTABLISHED`); another address does not; an established identity is untouched |
| `packages/application/http_dispatch.py`, `http_f02.py`, `apps/api/.../http/{workspaces,queries,commands}.py` | the generic gate: all three session→actor resolvers (`_resolve_actor_from_session`, `_resolve_principal_from_session`, `_with_actor`) refuse an unestablished identity with **403 `IDENTITY_NOT_ESTABLISHED`** (`IdentityNotEstablishedError`, a `NoValidSessionError` subclass with its own status so every handler's fail-closed mapping carries it); **`GET /auth/me`** += `establishment: ESTABLISHED \| PENDING_EMAIL_VERIFICATION` |
| `packages/application/http_email.py` | `GET /auth/contacts` += `registration: AVAILABLE \| UNAVAILABLE` |
| `packages/persistence/local_auth_repository.py` | `SqlAlchemyLocalSessionRepository.connection` (a sibling read in the same transaction) |
| tests | `tests/e2e/test_auth_wu22_local_registration.py` (10); 42 raw `users` inserts across the suite and `test_support` now state `established_at` (they emulate operator/seed-created identities) |

## FALSIFIERS
offered only with the open policy, a sink and an environment (`/auth/contacts` word and 503 otherwise) · registration creates the pending identity, credential, provenance (class, sources, PENDING, NONE; no secret), the challenge and ONE message, no session, no membership · a taken address: the same 200 body, no second identity, no message, `REGISTRATION_REFUSED` without the address; the impostor's password opens nothing · a pending identity logs in, reads `/auth/me` (PENDING) / identity / methods / emails, and is refused 403 `IDENTITY_NOT_ESTABLISHED` on list / create workspace, orientation and the f02 path; verifying ANOTHER address does not establish; verifying its OWN address establishes once (`IDENTITY_ESTABLISHED` after `EMAIL_VERIFICATION_COMPLETED`, `/auth/me` ESTABLISHED, `/workspaces` 200 and empty) · a delivery refusal rolls everything back (no identity, no provenance, `MAIL_DELIVERY_FAILED` audited, login 401) · malformed requests → public classes · cross-site origin and a form body → `LOGIN_CSRF_REJECTED`, nothing sent · the 6th attempt of a client → 429, another client unaffected · operator-created identities established at creation · no pre-WU-22 identity pending.

## CONSUMER DELTA (CYAN)
`/auth/contacts.registration` → offer the registration contact only on AVAILABLE; `POST /auth/register` (one answer; then the login); `/auth/me.establishment` → the "verify your address to continue" state; business reads answer 403 `IDENTITY_NOT_ESTABLISHED` for a pending identity (the chamber's verification control is the way out).

## CLAIM_CEILING
LOCAL SELF-REGISTRATION = MATERIALIZED AND PROVEN IN TEST; production = the next propagation (ASP-04: migration `a7c9e1b3d5f7`, api, web) and, for external recipients, the outbound port-25 boundary of the host (recorded in `FIELD_CLOSURE.md`).
