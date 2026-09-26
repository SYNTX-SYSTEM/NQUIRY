# WU-PFC-A1 — Checkpoint identity

**Authority:** "NQUIRY_PRODUCT_FUNCTION_COMPLETION AUTONOMOUS SFE EXECUTION
AUTHORIZATION" (2026-09-26), §1: "I accept the WU-PFC-A1 technical result and
authorize its checkpoint materialization."

## Verification before the commit

- The working tree was re-verified against `evidence/checksums.txt`: all five files OK.
- The change set is exactly the one recorded in `WU-PFC-A1.md`: 3 modified production files, 1 new test file, 1 new mutation script, and the PFC-A report and evidence.
- The recorded evidence (falsifiers 23 passed, mutation 18/18, live suite 1558 passed / 2 skipped, no-DB suite 808 passed) was produced on this exact tree.

## Identity

| Identity | Value |
|---|---|
| Materialization commit | `71b3babf50ae450bb2f02cbd592f2c8127da5518` (signed, good signature) |
| Predecessor | `1eb3799831d5f111c4d2e7fa7f4e5cfacabbb873` (`origin/pfc-architecture`; fast-forward, no history rewrite) |
| Remote branch | `origin/pfc-a1-challenge-frame` = `71b3bab` (verified with `git ls-remote`) |
| Checkpoint tag | `checkpoint-PFC-A1`, tag object `471cd51b66bc0b34934e2bd7a9b6e52a9125deb0` (annotated, signed, good signature) |
| Tag target | `71b3babf50ae450bb2f02cbd592f2c8127da5518` (verified remotely with `git ls-remote …^{}`) |
| This record | Follow-up identity commit on `pfc-a1-challenge-frame`. The tag stays on the materialization commit (F02/F03/F04 precedent). |

## Resulting status

**PFC-A1: TECHNICALLY_ACCEPTED, CHECKPOINTED, recoverable predecessor.**

- Not REVIEWED_FIELD.
- Not PUBLISHED_FIELD: the branch is not merged into master, and BLUE is untouched.
- CYAN is unchanged.
