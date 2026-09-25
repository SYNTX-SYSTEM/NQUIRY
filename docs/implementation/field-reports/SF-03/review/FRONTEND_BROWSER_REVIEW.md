# SF-03 FRONTEND BROWSER REVIEW — visible-website evidence for the doc 23 delta

Field: SF-03 NQIRY Symbiotic Surface Evolution (doc 23 on the SF-02 Field). Branch `frontend-symbiotic`, uncommitted
on top of `644e1c8`. Review date: 2026-09-25 (runs 1–5). Reviewer tool: real Chromium (Playwright 1.63, headless),
`browser-evidence-2026-09-25/harness/review-harness.mjs`. No network interception; every state's canonical
projection is read from the API with the page's own cookie.

This report is self-contained: an independent reviewer can reconstruct every visible claim from it, the per-run
`MANIFEST.md`, `results.json` and screenshots, `setup-scenario.mjs` and the harness, without the chat transcript.
Pre-existing SF-02 evidence lives under `SF-02/review/` and is not rewritten.

## 1. Runtime
| Item | Value |
|---|---|
| Code under review | this worktree (SF-02 + SF-03, uncommitted); run-5 = the final tree |
| Runtime | compose project `nquiry-sf03-inspect`: fresh Postgres (no host port), this tree's FastAPI, production `next build` + `next start`, same-origin proxy `http://127.0.0.1:13300` |
| Runtime-only files | `browser-evidence-2026-09-25/runtime/start-inspect.sh`, `runtime/proxy.mjs` (unchanged from SF-02) |
| Database | fresh, migrated to head `f6b2c4d9a318` (25 revisions) |
| Other Fields | untouched (`nquiry` project on :3000/:8000/:15432); `nquiry-sf02-inspect` (:13200) kept for side-by-side comparison; `nquiry-sf01-inspect` torn down |

Start / stop (worktree root; `$S` = directory holding `proxy.mjs` + `start-inspect.sh`):
```bash
docker compose -p nquiry-sf03-inspect -f infra/sf01/compose.yaml run -d --build --name nquiry-sf03-inspect-runner \
  --publish 127.0.0.1:13300:13300 -e INSPECT_ORIGIN=http://127.0.0.1:13300 -e INSPECT_PORT=13300 \
  -v "$S:/inspect:ro" runner bash /inspect/start-inspect.sh
docker compose -p nquiry-sf03-inspect -f infra/sf01/compose.yaml down -v --remove-orphans
```

## 2. Identities and scenarios (runtime-only, isolated inspection DB only)
Identities: `owner@inspect.local.test` / `inspect-owner-2026`, `facilitator@inspect.local.test` / `inspect-fac-2026`,
`outsider@inspect.local.test` / `inspect-outsider-2026` (HD-3 DEV-ONLY provisioning inside the runner:
`NQUIRY_DEV_IDENTITY_PROVISIONING=I_UNDERSTAND_THIS_IS_DEV_ONLY python scripts/dev_provision_local_identity.py …`).
Relations through the product (`harness/setup-scenario.mjs`, real commands with authority checks):

| Scenario | Workspace | Challenge |
|---|---|---|
| review (`SF-03 Inspection` / `Why did activation stall after onboarding?`) | `0e4aca27-b2e9-4b90-8ced-3cd909463ec6` | `f59774b3-68f6-4e98-88ca-c957c38675bf` |
| stress (`--stress`: 104-char name / 150-char title) | `c7d64325-a504-4162-865f-de59f409ca55` | `e959a4ec-b3b3-4555-add9-380622ada736` |

## 3. Method per state
As SF-02 (`record`: readiness → screenshot → explicit checks against the projection → axe wcag2a/aa serious/critical →
horizontal overflow → unexpected HTTP → keyboard walk with visible focus → topology). SF-03 adds the probes listed in
WU-SF03.8 (containment, identity centring, instrument columns, ambient, rail stability, lifecycle labels, node overlaps).

## 4. States (run-5 = final tree)
| # | State | Viewport | Doc 23 acceptance item |
|---|---|---|---|
| 1–31 | the SF-02 review states (Access, Overview, Workspace, Challenge PRIMARY, Session DRAFT → QUESTION_CAPTURE, Human Question Field, Frozen Field, empty, denied, not found, rejected, loading, unknown) | desktop, Pixel 7, reduced motion | regression (doc 22) |
| 19 | Human Question Field, wide | 1600 | 7 (instrument constellation), 6 (lifecycle labels readable), 13–14 |
| 32 | Challenge Field, wide | 1600 | 1 (centred identity), 2 (symbiotic breadcrumb), 3 (living background), 5 (expanded distribution), 8–9 (proof/governance beside the action, width used), 13–14 |
| 33 | keyboard focus inside governance | 1600 | 15 (Field/instrument reciprocity) |
| 34 | Workspace Field, wide | 1600 | 4 (node legibility) |
| 35 | Session Field (frozen), wide | 1600 | 6, 8 |
| 36 | Session Field, reduced motion | 1280 | 11 (reduced-motion equivalent: depth without motion) |
| 37–40 | stress Challenge (desktop, wide, phone), stress Workspace (desktop) | 1280 / 1600 / Pixel 7 | 12 (long-label stress), 13 (containment), 14 (collision resistance), 10 (phone capability) |

Run-5 result: **40 / 40** (30 SF-02 regression states + 10 doc 23 acceptance states; axe serious/critical 0, overflow 0, no unexpected HTTP, keyboard focus visible everywhere). Runs 1–4 (39/40, 39/40, 38/40, 40/40; pre-repair trees) are kept with their manifests.

## 5. Defects found by this review
WU-SF03.8 D-SF03-1 (uppercase token width → mid-token break), D-SF03-2 (path visible through a tinted frame); plus
the L3 stress-spec defects recorded in WU-SF03.1/.2/.7. All repaired at the root and re-proven by run-5.

## 6. Open visible items for the human review (Case 2, presentation)
- OV-1: at 1280 px the instruments compose in one column (two columns from 1500 px); whether the two-column
  constellation should start lower (e.g. 1360 px with a narrower topology) is a proportion preference.
- OV-2: the Session Field's later-phase labels use compact names without ordinals; the human may prefer ordinals
  everywhere (the geometry has room on wide screens).
- OV-3: doc 23 §9.4 breadcrumb → Field reciprocity not implemented (optional).
- OV-4: the isolated real-stack F03 protected spec's 90 s budget is marginal on this host under load (WU-SF03.7).

## 7. Reproduction
```bash
# runtime up (section 1); identities provisioned; from apps/web:
node ../../docs/implementation/field-reports/SF-03/review/browser-evidence-2026-09-25/harness/setup-scenario.mjs            # → WS CH
node ../../docs/implementation/field-reports/SF-03/review/browser-evidence-2026-09-25/harness/setup-scenario.mjs --stress   # → WS CH
EVIDENCE_RUN=run-3 node ../../docs/implementation/field-reports/SF-03/review/browser-evidence-2026-09-25/harness/review-harness.mjs <WS> <CH> <STRESS_WS> <STRESS_CH>
THROTTLE=4 BASE=http://localhost:3341 API=http://127.0.0.1:13300 node .../harness/perf-ab.mjs   # ambient cost (needs a next dev on :3341)
```
