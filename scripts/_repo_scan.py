"""Shared AST import-scanning helper for the architecture-check scripts.

Used by `check_architecture_dependencies.py`, `check_provider_sdk_imports.py`,
and `check_test_only_imports.py` (14 §41: DEPENDENCY ENFORCEMENT). This
module is tooling, not a domain package, and is not part of the
`packages/` dependency graph the checkers themselves police.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Python source roots and the flat top-level package name each file
# belongs to, mirroring the `[tool.setuptools] package-dir` mapping in
# pyproject.toml so the checkers reason about the same names the
# architecture documents use ("domain", "authority", "ai_gateway", ...).
PACKAGES_ROOT = REPO_ROOT / "packages"
API_SRC_ROOT = REPO_ROOT / "apps" / "api" / "src"
WORKER_SRC_ROOT = REPO_ROOT / "apps" / "worker" / "src"

# Every flat top-level import name this repository's Python packaging
# (pyproject.toml [tool.setuptools]) exposes. Anything imported under
# one of these names is an *internal* cross-package dependency subject
# to the 14 §3.1 allow-list; anything else is an external/stdlib import
# subject only to the narrower per-package deny-list.
KNOWN_INTERNAL_PACKAGES = frozenset(
    {
        "semantic_types",
        "domain",
        "governance",
        "authority",
        "boundaries",
        "evidence",
        "ai_contracts",
        "ai_gateway",
        "command",
        "commit",
        "audit",
        "events",
        "projection",
        "recovery",
        "security",
        "observability",
        "application",
        "persistence",
        "test_support",
        "nquiry_api",
        "nquiry_worker",
    }
)

# Known AI provider SDK module names. Closed, extend deliberately.
# 14 §4/§41: "provider SDK import only under provider adapter"
# (`packages/ai_gateway/adapters/providers/`).
PROVIDER_SDK_MODULES = frozenset(
    {
        "openai",
        "anthropic",
        "google",
        "cohere",
        "mistralai",
        "boto3",  # Bedrock access path
        "vertexai",
        "azure",
    }
)


@dataclass(frozen=True, slots=True)
class ImportedModule:
    """One `import` or `from ... import ...` statement found in source."""

    file: Path
    owner_package: str
    module: str  # top-level module name only, e.g. "sqlalchemy" from "sqlalchemy.orm"
    lineno: int


def iter_python_files(*roots: Path) -> Iterator[Path]:
    for root in roots:
        if not root.exists():
            continue
        yield from sorted(root.rglob("*.py"))


def iter_imports_in_file(py_file: Path, owner_package: str) -> Iterator[ImportedModule]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError as exc:  # pragma: no cover - defensive; static verify catches this first
        raise SyntaxError(f"{py_file}: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                yield ImportedModule(py_file, owner_package, top, node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # relative import within the same owning package: not a
                # cross-package dependency, never a forbidden-dependency
                # concern.
                continue
            if node.module is None:
                continue
            top = node.module.split(".")[0]
            yield ImportedModule(py_file, owner_package, top, node.lineno)


def scan_owned_packages(*roots: Path) -> Iterator[ImportedModule]:
    """Yield every top-level import made by every `.py` file under each of
    `roots`, tagged with the flat top-level package name that owns the
    file: the first path segment of the file's path relative to
    whichever root it was found under (e.g. a file at
    `<root>/domain/session.py` is owned by `"domain"`).

    This mirrors the `[tool.setuptools] package-dir` mapping in
    pyproject.toml, under which each of `packages/`, `apps/api/src/`
    and `apps/worker/src/` is a root whose immediate children are flat
    top-level import names. Passing arbitrary roots (e.g. a `tmp_path`
    fixture tree in a test) works the same way, which is what makes
    the controlled-violation fixtures in
    `tests/regression/test_architecture_dependency_checks.py` and
    `tests/security/test_ai_gateway.py` possible without touching real
    production code.
    """
    for root in roots:
        for py_file in iter_python_files(root):
            if "__pycache__" in py_file.parts:
                continue
            rel = py_file.relative_to(root)
            if len(rel.parts) < 2:
                continue  # a file directly under root has no owning package directory
            owner = rel.parts[0]
            yield from iter_imports_in_file(py_file, owner)
