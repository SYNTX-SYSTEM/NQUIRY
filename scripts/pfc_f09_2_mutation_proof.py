"""WU-PFC-F09-2 mutation proof: membership before disclosure is guarded on every Session path.

Each mutation removes or weakens the identity/Workspace/membership precheck at
one site, so a Session fact (version, state) could again reach a non-member,
and must make `tests/e2e/test_pfc_f09_2_isolation_sweep.py` fail. Sources are
restored byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_f09_2_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CONTROL = "packages/application/session_control_handler.py"
_BEGIN = "packages/application/analysis_begin_handler.py"
_REQUEST = "packages/application/analysis_request_handler.py"
_COMPLETE = "packages/application/burst_completion_handler.py"
_TESTS = ("tests/e2e/test_pfc_f09_2_isolation_sweep.py",)

_CALL = "    deny_unless_member(\n        ports,\n        actor=actor,"
_CALL_OFF = "    (lambda *a, **k: None)(\n        ports,\n        actor=actor,"

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    ("M01 session-control routes disclose before membership", [(_CONTROL, _CALL, _CALL_OFF)]),
    ("M02 begin-analysis discloses before membership", [(_BEGIN, _CALL, _CALL_OFF)]),
    ("M03 analysis/clustering request discloses before membership", [(_REQUEST, _CALL, _CALL_OFF)]),
    ("M04 complete-burst discloses before membership", [(_COMPLETE, _CALL, _CALL_OFF)]),
    (
        "M05 precheck ignores which Workspace owns the Session (BND-002 dropped)",
        [
            (
                _CONTROL,
                "        (BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003)\n        if session is not None",
                "        (BoundaryId.BND_001, BoundaryId.BND_003)\n        if session is not None",
            )
        ],
    ),
    (
        "M06 precheck result not enforced",
        [
            (
                _CONTROL,
                "    result = evaluate_chain(registry, chain, inputs, context)  # type: ignore[arg-type]\n    if result.result is not BoundaryResult.ALLOW:\n        raise SessionCommandDenied(result)",
                "    result = evaluate_chain(registry, chain, inputs, context)  # type: ignore[arg-type]\n    if False:\n        raise SessionCommandDenied(result)",
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
