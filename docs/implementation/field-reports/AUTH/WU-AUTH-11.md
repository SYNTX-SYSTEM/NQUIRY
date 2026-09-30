# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-11 — Email Verification

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-11 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-11; §7 FBR-AUTH-003; §13.9; §14.5; §16.1; §19.4; §21.10, §21.17; §22.2–22.3; §23.2; §24.5; §25.3; §31.1; §33.11; §36 #16; §42; §38 falsifiers 37, 43 |
| PREDECESSOR | WU-AUTH-10 `4e29c9f` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL falsifiers → AFFECTED suites (security, semantic, regression, the route sweep, the WU-04/-10 and HTTP auth suites, HD-28's suite) + frontend gates + mocked lane. No full repository regression (deferred to the next checkpoint). |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01 OPEN. §36 #16 (production email delivery provider) touched and **not decided**: no provider exists; delivery is unavailable outside the DEVELOPMENT / TEST capture sink. §36 #9 untouched (no provider-claim verification method). |

## FIRST_BROKEN_RELATION_BEFORE

Email address → verified email proof → identity relation: email was a lookup
attribute only; no challenge relation, no commit, no delivery port, no
verified relation existed (FBR-AUTH-003), blocking recovery (WU-AUTH-12) and
the "provider user adds a password" link flow (24 §14.3).

## CURRENT_RELATION

`POST /auth/email/verification/start` (session) → `auth_challenges` row
(hash only, expiry, attempt count) + `EMAIL_VERIFICATION_ISSUED` +
delivery through the mail port → `POST /auth/email/verification/complete`
(session of the same identity, challenge id + token) → one conditional
consume → `verified_emails` relation (earlier relation of the same identity
superseded) + `EMAIL_VERIFICATION_COMPLETED`. Wrong token → attempt counted +
`EMAIL_VERIFICATION_FAILED`; after `MAX_FAILED_ATTEMPTS` (5) the challenge is
spent. `GET /auth/emails` lists the caller's relations.

## INVARIANTS

1. Delivery is not verification: issuing writes no verified relation.
2. Only the token hash is stored; the token is in the delivered mail and in
   no response, row or SecurityEvent; the completion page removes it from the
   URL once used.
3. A challenge is issued to one identity for one address, expires after 30
   minutes, is consumed at most once (conditional write), may be superseded
   by a new start, counts failed attempts monotonically; consumed or revoked
   is terminal (trigger).
4. Completion needs the session of the challenge's identity; a foreign
   identity is denied without touching the challenge.
5. Resend is throttled (60 s); a new start supersedes the open challenge.
6. At most one ACTIVE verified relation per address across all identities
   (partial unique index); an address verified by another identity is refused
   at start and at completion; a re-verification by the same identity
   supersedes its earlier relation (trigger keeps supersession one-way).
7. Every public refusal of a completion is one class (`VERIFICATION_DENIED`).
8. Verification changes no session, no identity row, no authority.
9. Delivery: `NQUIRY_EMAIL_DELIVERY_MODE=capture` (DEVELOPMENT / TEST only)
   enables the in-process sink; unset → verification `unavailable`; any
   other value is refused at startup. The DEV / TEST outbox contact
   `GET /auth/test-mail/outbox` exists only with the capture sink.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/f7b9d1e3a5c8_auth_email_verification.py` | new: `auth_challenges`, `verified_emails`, triggers, partial unique index |
| `packages/persistence/tables.py` | the two tables |
| `packages/security/mail.py` | new: mail port, `CapturedMail`, `LocalMailCapture` |
| `packages/security/verification.py` | new: challenge / verified-email records, ports, token helpers |
| `packages/persistence/verification_repository.py` | new: adapters (conditional consume, attempt count, supersession) |
| `packages/application/email_verification.py` | new: issue / complete effect gate |
| `packages/application/http_email.py`, `apps/api/src/nquiry_api/http/email.py` | dispatch and routes: start, complete, `GET /auth/emails`, DEV / TEST outbox |
| `packages/application/auth_runtime.py` | `mail_sink` from `NQUIRY_EMAIL_DELIVERY_MODE` |
| `apps/api/src/nquiry_api/main.py` | router |
| `apps/web/lib/api/authClient.ts`, `apps/web/app/account/security/page.tsx`, `apps/web/app/account/verify-email/page.tsx` | verified addresses, "send verification email", completion page |
| tests | `tests/e2e/test_auth_wu11_email_verification.py` (22), `apps/web/tests/lib/authEmail.test.ts` (9), `apps/web/tests/e2e/verify-email.spec.ts` (4); sweep entries for the four new routes |

## Case 2 choices (recorded)

- **Completion requires the identity's session** (24 §16.1 "wrong-user
  denial"): the mailed link opens the app, which asks for login if needed.
  Anonymous completion would make the token alone an authority.
- **Challenge id + token** in the completion, so failed attempts can be
  attributed and limited (24 §16.1 "attempt limit"); the id is not secret.
- **One active relation per address across identities**: the conservative
  reading of "no verified email duplication policy violation" (24 §22.3) and
  the collision boundary of §14.5. A shared mailbox is a policy question and
  stays refused.
- **The address is not tied to `users.email`**: verification is a relation
  of its own (24 §13.9); email-change semantics are not materialized.
- **Environment required** for issuing and completing (audit events declare
  it, AC-11-017); `ENVIRONMENT_NOT_DECLARED` answers `unavailable`, as HD-28
  refuses an undeclared environment. Live deployment: PFC HA-20.
- **Constants:** 30-minute lifetime, 60-second resend interval, 5 attempts
  (24 §36 "exact challenge token length above security minimum" and similar
  parameters are not Human Authority; recorded as implementation constants).

## RED_RESULT

Collection error (`application.email_verification` absent), 0 of 19 could
run; the outbox and listing cases (3) were added after the first 19 were
green (classified). Frontend: the completion page first sent its request
twice under React's development double-mount and then rendered "working"
forever after the single-send guard; repaired by sharing the one request
across remounts. The mocked spec's "token not in HTML" assertion was
replaced by "token not visible and not in the URL / history after
completion", because the development server serializes the visited URL
into its own script payloads (not page content).

## GREEN_RESULT

22 backend cases; 9 vitest (167 total, 15 files); 4 mocked-browser cases (26
total on `:13460`); `tsc` and ESLint clean; static gates clean (ruff, mypy
246 files, architecture / test-only imports; one dependency finding during
the unit — a `security` import in `nquiry_api` — repaired by moving the
outbox rendering into `application`). Affected suites: see the evidence file.

## ADVERSARIAL_RESULT

Proven by the falsifiers: capture sink refused for PRODUCTION / STAGING /
unset; unknown delivery mode refused; verification unavailable without
delivery; token absent from row, response and audit facts; delivery alone
verifies nothing; correct token verifies once and replay is denied; wrong
token counted and the challenge spent after the limit (correct token then
denied); expired challenge denied; another identity's challenge denied
untouched; no session denied for both contacts; malformed inputs rejected;
resend throttled and superseded; an address verified by another identity
refused; a second verification supersedes the first; the database refuses a
second active relation per address and any change to a consumed challenge;
no session, identity or authority change; two concurrent completions verify
once.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..10).

## AFFECTED_SUITES_RESULT

`tests/security`, `tests/semantic`, `tests/regression`, the route sweep,
the WU-04 / WU-10 suites, `test_http_auth`, HD-28's suite: **556 passed, 1
skipped** (0:11:22); migration `f7b9d1e3a5c8` downgrade / upgrade PASS
(`evidence/wu11_proof.txt`). No full repository regression (HD-AUTH-04).

## INVERSE_SWEEP_RESULT

VISIBLE VERIFIED EMAIL → `verified_emails` relation → consumed challenge
(conditional write) → token proof by the challenge's identity → issued
challenge (hash) → target address candidate → verification start under the
identity's session (24 §44.6). The token itself is USER-PRESENTED material
compared against a stored hash; the address is a USER CLAIM until the
relation exists.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an address becomes a fact about an identity only
by that identity presenting a single-use secret delivered to the address, and
one address is a fact about one identity at a time. That is 24 §16.1 / §13.9.
No delivery-equals-verification, no authority, no provider dependence.

## FIRST_BROKEN_RELATION_AFTER

**Recovery** (24 WU-AUTH-12; FBR-AUTH-004): no proof-bearing recovery
challenge, no credential reset, no session effects of a reset. The recovery
policy and proof level are 24 §36 #11 (HUMAN_AUTHORITY_REQUIRED); the unit
will reach that boundary.

## Limitations and ceilings

- Production email delivery: 24 §36 #16, not decided; no provider exists.
- No real-stack browser proof (allowed origin, WU-AUTH-14); no real mail.
- No source-mutation proof; human decisions field-local; ledger deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-11 proven at the affected radius. Next: WU-AUTH-12.
