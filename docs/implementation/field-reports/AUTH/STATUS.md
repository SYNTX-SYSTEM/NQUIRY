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
- Open Human Authority boundaries: all 18 of 24 §36; none reached yet.

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
| WU-AUTH-02 Authentication Method Model | PROVEN | this commit |
| WU-AUTH-03 Local Credential Migration Compatibility | next | — |
| WU-AUTH-04..17 | not started | — |

### Current First Broken Relation

Local credential ↔ authentication method: credentials belong to no method and
login does not consult method status (owner WU-AUTH-03).

### Migrations

Head `f1a7c3d9b2e4` (WU-AUTH-02: `authentication_methods`). Pin head was `e8c2a5f1b7d4`.

## Upstream dependencies

RED `checkpoint-PFC-AC1.1` (pinned producer of the runtime, the local
authentication adapter and HD-28). Architectures 04, 05, 06, 11, 13, 14, 18, 20.

## Downstream dependencies

- RED PFC HA-09 / HA-10 (runtime DB-principal isolation) consume WU-AUTH-17.
- CYAN (`frontend-symbiotic`) consumes any authentication projection through a
  later, separately authorized integration. This worktree carries the RED-line
  frontend.
- Ledger reconciliation of HD-AUTH-n into 16 §41 happens at integration.
