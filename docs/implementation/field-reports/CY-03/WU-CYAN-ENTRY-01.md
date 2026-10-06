# WORK UNIT REPORT
FIELD: CYAN × NQUIRY Identity / Authentication Field — the entry path of a person without an nquiry identity
WORK_UNIT: CYAN-ENTRY-01 — the complete legitimate entry path projected on the production login surface
DATE: 2026-10-06 · BASE: `frontend-symbiotic` `3fc1b45` (over `checkpoint-CYAN-INTEGRATION-02b` `9f950c4`; production web `7d214e6` is an ancestor)
AUTHORITY: the human mandate of 2026-10-06 ("the production frontend must project the complete legitimate entry path by which a person without an existing NQUIRY identity can enter the Identity Field … materialize every frontend relation already supported by authoritative system state … do not invent identity semantics, registration policy … where a projection depends on an unresolved producer relation, preserve that dependency explicitly and stop only that relation"). Producer: PURPLE `origin/auth-identity` `06eff01` (closure #4, HD-AUTH-10/11/12), `CONSUMER_CONTRACT.md`, Architecture 24 §11.14, §14.5, §24.2, §24.6, §32; `identity_provisioning.py` (HD-28).

## Field reconstruction (before the delta)
| Relation (authoritative) | Producer state | Projected on the production login before |
|---|---|---|
| **Provider entry** — an unbound provider subject becomes its own identity under `SELF_REGISTRATION_ALLOWED` (24 §11.14; contract §1 GOOGLE_BOOTSTRAP: name = provider display name, e-mail = provider verified e-mail; §4 "bootstrap is the provider path, not a form") | production policy `SELF_REGISTRATION_ALLOWED` (`NQUIRY_ENVIRONMENT=PRODUCTION`; HD-AUTH-08 admitted the generic bootstrap in production; proven live 2026-10-04) | the contact "Continue with Google" existed (AUTH/CYAN-02) but **nothing said that it is the entry for a person without an identity, nor what it creates** |
| **Policy discovery** — whether THIS deployment admits a new identity | **NOT discoverable**: `/auth/providers` carries `providerId, label, proofClass`; `/auth/contacts` carries `recovery, emailVerification`; the policy is decided at the callback and refused as the class `unavailable` (`ACCOUNT_CREATION_POLICY_UNRESOLVED`, `EMAIL_COLLISION`, `PROVIDER_PROFILE_INCOMPLETE` → one enumeration-safe word) | n/a |
| **Operator entry** — a local password account is created only by the host operator's command (HD-28; no HTTP route; 24 §3.7 "no self-service registration") | authoritative, unchanged | stated only on `/recover` ("Ask the operator who created your account") |
| **LINK != LOGIN** — a provider joins an existing identity only from that identity's live session (`link/start`; contract §1 GOOGLE_LINKED); 24 §14.5 same e-mail is never an automatic link; §32 "email collision → boundary requiring link/recovery flow" | authoritative | the Access security chamber offers "Add Google" once logged in; **the login said nothing**, so a person with a local account who "continues with Google" is bootstrapped or refused, never linked, without being told |
| **Refusal words** (`?auth=unavailable` …) | authoritative, closed vocabulary | projected (AUTH/CYAN-03) |
| **After entry** — identity grants no authority; Workspace founding is open to every identity (`workspace_creation_handler`: ungated self-service); membership is added by a root by `userId` only | authoritative | projected (login lede; "Found a Workspace" chamber) |
| Recovery / verification contacts | `/auth/contacts` AVAILABLE / AVAILABLE on production since HD-AUTH-12 | projected (RECOVERY-01; "Forgot your password?" live) — not an entry |
| Invitation / pre-provisioned / governance-mediated creation (24 §11.14 other policies) | **not materialized** by the producer ("refused until their relations exist") | nothing to project; not invented |
First broken relation: the login surface offered the provider contact without projecting the entry relation it carries
(what a person without an identity may expect from it, that the server decides admission, that a local account comes
from the operator, and that continuing with a provider never links).

## Delta (CYAN only; no producer change)
| File | Change |
|---|---|
| `apps/web/lib/field/entryPath.ts` (new) | pure `entryPathFrom(contact)` → `{ providers (the parsed list only), operator: "HOST_OPERATOR" }`; `providerWords` joins the server's labels |
| `apps/web/components/field/EntryPath.tsx` (new) | `<section data-testid="access-entry" data-providers=n>` inside the Access core below the contacts: eyebrow "Without an nquiry identity"; with a listed provider: "Continue with <labels>: a provider account this deployment admits becomes your own nquiry identity, named and addressed as the provider presents you. Whether this deployment admits a new identity is decided by the server when you continue; a refusal is shown here, and no identity is created."; always: "A local password account is created by the operator of this deployment. There is no registration form."; with a provider: "Already have an nquiry account with a password? Log in with it and add <labels> under Access security. Continuing with a provider here does not attach it to an existing account." Words only: no control, link or form |
| `apps/web/app/login/page.tsx` | `<EntryPath entry={entryPathFrom(providerContact)} />` after the recovery contact, before the boundary — the SAME parsed contact that renders the provider button |
| `apps/web/app/globals.css` | `.access-entry` (rule, spacing) |
| `apps/web/tests/field/entryPath.test.tsx` (new, 8), `tests/e2e/cy12-entry.spec.ts` (new, 5 × 2 devices), `scripts/entry01-mutation-proof.mjs` (new, 6), `playwright.sf01.config.ts` (mobile regex `cy1[012]`) | falsifiers below |

## Dependency preserved explicitly (the one relation stopped)
**"This deployment admits new identities from <provider>" is not projected.** It depends on a producer relation that does
not exist: a discovery contact for the account-creation policy (e.g. a field on `/auth/contacts`). The frontend keeps the
sentence conditional ("a provider account this deployment admits …; decided by the server when you continue") and lets
the server's `unavailable` word carry every refusal class. PRODUCER_RELATION_UNRESOLVED → PURPLE authority; nothing was
invented to compensate. Likewise not projected: invitation, pre-provisioned or governance-mediated creation (24 §11.14
policies the producer has not materialized).

## Laws
NO PROVIDER NAMED BY THE FRONTEND (labels from `/auth/providers` only; M1, M6, unit E3) · NO REGISTRATION CONTROL (contract §4, 24 §24.2; M2, unit E2, cy12) · NO POLICY CLAIM (M3) · OPERATOR ENTRY ALWAYS STATED (M4) · LINK != LOGIN (M5) · IDENTITY != AUTHORITY (no success / authority / role words; unit E2) · UNAVAILABLE stays one enumeration-safe class (cy12: the refusal sentence unchanged; AUTH/CYAN-03 untouched).

## Proof
| Lane | Result |
|---|---|
| Unit falsifiers `tests/field/entryPath.test.tsx` | **8 / 8** |
| Full unit suite | **699 / 699** |
| `tsc --noEmit`, `eslint .` | clean (3 pre-existing warnings) |
| Mutation proof `scripts/entry01-mutation-proof.mjs` | **6 / 6 killed**, byte-identical restore |
| Browser: `cy12-entry` + preservation `cy06`, `cy07`, `cy11`, `auth`, `cy08`, `sf05` (desktop + Pixel 7) | **152 passed, 6 skipped by design, 0 failed** (4.1 min; STAGE_END rc=0) |
| Mount lane | **8 / 8** |
| Observed under SFE-PEO/1 (`sfe_observe.sh` from ORANGE `194adf4`, by reference) | events in the session scratchpad |

## Propagation through the actual production projection
| Step | Result |
|---|---|
| Field commit | `b5297a0` = tag `checkpoint-CYAN-ENTRY-01` on `frontend-symbiotic` (pushed) |
| Local review runtime `127.0.0.1:13500` | refreshed; the entry section renders from the proxy's provider fixture on desktop and Pixel 7 (`browser-evidence/entry-01/screenshots/entry-*.png`) |
| **Production projection candidate** | `frontend-symbiotic` carries PCPG-06 and RAIL-01 without human acceptance, so the mandated delta was projected onto production ALONE: production web `7d214e6` + `b5297a0` cherry-picked = **`8af287d`** (tree `73b5c3c`), local branch `cyan-production-projection` (not pushed). Proof on it: units 686 / 686, tsc / eslint clean, lanes `cy12` + `cy06` + `cy07` + `cy11` + `auth` + `cy08` + `cy09-account-security` + `cy10-roster-admin` + `sf05` **194 passed, 6 skipped by design, 0 failed**, mount lane **8 / 8**, mutations **6 / 6** — under SFE-PEO/1 observation |
| **Staged on the production origin** | `/cy-review/` rebuilt from `8af287d` (assembly `cyreview-8af287d-20261006T162821Z`, 2026-10-06T16:34:22Z; compose context line only; live `/` and `/login` hashes identical before and after, `c898a6eb…` / `8e72270b…`; vhost `14053fb3…` and `.env` unchanged; root web container `113105ae…` untouched). Served stylesheet carries `.access-entry`. |
| **Proven through the actual production projection** (headless, desktop 1280 + Pixel 7, no login, real production API) | the entry section inside the core below the contacts: `data-providers=1` from the REAL provider list ("Continue with Google: a provider account this deployment admits …"), the operator sentence, the LINK != LOGIN sentence; 0 controls in the section; provider href `…/api/auth/oidc/google/start?next=%2Fcy-review%2F`; the recovery contact `/cy-review/recover` (contacts AVAILABLE since HD-AUTH-12); `?auth=unavailable` → the unchanged refusal sentence with the entry present; requests only `GET /api/auth/providers`, `GET /api/auth/contacts`; zero `/cy-review/api/`; zero cookies; `scrollX` 0 — `browser-evidence/entry-01/screenshots/origin-cy-review-entry-*.png` |
| **Production root cutover** | **PREPARED, NOT EXECUTED** (a human-authorized act, as every root cutover before): session scratchpad `deploy/entry01/web-entry01.tar.gz` (archive of `8af287d` `apps/web`) + `cutover-entry01.sh` (guards on the recorded predecessors: compose `d8c32604…`, `.env` `708acb91…`, vhost `14053fb3…`, web container `113105ae…`, api `913528e8…`; baseline `_baseline-pre-ENTRY01-<ts>` with anchor image and preservation snapshots; web context switch only; build; switch; state after; `ROLLBACK-entry01.sh`). Human-run: `scp` both to `/opt/nquiry/assembly/`, then `bash cutover-entry01.sh`. |

## Status
CYAN-ENTRY-01: **TECHNICALLY CLOSED on both lineages; STAGED on the production origin; READY_FOR_HUMAN_FRONTEND_REVIEW.**
Not live on the root until the human-authorized cutover. The one stopped relation (policy discovery) stays with PURPLE.

## Boundary — HUMAN_AUTHORITY_REQUIRED
1. Human Frontend Acceptance of the entry path on `https://nquiry.condyn.eu/cy-review/login` (and of RECOVERY-01's live states there, now AVAILABLE).
2. Root cutover of the production projection candidate `8af287d` (prepared; web only), or of the whole CYAN lineage `b5297a0` once PCPG-06 and RAIL-01 are accepted (those remain reviewable on `127.0.0.1:13500` / a later staging).
3. PURPLE: a discovery contact for the account-creation policy (PRODUCER_RELATION_UNRESOLVED) if the product is to state that a deployment admits new identities; until then the conditional projection stands.
4. Housekeeping unchanged: erroneous tag `checkpoint-CYAN-INTEGRATION-02`; `auth-cyan-reconstruction` (now `572e2fd`) and `cyan-production-projection` publication; `nquiry-cy01-candidate` stack.
