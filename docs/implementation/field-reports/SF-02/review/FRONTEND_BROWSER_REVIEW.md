# SF-02 FRONTEND BROWSER REVIEW — visible-website evidence

Field: SF-02 NQIRY Symbiotic Interaction Field (materialization of doc 22). Branch `frontend-symbiotic`,
uncommitted on top of `644e1c8`. Review date: 2026-09-25 (runs 1–6 between 00:50Z and 02:11Z).
Reviewer tool: real Chromium (Playwright 1.63, headless), driven by `browser-evidence-2026-09-25/harness/review-harness.mjs`.
No network interception; every state's canonical projection is read from the API with the page's own cookie.

This report is self-contained: an independent reviewer can reconstruct every visible claim from it, the
per-run `MANIFEST.md`, `results.json` and screenshots, and the harness, without the chat transcript.

## 1. Runtime
| Item | Value |
|---|---|
| Code under review | this worktree (SF-02, uncommitted); run-6 = the final tree |
| Runtime | compose project `nquiry-sf02-inspect` (recipe `infra/sf01/compose.yaml`, unchanged): fresh Postgres (no host port), this tree's FastAPI (in-container :8000), production `next build` + `next start` (:3000 in-container), same-origin proxy `http://127.0.0.1:13200` |
| Why a proxy | the API's CORS origin is fixed to `http://localhost:3000` (another Field's running stack); the proxy serves pages and `/api/*` from ONE origin so no cross-origin call exists and nothing in the application changes |
| Runtime-only files | `browser-evidence-2026-09-25/runtime/start-inspect.sh`, `runtime/proxy.mjs` (mounted read-only; not part of the application) |
| Database | fresh, migrated to head `f6b2c4d9a318` (25 revisions) |
| Other Fields | untouched (`nquiry` project on :3000/:8000/:15432; `nquiry-sf01-inspect` on :13100) |

Start / stop (from the worktree root; `$S` = directory holding `proxy.mjs` + `start-inspect.sh`):
```bash
docker compose -p nquiry-sf02-inspect -f infra/sf01/compose.yaml run -d --build --name nquiry-sf02-inspect-runner \
  --publish 127.0.0.1:13200:13200 -e INSPECT_ORIGIN=http://127.0.0.1:13200 -e INSPECT_PORT=13200 \
  -v "$S:/inspect:ro" runner bash /inspect/start-inspect.sh
docker compose -p nquiry-sf02-inspect -f infra/sf01/compose.yaml down -v --remove-orphans
```

## 2. Identities (runtime-only, isolated inspection DB only)
Provisioned with the repository's HD-3 DEV-ONLY script (`scripts/dev_provision_local_identity.py`): identity +
local credential only. Every relation below was then established through the product (governed Commands).

| Login | Password | Relations established through the product |
|---|---|---|
| `owner@inspect.local.test` | `inspect-owner-2026` | founded Workspace `SF-02 Inspection` (governance root); participant in the reviewed Sessions |
| `facilitator@inspect.local.test` | `inspect-fac-2026` | Facilitator; framed the Challenge `Why did activation stall after onboarding?`; SESSION_CONTROL_RIGHT at CHALLENGE and SESSION scope (granted by the Owner) |
| `outsider@inspect.local.test` | `inspect-outsider-2026` | member of nothing (empty overview, denied Workspace) |

Workspace `56b52168-491d-48f5-bbc6-73ff96267919`, Challenge `24a4ea2f-9dd6-48da-9d98-81bc8716a2fa`; each run opens
its own Session through the UI (id in the run's `results.json`).

## 3. Method per state
`record(page, meta, verify)`: wait for the surface's readiness marker → screenshot → `verify` reads the API
projection and returns explicit checks (`check(name, expected, observed, source)`) → axe (wcag2a + wcag2aa,
serious/critical) → horizontal overflow → unexpected HTTP responses (every non-2xx not declared expected for the
state) → effective topology mode from computed style (`.orbit` absolute = orbit, else stack). A state PASSES only
when every check holds and axe/overflow/HTTP are clean. Reduced motion states use `emulateMedia({reducedMotion:
"reduce"})` and assert computed `animationName === "none"` on the background pseudo-element, the drift groups,
the core and the relation paths.

## 4. States (run-5 = final tree)
| # | State | Viewport | Identity | What is asserted (beyond axe/overflow/HTTP) |
|---|---|---|---|---|
| 1, 3, 5 | Access Field `/ → /login` | desktop, Pixel 7, reduced motion | anonymous | `GET /auth/me` = 401; access core; no topology; no external provider; "Log in" reachable by keyboard; (5) no animation |
| 2, 4, 6 | Access denied | same | wrong credentials | boundary `role=alert`, form retained, no success outcome, submit reachable |
| 7, 9 | Workspace Overview Field | desktop, Pixel 7 | owner | core current; founding node possible; workspace links = server list (names exact); trace = access only; effective mode orbit / stack |
| 8, 10 | Workspace Field | desktop, Pixel 7 | owner | Challenge relation unavailable with the server reason (Owner is not a Facilitator); challenge links = server; members/authority orbit; add member (governance-capable); proof depth closed |
| 11, 12, 13 | **Challenge Field (PRIMARY)** | desktop, Pixel 7, reduced motion | facilitator | core = challenge; sessions orbit with "Open Session" POSSIBLE (server `openSession.available`); session nodes = server sessions; governance orbit holder = server binding; relation paths present; proof depth; (13) animations none |
| 14 | Session DRAFT without control | desktop | facilitator (before the grant) | core DRAFT; lifecycle ring with DRAFT current; "Begin setup" shown only as unavailable with the server reason; no controller affordance |
| 15 | Grant committed | desktop | owner | committed outcome (blue), re-read line; governance node for the holder after re-read; no cyan/green success |
| 16 | CHALLENGE_CAPTURE, Burst prepared | desktop | facilitator | lifecycle reconstructed (DRAFT, SETUP passed; CHALLENGE_CAPTURE current); "Open question generation" blocked with the server reason (no participant); admit affordance |
| 17 | Human Question Field, rejected input | desktop | facilitator | core human (cyan); REJECTED boundary announced with plain-words reason; text retained; nothing stored (API count unchanged); expected HTTP 400 |
| 18 | own question (controller) | desktop | facilitator | own question exact text, `human` origin; count for the controller; timer presentation-only; "Complete Burst…" offered; no peer content |
| 19 | participant own-only | desktop | owner | own question only (HD-13); the controller's text absent from the DOM; no Complete Burst; participants as relation nodes without content |
| 20 | Human Question Field on the phone | Pixel 7 | owner | stack order core → lifecycle → active phase → governance → proof; capture reachable; effective stack; lifecycle rows uniform (D3) |
| 21 | completion requested, not committed | desktop | facilitator | still ACTIVE; no frozen set before commit; confirmation says irreversible |
| 22, 23 | Frozen Field | desktop | facilitator, owner | core frozen (blue); frozen entries with authors, exact text; verification; no capture form; no editable control; `establishedBy = CMD_COMPLETE_BURST` |
| 24 | Frozen Field on the phone | Pixel 7 | owner | frozen set rendered, no capture form; core frozen; stack; order core → lifecycle → frozen artifact → governance → proof; rows uniform |
| 25 | empty overview | desktop | outsider | `workspaces-empty`; founding still possible |
| 26 | denied Workspace | desktop | outsider | `orientation-denied` with the server reason code; Workspace name not leaked; boundary core; logout reachable; expected 403 |
| 27 | not found | desktop | facilitator | `load-failure[data-outcome=not_found]`; trace = access only; zero nodes; expected 404 |
| 28 | rejected founding | desktop | facilitator | malformed name → REJECTED boundary, distinct from denied; expected 400 |
| 29 | loading (2 s latency) | desktop | facilitator | core `loading`; trace = access only; no nodes; no count |
| 30 | unknown (offline mutation) | desktop | owner | network loss on a keyed Command → `network_failure` (unknown consequence), re-read on reconnection, same Idempotency-Key on repeat |

Run-6 result: 30/30 (85 explicit checks + D3/D8 guards; axe serious/critical 0 on every state; overflow 0; no unexpected HTTP). Runs 1–5 are kept with their manifests (19/30, 30/30, 30/30, aborted by D7 at state 8, aborted by D8 at state 11).

## 5. Defects found by this review
See WU-SF02.8 (D1–D6): reduced-motion pseudo-elements, accessible names, phone stack rows, contrast during a
text animation, background cost (D5, found by the real-stack lane and reconstructed with `harness/perf-ab.mjs`),
node meta overflow. All repaired at the root and re-proven by run-6 and the lanes of WU-SF02.7.

## 6. Open visible items for the human review (not defects against a stated rule)
- OV-1 (closed as D8): ring 2 now starts half an inner step after the top, so no outer node shares a spoke with an inner node.
- OV-2: the lifecycle ring holds 13 nodes with dot density for later phases; the numbers of later phases are
  visible in the dots and their names are assistive-only until reached (22 §16.2). The human may prefer names
  for the next two phases instead of one.
- OV-3: no reduced-motion screenshot of the Frozen Field or of a Session state exists in the set (reduced motion
  is proven on Access and Challenge states and by the mocked lane's global rule).

## 7. Reproduction
```bash
# from apps/web, runtime up (section 1), identities + scenario as in section 2
EVIDENCE_RUN=run-5 node ../../docs/implementation/field-reports/SF-02/review/browser-evidence-2026-09-25/harness/review-harness.mjs <WS> <CH>
THROTTLE=4 BASE=http://localhost:3341 API=http://127.0.0.1:13200 node .../harness/perf-ab.mjs   # D5 measurement (needs a next dev on :3341)
```
