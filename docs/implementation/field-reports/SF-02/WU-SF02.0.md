# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.0 — Repository binding gate, decisions, baseline

## Authority
Human instruction `SFE::MATERIALIZE_APPROVED_ARCHITECTURE` (2026-09-25): implementation authority over the
worktree `/home/codi/Entwicklung/nquiry/worktrees/frontend-symbiotic` (branch `frontend-symbiotic`, starting HEAD
`644e1c8ce340a9c2475132b717648f57dee1a541`), no publication authority (no tag, no push, no PUBLISHED claim).
Governing architecture: `docs/implementation/frontend/22_NQIRY_SYMBIOTIC_SURFACE_ARCHITECTURE.md` (5878 lines, read
completely; persisted into this worktree byte-identical to the main checkout copy, sha256 `9b9592bb351ce87f…`).
Doc 21 (SF-01) remains the foundation; doc 22 supersedes it where the two differ (dark Field identity, colour law).

## Repository reconstruction (before any change)
- Worktrees: main checkout `master` @ c529d3d (docs-only edits in progress, not mine); `.claude/worktrees/local-login-auth`
  @ c9d86ba (published F03; runs the `nquiry` compose project on :3000/:8000/:15432); `worktrees/f04-implementation`
  @ d9410b3 ("hand off reviewed architecture revision 6": F04 in progress, NOT published, not inspected further);
  this worktree @ 644e1c8, clean except the untracked SF-01 browser-review evidence.
- Baseline gates on 644e1c8: tsc 0 errors, eslint clean, vitest 196/196, isolated mocked lane 81/81 (SF-01 record),
  isolated real stack 14/14 (WU-SF01.8 record).
- Backend contracts discovered (never invented), all in this tree:

| Architectural relation (22 §9) | Domain / application source | Projection / query | Capability | Authority | Command (route) | Persistence | Frontend contact | Test contact |
|---|---|---|---|---|---|---|---|---|
| 9.1 Identity → Access | `application/auth_handler.py` (login/resolve_session) | `GET /auth/me` | authenticated or not | local credential + session (doc 18) | `POST /auth/login`, `POST /auth/logout` | `users`, `local_auth_credentials`, `local_auth_sessions` | `lib/api/authClient.ts`; `/login`, `/` | `auth.spec.ts`; every real-stack `openAs` |
| 9.2 Access → Workspace | `accessible_workspaces_query.py`; `workspace_creation_handler.py` (FOUNDING) | `GET /workspaces` | founding: any authenticated identity (HARD-DEP-001 Option A) | membership | `POST /workspaces` (keyless, F01) | `workspaces`, `workspace_memberships` | `workspaceClient.ts`; `/workspaces` | `workspaces.spec.ts`, F02 real-stack |
| 9.3/9.4 Workspace → Membership → Role | `capability_projection.py`; `membership_operations_handler.py` | `GET /workspaces/{w}` (role, heldAuthorityClasses, authorized, governanceCapable); `GET …/overview` (members[role]) | `overview.capabilities.addMember`; F01 `governanceCapable` | BND-004/005 at add-member | `POST /workspaces/{w}/members` (keyless, F01) | `workspace_memberships`, `role_assignments` | `/workspaces/[w]` | `workspaces.spec.ts` (orientation-*, add-member-*) |
| 9.5/9.6 Governance root → Grant | `authority_binding_handler.py` | `challenge_detail.sessionControllers`, `session_position.sessionControllers` (BindingProvenance: holder, grantedBy, scope) | `capabilities.grantSessionControl`, `actions.GRANT_SESSION_CONTROL` | WORKSPACE_GOVERNANCE_RIGHT | `POST /workspaces/{w}/authority-bindings` (Idempotency-Key) | `human_authority_bindings` | Challenge + Session pages | F02/F03 real-stack (grant flows) |
| 9.7 Grant/Role → Capability | `inquiry_queries._cap` / `_holds` (AuthorityResolver) | every `capabilities.*` / `actions.*` `{available, reasonCode, reason, relevant}` | itself | resolver | — | — | `Unavailable`, `affordanceState` | all specs (`action-reason-*`, `*-unavailable`) |
| 9.8/9.9 Workspace → Challenge → Framing | `challenge_creation_handler.py` (AUTH-DEP-CH-001 Facilitator) | `overview.challenges`, `challenge_detail.challenge` | `createChallenge` | role Facilitator | `POST /workspaces/{w}/challenges` (Idempotency-Key) | `challenges` | Workspace + Challenge pages | F02 real-stack, `sf01-field.spec.ts` |
| 9.10/9.11 Challenge → Session / New Session | `session_creation_handler.py` | `challenge_detail.sessions[{state, version, createdAt}]` | `openSession` (SESSION_CONTROL_RIGHT @ CHALLENGE) | resolver | `POST …/challenges/{c}/sessions` (Idempotency-Key) | `sessions` | Challenge page (containment/capability orbit) | F02/F03 real-stack ("Open Session") |
| 9.12 Session → Control | `session_control_handler.py` (HD-1 SESSION scope) | `session_position.sessionControllers`, `viewer.isSessionController` (label only) | `actions.*` with `NO_SESSION_CONTROL` | HD-1/HD-9 | transitions below | `human_authority_bindings` | Session page | F02/F03 real-stack |
| 9.13 Session → Participation | `session_control_handler.admit_participant` (HD-7/HD-14) | `participants[]`, `admitCandidates[]` | `actions.ADMIT_PARTICIPANT` | controller | `POST …/participants` | `session_participations` | Session page | F03 real-stack (admit loop) |
| 9.15 Session → Question Generation | `burst_capture_handler.py` (BND-005 PARTICIPATION, BND-008) | `burst{state, mode, startedAt, guidanceSeconds, guidanceIsAuthoritative=false}`, `questionSet{visibility=OWN_ONLY_WHILE_ACTIVE, mine, capturedCount}` | `actions.CAPTURE_QUESTION` | PARTICIPATION (HD-15) | `POST …/burst/questions` (originalText + expectedBurstVersion only) | `questions`, `burst_question_memberships` | `BurstCapturePanel`, `OwnQuestions`, `BurstTimer` | F03 real-stack + a11y; `frozenSet.test.tsx`, `burstClient.test.ts` |
| 9.14 Participation → Question visibility | `inquiry_queries._question_set` (HD-13, server-side filter) | `questionSet.visibility` NONE / OWN_ONLY_WHILE_ACTIVE / FULL_FROZEN_SET | — | server filter | — | — | same | F03 real-stack (peer texts absent from body) |
| 9.16 Question → Authorship | `_question_json` | `CapturedQuestion{origin=HUMAN, captureOrigin, authorUserId, authorName, capturedOrder}` | — | — | — | `questions` | `FrozenQuestionSet`, `OwnQuestions` | F03 specs |
| 9.17 Generation → Frozen set | `burst_completion_handler.py` (TRN-SESS-005 + TRN-BURST-005) | `questionSet.frozen{fingerprint, verified, memberCount, completedAt, questions}`; `session.state=QUESTION_CAPTURE`, `burst.state=COMPLETED` | `actions.COMPLETE_BURST` | BINDING @ SESSION (HD-9) | `POST …/transitions/complete-burst` (expectedVersion + expectedBurstVersion) | `question_bursts.frozen_membership_fingerprint` | `BurstCapturePanel` (confirm) | F03 real-stack |
| 9.18 Frozen → Verification | `application/frozen_set.py::verify_frozen_set` (recompute) | `frozen.verified`, `frozen.fingerprint` | — | — | — | same | `FrozenQuestionSet` | `frozenSet.test.tsx`, F03 real-stack (`frozen-verified`) |
| 9.19 Authority → Proof | `persistence/inquiry_directory.session_state_established_by` (audit) | `establishedBy{commandType, actorName, occurredAt, commitId, authoritySourceType, authoritySourceRef, authorityScopeRef}`; `workspace.governedFounding` | — | audit provenance | — | `audit_events`, `commit_units` | proof planes / `ProofDepth` | F02/F03 real-stack (`session-last-transition`) |
| Session lifecycle | `domain/session.py` (13 states), `session_transitions` | `session.state`, `phases[13]{status done/current/upcoming}`, `session.version` | `actions.BEGIN_SETUP`, `BEGIN_CHALLENGE_CAPTURE`, `PREPARE_BURST`, `OPEN_QUESTION_GENERATION` (+ `relevant`) | HD-1 | `POST …/transitions/begin-setup`, `…/begin-challenge-capture`, `…/burst`, `…/transitions/open-question-generation` | `sessions`, `question_bursts` | Session page lifecycle orbit | F02 real-stack |
| 9.20 Analysis contact zone | **not established in this tree** (F04 is an unpublished worktree) | none | none | none | none | none | **absent** (no mock introduced; 22 §36.1–36.2 conditions not met: the architecture is exercised without it) | gate: no F04 vocabulary |
| Boundaries (22 §28) | `http_f02._command_outcome`, `_query` | envelope kinds committed / denied / rejected / stale / blocked / failed_precommit / indeterminate / not_found (+ client `network_failure`) | — | — | — | — | `outcomeSemantics`, `effectLifecycle`, `EffectSurface`, `ReadBoundary` | `outcomeVocabulary.test.ts`, SF-01 tests |
| Legacy `/decision` (PKG-28/29) | `session_view_query.py` | `GET /workspaces/{w}/sessions/{s}` | — | — | `POST /decisions/{d}/decide` | — | untouched (non-primary, NON_PROOF prototype; F07 re-homes) | `session-view.spec.ts`, `decision.spec.ts` (unchanged) |

## Protected-semantics check (22 §43) against the repository
No contradiction found. Human Question Law = F03 as published (capture in QUESTION_GENERATION / ACTIVE HUMAN_ONLY;
`CMD_COMPLETE_BURST` freezes and yields QUESTION_CAPTURE; no BEGIN_ANALYSIS anywhere). Peer hiding is the server's
filter. Frozen set immutable (DB triggers). One derivable defect against 22 §4.7 (read failure used mutation language:
SF-01 review D-2) is repaired in WU-SF02.1.

## Case-3 register (22 §45) resolved by repository inspection
| 22 § | Question | Repository fact | Class |
|---|---|---|---|
| 45.1 | external auth providers | not established (doc 18: local adapter only) | not shown; open relation for the production-auth Field (Case 1: the architecture itself says "must not display … unless established") |
| 45.2 / 45.3 | analysis contact / mock analysis visibility | no analysis relation, route, projection or mock lane exists in this tree | absent; nothing to decide (recorded open) |
| 45.4 | participant identity during active generation | F02/F03 project and render participant NAMES to every member (`participants[]`, `participants-list`), HD-13 hides only question CONTENT | Case 1: keep |
| 45.5 | non-controller explanation | F02/F03 render the server reason for unavailable controller/participant actions (`action-reason-*`, asserted by real-stack specs) | Case 1: keep |
| 45.6 | denied vs not found | the server decides (`QueryDenied` for non-members, `QueryNotFound` inside the Workspace); the frontend renders the verdict | Case 1: keep |
| 45.7 | contradiction | none | — |

## Case-1/Case-2 technical closures (22 §44.1)
- Technology: DOM + inline SVG for orbits/paths, CSS custom properties for geometry (unit-circle coordinates from a
  pure function), CSS animations for motion, CSS/SVG for the background; no canvas, no visualization dependency
  (22 §35.12). Dark identity: `:root` tokens rewritten (cyan / blue / red / neutral); the F02 light theme is gone.
- Topology container: one `.field-stage` grid; core + rings absolutely positioned inside a `--field-size` square on
  desktop, planes in the second column; DOM order = semantic stack order (22 §32.6) so keyboard order never follows
  geometry; ≤ 860px or > ring capacity → the same DOM as a relational stack with connectors.
- Effect lifecycle: the SF-01 reducer, extended with a relation-specific `detail` and prefix-matched relation
  families; `useEffectField` remains the ONE lifecycle per surface (one `command-outcome` at a time).
- Field id `SF-02` and report/evidence location `docs/implementation/field-reports/SF-02/` (repository convention).
- Ledger reconciliation stays WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION (REC-018.., NQ-DEC-044.. claimed elsewhere).

## Work Unit plan
SF02.1 identity foundation + lifecycle extensions + gates · SF02.2 topology primitives · SF02.3 Challenge Field ·
SF02.4 Workspace Overview + Workspace Field · SF02.5 Session Field (Human Question Field, Frozen Field) ·
SF02.6 Access Field · SF02.7 proof ladder (unit, mocked, real stack) · SF02.8 browser evidence + reviews.

## Result
Binding gate closed; no Case 3 raised. Proceeding to implementation.
