# WU-PFC-B0 — Fixture Session identity (HD-24 rules 1–5)

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B0 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (prerequisite) |
| Colour / role / model | RED · domain / persistence / application / API / projection · Claude Opus 5.5 |
| Human authorization | HD-24 / NQ-DEC-052 (2026-09-27): "Choose Option 03 as the current working path for Fixture Sessions … Fixture Session semantics are hereby defined … Continue autonomous SFE execution across all newly derivable RED relations." |
| Derivation | HD-24's Option 03 path needs a Session identity it can bind to. No Fixture concept existed anywhere: not in the domain, schema, Command, event, projection or architecture. |
| Predecessor / baseline | `checkpoint-PFC-F09-3` → `d71ab5a`; HD-24 record `c4fded8`. Live 1859 passed / 2 skipped (with the 3 ledger tests). |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. |
| Authoritative home | HD-24 rules 1–5; 03 TRN-SESS-001 (Session creation); 09 §72 (event schema evolution). |
| Authorized delta | Declare at creation; immutable; no conversion; NON_PROOF status on every Session proof surface. **Not in scope:** the proof path itself (WU-PFC-B1); CYAN. |
| Must remain true | All F02/F03/F04/F08/F09 behaviour; existing Sessions (normal, by default); CMD_CREATE_SESSION authority unchanged. |
| Must remain impossible | Setting the marker after creation; conversion in either direction; a non-boolean declaration; replaying one intent with another declaration; a Fixture Session shown as governed. |

## 2. Execution record

1. **RED.** 13/13 failed for the right reasons (`evidence/b0_regression.txt`).
2. **FBR.** Session identity → proof semantics: the Session had no Fixture fact at any layer.
3. **Home.** HD-24; TRN-SESS-001 (the one creation point).
4. **Repair.**
   - **Migration `d4f7b2c9e6a1`:** `sessions.fixture` NOT NULL DEFAULT false, and trigger `trg_sessions_fixture_immutable` rejects any change for every writer. Also a nullable `session_read_model.fixture`.
   - **Domain:** `Session.fixture` (strict bool).
   - **Persistence:** repository insert and row mapping; directory list.
   - **CMD_CREATE_SESSION:** `CreateSessionPayload.fixture` (part of the fingerprint), `create_session(fixture=…)`.
   - **Event:** SESSION_CREATED contract **1.1** (+ `fixture`); committed 1.0 events stay as they are (09 §72).
   - **API:** `CreateSessionBody.fixture: StrictBool = False` on `POST …/challenges/{c}/sessions`; an absent body means a normal Session.
   - **Surfaces (rule 5):** position `session.fixture` / `proofMode` (`FIXTURE_NON_PROOF` | `GOVERNED`); challenge detail `sessions[].fixture` / `proofMode`; the legacy Session view `session.fixture`; `session_read_model.fixture` (from SESSION_CREATED, kept afterwards).
   - **Tests adapted, assertions unchanged in intent:** the F08-1 schema assertion now compares with each contract's version; the F04 ledger counts exclude later PFC decisions (committed with HD-24).
5. **Propagation.**
   - AFFECTED: the layers above.
   - NOT AFFECTED: authority (the declaration rides on the existing CMD_CREATE_SESSION authority, as HD-24 records), transitions (the marker is only read), F04 analysis (unchanged; B1 consumes the marker), CYAN (additive keys only; CYAN is out of scope).
6. **Local proof.** ruff, mypy (203 files), checks; 31 revisions, single head.
7. **Integration.**
   - Real HTTP → PostgreSQL: create Fixture and normal Sessions; read back through the DB, position, challenge detail and the legacy view.
   - The committed event carries `fixture` under schema 1.1.
   - A real delivery pass puts `fixture = true` in `session_read_model`.
8. **Preservation.** Normal is the default for absent, `{}` and `{"fixture": false}`. The full regression is green.
9. **Regression.** Live 1872 / 2; no-DB 911.
10. **Mutation.** 9/9 KILLED (`evidence/b0_mutation_proof.txt`). The immutability trigger is proven directly against PostgreSQL in both directions.
11. **Inverse.** `proofMode = FIXTURE_NON_PROOF` on any surface ← `sessions.fixture = true` (immutable) ← the CMD_CREATE_SESSION payload of the committed creation (fingerprinted) ← a SESSION_CONTROL_RIGHT holder at CHALLENGE scope ← audit.
12. **Deep sweep.** No new authority. No conversion path: a later Command naming `fixture` is ignored, and the DB refuses the change anyway. Old events stay interpretable.
13. **Inverse deep sweep.** Every `fixture` value traces to exactly one creation Command.

## 3. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B0`). Not REVIEWED_FIELD, not PUBLISHED_FIELD.
