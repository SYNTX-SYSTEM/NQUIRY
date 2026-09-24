# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.4 — Adoption on the pre-Session surfaces + isolated mocked lane (L3/L4)

## Mission
Make canonical context shape the pre-Session field. Workspaces, Workspace and Challenge are composed
by Field Frame + Relation Trace + zones + effect relations. Page literals no longer compose them.

## Files changed
- NEW `apps/web/lib/field/useEffectField.ts`: runs one effect relation.
  - Flow: request → send → settle → navigate to the new context OR canonical re-read.
  - Keyed and keyless relations are separate at type level. A synchronous `inFlight` guard blocks double submit. A thrown `send` is INDETERMINATE.
  - `settleCommand` maps the F02 envelope.
- REWRITE `apps/web/app/workspaces/page.tsx`: access regime.
  - Keyless F01 founding: transport loss vs unrecognized response is told apart by a tracking `fetchImpl` passed to the unchanged F01 client, giving `network_failure` vs `indeterminate`.
  - The list is re-read after any outcome. No "try again". The previously unhandled list-read rejection now renders a read boundary.
- REWRITE `apps/web/app/workspaces/[workspaceId]/page.tsx`: Workspace regime.
  - Trace from overview, else the orientation name, else access context.
  - Centre: Challenges. Near: frame a Challenge (keyed) and add a member (F01, keyless).
  - Outer: your standing and the members. Depth D2: held authority classes.
  - A failed re-read keeps the last confirmed projection, marked.
- REWRITE `apps/web/app/workspaces/[workspaceId]/challenges/[challengeId]/page.tsx`: Challenge regime.
  - Trace with the Session relation possible or unavailable.
  - Sessions named by server projection ("Session opened <time>" + SYSTEM STATE), no `Session {i+1}`.
  - Open Session and the grant are keyed effect relations. Controllers moved to proof depth D2.
  - NOT_FOUND keeps only the access context.
- MOD `apps/web/app/globals.css`: **append-only** (1 hunk at EOF, 0 removed lines).
  - Adds typographic roles, edge grammar, trace, field layout, effect, boundary and reconstruction surfaces, proof depth, `.visually-hidden`, `relation-settle` motion (disabled under reduced motion by the existing F02 rule).
  - One rule, drafted then removed before any test, dimmed last-confirmed content with opacity (a contrast/axe risk; the meaning is in words).
- NEW `apps/web/playwright.sf01.config.ts`: isolated mocked lane.
  - Own `next dev` on :3301 with `reuseExistingServer: false`.
  - Unmocked requests go to a dead proxy (Playwright's Chromium proxies loopback, so `localhost:8000` never reaches a running API). Only :3301 is bypassed.
  - Projects: desktop runs all mocked specs; mobile (Pixel 7) runs the SF-01 specs.
- NEW `apps/web/tests/e2e/sf01-field.spec.ts`: 21 tests.

## Preserved contracts (unchanged tests prove it)
- One `h1` per page.
- Exact texts: `orientation-role` / `-governance-capable` / `-denied`, `create-workspace-error`, `add-member-error`.
- `add-member-success`, `command-outcome[data-outcome]` (unique per page, because one current effect per surface), `challenge-create-unavailable`, `session-create-unavailable`, `load-failure`, `orientation-rejected` / `-error`.
- All labels and button names used by the F02 real-stack specs. Button labels no longer change to "Creating…"/"Adding…"; REQUESTED is announced by `EffectIntent` instead.

## Test-first intent (L3)
- **TRUE:**
  - isolation fails closed;
  - the trace comes from the projection; the loading trace is access only; NOT_FOUND invents nothing;
  - Workspace Challenge relation is possible; Session identity is server-projected;
  - an unavailable relation shows the server reason and no control;
  - REQUESTED ≠ COMMITTED;
  - C3-01 unknown consequence with re-read and the same key on repeat;
  - INDETERMINATE retains the key and a definitive outcome releases it;
  - the marker claims a re-read only after it happened;
  - C3-06 committed + unreadable → last-confirmed view, dependent effects blocked, manual re-read;
  - keyless founding → unknown, re-read, no "try again";
  - an unrecognized response → INDETERMINATE;
  - DENIED / REJECTED / FAILED_PRECOMMIT / INDETERMINATE are each distinct;
  - proof opens by keyboard in place;
  - relational order and no overflow;
  - reduced motion keeps meaning.
- **IMPOSSIBLE:** as above, inverted.

## RED → GREEN
- **RED:** the SF-01 spec ran against the pre-SF-01 pages (`git archive bea864b` into the session scratchpad, own `npm ci` from the same lockfile, own server :3302), desktop: **19 failed / 2 passed**.
  - The two passes are expected: the isolation harness, and the CF-07 rule F02 already satisfied (it acts as a regression guard here).
- **GREEN:** isolated lane **81 passed** (39 existing mocked F01/F02 specs unchanged + 21 SF-01 × 2 projects). vitest 170. eslint and tsc clean.
- One lint repair: React Compiler `set-state-in-effect` flagged an `async` loader invoked from an effect. It was rewritten in F02's promise-chain form; behavior is unchanged.

## Lane side effects (disclosed, reverted)
`next dev` (v16) generated `apps/web/AGENTS.md` and `apps/web/CLAUDE.md`, and rewrote `apps/web/next-env.d.ts` (`.next/types` → `.next/dev/types`).
- None of these existed or differed before the run.
- Generated at 20:50:49 by this lane; removed, and `next-env.d.ts` restored with `git checkout`.
- The same generation happens on every `next dev` run in this tree. Re-check `git status` after each lane.

## Accessibility / responsive
- Structural: one `h1`; `nav` "Inquiry position" with `aria-current="location"`; `role=status` for commit and request; `role=alert` for boundaries; native disclosure; the reason code is in text; status words sit outside the links.
- Responsive: the layout is single-column at ≤ 860px with DOM order = relational order, asserted by bounding boxes on Pixel 7. No overflow on desktop or mobile. axe runs in L7 (prepared).

## Residual divergence (disclosed, F03 contact zone)
The Session page still renders with F02 `AppShell` breadcrumbs, F02 `Outcome` and `OUTCOME_TEXT`, which includes "Nothing is assumed to have changed" for mutation network loss (falsifier 17), plus the index-based mobile phase hiding. It is re-homed only in Stage 2 after F03 is published (SF01-HD-3).

## DeepSweep
- Chain: position (CF-01) → PF-01 → CF-02 surfaces → CF-07 (server capabilities only; `governanceCapable` from the F01 server projection) → CF-08 (effect relations) → CF-09 (depth) → API unchanged → persistence unchanged → tests.
- Inverse (Challenge page, possible Session relation): trace segment `session/possible` ← `capabilities.openSession.available` ← `_holds(SESSION_CONTROL_RIGHT, CHALLENGE:<id>)` in `inquiry_queries.challenge_detail` ← an ACTIVE binding.

## Git state
Uncommitted, nothing staged.

## Result
PASS (L3/L4).
