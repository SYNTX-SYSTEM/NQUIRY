"""WU-PFC-B4 mutation proof: the ImpactChain product path under HD-26 is guarded.

Each mutation re-breaks one relation of HD-26 / 09 §86: the sole author (the
selector of the current primary), the QUESTION_SELECTION_RIGHT authority class
(at BND-005 and BND-014), one chain per primary (S2), strictly successive
levels, the structural completion predicate, the QUESTION_SELECTION state gate,
input validation, the content-authority denial mapping, the Fixture marking on
the event and the read model, and the capability. Each must make
`tests/e2e/test_pfc_b4_impact_chain.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified). The database backstops
(append-only, successive level, author FK) are proven directly by the
falsifiers, not by source mutation.

Usage: `python scripts/pfc_b4_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_H = "packages/application/impact_chain_handler.py"
_RUN = "packages/application/session_control_handler.py"
_HTTP = "packages/application/http_f02.py"
_F05 = "packages/application/http_f05.py"
_Q = "packages/application/inquiry_queries.py"
_TESTS = ("tests/e2e/test_pfc_b4_impact_chain.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 any selection-right holder may author (no selector check)",
        [(_H, "    if primary.selected_by_user_id != actor_id:", "    if False:")],
    ),
    (
        "M02 ImpactChain Commands run under SESSION_CONTROL_RIGHT",
        [
            (
                _H,
                "        authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,\n    )\n    return ImpactChainResult(commit_unit=unit, impact_chain_id=chain_id)",
                "        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,\n    )\n    return ImpactChainResult(commit_unit=unit, impact_chain_id=chain_id)",
            ),
            (
                _H,
                "        authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,\n    )\n    return ImpactChainResult(\n",
                "        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,\n    )\n    return ImpactChainResult(\n",
            ),
        ],
    ),
    (
        "M03 _run ignores the requested authority class (BND-005 and BND-014)",
        [
            (
                _RUN,
                "            required_authority_class=authority_class,",
                "            required_authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,",
            ),
            (
                _RUN,
                "        authority=BindingAuthority(\n            authority_class=authority_class,",
                "        authority=BindingAuthority(\n            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,",
            ),
        ],
    ),
    (
        "M04 a second chain for the same primary is not blocked",
        [
            (
                _H,
                '        return ("IMPACT_CHAIN_ALREADY_EXISTS", False) if chain is not None else (None, False)',
                "        return (None, False)",
            )
        ],
    ),
    (
        "M05 levels need not be successive",
        [(_H, "        if level != latest.next_level:", "        if False:")],
    ),
    (
        "M06 a complete chain still accepts appends",
        [(_H, '    if is_complete(chain):\n        return "IMPACT_CHAIN_COMPLETE", False\n', "")],
    ),
    (
        "M07 completion predicate weakened",
        [
            (
                _H,
                "    return chain is not None and tuple(n.level for n in chain.nodes) == LEVELS",
                "    return chain is not None and len(chain.nodes) >= 4",
            )
        ],
    ),
    (
        "M08 state gate removed",
        [
            (
                _H,
                '    if session.state is not SessionState.QUESTION_SELECTION:\n        return "SESSION_NOT_IN_QUESTION_SELECTION", False',
                '    if False:\n        return "SESSION_NOT_IN_QUESTION_SELECTION", False',
            )
        ],
    ),
    (
        "M09 a blank answer is accepted",
        [
            (
                _F05,
                "    if not isinstance(value, str) or not value.strip():",
                "    if not isinstance(value, str):",
            )
        ],
    ),
    (
        "M10 level range not validated",
        [
            (
                _F05,
                "    if not isinstance(value, int) or isinstance(value, bool) or value not in LEVELS:",
                "    if not isinstance(value, int) or isinstance(value, bool):",
            )
        ],
    ),
    (
        "M11 read model hides the Fixture proof mode",
        [
            (
                _Q,
                '        "proofMode": proof_mode(session.fixture),\n        "primaryQuestionId": str(primary.question_id.value) if primary else None,\n        "impactChainId"',
                '        "proofMode": "GOVERNED",\n        "primaryQuestionId": str(primary.question_id.value) if primary else None,\n        "impactChainId"',
            )
        ],
    ),
    (
        "M12 content-authority denial not answered as denied",
        [
            (
                _HTTP,
                "    except control.ContentAuthorityDenied as exc:\n        return _denied(exc.reason_code)\n",
                "",
            )
        ],
    ),
    (
        "M13 the append event drops the Fixture status",
        [
            (
                _H,
                '                    "complete": complete,\n                    "fixture": ready["fixture"],',
                '                    "complete": complete,\n                    "fixture": False,',
            )
        ],
    ),
    (
        "M14 capability ignores the selection right",
        [
            (
                _Q,
                '    if not holds_selection_right(ports, session, context.principal.user_id):\n        return _cap(False, "NO_QUESTION_SELECTION_RIGHT")\n    code, _ = impact_chain_blocker',
                "    code, _ = impact_chain_blocker",
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
