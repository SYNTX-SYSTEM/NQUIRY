# FIELD STATUS

## Field

AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)

## Semantic regime

`docs/architecture/24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`
(WU-AUTH-01..17). Authentication resolves an identity proof into a canonical
`UserId` and a local session. It ends at `AuthenticatedPrincipal` /
`ActorIdentity` and never produces membership, role, binding, participation,
Session control, capability or governance root.

## Status

**FIELD_GREEN — READY_FOR_HUMAN_REVIEW** (2026-10-01). Review bundle:
`FIELD_REVIEW.md`. Closure regression (`evidence/field_closure_regression.txt`,
HEAD `b939037`): live 2456 passed / 2 skipped, no-DB 1020 passed,
42 migrations single head `c1e3a5b7d9f2`, tree hash unchanged during the
run; vitest 181; mocked lanes 33 / 66; real stack 8 / 8 (authentication
persistence scoped). Open Human Authority: HA-AUTH-01, -02, -03, -05
(HA-AUTH-04 resolved by HD-AUTH-05).

- Worktree `worktrees/auth-identity`, branch `auth-identity`. Local commits
  only; not pushed, not tagged (HD-AUTH-03).
- Predecessor: `checkpoint-PFC-AC1.1` → `e91961e` (HD-AUTH-02).
- Human decisions: `HUMAN_DECISIONS.md` (HD-AUTH-01..03). Consumed from
  predecessors: HD-28 / NQ-DEC-056 (host-operator account creation), F02 HD-3
  (dev-only identity), F02 HD-6 (no own commit boundary in application modules).
- **HA-AUTH-01 OPEN** (WU-AUTH-09): production account creation policy for
  unknown provider subjects; DENIED in force. Block in `WU-AUTH-09.md`,
  queue in `HUMAN_DECISIONS.md`.
- **HA-AUTH-02 OPEN** (WU-AUTH-12): production recovery policy and proof
  level (24 §36 #11); DENIED in force, the verified-email self-service
  mechanism is refused outside DEVELOPMENT / TEST. Block in `WU-AUTH-12.md`.
- **HA-AUTH-03 OPEN** (WU-AUTH-13): unlinking the last authentication method
  (24 §36 #12); refused (`LAST_METHOD`) in force. Block in `WU-AUTH-13.md`.
- **HA-AUTH-04 RESOLVED** by HD-AUTH-05 (2026-10-01): identity disable
  authority = HOST_OPERATOR (HD-28 extended), every declared environment;
  no HTTP route, no self-disable, no derived authority; re-enable separate.
- **HA-AUTH-05 OPEN** (WU-AUTH-17; = PFC HA-10): switching the deployment /
  compose runtime to the scoped `auth_runtime` principal
  (`NQUIRY_AUTH_DATABASE_URL`); the runtime declares `UNSCOPED_BOOTSTRAP`
  until then. Block in `WU-AUTH-17.md`.
- **Proof cadence (HD-AUTH-04, 2026-10-01):** progressive proof radius from
  WU-AUTH-11 on; the WU-AUTH-10 full run is the current broad checkpoint;
  the next full repository regression at a chosen checkpoint or Field closure.
- Open Human Authority boundaries: all 18 of 24 §36.
  WU-AUTH-12: #11 recorded as HA-AUTH-02; #13 (administrative recovery) not
  materialized.
  WU-AUTH-13: #12 recorded as HA-AUTH-03; disable authority recorded as
  HA-AUTH-04; #13 (re-enable) not materialized.
  WU-AUTH-11: #16 (production email delivery provider) — no provider exists;
  delivery is unavailable outside the DEVELOPMENT / TEST capture sink. Touched and left
  undecided so far: #10 session lifetime (12 h kept), #18 multi-account UX
  (an earlier session is not revoked by a new login).
  WU-AUTH-07: #1 / #6 (Google as an official, production-enabled method:
  instantiable from configuration, configured nowhere), #3–#5 (account
  creation: fails closed).
- External dependency: real Google proof (24 §41) needs a Google OAuth
  client (id, secret, registered redirect URI). BLOCKED_EXTERNAL.
- **AUTH real-stack lane (WU-AUTH-14):** `scripts/auth_real_stack.sh` (API
  :18460, app :13470, hostile origin :13471, database `nquiry_purple_real`,
  never the pytest proof database). `AUTH_REAL_SPEC_MATCH=".*"` runs every
  real-stack spec of the repository on it (8 passed at WU-14).
- Tracked for the hardening step (24 §47 item 24): `auth_events` /
  SecurityEvents for login, logout, session and provider events (24 §31.1).

### Baseline (the pin, before any PURPLE change)

| Lane | Result |
|---|---|
| Live PostgreSQL (`nquiry_purple_test`, head `e8c2a5f1b7d4`) | 2007 passed, 2 skipped (0:38:39) |
| Migrations | `MIGRATION_STATIC_CHECK::PASS (32 revisions, single head e8c2a5f1b7d4)`; `MIGRATION_LIVE_CHECK::PASS` |

RED's record at WU-PFC-AC1 was 2005 / 2; AC1.1 added 2 packaging tests.
The baseline run overlapped with the creation of WU-AUTH-02 files; collection
preceded them, so the counts are those of the pin.

### Work Units

| Work Unit | State | Commit |
|---|---|---|
| WU-AUTH-01 Repository Binding Reconstruction | PASS (evidence) | `a0f5982` |
| WU-AUTH-02 Authentication Method Model | PROVEN | `53823d6` |
| WU-AUTH-03 Local Credential Migration Compatibility | PROVEN | `bf046b9` |
| WU-AUTH-04 Authenticated Session Evolution | PROVEN | `3ffbd1b` |
| WU-AUTH-05 OIDC Auth Transaction Field | PROVEN (mutation step: guard-necessity falsifiers only, see report) | `4495345` |
| WU-AUTH-06 Redirect Target Validation | PROVEN (same mutation disclosure) | `69b806a` |
| WU-AUTH-07 OIDC Provider Adapter, start / callback | PROVEN against the local test issuer; REAL GOOGLE PROOF BLOCKED_EXTERNAL (no client credentials) | `5aa13ae` |
| WU-AUTH-08 Provider Identity Binding | PROVEN | `e097de1` |
| WU-AUTH-09 Account Creation Boundary | PROVEN; HA-AUTH-01 OPEN (production policy), DENIED in force | `8d3df59` |
| WU-AUTH-10 Account Linking | PROVEN (broad checkpoint: live 2235 / 2) | `4e29c9f` |
| WU-AUTH-11 Email Verification | PROVEN at the affected radius (HD-AUTH-04) | `8ae8b9e` |
| WU-AUTH-12 Recovery | PROVEN at the affected radius; HA-AUTH-02 OPEN (production policy), DENIED in force | `f171484` |
| WU-AUTH-13 Revocation Expansion | PROVEN at the affected radius; HA-AUTH-03 (last method) and HA-AUTH-04 (disable authority) OPEN, defaults in force | `171a6e7` |
| WU-AUTH-14 Anti-CSRF Boundary | PROVEN at an escalated radius (security + semantic + regression + all of tests/e2e: 1388 / 2) incl. the real browser/API contract (AUTH real lane) | `26a134c` |
| WU-AUTH-15 Protocol Callback Semantics | PROVEN (declared contacts + write sets, measured over every table) | `5fe3cd6` |
| WU-AUTH-16 Authorization Regression | PROVEN (6 identity kinds × the full protected route table; no code delta) | `a4c3bc3` |
| WU-AUTH-17 Runtime DB Principal Capability Boundary | PROVEN in TEST (auth_runtime, exact capability matrix, live paths scoped, real lane scoped); HA-AUTH-05 (= PFC HA-10 deployment switch) OPEN | `b939037` |

### Current First Broken Relation

None inside 24 §37's seventeen Work Units. Field closure (24 §46) is next:
the one full fresh repository regression, the review bundle, FIELD_GREEN.

### Migrations

Head `c1e3a5b7d9f2`. Chain from the pin head `e8c2a5f1b7d4`: `f1a7c3d9b2e4`
(WU-AUTH-02 `authentication_methods`) → `a2c4e6f8b1d3` (WU-AUTH-03 credential ↔ method) → `b3d5f7a9c2e6` (WU-AUTH-04
session attribution and revocation reason) → `c4e6a8b1d3f5` (WU-AUTH-05 OIDC
transactions) → `d5f7b9c1e3a7` (WU-AUTH-08 provider identities) → `e6a8c1d3f5b9` (WU-AUTH-09
account creation failure classes) → `f7b9d1e3a5c8` (WU-AUTH-11 challenges and
verified emails) → `a8c1e3f5b7d9` (WU-AUTH-12 recovery challenges, `CREDENTIAL_RESET`) →
`b9d2f4a6c8e1` (WU-AUTH-13 account disable, one active binding per subject, `ACCOUNT_DISABLED`) →
`c1e3a5b7d9f2` (WU-AUTH-17 `auth_runtime` grants, session-resolution reads).

## Upstream dependencies

RED `checkpoint-PFC-AC1.1` (pinned producer of the runtime, the local
authentication adapter and HD-28). Architectures 04, 05, 06, 11, 13, 14, 18, 20.

## Downstream dependencies

- RED PFC HA-09 / HA-10 (runtime DB-principal isolation) consume WU-AUTH-17.
- CYAN (`frontend-symbiotic`) consumes any authentication projection through a
  later, separately authorized integration. This worktree carries the RED-line
  frontend.
- Ledger reconciliation of HD-AUTH-n into 16 §41 happens at integration.
