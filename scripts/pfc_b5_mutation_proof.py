"""WU-PFC-B5 mutation proof: TRN-SESS-009 BEGIN_INVESTIGATION is guarded.

Each mutation re-breaks one relation of 03 TRN-SESS-009 / 04 AUTH-DEP-SESS-009:
the QUESTION_SELECTION state gate, the compelling selection, exactly one
primary, the selection-authority validity (and its authority class), the
complete five-level ImpactChain (HD-26 rule 8), the audit link to the
selection authority evidence, the Fixture status on the event, and the
capability and read model. Each must make
`tests/e2e/test_pfc_b5_begin_investigation.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_b5_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_H = "packages/application/investigation_handler.py"
_Q = "packages/application/inquiry_queries.py"
_TESTS = ("tests/e2e/test_pfc_b5_begin_investigation.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 state gate removed",
        [
            (
                _H,
                '    if session.state is not SessionState.QUESTION_SELECTION:\n        return InvestigationReadiness("SESSION_NOT_IN_QUESTION_SELECTION", None)',
                '    if False:\n        return InvestigationReadiness("SESSION_NOT_IN_QUESTION_SELECTION", None)',
            )
        ],
    ),
    (
        "M02 no compelling selection required",
        [
            (
                _H,
                "    if not any(s.selection_type is SelectionType.COMPELLING for s in selections):",
                "    if False:",
            )
        ],
    ),
    (
        "M03 a missing primary is not refused",
        [(_H, "    if len(primaries) != 1:", "    if len(primaries) > 1:")],
    ),
    (
        "M04 selection authority not verified",
        [
            (
                _H,
                "    if not all(_selection_authority_valid(ports, s) for s in selections):",
                "    if False:",
            )
        ],
    ),
    (
        "M05 any binding class counts as selection authority",
        [
            (
                _H,
                "        and binding.authority_class is AuthorityClass.QUESTION_SELECTION_RIGHT\n",
                "",
            )
        ],
    ),
    (
        "M06 an incomplete chain suffices",
        [(_H, "    if chain is None or not is_complete(chain):", "    if chain is None:")],
    ),
    (
        "M07 audit loses the selection-authority link",
        [
            (
                _H,
                '                        f"authority_binding:{s.human_authority_binding_id.value}"',
                '                        f"binding_omitted:{s.human_authority_binding_id.value}"',
            )
        ],
    ),
    (
        "M08 event drops the Fixture status",
        [
            (
                _H,
                '                    "fixture": fresh.fixture,\n                    "primary_question_id"',
                '                    "fixture": False,\n                    "primary_question_id"',
            )
        ],
    ),
    (
        "M09 capability ignores the preconditions",
        [
            (
                _Q,
                '        "BEGIN_INVESTIGATION": blocked_or(investigation_readiness(ports, session).blocker),',
                '        "BEGIN_INVESTIGATION": blocked_or(None),',
            )
        ],
    ),
    (
        "M10 capability relevant outside QUESTION_SELECTION",
        [
            (
                _Q,
                '        "BEGIN_INVESTIGATION": session.state is SessionState.QUESTION_SELECTION,',
                '        "BEGIN_INVESTIGATION": True,',
            )
        ],
    ),
    (
        "M11 read model hides the primary Question",
        [
            (
                _Q,
                '        "primaryQuestionId": payload["primary_question_id"],',
                '        "primaryQuestionId": None,',
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
