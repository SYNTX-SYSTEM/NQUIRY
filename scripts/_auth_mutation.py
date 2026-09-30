"""Shared runner for the AUTH Field's mutation proofs (24; 13 AC-13-010).

Same contract as the `pfc_*_mutation_proof.py` scripts: every mutation
re-breaks one protection in the source, the named falsifiers must then fail
(KILLED), and every source file is restored byte-for-byte (sha256 verified).

One addition, because this Field's protections also live in migrations
(CHECK constraints, triggers, indexes): when a mutation edits a file under
`migrations/`, the falsifiers run against a scratch database that is created
for that one mutation, migrated to head from the mutated tree, and dropped
afterwards. The ambient `DATABASE_URL` database is never migrated with a
mutated migration.

`DATABASE_URL` must point at an isolated *_test database at head, on a server
where the role may create databases.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]

Edit = tuple[str, str, str]
Mutation = tuple[str, list[Edit]]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pytest(tests: tuple[str, ...], env: dict[str, str]) -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *tests],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def _admin(url: sa.URL, statement: str) -> None:
    engine = sa.create_engine(url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(sa.text(statement))
    finally:
        engine.dispose()


def _run_on_scratch_database(tests: tuple[str, ...], index: int) -> int:
    base = sa.make_url(os.environ["DATABASE_URL"])
    name = f"{base.database}_mut_{os.getpid()}_{index}"
    scratch = base.set(database=name)
    env = {**os.environ, "DATABASE_URL": scratch.render_as_string(hide_password=False)}
    _admin(base, f'CREATE DATABASE "{name}"')
    try:
        migrated = subprocess.run(
            [sys.executable, "scripts/verify_migrations.py"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        if migrated != 0:
            return 1  # the mutated migration does not even apply: killed
        return _pytest(tests, env)
    finally:
        _admin(base, f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')


def run_mutations(mutations: list[Mutation], tests: tuple[str, ...]) -> int:
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is required")
        return 2
    selected = sys.argv[1:]  # optional: run only mutations whose name starts with an argument
    if selected:
        mutations = [m for m in mutations if any(m[0].startswith(prefix) for prefix in selected)]
    files = {rel for _, edits in mutations for rel, _, _ in edits}
    before = {rel: _sha(ROOT / rel) for rel in files}
    if _pytest(tests, dict(os.environ)) != 0:
        print("UNMUTATED_BASELINE_NOT_GREEN")
        return 1
    failures: list[str] = []
    for index, (name, edits) in enumerate(mutations):
        originals = {rel: (ROOT / rel).read_text() for rel, _, _ in edits}
        texts = dict(originals)
        unique = True
        for rel, old, new in edits:
            if texts[rel].count(old) != 1:
                unique = False
                break
            texts[rel] = texts[rel].replace(old, new)
        if not unique:
            print(f"{name}: MUTATION_SITE_NOT_UNIQUE", flush=True)
            failures.append(name)
            continue
        touches_schema = any(rel.startswith("migrations/") for rel, _, _ in edits)
        try:
            for rel, text in texts.items():
                (ROOT / rel).write_text(text)
            if touches_schema:
                code = _run_on_scratch_database(tests, index)
            else:
                code = _pytest(tests, dict(os.environ))
        finally:
            for rel, text in originals.items():
                (ROOT / rel).write_text(text)
        killed = code != 0
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}", flush=True)
        if not killed:
            failures.append(name)
    restored = all(_sha(ROOT / rel) == digest for rel, digest in before.items())
    print(f"{len(mutations) - len(failures)}/{len(mutations)} killed; sources restored: {restored}")
    return 0 if not failures and restored else 1
