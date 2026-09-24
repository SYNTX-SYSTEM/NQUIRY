# NQUIRY FIELD REVIEW REPORT

## Field
F02 — CHALLENGE · SESSION · PARTICIPATION (19 §22). Semantic regime: inquiry
context and process lifecycle.

This review was **reconstructed after WU-02.12**, the Field-closure Work Unit
opened by human authority after the SFE bootstrap reconstruction. It replaces
the pre-WU-02.12 review, whose claims are corrected in "Corrections to the
previous review" below.

## Worktree State
*(State at review time, before publication. The approved commit identity is
recorded under "Commit Status" below.)*

- Worktree: `.claude/worktrees/local-login-auth`, branch
  `worktree-local-login-auth` at `0ea5bbb` (F01, = `origin/master`), plus
  uncommitted F02 (WU-02.0 … WU-02.12).
- Index empty, `git diff --check` clean. **NOT COMMITTED.**
- The main checkout (`master` @ `c529d3d`, one behind origin) holds the
  **documentation** of F02 as a docs-only mirror, synchronized to the final
  reconstructed version at the publication pre-flight (after WU-02.12). It
  contains no implementation code. Before synchronizing, every differing
  canonical copy was compared against the worktree: the canonical files had
  not been modified since the WU-02.11 mirror, and every line present only
  in a canonical copy is text that WU-02.12 replaced (no independent edits).
  Synchronized: WU-02.12.md, FIELD_REVIEW.md, CHATGPT_REVIEW.txt, STATUS.md,
  the bootstrap reconstruction report, 04 / 05 / 12 / 16 / 20, RUNTIME_OPERATION.md
  and README.md. The worktree copies and the canonical copies are
  byte-identical.
- The main checkout's `master` does not contain F01's commit `0ea5bbb`, so
  it lacks the F01 reports that F02 documents cite (for example
  `F01/WU-01.4.md`, cited by 16 §41 REC-001). Those citations resolve in the
  worktree and on `origin/master`; they resolve in the main checkout only
  after it is brought forward. That is a publication step for human
  authority, not a documentation defect.

## Field Purpose
Make the governed inquiry context real and visible:
`LOGIN → WORKSPACE → GOVERNANCE → CHALLENGE → SESSION → LAWFUL SESSION PROGRESSION → QUESTION_GENERATION`.
The UI shows:
- where the human is;
- what they may and may not do, and why;
- which state is canonical, and which authority enables an action;
- what failed, was rejected, or was denied.

## Authoritative Parent
- LEVEL 1 (SFE): `20_SYSTEM_FIELD_ENGINEERING.md`.
- LEVEL 2: 02 §12; 03 §12.3 / §13–§22; 04 §21–§25 / §35–§40; 05 §19–§20;
  06 BND-001..014; 09 §9 / §27 / §28 / §82; 12 §4–§11 / §23 / §24;
  16 (incl. §41); 19 §22.
- Human decisions: HD-1, HD-3, HD-6, HD-7, HD-8, **HD-9** (see "Human
  decisions" below), the WU-02.0 decisions (grant Command; Owner ≠
  Facilitator), and WU-02.2 (ChallengeCapability option A).

## Initial State (before F02)
- F01 committed. Only application-layer WIP for grant, CreateChallenge (a
  hand-rolled writer with fabricated `uuid4` audit ref), ChallengeCapability
  and CreateSession.
- No routes or UI for any of it. No Session transitions, no participation.
- `SESSION_CONTROL_RIGHT` resolved at three different scopes.
- The effect gate could express only binding authority.
- Browser proof was `page.route()`-mocked everywhere.
- SFE existed only in prompts.
- The 16 ledger contradicted the committed HARD-DEP-001 decision.
- One live-DB test was red since F00.

## Final State
A stakeholder can do the following in a real browser against the real stack:
1. log in;
2. found a Workspace, becoming its governance root;
3. add a Facilitator;
4. the Facilitator frames a Challenge;
5. the root grants Challenge-scoped Session control, and the Facilitator
   opens a Session;
6. the root grants Session-scoped control, and the Facilitator advances the
   Session (setup, challenge capture);
7. the Facilitator prepares a protected HUMAN_ONLY Burst, admits a
   participant, and opens question generation (Burst ACTIVE, same commit).

Every unavailable step shows the server's reason. Every outcome kind is
distinct on the wire and in the UI, on **every** route (since WU-02.12). An
`Idempotency-Key` names exactly one logical Command. The position page shows
canonical state, authority provenance (holder, grantor, scope) and the
committed Command that established the state.

## Internal Work Units Executed
| WU | Title | Report |
|---|---|---|
| 02.0 | GrantHumanAuthorityBinding | WU-02.0.md |
| 02.1 | CreateChallenge / GetChallenge | WU-02.1.md |
| 02.2 | ChallengeCapabilityProjection | WU-02.2.md |
| 02.3 | CreateSession | WU-02.3.md |
| 02.4 | SFE architecture 20 + ledger reconciliation + HD records | WU-02.4.md |
| 02.5 | Real-stack lane + DEV-ONLY identity (HD-3) + RED; normalized-red repair | WU-02.5.md |
| 02.6 | Effect gate typed authority sources (HD-6) | WU-02.6.md |
| 02.7 | HD-1 Session control, transitions, Burst prepare, TRN-SESS-004 bundle | WU-02.7.md (authority classification corrected by WU-02.12) |
| 02.8 | SessionParticipation (HD-7/HD-8) | WU-02.8.md |
| 02.9 | HTTP transport, failure envelope, idempotency, capability projections | WU-02.9.md (idempotency and envelope claims corrected by WU-02.12) |
| 02.10 | Frontend surfaces + F11 foundation, a11y / responsive / visual | WU-02.10.md |
| 02.11 | Field-end proof, L8, environment isolation, docs | WU-02.11.md |
| **02.12** | **Field closure: FBR-B idempotency identity, FBR-C outcome vocabulary, FBR-D ledger, HD-9** | **WU-02.12.md** |

## Corrections to the previous review (pre-WU-02.12)
| Previous claim | Truth found | Resolution |
|---|---|---|
| "Same key with a different payload is `rejected`" | True only for challenge, session and grant creation. On Session Commands the key was replayed whatever the payload (another expected version, another Session). A key reused across Command types **committed an effect under another Command's `commands` row**. Cross-Workspace reuse gave a **500** | FBR-B repaired (WU-02.12) |
| "Common failure envelope"; "F01/Arch-17 malformed input is now `rejected`" | The producers changed, but two consumers (`parseSessionReadResult`, orientation parse) threw on `rejected` and rendered a network error. Framework validation returned FastAPI 422 `{detail}` (collides with `blocked`). F01/PKG routes folded `failed_precommit` into `rejected` | FBR-C repaired (WU-02.12) |
| "Reconciled into 16 §41 as NQ-DEC-032..034"; ledger reconciled | §41 went up to 036. The §6 table, YAML and §36/§40 counts were not updated. GAP-09-007 had no canonical row. Status tokens were non-standard | FBR-D repaired (WU-02.12, 16 §41 REC-010) |
| WU-02.7: Session-scoped `SESSION_CONTROL_RIGHT` as Burst START authority is "Case 1" | A Case-3 authority relation. 04 §36–39 / 05 §20 name the Facilitator + FacilitatorScopeBinding | Closed by human decision **HD-9** (prototype narrowing), 16 §41 REC-009 |
| Static test forbids parallel savepoint writers | Matched one literal string only | AST detection + falsifier (WU-02.12) |
| Real-stack / mocked lanes run "against this tree" | Both lanes reuse whatever already serves `:3000`/`:8000` | Runbook §22 caution; WU-02.12 proof runs against containers rebuilt from this tree |

## Architecture Materialization
- **20** (SFE, governing): §15 lists HD-1 / 3 / 6 / 7 / 8 / 9. The range is
  corrected to NQ-DEC-032..037.
- **16**:
  - HARD-DEP-001 / NQ-GAP-041 / NQ-DEC-022 are RESOLVED (REC-001).
  - §41 REC-001..REC-010.
  - New canonical rows NQ-GAP-079 (GAP-09-007) and NQ-GAP-080 (production
    Burst control model).
  - NQ-DEC-032..037 are in §6 and the YAML.
  - Current counts (REC-010): 80 gaps (56 OPEN, 9 RESOLVED, 0 BLOCKED) and
    37 decisions (28 ESTABLISHED, 9 REQUIRED).
  - Ledger defects LD-1..5 are recorded.
- **04 §36/§39, 05 §20, 12 §9**: post-baseline narrowing pointers to
  REC-009. The original text is preserved. 12 also has the WU-02.4
  HARD-DEP-001 notes.
- **Runbook** §18 (outcome rules) and §22 (lanes + cautions).
- **README** (WU-02.11).
- **Proof-language successor record** (WU-02.4/02.5).

## Human decisions
| ID | Decision | Ledger |
|---|---|---|
| HD-1 | `SESSION_CONTROL_RIGHT` for Session transitions resolves at `SESSION:<id>`; no inheritance | REC-002 / NQ-DEC-032 |
| HD-3 | DEV-ONLY identity provisioning; no membership or authority | REC-003 / NQ-DEC-033 |
| HD-6 | Effect gate typed sources BINDING / ROLE / FOUNDING; no fabricated provenance | REC-004 / NQ-DEC-034 |
| HD-7 | The Session controller admits active Workspace members; no self-join | REC-006 / NQ-DEC-035 |
| HD-8 | At least one participant before QUESTION_GENERATION | REC-007 / NQ-DEC-036 |
| **HD-9** | **Prototype Burst control (start + manual completion) is closed by Session-scoped `SESSION_CONTROL_RIGHT`. It is an explicit prototype narrowing of 04 §36–39 / 05 §20, whose model stays OPEN for production (NQ-GAP-080)** | **REC-009 / NQ-DEC-037** |
| Procedural | Reopen F02 for WU-02.12 before commit review | WU-02.12.md |

## Domain Changes
None to domain vocabularies. F02 uses existing transitions (TRN-SESS-002 /
003 / 004, TRN-BURST-001 / 002). SessionParticipation is materialized as a
RELATION (02 §12).

## Authority / Governance Changes
- HD-1: all Session transitions resolve at `SESSION:<id>`. CreateSession
  resolves at `CHALLENGE:<id>`, which is how the Session comes into
  existence (AUTH-DEP-SESS-001).
- Grants must name a scope record of the same Workspace.
- HD-7: participation is admitted only by the Session controller.
- HD-8: at least one participant is required.
- **HD-9**: Burst START (inside TRN-SESS-004) and future manual completion
  are closed by the same Session-scoped binding in the prototype.
- WU-02.12 removed one illegitimate path: a `command_id` can no longer carry
  the effect of a different Command type.

## Boundary Changes
- BND-014 v1.1 evaluates typed authority (BINDING / ROLE / FOUNDING):
  - ROLE re-reads the current membership and role at commit;
  - FOUNDING requires a human actor and the founding Command ref;
  - there is no ALLOW without an `AuthoritySourceProof`.
- BND-007 applies to every Session transition.
- WU-02.12: the idempotency disposition (14 §27) runs before the version
  check on Session Commands, so replay ≠ STALE, and collision → `rejected`
  before any boundary or write.

## Effect Gate Changes
- `CommitCoordinator.commit(authority=…)`:
  - typed sources;
  - `EFFECT_GATE_NO_AUTHORITY_SOURCE` guard;
  - no `uuid4` fallback;
  - FOUNDING records its attempt inside the SAVEPOINT.
- CreateWorkspace and CreateChallenge commit through the gate.
- An AST-based static test forbids application-layer savepoint writers. The
  one documented exception is `recovery_handler` (F09).
- WU-02.12: the gate's input identity is guaranteed. A `commands` row's
  `command_type` now always matches the Command whose effect is committed
  under it.

## Provenance Changes
- `audit_events.authority_source_type` + `authority_scope_ref` (migration
  `a7f2c91d4e10`). Every new row names a resolvable binding, role
  assignment, or founding command.
- CreateWorkspace's circular ref is replaced by FOUNDING → its own command.
- The UI shows "current state established by" (command, actor, authority
  type, scope, commit).
- The NON_PROOF label is derived from provenance.

## Persistence Changes
- Migrations `a7f2c91d4e10` (typed audit provenance) and `b3d8e5f0a2c7`
  (`session_participations`: composite FK, ACTIVE-membership trigger,
  one-current partial unique, RLS; plus a one-open-Burst-per-Session
  unique). Head is `b3d8e5f0a2c7`.
- Repositories: `SessionRepository.transition`, Burst version reader,
  participation repository, `inquiry_directory`, deterministic membership
  tie-break.
- WU-02.12: `record_attempt` enforces Command-type identity. There is no
  schema change.

## API Changes
- 11 F02 routes (runbook §18), with a status-mapped envelope:
  - committed 200, denied 401/403, rejected 400, stale 409, blocked 422,
    failed_precommit 409, indeterminate 503, not_found 404.
- `Idempotency-Key` (UUID) is required on every F02 Command and is the
  `command_id`:
  - an identical retry → `committed` + `replayed`;
  - any other reuse → `rejected`.
- **WU-02.12, all routes:**
  - a body-validation failure → 400 `rejected` / `MALFORMED_REQUEST_BODY`;
  - F01/PKG decide, add-member, revoke report `failed_precommit` distinctly;
  - F01/PKG routes keep HTTP 200 with the outcome in the body `kind`
    (documented).
- CORS allows `Idempotency-Key`.

## Frontend Changes
- Workspace list, Workspace, Challenge and Session position pages.
  PKG-28/29 surface at `/sessions/{s}/decision`.
- `inquiryClient.ts`, with `network_failure` kept distinct. Restrained F11
  foundation (`globals.css`).
- Controls come only from server capabilities; an unavailable control shows
  the server's reason.
- WU-02.12:
  - every parser understands every kind its producer emits;
  - `/auth/me` fails closed on `rejected`;
  - rendering for `session-view-rejected`, `orientation-rejected`,
    `decision-failed-precommit-banner` and the login rejected message (no
    false "Incorrect email or password").

## Test-First Evidence
- RED was captured per WU (see the WU reports).
- WU-02.12 RED:
  - `test_wu_02_12_closure.py` **11 failed / 1 passed** (the positive
    control);
  - command-repository type test failed at collection;
  - vitest vocabulary **6 failed / 1 passed** (the fail-closed control);
  - real stack on the pre-repair containers: changed-payload reuse →
    HTTP 200.
- **Disclosed deviations:**
  - Several WU-02.4..02.10 modules were drafted before their tests ran;
    RED was proven by module removal (per report).
  - WU-02.12's failed_precommit test first failed for the wrong reason;
    RED was re-proven by temporarily restoring the old mapping line.
  - The AST gate's RED was shown by running the old predicate over the new
    falsifier cases.
  - The two WU-02.12 mocked component tests (decision `failed_precommit`,
    login `rejected`) were written **after** the UI change, with no RED
    demonstrated.

## Tests Added
**Backend:**
- `test_bnd_014_typed_authority.py` (9)
- `test_typed_authority_provenance.py` (4 + AST gate falsifier ×5)
- `test_session_control.py` (14)
- `test_http_f02.py` (4)
- `test_dev_identity_provisioning.py` (9)
- grant-scope (+1), burst readiness HD-1 (+1)
- **`test_wu_02_12_closure.py` (12)**
- **command repository type identity (+1)**
- WU-02.0..02.3's own 45

**Frontend:**
- `inquiryClient.test.ts`
- **`outcomeVocabulary.test.ts` (7)**
- mocked **+2**

**Real stack:**
- `f02-inquiry-context.real.spec.ts`
- `f02-accessibility.real.spec.ts`
- **`wu-02-12-closure.real.spec.ts`**
- each run on desktop + mobile

## Negative Tests
- Authority and scope:
  - an Owner without a Session binding;
  - Challenge-, Workspace- and other-Session-scoped control.
- Stale version (application, HTTP, browser).
- Cross-Workspace (three variants + HTTP + browser).
- Illegal topology (BND-007).
- Participation and Burst:
  - no Burst, no participant, second Burst;
  - non-member admission (handler + DB trigger), duplicate admission.
- ROLE source: wrong role, non-member, revoked, no reader.
- FOUNDING by a non-human actor.
- Grant to a missing or foreign scope.
- Malformed input:
  - missing Idempotency-Key or expectedVersion, malformed ids, no cookie;
  - **malformed bodies on F01, F02 and auth routes → `rejected`
    (WU-02.12).**

## Adversarial Tests
- **Idempotency-key reuse (WU-02.12):**
  - with a different payload on Session Commands;
  - on another Session;
  - across Command types sharing a payload shape;
  - across Workspaces.

  All are `rejected`, and canonical state and commits are unchanged.
- A replayed committed transition must not read as STALE.
- Unknown-Workspace attempts must not create command rows.
- Forged scope grants.
- The real-stack lane guards against its own mocking.

## Failure Injection
- Coupled bundle: the Burst is advanced underneath the TRN-SESS-004 commit
  → `CommitFailedPrecommit`, and neither the Session nor the Burst changes.
- Founding audit failure → full rollback.
- Duplicate founding attempt → FAILED_PRECOMMIT.
- **WU-02.12**: an injected `CommitFailedPrecommit` on add-member →
  `failed_precommit` on the wire (not `rejected`).

## ARCHITECTURE PROOF
- The F02 regime is materialized only through architecture-defined
  transitions and authority dependencies (03 TRN-SESS-002..004,
  TRN-BURST-001..002; 04 AUTH-DEP-*).
- Where the architecture was silent or contradictory, the relation was
  closed by recorded human decisions (HD-1 / 3 / 6 / 7 / 8 / 9) and
  reconciled into 16 §41 and 20 §15.
- History is preserved: baseline text is untouched, with inline pointers
  and successor records.
- The prototype narrowing HD-9 is explicit, and its production counterpart
  is an open canonical gap (NQ-GAP-080).
- No semantic rule is invented in code. The docstrings cite their source or
  their human decision.

## IMPLEMENTATION PROOF (this tree, after WU-02.12)
| Lane | Result |
|---|---|
| Backend live DB (isolated `nquiry_test`), run 1 / run 2 | **1360 passed, 2 skipped, 0 failed** (both) |
| Backend pure | **751 passed**, 611 skipped (SKIPPED_NO_DATABASE) |
| ruff format / ruff check / mypy (166 files) | clean / clean / clean |
| Architecture dependency / provider-SDK / test-only-import gates | PASS / PASS / PASS |
| Migrations static + live (`nquiry_test`) | PASS, 22 revisions, single head `b3d8e5f0a2c7` |
| eslint / tsc | clean / clean |
| vitest | **98 passed** |
| `next build` | compiled, 8 routes |

**Re-verified at the publication pre-flight** on the final tree (after the
`package.json` restoration and documentation synchronization; application
source unchanged since the containers were built): live DB 1360 passed / 2
skipped / 0 failed; pure 751 passed; ruff, mypy (166 files), architecture
gates and live migrations PASS; eslint and tsc clean; vitest 98; `next build`
OK; mocked Playwright **39 passed** (a full run; the WU-02.12 report's 39 had
been arithmetic from the earlier 37 plus two new tests); real stack 6 passed.

## REAL STACK PROOF
- **L6:** containers rebuilt from this worktree after WU-02.12 (api, web
  created 2026-09-24 15:29 UTC). `/healthz` 200; web 200; a live malformed
  login → `rejected`. Migration head `b3d8e5f0a2c7` on `nquiry` and
  `nquiry_test`.
- **L7:** `npx playwright test --config playwright.real-stack.config.ts` →
  **6 passed**:
  - F02 flow, desktop + mobile (three identities: unauthorized denial,
    stale, cross-Workspace read/write denial, malformed → `rejected`);
  - a11y, desktop + mobile (axe 0 serious/critical, keyboard, no overflow);
  - **WU-02.12 closure**, desktop + mobile (key reuse → `rejected` with
    canonical state unchanged in the UI; framework validation → `rejected`;
    `orientation-rejected` and `session-view-rejected` render as verdicts,
    not as network errors).
- The global setup refuses route mocking.
- **Accessibility:** axe 0 serious/critical WCAG 2 A/AA on all F02 pages,
  desktop + mobile, with a negative control. Keyboard-only transition with a
  visible focus ring.
- **Responsive:** 1280×860 and Pixel 7; no horizontal overflow; grid
  collapses at ≤ 860px.
- **Visual:** `docs/implementation/field-reports/F02/visual/` (6
  real-stack screenshots, WU-02.10). The WU-02.12 additions are text
  verdict banners, asserted by the real-stack spec. No new screenshots.

## Recursive Upward Test Ladder
- L0/L1 per WU.
- L2 producer/consumer: handlers ↔ BND-014 ↔ audit; queries ↔ Commands via
  shared blockers; **API outcome kinds ↔ every web parser (WU-02.12)**.
- L3 full F02 integration.
- L4 F01 (create workspace, add member, revoke, grant, orientation,
  accessible workspaces, login) + PKG-29 decide + F03 prerequisites.
- L5 static gates.
- L6 containers.
- L7 real browser.
- L8 regression (above).

## Recursive DeepSweep Result
PASS. Each WU report carries the reconstruction chain. Cross-Field effects
are handled:
- F01: CreateWorkspace behind the gate; F01 routes return `rejected` /
  `failed_precommit` distinctly; F01 clients and pages updated; ordering
  flake fixed at root.
- PKG-29: decide `failed_precommit`; the rejected session view renders as a
  verdict.
- F03: Burst scope aligned (HD-1); Burst control authority closed (HD-9);
  the idempotency pattern is sound for capture.

## Inverse DeepSweep Result
PASS.
- **Main chain.** Visible `QUESTION_GENERATION` (`session-state`) ← server
  `position.session.state` ← canonical `sessions` row re-read ← committed
  `CMD_OPEN_QUESTION_GENERATION` (`establishedBy.commitId`; since WU-02.12
  the `commands` row is guaranteed to be that Command type) ← BND-014
  BINDING at `SESSION:<id>` ← Session-scoped `SESSION_CONTROL_RIGHT` binding
  (shown with grantor), which is **also the Burst START authority under
  HD-9** ← `CMD_GRANT_HUMAN_AUTHORITY_BINDING` by the
  WORKSPACE_GOVERNANCE_RIGHT holder ← ACTIVE membership (`CMD_ADD_MEMBER`)
  ← FOUNDING (`CMD_CREATE_WORKSPACE`) ← verified local login
  (dev-provisioned identity, HD-3).
- **WU-02.12 chains** are in WU-02.12.md.
- No link is mocked, inferred, fabricated or fixture-created. The hop that
  the bootstrap marked "disputed authority mapping" is now closed by HD-9.

## First Broken Relation Result
Repaired at their homes:
- **Pre-WU-02.12:**
  - effect gate ↔ non-binding authority;
  - Session-control scope;
  - binding ↔ scoped record;
  - decision ↔ ledger (first pass);
  - challenge idempotency reuse;
  - rejected vs denied (producers);
  - test DB vs runtime history;
  - tie-order flake;
  - normalized-red HABB test.
- **WU-02.12:**
  - command identity ↔ Command type (provenance corruption);
  - Session replay guard ↔ authoritative disposition;
  - cross-Workspace key reuse ↔ 500;
  - producer ↔ consumer vocabulary (`rejected` on two reads, framework
    validation, `failed_precommit` fold);
  - decision ↔ ledger (tables, YAML, counts, GAP-09-007);
  - Burst control authority (HD-9);
  - weak parallel-writer gate;
  - test lanes ↔ running build.

**No known F02 First Broken Relation remains hidden.** The remaining items
are listed under Known Limitations with owner and reason.

## Fixture Ceilings
- The `scripts/seed_local_demo.py` Workspace is NON_PROOF: labelled from
  provenance and not the landing page. The only Decision data in the
  runtime comes from this seed. `/decision` for an F02-created Session shows
  "No Decision under consideration".
- Grant-suite preconditions insert Challenge rows directly (that suite tests
  grants).
- Dev identities (HD-3) carry no authority.

## Mock Ceilings
- The mocked Playwright lane (39) is component contract only. It includes
  the two retrofitted WU-02.12 tests.
- There are no backend mocks in F02 tests. `test_http_f02` and
  `test_wu_02_12_closure` monkeypatch only the DB `connect` onto the real
  test connection. `test_wu_02_12_closure` also replaces `add_member` with
  an injected `CommitFailedPrecommit` for one failure-injection case.

## External Dependency Ceilings
- GAP-14-001 (production identity provider): open. Only the local
  credential adapter and DEV-ONLY provisioning exist.
- HARD-DEP-002: not touched (no AI in F02).

## Known Limitations
- Question capture, Burst completion and the frozen set are F03. The
  ACTIVE Burst is visible but cannot yet receive questions (stated in the
  UI).
- Burst PAUSE/RESUME authority is not covered by HD-9. It is Case 3 if F03
  needs it.
- Leave/remove participation is undecided (NQ-GAP-079 remainder).
- Member addition takes a raw user id. Add-member is gated on F01
  `governanceCapable`, not on `overview.capabilities.addMember`. Both are
  server projections.
- `POST /workspaces` (F01) and `decide` have no client idempotency key
  (F01 / F07).
- F01/PKG routes answer HTTP 200 for every body kind (documented Case 2).
- `inquiryClient` does not shape-validate `ok`/`committed` bodies. Unknown
  kinds fail closed.
- `audit_events.authority_source_type` is nullable. Pre-F02 audit rows are
  immutable and untyped.
- **F03 entry conditions**:
  - `burst_repository.get_by_session` assumes one Burst per Session;
  - `inquiry_directory.establishedBy` assumes no re-entered state.
- The live-DB suite requires the isolated `nquiry_test` DB. Both browser
  lanes test whatever is already serving `:3000`/`:8000` (runbook §22).
- Ledger defects LD-1..LD-5 are recorded in 16 §41 REC-010.
- 00–13 still carry "DRAFT FOR HUMAN REVIEW" headers.

## Architecture Drift
- None introduced.
- Drift found by the pre-Field sweep and by the bootstrap reconstruction was
  repaired or scheduled: E7 `get_latest_by_challenge` → F07; E10 decide
  idempotency → F07.
- Process incident (WU-02.10): one accidental `git mv` staging, unstaged
  immediately.

## Downstream Fields Unlocked
F03 (Protected Human Question Field):
- **Satisfied dependencies:**
  - a Session lawfully reaches QUESTION_GENERATION with an ACTIVE HUMAN_ONLY
    Burst, Session-scoped control and participants;
  - Burst control authority for manual completion is closed (HD-9);
  - completion is manual (NQ-DEC-017);
  - the timer is presentation only (12 §11);
  - the participant capture right (AUTH-DEP-Q-001 + HD-7);
  - original_text immutability (NQ-DEC-002);
  - Question.status omitted (NQ-GAP-019 open);
  - the idempotency pattern is sound for capture (09 §108.2).
- **Entry conditions to handle in F03:** the two single-row assumptions
  above.
- **Conditional Case 3:** PAUSE/RESUME; automatic timer completion
  (CONFLICT-007).
- **Gate:** F03 must not start until `FIELD_COMMIT_APPROVED F02` publishes
  this Field.

F08 may start event-contract work in parallel (19 §47).

## Git Diff Summary
- 54 tracked files modified (+2571 / −677), all plain modifications: no
  deleted files, no renames, nothing staged.
- 59 untracked entries (71 files): new modules, 2 migrations, tests,
  15 F02 report files, 6 PNGs, doc 20, the reconciliation record, and the
  bootstrap report.
- Index empty.
- **Publication diff audit (pre-flight).** Every material file is
  classified as F02 implementation, test, documentation, proof,
  architecture reconciliation, or expected generated artefact. Two
  untracked files are **not F02 work and are withheld from the F02 commit**:
  `apps/web/AGENTS.md` and `apps/web/CLAUDE.md`, both generated by
  `next dev` on 2026-09-21 (they predate F02 and were not part of F01
  either). Publishing them would add agent-behaviour guidance to shared
  history. Whether to publish, ignore or delete them is a human decision.
- **Audit correction.** `apps/web/package.json` carried an unintended
  byte-level change beyond the intended `e2e:real` script: the description's
  em dash had been rewritten as a `\u2014` escape by tooling. It was
  restored to the original bytes (JSON-equivalent, no semantic change). Only
  the intended `e2e:real` line remains in that diff.
- Secrets check: no key- or token-shaped strings; the only credential
  literals are synthetic test passwords and the local-dev database password,
  which is already in committed history (`docker-compose.yml`, runbook,
  F00/F01 reports). `.env`, caches, `test-results/` and `.next/` are ignored
  and untracked.

## Git Diff Check
Clean.

## Commit Status
Approved via `FIELD_COMMIT_APPROVED F02` (human operator). Committed as
`2f33be11547b635b24be8cdba33f81afec643d7f`
("field(F02): governed Challenge, Session and participation vertical
(FIELD PASS)"): 123 files (54 modified, 69 added), parent `0ea5bbb`, signed.
Pushed to `origin/master` (fast-forward `0ea5bbb..2f33be1`). Signed annotated
tag `field-F02` (tag object `626054cb0e1b846eec645821c861cd3766de7eeb`,
resolving to `2f33be1`) pushed. Remote branch SHA and remote tag resolution
were verified from the remote, and the published tree was verified from a
fresh clone. `apps/web/AGENTS.md` and `apps/web/CLAUDE.md` were withheld by
human decision and are not in the published tree. This identity was recorded
after publication in a separate docs-only commit (19 §16). No other content
of this report was changed.

## Recommended Status
**FIELD_GREEN_WITH_DISCLOSED_EXTERNAL_CEILINGS**. The ceilings are
GAP-14-001 (production identity) and the disclosed DEV-ONLY identity source.
HARD-DEP-002 is not in scope.
