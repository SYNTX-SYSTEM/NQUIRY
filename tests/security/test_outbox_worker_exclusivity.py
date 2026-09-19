"""P-16/P-17 (14 section 41): "event consumer cannot import direct
consequential handler" -- outbox worker exclusivity.

`nquiry_worker`'s own 14 section 3.1 package-level ceiling
(`{events, projection, recovery, command, commit, semantic_types}`) is
wide enough for a future `recovery_worker.py` sibling that genuinely
needs governed recovery Commands. That package-level ceiling cannot by
itself prove `outbox_worker.py` -- specifically -- never reaches a
canonical writer; `check_architecture_dependencies.py` only polices
the coarser package-level graph. This file scans this repository's REAL
production source (not a fixture tree) and proves the file-level claim
directly, the same P-23-style dynamic proof PKG-19 established for
`MockProviderAdapter` exclusivity.
"""

from __future__ import annotations

import ast

from check_provider_sdk_imports import WORKER_SRC_ROOT

_OUTBOX_WORKER_PATH = WORKER_SRC_ROOT / "nquiry_worker" / "outbox_worker.py"

# 14 section 41: "event consumer cannot import direct consequential
# handler." A canonical writer is reachable only through `command`,
# `commit` or the concrete persistence adapters -- none of which
# `outbox_worker.py` may import (mandatory adversarial attacks:
# "consumer attempts canonical write", "outbox retry interpreted as
# command retry").
_FORBIDDEN_TOP_LEVEL_IMPORTS = frozenset({"command", "commit", "persistence", "application"})


def _top_level_imports(path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module.split(".")[0])
    return names


def test_outbox_worker_file_exists_at_its_disclosed_location() -> None:
    assert _OUTBOX_WORKER_PATH.is_file()


def test_outbox_worker_imports_no_canonical_writer() -> None:
    imports = _top_level_imports(_OUTBOX_WORKER_PATH)
    assert not _FORBIDDEN_TOP_LEVEL_IMPORTS & imports, imports


def test_outbox_worker_imports_only_its_own_allowed_ports() -> None:
    """Positive control: the file must still import *something* real
    (`events`, `semantic_types`) -- an empty-import file would make the
    negative check above vacuously true.
    """
    imports = _top_level_imports(_OUTBOX_WORKER_PATH)
    assert {"events", "semantic_types"} <= imports


def test_events_package_own_allow_list_remains_semantic_types_only() -> None:
    """Regression guard: this package's own DIFF_AUDIT introduces no
    new architecture-dependency extension for `events` -- its 14
    section 3.1 allow-list stays exactly `{semantic_types}`.
    """
    import check_architecture_dependencies as cad

    assert cad.INTERNAL_ALLOWED["events"] == frozenset({"semantic_types"})
