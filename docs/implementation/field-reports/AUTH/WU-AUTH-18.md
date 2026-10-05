# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-18 — authentication audit events (24 §31.1–31.3; §47 item 24 "security hardening")

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §31.1 required audit events, §31.2 provenance, §31.3 privacy; 11 §41–42 SecurityEvent; AC-11-017 (environment); F02 HD-6 (no commit boundary in application) |
| PREDECESSOR | `3aca298` (HD-AUTH-09 recorded; ASP-01 blocked on external permission) |
| AUTHORITY | the human mandate of 2026-10-04/05: continue autonomously with the next legitimate independent relation of the reconstructed PURPLE Field |
| PROOF_RADIUS | WU-18 falsifiers (10) → every auth suite (`tests/e2e/test_auth_*`, `test_http_auth`, the isolation sweep, AC1) + `tests/security` (HD-AUTH-04 affected radius: every path that now writes an event, the write-set and capability pins) |
| HUMAN_AUTHORITY_STATE | none crossed; no new boundary |

## FIRST_BROKEN_RELATION_BEFORE

AUTHENTICATION EFFECT → AUDIT EVIDENCE was partial: 24 §31.1 requires an audit
record for login success / failure, logout, session revocation (one / all),
provider login start, OIDC transaction outcomes, provider login success and
account-creation refusal. Only link, unlink, identity creation, disable,
verification and recovery emitted SecurityEvents (`STATUS.md` carried this as
"tracked for the hardening step"). Production evidence of 2026-10-04 showed
the gap concretely: the human's logins, logout and the Google login that
bootstrapped an identity left only `AUTH_METHOD_UNLINKED` and
`IDENTITY_CREATED`; the sessions and transactions had to be reconstructed from
state tables.

## DERIVED DELTA (narrowest)

| File | Change |
|---|---|
| `packages/security/auth_audit.py` (new) | closed vocabulary `AuthAuditEvent` (11 types), `ACTOR_UNAUTHENTICATED`, `FORBIDDEN_FACT_KEYS` (24 §31.3) |
| `packages/application/auth_audit.py` (new) | `record_auth_event(connection, event, environment, now, actor, facts, target_ref, never)`: one SecurityEvent on the effect's own connection (same transaction, HD-6); nothing without a declared environment; refuses a forbidden fact key and any fact value equal to / containing a secret the caller names (`never`) — `ForbiddenAuditFact` |
| `packages/application/http_dispatch.py` | `LOGIN_SUCCEEDED` (identity, session id, expiry), `LOGIN_FAILED` (failure class only — no account, no address, actor the unauthenticated client), `LOGOUT` (only when a live session ended), `ALL_SESSIONS_REVOKED` (count), `SESSION_REVOKED` (revoked id, whether the current one) |
| `packages/application/http_oidc.py` | `PROVIDER_LOGIN_STARTED` / `PROVIDER_LINK_STARTED` in the start transaction (provider, transaction id); `OIDC_TRANSACTION_FAILED` with every `_fail` (terminal reason) and for every claim / cancel rejection (reason: replay, missing, binding, purpose); `OIDC_TRANSACTION_CANCELLED` (provider error path); `PROVIDER_LOGIN_SUCCEEDED` in the login effect's transaction (provider, transaction id, method id); `PROVIDER_LOGIN_UNAVAILABLE` (account-creation boundary class). `PROTOCOL_START_WRITE_SET` += `security_events` (WU-15 measured) |
| `tests/e2e/test_auth_wu18_audit_events.py` (new) | 10 falsifiers |

Unchanged on purpose: the events that already existed (`AUTH_METHOD_LINKED`,
`AUTH_METHOD_UNLINKED`, `IDENTITY_CREATED`, `ACCOUNT_DISABLED`,
`EMAIL_VERIFICATION_*`, `RECOVERY_*`, `PASSWORD_RESET`); the anti-CSRF
middleware (24 §31.1 "anti-CSRF failure where security-relevant") writes no
event — it runs before any connection and a per-hostile-request write would
hand an attacker a write amplifier; the edge log and the 403 class remain its
evidence (disclosed, not decided here).

## FALSIFIERS

| # | Law | Proof |
|---|---|---|
| F1 | login success → one event: actor the identity, target `user:<id>`, facts exactly `{method, sessionId, expiresAt}`, `sessionId` = the issued row; neither token, password nor e-mail anywhere in any event column | `test_local_login_success_records_…` |
| F2 | login failure → one event per attempt, actor `UNAUTHENTICATED_CLIENT`, facts exactly `{method, reason}`; wrong password and unknown address are indistinguishable; no account, address or id in any column; no success event | `test_local_login_failure_is_aggregated_safely_…` |
| F3 | logout with a live session → one `LOGOUT` with the session ref; a second logout and a cookie-less logout write nothing | `test_logout_records_once_…` |
| F4 | revoking another own session → `SESSION_REVOKED {revokedSessionId, currentSessionEnded:false}`; an unknown id writes nothing; logout-all → `ALL_SESSIONS_REVOKED {revokedSessions, session}` once; a session-less logout-all writes nothing | `test_revoking_one_session_and_all_sessions_…` |
| F5 | provider link start (actor the identity) and provider login start (unauthenticated actor, target the transaction) carry only provider and transaction id; the login's success event names the same transaction and the method; a provider cancel → `OIDC_TRANSACTION_CANCELLED {provider, purpose, reason}`; state, nonce, code, cookie, subject and e-mail appear in no event | `test_provider_login_start_success_and_cancel_…` |
| F6 | a replayed callback → `OIDC_TRANSACTION_FAILED` reason `ALREADY_COMPLETED`; an unknown state → reason `MISSING_TRANSACTION`; never silent | `test_a_replayed_callback_and_an_unknown_state_…` |
| F7 | an unbound subject under DENIED → `PROVIDER_LOGIN_UNAVAILABLE` + `OIDC_TRANSACTION_FAILED` both with `ACCOUNT_CREATION_POLICY_UNRESOLVED`; no success event; subject and e-mail nowhere | `test_an_unbound_subject_under_denied_policy_…` |
| F8 | a bootstrapped login → `PROVIDER_LOGIN_SUCCEEDED` whose actor is the identity `IDENTITY_CREATED` created | `test_a_bootstrapped_login_records_success_…` |
| F9 | every type written is in the closed vocabulary (plus the pre-existing ones) | `test_every_recorded_event_type_is_in_the_closed_vocabulary` |
| F10 | the writer refuses a forbidden key (`email`) and a fact containing a named secret; writes nothing without an environment; writes with one | `test_the_writer_refuses_forbidden_keys_…` |

Mutation step: guard-necessity (removing any `record_auth_event` call, the
`principal is not None` guards, the `never=` arguments or the vocabulary
membership fails the named falsifier); no source-mutation script (disclosed,
as for the whole Field).

## AFFECTED SUITES

`evidence/wu18_proof.txt` (filled from the run): every `tests/e2e/test_auth_*`
suite, `test_http_auth`, the isolation sweep, AC1 and `tests/security`
(WU-15 write sets now include `security_events` on the start; WU-17's
capability matrix already grants `auth_runtime` INSERT on `security_events`).
ruff / mypy clean.

## DEPLOYMENT

Source only. Production takes it with the next api assembly (together with
`NQUIRY_ACCOUNT_SECURITY_PATH`, ASP-01 — blocked on external permission): no
migration, no configuration (the live `auth_runtime` role already inserts
`security_events`).

## CLAIM_CEILING

24 §31.1 human-facing authentication events = RECORDED in the effect's
transaction, ids and classes only (24 §31.3 proven by value-absence
falsifiers). Not covered: anti-CSRF / protocol-callback security failures
before any connection (disclosed above); "session replaced/rotated" after a
link (the existing `AUTH_METHOD_LINKED` event carries the rotation).
