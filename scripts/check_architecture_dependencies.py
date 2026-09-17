#!/usr/bin/env python3
"""Architecture dependency checker.

Enforces the directory ownership contract (14_IMPLEMENTATION_SEQUENCE.md
§3.1) and the forbidden dependency matrix (§4) at the level of actual
Python imports. Two independent rules are checked per file:

1. INTERNAL_ALLOWED: a cross-package import (one of this repository's
   own flat top-level packages) is only legitimate if it appears on
   the importing package's "May depend on" list. Anything else is
   default-DENY — no allow-all boundary (14 §45).
2. EXTERNAL_FORBIDDEN: an import of a named external framework/driver/
   provider-SDK group that 14 §3.1/§4 explicitly forbids for that
   package, regardless of whether it is "internal" to this repo.

This script does not know about JavaScript/TypeScript imports
(`apps/web`); frontend/backend isolation is enforced by the frontend
build only depending on the typed HTTP client, never on a backend
package (14 §3.1: "frontend | ... | Must not depend on: DB,
governance repository, authority resolver").

Known scope limitation (disclosed, not silently accepted): this is the
*checkable subset* of §3.1/§4 expressible as Python top-level import
names. It does not yet distinguish "governance mutation port" from
"governance read port", or "restricted" vs "unrestricted" persistence
access, because those distinctions do not yet exist as separate
importable modules at Phase 0. Extend the tables below as later
packages introduce the concrete module split.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from _repo_scan import (
    API_SRC_ROOT,
    KNOWN_INTERNAL_PACKAGES,
    PACKAGES_ROOT,
    PROVIDER_SDK_MODULES,
    WORKER_SRC_ROOT,
    scan_owned_packages,
)

# "May depend on" (14 §3.1), translated to flat internal package names.
# A package name not present as a key defaults to "no internal deps".
INTERNAL_ALLOWED: dict[str, frozenset[str]] = {
    "semantic_types": frozenset(),
    "domain": frozenset({"semantic_types"}),
    "governance": frozenset({"domain", "semantic_types"}),
    "authority": frozenset({"governance", "domain", "semantic_types"}),
    "boundaries": frozenset({"domain", "authority", "governance", "evidence", "semantic_types"}),
    "evidence": frozenset({"domain", "semantic_types"}),
    "ai_contracts": frozenset({"semantic_types", "evidence"}),
    "ai_gateway": frozenset({"ai_contracts", "security", "persistence", "semantic_types"}),
    "command": frozenset({"domain", "semantic_types"}),
    "commit": frozenset(
        {"command", "boundaries", "persistence", "audit", "events", "semantic_types"}
    ),
    "audit": frozenset({"semantic_types"}),
    "events": frozenset({"semantic_types"}),
    "projection": frozenset({"events", "persistence", "semantic_types"}),
    "recovery": frozenset({"command", "boundaries", "commit", "semantic_types"}),
    "security": frozenset({"semantic_types"}),
    "observability": frozenset({"semantic_types"}),
    "application": frozenset(
        {
            "command",
            "boundaries",
            "authority",
            "governance",
            "evidence",
            "ai_contracts",
            "ai_gateway",
            "recovery",
            "domain",
            "audit",
            "events",
            "projection",
            "security",
            "observability",
            "semantic_types",
        }
    ),
    "persistence": frozenset({"semantic_types"}),
    "test_support": frozenset(KNOWN_INTERNAL_PACKAGES - {"test_support"}),
    "nquiry_api": frozenset({"application", "semantic_types"}),
    "nquiry_worker": frozenset(
        {"events", "projection", "recovery", "command", "commit", "semantic_types"}
    ),
}

_WEB_FRAMEWORK = frozenset({"fastapi", "starlette", "uvicorn"})
_DB_DRIVER = frozenset({"sqlalchemy", "psycopg", "psycopg2", "asyncpg"})
_OTEL_VENDOR = frozenset({"opentelemetry"})

# "Must not depend on" (14 §3.1) plus the forbidden-dependency matrix
# (§4), restricted to concrete external module names. Provider SDK
# checking here is deliberately redundant with
# `check_provider_sdk_imports.py` (defense in depth, single rule
# stated twice is not a forbidden shortcut).
EXTERNAL_FORBIDDEN: dict[str, frozenset[str]] = {
    "domain": _WEB_FRAMEWORK | _DB_DRIVER | _OTEL_VENDOR | PROVIDER_SDK_MODULES,
    "authority": PROVIDER_SDK_MODULES,
    "boundaries": _WEB_FRAMEWORK | PROVIDER_SDK_MODULES,
    "evidence": PROVIDER_SDK_MODULES,
    "ai_contracts": PROVIDER_SDK_MODULES,
    "ai_gateway": PROVIDER_SDK_MODULES,  # exempted for adapters/providers/, see below
    "command": _WEB_FRAMEWORK | PROVIDER_SDK_MODULES,
    "commit": PROVIDER_SDK_MODULES,
    "application": _DB_DRIVER | PROVIDER_SDK_MODULES,
    "nquiry_api": _DB_DRIVER | PROVIDER_SDK_MODULES,
}

_PROVIDER_ADAPTER_PATH_MARKER = Path("ai_gateway") / "adapters" / "providers"


@dataclass(frozen=True, slots=True)
class Violation:
    file: Path
    owner_package: str
    imported: str
    lineno: int
    rule: str

    def __str__(self) -> str:
        try:
            rel = self.file.relative_to(Path(__file__).resolve().parent.parent)
        except ValueError:
            rel = self.file
        return (
            f"{rel}:{self.lineno}: package '{self.owner_package}' "
            f"imports '{self.imported}' — {self.rule}"
        )


def _is_approved_provider_adapter_file(file: Path) -> bool:
    return str(_PROVIDER_ADAPTER_PATH_MARKER) in str(file)


def check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
    """Run the check. `roots` defaults to this repository's real source
    roots; tests pass a fabricated fixture tree instead so a controlled
    violation can be proven without touching real production code.
    """
    scan_roots = roots if roots is not None else (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT)
    violations: list[Violation] = []
    for imp in scan_owned_packages(*scan_roots):
        if imp.module == imp.owner_package:
            continue  # self-import (re-export, package __init__), never a cross-package concern

        if imp.module in KNOWN_INTERNAL_PACKAGES:
            allowed = INTERNAL_ALLOWED.get(imp.owner_package, frozenset())
            if imp.module not in allowed:
                violations.append(
                    Violation(
                        imp.file,
                        imp.owner_package,
                        imp.module,
                        imp.lineno,
                        f"'{imp.module}' is not on the 14 §3.1 'May depend on' "
                        f"list for '{imp.owner_package}'",
                    )
                )
            continue

        forbidden = EXTERNAL_FORBIDDEN.get(imp.owner_package, frozenset())
        if imp.module in forbidden:
            if (
                imp.owner_package == "ai_gateway"
                and imp.module in PROVIDER_SDK_MODULES
                and _is_approved_provider_adapter_file(imp.file)
            ):
                continue  # the one approved provider SDK import boundary
            violations.append(
                Violation(
                    imp.file,
                    imp.owner_package,
                    imp.module,
                    imp.lineno,
                    f"'{imp.module}' is forbidden for '{imp.owner_package}' by 14 §3.1/§4",
                )
            )
    return violations


def main() -> int:
    violations = check()
    if violations:
        print("ARCHITECTURE_DEPENDENCY_CHECK::FAIL")
        for v in violations:
            print(f"  {v}")
        print(f"{len(violations)} violation(s) found.")
        return 1
    print("ARCHITECTURE_DEPENDENCY_CHECK::PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
