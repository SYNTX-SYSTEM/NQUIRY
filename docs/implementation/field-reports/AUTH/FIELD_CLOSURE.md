# NQUIRY FIELD CLOSURE — AUTH / AUTHZ (PURPLE, with the CYAN consumption)

Closure pass of 2026-10-05 under the mandate "Close the current NQUIRY
Authentication and Authorization Field … do not extend the Field merely
because additional features are conceivable". Supersedes the status line of
`FIELD_REVIEW.md` (the first closure of 2026-10-01); every proof listed there
stands and is not repeated.

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

Microsoft / GitHub providers (24 §36 #7 / #8) · provider tokens for API access (#14) · rate-limit thresholds beyond the existing attempt limits (#17) · INVITATION_REQUIRED / PRE_PROVISIONED / GOVERNANCE_MEDIATED creation policies (24 §11.14) · identity re-enable (one-way disable stays) · e-mail verification in production (needs #16).

## 24 §48 acceptance condition — delta since the first closure

Items 1–61 as in `FIELD_REVIEW.md` (unchanged, re-proven by this closure's
full regression). Items 62 (real-stack evidence) and 63 (provider evidence)
are now satisfied on production, not only on the local lanes. Item 51 (no
Human Authority boundary silently decided): the one remaining boundary is
stated below. Item 52 (no known internal contradiction): the stale
link-fallback target was repaired (`NQUIRY_ACCOUNT_SECURITY_PATH`, deployed);
24 §6.4's text "governance root open" is superseded by 16 §41 REC-001 (an
architecture-document edit, human-owned, F-AZ-6).

## TRUE_HUMAN_AUTHORITY_BOUNDARY — the one decision that closes the Field

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
