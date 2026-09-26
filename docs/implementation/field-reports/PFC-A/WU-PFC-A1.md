# WU-PFC-A1: Challenge Frame Completion

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND
RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Work Unit header (bound before the Delta, §23.4)

```text
WORK UNIT ID          WU-PFC-A1
PARENT FIELD          NQUIRY_PRODUCT_FUNCTION_COMPLETION
CHILD FIELD           PFC-A Challenge Frame (extension of F02 Inquiry Context)
COLOR / ROLE / MODEL  RED · backend / API / application / persistence · Claude Opus 5.5
HUMAN AUTHORIZATION   "WU-PFC-A1 IS AUTHORIZED." (2026-09-26); governing
                      architecture: branch pfc-architecture, Architecture 25
EXECUTION INVARIANT   §23
CHAIN                 FIELD → RELATION → STATE → BOUNDARY → AUTHORITY
                      → AUTHORIZED DELTA → PROOF → RECONSTRUCTION
```

| Item | Bound value |
|---|---|
| Current state | Branch `pfc-a1-challenge-frame` at `1eb3799` (= `origin/pfc-architecture`, signed). Its code is identical to published F03 `c9d86ba`; it differs only in documentation and `assets/logo/*`. Migration head `f6b2c4d9a318`. Field status F03 = published predecessor. |
| Baseline evidence | Unmodified tree: live suite **1535 passed, 2 skipped** (7:53); no-DB suite **808 passed, 729 skipped** (measured as 808 / 752 with the falsifier file present; see §9). |
| Recoverable predecessor | `origin/pfc-architecture` `1eb3799` (based on `master-2026-09-26` `6e7e402`). F04 is not a predecessor of this Work Unit (PFC-A does not depend on AI); its checkpoint `checkpoint-F04-backend-review-pass` → `b31264e` is untouched. |
| State isolation | Worktree `worktrees/pfc-a1`; PostgreSQL database `nquiry_pfc_a1_test` (created for this Work Unit, roles applied, migrated to head, `verify_migrations` PASS). The main checkout, BLUE, CYAN and the F04 databases are not used. |
| Authoritative home | 09 §25 (Challenge data contract names `context`, `desired_outcome`, `constraints`, `stakeholders`; §25.2: no invented `status`); 09 §80 (Challenge API: `POST`/`GET /workspaces/{w}/challenges[/{c}]`, `CMD_CREATE_CHALLENGE`, Facilitator source right, no Owner fallback); 02 §9 (Challenge). |
| Authorized Delta | Complete HTTP INPUT → APPLICATION COMMAND → DOMAIN → PERSISTENCE → READ PROJECTION / API OUTPUT for the four frame fields. Backend, API, application, persistence. Projections only where directly derivable. **Not in scope:** CYAN redesign, a status field, Emotional Temperature, any update command, any AI operation, F04/F05 behaviour, schema change. |
| Producers / consumers | Producer: `POST /workspaces/{w}/challenges` → `dispatch_create_challenge` → `create_challenge` (`CMD_CREATE_CHALLENGE`) → `ChallengeRepository` → `challenges`. Consumers: GET detail (`challenge_detail`), overview list, session-position header, legacy session view, `challenge_query.get_challenge`, CYAN client. |
| Boundary / authority | BND-001/002/003 (identity, workspace, membership) plus role authority `AUTH-DEP-CH-001` (`_CHALLENGE_CREATOR_ROLES = {FACILITATOR}`); unchanged. |
| Must become true | The four fields enter through `CMD_CREATE_CHALLENGE` over HTTP and return through the authoritative GET projection exactly as stored. |
| Must remain true | Title required; Facilitator-only creation (Owner and Contributor denied, no Owner fallback); idempotency (replay and key collision); description behaviour; F02/F03 behaviour; domain semantics; Architecture 25 invariants; CYAN visuals. |
| Must remain impossible | An invented Challenge status (NQ-GAP-018); an AI rewrite; a new AI operation; a new authority path; new role semantics; unrelated schema expansion; F04/F05 behaviour; a CYAN redesign; silent cross-field mutation; a denied request that stores anything. |
| Falsifiers | `tests/e2e/test_pfc_a1_challenge_frame.py` (23 cases, mapped in §4). |
| Human review required | No material CYAN change is made (§5, CYAN row), so human visual review is not required. Human review of this record is still required before the next dependent Work Unit (§21). |
| Stop conditions | A Case 3 (for example a visual decision for CYAN); scope expansion; a missing predecessor; publication authority (not granted: no commit, push or tag). |

## 2. Execution record (§23.5)

### 1 FALSIFIER RED

The falsifier file was written against the unmodified tree. Result: **16 failed, 7 passed**. The 7 that pass are preservation tests, which must be green before and after: title, authority ×3, CYAN shape, description and audit provenance. Every failure was checked for the right reason:

| Falsifier | RED reason (observed) |
|---|---|
| round trip | DB value `None` versus the sent value: dropped at dispatch |
| each field independently ×4; blank ×4; no status / no new fields | `KeyError` on the missing projection keys |
| non-text ×4 | `200` instead of `400`: the extra key was silently ignored by the body model |
| idempotency covers the frame | `committed` instead of `rejected`: the frame never reached the payload fingerprint |

The first draft of `test_status_or_unknown_input_is_not_honoured` failed for the **wrong** reason: its helper mapped `status` through the wire table and raised `KeyError`. The test was corrected to send the unknown keys directly. After the correction it was re-run and belongs to the preservation set: unknown keys are ignored, before and after.

### 2 FIRST BROKEN RELATION

```text
VISIBLE EFFECT  a Facilitator's context / desired outcome / constraints / stakeholders
                never appear on the Challenge
CONSUMER        GET /workspaces/{w}/challenges/{c} (challenge_detail)
RELATION        HTTP body → application command
PRODUCER        CreateChallengeBody {title, description} (extra keys silently ignored);
                dispatch_create_challenge passed context/desired_outcome/constraints/
                stakeholders = None
AUTHORITY       unchanged (Facilitator role, AUTH-DEP-CH-001)
STATE           domain Challenge, handler payload (idempotency fingerprint), repository
                and table already carried all four fields
FIRST BROKEN    HTTP INPUT → APPLICATION COMMAND (apps/api …/http/inquiry.py,
RELATION        packages/application/http_f02.py). Second break: READ PROJECTION
                (packages/application/inquiry_queries.py challenge_detail returned
                only challengeId/title/description/createdAt).
```

This is FBR-PFC-06 of the Understanding Report ("The Challenge wire contract drops four frame fields").

### 3 AUTHORITATIVE HOME

09 §25 (data contract) and 09 §80 (Challenge API). Both are already materialized in the domain, handler and persistence layers. The break sat only in the HTTP adapter, the dispatch and the detail projection.

### 4 MINIMUM LEGITIMATE ROOT REPAIR

| File | Change |
|---|---|
| `apps/api/src/nquiry_api/http/inquiry.py` | `CreateChallengeBody` gains `context`, `desiredOutcome`, `constraints`, `stakeholders` (`str \| None = None`, camelCase wire names). The route passes them to the dispatch. |
| `packages/application/http_f02.py` | `dispatch_create_challenge` accepts the four fields and passes them through `_frame_text` into `create_challenge` (previously `None`). |
| `packages/application/inquiry_queries.py` | The `challenge_detail` challenge block gains `context`, `desiredOutcome`, `constraints`, `stakeholders` from the domain Challenge. The four existing keys are unchanged. |

26 insertions and 4 deletions. No migration, domain, handler, repository, authority or frontend change.

**Case-2 choice (local and non-semantic; recorded here):**
- A frame value is stored byte-exact, with no trimming. This is "exactly as stored"; `title` and `description` keep their F02 strip behaviour.
- A missing, `null`, empty or whitespace-only value means "not provided" and is stored as `NULL`.
- A non-string value is a malformed body: `400 {"kind":"rejected","reasonCode":"MALFORMED_REQUEST_BODY"}`, and nothing is stored.

### 5 PROPAGATION

| Item | Status | Reason |
|---|---|---|
| HTTP body model `CreateChallengeBody` | **AFFECTED** | First broken relation (repaired). |
| `dispatch_create_challenge` | **AFFECTED** | First broken relation (repaired). |
| GET detail projection `challenge_detail` | **AFFECTED** | Authoritative Challenge projection (09 §80); additive keys. |
| Domain `Challenge` (02 §9) | NOT AFFECTED | Already carries the four fields as `str \| None`; title invariant unchanged. |
| Handler `create_challenge` / `CreateChallengePayload` | NOT AFFECTED | Already accepts the four fields and includes them in the idempotency fingerprint; now fed real values. |
| Authority `AUTH-DEP-CH-001` / BND-001..003 | NOT AFFECTED | No code path changed; re-proven by the authority falsifiers. |
| Repository / `challenge_from_row` / `challenges` table / migrations | NOT AFFECTED | Already mapped; no schema change; head stays `f6b2c4d9a318`. |
| Audit / command log / commit / outbox | NOT AFFECTED | The same single governed commit; re-proven by the audit-provenance falsifier. |
| Workspace overview challenge list | NOT AFFECTED | A list summary; keeps its exact key set (asserted). 09 names no frame on the list. |
| Session position challenge header | NOT AFFECTED | Session context header, not the Challenge API. Adding the frame there is not required for the relation and would be a projection choice without an architecture mandate. |
| Legacy PKG session view (`http_dispatch.py`) / `challenge_query.get_challenge` | NOT AFFECTED | Returns the domain object or its own view; not an HTTP Challenge contract of 09 §80. |
| `scripts/seed_local_demo.py` | NOT AFFECTED | Calls the handler directly with `None`; still valid. |
| Web package in this tree (`apps/web/lib/api/types.ts` `ChallengeView`) | NOT AFFECTED | Its documented choice is not to render the frame (12 §24); unchanged. |
| **CYAN** `frontend-symbiotic` `d3d9bd6` (`apps/web/lib/api/inquiryClient.ts`) | NOT AFFECTED | `createChallenge` sends `{title, description}`, which is accepted exactly as before. `ChallengeDetail.challenge` reads only named keys, and `parseQuery` checks only `kind === "ok"`, so the additive keys are invisible. No visual or interaction decision arises, so there is no Case 3. Proven by `test_cyan_shaped_request_and_pre_existing_keys_are_unchanged`. |
| F02 (parent Field) | NOT AFFECTED (behaviour) | Additive wire extension of F02's Challenge contract; the full F02 suite is green. |
| F03 | NOT AFFECTED | The F03 suite is green; no F03 relation touched. |
| F04 (`f04-implementation`) | NOT AFFECTED | Not in this tree; nothing in F04 reads the four fields over HTTP. A later merge will carry the additive keys. |
| F05+ / REFLECTION gate (HD-20, HARD-DEP-002) | NOT AFFECTED | No AI path touched. |
| Tests | AFFECTED (added) | New falsifier file; no existing test changed. |
| Reports / evidence | AFFECTED (added) | This file and `evidence/`. |
| Runtime evidence | NOT AFFECTED | No runtime configuration changed. The integration proof runs the real FastAPI app against real PostgreSQL. |

### 6 LOCAL PROOF

`ruff check`, `ruff format --check` and `mypy` pass on all changed files. `check_architecture_dependencies`, `check_provider_sdk_imports` and `check_test_only_imports` all return PASS.

### 7 INTEGRATION PROOF

Real FastAPI app (`TestClient`), real session authentication and real PostgreSQL (`nquiry_pfc_a1_test`):
- `POST` sends the frame.
- The `challenges` row is compared byte-exact.
- `GET` detail returns the same values, for the Facilitator, the Owner and a Contributor.
- Result: **23 passed** (`evidence/falsifiers_green.txt`).

### 8 PRESERVATION PROOF

Each MUST REMAIN TRUE is re-proven after the Delta:
- Title required: `test_title_remains_required`.
- Facilitator only, and a denial stores nothing: `test_authority_unchanged_and_denial_stores_nothing` (owner, contributor, stranger).
- Idempotency: `test_idempotency_covers_the_frame`.
- Description behaviour: `test_description_behaviour_unchanged`.
- CYAN shape: `test_cyan_shaped_request_and_pre_existing_keys_are_unchanged`.
- One governed commit with role provenance: `test_one_governed_commit_with_facilitator_role_provenance`.
- F02/F03: full regression.

MUST REMAIN IMPOSSIBLE:
- No status or new fields: `test_no_status_and_no_new_fields`, `test_status_or_unknown_input_is_not_honoured` and mutation M18.
- No silent cross-field mutation: `test_each_field_travels_independently` and mutations M10 and M17.
- No AI, authority or schema path: the diff touches none of them.

### 9 REGRESSION PROOF

Full suite on the modified tree, isolated DB (`evidence/regression.txt`):

| Run | Before (baseline) | After |
|---|---|---|
| Live suite (real PostgreSQL) | 1535 passed, 2 skipped | **1558 passed, 2 skipped** (= 1535 + 23 falsifiers) |
| No-DB suite | 808 passed, 752 skipped * | **808 passed, 752 skipped** |

\* The no-DB baseline was taken after the falsifier file was written, so its 752 skips include the 23 falsifiers, which skip without a DB. This was re-verified after the Delta: without the falsifier file the result is 808 passed, 729 skipped, and the falsifier file alone gives 23 skipped. The comparable baseline figure is therefore 808 / 729, and it is unchanged.

The F02 and F03 suites are part of the live run and all pass.

Mutation proof (`scripts/pfc_a1_mutation_proof.py`, `evidence/mutation_proof.txt`): **18/18 KILLED**. The sources were restored byte-exact after the run (sha256 verified).

### 10 INVERSE PROOF

```text
PROJECTION   GET detail challenge.{context,desiredOutcome,constraints,stakeholders}
  ← API      inquiry_queries.challenge_detail reads ports.challenges.get(cid)
  ← PERSIST  challenge_from_row ← challenges.{context,desired_outcome,constraints,stakeholders}
  ← APP      challenge_repository.add inside create_challenge (one governed commit)
  ← DOMAIN   Challenge(title non-empty; four frame fields str | None; no status)
  ← GATE     CMD_CREATE_CHALLENGE, idempotency fingerprint over CreateChallengePayload
  ← STATE    Workspace ACTIVE, Challenge created (no lifecycle status invented, 09 §25.2)
  ← AUTHORITY role FACILITATOR, AUTH-DEP-CH-001, BND-001/002/003
  ← GOVERNANCE audit CMD_CREATE_CHALLENGE, authority_source_type ROLE, actor HUMAN_USER
```

Every link is exercised by a named falsifier or mutation, so no link ends in an assumption.

### 11 RECURSIVE DEEP SWEEP

| Risk | Finding |
|---|---|
| Semantic drift | None. The fields keep their 09 §25 meaning: free text, not interpreted. |
| Authority leakage | None. No new route or role; Owner and Contributor are still denied. |
| Hidden cross-field mutation | None. M10 and M17 are killed, and each field travels independently. |
| State inconsistency | None. The same single commit; a denial and a malformed body store nothing. |
| Projection inconsistency | Only GET detail carries the frame. The overview and position keep their shapes, which is intentional and recorded in §5. |
| Preservation regression | None (§8, §9). |
| Documentation drift | The `apps/web/lib/api/types.ts` comment ("server-side detail this package does not render") stays true. |
| Evidence drift | Evidence is produced from the exact tree whose checksums are in `evidence/checksums.txt`. |

### 12 INVERSE DEEP SWEEP

From the stored `challenges.constraints` value back to its source: the only writer is `ChallengeRepository.add`, reachable only from `create_challenge` (`CMD_CREATE_CHALLENGE`), which is reachable over HTTP only from `POST /workspaces/{w}/challenges` behind the FACILITATOR role (checked with `grep`: no other writer and no update command). The value is the HTTP body string, passed through `_frame_text`, which returns it unchanged or `None`.

### 13 DOCUMENTATION / EVIDENCE

This file and `docs/implementation/field-reports/PFC-A/evidence/`.

### 14 FIELD RECONSTRUCTION

```text
DELTA → RE-READ (git diff, 3 files, +26/−4) → COMPARE EXPECTED (only the three
FBR sites changed; migration head unchanged; no frontend file changed) →
RECONSTRUCT FIELD (relation closed from HTTP input to GET projection) →
RESULTING FIELD STATUS (below)
```

### 15 HUMAN REVIEW

No CYAN change is made, so human visual review is not required. Human review of this record is required before any dependent Work Unit.

### 16 CHECKPOINTING

Human acceptance of the technical result and checkpoint authority (2026-09-26, "NQUIRY_PRODUCT_FUNCTION_COMPLETION AUTONOMOUS SFE EXECUTION AUTHORIZATION", §1: "I accept the WU-PFC-A1 technical result and authorize its checkpoint materialization.").

Before committing, the tree was re-verified against `evidence/checksums.txt` (all OK). The change set is exactly the one recorded here.

The checkpoint follows the F02/F03/F04 precedent: a signed materialization commit and an annotated, signed tag `checkpoint-PFC-A1` on it, then an identity-record commit. The commit and tag identities are recorded in `CHECKPOINT_WU-PFC-A1.md` by the identity-record commit.

The predecessor of the materialization commit is `origin/pfc-architecture` `1eb3799`.

### 17 RESULTING FIELD STATUS

Before acceptance: **LOCAL proof and FIELD proof complete; uncommitted; READY_FOR_HUMAN_REVIEW.**

After the human accepted the technical result (2026-09-26) and the checkpoint: **TECHNICALLY_ACCEPTED, CHECKPOINTED (`checkpoint-PFC-A1`), recoverable predecessor.**

This is not REVIEWED_FIELD (no independent review has been performed) and not PUBLISHED_FIELD (not merged into master).

## 3. Open / remaining

- Emotional Temperature (Case 3, NQ-GAP-018 neighbourhood) and Challenge `status` (NQ-GAP-018) remain open and are not touched.
- There is no update command for the frame (09 §80 names none), so the frame is create-only.
- Displaying the frame in CYAN (the challenge chamber and the session header) is a future visual decision and needs a CYAN Work Unit with human visual review.
- Checkpointing (commit, push, tag) needs publication authority.

## 4. Falsifier map

| Falsifier (`tests/e2e/test_pfc_a1_challenge_frame.py`) | Proves |
|---|---|
| `test_frame_fields_round_trip_exactly` | MUST BECOME TRUE: byte-exact DB and GET, for all readers |
| `test_each_field_travels_independently` ×4 | no cross-field mutation |
| `test_absent_null_empty_or_blank_means_not_provided` ×4 | Case-2 rule |
| `test_non_text_frame_value_is_rejected_and_nothing_stored` ×4 | malformed body rejected, nothing stored |
| `test_title_remains_required` | MUST REMAIN TRUE |
| `test_authority_unchanged_and_denial_stores_nothing` ×3 | MUST REMAIN TRUE / IMPOSSIBLE |
| `test_idempotency_covers_the_frame` | MUST REMAIN TRUE |
| `test_cyan_shaped_request_and_pre_existing_keys_are_unchanged` | CYAN compatibility |
| `test_description_behaviour_unchanged` | F02 behaviour |
| `test_no_status_and_no_new_fields` | NQ-GAP-018; no unrelated fields |
| `test_status_or_unknown_input_is_not_honoured` | unknown input not stored |
| `test_one_governed_commit_with_facilitator_role_provenance` | governance chain |
