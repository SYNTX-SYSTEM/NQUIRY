"""WU-PFC-F09-3 mutation proof: telemetry non-interference and Command correlation are guarded.

Each mutation re-breaks one relation (sink guard, correlation emission, the
commit identity only for committed outcomes, the command identity, the outcome
label) and must make `tests/e2e/test_pfc_f09_3_telemetry.py` fail. Sources are
restored byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_f09_3_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SINK = "packages/observability/context.py"
_F02 = "packages/application/http_f02.py"
_TESTS = ("tests/e2e/test_pfc_f09_3_telemetry.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 a tracer failure escapes the sink",
        [
            (
                _SINK,
                "        try:\n            self._emit(context)\n        except Exception as exc:",
                "        try:\n            self._emit(context)\n        except KeyboardInterrupt as exc:",
            )
        ],
    ),
    (
        "M02 governed Commands are not observed",
        [
            (
                _F02,
                "    response = _command_envelope(run)\n    _observe(ident, response)\n",
                "    response = _command_envelope(run)\n",
            )
        ],
    ),
    (
        "M03 a commit identity is claimed for a non-committed outcome",
        [
            (
                _F02,
                '            commit_id=ident.commit_id if kind == "committed" else None,',
                "            commit_id=ident.commit_id,",
            )
        ],
    ),
    (
        "M04 the command identity is not correlated",
        [
            (
                _F02,
                "            command_id=ident.command_id,\n            attempt_id=ident.attempt_id,",
                "            attempt_id=ident.attempt_id,",
            )
        ],
    ),
    (
        "M05 the outcome is not recorded",
        [
            (
                _F02,
                '            operation=f"http.command.{kind}",',
                '            operation="http.command",',
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
