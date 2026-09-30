# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-09 — Account Creation Boundary

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-09 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-09; §7 FBR-AUTH-007; §11.14–11.15; §19.11; §20.3; §25.3; §32.3; §33.9; §36 #3–#5, #9, #15; §39.10; §38 falsifiers 46–50, 107, 109 |
| PREDECESSOR | WU-AUTH-08 `e097de1` |
| HUMAN_AUTHORITY_STATE | **A TRUE boundary is reached and not crossed**: the production account creation policy (24 §36 #3–#5). Recorded below as HA-AUTH-01 and in `HUMAN_DECISIONS.md`. The default DENIED is in force. Consumed: HD-28 / NQ-DEC-056 (no self-service registration on PRODUCTION for local accounts; external-provider policy left fail-closed). |

## FIRST_BROKEN_RELATION_BEFORE

Unknown provider subject → account creation policy → canonical identity: the
DENIED default held only by absence; no explicit policy relation was
evaluated inside the effect gate, and the approved-policy branch (identity +
method + binding + audit as one effect, no authority) did not exist.

## CURRENT_RELATION

VALID PROVIDER PROOF → no binding → `AccountCreationPolicy` (configured,
default DENIED) →
DENIED: fail closed (`ACCOUNT_CREATION_POLICY_UNRESOLVED`, projection `unavailable`) |
SELF_REGISTRATION_ALLOWED (DEVELOPMENT / TEST only): provider email present
and verified, no identity with that email → `users` + provider method +
binding + `IDENTITY_CREATED` SecurityEvent, one transaction → fresh session →
COMPLETED transaction.

## INVARIANTS

1. The policy is explicit configuration (`NQUIRY_ACCOUNT_CREATION_POLICY`),
   default DENIED, validated at startup: SELF_REGISTRATION_ALLOWED is refused
   outside DEVELOPMENT / TEST; INVITATION_REQUIRED,
   PRE_PROVISIONED_IDENTITY_REQUIRED and GOVERNANCE_MEDIATED_CREATION are
   refused because their relations do not exist; an unknown value is refused.
2. Under DENIED nothing is created for an unknown subject.
3. Under SELF_REGISTRATION_ALLOWED a creation requires a provider email that
   the provider marked verified and that no identity already carries; a
   matching email is a collision (`EMAIL_COLLISION`), never a link.
4. Creation is one local effect: identity, method, binding, SecurityEvent
   commit together or not at all; a failure after provider proof makes the
   transaction FAILED_TERMINAL (`LOCAL_EFFECT_FAILURE`), never replayable.
5. A concurrent first login of one subject yields one identity; the loser's
   retry resolves the winner's binding.
6. A created identity has no membership, role, binding of authority,
   participation or Workspace; the audit facts carry a subject hash, not the
   subject or the email.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

- Policy vocabulary: `security.account_creation.AccountCreationPolicy`.
- Configuration: `application.auth_runtime` (`account_creation_policy`,
  `AccountCreationPolicyForbidden`, `AccountCreationPolicyNotMaterialized`).
- Effect: `application.oidc_identity.resolve_provider_identity` (policy
  branch), reusing HD-28's `SqlAlchemyIdentityRepository` for the `users`
  row, the method and provider-identity repositories, and
  `SqlAlchemySecurityEventRepository`.
- Typed conflict: `security.provider_identity.ProviderIdentityConflict`,
  raised by the persistence adapter for the subject's uniqueness (the
  `application` layer may not import the database driver, 14 §3.1).
- Consumer: the callback's step (3) in `application.http_oidc` (creation,
  session and terminal state in one transaction; refusals written afterwards).

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/security/account_creation.py` | new: vocabulary, materialized set |
| `packages/application/auth_runtime.py` | policy configuration and startup refusals |
| `packages/application/oidc_identity.py` | policy branch; creation effect |
| `packages/security/provider_identity.py`, `packages/persistence/provider_identity_repository.py` | `ProviderIdentityConflict` translation |
| `packages/security/oidc_transaction.py`, `packages/persistence/tables.py` | classes `PROVIDER_EMAIL_MISSING`, `PROVIDER_EMAIL_UNVERIFIED`, `EMAIL_COLLISION` |
| `migrations/versions/e6a8c1d3f5b9_auth_account_creation_reasons.py` | new: reason CHECK extended (no table) |
| `packages/application/http_oidc.py` | step (3) restructured: creation + session + terminal state in one transaction; refusal written separately; `unavailable` vs `failed` projection |
| `tests/e2e/test_auth_wu09_account_creation.py` | new: 19 cases |
| `tests/e2e/test_auth_wu08_provider_identity.py` | the duplicate-subject case now expects the typed conflict |

## Case 2 choices (recorded)

- **Verified provider email required for creation.** `users.email` is the
  local login's lookup key; an unverified provider claim must not become it.
  This does not decide 24 §36 #9 (no `verified_emails` relation is created).
- **Canonical email = provider email, lower-cased**; name = provider display
  name or the email's local part.
- **Relation-bearing policies refused at startup** rather than treated as
  DENIED: configuring them would otherwise look decided.
- **Three new failure classes** (24 §32.2 is a minimum); all project as `unavailable`.
- **Test fixture** for this suite mirrors `persistence.engine.connect`'s
  rollback on exception (a savepoint per dispatch), so the partial-effect
  proof is a proof of the runtime's boundary, not of the fixture's.

## MIGRATIONS

`e6a8c1d3f5b9` (revises `d5f7b9c1e3a7`): CHECK replaced; downgrade maps the
three classes to `ACCOUNT_CREATION_POLICY_UNRESOLVED` and restores the CHECK.
Fresh → head PASS (38 revisions, single head); downgrade / re-upgrade PASS.

## RED_RESULT

Collection error (`security.account_creation` absent), 0 of 19 could run.
After the first implementation 2 of 19 failed: the fixture reused one
connection without the runtime's rollback (a partial creation persisted), and
the race test tried to delete an append-only SecurityEvent in its cleanup.
Both corrected (fixture and cleanup; production code unchanged), then green.
One dependency violation was found by the affected suites (`application`
imported the database driver to catch a uniqueness error) and repaired at its
root: the adapter raises a typed conflict.

## GREEN_RESULT

19 new; with the WU-07/-08 suites, HD-28's suite, `test_http_auth`,
`tests/security`, `tests/semantic`, `tests/regression`: 468 passed, 1 skipped.
Static gates clean (ruff, mypy 240 files, architecture / provider-SDK /
test-only imports).

## ADVERSARIAL_RESULT

Proven by the falsifiers: DENIED default; SELF_REGISTRATION_ALLOWED refused
for PRODUCTION, STAGING, unset and misspelled environments; unmaterialized
policies and unknown values refused; under DENIED an unknown subject creates
nothing; under SELF_REGISTRATION a verified subject becomes one identity with
method, binding, audit and session, no authority, and logs in again as the
same identity; missing or unverified provider email refused; a matching email
is a collision with no link, no user, no session; a failed audit write leaves
no identity and a terminal transaction; two concurrent first logins yield one
identity.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..08).

## SECURITY_RESULT

Identity creation cannot happen in a production-like runtime by
configuration alone; email equality never links; the creation is audited
with a subject pseudonym; no authority is created; a partial creation cannot
be represented as success.

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu09_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `1f5b64869ab736d1c4bb97015fe1bd4478586ed478fc23bb3988bd7d313c859d` |
| Live result | 2219 passed, 2 skipped, 0 failed, exit 0 (0:43:43) = 2200 + 19 |
| No-database result | 986 passed, 1235 skipped, 0 failed, exit 0 |
| Migrations | single head `e6a8c1d3f5b9`; live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

LOCAL SESSION → canonical `UserId` → account creation effect → evaluated
policy (configured SELF_REGISTRATION_ALLOWED, DEVELOPMENT / TEST) → verified
provider credential → validated ID Token → nonce → exchange → PROCESSING
transaction → claim → user-agent binding → PENDING transaction → login start
(24 §44.4). The chain terminates in configuration that the runtime admits
only outside production; in production it terminates in DENIED. No link ends
in a provider callback alone or in email equality.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an unknown external identity becomes a canonical
identity only through an explicit policy, and the only materialized approving
policy is admitted where no production proof exists. That is 24 §11.14 with
the default of §36. No creation by convenience, no governance bootstrap.

## TRUE_HUMAN_AUTHORITY_BOUNDARY (recorded, not crossed)

```
TRUE_HUMAN_AUTHORITY_BOUNDARY
HA_ID: HA-AUTH-01 (24 §36 #3, #4, #5; PFC HA-09 sub-item)
CURRENT_WORK_UNIT: WU-AUTH-09
FIRST_BROKEN_RELATION: unknown verified provider subject → account creation policy → canonical identity, in PRODUCTION / STAGING
EXACT_QUESTION: Which account creation policy applies to an unknown, verified external-provider subject in a production-like runtime?
WHY_NOT_DERIVABLE: It is product policy (24 §11.14 "The exact product policy remains HUMAN_AUTHORITY_REQUIRED"). HD-28 decided the local-password case (host-operator creation only, no self-service) and stated that doc 24's external-provider policy "stays fail-closed"; nothing decides it.
AUTHORITATIVE_PREDECESSORS: 24 §11.14, §20.3, §36 #3–#5; HD-28 / NQ-DEC-056; 04 §17 (default deny); F02 HD-3; HARD-DEP-001 REC-001 (a verified human may found a Workspace: unchanged by any option here).
STRUCTURALLY_LEGITIMATE_OPTIONS:
  (a) DENIED — no identity from an unknown provider subject; production identities keep coming from the host operator (HD-28), who could bind a provider later through linking (WU-AUTH-10).
  (b) SELF_REGISTRATION_ALLOWED — a verified provider subject creates an identity (no authority); requires lifting the runtime refusal for production.
  (c) INVITATION_REQUIRED — needs an invitation relation (not materialized).
  (d) PRE_PROVISIONED_IDENTITY_REQUIRED — needs a pre-provisioned identity relation (not materialized).
  (e) GOVERNANCE_MEDIATED_CREATION — needs a governance-approved creation relation (not materialized).
DEFAULT_IF_UNDECIDED: (a) DENIED, in force now.
DOWNSTREAM_RELATIONS_BLOCKED: first-time provider login of a brand-new identity in production. NOT blocked: linking (WU-AUTH-10), verification (-11), recovery (-12), revocation (-13), CSRF (-14), protocol callback semantics (-15), authorization regression (-16), DB principal (-17).
FILES_CURRENTLY_CHANGED: none beyond this Work Unit's own commit.
CURRENT_PROOF_STATUS: WU-AUTH-09 proven with DENIED in force and the SELF_REGISTRATION branch proven in TEST.
```

Also touched, not decided: §36 #9 (provider-verified email as NQUIRY
verified email: no `verified_emails` row is created) and §36 #15 (a created
identity is a "verified human" for HARD-DEP-001's founding act by REC-001's
wording; whether a provider-created identity should be, is governance
bootstrap policy and is not narrowed here).

## FIRST_BROKEN_RELATION_AFTER

**Account linking** (24 WU-AUTH-10): an authenticated identity cannot add a
provider method; no ACCOUNT_LINK start / callback exists, no collision rule
is exercised for a subject already bound elsewhere, no link audit.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-09 proven; HA-AUTH-01 OPEN with DENIED in force. Next: WU-AUTH-10.
