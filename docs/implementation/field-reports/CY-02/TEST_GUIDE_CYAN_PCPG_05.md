# TEST GUIDE — CYAN-PCPG-05 · Actor raw intent observation → live governance membrane

**Field:** CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, commit `b0a5101fb787bd18092b632f0419366b350f110d` on `pfc-integration`)
**Status of the Work Unit:** FIELD_GREEN_WITH_DISCLOSED_CEILINGS · TECHNICALLY_CLOSED · HUMAN_FRONTEND_ACCEPTANCE · CHECKPOINTED.
Not REVIEWED_FIELD. Not PUBLISHED_FIELD.
**This document:** a self-contained test manual (documentation only; it changes nothing).

## 1. Purpose and scope

CYAN-PCPG-05 materializes the relation by which an authenticated actor observes a drafted intent for a Session and
sees the governance observation of that intent on the Session object:

```text
ACTOR
→ RAW INTENT                      (the actor's own draft, DATA, never instruction or authority)
→ submitPromptObservation(...)    (apps/web/lib/api/pcpgClient.ts — CYAN-PCPG-01)
→ PCPG-R12/1                      (RED Architecture 26 R-12 via B-10, serialized by application.http_pcpg)
→ ObservationPresence             (apps/web/lib/field/observation.ts — CYAN-PCPG-05)
→ presentationOf(...)             (apps/web/lib/field/pcpgPresentation.ts — CYAN-PCPG-02)
→ GovernanceMembrane              (apps/web/components/field/GovernanceMembrane.tsx — CYAN-PCPG-04)
```

Laws this guide tests, verbatim:

```text
OBSERVE != EXECUTE
OBSERVE != SEND
RAW INTENT != AUTHORITY
AUTHENTICATED ACTOR != AUTHORIZED EFFECT
GOVERNANCE OBSERVATION != PROVIDER CALL
CLIENT INPUT != GOVERNANCE RESULT
OBSERVATION != CANONICAL STATE
RELOAD → NO_OBSERVATION
```

**Materialized:** RAW INTENT PRODUCER · OBSERVATION PRESENCE · REAL PCPG-R12/1 PATH (proven) · SUPERSESSION (proven).
**Explicitly not materialized:** PERSISTENCE (none) · SEND · PROVIDER CALL · R-13 (not started) · attachment rendering
at the mapped targets · any production or PURPLE change.

## 2. Checkpoint identities (verified from Git)

| Identity | Tag | Tag object | Target commit | Tree |
|---|---|---|---|---|
| CYAN-PCPG-05 (this Work Unit) | `checkpoint-CY-PCPG-05` | `8ccd3c3ae07828079ff0e17dbc39de4c1e43b8b1` (signed) | `2d6163bfda1827815f4b3f99b74c4b9dea34a948` | `b76b1082a39d5a5240a0fcc048280afdd930a35d` |
| Base | `checkpoint-CY-PCPG-04` | `26a8c2599edc0aad1e351b7deb582c1a029e4d0a` | `daeff13f267ff78bf468f871f2e23b993e7150f3` | `41db958daa0612e2d466289ca75fc32702f4d79b` |
| Local/test RED producer pin (new) | `checkpoint-PFC-PCPG-18` | `0e12895fc64299abde1eb5115303f962b1c227af` (signed) | `41b4324a75077ec33b00ed3a878db7a318fc00d8` | `0631c936f99c9356f6082f05b460815a09632c7b` |
| Local/test RED producer pin (previous) | `checkpoint-PFC-B5` | `fd3d5600132e4dcb9203702d500daccf4c6d0439` (signed) | `7d3f74e4685b821cc948f45e413c1e0c207259d4` | `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750` |

`origin/frontend-symbiotic` = `2d6163bf…` = `checkpoint-CY-PCPG-05^{}` (remote-verified). The checkpoint's parent is
the documentation commit `f9f9ca35d129a183fd594a2432776257831fa395` (PCPG-04 acceptance record) on top of the base.

**Pin transition (local/test lanes only):** `checkpoint-PFC-B5` (`7d3f74e4685b821cc948f45e413c1e0c207259d4`) →
`checkpoint-PFC-PCPG-18` (`41b4324a75077ec33b00ed3a878db7a318fc00d8`). Migration head unchanged (`e8c2a5f1b7d4`): no
migration delta is required for this CYAN Work Unit. Production nquiry.condyn.eu is untouched and still runs
B5 + AC1.1 (no observation route there); no production cutover, no provider execution. The pin and its history live in
`scripts/run_cy01_real_stack.sh` (PIN_* constants); the lane refuses to start if the tag's object, commit or tree differ.

## 3. Prerequisites

- Worktree at `checkpoint-CY-PCPG-05` (`git rev-parse HEAD` = `2d6163bf…`), `npm ci` done in `apps/web`, Playwright
  Chromium installed, Docker + Compose (for the real-stack lane and the review runtime).
- For the manual review: the local review runtime (§4). Local-only identities and data; never production credentials
  or production data.

## 4. Local review runtime

The runtime of record is the compose project `nquiry-cy01-inspect` (file `infra/cy01/compose.yaml`), published only on
the loopback at **`http://127.0.0.1:13500`**: the pinned RED producer export (`checkpoint-PFC-PCPG-18`, verified by
`/repo/PRODUCER_IDENTITY.json` inside the runner) behind this tree's web app in a production build, with its own
database. It was rebuilt on this checkpoint for the accepted review (§13) and is verifiable at any time:
`curl http://127.0.0.1:13500/login` → 200; `POST …/api/workspaces/<any>/prompt-observations` unauthenticated → 401
(route present; the B5 producer would answer 404).

Rebuild (runner only; never re-seed, the database keeps the review data): the lane's producer export directory as
`CY01_PRODUCER_DIR`, then `docker compose -p nquiry-cy01-inspect -f infra/cy01/compose.yaml run -d --build --name
nquiry-cy01-inspect-runner --publish 127.0.0.1:13500:13500 -e INSPECT_ORIGIN=http://127.0.0.1:13500 -e
INSPECT_PORT=13500 -v <inspect scripts>:/inspect:ro runner bash /inspect/start-inspect.sh` (the start script runs
`db_roles.sql`, `verify_migrations.py`, uvicorn on 8000, `next build` + `next start` on 3000 and a loopback proxy on
13500). The scripts of that runtime live outside the repository, in the operator's scratch space, by design.

**Local review accounts** (identity rows created with the producer's dev-only provisioning script, every other
relation through the product API; passwords are not in the repository and are not reproduced here — they were issued
once to the operator who provisioned the runtime; `apps/web/tests/real-stack/identities.ts` shows the provisioning path):

| Account | Role / authority |
|---|---|
| `facilitator@cy01.local.test` (Maya Torres) | Facilitator; SESSION_CONTROL_RIGHT at CHALLENGE and at SESSION scope for Sessions A, B, C; participant |
| `ravi@cy01.local.test`, `elena@cy01.local.test` | Contributors; participants; no authority |
| `owner@cy01.local.test` | Owner, governance root; no Session control |

Workspace **Onboarding inquiry** `2c8b7729-868c-46e2-af9a-8ef40ba4afee`, Challenge **Where does onboarding lose
enterprise admins?** `49369d62-93a7-452f-bfab-1dacdb1fbc52`, Sessions A `58ed8f33-7074-5593-ad20-2e0382c45941`
(ANALYSIS), B `77276c5e-d912-547c-a9b7-bb5f74c5cf07` (FIXTURE_NON_PROOF), C `b2c9af2a-ff08-5099-9c23-3b3f9ac3ace1`
(ANALYSIS). Session URL pattern: `http://127.0.0.1:13500/workspaces/<workspaceId>/sessions/<sessionId>`.

## 5. The user surface under test

In the Session organ, after the proof chamber and before the derived field: the context chamber

- Title **Your intent** · eyebrow (marker) **observed, never sent**
- Controls: the **Your intent** textarea; **Declared purpose (optional)** input; one button labelled exactly **Observe**
  (Ctrl/⌘+Enter submits).
- There is **no** Send button, Run button, Execute button, Submit-to-AI button, provider selector or provider execution
  control — anywhere on the page, whatever the observation says.
- Observe performs governance observation only: it does not execute the requested action, and it sends nothing to an
  AI provider.
- After an observation the chamber shows the observation's own facts: *Observed* (time, "for this view only; a reload
  returns to “No observation”"), *Digest* (first 12 hex characters of the server's SHA-256 of the raw intent), and
  *Superseded* when applicable. The governance words themselves belong to the membrane in the core
  (`FIELD · <derived label>`, plus `observed at <time>` when a basis exists).

## 6. Request contract

`POST /workspaces/{workspaceId}/prompt-observations`, JSON body

```json
{ "rawIntent": "...", "sessionId": "...", "declaredPurpose": "..." }
```

`declaredPurpose` is sent only when the actor typed one. A query (Architecture 26 I-18): no Idempotency-Key, nothing
persisted server-side. The client may never supply — and `submitPromptObservation` cannot carry — **capability,
authority, governance result, basis, provider eligibility, send gate, proof ceiling**: all stay server-derived
(B-10). Server constraints: `rawIntent` non-blank, ≤ 8000 characters (`RAW_INTENT_REQUIRED`, `RAW_INTENT_TOO_LONG`);
`declaredPurpose` a string ≤ 2000 characters (`DECLARED_PURPOSE_INVALID`, `DECLARED_PURPOSE_TOO_LONG`). Scope:
Workspace membership (`WORKSPACE_NOT_ACCESSIBLE` → `denied`), Session in that Workspace (`SESSION_NOT_FOUND` → `not_found`).
Response: `kind: "ok"` with `governanceObservation` = `{kind:"current", contract:"PCPG-R12/1", …}` or
`{kind:"unavailable", reasonCode}`; the CYAN parser (CYAN-PCPG-01) accepts only contract `PCPG-R12/1` and kinds
`current` / `unavailable`, and fails closed (`MALFORMED_PROJECTION`) on anything else.

## 7. Access and authority

Observation is role-independent for an authenticated Workspace member who may read the Session. The chamber is not
gated by Facilitator role, Session control, Human Authority, participation, governance capability or `viewer.*` (the
component source contains none of them — a proven falsifier). The server stays authoritative: `denied` and
`not_found` are shown verbatim. Proven: a Contributor who is not the Session controller observes (mocked lane) and a
participant without authority observes on the real stack.

## 8. Manual visual test procedure

**TEST A — initial state**
1. Open `http://127.0.0.1:13500/login` (runtime per §4).
2. Log in with a legitimate local review account (e.g. `facilitator@cy01.local.test`).
3. Open the Workspace **Onboarding inquiry**.
4. Open the Challenge **Where does onboarding lose enterprise admins?**
5. Open one existing Session (A, B or C).
6. Confirm the Session organism loads as before (core, lifecycle ring, path, chambers).
7. Confirm the core membrane reads **FIELD · No observation** (`data-membrane-label="NO_OBSERVATION"`, quiet).
8. Confirm the **Your intent** chamber is visible, after the proof chamber.
9. Confirm it is one chamber of the existing organ — same glass, head, marker grammar.
10. Confirm the organism remains visually primary.
11. Confirm there is no second dashboard.
Expected: NO_OBSERVATION; no observation timestamp; no derived governance label; no SEND affordance.

**TEST B — real governance observation**
1. In **Your intent** type exactly: `begin the setup of this session`. Leave **Declared purpose** empty.
2. Press **Observe**.
Expected: the request goes through the real PCPG-R12/1 path (one `POST …/prompt-observations`); the intent is
observed, not executed (the Session's state and version do not change — compare the core state word before and
after); the membrane leaves "No observation"; in the accepted review the observed result was **FIELD · Boundary
reached** (prominent) with `observed at <time>`; the chamber shows *Observed* time and *Digest*; the raw text stays in
the textarea; no provider execution appears; no SEND action appears. The derived label must come from the current
server result (`presentationOf` over the parsed contract); CYAN hard-codes no label — a different Session state or
intent may legitimately yield "Observed", "Partial", "Human Authority required" or "Provider not executable".

**TEST C — ephemerality**
1. After a successful observation, reload the page.
Expected: **FIELD · No observation**; the chamber's facts are gone; the textarea is empty. Why: `ObservationPresence`
is React state only — no database persistence, no localStorage, no sessionStorage, no IndexedDB; the observation is
intentionally ephemeral and actor-local. NO OBSERVATION ≠ CURRENT OBSERVATION.

**TEST D — supersession**
1. Observe a valid intent (TEST B).
2. Perform a legitimate committed Session command that changes `session.version` or `burst.version` — on a DRAFT
   Session as its controller, **Begin setup** (the real-stack proof's canonical case); on any Session, a Session-control
   grant by the Owner.
3. The command's own canonical re-read follows automatically (the effect lifecycle re-reads before showing a commit).
Expected: the membrane reads **FIELD · Superseded** (`data-observation="superseded"`); the chamber adds *Superseded*;
the *Digest* is unchanged (the observation object is never mutated); `canSend` is presented as absent and creates no
action. Rule: supersession compares canonical versions remembered at observation time with the latest re-read — never
a wall clock.

**TEST E — second observation**
1. Observe once; observe again (same or different text).
Expected: the second observation replaces the first in the actor-local presentation; exactly one current observation
per actor and object view; no history is kept or implied.

**Loading:** while Observe is in flight the chamber shows "Observing… the Field is read; nothing is executed." and the
membrane keeps its previous legitimate state (for a first observation: **FIELD · No observation**) until the actual
result arrives. A provisional governance result is never rendered.

## 9. Failure tests

The mocked lane reproduces each; manually they need a server condition. For every failure the previous valid
observation (if any) and the actor's raw text are preserved, the chamber shows the words and the server's reason code
in `[data-testid="observe-failure"]`, and nothing is inferred.

| Result | Expected |
|---|---|
| **REJECTED** (`RAW_INTENT_REQUIRED`, `RAW_INTENT_TOO_LONG`, `DECLARED_PURPOSE_*`) | previous observation and text preserved; "Not observed. The request was invalid; nothing was read." + code |
| **DENIED** (`WORKSPACE_NOT_ACCESSIBLE`) | previous observation and text preserved; "Not observed. The server denied the observation." + code |
| **NOT_FOUND** (`SESSION_NOT_FOUND`) | previous observation and text preserved; "…not found in this Workspace." + code |
| **NETWORK_FAILURE** | previous observation preserved; "The server could not be reached. Nothing is assumed to have changed."; the actor may observe again (a query) |
| **INDETERMINATE** (unrecognizable server response) | nothing inferred; previous observation not replaced; "Outcome unknown…" |
| **MALFORMED PCPG-R12/1** (unknown contract/kind/value/key) | fail closed: membrane **Governance unavailable**, chamber "…could not be read. Governance is unavailable (fail closed)." + `MALFORMED_PROJECTION`; no facts shown |
| **UNAVAILABLE** (`SEMANTIC_OBSERVATION_UNAVAILABLE`, `FIELD_RECONSTRUCTION_UNAVAILABLE`, `PROJECTION_INCOMPLETE`) | membrane **Governance unavailable**; the reason code is in the parsed observation; nothing synthesized (no capability, boundary, authority, provider, proof or send words); never converted into success. Reproducible on the real stack with an unparseable intent such as `日本語のテキストです` |

## 10. Automated proof procedure (from `apps/web`)

| Proof | Command | Result at the checkpoint |
|---|---|---|
| Unit: state machine, chamber, membrane successor | `npx vitest run tests/field/observation.test.ts tests/field/intentObservationChamber.test.tsx tests/field/governanceMembrane.test.tsx` | 32 / 32 |
| Affected suites | `npx vitest run tests/field tests/lib tests/components` | 393 / 393 |
| Mutation proof | `node scripts/pcpg05-mutation-proof.mjs` | 5 / 5 killed, byte-identical restores |
| Mocked browser lane (desktop 1280 + Pixel 7) | `npx playwright test --config playwright.sf01.config.ts tests/e2e/cy05-observation.spec.ts tests/e2e/cy04-membrane.spec.ts tests/e2e/cy01-field.spec.ts tests/e2e/sf04-field.spec.ts tests/e2e/sf05-field.spec.ts` | 96 / 96 |
| Real-stack lane against PCPG-18 (from the repository root) | `bash scripts/run_cy01_real_stack.sh --timeout=300000` | 18 / 18 |
| TypeScript / ESLint | `npx tsc --noEmit` · `npx eslint .` | clean / clean |

The real-stack lane: verifies the pin (tag object, commit, tree, migration head), exports the producer with
`git archive`, writes `PRODUCER_IDENTITY.json`, starts compose project `nquiry-cy01` (own volume, no host ports),
runs the producer's API + this tree's web + Chromium in one namespace, and executes every `*.real.spec.ts`:
`cy05-observation.real`, `cy01-analysis.real`, `f02-accessibility.real`, `f02-inquiry-context.real`,
`f03-accessibility.real`, `f03-protected-question-field.real`, `sf01-field.real`, `wu-02-12-closure.real` — on desktop
and Pixel 7. Output: `apps/web/test-results/cy01-real-stack/` (gitignored). `--timeout=300000` matches the host:
the F03 flows take 2–3.5 minutes each under desktop load.

## 11. Falsifier matrix (24, all proven)

1. Membrane unchanged while the observation is loading (unit: reducer; mocked: held route). 2. Body exactly
`rawIntent` + `sessionId` (+ `declaredPurpose` only when present); no Idempotency-Key. 3. The hook forwards no
governance-derived value. 4. A Contributor without Session control can Observe. 5. A current PCPG-R12/1 observation
produces the real derived membrane label. 6. Unavailable produces only "Governance unavailable". 7. Rejected
preserves the valid observation and raw text. 8. Denied preserves them and exposes the server result. 9. Not-found
preserves them. 10. Network failure preserves them and assumes nothing. 11. A malformed projection fails closed.
12. A second Observe replaces the first. 13. A canonical version change produces Superseded with the digest unchanged.
14. No clock-based supersession exists (source law). 15. Reload returns to No observation. 16. Storage lengths stay
zero. 17. No console/logging of raw intent in the modules. 18. No Send / Run / Execute / Submit-to-AI control.
19. `canSend = true` creates no affordance. 20. Only `GET …/position` and `POST …/prompt-observations` are requested.
21. R-13 untouched. 22. The organism stays primary without overflow. 23. The PCPG-04 membrane semantics stay preserved
(its tests green). 24. The real-stack path is proven against `checkpoint-PFC-PCPG-18`.

## 12. Mutation proof (`apps/web/scripts/pcpg05-mutation-proof.mjs`)

| Mutation | Result |
|---|---|
| M1 provisional governance result rendered while observing | KILLED |
| M2 Observe control relabelled as Send | KILLED |
| M3 observation chamber role-gated | KILLED |
| M4 supersession ignores the canonical versions | KILLED |
| M5 raw intent persisted (localStorage) | KILLED |
Result 5/5 killed; every production file restored byte-identical (sha256-checked).

## 13. Human Frontend Review

HUMAN_FRONTEND_ACCEPTANCE = **ACCEPTED** (2026-10-01, local PCPG-18-backed runtime). Observed manually: "Your intent"
correctly integrated into the Session organism; organism visually primary; no second dashboard; "observed, never
sent" clear; the only action is Observe; no Send / Run / Execute / Submit-to-AI; initial state FIELD · No observation;
the raw intent "begin the setup of this session" produced a real governance observation; the membrane changed to
FIELD · Boundary reached; timestamp and digest visible; no provider execution represented; reload returned to FIELD ·
No observation (observation visibly ephemeral); the existing Session structure remained intact. Authoritative record:
`docs/implementation/field-reports/CY-02/HUMAN_REVIEW_RESULT_PCPG-05.md`.

## 14. Evidence

Root: `docs/implementation/field-reports/CY-02/browser-evidence/pcpg-05/`
- `mocked-lane-summary.txt` — tracked (96 passed).
- `real-stack-lane-pcpg18-summary.txt` — tracked (18 passed, per spec and project).
- `producer.json` — tracked: the exported producer identity (`checkpoint-PFC-PCPG-18`, `41b4324a…`, tree `0631c936…`).
- `screenshots/` — **untracked, not in the checkpoint** (local only, like every evidence run of this line):
  `desktop-chamber-no-observation.png`, `desktop-observed-provider.png` (mocked), `desktop-real-observed.png`
  (real stack), and the three `mobile-*` counterparts (Pixel 7). They are illustrations, not durable evidence.
- Mutation evidence: the script's console output (not stored); re-run to reproduce.
- Checkpoint identity: §2. Work Unit record: `WU-CYAN-PCPG-05.md`.

## 15. Files changed by the checkpoint (from `git show --stat 2d6163bf…`)

`apps/web/app/globals.css` · `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` ·
`apps/web/components/field/IntentObservationChamber.tsx` (new) · `apps/web/lib/field/observation.ts` (new) ·
`apps/web/lib/field/useObservation.ts` (new) · `apps/web/playwright.sf01.config.ts` ·
`apps/web/scripts/pcpg05-mutation-proof.mjs` (new) · `apps/web/tests/e2e/cy05-observation.spec.ts` (new) ·
`apps/web/tests/e2e/sf05-field.spec.ts` (successor truth: the organ lists the `context` chamber) ·
`apps/web/tests/field/governanceMembrane.test.tsx` (successor truth: the page's presence comes from the state machine) ·
`apps/web/tests/field/intentObservationChamber.test.tsx` (new) · `apps/web/tests/field/observation.test.ts` (new) ·
`apps/web/tests/real-stack/cy05-observation.real.spec.ts` (new) · `scripts/run_cy01_real_stack.sh` (pin) ·
`docs/implementation/field-reports/CY-02/WU-CYAN-PCPG-05.md` (new) · `browser-evidence/pcpg-05/{mocked-lane-summary.txt,
producer.json, real-stack-lane-pcpg18-summary.txt}` (new). Parent docs commit `f9f9ca35…`:
`HUMAN_REVIEW_RESULT_PCPG-04.md`, `WU-CYAN-PCPG-04.md`.

## 16. Interpreting a run

Green means: the relation of §1 holds end to end against the pinned producer, with no client-side governance, no
persistence, no SEND and no provider call; the membrane says exactly what the server's observation says, and nothing
when there is none. Any of these is a falsifier that must stop the review: a label while a request is in flight; a
label after a failed request; a Send-like control; a label that survives a reload; a membrane that ignores a version
change; a chamber hidden by role; a request body with any key beyond the three inputs.

## 17. CLAIM CEILING

- CYAN-PCPG-05 is technically closed and Human Frontend Accepted.
- Status: FIELD_GREEN_WITH_DISCLOSED_CEILINGS. It is not REVIEWED_FIELD. It is not PUBLISHED_FIELD.
- The RED producer `checkpoint-PFC-PCPG-18` / contract `PCPG-R12/1` is checkpointed, not reviewed.
- The PCPG-18 pin is local/test only.
- Production nquiry.condyn.eu still runs B5 + AC1.1, without the observation route.
- Observations are currently GOVERNANCE_ADMISSIBLE = false under the current HD-29 conditional state.
- CAN_SEND remains false; provider eligibility remains indeterminate under the current runtime truth.
- R-13 is NOT STARTED.
- The observation is ephemeral and actor-local.
- OBSERVE ≠ EXECUTE ≠ SEND.
- Attachment rendering is NOT STARTED.

## 18. Next First Broken Relation

```text
attachPresentation(presentationOf(observation))
→ rendering at the mapped targets of the Session organism
```
Mapped targets today: question set · burst panel · lifecycle ring · authority chamber · boundary marks · derived
chamber · decision entry (`apps/web/lib/field/pcpgAttachment.ts`). Status: NOT STARTED · NOT AUTHORIZED.

## 19. Troubleshooting

- **Real-stack lane silent for minutes:** normal. The runner builds an image (pip + npm ci + Chromium) and then runs
  eight specs on two projects; the F03 flows take 2–3.5 minutes each. Long periods without terminal output do not
  mean the proof hung. Inspect instead of killing: `docker ps` (project `nquiry-cy01`), `docker logs
  nquiry-cy01-runner-run-…`, and inside the runner the active processes — a Playwright worker, Chromium renderers,
  `next dev`, `uvicorn` — demonstrate active execution; the host's `docker compose ls` shows the project running. Only
  if the runner container has exited without the summary line should the lane be considered failed; then read
  `apps/web/test-results/cy01-real-stack/` and the lane log.
- **Never** stop processes by broad pattern (`pkill -f <pattern>` can kill the shell that issued it); use pids from `pgrep`.
- **A 90 s Playwright test timeout** in the real-stack lane is a budget problem under host load, not a product failure:
  rerun with `--timeout=300000`.
- **The membrane only ever shows "No observation" on a runtime:** the producer behind it has no `prompt-observations`
  route (B5 answers 404) — check `PRODUCER_IDENTITY.json` in the runner and the pin in `scripts/run_cy01_real_stack.sh`.
- **Future proof-infrastructure requirement (ORANGE concern, not implemented here):** STRUCTURED VERBOSE + HEARTBEAT
  for long-running proof runners, so that a reviewer can distinguish progress from a hang without process inspection.
- No secrets belong in this guide or in any evidence file; the review passwords exist only with the operator.
