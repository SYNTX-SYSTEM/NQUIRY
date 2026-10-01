# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-12 — Recovery

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-12 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-12; §7 FBR-AUTH-004; §17.1–17.7; §15.7; §19.6; §21.10, §21.17; §22.2; §23.2; §29; §31.1; §36 #11 (#13 touched); §38 falsifiers 38, 39, 40, 54; §45.2 |
| PREDECESSOR | WU-AUTH-11 `8ae8b9e` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL falsifiers → AFFECTED suites (security, semantic, regression, the route sweep, the WU-04 / WU-10 / WU-11 suites, `test_http_auth`, HD-28's suite) + frontend gates + the mocked lane (AUTH specs and every mocked spec). No full repository regression (deferred to the next checkpoint). |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01 OPEN. **24 §36 #11 reached: HA-AUTH-02 recorded below, not crossed.** DENIED is in force; the self-service mechanism exists and is provable only in DEVELOPMENT / TEST. §36 #13 (administrative recovery) not materialized. |

## FIRST_BROKEN_RELATION_BEFORE

Loss of the local password → recovery proof → restored authentication
(FBR-AUTH-004): no recovery challenge relation, no proof gate, no credential
replacement effect, no session effect of a reset. 24 §38 #54 (a production
password method without a reset / recovery policy) stood unanswered.

## CURRENT_RELATION

`POST /auth/recovery/start` (no session; `{email}`) → if, and only if, the
runtime policy is `VERIFIED_EMAIL_SELF_SERVICE` **and** the address is an
ACTIVE verified email of an identity that holds an ACTIVE `LOCAL_PASSWORD`
method: `recovery_challenges` row (hash only, 30-minute expiry, attempt
count, provenance) + `RECOVERY_ISSUED` + delivery through the mail port. Every
well-formed request answers the same `{"kind":"ok"}` and nothing else (24
§45.2: no account enumeration); within the resend interval nothing new is
sent; a later request supersedes the open challenge.
`POST /auth/recovery/complete` (no session; `{recoveryId, token, newPassword}`)
→ one conditional verify-and-consume of the challenge → password replaced
(`replace_password`, `PASSWORD_RESET`) → every live session of the identity
revoked with `CREDENTIAL_RESET` (24 §15.7, §17.5) → `RECOVERY_COMPLETED`. No
session is created (24 §17.5 "only after … explicit session commit"; none is
committed here): the visitor logs in with the new password. A wrong token
counts a failed attempt (`RECOVERY_FAILED`); after `MAX_FAILED_ATTEMPTS` (5)
the challenge is spent. Under the default policy `DENIED` both contacts
answer `503 RECOVERY_NOT_AVAILABLE` and write nothing.

## INVARIANTS

1. A recovery request alone commits no effect (24 §17.2 REQUEST != EFFECT):
   issuing writes the challenge and the audit fact only; credential, methods,
   sessions, authority are untouched.
2. The email string is not recovery authority (24 §17.2): only an ACTIVE
   verified relation (WU-AUTH-11) of an identity with an ACTIVE local
   password method yields a challenge; `users.email` alone yields nothing.
3. Only the token hash is stored; the token travels in the mail and in the
   completion body, never in a response, a row, a SecurityEvent or (after the
   page has read it) the browser's URL / history.
4. One challenge is consumed at most once (conditional write with the row
   locked); a second concurrent completion is denied and the password is
   replaced once. Consumed or revoked is terminal; `verified_at` and
   `consumed_at` cannot be cleared or rewritten; `failed_attempts` is
   monotonic (trigger + CHECKs).
5. Expired, unknown, superseded and spent challenges are all one public
   class (`403 RECOVERY_DENIED`); a wrong token on a live
   challenge is counted before that answer is given.
6. A recovery challenge is never an authentication method: it has no
   `authentication_methods` row, `GET /auth/methods` does not list it, and no
   session points at it (24 §17.2, falsifier 39).
7. A reset replaces the credential of the challenge's identity only, keeps
   the method identity, and ends every existing session of that identity with
   the reason `CREDENTIAL_RESET` (closed vocabulary, DB CHECK).
8. A completed recovery creates no session, no membership, no role, no
   binding, no participation (24 §17.1 "authorization recovery … not an
   authentication concern").
9. The new password passes the same `PASSWORD_MIN_CHARS..PASSWORD_MAX_CHARS`
   / no-surrounding-whitespace rule as HD-28 provisioning; a rejected
   password leaves the proof unconsumed and uncounted.
10. Policy is a closed vocabulary (`DENIED`, `VERIFIED_EMAIL_SELF_SERVICE`);
    the default is `DENIED`; `VERIFIED_EMAIL_SELF_SERVICE` is refused at
    startup outside DEVELOPMENT / TEST (`RecoveryPolicyForbidden`), so no
    production runtime can self-serve recovery before HA-AUTH-02 is decided.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/a8c1e3f5b7d9_auth_recovery_challenges.py` | new: `recovery_challenges` (24 §17.3 columns, CHECKs: type vocabulary, expiry > issue, attempts ≥ 0, verified ⇒ consumed ordering, one closure, provenance), transition trigger; `CREDENTIAL_RESET` added to the session reason CHECK |
| `packages/persistence/tables.py` | `recovery_challenges_table`; reason CHECK |
| `packages/security/recovery.py` | new: `RecoveryPolicy`, `RecoveryType`, record, repository port |
| `packages/security/local_auth.py` | `SessionRevocationReason.CREDENTIAL_RESET`; `replace_password` on the credential port |
| `packages/persistence/recovery_challenge_repository.py` | new: adapter (conditional `verify_and_consume`, attempt count, supersession) |
| `packages/persistence/local_auth_repository.py` | `replace_password(user_id, password_hash, now)` |
| `packages/application/recovery.py` | new: `request_recovery` / `complete_recovery` effect gates, `validate_new_password`, constants |
| `packages/application/auth_runtime.py` | `recovery_policy` from `NQUIRY_RECOVERY_POLICY` (default DENIED; self-service DEVELOPMENT / TEST only) |
| `packages/application/http_recovery.py`, `apps/api/src/nquiry_api/http/recovery.py`, `apps/api/src/nquiry_api/main.py` | dispatch and routes: start, complete |
| `apps/web/lib/api/authClient.ts` | `startRecovery`, `completeRecovery` (fail-closed parsers; `start` accepts only `ok` / `unavailable`, so an enumerating answer would be refused by the client too) |
| `apps/web/app/login/page.tsx` | "Forgot your password?" → `/recover` |
| `apps/web/app/recover/page.tsx`, `apps/web/app/recover/reset/page.tsx` | new: request surface; completion surface (reads the link once, strips it from URL / history, keeps it in memory, submits with the new password; controls wait for hydration) |
| `apps/web/playwright.auth.config.ts` | `recover` spec in the AUTH lane |
| tests | `tests/e2e/test_auth_wu12_recovery.py` (19), `apps/web/tests/lib/authRecovery.test.ts` (8), `apps/web/tests/e2e/recover.spec.ts` (5); `test_auth_wu04_session_evolution.py` reason vocabulary (+`CREDENTIAL_RESET`); sweep: the two contacts registered as unauthenticated entry points |

## Case 2 choices (recorded)

- **Eligibility = ACTIVE verified email ∧ ACTIVE local password method.**
  Recovery of a provider-only identity ("add a password by email proof") is
  24 §17.5 "addition of new authentication method" and §14.3; it is a
  distinct policy and is not materialized. Such a request answers the same
  `ok` and issues nothing.
- **No session after completion.** 24 §17.5 allows a session only after an
  explicit session commit; the architecture names none for this flow and the
  ordinary login exists, so none is committed.
- **All sessions revoked with `CREDENTIAL_RESET`** (24 §15.7 "revocation
  propagation", §17.5 "revocation of compromised … sessions"): a reset is the
  one moment the identity has asserted loss of control.
- **Same public answer for every request** (24 §45.2). The frontend repeats
  it ("if an account can be recovered with this address …").
- **Completion is unauthenticated.** The proof is the mailed token plus the
  verified relation; requiring a session would contradict "method
  unavailable" (24 §17.1). The surface therefore holds the token in memory
  only and removes it from the URL at once.
- **Constants:** 30-minute lifetime, 60-second resend interval, 5 attempts,
  as WU-AUTH-11 (implementation constants, not §36 items).
- **Hydration gating of the request form** (`useSyncExternalStore`): before
  React owns the form a native submit would send the address as a GET query;
  the controls are disabled until hydrated. This also removed a mocked-lane
  flake where a fill before hydration was reset to empty by the first render.

## RED_RESULT

Collection error (`application.recovery` absent): 0 of 17 could run; two
cases (the "not an authentication method" listing and the concurrency case)
were written after the first green. During the unit two test defects were
repaired, not the product: the fixture did not redirect
`application.http_oidc.connect` into the test transaction, so
`GET /auth/methods` answered `NO_SESSION` on a connection that could not see
the uncommitted identity; and the session count after a reset expected 2
where the setup login made 3 (the assertion now derives the count from the
live sessions before the reset and asserts that none survives). Mocked lane:
the completion page first reported "incomplete" under React's development
double-mount (the second effect run saw the already-cleaned URL) — repaired
by capturing the link once in a ref.

## GREEN_RESULT

19 backend cases; 8 vitest (175 total, 16 files); 5 mocked-browser cases
(31 on the AUTH lane, 64 with `AUTH_SPEC_MATCH=".*"`); `tsc` and ESLint
clean; ruff format / check, mypy (251 source files), architecture /
test-only import checks, migration static + live checks clean; migration
`a8c1e3f5b7d9` downgrade / upgrade PASS (`evidence/wu12_proof.txt`).

## ADVERSARIAL_RESULT

Proven by the falsifiers: policy defaults to DENIED and is a closed
vocabulary; self-service refused for PRODUCTION / STAGING / unset; under
DENIED both contacts unavailable and nothing written; a request for an
eligible identity issues one challenge, sends one mail, changes no
credential, method, session or authority; requests for an unverified email,
a provider-only identity, an unknown address and a malformed address answer
identically to the eligible case and send nothing; repeated requests are
throttled silently and supersede (the superseded token is denied); the
correct proof replaces the credential once, old password refused, new
accepted, every pre-reset session revoked with `CREDENTIAL_RESET`, the other
browser's session gone, replay denied with nothing changed; wrong tokens
counted and the challenge spent after the limit (correct token then denied);
expired and unknown recoveries do not reset; a weak / malformed new password
is rejected and the proof kept; the challenge is not a method and not listed;
no authority and no session created; the database refuses reopening or
rewriting a consumed challenge and a non-monotonic attempt count; two
concurrent completions reset once. Frontend: the token never appears in a
URL after the page has read it, is sent in the request body only, mismatched
entries never reach the server, and the client refuses any `start` answer
that is not `ok` / `unavailable`.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..11); the
guard-necessity falsifiers above stand in.

## AFFECTED_SUITES_RESULT

`tests/security`, `tests/semantic`, `tests/regression`, the route sweep,
the WU-04 / WU-10 / WU-11 / WU-12 suites, `test_http_auth`, HD-28's suite:
**575 passed, 1 skipped** (0:11:11); migration `a8c1e3f5b7d9` downgrade /
upgrade PASS; the WU-12 suite rerun after its last falsifier was added: 19
passed (`evidence/wu12_proof.txt`). No full repository regression
(HD-AUTH-04).

## INVERSE_SWEEP_RESULT

NEW PASSWORD ACCEPTED AT LOGIN → credential replaced by `complete_recovery`
→ consumed challenge (conditional write, one closure) → token proof against
the stored hash within expiry and attempts → challenge issued only for an
ACTIVE verified email of an identity with an ACTIVE local method → request
by anyone knowing an address (24 §44.6). The address is a USER CLAIM; the
token is USER-PRESENTED material; the verified relation (WU-AUTH-11) is the
only fact that turns the claim into a challenge.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: access is regained only by presenting a
single-use secret delivered to an address that this identity has itself
proven, and regaining it ends every standing login. That is 24 §17.2's chain
REQUEST → CHALLENGE → VERIFIED PROOF → AUTHORITY → EFFECT with no step
skipped, and falsifier "attacker knowing email resets credential" fails at
the first arrow.

## TRUE_HUMAN_AUTHORITY_BOUNDARY (recorded, not crossed)

```
TRUE_HUMAN_AUTHORITY_BOUNDARY
HA_ID: HA-AUTH-02 (24 §36 #11; §17.6–17.7; #13 adjacent)
CURRENT_WORK_UNIT: WU-AUTH-12
FIRST_BROKEN_RELATION: loss of the local password in PRODUCTION / STAGING → recovery policy → restored authentication
EXACT_QUESTION: Is self-service recovery allowed in a production-like runtime, and if so with which proof level?
WHY_NOT_DERIVABLE: 24 §17.7 "Whether self-service recovery is allowed, and what proof level it requires, is HUMAN_AUTHORITY_REQUIRED"; §17.6 "Recovery policy remains HUMAN_AUTHORITY_REQUIRED … Default unresolved behavior: fail closed". No predecessor decided it; HD-28 covers host-operator provisioning, not recovery.
AUTHORITATIVE_PREDECESSORS: 24 §17, §36 #11 / #13, §38 #54; HD-28 / NQ-DEC-056 (host operator creates production identities); WU-AUTH-11 (verified email relation); HD-AUTH-01..04.
STRUCTURALLY_LEGITIMATE_OPTIONS:
  (a) DENIED — no self-service recovery; a production identity that loses its password is restored by the host operator (the HD-28 command path) or by a provider method it has linked. Nothing further to build.
  (b) VERIFIED_EMAIL_SELF_SERVICE — the mechanism of this Work Unit (ACTIVE verified email ∧ ACTIVE local password method; single-use mailed token; all sessions ended). Requires lifting the DEVELOPMENT / TEST-only refusal and a production email provider (§36 #16, undecided).
  (c) VERIFIED_EMAIL_SELF_SERVICE with an additional factor (existing provider proof or operator confirmation) — needs relations that do not exist.
  (d) OPERATOR_MEDIATED (§36 #13) — an administrative recovery command with its own audit; not materialized.
DEFAULT_IF_UNDECIDED: (a) DENIED, in force now; the runtime refuses (b) outside DEVELOPMENT / TEST.
DOWNSTREAM_RELATIONS_BLOCKED: self-service password recovery in production. NOT blocked: revocation (WU-AUTH-13), CSRF (-14), protocol callback semantics (-15), authorization regression (-16), DB principal (-17), FIELD closure.
FILES_CURRENTLY_CHANGED: none beyond this Work Unit's own commit.
CURRENT_PROOF_STATUS: WU-AUTH-12 proven with DENIED in force and the VERIFIED_EMAIL_SELF_SERVICE branch proven in TEST.
```

## FIRST_BROKEN_RELATION_AFTER

**Revocation expansion** (24 WU-AUTH-13; §18): method revocation and
provider unlink have no contact, the last-method rule (§36 #12) is not
enforced, account disable does not exist, and terminal OIDC states are not
surfaced as revocation.

## Limitations and ceilings

- Production recovery policy: HA-AUTH-02 OPEN; production delivery: §36 #16.
- Provider-only identities cannot add a password by email proof (24 §14.3,
  §17.5 "addition of new authentication method": separate policy).
- No real-stack browser proof (allowed origin, WU-AUTH-14); no real mail.
- No source-mutation proof; human decisions field-local; ledger deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-12 proven at the affected radius; HA-AUTH-02 OPEN with
DENIED in force. Next: WU-AUTH-13.
