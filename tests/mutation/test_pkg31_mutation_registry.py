"""T11 MUTATION TEST: falsifiability of the PKG-31 mutation registry
itself (`tests/mutation/mutation_cases.py`), mirroring PKG-30's own
`test_every_proof_claim_matrix_evidence_file_actually_exists` /
`test_every_pkg30_exercised_claim_has_this_files_own_path_as_evidence`
discipline: a registry entry is only as trustworthy as a test that can
falsify a stale or typo'd claim in it.

This file does NOT run the mutation harness itself (that requires a
real PostgreSQL connection and takes on the order of a minute for ten
mutations x three phases each -- deliberately kept OUT of the normal
`pytest -q` regression run, exactly like `scripts/verify_migrations.py`'s
live-DB check is a separate, explicit step, not a collected test). It
proves the REGISTRY is internally consistent and every reference in it
resolves to something real, so a broken `target_test_nodeids` entry or
a renamed patch target is caught here, fast and DB-free, rather than
only surfacing as a confusing failure deep inside
`scripts/run_mutation_harness.py`.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

from harness import MUTATION_IDS
from mutation_cases import MUTATIONS

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_mutations_covers_exactly_the_ten_mandatory_ids() -> None:
    ids = tuple(case.mutation_id for case in MUTATIONS)
    assert len(ids) == len(set(ids)), f"duplicate mutation_id in registry: {ids}"
    assert set(ids) == set(MUTATION_IDS)
    assert len(MUTATIONS) == 10


def test_every_target_test_nodeid_file_actually_exists() -> None:
    missing: list[str] = []
    for case in MUTATIONS:
        for nodeid in case.target_test_nodeids:
            file_part = nodeid.split("::", 1)[0]
            if not (_REPO_ROOT / file_part).is_file():
                missing.append(f"{case.mutation_id}: {nodeid}")
    assert missing == [], f"registry cites non-existent test files: {missing}"


def test_every_target_test_function_name_appears_in_its_own_file() -> None:
    """Catches a renamed/typo'd test function name -- the exact
    drafting-error class PKG-30's own P-19 finding demonstrated is real,
    not theoretical, for a hand-maintained evidence list."""
    missing: list[str] = []
    for case in MUTATIONS:
        for nodeid in case.target_test_nodeids:
            file_part, _, func_part = nodeid.partition("::")
            source = (_REPO_ROOT / file_part).read_text(encoding="utf-8")
            if not re.search(rf"^def {re.escape(func_part)}\(", source, re.MULTILINE):
                missing.append(f"{case.mutation_id}: {nodeid}")
    assert missing == [], f"registry cites test functions not found in their file: {missing}"


def test_every_patch_target_resolves_to_a_real_attribute() -> None:
    """Proves each `MutationPatch.target_module`/`target_qualname` pair
    is currently valid -- an upstream rename would otherwise only be
    discovered when `scripts/run_mutation_harness.py` crashes."""
    unresolved: list[str] = []
    for case in MUTATIONS:
        try:
            module = importlib.import_module(case.patch.target_module)
        except ImportError:
            unresolved.append(f"{case.mutation_id}: module {case.patch.target_module!r}")
            continue
        owner: object = module
        *path, attr = case.patch.target_qualname.split(".")
        try:
            for part in path:
                owner = getattr(owner, part)
            getattr(owner, attr)
        except AttributeError:
            unresolved.append(
                f"{case.mutation_id}: {case.patch.target_module}.{case.patch.target_qualname}"
            )
    assert unresolved == [], f"registry cites unresolvable patch targets: {unresolved}"


def test_every_case_names_a_non_placeholder_invariant_and_boundary() -> None:
    for case in MUTATIONS:
        assert len(case.invariant) > 40, f"{case.mutation_id}: invariant looks like a placeholder"
        assert case.expected_boundary, f"{case.mutation_id}: expected_boundary must be non-empty"
