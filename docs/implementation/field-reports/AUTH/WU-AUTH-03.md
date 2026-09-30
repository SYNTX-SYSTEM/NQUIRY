# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-03 — Local Credential Migration Compatibility

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-03 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-03; §9.2; §16.3; §22.3–22.4; §28.2–28.3; §28.9; §39.13 |
| PREDECESSOR | WU-AUTH-02 `53823d6` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03; consumes HD-28 (host-operator creation) and F02 HD-3 (dev identity), both unchanged. No §36 boundary reached. |

## FIRST_BROKEN_RELATION_BEFORE

Local credential ↔ authentication method. `local_auth_credentials` rows
belonged to no method, and login did not consult any method status.

## ROOT_SWEEP

- Producer of credentials: one function,
  `SqlAlchemyLocalCredentialRepository.create`, called by the HD-28 operator
  path (`application.identity_provisioning`), dev provisioning
  (`test_support.dev_identity`), `scripts/seed_local_demo.py` and test fixtures.
- Consumer: `application.auth_handler.login` through `get_by_email`.
- Siblings: `local_auth_sessions` (untouched; session ↔ method is WU-AUTH-04).
- Downstream: every governed route resolves identity from a session, not from
  a credential; none is affected.

## CURRENT_RELATION

`local_auth_credentials` 1 — 1 `authentication_methods` (LOCAL_PASSWORD, same
user). Login: password proof → method ACTIVE (atomic
conditional write) → session.

## MUST BECOME TRUE / MUST REMAIN IMPOSSIBLE

Must become true: existing local credentials work through the method model.
Must remain impossible: plaintext password migration; existing login breaking.
Added by the relation itself: a credential without, or on a foreign or
non-password, method; a revoked method logging in; a revoked method being
distinguishable from a wrong password.

## INVARIANTS

1. Every credential names one method (NOT NULL), of its own user (composite
   FK), of type LOCAL_PASSWORD (trigger); one credential per method (UNIQUE).
2. A credential's method and user never change (trigger).
3. Creating a credential creates its method in the same transaction, with
   provenance `local-credential:<credential id>`.
4. Login succeeds only if `mark_authenticated` changed the method row, which
   it does only while the method is ACTIVE. There is one status check, and it
   is atomic with the write.
5. The denial for a revoked method is the same exception, HTTP status and
   body as for a wrong password, and sets no cookie.
6. The migration changes no `password_hash`, `user_id` or timestamp.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

- Producer (reused, extended): `SqlAlchemyLocalCredentialRepository.create`
  now also creates the method. No creator was edited; HD-28's and HD-3's
  modules are byte-unchanged.
- Producer (new): `SqlAlchemyLocalCredentialRepository.mark_authenticated`
  (port: `security.local_auth.LocalCredentialRepository`).
- Consumer: `application.auth_handler.login`. Its signature is unchanged.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/a2c4e6f8b1d3_auth_local_credential_method.py` | new: column, backfill, constraints, trigger |
| `packages/persistence/tables.py` | credential column + composite FK; `(id, user_id)` unique on methods |
| `packages/persistence/local_auth_repository.py` | `create` makes the method; `get_by_email` returns `method_id`; `mark_authenticated` |
| `packages/security/local_auth.py` | `LocalCredentialRecord.method_id`; port method |
| `packages/application/auth_handler.py` | login requires the ACTIVE method |
| `tests/e2e/test_auth_wu03_local_credential_method.py` | new: 14 cases |
| `tests/security/test_auth_migrations.py` | new: 2 cases (scratch databases) |
| `scripts/auth_wu03_mutation_proof.py` | new |

No route, response shape or frontend file changed.

## Case 2 choices (recorded)

- **One status check.** A first draft also compared a status read with the
  credential. It was removed: it was redundant with the atomic write and a
  stale read is not a fact. The record carries `method_id` only.
- **Provenance of new methods** is the credential row they were created for.
  The HD-28 SecurityEvent already names `user:<id>`; nothing in RED's module
  had to change.
- **Backfill provenance** is `migration:a2c4e6f8b1d3:local-credential:<id>`
  (24 §13.10: migration provenance is recorded and proves nothing about the identity).
- **`local_auth_credentials.user_id` UNIQUE is kept.** Several credentials
  per user (a superseded one after reset) belong to recovery (WU-AUTH-12).
  While it holds, the new UNIQUE on the method id cannot be violated on its
  own, so no mutation targets it (disclosed).
- **Downgrade deletes LOCAL_PASSWORD methods.** After the downgrade nothing
  relates them to a credential; a re-upgrade backfills them again.

## MIGRATIONS

`a2c4e6f8b1d3` (revises `f1a7c3d9b2e4`).

| Proof | Result |
|---|---|
| Upgrade with predecessor-shaped credentials in place | each gets one ACTIVE LOCAL_PASSWORD method of its user, created at the credential's time; hashes unchanged; a user without a credential gets none |
| Downgrade to `f1a7c3d9b2e4` | column gone, 0 methods, credentials and hashes intact |
| Upgrade again to head, then real `login` | both predecessor identities log in; the identity without a credential is denied |
| Fresh database → head → back to the pin schema `e8c2a5f1b7d4` | PASS |
| Shared test database | `MIGRATION_LIVE_CHECK::PASS (db head matches {'a2c4e6f8b1d3'})`, 34 revisions, single head |

No production migration was executed.

## RED_RESULT

The 14 falsifiers of `test_auth_wu03_local_credential_method.py`, run against
the committed predecessor tree (`git archive 53823d6`, database at
`f1a7c3d9b2e4`): **14 failed**. Deviation (20 §12): the falsifiers were
written first, but the implementation was started before they were executed;
the RED run was therefore taken on an export of the predecessor commit rather
than on the working tree.

## GREEN_RESULT

14 + 2 passed. With the affected suites (`tests/security`, `tests/semantic`,
`tests/regression`, `test_auth_handler`, `test_http_auth`,
`test_pfc_ac1_production_account_creation`, `test_http_workspaces`,
`test_http_f02`): 396 passed, 1 skipped.

## ADVERSARIAL_RESULT

- Revoked method: login denied, no session row, no cookie, `last_authenticated_at` unchanged.
- Method revoked between the credential read and the login's write: denied, no session.
- Raw SQL: credential without a method, with an unknown method, with another
  user's method, with a GOOGLE_OIDC method, or re-pointed to another method: refused.
- HTTP: revoked-method response equals the wrong-password response byte for byte.

## MUTATION_RESULT

`scripts/auth_wu03_mutation_proof.py`: **14/14 KILLED**, sources restored.

## SECURITY_RESULT

- No plaintext: the migration reads no password; the method row contains
  neither the password nor the hash.
- Enumeration: unknown email, wrong password and revoked method are one
  exception and one response. The method check runs after the password
  verification, so a revoked method costs the same PBKDF2 pass.
- Hash algorithm, salt, iteration count and constant-time comparison: unchanged.
- Authentication still creates no membership, role, binding or participation
  (the HD-28 "no authority of any kind" falsifier stays green).

## CONSUMER_PROOF / PRESERVATION_RESULT

`/auth/login`, `/auth/logout`, `/auth/me` and every governed route are proven
through the real FastAPI app against real PostgreSQL by the unchanged
predecessor suites. HD-28's 24 cases and the dev-provisioning suite pass
unchanged. Static gates: ruff clean; mypy no issues in 225 source files;
architecture, provider-SDK and test-only import checks PASS.

Not run in this unit: the real-browser lane. It binds `:8000` / `:3000`,
which another line's local stack occupies on this machine. The login contract
seen by the browser (request, response, cookie) is unchanged. A PURPLE browser
lane is set up where a browser boundary changes (WU-AUTH-14).

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu03_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `a064d60f022cedd4796ec9a9d3d3ff4786fa597005a083a44f811dc505f395b3` |
| Live result | 2065 passed, 2 skipped, 0 failed, exit 0 (0:30:47) = 2049 + 16 |
| No-database result | 938 passed, 1129 skipped, 0 failed, exit 0 |
| Migrations | single head `a2c4e6f8b1d3`; live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| credential → `authentication_method_id` | created with the credential, or backfilled from the credential row | CANONICAL FACT |
| method `provenance_ref` | the credential id generated in the same call / the migrated credential id | CANONICAL FACT (names an existing row) |
| method `created_at` (backfill) | the credential's `created_at` | DERIVED FACT |
| `last_authenticated_at` | set after a verified password, only while ACTIVE | AUTHENTICATION PROOF |
| session (login success) | verified password + ACTIVE method | AUTHENTICATION PROOF |
| login email | request body | USER CLAIM; used only as a lookup key, never as identity |

`provenance_ref`, UNPROVEN at WU-AUTH-02, is now proven for every
LOCAL_PASSWORD producer. No claim becomes canonical. The session does not yet
name the method that produced it: UNPROVEN, owner WU-AUTH-04.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: a canonical identity owns typed methods; a local
password credential is the secret material of exactly one LOCAL_PASSWORD
method; a login is a password proof against an ACTIVE method. That is 24
§9.2 / §13.2 / §16.3. No second credential store or second login path exists.

## FIRST_BROKEN_RELATION_AFTER

**Authenticated session ↔ authentication method / proof provenance, and
session revocation scope** (24 WU-AUTH-04; FBR-AUTH-005, FBR-AUTH-017): a
session cannot be traced to the method that produced it, revoking a method
leaves its sessions valid, and only single-session logout exists.

## Limitations and ceilings

- Real-browser lane not run (above).
- A revoked method still leaves its existing sessions valid until WU-AUTH-04 / -13.
- Human decisions are field-local; 16 §41 reconciliation deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-03 proven. Next: WU-AUTH-04.
