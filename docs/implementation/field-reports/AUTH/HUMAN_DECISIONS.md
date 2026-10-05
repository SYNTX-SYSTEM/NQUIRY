# HUMAN DECISIONS — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)

Field-local record. IDs are `HD-AUTH-n`. They are not yet reconciled into
`16_DECISION_GAP_REGISTER.md` §41 (see "Ledger reconciliation" at the end).

## HD-AUTH-01 — Field authorization (2026-09-30)

**Decision (human operator, the PURPLE execution brief of 2026-09-30, confirmed
as the operator's own instruction in the same session):** PURPLE is authorized
to materialize the complete Identity & Authentication Field defined by
Architecture 24 (`24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`),
autonomously, one proven relation at a time, in its own worktree and branch.

**What it authorizes:** reading, analysis, implementation, tests, migrations in
isolated test environments, local proof infrastructure, documentation, Work
Unit reports, and one local commit per fully proven Work Unit.

**What it does not decide:** any of the 18 Human Authority boundaries of
Architecture 24 §36. Each stays fail-closed (24 §36 "Default behavior for
unresolved human authority") until the Field reaches it and the operator
decides it. No push, no tag, no production action, no production migration.

**Relation to PFC HA-09:** `PFC/HUMAN_AUTHORITY_QUEUE.md` lists HA-09
("Architecture 24 Identity scope and its 18 §36 decisions") as OPEN at the
PURPLE base. HD-AUTH-01 answers the *scope* half (the Field may be
materialized). The §36 decisions stay open. The queue file is RED's record and
is not edited by PURPLE.

## HD-AUTH-02 — PURPLE predecessor: pinned RED checkpoint (2026-09-30)

**Question:** Architecture 24 is on `master` (`6e7e402`). The HD-28 / AC1.1
account-creation producer and seven newer migrations exist only on the RED
line. Which commit is PURPLE's predecessor?

**Options presented:** `checkpoint-PFC-AC1.1` (`e91961e`);
`checkpoint-PFC-SFE-PCPG` (`395ecf7`); `master` (`6e7e402`).

**Decision (human operator):** `checkpoint-PFC-AC1.1`.

- Commit `e91961e4a66ab21d9edf45d74bb43b8fbd324737`, tree `af6da710a9c5d81c48f3e84ecadc310e7edabd50`.
- Migration head at the pin: `e8c2a5f1b7d4`.
- The pin is a fixed commit, never the moving `pfc-integration` branch (the
  HD-27 precedent). RED's ceiling is unchanged by consumption: CHECKPOINTED,
  not REVIEWED_FIELD, not PUBLISHED_FIELD.

## HD-AUTH-03 — Work Unit commits without the per-commit gate (2026-09-30)

**Question:** 20 §14 (no-commit law) and the standing project rule require an
explicit approval before every commit. The brief authorizes local Work Unit
commits after full proof.

**Decision (human operator):** "Yes, commits included." PURPLE may create one
local commit per fully proven Work Unit on branch `auth-identity`. Never push.
No production tags.

**Scope:** this Field and this branch only. It does not change 20 §14 for any
other Field.

## HD-AUTH-04 — Proof cadence: progressive proof radius (2026-10-01)

**Decision (human operator, SFE proof-cadence update, confirmed in session):**
From WU-AUTH-11 onward the per-Work-Unit full-repository regression of the
original brief is replaced by a progressive proof radius:

```
IMPLEMENT / REPAIR → LOCAL FALSIFIERS → LOCAL MUTATION PROOF → AFFECTED SUITES → CONTINUE
LOCAL → AFFECTED → AUTH FIELD / INTEGRATION → FULL REPOSITORY
```

- A local defect or a failed affected test does not trigger a full
  regression; it is repaired and re-proven at the narrowest valid radius.
  Repairs may accumulate under local / affected proof as long as no failure
  is hidden or deferred unresolved. `ERROR FOUND != FULL REGRESSION REQUIRED`.
- A broader AUTH integration regression runs at meaningful block boundaries;
  failures it reveals are repaired one by one at the narrowest radius, then
  the broader level is rerun.
- The FULL repository regression runs only at final AUTH Field closure, at a
  deliberately selected major checkpoint, or immediately when a delta touches
  a genuinely global invariant (migration-wide semantics, shared persistence
  infrastructure, the session foundation, identity / authority boundary
  infrastructure, repository-wide protocol or serialization changes).
- The regression running at the time of the decision (WU-AUTH-10) finishes
  normally and is the current broad preservation checkpoint.
- Tests are not weakened; failures are not hidden; only the expensive global
  re-proof is deferred to the appropriate boundary.

**Why:** the full run costs 35–45 minutes per Work Unit; the proof radius must
follow the relations a delta affects, not the fact that a defect was found.

**Recorded:** here, `STATUS.md` (cadence line), and the WU reports from
WU-AUTH-11 on (a "PROOF_RADIUS" line replaces the per-WU full regression block).

## HD-AUTH-05 — HA-AUTH-04 resolved: identity disable authority = HOST_OPERATOR (2026-10-01)

**Decision (human operator, Human-Authority closure pass, verbatim intent):**
In PRODUCTION / STAGING, identity disable authority belongs to the
HOST_OPERATOR: HD-28's host-operator authority is extended to the already
materialized server-side identity-disable command. Constraints:

- no public HTTP disable route;
- no self-disable authority;
- no role-, membership-, email- or session-derived disable authority;
- operator identity must be attributable and recorded;
- disable remains audited and provenance-bearing;
- disabling remains one-way in the currently materialized field;
- re-enable is NOT granted by this decision and remains a separate Human
  Authority boundary (24 §36 #13);
- this decision grants only identity-disable authority, not broader account
  administration authority.

**Materialization (only what was already present):** the environment gate
that encoded "undecided" (`ACCOUNT_DISABLE_EXPOSURE_UNDECIDED` for
PRODUCTION / STAGING) is removed from `application.account_disable`; every
constraint above is structural and unchanged (no route — proven by
`test_no_http_route_disables_identities`; operator in `actor_id`,
`disabled_provenance` and the SecurityEvent; one-way trigger; no re-enable
path exists). `NQUIRY_ENVIRONMENT` must still be declared. Proof:
`tests/e2e/test_auth_wu13_revocation.py` (the command disables under a
declared PRODUCTION with the operator recorded; a second run is
`ALREADY_DISABLED`), WU-16 / WU-17 / HD-28 suites: 81 passed.

**Still OPEN after this decision:** re-enable / administrative recovery
(§36 #13); HA-AUTH-03 keeps only its default (NEVER) and option (c) — option
(b) "self-disable" is excluded by this decision's constraints.

## HD-AUTH-06 — HA-AUTH-05 resolved: SWITCH AUTH ONLY (2026-10-01)

**Decision (human operator, Human-Authority closure pass):** the running
deployment and the local compose stack perform authentication persistence
under the scoped principal `auth_runtime`; business paths keep their current
principal (option "SWITCH AUTH ONLY" of the HA-AUTH-05 block). The decision
sets the target posture; executing it on the live deployment is a separate
deployment act (PFC HA-10 external effect), not performed by PURPLE.

**Materialization (only what was already present):**
- local compose: `docker-compose.yml` `api` service gains
  `NQUIRY_AUTH_DATABASE_URL` (default `auth_runtime` on the compose
  database; `infra/local/db_roles.sql` once, then migrations). The worker
  performs no authentication persistence and is unchanged.
- deployment procedure, recorded for the deployment act (not executed): (1)
  run `infra/local/db_roles.sql` against the deployment database **with a
  production credential for `auth_runtime`** in place of the local-dev
  password (11 §23: the credential source is the deployment's, never the
  repository's); (2) apply migrations through `c1e3a5b7d9f2`; (3) set
  `NQUIRY_AUTH_DATABASE_URL` in the API's environment; (4) verify
  `auth_persistence_scope() == SCOPED` and the live login path; rollback =
  unset the variable (the runtime falls back to `DATABASE_URL`, declared
  `UNSCOPED_BOOTSTRAP`).
- no code change: `connect_auth`, the grants and the declaration exist since
  WU-AUTH-17.

**Not decided by this:** the HTTP server's business-path principal (the
wider HA-10 question); re-enable / §36 #13; anything about pushing,
integrating or deploying the branch.

## HD-AUTH-07 — PURPLE_IDENTITY_PRESENTATION_01 authorized (2026-10-04)

**Decision (human operator, Field brief):** read-only reconstruction of
existing identity truth; materialization of a safe authenticated
identity-presentation read contract ONLY IF authoritative source relations
already exist; minimal composition; typed tests. Not authorized: inventing
or guessing a name, promoting provider or credential email, profile
mutation, account settings, any change to creation / linking /
authorization. Outcome: STATE A reconstructed (`users.name`, `users.email`
produced by the identity creation authority, immutable by authentication,
already human-facing to other members) → `GET /auth/identity` materialized
(`WU-PURPLE-IDENTITY-PRESENTATION-01.md`). Deployment of the contact is a
separate deployment act; CYAN consumption is the next Field.

**Finding F-IP-1 for HA-AUTH-01:** DEV / TEST policy creation names a new
identity after the provider display name or the email local-part
(`oidc_identity._create_identity`). Never exercised on production (DENIED).
When HA-AUTH-01 is decided, the name a policy-created identity receives is
part of that decision.

## HA-AUTH-07 — OPEN: the live Google binding of identity `tobi` vs the human's intent (2026-10-04)

**Reconstructed from production (read-only, redacted):** exactly one provider
binding exists: Google subject `689df8a6…` (provider email domain
protonmail.com, email hash `35362e41…`, display name hash `28b2cf5b…`) →
identity `7dd6e767` (`tobi`, canonical email at thescaleforge.com). It was
created at 2026-10-03T16:48:42Z by the ACCOUNT_LINK transaction initiated by
that identity's own live LOCAL_PASSWORD session (the human's browser-console
link step of the authorized REAL GOOGLE LINK proof), audited as
`AUTH_METHOD_LINKED` with `actor_id = 7dd6e767`. Every later Google login
resolved to `tobi` through this binding and nothing else (the login callback
reads no session cookie, no previous identity, no email). No identity carries
the protonmail address; production account creation is DENIED (HA-AUTH-01).

**Human intent (2026-10-04):** this Google account is NOT meant to represent
`tobi`. The binding is legitimate under 24 §14.2 (a link binds the provider
subject to the authenticated identity that initiates it) but contradicts the
intended identity separation. Changing it mutates production identity
ownership → Human Authority.

Options (no preference implied):
(a) UNLINK from `tobi` (allowed by existing law: own-session action, LOCAL
    method remains, ends the Google-produced sessions; the subject then stays
    known and its login is denied — `failed`); nothing else.
(b) (a) + create a new NQUIRY identity for that human by the HD-28
    host-operator command (name, email, password chosen by the operator), then
    that identity links the Google account from its own session.
(c) (a) + link the Google account to an existing other identity (e.g. `62c8bb79`
    `otti`) from that identity's own session.
(d) KEEP the binding (status quo). Default while undecided: (d).

Process finding: the proof instruction "log in locally, then link" did not
state that the link makes that local identity the permanent owner of the
Google login; a future link surface (CYAN) must say which identity will own
the provider account before the start.

## HA-AUTH-01 — refined by PROVIDER_BOOTSTRAP_01 (2026-10-04), still OPEN

The generic provider-driven identity relation of 24 §11.14
(`SELF_REGISTRATION_ALLOWED`, provenance class PROVIDER_BOOTSTRAP_IDENTITY) is
now materialized and proven in TEST with these semantics: display name and
canonical email are copied from the provider's claims at creation (display
name required — never invented; email verified — never promoted), owned by
NQUIRY afterwards (provider drift refreshes the binding only); an email
collision is refused (the owner's own LINK is the path); an unlinked subject
bootstraps a NEW identity; no authority of any kind is created. The decision
remaining is unchanged: whether PRODUCTION / STAGING admit this class (and for
which production-enabled provider, §36 #1/#6). Default DENIED in force.
Consequence for HA-AUTH-07: option (b) "new identity for the Google account"
can be realized by bootstrap only after this decision; until then only via
HD-28 operator creation + the new identity's own LINK.

## HD-AUTH-08 — HA-AUTH-01 and HA-AUTH-07 resolved (2026-10-04)

**Decision 1 (human operator):** generic external-provider identity bootstrap
is authorized for PRODUCTION. Semantic and provider-generic. It does NOT
authorize email-string or display-name merging, reuse of a previous local /
browser identity, silent role / membership / authority creation, weakening
provider verification, or Google-specific hard-coding.
**Materialization:** `SELF_REGISTRATION_ALLOWED` (= PROVIDER_BOOTSTRAP class,
24 §11.14) is admitted in every DECLARED environment; undeclared refuses
(AC-11-017). Default remains DENIED; the policy must be set explicitly
(`NQUIRY_ACCOUNT_CREATION_POLICY`). Semantics as proven in
`WU-PROVIDER-BOOTSTRAP-01.md`: verified email + display-name claim required,
copied once, provenance recorded, collision refused, no authority. The
production switch of the policy is the deployment effect of this decision.

**Decision 2 (human operator):** the external Google identity presently bound
to `tobi` (HA-AUTH-07) is not intended to remain owned by that identity; the
ownership may be transitioned away from `tobi`; `tobi` and every unrelated
relation are preserved.
**Legitimate transition (derived):** (1) production admits bootstrap (Decision
1) — BEFORE the unlink, otherwise the unlinked subject would be denied at its
next login; (2) the owner identity unlinks the Google method through its own
live session (`POST /api/auth/methods/{id}/unlink`; LOCAL stays, so not
LAST_METHOD; the Google-produced sessions end; the binding becomes revoked
evidence); (3) the next Google login of that subject bootstraps its OWN NQUIRY
identity from the provider claims (`previouslyBound: true`). Steps 2 and 3 are
human browser actions (the owner's session; Google consent) and are not
performed by PURPLE.

**Executed on production by the human, observed read-only (2026-10-04,
14:25:01Z unlink → 14:28:16Z bootstrap):** `evidence/ha_auth_07_production_transition.txt`.
Security events `AUTH_METHOD_UNLINKED` (remainingActiveMethods 1,
providerBindingRevoked true) and `IDENTITY_CREATED` (identityClass
PROVIDER_BOOTSTRAP_IDENTITY, nameSource / emailSource = provider claims,
previouslyBound true, workspaceAuthority NONE); `tobi` unchanged
(record_version 1, memberships 2). HA-AUTH-07 is CLOSED; the generic
bootstrap is proven live once (24 §41 / §48 #62–63 for this relation).

## HD-AUTH-09 — Final Human Acceptance of the production authentication frontend (2026-10-04)

**Decision (human operator, verbatim essentials):** Human Frontend Acceptance on
`/cy-review/` "successful"; "Publish the accepted candidate to the production
root"; after publication and proof: "Final Human Acceptance on
https://nquiry.condyn.eu/: ACCEPTED. I verified the production root directly.
The production authentication frontend and the required human flows work
correctly."

**What it establishes (persisted):** the product frontend of the
authentication Field is the CYAN lineage at `auth-cyan-reconstruction`
`94759cd` (AUTH/CYAN-ACCOUNT-01), served at the production root since
2026-10-04T15:59Z (api `e069fc1`). The human flows accepted on production:
local password login, Google login (LINKED and BOOTSTRAP cases), identity
presentation, the Access security chamber (methods, link, sessions, sign out
everywhere). The AUTH-line web in this branch (`apps/web`) remains a proof
surface of the API, not the product.

**24 §36 boundaries resolved by this acceptance (recorded, not inferred):**
#1 official login methods = LOCAL_PASSWORD and GOOGLE_OIDC; #2 password
authentication is allowed in production; #6 Google OIDC is production-enabled
for the first release. (#3–#5 by HD-AUTH-08; #15 by HARD-DEP-001 Option A:
identity creation never founds, founding is a separate act.)

**Propagation derived from the resulting state (this commit):** the API's
link-projection fallback named a route of the AUTH-line web
(`/account/security`) that the product frontend does not serve; it is now
runtime-configured (`NQUIRY_ACCOUNT_SECURITY_PATH`, a local destination,
default unchanged) — `tests/e2e/test_auth_account_security_path.py`. The
production value `/workspaces` takes effect with the next API deployment
(human-run; recorded in `STATUS.md`).

## HD-AUTH-10 — HA-AUTH-02 resolved: VERIFIED_EMAIL_SELF_SERVICE is part of the product (2026-10-05)

**Decision (human operator, verbatim):** "HA-AUTH-02: A complete production
LOCAL_PASSWORD lifecycle requires legitimate self-service recovery through
verified e-mail. This is part of the current NQUIRY Authentication and
Authorization Field, not future scope. Reconstruct the complete recovery Field
and all dependencies it legitimately entails, including the existing production
mail-provider boundary. Operator-mediated recovery may exist where legitimate,
but does not replace the required self-service recovery path."

**What it establishes (persisted):** 24 §36 #11 = VERIFIED_EMAIL_SELF_SERVICE
with the proof level of §17.6–17.7 as materialized by WU-AUTH-11/12 (a
verified e-mail relation of the identity, a single-use time-boxed challenge,
the one answer at start, no session from completion, every ACTIVE session of
the identity revoked by completion). A second factor was not decided and is not
materialized. OPERATOR_MEDIATED (§36 #13) remains undecided and unmaterialized;
by this decision it could only ever be an addition, never the required path.

**Reconstruction (WU-AUTH-21, `d03d5ce`) — the dependencies the decision
legitimately entails:**
1. *Policy admission*: `NQUIRY_RECOVERY_POLICY=VERIFIED_EMAIL_SELF_SERVICE` is
   admitted in every declared environment (previously refused outside
   DEVELOPMENT / TEST); only an undeclared environment is still refused
   (`test_self_service_recovery_needs_a_declared_environment`). The default
   stays DENIED: a deployment that does not configure recovery has none.
2. *Production e-mail delivery* (§36 #16, the "existing production
   mail-provider boundary"): `SmtpMailSink` / `smtp_transport`
   (`packages/security/mail.py`) — STARTTLS or implicit TLS always (plaintext
   submission refused), SASL when configured, certificate verification never
   disabled, the challenge rendered as ONE message with ONE absolute link to the
   frontend's own contact; delivery failure is a recorded `MAIL_DELIVERY_FAILED`
   security event without address or token, the recovery start still answers
   with the one answer, the verification start answers 503
   `EMAIL_DELIVERY_FAILED`. Configuration: `NQUIRY_EMAIL_DELIVERY_MODE=smtp`,
   `NQUIRY_SMTP_HOST/PORT/SECURITY/FROM/USERNAME+PASSWORD/CA_FILE`,
   `NQUIRY_PUBLIC_WEB_BASE_URL`, `NQUIRY_EMAIL_VERIFY_PATH`,
   `NQUIRY_RECOVERY_COMPLETE_PATH`. Proven against a real STARTTLS + AUTH
   submission service in-test (`tests/e2e/test_auth_wu21_mail_delivery.py`).
   **Which provider, which sender identity and which credentials is the
   operator's (24 §36 #16) — see the external dependency below.**
3. *Discovery*: `GET /auth/contacts` (unauthenticated) states whether this
   deployment serves recovery and e-mail verification, so the product offers
   the contacts only where they exist (SERVER CAPABILITY → UI AFFORDANCE).
4. *The product frontend* (CYAN `auth-cyan-reconstruction` `b75ea1f`,
   AUTH/CYAN-RECOVERY-01): the E-mail verification relation and Send control
   in the Access security chamber, `/account/verify-email`, `/recover`,
   `/recover/reset`, "Forgot your password?" on the login. Proven end to end
   on the cross-lineage real lane (verification → recovery → login with the
   new password; 14/14).

**External dependency (not a human decision, not resolvable by this Field):**
the production host's MTA (`mail.condyn.eu`, postfix, submission on 587 with
TLS) relays only for loopback (`mynetworks`) or SASL-authenticated clients;
the api container is a bridge-network client. Production delivery therefore
needs either a SASL mailbox / credential for the sender identity on that MTA,
or the host operator's own relay decision. Neither is created, read or changed
by this Field (foreign mail-server configuration is never edited). Until the
facts exist in the production `.env`, the deployment serves
`recovery = UNAVAILABLE`, offers no recovery contact, and the product says so;
this is a correct, disclosed state, not a hidden failure.

**Consequence for HA-AUTH-03:** its precondition "HA-AUTH-02 ≠ DENIED" is now
met; the boundary itself (unlinking the last method) remains undecided and
NEVER remains in force. It blocks nothing.

## Open boundaries (OPEN, awaiting the operator)

| # | Boundary | Home | What it blocks | Default in force | Status |
|---|---|---|---|---|---|
| HA-AUTH-01 | **Production account creation policy for an unknown, verified external-provider subject** | 24 §11.14, §36 #3–#5; HD-28 | — | SELF_REGISTRATION_ALLOWED = PROVIDER_BOOTSTRAP (HD-AUTH-08) | **RESOLVED** by HD-AUTH-08 (2026-10-04): generic provider bootstrap admitted in PRODUCTION with the stated exclusions |
| HA-AUTH-02 | **Production recovery policy and proof level** (24 §36 #11; §17.6–17.7). Full block: `WU-AUTH-12.md`. | 24 §17, §36 #11 / #13; HD-28 (host-operator provisioning) | — | VERIFIED_EMAIL_SELF_SERVICE where configured (HD-AUTH-10); DENIED where not | **RESOLVED** by HD-AUTH-10 (2026-10-05): self-service recovery through verified e-mail is part of the product; materialized by WU-AUTH-21 + AUTH/CYAN-RECOVERY-01; production activation awaits the mail-provider facts (external dependency, see HD-AUTH-10) |
| HA-AUTH-03 | **Unlinking the last authentication method** (24 §36 #12; §14.6). Options: NEVER; ALLOWED WITH RECOVERY AUTHORITY (precondition HA-AUTH-02 ≠ DENIED — met by HD-AUTH-10). (ALLOWED AS SELF-DISABLE excluded by HD-AUTH-05.) Full block: `WU-AUTH-13.md`. | 24 §14.6, §36 #12 | Nothing (the default is complete) | NEVER (`409 LAST_METHOD`) | OPEN |
| HA-AUTH-04 | **Who may disable an identity in PRODUCTION / STAGING** | 24 §18, §36 #13; HD-28 | — | HOST_OPERATOR (HD-AUTH-05) | **RESOLVED** by HD-AUTH-05 (2026-10-01): HOST_OPERATOR; no HTTP route, no self-disable, no derived authority; re-enable separate |
| HA-AUTH-05 | **Deployment switch to the scoped authentication principal** (24 §21.18; = PFC HA-10) | 24 §21.18, §25.2; 14 §8; PFC HA-09 / HA-10 | — | SWITCH AUTH ONLY (HD-AUTH-06) | **RESOLVED** by HD-AUTH-06 (2026-10-01): SWITCH AUTH ONLY; compose configured; deployment procedure recorded, not executed |
| HA-AUTH-07 | **Google binding of `tobi` vs stated intent** | 24 §14.2, §18.2; HD-AUTH-08 | — | transition away from `tobi` (HD-AUTH-08 Decision 2) | **RESOLVED** by HD-AUTH-08 and **EXECUTED on production 2026-10-04** (unlink 14:25:01Z, bootstrap 14:28:16Z; `evidence/ha_auth_07_production_transition.txt`) |

Touched and left undecided, not blocking any Work Unit: 24 §36 #9
(provider-verified email as NQUIRY verified email), #10 (session lifetime,
12 h kept), #13 (administrative recovery / re-enable; no command exists),
#16 (production email delivery: the sink is materialized by WU-AUTH-21; the
provider, sender identity and credentials are the operator's facts), #18
(multi-account UX). Resolved by HD-AUTH-09: #1, #2, #6; by HD-AUTH-08: #3–#5;
by HD-AUTH-10: #11; #15 is governed by HARD-DEP-001 Option A (16 §41 REC-001).

## Ledger reconciliation (deferred, disclosed)

20 §14 requires human decisions to be reconciled into 16 §41, the §6 table and
the machine-readable register in the same Work Unit. PURPLE does not do this on
its branch, for two reasons:

1. `REC-nnn` / `NQ-DEC-nnn` numbers are global and are allocated on the RED
   line (last at the pin: REC-032 / NQ-DEC-056). RED continues to allocate
   after the pin. A number chosen here would collide at integration.
2. `tests/regression/test_pfc_ledger.py` (RED's falsifier) pins the register
   to exactly 56 decisions. Adding entries would break a RED test, and editing
   that test is a cross-Field change outside PURPLE's authority.

The decisions above are therefore recorded here with full provenance and are
to be reconciled into 16 when the Field lines are integrated. This is a
disclosed ceiling of every PURPLE Work Unit, not a closed relation.
