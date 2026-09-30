# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-05 — OIDC Auth Transaction Field

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-05 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-05; §7 FBR-AUTH-008, -010, -013, -014; §11.3–11.11, §11.16, §13.4–13.7, §16.2 steps 1–10, §19.9, §22.2–22.3, §22.6–22.8, §32.2, §33.2, §33.3, §33.6, §33.10, §39.2, §39.11; §47 items 5, 6, 7, 9 |
| PREDECESSOR | WU-AUTH-04 `3ffbd1b` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. No §36 boundary reached: no provider is configured or enabled by this unit. |

## FIRST_BROKEN_RELATION_BEFORE

OIDC start → transaction → callback → local validation → atomic claim →
verifier → token exchange: no authoritative transaction relation existed
between a provider login start and its callback (FBR-AUTH-008), no
confidential recoverable PKCE verifier lifecycle (FBR-AUTH-010), no
single-processor claim (FBR-AUTH-013), no initiating user-agent binding
(FBR-AUTH-014).

## ROOT_SWEEP

- Producer: none existed. Consumers waiting: redirect validation (WU-AUTH-06),
  the provider adapter and the start/callback routes (WU-AUTH-07), provider
  identity binding (WU-AUTH-08), account creation (WU-AUTH-09), linking
  (WU-AUTH-10), protocol callback semantics (WU-AUTH-15).
- Parent: authentication methods (a transaction is not one, 24 §13.2).
  Siblings: sessions (a completed transaction leads to a fresh session in
  WU-AUTH-07; nothing here creates one).
- Authority chain: not a consumer. A transaction carries no identity result.

## CURRENT_RELATION

`oidc_auth_transactions(id, provider, purpose, initiating_user_id, state,
state_hash, nonce_hash, user_agent_binding_hash, pkce_code_verifier,
pkce_code_challenge, post_auth_redirect_target, created_at, expires_at,
claimed_at, completed_at, failed_terminal_at, expired_at, cancelled_at,
verifier_unavailable_at, failure_reason, provenance_ref)` with the state
machine PENDING → PROCESSING → COMPLETED | FAILED_TERMINAL; PENDING →
EXPIRED | CANCELLED_TERMINAL | FAILED_TERMINAL.

## MUST BECOME TRUE / MUST REMAIN IMPOSSIBLE

As 24 WU-AUTH-05 (19 and 18 items). Not in this unit, by 24's own dependency
order: "nonce validation occurs after token exchange and trusted ID Token
validation" and "provider subject trusted only after ID Token validation" are
relations of the token exchange (WU-AUTH-07). This unit gives them their
input: the expected-nonce binding is handed to the winning processor as a
hash to compare against the validated token's claim, never earlier.

## INVARIANTS

1. Only PENDING can be claimed; the claim is one statement (row lock,
   conditional transition, verifier returned and blanked). Exactly one caller
   wins; every other observes PROCESSING or a terminal state.
2. The verifier exists in the row exactly while PENDING (CHECK), is never
   set again (trigger), and is never part of a read (only `claim` returns it).
3. PROCESSING never returns to PENDING; a terminal row never changes; the
   identity of a row (provider, purpose, initiating user, state / nonce /
   binding hashes, challenge, redirect target, created, expires,
   provenance) is immutable. Trigger, for every writer.
4. Each state requires exactly its timestamps; a terminal or PROCESSING row
   records `verifier_unavailable_at`; FAILED_TERMINAL and CANCELLED_TERMINAL
   carry a closed failure reason (24 §32.2).
5. Only hashes of state, nonce and binding token are stored.
6. ACCOUNT_LINK binds an initiating user; LOGIN binds none (CHECK and code).
7. Callback order: lookup → PENDING → user-agent binding → expiry → purpose →
   initiating user → claim. A foreign user-agent, wrong purpose or wrong
   initiating user terminalizes the transaction (FAILED_TERMINAL); a met
   expiry terminalizes it (EXPIRED). A cancel validates the same relations
   and terminalizes without a claim.
8. The redirect target column accepts a local path only (24 §22.8); its
   validator is WU-AUTH-06.
9. No `workspace_id`, no RLS, no identity or authority column.

## AUTHORITATIVE_PRODUCERS / CANONICAL_CONSUMERS

- New: `security.oidc_transaction` (types, state table, RFC 7636 helpers,
  hashing, port); `persistence.oidc_transaction_repository`
  (`create`, `get`, `get_by_state_hash`, `claim`, `terminalize`);
  `application.oidc_transactions` (`start_transaction`, `claim_transaction`,
  `complete_transaction`, `fail_transaction`, `cancel_transaction`).
- Consumers: none in production yet. The start/callback routes and the
  provider port arrive with WU-AUTH-07, which is where the application
  functions gain their callers. Disclosed, as for WU-AUTH-02.

## EXISTING_PRODUCERS_REUSED

`users` (initiating user), `UserId`, the port / adapter / handler split, the
two-trigger and CHECK discipline of the earlier units, `secrets.token_urlsafe`
and `hashlib.sha256` as already used by `security.local_auth`.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `migrations/versions/c4e6a8b1d3f5_auth_oidc_transactions.py` | new: table, 10 CHECKs, unique state hash, index, trigger |
| `packages/persistence/tables.py` | `oidc_auth_transactions_table`, `OIDC_FAILURE_REASONS` |
| `packages/security/oidc_transaction.py` | new |
| `packages/persistence/oidc_transaction_repository.py` | new |
| `packages/application/oidc_transactions.py` | new |
| `tests/security/test_auth_oidc_transactions.py` | new: 29 cases |

No route, no frontend, no configuration, no existing behavior changed.

## Case 2 choices (recorded)

- **Verifier storage.** 24 §22.6 allows "stored or referenced in a
  recoverable confidential server-side form". The verifier is stored as a
  plain column while PENDING and blanked by the claim itself. Sealing with a
  key (24 §25.2 `NQUIRY_PKCE_VERIFIER_SEALING_KEY` "if … used") would add a
  runtime cryptography dependency and a key to manage without changing the
  relation: a database reader during the pending minutes would still lack
  the authorization code, the state and the browser binding. Revisitable in
  WU-AUTH-07 if the token library brings the dependency anyway.
- **Security rejection before the claim terminalizes.** A callback with a
  foreign user-agent binding, wrong purpose or wrong initiating user makes
  the transaction FAILED_TERMINAL: callback material has reached the wrong
  context, and 24 §11.4 counts a security failure "in a way that makes reuse
  unsafe" as terminal. A missing transaction and a non-PENDING state change nothing.
- **Cancel path** validates lookup, state, binding and expiry like a
  callback (24 §11.16 "validate initiating user-agent binding … validate
  transaction") before terminalizing as CANCELLED_TERMINAL.
- **Lifetime.** 10 minutes by default, a parameter of `start_transaction`.
  Not a §36 item; recorded as an implementation constant.
- **Transaction id** is a plain UUID, like a session id; provider is free
  text with a non-empty CHECK until the provider registry (WU-AUTH-07)
  closes it.

## MIGRATIONS

`c4e6a8b1d3f5` (revises `b3d5f7a9c2e6`). Additive, starts empty (24 §28.4).
Fresh database → head PASS (`MIGRATION_LIVE_CHECK::PASS`, 36 revisions, single
head); downgrade −1 removes the table and the trigger function; re-upgrade
PASS; the migration-walk suite still steps back to the pin schema. No
production migration was executed.

## RED_RESULT

Collection error (`application.oidc_transactions` absent), 0 of 29 could run.

## GREEN_RESULT

29 passed. Affected suites (`tests/security`, `tests/semantic`,
`tests/regression`): 335 passed, 1 skipped.

## ADVERSARIAL_RESULT

Proven by the falsifiers: callback without a transaction; second callback
after the claim; transplanted callback (missing and mismatched binding) on
both the success and the cancel path; expired transaction; LOGIN claimed as
ACCOUNT_LINK; ACCOUNT_LINK from a stranger and from nobody; verifier of A
against B's challenge; completion without a claim; replay after COMPLETED,
FAILED_TERMINAL, EXPIRED and CANCELLED_TERMINAL; uncertain exchange outcome
made terminal; raw SQL attempts to return to PENDING, to move a claimed or
terminal row, to resurrect a verifier, to create a PENDING row without a
verifier or a PROCESSING row with one, an ACCOUNT_LINK without a user, an
absolute or protocol-relative redirect target, an unknown purpose; every
identity column rewritten; two real connections racing for the claim.

## MUTATION_RESULT

**Not performed by source mutation for this unit.** The response that was to
write this unit's mutation script was withheld by the session's safety
classifier, and the same content is not to be produced again. The unit's
protections are instead each covered by a guard-necessity falsifier that
exercises the boundary directly at the database and at the service (the list
above), including the concurrency race, which is the falsifier a mutation of
the claim statement would have to fail. This is a disclosed deviation from
the mutation law for this unit, recorded here and in `STATUS.md`.

## SECURITY_RESULT

- Raw state, nonce and binding token never reach the database (asserted on
  the rendered row).
- The verifier never leaves the server at start and leaves the row exactly
  once, to the claim winner.
- No provider call, no identity, no session, no authority is produced.
- Failure reasons are the closed internal vocabulary; nothing here renders
  them to a public response.

## CONSUMER_PROOF / PRESERVATION_RESULT

No consumer exists yet. Every predecessor suite passes unchanged. Static
gates: ruff clean; mypy no issues (229 files); architecture, provider-SDK and
test-only import checks PASS. No browser surface changed; no browser proof due.

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu05_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `f3ec6b4b024edeb63a4acbeca07dbd1dfe27dfae44f657598611f996b7ed20d8` |
| Live result | 2125 passed, 2 skipped, 0 failed, exit 0 (0:35:49) = 2096 + 29 |
| No-database result | 942 passed, 1185 skipped, 0 failed, exit 0 |
| Migrations | single head `c4e6a8b1d3f5`; live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| state / nonce / binding token (raw, returned at start) | server random | PROTOCOL FACT |
| their hashes in the row | derived from the above | DERIVED FACT |
| code challenge | S256 of the server-generated verifier | PROTOCOL FACT |
| verifier handed to the winner | the row, in the claiming statement | PROTOCOL FACT, single use |
| `state` presented by a callback | browser / provider redirect | USER CLAIM; only a lookup key |
| binding token presented by a callback | browser cookie (WU-AUTH-07) | USER CLAIM; compared, never trusted |
| `purpose`, `initiating_user_id` presented by a callback | the route and the current session | DERIVED FACT of the server |
| `redirect_target` | caller-supplied at start | UNPROVEN until WU-AUTH-06 validates it; the CHECK bounds it to a local path |

Nothing presented by a browser becomes canonical truth through this relation.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: an OIDC start is a short-lived, purpose-bound
record that a single callback may claim once, from the browser that started
it, before its expiry, receiving the one secret needed for the exchange; all
other outcomes are terminal and evidenced. That is 24 §11.3–11.9. No second
transaction store, no browser-held verifier, no identity result.

## FIRST_BROKEN_RELATION_AFTER

**Redirect target legitimacy** (24 WU-AUTH-06; FBR-AUTH-015): the
transaction binds a redirect target, but nothing validates a candidate into
a legitimate local destination before it is bound, and no error/cancel
redirect rule exists.

## Limitations and ceilings

- No production consumer until WU-AUTH-07.
- No source-mutation proof for this unit (above).
- Human decisions are field-local; 16 §41 reconciliation deferred.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-05 proven with the mutation deviation disclosed. Next: WU-AUTH-06.
