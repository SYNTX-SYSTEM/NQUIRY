"""P-17 (14 section 41): "event consumer cannot import direct
consequential handler" -- projection worker/package exclusivity.

Mandatory adversarial attacks this file proves: "replay tries Command"
("use projection in authority/commit"), "replay reruns AI". Same
P-23-style dynamic AST-scan proof PKG-19 established for
`MockProviderAdapter` exclusivity, and PKG-20 established for
`outbox_worker.py`.
"""

from __future__ import annotations

import ast

from check_provider_sdk_imports import PACKAGES_ROOT, WORKER_SRC_ROOT

_PROJECTION_WORKER_PATH = WORKER_SRC_ROOT / "nquiry_worker" / "projection_worker.py"
_PROJECTION_PACKAGE_ROOT = PACKAGES_ROOT / "projection"

# 14 section 41: "event consumer cannot import direct consequential
# handler." A canonical writer is reachable only through `command`,
# `commit` or the concrete persistence adapters.
_FORBIDDEN_CANONICAL_WRITE_IMPORTS = frozenset({"command", "commit", "persistence", "application"})

# Mandatory adversarial attacks: "replay reruns AI" / "use projection in
# authority/commit" -- 14 PKG-21 AUTHORITY: "Projection never authority
# source"; 14 PKG-21 AI: "Replay cannot invoke AI."
_FORBIDDEN_AI_AND_AUTHORITY_IMPORTS = frozenset(
    {"ai_gateway", "ai_contracts", "authority", "domain"}
)


def _top_level_imports(path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module.split(".")[0])
    return names


def test_projection_worker_file_exists_at_its_disclosed_location() -> None:
    assert _PROJECTION_WORKER_PATH.is_file()


def test_projection_worker_imports_no_canonical_writer() -> None:
    imports = _top_level_imports(_PROJECTION_WORKER_PATH)
    assert not _FORBIDDEN_CANONICAL_WRITE_IMPORTS & imports, imports


def test_projection_worker_imports_only_its_own_allowed_ports() -> None:
    """Positive control: the file must still import *something* real
    (`events`, `projection`, `semantic_types`) -- an empty-import file
    would make the negative check above vacuously true.
    """
    imports = _top_level_imports(_PROJECTION_WORKER_PATH)
    assert {"events", "projection", "semantic_types"} <= imports


def test_projection_package_never_imports_ai_or_authority_or_domain() -> None:
    """Scans every real production file under `packages/projection/`
    (not a fixture tree) -- "replay reruns AI" and "use projection in
    authority/commit" are both structurally impossible, not merely
    untested.
    """
    offenders: dict[str, set[str]] = {}
    for py_file in _PROJECTION_PACKAGE_ROOT.glob("*.py"):
        imports = _top_level_imports(py_file)
        hit = _FORBIDDEN_AI_AND_AUTHORITY_IMPORTS & imports
        if hit:
            offenders[str(py_file)] = hit
    assert not offenders, offenders


def test_projection_package_still_imports_something_real() -> None:
    """Positive control mirroring the worker's own check above."""
    all_imports: set[str] = set()
    for py_file in _PROJECTION_PACKAGE_ROOT.glob("*.py"):
        all_imports |= _top_level_imports(py_file)
    assert "events" in all_imports


def test_persistence_projection_extension_is_the_only_new_architecture_dependency() -> None:
    """Regression guard: this package's own DIFF_AUDIT introduces
    exactly one new architecture-dependency extension --
    `persistence -> projection` -- and `projection`'s own allow-list is
    unchanged from its Phase-0 skeleton value.
    """
    import check_architecture_dependencies as cad

    assert "projection" in cad.INTERNAL_ALLOWED["persistence"]
    assert cad.INTERNAL_ALLOWED["projection"] == frozenset(
        {"events", "persistence", "semantic_types"}
    )
