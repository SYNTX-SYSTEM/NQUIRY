# WORK UNIT REPORT
FIELD: CYAN (one lineage again) — the accepted production line and the symbiosis line
WORK_UNIT: CYAN-INTEGRATION-01 — integrate the proven candidate lineage, propagate, prove
DATE: 2026-10-05 · BASE: `frontend-symbiotic` `f4e3fed` (records) over `9b8771d` (`checkpoint-CY-RAIL-01`) × `auth-cyan-reconstruction` `c4c6c17` (production root `94759cd` + `5109e20`)
AUTHORITY: HUMAN_AUTHORITY_DECISION = ACCEPTED (2026-10-05, verbatim: "The proven integration of the two CYAN heads is authorized. Proceed under canonical SFE from the reconstructed Field state. Integrate only the proven candidate lineage, propagate and prove the resulting state, and continue autonomously until the next genuine Boundary."); the reconstruction `REVIEW_COVERAGE_RECONSTRUCTION_2026-10-04.md` and its proven candidate `c6479df`.

## Effect
| Step | Result |
|---|---|
| Merge | `c6479df` (the proven candidate: a merge of `c4c6c17` into `9b8771d`) merged into `f4e3fed` → **`7f42d8e`** (tree `e92b502`). Tree = the candidate's tree + this line's three record files since the candidate. One conflict: the AUTH-CYAN ledger's open list — both sides kept, integration noted. |
| Lineage check | `c4c6c17` is an ancestor of `origin/frontend-symbiotic`: the `auth-cyan-reconstruction` commits are published through this branch (the decision's consequence, disclosed beforehand). The temporary local branch `cyan-integration-candidate` was deleted after integration. |
| Auth sources | byte-identical to `c4c6c17` (`authClient`, `accountSecurity`, `accountEffects`, `linkBoundary`, `useLinkBoundary`, `providerContact`, `identityProjection`, `useIdentityProjection`, `AccountSecurity`, `ProviderContact`, `IdentityPanel`, `IdentityProjection`, `workspaces/page`, `login/page`): the relation proven on the cross-lineage real lane and accepted on production is carried unchanged; the merge touched only `globals.css` (this file + the other line's appended block) and the mobile test regex. |
| Tag | `checkpoint-CYAN-INTEGRATION-01` → tag object `4b0e699c…` → `7f42d8e`; branch and tag pushed. |

## Proof of the resulting state (this worktree, `7f42d8e`)
| Lane | Result |
|---|---|
| Unit suite | **685 / 685** |
| `tsc --noEmit`, `eslint .` | clean (the one pre-existing warning) |
| Full mocked browser lane `playwright.sf01.config.ts` (every spec, desktop + Pixel 7) | **350 passed, 51 pre-existing skips, 4 = the `mount-review` cases, which belong to the mount lane** |
| Mount lane `playwright.mount.config.ts` (STATE B, :3302) | **8 / 8** |
| Rail mutation proof `scripts/rail01-mutation-proof.mjs` (the merge touched the stylesheet) | **4 / 4 killed**, byte-identical restore |
| PCPG-06 mutation proof | not re-run: its anchors are TypeScript sources byte-identical to `c2a5426` (progressive proof radius) |
| Cross-lineage REAL auth lane `scripts/run_auth_cyan_real_lane.sh` | **not run here**: it serves the PURPLE API from the `auth-identity` worktree, which is currently dirty and moving under another session (`http_dispatch.py` modified, `auth_audit.py` untracked) — not a pinned producer. The relation stands on the byte-identity above and on the production acceptance (HD-AUTH-09). |

## Propagation
| Target | State |
|---|---|
| Local review runtime `127.0.0.1:13500` (RED `checkpoint-PFC-PCPG-18` + review proxy) | refreshed with the integrated `apps/web` (archive of `7f42d8e`, `.next` cleared, restarted). Rail at 1024 / 1280 / 1440: current station fits, no overlap (RAIL-01 holds); Session page: governance panel present, five stations, no sideways scroll on Pixel 7; Workspaces: identity panel (fail-closed words, since the RED producer serves no `/auth/identity`), "Identity and access" and "Access security" chambers rendered from the proxy's FIXTURE_NON_PROOF reads — `browser-evidence/integration-01/SUMMARY.md`. Coverage of this runtime unchanged: PCPG-06 + RAIL-01 only. |
| Staged review mount `https://nquiry.condyn.eu/cy-review/` (web only, loopback 3402) | **PREPARED, NOT EXECUTED**: the session's permission layer refused the rebuild as a production deploy (the same refusal the other session met for `5109e20`). Prepared in the session scratchpad: `deploy/cyreview/cyreview-7f42d8e-20261005T104910Z.tar.gz` (`git archive apps/web` of `7f42d8e`, 214 files) and `rebuild-integrated.sh` (the recorded `rebuild.sh` pattern: predecessor Dockerfile, `SHA256SUMS`, `DEPLOYMENT_MANIFEST.json` with source/tag/claim ceiling, `compose.yaml.pre`, context switch of `/opt/nquiry/review/compose.yaml`, build, up, `STATE_BEFORE/AFTER.txt`). Human-run: `scp` both to `/opt/nquiry/assembly/`, extract, then `ASSEMBLY=cyreview-7f42d8e-20261005T104910Z COMMIT=7f42d8e6ee6297c3c815810a04fbaca5cd6771d5 TREE=e92b50243e9300bdf951aee1a6086686431ef280 TAG=checkpoint-CYAN-INTEGRATION-01 bash rebuild.sh`. Rollback = `compose.yaml.pre` + rebuild, or `_baseline-pre-CYREVIEW-20261003T213429Z/ROLLBACK.sh`. |
| Production root `/` | unchanged (`94759cd`, accepted). Not touched; cutover not authorized. |
| Records | this unit; `HA-AUTH-CYAN.md` carries the integration note; `REVIEW_COVERAGE_RECONSTRUCTION_2026-10-04.md` names the candidate. Known cosmetic incoherence left as is: two units numbered "cy09" (`cy09-attachments`, `cy09-account-security`); files do not collide. |

## Status
CYAN-INTEGRATION-01: **CLOSED — LOCAL_GREEN + FIELD_GREEN on the mocked and mount lanes; PUBLISHED on `origin/frontend-symbiotic`.**
The integrated lineage carries: the accepted authentication / identity / account-security state (PUBLISHED_FIELD on the
production root), PCPG-06 (READY_FOR_HUMAN_FRONTEND_REVIEW), RAIL-01 (READY_FOR_HUMAN_FRONTEND_REVIEW), the
per-method last-use fact `5109e20` (proven, not published).

## Boundary — HUMAN_AUTHORITY_REQUIRED
1. **Staging of the integrated candidate on `/cy-review/`** — prepared, refused to the session as a production deploy; a human-run step.
2. **Human Frontend Acceptance of PCPG-06 and RAIL-01** on the real topology once staged (or on `127.0.0.1:13500` for the organism-only scope, guide `CY-02/HUMAN_REVIEW_GUIDE_PCPG-06.md`, record `WU-CYAN-RAIL-01.md`).
3. After acceptance: CYAN_PRODUCTION_ROOT_CUTOVER of the integrated tree (a separate, human-authorized Field, as before), which would also publish `5109e20`.
