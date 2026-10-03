# WORK UNIT REPORT

FIELD: NQUIRY_HUMAN_IDENTITY_PRESENTATION_FIELD (PURPLE)
WORK_UNIT: PURPLE_IDENTITY_PRESENTATION_01 — authenticated self identity presentation

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §13.1 (canonical identity), §13.9 (email relation), §13.10 (identity equivalence), §20.1 (what authentication may produce), §21.10; HD-28 / NQ-DEC-056 (identity creation); the Field brief of 2026-10-04 (laws, falsifiers, mutations) |
| PREDECESSOR | AUTH FIELD_GREEN `aa32c4d` (product `b47bc78`); REAL_GOOGLE_LINK and REAL_GOOGLE_LOGIN proven live 2026-10-03 |
| PROOF_RADIUS | Phase 1 read-only reconstruction → Phase 2 field decision (STATE A) → Phase 3 implementation → Phase 4 local falsifiers (11) → Phase 5 mutation proof (guard-necessity, no source-mutation script) → Phase 6 affected suites (security, regression, sweep, HTTP auth, WU-04/10/13/15/16, HD-28) → Phase 7 not performed (no deployment in this unit) |
| HUMAN_AUTHORITY_STATE | HA-AUTH-01/02/03 untouched; no new boundary crossed; one finding recorded for a later decision (below) |

## FIRST_BROKEN_RELATION_BEFORE

NQUIRY_IDENTITY → HUMAN_IDENTITY_PRESENTATION = NOT MATERIALIZED as a self
read: the authenticated identity ended at `userId` (`/auth/me`), so CYAN
could render how a session was made but not who the human is, independent
of the method.

## AUTHORITATIVE_SOURCE_RECONSTRUCTION (Phase 1, read-only)

| Candidate | Value class | Authoritative home | Object kind | Producer (writer trace) | Mutation authority | Readers (human-facing) | Exposed before | Safe to project |
|---|---|---|---|---|---|---|---|---|
| `users.id` | UUID | `users` | NQUIRY_IDENTITY key | identity creation | none | everywhere | `/auth/me` | yes |
| `users.name` | text, NOT NULL | `users` row | NQUIRY_IDENTITY attribute | HD-28 `create_identity_by_host_operator` (`--name` required, blank refused); DEV/TEST `_create_identity` (WU-09); dev script; fixtures | none (no update path; disable writes only `disabled_*`) | member roster `{userId,name,email,role}` (`inquiry_queries.py:383`), participants `user_name` (`:787`), admit/grant candidates `name` → rendered by CYAN rosters | to other members | yes — identity-owned, already human-facing |
| `users.email` | text, NOT NULL, UNIQUE | `users` row | NQUIRY_IDENTITY attribute (the "canonical `users.email`" of `oidc_identity.py`'s own contract; collision key of 24 §14.5) | same producers; HD-28 normalizes lower-case | none | member roster `email`, participants `user_email` | to other members | yes |
| local login identifier | — | **none of its own**: `local_auth_credentials` has `user_id` + hash only; `get_by_email` resolves the typed address via `users.email` | CREDENTIAL lookup through the identity attribute | — | — | — | — | not a separate relation: LOGIN_EMAIL *is* `users.email` by structure, not by promotion |
| provider email / display name | text | `external_provider_identities` | PROVIDER_BINDING attributes | link / first login; refreshed at provider login | provider | `/auth/methods` `provider.email` | yes (methods) | only as provider truth, never in the presentation |
| `display_name`, `canonical_email`, `login_email`, `username`, `label` columns | — | do not exist | — | — | — | — | — | — |

Finding F-IP-1 (disclosed, not changed): `oidc_identity._create_identity`
(DEV / TEST `SELF_REGISTRATION_ALLOWED` only) sets `users.name` to the
provider display name or, failing that, the email local-part at *creation*.
On production (HA-AUTH-01 DENIED) no identity was ever created this way; the
six live identities carry operator-entered names. What a policy-created
identity's name should be is part of the HA-AUTH-01 decision when it is
taken.

## FIELD DECISION (Phase 2)

STATE A: both human-facing attributes exist authoritatively on the identity
row, produced by the identity creation authority, immutable by every
authentication relation, and already projected to other humans. CEILING A is
reachable without any schema change.

## DERIVED IMPLEMENTATION (Phase 3)

Home: a **separate authenticated read contact**, not an extension of
`/auth/me`. `/auth/me` is the authentication verdict (`{kind, userId}`,
24 §20.1 AuthenticatedPrincipal) consumed by every frontend root guard; the
presentation is identity truth independent of authentication and gets its
own contact so the two questions stay distinct (AUTHENTICATION VERDICT !=
IDENTITY PRESENTATION).

| File | Change |
|---|---|
| `packages/persistence/identity_repository.py` | `presentation(user_id) -> (name, email) \| None` (reads `users` only) |
| `packages/application/identity_presentation.py` | new: `IdentityPresentation(user_id, display_name, canonical_email)`, `own_identity_presentation(connection, token, now)` — live session required, identity row required, else `SessionRequired` |
| `packages/application/http_identity.py` | new: `dispatch_identity_presentation` → `200 {kind:ok,userId,displayName,canonicalEmail}` / `401 NO_SESSION`; auth connector |
| `apps/api/src/nquiry_api/http/identity.py`, `main.py` | route `GET /auth/identity` |
| `tests/e2e/test_auth_identity_presentation.py` | 11 falsifiers |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` | route registered (own-identity exempt) |

Read contract: `GET /api/auth/identity` (deployed path), session cookie,
safe method (no CSRF), no parameters (self only), response keys exactly
`kind, userId, displayName, canonicalEmail` (both strings; the columns are
NOT NULL, so absence cannot occur in the current schema; a missing identity
row is a 401, never a partial body).

## SOURCE_AUTHORITY_PROOF

displayName: `users.name` ← HD-28 operator input (`IdentityCreationRefused
NAME_REQUIRED` otherwise) ← `users` row ← no mutation authority ←
`GET /auth/identity` (self, live session) ← CYAN (later Field).
canonicalEmail: `users.email` ← HD-28 operator input, normalized, unique ←
`users` row ← no mutation authority ← `GET /auth/identity` ← CYAN.
Every link in both chains exists in the repository; none is inferred.

## INVARIANCE PROOFS (Phase 4)

- LOCAL_PASSWORD: presentation readable with no provider method at all
  (FALSIFIER_02); `/auth/me` shape unchanged.
- GOOGLE_OIDC: the same identity via local → provider → local sessions
  yields byte-identical presentations while the current session's
  `methodType` changes LOCAL_PASSWORD → TEST_PROVIDER → LOCAL_PASSWORD;
  the provider email appears in `/auth/methods` only (FALSIFIER_01/03/15/16).
- LINK: before/after a completed link the presentation and the whole
  `users` row are unchanged (FALSIFIER_04/14); UNLINK leaves it (FALSIFIER_05,
  fixture).
- No promotion / invention: provider email == canonical email by value stays
  two relations (FALSIFIER_09); a name with punctuation differing from the
  local-part is returned verbatim and never the provider profile name
  (FALSIFIER_06/08); malformed source → 401 (FALSIFIER_10); unauthenticated →
  401 with no body beyond the denial (FALSIFIER_11); self-only — no
  parameter can name another identity (FALSIFIER_12); exact key set and a
  dataclass with three fields (FALSIFIER_13).

## MUTATIONS (Phase 5, guard-necessity)

M1/M2/M14/M15 killed by the resolver reading `users` only and the exact key
set; M3/M4/M13 by verbatim `users.name` with no fallback and the derived-name
falsifier; M5/M16 by the three-session invariance test; M6/M7 by the link /
unlink tests comparing the full `users` row; M8–M10 by the exact key set and
the three-field dataclass; M11 by the 401 test; M12 by the self-only route.
No source-mutation script (disclosed, as for the whole AUTH Field).

## AFFECTED SUITES (Phase 6)

`tests/security`, `tests/regression`, the route sweep, `test_http_auth`,
`test_auth_handler`, WU-04/10/13/15/16, HD-28's suite, this unit: **628 passed,
1 skipped** (0:10:44); ruff / mypy (263 files) / architecture / test-only /
migration checks clean; no migration (`evidence/identity_presentation_01_proof.txt`).

## FIELD_RECONSTRUCTION

NQUIRY IDENTITY (`userId`) → HUMAN IDENTITY PRESENTATION (`users.name`,
`users.email`, written by the creation authority, immutable by
authentication) → AUTHENTICATED SELF READ (`GET /auth/identity`) → CYAN
consumable projection; alongside, unchanged: IDENTITY → AUTH METHODS →
CURRENT SESSION → CURRENT METHOD → PROVIDER BINDING. AUTHENTICATION !=
AUTHORIZATION holds: the contract has no authority-shaped field and the
authority regression suite is part of the affected run.

## CLAIM_CEILING

CEILING A: HUMAN_IDENTITY_PRESENTATION = MATERIALIZED (source branch);
DISPLAY_NAME = AUTHORITATIVE (`users.name`); CANONICAL_EMAIL = AUTHORITATIVE
(`users.email`); LOCAL_PASSWORD and GOOGLE_OIDC → the same presentation.
Not deployed; not consumed by CYAN; F-IP-1 open for HA-AUTH-01.

## NEXT_FIELD_BOUNDARY

PURPLE_IDENTITY_PRESENTATION → CYAN_IDENTITY_PRESENTATION_CONSUMPTION
(typed client + the identity chamber), under its own authorization; the
production deployment of this contact is a separate deployment act.
