"""T12 REGRESSION TEST: falsifiability of `package_dependency_graph.py`
itself, mirroring PKG-30/PKG-31's own registry-falsifiability
discipline (`test_every_proof_claim_matrix_evidence_file_actually_exists`,
`test_every_target_test_nodeid_file_actually_exists`): a dependency
graph is only as trustworthy as a test that can falsify a stale or
mistranscribed edge or path in it.

This file does NOT itself execute the computed affected-test-path set
via a nested `pytest.main()` call -- unlike `tests/mutation/harness.py`
(a standalone script's own single-process runner, never itself
collected by pytest), a test FUNCTION calling `pytest.main()` while
already running inside a live pytest session risks exactly the
self-referential-collection/nested-session fragility PKG-31's own
`harness.py` module docstring warns about. The actual, real execution
of the dependency-computed affected suite for this package's own
concrete change (PKG-30+PKG-31 -> downstream PKG-32) is run as a plain
top-level `python -m pytest` invocation and captured verbatim in
`docs/implementation/proof-reports/PKG-32.md`'s own RAW_EVIDENCE_APPENDIX,
the same way `scripts/verify_migrations.py`'s live-DB check and PKG-31's
own `scripts/run_mutation_harness.py` are real but not pytest-nested.
"""

from __future__ import annotations

from pathlib import Path

from package_dependency_graph import (
    FRONTEND_TEST_PATHS,
    PACKAGE_IDS,
    PACKAGE_PREDECESSORS,
    PACKAGE_TEST_PATHS,
    PYTHON_TEST_PATHS,
    affected_python_test_paths,
    downstream_of,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_package_ids_cover_exactly_pkg00_through_pkg32() -> None:
    assert tuple(f"PKG-{n:02d}" for n in range(33)) == PACKAGE_IDS
    assert len(PACKAGE_IDS) == 33


def test_predecessor_and_test_path_key_sets_are_both_exactly_the_full_package_set() -> None:
    assert set(PACKAGE_PREDECESSORS) == set(PACKAGE_IDS)
    assert set(PACKAGE_TEST_PATHS) == set(PACKAGE_IDS)


def test_pkg00_has_no_predecessor_and_every_other_package_has_at_least_one() -> None:
    assert PACKAGE_PREDECESSORS["PKG-00"] == ()
    for pkg in PACKAGE_IDS[1:]:
        assert PACKAGE_PREDECESSORS[pkg], f"{pkg} must have at least one predecessor"


def test_dag_matches_14_section_47_key_edges() -> None:
    """Spot-checks the exact fan-out/fan-in edges 14 section 47's own
    DAG names explicitly, including the three multi-predecessor nodes
    (PKG-28/29/30) that are not expressible as a simple linear chain."""
    assert PACKAGE_PREDECESSORS["PKG-01"] == ("PKG-00",)
    assert set(PACKAGE_PREDECESSORS["PKG-02"]) == {"PKG-01"}
    assert set(PACKAGE_PREDECESSORS["PKG-05"]) == {"PKG-01"}
    assert set(PACKAGE_PREDECESSORS["PKG-14"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-15"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-16"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-20"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-22"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-25"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-27"]) == {"PKG-13"}
    assert set(PACKAGE_PREDECESSORS["PKG-28"]) == {"PKG-21", "PKG-26"}
    assert set(PACKAGE_PREDECESSORS["PKG-29"]) == {"PKG-15", "PKG-19", "PKG-28"}
    assert set(PACKAGE_PREDECESSORS["PKG-30"]) == {"PKG-24", "PKG-26", "PKG-29"}
    assert PACKAGE_PREDECESSORS["PKG-31"] == ("PKG-30",)
    assert PACKAGE_PREDECESSORS["PKG-32"] == ("PKG-31",)


def test_every_referenced_test_path_actually_exists_on_disk() -> None:
    missing: list[str] = []
    for pkg, paths in PACKAGE_TEST_PATHS.items():
        for path in paths:
            if not (_REPO_ROOT / path).is_file():
                missing.append(f"{pkg}: {path}")
    assert missing == [], f"graph cites non-existent test files: {missing}"


def test_python_and_frontend_split_covers_every_path_exactly_once() -> None:
    for pkg, paths in PACKAGE_TEST_PATHS.items():
        python_paths = set(PYTHON_TEST_PATHS.get(pkg, ()))
        frontend_paths = set(FRONTEND_TEST_PATHS.get(pkg, ()))
        assert python_paths | frontend_paths == set(paths)
        assert python_paths & frontend_paths == set()
        for path in frontend_paths:
            assert path.startswith("apps/web/tests/")
        for path in python_paths:
            assert not path.startswith("apps/web/tests/")


def test_downstream_of_pkg13_is_every_later_package() -> None:
    """PKG-13 (CommitCoordinator/BND-014) is the single largest
    fan-out node in the real DAG -- every package from PKG-14 onward
    ultimately depends on it, directly or through PKG-20/21, PKG-22/
    23/24, PKG-25/26, PKG-28/29/30/31/32."""
    expected = {f"PKG-{n:02d}" for n in range(14, 33)}
    assert downstream_of("PKG-13") == frozenset(expected)


def test_downstream_of_pkg31_is_only_pkg32() -> None:
    assert downstream_of("PKG-31") == frozenset({"PKG-32"})


def test_downstream_of_pkg00_is_every_other_package() -> None:
    expected = set(PACKAGE_IDS) - {"PKG-00"}
    assert downstream_of("PKG-00") == frozenset(expected)


def test_unknown_package_is_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="unknown package"):
        downstream_of("PKG-99")


def test_affected_python_test_paths_for_the_real_pkg30_pkg31_change_is_a_small_real_subset() -> (
    None
):
    """The real, concrete "dependency-based affected suite" for this
    package's own predecessor chain: PKG-31's own PACKAGE_PASS commit
    (2939750) both introduced tests/mutation/ and modified
    tests/e2e/test_proof_bundle_paths.py, a file PKG-30 itself
    introduced -- so both PKG-30 and PKG-31 are the "changed packages"
    a real reviewer would name, and PKG-32 (this package) is the only
    downstream dependent. This proves the computed set is the real,
    narrow, dependency-justified one 14 Phase 14 requires -- not "every
    test in the repository", and not merely PKG-31's own files in
    isolation (which would silently miss the PKG-30 file PKG-31 itself
    touched).
    """
    affected = affected_python_test_paths(("PKG-30", "PKG-31"))
    expected = (
        set(PYTHON_TEST_PATHS["PKG-30"])
        | set(PYTHON_TEST_PATHS["PKG-31"])
        | set(PYTHON_TEST_PATHS["PKG-32"])
    )
    assert affected == expected
    assert "tests/e2e/test_proof_bundle_paths.py" in affected
    assert "tests/mutation/test_pkg31_mutation_registry.py" in affected

    total_python_paths = {p for paths in PYTHON_TEST_PATHS.values() for p in paths}
    assert len(affected) < len(total_python_paths), (
        "affected set must be strictly smaller than the full suite -- "
        "otherwise this is not dependency-driven, it is 'rerun everything'"
    )
