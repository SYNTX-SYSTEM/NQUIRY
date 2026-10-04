# RECONSTRUCTION — can the Human Frontend Review on 127.0.0.1:13500 cover the authentication / identity projection?

DATE: 2026-10-04 · LINE: `frontend-symbiotic` @ `9b8771d` (`checkpoint-CY-RAIL-01`) · TRIGGER (human effect, verbatim):
"During Human Frontend Review on 127.0.0.1:13500, following the Google login path reaches the REVIEW BOUNDARY because
this review runtime has no PURPLE AUTH routes or Google client. Reconstruct whether the current Human Frontend Review
can legitimately cover the complete authentication/identity projection under this runtime topology."

## Answer
**No.** The :13500 review can legitimately cover the organism, the governance placement (PCPG-06) and the rail
(RAIL-01). It cannot cover the authentication / identity projection, for two independent reasons, and the Google path
reaching the review boundary is the runtime stating the first of them correctly.

## 1. The runtime topology (what :13500 is)
| Relation | Producer on :13500 | Proof class |
|---|---|---|
| Workspaces, Challenges, Sessions, position, bursts, question sets, governance observation (PCPG-R12/1) | the pinned RED producer `checkpoint-PFC-PCPG-18` (`41b4324`) with MockProvider | REAL (checkpointed, not reviewed/published) |
| `GET /api/auth/providers` | the review proxy: a byte copy of the live production body taken 2026-10-03 | FIXTURE_NON_PROOF |
| `GET /api/auth/sessions`, `/api/auth/methods` | the review proxy: live-shape fixtures driven by a review cookie | FIXTURE_NON_PROOF |
| `GET /api/auth/oidc/google/start` (the typed LOGIN start) | the review proxy's **review boundary page** ("no PURPLE AUTH routes and no Google client; no login is proven here") with a FIXTURE transition that only records "the current session was produced by GOOGLE_OIDC" | FIXTURE_NON_PROOF |
| `GET /api/auth/identity` | not served by the pinned RED producer (`auth-identity` routes are PURPLE's) | — |
| `/api/auth/login`, `/auth/me`, `/logout` | the pinned RED producer's local login (the CY-01 review identity) | REAL for RED's local session only |
The runtime was assembled this way on purpose (AUTH/CYAN-02, 2026-10-03): the mocked lanes and the review proxy
carry the SHAPES of the PURPLE contract so that the organism can be reviewed with a real RED producer, while every
AUTH relation is labelled `x-nquiry-review-fixture: FIXTURE_NON_PROOF`. FIXTURE_NON_PROOF != proof, and the human
already decided on 2026-10-03 that "the local fixture review is insufficient" for the identity projection. That
decision produced the same-origin review topology (`/cy-review/` on `nquiry.condyn.eu` → PURPLE `/api/`), which is the
only runtime on which authentication / identity can be reviewed.

## 2. The lineage (what :13500 projects)
The identity projection this tree carries is the **pre-hold** model (`checkpoint-CYAN-IDENTITY-PRESENTATION-01`,
TECHNICALLY_PROVEN_AGAINST_PREVIOUS_PURPLE_FIELD, HUMAN_ACCEPTANCE_SUSPENDED). Since then, outside this worktree:
| Fact | Where |
|---|---|
| PURPLE stated its reconstructed contract (`CONSUMER_CONTRACT.md`, `auth-identity` `4c82e0e`) and deployed `e069fc1` (HD-AUTH-08) | PURPLE line |
| CYAN consumed it on a **second CYAN line**: branch `auth-cyan-reconstruction` (worktree `worktrees/auth-cyan`, base `618d7a6`, NOT pushed) — AUTH/CYAN-ACCOUNT-01 `94759cd` (+ `5109e20`, records `11aa5f9`, `0f24465`, `e30550a`, `c4c6c17`): hold lifted, Access security chamber, provider contact generalized, cross-lineage real lane 6/6 | `auth-cyan-reconstruction` |
| Human Frontend Acceptance of that line on `/cy-review/`: ACCEPTED; root cutover executed (human-run, 15:59Z); **Final Human Acceptance on `https://nquiry.condyn.eu/`: ACCEPTED (HD-AUTH-09)** | `HUMAN_REVIEW_RESULT_AUTH_CYAN_ACCOUNT_01.md` on that line |
| Production root today: web `94759cd`, api `e069fc1`; `/cy-review/` = the same tree; `/api/auth/providers` live = `[google · PRODUCTION_PROVIDER]`; `/api/auth/identity` unauthenticated = 401 (read-only probes 2026-10-04) | live |
So the complete authentication / identity projection **has already been reviewed and accepted on the real topology**,
on the other CYAN line. Reviewing it on :13500 would review a superseded projection through a non-proof fixture.

## 3. The resulting Field: two CYAN heads
```
618d7a6 (HOLD record, common base)
├─ frontend-symbiotic (origin): 308ab88 baseline → c2a5426 PCPG-06 → 3a29319 RAIL-01 → 9b8771d   [this line; :13500]
└─ auth-cyan-reconstruction (unpushed): 94759cd ACCOUNT-01 → 5109e20 → … → c4c6c17                [production root]
```
First broken relation after this reconstruction: **the human-accepted production line and the symbiosis line are
not one lineage.** PCPG-06 and RAIL-01 are not in production; the accepted auth state is not in this tree; a
review of either line reviews a tree that is not the whole CYAN.

## 4. Integration candidate (prepared, proven, NOT on any branch)
A trial merge of `auth-cyan-reconstruction` `c4c6c17` into `frontend-symbiotic` `9b8771d` was made in a detached
temporary worktree (session scratchpad; no branch moved, nothing pushed, the `auth-cyan` worktree untouched):
| | |
|---|---|
| Conflicts | exactly two: `apps/web/app/globals.css` and `apps/web/playwright.sf01.config.ts` (mobile regex: this side's `cy0[1456789]|cy10` is the superset) |
| CSS resolution — finding | both lines APPEND blocks at the end of the base file (this side PCPG-06 + RAIL-01, the other side `.account-*`). Git splits the two conflict regions at lines the blocks share (`@media (min-width: 768px) {`, `}`), so a per-hunk "keep both sides" interleaves the blocks and leaves three braces unclosed — the browser then silently drops the RAIL-01 rules (first candidate `52a87d4`: the rail law failed 20/24 although every line was present; computed `container-type: normal`, `flex-shrink: 1`). The correct resolution is **this line's file + the other line's appended block** (79 lines, pure addition from the base), braces 1261/1261. |
| Auto-merged | everything else, including `HA-AUTH-CYAN.md` (the HOLD section and the HOLD LIFTED section both present, in order) |
| Dependencies | `package.json` / lockfile unchanged on both lines |
| Candidate commit | `c6479dfcc82c0e763c9ff956beefee93a85cc82e` (tree `d73b7974afe31a7da5f10bb3268027741a984b42`) — kept on the LOCAL branch `cyan-integration-candidate` (not pushed; the temporary worktree was removed) |
| Unit suite | **685 / 685** (661 + 24 of ACCOUNT-01) |
| `tsc --noEmit`, `eslint .` | clean (the one pre-existing warning) |
| Full mocked browser lane `playwright.sf01.config.ts` (every spec, desktop + Pixel 7) | **350 passed, 51 pre-existing skips, 4 failed = the four `mount-review` cases (lane mismatch, see note); the rail law 24 / 24, `cy09-attachments`, `cy09-account-security`, `cy08`, `cy04`–`cy07`, `sf01`–`sf05`, `cy01` all green** |
| Mount lane `playwright.mount.config.ts` (`mount-review`, STATE B on :3302) | **8 / 8** |
Lane note: the four `mount-review` cases belong to the mount lane only; under the default config they fail by construction (no mount), on both lines.
Note for the integrator: both lines number a unit "cy09" (`cy09-attachments.spec.ts` here, `cy09-account-security.spec.ts`
there); the files do not collide, the numbering does.

## 5. Boundary — HUMAN_AUTHORITY_REQUIRED
- **Scope of the :13500 review:** PCPG-06 and RAIL-01 only (the organism; real RED producer). The identity organisms
  on :13500 are fixture displays; the Google path's review boundary is correct and final on this runtime. The
  authentication / identity projection is accepted on production (HD-AUTH-09) and is not re-reviewed here.
- **Integration of the two CYAN heads** (named as a remaining human decision in `HUMAN_REVIEW_RESULT_AUTH_CYAN_ACCOUNT_01.md`:
  "push/integrate auth-cyan-reconstruction"): direction and publication are the human's. The candidate above shows the
  merge is small and green; applying it to `frontend-symbiotic` would publish the unpushed `auth-cyan-reconstruction`
  commits through this branch.
- After integration: PCPG-06 and RAIL-01 would reach production only through a new CYAN candidate assembly and a
  Human Frontend Acceptance on the real topology (`/cy-review/` rebuilt from the integrated tree), then a root
  cutover — each a human act, as before.
