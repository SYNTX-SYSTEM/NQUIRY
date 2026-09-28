# WU-PFC-AC1 — Production account creation by the host operator (HD-28)

**Execution invariant:** Architecture 25 §23. **Field:** PRODUCTION_ACCOUNT_CREATION (NQUIRY PRODUCTION ACCOUNT CREATION FIELD, human operator, 2026-09-28).

## 1. Header

| Item | Value |
|---|---|
| Work Unit | WU-PFC-AC1 · RED · application / operator tooling · Claude Opus 5.5 |
| Human authorization | The field authorization of 2026-09-28, plus HD-28 / NQ-DEC-056 (Option A: explicit host-operator command, operator recorded as `otti@condyn.eu`; credential only at creation; no reset). |
| First Broken Relation | Live materialization report §14: PRODUCTION AUTHORITY → legitimate account-creation relation → persisted identity → credential issuance → audit provenance. At B5 only `/auth/login`, `/auth/logout` and `/auth/me` exist, and the only provisioning path is dev-only (HD-3). A second defect was also found: the dev guard accepts DB host `postgres` (the live compose host) and ignores the environment. |
| Predecessor / baseline | `checkpoint-PFC-B5` → `7d3f74e` (the live RED producer); records `3300024`, `6921bf5` (HD-27), `bb1931a` (HD-28). Live 1981 / 2; no-DB 918. |
| Authoritative home | 24 §1 / §11.14 (account creation policy is HUMAN_AUTHORITY_REQUIRED; no Workspace authority with an identity); 04 §17 (default deny, no implicit administrator); 11 §47 (privileged infrastructure operation: attributable administrative identity plus SecurityEvent), TB-17 (Administrative Tooling: "privileged-operation security event", "no canonical bypass"), AC-11-017 (environments); 18 (local credential, PBKDF2); F02 HD-3; HD-6 (no own commit boundaries in application modules); HD-28. |
| Authorized delta | The application service, the identity repository, the host-operator command in the api image, and the environment guard on the dev path. **Not in scope:** any HTTP route; password reset or change; external providers (GAP-14-001); membership, roles, bindings, participation or Sessions; CYAN; migrations. |
| Must become true | Under `NQUIRY_ENVIRONMENT=PRODUCTION`, the explicitly named host operator creates one identity through the canonical path. The identity has a unique, case-normalized email, a PBKDF2 credential and an attributed SecurityEvent. It logs in normally and has no authority of any kind. |
| Must remain impossible | Creation over HTTP (public, self-service, admin or Workspace-owner); a password in argv, output, logs or records; a plaintext credential; a duplicate (case-insensitive); an undeclared or spoofed environment (`production`, `PROD`); dev provisioning under PRODUCTION or STAGING; a partial write; any change to existing identities. |
| Falsifiers | `tests/e2e/test_pfc_ac1_production_account_creation.py` (24 cases); `tests/security/test_dev_identity_provisioning.py` (unchanged, still green). |

## 2. Execution record

1. **RED.** 23 of 24 failed for the right reasons: no `nquiry_api.operator` ×20; the dev guard has no environment parameter ×3. The pre-passing case pins "no identity-creating route" (a preservation fact of Option A).
2. **FBR.** No production-safe identity creation relation exists. The dev guard's host check cannot tell development from the live compose deployment.
3. **Home.** HD-28, attributed and recorded under 11 §47 / TB-17.
4. **Repair.**
   - **`packages/application/identity_provisioning.py`.**
     - Environment: `declared_environment` requires one of AC-11-017's exact values; there is no default and no normalization.
     - Input: the operator is required; the email is normalized (strip, lower) and shape-checked; the name is required; the password is 12..1024 characters with no surrounding whitespace (login strips it).
     - Duplicates are refused case-insensitively (`IDENTITY_ALREADY_EXISTS`).
     - One transaction writes three things:
       1. `users`;
       2. `local_auth_credentials`, via `security.local_auth.hash_password` (PBKDF2-HMAC-SHA256, 600 000 iterations, random salt);
       3. a SecurityEvent: `IDENTITY_CREATED`, actor HOST_OPERATOR / the operator, TB-17, the declared environment, target `user:<id>`. Its facts are non-secret: authority "HD-28 HOST_OPERATOR", `workspaceAuthority` NONE, OS user and host.
     - No own savepoint (HD-6).
   - **`packages/persistence/identity_repository.py`.** A case-insensitive existence check and the identity insert.
   - **`apps/api/src/nquiry_api/operator/create_identity.py`.**
     - Run as `python -m nquiry_api.operator.create_identity --email … --name … --operator …`, inside the api container.
     - The password comes from stdin (or a no-echo prompt entered twice on a TTY) and is never an argument.
     - It prints one JSON line without the password. Exit codes: 0 created, 3 refused (reason code only), 2 usage error.
   - **`packages/test_support/dev_identity.py` and `scripts/dev_provision_local_identity.py`.** The dev path refuses any `NQUIRY_ENVIRONMENT` other than unset, DEVELOPMENT or TEST.
5. **Propagation.**
   - **AFFECTED:** the dev provisioning guard (narrowed); the api image (+1 module).
   - **NOT AFFECTED:**
     - login, logout and me (unchanged; the created identity uses them as-is);
     - every route (none added);
     - the schema;
     - web and CYAN;
     - B0–B5 semantics.
6. **Local proof.** ruff; mypy (220 files); the architecture, SDK and test-only import checks (the `nquiry_api` layer imports `application` only).
7. **Integration.**
   - **Falsifiers:** real PostgreSQL and the real FastAPI login.
   - **Production candidate and live:** see the live materialization report.
8. **Preservation.** Existing identities and credentials are byte-identical after a creation (falsifier). Workspace memberships are unchanged. HD-3 is narrowed, not widened.
9. **Regression.** Live 2005 / 2; no-DB 921 (`evidence/ac1_regression.txt`). The first full run found the HD-6 violation, repaired at its root (see there).
10. **Mutation.** **13/13 KILLED** (`evidence/ac1_mutation_proof.txt`). The mutations cover:
    - the dev guard;
    - environment spoofing and the undeclared-environment default;
    - duplicate refusal and email normalization;
    - plaintext storage and a password leak into the record;
    - operator attribution and the trust boundary;
    - the whitespace, length and operator rules;
    - a password argument on the command line.
11. **Inverse.** `users.id` traces back as follows:
    - `security_events.target_ref = user:<id>`;
    - that event names IDENTITY_CREATED by HOST_OPERATOR `otti@condyn.eu` at TB-17, in the declared environment, with OS user and host;
    - the authority is HD-28 / NQ-DEC-056.
    - No membership, role, binding or participation references the new identity until the governed product creates one.
12. **Deep sweep.**
    - **Enumeration:** refusals print reason codes only; login keeps its uniform `InvalidCredentials`.
    - **Secrets:** the password goes stdin → hash only.
    - **Scope:** no route and no reset.
13. **Inverse deep sweep.** Every identity created after AC1 on production has exactly one IDENTITY_CREATED SecurityEvent.

**Case 2 choices (recorded):**
- **Provenance record:** a SecurityEvent (11 §41/§47, TB-17), not `audit_events`. Audit rows are Workspace- and CommitUnit-bound; an identity has neither.
- **Email:** stored lower-case, with case-insensitive uniqueness (login already lower-cases).
- **Password bounds:** 12 characters minimum (the dev path's rule) and 1024 maximum.

## 3. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-AC1`). Deployment and live proof: `NQUIRY_LIVE_MATERIALIZATION_REPORT_2026-09-28.md` (CYAN-side, untracked). Not REVIEWED_FIELD, not PUBLISHED_FIELD.
