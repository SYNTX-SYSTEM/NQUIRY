# SF-01 FRONTEND BROWSER REVIEW — visible-website evidence

Field: SF-01 Symbiotic Frontend Foundation (synced with published F03). Branch `frontend-symbiotic`.
Review date: 2026-09-24/25 (runs at 2026-09-24T22:10Z and 22:37Z). Reviewer tool: real Chromium (Playwright
1.63, headless), driven by `browser-evidence-2026-09-25/harness/review-harness.mjs`. No network interception.

This report is self-contained: an independent reviewer can reconstruct every visible claim from it, the
screenshots, the per-state `results.json` files and the harness, without the chat transcript.

## 1. What was reviewed (runtime)

| Item | Value |
|---|---|
| Code under review | `frontend-symbiotic` @ `644e1c8ce340a9c2475132b717648f57dee1a541` (clean; SF-01 + published F03 `c9d86ba` + WU-SF01.8) |
| Runtime | isolated compose project `nquiry-sf01-inspect` (infra/sf01 recipe, unchanged): own Postgres volume (no host port), this tree's FastAPI (in-container :8000), production `next build`/`next start` (in-container :3000), same-origin proxy published **only** on `127.0.0.1:13100` |
| Why a proxy | the API's CORS origin is fixed to `http://localhost:3000` (owned by another Field's running stack). The proxy serves pages and `/api/*` from ONE origin, so no cross-origin call exists and no application code or config is changed. `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:13100/api` (documented runtime env) |
| Runtime-only files | `browser-evidence-2026-09-25/runtime/start-inspect.sh`, `runtime/proxy.mjs` (repaired, running), `runtime/proxy.before-repair.mjs` (original). Mounted read-only into the container from the session scratchpad; copies kept here for reconstruction |
| Database | fresh, migrated to head `f6b2c4d9a318` (25 revisions) |
| Other Fields | not touched: project `nquiry` (:3000/:8000/:15432, worktree `.claude/worktrees/local-login-auth`) kept running unchanged |

Start / stop (from the worktree root; `$S` = directory holding `proxy.mjs` + `start-inspect.sh`):
```bash
docker compose -p nquiry-sf01-inspect -f infra/sf01/compose.yaml run -d --build \
  --name nquiry-sf01-inspect-runner --publish 127.0.0.1:13100:13100 \
  -e INSPECT_ORIGIN=http://127.0.0.1:13100 -v "$S:/inspect:ro" runner bash /inspect/start-inspect.sh
docker compose -p nquiry-sf01-inspect -f infra/sf01/compose.yaml down -v --remove-orphans
```

## 2. Identities (runtime-only, isolated inspection DB only)

Created with the repository's HD-3 DEV-ONLY provisioning script (`scripts/dev_provision_local_identity.py`):
identity + local credential ONLY, no membership / role / authority. Every relation below was then established
through the product (governed Commands).

| Login | Password | Relations established through the product |
|---|---|---|
| `owner@inspect.local.test` | `inspect-owner-2026` | founded Workspace `SF-01 Inspection` (governance root); participant in the reviewed Sessions |
| `facilitator@inspect.local.test` | `inspect-fac-2026` | added as Facilitator; framed the Challenge; holds SESSION_CONTROL_RIGHT at CHALLENGE and at SESSION scope (granted by the Owner) |
| `outsider@inspect.local.test` | `inspect-outsider-2026` | member of nothing (empty + denied states) |
| `demo-owner@nonproof.test` | `nquiry-demo-2026` | repository NON_PROOF demo seed (`scripts/seed_local_demo.py`), labelled NON_PROOF in the UI; not used for proof |

Governed setup (API through the same proxy, Idempotency-Keys where required): CreateWorkspace → AddMember
(Facilitator) → CreateChallenge (Facilitator) → GrantHumanAuthorityBinding SESSION_CONTROL_RIGHT @ CHALLENGE
(Owner) → CreateSession (Facilitator, Session `7189d011-977b-5634-af1f-826bfc463d92`). A first harness attempt
used that Session and aborted at "Admit to Session" (harness timing, O-1), leaving it at CHALLENGE_CAPTURE with
a PREPARED Burst and 0 participants: truthful residue, not reviewed further.
The harness itself then opens a fresh Session per run **through the SF-01 "Open Session" relation in the UI**
and drives it through the real UI (Owner grants SESSION-scoped control → Begin setup → Begin challenge capture →
Prepare protected Burst → admit both as participants → Open question generation → capture → Complete Burst…).

Browser URLs:
- Login: http://127.0.0.1:13100/login
- **Primary SF-01 surface (Challenge):** http://127.0.0.1:13100/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2
- Workspace: http://127.0.0.1:13100/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007
- Session, frozen (run 2): http://127.0.0.1:13100/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509
- Session, frozen (run 1): http://127.0.0.1:13100/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8
- Session, aborted first attempt (CHALLENGE_CAPTURE, Burst PREPARED): http://127.0.0.1:13100/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/7189d011-977b-5634-af1f-826bfc463d92
- DRAFT state evidence: screenshot 13 of each run (taken before that run's Session was progressed)

## 3. Evidence layout

```
review/browser-evidence-2026-09-25/
  harness/review-harness.mjs              # the reviewer (rerunnable; EVIDENCE_RUN=<dir> writes a separate run)
  harness/proxy-keepalive-race.mjs        # D-1 mechanism falsifier (in-container)
  harness/proxy-race-through-proxy.mjs    # D-1 integration test through a proxy
  harness/proxy-race-fine.mjs             # D-1 finer through-proxy attempt
  runtime/{start-inspect.sh,proxy.mjs,proxy.before-repair.mjs}
  screenshots/  results/results.json  MANIFEST.md          # RUN 1 — BEFORE the D-1 repair (preserved)
  run-2-after-repair/{screenshots/,results.json,MANIFEST.md} # RUN 2 — AFTER the D-1 repair (authoritative)
```
Each `results.json` entry holds: URL, route, viewport, identity, canonical state, expected relation, the server
projection read with the same browser session, every check (expected vs actual), redirect chain, console,
page errors, failed requests, aborted prefetches, all 4xx/5xx, `_next/static` results, stylesheets + design
token, overflow, axe violations (all severities) and the keyboard focus walk.

## 4. Per-route results — RUN 2, after repair (authoritative)

| # | Screenshot | URL | Viewport | Identity | Canonical state (server projection) | Observed | Overflow px | axe s/c | Keyboard | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [01-desktop-login-anonymous.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/01-desktop-login-anonymous.png) | `/login` | desktop | anonymous | no NQUIRY session (GET /auth/me -> 401 denied) | FAILED check: login uses a layout container (shell/field/button classes) | 0 | 0 | 3 stops, 0 w/o focus | FAIL |
| 2 | [02-pixel-7-login-anonymous.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/02-pixel-7-login-anonymous.png) | `/login` | pixel-7 | anonymous | no NQUIRY session (GET /auth/me -> 401 denied) | FAILED check: login uses a layout container (shell/field/button classes) | 0 | 0 | 3 stops, 0 w/o focus | FAIL |
| 3 | [03-desktop-landing-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/03-desktop-landing-owner.png) | `/workspaces` | desktop | owner@inspect.local.test | authenticated; member of SF-01 Inspection | 4 checks met | 0 | 0 | 6 stops, 0 w/o focus | PASS |
| 4 | [04-desktop-workspace-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/04-desktop-workspace-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | owner@inspect.local.test | Workspace SF-01 Inspection; viewer = governance root (Owner), not Facilitator | 5 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 5 | [05-desktop-challenge-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/05-desktop-challenge-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | owner@inspect.local.test | Challenge framed; 1 Session DRAFT; Owner holds no Challenge-scoped Session control | 5 checks met | 0 | 0 | 10 stops, 0 w/o focus | PASS |
| 6 | [06-pixel-7-landing-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/06-pixel-7-landing-owner.png) | `/workspaces` | pixel-7 | owner@inspect.local.test | authenticated; member of SF-01 Inspection | 4 checks met | 0 | 0 | 6 stops, 0 w/o focus | PASS |
| 7 | [07-pixel-7-workspace-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/07-pixel-7-workspace-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | pixel-7 | owner@inspect.local.test | Workspace SF-01 Inspection; viewer = governance root (Owner), not Facilitator | 5 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 8 | [08-pixel-7-challenge-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/08-pixel-7-challenge-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | pixel-7 | owner@inspect.local.test | Challenge framed; 1 Session DRAFT; Owner holds no Challenge-scoped Session control | 5 checks met | 0 | 0 | 10 stops, 0 w/o focus | PASS |
| 9 | [09-desktop-workspace-facilitator.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/09-desktop-workspace-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | facilitator@inspect.local.test | Workspace; viewer = Facilitator (not governance root) | 2 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 10 | [10-desktop-challenge-facilitator-PRIMARY.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/10-desktop-challenge-facilitator-PRIMARY.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | Challenge; Facilitator holds SESSION_CONTROL_RIGHT at CHALLENGE:<c>; 1 Session DRAFT | 3 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 11 | [11-desktop-challenge-facilitator-proof-open.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/11-desktop-challenge-facilitator-proof-open.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | same, D2 authority proof opened by keyboard | 3 checks met | 0 | 0 | n/a | PASS |
| 12 | [12-pixel-7-challenge-facilitator-PRIMARY.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/12-pixel-7-challenge-facilitator-PRIMARY.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | pixel-7 | facilitator@inspect.local.test | same as desktop primary surface | 1 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 13 | [13-desktop-session-draft-facilitator.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/13-desktop-session-draft-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | desktop | facilitator@inspect.local.test | Session DRAFT; Facilitator has NO SESSION-scoped control yet (HD-1) | 2 checks met | 0 | 0 | 7 stops, 0 w/o focus | PASS |
| 14 | [14-desktop-session-question-generation-controller-participant.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/14-desktop-session-question-generation-controller-participant.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | desktop | facilitator@inspect.local.test | Session QUESTION_GENERATION; Burst ACTIVE HUMAN_ONLY; viewer = controller + participant | 6 checks met | 0 | 0 | 2 stops, 0 w/o focus | PASS |
| 15 | [15-desktop-session-question-generation-owner-participant.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/15-desktop-session-question-generation-owner-participant.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | desktop | owner@inspect.local.test | QUESTION_GENERATION; Owner = participant, not Session controller | 3 checks met | 0 | 0 | 2 stops, 0 w/o focus | PASS |
| 16 | [16-desktop-session-question-capture-frozen-facilitator.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/16-desktop-session-question-capture-frozen-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | desktop | facilitator@inspect.local.test | Session QUESTION_CAPTURE; Burst COMPLETED; frozen human set (fingerprint verified) | 5 checks met | 0 | 0 | 7 stops, 0 w/o focus | PASS |
| 17 | [17-desktop-session-question-capture-frozen-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/17-desktop-session-question-capture-frozen-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | desktop | owner@inspect.local.test | Session QUESTION_CAPTURE; Burst COMPLETED; frozen human set (fingerprint verified) | 5 checks met | 0 | 0 | 8 stops, 0 w/o focus | PASS |
| 18 | [18-pixel-7-session-question-capture-frozen-owner.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/18-pixel-7-session-question-capture-frozen-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/5170649f-b37c-5f1b-9f6c-27f3f3970509` | pixel-7 | owner@inspect.local.test | QUESTION_CAPTURE, frozen set | 0 checks met | 0 | 0 | 8 stops, 0 w/o focus | PASS |
| 19 | [19-desktop-landing-outsider-empty.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/19-desktop-landing-outsider-empty.png) | `/workspaces` | desktop | outsider@inspect.local.test | authenticated; member of nothing | 1 checks met | 0 | 0 | 5 stops, 0 w/o focus | PASS |
| 20 | [20-desktop-workspace-outsider-denied.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/20-desktop-workspace-outsider-denied.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | outsider@inspect.local.test | not a member → server denies | 3 checks met | 0 | 0 | 4 stops, 0 w/o focus | PASS |
| 21 | [21-desktop-challenge-not-found.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/21-desktop-challenge-not-found.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/00000000-0000-4000-8000-000000000000` | desktop | facilitator@inspect.local.test | Challenge id unknown in this Workspace | 2 checks met | 0 | 0 | 4 stops, 0 w/o focus | PASS |
| 22 | [22-desktop-workspace-malformed-rejected.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/22-desktop-workspace-malformed-rejected.png) | `/workspaces/not-a-uuid` | desktop | facilitator@inspect.local.test | malformed id → server rejects (input, not authority) | 1 checks met | 0 | 0 | 4 stops, 0 w/o focus | PASS |
| 23 | [23-desktop-challenge-loading-latency-2s.png](browser-evidence-2026-09-25/run-2-after-repair/screenshots/23-desktop-challenge-loading-latency-2s.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | projection not yet confirmed (2 s network latency, CDP emulation; no interception) | 1 checks met | n/a | n/a | n/a | PASS |

State 23 (loading) is captured under real 2 s network latency (CDP emulation, no interception); it records only
the trace check. All other states are fully instrumented.

## 5. Per-route results — RUN 1, before repair (preserved, shows D-1)

| # | Screenshot | URL | Viewport | Identity | Canonical state (server projection) | Observed | Overflow px | axe s/c | Keyboard | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [01-desktop-login-anonymous.png](browser-evidence-2026-09-25/screenshots/01-desktop-login-anonymous.png) | `/login` | desktop | anonymous | no NQUIRY session (GET /auth/me -> 401 denied) | FAILED check: login uses a layout container (shell/field/button classes) | 0 | 0 | 3 stops, 0 w/o focus | FAIL |
| 2 | [02-pixel-7-login-anonymous.png](browser-evidence-2026-09-25/screenshots/02-pixel-7-login-anonymous.png) | `/login` | pixel-7 | anonymous | no NQUIRY session (GET /auth/me -> 401 denied) | FAILED check: login uses a layout container (shell/field/button classes) | 0 | 0 | 3 stops, 0 w/o focus | FAIL |
| 3 | [03-desktop-landing-owner.png](browser-evidence-2026-09-25/screenshots/03-desktop-landing-owner.png) | `/workspaces` | desktop | owner@inspect.local.test | authenticated; member of SF-01 Inspection | 1 failed req | 0 | 0 | 6 stops, 0 w/o focus | FAIL |
| 4 | [04-desktop-workspace-owner.png](browser-evidence-2026-09-25/screenshots/04-desktop-workspace-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | owner@inspect.local.test | Workspace SF-01 Inspection; viewer = governance root (Owner), not Facilitator | 5 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 5 | [05-desktop-challenge-owner.png](browser-evidence-2026-09-25/screenshots/05-desktop-challenge-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | owner@inspect.local.test | Challenge framed; 1 Session DRAFT; Owner holds no Challenge-scoped Session control | 1 failed req | 0 | 0 | 9 stops, 0 w/o focus | FAIL |
| 6 | [06-pixel-7-landing-owner.png](browser-evidence-2026-09-25/screenshots/06-pixel-7-landing-owner.png) | `/workspaces` | pixel-7 | owner@inspect.local.test | authenticated; member of SF-01 Inspection | 1 failed req | 0 | 0 | 6 stops, 0 w/o focus | FAIL |
| 7 | [07-pixel-7-workspace-owner.png](browser-evidence-2026-09-25/screenshots/07-pixel-7-workspace-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | pixel-7 | owner@inspect.local.test | Workspace SF-01 Inspection; viewer = governance root (Owner), not Facilitator | 5 checks met | 0 | 0 | 9 stops, 0 w/o focus | PASS |
| 8 | [08-pixel-7-challenge-owner.png](browser-evidence-2026-09-25/screenshots/08-pixel-7-challenge-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | pixel-7 | owner@inspect.local.test | Challenge framed; 1 Session DRAFT; Owner holds no Challenge-scoped Session control | 3 failed req | 0 | 0 | 9 stops, 0 w/o focus | FAIL |
| 9 | [09-desktop-workspace-facilitator.png](browser-evidence-2026-09-25/screenshots/09-desktop-workspace-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | facilitator@inspect.local.test | Workspace; viewer = Facilitator (not governance root) | FAILED check: create-challenge form iff capability; 1 failed req; unexpected 502 GET /api/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/overview | 0 | 0 | 5 stops, 0 w/o focus | FAIL |
| 10 | [10-desktop-challenge-facilitator-PRIMARY.png](browser-evidence-2026-09-25/screenshots/10-desktop-challenge-facilitator-PRIMARY.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | Challenge; Facilitator holds SESSION_CONTROL_RIGHT at CHALLENGE:<c>; 1 Session DRAFT | 2 failed req | 0 | 0 | 8 stops, 0 w/o focus | FAIL |
| 11 | [11-desktop-challenge-facilitator-proof-open.png](browser-evidence-2026-09-25/screenshots/11-desktop-challenge-facilitator-proof-open.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | same, D2 authority proof opened by keyboard | 3 checks met | 0 | 0 | n/a | PASS |
| 12 | [12-pixel-7-challenge-facilitator-PRIMARY.png](browser-evidence-2026-09-25/screenshots/12-pixel-7-challenge-facilitator-PRIMARY.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | pixel-7 | facilitator@inspect.local.test | same as desktop primary surface | 1 failed req | 0 | 0 | 8 stops, 0 w/o focus | FAIL |
| 13 | [13-desktop-session-draft-facilitator.png](browser-evidence-2026-09-25/screenshots/13-desktop-session-draft-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | desktop | facilitator@inspect.local.test | Session DRAFT; Facilitator has NO SESSION-scoped control yet (HD-1) | 3 failed req | 0 | 0 | 7 stops, 0 w/o focus | FAIL |
| 14 | [14-desktop-session-question-generation-controller-participant.png](browser-evidence-2026-09-25/screenshots/14-desktop-session-question-generation-controller-participant.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | desktop | facilitator@inspect.local.test | Session QUESTION_GENERATION; Burst ACTIVE HUMAN_ONLY; viewer = controller + participant | 2 failed req | 0 | 0 | 2 stops, 0 w/o focus | FAIL |
| 15 | [15-desktop-session-question-generation-owner-participant.png](browser-evidence-2026-09-25/screenshots/15-desktop-session-question-generation-owner-participant.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | desktop | owner@inspect.local.test | QUESTION_GENERATION; Owner = participant, not Session controller | 7 failed req | 0 | 0 | 2 stops, 0 w/o focus | FAIL |
| 16 | [16-desktop-session-question-capture-frozen-facilitator.png](browser-evidence-2026-09-25/screenshots/16-desktop-session-question-capture-frozen-facilitator.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | desktop | facilitator@inspect.local.test | Session QUESTION_CAPTURE; Burst COMPLETED; frozen human set (fingerprint verified) | 3 failed req | 0 | 0 | 7 stops, 0 w/o focus | FAIL |
| 17 | [17-desktop-session-question-capture-frozen-owner.png](browser-evidence-2026-09-25/screenshots/17-desktop-session-question-capture-frozen-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | desktop | owner@inspect.local.test | Session QUESTION_CAPTURE; Burst COMPLETED; frozen human set (fingerprint verified) | 3 failed req | 0 | 0 | 8 stops, 0 w/o focus | FAIL |
| 18 | [18-pixel-7-session-question-capture-frozen-owner.png](browser-evidence-2026-09-25/screenshots/18-pixel-7-session-question-capture-frozen-owner.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/sessions/e9359f30-b993-53fb-9021-e6c271cc19c8` | pixel-7 | owner@inspect.local.test | QUESTION_CAPTURE, frozen set | 1 failed req | 0 | 0 | 8 stops, 0 w/o focus | FAIL |
| 19 | [19-desktop-landing-outsider-empty.png](browser-evidence-2026-09-25/screenshots/19-desktop-landing-outsider-empty.png) | `/workspaces` | desktop | outsider@inspect.local.test | authenticated; member of nothing | 1 checks met | 0 | 0 | 5 stops, 0 w/o focus | PASS |
| 20 | [20-desktop-workspace-outsider-denied.png](browser-evidence-2026-09-25/screenshots/20-desktop-workspace-outsider-denied.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007` | desktop | outsider@inspect.local.test | not a member → server denies | 3 checks met | 0 | 0 | 4 stops, 0 w/o focus | PASS |
| 21 | [21-desktop-challenge-not-found.png](browser-evidence-2026-09-25/screenshots/21-desktop-challenge-not-found.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/00000000-0000-4000-8000-000000000000` | desktop | facilitator@inspect.local.test | Challenge id unknown in this Workspace | 1 failed req | 0 | 0 | 4 stops, 0 w/o focus | FAIL |
| 22 | [22-desktop-workspace-malformed-rejected.png](browser-evidence-2026-09-25/screenshots/22-desktop-workspace-malformed-rejected.png) | `/workspaces/not-a-uuid` | desktop | facilitator@inspect.local.test | malformed id → server rejects (input, not authority) | 1 checks met | 0 | 0 | 4 stops, 0 w/o focus | PASS |
| 23 | [23-desktop-challenge-loading-latency-2s.png](browser-evidence-2026-09-25/screenshots/23-desktop-challenge-loading-latency-2s.png) | `/workspaces/7f9be38a-20a6-43ac-9a67-8773d9863007/challenges/3c646e0a-c53f-40a2-820b-29a2e48f4ec2` | desktop | facilitator@inspect.local.test | projection not yet confirmed (2 s network latency, CDP emulation; no interception) | 1 checks met | n/a | n/a | n/a | PASS |

In run 1 the `?_rsc=` `net::ERR_ABORTED` lines were still counted as failures (see §7, B-1); state 9 is the real
D-1 failure (502).

## 6. Browser proof summary (run 2, 22 fully instrumented states)

| Requirement | Result |
|---|---|
| DOM rendered | all states (screenshots + DOM checks) |
| CSS assets loaded | 1 stylesheet `/_next/static/chunks/155y1v2gu283g.css` on every state; design token `--accent` resolved everywhere |
| `_next/static` requests | 265, all 200 (0 non-200) |
| Unexpected 4xx / 5xx | **0**. Expected and asserted: 401 `/api/auth/me` (anonymous), 403 overview (outsider), 404 unknown Challenge, 400 malformed Workspace id |
| Browser console | only the browser's own "Failed to load resource" lines for exactly those expected 400/401/403/404; 0 page errors |
| Failed requests | 0 (47 aborted Next.js `_rsc` link prefetches, cancelled by navigation, recorded separately: B-1) |
| Authenticated session | verified: `/api/auth/me` → `ok` + userId for each identity; cookie host-only on `127.0.0.1`, HttpOnly |
| Redirect chains | anonymous `/` → `/login`; after login `/login` → `/` → `/workspaces` (desktop + Pixel 7) |
| Server projection vs visible UI | every state compares visible state/controls with the projection read in the same session; `localTruthDetected = false` everywhere |
| Desktop 1280×860 + Pixel 7 | both reviewed (login, landing, Workspace, Challenge, frozen Session) |
| Keyboard / focus | 21 focus walks, 2–10 stops each, **0 stops without visible focus**; proof disclosure opened by keyboard with focus kept |
| axe WCAG 2 A/AA | **0 serious/critical, 0 violations of any impact** |
| Horizontal overflow | 0 px everywhere |
| Loading / empty / error states | loading (2 s latency), empty (outsider), denied (outsider), not found (unknown Challenge), rejected (malformed id): all reviewed, all PASS |

## 7. Defects

### D-1 — REPAIRED (runtime-only, not tracked): inspection proxy returned 502
- Route/state: `/workspaces/[w]` as Facilitator (run 1, state 9). Symptom: the Workspace page showed a read
  boundary instead of the Challenges and "Frame a new Challenge" (`screenshots/09-desktop-workspace-facilitator.png`).
- First Broken Relation: **inspection proxy → upstream connection reuse**. Node 22's default HTTP agent pools
  connections (`keepAlive: true`); uvicorn closes idle keep-alive connections after 5 s. A pooled socket reset
  in flight made the proxy answer 502. The API logged no error (request never reached it).
- MUST BECOME TRUE: every proxied request reaches a live upstream connection. MUST REMAIN IMPOSSIBLE: a proxy
  502 for a healthy API. Falsifier: `harness/proxy-keepalive-race.mjs`.
- RED (mechanism, reproducible): pooled keep-alive agent, reuse at the 5 s boundary → **3/192 and 7/192 socket
  errors**. GREEN: no-reuse agent → **0/192 twice**.
- Repair: `runtime/proxy.mjs` uses `new http.Agent({ keepAlive: false })` (diff vs `proxy.before-repair.mjs`).
- Integration: through the repaired proxy 288/288 and 704/704 → 200. Browser: run 2 state 9 PASS
  (`run-2-after-repair/screenshots/09-desktop-workspace-facilitator.png`).
- **Proof limitation (honest):** the same race could **not** be reproduced end-to-end through the *old* proxy:
  0 errors in 576 + 1408 requests (`proxy-race-through-proxy.mjs`, `proxy-race-fine.mjs`), most likely because
  Node 22's `globalAgent` (used by the old proxy) also expires idle sockets at 5 s itself, narrowing the window.
  The browser-observed 502 (1 occurrence, run 1) is the only end-to-end RED. The repair removes the mechanism by
  construction (no socket is ever reused), which the mechanism falsifier proves.

### D-2 — OPEN_VISIBLE_DEFECT (SF-01, tracked code; not repaired in this pass)
- Route/state: any SF-01 page whose READ receives an unrecognizable response (seen in run 1 state 9: the proxy's
  502 plain-text body). `inquiryClient` maps it to `indeterminate` / `UNRECOGNIZED_SERVER_RESPONSE`.
- Symptom: the read boundary is titled "The system cannot currently determine whether the requested change
  committed." — on a read, where no change was requested (see run-1 screenshot 09).
- First Broken Relation: `lib/field/outcomeSemantics.ts` titles are path-independent; doc 21 §39 INDETERMINATE
  language is mutation language, while doc 21 §14 gives the read path its own meaning ("latest projection
  unavailable"). `ReadBoundary` uses the mutation title for a read.
- Severity: low–medium (a false visible claim, but only on unrecognizable read responses; the only observed
  trigger, D-1, is repaired). Blocks inspection: **no**.
- Proposed derivable repair (awaiting authorization): read-path titles for INDETERMINATE/NETWORK_FAILURE derived
  from doc 21 §14 read semantics; TDD falsifier: `describeOutcome("indeterminate","read").title` must not speak of
  a requested change.

### D-3 — OPEN_VISIBLE_DEFECT: `/login` has no page layout
- Route/state: `/login`, anonymous, desktop + Pixel 7 (run 2 states 1–2). Symptom: flush-left bare form,
  browser-default button. Global CSS **does** load (tokens, fonts, input styles apply; §6).
- First Broken Relation: the login page never received the F02/SF-01 layout (bare `<main>`, no container,
  no `.field`, no `.button`); SF-01 scope deliberately excluded `/login` (WU-SF01.4). Not a delivery defect.
- The harness check "login uses a layout container" is the falsifier: it FAILS today (the only failing check
  in run 2) and will pass once a layout is applied.
- Severity: low (cosmetic; login works: all authenticated states were reached through this page). Blocks
  inspection: **no**. Belongs to the production-authentication Field that will replace this page.

### Session page (F02/F03 page; SF-01 Stage 2 not applied) — OPEN_VISIBLE_DEFECTs, known Stage-2 scope
| Id | State | Symptom | First broken relation | Severity | Blocks inspection |
|---|---|---|---|---|---|
| S-1 | QUESTION_GENERATION after capture (run-2 #14) | page-level "Committed. The canonical state below was re-read…" banner persists after the action | page-local outcome model (F02), WU-SF01.8 I-5 | low | no |
| S-2 | QUESTION_GENERATION (#14) | "Next lawful step: No Session step is available in this phase" while "Complete Burst…" **is** available in the Burst panel | Session steps list ignores Burst-scoped actions (page composition) | medium (misleading orientation) | no |
| S-3 | QUESTION_CAPTURE (#16–18) | freeze marker `FROZEN` styled as an *authority* tag; fingerprint + integrity permanently on the surface | origin/proof grammar not applied (WU-SF01.8 I-6/I-7) | low | no |
| S-4 | all Session states | position is a breadcrumb + a 13-step linear list incl. future phases | page-centric position (SF-01 First Broken Relation, Session page not yet re-homed) | low | no |
| O-1 | CHALLENGE_CAPTURE, admitting participants | a participant selected while a previous Command is still settling is silently reset by the page's post-commit `setParticipant("")`; the select visibly resets, so the visible state stays consistent | page-local state reset after commit | low | no |

### B-1 — benign, recorded: aborted Next.js prefetches
`?_rsc=…` requests with `net::ERR_ABORTED` are background link prefetches cancelled by the next navigation (run 1
counted them as failures; run 2 records them as `prefetchAborted`, 47 total). Any COMPLETED prefetch that is not
2xx would still fail the state (none occurred).

## 8. Change reconstruction

| Item | Value |
|---|---|
| Starting HEAD (this review) | `644e1c8ce340a9c2475132b717648f57dee1a541` |
| Current HEAD | `644e1c8ce340a9c2475132b717648f57dee1a541` (no commit) |
| Tracked files changed | **none** (no application, test, infra or architecture change) |
| Untracked (new) | `docs/implementation/field-reports/SF-01/review/FRONTEND_BROWSER_REVIEW.md` (this report) and `review/browser-evidence-2026-09-25/**` (harnesses, runtime copies, 2 runs of screenshots, results, manifests) — review evidence, nothing else |
| Runtime-only changes | proxy repair (D-1) in the mounted runtime file (+ copy in `runtime/`); container restart to load it; inspection-DB data (4 identities incl. NON_PROOF seed; Workspace, Challenge, grants; Sessions `7189d011…` (aborted first harness attempt: CHALLENGE_CAPTURE, Burst PREPARED, 0 participants — truthful residue), `e9359f30…` (run 1) and `5170649f…` (run 2), both QUESTION_CAPTURE with a COMPLETED Burst, verified via `/api/.../position`) |
| Tests affected | none (product tests unchanged; the harness is an evidence tool) |
| Browser effects | D-1 gone (run 2 #9 PASS) |
| Downstream relations | D-2 and D-3 proposed for authorization; S-1..S-4, O-1 belong to Stage 2 (Session page) |
| Deliberately unchanged | all tracked code; `/login`; Session page; ledgers (WAIT_FOR_F04_ARCHITECTURE_RECONCILIATION); F04 |

## 9. Recursive DeepSweep (browser → reports)
- Browser: 23 states × runs, instrumentation above. Static assets: all 200. Auth: real login, host-only HttpOnly
  cookie on the inspection origin; 12 h server sessions (doc 18); logout present in every authenticated header.
- Frontend components: SF-01 FieldFrame / RelationTrace / EffectSurface / ReadBoundary / ProofDepth / Origin on
  Workspaces, Workspace, Challenge; F02/F03 components on the Session page (unchanged).
- Projection → API → application: every visible state/control matched `/api/…` projections read in the same
  session (overview, challenge detail, position incl. `questionSet`, `actions`); no local truth.
- Boundary / authority: denied (non-member), rejected (malformed), not found, unavailable-with-reason (Owner:
  Challenge framing; Owner: Open Session) all rendered from server verdicts; Session control resolved at
  SESSION scope (HD-1) — Begin setup unavailable until the Owner's grant; completion only for the controller.
- Persistence / origin: frozen texts and order equal the server's frozen set; `data-verified="true"` equals the
  server's fingerprint verification; authors shown only after completion (HD-13).
- Runtime: isolated project; other Field's containers untouched; no host port besides `127.0.0.1:13100`.
- Tests / reports: product ladder unchanged since WU-SF01.8 (vitest 196, mocked 81, real stack 14); this report
  + manifests + results are the review record.

## 10. Inverse DeepSweep (visible claim → origin)
| Visible claim | DOM / component | Projection / API | Application / boundary / authority | Persisted state → origin | Proven |
|---|---|---|---|---|---|
| "New Session (possible next relation)" (Facilitator, Challenge) | RelationTrace `data-status=possible` | `challenge_detail.capabilities.openSession.available` | `_holds(SESSION_CONTROL_RIGHT, CHALLENGE:<c>)` | ACTIVE binding ← GrantHumanAuthorityBinding by the governance root ← FOUNDING | yes (run 2 #10) |
| "New Session (not available now)" + reason (Owner) | trace + `Unavailable` | `openSession.available=false`, reason text | same resolver, no binding for Owner | no binding row | yes (#5, #8) |
| Session named "Session opened <time>" + DRAFT | sessions list + StateName | `challenge_detail.sessions[].createdAt/state` | CreateSession | `sessions` row | yes (#5, #10) |
| Owner's own question only while ACTIVE | OwnQuestions | `questionSet.visibility=OWN_ONLY_WHILE_ACTIVE`, `mine` | HD-13 server filter | question + membership rows (PARTICIPATION) | yes (#15) |
| Frozen set, verified, authors | FrozenQuestionSet | `questionSet.frozen` (verified, questions) | `verify_frozen_set` recomputes fingerprint | CMD_COMPLETE_BURST bundle (BINDING @ SESSION) ← captures (PARTICIPATION) | yes (#16–18) |
| "Denied" boundary (outsider) | ReadBoundary `orientation-denied` | `GET /workspaces/{w}` → denied reason | BND membership | no membership row | yes (#20) |
| Read boundary "cannot determine … requested change committed" (run 1 #9) | ReadBoundary | `indeterminate` synthesized by the client for an unparseable 502 | — (request never reached the application) | none | **chain breaks: false claim → D-2** |

## 11. Final state
- Working tree: HEAD `644e1c8`, no tracked change; review evidence untracked (not committed, not tagged, not pushed).
- Inspection runtime: up at http://127.0.0.1:13100 (repaired proxy); stop command in §1.
- Open visible defects: D-2, D-3, S-1..S-4, O-1 (none blocks human inspection). Repaired: D-1 (runtime-only).
- Proof limitation: D-1 end-to-end RED through the old proxy not reproducible on demand (§7).
