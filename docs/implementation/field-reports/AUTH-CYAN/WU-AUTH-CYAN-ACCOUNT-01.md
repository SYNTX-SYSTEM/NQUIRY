# WORK UNIT REPORT
FIELD: NQUIRY_AUTHENTICATION_FIELD × CYAN (whole-software coherence)
WORK_UNIT: AUTH/CYAN-ACCOUNT-01 — the 24 §24.5 account-security contacts in the product frontend; the PURPLE identity contract (post HD-AUTH-08) consumed; the cross-lineage real proof
DATE: 2026-10-04 · BASE: `origin/frontend-symbiotic` @ `618d7a6` (the FIELD_RECONSTRUCTION_HOLD record) · BRANCH: `auth-cyan-reconstruction` (worktree `worktrees/auth-cyan`; the `frontend-symbiotic` worktree and its uncommitted assembly records were not touched)
AUTHORITY: the human mandate of 2026-10-04 ("implement authentication and authorization for NQUIRY completely, coherently, generically and production-ready across the entire software"; recursive autonomy; stop only at a genuine boundary). PURPLE producer: `auth-identity` @ `e069fc1` (HD-AUTH-08), live as assembly `auth-e069fc1-20261004T140533Z`; its reconstructed contract: `docs/implementation/field-reports/AUTH/CONSUMER_CONTRACT.md` on that branch (`4c82e0e`).

## Field (before the delta)
| Relation | State at the base |
|---|---|
| PURPLE identity contract → CYAN | **HOLD**: CYAN waited for "PURPLE's reconstructed production Field, provider-bootstrap behaviour, identity presentation contract and real runtime proof" (`HA-AUTH-CYAN.md` HOLD) |
| CYAN expectation "LOCAL identity = GOOGLE identity" | stated as a law in the F3/F4 titles, the `authClient.ts` comment ("method-independent") and the review guide's CASE GOOGLE — true only for a LINKED subject |
| 24 §24.5 contacts (list methods · add provider · remove method · revoke sessions · sign out everywhere) | typed clients existed (AUTH/CYAN-01); **no surface** ("ACCOUNT MANAGEMENT = NOT MATERIALIZED") |
| provider contact of the Access Field | Google only, by a hard-coded provider id in the derivation (`googleLoginStart`) |
| real E2E of the current CYAN against the current PURPLE | **NOT PROVEN** (no local AUTH stack reachable from the CYAN lanes) |
| identity organisms (rail panel, "Identity and access" chamber), `?auth=` boundary, mount, typed contracts | proven, preserved |

## Delta (CYAN only; no PURPLE change, no production change)
| File | Change |
|---|---|
| `apps/web/lib/field/accountSecurity.ts` (new) | pure derivation from the SAME `IdentityReads`: ACTIVE methods (words from the server label, provider account, `current` = the one ACTIVE method of the current session's type, `removable` = another ACTIVE method remains — 24 §14.6 mirrored as an affordance, never decided), sessions (words of the producing method), link offers (every parsed provider not carried by an ACTIVE method, joined on `providerId`; none without a current methods read; none for an unsafe return target) |
| `apps/web/lib/field/accountEffects.ts` (new) | `removeMethod` / `endSession` / `signOutEverywhere` as keyless Settlements for the page's one effect field: committed with the server's facts, denied / rejected with the verbatim reason, lost response = `network_failure`, unrecognized = `indeterminate` |
| `apps/web/lib/field/linkBoundary.ts`, `useLinkBoundary.ts` (new) | the `?link=` result from the closed vocabulary (ok = committed, every other word a non-effect; unknown → nothing), same discipline as the `?auth=` boundary |
| `apps/web/lib/field/useIdentityProjection.ts` | returns `{ projection, reads, reload }`; the four reads unchanged and still the ONE source of both identity organisms and the chamber; `reload` = the canonical re-read after an effect |
| `apps/web/components/field/AccountSecurity.tsx` (new) | the "Access security" action chamber: Sign-in methods (Remove while another remains; last-method note; the link offer as a browser-submitted POST form to the typed LINK start with `next=/workspaces`), Sessions (End for every session but the current one, which Log out ends; Sign out everywhere), the `?link=` result (status / alert) |
| `apps/web/app/workspaces/page.tsx` | hosts the chamber after "Identity and access"; wires the three effects through `useEffectField` (`account-security:` relations; re-read via `reload`; leaves for `/login` only on a committed session end); `?link=` from the page-owned return target |
| `apps/web/lib/field/providerContact.ts`, `components/field/ProviderContact.tsx` | **generalized**: one contact per PARSED provider via `loginStartUrl` (no provider id known, none preferred); a non-production class still named "test provider" |
| `apps/web/lib/api/authClient.ts` | producer pin → `e069fc1` / `auth-e069fc1-20261004T140533Z`; the identity-presentation comment states the contract (a function of `userId`; LINKED vs BOOTSTRAP is PURPLE's resolution) |
| `apps/web/lib/field/identityProjection.ts` | header: the stale "display name NOT_MATERIALIZED" replaced by the contract statement |
| `apps/web/app/globals.css` | `.account-*` (chamber, list, items, link form, sign-out row; phone layout) |
| `apps/web/tests/real-stack/identities.ts` | `REAL_STACK_REPO_ROOT` override: provisioning speaks the schema of the checkout that serves the API |
| `scripts/run_auth_cyan_real_lane.sh` (new) | the cross-lineage real lane: PURPLE API from `PURPLE_ROOT` (:18461, TEST, test issuer, SELF_REGISTRATION_ALLOWED, auth_runtime) + this web (:13480) + the real database; refuses proof databases; process-group cleanup |
| tests | `tests/field/accountSecurity.test.tsx` (+24: A1–A6 derivation, L1–L4 link offer, B1–B3 `?link=`, C1–C7 markup incl. GOOGLE_BOOTSTRAP, E1–E4 effects), `tests/e2e/cy09-account-security.spec.ts` (+12 × desktop + Pixel 7), `tests/real-stack/cy09-account-security.real.spec.ts` (+3 × 2 devices), `tests/field/providerContact.test.tsx` (generalization: another provider is a contact; `loginStartUrl` per parsed provider), `tests/field/identityProjection.test.tsx` and `tests/e2e/cy08-identity.spec.ts` (F2/F3/F4 named as the GOOGLE_LINKED case; CASE 1's "no Google anywhere" scoped to the identity organisms — the held-methods list is a different relation), `tests/lib/authClient.test.ts` (pin), `playwright.sf01.config.ts` (cy09 on the phone project) |

## The three cases (PURPLE CONSUMER_CONTRACT.md §1) as the product shows them
| Case | Rail / chamber | Access security |
|---|---|---|
| LOCAL | name · canonical email · "Local password" | one method (not removable) · "Add <provider>" · this session |
| PROVIDER_LINKED | the SAME name, email and userId · "<Provider>" · the provider account beneath it | two methods, both removable, the current one marked · no offer |
| PROVIDER_BOOTSTRAP | ITS OWN name (the provider's display-name claim, copied once) · its own canonical email · "<Provider>" | one provider method (not removable) · no offer · no Workspace (founding stays possible; nothing was granted) |

## Proof
| Lane | Result |
|---|---|
| `npx vitest run` (whole unit suite) | **672 / 672** (648 at the base + 24) |
| `npx tsc --noEmit -p .` · `npx eslint .` | clean (the one pre-existing warning) |
| mocked browser lane `cy09-account-security` (desktop + Pixel 7, isolated :3301, dead proxy) | **24 / 24** |
| preservation lanes: `cy08-identity` (40), `cy06-provider` + `cy07-auth-boundary` + `auth.spec` (58), `workspaces`, `sf04-field`, `sf05-field` (170 in the combined run), `mount-review` on its own lane (8) | **all passed** |
| **cross-lineage REAL lane** `scripts/run_auth_cyan_real_lane.sh` — this web against the real PURPLE API (`auth-identity` @ `4c82e0e`, head `d2f4a6b8c1e3`), real PostgreSQL `nquiry_purple_real`, real Chromium, no mocking: LOCAL → LINK (form POST → the API's consent page → cross-site callback → `?link=ok`) → PROVIDER_LINKED (same userId, name, email) → UNLINK of the current method (server ends the session → `/login`) · SESSIONS (a second browser's session listed, End signs that browser out, Sign out everywhere) · PROVIDER_BOOTSTRAP (own identity, name "Test Subject" from the claim, email from the claim, one method, no Workspace, binding persists across logins) | **6 / 6** (3 × desktop, 3 × Pixel 7); re-run through the runner 3 / 3 |
| visual check (screenshots desktop + Pixel 7 of the chamber) | layout coherent with the chamber grammar; no sideways scroll |

Mutation step: guard-necessity falsifiers only (every control, offer and note has a test that fails when its guard is removed: A2/C2 last method, L2/L3 offer, C5 failed reads, E3 lost response, S3/S6 session end); no source-mutation script was written (same disclosure as the AUTH Field).

## Laws preserved / established
AUTHENTICATION != AUTHORIZATION (the chamber names no role, right or capability; falsifier C7, S1) · IDENTITY != METHOD (the identity organisms unchanged; the method list is a different relation) · CURRENT METHOD != ANY LINKED METHOD (still in both organisms; the linked method appears only in the held-methods list) · LINK != LOGIN != ACCOUNT_CREATION (link is the authenticated form POST; bootstrap is the provider path; no registration UI) · SERVER DECIDES (Remove withheld only on the server's own count; a refusal is the server's reason; the page leaves only on a committed session end) · NETWORK FAILURE != PROOF OF NO EFFECT · NO PROVIDER LITERAL (the login contact and the offer come from the parsed list only; production never lists a test issuer).

## Status
AUTH/CYAN-ACCOUNT-01: **TECHNICALLY CLOSED — LOCAL_GREEN + CROSS-LINEAGE REAL PROOF GREEN.** Claim ceiling: 24 §24.5 ACCOUNT SECURITY = MATERIALIZED IN THE PRODUCT FRONTEND (list methods · add provider · remove method · revoke sessions · sign out everywhere) · PURPLE CONTRACT (post HD-AUTH-08) = CONSUMED · REAL PURPLE E2E WITH CURRENT CYAN = PROVEN (test issuer) · REAL GOOGLE E2E WITH CURRENT CYAN = NOT YET PROVEN (needs the staged mount and the human's Google account) · HUMAN FRONTEND ACCEPTANCE = PENDING · PRODUCTION ROOT CUTOVER = NOT AUTHORIZED. Not materialized, by the producer's state: recovery and e-mail verification contacts (both `unavailable` in production: HA-AUTH-02 DENIED, 24 §36 #16).

## Next boundary
Human Frontend Acceptance of this chamber and of the identity field on the staged mount (`/cy-review/`, rebuilt from this branch), then CYAN_PRODUCTION_ROOT_CUTOVER — both human acts.
