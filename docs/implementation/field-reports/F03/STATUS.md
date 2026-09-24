# FIELD STATUS

## Field
F03 — PROTECTED HUMAN QUESTION FIELD

## Semantic regime
Protected human generation (§23).

## Status
FIELD_GREEN_WITH_DISCLOSED_CEILINGS — COMMITTED LOCALLY (`0d59ae3`, not pushed, not tagged)

12 Work Units (WU-03.0 through WU-03.11), all PASS. Not committed, not tagged,
not pushed. FIELD_GREEN != REVIEWED_FIELD != PUBLISHED_FIELD.

- Human decisions used: HD-10 (PAUSE/RESUME out of scope), HD-11 (no automatic
  timer completion), HD-12 (deterministic questions-only form rule; NQ-GAP-023
  stays open), HD-13 (own questions only while ACTIVE; full frozen set after),
  HD-14 (controller self-admission), HD-15 (PARTICIPATION source). Reconciled
  into 16 §41 REC-011..017 (NQ-DEC-038..043) and 20 §7 / §15A.
- First Broken Relations repaired: FBR-F03-2..6 (known) and FBR-F03-7, -8
  (discovered): see FIELD_REVIEW.md.
- Migrations: c4e9a2b7d135, e5a1b3c8f204, f6b2c4d9a318 (head f6b2c4d9a318).
- Proof: live DB 1535 passed / 2 skipped (baseline 1360); real stack 10 passed
  (F03 4, incl. axe + keyboard, desktop + mobile); vitest 123; mocked 39.

## Upstream dependencies
F02 (published `2f33be1`, tag `field-F02`)

## Downstream dependencies
F04 (post-Burst AI / sensemaking): prerequisites delivered (a provably frozen,
reconstructable human set; human origin and author on every raw Question).
F04 is NOT started. F08 (infrastructure may begin early once event contracts are
stable — §19 DAG note; the new event types are BURST_QUESTION_CAPTURED and
QUESTION_GENERATION_CLOSED).
