# WU-PFC-B3 — The QuestionSelection product path (TRN-SEL-001/002)

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B3 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (19 §25) |
| Colour / role / model | RED · application / API / projection · Claude Opus 5.5 |
| Human authorization | The standing autonomous authorization (2026-09-26), plus HD-25: "Derive all newly eligible RED Work Units". |
| Derivation | Field report §8. With a Session in QUESTION_SELECTION (B2), the next relation is the human selection. The governed Command exists but has no product path. |
| Predecessor / baseline | `checkpoint-PFC-B2` → `10d4517`; record `4c1eab9`. Live 1910 / 2; no-DB 914 (+1 ledger pin → 915). |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. Runtime: `nquiry_pfc_int_runtime` @ `d4f7b2c9e6a1`, API :18433. |
| Authoritative home | 03 §39 TRN-SEL-001/002; 04 AUTH-DEP-SEL-001/002 (QUESTION_SELECTION_RIGHT, "Specific Session", 1–3 compelling); 05 GOV-010, §40; 09 §33, §85; 12 §6, AC-12-004, row 19. |
| Authorized delta | The product entry, routes, read model and capabilities for the existing governed SelectQuestion Command. **Not in scope:** the Command's semantics (`question_selection_handler`, unchanged); replacing or withdrawing a selection (GAP-03-018); collaborative selection (NQ-GAP-026); AI recommendations (HA-07); ImpactChain (HA-22); TRN-SESS-009. |
| Must become true | The one QUESTION_SELECTION_RIGHT holder of a Session in QUESTION_SELECTION records compelling Questions (at most three) and one primary Question over HTTP. Selections are readable, marked with the Session's proof mode, and the Session stays in QUESTION_SELECTION. |
| Must remain true | The governed Command (BND-001..007, BND-014 at `SESSION:<id>`, audit, outbox, DB backstops); HD-24/HD-25; B0–B2; F02–F04, F08, F09. |
| Must remain impossible | Selection without QUESTION_SELECTION_RIGHT (including by the Session controller); selection while more than one active holder exists (AC-12-004; there is no conflict policy); a second primary (GAP-03-018); a fourth compelling Question (04 §41); the same selection twice; selection outside QUESTION_SELECTION; a Question of another Workspace; a SYSTEM_SERVICE actor selecting; a decision taken without the Session row lock; a stale view committing; one intent committing twice. |
| Falsifiers | `tests/e2e/test_pfc_b3_question_selection.py` (15 cases). |

## 2. Execution record

1. **RED.** 15 of 15 cases failed for the right reasons: no route (404, including envelope KeyErrors), no `SELECT_*` capability, and no `application.selection_command`. Two falsifier corrections were made **before** the repair:
   - The F04 fixture captures only three Questions, so the cap case needs a fourth; `_reach` now captures four.
   - A SYSTEM_SERVICE actor is denied at the F09-2 precheck (BND-001, `SessionCommandDenied`), before the Command's own chain. That is the earlier of two denials of the same fact.
2. **FBR.** `question_selection_handler.select_question` (a closed, earlier Work Unit) is reached only by tests. No route, read model or capability exists, so a Session in QUESTION_SELECTION cannot record a human selection.
3. **Home.** 03 §39, 04 AUTH-DEP-SEL-001/002, 09 §85, 12 AC-12-004.
4. **Repair.**
   - **`packages/application/selection_command.py` (new).** `select_in_session` is the one product entry:
     - replay guard, with the Command's own payload fingerprint;
     - F09-2 membership precheck;
     - **Session row lock** (`get_for_update`);
     - expected Session version (09 §85);
     - for an actor who holds the right, `selection_blocker`. It is the one definition shared with the projection, and checks in order:
       1. `SESSION_NOT_IN_QUESTION_SELECTION`;
       2. `SELECTOR_NOT_UNIQUE` (effective holders ≠ 1);
       3. `PRIMARY_ALREADY_SELECTED`;
       4. `COMPELLING_LIMIT_REACHED`;
       5. `QUESTION_ALREADY_SELECTED`;
     - then the unchanged governed Command.
     - An actor without the right skips the blockers and is denied by the Command's BND-005, with the attempt recorded.
   - **`packages/application/http_f05.py` (new).** `dispatch_select_question` and `dispatch_question_selections`.
   - **`http_f02._command_envelope`.** `SelectQuestionDenied` is answered as `denied` with the terminal boundary reason.
   - **API** (09 §85 under the Workspace-scoped Session path):
     - `POST …/sessions/{s}/question-selections` (TRN-SEL-001);
     - `POST …/sessions/{s}/primary-question` (TRN-SEL-002);
     - `GET …/sessions/{s}/question-selections`.
   - **Projection.**
     - Position `selection` (proof mode, primary, the selections).
     - `actions.SELECT_COMPELLING_QUESTION` / `SELECT_PRIMARY_QUESTION`: `NO_QUESTION_SELECTION_RIGHT`, or the blocker; relevant in QUESTION_SELECTION.
   - **Isolation sweep.** Three routes added.
5. **Propagation.**
   - **AFFECTED:** position (additive keys); the command envelope (one more denial type); the isolation sweep (+3 routes: outsider, cross-URL and expiry cases all pass).
   - **NOT AFFECTED:**
     - the governed Command and its tests (13, unchanged);
     - event contracts: the existing `CMD_SELECT_*_COMMITTED` names are kept, see the Case 2 choices;
     - the grant path, where the single-holder rule is enforced at selection and not at grant, see the Case 2 choices;
     - the DB schema.
6. **Local proof.** ruff, mypy (209 files), and the architecture, SDK and test-only import checks. The API layer passes the selection type as a string; it may not import `domain`.
7. **Integration.**
   - **Falsifiers:** real HTTP → PostgreSQL through F02 → F03 → F04 → B1 → B2.
   - **Real stack** (`evidence/b3_runtime_proof.txt`):
     - **Selection before any grant:** 403 `DENIED_NO_MATCHING_BINDING`. The controller holds no selection right.
     - **Grant:** the owner grants QUESTION_SELECTION_RIGHT over HTTP (200); both capabilities then show as available.
     - **Compelling q0:** 200.
     - **q0 again:** 422 `QUESTION_ALREADY_SELECTED`.
     - **Primary q0:** 200.
     - **Primary q1:** 422 `PRIMARY_ALREADY_SELECTED`.
     - **GET and position:** both show FIXTURE_NON_PROOF, the primary, and the two selections. The Session stays in QUESTION_SELECTION.
     - **Real worker:** 0 failed. The canonical rows, the committed `CMD_SELECT_*_COMMITTED` events and the COMMITTED | BINDING audit rows at `SESSION:<id>` all agree.
8. **Preservation.** The Command's BND-005 and BND-014 still decide authority. The HD-24 Fixture marking extends to selections. HD-25 is unchanged.
9. **Regression.** Live 1934 / 2; no-DB 915 (`evidence/b3_regression.txt`).
10. **Mutation.** **12/12 KILLED** (`evidence/b3_mutation_proof.txt`). The mutations cover:
    - the state gate, the single selector, one primary, the cap, and duplicates;
    - the holder-only precheck ordering;
    - the Session lock and the expected version;
    - the denial mapping;
    - the read-model proof mode;
    - both capability rules.
11. **Inverse.** A position `selection.selections[i]` traces back as follows:
    - the `question_selections` row (selector, binding id);
    - the CommitUnit of CMD_SELECT_*_QUESTION, with BND-014 fresh QUESTION_SELECTION_RIGHT at `SESSION:<id>`;
    - the audit row (HUMAN_USER, BINDING);
    - the grant CommitUnit of that binding (WORKSPACE_GOVERNANCE_RIGHT);
    - the Session in QUESTION_SELECTION, entered by B2's HUMAN_PROCEDURAL_CONFIRMATION.
12. **Deep sweep.**
    - **Semantic drift:** none; no new vocabulary beyond blocker codes.
    - **Authority:** the controller does not inherit selection (P-08).
    - **Race:** the Session lock serializes the cross-row rules, and the DB constraints remain the backstop.
    - **Questions-only:** nothing is deleted.
13. **Inverse deep sweep.** Every selection traces to exactly one effective, unique holder binding.

**Case 2 choices (recorded):**
- **Single holder (AC-12-004) enforced at selection time.** A second active holder blocks everyone (`SELECTOR_NOT_UNIQUE`) instead of choosing a winner. This makes 05 §40's "only if later policy defines" fail closed without changing the F02 grant contract. Refusing such a grant at grant time would narrow a shared F02 Command and is left to NQ-GAP-026.
- **Primary Question.** TRN-SEL-002 reads "among valid candidate/compelling Questions". The existing Command admits any Question of the Session's Challenge as a candidate, and this Work Unit does not narrow it to the compelling set. A narrower reading would be a semantic change to a closed Command.
- **Eligibility** "under later method contract" stays "same Challenge" (existing BND-007) plus the 12 prototype rule. No method contract exists.
- **Event names.** 12 row 19 / 13 P-08 name `QUESTION_SELECTED`, and 09 §71 lists `QUESTION_SELECTION_CREATED` / `PRIMARY_QUESTION_SELECTED`. The committed contracts `CMD_SELECT_*_QUESTION_COMMITTED` (F08 registry) are kept, because renaming a registered event contract is a naming migration outside this relation.
- **Proof mode.** A human selection is not an AI proof. Its Fixture status is carried by the Session's `proofMode` on the read model, not by a new event key.
- **Session version.** The expected Session version is checked, but a selection does not advance it, because the Session state is unchanged (03 "Session remains QUESTION_SELECTION").

## 3. After B3 (derivation)
Every further F05 relation depends on HA-22 (ImpactChain authoring authority): the ImpactChain, then TRN-SESS-009, then everything after INVESTIGATION. Replacing or withdrawing a selection stays blocked by GAP-03-018. See the Field report §9.

## 4. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B3`). Not REVIEWED_FIELD, not PUBLISHED_FIELD.
