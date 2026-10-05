# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-20 — the login lockout boundary (24 §21.16, §22.3, §9.2 "rate limiting")

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §9.2 (official password method requires rate limiting), §21.16 ("IP/user/email-keyed rate limits, lockout/step-up policy, audit security events, … do not disclose account existence"), §22.3 ("no active lockout/rate-limit boundary"), §22 optional persistence `auth_rate_limits`, §36 #17 (thresholds adjustable by product / security policy), §31 (audit), §45 |
| PREDECESSOR | `146561e` (WU-AUTHZ-01) |
| AUTHORITY | the human mandate of 2026-10-05 (complete operational Field); LOCAL_PASSWORD official since HD-AUTH-09 |
| PROOF_RADIUS | WU-20 falsifiers (6) → every auth suite, the sweep, `tests/security` (the capability matrix now includes the new table) |
| HUMAN_AUTHORITY_STATE | none crossed: the mechanism is derived; the thresholds are the fail-closed defaults and per-deployment overrides are the operator's (§36 #17 recorded, not decided) |

## FIRST_BROKEN_RELATION_BEFORE
`login` had constant-effort failure handling but no lockout boundary: an
official password method was open to unbounded guessing (24 §22.3 names
"no active lockout/rate-limit boundary" as a condition of credential validity).

## DELTA
| File | Change |
|---|---|
| `migrations/versions/e3a5c7d9f1b4_auth_rate_limits.py`, `persistence/tables.py` | `auth_rate_limits (key_kind, key_hash) → window_started_at, failures, locked_until`; digests only; grants `auth_runtime` RW, `test_principal` RWD; downgrade proven |
| `security/login_throttle.py` (new) | `ThrottleKeyKind` CREDENTIAL / CLIENT, `ThrottlePolicy` (5 failures / 15 min window = lock; CLIENT ×10), `throttle_key` (SHA-256 of kind + normalized value), `next_window` (sliding window; a lock is never extended by refused attempts) |
| `persistence/auth_rate_limit_repository.py` (new) | get (for update) / put / clear |
| `application/login_throttle.py` (new) | `LoginThrottle.locked / failed / succeeded` |
| `application/auth_runtime.py` | `login_throttle` policy from `NQUIRY_LOGIN_LOCKOUT_FAILURES` / `_MINUTES` (positive integers, else refused at startup) |
| `application/http_dispatch.py`, `apps/api/.../http/auth.py` | the boundary decided BEFORE credential work (429 `RATE_LIMITED`, `LOGIN_RATE_LIMITED` audited, class only), failures recorded in the login transaction, success clears the address window; the CLIENT key from the first `X-Forwarded-For` hop (the deployment's edge) else the socket peer |
| `security/auth_audit.py`, `security/db_capabilities.py`, `tests/security/test_auth_db_principal.py` | `LOGIN_RATE_LIMITED`; `auth_rate_limits` in the auth principal's matrix |
| `tests/e2e/test_auth_wu20_login_lockout.py` (new) | 6 falsifiers |

## FALSIFIERS
window arithmetic (threshold, no lock extension, window reset, normalized key, CLIENT ×10) · policy configurable, nonsense refused · five failures lock the address, the right password is refused with 429 and no cookie, refusals audited without an account, a refused attempt neither counts nor extends the lock, no address in the table or the events · the lock ends with the window; a success clears the address (four failures then success → window clear) · an unknown address is locked exactly like a known one (status and body equal) · a client is locked after 50 failures across addresses even with the right password; another client still logs in.

## DISCLOSED
Step-up (second factor) is not materialized (24 §21.16 "lockout/step-up": lockout chosen; step-up needs a second factor that does not exist). The CLIENT key trusts the first `X-Forwarded-For` hop, which is only meaningful behind the deployment's own edge (the API listens on loopback there); the CREDENTIAL key does not depend on it. Rows are never deleted by the runtime (evidence); a retention policy is 16's open retention gap.
