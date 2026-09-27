"""WU-PFC-B2 mutation proof: BEGIN_QUESTION_SELECTION under HD-25 is guarded.

Each mutation re-breaks one relation of TRN-SESS-008 as decided by HD-25: the
explicit confirmation (in the precondition, in the fingerprinted payload and at
the HTTP edge), the REFLECTION state gate, the audited HUMAN_PROCEDURAL_CONFIRMATION
basis (audit row, committed event, projection), the Fixture status on the event,
and the server capability. Each must make
`tests/e2e/test_pfc_b2_begin_question_selection.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_b2_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_HANDLER = "packages/application/reflection_handler.py"
_HTTP = "packages/application/http_f04.py"
_QUERIES = "packages/application/inquiry_queries.py"
_TESTS = ("tests/e2e/test_pfc_b2_begin_question_selection.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 confirmation not required: the precondition ignores it",
        [(_HANDLER, "    if confirmed is not True:", "    if False:")],
    ),
    (
        "M02 the fingerprinted payload assumes confirmation",
        [
            (
                _HANDLER,
                "        reflection_completion_confirmed=reflection_completion_confirmed is True,",
                "        reflection_completion_confirmed=True,",
            )
        ],
    ),
    (
        "M03 HTTP edge: an absent confirmation counts as given",
        [
            (
                _HTTP,
                "                    reflection_completion_confirmed=reflection_completion_confirmed is True,",
                "                    reflection_completion_confirmed=reflection_completion_confirmed is not False,",
            )
        ],
    ),
    (
        "M04 state gate removed",
        [
            (
                _HANDLER,
                '    if session.state is not SessionState.REFLECTION:\n        return "SESSION_NOT_IN_REFLECTION"',
                '    if False:\n        return "SESSION_NOT_IN_REFLECTION"',
            )
        ],
    ),
    (
        "M05 audit row loses the completion basis",
        [
            (
                _HANDLER,
                '                f"session:QUESTION_SELECTION|reflection_completion:{HUMAN_PROCEDURAL_CONFIRMATION}"',
                '                "session:QUESTION_SELECTION"',
            )
        ],
    ),
    (
        "M06 committed event claims SYSTEM_DERIVED completion",
        [
            (
                _HANDLER,
                '                    "reflection_completion_basis": HUMAN_PROCEDURAL_CONFIRMATION,',
                '                    "reflection_completion_basis": "SYSTEM_DERIVED",',
            )
        ],
    ),
    (
        "M07 committed event drops the Fixture status",
        [
            (
                _HANDLER,
                '                    "state": SessionState.QUESTION_SELECTION.value,\n                    "fixture": fresh.fixture,',
                '                    "state": SessionState.QUESTION_SELECTION.value,\n                    "fixture": False,',
            )
        ],
    ),
    (
        "M08 projection hides the completion basis",
        [
            (
                _QUERIES,
                '    return {"basis": payload["reflection_completion_basis"]}',
                "    return None",
            )
        ],
    ),
    (
        "M09 capability available outside REFLECTION",
        [
            (
                _QUERIES,
                '                None if session.state is SessionState.REFLECTION else "SESSION_NOT_IN_REFLECTION"',
                "                None",
            )
        ],
    ),
    (
        "M10 capability no longer states that confirmation is required",
        [
            (
                _QUERIES,
                '            "requiresReflectionCompletionConfirmation": True,',
                '            "requiresReflectionCompletionConfirmation": False,',
            )
        ],
    ),
    (
        "M11 transition target is not QUESTION_SELECTION-relevant in the projection",
        [
            (
                _QUERIES,
                '        "BEGIN_QUESTION_SELECTION": session.state is SessionState.REFLECTION,',
                '        "BEGIN_QUESTION_SELECTION": session.state is SessionState.ANALYSIS,',
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
