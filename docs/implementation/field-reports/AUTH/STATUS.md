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

**FIELD_GREEN ON CURRENT HEAD — READY_FOR_HUMAN_REVIEW** (2026-10-01).
Final global preservation proof on `b47bc78` (after HD-AUTH-05 / -06):
`evidence/final_global_preservation_b47bc78.txt` — live 2456 passed / 2
skipped (0:42:54), no-DB 1020, tree hash unchanged, migration head
`c1e3a5b7d9f2` unchanged, 0 failed. Earlier closure proof at `febf117`:
`FIELD_REVIEW.md`. Closure regression (`evidence/field_closure_regression.txt`,
HEAD `b939037`): live 2456 passed / 2 skipped, no-DB 1020 passed,
42 migrations single head `c1e3a5b7d9f2`, tree hash unchanged during the
run; vitest 181; mocked lanes 33 / 66; real stack 8 / 8 (authentication
persistence scoped). Open Human Authority: HA-AUTH-02 (recovery), HA-AUTH-03 (last method)
(HA-AUTH-01 / -07 resolved by HD-AUTH-08; -04 / -05 by HD-AUTH-05 / -06).

- Worktree `worktrees/auth-identity`, branch `auth-identity`. Local commits
  only; not pushed, not tagged (HD-AUTH-03).
- Predecessor: `checkpoint-PFC-AC1.1` → `e91961e` (HD-AUTH-02).
- Human decisions: `HUMAN_DECISIONS.md` (HD-AUTH-01..03). Consumed from
  predecessors: HD-28 / NQ-DEC-056 (host-operator account creation), F02 HD-3
  (dev-only identity), F02 HD-6 (no own commit boundary in application modules).
- **HA-AUTH-01 RESOLVED** by HD-AUTH-08 (2026-10-04): generic provider
  bootstrap (`SELF_REGISTRATION_ALLOWED`, PROVIDER_BOOTSTRAP class) admitted
  in every declared environment incl. PRODUCTION; default DENIED unchanged.
- **HA-AUTH-02 OPEN** (WU-AUTH-12): production recovery policy and proof
  level (24 §36 #11); DENIED in force, the verified-email self-service
  mechanism is refused outside DEVELOPMENT / TEST. Block in `WU-AUTH-12.md`.
- **HA-AUTH-03 OPEN** (WU-AUTH-13): unlinking the last authentication method
  (24 §36 #12); refused (`LAST_METHOD`) in force. Block in `WU-AUTH-13.md`.
- **HA-AUTH-04 RESOLVED** by HD-AUTH-05 (2026-10-01): identity disable
  authority = HOST_OPERATOR (HD-28 extended), every declared environment;
  no HTTP route, no self-disable, no derived authority; re-enable separate.
- **HD-AUTH-08 deployed 2026-10-04:** live api = auth-identity `e069fc1`, head
  `d2f4a6b8c1e3`, `NQUIRY_ACCOUNT_CREATION_POLICY=SELF_REGISTRATION_ALLOWED`
  (generic provider bootstrap live); recovery DENIED, test provider absent;
  `GET /auth/identity` live since the IP01 deploy. **HA-AUTH-07 transition
  executed by the human on production 2026-10-04** (unlink 14:25:01Z →
  generic bootstrap 14:28:16Z, identity class PROVIDER_BOOTSTRAP_IDENTITY,
  `tobi` unchanged): `evidence/ha_auth_07_production_transition.txt`. Google
  LOGIN, ACCOUNT_LINK and PROVIDER_BOOTSTRAP are each proven live once.
- **HA-AUTH-05 RESOLVED** by HD-AUTH-06 (2026-10-01): SWITCH AUTH ONLY —
  local compose configured (`NQUIRY_AUTH_DATABASE_URL` → `auth_runtime`);
  the live deployment switch is recorded as a procedure for the deployment
  act and not executed (PFC HA-10).
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
| PURPLE_IDENTITY_PRESENTATION_01 (post-closure Field, 2026-10-04) | PROVEN at the affected radius: `GET /auth/identity` (self, `displayName`=`users.name`, `canonicalEmail`=`users.email`, method-invariant); F-IP-1 disclosed | this commit |
| PROVIDER_BOOTSTRAP_01 (post-closure Field, 2026-10-04) | PROVEN in TEST: generic provider-driven identity (24 §11.14) — no name invention (`PROVIDER_PROFILE_INCOMPLETE`), provenance of name/email, re-bootstrap after unlink, collision refusal; production policy still DENIED (HA-AUTH-01) | this commit |

### Current First Broken Relation

None inside 24 §37's seventeen Work Units (closed). Post-closure:
PURPLE_IDENTITY_PRESENTATION_01 materialized `GET /auth/identity`; next Field
is CYAN's consumption of it (separate authorization); production deployment of
the contact is a separate deployment act.

### Whole-software reconstruction (2026-10-04, mandate "authentication and authorization complete across the entire software")

Reconstructed from source (this branch, `frontend-symbiotic` HEAD `618d7a6`
read-only), production runtime (api `e069fc1`, web root = CYAN `field-CY-01`
`54f8b4f`, staged `/cy-review/` = CYAN `bfd5300`), persistence and the
proof lineage of both lines.

| Layer | State | Evidence |
|---|---|---|
| Authentication, API | 24 §37 closed; LOGIN / LINK / UNLINK / PROVIDER_BOOTSTRAP proven live | this file, `evidence/` |
| Authorization, API | server-resolved `ActorIdentity` on every business route; boundary chain BND-001→005→014 per handler; sweep covers 43 + 11 of 54 routes; six identity kinds denied everywhere (WU-16) | `tests/e2e/test_pfc_f09_2_isolation_sweep.py`, `test_auth_wu16_authorization_regression.py` |
| Authentication, product web (CYAN HEAD, staged) | login, provider button, identity presentation, read-only methods / sessions, logout | CYAN `WU-AUTH-CYAN-01..03`, `WU-AUTH-CYAN-IDENTITY-01`, `WU-CYAN-IDENTITY-PRESENTATION-CONSUMPTION-01` |
| Authentication, product web (live root) | local login + logout only — no provider button, no identity, no method / session surface | `WU-CYAN-REAL-E2E-ASSEMBLY-01.md:29` (CYAN) |
| Authorization, product web | role = label, every control gated by a server capability | CYAN `lib/field/humanPosition.ts` |

First Broken Relations, in dependency order:

1. **PURPLE → CYAN contract (CLOSED by `CONSUMER_CONTRACT.md`):** CYAN's
   FIELD_RECONSTRUCTION_HOLD waited for PURPLE's reconstructed identity
   contract. Stated: shapes unchanged; presentation is a function of
   `userId`; LOCAL / GOOGLE_LINKED / GOOGLE_BOOTSTRAP are the three cases;
   live proof of each relation.
2. **CYAN stale expectation (CLOSED on branch `auth-cyan-reconstruction`,
   worktree `worktrees/auth-cyan`, base `frontend-symbiotic` `618d7a6`;
   `94759cd`..`0f24465`, not pushed):** F2/F3/F4 named as GOOGLE_LINKED,
   GOOGLE_BOOTSTRAP falsifiers added, contract stated in `authClient.ts`,
   producer pin → `e069fc1`, review guide split; HOLD lifted in CYAN's
   `HA-AUTH-CYAN.md`.
3. **24 §24.5 account-security contacts (CLOSED, same branch — AUTH/CYAN-ACCOUNT-01):**
   the "Access security" chamber on `/workspaces` (methods with Remove,
   "Add <provider>" link form, sessions with End, Sign out everywhere, the
   `?link=` result, per-method last use); the login provider contact
   generalized over the parsed provider list. Proof: vitest 672, mocked
   lanes cy09 24 / 24 + preservation green, and the **cross-lineage real
   lane** `scripts/run_auth_cyan_real_lane.sh` (this API from this branch +
   the CYAN web + `nquiry_purple_real` + real Chromium): LOCAL → LINK →
   PROVIDER_LINKED → UNLINK, SESSIONS, PROVIDER_BOOTSTRAP — 6 / 6. Staged
   on `https://nquiry.condyn.eu/cy-review/` from `94759cd` (web only; live
   root untouched).
4. **Live root web — CLOSED 2026-10-04T15:59Z:** after the human's Frontend
   Acceptance on `/cy-review/`, the accepted CYAN candidate (`94759cd`) was
   published to the production root (human-authorized, human-run
   `cutover-cyanroot.sh`; web only; api / DB / `.env` / vhost unchanged;
   record and proof in CYAN `WU-AUTH-CYAN-ACCOUNT-01.md`). The authentication
   Field is now reachable by a human through the deployed UI (local login,
   Google login, identity presentation, account security). **Final Human
   Acceptance on `https://nquiry.condyn.eu/`: ACCEPTED (HD-AUTH-09).**
   Propagation: `NQUIRY_ACCOUNT_SECURITY_PATH` (link-projection fallback is
   frontend-owned; production value `/workspaces`) — source + falsifiers in
   this branch (`36c5585`); **pending deployment ASP-01** (prepared: assembly
   archive of `36c5585` + `deploy-asp01.sh` with guards / baseline / anchor
   `nquiry-api:pre-asp01` / rollback; no migration). 2026-10-05: the session's
   permission layer refuses the upload + run as a production deploy
   (BOUNDARY: tool permission, not Field semantics); the two commands are
   recorded for the operator; production is unchanged (api `e069fc1`, web
   `94759cd`, verified read-only). Previously: the authentication Field is not
   reachable by a human through the deployed UI (provider login only via a
   typed URL). Root cutover of the CYAN candidate = CYAN_PRODUCTION_ROOT_CUTOVER
   → Human Frontend Acceptance (human boundary) after 2 and 3 and the real
   same-origin E2E on `/cy-review/`.

Authorization findings (recorded, not repaired here; none is an
authentication relation and none grants authority by side effect):

- F-AZ-1 (checked, no defect): `GET /auth/oidc/{p}/link/callback` sits with
  the protocol callbacks in the sweep's `_UNAUTHENTICATED` set; it needs a
  session for the link effect but answers a missing one with the
  `303 /login?auth=failed` projection, not a 401 — a protocol contact (24
  §11.19), proven in WU-AUTH-10 / 15, not a self route.
- F-AZ-2 existence oracle before membership on two routes: legacy
  `GET /workspaces/{ws}/sessions/{s}` (`SESSION_NOT_FOUND`) and
  `POST /decisions/{d}/decide` (`DECISION_NOT_FOUND`); random UUIDs, low.
- F-AZ-3 FastAPI `/docs`, `/redoc`, `/openapi.json` are served
  unauthenticated in PRODUCTION (live probe 2026-10-04: 200). 09 §172 allows
  generated API descriptions (shapes, operation ids, no authority semantics);
  no architecture rule hides them — disclosed as a hardening preference, not
  a broken relation.
- F-AZ-4 DB-level isolation: RLS is defined but not in force at runtime
  (business path on the bootstrap owner; PFC HA-10 undecided; HD-AUTH-06
  switched AUTH only).
- F-AZ-5 governance successors not built: remove member, change / revoke
  role, owner succession (GAP-05-001), FacilitatorScopeBinding (NQ-GAP-080),
  GAP-05-002; account-creation policies INVITATION_REQUIRED /
  PRE_PROVISIONED / GOVERNANCE_MEDIATED not materialized (24 §11.14).
- F-AZ-6 24 §6.4 text "governance root open and blocked" is stale against
  HARD-DEP-001 RESOLVED (16 §41 REC-001, founder self-service); the runtime
  is coherent with 16: identity creation never founds (`workspaceAuthority
  NONE`), founding is a separate authenticated act.

### Migrations

Head `d2f4a6b8c1e3`. Chain from the pin head `e8c2a5f1b7d4`: `f1a7c3d9b2e4`
(WU-AUTH-02 `authentication_methods`) → `a2c4e6f8b1d3` (WU-AUTH-03 credential ↔ method) → `b3d5f7a9c2e6` (WU-AUTH-04
session attribution and revocation reason) → `c4e6a8b1d3f5` (WU-AUTH-05 OIDC
transactions) → `d5f7b9c1e3a7` (WU-AUTH-08 provider identities) → `e6a8c1d3f5b9` (WU-AUTH-09
account creation failure classes) → `f7b9d1e3a5c8` (WU-AUTH-11 challenges and
verified emails) → `a8c1e3f5b7d9` (WU-AUTH-12 recovery challenges, `CREDENTIAL_RESET`) →
`b9d2f4a6c8e1` (WU-AUTH-13 account disable, one active binding per subject, `ACCOUNT_DISABLED`) →
`c1e3a5b7d9f2` (WU-AUTH-17 `auth_runtime` grants, session-resolution reads) →
`d2f4a6b8c1e3` (PROVIDER_BOOTSTRAP `PROVIDER_PROFILE_INCOMPLETE` failure class).

## Upstream dependencies

RED `checkpoint-PFC-AC1.1` (pinned producer of the runtime, the local
authentication adapter and HD-28). Architectures 04, 05, 06, 11, 13, 14, 18, 20.

## Downstream dependencies

- RED PFC HA-09 / HA-10 (runtime DB-principal isolation) consume WU-AUTH-17.
- CYAN (`frontend-symbiotic`) consumes any authentication projection through a
  later, separately authorized integration. This worktree carries the RED-line
  frontend.
- Ledger reconciliation of HD-AUTH-n into 16 §41 happens at integration.
