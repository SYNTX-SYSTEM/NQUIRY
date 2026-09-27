"""WU-PFC-B0 mutation proof: the Fixture Session identity (HD-24 rules 1-5) is guarded.

Each mutation re-breaks one link: the creation-time declaration (wire, strict
type, Command fingerprint, persistence), its read-back, the committed event
fact, and the NON_PROOF status on every Session surface. It must make
`tests/e2e/test_pfc_b0_fixture_session.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified). The immutability trigger
is proven directly against PostgreSQL by the falsifier (a migration cannot be
mutated in place).

Usage: `python scripts/pfc_b0_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_ROUTE = "apps/api/src/nquiry_api/http/inquiry.py"
_HANDLER = "packages/application/session_creation_handler.py"
_REPO = "packages/persistence/session_repository.py"
_MAP = "packages/persistence/challenge_session_mapping.py"
_QUERIES = "packages/application/inquiry_queries.py"
_LEGACY = "packages/application/http_dispatch.py"
_CONSUMER = "packages/projection/consumer.py"
_TESTS = ("tests/e2e/test_pfc_b0_fixture_session.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 the declaration is dropped at the API edge",
        [
            (
                _ROUTE,
                "            fixture=body.fixture if body is not None else False,",
                "            fixture=False,",
            )
        ],
    ),
    (
        "M02 a non-boolean declaration is coerced",
        [(_ROUTE, "    fixture: StrictBool = False", "    fixture: bool = False")],
    ),
    (
        "M03 the declaration is not part of the Command fingerprint",
        [
            (
                _HANDLER,
                "            fixture=fixture,\n        ),\n        idempotency_key=idempotency_key,",
                "        ),\n        idempotency_key=idempotency_key,",
            )
        ],
    ),
    (
        "M04 the declaration is not persisted",
        [(_REPO, "                fixture=session.fixture,\n", "")],
    ),
    (
        "M05 the stored marker is not read back",
        [(_MAP, '            fixture=row["fixture"],', "            fixture=False,")],
    ),
    (
        "M06 the committed event omits the real fixture fact",
        [
            (
                _HANDLER,
                '                    "fixture": self._session.fixture,',
                '                    "fixture": False,',
            )
        ],
    ),
    (
        "M07 projections present a Fixture Session as governed",
        [
            (
                _QUERIES,
                '    return "FIXTURE_NON_PROOF" if fixture else "GOVERNED"',
                '    return "GOVERNED"',
            )
        ],
    ),
    (
        "M08 the read model drops the Fixture status",
        [
            (
                _CONSUMER,
                "            fixture=_extract_fixture(envelope.payload, current),",
                "            fixture=None,",
            )
        ],
    ),
    (
        "M09 the legacy Session view drops the Fixture status",
        [
            (
                _LEGACY,
                '                "fixture": result.session.fixture,',
                '                "fixture": False,',
            )
        ],
    ),
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_tests() -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *_TESTS],
        cwd=_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def main() -> int:
    files = {rel for _, edits in MUTATIONS for rel, _, _ in edits}
    before = {rel: _sha(_ROOT / rel) for rel in files}
    failures: list[str] = []
    for name, edits in MUTATIONS:
        originals = {rel: (_ROOT / rel).read_text() for rel, _, _ in edits}
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
        try:
            for rel, text in texts.items():
                (_ROOT / rel).write_text(text)
            code = _run_tests()
        finally:
            for rel, text in originals.items():
                (_ROOT / rel).write_text(text)
        killed = code != 0
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}", flush=True)
        if not killed:
            failures.append(name)
    restored = all(_sha(_ROOT / rel) == digest for rel, digest in before.items())
    print(f"{len(MUTATIONS) - len(failures)}/{len(MUTATIONS)} killed; sources restored: {restored}")
    return 0 if not failures and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
