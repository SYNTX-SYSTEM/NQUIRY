# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-08 — Provider Identity Binding

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-08 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-08; §11.13–11.15; §13.3; §13.10; §14.4, §14.7; §19.1, §19.3; §22.2–22.3; §33.9; §39.10; §38 falsifiers 1, 42, 43, 47–50 |
| PREDECESSOR | WU-AUTH-07 `5aa13ae` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. §36 #3–#5 (account creation for an unknown subject) **not decided**: still fails closed. No new boundary touched. |

## FIRST_BROKEN_RELATION_BEFORE

`provider_issuer + provider_subject` → canonical `UserId`: no relation
existed, so every verified provider credential failed closed at the identity
step, including one that should have resolved an existing identity.

## ROOT_SWEEP

- Producer of bindings: none in production yet (account creation WU-AUTH-09,
  linking WU-AUTH-10); the repository `create` is the producer they will use.
- Consumers: `application.oidc_identity.resolve_provider_identity` in the
  callback's local effect gate; the session issuer (shared with the local
  login, factored out here as `auth_handler.issue_session`).
- Parent: authentication methods (a binding hangs on one provider-type
  method). Siblings: local credentials (untouched).

## CURRENT_RELATION

VALID PROVIDER PROOF → lookup issuer + subject → existing unrevoked binding of
an ACTIVE method → one conditional write (authentication recorded on the
method, provider attributes refreshed) → canonical `UserId` → fresh session →
COMPLETED transaction → cookie → bound redirect target.
No binding → ACCOUNT_CREATION_POLICY_UNRESOLVED (unchanged).
Binding whose method is revoked → AUTHENTICATION_METHOD_REVOKED.

## INVARIANTS

1. One identity per issuer + subject (UNIQUE); one binding per method
   (UNIQUE); the method belongs to the same user (composite FK) and is a
   provider method (trigger).
2. Issuer, subject, method and user of a binding never change; a revoked
   binding stays revoked (trigger). Provider email, verified flag and display
   name are refreshed at each provider login and never move the link.
3. Login through a binding is one conditional write that succeeds only while
   the binding is unrevoked and the method ACTIVE.
4. No lookup by email exists; two identities may carry the same provider
   email; a matching email without a binding does not log in.
5. A provider login issues a fresh session through the same producer as the
   local login, attributed to the provider method; whatever session cookie
   the browser carried is replaced.
6. Nothing in this unit creates a user, a membership, a role, a binding of
   authority or a participation.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/d5f7b9c1e3a7_auth_provider_identities.py` | new: table, constraints, trigger; failure vocabulary + `AUTHENTICATION_METHOD_REVOKED` |
| `packages/persistence/tables.py` | table; reason list |
| `packages/security/provider_identity.py` | new: record, authentication result, port |
| `packages/persistence/provider_identity_repository.py` | new: `create`, `find`, `authenticate` |
| `packages/security/oidc_transaction.py` | `OidcFailureReason.AUTHENTICATION_METHOD_REVOKED` |
| `packages/application/oidc_identity.py` | real resolution (lookup, active-method write) |
| `packages/application/auth_handler.py` | `issue_session` factored out of `login` (behavior unchanged) |
| `packages/application/http_oidc.py` | session issued and cookie set on a resolved identity; revoked-method projection `failed` |
| `tests/e2e/test_auth_wu08_provider_identity.py` | new: 13 cases |

No route or frontend change: the contacts of WU-AUTH-07 now complete.

## Case 2 choices (recorded)

- **Failure class for a revoked method** is a new internal class
  `AUTHENTICATION_METHOD_REVOKED` (24 §32.2 is a minimum list; nothing in it
  names this case). Projected as `failed`, not as a distinct public message.
- **Attributes refreshed only after the conditional write succeeded**, so a
  revoked binding's attributes never change.
- **`issue_session`** is now the single session producer for both methods,
  rather than a second producer for provider logins.
- **`find` before `authenticate`** distinguishes "no binding" (policy
  question) from "binding, method not active" (revocation) for the internal
  evidence; the write itself is the only status authority.

## MIGRATIONS

`d5f7b9c1e3a7` (revises `c4e6a8b1d3f5`): fresh → head PASS (37 revisions,
single head); downgrade −1 removes the table and restores the previous reason
vocabulary (rows with the new reason are mapped to `LOCAL_EFFECT_FAILURE`
first); re-upgrade PASS. No production migration was executed.

## RED_RESULT

Collection error (`persistence.provider_identity_repository` absent), 0 of 13
could run. After the first implementation 1 of 13 failed: the test set the
binding's method to its own current value, which is not a change; the case was
corrected to a genuine move and then refused as intended.

## GREEN_RESULT

13 new + 32 WU-AUTH-07 cases green; affected suites (`tests/security`,
`tests/semantic`, `tests/regression`, the WU-03/-04/-07 suites,
`test_http_auth`): 453 passed, 1 skipped. Static gates clean (ruff, mypy 239
files, architecture / provider-SDK / test-only imports).

## ADVERSARIAL_RESULT

Proven by the falsifiers: two identities on one issuer + subject refused;
same subject at another issuer is another identity; same provider email on
two identities allowed and unrelated; binding on a LOCAL_PASSWORD method or on
another user's method refused; second binding on one method refused; every
identity column of a binding immutable; unknown subject creates no user, no
binding, no session; an identity with a local password and the same email is
not linked and not logged in; a revoked provider method does not log in and
the transaction records the class; a provider login replaces a planted
session cookie; a provider login creates no authority rows and the new
session sees no Workspace; provider sessions list, log out and revoke like any other.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..07); each
protection has a direct falsifier above.

## SECURITY_RESULT

Email is never a key; the link cannot be moved by an attribute change; the
active-method check is atomic with the authentication record; the session
follows the same rules as every other (opaque, hashed, attributed).

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu08_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `9b8b1decb0f2d03c606ed87afb37f8536106a5c77251b0f7c4717ca10522b311` |
| Live result | 2200 passed, 2 skipped, 0 failed, exit 0 (0:34:34) = 2187 + 13 |
| No-database result | 976 passed, 1226 skipped, 0 failed, exit 0 |
| Migrations | single head `d5f7b9c1e3a7`; live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

VISIBLE AUTHENTICATED STATE → `/auth/me` → cookie → session row → provider
method (ACTIVE) → binding (issuer + subject) → verified credential (validated
ID Token, nonce matched) → token exchange with the original verifier →
PROCESSING transaction → atomic claim → user-agent binding → PENDING
transaction → login start → initiating browser interaction. The chain of 24
§44.3 now terminates in authoritative state at every link. Email is never a
link. Account creation (24 §44.4) remains UNPROVEN: the branch does not exist.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an external identity is a (issuer, subject) pair
bound once to one method of one canonical identity; a provider login is that
binding, active, after a valid provider proof. That is 24 §11.13–11.14 and
§13.3. No email-based path, no second identity store.

## FIRST_BROKEN_RELATION_AFTER

**Account creation boundary** (24 WU-AUTH-09; FBR-AUTH-007): an unknown
provider subject evaluates no explicit policy; the default DENIED /
UNAVAILABLE holds by absence rather than by an evaluated policy relation,
and the approved-policy branch (identity creation without authority, coherent
with the binding) does not exist. The product policy itself is 24 §36 #3–#5,
HUMAN_AUTHORITY_REQUIRED.

## Limitations and ceilings

- No production producer of bindings until WU-AUTH-09 / -10; the end-to-end
  proof seeds bindings through the repository.
- Real Google proof still BLOCKED_EXTERNAL; real-stack browser lane still blocked (WU-AUTH-14).
- No source-mutation proof; human decisions field-local.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-08 proven. Next: WU-AUTH-09, which reaches a Human Authority boundary (account creation policy).
