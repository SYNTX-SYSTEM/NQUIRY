# WU-PFC-PCPG-2 — FBR-PCPG-2 (closed): the full consumable operation index

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-2 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "continue with FBR-PCPG-2" (2026-09-30), following "PASS. Human Authority approves WU-PFC-PCPG-1" and the explicit push/tag of `checkpoint-PFC-PCPG-1` — both instructed discipline (RED falsifiers first, minimum coherent delta, adversarial proof, mutation proof, fresh full repository regression, E6, Field reconstruction, documentation) and "continue autonomously ... until the next proven Work Unit closure". Then, explicitly: "Continue by completing FBR-PCPG-2 as a whole. Finish the remaining Workspace / Challenge-root and Decision-operation slices ... Only when FBR-PCPG-2 is completely closed may you create the canonical Work Unit commit/checkpoint and move to R-05." Do not cross a Human Authority boundary; do not begin any provider SEND path — honored throughout (no boundary crossed, R-05 not begun). |
| Predecessor | `pfc-integration` `769b7b9815a0d840aeff157cbe76203eb0b48e31` (`checkpoint-PFC-PCPG-1`, pushed). |
| State isolation | Same worktree/branch/DB as WU-PFC-PCPG-1; no migration needed (this Work Unit adds no schema). |
| E1 (re-derived against the current repository) | FBR-PCPG-1 (R-01/R-02) is closed (`checkpoint-PFC-PCPG-1`). The next relation in `00_FIELD.md` §12's own order is **FBR-PCPG-2: SEMANTIC DELTA → CANONICAL OPERATION**, quoted verbatim: "There is no vocabulary relation mapping an observed action onto the existing operation catalog... What is missing is its consumable index: per operation, its execution class, authority home, readiness producer, effect class and data inputs." A repository search confirmed no such index existed anywhere before this Work Unit (`grep` for `OperationIndexEntry`/`operation_index`: zero hits). Break type (a): nothing exists. Not Case 3 (00_FIELD.md §13 lists no HA question gating R-06's catalog itself; HA-PCPG-1 gates the LATER capability value, FBR-PCPG-4, not this relation). |
| Delta (both increments, this Work Unit in full) | **Increment 1** (session recorded below, §2A): the 18 Session-scoped operations `application.inquiry_queries.session_position` already projects readiness for. **Increment 2** (§2B): the remaining 8 real Commands — CREATE_WORKSPACE, CREATE_CHALLENGE, ADD_MEMBER, GRANT_AUTHORITY_BINDING, REVOKE_AUTHORITY_BINDING, CREATE_SESSION, OPEN_DECISION_CONSIDERATION, RECORD_HUMAN_DECISION — closing FBR-PCPG-2 completely. 26 real operations catalogued; none invented, none guessed. |
| Must become true | A pure, read-only catalog of all 26 real operations: for each, `execution_class` (this Field's own vocabulary, 04_OBSERVATION_RESULT.md §4), `architecture_ref` (real citations), `readiness_producer` (a real, checked function reference, or `None` when honestly absent — R-07's own `NO_AUTHORITATIVE_PRODUCER` vocabulary) and `data_inputs`. |
| Must remain true | Every existing route, Command, migration and test; `session_position`/`workspace_overview`/`challenge_detail` themselves unchanged. |
| Must remain impossible | The index missing or over-claiming an operation relative to the real producers/routes it cites; a decision-class, founding, governance or state-transition operation classified `PROVIDER_COMPUTATION`; an AIOP-request operation classified anything else; a duplicate `operation_id` across either group; a fabricated `readiness_producer` for OPEN_DECISION_CONSIDERATION/RECORD_HUMAN_DECISION where none exists; the module touching a database, a provider or any live authority evaluation of its own. |
| Falsifiers | `tests/e2e/test_pcpg_operation_index.py`: 78 cases (47 increment-1 + 31 increment-2). |

## 2A. Execution record — Increment 1 (Session-scoped, 18 operations)

**1 RED (right reason).** The falsifier suite was written first; the module was then moved aside and the suite run against the unrepaired tree: collection error, `ModuleNotFoundError: No module named 'application.pcpg_operation_index'` — the correct reason (the relation genuinely does not exist). Restored: 47/47 passed on first run.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no consumable per-operation index exists for R-06 to map a semantic delta onto
CONSUMER         (future) R-06 candidate-delta formation — not materialized here
PRODUCER         none (ABSENT — break type (a))
FBR              FBR-PCPG-2 (00_FIELD.md §12), increment 1: Session-scoped operations
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-06 (catalog: 03 transitions, 09 Commands, 04 AUTH-DEPs, 08 AIOP contracts; execution class: this Field); `application.inquiry_queries.session_position` (the real, existing capability-projection surface consumed, not re-implemented).

**4 REPAIR** (2 new files).
- `packages/application/pcpg_operation_index.py`: `ExecutionClass` (this Field's own §4 vocabulary, its first materialization), `OperationIndexEntry`, `SESSION_SCOPED_OPERATIONS` (18 entries), `operation_index()` (fresh dict per call, raises on a duplicate id), `resolve_operation()` (returns `None` for an unknown id — I-04). Every `architecture_ref` citation copied verbatim from the real handler docstrings already in this tree; every `data_inputs` tuple copied verbatim from the real route bodies in `tests/e2e/test_pfc_f09_2_isolation_sweep.py`'s own `ROUTES` table. `readiness_producer` is the single literal string `"application.inquiry_queries.session_position"` for all 18 entries, matching 00_FIELD.md's own words ("per-operation capability in `session_position.actions`", one surface).
- `tests/e2e/test_pcpg_operation_index.py`: 47 falsifiers (§3).
- **Housekeeping found in passing:** `ruff format --check .` across the whole tree surfaced that `docs/implementation/field-reports/PFC/WU-PFC-PCPG-1.md`'s own embedded Python example was not `ruff format`-clean, and ruff's markdown code-fence formatter would silently mis-render it. Corrected by hand and re-fenced as `` ```text ``. Predates this Work Unit (already present in committed `769b7b9`); fixed here because found here.

**5 PROPAGATION.** `session_position` NOT AFFECTED (read-only consumption); every existing route/Command NOT AFFECTED; WU-1's own coverage guard NOT AFFECTED; `ai_gateway`/provider path NOT AFFECTED (static falsifier); `WU-PFC-PCPG-1.md` AFFECTED (documentation only, the formatting fix above).

**6–9 PROOFS.**
- Local: `ruff check .` / `ruff format --check .` clean (except the one pre-existing, disclosed `F04/review` exception already recorded in `WU-PFC-I1.md`); `mypy` (new module) 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; migrations unchanged.
- Producer proof: `test_covers_every_session_position_action` re-reads the LIVE `session_position(...)['actions']` keys from a real Session and asserts set-equality with the index.
- Consumer proof: none yet — R-06 does not exist. Proof available: readiness-to-be-consumed (`test_every_entry_names_the_real_readiness_producer`, importlib existence check).
- Adversarial proof: `test_decision_and_transition_operations_are_never_provider_computation` / `test_aiop_request_operations_are_exactly_provider_computation` (table-driven against the architecture's own AI-prohibition facts); `test_no_entry_is_external_effect_or_disclosure`; `test_unknown_operation_id_resolves_to_none_never_a_guess`; `test_the_module_touches_no_database_and_no_provider` (static).
- **MUTATION proof (manual, 3 guards):** (1) removed the duplicate-id raise → `test_operation_index_itself_raises_on_a_duplicate_id` failed (`DID NOT RAISE`), restored. (2) flipped `SELECT_PRIMARY_QUESTION`'s class to `PROVIDER_COMPUTATION` → two independent falsifiers failed, restored. (3) dropped `BEGIN_INVESTIGATION` entirely → `test_covers_every_session_position_action` failed, restored. Byte-diff confirmed clean restoration each time.
- **PRESERVATION / REGRESSION (increment 1's own, now superseded by §2B's final combined run).** Result at the time: 2084 passed, 2 skipped, 0 failed (2037 + 47).

**10 INVERSE SWEEP (E6).** No cached/client/re-observed value (no observation yet to read from); no DUPLICATED value (`session_position.actions` itself carries no execution-class/citation/data-input metadata — genuinely new structure); no PROMOTED value (static catalog data, not authority/evidence/decision); no BYPASSED value (no consumer exists yet; static import/parameter check confirms no path around a provider or Command). **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION (increment 1, superseded below).** FBR-PCPG-2's Session-scoped increment closed; the Workspace/Challenge-root/Decision slice remained open, disclosed, not silently dropped.

## 2B. Execution record — Increment 2 (Workspace/Challenge-root + Decision, 8 operations)

**1 RED (right reason).** New falsifiers were written first against the then-current module (31 new test functions, parametrized cases included), importing `ROOT_OPERATIONS` — which did not yet exist. Run before any implementation change:
```text
ImportError: cannot import name 'ROOT_OPERATIONS' from 'application.pcpg_operation_index'
```
— genuine RED, the correct reason (the relation's second slice does not exist yet). Confirmed before any repair line was written.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no consumable index entry exists for CREATE_WORKSPACE, CREATE_CHALLENGE,
                 ADD_MEMBER, GRANT/REVOKE_AUTHORITY_BINDING, CREATE_SESSION,
                 OPEN_DECISION_CONSIDERATION or RECORD_HUMAN_DECISION
CONSUMER         (future) R-06 candidate-delta formation, for any observed action naming one
                 of these operations -- today resolves UNKNOWN (I-04), correctly, but
                 incompletely relative to R-06's own "existing operation catalog" scope
PRODUCER         none (ABSENT for the entries themselves -- break type (a)); the underlying
                 Commands/AUTH-DEPs/capability projections they cite DO already exist (09/04/
                 `workspace_overview`/`challenge_detail`/`AllowAllWorkspaceCreationEligibilityChecker`)
FBR              FBR-PCPG-2 (00_FIELD.md §12), increment 2: the remaining slice, closing it
```

**3 HOME.** Same R-06 home as increment 1, plus three additional real producers consumed (never re-implemented): `application.inquiry_queries.workspace_overview` (`capabilities.createChallenge`/`addMember`, `viewer.isGovernanceRoot`), `application.inquiry_queries.challenge_detail` (`capabilities.openSession`/`grantSessionControl`), `application.workspace_creation_handler.AllowAllWorkspaceCreationEligibilityChecker`. For OPEN_DECISION_CONSIDERATION/RECORD_HUMAN_DECISION, the relevant "home" is the documented ABSENCE itself: `02_RELATIONS.md` R-07's own vocabulary, "a delta with no authoritative producer for its authority gives INDETERMINATE with reason `NO_AUTHORITATIVE_PRODUCER`" — confirmed by direct grep of `http_dispatch.py` (only `_decision_view_body` exists; no `canDecide`-shaped projection anywhere) and by `human_decision_handler.py`'s own docstring (AUTH-DEP-DEC-001/002 checked fresh only at commit time).

**4 REPAIR** (2 files extended, 0 new files).
- `packages/application/pcpg_operation_index.py`:
  - `OperationIndexEntry.readiness_producer` widened from `str` to `str | None` (R-07's `NO_AUTHORITATIVE_PRODUCER` honestly encoded, not a placeholder).
  - New field `http_route: tuple[str, str] | None` — `(method, path)` exactly as `ROUTES` spells it, or `None` when no HTTP route wires the operation yet (disclosed for OPEN_DECISION_CONSIDERATION, not silently omitted).
  - Three new named producer constants: `READINESS_PRODUCER_WORKSPACE_OVERVIEW`, `READINESS_PRODUCER_CHALLENGE_DETAIL`, `READINESS_PRODUCER_WORKSPACE_ELIGIBILITY`.
  - `ROOT_OPERATIONS`: 8 entries (CREATE_WORKSPACE, CREATE_CHALLENGE, ADD_MEMBER, GRANT_AUTHORITY_BINDING, REVOKE_AUTHORITY_BINDING, CREATE_SESSION, OPEN_DECISION_CONSIDERATION, RECORD_HUMAN_DECISION). Every citation copied verbatim from the real handler module docstrings (`workspace_creation_handler.py`, `challenge_creation_handler.py`, `membership_operations_handler.py`, `authority_binding_handler.py`, `session_creation_handler.py`, `human_decision_handler.py`); every `data_inputs` tuple copied verbatim from the real Pydantic body models (`apps/api/src/nquiry_api/http/{workspaces,inquiry,commands}.py`) and cross-checked against `ROUTES`' own tested bodies. GRANT_AUTHORITY_BINDING and REVOKE_AUTHORITY_BINDING both cite `workspace_overview` regardless of which scope (WORKSPACE/CHALLENGE/SESSION) the binding itself targets — proven, not assumed, by §6 below.
  - `operation_index()`/`resolve_operation()` now iterate `(*SESSION_SCOPED_OPERATIONS, *ROOT_OPERATIONS)` — one combined catalog, duplicate-id guard now spans both groups.
  - Module docstring rewritten to describe the full, closed catalog (no longer "first increment").
- `tests/e2e/test_pcpg_operation_index.py`: 31 new falsifiers (§3), plus one existing WU-2 test corrected (`test_covers_every_session_position_action` re-scoped to compare against `SESSION_SCOPED_OPERATIONS` specifically, since `operation_index()` now also carries `ROOT_OPERATIONS` — a real, necessary fix, not a weakening: the test's own claim ("covers every session_position action") is unchanged; only its subject changed from "the whole catalog" to "the session-scoped half of the catalog" it was always actually about).
- Two `ruff` line-length nits (>100 cols) in the new test code, fixed by wrapping — no semantic change; `ruff check`/`ruff format --check` clean afterward.

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `workspace_overview` / `challenge_detail` / `session_position` | NOT AFFECTED | Read-only consumption in all three cases; nothing in any of them changed. |
| `workspace_creation_handler.AllowAllWorkspaceCreationEligibilityChecker` | NOT AFFECTED | Cited by name/import-existence only, never called. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched. |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` (WU-1's own coverage guard) | NOT AFFECTED | No new HTTP route exists in this Work Unit; its own `ROUTES` table is read-only reused as a completeness oracle, never written to. |
| `human_decision_handler.open_decision_consideration` | NOT AFFECTED, confirmed still HTTP-unwired | Grepped: called only from `test_human_decision.py`/`test_proof_bundle_paths.py`; this Work Unit records that fact, does not change it. |
| `ai_gateway` / provider path | NOT AFFECTED | No import from the module reaches it (static falsifier, unchanged from increment 1). |
| WU-2's own increment-1 entries (`SESSION_SCOPED_OPERATIONS`) | NOT AFFECTED | Zero edits to any of the 18 existing entries; only the surrounding type (`readiness_producer: str | None`) widened, which is a superset, not a narrowing — `test_every_entry_names_the_real_readiness_producer` (increment 1's own test) still passes unmodified. |

**6–9 PROOFS.**
- Local: `ruff check packages/application/pcpg_operation_index.py tests/e2e/test_pcpg_operation_index.py` clean; `ruff format --check` clean; `mypy packages/application/pcpg_operation_index.py` — 0 issues; `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` — all PASS; migrations unchanged (none added).
- **Completeness proof (route-based, not `session_position`-based — this slice has no single shared surface):** `test_root_operations_route_map_is_exhaustive_against_the_proven_sweep` reuses `test_pfc_f09_2_isolation_sweep.ROUTES` (already proven exhaustive against `app.routes` by that file's own `test_the_sweep_covers_every_route`) as the completeness oracle: every non-Session, non-ingress POST Command route is claimed by exactly one of {the 17 session-dedicated routes, the 7 `ROOT_OPERATIONS` routes (GRANT_AUTHORITY_BINDING's route is deliberately shared with GRANT_SESSION_CONTROL's, both real, both provable)} — set equality, not a subset either way.
- **Per-entry proof:** `test_every_routed_root_entry_names_its_real_http_route` (7 routed entries) confirms each entry's own `http_route` field matches its real route, independently of the completeness test above (the two catch different defect classes, both exercised by mutation, §mutation 3 below). `test_open_decision_consideration_has_no_http_route_by_disclosed_design` confirms the 8th entry's `http_route is None` AND that the underlying function genuinely exists (`importlib`), proving "unwired" rather than "nonexistent."
- **Producer honesty proof:** `test_every_root_entry_producer_is_real_or_honestly_absent` — for the 6 entries with a producer, `importlib`-checks it really exists; for the 2 without (OPEN_DECISION_CONSIDERATION, RECORD_HUMAN_DECISION), asserts `readiness_producer is None` AND that the R-07 citation is present — never silently omitted.
- **Equivalence (adversarial) proof:** `test_governance_root_fact_never_diverges_across_three_projections` — against a REAL Workspace/Challenge/Session (via `f03_support.generating_context`), for both a real governance-root actor (`ctx["owner"]`) and a real non-root actor (`ctx["fac"]`), proves `workspace_overview.viewer.isGovernanceRoot`, `workspace_overview.capabilities.addMember.available`, `challenge_detail.capabilities.grantSessionControl.available` and `session_position.actions.GRANT_SESSION_CONTROL.available` are never four divergent facts — all four derive from the identical `_holds(..., WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws)` call in `inquiry_queries.py` (read directly, not assumed). This is the proof that justifies citing `workspace_overview` as GRANT/REVOKE_AUTHORITY_BINDING's producer regardless of the binding's own target scope.
- **Classification proof:** `test_all_root_entries_are_human_command` (table check against 04 AUTH-DEP-SEL-*/HD-25/26, mirroring increment 1's own pattern for the session-scoped half).
- **Cross-group duplicate proof:** `test_no_duplicate_operation_ids_across_the_full_catalog` (static) and `test_root_operation_index_itself_raises_on_a_cross_group_duplicate` (direct exercise of the runtime guard, a collision spanning the two groups — increment 1's own duplicate test only ever injected a same-group collision).
- **Catalog-size proof:** `test_operation_index_now_covers_the_full_catalog_size` (18 + 8 = 26, asserted directly, not inferred).
- **MUTATION proof (manual, 5 guards, this increment):**
  1. Flipped `CREATE_WORKSPACE`'s class to `PROVIDER_COMPUTATION` → `test_all_root_entries_are_human_command` failed. Restored; byte-diff clean.
  2. Set `CREATE_WORKSPACE`'s `readiness_producer` to `None` (should be real) → `test_every_root_entry_producer_is_real_or_honestly_absent[CREATE_WORKSPACE]` failed (`assert None is not None`). Restored; byte-diff clean.
  3. Corrupted `GRANT_AUTHORITY_BINDING`'s `http_route` to a fake path → `test_every_routed_root_entry_names_its_real_http_route[GRANT_AUTHORITY_BINDING-]` failed; the separate exhaustiveness test (built from its own independent route table, not the entry) correctly did NOT fail — confirming the two completeness tests catch genuinely different defect classes, as designed. Restored; byte-diff clean.
  4. Removed the `OPEN_DECISION_CONSIDERATION` entry entirely → two independent falsifiers failed (`test_open_decision_consideration_has_no_http_route_by_disclosed_design`: `entry is None`; `test_operation_index_now_covers_the_full_catalog_size`: `7 == 8` false). Restored; byte-diff clean.
  5. Removed the duplicate-id raise from `operation_index()` → both the increment-1 duplicate test AND the new cross-group duplicate test failed (`DID NOT RAISE`), proving the shared guard protects both groups. Restored; byte-diff clean.
  All 5 mutations confirmed via `sha256sum`/`diff -q` byte-identical restoration to the pre-mutation file after each.
- **PRESERVATION / REGRESSION — FINAL, AUTHORITATIVE RUN (this Work Unit's own, superseding increment 1's interim number).** Protocol: (1) `git status --short`/`git diff` recorded with the COMPLETE final tree already in place (1 modified file — the WU-1 documentation fix — and 3 new files, all three of this Work Unit's own); tracked-diff SHA-256 `efca17c59e895ae46ddd81fce0d2ea729210d00b2ddcf8b0bd83c3585d3e934a`, each untracked file's own content hash recorded. (2) The full repository suite (`python -m pytest -q`, no path filter — every test directory, not just `tests/e2e/`) started only after that tree was complete. (3) No file was modified while it ran (detached background process, watched to completion, zero intervening edits). (4) After completion: `git status --short`/`git diff` re-recorded — **identical file list**; tracked-diff SHA-256 **`efca17c59e895ae46ddd81fce0d2ea729210d00b2ddcf8b0bd83c3585d3e934a`, byte-identical**; all three untracked files' content hashes **unchanged**. Result: **2102 passed, 15 skipped, 0 failed, in 1955.35s (0:32:35)** — zero errors, zero failures anywhere in the repository, not only in the PCPG suite (the 15 skips are the pre-existing, disclosed real-stack/extra-service skips this session has consistently seen throughout the PFC field, unrelated to this Work Unit). `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
operation_id         <- session_position.actions key (increment 1) OR a real Command name    -- canonical,
                          cited against a real handler module (increment 2)                       sourced (a/c)
architecture_ref      <- copied verbatim from a real handler docstring                        -- canonical, sourced (a/c)
execution_class       <- this Field's own §4 vocabulary, "effect not verb", applied to real   -- versioned SFE rule (c)
                          AI-prohibition facts already stated in those same docstrings
readiness_producer    <- a literal string checked live via importlib, OR None + an explicit   -- canonical, sourced (a),
                          R-07 NO_AUTHORITATIVE_PRODUCER citation when genuinely absent           or an honest absence
http_route             <- (method, path) read from the proven-exhaustive ROUTES table, OR     -- canonical, sourced (a),
                          None + a grep-confirmed "called only from tests" fact                   or an honest absence
data_inputs            <- copied verbatim from the real, already-tested Pydantic body models   -- canonical, sourced (a)
                          / ROUTES wire-contract bodies
```
No CACHED value (every producer/route check re-imports or re-reads live, nothing is memoized across a call boundary this module owns). No DUPLICATED value: neither `workspace_overview` nor `challenge_detail` nor the eligibility checker carries execution-class/citation/data-input metadata of its own — this index adds structure that did not exist anywhere else, without re-implementing the AVAILABILITY computation those surfaces already own (proven not to diverge from them, §6 equivalence proof, rather than assumed). No PROMOTED value: a `None` `readiness_producer`/`http_route` is never silently upgraded to a guessed value anywhere in this module or its tests. No BYPASSED value: the module still has no consumer (R-06 not materialized); the static falsifier (unchanged from increment 1) confirms no `ports`/`connection`/`db` parameter and no provider import exists anywhere in it, including the 8 new entries. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION — COMBINED, FINAL.** FBR-PCPG-2 is now **fully closed**: all 26 real operations the existing homes (09 Commands, 03 transitions, 04 AUTH-DEPs, 08 AIOP contracts) define are catalogued, each with a real, checked `execution_class`, `architecture_ref`, `data_inputs`, and either a real, checked `readiness_producer`/`http_route` or an explicit, cited absence (never a guess, never silently dropped). R-06 (candidate-delta formation, not yet materialized) may now map ANY observed action naming a real NQUIRY operation to a catalog entry; an action naming anything else still correctly resolves UNKNOWN (I-04). **Next First Broken Relation:** R-05 (the local SIMPLIX semantic sweep, HA-PCPG-2's reproducible-rule-based constraint) against the now-complete catalog — explicitly the next step this Work Unit's own authorization names, not begun here. Not a Human Authority boundary; not a future Field.

## 3. Falsifier map (combined, 78 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_covers_every_session_position_action` | 1 | R-06 catalog completeness, session-scoped half, against the real producer |
| `test_no_duplicate_operation_ids` / `test_operation_index_itself_raises_on_a_duplicate_id` | 2 | I-20, session-scoped group |
| `test_every_entry_has_a_real_citation_shape` (×18) | 18 | every session-scoped entry cites a real architecture-shaped identifier |
| `test_every_entry_names_the_real_readiness_producer` (×18) | 18 | the cited producer really exists, session-scoped group |
| `test_decision_and_transition_operations_are_never_provider_computation` / `test_aiop_request_operations_are_exactly_provider_computation` | 2 | I-08, session-scoped group |
| `test_no_entry_is_external_effect_or_disclosure` / `test_execution_class_partition_is_exhaustive_and_matches_the_catalog_size` | 2 | 00_FIELD.md §3, session-scoped group |
| `test_unknown_operation_id_resolves_to_none_never_a_guess` | 1 | I-04 |
| `test_index_is_a_pure_function_no_hidden_state` | 1 | determinism, I-19 |
| `test_the_module_touches_no_database_and_no_provider` | 1 | P-01/I-16, static, whole module |
| `test_data_inputs_are_disjoint_from_the_universal_fields` | 1 | session-scoped group never restates `expectedVersion` |
| `test_root_operations_route_map_is_exhaustive_against_the_proven_sweep` | 1 | R-06 catalog completeness, root slice, against the proven-exhaustive ROUTES oracle |
| `test_every_routed_root_entry_names_its_real_http_route` (×7) | 7 | each routed root entry's `http_route` matches the real route |
| `test_open_decision_consideration_has_no_http_route_by_disclosed_design` | 1 | honest absence, not a gap left unrepresented |
| `test_every_root_entry_has_a_real_citation_shape` (×8) | 8 | every root entry cites a real architecture-shaped identifier |
| `test_every_root_entry_producer_is_real_or_honestly_absent` (×8) | 8 | real producer existence OR R-07-cited honest absence |
| `test_all_root_entries_are_human_command` | 1 | I-08/HD-25/26, root group |
| `test_no_duplicate_operation_ids_across_the_full_catalog` / `test_root_operation_index_itself_raises_on_a_cross_group_duplicate` | 2 | I-20, across both groups |
| `test_operation_index_now_covers_the_full_catalog_size` | 1 | 18 + 8 = 26, asserted directly |
| `test_root_entries_have_no_expected_version_in_data_inputs` | 1 | root group never restates `expectedVersion` |
| `test_governance_root_fact_never_diverges_across_three_projections` | 1 | the single-authority-fact equivalence GRANT/REVOKE_AUTHORITY_BINDING's shared producer citation depends on |

(47 + 31 = 78; matches the collected test count exactly.)

## 4. Deliberate exclusions (not defects; later Work Units)

- R-05 (SIMPLIX semantic sweep): no clause, action or target is derived from any raw text in this Work Unit. This module has no input from a raw intent at all.
- R-06 (candidate delta formation) itself: this index is what R-06 will read from; R-06's own delta-record construction, dependency ordering and IMPLIED-delta logic are not materialized here.
- No wiring into the PCPG observation ingress (`pcpg_observation.py`/`http_pcpg.py`): the ingress response still carries `governanceObservation: null`, honestly, since consuming this index is R-06's job, not this one's.
- OPEN_DECISION_CONSIDERATION's own HTTP wiring: disclosed as `SUCCESSOR_NOT_BUILT` (§2B), not solved here — adding a route is a separate, real Work Unit with its own authorization, not implied by cataloguing the Command that already exists.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW — FBR-PCPG-2 CLOSED IN FULL.** All 26 real NQUIRY operations (18 Session-scoped + 8 Workspace/Challenge-root/Decision) are catalogued, independently falsified (78/78), mutation-proven (8/8 guards killed and restored across both increments, byte-identical restoration confirmed each time), and proven repository-wide preservation-clean: fresh full-repository regression **2102 passed, 15 skipped, 0 failed**, tree verified byte-identical before/after. Not yet committed, not yet tagged, not yet pushed — the canonical Work Unit commit/checkpoint is the next step this Work Unit's own authorization names.
