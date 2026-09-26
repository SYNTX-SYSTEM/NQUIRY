"""WU-PFC-F09-1 mutation proof: the technical failure facts and their honest mapping are guarded.

Each mutation re-breaks one relation: the engine's typed failure facts, the
Command/Query mapping (never a guessed or false outcome), the command identity
echo, the API-edge installation, the worker's survival. It must make
`tests/e2e/test_pfc_f09_1_technical_failure.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_f09_1_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_ENGINE = "packages/persistence/engine.py"
_MAP = "packages/application/technical_failure.py"
_API = "apps/api/src/nquiry_api/main.py"
_WORKER = "apps/worker/src/nquiry_worker/__main__.py"
_TESTS = ("tests/e2e/test_pfc_f09_1_technical_failure.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 unreachable database not reported as unavailable",
        [
            (
                _ENGINE,
                '        raise DatabaseUnavailable(f"{type(exc).__name__}: {exc}") from exc',
                "        raise",
            )
        ],
    ),
    (
        "M02 rejected COMMIT treated as unproven",
        [
            (
                _ENGINE,
                "        except (sa.exc.IntegrityError, sa.exc.ProgrammingError, sa.exc.DataError) as exc:",
                "        except () as exc:",
            )
        ],
    ),
    (
        "M03 lost COMMIT claimed as proven abort",
        [
            (
                _ENGINE,
                '            raise CommitOutcomeUnknown(f"{type(exc).__name__}: {exc}") from exc',
                '            raise CommitRejected(f"{type(exc).__name__}: {exc}") from exc',
            )
        ],
    ),
    (
        "M04 caller exception swallowed by the transaction scope",
        [
            (
                _ENGINE,
                "                    transaction.rollback()\n            raise\n",
                "                    transaction.rollback()\n            return\n",
            )
        ],
    ),
    (
        "M05 uncertain Command commit reported as failed_precommit",
        [
            (
                _MAP,
                '            status, kind, reason = 503, "indeterminate", "COMMIT_OUTCOME_UNPROVEN"',
                '            status, kind, reason = 503, "failed_precommit", "COMMIT_OUTCOME_UNPROVEN"',
            )
        ],
    ),
    (
        "M06 unknown Command failure guessed as failed_precommit",
        [
            (
                _MAP,
                '        status, kind, reason = 500, "indeterminate", "UNEXPECTED_SERVER_FAILURE"',
                '        status, kind, reason = 500, "failed_precommit", "UNEXPECTED_SERVER_FAILURE"',
            )
        ],
    ),
    (
        "M07 command identity not echoed",
        [(_MAP, '        body["commandId"] = idempotency_key', "        pass")],
    ),
    (
        "M08 API edge mapping not installed",
        [(_API, "@app.exception_handler(Exception)", "@app.exception_handler(LookupError)")],
    ),
    (
        "M09 worker loop dies on a database outage",
        [
            (
                _WORKER,
                "        try:\n            _one_pass(args.retry_backoff)\n        except TECHNICAL_FAILURES as exc:",
                "        try:\n            _one_pass(args.retry_backoff)\n        except KeyboardInterrupt as exc:",
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
