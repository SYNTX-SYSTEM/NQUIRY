"""WU-PFC-B3 mutation proof: the QuestionSelection product path is guarded.

Each mutation re-breaks one relation of the product path to TRN-SEL-001/002:
the state gate, the single-selector rule (AC-12-004), the one-primary rule, the
04 §41 compelling cap, the duplicate rule, the holder-only precheck, the
Session row lock, the expected Session version, the denial mapping, the read
model and the server capabilities. Each must make
`tests/e2e/test_pfc_b3_question_selection.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_b3_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CMD = "packages/application/selection_command.py"
_HTTP = "packages/application/http_f02.py"
_QUERIES = "packages/application/inquiry_queries.py"
_TESTS = ("tests/e2e/test_pfc_b3_question_selection.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 state gate removed",
        [(_CMD, "    if session.state is not SessionState.QUESTION_SELECTION:", "    if False:")],
    ),
    (
        "M02 several selectors tolerated",
        [
            (
                _CMD,
                "    if len(selection_holders(ports, session)) != 1:",
                "    if len(selection_holders(ports, session)) < 1:",
            )
        ],
    ),
    (
        "M03 a second primary is not blocked",
        [(_CMD, "    if selection_type is SelectionType.PRIMARY and same_type:", "    if False:")],
    ),
    ("M04 compelling cap raised", [(_CMD, "MAX_COMPELLING = 3", "MAX_COMPELLING = 4")]),
    (
        "M05 duplicate selection not blocked",
        [
            (
                _CMD,
                "    if question_id is not None and any(s.question_id == question_id for s in same_type):",
                "    if False:",
            )
        ],
    ),
    (
        "M06 blockers evaluated for non-holders too (authority after state)",
        [
            (
                _CMD,
                "    if actor.actor_class is ActorClass.HUMAN_USER and holds_selection_right(\n        ports, locked, actor.user_id\n    ):",
                "    if True:",
            )
        ],
    ),
    (
        "M07 no Session row lock",
        [
            (
                _CMD,
                "    locked = ports.sessions.get_for_update(session_id)",
                "    locked = ports.sessions.get(session_id)",
            )
        ],
    ),
    (
        "M08 expected Session version ignored",
        [
            (
                _CMD,
                "    if locked.record_version.value != expected_session_version:",
                "    if False:",
            )
        ],
    ),
    (
        "M09 a denied selection is not answered as denied",
        [
            (
                _HTTP,
                "        GrantAuthorityBindingDenied,\n        SelectQuestionDenied,\n",
                "        GrantAuthorityBindingDenied,\n",
            )
        ],
    ),
    (
        "M10 read model hides the proof mode",
        [
            (
                _QUERIES,
                '        "proofMode": proof_mode(session.fixture),\n        "primaryQuestionId"',
                '        "proofMode": "GOVERNED",\n        "primaryQuestionId"',
            )
        ],
    ),
    (
        "M11 capability ignores the selection right",
        [
            (
                _QUERIES,
                "    if not holds_selection_right(ports, session, context.principal.user_id):",
                "    if False:",
            )
        ],
    ),
    (
        "M12 capability ignores the product preconditions",
        [(_QUERIES, "    return _cap(blocker is None, blocker)", "    return _cap(True)")],
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
