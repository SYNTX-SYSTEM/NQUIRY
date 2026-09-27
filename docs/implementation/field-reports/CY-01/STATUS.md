# CY-01 — STATUS

**Field:** CYAN symbiotic frontend, Work Unit WU-CY-01 — Session position projection across the ANALYSIS boundary.
**Authority:** HD-27 (HA-03, Option B; `HUMAN_DECISIONS.md` here, verbatim). The human operator is the Human Visual
Authority for the frontend.

**Predecessor tuple (verified 2026-09-27):**

| Line | Identity |
|---|---|
| CYAN predecessor | `field-SF-06` → `d3d9bd6722bbddabeca56f18d468a8e78bfa294b` (human-reviewed symbiotic frontend) |
| RED producer | `checkpoint-PFC-B5` (tag object `fd3d5600132e4dcb9203702d500daccf4c6d0439`, signed) → `7d3f74e4685b821cc948f45e413c1e0c207259d4`, tree `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`, migration head `e8c2a5f1b7d4` |
| RED producer ceiling | TECHNICALLY_CLOSED · CHECKPOINTED · NOT REVIEWED_FIELD · NOT PUBLISHED_FIELD; MockProvider only → MOCK / NON_PROOF; Fixture Sessions → FIXTURE_NON_PROOF |

**Resulting status (2026-09-28):** WU-CY-01 **TECHNICALLY_CLOSED · HUMAN_VISUAL_REVIEW_PASS · CHECKPOINTED**
(`HUMAN_REVIEW_RESULT.md`, verbatim). CYAN Field status: **FIELD_GREEN_WITH_DISCLOSED_CEILINGS for the WU-CY-01
scope**. Not REVIEWED_FIELD, not PUBLISHED_FIELD; not merged to master; not deployed. No further CYAN Work Unit started.

**Checkpoint identity (19 §16: the Field commit, then this documentation-only identity commit):**

| Identity | Value |
|---|---|
| Field commit | `a0a5afc206444ba24158158d9918f12ac2d2efae` (signed, good signature; 28 files, 1946+ / 20−) |
| Identity commit | the commit that adds this table (see `git log -1 -- docs/implementation/field-reports/CY-01/STATUS.md`) |
| Branch | `frontend-symbiotic`, parent line `field-SF-06` → `d3d9bd6722bbddabeca56f18d468a8e78bfa294b` |
| Checkpoint tag | `field-CY-01` (annotated, signed) → the identity commit; verified remotely with `^{}` after the push |
| Remote | `origin/frontend-symbiotic` = the identity commit (verified with `git ls-remote`) |
| RED producer (unchanged) | `checkpoint-PFC-B5` → `7d3f74e4685b821cc948f45e413c1e0c207259d4`, tree `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`, migration head `e8c2a5f1b7d4` |

Evidence not in Git: `browser-evidence/run-1/screenshots/` (16 PNG, ~11 MB; kept untracked like every SF evidence run).

**Rollback:** CYAN → `field-SF-06`; RED → `checkpoint-PFC-B5`; independent.
