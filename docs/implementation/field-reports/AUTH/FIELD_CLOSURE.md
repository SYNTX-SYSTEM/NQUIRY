# NQUIRY FIELD CLOSURE — AUTH / AUTHZ (PURPLE, with the CYAN consumption)

Closure pass of 2026-10-05 under the mandate "Close the current NQUIRY
Authentication and Authorization Field … do not extend the Field merely
because additional features are conceivable". Supersedes the status line of
`FIELD_REVIEW.md` (the first closure of 2026-10-01); every proof listed there
stands and is not repeated.

## Closure #4 (2026-10-06, HD-AUTH-10: the recovery boundary resolved)

The one closure-critical boundary of closures #2/#3 (section A, the block at
the end) was decided by the human on 2026-10-05 (HD-AUTH-10 / HA-AUTH-02):
self-service recovery through verified e-mail is part of the product, not
future scope; operator-mediated recovery may exist but does not replace it.
The recovery Field and the dependencies it entails were reconstructed:

| Relation | Work Unit | State |
|---|---|---|
| `VERIFIED_EMAIL_SELF_SERVICE` admitted in every declared environment (default DENIED unchanged) | WU-AUTH-21 (`d03d5ce`) | PROVEN |
| production e-mail delivery (24 §36 #16): SMTP submission, STARTTLS / implicit TLS only, SASL when configured, one rendered message with one link to the frontend's contact; delivery failure = `MAIL_DELIVERY_FAILED` event, the one answer kept at recovery start, 503 at verification start | WU-AUTH-21 (`packages/security/mail.py`, `auth_runtime.py`) | PROVEN against a real STARTTLS + AUTH submission service in-test |
| discovery of what a deployment serves: `GET /auth/contacts` | WU-AUTH-21 | PROVEN |
| the product surfaces: verified-address relation + Send in the Access security chamber, `/account/verify-email`, `/recover`, `/recover/reset`, "Forgot your password?" on the login — each only on the server's AVAILABLE | CYAN AUTH/CYAN-RECOVERY-01 (`auth-cyan-reconstruction` `7d214e6`) | PROVEN: vitest 678, cy11 10 / 10, cross-lineage real lane **14 / 14** (verification → recovery → login with the new password) |
| production activation | ASP-03 (api `d03d5ce`+, web `7d214e6`+) + the production `.env` mail facts | see "Closure #4 status" below |

### Closure #4 status

Code and proof complete on both lineages; full hash-proven regression and
production propagation recorded below as they happen (this document is
updated in place):

- PURPLE closure regression #4 on `accb976` (`evidence/field_closure_4_regression.txt`): **2538 passed / 2 skipped** (0:46:53), no-DB 1030, 44 migrations single head `e3a5c7d9f1b4`, tree hash unchanged during the run. CYAN mocked preservation set 194 passed, cy11 10 / 10, cross-lineage real lane 14 / 14.
- ASP-03 propagation: PENDING
- **EXTERNAL DEPENDENCY (not a Human Authority decision):** the production
  host's MTA (`mail.condyn.eu`, postfix, submission 587 + TLS) relays only
  for loopback or SASL-authenticated clients, and the api container is a
  bridge client. Activating recovery on production therefore needs, in the
  production `.env`: `NQUIRY_EMAIL_DELIVERY_MODE=smtp`,
  `NQUIRY_SMTP_HOST`/`PORT=587`/`SECURITY=starttls`, `NQUIRY_SMTP_FROM` (a
  sender identity of that MTA), `NQUIRY_SMTP_USERNAME`/`PASSWORD` (a SASL
  credential of that MTA — created by its operator, never by this Field),
  `NQUIRY_PUBLIC_WEB_BASE_URL=https://nquiry.condyn.eu`,
  `NQUIRY_RECOVERY_POLICY=VERIFIED_EMAIL_SELF_SERVICE`. Until they exist,
  the deployed product says "recovery is not available on this deployment"
  (`/auth/contacts` UNAVAILABLE) — a disclosed state, not a silent default.
  Section A below is thereby RESOLVED as a decision and OPEN only as this
  operational fact.

## Closure #3 (2026-10-05, mandate "complete and close as a complete operational product field")

The Field was re-reconstructed against the full identity and access lifecycle.
Four relations the accepted scope required were found missing and were
materialized, proven and published:

| Relation | Work Unit | Live since |
|---|---|---|
| a local password's owner rotates it (24 §9.2) | WU-AUTH-19 `POST /auth/password/change` | ASP-02 2026-10-05T15:24Z |
| the governance root ends a membership — role and every Workspace binding end in the same commit (05 GOV-003, 09 §102.1) | WU-AUTHZ-01 `POST /workspaces/{ws}/members/{user}/revoke` | ASP-02 |
| the governance root changes a member's role (05 GOV-004, §14) | WU-AUTHZ-01 `…/members/{user}/role` | ASP-02 |
| the login lockout boundary (24 §21.16, §22.3): address- and client-keyed windows, 429 `RATE_LIMITED`, audited, enumeration-resistant | WU-AUTH-20 (`auth_rate_limits`, head `e3a5c7d9f1b4`) | ASP-02 |
| the product surfaces for all of the above (password form; membership administration from the server's capabilities and per-member `administrable` verdict; the lockout presented as a pause) | CYAN AUTH/CYAN-ACCOUNT-02 `2fb7bfa` | ASP-02 (web root) |

Proof at this closure: full hash-proven regression on `28e6620`
(`evidence/field_closure_3_regression.txt`): **2530 passed / 2 skipped**,
no-DB 1026, 44 migrations single head `e3a5c7d9f1b4`, tree unchanged;
CYAN vitest 675, mocked lanes 172 + 12, cross-lineage real lane **12 / 12**
(incl. real rotation, roster administration and lockout). Production after
ASP-02: api `28e6620`, web `2fb7bfa`, head `e3a5c7d9f1b4`, `.env` and vhost
unchanged, baseline `_baseline-pre-ASP02-20261005T152356Z` (pg_dump, anchors
`nquiry-api:pre-asp02` / `nquiry-web:pre-asp02`, `ROLLBACK-asp02.sh`).

The remaining boundary is unchanged: section A below (recovery of a lost
local password, HA-AUTH-02 + 24 §36 #13). GAP-05-001 (owner succession) stays
an architectural gap of 05 enforced as a refusal.

## Status

**FIELD_CLOSED_WITH_ONE_RECORDED_HUMAN_BOUNDARY (2026-10-05).** Every
relation of the accepted product scope is materialized, proven and live;
the full repository regression on this HEAD's product tree is green
(`evidence/field_closure_2_regression.txt`: live **2499 passed / 2 skipped**,
no-DB 1024, 43 migrations single head `d2f4a6b8c1e3`, tree hash unchanged;
AUTH real lane 8 / 8; RED-line web 181; CYAN 672 + lanes + cross-lineage real
6 / 6). Exactly one closure-critical relation remains, and it is a Human
Authority decision that cannot be derived (section A below); until it is
taken the fail-closed default (DENIED) is in force and recorded. Nothing else
blocks NQUIRY architecture or product implementation on identity, authority
or authorization.

## The Field as it is (reconstructed 2026-10-05)

| Layer | Authoritative state | Evidence |
|---|---|---|
| Architecture | 24 (identity & authentication), 04 / 05 / 06 (authority, governance, boundaries), 16 §41 REC-001 (HARD-DEP-001 Option A), HD-28 / NQ-DEC-056 | `docs/architecture/` |
| Human decisions | HD-AUTH-01..09 (`HUMAN_DECISIONS.md`); 24 §36 resolved: #1 #2 #6 (HD-AUTH-09), #3–#5 (HD-AUTH-08), #13-disable / #15 (HD-AUTH-05, HARD-DEP-001), #12 default NEVER, #10 default 12 h | `HUMAN_DECISIONS.md` |
| Production api | `auth-identity` `64930ac` (assembly `auth-64930ac-20261005T113144Z`), migration head `d2f4a6b8c1e3`, `auth_runtime` principal for authentication persistence, Google = PRODUCTION_PROVIDER, `SELF_REGISTRATION_ALLOWED` (= provider bootstrap), recovery DENIED, `NQUIRY_ACCOUNT_SECURITY_PATH=/workspaces` | `STATUS.md`, server baselines `_baseline-pre-AUTH-*` |
| Production web | `auth-cyan-reconstruction` `94759cd` at the root (assembly `cyanroot-94759cd-20261004T155914Z`); Final Human Acceptance 2026-10-04 (HD-AUTH-09) | CYAN `WU-AUTH-CYAN-ACCOUNT-01.md`, `HUMAN_REVIEW_RESULT_AUTH_CYAN_ACCOUNT_01.md` |
| Production identities | `tobi` (LOCAL_PASSWORD), "SYNTX System" (GOOGLE_OIDC, PROVIDER_BOOTSTRAP_IDENTITY), four review identities (LOCAL) | `evidence/ha_auth_07_production_transition.txt` |
| Published lineage | `origin/auth-identity` = this commit; `auth-cyan-reconstruction` (worktree `auth-cyan`, local; base `frontend-symbiotic` `618d7a6`) | git |
| Proof lineage | first closure `FIELD_REVIEW.md` (2456 / 2); this closure `evidence/field_closure_2_regression.txt` (2499 / 2); AUTH real lane 8 / 8; RED-line web vitest 181; CYAN vitest 672, mocked lanes, cross-lineage real lane 6 / 6 | `evidence/` |

### Relations proven live on production (24 §48 #62–#63)
LOCAL login · Google LINK (2026-10-03) · Google LOGIN linked (2026-10-03) ·
owner UNLINK (2026-10-04) · Google LOGIN → PROVIDER_BOOTSTRAP (2026-10-04) ·
the Access security chamber and the identity organisms through the product
UI (Human Acceptance 2026-10-04) · audit events (2026-10-05, `LOGIN_FAILED`
probe).

## Closure scope decision

The product scope is what the human accepted on production (HD-AUTH-09):
LOCAL_PASSWORD and GOOGLE_OIDC login, provider-driven identity bootstrap,
identity presentation, account security (link, unlink, sessions), operator
identity creation and disable, the existing governance / authority chain for
every business effect. Against that scope every remaining open relation is
classified below; nothing is added because it is conceivable.

### A. Closure-critical — needs one Human Authority decision (cannot be derived)

| Relation | Why closure-critical | Default in force | Boundary |
|---|---|---|---|
| **Credential recovery for a LOCAL_PASSWORD identity in production** | HD-AUTH-09 admits password authentication in production. A local-only identity that loses its password has today no legitimate path back: self-service recovery is DENIED (HA-AUTH-02; no mail provider, 24 §36 #16), and no administrative reset exists (24 §36 #13). Its e-mail is unique, so it cannot be re-provisioned under the same address without losing its memberships. An identity dependency therefore remains unresolved for the accepted scope. | DENIED (fail closed) | HA-AUTH-02 + 24 §36 #13 — see the block below |
| *(2026-10-06)* **RESOLVED by HD-AUTH-10** — option (b) of the block below is the decided path and is materialized (WU-AUTH-21 + AUTH/CYAN-RECOVERY-01); (a) may be added later, (c) is excluded. What remains is the production mail-provider fact (external dependency, "Closure #4 status"). | | VERIFIED_EMAIL_SELF_SERVICE where configured | — |

### B. Closure-compatible as recorded (defaults in force, documented, no silent decision)

| Relation | State |
|---|---|
| HA-AUTH-03 unlinking the last method | NEVER (`409 LAST_METHOD`); complete and safe; the product UI withholds the control |
| 24 §36 #18 multi-account UX | a live session starting a provider login is not refused; the new session replaces the cookie, the earlier one stays listed and revocable until expiry (Access security) |
| 24 §36 #10 session lifetime | 12 h (WU-04), unchanged |
| 24 §36 #9 provider-verified e-mail as NQUIRY verified e-mail | a bootstrapped identity's canonical e-mail is the provider's verified claim (copied once, provenance recorded); no `verified_emails` relation is created by it — relevant only to self-service recovery (A) |
| anti-CSRF failures not audited as SecurityEvents | WU-AUTH-18 disclosure: edge log + 403 class remain the evidence (write-amplification) |
| F-AZ-2 existence oracle on two legacy routes | random UUIDs; recorded, RED-owned handlers |
| `/api/docs` public | allowed by 09 §172; recorded |

### C. Owned by another Field — not an AUTH/AUTHZ closure dependency

| Relation | Owner |
|---|---|
| Business-path DB principal / RLS at runtime (PFC HA-10; HD-AUTH-06 switched AUTH only) | RED / PFC |
| Governance successors: remove member, change / revoke role, owner succession (GAP-05-001), `FacilitatorScopeBinding` (NQ-GAP-080), GAP-05-002 | RED (05 GOV-003/004/008) |
| 16 §41 reconciliation of HD-AUTH-01..09 (REC / NQ-DEC numbers are allocated on the RED line) | the integration act |
| Branch integration: `auth-identity` and `auth-cyan-reconstruction` into their lineages; push of the CYAN branch | human / integration |

### D. Operational leftovers — human decisions, no Field relation

`/cy-review/` mount (now a duplicate of the root) · `nquiry-cy01-candidate` stack (since 2026-09-28) · unreferenced assembly `auth-64930ac-20261005T113056Z` (aborted first ASP-01 attempt) · publication of `5109e20` (per-method "last used" line, proven, not published).

### E. Explicitly future / optional scope (not required for closure)

Microsoft / GitHub providers (24 §36 #7 / #8) · provider tokens for API access (#14) · rate-limit thresholds beyond the existing attempt limits (#17) · INVITATION_REQUIRED / PRE_PROVISIONED / GOVERNANCE_MEDIATED creation policies (24 §11.14) · identity re-enable (one-way disable stays) · a second factor on recovery (HD-AUTH-10 decided none) · operator-mediated reset as an addition (HD-AUTH-10: permitted, not required).

## 24 §48 acceptance condition — delta since the first closure

Items 1–61 as in `FIELD_REVIEW.md` (unchanged, re-proven by this closure's
full regression). Items 62 (real-stack evidence) and 63 (provider evidence)
are now satisfied on production, not only on the local lanes. Item 51 (no
Human Authority boundary silently decided): the one remaining boundary is
stated below. Item 52 (no known internal contradiction): the stale
link-fallback target was repaired (`NQUIRY_ACCOUNT_SECURITY_PATH`, deployed);
24 §6.4's text "governance root open" is superseded by 16 §41 REC-001 (an
architecture-document edit, human-owned, F-AZ-6).

## TRUE_HUMAN_AUTHORITY_BOUNDARY — the one decision that closes the Field (DECIDED 2026-10-05: HD-AUTH-10 → option (b); kept as the record of the question)

```
BOUNDARY: HA-AUTH-02 (24 §36 #11) together with 24 §36 #13
QUESTION: How does a LOCAL_PASSWORD identity in PRODUCTION regain access after losing its password?
WHY IT IS HUMAN: 24 §36 lists recovery policy (#11) and administrative recovery (#13) as Human Authority; the default is fail closed (DENIED) and PURPLE may not decide it.
WHY IT IS CLOSURE-CRITICAL: HD-AUTH-09 accepted password login in production; without any recovery path an accepted identity relation can become permanently unreachable.
OPTIONS (what exists today, nothing is recommended):
  (a) OPERATOR_MEDIATED credential reset — a HOST_OPERATOR command on the host (pattern of HD-28 create / HD-AUTH-05 disable): attributable operator, SecurityEvent PASSWORD_RESET, every session of the identity revoked, no HTTP route, no self-service. Materializable from existing relations (WU-12's CREDENTIAL_RESET effect, the operator command shape); no external dependency.
  (b) VERIFIED_EMAIL_SELF_SERVICE in production — exists in code (WU-12), needs a production e-mail delivery provider (24 §36 #16, external) and verified e-mail relations (a bootstrapped identity has none yet).
  (c) DENIED remains — accepted as the product's scope: a locked-out local identity is disabled by the operator and the human continues under a new identity (memberships are not transferred).
  (a) and (b) are not exclusive.
DEFAULT IF UNDECIDED: (c) de facto, with the loss stated above.
```

## Integration notes (unchanged plus)

- `.env` of a deployment: `NQUIRY_ACCOUNT_SECURITY_PATH` = the product
  frontend's account-security location (`/workspaces` for CYAN).
- The CYAN consumption lives on `auth-cyan-reconstruction`; the
  `frontend-symbiotic` worktree holds uncommitted `HA-AUTH-CYAN.md` edits that
  must be merged by hand.
