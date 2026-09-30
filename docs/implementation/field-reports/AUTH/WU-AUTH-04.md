# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-04 — Authenticated Session Evolution

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-04 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-04; §7 FBR-AUTH-005, FBR-AUTH-017; §15; §18; §19.3; §21.2; §21.5; §24.5; §28.3; §38 falsifiers 32–35, 51, 62, 74–76, 105 |
| PREDECESSOR | WU-AUTH-03 `bf046b9` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. §36 #10 (session lifetime) and #18 (multi-account UX) were touched and **not decided**: see "Human Authority boundaries not crossed". |

## FIRST_BROKEN_RELATION_BEFORE

Authenticated session ↔ authentication method / proof provenance, and session
revocation scope. A session could not be traced to what produced it; revoking
a method left its sessions valid; only single-session logout existed; nothing
proved that a login replaces a session identity the browser already carried.

## ROOT_SWEEP

- Producer of sessions: `application.auth_handler.login` only (no other code
  or test inserts a session).
- Consumers: `resolve_session`, called by every dispatch function in
  `http_dispatch.py` and by `http_f02._with_actor`; they receive an
  `AuthenticatedPrincipal` and are unchanged.
- Parent: the authentication method (WU-AUTH-02/-03). Siblings: credential.
- Downstream: BND-001 and the whole authorization chain consume only the
  resolved `UserId`. No authority code reads a session.

## CURRENT_RELATION

`local_auth_sessions(id, user_id, session_token_hash, issued_at, expires_at,
revoked_at, revoked_reason, authentication_method_id | proof_provenance)`.
A session authenticates exactly when: the row exists, is not revoked, is not
expired, and its method (if any) is ACTIVE.

## MUST BECOME TRUE / MUST REMAIN IMPOSSIBLE

As 24 WU-AUTH-04. All eleven "must become true" items and all eight "must
remain impossible" items have a falsifier below. FALSIFIER of the unit:
"session fixation succeeds across login."

## INVARIANTS

1. Every session names its user and either its method (same user, composite
   FK) or an explicit proof provenance (CHECK).
2. Session identity (id, user, token hash, issue time, method, provenance) is
   immutable; a revoked session never changes again; `expires_at` may only
   decrease. Trigger, for every writer.
3. `revoked_at` and `revoked_reason` appear together; the reason is one of
   LOGOUT, ALL_SESSIONS_LOGOUT, SESSION_REVOKED, METHOD_REVOKED,
   ACCOUNT_DISABLED, ROTATED.
4. Every revocation is one conditional UPDATE (`revoked_at IS NULL`): one
   writer, one time, one reason.
5. A session does not resolve once its method is REVOKED, whether or not its
   own row has been revoked yet.
6. Login always creates a new row and a new token and sets the cookie; it
   never reads the cookie the request carried.
7. A caller lists and revokes only sessions of their own identity; a foreign
   id and an unknown id are one answer.
8. Rotation revokes the presented session and creates its successor with the
   same user, attribution, `issued_at` and `expires_at`.
9. No raw token and no token hash leaves the server in JSON.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

| Relation | Producer | Consumer |
|---|---|---|
| session + attribution | `auth_handler.login` → `SqlAlchemyLocalSessionRepository.create` | `_live_session` |
| "authenticates now" | `auth_handler._live_session` (single definition) | `resolve_session`, `list_sessions`, `logout_all_sessions`, `revoke_own_session`, `rotate_session` |
| single-session scope | `logout`, `revoke_own_session` | `POST /auth/logout`, `POST /auth/sessions/{id}/revoke` |
| all-session scope | `logout_all_sessions` → `revoke_all_for_user` | `POST /auth/logout-all` |
| method scope | `revoke_for_method` | none yet (WU-AUTH-13) |
| account-disable scope | `revoke_all_for_user(reason=ACCOUNT_DISABLED)` | none yet (WU-AUTH-13) |
| rotation | `rotate_session` | none yet (WU-AUTH-10, -12, -13) |

## EXISTING_PRODUCERS_REUSED

`local_auth_sessions`, the token generator and hash, the cookie mechanics of
`http/auth.py`, `AuthenticatedPrincipal` (shape unchanged, 14 §32), the
`security` port / `persistence` adapter / `application` handler /
`http_dispatch` composition / thin HTTP adapter split of Architecture 18.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/b3d5f7a9c2e6_auth_session_evolution.py` | new: 3 columns, backfill, FK, 3 CHECKs, index, trigger |
| `packages/persistence/tables.py` | session columns and constraints |
| `packages/security/local_auth.py` | `SessionRevocationReason`; record and port extended |
| `packages/persistence/local_auth_repository.py` | session adapter: attribution, live list, four revocation scopes |
| `packages/application/auth_handler.py` | `_live_session`; `SessionRequired`; `list_sessions`, `logout_all_sessions`, `revoke_own_session`, `rotate_session` |
| `packages/application/http_dispatch.py` | `dispatch_logout_all`, `dispatch_list_sessions`, `dispatch_revoke_session` |
| `apps/api/src/nquiry_api/http/auth.py` | `POST /auth/logout-all`, `GET /auth/sessions`, `POST /auth/sessions/{id}/revoke` |
| `apps/web/lib/api/authClient.ts` | `listSessions`, `revokeSession`, `logoutAll` |
| `apps/web/app/account/security/page.tsx` | new: account security surface (own sessions) |
| `apps/web/components/f02/AppShell.tsx` | header link to the surface |
| `apps/web/playwright.auth.config.ts` | new: mocked-browser lane on a PURPLE port |
| tests | `tests/e2e/test_auth_wu04_session_evolution.py` (27), `tests/security/test_auth_migrations.py` (+1), `apps/web/tests/lib/authSessions.test.ts` (16), `apps/web/tests/e2e/account-security.spec.ts` (8) |
| `scripts/auth_wu04_mutation_proof.py` | new |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` (RED's falsifier) | +12 lines: the three new routes entered into the route sweep (see "First full regression") |

## API

| Contact | Result |
|---|---|
| `POST /auth/logout-all` | 200 `{"kind":"ok","revokedSessions":n}` + cookie cleared; 401 `denied NO_SESSION` |
| `GET /auth/sessions` | 200 `{"kind":"ok","sessions":[{sessionId, issuedAt, expiresAt, current, methodType}]}`; 401 `denied NO_SESSION` |
| `POST /auth/sessions/{id}/revoke` | 200 `ok` (cookie cleared if it was the current session); 404 `denied SESSION_NOT_FOUND` (unknown, already revoked or foreign); 400 `rejected MALFORMED_SESSION_ID`; 401 `denied NO_SESSION` |

`/auth/login`, `/auth/logout`, `/auth/me`: contracts unchanged.

These three contacts, like every existing POST, are cookie-authenticated
unsafe requests without an anti-CSRF boundary. That relation is FBR-AUTH-009,
owner WU-AUTH-14, which 24 orders after this unit. It is open, not new.

## Case 2 choices (recorded)

- **Method check at resolution and revocation on the row are both kept.**
  The resolution check is the race-free guarantee (falsifier 76); the row
  revocation with reason METHOD_REVOKED is the persisted evidence 24 §15.7 /
  §18.2 asks for and is written by the method-revocation effect (WU-AUTH-13).
- **`expires_at` may be shortened.** Existing suites simulate expiry by
  moving it into the past; shortening never widens access. Extension is refused.
- **Rotation keeps `issued_at` and `expires_at`.** Rotation is not an
  authentication, so `authentication_time` does not move, and it grants no
  extra lifetime. No lifetime policy is invented (§36 #10).
- **Backfill.** Existing sessions are attributed to the user's local password
  method (the only way a session could have been created). Already revoked
  sessions get `LOGOUT`. A session whose user has no credential is kept with
  an explicit migration provenance rather than deleted.
- **Route names** are implementation-autonomous (24 §23.2).
- **`AppShell` link.** The header of the RED-line frontend gains one link so
  the surface is reachable. CYAN's frontend is a separate line.

## Human Authority boundaries not crossed

- **§36 #10 Session lifetime policy.** The 12 h lifetime is unchanged (24
  §15.5: "Implementation may keep 12 hours until policy changes").
- **§36 #18 Multi-account UX for an already authenticated browser.** A login
  in a browser that already holds a session replaces the cookie; the earlier
  session is **not** revoked (24 §33.1 "Multiple sessions per user currently
  allowed; preserve unless policy changes"). Whether it should be is policy
  and stays open.

## MIGRATIONS

`b3d5f7a9c2e6` (revises `a2c4e6f8b1d3`). Proven on a scratch database with
predecessor-shaped rows: a live session, a revoked one and one of a user
without a credential. After the upgrade all three keep user, token hash,
issue, expiry and revocation time; the first two name the credential's
method; the revoked one has reason LOGOUT; the third carries the migration
provenance. At head the live predecessor token still resolves to the same
user with the original authentication time; the revoked one does not.
Downgrade to `a2c4e6f8b1d3` removes the three columns and keeps all three
rows. No production migration was executed.

## RED_RESULT

- Backend: collection error, `ImportError: cannot import name
  'SessionRequired' from 'application.auth_handler'` (0 of 27 could run).
- Frontend client: 16 of 16 failed (functions absent).
- Deviation (20 §12): the migration walk case and the browser spec were
  written after their implementation.

## GREEN_RESULT

Backend 27 + 3 migration walks passed. Vitest 139 passed (12 files; 16 new).
`tsc --noEmit` and ESLint clean.

## ADVERSARIAL_RESULT

- **Session fixation:** a login with a planted garbage cookie, and with
  another identity's valid session cookie, yields a new token, `/auth/me`
  reports the identity that logged in, and neither token appears in the body.
- A failed login sets no cookie.
- Revoked, expired and method-revoked sessions do not resolve.
- Raw SQL cannot un-revoke, extend or move a session, rewrite its token hash
  or attribution, revoke without a reason or with an unknown reason, create a
  session with neither method nor proof, or attach another user's method.
- A caller cannot revoke another identity's session; the answer equals the
  answer for an unknown id.
- A dead token cannot be rotated; a token rotates once.
- Session operations change no membership, role, binding, participation or Workspace row.

## MUTATION_RESULT

`scripts/auth_wu04_mutation_proof.py`: **29/29 KILLED**, sources restored.
The full run killed 28 and reported M03 as `MUTATION_SITE_NOT_UNIQUE` (the
formatter had wrapped the mutated line, so the fragment no longer matched);
the site was corrected and M03 was run alone: KILLED. M01–M18 mutate the
handler, the repository and the dispatch; M19–M29 mutate the migration and run
on scratch databases.

## SECURITY_RESULT

- Tokens: 256-bit, stored only as SHA-256; never in JSON; the session list
  contains neither token nor hash (asserted on the HTTP body).
- Cookie: `HttpOnly`, `SameSite=Lax`, `Secure` by `NQUIRY_COOKIE_SECURE`; unchanged.
- Non-enumeration: every "no valid session" cause is one `SessionRequired` / one `NO_SESSION`.
- Session is not authority: the row has no role, membership or capability
  column (asserted); the authorization regression suites are unchanged and green.

## CONSUMER_PROOF / PRESERVATION_RESULT

- Every predecessor suite that logs in and calls governed routes passes unchanged.
- MOCKED BROWSER PROOF (20 §12 class; `apps/web/playwright.auth.config.ts`,
  this tree on `:13460`): 8 new account-security cases and the 6 existing
  `auth.spec.ts` cases pass; all 47 mocked specs of the app pass on that port
  with the header link present.
- REAL-STACK BROWSER PROOF: **not run**. The real lane needs the browser
  origin to be allowed by the API, and the allowed origin is the hard-coded
  `http://localhost:3000`, which another line's stack serves on this machine.
  Making the allowed origin configuration is 24 §25.2 `NQUIRY_ALLOWED_ORIGINS`
  and belongs to the CORS boundary (WU-AUTH-14). The HTTP contract of the
  three new contacts is proven through the real FastAPI app against real
  PostgreSQL. This is a ceiling of this unit.
- Static gates: ruff clean; mypy no issues (225 files); architecture,
  provider-SDK and test-only import checks PASS.

## First full regression: one failure, repaired at its root

The first final run (tree `1a7103ed…`) ended **1 failed, 2092 passed, 2
skipped**: `tests/e2e/test_pfc_f09_2_isolation_sweep.py::test_the_sweep_covers_every_route`.
That RED falsifier derives the served routes from the application and states
in its own header: "a route added later without an entry here fails". The
three new routes were not in the sweep.

- Classification: not a defect of the routes; a missing consumer relation.
  Adding a route obliges its author to enter it in the sweep.
- Repair: the three routes were entered in `ROUTES`, so RED's
  expired-session law ("an expired session is no identity on every route")
  now also runs against them and passes (401 `denied`, nothing changed). They
  are listed as cross-Workspace-exempt next to `GET /auth/me`, for the same
  reason (they act on the caller's own identity and name no Workspace); their
  own-identity scope is proven in this unit's suite. Nothing was removed or
  weakened in RED's file.
- Found on the way: the path parameter was named `session_id`, the sweep's
  name for an inquiry Session. It is now `auth_session_id`. The URL is unchanged.
- This is the one edit PURPLE made to a file authored by another Field, and
  it is the edit that file demands.

## FULL_REPOSITORY_REGRESSION

Second run, after the repair above, with no change to the tree while it ran
(`evidence/wu04_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `2ddb929ab42d5e940a3a724af9e1efc9762e9e9f995dc88c42d4e3ab25414f37` |
| Live result | 2096 passed, 2 skipped, 0 failed, exit 0 (0:33:55) = 2065 + 27 + 1 + 3 |
| No-database result | 938 passed, 1160 skipped, 0 failed, exit 0 |
| Migrations | single head `b3d5f7a9c2e6`; live check PASS |
| Post-run tree hash | identical; git status identical |
| Frontend | vitest 139 passed; tsc and eslint clean; 47/47 mocked specs on `:13460` |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| session → method | the method of the credential whose password was just verified | AUTHENTICATION PROOF |
| session → method (backfill) | the user's only credential at migration time | DERIVED FACT, provenance in the migration |
| `revoked_reason` | the operation that revoked | CANONICAL FACT |
| `current` in the list | server comparison of session ids | DERIVED FACT |
| `methodType` in the list | joined from the method row | CANONICAL FACT |
| visible "session ended" in the UI | server `ok`, then a fresh server read | CANONICAL FACT |
| session id in `POST …/revoke` | client path segment | USER CLAIM; honored only for a session of the caller's identity |
| cookie presented to `/auth/login` | browser | USER CLAIM; never read by login |

Visible authenticated state → `/auth/me` → cookie → hash lookup → unrevoked,
unexpired session → ACTIVE method → credential proof → canonical `UserId`.
The chain now ends in a method (24 §44.1). It does not yet pass a login-CSRF
boundary (24 §44.2): UNPROVEN, owner WU-AUTH-14.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an opaque server-side session is evidence of one
authentication by one method of one identity, with a reasoned, one-way
revocation at four scopes and an identity-preserving rotation. That is 24 §15.
No second session mechanism, no token in the client, no authority on the session.

## FIRST_BROKEN_RELATION_AFTER

**OIDC Auth Transaction** (24 WU-AUTH-05; FBR-AUTH-008, -010, -013, -014):
no authoritative, expiring, purpose-bound, user-agent-bound, atomically
claimable transaction relation exists between a provider login start and its
callback. It is the next unit in 24's dependency order (depends on WU-AUTH-02).

## Limitations and ceilings

- No real-stack browser proof (above).
- Method-scope and account-scope revocation and rotation have no production
  caller until WU-AUTH-10 / -12 / -13.
- The new unsafe contacts share the open anti-CSRF relation (WU-AUTH-14).
- Human decisions are field-local; 16 §41 reconciliation deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-04 proven. Next: WU-AUTH-05.
