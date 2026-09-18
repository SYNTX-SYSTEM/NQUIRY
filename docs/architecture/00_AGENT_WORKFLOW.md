# 00_AGENT_WORKFLOW

**Document role:** Process reference for how a coding agent executes this repository's implementation sequence.
**Scope:** Execution discipline only. It does not define architecture — 00 through 16 do that — and nothing here may be read as authority to add, relax, or reinterpret a semantic rule those files establish.
**Status:** Reflects the workflow actually used from PKG-00 through PKG-07 and carried forward unchanged.

---

## 0. Document Authority

This file has no architectural authority. It records the operating procedure a coding agent follows when asked to execute a package from `NQUIRY_IMPLEMENTATION_MASTER.md`, so that procedure does not have to be re-derived, re-explained, or silently drift from one package to the next.

If this file and `14_IMPLEMENTATION_SEQUENCE.md` or `15_AI_CODING_PROMPTS.md` ever appear to disagree, 14/15 govern. This file exists to make their discipline concrete and repeatable, not to compete with them.

---

## 1. One Package at a Time, Strictly by the DAG

Work proceeds package by package, in the order `NQUIRY_IMPLEMENTATION_MASTER.md`'s Coding Package Manifest and DAG define (`14_IMPLEMENTATION_SEQUENCE.md` §46/§47). A package is only started when:

- its `REQUIRED PREDECESSORS` are each verified complete (`PACKAGE_PASS`, committed) — mere code existing is not enough, per that package's own `PREDECESSOR_ACCEPTANCE_REQUIRED` clause;
- the human has explicitly authorized it by name, quoting `HUMAN_AUTHORIZED_SCOPE: <PKG-ID> ONLY`.

No package is started speculatively, "while we're at it," or because it looked eligible after a prior `PACKAGE_PASS`. Eligibility (satisfied predecessors) and authorization (a human saying so) are always kept distinct — every completion report says so explicitly (`NEXT_PACKAGE_ELIGIBLE` / `NEXT_PACKAGE_ALLOWED_BY_DAG` vs. `NEXT_PACKAGE_AUTHORIZED: NO`).

A phase boundary (`BUILD_PHASE` changing between consecutive packages) does not by itself require a separate ceremony beyond the same per-package authorization; the human gate is exercised at every package regardless of phase.

## 2. No Package Starts Without the Previous One Being Gated

"Gated" means, concretely, both of:

1. **`PACKAGE_PASS`** was reported for the prior package, with its full `PACKAGE COMPLETION REPORT`.
2. **A commit exists** for that package's changes, and the human has confirmed the commit hash and verdict back to the agent before the next package's prompt is read.

An agent does not commit on the human's behalf and does not infer a gate from silence. The human's own message authorizing the next package (stating the prior commit hash and `PACKAGE_PASS`) is the gate.

## 3. Every Package Runs the Full `IMPLEMENTATION_SEQUENCE`

Each package's Architecture-15 coding prompt defines the same fixed sequence, and it is followed in order, without skipping steps because a package looks small:

```text
A. ORIENT
B. TRACE
C. PLAN
D. PRE-IMPLEMENTATION FALSIFICATION
E. IMPLEMENT
F. STATIC VERIFY
G. TARGETED TEST
H. NEGATIVE TEST
I. ADVERSARIAL TEST
J. CROSS-LAYER TEST
K. RECURSIVE REGRESSION
L. DIFF AUDIT
M. ARCHITECTURE RECONSTRUCTION CHECK
N. PACKAGE VERDICT
O. STOP OR RETURN
```

Concretely:

- **A (ORIENT)** confirms the previous package's commit exists and the working tree is clean before anything is read or written.
- **B–D** are produced as text (`PRE_IMPLEMENTATION_TRACE`, the file/module plan, the falsification statement and attack model) *before* any file is created or edited — the prompt is explicit that editing may not begin until D is complete. Real upstream reading happens here: only the architecture files 14 names for that package, read at whatever depth is needed to resolve every field the package's manifest and coding prompt reference (including chasing a citation into a Home-File the package manifest doesn't name directly, when the manifest's own wording depends on it).
- **E (IMPLEMENT)** builds exactly what B–D planned — no unrelated refactor, no future-generic abstraction, nothing for a package that hasn't been authorized yet.
- **F (STATIC VERIFY)** runs formatting, lint, typecheck, and all three architecture-check scripts (`check_architecture_dependencies.py`, `check_provider_sdk_imports.py`, `check_test_only_imports.py`) before any test is trusted.
- **G–I** run targeted, negative, and adversarial tests — adversarial cases include every package-specific mandatory attack the coding prompt names, plus enough novel/adapted attacks to clear its stated minimum (never satisfied by re-running the happy path under a new name).
- **J (CROSS-LAYER TEST)** exercises the package against its real predecessor layers — genuine repositories, genuine prior-package types — not isolated mocks.
- **K (RECURSIVE REGRESSION)** re-runs the full existing suite (every predecessor package's tests, not just the new package's own) after the new code lands, both without a database and against a live one.
- **L (DIFF AUDIT)** inspects the actual `git diff` and answers, explicitly, whether the change introduced any new semantic type, enum value, transition, authority path, DB write path, weakened boundary, easier test, removed negative test, admin shortcut, projection/cache truth, AI canonical authority, broader Workspace scope, changed migration semantics, or forbidden dependency.
- **M (ARCHITECTURE RECONSTRUCTION CHECK)** reconstructs the request→...→resulting-state chain the package participates in, marking every node the package does not yet reach `NOT_APPLICABLE` or `SUCCESSOR_NOT_BUILT` rather than stubbing it.
- **N/O** produce the binary verdict and either return the completion report or STOP.

## 4. Migrations Are Proven Against Real PostgreSQL, Never Mocked

Whenever a package touches the schema:

1. Inspect the current migration head before writing a new revision.
2. Write exactly the migration the package's `DATABASE_CHANGES` mapping requires — no more.
3. Start a real PostgreSQL 17 instance (`docker compose up -d postgres`; local port 5432 is often already occupied on the development machine, so `POSTGRES_PORT` is set to an alternate port such as `55432` for the session).
4. `alembic upgrade head` against that live instance and confirm it applies cleanly.
5. Inspect the live schema directly (`\d <table>`) to confirm every column, constraint, foreign key, index, and trigger matches what the migration says it creates — triggers in particular are invisible to the SQLAlchemy Core `Table` metadata used elsewhere in the codebase and can only be confirmed this way.
6. Run the full test suite against that live database (`DATABASE_URL` set) — not just the new package's own tests.
7. `alembic downgrade -1`, inspect the schema again to confirm a clean, complete removal (including of anything retrofitted onto a predecessor's table), then `alembic upgrade head` again and re-run the full suite once more, to prove the migration is reversible and re-appliable, not merely appliable once.
8. Run `scripts/verify_migrations.py` for both its static check (single head, linear history) and its live check (database head matches the code's head).
9. Tear down the container (`docker compose down -v`) and remove any local `.env` used to point at the alternate port, leaving no running services or leftover local state.

Tests that require a live database skip cleanly (not silently pass) when `DATABASE_URL` is unset, using the same `SKIPPED_NO_DATABASE` convention throughout the suite — a skip is always visible in the test summary, never indistinguishable from a pass.

## 5. Open Gaps and Hard Dependencies Are Never Silently Bypassed

`16_DECISION_GAP_REGISTER.md`'s open gaps (`[UNDERDEFINED]`, `[OPEN]`, `[OPEN SOURCE TENSION]`) and the two standing hard dependencies — `HARD-DEP-001` (legitimate Workspace governance-root bootstrap) and `HARD-DEP-002` (real AI-provider eligibility) — stay open unless a human legitimately updates Architecture 16 itself. In particular:

- A field, column, or enum value whose vocabulary is genuinely unresolved upstream is **omitted**, not invented — the same way `Challenge.status`, `Question.status`, and Burst duration/timer fields were all left out rather than guessed at, each with a docstring citing exactly which gap makes it unsafe to materialize.
- `test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap` (and any fixture like it) is usable to seed data *so that other invariants can be tested*, but its output is never treated as evidence that `HARD-DEP-001` is closed, and it stays behind the `test_support` import-graph guard so production code cannot reach it even by accident.
- Any capability that would require a hard dependency to be resolved is deferred to whichever future package the DAG actually assigns it to, disclosed as `KNOWN_LIMITATIONS`/`BLOCKED_DEPENDENCIES` in that package's completion report, not quietly worked around.

## 6. Architecture Contradictions Stop the Agent — They Are Never Patched Locally

If implementing a package would require resolving genuine ambiguity by inventing a rule the upstream architecture does not state, the agent does not pick a plausible-sounding answer and move on. Two outcomes are legitimate:

- **A real, disclosed design choice**, when the upstream text itself provides the resolution (a hedge, a cross-reference, an existing pattern from a predecessor package) — always written down with its exact citation, in the code's own docstrings and in the package's `PRE_IMPLEMENTATION_TRACE`, so the reasoning is auditable rather than assumed. Reusing `WORKSPACE` scope for `SESSION_CONTROL_RIGHT` authority checks (citing 12 §7's own "where upstream assigns it" hedge, since 12 §8.1's bootstrap sequence never produces any other scope shape) is an example of this — a choice, not an invention, because the source text itself supplied the resolution.
- **A STOP**, when no such resolution exists — the agent halts, states which upstream files conflict, why any local workaround would itself be semantic invention, and what minimum human decision would unblock it, exactly in the `STOP::TRUE` shape the coding prompt defines. No package in this sequence has yet required a hard STOP, but the discipline is unconditional: a plausible guess is never substituted for one.

## 7. Every Package Ends With a Full Completion Report and Its Own Commit

At the end of every package, regardless of outcome:

1. The exact `PACKAGE COMPLETION REPORT` fields the coding prompt specifies are produced, with evidence for each — not narrative summary in place of the field, and not a field silently omitted because it was `NOT_APPLICABLE` (that is itself a value to state, with the reason).
2. The full report is appended to the standing external log (`/tmp/nquiry_pkg_reports.log`), under a `=== PKG-XX ===` separator, verbatim — never overwritten, so the log accumulates one full record per package. The identical rule applies to any `STOP::TRUE`/`ARCHITECTURE_CONTRADICTION` block, should one occur.
3. Project memory is updated with what the package actually added and any load-bearing design decisions future packages need to know about, so the next session does not have to re-derive them from the diff alone.
4. The package's changes are committed on their own — never bundled with a future package's work, and never committed before the human has reviewed the report and given the gate.
5. Docker/local state used for live migration and database testing is torn down (`docker compose down -v`, any temporary `.env` removed) before the package is considered finished.

The next package is not started until steps 1–5 are done and the human has explicitly authorized it by name.
