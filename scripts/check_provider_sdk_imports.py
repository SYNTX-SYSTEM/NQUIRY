#!/usr/bin/env python3
"""Provider SDK import checker.

14 §41: "provider SDK import only under provider adapter"
(`packages/ai_gateway/adapters/providers/`). This is the single
approved location in the entire repository for a provider SDK import
(14 §4: "provider adapter | Forbidden dependency: CommandProcessor,
CommitWriter, DecisionRepository write" — the reverse direction is
enforced by `check_architecture_dependencies.py`'s INTERNAL_ALLOWED
table; this script enforces the forward direction: nowhere *else* may
import a provider SDK at all).

This is P-23's structural proof at Phase 0
(14 §50: `tests/security/test_ai_gateway.py`, "direct provider
import/path -> unavailable/security signal"): a direct provider
import outside the adapter boundary is rejected here as a static CI
signal, since no runtime AI Gateway exists yet to reject it
dynamically.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from _repo_scan import (
    API_SRC_ROOT,
    PACKAGES_ROOT,
    PROVIDER_SDK_MODULES,
    WORKER_SRC_ROOT,
    scan_owned_packages,
)

_APPROVED_PATH_MARKER = Path("ai_gateway") / "adapters" / "providers"


@dataclass(frozen=True, slots=True)
class Violation:
    file: Path
    owner_package: str
    imported: str
    lineno: int

    def __str__(self) -> str:
        try:
            rel = self.file.relative_to(Path(__file__).resolve().parent.parent)
        except ValueError:
            rel = self.file
        return (
            f"{rel}:{self.lineno}: package '{self.owner_package}' imports provider SDK "
            f"'{self.imported}' outside packages/ai_gateway/adapters/providers/"
        )


def _is_approved(file: Path) -> bool:
    return str(_APPROVED_PATH_MARKER) in str(file)


def check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
    """Run the check. `roots` defaults to this repository's real source
    roots; tests pass a fabricated fixture tree instead so a controlled
    violation can be proven without touching real production code.
    """
    scan_roots = roots if roots is not None else (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT)
    violations: list[Violation] = []
    for imp in scan_owned_packages(*scan_roots):
        if imp.module not in PROVIDER_SDK_MODULES:
            continue
        if _is_approved(imp.file):
            continue
        violations.append(Violation(imp.file, imp.owner_package, imp.module, imp.lineno))
    return violations


def main() -> int:
    violations = check()
    if violations:
        print("PROVIDER_SDK_IMPORT_CHECK::FAIL")
        for v in violations:
            print(f"  {v}")
        print(f"{len(violations)} violation(s) found.")
        return 1
    print("PROVIDER_SDK_IMPORT_CHECK::PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
