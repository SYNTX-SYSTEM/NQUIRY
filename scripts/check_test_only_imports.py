#!/usr/bin/env python3
"""Test-only import checker.

14 §41: "production packages cannot import `test_support`". 14 §40:
"Production import test forbids FailureInjector" — FailureInjector
lives under `packages/test_support/` (14 §48), so banning any
production import of `test_support` (or of the `tests` top-level
package) as a whole subsumes that specific rule too.

Production roots scanned: everything under `packages/` except
`packages/test_support` itself, plus `apps/api/src` and
`apps/worker/src`. `packages/test_support` importing its own sibling
modules is not a violation (relative/self imports are already
excluded by `_repo_scan.iter_imports_in_file`).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from _repo_scan import API_SRC_ROOT, PACKAGES_ROOT, WORKER_SRC_ROOT, scan_owned_packages

_FORBIDDEN_TEST_MODULES = frozenset({"test_support", "tests"})


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
            f"{rel}:{self.lineno}: production package '{self.owner_package}' "
            f"imports test-only module '{self.imported}'"
        )


def check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
    """Run the check. `roots` defaults to this repository's real source
    roots; tests pass a fabricated fixture tree instead so a controlled
    violation can be proven without touching real production code.
    """
    scan_roots = roots if roots is not None else (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT)
    violations: list[Violation] = []
    for imp in scan_owned_packages(*scan_roots):
        if imp.owner_package == "test_support":
            continue  # test_support is itself the test-only package; scanning it is not the point
        if imp.module in _FORBIDDEN_TEST_MODULES:
            violations.append(Violation(imp.file, imp.owner_package, imp.module, imp.lineno))
    return violations


def main() -> int:
    violations = check()
    if violations:
        print("TEST_ONLY_IMPORT_CHECK::FAIL")
        for v in violations:
            print(f"  {v}")
        print(f"{len(violations)} violation(s) found.")
        return 1
    print("TEST_ONLY_IMPORT_CHECK::PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
