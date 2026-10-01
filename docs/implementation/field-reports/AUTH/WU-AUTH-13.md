# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-13 — Revocation Expansion

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-13 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-13; §7 FBR-AUTH-005; §11.9 (unlink contact); §14.6; §15.7; §16.3; §18.1–18.3; §19.2–19.3; §23.2; §31.1; §33.7; §36 #12, #13; §38 falsifiers 53, 76; §44.4 |
| PREDECESSOR | WU-AUTH-12 `f171484` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL falsifiers → AFFECTED suites (security, semantic, regression, the route sweep, WU-03/04/07/08/09/10/11/12/13, `test_http_auth`, `test_auth_handler`, HD-28's suite) + frontend gates + mocked lane. Radius widened by the provider suites (07–09) because provider resolution changed; no full repository regression (next checkpoint). |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01, HA-AUTH-02 OPEN. **Two boundaries recorded below, not crossed:** HA-AUTH-03 (24 §36 #12, last-method unlink; default "impossible" in force) and HA-AUTH-04 (who may disable an account in production; DEVELOPMENT / TEST host-operator mechanism only). §36 #13 (administrative recovery / re-enable) not materialized. |

## FIRST_BROKEN_RELATION_BEFORE

Revocation covered sessions (single, all, by method, rotation; WU-AUTH-04)
and terminal OIDC states (WU-AUTH-05/07). Missing (FBR-AUTH-005): a contact
by which an identity revokes one of its own methods / unlinks a provider,
propagation from that revocation, the last-method rule, and account disable
with its propagation (24 §18.2 "If account disabled").

## CURRENT_RELATION

**Unlink.** `POST /auth/methods/{method_id}/unlink` (own session) → the
method becomes REVOKED (conditional write; terminal at the database, WU-02's
trigger) → its provider binding becomes revoked evidence (`revoked_at`) →
every session the method produced is revoked with `METHOD_REVOKED`, the
presenting one included (cookie cleared, `currentSessionEnded`) →
`AUTH_METHOD_UNLINKED`. The last ACTIVE method is refused (`409 LAST_METHOD`);
unknown / foreign / already-revoked are one class (`403 UNLINK_DENIED`). A
provider login through an unlinked subject is denied
(`AUTHENTICATION_METHOD_REVOKED`), never re-created as a new identity; the
subject may be linked again as a new method (one ACTIVE binding per subject,
partial unique index). A local password method unlinks the same way: the
credential row stays as evidence, password login is denied by the method
state, and that password cannot be recovered by email (WU-12 eligibility).

**Account disable.** `disable_identity_by_host_operator` (and the command
`python -m nquiry_api.operator.disable_identity`, no HTTP route): one
transaction sets `users.disabled_at` + `disabled_provenance` (one-way at the
database), revokes every session with `ACCOUNT_DISABLED`, revokes every open
recovery challenge, records `ACCOUNT_DISABLED` (TB-17, actor HOST_OPERATOR).
Methods are blocked by the identity's state, not rewritten: local login,
provider login (`ACCOUNT_DISABLED` failure class), session resolution,
recovery request and recovery completion all check it, and the database
refuses any new session row for a disabled identity. Admitted in DEVELOPMENT
/ TEST only (HA-AUTH-04): PRODUCTION / STAGING refuse with
`ACCOUNT_DISABLE_EXPOSURE_UNDECIDED` and write nothing.

**Terminal transactions** (24 §18.2, proven again at the HTTP contact): from
PROCESSING, COMPLETED, FAILED_TERMINAL, CANCELLED_TERMINAL and EXPIRED a
callback never reaches the token endpoint, the state does not change, the
verifier is unavailable, and the claim is rejected.

## INVARIANTS

1. A revoked method continues no login: local (`mark_authenticated`
   conditional on ACTIVE) and provider (`authenticate` conditional on an
   unrevoked binding, an ACTIVE method and a non-disabled identity).
2. Dependent sessions end with their method (`_live_session` denies before
   propagation; propagation writes `METHOD_REVOKED`).
3. Revocation preserves evidence (24 §18.3): method row (REVOKED, terminal),
   binding row (revoked, immutable), credential row, identity row; nothing is
   deleted.
4. The last ACTIVE method cannot be unlinked (24 §14.6; HA-AUTH-03 default).
5. One ACTIVE binding per (issuer, subject) across all identities (partial
   unique index); an unlinked subject is denied at login and free to be
   linked again.
6. A disabled identity authenticates by no method, holds no session (the
   session INSERT is refused by trigger), recovers nothing (open challenges
   revoked, eligibility denied, completion denied even with a correct proof),
   and keeps its row; disable is one-way (trigger) and needs provenance (CHECK).
7. Every revocation carries its reason (closed vocabulary, unchanged in this
   unit) and its audit fact.
8. No revocation creates or removes authority (membership, role, binding,
   participation, Workspace counts unchanged).
9. Account disable is not reachable over HTTP and not admitted outside
   DEVELOPMENT / TEST.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/b9d2f4a6c8e1_auth_revocation_expansion.py` | new: `users.disabled_at` / `disabled_provenance` + CHECK + one-way trigger; `local_auth_sessions` no-disabled-identity INSERT trigger; binding uniqueness → partial unique index over unrevoked + plain index; `ACCOUNT_DISABLED` failure class |
| `packages/persistence/tables.py` | the columns, CHECK, indexes, failure reason |
| `packages/security/local_auth.py` | `account_disabled` on credential and session records |
| `packages/security/oidc_transaction.py` | `OidcFailureReason.ACCOUNT_DISABLED` |
| `packages/security/provider_identity.py` | port: `was_bound`, `find_by_method`, `revoke_for_method`; `authenticate` contract includes the identity state |
| `packages/persistence/local_auth_repository.py` | credential read carries `disabled_at`; session select joins `users` |
| `packages/persistence/identity_repository.py` | `find_by_email`, `is_disabled`, `disable` (conditional) |
| `packages/persistence/provider_identity_repository.py` | `find` = active binding only; the three new lookups; `authenticate` requires a non-disabled identity |
| `packages/application/auth_handler.py` | login and `_live_session` deny a disabled identity |
| `packages/application/oidc_identity.py` | unlinked subject → `AUTHENTICATION_METHOD_REVOKED` (no creation); disabled identity → `ACCOUNT_DISABLED` |
| `packages/application/recovery.py` | disabled identity ineligible at request and at completion |
| `packages/application/revocation.py` | new: `unlink_method` effect gate |
| `packages/application/account_disable.py` | new: disable effect gate + command entry (environment-gated) |
| `packages/application/http_revocation.py`, `apps/api/src/nquiry_api/http/revocation.py`, `main.py` | dispatch + route |
| `apps/api/src/nquiry_api/operator/disable_identity.py` | new: host-operator command |
| `apps/web/lib/api/authClient.ts`, `apps/web/app/account/security/page.tsx` | `unlinkMethod`; "Remove" per ACTIVE method (disabled, with its reason, when it is the last); current-session removal returns to `/login` |
| tests | `tests/e2e/test_auth_wu13_revocation.py` (20 cases), `apps/web/tests/lib/authMethods.test.ts` (+6), `apps/web/tests/e2e/account-security-methods.spec.ts` (+2); sweep: the unlink route registered (own-identity exempt, `method_id` placeholder); WU-08 adapter-surface pin extended (see RED_RESULT) |

## Case 2 choices (recorded)

- **Unlink = revoke** for both method kinds; no separate "disable method"
  state (24 §13.2 has ACTIVE / REVOKED only). Re-activation is not a
  transition (WU-02 trigger); re-linking creates a new method.
- **Unlinked subject denied, not re-created** (24 §18.2 "provider login
  denied"), even under `SELF_REGISTRATION_ALLOWED`: the subject is known
  evidence, and silently minting a second identity for it would be identity
  equivalence by provider success alone (24 §13.10).
- **Re-link of an unlinked subject allowed** (by whichever identity presents
  a session and the provider proof): the human controls the provider account
  and chose to unlink; the one-ACTIVE-binding rule still forbids two holders.
- **The current session's method may be unlinked**; the session ends with it
  (24 §18.2 dependent sessions) — refusing it would block removing a
  compromised method from the one browser still signed in by it.
- **Disable blocks methods instead of revoking them**, so that an eventual
  administrative recovery (§36 #13) finds the identity's methods intact; the
  DB-level session refusal and the per-path checks make the block complete
  without rewriting evidence.
- **Verification challenges are not revoked on disable**: their completion
  requires the identity's own live session, which no longer exists.
- **Operator command shape mirrors HD-28** (named operator, declared
  environment, JSON line, exit 3 refusal), but the authority to use it in
  production is not HD-28's and is left to HA-AUTH-04.

## RED_RESULT

Collection error (`application.http_revocation` / `application.account_disable`
absent): 0 of 20 could run. Repairs during the unit, all test-side: a
binding-order assertion depended on fixture dates (made order-independent);
the duplicate-binding falsifier expected the raw `IntegrityError` where the
adapter raises the typed `ProviderIdentityConflict` (WU-08's design); the
authority check queried a column that does not exist on every table (now the
WU-12 whole-table counts). Affected suites: **1 failed, 688 passed, 1
skipped** — WU-08's exact pin of the provider-identity adapter surface, which
this unit extends by three non-email lookups; the pin was extended and the
WU-08 suite rerun (13 passed). Mocked lane: green first run.

## GREEN_RESULT

20 backend cases; 6 vitest (181 total, 16 files); 2 mocked-browser cases
(33 on the AUTH lane); `tsc` and ESLint clean; ruff format / check, mypy
(256 source files), architecture / test-only import checks, migration static
+ live checks clean; migration `b9d2f4a6c8e1` downgrade / upgrade PASS.

## ADVERSARIAL_RESULT

Proven by the falsifiers: unlink without a session denied; a provider unlink
revokes the method, keeps the binding as revoked evidence, ends the sessions
of that method only, denies the next provider login with a terminal failed
transaction and leaves the identity and the other session intact; unlinking
the current session's method ends it (cookie cleared); unlinking the local
password denies password login, keeps the credential row and makes recovery
issue nothing while the provider login still works; the last ACTIVE method
is refused with nothing changed; foreign, unknown and revoked methods answer
identically; a malformed id is rejected; an unlinked subject can be linked
again and logs in through the new method; the database refuses a second
ACTIVE binding of a subject; disable ends both sessions, denies local and
provider login (own failure class), revokes the open recovery challenge and
denies its completion with the correct token, issues no new challenge, keeps
every method row ACTIVE and the identity row present, records the audit fact
with the operator, and changes no authority count; the database refuses a
session row for a disabled identity and any un-disable or re-disable; every
refusal of the disable effect (unknown, no reason, no operator, PRODUCTION,
STAGING, already disabled) writes nothing; the command refuses without a
declared environment and under PRODUCTION, succeeds under TEST; no HTTP route
disables; every non-PENDING transaction state keeps a callback out of the
token exchange, out of PENDING and without a verifier.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..12); the
guard-necessity falsifiers above stand in.

## AFFECTED_SUITES_RESULT

`tests/security`, `tests/semantic`, `tests/regression`, the route sweep,
WU-03/04/07/08/09/10/11/12/13, `test_http_auth`, `test_auth_handler`, HD-28's
suite: **688 passed, 1 skipped, 1 failed → repaired (WU-08 surface pin), WU-08
rerun 13 passed** (`evidence/wu13_proof.txt`). No full repository regression
(HD-AUTH-04).

## INVERSE_SWEEP_RESULT

A LOGIN THAT SUCCEEDS NOW → a method that is ACTIVE → never unlinked by its
identity → an identity that is not disabled → no operator disable committed
(and none possible in production yet) (24 §44.4). Conversely, every denied
login after this unit traces to a recorded fact: `authentication_methods.
revoked_at`, `external_provider_identities.revoked_at`, `users.disabled_at`,
each with its SecurityEvent.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: trust in a method is withdrawable by its owner,
withdrawal propagates to everything the method produced and leaves evidence
behind; an identity can be switched off as a whole, which propagates further
and is irreversible without a decision nobody has taken yet; and nothing in
either path deletes or re-creates. That is 24 §18.2–18.3.

## TRUE_HUMAN_AUTHORITY_BOUNDARY (recorded, not crossed) — HA-AUTH-03

```
TRUE_HUMAN_AUTHORITY_BOUNDARY
HA_ID: HA-AUTH-03 (24 §36 #12; §14.6)
CURRENT_WORK_UNIT: WU-AUTH-13
FIRST_BROKEN_RELATION: identity with one ACTIVE method → unlink request → stranded identity or refusal
EXACT_QUESTION: Is unlinking the last authentication method ever allowed, and under which explicit effect gate (recovery authority established, or account disable intended)?
WHY_NOT_DERIVABLE: 24 §36 #12 names it HUMAN_AUTHORITY_REQUIRED; §14.6 gives only the default ("must remain impossible unless …") and the two conditions under which it could become possible, both of which need relations or decisions that do not exist (self-service recovery policy HA-AUTH-02; self-disable authority).
AUTHORITATIVE_PREDECESSORS: 24 §14.6, §17.5, §18.2, §36 #12; falsifier 53; HA-AUTH-02 (recovery policy, OPEN); HA-AUTH-04 (disable authority, OPEN).
STRUCTURALLY_LEGITIMATE_OPTIONS:
  (a) NEVER — the last ACTIVE method stays; removing it means disabling the account through whatever HA-AUTH-04 decides.
  (b) ALLOWED AS SELF-DISABLE — unlinking the last method is an explicit account disable by the identity itself (needs HA-AUTH-04 to grant the identity that authority).
  (c) ALLOWED WITH RECOVERY AUTHORITY — only when a recovery path exists for that identity (needs HA-AUTH-02 ≠ DENIED and a verified email).
DEFAULT_IF_UNDECIDED: (a), in force now (`409 LAST_METHOD`).
DOWNSTREAM_RELATIONS_BLOCKED: none; the default is complete.
FILES_CURRENTLY_CHANGED: none beyond this Work Unit's own commit.
CURRENT_PROOF_STATUS: WU-AUTH-13 proven with (a) in force.
```

## TRUE_HUMAN_AUTHORITY_BOUNDARY (recorded, not crossed) — HA-AUTH-04

```
TRUE_HUMAN_AUTHORITY_BOUNDARY
HA_ID: HA-AUTH-04 (24 §18.1 "account disable", §36 #13 adjacent; HD-28 scope)
CURRENT_WORK_UNIT: WU-AUTH-13
FIRST_BROKEN_RELATION: compromised or departing identity in PRODUCTION / STAGING → account disable → all sessions revoked, all methods blocked
EXACT_QUESTION: Who may disable an NQUIRY identity in a production-like runtime (host operator, the identity itself, governance), and does the same authority cover re-enabling (§36 #13)?
WHY_NOT_DERIVABLE: 24 §18 requires the effect but names no actor; HD-28 / NQ-DEC-056 made the host operator the production identity *creator* and stated that command changes no existing identity; §36 #13 reserves administrative recovery for human authority; §17.6 "Default unresolved behavior: fail closed".
AUTHORITATIVE_PREDECESSORS: 24 §18.1–18.3, §19.2–19.3, §33.7, §36 #13; HD-28 / NQ-DEC-056; 11 §47 / TB-17 (privileged operations audited); 04 §17 (default deny).
STRUCTURALLY_LEGITIMATE_OPTIONS:
  (a) HOST_OPERATOR — extend HD-28's operator authority to disable (the command exists; lift the DEVELOPMENT / TEST gate). Re-enable stays separate (#13).
  (b) HOST_OPERATOR + SELF — additionally the identity may disable itself through its own session (would also settle HA-AUTH-03 option (b)); needs an HTTP contact that does not exist.
  (c) GOVERNANCE_MEDIATED — a governance-approved administrative action; needs relations that do not exist.
  (d) NONE YET — production identities cannot be disabled; the only response to a compromise is unlinking the compromised method by the identity itself (requires a remaining method) or operator-side credential replacement outside this Field.
DEFAULT_IF_UNDECIDED: (d) for PRODUCTION / STAGING (the mechanism refuses with ACCOUNT_DISABLE_EXPOSURE_UNDECIDED); (a) for DEVELOPMENT / TEST. Consequence of the default, stated without recommendation: a production security response that needs account disable has no path until this is decided.
DOWNSTREAM_RELATIONS_BLOCKED: production account disable; §36 #13 re-enable. NOT blocked: WU-AUTH-14..17, FIELD closure.
FILES_CURRENTLY_CHANGED: none beyond this Work Unit's own commit.
CURRENT_PROOF_STATUS: WU-AUTH-13 proven with the default in force and the mechanism proven in TEST.
```

## FIRST_BROKEN_RELATION_AFTER

**Anti-CSRF boundary** (24 WU-AUTH-14): no explicit CSRF boundary for the
state-changing browser contacts (logout-all, revoke, unlink, verification,
link start, local login), no `SameSite` / origin decision proven for them,
no local-login-CSRF mechanism, and the configurable allowed origin that the
real-stack browser proof needs.

## Limitations and ceilings

- HA-AUTH-03 and HA-AUTH-04 OPEN; §36 #13 (re-enable / administrative
  recovery) not materialized.
- Verification challenges of a disabled identity are not revoked (they are
  unreachable without a session; recorded as a Case 2 choice).
- No real-stack browser proof; no source-mutation proof; ledger deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-13 proven at the affected radius; HA-AUTH-03 and
HA-AUTH-04 OPEN with their defaults in force. Next: WU-AUTH-14.
