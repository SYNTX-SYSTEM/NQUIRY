# HUMAN DECISIONS — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)

Field-local record. IDs are `HD-AUTH-n`. They are not yet reconciled into
`16_DECISION_GAP_REGISTER.md` §41 (see "Ledger reconciliation" at the end).

## HD-AUTH-01 — Field authorization (2026-09-30)

**Decision (human operator, the PURPLE execution brief of 2026-09-30, confirmed
as the operator's own instruction in the same session):** PURPLE is authorized
to materialize the complete Identity & Authentication Field defined by
Architecture 24 (`24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`),
autonomously, one proven relation at a time, in its own worktree and branch.

**What it authorizes:** reading, analysis, implementation, tests, migrations in
isolated test environments, local proof infrastructure, documentation, Work
Unit reports, and one local commit per fully proven Work Unit.

**What it does not decide:** any of the 18 Human Authority boundaries of
Architecture 24 §36. Each stays fail-closed (24 §36 "Default behavior for
unresolved human authority") until the Field reaches it and the operator
decides it. No push, no tag, no production action, no production migration.

**Relation to PFC HA-09:** `PFC/HUMAN_AUTHORITY_QUEUE.md` lists HA-09
("Architecture 24 Identity scope and its 18 §36 decisions") as OPEN at the
PURPLE base. HD-AUTH-01 answers the *scope* half (the Field may be
materialized). The §36 decisions stay open. The queue file is RED's record and
is not edited by PURPLE.

## HD-AUTH-02 — PURPLE predecessor: pinned RED checkpoint (2026-09-30)

**Question:** Architecture 24 is on `master` (`6e7e402`). The HD-28 / AC1.1
account-creation producer and seven newer migrations exist only on the RED
line. Which commit is PURPLE's predecessor?

**Options presented:** `checkpoint-PFC-AC1.1` (`e91961e`);
`checkpoint-PFC-SFE-PCPG` (`395ecf7`); `master` (`6e7e402`).

**Decision (human operator):** `checkpoint-PFC-AC1.1`.

- Commit `e91961e4a66ab21d9edf45d74bb43b8fbd324737`, tree `af6da710a9c5d81c48f3e84ecadc310e7edabd50`.
- Migration head at the pin: `e8c2a5f1b7d4`.
- The pin is a fixed commit, never the moving `pfc-integration` branch (the
  HD-27 precedent). RED's ceiling is unchanged by consumption: CHECKPOINTED,
  not REVIEWED_FIELD, not PUBLISHED_FIELD.

## HD-AUTH-03 — Work Unit commits without the per-commit gate (2026-09-30)

**Question:** 20 §14 (no-commit law) and the standing project rule require an
explicit approval before every commit. The brief authorizes local Work Unit
commits after full proof.

**Decision (human operator):** "Yes, commits included." PURPLE may create one
local commit per fully proven Work Unit on branch `auth-identity`. Never push.
No production tags.

**Scope:** this Field and this branch only. It does not change 20 §14 for any
other Field.

## HD-AUTH-04 — Proof cadence: progressive proof radius (2026-10-01)

**Decision (human operator, SFE proof-cadence update, confirmed in session):**
From WU-AUTH-11 onward the per-Work-Unit full-repository regression of the
original brief is replaced by a progressive proof radius:

```
IMPLEMENT / REPAIR → LOCAL FALSIFIERS → LOCAL MUTATION PROOF → AFFECTED SUITES → CONTINUE
LOCAL → AFFECTED → AUTH FIELD / INTEGRATION → FULL REPOSITORY
```

- A local defect or a failed affected test does not trigger a full
  regression; it is repaired and re-proven at the narrowest valid radius.
  Repairs may accumulate under local / affected proof as long as no failure
  is hidden or deferred unresolved. `ERROR FOUND != FULL REGRESSION REQUIRED`.
- A broader AUTH integration regression runs at meaningful block boundaries;
  failures it reveals are repaired one by one at the narrowest radius, then
  the broader level is rerun.
- The FULL repository regression runs only at final AUTH Field closure, at a
  deliberately selected major checkpoint, or immediately when a delta touches
  a genuinely global invariant (migration-wide semantics, shared persistence
  infrastructure, the session foundation, identity / authority boundary
  infrastructure, repository-wide protocol or serialization changes).
- The regression running at the time of the decision (WU-AUTH-10) finishes
  normally and is the current broad preservation checkpoint.
- Tests are not weakened; failures are not hidden; only the expensive global
  re-proof is deferred to the appropriate boundary.

**Why:** the full run costs 35–45 minutes per Work Unit; the proof radius must
follow the relations a delta affects, not the fact that a defect was found.

**Recorded:** here, `STATUS.md` (cadence line), and the WU reports from
WU-AUTH-11 on (a "PROOF_RADIUS" line replaces the per-WU full regression block).

## HD-AUTH-05 — HA-AUTH-04 resolved: identity disable authority = HOST_OPERATOR (2026-10-01)

**Decision (human operator, Human-Authority closure pass, verbatim intent):**
In PRODUCTION / STAGING, identity disable authority belongs to the
HOST_OPERATOR: HD-28's host-operator authority is extended to the already
materialized server-side identity-disable command. Constraints:

- no public HTTP disable route;
- no self-disable authority;
- no role-, membership-, email- or session-derived disable authority;
- operator identity must be attributable and recorded;
- disable remains audited and provenance-bearing;
- disabling remains one-way in the currently materialized field;
- re-enable is NOT granted by this decision and remains a separate Human
  Authority boundary (24 §36 #13);
- this decision grants only identity-disable authority, not broader account
  administration authority.

**Materialization (only what was already present):** the environment gate
that encoded "undecided" (`ACCOUNT_DISABLE_EXPOSURE_UNDECIDED` for
PRODUCTION / STAGING) is removed from `application.account_disable`; every
constraint above is structural and unchanged (no route — proven by
`test_no_http_route_disables_identities`; operator in `actor_id`,
`disabled_provenance` and the SecurityEvent; one-way trigger; no re-enable
path exists). `NQUIRY_ENVIRONMENT` must still be declared. Proof:
`tests/e2e/test_auth_wu13_revocation.py` (the command disables under a
declared PRODUCTION with the operator recorded; a second run is
`ALREADY_DISABLED`), WU-16 / WU-17 / HD-28 suites: 81 passed.

**Still OPEN after this decision:** re-enable / administrative recovery
(§36 #13); HA-AUTH-03 keeps only its default (NEVER) and option (c) — option
(b) "self-disable" is excluded by this decision's constraints.

## HD-AUTH-06 — HA-AUTH-05 resolved: SWITCH AUTH ONLY (2026-10-01)

**Decision (human operator, Human-Authority closure pass):** the running
deployment and the local compose stack perform authentication persistence
under the scoped principal `auth_runtime`; business paths keep their current
principal (option "SWITCH AUTH ONLY" of the HA-AUTH-05 block). The decision
sets the target posture; executing it on the live deployment is a separate
deployment act (PFC HA-10 external effect), not performed by PURPLE.

**Materialization (only what was already present):**
- local compose: `docker-compose.yml` `api` service gains
  `NQUIRY_AUTH_DATABASE_URL` (default `auth_runtime` on the compose
  database; `infra/local/db_roles.sql` once, then migrations). The worker
  performs no authentication persistence and is unchanged.
- deployment procedure, recorded for the deployment act (not executed): (1)
  run `infra/local/db_roles.sql` against the deployment database **with a
  production credential for `auth_runtime`** in place of the local-dev
  password (11 §23: the credential source is the deployment's, never the
  repository's); (2) apply migrations through `c1e3a5b7d9f2`; (3) set
  `NQUIRY_AUTH_DATABASE_URL` in the API's environment; (4) verify
  `auth_persistence_scope() == SCOPED` and the live login path; rollback =
  unset the variable (the runtime falls back to `DATABASE_URL`, declared
  `UNSCOPED_BOOTSTRAP`).
- no code change: `connect_auth`, the grants and the declaration exist since
  WU-AUTH-17.

**Not decided by this:** the HTTP server's business-path principal (the
wider HA-10 question); re-enable / §36 #13; anything about pushing,
integrating or deploying the branch.

## Open boundaries (OPEN, awaiting the operator)

| # | Boundary | Home | What it blocks | Default in force | Status |
|---|---|---|---|---|---|
| HA-AUTH-01 | **Production account creation policy for an unknown, verified external-provider subject** (24 §36 #3–#5). Options: DENIED; SELF_REGISTRATION_ALLOWED; INVITATION_REQUIRED; PRE_PROVISIONED_IDENTITY_REQUIRED; GOVERNANCE_MEDIATED_CREATION (the last three need relations that do not exist). Full block: `WU-AUTH-09.md`. | 24 §11.14, §36; HD-28 (external-provider policy left fail-closed) | First-time provider login of a brand-new identity in PRODUCTION / STAGING | DENIED | OPEN |
| HA-AUTH-02 | **Production recovery policy and proof level** (24 §36 #11; §17.6–17.7). Options: DENIED; VERIFIED_EMAIL_SELF_SERVICE (materialized, DEVELOPMENT / TEST only); VERIFIED_EMAIL_SELF_SERVICE plus a second factor; OPERATOR_MEDIATED (§36 #13; not materialized). Full block: `WU-AUTH-12.md`. | 24 §17, §36 #11 / #13; HD-28 (host-operator provisioning) | Self-service password recovery in PRODUCTION / STAGING | DENIED | OPEN |
| HA-AUTH-03 | **Unlinking the last authentication method** (24 §36 #12; §14.6). Options: NEVER; ALLOWED WITH RECOVERY AUTHORITY (needs HA-AUTH-02 ≠ DENIED). (ALLOWED AS SELF-DISABLE excluded by HD-AUTH-05.) Full block: `WU-AUTH-13.md`. | 24 §14.6, §36 #12 | Nothing (the default is complete) | NEVER (`409 LAST_METHOD`) | OPEN |
| HA-AUTH-04 | **Who may disable an identity in PRODUCTION / STAGING** | 24 §18, §36 #13; HD-28 | — | HOST_OPERATOR (HD-AUTH-05) | **RESOLVED** by HD-AUTH-05 (2026-10-01): HOST_OPERATOR; no HTTP route, no self-disable, no derived authority; re-enable separate |
| HA-AUTH-05 | **Deployment switch to the scoped authentication principal** (24 §21.18; = PFC HA-10) | 24 §21.18, §25.2; 14 §8; PFC HA-09 / HA-10 | — | SWITCH AUTH ONLY (HD-AUTH-06) | **RESOLVED** by HD-AUTH-06 (2026-10-01): SWITCH AUTH ONLY; compose configured; deployment procedure recorded, not executed |

Touched and left undecided, not blocking any Work Unit: 24 §36 #1 / #6
(Google as an official, production-enabled method), #9 (provider-verified
email as NQUIRY verified email), #10 (session lifetime, 12 h kept), #13
(administrative recovery / re-enable; no command exists), #15 (governance bootstrap for
provider-created identities), #16 (production email delivery provider;
WU-AUTH-11), #18 (multi-account UX).

## Ledger reconciliation (deferred, disclosed)

20 §14 requires human decisions to be reconciled into 16 §41, the §6 table and
the machine-readable register in the same Work Unit. PURPLE does not do this on
its branch, for two reasons:

1. `REC-nnn` / `NQ-DEC-nnn` numbers are global and are allocated on the RED
   line (last at the pin: REC-032 / NQ-DEC-056). RED continues to allocate
   after the pin. A number chosen here would collide at integration.
2. `tests/regression/test_pfc_ledger.py` (RED's falsifier) pins the register
   to exactly 56 decisions. Adding entries would break a RED test, and editing
   that test is a cross-Field change outside PURPLE's authority.

The decisions above are therefore recorded here with full provenance and are
to be reconciled into 16 when the Field lines are integrated. This is a
disclosed ceiling of every PURPLE Work Unit, not a closed relation.
