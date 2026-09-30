# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-06 — Redirect Target Validation

| Item | Value |
|---|---|
| WORK_UNIT_ID | WU-AUTH-06 |
| ARCHITECTURE_SOURCE | 24 §37 WU-AUTH-06; §7 FBR-AUTH-015; §11.17; §21.15; §22.8; §32.8; §38 falsifiers 103, 104 |
| PREDECESSOR | WU-AUTH-05 `4495345` |
| HUMAN_AUTHORITY_STATE | HD-AUTH-01..03. No §36 boundary touched. |

## FIRST_BROKEN_RELATION_BEFORE

Redirect target legitimacy terminated in convention: a login start bound
whatever redirect target its caller supplied (bounded only by the database's
local-path CHECK), and no rule turned a candidate into a legitimate local
destination or a safe default.

## ROOT_SWEEP

- Producer: none; the relation was missing.
- Consumers: `application.oidc_transactions.start_transaction` (login and
  link start) and, through the bound value, the post-auth, error and cancel
  redirects of the callback routes (WU-AUTH-07). Recovery redirects
  (WU-AUTH-12) consume the same rule when they arrive.
- No other module redirects a browser today (the API answers JSON; the web
  app navigates client-side after `ok` results).

## CURRENT_RELATION

REDIRECT TARGET CANDIDATE → `security.redirect_target.is_legitimate_local_destination`
→ LEGITIMATE LOCAL DESTINATION (bound) | SAFE DEFAULT `/` (bound) | rejected boundary.

## INVARIANTS

1. A legitimate local destination is a path of this application: exactly one
   leading `/`, printable ASCII only, no whitespace or control character
   (literal or percent-encoded), no backslash, at most 1024 characters. Query
   and fragment are allowed.
2. No absolute or scheme-relative URL is a legitimate application target;
   in particular the provider's registered redirect URI is never one
   (falsifier 104: the two remain distinct).
3. `start_transaction` binds only the validated destination or the safe
   default. The database CHECK of `c4e6a8b1d3f5` remains an independent bound.
4. A rejected candidate is never echoed (`RedirectTargetRejected` carries no value).

## Case 2 choices (recorded)

- **Safe default over rejection at login start.** 24 §32.8 permits either. A
  hostile candidate in a login link must not be able to block a legitimate
  login, and it must never reach the transaction; the login proceeds to `/`.
  The rejecting form (`validate_redirect_target`) exists for contexts that
  must answer with the boundary (24 §32.2 `REDIRECT_TARGET_REJECTED`).
- **Percent-encoded control characters are refused** although they do not
  split a header while encoded: nothing needs them, and they are harmless
  only as long as nothing downstream decodes them.
- **Non-ASCII is refused**; an internationalised path would have to be
  percent-encoded before it is a candidate.

## DELTA_MATERIALIZED / FILES_CHANGED

| File | Change |
|---|---|
| `packages/security/redirect_target.py` | new: the rule, a validating and a defaulting entry point |
| `packages/application/oidc_transactions.py` | `start_transaction` binds `resolve_redirect_target(candidate)` |
| `tests/security/test_auth_redirect_target.py` | new: 31 cases |

No migration, no route, no frontend, no configuration.

## FALSIFIERS / TESTS_ADDED

`tests/security/test_auth_redirect_target.py`: a parametrized list of
illegitimate candidates (absolute and scheme-relative forms, wrong or missing
leading slash, whitespace and control characters literal and encoded,
backslash forms, non-ASCII, over-length, empty and absent) each of which must
be refused by the rule, rejected by the validating form and replaced by the
safe default by the defaulting form; a list of legitimate local destinations
(root, nested paths, query, fragment, unreserved characters, an encoded
space) each of which must pass unchanged; the provider redirect URI never a
target; and a transaction-binding case proving that only validated targets
or the default ever reach `oidc_auth_transactions`. Each check of the rule is
necessary for at least one listed candidate: the list is the guard-necessity
proof of the rule.

## RED_RESULT

Collection error (`security.redirect_target` absent), 0 of 31 could run.
After the first implementation 4 of 59 (with the transaction suite) failed:
the character class excluded every `/` after the first, so nested legitimate
paths were refused, and an encoded CR/LF pair was accepted. Both were
corrected; then green.

## GREEN_RESULT

31 new + 29 WU-AUTH-05 cases passed (the transaction suite is the consumer
proof: legitimate targets still bind unchanged).

## MUTATION_RESULT

No source-mutation script for this unit. The rule is a small pure predicate
whose every clause is pinned by a listed candidate (above); weakening any
clause fails that candidate's case. Disclosed as for WU-AUTH-05.

## SECURITY_RESULT

A browser can no longer be sent to a foreign origin through a transaction's
bound target; the rejected value is not echoed; the login is not deniable
through a hostile candidate.

## CONSUMER_PROOF / PRESERVATION_RESULT

Static gates: ruff clean; mypy no issues (230 files); architecture,
provider-SDK and test-only import checks PASS. No browser surface changed.

## FULL_REPOSITORY_REGRESSION

Run after the implementation was complete, with no change to the tree while
it ran (`evidence/wu06_regression.txt`).

| Item | Value |
|---|---|
| Pre-run tree hash | `5ec4a98bf5fe9253a68849197c47451a9fe3d5f99145f70c21dc8dcd22b3b4d5` |
| Live result | 2155 passed, 2 skipped, 0 failed, exit 0 (0:34:18) |
| No-database result | 971 passed, 1186 skipped, 0 failed, exit 0 |
| Migrations | single head `c4e6a8b1d3f5` (unchanged); live check PASS |
| Post-run tree hash | identical; git status identical |

After the run only this report and the evidence file were written.

## INVERSE_SWEEP_RESULT

| Output | Origin | Class |
|---|---|---|
| bound `post_auth_redirect_target` | the rule applied to the candidate, or the default | DERIVED FACT |
| the candidate | request / link parameter | USER CLAIM; never bound as such |

The `redirect_target` link that was UNPROVEN at WU-AUTH-05 is now proven.

## FIELD_RECONSTRUCTION_RESULT

From the proven relations: a redirect goes to a destination of this
application or to its root; the provider's callback address is a separate
registered fact. That is 24 §11.17 / §21.15. No accidental architecture.

## FIRST_BROKEN_RELATION_AFTER

**External provider proof** (24 WU-AUTH-07; FBR-AUTH-001, -012, -016): no
provider port, no start/callback contact, no token exchange, no ID Token
validation, no provider error/cancel path, no test provider. Real Google
proof will additionally need real client credentials (an external secret).

## CURRENT_FIELD_STATUS

IN_PROGRESS. WU-AUTH-06 proven (mutation deviation disclosed). Next: WU-AUTH-07.
