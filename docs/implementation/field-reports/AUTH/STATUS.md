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

IN_PROGRESS.

- Worktree `worktrees/auth-identity`, branch `auth-identity`. Local commits
  only; not pushed, not tagged (HD-AUTH-03).
- Predecessor: `checkpoint-PFC-AC1.1` → `e91961e` (HD-AUTH-02).
- Human decisions: `HUMAN_DECISIONS.md` (HD-AUTH-01..03). Consumed from
  predecessors: HD-28 / NQ-DEC-056 (host-operator account creation), F02 HD-3
  (dev-only identity), F02 HD-6 (no own commit boundary in application modules).
- Open Human Authority boundaries: all 18 of 24 §36. Touched and left
  undecided so far: #10 session lifetime (12 h kept), #18 multi-account UX
  (an earlier session is not revoked by a new login).
  WU-AUTH-07: #1 / #6 (Google as an official, production-enabled method:
  instantiable from configuration, configured nowhere), #3–#5 (account
  creation: fails closed).
- External dependency: real Google proof (24 §41) needs a Google OAuth
  client (id, secret, registered redirect URI). BLOCKED_EXTERNAL.
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
| WU-AUTH-07 OIDC Provider Adapter, start / callback | PROVEN against the local test issuer; REAL GOOGLE PROOF BLOCKED_EXTERNAL (no client credentials) | this commit |
| WU-AUTH-08 Provider Identity Binding | next | — |
| WU-AUTH-09..17 | not started | — |

### Current First Broken Relation

Provider identity binding: no relation maps provider issuer + subject to a
canonical UserId; every provider login fails closed at the identity step
(owner WU-AUTH-08).

### Migrations

Head `c4e6a8b1d3f5`. Chain from the pin head `e8c2a5f1b7d4`: `f1a7c3d9b2e4`
(WU-AUTH-02 `authentication_methods`) → `a2c4e6f8b1d3` (WU-AUTH-03 credential ↔ method) → `b3d5f7a9c2e6` (WU-AUTH-04
session attribution and revocation reason) → `c4e6a8b1d3f5` (WU-AUTH-05 OIDC
transactions).

## Upstream dependencies

RED `checkpoint-PFC-AC1.1` (pinned producer of the runtime, the local
authentication adapter and HD-28). Architectures 04, 05, 06, 11, 13, 14, 18, 20.

## Downstream dependencies

- RED PFC HA-09 / HA-10 (runtime DB-principal isolation) consume WU-AUTH-17.
- CYAN (`frontend-symbiotic`) consumes any authentication projection through a
  later, separately authorized integration. This worktree carries the RED-line
  frontend.
- Ledger reconciliation of HD-AUTH-n into 16 §41 happens at integration.
