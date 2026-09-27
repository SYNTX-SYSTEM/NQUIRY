# WU-PFC-B5 — TRN-SESS-009 BEGIN_INVESTIGATION

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B5 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (19 §25) |
| Colour / role / model | RED · application / API / projection · Claude Opus 5.5 |
| Human authorization | HD-26: "…including the ImpactChain product path and TRN-SESS-009 BEGIN_INVESTIGATION where now derivable". |
| Derivation | With the ImpactChain (B4), every precondition of TRN-SESS-009 is source-defined: 03 TRN-SESS-009 and 04 AUTH-DEP-SESS-009 (authority SESSION_CONTROL_RIGHT; "Selection was created by valid Question Selection Authority"). |
| Predecessor / baseline | `checkpoint-PFC-B4` → `6726401`; identity record `7d52549`. Live 1962 / 2; no-DB 915. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test` @ `e8c2a5f1b7d4`. Runtime: `nquiry_pfc_int_runtime`, API :18433. |
| Authoritative home | 03 TRN-SESS-009, §40.3, §47.7, §23 examples ("INVESTIGATION cannot be reached without valid human selection and ImpactChain completion for Question Burst"); 04 AUTH-DEP-SESS-009; HD-26 rule 8. |
| Authorized delta | The Command, handler, route, event contract and projection for TRN-SESS-009. **Not in scope:** anything inside INVESTIGATION (Evidence, research; HA-08); TRN-SESS-010 (GAP-03-008, see HA-23); CYAN. |
| Must become true | The SESSION_CONTROL_RIGHT holder moves a Session with at least one compelling selection, exactly one primary, validly authorized selections and a complete five-level ImpactChain into INVESTIGATION. The audit links the transition to the selection authority evidence. A Fixture Session stays FIXTURE_NON_PROOF. |
| Must remain true | B0–B4; HD-24, HD-25, HD-26; F02–F04, F08, F09. |
| Must remain impossible | INVESTIGATION with no chain, or an incomplete chain (0 or 4 levels); without a compelling selection; without a primary; with a selection not made under a QUESTION_SELECTION_RIGHT binding of the selector at this Session; begun by the owner, a participant, the selector without control, or a system actor. Also impossible: selecting after INVESTIGATION begins; a stale view committing; one intent committing twice. |
| Falsifiers | `tests/e2e/test_pfc_b5_begin_investigation.py` (13 cases). |

## 2. Execution record

1. **RED.**
   - **Ordering note:** the handler module was drafted (unwired) before the falsifier file was run.
   - **How RED was proven:** the falsifiers ran against the committed B4 tree `7d52549` in a temporary detached worktree containing only the new test file.
   - **Result:** **13 of 13 failed**, for the right reasons:
     - no route (404 ×13, across the assertion shapes);
     - no `BEGIN_INVESTIGATION` capability ×3;
     - envelope KeyErrors;
     - no `application.investigation_handler`.
2. **FBR.** TRN-SESS-009 exists only in the domain topology. No Command realizes it, so no Session reaches INVESTIGATION.
3. **Home.** 03 TRN-SESS-009 and 04 AUTH-DEP-SESS-009.
4. **Repair.**
   - **`packages/application/investigation_handler.py` (new).**
     - `investigation_readiness` is shared with the projection and re-checked under the Session row lock. It checks in order:
       1. `SESSION_NOT_IN_QUESTION_SELECTION`;
       2. `NO_COMPELLING_QUESTION_SELECTED`;
       3. `NO_PRIMARY_QUESTION` (exactly one);
       4. `SELECTION_AUTHORITY_INVALID`: every selection's stored binding must be a QUESTION_SELECTION_RIGHT at exactly this Session, held by its selector (a later revocation does not undo a valid selection, 09 §33.1);
       5. `IMPACT_CHAIN_INCOMPLETE` (HD-26 rule 8).
     - `begin_investigation`, CMD_BEGIN_INVESTIGATION: replay guard, F09-2 membership precheck, stale check, BND-007 TRN-SESS-009, `_run` with SESSION_CONTROL_RIGHT BINDING (HUMAN_USER only), one commit QUESTION_SELECTION → INVESTIGATION.
     - The relation refs name every selection, every selection binding and the chain (04 AUDIT "Link transition authority to selection authority evidence").
     - Event **SESSION_INVESTIGATION** carries the primary Question, its selection and binding, the compelling count, the chain and `fixture`.
   - **API.** `POST …/sessions/{s}/transitions/begin-investigation`.
   - **Event registry.** SESSION_INVESTIGATION.
   - **Projection.** `actions.BEGIN_INVESTIGATION` (relevant in QUESTION_SELECTION), and `investigation`, read from the committed event.
   - **Isolation sweep.** +1 route.
5. **Propagation.**
   - **AFFECTED:** position (additive keys); event registry (+1); isolation sweep (+1 route).
   - **NOT AFFECTED:** selection and ImpactChain Commands (read only); the DB transition trigger (QUESTION_SELECTION → INVESTIGATION is already legal in 03's chain); CYAN.
6. **Local proof.** ruff, mypy (215 files), architecture check.
7. **Integration.**
   - **Falsifiers:** real HTTP → PostgreSQL through F02 → F03 → F04 → B1–B4.
   - **Real stack** (`evidence/b5_runtime_proof.txt`):
     - without a chain: 422 `IMPACT_CHAIN_INCOMPLETE`;
     - after levels 1–5: 200 committed. The Session is in INVESTIGATION and FIXTURE_NON_PROOF, and `investigation` shows the primary, its selection, compelling count 1 and the chain.
   - **Real worker:** `session_read_model` shows INVESTIGATION | fixture=true.
     - The SESSION_INVESTIGATION event runs QUESTION_SELECTION → INVESTIGATION with `fixture` true.
     - The audit row is COMMITTED | BINDING at `SESSION:<id>`. The CommitUnit relation refs name both selections, the selection binding and the chain.
     - Diagnostics show 0 failed.
8. **Preservation.** The selection right is not the operation authority: the selector without control is denied. The controller is the operation authority, but the required human decision is the prior selection (04). The Fixture marking is kept on the event and the read model.
9. **Regression.** Live 1978 / 2; no-DB 915 (`evidence/b5_regression.txt`).
10. **Mutation.** **11/11 KILLED** (`evidence/b5_mutation_proof.txt`). The mutations cover:
    - the state gate, the compelling selection and exactly one primary;
    - selection-authority verification, including its authority class;
    - chain completeness;
    - the audit link to selection authority;
    - Fixture marking on the event;
    - the capability's preconditions and relevance;
    - the read model.
11. **Inverse.** Position `investigation.primaryQuestionId` traces back as follows:
    - the committed SESSION_INVESTIGATION event;
    - the CommitUnit of CMD_BEGIN_INVESTIGATION, whose relation refs name each `question_selection`, each `authority_binding` and the `impact_chain`;
    - those rows: the selector's QUESTION_SELECTION_RIGHT grant, and the five human nodes by the primary selector (B4);
    - the audit row: HUMAN_USER, BINDING SESSION_CONTROL_RIGHT at `SESSION:<id>`.
12. **Deep sweep.**
    - **Authority separation:** control and selection authority stay distinct (P-08).
    - **Race:** the Session row lock serializes against a concurrent append or selection.
    - **After INVESTIGATION:** selection and chain authoring are blocked by their state gates.
13. **Inverse deep sweep.** Every INVESTIGATION entry traces to exactly one complete chain and one primary selection made under a valid selection binding.

**Case 2 choices (recorded):**
- "Selection was created by valid Question Selection Authority" is checked against the binding stored on each selection: class, exact Session scope, and holder = selector. It is not checked against current effectiveness, because 09 §33.1 says the stored reference records the authority of the act.
- The event name `SESSION_INVESTIGATION` follows the `SESSION_<STATE>` naming.

## 3. After B5 (derivation)
- **TRN-SESS-010 BEGIN_EXPERIMENT_PHASE:** its authority is defined (SESSION_CONTROL_RIGHT), but its precondition, "Investigation phase completion is explicitly asserted", is **GAP-03-008 `[UNDERDEFINED]`**. 04 says SYSTEM-DERIVED authority is "Not enabled while GAP-03-008 … remain[s] open". This is a new Case 3: **HA-23**.
- **Work inside INVESTIGATION** (Evidence, research, observation): **HA-08**.

See the Field report §10.

## 4. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B5`). Not REVIEWED_FIELD, not PUBLISHED_FIELD.
