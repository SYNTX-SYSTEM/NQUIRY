# FIELD REPORT — GENERIC PROVIDER-DRIVEN IDENTITY (PROVIDER_BOOTSTRAP)

FIELD: AUTHENTICATION_IDENTITY_RESOLUTION — VERIFIED EXTERNAL PROVIDER IDENTITY → NQUIRY IDENTITY
WORK_UNIT: PROVIDER_BOOTSTRAP_01 (source Field; production policy unchanged)

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §11.14 (first provider login / account creation boundary — the generic bootstrap sequence is defined there as `SELF_REGISTRATION_ALLOWED`), §13.3, §13.10 (identity equivalence), §14.2 (link), §14.5 (collision), §14.7 (provider attribute change), §18.2 (unlink), §20.3 (no governance bootstrap), §36 #3–#5, #9, #15; HD-28; HA-AUTH-01 (DENIED); HA-AUTH-07 |
| PREDECESSOR | PURPLE_IDENTITY_PRESENTATION_01 `2ec05c0`; live production at that lineage (+ HA-AUTH-07 recorded `af9916d`) |
| PROOF_RADIUS | RED (14 generic falsifiers) → delta → GREEN → directly affected suites (WU-09/13/15/16, identity presentation: 114) → broader affected radius: security, regression, sweep, WU-07/08/09/10/13/15/16, identity presentation, HD-28: **649 passed, 1 skipped**; migration `d2f4a6b8c1e3` round-trip PASS (`evidence/provider_bootstrap_01_proof.txt`) |
| HUMAN_AUTHORITY_STATE | HA-AUTH-01 unchanged (DENIED on PRODUCTION / STAGING; the bootstrap policy is refused at startup there); HA-AUTH-07 unchanged (the live binding untouched). Two boundaries returned at the end. |

## SEMANTIC TYPES (reconstructed from schema, code and 24)

| Type | Object | Key | Owner / producer |
|---|---|---|---|
| NQUIRY_IDENTITY | `users` row | `id` | identity creation authority (HD-28 operator; PROVIDER_BOOTSTRAP under policy) |
| NQUIRY_DISPLAY_NAME / NQUIRY_CANONICAL_EMAIL | `users.name`, `users.email` | — | copied at creation by the creation authority; **immutable afterwards** (no mutation path exists; identity mutation would be a new Human Authority relation) |
| LOCAL_CREDENTIAL | `local_auth_credentials` | `user_id` | HD-28 / recovery; carries no identifier (login resolves via `users.email`) |
| AUTHENTICATION_METHOD | `authentication_methods` | `id` | login / link / bootstrap; ACTIVE → REVOKED one-way |
| PROVIDER_IDENTITY | `external_provider_identities` | **(provider_issuer, provider_subject)** — the only resolution key | link / bootstrap; attributes refreshed at every provider login |
| PROVIDER_SUBJECT | binding column | — | the provider (OIDC `sub`: stable, unique per issuer) |
| PROVIDER_EMAIL / PROVIDER_DISPLAY_NAME / verified flag | binding columns | — | the provider (OIDC `email`, `email_verified`, `name`); attributes, never keys |
| LOGIN_TRANSACTION / LINK_TRANSACTION | `oidc_auth_transactions` purpose | — | start contacts; a link transaction binds its initiating identity |
| SESSION / AUTHENTICATED_PRINCIPAL | `local_auth_sessions` → `AuthenticatedPrincipal(userId, session ref, time, issuer)` | — | `issue_session` / `rotate_session`; no authority |
| PROVENANCE | `security_events` IDENTITY_CREATED / AUTH_METHOD_LINKED / UNLINKED, `*.provenance_ref` | — | the effect that created the relation |

Equal strings across these types are never an identity relation (24 §13.10).

## IDENTITY RESOLUTION (generic, provider-independent)

```
VERIFIED PROVIDER CREDENTIAL {issuer, subject, email, email_verified, display_name}
  (after transaction / binding cookie / state / claim / PKCE / signature / audience / expiry / issuer / nonce)
→ lookup ACTIVE binding by (issuer, subject)                       ← the one authoritative key
  ├─ found, method ACTIVE, identity not disabled → that identity; binding attributes refreshed; fresh session
  ├─ found, method REVOKED → AUTHENTICATION_METHOD_REVOKED (failed)
  ├─ found, identity disabled → ACCOUNT_DISABLED (failed)
  └─ none (never bound, or unlinked) → ACCOUNT CREATION POLICY
       ├─ SELF_REGISTRATION_ALLOWED (= PROVIDER_BOOTSTRAP class)  → bootstrap (below)
       ├─ DENIED, subject previously bound → AUTHENTICATION_METHOD_REVOKED (failed)
       └─ DENIED, subject unknown        → ACCOUNT_CREATION_POLICY_UNRESOLVED (unavailable)
```
Nothing else enters: no session cookie (the login callback receives none), no previous identity, no email or name equality, no frontend state.

## PROVIDER_BOOTSTRAP relation (24 §11.14, validated, refined)

```
unbound subject + policy admits
→ email claim present AND email_verified          else PROVIDER_EMAIL_MISSING / PROVIDER_EMAIL_UNVERIFIED (unavailable)
→ display-name claim present (non-blank)           else PROVIDER_PROFILE_INCOMPLETE (unavailable)   ← new: nothing is invented
→ no identity holds that email                     else EMAIL_COLLISION (unavailable; path = the owner's own LINK)
→ create NQUIRY identity: name := display-name claim verbatim; email := verified claim lower-cased
→ create method (provider type) + binding (subject, email, verified, display name) + IDENTITY_CREATED
  {identityClass PROVIDER_BOOTSTRAP_IDENTITY, nameSource PROVIDER_DISPLAY_NAME_CLAIM,
   emailSource PROVIDER_VERIFIED_EMAIL_CLAIM, previouslyBound, providerIssuer, providerSubjectHash, workspaceAuthority NONE}
→ fresh session attributed to the method; no membership, role, binding or participation.
```
The mandate's sequence is validated by 24 §11.14 and by the code; the refinements are: no name derivation (was: email local-part), provenance of both attributes, and the unlinked-subject rule (was: denied forever) — an unlinked subject is simply unbound again and bootstraps a *new* identity under the policy (`previouslyBound: true`); its former owner keeps its identity and the revoked binding as evidence.

## IDENTITY PRESENTATION and PROVENANCE for a provider-origin identity

- WHY is this person called this? `users.name` = the provider's display-name claim at bootstrap; IDENTITY_CREATED `nameSource`.
- WHERE did this email come from? `users.email` = the provider's verified email claim at bootstrap; `emailSource`.
- WHO may change them? Nobody today (immutable; a profile / identity-mutation relation is not materialized and would be Human Authority).
- WHAT if the provider later changes the display name or email? The binding's attributes are refreshed at the next provider login (24 §14.7, provider truth visible in `/auth/methods`); the NQUIRY identity and `/auth/identity` are unchanged. Equal strings may drift apart; they were never one relation.
- Copied-at-creation, NQUIRY-owned afterwards: chosen over provider-synchronized because a synchronized name would make LOGIN an identity mutation and would let a provider rename a person in every roster; chosen over provider-derived-dynamically because the presentation must be method-invariant (PURPLE_IDENTITY_PRESENTATION_01).

## COLLISION relation (24 §14.5)

provider verified email == an existing identity's canonical email → refused, nothing created, nothing merged. The legitimate transition is the existing identity's own authenticated LINK (then the subject resolves through the binding, and the identity keeps its own name/email). Provider-verified-email equivalence as an automatic merge is excluded (24 §13.10; §36 #9 undecided).

## LINK / LOGIN / BOOTSTRAP / OPERATOR CREATION stay four relations

LINK: an authenticated identity attaches a subject to itself (never creates an identity; binds whichever identity initiates). LOGIN: resolves a bound subject; never links, never changes the identity. BOOTSTRAP: only inside LOGIN of an unbound subject under the policy. OPERATOR CREATION (HD-28): a local identity with operator-entered name/email and a password; no provider involved.

## CURRENT UNINTENDED BINDING (evidence, not target)

Subject `689df8a6…` → identity `7dd6e767` ("tobi") is a legitimate LINK made by that identity's own session on 2026-10-03 (HA-AUTH-07). Under this generic architecture the intended outcome ("the Google account is its own NQUIRY identity") is: the owner unlinks (allowed by existing law), then — only if production policy admits provider bootstrap (HA-AUTH-01) — the next Google login bootstraps a new identity named from the provider claims. Nothing was mutated in this unit.

## DELTA

| File | Change |
|---|---|
| `packages/security/account_creation.py` | provenance vocabulary: `IDENTITY_CLASS_PROVIDER_BOOTSTRAP`, `NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM`, `EMAIL_SOURCE_PROVIDER_VERIFIED_CLAIM` |
| `packages/security/oidc_transaction.py`, `persistence/tables.py`, migration `d2f4a6b8c1e3` | failure class `PROVIDER_PROFILE_INCOMPLETE` (CHECK extended; reversible) |
| `packages/application/oidc_identity.py` | `_bootstrap_identity`: display name required (no derivation), provenance facts, `previouslyBound`; resolver: unbound subject → policy first; unlinked subject denied only under DENIED |
| `packages/application/http_oidc.py` | `PROVIDER_PROFILE_INCOMPLETE` projects `unavailable` |
| `packages/security/oidc_test_issuer.py` | the test provider emits a `name` claim (`display_name`, default "Test Subject"; None simulates a profile without one) |
| `tests/e2e/test_auth_provider_bootstrap.py` | 14 generic falsifiers |

Policy vocabulary unchanged (`AccountCreationPolicy` is 24 §11.14's); the bootstrap class is named in provenance, not by renaming the policy.

## SEMANTIC FALSIFIERS (all green)

NEW subject → own identity with provider-claim attributes, provenance, no authority, session attributed · KNOWN subject → stable identity, nothing created · no display name → `PROVIDER_PROFILE_INCOMPLETE`, nothing named (unit + HTTP `unavailable`) · absent / unverified email → refused · EMAIL COLLISION → refused, then the owner's LINK makes the subject resolve to the owner with the owner's own name · unbound subject with a local session A active in the browser → new identity B, A untouched (CASE C/G) · unlinked subject → new identity under the policy (`previouslyBound: true`), former owner intact, old binding revoked; under DENIED → `AUTHENTICATION_METHOD_REVOKED`, unknown → `unavailable` · attribute drift → binding refreshed, identity and presentation unchanged · LINK ≠ BOOTSTRAP ≠ LOGIN (user count and method count) · bootstrap policy refused at startup on PRODUCTION / STAGING.

## MUTATIONS killed (guard-necessity; no source-mutation script, as disclosed for the whole Field)

resolve from last local user / previous session (callback has no session input; CASE C test) · resolve from provider email or display name (lookup by subject; collision test; drift test) · silent same-email merge (collision test) · authority / membership with identity (authority counts; WU-16) · bootstrap without provenance (facts asserted) · LINK→BOOTSTRAP and BOOTSTRAP→LINK collapse (three-relations test; purpose binding WU-10) · unverified email → canonical (refusal test) · reuse of a revoked binding (unlink tests WU-13; new identity test) · CYAN-state identity (no such input exists) · name from local-part (removed; nameless test).

## HUMAN AUTHORITY (returned, not crossed)

- **HA-AUTH-01 (refined by this Field):** whether PRODUCTION / STAGING admit the PROVIDER_BOOTSTRAP class (24 §11.14 `SELF_REGISTRATION_ALLOWED`) for a production-enabled provider (today only Google, §36 #1/#6). Mechanism now generic and proven in TEST; the runtime refuses it outside DEVELOPMENT / TEST until decided. Options unchanged from the WU-09 block; what this Field adds is the exact semantics an approval would enable (no invention, provenance, collision refusal, re-bootstrap after unlink).
- **HA-AUTH-07:** the live binding of `tobi` — unlink by the owner is the first step of the human's intent; the second step (a new identity for the Google account via bootstrap) depends on HA-AUTH-01, or on HD-28 operator creation + link.

## CLAIM CEILING

Source: PROVIDER_BOOTSTRAP generic relation MATERIALIZED and proven in TEST; production policy DENIED (unchanged); live binding unchanged. The incident's two causes are now separated: (1) the link bound the Google account to the initiating identity by design (HA-AUTH-07), (2) production could not have bootstrapped it anyway (HA-AUTH-01).
