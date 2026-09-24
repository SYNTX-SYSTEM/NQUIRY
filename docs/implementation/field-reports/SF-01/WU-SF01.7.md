# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.7 — Isolated real-stack execution (L6/L7), defects found and repaired

## Mission
Run L6/L7 exactly as prepared in WU-SF01.6, in the isolated environment only (SF01-HD-2).
- An application defect is traced to its First Broken Relation and repaired inside SF-01.
- An environment defect is repaired inside `infra/sf01` only.
- The F03 contact zone is not crossed and F03 is not integrated.

## Runs
| Run | Tree | Result |
|---|---|---|
| L7 run 1 | SF-01 as of WU-SF01.6 | **10/10 passed**, exit 0 (F02 a11y, F02 flow, WU-02.12 closure, 2 × SF-01; desktop + Pixel 7) |
| L7 run 2 (final) | after the two repairs below | **10/10 passed**, exit 0 |

Both runs:
- `SF01_GUARD: project nquiry-sf01, no host ports`;
- `MIGRATION_STATIC_CHECK::PASS (22 revisions, single head b3d8e5f0a2c7)`;
- `MIGRATION_LIVE_CHECK::PASS` on the empty isolated DB, after `db_roles.sql`.

The environment starts from an empty DB each run, and only `nquiry-sf01` volumes are removed. After each run, only the F03 project's containers exist, untouched:
- `nquiry-api-1` / `nquiry-web-1` have run continuously since 17:50Z;
- `nquiry-worker-1` exited at 17:50:17Z, 0.24 s after it started (the no-op worker skeleton), 79 min before run 1 began at 19:09:25Z.

## Defect 1: APPLICATION (found by visual proof, not by a test)
- **Symptom:** in the run-1 screenshots, the closed proof disclosures ("Who holds Session control for this Challenge", "Authority you hold here") had no visible open/closed marker, so they looked like static headings.
- **First Broken Relation:** `PROOF DEPTH → PERCEIVABLE ACTIVATION TARGET` (21 §35: "reasons and proof are explicit activation targets", no hover).
  - The SF-01 CSS set `summary { display: flex }`, which removes the native `list-item` marker.
  - Keyboard and screen-reader semantics were intact (native `<details>`), so every test passed. Only sighted users lost the relation.
- **Test first:** the L3 proof-depth test now requires a visible `::before` marker that changes between closed and open.
  - RED: 2 failed (desktop + mobile, `content: "none"`).
- **Root repair** (`globals.css`, SF-01 section): explicit ▸ / ▾ marker, decorative for assistive tech (`content: "▸" / ""`), since `<details>` already exposes the state. The summary also takes the action color.
  - GREEN: isolated mocked lane 81/81; L7 run 2 10/10; visually verified (`visual/desktop-03`, `visual/desktop-04`).
- **Propagation:** `ProofDepth` is the only disclosure primitive; the Workspace and Challenge proof zones are repaired by the same rule.

## Defect 2: ENVIRONMENT
- **Symptom:** after run 1, the mocked lane failed at start with `EACCES: unlink … test-results/sf01-real-stack/f02-visual/…png`.
- **First Broken Relation:** runner output ↔ host workspace ownership. The runner runs as root and wrote root-owned files into the bind mount, so the other lanes could not clean `test-results/`.
- **Repair (infra/sf01 only):** `run-in-namespace.sh` records the owner of the mounted output directory, which the host wrapper creates as the host user, and `chown`s everything back on exit (EXIT trap).
  - The files already root-owned were handed back once with a one-shot container that mounted only that directory.
  - After run 2: 0 non-user-owned files.

## Lane side effects (unchanged, disclosed)
- Every host `next dev` run of the mocked lane regenerates `apps/web/AGENTS.md` / `CLAUDE.md` and rewrites `next-env.d.ts`. They were removed and restored after every run; the final tree is clean.
- The mocked lane wipes `apps/web/test-results/` at start, so raw L7 output is transient. The final screenshots are curated into `visual/` (10 PNGs, 1.7 MB).

## Proof ceilings
- The web server under L7 is `next dev` (same as the F02 real-stack lane), not a production server. `next build` is proven separately (L5).
- L7 RED against the pre-SF-01 pages was **not** run. Non-vacuity of the SF-01 assertions is proven at L3 (19/21 RED on the `bea864b` pages). The L7 spec asserts the same relations with the real stack underneath.

## Git state
Uncommitted, nothing staged.

## Result
PASS: L6/L7 GREEN in the isolated environment on the final tree.
