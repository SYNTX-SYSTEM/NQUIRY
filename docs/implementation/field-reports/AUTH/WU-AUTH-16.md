# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-16 — Authorization Regression

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-16 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-16; §20.1–20.3; §11.14; §18.2 "authorization must fail before business capability"; §38 falsifiers 71–73; §44.9; HARD-DEP-001 REC-001 |
| PREDECESSOR | WU-AUTH-15 `5fe3cd6` |
| PROOF_RADIUS (HD-AUTH-04) | LOCAL regression suite (15 cases: 6 identity kinds × the full protected route table, membership path, founding parity, disabled identity, principal shape) → AFFECTED suites: `tests/authority`, `tests/regression`, the isolation sweep, `test_http_f02`, WU-09 (259 passed). No code delta. |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..04; HA-AUTH-01..04 OPEN, unchanged. §36 #15 (governance bootstrap for provider-created identities) touched again and left as REC-001's wording (see Case 2). |

## FIRST_BROKEN_RELATION_BEFORE

The Field had produced new identity kinds (provider-created, linked,
recovered, unlinked, rotated, disabled) and eleven new contacts; each unit
proved "no authority" for its own kind, but the authorization chain had not
been re-proven as one unit against all of them over every protected route.

## CURRENT_RELATION

For each identity kind the Field can produce — `local_password`,
`provider_created` (SELF_REGISTRATION in TEST), `linked_then_provider_login`,
`rotated_after_link`, `recovered` (logged in with the reset password),
`unlinked_remaining_method` — the authenticated principal is the same
`AuthenticatedPrincipal` (24 §20.1 fields only), holds zero authority
relations (Workspaces owned, memberships, role assignments, bindings,
participations), lists no Workspace, and is denied on every non-exempt route
of the F09-2 isolation sweep's table against Workspace A without disclosure
of its ids and without any protected-table mutation. Access to Workspace A
comes only through the owner's governed membership command, after which the
identity reads the Workspace like any member, still holds no binding or
participation, and is still denied the governed Session transitions
(membership != control). Founding a Workspace is an explicit command with the
same outcome for a provider-created and a local identity; the login itself
founds nothing. A disabled identity has no principal at all: membership is
preserved but never consulted (401 before any business capability).

## INVARIANTS

1. AUTHENTICATION != AUTHORIZATION, for every kind: the principal carries
   identity, session reference, time and issuer — nothing else.
2. IDENTITY CREATION != MEMBERSHIP != ROLE != AUTHORITY: no login kind writes
   or implies any of the five authority relations.
3. The existing authority resolver and boundary chains decide every
   protected route identically for every login kind (same denial class, same
   non-disclosure, same non-mutation).
4. OIDC CALLBACK != BUSINESS AUTHORITY; LOCAL PASSWORD LOGIN != BUSINESS
   AUTHORITY: founding remains an explicit, equal command.
5. Account disable removes the principal before authorization (24 §18.2).

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `tests/e2e/test_auth_wu16_authorization_regression.py` | new: 15 cases over the sweep's world and route table |

No product code changed: the regression found no defect.

## Case 2 choices (recorded)

- **Reuse of the F09-2 world and `ROUTES`** so the regression is the
  repository's own protected surface, not a hand-picked subset; the
  cross-Workspace-exempt (own-identity) contacts are excluded as they are
  there.
- **Founding parity, not founding prohibition.** HARD-DEP-001 REC-001 lets a
  verified human found a Workspace (F01). Whether a provider-created identity
  counts as such is §36 #15 (recorded OPEN since WU-09, not blocking). The
  regression asserts what 24 §20.3 forbids — that creation or login founds
  anything by itself — and that the explicit act is treated identically.
- **Member transition check presents the current version**: F02 answers
  `stale` before authority for a member; the regression re-presents the
  current version and then expects the authority denial. The precedence is
  F02's, unchanged.
- **Frontend "authenticated but unauthorized distinct"** is already proven by
  the Workspaces surface (`workspaces.spec.ts`: 401 → `/login`, 403 →
  `orientation-denied`); no new surface was needed.

## RED_RESULT

No RED by absence: this is a regression unit over existing code. First run
failed on the test's own queries (authority column names: `owner_id`,
`human_user_id`, role assignments by membership) and on the member transition
precedence (`stale` before `denied`); both were test corrections. The product
answered correctly throughout.

## GREEN_RESULT

15 cases; static gates clean.

## ADVERSARIAL_RESULT

Six identity kinds × every protected route denied / undisclosed / unmutated;
six kinds × membership path (access after the command, still no control);
founding parity; disabled identity 401 with membership preserved; principal
dataclass fields exactly four.

## MUTATION_RESULT

No source-mutation script (disclosed, as for WU-AUTH-05..15).

## AFFECTED_SUITES_RESULT

`tests/authority`, `tests/regression`, the isolation sweep, `test_http_f02`,
WU-09, WU-16: **259 passed** (0:04:47; `evidence/wu16_proof.txt`).

## INVERSE_SWEEP_RESULT

A BUSINESS EFFECT COMMITTED FOR AN IDENTITY → the authority resolver found a
membership / role / binding / participation → written by a governed command
of someone who held the authority to write it → never by a login, a
callback, a link, a recovery, an unlink or a creation (24 §44.9).

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: how a human proved who they are has no bearing
on what they may do; the whole Field ends at `AuthenticatedPrincipal`, and
every door after that is the one the governed product already had.

## FIRST_BROKEN_RELATION_AFTER

**Runtime DB principal capability boundary** (24 WU-AUTH-17; §21.18;
FBR-AUTH-006): the authentication relations are written by the runtime's
database principal whose capability set is not yet scoped to them; the unit
reaches PFC HA-09 / 24 §36-adjacent human authority (the deployment's
principal grants are a production action).

## Limitations and ceilings

- Provider-created identities exist only under the TEST / DEVELOPMENT
  SELF_REGISTRATION branch (HA-AUTH-01).
- No source-mutation proof; ledger deferred; full regression at closure.

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-16 proven. Next: WU-AUTH-17.
