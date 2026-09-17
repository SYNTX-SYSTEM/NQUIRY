# nquiry

Architectural prototype implementing the NQUIRY specification in
`docs/architecture/`. This repository is materialized package by
package, in the order fixed by
`docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §46/§47 (Coding
Package Manifest / DAG), using the execution prompts in
`docs/architecture/15_AI_CODING_PROMPTS.md`.

Architecture defines what may exist. 14 defines how it is
materialized. 15 defines how a coding agent may build it. No code in
this repository defines architecture.

## Current state

`PKG-00` (Repository and architecture skeleton, Build Phase 0) —
toolchain, package boundaries, dependency enforcement, local DB and CI
skeleton. See `docs/implementation/proof-reports/PKG-00.md` for the
package completion report. No domain, authority, or persistence
behavior is implemented yet.

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

## Local development

```bash
cp infra/local/.env.example .env
docker compose up -d postgres           # PostgreSQL 17 only
docker compose --profile app up --build # + api, worker, web toolchain shells

pip install -e ".[dev]"                 # requires Python >= 3.13
pytest
ruff check .
mypy packages apps/api/src apps/worker/src scripts

cd apps/web && npm install && npm run dev
```

## No production claims

Per `docs/architecture/14_IMPLEMENTATION_SEQUENCE.md` §43, this
repository may claim only `ARCHITECTURAL PROTOTYPE` status, subject to
proof. It does not claim production readiness, regulatory compliance,
privacy approval, provider approval, security certification, or
validated-system status.
