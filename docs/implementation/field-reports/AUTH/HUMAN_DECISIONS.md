# HUMAN DECISIONS — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)

Field-local record. IDs are `HD-AUTH-n`. They are not yet reconciled into
`16_DECISION_GAP_REGISTER.md` §41 (see "Ledger reconciliation" at the end).

## HD-AUTH-01 — Field authorization (2026-09-30)

**Decision (human operator, the PURPLE execution brief of 2026-09-30, confirmed
as the operator's own instruction in the same session):** PURPLE is authorized
to materialize the complete Identity & Authentication Field defined by
Architecture 24 (`24_NQIRY_IDENTITY_AUTHENTICATION_FIELD_ARCHITECTURE.md`),
autonomously, one proven relation at a time, in its own worktree and branch.

**What it authorizes:** reading, analysis, implementation, tests, migrations in
isolated test environments, local proof infrastructure, documentation, Work
Unit reports, and one local commit per fully proven Work Unit.

**What it does not decide:** any of the 18 Human Authority boundaries of
Architecture 24 §36. Each stays fail-closed (24 §36 "Default behavior for
unresolved human authority") until the Field reaches it and the operator
decides it. No push, no tag, no production action, no production migration.

**Relation to PFC HA-09:** `PFC/HUMAN_AUTHORITY_QUEUE.md` lists HA-09
("Architecture 24 Identity scope and its 18 §36 decisions") as OPEN at the
PURPLE base. HD-AUTH-01 answers the *scope* half (the Field may be
materialized). The §36 decisions stay open. The queue file is RED's record and
is not edited by PURPLE.

## HD-AUTH-02 — PURPLE predecessor: pinned RED checkpoint (2026-09-30)

**Question:** Architecture 24 is on `master` (`6e7e402`). The HD-28 / AC1.1
account-creation producer and seven newer migrations exist only on the RED
line. Which commit is PURPLE's predecessor?

**Options presented:** `checkpoint-PFC-AC1.1` (`e91961e`);
`checkpoint-PFC-SFE-PCPG` (`395ecf7`); `master` (`6e7e402`).

**Decision (human operator):** `checkpoint-PFC-AC1.1`.

- Commit `e91961e4a66ab21d9edf45d74bb43b8fbd324737`, tree `af6da710a9c5d81c48f3e84ecadc310e7edabd50`.
- Migration head at the pin: `e8c2a5f1b7d4`.
- The pin is a fixed commit, never the moving `pfc-integration` branch (the
  HD-27 precedent). RED's ceiling is unchanged by consumption: CHECKPOINTED,
  not REVIEWED_FIELD, not PUBLISHED_FIELD.

## HD-AUTH-03 — Work Unit commits without the per-commit gate (2026-09-30)

**Question:** 20 §14 (no-commit law) and the standing project rule require an
explicit approval before every commit. The brief authorizes local Work Unit
commits after full proof.

**Decision (human operator):** "Yes, commits included." PURPLE may create one
local commit per fully proven Work Unit on branch `auth-identity`. Never push.
No production tags.

**Scope:** this Field and this branch only. It does not change 20 §14 for any
other Field.

## Ledger reconciliation (deferred, disclosed)

20 §14 requires human decisions to be reconciled into 16 §41, the §6 table and
the machine-readable register in the same Work Unit. PURPLE does not do this on
its branch, for two reasons:

1. `REC-nnn` / `NQ-DEC-nnn` numbers are global and are allocated on the RED
   line (last at the pin: REC-032 / NQ-DEC-056). RED continues to allocate
   after the pin. A number chosen here would collide at integration.
2. `tests/regression/test_pfc_ledger.py` (RED's falsifier) pins the register
   to exactly 56 decisions. Adding entries would break a RED test, and editing
   that test is a cross-Field change outside PURPLE's authority.

The decisions above are therefore recorded here with full provenance and are
to be reconciled into 16 when the Field lines are integrated. This is a
disclosed ceiling of every PURPLE Work Unit, not a closed relation.
