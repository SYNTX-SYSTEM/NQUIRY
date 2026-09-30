# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-10 — Account Linking

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-10 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-10; §11.21; §14.1–14.4, §14.7; §15.6; §19.5; §23.2; §24.5; §33.5; §44.5; §38 falsifiers 59–61, 91 |
| PREDECESSOR | WU-AUTH-09 `8d3df59` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03; HA-AUTH-01 OPEN (unchanged). No new boundary: linking requires an authenticated identity and grants nothing. 24 §14.2 "additional step-up may be required if method is high risk" is not decided (no step-up policy exists; noted). |

## FIRST_BROKEN_RELATION_BEFORE

An authenticated identity could not add a provider method: no ACCOUNT_LINK
start or callback contact, no link effect, no collision rule exercised for a
subject bound elsewhere, no link audit, no listing of an identity's methods.

## CURRENT_RELATION

AUTHENTICATED SESSION → `POST /auth/oidc/{p}/link/start` → ACCOUNT_LINK
transaction bound to the identity and the browser → provider → `GET
/auth/oidc/{p}/link/callback` (24 §16.2 order with purpose ACCOUNT_LINK and
the current session's identity as the initiating user, checked before the
claim) → provider proof → link effect (subject not bound elsewhere → method +
binding + `AUTH_METHOD_LINKED` SecurityEvent) → session rotation → COMPLETED →
`/account/security?link=ok`. Own subject already linked → `already_linked`;
subject bound to another identity → `PROVIDER_SUBJECT_COLLISION`, nothing moves.

## INVARIANTS

1. Link start needs a live session; the transaction binds the identity.
2. LOGIN and ACCOUNT_LINK use separate callback contacts with separate
   registered redirect URIs; a transaction of one purpose is refused by the
   other's callback before any exchange (`PURPOSE_MISMATCH`, terminal).
3. The link callback requires the session of the initiating identity; a
   different or missing session is refused before the exchange
   (`INITIATING_USER_MISMATCH`, terminal).
4. The browser binding applies to links as to logins.
5. A subject already bound to another identity never moves; a subject
   already bound to the caller is not a second method.
6. Link effect and audit are one transaction; the current session is rotated
   after a successful link (24 §15.6); the old token is dead, the identity unchanged.
7. `GET /auth/methods` lists only the caller's own methods, with the provider
   attribute (provider id, email), never a subject or a secret.
8. A link creates no membership, role, binding of authority, participation or Workspace.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/security/oidc_provider.py`, `oidc_standard.py`, `oidc_test_issuer.py` | purpose-specific redirect URIs (`link_redirect_uri`; `authorization_url` / `exchange_code` take the URI); test issuer accepts both |
| `packages/application/auth_runtime.py` | `NQUIRY_GOOGLE_LINK_REDIRECT_URI` (optional; default derived) |
| `packages/application/oidc_identity.py` | `link_provider_identity`, `list_methods` |
| `packages/security/provider_identity.py`, `packages/persistence/provider_identity_repository.py` | `list_for_user` |
| `packages/application/http_oidc.py` | shared protocol steps for both purposes; `dispatch_oidc_link_start`, `dispatch_oidc_link_callback`, `dispatch_list_methods` |
| `apps/api/src/nquiry_api/http/oidc.py` | `POST /auth/oidc/{provider}/link/start`, `GET /auth/oidc/{provider}/link/callback`, `GET /auth/methods`; consent page accepts the link redirect URI |
| `apps/web/lib/api/authClient.ts`, `apps/web/app/account/security/page.tsx` | methods list, link actions (form POST), link projections |
| tests | `tests/e2e/test_auth_wu10_account_linking.py` (14), `apps/web/tests/lib/authMethods.test.ts` (10), `apps/web/tests/e2e/account-security-methods.spec.ts` (4); WU-08 suite: repository surface + `list_for_user` |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` | the three new routes entered (own-identity routes as cross-Workspace-exempt; the link callback as an unauthenticated protocol contact) |

No migration.

## Case 2 choices (recorded)

- **Separate link callback route and redirect URI** (24 §11.21 recommends
  them): it makes the purpose check a real check. Google's link URI defaults
  to the login URI with `/link/callback`; both must be registered at the provider.
- **Link start is a POST** (it creates state for the caller); the frontend
  navigates to it with a form so the provider redirect can be followed.
  Like every existing unsafe cookie-authenticated request it has no
  anti-CSRF boundary yet (FBR-AUTH-009, WU-AUTH-14).
- **Rotation after a link** replaces the current session's token; the
  identity, issue time and expiry are unchanged (WU-AUTH-04 rules).
- **Already-linked own subject** is a no-op success with its own projection,
  not an error and not a duplicate method.
- **A revoked binding of the caller's own subject** counts as a collision
  (re-linking a revoked binding is a recovery / unlink-history question for WU-AUTH-13).

## RED_RESULT

14 of 14 failed (routes absent; 404 responses and missing cookies). After the
first implementation 2 of 14 failed on method ordering: the fixture dates the
local method in 2030 while a link is dated now, so the created-at order put
the provider method first; the assertions were made order-independent
(production ordering unchanged). The WU-08 repository-surface case was
extended by `list_for_user`.

## GREEN_RESULT

14 new backend cases; 10 vitest; 4 mocked-browser cases; with the WU-04,
-07, -08, -09 suites, `test_http_auth`, `tests/security`, `tests/semantic`,
`tests/regression`: 485 passed, 1 skipped; the route sweep (87) passes with
the new entries. Frontend: vitest 158 (14 files), `tsc` and ESLint clean, 22
mocked specs on `:13460`.

## ADVERSARIAL_RESULT

Proven by the falsifiers: link start without a session denied; unconfigured
provider unavailable; a subject bound to another identity refused as a
collision with nothing moved and the intruder's session untouched; own
subject not duplicated; link callback with another identity's session, with
no session, with a LOGIN transaction, or without the browser binding refused
before any exchange; a LOGIN callback refusing a link transaction; provider
cancel during a link terminal without effect; no authority created; the
methods list free of subjects and secrets and denied without a session.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..09).

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete (`evidence/wu10_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `5a4785c3011cb199600588d1f3a7bf0b9d0c4c6fdbd416e392334914899f402f` |
| Live result | 2235 passed, 2 skipped, 0 failed, exit 0 (0:42:52) = 2219 + 14 + 2 |
| No-database result | 986 passed, 1251 skipped, 0 failed, exit 0 |
| Migrations | single head `e6a8c1d3f5b9` (unchanged); live check PASS |
| Post-run tree hash | **different** — see disclosure |
| Frontend | vitest 158; tsc, eslint clean; 22 mocked specs on `:13460` |

**Disclosure (process deviation).** While this run was executing, the
operator's proof-cadence decision (HD-AUTH-04) arrived and was written into
`HUMAN_DECISIONS.md` and `STATUS.md`. The tree therefore differed at the end
of the run. It was verified afterwards that the difference is exactly those
two documentation additions (removing them reproduces the pre-run hash;
re-adding them reproduces the post-run hash) and that no source, test,
migration or configuration file changed. The counts are those of the pre-run
tree. Under HD-AUTH-04 this run is the Field's current broad preservation
checkpoint; the next full repository regression runs at a chosen checkpoint
or at Field closure.

## INVERSE_SWEEP_RESULT

VISIBLE LINKED METHOD → auth method → link effect → authenticated existing
`UserId` (the session at start AND at callback) → provider subject collision
check → trusted provider subject → validated ID Token → nonce → exchange →
link-purpose PROCESSING transaction → initiating user binding → user-agent
binding → atomic claim → PENDING ACCOUNT_LINK transaction → authenticated
link start (24 §44.5). Every link terminates in authoritative state; email
takes no part.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an identity extends its own set of methods by a
provider proof made in its own browser, under its own session, for a subject
not owned by anyone else. That is 24 §14.2. No second linking path, no
email-based linking, no authority.

## FIRST_BROKEN_RELATION_AFTER

**Email verification** (24 WU-AUTH-11; FBR-AUTH-003): no verified-email
relation, no challenge issuance / completion, no local delivery sink; email
remains a lookup attribute without proof, which blocks recovery (WU-AUTH-12)
and the "Google user adds password" link flow (24 §14.3).

## Limitations and ceilings

- No anti-CSRF boundary on the link-start POST (WU-AUTH-14).
- Real Google proof BLOCKED_EXTERNAL; real-stack browser lane blocked (WU-AUTH-14).
- Unlink and last-method semantics: WU-AUTH-13 (with the §36 #12 boundary).
- No source-mutation proof; human decisions field-local.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-10 proven. Next: WU-AUTH-11.
