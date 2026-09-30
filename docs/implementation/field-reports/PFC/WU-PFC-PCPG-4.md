# WU-PFC-PCPG-4 — R-03: Current Field reconstruction

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Field | WU-PFC-PCPG-4 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · PRE_CALL_PROMPT_GOVERNANCE (Architecture 26) |
| Colour / role | BLUE · application materialization |
| Human authorization | "PASS. WU-PFC-PCPG-3 is approved... Then run E1 / Field reconstruction against the new committed state and derive the next First Broken Relation. Do not choose R-03 or R-06 merely from this instruction. Let the current Field determine which relation is first. Continue autonomously with that relation under the same SFE discipline. Do not cross Human Authority. Do not begin any SEND path." (2026-09-30). |
| Predecessor | `pfc-integration` `057f205e47539d568083bfb6e94a31d1a1b28fa0` (`checkpoint-PFC-PCPG-3`, pushed). |
| State isolation | Same worktree/branch as prior PCPG Work Units. No migration (this Work Unit adds no schema; it composes existing read-only producers only). |
| E1 re-derivation (2026-09-30, against `checkpoint-PFC-PCPG-3`) | See §0 below — done in full, independently, not assumed. |
| Authorized delta (this Work Unit, disclosed scope) | R-03 ONLY: Actor context (role, governance-root fact, and the actor's own raw, current authority bindings — quoted from `list_current_bindings`, never filtered), Session context (state/version/fixture/proof-mode/actions, quoted verbatim from `session_position`, present only when a Session is named, UNRESOLVED — never a crash — when the named Session does not belong to the validated Workspace), two Field-wide static cited facts (HD-21's admitted AIOP scope; that no external dependency exists in NQUIRY today), and Provider context (environment + whether a route is configured, from `analysis_runtime`'s own configuration reader — never an invocation). "Data handling" (R-03's own "at minimum" bullet) is explicitly NOT a field: `00_FIELD.md` §7 itself states no classifier is materialized (GAP-11-006, FBR-PCPG-3, still OPEN) — fabricating a value would violate I-02. |
| Must become true | A pure function `reconstruct_field(ports, principal, *, workspace_id, session_id, now, environment) -> FieldSnapshot` exists, composing only real, already-proven producers; never derives authority, state or capability of its own; never depends on a raw intent (I-05). |
| Must remain true | `workspace_overview`, `session_position`, `AuthorityBindingRepository.list_current_bindings`, `analysis_runtime.runtime_from_environment` all unchanged; every existing route, Command, migration and test. |
| Must remain impossible | Any field value that diverges from its real producer's own value at the same basis (P-02, P-14, P-15); a crash (unhandled exception) for a named-but-foreign Session, where UNRESOLVED is the correct, defined failure state; a provider invocation of any kind; a cached/stale snapshot. |
| Falsifiers | `tests/e2e/test_pcpg_field_snapshot.py`: 17 cases. |

## 0. E1 re-derivation (independent, against `checkpoint-PFC-PCPG-3`)

**ROOT RELATION.** Before this Work Unit, of R-01…R-12: R-01/R-02 (ingress+scope) materialized (WU-1); R-05 (SIMPLIX) materialized (WU-3); R-06's operation-catalog half (the "consumable index") materialized (WU-2, FBR-PCPG-2) but R-06 itself (candidate-delta *formation*) is not. R-03 (Field reconstruction) and R-04 (Pulse) were both genuinely ABSENT — confirmed by repository search (`grep` for `FieldSnapshot`/`Pulse` outside docstrings/disclosures: zero hits; the only four `pcpg_*.py` files were `http_pcpg.py`, `pcpg_observation.py`, `pcpg_operation_index.py`, `pcpg_simplix.py`). R-03's own INPUT ("the validated scope, the actor, and the current time") is already fully produced by R-01/R-02; nothing later is its own prerequisite. R-04's INPUT is "the Field snapshot" — i.e. R-03's own output. R-06's INPUT (its own prose, not the diagram — see SFE CORRECTION below) is "the semantic observation and the Field snapshot" — i.e. R-05's and R-03's output. **R-03 was therefore the unique root**: both R-04 and R-06 name it as their sole remaining missing prerequisite, and R-03 itself had none.

**FBR CHAIN (before this Work Unit).**
```text
FBR-1  R-03 Current Field reconstruction   ABSENT (break type a)   needed by R-04, R-06, R-07
FBR-2  R-04 Field Pulse                    ABSENT (break type a)   needed by R-07, R-09 -- blocked on FBR-1
FBR-3  R-06 Candidate delta formation      ABSENT (break type a)   needed by R-07        -- blocked on FBR-1
```

**EXISTING-BYPASS REPORT.** Re-swept: `grep` for `ai_gateway` importers across `apps/api/src/nquiry_api/http/*.py` and `packages/application/*.py` returns only the pre-existing, already-governed `analysis_system.py`/`analysis_runtime.py`/`analysis_input.py` (the human-authorized BEGIN_ANALYSIS→AIOP-001/002 path) — unchanged since WU-1's own sweep. No new bypass introduced by WU-2 or WU-3.

**SFE CORRECTION.** `02_RELATIONS.md`'s own header ASCII diagram draws BOTH R-04 (pulse) and R-05 (semantic sweep) as flowing into R-06 ("R-03 field ─┬─► R-04 pulse ─┐ ... ├─► R-06 deltas"). R-06's own detailed section, below the diagram, states its INPUT as "the semantic observation and the Field snapshot" only — no mention of Pulse. This is a real discrepancy, not a restatement. The per-relation section is authoritative here (it is the detailed contract R-06's own PRECONDITION/OUTPUT/PROOF are written against; the diagram is an orientation aid), so this report treats R-06 as depending on R-03+R-05 only, not on R-04 — stated as a finding, not edited into the RED file.

**HUMAN AUTHORITY.** Neither R-03 nor (per the corrected reading) R-04/R-06 is Case 3: no open HA-* question governs any of the three (HA-PCPG-5 explicitly states "NQUIRY relations are not blocked" for R-03 in the real NQUIRY scope — only a non-NQUIRY domain producer would be gated). None blocks this Work Unit.

## 2. Execution record

**1 RED (right reason).** The falsifier suite (17 cases) was written first, importing `AI_CONTRACTS_ADMITTED`, `EXTERNAL_EFFECTS`, `FieldSnapshot`, `reconstruct_field` from `application.pcpg_field_snapshot`. Run against the unrepaired tree: `ModuleNotFoundError: No module named 'application.pcpg_field_snapshot'` — the correct reason. After implementation, one authoring bug (not a RED-authoring mistake): the outsider falsifier used `ctx["outsider"]` from `f03_support.generating_context`, which is a same-Workspace non-participant, not a cross-Workspace outsider — the same mistake WU-PFC-PCPG-1 made and fixed; corrected here the same way (`f03.new_workspace_with_member`). A second correction: the propagated exception for a genuine outsider is `QueryDenied("WORKSPACE_NOT_ACCESSIBLE")` (from `inquiry_queries._context`'s own uniform translation of `WorkspaceNotFoundError`/`NotAWorkspaceMemberError`), not the raw `NotAWorkspaceMemberError` the test first assumed — fixed, and the module's own docstring corrected to match. 17/17 passed after both fixes.

**2 FIRST BROKEN RELATION.**
```text
VISIBLE EFFECT   no composed Field snapshot exists for R-04/R-06/R-07 to consume
CONSUMER         (future) R-04 (Pulse), R-06 (candidate delta formation) -- not materialized here
PRODUCER         none (ABSENT -- break type (a))
FBR              R-03 (00_FIELD.md §10 timeline; 02_RELATIONS.md R-03), Current Field
                 reconstruction
```

**3 HOME.** `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md` R-03; each quoted fact's own real home (`00_FIELD.md` §7's Authoritative-predecessors table): `application.inquiry_queries.workspace_overview`/`session_position`, `persistence.authority_binding_repository.AuthorityBindingRepository.list_current_bindings`, `application.analysis_runtime.runtime_from_environment`.

**4 REPAIR** (2 new files).
- `packages/application/pcpg_field_snapshot.py`: `AuthorityFact`, `ActorContext`, `SessionContext`, `ProviderContext`, `FieldSnapshot`, `reconstruct_field()`. Two static, cited Field-wide constants (`AI_CONTRACTS_ADMITTED = {"AIOP-001", "AIOP-002"}` — HD-21's own admitted scope; `EXTERNAL_EFFECTS = frozenset()` — `00_FIELD.md` §3's own Pulse note, verbatim). Every other field is a direct quote of a real producer's return value at the same call, never re-derived: `workspace_overview`'s own `viewer` block for role/governance-root; `AuthorityBindingRepository.list_current_bindings`'s own rows, unfiltered, for the actor's authority facts (P-14: no parallel authority model — proven by an equivalence falsifier parametrized over an actor whose only real binding is WORKSPACE-scoped and one whose only real binding is SESSION-scoped, so a scope-based filter cannot hide behind an under-specified test); `session_position`'s own `session`/`actions` blocks, quoted verbatim, when a Session is named; `runtime_from_environment`'s own `environment`/`available` for Provider context, read for CONFIGURATION only (`.gateway` is never dereferenced to invoke anything — proven statically). A named Session that does not belong to the validated Workspace becomes `"session"` in `unresolved` (R-03's own FAILURE STATE), never an unhandled exception; a genuinely non-member actor's `QueryDenied` (I-06's uniform denial, raised inside `workspace_overview` itself) propagates unchanged, since R-03's own PRECONDITION is "R-02 succeeded" and a caller without a validated scope has violated that precondition, not discovered a new case.
- `tests/e2e/test_pcpg_field_snapshot.py`: 17 falsifiers (§3).

**5 PROPAGATION.**

| Surface | Status | Reason |
|---|---|---|
| `workspace_overview` / `session_position` / `list_current_bindings` / `runtime_from_environment` | NOT AFFECTED | Read-only consumption in every case; nothing in any of them changed. |
| Every existing route/Command | NOT AFFECTED | No route added, no dispatch module touched; R-03 has no HTTP surface in this Work Unit. |
| `pcpg_simplix.py` / `pcpg_operation_index.py` / `pcpg_observation.py` | NOT AFFECTED | No import from this module reaches any of them; R-03 and R-05 remain independent, siblings under a future R-06, per the SFE correction in §0. |
| `ai_gateway` / provider path | NOT AFFECTED | `analysis_runtime`'s own configuration reader is consumed; `.gateway` is read for existence only, never called (static falsifier, §3). |

**6–9 PROOFS.**
- Local: `ruff check` / `ruff format --check` clean; `mypy` (new module) 0 issues (two `cast()` uses, documented, needed because `workspace_overview`/`session_position` return loosely-typed `dict[str, object]`); `check_architecture_dependencies.py` / `check_provider_sdk_imports.py` / `check_test_only_imports.py` all PASS; no migration.
- Producer proof: `test_actor_context_role_matches_the_real_workspace_overview_exactly`, `test_actor_context_authority_bindings_equal_the_real_repository_output` (×2, WORKSPACE- and SESSION-scoped actors), `test_session_context_matches_session_position_exactly` — each a direct equality against the real producer's own live return value, not a hardcoded expectation.
- Consumer proof: none yet — R-04/R-06 do not exist. Readiness-to-be-consumed: every field's own docstring cites its real producer by name.
- Adversarial proof: `test_a_non_member_is_denied_before_any_field_fact_is_read` (I-06, a genuine cross-Workspace outsider via `new_workspace_with_member`); `test_a_session_of_another_workspace_is_unresolved_never_a_crash` (R-03's own FAILURE STATE); `test_provider_context_is_unresolved_on_a_forbidden_mock_configuration` (HD-19); `test_reconstruct_field_takes_no_raw_intent_parameter` (I-05, static signature check); `test_the_module_never_invokes_a_provider_only_reads_configuration` (I-16/B-08, static AST check: no `.generate(`/`.invoke(`/`.send(`/`.call(` call anywhere, no `ai_gateway.adapters`/provider-SDK import).
- **MUTATION proof (manual, 5 guards):**
  1. Removed the `QueryNotFound` catch around `session_position` (let it propagate) → `test_a_session_of_another_workspace_is_unresolved_never_a_crash` failed with an unhandled `QueryNotFound`. Restored; byte-diff clean.
  2. Silently filtered the quoted authority bindings to `scope_type == "WORKSPACE"` only → initially NOT caught (the first version of the equivalence test used only the owner, whose one real binding happens to be WORKSPACE-scoped) — the test itself was strengthened to parametrize over an actor whose only real binding is SESSION-scoped, which then correctly failed (`0 == 2`) against the same mutation. Restored; byte-diff clean. (This sequence — a mutation not caught, the test corrected to be a genuine adversarial case, the same mutation then caught — is recorded here in full rather than only showing the final passing run, per this Field's own proof discipline: a mutation proof that silently strengthens itself without disclosure is not a proof.)
  3. Removed the `unresolved.append("provider")` on a forbidden MockProvider configuration → `test_provider_context_is_unresolved_on_a_forbidden_mock_configuration` failed (`'provider' in ()` false). Restored; byte-diff clean.
  4. Dropped `AIOP-002` from `AI_CONTRACTS_ADMITTED` → `test_ai_contracts_admitted_is_the_real_hd21_scope` failed. Restored; byte-diff clean.
  5. Hardcoded `SessionContext.state` to a literal instead of quoting `session_position`'s own value → `test_session_context_matches_session_position_exactly` failed (`'QUESTION_CAPTURE' == 'QUESTION_GENERATION'` false). Restored; byte-diff clean.
  Final restore hash `d10817d092ea33562471ccb265ded3f59b3e4c922245355903e0c25cccd268fb` confirmed byte-identical to the pre-mutation baseline after every mutation.
- **PRESERVATION / REGRESSION.** Combined PCPG suite (field_snapshot + simplix + operation_index + observation_ingress + isolation_sweep): **297 passed, 0 failed** (17 + 90 + 78 + 28 + 84). **FINAL, AUTHORITATIVE FULL-REPOSITORY RUN:** started only after `git status`/`git diff` confirmed the complete final tree (0 modified, 3 new files, all this Work Unit's own, including this report); tracked-diff SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff), each untracked file's own content hash recorded before starting. No file was modified while it ran (detached background process, watched to completion, zero intervening edits). After completion: identical file list; tracked-diff SHA-256 **unchanged**; all three untracked files' content hashes **unchanged**. Result: **2209 passed, 15 skipped, 0 failed, in 2109.35s (0:35:09)** — exactly 2192 (WU-3's own closing count) + 17 (this Work Unit's falsifiers), confirming nothing else moved. `TREE_UNCHANGED_DURING_PROOF: CONFIRMED`.

**10 INVERSE SWEEP (E6).**
```text
actor.role / is_governance_root  <- workspace_overview's own `viewer` block, quoted          -- canonical, sourced (a)
actor.authority                  <- AuthorityBindingRepository.list_current_bindings's own   -- canonical, sourced (a)
                                     rows, quoted whole, never filtered/re-derived
session.*                        <- session_position's own `session`/`actions` blocks,       -- canonical, sourced (a)
                                     quoted verbatim, or absent/UNRESOLVED (never guessed)
ai_contracts_admitted /          <- two static, cited facts THIS Field's own architecture      -- versioned SFE fact (c),
  external_effects                  text already states (HD-21; 00_FIELD §3) -- no producer       self-disclosed as such
                                     call exists for either, disclosed as such
provider.*                       <- analysis_runtime.runtime_from_environment's own            -- canonical, sourced (a)
                                     configuration read, never an invocation
```
No CACHED value: every field is read fresh on each call (no module-level state, no memoization; `test_the_snapshot_is_identical_for_two_calls_at_the_same_basis` proves determinism without needing or implying a cache). No DUPLICATED value in the harmful sense (I-02/I-20: "a second, divergent definition"): every quoted field is read FROM the same real producer call the equivalence falsifiers directly compare against, never independently recomputed by a separate code path that could drift. No PROMOTED value: `FieldSnapshot` and its nested types are documented, and used, purely as stratum-1 canonical-fact composition — nothing here is labeled or treated as authority, evidence, a decision or a capability. No BYPASSED value: the module has no consumer yet (R-04/R-06 not materialized); the static AST falsifier confirms no forbidden method call (`generate`/`invoke`/`send`/`call`) and no import of an `ai_gateway` adapter or a provider SDK exists anywhere in it. **VERDICT: CLEAN.**

**11 FIELD RECONSTRUCTION.** R-03 (Current Field reconstruction) is materialized and closed for its own disclosed scope. Re-running E1 against this now-committed state: **R-04 (Field Pulse) and R-06 (candidate delta formation) are both now unblocked** — each depends only on R-03 (and, for R-06, also R-05 — both now real) — and neither depends on the other (per the SFE correction in §0: R-06's own written INPUT does not name Pulse, despite the header diagram's more compressed drawing). They are genuine siblings, not a strict chain. Tie-broken on evidence, not preference: R-04's own header names two consumers (`R-07, R-09`) against R-06's one (`R-07`) — R-04 is needed by strictly more of what still remains, so **R-04 is the next First Broken Relation**, not assumed, derived. Not a Human Authority boundary, not a future Field.

## 3. Falsifier map (17 cases)

| Falsifier | Cases | Proves |
|---|---|---|
| `test_actor_context_role_matches_the_real_workspace_overview_exactly` | 1 | P-02/P-14: actor role/governance-root quoted, not re-derived |
| `test_actor_context_authority_bindings_equal_the_real_repository_output` (×2: owner, fac) | 2 | P-14: no parallel authority model, across WORKSPACE- and SESSION-scoped actors |
| `test_a_non_member_is_denied_before_any_field_fact_is_read` | 1 | I-06: identity/scope before any fact |
| `test_session_context_is_absent_when_no_session_is_named` | 1 | Session context is conditionally present, never fabricated |
| `test_session_context_matches_session_position_exactly` | 1 | P-02/P-14: session context quoted, not re-derived |
| `test_a_session_of_another_workspace_is_unresolved_never_a_crash` | 1 | R-03's own FAILURE STATE: UNRESOLVED, never an unhandled exception |
| `test_ai_contracts_admitted_is_the_real_hd21_scope` / `test_external_effects_is_empty_matching_00_field_section_3` | 2 | the two static, cited Field-wide facts are exactly right |
| `test_snapshot_carries_the_same_static_facts_every_time` | 1 | determinism of the static facts |
| `test_provider_context_reflects_a_real_test_environment` / `..._is_unresolved_on_a_forbidden_mock_configuration` / `..._with_no_provider_configured_is_resolved_and_false` | 3 | Provider context reflects real configuration, including HD-19's dev-only MockProvider rule |
| `test_the_snapshot_is_identical_for_two_calls_at_the_same_basis` | 1 | I-05/I-19: no dependency on a raw intent; determinism |
| `test_reconstruct_field_takes_no_raw_intent_parameter` | 1 | I-05, static signature proof |
| `test_the_module_never_invokes_a_provider_only_reads_configuration` | 1 | I-16/B-08, static AST proof |
| `test_field_snapshot_equality_is_structural_not_identity` | 1 | the frozen-dataclass shape the determinism falsifier depends on |

## 4. Deliberate exclusions (not defects; later Work Units)

- Data handling (per-source data classes): FBR-PCPG-3's own unmaterialized scope (GAP-11-006 still OPEN). No field fabricated.
- R-04 (Pulse): a separate relation, derived next in §0/§11, not begun here.
- R-06 through R-12: not materialized; this module has no consumer yet.
- Multi-object scopes beyond one optional Session (e.g. a Challenge-only or cross-Session observation): R-03's own OUTPUT is "at minimum" Actor + Session context; the real, already-supported NQUIRY shapes (Workspace-only, Workspace+Session) are covered; a Challenge-scoped variant is a straightforward, disclosed extension for whichever future Work Unit needs it, not built speculatively here.

## 5. Resulting status

**WORK_UNIT_READY_FOR_HUMAN_REVIEW.** R-03 (Current Field reconstruction) is materialized for its own disclosed scope, independently falsified (17/17), mutation-proven (5/5 guards killed and restored — one mutation's first pass revealed a genuine test-strength gap, disclosed and corrected in §2, then re-proven caught), and proven repository-wide preservation-clean (2209 passed / 15 skipped / 0 failed, tree verified byte-identical before/after). Not committed, not tagged, not pushed.
