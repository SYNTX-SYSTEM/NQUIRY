# WU-PFC-B4 — The Five-Why ImpactChain product path under HD-26

**Execution invariant:** Architecture 25 §23.

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-B4 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PFC-B = F05 (19 §25); 25 F16 |
| Colour / role / model | RED · schema / application / API / projection · Claude Opus 5.5 |
| Human authorization | HD-26 / NQ-DEC-054 (2026-09-27): Option A, S1(i), S2(i); "Derive and autonomously execute all newly eligible RED Work Units, including the ImpactChain product path". |
| Derivation | Field report §10. HA-22 was the only boundary of the ImpactChain; HD-26 closes it. |
| Predecessor / baseline | `checkpoint-PFC-B3` → `4cf9498`; record `5a91248`; HD-26 record `0e18e63`. Live 1934 / 2 (+1 HD-26 ledger case); no-DB 915 (+1). |
| State isolation | `worktrees/pfc-integration`; `nquiry_pfc_int_test` (migrated to `e8c2a5f1b7d4`, round-trip proven). Runtime: `nquiry_pfc_int_runtime`, API :18433. |
| Authoritative home | 02 §28, §45.1, §51.1, AC-02-014/015; 03 §5, §40, §47.7, AC-03-014; 09 §48, §63, §86; HD-26. |
| Authorized delta | The ImpactChain aggregate (schema, repository), CMD_CREATE_IMPACT_CHAIN and CMD_APPEND_IMPACT_CHAIN_NODE, their routes, the read model and the capabilities. Also a backward-compatible `authority_class` parameter on the shared governed runner `_run` (default SESSION_CONTROL_RIGHT) and one content-authority denial type. **Not in scope:** correction or supersession of answers (HD-26 S1); chain replacement or rebuild (GAP-03-018); AI of any kind (HD-26 rule 5, HD-21); TRN-SESS-009 (WU-PFC-B5); CYAN. |
| Must become true | The QUESTION_SELECTION_RIGHT holder who selected the current primary Question creates exactly one ImpactChain for it and appends human answers for levels 1 to 5, strictly one after another. The chain is complete exactly when levels 1 to 5 exist. Every node keeps its author, level, capture time, chain, Session and primary anchor. A Fixture chain reads FIXTURE_NON_PROOF. |
| Must remain true | B0–B3, HD-24, HD-25; the governed runner's behaviour for every existing caller (SESSION_CONTROL_RIGHT by default); F02–F04, F08, F09. |
| Must remain impossible | Authoring by the Session controller without the selection right (rule 3); by a participant (rule 4); by a selection-right holder who did not select the current primary; by a system or AI actor (rule 5). Also impossible: a chain without a primary; a second chain for the same primary (S2); a skipped or repeated level; a level outside 1..5; a blank or oversized answer; any UPDATE or DELETE of a node, or a change of a chain's anchor (S1), including directly in the database; a node by another author than the chain's; authoring outside QUESTION_SELECTION; a stale chain view committing; one intent committing twice; answer text in an Event. |
| Falsifiers | `tests/e2e/test_pfc_b4_impact_chain.py` (20 cases). |

## 2. Execution record

1. **RED.**
   - **Honest ordering note:** in this Work Unit the implementation was written before the falsifier file.
   - **How RED was then proven:** the falsifiers were run against the unchanged predecessor tree `0e18e63`, in a temporary detached worktree containing only the new test file, with the test database at the predecessor head.
   - **Result:** **20 of 20 failed**, for the right reasons:
     - no route (404, and envelope KeyErrors: `kind` ×10, `impactChainId` ×3);
     - no `CREATE_IMPACT_CHAIN` capability ×5;
     - no `application.impact_chain_handler`.
   - **Evidence:** `evidence/b4_regression.txt`.
2. **FBR.** No ImpactChain exists: no table, Command, route or view. So 03 TRN-SESS-009's "SYSTEM_PROOF of complete five-level ImpactChain" can never hold.
3. **Home.** 02 §28, 03 §40, 09 §48/§63/§86, completed by HD-26.
4. **Repair.**
   - **Migration `e8c2a5f1b7d4`.**
     - `impact_chains`, unique per (Session, primary Question). An anchor trigger requires the Session's PRIMARY selection made by the creator.
     - A chain's columns are immutable except `record_version`, which only advances by +1. DELETE is rejected.
     - `impact_chain_nodes` uses a composite FK to the chain's identity (chain, Workspace, Session, primary Question, **creator = author**).
     - Levels are limited to 1..5 and are unique; a non-blank answer is required.
     - A successive-level trigger takes the chain row lock and requires level = max + 1.
     - Nodes reject UPDATE and DELETE.
     - RLS `workspace_isolation` applies.
   - **`persistence/impact_chain_repository.py`.** Create, append (node plus version +1), read, and a version reader.
   - **`application/impact_chain_handler.py`.**
     - `create_impact_chain` and `append_impact_chain_node` run through `_run` with **QUESTION_SELECTION_RIGHT**, at BND-005 and fresh at BND-014, HUMAN_USER only.
     - `impact_chain_blocker` is shared with the projection and checks in order:
       1. `SESSION_NOT_IN_QUESTION_SELECTION`;
       2. `NO_PRIMARY_QUESTION`;
       3. `NOT_PRIMARY_QUESTION_SELECTOR`, a content-authority denial answered 403;
       4. `IMPACT_CHAIN_ALREADY_EXISTS`, `NO_IMPACT_CHAIN` or `IMPACT_CHAIN_COMPLETE`;
       5. `LEVEL_NOT_SUCCESSIVE`.
     - It is re-checked under the Session row lock.
     - Events: IMPACT_CHAIN_CREATED and IMPACT_CHAIN_NODE_APPENDED (level, author, `complete`, `fixture`). The answer text is never included.
   - **`session_control_handler`.**
     - `_run(authority_class=…)`, defaulting to SESSION_CONTROL_RIGHT, so all existing callers are unchanged.
     - `ContentAuthorityDenied`, recorded as DENIED with `failure_code` CONTENT_AUTHORITY_DENIED.
   - **Envelope.** `http_f02` maps `ContentAuthorityDenied` to `denied`.
   - **Event registry.** Two contracts, plus the `impact_chain` aggregate in the committed-event table map.
   - **API** (09 §86, under the Workspace-scoped Session path; one chain per current primary):
     - `POST …/sessions/{s}/impact-chain` with `{expectedVersion}`;
     - `POST …/sessions/{s}/impact-chain/nodes` with `{expectedChainVersion, level, answer}`;
     - `GET …/sessions/{s}/impact-chain`.
     - Input rejections: `LEVEL_OUT_OF_RANGE`, `ANSWER_REQUIRED`, `ANSWER_TOO_LONG`.
   - **Projection.**
     - Position `impactChain`: proof mode, primary, chain, version, author, `nextLevel`, `complete`, and the levels. Answer text is served to the frozen-set audience.
     - `actions.CREATE_IMPACT_CHAIN` / `APPEND_IMPACT_CHAIN_NODE`.
5. **Propagation.**
   - **AFFECTED:**
     - the schema (+2 tables, head `e8c2a5f1b7d4`);
     - `tests/security/test_workspace.py`'s RLS table registry (+2);
     - the isolation sweep (+3 routes);
     - the event registry (+2);
     - `_run`, backward compatible: the full regression is the proof.
   - **NOT AFFECTED:** the selection Command; B0–B3 behaviour; CYAN.
6. **Local proof.** ruff; mypy (213 files); the architecture, SDK and test-only import checks; `verify_migrations` static and live; migration down/up round-trip.
7. **Integration.**
   - **Falsifiers:** real HTTP → PostgreSQL through F02 → F03 → F04 → B1 → B2 → B3.
   - **Real stack** (`evidence/b4_runtime_proof.txt`, runtime DB migrated to `e8c2a5f1b7d4`):
     - create: 200;
     - level 2 first: 422 `LEVEL_NOT_SUCCESSIVE`;
     - levels 1–5: 200, with `complete` only at 5;
     - level 6: 400 `LEVEL_OUT_OF_RANGE`;
     - GET: complete, `nextLevel` null, FIXTURE_NON_PROOF, levels [1..5].
   - **Real worker:** 0 failed.
     - The canonical nodes carry author, Session and primary anchor.
     - Events IMPACT_CHAIN_CREATED (v1) and NODE_APPENDED (v2..v6) carry `fixture` true, and `complete` only at level 5.
     - Audit rows: COMMITTED | BINDING (1 create, 5 appends).
8. **Preservation.** HD-26 rules 1–8, S1 and S2 are each pinned by a falsifier. HD-24 Fixture marking is pinned on the event and the read model. HD-21 holds: no AI path exists.
9. **Regression.** Live 1962 / 2; no-DB 915 (`evidence/b4_regression.txt`).
10. **Mutation.** **14/14 KILLED** (`evidence/b4_mutation_proof.txt`). The mutations cover:
    - the sole-author check;
    - the authority class, in the handler and in `_run` at BND-005 and BND-014;
    - S2;
    - successive levels, appending to a complete chain, and the completion predicate;
    - the state gate;
    - answer and level validation;
    - Fixture marking on the read model and the event;
    - the denial mapping;
    - the capability.
    The database backstops are proven directly by falsifiers.
11. **Inverse.** A position `impactChain.levels[i]` traces back as follows:
    - the node row (author, level, captured_at, chain, Session, primary Question);
    - which is FK-bound to the chain, whose anchor trigger proved the creator's PRIMARY selection;
    - the CommitUnit of CMD_APPEND_IMPACT_CHAIN_NODE: BND-014 fresh QUESTION_SELECTION_RIGHT at `SESSION:<id>`, audit HUMAN_USER BINDING;
    - the selection's binding;
    - the owner's grant.
12. **Deep sweep.**
    - **Authority:** control, participation, system and AI all confer nothing.
    - **Content:** the answer text stays in its canonical row, with no Event copy (F08 payload rule).
    - **Race:** the Session lock plus the chain row lock in the trigger serialize appends.
    - **Cross-field:** the selection rows are read only.
13. **Inverse deep sweep.** Every node traces to exactly one human author, who selected the primary Question the chain is anchored to.

**Case 2 choices (recorded):**
- **Routes** sit under the Workspace-scoped Session path instead of 09 §86's `/impact-chains/{id}`. S2(i) makes the Session's current chain unique, and every product route is Workspace-scoped (F09-2).
- **Event names** IMPACT_CHAIN_CREATED and IMPACT_CHAIN_NODE_APPENDED: 09 §70/§71 name none, and §71 permits names for approved facts.
- **Answer bound:** 2000 characters, the Burst Question bound. The answer is stored verbatim; only a blank answer is refused.
- **Answer visibility:** the frozen-set audience (HD-13 / HD-22). The structure is always served.
- **Expected versions:** creation checks the Session version (the Session is not advanced). An append checks the chain version, which advances by one per node.
- **Refusal kinds:** "not the primary selector" is a **denial** (authority, HD-26). Every other unmet condition is **blocked**.

## 3. After B4 (derivation)
With a complete chain, TRN-SESS-009 is fully specified (03, 04 AUTH-DEP-SESS-009): **WU-PFC-B5**.

## 4. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-B4`). Not REVIEWED_FIELD, not PUBLISHED_FIELD.
