"""WU-PFC-B1 mutation proof: BEGIN_REFLECTION under HD-24 is guarded.

Each mutation re-breaks one relation of TRN-SESS-007 as decided by HD-24: the
proof-source rule (Fixture/mock, HD-20, the empty real-provider set, proof class),
the unresolved-run rule (BND-017), the required analysis, the state gate, and
the NON_PROOF representation on the committed event, the projection and the
server capability. Each must make `tests/e2e/test_pfc_b1_begin_reflection.py`
fail. Sources are restored byte-for-byte after every mutation (sha256 verified).

Usage: `python scripts/pfc_b1_mutation_proof.py` with `DATABASE_URL` pointed at
an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PROOF = "packages/application/reflection_proof.py"
_HANDLER = "packages/application/reflection_handler.py"
_QUERIES = "packages/application/inquiry_queries.py"
_TESTS = ("tests/e2e/test_pfc_b1_begin_reflection.py",)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 HD-20 broken: a mock proof admits a real Session",
        [
            (
                _PROOF,
                "        return fixture and provider == MOCK_PROVIDER and proof_class == MOCK_NON_PROOF",
                "        return provider == MOCK_PROVIDER and proof_class == MOCK_NON_PROOF",
            )
        ],
    ),
    (
        "M02 a mock result passes under a real proof class",
        [
            (
                _PROOF,
                "        return fixture and provider == MOCK_PROVIDER and proof_class == MOCK_NON_PROOF",
                "        return fixture and provider == MOCK_PROVIDER",
            )
        ],
    ),
    (
        "M03 the real-provider source ignores the eligible set (HARD-DEP-002)",
        [(_PROOF, "            and provider in self.eligible_providers\n", "")],
    ),
    (
        "M04 the real-provider source admits the mock",
        [(_PROOF, "            provider != MOCK_PROVIDER\n            and ", "            ")],
    ),
    (
        "M05 an unresolved AI operation does not block (BND-017)",
        [(_PROOF, "    if _unresolved(ports, session):", "    if False:")],
    ),
    (
        "M06 no accepted analysis is required",
        [
            (
                _PROOF,
                '    if artifact is None:\n        return ReflectionReadiness("REQUIRED_ANALYSIS_NOT_COMPLETED", None)',
                "    if artifact is None:\n        pass",
            )
        ],
    ),
    (
        "M07 the ANALYSIS state gate is dropped",
        [(_PROOF, "    if session.state is not SessionState.ANALYSIS:", "    if False:")],
    ),
    (
        "M08 the event claims a real proof class",
        [
            (
                _HANDLER,
                '                    "proof_class": proof.proof_class,',
                '                    "proof_class": "PROVIDER_OUTPUT",',
            )
        ],
    ),
    (
        "M09 the event claims real provider proof",
        [
            (
                _HANDLER,
                '                    "is_real_provider_proof": proof.is_real_provider_proof,',
                '                    "is_real_provider_proof": True,',
            )
        ],
    ),
    (
        "M10 the projection hides the NON_PROOF class",
        [
            (
                _QUERIES,
                '        "proofClass": payload["proof_class"],',
                '        "proofClass": "PROVIDER_OUTPUT",',
            )
        ],
    ),
    (
        "M11 the server capability ignores readiness",
        [
            (
                _QUERIES,
                '        "BEGIN_REFLECTION": blocked_or(reflection_readiness(ports, session).blocker),',
                '        "BEGIN_REFLECTION": blocked_or(None),',
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
