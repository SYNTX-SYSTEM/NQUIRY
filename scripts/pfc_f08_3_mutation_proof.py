"""WU-PFC-F08-3 mutation proof: diagnostics and freshness are guarded.

Each mutation re-breaks one relation (undelivered filter, Workspace scope,
basis detection, oldest-undelivered filter, the operator command) and must make
`tests/e2e/test_pfc_f08_3_diagnostics.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_f08_3_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_DIAG = "packages/persistence/delivery_diagnostics.py"
_MAIN = "apps/worker/src/nquiry_worker/__main__.py"
_TESTS = ("tests/e2e/test_pfc_f08_3_diagnostics.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 freshness counts delivered records as undelivered",
        [
            (
                _DIAG,
                "                sa.func.count().filter(undelivered),",
                "                sa.func.count(),",
            )
        ],
    ),
    (
        "M02 freshness/diagnostics not Workspace-scoped",
        [
            (
                _DIAG,
                "    if workspace_id is None:\n        return stmt\n",
                "    if True:\n        return stmt\n",
            )
        ],
    ),
    (
        "M03 every record reported without basis",
        [
            (
                _DIAG,
                "                sa.func.count().filter(e.c.event_id.is_(None)),",
                "                sa.func.count(),",
            )
        ],
    ),
    (
        "M04 oldest undelivered includes delivered records",
        [
            (
                _DIAG,
                "                sa.func.min(o.c.created_at).filter(undelivered),",
                "                sa.func.min(o.c.created_at),",
            )
        ],
    ),
    ("M05 operator diagnose prints nothing", [(_MAIN, "        _diagnose()\n", "        pass\n")]),
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
