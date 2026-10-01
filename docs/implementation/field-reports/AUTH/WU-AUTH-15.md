# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-15 — Protocol Callback Semantics

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-15 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-15; §11.2, §11.19, §11.21; §21.8, §21.14; §38 falsifiers 67–70; §44.8 |
| PREDECESSOR | WU-AUTH-14 `26a134c` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL falsifiers (34, measured over every table) → AFFECTED suites: the OIDC security suite, the request-security suite, the route sweep, WU-07/08/09/10/13/14/15 (337 passed). Delta is declarative (constants) plus proof; no migration, no route, no frontend change. |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01..04 OPEN, unchanged. No boundary touched. |

## FIRST_BROKEN_RELATION_BEFORE

The callback's GET-with-effect nature was governed by the transaction
proof (WU-05/07) but not stated as one contract nor proven as one: which GET
routes are protocol contacts, what exactly each may write, and that every
other GET writes nothing were implied by many tests and declared nowhere.

## CURRENT_RELATION

`application.http_oidc` declares the protocol contacts and their write
sets: `PROTOCOL_CONTACTS` = login start (protocol initiation), login
callback and link callback (protocol response); `PROTOCOL_START_WRITE_SET` =
`{oidc_auth_transactions}`; `PROTOCOL_CALLBACK_WRITE_SET` =
`{oidc_auth_transactions, local_auth_sessions, users, authentication_methods,
external_provider_identities, security_events}`. The proof measures the row
counts of **every** user table around each contact: a first login writes
within the callback set (identity, method, binding, session, audit,
transaction); a returning login writes session, transaction, audit only; a
link callback writes method, binding, session (rotation), audit,
transaction, never `users`; the start writes the transaction only; thirteen
bypass attempts (no transaction, no state, no code, no binding cookie,
transplanted browser, wrong code, tampered nonce, invalid signature, foreign
audience, foreign issuer, missing subject, provider error, link callback for
a login transaction) each end as a `/login?auth=…` projection with no session
cookie, writes confined to the transaction's terminal state and audit, and
no second entry into the token exchange; every ordinary GET route of the API
(16, as Workspace A's owner with the sweep's full world) changes no table.

## INVARIANTS

1. A GET route either is a declared protocol contact or writes nothing.
2. The callback's effects are a closed set of protocol / identity relations;
   none of the business or authority relations (Workspaces, memberships,
   roles, bindings, participations, Sessions, Bursts, questions, Decisions,
   commit units, outbox) is in it.
3. No proof gate can be skipped into a session or an identity: every failed
   gate leaves at most a terminal transaction and an audit fact.
4. A failed transaction never re-enters the token exchange.
5. A created identity holds no Workspace (24 §11.14, §21.14 "grant Workspace
   authority": impossible by effect set).

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/application/http_oidc.py` | `PROTOCOL_CONTACTS`, `PROTOCOL_START_WRITE_SET`, `PROTOCOL_CALLBACK_WRITE_SET` (declared, documented, exported) |
| `tests/e2e/test_auth_wu15_protocol_callback.py` | new: 34 cases (contract, start, three callback effect sets, 13 bypasses, 16 GET routes) |

## Case 2 choices (recorded)

- **The login start GET is a protocol contact too** (initiation), not an
  ordinary resource: it writes one protocol row and sets the binding
  cookie, and the login page reaches it by navigation (24 §11.2, §11.21).
  Its effect set is declared separately and is the transaction only.
- **Write set measured by row counts of every table**, not by a list of
  "watched" tables: an unforeseen write anywhere fails the proof.
- **No new code path.** The contract was already true; this unit makes it
  declared (one place), checked (the GET sweep uses the declaration) and
  reconstructible.

## RED_RESULT

Collection error (`PROTOCOL_CONTACTS` absent): 0 of 34 could run. After the
declaration all 34 passed on the first run — the relation was true and
unstated. Two lint corrections in the test (Yoda comparisons, one long
comment); the issuer's defect vocabulary names (`wrong_nonce`, …) aligned.

## GREEN_RESULT

34 cases; static gates clean (ruff, mypy 259 files, architecture /
test-only imports). No frontend delta (the callback's browser handling —
projections on `/login`, `?link=` on `/account/security` — exists since
WU-07/10).

## ADVERSARIAL_RESULT

Proven by the falsifiers: see CURRENT_RELATION (13 bypass shapes × effect
set; 16 GET routes × every table; 3 callback kinds × write set).

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..14).

## AFFECTED_SUITES_RESULT

OIDC security suite, request-security suite, route sweep, WU-07/08/09/10/
13/14/15: **337 passed** (0:07:46; `evidence/wu15_proof.txt`). No full
repository regression (HD-AUTH-04).

## INVERSE_SWEEP_RESULT

A ROW WRITTEN BY A GET → the route is one of the three declared protocol
contacts → the table is in that contact's declared write set → for a
callback, every proof gate passed (transaction, binding, claim, PKCE, token
validation, nonce, subject, policy / linking authority) → the write is a
protocol-defined security or identity effect (24 §44.8). Any other GET
writing any row is a falsified invariant.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: the HTTP verb grants nothing (24 §11.19 "!=
authority by HTTP verb alone"); the callback's authority is the chain of
proofs it carries, and its reach is a closed set of relations that stops
before the first business or authority row. That is §21.14 as a measured
fact rather than a rule.

## FIRST_BROKEN_RELATION_AFTER

**Authorization regression** (24 WU-AUTH-16): the authentication Field has
grown eleven new contacts, new identities (provider-created, linked,
recovered, unlinked, disabled) and a new request boundary; the authorization
chain (membership, role, binding, participation, governance root) must be
re-proven unchanged against all of them as one unit (AUTHENTICATION !=
AUTHORIZATION), including the sweep's isolation for every new identity kind.

## Limitations and ceilings

- Real Google callback semantics BLOCKED_EXTERNAL (test issuer only).
- No source-mutation proof; ledger deferred; full regression at closure.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-15 proven. Next: WU-AUTH-16.
