"""ORANGE worker <-> database binding (proof lane; PARALLEL != SHARED_MUTABLE_DB).

Loaded in every pytest process of the ORANGE env (pytest11 entry point), inert outside xdist
workers except for one controller check. Fail-closed:

Controller (xdist, lane on): DATABASE_URL must be UNSET, so no worker can inherit a shared URL.
Worker:
- the lane must be explicitly on (ORANGE_XDIST_LANE=1); an xdist worker without it is REFUSED
  (workers must never fall back to an inherited / shared DATABASE_URL);
- workerid must be one of gw0..gw3 (no gw4+, no restarted-worker ids);
- the inherited DATABASE_URL must be unset; NQUIRY_RUN_REAL_COMMIT_TESTS must be unset;
- ORANGE_DB_BASE must be exactly the proof cluster base URL;
- the target name comes ONLY from the fixed injective map gwN -> nquiry_proof_gwN_test, validated
  BEFORE any connection (a forbidden database is never contacted);
- read-only identity check on the target: current_database(), alembic head, zero foreign
  connections, zero rows in every table except alembic_version;
- only then DATABASE_URL is set for this worker process (every reader in the frozen tree reads it
  lazily, statically proven).
A refused worker raises inside collection (a reported ERROR, exit != 0 and != 5).
"""

from __future__ import annotations

import json
import os
import pathlib

LANE_ENV = "ORANGE_XDIST_LANE"
BASE_ENV = "ORANGE_DB_BASE"
EVIDENCE_ENV = "ORANGE_BINDING_EVIDENCE"
PROOF_BASE = "postgresql+psycopg://nquiry:nquiry_local_dev_only@127.0.0.1:15432/"
EXPECTED_HEAD = "e8c2a5f1b7d4"
WORKER_DB = {f"gw{i}": f"nquiry_proof_gw{i}_test" for i in range(4)}
assert len(set(WORKER_DB.values())) == len(WORKER_DB), "worker->db map must be injective"

_REFUSAL: list[str] = []


class WorkerBindingRefused(Exception):
    pass


def identity_problems(expected_db: str, observed: dict[str, object]) -> list[str]:
    """Pure: compare a read-only identity observation with the expected worker database."""
    problems = []
    if observed.get("current_database") != expected_db:
        problems.append(f"connected to {observed.get('current_database')!r}, expected {expected_db!r}")
    if observed.get("head") != [EXPECTED_HEAD]:
        problems.append(f"alembic head {observed.get('head')} != [{EXPECTED_HEAD!r}]")
    if observed.get("foreign_connections") != 0:
        problems.append(f"{observed.get('foreign_connections')} foreign connection(s) on {expected_db}")
    if observed.get("nonempty_tables"):
        problems.append(f"not clean: {observed.get('nonempty_tables')}")
    return problems


def _observe(url: str) -> dict[str, object]:
    import sqlalchemy as sa

    engine = sa.create_engine(url, poolclass=sa.pool.NullPool)
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SET TRANSACTION READ ONLY"))
            obs: dict[str, object] = {
                "current_database": conn.execute(sa.text("select current_database()")).scalar_one(),
                "head": conn.execute(sa.text("select version_num from alembic_version")).scalars().all(),
                "foreign_connections": conn.execute(sa.text(
                    "select count(*) from pg_stat_activity where datname = current_database() "
                    "and pid <> pg_backend_pid()")).scalar_one(),
            }
            tables = conn.execute(sa.text(
                "select tablename from pg_tables where schemaname='public' "
                "and tablename <> 'alembic_version'")).scalars().all()
            obs["nonempty_tables"] = {
                t: n for t in tables
                if (n := conn.execute(sa.text(f'select count(*) from public."{t}"')).scalar_one())
            }
            conn.rollback()
    finally:
        engine.dispose()
    return obs


def bind_worker(workerid: str, environ: os._Environ[str] | dict[str, str]) -> tuple[str, dict[str, object]]:
    """Returns (url, observation) or raises WorkerBindingRefused. Validates before connecting."""
    problems = []
    if environ.get(LANE_ENV) != "1":
        problems.append("xdist worker without ORANGE_XDIST_LANE=1: workers must never share an inherited DATABASE_URL")
    if workerid not in WORKER_DB:
        problems.append(f"worker id {workerid!r} not in allowlist {sorted(WORKER_DB)} (max 4, no restarts)")
    if environ.get("DATABASE_URL"):
        problems.append("worker inherited a DATABASE_URL (controller must leave it unset)")
    if environ.get("NQUIRY_RUN_REAL_COMMIT_TESTS"):
        problems.append("NQUIRY_RUN_REAL_COMMIT_TESTS is set (would commit durable rows into a worker DB)")
    if environ.get(BASE_ENV) != PROOF_BASE:
        problems.append(f"{BASE_ENV} is not the proof cluster base")
    if problems:
        raise WorkerBindingRefused("; ".join(problems))
    db = WORKER_DB[workerid]
    url = PROOF_BASE + db
    observed = _observe(url)
    problems = identity_problems(db, observed)
    if problems:
        raise WorkerBindingRefused(f"{workerid}->{db}: " + "; ".join(problems))
    return url, observed


def pytest_configure(config):  # type: ignore[no-untyped-def]
    import pytest

    workerinput = getattr(config, "workerinput", None)
    if workerinput is None:
        numprocesses = getattr(config.option, "numprocesses", None)
        if os.environ.get(LANE_ENV) == "1" and numprocesses and os.environ.get("DATABASE_URL"):
            raise pytest.UsageError(
                "ORANGE worker-DB binding REFUSED: controller has DATABASE_URL set; "
                "workers would inherit one shared mutable database")
        return
    workerid = workerinput["workerid"]
    try:
        url, observed = bind_worker(workerid, os.environ)
    except WorkerBindingRefused as exc:
        _REFUSAL.append(f"ORANGE worker-DB binding REFUSED ({workerid}): {exc}")
        return
    os.environ["DATABASE_URL"] = url
    evidence = os.environ.get(EVIDENCE_ENV)
    if evidence:
        path = pathlib.Path(evidence)
        path.mkdir(parents=True, exist_ok=True)
        (path / f"binding_{workerid}.json").write_text(json.dumps(
            {"workerid": workerid, "pid": os.getpid(), "database": WORKER_DB[workerid],
             "observed": observed}, indent=1, default=str))


def pytest_runtest_logstart(nodeid, location):  # type: ignore[no-untyped-def]
    """OBSERVATION ONLY: per-worker execution order, so the scheduling argument (each worker runs
    node indices in increasing collection order under --dist load) is verifiable after the run."""
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    evidence = os.environ.get(EVIDENCE_ENV)
    if worker and evidence and not _REFUSAL:
        with (pathlib.Path(evidence) / f"order_{worker}.txt").open("a") as fh:
            fh.write(nodeid + "\n")


def pytest_collect_file(file_path, parent):  # type: ignore[no-untyped-def]
    if _REFUSAL:
        raise WorkerBindingRefused(_REFUSAL[0])
    return None


def pytest_report_header(config):  # type: ignore[no-untyped-def]
    return ["ORANGE worker-DB binding: gwN -> nquiry_proof_gwN_test (xdist lane only)"]
