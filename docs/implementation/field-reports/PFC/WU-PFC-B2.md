# WU-PFC-B2 — TRN-SESS-008 BEGIN_QUESTION_SELECTION under HD-25

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B2 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (19 §25) |
| Colour / role / model | RED · application / API / projection · Claude Opus 5.5 |
| Human authorization | HD-25 / NQ-DEC-053 (2026-09-27): C-a together with C-c; "Materialize the confirmation through the existing TRN-SESS-008 / CMD_BEGIN_QUESTION_SELECTION path." |
| Derivation | HD-25 closes GAP-03-007 for this product, the only open precondition of TRN-SESS-008 (WU-PFC-B1 §3). |
| Predecessor / baseline | `checkpoint-PFC-B1` → `ea4755d`; HD-25 record `3319b58`. Live 1891 / 2; no-DB 913. |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test`. Runtime: `nquiry_pfc_int_runtime` @ `d4f7b2c9e6a1`, API :18433. |
| Authoritative home | 03 TRN-SESS-008 ("explicitly completed according to later contract"; "No AI output may create the selection transition by itself"; "Reflection response persistence is not required by 03"; FAILURE "Session remains REFLECTION"); 04 AUTH-DEP-SESS-008 (SESSION_CONTROL_RIGHT; DENY "Only UI navigation. Only AI output."; SYSTEM-DERIVED not enabled; AUDIT "Record controller authority and completion proof basis"); 12 row 18; 16 REC-029 (HD-25). |
| Authorized delta | The Command, handler, route, event contract and projection for TRN-SESS-008. **Not in scope:** Reflection prompts and responses (HA-05 stays OPEN and decoupled); QuestionSelection (TRN-SEL-001/002); ImpactChain; TRN-SESS-009; CYAN. |
| Must become true | The SESSION_CONTROL_RIGHT holder's explicit confirmation moves a Session from REFLECTION into QUESTION_SELECTION, with zero Reflection responses. The audit row and the committed event record the basis HUMAN_PROCEDURAL_CONFIRMATION. A Fixture Session stays FIXTURE_NON_PROOF, and its REFLECTION still reads MOCK_NON_PROOF. |
| Must remain true | HD-16, HD-19, HD-20, HD-24; B0 and B1 semantics; F02/F03/F04/F08/F09 behaviour. |
| Must remain impossible | QUESTION_SELECTION without an explicit confirmation (missing, `false`, `null`); a non-boolean confirmation; the owner or a participant confirming; a SYSTEM_SERVICE actor confirming (SYSTEM_DERIVED); the transition from any state but REFLECTION; a separate Reflection-complete state or transition; two commits of one intent. |
| Falsifiers | `tests/e2e/test_pfc_b2_begin_question_selection.py` (16 cases). |

## 2. Execution record

1. **RED.** 15 of 16 cases failed for the right reasons: no route (404, including envelope KeyErrors), no `BEGIN_QUESTION_SELECTION` capability, and no `begin_question_selection`. The one case that already passed pins the HD-25 prohibition: no Reflection-complete state or transition exists.
2. **FBR.** TRN-SESS-008 exists only in the domain topology (`session_transitions.py`). No Command realizes it, so every Session stays in REFLECTION.
3. **Home.** 03 TRN-SESS-008 and 04 AUTH-DEP-SESS-008, completed by HD-25.
4. **Repair.**
   - **`packages/application/reflection_handler.py`.**
     - `question_selection_blocker(session, confirmed)`: returns `SESSION_NOT_IN_REFLECTION` or `REFLECTION_COMPLETION_NOT_CONFIRMED`. Responses are not consulted.
     - `begin_question_selection`, CMD_BEGIN_QUESTION_SELECTION:
       - the confirmation is a **mandatory field of the fingerprinted payload**, so a replay with a different confirmation is a different intent;
       - replay guard, membership precheck (F09-2), stale check;
       - BND-007 TRN-SESS-008;
       - `_run`: BND-001 HUMAN_USER only, BINDING SESSION_CONTROL_RIGHT at `SESSION:<id>`;
       - the blocker is re-checked under the Session row lock;
       - one commit: REFLECTION → QUESTION_SELECTION.
     - The audit `state_after_ref` is `session:QUESTION_SELECTION|reflection_completion:HUMAN_PROCEDURAL_CONFIRMATION`.
     - Event **SESSION_QUESTION_SELECTION** carries `reflection_completion_basis` and `fixture`.
   - **API.** `POST /workspaces/{w}/sessions/{s}/transitions/begin-question-selection`, body `{expectedVersion, reflectionCompletionConfirmed: StrictBool | null}`, via `http_f04.dispatch_begin_question_selection`. An absent or `null` confirmation is treated as not confirmed (blocked); a non-boolean value is rejected (400).
   - **Event contract.** SESSION_QUESTION_SELECTION added to `PRODUCTION_EVENT_CONTRACTS`.
   - **Projection.**
     - `actions.BEGIN_QUESTION_SELECTION`: available in REFLECTION to the controller, with `requiresReflectionCompletionConfirmation: true`; relevant in REFLECTION.
     - `reflectionCompletion: {basis}`, read from the committed event.
   - **Isolation sweep.** The route was added; its coverage guard requires this.
5. **Propagation.**
   - **AFFECTED:** the new Command path; position (additive keys); the event contract registry (+1); the isolation sweep (+1 route: outsider, cross-URL and expiry cases all pass).
   - **NOT AFFECTED:** B1 readiness (read only); authority vocabulary; the DB transition trigger (REFLECTION → QUESTION_SELECTION is already legal); the selection handler (not touched); CYAN.
6. **Local proof.** ruff, mypy (206 files), and the architecture, SDK and test-only import checks.
7. **Integration.**
   - **Falsifiers:** real HTTP → PostgreSQL, through the F02 → F03 → F04 → B1 chain.
   - **Real stack** (`evidence/b2_runtime_proof.txt`):
     - **Fixture Session, without confirmation:** 422 `REFLECTION_COMPLETION_NOT_CONFIRMED`; the Session stays in REFLECTION.
     - **Fixture Session, with confirmation:** 200 committed, `reflectionCompletionBasis` HUMAN_PROCEDURAL_CONFIRMATION; the Session reaches QUESTION_SELECTION; `proofMode` stays FIXTURE_NON_PROOF; the reflection view stays MOCK_NON_PROOF.
     - **Real Session:** stays in ANALYSIS (HD-20, blocked at B1); `SESSION_NOT_IN_REFLECTION`.
     - **Real worker:** `session_read_model` shows QUESTION_SELECTION | fixture=true and ANALYSIS | fixture=false. The audit row is COMMITTED | BINDING with the basis. Diagnostics show 0 failed.
8. **Preservation.**
   - **HD-25:** zero responses; no new state; SYSTEM_SERVICE denied; owner and participant denied.
   - **HD-24 rules 6 and 7:** the Fixture keeps FIXTURE_NON_PROOF.
   - **HD-20:** a real Session still cannot pass REFLECTION on mock proof.
   - **Full regression:** see item 9.
9. **Regression.** Live 1910 / 2; no-DB 914 (`evidence/b2_regression.txt`).
10. **Mutation.** **11/11 KILLED** (`evidence/b2_mutation_proof.txt`). The mutations cover:
    - the confirmation, in the precondition, in the fingerprinted payload and at the HTTP edge;
    - the state gate;
    - the basis, in the audit row, the event and the projection;
    - the Fixture status on the event;
    - the capability's availability, its relevance, and its confirmation flag.
    Before the proof, one falsifier was strengthened: the capability outside REFLECTION.
11. **Inverse.** Projection `reflectionCompletion.basis = HUMAN_PROCEDURAL_CONFIRMATION` traces back as follows:
    - the committed SESSION_QUESTION_SELECTION event;
    - the CommitUnit of CMD_BEGIN_QUESTION_SELECTION, whose payload fingerprint includes `reflection_completion_confirmed = true`;
    - the audit row: HUMAN_USER, BINDING SESSION_CONTROL_RIGHT at `SESSION:<id>`, with the basis in `state_after_ref`;
    - the previous SESSION_REFLECTION event and its proof (B1).
12. **Deep sweep.**
    - **Semantic drift:** none; no new state, transition or Authority class.
    - **Authority leakage:** none; this is the same `_run` authority as TRN-SESS-007.
    - **HA-05:** untouched. No response table or content is read.
13. **Inverse deep sweep.** Every QUESTION_SELECTION entry traces to exactly one human BINDING confirmation.

**Case 2 choices (recorded):**
- An absent or `null` confirmation is answered as `blocked` (422, 03 FAILURE "Session remains REFLECTION"), not as `rejected`. Only an ill-typed value is `rejected`.
- The basis lives in the audit `state_after_ref` and in the committed event, because the command row stores only a fingerprint.
- The event name `SESSION_QUESTION_SELECTION` follows the `SESSION_<STATE>` naming.

## 3. After B2 (derivation)

See the Field report §8. QuestionSelection (TRN-SEL-001/002) can be derived for a single selector. The Five-Why ImpactChain has no defined author or creator authority, which is a new Case 3 (HA-22). TRN-SESS-009 is therefore transitively blocked.

## 4. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B2`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F05: Fixture Sessions reach QUESTION_SELECTION.
