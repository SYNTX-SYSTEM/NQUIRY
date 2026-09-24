# nquiry

**N.Q.U.I.R.Y. — Questions Are the Answer-System.**

An AI-augmented inquiry system for leadership, decision-making,
innovation and complex problem solving. Its primary product behavior
is not answer generation — its purpose is to help individuals and
teams improve the quality of inquiry around complex, ambiguous or
consequential challenges, by discovering better questions, challenging
assumptions, generating alternative perspectives, connecting inquiry
to evidence, and moving inquiry toward action. The central product
hypothesis (`docs/architecture/00_NQUIRY_MASTER_ARCHITECTURE.md` §1.1):

> A better question can change the problem, which can change the
> available options, which can change the decision and ultimately the
> outcome.

The canonical product progression a Challenge moves through:

```text
Problem → Questions → Perspectives → Assumptions → Insights →
Evidence → Experiments → Learning → Action
```

This repository implements the NQUIRY specification in
`docs/architecture/`, package by package, in the order fixed by
`docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §46/§47 (Coding
Package Manifest / DAG), using the execution prompts in
`docs/architecture/15_AI_CODING_PROMPTS.md`.

Architecture defines what may exist. 14 defines how it is
materialized. 15 defines how a coding agent may build it. No code in
this repository defines architecture.

## Current state

All 32 originally-scoped packages (`PKG-00` through `PKG-32`) are
complete — the full domain/boundary/authority/commit/persistence/
security/observability/recovery core described in `docs/architecture/`
is implemented and tested. Two further fields extended that base:

- **Architecture 17** — the first real HTTP surface (`GET
  /workspaces/{w}/sessions/{s}`, `POST /decisions/{d}/decide`), wiring
  the existing application layer to a real, running FastAPI/Next.js
  stack for the first time.
- **Local Authentication Adapter** — a real, local email/password
  login with a genuine server-verified session (closing the GAP-14-001
  header-trust weakness Architecture 17 disclosed; see "What's still
  open" below for what this does *not* close).

Since then, execution runs Field by Field under
`docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md` (governing
engineering architecture) and `19_NQUIRY_IMPLEMENTATION_WITH_FRONTEND_RUNNING.md`
(Field plan F00–F12). Field reports live under
`docs/implementation/field-reports/`: F00 (baseline) and F01 (identity,
Workspace, governance) are committed. F02 (Challenge, Session,
participation) is complete, including its Field-closure Work Unit WU-02.12,
and awaiting human review. It makes the
governed path clickable: found a Workspace → add a Facilitator → frame a
Challenge → grant and open a Session → lawful progression to the
protected, HUMAN_ONLY question-generation position. The walkthrough is in
`docs/RUNTIME_OPERATION.md` §21.

Every package and field has its own dated completion report — the
full, ordered proof trail — under
[`docs/implementation/proof-reports/`](docs/implementation/proof-reports/)
(`PKG-00.md` through `PKG-32.md`, then
`ARCH-17-RUNTIME-MATERIALIZATION.md`,
`FULLSTACK-RUNTIME-ACCEPTANCE.md`, `LOCAL-AUTH-ADAPTER.md`). Each
report states its own test results, adversarial/negative test proof,
and any gaps left deliberately open.

## Reference stack

Python 3.13, FastAPI, PostgreSQL 17, Alembic, SQLAlchemy 2.x Core,
Next.js 16 (TypeScript), pytest, Vitest, Playwright, Docker Compose,
GitHub Actions. See `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md`
§2.1 for the full rationale table.

## Repository topology

See `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §3. Directory
ownership and allowed/forbidden dependencies are in §3.1 and §4, and
are enforced by `scripts/check_architecture_dependencies.py`,
`scripts/check_provider_sdk_imports.py`, and
`scripts/check_test_only_imports.py`.

## Running it locally

Full, step-by-step instructions (prerequisites, environment
variables, ports, database migration, seeding a login you can actually
use) live in [`docs/RUNTIME_OPERATION.md`](docs/RUNTIME_OPERATION.md)
— that file is the single source of truth for this; the summary below
is not a substitute for it.

```bash
docker compose --profile app up -d --build   # postgres + api + worker + web
psql -h localhost -p 15432 -U nquiry -d nquiry -f infra/local/db_roles.sql
python scripts/verify_migrations.py           # applies migrations to head
python scripts/seed_local_demo.py              # creates a demo login + Challenge
```

Then open `http://localhost:3000/` and log in with the credentials
`seed_local_demo.py` prints (`docs/RUNTIME_OPERATION.md` §0 has the
exact defaults and a plain-language walkthrough of the login/session
flow, including who the demo account is and what it is not).

To run the test suite / static gates directly:

```bash
pip install -e ".[dev]"                 # requires Python >= 3.13
DATABASE_URL=…/nquiry_test pytest       # isolated test DB, see runbook §22
ruff check .
mypy packages apps/api/src apps/worker/src scripts

cd apps/web && npm install && npm run lint && npm run typecheck && npm test && npm run e2e
npm run e2e:real                        # real-stack browser lane (no mocking)
```

Both browser lanes test whatever already serves `:3000`/`:8000`. To prove
your working tree, rebuild first (`docker compose -p nquiry --profile app up
-d --build`). See `docs/RUNTIME_OPERATION.md` §22.

## What's still mocked, stubbed, or blocked — and why

Honest, not marketing:

- **HARD-DEP-001 — legitimate first Workspace governance-root
  bootstrap: RESOLVED (Option A, self-service founder), 2026-09-21.**
  Materialized in Field F01 as the governed `CMD_CREATE_WORKSPACE`
  Command; provenance in `docs/architecture/16_DECISION_GAP_REGISTER.md`
  §41 REC-001. Workspaces seeded by
  `test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap` (every
  PKG-era test fixture and `scripts/seed_local_demo.py`'s demo
  Workspace) stay `NON_PROOF_FIXTURE`. Note: the database has no column
  that labels those rows; the distinction lives in provenance (only a
  governed founding has `CMD_CREATE_WORKSPACE` command/audit rows) and
  in the seed script's own printed disclosure.
- **HARD-DEP-002 — real AI provider eligibility: EXTERNAL_DEPENDENCY,
  open.** The AI Gateway's only concrete provider is
  `MockProviderAdapter` (`packages/ai_gateway/adapters/providers/mock.py`).
  No real model provider is integrated; provider/data-classification/
  privacy eligibility has not been established.
- **Worker has no continuous production loop.** The real, tested
  `OutboxWorker`/`ProjectionWorker` classes exist and are exercised by
  their own test suites, but `apps/worker/src/nquiry_worker/__main__.py`
  is not wired to run them continuously — it starts, logs a Phase-0
  message, and exits `0` by design. Blocked on a durable
  `OutboxRecord.commit_id` → `EventEnvelope` reconstruction path that
  does not exist yet.
- **HTTP coverage is partial, and grows per Field.** Routes exist for
  local auth, the Architecture-17 Session view and decide, and the F01
  Workspace Commands/Queries, and the F02 Challenge/Session/transition/
  participation/grant routes (runbook §18). Several application-layer
  Commands still have no route (Question selection, open Decision
  consideration, recovery). F03 added Question capture and manual Burst
  completion (runbook §18). AI analysis and Evidence commands are F04–F06
  scope. Burst PAUSE/RESUME is out of scope (F03 HD-10).
- **No production authentication provider.** The local login (above)
  is a real, hardened LOCAL credential adapter — not an OIDC/external
  identity provider integration (GAP-14-001 remains open).
- **Browser proof classes.** The Playwright suites under
  `apps/web/tests/e2e/` that use `page.route()` are *mocked browser
  proof* (component/contract behavior only). They are not runtime
  proof. Real-stack browser proof (real web → API → auth → PostgreSQL,
  no mocking) is the `apps/web/tests/real-stack/` lane, starting with
  Field F02. See `docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md`
  §12.
- **The seeded demo Session is a NON_PROOF fixture.** Its state
  (a frozen Burst of a DRAFT Session) is not reachable through lawful
  transitions. Use it only as a labelled
  fixture, never as proof of governed behavior.

## No production claims

Per `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §43, this
repository may claim only `ARCHITECTURAL PROTOTYPE` status, subject to
proof. It does not claim production readiness, regulatory compliance,
privacy approval, provider approval, security certification, or
validated-system status.
