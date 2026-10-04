# NQUIRY LIVE TEST PLAN (sanitized — no passwords, no secrets; UNTRACKED, do not commit)

**Purpose.** Human live review of the exact authorized pair on `https://nquiry.condyn.eu` after its materialization:
the ANALYSIS boundary of WU-CY-01 as projected by the pinned RED producer, without any upgrade of the producer's ceiling.

**Authorized pair.** RED producer `checkpoint-PFC-B5` → `7d3f74e4685b821cc948f45e413c1e0c207259d4` (tree `bc77cc8b…`,
migration head `e8c2a5f1b7d4`; TECHNICALLY_CLOSED, CHECKPOINTED, not REVIEWED_FIELD, not PUBLISHED_FIELD). CYAN consumer
`field-CY-01` → `54f8b4f91b12f7c05c10eb98d6281bbe1ba19859` (tree `f980bde0…`; Human Visual Review PASS 2026-09-28).
Assembly `cy01-b5-20260928T031904Z` (`DEPLOYMENT_MANIFEST.json`).

**Status (2026-09-28T19:00Z): READY_FOR_HUMAN_LIVE_REVIEW.** The pair is live; the production account creation relation
(WU-PFC-AC1 / AC1.1, HD-28: host-operator command, operator `otti@condyn.eu`) is live since 18:50Z; the four review
identities were created through it and every other relation (Workspace, memberships, roles, Challenge, authority
bindings, Sessions, participation, Bursts, questions) through the product API. The automatic live run passed 21/21
(report §24). **Producer now live:** RED `checkpoint-PFC-AC1.1` @ `e91961e4a66ab21d9edf45d74bb43b8fbd324737`
(= `checkpoint-PFC-B5` semantics + account creation) with CYAN `field-CY-01` unchanged; assembly
`ac11-cy01-20260928T182206Z`.

**Live URL.** `https://nquiry.condyn.eu` (API under `/api`). Pair deployed 2026-09-28T03:43Z; api replaced 18:50Z by the
account-creation delta: containers api `521dac0a…`, web `2d92fd34…` (unchanged); migration head `e8c2a5f1b7d4`.

**Proof ceiling (HD-LIVE-1 / HA-20, 2026-09-28).** Live is PRODUCTION; the MockProvider stays unavailable. A live
`Begin analysis` commits TRN-SESS-006 and the producer reports the run as **NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE**:
the derived field reads **"authorized, not yet executed"** (status PENDING, reason AUTHORIZATION_NOT_EXECUTED), no proof
line, no provider. "accepted · MOCK / NON_PROOF" must never appear on live; if it does, that is a falsifier.

## 1. Review users (usernames only; passwords in the local secret plan, never here)

| Purpose | Username (email) | User id | Role | Authority | Participation |
|---|---|---|---|---|---|
| LIVE REVIEW Owner | `owner@livereview.nquiry.condyn.eu` | `91b04e93-2e75-492f-a3e8-f3400bb0e5bf` | Owner (founder, governance root) | WORKSPACE_GOVERNANCE_RIGHT; no Session control | none |
| LIVE REVIEW Facilitator (Maya) | `maya@livereview.nquiry.condyn.eu` | `06b8043d-a83d-4e66-8404-aeb2b6c656fe` | Facilitator | SESSION_CONTROL_RIGHT at CHALLENGE and at SESSION scope for A, B, C, D | participant A, B, C, D |
| LIVE REVIEW Ravi | `ravi@livereview.nquiry.condyn.eu` | `99197c0b-b2b8-4efc-87ee-b68bb779453f` | Contributor | none | participant A, B, C, D |
| LIVE REVIEW Elena | `elena@livereview.nquiry.condyn.eu` | `2162e130-b7b1-4413-b520-94afc4f586ab` | Contributor | none | participant A, B, C, D |

All four were created only through the host-operator command (HD-28; SecurityEvent IDENTITY_CREATED, actor
HOST_OPERATOR `otti@condyn.eu`, TB-17, PRODUCTION); every membership, role, authority, participation, Workspace,
Challenge, Session and Question was created through the product API by the respective user.

## 2. Review data

Workspace **NQUIRY LIVE REVIEW 2026-09-28** `8311d170-2f30-461f-9085-7a0b9e0e34ac` · Challenge "Where does onboarding lose new team admins?"
`b9bc6c4c-d419-4091-a223-7f491c6b8a48` · Session URL pattern `https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/<sessionId>`.

| Session | Id | Direct URL | Proof mode | Starting canonical state | Content |
|---|---|---|---|---|---|
| A | `95f027cb-c279-5a22-81b6-039f83a6366a` | https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/95f027cb-c279-5a22-81b6-039f83a6366a | GOVERNED | QUESTION_CAPTURE (v5), Burst COMPLETED | 3 frozen human questions (Ravi, Elena, Maya) |
| B | `d1827699-2cdc-56e2-be3e-e9834d54686c` | https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/d1827699-2cdc-56e2-be3e-e9834d54686c | FIXTURE_NON_PROOF | QUESTION_CAPTURE, Burst COMPLETED | 2 frozen human questions (Ravi, Elena) |
| C | `493dd951-b26d-5605-84d4-de72336325b1` | https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/493dd951-b26d-5605-84d4-de72336325b1 | GOVERNED | ANALYSIS (BEGIN_ANALYSIS committed through the API by Maya) | 3 frozen questions; derived field "authorized, not yet executed", reason AUTHORIZATION_NOT_EXECUTED (run NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE) |
| D (automation) | `5c257b05-1be6-5a9e-aa9e-9276395bc570` | https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/5c257b05-1be6-5a9e-aa9e-9276395bc570 | GOVERNED | ANALYSIS — consumed by the automatic run (Begin analysis pressed by Maya's browser) | 3 frozen questions; not part of the human steps |

Challenge page: https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/challenges/b9bc6c4c-d419-4091-a223-7f491c6b8a48 · Workspace: https://nquiry.condyn.eu/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac

## 3. Order, click by click

**Step 0 — access.** Open `/login`. Enter a wrong password once: the field answers with a boundary (no success
implied, no alert storm). Log in as Ravi. Expect the Workspaces overview with one visible Workspace for this user.

**Step 1 — Session A as Ravi.** Open Session A by direct URL. Expect: path … › Session › QUESTION_CAPTURE (current
station breathing); core "Frozen human question set", state QUESTION_CAPTURE, "Role: Contributor · Not the Session
controller · Participant", no fixture tag; ring 1–4 passed, 5 current, 6 Analysis later; frozen chamber with the 3
questions verbatim (`human` tag, immutable, fingerprint verified); **no "Begin analysis"**; boundary mark
MISSING_AUTHORITY with the server's reason; derived field chamber "not begun", Generations 0, no Proof, no provider;
proof chamber "Proof mode GOVERNED". Refresh the browser: identical. Log out, log in again as Ravi: identical.

**Step 2 — Session A as Maya (cross the boundary).** Log out, log in as Maya, open Session A. Expect "Begin analysis"
in the frozen chamber with its explanation; core meta "Session controller · Participant"; Session control chamber:
granted by Owner → SESSION_CONTROL_RIGHT → held by Maya → this Session. Press **Begin analysis**. Expect, in order:
"Committed" with reconstruction "reading" (ring and state unchanged) → after the re-read: ANALYSIS current on the ring
and the path, resonance event "ANALYSIS BEGUN" once → derived chamber with the producer's status (see ceiling) →
3 questions unchanged → no further affordance → proof spine `CMD_BEGIN_ANALYSIS` by Maya, SESSION scope, commit id.
Reload: the same state re-read. Press nothing else.

**Step 3 — Session C as Maya, then Ravi.** Open C as Maya: ANALYSIS current; derived chamber identical in shape to A
after Step 2. Log in as Ravi, open C: same derived field visible (frozen-set audience), no affordance, no boundary mark
for BEGIN_ANALYSIS (not relevant in ANALYSIS).

**Step 4 — Session B as Maya.** FIXTURE_NON_PROOF tag at the core, "Proof mode FIXTURE_NON_PROOF" in the proof chamber,
spine still names the governed commit; "Begin analysis" available; optionally press it: ANALYSIS, tag stays, derived
output as the producer reports it.

**Step 5 — Challenge page as Maya.** "Open a Session" chamber: checkbox "Open as a Fixture Session" unchecked by
default with the immutable-Fixture note. Do not open a fourth Session unless intended.

**Step 6 — authority denial (API, optional).** As Ravi, `POST /api/workspaces/8311d170-2f30-461f-9085-7a0b9e0e34ac/sessions/95f027cb-c279-5a22-81b6-039f83a6366a/transitions/begin-analysis`
with the version seen: `denied`. As Maya, the same request with the old version after Step 2: `stale`/`blocked`, never a
second transition.

**Step 7 — responsive and accessibility.** Repeat Steps 1–2 views at 1280 × 860, 1600 × 1000 and a phone viewport
(Pixel 7): no horizontal scroll, organ scrolls internally on desktop, chambers stack in order on the phone. Run axe
(wcag2a/aa) on the Session page in QUESTION_CAPTURE and ANALYSIS: 0 serious/critical. Enable "reduce motion": every
animation stops, every meaning stays.

## 4. Expected authority and denial states
Ravi: capability projected as unavailable with reason (MISSING_AUTHORITY class); Owner: no Begin analysis, derived field
only if the producer serves the frozen set to the Owner; Maya: available exactly while QUESTION_CAPTURE.

## 5. Preservation checks
`https://condyn.eu`, `https://admin.condyn.eu` and the other vhosts answer as in the baseline; the two real NQUIRY
accounts can still log in; the real Workspace is still listed for its founder; nothing of the review namespace appears
to the real accounts.

## 6. Troubleshooting
404 on begin-analysis = the F03 producer is still live (cutover not done). "authorized, not yet executed" = no AI
provider on production (expected without an HA decision). A page that shows an affordance the API denies = falsifier;
stop and report.

## 7. Cleanup and rollback
Cleanup: `evidence-2026-09-28/CLEANUP_MANIFEST.md` (review identities and data only after explicit authorization; there is
no delete Command, so removal is itself a separate authorized operation). Rollback of the account-creation delta: the
report's §26 (compose `_baseline-pre-AC1-*/compose.yaml.pre`, image `nquiry-api:pre-ac1`, `up -d --no-deps api`).
Rollback of the pair: the report's §19.

## 8. What the automatic run already did (do not repeat on A)
It pressed "Begin analysis" only on Session D, denied Ravi's API begin-analysis on A (403, A unchanged), and changed
nothing else. A, B and C are exactly in their starting states. Results: `evidence-2026-09-28/live-review-auto/`.

## 9. Known visual observation (CYAN, for your judgement)
At 1280 px the centred wordmark overlaps the breadcrumb's current-state chip (e.g. "QUESTION_CAPTURE") in the top bar
(`live-review-auto/02-ravi-session-A-desktop.png`). Not changed: CYAN is out of scope for this Field.
