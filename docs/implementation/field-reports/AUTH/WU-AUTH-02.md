# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-02 — Authentication Method Model

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-02 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-02; §7 FBR-AUTH-002; §9.1; §13.2; §18.3; §22.2–22.3; §38 falsifiers 39, 64 |
| PREDECESSOR | WU-AUTH-01 `a0f5982` (on `checkpoint-PFC-AC1.1` `e91961e`) |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. No §36 boundary reached or decided. |

## FIRST_BROKEN_RELATION_BEFORE

FBR-AUTH-002: canonical NQUIRY identity ↔ authentication method. A credential
was persisted only as the adapter-specific row `local_auth_credentials`; no
relation typed the method, carried its status or its provenance.

## ROOT_SWEEP

- Producer of the broken relation: none existed.
- Consumers waiting on it: local credential (WU-AUTH-03), session
  traceability and method-scoped revocation (WU-AUTH-04, -13), provider
  identity (WU-AUTH-08), linking (WU-AUTH-10), recovery (WU-AUTH-12).
- Parent: `users` (canonical identity). Siblings: `local_auth_credentials`,
  `local_auth_sessions` — both untouched here.
- Authority chain: not a consumer. No boundary, `AuthorityResolver` or
  `CommitCoordinator` code reads or writes this relation.

## CURRENT_RELATION

`UserId` 1 — n `AuthenticationMethod(method_id, user_id, method_type, status,
created_at, revoked_at, last_authenticated_at, provenance_ref)`.

## BOUNDARY

Inside the Authentication Field. The relation carries no email, no Workspace,
no role, no capability. It is cross-Workspace like `users` (no `workspace_id`,
no RLS).

## MUST BECOME TRUE / MUST REMAIN IMPOSSIBLE

Must become true: a canonical `UserId` can have typed authentication methods;
a method's status is an authoritative fact.

Must remain impossible: email equality links accounts; a recovery challenge,
an OIDC transaction or an initiating user-agent binding appears as an
authentication method; a method without a canonical user; a revoked method
becoming active again; a method creating authority.

## INVARIANTS

1. `method_type` ∈ {LOCAL_PASSWORD, GOOGLE_OIDC, TEST_PROVIDER} (24 §9.1).
2. `status` ∈ {ACTIVE, REVOKED}; REVOKED ⟺ `revoked_at` set.
3. A method is created ACTIVE.
4. `id`, `user_id`, `method_type`, `created_at`, `provenance_ref` never change.
5. REVOKED is terminal; the row is kept (24 §18.3).
6. At most one ACTIVE LOCAL_PASSWORD method per user.
7. Every method references an existing `users` row; provenance is non-empty.
8. Methods are found by method id or user id, never by email.

Invariants 1–7 are enforced by the database (CHECK, FK, partial unique index,
two triggers), for every writer. 1, 2, 7 are also enforced by the record type.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

- Producer (new): `persistence.authentication_method_repository.SqlAlchemyAuthenticationMethodRepository.create / revoke`.
- Port (new): `security.auth_methods.AuthenticationMethodRepository`.
- Consumers: none yet in production code. The first is WU-AUTH-03 (local
  credential through the method model). This is stated, not hidden: until
  then no login reads method status.

## EXISTING_PRODUCERS_REUSED

`users` as the canonical identity; the `security` port / `persistence` adapter
split of Architecture 18; the strong-id pattern (`semantic_types.ids`); the
two-trigger pattern of `evidence` / `decisions` for initial state and
transition topology.

## NEW_PRODUCERS_CREATED

`AuthenticationMethodId`; `security/auth_methods.py`;
`persistence/authentication_method_repository.py`; table `authentication_methods`.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/semantic_types/ids.py` | + `AuthenticationMethodId` |
| `packages/security/auth_methods.py` | new: vocabulary, record, port |
| `packages/persistence/tables.py` | + `authentication_methods_table` |
| `packages/persistence/authentication_method_repository.py` | new: adapter |
| `migrations/versions/f1a7c3d9b2e4_auth_authentication_methods.py` | new |
| `tests/security/test_authentication_methods.py` | new: 42 cases |
| `scripts/_auth_mutation.py`, `scripts/auth_wu02_mutation_proof.py` | new |

No route, no frontend file, no existing behavior changed.

## Case 2 choices (recorded)

- **Vocabulary.** 24 §9.1 lists `FUTURE_OIDC_PROVIDER` as a class of later
  providers. It is not a value; a new provider extends the enum and the CHECK
  in its own Work Unit. GOOGLE_OIDC and TEST_PROVIDER are in the vocabulary
  because §9.1 closes it; no producer writes them until WU-AUTH-07/-08.
- **Status.** ACTIVE / REVOKED. "Disable", "unlink" and "credential
  revocation" (24 §18.1) all end in REVOKED; nothing in 24 defines a
  reversible suspended state.
- **No DELETE guard.** 24 §18.3 prefers revocation "unless retention policy
  requires deletion". The repository offers no delete; a database-level ban
  would pre-empt an undecided retention policy.
- **`last_authenticated_at`** exists as a column (24 §13.2) and may change
  only while ACTIVE. Its writer is the login path (WU-AUTH-03).
- **API effect.** 24: "list methods internally or publicly as allowed".
  Internal only (`list_for_user`). The public contact belongs to the account
  security surface.

## MIGRATIONS

`f1a7c3d9b2e4` (revises `e8c2a5f1b7d4`). Additive; reads and changes no existing row.

| Proof | Result |
|---|---|
| Fresh database → head | `MIGRATION_LIVE_CHECK::PASS (db head matches {'f1a7c3d9b2e4'})`, 33 revisions, single head |
| Upgrade from the previous head (database used by the baseline run) | PASS |
| Downgrade −1 | table absent, 0 `trg_authentication_methods%` functions, version `e8c2a5f1b7d4` |
| Re-upgrade | PASS; `local_auth_credentials` untouched |
| DB-principal grants | none made; owner WU-AUTH-17 (24 §21.18, §28.8) |

No production migration was executed.

## TESTS_ADDED / FALSIFIERS

`tests/security/test_authentication_methods.py`, 42 cases: closed vocabulary
(1 + 7 excluded relations); statuses; record has no email or authority field;
record consistency (5); create / get / list; several types per user; unknown
ids; one active local password; successor after revocation; no method without
a user; database refuses the 7 excluded relations; not created REVOKED;
status / revocation / provenance CHECKs; revoke once; REVOKED terminal (3
statements); identity immutable (5 columns); no cross-effect on other methods;
columns exact and no RLS; by user never by email, repository surface exact;
no authority rows created; two concurrent creations leave one active method.

## RED_RESULT

Before any implementation: collection error,
`ModuleNotFoundError: No module named 'security.auth_methods'` (0 of 42 could run).

## GREEN_RESULT

42 passed (live PostgreSQL). Without a database: 15 passed, 27 skipped.

## ADVERSARIAL_RESULT

Raw SQL as the table owner, bypassing the repository, is refused for: an
excluded relation as method type; ACTIVE with a revocation time; empty
provenance; creation in REVOKED; reactivation; any change after revocation;
rewriting id, user, type, creation time or provenance; an unknown user; a
second active local password. Two real connections racing to create the
second active local password: the second waits, then is refused.

## MUTATION_RESULT

`scripts/auth_wu02_mutation_proof.py`: **20/20 KILLED**, sources restored
byte-for-byte. M01–M12 mutate the migration and run on a scratch database
migrated from the mutated tree; M13–M20 mutate the record type and the
repository.

## SECURITY_RESULT

No secret is stored or handled by this relation. No identity can be reached
through an email value. The relation is not Workspace-scoped (falsifier 64).
Creating and revoking a method changes no membership, role, binding,
participation or Workspace row.

## CONSUMER_PROOF / PRESERVATION_RESULT

Affected suites after the change (`tests/security`, `tests/semantic`,
`tests/regression`, `test_auth_handler`, `test_http_auth`,
`test_pfc_ac1_production_account_creation`): 357 passed, 1 skipped. Login,
logout, `/auth/me` and the HD-28 operator command are byte-unchanged.

Static gates: `ruff check` clean; `ruff format --check` clean for all Python
(one pre-existing finding in a RED Markdown bundle under `field-reports/F04/review/`,
not touched); mypy no issues in 222 source files;
`ARCHITECTURE_DEPENDENCY_CHECK::PASS`; `PROVIDER_SDK_IMPORT_CHECK::PASS`;
`TEST_ONLY_IMPORT_CHECK::PASS`.

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu02_regression.txt`, produced by `scripts/auth_regression_run.sh`).

| Item | Value |
|---|---|
| Pre-run tree hash | `16005d33a5cd2968381f8d81e2dfc9651708dcbe4dbdc6ce87f42ba34571d722` |
| Live command | `DATABASE_URL=<isolated test db> python -m pytest -q -p no:cacheprovider` |
| Live result | 2049 passed, 2 skipped, 0 failed, exit 0 (0:33:47) = baseline 2007 + 42 |
| No-database result | 938 passed, 1113 skipped, 0 failed, exit 0 |
| Migrations | single head `f1a7c3d9b2e4`; live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| `method_id` | generated by the repository (`uuid4`) | CANONICAL FACT |
| `user_id` | caller-supplied, verified by FK against `users` | CANONICAL FACT |
| `method_type` | closed enum, re-checked by the database | CANONICAL FACT |
| `status`, `revoked_at` | repository transition, guarded by triggers | CANONICAL FACT |
| `created_at` | caller clock | DERIVED FACT |
| `provenance_ref` | caller-supplied text, non-empty | USER CLAIM of the producing code path, not verified against a referent |

`provenance_ref` is free text at this unit: nothing proves it names a real
record. Each producer that writes a method must supply a reconstructable
reference (WU-AUTH-03 for local credentials and the migration backfill,
WU-AUTH-08/-09 for provider methods). No user or provider claim becomes
canonical through this relation. Nothing FABRICATED, DUPLICATED, STALE,
BYPASSED, PROMOTED or UNAUTHORIZED found; `provenance_ref` is UNPROVEN until
its producers exist.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations alone: a canonical identity owns a set of typed
methods with a two-state lifecycle. That is 24 §13.2. The code adds no second
identity, no second credential store and no authority path. The relation does
not yet affect authentication, which is exactly the next broken relation.

## FIRST_BROKEN_RELATION_AFTER

**Local credential ↔ authentication method** (24 WU-AUTH-03, §22.4, §28.2):
existing and newly created `local_auth_credentials` rows belong to no method,
and login does not consult method status. "Method status controls login" is
therefore not yet true.

## Limitations and ceilings

- No production consumer yet (see above).
- Local interpreter Python 3.10; images run 3.13.
- Human decisions are field-local; 16 §41 reconciliation deferred (`HUMAN_DECISIONS.md`).

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-02 proven. Next: WU-AUTH-03.
